#!/bin/bash

# Stop Goodmap Backend Script
# Usage: stop-backend.sh <pid-file> <config-pattern>

PID_FILE="$1"
CONFIG_PATTERN="$2"

if [ -z "$PID_FILE" ] || [ -z "$CONFIG_PATTERN" ]; then
  echo "Error: Missing required arguments"
  echo "Usage: stop-backend.sh <pid-file> <config-pattern>"
  exit 1
fi

echo "Stopping backend:"
echo "  PID_FILE: $PID_FILE"
echo "  CONFIG_PATTERN: $CONFIG_PATTERN"

# Kill process by PID file if it exists
if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if kill -0 "$PID" 2>/dev/null; then
    echo "Stopping backend with PID $PID"
    kill "$PID" 2>/dev/null || true
  else
    echo "Process $PID is not running"
  fi
else
  echo "PID file $PID_FILE not found"
fi

# Kill by pattern as a fallback
if pkill -f "$CONFIG_PATTERN" 2>/dev/null; then
  echo "Stopped additional processes matching pattern: $CONFIG_PATTERN"
fi

# Give processes time to clean up
sleep 1

echo "Backend stopped"
