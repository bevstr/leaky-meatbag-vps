#!/bin/bash
# Launch script for Leaky Meatbag

clear
echo "==============================================="
echo "🧠 Starting Leaky Meatbag on port 5100"
echo "==============================================="

cd /Users/bitty/Documents/GitHub/leaky-meatbag


# Kill anything on port 5100 (just in case)
if lsof -ti:5100 >/dev/null; then
  echo "⚠️  Killing old process on port 5100..."
  lsof -ti:5100 | xargs kill -9
  sleep 1
fi

# Start the app manually (for local dev without Docker)
echo ""
echo "🟢 Launching locally: http://localhost:5100"
echo ""
python3 run.py
