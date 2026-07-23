import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useAdminArticles, useAdminCategories, useAdminResources } from '@/features/content/hooks'
import { Skeleton } from '@/shared/ui/Skeleton'

export default function AdminDashboardPage() {
  const articles = useAdminArticles({ page_size: 1 })
  const categories = useAdminCategories({ page_size: 1 })
  const resources = useAdminResources({ page_size: 1 })

  const cards = useMemo(
    () => [
      { label: 'Ideas', value: articles.data?.total ?? '—', to: '/admin/articles', hint: 'Manage startup ideas' },
      { label: 'Categories', value: categories.data?.total ?? '—', to: '/admin/categories', hint: 'Topic taxonomy' },
      { label: 'Resources', value: resources.data?.total ?? '—', to: '/admin/resources', hint: 'Curated links' },
    ],
    [articles.data, categories.data, resources.data],
  )

  return (
    <div className="space-y-8">
      <header>
        <h1 className="font-display text-3xl text-ink">Admin dashboard</h1>
        <p className="mt-2 text-ink-muted">Content management overview for Startup Navigator.</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-3">
        {cards.map((card) => (
          <Link
            key={card.label}
            to={card.to}
            className="rounded-2xl border border-border bg-white p-5 transition hover:-translate-y-0.5 hover:border-accent/40"
          >
            <p className="text-sm text-ink-muted">{card.label}</p>
            {articles.isLoading || categories.isLoading || resources.isLoading ? (
              <Skeleton className="mt-3 h-8 w-16" />
            ) : (
              <p className="mt-2 font-display text-3xl text-ink">{card.value}</p>
            )}
            <p className="mt-2 text-xs text-ink-muted">{card.hint}</p>
          </Link>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-dashed border-border bg-white/60 p-6">
          <h2 className="font-display text-xl text-ink">Users</h2>
          <p className="mt-2 text-sm text-ink-muted">User management arrives in a later phase.</p>
        </div>
        <div className="rounded-2xl border border-dashed border-border bg-white/60 p-6">
          <h2 className="font-display text-xl text-ink">Analytics</h2>
          <p className="mt-2 text-sm text-ink-muted">Search logs and analytics arrive with the AI phase.</p>
        </div>
      </div>
    </div>
  )
}
