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
    mutationFn: (data: { slug: string; provider: string }) => locationApi.create(data.slug, data.provider),
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
      setError('Please enter a location URL')
      return
    }

    const url = slug.trim()
    let processedSlug = url
    let provider: string | null = null

    // Extract provider and slug from URL
    try {
      const urlObj = new URL(url)
      const hostname = urlObj.hostname // e.g., www.playtomic.com or playtomic.com

      // Extract provider (domain name without www or .com)
      const parts = hostname.replace('www.', '').split('.')
      provider = parts[0] // e.g., playtomic

      // Extract slug from path
      if (urlObj.pathname.includes('/clubs/')) {
        const pathParts = urlObj.pathname.split('/clubs/')
        if (pathParts.length > 1) {
          processedSlug = pathParts[1].split(/[/?]/)[0]
        }
      }
    } catch {
      setError('Please enter a valid URL')
      return
    }

    if (!processedSlug) {
      setError('Could not extract location slug from URL')
      return
    }

    mutation.mutate({ slug: processedSlug, provider: provider || '' })
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
          Location URL
        </label>
        <Input
          id="slug"
          placeholder="e.g., https://playtomic.com/clubs/club-name-city"
          value={slug}
          onChange={(e) => setSlug(e.target.value)}
          disabled={mutation.isPending}
          className="text-white"
        />
        <p className="text-xs text-white/60">
          Enter the full Playtomic URL for the location (provider and slug will be extracted automatically)
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
