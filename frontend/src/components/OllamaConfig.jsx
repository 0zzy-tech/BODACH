import { useState, useEffect } from 'react'
import { useAppStore } from '../store/appStore'
import { apiClient } from '../api/client'

// Models known to support native tool/function calling
const TOOL_CALLING_MODELS = new Set([
  'llama3.1', 'llama3.1:8b', 'llama3.1:70b', 'llama3.1:405b',
  'llama3.2', 'llama3.2:1b', 'llama3.2:3b',
  'qwen2.5', 'qwen2.5:7b', 'qwen2.5:14b', 'qwen2.5:32b', 'qwen2.5:72b',
  'qwen2.5-coder', 'qwen2.5-coder:7b', 'qwen2.5-coder:32b',
  'mistral-nemo', 'mistral-small',
  'firefunction-v2',
])

function modelSupportsTools(name) {
  const base = name.split(':')[0]
  return TOOL_CALLING_MODELS.has(name) || TOOL_CALLING_MODELS.has(base)
}

function ModelRow({ name, selected, onSelect }) {
  const hasTools = modelSupportsTools(name)
  return (
    <button
      onClick={() => onSelect(name)}
      className={`w-full flex items-center gap-3 px-3 py-2 rounded text-left text-xs transition-colors ${
        selected
          ? 'bg-kali-accent/20 border border-kali-accent/50 text-kali-text'
          : 'hover:bg-kali-border text-kali-muted hover:text-kali-text border border-transparent'
      }`}
    >
      <span className={`w-2 h-2 rounded-full shrink-0 ${selected ? 'bg-kali-accent' : 'bg-kali-border'}`} />
      <span className="flex-1 font-mono">{name}</span>
      {hasTools && (
        <span className="text-kali-green text-xs shrink-0" title="Supports tool calling">
          ⚡ tools
        </span>
      )}
    </button>
  )
}

export default function OllamaConfig() {
  const { ollamaConfig, saveOllamaConfig } = useAppStore()

  const [open, setOpen] = useState(false)
  const [url, setUrl] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [model, setModel] = useState('')
  const [showKey, setShowKey] = useState(false)

  // Inline fetch state
  const [fetchedModels, setFetchedModels] = useState([])
  const [fetching, setFetching] = useState(false)
  const [fetchStatus, setFetchStatus] = useState(null) // {ok, message}
  const [modelSearch, setModelSearch] = useState('')

  // Saving state
  const [saving, setSaving] = useState(false)

  const handleOpen = () => {
    setUrl(ollamaConfig.baseUrl || 'https://ollama.com')
    setApiKey('')
    setModel(ollamaConfig.model || 'llama3.1')
    setFetchedModels(ollamaConfig.availableModels || [])
    setFetchStatus(
      ollamaConfig.connected
        ? { ok: true, message: ollamaConfig.statusMessage }
        : null
    )
    setModelSearch('')
    setOpen(true)
  }

  const handleFetchModels = async () => {
    if (!url.trim()) return
    setFetching(true)
    setFetchStatus(null)
    try {
      const result = await apiClient.testOllamaConnection(url.trim(), apiKey.trim())
      setFetchStatus({ ok: result.connected, message: result.status_message })
      if (result.connected && result.available_models.length > 0) {
        setFetchedModels(result.available_models)
        // Auto-select first tool-calling model if current selection isn't in the list
        if (!result.available_models.includes(model)) {
          const first = result.available_models.find(modelSupportsTools) || result.available_models[0]
          setModel(first)
        }
      }
    } catch (e) {
      setFetchStatus({ ok: false, message: String(e) })
    } finally {
      setFetching(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    await saveOllamaConfig(url.trim(), apiKey.trim(), model.trim())
    setSaving(false)
    setOpen(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleFetchModels()
  }

  const visibleModels = fetchedModels.filter((m) =>
    m.toLowerCase().includes(modelSearch.toLowerCase())
  )

  // Split models into tool-supporting and other
  const toolModels = visibleModels.filter(modelSupportsTools)
  const otherModels = visibleModels.filter((m) => !modelSupportsTools(m))

  const dot = ollamaConfig.connected ? 'bg-kali-green' : 'bg-kali-red'
  const canFetch = url.trim().length > 0 && !fetching

  return (
    <div className="border-t border-kali-border">
      {/* Sidebar trigger button */}
      <button
        onClick={handleOpen}
        className="w-full flex items-center gap-2 px-4 py-3 text-xs text-kali-muted hover:text-kali-text hover:bg-kali-border transition-colors"
      >
        <span className={`w-2 h-2 rounded-full ${dot} shrink-0`} />
        <span className="truncate">
          {ollamaConfig.connected
            ? `${ollamaConfig.model || 'Ollama Cloud'}`
            : ollamaConfig.apiKeySet
            ? 'Ollama Cloud (check connection)'
            : 'Configure Ollama Cloud'}
        </span>
        <span className="ml-auto text-kali-muted">⚙</span>
      </button>

      {/* Modal */}
      {open && (
        <div
          className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4"
          onClick={() => setOpen(false)}
        >
          <div
            className="bg-kali-surface border border-kali-border rounded-xl w-full max-w-lg shadow-2xl flex flex-col max-h-[90vh]"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="px-6 pt-5 pb-4 border-b border-kali-border">
              <div className="flex items-center justify-between mb-1">
                <h2 className="text-kali-text font-bold text-sm">Ollama Cloud</h2>
                <button
                  onClick={() => setOpen(false)}
                  className="text-kali-muted hover:text-kali-text text-lg leading-none"
                >
                  ×
                </button>
              </div>
              <p className="text-kali-muted text-xs">
                API key required — sign up at{' '}
                <span className="text-kali-accent">ollama.com</span>
              </p>
            </div>

            <div className="overflow-y-auto flex-1 px-6 py-4 space-y-4">
              {/* API Endpoint */}
              <div>
                <label className="text-xs text-kali-muted font-semibold block mb-1 uppercase tracking-wider">
                  API Endpoint
                </label>
                <input
                  className="w-full bg-kali-bg border border-kali-border rounded-lg px-3 py-2 text-xs text-kali-text outline-none focus:border-kali-accent transition-colors"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://ollama.com"
                />
              </div>

              {/* API Key */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs text-kali-muted font-semibold uppercase tracking-wider">
                    API Key
                  </label>
                  {ollamaConfig.apiKeySet && !apiKey && (
                    <span className="text-kali-green text-xs">✓ key saved — enter new to replace</span>
                  )}
                </div>
                <div className="relative">
                  <input
                    className="w-full bg-kali-bg border border-kali-border rounded-lg px-3 py-2 text-xs text-kali-text outline-none focus:border-kali-accent transition-colors pr-16"
                    type={showKey ? 'text' : 'password'}
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={ollamaConfig.apiKeySet ? '(unchanged)' : 'sk-ollama-…'}
                    autoComplete="off"
                  />
                  <div className="absolute right-1 top-1/2 -translate-y-1/2 flex items-center gap-1">
                    <button
                      className="text-kali-muted hover:text-kali-text text-xs px-1 py-0.5"
                      onClick={() => setShowKey((x) => !x)}
                      type="button"
                      title={showKey ? 'Hide key' : 'Show key'}
                    >
                      {showKey ? '🙈' : '👁'}
                    </button>
                  </div>
                </div>
              </div>

              {/* Fetch Models button + status */}
              <div>
                <button
                  onClick={handleFetchModels}
                  disabled={!canFetch}
                  className="w-full flex items-center justify-center gap-2 bg-kali-border hover:bg-kali-muted disabled:opacity-40 disabled:cursor-not-allowed text-kali-text text-xs font-semibold py-2 rounded-lg transition-colors"
                >
                  {fetching ? (
                    <>
                      <span className="animate-spin">⟳</span>
                      Fetching models…
                    </>
                  ) : (
                    <>
                      ↻ Fetch Available Models
                    </>
                  )}
                </button>

                {fetchStatus && (
                  <p className={`mt-2 text-xs ${fetchStatus.ok ? 'text-kali-green' : 'text-kali-red'}`}>
                    {fetchStatus.ok ? '✓' : '✗'} {fetchStatus.message}
                  </p>
                )}
              </div>

              {/* Model picker */}
              {fetchedModels.length > 0 && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-xs text-kali-muted font-semibold uppercase tracking-wider">
                      Select Model
                    </label>
                    <span className="text-xs text-kali-muted">{fetchedModels.length} available</span>
                  </div>

                  {/* Search */}
                  <input
                    className="w-full bg-kali-bg border border-kali-border rounded-lg px-3 py-1.5 text-xs text-kali-text outline-none focus:border-kali-accent mb-2 transition-colors"
                    placeholder="Filter models…"
                    value={modelSearch}
                    onChange={(e) => setModelSearch(e.target.value)}
                  />

                  <div className="bg-kali-bg rounded-lg border border-kali-border overflow-y-auto max-h-52 p-1">
                    {toolModels.length > 0 && (
                      <>
                        <p className="text-xs text-kali-muted px-2 py-1 font-semibold">
                          ⚡ Tool Calling (recommended for agentic use)
                        </p>
                        {toolModels.map((m) => (
                          <ModelRow
                            key={m}
                            name={m}
                            selected={model === m}
                            onSelect={setModel}
                          />
                        ))}
                      </>
                    )}

                    {otherModels.length > 0 && (
                      <>
                        {toolModels.length > 0 && (
                          <div className="border-t border-kali-border my-1" />
                        )}
                        <p className="text-xs text-kali-muted px-2 py-1 font-semibold">
                          Other Models
                        </p>
                        {otherModels.map((m) => (
                          <ModelRow
                            key={m}
                            name={m}
                            selected={model === m}
                            onSelect={setModel}
                          />
                        ))}
                      </>
                    )}

                    {visibleModels.length === 0 && (
                      <p className="text-kali-muted text-xs text-center py-4">No models match</p>
                    )}
                  </div>

                  {model && !modelSupportsTools(model) && (
                    <p className="text-kali-yellow text-xs mt-1">
                      ⚠ This model may not support tool calling. Agent may not be able to run pentesting tools.
                    </p>
                  )}
                </div>
              )}

              {/* Manual model entry when no models fetched yet */}
              {fetchedModels.length === 0 && (
                <div>
                  <label className="text-xs text-kali-muted font-semibold block mb-1 uppercase tracking-wider">
                    Model Name
                  </label>
                  <input
                    className="w-full bg-kali-bg border border-kali-border rounded-lg px-3 py-2 text-xs text-kali-text outline-none focus:border-kali-accent transition-colors"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    placeholder="llama3.1"
                  />
                  <p className="text-kali-muted text-xs mt-1">
                    Click "Fetch Available Models" above to browse models from your account.
                  </p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-kali-border flex gap-2">
              <button
                onClick={handleSave}
                disabled={saving || !model.trim()}
                className="flex-1 bg-kali-accent hover:bg-blue-400 disabled:opacity-40 disabled:cursor-not-allowed text-kali-bg text-xs font-bold py-2.5 rounded-lg transition-colors"
              >
                {saving ? 'Saving…' : 'Save & Connect'}
              </button>
              <button
                onClick={() => setOpen(false)}
                className="px-4 bg-kali-border hover:bg-kali-muted text-kali-text text-xs py-2.5 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
