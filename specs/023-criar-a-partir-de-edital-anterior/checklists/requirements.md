# Specification Quality Checklist: Criar Edital a partir de Edital anterior

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-09
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs) — *com desvio deliberado: a spec cita
  módulos e arquivos existentes em §3 e nas decisões. É a convenção deste repositório (ver §1.2 e §3
  da `022`) e é o que o Princípio V cobra: rastreabilidade entre especificação e código. Nenhum
  requisito (`FR-`) nomeia arquivo; as citações ficam nas decisões e no inventário do que já existe.*
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders — *as User Stories, os Success Criteria e §1 são
  legíveis sem o código; §4 pressupõe o domínio, como nas features anteriores*
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain — nenhum foi necessário: as três ambiguidades da
  proposta de origem (qual permissão, qual fonte do conteúdo, seleção por blocos) foram fechadas em
  D-001, D-003 e D-004, com evidência no código.
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic — SC-007 nomeia *migration*, *permissão* e
  *impedimento de publicação*: são os limites de tamanho que a feature promete não cruzar, e não há
  como dizê-los sem nomeá-los.
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified — oito, incluindo os dois que a leitura ingênua perde: origem
  retificada e Seção gerada.
- [x] Scope is clearly bounded — §2 (régua de tamanho) e §6 (Out of Scope), com a razão de cada item.
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification — ver a primeira nota.

## Notes

- `backend/tests/test_citacoes_de_requisito.py` passa: as citações a `FR-011` (`020`), `FR-034` e
  `FR-036` (`006`), `FR-042` (`006`) e `FR-063` (`015`) apontam para requisitos definidos, e as
  decisões `D-001`–`D-008` estão declaradas nesta spec.
- **Rodada de correção antes do plano.** Quatro afirmações da primeira redação foram conferidas no
  código e três estavam erradas ou incompletas: (a) o vínculo com o Anexo **não** é a única
  referência que escapa da gravação — marco → Etapas enumeradas, critério → Etapa/fato e
  `drawMethod.qualifyingStageId` escapam também, e a razão é que a cópia preserva a coerência
  interna; (b) *"o que a composição grava"* não serve como lista branca, porque a gravação
  **preserva** campos que nenhuma tela desenha — daí FR-008 e FR-008a; (c) a ordem do §7 misturava
  ordem de transação com ordem de entrega, e afirmava o inverso do que a integridade exige. A quarta
  correção é de redação: o destino já existe quando a operação começa, então a idempotência protege
  contra segunda **cópia**, não contra segundo Edital.
- **Rodada de `$speckit-analyze`, com um achado CRITICAL.** A varredura cruzada encontrou uma
  cláusula da Constituição escrita para esta feature e **nunca citada por spec alguma** —
  *"Modelos reutilizáveis DEVEM ser apenas origem controlada […] estas DEVEM preservar independência
  **e versão**"*. A metade "versão" não estava atendida: o registro nomeava o Edital de origem, não a
  versão consolidada de onde o conteúdo saiu, e uma Retificação posterior na origem apagaria *de qual
  configuração se partiu*. Corrigido em `FR-015a`, `SC-005`, `D-005`, `T-008`, no contrato e em
  `T034`/`T037`. Corrigidos junto: a linha do §3 que ainda apontava `forms.py` (`*_persistidos`) como
  fonte, contra `D-003`; `FR-006`, que dizia "Seções textuais **redigidas**" quando são todas as
  textuais; o aceite da `US2`, que só cobria uma das quatro referências; o aviso, que migrou de
  `base.html` para `compor_base.html`; a palavra *proveniência*, trocada por *origem* também na
  prosa; e a árvore do plano, que omitia quatro arquivos e nomeava um que nenhuma tarefa usa.
- **Segunda rodada de análise cruzada, com dois HIGH.** (1) A ordem da idempotência estava invertida:
  a recusa por rascunho não vazio vinha antes da reserva da chave, de modo que a repetição — que só
  existe **depois** de a primeira cópia encher o rascunho — responderia `draft_not_empty`. Virou
  `FR-017a`, com a ordem do contrato refeita e a razão que `add_edital` já tinha escrito. (2) A trilha
  mostraria o identificador cru: guardar a versão resolveu o envelhecimento e criou um problema de
  leitura, e `US3` ficaria atendida no banco e não no canal do ator. Virou `FR-014a`, `T-010` e as
  tarefas `T039`/`T040`. Corrigidos junto: a linha da spec que dizia usar os comandos de Anexo; o
  data-model, que punha o `ArtefatoAnexo` no mapa de `T-005`; e os dois casos positivos que faltavam —
  origem `ENCERRADO` e versão em esquema anterior (`T031a`).
- **Terceira rodada: nada reabriu, e o defeito novo era de alcance.** `FR-014a` dizia *"não deve
  exibir identificador cru a quem a consulta"* **sem qualificar a entrada** — lido ao pé da letra,
  arrastava para esta feature a correção das entradas da `020`, que gravam `anexo <uuid>`. Qualificado
  para *esta* operação, com a nota de que uniformizar a trilha é de quem for dono dela. Junto: o §7.1
  ganhou a sequência inteira (autorizar → reservar → recusar → copiar → registrar), o bloco de código
  vazio que a rodada anterior deixou saiu, o contrato passou a dizer que **detalha** o §7.1 em vez de
  reivindicar a mesma numeração, e o caso de borda da repetição passou a dizer o que importa: ela não
  é recusada por rascunho não vazio.
- **Quarta rodada, depois da implementação: os artefatos tinham ficado para trás em quatro pontos.**
  Nenhum defeito de código; deriva de rastreabilidade, que é o que o Princípio V não admite deixar.
  (1) `FR-006` e `T-002` falavam só dos três instantes, e a implementação converte também os três
  decimais da Etapa — `validate_stage` compara `peso <= 0` e `str` contra `int` levanta `TypeError`.
  (2) O contrato descrevia a afordância sem separar **exibir** de **enviar**, que é exatamente a
  regra cuja ausência produziu dois defeitos de 404 no reenvio. (3) `FR-014a` exigia forma legível,
  mas não que a versão fosse **distinguível** — e uma Retificação rematerializa uma versão por
  fronteira temporal, de modo que a data não separa duas. (4) `quickstart` e contrato citavam a
  redação antiga do aviso.
- Pendência de processo, e não de qualidade: `$speckit-plan` e `$speckit-tasks` ainda não rodaram, e
  `$speckit-analyze` exige os três artefatos.
