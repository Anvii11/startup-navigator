import { Link } from 'react-router-dom'

export function Footer() {
  return (
    <footer className="border-t border-border/80 bg-slate-900 text-slate-300">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6">
        <div className="grid gap-8 md:grid-cols-4">
          {/* Brand Info */}
          <div className="space-y-4 md:col-span-2">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-white font-bold text-sm">
                💡
              </div>
              <span className="font-display text-xl font-bold tracking-tight text-white">
                Startup Navigator
              </span>
            </div>
            <p className="max-w-md text-xs text-slate-400 leading-relaxed">
              A modern discovery platform for startup & manufacturing ideas. Grounded AI search powered by internal knowledge bases, unit economics models, and 90-day execution roadmaps.
            </p>
          </div>

          {/* Platform Quick Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Platform Links
            </h4>
            <ul className="space-y-2 text-xs text-slate-400">
              <li>
                <Link to="/explore" className="hover:text-white transition">
                  Explore Ideas
                </Link>
              </li>
              <li>
                <Link to="/search" className="hover:text-white transition">
                  AI Search Assistant
                </Link>
              </li>
              <li>
                <Link to="/resources" className="hover:text-white transition">
                  Curated Resources
                </Link>
              </li>
              <li>
                <Link to="/about" className="hover:text-white transition">
                  About Us
                </Link>
              </li>
            </ul>
          </div>

          {/* Top Categories */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Top Sectors
            </h4>
            <ul className="space-y-2 text-xs text-slate-400">
              <li>
                <Link to="/explore?category=manufacturing-hardware" className="hover:text-white transition">
                  Manufacturing & Hardware
                </Link>
              </li>
              <li>
                <Link to="/explore?category=ai-tools" className="hover:text-white transition">
                  AI Tools & Copilots
                </Link>
              </li>
              <li>
                <Link to="/explore?category=funding" className="hover:text-white transition">
                  Funding & Angel Rounds
                </Link>
              </li>
              <li>
                <Link to="/explore?category=company-registration" className="hover:text-white transition">
                  Company Registration
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-10 border-t border-slate-800 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <p>© {new Date().getFullYear()} Startup Navigator. All rights reserved.</p>
          <div className="flex gap-4">
            <Link to="/explore" className="hover:text-slate-300">Startup Ideas</Link>
            <Link to="/search" className="hover:text-slate-300">RAG AI Search</Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
