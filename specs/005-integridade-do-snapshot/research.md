# Research: Integridade do Snapshot Normativo

**Feature**: `005-integridade-do-snapshot` | **Fase**: 0 | **Data**: 2026-08-29

Nenhuma questão ficou em aberto no Technical Context — as três da revisão foram resolvidas em
`$speckit-clarify`. O que fica aqui são as alternativas de **desenho** avaliadas, e por que cada uma
foi ou não escolhida.

## R1 — De onde vem a forma que se exige

**Decisão**: declarada no domínio, transcrevendo `PerfilInput` e `EventoInput` do `openapi.yaml` da
`001`, e verificada por teste contra ele.

**Rationale**: o contrato é a autoridade, e a spec o nomeia. Mas o domínio não pode consultá-lo em
execução: o arquivo vive em `specs/`, é artefato de processo e não é distribuído com o pacote. A
declaração verificada é o mesmo arranjo que a `004` adotou para as coleções com chave, e pelo mesmo
motivo — o que é declarado e conferido falha alto quando diverge; o que é inferido falha calado.

| Alternativa | Por que não |
| --- | --- |
| Ler o `openapi.yaml` em tempo de execução | Inverte a relação entre domínio e especificação, e transforma um arquivo de documentação em dependência de produção. O pacote instalado não o contém. |
| Derivar a forma dos modelos Django | O snapshot é conteúdo canônico publicado, não espelho do ORM. Um campo pode existir num e não no outro, e a `004` já registrou essa diferença. |
| Derivar da forma que `edital_snapshot` produz | Era a redação original de FR-005, e a revisão a apontou como insuficiente: descreve presença, não tipo nem nulabilidade, e inclui campos que o contrato não exige. |
| Usar `jsonschema` no domínio | É dependência de **desenvolvimento**, usada pelos testes de conformidade. Promovê-la a dependência de produção para verificar quatro dimensões em duas entidades é custo maior que o próprio código. |

## R2 — O que se verifica, e o que o contrato declara e fica de fora

**Decisão**: presença de campo obrigatório, tipo JSON, nulabilidade e formato. `minimum` e `enum`
ficam de fora.

**Rationale**: FR-009. O contrato declara `minimum: 0` para vagas e `enum: [NONE, LIMITED,
UNLIMITED]` para o tipo de reserva; são regras de negócio, e decidir se um Perfil pode ter vagas
negativas é discussão normativa que esta feature não abre.

**Consequência aceita e registrada**: depois desta feature, `immediateVacancies: -3` continua
publicável. Está dito no contrato da feature para que ninguém leia a garantia como maior do que é.

| Alternativa | Por que não |
| --- | --- |
| Verificar o contrato inteiro | Excede o escopo acordado e mistura "tem forma de Edital" com "é um Edital admissível", que são duas perguntas com donos diferentes. |
| Verificar só presença | Era o escopo original, e a revisão o mediu insuficiente: `name = []`, `immediateVacancies = "muitas"` e `startAt = {}` atravessam a validação atual sem achado impeditivo. |

## R3 — Onde a verificação é chamada na Publicação

**Decisão**: em lugar nenhum novo. `_materialize_affected_versions` já chama a verificação
estrutural uma vez por fronteira de vigência, dentro do laço, antes de materializar cada versão.

**Rationale**: a exigência de FR-003 — cada fronteira, e não só a primeira — já está estruturalmente
satisfeita. O que falta é profundidade na verificação chamada ali, e testes que provem o
comportamento por fronteira, que hoje não existem.

**Consequência não óbvia**: a maior parte do risco desta feature está em **não** construir coisa
nova. Um segundo laço, paralelo ao que já existe, seria a duplicação que o princípio V manda evitar
— e divergiria do primeiro na primeira mudança.

| Alternativa | Por que não |
| --- | --- |
| Um passo de verificação próprio, antes da materialização | Duplicaria o percurso das fronteiras e criaria duas respostas possíveis para a mesma pergunta. |
| Verificar só o conteúdo que passa a vigorar de imediato | É a leitura que o singular de FR-003 permitia, e a revisão a apontou: a fronteira seguinte vigoraria malformada semanas depois, sem ninguém publicar nada naquele dia. |

## R4 — Como o portão da Publicação é demonstrado

**Decisão**: com o ato malformado **já homologado, gravado diretamente**.

**Rationale**: a recusa na elaboração torna o caminho normal inalcançável — foi o segundo achado da
revisão. O padrão já existe na `003`, no teste da precondição ausente: a linha restaurada de backup
ou criada por importação, que nunca passou pela borda. É também a razão de o portão não ser
redundante, e virou requisito próprio (FR-013).

| Alternativa | Por que não |
| --- | --- |
| Montar duas Retificações cujo consolidado é malformado | Mais fiel ao mundo real, mas depende de tal composição existir: a precondição por hash e a guarda de identidade da `004` já recusam quase tudo que chegaria ali. Construir o teste sobre um cenário que talvez não exista é apostar. |
| Abandonar o portão e confiar só na elaboração | Deixa sem defesa toda linha que chegue por fora da borda, que é exatamente o que a `003` aprendeu a não fazer. |

## R5 — Que código de erro a recusa usa

**Decisão**: `blocking_findings`, `422` — o que o contrato já declara para a Publicação.

**Rationale**: a natureza da recusa não mudou; mudaram o momento e o alcance. Um código novo diria a
mesma coisa com outro nome, e o contrato ganharia superfície sem ganhar informação.

| Alternativa | Por que não |
| --- | --- |
| Código próprio, por exemplo `malformed_snapshot` | Distinguiria por implementação, e não por natureza: continua sendo erro impeditivo de publicação. |
| Reutilizar `invalid_change` | Descreve a alteração, e a recusa aqui é sobre o resultado — inclusive quando nenhuma alteração isolada é inválida. |

## R6 — O que acontece com a tela de composição

**Decisão**: nada, e há um pressuposto a proteger.

**Rationale**: a tela lista pendências com a mesma `validate_for_publication` e mapeia o caminho do
achado para a etapa onde se corrige. Caminho desconhecido cai em "não corrigível". Os achados novos
não devem aparecer lá, porque o snapshot de um Edital em composição é montado do ORM e sempre traz
as entidades completas.

**Consequência**: isso é pressuposto, não garantia, e vira teste. Se um dia deixar de valer, a tela
passaria a exibir pendências que ninguém consegue resolver por ela — falha silenciosa de
usabilidade, que é a espécie que este projeto vem aprendendo a transformar em falha de suíte.
