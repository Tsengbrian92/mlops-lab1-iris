$env:Path = "$PSScriptRoot\tools;$PSScriptRoot\.venv\Scripts;" + $env:Path
$dockerBin = Join-Path $env:LOCALAPPDATA 'Programs\DockerDesktop\resources\bin'
if (Test-Path -LiteralPath $dockerBin) { $env:Path = "$dockerBin;" + $env:Path }
Set-Location -LiteralPath $PSScriptRoot
Write-Host 'Lab environment ready: python, mlflow, uvicorn, kind, kubectl, hey'
