import React, { useState, useEffect } from 'react'
import { Search, BookOpen, Send, Tag } from 'lucide-react'
import { getKnowledgeDocs, queryKnowledge, getKnowledgeCategories } from '../services/api'

function KnowledgeBase() {
  const [docs, setDocs] = useState([])
  const [categories, setCategories] = useState({})
  const [search, setSearch] = useState('')
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('browse') // browse | query

  useEffect(() => { loadDocs() }, [search])
  useEffect(() => { loadCategories() }, [])

  const loadDocs = async () => {
    try { const data = await getKnowledgeDocs({ keyword: search }); setDocs(data?.items || []) } catch (e) {}
  }

  const loadCategories = async () => {
    try { const data = await getKnowledgeCategories(); setCategories(data || {}) } catch (e) {}
  }

  const handleAsk = async () => {
    if (!question.trim()) return
    setLoading(true)
    try {
      const data = await queryKnowledge({ question })
      setAnswer(data?.answer || '暂无回答')
    } catch (e) { setAnswer('查询失败: ' + e.message) }
    setLoading(false)
  }

  const typeLabels = { law: '法律法规', policy: '政策文件', report: '行业报告', standard: '标准规范', whitepaper: '白皮书' }
  const typeColors = { law: 'bg-blue-100 text-blue-700', policy: 'bg-green-100 text-green-700', report: 'bg-purple-100 text-purple-700', standard: 'bg-orange-100 text-orange-700', whitepaper: 'bg-gray-100 text-gray-700' }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">知识库</h2>
          <p className="text-gray-500 mt-1">科技政策法规、行业研报、标准规范等知识文档</p>
        </div>
        <div className="flex gap-2 bg-white rounded-xl p-1 border border-gray-200">
          <button onClick={() => setActiveTab('browse')} className={`px-4 py-2 rounded-lg text-sm ${activeTab === 'browse' ? 'bg-primary text-white' : 'text-gray-600'}`}>浏览</button>
          <button onClick={() => setActiveTab('query')} className={`px-4 py-2 rounded-lg text-sm ${activeTab === 'query' ? 'bg-primary text-white' : 'text-gray-600'}`}>AI问答</button>
        </div>
      </div>

      {activeTab === 'browse' && (
        <>
          <div className="relative mb-6">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text" placeholder="搜索知识库..." value={search} onChange={e => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
          </div>
          <div className="grid gap-4">
            {docs.map(d => (
              <div key={d.id} className="bg-white rounded-2xl p-5 shadow-card border border-gray-100">
                <div className="flex items-center gap-3 mb-2">
                  <span className={`px-2 py-1 rounded-lg text-xs font-medium ${typeColors[d.doc_type] || 'bg-gray-100'}`}>{typeLabels[d.doc_type] || d.doc_type}</span>
                  <h3 className="font-semibold text-gray-800">{d.title}</h3>
                </div>
                <p className="text-sm text-gray-500">{d.category} {d.tags?.length > 0 && `| ${d.tags.join(', ')}`}</p>
              </div>
            ))}
          </div>
        </>
      )}

      {activeTab === 'query' && (
        <div className="bg-white rounded-2xl p-6 shadow-card border border-gray-100">
          <div className="flex gap-3 mb-4">
            <input
              type="text" placeholder="输入您的问题..." value={question} onChange={e => setQuestion(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleAsk()}
              className="flex-1 px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
            <button onClick={handleAsk} disabled={loading} className="px-6 py-3 bg-primary text-white rounded-xl hover:bg-secondary disabled:opacity-50">
              {loading ? '思考中...' : <Send className="w-4 h-4" />}
            </button>
          </div>
          {answer && (
            <div className="bg-gray-50 rounded-xl p-4 mt-4">
              <h4 className="font-medium text-gray-700 mb-2">AI回答</h4>
              <div className="text-gray-700 whitespace-pre-wrap">{answer}</div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default KnowledgeBase
