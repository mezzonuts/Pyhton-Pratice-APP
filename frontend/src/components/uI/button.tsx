// @ts-nocheck
import * as React from 'react'
import { cn } from '@/lib/utils'

export const Button = ({
  variant = 'default',
  size = 'default',
  className,
  children,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'default' | 'primary' | 'secondary' | 'destructive' | 'link'
  size?: 'default' | 'sm' | 'tiny'
}) => {
  const variants = {
    default: 'bg-primary text-primary-foreground hover:opacity-90',
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-secondary text-secondary-foreground hover:opacity-90',
    destructive: 'bg-red-600 text-white hover:bg-red-700',
    link: 'underline text-blue-600 bg-transparent',
  }
  const sizes = {
    default: 'px-4 py-2 text-sm',
    sm: 'px-3 py-1.5 text-xs',
    tiny: 'px-2 py-1 text-xs',
  }

  return (
    <button
      className={cn(
        'inline-flex items-center justify-center rounded font-medium disabled:opacity-50',
        variants[variant] || variants.default,
        sizes[size] || sizes.default,
        className,
      )}
      {...props}
    >
      {children}
    </button>
  )
}
