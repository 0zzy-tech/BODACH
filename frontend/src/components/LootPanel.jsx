import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '../api/client'

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso) {
  return new Date(iso).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' })
}

export default function LootPanel() {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.getLoot()
      setFiles(data)
    } catch (e) {
      setError('Failed to load loot files')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleDownload = async (name) => {
    try {
      const res = await apiClient.downloadLoot(name)
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = name
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      alert('Download failed')
    }
  }

  const handleDelete = async (name) => {
    if (!confirm(`Delete ${name}?`)) return
    try {
      await apiClient.deleteLoot(name)
      setFiles((f) => f.filter((x) => x.name !== name))
    } catch (e) {
      alert('Delete failed')
    }
  }

  return (
    <div className="p-3 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="text-kali-muted text-xs">{files.length} file{files.length !== 1 ? 's' : ''}</span>
        <button
          onClick={load}
          disabled={loading}
          className="text-xs px-2 py-1 border border-kali-border rounded text-kali-muted hover:text-kali-accent hover:border-kali-accent disabled:opacity-40 transition-colors"
          title="Refresh"
        >
          ↻ Refresh
        </button>
      </div>

      {error && <p className="text-kali-red text-xs">{error}</p>}

      {!loading && files.length === 0 && !error && (
        <p className="text-kali-muted text-xs text-center mt-4">
          No loot files yet — payloads and extracted files will appear here.
        </p>
      )}

      {files.map((f) => (
        <div key={f.name} className="border border-kali-border rounded p-2 text-xs flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <p className="text-kali-text font-mono truncate" title={f.name}>{f.name}</p>
            <p className="text-kali-muted mt-0.5">{formatBytes(f.size_bytes)} · {formatDate(f.modified_at)}</p>
          </div>
          <div className="flex gap-1 shrink-0">
            <button
              onClick={() => handleDownload(f.name)}
              className="text-kali-muted hover:text-kali-accent text-xs p-0.5 transition-colors"
              title="Download"
            >
              ⬇
            </button>
            <button
              onClick={() => handleDelete(f.name)}
              className="text-kali-muted hover:text-kali-red text-xs p-0.5 transition-colors"
              title="Delete"
            >
              ✕
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
