import { useState } from 'react'
import { useAppStore } from '../store/appStore'

const SEVERITIES = ['critical', 'high', 'medium', 'low', 'info']

const SEVERITY_STYLES = {
  critical: 'bg-red-900/50 text-red-300 border-red-700',
  high:     'bg-orange-900/50 text-orange-300 border-orange-700',
  medium:   'bg-yellow-900/50 text-yellow-300 border-yellow-700',
  low:      'bg-blue-900/50 text-blue-300 border-blue-700',
  info:     'bg-gray-700/50 text-gray-300 border-gray-600',
}

const SEVERITY_ORDER = { critical: 0, high: 1, medium: 2, low: 3, info: 4 }

const EMPTY_FORM = { title: '', severity: 'high', description: '', evidence: '', recommendation: '' }

function SeverityBadge({ severity }) {
  return (
    <span className={`text-xs px-1.5 py-0.5 rounded border font-semibold uppercase ${SEVERITY_STYLES[severity] || SEVERITY_STYLES.info}`}>
      {severity}
    </span>
  )
}

function FindingForm({ initial = EMPTY_FORM, onSave, onCancel }) {
  const [form, setForm] = useState(initial)
  const [expanded, setExpanded] = useState(false)

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  return (
    <div className="border border-kali-border rounded p-3 bg-kali-bg text-xs space-y-2">
      <input
        className="w-full bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text outline-none focus:border-kali-accent placeholder-kali-muted"
        placeholder="Title *"
        value={form.title}
        onChange={(e) => set('title', e.target.value)}
      />
      <select
        className="w-full bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text outline-none focus:border-kali-accent"
        value={form.severity}
        onChange={(e) => set('severity', e.target.value)}
      >
        {SEVERITIES.map((s) => (
          <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
        ))}
      </select>
      <textarea
        className="w-full bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text outline-none focus:border-kali-accent placeholder-kali-muted resize-none"
        placeholder="Description *"
        rows={3}
        value={form.description}
        onChange={(e) => set('description', e.target.value)}
      />
      <button
        onClick={() => setExpanded((x) => !x)}
        className="text-kali-muted hover:text-kali-text"
      >
        {expanded ? '▲ Hide' : '▼ Evidence & Recommendation'}
      </button>
      {expanded && (
        <>
          <textarea
            className="w-full bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text outline-none focus:border-kali-accent placeholder-kali-muted resize-none font-mono"
            placeholder="Evidence (optional)"
            rows={3}
            value={form.evidence}
            onChange={(e) => set('evidence', e.target.value)}
          />
          <textarea
            className="w-full bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text outline-none focus:border-kali-accent placeholder-kali-muted resize-none"
            placeholder="Recommendation (optional)"
            rows={2}
            value={form.recommendation}
            onChange={(e) => set('recommendation', e.target.value)}
          />
        </>
      )}
      <div className="flex gap-2 justify-end">
        <button
          onClick={onCancel}
          className="px-3 py-1 text-kali-muted hover:text-kali-text border border-kali-border rounded transition-colors"
        >
          Cancel
        </button>
        <button
          onClick={() => {
            if (!form.title.trim() || !form.description.trim()) return
            onSave(form)
          }}
          className="px-3 py-1 bg-kali-accent hover:bg-blue-400 text-kali-bg font-semibold rounded transition-colors"
        >
          Save
        </button>
      </div>
    </div>
  )
}

export default function FindingsPanel() {
  const { findings, addFinding, updateFinding, deleteFinding } = useAppStore()
  const [showAdd, setShowAdd] = useState(false)
  const [editingId, setEditingId] = useState(null)

  const sorted = [...findings].sort(
    (a, b) => (SEVERITY_ORDER[a.severity] ?? 99) - (SEVERITY_ORDER[b.severity] ?? 99)
  )

  const handleAdd = async (form) => {
    try {
      await addFinding(form)
      setShowAdd(false)
    } catch (_) {}
  }

  const handleUpdate = async (id, form) => {
    try {
      await updateFinding(id, form)
      setEditingId(null)
    } catch (_) {}
  }

  return (
    <div className="p-3 space-y-3 text-xs">
      <div className="flex items-center justify-between">
        <span className="text-kali-muted font-semibold uppercase tracking-wider">
          Findings ({findings.length})
        </span>
        {!showAdd && (
          <button
            onClick={() => setShowAdd(true)}
            className="text-kali-accent hover:text-blue-300 font-semibold"
          >
            + Add Finding
          </button>
        )}
      </div>

      {showAdd && (
        <FindingForm
          onSave={handleAdd}
          onCancel={() => setShowAdd(false)}
        />
      )}

      {sorted.length === 0 && !showAdd && (
        <p className="text-kali-muted text-center py-6">
          No findings yet — add manually or ask the AI to summarise vulnerabilities found.
        </p>
      )}

      {sorted.map((f) => (
        <div key={f.id} className="border border-kali-border rounded">
          {editingId === f.id ? (
            <FindingForm
              initial={{ title: f.title, severity: f.severity, description: f.description, evidence: f.evidence, recommendation: f.recommendation }}
              onSave={(form) => handleUpdate(f.id, form)}
              onCancel={() => setEditingId(null)}
            />
          ) : (
            <div className="p-3">
              <div className="flex items-start justify-between gap-2 mb-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <SeverityBadge severity={f.severity} />
                  <span className="text-kali-text font-semibold">{f.title}</span>
                </div>
                <div className="flex gap-1 shrink-0">
                  <button
                    onClick={() => setEditingId(f.id)}
                    className="text-kali-muted hover:text-kali-accent p-0.5"
                    title="Edit"
                  >
                    ✎
                  </button>
                  <button
                    onClick={() => {
                      if (confirm('Delete this finding?')) deleteFinding(f.id)
                    }}
                    className="text-kali-muted hover:text-kali-red p-0.5"
                    title="Delete"
                  >
                    ✕
                  </button>
                </div>
              </div>
              <p className="text-kali-muted leading-relaxed">{f.description}</p>
              {f.evidence && (
                <pre className="mt-2 bg-kali-bg border border-kali-border rounded p-2 text-kali-text font-mono text-xs overflow-x-auto whitespace-pre-wrap">
                  {f.evidence}
                </pre>
              )}
              {f.recommendation && (
                <p className="mt-2 text-kali-accent">
                  <span className="font-semibold">Fix: </span>{f.recommendation}
                </p>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
