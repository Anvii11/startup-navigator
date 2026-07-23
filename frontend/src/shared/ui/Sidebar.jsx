import { NavLink } from 'react-router-dom'

const linkClass = ({ isActive }) =>
  [
    'block rounded-lg px-3 py-2 text-sm font-medium transition',
    isActive
      ? 'bg-accent-soft text-accent'
      : 'text-ink-muted hover:bg-surface hover:text-ink',
  ].join(' ')

export function Sidebar({ items = [] }) {
  return (
    <aside className="hidden w-56 shrink-0 border-r border-border bg-white/40 p-4 lg:block">
      <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-wide text-ink-muted">
        Navigation
      </p>
      <nav className="flex flex-col gap-1" aria-label="Sidebar">
        {items.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.end} className={linkClass}>
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

export const dashboardSidebarItems = [
  { to: '/dashboard', label: 'Overview', end: true },
  { to: '/dashboard/saved', label: 'Saved ideas' },
  { to: '/dashboard/chats', label: 'Chat history' },
]

export const adminSidebarItems = [
  { to: '/admin', label: 'Dashboard', end: true },
  { to: '/admin/articles', label: 'Ideas' },
  { to: '/admin/categories', label: 'Categories' },
  { to: '/admin/resources', label: 'Resources' },
  { to: '/admin/users', label: 'Users' },
  { to: '/admin/analytics', label: 'Analytics' },
]
