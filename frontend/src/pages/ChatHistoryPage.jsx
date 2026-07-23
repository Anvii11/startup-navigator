import { useState } from 'react'
import toast from 'react-hot-toast'
import { PageShell } from '@/shared/ui/PageShell'
import { EmptyState } from '@/shared/ui/EmptyState'
import { Skeleton } from '@/shared/ui/Skeleton'
import { useUserChatSessions, useDeleteChatSessionMutation } from '@/features/content/hooks'

export default function ChatHistoryPage() {
  const sessionsQuery = useUserChatSessions()
  const deleteMutation = useDeleteChatSessionMutation()
  const [selectedSession, setSelectedSession] = useState(null)

  const sessions = sessionsQuery.data || []

  const handleDelete = (sessionId) => {
    deleteMutation.mutate(sessionId, {
      onSuccess: () => {
        toast.success('Chat history item deleted')
        if (selectedSession?.id === sessionId) {
          setSelectedSession(null)
        }
      },
      onError: () => toast.error('Could not delete history item'),
    })
  }

  return (
    <PageShell
      title="Chat History"
      description="View and manage your previous AI search queries and generated startup blueprints."
    >
      <div className="space-y-6">
        {sessionsQuery.isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-20 w-full rounded-2xl" />
            ))}
          </div>
        ) : sessions.length === 0 ? (
          <EmptyState
            title="No search history yet"
            message="Queries asked using the AI Search assistant will appear here automatically."
          />
        ) : (
          <div className="grid gap-4">
            {sessions.map((session) => {
              const formattedDate = new Date(session.updated_at || session.created_at).toLocaleString(undefined, {
                dateStyle: 'medium',
                timeStyle: 'short',
              })

              const messages = session.messages || []
              const assistantMsg = messages.find((m) => m.role === 'assistant')
              const userMsg = messages.find((m) => m.role === 'user')

              return (
                <div
                  key={session.id}
                  className="rounded-2xl border border-border bg-white p-5 space-y-3 shadow-xs hover:border-accent/40 transition"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/50 pb-3">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-base">🤖</span>
                        <h3 className="font-display text-base font-bold text-ink">
                          {session.title || userMsg?.content || 'AI Search Query'}
                        </h3>
                      </div>
                      <p className="text-xs text-ink-muted">Asked on {formattedDate}</p>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => setSelectedSession(selectedSession?.id === session.id ? null : session)}
                        className="rounded-xl bg-accent-soft px-3.5 py-1.5 text-xs font-semibold text-accent hover:bg-accent hover:text-white transition"
                      >
                        {selectedSession?.id === session.id ? 'Close View' : 'View Conversation'}
                      </button>

                      <button
                        type="button"
                        onClick={() => handleDelete(session.id)}
                        className="rounded-xl border border-rose-200 bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-700 hover:bg-rose-100 transition"
                      >
                        Delete
                      </button>
                    </div>
                  </div>

                  {/* Expanded Conversation View */}
                  {selectedSession?.id === session.id ? (
                    <div className="rounded-xl bg-slate-50 p-4 space-y-4 text-xs border border-slate-200">
                      {userMsg ? (
                        <div className="space-y-1">
                          <span className="font-bold text-slate-500 uppercase text-[10px]">Your Question</span>
                          <p className="font-semibold text-ink bg-white p-3 rounded-lg border border-slate-200">
                            {userMsg.content}
                          </p>
                        </div>
                      ) : null}

                      {assistantMsg ? (
                        <div className="space-y-1">
                          <span className="font-bold text-accent uppercase text-[10px]">AI Response & Sources</span>
                          <div className="bg-white p-4 rounded-lg border border-slate-200 space-y-3 whitespace-pre-wrap leading-relaxed text-ink-muted">
                            {assistantMsg.content}
                          </div>
                        </div>
                      ) : (
                        <p className="text-slate-500 italic">No response details available.</p>
                      )}
                    </div>
                  ) : null}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </PageShell>
  )
}
