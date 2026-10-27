# Agents-Modelagem

Um comando, uma URL de oferta: a skill investiga cloaking, extrai a VSL, limpa
todo rastreamento, monta presell + oferta organizadas e sobe na Vercel — com
relatório documentando cada etapa.

---

## 🚀 Começando do zero (nunca usou Claude nem IA? comece aqui)

Siga na ordem. Leva uns 15 minutos. Tudo no **Windows 10 ou 11**.

### Passo 1 — Ter uma conta Claude paga
Crie sua conta em [claude.ai](https://claude.ai) e assine o plano **Pro** ou
**Max**. O plano grátis não roda o Claude Code.

### Passo 2 — Abrir o PowerShell
Aperte a tecla **Windows**, digite **PowerShell** e clique em
**Windows PowerShell**. Vai abrir uma janela azul/preta. É nela que você cola
os comandos.

### Passo 3 — Colar o comando de instalação
Copie a linha abaixo, cole no PowerShell (botão direito do mouse cola) e
aperte **Enter**:

```powershell
irm https://raw.githubusercontent.com/smallfiver/Agents-Modelagem/master/instalar-do-zero.ps1 | iex
```

Ele instala sozinho: Git, Node.js, ffmpeg, Python, transcrição
(faster-whisper), Claude Code, Vercel e o próprio agente. Se o Windows
perguntar "Deseja permitir alterações?", clique **Sim**. Espere aparecer
**"== Tudo pronto =="**.

> Deu erro no meio? Feche o PowerShell, abra de novo e cole o mesmo comando.
> Ele continua de onde parou.

### Passo 4 — Entrar no Claude
**Feche o PowerShell e abra de novo** (obrigatório). Depois digite:

```powershell
claude
```

Na primeira vez abre o navegador: entre com a conta do Passo 1 e autorize.
Volte pro PowerShell.

### Passo 5 — Testar
Dentro do Claude, digite `/Agents-Modelagem`. Se aparecer na lista, está
instalado. Para modelar uma oferta:

```
/Agents-Modelagem https://link-da-oferta.com
```

### Passo 6 — Configurar para publicar e vender (uma vez só)
| O quê | Pra quê | Como |
|---|---|---|
| **Vercel** | publicar presell e oferta na internet | crie conta em [vercel.com](https://vercel.com) e rode `vercel login` no PowerShell (fora do Claude) |
| **Vturb** (2 chaves) | subir a VSL e o botão no segundo do pitch | no painel da Vturb pegue a chave de **Analytics** e a da **API de Vídeos** (começa com `vt_`). São **diferentes**. No PowerShell: `setx VTURB_API_KEY "SUA_CHAVE_ANALYTICS"` e `setx VTURB_VIDEOS_API_KEY "SUA_CHAVE_VIDEOS"`. Feche e reabra o PowerShell |
| **Kirvano** | criar produto e checkout (só ofertas BR) | conecte a Kirvano como conector em [claude.ai](https://claude.ai) → Configurações → Conectores. Peça o passo a passo ao seu mentor |

> **Nunca** cole suas chaves em arquivo nem mande no grupo. Só no `setx`.

### Atualizar para a versão mais nova
Cole o mesmo comando do Passo 3 de novo. Ele baixa a versão nova e reinstala.

### Mac / Linux
Abra o Terminal e rode:
```bash
git clone https://github.com/smallfiver/Agents-Modelagem.git && cd Agents-Modelagem && bash instalar.sh
```

---

## Requisitos

O que precisa estar instalado na máquina **antes** de usar a skill:

| requisito | pra que serve | como checar |
|---|---|---|
| **Node.js 18+** | roda o Claude Code CLI | `node --version` |
| **Git** | clonar este repo, e algumas ofertas usam `git` internamente | `git --version` |
| **ffmpeg** | baixar e recomprimir os vídeos das VSLs | `ffmpeg -version` |
| **Claude Code** | é o agente que lê e executa a skill | `claude --version` |
| **Python 3.12 + faster-whisper** | scripts da skill e transcrição da VSL | `python --version` |
| **Vercel CLI** | publicar presell e oferta | `vercel --version` |

Não precisa instalar nada disso manualmente um por um — o instalador abaixo
faz tudo de uma vez.

## 0. Instalar tudo do zero

**Opção A — instalador automático** (recomendado, cobre requisitos + skill):

```bash
git clone https://github.com/smallfiver/Agents-Modelagem.git
cd Agents-Modelagem
```

Windows (PowerShell):
```powershell
powershell -ExecutionPolicy Bypass -File .\instalar.ps1
```

macOS / Linux:
```bash
bash instalar.sh
```

O script (`instalar.ps1` / `instalar.sh`) checa Node.js, Git, ffmpeg e o
Claude Code — instala o que estiver faltando (via `winget` no Windows,
`brew`/`apt` no Mac/Linux) — e já copia a pasta da skill pro lugar certo.

**Opção B — manual**, se preferir controlar cada passo:

```bash
git clone https://github.com/smallfiver/Agents-Modelagem.git
npm install -g @anthropic-ai/claude-code
```

Copie a pasta `Agents-Modelagem/` inteira para dentro de:

```
%USERPROFILE%\.claude\skills\Agents-Modelagem\
```

e os arquivos de `agents/*.md` para `%USERPROFILE%\.claude\agents\`.

Confirme que ficaram lá dentro: `SKILL.md`, a pasta `references/` e a pasta
`scripts/`. Se faltar uma, a cópia ficou incompleta.

**Testar:** abra o Claude Code numa pasta de projeto qualquer, rode `claude`
pra autenticar (abre o navegador na primeira vez), e digite
`/Agents-Modelagem` — se aparecer no autocomplete, está
instalada.

Pra manter atualizado depois, é só `git pull` neste repo e rodar o
instalador de novo (ele sobrescreve a skill com a versão atual).

---

## 1. O prompt-mestre

Cole isso no Claude Code, troque a URL, e mande. Ele carrega o playbook
completo da skill e já sai executando: reconhecimento, cloaking, VSL,
limpeza, montagem, validação, deploy e relatório.

```
/Agents-Modelagem https://URL-DA-OFERTA-AQUI/

Replicar essa oferta por completo, seguindo o playbook padrão:
- Checar cloaking antes de clonar (HTTP com 3+ identidades e depois confirmar
  com navegador real renderizando JS — não parar só na checagem HTTP)
- Extrair a VSL: achar o player.js (inclusive testes A/B), o segundo exato
  do pitch, o link de checkout real, e baixar o vídeo completo pro computador
  (confirmar duração com ffprobe, recomprimir se passar de ~95MB)
- Se algum script vier ofuscado (atob/XOR), decodificar e documentar o que
  carregava, não ignorar
- Limpar TODO o tracking: Meta Pixel, GTM/GA4, UTMify, pixels ofuscados,
  qualquer link ou botão invisível — zero rastreamento no clone final
- Montar a estrutura em C:\Ofertas\<Nome-Da-Oferta>\ com presell (obrigatória,
  botão de CTA no topo) + oferta (layout replicado por completo, sem
  simplificar prova social/depoimentos/footer) + reveal automático do
  checkout no segundo certo do pitch
- Validar tudo no navegador antes de finalizar: 0 imagens quebradas, sem
  overflow horizontal no mobile (375px), grep de tracking residual = 0
- Fazer deploy na Vercel (presell e oferta como dois projetos, com
  vercel.json de SPA rewrite) e validar o deploy publicado com curl
- Escrever o RELATORIO.md completo: cloaking checado, pitch, checkout,
  valor da oferta, tracking removido, padrões manipulativos documentados
  (não replicados por padrão)
```

Troca só a primeira linha (a URL). O resto é o padrão fixo — não precisa
reescrever a cada oferta.

> **Destino não é mais escolha**: toda oferta sobe sempre nos dois — Vercel
> (deploy direto) **e** Lovable (zip, sem vídeo nem `node_modules`).
>
> Pra vender a oferta de verdade (produto + checkout próprio), acrescente:
> *"subir o produto na Kirvano (preço conforme dito na transcrição do pitch)
> e subir o vídeo com o CTA configurado na Vturb"* — o **orquestrador**
> (não um sub-agent) confirma nome, preço e capa com você e escreve direto
> na Kirvano; a Vturb usa a API de Vídeos própria (não a de Analytics) e
> sobe/configura o CTA sozinha — só o link de embed do player é sempre um
> passo manual no painel, avisado assim que o upload termina.

---

## 2. Como o fluxo roda

Um sub-agent por tarefa (21 no total, ver `CLAUDE.md` §4), sempre nessa
ordem. A skill já sabe disso pelo `SKILL.md` — isto é só pra você entender o
que está vendo rodar.

| fase | agents | o que faz |
|---|---|---|
| Diagnóstico | `recon` → `cloaking` → `ocultos` → `mapa` → `limpeza` | baixa a página, prova/descarta cloaking (`checar_cloaking.py` + `analisar_script_decisor.py`), analisa ocultos, confirma o tipo, gera a base limpa (zero tracking). |
| Vídeo (se houver) | `vsl-detector` → por variante: `pitch` ∥ `checkout` ∥ `vsl-download` → `transcricao` (opcional) | detecta VSL(s)/teste A/B, segundo exato do pitch, checkout real, baixa e recomprime o vídeo, transcreve se pedido. |
| Comercialização (condicional, só se confirmar que vai vender de verdade) | `kirvano` (só lê/prepara plano) → orquestrador escreve na Kirvano+Canva → `vturb` | produto+checkout+capa+ebook: o plano sai do `kirvano`, mas quem cria/escreve de verdade na Kirvano é o orquestrador (confirmação do dono antes); upload+CTA na Vturb via **Videos API**. |
| Construção | `presell` (já roda em paralelo desde a Limpeza) · `oferta` · `upsell-downsell` · `backredirect` | monta a página conforme o tipo — layout replicado por completo, reveal automático no segundo certo. |
| Gate | `qa` | verifica sem corrigir (reprovado volta ao agent de construção, máx. 2 ciclos). |
| Entrega | `deploy-vercel` ∥ `lovable` (sempre os dois) → `dominio` (se pedido) → `relatorio` | deploy validado por curl, zip pra Lovable, domínio próprio opcional, `RELATORIO.md`. |

---

## 3. Estrutura entregue

Sempre a mesma organização — não importa qual oferta, você sabe de cor onde
procurar cada coisa.

```
C:\Ofertas\<Nome-Da-Oferta>\
├── RELATORIO.md               ← checklist preenchido, sempre
├── presell\                   ← página 1: explicação + botão no topo
│   └── src\App.tsx                 (OFFER_URL configurável)
├── oferta\                    ← página 2: VSL + reveal automático
│   ├── index.html
│   ├── vsl.mp4                     (versão compacta, a que sobe)
│   └── assets\
└── vsl\                       ← arquivos-fonte, não sobem pro deploy
    ├── <nome>-vsl.mp4              (qualidade original)
    └── <nome>-vsl-compact.mp4      (a usada em oferta/vsl.mp4)
```

---

## 4. O que sempre é removido

Confirmado por grep, nunca só por leitura visual — inclusive o que vem
escondido em base64/XOR pra escapar de scanner simples.

- [x] **Meta Pixel / fbevents** — `fbq(`, `connect.facebook.net`
- [x] **Google Ads / GA4 / GTM** — `gtag(`, `googletagmanager`
- [x] **UTMify, Clarity, Hotjar, TikTok Pixel** — script visível *e* pixel oculto/ofuscado
- [x] **Script de atribuição cross-domain** — fbclid/_fbp/_fbc repassado pro checkout
- [x] **Player de terceiros** (VTurb/converteai, Panda) — trocado por vídeo self-hosted
- [x] **Boilerplate WordPress/Elementor** — feeds, oEmbed, wp-json, xmlrpc

Verificação final, deve dar **0**:

```bash
grep -icE 'fbq\(|gtag\(|googletagmanager|connect\.facebook|utm_source=|clarity|hotjar|converteai|vturb|utmify' index.html
```

---

## 5. Deploy na Vercel

Dois projetos por oferta — um pra presell, um pra oferta. O limite de 100MB
por arquivo é real: se o vídeo passar de ~95MB, a skill recomprime antes de
tentar subir.

```bash
cd C:\Ofertas\<Nome>\presell
vercel deploy --prod --yes --name <nome>-presell

cd C:\Ofertas\<Nome>\oferta
vercel deploy --prod --yes --name <nome>-oferta

# validação pós-deploy — nunca confiar só no "Aliased ✓"
curl -sL -o /dev/null -w "root HTTP %{http_code}\n" https://SEU-DEPLOY.vercel.app/
curl -sI https://SEU-DEPLOY.vercel.app/vsl.mp4 | grep -iE "HTTP|content-length"
```

Nome de projeto Vercel só aceita minúsculas, números, `.` `_` `-` — sem `---`
seguido.

---

## 6. Regras do jogo

A skill já tem esses limites embutidos — vale entender por que existem, não
é burocracia.

**Sempre replica** (é conteúdo de marketing, não tracking):
- Layout, copy, depoimentos, prova social
- A mecânica de personalização (quiz, cartas) mesmo quando o resultado é
  sempre o mesmo
- O segundo exato do pitch, extraído do player original

**Nunca faz:**
- Preencher formulário com dado real ou avançar até pagamento investigando
  um checkout
- Entregar clone que ainda dispara pixel/analytics de outra pessoa
- Replicar sequestro de botão voltar ou urgência com data falsa — isso é
  documentado no relatório, não copiado silenciosamente

---

## 7. Orquestrador + sub-agents

O `SKILL.md` é um **orquestrador que só orquestra**: pergunta, despacha,
confere status e entrega. **Cada tarefa tem um sub-agent próprio** (21 no
total), e eles conversam por arquivos em `_handoff/`. O mapa completo e vivo
está em [`CLAUDE.md`](CLAUDE.md).

**Perguntas no início** (uma só vez): tipo da página (front-end, upsell,
downsell, back-redirect) e se transcreve a VSL. Depois, só quando necessário:
se o mapa divergir do tipo, se houver 2+ VSLs (clonar só a principal ou
todas), **se vai vender de verdade (Kirvano + Vturb)**, domínio próprio.
Destino de deploy não é mais pergunta — sobe sempre nos dois.

| fase | agents |
|---|---|
| Diagnóstico | `recon` → `cloaking` → `ocultos` → `mapa` → `limpeza` |
| Vídeo (se houver) | `vsl-detector` → por variante: `pitch` ∥ `checkout` ∥ `vsl-download` → `transcricao` (opcional) |
| Comercialização (condicional) | `kirvano` (só plano/leitura) → orquestrador escreve na Kirvano+Canva (com confirmação do dono) → `vturb` (upload + CTA via API de Vídeos da Vturb) |
| Construção | front-end: `presell` (em paralelo desde a Limpeza) · `oferta` · `upsell-downsell` · `backredirect` |
| Gate | `qa` (reprovado volta ao agent de construção, máx. 2 ciclos) |
| Entrega | `deploy-vercel` ∥ `lovable` (sempre os dois) → [`dominio` se pedido] → `relatorio` |

Todos têm o prefixo `clonagem-` e vivem em `agents/`; o instalador copia para
`~/.claude/agents/`. O playbook completo continua em
`references/playbook-detalhado.md`.

---

## Estrutura deste repositório

```
.
├── README.md                          ← este arquivo
├── CLAUDE.md                          ← mapa vivo da arquitetura
├── agents/                            ← 21 sub-agents (vão pra ~/.claude/agents/)
│   └── clonagem-*.md                      recon, cloaking, ocultos, mapa, limpeza,
│                                          vsl-detector, pitch, checkout, vsl-download,
│                                          transcricao, kirvano, vturb, presell, oferta,
│                                          upsell-downsell, backredirect, qa,
│                                          deploy-vercel, lovable, dominio, relatorio
└── Agents-Modelagem/    ← a skill orquestradora, pronta pra copiar
    ├── SKILL.md
    ├── references/
    │   ├── playbook-detalhado.md
    │   ├── deploy-vercel.md
    │   ├── dominio-hostinger-vercel.md
    │   ├── estrutura-pasta-oferta.md
    │   ├── extrair-vsl-vturb.md
    │   ├── template-dossie-cloaking.md
    │   ├── template-relatorio-oferta.md
    │   └── trackers-para-remover.md
    └── scripts/
        ├── analisar_script_decisor.py
        ├── checar_cloaking.py
        ├── comprimir_vsl_2pass.py
        ├── decodificar_pixel_ofuscado.py
        ├── limpar_ocultos.py
        └── mapear_pagina.py
```
