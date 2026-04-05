import { useState } from 'react'
import TerminalOutput from './TerminalOutput'
import TargetConfig from './TargetConfig'
import FindingsPanel from './FindingsPanel'
import CredentialVault from './CredentialVault'
import LootPanel from './LootPanel'
import NotesPanel from './NotesPanel'
import AssetInventory from './AssetInventory'
import TimelinePanel from './TimelinePanel'
import { useAppStore } from '../store/appStore'

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

export default function RightPanel() {
  const { activeSessionId, findings, credentials, assets } = useAppStore()
  const [tab, setTab] = useState('terminal')

  if (!activeSessionId) return null

  return (
    <aside className="w-80 flex flex-col bg-kali-surface border-l border-kali-border shrink-0">
      {/* Tabs — scrollable row */}
      <div className="flex border-b border-kali-border overflow-x-auto scrollbar-none">
        {TABS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
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
    </aside>
  )
}
