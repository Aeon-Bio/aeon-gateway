# Aeon Gateway - Quick Setup Script (Windows)
# For collaborators to get gateway running in minutes

$ErrorActionPreference = "Stop"

Write-Host "🔮 Aeon Gateway - Setup Script (Windows)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "1️⃣  Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = & python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+)") {
        $version = [version]$matches[1]
        if ($version -lt [version]"3.10") {
            Write-Host "❌ Python $version found, but 3.10+ required" -ForegroundColor Red
            Write-Host "   Download from https://www.python.org" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ $pythonVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Python not found. Please install Python 3.10+" -ForegroundColor Red
    Write-Host "   Download from https://www.python.org" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check uv
Write-Host "2️⃣  Checking uv package manager..." -ForegroundColor Yellow
try {
    $uvVersion = & uv --version 2>&1
    Write-Host "✅ uv installed" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing uv..." -ForegroundColor Yellow
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    Write-Host "✅ uv installed" -ForegroundColor Green
}
Write-Host ""

# Create virtual environment
Write-Host "3️⃣  Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "⚠️  Virtual environment already exists, skipping..." -ForegroundColor Yellow
} else {
    & uv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "4️⃣  Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1
Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "5️⃣  Installing dependencies..." -ForegroundColor Yellow
& uv pip install -r requirements.txt
Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Verify installation
Write-Host "6️⃣  Verifying installation..." -ForegroundColor Yellow
try {
    & python -c "from src.models.gateway import *"
    Write-Host "✅ Gateway modules imported successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to import gateway modules" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Run tests
Write-Host "7️⃣  Running tests..." -ForegroundColor Yellow
$testResult = & pytest tests/contracts/ -q --tb=no 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Contract tests passed (13/13)" -ForegroundColor Green
} else {
    Write-Host "❌ Some tests failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Success
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Start the server:" -ForegroundColor Cyan
Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "📖 Documentation:" -ForegroundColor Cyan
Write-Host "   UI Team:          docs/api/ui-integration-spec.md" -ForegroundColor White
Write-Host "   Agentic System:   docs/api/agentic-system-spec.md" -ForegroundColor White
Write-Host "   Local Dev Guide:  docs/deployment/local-development.md" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Test the gateway:" -ForegroundColor Cyan
Write-Host "   curl http://localhost:8000/health" -ForegroundColor White
Write-Host ""
