# Quickstart: ver e medir o MVP de UX da Retificação (123)

## Pré-requisitos

- PostgreSQL local (no macOS com Homebrew, `LC_ALL` exportado).
- `cd backend && uv sync --extra dev --extra navegador && uv run playwright install chromium`.
- Um banco próprio desta worktree (`DB_NAME` distinto), preparado com `make preparar` e semeado com
  `seed_demo`, como na seção *Reprodução* da auditoria
  (`doc/auditoria-ux-retificacao-2026-11-05/README.md`).
- `runserver` com `INTERFACE_SELETOR_IDENTIDADE=true`, aberto em `localhost` (não `127.0.0.1`).

## 1. A suíte

```bash
cd backend && make lint check test-pg
```

A jornada de navegador roda dentro do `test-pg` com o grupo `navegador` instalado. Para assisti-la:

```bash
cd backend && PYTEST_ADDOPTS="-k jornada_da_retificacao_123" make test-navegador NAVEGADOR_VISIVEL=1
```

## 2. Os cenários pela tela (Edital 01/2026 do demo, como `ana.elaboradora`)

| Cenário | Faça | Espere |
|---|---|---|
| A | «Retificar» → «Encontrar»: `término` → «Ir ao campo» do Evento de inscrições; mude a data; «Ver o que vai mudar» | Foco no campo em 2 ações; na volta, o cartão «na proposta», a frase da base e "1 cartão com alteração na proposta". |
| B | `vagas` → o Perfil DOC-INFO; 3 → 4; «Ver o que vai mudar» | A seção "O que impede criar esta Retificação" com o impeditivo do quadro e «Ir ao cartão» até a 1ª linha do quadro. Nenhuma Retificação criada. Corrija a linha, confira: a seção some. |
| C | `requisito` | Os «Requisitos de participação» dos dois Perfis e a Seção «Requisitos gerais». |
| D | Três alterações em Cronograma, Perfis e Seções; conferir | Três selos «na proposta»; "3 cartões com alteração na proposta" e "Nenhuma alteração nova desde a última conferência"; cada «Ir ao campo» do resumo leva ao campo. Mude mais um: "1 campo alterado desde a última conferência". |
| G | Com a Retificação nº 3 do demo, de vigência futura | "Ela ainda não vigora: passa a vigorar em …" em Retificar e no detalhe/homologar/publicar de uma Retificação composta sobre ela; nenhum "Vigente hoje". |
| Edição | Devolva uma Retificação pela homologação e abra «Editar a Retificação» | Os cartões que o ato altera já marcados; a coluna «No rascunho». |

Teclado: repita D sem mouse — Tab até «Encontrar», digite, Enter (foco no 1º resultado), Enter (foco
no campo).

## 3. A medição da segunda etapa (FR-3950, SC-1182)

Sobre o Edital ampliado (`renderizar-edital-extenso.py`, ou a fixture `edital_extenso` num banco de
demonstração), a 1280×900 e a 375×812, pelo roteiro da auditoria estendido com E1–E3 da spec
(*Critério de decisão da segunda etapa*):

```bash
cd backend && UX_BASE=http://localhost:<porta> UX_SAIDA=/tmp/ux-retificacao-123 uv run python \
  ../doc/auditoria-ux-retificacao-2026-11-05/roteiro-de-captura.py
```

Registre ações e telas roladas de E1, E2 e E3 em `doc/` (pasta nova, datada), aplique a regra da spec
e leve os números ao usuário. A decisão é dele.
