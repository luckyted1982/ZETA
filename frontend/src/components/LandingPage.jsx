import React from 'react'
import { Sparkles, BarChart3, Brain, Zap, ChevronRight, Building2, Award, TrendingUp, Shield } from 'lucide-react'

/**
 * 首页/Landing页面
 * 展示平台介绍、核心特色、评测流程和Demo案例
 */
function LandingPage({ onStart }) {
  // 8大维度数据
  const dimensions = [
    { name: '技术创新力', icon: Zap, desc: '核心技术与研发能力' },
    { name: '团队实力', icon: Building2, desc: '创始人背景与团队配置' },
    { name: '市场前景', icon: TrendingUp, desc: '市场空间与增长潜力' },
    { name: '商业模式', icon: BarChart3, desc: '盈利路径与可持续性' },
    { name: '知识产权', icon: Shield, desc: '专利布局与保护能力' },
    { name: '财务健康', icon: Award, desc: '现金流与融资能力' },
    { name: '运营效率', icon: Brain, desc: '组织管理与执行效率' },
    { name: 'ESG表现', icon: Sparkles, desc: '环境社会治理责任' },
  ]

  // 评测流程步骤
  const steps = [
    { step: 1, title: '填写企业信息', desc: '3分钟完成基础资料录入' },
    { step: 2, title: '8维度评测', desc: '基于行业标准的科学评分' },
    { step: 3, title: '获取AI报告', desc: '深度诊断与改进方案' },
  ]

  return (
    <div className="fade-in">
      {/* 英雄区域 */}
      <header className="relative bg-gradient-to-br from-primary via-secondary to-gray-800 text-white py-20 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <div className="flex items-center justify-center gap-3 mb-6">
            <Sparkles className="w-10 h-10 text-accent" />
            <h1 className="text-4xl md:text-5xl font-bold">AI科创企业评测系统</h1>
          </div>
          <p className="text-lg md:text-xl text-gray-200 max-w-2xl mx-auto mb-8 leading-relaxed">
            基于深度研究的8维度科学评测，AI驱动的个性化诊断与改进方案
          </p>
          <button
            onClick={onStart}
            className="btn-primary text-lg flex items-center gap-2 mx-auto"
          >
            开始评测
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        {/* 装饰背景 */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-32 h-32 bg-white/5 rounded-full blur-2xl" />
          <div className="absolute bottom-20 right-10 w-40 h-40 bg-accent/10 rounded-full blur-3xl" />
        </div>
      </header>

      {/* 8大维度展示 */}
      <section className="py-16 px-4 max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
          8大核心评测维度
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {dimensions.map((dim) => {
            const Icon = dim.icon
            return (
              <div
                key={dim.name}
                className="bg-white rounded-2xl p-6 shadow-card card-hover text-center"
              >
                <div className="w-14 h-14 mx-auto mb-4 bg-gradient-to-br from-primary/20 to-secondary/20 rounded-xl flex items-center justify-center">
                  <Icon className="w-7 h-7 text-primary" />
                </div>
                <h3 className="font-semibold text-gray-800 mb-1">{dim.name}</h3>
                <p className="text-sm text-gray-500">{dim.desc}</p>
              </div>
            )
          })}
        </div>
      </section>

      {/* 评测流程 */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
            简单3步，完成评测
          </h2>
          <div className="flex flex-col md:flex-row gap-8 justify-between items-center">
            {steps.map((s, index) => (
              <div key={s.step} className="flex items-center gap-4">
                <div className="bg-gradient-to-br from-primary to-secondary text-white w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-bold shadow-lg">
                  {s.step}
                </div>
                <div>
                  <h3 className="font-semibold text-lg text-gray-800">{s.title}</h3>
                  <p className="text-gray-500">{s.desc}</p>
                </div>
                {index < steps.length - 1 && (
                  <ChevronRight className="hidden md:block w-8 h-8 text-gray-300 mx-4" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Demo案例 */}
      <section className="py-16 px-4 max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
          Demo企业案例
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-white rounded-2xl p-6 shadow-card card-hover border border-gray-100">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-800">智芯半导体</h3>
                <p className="text-sm text-gray-500">A轮 | 芯片设计</p>
              </div>
            </div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl font-bold text-blue-600">86</span>
              <span className="text-sm text-gray-500">综合评分</span>
              <span className="ml-auto px-2 py-1 bg-blue-50 text-blue-600 rounded-lg text-sm font-semibold">A级</span>
            </div>
            <p className="text-sm text-gray-600">技术壁垒深厚，团队背景优秀，建议重点突破市场渠道。</p>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-card card-hover border border-gray-100">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-800">云智医疗</h3>
                <p className="text-sm text-gray-500">B轮 | AI医疗</p>
              </div>
            </div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl font-bold text-green-600">92</span>
              <span className="text-sm text-gray-500">综合评分</span>
              <span className="ml-auto px-2 py-1 bg-green-50 text-green-600 rounded-lg text-sm font-semibold">S级</span>
            </div>
            <p className="text-sm text-gray-600">全面均衡发展，商业模式清晰，具备独角兽潜质。</p>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-card card-hover border border-gray-100">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-800">碳能科技</h3>
                <p className="text-sm text-gray-500">Pre-A轮 | 新能源</p>
              </div>
            </div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl font-bold text-amber-600">72</span>
              <span className="text-sm text-gray-500">综合评分</span>
              <span className="ml-auto px-2 py-1 bg-amber-50 text-amber-600 rounded-lg text-sm font-semibold">B级</span>
            </div>
            <p className="text-sm text-gray-600">赛道前景广阔，需加强知识产权布局和团队扩充。</p>
          </div>
        </div>
      </section>

      {/* 底部CTA */}
      <section className="py-20 px-4 bg-gradient-to-br from-primary to-secondary text-white text-center">
        <h2 className="text-3xl font-bold mb-4">准备好了解您的企业了吗？</h2>
        <p className="text-gray-200 mb-8 max-w-xl mx-auto">
          基于AI算法的科学评测，为您提供客观、专业的企业诊断报告
        </p>
        <button
          onClick={onStart}
          className="bg-white text-primary px-10 py-4 rounded-xl font-semibold text-lg shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-105"
        >
          立即开始评测
        </button>
      </section>

      {/* 页脚 */}
      <footer className="py-8 px-4 text-center text-gray-500 text-sm bg-gray-50">
        <p>AI科创企业评测系统 | 基于深度研究的专业评测工具</p>
      </footer>
    </div>
  )
}

export default LandingPage
