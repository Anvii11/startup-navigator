import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@/features/auth/AuthContext'
import { Loading } from '@/shared/ui/Loading'

export function ProtectedRoute({ roles }) {
  const { isAuthenticated, user, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return <Loading label="Checking session…" />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  if (roles?.length && !roles.includes(user?.role)) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}
