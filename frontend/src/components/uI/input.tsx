// @ts-nocheck
import * as React from 'react'
import { cn } from '@/lib/utils'

export const Input = ({
  className,
  masked,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & { masked?: boolean }) => {
  return (
    <input
      className={cn('mb-2 w-full rounded border px-3 py-2 text-sm', className)}
      {...props}
    />
  )
}
