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
    swaks awscli default-jre ruby \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Layer 3: Extended tools (best-effort — skip any unavailable packages) ──────
RUN apt-get update && \
    for pkg in \
        feroxbuster nuclei netexec crackmapexec impacket-scripts \
        evil-winrm kerbrute exploitdb commix wpscan amass subfinder \
        snmp-check seclists wafw00f eyewitness joomscan dotdotpwn \
        testssl.sh golang-go trivy \
    ; do \
        apt-get install -y --no-install-recommends "$pkg" \
            && echo "[+] Installed $pkg" \
            || echo "[!] $pkg not available, skipping"; \
    done \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Layer 4: Go-based web tools ────────────────────────────────────────────────
ENV PATH="$PATH:/root/go/bin"
RUN which go >/dev/null 2>&1 && \
    for tool in \
        "github.com/projectdiscovery/httpx/cmd/httpx@latest" \
        "github.com/projectdiscovery/katana/cmd/katana@latest" \
        "github.com/projectdiscovery/dnsx/cmd/dnsx@latest" \
        "github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest" \
        "github.com/lc/gau/v2/cmd/gau@latest" \
        "github.com/hahwul/dalfox/v2@latest" \
        "github.com/dwisiswant0/crlfuzz/cmd/crlfuzz@latest" \
        "github.com/d3mondev/puredns/v2@latest" \
        "github.com/sensepost/gowitness@latest" \
        "github.com/zricethezav/gitleaks/v8@latest" \
        "github.com/trufflesecurity/trufflehog/v3@latest" \
        "github.com/Ice3man543/subover@latest" \
        "github.com/haccer/subjack@latest" \
    ; do \
        go install "$tool" && echo "[+] go install $tool" \
            || echo "[!] Failed: $tool, skipping"; \
    done || echo "[!] Go not available, skipping Go tools"

# ── Layer 5: Python/git web tools ──────────────────────────────────────────────
RUN pip3 install --no-cache-dir \
        droopescan \
        s3scanner \
        lfimap \
        graphql-cop \
        bloodhound \
        prowler \
        kube-hunter \
        hosthunter \
    2>/dev/null || true

RUN cd /opt && \
    for repo in \
        "https://github.com/ticarpi/jwt_tool" \
        "https://github.com/swisskyrepo/SSRFmap" \
        "https://github.com/chenjj/CORScanner" \
        "https://github.com/nicowillis/smuggler" \
        "https://github.com/epinna/tplmap" \
        "https://github.com/GerbenJavado/LinkFinder" \
        "https://github.com/m4ll0k/SecretFinder" \
        "https://github.com/r0oth3x49/Oralyzer" \
        "https://github.com/assetnote/kiterunner" \
        "https://github.com/enjoiz/XXEinjector" \
        "https://github.com/carlospolop/PEASS-ng" \
    ; do \
        name=$(basename "$repo") && \
        git clone --depth 1 "$repo" "$name" && echo "[+] Cloned $name" \
            || echo "[!] Failed to clone $repo, skipping"; \
    done

# Install Python deps for cloned tools (best-effort)
RUN for req in /opt/*/requirements.txt; do \
        pip3 install --no-cache-dir -r "$req" 2>/dev/null || true; \
    done

# ── Layer 6: Binary tools ───────────────────────────────────────────────────────
# websocat (WebSocket testing)
RUN curl -fsSL "https://github.com/vi/websocat/releases/download/v1.13.0/websocat.x86_64-unknown-linux-musl" \
        -o /usr/local/bin/websocat && chmod +x /usr/local/bin/websocat \
    || echo "[!] websocat download failed, skipping"

# ysoserial (Java deserialization)
RUN curl -fsSL "https://github.com/frohoff/ysoserial/releases/latest/download/ysoserial-all.jar" \
        -o /opt/ysoserial.jar \
    || echo "[!] ysoserial download failed, skipping"

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
