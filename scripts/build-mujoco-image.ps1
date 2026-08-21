$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

docker build `
    --file (Join-Path $projectRoot 'docker\mujoco\Dockerfile') `
    --tag 'cod-mujoco:3.2.6-local' `
    $projectRoot

exit $LASTEXITCODE