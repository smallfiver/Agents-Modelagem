# Modo aprender — tutorial e modelagem manual guiada

Lido pelo orquestrador quando a resposta da pergunta **"Como quer fazer?"**
(SKILL.md §1) for **"Me explica primeiro"** ou **"Manual guiado"**. No modo
**Automático** este arquivo não é usado.

## A. "Me explica primeiro" — tutorial curto

Mostre ao usuário, nesta ordem, em frases curtas (sem muro de texto):

1. **O que a skill faz:** você manda o link de uma oferta e ela entrega a
   presell + a oferta limpas (sem pixel, sem UTM), o vídeo baixado, o segundo
   do pitch, o checkout, e publica na Vercel e na Lovable. Tudo fica em
   `C:\Ofertas\<Nome>\` com um `RELATORIO.md`.
2. **Como chamar:** `/Agents-Modelagem <link da oferta>`. Ela faz 4 perguntas
   no começo (modo, tipo, transcrever, domínio) e depois só para quando
   precisa de uma decisão sua.
3. **O que precisa estar pronto:** `vercel login` feito uma vez; chaves
   `VTURB_VIDEOS_API_KEY` (e `VTURB_API_KEY`) configuradas; Kirvano conectada
   (só oferta BR). Passo a passo: `README.md` do repositório.
4. **As fases, em uma linha cada:** reconhecimento → cloaking → elementos
   ocultos → mapa → limpeza → vídeo (pitch, checkout, download) →
   Kirvano/Vturb → montar oferta → QA → publicar → relatório.
5. **O que ela nunca faz:** preencher formulário com dado real, pagar,
   modelar golpe, sequestrar o botão voltar, urgência com data falsa.

Depois pergunte (uma `AskUserQuestion`): **"Agora quer fazer Automático ou
Manual guiado?"** e siga o fluxo normal com a resposta.

## B. "Manual guiado" — aula fazendo a oferta de verdade

O fluxo e os sub-agents são **os mesmos** do modo automático (SKILL.md §4).
O que muda é que você **para depois de cada fase** e ensina. A oferta sai
pronta igual; o usuário só aprende no caminho.

### Em cada fase, mostre 4 coisas (curto)

1. **O que essa fase faz e por quê** — 1–2 frases.
2. **Como fazer na mão** — o passo que o usuário repetiria sozinho, sem o
   agente (tabela abaixo). Comando ou clique exato.
3. **O que o agente achou** — 2–3 linhas tiradas do handoff da fase.
4. **Print** — quando a fase tem algo visual (ver "Prints").

Termine perguntando: **"Segue para a próxima fase?"** (opções: Segue ·
Explica melhor · Quero fazer essa na mão). Se o usuário escolher fazer na
mão, espere ele dizer "feito", e só então despache o sub-agent para conferir
o resultado.

### Como fazer na mão, fase por fase

| Fase | Na mão |
|---|---|
| Recon | Abrir a página, `Ctrl+U` (ver código-fonte), procurar `fbq`, `gtag`, `ttq`, `utm`, `converteai`, `vturb`. |
| Cloaking | Abrir o link no navegador normal e numa aba anônima com `?fbclid=teste`; comparar se a página muda. `curl -A "facebookexternalhit/1.1" <url>` mostra o que o robô do Facebook vê. |
| Ocultos | DevTools (`F12`) → Elements → procurar `display:none`, `hidden`, `.esconder`; aba Console mostra timers que revelam o botão. |
| Mapa | Rolar a página inteira e listar seções: headline, VSL, depoimentos, garantia, FAQ, botão. |
| Limpeza | `Ctrl+S` (página completa), abrir o `.html` e apagar os `<script>` de pixel/UTM; conferir com busca por `fbq`/`gtag` = 0. |
| Pitch | Assistir a VSL e anotar o segundo em que o botão de compra aparece (ou buscar `delay`/`displayHiddenElements` no código). |
| Checkout | Esperar o botão aparecer e copiar o link (botão direito → copiar endereço). Não clicar para pagar. |
| Download | `ffmpeg -i "<url .m3u8>" -c copy vsl.mp4` (a URL `.m3u8` aparece em DevTools → Network, filtro `m3u8`). |
| Transcrição | Rodar o whisper local ou subir o MP4 num transcritor. |
| Kirvano / Vturb | Criar produto + checkout na Kirvano (boleto desligado); subir o vídeo na Vturb e marcar o CTA no segundo do pitch. |
| Oferta / presell | Trocar o player pelo da Vturb, apontar o botão para o checkout próprio, presell com botão no topo para a oferta. |
| QA | Abrir no celular (DevTools → modo celular), conferir vídeo, botão no segundo certo, imagens, nenhum pixel. |
| Publicar | `vercel --prod` dentro da pasta; Lovable: subir o zip. |

### Prints

Salve em `<pasta>/_aula/` com número da fase (`01-original.png`,
`05-limpa.png`, `09-oferta-local.png`, `10-publicada.png`). Tire com o MCP de
navegador disponível (Playwright `browser_take_screenshot` ou REA
`capture_web_screenshot`) — é a única ação que você mesmo faz no modo manual;
o resto continua sendo dos sub-agents. Se nenhum MCP de navegador estiver
disponível, diga isso e peça ao usuário um print da tela dele.

Prints mínimos: página original · página limpa local · oferta montada local
(desktop e celular) · URL publicada. Mostre o caminho do print na resposta.

### No fim

Além do `RELATORIO.md`, gere `<pasta>/_aula/RESUMO-DA-AULA.md`: fases feitas,
o "como fazer na mão" de cada uma, os prints e o que o usuário fez sozinho.
