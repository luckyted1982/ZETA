import React, { useState, useEffect } from 'react'
import { Plus, Search, Trash2, Eye, RefreshCw, Building2 } from 'lucide-react'
import { getCompanies, deleteCompany, getCompanyEvaluations } from '../services/api'

function CompanyLibrary() {
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedCompany, setSelectedCompany] = useState(null)
  const [evaluations, setEvaluations] = useState([])

  useEffect(() => { loadCompanies() }, [search])

  const loadCompanies = async () => {
    setLoading(true)
    try {
      const data = await getCompanies({ keyword: search })
      setCompanies(data?.items || [])
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('确定删除该企业？')) return
    try { await deleteCompany(id); loadCompanies() } catch (e) { alert('删除失败') }
  }

  const handleView = async (company) => {
    setSelectedCompany(company)
    try {
      const data = await getCompanyEvaluations(company.id)
      setEvaluations(data?.items || [])
    } catch (e) { console.error(e) }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">企业库</h2>
          <p className="text-gray-500 mt-1">管理已评测企业，支持历史记录查看和再次评测</p>
        </div>
      </div>

      <div className="flex gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="搜索企业名称..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/20"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {companies.map(c => (
          <div key={c.id} className="bg-white rounded-2xl p-5 shadow-card border border-gray-100 hover:shadow-lg transition-all cursor-pointer" onClick={() => handleView(c)}>
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  <Building2 className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">{c.name}</h3>
                  <p className="text-sm text-gray-500">{c.industry} | {c.stage}</p>
                </div>
              </div>
              <button onClick={(e) => { e.stopPropagation(); handleDelete(c.id) }} className="text-gray-400 hover:text-red-500">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
            <div className="mt-4 flex gap-4 text-sm">
              <span className="text-gray-500">评测次数: <span className="font-medium text-gray-800">{c.evaluation_count || 0}</span></span>
              {c.latest_score && <span className="text-gray-500">最新得分: <span className="font-medium text-primary">{c.latest_score}</span></span>}
            </div>
          </div>
        ))}
      </div>

      {selectedCompany && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setSelectedCompany(null)}>
          <div className="bg-white rounded-2xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
            <h3 className="text-xl font-bold text-gray-800">{selectedCompany.name}</h3>
            <p className="text-gray-500 mt-1">{selectedCompany.industry} | {selectedCompany.stage}</p>
            <h4 className="font-semibold text-gray-700 mt-6 mb-3">评测历史</h4>
            {evaluations.length === 0 ? <p className="text-gray-400">暂无评测记录</p> : (
              <div className="space-y-3">
                {evaluations.map((e, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                    <div>
                      <span className="font-medium text-gray-800">{e.evaluation_date?.slice(0, 10)}</span>
                      <span className="text-gray-400 text-sm ml-2">{e.evaluator || '系统评测'}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-bold text-primary">{e.total_score}</span>
                      <span className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-lg font-medium">{e.overall_grade}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default CompanyLibrary
