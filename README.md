# Simulador_Investimento_V4

Novidade: botão **Pedir relatório** (canto da tela) abre um chat que pergunta a versão do relatório (carteira ou só mercado) e o canal:
- **WhatsApp:** em celulares (e navegadores que permitem), compartilha o PDF anexado pelo menu do sistema. Em outros, baixa o PDF e abre o WhatsApp com o resumo (wa.me); o PDF é anexado pelo usuário.
- **E-mail:** envio automático via Google Apps Script (opcional) ou, sem ele, PDF baixado + app de e-mail com texto preenchido.
- **Só PDF:** download direto.

## 1. Publicar no GitHub Pages
1. Envie index.html, enviar-email.html, news.json, scripts/ e apps-script/ para a raiz do repositório.
2. Crie `.github/workflows/news.yml` e `.github/workflows/report.yml` **pelo site do GitHub** (Add file > Create new file; digite o caminho com barras). Pastas que começam com ponto costumam ser ignoradas no upload pelo navegador.
3. Settings > Pages > Deploy from branch > main / root.

## 2. GitHub Actions (notícias e relatório diário)
1. Settings > Actions > General > Workflow permissions: **Read and write permissions** > Save.
2. Aba Actions > "Atualizar notícias" > Run workflow. Leia o log: cada fonte informa quantos itens trouxe e o final informa quantos têm imagem. Verde = ok; vermelho = copie o texto do log.
3. Aguarde cerca de 1 minuto e recarregue o site com Ctrl+F5.
4. Relatório diário por e-mail (opcional): em Settings > Secrets and variables > Actions crie SMTP_USER (seu e-mail), SMTP_PASS (senha de aplicativo do Gmail, exige verificação em duas etapas) e MAIL_TO (destinatários separados por vírgula). Depois rode "Enviar relatório por e-mail".
5. Se o agendamento não disparar: o GitHub pode atrasar tarefas agendadas e desativa agendamentos de repositórios sem atividade por 60 dias; rode manualmente para reativar.
6. Chave opcional GNEWS_KEY (gnews.io) para mais volume de notícias.

## 3. E-mail automático pelo chat (Apps Script, grátis)
1. script.google.com > Novo projeto > cole o conteúdo de `apps-script/Code.gs` e troque `NEWS_URL` pelo endereço do seu news.json no Pages.
2. Execute a função `teste` uma vez e autorize (envia um e-mail para você).
3. Implantar > Nova implantação > App da Web > Executar como: **Eu** > Quem tem acesso: **Qualquer pessoa** > Implantar. Copie a URL.
4. No index.html, preencha `const EMAIL_ENDPOINT="URL_COPIADA";` (procure por EMAIL_ENDPOINT) e envie o arquivo ao GitHub.
Limites: conta gmail.com ~100 destinatários/dia (Workspace 1.500; a Google pode mudar). O script envia no máximo 1 e-mail por endereço a cada 6 h e MAX_POR_DIA no total. O corpo é montado no servidor, não pela página.

## 4. Cuidados
- A URL do Apps Script é pública: o risco é alguém digitar o e-mail de outra pessoa. Por isso o conteúdo é fixo e inofensivo, há limite por endereço e por dia, e o rodapé explica a origem.
- LGPD: o site não guarda e-mail nem telefone. No envio automático o endereço passa pelo Google só para aquele envio. Não sou advogado; confirme o enquadramento do seu caso.
- Material educacional, não é recomendação de investimento.
