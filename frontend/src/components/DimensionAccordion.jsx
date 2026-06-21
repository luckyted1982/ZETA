import React, { useState } from 'react'
import { ChevronDown, ChevronUp, Info } from 'lucide-react'

/**
 * 维度折叠面板组件
 * 每个维度包含多个评分题，使用滑块评分
 */
function DimensionAccordion({ dimension, scores, onScoreChange }) {
  const [isOpen, setIsOpen] = useState(false)
  const completedCount = scores.filter(s => s > 0).length
  const totalQuestions = dimension.questions?.length || 0
  const isCompleted = completedCount === totalQuestions && totalQuestions > 0

  // 维度颜色映射
  const colorMap = {
    '技术创新力': 'bg-blue-50 border-blue-200 text-blue-600',
    '团队实力': 'bg-purple-50 border-purple-200 text-purple-600',
    '市场前景': 'bg-green-50 border-green-200 text-green-600',
    '商业模式': 'bg-amber-50 border-amber-200 text-amber-600',
    '知识产权': 'bg-indigo-50 border-indigo-200 text-indigo-600',
    '财务健康': 'bg-emerald-50 border-emerald-200 text-emerald-600',
    '运营效率': 'bg-rose-50 border-rose-200 text-rose-600',
    'ESG表现': 'bg-teal-50 border-teal-200 text-teal-600',
  }
  const colorClass = colorMap[dimension.name] || 'bg-gray-50 border-gray-200 text-gray-600'

  // 获取滑块背景颜色
  const getSliderColor = (value) => {
    if (value <= 3) return 'from-red-400 to-red-500'
    if (value <= 6) return 'from-amber-400 to-amber-500'
    return 'from-green-400 to-green-500'
  }

  return (
    <div className={`border rounded-xl overflow-hidden transition-all duration-300 ${isOpen ? 'shadow-card-hover' : 'shadow-card'}`}>
      {/* 面板头部 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-5 bg-white hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-4">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center border-2 ${colorClass}`}>
            <span className="text-xl font-bold">{dimension.icon || dimension.name[0]}</span>
          </div>
          <div className="text-left">
            <h3 className="font-semibold text-gray-800 text-lg">{dimension.name}</h3>
            <p className="text-sm text-gray-500">{dimension.description || '该维度描述'}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {isCompleted && (
            <span className="px-2 py-1 bg-green-100 text-green-600 rounded-lg text-xs font-medium">
              已完成
            </span>
          )}
          <span className="text-sm text-gray-400">
            {completedCount}/{totalQuestions}
          </span>
          {isOpen ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </button>

      {/* 面板内容 - 评分题 */}
      {isOpen && (
        <div className="p-5 border-t border-gray-100 bg-gray-50/50">
          <div className="space-y-6">
            {dimension.questions?.map((question, qIndex) => {
              const scoreIndex = dimension.questionIndexOffset + qIndex
              const currentScore = scores[scoreIndex] || 0

              return (
                <div key={qIndex} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                  <div className="flex items-start gap-2 mb-4">
                    <Info className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-gray-800">{question.text}</p>
                      {question.description && (
                        <p className="text-sm text-gray-500 mt-1">{question.description}</p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-400 w-8">1</span>
                    <input
                      type="range"
                      min="1"
                      max="10"
                      step="1"
                      value={currentScore}
                      onChange={(e) => onScoreChange(scoreIndex, parseInt(e.target.value))}
                      className={`flex-1 h-2 bg-gradient-to-r ${getSliderColor(currentScore)} rounded-lg appearance-none cursor-pointer`}
                    />
                    <span className="text-sm text-gray-400 w-8 text-right">10</span>
                  </div>

                  <div className="flex justify-between mt-2">
                    <div className="flex gap-1">
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((star) => (
                        <button
                          key={star}
                          onClick={() => onScoreChange(scoreIndex, star)}
                          className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-semibold transition-all duration-200 ${
                            star <= currentScore
                              ? star <= 3
                                ? 'bg-red-100 text-red-600'
                                : star <= 6
                                ? 'bg-amber-100 text-amber-600'
                                : 'bg-green-100 text-green-600'
                              : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
                          }`}
                        >
                          {star}
                        </button>
                      ))}
                    </div>
                    <span className={`font-bold text-lg ${
                      currentScore <= 3 ? 'text-red-500' : currentScore <= 6 ? 'text-amber-500' : 'text-green-500'
                    }`}>
                      {currentScore}分
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default DimensionAccordion
