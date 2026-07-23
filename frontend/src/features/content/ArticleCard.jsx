import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { DifficultyBadge } from './DifficultyBadge'
import { useAuth } from '@/features/auth/AuthContext'
import {
  useUserSavedIdeaIds,
  useSaveIdeaMutation,
  useRemoveSavedIdeaMutation,
} from './hooks'

export function ArticleCard({ article }) {
  if (!article) return null

  const { isAuthenticated } = useAuth()
  const savedIdeaIdsQuery = useUserSavedIdeaIds()
  const saveMutation = useSaveIdeaMutation()
  const removeMutation = useRemoveSavedIdeaMutation()

  const savedIds = savedIdeaIdsQuery.data || []
  const isSaved = savedIds.includes(article.id)

  const handleSaveToggle = (e) => {
    e.preventDefault()
    e.stopPropagation()

    if (!isAuthenticated) {
      toast('Please login to save ideas.', { icon: '🔒' })
      return
    }

    if (isSaved) {
      removeMutation.mutate(article.id, {
        onSuccess: () => toast.success('Idea removed from saved'),
        onError: () => toast.error('Could not remove idea'),
      })
    } else {
      saveMutation.mutate(article.id, {
        onSuccess: () => toast.success('Idea saved!'),
        onError: () => toast.error('Could not save idea'),
      })
    }
  }

  // Extract / infer structured card metrics
  const tags = article.tags || []
  const categoryName = article.category?.name || 'General'

  // Investment estimation
  let investmentText = 'Bootstrapped'
  if (tags.includes('investment-high') || tags.includes('cnc')) {
    investmentText = '₹25 Lakh+'
  } else if (tags.includes('investment-medium') || tags.includes('iot') || tags.includes('telemetry')) {
    investmentText = '₹10 - ₹25 Lakh'
  } else if (tags.includes('investment-low') || tags.includes('bootstrap')) {
    investmentText = 'Under ₹10 Lakh'
  }

  // AI Level estimation
  let aiLevel = 'Hybrid AI'
  if (tags.includes('ai-high') || tags.includes('chatgpt') || categoryName.includes('AI') || categoryName.includes('Artificial Intelligence')) {
    aiLevel = 'AI Core'
  } else if (tags.includes('ai-non-ai') || tags.includes('packaging') || tags.includes('cnc')) {
    aiLevel = 'Hardware/Ops'
  }

  const marketPotential = 'High Growth'

  return (
    <motion.article
      whileHover={{ y: -3 }}
      transition={{ duration: 0.2 }}
      className="group flex h-full flex-col overflow-hidden rounded-2xl border border-border bg-white shadow-xs hover:shadow-md transition-all relative"
    >
      <Link to={`/articles/${article.slug}`} className="block overflow-hidden relative">
        <div className="aspect-[16/9] overflow-hidden bg-accent-soft relative">
          {article.thumbnail ? (
            <img
              src={article.thumbnail}
              alt={article.title}
              className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
              loading="lazy"
            />
          ) : null}
          <div className="absolute top-3 left-3 flex flex-wrap gap-1.5">
            <span
              className="rounded-md px-2 py-0.5 text-[11px] font-semibold text-white shadow-xs"
              style={{ backgroundColor: article.category?.color || '#1a6b4a' }}
            >
              {categoryName}
            </span>
          </div>

          {/* Bookmark / Save Button */}
          <button
            type="button"
            onClick={handleSaveToggle}
            title={isSaved ? 'Saved' : 'Save idea'}
            className={[
              'absolute top-3 right-3 rounded-full p-2 text-xs font-semibold transition shadow-sm z-10 flex items-center gap-1',
              isSaved
                ? 'bg-amber-400 text-slate-900 font-bold'
                : 'bg-white/90 text-slate-700 hover:bg-white hover:text-accent',
            ].join(' ')}
          >
            <svg
              className="h-4 w-4"
              fill={isSaved ? 'currentColor' : 'none'}
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
              />
            </svg>
            {isSaved ? <span className="text-[10px] pr-0.5">Saved ✓</span> : null}
          </button>
        </div>
      </Link>

      <div className="flex flex-1 flex-col justify-between p-4 space-y-3">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-ink-muted">
            <DifficultyBadge value={article.difficulty} />
            <span className="font-medium text-slate-500">{article.estimated_reading_time} min read</span>
          </div>

          <Link to={`/articles/${article.slug}`}>
            <h3 className="font-display text-base font-bold leading-snug text-ink transition group-hover:text-accent line-clamp-2">
              {article.title}
            </h3>
          </Link>

          <p className="line-clamp-2 text-xs text-ink-muted leading-relaxed">
            {article.summary}
          </p>
        </div>

        {/* Structured Metrics Bar */}
        <div className="space-y-2.5 pt-2 border-t border-border/60">
          <div className="grid grid-cols-3 gap-1 text-[11px] text-slate-600 bg-slate-50 p-2 rounded-xl border border-slate-100">
            <div className="flex flex-col">
              <span className="text-[9px] font-semibold uppercase text-slate-400">Investment</span>
              <span className="font-bold text-ink truncate">{investmentText}</span>
            </div>
            <div className="flex flex-col border-l border-slate-200 pl-1.5">
              <span className="text-[9px] font-semibold uppercase text-slate-400">AI Level</span>
              <span className="font-bold text-accent truncate">{aiLevel}</span>
            </div>
            <div className="flex flex-col border-l border-slate-200 pl-1.5">
              <span className="text-[9px] font-semibold uppercase text-slate-400">Market</span>
              <span className="font-bold text-emerald-700 truncate">{marketPotential}</span>
            </div>
          </div>

          <Link
            to={`/articles/${article.slug}`}
            className="flex items-center justify-center w-full rounded-xl bg-surface hover:bg-accent hover:text-white border border-border/80 py-2 text-xs font-semibold text-ink transition"
          >
            Read Blueprint →
          </Link>
        </div>
      </div>
    </motion.article>
  )
}
