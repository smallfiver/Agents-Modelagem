# CLAUDE.md — Mapa vivo do Agents-Modelagem

Esta é a **visão única** da estrutura: orquestrador, sub-agents, skills,
scripts e referências. O Claude Code a carrega automaticamente neste
repositório, e o agente é responsável por **mantê-la atualizada e por melhorar
a estrutura** (seção 8).

---

## 1. Princípio

> **O orquestrador só orquestra. Cada tarefa tem um sub-agent próprio.**

O orquestrador pergunta ao usuário, despacha o agent certo, confere o status e
entrega. Não baixa página, não lê HTML bruto, não roda script, não edita
oferta. As fases conversam por arquivos em `_handoff/`, não por contexto.

## 2. Estrutura de arquivos

```
D:\Agents-Modelagem\
├── CLAUDE.md                      ← este mapa (fonte única da estrutura)
├── README.md                      ← uso e instalação para humanos
├── instalar.ps1 / instalar.sh     ← instalam skill + agents em ~/.claude/
├── agents/                        ← 19 sub-agents → ~/.claude/agents/
│   ├── clonagem-recon.md              diagnóstico
│   ├── clonagem-cloaking.md
│   ├── clonagem-ocultos.md
│   ├── clonagem-mapa.md
│   ├── clonagem-limpeza.md
│   ├── clonagem-vsl-detector.md       vídeo
│   ├── clonagem-pitch.md
│   ├── clonagem-checkout.md
│   ├── clonagem-vsl-download.md
│   ├── clonagem-transcricao.md
│   ├── clonagem-presell.md            construção
│   ├── clonagem-oferta.md
│   ├── clonagem-upsell-downsell.md
│   ├── clonagem-backredirect.md
│   ├── clonagem-qa.md                 gate
│   ├── clonagem-deploy-vercel.md      entrega
│   ├── clonagem-lovable.md
│   ├── clonagem-dominio.md
│   └── clonagem-relatorio.md
└── Agents-Modelagem\              ← skill orquestradora → ~/.claude/skills/Agents-Modelagem/
    ├── SKILL.md                   ← o orquestrador (perguntas, fluxo, regras)
    ├── references\                ← conhecimento lido sob demanda pelos agents
    │   ├── playbook-detalhado.md      (passos completos + lições aprendidas)
    │   ├── estrutura-pasta-oferta.md
    │   ├── extrair-vsl-vturb.md
    │   ├── trackers-para-remover.md
    │   ├── deploy-vercel.md
    │   ├── dominio-hostinger-vercel.md
    │   ├── template-dossie-cloaking.md
    │   └── template-relatorio-oferta.md
    └── scripts\                   ← automações determinísticas (gates)
        ├── mapear_pagina.py
        ├── checar_cloaking.py
        ├── decodificar_pixel_ofuscado.py
        ├── limpar_ocultos.py
        └── comprimir_vsl_2pass.py
```

Saída de cada oferta (fora do repo): `C:\Ofertas\<Nome>\{presell,oferta,vsl,_handoff}` + `RELATORIO.md`.

## 3. Orquestrador

| item | valor |
|---|---|
| Skill | `Agents-Modelagem` (`Agents-Modelagem/SKILL.md`), entrada: `/Agents-Modelagem <url>` |
| Papel | pergunta, despacha, confere status, decide o próximo passo, entrega |
| Não faz | nenhuma tarefa de execução — nem em pedido pontual (despacha só o agent daquela tarefa) |
| Perguntas iniciais (1 chamada) | **tipo** (front-end/upsell/downsell/back-redirect) · **destino** (Vercel/Lovable) · **transcrever a VSL?** |
| Perguntas condicionais | mapa diverge do tipo · cloaking confirmado, continua? · **2+ VSLs: só a principal ou todas?** · autorizar instalar whisper · domínio próprio (Vercel) |

## 4. Fluxo

```
perguntas ─► recon ─► cloaking ─► ocultos ─► mapa ─► limpeza
                                                       │
                      ┌── há vídeo? ──── não ──────────┤
                      ▼                                │
              vsl-detector ─► (pitch ∥ checkout ∥ vsl-download) por variante ─► transcricao*
                                                       │   * só se pediu
                      ┌────────────────────────────────┘
                      ▼
   front-end: presell ∥ oferta │ upsell/downsell │ back-redirect
                      ▼
                     qa ──(reprovou: volta ao agent de construção, máx. 2)
                      ▼
        Vercel: deploy-vercel ─► [pergunta domínio] ─► dominio
        Lovable: lovable
                      ▼
                  relatorio ─► entrega
```

## 5. Sub-agents (uma tarefa cada)

| # | agent | tarefa única | modelo | edita arquivos? | escreve (`_handoff/`) |
|---|---|---|---|---|---|
| 1 | `clonagem-recon` | baixar página, mapear plataforma/player/trackers | sonnet | só `page.html` | `01-recon.md` |
| 2 | `clonagem-cloaking` | provar/descartar cloaking (HTTP + JS) | sonnet | não | `02-cloaking.md` |
| 3 | `clonagem-ocultos` | analisar botões/links ocultos | sonnet | **não** | `03-ocultos.md` |
| 4 | `clonagem-mapa` | inventário completo + confirmar tipo | sonnet | **não** | `04-mapa.md` |
| 5 | `clonagem-limpeza` | base limpa: sem tracking nem ocultos | sonnet | `oferta/index.html` | `05-limpeza.md` |
| 6 | `clonagem-vsl-detector` | quantas VSLs, A/B, pesos | sonnet | não | `06-vsl-detector.md` |
| 7 | `clonagem-pitch` | segundo **exato** do pitch (por variante) | sonnet | não | `07-pitch-<v>.md` |
| 8 | `clonagem-checkout` | checkout real + valor (por variante) | sonnet | não | `08-checkout-<v>.md` |
| 9 | `clonagem-vsl-download` | baixar, comprimir, ffprobe (por variante) | sonnet | `vsl/`, `oferta/vsl.mp4` | `09-vsl-download-<v>.md` |
| 10 | `clonagem-transcricao` | transcrever com timestamps (se pedido) | sonnet | `vsl/transcricao-*.md` | `10-transcricao-<v>.md` |
| 11 | `clonagem-presell` | presell com CTA no topo (front-end) | herda | `presell/` | `11-presell.md` |
| 12 | `clonagem-oferta` | oferta + `<video>` + reveal no pitch (front-end) | herda | `oferta*/` | `12-oferta.md` |
| 13 | `clonagem-upsell-downsell` | aceitar/recusar | herda | `oferta/` | `13-upsell-downsell.md` |
| 14 | `clonagem-backredirect` | standalone sem history hijack | herda | `oferta/` | `14-backredirect.md` |
| 15 | `clonagem-qa` | gate independente | sonnet | **não corrige** | `15-qa.md` |
| 16a | `clonagem-deploy-vercel` | deploy + curl | sonnet | não | `16-deploy-vercel.md` |
| 16b | `clonagem-lovable` | zip para Lovable (sem vídeo/node_modules) | sonnet | `*.zip` | `16-lovable.md` |
| 17 | `clonagem-dominio` | domínio próprio (só se confirmado) | sonnet | não | `17-dominio.md` |
| 18 | `clonagem-relatorio` | `RELATORIO.md` | sonnet | `RELATORIO.md` | `18-relatorio.md` |

Agents "por variante" rodam **uma instância por VSL**, em paralelo. Tools: os
de leitura/análise usam `Bash, Read, Write, Glob, Grep`; os que alteram
arquivos acrescentam `Edit`.

## 6. Skills utilizadas

| skill | onde | quando |
|---|---|---|
| `Agents-Modelagem` | `Agents-Modelagem/SKILL.md` | orquestrador — ponto de entrada |
| `deploy-vercel-github` *(externa, opcional)* | skills do usuário | alternativa/consulta para deploy |
| `cloaker-agente` *(externa, opcional)* | skills do usuário | referência cruzada; **não** é dependência |

> Ao passar a depender de uma nova skill (nossa ou externa), registre aqui.

## 7. Regras invariantes (valem para todo o time)

- Sem formulários com dados reais; sem avançar a pagamento.
- Reportar só o observado, com comandos; "não verificado" quando não verificou.
- Layout, copy e prova social são replicados; só tracking sai. Sequestro do
  botão voltar e urgência com data falsa **não entram** no clone, mas são
  documentados.
- Gates obrigatórios: grep de tracking = 0, `limpar_ocultos.py` exit 0,
  `ffprobe` da duração batendo, pitch com segundo exato, deploy validado por
  `curl`.
- Sub-agents não falam com o usuário e não mexem em DNS sem instrução. Só o
  orquestrador fala com o usuário.

---

## 8. Autoaperfeiçoamento (instruções ao agente)

Sempre que você alterar a **estrutura** — criar, renomear, remover ou mudar o
papel de um agent, skill, script ou referência — faça no mesmo trabalho:

1. **Atualize este arquivo**: árvore (seção 2), tabelas (3–6) e uma linha no
   "Registro de melhorias" (data, o que mudou, por quê).
2. Atualize o que depende disso: `SKILL.md` (fluxo/tabela), `README.md`
   (tabela de agents e árvore) e os instaladores se mudou o que é copiado.
3. Se a mudança vier de uma **falha real observada** numa oferta (gate que
   deixou passar algo, etapa que travou, pergunta que faltou), registre a
   lição na referência certa (`playbook-detalhado.md` ou o agent afetado) e
   descreva a falha no registro — não só o conserto.

**Fim de cada oferta** (orquestrador, depois do `18-relatorio.md`):
mini-retrospecto de 3 linhas — o que travou, qual gate pegou/deixou passar, o
que automatizar. Melhoria concreta e de baixo risco: aplique (via edição do
repo). Maior (novo agent, mudança de ordem): **proponha ao usuário** antes.

**Limites:** não apague agents/gates sem pedido explícito; não afrouxe um gate
para uma oferta passar; não commite sem o usuário pedir.

### Backlog de melhorias (candidatas, ainda não feitas)

- [ ] `clonagem-qa` com navegador real obrigatório (hoje "não verificado" é aceito).
- [ ] Script `validar_handoff.py` que confere se os handoffs esperados existem e têm status `OK`.
- [ ] Script de transcrição em `scripts/` (hoje o agent escolhe a ferramenta na hora).
- [ ] Instaladores removerem agents antigos (`clonagem-vsl`, `clonagem-builder`, `clonagem-deploy`) de `~/.claude/agents/`.
- [ ] Reaproveitar `_handoff/` de ofertas anteriores como exemplos de referência.
- [ ] Listar `limpar_ocultos.py` no README.

### Registro de melhorias

| data | mudança | motivo |
|---|---|---|
| 2026-10-04 | Skill virou orquestrador; criados 5 sub-agents; playbook movido p/ `references/playbook-detalhado.md` | contexto do orquestrador limpo, QA independente de quem constrói |
| 2026-10-04 | Nova ordem: cloaking → ocultos → mapa; builders por tipo; handoffs 01–07 | cloaking primeiro, análise antes de limpar |
| 2026-10-04 | Criado `CLAUDE.md` (este mapa vivo) | visão única da estrutura e melhoria contínua |
| 2026-10-04 | **Um sub-agent por tarefa (19 agents)**: `vsl`→`vsl-detector`+`pitch`+`checkout`+`vsl-download`+`transcricao`; `builder`→`limpeza`+`presell`+`oferta`+`upsell-downsell`+`backredirect`; `deploy`→`deploy-vercel`+`lovable`+`dominio`+`relatorio`; `recon` separado de `cloaking`; `mapa` virou só leitura. Perguntas iniciais (tipo, destino, transcrever) e detecção de 2+ VSLs com variantes | pedido do usuário: orquestrador só orquestra, cada tarefa com dono único |
