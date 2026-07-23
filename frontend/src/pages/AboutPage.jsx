import { PageShell } from '@/shared/ui/PageShell'

export default function AboutPage() {
  return (
    <PageShell
      title="About Startup Navigator"
      description="Empowering founders, operators, and engineers with structured startup ideas, manufacturing playbooks, and grounded AI intelligence."
    >
      <div className="space-y-10 max-w-4xl">
        {/* Mission & Vision Cards */}
        <div className="grid gap-6 md:grid-cols-2">
          <div className="rounded-2xl border border-emerald-100 bg-emerald-50/60 p-6 space-y-2">
            <h2 className="font-display text-lg font-bold text-emerald-900 flex items-center gap-2">
              <span>🎯 Our Mission</span>
            </h2>
            <p className="text-xs text-slate-700 leading-relaxed">
              To bridge the gap between high-level startup concepts and ground-level execution. We provide structured blueprints, validated unit economics, and hardware manufacturing playbooks so entrepreneurs can build scalable ventures faster.
            </p>
          </div>

          <div className="rounded-2xl border border-sky-100 bg-sky-50/60 p-6 space-y-2">
            <h2 className="font-display text-lg font-bold text-sky-900 flex items-center gap-2">
              <span>🚀 Our Vision</span>
            </h2>
            <p className="text-xs text-slate-700 leading-relaxed">
              To become the world's most trusted, AI-grounded discovery engine for physical and digital startups—democratizing access to supply chain insights, government schemes, and technical roadmaps.
            </p>
          </div>
        </div>

        {/* Core Platform Features */}
        <div className="space-y-4">
          <h2 className="font-display text-2xl font-bold text-ink">
            ✨ Key Platform Features
          </h2>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-2xl border border-border bg-white p-5 space-y-2 shadow-xs">
              <div className="h-9 w-9 rounded-xl bg-accent-soft text-accent flex items-center justify-center font-bold text-lg">
                💡
              </div>
              <h3 className="font-display text-base font-bold text-ink">AI-Powered Startup Discovery</h3>
              <p className="text-xs text-ink-muted leading-relaxed">
                Filter 70+ structured startup & manufacturing playbooks by industry, investment range (under ₹10 Lakh to Growth), AI integration level, and difficulty.
              </p>
            </div>

            <div className="rounded-2xl border border-border bg-white p-5 space-y-2 shadow-xs">
              <div className="h-9 w-9 rounded-xl bg-accent-soft text-accent flex items-center justify-center font-bold text-lg">
                🏭
              </div>
              <h3 className="font-display text-base font-bold text-ink">Manufacturing Idea Database</h3>
              <p className="text-xs text-ink-muted leading-relaxed">
                Detailed micro-factory blueprints including PCB SMT assembly lines, CNC metal machining, 3D printing bureaus, and food processing plants.
              </p>
            </div>

            <div className="rounded-2xl border border-border bg-white p-5 space-y-2 shadow-xs">
              <div className="h-9 w-9 rounded-xl bg-accent-soft text-accent flex items-center justify-center font-bold text-lg">
                🔍
              </div>
              <h3 className="font-display text-base font-bold text-ink">RAG-Powered Intelligent Search</h3>
              <p className="text-xs text-ink-muted leading-relaxed">
                Grounded AI search assistant powered by Retrieval-Augmented Generation that queries internal knowledge documents and cites exact sources.
              </p>
            </div>

            <div className="rounded-2xl border border-border bg-white p-5 space-y-2 shadow-xs">
              <div className="h-9 w-9 rounded-xl bg-accent-soft text-accent flex items-center justify-center font-bold text-lg">
                🛠️
              </div>
              <h3 className="font-display text-base font-bold text-ink">Curated Founder Toolkit</h3>
              <p className="text-xs text-ink-muted leading-relaxed">
                Direct access to top AI tools, government portals (DPIIT, MCA, GST, MSME), manufacturing platforms (IndiaMART, PCBWay), and learning hubs.
              </p>
            </div>

            <div className="rounded-2xl border border-border bg-white p-5 space-y-2 shadow-xs">
              <div className="h-9 w-9 rounded-xl bg-accent-soft text-accent flex items-center justify-center font-bold text-lg">
                🗺️
              </div>
              <h3 className="font-display text-base font-bold text-ink">90-Day Execution Roadmaps</h3>
              <p className="text-xs text-ink-muted leading-relaxed">
                Step-by-step phased execution frameworks (Validation, MVP build, GTM launch) designed for immediate team deployment.
              </p>
            </div>

            <div className="rounded-2xl border border-border bg-white p-5 space-y-2 shadow-xs">
              <div className="h-9 w-9 rounded-xl bg-accent-soft text-accent flex items-center justify-center font-bold text-lg">
                📊
              </div>
              <h3 className="font-display text-base font-bold text-ink">Unit Economics & Schemes</h3>
              <p className="text-xs text-ink-muted leading-relaxed">
                Budget breakdowns, capital requirements, revenue models, and applicable government subsidies (PMEGP, SISFS, RKVY-RAFTAAR).
              </p>
            </div>
          </div>
        </div>

        {/* Technology Stack */}
        <div className="rounded-2xl border border-border bg-white p-6 space-y-4 shadow-xs">
          <h2 className="font-display text-xl font-bold text-ink">
            ⚙️ Technology Stack
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-4 text-xs">
            <div className="space-y-1">
              <span className="font-bold text-accent uppercase text-[10px]">Backend Framework</span>
              <p className="font-semibold text-ink">FastAPI (Python 3.12+)</p>
              <p className="text-ink-muted">High-performance async REST API with Pydantic validation.</p>
            </div>

            <div className="space-y-1">
              <span className="font-bold text-accent uppercase text-[10px]">Frontend UI</span>
              <p className="font-semibold text-ink">React 19 & Tailwind CSS v4</p>
              <p className="text-ink-muted">Modern component hierarchy, Framer Motion animations, DM Sans font.</p>
            </div>

            <div className="space-y-1">
              <span className="font-bold text-accent uppercase text-[10px]">RAG Vector Pipeline</span>
              <p className="font-semibold text-ink">ChromaDB & Hybrid TF-IDF</p>
              <p className="text-ink-muted">Semantic vector search + domain token boosting retrieval.</p>
            </div>

            <div className="space-y-1">
              <span className="font-bold text-accent uppercase text-[10px]">LLM Provider</span>
              <p className="font-semibold text-ink">OpenAI / Gemini / Mock</p>
              <p className="text-ink-muted">Multi-provider fallback architecture for grounded generation.</p>
            </div>
          </div>
        </div>

        {/* Why Useful */}
        <div className="rounded-2xl border border-slate-200 bg-slate-900 p-8 text-white space-y-3 shadow-md">
          <h2 className="font-display text-2xl font-bold">
            💡 Why Startup Navigator Is Useful For Founders
          </h2>
          <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
            Starting a business requires navigating complex regulatory approvals, equipment procurement, and capital allocation. Startup Navigator replaces generic advice with verifiable blueprints, clear budget benchmarks, and an intelligent AI assistant that answers specific questions grounded in factual data.
          </p>
        </div>
      </div>
    </PageShell>
  )
}
