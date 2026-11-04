# Verificação: Referência da Loteria Federal conferida antes do compromisso

O registro das tarefas que pedem medição (T001, T002, T028, T030, T032), as divergências deliberadas
do [plano](plan.md) e os achados que a implementação encontrou fora dela. Medido em 04/11/2026, na
worktree `sweet-rosalind-1204e0`, com `DB_NAME=ps_116`, os grupos `assistente` e `navegador`
instalados e 4 workers.

## T001 — Linha de base

Sobre `fac5e2f2` (a ponta do PR #370, sem código desta feature):

- `make preparar`: `46 de 46 tabelas append-only` na segunda passada; `Unidades: 1 semeadas.`;
- `make test-pg`: **14676 passando, 12 pulados, 1 falha**, em 644 s.

A falha é `tests/performance/test_ocupacao.py::test_a_apuracao_cabe_no_dobro_do_tempo_da_emissao_da_ordem`,
o teste de tempo que o `CLAUDE.md` registra como oscilante com 4 workers (*Um teste de tempo oscila
sob carga*). Ele passou nas duas rodadas seguintes, com o código desta feature.

Os 12 pulados, agrupados por arquivo e motivo:

| Quantos | Arquivo | Motivo |
|---|---|---|
| 10 | `tests/test_vocabulario_da_composicao.py` | o template não usa o termo em texto visível |
| 1 | `tests/integration/test_database_permissions.py` | a recusa por vendor só aparece fora do PostgreSQL |
| 1 | `tests/interface/test_sorteio_com_a_fonte_de_producao.py` | o E2E contra a Caixa, atrás de `SORTEIO_E2E_FONTE_REAL` |

## T002 — Inventário

27 arquivos de `backend/tests/` citam `"Loteria Federal"` (o plano contava 18 com `"source"`; a
diferença são os arquivos de PDF e de redação, que a citam em prosa ou em JSON do corpus).

**Nenhum deles compara a lista inteira de achados de um ato.** Os três arquivos da suíte que leem
`validationFindings` da submissão — `contract/test_edital_draft_api.py`,
`integration/publicacoes/test_numeracao_na_publicacao.py` e
`integration/publicacoes/test_correcoes_de_norma_na_publicacao.py` — filtram por código, e não veem
o `INFO` novo. As chamadas diretas a `validate_for_publication` não passam `situacoes`, e por
isso não produzem achado desta feature (`situacoes=None`).

A fonte de demonstração também confere (FR-3650), e o `INFO` aparece em todo ato de Edital que a
declara. Pela mesma razão, nenhuma expectativa muda.

O que o inventário **não** previu, e a suíte mostrou (T029):

| Arquivo | Por que mudou | O que mudou |
|---|---|---|
| `unit/editais/test_forma_da_ocorrencia_na_composicao.py` | prova a guarda da `035` (derivação) com a Loteria Federal, onde a forma da `116` responde antes, com outra frase | a fonte do método do arquivo passa a ser a de demonstração; a guarda da `035` continua inteira para ela |
| `fixtures/corpus.py` (184 casos do `assistente` e do `kit`) | o Edital 91/2026 do corpus declara `Concurso 6010` na Loteria Federal, e a forma o recusa na gravação | o corpus é republicado como acervo: sem a forma e sem a conferência, que não existiam quando ele foi publicado. O JSON gravado não muda |
| `interface/test_sorteio_com_a_fonte_de_producao.py` | ver T028 | reidentifica depois de desfazer o relógio; ganhou o passo 6 |
| `specs/033-navegacao-por-capacidade/inventario-das-negativas.md` | a view nova responde 404 | uma linha nova |

## T028 — O E2E contra a Caixa real

`SORTEIO_E2E_FONTE_REAL=1`, `tests/interface/test_sorteio_com_a_fonte_de_producao.py` e
`tests/test_suite_sem_caixa.py`: **2 passando e 2 pulados** — o E2E e o caso do padrão do vigia
passam, e os dois casos que provam a recusa da conexão se desligam com a chave, de propósito. Em
04/11/2026, às 09h51, sobre `4563a96f`.

**O E2E estava quebrado antes desta feature**, e a causa não é dela: a sessão de identificação era
aberta com o relógio recuado para cinco dias antes do 6098 (06/09/2026), e a validade padrão de duas
semanas venceu antes de hoje. Ao desfazer o relógio, a tela do sorteio devolvia a identificação, e o
percurso parava no passo 2 com o corpo vazio. Reproduzido na base (`fac5e2f2`) com o mesmo
resultado. A correção é reidentificar depois de desfazer o relógio, e está comentada no arquivo.

Durante o relógio recuado, a conferência é a do vigia da suíte ("ainda não realizado"), e não a da
Caixa: a Caixa de hoje sabe que o 6098 foi realizado, e recusaria a publicação e o congelamento que
o percurso finge fazer antes da extração. Com o relógio de volta, o passo 6 novo confere o 6098
**contra a Caixa de verdade**: `REALIZADO`, realizado em 06/09/2026, e o último informado maior ou
igual a ele. É a única medida do contrato real da consulta de uma tentativa.

## T030 — A suíte inteira

`cd backend && make lint check test-pg`, sobre `4563a96f`:

- `ruff check` e `ruff format --check`: limpos; `manage.py check` e `makemigrations --check`: sem
  mudança;
- `make test-pg`: **14939 passando, 12 pulados, nenhuma falha**, em 640 s.

**Comparado por lista, e não por total.** Os 12 pulados são os mesmos da linha de base, arquivo a
arquivo e motivo a motivo (`diff` vazio sobre `-rs` sem o número da linha). A falha da base — o teste
de tempo da ocupação — não se repetiu. Os 262 casos a mais são os dos 13 arquivos novos desta
feature, com as parametrizações, mais os dois casos novos de `test_metodo_do_marco.py` e
`test_suite_sem_caixa.py`; nenhum caso existente deixou de rodar.

Duas rodadas intermediárias ficaram registradas aqui porque mostraram o que o inventário não viu:

- **depois da US1** (sobre `dbfb1c2b`): 14821 passando e 2 falhas — o caso da forma `6106-9`, que
  dependia da US5, e uma jornada do Playwright (`test_us3_concessao_e_revogacao_pela_tela…`) que
  caiu com `TargetClosedError`, de navegador, e não se repetiu;
- **depois das US2 a US6** (sobre `30bf43fe`): 85 falhas e 100 erros, todos de duas causas — 184
  do corpus do 91/2026 (`Concurso 6010`, ver T002) e 1 do inventário de negativas da `033`. As duas
  foram corrigidas em `4563a96f`.

## T032 — O roteiro local no navegador

Banco de desenvolvimento `ps_116`, `SORTEIO_FONTE_DE_DEMONSTRACAO` ligada (padrão do
`development`), runserver na porta 8116, identificada como `ana.elaboradora` pelo seletor de
demonstração. Um Edital em elaboração com marco de sorteio e o método declarando a "Fonte de
demonstração", concurso 5000, extração em 06/12/2026 às 19h.

Na etapa Classificação, o botão **Conferir na Caixa**, junto do campo do concurso do marco, com o
número trocado na tela antes de cada clique (sem gravar):

| Concurso | Classe | O que apareceu no lugar |
|---|---|---|
| 5000 | `impede` | O concurso 5000 da Fonte de demonstração já foi realizado, em 26/08/2015. A semente precisa vir de uma extração que ainda não aconteceu quando a relação de participantes for congelada. O último concurso realizado é o 5000, de 26/08/2015: declare um concurso posterior a ele, que ocorra depois do fim das inscrições, conferindo o número e a data no calendário oficial da Caixa. |
| 9998 | `adverte` | Não foi possível verificar na Caixa se o concurso 9998 já foi realizado: a Caixa não respondeu a tempo. Isso não confirma nem recusa o concurso. Confira no resultado oficial da Fonte de demonstração que ele ainda não foi realizado. |
| 6200 | `informa` | Concurso 6200: ainda não realizado na consulta de 04/11/2026 às 09:26. O último concurso realizado é o 5000, de 26/08/2015; o declarado está 1200 concurso(s) adiante, e a data declarada, 06/12/2026, 4120 dia(s) depois. A data prevista não é verificada pela Caixa: confira no calendário oficial que o concurso 6200 é o de 06/12/2026. |

Depois, **Submeter para revisão** com o 5000 gravado: a confirmação voltou com HTTP 422 e o alerta
"O marco M1: O concurso 5000 da Fonte de demonstração já foi realizado, em 26/08/2015…". O console
do navegador ficou sem mensagem nenhuma — nenhuma violação de CSP.

## Divergências deliberadas do plano

| Plano | Implementado | Por quê |
|---|---|---|
| Demonstração com último 6114 (§1) | último **5000**, de 26/08/2015; 5000 realizado e 9998 inconclusivo | a suíte declara `6113` com a fonte de demonstração, e com o 6114 a tabela diria "ainda não realizado, −1 concurso adiante" do 6113. Com o 5000 a tabela é coerente com a regra (menor ou igual é realizado), e o roteiro do plano (5000, 9998, 6200) dá as três mensagens |
| Forma `^\d{1,6}$` (§1) | `^0*\d{1,6}$` | `0006116` tem sete caracteres e é o 6116; os zeros à esquerda não contam nos seis algarismos (FR-3623 manda aceitá-los). `1234567` continua recusado |
| Conferência sob demanda por `POST` (§6) | fragmento `GET`, `interface:fragmento-conferir-referencia` | é a convenção de todo fragmento da composição (R-004 da `043`), e a conferência é leitura: não grava nada nem exige CSRF. A recusa de entrada é 404 sem consulta; a falta de capacidade, 403 |
| Rótulo "Número do concurso" (§6) | o rótulo continua "Ocorrência que fixará a semente"; mudam a ajuda e o exemplo (`6115`) | o rótulo é o de `CAMPOS_DO_METODO`, o mesmo do documento publicado e da Retificação (FR-507 da `035`, Princípio I), e o campo serve também à fonte de demonstração, que aceita texto. A ajuda pede só o número na Loteria Federal (FR-3643) |
| Duas chamadas de 5 s cabem em 15 s (§1) | teto de 15 s **somado** em `FonteExterna.conferir_referencias` | com várias referências realizadas e a Caixa lenta, cada data de 5 s somaria além do teto (medido: 20 s com quatro). A data que não cabe não é pedida; a recusa vale sem ela (FR-3629). `test_a_espera_com_a_fonte_que_dorme_nao_passa_de_quinze_segundos` falhava sem o teto |
| `detalhe` com os campos da FR-3647 (§7) | os mesmos, mais `ato`, `caminho`, `alvo` e `declaradaEm` | é o que permite à tela repetir a mensagem do ato a partir do registro, sem consultar de novo (FR-3646) |
| `_assert_well_formed` recebe as situações (§4) | recebe, por `_materialize_affected_versions`, fronteira a fronteira | é onde a Retificação já confere o conteúdo que passa a vigorar; o registro do log da recusa envolve essa chamada |

O motivo da referência travada sem consulta correspondente (FR-3632) é "não foi possível falar com a
Caixa", um dos quatro do contrato: é verdade sobre ela, que não foi consultada.

## Emenda de 04/11/2026 — o reaproveitamento (T033–T038)

A revisão bloqueante, com diagnóstico, alternativas e critério de liberação, está em
[revisao-do-reaproveitamento.md](revisao-do-reaproveitamento.md). Aqui fica o que foi medido.

**Os testes novos, vistos falhando antes do código.** Sobre o código da T030, antes da T036:
`test_metodo_sem_a_extracao.py` e `test_reaproveitamento_sem_a_extracao.py` deram **17 falhas e 4
passando**. As falhas eram exatamente os dois defeitos do diagnóstico — o `Concurso 6010` do 91/2026
recusava a cópia inteira (`invalid_draw_method`), e o `6010` válido chegava ao destino em silêncio. Os
quatro que passavam eram regras que a emenda preserva, e continuaram passando. Os dois
casos da tela (`test_reaproveitar.py`, T037) falharam antes do template.

**O mecanismo do acervo (T033).** `tests/fixtures/legado.py::antes_da_116()` é o único lugar que
desliga a forma e a conferência. Usam-no o corpus (`tests/fixtures/corpus.py`) e três casos de acervo
da 116 — o congelamento e duas Retificações. Nenhum teste de reaproveitamento o usa para o destino:
o arquivo da US7 só o cita na docstring, e a origem histórica chega pela fixture do corpus (conferido
por `grep` em 04/11/2026).

**A suíte (T038).** `cd backend && make lint check test-pg`, sobre o commit da emenda:

- `ruff check` e `ruff format --check` limpos; `manage.py check` e `makemigrations --check` sem
  mudança;
- `make test-pg`: **14964 passando, 12 pulados, nenhuma falha**, em 652 s, sobre `fc154aa9`. Os 12
  pulados são os mesmos da linha de base (`diff` vazio). Os 25 casos a mais que na T030 são os dos
  dois arquivos novos e os dois casos novos de `test_reaproveitar.py`; nenhum caso existente mudou de
  expectativa nesta emenda;
- o E2E com `SORTEIO_E2E_FONTE_REAL=1` continua passando (04/11/2026, 10h38).

**O achado 2 abaixo, sobre o reaproveitamento do acervo, foi resolvido pela emenda** (FR-3715): a
cópia do 91/2026 conclui, sem a extração.

## Achados para o usuário (não são escopo desta implementação)

1. **Corrigido na emenda.** A spec dizia "5885 concursos adiante" para o 9999 (*Edge Cases*), e a conta com o último 6114 dá
   **3885**. O teste usa 3885.
2. **Resolvido pela emenda de 04/11/2026** (FR-3715): a cópia não traz a extração, e por isso a
   grafia da origem não impede mais o reaproveitamento. O registro original fica abaixo.
   **Reaproveitar um Edital do acervo com a ocorrência fora da forma passava a ser recusado.** O
   reaproveitamento (A-10) grava o rascunho por `replace_draft`, e a forma da Loteria Federal é
   conferida ali (FR-3624). O 91/2026 do corpus é um caso real: `Concurso 6010`. É o padrão que o
   reaproveitamento já adota ("um valor que a origem publicou sob regra mais frouxa recusa a cópia
   inteira"), e a mensagem diz o que corrigir — mas quem reaproveita não pode corrigir antes da
   cópia. Fica registrado para decisão: manter, ou normalizar só na cópia.
3. **`scripts/publicar_corpus_do_piloto.py` continua funcionando** porque usa a fixture do corpus,
   que agora republica como acervo.
4. **O E2E da fonte real envelhece sozinho** (ver T028): ele usa um concurso fixo do passado, e a
   validade da sessão era mais curta que a idade dele. Corrigido aqui por ser condição da T028.
