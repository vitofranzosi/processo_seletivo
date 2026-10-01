# 058 — Polish: os resíduos dos três lotes

**Prompt de sessão autônoma: da spec ao PR, sem parar para perguntar.** Escrito em 01/10/2026 a
partir da [reavaliação do polish](../reavaliacao-polish-ui-2026-10-01.md), sobre a `main` em
`39c9ec40`. É o fecho da série da [auditoria de polish](../auditoria-polish-ui-2026-09-30.md), depois
da [`055`](055-polish-folha-e-componentes.md), da [`056`](056-polish-assistente-de-composicao.md) e
da [`057`](057-polish-telas-de-operacao.md).

**A frase que governa:**

> O que já foi decidido para uma tela vale para a tela vizinha que ficou de fora, e nenhuma ação fica
> fora de alcance em tela estreita.

**E a frase que mantém o corte:**

> Só os resíduos listados na reavaliação. Nada de auditoria nova, nada de padrão novo: cada item
> reaplica uma decisão que já está na `main`.

---

## MODO DE TRABALHO — leia antes de tudo

Esta sessão roda **do início ao fim sem interação**. As decisões já estão tomadas abaixo (D-1 a D-10)
e entram **como recebidas, não como perguntas a reabrir**.

- **Não rode `/speckit-clarify`.** Se surgir uma ambiguidade real, decida pelo critério mensurável
  do item correspondente. Registre a decisão como `D-0NN` no `research.md`, com a alternativa
  descartada e o custo dela, e siga.
- **Não peça confirmação entre as fases.** Specify, plan, tasks, analyze, implement, verificação e
  PR são uma sequência só.
- **Meta numérica fora de alcance não amplia o escopo nem interrompe o lote.** Se um critério
  numérico não for atingível dentro do escopo, registre em `verificacao.md` o valor inicial, o valor
  alcançado e a justificativa, e siga.
- **Pare apenas nas condições da seção *Quando parar*.** Parar ali significa registrar o motivo em
  `doc/`, entregar o que já estiver verde e dizer o que faltou. Não significa perguntar e esperar.
- **Achado fora do escopo vira registro, não escopo.** Um arquivo `doc/achado-*.md` no estilo dos
  existentes. Governança é do usuário.
- **O merge é do usuário.** Abra o PR e pare. Não use `--auto`.

---

## PRÉ-CONDIÇÕES

1. **Worktree própria a partir da `main` atualizada.** Confira se outra sessão já abriu a `058`:
   `gh pr list` e `specs/058-*` em todas as worktrees.
2. **Número e faixas.**
   - Esta é a **`058`**, e o número vem de **`--number 58`**.
   - Em 01/10 o teto era **FR-1068, SC-410, UX-142**, e a faixa abria em **FR-1069, SC-411,
     UX-143**.
   - Meça de novo **em todas as worktrees** e **com quatro dígitos**:

   ```bash
   for w in $(git worktree list --porcelain | grep '^worktree ' | cut -d' ' -f2-); do
     grep -rhoE '(FR|SC|UX)-[0-9]{3,4}' "$w"/specs/*/spec.md 2>/dev/null; done |
     sort -u | awk -F- '{if($2+0>m[$1]) m[$1]=$2+0} END{for(k in m) print k, m[k]}'
   ```

3. **Ambiente de desenvolvimento.**
   - Worktree nova não tem pytest: rode `uv sync --extra dev` uma vez.
   - Sem `backend/.env`, o `make check` morre com `permission denied for table django_migrations`.
     É ambiente, não o diff.
   - `make test-pg` lê `POSTGRES_USER`, não `DB_USER`.
   - Use um **`DB_NAME` próprio**.

---

## CONTEXTO OBRIGATÓRIO, ANTES DO /specify

Ler, nesta ordem:

- **A [reavaliação](../reavaliacao-polish-ui-2026-10-01.md)**, inteira. É a matéria deste lote. O §5
  e o §7 dizem o que entra e o que fica de fora.
- **Os achados que este lote fecha:**
  - [achado-lista-e-conducao-a-375px.md](../achado-lista-e-conducao-a-375px.md);
  - [achado-resumo-na-secao-das-matriculas.md](../achado-resumo-na-secao-das-matriculas.md);
  - [achado-coluna-numerica-dos-resultados.md](../achado-coluna-numerica-dos-resultados.md);
  - [achado-f8-textos-que-saem-da-tela.md](../achado-f8-textos-que-saem-da-tela.md) — **só** a parte
    "Fora da lista do F8, na tela" e os campos numéricos das Etapas.
- **O achado que este lote não toca:**
  [achado-marca-de-cpf-repetido-alarga-a-lista.md](../achado-marca-de-cpf-repetido-alarga-a-lista.md).
  Foi fechado pelo usuário em 01/10: a marca fica como está.
- **As decisões que este lote reaplica:**
  - `specs/057-*/research.md`: D-002 (`hierarquia()`), D-003 (o contorno das terminais dentro do
    grupo), D-017 (a prova de ações por papel);
  - o comentário de `.distribuicao-moldura` na folha da gestão: a matriz de Alocação rola na
    horizontal só abaixo de 60 rem;
  - `specs/056-*/research.md`: D-005 e D-015 (a prova do POST por etapa).
- **O código:**
  - `interface/templates/interface/processo_detalhe.html`, l. 195 a 214 (a lista de atos), e
    `interface/atos_processo.py`;
  - `interface/acoes.py`, l. 240 a 290 (`hierarquia`, `da_linha`, `TERMINAIS`);
  - `lista.html` e `_linha_do_edital.html`, com a regra de `article.processo` (`overflow:hidden`);
  - `marco.html`, a tabela "Recortes deste marco" da Condução;
  - `matriculas.html`, a `section.resumo`;
  - `resultados.html`, a tabela de resultado;
  - `compor_revisao.html` e a grade de `dl` da Revisão (`Rotulada` em `interface/origens.py`, da
    `056`);
  - o motivo de um ato que sucede outro: área de texto de 3 linhas em `ordenacao.html` e `corte.html`,
    e campo de uma linha em `ocupacao.html` ("Motivo da nova apuração") e em `sorteio.html`;
  - `compor_etapas.html` com `_etapa.html` e o form que lê Peso, Nota mínima e Pontuação máxima;
  - os plurais com parênteses em `distribuicao.html`, `matriculas.html`, `recurso.html`,
    `ocupacao.html` (l. 117) e `ocupacao_historico.html` (l. 71), e o filtro `plural` em
    `interface/templatetags/interface_extras.py`.
- **Os testes que guardam a folha e as telas:** `tests/interface/test_acessibilidade.py`,
  `tests/interface/test_larguras.py`, `tests/performance/test_escala_da_mesa.py:326`,
  `tests/test_vocabulario_da_composicao.py`, `tests/test_citacoes_de_requisito.py`.
- `CLAUDE.md` e a Constituição.

---

## AS DECISÕES FECHADAS

| | Decisão | Critério |
|---|---|---|
| **D-1** | **Escopo:** R1 a R9 abaixo, e nada mais. **Ficam fora, aceitos:** <ul><li>a marca de CPF (decisão do usuário);</li><li>o cartão de Evento do Cronograma (a geometria não comporta);</li><li>o ganho menor do glossário (a faixa visível é decisão);</li><li>os textos que gravam ato (`objeto_legivel`, `validation.py`, `ocupacao.html` l. 207);</li><li>a ação cheia com contador zero no Edital (observação da reavaliação, sem proposta)</li></ul> | O item está na lista? Então entra. Não está? É registro |
| **D-2** | **Nenhuma ação acrescentada nem removida, nenhuma permissão mudada, nada muda no que se grava.** A prova da `057` (ações por papel, `href` e `formaction`) e a da `056` (POST de "Salvar rascunho" por etapa) valem aqui. A exceção é a do R6, com o critério dela | Diff vazio nas duas provas, nas telas tocadas |
| **D-3** | **R1 — Processo, "O que fazer agora".** Os atos do Processo seguem a regra que a `057` fixou para o Edital: os irreversíveis e as interrupções (Encerrar, Cancelar) ficam **contornados, nunca cheios**, à parte e por último, com o marcador "IRREVERSÍVEL". Reuse `hierarquia()` se o conjunto couber nela; se não, aplique a mesma regra de classe sem forçar o helper. O aviso de impedimento continua onde está, e os links continuam levando ao mesmo lugar | Nenhum botão cheio entre os atos do Processo, quando ele está Ativo, no seed |
| **D-4** | **R2 — 375 px.** A Lista de Editais adota a solução da matriz de Alocação: abaixo de 60 rem, a tabela de cada Processo fica numa moldura com rolagem horizontal, no lugar do recorte silencioso. **Não** empilhar as células. A tabela "Recortes deste marco" da Condução ganha a mesma moldura | A 375 px: largura de rolagem do documento igual a 375 na Lista e na Condução, e todo botão de ação da Lista alcançável dentro da moldura (`scrollWidth` da moldura ≥ a borda direita do último botão) |
| **D-5** | **R3 — Matrículas.** Tirar `class="resumo"` da `section`, como a `055` fez na Ocupação. Sem regra nova | Título e nota empilhados, sem nenhum filho da seção lado a lado |
| **D-6** | **R4 — Resultados.** `class="tabela"` na tabela de `resultados.html`, para a regra `.tabela td.numero` pegar. Se a coluna misturar número e texto ("favorável", "não avaliada"), só a célula numérica leva `numero`: texto não vai à direita sozinho | Números à direita; nenhuma célula de texto à direita |
| **D-7** | **R5 — F8, o que é só tela.** Os plurais com parênteses de `distribuicao.html` ("consolidada(s)", "recusada(s)"), `matriculas.html` ("linha(s)"), `recurso.html` ("ato(s) de instrução") e o "Reversão de cota: N vaga(s)" de `ocupacao.html` l. 117 e `ocupacao_historico.html` l. 71 passam ao filtro `plural`. **Antes de cada troca**, confira se o texto vai para ato, registro ou documento; se for, ele fica e entra no achado. `compor_base.html` l. 70 entra, com o teste que o prende reescrito para a grafia nova, sem mudar o que ele verifica | Nenhum "(s)" nas telas tocadas, salvo os registrados como texto que grava |
| **D-8** | **R6 — campos numéricos das Etapas.** Peso, Nota mínima e Pontuação máxima mostram o valor como uma pessoa o escreve ("2", "6", "87,5"), **só se o rascunho gravado continuar idêntico**. A prova aqui não é o POST (o texto enviado muda de "2.0000" para "2"), e sim o **rascunho gravado depois de "Salvar rascunho"**, comparado antes e depois no mesmo banco. Se o rascunho gravado mudar, o item sai e fica registrado | Campos sem zeros à direita, **e** rascunho gravado idêntico. Os dois juntos, ou nenhum |
| **D-9** | **R7 e R8 — os dois desalinhamentos.** R7: na Revisão, a coluna de rótulos tem a **mesma largura** em todos os blocos de `dl`, com valor fixo em rem. R8: o motivo de sucessão da Ocupação ("Motivo da nova apuração") e o do Sorteio usam o mesmo controle e a mesma largura do motivo da Ordenação e do Corte (área de texto de 3 linhas em `--leitura`), sem mudar o nome do campo | R7: os valores começam no mesmo x em todos os blocos da Revisão do 76/2027. R8: o mesmo controle e a mesma largura nas quatro telas |
| **D-10** | **R9 — documentação dos lotes.** Corrigir no repositório o que a reavaliação (§6) apontou: a D-003 da `056` passa a dizer 60 rem, o valor da folha. O PR 246 não se edita. O total da suíte completa vai na `verificacao.md` **desta** spec | Nenhuma divergência entre o `research.md` da `056` e a folha |

**O que esta feature não faz, por decisão:**
- não cria padrão novo: cada item reaplica uma decisão que já está na `main`;
- não muda texto de interface além dos plurais da D-7;
- não mexe em view, form nem domínio, com a exceção possível do valor exibido da D-8;
- não toca o PDF.

---

## AS RESTRIÇÕES QUE O CÓDIGO IMPÕE

**O teto de 120.000 caracteres fica.** Em 01/10 a página da distribuição tinha 82.477.
- **Registre o tamanho antes e depois**: rode o teste isolado, imprima `len(corpo)` e grave os dois
  números em `verificacao.md` e na descrição do PR.
- Comentário novo nasce como `{% comment %}`. Não apague documentação e não altere regra CSS só para
  reduzir tamanho.

**Toda classe nova precisa de regra na folha. `max-width` só em rem, ch, % ou token.** Prosa de
comentário sem tag HTML.

**A moldura com rolagem (D-4) não pode quebrar o cabeçalho fixo da Alocação**, que é o motivo de a
moldura dela não rolar em tela larga. Leia o comentário de `.distribuicao-moldura` antes. Na Lista,
a rolagem vale **só abaixo de 60 rem**.

---

## ROTEIRO

1. **`/speckit-specify --number 58`**, com este documento como entrada.
   - O cabeçalho da spec declara a faixa. Se o teto vier de spec não mergeada, escreva o número por
     extenso.
   - As decisões da spec nascem em **D-001**.
   - Os casos-limite viram FR/SC, porque a seção Edge Cases não entra na matriz.
2. **`/speckit-plan`**, **`/speckit-tasks`** e **`/speckit-analyze`**.
   - Confira que `.specify/feature.json` aponta para `specs/058-…` antes do analyze.
   - A `rastreabilidade.md` é cobrada requisito a requisito.
3. **Medição "antes", antes de tocar template ou folha.**
   - Banco: `createdb -T ps_polish_audit ps_058_polish`, ou `createdb`, `migrate` e `seed_demo` se a
     origem não existir.
   - Servidor: entrada **acrescentada** ao `.claude/launch.json` e revertida antes do commit.
   - Telas e janelas:
     - Processo, Matrículas, Resultados, Revisão (76/2027), Ocupação e Etapas, a 1280 × 900;
     - Lista e Condução, a **375 px**.
   - Grave em `specs/058-…/verificacao.md`:
     - as medidas de cada critério;
     - a lista de ações por papel das telas tocadas;
     - o POST de "Salvar rascunho" das Etapas;
     - **o rascunho gravado** das Etapas (D-8).
4. **`/speckit-implement`.** Um item por vez. Depois de cada um, recapture a prova que ele toca
   (ações, POST ou rascunho) e rode `test_acessibilidade`.
5. **Suíte:** `cd backend && make lint check test-pg`, com o seu `DB_NAME`. Não edite arquivo
   durante a suíte.
6. **Medição "depois"**, no mesmo banco.
   - A tabela antes/depois vai para `verificacao.md`, com os diffs das provas (vazios).
   - Screenshots de antes e depois do Processo, da Lista a 375 px e da Revisão.
7. **Fechar os achados.** Em cada `doc/achado-*.md` que este lote resolveu, acrescente a situação
   (**resolvido pela `058`**, com a medida), sem apagar o registro.
8. **Commit e PR.**
   - Na descrição: a tabela antes/depois, os diffs vazios, o tamanho da página da distribuição
     antes e depois, e o total da suíte.
   - **Não faça merge.**

---

## QUANDO PARAR

- **Uma das provas da D-2 muda** e a causa não se resolve sem acrescentar, tirar ou mudar ação ou
  campo. O item sai do lote, o código dele é revertido, e vira registro.
- **O rascunho gravado das Etapas muda** com a D-8. O R6 sai, e o achado do F8 recebe a medida.
- **A moldura da D-4 quebra o cabeçalho fixo da Alocação**, ou exige mexer na matriz. A Lista e a
  Condução seguem, e a Alocação fica como está.
- **Um teste existente exige mudar comportamento, texto (fora da D-7) ou domínio** para o item
  passar. O item sai, e o conflito vira registro.

Em qualquer caso, o que já estiver verde segue para o PR. Parar não é perguntar.

---

## O TESTE QUE A FEATURE PRECISA PASSAR

1. **Processo Ativo do seed:** Encerrar Processo e Cancelar Processo contornados, à parte, com
   "IRREVERSÍVEL"; nenhum ato cheio; os links levam aos mesmos lugares.
2. **Lista de Editais a 375 px:** largura do documento = 375; os botões de ação de cada Edital
   alcançáveis por rolagem dentro da moldura.
3. **Condução a 375 px:** largura do documento = 375.
4. **Alocação a 1280 px:** o cabeçalho continua fixo ao rolar a página.
5. **Matrículas:** título e nota da seção empilhados.
6. **Resultados:** números à direita, texto à esquerda.
7. **Distribuição, Matrículas, Recurso, Ocupação e histórico:** nenhum "(s)" nas telas tocadas, salvo
   os registrados.
8. **Etapas:** "2", "6", sem zeros, e rascunho gravado idêntico. Ou o item registrado como fora,
   com a medida.
9. **Revisão:** valores alinhados no mesmo x em todos os blocos.
10. **Ocupação e Sorteio:** o motivo com o mesmo controle e largura do motivo da Ordenação e do Corte.
11. **Provas:** ações por papel e POST das Etapas idênticos.
12. **Suíte:** `make lint check test-pg` verde; HTML da distribuição abaixo de 120.000, com o tamanho
    antes e depois registrado.

E o que o teste **não** cobre, deliberadamente: a marca de CPF, o cartão de Evento, o glossário e os
textos que gravam ato. Todos já estão decididos ou registrados.

---

## ARMADILHAS OPERACIONAIS

- **Viewport emulado a 375 px tem o modo de dispositivo móvel.** Uma página mais larga que a janela
  faz o navegador aumentar a janela de layout: `innerWidth` passa de 375 para a largura da página (a
  Condução deu 486). Meça `document.documentElement.scrollWidth` **e** `innerWidth`.
- **Painel oculto do navegador tem viewport zero.** `resize_window` antes de medir; volte ao preset
  `desktop` no fim.
- **Viewport emulado desalinha cliques.** Para agir, use `javascript_tool` (`botão.click()`).
- **O preview reusa JS e CSS em cache.** Recarregue antes de medir o "depois".
- **Para trocar de papel na gestão**, use o botão "Sair" do cabeçalho (é POST) e entre de novo pelo
  seletor de identidade.
- **`sed` do macOS ignora `\b`.** Renome em massa se faz em Python.
- **Matar o `make` deixa pytest órfão.** A próxima suíte disputa o banco.
