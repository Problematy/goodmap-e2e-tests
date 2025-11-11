#!/bin/bash
set +e  # Don't exit on errors
set +m  # Disable job control messages

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

# Debug: Check current jobs
echo "DEBUG: Current jobs:"
jobs -l || true

# Kill process by PID file if it exists
if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if kill -0 "$PID" 2>/dev/null; then
    echo "Stopping backend with PID $PID"
    kill "$PID" 2>/dev/null
    KILL_EXIT=$?
    echo "DEBUG: kill command exited with code: $KILL_EXIT"
    # Wait a moment for clean shutdown
    sleep 0.5
    echo "DEBUG: After sleep 0.5"
  else
    echo "Process $PID is not running"
  fi
else
  echo "PID file $PID_FILE not found"
fi

echo "DEBUG: Before pkill, exit code: $?"

# Kill by pattern as a fallback
pkill -f "$CONFIG_PATTERN" 2>/dev/null
PKILL_EXIT=$?
echo "DEBUG: pkill exited with code: $PKILL_EXIT"

if [ "$PKILL_EXIT" -eq 0 ]; then
  echo "Stopped additional processes matching pattern: $CONFIG_PATTERN"
fi

# Give processes time to clean up
sleep 1
echo "DEBUG: After sleep 1, exit code: $?"

echo "Backend stopped"
echo "DEBUG: Final exit code before script end: $?"
