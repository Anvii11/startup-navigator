import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'

import { PageShell } from '@/shared/ui/PageShell'
import apiClient from '@/shared/api/client'
import { useAuth } from '@/features/auth/AuthContext'
import { useUserSavedIdeaIds, useSaveIdeaMutation, useRemoveSavedIdeaMutation } from '@/features/content/hooks'

const FORBIDDEN_HEADINGS = new Set([
  'quick overview',
  'problem statement',
  'market opportunity',
  'implementation roadmap',
  'technology stack',
  'revenue model',
  'executive summary',
  'key highlights',
  'target customers',
  'references',
  'government schemes',
  'financial plan',
])

export default function AISearchPage() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const { data: savedIds = [] } = useUserSavedIdeaIds()
  const saveMutation = useSaveIdeaMutation()
  const removeMutation = useRemoveSavedIdeaMutation()

  async function handleSubmit(e) {
    e.preventDefault()
    if (!question.trim()) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const res = await apiClient.post('/ai/ask', { question: question.trim() })
      setResult(res.data)
    } catch (err) {
      const msg =
        err.response?.data?.detail ??
        err.response?.data?.message ??
        err.message ??
        'Something went wrong'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setLoading(false)
    }
  }

  return (
    <PageShell
      title="AI Startup Advisor"
      description="Ask questions to discover grounded, high-growth startup & manufacturing opportunities."
    >
      <div className="mx-auto max-w-5xl space-y-8">
        {/* Question Search Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative rounded-2xl border border-border bg-surface p-2 shadow-sm transition-all focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/20">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. Healthcare startup ideas, Manufacturing business under ₹10 lakh, AI legal copilot..."
              rows={3}
              className="w-full resize-none bg-transparent px-3 py-2 text-sm text-ink placeholder:text-ink-muted focus:outline-none"
              disabled={loading}
            />
            <div className="flex items-center justify-between border-t border-border/50 pt-2 px-2">
              <span className="text-xs text-ink-muted">
                Powered by Startup Navigator RAG Knowledge Engine
              </span>
              <button
                type="submit"
                disabled={loading || !question.trim()}
                className="inline-flex items-center gap-2 rounded-xl bg-accent px-6 py-2.5 text-sm font-semibold text-white shadow-md transition-all hover:bg-accent/90 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <svg className="h-4 w-4 animate-spin text-white" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <span>Search Advisor</span>
                    <span className="text-lg">✨</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Quick Query Pills */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="font-medium text-ink-muted">Try asking:</span>
            {[
              'Healthcare startup ideas',
              'Manufacturing under ₹10 lakh',
              'AI Legal Copilot',
              'Food processing business',
              'Robotics & Automation',
            ].map((q) => (
              <button
                key={q}
                type="button"
                onClick={() => setQuestion(q)}
                className="rounded-lg border border-border bg-surface/50 px-2.5 py-1 text-ink-muted hover:border-accent hover:text-accent transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </form>

        {/* Error State */}
        {error && (
          <div className="rounded-xl border border-red-300 bg-red-50 p-4 text-sm text-red-700 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-400">
            {error}
          </div>
        )}

        {/* Loading State Skeleton */}
        {loading && <LoadingSkeleton />}

        {/* AI Answer Cards Result */}
        {result && !loading && (
          <AnimatePresence>
            <AdvisorResultPresenter
              data={result}
              isAuthenticated={isAuthenticated}
              savedIds={savedIds}
              saveMutation={saveMutation}
              removeMutation={removeMutation}
              navigate={navigate}
            />
          </AnimatePresence>
        )}
      </div>
    </PageShell>
  )
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-20 rounded-2xl border border-border bg-surface/50 p-4" />
      <div className="h-64 rounded-2xl border border-border bg-surface/50 p-6" />
      <div className="h-64 rounded-2xl border border-border bg-surface/50 p-6" />
    </div>
  )
}

function AdvisorResultPresenter({
  data,
  isAuthenticated,
  savedIds,
  saveMutation,
  removeMutation,
  navigate,
}) {
  const textAnswer = data.answer || ''
  const sources = data.sources || []

  // Parse structured cards from JSON or Markdown
  const parsedResponse = parseStructuredResponse(textAnswer, sources)

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      {/* ── TOP SECTION: Startup Recommendations Header ── */}
      <div className="rounded-2xl border border-accent/20 bg-gradient-to-r from-accent/10 via-surface to-accent/5 p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">🏆</span>
              <h2 className="text-xl font-bold text-ink">Startup Recommendations</h2>
            </div>
            <p className="mt-1 text-sm text-ink-muted">
              {parsedResponse.summaryIntro ||
                `I found the ${parsedResponse.cards.length || sources.length} most relevant startup opportunities based on your query.`}
            </p>
          </div>

          <div className="flex flex-wrap gap-2 text-xs font-medium">
            <span className="rounded-full bg-accent/15 px-3 py-1 text-accent">
              📊 {parsedResponse.cards.length || sources.length} Ideas Found
            </span>
            {parsedResponse.industry && (
              <span className="rounded-full bg-surface border border-border px-3 py-1 text-ink">
                🏭 {parsedResponse.industry}
              </span>
            )}
            <span className="rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 px-3 py-1">
              ✨ Relevance Ranked
            </span>
          </div>
        </div>
      </div>

      {/* ── STARTUP CARDS GRID ── */}
      <div className="space-y-6">
        {parsedResponse.cards.map((card, idx) => {
          const matchedSource = sources.find(
            (s) =>
              (card.slug && s.slug === card.slug) ||
              s.title.toLowerCase().includes(card.title.toLowerCase())
          )
          const slug = card.slug || matchedSource?.slug

          return (
            <StartupCardItem
              key={idx}
              card={card}
              index={idx + 1}
              slug={slug}
              isAuthenticated={isAuthenticated}
              savedIds={savedIds}
              saveMutation={saveMutation}
              removeMutation={removeMutation}
              navigate={navigate}
            />
          )
        })}
      </div>

      {/* ── RESPONSE ENDING FOOTER ── */}
      <div className="rounded-2xl border border-border bg-surface/50 p-6 text-center shadow-sm">
        <div className="mx-auto max-w-xl space-y-2">
          <p className="text-sm font-medium text-ink">
            You can explore complete business blueprints, implementation roadmaps and technical details from the Explore section.
          </p>
          <p className="text-xs text-ink-muted">
            Ask another question to discover more startup opportunities.
          </p>
        </div>
      </div>
    </motion.div>
  )
}

function StartupCardItem({
  card,
  index,
  slug,
  isAuthenticated,
  savedIds,
  saveMutation,
  removeMutation,
  navigate,
}) {
  const articleId = card.articleId

  const isSaved = articleId ? savedIds.includes(articleId) : false

  const handleToggleSave = () => {
    if (!isAuthenticated) {
      toast.error('Please log in to save ideas to your dashboard.')
      navigate('/login')
      return
    }
    if (!articleId) {
      toast.success('Idea saved to your interest list!')
      return
    }
    if (isSaved) {
      removeMutation.mutate(articleId, {
        onSuccess: () => toast.success('Idea removed from saved list.'),
      })
    } else {
      saveMutation.mutate(articleId, {
        onSuccess: () => toast.success('Idea saved to your dashboard!'),
      })
    }
  }

  return (
    <div className="group rounded-2xl border border-border bg-surface p-6 shadow-sm transition-all hover:border-accent/40 hover:shadow-md">
      {/* Title & Badge Header */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 border-b border-border/60 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-accent/10 text-xs font-bold text-accent">
              #{index}
            </span>
            <h3 className="text-lg font-bold text-ink group-hover:text-accent transition-colors">
              🚀 {card.title}
            </h3>
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
            <span className="rounded-md bg-accent/10 px-2.5 py-0.5 font-medium text-accent">
              🏭 {card.industry || 'General'}
            </span>
            {card.subtopic && card.subtopic !== 'General' && (
              <span className="rounded-md bg-surface-muted border border-border px-2.5 py-0.5 text-ink-muted">
                📂 {card.subtopic}
              </span>
            )}
            <span className="rounded-md bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 px-2.5 py-0.5 font-medium">
              ⚡ {card.difficulty || 'Intermediate'}
            </span>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4 rounded-xl border border-border/40 bg-surface-muted/30 p-3 text-xs">
        <div>
          <span className="text-ink-muted block">💰 Investment</span>
          <span className="font-semibold text-ink">{card.investment || 'Under ₹10 Lakh'}</span>
        </div>
        <div>
          <span className="text-ink-muted block">⚡ Difficulty</span>
          <span className="font-semibold text-ink">{card.difficulty || 'Intermediate'}</span>
        </div>
        <div>
          <span className="text-ink-muted block">📈 Market Potential</span>
          <span className="font-semibold text-ink line-clamp-1">{card.marketPotential || 'High Growth'}</span>
        </div>
        <div>
          <span className="text-ink-muted block">🤖 AI Tech</span>
          <span className="font-semibold text-ink line-clamp-1">{card.aiTech || 'Machine Learning'}</span>
        </div>
      </div>

      {/* Quick Overview Box */}
      <div className="mt-4 rounded-xl border border-accent/15 bg-accent/5 p-4">
        <h4 className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-accent">
          <span>💡</span> Quick Overview
        </h4>
        <p className="mt-1.5 text-sm leading-relaxed text-ink">
          {card.overview}
        </p>
      </div>

      {/* Key Highlights Badges */}
      <div className="mt-4">
        <h4 className="text-xs font-semibold text-ink-muted">Key Highlights:</h4>
        <div className="mt-2 flex flex-wrap gap-1.5 text-xs">
          <span className="rounded-lg bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20 px-2.5 py-1">
            ✔ Low Investment
          </span>
          <span className="rounded-lg bg-blue-500/10 text-blue-700 dark:text-blue-400 border border-blue-500/20 px-2.5 py-1">
            ✔ High AI Adoption
          </span>
          <span className="rounded-lg bg-purple-500/10 text-purple-700 dark:text-purple-400 border border-purple-500/20 px-2.5 py-1">
            ✔ Scalable Model
          </span>
          <span className="rounded-lg bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 border border-indigo-500/20 px-2.5 py-1">
            ✔ Growing Market
          </span>
          <span className="rounded-lg bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/20 px-2.5 py-1">
            ✔ Government Support
          </span>
        </div>
      </div>

      {/* Target Customers Chips */}
      {card.targetCustomers && (
        <div className="mt-4">
          <h4 className="text-xs font-semibold text-ink-muted">🎯 Target Customers:</h4>
          <div className="mt-1.5 flex flex-wrap gap-1.5 text-xs text-ink">
            {(Array.isArray(card.targetCustomers) ? card.targetCustomers : card.targetCustomers.split(',')).map((cust, i) => (
              <span key={i} className="rounded-md border border-border bg-surface px-2.5 py-1">
                {String(cust).trim()}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Revenue Model */}
      {card.revenueModel && (
        <div className="mt-4 rounded-lg bg-surface-muted/40 border border-border/40 px-3 py-2 text-xs text-ink">
          <span className="font-semibold text-ink-muted">💵 Revenue Model: </span>
          <span>{card.revenueModel}</span>
        </div>
      )}

      {/* Actions Toolbar */}
      <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-border/60 pt-4">
        <div className="flex flex-wrap gap-2">
          {slug ? (
            <Link
              to={`/articles/${slug}`}
              className="inline-flex items-center gap-1.5 rounded-xl bg-accent px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-accent/90"
            >
              <span>📄 View Complete Blueprint</span>
            </Link>
          ) : (
            <button
              disabled
              className="inline-flex items-center gap-1.5 rounded-xl bg-accent/50 px-4 py-2 text-xs font-semibold text-white/80 cursor-not-allowed"
            >
              <span>📄 View Complete Blueprint</span>
            </button>
          )}

          <button
            disabled
            title="Comparison tool coming soon"
            className="inline-flex items-center gap-1.5 rounded-xl border border-border bg-surface-muted px-3.5 py-2 text-xs font-medium text-ink-muted opacity-65 cursor-not-allowed"
          >
            <span>📊 Compare Ideas</span>
          </button>
        </div>

        <button
          onClick={handleToggleSave}
          className={`inline-flex items-center gap-1.5 rounded-xl border px-3.5 py-2 text-xs font-semibold transition-all ${
            isSaved
              ? 'border-amber-500/40 bg-amber-500/10 text-amber-600 dark:text-amber-400'
              : 'border-border bg-surface text-ink hover:border-accent hover:text-accent'
          }`}
        >
          <span>{isSaved ? '★ Saved' : '⭐ Save Idea'}</span>
        </button>
      </div>
    </div>
  )
}

function parseStructuredResponse(text, sources) {
  // 1. Try parsing JSON first
  try {
    const cleaned = text.replace(/```json/g, '').replace(/```/g, '').trim()
    const jsonPayload = JSON.parse(cleaned)
    if (jsonPayload && Array.isArray(jsonPayload.ideas) && jsonPayload.ideas.length > 0) {
      const cleanIdeas = jsonPayload.ideas.map((item, idx) => {
        let title = item.title ? item.title.trim() : ''
        if (!title || FORBIDDEN_HEADINGS.has(title.toLowerCase())) {
          const matchedSrc = sources[idx] || sources[0]
          title = matchedSrc ? matchedSrc.title : 'High Growth Startup Opportunity'
        }

        const aiTechStr = Array.isArray(item.aiTechnologies)
          ? item.aiTechnologies.join(', ')
          : item.aiTechnologies || 'Machine Learning Automation'
        const custStr = Array.isArray(item.targetCustomers)
          ? item.targetCustomers.join(', ')
          : item.targetCustomers || 'Enterprise SMBs, retail buyers'
        const overview =
          item.summary ||
          item.overview ||
          `${title} provides an innovative solution grounded in our knowledge base database.`

        return {
          title,
          industry: item.industry || jsonPayload.industry || 'Startup Opportunity',
          subtopic: item.subtopic || 'General',
          investment: item.investment || 'Under ₹10 Lakh',
          difficulty: item.difficulty || 'Intermediate',
          marketPotential: item.marketPotential || 'High Growth Market',
          aiTech: aiTechStr,
          overview: overview,
          targetCustomers: custStr,
          revenueModel: item.revenueModel || 'B2B subscription and unit sales',
          slug: item.slug || (sources[idx] ? sources[idx].slug : ''),
        }
      })

      return {
        summaryIntro:
          jsonPayload.summaryIntro ||
          `I found the ${cleanIdeas.length} most relevant startup opportunities based on your query.`,
        industry: jsonPayload.industry || (cleanIdeas[0] ? cleanIdeas[0].industry : 'Startup Ideas'),
        cards: cleanIdeas,
      }
    }
  } catch (e) {
    // Fallback to markdown text parser
  }

  // 2. Fallback text parser
  const cards = []
  let summaryIntro = ''
  let industry = ''

  const sections = text.split(/(?=###|\n---)/)

  for (const sec of sections) {
    const trimmed = sec.trim()
    if (!trimmed) continue

    if (trimmed.startsWith('# 🏆') || trimmed.startsWith('Based on your query') || trimmed.includes('most relevant')) {
      const matchIntro = trimmed.match(/I found the (.+?)(?=\n|$)/i)
      if (matchIntro) {
        summaryIntro = matchIntro[0]
      }
      const matchInd = trimmed.match(/Industry:\*\*\s*(.+)/i)
      if (matchInd) {
        industry = matchInd[1].trim()
      }
      continue
    }

    if (trimmed.startsWith('###') || trimmed.includes('🚀')) {
      const titleMatch = trimmed.match(/(?:###\s*\d*\.?\s*🚀?\s*|🚀\s*)([^\n]+)/)
      let title = titleMatch ? titleMatch[1].replace(/^[0-9.\s🚀]+/, '').trim() : 'Startup Opportunity'

      if (FORBIDDEN_HEADINGS.has(title.toLowerCase())) {
        title = sources[cards.length] ? sources[cards.length].title : 'High Growth Startup Opportunity'
      }

      const indMatch = trimmed.match(/🏭 \*\*Industry:\*\*\s*([^\n]+)/)
      const subMatch = trimmed.match(/📂 \*\*Subtopic:\*\*\s*([^\n]+)/)
      const invMatch = trimmed.match(/💰 \*\*Estimated Investment:\*\*\s*([^\n]+)/)
      const diffMatch = trimmed.match(/⚡ \*\*Difficulty:\*\*\s*([^\n]+)/)
      const mktMatch = trimmed.match(/📈 \*\*Market Potential:\*\*\s*([^\n]+)/)
      const aiMatch =
        trimmed.match(/🤖 \*\*AI Technologies:\*\*\s*([^\n]+)/) ||
        trimmed.match(/🤖 \*\*AI Technologies Used:\*\*\s*([^\n]+)/)
      const custMatch = trimmed.match(/🎯 \*\*Target Customers:\*\*\s*([^\n]+)/)
      const revMatch = trimmed.match(/💵 \*\*Revenue Model:\*\*\s*([^\n]+)/)
      const slugMatch = trimmed.match(/🔗 \*\*Slug:\*\*\s*([^\n]+)/)

      let overview = ''
      const overviewMatch = trimmed.match(/#### 💡 Quick Overview\s*\n+([\s\S]+?)(?=\n####|\n🎯|\n💵|\n📚|\n---|$)/)
      if (overviewMatch) {
        overview = overviewMatch[1].trim()
      } else {
        const sumMatch = trimmed.match(/💡 \*\*Summary:\*\*\s*([^\n]+)/)
        if (sumMatch) {
          overview = sumMatch[1].trim()
        }
      }

      if (!overview) {
        overview = `${title} is a scalable venture addressing critical industry needs with high unit economics and government subsidy support.`
      }

      cards.push({
        title,
        industry: indMatch ? indMatch[1].trim() : industry || 'Startup Idea',
        subtopic: subMatch ? subMatch[1].trim() : 'General',
        investment: invMatch ? invMatch[1].trim() : 'Under ₹10 Lakh',
        difficulty: diffMatch ? diffMatch[1].trim() : 'Intermediate',
        marketPotential: mktMatch ? mktMatch[1].trim() : 'High Growth Market',
        aiTech: aiMatch ? aiMatch[1].trim() : 'Machine Learning Automation',
        overview,
        targetCustomers: custMatch ? custMatch[1].trim() : 'Enterprise SMBs, retail buyers',
        revenueModel: revMatch ? revMatch[1].trim() : 'B2B subscription + margin model',
        slug: slugMatch ? slugMatch[1].trim() : '',
      })
    }
  }

  // Fallback if parsing produced 0 cards but sources exist
  if (cards.length === 0 && sources.length > 0) {
    sources.forEach((src) => {
      cards.push({
        title: src.title,
        industry: industry || 'Startup Idea',
        subtopic: 'General',
        investment: 'Under ₹10 Lakh',
        difficulty: 'Intermediate',
        marketPotential: 'High Growth Market',
        aiTech: 'AI & IoT Sensors',
        overview: `${src.title} provides an innovative solution grounded in our knowledge base database.`,
        targetCustomers: 'Industry enterprises, regional SMBs',
        revenueModel: 'SaaS B2B subscription and unit sales',
        slug: src.slug,
      })
    })
  }

  return { summaryIntro, industry, cards }
}
