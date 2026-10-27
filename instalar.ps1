# ============================================================================
# Instalador — Clonar Funil & Detectar Cloaking (Windows / PowerShell)
# ============================================================================
# Roda tudo do zero: checa/instala Node.js, Git, ffmpeg e o Claude Code,
# clona este repositório (se ainda não estiver clonado) e instala a skill
# em %USERPROFILE%\.claude\skills\Agents-Modelagem\
#
# Uso:
#   1. Clone este repo primeiro (ou use o instalar-do-zero.ps1, ver README):
#        git clone https://github.com/smallfiver/Agents-Modelagem.git Agents-Modelagem
#   2. Entre na pasta clonada e rode este script:
#        cd Agents-Modelagem
#        powershell -ExecutionPolicy Bypass -File .\instalar.ps1
# ============================================================================

$ErrorActionPreference = "Stop"

function Test-Comando($nome) {
    return [bool](Get-Command $nome -ErrorAction SilentlyContinue)
}

Write-Host "== Verificando requisitos ==" -ForegroundColor Cyan

# ---- Node.js ----
if (Test-Comando "node") {
    Write-Host "[ok] Node.js já instalado: $(node --version)" -ForegroundColor Green
} else {
    Write-Host "[instalando] Node.js (LTS) via winget..." -ForegroundColor Yellow
    winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
    Write-Host "Node.js instalado. Pode ser necessário reabrir o terminal se o próximo passo falhar." -ForegroundColor Yellow
}

# ---- Git ----
if (Test-Comando "git") {
    Write-Host "[ok] Git já instalado: $(git --version)" -ForegroundColor Green
} else {
    Write-Host "[instalando] Git via winget..." -ForegroundColor Yellow
    winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements
}

# ---- ffmpeg (necessário pra baixar/recomprimir as VSLs) ----
if (Test-Comando "ffmpeg") {
    Write-Host "[ok] ffmpeg já instalado." -ForegroundColor Green
} else {
    Write-Host "[instalando] ffmpeg via winget..." -ForegroundColor Yellow
    winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
}

# ---- Python (scripts da skill e transcrição) ----
# Windows tem um atalho falso "python" da Microsoft Store; só conta se responder a versão
$pyVersao = if (Test-Comando "python") { python --version 2>$null } else { $null }
if ($pyVersao) {
    Write-Host "[ok] Python já instalado: $pyVersao" -ForegroundColor Green
} else {
    Write-Host "[instalando] Python 3.12 via winget..." -ForegroundColor Yellow
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
}

# winget não atualiza o PATH desta janela; recarrega pra npm/pip funcionarem já
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")

# ---- faster-whisper (transcrição da VSL) ----
Write-Host "[instalando/conferindo] faster-whisper..." -ForegroundColor Yellow
python -m pip install --user --quiet faster-whisper

# ---- Claude Code CLI ----
Write-Host ""
Write-Host "== Instalando o Claude Code ==" -ForegroundColor Cyan
if (Test-Comando "claude") {
    Write-Host "[ok] Claude Code já instalado." -ForegroundColor Green
} else {
    npm install -g @anthropic-ai/claude-code
}

# ---- Vercel CLI (publicar presell e oferta) ----
if (Test-Comando "vercel") {
    Write-Host "[ok] Vercel CLI já instalado." -ForegroundColor Green
} else {
    npm install -g vercel
}

# ---- Instalar a skill ----
Write-Host ""
Write-Host "== Instalando a skill ==" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$origemSkill = Join-Path $scriptDir "Agents-Modelagem"
$destinoSkills = Join-Path $env:USERPROFILE ".claude\skills"
$destinoSkill = Join-Path $destinoSkills "Agents-Modelagem"

if (-not (Test-Path $origemSkill)) {
    Write-Host "[erro] Não achei a pasta 'Agents-Modelagem' ao lado deste script." -ForegroundColor Red
    Write-Host "Confirme que você rodou este .ps1 de dentro da pasta do repositório clonado." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $destinoSkills)) {
    New-Item -ItemType Directory -Force -Path $destinoSkills | Out-Null
}

if (Test-Path $destinoSkill) {
    Write-Host "Já existe uma skill instalada em $destinoSkill — substituindo pela versão atual do repo." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $destinoSkill
}

Copy-Item -Recurse -Force $origemSkill $destinoSkill
Write-Host "[ok] Skill instalada em: $destinoSkill" -ForegroundColor Green

# ---- Instalar os sub-agents (time do orquestrador) ----
$origemAgents = Join-Path $scriptDir "agents"
$destinoAgents = Join-Path $env:USERPROFILE ".claude\agents"

# Remove agents antigos (nomes trocados em 04/10) pra não ficarem duplicados/obsoletos
$agentsAntigos = @("clonagem-vsl.md", "clonagem-builder.md", "clonagem-deploy.md")
foreach ($antigo in $agentsAntigos) {
    $caminhoAntigo = Join-Path $destinoAgents $antigo
    if (Test-Path $caminhoAntigo) {
        Remove-Item -Force $caminhoAntigo
        Write-Host "[limpeza] Removido agent antigo: $antigo" -ForegroundColor Yellow
    }
}

if (Test-Path $origemAgents) {
    New-Item -ItemType Directory -Force -Path $destinoAgents | Out-Null
    Copy-Item -Force (Join-Path $origemAgents "*.md") $destinoAgents
    Write-Host "[ok] Sub-agents instalados em: $destinoAgents" -ForegroundColor Green
} else {
    Write-Host "[aviso] Pasta 'agents' não encontrada — o orquestrador vai funcionar sem sub-agents dedicados." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "== Checando chaves da Vturb (antes do primeiro uso real do clonagem-vturb) ==" -ForegroundColor Cyan
# A Vturb tem DUAS chaves diferentes: VTURB_API_KEY (Analytics, X-Api-Token,
# só leitura) e VTURB_VIDEOS_API_KEY (Videos API, bearer vt_..., upload+CTA).
# Só confere se os NOMES existem no ambiente — nunca lê nem imprime o valor.
$temApiKey = [bool]$env:VTURB_API_KEY
$temVideosKey = [bool]$env:VTURB_VIDEOS_API_KEY
if ($temApiKey -and $temVideosKey) {
    Write-Host "[ok] VTURB_API_KEY e VTURB_VIDEOS_API_KEY estão definidas." -ForegroundColor Green
} elseif ($temApiKey -or $temVideosKey) {
    $faltando = if ($temApiKey) { "VTURB_VIDEOS_API_KEY" } else { "VTURB_API_KEY" }
    Write-Host "[aviso] Só uma das duas chaves da Vturb está definida — falta $faltando." -ForegroundColor Yellow
    Write-Host "        Analytics (X-Api-Token) e Videos API (bearer vt_...) são chaves DIFERENTES;" -ForegroundColor Yellow
    Write-Host "        colar uma por cima da outra apaga a que já existia. Confirme com o dono antes do clonagem-vturb." -ForegroundColor Yellow
} else {
    Write-Host "[aviso] Nenhuma das duas chaves da Vturb (VTURB_API_KEY / VTURB_VIDEOS_API_KEY) está definida." -ForegroundColor Yellow
    Write-Host "        Normal se ainda não for comercializar de verdade; necessário antes de rodar o clonagem-vturb." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "== Tudo pronto ==" -ForegroundColor Cyan
Write-Host "1. Feche e reabra o PowerShell (garante que o PATH do Node/Git/ffmpeg/Python atualizou)."
Write-Host "2. Digite 'claude' e aperte Enter. Na primeira vez abre o navegador: entre com sua conta Claude (plano Pro ou Max)."
Write-Host "3. Dentro do Claude, digite '/Agents-Modelagem' — se aparecer na lista, está instalado."
Write-Host "4. Pra publicar ofertas: rode 'vercel login' uma vez (fora do Claude)."
Write-Host "Passo a passo completo (chaves Vturb, Kirvano): README do repositório."
