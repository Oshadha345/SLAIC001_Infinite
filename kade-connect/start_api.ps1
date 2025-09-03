# Kade Connect Startup Script
Write-Host "🚀 Starting Kade Connect API..." -ForegroundColor Green

# Set location to project directory
Set-Location "S:\Projects\SLAIC001_Infinite\kade-connect"

# Check if virtual environment exists
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
    
    # Run the FastAPI application
    Write-Host "📡 Starting FastAPI server on http://localhost:8000" -ForegroundColor Cyan
    & "S:\Projects\SLAIC001_Infinite\kade-connect\venv\Scripts\uvicorn.exe" test_app:app --host 0.0.0.0 --port 8000
} else {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run the setup script first." -ForegroundColor Yellow
}
