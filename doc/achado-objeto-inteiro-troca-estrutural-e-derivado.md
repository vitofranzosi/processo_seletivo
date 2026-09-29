# Achado — o objeto inteiro ainda troca campo estrutural e derivado

Encontrado em 28/09/2026, ao fechar o RC-130 da
[auditoria de consolidação](auditoria-de-consolidacao-2026-09-26.md) (A-6 da
[`048`](../specs/048-retificacao-que-acrescenta/spec.md)).

> **Não virou escopo por estar escrito aqui.** O que se registra é uma decisão em aberto, e decidir é
> do usuário.

## O que se observou

A gramática de `publicacoes/domain/changes.py` recusa o endereçamento direto de **três** naturezas
do contrato de mutabilidade, e não de uma: a não retificável, a derivada e a estrutural
(`colecoes.FORA_DO_ALCANCE_DIRETO`, FR-297 da `026`). O RC-130 era a troca de campo **não
retificável** pela substituição do objeto que o contém, e é essa que a correção fechou:
`recusar_troca_de_campo_nao_retificavel` compara o antes e o depois de cada elemento, no ato de
Retificação, e recusa.

As outras duas naturezas têm a mesma porta, e ela continua aberta. Medido sobre `apply_changes` e a
guarda nova, com um conteúdo mínimo:

| Alteração | Endereçado sozinho | Pelo objeto inteiro |
|---|---|---|
| `code` do Perfil (estrutural) | recusado | **aceito** |
| `code` do marco (estrutural) | recusado | **aceito** |
| `order` e `status` do Evento (estrutural e derivado) | recusado | **aceito** |

Não foi reproduzido pela API, e só o `apply_changes` foi exercitado. A validação de publicação pode
recusar parte desses casos por outro motivo, como código repetido no Edital.

## Por que não coube na correção

- **O pedido e a `DP-13` nomeiam o não retificável.** Estender a guarda às outras naturezas é
  decidir o que ela protege, e não só corrigir o que já estava decidido.
- **O derivado tem caminho legítimo de mudança.** O `artifactHash` do Anexo muda junto com o
  `artifactId` que o origina, e a tela emite os dois no mesmo ato (`colecoes.FONTE_DO_DERIVADO`).
  Uma guarda por elemento precisaria saber que o derivado só muda quando a fonte dele muda no mesmo
  elemento. Ninguém escreveu essa regra.
- **O estrutural é o que a `DP-13` usa para casar Perfis.** O código da Modalidade é identidade do
  Edital desde a `044`, e o "aplicar a todos" do passo 1 remapeia por código. Trocar o código de um
  objeto publicado pela substituição inteira é, das portas que sobram, a que pesa mais na próxima
  spec.

## O que destravaria

Uma decisão sobre a extensão da guarda:

- **ao estrutural**, com a razão da natureza que `colecoes.RECUSA_POR_NATUREZA` já escreve;
- **ao derivado**, com a regra de que ele só muda acompanhado da fonte no mesmo elemento. É a regra
  que `_derivado_tem_a_fonte_no_mesmo_ato` aplica hoje ao endereçamento direto.

A guarda do RC-130 já percorre os elementos e compara campo a campo. Estendê-la custa a lista de
campos por natureza e os testes das fronteiras. Não custa mecanismo novo.
