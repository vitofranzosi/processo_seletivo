# Research: Endereçamento Normativo por Chave Estável

**Feature**: `004-enderecamento-normativo-estavel` | **Fase**: 0 | **Data**: 2026-08-29

Nenhuma questão ficou em aberto no Technical Context. O que fica aqui são as alternativas de
**desenho** avaliadas, e por que cada uma foi ou não escolhida.

## R1 — Onde interpretar o seletor

**Decisão**: no domínio, em `publicacoes/domain/changes.py`, junto de `parse_path` e `_descend`; e
**apenas quando o contêiner do segmento for uma lista**.

**Rationale**: a semântica de caminho já mora ali. Interpretar o seletor em qualquer contêiner
tiraria expressividade — uma chave de objeto chamada `id=algo` deixaria de ser endereçável —, e a
extensão não deve remover nada que o RFC 6901 permitia.

| Alternativa | Por que não |
| --- | --- |
| Resolver na camada de aplicação | A aplicação passaria a conhecer forma de caminho, que é conhecimento de domínio. E a consolidação, que roda no domínio, precisaria da mesma resolução — duas cópias. |
| Interpretar `id=` em qualquer contêiner | Remove expressividade sem ganho: em objeto não há ambiguidade a resolver, porque a chave já é nome. |
| Pré-normalizar todo caminho para índice antes de aplicar | Voltaria a depender da forma da lista no momento da aplicação, que é exatamente o defeito. |

## R2 — Como saber quais coleções têm chave

**Decisão**: declaração explícita no domínio, verificada por teste contra um snapshot real.

**Rationale**: detectar em tempo de execução — "elemento é dict e tem `id`" — funciona hoje e falha
em silêncio no dia em que uma coleção nova nascer sem identificador. A declaração transforma esse
dia numa falha de suíte em vez de num pressuposto quebrado sem aviso (FR-012).

| Alternativa | Por que não |
| --- | --- |
| Detecção por introspecção do elemento | Silenciosa quando erra. O pressuposto de que `requirements` é a única sem chave passaria a ser falso sem que nada acusasse. |
| Derivar dos modelos Django | O snapshot é conteúdo canônico, não espelho do ORM; um campo pode existir no modelo e não no snapshot, e vice-versa. |
| Não declarar e aceitar ambas as formas em qualquer coleção | Manteria o endereçamento posicional gravável onde há identidade, que é o que a feature elimina. |

## R3 — O que fazer com `expected_anchors`

**Decisão**: remover por migração de esquema. `RemoveField`, sem conversão.

**Rationale**: o sistema não está em produção e não há ato a preservar. A âncora respondia "ainda é
esta entidade neste índice?", pergunta que o caminho por chave passa a responder sozinho. Manter
mecanismo sem função é armadilha: alguém volta a preenchê-lo achando que protege algo.

| Alternativa | Por que não |
| --- | --- |
| Converter os caminhos existentes a partir das âncoras | Sem objeto: não há caminho a converter. Era o desenho da versão anterior, quando se supunha dado a preservar. |
| Manter a coluna e parar de usá-la | Coluna morta que a próxima pessoa tenta entender. E `models_retificacao.py` continuaria descrevendo um campo sem sentido. |
| Depreciar e remover num incremento posterior | Etapa a mais num sistema sem usuários. |

## R4 — Não construir `before=` e `after=`

**Decisão**: acréscimo é `/colecao/-`, ao fim. Inserção em posição específica não entra.

**Rationale**: a interface não oferece a operação, e nenhuma história a pede. Construir a gramática,
a resolução, os testes e o código de recusa para um caso que não existe é custo sem contrapartida.

**Consequência aceita e registrada**: o PDF publicado renderiza `profiles` e `schedule` na ordem do
array, então um Perfil acrescentado aparece ao fim. Se a ordem de apresentação vier a importar, a
resposta é ordenar por conteúdo — `code`, `order` —, não reintroduzir endereçamento por posição.

Vale o mesmo para o identificador: o seletor aceita **UUID**. Aceitar "qualquer texto" seria
generalizar para um caso que não existe, e cada forma admitida é uma que precisa ser testada e
documentada.

## R5 — O que acontece com a coreografia de ordem na interface

**Decisão**: some. `REPLACE` e `REMOVE` passam a ser independentes de ordem.

**Rationale**: `interface/retificacao.py` documenta hoje que a ordem de emissão **é a garantia de
correção** — `REPLACE` com os índices do vigente, `REMOVE` em ordem decrescente, `ADD` por último.
Essa coreografia inteira existe porque índice desloca. Com chave, o motivo desaparece, e é
literalmente o que a US2, cenário 2, pede.

**Consequência não óbvia**: o código de emissão encolhe. É raro uma mudança de representação
simplificar quem a consome; vale registrar para que ninguém preserve a ordenação por hábito.

## R6 — Como representar a mudança de contrato

**Decisão**: alterar o `openapi.yaml` da `001`, que segue sendo fonte única, e usar o `contracts/`
desta feature para a **gramática** e os códigos de recusa.

**Rationale**: mesma escolha da `003`. Um segundo arquivo OpenAPI criaria duas fontes para a mesma
API. Mas OpenAPI não expressa bem gramática de caminho — `targetPath` é `string` para ele —, e é
justamente a gramática que precisa estar escrita para quem audita um ato publicado saber como o
caminho foi resolvido (FR-017).

| Alternativa | Por que não |
| --- | --- |
| OpenAPI próprio da `004` | Duas fontes para a mesma API. |
| Só descrição em prosa no `openapi.yaml` | A gramática tem quatro formas de segmento e regra de contêiner; prosa dentro de um campo `description` não é lugar para isso. |
| Expressar a gramática como `pattern` regex no schema | Capturaria a sintaxe e não a regra que importa — qual forma vale depende do contêiner, que o schema não conhece. |
