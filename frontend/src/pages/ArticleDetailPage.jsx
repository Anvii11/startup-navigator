import { useEffect, useState, useMemo } from 'react'
import { Link, useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  useArticle,
  useRelatedArticles,
  useUserSavedIdeaIds,
  useSaveIdeaMutation,
  useRemoveSavedIdeaMutation,
} from '@/features/content/hooks'
import { useAuth } from '@/features/auth/AuthContext'
import { ArticleCard } from '@/features/content/ArticleCard'
import { DifficultyBadge } from '@/features/content/DifficultyBadge'
import { Loading } from '@/shared/ui/Loading'
import { ErrorState } from '@/shared/ui/ErrorState'

export default function ArticleDetailPage() {
  const { slug } = useParams()
  const articleQuery = useArticle(slug)
  const relatedQuery = useRelatedArticles(slug)
  const [progress, setProgress] = useState(0)
  const [activeTab, setActiveTab] = useState('overview')
  const [copied, setCopied] = useState(false)

  const { isAuthenticated } = useAuth()
  const savedIdeaIdsQuery = useUserSavedIdeaIds()
  const saveMutation = useSaveIdeaMutation()
  const removeMutation = useRemoveSavedIdeaMutation()

  const article = articleQuery.data
  const savedIds = savedIdeaIdsQuery.data || []
  const isSaved = article ? savedIds.includes(article.id) : false

  const handleSaveToggle = () => {
    if (!isAuthenticated) {
      toast('Please login to save ideas.', { icon: '🔒' })
      return
    }
    if (!article) return

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

  useEffect(() => {
    const onScroll = () => {
      const el = document.documentElement
      const total = el.scrollHeight - el.clientHeight
      setProgress(total > 0 ? (el.scrollTop / total) * 100 : 0)
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [slug])

  // Infer structured idea details
  const ideaDetails = useMemo(() => {
    if (!article) return null

    const tags = article.tags || []
    const categoryName = article.category?.name || 'General'

    // Investment Tier
    let investmentTier = 'Under ₹10 Lakh'
    let investmentDetail = 'Low upfront capital required. Accessible through open-source tools, low-cost components, and small-batch MVP pilots.'
    if (tags.includes('investment-high') || tags.includes('cnc')) {
      investmentTier = '₹25 Lakh+'
      investmentDetail = 'Requires industrial machinery, inventory stock, specialized engineering talent, or regulatory compliance reserves.'
    } else if (tags.includes('investment-medium') || tags.includes('iot')) {
      investmentTier = '₹10 - ₹25 Lakh'
      investmentDetail = 'Moderate capital for initial hardware prototyping, supplier tooling, or early pilot customer acquisition.'
    }

    // AI Opportunity
    let aiOpportunity = 'AI-assisted customer support, automated content generation, and LLM-driven research.'
    if (tags.includes('ai-high') || categoryName.includes('AI')) {
      aiOpportunity = 'Core LLM/Vision model integration, custom agentic workflows, fine-tuned domain models, and predictive analytics.'
    } else if (categoryName.includes('Manufacturing') || tags.includes('hardware')) {
      aiOpportunity = 'Predictive maintenance, automated defect inspection using computer vision, supply chain optimization, and automated CAD/BOM generation.'
    }

    // Business Model
    let businessModel = 'SaaS Subscription (Tiered monthly/annual recurring revenue)'
    if (categoryName.includes('Manufacturing') || tags.includes('packaging') || tags.includes('cnc')) {
      businessModel = 'Direct Unit Manufacturing + Contract Retainers (Cost-plus or per-unit pricing)'
    } else if (categoryName.includes('GST') || categoryName.includes('Registration')) {
      businessModel = 'Professional Service Fees + Annual Recurring Compliance Subscriptions'
    } else if (categoryName.includes('Funding')) {
      businessModel = 'Platform Transaction Fees / Success Fees + Premium Founder Membership'
    }

    // Target Customers
    let targetCustomers = 'Early-stage founders, startup operators, and SMB business owners.'
    if (categoryName.includes('Manufacturing') || tags.includes('hardware')) {
      targetCustomers = 'Hardware startups, D2C brands, IoT device manufacturers, and industrial OEM component buyers.'
    } else if (categoryName.includes('Hiring')) {
      targetCustomers = 'Scaling venture-backed startups, VP of Engineering, and talent acquisition teams.'
    }

    return {
      investmentTier,
      investmentDetail,
      aiOpportunity,
      businessModel,
      targetCustomers,
      roadmap: [
        {
          phase: 'Phase 1: Market Validation & Specs (Days 1–30)',
          tasks: 'Define core target personas, conduct 15 customer discovery calls, specify hardware/software architecture, and audit regulatory requirements.',
        },
        {
          phase: 'Phase 2: MVP & Prototype (Days 31–60)',
          tasks: 'Build functional V1 prototype/pilot service. Secure initial 3-5 pilot customers or beta agreement letters.',
        },
        {
          phase: 'Phase 3: Launch & GTM Execution (Days 61–90)',
          tasks: 'Execute targeted acquisition loop, establish recurring operational metrics, and optimize unit economics for scale.',
        },
      ],
    }
  }, [article])

  if (articleQuery.isLoading) return <Loading label="Loading idea details…" />
  if (articleQuery.isError) {
    return (
      <ErrorState
        title="Idea details unavailable"
        message="This startup idea may have been removed or is undergoing revision."
        onRetry={() => articleQuery.refetch()}
      />
    )
  }

  return (
    <article className="relative space-y-8">
      {/* Scroll progress bar */}
      <div className="fixed left-0 top-0 z-50 h-1 w-full bg-border/40">
        <div className="h-full bg-accent transition-[width] duration-150" style={{ width: `${progress}%` }} />
      </div>

      {/* Breadcrumb Navigation */}
      <nav className="flex flex-wrap items-center gap-2 text-sm text-ink-muted">
        <Link to="/explore" className="hover:text-ink">
          Explore Ideas
        </Link>
        <span>/</span>
        <Link to={`/explore?category=${article.category.slug}`} className="hover:text-ink">
          {article.category.name}
        </Link>
        <span>/</span>
        <span className="text-ink font-medium truncate max-w-[280px]">{article.title}</span>
      </nav>

      {/* Hero Header Card */}
      <motion.header
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="overflow-hidden rounded-3xl border border-border bg-white shadow-sm"
      >
        <div className="aspect-[21/9] max-h-[360px] bg-accent-soft relative overflow-hidden">
          {article.thumbnail ? (
            <img src={article.thumbnail} alt={article.title} className="h-full w-full object-cover" />
          ) : null}
        </div>

        <div className="p-6 sm:p-10 space-y-6">
          <div className="flex flex-wrap items-center gap-3 text-xs">
            <span
              className="rounded-md px-3 py-1 font-bold text-white shadow-xs"
              style={{ backgroundColor: article.category?.color || '#1a6b4a' }}
            >
              {article.category?.name}
            </span>
            <DifficultyBadge value={article.difficulty} />
            <span className="text-ink-muted">· {article.estimated_reading_time} min read</span>
            <span className="text-ink-muted">· {article.view_count} views</span>
          </div>

          <h1 className="font-display text-3xl font-bold tracking-tight text-ink sm:text-4xl lg:text-5xl">
            {article.title}
          </h1>

          <p className="max-w-3xl text-lg text-ink-muted leading-relaxed">{article.summary}</p>

          <div className="flex flex-wrap items-center justify-between gap-4 border-t border-border pt-4">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-full bg-accent/10 flex items-center justify-center font-bold text-accent text-sm">
                {article.author.full_name?.charAt(0) || 'A'}
              </div>
              <p className="text-sm text-ink-muted">
                Curated by <span className="font-medium text-ink">{article.author.full_name}</span>
                {article.published_at
                  ? ` · ${new Date(article.published_at).toLocaleDateString()}`
                  : null}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={handleSaveToggle}
                className={[
                  'rounded-xl px-3.5 py-1.5 text-xs font-semibold transition flex items-center gap-1.5',
                  isSaved
                    ? 'bg-amber-400 text-slate-900 font-bold'
                    : 'border border-border bg-white text-ink hover:bg-slate-50',
                ].join(' ')}
              >
                <span>🔖</span>
                <span>{isSaved ? 'Saved ✓' : 'Save Idea'}</span>
              </button>

              <button
                type="button"
                className="rounded-xl border border-border px-3.5 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50 transition"
                onClick={() => {
                  navigator.clipboard?.writeText(window.location.href)
                  setCopied(true)
                  setTimeout(() => setCopied(false), 2000)
                }}
              >
                {copied ? '✓ Copied!' : 'Share Link'}
              </button>

              <Link
                to="/search"
                className="rounded-xl bg-accent px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-accent-hover transition shadow-xs flex items-center gap-1.5"
              >
                <span>✨ Ask AI Copilot</span>
              </Link>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Structured Blueprint Tabs / View */}
      <div className="flex border-b border-border text-sm font-semibold text-ink-muted">
        <button
          type="button"
          onClick={() => setActiveTab('overview')}
          className={`pb-3 px-4 transition border-b-2 ${
            activeTab === 'overview'
              ? 'border-accent text-accent'
              : 'border-transparent hover:text-ink'
          }`}
        >
          Blueprint Overview
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('roadmap')}
          className={`pb-3 px-4 transition border-b-2 ${
            activeTab === 'roadmap'
              ? 'border-accent text-accent'
              : 'border-transparent hover:text-ink'
          }`}
        >
          90-Day Execution Roadmap
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('full')}
          className={`pb-3 px-4 transition border-b-2 ${
            activeTab === 'full'
              ? 'border-accent text-accent'
              : 'border-transparent hover:text-ink'
          }`}
        >
          Full Content & Specs
        </button>
      </div>

      {/* Tab Contents */}
      {activeTab === 'overview' && ideaDetails ? (
        <div className="space-y-6">
          <div className="rounded-2xl border border-border bg-white p-6 space-y-3">
            <h3 className="font-display text-lg font-bold text-ink">Executive Summary</h3>
            <p className="text-sm leading-relaxed text-ink-muted">
              {article.summary}
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-2xl border border-border bg-white p-5 space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-accent">
                💰 Estimated Investment
              </span>
              <p className="font-display text-base font-bold text-ink">{ideaDetails.investmentTier}</p>
              <p className="text-xs text-ink-muted leading-relaxed">{ideaDetails.investmentDetail}</p>
            </div>

            <div className="rounded-2xl border border-border bg-white p-5 space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-accent">
                ⚡ Execution Difficulty
              </span>
              <div className="pt-1">
                <DifficultyBadge value={article.difficulty} />
              </div>
              <p className="text-xs text-ink-muted leading-relaxed pt-1">
                Requires structured technical execution and clear domain expertise.
              </p>
            </div>

            <div className="rounded-2xl border border-border bg-white p-5 space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-accent">
                🤖 AI & Automation Opportunities
              </span>
              <p className="text-xs text-ink-muted leading-relaxed pt-1">{ideaDetails.aiOpportunity}</p>
            </div>

            <div className="rounded-2xl border border-border bg-white p-5 space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-accent">
                💵 Business & Revenue Model
              </span>
              <p className="text-xs font-semibold text-ink leading-relaxed pt-1">{ideaDetails.businessModel}</p>
            </div>

            <div className="rounded-2xl border border-border bg-white p-5 space-y-2 sm:col-span-2 lg:col-span-2">
              <span className="text-xs font-bold uppercase tracking-wider text-accent">
                🎯 Target Customers
              </span>
              <p className="text-xs text-ink-muted leading-relaxed pt-1">{ideaDetails.targetCustomers}</p>
            </div>
          </div>
        </div>
      ) : activeTab === 'roadmap' && ideaDetails ? (
        <div className="rounded-2xl border border-border bg-white p-6 space-y-6">
          <h3 className="font-display text-xl font-bold text-ink">90-Day Execution Roadmap</h3>
          <div className="space-y-4">
            {ideaDetails.roadmap.map((item, idx) => (
              <div key={idx} className="rounded-xl border border-border/80 bg-slate-50/50 p-4 space-y-1">
                <span className="font-display text-sm font-bold text-accent">{item.phase}</span>
                <p className="text-xs text-ink-muted leading-relaxed">{item.tasks}</p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="rounded-2xl border border-border bg-white p-6 sm:p-8">
          <div className="prose prose-slate max-w-none leading-relaxed">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{article.content}</ReactMarkdown>
          </div>
        </div>
      )}

      {/* Related Ideas Section */}
      {relatedQuery.data && relatedQuery.data.length > 0 ? (
        <section className="space-y-4 pt-6 border-t border-border">
          <h2 className="font-display text-2xl font-bold text-ink">Related Startup Ideas</h2>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {relatedQuery.data.map((item) => (
              <ArticleCard key={item.id} article={item} />
            ))}
          </div>
        </section>
      ) : null}
    </article>
  )
}
