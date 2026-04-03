import { create } from 'zustand'
import { apiClient } from '../api/client'
import { wsManager } from '../api/websocket'

const useAppStore = create((set, get) => ({
  // Sessions
  sessions: [],
  activeSessionId: null,
  activeSession: null,

  // Messages for current session
  messages: [],

  // Ollama config
  ollamaConfig: {
    baseUrl: 'https://api.ollama.com',
    apiKey: '',
    apiKeySet: false,
    model: 'llama3.1',
    availableModels: [],
    connected: false,
    statusMessage: '',
  },

  // Findings
  findings: [],

  // Credentials
  credentials: [],

  // Theme
  theme: localStorage.getItem('theme') || 'dark',

  // Agent state
  isConnected: false,
  isAgentRunning: false,

  // Terminal lines (for xterm)
  terminalLines: [],
  currentTool: null,

  // ── Session actions ──────────────────────────────────────────────

  loadSessions: async () => {
    try {
      const sessions = await apiClient.getSessions()
      set({ sessions })
    } catch (e) {
      console.error('Failed to load sessions', e)
    }
  },

  createSession: async (name = '') => {
    try {
      const session = await apiClient.createSession(name)
      // Set activeSession immediately from the POST response — no extra GET needed
      wsManager.disconnect()
      set((s) => ({
        sessions: [session, ...s.sessions],
        activeSessionId: session.id,
        activeSession: session,
        messages: [],
        findings: [],
        credentials: [],
        terminalLines: [],
        isConnected: false,
        isAgentRunning: false,
      }))
      wsManager.connect(session.id)
      return session
    } catch (e) {
      console.error('Failed to create session', e)
    }
  },

  deleteSession: async (id) => {
    try {
      await apiClient.deleteSession(id)
      set((s) => {
        const sessions = s.sessions.filter((x) => x.id !== id)
        const next = s.activeSessionId === id ? null : s.activeSessionId
        return { sessions, activeSessionId: next }
      })
      if (get().activeSessionId === null) {
        wsManager.disconnect()
        set({ messages: [], activeSession: null, isConnected: false })
      }
    } catch (e) {
      console.error('Failed to delete session', e)
    }
  },

  setActiveSession: async (id) => {
    if (get().activeSessionId === id) return
    wsManager.disconnect()
    set({ activeSessionId: id, activeSession: null, messages: [], findings: [], credentials: [], terminalLines: [], isConnected: false, isAgentRunning: false })
    try {
      const [session, findings, credentials] = await Promise.all([
        apiClient.getSession(id),
        apiClient.getFindings(id),
        apiClient.getCredentials(id),
      ])
      set({ activeSession: session, findings, credentials })
      wsManager.connect(id)
    } catch (e) {
      console.error('Failed to load session', e)
    }
  },

  renameSession: async (id, name) => {
    try {
      const session = await apiClient.renameSession(id, name)
      set((s) => ({
        sessions: s.sessions.map((x) => (x.id === id ? { ...x, name } : x)),
        activeSession: s.activeSessionId === id ? session : s.activeSession,
      }))
    } catch (e) {
      console.error('Failed to rename session', e)
    }
  },

  updateTargetConfig: async (target) => {
    const id = get().activeSessionId
    if (!id) throw new Error('No active session')
    try {
      const session = await apiClient.updateTarget(id, target)
      set({ activeSession: session })
    } catch (e) {
      console.error('Failed to update target', e)
      throw e  // re-throw so TargetConfig can show the error
    }
  },

  // ── Findings actions ─────────────────────────────────────────────

  loadFindings: async (sessionId) => {
    try {
      const findings = await apiClient.getFindings(sessionId)
      set({ findings })
    } catch (e) {
      console.error('Failed to load findings', e)
    }
  },

  addFinding: async (data) => {
    const id = get().activeSessionId
    if (!id) return
    try {
      const finding = await apiClient.addFinding(id, data)
      set((s) => ({ findings: [...s.findings, finding] }))
    } catch (e) {
      console.error('Failed to add finding', e)
      throw e
    }
  },

  updateFinding: async (findingId, data) => {
    const id = get().activeSessionId
    if (!id) return
    try {
      const updated = await apiClient.updateFinding(id, findingId, data)
      set((s) => ({ findings: s.findings.map((f) => (f.id === findingId ? updated : f)) }))
    } catch (e) {
      console.error('Failed to update finding', e)
      throw e
    }
  },

  deleteFinding: async (findingId) => {
    const id = get().activeSessionId
    if (!id) return
    try {
      await apiClient.deleteFinding(id, findingId)
      set((s) => ({ findings: s.findings.filter((f) => f.id !== findingId) }))
    } catch (e) {
      console.error('Failed to delete finding', e)
    }
  },

  // ── Message actions ──────────────────────────────────────────────

  sendMessage: (content) => {
    if (!get().isConnected || get().isAgentRunning) return
    set({ isAgentRunning: true, terminalLines: [], currentTool: null })
    wsManager.send({ type: 'message', content })
    // Optimistically add user message
    set((s) => ({
      messages: [
        ...s.messages,
        { role: 'user', content, timestamp: new Date().toISOString() },
      ],
    }))
  },

  cancelAgent: () => {
    wsManager.send({ type: 'cancel' })
  },

  // ── WebSocket event handlers (called by wsManager) ───────────────

  onConnected: () => {
    set({ isConnected: true })
  },

  onHistory: (messages) => {
    set({ messages })
  },

  onToolStart: (tool, args) => {
    set({ currentTool: tool, terminalLines: [] })
    set((s) => ({
      messages: [
        ...s.messages,
        { role: 'tool_start', tool, args, timestamp: new Date().toISOString() },
      ],
    }))
  },

  onToolOutput: (line) => {
    set((s) => ({ terminalLines: [...s.terminalLines, line] }))
  },

  onToolEnd: (tool, exitCode) => {
    set((s) => ({
      messages: s.messages.map((m, i) =>
        i === s.messages.length - 1 && m.role === 'tool_start' && m.tool === tool
          ? { ...m, exitCode, done: true }
          : m
      ),
      currentTool: null,
    }))
  },

  onAssistantToken: (token) => {
    set((s) => {
      const msgs = [...s.messages]
      const last = msgs[msgs.length - 1]
      if (last && last.role === 'assistant_streaming') {
        msgs[msgs.length - 1] = { ...last, content: last.content + token }
      } else {
        msgs.push({ role: 'assistant_streaming', content: token, timestamp: new Date().toISOString() })
      }
      return { messages: msgs }
    })
  },

  onAssistantDone: (content) => {
    set((s) => {
      const msgs = s.messages.filter((m) => m.role !== 'assistant_streaming')
      msgs.push({ role: 'assistant', content, timestamp: new Date().toISOString() })
      return { messages: msgs, isAgentRunning: false }
    })
    // Update session list last_active
    get().loadSessions()
  },

  onError: (message) => {
    console.error('Agent error:', message)
    set((s) => ({
      messages: [...s.messages, { role: 'error', content: message, timestamp: new Date().toISOString() }],
      isAgentRunning: false,
    }))
  },

  onFindingAdded: (finding) => {
    set((s) => ({ findings: [...s.findings, finding] }))
  },

  onCredentialAdded: (credential) => {
    set((s) => ({ credentials: [...s.credentials, credential] }))
  },

  onCancelled: () => {
    set((s) => ({
      messages: [...s.messages, { role: 'error', content: 'Agent stopped by user.', timestamp: new Date().toISOString() }],
      isAgentRunning: false,
    }))
  },

  onDisconnected: () => {
    set({ isConnected: false, isAgentRunning: false })
  },

  // ── Credential actions ───────────────────────────────────────────────

  addCredential: async (data) => {
    const id = get().activeSessionId
    if (!id) return
    try {
      const credential = await apiClient.addCredential(id, data)
      set((s) => ({ credentials: [...s.credentials, credential] }))
    } catch (e) {
      console.error('Failed to add credential', e)
      throw e
    }
  },

  updateCredential: async (credId, data) => {
    const id = get().activeSessionId
    if (!id) return
    try {
      const updated = await apiClient.updateCredential(id, credId, data)
      set((s) => ({ credentials: s.credentials.map((c) => (c.id === credId ? updated : c)) }))
    } catch (e) {
      console.error('Failed to update credential', e)
      throw e
    }
  },

  deleteCredential: async (credId) => {
    const id = get().activeSessionId
    if (!id) return
    try {
      await apiClient.deleteCredential(id, credId)
      set((s) => ({ credentials: s.credentials.filter((c) => c.id !== credId) }))
    } catch (e) {
      console.error('Failed to delete credential', e)
    }
  },

  // ── Ollama config ────────────────────────────────────────────────

  loadOllamaConfig: async () => {
    try {
      const cfg = await apiClient.getOllamaConfig()
      set((s) => ({
        ollamaConfig: {
          ...s.ollamaConfig,
          baseUrl: cfg.base_url,
          apiKeySet: cfg.api_key_set,
          model: cfg.model,
          availableModels: cfg.available_models,
          connected: cfg.connected,
          statusMessage: cfg.status_message,
        },
      }))
    } catch (e) {
      console.error('Failed to load Ollama config', e)
    }
  },

  saveOllamaConfig: async (baseUrl, apiKey, model) => {
    try {
      const cfg = await apiClient.updateOllamaConfig(baseUrl, apiKey, model)
      set((s) => ({
        ollamaConfig: {
          ...s.ollamaConfig,
          baseUrl: cfg.base_url,
          apiKeySet: cfg.api_key_set,
          model: cfg.model,
          availableModels: cfg.available_models,
          connected: cfg.connected,
          statusMessage: cfg.status_message,
        },
      }))
    } catch (e) {
      console.error('Failed to save Ollama config', e)
    }
  },

  clearTerminal: () => set({ terminalLines: [] }),

  toggleTheme: () => {
    const next = get().theme === 'dark' ? 'light' : 'dark'
    localStorage.setItem('theme', next)
    document.documentElement.classList.toggle('light', next === 'light')
    set({ theme: next })
  },
}))

export { useAppStore }
