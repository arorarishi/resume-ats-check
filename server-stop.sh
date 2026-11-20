#!/usr/bin/env bash
# Stops the ATS Resume Tracker FastAPI server started by server-start.sh.
# Falls back to killing whatever is listening on the port, in case the PID file
# is stale or the server was started another way.
set +e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PORT=8765
PID_FILE="$ROOT/server.pid"
stopped=0

if [ -f "$PID_FILE" ]; then
    saved_pid="$(cat "$PID_FILE" 2>/dev/null)"
    if [ -n "$saved_pid" ] && kill -0 "$saved_pid" 2>/dev/null; then
        kill -9 "$saved_pid" 2>/dev/null
        echo "Stopped server (PID $saved_pid)."
        stopped=1
    fi
    rm -f "$PID_FILE"
fi

for listener_pid in $(lsof -ti tcp:"$PORT" -sTCP:LISTEN 2>/dev/null); do
    kill -9 "$listener_pid" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "Stopped process PID $listener_pid listening on port $PORT."
        stopped=1
    fi
done

if [ "$stopped" -eq 0 ]; then
    echo "No running server found on port $PORT."
fi
