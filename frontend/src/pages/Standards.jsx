import React, { useState, useEffect } from 'react'
import { Search, HelpCircle, ChevronRight, BookOpen } from 'lucide-react'
import { getStandards, getDimensionsSummary, explainStandard } from '../services/api'

function Standards() {
  const [standards, setStandards] = useState([])
  const [dimensions, setDimensions] = useState([])
  const [search, setSearch] = useState('')
  const [selectedDimension, setSelectedDimension] = useState('')
  const [loading, setLoading] = useState(true)
  const [explaining, setExplaining] = useState(null)
  const [explanation, setExplanation] = useState(null)

  useEffect(() => { loadStandards(); loadDimensions() }, [search, selectedDimension])

  const loadStandards = async () => {
    setLoading(true)
    try {
      const params = {}
      if (selectedDimension) params.dimension_id = selectedDimension
      if (search) params.keyword = search
      const data = await getStandards(params)
      setStandards(data?.items || [])
    } catch (e) {}
    setLoading(false)
  }

  const loadDimensions = async () => {
    try { const data = await getDimensionsSummary(); setDimensions(data?.dimensions || []) } catch (e) {}
  }

  const handleExplain = async (id) => {
    setExplaining(id)
    try {
      const data = await explainStandard(id)
      setExplanation({ id, text: data?.explanation || '暂无解释' })
    } catch (e) { setExplanation({ id, text: '生成失败' }) }
    setExplaining(null)
  }

  const dimNames = {
    rd_innovation: '研发创新', ip_protection: '知识产权', qualification_progress: '资质培育',
    financing_valuation: '融资估值', legal_governance: '法律治理', financial_tax: '财务税务',
    ipo_readiness: '上市准备', talent_resources: '人才资源'
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800">评测标准解释</h2>
        <p className="text-gray-500 mt-1">了解8维度55指标的详细评测标准，AI增强深度解读</p>
      </div>

      {/* 维度筛选 */}
      <div className="flex flex-wrap gap-2 mb-6">
        <button onClick={() => setSelectedDimension('')} className={`px-4 py-2 rounded-xl text-sm ${!selectedDimension ? 'bg-primary text-white' : 'bg-white border border-gray-200 text-gray-600'}`}>全部</button>
        {dimensions.map(d => (
          <button key={d.dimension_id} onClick={() => setSelectedDimension(d.dimension_id)}
            className={`px-4 py-2 rounded-xl text-sm ${selectedDimension === d.dimension_id ? 'bg-primary text-white' : 'bg-white border border-gray-200 text-gray-600'}`}>
            {dimNames[d.dimension_id] || d.dimension_id} ({d.indicator_count})
          </button>
        ))}
      </div>

      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input type="text" placeholder="搜索指标..." value={search} onChange={e => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/20" />
      </div>

      <div className="grid gap-4">
        {standards.map(s => (
          <div key={s.id} className="bg-white rounded-2xl p-5 shadow-card border border-gray-100">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-lg font-medium">{dimNames[s.dimension_id] || s.dimension_id}</span>
                  <h3 className="font-semibold text-gray-800">{s.name}</h3>
                  {s.importance_level === 'high' && <span className="px-2 py-0.5 bg-red-100 text-red-600 text-xs rounded">核心</span>}
                </div>
                <p className="text-sm text-gray-600 mb-2">{s.description}</p>
                <p className="text-sm text-gray-500 bg-gray-50 rounded-lg p-2">评分标准：{s.scoring_criteria}</p>
              </div>
              <button onClick={() => handleExplain(s.id)} disabled={explaining === s.id}
                className="ml-4 px-4 py-2 bg-primary/10 text-primary rounded-lg text-sm hover:bg-primary/20 disabled:opacity-50 flex items-center gap-2">
                <HelpCircle className="w-4 h-4" />
                {explaining === s.id ? '生成中...' : 'AI解读'}
              </button>
            </div>

            {explanation?.id === s.id && (
              <div className="mt-4 bg-gradient-to-br from-primary/5 to-secondary/5 rounded-xl p-4 border border-primary/10">
                <h4 className="font-medium text-gray-800 mb-2 flex items-center gap-2"><BookOpen className="w-4 h-4 text-primary" /> AI深度解读</h4>
                <div className="text-sm text-gray-700 whitespace-pre-wrap">{explanation.text}</div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default Standards
