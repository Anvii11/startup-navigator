import { NavLink, Link } from 'react-router-dom'
import { useAuth } from '@/features/auth/AuthContext'

const navLinkClass = ({ isActive }) =>
  [
    'rounded-xl px-3.5 py-2 text-sm font-medium transition',
    isActive
      ? 'bg-accent-soft text-accent font-semibold shadow-2xs'
      : 'text-ink-muted hover:bg-white/80 hover:text-ink',
  ].join(' ')

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()

  return (
    <header className="sticky top-0 z-40 border-b border-border/80 bg-surface/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-accent text-white font-bold text-base shadow-sm">
            💡
          </div>
          <div className="flex flex-col">
            <span className="font-display text-lg font-bold tracking-tight text-ink leading-tight">
              Startup Navigator
            </span>
            <span className="text-[10px] font-semibold text-accent uppercase tracking-wider">
              Ideas Platform
            </span>
          </div>
        </Link>

        {/* Desktop Primary Nav */}
        <nav className="hidden items-center gap-1.5 md:flex" aria-label="Primary">
          <NavLink to="/explore" className={navLinkClass}>
            Explore Ideas
          </NavLink>
          <NavLink
            to="/search"
            className={({ isActive }) =>
              [
                'rounded-xl px-3.5 py-2 text-sm font-semibold transition flex items-center gap-1.5',
                isActive
                  ? 'bg-accent text-white shadow-xs'
                  : 'bg-emerald-50 text-emerald-800 hover:bg-emerald-100',
              ].join(' ')
            }
          >
            <span>✨ AI Search</span>
          </NavLink>
          <NavLink to="/resources" className={navLinkClass}>
            Resources
          </NavLink>
          <NavLink to="/about" className={navLinkClass}>
            About
          </NavLink>
          <NavLink to="/contact" className={navLinkClass}>
            Contact
          </NavLink>
        </nav>

        {/* User / Auth Nav */}
        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <>
              <NavLink to="/dashboard" className={navLinkClass}>
                Dashboard
              </NavLink>
              {user?.role === 'admin' ? (
                <NavLink
                  to="/admin"
                  className={({ isActive }) =>
                    [
                      'rounded-xl px-3 py-1.5 text-xs font-bold transition uppercase tracking-wider',
                      isActive
                        ? 'bg-slate-900 text-white'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200',
                    ].join(' ')
                  }
                >
                  CMS Admin
                </NavLink>
              ) : null}
              <button
                type="button"
                onClick={logout}
                className="rounded-xl border border-border bg-white px-3.5 py-2 text-xs font-semibold text-ink-muted transition hover:text-rose-600 hover:border-rose-200"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className={navLinkClass}>
                Log in
              </NavLink>
              <Link
                to="/register"
                className="rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-white transition hover:bg-accent-hover shadow-xs"
              >
                Sign up
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
