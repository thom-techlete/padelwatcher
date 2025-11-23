import * as React from 'react'
import { ChevronUp, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useRef, useEffect } from 'react'

interface TimePickerProps {
  value?: string
  onChange?: (time: string) => void
  disabled?: boolean
}

const TimePicker = React.forwardRef<HTMLDivElement, TimePickerProps>(
  ({ value = '09:00', onChange, disabled = false }, ref) => {
    const [isOpen, setIsOpen] = React.useState(false)
    const containerRef = useRef<HTMLDivElement>(null)

    const setRefs = (el: HTMLDivElement | null) => {
      containerRef.current = el
      if (typeof ref === 'function') {
        ref(el)
      } else if (ref) {
        ref.current = el
      }
    }
    const [hours, setHours] = React.useState(() => {
      if (!value) return '09'
      const [h] = value.split(':')
      return h.padStart(2, '0')
    })
    const [minutes, setMinutes] = React.useState(() => {
      if (!value) return '00'
      const [, m] = value.split(':')
      return (m || '00').padStart(2, '0')
    })

    // Close picker when clicking outside
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

    React.useEffect(() => {
      if (value && value !== `${hours}:${minutes}`) {
        const [h, m] = value.split(':')
        setHours(h.padStart(2, '0'))
        setMinutes((m || '00').padStart(2, '0'))
      }
    }, [value, hours, minutes])

    const handleTimeChange = (newHours: string, newMinutes: string) => {
      setHours(newHours)
      setMinutes(newMinutes)
      onChange?.(`${newHours}:${newMinutes}`)
    }

    const incrementHours = () => {
      const h = parseInt(hours)
      const newH = h === 23 ? 0 : h + 1
      handleTimeChange(newH.toString().padStart(2, '0'), minutes)
    }

    const decrementHours = () => {
      const h = parseInt(hours)
      const newH = h === 0 ? 23 : h - 1
      handleTimeChange(newH.toString().padStart(2, '0'), minutes)
    }

    const incrementMinutes = () => {
      const m = parseInt(minutes)
      if (m === 0) {
        handleTimeChange(hours, '30')
      } else {
        // m === 30, go to next hour at 00
        const h = parseInt(hours)
        const newH = h === 23 ? 0 : h + 1
        handleTimeChange(newH.toString().padStart(2, '0'), '00')
      }
    }

    const decrementMinutes = () => {
      const m = parseInt(minutes)
      if (m === 30) {
        handleTimeChange(hours, '00')
      } else {
        // m === 0, go to previous hour at 30
        const h = parseInt(hours)
        const newH = h === 0 ? 23 : h - 1
        handleTimeChange(newH.toString().padStart(2, '0'), '30')
      }
    }

    const handleHoursInput = (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = e.target.value.replace(/\D/g, '').slice(0, 2)
      if (val === '') {
        setHours('')
        return
      }
      const num = parseInt(val)
      if (num >= 0 && num <= 23) {
        const paddedVal = val.padStart(2, '0')
        setHours(paddedVal)
        onChange?.(`${paddedVal}:${minutes}`)
      }
    }

    const handleMinutesInput = (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = e.target.value.replace(/\D/g, '').slice(0, 2)
      if (val === '') {
        setMinutes('')
        return
      }
      const num = parseInt(val)
      // Snap to nearest 30-minute interval
      const snappedMinutes = num < 15 ? '00' : num < 45 ? '30' : '00'
      setMinutes(snappedMinutes)
      onChange?.(`${hours}:${snappedMinutes}`)
    }

    const handleInputBlur = (type: 'hours' | 'minutes') => {
      if (type === 'hours' && hours === '') {
        setHours('00')
        onChange?.(`00:${minutes}`)
      }
      if (type === 'minutes' && minutes === '') {
        setMinutes('00')
        onChange?.(`${hours}:00`)
      }
    }

    return (
      <div ref={setRefs} className="relative w-full">
        <button
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          disabled={disabled}
          className={cn(
            'flex h-10 w-full rounded-md border-2 border-white/20 bg-white px-3 py-2 text-sm font-semibold text-gray-900 backdrop-blur-sm',
            'focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 focus:ring-offset-1',
            'disabled:cursor-not-allowed disabled:opacity-50',
            'items-center justify-center gap-2'
          )}
        >
          <span className="text-lg tracking-wider">{hours}:{minutes}</span>
        </button>

        {isOpen && !disabled && (
          <div className="absolute top-full left-0 mt-2 z-50 w-full bg-white border-2 border-white/20 rounded-lg shadow-lg p-4 backdrop-blur-sm">
            <div className="flex items-center justify-between gap-4">
              {/* Hours */}
              <div className="flex flex-col items-center gap-2">
                <button
                  type="button"
                  onClick={incrementHours}
                  className="p-1 hover:bg-gray-100 rounded-md transition-colors"
                  aria-label="Increase hours"
                >
                  <ChevronUp className="w-5 h-5 text-gray-900" />
                </button>

                <input
                  type="text"
                  value={hours}
                  onChange={handleHoursInput}
                  onBlur={() => handleInputBlur('hours')}
                  onFocus={(e) => e.target.select()}
                  maxLength={2}
                  inputMode="numeric"
                  className="w-12 h-12 text-center text-lg font-bold border-2 border-gray-300 rounded-md focus:outline-none focus:border-accent-500 focus:ring-2 focus:ring-accent-500/20 text-gray-900"
                />

                <button
                  type="button"
                  onClick={decrementHours}
                  className="p-1 hover:bg-gray-100 rounded-md transition-colors"
                  aria-label="Decrease hours"
                >
                  <ChevronDown className="w-5 h-5 text-gray-900" />
                </button>

                <span className="text-xs text-gray-500 font-medium mt-1">Hours</span>
              </div>

              {/* Separator */}
              <div className="text-2xl font-bold text-gray-900 h-24 flex items-center">:</div>

              {/* Minutes */}
              <div className="flex flex-col items-center gap-2">
                <button
                  type="button"
                  onClick={incrementMinutes}
                  className="p-1 hover:bg-gray-100 rounded-md transition-colors"
                  aria-label="Increase minutes"
                >
                  <ChevronUp className="w-5 h-5 text-gray-900" />
                </button>

                <input
                  type="text"
                  value={minutes}
                  onChange={handleMinutesInput}
                  onBlur={() => handleInputBlur('minutes')}
                  onFocus={(e) => e.target.select()}
                  maxLength={2}
                  inputMode="numeric"
                  className="w-12 h-12 text-center text-lg font-bold border-2 border-gray-300 rounded-md focus:outline-none focus:border-accent-500 focus:ring-2 focus:ring-accent-500/20 text-gray-900"
                />

                <button
                  type="button"
                  onClick={decrementMinutes}
                  className="p-1 hover:bg-gray-100 rounded-md transition-colors"
                  aria-label="Decrease minutes"
                >
                  <ChevronDown className="w-5 h-5 text-gray-900" />
                </button>

                <span className="text-xs text-gray-500 font-medium mt-1">Minutes</span>
              </div>
            </div>

            {/* Quick select presets */}
            <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-3 gap-2">
              {[
                { label: 'Morning', time: '09:00' },
                { label: 'Lunch', time: '13:00' },
                { label: 'Evening', time: '18:00' },
              ].map((preset) => (
                <button
                  key={preset.time}
                  type="button"
                  onClick={() => {
                    const [h, m] = preset.time.split(':')
                    handleTimeChange(h, m)
                    setIsOpen(false)
                  }}
                  className="px-3 py-2 text-xs font-medium bg-primary-100 text-primary-900 hover:bg-primary-200 rounded-md transition-colors"
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }
)
TimePicker.displayName = 'TimePicker'

export { TimePicker }
