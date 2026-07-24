# setup_dev_env.ps1
# Bootstrap-Skript für Windows, das die normale Python-Installation verwendet und eine virtuelle Umgebung einrichtet.

$scriptRoot = $PSScriptRoot
Set-Location $scriptRoot

$pythonPath = "C:\Users\Student\AppData\Local\Python\bin\python.exe"
if (-Not (Test-Path $pythonPath)) {
    Write-Error "Python nicht gefunden: $pythonPath"
    exit 1
}

$venvPath = Join-Path $scriptRoot ".venv"
$activatePath = Join-Path $venvPath "Scripts\Activate.ps1"

Write-Host "Using Python: $pythonPath"
& $pythonPath -m venv $venvPath
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create virtual environment."
    exit $LASTEXITCODE
}

Write-Host "Activating virtual environment..."
. $activatePath
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to activate virtual environment. Run '. $activatePath' manually."
    exit $LASTEXITCODE
}

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip
Write-Host "Installing requirements..."
python -m pip install -r requirements.txt

if (-Not (Test-Path .env) -and (Test-Path .env.example)) {
    Copy-Item .env.example .env
    Write-Host ".env file created from .env.example. Please edit .env before running the app."
}

Write-Host "Bootstrap complete. Run 'python init_db.py' and then 'python app.py'."
