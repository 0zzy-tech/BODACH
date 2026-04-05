import { useState, useEffect } from 'react'
import TerminalOutput from './TerminalOutput'
import TargetConfig from './TargetConfig'
import FindingsPanel from './FindingsPanel'
import CredentialVault from './CredentialVault'
import LootPanel from './LootPanel'
import NotesPanel from './NotesPanel'
import AssetInventory from './AssetInventory'
import TimelinePanel from './TimelinePanel'
import { useAppStore } from '../store/appStore'
import { apiClient } from '../api/client'

const TABS = [
  { key: 'terminal', label: 'Terminal' },
  { key: 'target', label: 'Target' },
  { key: 'findings', label: 'Findings' },
  { key: 'creds', label: 'Creds' },
  { key: 'assets', label: 'Assets' },
  { key: 'loot', label: 'Loot' },
  { key: 'notes', label: 'Notes' },
  { key: 'timeline', label: 'Timeline' },
]

function ToolAvailabilityModal({ onClose }) {
  const [data, setData] = useState(null)

  useEffect(() => {
    apiClient.getToolAvailability().then(setData).catch(() => {})
  }, [])

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-kali-surface border border-kali-border rounded-lg w-96 max-h-[70vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-kali-border">
          <span className="font-semibold text-kali-text text-sm">Tool Availability</span>
          <button onClick={onClose} className="text-kali-muted hover:text-kali-text">✕</button>
        </div>
        <div className="overflow-y-auto flex-1 p-3">
          {!data ? (
            <p className="text-kali-muted text-xs text-center py-4">Loading…</p>
          ) : (
            <div className="space-y-1">
              {Object.entries(data.availability).sort(([a], [b]) => a.localeCompare(b)).map(([tool, available]) => (
                <div key={tool} className="flex items-center justify-between text-xs">
                  <span className="font-mono text-kali-muted">{tool.replace('run_', '')}</span>
                  <span className={available ? 'text-green-400' : 'text-kali-red'}>
                    {available ? '✓' : '✗'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
        {data && (
          <div className="px-4 py-2 border-t border-kali-border text-xs text-kali-muted">
            {data.installed}/{data.total} tools available
          </div>
        )}
      </div>
    </div>
  )
}

export default function RightPanel() {
  const { activeSessionId, activeSession, findings, credentials, assets, sessionTabs, setActiveSessionTab } = useAppStore()
  const [showAvailability, setShowAvailability] = useState(false)

  // Restore tab from per-session memory
  const tab = (activeSessionId && sessionTabs[activeSessionId]) || 'terminal'

  const handleTabChange = (key) => {
    setActiveSessionTab(key)
  }

  if (!activeSessionId) return null

  return (
    <aside className="w-80 flex flex-col bg-kali-surface border-l border-kali-border shrink-0">
      {/* Tabs — scrollable row */}
      <div className="flex border-b border-kali-border overflow-x-auto scrollbar-none">
        {TABS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => handleTabChange(key)}
            className={`shrink-0 text-xs py-2 px-2.5 transition-colors relative whitespace-nowrap ${
              tab === key
                ? 'text-kali-text border-b-2 border-kali-accent'
                : 'text-kali-muted hover:text-kali-text'
            }`}
          >
            {label}
            {key === 'findings' && findings.length > 0 && (
              <span className="ml-1 bg-kali-accent text-kali-bg text-xs rounded-full px-1 leading-none">
                {findings.length}
              </span>
            )}
            {key === 'creds' && credentials.length > 0 && (
              <span className="ml-1 bg-kali-green text-kali-bg text-xs rounded-full px-1 leading-none">
                {credentials.length}
              </span>
            )}
            {key === 'assets' && assets.length > 0 && (
              <span className="ml-1 bg-kali-yellow text-kali-bg text-xs rounded-full px-1 leading-none">
                {assets.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto min-h-0">
        {tab === 'terminal' ? (
          <div className="h-full flex flex-col">
            {/* Tool availability badge */}
            <div className="px-3 pt-2 pb-1 border-b border-kali-border flex items-center justify-between">
              <span className="text-xs text-kali-muted uppercase tracking-wider font-semibold">Terminal</span>
              <button
                onClick={() => setShowAvailability(true)}
                className="text-xs text-kali-muted hover:text-kali-accent transition-colors"
                title="Check tool availability"
              >
                🔧 Tools
              </button>
            </div>
            <TerminalOutput />
          </div>
        ) : tab === 'target' ? (
          <TargetConfig />
        ) : tab === 'findings' ? (
          <FindingsPanel />
        ) : tab === 'creds' ? (
          <CredentialVault />
        ) : tab === 'assets' ? (
          <AssetInventory />
        ) : tab === 'loot' ? (
          <LootPanel />
        ) : tab === 'notes' ? (
          <NotesPanel />
        ) : (
          <TimelinePanel />
        )}
      </div>

      {showAvailability && <ToolAvailabilityModal onClose={() => setShowAvailability(false)} />}
    </aside>
  )
}
