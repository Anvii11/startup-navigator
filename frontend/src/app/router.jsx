import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { MainLayout, DashboardLayout } from '@/shared/ui/Layout'
import { ProtectedRoute } from '@/shared/ui/ProtectedRoute'
import {
  adminSidebarItems,
  dashboardSidebarItems,
} from '@/shared/ui/Sidebar'
import HomePage from '@/pages/HomePage'
import ExplorePage from '@/pages/ExplorePage'
import AISearchPage from '@/pages/AISearchPage'
import ResourcesPage from '@/pages/ResourcesPage'
import DashboardPage from '@/pages/DashboardPage'
import SavedIdeasPage from '@/pages/SavedIdeasPage'
import ChatHistoryPage from '@/pages/ChatHistoryPage'
import AboutPage from '@/pages/AboutPage'
import ContactPage from '@/pages/ContactPage'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'
import AdminDashboardPage from '@/pages/AdminDashboardPage'
import AdminArticlesPage from '@/pages/AdminArticlesPage'
import AdminCategoriesPage from '@/pages/AdminCategoriesPage'
import AdminResourcesPage from '@/pages/AdminResourcesPage'
import ArticleDetailPage from '@/pages/ArticleDetailPage'
import PlaceholderSectionPage from '@/pages/PlaceholderSectionPage'

function DashboardShell() {
  return <DashboardLayout sidebarItems={dashboardSidebarItems} />
}

function AdminShell() {
  return <DashboardLayout sidebarItems={adminSidebarItems} />
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route index element={<HomePage />} />
          <Route path="explore" element={<ExplorePage />} />
          <Route path="articles/:slug" element={<ArticleDetailPage />} />
          <Route path="search" element={<AISearchPage />} />
          <Route path="resources" element={<ResourcesPage />} />
          <Route path="about" element={<AboutPage />} />
          <Route path="contact" element={<ContactPage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route path="dashboard" element={<DashboardShell />}>
            <Route index element={<DashboardPage />} />
            <Route path="saved" element={<SavedIdeasPage />} />
            <Route path="chats" element={<ChatHistoryPage />} />
          </Route>
        </Route>

        <Route element={<ProtectedRoute roles={['admin']} />}>
          <Route path="admin" element={<AdminShell />}>
            <Route index element={<AdminDashboardPage />} />
            <Route path="articles" element={<AdminArticlesPage />} />
            <Route path="categories" element={<AdminCategoriesPage />} />
            <Route path="resources" element={<AdminResourcesPage />} />
            <Route
              path="users"
              element={
                <PlaceholderSectionPage
                  title="Users"
                  description="User management arrives in a later phase."
                />
              }
            />
            <Route
              path="logs"
              element={
                <PlaceholderSectionPage
                  title="Search logs"
                  description="User search logs arrive in a later phase."
                />
              }
            />
            <Route
              path="analytics"
              element={
                <PlaceholderSectionPage
                  title="Analytics"
                  description="Admin analytics arrive in a later phase."
                />
              }
            />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
