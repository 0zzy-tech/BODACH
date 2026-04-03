import { useState } from 'react'
import { apiClient } from '../api/client'

async function triggerDownload(id, format) {
  const res = await apiClient.downloadReport(id, format)
  if (!res.ok) throw new Error(`Server returned ${res.status}`)
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  const cd = res.headers.get('Content-Disposition') || ''
  const match = cd.match(/filename="(.+?)"/)
  a.download = match ? match[1] : `report.${format === 'markdown' ? 'md' : format}`
  a.click()
  URL.revokeObjectURL(url)
}

async function triggerExport(id, format) {
  const res = await apiClient.exportSession(id, format)
  if (!res.ok) throw new Error(`Server returned ${res.status}`)
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  const cd = res.headers.get('Content-Disposition') || ''
  const match = cd.match(/filename="(.+?)"/)
  a.download = match ? match[1] : `export.${format === 'json' ? 'json' : 'txt'}`
  a.click()
  URL.revokeObjectURL(url)
}

export default function ReportModal({ sessionId, onClose }) {
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState({})

  const handle = async (key, fn) => {
    setLoading((l) => ({ ...l, [key]: true }))
    setErrors((e) => ({ ...e, [key]: null }))
    try {
      await fn()
    } catch (err) {
      setErrors((e) => ({ ...e, [key]: err.message }))
    } finally {
      setLoading((l) => ({ ...l, [key]: false }))
    }
  }

  const btn = (key, label, fn, extraClass = '') => (
    <button
      key={key}
      onClick={() => handle(key, fn)}
      disabled={!!loading[key]}
      className={`flex items-center justify-between w-full px-4 py-3 rounded border transition-colors text-sm font-medium
        ${loading[key] ? 'opacity-50 cursor-not-allowed' : 'hover:bg-kali-border'}
        border-kali-border text-kali-text ${extraClass}`}
    >
      <span>{label}</span>
      {loading[key] ? (
        <span className="text-kali-yellow text-xs animate-pulse">downloading…</span>
      ) : errors[key] ? (
        <span className="text-kali-red text-xs">{errors[key]}</span>
      ) : (
        <span className="text-kali-muted text-xs">↓</span>
      )}
    </button>
  )

  return (
    <div
      className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-kali-surface border border-kali-border rounded-lg w-full max-w-sm p-5 space-y-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-kali-text font-bold text-sm">Reports &amp; Exports</h2>
          <button onClick={onClose} className="text-kali-muted hover:text-kali-text">✕</button>
        </div>

        <div>
          <p className="text-kali-muted text-xs mb-2 uppercase tracking-wider font-semibold">Reports</p>
          <div className="space-y-2">
            {btn('html', 'Download HTML Report', () => triggerDownload(sessionId, 'html'))}
            {btn('markdown', 'Download Markdown Report', () => triggerDownload(sessionId, 'markdown'))}
            {btn('pdf', 'Download PDF Report', () => triggerDownload(sessionId, 'pdf'))}
          </div>
        </div>

        <div>
          <p className="text-kali-muted text-xs mb-2 uppercase tracking-wider font-semibold">Exports</p>
          <div className="space-y-2">
            {btn('json', 'Export Session JSON', () => triggerExport(sessionId, 'json'))}
            {btn('text', 'Export Plain Text Transcript', () => triggerExport(sessionId, 'text'))}
          </div>
        </div>
      </div>
    </div>
  )
}
