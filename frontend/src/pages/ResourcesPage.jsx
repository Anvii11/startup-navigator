import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { useResources } from '@/features/content/hooks'

const CURATED_TOOLKIT = [
  // AI Tools
  { name: 'ChatGPT', category: 'AI Tools', icon: '🤖', description: 'General-purpose AI assistant for research, strategy, and content.', url: 'https://chatgpt.com/', featured: true },
  { name: 'Claude', category: 'AI Tools', icon: '🧠', description: 'Long-context AI reasoning assistant for complex analysis & coding.', url: 'https://claude.ai/', featured: true },
  { name: 'Gemini', category: 'AI Tools', icon: '✨', description: 'Multimodal AI model integrated with Google ecosystem.', url: 'https://gemini.google.com/', featured: false },
  { name: 'Cursor', category: 'AI Tools', icon: '💻', description: 'AI-assisted IDE built for high-velocity software engineering.', url: 'https://cursor.com/', featured: true },
  { name: 'GitHub Copilot', category: 'AI Tools', icon: '⚡', description: 'AI pair programmer for real-time code autocompletion.', url: 'https://github.com/features/copilot', featured: false },
  { name: 'Perplexity', category: 'AI Tools', icon: '🔍', description: 'AI search engine providing cited market research.', url: 'https://www.perplexity.ai/', featured: true },

  // Design
  { name: 'Figma', category: 'Design', icon: '🎨', description: 'Collaborative UI/UX design and vector wireframing tool.', url: 'https://www.figma.com/', featured: true },
  { name: 'Canva', category: 'Design', icon: '🖼️', description: 'Quick brand identity, pitch deck, and social media creative platform.', url: 'https://www.canva.com/', featured: false },

  // Development
  { name: 'GitHub', category: 'Development', icon: '🐙', description: 'Version control repository hosting and DevOps CI/CD pipeline.', url: 'https://github.com/', featured: true },
  { name: 'Vercel', category: 'Development', icon: '▲', description: 'Frontend cloud platform for instant static & Next.js deployment.', url: 'https://vercel.com/', featured: true },
  { name: 'Render', category: 'Development', icon: '🚀', description: 'Unified cloud hosting for FastAPI backends, PostgreSQL, and Web Services.', url: 'https://render.com/', featured: false },
  { name: 'Railway', category: 'Development', icon: '🚂', description: 'Infrastructure platform for rapid backend deployment & database provisioning.', url: 'https://railway.app/', featured: false },

  // Startup & Government
  { name: 'Startup India', category: 'Startup', icon: '🇮🇳', description: 'Official DPIIT recognition portal for tax benefits, grants & schemes.', url: 'https://www.startupindia.gov.in/', featured: true },
  { name: 'DPIIT Portal', category: 'Startup', icon: '🏛️', description: 'Department for Promotion of Industry and Internal Trade certificate portal.', url: 'https://dpiit.gov.in/', featured: false },
  { name: 'MCA Portal', category: 'Startup', icon: '🏢', description: 'Ministry of Corporate Affairs company incorporation & compliance.', url: 'https://www.mca.gov.in/', featured: true },
  { name: 'GST Portal', category: 'Startup', icon: '🧾', description: 'Official Goods and Services Tax registration & return filing system.', url: 'https://www.gst.gov.in/', featured: true },
  { name: 'MSME Udyam Portal', category: 'Startup', icon: '⚙️', description: 'Government MSME registration for credit guarantees & subsidies.', url: 'https://udyamregistration.gov.in/', featured: true },

  // Manufacturing
  { name: 'IndiaMART', category: 'Manufacturing', icon: '🏭', description: 'B2B marketplace for industrial machinery, raw materials, & local suppliers.', url: 'https://www.indiamart.com/', featured: true },
  { name: 'Alibaba', category: 'Manufacturing', icon: '🌐', description: 'Global wholesale sourcing marketplace for industrial equipment & tooling.', url: 'https://www.alibaba.com/', featured: false },
  { name: 'PCBWay', category: 'Manufacturing', icon: '🔌', description: 'Quick-turn prototype PCB fabrication, SMT assembly, & 3D printing.', url: 'https://www.pcbway.com/', featured: true },
  { name: 'JLCPCB', category: 'Manufacturing', icon: '⚡', description: 'Low-cost rapid PCB manufacturing and component assembly services.', url: 'https://jlcpcb.com/', featured: true },

  // Learning
  { name: 'Y Combinator Library', category: 'Learning', icon: '📚', description: 'Essays, videos, and Startup School playbooks for early-stage founders.', url: 'https://www.ycombinator.com/library', featured: true },
  { name: 'Coursera', category: 'Learning', icon: '🎓', description: 'University courses on engineering, business, and AI technology.', url: 'https://www.coursera.org/', featured: false },
  { name: 'MIT OpenCourseWare', category: 'Learning', icon: '🏛️', description: 'Free course material covering computer science, robotics, & engineering.', url: 'https://ocw.mit.edu/', featured: false },
]

const CATEGORIES = ['All', 'AI Tools', 'Design', 'Development', 'Startup', 'Manufacturing', 'Learning']

export default function ResourcesPage() {
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [showFeaturedOnly, setShowFeaturedOnly] = useState(false)

  // Query API resources to seamlessly merge database entries
  const apiResourcesQuery = useResources({ page_size: 50 })
  const apiItems = apiResourcesQuery.data?.items || []

  const allResources = useMemo(() => {
    const combined = [...CURATED_TOOLKIT]
    apiItems.forEach((dbItem) => {
      if (!combined.some((c) => c.name.toLowerCase() === dbItem.title.toLowerCase())) {
        combined.push({
          name: dbItem.title,
          category: dbItem.category?.name || (dbItem.type === 'tool' ? 'AI Tools' : 'Learning'),
          icon: dbItem.type === 'tool' ? '🛠️' : '📄',
          description: dbItem.description,
          url: dbItem.url,
          featured: dbItem.is_featured || false,
        })
      }
    })
    return combined
  }, [apiItems])

  const filteredResources = useMemo(() => {
    return allResources.filter((item) => {
      if (showFeaturedOnly && !item.featured) return false
      if (selectedCategory !== 'All' && item.category !== selectedCategory) return false
      if (search.trim()) {
        const q = search.toLowerCase()
        const matchesName = item.name.toLowerCase().includes(q)
        const matchesDesc = item.description.toLowerCase().includes(q)
        const matchesCat = item.category.toLowerCase().includes(q)
        if (!matchesName && !matchesDesc && !matchesCat) return false
      }
      return true
    })
  }, [allResources, selectedCategory, showFeaturedOnly, search])

  return (
    <div className="space-y-8">
      {/* Header */}
      <header className="space-y-2">
        <h1 className="font-display text-3xl font-bold text-ink sm:text-4xl">
          Curated Founder Toolkit
        </h1>
        <p className="max-w-2xl text-sm text-ink-muted leading-relaxed">
          Hand-picked tools, government portals, manufacturing platforms, AI copilots, and learning hubs to accelerate your startup execution.
        </p>
      </header>

      {/* Search & Filter Bar */}
      <div className="grid gap-3 rounded-2xl border border-border bg-white p-4 sm:grid-cols-4">
        <div className="sm:col-span-3 relative">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search tools (e.g. Figma, PCBWay, Startup India, Cursor)..."
            className="w-full rounded-xl border border-border px-3.5 py-2.5 text-xs font-medium outline-none focus:ring-2 focus:ring-accent/30"
          />
        </div>

        <label className="flex items-center justify-center gap-2 rounded-xl border border-border bg-slate-50 px-3.5 py-2.5 text-xs font-semibold text-ink cursor-pointer hover:bg-slate-100">
          <input
            type="checkbox"
            checked={showFeaturedOnly}
            onChange={(e) => setShowFeaturedOnly(e.target.checked)}
            className="rounded text-accent focus:ring-accent"
          />
          <span>Featured Only</span>
        </label>
      </div>

      {/* Category Chips Filtering */}
      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map((cat) => {
          const active = selectedCategory === cat
          return (
            <button
              key={cat}
              type="button"
              onClick={() => setSelectedCategory(cat)}
              className={[
                'rounded-xl px-3.5 py-1.5 text-xs font-semibold transition',
                active
                  ? 'bg-accent text-white shadow-xs'
                  : 'bg-white text-ink-muted border border-border/60 hover:bg-slate-50 hover:text-ink',
              ].join(' ')}
            >
              {cat === 'All' ? '🌐 All Toolkit' : cat}
            </button>
          )
        })}
      </div>

      {/* Grid of Resource Cards */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {filteredResources.map((item, idx) => (
          <motion.div
            key={idx}
            whileHover={{ y: -3 }}
            transition={{ duration: 0.2 }}
            className="group flex flex-col justify-between overflow-hidden rounded-2xl border border-border bg-white p-5 shadow-xs hover:shadow-md transition-all"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl bg-slate-100 flex items-center justify-center text-xl font-bold border border-slate-200/60 shadow-xs">
                    {item.icon}
                  </div>
                  <div>
                    <h3 className="font-display text-base font-bold text-ink transition group-hover:text-accent">
                      {item.name}
                    </h3>
                    <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-600">
                      {item.category}
                    </span>
                  </div>
                </div>
                {item.featured ? (
                  <span className="rounded-md bg-accent-soft px-2 py-0.5 text-[10px] font-bold text-accent">
                    Featured
                  </span>
                ) : null}
              </div>

              <p className="text-xs text-ink-muted leading-relaxed line-clamp-3">
                {item.description}
              </p>
            </div>

            <div className="pt-4 mt-2 border-t border-border/60">
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center w-full rounded-xl bg-surface hover:bg-accent hover:text-white border border-border/80 py-2 text-xs font-semibold text-ink transition gap-1"
              >
                <span>Visit Website</span>
                <span>↗</span>
              </a>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
