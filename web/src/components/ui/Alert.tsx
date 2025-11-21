import { cn } from '@/lib/utils'
import { AlertCircle, CheckCircle2, Info, XCircle } from 'lucide-react'

interface AlertProps {
  variant?: 'default' | 'success' | 'warning' | 'error'
  title?: string
  children: React.ReactNode
  className?: string
}

const variants = {
  default: {
    container: 'bg-white/10 border-2 border-white/20 text-white',
    icon: Info,
  },
  success: {
    container: 'bg-green-500/20 border-2 border-green-500/40 text-green-200',
    icon: CheckCircle2,
  },
  warning: {
    container: 'bg-yellow-500/20 border-2 border-yellow-500/40 text-yellow-200',
    icon: AlertCircle,
  },
  error: {
    container: 'bg-red-500/20 border-2 border-red-500/40 text-red-200',
    icon: XCircle,
  },
}

export function Alert({ variant = 'default', title, children, className }: AlertProps) {
  const { container, icon: Icon } = variants[variant]

  return (
    <div className={cn('rounded-lg border p-4', container, className)}>
      <div className="flex gap-3">
        <Icon className="h-5 w-5 flex-shrink-0" />
        <div className="flex-1">
          {title && <h5 className="mb-1 font-medium">{title}</h5>}
          <div className="text-sm">{children}</div>
        </div>
      </div>
    </div>
  )
}
