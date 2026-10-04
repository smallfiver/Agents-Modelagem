#!/usr/bin/env bash
# ============================================================================
# Instalador — Clonar Funil & Detectar Cloaking (macOS / Linux)
# ============================================================================
# Checa/instala Node.js, Git, ffmpeg e o Claude Code, e instala a skill
# em ~/.claude/skills/Agents-Modelagem/
#
# Uso:
#   git clone https://github.com/smallfiver/Agents-Modelagem.git
#   cd Agents-Modelagem
#   bash instalar.sh
# ============================================================================

set -e

echo "== Verificando requisitos =="

tem_comando() { command -v "$1" >/dev/null 2>&1; }

# ---- Node.js ----
if tem_comando node; then
  echo "[ok] Node.js já instalado: $(node --version)"
else
  echo "[aviso] Node.js não encontrado."
  if tem_comando brew; then
    echo "[instalando] Node.js via Homebrew..."
    brew install node
  else
    echo "Instale o Node.js 18+ manualmente: https://nodejs.org e rode este script de novo."
    exit 1
  fi
fi

# ---- Git ----
if tem_comando git; then
  echo "[ok] Git já instalado: $(git --version)"
else
  echo "[aviso] Git não encontrado."
  if tem_comando brew; then
    echo "[instalando] Git via Homebrew..."
    brew install git
  elif tem_comando apt-get; then
    sudo apt-get update && sudo apt-get install -y git
  else
    echo "Instale o git manualmente e rode este script de novo."
    exit 1
  fi
fi

# ---- ffmpeg (necessário pra baixar/recomprimir as VSLs) ----
if tem_comando ffmpeg; then
  echo "[ok] ffmpeg já instalado."
else
  echo "[aviso] ffmpeg não encontrado."
  if tem_comando brew; then
    echo "[instalando] ffmpeg via Homebrew..."
    brew install ffmpeg
  elif tem_comando apt-get; then
    sudo apt-get update && sudo apt-get install -y ffmpeg
  else
    echo "Instale o ffmpeg manualmente e rode este script de novo."
    exit 1
  fi
fi

# ---- Claude Code CLI ----
echo ""
echo "== Instalando o Claude Code =="
if tem_comando claude; then
  echo "[ok] Claude Code já instalado."
else
  npm install -g @anthropic-ai/claude-code
fi

# ---- Instalar a skill ----
echo ""
echo "== Instalando a skill =="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORIGEM_SKILL="$SCRIPT_DIR/Agents-Modelagem"
DESTINO_SKILLS="$HOME/.claude/skills"
DESTINO_SKILL="$DESTINO_SKILLS/Agents-Modelagem"

if [ ! -d "$ORIGEM_SKILL" ]; then
  echo "[erro] Não achei a pasta 'Agents-Modelagem' ao lado deste script."
  echo "Confirme que você rodou este instalar.sh de dentro da pasta do repositório clonado."
  exit 1
fi

mkdir -p "$DESTINO_SKILLS"

if [ -d "$DESTINO_SKILL" ]; then
  echo "Já existe uma skill instalada em $DESTINO_SKILL — substituindo pela versão atual do repo."
  rm -rf "$DESTINO_SKILL"
fi

cp -r "$ORIGEM_SKILL" "$DESTINO_SKILL"
echo "[ok] Skill instalada em: $DESTINO_SKILL"

# ---- Instalar os sub-agents (time do orquestrador) ----
ORIGEM_AGENTS="$SCRIPT_DIR/agents"
DESTINO_AGENTS="$HOME/.claude/agents"
if [ -d "$ORIGEM_AGENTS" ]; then
  mkdir -p "$DESTINO_AGENTS"
  cp "$ORIGEM_AGENTS"/*.md "$DESTINO_AGENTS/"
  echo "[ok] Sub-agents instalados em: $DESTINO_AGENTS"
else
  echo "[aviso] Pasta 'agents' não encontrada — o orquestrador vai funcionar sem sub-agents dedicados."
fi

echo ""
echo "== Tudo pronto =="
echo "1. Feche e reabra o terminal (garante que o PATH atualizou)."
echo "2. Rode 'claude' numa pasta qualquer para autenticar (abre o navegador)."
echo "3. Digite '/Agents-Modelagem' — se aparecer no autocomplete, a skill está instalada."
