const BASE = '/api/v1'

async function req(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body !== undefined) opts.body = JSON.stringify(body)
  const res = await fetch(BASE + path, opts)
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${method} ${path} → ${res.status}: ${text}`)
  }
  if (res.status === 204) return null
  return res.json()
}

export const apiClient = {
  getSessions: () => req('GET', '/sessions'),
  createSession: (name) => req('POST', '/sessions', { name }),
  getSession: (id) => req('GET', `/sessions/${id}`),
  deleteSession: (id) => req('DELETE', `/sessions/${id}`),
  renameSession: (id, name) => req('PATCH', `/sessions/${id}/name`, { name }),
  updateTarget: (id, target) => req('PUT', `/sessions/${id}/target`, target),

  getOllamaConfig: () => req('GET', '/config/ollama'),
  updateOllamaConfig: (base_url, api_key, model) => req('PUT', '/config/ollama', { base_url, api_key, model }),
  testOllamaConnection: (base_url, api_key) => req('POST', '/config/ollama/test', { base_url, api_key }),
  listTools: () => req('GET', '/config/tools'),

  // Findings
  getFindings: (id) => req('GET', `/sessions/${id}/findings`),
  addFinding: (id, data) => req('POST', `/sessions/${id}/findings`, data),
  updateFinding: (id, fid, data) => req('PUT', `/sessions/${id}/findings/${fid}`, data),
  deleteFinding: (id, fid) => req('DELETE', `/sessions/${id}/findings/${fid}`),

  // Reports & exports (return raw Response for blob download)
  downloadReport: (id, format) => fetch(`${BASE}/sessions/${id}/report?format=${format}`),
  exportSession: (id, format) => fetch(`${BASE}/sessions/${id}/export?format=${format}`),

  // Credentials
  getCredentials: (id) => req('GET', `/sessions/${id}/credentials`),
  addCredential: (id, data) => req('POST', `/sessions/${id}/credentials`, data),
  updateCredential: (id, cid, data) => req('PUT', `/sessions/${id}/credentials/${cid}`, data),
  deleteCredential: (id, cid) => req('DELETE', `/sessions/${id}/credentials/${cid}`),

  // Loot
  getLoot: () => req('GET', '/loot'),
  deleteLoot: (name) => req('DELETE', `/loot/${encodeURIComponent(name)}`),
  downloadLoot: (name) => fetch(`${BASE}/loot/${encodeURIComponent(name)}`),

  // Notes
  updateNotes: (id, notes) => req('PATCH', `/sessions/${id}/notes`, { notes }),

  // Assets
  getAssets: (id) => req('GET', `/sessions/${id}/assets`),
  addAsset: (id, data) => req('POST', `/sessions/${id}/assets`, data),
  updateAsset: (id, aid, data) => req('PUT', `/sessions/${id}/assets/${aid}`, data),
  deleteAsset: (id, aid) => req('DELETE', `/sessions/${id}/assets/${aid}`),
}
