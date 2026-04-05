import { useState, useMemo } from 'react'
import { useAppStore } from '../store/appStore'

const SEVERITIES = ['critical', 'high', 'medium', 'low', 'info']

const SEVERITY_STYLES = {
  critical: 'bg-red-900/50 text-red-300 border-red-700',
  high:     'bg-orange-900/50 text-orange-300 border-orange-700',
  medium:   'bg-yellow-900/50 text-yellow-300 border-yellow-700',
  low:      'bg-blue-900/50 text-blue-300 border-blue-700',
  info:     'bg-gray-700/50 text-gray-300 border-gray-600',
}

const STATUS_STYLES = {
  open:          'bg-red-900/40 text-red-300',
  in_progress:   'bg-yellow-900/40 text-yellow-300',
  resolved:      'bg-green-900/40 text-green-300',
  risk_accepted: 'bg-gray-700/40 text-gray-400',
}

const STATUS_LABELS = {
  open: 'Open',
  in_progress: 'In Progress',
  resolved: 'Resolved',
  risk_accepted: 'Risk Accepted',
}

const SEVERITY_ORDER = { critical: 0, high: 1, medium: 2, low: 3, info: 4 }

const SEVERITY_PILL_STYLES = {
  critical: 'bg-red-900/60 text-red-300',
  high:     'bg-orange-900/60 text-orange-300',
  medium:   'bg-yellow-900/60 text-yellow-300',
  low:      'bg-blue-900/60 text-blue-300',
  info:     'bg-gray-700/60 text-gray-400',
}

const EMPTY_FORM = { title: '', severity: 'high', description: '', evidence: '', recommendation: '' }

function SeverityBadge({ severity }) {
  return (
    <span className={`text-xs px-1.5 py-0.5 rounded border font-semibold uppercase ${SEVERITY_STYLES[severity] || SEVERITY_STYLES.info}`}>
      {severity}
    </span>
  )
}

function CvssBadge({ cvss }) {
  if (cvss == null) return null
  const color = cvss >= 9 ? 'text-red-400' : cvss >= 7 ? 'text-orange-400' : cvss >= 4 ? 'text-yellow-400' : 'text-blue-400'
  return (
    <span className={`text-xs font-mono font-semibold ${color}`} title="CVSS 3.1 Base Score">
      {cvss.toFixed(1)}
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
  const { findings, addFinding, updateFinding, deleteFinding, patchFinding } = useAppStore()
  const [showAdd, setShowAdd] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [search, setSearch] = useState('')
  const [filterSeverity, setFilterSeverity] = useState('all')
  const [sortMode, setSortMode] = useState('severity') // severity | newest

  // Severity summary counts
  const counts = useMemo(() => {
    const c = { critical: 0, high: 0, medium: 0, low: 0, info: 0 }
    for (const f of findings) {
      if (c[f.severity] !== undefined) c[f.severity]++
    }
    return c
  }, [findings])

  const filtered = useMemo(() => {
    let list = [...findings]
    if (filterSeverity !== 'all') list = list.filter((f) => f.severity === filterSeverity)
    if (search.trim()) {
      const q = search.toLowerCase()
      list = list.filter((f) =>
        f.title.toLowerCase().includes(q) ||
        f.description.toLowerCase().includes(q)
      )
    }
    if (sortMode === 'severity') {
      list.sort((a, b) => (SEVERITY_ORDER[a.severity] ?? 99) - (SEVERITY_ORDER[b.severity] ?? 99))
    } else {
      list.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    }
    return list
  }, [findings, filterSeverity, search, sortMode])

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
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="text-kali-muted font-semibold uppercase tracking-wider">
          Findings ({findings.length})
        </span>
        {!showAdd && (
          <button
            onClick={() => setShowAdd(true)}
            className="text-kali-accent hover:text-blue-300 font-semibold"
          >
            + Add
          </button>
        )}
      </div>

      {/* Severity summary */}
      {findings.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {SEVERITIES.map((s) => counts[s] > 0 && (
            <button
              key={s}
              onClick={() => setFilterSeverity(filterSeverity === s ? 'all' : s)}
              className={`px-2 py-0.5 rounded text-xs font-semibold transition-opacity ${SEVERITY_PILL_STYLES[s]} ${filterSeverity !== 'all' && filterSeverity !== s ? 'opacity-40' : ''}`}
            >
              {s.toUpperCase().slice(0, 4)}: {counts[s]}
            </button>
          ))}
        </div>
      )}

      {/* Search & sort controls */}
      {findings.length > 0 && (
        <div className="flex gap-2">
          <input
            className="flex-1 bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text outline-none focus:border-kali-accent placeholder-kali-muted text-xs"
            placeholder="Search findings…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select
            className="bg-kali-surface border border-kali-border rounded px-1.5 py-1 text-kali-text outline-none focus:border-kali-accent text-xs"
            value={sortMode}
            onChange={(e) => setSortMode(e.target.value)}
          >
            <option value="severity">By severity</option>
            <option value="newest">Newest first</option>
          </select>
        </div>
      )}

      {showAdd && (
        <FindingForm
          onSave={handleAdd}
          onCancel={() => setShowAdd(false)}
        />
      )}

      {filtered.length === 0 && !showAdd && (
        <p className="text-kali-muted text-center py-6">
          {findings.length === 0
            ? 'No findings yet — add manually or ask the AI to summarise vulnerabilities found.'
            : 'No findings match your filter.'}
        </p>
      )}

      {filtered.map((f) => (
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
                  <CvssBadge cvss={f.cvss} />
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

              {/* Status dropdown */}
              <div className="mb-2">
                <select
                  className={`text-xs px-2 py-0.5 rounded border-0 outline-none cursor-pointer font-semibold ${STATUS_STYLES[f.status] || STATUS_STYLES.open}`}
                  value={f.status || 'open'}
                  onChange={(e) => patchFinding(f.id, { status: e.target.value })}
                >
                  {Object.entries(STATUS_LABELS).map(([v, label]) => (
                    <option key={v} value={v}>{label}</option>
                  ))}
                </select>
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
