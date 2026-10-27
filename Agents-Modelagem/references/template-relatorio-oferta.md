# RELATÓRIO DA OFERTA — {NOME DA OFERTA}

**Origem:** `{URL ORIGINAL}`
**Data da clonagem:** {DATA}
**Pasta:** `C:\Ofertas\{Nome-Da-Oferta}\`

> Este é o checklist padrão que preenchemos para TODA oferta clonada.
> Copie este arquivo para dentro da pasta da nova oferta como `RELATORIO.md`
> e preencha cada seção. Nenhuma oferta é considerada "entregue" sem isso.

---

## ☐ Checagem de cloaking (fazer ANTES de clonar)
Se a URL chegou com `fbclid`/`utm_source=facebook` (veio de um anúncio ativo),
rode `scripts/checar_cloaking.py <url> --fbclid <fbclid>` — compara a resposta
HTTP pra navegador normal, com fbclid, `facebookexternalhit`, e `Googlebot`.
- [ ] As 4 respostas foram comparadas
- [ ] Se idênticas: documentado que não há cloaking no nível HTTP, mas isso
      não descarta cloaking via JS (confirmar abrindo num navegador real)
- [ ] Se houver scripts ofuscados (`atob(`, XOR): decodificados com
      `scripts/decodificar_pixel_ofuscado.py` e documentado o que carregavam

## ☐ Momento do pitch da VSL
Em que segundo/minuto do vídeo original o botão de compra é revelado?
(Extrair do player original — campo `range:{start:...}` no VTurb/converteai,
ver `references/extrair-vsl-vturb.md`.) Se for teste A/B, documentar o peso
de tráfego e o pitch de CADA variação, não só da principal.

## ☐ Baixa da VSL
- [ ] Vídeo baixado por completo (ffmpeg + m3u8 do CDN original)
- [ ] Duração confirmada com `ffprobe` (bate com o original, sem cortes)
- [ ] Se > 95MB: recomprimido com `scripts/comprimir_vsl_2pass.py` (mirar
      ~90MB) para caber no limite de 100MB por arquivo da Vercel
- Caminho do arquivo mestre (maior qualidade): `vsl/...mp4`
- Caminho da versão web usada no deploy: `oferta/vsl.mp4`

## ☐ Presell antes da oferta, com botão
Toda oferta SEMPRE ganha uma página de presell antes da VSL:
- [ ] Página separada (Vite + React + TS, Lovable-ready)
- [ ] Texto explicativo (contexto/curiosidade) — não é obrigatório ter vídeo/player na presell
- [ ] Botão de CTA bem visível **no topo** (logo após o headline — segundo
      elemento da página, não enterrado embaixo de parágrafos)
- [ ] Ao clicar, redireciona para a página da oferta (repassando UTMs se houver)

## ☐ Link do checkout
```
{URL DO CHECKOUT}
```
Plataforma: {Kiwify / Kirvano / Hotmart / Perfectpay / Stripe próprio / etc.}
Preço: {valor}

⚠️ Se algum script de atribuição no código referenciar um domínio de
checkout DIFERENTE do link real embutido no player/botão, documentar essa
discrepância aqui (pode ser domínio desatualizado ou camada extra de
redirecionamento).

## ☐ Checkout — outros links dentro do código da oferta
Rodar `grep -oiE 'https?://[a-z0-9.-]+[a-z0-9/?=_&.-]*' oferta/index.html | sort -u`
e listar TODOS os links encontrados no código. Confirmar que só sobrou o
checkout (e assets próprios) — qualquer outro domínio de terceiro deve ser
removido ou substituído.

## ☐ Limpar todos os dados da oferta original
Checklist de remoção (confirmar cada um por grep, não por leitura visual —
ver `references/trackers-para-remover.md` para a lista completa):
- [ ] Meta Pixel / fbevents (`fbq(`, `connect.facebook.net`)
- [ ] Google Ads / GA4 / GTM (`gtag(`, `googletagmanager`)
- [ ] UTMify (script visível E pixel oculto/ofuscado), Clarity, Hotjar, TikTok Pixel
- [ ] Botões/links de checkout ocultos do original removidos (`limpar_ocultos.py` = 0)
- [ ] Script de atribuição cross-domain (fbclid/_fbp/_fbc repassados pro checkout)
- [ ] Player/analytics de terceiros (VTurb/converteai, Panda, etc.) — trocado por vídeo self-hosted
- [ ] Boilerplate de WordPress/Elementor (feeds, oEmbed, wp-json, xmlrpc)
- [ ] UTMs fixas no código — mantido só repasse dinâmico de UTMs reais da URL de entrada

Verificação final obrigatória:
```bash
grep -icE 'fbq\(|gtag\(|googletagmanager|connect\.facebook|utm_source=|clarity|hotjar|converteai|vturb|utmify' index.html
```
Deve dar **0** (ou só aparecer dentro de comentários explicativos).

## ☐ Padrões observados (não entram no clone)
Se o original usava sequestro do botão voltar ou urgência com data falsa
(ver `references/trackers-para-remover.md`), documentar aqui em vez de
replicar silenciosamente. O resto do layout (headline, prova social,
depoimentos, footer) É replicado fielmente — só esses dois padrões
manipulativos ficam de fora: **não são implementados, nem comentados no
código** — `CLAUDE.md` §7 e os agents mandam só documentar, nunca
implementar. (Correção de 20/10: a versão anterior deste template dizia
"deixados comentados no código para ativar", o que divergia do `CLAUDE.md`;
removido. Se algum dia vale ter uma versão comentada pronta pra ativar sob
pedido explícito do dono — em vez de só documentada — isso ainda é
`[PENDENTE DE VALIDAÇÃO com o dono]`.)

## ☐ Valor da oferta
Preço, moeda, order bump (se houver), upsell/downsell (se verificável sem
completar pagamento — NUNCA completar uma compra real para descobrir).

## ☐ Comercialização (só se o dono pediu pra vender de verdade)
- [ ] **Produto na Kirvano:** nome, ID, preço confirmado (dito na transcrição
      do pitch; divergência com o preço do concorrente documentada, se houve)
- [ ] **Checkout Kirvano:** `{link}`
- [ ] **Capa/banner:** gerada e aplicada (ferramenta usada)
- [ ] **Ebook entregável:** montado a partir da transcrição, caminho/link, e
      subido como conteúdo do produto
- [ ] **Vturb:** `video_id`, status (`ready`/outro), CTA configurado no
      segundo exato do pitch apontando pro checkout, via **API de Vídeos**
      (`api.vturb.com` — diferente da API de Analytics, só leitura); embed
      final: {link/script, ou "buscar no painel" se a API não devolveu}
- Se o dono optou por **só clonar, sem vender**: escreva "não aplicável —
  modelagem só para estudo/teste".

---

## 📁 Estrutura de pastas padrão (toda oferta)
```
{Nome-Da-Oferta}/
├── RELATORIO.md
├── presell/     <- página 1: explicação + botão (Vite/React/TS)
├── oferta/      <- página 2: VSL + reveal automático do checkout
└── vsl/         <- vídeos baixados (arquivo-fonte + versão compacta)
```

## 🔗 URLs publicadas (sempre os dois destinos)
- **Vercel** — Presell: {URL} · Oferta (VSL): {URL}
- **Lovable** — zip: `{Nome}-lovable.zip` ({caminho})
- Checkout (original, detectado no concorrente): {URL}
- Checkout próprio (Kirvano, se comercializou): {URL}
- Domínio próprio conectado (Hostinger)? {Sim / Não — usuário optou por
  ficar só no `*.vercel.app` / Não perguntado ainda}
  - Se sim: domínio, registros DNS aplicados, e se foi via API (token) ou
    configurado manualmente pelo usuário — ver `references/dominio-hostinger-vercel.md`

## ✏️ Onde editar
- `presell/src/App.tsx` → `OFFER_URL`
- `oferta/index.html` → `DELAY_REVEAL` e o `href` do botão de checkout
