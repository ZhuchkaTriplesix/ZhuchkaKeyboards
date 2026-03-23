#Requires -Version 5.1
<#
.SYNOPSIS
  Creates baseline GitHub issues in each submodule and in the monorepo (run once; re-run duplicates).

  Usage: .\scripts\gh-create-issues.ps1

  If gh fails with a TLS timeout, create any missing issues manually for that repo (compare with siblings).
#>
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

function New-Issue {
  param([string]$Path, [string]$Title, [string]$Body)
  Push-Location $Path
  try {
    gh issue create --title $Title --body $Body
  } finally {
    Pop-Location
  }
}

function Generic-BackendBody {
  param([string]$Label, [string]$DocHint)
  $lines = @(
    "Context: service $Label."
    "Details: docs/microservices/ and docs/microservices-api-requirements.md"
    $DocHint
    "Open PRs against dev; in the PR description use Refs #issue-number."
  )
  return ($lines -join "`n")
}

$backendServices = @(
  @{ path = "services/auth";           label = "auth" },
  @{ path = "services/catalog";        label = "catalog" },
  @{ path = "services/commerce";       label = "commerce" },
  @{ path = "services/counterparties"; label = "counterparties" },
  @{ path = "services/custom";         label = "custom" },
  @{ path = "services/directory";      label = "directory" },
  @{ path = "services/fulfillment";    label = "fulfillment" },
  @{ path = "services/inventory";      label = "inventory" },
  @{ path = "services/notification";  label = "notification" },
  @{ path = "services/oms";            label = "oms" },
  @{ path = "services/payments";       label = "payments" },
  @{ path = "services/procurement";    label = "procurement" },
  @{ path = "services/production";     label = "production" },
  @{ path = "services/wms";            label = "wms" }
)

foreach ($svc in $backendServices) {
  $p = Join-Path $root $svc.path
  $L = $svc.label
  $b = Generic-BackendBody -Label $L -DocHint "See docs/microservices/README.md and the service-specific doc file."

  New-Issue $p "[$L] CI: ruff, pytest, Docker image" $b
  New-Issue $p "[$L] OpenAPI 3 and /api/openapi.json" $b
  New-Issue $p "[$L] Alembic migrations and domain DB schema" $b
  New-Issue $p "[$L] REST /api/v1 endpoints per docs" $b
  New-Issue $p "[$L] Events: outbox and message schemas" $b
  New-Issue $p "[$L] Integration tests and API smoke" $b
  New-Issue $p "[$L] Observability: /metrics, logs, request_id" $b
  New-Issue $p "[$L] Auth: JWT scopes (auth-service contract)" $b
  New-Issue $p "[$L] Docs: README, DEPLOYMENT, env vars" $b

  if ($L -eq "auth") {
    $ab = @"
docs/microservices/01-auth.md; architecture IAM (domain).
PR to dev. Do not mix storefront Google/Telegram with staff-only login.
"@
    New-Issue $p "[auth] Google OIDC federation for storefront customers" $ab
    New-Issue $p "[auth] Telegram Login Widget (hash verification)" $ab
    New-Issue $p "[auth] customer/staff identity_kind and external identities" $ab
    New-Issue $p "[auth] Authorization Code + PKCE for storefront public client" $ab
    New-Issue $p "[auth] Optional POST /oauth/introspect" $ab
    New-Issue $p "[auth] Admin API: CRUD OAuth clients (beyond bootstrap)" $ab
  }
}

$frontends = @(
  @{ path = "frontend/market";  name = "market";  role = "storefront" },
  @{ path = "frontend/system"; name = "system"; role = "staff console" }
)
foreach ($fe in $frontends) {
  $p = Join-Path $root $fe.path
  $n = $fe.name
  $r = $fe.role
  $fb = "Flutter web $n ($r). UI: docs/frontend-requirements.md. PR to dev."

  New-Issue $p "[$n] M3 theme, OLED #000000, surface tokens" $fb
  New-Issue $p "[$n] Routing (go_router) and app shell" $fb
  New-Issue $p "[$n] HTTP client (dio/http), errors, retry" $fb
  New-Issue $p "[$n] Auth state and token storage (web)" $fb
  New-Issue $p "[$n] CI: flutter analyze, test, build web" $fb
  if ($n -eq "market") {
    New-Issue $p "[market] Login: Google and Telegram (auth-service)" $fb
    New-Issue $p "[market] Catalog and cart placeholders for backend" $fb
  } else {
    New-Issue $p "[system] Staff login only (password or SSO), no social" $fb
    New-Issue $p "[system] Table views: lists and filters prototype" $fb
  }
  New-Issue $p "[$n] A11y: focus, semantics, browser zoom" $fb
  New-Issue $p "[$n] Empty/loading/error states" $fb
  New-Issue $p "[$n] i18n (intl) RU/EN baseline" $fb
  New-Issue $p "[$n] README: run, build, env" $fb
}

$monoBody = "Monorepo ZhuchkaKeyboards. Branch from dev, PR to dev. See docs/git-workflow.md."
$mono = @(
  "Monorepo: MkDocs (or similar) for static docs",
  "Monorepo: local docker-compose (Postgres, Redis, Traefik)",
  "Monorepo: checklist for submodule bumps after service releases",
  "Monorepo: policy dev to main merge in submodules",
  "Monorepo: PR template (tests, migrations, breaking changes)",
  "Monorepo: secrets and example env files (no real keys)",
  "Monorepo: Traefik routes map to services (document)",
  "Monorepo: sync docs with submodule OpenAPI periodically"
)
foreach ($t in $mono) {
  gh issue create --title $t --body $monoBody
}

Write-Host "Finished creating issues." -ForegroundColor Green
