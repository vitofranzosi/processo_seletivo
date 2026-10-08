# 056 — Polish do assistente de composição

**Prompt de sessão autônoma: da spec ao PR, sem parar para perguntar.** Escrito em 30/09/2026 a
partir da [auditoria de polish](../auditoria-polish-ui-2026-09-30.md), sobre a `main` em `ed9b13ca`.
É o **lote 2 de 3** da proposta de execução da auditoria (§9):

- o lote 1 é a [`055`](055-polish-folha-e-componentes.md), folha e componentes;
- o lote 3 é a [`057`](057-polish-telas-de-operacao.md), telas de operação.

**A frase que governa:**

> Quem abre uma etapa do assistente vê o trabalho da etapa na primeira dobra, e cada item da coleção
> ocupa a altura do que ele tem a dizer.

**E a frase que mantém o corte:**

> Densidade dentro do padrão que existe. Nenhuma coleção vira tabela editável nem mestre-detalhe,
> nenhum campo sai do formulário, e nada muda no que a etapa grava.

---

## MODO DE TRABALHO — leia antes de tudo

Esta sessão roda **do início ao fim sem interação**. As decisões que uma spec normalmente
perguntaria já estão tomadas abaixo (D-1 a D-9) e entram **como recebidas, não como perguntas a
reabrir**.

- **Não rode `/speckit-clarify`.** Se surgir uma ambiguidade real, decida pelo critério mensurável
  do item correspondente. Registre a decisão como `D-0NN` no `research.md`, com a alternativa
  descartada e o custo dela, e siga.
- **Não peça confirmação entre as fases.** Specify, plan, tasks, analyze, implement, verificação e
  PR são uma sequência só.
- **Pare apenas nas condições da seção *Quando parar*.** Parar ali significa registrar o motivo em
  `doc/`, entregar o que já estiver verde e dizer o que faltou. Não significa perguntar e esperar.
- **Meta numérica fora de alcance não amplia o escopo nem interrompe o lote.** Se um critério
  numérico (altura, largura, posição) não for atingível dentro do escopo, registre em
  `verificacao.md` o valor inicial, o valor alcançado e a justificativa, e siga para o próximo item.
  Não amplie o escopo para alcançá-lo e não pare o lote por causa dele.
- **Achado fora do escopo vira registro, não escopo.** Um arquivo `doc/achado-*.md` no estilo dos
  existentes. Governança é do usuário.
- **O merge é do usuário.** Abra o PR e pare. Não use `--auto`.

---

## PRÉ-CONDIÇÕES

1. **A `055` precisa estar na `main`.**
   - Confira se `specs/055-*` existe em `origin/main`.
   - Se não existir, **pare antes do specify** e diga que falta a `055`.
   - O motivo: as duas mexem na mesma folha e dividem o mesmo teto de 120.000 caracteres. Rodar
     em paralelo faz cada uma medir uma margem que a outra vai gastar.
2. **Worktree própria a partir da `main` atualizada.**
3. **Número e faixas: meça de novo.**
   - Esta é a **`056`**, e o número vem de **`--number 56`**.
   - A faixa abre logo acima do teto que a `055` deixar. Em 30/09 o teto era FR-999, SC-370,
     UX-133, antes da `055`.
   - Meça **em todas as worktrees** e **com quatro dígitos**:

   ```bash
   for w in $(git worktree list --porcelain | grep '^worktree ' | cut -d' ' -f2-); do
     grep -rhoE '(FR|SC|UX)-[0-9]{3,4}' "$w"/specs/*/spec.md 2>/dev/null; done |
     sort -u | awk -F- '{if($2+0>m[$1]) m[$1]=$2+0} END{for(k in m) print k, m[k]}'
   ```

4. **Ambiente de desenvolvimento.**
   - Worktree nova não tem pytest: rode `uv sync --extra dev` uma vez.
   - Sem `backend/.env`, o `make check` morre com `permission denied for table django_migrations`.
     É ambiente, não o diff.
   - `make test-pg` lê `POSTGRES_USER`, não `DB_USER`.
   - Use um **`DB_NAME` próprio**.

---

## CONTEXTO OBRIGATÓRIO, ANTES DO /specify

Ler, nesta ordem:

- **A auditoria.**
  - A seção 5 inteira (F1 a F6) e o D4 da seção 7 — a matéria deste lote.
  - A seção 9 — as restrições.
  - A tabela "antes".
- **[analise-ux-colecoes-repetidas-2026-09-29.md](../analise-ux-colecoes-repetidas-2026-09-29.md),
  §9 e §10.**
  - Ela classifica o Cronograma como "tabela editável, P2" e Etapas, Anexos e Conteúdo como
    "manter".
  - **Este lote não contradiz isso**: faz densidade dentro do cartão que existe e não troca o padrão
    de interação. A tabela editável do Cronograma continua sendo a proposta dela, e continua fora
    daqui.
- **A `specs/055-*`**, inteira: o que ela já acertou na folha (botões, títulos, controles) é base
  deste lote, e não se refaz.
- **Os templates do assistente**, em `backend/processo_seletivo/interface/templates/interface/`:
  - `compor_base.html`, `_navegacao_etapa.html` e o stepper `.assistente` (folha da gestão, l. 255
    a 262);
  - `compor_cronograma.html` com `_evento.html`;
  - `compor_etapas.html` com `_etapa.html`;
  - `compor_inscricao.html` com `_documento.html`;
  - `_perfil.html` com `_modalidade.html`;
  - `compor_conteudo.html`;
  - `compor_revisao.html` com `interface/revisao.py`;
  - `compor_anexos.html`;
  - `retificar.html` com `_retificacao_perfil.html`.
- **Os scripts** em `interface/static/interface/`:
  - `remocao.js` e `assistente.js`, que localizam os botões ↑ ↓ 🗑 e a ordem;
  - `rascunho.js`;
  - `retificacao.js`, que detecta alteração pelos **nomes** dos campos.
- **As memórias do repositório sobre perda de dado**, que valem como norma aqui:
  - `replace_draft` apaga o que não for reenviado: **campo que sai do HTML é dado apagado** na
    próxima gravação;
  - campo `required` escondido é envio que o navegador recusa sem mostrar o que falta;
  - a etapa Perfis tem teto de campos por envio (13.000) e um guardião que o cobra.
- **Os testes que guardam a folha e as telas:**
  - `tests/interface/test_acessibilidade.py`;
  - `tests/interface/test_larguras.py`;
  - `tests/performance/test_escala_da_mesa.py:326`, o teto de 120.000 caracteres;
  - `tests/test_vocabulario_da_composicao.py`;
  - `tests/test_citacoes_de_requisito.py`.
- `CLAUDE.md` e a Constituição.

---

## AS DECISÕES FECHADAS

Cada uma traz o **critério mensurável** que resolve a dúvida que ela não previu.

| | Decisão | Critério |
|---|---|---|
| **D-1** | **Escopo:** F1, F2, F3, F4, F5 e D4 da auditoria, e F6 **por último e dispensável**. Nada dos lotes 1 e 3 | O item está na lista? Então entra. Não está? É registro |
| **D-2** | **Nenhum campo sai do formulário, nenhum nome de campo muda, nada muda no que a etapa grava.** Mudar o **controle** de um campo (input para textarea) é permitido: o nome e o valor enviado são os mesmos | Diff do POST de cada etapa, antes e depois, no mesmo rascunho: **idêntico** nas chaves e nos valores |
| **D-3** | **F1, o stepper:** as 9 etapas **numa linha** a partir de 1280 px, cada uma com número, nome e situação em texto (a situação continua legível, não vira só cor ou ícone). Abaixo da largura que não comporta, pode quebrar, mas em linhas **de largura igual** — nunca 7 + 2 com as duas últimas esticadas | A 1280 px, stepper com **≤ 80 px** de altura (hoje 174). Em Perfis, o h2 da etapa sobe de y=524 para **≤ 440** |
| **D-4** | **F2, as coleções em cartão** (Evento, Etapa, Documento exigido, Modalidade). As ações ↑ ↓ 🗑 saem da linha própria e vão para a **linha da legenda**, à direita. A legenda passa a carregar o identificador do item ("Evento 1 — Inscrições", "Modalidade PPP"), como o Retificar já faz, mantendo o "N de M" quando existir. **Não** vira tabela editável | Nenhum cartão com linha dedicada só a ações. Cartão de Evento do Cronograma de ~230 para **≤ 150 px** |
| **D-5** | **F2, o Cronograma:** Tipo, Descrição, Início e Término **na mesma linha**; "Onde acontece" na linha de baixo. A Descrição (obrigatória) passa a ter a maior parte da largura | Início e Término com o mesmo `top`. Descrição mais larga que "Onde acontece" |
| **D-6** | **F3, o Conteúdo do Edital:** o cartão tem a largura do texto (`--leitura`), não a da página. Textarea **vazia** nasce com 2 ou 3 linhas; a preenchida, com a altura atual. Seção **gerada** em uma linha só (título e "composta a partir de X"), sem caixa de 121 a 139 px. O sufixo "(VAZIA — NÃO SAI NO DOCUMENTO)" vira marcador curto — **o texto do marcador pode encurtar, mas a informação "não sai no documento" continua visível** | Página de 4.790 px para **≤ 3.000 px** no Edital 76/2027 do seed |
| **D-7** | **F4, a Revisão:** "Rótulo: valor" em texto corrido vira `dl` em grade, reusando uma grade de `dl` que a folha já tenha (a de "Dados da inscrição" serve). **Não** muda o conteúdo nem a ordem do que a Revisão mostra, e não mexe em número nem data (isso é a `057`) | Nenhuma linha "Rótulo: valor" em texto corrido: os rótulos formam uma coluna alinhada. A altura (7.987 px) não cresce mais de 10% — o ganho aqui é leitura, não altura |
| **D-8** | **F5 e D4.** Texto longo vira textarea de 2 linhas, onde a auditoria mediu: "Descrição" do Perfil, "Instrução ao candidato" do Documento exigido, e Título, Descrição e Declaração do Requerimento no Retificar. D4: a etapa Anexos usa as mesmas larguras das outras etapas | Nenhum desses campos trunca o valor do seed. No Anexos, "Avançar" na mesma posição horizontal das outras etapas |
| **D-9** | **F6, só se sobrar margem e sem risco:** a ordem dos campos do Perfil no Retificar segue a do Compor (Código ou Denominação primeiro, Requisitos depois). Se `retificacao.js` ou um teste depender da ordem, **o item sai** e vira registro | Ordem igual à do Compor, ou registro dizendo por que não |

**O que esta feature não faz, por decisão:**
- não cria tabela editável, mestre-detalhe nem padrão de interação novo;
- não muda o que se grava nem o nome de campo algum;
- não mexe em texto de ajuda além do marcador de seção vazia (D-6);
- não toca Perfis e Classificação além de Modalidades e do Descrição (a visão do conjunto da
  `052`/`053` fica como está);
- não mexe no PDF.

---

## AS RESTRIÇÕES QUE O CÓDIGO IMPÕE

**O teto de 120.000 caracteres fica.** Ele mede o HTML **inteiro** da distribuição
(`tests/performance/test_escala_da_mesa.py:326`).
- **Registre o tamanho da página antes e depois**: rode o teste isolado, imprima `len(corpo)` e
  grave os dois números em `verificacao.md` e na descrição do PR.
- **Está autorizado** converter os comentários CSS **puramente documentais** de `/* … */` para
  `{% comment %}…{% endcomment %}`. A explicação continua no código e deixa de ir no HTML. O texto do
  comentário é o mesmo; só muda o delimitador.
- **Não apague documentação e não altere regra CSS só para reduzir tamanho.** Comentário que não é
  puramente documental (uma regra desativada, por exemplo) fica como está e é listado em
  `verificacao.md`.
- Os testes que leem a folha crua já tratam as duas formas como prosa (`sem_prosa` em
  `tests/interface/test_acessibilidade.py`). Os que leem o `<style>` renderizado deixam de ver o
  comentário: se algum deles afirmava sobre o texto de um comentário, o teste lia documentação como
  se fosse regra. Registre o caso no `research.md` e ajuste o teste para ler o arquivo-fonte, **sem
  mudar o que ele verifica**.
- **Confira se a folha da gestão ainda tem `/* … */` documental.** A `055` (PR 242) rodou antes
  desta autorização e **não converteu**: fechou com 119.884 caracteres, 116 de margem. Se a
  conversão ainda não estiver na `main`, ela é a **primeira tarefa** da implementação, num commit
  só dela, antes de qualquer regra mudar. Sem ela, este lote não cabe no teto.
- Comentário novo nasce como `{% comment %}`. A mesma autorização vale para qualquer outra folha
  que você tocar.
- Regras que o lote torna mortas (a linha de ações do cartão, o flex do stepper) saem junto.
- Estilo que só uma etapa usa vai para o `{% block estilo_da_pagina %}` dela, que não pesa na
  distribuição.

**Prosa de comentário de CSS sem tag HTML.** Toda classe nova precisa de regra. `max-width` só em
rem, ch, % ou token.

**Scripts que localizam elementos.** Se `remocao.js`, `assistente.js` ou `rascunho.js` acharem os
botões ou a legenda por posição ou por seletor de estrutura, ajuste o seletor. **Não mude o
comportamento.** Os testes de JS (`backend/tests/javascript/*.test.js`) rodam dentro da suíte, por
`tests/test_javascript.py`; rode esse arquivo isolado depois de cada ajuste de script.

---

## ROTEIRO

1. **`/speckit-specify --number 56`**, com este documento como entrada.
   - O cabeçalho da spec declara a faixa. Se o teto vier de spec não mergeada, escreva o número por
     extenso.
   - As decisões da spec nascem em **D-001**.
   - Os casos-limite viram FR/SC, porque a seção Edge Cases não entra na matriz.
2. **`/speckit-plan`**, **`/speckit-tasks`** e **`/speckit-analyze`**.
   - Confira que `.specify/feature.json` aponta para `specs/056-…` antes do analyze.
   - A `rastreabilidade.md` é cobrada requisito a requisito.
3. **Medição "antes", antes de tocar template ou folha.**
   - Banco: `createdb -T ps_polish_audit ps_056_polish`, ou `createdb`, `migrate` e `seed_demo` se a
     origem não existir.
   - O Edital de trabalho é o **76/2027** do seed, em elaboração.
   - Servidor: entrada **acrescentada** ao `.claude/launch.json` e revertida antes do commit.
   - Janela: `resize_window` para 1280 × 900.
   - Grave em `specs/056-…/verificacao.md`:
     - a tabela "antes" da auditoria;
     - as medidas das D-3 a D-8;
     - **o POST de cada etapa** (D-2): capture o corpo de "Salvar rascunho" de cada etapa.
4. **`/speckit-implement`.** Uma etapa do assistente por vez. Depois de cada uma:
   - recapture o POST e compare com o de antes;
   - rode `test_acessibilidade` e os testes da etapa.
5. **Suíte:** `cd backend && make lint check test-pg`, com o seu `DB_NAME`. Os testes de JS vêm junto.
   Não edite arquivo durante a suíte.
6. **Medição "depois"**, no mesmo banco.
   - A tabela antes/depois vai para `verificacao.md`, com o diff dos POSTs (que deve ser vazio).
   - Passe por **375 px** no stepper, no Cronograma e no Conteúdo.
   - Screenshots de antes e depois do topo de uma etapa, de um cartão de Evento e do Conteúdo.
7. **Commit e PR.**
   - Na descrição: a tabela antes/depois, o diff vazio dos POSTs, o tamanho da página da distribuição antes e depois, e o
     total da suíte.
   - **Não faça merge.**

---

## QUANDO PARAR

- **A `055` não está na `main`.** Pare antes do specify.
- **Um POST muda** (chave ou valor) e a causa não se resolve sem tirar ou renomear campo. O item sai
  do lote, o código dele é revertido, e vira registro.
- **O teto de 120K não comporta o lote**, mesmo com os comentários convertidos. Entregue na ordem F1, F3, F2, F4, F5, D4, F6 e registre o
  que faltou.
- **Um teste existente exige mudar comportamento, texto ou domínio** para o item passar. O item sai,
  e o conflito vira registro.
- **Uma medida piora em outra tela** e a correção exige mexer fora do escopo. Reverta e registre.

Em qualquer caso, o que já estiver verde segue para o PR. Parar não é perguntar.

---

## O TESTE QUE A FEATURE PRECISA PASSAR

Medido no Edital 76/2027 do seed, a 1280 × 900, antes e depois:

1. **Stepper:** numa linha, com **≤ 80 px** de altura; em Perfis, o h2 da etapa em **y ≤ 440**.
2. **Cronograma:** Início e Término lado a lado; cartão de Evento **≤ 150 px**; Descrição mais larga
   que "Onde acontece".
3. **Coleções:** nenhum cartão de Evento, Etapa, Documento ou Modalidade com linha só de ações; toda
   legenda diz de qual item se trata.
4. **Conteúdo do Edital:** **≤ 3.000 px**, e toda seção vazia continua dizendo que não sai no
   documento.
5. **Revisão:** em grade de rótulo e valor, sem crescer mais de 10%.
6. **Texto longo:** Descrição do Perfil, Instrução ao candidato e os três campos longos do Retificar
   sem truncar.
7. **Anexos:** "Avançar" na mesma posição das outras etapas.
8. **Gravação:** o POST de "Salvar rascunho" de **cada etapa** é idêntico antes e depois.
9. **Suíte:** `make lint check test-pg` verde, com os testes de JS; HTML da distribuição abaixo de 120.000
   caracteres, com o tamanho antes e depois registrado.

E o que o teste **não** cobre, deliberadamente:
- a tabela editável do Cronograma (análise de 29/09, P2);
- o seletor de Modalidade agrupado por Perfil nos Documentos (P3 daquela análise);
- o tamanho do Retificar (é estrutural, e está registrado);
- números em formato pt-BR (é a `057`).

---

## ARMADILHAS OPERACIONAIS

- **Painel oculto do navegador tem viewport zero.** `resize_window` 1280 × 900 antes de medir.
- **Viewport emulado desalinha cliques.** Para "Salvar rascunho" e "Avançar", use `javascript_tool`
  (`botão.click()`), e confira o POST em `read_network_requests` ou `preview_logs`.
- **O preview reusa JS em cache.** Depois de editar um script, recarregue com cache ignorado antes
  de medir.
- **O `confirm()` nativo é suprimido no painel.** Remover uma linha preenchida vira no-op silencioso.
  Esvazie os campos antes, ou teste a remoção pelos testes de JS.
- **`levar_a_publicacao` sem rascunho regrava o mínimo.** Teste que publica pode passar sem exercitar
  a etapa que você mudou.
- **`sed` do macOS ignora `\b`.** Renome em massa se faz em Python.
- **Matar o `make` deixa pytest órfão.** A próxima suíte disputa o banco.
