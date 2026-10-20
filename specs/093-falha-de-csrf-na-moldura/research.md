# Pesquisa — 093

Caminhos de código relativos a `backend/processo_seletivo/`; de teste, a `backend/tests/`. A base é a
`main` em `745f115f`; o banco de teste, `ps_093`; o da prova no navegador, `ps_inventario_082`, pela
entrada `telas-082` do `.claude/launch.json` (porta 8084), servindo o código desta worktree.

## R-001 — O que o framework faz quando a verificação recusa

O `CsrfViewMiddleware` (Django 5.2) recusa em `process_view` e chama a view de `CSRF_FAILURE_VIEW`
com a requisição e um `reason` — uma frase em inglês, constante do módulo: `CSRF cookie not set.`,
`CSRF token from POST incorrect.`, `CSRF token missing.`, `Origin checking failed - … does not match
any trusted origins.`, `Referer checking failed - … does not match any trusted origins.`, entre
outras. As duas últimas trazem o endereço que o navegador informou, isto é, texto de fora.

A view padrão, `django.views.csrf.csrf_failure`, renderiza o `403_csrf.html` — em inglês, com um
`<style>` no `<head>` — e, com `DEBUG`, acrescenta o `reason` e uma explicação para desenvolvedor. Sob
a política em recusa (`shared/politica_de_conteudo.py`), o navegador recusa o `<style>`: a página sai
sem desenho, como a `091` e a `092` registraram. Com `DEBUG`, a variante técnica traz a marca
`<meta name="robots" content="NONE,NOARCHIVE">` e escapa da política pela decisão 010 da `091`; sem
`DEBUG`, não.

**Só o modelo não bastaria (D-001).** `CSRF_FAILURE_TEMPLATE_NAME` troca o modelo, mas a view padrão o
renderiza com `loader.get_template(...).render(contexto)`, sem a requisição: os processadores de
contexto não rodam, e as bases das duas áreas precisam deles — `contexto_identidade` e
`contexto_da_navegacao`, na gestão; `contexto_candidato`, no portal. O modelo também não teria como
saber de que área o envio veio.

**A view nova** (`interface/erros.py`, `falha_de_csrf`) recebe `(request, reason="")`, que é a
assinatura que `check_csrf_failure_view` (o `security.E101` e o `E102` do framework) confere no `manage.py
check`. Ela renderiza as recusas que já existem — `interface/recusa.html` e `portal/recusa.html` —
pelo `render`, com a requisição, e responde 403. A resposta volta pelos middlewares de fora: a
política, o `X-Frame-Options`, e o próprio CSRF, que grava o cookie novo quando a página o emitiu.

## R-002 — Onde a recusa aparece

- **Gestão** (`/gestao/`): todo formulário `POST` das telas, inclusive o seletor de identidade.
- **Portal** (`/selecoes/`): os formulários de acesso, da inscrição, dos recursos, o "Sair" do
  cabeçalho e os dois formulários da barra de documentos, que também enviam por htmx (R-004).
- **Fora das duas**: as views da raiz (`/`, `/health`, `/readiness`, `/metrics`) e toda a API são
  `APIView` do DRF, que as marca `csrf_exempt`; a autenticação da API é por cabeçalho. Um endereço que
  não resolve não chega ao `process_view`. Hoje, nenhum envio fora das duas áreas passa pela
  verificação; o ramo existe para o que vier (D-002), e é provado chamando a view diretamente.

A escolha da moldura lê `request.path_info`, como a política lê desde a revisão da `091`: com a
aplicação sob um prefixo de implantação, `request.path` o traria, e `/gestao/` deixaria de casar.

## R-003 — O motivo vai para onde

O Django já registra a recusa: `log_response("Forbidden (%s): %s", reason, path)`, no logger
`django.security.csrf`. Mas o `LOGGING` do sistema (`config/settings/base.py`) só configura
`processo_seletivo` e `django.request`, e o `django.security.csrf` cai no logger `django` do
`DEFAULT_LOGGING` do framework, cujos manipuladores são o console **com o filtro `RequireDebugTrue`** e
o e-mail aos administradores **com `RequireDebugFalse`**, que sem `ADMINS` não manda nada. Medido
nesta worktree, com `config.settings.test`: a cadeia do `django.security.csrf` termina na raiz sem
manipulador, e com `DEBUG` desligado a linha não sai em lugar nenhum.

Por isso a view registra no logger do projeto (`processo_seletivo.interface`, o mesmo da recusa do
envio grande), em nível de aviso, com o caminho e o motivo por `%r` — o motivo pode trazer o endereço
que o navegador informou, e a representação escapa quebra de linha. No runserver as duas linhas
aparecem, a do framework e a do sistema; em produção, só a do sistema, em JSON, que é o que se coleta.

## R-004 — O envio por fragmento (registrado, e não feito)

A barra de documentos do portal (`portal/_documentos.html`) envia e remove por `hx-post`. O htmx 2
não troca o alvo por resposta 4xx (`responseHandling` padrão: `[45]..` sem troca, com erro): diante
de uma recusa da verificação, o botão parece não responder. Era assim com a página do framework e
continua — a página nova só é vista nos envios de página inteira. Resolver pede decidir como um
fragmento mostra a recusa, o que a gestão resolveu, em outro caso, com 200 e `HX-Retarget`; não é o
pedido desta feature.

## R-005 — A prova no navegador

Na entrada `telas-082`, com o código desta worktree: o formulário do seletor de identidade da gestão
e o de acesso do portal, cada um enviado com a prova trocada por 64 caracteres inválidos (e, no
primeiro envio da gestão, sem o cookie), a 1280 × 900 e a 375 × 812.

| Página | Largura | Título | Folhas carregadas | Estouro | Violações da política no console |
|---|---|---|---|---|---|
| Gestão | 1280 | "O formulário não pôde ser enviado" | 8 | não (1280 = 1280) | 0 |
| Gestão | 375 | idem | 8 | não (375 = 375) | 0 |
| Portal | 375 | idem | 2 | não (375 = 375) | 0 |
| Portal | 1280 | idem | 2 | não (1280 = 1280) | 0 |

O único erro do console em cada passada é o do próprio documento, "Failed to load resource: … 403".
O terminal do servidor trouxe, a cada envio, a linha do sistema com o motivo — `CSRF cookie not set.`
e `CSRF token from POST incorrect.` — e a do framework logo abaixo.

## O que ficou registrado, e não foi feito

- **A recusa do domínio lê `request.path`** (`RecusaDoDominioMiddleware`, em `interface/erros.py`):
  sob um prefixo de implantação, nenhuma das duas molduras casaria e a recusa do domínio voltaria a
  ser erro de servidor. A view desta feature lê `path_info`; a do domínio não foi tocada.
- **O envio por fragmento** (R-004).
