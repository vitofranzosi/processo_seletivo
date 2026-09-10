# Pesquisa — Criar Edital a partir de Edital anterior

Fase 0 da [plan.md](./plan.md). Cada questão foi fechada contra o código, não contra a memória; onde
há citação de arquivo, ela foi lida.

---

## T-001 — De onde sai o conteúdo da origem

**Decisão.** `effective_version(edital_id=<origem>).content`, passado por `elevar()`.

**Racional.** É o idioma que o repositório já usa para ler conteúdo publicado — `classificacao`,
`interface` e `supervisao` chamam o mesmo seletor, e `retificacoes.py` faz exatamente
`elevar(versao.content)`. A `VersaoConsolidada` nasce tanto na publicação inicial quanto em cada
Retificação, de modo que **todo Edital publicado tem versão vigente**: não há caso de origem
elegível sem conteúdo a ler.

**Alternativas consideradas.**

- *O estado relacional da origem* — recusado em `D-003`, e vale repetir o motivo aqui porque ele é a
  descoberta que mais muda a implementação: a Retificação não reescreve `PerfilVaga`,
  `EventoCronograma` e companhia. O único escritor dessas tabelas é `replace_draft`. Copiar dali
  reproduziria a configuração **do dia da publicação**, silenciosamente desatualizada justamente nos
  campos que mais se retificam.
- *`Publicacao.content` da primeira publicação* — mesmo defeito, declarado: ignora toda Retificação.

---

## T-002 — Três instantes viajam como texto, e a validação estoura neles

**Decisão.** Converter para `datetime` com offset, antes de chamar `replace_draft`, exatamente três
campos: `schedule[].startAt`, `schedule[].endAt` e `profiles[].competitionModalities[].normativeRule.effectiveFrom`.

**Racional.** O conteúdo canônico grava instantes com `.isoformat()`
(`publicacoes/application/publish_edital.py`), enquanto o caminho da tela entrega objetos `datetime`
— o formulário os constrói, e a API os converte por `serializers.DateTimeField`. `validate_event`
faz `timezone.is_aware(start)` (`editais/domain/cronograma.py`), que **levanta `AttributeError` em
`str`**: não é uma recusa de domínio bem formada, é um estouro. A conversão, portanto, não é
polimento — é condição de funcionamento, e é a primeira coisa que um teste deve prender.

**Alternativas consideradas.**

- *Ensinar `validate_event` a aceitar texto* — alargaria o contrato de um validador de domínio para
  acomodar uma chamadora. A forma que o comando aceita já está declarada nos serializers; quem
  chega de outro formato converte na entrada.

---

## T-003 — Os Anexos não passam pelos comandos de Anexo

**Decisão.** A cópia cria `ArtefatoAnexo` e `AnexoEdital` **diretamente**, dentro da sua própria
transação, reusando as regras do módulo (`congelado_em` nulo, `document_hash`, `tamanho`,
`content_type`, ordem por Edital) e não os comandos `anexar`/`substituir`.

**Racional.** Cada comando de Anexo abre `command_context`, faz `compare_and_swap` sobre a revisão do
Edital e grava um evento próprio (`editais/application/anexos.py`). Chamá-los `N` vezes produziria
`N` saltos de revisão e `N` registros para **uma** operação, e obrigaria a cópia a acompanhar a
revisão a cada passo. A operação é uma; o registro é um (`FR-015`).

Os bytes vêm de um artefato **congelado** da origem — publicado, imutável por trigger — e o destino
recebe artefato próprio em rascunho, substituível (`D-007`). Resumo criptográfico repetido é
legítimo por decisão já tomada (`020`, FR-011).

**Alternativas consideradas.**

- *Compartilhar o artefato congelado* — recusado em `D-007`: `congelado_em` responde ciclo de vida, e
  o rascunho do destino não poderia substituir o próprio anexo.
- *Chamar os comandos e aceitar o ruído* — deixaria a trilha afirmando `N` atos onde houve um, e a
  atomicidade dependeria de `N` transações aninhadas darem certo em sequência.

---

## T-004 — A escrita reusa `replace_draft` inteiro, e paga um segundo registro

**Decisão.** A cópia chama `replace_draft` como qualquer outra gravação, aninhada na transação da
operação. A trilha fica com **dois** registros: o `ALTERAR_RASCUNHO` do comando e o registro de
origem desta feature.

**Racional.** `replace_draft` é onde moram `validate_profiles`, `validate_schedule`,
`validate_stages`, `validate_document_requirements`, `_validar_secoes` e a recusa de identidade de
outro contêiner. Reproduzir esse caminho seria abrir uma segunda porta para as mesmas invariantes —
o defeito que este repositório mais evita, e que a `003` já pagou uma vez.

**O `area` da gravação recebe um rótulo que não é nome de etapa.** `replace_draft` grava
`reason=area` para dizer **qual área mudou** (`006`, FR-042); passar vazio devolveria o registro
indistinguível que aquela decisão veio corrigir, e passar o nome de uma etapa afirmaria que alguém a
compôs. O rótulo diz o que aconteceu: reaproveitamento, com a origem.

**Alternativas consideradas.**

- *Extrair um núcleo interno de `replace_draft` para evitar o segundo registro* — refatorar o comando
  mais sensível do sistema por cosmética de trilha. Dois registros honestos custam menos que um
  caminho novo.

---

## T-005 — O mapa de identidades, e por que ele precisa de teste próprio

**Decisão.** Uma substituição uniforme sobre o payload: monta-se o mapa `identidade da origem →
identidade nova` percorrendo tudo o que **é** identidade, e reescreve-se tudo o que **referencia**
identidade. As chaves são estas, e a lista é fechada:

```text
são identidade          profiles[].id
                        profiles[].competitionModalities[].id
                        profiles[].competitionModalities[].normativeRule.id
                        profiles[].declaredFacts[].id
                        profiles[].classificationMilestones[].id
                        profiles[].classificationMilestones[].tiebreakers[].id
                        schedule[].id
                        stages[].id
                        documentRequirements[].id
                        attachments[].id          (criadas fora do payload, ver T-003)

referenciam identidade  stages[].scheduleEventId
                        documentRequirements[].profileId
                        documentRequirements[].modalityId
                        documentRequirements[].attachmentId
                        classificationMilestones[].stages[]                (lista de Etapas)
                        classificationMilestones[].tiebreakers[].parameters.stageId
                        classificationMilestones[].tiebreakers[].parameters.factId
                        classificationMilestones[].drawMethod.qualifyingStageId

não entram no mapa      sections[].id   — recalculada por `identidade(edital.id, key)` dentro do
                                          próprio `replace_draft`
```

**Racional, e é o achado que governa o teste.** A cópia **preserva a coerência interna**. Um
identificador da origem que escape do mapa continua consistente com os seus vizinhos, e por isso
atravessa a gravação sem recusa:

- `validate_profiles` confere o marco *"enxergando só o Perfil"* — o `qualifyingStageId` é conferido
  contra as `stages` que o **próprio marco** enumera, e as duas vieram juntas da origem;
- `validate_document_requirements` confere `profileId` e `modalityId` contra os Perfis **desta
  gravação**, que também vieram juntos;
- `attachmentId` não é conferido na gravação — só na publicação, como referência pendurada.

O que a gravação de fato recusa é identidade de **outro contêiner** já existente no banco
(`_reject_identifiers_of_other_editais`) — e um id da origem cai justamente nesse caso para Perfil,
Evento e Etapa, que são os três que ela cobre. Sobram descobertas para a publicação, ou para nunca:
Anexo, `stages` do marco, critério → Etapa/fato e `qualifyingStageId`. **Cada uma ganha teste
próprio, partindo de uma origem que a usa** (`FR-010a`, `SC-003`).

**Alternativas consideradas.**

- *Remapear entidade por entidade, com uma função por coleção* — mais código para o mesmo efeito, e
  cada coleção nova seria uma função a lembrar. A substituição uniforme falha alto quando aparece
  chave nova: um identificador não mapeado é detectável.
- *Confiar nas validações existentes* — a lista acima mostra por quê não.

---

## T-006 — Seções: só as textuais

**Decisão.** Filtrar `sections` pelas textuais do catálogo antes de gravar.

**Racional.** O conteúdo canônico descreve as **doze** seções do catálogo, e a gerada não carrega
`content` — ela declara a coleção que a origina (`006`, FR-036). `_validar_secoes` recusa gravar
qualquer chave que não seja textual, e com razão: persistir texto gerado criaria dois endereços para
o mesmo conteúdo normativo. A identidade não entra no mapa porque `replace_draft` a recalcula a
partir do Edital de destino.

**Nota de efeito colateral aceito.** A origem publica todas as textuais, inclusive as que ninguém
editou — o conteúdo canônico traz o padrão do catálogo quando não há linha. A cópia, portanto,
persiste linha para todas elas no destino. É indistinguível do que o assistente produz quando alguém
abre e grava a etapa `Conteúdo`, e não altera o documento publicado.

---

## T-007 — "Rascunho vazio", e onde cada recusa é dita

**Decisão.** Rascunho vazio é o Edital que não tem Perfil, Evento, Etapa, Documento Exigido, Seção
persistida nem Anexo. A verificação acontece **duas vezes**: a tela não oferece a afordância, e o
serviço recusa.

**Racional.** `replace_draft` substitui o rascunho inteiro — o que não é reenviado é apagado. Sem a
recusa, escolher uma origem sobre um Edital já composto destruiria o trabalho em silêncio, e nenhum
diálogo de confirmação compra isso de volta (`D-002`). A dupla verificação é o padrão da casa:
*"oferecer o que se vai recusar é pior do que não oferecer"*, e a regra mora no backend de todo jeito.

**As recusas, e o código de cada uma:**

| Situação | Resposta |
|---|---|
| Ator sem `edital:elaborar` | recusa de permissão, como em toda a gestão |
| Edital de destino fora do escopo do ator | `404` indistinguível |
| Origem fora do escopo, inexistente, ou não publicada nem encerrada | `404` indistinguível — inelegível e inexistente respondem igual |
| Destino com qualquer conteúdo | recusa de domínio que nomeia o que já existe |
| Destino fora de elaboração, ou Processo encerrado | as recusas que a elaboração já dá |

---

## T-008 — O registro de origem, e a palavra que não se pode usar

**Decisão.** Um registro de auditoria com operação própria, cujo campo de motivo carrega o
**identificador da versão consolidada** de onde o conteúdo saiu. O aviso permanente resolve a versão
por esse identificador, chega ao Edital por `VersaoConsolidada.edital_id`, e renderiza número, ano e
título a partir da linha — nunca interpretando texto.

**Por que a versão, e não o Edital.** A Constituição exige que instâncias incorporadas *"preservem
independência **e versão**"* (*Restrições e Invariantes do Domínio*). Um identificador só responde as
duas perguntas, porque o Edital deriva da versão — o contrário não vale. E é a diferença entre
registrar algo verificável e algo que envelhece: retificada a origem, *de qual configuração partimos*
só tem resposta se a versão estiver nomeada. **Um identificador no campo, e não dois**: dois
exigiriam separá-los na leitura, e separar é interpretar texto.

**E a palavra:** em código, o conceito chama-se **origem** (`reaproveitado de`, `edital de origem`),
nunca *proveniência*. `proveniência` já está tomada neste domínio: `VersaoConsolidada.proveniencias`
relaciona **caminho normativo → Publicação que o alterou** (`004`/`005`). Dois sentidos para a mesma
palavra é precisamente o que o princípio I recusa, e a colisão seria pior por serem ambos sobre
"de onde isto veio".

**Racional.** `RegistroAuditoria` é append-only, indexado por `(aggregate_type, aggregate_id,
occurred_at)`, e é onde as outras perguntas de proveniência de ato já são respondidas. O
identificador é estável; o texto que hoje se escreve no motivo, não. Se o aviso lesse prosa, renomear
um rótulo apagaria a origem de Editais antigos — e o registro é justamente o que precisa sobreviver.

**Alternativas consideradas.**

- *Coluna `reaproveitado_de` no Edital* — reintroduz, em miniatura, a aresta Edital → Edital que a
  régua de `§2` recusa por colidir com P-6 (derivação normativa).
- *Guardar número e ano da origem no texto do registro* — congela no evento um dado que o Edital de
  origem já tem, e que uma Retificação pode alterar.
- *Guardar o identificador do **Edital*** — foi a primeira redação, e a análise cruzada a reprovou:
  é exatamente a metade "versão" que a Constituição pede, e que faltava.

---

## T-009 — Idempotência

**Decisão.** Reserva de chave por operação e destino, no formato que os comandos de criação já usam,
com a chave atravessando o reenvio do formulário.

**Racional.** O destino **já existe** quando a operação começa — não é ele que ela cria. O que a
repetição não pode produzir é uma segunda cópia sobre ele: sem reserva, um duplo clique gravaria o
rascunho duas vezes e criaria os Anexos duas vezes, deixando a coleção duplicada. O
`compare_and_swap` de `replace_draft` protege contra escrita concorrente sobre revisão velha, e não
contra a mesma requisição chegando duas vezes; são proteções diferentes e as duas são necessárias.

A tela leva `chave_idempotencia` como as telas de criação já levam — *"a chave atravessa o reenvio do
formulário: recarregar depois de um erro de preenchimento não pode criar dois"*.

**A ordem importa, e a primeira redação a tinha invertida.** A reserva vem **antes** das precondições
que a operação altera, porque ela altera justamente a que seria conferida: depois da primeira cópia o
rascunho não está mais vazio, e checar isso antes da chave faria toda repetição responder
`draft_not_empty` — a operação seria idempotente em tudo, menos no caso em que a idempotência serve.
`add_edital` já resolveu isso e deixou a razão escrita: *"Depois da repetição idempotente, como nos
demais comandos: reenviar a requisição que já criou o Edital continua devolvendo o mesmo Edital,
mesmo com o Processo já encerrado."*

Autorização e escopo ficam **antes** da reserva. Repetição conhecida não é passe para quem não
alcança o objeto, e `reserve` é por `(escopo, ator, operação, chave)` — a chave de outra pessoa nunca
é a sua.

### T-010 — A trilha precisa dizer de onde, e não um UUID

**Decisão.** A view de auditoria ganha duas coisas para esta operação: a entrada em `OPERACOES`, que
traduz o código em rótulo humano, e o **enriquecimento do motivo** — resolver a versão e o Edital, e
exibir *"a partir do Edital 173/2025, versão de 12/03/2026"* em lugar do identificador.

**Racional.** `FR-015a` guarda um identificador de propósito, para que nada envelheça. Mas quem abre
a trilha é pessoa, e `interface/views.py` entrega `"motivo": registro.reason` cru: sem o
enriquecimento, `US3` e `SC-005` ficariam atendidos no banco e não no canal do ator — e o princípio
VI diz que *"uma capacidade que o domínio sustenta mas que nenhuma interface alcança NÃO DEVE ser
considerada entregue"*. A própria `011` cita esse princípio para justificar a tela de auditoria da
comissão.

**O precedente, dito com honestidade.** A trilha **já** exibe identificador cru: a `020` grava
`reason=f"anexo {anexo.id}"`. Seguir o precedente seria defensável para um anexo, cuja identidade só
importa dentro do Edital; não é para a origem, porque é dela que `US3` trata. A decisão não corrige a
`020` — apenas não a imita onde o requisito é outro.

**Alternativas consideradas.**

- *Guardar o texto já legível no registro* — volta ao que `T-008` recusou: o texto envelhece, e
  renomear ou retificar a origem deixaria a trilha mentindo.
- *Resolver só no aviso da composição* — foi a primeira redação, e a análise cruzada a reprovou: o
  aviso desaparece quando o Edital sai da elaboração, e a trilha é justamente o que sobrevive.
