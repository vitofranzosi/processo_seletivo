# Contrato — o que a publicação passa a recusar, avisar e esconder

**Feature**: `046` · **Spec**: [../spec.md](../spec.md) · **Pesquisa**: [../research.md](../research.md)

Este contrato fixa **códigos, severidades, atos, caminhos e o esqueleto das frases**. A redação final
de cada frase é da implementação, desde que cada uma diga as quatro coisas da `FR-749` / `FR-752`
(`SC-280`): a entidade, o que falta, por que isso impede a execução, onde se corrige.

## 1. Os achados novos

| Código | Severidade | Ato | Quando | Caminho |
|---|---|---|---|---|
| `stage_result_unreachable` | impeditivo | publicação | a regra da consolidação recusa a Etapa **e** o fluxo exige o Resultado dela (`FR-746`) | `/stages/id=<etapa>` |
| `stage_without_result` | aviso | publicação | a regra recusa a Etapa **e** nada exige o Resultado (`FR-748`) | `/stages/id=<etapa>` |
| `stage_without_result` | advertência | Retificação | a regra recusa a Etapa, exigida ou não (`FR-751`) | `/stages/id=<etapa>` |
| `profile_without_cut_rule` | impeditivo | publicação | Perfil com marco, e nenhum marco dele declara `cutRule` (`FR-752`) | `/profiles/id=<perfil>/classificationMilestones` |

**Dois códigos para a Etapa, e não um com duas severidades.** Num mesmo ato, nenhum código é
impeditivo e aviso ao mesmo tempo — é o invariante que
`tests/unit/editais/test_invariantes_da_declaracao_unica.py` já prende —, e é o que faz a advertência
da Retificação sobreviver à subtração de `advertencias_do_ato` sem mexer nela (`R-3`).

**Destino no assistente**: os caminhos acima já são resolvidos por `_destino` — `/stages/…` leva à
etapa *Etapas*; `/profiles/…/classificationMilestones` leva à *Classificação*. Nenhuma entrada nova
em `DESTINO_DA_PENDENCIA` nem em `DESTINO_POR_CODIGO`.

### Quem exige o Resultado (`D-001`)

Uma Etapa tem o Resultado **exigido** quando qualquer uma destas é verdadeira:

| Consumidor | Declaração lida | Consequência que a frase nomeia |
|---|---|---|
| caráter eliminatório | `stages[].eliminatory` | ninguém é eliminado por ela, e o Edital segue sem o critério que publicou |
| marco que a enumera | `classificationMilestones[].stages` | ninguém é posicionado pelo marco `<código>` |
| corte que a governa | `faixa.etapa_governada(cutRule)` | ninguém é convocado pelo corte do marco `<código>` |
| Etapa de habilitação do sorteio | `marcos.metodo_que_governa(...).qualifyingStageId` | ninguém entra na relação do sorteio do marco `<código>` |

Mais de um consumidor: a frase nomeia o primeiro na ordem da tabela; os demais não mudam a correção.

### Esqueleto das frases

```text
stage_result_unreachable
  A Etapa '<nome>' não terá Resultado: <frase de impedimento_da_regra>.
  <consequência do consumidor>. Corrija-a na etapa Etapas<, ou retire-a do marco <código> na etapa
  Classificação>.

stage_without_result
  A Etapa '<nome>' não terá Resultado: <frase de impedimento_da_regra>. Nada neste Edital depende
  dele, e por isso a publicação não é impedida.

profile_without_cut_rule
  Nenhum marco do Perfil '<code ou nome>' declara regra de corte: sem corte não há faixa, e a
  convocação não alcança ninguém deste Perfil. Declare a regra em ao menos um marco, na etapa
  Classificação.
```

A `<frase de impedimento_da_regra>` é o segundo elemento que a função devolve, **sem reescrita**
(`FR-747`). O rótulo do Perfil segue a convenção de `_perfil_sem_marco`: `code` antes de `name`.

## 2. O que deixa de aparecer

| Onde | Antes | Depois |
|---|---|---|
| `milestone_without_cut_rule` (`032`, `FR-461`) num Perfil **sem** corte algum | um aviso por marco | nenhum — a recusa `profile_without_cut_rule` é o relato (`FR-753`) |
| `milestone_without_cut_rule` num Perfil em que outro marco corta | aviso | aviso, sem mudança |
| Seção *"Validação do conteúdo"* na tela do Edital, e pendências do assistente, com Edital `PUBLICADO`, `ENCERRADO` ou `CANCELADO` | todos os achados do ato de publicação sobre o relacional | **só** os códigos da lista de fatos do conteúdo publicado — hoje `stage_without_schedule_event` (`045`, `FR-739`), como *"Aviso"*; nenhum impeditivo (`FR-755`) |
| Previsão de recusa dos atos em Edital publicado | calculada e nunca usada | não calculada |

Nada muda para `EM_ELABORACAO`, `EM_REVISAO` e `HOMOLOGADO`.

## 3. Quem consulta a validação de publicabilidade (`FR-756`)

A lista é fechada, e uma varredura a prende:

| Chamador | Ato | Para quê |
|---|---|---|
| `publicacoes/application/publish_edital.py` (`submit_edital`, `publish_edital`) | publicação | recusar o ato |
| `publicacoes/application/retificacoes.py` (`_assert_well_formed`, `advertencias_do_ato`) | Retificação (e publicação, só para subtrair) | recusar o ato; advertir na confirmação |
| `interface/views.py` (`_pendencias`) | publicação | antecipar, **só antes da publicação** |

## 4. A fonte de demonstração

| Ambiente | Vocabulário de fontes | Configuração |
|---|---|---|
| produção (`config.settings.production`) | `Loteria Federal` | `SORTEIO_FONTE_DE_DEMONSTRACAO` verdadeira **recusa o boot** (`FR-758`) |
| desenvolvimento (`config.settings.development`) | `Loteria Federal`, `Fonte de demonstração` | ligada pelo módulo, sem variável |
| testes (`config.settings.test`) | `Loteria Federal`, `Fonte de demonstração` | ligada pelo módulo, sem variável |

A recusa, quando a fonte não pertence ao vocabulário, é a que já existe — `draw_source_not_supported`
na execução, e a mensagem de `editais/domain/perfis.py:536-541` na validação —, com a lista das
fontes **daquele ambiente**. Nenhuma frase nova.
