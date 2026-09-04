# Rastreabilidade: revisão de compatibilidade 012–013

**Fechada em 04/09/2026**, ao final da implementação. Liga cada requisito da revisão à tarefa que o
entregou e ao teste que o demonstra — e enumera, uma a uma, as asserções que precisaram mudar.

## 1. A não regressão, medida

FR-124 (012) e FR-050 (013) cobram **identidade de teste**, e não contagem. O baseline foi coletado
antes de T001 e comparado ao final:

```text
baseline   2750 testes coletados
final      2819 testes coletados
sumiram       0
```

**Nenhum teste que existia deixou de existir.** A contagem cresce porque a revisão acrescentou 69
testes — exigir que ela não crescesse seria exigir que a revisão não fosse testada.

### As asserções que mudaram, e por quê

Só duas naturezas são admissíveis: o literal da versão canônica e a forma do conteúdo publicado.
Nenhuma alteração abaixo é comportamento da forma pontuada.

| arquivo | o que mudou | natureza |
|---|---|---|
| `tests/contract/test_forma_publicada.py` | `SCHEMA_VERSION == 5` → `== 6` | literal da versão |
| `tests/integration/editais/test_contrato_de_inscricao.py` | `schemaVersion == 5` → `== 6` | literal da versão |
| `tests/unit/avaliacoes/test_elevacao.py` | as fixtures de "já declarou" ganham as chaves da v6 | forma do conteúdo |
| `tests/integration/publicacoes/test_elevacao_de_versao.py` | a grafia elevada passa a vir de `elevar_etapa`, e não de cópia literal — a cópia já ficara desatualizada uma vez | forma do conteúdo |
| `tests/fixtures/legado.py` | `PROPRIEDADES_DO_INCREMENTO` derivada de `DEGRAUS` | forma do conteúdo |
| `tests/unit/resultados/test_regra.py` | `consequencia(etapa, decimal)` → `consequencia(etapa, conclusão)` | assinatura; **nenhum desfecho asseverado mudou** |
| `tests/migrations/test_migrations.py` | `TRIGGERS` agrupadas por app, e a asserção do upgrade de `publicacoes` escopada às dela | o teste voltava um app e cobrava as triggers de todos |
| seis fixtures que criavam avaliação concluída fora da aplicação | passam a declarar `forma` | é o que a linha precisa ter para existir |

## 2. Requisitos → tarefas → testes

### SPEC 012

| Requisito | Tarefas | Onde se demonstra |
|---|---|---|
| **FR-116** conclusão completa por forma | T015, T016 | `test_constraints.py` — quatro `INSERT` crus nas duas tabelas |
| **FR-117** a forma gravada é a da versão validada | T015, T037 | `test_versao_da_avaliacao.py::test_a_forma_gravada_e_a_da_versao_validada` |
| **FR-118** sentido no domínio, rótulo na tela | T001–T003, T036, T039 | `test_previsao.py`, `test_avaliacao.py::test_o_rotulo_publicado_no_lugar_do_enum_e_recusado` |
| **FR-119** a Etapa publica forma e rótulos | T004–T011, T023–T030 | `test_compor.py`, `test_etapas.py`, `openapi.yaml` conferido por `test_forma_publicada.py` |
| **FR-120** ausência lida como pontuada | T002, T012–T014 | `test_previsao.py`, `test_elevacao.py`, `test_elevacao_de_versao.py::test_9` |
| **FR-121** nota não se aplica à forma decisória | T006, T030 | `test_etapas.py::test_a_decisoria_com_nota_e_recusada` |
| **FR-122** um instrumento, e a recusa do outro | T037, T039, T044 | `test_mesa.py::test_o_post_com_o_campo_da_outra_forma_e_recusado_no_canal_real` |
| **FR-123** desfavorável exige parecer | T036, T043 | `test_avaliacao.py::test_concluir_desfavoravel_sem_parecer_e_recusado` |
| **FR-124** não regressão | T061 | §1 acima |
| **SC-032 a SC-039** | T027–T046 | ver a linha do FR correspondente |
| **EC-021** retificar a forma depois de conclusões | T034, T056 | `test_compatibilidade.py::test_a_troca_de_forma_cria_incompatibilidade` |
| **EC-022** forma muda entre a montagem e o envio | T037 | herda a recusa de FR-073, exercitada em `test_versao_da_avaliacao.py` |

### SPEC 013

| Requisito | Tarefas | Onde se demonstra |
|---|---|---|
| **FR-046** sentido vira consequência na Etapa eliminatória | T049, T057 | `test_regra.py::test_o_sentido_vira_consequencia_na_etapa_eliminatoria`, `test_resultado_da_etapa.py` |
| **FR-047** decisória não eliminatória é impedida | T058, T060 | `test_regra.py`, `test_prontidao.py`, `test_quickstart.py::test_j4_...` |
| **FR-048** nota mínima ausente só impede na forma pontuada | T019, T020 | `test_regra.py::test_decisoria_eliminatoria_sem_nota_minima_nao_cai_em_regra_insuficiente` |
| **FR-049** o Resultado registra a forma, e a conferência compara os três | T017, T018, T051, T054 | `test_imutabilidade_do_resultado.py::test_a_trigger_recusa_resultado_com_sentido_diferente_do_da_fonte` |
| **FR-050** não regressão | T061 | §1 acima |
| **SC-012 a SC-015** | T049–T060 | ver a linha do FR correspondente |

## 3. O que a implementação corrigiu do plano

Quatro decisões do `research.md` não sobreviveram ao código, e as quatro estão registradas nos
comentários do que ficou:

1. **`null` em campo de texto.** O projeto não o usa, e a mesma constraint já comparava
   `~Q(concluida_por="")`. Vazio passou a ser a ausência de forma e de sentido.
2. **O `DROP TRIGGER` em torno do backfill era desnecessário.** O preenchimento da conclusão
   preservada vem do `DEFAULT` do `ADD COLUMN`, que é DDL e não dispara trigger de linha, com
   `preserve_default=False` removendo o default em seguida.
3. **A aplicabilidade por forma tem três estados, e não dois.** Nota é proibida na decisória e
   apenas **admitida** na pontuada — tratá-la como exigida recusaria Edital que o sistema publica
   desde a 012.
4. **A escrita da forma na conclusão subiu para a Foundational.** A constraint e o código que a
   satisfaz precisam entrar no mesmo commit, senão o repositório fica quebrado entre as fatias.

E dois defeitos foram encontrados escrevendo, ambos silenciosos:

- a fixture de conteúdo legado rebaixava só as chaves da v5, deixando `forma` num conteúdo
  carimbado como v4 — uma grafia que nunca existiu;
- `ck_resultado_completo_por_forma` é inalcançável pelo caminho comum, porque a trigger
  `BEFORE INSERT` chega primeiro. Ela permanece como defesa em profundidade, e o teste diz isso.


## 4. O que a revisão do PR encontrou, e que a suíte verde não cobria

Três bloqueadores e dois menores, todos reais, todos corrigidos antes do merge. Ficam registrados
porque o padrão que os une é instrutivo: **os três P1 eram invisíveis para uma suíte que só
exercitava o caminho feliz da forma nova.**

| achado | o que estava errado | o que passou a existir |
|---|---|---|
| **P1 · a conclusão histórica lida pela norma vigente** | a Mesa renderizava conclusão concluída pela forma **vigente**, e as duas telas históricas só mostravam pontuação. Uma decisória preservada aparecia como traço; depois de uma Retificação de forma, uma pontuada apareceria como favorável | `conclusao_exibivel` lê a forma **da conclusão** e os rótulos da versão que a governou; os dois seletores resolvem o conteúdo histórico uma vez por versão distinta |
| **P1 · o banco aceitava qualquer sentido** | as três constraints só exigiam `~Q(sentido="")`. `TextChoices` não cria constraint, e `_consequencia_decisoria` trata tudo que não é `DESFAVORAVEL` como favorável: uma inscrição sairia **habilitada** por um valor inventado | `sentido__in=Sentido.values` nas três, com migration própria e `INSERT` cru de prova. Era o padrão que `ck_resultado_consequencia` já estabelecia, e não seguido |
| **P1 · a reversão falharia com dado decisório** | reverter restaura a constraint que exige nota e devolve `pontuacao` a `NOT NULL`; qualquer linha decisória a derruba, com um erro de coluna nula que não explica nada | guarda que recusa a reversão nomeando o ato administrativo que precisa vir antes, e teste que a exercita **com dado** — o anterior só verificava que havia caminho declarado |
| **P2 · o cabeçalho dizia "Pontuação"** | sobre uma célula que trazia "Deferido" | "Conclusão" |
| **P2 · artefatos descrevendo o desenho abandonado** | `data-model.md` e `research.md` ainda falavam em `NULL` e `DROP TRIGGER`; T007 estava marcado sem o teste correspondente | artefatos alinhados ao que existe, e os limites de borda dos três campos escritos |
