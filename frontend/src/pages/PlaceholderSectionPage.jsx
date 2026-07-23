import { PageShell } from '@/shared/ui/PageShell'

export default function PlaceholderSectionPage({ title, description }) {
  return (
    <PageShell title={title} description={description}>
      <p className="text-sm text-ink-muted">Section placeholder — content arrives in a later phase.</p>
    </PageShell>
  )
}
