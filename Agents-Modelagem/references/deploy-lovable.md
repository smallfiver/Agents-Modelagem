# Deploy na Lovable via MCP (feito pelo orquestrador)

Toda oferta sobe **nos dois destinos de verdade**: Vercel (`clonagem-deploy-vercel`)
e Lovable (este passo). O zip do `clonagem-lovable` é só a matéria-prima; a oferta
**não está entregue** enquanto não houver projeto Lovable publicado e testado.

**Quem faz:** o orquestrador, direto pelo MCP da Lovable (`mcp__claude_ai_LOVABLE__*`).
O sub-agent `clonagem-lovable` não tem as tools do MCP. Além disso, escrita em app
conectado pedida por sub-agent é barrada pelo classificador (mesmo gap da Kirvano).
Criar projeto e mandar mensagem **gasta créditos do workspace Lovable**.

## Passo a passo

1. **Workspace:** `list_workspaces`. Se houver mais de um, use o mesmo das ofertas
   anteriores (anote no relatório). Na dúvida, pergunte ao dono uma vez.
2. **Subir o zip:** `get_file_upload_url` (`file_name` = `<Nome>-lovable.zip`,
   `content_type` = `application/zip`) → `PUT` do arquivo na URL com os headers
   devolvidos (`curl -X PUT --data-binary @<zip> -H "Content-Type: application/zip"`).
   Guarde o `file_id`.
3. **Criar o projeto:** `create_project` com `workspace_id`, `files: [{file_id,
   file_name, mime_type: "application/zip"}]`, `wait: true` e `initial_message`:
   > Publique EXATAMENTE os arquivos deste zip, sem redesenhar nada. Coloque tudo
   > em `public/`: a presell na raiz (`public/index.html` e assets) e a oferta em
   > `public/oferta/`. A rota `/` deve servir a presell como está, e `/oferta`
   > deve redirecionar para `/oferta/index.html` mantendo a query string. Não mude
   > textos, cores, fontes, imagens nem scripts (o player Vturb fica igual). Não
   > adicione analytics, tracking nem componentes. Não use tema próprio.
   Se voltar `awaiting_input`, mostre ao dono e responda com `respond_to_approval`
   (nunca com outro `send_message`). Se der timeout, `get_message` com o mesmo id.
4. **Publicar:** `deploy_project` (`name` = `<Nome>`). A URL devolvida ainda **não**
   prova nada: confira com `curl -sL -o /dev/null -w "%{http_code}"` até 200 em
   `/` e em `/oferta/index.html`.
5. **Badge:** peça via `send_message` para esconder o "Edit with Lovable"
   (`publish_settings--set_badge_visibility`, `hide_badge: true`). Exige plano pago;
   sem plano, vira pendência no relatório (painel: Settings → General).
6. **Presell da Lovable:** o `OFFER_URL` dela é relativo (`/oferta/index.html`),
   então não precisa de patch depois do deploy. Confira que o link continua assim.
7. **Vturb:** libere o domínio `<slug>.lovable.app` (`POST /v1/domains`, via
   `clonagem-vturb`). Sem isso o player mostra "domínio não permitido".
8. **Verificação ao vivo (passo 9.5 da SKILL):** a URL Lovable entra junto com a
   Vercel. Compare `getComputedStyle` com o clone, confira imagens reais, player
   carregando, badge ausente e query repassada da presell para a oferta.

## Falhas conhecidas
- Lovable reescreve a página se a instrução deixar brecha (tema claro/dourado,
  avatares viraram letras, texto parafraseado — oferta de 21/10). Por isso a
  instrução manda **copiar os arquivos**, não "recriar a página".
- Diretório em `public/` não serve `index.html` sozinho: links sempre com
  `index.html` explícito (ProsperitySource, 09/10).
- O badge pode voltar entre publicações: reconfirme sempre no passo 8.
- Corrigir pelo `send_message` no mesmo projeto, nunca criar projeto novo (gasta crédito).
