#!/bin/bash
set -e

echo "[*] Starting Pentest Agent 2.0 container..."

# Start PostgreSQL for Metasploit
echo "[*] Starting PostgreSQL..."
service postgresql start || true
sleep 2

# Initialize/update Metasploit database
echo "[*] Initializing Metasploit database..."
msfdb init 2>/dev/null || msfdb reinit 2>/dev/null || true

# Ensure loot directory exists
mkdir -p /app/loot /data

echo "[*] Starting Pentest Agent 2.0 server on :8000..."
exec uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --loop asyncio \
    --log-level info
