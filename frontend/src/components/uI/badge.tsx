// @ts-nocheck
import { cn } from '@/lib/utils'

export type Variant = 'default' | 'secondary' | 'destructive' | 'link'

export const Badge = ({
  variant = 'default',
  size,
  children,
  className,
}: {
  variant?: Variant
  size?: string
  children: React.ReactNode
  className?: string
}) => {
  const variants = {
    default: 'bg-primary text-primary-foreground',
    secondary: 'bg-secondary text-secondary-foreground',
    destructive: 'bg-destructive text-destructive-foreground',
    link: 'bg-transparent underline text-primary',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        variants[variant] || variants.default,
        className,
      )}
    >
      {children}
    </span>
  )
}
