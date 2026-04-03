import { useState, useEffect } from 'react'
import { useAppStore } from '../store/appStore'

export default function TargetConfig() {
  const { activeSession, activeSessionId, updateTargetConfig } = useAppStore()
  const [form, setForm] = useState({
    ip: '',
    domain: '',
    ports: '1-65535',
    notes: '',
    scope: [],
  })
  const [scopeInput, setScopeInput] = useState('')
  const [saving, setSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState(null) // 'ok' | 'error' | null

  // Reset form when session changes
  useEffect(() => {
    const t = activeSession?.target_config
    if (t) {
      setForm({
        ip: t.ip || '',
        domain: t.domain || '',
        ports: t.ports || '1-65535',
        notes: t.notes || '',
        scope: t.scope || [],
      })
    } else {
      setForm({ ip: '', domain: '', ports: '1-65535', notes: '', scope: [] })
    }
    setSaveStatus(null)
  }, [activeSessionId])

  const handleSave = async () => {
    setSaving(true)
    setSaveStatus(null)
    try {
      await updateTargetConfig({
        ip: form.ip.trim() || null,
        domain: form.domain.trim() || null,
        ports: form.ports.trim() || '1-65535',
        notes: form.notes,
        scope: form.scope,
      })
      setSaveStatus('ok')
      setTimeout(() => setSaveStatus(null), 3000)
    } catch (e) {
      console.error('Failed to save target', e)
      setSaveStatus('error')
    } finally {
      setSaving(false)
    }
  }

  const addScope = () => {
    const v = scopeInput.trim()
    if (v && !form.scope.includes(v)) {
      setForm((f) => ({ ...f, scope: [...f.scope, v] }))
    }
    setScopeInput('')
  }

  const removeScope = (item) => {
    setForm((f) => ({ ...f, scope: f.scope.filter((s) => s !== item) }))
  }

  // Show loading state while session is being fetched
  if (activeSessionId && !activeSession) {
    return (
      <div className="p-4 text-xs text-kali-muted text-center">Loading…</div>
    )
  }

  if (!activeSession) return null

  return (
    <div className="p-3 text-xs">
      <h3 className="text-kali-muted font-semibold mb-3 uppercase tracking-wider text-xs">
        Target Configuration
      </h3>

      <div className="space-y-3">
        {/* IP Address */}
        <div>
          <label className="text-kali-muted block mb-1">IP Address</label>
          <input
            className="w-full bg-kali-bg border border-kali-border rounded px-2 py-1.5 text-kali-text outline-none focus:border-kali-accent transition-colors"
            value={form.ip}
            onChange={(e) => setForm((f) => ({ ...f, ip: e.target.value }))}
            placeholder="192.168.1.1"
            autoComplete="off"
          />
        </div>

        {/* Domain */}
        <div>
          <label className="text-kali-muted block mb-1">Domain / Host</label>
          <input
            className="w-full bg-kali-bg border border-kali-border rounded px-2 py-1.5 text-kali-text outline-none focus:border-kali-accent transition-colors"
            value={form.domain}
            onChange={(e) => setForm((f) => ({ ...f, domain: e.target.value }))}
            placeholder="target.com"
            autoComplete="off"
          />
        </div>

        {/* Port Scope */}
        <div>
          <label className="text-kali-muted block mb-1">Port Scope</label>
          <input
            className="w-full bg-kali-bg border border-kali-border rounded px-2 py-1.5 text-kali-text outline-none focus:border-kali-accent transition-colors"
            value={form.ports}
            onChange={(e) => setForm((f) => ({ ...f, ports: e.target.value }))}
            placeholder="1-65535 or 80,443,8080"
            autoComplete="off"
          />
        </div>

        {/* Authorized Scope */}
        <div>
          <label className="text-kali-muted block mb-1">Authorized Scope (CIDR)</label>
          <div className="flex gap-1 mb-1">
            <input
              className="flex-1 bg-kali-bg border border-kali-border rounded px-2 py-1 text-kali-text outline-none focus:border-kali-accent transition-colors"
              value={scopeInput}
              onChange={(e) => setScopeInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addScope()}
              placeholder="10.0.0.0/24"
              autoComplete="off"
            />
            <button
              onClick={addScope}
              className="bg-kali-border hover:bg-kali-muted text-kali-text px-3 py-1 rounded transition-colors font-bold"
            >
              +
            </button>
          </div>
          {form.scope.length === 0 && (
            <p className="text-kali-muted text-xs italic">No scope set — all targets in scope</p>
          )}
          {form.scope.map((s) => (
            <div key={s} className="flex items-center gap-1 mb-0.5 bg-kali-bg rounded px-2 py-1">
              <span className="text-kali-green text-xs">✓</span>
              <span className="text-kali-text flex-1 font-mono">{s}</span>
              <button
                onClick={() => removeScope(s)}
                className="text-kali-muted hover:text-kali-red transition-colors ml-1"
                title="Remove"
              >
                ✕
              </button>
            </div>
          ))}
        </div>

        {/* Notes */}
        <div>
          <label className="text-kali-muted block mb-1">Notes</label>
          <textarea
            className="w-full bg-kali-bg border border-kali-border rounded px-2 py-1.5 text-kali-text outline-none focus:border-kali-accent resize-none transition-colors"
            rows={4}
            value={form.notes}
            onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
            placeholder="Credentials found, interesting paths, engagement notes…"
          />
        </div>

        {/* Save button + status */}
        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full bg-kali-green/20 hover:bg-kali-green/30 border border-kali-green/40 text-kali-green font-semibold py-2 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saving ? 'Saving…' : 'Save Target'}
        </button>

        {saveStatus === 'ok' && (
          <p className="text-kali-green text-xs text-center">
            ✓ Target saved — AI will use this in its next prompt
          </p>
        )}
        {saveStatus === 'error' && (
          <p className="text-kali-red text-xs text-center">
            ✗ Failed to save — check the console for details
          </p>
        )}
      </div>
    </div>
  )
}
