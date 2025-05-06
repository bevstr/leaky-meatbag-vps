#!/bin/bash
# Launch script for Leaky Meatbag (local with virtual environment)

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_PORT=5100
VENV_DIR="$APP_DIR/venv"

clear
echo "==============================================="
echo "🧠 Starting Leaky Meatbag on port $APP_PORT"
echo "==============================================="

# Change to app directory
cd "$APP_DIR" || {
  echo "❌ Failed to change directory to $APP_DIR"
  exit 1
}

# Check for virtual environment
if [ ! -d "$VENV_DIR" ]; then
  echo "⚠️  Virtual environment not found. Creating one..."
  python3 -m venv venv
  source "$VENV_DIR/bin/activate"
  pip install --upgrade pip
  pip install -r requirements.txt
else
  echo "✅ Found virtual environment. Activating..."
  source "$VENV_DIR/bin/activate"
fi

# Kill anything already running on port
if lsof -ti:$APP_PORT >/dev/null; then
  echo "⚠️  Killing old process on port $APP_PORT..."
  lsof -ti:$APP_PORT | xargs kill -9
  sleep 1
fi

# Launch the app
echo ""
echo "🟢 Launching locally: http://localhost:$APP_PORT"
echo ""
python3 run.py || echo "❌ Failed to launch the app"

# Auto-deactivate on exit
deactivate
