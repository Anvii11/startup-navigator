import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { PageShell } from '@/shared/ui/PageShell'
import { EmptyState } from '@/shared/ui/EmptyState'
import { Skeleton } from '@/shared/ui/Skeleton'
import { useUserSavedIdeas, useRemoveSavedIdeaMutation } from '@/features/content/hooks'

export default function SavedIdeasPage() {
  const savedIdeasQuery = useUserSavedIdeas()
  const removeMutation = useRemoveSavedIdeaMutation()

  const savedList = savedIdeasQuery.data || []

  const handleRemove = (articleId) => {
    removeMutation.mutate(articleId, {
      onSuccess: () => toast.success('Removed from saved ideas'),
      onError: () => toast.error('Could not remove idea'),
    })
  }

  return (
    <PageShell
      title="Saved Ideas"
      description="Manage your bookmarked startup and manufacturing blueprints."
    >
      <div className="space-y-6">
        {savedIdeasQuery.isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-24 w-full rounded-2xl" />
            ))}
          </div>
        ) : savedList.length === 0 ? (
          <EmptyState
            title="No saved ideas yet"
            message="Click the bookmark icon on any startup idea card in Explore to save it here."
          />
        ) : (
          <div className="grid gap-4">
            {savedList.map((item) => {
              const article = item.article
              const savedDate = new Date(item.saved_at).toLocaleDateString(undefined, {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
              })

              return (
                <div
                  key={item.id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl border border-border bg-white p-5 shadow-xs hover:border-accent/40 transition"
                >
                  <div className="space-y-1 flex-1">
                    <div className="flex flex-wrap items-center gap-2 text-xs">
                      <span
                        className="rounded-md px-2 py-0.5 font-bold text-white text-[10px]"
                        style={{ backgroundColor: article.category?.color || '#1a6b4a' }}
                      >
                        {article.category?.name || 'General'}
                      </span>
                      <span className="capitalize font-semibold text-slate-600">• {article.difficulty}</span>
                      <span className="text-ink-muted">Saved on {savedDate}</span>
                    </div>

                    <Link to={`/articles/${article.slug}`}>
                      <h3 className="font-display text-base font-bold text-ink hover:text-accent transition">
                        {article.title}
                      </h3>
                    </Link>

                    <p className="text-xs text-ink-muted line-clamp-1">
                      {article.summary}
                    </p>
                  </div>

                  <div className="flex items-center gap-2 shrink-0 border-t sm:border-t-0 pt-3 sm:pt-0 border-border/60">
                    <Link
                      to={`/articles/${article.slug}`}
                      className="rounded-xl bg-accent px-4 py-2 text-xs font-semibold text-white hover:bg-accent-hover transition"
                    >
                      Open Idea Details →
                    </Link>

                    <button
                      type="button"
                      onClick={() => handleRemove(item.article_id)}
                      className="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-700 hover:bg-rose-100 transition"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </PageShell>
  )
}
