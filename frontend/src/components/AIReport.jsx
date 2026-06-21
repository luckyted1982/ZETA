import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Loader2, FileText, RefreshCw } from 'lucide-react'
import { generateAIDiagnosis } from '../services/api'

/**
 * AI深度诊断报告组件
 * 调用后端AI接口生成报告，并渲染Markdown内容
 */
function AIReport({ evaluationId }) {
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleGenerateReport = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await generateAIDiagnosis(evaluationId)
      setReport(data.report_content || 'AI诊断报告生成成功。')
    } catch (err) {
      setError(err.message || '生成报告失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadPDF = () => {
    window.print()
  }

  // 如果还没有生成报告，显示生成按钮
  if (!report) {
    return (
      <div className="bg-gradient-to-br from-primary/5 to-secondary/5 rounded-2xl p-8 border border-primary/20 text-center">
        <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-primary to-secondary rounded-2xl flex items-center justify-center">
          <FileText className="w-8 h-8 text-white" />
        </div>
        <h3 className="text-xl font-semibold text-gray-800 mb-2">AI深度诊断报告</h3>
        <p className="text-gray-600 mb-6 max-w-md mx-auto">
          基于DeepSeek大模型，结合您的评测数据，生成包含优势分析、劣势分析、风险预警和改进路线的深度诊断报告
        </p>
        <button
          onClick={handleGenerateReport}
          disabled={loading}
          className="btn-primary flex items-center gap-2 mx-auto disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              AI正在分析中...
            </>
          ) : (
            <>
              <FileText className="w-5 h-5" />
              生成AI深度诊断报告
            </>
          )}
        </button>
        {error && (
          <p className="mt-4 text-red-500 text-sm">{error}</p>
        )}
      </div>
    )
  }

  // 显示生成的报告
  return (
    <div className="bg-white rounded-2xl p-8 shadow-card border border-gray-100">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-xl font-semibold text-gray-800">AI深度诊断报告</h3>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleGenerateReport}
            className="flex items-center gap-2 px-4 py-2 text-sm text-primary hover:bg-primary/5 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            重新生成
          </button>
          <button
            onClick={handleDownloadPDF}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-white text-sm rounded-lg hover:bg-secondary transition-colors"
          >
            <FileText className="w-4 h-4" />
            下载报告
          </button>
        </div>
      </div>

      <div className="markdown-body border-t border-gray-100 pt-6">
        <ReactMarkdown>{report}</ReactMarkdown>
      </div>
    </div>
  )
}

export default AIReport
