# Research: Trilha da unidade

Decisões técnicas e de recorte da `108`. As de governança ficam como pendências na
[spec](spec.md#decisões-pendentes-do-usuário), com a saída que não concede nada.

## D-001 — A permissão é `auditoria:consultar`, na unidade ativa

**Decisão.** A página exige `auditoria:consultar` no escopo ativo, e nenhuma permissão nova nasce.

**Por quê.** É a capacidade que o catálogo descreve como "consulta a trilha de auditoria dos atos
praticados" (`DESCRICOES["auditor"]`), e o Auditor já a usa para ler a trilha de todo Edital e de
toda comissão da unidade. A trilha administrativa é a mesma tabela, do mesmo escopo, lida pelo mesmo
seletor; uma permissão própria só se justificaria se ela fosse dada a alguém que **não** deve ler a
trilha do certame — e quem seria esse alguém é decisão de governança (pendência P3).

**Alternativas.** `trilha-da-unidade:consultar`, dada ao Auditor e ao Gestor: o Gestor é o autor
da maior parte dos atos desta página, e ler os próprios atos não é fiscalização; fica registrado
como P3-B. `visao:consultar`: responde a outra pergunta (o panorama dos certames), e a `040` já
recusou reusá-la para a trilha.

## D-002 — Os eventos de acesso entram; o histórico da `107` fica como está

**Decisão.** A trilha da unidade inclui os eventos `ACESSO_CONCEDER` e `ACESSO_REVOGAR` cujo vínculo
é da unidade: os gravados no escopo dela e os gravados no escopo institucional com `detalhe.escopo`
igual a ela — a concessão do Administrador de acessos da unidade pelo administrador institucional.
O histórico da `107` não é copiado nem lido aqui.

**Por quê.** São dois leitores e duas fontes. O histórico da `107` lê os vínculos e as revogações
(a FR-3107 da `107`), exige `acesso:consultar`, e é a ferramenta de quem concede: ele responde "quem
tem qual papel, e desde quando". A trilha é a prova append-only, e responde "quem fez este ato, e
por quê" a quem **não** concede. Sem ela, o Administrador de acessos da unidade seria o único leitor
das próprias concessões — o mesmo vício de quem homologa o próprio ato. A página não ganha código
de acesso: só rótulos e o nome do papel pelo catálogo.

**O escopo institucional entra só por esta porta.** O escopo do evento é o do ator
(`record_event` grava `actor.institution_scope`), e a concessão do Administrador de acessos do
`cefor` fica no institucional. A condição é `aggregate_type = 'Vinculo'` **e** `detalhe.escopo` igual
à unidade: nenhuma suspensão, nenhuma administração institucional, nenhuma sessão sem unidade.

**Alternativas.** Ficar só na `107`: deixaria o fiscal sem a pergunta mais importante. Juntar o
histórico da `107` na página: duas fontes para o mesmo fato, que podem divergir na primeira
correção; e daria ao Auditor a listagem dos vínculos vigentes, que a `107` reservou a
`acesso:consultar`.

## D-003 — Sem leitura no nível institucional nesta spec

**Decisão.** A página é só da unidade ativa. Quem está no escopo institucional não a alcança — a
condição de acesso exige que o escopo ativo seja uma unidade, e não o institucional.

**Por quê.** O único papel institucional, o Administrador institucional de acessos, tem só
`acesso:administrar`, e a `107` lhe recusou ver os papéis operacionais das unidades. A trilha de
todas as unidades lhe daria isso e mais (autoridades, avisos); a trilha só do escopo institucional
seria ele lendo os próprios atos, que o histórico da `107` já lhe mostra. Quem audita o nível
institucional é pergunta de governança (P1).

**Alternativas.** As opções B e C de P1, na spec. Ambas custam uma linha no catálogo de papéis e
um ramo no seletor; nenhuma muda o que se grava.

## D-004 — Sessões e suspensões ficam fora

**Decisão.** `ENTRADA`, `TROCA_DE_UNIDADE`, `SAIDA`, o término por prazo, `PESSOA_SUSPENDER` e
`PESSOA_REATIVAR` não entram.

**Por quê.** A sessão não é ato administrativo, e uma entrada por pessoa por dia soterraria os atos
que a página existe para mostrar. A suspensão é global (a decisão P1 da `107`), gravada no escopo
institucional e sem unidade no detalhe: mostrá-la na unidade exigiria decidir em qual das unidades
da pessoa ela aparece. As duas ficam como P2 e P1.

## D-005 — O que a linha mostra, e de onde vem

**Decisão.** Cada linha mostra quando, o ato, sobre o quê, quem, a situação e o motivo. "Sobre o
quê" vem **do próprio registro** sempre que ele o tem — o `detalhe` da unidade, do modelo e do
vínculo guarda o nome no instante do ato, e o motivo da autoridade é o rótulo dela —, e de uma
consulta por tipo só para o aviso e a interrupção, cujo registro não nomeia o Edital.

| Assunto | Sobre o quê | Motivo |
|---|---|---|
| Unidade, registro | `detalhe.depois.nome` | — |
| Unidade, alteração | `detalhe.depois.nome`, e os campos mudados com antes e depois | — |
| Unidade, exclusão do piloto | o nome da unidade ativa | "N trocas excluídas; relatório final de dd/mm/aaaa", do `detalhe` |
| Autoridade | o `reason`, que é o rótulo (nome, cargo e ato de nomeação); na correção e no encerramento, os campos mudados com antes e depois | — |
| Modelo de aviso | `detalhe.depois.nome` | o `reason` ("Modelo editado.") |
| Aviso | "Edital NN/AAAA", e a origem | o `reason` (contagens; justificativa) |
| Interrupção | "Edital NN/AAAA", e a origem | o `reason` (motivo da interrupção) |
| Vínculo | o nome da pessoa e o papel pelo catálogo | o `reason` (motivo da concessão ou revogação) |

**Nunca**: o `detalhe` cru (o do modelo traz assunto e corpo), a correlação, a idempotência, o
identificador interno.

**Por quê.** O nome do instante do ato é o que a trilha prova; o de hoje pode ter mudado. E ler do
registro poupa uma consulta por linha, que é o que `FR-3168` proíbe.

## D-006 — Uma consulta por página, e no máximo uma por tipo de enriquecimento

**Decisão.** A página faz: a consulta paginada da trilha (vinte e um registros, para saber se há
mais); no máximo uma consulta de avisos e uma de interrupções, pelos identificadores da página, com
o Edital junto; a do nome das pessoas institucionais, que a tag `nome_de_pessoa` da `107` já faz uma
vez por requisição; e a da unidade ativa, só se houver exclusão do piloto na página.

**Por quê.** Constante no número de linhas e no tamanho da trilha (`FR-3168`). O teste mede uma
página com um ato e uma com vinte, dos cinco assuntos.

## D-007 — O seletor novo reaproveita o cursor e a paginação de `consultar`

**Decisão.** `auditoria/selectors.py` ganha `trilha_da_unidade(*, actor, assunto, cursor, limit)`,
e a paginação por cursor sai de `consultar` para uma função comum, sem mudar o comportamento dele.
O escopo vem do `actor`, e só dele.

**Por quê.** `consultar` filtra por `institution_scope = actor.institution_scope`, e a condição de
`D-002` precisa de um segundo escopo, restrito a um tipo e a um valor do detalhe. Estender
`consultar` com um escopo extra abriria a porta para qualquer chamador; uma função própria deixa a
exceção num lugar só, nomeada e testada. O cursor e a ordem são os mesmos, e por isso o mesmo
`pagina_seguinte` serve à tela.

**Índice.** O índice existente (`aggregate_type, aggregate_id, occurred_at`) não cobre
`institution_scope, occurred_at`. Com dezenas a milhares de eventos administrativos por ano, a
leitura por escopo e tipo é barata, e um índice novo seria migration numa tabela append-only que
cresce com o certame inteiro. Fica registrado: se a trilha passar de centenas de milhares de linhas
por unidade, o índice é o primeiro passo.

## D-008 — A página mora num módulo de view próprio

**Decisão.** `interface/trilha_da_unidade.py`, rota `trilha-da-unidade` em `/gestao/`, template
`interface/trilha_da_unidade.html`, folha `interface/telas/trilha_da_unidade.css` pelo bloco
`estilo_da_pagina`. O módulo entra em `MODULOS_DE_VIEW` (`tests/test_gramatica_das_portas.py`). A
página não tem identificador no endereço e não responde 404 nenhum: a falta de permissão é 403
explicado, e o escopo vem do ator. Por isso o inventário de negativas da `033` não ganha linha.

**Por quê.** `views.py` tem nove mil linhas, e as telas novas desde a `099` nascem em módulo próprio.
A barra ganha o item em `SECOES` — e não em `SECOES_DE_ACESSO` —, porque `auditoria:consultar`
existe na demonstração e o seletor a alcança (`FR-3156`).

## D-009 — O filtro desconhecido vale como "Todos"

**Decisão.** `?assunto=` com valor fora da lista é ignorado; o seletor do filtro mostra "Todos".

**Por quê.** É o que o formulário consegue produzir; um valor fora dele é endereço montado à mão. A
recusa não protegeria nada — o escopo continua o do ator — e a página nunca parece filtrada sem
estar. O cursor adulterado continua recusado como em `consultar` (`invalid_cursor`, 400).
