# Verificação: O andamento diz o que cada providência é (135)

Feita em 09/11/2026, na worktree `135-implementacao-75ef0e`, sobre a spec do PR #440.

## A suíte

`make lint check test-pg` com `DB_NAME=ps135`, 4 workers, com os grupos `dev`, `navegador` e
`assistente` instalados:

- `ruff check` e `ruff format --check`: sem achado;
- `manage.py check` e `makemigrations --check --dry-run`: "No changes detected" — nenhuma migration
  (SC-1466);
- pytest: **17 581 passando, 12 pulados, 1 falha**, em 893 s. Os 12 pulados são os deliberados que o
  `AGENTS.md` descreve para quem tem os dois grupos. A falha era o guardião
  `test_readme_acompanha_o_codigo.py::test_toda_pasta_de_specs_aparece_na_tabela_de_incrementos`: a
  pasta `specs/135-…`, que veio do PR da spec, não estava na tabela de incrementos do README. A
  linha foi acrescentada, e o guardião e a varredura de citações passaram de novo (8 de 8); nenhum
  outro arquivo mudou depois da rodada.

Os casos novos, isolados: 31 puros (`unit/interface/test_andamento_o_que_cada_providencia_e.py`), 3 do
critério (`integration/classificacao/test_listas_sem_concorrente.py`) e 13 de cenário
(`integration/treinamento/test_andamento_dos_cenarios.py`).

**Os testes da `127` e da `133` que mudaram**, e só na entrada: os casos puros de
`unit/interface/test_andamento_situacoes.py` e `test_andamento_composicao.py` montavam a célula da
publicação só com a nota ("resultado preliminar"). Com a FR-4679, quem decide é a natureza, e eles
passam a informá-la (`"natureza": "PRELIMINAR"`, ou `divulgado=a.PRELIMINAR` nas células prontas). A
expectativa de cada um é a mesma.

## Depois da revisão do PR #441

Sete achados, corrigidos no mesmo PR (T026 a T031 em [tasks.md](tasks.md)). O que muda para quem lê:

- a frase da lista vazia passou a **"Emitir a ordem que declara que ninguém concorreu nesta lista"**,
  e a nota a **"lista em que ninguém concorre"**. A tabela abaixo registra o que se viu **antes** da
  troca, com a frase antiga; a nova foi conferida pelo HTML da página do C08
  (`test_c08_a_pagina_do_edital_diz_que_ninguem_concorre_no_nivel_1_e_na_matriz`), e não de novo no
  navegador;
- com o preliminar publicado e a janela aberta sem data conhecida, a espera diz "O prazo recursal
  deste marco ainda está aberto", sem a oferta;
- duas ordens sucessoras vazias juntadas vão ao plural.

O custo da pergunta caiu: o conteúdo já lido é repassado à condição do corte, e o marco que espera
Etapas não pergunta nada. O resultado da suíte depois das correções está no fim deste arquivo.

## No navegador

Um banco próprio, `ps135_cenarios`, com os cenários C04, C06, C08, C12 e C14 da `134` carregados
pelo gerador (rodada 1), e um `runserver` da worktree na porta 8135 com o seletor de demonstração. O
roteiro está em [quickstart.md](quickstart.md); a entrada do `launch.json` usada não foi versionada.

| Cenário | Quem | O que se viu |
|---|---|---|
| C08 | `treino.presidencia` | "O que fazer agora": **Sua** *Emitir a ordem da lista sem inscritos, que declara que ninguém concorreu — Professor de Informática · PPP*; a espera do definitivo: *"O prazo recursal deste marco ainda está aberto: ele se encerra em 14/11/2026 às 23h59. O resultado preliminar já está publicado, e o definitivo vem depois do encerramento."* — sem "publique como resultado preliminar" em lugar nenhum da página. Na matriz, a ordem da PPP é **● Pendente** com a nota *lista sem inscritos*; o resultado da ampla, **◷ Aguarda** com *resultado preliminar*. O resumo do Perfil termina em *3 providências em aberto nos marcos*. |
| C08 | `treino.presidencia` | O link da providência leva à tela da ordenação da PPP, que diz *"Ninguém concorreu por este recorte"* e oferece "Emitir ordem": o mesmo critério. |
| C08 | `demo.publicador` | A prévia de publicação do ato da ampla continua dizendo *"… ele se encerra em 14/11/2026 às 23h59. Aguarde o encerramento, ou publique como resultado preliminar."* — a mensagem da aferição, intacta (FR-4682). |
| C12 | `treino.presidencia` | **Sua** *Emitir a ordem da lista sem inscritos, que declara que ninguém concorreu — · PPP*; a espera do definitivo com a segunda redação, sem a oferta; a PPP **● Pendente** *lista sem inscritos* na matriz. |
| C04 | `demo.publicador` | *Quem conduz a seleção: emitir a ordem — Professor de Informática · Ampla concorrência e PPP*, sem menção a lista vazia (SC-1461). |
| C06 | `treino.presidencia` (teste) | O cartão diz *2 providências em aberto · 2 são suas*, e o resumo do Perfil *1 providência em aberto nos marcos* (SC-1464). |
| C14 | `demo.publicador` | *Quem conduz a seleção: emitir a ordem da lista sem inscritos, que declara que ninguém concorreu — Professor de Informática · PPP*; o resumo termina em *2 providências em aberto nos marcos*. |

## O que não foi coberto

- **O "Próximo nesta lista" na tela**, depois de um ato real: emitir a ordem da PPP no banco dos
  cenários mudaria o cenário. A transição lê a mesma célula pela mesma função (`andamento.da_lista`),
  e o teste `test_c08_o_proximo_nesta_lista_diz_a_mesma_frase` prova que a frase é a da providência.
- **O recurso pendente** (FR-4681, segundo caso) não existe em nenhum cenário da `134` com o
  preliminar publicado: está provado nas funções puras.
- **R-006** (o resumo conta o preliminar com a ordem obsoleta como publicado) é uma consequência da
  FR-4679 que a spec não nomeia. Nenhum teste existente da `127` ou da `133` mede esse resumo —
  conferido por busca: os casos de resumo são o de `test_andamento_composicao.py` (sorteio, sem
  ordem obsoleta) e o da apuração do marco intermediário, que não lê o resultado. A decisão fica
  registrada para o usuário revê-la no PR.

## A suíte depois da revisão

`make lint check test-pg` com `DB_NAME=ps135`, 4 workers, os mesmos grupos: `ruff check` e
`ruff format --check` sem achado, `manage.py check` sem problema, "No changes detected", e
**17 585 passando, 12 pulados, nenhuma falha**, em 1530 s. São quatro casos a mais que na primeira
rodada — o plural das sucessoras, a sucessora única, a janela sem data e o guardião do README, que
desta vez passou —, e os 12 pulados são os mesmos.
