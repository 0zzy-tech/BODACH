# Bodach — Kali Linux container
FROM kalilinux/kali-rolling

LABEL maintainer="MRO"
LABEL description="Bodach — Agentic AI-driven red team assistant powered by Ollama"

# Avoid interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# ── Layer 1: System utilities & build deps ─────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget git vim procps \
    python3 python3-pip python3-venv \
    nodejs npm \
    postgresql postgresql-client \
    gcc python3-dev libssl-dev libffi-dev \
    libpango-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Layer 2: Core pentesting tools (stable Kali packages) ─────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap masscan gobuster ffuf nikto sqlmap whatweb dirb wfuzz sslscan \
    hydra john hashcat medusa \
    enum4linux smbclient ldap-utils nbtscan \
    metasploit-framework \
    dnsrecon theharvester \
    tcpdump netdiscover arp-scan hping3 fping socat \
    onesixtyone snmp \
    wordlists \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Layer 3: Extended tools (best-effort — skip any unavailable packages) ──────
# Package names can vary across Kali rolling snapshots; failures are non-fatal
RUN apt-get update && \
    for pkg in \
        feroxbuster \
        nuclei \
        netexec \
        crackmapexec \
        impacket-scripts \
        evil-winrm \
        kerbrute \
        exploitdb \
        commix \
        wpscan \
        amass \
        subfinder \
        snmp-check \
        seclists \
    ; do \
        apt-get install -y --no-install-recommends "$pkg" \
            && echo "[+] Installed $pkg" \
            || echo "[!] $pkg not available in current repos, skipping"; \
    done \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Python virtual environment ─────────────────────────────────────────────────
ENV VENV=/opt/venv
RUN python3 -m venv $VENV
ENV PATH="$VENV/bin:$PATH"

WORKDIR /app

# Install Python dependencies (cached layer)
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# ── Frontend build ─────────────────────────────────────────────────────────────
COPY frontend/package.json frontend/package-lock.json* /app/frontend/
RUN cd /app/frontend && npm install --prefer-offline 2>/dev/null || npm install

COPY frontend/ /app/frontend/
RUN cd /app/frontend && npm run build

# ── Backend source ─────────────────────────────────────────────────────────────
COPY backend/ /app/backend/

# ── Entrypoint ────────────────────────────────────────────────────────────────
COPY scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create data and loot directories
RUN mkdir -p /data /app/loot /app/backend/static

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
