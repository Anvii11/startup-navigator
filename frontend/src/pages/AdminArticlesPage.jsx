import { useMemo, useState } from 'react'
import toast from 'react-hot-toast'
import {
  useAdminArticles,
  useAdminArticleMutations,
  useAdminCategories,
} from '@/features/content/hooks'
import { adminFetchArticle } from '@/features/content/api'
import { ConfirmDialog } from '@/shared/ui/ConfirmDialog'
import { EmptyState } from '@/shared/ui/EmptyState'
import { ErrorState } from '@/shared/ui/ErrorState'
import { Loading } from '@/shared/ui/Loading'

const PRESET_TAGS = [
  'manufacturing',
  'hardware',
  'prototyping',
  'investment-low',
  'investment-medium',
  'investment-high',
  'ai-high',
  'ai-hybrid',
  'ai-non-ai',
  'bootstrap',
  'compliance',
]

const emptyForm = {
  title: '',
  summary: '',
  content: '',
  category_id: '',
  status: 'published',
  difficulty: 'beginner',
  estimated_reading_time: '',
  thumbnail: '',
  tags: '',
  slug: '',
}

export default function AdminArticlesPage() {
  const [search, setSearch] = useState('')
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState(null)
  const [deleteId, setDeleteId] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [loadingEdit, setLoadingEdit] = useState(false)

  const categories = useAdminCategories({ page_size: 100 })
  const articles = useAdminArticles({ page, page_size: 10, search: query || undefined })
  const { create, update, remove } = useAdminArticleMutations()

  const categoryOptions = categories.data?.items || []
  const pages = articles.data?.pages || 1

  const payloadFromForm = useMemo(
    () => ({
      title: form.title.trim(),
      summary: form.summary.trim() || null,
      content: form.content,
      category_id: Number(form.category_id),
      status: form.status,
      difficulty: form.difficulty,
      estimated_reading_time: form.estimated_reading_time
        ? Number(form.estimated_reading_time)
        : null,
      thumbnail: form.thumbnail.trim() || null,
      tags: form.tags
        ? form.tags.split(',').map((t) => t.trim()).filter(Boolean)
        : null,
      slug: form.slug.trim() || null,
    }),
    [form]
  )

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!payloadFromForm.category_id) {
      toast.error('Please select an industry category')
      return
    }
    try {
      if (editingId) {
        await update.mutateAsync({ id: editingId, payload: payloadFromForm })
        toast.success('Startup idea updated successfully')
      } else {
        await create.mutateAsync(payloadFromForm)
        toast.success('New startup idea published')
      }
      setForm(emptyForm)
      setEditingId(null)
      setShowForm(false)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Save operation failed')
    }
  }

  const startEdit = async (article) => {
    setEditingId(article.id)
    setShowForm(true)
    setLoadingEdit(true)
    try {
      const full = await adminFetchArticle(article.id)
      setForm({
        title: full.title,
        summary: full.summary || '',
        content: full.content || '',
        category_id: String(full.category?.id || full.category_id || ''),
        status: full.status,
        difficulty: full.difficulty,
        estimated_reading_time: String(full.estimated_reading_time || ''),
        thumbnail: full.thumbnail || '',
        tags: (full.tags || []).join(', '),
        slug: full.slug,
      })
    } catch {
      toast.error('Could not load idea details for editing')
    } finally {
      setLoadingEdit(false)
    }
  }

  const addTag = (tag) => {
    const currentTags = form.tags
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean)
    if (!currentTags.includes(tag)) {
      setForm((f) => ({ ...f, tags: [...currentTags, tag].join(', ') }))
    }
  }

  if (articles.isLoading && !articles.data) return <Loading label="Loading startup ideas CMS…" />
  if (articles.isError) return <ErrorState title="Failed to load startup ideas" onRetry={articles.refetch} />

  return (
    <div className="space-y-6">
      {/* CMS Header */}
      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-border/60 pb-5">
        <div>
          <h1 className="font-display text-3xl font-bold text-ink">Startup Ideas CMS</h1>
          <p className="mt-1 text-sm text-ink-muted">
            Manage, publish, and re-index startup & manufacturing ideas for the AI assistant.
          </p>
        </div>
        <button
          type="button"
          onClick={() => {
            setShowForm((v) => !v)
            if (showForm) {
              setEditingId(null)
              setForm(emptyForm)
            }
          }}
          className="rounded-xl bg-accent px-5 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-accent-hover transition flex items-center gap-2"
        >
          <span>{showForm ? '✕ Close Editor' : '＋ Add New Idea'}</span>
        </button>
      </header>

      {/* Search Bar */}
      <form
        className="flex gap-3"
        onSubmit={(e) => {
          e.preventDefault()
          setPage(1)
          setQuery(search.trim())
        }}
      >
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by title, summary, or category..."
          className="w-full max-w-md rounded-xl border border-border bg-white px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-accent/30"
        />
        <button
          type="submit"
          className="rounded-xl border border-border bg-white px-4 py-2.5 text-sm font-medium hover:bg-slate-50 transition"
        >
          Search
        </button>
      </form>

      {/* ── CREATE / EDIT IDEA FORM ────────────────────────────────────── */}
      {showForm ? (
        <form onSubmit={onSubmit} className="grid gap-4 rounded-3xl border border-border bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <h2 className="font-display text-lg font-bold text-ink">
              {editingId ? 'Edit Startup Idea' : 'Create New Startup Idea'}
            </h2>
            {loadingEdit ? <span className="text-xs text-accent">Loading details...</span> : null}
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-1">
              <label className="block text-xs font-semibold text-ink">Idea Title *</label>
              <input
                required
                value={form.title}
                onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                placeholder="e.g. Smart IoT Edge Controller Fabrication"
                className="w-full rounded-xl border border-border px-3.5 py-2 text-sm outline-none focus:border-accent"
              />
            </div>

            <div className="space-y-1">
              <label className="block text-xs font-semibold text-ink">Custom Slug (Optional)</label>
              <input
                value={form.slug}
                onChange={(e) => setForm((f) => ({ ...f, slug: e.target.value }))}
                placeholder="e.g. smart-iot-edge-controller"
                className="w-full rounded-xl border border-border px-3.5 py-2 text-sm outline-none focus:border-accent"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-semibold text-ink">Executive Summary</label>
            <textarea
              value={form.summary}
              onChange={(e) => setForm((f) => ({ ...f, summary: e.target.value }))}
              placeholder="A 2-3 sentence overview of the idea, problem solved, and value proposition..."
              className="min-h-20 w-full rounded-xl border border-border px-3.5 py-2 text-sm outline-none focus:border-accent"
            />
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-semibold text-ink">Full Playbook & Description (Markdown) *</label>
            <textarea
              required
              value={form.content}
              onChange={(e) => setForm((f) => ({ ...f, content: e.target.value }))}
              placeholder="## Core Operating Playbook&#10;&#10;Describe problem, solution, market size, execution steps..."
              className="min-h-48 w-full rounded-xl border border-border px-3.5 py-2.5 font-mono text-sm outline-none focus:border-accent"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-1">
              <label className="block text-xs font-semibold text-ink">Category / Industry *</label>
              <select
                required
                value={form.category_id}
                onChange={(e) => setForm((f) => ({ ...f, category_id: e.target.value }))}
                className="w-full rounded-xl border border-border px-3 py-2 text-sm outline-none focus:border-accent"
              >
                <option value="">Select Category</option>
                {categoryOptions.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1">
              <label className="block text-xs font-semibold text-ink">Publication Status</label>
              <select
                value={form.status}
                onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
                className="w-full rounded-xl border border-border px-3 py-2 text-sm outline-none focus:border-accent"
              >
                <option value="published">Published</option>
                <option value="draft">Draft</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="block text-xs font-semibold text-ink">Difficulty</label>
              <select
                value={form.difficulty}
                onChange={(e) => setForm((f) => ({ ...f, difficulty: e.target.value }))}
                className="w-full rounded-xl border border-border px-3 py-2 text-sm outline-none focus:border-accent"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="block text-xs font-semibold text-ink">Est. Read Time (Minutes)</label>
              <input
                type="number"
                min="1"
                value={form.estimated_reading_time}
                onChange={(e) => setForm((f) => ({ ...f, estimated_reading_time: e.target.value }))}
                placeholder="Auto-calculated if blank"
                className="w-full rounded-xl border border-border px-3 py-2 text-sm outline-none focus:border-accent"
              />
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-1">
              <label className="block text-xs font-semibold text-ink">Thumbnail Image URL</label>
              <input
                value={form.thumbnail}
                onChange={(e) => setForm((f) => ({ ...f, thumbnail: e.target.value }))}
                placeholder="https://images.unsplash.com/..."
                className="w-full rounded-xl border border-border px-3.5 py-2 text-sm outline-none focus:border-accent"
              />
            </div>

            <div className="space-y-1">
              <label className="block text-xs font-semibold text-ink">Tags (Comma Separated)</label>
              <input
                value={form.tags}
                onChange={(e) => setForm((f) => ({ ...f, tags: e.target.value }))}
                placeholder="manufacturing, hardware, investment-low, ai-hybrid"
                className="w-full rounded-xl border border-border px-3.5 py-2 text-sm outline-none focus:border-accent"
              />
            </div>
          </div>

          {/* Quick Tag Presets */}
          <div className="space-y-1.5 pt-1">
            <span className="text-xs text-ink-muted">Quick add tags:</span>
            <div className="flex flex-wrap gap-1.5">
              {PRESET_TAGS.map((tag) => (
                <button
                  key={tag}
                  type="button"
                  onClick={() => addTag(tag)}
                  className="rounded-lg bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-700 hover:bg-accent-soft hover:text-accent transition"
                >
                  +{tag}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-3 border-t border-border">
            <button
              type="submit"
              disabled={create.isPending || update.isPending}
              className="rounded-xl bg-accent px-5 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-accent-hover transition disabled:opacity-50"
            >
              {editingId ? 'Save Changes' : 'Publish Idea'}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowForm(false)
                setEditingId(null)
                setForm(emptyForm)
              }}
              className="rounded-xl border border-border px-4 py-2.5 text-sm font-medium text-ink-muted hover:bg-slate-50 transition"
            >
              Cancel
            </button>
          </div>
        </form>
      ) : null}

      {/* ── IDEAS MANAGEMENT TABLE ────────────────────────────────────── */}
      {!articles.data?.items?.length ? (
        <EmptyState title="No startup ideas found" message="Click 'Add New Idea' to create the first entry." />
      ) : (
        <div className="overflow-hidden rounded-2xl border border-border bg-white shadow-xs">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="border-b border-border bg-slate-50/80 text-xs font-semibold uppercase tracking-wider text-ink-muted">
              <tr>
                <th className="px-5 py-3.5">Idea Title</th>
                <th className="px-5 py-3.5">Category</th>
                <th className="px-5 py-3.5">Status</th>
                <th className="px-5 py-3.5">Difficulty</th>
                <th className="px-5 py-3.5">Views</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {articles.data.items.map((article) => (
                <tr key={article.id} className="hover:bg-slate-50/50 transition">
                  <td className="px-5 py-4">
                    <p className="font-semibold text-ink">{article.title}</p>
                    <p className="text-xs text-ink-muted font-mono">{article.slug}</p>
                  </td>
                  <td className="px-5 py-4">
                    <span
                      className="rounded-md px-2 py-0.5 text-xs font-medium text-white shadow-xs"
                      style={{ backgroundColor: article.category?.color || '#1a6b4a' }}
                    >
                      {article.category?.name || 'Uncategorized'}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${
                        article.status === 'published'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-amber-50 text-amber-700 border border-amber-200'
                      }`}
                    >
                      {article.status}
                    </span>
                  </td>
                  <td className="px-5 py-4 capitalize text-xs font-medium text-slate-600">
                    {article.difficulty}
                  </td>
                  <td className="px-5 py-4 text-xs font-mono text-ink-muted">
                    {article.view_count || 0}
                  </td>
                  <td className="px-5 py-4 text-right">
                    <div className="flex items-center justify-end gap-3">
                      <button
                        type="button"
                        className="text-xs font-semibold text-accent hover:underline"
                        onClick={() => startEdit(article)}
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        className="text-xs font-semibold text-rose-600 hover:underline"
                        onClick={() => setDeleteId(article.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination Controls */}
      {pages > 1 ? (
        <div className="flex items-center justify-between pt-2">
          <span className="text-xs text-ink-muted">
            Page <span className="font-semibold text-ink">{page}</span> of{' '}
            <span className="font-semibold text-ink">{pages}</span>
          </span>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="rounded-xl border border-border bg-white px-3 py-1.5 text-xs font-medium disabled:opacity-40"
            >
              Previous
            </button>
            <button
              type="button"
              disabled={page >= pages}
              onClick={() => setPage((p) => p + 1)}
              className="rounded-xl border border-border bg-white px-3 py-1.5 text-xs font-medium disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      ) : null}

      {/* Confirmation Dialog */}
      <ConfirmDialog
        open={Boolean(deleteId)}
        title="Delete Startup Idea?"
        message="This permanently removes the idea from both the database and the RAG AI vector index."
        loading={remove.isPending}
        onCancel={() => setDeleteId(null)}
        onConfirm={async () => {
          try {
            await remove.mutateAsync(deleteId)
            toast.success('Idea deleted and vector store updated')
            setDeleteId(null)
          } catch (err) {
            toast.error(err.response?.data?.detail || 'Delete failed')
          }
        }}
      />
    </div>
  )
}
