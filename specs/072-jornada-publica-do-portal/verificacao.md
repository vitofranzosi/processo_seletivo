# Verificação — 072

**Estado: implementação técnica concluída; feature NÃO validada nem pronta para publicação.** Duas
validações humanas estão pendentes ([validacao-humana.md](validacao-humana.md)): o percurso com cinco
pessoas (SC-605) e a validação do texto de finalidade de nome e CPF (FR-1627).

## Ambiente

| Item | Valor |
|---|---|
| Branch | `claude/072-jornada-publica`, empilhada sobre `claude/auditoria-processo-seletivo-ux-ef5de7` (PR 276) |
| Banco de demonstração | `ps_ux_conversao` — `make preparar` + `seed_demo`; `migrate --check` sem pendência (13/10) |
| Banco de teste | `test_ps_ux_conversao`, exclusivo desta worktree |
| Navegador | painel do aplicativo (Chromium 152), viewport emulado |
| Servidor | `runserver` na porta 8077, com o seletor de identidade e o e-mail no console |

## Verificação canônica

`cd backend && make lint check test-pg`, contra PostgreSQL, com `DB_NAME=ps_ux_conversao` (banco de teste
`test_ps_ux_conversao`, exclusivo desta worktree).

| Rodada | lint | check | test-pg |
|---|---|---|---|
| 1ª (13/10, depois das US1–US5) | `ruff check` e `ruff format --check` limpos | sem problema; `makemigrations --check` sem mudança | **10.877 passando, 11 pulados, 1 falha** em 1.194 s — `test_readme_acompanha_o_codigo.py`: a 072 fora da tabela de incrementos do README. Corrigido |
| 2ª (13/10, depois das correções) | limpos | limpos | **10.877 passando, 11 pulados, 2 erros** em 1.411 s — ambos em `test_database_permissions.py`, com `role "ps_runtime_conformance" cannot be dropped … objects in database test_ps_071`: a suíte da worktree da 071 rodava ao mesmo tempo no mesmo cluster. Os papéis de conformidade são do cluster, e `DB_NAME` próprio não os isola |
| arquivo isolado, sem outra suíte no cluster | — | — | **91 passando, 1 pulado** em 21 s, rodado depois que a suíte da 071 terminou — os 2 erros da 2ª rodada eram concorrência no cluster, e não defeito |
| 3ª (13/10, sobre o merge com a `main` que já tem a 070) | limpos | limpos; `makemigrations --check` sem mudança | **11.080 passando, 11 pulados, 1 falha** em 1.277 s — `divulgacao/test_imutabilidade.py::test_o_papel_de_runtime_nao_consegue_escrever_sobre_as_tres`, com `role "postgres" does not exist`: a rodada foi chamada sem `POSTGRES_USER=$USER`, e esta worktree não tem `.env`, de modo que o usuário do banco chegou vazio e o teste caiu no padrão `"postgres"`. É o único teste que lê `settings_dict["USER"]` |
| arquivo isolado, com as variáveis das rodadas anteriores | — | — | **12 passando** em 11 s — a falha da 3ª rodada era a invocação, e não o merge |

Os 11 pulados são os de sempre, segundo o `AGENTS.md` (9 pares termo × template da varredura de
vocabulário, a recusa por vendor e o E2E da Caixa). A diferença de total em relação ao `AGENTS.md`
(10.408 em 09/10) é das features integradas desde então e dos testes desta.

**Testes desta feature** (todos verdes nas duas rodadas): `portal/test_oferta_e_teto.py`,
`portal/test_resumo_do_acompanhamento.py`, `portal/test_acompanhamento_na_vitrine.py`,
`portal/test_vocabulario_das_telas_publicas.py`, `integration/portal/test_contexto_do_acesso.py`,
`acceptance/portal/test_jornada_publica.py`, e os casos novos em `integration/portal/test_vitrine.py`,
`test_consulta_da_vitrine.py`, `test_detalhe_selecao.py`, `test_leitura_sem_escrita.py` e
`interface/test_acessibilidade_do_portal.py`. Guardião de citações e matriz de rastreabilidade
(`tests/test_citacoes_de_requisito.py`): verdes.

## Medição da primeira tela (SC-600, SC-601, SC-607)

Script: [`doc/auditoria-ux-conversao-2026-10-12/medir-primeira-tela.js`](../../doc/auditoria-ux-conversao-2026-10-12/medir-primeira-tela.js),
páginas buscadas sem sessão e renderizadas em `iframe` de largura e altura fixas, contra o seed.

### Vitrine

| Tela | Antes: 1º cartão | Depois: 1º cartão | Título do Edital na 1ª tela | Convite na 1ª tela | Rolagem lateral |
|---|---|---|---|---|---|
| 320 × 568 | 657 | 531 | não (645) | não | 0 |
| 360 × 800 | 602 | 531 | **sim** | não | 0 |
| 375 × 667 | 602 | 505 | **sim** (597) | não | 0 |
| 375 × 812 | 602 | 505 | **sim** | não | 0 |
| 390 × 844 | 602 | 476 | **sim** | **sim** (807) | 0 |
| 768 × 1024 | 433 | 463 | sim | sim | 0 |
| 1280 × 800 | 355 | 359 | sim | sim | 0 |
| 1440 × 900 | 355 | 359 | sim | sim | 0 |

A busca está na primeira tela em todas. Em tela larga a barra continua numa linha (100 px de altura,
como antes), com o grupo aberto pelo script. **SC-600: atendido.**

### Página da seleção (Edital 01/2026)

| Tela | Resumo da oferta termina em | Resumo e ação na 1ª tela | 1º "Inscrever-se" antes → depois |
|---|---|---|---|
| 320 × 568 | 612 | **não** | 1.350 → 1.704 |
| 360 × 800 | 587 | sim | 1.275 → 1.580 |
| 375 × 667 | 587 | sim | 1.249 → 1.580 |
| 375 × 812 | 587 | sim | 1.249 → 1.580 |
| 390 × 844 | 562 | sim | 1.223 → 1.529 |
| 768 × 1024 | 446 | sim | 783 → 987 |
| 1280 × 800 | 413 | sim | 726 → 929 |

**SC-601: atendido** nas quatro telas que ele nomeia. **Custo registrado:** o resumo acrescenta cerca de
200 px ao cabeçalho, e o primeiro botão "Inscrever-se" desce na mesma medida — o caminho até a vaga
passa a ser o atalho do resumo, e não a rolagem. Em 320 × 568 o resumo não cabe inteiro.

### Sem script

Com a página em `iframe` sem permissão de script (`sandbox="allow-same-origin"`): o grupo de filtros
fica fechado com o `summary` à vista também em 1280 px — a degradação prevista na research T-002 —, e
a consulta funciona por envio de formulário. Nenhuma rolagem lateral.

## Jornadas no navegador

| Jornada | O que foi visto |
|---|---|
| Encontrar | Vitrine em 375 × 667 e 1280 × 900: título "Processos seletivos do Cefor/Ifes", "1 seleção com inscrições abertas.", busca à vista e "Mais filtros e ordenação" recolhido no celular; cartão titulado pelo Edital, oferta por Perfil, "Onde:", dados de apoio por último |
| Acompanhar | Cartão do Edital 51/2026: "Resultado preliminar publicado em 12/10/2026. Recurso até 17/10/2026 às 23h59." e "Ver resultados e prazo de recurso"; Edital 26/2026 sem frase de resultado |
| Preparar | Página do Edital 01/2026: "Além dos documentos, a inscrição pede o preenchimento do Requerimento de Matrícula." antes do primeiro Perfil |
| Começar — visitante novo | "Inscrever-se" no Técnico de Laboratório → "Confirme seu e-mail para se inscrever" com a vaga → código (com a ajuda de spam) → "Seus dados" com a vaga e a finalidade. **Parado aqui**: o CPF é digitado por uma pessoa; a passagem por esta tela pelo formulário está provada no teste de aceitação |
| Começar — recorrente | Candidata do fixture (`m@ex.br`): volta à página com a vaga em destaque ("Vaga indicada") e a mensagem "Você entrou como m@ex.br. Para abrir sua inscrição nesta vaga, toque em “Inscrever-se nesta vaga”."; a confirmação abriu o rascunho da vaga, sem aviso fora de contexto |

Parte dos acionamentos no navegador foi feita por `click()` no botão da própria página, porque o clique
por coordenada no viewport emulado não chegou ao servidor uma vez (o log mostra um só `POST /sair`
para dois cliques). É o mesmo formulário, com o mesmo CSRF; o que se perde é a prova do clique.

## Diferenças em relação ao plano aprovado

- **Orçamento de consultas** provado com 1 e 3 Editais com resultado, e não 1 e 4: cada cenário com
  resultado publicado é caro de montar, e três já mostram que o número de consultas não cresce.
- **A sigla da unidade vale também para o filtro e a busca da vitrine**, e não só para o cartão
  (research T-006): filtro, busca e cartão passam a dizer o mesmo. O filtro de unidade só aparece com
  mais de uma unidade, e um endereço antigo com `unidade=CEFOR` passa a ser lido como filtro ausente —
  a regra que a `024` já dá a valor irreconhecível.
- **As regras de tela larga da consulta** entraram no bloco `@media (min-width:60rem)` que já existia,
  e não num bloco próprio: um teste da `055` localiza o primeiro bloco dessa largura.
- **Três correções depois da verificação no navegador**: a grade do cartão esticava a marca do cartão
  mais curto de um par (`align-content:start`); o contexto do acesso repetia o número quando o título
  do Edital já o traz (com teste); a aba do acesso a caminho de uma vaga passou a dizer "Confirme seu
  e-mail".
- **Testes antigos ajustados** só no recorte: quatro casos localizavam a vaga pela primeira
  ocorrência do nome do Perfil, que agora aparece antes, no resumo do cabeçalho; passaram a recortar a
  seção das vagas. Nenhuma asserção de texto de decisão anterior foi alterada.

## Achados laterais (registrados, não resolvidos aqui)

- **A página da seleção ainda diz "Unidade: CEFOR"** no subtítulo, enquanto o cartão da vitrine passou
  a dizer "Cefor" (FR-1605 cobre só o cartão). Ler a sigla na página custaria uma consulta a mais; fica
  para quem tratar a marca da unidade (pendência registrada na `060`).
- **O resumo da oferta empurra as vagas para baixo** (≈ 200 px no celular). É o custo esperado de pôr o
  atalho na primeira tela; se o percurso conduzido mostrar que as pessoas rolam em vez de usar o
  atalho, é dado para rever a posição.

## Pendências

- **SC-605** — percurso conduzido com cinco pessoas: roteiro pronto, **não realizado**.
- **FR-1627** — validação do texto de finalidade de "Seus dados": texto proposto, **não validado**.
