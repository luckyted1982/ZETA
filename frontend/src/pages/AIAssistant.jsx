import React, { useState, useEffect, useRef } from 'react'
import {
  Send, Upload, FileText, Download, Import, CheckCircle,
  User, Bot, BarChart3, Plus
} from 'lucide-react'
import {
  sendChatStream, getConversations, getConversation,
  uploadDocument, extractScores, exportReport, submitEvaluation
} from '../services/api'

const dimensionMap = {
  rd_innovation: '研发创新能力',
  ip_protection: '知识产权实力',
  qualification_progress: '资质培育进度',
  financing_valuation: '融资与估值能力',
  legal_governance: '法律治理合规',
  financial_tax: '财务税务能力',
  ipo_readiness: '上市准备度',
  talent_resources: '人才资源',
}

const dimensionKeys = Object.keys(dimensionMap)

function AIAssistant() {
  const [conversations, setConversations] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [streamingReply, setStreamingReply] = useState('')
  const [report, setReport] = useState('')
  const [extractedScores, setExtractedScores] = useState(null)
  const [scores, setScores] = useState({})
  const [uploading, setUploading] = useState(false)
  const [generatingReport, setGeneratingReport] = useState(false)
  const [mobileTab, setMobileTab] = useState('chat')
  const [rightTab, setRightTab] = useState('report')
  const streamingReplyRef = useRef('')
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)

  useEffect(() => { loadConversations() }, [])
  useEffect(() => { if (sessionId) loadConversation(sessionId) }, [sessionId])
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, streamingReply])

  const loadConversations = async () => {
    try { const data = await getConversations(); setConversations(data?.items || []) } catch (e) {}
  }

  const loadConversation = async (id) => {
    try {
      const data = await getConversation(id)
      if (data?.messages) setMessages(data.messages)
      if (data?.report) setReport(data.report)
      if (data?.extracted_scores) setExtractedScores(data.extracted_scores)
    } catch (e) {}
  }

  const startStream = async (msg, onDone) => {
    setIsLoading(true)
    setStreamingReply('')
    streamingReplyRef.current = ''
    try {
      await sendChatStream(
        sessionId,
        msg,
        null,
        (chunk) => {
          streamingReplyRef.current += chunk
          setStreamingReply(streamingReplyRef.current)
        },
        (done) => {
          setIsLoading(false)
          onDone?.(done)
          setMessages(prev => [...prev, { role: 'assistant', content: streamingReplyRef.current }])
          setStreamingReply('')
          streamingReplyRef.current = ''
        },
        (err) => { setIsLoading(false); console.error(err) }
      )
    } catch (e) { setIsLoading(false) }
  }

  const handleSend = async () => {
    if (!input.trim()) return
    const text = input.trim()
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setInput('')
    await startStream(text, (done) => {
      if (done?.extracted_scores) setExtractedScores(done.extracted_scores)
    })
  }

  const handleGenerateReport = async () => {
    setGeneratingReport(true)
    await startStream('请生成调研报告', (done) => {
      setGeneratingReport(false)
      setReport(streamingReplyRef.current)
      if (done?.extracted_scores) setExtractedScores(done.extracted_scores)
    })
    setGeneratingReport(false)
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setUploading(true)
    try {
      const result = await uploadDocument(file, sessionId)
      setMessages(prev => [...prev, { role: 'system', content: `已上传文件：${result.filename}` }])
      if (result.extracted_scores) {
        setExtractedScores(result.extracted_scores)
        setReport(result.analysis || '')
      }
    } catch (e) { alert('上传失败：' + e.message) }
    finally { setUploading(false); e.target.value = '' }
  }

  const handleExtractScores = async () => {
    if (!sessionId) return
    try {
      const data = await extractScores(sessionId)
      if (data?.scores) setExtractedScores(data.scores)
    } catch (e) { alert('提取失败: ' + e.message) }
  }

  const handleImportScores = () => {
    if (extractedScores) setScores({ ...extractedScores })
  }

  const handleScoreChange = (key, value) => {
    setScores(prev => ({ ...prev, [key]: Number(value) || 0 }))
  }

  const handleSubmitEvaluation = async () => {
    try {
      await submitEvaluation({ session_id: sessionId, scores })
      alert('评测提交成功！')
    } catch (e) { alert('提交失败: ' + e.message) }
  }

  const handleExport = async (format) => {
    if (!sessionId) return
    try { await exportReport(sessionId, format) } catch (e) { alert('导出失败') }
  }

  const newSession = () => {
    setSessionId(null)
    setMessages([])
    setReport('')
    setExtractedScores(null)
    setScores({})
    setMobileTab('chat')
  }

  const renderMessage = (msg, idx) => {
    const isUser = msg.role === 'user'
    const isSystem = msg.role === 'system'
    return (
      <div key={idx} className={`flex gap-3 mb-4 ${isUser ? 'justify-end' : ''}`}>
        {!isUser && (
          <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isSystem ? 'bg-gray-100' : 'bg-primary/10'}`}>
            {isSystem ? <FileText className="w-4 h-4 text-gray-500" /> : <Bot className="w-4 h-4 text-primary" />}
          </div>
        )}
        <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${isUser ? 'bg-primary text-white' : isSystem ? 'bg-gray-100 text-gray-600' : 'bg-gray-50 text-gray-800'}`}>
          {msg.content}
        </div>
        {isUser && (
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
            <User className="w-4 h-4 text-white" />
          </div>
        )}
      </div>
    )
  }

  const mobileTabs = (
    <div className="md:hidden flex gap-2 bg-white rounded-xl p-1 border border-gray-200 mb-4">
      <button onClick={() => setMobileTab('list')} className={`flex-1 px-3 py-2 rounded-lg text-sm ${mobileTab === 'list' ? 'bg-primary text-white' : 'text-gray-600'}`}>会话</button>
      <button onClick={() => setMobileTab('chat')} className={`flex-1 px-3 py-2 rounded-lg text-sm ${mobileTab === 'chat' ? 'bg-primary text-white' : 'text-gray-600'}`}>对话</button>
      <button onClick={() => setMobileTab('report')} className={`flex-1 px-3 py-2 rounded-lg text-sm ${mobileTab === 'report' ? 'bg-primary text-white' : 'text-gray-600'}`}>报告</button>
    </div>
  )

  return (
    <div>
      <div className="mb-4 md:mb-6">
        <h2 className="text-2xl font-bold text-gray-800">AI评测助手</h2>
        <p className="text-gray-500 mt-1">AI智能对话生成调研报告，自动提取评分并导入评测</p>
      </div>

      {mobileTabs}

      <div className="flex gap-4 h-[calc(100vh-220px)] min-h-[500px]">
        {/* 左侧会话列表 */}
        <div className={`${mobileTab === 'list' ? 'flex' : 'hidden'} md:flex w-full md:w-[20%] bg-white rounded-2xl border border-gray-100 flex-col`}>
          <div className="p-4 border-b border-gray-100 flex items-center justify-between">
            <h3 className="font-semibold text-gray-800">对话历史</h3>
            <button onClick={newSession} className="text-sm text-primary hover:underline flex items-center gap-1">
              <Plus className="w-3 h-3" /> 新建
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {conversations.map(c => (
              <button key={c.id} onClick={() => { setSessionId(c.id); setMobileTab('chat') }}
                className={`w-full text-left px-3 py-2 rounded-xl text-sm transition-all ${sessionId === c.id ? 'bg-primary/10 text-primary font-medium' : 'text-gray-600 hover:bg-gray-50'}`}>
                <div className="truncate">{c.title || `会话 ${c.id}`}</div>
                <div className="text-xs text-gray-400 mt-0.5">{c.updated_at?.slice(0, 10)}</div>
              </button>
            ))}
            {conversations.length === 0 && <p className="text-sm text-gray-400 text-center py-8">暂无会话</p>}
          </div>
        </div>

        {/* 中间对话区 */}
        <div className={`${mobileTab === 'chat' ? 'flex' : 'hidden'} md:flex w-full md:w-[50%] bg-white rounded-2xl border border-gray-100 flex-col`}>
          <div className="flex-1 overflow-y-auto p-4">
            {messages.length === 0 && !streamingReply && (
              <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <Bot className="w-12 h-12 mb-3 text-primary/30" />
                <p>开始对话或上传文件</p>
                <p className="text-sm mt-1">AI将自动分析并生成调研报告</p>
              </div>
            )}
            {messages.map((msg, idx) => renderMessage(msg, idx))}
            {streamingReply && renderMessage({ role: 'assistant', content: streamingReply }, 'stream')}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-4 border-t border-gray-100">
            <div className="flex gap-2 mb-3">
              <button onClick={() => fileInputRef.current?.click()} disabled={uploading}
                className="px-3 py-2 bg-gray-100 rounded-lg text-sm text-gray-600 hover:bg-gray-200 disabled:opacity-50 flex items-center gap-2">
                <Upload className="w-4 h-4" /> {uploading ? '上传中...' : '上传文件'}
              </button>
              <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" />
              <button onClick={handleGenerateReport} disabled={generatingReport || isLoading}
                className="px-3 py-2 bg-primary/10 rounded-lg text-sm text-primary hover:bg-primary/20 disabled:opacity-50 flex items-center gap-2">
                <FileText className="w-4 h-4" /> {generatingReport ? '生成中...' : '生成调研报告'}
              </button>
            </div>
            <div className="flex gap-2">
              <input type="text" value={input} onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                placeholder="输入消息..."
                className="flex-1 px-4 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/20 text-sm" />
              <button onClick={handleSend} disabled={isLoading || !input.trim()}
                className="px-4 py-2.5 bg-primary text-white rounded-xl hover:bg-secondary disabled:opacity-50">
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* 右侧报告/评分区 */}
        <div className={`${mobileTab === 'report' ? 'flex' : 'hidden'} md:flex w-full md:w-[30%] bg-white rounded-2xl border border-gray-100 flex-col overflow-hidden`}>
          <div className="flex border-b border-gray-100">
            <button onClick={() => setRightTab('report')} className={`flex-1 py-3 text-sm font-medium ${rightTab === 'report' ? 'text-primary border-b-2 border-primary' : 'text-gray-500'}`}>报告预览</button>
            <button onClick={() => setRightTab('scores')} className={`flex-1 py-3 text-sm font-medium ${rightTab === 'scores' ? 'text-primary border-b-2 border-primary' : 'text-gray-500'}`}>评分导入</button>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {rightTab === 'scores' ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-800">8维度评分</h3>
                  <div className="flex gap-2">
                    <button onClick={handleExtractScores} className="text-xs px-2 py-1 bg-primary/10 text-primary rounded-lg hover:bg-primary/20">提取</button>
                    <button onClick={handleImportScores} disabled={!extractedScores}
                      className="text-xs px-2 py-1 bg-primary text-white rounded-lg hover:bg-secondary disabled:opacity-50 flex items-center gap-1">
                      <Import className="w-3 h-3" /> 导入
                    </button>
                  </div>
                </div>
                {dimensionKeys.map(key => (
                  <div key={key} className="flex items-center gap-3">
                    <label className="text-sm text-gray-700 flex-1">{dimensionMap[key]}</label>
                    <input type="number" min="0" max="100" value={scores[key] || ''}
                      onChange={e => handleScoreChange(key, e.target.value)}
                      className="w-16 px-2 py-1.5 rounded-lg border border-gray-200 text-sm text-center focus:outline-none focus:ring-2 focus:ring-primary/20" />
                  </div>
                ))}
                <button onClick={handleSubmitEvaluation}
                  className="w-full py-2.5 bg-primary text-white rounded-xl text-sm font-medium hover:bg-secondary flex items-center justify-center gap-2">
                  <CheckCircle className="w-4 h-4" /> 确认提交评测
                </button>
              </div>
            ) : (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <button onClick={() => handleExport('pdf')} className="text-xs px-2 py-1 bg-gray-100 rounded-lg text-gray-600 hover:bg-gray-200 flex items-center gap-1">
                    <Download className="w-3 h-3" /> PDF
                  </button>
                  <button onClick={() => handleExport('docx')} className="text-xs px-2 py-1 bg-gray-100 rounded-lg text-gray-600 hover:bg-gray-200 flex items-center gap-1">
                    <Download className="w-3 h-3" /> Word
                  </button>
                </div>
                {report ? (
                  <div className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 rounded-xl p-4">{report}</div>
                ) : (
                  <div className="text-center text-gray-400 py-12">
                    <BarChart3 className="w-10 h-10 mx-auto mb-2 text-primary/30" />
                    <p>暂无报告</p>
                    <p className="text-xs mt-1">生成调研报告后预览</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default AIAssistant
