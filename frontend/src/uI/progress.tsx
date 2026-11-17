import { cn } from '@/lib/utils'

export const Progress = ({
  value,
  max = 100,
  className,
  ...props
}: {
  value: number
  max?: number
  className?: string
} & React.HTMLAttributes<HTMLDivElement>) => {
  const percentage = (value / max) * 100
  return (
    <div className={cn('h-2 bg-muted/50 rounded-full overflow-hidden', className)} {...props}>
      <div
        className={cn(
          'h-full bg-primary rounded-full',
          { 'w-full': percentage >= 100, 'w-[percentage]': percentage < 100 }
        )}
        style={{ width: `${percentage}%` }}
      ></div>
    </div>
  )
}