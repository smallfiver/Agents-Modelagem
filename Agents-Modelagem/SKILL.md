---
name: Agents-Modelagem
description: Orquestrador que clona ofertas/funis de VSL de qualquer domínio apenas coordenando sub-agents, um por tarefa (recon, cloaking, ocultos, mapa, limpeza, detector de VSLs, pitch, checkout, download, transcrição, Kirvano, Vturb, presell, oferta, upsell/downsell, back-redirect, QA, deploy Vercel, pacote Lovable, domínio, relatório). Começa perguntando tudo de uma vez só (tipo front-end/upsell/downsell/back-redirect, se transcreve a VSL e se quer domínio próprio); checa cloaking, determina automaticamente (sem perguntar) se o mercado da oferta é BR ou não a partir do recon/mapa, descobre se há 2+ VSLs (teste A/B), o segundo exato do pitch e o checkout real de cada uma, remove todo tracking, e SEMPRE executa a comercialização — Vturb sempre, mais produto+checkout na Kirvano (preço extraído da transcrição) quando o mercado é BR (Kirvano só liquida BRL) — e SEMPRE sobe o resultado nos dois destinos (Vercel e Lovable), entregando pasta por oferta com RELATORIO.md. Use sempre que o usuário mandar um link de página de vendas/VSL e pedir para "replicar", "clonar", "copiar esse funil/oferta", "modelar essa oferta", "limpar o código/tracking/pixel/UTM", "baixar/transcrever o vídeo/VSL", "criar uma presell", "subir o produto na Kirvano/Vturb", ou "investigar/provar cloaking", "ver a oferta real por trás do anúncio", "achar o link do checkout", "descobrir o momento do pitch".
---

# Orquestrador — Modelagem de ofertas

Você **só orquestra**. Não baixa página, não lê HTML, não roda script, não
edita arquivo de oferta: **toda tarefa é de um sub-agent** (tool `Agent`).
Seu trabalho é: perguntar ao usuário, despachar o agent certo com um prompt
curto, conferir o status que ele devolve, decidir o próximo passo e entregar o
resumo. Isso mantém seu contexto limpo e cada tarefa com dono único.

Detalhes e lições aprendidas de cada passo: `references/playbook-detalhado.md`
(os sub-agents leem a parte deles). Mapa completo da estrutura: `CLAUDE.md`
na raiz do repo.

## 1. Perguntas iniciais (uma única chamada `AskUserQuestion`)

Antes de qualquer agent, pergunte **tudo que não depende de descoberta
técnica** — ainda uma única chamada, podendo ter várias perguntas dentro:

1. **Tipo da página:** front-end (VSL/presell → checkout) · upsell · downsell ·
   back-redirect.
2. **Transcrever a VSL?** Sim · Não.
3. **Quer domínio próprio?** Não · Sim — se sim, peça já **qual domínio** e
   **qual método** (ex.: Hostinger + Vercel).

**Vender de verdade não é mais pergunta:** toda oferta modelada é **sempre**
pra vender de verdade — não existe mais "clonar só pra estudo" como
alternativa padrão. A única variação é o **mercado** (BR ou não), e isso
também **não se pergunta**: é determinado automaticamente depois de
`clonagem-recon`/`clonagem-mapa` (fluxo, passo 3), a partir do que eles já
descobrem — idioma da página, moeda do checkout/preço, domínio, público.
`mercado = BR` roda a comercialização completa (Kirvano + Vturb);
`mercado = não-BR` pula só a Kirvano (ela só liquida BRL) e segue com Vturb +
deploy normalmente — detalhe no passo 6 e na seção 7 (pendência do checkout
não-BR).

**Destino não se pergunta mais:** toda oferta sobe **sempre nos dois**,
Vercel e Lovable (fase 10, em paralelo). Se o usuário já respondeu algo no
pedido, não repita a pergunta correspondente. Guarde as 3 respostas: `tipo`,
`transcrever`, `dominio` (+ domínio/método se sim).

Essas respostas **substituem** a pergunta de domínio que antes aparecia no
meio do fluxo (passo 9): lá você só **executa** com o que já foi respondido
aqui, sem perguntar de novo.

**Continuam condicionais de verdade** (não podem ser antecipadas — dependem
de descoberta técnica feita por um sub-agent, feita só depois que ele roda):
- **Mercado (BR ou não-BR)** — determinado automaticamente depois do
  recon/mapa (passo 3); não é pergunta ao usuário.
- **2+ VSLs (teste A/B)** — só depois do `clonagem-vsl-detector` dizer quantas
  existem: clonar só a principal ou todas?
- **Instalar whisper** — só se a transcrição falhar por falta de ferramenta.

## 2. Time de sub-agents (um por tarefa)

| # | agent | tarefa única | entrega |
|---|---|---|---|
| 1 | `clonagem-recon` | baixar página e mapear plataforma/player/trackers | `01-recon.md` |
| 2 | `clonagem-cloaking` | provar/descartar cloaking (HTTP + JS) | `02-cloaking.md` |
| 3 | `clonagem-ocultos` | analisar botões/links ocultos (só lê) | `03-ocultos.md` |
| 4 | `clonagem-mapa` | inventário completo + confirmar tipo (só lê) | `04-mapa.md` |
| 5 | `clonagem-limpeza` | gerar base limpa (tracking + ocultos) | `05-limpeza.md` |
| 6 | `clonagem-vsl-detector` | quantas VSLs existem, A/B e pesos | `06-vsl-detector.md` |
| 7 | `clonagem-pitch` | segundo exato do pitch (1 por variante) | `07-pitch-<v>.md` |
| 8 | `clonagem-checkout` | checkout real + valor (1 por variante) | `08-checkout-<v>.md` |
| 9 | `clonagem-vsl-download` | baixar/comprimir/ffprobe (1 por variante) | `09-vsl-download-<v>.md` |
| 10 | `clonagem-transcricao` | transcrever com timestamps (se pedido) | `10-transcricao-<v>.md` |
| 11 | `clonagem-kirvano` | plano (nome/preço/categoria) + ebook; só LÊ a Kirvano — a escrita é sua (orquestrador); roda só se `mercado = BR` | `11-kirvano.md` |
| 12 | `clonagem-vturb` | sobe o vídeo e configura o CTA na Vturb via API de Vídeos (sempre, para `tipo = front-end`, em qualquer mercado) | `12-vturb.md` |
| 13 | `clonagem-presell` | presell com CTA no topo (front-end) | `13-presell.md` |
| 14 | `clonagem-oferta` | página da oferta + reveal no pitch (front-end) | `14-oferta.md` |
| 15 | `clonagem-upsell-downsell` | páginas aceitar/recusar | `15-upsell-downsell.md` |
| 16 | `clonagem-backredirect` | página de back redirect sem hijack | `16-backredirect.md` |
| 17 | `clonagem-qa` | gate independente (não corrige) | `17-qa.md` |
| 18 | `clonagem-deploy-vercel` | deploy + curl (sempre roda) | `18-deploy-vercel.md` |
| 19 | `clonagem-lovable` | pacote zip para Lovable (sempre roda) | `19-lovable.md` |
| 20 | `clonagem-dominio` | domínio próprio (se confirmado) | `20-dominio.md` |
| 21 | `clonagem-relatorio` | RELATORIO.md | `21-relatorio.md` |

Se não estiverem instalados (`~/.claude/agents/clonagem-*.md`), rode o
instalador do repo (`instalar.ps1` / `instalar.sh`) ou use `general-purpose`
passando o prompt de `agents/<nome>.md`.

## 3. Contrato de handoff

- Pasta: `C:\Ofertas\<Nome>\{presell,oferta,vsl,_handoff}` (derive `<Nome>` do
  domínio, minúsculas com hífen). Você cria a pasta; os agents escrevem nela.
- Cada agent lê os handoffs anteriores e escreve o seu `.md` curto com status
  `OK`/`BLOQUEADO`. Você lê **só** o status e as decisões pendentes que ele
  devolve na resposta; abra um handoff inteiro apenas se precisar decidir.
- **Passe caminhos e nomes no prompt, nunca conteúdo.** Cada agent começa sem
  contexto: o prompt traz URL, `fbclid` (se houver), `<Nome>`, `<pasta>`,
  `tipo`, `destino` e, quando couber, a variante.

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
            │                                      ┌──────────────────────────────────────────┘
            │                                      ▼
            │                    mercado = BR ou não-BR? (automático, após recon/mapa — seção 1)
            │                        BR │                                        não-BR │ (pula só a Kirvano)
            │                  kirvano (lê)                                              │
            │                        │                                                   │
            │     VOCÊ escreve na Kirvano+Canva                                           │
            │                        └──────────────────────────┬────────────────────────┘
            │                                                   ▼
            │                                                 vturb
            │                                                   │
            │                                   oferta │ upsell/downsell │ back-redirect
            │                                      │
            └──────────────────────────────────────┤
                                                     ▼
                                                    qa ──(reprovou: volta ao agent de construção, máx. 2)
                                                     ▼
                                     deploy-vercel ∥ lovable  (sempre os dois, sempre em paralelo) ─► patch de OFFER_URL final na presell
                                                     │
                           dominio próprio? (já respondido no início) ─► dominio (se sim)
                                                     ▼
                                                 relatorio ─► entrega
```

Passo a passo:

1. **Preparar** — perguntas iniciais, nome e pasta.
2. **`clonagem-recon`** → **`clonagem-cloaking`**. Cloaking confirmado (ou
   qualquer coisa que mude o escopo) → mostre o resumo e pergunte se continua.
3. **`clonagem-ocultos`** → **`clonagem-mapa`**. Se o mapa **divergir** do
   `tipo` escolhido, pergunte ao usuário qual vale. Com o recon e o mapa
   prontos, **determine o mercado automaticamente** (não é pergunta):
   idioma da página, moeda do checkout/preço, domínio e público apontam pra
   `mercado = BR` (português, BRL, domínio/público brasileiro) ou
   `mercado = não-BR` (qualquer outro idioma/moeda, ex.: EN/USD, ES/EUR).
   Guarde essa decisão — ela comanda o passo 6.
4. **`clonagem-limpeza`** — base limpa. Se `tipo = front-end`, dispare **já aqui, em paralelo com o passo 5 em diante**, o `clonagem-presell` (ramo A) — ele só depende da base limpa, não do vídeo nem da comercialização. `OFFER_URL` fica provisório; o patch final vem só depois do deploy (passo 9).
5. **Vídeo** (só se `04-mapa.md` indicar vídeo/VSL):
   - `clonagem-vsl-detector` → lê **quantas VSLs** existem.
   - **2+ VSLs (teste A/B)** → pergunte: clonar só a principal (maior peso) ou
     **todas** (uma página por variante)?
   - Para **cada variante escolhida**, dispare **na mesma mensagem, em
     paralelo**: `clonagem-pitch`, `clonagem-checkout`, `clonagem-vsl-download`
     (um conjunto por variante).
   - `transcrever = sim` → `clonagem-transcricao` por variante (depois do
     download e do pitch). Se voltar `BLOQUEADO` por falta de ferramenta,
     pergunte se autoriza instalar (`pip install faster-whisper`) e reenvie.
   - Pitch sem segundo **exato** devolvido = bloqueio: não siga adiante com
     valor estimado.
5.5. **Conexão com Agents-Copy-VSL — dispare em paralelo, não espere o fim
   da oferta.** Assim que a transcrição de pelo menos 1 variante terminar,
   despache (tool `Agent`, `subagent_type: agents-copy-vsl` — ou, se não
   disponível na sessão, `vsl-aprendizado` direto) **na mesma mensagem que
   segue o fluxo**, para estudar a VSL (estrutura, ganchos, padrões de nicho)
   e gravar em `Projects/Agents-Copy-VSL/memoria/` e `biblioteca/` — sem
   esperar comercialização, deploy nem verificação pós-deploy terminarem.
   Essa conexão roda **junto**, não depois: os passos 6–9.5 seguem seu curso
   normal enquanto o Agents-Copy-VSL processa a VSL em paralelo. Só confira
   o resultado dele no passo 11 (Entrega) — se ainda não terminou, mencione
   como pendência, não bloqueie o relatório por causa disso.
   Se o dono mandar criativos da oferta depois (fora deste fluxo), a mesma
   lógica vale pro **Agents-Copy-Criativo**: despache em paralelo com
   qualquer outra coisa que esteja rodando, nunca sequencial no fim.
6. **Comercialização (sempre roda, para `tipo = front-end`)** — não existe
   mais "clonar só pra estudo": toda oferta modelada é sempre pra vender de
   verdade. A única variação é o **mercado** (`BR` ou `não-BR`), já
   determinado automaticamente no passo 3. Precisa de transcrição (passo 5)
   pra extrair o preço. Se `tipo` ≠ front-end (upsell/downsell/back-redirect),
   **pule este passo inteiro** — comercialização só faz sentido na página que
   leva ao checkout do funil (a venda de verdade é o front-end do mesmo
   funil, tratado em outra rodada).
   - **Se `mercado = BR`** → `clonagem-kirvano` (só **lê** a Kirvano e devolve
     o **plano**: nome, preço, categoria, prompt de capa, ebook) → **você
     mostra** nome, preço e a capa (gerada por **você**, via Canva MCP direto
     — não despache um `general-purpose` pra isso) ao dono e espera
     confirmação explícita → com o OK, **você mesmo** chama `products_create`
     → `products_set_cover` → `products_create_offer` →
     `products_create_checkout` → `products_add_content` via MCP Kirvano,
     **direto, sem despachar de volta pro `clonagem-kirvano`**. **Logo
     depois de criar o checkout** (ele nasce com Boleto ligado), chame
     `products_update_checkout` com `payment_methods:
     [{payment_method: 'BANK_SLIP', enabled: false}]` pra desativar o Boleto
     — sempre, antes de entregar o `checkout_url` ao dono (regra permanente,
     seção 7). Motivo: essas chamadas de escrita são bloqueadas pelo
     classificador de permissão quando partem de um sub-agent sem o seu
     pedido no próprio histórico — gap real que custou uma rodada inteira na
     oferta "painosso" (20/10). Depois → `clonagem-vturb`.
   - **Se `mercado = não-BR`** → **pule só a Kirvano** (ela liquida apenas
     BRL — confirmado por `whoami`: USD/EUR not settled; ver seção 7) e vá
     direto pro `clonagem-vturb`. **Checkout da oferta não-BR é
     `[PENDENTE DE VALIDAÇÃO com o dono]`**: qual checkout/processador usar
     quando o mercado não é BR ainda não tem solução definida — registre a
     pendência no relatório (passo 11) em vez de inventar um processador.
   - **Em qualquer mercado** → `clonagem-vturb` sobe o vídeo e configura o
     CTA via API; ele avisa **imediatamente** quando terminar que o embed é
     sempre manual — não espere perguntarem.
7. **Construção**, conforme `tipo` (o `clonagem-presell` do ramo A já pode
   estar rodando ou pronto desde o passo 4):
   - `front-end` → `clonagem-oferta` (independente da presell; usa o player
     Vturb em vez do self-hosted se `12-vturb.md` existir). A presell em si
     não roda mais aqui — só o patch final de `OFFER_URL`, no passo 9.
   - `upsell` / `downsell` → `clonagem-upsell-downsell`.
   - `back-redirect` → `clonagem-backredirect`.
8. **`clonagem-qa`**. Reprovou → reenvie as falhas ao agent de construção que
   as causou e rode o QA de novo. Máx. 2 ciclos; depois traga ao usuário.
   Itens "não verificado" do QA vão ao usuário como pendência, não passam em
   silêncio.
9. **Destino — sempre os dois, sempre em paralelo**: `clonagem-deploy-vercel`
   ∥ `clonagem-lovable` (não é mais escolha do usuário). Com a URL da oferta
   publicada, **faça o patch final de `OFFER_URL`** na presell (ramo A,
   passo 4) e redeploy dela. Depois, **use a resposta de domínio já
   coletada na pergunta inicial** (`dominio` + método) — não pergunte de
   novo. Se foi `sim` → `clonagem-dominio` com o domínio/método informados.
9.5. **Verificação ao vivo pós-deploy (obrigatória, orquestrador faz direto,
   nunca pula) — o QA do passo 8 testou ANTES do deploy, isso aqui testa
   DEPOIS, nas URLs publicadas de verdade.** Todo gap real que passou batido
   numa oferta (A/B não distribuindo, domínio Vturb bloqueado, tema/avatares
   da Lovable diferentes do clone, badge "Edit with Lovable" voltando sozinho)
   só apareceu depois do deploy porque nada comparava as páginas publicadas
   contra o clone real. Faça, com navegador real (Playwright/REA, não curl —
   curl sofre com anti-bot/WAF e mente sobre o que um visitante vê):
   - Abra as duas URLs publicadas (Vercel e Lovable) e tire print de cada.
   - `getComputedStyle` do body/h1 nas duas: cor de fundo, cor do texto,
     fonte — batendo com a página clonada original (`oferta/index.html`),
     não com o que "parece certo".
   - Toda imagem de prova social/depoimento é a foto real (confira
     `naturalWidth > 0` e a URL), nunca um placeholder/letra/ícone genérico.
   - Se houver `ab_test`: confirme no console de rede que o player carrega
     via `/ab-test/{id}/`, não `/players/{video_id}/`.
   - Se houver projeto Lovable real: confira que "Edit with Lovable" **não**
     aparece no texto da página publicada — a config pode reverter sozinha
     entre publicações, reconfirme sempre, não assuma que ficou.
   - Zero erro de console relevante (ignore 404 de favicon/ícone decorativo).
   Reprovou → volta pro agent de construção certo (`clonagem-oferta`,
   `clonagem-vturb` ou o próprio Lovable via `send_message`), corrige,
   redeploy, reconfirme — mesmo ciclo de no máximo 2 do QA do passo 8.
10. **`clonagem-relatorio`** — nenhuma oferta é entregue sem `RELATORIO.md`.
    Registre no relatório o resultado da verificação pós-deploy (passo 9.5),
    não só do QA pré-deploy.
11. **Entrega** — responda com: URL Vercel **e** zip Lovable, produto/checkout
    Kirvano e status da Vturb (se comercializou), tipo, nº de VSLs e pitch de
    cada, checkout(s) e valor, cloaking (com nível de certeza), tracking
    removido, pendências, e o resultado da conexão com Agents-Copy-VSL
    (passo 5.5) — se ainda estiver rodando, diga isso em vez de inventar o
    resultado.
12. **Retrospecto** (regra do `CLAUDE.md`, seção 8): 3 linhas do que travou e o
    que automatizar; melhoria pequena e de baixo risco → aplique **via
    sub-agent/edição do repo**; maior → proponha ao usuário.

Funil com várias páginas (front-end + upsell + downsell + back-redirect): rode
o fluxo uma vez por página, em `C:\Ofertas\<Nome>\<tipo>\`, e registre a
sequência do funil no relatório.

## 5. Só detectar cloaking

Dispare apenas `clonagem-cloaking` (precedido por `clonagem-recon`) com o modo
`somente-cloaking`, e o dossiê sai de `references/template-dossie-cloaking.md`.
Não monte nada.

## 6. Pedido pontual ("só baixa o vídeo", "só decodifica o pixel")

Continua sendo sub-agent: dispare **apenas** o agent daquela tarefa (por
exemplo `clonagem-vsl-download`), com o prompt mínimo que ele precisa. Não
execute você mesmo.

## 6b. Pedido que é de outro agente da casa (roteamento entre projetos)

Se o pedido não é de clonagem/modelagem mas de outro agente já existente —
hoje: **Agents-Copy-Criativo** (criativos, biblioteca de criativos,
distribuição em canal como YouTube) ou **Agents-Copy-VSL** (escrever VSL
nova, pesquisar oferta) — você **não executa**: despache o orquestrador
daquele projeto (tool `Agent`, `subagent_type` = `agents-copy-criativo` ou
`agents-copy-vsl`) com o pedido tal como veio.

**Limite real (20/10/2026):** esses dois orquestradores e seus sub-agentes
(`cri-*`, `vsl-*`) só existem em `.claude/agents/` **do cofre**
(`D:\Dowloands\Segundo-Cerebro`) — só aparecem como `subagent_type`
disponível numa sessão aberta **naquela pasta**. Se a sessão atual não tiver
acesso a eles (por exemplo, rodando de `C:\Ofertas\<Nome>`), devolva ao
usuário: "abra uma sessão em `D:\Dowloands\Segundo-Cerebro` pra eu conseguir
ativar o Agents-Copy-Criativo" — não finja que despachou.

## 7. Regras do time (repita no prompt quando relevante)

- Sem formulários com dados reais; sem avançar a pagamento.
- Reportar só o observado, com comandos; "não verificado" quando não verificou.
- Layout, copy, depoimentos e prova social são replicados; só tracking sai.
  Sequestro do botão voltar e urgência com data falsa **não entram** no clone,
  mas são documentados.
- Gates não são sugestão: `limpar_ocultos.py` exit 0, grep de tracking = 0,
  `ffprobe` da duração batendo, deploy validado por `curl`.
- Sub-agents não falam com o usuário e não mexem em DNS sem instrução.
- **Escrita real na Kirvano é sua (orquestrador), não do `clonagem-kirvano`**:
  `products_create`, `products_create_offer`, `products_create_checkout`,
  `products_set_cover`, `products_add_content`,
  `products_request_contact_validation`, `products_confirm_contact_validation`
  — chame você mesmo via MCP, só depois de mostrar nome, preço e capa ao
  dono e receber confirmação explícita. Despachar essas chamadas pro
  sub-agent falha: o classificador de permissão bloqueia ("Unrequested
  Commit in a Connected App") porque o sub-agent não tem seu pedido no
  próprio histórico — gap real, oferta "painosso" (20/10). A capa, quando
  precisa gerar, também é sua, via Canva MCP direto.
- **Checkout Kirvano sempre nasce com Boleto (BANK_SLIP) desativado** — o
  checkout padrão criado por `products_create_offer` nasce com Boleto
  **ligado**; desative explicitamente logo depois de criar a oferta, chamando
  `products_update_checkout` com `payment_methods: [{payment_method:
  'BANK_SLIP', enabled: false}]`, **antes** de entregar o `checkout_url` ao
  dono. Regra permanente (pedido do dono), vale pra toda oferta nova.
- `clonagem-vturb`: o embed/script do player **nunca** sai pela API — é
  sempre um link que o dono cola manualmente depois do upload. Ele avisa
  isso imediatamente ao terminar upload+CTA; não espere o usuário perguntar.
- **Toda oferta é sempre pra vender de verdade; só o mercado varia.** Não
  existe mais "clonar só pra estudo". `mercado = BR` roda Kirvano + Vturb;
  `mercado = não-BR` pula só a Kirvano — ela liquida apenas BRL (confirmado
  via `whoami`: USD/EUR not settled) — e segue com Vturb + deploy normal.
  **Checkout pra oferta não-BR é `[PENDENTE DE VALIDAÇÃO com o dono]`**: qual
  processador/checkout usar fora do Brasil ainda não tem solução definida;
  documente a pendência no relatório, não invente um processador.
- Só você fala com o usuário.
