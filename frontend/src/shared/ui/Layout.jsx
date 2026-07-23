import { Outlet } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Navbar } from './Navbar'
import { Footer } from './Footer'
import { Sidebar } from './Sidebar'
import { theme } from '@/shared/lib/theme'

export function MainLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <motion.main
        className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={theme.motion.page}
      >
        <Outlet />
      </motion.main>
      <Footer />
    </div>
  )
}

export function DashboardLayout({ sidebarItems }) {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <div className="mx-auto flex w-full max-w-6xl flex-1">
        <Sidebar items={sidebarItems} />
        <motion.main
          className="flex-1 px-4 py-8 sm:px-6"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={theme.motion.page}
        >
          <Outlet />
        </motion.main>
      </div>
      <Footer />
    </div>
  )
}
