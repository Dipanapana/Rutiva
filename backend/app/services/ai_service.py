from typing import Optional, List, AsyncGenerator
import httpx
import json
from app.core.config import settings


# System prompt for RutaBot
SYSTEM_PROMPT = """You are RutaBot, an AI tutor for South African learners following the CAPS curriculum.

CORE PRINCIPLES:
1. GUIDE, don't give direct answers - use Socratic questioning
2. Explain concepts step-by-step, appropriate to the learner's grade level
3. REFUSE to complete full exams, tests, or assignments - offer to explain concepts instead
4. Encourage critical thinking and self-discovery
5. Be warm, patient, and encouraging

SAFETY RULES (STRICTLY ENFORCED):
- NO political opinions or content
- NO adult, violent, or inappropriate content
- NO bullying, manipulation, or emotional exploitation
- NO fabricating facts - say "I'm not sure" when uncertain
- NO personal advice beyond academics
- Keep responses focused on CAPS curriculum topics

CONTEXT:
- Learner Grade: {grade}
- Subject: {subject}
- Topic: {topic}

RESPONSE STYLE:
{style}

Remember: Your goal is to help learners UNDERSTAND, not just get answers. Guide them to think!
"""

GRADE_STYLES = {
    "junior": """
- Use simple, everyday language
- Give concrete examples from daily life
- Break down into very small steps
- Use encouraging phrases like "Great question!" and "You're on the right track!"
- Keep responses under 150 words
""",
    "senior": """
- Use clear academic language with explanations of new terms
- Connect concepts to real-world applications
- Encourage learners to make connections
- Provide structured step-by-step explanations
- Keep responses under 200 words
""",
    "matric": """
- Use formal academic language appropriate for FET phase
- Reference CAPS curriculum requirements where relevant
- Encourage deeper analysis and critical evaluation
- Support exam preparation with structured approaches
- Keep responses under 250 words
"""
}


class AIService:
    """AI service with DeepSeek primary and OpenAI fallback."""

    def __init__(self):
        self.providers = {
            "deepseek": {
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "api_key": settings.DEEPSEEK_API_KEY,
            },
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o-mini",
                "api_key": settings.OPENAI_API_KEY,
            }
        }
        self.primary = "deepseek"
        self.fallback = "openai"

    def _get_style(self, grade: int) -> str:
        """Get appropriate response style for grade."""
        if grade <= 7:
            return GRADE_STYLES["junior"]
        elif grade <= 9:
            return GRADE_STYLES["senior"]
        else:
            return GRADE_STYLES["matric"]

    def _build_system_prompt(
        self,
        grade: int,
        subject: Optional[str] = None,
        topic: Optional[str] = None
    ) -> str:
        """Build the system prompt with context."""
        return SYSTEM_PROMPT.format(
            grade=grade,
            subject=subject or "General",
            topic=topic or "General study help",
            style=self._get_style(grade)
        )

    async def chat_completion(
        self,
        messages: List[dict],
        grade: int = 10,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
        max_tokens: int = 500,
    ) -> AsyncGenerator[str, None]:
        """
        Send chat completion with automatic fallback.
        Streams the response.
        """
        # Build messages with system prompt
        system_prompt = self._build_system_prompt(grade, subject, topic)
        full_messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]

        # Try primary provider
        try:
            async for chunk in self._call_provider(
                self.primary, full_messages, max_tokens
            ):
                yield chunk
        except Exception as e:
            print(f"Primary AI ({self.primary}) failed: {e}, trying fallback")
            # Try fallback
            try:
                async for chunk in self._call_provider(
                    self.fallback, full_messages, max_tokens
                ):
                    yield chunk
            except Exception as e2:
                print(f"Fallback AI ({self.fallback}) also failed: {e2}")
                yield "I'm sorry, I'm having trouble connecting right now. Please try again in a moment."

    async def _call_provider(
        self,
        provider: str,
        messages: List[dict],
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """Call a specific AI provider with streaming."""
        config = self.providers.get(provider)
        if not config or not config.get("api_key"):
            raise ValueError(f"Provider {provider} not configured")

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{config['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config["model"],
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "stream": True,
                    "temperature": 0.7,
                }
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue

    async def simple_completion(
        self,
        prompt: str,
        grade: int = 10,
        max_tokens: int = 500
    ) -> str:
        """Non-streaming completion for simple requests."""
        messages = [{"role": "user", "content": prompt}]
        response = ""
        async for chunk in self.chat_completion(messages, grade, max_tokens=max_tokens):
            response += chunk
        return response

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        provider: str = None
    ) -> float:
        """Estimate cost in USD for a request."""
        provider = provider or self.primary
        rates = {
            "deepseek": {"input": 0.14, "output": 0.28},
            "openai": {"input": 0.15, "output": 0.60},
        }
        rate = rates.get(provider, rates["openai"])
        return (input_tokens * rate["input"] + output_tokens * rate["output"]) / 1_000_000
