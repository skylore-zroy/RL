param(
    [switch]$FreeBase,
    [switch]$Simulate,
    [switch]$Headless,
    [switch]$LowResource
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$python = if ($env:ISAACSIM_PYTHON) { $env:ISAACSIM_PYTHON } else { 'D:\is5\Scripts\python.exe' }

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Isaac Sim Python not found: $python"
}

$arguments = @(
    (Join-Path $projectRoot 'scripts\open_cod_isaac.py'),
    (Join-Path $projectRoot 'models\cod_balance\usd\COD-2026RoboMaster-Balance.usd')
)
if ($FreeBase) { $arguments += '--free-base' }
if ($Simulate) { $arguments += '--simulate' }
if ($Headless) { $arguments += '--headless' }
if ($LowResource) { $arguments += '--low-resource' }

$env:OMNI_KIT_ACCEPT_EULA = 'YES'
& $python @arguments
exit $LASTEXITCODE