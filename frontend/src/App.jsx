import React from 'react'
import { createHashRouter, RouterProvider } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import AIAssistant from './pages/AIAssistant'
import CompanyLibrary from './pages/CompanyLibrary'
import KnowledgeBase from './pages/KnowledgeBase'
import Standards from './pages/Standards'
import EvaluationPage from './components/EvaluationPage'

const router = createHashRouter([
  {
    element: <Dashboard />,
    children: [
      { path: '/', element: <EvaluationPage /> },
      { path: '/ai-assistant', element: <AIAssistant /> },
      { path: '/companies', element: <CompanyLibrary /> },
      { path: '/knowledge', element: <KnowledgeBase /> },
      { path: '/standards', element: <Standards /> },
    ],
  },
])

function App() {
  return <RouterProvider router={router} />
}

export default App
