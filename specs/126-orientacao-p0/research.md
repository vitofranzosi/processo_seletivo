# Research: Correções de orientação e segurança operacional (P0)

Leitura do código da `main` em `250efe97`, em 06/11/2026. Cada item confere um achado do estudo antes
de virar requisito.

## R-1 — Os achados conferem

| Achado | Onde | Confirmado |
|---|---|---|
| J-08: sucessão aberta depois do ato | `corte.html:130-143` (um formulário só, com `motivo` quando há geração, botão `botao`); `ordenacao.html:253-288`; `ocupacao.html:180-201`; `sorteio.html:472-491` | sim; os quatro desenham a sucessão aberta logo abaixo da confirmação |
| J-06: *Falta* em lista sem inscrito | `conducao_do_marco._celula_da_ordem` devolve `FALTA` quando `ato is None`, sem distinguir "não haverá ato"; `_celula_do_corte`, `_celula_da_apuracao` e `_celula_da_publicacao` idem; `_gestos_oferecidos` (`views.py`) oferece todo gesto com alguma célula `FALTA` | sim |
| J-06: as duas frases da convocação | `convocacao.html:75-78` ("Ir para a apuração") e `:235-250` (a faixa seguinte, que só depende de `leitura.esgotou`, que é `not fila`) | sim; `esgotou` é verdadeiro com fila vazia por qualquer razão, inclusive sem ordem |
| J-07: "aguardando resposta" sem comunicação | `relatorio_do_edital._convocacoes`: sem desfecho e `vencimento > agora` → `aguardando`; `vencimento <= agora` → `vencidas`; nunca lê as comunicações | sim, e há um segundo defeito: sem envio e vencimento passado vira "vencida", o que `prazo.decorrido` proíbe |
| J-10: aviso no topo | `previa.recortes_do_marco` devolve `congelar_agora_inviavel` quando **algum** recorte não tem diagnóstico, com `inclui_sucessao`; `sorteio.html:245-260` o mostra no topo dos recortes | sim; com todas congeladas, o aviso só vale para a sucessão, e mesmo assim é a primeira frase |
| G-01: ordem sem resultado emissível | `emitir_ordem` não recusa por Resultado ausente; `ordenacao_confirmar.html:44-53` mostra só as contagens e os protocolos | sim |

## R-2 — O critério de "sem inscrito", e por que não chamar a prévia inteira

**Decision**: `sorteios/application/previa.recortes_sem_inscrito(*, edital, conteudo, perfil_id,
marco_id, agora)`, ao lado de `recortes_do_marco`, devolve o conjunto de `lista_id` (com `None` para a
ampla); `conducao_do_marco.recortes_sem_inscrito` só a chama com o marco que já leu (revisão do PR, que
apontou a terceira redação da regra em `interface/`). Vazio quando o marco não sorteia ou quando o
período está aberto ou por abrir (`periodo_de_inscricoes`; o não designado conta como fechado). Para os
demais: **uma** consulta às Modalidades declaradas, distintas, pelas inscrições enviadas do Perfil — a
mesma pergunta de `projecao.elegiveis(..., habilitadas=None)`, sem trazer as inscrições —, e
`relacao_vigente` e `ato_vigente` só para os recortes vazios; sem inscrito é nenhuma declarante, sem
relação nem ordem vigente.

**Rationale**: são as mesmas peças que `previa.recortes_do_marco` usa para `projetados` e `congelada`,
e que `publicar_relacao` usa para recusar com `relation_would_be_empty`. Chamar a prévia inteira na
condução custaria a ocorrência, os sorteios, os diagnósticos e as relações sucessoras de cada recorte,
para ler dois campos. As duas condições a mais (inscrições encerradas; sem o filtro de habilitação) são
a D-002 da spec.

**Alternatives considered**: (a) chamar `previa.recortes_do_marco` — o pedido sugere o critério dela, e
o critério é o mesmo; o custo, não. (b) usar a ausência de ato — explicitamente recusada pelo pedido.

## R-3 — Onde a lista sem inscrito aparece, e o que muda em cada lugar

| Lugar | Hoje | Depois |
|---|---|---|
| Condução, células | `FALTA` | `NAO_SE_APLICA`, nota "nenhuma inscrição nesta lista", sem `url` |
| Condução, totais | contam | não contam (o `_totais` já exclui `NAO_SE_APLICA`) |
| Condução, gestos | oferecidos por causa dela | não (o `_gestos_oferecidos` só olha `FALTA`) |
| Conferência do gesto | `IMPEDIDO` "sem ordem" | `FORA`, razão "Nenhuma inscrição nesta lista" |
| Condução, tudo sem inscrito | "Nenhum recorte… em falta" | "Nada a conduzir neste marco" |
| Convocação | "Ir para a apuração" + faixa seguinte | frase de não se aplica, sem os dois caminhos nem o gesto de titulares |
| Ocupação | "emita a ordem deste recorte" | frase de não se aplica |

O alcance (conferência) recebe `agora` da view, como a condução.

## R-4 — A sucessão recolhida

**Decision**: um `<details class="sucessao">` com `<summary>` "Suceder este corte (exige motivo)" (e as
variantes de ordem, apuração e relação), com o formulário dentro. `open` quando o ato é obsoleto:
`corte_obsoleto`; `obsoleto and recomputavel` na ordem; `recorte.estado == "OBSOLETE"` na ocupação;
`recorte.diagnostico_da_relacao` no sorteio. O formulário da primeira emissão continua fora do bloco.

**Rationale**: `details` abre por teclado e toque, é o padrão do repositório para conteúdo recolhido
(`.como-preencher`, `057`), e não precisa de script (CSP). O botão interno fica `botao secundario`/`acao`:
mesmo dentro do bloco aberto, a sucessão não é o botão de maior peso.

**Corte**: o formulário único se divide em dois ramos (`{% if geracao %}` dentro do bloco, `else` fora).
A faixa seguinte continua fora (FR-4013).

**Ordem**: as citações de decisão continuam dentro do formulário que as envia; quando há ato vigente,
elas vão junto para dentro do bloco — sucessão é o único caminho que as executa, nesse caso.

## R-5 — A convocação por estado, no relatório

**Decision**: `_convocacoes` prefetcha `comunicacoes` e classifica cada vigente por
`prazo.estado(tem_desfecho=..., enviado_em=envio, vencimento=..., agora=...)`, com `envio` lido das
comunicações prefetchadas (a mesma regra de `selectors.envio_de`). `Convocacoes` ganha
`sem_comunicacao: int = 0`. A espécie `CONVOCACAO_SEM_COMUNICACAO` nasce em `pendencias_do_edital` (ao
lado das outras), entra em `texto_da_pendencia`, em `DA_099` e na soma do Encerrar, nos rótulos do
consolidado e na tabela do PDF consolidado.

**Rationale**: `prazo.estado` é a função que a tela da convocação e o portal já usam; o relatório era o
único leitor com uma segunda conta. O `prefetch` acrescenta uma consulta por Edital.

**Fixtures**: `tests/fixtures/relatorio.py` convocava sem comunicar e esperava "aguardando resposta". O
cenário representa uma convocação comunicada; a fixture passa a registrar o envio, e as asserções
continuam as mesmas. Um teste novo cobre a convocação sem envio.

## R-6 — O aviso de congelamento no lugar

**Decision**: `previa.recortes_do_marco` acrescenta ao dicionário `congelar_agora_inviavel` a chave
`inclui_congelamento`: algum recorte não congelado, com `projetados > 0` e sem diagnóstico. O template
mostra o aviso no topo se `inscricoes_correndo or inclui_congelamento`, e dentro do bloco de sucessão de
cada relação congelada sem diagnóstico. A frase "Vale também para publicar relação nova…" sai do topo.

**Rationale**: a regra de quando o aviso existe (`102`) não muda; só se acrescenta a informação de para
quem ele vale. O recorte sem inscrito tem `projetados == 0`, e por isso não conta (FR-4033).

## R-7 — As mensagens de sucesso

| Ato | De onde vêm os números | Recorte |
|---|---|---|
| Corte | `resultado.progrediram`, `resultado.ultimaPosicao`; sucedeu: `geracao.0.corte_anterior_id`; continuação: a view marca `acao` | `recorte_atual.rotulo`, quando há navegação |
| Ordem | a view, depois de `emitir_ordem`, conta as posições do ato vigente (com e sem posição) e as guarda junto do resultado | idem |
| Apuração | `resultado.efetivas`, `ocupadas`, `faltando`; a view guarda `listaId`, e a leitura acha o rótulo | rótulo do recorte da ocupação |
| Relação | `resultado.quantidade`; a view `publicar_relacao_do_sorteio` acrescenta ao resultado o `listaId` do POST | o template acha `recorte.nome` pelo `lista_id` |

Nenhuma diz o próximo passo (FR-4018).

## R-8 — A confirmação da ordem

**Decision**: `interface/conferencia_da_ordem.resumo(proposta)` lê `proposta["marco"]["stages"]`,
`proposta["etapas"]` e `proposta["sem_posicao"]`. Sem resultado na Etapa *e* é a inscrição sem posição,
não eliminada (`consequencia` vazia), cuja chave da Etapa não está em `pontuacoes` (a chave existe sempre
que há Resultado vigente, mesmo de Etapa decisória sem pontuação). Devolve as Etapas com contagem, o total
considerado, se nenhuma tem resultado, e os grupos por motivo, na ordem de aparição.

**Rationale**: o motivo gravado ("Sem pontuação nas Etapas enumeradas: X, Y.") lista também a decisória
com resultado, e não serve para contar; a chave em `pontuacoes` serve.

## R-9 — Convivência com o PR #410 (`124`)

O #410 toca `sorteio.html` (linhas 57-75 e 169), a view `sorteio` (perto de 10973 e 11054) e
`ocorrencia.py`. Esta spec toca `sorteio.html` na mensagem da relação (linha 54), no aviso (245-260) e no
formulário de sucessão (472-491), e não toca a view `sorteio` nem `ocorrencia.py`. Antes de cada push:
`gh pr view 410 --json state,mergeable`; mergeado, sincronizar antes de continuar.
