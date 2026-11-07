# Verificação: A confirmação de "Encerrar Processo" adverte as providências em aberto (130)

Feita em 06/11/2026, na branch `claude/silly-engelbart-07c8f4`, sobre a `main` em `5cf5f179`. PR #421.

## A análise cruzada (spec × plano × tarefas)

`/speckit-analyze` antes de implementar: dez achados, todos corrigidos no commit `83630cd3`, antes da
primeira linha de código. O CRITICAL era a seção de LGPD ausente (princípio III da Constituição). O HIGH
era o cenário 2 da história 4, que ficara obsoleto depois do esclarecimento: a renovação vem antes do
motivo e do comando. Os demais eram cobertura (a linha de base de consultas, o GET de "Cancelar
Processo", o título antigo ausente), `[P]` indevido em tarefas do mesmo arquivo, a FR-4367 como
requisito sobre documentos e dois casos-limite (o prazo que vence com a tela aberta e o Processo com
muitos Editais).

## Suíte

`make lint check test-pg` com `DB_NAME=ps_130`, 4 workers. O ambiente tem só o grupo `dev`: sem
`assistente` e sem `navegador`.

| Rodada | Resultado |
|---|---|
| linha de base dos vizinhos (T002): `test_processo.py`, a confirmação da `113` e o desempenho dela | **44 passando** |
| 1ª, com a feature inteira | **17077 passando, 21 pulados, sem falha** (744s); `makemigrations --check`: *No changes detected* |
| final, depois da revisão | **17078 passando, 21 pulados, sem falha** (724s); `ruff check` e `ruff format --check` verdes; `manage.py check` sem achados; `makemigrations --check`: *No changes detected* |

Os 21 pulados não vêm da 130: os 31 testes novos rodaram todos, e nenhum tem marca de pular. O número
difere dos 12 do CLAUDE.md porque esta máquina não tem os grupos opcionais; a contagem por arquivo e
motivo está em *Pulados*, abaixo.

## O teste ajustado

| Teste | Por que mudou | O ajuste | O que continua provado |
|---|---|---|---|
| `tests/interface/test_processo.py::ato` (helper de `test_ativar_e_encerrar_seguem_o_fluxo_ordinario` e dos demais) | o envio sem resumo, no encerrar confirmável, passou a ser reapresentado (409) pela FR-4365 | o helper lê `advertencia.resumo` do contexto do GET e o envia, como o navegador envia o campo oculto | o fluxo de ativar, encerrar e cancelar pela tela, com as recusas de hoje |

Nenhum outro teste existente mudou. Os POSTs de `test_csrf.py` são recusados antes da view.

## A revisão independente (T029)

Feita por subagente, só leitura, com a spec e o diff. Nenhum achado de severidade alta. Os seis achados
e o que se fez:

| # | Achado | O que se fez |
|---|---|---|
| 1 | No "Ativar" e no "Cancelar", o motivo passara a voltar ao formulário, e o `impedimento` a ser relido na recusa, contra a FR-4364 | o motivo volta só no encerrar; no ativar e no cancelar, a recusa recalcula só os pendentes, como antes |
| 2 | A ordem das frases de prazo de recurso vem do banco (`pendencias_do_edital._dos_prazos_recursais` sem `order_by`), e o resumo dependia dela: 409 sem nada ter mudado | o resumo ordena as frases dentro de cada Edital; teste unitário novo |
| 3 | A prova da SC-1321 comparava a composição com uma cópia dela mesma | `_esperadas` redige as frases pela redação do relatório (`texto_da_pendencia`) e pela da `113` (`frase`), sem passar pela composição |
| 4 | O teste da D-002 podia ser vazio no cenário usado | cenário próprio: Edital encerrado com Retificação em revisão, com a prova de que a regra da `113` a produz e de que ela não chega ao Processo |
| 5 | No 422 do motivo a advertência era lida duas vezes, e a releitura da FR-4360 não era exercitada | o motivo é conferido antes do `try`, com a lista do próprio pedido; a releitura fica para a recusa do comando, provada pelo Processo encerrado por outra sessão; um teste conta uma leitura só |
| 6 | O orçamento de consultas com igualdade exata quebra com qualquer consulta a mais na `099` ou na `113` | mantido, como no teste de desempenho da `113`; registrado em *O custo* |

**Observação herdada da `113`, registrada e não alterada.** Num Edital abaixo do limiar de privacidade
do relatório (FR-2587 da `100`), `_providencias_da_099` mostra a contagem de convocações somada no Edital,
onde o relatório omite até a quantidade. A confirmação do Edital já faz isso, e a 130 o repete no
Processo. A spec aceita o caso ("somadas, sem Perfil"), e quem pode encerrar o Processo é a gestão.
Mudar a regra é decisão do usuário.

## O custo (SC-1324, D-007)

`do_processo` faz **145 consultas** com um Edital encerrado com convocação aguardando, com 38 e com 362
inscrições (escala 1 e 10). Cada Edital a mais custa **142**. É bem mais que as 23 da confirmação do
Edital, porque aqui o relatório da `099` é lido inteiro por Edital. Foi aceito pela D-007: a tela é
rara, e o Processo tem poucos Editais. O número está fixado por igualdade em
`tests/performance/test_confirmacao_do_encerramento_do_processo.py`. Uma consulta a mais no relatório
o quebra, como quebra o da `113`, e quem mexer no relatório atualiza os dois.

**Desvio do T002**: a linha de base de consultas da lista e do detalhe não foi medida em número. A prova
de que eles não pagam nada é mais forte e não envelhece: o teste os abre com `do_processo` trocado por
uma função que falha se for chamada.

## As capturas (T026)

Num banco descartável (`ps_130_demo`), com os cenários do relatório montados pelos helpers dos testes.
O servidor rodou com o relógio no instante de referência do cenário
(`demonstracao/servidor.py`, entrada `advertencia-130` do `.claude/launch.json`).

- `capturas/a-convocacao-no-prazo.jpg`: o bloco, a frase da UX-276, o Edital 61/2026 e "1 convocação
  aguardando resposta, até 30/10/2026.", antes das consequências.
- `capturas/c-a-lista-mudou.jpg`: depois de registrar o aceite da reservada pelo shell, com a tela
  aberta, o envio voltou com **409**, a mensagem da UX-279, a lista atual (vazia: a frase da UX-277) e o
  motivo preenchido. O envio seguinte encerrou o Processo ("Ato registrado").
- `capturas/e-nada-em-aberto.jpg`: o Processo do Edital 62, sem nada em aberto: a frase da UX-277, sem
  bloco.

O console do navegador registrou só o 409 da renovação, sem violação de CSP. O roteiro do quickstart
previa uma convocação feita com a tela aberta; o domínio recusou a nova convocação por falta de vaga
(`sem_deficit`), e a mudança da lista foi provocada pelo aceite, como no teste.

## Pulados

Agrupados por arquivo e motivo (`pytest -rs`, rodada final). Nenhum é desta feature.

| Quantos | Arquivo | Motivo |
|---|---|---|
| 10 | `test_vocabulario_da_composicao.py` | pares *termo × template* em que a tela não usa o termo em texto visível (deliberados, CLAUDE.md) |
| 8 | `tests/navegador/*` | sem o grupo opcional `navegador` |
| 1 | `unit/duvidas/test_tokens.py` | sem o grupo opcional `assistente` (`tokenizers`) |
| 1 | `integration/test_database_permissions.py` | a recusa por vendor, que só aparece fora do PostgreSQL |
| 1 | `interface/test_sorteio_com_a_fonte_de_producao.py` | o E2E da Caixa, atrás de `SORTEIO_E2E_FONTE_REAL` |

Com os grupos `assistente` e `navegador` instalados, como no CI, sobram os 12 do CLAUDE.md: os nove
arquivos de jornada no navegador e a contagem do tokenizer rodam.

A varredura de vocabulário não lê `processo_confirmar.html`: ela tem lista literal de templates, e a tela
do Processo não está nela. As frases novas (UX-275 a UX-277, UX-279), tiradas do template, foram passadas
pelos `PROIBIDOS` de `test_vocabulario_da_convocacao.py` e de `test_vocabulario_do_requerimento.py`,
por um script avulso, sem nenhum achado.
