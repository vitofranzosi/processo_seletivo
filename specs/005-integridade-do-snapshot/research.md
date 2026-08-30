# Research: Integridade do Snapshot Normativo

**Feature**: `005-integridade-do-snapshot` | **Fase**: 0 | **Data**: 2026-08-29

Nenhuma questão ficou em aberto no Technical Context — as três da revisão foram resolvidas em
`$speckit-clarify`. O que fica aqui são as alternativas de **desenho** avaliadas, e por que cada uma
foi ou não escolhida.

## R1 — De onde vem a forma que se exige

**Decisão**: o contrato ganha `PerfilPublicado` e `EventoPublicado` — esquemas de **saída**, com os
campos canônicos. O domínio transcreve e um teste confere a transcrição contra o contrato.

**Rationale**: o contrato é a autoridade, e a spec o nomeia. Mas o domínio não pode consultá-lo em
execução: o arquivo vive em `specs/`, é artefato de processo e não é distribuído com o pacote. A
declaração verificada é o mesmo arranjo que a `004` adotou para as coleções com chave, e pelo mesmo
motivo — o que é declarado e conferido falha alto quando diverge; o que é inferido falha calado.

**Por que não bastavam os esquemas de entrada**, que era o desenho anterior: `PerfilInput` exige 5
dos 12 campos do Perfil publicado. Um Perfil reduzido a esses cinco passaria, e é exatamente o Perfil
mutilado que a feature existe para impedir — `requirements`, medido como defeito, entre os ausentes.

| Alternativa | Por que não |
| --- | --- |
| Ler o `openapi.yaml` em tempo de execução | Inverte a relação entre domínio e especificação, e transforma um arquivo de documentação em dependência de produção. O pacote instalado não o contém. |
| Derivar a forma dos modelos Django | O snapshot é conteúdo canônico publicado, não espelho do ORM. Um campo pode existir num e não no outro, e a `004` já registrou essa diferença. |
| Derivar da forma que `edital_snapshot` produz, sem declarar no contrato | Descreve presença e não tipo, nulabilidade ou restrição, e deixa a autoridade num detalhe de implementação. Declarar no contrato o que ele produz é o mesmo alcance com autoridade no lugar certo. |
| Usar `PerfilInput` e `EventoInput` como autoridade | Era o desenho da primeira versão deste plano. Descrevem entrada, exigem 5 dos 12 campos, e deixariam `requirements` sem verificação. |
| Usar `jsonschema` no domínio | É dependência de **desenvolvimento**, usada pelos testes de conformidade. Promovê-la a dependência de produção para verificar cinco dimensões em duas entidades é custo maior que o próprio código. |

## R2 — O que se verifica, e o que o contrato declara e fica de fora

**Decisão**: presença, tipo, nulabilidade, formato **e as restrições que o contrato já escreve** —
faixa e enumeração. Coerência entre campos fica de fora.

**Rationale**: a linha é entre **aplicar** e **inventar**. `minimum: 0` e `enum: [NONE, LIMITED,
UNLIMITED]` já estão escritos; não aplicá-los exigiria uma garantia nova para preservar
comportamento inválido — um teste que obrigasse `immediateVacancies: -3` a continuar publicável.
Congelar defeito não é o mesmo que evitar overengineering.

Coerência entre campos é outra coisa: `reserveLimit` compatível com o tipo de reserva e `endAt`
posterior a `startAt` não estão escritos em lugar nenhum, e escrevê-los aqui seria decidir por
antecipação.

| Alternativa | Por que não |
| --- | --- |
| Deixar faixa e enumeração de fora | Era o desenho da primeira versão, e a revisão o desmontou: transforma limitação atual em comportamento obrigatório, com teste e tudo. |
| Verificar também coerência entre campos | Nenhuma dessas regras existe escrita; inventá-las aqui decide normativamente o que um Edital admissível é. |
| Verificar só presença | Era o escopo original, e a avaliação da spec o mediu insuficiente: `name = []`, `immediateVacancies = "muitas"` e `startAt = {}` atravessam sem achado impeditivo. |

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

**Decisão**: `blocking_findings`, `422` — o código que o sistema já emite para erro impeditivo de
publicação, em nove pontos.

**Rationale**: a natureza da recusa não mudou; mudaram o momento e o alcance. Um código novo diria a
mesma coisa com outro nome.

**Achado ao conferir**: o `openapi.yaml` **não nomeia** `blocking_findings`. Ele nomeia
`expected_hash_mismatch`, `target_already_present`, `inconsistent_consolidation` e os três da `004`,
e deixou de fora o mais antigo. Esta feature o declara, porque passa a produzi-lo num momento novo.

| Alternativa | Por que não |
| --- | --- |
| Código próprio, por exemplo `malformed_snapshot` | Distinguiria por implementação, e não por natureza: continua sendo erro impeditivo de publicação. |
| Reutilizar `invalid_change` | Descreve a alteração, e a recusa aqui é sobre o resultado — inclusive quando nenhuma alteração isolada é inválida. |

## R6 — O que acontece com a tela de composição

**Decisão**: nada, e a suíte existente responde.

**Rationale**: a tela lista pendências com a mesma `validate_for_publication` e mapeia o caminho do
achado para a etapa onde se corrige. Caminho desconhecido cai em "não corrigível". Os achados novos
não devem aparecer lá, porque o snapshot de um Edital em composição é montado do ORM e sempre traz
as entidades completas.

**Consequência**: a suíte de interface já cobre a lista de pendências. Se ela acusar mudança, aí sim
há regressão a entender e um teste a escrever. Criar um teste novo antes de a suíte dizer alguma
coisa seria proteger um pressuposto que ninguém contestou.
