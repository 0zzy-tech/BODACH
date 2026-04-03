/**
 * WebSocket connection manager. Singleton that wraps a WebSocket and
 * dispatches typed events. App.jsx sets wsManager._dispatch after
 * the Zustand store is ready.
 */

let ws = null
let sessionId = null
let reconnectTimer = null
let reconnectDelay = 1000
let manuallyDisconnected = false

function dispatch(type, payload) {
  if (wsManager._dispatch) wsManager._dispatch(type, payload)
}

export const wsManager = {
  // Set by App.jsx: (type, payload) => void
  _dispatch: null,

  connect(id) {
    if (ws) {
      ws.close()
      ws = null
    }
    sessionId = id
    manuallyDisconnected = false
    _connect()
  },

  disconnect() {
    manuallyDisconnected = true
    clearTimeout(reconnectTimer)
    if (ws) {
      ws.close()
      ws = null
    }
    sessionId = null
    dispatch('disconnected', {})
  },

  send(data) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data))
    }
  },
}

function _connect() {
  if (!sessionId) return
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const url = `${proto}://${window.location.host}/ws/${sessionId}`
  ws = new WebSocket(url)

  ws.onopen = () => {
    reconnectDelay = 1000
    dispatch('connected', {})
  }

  ws.onmessage = (event) => {
    let data
    try {
      data = JSON.parse(event.data)
    } catch {
      return
    }
    const { type, ...payload } = data
    dispatch(type, payload)
  }

  ws.onclose = () => {
    ws = null
    dispatch('disconnected', {})
    if (!manuallyDisconnected && sessionId) {
      reconnectTimer = setTimeout(() => {
        reconnectDelay = Math.min(reconnectDelay * 2, 30000)
        _connect()
      }, reconnectDelay)
    }
  }

  ws.onerror = (e) => {
    console.error('WebSocket error', e)
  }
}
