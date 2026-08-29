# Research: Endereçamento Normativo por Chave Estável

**Feature**: `004-enderecamento-normativo-estavel` | **Fase**: 0 | **Data**: 2026-08-29

Nenhum `NEEDS CLARIFICATION` restou do Technical Context: as cinco decisões abertas foram
respondidas na clarificação e o portão de qualidade fechou antes deste documento. O que fica aqui
são as alternativas de **desenho** avaliadas na Fase 0, e por que cada uma foi ou não escolhida.

## R1 — Onde interpretar o seletor

**Decisão**: no domínio, em `publicacoes/domain/changes.py`, junto de `parse_path` e `_descend`; e
**apenas quando o contêiner do segmento for uma lista**.

**Rationale**: a semântica de caminho já mora ali. Interpretar o seletor em qualquer contêiner
tiraria expressividade — uma chave de objeto chamada `id=algo` deixaria de ser endereçável —, e a
extensão não deve remover nada que o RFC 6901 permitia.

**Alternativas consideradas**:

| Alternativa | Por que não |
| --- | --- |
| Resolver na camada de aplicação, antes de chamar `apply_change` | A aplicação passaria a conhecer forma de caminho, que é conhecimento de domínio. E a consolidação, que roda no domínio, precisaria da mesma resolução — duas cópias. |
| Interpretar `id=` em qualquer contêiner | Remove expressividade sem ganho: em objeto não há ambiguidade a resolver, porque a chave já é nome. |
| Pré-normalizar todo caminho para índice antes de aplicar | Voltaria a depender da forma da lista no momento da aplicação, que é exatamente o defeito. |

## R2 — Como saber quais coleções têm chave

**Decisão**: declaração explícita no domínio, verificada por teste contra um snapshot real.

**Rationale**: detectar em tempo de execução — "elemento é dict e tem `id`" — funciona hoje e falha
em silêncio no dia em que uma coleção nova nascer sem identificador. A declaração transforma esse
dia numa falha de suíte em vez de num pressuposto quebrado sem aviso (FR-004c).

**Alternativas consideradas**:

| Alternativa | Por que não |
| --- | --- |
| Detecção por introspecção do elemento | Silenciosa quando erra. O pressuposto de que `requirements` é a única sem chave passaria a ser falso sem que nada acusasse. |
| Derivar dos modelos Django | O snapshot é conteúdo canônico, não espelho do ORM; um campo pode existir no modelo e não no snapshot, e vice-versa. |
| Não declarar e aceitar ambas as formas em qualquer coleção | Manteria o endereçamento posicional gravável onde há identidade, que é o que a feature elimina. |

## R3 — Estratégia da migração de conversão

**Decisão**: migração de dados que converte `target_path` das Retificações em estado não final a
partir de `expected_anchors`, com a lógica **congelada dentro da própria migração**, devolvendo o
que não resolver inequivocamente.

**Rationale**: `expected_anchors` já contém exatamente o que a conversão precisa — a identidade de
cada índice atravessado —, gravada pela `003`. A conversão não adivinha nada; recalcula o que teria
sido escrito se a forma por chave já existisse. O congelamento repete a lição que a revisão de
fechamento da `003` deu: migração aplicada não pode mudar de efeito porque o domínio evoluiu.

**Alternativas consideradas**:

| Alternativa | Por que não |
| --- | --- |
| Converter também as publicadas | Alterar ato normativo já produzido. A Constituição proíbe e as triggers da `003` recusam. |
| Devolver todas as não publicadas | Custa retrabalho e, nas homologadas, desfaz ato de autoridade por motivo de representação e não de mérito. |
| Deixar publicar como estão | São justamente os atos que atravessam a fronteira da mudança — os de maior risco. |
| Converter inferindo quando a âncora falta | Produz ato normativo que ninguém redigiu. É o defeito que a `003` levou duas revisões para corrigir. |

## R4 — Sequência da aposentadoria da âncora

**Decisão**: duas etapas. Primeiro parar de derivar e de verificar; depois, uma migração que
**comprova** a condição de SC-007 e só então remove a coluna.

**Rationale**: aposentar num movimento só juntaria três riscos diferentes. Separado, a primeira
etapa é reversível sem perda de dado, e a remoção da coluna acontece sobre condição verificada em
vez de sobre expectativa.

**Alternativas consideradas**:

| Alternativa | Por que não |
| --- | --- |
| Remover coluna e verificação juntas | Se a conversão tiver deixado caso para trás, o dado que provaria isso desaparece no mesmo movimento. |
| Manter a coluna indefinidamente | Mecanismo sem função vira armadilha: alguém volta a preenchê-lo achando que protege algo. |
| Manter a verificação como defesa em profundidade | Ela responde a pergunta que deixou de existir — não há índice a deslocar em caminho gravável. Verificação que nunca falha é ruído. |

## R5 — O que acontece com a coreografia de ordem na interface

**Decisão**: some. `REPLACE` e `REMOVE` passam a ser independentes de ordem.

**Rationale**: `interface/retificacao.py` documenta hoje que a ordem de emissão **é a garantia de
correção** — `REPLACE` com os índices do vigente, `REMOVE` em ordem decrescente, `ADD` por último.
Essa coreografia inteira existe porque índice desloca. Com chave, o motivo desaparece, e é
literalmente o que a US3, cenário 2, pede.

**Consequência não óbvia**: o código de emissão encolhe. É raro uma mudança de representação
simplificar quem a consome; vale registrar para que ninguém preserve a ordenação por hábito.

## R6 — Como representar a mudança de contrato

**Decisão**: alterar o `openapi.yaml` da `001`, que segue sendo fonte única, e usar o `contracts/`
desta feature para a **gramática** e os códigos de recusa.

**Rationale**: mesma escolha da `003`. Um segundo arquivo OpenAPI criaria duas fontes para a mesma
API. Mas OpenAPI não expressa bem gramática de caminho — `targetPath` é `string` para ele —, e é
justamente a gramática que precisa estar escrita para quem audita um ato publicado saber como o
caminho foi resolvido (FR-001b).

**Alternativas consideradas**:

| Alternativa | Por que não |
| --- | --- |
| OpenAPI próprio da `004` | Duas fontes para a mesma API. |
| Só descrição em prosa no `openapi.yaml` | A gramática tem cinco formas de segmento e regra de contêiner; prosa dentro de um campo `description` não é lugar para isso. |
| Expressar a gramática como `pattern` regex no schema | Capturaria a sintaxe e não a regra que importa — qual forma vale depende do contêiner, que o schema não conhece. |
