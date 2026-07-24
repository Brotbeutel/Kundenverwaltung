# setup_dev_env.ps1
# Bootstrap-Skript für Windows, das die normale Python-Installation verwendet und eine virtuelle Umgebung einrichtet.

$scriptRoot = $PSScriptRoot
$projectRoot = Split-Path $scriptRoot -Parent
Set-Location $projectRoot

$pythonPath = "C:\Users\Student\AppData\Local\Python\bin\python.exe"
if (-Not (Test-Path $pythonPath)) {
    Write-Error "Python nicht gefunden: $pythonPath"
    exit 1
}

$venvPath = Join-Path $projectRoot ".venv"
$activatePath = Join-Path $venvPath "Scripts\Activate.ps1"
$pythonInVenv = Join-Path $venvPath "Scripts\python.exe"

Write-Host "Using Python: $pythonPath"
if (-Not (Test-Path $pythonInVenv)) {
    & $pythonPath -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment."
        exit $LASTEXITCODE
    }
}
else {
    Write-Host "Using existing virtual environment at $venvPath"
}

if (-Not (Test-Path $activatePath)) {
    Write-Error "Virtual environment activation script not found: $activatePath"
    exit 1
}

Write-Host "Upgrading pip..."
& $pythonInVenv -m pip install --upgrade pip
Write-Host "Installing requirements..."
& $pythonInVenv -m pip install -r "$scriptRoot\requirements.txt"

if (-Not (Test-Path "$projectRoot\.env") -and (Test-Path "$scriptRoot\.env.example")) {
    Copy-Item "$scriptRoot\.env.example" "$projectRoot\.env"
    Write-Host ".env file created from .env.example. Please edit .env before running the app."
}

Write-Host "Bootstrap complete. Run 'python App/init_db.py' and then 'python App/app.py'."
