import { useState, useEffect, useRef, useMemo } from 'react'
import { useAppStore } from '../store/appStore'

const STATIC_COMMANDS = [
  { id: 'new-session', label: 'New Session', icon: '+', action: 'createSession' },
  { id: 'toggle-theme', label: 'Toggle Light/Dark Theme', icon: '◑', action: 'toggleTheme' },
  { id: 'focus-chat', label: 'Focus Chat Input', icon: '✎', action: 'focusChat' },
]

export default function CommandPalette({ onClose }) {
  const { sessions, setActiveSession, createSession, toggleTheme } = useAppStore()
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState(0)
  const inputRef = useRef(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const sessionCommands = useMemo(() => {
    return sessions.map((s) => ({
      id: `session-${s.id}`,
      label: s.name,
      icon: '⚡',
      action: 'switchSession',
      sessionId: s.id,
    }))
  }, [sessions])

  const allCommands = [...STATIC_COMMANDS, ...sessionCommands]

  const filtered = useMemo(() => {
    if (!query.trim()) return allCommands
    const q = query.toLowerCase()
    return allCommands.filter((c) => c.label.toLowerCase().includes(q))
  }, [query, allCommands])

  const handleSelect = (cmd) => {
    if (cmd.action === 'createSession') {
      createSession()
    } else if (cmd.action === 'toggleTheme') {
      toggleTheme()
    } else if (cmd.action === 'focusChat') {
      document.getElementById('chat-input')?.focus()
    } else if (cmd.action === 'switchSession') {
      setActiveSession(cmd.sessionId)
    }
    onClose()
  }

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelected((s) => Math.min(s + 1, filtered.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelected((s) => Math.max(s - 1, 0))
    } else if (e.key === 'Enter') {
      if (filtered[selected]) handleSelect(filtered[selected])
    } else if (e.key === 'Escape') {
      onClose()
    }
  }

  // Reset selection when filter changes
  useEffect(() => {
    setSelected(0)
  }, [query])

  return (
    <div className="fixed inset-0 bg-black/60 flex items-start justify-center pt-[15vh] z-50" onClick={onClose}>
      <div
        className="bg-kali-surface border border-kali-border rounded-lg w-[480px] shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 px-4 py-3 border-b border-kali-border">
          <span className="text-kali-muted text-sm">⌘</span>
          <input
            ref={inputRef}
            className="flex-1 bg-transparent text-kali-text outline-none placeholder-kali-muted text-sm"
            placeholder="Type a command or session name…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <kbd className="text-xs text-kali-muted border border-kali-border rounded px-1.5 py-0.5">ESC</kbd>
        </div>

        <div className="max-h-72 overflow-y-auto">
          {filtered.length === 0 ? (
            <p className="text-kali-muted text-xs text-center py-6">No commands match</p>
          ) : (
            filtered.map((cmd, i) => (
              <button
                key={cmd.id}
                className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors ${
                  i === selected ? 'bg-kali-accent/20 text-kali-text' : 'text-kali-muted hover:bg-kali-bg hover:text-kali-text'
                }`}
                onClick={() => handleSelect(cmd)}
                onMouseEnter={() => setSelected(i)}
              >
                <span className="text-kali-muted w-4 text-center shrink-0">{cmd.icon}</span>
                <span>{cmd.label}</span>
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
