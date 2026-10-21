# Achado — a lista reservada sem inscrito nenhum não reverte a vaga, nem "por saldo"

**Encontrado em**: 21/10/2026, escrevendo a equivalência da prévia do sorteio
([`098`](../specs/098-previa-do-sorteio/spec.md), T009), contra a `main` em `14efe941`.

**Estado**: **registrado, não decidido.** A prévia do sorteio mostra o comportamento atual, como manda
a FR-2507 da `098`. Se ele é a leitura certa da norma é decisão do usuário.

> **Não vira escopo por estar escrito aqui.** O que se registra é o que o sistema faz, medido, e o que
> uma decisão teria de responder.

---

## O que se viu

Um Perfil com marco por sorteio, 4 vagas na ampla, 1 na PcD e 2 na PPI, alvo do quadro, reversão
declarada **"A quantidade que ficou sem preencher"** (por saldo). Doze inscritos, três autodeclarados
PPI e **nenhum** PcD. O caminho oficial, comando a comando:

| Passo | Ampla | PPI | PcD |
|---|---|---|---|
| Publicar a relação | ✅ 12 | ✅ 3 | ❌ `relation_would_be_empty` — *"Não há inscrição submetida no recorte: não existe universo a comprometer."* |
| Sortear | ✅ | ✅ | — (não há relação) |
| Calcular o corte | ✅ | ✅ | ❌ `sem_ato_vigente` — *"Este recorte ainda não tem ordem emitida…"* |
| Apurar a ocupação | ✅ 4/4/4/0 | ✅ 2/2/2/0 | ❌ `ordem_nao_vigente` — *"Este recorte não tem ordem vigente: não há ocupação a apurar."* |
| Movimentos de vaga gravados | — | — | **nenhum** |

**A vaga da PcD fica sem ocupante e não vai para a ampla.** O movimento de reversão nasce com a
apuração da reservada de origem, na mesma transação: `ocupacao/application/emissao.py` o calcula e
`ocupacao/application/movimento.py::gravar_reversao` o grava — é o único lugar do código que cria um
`MovimentoDeVaga`. A apuração de uma lista sem ordem é recusada antes de chegar lá, e por isso o
movimento nunca nasce.

## Por que importa

É o caso mais comum de vaga reservada não preenchida: **ninguém se inscreveu nela**. Os dois Editais
da amostra que declaram reversão o dizem com todas as letras:

- **28/2026, 4.3**: *"havendo ausência de candidatos aprovados"* na reserva, o quantitativo vai para a
  ampla do mesmo polo;
- **57/2026, 4.3**: *"na hipótese do não preenchimento total"* das vagas de ações afirmativas, o
  quantitativo vai para a ampla.

Uma lista vazia é a ausência mais completa possível de candidato. Lido ao pé da letra, os dois
Editais mandam reverter — e o sistema não reverte.

## A relação com a DP-2 da `095`

São parentes, e não o mesmo defeito:

- a **DP-2** é a reversão "por esgotamento" que nunca cede porque conta como "quem ocupar" quem já
  ocupa pela ampla — a apuração **roda**, e a regra decide não ceder;
- este achado é a lista vazia, em que a apuração **não roda** — e nenhuma espécie de reversão chega a
  ser consultada.

Uma decisão sobre a DP-2 não resolve este, e vice-versa.

## O que uma decisão teria de responder

1. **A relação vazia deve existir?** Hoje ela é recusada porque "não existe universo a comprometer".
   Uma relação vazia publicada comprometeria o universo vazio — que é um fato do certame, e auditável.
2. **Ou a apuração de lista sem ordem deve existir?** Apurar "0 ocupadas de 1" sem ordem nenhuma
   permitiria à reversão agir, sem tocar no sorteio.
3. **Quando a ausência é definitiva.** Lista vazia no fim das inscrições é definitiva; a decisão
   precisa dizer se o gatilho é o encerramento do período ou o congelamento das outras relações.

## O que a prévia faz enquanto isso

A prévia do sorteio (`098`) reproduz o caminho oficial: a lista vazia não é sorteada, a ocupação dela
aparece como "corte não emitido", e nada é cedido. O teste
`tests/integration/sorteios/test_previa_do_sorteio_equivale_ao_oficial.py::test_reservada_sem_inscritos_coincide`
prende a igualdade dos dois lados. Se a decisão mudar o caminho oficial, esse teste é o que acusa que
a prévia precisa acompanhar.
