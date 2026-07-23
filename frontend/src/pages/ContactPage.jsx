import { useState } from 'react'
import toast from 'react-hot-toast'
import { PageShell } from '@/shared/ui/PageShell'

const FAQS = [
  {
    q: 'How are startup and manufacturing ideas curated on the platform?',
    a: 'Our research team collaborates with domain experts, industrial engineers, and MSME consultants to build structured blueprints covering problem statements, equipment costs, unit economics, and 90-day execution roadmaps.'
  },
  {
    q: 'How does the RAG AI Search assistant work?',
    a: 'The AI assistant uses Retrieval-Augmented Generation (RAG) to query our internal vector database of startup playbooks first, synthesizing grounded answers with direct source title citations.'
  },
  {
    q: 'Can I submit or publish my own startup idea?',
    a: 'Yes! Registered administrators can add, edit, and publish new ideas directly through the CMS Admin dashboard, which automatically re-indexes the RAG vector store in real-time.'
  },
  {
    q: 'Are government schemes and subsidies updated for Indian founders?',
    a: 'Yes, playbooks explicitly detail applicable schemes like Startup India Seed Fund (SISFS), PMEGP 35% subsidies, RKVY-RAFTAAR agritech grants, and DPIIT 80-IAC tax exemptions.'
  }
]

export default function ContactPage() {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' })
  const [submitted, setSubmitted] = useState(false)
  const [openFaq, setOpenFaq] = useState(null)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!form.name || !form.email || !form.message) {
      toast.error('Please fill in required fields.')
      return
    }
    setSubmitted(true)
    toast.success("Thank you for contacting us. We'll get back to you shortly.")
  }

  return (
    <PageShell
      title="Contact Us"
      description="Have questions about startup blueprints, manufacturing setup, or platform features? Get in touch with our team."
    >
      <div className="space-y-12 max-w-5xl">
        <div className="grid gap-8 lg:grid-cols-[1fr_360px]">
          {/* ── 1. CONTACT FORM ────────────────────────────────────────── */}
          <div className="rounded-3xl border border-border bg-white p-6 sm:p-8 space-y-6 shadow-xs">
            <h2 className="font-display text-xl font-bold text-ink">Send Us a Message</h2>

            {submitted ? (
              <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-6 text-center space-y-2">
                <span className="text-3xl">✅</span>
                <h3 className="font-display text-lg font-bold text-emerald-900">Message Received!</h3>
                <p className="text-xs text-emerald-800 leading-relaxed font-medium">
                  Thank you for contacting us. We'll get back to you shortly.
                </p>
                <button
                  type="button"
                  onClick={() => { setSubmitted(false); setForm({ name: '', email: '', subject: '', message: '' }); }}
                  className="mt-2 text-xs font-semibold text-accent underline"
                >
                  Send another message
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-1">
                    <label className="block text-xs font-semibold text-ink">Your Name *</label>
                    <input
                      required
                      value={form.name}
                      onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                      placeholder="e.g. Rahul Sharma"
                      className="w-full rounded-xl border border-border px-3.5 py-2 text-sm outline-none focus:border-accent"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="block text-xs font-semibold text-ink">Business Email *</label>
                    <input
                      required
                      type="email"
                      value={form.email}
                      onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                      placeholder="rahul@startup.com"
                      className="w-full rounded-xl border border-border px-3.5 py-2 text-sm outline-none focus:border-accent"
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="block text-xs font-semibold text-ink">Subject</label>
                  <input
                    value={form.subject}
                    onChange={(e) => setForm((f) => ({ ...f, subject: e.target.value }))}
                    placeholder="e.g. SMT Manufacturing Blueprint Inquiry"
                    className="w-full rounded-xl border border-border px-3.5 py-2 text-sm outline-none focus:border-accent"
                  />
                </div>

                <div className="space-y-1">
                  <label className="block text-xs font-semibold text-ink">Message *</label>
                  <textarea
                    required
                    value={form.message}
                    onChange={(e) => setForm((f) => ({ ...f, message: e.target.value }))}
                    placeholder="How can we help your startup?"
                    className="min-h-32 w-full rounded-xl border border-border px-3.5 py-2.5 text-sm outline-none focus:border-accent"
                  />
                </div>

                <button
                  type="submit"
                  className="rounded-xl bg-accent px-6 py-3 text-sm font-semibold text-white hover:bg-accent-hover transition shadow-xs"
                >
                  Send Message
                </button>
                <p className="mt-2 text-xs text-ink-muted">
                  We typically respond within 24–48 business hours.
                </p>
              </form>
            )}
          </div>

          {/* ── 2. BUSINESS INFO CARD ──────────────────────────────────── */}
          <div className="space-y-6">
            <div className="rounded-3xl border border-border bg-white p-6 space-y-5 shadow-xs">
              <h2 className="font-display text-lg font-bold text-ink">Contact Details</h2>

              <div className="space-y-4 text-xs">
                <div className="flex items-start gap-3">
                  <span className="text-base">📧</span>
                  <div>
                    <span className="font-bold text-ink block">Business Email</span>
                    <a href="mailto:support@startupnavigator.io" className="text-accent font-medium hover:underline">
                      support@startupnavigator.io
                    </a>
                  </div>
                </div>

                <div className="flex items-start gap-3 border-t border-border/60 pt-3">
                  <span className="text-base">📍</span>
                  <div>
                    <span className="font-bold text-ink block">Locations</span>
                    <p className="text-ink-muted">Bengaluru Tech Hub & New Delhi, India</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 border-t border-border/60 pt-3">
                  <span className="text-base">⏰</span>
                  <div>
                    <span className="font-bold text-ink block">Working Hours</span>
                    <p className="text-ink-muted">Monday - Friday: 9:00 AM - 6:00 PM IST</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ── 3. FAQ ACCORDION SECTION ────────────────────────────────── */}
        <div className="rounded-3xl border border-border bg-white p-6 sm:p-8 space-y-6 shadow-xs">
          <div className="space-y-1">
            <h2 className="font-display text-xl font-bold text-ink">Frequently Asked Questions</h2>
            <p className="text-xs text-ink-muted">Quick answers to common questions about Startup Navigator.</p>
          </div>

          <div className="divide-y divide-border/60">
            {FAQS.map((faq, idx) => {
              const isOpen = openFaq === idx
              return (
                <div key={idx} className="py-4 space-y-2">
                  <button
                    type="button"
                    onClick={() => setOpenFaq(isOpen ? null : idx)}
                    className="flex w-full items-center justify-between text-left text-sm font-semibold text-ink hover:text-accent transition"
                  >
                    <span>{faq.q}</span>
                    <span className="text-xs font-bold text-accent ml-2">{isOpen ? '−' : '＋'}</span>
                  </button>
                  {isOpen ? (
                    <p className="text-xs text-ink-muted leading-relaxed pt-1">
                      {faq.a}
                    </p>
                  ) : null}
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </PageShell>
  )
}
