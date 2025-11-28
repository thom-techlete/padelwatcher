import { cn } from '@/lib/utils'

interface ProgressProps {
  value: number
  max?: number
  className?: string
  showLabel?: boolean
  label?: string
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'accent' | 'success' | 'warning' | 'error'
}

export function Progress({
  value,
  max = 100,
  className,
  showLabel = false,
  label,
  size = 'md',
  variant = 'accent',
}: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)

  const sizeClasses = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4',
  }

  const variantClasses = {
    default: 'bg-white/80',
    accent: 'bg-accent-500',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500',
  }

  return (
    <div className={cn('w-full', className)}>
      {(showLabel || label) && (
        <div className="flex justify-between mb-1.5">
          {label && (
            <span className="text-sm font-medium text-white/90">{label}</span>
          )}
          {showLabel && (
            <span className="text-sm font-medium text-white/70">{Math.round(percentage)}%</span>
          )}
        </div>
      )}
      <div
        className={cn(
          'w-full bg-white/20 rounded-full overflow-hidden',
          sizeClasses[size]
        )}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
      >
        <div
          className={cn(
            'h-full rounded-full transition-all duration-300 ease-out',
            variantClasses[variant]
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
