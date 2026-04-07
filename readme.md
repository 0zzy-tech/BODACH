# Bodach

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker Hub](https://img.shields.io/docker/pulls/momomomomomomomomomo/bodach.svg)](https://hub.docker.com/r/momomomomomomomomomo/bodach)

> In folklore, **Bodach** is a sinister old man or bogeyman figure from Scottish and Gaelic tradition. It's often used for a spooky, mischievous presence.

An agentic AI-powered penetration testing assistant running inside Kali Linux. Chat with an AI that autonomously selects and runs 80+ pentesting tools, streams real-time output, tracks findings automatically, and generates professional reports.

> **For educational purposes only.** This tool is intended for learning about penetration testing techniques, practising in controlled lab environments, and studying offensive security concepts. Only use it against systems you own or have **explicit written authorisation** to test. Unauthorised use against systems you do not own is illegal.

Made for education purposes by **Ozzytech**

---

## Features

- **Agentic loop** — AI plans, runs tools, reads output, and adapts autonomously
- **80+ integrated tools** — covering the full attack lifecycle: recon, web, AD, cloud, containers, OSINT, and more
- **Auto-findings** — vulnerabilities automatically captured into the Findings tracker with CVSS scores and remediation status
- **Credential Vault** — discovered credentials saved automatically with click-to-reveal and copy support
- **Asset Inventory** — hosts discovered during scanning auto-populate a structured inventory
- **Attack Timeline** — chronological view of all tool executions per session
- **Real-time terminal** — live tool output streamed to the browser via WebSocket
- **Findings tracker** — filter, search, rate, and manage vulnerabilities per session
- **Reporting** — export HTML, Markdown, or PDF reports with one click
- **Session notes** — freeform scratchpad with auto-save per session
- **Command palette** — Ctrl+K to switch sessions, create new sessions, and more
- **Chat search** — Ctrl+F to filter and highlight messages
- **Light / Dark mode** — toggle in the sidebar footer
- **Multi-session** — run parallel investigations with full persistence
- **Stop button** — cancel a running agent at any time

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
                 └── 80+ pentesting tools (subprocess)
```

---

## Requirements

- Docker + Docker Compose
- An [Ollama Cloud](https://ollama.com) account and API key

---

## Quick Start (Docker Hub)

The easiest way to run Bodach is to pull the pre-built image directly from Docker Hub:

```bash
# 1. Copy and configure environment
cp .env.example .env
# Edit .env — set your OLLAMA_API_KEY

# 2. Pull and run
docker pull momomomomomomomomomo/bodach:latest
docker run -d \
  --name BODACH \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  -p 8000:8000 \
  --env-file .env \
  momomomomomomomomomo/bodach:latest

# 3. Open browser
open http://localhost:8000

# 4. Configure Ollama in the bottom-left panel, then start a session
```

Or using Docker Compose (builds locally):

```bash
cp .env.example .env
docker compose up --build
open http://localhost:8000
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
| `run_testssl` | `testssl.sh` | Comprehensive TLS/SSL testing |
| `run_arjun` | `arjun` | Hidden HTTP parameter discovery |
| `run_httpx` | `httpx` | Fast HTTP probing and fingerprinting |
| `run_katana` | `katana` | Fast web crawler and spider |
| `run_eyewitness` | `eyewitness` | Web screenshot and service fingerprinting |
| `run_gowitness` | `gowitness` | Web screenshot utility |
| `run_wafw00f` | `wafw00f` | WAF detection and fingerprinting |

### Web Application & Injection

| Tool | Command | Purpose |
|------|---------|---------|
| `run_sqlmap` | `sqlmap` | Automated SQL injection detection and exploitation |
| `run_commix` | `commix` | Command injection detection and exploitation |
| `run_dalfox` | `dalfox` | XSS scanning and exploitation |
| `run_tplmap` | `tplmap` | Server-side template injection (SSTI) detection |
| `run_ssrfmap` | `SSRFmap` | SSRF detection and exploitation |
| `run_xxeinjector` | `xxeinjector` | XXE injection exploitation |
| `run_lfimap` | `lfimap` | Local file inclusion testing |
| `run_crlfuzz` | `crlfuzz` | CRLF injection fuzzing |
| `run_corscanner` | `CORScanner` | CORS misconfiguration scanning |
| `run_smuggler` | `smuggler` | HTTP request smuggling detection |
| `run_oralyzer` | `oralyzer` | Open redirect analysis |
| `run_graphql_cop` | `graphql-cop` | GraphQL security testing |
| `run_kiterunner` | `kiterunner` | API endpoint discovery and fuzzing |
| `run_websocat` | `websocat` | WebSocket endpoint testing |
| `run_hosthunter` | `hosthunter` | Virtual host / host header injection discovery |
| `run_wpscan` | `wpscan` | WordPress vulnerability scanner |
| `run_joomscan` | `joomscan` | Joomla vulnerability scanner |
| `run_droopescan` | `droopescan` | Drupal/SilverStripe scanner |
| `run_dotdotpwn` | `dotdotpwn` | Directory traversal fuzzer |

### Secrets & Credential Discovery

| Tool | Command | Purpose |
|------|---------|---------|
| `run_trufflehog` | `trufflehog` | Secrets scanning in git repos and filesystems |
| `run_gitleaks` | `gitleaks` | Git repo secrets detection |
| `run_linkfinder` | `linkfinder` | JavaScript endpoint and secret extraction |
| `run_secretfinder` | `secretfinder` | Secret and API key discovery in JS files |
| `run_jwt_tool` | `jwt_tool` | JWT analysis, tampering, and attacks |

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
| `run_impacket_getnpusers` | `impacket-GetNPUsers` | AS-REP roasting — harvest crackable Kerberos hashes |
| `run_impacket_getuserspns` | `impacket-GetUserSPNs` | Kerberoasting — extract TGS hashes for offline cracking |
| `run_impacket_secretsdump` | `impacket-secretsdump` | Remote SAM/LSA/NTDS hash dumping |
| `run_bloodhound` | `bloodhound-python` | Active Directory enumeration and attack path mapping |

### DNS, Subdomain & OSINT

| Tool | Command | Purpose |
|------|---------|---------|
| `run_dnsrecon` | `dnsrecon` | DNS enumeration, zone transfers, subdomain brute-force |
| `run_subfinder` | `subfinder` | Passive subdomain discovery from 50+ public sources |
| `run_amass` | `amass` | In-depth subdomain enumeration and network mapping |
| `run_dnsx` | `dnsx` | Fast DNS resolution and enumeration |
| `run_puredns` | `puredns` | Mass DNS resolution and subdomain bruteforcing |
| `run_gau` | `gau` | Fetch known URLs from AlienVault, Wayback Machine |
| `run_theharvester` | `theHarvester` | OSINT — emails, subdomains from Google/Bing/crt.sh |
| `run_subover` | `subover` | Subdomain takeover detection |
| `run_subjack` | `subjack` | Subdomain takeover via dangling CNAME detection |

### Cloud & Containers

| Tool | Command | Purpose |
|------|---------|---------|
| `run_awscli` | `aws` | AWS resource enumeration with provided credentials |
| `run_prowler` | `prowler` | AWS/GCP/Azure security audit against CIS benchmarks |
| `run_s3scanner` | `s3scanner` | S3 bucket enumeration and permission testing |
| `run_kubehunter` | `kube-hunter` | Kubernetes cluster vulnerability scanning |
| `run_trivy` | `trivy` | Container image and filesystem vulnerability scanning |

### Exploitation & Post-Exploitation

| Tool | Command | Purpose |
|------|---------|---------|
| `run_metasploit` | `msfconsole` | Exploitation via Metasploit resource scripts |
| `run_msfvenom` | `msfvenom` | Payload generation (exe, elf, php, apk…) |
| `run_searchsploit` | `searchsploit` | Search Exploit-DB for known CVEs by software + version |
| `run_ysoserial` | `ysoserial` | Java deserialization exploit payload generation |
| `run_linpeas` | `linpeas.sh` | Linux privilege escalation enumeration (SSH-based) |

### Network & Infrastructure

| Tool | Command | Purpose |
|------|---------|---------|
| `run_snmpcheck` | `snmp-check` | Detailed SNMP enumeration (processes, users, routes) |
| `run_swaks` | `swaks` | SMTP server testing and open relay detection |

---

## Auto-Findings

The AI emits structured finding markers in its responses. When detected, findings are automatically:

1. Stripped from the displayed chat message
2. Saved to the session's Findings database (with CVSS score and remediation status)
3. Pushed live to the **Findings** tab in the right panel

Findings can be filtered by severity, searched by keyword, and tracked through remediation statuses: Open → In Progress → Resolved → Risk Accepted.

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
  -t momomomomomomomomomo/bodach:latest \
  --push .
```

---

## Docker Hub

```
docker pull momomomomomomomomomo/bodach:latest
```

[hub.docker.com/r/momomomomomomomomomo/bodach](https://hub.docker.com/r/momomomomomomomomomo/bodach)

---

## Licence

MIT — see [LICENSE](LICENSE). Copyright © 2026 Ozzytech.
