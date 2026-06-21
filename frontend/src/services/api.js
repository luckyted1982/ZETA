const API_BASE = '/api/v1'

/**
 * 统一的fetch封装
 */
async function fetchAPI(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || errorData.message || `请求失败: ${response.status}`)
  }

  const result = await response.json()
  return result.data || result
}

/* ==================== 系统 ==================== */
export async function checkHealth() {
  return fetch('/health').then(r => r.json())
}

/* ==================== 评测接口 ==================== */
export async function getDimensions() {
  return fetchAPI(`${API_BASE}/dimensions`)
}

export async function getStages() {
  return fetchAPI(`${API_BASE}/stages`)
}

export async function submitEvaluation(data) {
  return fetchAPI(`${API_BASE}/evaluate-simple`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function generateAIDiagnosis(evaluationId) {
  return fetchAPI(`${API_BASE}/evaluate/${evaluationId}/ai-diagnosis`, {
    method: 'POST',
  })
}

export async function getEvaluationResult(evaluationId) {
  return fetchAPI(`${API_BASE}/evaluation/${evaluationId}`)
}

/* ==================== AI评测助手 ==================== */
export async function sendChatMessage(sessionId, message, companyInfo) {
  return fetchAPI(`${API_BASE}/ai/chat`, {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, message, company_info: companyInfo }),
  })
}

export async function sendChatStream(sessionId, message, companyInfo, onChunk, onDone, onError) {
  const resp = await fetch(`${API_BASE}/ai/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message, company_info: companyInfo }),
  })

  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          if (data.type === 'content') onChunk(data.content)
          if (data.type === 'done') onDone(data)
        } catch (e) { /* ignore */ }
      }
    }
  }
}

export async function getConversations() {
  return fetchAPI(`${API_BASE}/ai/conversations`)
}

export async function getConversation(sessionId) {
  return fetchAPI(`${API_BASE}/ai/conversations/${sessionId}`)
}

export async function uploadDocument(file, sessionId) {
  const formData = new FormData()
  formData.append('file', file)
  if (sessionId) formData.append('session_id', sessionId)

  const response = await fetch(`${API_BASE}/ai/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `上传失败: ${response.status}`)
  }

  const result = await response.json()
  return result.data || result
}

export async function extractScores(sessionId) {
  return fetchAPI(`${API_BASE}/ai/extract-scores`, {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId }),
  })
}

export async function exportReport(sessionId, format = 'markdown') {
  return fetchAPI(`${API_BASE}/ai/export-report`, {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, format }),
  })
}

/* ==================== 企业库 ==================== */
export async function createCompany(data) {
  return fetchAPI(`${API_BASE}/companies`, { method: 'POST', body: JSON.stringify(data) })
}

export async function getCompanies(params = {}) {
  const query = new URLSearchParams(params).toString()
  return fetchAPI(`${API_BASE}/companies?${query}`)
}

export async function getCompany(id) {
  return fetchAPI(`${API_BASE}/companies/${id}`)
}

export async function updateCompany(id, data) {
  return fetchAPI(`${API_BASE}/companies/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export async function deleteCompany(id) {
  return fetchAPI(`${API_BASE}/companies/${id}`, { method: 'DELETE' })
}

export async function evaluateCompany(id, dimensionScores) {
  return fetchAPI(`${API_BASE}/companies/${id}/evaluate`, {
    method: 'POST',
    body: JSON.stringify({ dimension_scores: dimensionScores }),
  })
}

export async function getCompanyEvaluations(id) {
  return fetchAPI(`${API_BASE}/companies/${id}/evaluations`)
}

/* ==================== 知识库 ==================== */
export async function createKnowledgeDoc(data) {
  return fetchAPI(`${API_BASE}/knowledge/docs`, { method: 'POST', body: JSON.stringify(data) })
}

export async function getKnowledgeDocs(params = {}) {
  const query = new URLSearchParams(params).toString()
  return fetchAPI(`${API_BASE}/knowledge/docs?${query}`)
}

export async function getKnowledgeDoc(id) {
  return fetchAPI(`${API_BASE}/knowledge/docs/${id}`)
}

export async function queryKnowledge(data) {
  return fetchAPI(`${API_BASE}/knowledge/query`, { method: 'POST', body: JSON.stringify(data) })
}

export async function getKnowledgeCategories() {
  return fetchAPI(`${API_BASE}/knowledge/categories`)
}

/* ==================== 评测标准 ==================== */
export async function getStandards(params = {}) {
  const query = new URLSearchParams(params).toString()
  return fetchAPI(`${API_BASE}/standards?${query}`)
}

export async function getStandard(id) {
  return fetchAPI(`${API_BASE}/standards/${id}`)
}

export async function explainStandard(id) {
  return fetchAPI(`${API_BASE}/standards/${id}/explain`, { method: 'POST', body: JSON.stringify({}) })
}

export async function getDimensionsSummary() {
  return fetchAPI(`${API_BASE}/standards/dimensions/summary`)
}
