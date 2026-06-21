import React from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import { LayoutDashboard, MessageSquare, Building2, BookOpen, ClipboardList, Sparkles } from 'lucide-react'

function Dashboard() {
  const navItems = [
    { to: '/', label: '评测中心', icon: LayoutDashboard },
    { to: '/ai-assistant', label: 'AI评测助手', icon: MessageSquare },
    { to: '/companies', label: '企业库', icon: Building2 },
    { to: '/knowledge', label: '知识库', icon: BookOpen },
    { to: '/standards', label: '评测标准', icon: ClipboardList },
  ]

  return (
    <div className="min-h-screen flex bg-background">
      {/* 侧边栏 */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col fixed h-full z-30">
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-gray-800">AI科创评测</h1>
              <p className="text-xs text-gray-400">工作台</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                  isActive
                    ? 'bg-primary/10 text-primary font-medium'
                    : 'text-gray-600 hover:bg-gray-50'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-100">
          <div className="bg-gradient-to-br from-primary/5 to-secondary/5 rounded-xl p-4">
            <p className="text-sm font-medium text-gray-700">AI赋能评测</p>
            <p className="text-xs text-gray-500 mt-1">基于8维度55指标</p>
          </div>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 ml-64 p-8">
        <Outlet />
      </main>
    </div>
  )
}

export default Dashboard
