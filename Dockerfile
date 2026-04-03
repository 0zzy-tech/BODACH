# Agentic Pentesting AI - Kali Linux container
FROM kalilinux/kali-rolling

LABEL maintainer="PenTest AI"
LABEL description="AI-driven red team assistant powered by Ollama"

# Avoid interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# ── System packages ────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core utilities
    curl wget git vim procps \
    # Pentesting tools
    nmap \
    gobuster \
    nikto \
    sqlmap \
    hydra \
    whatweb \
    dirb \
    wfuzz \
    enum4linux \
    smbclient \
    metasploit-framework \
    wordlists \
    # Python
    python3 \
    python3-pip \
    python3-venv \
    # Node.js for frontend build
    nodejs \
    npm \
    # PostgreSQL for Metasploit
    postgresql \
    postgresql-client \
    # Build dependencies for Python packages
    gcc \
    python3-dev \
    libssl-dev \
    libffi-dev \
    # WeasyPrint system dependencies (for PDF report generation)
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
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
