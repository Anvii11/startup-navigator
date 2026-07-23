import { useState } from 'react'
import toast from 'react-hot-toast'
import {
  useAdminCategories,
  useAdminResourceMutations,
  useAdminResources,
} from '@/features/content/hooks'
import { ConfirmDialog } from '@/shared/ui/ConfirmDialog'
import { EmptyState } from '@/shared/ui/EmptyState'
import { ErrorState } from '@/shared/ui/ErrorState'
import { Loading } from '@/shared/ui/Loading'

const emptyForm = {
  title: '',
  url: '',
  description: '',
  type: 'tool',
  category_id: '',
  is_featured: false,
  thumbnail: '',
}

export default function AdminResourcesPage() {
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState(null)
  const [deleteId, setDeleteId] = useState(null)
  const [page, setPage] = useState(1)

  const categories = useAdminCategories({ page_size: 100 })
  const resources = useAdminResources({ page, page_size: 12 })
  const { create, update, remove } = useAdminResourceMutations()

  const onSubmit = async (e) => {
    e.preventDefault()
    const payload = {
      title: form.title.trim(),
      url: form.url.trim(),
      description: form.description.trim() || null,
      type: form.type,
      category_id: form.category_id ? Number(form.category_id) : null,
      is_featured: form.is_featured,
      thumbnail: form.thumbnail.trim() || null,
    }
    try {
      if (editingId) {
        await update.mutateAsync({ id: editingId, payload })
        toast.success('Resource updated')
      } else {
        await create.mutateAsync(payload)
        toast.success('Resource created')
      }
      setForm(emptyForm)
      setEditingId(null)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Save failed')
    }
  }

  if (resources.isLoading && !resources.data) return <Loading label="Loading resources…" />
  if (resources.isError) return <ErrorState title="Failed to load resources" onRetry={resources.refetch} />

  return (
    <div className="space-y-8">
      <header>
        <h1 className="font-display text-3xl text-ink">Resources</h1>
        <p className="mt-2 text-sm text-ink-muted">Curate tools and learning links.</p>
      </header>

      <form onSubmit={onSubmit} className="grid gap-3 rounded-2xl border border-border bg-white p-5 sm:grid-cols-2">
        <input
          required
          value={form.title}
          onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
          placeholder="Title"
          className="rounded-lg border border-border px-3 py-2 text-sm"
        />
        <input
          required
          value={form.url}
          onChange={(e) => setForm((f) => ({ ...f, url: e.target.value }))}
          placeholder="https://…"
          className="rounded-lg border border-border px-3 py-2 text-sm"
        />
        <select
          value={form.type}
          onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))}
          className="rounded-lg border border-border px-3 py-2 text-sm"
        >
          <option value="tool">Tool</option>
          <option value="article">Article</option>
          <option value="video">Video</option>
          <option value="community">Community</option>
        </select>
        <select
          value={form.category_id}
          onChange={(e) => setForm((f) => ({ ...f, category_id: e.target.value }))}
          className="rounded-lg border border-border px-3 py-2 text-sm"
        >
          <option value="">No category</option>
          {(categories.data?.items || []).map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <input
          value={form.thumbnail}
          onChange={(e) => setForm((f) => ({ ...f, thumbnail: e.target.value }))}
          placeholder="Thumbnail URL"
          className="rounded-lg border border-border px-3 py-2 text-sm sm:col-span-2"
        />
        <textarea
          value={form.description}
          onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          placeholder="Description"
          className="min-h-24 rounded-lg border border-border px-3 py-2 text-sm sm:col-span-2"
        />
        <label className="flex items-center gap-2 text-sm text-ink-muted">
          <input
            type="checkbox"
            checked={form.is_featured}
            onChange={(e) => setForm((f) => ({ ...f, is_featured: e.target.checked }))}
          />
          Featured
        </label>
        <div className="flex gap-2">
          <button type="submit" className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white">
            {editingId ? 'Update resource' : 'Create resource'}
          </button>
          {editingId ? (
            <button
              type="button"
              onClick={() => {
                setEditingId(null)
                setForm(emptyForm)
              }}
              className="rounded-lg border border-border px-4 py-2 text-sm"
            >
              Cancel
            </button>
          ) : null}
        </div>
      </form>

      {!resources.data?.items?.length ? (
        <EmptyState title="No resources" />
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-border bg-white">
          <table className="w-full min-w-[680px] text-left text-sm">
            <thead className="border-b border-border bg-surface text-ink-muted">
              <tr>
                <th className="px-4 py-3 font-medium">Title</th>
                <th className="px-4 py-3 font-medium">Type</th>
                <th className="px-4 py-3 font-medium">Featured</th>
                <th className="px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {resources.data.items.map((resource) => (
                <tr key={resource.id} className="border-b border-border/70">
                  <td className="px-4 py-3">
                    <p className="font-medium text-ink">{resource.title}</p>
                    <p className="text-xs text-ink-muted">{resource.category?.name || 'Uncategorized'}</p>
                  </td>
                  <td className="px-4 py-3 capitalize text-ink-muted">{resource.type}</td>
                  <td className="px-4 py-3 text-ink-muted">{resource.is_featured ? 'Yes' : 'No'}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button
                        type="button"
                        className="text-accent hover:underline"
                        onClick={() => {
                          setEditingId(resource.id)
                          setForm({
                            title: resource.title,
                            url: resource.url,
                            description: resource.description || '',
                            type: resource.type,
                            category_id: resource.category_id ? String(resource.category_id) : '',
                            is_featured: resource.is_featured,
                            thumbnail: resource.thumbnail || '',
                          })
                        }}
                      >
                        Edit
                      </button>
                      <button type="button" className="text-danger hover:underline" onClick={() => setDeleteId(resource.id)}>
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

      {(resources.data?.pages || 1) > 1 ? (
        <div className="flex items-center gap-3">
          <button type="button" disabled={page <= 1} onClick={() => setPage((p) => p - 1)} className="rounded-lg border border-border px-3 py-1.5 text-sm disabled:opacity-40">
            Prev
          </button>
          <span className="text-sm text-ink-muted">
            Page {page}/{resources.data.pages}
          </span>
          <button
            type="button"
            disabled={page >= resources.data.pages}
            onClick={() => setPage((p) => p + 1)}
            className="rounded-lg border border-border px-3 py-1.5 text-sm disabled:opacity-40"
          >
            Next
          </button>
        </div>
      ) : null}

      <ConfirmDialog
        open={Boolean(deleteId)}
        title="Delete resource?"
        loading={remove.isPending}
        onCancel={() => setDeleteId(null)}
        onConfirm={async () => {
          try {
            await remove.mutateAsync(deleteId)
            toast.success('Resource deleted')
            setDeleteId(null)
          } catch (err) {
            toast.error(err.response?.data?.detail || 'Delete failed')
          }
        }}
      />
    </div>
  )
}
