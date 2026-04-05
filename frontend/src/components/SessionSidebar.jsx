import { useState } from 'react'
import { useAppStore } from '../store/appStore'
import OllamaConfig from './OllamaConfig'
import ReportModal from './ReportModal'

function AboutModal({ onClose }) {
  return (
    <div
      className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-kali-surface border border-kali-border rounded-lg w-full max-w-sm p-6 text-center space-y-4"
        onClick={(e) => e.stopPropagation()}
      >
        <p className="text-6xl">⚔</p>
        <div>
          <h2 className="text-kali-text font-bold text-lg tracking-wider">BODACH</h2>
          <p className="text-kali-muted text-xs mt-1">The Scottish Boogieman</p>
          <p className="text-kali-accent text-xs font-semibold mt-0.5">Agentic AI red team assistant</p>
        </div>
        <div className="border-t border-kali-border pt-4 space-y-1">
          <p className="text-kali-muted text-xs">Made for education purposes by</p>
          <p className="text-kali-text font-semibold text-sm">Ozzytech</p>
        </div>
        <button
          onClick={onClose}
          className="mt-2 px-4 py-1.5 border border-kali-border rounded text-kali-muted hover:text-kali-text text-xs transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  )
}

export default function SessionSidebar() {
  const { sessions, activeSessionId, createSession, deleteSession, setActiveSession, renameSession, theme, toggleTheme } = useAppStore()
  const [editingId, setEditingId] = useState(null)
  const [editName, setEditName] = useState('')
  const [reportSessionId, setReportSessionId] = useState(null)
  const [showAbout, setShowAbout] = useState(false)

  const handleCreate = () => createSession()

  const startRename = (e, session) => {
    e.stopPropagation()
    setEditingId(session.id)
    setEditName(session.name)
  }

  const commitRename = (id) => {
    if (editName.trim()) renameSession(id, editName.trim())
    setEditingId(null)
  }

  const handleDelete = (e, id) => {
    e.stopPropagation()
    if (confirm('Delete this session?')) deleteSession(id)
  }

  return (
    <aside className="w-64 flex flex-col bg-kali-surface border-r border-kali-border shrink-0">
      {/* Header */}
      <div className="p-4 border-b border-kali-border">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-kali-red font-bold text-2xl">⚔</span>
          <span className="text-kali-text font-bold text-sm tracking-wider">BODACH</span>
        </div>
        <button
          onClick={handleCreate}
          className="w-full bg-kali-accent hover:bg-blue-400 text-kali-bg font-semibold text-xs py-2 px-3 rounded transition-colors"
        >
          + New Session
        </button>
      </div>

      {/* Session list */}
      <div className="flex-1 overflow-y-auto py-2">
        {sessions.length === 0 && (
          <p className="text-kali-muted text-xs px-4 py-2">No sessions yet</p>
        )}
        {sessions.map((s) => (
          <div
            key={s.id}
            onClick={() => setActiveSession(s.id)}
            className={`group flex items-start gap-2 px-3 py-2 cursor-pointer hover:bg-kali-border transition-colors ${
              s.id === activeSessionId ? 'bg-kali-border border-l-2 border-kali-accent' : 'border-l-2 border-transparent'
            }`}
          >
            <div className="flex-1 min-w-0">
              {editingId === s.id ? (
                <input
                  className="w-full bg-kali-bg border border-kali-accent rounded px-1 text-xs text-kali-text outline-none"
                  value={editName}
                  autoFocus
                  onChange={(e) => setEditName(e.target.value)}
                  onBlur={() => commitRename(s.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') commitRename(s.id)
                    if (e.key === 'Escape') setEditingId(null)
                  }}
                  onClick={(e) => e.stopPropagation()}
                />
              ) : (
                <div className="flex items-center gap-1.5">
                  <p className="text-xs text-kali-text truncate font-medium">{s.name}</p>
                  {s.highest_severity === 'critical' && <span className="shrink-0 text-[10px] font-bold text-white bg-red-600 rounded px-1 leading-tight">CRIT</span>}
                  {s.highest_severity === 'high' && <span className="shrink-0 text-[10px] font-bold text-white bg-orange-500 rounded px-1 leading-tight">HIGH</span>}
                  {s.highest_severity === 'medium' && <span className="shrink-0 text-[10px] font-bold text-black bg-yellow-400 rounded px-1 leading-tight">MED</span>}
                  {s.highest_severity === 'low' && <span className="shrink-0 text-[10px] font-bold text-white bg-blue-500 rounded px-1 leading-tight">LOW</span>}
                </div>
              )}
              {(s.target_ip || s.target_domain) && (
                <p className="text-xs text-kali-muted truncate">
                  {s.target_ip || s.target_domain}
                </p>
              )}
              <p className="text-xs text-kali-muted">{s.message_count} msgs</p>
            </div>
            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={(e) => { e.stopPropagation(); setReportSessionId(s.id) }}
                className="text-kali-muted hover:text-kali-accent text-xs p-0.5"
                title="Report / Export"
              >
                ⬇
              </button>
              <button
                onClick={(e) => startRename(e, s)}
                className="text-kali-muted hover:text-kali-accent text-xs p-0.5"
                title="Rename"
              >
                ✎
              </button>
              <button
                onClick={(e) => handleDelete(e, s.id)}
                className="text-kali-muted hover:text-kali-red text-xs p-0.5"
                title="Delete"
              >
                ✕
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Ollama config at bottom */}
      <OllamaConfig />

      {/* Footer: theme toggle + about */}
      <div className="border-t border-kali-border px-4 py-2 flex items-center justify-between">
        <button
          onClick={toggleTheme}
          className="text-kali-muted hover:text-kali-accent text-xs transition-colors"
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? '☀ Light' : '☾ Dark'}
        </button>
        <button
          onClick={() => setShowAbout(true)}
          className="text-kali-muted hover:text-kali-accent text-xs transition-colors"
        >
          About
        </button>
      </div>

      {/* Modals */}
      {reportSessionId && (
        <ReportModal sessionId={reportSessionId} onClose={() => setReportSessionId(null)} />
      )}
      {showAbout && <AboutModal onClose={() => setShowAbout(false)} />}
    </aside>
  )
}
