import { useState } from 'react'
import { useAppStore } from '../store/appStore'

function formatTime(ts) {
  if (!ts) return '??:??'
  try {
    return new Date(ts).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return '??:??'
  }
}

function duration(startTs, endTs) {
  if (!startTs || !endTs) return null
  const ms = new Date(endTs) - new Date(startTs)
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`
}

export default function TimelinePanel() {
  const { messages } = useAppStore()
  const [expandedIdx, setExpandedIdx] = useState(null)

  // Build timeline entries from messages
  const entries = []
  const toolStarts = {}

  for (let i = 0; i < messages.length; i++) {
    const m = messages[i]

    if (m.role === 'user') {
      entries.push({ type: 'user', content: m.content, timestamp: m.timestamp })
    } else if (m.role === 'assistant') {
      // Short summary: first 100 chars
      entries.push({ type: 'assistant', content: m.content, timestamp: m.timestamp })
    } else if (m.role === 'tool_start') {
      const key = m.tool
      toolStarts[key] = { idx: entries.length, timestamp: m.timestamp }
      entries.push({
        type: 'tool',
        tool: m.tool,
        args: m.args,
        exitCode: m.exitCode,
        done: m.done,
        timestamp: m.timestamp,
        endTimestamp: null,
      })
    }
    // tool_start gets updated when we see exitCode on the message (already merged in store)
  }

  if (entries.length === 0) {
    return (
      <div className="p-4 text-center text-kali-muted text-xs mt-4">
        No activity yet — tool runs and AI responses will appear here.
      </div>
    )
  }

  return (
    <div className="p-3 space-y-1">
      {entries.map((e, i) => (
        <TimelineEntry
          key={i}
          entry={e}
          index={i}
          expanded={expandedIdx === i}
          onToggle={() => setExpandedIdx(expandedIdx === i ? null : i)}
        />
      ))}
    </div>
  )
}

function TimelineEntry({ entry, index, expanded, onToggle }) {
  if (entry.type === 'user') {
    return (
      <div className="flex gap-2 items-start text-xs">
        <span className="text-kali-muted shrink-0 w-14 text-right">{formatTime(entry.timestamp)}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1">
            <span className="text-kali-accent">▶</span>
            <span className="text-kali-muted">You:</span>
            <span className="text-kali-text truncate">{entry.content.slice(0, 60)}{entry.content.length > 60 ? '…' : ''}</span>
          </div>
        </div>
      </div>
    )
  }

  if (entry.type === 'assistant') {
    return (
      <div className="flex gap-2 items-start text-xs">
        <span className="text-kali-muted shrink-0 w-14 text-right">{formatTime(entry.timestamp)}</span>
        <div className="flex-1 min-w-0">
          <button
            className="w-full text-left flex items-start gap-1 hover:text-kali-text transition-colors"
            onClick={onToggle}
          >
            <span className="text-kali-red shrink-0">⚔</span>
            <span className="text-kali-muted truncate">{entry.content.slice(0, 80)}{entry.content.length > 80 ? '…' : ''}</span>
          </button>
          {expanded && (
            <div className="mt-1 pl-4 text-kali-muted leading-relaxed whitespace-pre-wrap">
              {entry.content.slice(0, 500)}{entry.content.length > 500 ? '\n…' : ''}
            </div>
          )}
        </div>
      </div>
    )
  }

  if (entry.type === 'tool') {
    const isSuccess = entry.exitCode === 0
    const isCancelled = entry.exitCode === -2
    return (
      <div className="flex gap-2 items-start text-xs">
        <span className="text-kali-muted shrink-0 w-14 text-right">{formatTime(entry.timestamp)}</span>
        <div className="flex-1 min-w-0 border border-kali-border rounded">
          <button
            className="w-full flex items-center gap-2 px-2 py-1 text-left hover:bg-kali-border transition-colors"
            onClick={onToggle}
          >
            <span className="text-kali-accent">⚡</span>
            <span className="text-kali-text font-semibold">{entry.tool}</span>
            {entry.args && Object.keys(entry.args).length > 0 && (
              <span className="text-kali-muted truncate">
                {Object.values(entry.args).join(' ').slice(0, 40)}
              </span>
            )}
            <span className="ml-auto shrink-0">
              {!entry.done ? (
                <span className="text-kali-yellow animate-pulse">running</span>
              ) : isCancelled ? (
                <span className="text-kali-muted">cancelled</span>
              ) : isSuccess ? (
                <span className="text-kali-green">✓</span>
              ) : (
                <span className="text-kali-red">✗ {entry.exitCode}</span>
              )}
            </span>
          </button>
          {expanded && entry.args && Object.keys(entry.args).length > 0 && (
            <div className="border-t border-kali-border px-2 py-1 text-kali-muted font-mono text-[10px]">
              {Object.entries(entry.args).map(([k, v]) => (
                <span key={k} className="mr-3">{k}={JSON.stringify(v)}</span>
              ))}
            </div>
          )}
        </div>
      </div>
    )
  }

  return null
}
