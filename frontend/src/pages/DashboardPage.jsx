import { Link } from 'react-router-dom'
import { PageShell } from '@/shared/ui/PageShell'
import { Skeleton } from '@/shared/ui/Skeleton'
import { useUserDashboard } from '@/features/content/hooks'
import { useAuth } from '@/features/auth/AuthContext'

export default function DashboardPage() {
  const { user } = useAuth()
  const dashboardQuery = useUserDashboard()
  const data = dashboardQuery.data

  const loading = dashboardQuery.isLoading

  return (
    <PageShell
      title={`Welcome back, ${user?.full_name || 'Founder'}!`}
      description="Track your bookmarked startup ideas, recent AI searches, and industry activity."
    >
      <div className="space-y-8 max-w-5xl">
        {/* ── Stat Metric Cards ─────────────────────────────────────────── */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {/* 1. Saved Ideas Count */}
          <div className="rounded-2xl border border-border bg-white p-5 space-y-2 shadow-xs">
            <div className="flex items-center justify-between text-xs text-ink-muted">
              <span className="font-semibold uppercase tracking-wider text-[10px]">Saved Ideas</span>
              <span className="text-xl">🔖</span>
            </div>
            {loading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="flex items-baseline justify-between">
                <span className="font-display text-3xl font-bold text-ink">
                  {data?.saved_ideas_count ?? 0}
                </span>
                <Link to="/dashboard/saved" className="text-xs font-semibold text-accent hover:underline">
                  View saved →
                </Link>
              </div>
            )}
          </div>

          {/* 2. AI Searches Count */}
          <div className="rounded-2xl border border-border bg-white p-5 space-y-2 shadow-xs">
            <div className="flex items-center justify-between text-xs text-ink-muted">
              <span className="font-semibold uppercase tracking-wider text-[10px]">AI Searches</span>
              <span className="text-xl">🤖</span>
            </div>
            {loading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="flex items-baseline justify-between">
                <span className="font-display text-3xl font-bold text-ink">
                  {data?.ai_searches_count ?? 0}
                </span>
                <Link to="/dashboard/chats" className="text-xs font-semibold text-accent hover:underline">
                  View chats →
                </Link>
              </div>
            )}
          </div>

          {/* 3. Favourite Industry (if available) */}
          {loading ? (
            <div className="rounded-2xl border border-border bg-white p-5 space-y-2 shadow-xs sm:col-span-2 lg:col-span-1">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-8 w-32" />
            </div>
          ) : data?.favourite_industry ? (
            <div className="rounded-2xl border border-emerald-100 bg-emerald-50/50 p-5 space-y-2 shadow-xs sm:col-span-2 lg:col-span-1">
              <div className="flex items-center justify-between text-xs text-emerald-800 font-semibold">
                <span className="font-semibold uppercase tracking-wider text-[10px]">Top Saved Industry</span>
                <span className="text-xl">🌟</span>
              </div>
              <p className="font-display text-lg font-bold text-emerald-950 truncate">
                {data.favourite_industry}
              </p>
            </div>
          ) : null}
        </div>

        {/* ── Recent Searches Section ───────────────────────────────────── */}
        <div className="rounded-3xl border border-border bg-white p-6 space-y-4 shadow-xs">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-display text-lg font-bold text-ink">Recent AI Searches</h2>
              <p className="text-xs text-ink-muted">Queries you asked the Startup Navigator AI Assistant.</p>
            </div>
            <Link to="/dashboard/chats" className="text-xs font-semibold text-accent hover:underline">
              All history →
            </Link>
          </div>

          {loading ? (
            <Skeleton className="h-20 w-full rounded-2xl" />
          ) : !data?.recent_searches?.length ? (
            <p className="text-xs text-slate-500 italic">No recent AI searches found. Try asking the AI Assistant a question!</p>
          ) : (
            <div className="divide-y divide-border/60">
              {data.recent_searches.map((search) => {
                const searchDate = new Date(search.created_at).toLocaleDateString(undefined, {
                  month: 'short',
                  day: 'numeric',
                })
                return (
                  <div key={search.id} className="py-3 flex items-center justify-between gap-4 text-xs">
                    <div className="flex items-center gap-2 truncate">
                      <span>🤖</span>
                      <span className="font-semibold text-ink truncate">{search.title}</span>
                    </div>
                    <span className="text-slate-400 shrink-0">{searchDate}</span>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* ── Recent Saved Ideas Section ────────────────────────────────── */}
        <div className="rounded-3xl border border-border bg-white p-6 space-y-4 shadow-xs">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-display text-lg font-bold text-ink">Recently Saved Ideas</h2>
              <p className="text-xs text-ink-muted">Startup and manufacturing playbooks you saved.</p>
            </div>
            <Link to="/dashboard/saved" className="text-xs font-semibold text-accent hover:underline">
              View all →
            </Link>
          </div>

          {loading ? (
            <Skeleton className="h-24 w-full rounded-2xl" />
          ) : !data?.recent_saved_ideas?.length ? (
            <p className="text-xs text-slate-500 italic">No saved ideas yet. Click the bookmark icon on any idea card to save it.</p>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2">
              {data.recent_saved_ideas.map((item) => {
                const article = item.article
                return (
                  <Link
                    key={item.id}
                    to={`/articles/${article.slug}`}
                    className="flex flex-col justify-between p-4 rounded-2xl border border-border/80 bg-slate-50/50 hover:bg-white hover:border-accent transition group"
                  >
                    <div className="space-y-1">
                      <span
                        className="rounded-md px-2 py-0.5 text-[9px] font-bold text-white inline-block"
                        style={{ backgroundColor: article.category?.color || '#1a6b4a' }}
                      >
                        {article.category?.name}
                      </span>
                      <h3 className="font-display text-sm font-bold text-ink group-hover:text-accent transition line-clamp-1">
                        {article.title}
                      </h3>
                    </div>
                    <span className="text-[11px] font-semibold text-accent pt-2 block">Read Blueprint →</span>
                  </Link>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </PageShell>
  )
}
