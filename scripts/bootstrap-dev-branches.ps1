#Requires -Version 5.1
<#
.SYNOPSIS
  Creates or updates `dev` from `master` in every git submodule (services/*, frontend/*).
  Run from repo root: .\scripts\bootstrap-dev-branches.ps1
#>
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

$paths = @(
  "services/auth", "services/catalog", "services/commerce", "services/counterparties",
  "services/custom", "services/directory", "services/fulfillment", "services/inventory",
  "services/notification", "services/oms", "services/payments", "services/procurement",
  "services/production", "services/wms",
  "frontend/market", "frontend/system"
)

foreach ($rel in $paths) {
  $p = Join-Path $root $rel
  if (-not (Test-Path $p)) { Write-Warning "Skip missing: $rel"; continue }
  Write-Host "=== $rel ===" -ForegroundColor Cyan
  Push-Location $p
  try {
    git fetch origin
    git checkout master
    git pull origin master
    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    git rev-parse --verify dev 2>$null | Out-Null
    $hasDev = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $old
    if ($hasDev) {
      git checkout dev
      git merge master -m "Merge branch 'master' into dev"
    } else {
      git checkout -b dev
    }
    git push -u origin dev
  } finally {
    Pop-Location
  }
}

Write-Host "Done. All submodules on dev pushed to origin." -ForegroundColor Green
