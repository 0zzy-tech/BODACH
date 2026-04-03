# PenTest AI

An agentic AI-powered penetration testing assistant running in Kali Linux. Chat with an AI agent that autonomously selects and runs pentesting tools, streams real-time output, and synthesizes findings.

## Architecture

```
Browser  →  FastAPI (port 8000)
               ├── REST API  /api/v1/
               ├── WebSocket /ws/{session_id}
               └── React frontend (static)
                        ↓
               Agentic Loop
                 ├── Ollama (remote LLM server)
                 └── Pentesting tools:
                     nmap · gobuster · nikto · sqlmap
                     metasploit · hydra · whatweb · dirb
                     wfuzz · enum4linux · smbclient
```

## Requirements

- Docker + Docker Compose
- An [Ollama Cloud](https://ollama.com) account and API key

## Quick Start

```bash
# 1. Copy and configure environment
cp .env.example .env
# Edit .env: set your OLLAMA_API_KEY

# 2. Build and run
docker compose up --build

# 3. Open browser
open http://localhost:8000

# 4. Click the Ollama indicator (bottom-left) to confirm connection
```

## Supported Models

These models support native tool/function calling via Ollama:

| Model | Notes |
|-------|-------|
| `llama3.1` | Recommended — best balance |
| `llama3.2` | Faster, less capable |
| `qwen2.5` | Excellent for technical tasks |
| `mistral-nemo` | Good instruction following |

## Usage

1. Open `http://localhost:8000`
2. Click the Ollama indicator (bottom-left sidebar) to configure your server URL and model
3. Click **+ New Session**
4. Set the target IP/domain in the **Target** tab (right panel)
5. Chat: *"Scan this host and identify open services"*

The agent will plan its approach, run tools, stream output to the terminal panel, and summarize findings.

## Tools Available

| Tool | Purpose |
|------|---------|
| `run_nmap` | Port scanning and service detection |
| `run_gobuster` | Directory/DNS brute-forcing |
| `run_nikto` | Web vulnerability scanning |
| `run_sqlmap` | SQL injection testing |
| `run_metasploit` | Exploitation via resource scripts |
| `run_hydra` | Password brute-forcing |
| `run_whatweb` | Web technology fingerprinting |
| `run_dirb` | Web directory enumeration |
| `run_wfuzz` | Web application fuzzing |
| `run_enum4linux` | SMB/Windows enumeration |
| `run_smbclient` | SMB share access and enumeration |

## Security Notes

- Only use against systems you have explicit written authorization to test
- The agent enforces scope constraints set in the Target configuration
- All subprocess calls use argument lists (no `shell=True`) to prevent injection
- Tool output is capped at 10MB per run
- sqlmap and hydra always run in non-interactive (`--batch`) mode

## Development

```bash
# Backend (requires Python 3.11+)
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend dev server (proxies /api and /ws to :8000)
cd frontend
npm install
npm run dev
```
