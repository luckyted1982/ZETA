import React, { useState, useEffect, useCallback } from 'react'
import { Save, AlertCircle, Loader2 } from 'lucide-react'
import ProgressBar from './ProgressBar'
import { getDimensions } from '../services/api'

/**
 * Step 2: 8维度简化评测问卷
 * 每个维度显示一个总分数滑块（0-100），支持保存进度
 */
function Step2Evaluation({ scores, onScoresChange, onSubmit, onPrev }) {
  const [dimensions, setDimensions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState(null)

  const totalQuestions = dimensions.length
  const completedCount = Object.keys(scores).length

  // 加载维度定义
  useEffect(() => {
    async function loadDimensions() {
      try {
        setLoading(true)
        const dims = await getDimensions()
        setDimensions(dims)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadDimensions()
  }, [])

  // 保存进度到localStorage
  const saveProgress = useCallback(() => {
    setSaving(true)
    try {
      const progressData = {
        scores,
        timestamp: Date.now(),
      }
      localStorage.setItem('evaluation_progress', JSON.stringify(progressData))
      setLastSaved(new Date())
    } catch (e) {
      console.error('保存进度失败:', e)
    } finally {
      setSaving(false)
    }
  }, [scores])

  // 自动保存（每30秒）
  useEffect(() => {
    const interval = setInterval(() => {
      if (completedCount > 0) {
        saveProgress()
      }
    }, 30000)
    return () => clearInterval(interval)
  }, [saveProgress, completedCount])

  const handleScoreChange = (dimId, value) => {
    onScoresChange({
      ...scores,
      [dimId]: parseInt(value, 10),
    })
  }

  const handleSubmit = () => {
    if (completedCount < totalQuestions) {
      const confirm = window.confirm(`您已完成 ${completedCount}/${totalQuestions} 个维度评分，确认提交吗？`)
      if (!confirm) return
    }
    onSubmit()
  }

  // 获取等级标签
  const getGradeLabel = (score) => {
    if (score >= 90) return 'S - 卓越'
    if (score >= 80) return 'A - 优秀'
    if (score >= 70) return 'B - 良好'
    if (score >= 60) return 'C - 合格'
    return 'D - 待提升'
  }

  const getGradeColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getSliderColor = (score) => {
    if (score >= 80) return 'bg-green-500'
    if (score >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
        <span className="ml-3 text-gray-600">正在加载评测维度...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
        <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
        <p className="text-red-600">加载失败: {error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
        >
          重新加载
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* 顶部进度和操作 */}
      <div className="bg-white rounded-2xl p-6 shadow-card border border-gray-100 sticky top-4 z-20">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-lg font-semibold text-gray-800">8维度评测</h2>
              <div className="flex items-center gap-3">
                {lastSaved && (
                  <span className="text-xs text-gray-400">
                    上次保存: {lastSaved.toLocaleTimeString()}
                  </span>
                )}
                <button
                  onClick={saveProgress}
                  disabled={saving}
                  className="flex items-center gap-1 px-3 py-1.5 text-sm text-primary hover:bg-primary/5 rounded-lg transition-colors disabled:opacity-50"
                >
                  {saving ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Save className="w-4 h-4" />
                  )}
                  保存进度
                </button>
              </div>
            </div>
            <ProgressBar
              current={completedCount}
              total={totalQuestions}
              label={`已完成 ${completedCount} / ${totalQuestions} 个维度`}
            />
          </div>
        </div>
      </div>

      {/* 维度评分卡片 */}
      <div className="space-y-4">
        {dimensions.map((dim) => {
          const score = scores[dim.dimension_id] || 0
          const gradeLabel = score > 0 ? getGradeLabel(score) : '未评分'
          const gradeColor = score > 0 ? getGradeColor(score) : 'text-gray-400'
          const sliderColor = score > 0 ? getSliderColor(score) : 'bg-gray-300'

          return (
            <div
              key={dim.dimension_id}
              className="bg-white rounded-2xl p-6 shadow-card border border-gray-100 transition-all hover:shadow-lg"
            >
              <div className="flex flex-col md:flex-row md:items-start gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-800">
                      {dim.name}
                    </h3>
                    {score > 0 && (
                      <span className={`text-sm font-medium ${gradeColor}`}>
                        {gradeLabel}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 mb-4">
                    {dim.description}
                  </p>
                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      min="0"
                      max="100"
                      step="1"
                      value={score}
                      onChange={(e) => handleScoreChange(dim.dimension_id, e.target.value)}
                      className="flex-1 h-2 rounded-lg appearance-none cursor-pointer bg-gray-200 accent-current"
                      style={{ accentColor: score >= 80 ? '#22c55e' : score >= 60 ? '#eab308' : '#ef4444' }}
                    />
                    <div className="w-20 text-right">
                      <span className={`text-xl font-bold ${gradeColor}`}>
                        {score}
                      </span>
                      <span className="text-sm text-gray-400 ml-1">分</span>
                    </div>
                  </div>
                  <div className="flex justify-between mt-2 text-xs text-gray-400">
                    <span>0</span>
                    <span>25</span>
                    <span>50</span>
                    <span>75</span>
                    <span>100</span>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* 底部操作 */}
      <div className="flex justify-between items-center pt-6">
        <button
          onClick={onPrev}
          className="px-6 py-3 text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
        >
          返回上一步
        </button>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500">
            已完成 {completedCount}/{totalQuestions} 个维度
          </span>
          <button
            onClick={handleSubmit}
            className="px-6 py-3 bg-primary text-white rounded-xl hover:bg-secondary transition-colors font-medium"
          >
            提交评测
          </button>
        </div>
      </div>
    </div>
  )
}

export default Step2Evaluation
