import { useState } from 'react'
import toast from 'react-hot-toast'
import {
  useAdminCategories,
  useAdminCategoryMutations,
} from '@/features/content/hooks'
import { ConfirmDialog } from '@/shared/ui/ConfirmDialog'
import { EmptyState } from '@/shared/ui/EmptyState'
import { ErrorState } from '@/shared/ui/ErrorState'
import { Loading } from '@/shared/ui/Loading'

const PRESET_COLORS = [
  '#1a6b4a', // Emerald
  '#0f766e', // Teal
  '#b45309', // Amber
  '#1d4ed8', // Blue
  '#be123c', // Rose
  '#7c3aed', // Purple
  '#0369a1', // Sky
  '#475569', // Slate (Manufacturing)
  '#c2410c', // Orange
  '#15803d', // Green
]

const emptyForm = { name: '', description: '', icon: '', color: '#1a6b4a', slug: '' }

export default function AdminCategoriesPage() {
  const { data, isLoading, isError, refetch } = useAdminCategories({ page_size: 100 })
  const { create, update, remove } = useAdminCategoryMutations()
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState(null)
  const [deleteId, setDeleteId] = useState(null)

  const onSubmit = async (e) => {
    e.preventDefault()
    const payload = {
      name: form.name.trim(),
      description: form.description.trim() || null,
      icon: form.icon.trim() || null,
      color: form.color || null,
      slug: form.slug.trim() || null,
    }
    try {
      if (editingId) {
        await update.mutateAsync({ id: editingId, payload })
        toast.success('Category updated successfully')
      } else {
        await create.mutateAsync(payload)
        toast.success('New category created')
      }
      setForm(emptyForm)
      setEditingId(null)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Save failed')
    }
  }

  const startEdit = (cat) => {
    setEditingId(cat.id)
    setForm({
      name: cat.name,
      description: cat.description || '',
      icon: cat.icon || '',
      color: cat.color || '#1a6b4a',
      slug: cat.slug,
    })
  }

  if (isLoading) return <Loading label="Loading categories CMS…" />
  if (isError) return <ErrorState title="Failed to load categories" onRetry={refetch} />

  return (
    <div className="space-y-6">
      <header className="border-b border-border/60 pb-5">
        <h1 className="font-display text-3xl font-bold text-ink">Categories CMS</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Organize startup and manufacturing ideas taxonomy and categories.
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[340px_1fr]">
        {/* ── Category Form Editor Card ───────────────────────────────── */}
        <form onSubmit={onSubmit} className="rounded-3xl border border-border bg-white p-5 space-y-4 shadow-xs h-fit">
          <div className="border-b border-border pb-3">
            <h2 className="font-display text-base font-bold text-ink">
              {editingId ? 'Edit Category' : 'Create Category'}
            </h2>
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-semibold text-ink">Category Name *</label>
            <input
              required
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              placeholder="e.g. Manufacturing & Hardware"
              className="w-full rounded-xl border border-border px-3.5 py-2 text-sm outline-none focus:border-accent"
            />
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-semibold text-ink">Slug (Optional)</label>
            <input
              value={form.slug}
              onChange={(e) => setForm((f) => ({ ...f, slug: e.target.value }))}
              placeholder="e.g. manufacturing-hardware"
              className="w-full rounded-xl border border-border px-3.5 py-2 text-sm outline-none focus:border-accent"
            />
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-semibold text-ink">Icon Key / Emoji</label>
            <input
              value={form.icon}
              onChange={(e) => setForm((f) => ({ ...f, icon: e.target.value }))}
              placeholder="e.g. cpu, building, coins"
              className="w-full rounded-xl border border-border px-3.5 py-2 text-sm outline-none focus:border-accent"
            />
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-ink">Theme Color</label>
            <div className="flex items-center gap-2">
              <input
                type="color"
                value={form.color}
                onChange={(e) => setForm((f) => ({ ...f, color: e.target.value }))}
                className="h-9 w-12 rounded-lg border border-border cursor-pointer"
              />
              <input
                type="text"
                value={form.color}
                onChange={(e) => setForm((f) => ({ ...f, color: e.target.value }))}
                className="w-full rounded-xl border border-border px-3 py-1.5 text-xs font-mono outline-none focus:border-accent"
              />
            </div>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {PRESET_COLORS.map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => setForm((f) => ({ ...f, color: c }))}
                  className="h-5 w-5 rounded-full border border-black/10 transition hover:scale-110"
                  style={{ backgroundColor: c }}
                />
              ))}
            </div>
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-semibold text-ink">Description</label>
            <textarea
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              placeholder="Short category description..."
              className="min-h-20 w-full rounded-xl border border-border px-3.5 py-2 text-sm outline-none focus:border-accent"
            />
          </div>

          <div className="flex gap-2 pt-2 border-t border-border">
            <button
              type="submit"
              disabled={create.isPending || update.isPending}
              className="rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-white shadow-xs hover:bg-accent-hover transition disabled:opacity-50"
            >
              {editingId ? 'Update' : 'Create Category'}
            </button>
            {editingId ? (
              <button
                type="button"
                onClick={() => {
                  setEditingId(null)
                  setForm(emptyForm)
                }}
                className="rounded-xl border border-border px-3 py-2 text-sm font-medium text-ink-muted hover:bg-slate-50 transition"
              >
                Cancel
              </button>
            ) : null}
          </div>
        </form>

        {/* ── Categories Table List ───────────────────────────────────── */}
        <div>
          {!data?.items?.length ? (
            <EmptyState title="No categories found" message="Create your first category using the form." />
          ) : (
            <div className="overflow-hidden rounded-2xl border border-border bg-white shadow-xs">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-border bg-slate-50/80 text-xs font-semibold uppercase tracking-wider text-ink-muted">
                  <tr>
                    <th className="px-5 py-3.5">Category</th>
                    <th className="px-5 py-3.5">Ideas Count</th>
                    <th className="px-5 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {data.items.map((cat) => (
                    <tr key={cat.id} className="hover:bg-slate-50/50 transition">
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-3">
                          <span
                            className="h-4 w-4 rounded-full shadow-xs flex-shrink-0"
                            style={{ backgroundColor: cat.color || '#1a6b4a' }}
                          />
                          <div>
                            <p className="font-semibold text-ink">{cat.name}</p>
                            <p className="text-xs text-ink-muted font-mono">{cat.slug}</p>
                            {cat.description ? (
                              <p className="text-xs text-ink-muted line-clamp-1 mt-0.5">{cat.description}</p>
                            ) : null}
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-4">
                        <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                          {cat.idea_count || 0} idea(s)
                        </span>
                      </td>
                      <td className="px-5 py-4 text-right">
                        <div className="flex items-center justify-end gap-3">
                          <button
                            type="button"
                            onClick={() => startEdit(cat)}
                            className="text-xs font-semibold text-accent hover:underline"
                          >
                            Edit
                          </button>
                          <button
                            type="button"
                            onClick={() => setDeleteId(cat.id)}
                            className="text-xs font-semibold text-rose-600 hover:underline"
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
        </div>
      </div>

      <ConfirmDialog
        open={Boolean(deleteId)}
        title="Delete Category?"
        message="Categories containing existing startup ideas cannot be deleted. Delete or reassign those ideas first."
        onCancel={() => setDeleteId(null)}
        loading={remove.isPending}
        onConfirm={async () => {
          try {
            await remove.mutateAsync(deleteId)
            toast.success('Category deleted')
            setDeleteId(null)
          } catch (err) {
            toast.error(err.response?.data?.detail || 'Delete failed')
          }
        }}
      />
    </div>
  )
}
