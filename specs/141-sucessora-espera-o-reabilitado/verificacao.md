# Verificação: A ordem sucessora e o corte esperam a avaliação do reabilitado (141)

## No navegador (SC-1516)

**Onde.** Um banco descartável, `ps_141_nav`, preparado pelo `make preparar` (53 de 53 tabelas
append-only protegidas), com uma autoridade fictícia registrada e o C08 carregado pelo comando da
`134`:

```bash
CENARIOS_DE_TREINAMENTO=true ARQUIVOS_CANDIDATOS_RAIZ=<pasta descartável> DB_NAME=ps_141_nav \
  uv run python manage.py carregar_cenarios_de_treinamento --cenario C08 --banco ps_141_nav \
  --autoridade <a fictícia>
```

O servidor rodou da worktree, com o seletor de identidade, como `treino.presidencia`.

**Como os atos foram praticados.** Pelo mesmo comando que a tela chama, num shell, com os
auxiliares do teste de integração (`_deferir_correcao_da_prova`, `_emitir_sucessora`,
`_avaliar_titulos`). O painel do navegador estava oculto e não rolava até o botão "Emitir ordem"; as
telas foram lidas pelo navegador em cada estado.

| Estado | O que o Centro e as telas disseram |
|---|---|
| Antes do recurso | "Emitir o corte" à espera do prazo recursal; publicar o definitivo à espera; a ordem da PPP vazia |
| Recurso do 08 deferido (prova de 5,0 para 6,0) | **uma** ação: "Distribuir 1 inscrição sem avaliador suficiente — Análise de títulos". Nenhuma sucessora, nenhum corte. Na fase Classificação: *Depois*, "a ordem sucessora lê Análise de títulos, que ainda não está feita; a vigente continua produzindo efeito" |
| O mesmo, no mapa de fases | Classificação "Em curso · nada a fazer agora" — antes da FR-4845, "Ainda não começou" |
| Sucessora parcial emitida pelo comando (o 08 sem posição) | célula do corte *Depois*, "há inscrição reabilitada por recurso ainda sem resultado numa Etapa deste marco: o corte espera a consolidação dela e a ordem sucessora"; nenhum corte entre as providências |
| A tela do corte, no mesmo estado | o aviso "1 inscrição reabilitada por recurso está sem resultado numa Etapa deste marco. Emitido agora, o corte a deixa fora da faixa, porque está sem posição…", antes do botão "Emitir corte", que continua |
| Análise de títulos do 08 consolidada | o Centro oferece "Classificar a lista · Ampla concorrência · no GPS: emitir a ordem sucessora"; o corte ainda não |
| Sucessora completa emitida | "Emitir o corte" à espera do prazo recursal (recomendação da `133`); a tela do corte sem o aviso do reingresso, com o da espera |

O console do navegador só registrou o 404 do favicon.

## A suíte

`cd backend && make lint check test-pg`, com `DB_NAME=ps_141`, sobre a `main` em `4ae78556`, com o grupo
`assistente` e sem o `navegador`, 4 workers: **17714 passando, 21 pulados, nenhuma falha**, em 1694 s
(10/11/2026, com as suítes da `139` e da `140` no mesmo cluster). `ruff check` e `ruff format --check`
limpos; `makemigrations --check` sem mudança.

## O que não foi coberto

- A emissão do corte e a distribuição da Análise documental foram provadas no teste de integração
  (`test_a_cadeia_do_reabilitado_oferece_um_ato_de_cada_vez`), e não no navegador: no C08 o prazo
  recursal só se encerra em cinco dias, e a leitura do teste passa o instante adiante.
- O corte obsoleto com reingresso pendente (FR-4836) só se forma com quem estava no universo da
  ordem; o C08 não o forma, e ele está provado nas células puras.
