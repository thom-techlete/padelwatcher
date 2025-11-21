import { Link } from '@tanstack/react-router'
import { Button, Card, CardHeader, CardTitle, CardContent } from '@/components/ui'
import { Search, Bell, Calendar, Shield } from 'lucide-react'
import { useAuth } from '@/contexts'

export function HomePage() {
  const { isAuthenticated } = useAuth()

  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-500 via-primary-600 to-secondary-700 text-white">
        <div className="container mx-auto px-4 py-20">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-6">
              Never Miss Your Perfect Padel Game
            </h1>
            <p className="text-xl mb-8 text-primary-100">
              Track court availability across multiple locations and get notified when your ideal time slots open up
            </p>
            <div className="flex gap-4 justify-center">
              {isAuthenticated ? (
                <Link to="/dashboard">
                  <Button size="lg" variant="secondary">
                    Go to Dashboard
                  </Button>
                </Link>
              ) : (
                <>
                  <Link to="/register">
                    <Button size="lg" variant="secondary">
                      Get Started Free
                    </Button>
                  </Link>
                  <Link to="/login">
                    <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-primary-500">
                      Sign In
                    </Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-secondary-800">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-white">
            How Padel Watcher Works
          </h2>
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-accent-100 flex items-center justify-center mb-4">
                  <Search className="h-6 w-6 text-accent-500" />
                </div>
                <CardTitle>Search Courts</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-white/80">
                  Search for available courts across multiple locations and time slots
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-white/10 flex items-center justify-center mb-4">
                  <Calendar className="h-6 w-6 text-accent-400" />
                </div>
                <CardTitle>Set Preferences</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-white/80">
                  Define your preferred times, locations, and court types
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-accent-100 flex items-center justify-center mb-4">
                  <Bell className="h-6 w-6 text-accent-500" />
                </div>
                <CardTitle>Get Notified</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-white/80">
                  Receive instant notifications when courts become available
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-white/10 flex items-center justify-center mb-4">
                  <Shield className="h-6 w-6 text-accent-400" />
                </div>
                <CardTitle>Book Fast</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-white/80">
                  Never miss out on your ideal time slot again
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      {!isAuthenticated && (
        <section className="py-20">
          <div className="container mx-auto px-4">
            <Card className="max-w-2xl mx-auto border-2 border-primary-500">
              <CardContent className="p-12 text-center">
                <h2 className="text-3xl font-bold mb-4 text-white">
                  Ready to Start Tracking?
                </h2>
                <p className="text-white/80 mb-6">
                  Join Padel Watcher today and never miss your perfect game time
                </p>
                <Link to="/register">
                  <Button size="lg">
                    Create Free Account
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </section>
      )}
    </div>
  )
}
