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
├── agents/                        ← 21 sub-agents → ~/.claude/agents/
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
│   ├── clonagem-kirvano.md            comercialização (condicional)
│   ├── clonagem-vturb.md
│   ├── clonagem-presell.md            construção
│   ├── clonagem-oferta.md
│   ├── clonagem-upsell-downsell.md
│   ├── clonagem-backredirect.md
│   ├── clonagem-qa.md                 gate
│   ├── clonagem-deploy-vercel.md      entrega (sempre os dois)
│   ├── clonagem-lovable.md            (sempre os dois)
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
        ├── analisar_script_decisor.py
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
| Perguntas iniciais (1 chamada, até 4 perguntas) | **tipo** (front-end/upsell/downsell/back-redirect) · **transcrever a VSL?** · **vai vender de verdade (Kirvano/Vturb)?** (só se `tipo=front-end`) · **domínio próprio?** (+ qual/método, se sim) |
| Perguntas condicionais (só depois de descoberta técnica de um sub-agent) | mapa diverge do tipo · cloaking confirmado, continua? · **2+ VSLs: só a principal ou todas?** · autorizar instalar whisper |
| Destino | **não é pergunta** — sempre sobe nos dois, Vercel e Lovable, em paralelo |

## 4. Fluxo

```
perguntas ─► recon ─► cloaking ─► ocultos ─► mapa ─► limpeza
                                                       │
            ┌──────────────────────────────────────────┴──────────────────────────────────┐
            ▼ ramo A (só front-end) — já pode rodar                ▼ ramo B — segue normalmente
       clonagem-presell                                  há vídeo? ── não ──────────────────┐
       (OFFER_URL provisório;                                    │ sim                       │
        patch final só depois do deploy)             vsl-detector ─► (pitch ∥ checkout ∥ vsl-download) por variante ─► transcricao*
            │                                                    │   * só se pediu
            │                                      ┌──────────────┴──► Agents-Copy-VSL (paralelo, não bloqueia o resto)
            │                                      ┌──────────────────────────────────────────┘
            │                                      ▼
            │                        [pergunta: vender de verdade?] ──sim──► kirvano (lê) ─► orquestrador escreve na Kirvano+Canva ─► vturb ──┐
            │                                      │ não                                                                                       │
            │                                      └───────────────────────────────────────────────────────────────────────────────────────────┤
            │                                      ▼
            │                     front-end: oferta │ upsell/downsell │ back-redirect
            │                                      │
            └──────────────────────────────────────┤
                                                     ▼
                                                    qa ──(reprovou: volta ao agent de construção, máx. 2)
                                                     ▼
                                     deploy-vercel ∥ lovable  (sempre os dois) ─► patch de OFFER_URL final na presell
                                                     │
                                     verificação AO VIVO pós-deploy (obrigatória, navegador real nas URLs publicadas)
                                                     │
                                     [pergunta domínio próprio] ─► dominio (se sim)
                                                     ▼
                                                 relatorio ─► entrega
```

## 5. Sub-agents (uma tarefa cada)

| # | agent | tarefa única | modelo | edita arquivos? | escreve (`_handoff/`) |
|---|---|---|---|---|---|
| 1 | `clonagem-recon` | baixar página, mapear plataforma/player/trackers | sonnet | só `page.html` | `01-recon.md` |
| 2 | `clonagem-cloaking` | provar/descartar cloaking (HTTP + JS + análise estática do script decisor) | sonnet | não | `02-cloaking.md` |
| 3 | `clonagem-ocultos` | analisar botões/links ocultos | sonnet | **não** | `03-ocultos.md` |
| 4 | `clonagem-mapa` | inventário completo + confirmar tipo | sonnet | **não** | `04-mapa.md` |
| 5 | `clonagem-limpeza` | base limpa: sem tracking nem ocultos | sonnet | `oferta/index.html` | `05-limpeza.md` |
| 6 | `clonagem-vsl-detector` | quantas VSLs, A/B, pesos | sonnet | não | `06-vsl-detector.md` |
| 7 | `clonagem-pitch` | segundo **exato** do pitch (por variante) | sonnet | não | `07-pitch-<v>.md` |
| 8 | `clonagem-checkout` | checkout real + valor (por variante) | sonnet | não | `08-checkout-<v>.md` |
| 9 | `clonagem-vsl-download` | baixar, comprimir, ffprobe (por variante) | sonnet | `vsl/`, `oferta/vsl.mp4` | `09-vsl-download-<v>.md` |
| 10 | `clonagem-transcricao` | transcrever com timestamps (se pedido) | sonnet | `vsl/transcricao-*.md` | `10-transcricao-<v>.md` |
| 11 | `clonagem-kirvano` | plano de venda (nome/preço/categoria) + ebook, a partir da transcrição; só LÊ a Kirvano (`whoami`, categorias/formatos, `products_get`) — a escrita real fica com o orquestrador | sonnet | `_handoff/` | `11-kirvano.md` |
| 12 | `clonagem-vturb` | sobe o vídeo e configura o CTA na Vturb via API de Vídeos (`api.vturb.com`, distinta da de Analytics) | sonnet | `_handoff/` | `12-vturb.md` |
| 13 | `clonagem-presell` | presell com CTA no topo (front-end) | herda | `presell/` | `13-presell.md` |
| 14 | `clonagem-oferta` | oferta + `<video>` (ou player Vturb, se houver) + reveal no pitch (front-end) | herda | `oferta*/` | `14-oferta.md` |
| 15 | `clonagem-upsell-downsell` | aceitar/recusar | herda | `oferta/` | `15-upsell-downsell.md` |
| 16 | `clonagem-backredirect` | standalone sem history hijack | herda | `oferta/` | `16-backredirect.md` |
| 17 | `clonagem-qa` | gate independente | sonnet | **não corrige** | `17-qa.md` |
| 18 | `clonagem-deploy-vercel` | deploy + curl — **sempre roda** (não é mais escolha) | sonnet | não | `18-deploy-vercel.md` |
| 19 | `clonagem-lovable` | zip para Lovable (sem vídeo/node_modules) — **sempre roda** | sonnet | `*.zip` | `19-lovable.md` |
| 20 | `clonagem-dominio` | domínio próprio (só se confirmado) | sonnet | não | `20-dominio.md` |
| 21 | `clonagem-relatorio` | `RELATORIO.md` | sonnet | `RELATORIO.md` | `21-relatorio.md` |

`clonagem-kirvano` e `clonagem-vturb` só rodam se o dono confirmar que vai
vender de verdade a oferta (pergunta condicional, seção 4). `clonagem-kirvano`
só LÊ a Kirvano (`whoami`, categorias/formatos, `products_get`) e prepara o
plano (nome/preço/categoria) e o ebook; a ESCRITA real na Kirvano
(`products_create`, `products_create_offer`, `products_create_checkout`,
`products_set_cover`, `products_add_content`, `products_request_contact_validation`,
`products_confirm_contact_validation`) e a geração da capa via Canva são
feitas pelo **ORQUESTRADOR diretamente**, depois de mostrar nome, preço e
capa ao dono e receber OK — ver seção 6 e seção 7.

`clonagem-presell` (tipo front-end) não depende da fase de Vídeo nem da
Comercialização — só da base limpa (`05-limpeza.md`). Pode começar a rodar
em paralelo com todo o resto do fluxo, logo depois de `clonagem-limpeza`. O
`OFFER_URL` fica provisório até o patch final, que só acontece depois do
deploy da oferta (fase 9).

Agents "por variante" rodam **uma instância por VSL**, em paralelo. Tools: os
de leitura/análise usam `Bash, Read, Write, Glob, Grep`; os que alteram
arquivos acrescentam `Edit`.

## 6. Skills utilizadas

| skill | onde | quando |
|---|---|---|
| `Agents-Modelagem` | `Agents-Modelagem/SKILL.md` | orquestrador — ponto de entrada |
| `deploy-vercel-github` *(externa, opcional)* | skills do usuário | alternativa/consulta para deploy |
| `cloaker-agente` *(externa, opcional)* | skills do usuário | referência cruzada; **não** é dependência |
| `pdf` *(externa, opcional)* | skills do usuário | `clonagem-kirvano`, se o dono preferir o ebook em PDF em vez de markdown |

> Ao passar a depender de uma nova skill (nossa ou externa), registre aqui.

### Ferramentas MCP usadas (fora de skill)

| ferramenta | onde | quando |
|---|---|---|
| Kirvano (`mcp__claude_ai_KIRVANO__*`) — leitura | `clonagem-kirvano` | `whoami`, `products_list_categories_and_formats`, `products_get`, `products_get_checkout` — só consulta e prepara o plano (nome/preço/categoria) pro orquestrador confirmar com o dono |
| Kirvano (`mcp__claude_ai_KIRVANO__*`) — escrita | **orquestrador**, direto (nunca despachado pro sub-agent) | `products_create`, `products_create_offer`, `products_create_checkout`, `products_set_cover`, `products_add_content`, `products_request_contact_validation`, `products_confirm_contact_validation` — **sempre com confirmação do dono (nome, preço, capa) antes de qualquer chamada**. Rodar no orquestrador evita o bloqueio do classificador de permissão ("Unrequested Commit in a Connected App") que ocorre quando um sub-agent sem o pedido do dono no próprio histórico tenta a mesma chamada — gap real observado na oferta "painosso" (20/10). **Logo depois de criar o checkout**, chame também `products_update_checkout` com `payment_methods: [{payment_method: 'BANK_SLIP', enabled: false}]` — todo checkout nasce com Boleto ligado e isso tem de ser desativado sempre, antes de entregar o `checkout_url` (regra permanente, seção 7) |
| Canva (`generate-image`/`create-design`) | **orquestrador**, direto | gerar a capa/banner do produto a partir do prompt preparado por `clonagem-kirvano` — evita o hop extra por um agent `general-purpose` separado + relay manual (gap real observado em "painosso") |
| Vturb **Videos API** (`https://api.vturb.com/v1`, bearer `vt_...`) | `clonagem-vturb` | Upload (multipart S3), confirmação, e `PATCH` de `call_actions` (CTA no segundo exato) + `general.pitch_time`. **Diferente** da Vturb Analytics API (`analytics.vturb.net`, header `X-Api-Token`, só leitura) que já estava documentada — token `[PENDENTE DE VALIDAÇÃO]`: confirmar se é o mesmo `VTURB_API_KEY` ou outro. Docs: `docs.vturb.com/pt/docs/reference/videos-api` |
| REA (`mcp__rea__*`, Reverse Engineer Anything) | `clonagem-cloaking` (principal: `capture_browser_scenario`, `inspect_web_page`, `list_browser_targets`, `trace_javascript_semantics`); `clonagem-vsl-detector` e `clonagem-mapa` (fallback secundário: `capture_browser_scenario`, `inspect_web_page`) | **Fallback**, só quando curl+grep/leitura estática não bastam pra confirmar decisão client-side (redirect por JS, config de player não inline). Uso só observacional — página pública do terceiro, sem login, sem burlar proteção (ver `DISCLAIMER.md` do REA) |

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
- **Dinheiro/produto real:** as chamadas de ESCRITA na Kirvano
  (`products_create`, `products_create_offer`, `products_create_checkout`,
  `products_set_cover`, `products_add_content`,
  `products_request_contact_validation`, `products_confirm_contact_validation`)
  são feitas pelo **orquestrador**, nunca despachadas pro `clonagem-kirvano`
  — ele só lê (`whoami`/categorias/`products_get`) e prepara plano + ebook.
  Motivo: o classificador de permissão do Claude Code bloqueia essas chamadas
  quando partem de um sub-agent sem o pedido do dono no próprio histórico de
  conversa, mesmo com o orquestrador já autorizado (gap real, oferta
  "painosso", 20/10). O orquestrador sempre mostra nome, preço e capa ao dono
  e espera confirmação explícita antes de escrever, mesmo com o fluxo já
  autorizado a "vender de verdade". Quando precisa gerar capa, o orquestrador
  usa o Canva MCP direto (mesmo motivo — evita o hop extra por um
  `general-purpose` separado). `clonagem-vturb` usa a **Videos API** real da
  Vturb (upload + CTA); nunca confunde com a API de Analytics (só leitura).
  **Embed sai pela API sim** — `GET /v1/videos/{id}/embed?type=js` devolve o
  snippet pronto (confirmado 21/10, corrige regra antiga que dizia "nunca sai
  pela API"). **Teste A/B real (`ab_tests`): o embed de vídeo avulso
  (`/players/{video_id}/v4/player.js`) NUNCA distribui o split — sempre mostra
  a mesma variante.** O embed que distribui de verdade usa
  `/ab-test/{ab_test_id}/player.js` (não `/players/`) com elemento
  `<vturb-smartplayer id="ab-{ab_test_id}">` (não `id="vid-{video_id}"`) —
  confirmado por teste direto (colar o id do `ab_test` como se fosse vídeo dá
  404; o path `/ab-test/` com esse mesmo id devolve 200 com `randomizer` e os
  pesos corretos). Sempre que existir `ab_test`, `clonagem-oferta` usa esse
  padrão de embed, nunca o de vídeo avulso de uma variante.
- **Retenção/play rate do player (Videos API, campos reais confirmados
  21/10):** depois de configurar `call_actions`/`pitch_time`, aplique por
  padrão via `PATCH /v1/videos/{id}`: `playback.disable_pause: true`,
  `playback.smart_pause: true`, `immersive_mode.enabled/mobile/expand_on_play:
  true`. Campos existem e documentados no schema devolvido pela própria API
  (não na doc pública, que não lista isso): `playback`, `resume` (já nasce
  `enabled:true`), `smart_autoplay` (já nasce `enabled:true`), `immersive_mode`,
  `turbo`, `thumbsniper`, `action_after_finish`. Testar com `?dry_run=true`
  antes de aplicar de verdade.
- **Checkout Kirvano sempre nasce com Boleto (BANK_SLIP) desativado** —
  desative explicitamente ao criar o checkout (`products_create_offer` cria
  o checkout padrão já ligado; chame `products_update_checkout` com
  `payment_methods: [{payment_method: 'BANK_SLIP', enabled: false}]` logo
  depois de criar a oferta, antes de entregar o `checkout_url` ao dono). Regra
  do orquestrador (quem faz a escrita real na Kirvano), não do
  `clonagem-kirvano`.
- **Destino de deploy não é escolha:** toda oferta sobe sempre nos dois,
  Vercel e Lovable, em paralelo.
- **Projeto Lovable real (via MCP, feito pelo orquestrador) sempre desativa o
  badge "Edit with Lovable"** antes de considerar a oferta pronta: tool
  `publish_settings--set_badge_visibility` (chamada pelo próprio Lovable via
  `send_message`, pergunte a ele — não existe tool MCP direta nossa pra isso)
  com `hide_badge: true`. Exige plano pago do workspace Lovable; se não tiver,
  avise o dono (toggle manual: nome do projeto → Settings → Project →
  General → "Hide 'Lovable' Badge"). Regra adicionada 21/10 — pedido do dono.

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

- [ ] `clonagem-qa` com navegador real obrigatório (hoje "não verificado" é aceito). **Grande** — muda o gate; proposta em `pendencias.md` do cérebro.
- [ ] Script `validar_handoff.py` que confere se os handoffs esperados existem e têm status `OK`. **Grande** — a lista de handoffs esperados depende do fluxo condicional (tipo, nº de VSLs, comercialização, domínio); proposta em `pendencias.md` do cérebro.
- [ ] Script de transcrição em `scripts/` (hoje o agent escolhe a ferramenta na hora). **Grande** — qual ferramenta/API usar é decisão do dono; proposta em `pendencias.md` do cérebro.
- [ ] Reaproveitar `_handoff/` de ofertas anteriores como exemplos de referência. **Grande** — depende de decidir qual pasta é "exemplo-padrão" e como os agents a acham; proposta em `pendencias.md` do cérebro.
- [x] Instaladores removerem agents antigos (`clonagem-vsl`, `clonagem-builder`, `clonagem-deploy`) de `~/.claude/agents/` — feito em 2026-10-20 (`instalar.ps1`/`instalar.sh` agora removem antes de copiar).
- [x] Listar `limpar_ocultos.py` no README — feito em 2026-10-20 (`README.md` §2/§3, árvore de scripts e references).

### Registro de melhorias

| data | mudança | motivo |
|---|---|---|
| 21/10/2026 (verificação ao vivo pós-deploy — passo 9.5 novo) | Novo passo obrigatório no fluxo, entre o deploy (9) e o relatório (10): verificar as URLs PUBLICADAS com navegador real (Playwright/REA), não só rodar QA antes do deploy. Checa `getComputedStyle` (cores/fonte) contra o clone real, imagens de prova social sendo fotos reais, embed do `ab_test` correto, badge Lovable realmente escondido, 0 erro de console. `SKILL.md` §4 (diagrama) e passo 9.5 novo; `CLAUDE.md` §4 diagrama atualizado. | Consolidação de TODOS os gaps da sessão de hoje: A/B não distribuía (vídeo avulso em vez do embed do teste), Vturb bloqueava o domínio publicado, tema da Lovable saiu completamente diferente (claro/dourado em vez de preto/branco), avatares viraram letra em vez de foto real, badge "Edit with Lovable" reapareceu sozinho depois de desativado. Nenhum desses foi pego pelo QA (que só roda antes do deploy, contra arquivo local) — só o dono testando a URL publicada encontrou, um de cada vez, ao longo da mesma sessão. O padrão repetido (achar só depois de publicar) é o sintoma; a causa raiz é não existir um gate que teste a URL real. |
| 21/10/2026 (embed A/B real + retenção) | Corrigida regra errada "embed nunca sai pela API" (sai sim, `GET /v1/videos/{id}/embed`). Descoberto e documentado o padrão certo de embed quando existe `ab_test`: `/ab-test/{ab_test_id}/player.js` + `id="ab-{ab_test_id}"`, nunca o embed de vídeo avulso de uma variante (esse nunca distribui tráfego, sempre mostra a mesma). Adicionado passo padrão de retenção pós-CTA: `playback.disable_pause`, `playback.smart_pause`, `immersive_mode` via `PATCH /v1/videos/{id}`, testado com `dry_run`. `CLAUDE.md` §7 atualizado; `SKILL.md` §4/§6 e os agents `clonagem-vturb`/`clonagem-oferta`/`clonagem-qa` precisam do mesmo ajuste (feito nesta sessão). | Oferta "saobento-antonio" (21/10): 2 VSLs com A/B real pedido pelo dono. `clonagem-oferta` colou o embed de vídeo avulso da V1 por falta de id "pai" documentado — QA aprovou sem pegar isso (não testava distribuição real). O dono perguntou "mais ta configurado o teste A/B" depois do deploy; só aí o orquestrador testou a API diretamente e achou o padrão certo. Gap real: nenhum gate do QA testava se o A/B de fato distribuía tráfego, só se o embed existia. Pedido explícito do dono também motivou configurar retenção (`disable_pause`/`immersive_mode`), que não existia como passo padrão. |
| 21/10/2026 (domínio Vturb + fidelidade literal) | 2 falhas novas achadas DEPOIS do deploy, viradas gate: (1) Vturb tem allowlist de domínio própria (`GET/POST /v1/domains`) — sem o domínio publicado (Vercel/Lovable) cadastrado lá, o player mostra "domínio não permitido" em produção mesmo com tudo certo no resto; virou passo 7 do `clonagem-vturb` e item 12 do `clonagem-qa`. (2) reconstrução de página por outra ferramenta (ex. Lovable) tem que copiar headline/depoimentos **literal**, nunca parafrasear — a 1ª versão da oferta via Lovable tinha texto inventado parecido mas diferente do clone real; virou regra no `clonagem-oferta` (item 3) e item 13 do QA. | Dono testou a oferta publicada e achou os dois: vídeo quebrado (erro de domínio, print mostrado) e texto da Lovable diferente do clone. Nenhum dos dois gates existia antes — QA só testava "o vídeo carrega localmente" e "o embed existe", não "funciona no domínio final" nem "o texto bate palavra por palavra". |
| 20/10/2026 (comercialização sempre ligada, Kirvano só BR) | Não existe mais pergunta "vai vender de verdade ou só clonar pra estudo": toda oferta modelada é **sempre** pra vender de verdade. A única variação passa a ser o **mercado**, determinado automaticamente (não é pergunta) a partir do que `clonagem-recon`/`clonagem-mapa` já descobrem (idioma, moeda, domínio, público). `mercado = BR` roda Kirvano + Vturb como já documentado; `mercado = não-BR` pula só a Kirvano (ela liquida apenas BRL) e segue com Vturb + deploy normalmente. Checkout pra oferta não-BR fica `[PENDENTE DE VALIDAÇÃO com o dono]`. Atualizado em `SKILL.md` §1 (perguntas iniciais), §4 (diagrama e passos 3/6) e §7 | decisão direta do dono: parar de perguntar "pra estudo ou pra vender" — é sempre pra vender; só o mercado muda o que roda (Kirvano exige BRL) |
| 20/10/2026 (boleto desativado por padrão) | Nova regra permanente: todo checkout criado na Kirvano (`products_create_offer`) nasce com Boleto (`BANK_SLIP`) ligado — o orquestrador agora **sempre** chama `products_update_checkout` com `payment_methods: [{payment_method: 'BANK_SLIP', enabled: false}]` logo depois de criar a oferta, antes de entregar o `checkout_url` ao dono. Regra do orquestrador (quem escreve na Kirvano), não do `clonagem-kirvano`. Entrou em `SKILL.md` §6 (passo de comercialização) e `CLAUDE.md` §6 (tabela MCP) e §7 (regra do dinheiro real) | pedido direto do dono: hoje já tinha sido corrigido manualmente no checkout da oferta "painosso"; precisa virar regra padrão pra não esquecer nas próximas ofertas |
| 2026-10-20 (perguntas unificadas) | `SKILL.md` seção 1: a mesma chamada inicial `AskUserQuestion` passa a perguntar também **vender de verdade (Kirvano/Vturb)** (só se `tipo=front-end`) e **domínio próprio** (+ qual/método) — antes eram perguntas condicionais feitas no meio do fluxo (passo 6 e passo 9). Passo 6 e passo 9 agora só **executam** com a resposta já coletada, sem perguntar de novo. Continuam condicionais de verdade (dependem de descoberta técnica de um sub-agent, não podem ser antecipadas): 2+ VSLs (depende do `clonagem-vsl-detector`) e autorizar instalar whisper (só se a transcrição falhar). Diagrama (seção 4) e tabela da seção 3 atualizados. | pedido do dono: parar de interromper no meio da execução — responder tudo de uma vez no início, com um prompt pronto pra colar (`Projects/Agente-de-Modelagem/prompt-rapido-nova-oferta.md` no cofre) |
| 2026-10-20 (otimização pós-"painosso") | `clonagem-kirvano` perde as tools de escrita na Kirvano (`products_create`, `products_create_offer`, `products_create_checkout`, `products_set_cover`, `products_add_content`, `products_request_contact_validation`, `products_confirm_contact_validation`) — fica só leitura (`whoami`, categorias/formatos, `products_get`) + preparo de plano/ebook; essas chamadas de escrita passam a ser feitas pelo **orquestrador** direto. `clonagem-vturb` ganhou nota explícita: o embed/script nunca sai pela API, avisar o orquestrador imediatamente após upload+CTA. Capa gerada via Canva passa a ser o orquestrador direto (não mais via sub-agent `general-purpose` + relay). `clonagem-presell` pode rodar logo depois de `clonagem-limpeza`, em paralelo com o resto (diagrama §4 e tabela §5 atualizados); só o patch final de `OFFER_URL` continua esperando o deploy. | primeira comercialização real (oferta "painosso", 20/10) ficou lenta por atrito evitável: (1) `products_create` via `clonagem-kirvano` foi recusado pelo classificador de permissão ("Unrequested Commit in a Connected App") porque o sub-agent não tem o pedido do dono no próprio histórico — a mesma chamada pelo orquestrador passou direto, custando uma rodada inteira de bloqueio→relatório→refação; (2) capa precisou de um agent `general-purpose` extra com Canva + relay manual, dois hops que podiam ser um; (3) o embed da Vturb só foi descoberto como limite manual da plataforma na hora, depois de tudo pronto; (4) `clonagem-presell` só disparou depois da comercialização, sem depender dela |
| 2026-10-20 (REA) | `clonagem-cloaking` ganhou tools `mcp__rea__capture_browser_scenario`, `mcp__rea__inspect_web_page`, `mcp__rea__list_browser_targets`, `mcp__rea__trace_javascript_semantics` (fallback, não substitui curl+grep nem o script decisor estático); `clonagem-vsl-detector` e `clonagem-mapa` ganharam o subconjunto `capture_browser_scenario`+`inspect_web_page` pro mesmo tipo de fallback (config de player/redirect que só existe em runtime) | gap real na oferta "painosso" (`02-cloaking.md`): o `clonagem-cloaking` tentou provar/descartar cloaking só com HTTP (4 identidades) + leitura estática de JS e não conseguiu verificar redirect/decisão client-side por falta de navegador no ambiente; dono decidiu ligar o REA como fallback nesses três agents |
| 2026-10-20 (textos) | 6 correções de texto: `README.md` ganhou `limpar_ocultos.py` e `dominio-hostinger-vercel.md` nas listas e teve a tabela de "nove etapas" (§2) trocada pelas fases/agents reais (§4); `SKILL.md` passo 11 agora cita `CLAUDE.md` seção 8 (não 7); `mapear_pagina.py` não cita mais `clonar_pagina.py`/`detectar_cloaking.py` (não existem) e sim `checar_cloaking.py`; `instalar.ps1`/`instalar.sh` corrigem a URL do remoto pra `smallfiver/clonar-funil-detectar-cloaking.git`; `template-relatorio-oferta.md` não diz mais que os 2 padrões manipulativos ficam "comentados pra ativar" (contradizia a seção 7 — nunca implementar, só documentar); instaladores agora removem `clonagem-vsl.md`/`clonagem-builder.md`/`clonagem-deploy.md` antigos antes de copiar os novos | docs desatualizados depois da reestruturação de 04/10 e 20/10; cada um gerava confusão pra quem seguisse a doc ao pé da letra |
| 2026-10-20 (correção) | `clonagem-vturb` corrigido: existe sim uma API de escrita da Vturb — **Videos API** (`api.vturb.com/v1`, bearer `vt_...`), diferente da de Analytics (`analytics.vturb.net`, só leitura, já documentada antes). O agent agora sobe o vídeo (upload multipart S3), confirma, e configura `call_actions`/`general.pitch_time` via `PATCH` de verdade — não é mais checklist manual | primeira versão assumiu, sem checar, que não havia API de escrita; o dono corrigiu e a doc real (`docs.vturb.com/pt/docs/reference/videos-api`) confirmou o endpoint |
| 2026-10-20 | Novos sub-agents `clonagem-kirvano` (produto+checkout+capa+ebook na Kirvano, preço extraído da transcrição, condicional e com confirmação do dono) e `clonagem-vturb` (checklist manual — a API da Vturb conectada é só Analytics, sem escrita). Inseridos entre a fase de Vídeo e a Construção (11 e 12); `clonagem-presell` a `clonagem-relatorio` renumerados (13→21). `clonagem-oferta` passa a usar o player Vturb no lugar do `<video>` self-hosted quando `12-vturb.md` existir. `clonagem-deploy-vercel`/`clonagem-lovable` deixam de ser escolha (Vercel OU Lovable) e passam a rodar **sempre os dois**, em paralelo | pedido do dono: o agente deve ajudar a vender de verdade a oferta modelada (não só clonar o funil), e ele já tem conexão com as duas plataformas de deploy, então não precisa escolher |
| 2026-10-04 | Skill virou orquestrador; criados 5 sub-agents; playbook movido p/ `references/playbook-detalhado.md` | contexto do orquestrador limpo, QA independente de quem constrói |
| 2026-10-04 | Nova ordem: cloaking → ocultos → mapa; builders por tipo; handoffs 01–07 | cloaking primeiro, análise antes de limpar |
| 2026-10-04 | Criado `CLAUDE.md` (este mapa vivo) | visão única da estrutura e melhoria contínua |
| 2026-10-09 | `clonagem-lovable`: links entre páginas com `index.html` explícito + validar redirects com `curl -L` | falha real (ProsperitySource-Offer1): CTA da presell apontava para `../oferta/`; no Lovable diretório em `public/` não serve `index.html`, caía no 404 do template e o fluxo travava na presell. O `/oferta/` = 307 da criação foi aceito sem seguir o redirect |
| 2026-10-10 | Novo script `analisar_script_decisor.py` (análise estática + `webcrack` opcional) e passos 4–6 no `clonagem-cloaking`: comparar com/sem cabeçalhos de navegador, registrar `Set-Cookie`, analisar o script decisor, dizer o que reprovou, consultar a Biblioteca de Anúncios | falha real (NatureVital): `checar_cloaking.py` deu "idêntico" e a 1ª rodada reportou "nenhum Set-Cookie", mas o servidor injetava o decisor e cookies só com `Accept-Language`/`Sec-Fetch-*`; a VM do script não foi decompilada; o país-alvo foi presumido errado duas vezes (idioma da fachada, depois anúncios antigos em espanhol). Página real não obtida: decisão no servidor e campanha pausada |
| 2026-10-04 | **Um sub-agent por tarefa (19 agents)**: `vsl`→`vsl-detector`+`pitch`+`checkout`+`vsl-download`+`transcricao`; `builder`→`limpeza`+`presell`+`oferta`+`upsell-downsell`+`backredirect`; `deploy`→`deploy-vercel`+`lovable`+`dominio`+`relatorio`; `recon` separado de `cloaking`; `mapa` virou só leitura. Perguntas iniciais (tipo, destino, transcrever) e detecção de 2+ VSLs com variantes | pedido do usuário: orquestrador só orquestra, cada tarefa com dono único |
