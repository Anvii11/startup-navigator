import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from './api'
import { useAuth } from '@/features/auth/AuthContext'

export function useCategories(params = {}) {
  return useQuery({
    queryKey: ['categories', params],
    queryFn: () => api.fetchCategories(params),
  })
}

export function useArticles(params = {}, options = {}) {
  return useQuery({
    queryKey: ['articles', params],
    queryFn: () => api.fetchArticles(params),
    ...options,
  })
}

export function useArticle(slug, options = {}) {
  return useQuery({
    queryKey: ['article', slug],
    queryFn: () => api.fetchArticle(slug),
    enabled: Boolean(slug),
    ...options,
  })
}

export function useRelatedArticles(slug) {
  return useQuery({
    queryKey: ['articles', 'related', slug],
    queryFn: () => api.fetchRelatedArticles(slug),
    enabled: Boolean(slug),
  })
}

export function useResources(params = {}) {
  return useQuery({
    queryKey: ['resources', params],
    queryFn: () => api.fetchResources(params),
  })
}

// User Saved Ideas & Dashboard Hooks
export function useUserSavedIdeas() {
  const { isAuthenticated } = useAuth()
  return useQuery({
    queryKey: ['user', 'saved-ideas'],
    queryFn: api.fetchUserSavedIdeas,
    enabled: isAuthenticated,
  })
}

export function useUserSavedIdeaIds() {
  const { isAuthenticated } = useAuth()
  return useQuery({
    queryKey: ['user', 'saved-idea-ids'],
    queryFn: api.fetchUserSavedIdeaIds,
    enabled: isAuthenticated,
  })
}

export function useUserDashboard() {
  const { isAuthenticated } = useAuth()
  return useQuery({
    queryKey: ['user', 'dashboard'],
    queryFn: api.fetchUserDashboard,
    enabled: isAuthenticated,
  })
}

export function useUserChatSessions() {
  const { isAuthenticated } = useAuth()
  return useQuery({
    queryKey: ['user', 'chat-sessions'],
    queryFn: api.fetchUserChatSessions,
    enabled: isAuthenticated,
  })
}

export function useSaveIdeaMutation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (articleId) => api.saveUserIdea(articleId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['user', 'saved-ideas'] })
      qc.invalidateQueries({ queryKey: ['user', 'saved-idea-ids'] })
      qc.invalidateQueries({ queryKey: ['user', 'dashboard'] })
    },
  })
}

export function useRemoveSavedIdeaMutation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (articleId) => api.removeUserSavedIdea(articleId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['user', 'saved-ideas'] })
      qc.invalidateQueries({ queryKey: ['user', 'saved-idea-ids'] })
      qc.invalidateQueries({ queryKey: ['user', 'dashboard'] })
    },
  })
}

export function useDeleteChatSessionMutation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (sessionId) => api.deleteUserChatSession(sessionId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['user', 'chat-sessions'] })
      qc.invalidateQueries({ queryKey: ['user', 'dashboard'] })
    },
  })
}

// Admin Hooks
export function useAdminCategories(params = {}) {
  return useQuery({
    queryKey: ['admin', 'categories', params],
    queryFn: () => api.adminFetchCategories(params),
  })
}

export function useAdminArticles(params = {}) {
  return useQuery({
    queryKey: ['admin', 'articles', params],
    queryFn: () => api.adminFetchArticles(params),
  })
}

export function useAdminResources(params = {}) {
  return useQuery({
    queryKey: ['admin', 'resources', params],
    queryFn: () => api.adminFetchResources(params),
  })
}

export function useInvalidateContent() {
  const qc = useQueryClient()
  return () => {
    qc.invalidateQueries({ queryKey: ['categories'] })
    qc.invalidateQueries({ queryKey: ['articles'] })
    qc.invalidateQueries({ queryKey: ['resources'] })
    qc.invalidateQueries({ queryKey: ['admin'] })
    qc.invalidateQueries({ queryKey: ['user'] })
  }
}

export function useAdminCategoryMutations() {
  const invalidate = useInvalidateContent()
  const create = useMutation({ mutationFn: api.adminCreateCategory, onSuccess: invalidate })
  const update = useMutation({
    mutationFn: ({ id, payload }) => api.adminUpdateCategory(id, payload),
    onSuccess: invalidate,
  })
  const remove = useMutation({ mutationFn: api.adminDeleteCategory, onSuccess: invalidate })
  return { create, update, remove }
}

export function useAdminArticleMutations() {
  const invalidate = useInvalidateContent()
  const create = useMutation({ mutationFn: api.adminCreateArticle, onSuccess: invalidate })
  const update = useMutation({
    mutationFn: ({ id, payload }) => api.adminUpdateArticle(id, payload),
    onSuccess: invalidate,
  })
  const remove = useMutation({ mutationFn: api.adminDeleteArticle, onSuccess: invalidate })
  return { create, update, remove }
}

export function useAdminResourceMutations() {
  const invalidate = useInvalidateContent()
  const create = useMutation({ mutationFn: api.adminCreateResource, onSuccess: invalidate })
  const update = useMutation({
    mutationFn: ({ id, payload }) => api.adminUpdateResource(id, payload),
    onSuccess: invalidate,
  })
  const remove = useMutation({ mutationFn: api.adminDeleteResource, onSuccess: invalidate })
  return { create, update, remove }
}
