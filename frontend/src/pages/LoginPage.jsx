import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '@/features/auth/AuthContext'
import { PageShell } from '@/shared/ui/PageShell'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(email.trim(), password)
      toast.success('Welcome back')
      navigate(location.state?.from || '/dashboard', { replace: true })
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <PageShell title="Log in" description="Sign in to save ideas, view chat history, or manage content.">
      <form onSubmit={onSubmit} className="mx-auto max-w-md space-y-4">
        <label className="block space-y-1.5 text-sm">
          <span className="font-medium text-ink">Email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-border px-3 py-2.5 outline-none ring-accent/30 focus:ring-2"
          />
        </label>
        <label className="block space-y-1.5 text-sm">
          <span className="font-medium text-ink">Password</span>
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-border px-3 py-2.5 outline-none ring-accent/30 focus:ring-2"
          />
        </label>
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-accent px-4 py-2.5 text-sm font-semibold text-white hover:bg-accent-hover disabled:opacity-60"
        >
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
        <p className="text-sm text-ink-muted">
          No account?{' '}
          <Link to="/register" className="font-medium text-accent hover:underline">
            Register
          </Link>
        </p>
      </form>
    </PageShell>
  )
}
