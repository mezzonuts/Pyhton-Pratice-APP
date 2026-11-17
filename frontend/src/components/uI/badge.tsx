// @ts-nocheck
import { cn } from '@/lib/utils'

export type Variant = 'default' | 'secondary' | 'destructive'

export const Badge = ({
  variant = 'default',
  children,
  className,
}: {
  variant?: Variant
  children: React.ReactNode
  className?: string
}) => {
  const variants = {
    default: 'bg-primary text-primary-foreground',
    secondary: 'bg-secondary text-secondary-foreground',
    destructive: 'bg-destructive text-destructive-foreground',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        variants[variant],
        className,
      )}
    >
      {children}
    </span>
  )
}