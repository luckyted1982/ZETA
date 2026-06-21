import React, { useState } from 'react'
import { ArrowLeft, RotateCcw, Printer, Sparkles } from 'lucide-react'
import ScoreCard from './ScoreCard'
import RadarChart from './RadarChart'
import BenchmarkBar from './BenchmarkBar'
import AIReport from './AIReport'

/**
 * Step 3: 评测报告展示
 * 展示综合评分、雷达图、基准对比、优势劣势分析，以及AI深度诊断
 */
function Step3Report({ result, onRestart, onPrev }) {
  const [showAIReport, setShowAIReport] = useState(false)

  if (!result) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
          <p className="text-gray-600">正在生成评测报告...</p>
        </div>
      </div>
    )
  }

  // 从 EvaluationResult 中提取数据
  const company = result.company || {}
  const dimensions = result.dimensions || []
  const totalScore = result.total_score || 0
  const overallGrade = result.overall_grade || 'C'
  const overallGradeLabel = result.overall_grade_label || '合格'
  const strengths = result.strengths || []
  const weaknesses = result.weaknesses || []
  const evaluationId = result.evaluation_id || ''

  // 提取各维度分数和基准值
  const dimensionNames = dimensions.map(d => d.name)
  const dimensionScores = dimensions.map(d => d.score)
  const benchmarkScores = dimensions.map(d => d.benchmark || d.score * 0.9) // 如果没有基准，模拟一个略低的值

  const handlePrint = () => {
    window.print()
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8 fade-in">
      {/* 报告头部 */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">评测报告</h2>
          <p className="text-gray-500 mt-1">
            {company.name || '企业'} | {company.industry || '未知行业'} | {company.stage || '未知阶段'}
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handlePrint}
            className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
          >
            <Printer className="w-4 h-4" />
            打印/下载
          </button>
          <button
            onClick={onRestart}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-xl hover:bg-secondary transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            重新评测
          </button>
        </div>
      </div>

      {/* 综合评分 */}
      <ScoreCard totalScore={totalScore} grade={overallGrade} />

      {/* 雷达图 + 基准对比 */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-card border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">8维度能力雷达图</h3>
          <RadarChart
            dimensions={dimensionNames}
            scores={dimensionScores}
            benchmarkScores={benchmarkScores}
          />
        </div>
        <BenchmarkBar
          dimensions={dimensionNames}
          scores={dimensionScores}
          benchmarkScores={benchmarkScores}
        />
      </div>

      {/* 优势 + 劣势 */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* TOP3 优势 */}
        <div className="bg-white rounded-2xl p-6 shadow-card border border-gray-100">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-800">优势维度</h3>
          </div>
          <div className="space-y-3">
            {strengths.length > 0 ? strengths.slice(0, 5).map((item, idx) => (
              <div key={idx} className="flex items-center gap-3 p-3 bg-green-50 rounded-xl border border-green-100">
                <span className="w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  {idx + 1}
                </span>
                <div className="flex-1">
                  <span className="font-medium text-gray-800">{item}</span>
                </div>
              </div>
            )) : (
              <p className="text-gray-500 text-sm">暂无显著优势</p>
            )}
          </div>
        </div>

        {/* TOP3 劣势 */}
        <div className="bg-white rounded-2xl p-6 shadow-card border border-gray-100">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-800">待改进维度</h3>
          </div>
          <div className="space-y-3">
            {weaknesses.length > 0 ? weaknesses.slice(0, 5).map((item, idx) => (
              <div key={idx} className="flex items-center gap-3 p-3 bg-red-50 rounded-xl border border-red-100">
                <span className="w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  {idx + 1}
                </span>
                <div className="flex-1">
                  <span className="font-medium text-gray-800">{item}</span>
                </div>
              </div>
            )) : (
              <p className="text-gray-500 text-sm">暂无显著劣势</p>
            )}
          </div>
        </div>
      </div>

      {/* AI深度诊断报告 */}
      <AIReport evaluationId={evaluationId} />

      {/* 底部操作 */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-200">
        <button
          onClick={onPrev}
          className="flex items-center gap-2 px-6 py-3 text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          返回修改
        </button>
        <button
          onClick={onRestart}
          className="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-xl hover:bg-secondary transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          重新评测
        </button>
      </div>
    </div>
  )
}

export default Step3Report
