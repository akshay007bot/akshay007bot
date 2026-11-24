# Jarvis installer for Windows 10/11.
# Run from this folder in PowerShell:
#   powershell -ExecutionPolicy Bypass -File .\install.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "== Jarvis installer ==" -ForegroundColor Cyan

# 1. Python 3.10-3.12 (best wheel support for audio/AI packages)
$py = $null
foreach ($v in "3.12", "3.11", "3.10") {
    try { & py -$v --version *> $null; if ($LASTEXITCODE -eq 0) { $py = "py -$v"; break } } catch {}
}
if (-not $py) {
    Write-Host "Python 3.12 not found. Installing it with winget..." -ForegroundColor Yellow
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    $py = "py -3.12"
}
Write-Host "Using $py"

# 2. Virtual environment + packages
if (-not (Test-Path .venv)) { Invoke-Expression "$py -m venv .venv" }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. Settings file
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Created .env - add your free GEMINI_API_KEY in it (https://aistudio.google.com/apikey)." -ForegroundColor Yellow
}

# 4. Download the wake word + speech models now, so the first start is fast
& .\.venv\Scripts\python.exe -m jarvis.setup_models

Write-Host ""
Write-Host "Done. Next steps:" -ForegroundColor Green
Write-Host "  1. notepad .env            (paste your Gemini key)"
Write-Host "  2. Double-click run.bat     (voice mode - say 'Hey Jarvis')"
Write-Host "     or run-text.bat          (type instead of talk)"
Write-Host "  Optional: install Ollama from https://ollama.com and run 'ollama pull qwen3:8b' for offline use."
