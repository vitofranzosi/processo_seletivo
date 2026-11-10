# Verificação: A tela do sorteio como a jornada de quem o conduz (142)

## Onde

Dois servidores lado a lado, cada um com a sua cópia da mesma base (`ps142_base`: C06 e C07 da
`134`, rodada 1, recém-carregados, com a autoridade da suíte):

- **antes**: um checkout descartável da `main` em `daba322f`, sobre `ps142_antes`;
- **depois**: esta branch, sobre `ps142_dev` (entrada `jornada-do-sorteio-142` do `.claude/launch.json`).

O roteiro [`capturas/capturar.py`](capturas/capturar.py) pratica os atos de verdade, na mesma ordem
nos dois lados, e captura a página inteira a 1440 × 900 (e a dobra, em quatro estados) e a 375 px.
Ele mede, em cada estado, a posição dos botões, a rolagem horizontal e o conjunto de formulários de
ato, e escuta o console para violações de política de conteúdo. As medidas estão em
`capturas/antes-medidas.json` e `capturas/depois-medidas.json`.

## Os estados

| # | Estado (cenário da validação) | Captura |
|---|---|---|
| 01 | C06: nada preparado (1) | `antes-01-…`, `depois-01-…` (e `-dobra`) |
| 02 | C06: a ampla fixada, a PPP pendente (2) | `…-02-…` (e `-dobra`) |
| 03 | C06: as duas fixadas (3) | `…-03-…` |
| 04 | C07: as duas fixadas, a semente não observada (4) | `…-04-…`, e a 375 px |
| 05 | C06: a semente observada (5) | `…-05-…` (e `-dobra`) |
| 06 | C06: a ampla sorteada, a PPP não (6) | `…-06-…` (e `-dobra`) |
| 07 | C06: o sorteio concluído (7), na volta do ato e aberto pelo topo | `…-07-…`, `…-07b-…`, e a 375 px |
| 08 | C06 rodada 2: a semente antes da PPP; o sorteio da PPP **recusado** (8) | `…-09-…`, `…-08-…` |
| 09 | A lista em que ninguém concorre (9) | não há nos cenários da `134`; coberto por `tests/interface/test_jornada_do_sorteio.py` (a PcD vazia) |
| 10 | O Auditor, sem a condução (10) | `…-10-…` |
| 11 | O Centro depois dos sorteios | `…-11-…` |
| 12 | Do Centro ao sorteio da rodada 2, pela providência | `depois-12-…-1440`, `depois-12-…-375` |

## O que mediu

**Os formulários (SC-1542, FR-4903).** Em **13 de 13 estados**, o conjunto de formulários de ato —
destino e lista — é o mesmo antes e depois. Nenhum controle foi acrescentado, removido ou habilitado.

**Rolagem horizontal e CSP (SC-1545).** Nenhuma rolagem horizontal, a 1440 e a 375 px, nos dois
lados; nenhuma violação de política de conteúdo no console.

**As posições** (px do topo da página, a 1440 × 900; "fixar" só tem sentido nos estados com lista
por fixar, e nos outros é o botão recolhido da sucessão):

| Estado | antes: fixar / observar / sortear | depois: fixar / observar / sortear | altura da página |
|---|---|---|---|
| 01 nada preparado | 1681 / **887** / — | **1679** / 2591 / — | 2220 → 3368 |
| 02 ampla fixada | 2120 / **1106** / — | **1539** / 2302 / — | 2511 → 3079 |
| 04 C07, sem semente | 1901 / **887** / — | 1132 / 1821 / — | 2364 → 2598 |
| 05 semente observada | — / — / 1953 | — / — / 2448 | 2670 → 3035 |
| 06 uma sorteada | — / — / 2685 | — / — / 2814 | 2864 → 3852 |

- **SC-1540**: fixar passou para cima de observar em todos os estados com lista por fixar (antes,
  observar vinha 794 a 1014 px acima). No C06 aberto pelo topo, o primeiro fixar continua a
  ~1.680 px: o que fica acima dele agora são os passos e a conferência do cartão, e não o método.
- **A página ficou mais alta** (até ~1.000 px no estado 06), pelos quatro cabeçalhos de passo, pela
  ordem sorteada e pelo "o que este passo pede", aberto no passo da vez. As tabelas das listas
  fixadas passaram a ficar recolhidas, o que compensa parte disso com listas grandes.
- **A chegada pelo Centro** (estado 12): a providência "Realizar o sorteio" leva a `#sorteio-ampla`,
  e o botão fica a **313 px** do topo da janela a 1440 × 900 e a **283 px** a 375 × 812. Antes ela
  levava ao cartão da lista, com a relação e a tabela antes do botão.

## O que se leu nas capturas

- **Antes**: a tela abria pelo método (algoritmo, derivação, normalização, resumo); "Nenhum corte
  emitido" encabeçava listas sem participantes fixados; a ordem sorteada não aparecia; a semente
  aparecia antes das listas.
- **Depois**: o contexto (Perfil, Edital, as listas pelo nome); os quatro passos com a situação de
  cada lista, e "Agora" no passo da vez; uma seção por passo, na ordem; a conferência antes de
  fixar; a semente uma vez, "uma só, para as 2 listas do marco"; o método recolhido; a execução de
  cada lista com o botão ou a razão; a ordem gravada, aberta na lista que acabou de ser sorteada, com
  "Ainda não foi divulgada como resultado".
- **O Centro** (`…-11-…`) mostra os mesmos atos nos dois lados — esta feature não muda o Centro.

## Achados, para decisão (não são escopo)

1. **Observar antes de fixar a primeira lista.** No C06 inicial, o passo 2 diz *Depois* ("nenhuma
   relação deste marco está congelada") e a tela oferece o botão de observar — como já oferecia. A
   derivação e a tela de antes já divergiam aqui; a `142` não mexeu na condição (FR-4903) e deixou o
   botão como ação secundária. Liga-se à decisão de 10/11 sobre a observação.
2. **O F-1 do estudo, reproduzido** (estados 08 e 09): na rodada 2 do C06, com a fonte de
   treinamento que publica a hora, a semente obtida antes de fixar a PPP deixa o sorteio da PPP
   *Pendente* na derivação, na tela e no Centro, e o serviço o recusa. É o comportamento decidido
   (alternativa "não decidir agora"); a correção do diagnóstico continua "a considerar".
3. **A conferência em dois passos do congelamento** e **a frase do conceito da relação** em
   `conceitos.py` — registrados no plano.

## A suíte

`cd backend && make lint check test-pg`, com `DB_NAME=ps142`, sobre a `main` em `daba322f`, com o
grupo `navegador` e sem o `assistente`, 4 workers (10/11/2026): `ruff check` e `ruff format --check`
limpos, `check` sem problema, `makemigrations --check` sem mudança, e **17849 passando, 13 pulados e 2
falhas**, em 1539 s. Os 13 pulados são os 12 de sempre com o grupo `navegador` mais o da contagem real
de tokens, que pula sem o `assistente`.

As duas falhas eram de testes que liam o que a `142` mudou de propósito, e foram ajustados:

- `test_folha_estatica.py::test_cada_folha_de_tela_e_carregada_so_por_quem_a_usa` — o registro de
  quem carrega `andamento.css` ganhou a tela do sorteio, que usa as classes de situação do Centro;
- `test_carga_e_restauracao.py::test_o_exercicio_e_preservado_isolado_e_a_restauracao_so_alcanca_o_c07`
  — procurava a prosa "Realizar o sorteio", que agora é também o nome do passo 3; passou a procurar o
  formulário.

Os dois, mais os guardiões de folha, citação, README, vocabulário, acessibilidade, estáticos e
política de conteúdo e os testes novos, rodaram de novo depois do ajuste: verdes. A suíte inteira não
rodou uma segunda vez.

Os testes que liam a prosa ou os rótulos antigos da tela foram ajustados para ler o controle, e os
que procuravam um rótulo com `not in` trocaram de marca — com o rótulo antigo, passariam calados:
`test_tela_do_sorteio.py`, `test_relacao_de_habilitados.py`, `test_sorteio_espera_o_periodo.py`,
`test_sorteio_extracao_inviavel.py`, `test_recortes_alinhados.py` (a seção dos cartões termina na da
semente) e `test_telas_de_resultado_e_atos.py` (os rótulos e o desenho dos botões da tela, com a
razão).
