# Matriz de regressão — PS-RET-002

## Novas regressões automatizadas

| Requisito | Cenário | Teste | Resultado final |
|---|---|---|---|
| FR-2609 / FR-2610 | Formulário parte da vigente; rascunho não altera público; imediata publica com futuro; histórico e ato futuro imutáveis | `tests/interface/test_base_temporal_da_retificacao.py::test_formulario_publica_imediata_sem_sobrescrever_ato_futuro` | APROVADO |
| FR-2611 | Três tipos de Evento, publicação/retificação, igualdade, offsets distintos, mudança de dia, término nulo e início malformado | `tests/unit/editais/test_intervalo_do_evento.py` (36 casos) | APROVADOS |
| FR-2611 / FR-2612 | Intervalo invertido é recusado antes de criar ato | `test_intervalo_retificado.py::test_publicacao_de_intervalo_invertido_recusa_sem_efeito_parcial` | APROVADO |
| FR-2611 / FR-2612 | Dois Eventos alterados, um inválido; nenhuma alteração parcial | `test_intervalo_retificado.py::test_um_evento_invalido_impede_publicacao_mesmo_com_outro_valido` | APROVADO |
| FR-2612 | Atos individualmente válidos produzem inversão por concorrência; publicação 422 com rollback | `test_intervalo_retificado.py::test_publicacao_recusa_intervalo_invertido_por_ato_concorrente` | APROVADO |
| FR-2610 / FR-2612 | Imediata válida agora invalidaria intervalo futuro; nenhuma versão/ato parcial | `test_intervalo_retificado.py::test_intervalo_invalido_na_fronteira_futura_recusa_imediata_atomicamente` | APROVADO |
| FR-2611 | Igualdade continua publicável pela API | `test_intervalo_retificado.py::test_evento_com_inicio_igual_ao_termino_continua_publicavel` | APROVADO |

Total novo: **42 casos**. Os testes de integração de intervalo ficam em
`backend/tests/integration/publicacoes/`; os demais caminhos são relativos a `backend/`.

## Testes anteriores e cenários reais

Os seis arquivos selecionados na auditoria anterior foram executados novamente, com os 42 casos
novos: **128 passed, 0 failed, 0 skipped**, em 389,31s. Banco PostgreSQL próprio
`test_selecao_ret_002`; evidência: `regressao-selecionada-final.log`.

| Cobertura existente | Arquivos/casos | Evidência |
|---|---|---|
| Criar, detalhe, atos, identidade, mensagens e base conservada no POST | `tests/interface/test_retificar.py` | Seleção final aprovada |
| Devolver/cancelar e estados | `test_devolucao_da_retificacao.py`, `test_cancelamento_da_retificacao.py` | Seleção final aprovada |
| Autorização explícita | `tests/authorization/test_retificacoes.py` | Seleção final aprovada |
| Contrato HTTP | `tests/contract/test_retificacoes_api.py` | Seleção final aprovada |
| Histórico, futura, revisão obsoleta, precondições, replay, auditoria, conflito legítimo | `tests/integration/publicacoes/test_retificacoes.py` | Seleção final aprovada |
| Chrome real, datas simultâneas, portal, HTTP e SQL | E2E-01 a E2E-06 | Seis APROVADOS; `EVIDENCIAS-E2E.md` |
| Segurança HTTP real | Criar/editar/submeter/homologar/devolver/publicar sem permissão, edição válida/obsoleta, histórico e versão anônimos | 15 APROVADOS; `autorizacao-http.json` |
| Integridade SQL e hashes | Original, ato futuro, consolidações, rollback, autoria e semente | 28 APROVADOS; `integridade-verificada.json` |

## Reprodução antes da correção e ajustes de teste

`regressoes-antes.log`: **15 failed, 24 passed**; reproduziu seleção de base futura e ausência do
achado impeditivo. Os casos extras de fronteira futura/concorrência foram acrescentados depois.

`regressoes-depois.log` e `regressoes-depois-final.log` são tentativas intermediárias com erro de
nome do enum (`Severity.ERROR`, inexistente). Corrigido para `Severity.BLOCKING_ERROR` antes da
validação final. Não representam aprovação. Foram conservados para transparência.

A validação central já era usada na criação; portanto os testes que inicialmente esperavam criar
rascunho invertido foram ajustados para comprovar a recusa precoce. Isso não substituiu a prova de
publicação: um caso concorrente, preparado exclusivamente por fluxos válidos, comprovou 422 na
publicação e rollback, e há um segundo caso de conflito na fronteira futura.

## Checks e suíte completa

- `manage.py check`: aprovado.
- `manage.py migrate --check`: aprovado no banco sintético preparado.
- `ruff check` e `ruff format --check` nos cinco arquivos de código/testes alterados: aprovados.
- `git diff --check`: aprovado.
- Lint geral: E501 em `processos/models.py:30`; formatação em três modelos fora do escopo.
  `baseline-checks.json` reproduz os mesmos resultados sobre os arquivos originais de HEAD.
- `makemigrations --check --dry-run`: aponta constraints sem migrations em `processos`, `editais`
  e `comissoes`, sobre modelos comprovadamente idênticos a HEAD. Nenhuma migration foi gerada.
- Suíte completa PostgreSQL com quatro workers: registro integral em `suite-completa.log`;
  o fechamento e a classificação das falhas constam do relatório final.

Resultado amplo inicial: 12.967 aprovados, 133 falhas, 14 pulados, 55 erros (fixtures documentais
ausentes, introspecção afetada por bytecode Windows, duas expectativas intermediárias dos testes e
falhas de baseline). Rechecagem com fixtures e cache separados: 617 aprovados, 7 falhas, 12 pulados,
1 erro; caminhos Windows complementares: 1.086 aprovados, 1 falha, 2 pulados. As contagens se
sobrepõem e não representam soma de casos distintos. Os dois módulos originais de HEAD reproduzem
as seis falhas de navegação, o erro de FileResponse e a falha de migrations; o README original já
omitia 099-link-documentacao. A nova 101 foi registrada sem corrigir essa omissão preexistente.

Evidências: `rechecagem-com-fixtures.log`, `rechecagem-extra.log`, `baseline-pytest-final.log`,
`baseline-checks.json`, `baseline-readme.json`. A suíte geral não é declarada aprovada.

Últimas verificações: JavaScript no host, 154 aprovados/zero falhas; rastreabilidade/README,
7 aprovados/1 falha, somente a omissão 099-link-documentacao já demonstrada em HEAD. A linha da
nova 101 foi acrescentada no README para que o incremento não criasse outra omissão.
