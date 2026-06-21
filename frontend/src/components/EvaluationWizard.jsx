import React, { useState, useEffect, useCallback } from 'react'
import { ArrowLeft, Loader2 } from 'lucide-react'
import Step1BasicInfo from './Step1BasicInfo'
import Step2Evaluation from './Step2Evaluation'
import Step3Report from './Step3Report'
import { submitEvaluation } from '../services/api'

/**
 * 评测向导组件
 * 管理3步骤流程：基本信息 → 8维度评测 → 报告展示
 * 支持localStorage保存进度
 */
function EvaluationWizard({ onBack }) {
  const [step, setStep] = useState(1)
  const [basicInfo, setBasicInfo] = useState({})
  const [scores, setScores] = useState({})
  const [result, setResult] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  // 从localStorage加载保存的进度
  useEffect(() => {
    try {
      const saved = localStorage.getItem('evaluation_progress')
      if (saved) {
        const progress = JSON.parse(saved)
        if (progress.basicInfo) {
          setBasicInfo(progress.basicInfo)
        }
        if (progress.scores && Object.keys(progress.scores).length > 0) {
          setScores(progress.scores)
        }
        if (progress.step) {
          setStep(progress.step)
        }
      }
    } catch (e) {
      console.error('读取保存进度失败:', e)
    }
  }, [])

  // 保存进度到localStorage
  const saveProgress = useCallback(() => {
    try {
      const progressData = {
        basicInfo,
        scores,
        step,
        timestamp: Date.now(),
      }
      localStorage.setItem('evaluation_progress', JSON.stringify(progressData))
    } catch (e) {
      console.error('保存进度失败:', e)
    }
  }, [basicInfo, scores, step])

  // 自动保存
  useEffect(() => {
    saveProgress()
  }, [saveProgress])

  const handleStep1Next = () => {
    setStep(2)
    window.scrollTo(0, 0)
  }

  const handleStep2Submit = async () => {
    setSubmitting(true)
    setError(null)

    try {
      // 组装简化版提交数据
      const evaluationData = {
        company: {
          name: basicInfo.companyName || '未命名企业',
          stage: basicInfo.stage || 'seed',
          industry: basicInfo.industry,
          founded_year: basicInfo.foundedYear ? parseInt(basicInfo.foundedYear) : null,
          employees: basicInfo.teamSize ? parseInt(basicInfo.teamSize) : null,
          location: basicInfo.location,
          description: basicInfo.description,
        },
        dimension_scores: scores,
      }

      const response = await submitEvaluation(evaluationData)
      setResult(response)
      setStep(3)
      window.scrollTo(0, 0)

      // 提交成功后清除保存的进度
      localStorage.removeItem('evaluation_progress')
    } catch (err) {
      setError(err.message || '提交评测失败，请稍后重试')
    } finally {
      setSubmitting(false)
    }
  }

  const handleRestart = () => {
    // 清除所有状态
    setBasicInfo({})
    setScores({})
    setResult(null)
    setError(null)
    setStep(1)
    localStorage.removeItem('evaluation_progress')
    window.scrollTo(0, 0)
  }

  const steps = [
    { number: 1, title: '企业基本信息' },
    { number: 2, title: '8维度评测' },
    { number: 3, title: '生成报告' },
  ]

  return (
    <div className="min-h-screen bg-background py-8 px-4">
      {/* 顶部导航 */}
      <div className="max-w-5xl mx-auto mb-8">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            返回首页
          </button>
          <h1 className="text-xl font-bold text-gray-800">AI科创企业评测</h1>
          <div className="w-20" /> {/* 占位保持居中 */}
        </div>

        {/* 步骤条 */}
        <div className="flex items-center justify-between">
          {steps.map((s, index) => (
            <div key={s.number} className="flex items-center flex-1">
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm transition-all ${
                    step > s.number
                      ? 'bg-primary text-white'
                      : step === s.number
                      ? 'bg-primary text-white ring-4 ring-primary/20'
                      : 'bg-gray-200 text-gray-400'
                  }`}
                >
                  {step > s.number ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    s.number
                  )}
                </div>
                <span
                  className={`mt-2 text-sm font-medium ${
                    step >= s.number ? 'text-gray-800' : 'text-gray-400'
                  }`}
                >
                  {s.title}
                </span>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`flex-1 h-1 mx-4 rounded-full ${
                    step > s.number ? 'bg-primary' : 'bg-gray-200'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 步骤内容 */}
      <div className="max-w-5xl mx-auto">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4 text-red-600">
            {error}
          </div>
        )}

        {step === 1 && (
          <Step1BasicInfo
            data={basicInfo}
            onChange={setBasicInfo}
            onNext={handleStep1Next}
          />
        )}

        {step === 2 && (
          <Step2Evaluation
            scores={scores}
            onScoresChange={setScores}
            onSubmit={handleStep2Submit}
            onPrev={() => setStep(1)}
          />
        )}

        {step === 3 && (
          <Step3Report
            result={result}
            onRestart={handleRestart}
            onPrev={() => setStep(2)}
          />
        )}
      </div>

      {/* 提交加载遮罩 */}
      {submitting && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 text-center shadow-2xl">
            <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-800">AI正在深度分析中...</p>
            <p className="text-sm text-gray-500 mt-2">请稍候，正在生成您的评测报告</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default EvaluationWizard
