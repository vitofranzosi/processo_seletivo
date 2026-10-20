# Quickstart — 093

## Os testes

```bash
cd backend && uv sync --extra dev --extra assistente
LC_ALL=pt_BR.UTF-8 TEST_DB_ENGINE=postgresql DB_NAME=ps_093 DB_USER=$USER DB_RUNTIME_USER=$USER \
  uv run pytest tests/interface/test_falha_de_csrf.py tests/interface/test_csrf.py -q
```

E a verificação inteira: `make lint check test-pg DB_NAME=ps_093 POSTGRES_USER=$USER`, com
`LC_ALL=pt_BR.UTF-8`.

## No navegador

1. Suba um servidor desta worktree com um banco migrado e o seletor de identidade ligado — por
   exemplo a entrada `telas-082` do `.claude/launch.json`.
2. Abra `/gestao/identificar/demonstracao`. No console do navegador, troque a prova de um dos
   formulários e envie-o:

   ```js
   const f = document.querySelectorAll("form[method=post]")[0];
   f.querySelector("[name=csrfmiddlewaretoken]").value = "x".repeat(64);
   f.requestSubmit();
   ```

3. A resposta é a recusa da gestão, com o cabeçalho e a barra, o título "O formulário não pôde ser
   enviado", a frase "Nada foi gravado" e o link "Reabrir a tela como está gravada". O console mostra
   só o 403 do documento — nenhuma linha "Refused to apply…".
4. O mesmo em `/selecoes/acesso`, com o formulário do endereço de e-mail: a recusa do portal, com o
   link "Abrir a página do formulário de novo".
5. O terminal do servidor traz a linha `Envio recusado pela verificação de CSRF em …` com o motivo.
