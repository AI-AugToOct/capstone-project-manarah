# Quick Start Script for Windows

Write-Host "🚀 Starting Manarah Content Moderation System..." -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host "⚠️  .env file not found! Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "❌ Please edit .env and add your OPENAI_API_KEY, then run this script again." -ForegroundColor Red
    Write-Host "   Get your API key from: https://platform.openai.com/api-keys" -ForegroundColor Cyan
    exit 1
}

# Check if virtual environment exists
if (!(Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    
    Write-Host "📥 Installing dependencies..." -ForegroundColor Cyan
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
} else {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
    .\venv\Scripts\Activate.ps1
}

Write-Host ""
Write-Host "🧪 Running system tests..." -ForegroundColor Cyan
python tests/test_system.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ All tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Starting FastAPI server..." -ForegroundColor Cyan
    Write-Host "   API will be available at: http://localhost:8000" -ForegroundColor Yellow
    Write-Host "   API docs at: http://localhost:8000/docs" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
    Write-Host ""
    
    python -m uvicorn src.main:app --reload --port 8000
} else {
    Write-Host ""
    Write-Host "❌ Tests failed. Please fix the issues before starting the server." -ForegroundColor Red
    exit 1
}
