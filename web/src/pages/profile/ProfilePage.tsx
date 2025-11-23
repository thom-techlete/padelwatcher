import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/hooks/useAuth'
import { authApi, type UpdateProfileRequest, type UpdatePasswordRequest } from '@/lib/api/auth'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Card } from '@/components/ui/Card'
import { Alert } from '@/components/ui/Alert'

interface ApiError {
  response?: {
    data?: {
      message?: string
    }
  }
}

export function ProfilePage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()

  // Profile update state
  const [email, setEmail] = useState(user?.email || '')
  const [profileSuccess, setProfileSuccess] = useState('')
  const [profileError, setProfileError] = useState('')

  // Password update state
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [passwordSuccess, setPasswordSuccess] = useState('')
  const [passwordError, setPasswordError] = useState('')

  const updateProfileMutation = useMutation({
    mutationFn: (data: UpdateProfileRequest) => authApi.updateProfile(data),
    onSuccess: (response) => {
      setProfileSuccess('Profile updated successfully')
      setProfileError('')
      // Update the user in the query cache
      queryClient.invalidateQueries({ queryKey: ['currentUser'] })
      // Update email state from response
      setEmail(response.user.email)
    },
    onError: (error: ApiError) => {
      setProfileError(error.response?.data?.message || 'Failed to update profile')
      setProfileSuccess('')
    },
  })

  const updatePasswordMutation = useMutation({
    mutationFn: (data: UpdatePasswordRequest) => authApi.updatePassword(data),
    onSuccess: () => {
      setPasswordSuccess('Password updated successfully')
      setPasswordError('')
      // Clear password fields
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    },
    onError: (error: ApiError) => {
      setPasswordError(error.response?.data?.message || 'Failed to update password')
      setPasswordSuccess('')
    },
  })

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setProfileSuccess('')
    setProfileError('')

    // Only update if email changed
    if (email !== user?.email) {
      updateProfileMutation.mutate({ email })
    } else {
      setProfileError('No changes detected')
    }
  }

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setPasswordSuccess('')
    setPasswordError('')

    // Validate passwords
    if (newPassword.length < 6) {
      setPasswordError('New password must be at least 6 characters long')
      return
    }

    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match')
      return
    }

    updatePasswordMutation.mutate({
      current_password: currentPassword,
      new_password: newPassword,
    })
  }

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert variant="error">Please log in to view your profile</Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8 text-white">Profile Settings</h1>

      <div className="space-y-8">
        {/* Profile Information */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">Profile Information</h2>

          <form onSubmit={handleProfileSubmit} className="space-y-4">
            <div>
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                value={user.username}
                disabled
                className="bg-white/5"
              />
              <p className="text-sm text-white/60 mt-1">Username cannot be changed</p>
            </div>

            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            {profileSuccess && (
              <Alert variant="success">{profileSuccess}</Alert>
            )}

            {profileError && (
              <Alert variant="error">{profileError}</Alert>
            )}

            <div className="flex justify-end">
              <Button
                type="submit"
                disabled={updateProfileMutation.isPending || email === user.email}
              >
                {updateProfileMutation.isPending ? 'Updating...' : 'Update Profile'}
              </Button>
            </div>
          </form>
        </Card>

        {/* Change Password */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">Change Password</h2>

          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <div>
              <Label htmlFor="current-password">Current Password</Label>
              <Input
                id="current-password"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
              />
            </div>

            <div>
              <Label htmlFor="new-password">New Password</Label>
              <Input
                id="new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={6}
              />
              <p className="text-sm text-white/60 mt-1">Minimum 6 characters</p>
            </div>

            <div>
              <Label htmlFor="confirm-password">Confirm New Password</Label>
              <Input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>

            {passwordSuccess && (
              <Alert variant="success">{passwordSuccess}</Alert>
            )}

            {passwordError && (
              <Alert variant="error">{passwordError}</Alert>
            )}

            <div className="flex justify-end">
              <Button
                type="submit"
                disabled={updatePasswordMutation.isPending}
              >
                {updatePasswordMutation.isPending ? 'Updating...' : 'Update Password'}
              </Button>
            </div>
          </form>
        </Card>

        {/* Account Information */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">Account Information</h2>

          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-white/70">Account Status:</span>
              <span className="font-medium">
                {user.approved ? (
                  <span className="text-green-400">Approved</span>
                ) : (
                  <span className="text-yellow-400">Pending Approval</span>
                )}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-white/70">Account Type:</span>
              <span className="font-medium">
                {user.is_admin ? 'Administrator' : 'User'}
              </span>
            </div>

            {user.created_at && (
              <div className="flex justify-between">
                <span className="text-white/70">Member Since:</span>
                <span className="font-medium">
                  {new Date(user.created_at).toLocaleDateString()}
                </span>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
