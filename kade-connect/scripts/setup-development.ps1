# PowerShell Development Environment Setup Script for Kade Connect
# Run this script as Administrator

Write-Host "🚀 Setting up Kade Connect Development Environment..." -ForegroundColor Green

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ This script requires Administrator privileges. Please run PowerShell as Administrator." -ForegroundColor Red
    exit 1
}

# Install Chocolatey if not already installed
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    refreshenv
}

# Install core development tools
Write-Host "🛠️ Installing development tools..." -ForegroundColor Yellow
$tools = @(
    "git",
    "python311",
    "nodejs",
    "docker-desktop",
    "vscode",
    "postgresql14",
    "redis-64",
    "microsoft-windows-terminal",
    "googlechrome"
)

foreach ($tool in $tools) {
    Write-Host "Installing $tool..." -ForegroundColor Cyan
    choco install -y $tool
}

# Refresh environment variables
refreshenv

Write-Host "🐍 Setting up Python environment..." -ForegroundColor Yellow

# Navigate to project directory
$projectDir = "s:\Projects\SLAIC001_Infinite\kade-connect"
Set-Location $projectDir

# Create Python virtual environment
if (!(Test-Path "venv")) {
    python -m venv venv
}

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Install Python dependencies
if (Test-Path "backend\requirements.txt") {
    Write-Host "📋 Installing Python packages..." -ForegroundColor Cyan
    pip install --upgrade pip
    pip install -r backend\requirements.txt
}

Write-Host "📱 Setting up Node.js environment..." -ForegroundColor Yellow

# Install global Node.js packages
$nodePackages = @(
    "@expo/cli",
    "create-react-app",
    "typescript",
    "@react-native-community/cli"
)

foreach ($package in $nodePackages) {
    Write-Host "Installing $package..." -ForegroundColor Cyan
    npm install -g $package
}

Write-Host "🐳 Setting up Docker environment..." -ForegroundColor Yellow

# Check if Docker is running
try {
    docker version > $null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Docker Desktop may need to be started manually" -ForegroundColor Yellow
}

Write-Host "📄 Creating configuration files..." -ForegroundColor Yellow

# Copy environment file if it doesn't exist
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file from template" -ForegroundColor Green
    Write-Host "⚠️ Please edit .env file with your API keys" -ForegroundColor Yellow
}

Write-Host "🎉 Development environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your API keys" -ForegroundColor White
Write-Host "2. Start Docker Desktop" -ForegroundColor White
Write-Host "3. Run: docker-compose up -d" -ForegroundColor White
Write-Host "4. Open VS Code: code ." -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation: See PROJECT_SETUP.md for detailed instructions" -ForegroundColor Cyan

# Pause to show results
Read-Host "Press Enter to continue..."
