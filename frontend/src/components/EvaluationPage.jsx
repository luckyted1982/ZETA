import React from 'react'
import EvaluationWizard from './EvaluationWizard'

function EvaluationPage() {
  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800">评测中心</h2>
        <p className="text-gray-500 mt-1">基于8维度科学评测体系，全面评估科创企业能力</p>
      </div>
      <EvaluationWizard onBack={() => {}} />
    </div>
  )
}

export default EvaluationPage
