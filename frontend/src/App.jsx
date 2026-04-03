import { useEffect } from 'react'
import { useAppStore } from './store/appStore'
import { wsManager } from './api/websocket'
import SessionSidebar from './components/SessionSidebar'
import ChatPanel from './components/ChatPanel'
import RightPanel from './components/RightPanel'

export default function App() {
  const store = useAppStore()

  // Apply saved theme on mount
  useEffect(() => {
    const saved = localStorage.getItem('theme') || 'dark'
    document.documentElement.classList.toggle('light', saved === 'light')
  }, [])

  // Wire wsManager dispatch to store actions
  useEffect(() => {
    wsManager._dispatch = (type, payload) => {
      switch (type) {
        case 'connected':
          store.onConnected()
          break
        case 'history':
          store.onHistory(payload.messages)
          break
        case 'tool_start':
          store.onToolStart(payload.tool, payload.args)
          break
        case 'tool_output':
          store.onToolOutput(payload.line)
          break
        case 'tool_end':
          store.onToolEnd(payload.tool, payload.exit_code)
          break
        case 'assistant_token':
          store.onAssistantToken(payload.token)
          break
        case 'assistant_done':
          store.onAssistantDone(payload.content)
          break
        case 'finding_added':
          store.onFindingAdded(payload.finding)
          break
        case 'error':
          store.onError(payload.message)
          break
        case 'disconnected':
          store.onDisconnected()
          break
        default:
          break
      }
    }
  }, [store])

  // Load initial data
  useEffect(() => {
    store.loadSessions()
    store.loadOllamaConfig()
  }, [])

  return (
    <div className="flex h-screen bg-kali-bg overflow-hidden">
      <SessionSidebar />
      <ChatPanel />
      <RightPanel />
    </div>
  )
}
