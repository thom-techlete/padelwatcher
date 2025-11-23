import { Link } from '@tanstack/react-router'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Alert } from '@/components/ui'
import { Clock } from 'lucide-react'
import { useAuth } from '@/contexts'

export function PendingApprovalPage() {
  const { logout } = useAuth()

  return (
    <div className="container mx-auto flex min-h-[calc(100vh-200px)] items-center justify-center px-4 py-12">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-yellow-500/20">
            <Clock className="h-8 w-8 text-yellow-400" />
          </div>
          <CardTitle>Account Pending Approval</CardTitle>
          <CardDescription>Your registration is under review</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert variant="warning" title="Awaiting Admin Approval">
            Your account has been created successfully and is currently pending approval by an administrator.
            You'll be able to access all features once your account is approved.
          </Alert>
          <div className="space-y-2 text-sm text-white">
            <p>What happens next?</p>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li>An administrator will review your registration</li>
              <li>You'll receive an email once approved</li>
              <li>You can then log in and start using Padel Watcher</li>
            </ul>
          </div>
          <div className="flex gap-2 pt-4">
            <Button variant="outline" className="flex-1" onClick={logout}>
              Sign Out
            </Button>
            <Link to="/" className="flex-1">
              <Button variant="outline" className="w-full">
                Go Home
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
