# Varredura dos 17 `AX` — quais sobrevivem às features que entraram depois

**Data:** 19/09/2026
**Contra:** a `main` em `b57052a`, que já traz a `032`, a `033`, a `034`, a `035`, a `036` e a `037`
**Objeto:** os 17 achados de
[auditoria-granularidade-normativa-2026-09-15.md](auditoria-granularidade-normativa-2026-09-15.md)

**Por que esta varredura existe.** Aquela auditoria é de **15/09** e ficou **quatro dias fora do
git** — existia só no diretório de trabalho de uma worktree, e foi encontrada por acaso numa
limpeza. Nesse intervalo entraram **seis features**, e a priorização de todas elas foi feita sem ela.
Antes de a auditoria voltar a pesar na fila, era preciso saber **o que dela ainda vale**.

---

## O resultado

**Nenhum dos 17 fechou.**

E a razão não é acaso: **o único commit em `backend/processo_seletivo/editais/models` desde 15/09 é
o da `030`**. As seis features que entraram depois trataram de **validação de executabilidade
(`032`), navegação por capacidade (`033`), ordem por recorte (`034`), sorteio executável (`035`),
instrução do recurso (`036`) e quatro becos de condução (`037`)**.

**Onze dos dezessete achados são sobre o que o modelo consegue representar.** Os dois eixos são
**ortogonais**, e é por isso que nada se fechou por consequência.

---

## Achado a achado

| | Achado | Estado | Como foi medido |
|---|---|---|---|
| `AX-1` | desempate aponta ao lado oposto, campo não retificável | 🔴 **aberto** | o sentido mora no campo `type` — `MAIOR_VALOR_DE_FATO` × `MENOR_VALOR_DE_FATO` em `classificacao/domain/desempate.py` —, e `CAMPOS_CRITERIO` em `interface/retificacao.py` expõe **apenas `order`** |
| `AX-2` | requisito de formação com duas fontes que se contradizem | 🟠 **provável** | não confirmado a fundo nesta varredura |
| `AX-3` | catálogo de Seções fechado, oito seções sem onde morar | 🔴 **aberto** | catálogo inalterado desde 15/09 |
| `AX-4` | Ficha de Avaliação varia por curso; a Etapa é do Edital | 🔴 **aberto** | modelo inalterado |
| `AX-5` | Curso, Área e Campus ofertante não existem | 🔴 **aberto** | modelo inalterado |
| `AX-6` | o código é o par `(perfil × polo)`, e o sistema tem um eixo | 🔴 **aberto** | modelo inalterado |
| `AX-7` | 3% e 30% para a mesma lei, sem uma conferência | 🔴 **aberto** | ver abaixo — **a conferência que existe é de outra natureza** |
| `AX-8` | número do Edital com duas fontes | 🟠 **provável** | não confirmado a fundo |
| `AX-9` | teto de inscrições por candidato não é publicado | 🔴 **aberto** | zero ocorrências de `registrationsPerCandidate` em `divulgacao/` e `portal/` |
| `AX-10` | "Documentos exigidos" funde quatro categorias | 🔴 **aberto** | modelo inalterado |
| `AX-11` | fatos declarados são do certame e moram no Perfil | 🔴 **aberto** | modelo inalterado |
| `AX-12` | numeração romana dos anexos não é verificada | 🔴 **aberto** | nenhuma verificação existe no backend |
| `AX-13` | cabeçalho de alcance dizia o nome do Perfil | ❓ **percurso** | comportamento de tela; o código não decide |
| **`AX-14`** | **documento publicado × execução se contradizem** | 🟠 **aberto** | ver abaixo — **a validação confere outra coisa** |
| `AX-15` | submodalidades de PPIQ não existem | 🔴 **aberto** | modelo inalterado |
| `AX-16` | restaurar o rascunho perde coleções aninhadas | ❓ **percurso** | a rede da `032` é **round-trip de servidor**; o `AX-16` é a **restauração no navegador**, outro caminho |
| `AX-17` | o PDF apaga a qualificação da modalidade | ❓ **percurso** | renderizador; precisa do documento gerado |

**11 abertos por medição · 3 prováveis · 3 dependem de percurso · 0 fechados.**

---

## As duas medições que decidem a fila

### `AX-7` — existe conferência de percentual, e ela não é a que falta

`editais/domain/validation.py::_divergencia_do_percentual` emite
`vacancy_row_percentage_divergence`, e o docstring diz o que ela faz:

> *"Dizer que `4` não é 20% de `80` é serviço legítimo; recalcular `4` não é."*

Ela compara **a quantidade declarada contra o percentual da própria linha**. Veio da **`025`**, que
**antecede a auditoria**.

**O que o `AX-7` descreve é outra coisa**: duas linhas vizinhas do mesmo Edital declarando **3% e
30% para a mesma lei federal**, e nada confrontando uma com a outra. **Nenhuma conferência cruza
fontes** — que é exatamente a forma do problema estrutural `E-4`.

### `AX-14` — a validação confere existência, não alcance

`validation.py` valida `documentRequirements` com esta intenção, escrita no próprio docstring:

> *"Requisito inaplicável nunca seria pedido a ninguém — e ninguém perceberia."*

Ela recusa documento que aponte para **Perfil inexistente** ou **modalidade inexistente**. E o
modelo **suporta** o alcance amplo: quando `profileId` é nulo, o alcance é `perfis.values()`, isto é,
todos.

**O que o `AX-14` descreve não é isso.** É um documento que **tem** `profileId` — porque o caminho
de composição o obriga —, alcança **um Perfil**, e é publicado com um texto que anuncia **a
modalidade inteira**. Nada confere se o alcance executado é o alcance anunciado.

**É o único achado do repositório em que o documento publicado e o comportamento do sistema se
contradizem**, e publicação é ato imutável.

---

## O que esta varredura recomenda

**Não decide a fila — mede para que a decisão seja informada.** A ordem é de quem governa o backlog.

1. **A `E-4` se confirma como a próxima**, e melhor armada do que estava: o `ACH-41` (duas datas de
   recurso), o `AX-2`, o `AX-8` e o `AX-7` são **quatro casos da mesma doença**, três deles medidos
   num Edital real. Era "ataca uma classe"; passou a ser "a classe tem membros".

2. **O `AX-14` precisa do percurso `E-2` refeito** contra o código de hoje — meio dia. Se confirmar,
   **é mais grave que a `E-4`**, e a ordem muda.

3. **O `AX-1` está confirmado** e é pequeno: `CAMPOS_CRITERIO`, em `interface/retificacao.py`, e os
   testes que a prendem. Cabe dentro da `E-4` ou vira spec curta. Muda **ordem de classificação** e
   hoje **não tem conserto pela interface**.

---

## O que esta varredura NÃO fez

- **Não reauditou nada.** Ela confronta os achados de 15/09 com o código de hoje; não procurou
  achados novos.
- **Não decidiu os três de percurso** — `AX-13`, `AX-16` e `AX-17` dependem de ver a tela e o
  documento gerado.
- **Não confirmou a fundo o `AX-2` e o `AX-8`.** Os dois têm forte indício e ficam como prováveis.

## A lição de método, que não é sobre os achados

**Um documento com 17 achados medidos ficou quatro dias invisível ao backlog** — não por decisão, por
estar num diretório que ninguém commitou. Seis features foram priorizadas sem ele.

O que impediu a perda foi uma limpeza de worktrees que **olhou antes de remover**. `git worktree
remove --force` teria apagado 1415 linhas sem recuperação, porque arquivo não rastreado não vai para
lugar nenhum.
