#!/bin/bash
set -e

# Start Goodmap Backend Script
# Usage: start-backend.sh <config-path> <goodmap-path> <working-directory> <make-target> <log-file> <pid-file> [startup-wait-seconds]

CONFIG_PATH="$1"
GOODMAP_PATH="$2"
WORKING_DIRECTORY="$3"
MAKE_TARGET="$4"
LOG_FILE="$5"
PID_FILE="$6"
STARTUP_WAIT="${7:-5}"

if [ -z "$CONFIG_PATH" ] || [ -z "$GOODMAP_PATH" ] || [ -z "$WORKING_DIRECTORY" ] || [ -z "$MAKE_TARGET" ] || [ -z "$LOG_FILE" ] || [ -z "$PID_FILE" ]; then
  echo "Error: Missing required arguments"
  echo "Usage: start-backend.sh <config-path> <goodmap-path> <working-directory> <make-target> <log-file> <pid-file> [startup-wait-seconds]"
  exit 1
fi

echo "Starting backend with:"
echo "  CONFIG_PATH: $CONFIG_PATH"
echo "  GOODMAP_PATH: $GOODMAP_PATH"
echo "  WORKING_DIRECTORY: $WORKING_DIRECTORY"
echo "  MAKE_TARGET: $MAKE_TARGET"
echo "  LOG_FILE: $LOG_FILE"
echo "  PID_FILE: $PID_FILE"
echo "  STARTUP_WAIT: ${STARTUP_WAIT}s"

# Start the backend
cd "$WORKING_DIRECTORY"
export CONFIG_PATH
export GOODMAP_PATH
make "$MAKE_TARGET" > "$LOG_FILE" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$PID_FILE"
disown $BACKEND_PID

# Wait for startup
sleep "$STARTUP_WAIT"

# Check if backend started successfully
if ! kill -0 $(cat "$PID_FILE") 2>/dev/null; then
  echo "Backend failed to start. Log:"
  cat "$LOG_FILE"
  exit 1
fi

echo "Backend started successfully with PID $(cat "$PID_FILE")"
