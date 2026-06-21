import React, { useState, useEffect } from 'react'
import { Building2, Users, Calendar, TrendingUp, Award, DollarSign, Cpu, FileBadge } from 'lucide-react'

/**
 * Step 1: 企业基本信息表单
 * 收集企业的基础信息，支持从localStorage加载和保存
 */
function Step1BasicInfo({ data, onChange, onNext }) {
  const [errors, setErrors] = useState({})

  // 行业选项
  const industries = [
    '人工智能',
    '半导体',
    '生物医药',
    '新能源',
    '新材料',
    '高端装备制造',
    '其他',
  ]

  // 发展阶段选项（值对应后端stage格式）
  const stages = [
    { label: '种子期', value: 'seed' },
    { label: '天使期', value: 'angel' },
    { label: 'Pre-A轮', value: 'pre-a' },
    { label: 'A轮', value: 'a-round' },
  ]

  // 成立年限选项
  const yearsOptions = [
    '1年以内',
    '1-2年',
    '2-3年',
    '3-5年',
    '5年以上',
  ]

  // 团队规模选项
  const teamSizes = [
    '10人以下',
    '10-20人',
    '20-50人',
    '50-100人',
    '100人以上',
  ]

  // 年营收选项
  const revenues = [
    '无营收',
    '100万以下',
    '100-500万',
    '500-2000万',
    '2000万以上',
  ]

  // 融资状态选项
  const fundingStatus = [
    '未融资',
    '种子轮',
    '天使轮',
    'Pre-A轮',
    'A轮',
    'B轮及以上',
  ]

  // 现有资质选项
  const qualifications = [
    '科技型中小企业',
    '高新技术企业',
    '专精特新',
    '小巨人',
    '瞪羚企业',
    '独角兽',
  ]

  const handleChange = (field, value) => {
    onChange({ ...data, [field]: value })
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

  const handleQualificationToggle = (qual) => {
    const current = data.qualifications || []
    const updated = current.includes(qual)
      ? current.filter(q => q !== qual)
      : [...current, qual]
    handleChange('qualifications', updated)
  }

  const validate = () => {
    const newErrors = {}
    if (!data.companyName?.trim()) newErrors.companyName = '请输入企业名称'
    if (!data.industry) newErrors.industry = '请选择所属行业'
    if (!data.stage) newErrors.stage = '请选择发展阶段'

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (validate()) {
      onNext()
    }
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-3xl mx-auto space-y-6">
      <div className="bg-white rounded-2xl p-8 shadow-card border border-gray-100">
        <h2 className="text-xl font-semibold text-gray-800 mb-6 flex items-center gap-2">
          <Building2 className="w-5 h-5 text-primary" />
          企业基本信息
        </h2>

        <div className="grid md:grid-cols-2 gap-6">
          {/* 企业名称 */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              企业名称 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={data.companyName || ''}
              onChange={(e) => handleChange('companyName', e.target.value)}
              placeholder="请输入企业全称"
              className={`w-full px-4 py-3 rounded-xl border ${
                errors.companyName ? 'border-red-500' : 'border-gray-200'
              } focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all`}
            />
            {errors.companyName && (
              <p className="mt-1 text-sm text-red-500">{errors.companyName}</p>
            )}
          </div>

          {/* 所属行业 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              所属行业 <span className="text-red-500">*</span>
            </label>
            <select
              value={data.industry || ''}
              onChange={(e) => handleChange('industry', e.target.value)}
              className={`w-full px-4 py-3 rounded-xl border ${
                errors.industry ? 'border-red-500' : 'border-gray-200'
              } focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all bg-white`}
            >
              <option value="">请选择行业</option>
              {industries.map(ind => (
                <option key={ind} value={ind}>{ind}</option>
              ))}
            </select>
            {errors.industry && (
              <p className="mt-1 text-sm text-red-500">{errors.industry}</p>
            )}
          </div>

          {/* 发展阶段 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              发展阶段 <span className="text-red-500">*</span>
            </label>
            <select
              value={data.stage || ''}
              onChange={(e) => handleChange('stage', e.target.value)}
              className={`w-full px-4 py-3 rounded-xl border ${
                errors.stage ? 'border-red-500' : 'border-gray-200'
              } focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all bg-white`}
            >
              <option value="">请选择阶段</option>
              {stages.map(s => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
            {errors.stage && (
              <p className="mt-1 text-sm text-red-500">{errors.stage}</p>
            )}
          </div>

          {/* 成立年限 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Calendar className="w-4 h-4 inline mr-1" />
              成立年限
            </label>
            <select
              value={data.foundedYear || ''}
              onChange={(e) => handleChange('foundedYear', e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all bg-white"
            >
              <option value="">请选择年限</option>
              {yearsOptions.map(y => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>

          {/* 团队规模 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Users className="w-4 h-4 inline mr-1" />
              团队规模
            </label>
            <select
              value={data.teamSize || ''}
              onChange={(e) => handleChange('teamSize', e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all bg-white"
            >
              <option value="">请选择规模</option>
              {teamSizes.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          {/* 年营收 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <TrendingUp className="w-4 h-4 inline mr-1" />
              年营收
            </label>
            <select
              value={data.revenue || ''}
              onChange={(e) => handleChange('revenue', e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all bg-white"
            >
              <option value="">请选择营收</option>
              {revenues.map(r => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>

          {/* 融资状态 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <DollarSign className="w-4 h-4 inline mr-1" />
              融资状态
            </label>
            <select
              value={data.fundingStatus || ''}
              onChange={(e) => handleChange('fundingStatus', e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all bg-white"
            >
              <option value="">请选择状态</option>
              {fundingStatus.map(f => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
          </div>

          {/* 核心技术方向 */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Cpu className="w-4 h-4 inline mr-1" />
              核心技术方向
            </label>
            <input
              type="text"
              value={data.techDirection || ''}
              onChange={(e) => handleChange('techDirection', e.target.value)}
              placeholder="例如：大语言模型、自动驾驶芯片、创新药研发..."
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
            />
          </div>

          {/* 现有资质 */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <FileBadge className="w-4 h-4 inline mr-1" />
              现有资质（可多选）
            </label>
            <div className="flex flex-wrap gap-3">
              {qualifications.map(qual => {
                const isSelected = (data.qualifications || []).includes(qual)
                return (
                  <button
                    key={qual}
                    type="button"
                    onClick={() => handleQualificationToggle(qual)}
                    className={`px-4 py-2 rounded-xl border transition-all ${
                      isSelected
                        ? 'bg-primary/10 border-primary text-primary font-medium'
                        : 'border-gray-200 text-gray-600 hover:border-gray-300'
                    }`}
                  >
                    {isSelected && <span className="mr-1">✓</span>}
                    {qual}
                  </button>
                )
              })}
              <button
                type="button"
                onClick={() => handleChange('qualifications', [])}
                className="px-4 py-2 rounded-xl border border-gray-200 text-gray-400 hover:border-gray-300 transition-all"
              >
                无资质
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 下一步按钮 */}
      <div className="flex justify-end">
        <button
          type="submit"
          className="btn-primary flex items-center gap-2"
        >
          下一步：开始评测
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </form>
  )
}

export default Step1BasicInfo
