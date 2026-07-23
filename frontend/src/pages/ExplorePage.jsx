import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useArticles } from '@/features/content/hooks'
import { ArticleCard } from '@/features/content/ArticleCard'
import { ArticleCardSkeleton } from '@/shared/ui/Skeleton'
import { EmptyState } from '@/shared/ui/EmptyState'
import { ErrorState } from '@/shared/ui/ErrorState'

// 1. EXACT 10 TOP-LEVEL INDUSTRIES REQUIRED BY USER
const TOP_INDUSTRIES = [
  { slug: '', name: 'All Industries', icon: '🌐', count: 70 },
  { slug: 'artificial-intelligence', name: 'Artificial Intelligence', icon: '🤖', subtopics: ['Legal AI', 'Code Security', 'Synthetic Data', 'Customer Copilot'] },
  { slug: 'manufacturing-industry-4-0', name: 'Manufacturing & Industry 4.0', icon: '🏭', subtopics: ['PCB Assembly', 'Smart Factory', 'Predictive Maintenance', 'Industrial IoT', 'Textile Automation'] },
  { slug: 'healthcare', name: 'Healthcare', icon: '🏥', subtopics: ['Telemedicine', 'Remote Monitoring', 'Medical Devices', 'AI Diagnostics'] },
  { slug: 'agriculture', name: 'Agriculture', icon: '🌾', subtopics: ['Precision Farming', 'Smart Irrigation', 'Cold Storage', 'Soil Health'] },
  { slug: 'fintech', name: 'FinTech', icon: '💳', subtopics: ['Micro Khata', 'Credit Scoring', 'Invoice Discounting', 'Embedded Insurance'] },
  { slug: 'edtech', name: 'EdTech', icon: '🎓', subtopics: ['Adaptive Learning', 'VR Vocational Labs', 'Attendance Telemetry', 'STEM Vernacular'] },
  { slug: 'renewable-energy', name: 'Clean Energy', icon: '⚡', subtopics: ['Solar Microgrids', 'Biomass Briquettes', 'Second-Life Battery', 'Micro-Wind'] },
  { slug: 'construction-tech', name: 'Construction & Infrastructure', icon: '🏗️', subtopics: ['Modular Prefab', 'Drone Site Safety', 'Eco Interlocking Bricks', 'Concrete Sensors'] },
  { slug: 'food-processing', name: 'Food Processing', icon: '🍲', subtopics: ['Fruit Powder', 'Cold-Pressed Oil', 'Retort Packaging', 'Millet Snacks'] },
  { slug: 'robotics', name: 'Robotics & Automation', icon: '🤖', subtopics: ['Spraying Drones', 'Pipe Inspection Crawlers', 'Mobile Robots', 'Robotic Welding'] },
]

const INVESTMENT_RANGES = [
  { value: '', label: 'All Investment Ranges' },
  { value: 'low', label: 'Under ₹10 Lakh' },
  { value: 'medium', label: '₹10 Lakh - ₹25 Lakh' },
  { value: 'high', label: '₹25 Lakh+' },
]

const AI_INVOLVEMENT_OPTIONS = [
  { value: '', label: 'All AI Levels' },
  { value: 'ai-high', label: 'AI Core' },
  { value: 'ai-hybrid', label: 'Hybrid AI' },
  { value: 'ai-non-ai', label: 'Hardware / Ops' },
]

const DIFFICULTY_OPTIONS = [
  { value: '', label: 'All Difficulties' },
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' },
]

const SORT_OPTIONS = [
  { value: 'newest', label: 'Newest first' },
  { value: 'trending', label: 'Most popular' },
  { value: 'title', label: 'Alphabetical' },
]

export default function ExplorePage() {
  const [search, setSearch] = useState('')
  const [query, setQuery] = useState('')
  const [selectedIndustry, setSelectedIndustry] = useState('')
  const [selectedSubtopic, setSelectedSubtopic] = useState('')
  const [selectedInvestment, setSelectedInvestment] = useState('')
  const [selectedAi, setSelectedAi] = useState('')
  const [selectedDifficulty, setSelectedDifficulty] = useState('')
  const [sortBy, setSortBy] = useState('newest')

  const featuredQuery = useArticles({ sort: 'trending', page_size: 1 })
  const articlesQuery = useArticles({
    sort: sortBy,
    page_size: 100,
    search: query || undefined,
    category: selectedIndustry || undefined,
    difficulty: selectedDifficulty || undefined,
  })

  const featured = featuredQuery.data?.items?.[0]
  const allArticles = articlesQuery.data?.items || []

  // Active industry subtopics list
  const activeIndustryData = useMemo(() => {
    return TOP_INDUSTRIES.find((ind) => ind.slug === selectedIndustry)
  }, [selectedIndustry])

  // Multi-facet filtering logic
  const filteredArticles = useMemo(() => {
    return allArticles.filter((article) => {
      const tags = article.tags || []
      const contentStr = (article.title + ' ' + article.summary + ' ' + (article.content || '')).toLowerCase()

      // Sub-topic filter within industry
      if (selectedSubtopic) {
        const subLower = selectedSubtopic.toLowerCase()
        const matchesTitle = article.title.toLowerCase().includes(subLower)
        const matchesSummary = (article.summary || '').toLowerCase().includes(subLower)
        const matchesTags = tags.some((t) => t.toLowerCase().includes(subLower))
        if (!matchesTitle && !matchesSummary && !matchesTags) return false
      }

      // Investment Range Filter
      if (selectedInvestment === 'low') {
        const matchesTag = tags.includes('investment-low') || tags.includes('bootstrap')
        const matchesContent = contentStr.includes('under 10 lakh') || contentStr.includes('bootstrapped') || contentStr.includes('low-cost') || contentStr.includes('₹4 lakh') || contentStr.includes('₹5 lakh') || contentStr.includes('₹6 lakh') || contentStr.includes('₹7 lakh') || contentStr.includes('₹8 lakh') || contentStr.includes('₹9 lakh')
        if (!matchesTag && !matchesContent) return false
      } else if (selectedInvestment === 'medium') {
        const matchesTag = tags.includes('investment-medium') || tags.includes('angels')
        const matchesContent = contentStr.includes('₹10') || contentStr.includes('₹12') || contentStr.includes('₹15') || contentStr.includes('₹18') || contentStr.includes('₹20')
        if (!matchesTag && !matchesContent) return false
      } else if (selectedInvestment === 'high') {
        const matchesTag = tags.includes('investment-high') || tags.includes('vc') || tags.includes('cnc')
        const matchesContent = contentStr.includes('₹25') || contentStr.includes('₹30') || contentStr.includes('₹45') || contentStr.includes('growth')
        if (!matchesTag && !matchesContent) return false
      }

      // AI Involvement Filter
      if (selectedAi === 'ai-high') {
        const matchesTag = tags.includes('ai-high') || tags.includes('chatgpt')
        const matchesContent = contentStr.includes('ai stack') || contentStr.includes('copilot') || contentStr.includes('llm') || contentStr.includes('machine learning')
        if (!matchesTag && !matchesContent) return false
      } else if (selectedAi === 'ai-hybrid') {
        const matchesTag = tags.includes('ai-hybrid') || tags.includes('automation')
        const matchesContent = contentStr.includes('automation') || contentStr.includes('hybrid') || contentStr.includes('sensors')
        if (!matchesTag && !matchesContent) return false
      } else if (selectedAi === 'ai-non-ai') {
        const matchesTag = tags.includes('ai-non-ai') || tags.includes('packaging')
        const matchesContent = contentStr.includes('hardware') || contentStr.includes('physical') || contentStr.includes('fabrication')
        if (!matchesTag && !matchesContent) return false
      }

      return true
    })
  }, [allArticles, selectedSubtopic, selectedInvestment, selectedAi])

  const hasActiveFilters = Boolean(
    query || selectedIndustry || selectedSubtopic || selectedInvestment || selectedAi || selectedDifficulty
  )

  const clearAllFilters = () => {
    setSearch('')
    setQuery('')
    setSelectedIndustry('')
    setSelectedSubtopic('')
    setSelectedInvestment('')
    setSelectedAi('')
    setSelectedDifficulty('')
  }

  const loading = articlesQuery.isLoading || featuredQuery.isLoading
  const error = articlesQuery.isError

  return (
    <div className="grid gap-8 lg:grid-cols-[260px_1fr]">
      {/* ── 1. SIDEBAR: ONLY 10 TOP-LEVEL INDUSTRIES ─────────────────── */}
      <aside className="space-y-6 lg:sticky lg:top-24 lg:self-start">
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <h2 className="text-xs font-bold uppercase tracking-wider text-ink-muted">
              Top Industries
            </h2>
            {selectedIndustry ? (
              <button
                type="button"
                onClick={() => { setSelectedIndustry(''); setSelectedSubtopic(''); }}
                className="text-xs text-accent font-semibold hover:underline"
              >
                Clear
              </button>
            ) : null}
          </div>

          <nav className="flex gap-1.5 overflow-x-auto pb-2 lg:flex-col lg:overflow-visible lg:pb-0">
            {TOP_INDUSTRIES.map((ind) => {
              const active = selectedIndustry === ind.slug
              return (
                <button
                  key={ind.slug || 'all'}
                  type="button"
                  onClick={() => {
                    setSelectedIndustry(ind.slug)
                    setSelectedSubtopic('')
                  }}
                  className={[
                    'whitespace-nowrap rounded-xl px-3.5 py-2.5 text-left text-xs font-semibold transition flex items-center justify-between gap-2 border',
                    active
                      ? 'bg-accent text-white border-accent shadow-xs'
                      : 'bg-white text-ink-muted hover:bg-slate-50 hover:text-ink border-border/60',
                  ].join(' ')}
                >
                  <div className="flex items-center gap-2 truncate">
                    <span>{ind.icon}</span>
                    <span className="truncate">{ind.name}</span>
                  </div>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Refine Filters Box */}
        <div className="rounded-2xl border border-border bg-white p-4 space-y-3.5 shadow-xs">
          <h3 className="text-xs font-bold uppercase tracking-wider text-ink-muted">
            Refine Filter
          </h3>

          <div className="space-y-1">
            <label className="block text-[11px] font-semibold text-ink">Investment Budget</label>
            <select
              value={selectedInvestment}
              onChange={(e) => setSelectedInvestment(e.target.value)}
              className="w-full rounded-xl border border-border bg-slate-50 px-3 py-2 text-xs outline-none focus:border-accent"
            >
              {INVESTMENT_RANGES.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label className="block text-[11px] font-semibold text-ink">AI Level</label>
            <select
              value={selectedAi}
              onChange={(e) => setSelectedAi(e.target.value)}
              className="w-full rounded-xl border border-border bg-slate-50 px-3 py-2 text-xs outline-none focus:border-accent"
            >
              {AI_INVOLVEMENT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label className="block text-[11px] font-semibold text-ink">Difficulty</label>
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="w-full rounded-xl border border-border bg-slate-50 px-3 py-2 text-xs outline-none focus:border-accent"
            >
              {DIFFICULTY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {hasActiveFilters ? (
            <button
              type="button"
              onClick={clearAllFilters}
              className="w-full rounded-xl border border-rose-200 bg-rose-50 py-2 text-xs font-semibold text-rose-700 hover:bg-rose-100 transition"
            >
              Clear All Filters
            </button>
          ) : null}
        </div>
      </aside>

      {/* ── 2. MAIN CONTENT AREA ─────────────────────────────────────── */}
      <div className="space-y-6">
        <header className="space-y-4">
          <div>
            <h1 className="font-display text-3xl font-bold text-ink sm:text-4xl">
              Startup & Manufacturing Ideas
            </h1>
            <p className="mt-1 text-sm text-ink-muted max-w-2xl">
              Browse structured startup playbooks, unit economics, technology stacks, and roadmaps across 10 top industries.
            </p>
          </div>

          {/* Search bar & Sort Controls */}
          <div className="flex flex-col gap-2.5 sm:flex-row sm:items-center">
            <form
              className="flex flex-1 gap-2"
              onSubmit={(e) => {
                e.preventDefault()
                setQuery(search.trim())
              }}
            >
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search ideas by keywords (e.g. PCB, telemetry, diagnostic, drone, IoT)..."
                className="w-full flex-1 rounded-xl border border-border bg-white px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-accent/30"
              />
              <button
                type="submit"
                className="rounded-xl bg-accent px-5 py-2.5 text-sm font-semibold text-white hover:bg-accent-hover transition shadow-xs"
              >
                Search
              </button>
            </form>

            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-ink-muted whitespace-nowrap">Sort:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="rounded-xl border border-border bg-white px-3 py-2.5 text-xs font-medium outline-none focus:border-accent"
              >
                {SORT_OPTIONS.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Sub-Topic Idea Pills under selected industry */}
          {activeIndustryData?.subtopics?.length ? (
            <div className="rounded-2xl border border-accent/20 bg-accent-soft/50 p-3 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-accent">
                  Browse {activeIndustryData.name} Ideas:
                </span>
                {selectedSubtopic ? (
                  <button
                    type="button"
                    onClick={() => setSelectedSubtopic('')}
                    className="text-xs text-accent underline font-semibold"
                  >
                    Clear Subtopic
                  </button>
                ) : null}
              </div>
              <div className="flex flex-wrap gap-1.5">
                {activeIndustryData.subtopics.map((sub) => {
                  const active = selectedSubtopic === sub
                  return (
                    <button
                      key={sub}
                      type="button"
                      onClick={() => setSelectedSubtopic(active ? '' : sub)}
                      className={[
                        'rounded-lg px-2.5 py-1 text-xs font-semibold transition',
                        active
                          ? 'bg-accent text-white shadow-xs'
                          : 'bg-white text-slate-700 hover:bg-accent hover:text-white border border-border/60',
                      ].join(' ')}
                    >
                      • {sub}
                    </button>
                  )
                })}
              </div>
            </div>
          ) : null}

          {/* Active Filter Badges */}
          {hasActiveFilters ? (
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="font-semibold text-ink-muted">Filters:</span>
              {query ? (
                <span className="inline-flex items-center gap-1 rounded-lg bg-accent-soft px-2.5 py-1 text-accent font-semibold">
                  “{query}”
                  <button type="button" onClick={() => { setSearch(''); setQuery(''); }} className="hover:text-ink">×</button>
                </span>
              ) : null}
              {selectedIndustry ? (
                <span className="inline-flex items-center gap-1 rounded-lg bg-slate-100 px-2.5 py-1 text-slate-700 font-semibold">
                  Industry: {activeIndustryData?.name || selectedIndustry}
                  <button type="button" onClick={() => { setSelectedIndustry(''); setSelectedSubtopic(''); }} className="hover:text-ink">×</button>
                </span>
              ) : null}
              {selectedSubtopic ? (
                <span className="inline-flex items-center gap-1 rounded-lg bg-emerald-100 px-2.5 py-1 text-emerald-800 font-semibold">
                  Subtopic: {selectedSubtopic}
                  <button type="button" onClick={() => setSelectedSubtopic('')} className="hover:text-ink">×</button>
                </span>
              ) : null}
              {selectedInvestment ? (
                <span className="inline-flex items-center gap-1 rounded-lg bg-emerald-50 px-2.5 py-1 text-emerald-700 font-semibold">
                  Budget: {INVESTMENT_RANGES.find((i) => i.value === selectedInvestment)?.label}
                  <button type="button" onClick={() => setSelectedInvestment('')} className="hover:text-ink">×</button>
                </span>
              ) : null}
              <button
                type="button"
                onClick={clearAllFilters}
                className="text-xs text-rose-600 hover:underline font-semibold ml-1"
              >
                Clear all
              </button>
            </div>
          ) : null}
        </header>

        {error ? (
          <ErrorState
            title="Could not load ideas"
            message="Please ensure backend server is running."
            onRetry={() => articlesQuery.refetch()}
          />
        ) : null}

        {/* Featured Idea Spotlight (when no query is active) */}
        {!error && featured && !hasActiveFilters ? (
          <motion.section
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="overflow-hidden rounded-3xl border border-border bg-white shadow-xs"
          >
            <div className="grid md:grid-cols-2">
              <div className="aspect-[16/10] bg-accent-soft md:aspect-auto">
                {featured.thumbnail ? (
                  <img src={featured.thumbnail} alt="" className="h-full w-full object-cover" />
                ) : null}
              </div>
              <div className="flex flex-col justify-center gap-3.5 p-6">
                <span className="text-xs font-bold uppercase tracking-wider text-accent">
                  Featured Idea Spotlight
                </span>
                <h2 className="font-display text-2xl font-bold text-ink">{featured.title}</h2>
                <p className="text-ink-muted text-xs leading-relaxed line-clamp-3">{featured.summary}</p>
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <span className="rounded-md bg-emerald-100 px-2 py-0.5 font-semibold text-emerald-800">
                    {featured.category?.name}
                  </span>
                  <span className="capitalize font-medium text-slate-600">· {featured.difficulty}</span>
                </div>
                <Link
                  to={`/articles/${featured.slug}`}
                  className="inline-flex w-fit rounded-xl bg-accent px-4 py-2 text-xs font-semibold text-white hover:bg-accent-hover transition shadow-xs"
                >
                  Read Blueprint →
                </Link>
              </div>
            </div>
          </motion.section>
        ) : null}

        {/* ── IDEAS GRID ────────────────────────────────────────────────── */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-xl font-bold text-ink">
              {selectedIndustry
                ? `${activeIndustryData?.name || 'Industry'} Ideas`
                : 'Startup & Manufacturing Ideas'}
            </h2>
            <span className="text-xs font-semibold text-ink-muted">
              {filteredArticles.length} Startup Ideas
            </span>
          </div>

          {loading ? (
            <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <ArticleCardSkeleton key={i} />
              ))}
            </div>
          ) : filteredArticles.length > 0 ? (
            <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
              {filteredArticles.map((article) => (
                <ArticleCard key={article.id} article={article} />
              ))}
            </div>
          ) : (
            <EmptyState
              title="No ideas match your filters"
              message="Try selecting another industry or clearing subtopic filters."
            />
          )}
        </section>
      </div>
    </div>
  )
}
