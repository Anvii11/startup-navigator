export function ErrorState({
  title = 'Something went wrong',
  message = 'Please try again in a moment.',
  onRetry,
}) {
  return (
    <div
      className="mx-auto flex max-w-md flex-col items-center gap-4 px-4 py-16 text-center"
      role="alert"
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-50 text-danger">
        !
      </div>
      <div>
        <h2 className="font-display text-xl text-ink">{title}</h2>
        <p className="mt-2 text-sm text-ink-muted">{message}</p>
      </div>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition hover:bg-accent-hover"
        >
          Try again
        </button>
      ) : null}
    </div>
  )
}
