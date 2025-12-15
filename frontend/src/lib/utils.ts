import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  const d = new Date(date)
  return d.toLocaleDateString('id-ID', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatFrequency(freq: number): string {
  return `${freq.toFixed(3)} MHz`
}

export function formatFieldStrength(strength: number): string {
  return `${strength.toFixed(1)} dBµV/m`
}

export function getOccupancyColor(percentage: number): string {
  if (percentage >= 70) return 'text-red-600'
  if (percentage >= 50) return 'text-yellow-600'
  return 'text-green-600'
}

export function getOccupancyBgColor(percentage: number): string {
  if (percentage >= 70) return 'bg-red-100'
  if (percentage >= 50) return 'bg-yellow-100'
  return 'bg-green-100'
}
