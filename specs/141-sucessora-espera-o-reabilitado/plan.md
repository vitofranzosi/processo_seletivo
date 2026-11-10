# Implementation Plan: A ordem sucessora e o corte esperam a avaliação do reabilitado

**Branch**: `claude/141-sucessora-espera-reabilitado-af020a` | **Date**: 2026-11-10 | **Spec**: [spec.md](spec.md)

## Summary

Duas esperas na derivação do andamento da `127`, e um aviso na tela do corte. Nenhum comando muda.

1. **A sucessora espera as Etapas por fazer** (FR-4830 a FR-4834). Em `situacao_da_ordem`, o ramo da
   ordem obsoleta passa a olhar `faltam` antes de devolver o ato: com Etapa por fazer, a célula é
   *Depois*, com a razão da UX-340 e o dado `vigente_para_tras`. O resultado lê esse dado pela função
   nova `ordem_para_tras`, nos três lugares que liam `situacao == OBSOLETO`.
2. **O corte espera o reingresso** (FR-4835 a FR-4838). `situacao_do_corte` recebe `reingresso`. Com
   ele, a célula é *Depois* nas duas formas: a emitir, depois da ordem feita; e obsoleta. A leitura
   (`_Leitor._reingresso_pendente`) chama `publicabilidade.reingressos_pendentes`, a mesma função que
   recusa a publicação, uma vez por marco, só quando o corte poderia ser providência.
3. **O aviso na tela do corte** (FR-4840, FR-4841). A view `corte` conta os reingressos pendentes
   pela mesma função, para quem pode emitir, e o template o diz antes do botão.

## Technical Context

**Language/Version**: Python 3.13, Django 5 · **Storage**: PostgreSQL 16, sem migration ·
**Testing**: pytest, contra PostgreSQL (`make test-pg`) · **Constraints**: o orçamento de consulta
da `127` (FR-4120), que mede o detalhe do Edital em escala.

## Constitution Check

- **Publicação imutável, nada excluído**: nada é gravado; a derivação é leitura.
- **Negar por padrão**: nenhuma permissão nova; o aviso só sai para quem já pode emitir o corte.
- **Rastreabilidade**: cada requisito tem linha em [rastreabilidade.md](rastreabilidade.md).

## Desenho

### A célula ganha um dado, e não uma situação

`Celula.vigente_para_tras: bool = False`. A alternativa, uma oitava situação, seria estado de
apresentação novo para a legenda, a folha e os guardiões da `127` — e o caso é exatamente o *Depois*
que a apuração já usa para "está para trás, e a sucessora espera" (D-001).

Quem lia a ordem obsoleta:

| Leitor | Lia | Passa a ler |
|---|---|---|
| `_situacao_do_resultado`, o primeiro teste | `ordem.situacao == OBSOLETO` | `ordem_para_tras(ordem)` |
| `_resultado`, quando precisa do ato | `ordem.situacao in (FEITO, OBSOLETO)` | `FEITO`, ou `ordem_para_tras` |
| `_resultado`, quando afere | `ordem.situacao != OBSOLETO` | `not ordem_para_tras(ordem)` |
| `situacao_do_corte`, `situacao_da_apuracao` | `ordem.situacao != FEITO` | sem mudança: dizem *Depois* com as duas |
| `centro.agregar` (`136`) | só *Depois* → "ainda não começou" | com o dado, "em curso" (FR-4845) |

### A lista vazia

A pergunta das listas vazias (`_listas_vazias`, da `135`) era feita para toda ordem obsoleta. Com
Etapa por fazer, a resposta não é lida, e a condição passa a ser `estado in ("obsoleto", "falta") and
not faltam`: a `141` não acrescenta consulta, e tira uma no caso novo.

### O reingresso no corte

- **A ordem dos ramos.** *Não se aplica* e *Feito* primeiro, como hoje (o ato vigente não é
  desmentido, D-004). Depois o obsoleto com reingresso. No corte a emitir, a ordem à espera vem antes
  do reingresso — a razão dela já nomeia a Etapa —, e o reingresso vem antes da espera do prazo
  recursal: esperar o prazo não basta enquanto o reabilitado não tem resultado.
- **O custo.** `reingressos_pendentes` faz uma consulta quando ninguém foi reabilitado no Edital, e
  uma por Etapa enumerada quando alguém foi. É perguntado uma vez por marco, na primeira lista que
  precisar, e só com o corte obsoleto ou a emitir sobre ordem feita. No sorteio, nunca (FR-4838).

### Os textos

- UX-340: *"a ordem sucessora lê {Etapas}, que ainda não está feita; a vigente continua produzindo
  efeito"* (plural: *"não estão feitas"*).
- UX-341: `REINGRESSO_NO_CORTE`, *"há inscrição reabilitada por recurso ainda sem resultado numa Etapa
  deste marco: o corte espera a consolidação dela e a ordem sucessora"*; no obsoleto, prefixada por
  *"o corte vigente está para trás, e "*.
- UX-342: *"N inscrição reabilitada por recurso está sem resultado numa Etapa deste marco. Emitido
  agora, o corte a deixa fora da faixa, porque está sem posição. Quando o resultado for consolidado,
  a ordem e este corte ficarão para trás, e suceder os dois exigirá motivo. Emitir agora continua
  possível."* — na classe `aviso` que a espera do prazo já usa, sem regra nova na folha.

## Testes

- **Unitários, puros** — `tests/unit/interface/test_sucessora_espera_o_reabilitado.py`: cada célula,
  inclusive o que o C08 não forma (duas Etapas, lista vazia, a preliminar publicada com a ordem à
  espera).
- **A cadeia, com banco** — `tests/integration/treinamento/test_sucessora_espera_o_reabilitado.py`,
  sobre o C08 carregado pelo comando da `134`, com os atos pelos comandos que as telas chamam:
  - a cadeia inteira (US3);
  - a sucessora parcial emitida pela tela e o corte anterior ao recurso (US2);
  - a correção de nota sem reabilitar (US4);
  - a tela do corte, com e sem reingresso (US5).
- **Sem mudança de expectativa**: `test_o_andamento_nunca_diz_pendente_para_a_ordem_que_o_comando_recusa`,
  os casos da lista vazia da `135`, e o orçamento em `tests/performance/test_andamento_em_escala.py`.

## Verificação

`cd backend && make lint check test-pg`, com `DB_NAME=ps_141`; e o C08 no navegador, num banco
descartável, com `CENARIOS_DE_TREINAMENTO=true`, `--banco` igual ao conectado e
`ARQUIVOS_CANDIDATOS_RAIZ` exportada. O roteiro e o que se viu ficam em [verificacao.md](verificacao.md).

## Project Structure

```text
backend/processo_seletivo/interface/andamento.py        # as duas esperas e o dado da célula
backend/processo_seletivo/interface/views.py            # o aviso: _reingressos_no_corte
backend/processo_seletivo/interface/centro.py           # a fase em curso com a vigente para trás
backend/processo_seletivo/interface/templates/interface/corte.html
backend/tests/unit/interface/test_sucessora_espera_o_reabilitado.py
backend/tests/integration/treinamento/test_sucessora_espera_o_reabilitado.py
```

**Sessão paralela.** A `139` também mexe em `andamento.py` (a URL da célula). Quem mergear depois
roda a suíte sobre o outro.
