export function Loading({ label = 'Loading…' }) {
  return (
    <div
      className="flex min-h-[40vh] flex-col items-center justify-center gap-3 text-ink-muted"
      role="status"
      aria-live="polite"
    >
      <div
        className="h-9 w-9 animate-spin rounded-full border-2 border-border border-t-accent"
        aria-hidden
      />
      <p className="text-sm font-medium">{label}</p>
    </div>
  )
}
