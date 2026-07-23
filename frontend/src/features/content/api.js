import apiClient from '@/shared/api/client'

export async function fetchCategories(params = {}) {
  const { data } = await apiClient.get('/categories', { params })
  return data
}

export async function fetchCategory(slug) {
  const { data } = await apiClient.get(`/categories/${slug}`)
  return data
}

export async function fetchArticles(params = {}) {
  const { data } = await apiClient.get('/articles', { params })
  return data
}

export async function fetchArticlesByCategory(slug, params = {}) {
  const { data } = await apiClient.get(`/categories/${slug}/articles`, { params })
  return data
}

export async function fetchArticle(slug) {
  const { data } = await apiClient.get(`/articles/${slug}`)
  return data
}

export async function fetchRelatedArticles(slug) {
  const { data } = await apiClient.get(`/articles/${slug}/related`)
  return data
}

export async function fetchResources(params = {}) {
  const { data } = await apiClient.get('/resources', { params })
  return data
}

// User Dashboard & Saved Ideas
export async function fetchUserSavedIdeas() {
  const { data } = await apiClient.get('/user/saved-ideas')
  return data
}

export async function fetchUserSavedIdeaIds() {
  const { data } = await apiClient.get('/user/saved-idea-ids')
  return data
}

export async function saveUserIdea(articleId) {
  const { data } = await apiClient.post(`/user/saved-ideas/${articleId}`)
  return data
}

export async function removeUserSavedIdea(articleId) {
  const { data } = await apiClient.delete(`/user/saved-ideas/${articleId}`)
  return data
}

export async function fetchUserDashboard() {
  const { data } = await apiClient.get('/user/dashboard')
  return data
}

export async function fetchUserChatSessions() {
  const { data } = await apiClient.get('/ai/sessions')
  return data
}

export async function deleteUserChatSession(sessionId) {
  const { data } = await apiClient.delete(`/ai/sessions/${sessionId}`)
  return data
}

// Admin
export async function adminFetchCategories(params = {}) {
  const { data } = await apiClient.get('/admin/categories', { params })
  return data
}

export async function adminCreateCategory(payload) {
  const { data } = await apiClient.post('/admin/categories', payload)
  return data
}

export async function adminUpdateCategory(id, payload) {
  const { data } = await apiClient.put(`/admin/categories/${id}`, payload)
  return data
}

export async function adminDeleteCategory(id) {
  await apiClient.delete(`/admin/categories/${id}`)
}

export async function adminFetchArticles(params = {}) {
  const { data } = await apiClient.get('/admin/articles', { params })
  return data
}

export async function adminFetchArticle(id) {
  const { data } = await apiClient.get(`/admin/articles/${id}`)
  return data
}

export async function adminCreateArticle(payload) {
  const { data } = await apiClient.post('/admin/articles', payload)
  return data
}

export async function adminUpdateArticle(id, payload) {
  const { data } = await apiClient.put(`/admin/articles/${id}`, payload)
  return data
}

export async function adminDeleteArticle(id) {
  await apiClient.delete(`/admin/articles/${id}`)
}

export async function adminFetchResources(params = {}) {
  const { data } = await apiClient.get('/admin/resources', { params })
  return data
}

export async function adminCreateResource(payload) {
  const { data } = await apiClient.post('/admin/resources', payload)
  return data
}

export async function adminUpdateResource(id, payload) {
  const { data } = await apiClient.put(`/admin/resources/${id}`, payload)
  return data
}

export async function adminDeleteResource(id) {
  await apiClient.delete(`/admin/resources/${id}`)
}
