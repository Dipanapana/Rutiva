import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPrice(cents: number): string {
  return `R${(cents / 100).toFixed(0)}`;
}

export function formatPriceWithCents(cents: number): string {
  return `R${(cents / 100).toFixed(2)}`;
}

export function getGradeLabel(grade: number): string {
  return `Grade ${grade}`;
}

export function getTermLabel(term: number): string {
  if (term === 0) return 'Full Year';
  return `Term ${term}`;
}

export function getSubjectColor(code: string): string {
  const colors: Record<string, string> = {
    MATH: '#0ea5e9',           // Mathematics - Blue
    'PHY-SCI': '#8b5cf6',      // Physical Sciences - Purple
    'LIFE-SCI': '#22c55e',     // Life Sciences - Green
    ACC: '#14b8a6',            // Accounting - Teal
    'BUS-STU': '#f97316',      // Business Studies - Orange
    'ENG-FAL': '#3b82f6',      // English FAL - Blue
    'ENG-HL': '#1d4ed8',       // English HL - Dark Blue
    'AFR-FAL': '#ec4899',      // Afrikaans FAL - Pink
    'AFR-HL': '#db2777',       // Afrikaans HL - Dark Pink
    GEOG: '#f59e0b',           // Geography - Amber
    HIST: '#ef4444',           // History - Red
  };
  return colors[code] || '#6b7280';
}
