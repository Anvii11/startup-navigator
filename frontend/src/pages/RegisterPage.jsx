import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '@/features/auth/AuthContext'
import { PageShell } from '@/shared/ui/PageShell'

export default function RegisterPage() {
  const { register, login } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await register({ email: email.trim(), password, full_name: fullName.trim() })
      await login(email.trim(), password)
      toast.success('Account created')
      navigate('/dashboard', { replace: true })
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <PageShell title="Create account" description="Join Startup Navigator to save guides and ask the AI later.">
      <form onSubmit={onSubmit} className="mx-auto max-w-md space-y-4">
        <label className="block space-y-1.5 text-sm">
          <span className="font-medium text-ink">Full name</span>
          <input
            required
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="w-full rounded-lg border border-border px-3 py-2.5 outline-none ring-accent/30 focus:ring-2"
          />
        </label>
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
          {loading ? 'Creating…' : 'Create account'}
        </button>
        <p className="text-sm text-ink-muted">
          Already registered?{' '}
          <Link to="/login" className="font-medium text-accent hover:underline">
            Log in
          </Link>
        </p>
      </form>
    </PageShell>
  )
}
