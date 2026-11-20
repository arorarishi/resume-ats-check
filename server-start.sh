#!/usr/bin/env bash
# Starts the Resume ATS Check FastAPI server directly (no desktop browser window),
# detached from this shell, tracked via server.pid for server-stop.sh to find later.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PORT=8765
PID_FILE="$ROOT/server.pid"
VENV_PYTHON="$ROOT/.venv-linux/bin/python"
LOG_FILE="$ROOT/server.log"
ERR_LOG_FILE="$ROOT/server.err.log"

if [ ! -x "$VENV_PYTHON" ]; then
    echo "Virtual environment not found at $VENV_PYTHON. Set up .venv-linux first." >&2
    exit 1
fi

# Already tracked and alive?
if [ -f "$PID_FILE" ]; then
    existing_pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [ -n "$existing_pid" ] && kill -0 "$existing_pid" 2>/dev/null; then
        echo "Server already running (PID $existing_pid) at http://127.0.0.1:$PORT"
        exit 0
    fi
    rm -f "$PID_FILE"
fi

# Something else already bound to the port?
existing_listener_pid="$(lsof -ti tcp:"$PORT" -sTCP:LISTEN 2>/dev/null | head -n1 || true)"
if [ -n "$existing_listener_pid" ]; then
    echo "Port $PORT is already in use by PID $existing_listener_pid (not started by this script). Not starting a new instance."
    exit 1
fi

nohup "$VENV_PYTHON" -m uvicorn app.server:app --host 127.0.0.1 --port "$PORT" \
    >"$LOG_FILE" 2>"$ERR_LOG_FILE" &
new_pid=$!

sleep 2

if kill -0 "$new_pid" 2>/dev/null; then
    echo "$new_pid" > "$PID_FILE"
    echo "Server started (PID $new_pid) at http://127.0.0.1:$PORT"
    echo "Logs: $LOG_FILE"
else
    echo "Server failed to start. Check $ERR_LOG_FILE for details." >&2
    exit 1
fi
