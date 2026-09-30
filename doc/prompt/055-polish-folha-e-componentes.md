# 055 — Polish da folha e dos componentes

**Prompt de sessão autônoma: da spec ao PR, sem parar para perguntar.** Escrito em 30/09/2026 a
partir da [auditoria de polish](../auditoria-polish-ui-2026-09-30.md) (PR 240), sobre a `main` em
`c0f5ad3d`. É o **lote 1 de 3** da proposta de execução da auditoria (§9). Os lotes 2 (assistente de
composição) e 3 (telas de operação) terão prompt e spec próprios, e **não entram aqui**.

**A frase que governa:**

> Mesma informação, mesmo desenho, mesma altura — e nenhuma mudança que não se possa medir.

**E a frase que mantém o corte:**

> Esta feature acerta a folha e os componentes. Não reorganiza tela, não muda texto, não mexe em
> fluxo, e não toca o assistente de composição nem as telas de operação além do que a folha
> alcança sozinha.

---

## MODO DE TRABALHO — leia antes de tudo

Esta sessão roda **do início ao fim sem interação**. As decisões que uma spec normalmente
perguntaria já estão tomadas abaixo (D-1 a D-10) e entram **como recebidas, não como perguntas a
reabrir**.

- **Não rode `/speckit-clarify`.** Se surgir uma ambiguidade real, decida pelo critério mensurável
  do item correspondente. Registre a decisão como `D-0NN` no `research.md`, com a alternativa
  descartada e o custo dela, e siga.
- **Não peça confirmação entre as fases.** Specify, plan, tasks, analyze, implement, verificação e
  PR são uma sequência só.
- **Pare apenas nas condições da seção *Quando parar*.** Parar ali significa registrar o motivo em
  `doc/`, entregar o que já estiver verde e dizer o que faltou. Não significa perguntar e esperar.
- **Achado fora do escopo vira registro, não escopo.** Um arquivo `doc/achado-*.md` no estilo dos
  existentes. Governança é do usuário.
- **O merge é do usuário.** Abra o PR e pare. Não use `--auto`.

---

## PRÉ-CONDIÇÕES

1. **Worktree própria a partir da `main` atualizada.** Confira `git log origin/main -1`.
2. **A auditoria precisa estar legível.**
   - Confira o PR 240 com `gh pr view 240 --json state`.
   - Se já estiver mergeado, leia `doc/auditoria-polish-ui-2026-09-30.md` na própria árvore.
   - Se não estiver, leia pela branch:
     `git show origin/claude/audit-recruitment-ui-polish-a1a41c:doc/auditoria-polish-ui-2026-09-30.md`.
   - **Não** traga o arquivo para esta branch.
3. **Número e faixas: meça de novo, porque outra worktree pode ter avançado.**
   - Em 30/09 a pasta seguinte era **`specs/055`**.
   - O teto das faixas era **FR-999, SC-370, UX-133**.
   - A **faixa FR de três dígitos acabou**: esta spec abre em **FR-1000, SC-371, UX-134**.
   - Meça **em todas as worktrees** e **com quatro dígitos**. A varredura antiga, com `{3}`, não
     enxerga `FR-1000`:

   ```bash
   for w in $(git worktree list --porcelain | grep '^worktree ' | cut -d' ' -f2-); do
     grep -rhoE '(FR|SC|UX)-[0-9]{3,4}' "$w"/specs/*/spec.md 2>/dev/null; done |
     sort -u | awk -F- '{if($2+0>m[$1]) m[$1]=$2+0} END{for(k in m) print k, m[k]}'
   ```

   O número da spec vem de **`--number 55`**. `SPECIFY_FEATURE_DIRECTORY` não numera.
4. **Ambiente de desenvolvimento.**
   - Worktree nova não tem pytest: rode `uv sync --extra dev` uma vez.
   - Sem `backend/.env`, o `make check` morre com `permission denied for table django_migrations`.
     É ambiente, não o diff.
   - `make test-pg` lê `POSTGRES_USER`, não `DB_USER`.
   - Use um **`DB_NAME` próprio** — pelo `make`, é variável do Make e não prefixo de ambiente.

---

## CONTEXTO OBRIGATÓRIO, ANTES DO /specify

Ler, nesta ordem:

- **A auditoria.**
  - Seções 3, 4 e 7 (D1) e o F7 da seção 5 — a matéria deste lote.
  - A seção 9 — os lotes e as restrições que o código impõe.
  - A tabela "antes" da seção 9 — o que será medido de novo.
- **Os registros anteriores.**
  - [achado-numeros-da-ocupacao-espremidos.md](../achado-numeros-da-ocupacao-espremidos.md): o
    sintoma, cuja causa é o G1.
  - [achado-grade-dos-cartoes.md](../achado-grade-dos-cartoes.md): o que este lote **não** resolve.
- **A folha da gestão:** `backend/processo_seletivo/interface/templates/interface/base.html`.
  - l. 27–28: h1 e h2. Não existe h3.
  - l. 88: `.resumo`.
  - l. 117: padding de `th,td`.
  - l. 171: `.acao`.
  - l. 175: `.botao`.
  - l. 555: `.filtros`.
  - l. 708: `.botao.secundario`, com a borda que o primário não tem.
  - l. 1174–1189: o comentário do teto de bytes e o `estilo_da_pagina`.
- **A folha do portal:** `backend/processo_seletivo/portal/templates/portal/base.html`.
  - l. 238 e 254: as áreas da grade da seleção.
- **Os templates do G1.**
  - `interface/templates/interface/ocupacao.html:50`: `section.resumo`.
  - `corte.html:98` e `corte_historico.html`: `dl.resumo`.
  - `convocacao.html:85`: `ul.resumo` usado do jeito certo, com os mesmos quatro números da
    Ocupação.
- **O botão sem classe:** `portal/templates/portal/requerimento.html:204`.
- **Os testes que guardam a folha:**
  - `backend/tests/interface/test_acessibilidade.py`:
    - `:556`, toda classe citada precisa de regra;
    - `:527`, modificador sem base;
    - `:422`, todo botão de envio declara o seu peso;
    - `:106`, contraste.
  - `backend/tests/interface/test_larguras.py`: nenhum `max-width` em px; as duas larguras nos
    tokens.
  - `backend/tests/performance/test_escala_da_mesa.py:326`: o HTML **inteiro** da distribuição
    abaixo de 120.000 caracteres.
  - A varredura de vocabulário (`test_vocabulario_da_composicao.py`) e a de citações
    (`tests/test_citacoes_de_requisito.py`).
- `CLAUDE.md` e a Constituição.

---

## AS DECISÕES FECHADAS

Cada uma traz o **critério mensurável** que resolve a dúvida que ela não previu.

| | Decisão | Critério |
|---|---|---|
| **D-1** | **Escopo:** G1, G2, G3, G4, G5, G6, G7, G8, D1 e F7 da auditoria. Nada dos lotes 2 e 3: nem o stepper, nem o Conteúdo, nem coleções, glossário, hierarquia de ações de tela, formatação pt-BR ou Retificar | O item está na lista? Então entra. Não está? É registro |
| **D-2** | **G1:** a Ocupação e o Corte (e o histórico do Corte) mostram os números com o **padrão visual dos blocos da Convocação**, reaproveitando `ul.resumo` ou a regra dela. A `<section>` da Ocupação deixa de carregar a classe `.resumo`. Não se cria regra nova se a existente servir | Cada número fica visualmente preso ao **seu** rótulo, dentro do mesmo bloco. Nenhum número equidistante de dois rótulos. A `section` da Ocupação não é mais flex |
| **D-3** | **G2:** o padding global de `th,td` passa a `.5rem .75rem`, o do portal. Tabela com padding próprio **menor** fica como está | Linha das Inscrições do Edital 51/2026: **de 70 para ≤ 45 px** a 1280 px |
| **D-4** | **G3:** coluna numérica alinhada à direita, com **uma** classe. Unifique as grafias que a folha já tem só onde a unificação couber na D-1; a Visão Geral (estilo próprio da página) fica como está | A pontuação da ordem do marco fica à direita |
| **D-5** | **G4/G5, os botões:** `.botao` e `.botao.secundario` com a **mesma altura externa**. O primário ganha borda da cor do próprio fundo; não se tira a borda do secundário. Em **barras de ação** (navegação do assistente, barra de filtro, rodapé de confirmação), todo botão da linha tem a mesma altura. `.acao` continua pequeno dentro de linha de tabela e em contexto inline | Na barra do assistente, Voltar, Salvar rascunho e Avançar com **diferença de 0 px** de altura |
| **D-6** | **G5, a ação principal nunca é `.acao`.** Aplica-se onde a auditoria mediu: "Ver o que sairá vazio" (Matrículas) e "Filtrar" (Inscrições, Distribuição, Comissão). "Guardar e continuar depois" (`requerimento.html:204`) recebe `class="secundario"`. Não reclassificar botões fora dessa lista | Nenhum botão de envio sem classe no portal. As ações medidas deixam de ter 25 px |
| **D-7** | **G6, os títulos:** regra global de h3 na gestão. Escala h1 1,6 rem / h2 1,15 rem / h3 1 rem, com peso 600. Remova as sobreposições por contêiner que **só** mudam o tamanho de um título equivalente. A caixa-alta do h2 do Retificar sai, **salvo** se um comentário registrar o motivo — nesse caso fica, e o motivo entra no `research.md` | Em nenhuma tela auditada um h3 renderiza maior que o h2 da mesma página |
| **D-8** | **G7, os controles:** uma altura **por folha** para `input` (text, search, number, date, datetime-local, tel, email) e `select`. `textarea` e `file` não entram. Gestão e portal **não precisam** ter a mesma altura entre si | Na mesma linha, input e select com diferença de 0 px. Hoje: 38/40 na Visão Geral, 39/41 no Requerimento, 35/36/38 na Comissão |
| **D-9** | **G8, a barra de filtro:** o desenho da Vitrine — rótulos no topo, controles alinhados pelo topo, botão da altura dos controles. O texto de ajuda **não sai da tela** (é descrição do campo, e deve seguir ligado a ele por `aria-describedby` se já estiver); só deixa de desalinhar a linha | Na Distribuição, o desnível entre o select e o input cai de **22 px para 0**, e "Filtrar" tem a altura dos controles |
| **D-10** | **D1 e F7.** A grade da seleção do portal não reserva a área "sorteio" quando não há sorteio. Larguras pelo conteúdo, só nas telas medidas: Comissão (Identificador, Nome), Requerimento do portal (Telefone, Faixa de renda, Nome da mãe e do pai, UF) e Anexos (Rótulo, Arquivo). **Não** reorganizar `.campos` em grade de 12 colunas — isso é o `achado-grade-dos-cartoes`, e continua registro | Na seleção sem sorteio, o Cronograma começa na altura do topo das Vagas, e não **335 px** abaixo. Nenhum campo com conteúdo esperado de até 20 caracteres fica mais largo que ~20 rem; nomes até ~40 rem |

**O que esta feature não faz, por decisão:**
- não cria arquivo de tokens novo nem token de espaçamento — os três valores novos (escala de
  títulos, altura de controle, padding de célula) moram na folha;
- não muda texto de interface;
- não mexe em view, form nem domínio;
- não toca o PDF.

---

## AS RESTRIÇÕES QUE O CÓDIGO IMPÕE

**O teto de 120.000 caracteres.** A folha da gestão já ocupa ~81,5K do HTML da distribuição, e ~36,8K
disso são comentários `/* */`.
- **Meça a margem antes de escrever a primeira regra.** Rode o teste isolado e imprima
  `len(corpo)`.
- O saldo de bytes deste lote **não pode passar da margem**.
- **Não remova comentários da folha para abrir espaço.** Enxugar ou deixar de servir os comentários é
  decisão do usuário, e fica registrada como achado se for preciso.
- O caminho é o contrário: G2, D-5 e D-8 **substituem** regras. Apague a regra velha junto, em vez de
  sobrepor.
- Comentário novo segue o tom da casa — por quê, não o quê — e é **curto**.

**Prosa de comentário não pode ter tag HTML.** Um `<a>` dentro de comentário de CSS quebra a
varredura de template.

**Toda classe nova precisa de regra na folha, e toda regra removida pode órfã uma classe.** Rode
`test_acessibilidade` depois de cada remoção, não só no fim.

**`max-width` só em rem/ch/%/token**, nunca em px.

---

## ROTEIRO

1. **`/speckit-specify --number 55`**, com este documento como entrada.
   - O cabeçalho da spec declara a faixa de identificadores. Se o teto vier de spec **não
     mergeada**, escreva o número por extenso: citar identificador que a árvore não define reprova o
     teste de citações.
   - As decisões da spec nascem em **D-001**. As D-1 a D-10 deste documento são entrada, e não se
     reaproveitam como números.
   - Os casos-limite da spec também são requisitos: escreva cada um como FR/SC, porque a seção Edge
     Cases não entra na matriz e nenhuma ferramenta a cobra.
2. **`/speckit-plan`**, **`/speckit-tasks`** e **`/speckit-analyze`**.
   - O analyze exige plan e tasks, e lê a spec do `.specify/feature.json` (gitignored), não da
     branch.
   - Confira que o arquivo aponta para `specs/055-…` antes de rodá-lo, ou ele analisa a spec anterior
     sem avisar.
   - A `rastreabilidade.md` é cobrada requisito a requisito.
3. **Medição "antes", antes de tocar a folha.**
   - Banco: `createdb -T ps_polish_audit ps_055_polish`. Se `ps_polish_audit` não existir, use
     `createdb`, `migrate` e `seed_demo`.
   - Servidor: entrada **acrescentada** ao `.claude/launch.json` (o arquivo é versionado), com o
     seletor de identidade e o portal demo ligados e uma porta livre. **Reverta a entrada antes do
     commit.**
   - Janela: `resize_window` para 1280 × 900.
   - Repita a tabela "antes" da auditoria (§9) e as medidas próprias das D-2 a D-10, e grave em
     `specs/055-…/verificacao.md`.
4. **`/speckit-implement`.** Uma tarefa de cada vez. Rode `test_acessibilidade` e `test_larguras` a
   cada regra removida.
5. **Suíte:** `cd backend && make lint check test-pg`, com o seu `DB_NAME`. Não edite arquivo
   durante a suíte.
6. **Medição "depois"**, no mesmo banco, com os mesmos passos.
   - A tabela antes/depois vai para `verificacao.md`.
   - Passe também por **375 px** nas telas que mudaram de largura: Inscrições, Requerimento do
     portal, seleção do portal, barra de filtro.
   - Screenshots de antes e depois das telas do G1, da barra do assistente e da tabela de
     Inscrições.
7. **Commit e PR.**
   - Mensagens no padrão do repositório.
   - Na descrição do PR: a tabela antes/depois, o saldo de bytes contra o teto de 120K, e o total da
     suíte (passando/pulados).
   - **Não faça merge**, e não use `--auto`.

---

## QUANDO PARAR

- **O teto de 120K não comporta o lote**, mesmo apagando as regras substituídas. Entregue os itens
  que couberem, na ordem da matriz da auditoria (G1, G2+G3, G4+G5, depois G6, G7, G8, D1, F7).
  Registre em `doc/achado-*.md` quanto faltou e a opção dos comentários, e abra o PR com o que ficou
  verde.
- **Um teste existente exige mudar comportamento, texto ou domínio** para o item passar. O item sai
  do lote, o teste fica como está, e o conflito vira registro.
- **Uma medida "depois" piora em outra tela** — linha que quebra, controle cortado em 375 px — e a
  correção exigiria mexer em tela fora do escopo. Reverta o item e registre.

Em qualquer caso, o que já estiver verde segue para o PR. Parar não é perguntar.

---

## O TESTE QUE A FEATURE PRECISA PASSAR

Medido no mesmo banco, a 1280 × 900, antes e depois:

1. **Corte:** cada número da faixa calculada fica preso ao seu rótulo, sem número entre dois
   rótulos.
2. **Ocupação:** os quatro números em blocos, como na Convocação.
3. **Inscrições (Edital 51/2026):** linha de 70 px cai para **≤ 45 px**.
4. **Barra do assistente:** Voltar, Salvar rascunho e Avançar com a **mesma altura**.
5. **Portal:** "Guardar e continuar depois" deixa de renderizar como botão nativo do navegador.
6. **Títulos:** em Convocação e Processo, nenhum h3 maior que o h2 da página.
7. **Controles:** Visão Geral, Requerimento do portal e Comissão com input e select da mesma altura
   na mesma linha.
8. **Filtro da Distribuição:** desnível entre controles cai de 22 px para 0.
9. **Seleção do portal sem sorteio:** o Cronograma não começa 335 px abaixo das Vagas.
10. **Comissão:** o Identificador institucional deixa de ter 1.190 px.
11. **Requerimento do portal:** o Telefone celular deixa de ter 1.232 px.
12. **Suíte:** `make lint check test-pg` verde. O HTML da distribuição continua abaixo de 120.000
    caracteres, com o saldo declarado.

E o que o teste **não** cobre, deliberadamente:
- altura do stepper, tamanho do Conteúdo do Edital, coluna de ações da lista e detalhe do Edital —
  lote 3;
- números em formato pt-BR na Revisão — lote 3.

Se a spec prometer isso, está prometendo outra feature.

---

## ARMADILHAS OPERACIONAIS

- **Painel oculto do navegador tem viewport zero.** `resize_window` 1280 × 900 primeiro. Screenshot
  em branco não é defeito do produto.
- **Viewport emulado desalinha cliques.** Para agir, prefira `javascript_tool` (`botão.click()`); o
  `resize_window` fica para medir.
- **O preview pode reusar JS e CSS em cache.** Recarregue antes de medir o "depois".
- **Cookie de `localhost` não separa porta.** Outro `runserver` derruba a sessão da gestão.
- **`navigate` depois do código de acesso derruba a sessão do portal.** Para chegar ao Requerimento,
  use a candidata `MARIA` do fixture (`registrar(MARIA)`, `m@ex.br`) e navegue **por cliques**. O
  código sai em `preview_logs`.
- **`sed` do macOS ignora `\b`.** Renome em massa se faz em Python.
- **Matar o `make` deixa pytest órfão.** A próxima suíte disputa o banco.
