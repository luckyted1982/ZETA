import React from 'react'

/**
 * 基准对比条形图组件
 * 使用原生HTML/CSS实现，对比企业得分与行业基准
 */
function BenchmarkBar({ dimensions, scores, benchmarkScores }) {
  const maxScore = 100

  return (
    <div className="bg-white rounded-2xl p-6 shadow-card border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-800 mb-6">同阶段基准对比</h3>
      <div className="space-y-4">
        {dimensions.map((dim, index) => {
          const score = scores[index] || 0
          const benchmark = benchmarkScores?.[index] || 5
          const scorePercent = (score / maxScore) * 100
          const benchmarkPercent = (benchmark / maxScore) * 100
          const diff = score - benchmark

          return (
            <div key={index} className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">{dim}</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-primary">{score.toFixed(1)}</span>
                  <span className="text-xs text-gray-400">/ 基准 {benchmark.toFixed(1)}</span>
                  {diff > 0 ? (
                    <span className="text-xs text-green-600 font-medium">+{diff.toFixed(1)}</span>
                  ) : diff < 0 ? (
                    <span className="text-xs text-red-500 font-medium">{diff.toFixed(1)}</span>
                  ) : (
                    <span className="text-xs text-gray-400">持平</span>
                  )}
                </div>
              </div>
              <div className="relative h-6 bg-gray-100 rounded-lg overflow-hidden">
                {/* 基准线 */}
                <div
                  className="absolute top-0 bottom-0 w-0.5 bg-gray-400 z-10"
                  style={{ left: `${benchmarkPercent}%` }}
                />
                {/* 企业得分条 */}
                <div
                  className="h-full rounded-lg transition-all duration-1000 ease-out relative"
                  style={{
                    width: `${scorePercent}%`,
                    background: diff >= 0
                      ? 'linear-gradient(90deg, #7B6D8D, #9CA3AF)'
                      : 'linear-gradient(90deg, #F59E0B, #D97706)',
                  }}
                />
              </div>
            </div>
          )
        })}
      </div>
      <div className="flex gap-6 mt-6 pt-4 border-t border-gray-100">
        <div className="flex items-center gap-2">
          <div className="w-4 h-2 rounded bg-gradient-to-r from-primary to-gray-400" />
          <span className="text-xs text-gray-500">企业得分</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-0.5 h-4 bg-gray-400" />
          <span className="text-xs text-gray-500">行业基准</span>
        </div>
      </div>
    </div>
  )
}

export default BenchmarkBar
