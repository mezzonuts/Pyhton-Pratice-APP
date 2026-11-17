// @ts-nocheck
import { cn } from '@/lib/utils'

export interface CardProps {
  className?: string
  children: React.ReactNode
}

export const Card = ({ className, children }: CardProps) => {
  return (
    <div className={cn('rounded-lg border bg-card p-6', className)}>{children}</div>
  )
}

export const CardHeader = ({ children }: { children: React.ReactNode }) => {
  return <div className="flex flex-col space-y-1.5 pt-2">{children}</div>
}

export const CardTitle = ({ children }: { children: React.ReactNode }) => {
  return <h3 className="font-semibold text-lg">{children}</h3>
}

export const CardContent = ({ children }: { children: React.ReactNode }) => {
  return <div className="pt-2">{children}</div>
}