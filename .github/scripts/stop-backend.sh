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
KILLED_BY_PID=false
if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if kill -0 "$PID" 2>/dev/null; then
    echo "Stopping backend with PID $PID"
    kill "$PID" 2>/dev/null
    KILL_EXIT=$?
    echo "DEBUG: kill command exited with code: $KILL_EXIT"

    if [ "$KILL_EXIT" -eq 0 ]; then
      # Wait for process to actually die (up to 10 seconds)
      echo "Waiting for process to terminate..."
      for i in {1..20}; do
        if ! kill -0 "$PID" 2>/dev/null; then
          echo "Process $PID terminated successfully after ${i} attempts"
          KILLED_BY_PID=true
          break
        fi
        sleep 0.5
      done

      if [ "$KILLED_BY_PID" = false ]; then
        echo "WARNING: Process $PID did not terminate after 10 seconds, trying SIGKILL"
        kill -9 "$PID" 2>/dev/null || true
        sleep 1
        KILLED_BY_PID=true
      fi
    fi
    echo "DEBUG: After kill verification"
  else
    echo "Process $PID is not running"
  fi
else
  echo "PID file $PID_FILE not found"
fi

# Only try pkill if we didn't successfully kill by PID
if [ "$KILLED_BY_PID" = false ]; then
  echo "DEBUG: Attempting pkill fallback"
  # Kill by pattern as a fallback - run in completely isolated subshell
  PKILL_EXIT=1
  (
    set +e
    pkill -f "$CONFIG_PATTERN" 2>/dev/null
    exit $?
  ) && PKILL_EXIT=0 || PKILL_EXIT=$?

  echo "DEBUG: pkill exited with code: $PKILL_EXIT"
  if [ "$PKILL_EXIT" -eq 0 ]; then
    echo "Stopped additional processes matching pattern: $CONFIG_PATTERN"
  fi
else
  echo "DEBUG: Skipping pkill (already killed by PID)"
fi

# Give processes time to clean up
sleep 1
echo "DEBUG: After sleep 1, exit code: $?"

echo "Backend stopped"
echo "DEBUG: Final exit code before script end: $?"
