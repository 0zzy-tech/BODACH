import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useAppStore } from '../store/appStore'

function ToolBlock({ msg }) {
  const [expanded, setExpanded] = useState(false)
  const isSuccess = msg.exitCode === 0
  const isDone = msg.done

  return (
    <div className="my-1 border border-kali-border rounded text-xs">
      <button
        onClick={() => setExpanded((x) => !x)}
        className="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-kali-border transition-colors"
      >
        <span className="text-kali-accent">⚡</span>
        <span className="text-kali-muted">run</span>
        <span className="text-kali-text font-semibold">{msg.tool}</span>
        {msg.args && Object.keys(msg.args).length > 0 && (
          <span className="text-kali-muted truncate">
            {Object.entries(msg.args)
              .map(([k, v]) => `${k}=${JSON.stringify(v)}`)
              .join(' ')}
          </span>
        )}
        <span className="ml-auto">
          {!isDone ? (
            <span className="text-kali-yellow animate-pulse">running…</span>
          ) : isSuccess ? (
            <span className="text-kali-green">✓ {msg.exitCode}</span>
          ) : (
            <span className="text-kali-red">✗ {msg.exitCode}</span>
          )}
        </span>
        <span className="text-kali-muted">{expanded ? '▲' : '▼'}</span>
      </button>
    </div>
  )
}

function Message({ msg, searchQuery = '' }) {
  if (msg.role === 'user') {
    return (
      <div className="flex justify-end mb-3">
        <div className="max-w-[75%] bg-kali-accent/20 border border-kali-accent/30 rounded-lg px-4 py-2">
          <p className="text-xs text-kali-text whitespace-pre-wrap">{highlightText(msg.content, searchQuery)}</p>
        </div>
      </div>
    )
  }

  if (msg.role === 'assistant' || msg.role === 'assistant_streaming') {
    return (
      <div className="mb-3">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-kali-red text-xs">⚔</span>
          <span className="text-kali-muted text-xs">AI Agent</span>
          {msg.role === 'assistant_streaming' && (
            <span className="text-kali-yellow text-xs animate-pulse">▋</span>
          )}
        </div>
        <div className="prose prose-invert prose-sm max-w-none text-kali-text text-xs leading-relaxed">
          <ReactMarkdown
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '')
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={vscDarkPlus}
                    language={match[1]}
                    PreTag="div"
                    className="text-xs rounded"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className="bg-kali-border px-1 rounded text-kali-accent" {...props}>
                    {children}
                  </code>
                )
              },
            }}
          >
            {msg.content}
          </ReactMarkdown>
        </div>
      </div>
    )
  }

  if (msg.role === 'tool_start') {
    return <ToolBlock msg={msg} />
  }

  if (msg.role === 'error') {
    return (
      <div className="mb-2 px-3 py-2 bg-kali-red/20 border border-kali-red/30 rounded text-xs text-kali-red">
        ⚠ {msg.content}
      </div>
    )
  }

  return null
}

function highlightText(text, query) {
  if (!query) return text
  const parts = text.split(new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'))
  return parts.map((part, i) =>
    part.toLowerCase() === query.toLowerCase()
      ? <mark key={i} className="bg-yellow-400 text-black rounded-sm">{part}</mark>
      : part
  )
}

export default function ChatPanel() {
  const { messages, activeSessionId, isConnected, isAgentRunning, sendMessage, createSession } = useAppStore()
  const [input, setInput] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchOpen, setSearchOpen] = useState(false)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)
  const searchRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault()
        setSearchOpen((x) => {
          if (!x) setTimeout(() => searchRef.current?.focus(), 50)
          return !x
        })
      }
      if (e.key === 'Escape') {
        setSearchOpen(false)
        setSearchQuery('')
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  const handleSend = () => {
    const text = input.trim()
    if (!text || !isConnected || isAgentRunning) return
    sendMessage(text)
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!activeSessionId) {
    return (
      <main className="flex-1 flex flex-col items-center justify-center bg-kali-bg">
        <div className="text-center">
          <p className="text-6xl mb-4">⚔</p>
          <h1 className="text-kali-text text-xl font-bold mb-2">Pentest Agent 2.0</h1>
          <p className="text-kali-muted text-sm mb-6">AI-powered red team assistant</p>
          <button
            onClick={() => createSession()}
            className="bg-kali-accent hover:bg-blue-400 text-kali-bg font-semibold text-sm py-2 px-6 rounded transition-colors"
          >
            Start New Session
          </button>
        </div>
      </main>
    )
  }

  const searchableRoles = ['user', 'assistant', 'assistant_streaming', 'tool_start']
  const visibleMessages = searchQuery
    ? messages.filter((m) => searchableRoles.includes(m.role) && m.content?.toLowerCase().includes(searchQuery.toLowerCase()))
    : messages

  return (
    <main className="flex-1 flex flex-col bg-kali-bg min-w-0">
      {/* Status bar */}
      <div className="flex items-center gap-3 px-4 py-2 border-b border-kali-border text-xs">
        <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-kali-green' : 'bg-kali-red'}`} />
        <span className="text-kali-muted">{isConnected ? 'Connected' : 'Disconnected'}</span>
        {isAgentRunning && (
          <span className="text-kali-yellow animate-pulse ml-2">Agent running…</span>
        )}
        <button
          onClick={() => { setSearchOpen((x) => { if (!x) setTimeout(() => searchRef.current?.focus(), 50); return !x }); setSearchQuery('') }}
          className="ml-auto text-kali-muted hover:text-kali-accent"
          title="Search (Ctrl+F)"
        >
          🔍
        </button>
      </div>

      {/* Search bar */}
      {searchOpen && (
        <div className="flex items-center gap-2 px-4 py-2 border-b border-kali-border bg-kali-surface text-xs">
          <input
            ref={searchRef}
            className="flex-1 bg-kali-bg border border-kali-border rounded px-2 py-1 text-kali-text outline-none focus:border-kali-accent placeholder-kali-muted"
            placeholder="Search messages…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <span className="text-kali-muted shrink-0">
              {visibleMessages.length} of {messages.filter(m => searchableRoles.includes(m.role)).length} match
            </span>
          )}
          <button
            onClick={() => { setSearchOpen(false); setSearchQuery('') }}
            className="text-kali-muted hover:text-kali-text"
          >
            ✕
          </button>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {visibleMessages.length === 0 && (
          <div className="text-center text-kali-muted text-xs mt-8">
            <p>{searchQuery ? 'No messages match your search.' : 'Session started. Configure your target and begin.'}</p>
          </div>
        )}
        {visibleMessages.map((msg, i) => (
          <Message key={i} msg={msg} searchQuery={searchQuery} />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-kali-border p-4">
        <div className="flex gap-2">
          <textarea
            ref={textareaRef}
            className="flex-1 bg-kali-surface border border-kali-border rounded-lg px-3 py-2 text-xs text-kali-text outline-none focus:border-kali-accent resize-none placeholder-kali-muted"
            rows={3}
            placeholder={
              !isConnected
                ? 'Connecting…'
                : isAgentRunning
                ? 'Agent is working…'
                : 'Describe what you want to test… (Enter to send, Shift+Enter for newline)'
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={!isConnected || isAgentRunning}
          />
          <button
            onClick={handleSend}
            disabled={!isConnected || isAgentRunning || !input.trim()}
            className="bg-kali-accent hover:bg-blue-400 disabled:opacity-40 disabled:cursor-not-allowed text-kali-bg font-semibold text-xs px-4 rounded-lg transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </main>
  )
}
