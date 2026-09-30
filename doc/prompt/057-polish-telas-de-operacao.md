# 057 — Polish das telas de operação

**Prompt de sessão autônoma: da spec ao PR, sem parar para perguntar.** Escrito em 30/09/2026 a
partir da [auditoria de polish](../auditoria-polish-ui-2026-09-30.md), sobre a `main` em `ed9b13ca`.
É o **lote 3 de 3** da proposta de execução da auditoria (§9):

- o lote 1 é a [`055`](055-polish-folha-e-componentes.md), folha e componentes;
- o lote 2 é a [`056`](056-polish-assistente-de-composicao.md), assistente de composição.

**A frase que governa:**

> Em cada tela, a ação que se pratica todo dia é a mais visível, a excepcional é a mais discreta, e a
> destrutiva nunca é a mais forte.

**E a frase que mantém o corte:**

> Esta feature reordena, recolhe e formata o que já está na tela. Não acrescenta ação, não remove
> ação, não muda permissão nem o que cada ação faz.

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

1. **A `055` e a `056` precisam estar na `main`.**
   - Confira se `specs/055-*` e `specs/056-*` existem em `origin/main`.
   - Se faltar qualquer uma, **pare antes do specify** e diga qual falta.
   - O motivo: as três dividem a mesma folha e o mesmo teto de 120.000 caracteres, e este lote parte
     dos botões e títulos que a `055` acertou.
2. **Worktree própria a partir da `main` atualizada.**
3. **Número e faixas: meça de novo.**
   - Esta é a **`057`**, e o número vem de **`--number 57`**.
   - A faixa abre logo acima do teto que a `056` deixar.
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
  - A seção 6 inteira (T1 a T4), o F8 da seção 5 e o D2 e o D5 da seção 7 — a matéria deste lote.
  - O D3, com a conferência de 30/09: **não é do produto** e não entra.
  - A seção 9 e a tabela "antes".
- **A `specs/055-*` e a `specs/056-*`**: o que já foi acertado não se refaz.
- **As telas**, em `backend/processo_seletivo/interface/templates/interface/`:
  - `lista.html` com `_linha_do_edital.html`: a coluna "O que posso fazer";
  - `detalhe.html`: "Quem atuou" e "O que fazer agora";
  - o glossário repetido ("**Recorte** é a lista em que a pessoa concorre…"), em oito templates:
    `marco.html` (é ele que desenha a condução), `ordenacao.html`, `corte.html`,
    `corte_historico.html`, `ocupacao.html`, `convocacao.html`, `convocacao_historico.html` e
    `sorteio.html`. Mais o de `matriculas.html`, que é outro ("Geração", "Faixa");
  - `compor_perfis.html` tem o mesmo glossário e **não entra**: é do assistente, a `056`;
  - `processo_detalhe.html` e `supervisao.html`: a seção "Atenção", com `_sinal.html`;
  - `auditoria.html`;
  - `inscricao_detalhe.html` com `_documento.html`: comparar com a lista de documentos de
    `mesa_inscricao.html`, que é o modelo;
  - `distribuicao.html` e `minha_etapa.html`: as fichas de largura total;
  - `alocacoes.html`: o cabeçalho da matriz. Leia o comentário de `.distribuicao-moldura` na folha
    da gestão, l. 433 a 446, **antes** de mexer nela.
- **O padrão de ajuda recolhida que já existe:** `details.como-preencher` e o
  `_como_preencher_o_marco.html`.
- **Os formatadores que já existem**, e que este lote reaproveita em vez de criar outro:
  - `pontuacao` em `interface/templatetags/interface_extras.py:148`: decimal sem zeros à direita,
    com vírgula, sem arredondar;
  - `plural`, no mesmo arquivo, l. 88.
- **As fontes do F8:**
  - `interface/revisao.py:111` (percentual), `:310` (peso), `:312` (nota mínima), e os `vaga(s)`
    em `revisao.py`, `retificacao.py`, `supervisao.py` e `conducao_do_marco.py`;
  - o mesmo problema no valor dos campos numéricos da etapa Etapas ("2,0000").
- **O portal:** o bloco de envio de documento em `portal/templates/portal/inscricao.html` e os
  parciais `_documentos*.html`.
- **Os testes que guardam a folha e as telas:**
  - `tests/interface/test_acessibilidade.py`;
  - `tests/interface/test_larguras.py`;
  - `tests/performance/test_escala_da_mesa.py:326`, o teto de 120.000 caracteres;
  - `tests/test_vocabulario_da_composicao.py`, que confere termo em **texto visível**;
  - `tests/test_citacoes_de_requisito.py`;
  - o inventário de negativas da `033`, se alguma view for tocada.
- `CLAUDE.md` e a Constituição.

---

## AS DECISÕES FECHADAS

Cada uma traz o **critério mensurável** que resolve a dúvida que ela não previu.

| | Decisão | Critério |
|---|---|---|
| **D-1** | **Escopo:** T1, T2, T3, T4, D2, D5 e F8 da auditoria. **D3 não entra**: a conferência de 30/09 mostrou que a repetição vem do título do `seed_demo`, não da interface. Nada dos lotes 1 e 2 | O item está na lista? Então entra. Não está? É registro |
| **D-2** | **Nenhuma ação acrescentada nem removida, nenhuma permissão mudada.** A tela oferece exatamente as mesmas ações ao mesmo papel, e cada uma leva ao mesmo lugar. O que muda é ordem, agrupamento e peso visual | Para cada tela tocada, a lista de `href` e `formaction` de ações, por papel, é **idêntica** antes e depois |
| **D-3** | **T2, o grupo de ações** (Detalhe do Edital, Condução do marco). **Uma** ação primária por estado, a que o fluxo pede a seguir. As demais são secundárias, em linha e com quebra, não uma por linha. As destrutivas e irreversíveis (Encerrar, Cancelar) ficam **separadas e por último**, **contornadas e nunca preenchidas**, com o marcador "IRREVERSÍVEL" que já existe. As colunas do Detalhe alinham pelo topo | Nenhuma tela com botão destrutivo preenchido quando há ação não destrutiva. "Quem atuou" com a altura do próprio conteúdo (hoje 515 px para ~160) |
| **D-4** | **T1, a coluna da Lista de Editais.** Mesma regra da D-3, em linha: frequentes primeiro, destrutivas no fim e separadas. Encurtar rótulo **só** se nenhum teste o prender; se prender, o texto fica e só a ordem muda. Contador zero esmaecido, mas presente | Linha da Lista de **125 para ≤ 90 px** a 1280 px |
| **D-5** | **D2, o glossário repetido.** "Recorte é…, Faixa é…, Geração é…" vai para um `details` no padrão `como-preencher`, **fechado**, no mesmo lugar, nos oito templates de marco listados no contexto, e o de `matriculas.html` também. `compor_perfis.html` fica como está. A faixa "abrir esta tela não pratica nada" **fica visível**: é garantia ao operador, não glossário. O texto não muda | O primeiro controle ou a primeira tabela de cada tela sobe **≥ 120 px**. `test_vocabulario_da_composicao` verde |
| **D-6** | **T3, caixa dentro de caixa.** "Atenção" (Processo e Supervisão) vira lista com divisor, com a faixa **âmbar** do aviso e não a verde. A Auditoria vira lista de eventos com divisor, sem cartão por evento. Os documentos apresentados de `inscricao_detalhe` adotam o desenho da mesa do avaliador. Fichas de 2 ou 3 dados (Distribuição, Minha etapa) ficam na largura do conteúdo | Auditoria do Edital 51/2026 com altura média por evento **≤ 70 px** (hoje 97). Nenhuma caixa com borda dentro de outra nessas telas |
| **D-7** | **F8, números, datas e plurais na interface.** Reaproveite `pontuacao` e `plural`. Datas em dd/mm/aaaa. Vale **só para texto que a interface compõe para ser lido na tela**. Não toca: <ul><li>conteúdo canônico ou publicado;</li><li>o renderizador do PDF;</li><li>texto que vá para o "o que mudou" publicado de uma Retificação;</li><li>valor enviado por formulário.</li></ul>Antes de trocar cada `vaga(s)`, confira para onde a string vai; se ela sair da tela, fica e vira registro | Na Revisão do 76/2027: "Peso: 2", "Nota mínima: 6", "20%", "versão 09/06/2014", "2 vagas imediatas". O POST das etapas continua idêntico |
| **D-8** | **T4, a matriz de Alocação.** Mantém a decisão registrada: sem rolagem interna em tela larga, com o cabeçalho fixo. O que muda é a **largura das colunas**: o número do Edital vira linha de grupo sobre as suas Etapas, e os controles do cabeçalho ("Distribuir", "Todos · Nenhum") ficam mais compactos | A 1280 px, com as 9 Etapas do seed: largura da página de **1.398 para ≤ 1.280 px**, e altura do `thead` de 174 para **≤ 130 px** |
| **D-9** | **D5, envio de documento no portal.** Seletor, nome do arquivo e "Enviar" numa linha, com a dica de formato junto do seletor. O comportamento de `arquivo.js` e `envio.js` não muda | Bloco de cada documento com **uma** linha de controles a 1280 px. A 375 px pode quebrar |

**O que esta feature não faz, por decisão:**
- não acrescenta nem remove ação, e não muda permissão;
- não muda o título do `seed_demo` (o D3 fica como está);
- não toca o PDF nem o conteúdo publicado;
- não mexe no assistente de composição, que é a `056`, além da formatação da Revisão (D-7).

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
- Regra que o lote torna morta (cartão de sinal, cartão de evento de auditoria, a faixa verde da
  Atenção) sai junto.
- Estilo de uma tela só vai para o `{% block estilo_da_pagina %}` dela.

**A distribuição é a tela medida pelo teto.** Mexer na Distribuição (fichas, D-6) mexe no próprio
número. Meça o teto de novo depois dessa tarefa, e não só no fim.

**Prosa de comentário de CSS sem tag HTML.** Toda classe nova precisa de regra. `max-width` só em
rem, ch, % ou token.

**404 novo reprova o inventário da `033`.** Este lote não deveria criar view nem `Http404`. Se criar,
é sinal de que saiu do escopo.

---

## ROTEIRO

1. **`/speckit-specify --number 57`**, com este documento como entrada.
   - O cabeçalho da spec declara a faixa. Se o teto vier de spec não mergeada, escreva o número por
     extenso.
   - As decisões da spec nascem em **D-001**.
   - Os casos-limite viram FR/SC, porque a seção Edge Cases não entra na matriz.
2. **`/speckit-plan`**, **`/speckit-tasks`** e **`/speckit-analyze`**.
   - Confira que `.specify/feature.json` aponta para `specs/057-…` antes do analyze.
   - A `rastreabilidade.md` é cobrada requisito a requisito.
3. **Medição "antes", antes de tocar template ou folha.**
   - Banco: `createdb -T ps_polish_audit ps_057_polish`, ou `createdb`, `migrate` e `seed_demo` se a
     origem não existir.
   - Os Editais de trabalho são o **51/2026** (concluído, com marco, corte, ocupação e convocação),
     o **01/2026** (publicado, inscrições abertas) e o **76/2027** (Revisão).
   - Servidor: entrada **acrescentada** ao `.claude/launch.json` e revertida antes do commit.
   - Janela: `resize_window` para 1280 × 900.
   - Grave em `specs/057-…/verificacao.md`:
     - a tabela "antes" da auditoria;
     - as medidas das D-3 a D-9;
     - **a lista de ações de cada tela tocada, por papel** (D-2): `href` e `formaction` de cada
       botão e link de ação, com `ana.gestora` (todos os papéis) e com `joana.avaliadora`.
4. **`/speckit-implement`.** Uma tela por vez. Depois de cada uma:
   - recapture a lista de ações e compare;
   - rode `test_acessibilidade` e os testes da tela.
5. **Suíte:** `cd backend && make lint check test-pg`, com o seu `DB_NAME`. Os testes de JS vêm
   junto, por `tests/test_javascript.py`. Não edite arquivo durante a suíte.
6. **Medição "depois"**, no mesmo banco.
   - A tabela antes/depois vai para `verificacao.md`, com o diff das listas de ações (que deve ser
     vazio).
   - Passe por **375 px** na Lista, no Detalhe, na Alocação e no envio de documento do portal.
   - Screenshots de antes e depois do Detalhe do Edital, da Lista, da Auditoria e da Alocação.
7. **Commit e PR.**
   - Na descrição: a tabela antes/depois, o diff vazio das ações, o tamanho da página da distribuição antes e depois, e o
     total da suíte.
   - **Não faça merge.**

---

## QUANDO PARAR

- **A `055` ou a `056` não está na `main`.** Pare antes do specify.
- **A lista de ações de uma tela muda** e a causa não se resolve sem acrescentar, tirar ou mudar
  ação. O item sai do lote, o código dele é revertido, e vira registro.
- **Uma string do F8 sai da tela** (vai para conteúdo publicado, PDF ou "o que mudou"). Ela fica
  como está, e vira registro.
- **O teto de 120K não comporta o lote**, mesmo com os comentários convertidos. Entregue na ordem T2, T1, D2, F8, T3, T4, D5 e registre o
  que faltou.
- **Um teste existente exige mudar comportamento, texto ou domínio** para o item passar. O item sai,
  e o conflito vira registro.
- **Uma medida piora em outra tela** e a correção exige mexer fora do escopo. Reverta e registre.

Em qualquer caso, o que já estiver verde segue para o PR. Parar não é perguntar.

---

## O TESTE QUE A FEATURE PRECISA PASSAR

Medido no mesmo banco, a 1280 × 900, antes e depois:

1. **Detalhe do Edital 01/2026:** uma ação primária; Encerrar e Cancelar separados, por último,
   contornados; "Quem atuou" na altura do próprio conteúdo.
2. **Condução do marco:** uma ação primária, não quatro.
3. **Lista de Editais:** linha com **≤ 90 px**, destrutivas no fim.
4. **As telas de marco e a de matrículas:** o glossário fechado num `details`, a faixa "não pratica
   nada" visível, e o primeiro controle **≥ 120 px** mais alto.
5. **Processo e Supervisão:** "Atenção" em lista com divisor e faixa âmbar.
6. **Auditoria:** **≤ 70 px** por evento, em média.
7. **Detalhe da inscrição:** documentos no desenho da mesa do avaliador.
8. **Revisão do 76/2027:** "Peso: 2", "20%", "09/06/2014", sem "(s)".
9. **Alocação:** a página não passa de 1.280 px de largura; `thead` com **≤ 130 px**.
10. **Portal:** cada documento com uma linha de controles.
11. **Ações:** a lista por papel é idêntica antes e depois, em toda tela tocada.
12. **Suíte:** `make lint check test-pg` verde; HTML da distribuição abaixo de 120.000 caracteres,
    com o tamanho antes e depois registrado.

E o que o teste **não** cobre, deliberadamente:
- a duplicação do número do Edital no cabeçalho (D3: é do seed);
- o tamanho do Retificar e a repetição entre Processo e Supervisão (estruturais, registrados);
- qualquer mudança no PDF.

---

## ARMADILHAS OPERACIONAIS

- **404 na gestão costuma ser autorização**, não rota quebrada. Reproduza com o papel exato antes de
  caçar URL.
- **Painel oculto do navegador tem viewport zero.** `resize_window` 1280 × 900 antes de medir.
- **Viewport emulado desalinha cliques.** Para agir, use `javascript_tool` (`botão.click()`).
- **O `batch` do navegador pode ler a página anterior.** `get_page_text` logo depois de um clique que
  redireciona devolve a tela antiga.
- **Cookie de `localhost` não separa porta.** Outro `runserver` derruba a sessão da gestão.
- **`navigate` depois do código de acesso derruba a sessão do portal.** Para o envio de documento,
  use a candidata `MARIA` do fixture (`registrar(MARIA)`, `m@ex.br`) e navegue **por cliques**. O
  código sai em `preview_logs`.
- **Para trocar de papel na gestão**, use o botão "Sair" do cabeçalho (é POST) e entre de novo pelo
  seletor de identidade.
- **`sed` do macOS ignora `\b`.** Renome em massa se faz em Python.
- **Matar o `make` deixa pytest órfão.** A próxima suíte disputa o banco.
