# Matriz de mutabilidade — proposta para aprovação

**Status**: **aprovada em 2026-09-13**, e **emendada no mesmo dia** pelo `$speckit-analyze`, que
encontrou 18 linhas com razão técnica — o que a D-002 e a FR-299 proíbem, e o que esta feature
existe para impedir — e **duas classificações erradas**. Ver *O que a revisão mudou*, ao final.

São **123 entradas** depois da emenda.

A partir daqui esta matriz é **norma**, e não sugestão. Mudar qualquer linha é decisão nova e
escrita, sujeita à D-011 (a classificação vigente governa os atos futuros) e, na direção
retificável → não retificável, à FR-315.

As marcas ⚠️ ficam no documento de propósito: elas não significam mais "pendente", e sim "esta linha
foi uma escolha entre alternativas defensáveis" — que é o que alguém precisa saber antes de
reclassificá-la.

Esta é a resposta ao achado C2: os artefatos definiam a estrutura do contrato e mandavam o
implementador decidir o conteúdo dela. Natureza, razão e política de ausência são decisões
normativas que afetam direitos, e não cabem numa tarefa de implementação.

**Como ler**: cada linha é uma entrada do `CONTRATO`. A chave é `(coleção, caminho relativo)`.
A coluna **⚠️** marca as linhas em que a proposta é uma escolha entre alternativas defensáveis —
são as que precisam do seu julgamento, e não da sua conferência.

**Como foi medida**: enumerada de `publicacoes/application/publish_edital.py`, que é o que produz o
conteúdo canônico. **123 entradas.** É mais do que os 81–98 campos que a auditoria contou por
Edital, e a diferença não é erro: a auditoria contou ocorrências num Edital concreto; isto é a
forma, que é a união de tudo o que pode aparecer.

Uma consequência disso vale para o guardião, e está em `sections`: `content` e `source` são
**mutuamente exclusivos** — seção redigida tem o primeiro, seção gerada tem o segundo. O domínio de
uma coleção é a **união** das chaves dos seus itens, e nunca a interseção. Exigir que todo item
carregue todo campo faria o guardião falhar conforme a seção que a travessia visse primeiro.

## Naturezas

| Sigla | Natureza | Carrega razão? |
|---|---|---|
| **R** | Retificável | não |
| **N** | Não retificável | **sim**, e normativa |
| **D** | Derivado | não |
| **E** | Identidade / estrutural | não |

---

## 1. Raiz do Edital — 10 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `schemaVersion` | | **E** | Versão da forma canônica. Não é norma do certame. |
| `editalId` | | **E** | Identidade. |
| `processoId` | | **E** | Identidade do Processo. |
| `processoCode` | | **D** | Cópia do código institucional do Processo, para o documento nomeá-lo sem expor UUID. |
| `processoTitle` | | **D** | Idem. |
| `number` | ⚠️ | **N** | O número do Edital é como o certame é citado em todo lugar — outros atos, ofícios, o Diário. Trocá-lo por Retificação faria dois documentos nomearem coisas diferentes com o mesmo nome. |
| `year` | ⚠️ | **N** | Mesma razão. |
| `title` | | **R** | Já oferecido hoje em `CAMPOS_RAIZ`. |
| `description` | | **R** | Já oferecido hoje. |
| `maxInscricoesPorCandidato` | ⚠️ | **N** | Governa quantas inscrições a pessoa pôde fazer. Reduzi-lo depois de aberto o prazo invalidaria inscrição já aceita; aumentá-lo daria a quem se inscreveu depois uma chance que os primeiros não tiveram. **Alternativa defensável**: retificável apenas para mais, e apenas antes de abrir o prazo — mas isso é regra condicional, e o contrato não tem forma para ela. |

## 2. `profiles` — 17 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade. |
| `code` | | **E** | Identificador estável do Perfil dentro do Edital; a inscrição o referencia. |
| `name` | | **R** | Já oferecido. |
| `description` | | **R** | ⚠️ Não está em `CAMPOS_PERFIL` hoje. Proposta: retificável, pela mesma razão de `duties` e `compensation`, que a FR-016 já admitiu. |
| `requirements` | ⚠️ | **R** | **Canário 2.** Decide quem pode concorrer. **A unidade endereçável é a lista inteira**, e não o item: texto em lista não tem identidade estável, e "o terceiro requisito" não é endereçar — é contar. Um ato que diz "onde se lê, leia-se" precisa nomear o que substitui, e o que ele pode nomear aqui é a lista. |
| `immediateVacancies` | | **R** | **Corrigido na revisão**: a tela já o oferece hoje (`CAMPOS_PERFIL`). Classificá-lo **N** o *removeria* — regressão, e a direção que a FR-315 existe para vigiar. Com ele **R**, some também a divergência com `vacancyTable/immediateVacancies`. |
| `reserveType` | ⚠️ | **N** | A espécie do cadastro reserva define **o que o Edital ofereceu** — nenhum, limitado ou ilimitado. Quem se inscreveu decidiu concorrer sabendo se havia reserva e de que tipo; trocá-la depois não corrige um erro de redação, oferece outra coisa. O limite dentro da espécie (`reserveLimit`) é parâmetro, e esse se corrige. |
| `reserveLimit` | | **R** | **Corrigido na revisão**: a tela já o oferece hoje (`CAMPOS_PERFIL`). |
| `locality` | | **R** | Já oferecido. |
| `duties` | | **R** | Já oferecido (FR-016). |
| `workload` | | **R** | Já oferecido. |
| `compensation` | | **R** | Já oferecido. |
| `classificationInformation` | ⚠️ | **R** | **Reclassificado na revisão.** Nenhum cálculo o lê: ele é armazenado, publicado e mais nada — nem o PDF nem o portal o consomem. É texto descritivo da mesma natureza de `description`, e descreve norma que **é** retificável (o marco, o método). Se a norma se corrige e a descrição dela não, o Edital passa a dizer duas coisas. Classificado **inteiro**: a forma de dentro é do Edital, não do sistema. |
| `callInformation` | ⚠️ | **R** | **Reclassificado na revisão**, pela mesma razão — e com mais força: ele descreve a convocação, e `callForm` ao lado é **R**. |
| `generalCompetitionModalityId` | | **R** | Já oferecido (014, FR-231). |
| `vacancyReversion/kind` | | **R** | Já oferecido — `CAMPOS_DA_REVERSAO`. |
| `callForm` | ⚠️ | **R** | **É o precedente que deu origem a esta feature.** O código registra que "o primeiro Edital publicado com a forma declarada nasceria irretificável nela". Propor **R** é fechar esse precedente. |

## 3. `competitionModalities` — 13 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade; a inscrição e o quadro a referenciam. |
| `code` | | **E** | Identificador estável. |
| `name` | | **R** | Já oferecido. |
| `description` | | **R** | Já oferecido. |
| `normativeRule/id` | | **E** | Identidade. |
| `normativeRule/foundation` | | **R** | Já oferecido. |
| `normativeRule/version` | | **R** | Já oferecido. |
| `normativeRule/percentage` | | **R** | Já oferecido. |
| `normativeRule/effectiveFrom` | ⚠️ | **R** | Não oferecido hoje. Proposta: retificável, pela mesma razão do fundamento e da versão — os três descrevem a norma externa que a Modalidade cita. |
| `normativeRule/calculation` | ⚠️ | **N** | A Constituição determina que os parâmetros da cota mudam por **versionamento**, e não por correção: *"Cotas DEVEM ser definidas por Perfil e, quando necessário, versionar modalidade, fundamento, percentual, cálculo, arredondamento, distribuição e vigência"*. O cálculo da reserva é um deles. O caminho de correção existe e é outro — `normativeRule/version` e `/effectiveFrom`, ambos **R**. Corrigir o parâmetro no lugar de versionar a regra apagaria sob qual norma cada Edital anterior concorreu. |
| `normativeRule/rounding` | ⚠️ | **N** | A Constituição determina que os parâmetros da cota mudam por **versionamento**, e não por correção: *"Cotas DEVEM ser definidas por Perfil e, quando necessário, versionar modalidade, fundamento, percentual, cálculo, arredondamento, distribuição e vigência"*. O arredondamento da reserva é um deles. O caminho de correção existe e é outro — `normativeRule/version` e `/effectiveFrom`, ambos **R**. Corrigir o parâmetro no lugar de versionar a regra apagaria sob qual norma cada Edital anterior concorreu. |
| `normativeRule/distribution` | ⚠️ | **N** | A Constituição determina que os parâmetros da cota mudam por **versionamento**, e não por correção: *"Cotas DEVEM ser definidas por Perfil e, quando necessário, versionar modalidade, fundamento, percentual, cálculo, arredondamento, distribuição e vigência"*. A distribuição é um deles. O caminho de correção existe e é outro — `normativeRule/version` e `/effectiveFrom`, ambos **R**. Corrigir o parâmetro no lugar de versionar a regra apagaria sob qual norma cada Edital anterior concorreu. |
| `normativeRule/callRules` | ⚠️ | **N** | A Constituição determina que os parâmetros da cota mudam por **versionamento**, e não por correção: *"Cotas DEVEM ser definidas por Perfil e, quando necessário, versionar modalidade, fundamento, percentual, cálculo, arredondamento, distribuição e vigência"*. As regras de convocação da reserva são um deles. O caminho de correção existe e é outro — `normativeRule/version` e `/effectiveFrom`, ambos **R**. Corrigir o parâmetro no lugar de versionar a regra apagaria sob qual norma cada Edital anterior concorreu. |

## 4. `vacancyTable` — 3 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade da linha (025, FR-170). |
| `modalityId` | | **R** | Já oferecido. |
| `immediateVacancies` | | **R** | Já oferecido, e **agora coerente** com `profiles/immediateVacancies`. Que os dois existam continua sendo o achado S4 da auditoria; que tenham a mesma natureza é o que esta matriz podia resolver. |

## 5. `declaredFacts` — 4 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade. |
| `code` | | **E** | Identificador estável dentro do Perfil. |
| `label` | | **R** | Já oferecido. |
| `type` | | **N** | Razão já escrita em `retificacao.py`, e normativa: trocar o tipo reinterpretaria valor já congelado sob o tipo anterior. Mudar o tipo é remover um fato e acrescentar outro (015, FR-058). |

## 6. `classificationMilestones` — 27 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade. |
| `code` | | **E** | Identificador estável. |
| `name` | | **R** | Já oferecido. |
| `stages` | ⚠️ | **N** | Quais Etapas o marco mede é **o que o marco é**, e não um parâmetro dele. Um marco que passa a medir outras Etapas não é o mesmo marco corrigido: é outro marco, sob o mesmo nome e o mesmo código, com as pontuações já registradas valendo para uma pergunta que ninguém fez. O caminho para mudar o que se mede é declarar marco novo. |
| `operation` | ⚠️ | **N** | Como as pontuações se combinam reinterpreta **toda pontuação já registrada** sob o marco: a mesma nota passa a significar outra posição sem que ninguém a tenha reavaliado. Trocar soma por média não corrige o que foi publicado, recalcula o certame. |
| `normalization` | ⚠️ | **N** | Mesma razão de `operation`, um passo antes: a normalização é o que torna as notas comparáveis entre si. Mudá-la depois de publicada reinterpreta cada nota já lançada. |
| `rounding/scale` | | **R** | **Deixou de ser opaco na revisão.** `classificacao/domain/combinacao.py:63` lê `scale`, cobra inteiro e valida a faixa: a forma é conhecida e a máquina calcula com ela. Chamar isso de opaco era classificar por onde o dado é guardado (`JSONField`), que é razão técnica. Corrigir a escala é a correção clássica — "onde se lê 2 casas, leia-se 4". |
| `rounding/mode` | | **R** | Idem: `combinacao.py:75` cobra um entre `MEIO_PARA_CIMA`, `MEIO_PARA_PAR` e `TRUNCAR`. Lista fechada, oferecida como escolha (FR-311). **Com estes dois, metade do canário 4 original volta a ser endereçável** — parte do que a troca da D-010 havia custado. |
| `appealWindow/admits` | | **R** | **Canário 3.** |
| `appealWindow/durationDays` | | **R** | **Canário 3.** |
| `appealWindow/unit` | | **R** | **Canário 3.** Lista fechada, oferecida como escolha (FR-311). |
| `drawMethod/algorithm` | | **R** | **Canário 4.** |
| `drawMethod/source` | | **R** | **Canário 4.** |
| `drawMethod/occurrence` | | **R** | **Canário 4.** |
| `drawMethod/occurrenceAt` | | **R** | **Canário 4.** |
| `drawMethod/derivation` | | **R** | **Canário 4.** |
| `drawMethod/normalization/rule` | | **R** | **Canário 4.** |
| `drawMethod/normalization/text` | | **R** | **Canário 4.** |
| `drawMethod/substitutionRule/rule` | | **R** | **Canário 4.** |
| `drawMethod/substitutionRule/text` | | **R** | **Canário 4.** |
| `drawMethod/qualifyingStageId` | | **R** | **Canário 4.** |
| `cutRule/targetKind` | ⚠️ | **N** | A espécie do alvo diz se o corte tem número fixo ou derivado — são **duas regras diferentes**, e não dois valores da mesma. `targetCount` é o parâmetro dentro da espécie fixa, e esse se corrige. |
| `cutRule/targetCount` | | **R** | Já oferecido (014, FR-184) — "onde se lê 10, leia-se 12". |
| `cutRule/surplusCount` | | **R** | Já oferecido. |
| `cutRule/tieOutcome` | | **R** | Já oferecido. |
| `cutRule/governedStage` | ⚠️ | **N** | A razão normativa já está escrita no código, em `classificacao/domain/faixa.py:88`: trocá-la *"moveria em silêncio quem continua no certame"*. É o campo que decide quem progride, e corrigi-lo depois do corte aplicado mudaria quem passou sem reavaliar ninguém. |
| `cutRule/continuation` | ⚠️ | **N** | Mesma razão de `governedStage`, do outro lado: admitir ou não continuação decide quem segue. Mudá-la depois do corte reescreveria o resultado de um ato já praticado. |

## 7. `tiebreakers` — 6 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade (015, FR-015). |
| `order` | | **R** | Já oferecido — **a ordem é a norma**. |
| `type` | ⚠️ | **N** | O que o critério compara. |
| `parameters/stageId` | ⚠️ | **N** | **Deixou de ser opaco na revisão**: `classificacao/domain/desempate.py:37` e `application/emissao.py:244` leem `stageId` e `factId`, e `editais/domain/perfis.py` cobra que um dos dois exista. A forma é conhecida. A natureza é **N** por outra razão: o que o critério compara é **o que ele é** — trocá-lo não corrige o desempate, substitui-o por outro, e os empates já resolvidos sob o anterior ficariam resolvidos por um critério que o Edital não tem mais. |
| `parameters/factId` | ⚠️ | **N** | Idem. |
| `whenMissing` | ⚠️ | **N** | O que fazer quando o valor não existe é regra de desempate como qualquer outra, e `editais/domain/perfis.py` registra por quê ela é declarada e nunca inferida: *"o silêncio não vira zero nem último lugar"*. Mudá-la depois de empates resolvidos os resolveria de outro jeito. |

## 8. `schedule` — 9 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade; a Etapa a referencia. |
| `type` | ⚠️ | **N** | Espécie do Evento. |
| `description` | | **R** | Já oferecido. |
| `startAt` | | **R** | Já oferecido. |
| `endAt` | | **R** | Já oferecido. |
| `order` | | **E** | Posição no Cronograma. |
| `status` | | **D** | Produzido pelo sistema. Nenhum esquema declara a enumeração dele. |
| `location` | | **R** | **Canário 1.** Hoje nem forma declarada tem. |
| `isRegistrationPeriod` | ⚠️ | **N** | Qual Evento é o período de inscrições. Trocá-lo depois de publicado redefiniria retroativamente quando as inscrições estiveram abertas. |

## 9. `stages` — 13 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Já era `NAO_SAO_NORMA`. |
| `order` | | **E** | Insumo da progressão. Já era `NAO_SAO_NORMA`. |
| `scheduleEventId` | | **E** | ⚠️ Vínculo endereçado pela coleção do Cronograma. Já era `NAO_SAO_NORMA`, **sem razão escrita** — esta linha é a razão que faltava. |
| `name` | | **R** | Já oferecido. |
| `weight` | | **R** | Já oferecido. |
| `minimumScore` | | **R** | Já oferecido. |
| `maximumScore` | | **R** | Já oferecido (012). |
| `evaluationsPerRegistration` | | **R** | Já oferecido (012). |
| `eliminatory` | | **R** | Já oferecido. |
| `classificatory` | | **R** | Já oferecido. |
| `forma` | | **R** | Já oferecido. |
| `rotuloFavoravel` | | **R** | Já oferecido. |
| `rotuloDesfavoravel` | | **R** | Já oferecido. |

## 10. `sections` — 7 campos (6 por item)

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade derivada de `(edital, key)`. |
| `key` | | **E** | Chave do catálogo. |
| `title` | | **N** | As seções do Edital são um **catálogo institucional**, e não escolha deste Edital: título, ordem e espécie são os mesmos em todo Edital do Cefor, e é isso que torna um Edital legível por quem já leu outro. Corrigi-los aqui mudaria este Edital em relação aos demais. O que este Edital escreve é o `content`, e esse se corrige. |
| `order` | | **N** | Idem — é a ordem do catálogo, não deste Edital. |
| `type` | | **N** | Idem — é a espécie declarada pelo catálogo. |
| `content` | | **R** | Já oferecido. |
| `source` | | **E** | ⚠️ **Campo condicional**: só existe em seção gerada, onde `content` não existe. Declara a coleção que origina o texto. |

## 11. `attachments` — 5 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade que o Documento Exigido referencia. |
| `label` | | **R** | Já oferecido. |
| `order` | | **R** | Já oferecido — ordem editorial. |
| `artifactId` | | **R** | Já oferecido — o arquivo se troca por Retificação. |
| `artifactHash` | | **D** | Derivado dos bytes do artefato. `retificacao.py` já escreve por quê: oferecê-lo faria a tela pedir que alguém copiasse um SHA-256 à mão. |

## 12. `documentRequirements` — 9 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade. |
| `key` | | **N** | Razão já escrita e normativa: é com ela que a inscrição já submetida nomeia o arquivo enviado; trocá-la desligaria o documento do que os candidatos mandaram. |
| `name` | | **R** | Já oferecido. |
| `instructions` | | **R** | Já oferecido. |
| `required` | | **R** | Já oferecido. |
| `order` | | **R** | Já oferecido. |
| `profileId` | | **R** | Já oferecido. |
| `modalityId` | | **R** | Já oferecido. |
| `attachmentId` | | **R** | Já oferecido (020, FR-020). |

---

## Política de objeto ausente — FR-313

Cinco objetos podem estar ausentes do conteúdo. `null` não é campo sem natureza: é declaração que
não foi feita, e a pergunta é se ela pode passar a existir por Retificação.

| Objeto | ⚠️ | Proposta |
|---|---|---|
| `classificationMilestones/cutRule` | ⚠️ | Pode passar a existir. Um marco que não cortava passa a cortar por Retificação, com a regra inteira num ato só — declarar pela metade é o que a validação já recusa. |
| `classificationMilestones/appealWindow` | ⚠️ | Pode passar a existir. Declarar janela onde não havia **concede** prazo, e conceder é menos grave do que retirar. |
| `classificationMilestones/drawMethod` | ⚠️ | **Não pode.** Um marco que não declarou método não sorteia; fazê-lo sortear depois de publicado muda a espécie da ordenação, e não um parâmetro dela. |
| `profiles/vacancyReversion` | ⚠️ | Pode passar a existir — a `016` já a trata como declaração do Edital. |
| `competitionModalities/normativeRule` | ⚠️ | **Não pode.** Modalidade sem regra normativa é Modalidade sem fundamento; acrescentá-lo depois é criar reserva que o Edital publicado não tinha. |

---

## Resumo da proposta

| Natureza | Quantas |
|---|---|
| **R** — retificável | 70 |
| **N** — não retificável | 25 |
| **E** — identidade/estrutural | 24 |
| **D** — derivado | 4 |
| **Total** | **123** |

**27 linhas marcadas ⚠️**, mais as 5 de objeto ausente. A marca significa "esta linha foi escolha
entre alternativas defensáveis" — e não "pendente".

**Cruzamento com a tela**: 49 das 70 linhas **R** são campos que a Retificação já oferece hoje.
Nenhuma linha **N**, **E** ou **D** é oferecida — depois da emenda. As demais transcrevem decisão
que o código já registra com razão normativa, ou são identidade sem controvérsia.

**O padrão que a matriz revela**: o reexame da FR-310 já aconteceu, e aconteceu aqui. Toda exclusão
que se sustentava em "valor fechado", "lista de identidades" ou "UUID digitado" foi reescrita em
termos de norma — ou caiu. O saldo é **seis campos a mais retificáveis** do que a primeira proposta.

---

## O que a revisão mudou

O `$speckit-analyze` encontrou 18 linhas cuja razão era técnica, e duas classificações erradas. A
medição que resolveu quase tudo foi simples: **quem lê cada objeto?**

**Dois erros de classificação.** `profiles/immediateVacancies` e `profiles/reserveLimit` estavam
marcados **N** — e a tela **já os oferece hoje**, em `CAMPOS_PERFIL`. Classificá-los **N** os
removeria: regressão, e exatamente a direção que a FR-315 existe para vigiar. Os dois passaram a
**R**, e com isso some também a divergência com `vacancyTable/immediateVacancies`, que era um
conflito com o princípio II da Constituição.

**A regra do "objeto opaco" estava super-aplicada.** Ela juntava duas coisas opostas:

| Grupo | Quem lê | Veredicto |
|---|---|---|
| `classificationInformation`, `callInformation` | **ninguém** — nem o PDF, nem o portal, nem cálculo algum | texto descritivo → **R** |
| `normativeRule/{calculation, rounding, distribution, callRules}` | **ninguém** | mas a Constituição manda **versionar**, não corrigir → **N** com razão constitucional |
| `classificationMilestones/rounding` | `combinacao.py:63-86`, que valida `scale` e `mode` | **não é opaco**: forma conhecida → dois campos **R** |
| `tiebreakers/parameters` | `desempate.py:37`, `emissao.py:244`, `calculo.py:217` | **não é opaco**: forma conhecida → dois campos **N**, por razão de identidade |

Chamar os dois últimos de opacos era classificar **por onde o dado está guardado** — um `JSONField`
—, que é razão técnica um nível acima daquelas que a feature veio proibir.

**Um efeito colateral bem-vindo**: com `rounding/scale` e `rounding/mode` endereçáveis, **metade do
canário 4 original volta** — parte do que a troca da D-010 havia custado.

**O que continua sendo achado, e não desta spec**: `profiles/immediateVacancies` e
`vacancyTable/immediateVacancies` continuam sendo dois lugares para o mesmo número. A matriz podia
dar-lhes a mesma natureza, e deu; **não** pode resolver a duplicação. É o S4 da auditoria, e a spec
estrutural de vagas é quem o fecha.
