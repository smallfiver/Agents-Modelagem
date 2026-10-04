# CLAUDE.md — Mapa vivo do Agents-Modelagem

Este arquivo é a **visão única** de toda a estrutura: orquestrador, sub-agents,
skills, scripts e referências. Ele é carregado automaticamente pelo Claude
Code neste repositório e **o agente é responsável por mantê-lo atualizado e
por melhorar a estrutura** (regras na seção "Autoaperfeiçoamento").

> Última revisão estrutural: ver o topo do "Registro de melhorias" (fim do arquivo).

---

## 1. Visão geral

Pipeline que clona ofertas/funis de VSL: checa cloaking, mapeia e limpa o
original, monta o clone conforme o tipo de página, valida, faz deploy e
entrega com `RELATORIO.md`. Um **orquestrador** (skill) despacha **sub-agents
especialistas**; as fases conversam por arquivos em `_handoff/`, não por
contexto.

```
recon ─► ocultos ─► mapa ─► [pergunta: tipo] ─► vsl* ─► builder ─► qa ─► [pergunta: domínio] ─► deploy
                                                 *só se houver vídeo      └─ reprovou: volta ao builder (máx. 2)
```

## 2. Estrutura de arquivos

```
D:\Agents-Modelagem\
├── CLAUDE.md                      ← este mapa (fonte única da estrutura)
├── README.md                      ← uso e instalação para humanos
├── instalar.ps1 / instalar.sh     ← instalam skill + agents em ~/.claude/
├── agents/                        ← sub-agents  → ~/.claude/agents/
│   ├── clonagem-recon.md
│   ├── clonagem-ocultos.md
│   ├── clonagem-mapa.md
│   ├── clonagem-vsl.md
│   ├── clonagem-builder.md
│   ├── clonagem-qa.md
│   └── clonagem-deploy.md
└── Agents-Modelagem\              ← skill orquestradora → ~/.claude/skills/Agents-Modelagem/
    ├── SKILL.md                   ← o orquestrador (fluxo, perguntas, regras)
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
| Skill | `Agents-Modelagem` (`Agents-Modelagem/SKILL.md`) |
| Papel | divide em fases, despacha sub-agents, confere gates, fala com o usuário |
| Pergunta ao usuário | (1) tipo da página, (2) domínio próprio — **só ele pergunta** |
| Não faz | trabalho pesado (HTML bruto, ffmpeg, grep ficam nos sub-agents) |
| Exceção | pedido pequeno e pontual → executa o passo do playbook direto |

## 4. Sub-agents

| # | agent | modelo | tools | lê | escreve (`_handoff/`) | usa (scripts/refs) |
|---|---|---|---|---|---|---|
| 1 | `clonagem-recon` | sonnet | Bash, Read, Write, Glob, Grep | URL | `page.html`, `01-recon.md` | `mapear_pagina.py`, `checar_cloaking.py`, `decodificar_pixel_ofuscado.py`, `template-dossie-cloaking.md` |
| 2 | `clonagem-ocultos` | sonnet | Bash, Read, Write, Glob, Grep | `page.html`, 01 | `02-ocultos.md` (**só analisa**) | `limpar_ocultos.py` (modo lista) |
| 3 | `clonagem-mapa` | sonnet | Bash, Read, Write, Edit, Glob, Grep | `page.html`, 01, 02 | `03-mapa.md` + base limpa `oferta/index.html` + **tipo sugerido** | `limpar_ocultos.py`, `trackers-para-remover.md`, `decodificar_pixel_ofuscado.py` |
| 4 | `clonagem-vsl` | sonnet | Bash, Read, Write, Glob, Grep | 01, 03 | `04-vsl.md`, vídeos em `vsl/` e `oferta/vsl.mp4` | `extrair-vsl-vturb.md`, `comprimir_vsl_2pass.py` |
| 5 | `clonagem-builder` | herda da sessão | Bash, Read, Write, Edit, Glob, Grep | 01–04, `tipo` | `05-build.md`, presell/oferta finais | `estrutura-pasta-oferta.md`, `trackers-para-remover.md`, `limpar_ocultos.py` |
| 6 | `clonagem-qa` | sonnet | Bash, Read, Write, Glob, Grep | 01–05, `tipo` | `06-qa.md` (**não corrige**) | `limpar_ocultos.py`, ffprobe, grep |
| 7 | `clonagem-deploy` | sonnet | Bash, Read, Write, Edit, Glob, Grep | 01–06, domínio | `07-deploy.md`, `RELATORIO.md` | `deploy-vercel.md`, `dominio-hostinger-vercel.md`, `template-relatorio-oferta.md` |

Tipos de página suportados pelo builder/qa/deploy: `front-end` · `upsell` ·
`downsell` · `back-redirect` · `outro` (devolve BLOQUEADO).

## 5. Skills utilizadas

| skill | onde | quando |
|---|---|---|
| `Agents-Modelagem` | `Agents-Modelagem/SKILL.md` | orquestrador — ponto de entrada (`/Agents-Modelagem <url>`) |
| `deploy-vercel-github` *(opcional, externa)* | skills do usuário | alternativa ao deploy manual |
| `anthropic-skills:cloaker-agente` / `clonagem-funil…` *(externas)* | skills do usuário | só como referência cruzada; **não** são dependências |

> Ao passar a depender de uma nova skill (nossa ou externa), registre aqui.

## 6. Regras invariantes (valem para todo o time)

- Sem formulários com dados reais; sem avançar a pagamento.
- Reportar só o observado, com comandos; "não verificado" quando não verificou.
- Layout, copy e prova social são replicados; só tracking sai. Sequestro do
  botão voltar e urgência com data falsa **não entram** no clone, mas são
  documentados.
- Gates são obrigatórios: grep de tracking = 0, `limpar_ocultos.py` exit 0,
  `ffprobe` da duração batendo, deploy validado por `curl`.
- Sub-agents não falam com o usuário e não mexem em DNS.

---

## 7. Autoaperfeiçoamento (instruções ao agente)

Sempre que você (orquestrador ou sub-agent) **alterar a estrutura** — criar,
renomear, remover ou mudar o papel de um agent, skill, script ou referência —
faça no mesmo trabalho:

1. **Atualize este arquivo**: árvore (seção 2), tabelas (3–5) e uma linha no
   "Registro de melhorias" (data, o que mudou, por quê).
2. Atualize junto o que depende disso: `SKILL.md` (fluxo/tabela), `README.md`
   (tabela de agents e árvore) e os instaladores se mudou o que é copiado.
3. Se a mudança vier de uma **falha real observada** numa oferta (gate que
   deixou passar algo, etapa que travou, pergunta que faltou), registre a
   lição na referência certa (`playbook-detalhado.md` ou o agent afetado) e
   descreva a falha no registro — não só o conserto.

**Fim de cada oferta** (orquestrador, depois do `07-deploy.md`): faça um
mini-retrospecto de 3 linhas — o que travou, qual gate pegou/deixou passar,
o que automatizar. Se houver melhoria concreta e de baixo risco, aplique;
se for maior (novo agent, mudança de ordem), **proponha ao usuário** antes.

**Limites:** não apague agents/gates existentes sem pedido explícito; não
afrouxe um gate para fazer uma oferta passar; não commite sem o usuário pedir.

### Backlog de melhorias (candidatas, ainda não feitas)

- [ ] Agent separado para upsell/downsell (hoje é um bloco dentro do builder).
- [ ] `clonagem-qa` com navegador real obrigatório (hoje "não verificado" é aceito).
- [ ] Script `validar_handoff.py` que confere se 01–07 existem e têm status `OK`.
- [ ] Reaproveitar `_handoff/` de ofertas anteriores como exemplos de referência.
- [ ] Versionar `scripts/limpar_ocultos.py` (está sem commit) e listá-lo no README.

### Registro de melhorias

| data | mudança | motivo |
|---|---|---|
| 2026-10-04 | Skill virou orquestrador; criados 5 sub-agents (`recon`, `vsl`, `builder`, `qa`, `deploy`); playbook movido p/ `references/playbook-detalhado.md` | contexto do orquestrador limpo, QA independente de quem constrói |
| 2026-10-04 | Nova ordem sequencial: criados `clonagem-ocultos` e `clonagem-mapa`; pergunta de tipo (front-end/upsell/downsell/back-redirect); handoffs renumerados 01–07 | cloaking primeiro, análise de ocultos antes de limpar, builder por tipo |
| 2026-10-04 | Criado `CLAUDE.md` (este mapa vivo) | visão única da estrutura e melhoria contínua |
