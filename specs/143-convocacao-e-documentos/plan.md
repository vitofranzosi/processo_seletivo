# Implementation Plan: A convocação e a conferência documental, pelas perguntas de quem conduz

**Branch**: `claude/143-convocacao-e-documentos-770b40` | **Date**: 2026-11-10 | **Spec**: [spec.md](spec.md)

## Summary

Duas telas mudam de organização, sem mudar o que praticam: a da convocação de um recorte
(`interface/convocacao.html`) e a dos documentos de uma convocação
(`interface/convocacao_documentos.html`). Um módulo de leitura novo,
`interface/conducao_da_convocacao.py`, deriva — de dados que as views já leem — o contexto do
recorte, o índice "Neste recorte, agora", o passo de cada chamada e a situação do aviso de pendência
de cada chamada. As views `convocacao` e `documentos_da_convocacao` passam a chamá-lo; os templates
são reescritos sobre os mesmos formulários, ids e comandos. A prévia do aviso de pendência da `134`
passa a expor o motivo de cada chamada, que ela já calculava.

## Technical Context

**Language/Version**: Python 3.13, Django 5 (monólito)
**Primary Dependencies**: as de hoje; nenhuma nova
**Storage**: PostgreSQL; **nenhuma migration**, nenhum modelo novo
**Testing**: pytest contra PostgreSQL (`make test-pg`), cliente de teste do Django; Playwright para
os passeios
**Target Platform**: a gestão (`/gestao/`), sob a CSP da `091`/`092`
**Performance Goals**: a tela da convocação continua sem consulta por linha (os guardiões de
`tests/performance/test_convocacao.py` e `test_conducao_com_documentos.py`)
**Constraints**: sem script nem estilo no template; nenhuma regra nova; os fragmentos da `139`

## Constitution Check

- **Ato imutável e nada é excluído**: nada é gravado; as telas leem.
- **Negar por padrão**: as portas são as de hoje (`_edital_para_classificar`,
  `_convocacao_para_conferir`); o que a tela oferece segue `pode_emitir`, `pode_convocar` e o
  predicado da conferência da `115`, e cada comando confere de novo.
- **Representação não autoriza**: o passo da chamada orienta; o formulário do desfecho continua onde
  estava para quem conduz (D-007).
- **Rastreabilidade**: cada FR, SC, UX e caso-limite tem linha em `rastreabilidade.md`.

Sem violação. Pós-desenho: igual.

## O desenho

### 1. Leitura — `interface/conducao_da_convocacao.py` (novo)

- `contexto_do_recorte(edital, marco_id, lista_id)` → Edital, Perfil, marco e lista, pela versão
  vigente (`conducao_do_marco.marco_publicado` e `recortes_do_marco`). Uma leitura da versão.
- `passo_da_chamada(*, estado, desfecho, documentos, vencimento)` → `Passo(codigo, frase, tom,
  acao)`. Puro. Precedência: desfecho → sem comunicação → vencimento decorrido → estado documental
  (reenviado antes de "a conferir") → aguardando a resposta (D-007).
- `avisos_por_raiz(convocacoes, agora)` e `situacao_do_aviso(documentos, aviso, motivo,
  habilitado)` → `SituacaoDoAviso`. Uma consulta aos `DestinatarioDoAviso` de origem `PENDENCIA` das convocações
  do recorte, com as tentativas e a interrupção em `prefetch`; o estado pelo
  `avisos.domain.estado.estado_do_destinatario`. A pendência mais recente é o `conferido_em` da
  conferência vigente dos itens pendentes; o reenvio, o `apresentado_em` da versão vigente dos
  complementados. Aviso anterior à pendência não a cobre.
- `indice(...)` → as linhas do índice, na ordem fixa da FR-5001, com a âncora: seção da tela ou
  `convocacao-<id>` da primeira chamada no estado (D-003).
- `anotar(linhas, ...)` → acrescenta `passo` e `aviso` a cada linha que a view já montou.
- `pessoas_do_recorte(edital, vigente)` → a anterior, a seguinte e a próxima a conferir, e a leitura
  documental do recorte que a prévia do aviso reaproveita.

### 2. A prévia do aviso — `avisos/application/pendencias.py`

`previa` passa a devolver também `por_chamada: {str(raiz.id): motivo}` — `""` quando o gesto a
alcança. A seleção é a mesma; nenhuma regra muda.

### 3. As views — `interface/views.py`

- `convocacao`: depois de `_documentos_por_linha` e da prévia, `anotar` e `indice`; o contexto do
  recorte; `confere` (o predicado da `115`) e o envio habilitado.
- `documentos_da_convocacao`: o contexto do recorte; as convocações vigentes do recorte em ordem da
  tela (anterior, seguinte e próxima a conferir, numa leitura de número fixo); o passo e a situação
  do aviso desta chamada; o resumo; `pode_emitir` para o link do desfecho.

### 4. Templates e folha

- `convocacao.html` reescrito em: cabeçalho com contexto; índice; vagas em dois grupos; três áreas;
  cartões com o passo primeiro e as ações excepcionais numa linha secundária. Ids, nomes de campo,
  chaves e ações dos formulários intactos.
- `convocacao_documentos.html`: contexto, resumo, "Situação desta convocação", navegação entre
  pessoas; os itens como hoje.
- Folha nova `interface/telas/convocacao.css` (pelo bloco `estilo_da_pagina`) e a de documentos
  ampliada.

## Project Structure

```text
backend/processo_seletivo/interface/conducao_da_convocacao.py      (novo)
backend/processo_seletivo/interface/views.py                       (duas views)
backend/processo_seletivo/avisos/application/pendencias.py         (previa: por_chamada)
backend/processo_seletivo/interface/templates/interface/convocacao.html
backend/processo_seletivo/interface/templates/interface/convocacao_documentos.html
backend/processo_seletivo/interface/static/interface/telas/convocacao.css   (novo)
backend/processo_seletivo/interface/static/interface/telas/convocacao-documentos.css
backend/tests/unit/interface/test_conducao_da_convocacao.py          (novo)
backend/tests/integration/treinamento/test_convocacao_pelas_perguntas.py   (novo)
```

## Complexity Tracking

Nenhuma violação a justificar.
