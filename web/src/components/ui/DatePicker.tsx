import * as React from 'react'
import { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isToday } from 'date-fns'

export interface DatePickerProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'onChange'> {
  value?: Date
  onChange?: (date: Date) => void
  placeholder?: string
}

const DatePicker = React.forwardRef<HTMLDivElement, DatePickerProps>(
  ({ className, value, onChange, placeholder = 'Select a date...', ...props }, ref) => {
    const [isOpen, setIsOpen] = useState(false)
    const [currentMonth, setCurrentMonth] = useState<Date>(value || new Date())
    const containerRef = useRef<HTMLDivElement>(null)

    const displayDate = value ? format(value, 'dd/MM/yyyy') : ''

    const days = eachDayOfInterval({
      start: startOfMonth(currentMonth),
      end: endOfMonth(currentMonth),
    })

    const handleSelectDate = (date: Date) => {
      onChange?.(date)
      setIsOpen(false)
    }

    const handlePrevMonth = () => {
      setCurrentMonth(prev => new Date(prev.getFullYear(), prev.getMonth() - 1))
    }

    const handleNextMonth = () => {
      setCurrentMonth(prev => new Date(prev.getFullYear(), prev.getMonth() + 1))
    }

    // Close dropdown when clicking outside
    useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
          setIsOpen(false)
        }
      }

      if (isOpen) {
        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
      }
    }, [isOpen])

    return (
      <div ref={ref} className={cn('relative w-full', className)} {...props}>
        <div ref={containerRef} className="relative">
          {/* Display Button */}
          <button
            type="button"
            onClick={() => setIsOpen(!isOpen)}
            className={cn(
              'w-full px-3 py-2 text-left rounded-md border-2 border-white/20 bg-white/10 text-white backdrop-blur-sm',
              'flex items-center justify-between gap-2',
              'transition-all duration-200',
              'hover:border-white/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-500 focus-visible:ring-offset-1',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              isOpen && 'ring-2 ring-accent-500 ring-offset-1'
            )}
          >
            <span className={cn(displayDate ? 'text-white font-medium' : 'text-white/60')}>
              {displayDate || placeholder}
            </span>
            <ChevronLeft
              className={cn(
                'h-5 w-5 text-white/60 transition-transform duration-200 flex-shrink-0 rotate-180',
                isOpen && 'rotate-0'
              )}
            />
          </button>

          {/* Calendar Dropdown */}
          {isOpen && (
            <div className={cn(
              'absolute top-full left-0 mt-2 z-50',
              'bg-secondary-700 backdrop-blur-md border-2 border-white/20 rounded-md shadow-xl p-4',
              'w-80'
            )}>
              {/* Month Navigation */}
              <div className="flex items-center justify-between mb-4">
                <button
                  type="button"
                  onClick={handlePrevMonth}
                  className="p-2 hover:bg-white/20 rounded transition-colors text-white"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
                <h2 className="text-sm font-semibold text-white">
                  {format(currentMonth, 'MMMM yyyy')}
                </h2>
                <button
                  type="button"
                  onClick={handleNextMonth}
                  className="p-2 hover:bg-white/20 rounded transition-colors text-white"
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              </div>

              {/* Weekday Headers */}
              <div className="grid grid-cols-7 gap-2 mb-2">
                {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(day => (
                  <div key={day} className="text-center text-xs font-semibold text-white/70 p-1">
                    {day}
                  </div>
                ))}
              </div>

              {/* Days Grid */}
              <div className="grid grid-cols-7 gap-2">
                {/* Empty cells for days before month starts */}
                {Array.from({ length: days[0]?.getDay() || 0 }).map((_, i) => (
                  <div key={`empty-${i}`} />
                ))}

                {/* Day buttons */}
                {days.map(day => {
                  const isSelected = value && format(value, 'yyyy-MM-dd') === format(day, 'yyyy-MM-dd')
                  const isTodayDate = isToday(day)

                  return (
                    <button
                      key={format(day, 'yyyy-MM-dd')}
                      type="button"
                      onClick={() => handleSelectDate(day)}
                      className={cn(
                        'p-2 text-sm rounded transition-colors font-medium',
                        'hover:bg-white/20 text-white',
                        isSelected && 'bg-accent-500 text-white font-semibold hover:bg-accent-600',
                        !isSelected && isTodayDate && 'border-2 border-accent-500 text-accent-300 font-semibold',
                        !isSelected && !isTodayDate && 'text-white'
                      )}
                    >
                      {format(day, 'd')}
                    </button>
                  )
                })}
              </div>

              {/* Today Button */}
              <button
                type="button"
                onClick={() => handleSelectDate(new Date())}
                className="w-full mt-4 px-3 py-2 text-sm font-semibold text-accent-300 hover:bg-accent-500/30 rounded transition-colors"
              >
                Today
              </button>
            </div>
          )}
        </div>
      </div>
    )
  }
)
DatePicker.displayName = 'DatePicker'

export { DatePicker }