# Research: A ordem por pontuação sem nenhum resultado é recusada (128)

As decisões D-001 a D-005 estão na spec. Aqui ficam as leituras do código que as sustentam e as
escolhas de implementação.

## R-1 — O critério sai da proposta, e não de uma consulta

**Decisão**: `nenhuma_com_resultado(marco, linhas)` em `classificacao/domain/universo_classificavel.py`,
sobre `posicoes + sem_posicao` da proposta. Uma linha tem resultado quando alguma Etapa enumerada é
chave de `pontuacoes`.

**Por quê**: `preparar` monta `pontuacoes` de **todo** Resultado vigente lido — o da Etapa decisória
entra com valor nulo, a Ocorrência entra com a pontuação que tiver (nula) —, e o universo é o de
`calcular_ordem`, já restrito pelo recorte, pela progressão e pela faixa do corte (FR-4203). A
eliminação vinda de Etapa enumerada tem a chave por construção; a vinda do desempate não tira ninguém
da ordem (FR-3548 da `114`) e não é enumerada, e por isso não conta (D-003). É exatamente o critério
que a `126` usava em `conferencia_da_ordem.resumo` para "nenhuma com resultado", que passa a chamar a
função.

**Alternativa descartada**: perguntar ao banco se há `ResultadoEtapa` vigente das Etapas enumeradas para
as inscrições do Perfil. Seria uma consulta a mais no comando, na tela e em cada recorte da conferência
do gesto, e um segundo universo (sem progressão nem faixa) que divergiria do cálculo.

## R-2 — Onde o comando recusa

**Decisão**: em `emitir_ordem`, logo depois de `calcular_ordem` e antes da busca do vigente.

**Leitura**: a repetição (`ctx.repetido`) já devolve o desfecho anterior antes de tudo (FR-4209); a
recusa do marco por sorteio vem antes do cálculo (FR-1318 da `067`), e um marco por sorteio nunca chega
aqui. Entre o cálculo e a assinatura, a recusa nova responde com a razão útil, e não com "a ordem mudou
desde a sua leitura" (D-005). O `DomainError` dentro de `comando_de_comissao` desfaz a transação: nada é
gravado, nem o desfecho da chave de idempotência (FR-4210) — é o mesmo caminho de toda recusa do
comando.

## R-3 — A frase

**Decisão**: `ordering_without_stage_results`, 422, `campo="marco"`. Frase da UX-260, com o número de
inscrições do universo e os nomes publicados das Etapas enumeradas, na ordem em que o marco as enumera.
Etapa enumerada que não existe no conteúdo vigente não aparece: o cálculo já recusaria antes
(`marco_sem_etapa`) se nenhuma existisse.

## R-4 — A tela

**Decisão**: `views.ordenacao` põe `sem_resultado` no contexto (o impedimento, ou `None`), com a lista
`(nome, url da distribuição)` só para quem `pode_emitir` — a porta da distribuição é a mesma base de
gestão da comissão (`_etapa_para_distribuir`). O template troca `{% if pode_emitir and recomputavel %}`
por um ramo que mostra o bloco UX-261 quando `sem_resultado`, e o pedido "peça a alguém que a emita"
deixa de aparecer nesse caso.

`emitir_ordenacao` sem `confirmar=1` volta à tela quando o impedimento existe, sem abrir a confirmação.
Quando o comando recusa no `confirmar=1` (formulário antigo), o erro de sessão traz a mesma frase que o
bloco; a tela não a repete duas vezes: o erro igual à frase do bloco não é impresso, e o bloco recebe o
foco (`role="alert"`).

**Alternativa descartada**: esconder só o botão e manter o formulário. O motivo e as citações não fazem
sentido sem o ato.

## R-5 — Os testes e fixtures que emitiam ordem sem resultado

**Decisão**: rodar a suíte com a recusa ligada e ajustar cada falha que for de **conveniência** —
fixture que emitia a ordem antes de avaliar alguém, só para ter um ato. O ajuste é dar Resultado a ao
menos uma inscrição, ou, quando o teste prova algo sobre a ordem vazia do acervo, emiti-la com a regra
desligada por `monkeypatch` (a ordem do acervo foi emitida antes desta regra). Cada um vai nomeado em
`verificacao.md`.

**Por quê**: um teste que prova "ninguém concorreu" usa universo vazio e não muda. Um que prova
obsolescência quando o resultado chega precisa da ordem emitida sem resultado — que agora só existe no
acervo —, e o `monkeypatch` é a forma honesta de dizer isso.

## R-6 — A base da branch e a `127`

**Decisão**: esta branch partiu de `claude/126-orientacao-p0-307906` (PR #414, aberto em 06/11). O
#414 e a `127` (PRs #415, #416, #417) entraram na `main` durante a implementação, e a branch foi
sincronizada com ela. Pela regra da `127`, `andamento.situacao_da_ordem` diz *Depois* enquanto
alguma Etapa lida pela ordem não está feita no Perfil, e só diz *Pendente* quando todas estão —
feitas, todo participante do Perfil tem Resultado, e a regra não recusa (FR-4218). O teste de
coerência está em `tests/interface/test_ordem_sem_resultado.py`.
