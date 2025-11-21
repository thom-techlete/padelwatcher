import * as React from 'react'
import { cn } from '@/lib/utils'

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          'flex h-10 w-full rounded-md border-2 border-white/20 bg-white/10 px-3 py-2 text-sm text-white backdrop-blur-sm',
          'placeholder:text-white/50',
          'focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 focus:ring-offset-1',
          'disabled:cursor-not-allowed disabled:opacity-50',
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = 'Input'

export { Input }
