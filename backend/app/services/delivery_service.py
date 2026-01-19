import boto3
from botocore.config import Config
from datetime import datetime, timedelta
import secrets
from typing import Optional
from app.core.config import settings


class DeliveryService:
    """
    Secure digital product delivery with:
    - Signed URLs (time-limited)
    - Download tokens (single-use optional)
    - Download tracking
    """

    def __init__(self):
        self.expiry_hours = 24

        # Initialize S3 client if credentials are available
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
                config=Config(signature_version='s3v4')
            )
        else:
            self.s3 = None

    def generate_download_url(
        self,
        user_id: str,
        product_id: str,
        file_key: str,
        single_use: bool = False
    ) -> dict:
        """Generate a signed download URL."""

        if not self.s3:
            # Return mock URL for development
            return {
                "url": f"{settings.API_URL}/mock-download/{file_key}",
                "token": secrets.token_urlsafe(32),
                "expires_at": (datetime.utcnow() + timedelta(hours=self.expiry_hours)).isoformat(),
                "single_use": single_use
            }

        # Parse S3 key from URL if needed
        if file_key.startswith("s3://"):
            # Format: s3://bucket/key
            parts = file_key.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ""
        else:
            bucket = settings.S3_BUCKET
            key = file_key

        # Get the filename from the key
        filename = key.split("/")[-1] if "/" in key else key

        # Generate signed URL
        url = self.s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': key,
                'ResponseContentDisposition': f'attachment; filename="{filename}"'
            },
            ExpiresIn=self.expiry_hours * 3600
        )

        # Create download token for tracking
        token = secrets.token_urlsafe(32)

        return {
            "url": url,
            "token": token,
            "expires_at": (datetime.utcnow() + timedelta(hours=self.expiry_hours)).isoformat(),
            "single_use": single_use
        }

    def upload_file(
        self,
        file_content: bytes,
        file_key: str,
        content_type: str = "application/pdf"
    ) -> str:
        """Upload a file to S3."""
        if not self.s3:
            return f"s3://{settings.S3_BUCKET}/{file_key}"

        self.s3.put_object(
            Bucket=settings.S3_BUCKET,
            Key=file_key,
            Body=file_content,
            ContentType=content_type
        )

        return f"s3://{settings.S3_BUCKET}/{file_key}"

    def delete_file(self, file_key: str) -> bool:
        """Delete a file from S3."""
        if not self.s3:
            return True

        # Parse S3 key from URL if needed
        if file_key.startswith("s3://"):
            parts = file_key.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ""
        else:
            bucket = settings.S3_BUCKET
            key = file_key

        try:
            self.s3.delete_object(Bucket=bucket, Key=key)
            return True
        except Exception:
            return False

    def file_exists(self, file_key: str) -> bool:
        """Check if a file exists in S3."""
        if not self.s3:
            return True  # Assume exists in development

        # Parse S3 key from URL if needed
        if file_key.startswith("s3://"):
            parts = file_key.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ""
        else:
            bucket = settings.S3_BUCKET
            key = file_key

        try:
            self.s3.head_object(Bucket=bucket, Key=key)
            return True
        except Exception:
            return False
