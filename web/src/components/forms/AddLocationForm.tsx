import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { locationApi } from '@/lib/api'
import { Button, Input, Alert, Spinner } from '@/components/ui'
import { Dialog } from '@/components/ui'

interface AddLocationFormProps {
  onSuccess?: () => void
}

export function AddLocationForm({ onSuccess }: AddLocationFormProps) {
  const [slug, setSlug] = useState('')
  const [error, setError] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (processedSlug: string) => locationApi.create(processedSlug),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['locations'] })
      setSlug('')
      setError(null)
      onSuccess?.()
    },
    onError: (err: unknown) => {
      const error = err as { message?: string }
      setError(error.message || 'Failed to add location')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!slug.trim()) {
      setError('Please enter a location slug')
      return
    }

    let processedSlug = slug.trim()
    // Extract slug from full URL if provided
    if (processedSlug.includes('/clubs/')) {
      const parts = processedSlug.split('/clubs/')
      if (parts.length > 1) {
        processedSlug = parts[1].split(/[/?]/)[0] // Take everything before / or ?
      }
    }

    mutation.mutate(processedSlug)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <Alert variant="error">
          {error}
        </Alert>
      )}

      <div className="space-y-2">
        <label htmlFor="slug" className="text-sm font-medium text-white">
          Location Slug
        </label>
        <Input
          id="slug"
          placeholder="e.g., club-name-city or https://playtomic.com/clubs/club-name-city"
          value={slug}
          onChange={(e) => setSlug(e.target.value)}
          disabled={mutation.isPending}
          className="text-white"
        />
        <p className="text-xs text-white/60">
          Enter the slug identifier or full Playtomic URL for the location (slug will be extracted automatically from URLs)
        </p>
      </div>

      <div className="flex justify-end space-x-2">
        <Dialog.Close>
          <Button variant="outline" disabled={mutation.isPending}>
            Cancel
          </Button>
        </Dialog.Close>
        <Button disabled={mutation.isPending} type="submit">
          {mutation.isPending ? (
            <>
              <Spinner className="mr-2 h-4 w-4" />
              Adding...
            </>
          ) : (
            'Add Location'
          )}
        </Button>
      </div>
    </form>
  )
}
