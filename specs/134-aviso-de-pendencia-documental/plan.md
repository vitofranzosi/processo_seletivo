# Implementation Plan: O aviso de pendência documental por e-mail (134)

**Branch**: `claude/134-aviso-de-pendencia` | **Date**: 2026-11-08 | **Spec**: [spec.md](spec.md)

## Summary

O gesto *"Avisar as pessoas com pendência nesta chamada"*, na tela de condução da convocação, grava
um aviso da `066` de origem nova, `PENDENCIA`, por pessoa alcançada; o despacho da `066` envia. O
texto é composto por uma função pura, congelado no aviso e sem variáveis. A FR-084 da `010` passa a
cinco situações, e a guarda que as conta, a pares (módulo, situação).

## Technical Context

- **Linguagem e base**: Python 3.13, Django 5.2, PostgreSQL. Sem dependência nova.
- **Armazenamento**: as tabelas da `066`. Uma migration (`avisos/0002`) que muda duas
  *constraints* de `Aviso`: a lista de origens e o ato de cada origem. Zero tabelas, zero colunas.
- **Testes**: `tests/integration/avisos/test_aviso_de_pendencia.py` (transacional, PostgreSQL) e
  `tests/unit/avisos/test_texto_da_pendencia.py`. Guardiões tocados: `test_situacoes_de_mensagem`,
  `test_vocabulario_do_aviso`, `test_mensagem_da_convocacao` (SC-1161 da `121`) e o README.
- **Restrições**: a CSP (sem inline), regra na folha para toda classe (a seção usa só classes que
  já existem), sem `raise Http404` novo (a recusa de inexistente é `DomainError` 404, que o
  middleware traduz), e nada de e-mail real: o despacho usa o backend configurado.

## Constitution Check

- **Publicação imutável / nada se exclui**: o aviso é append-only, como na `066`; o gesto não muda
  convocação, lista, conferência nem desfecho.
- **Negar por padrão**: o gesto passa pelo predicado da conferência (FR-3595 da `115`), sob a trava
  do Processo e com o escopo filtrado; quem não alcança recebe a recusa de inexistente.
- **Rastreabilidade**: FR-4601 a FR-4623 e SC-1441 a SC-1449 na [matriz](rastreabilidade.md).

## Project Structure

```text
backend/processo_seletivo/avisos/
├── domain/nomes.py                 # PENDENCIA, recusas, operações, sujeito do despacho
├── domain/pendencia.py             # novo: o texto (assunto, corpo, rodapé)
├── application/pendencias.py       # novo: a seleção, a prévia e o gesto
├── application/despacho.py         # a constante da revisão e a trilha de cada envio
├── application/comando.py          # PENDENCIA na porta das telas da 066 (D-010)
├── application/confirmar.py        # o reenvio recusado (D-008)
├── models.py, migrations/0002_origem_pendencia.py
backend/processo_seletivo/interface/
├── views.py                        # avisar_pendencias_view e a prévia na condução
├── urls.py                         # convocacao/avisar-pendencias
└── templates/interface/convocacao.html, aviso.html, avisos_do_edital.html
```

## Decisões de implementação

- **Um aviso por pessoa** (D-002): o aviso guarda o texto final, e o texto é da pessoa.
- **A seleção lê o que a condução já lê**: `convocacoes_do_recorte`, `leituras_por_chamada`, as
  inscrições, os endereços e os avisos de hoje — consultas em número fixo, nenhuma por pessoa.
- **A raiz é a da condução**, por `documentos.raizes_das` (D-003): uma definição só, que a tela e o
  gesto compartilham. A prévia recebe da tela as raízes e as leituras que ela já fez.
- **O despacho relê a pendência antes de cada tentativa** (FR-4623, D-011), por
  `pendencias.motivo_para_nao_enviar`, e interrompe o aviso que chegaria tarde.
- **A unidade é lida uma vez por gesto, e os avisos se gravam em lote**: o gesto segura a trava do
  Processo.
- **O limite do dia** é lido de `DestinatarioDoAviso` (origem `PENDENCIA`, `solicitado_em` desde o
  início do dia local, convocações do recorte), mapeado para a raiz.
- **A trilha do envio** é escrita pelo despacho só para a origem nova (D-009), com o sujeito
  `sistema:despacho-de-avisos`, na mesma transação do resultado.
