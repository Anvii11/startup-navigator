export function Skeleton({ className = '' }) {
  return (
    <div
      className={`animate-pulse rounded-xl bg-border/60 ${className}`}
      aria-hidden
    />
  )
}

export function ArticleCardSkeleton() {
  return (
    <div className="overflow-hidden rounded-2xl border border-border bg-white">
      <Skeleton className="aspect-[16/9] rounded-none" />
      <div className="space-y-3 p-4">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-5 w-4/5" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-2/3" />
      </div>
    </div>
  )
}
