import { useState } from 'react'
import { useAppStore } from '../store/appStore'

const EMPTY_FORM = { ip: '', hostname: '', os: '', open_ports: '', services: '', notes: '' }

function parsePorts(str) {
  return str.split(/[,\s]+/).map(Number).filter((n) => n > 0 && n < 65536)
}

function parseServices(str) {
  // Accept "80:http, 443:https" or "80/http 443/https"
  const out = {}
  str.split(/[,\n]+/).forEach((part) => {
    const m = part.trim().match(/^(\d+)[:/](\S+)$/)
    if (m) out[m[1]] = m[2]
  })
  return out
}

export default function AssetInventory() {
  const { assets, addAsset, updateAsset, deleteAsset } = useAppStore()
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [saving, setSaving] = useState(false)
  const [expanded, setExpanded] = useState(null)

  const handleAdd = async () => {
    if (!form.ip.trim()) return
    setSaving(true)
    try {
      await addAsset({
        ip: form.ip.trim(),
        hostname: form.hostname.trim(),
        os: form.os.trim(),
        open_ports: form.open_ports ? parsePorts(form.open_ports) : [],
        services: form.services ? parseServices(form.services) : {},
        notes: form.notes.trim(),
      })
      setForm(EMPTY_FORM)
      setShowAdd(false)
    } finally {
      setSaving(false)
    }
  }

  const startEdit = (a) => {
    setEditingId(a.id)
    setEditForm({
      ip: a.ip,
      hostname: a.hostname,
      os: a.os,
      open_ports: a.open_ports.join(', '),
      services: Object.entries(a.services).map(([p, s]) => `${p}:${s}`).join(', '),
      notes: a.notes,
    })
  }

  const commitEdit = async (id) => {
    setSaving(true)
    try {
      await updateAsset(id, {
        ip: editForm.ip.trim(),
        hostname: editForm.hostname.trim(),
        os: editForm.os.trim(),
        open_ports: editForm.open_ports ? parsePorts(editForm.open_ports) : [],
        services: editForm.services ? parseServices(editForm.services) : {},
        notes: editForm.notes.trim(),
      })
      setEditingId(null)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (confirm('Delete this asset?')) await deleteAsset(id)
  }

  return (
    <div className="p-3 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="text-kali-muted text-xs">{assets.length} host{assets.length !== 1 ? 's' : ''}</span>
        <button
          onClick={() => { setShowAdd((x) => !x); setForm(EMPTY_FORM) }}
          className="text-xs px-2 py-1 border border-kali-border rounded text-kali-muted hover:text-kali-accent hover:border-kali-accent transition-colors"
        >
          {showAdd ? '✕ Cancel' : '+ Add'}
        </button>
      </div>

      {/* Add form */}
      {showAdd && (
        <div className="border border-kali-border rounded p-3 space-y-1.5 bg-kali-bg text-xs">
          <div className="grid grid-cols-2 gap-1.5">
            <input className="col-span-2 bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text placeholder-kali-muted outline-none focus:border-kali-accent"
              placeholder="IP address *" value={form.ip} onChange={(e) => setForm({ ...form, ip: e.target.value })} />
            <input className="bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text placeholder-kali-muted outline-none focus:border-kali-accent"
              placeholder="Hostname" value={form.hostname} onChange={(e) => setForm({ ...form, hostname: e.target.value })} />
            <input className="bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text placeholder-kali-muted outline-none focus:border-kali-accent"
              placeholder="OS (e.g. Linux)" value={form.os} onChange={(e) => setForm({ ...form, os: e.target.value })} />
            <input className="col-span-2 bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text placeholder-kali-muted outline-none focus:border-kali-accent"
              placeholder="Ports: 22, 80, 443" value={form.open_ports} onChange={(e) => setForm({ ...form, open_ports: e.target.value })} />
            <input className="col-span-2 bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text placeholder-kali-muted outline-none focus:border-kali-accent"
              placeholder="Services: 22:ssh, 80:http" value={form.services} onChange={(e) => setForm({ ...form, services: e.target.value })} />
          </div>
          <button onClick={handleAdd} disabled={saving || !form.ip.trim()}
            className="w-full bg-kali-accent hover:bg-blue-400 disabled:opacity-40 text-kali-bg font-semibold py-1 rounded transition-colors">
            Save
          </button>
        </div>
      )}

      {assets.length === 0 && !showAdd && (
        <p className="text-kali-muted text-xs text-center mt-4">
          No assets yet — hosts will appear automatically as the AI discovers them.
        </p>
      )}

      {assets.map((a) => (
        <div key={a.id} className="border border-kali-border rounded text-xs">
          {editingId === a.id ? (
            <div className="p-2 space-y-1.5">
              <div className="grid grid-cols-2 gap-1">
                <input className="col-span-2 bg-kali-bg border border-kali-border rounded px-2 py-1 text-kali-text outline-none"
                  placeholder="IP *" value={editForm.ip} onChange={(e) => setEditForm({ ...editForm, ip: e.target.value })} />
                <input className="bg-kali-bg border border-kali-border rounded px-2 py-1 text-kali-text outline-none"
                  placeholder="Hostname" value={editForm.hostname} onChange={(e) => setEditForm({ ...editForm, hostname: e.target.value })} />
                <input className="bg-kali-bg border border-kali-border rounded px-2 py-1 text-kali-text outline-none"
                  placeholder="OS" value={editForm.os} onChange={(e) => setEditForm({ ...editForm, os: e.target.value })} />
                <input className="col-span-2 bg-kali-bg border border-kali-border rounded px-2 py-1 text-kali-text outline-none"
                  placeholder="Ports" value={editForm.open_ports} onChange={(e) => setEditForm({ ...editForm, open_ports: e.target.value })} />
                <input className="col-span-2 bg-kali-bg border border-kali-border rounded px-2 py-1 text-kali-text outline-none"
                  placeholder="Services (22:ssh, 80:http)" value={editForm.services} onChange={(e) => setEditForm({ ...editForm, services: e.target.value })} />
              </div>
              <div className="flex gap-2">
                <button onClick={() => commitEdit(a.id)} disabled={saving}
                  className="flex-1 bg-kali-accent hover:bg-blue-400 disabled:opacity-40 text-kali-bg font-semibold py-1 rounded">Save</button>
                <button onClick={() => setEditingId(null)}
                  className="px-3 border border-kali-border rounded text-kali-muted hover:text-kali-text">Cancel</button>
              </div>
            </div>
          ) : (
            <div>
              {/* Header row */}
              <div
                className="flex items-center gap-2 px-2 py-1.5 cursor-pointer hover:bg-kali-border transition-colors"
                onClick={() => setExpanded(expanded === a.id ? null : a.id)}
              >
                <span className="font-mono font-semibold text-kali-accent">{a.ip}</span>
                {a.hostname && <span className="text-kali-muted">({a.hostname})</span>}
                {a.os && <span className="text-kali-yellow text-[10px]">{a.os}</span>}
                {a.open_ports.length > 0 && (
                  <span className="ml-auto text-kali-muted text-[10px]">{a.open_ports.length} port{a.open_ports.length !== 1 ? 's' : ''}</span>
                )}
                <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                  <button onClick={() => startEdit(a)} className="text-kali-muted hover:text-kali-accent p-0.5">✎</button>
                  <button onClick={() => handleDelete(a.id)} className="text-kali-muted hover:text-kali-red p-0.5">✕</button>
                </div>
              </div>

              {/* Expanded detail */}
              {expanded === a.id && (
                <div className="border-t border-kali-border px-2 py-1.5 space-y-1 bg-kali-bg">
                  {a.open_ports.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {a.open_ports.map((p) => (
                        <span key={p} className="px-1.5 py-0.5 bg-kali-surface border border-kali-border rounded font-mono text-[10px] text-kali-text">
                          {p}{a.services[String(p)] ? `/${a.services[String(p)]}` : ''}
                        </span>
                      ))}
                    </div>
                  )}
                  {a.notes && <p className="text-kali-muted">{a.notes}</p>}
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
