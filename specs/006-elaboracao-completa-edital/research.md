# Fase 0 — Decisões de desenho

Nenhum `NEEDS CLARIFICATION` restou do `spec.md`: as três decisões de produto foram fechadas na
sessão de clarificação e as duas de fato, por verificação no código. O que segue são as decisões
técnicas que o plano precisa fixar antes das tarefas, cada uma com o que foi recusado e por quê.

A régua de todas elas é a instrução da spec: **a menor evolução que atende integralmente o
requisito**. Onde uma solução mais genérica seria possível e não é necessária, ela aparece como
alternativa recusada — para que não volte durante a implementação.

---

## D-001 — Ordem como dado explícito, sem endpoint e sem command

**Decisão**: cada linha de Evento e de Etapa carrega um campo oculto `order`, atualizado pelos botões
de subir e descer; `ler_eventos` passa a ordenar por esse campo em vez de derivar a ordem da posição
de leitura.

**Racional, e correção de uma afirmação errada**: a versão anterior deste documento dizia que bastava
mover a linha no DOM porque a gravação já derivaria a ordem da posição. **Não derivaria.** `_indices`
recolhe os índices em um conjunto e os devolve ordenados numericamente
(`interface/forms.py:20-26`); a ordem visual é descartada antes do `enumerate` que produz `order`.
Mover a linha na tela, sozinho, não mudaria nada — e o defeito seria silencioso, porque a tela
mostraria a ordem nova e o banco guardaria a antiga.

Tornar a ordem explícita é menor do que a alternativa e mais honesto: a ordem passa a ser dado
enviado, e não convenção implícita que o cliente e o parser precisam manter em acordo.

**Alternativas recusadas**: renumerar os nomes dos campos no cliente ao mover a linha — mantém o
parser intocado, mas torna a correção do formulário dependente de o JavaScript reindexar
corretamente, e quebra em silêncio se uma remoção deixar buraco. `move_schedule_event` como command
com posição de destino — introduz semântica de movimento onde a gravação já expressa a ordem final.
Reordenação por arrastar — depende de biblioteca ou de muito JavaScript próprio, e degrada em
teclado e leitor de tela, contra o que a `002` estabeleceu.

**Consequência a testar**: mover uma linha e salvar muda a ordem persistida **e** não altera o `id`
de nenhum Evento. O primeiro é o teste que a afirmação anterior teria deixado passar.

---

## D-002 — Prévia: um renderizador com modo, não dois renderizadores

**Decisão**: `render_edital_pdf(snapshot, content_hash, modo)` com `modo ∈ {PREVIEW, PUBLISHED}`.
Em `PREVIEW` a composição não inclui a seção de integridade e o rodapé traz a marca de prévia; em
`PUBLISHED` o resultado é idêntico ao de hoje.

**Racional**: FR-010 proíbe um segundo layout, e FR-014 proíbe que a prévia exiba declaração de
integridade. Um parâmetro no ponto onde a diferença existe atende aos dois; a alternativa produz
divergência silenciosa entre o que se revisa e o que se publica — exatamente o risco que a prévia
deveria eliminar.

**Alternativas recusadas**: renderizador separado para prévia — duplica a composição e permite que
os dois documentos divirjam sem que nada acuse. Marca d'água aplicada depois, sobre os bytes —
exigiria manipular o PDF já montado, num gerador escrito à mão, por um ganho estético.

**Consequência a testar**: em `PUBLISHED`, os bytes gerados continuam idênticos aos de antes da
mudança; em `PREVIEW`, nenhuma página contém o hash e todas contêm a marca.

---

## D-003 — Prévia com origem única de conteúdo

**Decisão**: a prévia sempre renderiza `edital_snapshot(edital)`, em elaboração, submetido ou
homologado.

**Racional**: depois da submissão o rascunho não é editável — `replace_draft` exige
`EM_ELABORACAO` — e a publicação já recusa divergência entre o rascunho e a revisão homologada
(`publicacoes/application/publish_edital.py:282-285`). Nos três estados, portanto, o snapshot atual
é o conteúdo que será publicado. Uma segunda origem existiria para reproduzir o que a primeira já
garante.

**Alternativas recusadas**: renderizar de `revisao.content` quando submetido — dois caminhos de
origem, dois conjuntos de teste, e a divergência entre eles seria por definição impossível de
observar em produção, porque o sistema a proíbe antes.

**Consequência a testar**: a prévia de um Edital homologado e o documento publicado em seguida têm
o mesmo conteúdo normativo.

---

## D-004 — Identidade das entidades aninhadas na gravação do rascunho

**Decisão**: `ModalidadeConcorrencia` **e `RegraNormativa`** passam a ser criadas com os `id`
recebidos, como já ocorre com `PerfilVaga` e `EventoCronograma`; `perfis_persistidos` passa a
serializar a modalidade inteira, regra incluída; e `_reject_identifiers_of_other_editais` passa a
cobrir as duas.

**Racional**: hoje a modalidade é criada sem `id` (`editais/application/draft.py:87-92`) e a
serialização de preservação leva só `code` e `name` (`interface/forms.py:166-169`). O efeito é que
salvar qualquer etapa troca as identidades e apaga as regras normativas. Sem isso, a US3 entrega
uma tela que perde o que o usuário digitou.

**Alternativas recusadas**: gravação parcial por etapa, que preservaria o que não foi enviado — é
`replace_draft` deixando de ser substituição total, com um contrato ambíguo sobre o que a ausência
de uma coleção significa. Manter a modalidade sem identidade e reconciliar por `code` — chave de
negócio editável não é chave estável, e renomear um código passaria a apagar e recriar a regra.

**A Regra é parte do mesmo defeito.** Ela também é criada sem o `id` recebido
(`editais/application/draft.py:95-105`), e o `id` dela **viaja no conteúdo publicado**
(`publicacoes/application/publish_edital.py:36`). Considerei removê-lo do snapshot da versão 2 em vez
de preservá-lo — ele não endereça nada, como `colecoes.py` registra, e removê-lo faria o problema
desaparecer. Recusei: subtrair campo do conteúdo publicado exige decidir que a Regra não tem
identidade no domínio, o que a presença de `version` e `effective_from` contradiz. Preservar custa o
mesmo e é simétrico com todo o resto.

**`version` entra no formulário pelo mesmo motivo.** É obrigatório no serializer
(`editais/api/serializers.py:9`) e lido sem padrão no command; oferecer fundamento e percentual sem
ele produziria regra que a gravação recusa, ou obrigaria a inventar valor para um atributo normativo.

**Consequência a testar**: configurar regra com fundamento, versão e percentual, salvar o Cronograma,
recarregar; regra intacta, identidades da modalidade **e da regra** preservadas.

---

## D-005 — Coleções novas entram por declaração, em três registros

**Decisão**: `stages` e `sections` são acrescentadas a `COLECOES_COM_CHAVE`
(`publicacoes/domain/colecoes.py`), a `COLECOES_PUBLICADAS`
(`editais/domain/validation.py`) e ao dicionário produzido por `edital_snapshot`.

**Racional**: os três registros são declarativos e existem exatamente para isto. Endereçamento,
proveniência, consolidação e verificação de forma passam a cobrir as coleções novas sem código novo.

**Ressalva, corrigindo afirmação anterior**: não é verdade que a suíte hoje acuse sozinha o
esquecimento de qualquer um dos três. A `005` cobre a **coerência estrutural** do que está
declarado, mas a transcrição da forma publicada é conferida contra uma lista explícita —
`FORMAS` em `tests/contract/test_forma_publicada.py:67-70` nomeia `PerfilPublicado` e
`EventoPublicado` um a um. Acrescentar uma coleção ao snapshot e esquecer de declará-la em
`COLECOES_PUBLICADAS` não faria falhar nada: a lista simplesmente não a mencionaria.

**Por isso nasce um teste de cobertura**, e ele é tarefa desta feature: para cada coleção presente no
snapshot, exigir que exista forma declarada em `COLECOES_PUBLICADAS` e esquema correspondente no
`openapi.yaml`. É o que transforma "esquecemos de declarar" em falha de suíte, e é o que a
afirmação anterior deu como já existente.

**Alternativas recusadas**: descobrir coleções em tempo de execução pela presença de `id` — é
justamente o que o cabeçalho de `colecoes.py` descarta, porque acerta hoje e falha em silêncio no
dia em que nascer coleção sem identificador. Continuar com a lista explícita e confiar na revisão —
é exatamente o modo de falha que se acabou de observar neste plano.

**Consequência a testar**: uma Retificação que endereça `/stages/id=<uuid>/name` é aceita sem
alteração da gramática; e uma coleção acrescentada ao snapshot sem declaração falha a suíte.

---

## D-006 — Seção gerada não tem campo de conteúdo

**Decisão**: no snapshot, a seção gerada carrega `id`, `key`, `title`, `order`, `type` e `source`; a
seção textual carrega também `content`. A recusa a retificar conteúdo gerado não é uma regra: é
consequência de não haver caminho a endereçar.

**Racional**: FR-039 exige fonte única por conteúdo normativo. Persistir o texto gerado criaria dois
endereços para o mesmo conteúdo e a possibilidade de retificar um deixando o outro desatualizado. Não
persistir resolve o problema e ainda dispensa a regra: `REPLACE /sections/id=<uuid>/content` sobre
seção gerada falha pelo erro de caminho inexistente que a `004` já implementa.

**Alternativas recusadas**: manter o texto gerado no snapshot e recusar seu endereçamento por regra
nova na gramática — mais código, mais um erro nomeado, e contraria P-003. Deixar as seções geradas
fora do snapshot — a ordem do documento deixaria de ser normativa, e o documento publicado não
poderia ser reproduzido a partir do conteúdo publicado.

**Consequência a testar**: `REPLACE` sobre `/sections/id=<gerada>/content` é recusado; sobre
`/sections/id=<textual>/content` é aceito.

---

## D-007 — Catálogo de seções declarado, não gerenciável

**Decisão**: o conjunto de seções e sua ordem vivem em `editais/domain/secoes.py`, como declaração.
A persistência guarda apenas o conteúdo das seções textuais, referenciado pela chave do catálogo.

**Racional**: a clarificação fixou conjunto fixo. Declarar o catálogo em código torna a estrutura do
Edital revisável em diff, dispensa migration para mudar a redação institucional inicial e impede que
a ausência de uma seção obrigatória seja um estado alcançável.

**Alternativas recusadas**: seções como linhas criadas por seed — a estrutura passaria a depender do
estado do banco, e um Edital criado antes de uma mudança de catálogo ficaria estruturalmente
diferente sem que nada registrasse a diferença. Catálogo configurável por interface — é o construtor
de documentos que a P-006 e a clarificação excluem.

---

## D-008 — Versão canônica: recusar, não converter

**Decisão**: `SCHEMA_VERSION` sobe para 2 uma vez; a consolidação de Retificação recusa conteúdo-base
cuja `schemaVersion` difira da vigente; seeds e fixtures são regenerados.

**Racional**: hoje a Publicação de Retificação carimba a constante global
(`publicacoes/application/retificacoes.py:564`) sobre conteúdo derivado de uma Publicação-base que
carrega a própria versão. Depois do incremento, as duas podem divergir e o registro afirmaria uma
versão que o conteúdo não tem. A recusa é uma comparação; a alternativa é uma máquina.

**Alternativas recusadas**: conversão v1→v2 do conteúdo publicado, ou atualização em massa dos
snapshots existentes — ambas constroem compatibilidade para zero linhas publicadas, contra P-002 e
FR-048.

**Consequência a testar**: consolidar sobre conteúdo-base de versão anterior é recusado com erro
próprio, e não gravado com a versão errada.

---

## D-009 — Faixa do percentual no domínio, não no serializer

**Decisão**: a faixa entra em `editais/domain/perfis.py`, no caminho que a gravação atravessa.

**Racional**: a interface chama o command diretamente e não passa pelo serializer da API
(`interface/views.py:1-6`), de modo que validar no serializer deixaria a interface sem validação —
que é exatamente o canal onde o dado será digitado.

**Alternativas recusadas**: validar no serializer e no formulário — duas cópias da mesma regra, com
a certeza de divergirem. `CheckConstraint` apenas — recusa correta, mensagem inútil: o usuário
receberia erro de banco em vez de indicação de onde corrigir. A restrição de banco pode existir como
segunda camada, mas não substitui a verificação de domínio.

---

## D-010 — A seção tem `id` UUID e `key` textual, não uma coisa só

**Decisão**: cada item de `sections` carrega `id`, um UUID determinístico derivado de
`(edital.id, key)` por `uuid5`, e `key`, o identificador textual do catálogo. O caminho de
Retificação é `/sections/id=<uuid>/content`.

**Racional, e correção de um erro**: a versão anterior dizia que a `key` do catálogo seria o `id` da
coleção. **Não pode ser.** O seletor exige UUID — `selector_uuid` recusa qualquer outro texto e a
recusa é explícita: "o seletor id= exige um UUID"
(`publicacoes/domain/changes.py:101-113`, `:138-139`). `/sections/id=cronograma/content` seria
recusado como seletor inválido, e a coleção ficaria inendereçável — quebrando FR-038 sem que nada
no plano acusasse.

Determinístico, e não aleatório, porque a seção precisa ter identidade **antes de existir linha em
`SecaoEdital`**: uma seção gerada nunca tem linha, e uma textual só passa a ter depois da primeira
edição. Derivar de `(edital.id, key)` dá identidade estável desde o primeiro snapshot, igual entre
duas gerações do mesmo conteúdo, e distinta entre Editais.

**Alternativas recusadas**: gerar linha em `SecaoEdital` para toda seção no momento da criação do
Edital, só para ter UUID — persistiria estrutura que é declaração, e traria de volta o problema que
D-007 evita. Alargar a gramática para aceitar seletor textual — altera `changes.py`, contra P-003, e
por um caso que `uuid5` resolve sem tocar em nada.

**Consequência a testar**: o `id` de uma seção é o mesmo antes e depois de editá-la, e antes e
depois de republicar; e `REPLACE /sections/id=<uuid>/content` de uma seção textual é aceito.

---

## D-011 — Duas verificações direcionadas, e nenhum framework

**Decisão**: além da forma declarada, duas verificações próprias entram na validação de publicação —
a topologia de `sections` contra o catálogo, e a integridade de `stages[*].scheduleEventId` contra
`schedule`. Ambas produzem erro impeditivo, pelo mecanismo de `ValidationFinding` já existente.

**Racional**: `Campo` verifica presença, tipo, nulabilidade, formato e faixa **de um campo**, e o
próprio código registra que a coerência entre campos ficou de fora de propósito. Confiar só nela
deixaria uma Retificação fazer, sobre conteúdo publicado, o que a interface impede: acrescentar
seção com `ADD /sections/-`, remover uma seção do catálogo, trocar `type`, `order`, `title` ou
`source`, esvaziar o conteúdo de uma textual ou dar conteúdo a uma gerada. O catálogo fixo e a fonte
normativa única deixariam de valer exatamente onde mais importam — depois da publicação.

O mesmo vale para as Etapas: uma Retificação pode remover o Evento referenciado ou apontar
`scheduleEventId` inexistente, porque a verificação de forma confere que é um UUID, não que ele
exista.

São **duas verificações**, escritas para estes dois casos, no arquivo que já faz a verificação de
publicação. Não é um mecanismo de regras entre campos: expressar isso de forma genérica seria, nas
palavras do próprio `validation.py`, o primeiro passo para inventá-lo.

**Ainda pela via declarativa**: `weight` e `minimumScore` recebem `padrao` com a forma decimal
canônica, como `INSTANTE` já faz para o instante. Sem isso, declará-los apenas como texto aceitaria
`"banana"` depois de uma Retificação.

**Alternativas recusadas**: acrescentar coerência entre campos a `Campo` — generaliza a partir de
dois casos e contraria a nota deliberada do módulo. Recusar `sections` como coleção endereçável para
não precisar protegê-la — tornaria o texto do Edital incorrigível depois de publicado, que é
justamente o que a Retificação existe para permitir.

**Consequência a testar**: `ADD /sections/-`, `REMOVE /sections/id=<uuid>` e a troca de `type` são
recusados; `REPLACE` de `scheduleEventId` para UUID inexistente é recusado; `REPLACE` do `content`
de uma seção textual é aceito.

---

## Fora de pesquisa, por decisão da spec

Não foram investigados, por estarem fora de escopo: motor de cotas, critérios e planilhas de etapa,
modelos reutilizáveis, clonagem, editor rico e desempenho. Não há decisão pendente sobre eles nesta
feature.
