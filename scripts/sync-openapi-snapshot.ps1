#Requires -Version 5.1
<#
.SYNOPSIS
  Fetches GET /api/openapi.json from a running service and writes docs/openapi/snapshots/<ServiceName>.openapi.json
.EXAMPLE
  ./scripts/sync-openapi-snapshot.ps1 -BaseUrl "http://127.0.0.1:8000" -ServiceName "auth"
.EXAMPLE
  ./scripts/sync-openapi-snapshot.ps1 -BaseUrl "http://127.0.0.1:8002" -ServiceName "directory" -BasicAuthUser "USERNAME" -BasicAuthPassword "PASSWORD"
#>
param(
    [Parameter(Mandatory = $true)]
    [string] $BaseUrl,
    [Parameter(Mandatory = $true)]
    [string] $ServiceName,
    [string] $OutDir = "docs/openapi/snapshots",
    [string] $BasicAuthUser = "",
    [string] $BasicAuthPassword = ""
)

$ErrorActionPreference = "Stop"
$uri = $BaseUrl.TrimEnd("/") + "/api/openapi.json"
$repoRoot = Split-Path $PSScriptRoot -Parent
$dir = Join-Path $repoRoot $OutDir
$outFile = Join-Path $dir "$ServiceName.openapi.json"

New-Item -ItemType Directory -Force -Path $dir | Out-Null
$headers = @{}
if ($BasicAuthUser -and $BasicAuthPassword) {
    $pair = $BasicAuthUser + ":" + $BasicAuthPassword
    $b64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
    $headers["Authorization"] = "Basic $b64"
}
Invoke-WebRequest -Uri $uri -OutFile $outFile -UseBasicParsing -Headers $headers
Write-Host "Wrote $outFile"
