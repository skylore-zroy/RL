$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

docker build `
    --file (Join-Path $projectRoot 'docker\isaacsim\Dockerfile') `
    --tag 'cod-isaac-lab:2.2.0-local' `
    $projectRoot

exit $LASTEXITCODE