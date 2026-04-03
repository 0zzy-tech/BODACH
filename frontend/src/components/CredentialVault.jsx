import { useState } from 'react'
import { useAppStore } from '../store/appStore'

const CRED_TYPES = ['plaintext', 'hash', 'ssh_key', 'api_key', 'token', 'other']

const TYPE_LABELS = {
  plaintext: 'Password',
  hash: 'Hash',
  ssh_key: 'SSH Key',
  api_key: 'API Key',
  token: 'Token',
  other: 'Other',
}

const TYPE_COLORS = {
  plaintext: 'text-kali-green',
  hash: 'text-kali-yellow',
  ssh_key: 'text-kali-accent',
  api_key: 'text-purple-400',
  token: 'text-orange-400',
  other: 'text-kali-muted',
}

function SecretCell({ secret }) {
  const [revealed, setRevealed] = useState(false)
  return (
    <span
      className="cursor-pointer font-mono"
      onClick={() => setRevealed((x) => !x)}
      title={revealed ? 'Click to hide' : 'Click to reveal'}
    >
      {revealed ? secret : '••••••••'}
    </span>
  )
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)
  const handleCopy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }
  return (
    <button
      onClick={handleCopy}
      className="text-kali-muted hover:text-kali-accent text-xs p-0.5 transition-colors"
      title="Copy to clipboard"
    >
      {copied ? '✓' : '⎘'}
    </button>
  )
}

const EMPTY_FORM = { username: '', secret: '', cred_type: 'plaintext', service: '', host: '', notes: '' }

export default function CredentialVault() {
  const { credentials, addCredential, updateCredential, deleteCredential } = useAppStore()
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [saving, setSaving] = useState(false)

  const handleAdd = async () => {
    if (!form.secret.trim()) return
    setSaving(true)
    try {
      await addCredential(form)
      setForm(EMPTY_FORM)
      setShowAdd(false)
    } finally {
      setSaving(false)
    }
  }

  const startEdit = (c) => {
    setEditingId(c.id)
    setEditForm({ username: c.username, secret: c.secret, cred_type: c.cred_type, service: c.service, host: c.host, notes: c.notes, cracked: c.cracked })
  }

  const commitEdit = async (id) => {
    setSaving(true)
    try {
      await updateCredential(id, editForm)
      setEditingId(null)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (confirm('Delete this credential?')) await deleteCredential(id)
  }

  const toggleCracked = async (c) => {
    await updateCredential(c.id, { cracked: !c.cracked })
  }

  return (
    <div className="p-3 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-kali-muted text-xs">{credentials.length} credential{credentials.length !== 1 ? 's' : ''}</span>
        <button
          onClick={() => { setShowAdd((x) => !x); setForm(EMPTY_FORM) }}
          className="text-xs px-2 py-1 border border-kali-border rounded text-kali-muted hover:text-kali-accent hover:border-kali-accent transition-colors"
        >
          {showAdd ? '✕ Cancel' : '+ Add'}
        </button>
      </div>

      {/* Add form */}
      {showAdd && (
        <div className="border border-kali-border rounded p-3 space-y-2 bg-kali-bg text-xs">
          <div className="grid grid-cols-2 gap-2">
            <input className="col-span-2 bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text placeholder-kali-muted outline-none focus:border-kali-accent"
              placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
            <input className="col-span-2 bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text placeholder-kali-muted outline-none focus:border-kali-accent font-mono"
              placeholder="Secret / password / hash *" value={form.secret} onChange={(e) => setForm({ ...form, secret: e.target.value })} />
            <select className="bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text outline-none focus:border-kali-accent"
              value={form.cred_type} onChange={(e) => setForm({ ...form, cred_type: e.target.value })}>
              {CRED_TYPES.map((t) => <option key={t} value={t}>{TYPE_LABELS[t]}</option>)}
            </select>
            <input className="bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text placeholder-kali-muted outline-none focus:border-kali-accent"
              placeholder="Service (SSH, SMB…)" value={form.service} onChange={(e) => setForm({ ...form, service: e.target.value })} />
            <input className="col-span-2 bg-kali-surface border border-kali-border rounded px-2 py-1 text-kali-text placeholder-kali-muted outline-none focus:border-kali-accent"
              placeholder="Host / IP" value={form.host} onChange={(e) => setForm({ ...form, host: e.target.value })} />
          </div>
          <button
            onClick={handleAdd}
            disabled={saving || !form.secret.trim()}
            className="w-full bg-kali-accent hover:bg-blue-400 disabled:opacity-40 text-kali-bg font-semibold py-1 rounded transition-colors"
          >
            Save
          </button>
        </div>
      )}

      {/* Credentials list */}
      {credentials.length === 0 && !showAdd && (
        <p className="text-kali-muted text-xs text-center mt-4">
          No credentials yet — the AI will populate these automatically when credentials are discovered.
        </p>
      )}

      {credentials.map((c) => (
        <div key={c.id} className="border border-kali-border rounded p-2 space-y-1 text-xs">
          {editingId === c.id ? (
            <div className="space-y-1.5">
              <div className="grid grid-cols-2 gap-1">
                <input className="col-span-2 bg-kali-bg border border-kali-border rounded px-2 py-1 text-kali-text outline-none focus:border-kali-accent"
                  placeholder="Username" value={editForm.username} onChange={(e) => setEditForm({ ...editForm, username: e.target.value })} />
                <input className="col-span-2 bg-kali-bg border border-kali-border rounded px-2 py-1 text-kali-text outline-none focus:border-kali-accent font-mono"
                  placeholder="Secret" value={editForm.secret} onChange={(e) => setEditForm({ ...editForm, secret: e.target.value })} />
                <select className="bg-kali-bg border border-kali-border rounded px-2 py-1 text-kali-text outline-none"
                  value={editForm.cred_type} onChange={(e) => setEditForm({ ...editForm, cred_type: e.target.value })}>
                  {CRED_TYPES.map((t) => <option key={t} value={t}>{TYPE_LABELS[t]}</option>)}
                </select>
                <input className="bg-kali-bg border border-kali-border rounded px-2 py-1 text-kali-text outline-none"
                  placeholder="Service" value={editForm.service} onChange={(e) => setEditForm({ ...editForm, service: e.target.value })} />
                <input className="col-span-2 bg-kali-bg border border-kali-border rounded px-2 py-1 text-kali-text outline-none"
                  placeholder="Host" value={editForm.host} onChange={(e) => setEditForm({ ...editForm, host: e.target.value })} />
              </div>
              <div className="flex gap-2">
                <button onClick={() => commitEdit(c.id)} disabled={saving}
                  className="flex-1 bg-kali-accent hover:bg-blue-400 disabled:opacity-40 text-kali-bg font-semibold py-1 rounded">Save</button>
                <button onClick={() => setEditingId(null)}
                  className="px-3 border border-kali-border rounded text-kali-muted hover:text-kali-text">Cancel</button>
              </div>
            </div>
          ) : (
            <>
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span className="font-semibold text-kali-text">{c.username || <span className="text-kali-muted italic">no username</span>}</span>
                    <span className={`text-[10px] font-medium ${TYPE_COLORS[c.cred_type]}`}>{TYPE_LABELS[c.cred_type]}</span>
                    {c.service && <span className="text-kali-muted">· {c.service}</span>}
                    {c.host && <span className="text-kali-muted">@ {c.host}</span>}
                    {c.cred_type === 'hash' && (
                      <button
                        onClick={() => toggleCracked(c)}
                        className={`text-[10px] px-1 rounded border ${c.cracked ? 'border-kali-green text-kali-green' : 'border-kali-muted text-kali-muted hover:border-kali-accent'}`}
                        title="Toggle cracked status"
                      >
                        {c.cracked ? '✓ cracked' : 'uncracked'}
                      </button>
                    )}
                  </div>
                  <div className="flex items-center gap-1 mt-0.5 text-kali-muted font-mono">
                    <SecretCell secret={c.secret} />
                    <CopyButton text={c.secret} />
                  </div>
                </div>
                <div className="flex gap-1 shrink-0">
                  <button onClick={() => startEdit(c)} className="text-kali-muted hover:text-kali-accent p-0.5" title="Edit">✎</button>
                  <button onClick={() => handleDelete(c.id)} className="text-kali-muted hover:text-kali-red p-0.5" title="Delete">✕</button>
                </div>
              </div>
            </>
          )}
        </div>
      ))}
    </div>
  )
}
