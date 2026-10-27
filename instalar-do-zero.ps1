# ============================================================================
# Instalador do ZERO — Agents-Modelagem (Windows / PowerShell)
# ============================================================================
# Pra quem nunca usou Claude nem Git. Cole UMA linha no PowerShell:
#
#   irm https://raw.githubusercontent.com/smallfiver/Agents-Modelagem/master/instalar-do-zero.ps1 | iex
#
# O que faz: instala o Git (se faltar), baixa este repositório em
# %USERPROFILE%\Agents-Modelagem (ou atualiza, se já existir) e roda o
# instalar.ps1, que instala o resto (Node, ffmpeg, Python, Claude Code,
# Vercel CLI, a skill e os sub-agents).
# Rodar de novo = atualizar pra versão mais nova.
# ============================================================================

$ErrorActionPreference = "Stop"
$repo = "https://github.com/smallfiver/Agents-Modelagem.git"
$pasta = Join-Path $env:USERPROFILE "Agents-Modelagem"

function Atualizar-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "[erro] 'winget' não encontrado. Atualize o 'Instalador de Aplicativo' na Microsoft Store e rode de novo." -ForegroundColor Red
    return
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[instalando] Git..." -ForegroundColor Yellow
    winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements
    Atualizar-Path
}

if (Test-Path (Join-Path $pasta ".git")) {
    Write-Host "[atualizando] $pasta" -ForegroundColor Cyan
    git -C $pasta pull --ff-only
} else {
    Write-Host "[baixando] $repo -> $pasta" -ForegroundColor Cyan
    git clone $repo $pasta
}

powershell -ExecutionPolicy Bypass -File (Join-Path $pasta "instalar.ps1")
