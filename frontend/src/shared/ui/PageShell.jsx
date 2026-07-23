export function PageShell({ title, description, children }) {
  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
          {title}
        </h1>
        {description ? <p className="max-w-2xl text-ink-muted">{description}</p> : null}
      </header>
      <div className="rounded-2xl border border-dashed border-border bg-white/60 p-6 sm:p-8">
        {children}
      </div>
    </section>
  )
}
