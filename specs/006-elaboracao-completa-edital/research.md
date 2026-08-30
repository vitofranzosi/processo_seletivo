# Fase 0 — Decisões de desenho

Nenhum `NEEDS CLARIFICATION` restou do `spec.md`: as três decisões de produto foram fechadas na
sessão de clarificação e as duas de fato, por verificação no código. O que segue são as decisões
técnicas que o plano precisa fixar antes das tarefas, cada uma com o que foi recusado e por quê.

A régua de todas elas é a instrução da spec: **a menor evolução que atende integralmente o
requisito**. Onde uma solução mais genérica seria possível e não é necessária, ela aparece como
alternativa recusada — para que não volte durante a implementação.

---

## D-001 — Reordenar sem endpoint e sem command

**Decisão**: os botões de subir e descer movem a linha no DOM; a gravação existente deriva a ordem
da posição das linhas no POST.

**Racional**: `interface/forms.py:97` já produz `order` por `enumerate` sobre os índices lidos, e
`replace_draft` já preserva o `id` de cada Evento. A capacidade inteira cabe em botões, uma função
de JavaScript e nenhuma linha de backend. FR-005 proíbe explicitamente criar endpoint enquanto isso
bastar.

**Alternativas recusadas**: `move_schedule_event` como command com posição de destino — introduz
semântica de movimento onde a gravação já expressa a ordem final, e obrigaria a conciliar duas
fontes de verdade sobre a mesma coisa. Reordenação por arrastar — depende de biblioteca ou de muito
JavaScript próprio, e degrada em teclado e leitor de tela, contra o que a `002` estabeleceu.

**Consequência a testar**: mover uma linha e salvar não pode alterar o `id` de nenhum Evento.

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

**Decisão**: `ModalidadeConcorrencia` passa a ser criada com `id` recebido, como já ocorre com
`PerfilVaga` e `EventoCronograma`; `perfis_persistidos` passa a serializar a modalidade inteira; e
`_reject_identifiers_of_other_editais` passa a cobrir modalidades.

**Racional**: hoje a modalidade é criada sem `id` (`editais/application/draft.py:87-92`) e a
serialização de preservação leva só `code` e `name` (`interface/forms.py:166-169`). O efeito é que
salvar qualquer etapa troca as identidades e apaga as regras normativas. Sem isso, a US3 entrega
uma tela que perde o que o usuário digitou.

**Alternativas recusadas**: gravação parcial por etapa, que preservaria o que não foi enviado — é
`replace_draft` deixando de ser substituição total, com um contrato ambíguo sobre o que a ausência
de uma coleção significa. Manter a modalidade sem identidade e reconciliar por `code` — chave de
negócio editável não é chave estável, e renomear um código passaria a apagar e recriar a regra.

**Consequência a testar**: configurar regra, salvar o Cronograma, recarregar; regra intacta e
identidades preservadas.

---

## D-005 — Coleções novas entram por declaração, em três registros

**Decisão**: `stages` e `sections` são acrescentadas a `COLECOES_COM_CHAVE`
(`publicacoes/domain/colecoes.py`), a `COLECOES_PUBLICADAS`
(`editais/domain/validation.py`) e ao dicionário produzido por `edital_snapshot`.

**Racional**: os três registros são declarativos e existem exatamente para isto. A `005` já garante
por teste que uma coleção presente no snapshot e ausente da declaração falhe a suíte, de modo que
esquecer um dos registros aparece como falha, não como silêncio. Endereçamento, proveniência,
consolidação e verificação de forma passam a cobrir as coleções novas sem código novo.

**Alternativas recusadas**: descobrir coleções em tempo de execução pela presença de `id` — é
justamente o que o cabeçalho de `colecoes.py` descarta, porque acerta hoje e falha em silêncio no
dia em que nascer coleção sem identificador.

**Consequência a testar**: uma Retificação que endereça `/stages/id=<uuid>/name` é aceita sem
alteração da gramática.

---

## D-006 — Seção gerada não tem campo de conteúdo

**Decisão**: no snapshot, a seção gerada carrega `key`, `title`, `order`, `type` e `source`; a
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
FR-046.

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

## Fora de pesquisa, por decisão da spec

Não foram investigados, por estarem fora de escopo: motor de cotas, critérios e planilhas de etapa,
modelos reutilizáveis, clonagem, editor rico e desempenho. Não há decisão pendente sobre eles nesta
feature.
