import { useEffect, useRef, useState } from 'react'
import { useAppStore } from '../store/appStore'

export default function NotesPanel() {
  const { notes, updateNotes, activeSessionId } = useAppStore()
  const [localNotes, setLocalNotes] = useState(notes)
  const [saved, setSaved] = useState(true)
  const debounceRef = useRef(null)

  // Sync when session switches
  useEffect(() => {
    setLocalNotes(notes)
    setSaved(true)
  }, [activeSessionId, notes])

  const handleChange = (e) => {
    const val = e.target.value
    setLocalNotes(val)
    setSaved(false)
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(async () => {
      await updateNotes(val)
      setSaved(true)
    }, 800)
  }

  return (
    <div className="flex flex-col h-full p-3 gap-2">
      <div className="flex items-center justify-between">
        <span className="text-kali-muted text-xs">{localNotes.length} chars</span>
        <span className={`text-xs transition-colors ${saved ? 'text-kali-green' : 'text-kali-yellow animate-pulse'}`}>
          {saved ? '✓ saved' : 'saving…'}
        </span>
      </div>
      <textarea
        className="flex-1 bg-kali-bg border border-kali-border rounded p-3 text-xs text-kali-text outline-none focus:border-kali-accent resize-none placeholder-kali-muted leading-relaxed"
        placeholder="Operator notes — hypotheses, planning, observations, attack paths…"
        value={localNotes}
        onChange={handleChange}
      />
    </div>
  )
}
