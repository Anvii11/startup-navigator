export function EmptyState({ title = 'Nothing here yet', message, action }) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-border bg-white/50 px-6 py-14 text-center">
      <h3 className="font-display text-lg text-ink">{title}</h3>
      {message ? <p className="max-w-md text-sm text-ink-muted">{message}</p> : null}
      {action}
    </div>
  )
}
