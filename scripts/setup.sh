#!/bin/bash
# Aeon Gateway - Quick Setup Script
# For collaborators to get gateway running in minutes

set -e  # Exit on error

echo "🔮 Aeon Gateway - Setup Script"
echo "================================"
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+ from https://www.python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION found, but $REQUIRED_VERSION+ required"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION"
echo ""

# Check uv
echo "2️⃣  Checking uv package manager..."
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi
echo "✅ uv installed"
echo ""

# Create virtual environment
echo "3️⃣  Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "⚠️  Virtual environment already exists, skipping..."
else
    uv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "4️⃣  Activating virtual environment..."
source .venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "5️⃣  Installing dependencies..."
uv pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Verify installation
echo "6️⃣  Verifying installation..."
if python -c "from src.models.gateway import *" 2>/dev/null; then
    echo "✅ Gateway modules imported successfully"
else
    echo "❌ Failed to import gateway modules"
    exit 1
fi
echo ""

# Run tests
echo "7️⃣  Running tests..."
if pytest tests/contracts/ -q --tb=no; then
    echo "✅ Contract tests passed (13/13)"
else
    echo "❌ Some tests failed"
    exit 1
fi
echo ""

# Success
echo "================================"
echo "✅ Setup complete!"
echo ""
echo "🚀 Start the server:"
echo "   source .venv/bin/activate"
echo "   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "📖 Documentation:"
echo "   UI Team:          docs/api/ui-integration-spec.md"
echo "   Agentic System:   docs/api/agentic-system-spec.md"
echo "   Local Dev Guide:  docs/deployment/local-development.md"
echo ""
echo "🧪 Test the gateway:"
echo "   curl http://localhost:8000/health"
echo ""
