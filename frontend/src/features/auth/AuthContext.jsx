import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import apiClient from '@/shared/api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }, [])

  const refreshUser = useCallback(async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setUser(null)
      setIsLoading(false)
      return
    }

    try {
      const { data } = await apiClient.get('/auth/me')
      setUser(data)
    } catch {
      logout()
    } finally {
      setIsLoading(false)
    }
  }, [logout])

  useEffect(() => {
    refreshUser()
  }, [refreshUser])

  const login = useCallback(async (email, password) => {
    const { data } = await apiClient.post('/auth/login', { email, password })
    localStorage.setItem('access_token', data.access_token)
    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token)
    }
    await refreshUser()
    return data
  }, [refreshUser])

  const register = useCallback(async (payload) => {
    const { data } = await apiClient.post('/auth/register', payload)
    return data
  }, [])

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      register,
      logout,
      refreshUser,
    }),
    [user, isLoading, login, register, logout, refreshUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}
