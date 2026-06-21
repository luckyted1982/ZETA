import React, { useEffect, useState } from 'react'

/**
 * 评分卡片组件
 * 展示总分和等级，带动画效果
 */
function ScoreCard({ totalScore, grade }) {
  const [displayScore, setDisplayScore] = useState(0)

  // 数字递增动画
  useEffect(() => {
    const duration = 1000
    const startTime = Date.now()

    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setDisplayScore(Math.round(totalScore * eased))

      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }

    requestAnimationFrame(animate)
  }, [totalScore])

  // 等级样式映射
  const gradeStyles = {
    'S': { class: 'grade-s', label: '卓越' },
    'A': { class: 'grade-a', label: '优秀' },
    'B': { class: 'grade-b', label: '良好' },
    'C': { class: 'grade-c', label: '合格' },
    'D': { class: 'grade-d', label: '待改进' },
  }

  const gradeInfo = gradeStyles[grade] || gradeStyles['D']

  return (
    <div className="bg-white rounded-2xl p-8 shadow-card border border-gray-100 text-center">
      <h3 className="text-lg font-medium text-gray-500 mb-4">综合评分</h3>
      <div className="flex items-center justify-center gap-4 mb-4">
        <span className="text-6xl font-bold text-gray-800 count-up">
          {displayScore}
        </span>
        <span className="text-xl text-gray-400">/100</span>
      </div>
      <div className={`inline-block px-6 py-2 rounded-xl border-2 font-bold text-xl ${gradeInfo.class}`}>
        {grade}级 - {gradeInfo.label}
      </div>
      <p className="mt-4 text-sm text-gray-500">
        基于8个维度的加权综合计算
      </p>
    </div>
  )
}

export default ScoreCard
