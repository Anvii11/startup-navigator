const styles = {
  beginner: 'bg-emerald-50 text-emerald-800',
  intermediate: 'bg-amber-50 text-amber-800',
  advanced: 'bg-rose-50 text-rose-800',
}

export function DifficultyBadge({ value }) {
  if (!value) return null
  return (
    <span
      className={`inline-flex rounded-md px-2 py-0.5 text-xs font-semibold capitalize ${styles[value] || 'bg-surface text-ink-muted'}`}
    >
      {value}
    </span>
  )
}
