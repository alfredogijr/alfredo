# Passo a passo: obter credenciais do Google

Você vai precisar de **4 coisas** para conectar ao Google Ads:

| # | O que é | Onde pegar |
|---|---|---|
| 1 | Developer Token | Dentro do próprio Google Ads |
| 2 | Client ID | Google Cloud Console |
| 3 | Client Secret | Google Cloud Console |
| 4 | Refresh Token | Script automático (gerado por você) |

---

## PARTE 1 — Developer Token (Google Ads)

> Tempo estimado: 2 minutos

1. Acesse **ads.google.com** e entre com sua conta MCC
2. Clique no ícone de **ferramentas** (chave inglesa) no topo direito
3. Em "Configuração", clique em **API Center**
4. Se ainda não tiver, clique em **Solicitar acesso de teste**
5. Copie o valor do campo **Developer Token**
   - Vai parecer algo como: `ABc123xYz456...`
   - Em modo de teste você só acessa suas próprias contas — o que é perfeito para começar

> ⚠️ Guarde esse token. Ele vai no `.env` como `GOOGLE_ADS_DEVELOPER_TOKEN`.

---

## PARTE 2 — Client ID e Client Secret (Google Cloud Console)

> Tempo estimado: 5–8 minutos

### 2.1 Criar projeto

1. Acesse **console.cloud.google.com**
2. No topo, ao lado do logo Google Cloud, clique em **"Selecionar projeto"**
3. Clique em **"Novo projeto"**
4. Nome: `Google Ads MCC` (pode ser qualquer nome)
5. Clique em **Criar** e aguarde ~10 segundos

### 2.2 Ativar a Google Ads API

1. No menu lateral esquerdo → **"APIs e serviços"** → **"Biblioteca"**
2. Na barra de busca, digite: `Google Ads API`
3. Clique no resultado **"Google Ads API"**
4. Clique em **"Ativar"**
5. Aguarde a ativação (barra de progresso verde)

### 2.3 Criar credenciais OAuth2

1. No menu lateral → **"APIs e serviços"** → **"Credenciais"**
2. Clique em **"+ Criar credenciais"** (topo da página)
3. Escolha **"ID do cliente OAuth"**
4. Se aparecer uma tela pedindo para "Configurar tela de consentimento":
   - Clique em **"Configurar tela de consentimento"**
   - Escolha **"Externo"** → Criar
   - Preencha apenas o **Nome do app** (ex: `Meu MCC`) e o **e-mail de suporte**
   - Clique em **Salvar e continuar** em todas as telas até o final
   - Na aba **"Usuários de teste"** → adicione seu próprio e-mail
   - Volte para Credenciais → **"+ Criar credenciais"** → "ID do cliente OAuth"
5. Em **"Tipo de aplicativo"** selecione: **"App para computador"**
6. Nome: `Claude Code MCC` (qualquer nome)
7. Clique em **Criar**
8. Uma janela vai aparecer com:
   - **ID do cliente** → copie (vai no `.env` como `GOOGLE_ADS_CLIENT_ID`)
   - **Chave secreta do cliente** → copie (vai no `.env` como `GOOGLE_ADS_CLIENT_SECRET`)

> Formato esperado do Client ID: `123456789-abcdef.apps.googleusercontent.com`

---

## PARTE 3 — Refresh Token (script automático)

> Tempo estimado: 2 minutos

Com o `.env` preenchido com as 3 variáveis acima, execute:

```bash
python setup_auth.py
```

O script vai:
1. Gerar um link de autorização — copie e cole no navegador
2. Você faz login com a conta Google Ads
3. Autoriza o acesso
4. Copia o código que aparece na tela
5. Cola no terminal
6. O **Refresh Token** é gerado e salvo automaticamente no `.env`

---

## PARTE 4 — ID da MCC (Login Customer ID)

1. Acesse **ads.google.com**
2. Confirme que está na conta MCC (e não em uma conta cliente)
3. No canto superior direito, o ID da conta aparece no formato `XXX-XXX-XXXX`
4. Remova os hífens: `1234567890` → vai no `.env` como `GOOGLE_ADS_LOGIN_CUSTOMER_ID`

---

## Verificar se tudo funcionou

```bash
python test_connection.py
```

Saída esperada:
```
✅  Todas as variáveis de ambiente encontradas
✅  google-ads instalado corretamente
✅  Conectado! Conta: Minha MCC (ID: 1234567890) | Moeda: BRL
✅  MCC tem 5 conta(s) gerenciada(s)
```

---

## Resumo do .env final

```env
GOOGLE_ADS_DEVELOPER_TOKEN=ABcd1234...
GOOGLE_ADS_CLIENT_ID=123456789-abc.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=GOCSPX-...
GOOGLE_ADS_REFRESH_TOKEN=1//0abc...
GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890
```

---

## Problemas comuns

| Erro | Causa | Solução |
|---|---|---|
| `DEVELOPER_TOKEN_NOT_APPROVED` | Token em nível básico acessando contas de terceiros | Use apenas suas próprias contas ou solicite acesso padrão |
| `invalid_grant` | Refresh token expirado ou inválido | Execute `python setup_auth.py` novamente |
| `USER_PERMISSION_DENIED` | Conta não tem acesso à MCC | Verifique se está logado na conta certa |
| `CUSTOMER_NOT_FOUND` | ID da MCC errado | Confirme o ID sem hífens |
