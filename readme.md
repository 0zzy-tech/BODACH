# Bodach

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> In folklore, **Bodach** is a sinister old man or bogeyman figure from Scottish and Gaelic tradition. It's often used for a spooky, mischievous presence rather than just the plain meaning of "old man."

An agentic AI-powered penetration testing assistant running inside Kali Linux. Chat with an AI that autonomously selects and runs pentesting tools, streams real-time output, tracks findings automatically, and generates professional reports.

> **For educational purposes only.** This tool is intended for learning about penetration testing techniques, practising in controlled lab environments, and studying offensive security concepts. Only use it against systems you own or have **explicit written authorisation** to test. Unauthorised use against systems you do not own is illegal.

Made for education purposes by **Ozzytech**

---

## Features

- **Agentic loop** — AI plans, runs tools, reads output, and adapts autonomously
- **33 integrated tools** — covering the full attack lifecycle
- **Auto-findings** — vulnerabilities are automatically captured into the Findings tracker as the AI discovers them
- **Real-time terminal** — live tool output streamed to the browser via WebSocket
- **Findings tracker** — log, rate, and manage vulnerabilities per session
- **Reporting** — export HTML, Markdown, or PDF reports with one click
- **Session export** — download full chat + tool output as JSON or plain text
- **Chat search** — Ctrl+F to filter and highlight messages
- **Light / Dark mode** — toggle in the sidebar footer
- **Multi-session** — run parallel investigations with full persistence

---

## Architecture

```
Browser  →  FastAPI (port 8000)
               ├── REST API   /api/v1/
               ├── WebSocket  /ws/{session_id}
               └── React frontend (static)
                        ↓
               Agentic Loop
                 ├── Ollama Cloud (remote LLM)
                 └── 33 pentesting tools (subprocess)
```

---

## Requirements

- Docker + Docker Compose
- An [Ollama Cloud](https://ollama.com) account and API key

---

## Quick Start

```bash
# 1. Copy and configure environment
cp .env.example .env
# Edit .env — set your OLLAMA_API_KEY

# 2. Build and run
docker compose up --build

# 3. Open browser
open http://localhost:8000

# 4. Configure Ollama in the bottom-left panel, then start a session
```

---

## Supported Models

Models must support native tool/function calling:

| Model | Notes |
|-------|-------|
| `llama3.1` | Recommended — best balance of speed and capability |
| `llama3.3` | More capable, slower |
| `qwen2.5` | Excellent for technical/structured tasks |
| `mistral-nemo` | Good instruction following |
| `qwen2.5-coder` | Strong for code and exploit analysis |

---

## Tools

### Scanning & Enumeration

| Tool | Command | Purpose |
|------|---------|---------|
| `run_nmap` | `nmap` | Port scanning, service/version detection, OS fingerprinting |
| `run_masscan` | `masscan` | Ultra-fast port scanning across large IP ranges |
| `run_gobuster` | `gobuster` | Directory and DNS brute-forcing |
| `run_ffuf` | `ffuf` | Fast web fuzzing — dirs, files, vhosts, parameters |
| `run_feroxbuster` | `feroxbuster` | Recursive web content discovery |
| `run_nikto` | `nikto` | Web server vulnerability scanning |
| `run_nuclei` | `nuclei` | Template-based CVE and misconfiguration scanning |
| `run_whatweb` | `whatweb` | Web technology fingerprinting |
| `run_dirb` | `dirb` | Dictionary-based web directory scanning |
| `run_wfuzz` | `wfuzz` | Web application fuzzing |
| `run_sslscan` | `sslscan` | SSL/TLS configuration audit |
| `run_arjun` | `arjun` | Hidden HTTP parameter discovery |

### Web Application

| Tool | Command | Purpose |
|------|---------|---------|
| `run_sqlmap` | `sqlmap` | Automated SQL injection detection and exploitation |
| `run_commix` | `commix` | Command injection detection and exploitation |
| `run_wpscan` | `wpscan` | WordPress vulnerability scanner |

### Password Attacks

| Tool | Command | Purpose |
|------|---------|---------|
| `run_hydra` | `hydra` | Online password brute-forcing (SSH, FTP, HTTP, RDP…) |
| `run_medusa` | `medusa` | Parallel online brute-forcing |
| `run_john` | `john` | Offline hash cracking with wordlists |
| `run_hashcat` | `hashcat` | GPU/CPU hash cracking (NTLM, bcrypt, WPA2, AS-REP…) |

### SMB / Windows / Active Directory

| Tool | Command | Purpose |
|------|---------|---------|
| `run_netexec` | `nxc` | SMB/WinRM/LDAP auth testing, share enum, user listing |
| `run_enum4linux` | `enum4linux` | SMB/Samba enumeration |
| `run_smbclient` | `smbclient` | SMB share access and file retrieval |
| `run_kerbrute` | `kerbrute` | Kerberos user enumeration and password spraying |
| `run_getnpusers` | `impacket-GetNPUsers` | AS-REP roasting — harvest crackable Kerberos hashes |
| `run_getuserspns` | `impacket-GetUserSPNs` | Kerberoasting — extract TGS hashes for offline cracking |
| `run_secretsdump` | `impacket-secretsdump` | Remote SAM/LSA/NTDS hash dumping |

### SNMP

| Tool | Command | Purpose |
|------|---------|---------|
| `run_snmpcheck` | `snmp-check` | Detailed SNMP enumeration (processes, users, routes) |

### DNS & OSINT

| Tool | Command | Purpose |
|------|---------|---------|
| `run_dnsrecon` | `dnsrecon` | DNS enumeration, zone transfers, subdomain brute-force |
| `run_subfinder` | `subfinder` | Passive subdomain discovery from 50+ public sources |
| `run_theharvester` | `theHarvester` | OSINT — emails, subdomains from Google/Bing/crt.sh |

### Exploitation

| Tool | Command | Purpose |
|------|---------|---------|
| `run_metasploit` | `msfconsole` | Exploitation via Metasploit resource scripts |
| `run_msfvenom` | `msfvenom` | Payload generation (exe, elf, php, apk…) |
| `run_searchsploit` | `searchsploit` | Search Exploit-DB for known CVEs by software + version |

---

## Auto-Findings

The AI is instructed to emit structured finding markers in its responses. When detected, findings are automatically:

1. Stripped from the displayed chat message
2. Saved to the session's Findings database
3. Pushed live to the **Findings** tab in the right panel

You can also add, edit, and delete findings manually from the Findings tab.

---

## Reporting

Hover over any session in the sidebar and click **⬇** to open the report/export dialog:

| Format | Contents |
|--------|---------|
| **HTML** | Self-contained dark-themed report with findings table and chat transcript |
| **Markdown** | Plain Markdown — suitable for pasting into wikis or docs |
| **PDF** | Printable PDF generated server-side via WeasyPrint |
| **JSON export** | Full session data including messages and findings |
| **Text export** | Human-readable plain-text transcript |

---

## Security Notes

- Only use against systems you have **explicit written authorisation** to test
- The agent enforces the scope constraints set in the Target tab
- All subprocess calls use argument lists — no `shell=True`
- Tool output is capped at 10 MB per run
- sqlmap and hydra always run in non-interactive (`--batch`) mode
- API keys are never echoed back in API responses

---

## Development

```bash
# Backend (Python 3.11+)
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000

# Frontend dev server (proxies /api and /ws to :8000)
cd frontend
npm install
npm run dev
```

---

## Multi-arch Build

The image supports both `linux/amd64` and `linux/arm64`:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t your-registry/pentest-agent:2.0 \
  --push .
```

---

## Licence

MIT — see [LICENSE](LICENSE). Copyright © 2026 Ozzytech.
