import * as React from 'react'
import { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { ChevronDown, X, Check, Search } from 'lucide-react'

export interface MultiSelectProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'onChange'> {
  options: Array<{ value: string | number; label: string }>
  onChange?: (values: (string | number)[]) => void
  value?: (string | number)[]
  placeholder?: string
}

const MultiSelect = React.forwardRef<HTMLDivElement, MultiSelectProps>(
  ({ className, options, onChange, value = [], placeholder = 'Select items...', ...props }, ref) => {
    const [isOpen, setIsOpen] = useState(false)
    const [searchQuery, setSearchQuery] = useState('')
    const containerRef = useRef<HTMLDivElement>(null)
    const dropdownRef = useRef<HTMLDivElement>(null)

    const selectedValues = Array.isArray(value) ? value : []

    const filteredOptions = options.filter(option =>
      option.label.toLowerCase().includes(searchQuery.toLowerCase())
    )

    const selectedLabels = options
      .filter(opt => selectedValues.includes(opt.value))
      .map(opt => opt.label)

    const handleToggle = (optionValue: string | number) => {
      const newValues = selectedValues.includes(optionValue)
        ? selectedValues.filter(v => v !== optionValue)
        : [...selectedValues, optionValue]
      onChange?.(newValues)
    }

    const handleRemove = (e: React.MouseEvent, optionValue: string | number) => {
      e.stopPropagation()
      const newValues = selectedValues.filter(v => v !== optionValue)
      onChange?.(newValues)
    }

    const handleSelectAll = () => {
      if (selectedValues.length === options.length) {
        onChange?.([])
      } else {
        onChange?.(options.map(opt => opt.value))
      }
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
        <div
          ref={containerRef}
          className="relative"
        >
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
            <div className="flex flex-wrap gap-1 flex-1 min-h-[1.5rem] items-center">
              {selectedLabels.length > 0 ? (
                selectedLabels.map((label, idx) => {
                  const optionValue = options.find(opt => opt.label === label)?.value
                  return (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 px-2 py-1 bg-accent-500 text-white rounded text-sm font-medium"
                    >
                      {label}
                      <button
                        type="button"
                        onClick={(e) => optionValue !== undefined && handleRemove(e, optionValue)}
                        className="hover:text-accent-700 focus:outline-none"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  )
                })
              ) : (
                <span className="text-white/60 text-sm">{placeholder}</span>
              )}
            </div>
            <ChevronDown
              className={cn(
                'h-5 w-5 text-white/60 transition-transform duration-200 flex-shrink-0',
                isOpen && 'rotate-180'
              )}
            />
          </button>

          {/* Dropdown Menu */}
          {isOpen && (
            <div
              ref={dropdownRef}
              className={cn(
                'absolute top-full left-0 right-0 mt-2 z-50',
                'bg-secondary-700/90 backdrop-blur-md border-2 border-white/20 rounded-md shadow-xl',
                'max-h-80 overflow-hidden flex flex-col'
              )}
            >
              {/* Search Input */}
              <div className="p-3 border-b border-white/20 sticky top-0 bg-secondary-700/90">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-white/60" />
                  <input
                    type="text"
                    placeholder="Search..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className={cn(
                      'w-full pl-9 pr-3 py-2 text-sm rounded border-2 border-white/20 bg-white/10 text-white backdrop-blur-sm placeholder:text-white/50',
                      'focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500'
                    )}
                    onClick={(e) => e.stopPropagation()}
                  />
                </div>
              </div>

              {/* Select All Option */}
              {options.length > 0 && (
                <div className="px-3 py-2 border-b border-white/20 sticky top-12 bg-secondary-700/90">
                  <button
                    type="button"
                    onClick={handleSelectAll}
                    className={cn(
                      'w-full px-3 py-2 text-sm font-medium rounded text-left',
                      'transition-colors duration-150',
                      selectedValues.length === options.length
                        ? 'bg-accent-500 text-white'
                        : 'hover:bg-white/20 text-white'
                    )}
                  >
                    <div className="flex items-center gap-2">
                      <div
                        className={cn(
                          'w-4 h-4 rounded border-2 transition-colors',
                          selectedValues.length === options.length
                            ? 'bg-white border-white'
                            : 'border-white/30'
                        )}
                      >
                        {selectedValues.length === options.length && (
                          <Check className="h-3 w-3 text-white" />
                        )}
                      </div>
                      <span>
                        {selectedValues.length === options.length ? 'Deselect all' : 'Select all'}
                      </span>
                    </div>
                  </button>
                </div>
              )}

              {/* Options List */}
              <div className="overflow-y-auto flex-1">
                {filteredOptions.length > 0 ? (
                  filteredOptions.map((option) => {
                    const isSelected = selectedValues.includes(option.value)
                    return (
                      <button
                        key={option.value}
                        type="button"
                        onClick={() => handleToggle(option.value)}
                        className={cn(
                          'w-full px-3 py-2.5 text-sm text-left transition-colors duration-150',
                          'flex items-center gap-2 hover:bg-white/10 text-white',
                          isSelected && 'bg-accent-500/30'
                        )}
                      >
                        <div
                          className={cn(
                            'w-4 h-4 rounded border-2 transition-all',
                            isSelected
                              ? 'bg-accent-500 border-accent-500'
                              : 'border-white/30 hover:border-white/50'
                          )}
                        >
                          {isSelected && (
                            <Check className="h-3 w-3 text-white" />
                          )}
                        </div>
                        <span className={isSelected ? 'font-medium text-white' : 'text-white'}>
                          {option.label}
                        </span>
                      </button>
                    )
                  })
                ) : (
                  <div className="px-3 py-8 text-center text-sm text-white/60">
                    No options found
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }
)
MultiSelect.displayName = 'MultiSelect'

export { MultiSelect }
