import { Link } from '@tanstack/react-router'

export function Footer() {
  return (
    <footer className="border-t border-white/20 bg-secondary-700/50 backdrop-blur-sm">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="font-semibold text-white mb-4">Padel Watcher</h3>
            <p className="text-sm text-white/70">
              Track padel court availability and never miss your perfect game time.
            </p>
          </div>

          <div>
            <h4 className="font-medium text-white mb-4">Product</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/search" className="text-white/70 hover:text-accent-400">
                  Search Courts
                </Link>
              </li>
              <li>
                <Link to="/locations" className="text-white/70 hover:text-accent-400">
                  Locations
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium text-white mb-4">Support</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#" className="text-white/70 hover:text-accent-400">
                  Help Center
                </a>
              </li>
              <li>
                <a href="#" className="text-white/70 hover:text-accent-400">
                  Contact Us
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium text-white mb-4">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#" className="text-white/70 hover:text-accent-400">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#" className="text-white/70 hover:text-accent-400">
                  Terms of Service
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-white/20 text-center text-sm text-white/60">
          © {new Date().getFullYear()} Padel Watcher. All rights reserved.
        </div>
      </div>
    </footer>
  )
}
