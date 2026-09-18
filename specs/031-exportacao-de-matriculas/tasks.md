# Tasks: Exportação de matrículas

**Spec**: [spec.md](./spec.md) · **Plan**: [plan.md](./plan.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivos distintos, sem dependência pendente
- **[Story]**: a que user story pertence (`US1` a `US4`)
- Caminho de arquivo exato em toda tarefa

## Path Conventions

Monólito Django. Código em `backend/processo_seletivo/`, testes em `backend/tests/`.

**O que esta feature acrescenta**: um app (`matriculas/`), **uma** tabela, uma permissão, uma
dependência, três campos em `requerimentos.RequerimentoDeMatricula` e o fechamento de uma lista que
já existia aberta. **O que ela não acrescenta**:
nenhum estado novo, nenhuma etapa no assistente, nenhum acervo de arquivo.

**Banco próprio nesta worktree**: `DB_NAME=ps_demo_031`, e **como variável do Make** —
`make DB_NAME=ps_demo_031 …`, nunca `DB_NAME=ps_demo_031 make …`. O `Makefile` faz `include .env`
seguido de `export`, e `include` sobrepõe variável de ambiente.

**`TABELAS_APPEND_ONLY` muda, e este é o número.** `GeracaoDeArquivo` é registro de ato e entra na
tupla de `seguranca/papeis.py` na mesma leva da migration. O provisionamento passa a dizer
**`32 de 32`** — e o primeiro número vindo `0` continua sendo a armadilha, não o total.

**`make test-pg`, sempre.** A recusa por privilégio e a trigger de append-only não são exercidas no
modo padrão da suíte.

---

> **Estado em 18/09/2026, depois da revisão de código.** Tudo o que este repositório alcança está
> feito e verde: `make DB_NAME=ps_demo_031 lint check test-pg` fecha em **7089 passando e 13
> pulados**, e `make provisionar` diz **32 de 32**.
>
> **A revisão encontrou sete defeitos, e os sete estão corrigidos** — três deles bloqueantes, e os
> três eram da mesma família: a feature decidia **sozinha** o que a spec não tinha fechado.
> A população admitia resultado preliminar, publicação já sucedida e quem ficou sem posição; a
> composição lia a norma **vigente** em vez da que o ato citou (Princípio II), o que fazia uma
> Modalidade removida por Retificação recusar a geração de quem concorreu por ela; e o download
> não tinha vínculo nenhum com o resumo que a `UX-060` manda ler antes. As três regras estão
> escritas em `contracts/arquivo-de-importacao.md`, e cada uma tem teste próprio em
> `tests/integration/matriculas/test_populacao.py` e `test_recusas.py`. Continuam abertas as quatro tarefas que **não
> são deste repositório** — a conversa com o Registro Acadêmico (`T001`–`T003`) e a importação real
> (`T038`) —, exatamente as que a §5 da spec mede como gate da aceitação, e não da construção.
>
> **O que a resposta da `Q-1` ainda pode mudar**: três células e os testes que as prendem. A
> `T017d` (`CLASSIF_CURSO_FINAL`) e a lista `CODIGOS_DO_DESTINO` em `domain/colunas.py` são os dois
> pontos em que a resposta entra.

## Phase 0: A pergunta externa — feita cedo, **sem parar a fila**

- [ ] **T001** Obter do Registro Acadêmico a resposta de `Q-1`: o importador aceita célula vazia em
  `COD_CURSO`, `COD_TURNO`, `COD_POLO` e `COD_NACIONALIDADE`? Enviar **duas linhas sintéticas** —
  nunca a linha `2` da amostra (`D-006`) — e registrar a resposta na spec
- [ ] **T002** Na mesma conversa, perguntar `Q-3` (o importador aceita protocolo opaco
  `INS-2026-K7M4Q2PX`?), `Q-2` (`CLASSIF_CURSO_FINAL` é classificação ou numeração de linha?) e
  **`Q-7` (a coluna 16 usa ISO 3166-1 alpha-2?)**, e confirmar `R-1`: o que o destino espera para
  quem declarou cor **indígena**. As quatro perguntas custam uma conversa só, e `Q-7` custa uma
  frase — se a resposta for sim, a `D-008` se simplifica e a coluna 16 sai exata também para
  estrangeiro
- [ ] **T003** Registrar as respostas em [spec.md](./spec.md) §15, fechar as questões e ajustar o
  que elas mudarem — `T017c` e `T017d` são as tarefas que dependem delas.

  **Esta tarefa não segura as demais.** A primeira redação dizia que nenhuma começava antes dela, e
  §5 da spec mede por que era largo demais: se a `Q-1` responder *"não aceita"*, o retrabalho são
  três dos 34 serializadores. Perguntar cedo continua certo; esperar pela resposta, não

## Phase 1: Setup

- [X] **T004** Acrescentar `openpyxl` a `backend/pyproject.toml` e rodar `uv sync --extra dev`,
  registrando a razão no cabeçalho de `infrastructure/planilha.py` (plan.md, *Complexity Tracking*)
- [X] **T005** Criar o app `backend/processo_seletivo/matriculas/` — `__init__.py`, `apps.py`,
  `domain/nomes.py` — e registrá-lo em `INSTALLED_APPS`

## Phase 2: Foundational (Blocking Prerequisites)

- [X] **T006** `[US1]` Acrescentar `titulo_eleitoral`, `zona_eleitoral` e `secao_eleitoral` a
  `backend/processo_seletivo/requerimentos/models.py`, guardados **sem pontuação** como o CEP já é,
  e a migration `requerimentos/0005_campos_eleitorais.py` (`D-007`, `FR-451`)
- [X] **T007** `[US1]` Estender `requerimentos/domain/declaracao.py` com o saneamento dos três —
  dígitos apenas, comprimentos 12/3/4, e a recusa **sem repetir o valor rejeitado** (`FR-401` da
  `029`)
- [X] **T008** `[US1]` Rótulos e descritores dos três campos em `requerimentos/domain/rotulos.py` e
  `portal/requerimento.py`, no grupo *Documento de identidade* — e conferir que o ENTER continua
  percorrendo a ordem certa (`D-007`)
- [X] **T008b** `[US1]` Fechar a lista de `nacionalidade` na `029` (`D-008`): entrada em
  `requerimentos/domain/nomes.py` e `rotulos.py`, em `declaracao.py::LISTAS`, e a migration de
  conversão do texto livre existente — **`Brasil` reconhecido, o resto preservado como declarado
  até alguém conferir**, porque converter à força apagaria declaração de quem já enviou
- [X] **T009** `[P]` Criar `matriculas/models.py::GeracaoDeArquivo` — Edital, população, quantidade,
  autor, instante, **versão do resultado** e **versão dos mapeamentos** — e
  `migrations/0001_geracao.py` (`FR-447`)
- [X] **T009b** `[P]` Declarar `VERSAO_DOS_MAPEAMENTOS` em `matriculas/domain/colunas.py` como
  constante alterada à mão, no molde de `SCHEMA_VERSION`, com o comentário dizendo **por que não é
  derivada do arquivo**: um resumo criptográfico mudaria também quando só um comentário mudasse
  (`FR-454`)
- [X] **T010** Acrescentar a tabela a `seguranca/papeis.py::TABELAS_APPEND_ONLY` **na mesma leva**, e
  confirmar que `make provisionar` diz `32 de 32` (`FR-447`)
- [X] **T011** `[P]` Criar a permissão `matricula:exportar` no catálogo de permissões, sem concedê-la
  a papel nenhum por padrão (`FR-455`, Princípio *negar por padrão*)

## Phase 3: User Story 1 — O arquivo de um Edital, sem redigitar nada (P1)

- [X] **T012** `[P]` `[US1]` `matriculas/domain/flexao.py`: a tabela de 8 strings da `D-004`, com
  teste unitário que percorre os 4 estados × 2 sexos (`FR-442`)
- [X] **T013** `[US1]` `matriculas/domain/colunas.py`: as **34** colunas, cada uma com nome exato do
  cabeçalho, origem, serializador e comportamento na ausência (`FR-445`). Uma função por coluna —
  **nunca** `legivel()` genérico
- [X] **T014** `[P]` `[US1]` Teste unitário por coluna em `backend/tests/unit/matriculas/`, cobrindo
  o caso normal e o vazio (`FR-445`). É a fase em que o erro silencioso morre
- [X] **T015** `[US1]` `COD_FORMA_INGRESSO`: ausência de Modalidade → `AC`; com Modalidade → o `code`
  publicado, sem reescrita (`FR-443`, `D-003`)
- [X] **T016** `[US1]` `RENDA_PER_CAPITA_PNP` recebe `renda_familiar_faixa` sem conversão (`D-002`),
  e o serializador **cita a decisão no docstring** — é a coluna que alguém vai tentar "consertar"
- [X] **T017** `[P]` `[US1]` `TITULO_ELE`, `ZONA_ELE`, `SECAO_ELE` na forma do destino, com zeros à
  esquerda (`FR-451`, `SC-152`)
- [X] **T017b** `[P]` `[US1]` `COD_NACIONALIDADE`: `BR` para Brasil, vazia e nomeada para os demais
  (`FR-453`, `SC-154`). **Sem tabela de países** enquanto `Q-7` não responder
- [X] **T017c** `[US1]` As **três** colunas da `D-001` — `COD_CURSO`, `COD_TURNO`, `COD_POLO` — saem
  vazias, e o teste prova que nenhuma delas recebe valor deduzido (`FR-438`, `SC-145`). É a decisão
  central da spec, e ela precisa de tarefa própria em vez de ficar diluída em T013
- [X] **T017d** `[US1]` `CLASSIF_CURSO_FINAL` sai **vazia e nomeada no relatório** enquanto `Q-2`
  não for respondida, e o serializador **não escolhe** entre classificação e numeração de linha
  (`FR-448`). Quando a `Q-2` responder, esta tarefa vira a implementação da fonte que ela indicar
- [X] **T017e** `[P]` `[US1]` `CEP` com hífen, `CPF` e `CELULAR` sem pontuação (`FR-444`)
- [X] **T018** `[US1]` `matriculas/infrastructure/planilha.py`: `.xlsx` de uma aba
  `Import_ModeloCefor`, 34 cabeçalhos em `A1:AH1` na grafia exata — `ENDEREÇO` e `NÚMERO` acentuados
  —, dados a partir da linha 2, **tudo com formato `@`** (`FR-436`, `FR-437`)
- [X] **T019** `[US1]` Teste de ida e volta: CPF com zero à esquerda, data e CEP sobrevivem à leitura
  do arquivo gerado (`SC-144`)
- [X] **T020** `[US1]` `matriculas/application/populacao.py`: a população explícita, só *enviados*
  (`FR-433`, `FR-434`)
- [X] **T021** `[US1]` `matriculas/application/exportar.py`: permissão (`FR-455`), montagem, ordem
  determinística (`FR-446`), registro da geração (`FR-447`) — e **o arquivo não é persistido**
  (`FR-456`)

## Phase 4: User Story 2 — O que saiu vazio, dito antes de alguém perguntar (P1)

- [X] **T022** `[US2]` `matriculas/domain/lacuna.py`: cada lacuna com coluna, razão e quantidade
  (`FR-439`)
- [X] **T023** `[US2]` O aviso **obrigatório** da coluna 31 em toda geração, inclusive nas sem outra
  lacuna (`FR-452`, `SC-153`)
- [X] **T024** `[US2]` A lacuna nominal de `COR` para quem declarou **indígena** (`FR-440`,
  `SC-146`) — caso de teste próprio, e não efeito colateral
- [X] **T025** `[US2]` A tela mostra o resumo das lacunas **antes** do download (`UX-060`)

## Phase 5: User Story 3 — A geração que se recusa a mentir (P1)

- [X] **T026** `[US3]` Recusa quando alguém da população não tem requerimento enviado, nomeando quem
  falta (`FR-435`, `SC-149`) — **e quando a população fica vazia** porque o Edital não exige
  requerimento, a recusa diz isso, em vez de um arquivo de zero linhas (§9, *Edge Cases*)
- [X] **T027** `[US3]` Recusa quando o `code` da Modalidade é desconhecido, nomeando código e Edital
  (`FR-441`, `SC-147`)
- [X] **T028** `[US3]` A recusa diz o que falta e de quem (`UX-061`), e **a aplicação recusa mesmo
  quando a tela não oferece** — Princípio IV
- [X] **T029** `[US3]` Recusa sem `matricula:exportar`, verificada por acesso direto ao endereço
  (`SC-150`)

## Phase 6: User Story 4 — O mesmo arquivo, duas vezes (P2)

- [X] **T030** `[US4]` Ordem determinística e comparação célula a célula de duas gerações seguidas
  (`FR-446`, `SC-148`)
- [X] **T031** `[US4]` Requerimento sucedido entre gerações: o arquivo traz o **vigente**, e o
  registro guarda qual era (`FR-447`, §9 *Edge Cases*)

## Phase 7: A superfície — sem ela a capacidade não é entregue

**Esta fase não é acabamento.** A Constituição, Princípio VI: *"Uma capacidade que o domínio sustenta
mas que nenhuma interface alcança NÃO DEVE ser considerada entregue"*, e *"demonstrar por chamada
manual aquilo que o canal do ator não oferece NÃO satisfaz esta exigência"*. Sem as tarefas abaixo,
a exportação só existe para quem abre um shell.

- [X] **T031b** `[US1]` Rota de geração em `processo_seletivo/interface/urls.py`, sob o Edital, com a
  verificação de escopo do ator (`FR-455`) — e o 404 indistinguível para quem não tem o Edital, como
  o resto da gestão já faz
- [X] **T031c** `[US1]` View de geração em `processo_seletivo/interface/views.py`: recebe a escolha da
  população, chama `exportar`, devolve o `.xlsx` em resposta de download — **sem gravar o arquivo**
  (`FR-456`)
- [X] **T031d** `[US1]` Template com a escolha da população e o botão, no molde das demais telas de
  gestão do Edital, e a entrada no menu do Edital — **uma capacidade sem porta não é capacidade**
- [X] **T031e** `[US2]` O resumo das lacunas na tela, **antes** do download (`UX-060`), e a recusa
  dizendo o que falta e de quem (`UX-061`)
- [X] **T031g** `[US1]` **Acrescentar a tela nova a `tests/test_vocabulario_da_composicao.py::TELAS`**
  e definir os termos no primeiro uso, dentro de `<dfn>`.

  **A lista daquela varredura é literal, e não por `glob`** — por decisão escrita: uma lista
  calculada deixaria de cobrir a tela que abandonasse o termo. A consequência para esta feature é
  que a tela nova **escaparia da regra em silêncio**, e ninguém veria falha nenhuma.

  E ela usa os termos sem querer: o padrão de *geração* é `\bgerac`, que casa com **"Gerar"** — um
  botão escrito *"Gerar arquivo"* já é uso do termo. *Faixa* aparece no aviso da coluna 31
  (`FR-452`). A regra da `030` (`FR-424`) vale aqui, e é preciso entrar na lista para que ela valha
  de fato
- [X] **T031f** Percurso ponta a ponta pelo canal de quem conduz — entrar na gestão, abrir o Edital,
  escolher a população, ler as lacunas, baixar o arquivo — **sem shell e sem chamada manual**
  (Princípio VI)

## Phase 8: Polish & Cross-Cutting Concerns

- [X] **T032** `[P]` `contracts/arquivo-de-importacao.md`: as 34 colunas com o serializador nomeado
  (`FR-445`),
  e a `D-001` substituindo a citação errada de `Q-3` no
  [contrato de saída da `029`](../029-requerimento-de-matricula/contrato-de-saida.md) (spec §17)
- [X] **T033** `[P]` `quickstart.md` com um cenário por FR
- [X] **T034** `[P]` Conferir que **nenhum** app importa `matriculas` — é a verificação de que a
  feature continua sendo ponta de leitura (plan.md, *Project Structure*)
- [X] **T035** `[P]` Confirmar que a varredura `tests/test_sem_dado_pessoal_da_amostra.py` alcança
  os arquivos novos por `glob` (`SC-151`, `D-006`)
- [X] **T035b** `[P]` **A exportação não escreve nada** além do registro da `FR-447`: teste que conta
  as escritas durante uma geração completa (`FR-449`, `SC-156`). Ler o código não prova — é preciso
  contar
- [X] **T035c** `[P]` **Nenhum arquivo fica no servidor** depois da geração, verificado no
  armazenamento (`FR-456`, `SC-155`)
- [X] **T035d** `[P]` `matriculas/` não faz chamada de rede nem importa cliente de sistema externo
  (`FR-450`) — verificado por varredura, junto da T034
- [X] **T036** Semear em `seed_demo.py` um Edital com convocados de requerimento enviado, incluindo
  **um que declarou cor indígena** (`FR-440`, `SC-146`) — o caso do `R-1` precisa existir para ser
  visto
- [X] **T037** `make lint check test-pg` verde, e `make provisionar` dizendo `32 de 32`
- [ ] **T038** **`SC-143`: gerar e importar de verdade no ambiente do Registro Acadêmico.** É o único
  critério que não se verifica neste repositório, e é o que decide se a feature funciona

## Dependencies

- **T001–T003 primeiro, e em paralelo com o resto.** Elas são uma conversa com gente de fora, e
  atrasar a pergunta é o que custa caro. O que elas **gateiam** é estreito: a `T038` (a importação
  real, `SC-143`), a `T017c` (as três células da `D-001`) e a `T017d` (`CLASSIF_CURSO_FINAL`)
- T006–T008b (campos eleitorais e lista de nacionalidade) antes de T017 e T017b
- T013 antes de T014, T018 e T022 — as colunas são o centro
- T009–T010 juntas: tabela e privilégio na mesma leva, ou o provisionamento reporta errado
- **T031b–T031f depois de T021**, e antes da T037: são elas que tornam a capacidade alcançável
- T017d é reaberta quando a `Q-2` for respondida — a tarefa não morre com o vazio
- T038 por último, e fora deste repositório

## Parallel Execution

`[P]` em **T001–T003** (são conversa, não código), T009/T009b/T011, T012, T014, T017, T017b, T017e, T032–T035, T035b–T035d. O resto é sequencial porque passa por
`colunas.py`.

## Implementation Strategy

**MVP é US1 + US2 mais a Fase 7, e as três juntas.** A superfície não é acabamento: sem rota e
tela, o que existe é uma função que ninguém alcança — e o Princípio VI diz, com todas as letras, que
isso não conta como entregue.

**MVP é US1 + US2, e as duas juntas.** Gerar o arquivo sem o relatório de lacunas entregaria
exatamente o problema que a feature existe para resolver: alguém recebe uma planilha com células
vazias e as preenche do jeito que acha. US3 vem logo atrás porque a recusa é o que separa esta
feature de uma planilha feita à mão; US4 é garantia de operação e pode esperar.
