import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useArticles, useCategories } from '@/features/content/hooks'
import { ArticleCard } from '@/features/content/ArticleCard'
import { ArticleCardSkeleton } from '@/shared/ui/Skeleton'

const PROMPT_SUGGESTIONS = [
  'How do I build a PCB electronics hardware MVP?',
  'What are the GST rules and thresholds for D2C manufacturing?',
  'Compare Private Limited vs LLP for a hardware startup',
  'How to structure a seed pitch deck for angel investors?',
]

export default function HomePage() {
  const [heroSearch, setHeroSearch] = useState('')
  const navigate = useNavigate()

  const categoriesQuery = useCategories({ page_size: 10 })
  const trendingQuery = useArticles({ sort: 'trending', page_size: 6 })
  const newestQuery = useArticles({ sort: 'newest', page_size: 4 })

  const categories = categoriesQuery.data?.items || []
  const trendingIdeas = trendingQuery.data?.items || []
  const newestIdeas = newestQuery.data?.items || []

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    if (heroSearch.trim()) {
      navigate(`/explore?search=${encodeURIComponent(heroSearch.trim())}`)
    } else {
      navigate('/explore')
    }
  }

  return (
    <div className="space-y-16 pb-12">
      {/* ── 1. HERO SECTION ───────────────────────────────────────────── */}
      <section className="relative overflow-hidden rounded-3xl border border-border/80 bg-gradient-to-b from-white via-surface to-accent-soft/30 px-6 py-16 sm:px-12 sm:py-24 shadow-sm">
        {/* Soft Background Radial Lighting */}
        <div
          className="pointer-events-none absolute inset-0 opacity-70"
          style={{
            background:
              'radial-gradient(circle 600px at 75% 20%, rgba(26,107,74,0.12), transparent 70%), radial-gradient(circle 500px at 20% 80%, rgba(3,105,161,0.08), transparent 60%)',
          }}
          aria-hidden
        />

        <div className="relative mx-auto max-w-4xl space-y-8 text-center">
          {/* Badge Preamble */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="inline-flex items-center gap-2 rounded-full border border-accent/20 bg-accent-soft/80 px-4 py-1.5 text-xs font-semibold text-accent shadow-xs"
          >
            <span className="flex h-2 w-2 rounded-full bg-accent animate-pulse" />
            <span>AI-Powered Startup & Manufacturing Discovery Platform</span>
          </motion.div>

          {/* Main Hero Headline */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="space-y-4"
          >
            <h1 className="font-display text-4xl font-extrabold tracking-tight text-ink sm:text-6xl sm:leading-tight">
              Turn Concepts Into <span className="text-accent underline decoration-accent/30 underline-offset-8">Executable Ventures</span>
            </h1>
            <p className="mx-auto max-w-2xl text-base text-ink-muted sm:text-lg leading-relaxed">
              Explore 44+ structured startup ideas, hardware manufacturing playbooks, unit economics models, and get instant answers from our grounded RAG AI Copilot.
            </p>
          </motion.div>

          {/* Hero Search Bar */}
          <motion.form
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            onSubmit={handleSearchSubmit}
            className="mx-auto flex max-w-2xl flex-col gap-2.5 sm:flex-row sm:items-center rounded-2xl border border-border bg-white p-2 shadow-md focus-within:ring-2 focus-within:ring-accent/30"
          >
            <div className="flex flex-1 items-center gap-2 px-3">
              <span className="text-ink-muted text-sm">🔍</span>
              <input
                value={heroSearch}
                onChange={(e) => setHeroSearch(e.target.value)}
                placeholder="Search ideas (e.g. PCB prototyping, CNC machining, SaaS, GST)..."
                className="w-full bg-transparent text-sm font-medium text-ink outline-none placeholder:text-ink-muted/60"
              />
            </div>
            <button
              type="submit"
              className="rounded-xl bg-accent px-6 py-3 text-sm font-semibold text-white transition hover:bg-accent-hover shadow-xs flex-shrink-0"
            >
              Explore Ideas
            </button>
          </motion.form>

          {/* Hero Quick Tags / CTAs */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-wrap items-center justify-center gap-3 pt-2 text-xs"
          >
            <span className="font-semibold text-ink-muted">Popular Industries:</span>
            {categories.slice(0, 5).map((cat) => (
              <Link
                key={cat.slug}
                to={`/explore?category=${cat.slug}`}
                className="rounded-lg border border-border/80 bg-white/80 px-3 py-1.5 font-medium text-ink-muted hover:border-accent hover:text-accent transition shadow-xs"
              >
                {cat.name}
              </Link>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── 2. PLATFORM METRICS ───────────────────────────────────────── */}
      <section className="grid gap-4 grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl border border-border bg-white p-6 space-y-1 text-center shadow-xs">
          <p className="font-display text-3xl font-extrabold text-accent">100+</p>
          <p className="text-xs font-semibold text-ink">Startup Ideas</p>
          <p className="text-[11px] text-ink-muted">Validated business models</p>
        </div>
        <div className="rounded-2xl border border-border bg-white p-6 space-y-1 text-center shadow-xs">
          <p className="font-display text-3xl font-extrabold text-emerald-700">10</p>
          <p className="text-xs font-semibold text-ink">Industries</p>
          <p className="text-[11px] text-ink-muted">AI, Manufacturing, Healthcare</p>
        </div>
        <div className="rounded-2xl border border-border bg-white p-6 space-y-1 text-center shadow-xs">
          <p className="font-display text-3xl font-extrabold text-sky-700">AI-Powered</p>
          <p className="text-xs font-semibold text-ink">Discovery</p>
          <p className="text-[11px] text-ink-muted">RAG knowledge advisor</p>
        </div>
        <div className="rounded-2xl border border-border bg-white p-6 space-y-1 text-center shadow-xs">
          <p className="font-display text-3xl font-extrabold text-amber-700">90-Day</p>
          <p className="text-xs font-semibold text-ink">Execution Roadmaps</p>
          <p className="text-[11px] text-ink-muted">Step-by-step launch plans</p>
        </div>
      </section>

      {/* ── 3. TRENDING STARTUP & MANUFACTURING IDEAS ───────────────────── */}
      <section className="space-y-6">
        <div className="flex flex-wrap items-end justify-between gap-4 border-b border-border/60 pb-4">
          <div>
            <h2 className="font-display text-2xl font-bold text-ink sm:text-3xl">
              🔥 Trending Startup & Manufacturing Ideas
            </h2>
            <p className="mt-1 text-sm text-ink-muted">
              Top curated ideas with validated problem statements, capital requirements, and execution roadmaps.
            </p>
          </div>
          <Link
            to="/explore"
            className="text-sm font-semibold text-accent hover:underline flex items-center gap-1"
          >
            View all 44+ ideas →
          </Link>
        </div>

        {trendingQuery.isLoading ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <ArticleCardSkeleton key={i} />
            ))}
          </div>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {trendingIdeas.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        )}
      </section>

      {/* ── 4. INDUSTRY CATEGORY EXPLORER ─────────────────────────────── */}
      <section className="space-y-6">
        <div className="border-b border-border/60 pb-4">
          <h2 className="font-display text-2xl font-bold text-ink sm:text-3xl">
            🏭 Explore Industries & Sectors
          </h2>
          <p className="mt-1 text-sm text-ink-muted">
            From electronics hardware fabrication to B2B SaaS and compliance playbooks.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {categories.map((cat) => (
            <Link
              key={cat.id}
              to={`/explore?category=${cat.slug}`}
              className="group rounded-2xl border border-border bg-white p-5 shadow-xs transition hover:-translate-y-1 hover:shadow-md hover:border-accent"
            >
              <div className="flex items-center justify-between">
                <span
                  className="h-3 w-3 rounded-full"
                  style={{ backgroundColor: cat.color || '#1a6b4a' }}
                />
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-700">
                  {cat.idea_count || 0} ideas
                </span>
              </div>
              <h3 className="font-display text-lg font-bold text-ink mt-3 transition group-hover:text-accent">
                {cat.name}
              </h3>
              <p className="text-xs text-ink-muted line-clamp-2 mt-1 leading-relaxed">
                {cat.description || 'Structured startup playbooks and execution guides.'}
              </p>
            </Link>
          ))}
        </div>
      </section>

      {/* ── 5. AI ASSISTANT PROMPT SPOTLIGHT ───────────────────────────── */}
      <section className="rounded-3xl border border-accent/20 bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-950 p-8 text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10 space-y-6 max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-emerald-300">
            <span>✨ Powered by RAG Pipeline</span>
          </div>

          <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl text-white">
            Ask Startup Navigator AI Anything
          </h2>

          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Our intelligent assistant queries our internal knowledge base first to provide grounded, source-cited answers on business validation, hardware prototyping, GST, and fundraising.
          </p>

          {/* Prompt Suggestion Chips */}
          <div className="space-y-2">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Try asking:</p>
            <div className="flex flex-wrap gap-2">
              {PROMPT_SUGGESTIONS.map((prompt, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => navigate(`/search?q=${encodeURIComponent(prompt)}`)}
                  className="rounded-xl bg-white/10 px-3.5 py-2 text-xs font-medium text-slate-200 transition hover:bg-emerald-500 hover:text-white text-left"
                >
                  💬 "{prompt}"
                </button>
              ))}
            </div>
          </div>

          <div className="pt-2">
            <Link
              to="/search"
              className="inline-flex items-center gap-2 rounded-xl bg-accent px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-accent-hover"
            >
              <span>Launch AI Search Assistant →</span>
            </Link>
          </div>
        </div>
      </section>

      {/* ── 6. NEWEST ADDITIONS ───────────────────────────────────────── */}
      {newestIdeas.length > 0 ? (
        <section className="space-y-6">
          <div className="flex items-center justify-between border-b border-border/60 pb-4">
            <h2 className="font-display text-2xl font-bold text-ink">✨ Newly Published Ideas</h2>
            <Link to="/explore" className="text-sm font-semibold text-accent hover:underline">
              View all
            </Link>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {newestIdeas.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        </section>
      ) : null}
    </div>
  )
}
