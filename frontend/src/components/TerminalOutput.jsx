import { useEffect, useRef } from 'react'
import { Terminal } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import { useAppStore } from '../store/appStore'
import '@xterm/xterm/css/xterm.css'

const KALI_THEME = {
  background: '#0d1117',
  foreground: '#e6edf3',
  cursor: '#58a6ff',
  black: '#161b22',
  red: '#f85149',
  green: '#3fb950',
  yellow: '#d29922',
  blue: '#58a6ff',
  magenta: '#bc8cff',
  cyan: '#39c5cf',
  white: '#e6edf3',
  brightBlack: '#8b949e',
  brightRed: '#ff7b72',
  brightGreen: '#56d364',
  brightYellow: '#e3b341',
  brightBlue: '#79c0ff',
  brightMagenta: '#d2a8ff',
  brightCyan: '#56d4dd',
  brightWhite: '#f0f6fc',
}

export default function TerminalOutput() {
  const termRef = useRef(null)
  const termInstance = useRef(null)
  const fitAddon = useRef(null)
  const prevLinesCount = useRef(0)
  const { terminalLines, clearTerminal, currentTool } = useAppStore()

  useEffect(() => {
    const term = new Terminal({
      theme: KALI_THEME,
      fontFamily: '"JetBrains Mono", "Fira Code", Consolas, monospace',
      fontSize: 11,
      lineHeight: 1.4,
      cursorBlink: false,
      disableStdin: true,
      scrollback: 5000,
    })
    const fit = new FitAddon()
    term.loadAddon(fit)
    term.open(termRef.current)
    fit.fit()
    termInstance.current = term
    fitAddon.current = fit

    const observer = new ResizeObserver(() => fit.fit())
    observer.observe(termRef.current)

    return () => {
      observer.disconnect()
      term.dispose()
    }
  }, [])

  // Write new lines to terminal
  useEffect(() => {
    const term = termInstance.current
    if (!term) return
    const newLines = terminalLines.slice(prevLinesCount.current)
    newLines.forEach((line) => {
      // Convert bare \n to \r\n for xterm
      term.write(line.replace(/\n/g, '\r\n'))
    })
    prevLinesCount.current = terminalLines.length
  }, [terminalLines])

  // Clear terminal when terminalLines resets to empty
  useEffect(() => {
    if (terminalLines.length === 0 && termInstance.current) {
      termInstance.current.clear()
      prevLinesCount.current = 0
    }
  }, [terminalLines.length])

  const handleCopy = () => {
    navigator.clipboard.writeText(terminalLines.join(''))
  }

  return (
    <div className="flex flex-col h-full min-h-0">
      <div className="flex items-center justify-between px-3 py-2 border-b border-kali-border">
        <div className="flex items-center gap-2">
          <span className="text-kali-green text-xs">⬤</span>
          <span className="text-kali-muted text-xs">
            {currentTool ? `Running: ${currentTool}` : 'Terminal'}
          </span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="text-kali-muted hover:text-kali-text text-xs px-2 py-0.5 border border-kali-border rounded transition-colors"
          >
            Copy
          </button>
          <button
            onClick={clearTerminal}
            className="text-kali-muted hover:text-kali-text text-xs px-2 py-0.5 border border-kali-border rounded transition-colors"
          >
            Clear
          </button>
        </div>
      </div>
      <div ref={termRef} className="flex-1 min-h-0 p-1" />
    </div>
  )
}
