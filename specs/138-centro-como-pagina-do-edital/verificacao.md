# Verificação da 138

Worktree `138-centro-como-padrao-f6f2a9`, sobre a `main` em `daba322f`, em 10/11/2026.

## A suíte

`DB_NAME=ps138 make lint check test-pg`, com os grupos `dev`, `assistente` e `navegador`, 4 workers:

- **17 843 passando, 12 pulados, nenhuma falha**, em 828s.
- Os 12 pulados são os deliberados: 10 pares do vocabulário, a recusa por vendor e o E2E contra a
  Caixa. Nenhum é desta spec.

## A repartição dos testes do detalhe (R-008)

A primeira rodada completa, só com a troca, deu **72 falhas em 20 arquivos**. Todas abriam a página
de um Edital publicado e conferiam a composição do detalhe (o cartão "O que fazer agora" da `127`, o
"Andamento da seleção", "Quem atuou", os destinos, o bastão, a condução do imutável).

| O que o teste fazia | Quantos | O que mudou |
|---|---|---|
| Exercitava o detalhe de um Edital publicado | 71 em 19 arquivos | Passou a abrir `interface:pagina-anterior`, **sem mudar a asserção**. A troca foi feita só dentro da função que falhou e dos auxiliares que ela chama |
| Conferia o rótulo das dúvidas na página do Edital publicado (`test_duvidas.py`) | 1 | Nenhuma mudança no teste: o Centro passou a usar o mesmo rótulo do detalhe, "Ver as respostas do assistente de dúvidas (validação interna)" |

Um auxiliar compartilhado (`abrir_edital`, em `test_telas_de_quem_elabora.py`) servia também a um
caso de Edital em elaboração, cujo caminho de navegação é o da rota do Edital: esse caso voltou a
abrir `interface:detalhe`, com a mesma asserção.

Os testes da `136` que abriam `/centro/` passaram a abrir a rota do Edital
(`test_centro_do_edital.py`, `test_andamento_transicoes.py`, `test_centro_nos_cenarios.py`,
`test_chegada_e_volta_nos_cenarios.py`, `test_centro_em_escala.py`, `test_jornada_do_centro.py`).
`test_auditoria_passagem_da_retificacao.py` conta as páginas que alcançam a Retificação: eram a Lista,
o detalhe e o Centro; agora são a Lista, a página do Edital e a página anterior.

Dois casos novos conferem no Centro o alcance que os testes antigos conferiam no detalhe: o caminho do
publicador puro até a divulgação (`test_publicar_resultado.py`) e o link para a tela do marco
(`test_conducao_do_marco.py`).

## Os casos desta spec

`tests/interface/test_centro_como_pagina.py`:

- a escolha da composição: publicado → Centro; cancelado e derivação que falha → detalhe; a leitura
  do andamento acontece uma vez por página (FR-4860, FR-4861);
- **os sete atos** de `atos.ATOS`, pela tela de confirmação, como quem clica: submeter, devolver,
  homologar e revogar a homologação chegam ao detalhe; publicar e encerrar, ao Centro, com o retorno e,
  depois de publicar, a conferência da `116`; cancelar, ao detalhe (FR-4865, FR-4866, SC-1521);
- o redirecionamento de `/centro/`, com e sem consulta, e sem porta própria (FR-4863, SC-1523);
- a página anterior: o caminho de volta, a porta, o link único e nenhum outro template levando a ela
  (FR-4873 a FR-4875);
- o que só o detalhe oferecia: as dúvidas, o imutável e a condução, as datas (FR-4871, FR-4872).

O orçamento de consultas da `136` (`test_centro_em_escala.py`) passou sem mudança de teto, agora na
rota do Edital (SC-1524).

## No navegador

Banco descartável `ps138_dev`, com C06, C08 e C12 da `134` carregados (`--autoridade` com uma
autoridade criada para o banco), servidor pela entrada `centro-138` do `.claude/launch.json`.

- **C06, como `treino.presidencia`**, pela lista de Processos: a página do Edital é o Centro, sem a
  faixa; o caminho termina em "Edital SIM06/2026"; "Quem atuou" com datas e unidade; o link da página
  anterior é um só, no fim da administração.
- **A página anterior** abre o detalhe de antes, sem o botão do Centro, com o caminho "Edital
  SIM06/2026 › Página anterior".
- **`/centro/?fase=vagas`** redireciona para `/gestao/editais/<id>/?fase=vagas`, com Vagas consultada.
- **C12, como Gestor**: o Encerrar está impedido pelo prazo de recurso do cenário ("Antes de encerrar,
  resolva 1 pendência"), e o ato não foi forçado. O retorno foi conferido com o endereço que a tela do
  ato devolve (`?ato=publicar`): "Ato registrado: Publicar." no topo do Centro. O ato real está
  coberto pela suíte, nos sete atos.
- **A 375 px**, nenhuma rolagem horizontal; nenhuma mensagem no console (CSP).
- **C08**: abre no Centro, sem faixa.

## O que não foi verificado

- A conferência do concurso no Centro só foi vista na suíte (depois de publicar); os cenários da `134`
  não deixam registro de conferência para o Edital.
- O ato real pelo navegador: nenhum Edital dos cenários carregados podia ser publicado ou encerrado sem
  forçar o cenário.
