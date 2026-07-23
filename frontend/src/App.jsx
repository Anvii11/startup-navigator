import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '@/features/auth/AuthContext'
import { AppRouter } from '@/app/router'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AppRouter />
        <Toaster
          position="top-right"
          toastOptions={{
            className: 'text-sm',
            style: {
              background: '#ffffff',
              color: '#0f1c18',
              border: '1px solid #d5e0db',
            },
          }}
        />
      </AuthProvider>
    </QueryClientProvider>
  )
}
