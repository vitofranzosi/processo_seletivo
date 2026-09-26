# Research — 047 · Situação pública e histórico oficial do Edital em execução

Medido contra a `main` em `ee894ab`, em 26/09/2026. Cada item diz o que foi decidido, por quê e o
que foi descartado. Nenhum depende de decisão do usuário: as duas de domínio estão em
*Clarifications* da spec.

---

## R-1 — A fase do Evento sai da gestão para o domínio, e o portal a lê de lá

**Decisão.** `fase_do_evento`, `instantes_do_evento`, `descricao_do_evento`, `eventos_do_conteudo`
e `FASE_DO_PERIODO` saem de `interface/supervisao.py` e passam a morar num módulo de domínio,
`editais/domain/fase_do_evento.py`. A `supervisao` os reimporta com os mesmos nomes, e nenhum
chamador da gestão muda. O portal apaga `_situacao_do_evento` (`portal/leitura.py:62-89`) e
`leitura.cronograma` passa a chamar `fase_do_evento`.

**Por quê.** A `045` pôs a régua certa na camada errada para quem mais precisava dela. O portal não
importa nada de `interface/` hoje (`grep` vazio), e importar `supervisao` puxaria trinta módulos da
gestão para dentro da página pública. `editais/domain` já depende de `inscricoes/domain/periodo`
(`editais/domain/validation.py`), então o módulo novo não cria direção de dependência nova. É o
mesmo movimento que a `028` fez ao criar `calendario.py`: *"uma regra consultada de dois lugares
vira módulo"*.

**O mapa para a tela.** O template continua com as classes `futuro`, `em_curso` e `concluido`,
porque testes da `010` e da `024` afirmam sobre essas substrings e o CSS depende delas. A fase
nova se traduz nelas uma a uma: `PLANEJADO` vira `futuro`, `EM_ANDAMENTO` vira `em_curso` e
`CONCLUIDO` vira `concluido`. O cancelado ganha a quarta classe, `cancelado`, com rótulo em texto
(`FR-766`).

**Descartado.**
- *Manter duas funções e um teste de equivalência.* Seriam duas réguas vigiadas por um terceiro
  artefato, e não uma régua.
- *Portal importar `supervisao`.* Inverte a dependência, pelo motivo acima.

---

## R-2 — O desfecho: o estado diz *se*, o ato diz *quando*

**Decisão.** A presença de desfecho é lida de `Edital.status` e de `ProcessoSeletivo.status`, cujos
valores finais são terminais e mudam por CAS (`processos/domain/finalizacao.py:10-11`). A data é
lida do `AtoAdministrativo` de operação `ENCERRAR` ou `CANCELAR` daquele agregado
(`processos/application/finalizacao.py:140,170,235,250`), que é append-only nas duas camadas. Um
selector novo em `processos/application/selectors.py`, `desfechos(editais)`, devolve, para uma
lista de Editais, o desfecho aplicável a cada um pela precedência da `D-003`. Faz **uma** consulta
aos atos, e só quando algum dos Editais ou Processos está em estado final.

**Por quê.** O estado já está carregado, porque o `select_related("edital", "edital__processo")` de
`selecao_publica` e de `selecoes_publicas` o traz, e ele decide sem consulta nenhuma na imensa
maioria dos casos. O ato é a fonte imutável da data, como o `FR-760` exige. `last_changed_at` foi
descartado porque é sobrescrito a cada transição.

**Ato ausente.** Se o estado é final e o ato não existe, a página diz o desfecho **sem data**
(`FR-775`: omitir, não inferir). Não deveria acontecer, porque a finalização grava os dois na mesma
transação desde 29/08, e o caso existe só para não fabricar data.

**Descartado.**
- *Ler só o ato.* Exigiria consulta por Edital na vitrine, para confirmar a ausência.
- *Ler só o estado.* Não tem data.

---

## R-3 — A situação pública é uma função, e o desfecho vence o período

**Decisão.** `portal/leitura.py` ganha `situacao_publica(periodo, desfecho)`, que devolve a chave e
o rótulo da marca:

- **com desfecho:** chave `encerrado_edital`, `cancelado` ou `encerrado_processo`, e rótulo do
  desfecho. Não há chave para o Processo cancelado, porque cancelá-lo exige todos os Editais em
  estado final, e o desfecho do Edital vence;
- **sem desfecho:** a marca de hoje (`SITUACAO_DO_CARTAO`), sem mudança.

A página e o cartão da vitrine passam a usar essa função, e `_periodo.html` não escreve frase de
prazo quando há desfecho (`FR-761`).

**O agrupamento da vitrine.** Hoje o grupo sai só do período (`agrupar_por_situacao`). Um Edital
encerrado antes do fim do período cairia em *"Inscrições abertas"*, e isso contradiz o `FR-761`.
O Edital com desfecho passa ao grupo *"Inscrições encerradas"*, o que é verdade: o sistema não
recebe mais inscrição dele (`recebe_inscricoes` exige `PUBLICADO`). No cartão, a marca diz o
desfecho, e isso o distingue do Edital que apenas teve o período encerrado (`FR-763`). O cancelado
continua fora da vitrine (`selecoes_publicas`, inalterado).

**Descartado.**
- *Quinto grupo, "Seleções encerradas".* A `024` fixou quatro grupos pelo que o candidato procura,
  e o Edital encerrado não é uma quinta coisa que ele procure. A marca basta.
- *Tirar o encerrado da vitrine.* Contradiz o `FR-763`, e a decisão *preservar × anunciar* da
  `024`: encerrado é registro consultável, e não oportunidade cancelada.

---

## R-4 — Agora e próximo são a lista de marcos da gestão, lida para o público

**Decisão.** `marcos_do_edital` (`supervisao.py:378-405`) já devolve os Eventos não concluídos e não
cancelados, em ordem cronológica, pela régua da `045`. A parte que não depende de `Edital` vai para
o módulo da `R-1`, como `marcos_pendentes(conteudo, agora)`. O portal a lê e separa **em
andamento** (todos) de **próximo** (o de início mais próximo entre os planejados, e todos os que
empatam com ele). A gestão continua montando `Marco` em cima da mesma função.

**Onde aparece.** No cabeçalho da página, junto do período, e só quando não há desfecho
(`FR-767`). Nada é dito quando a lista é vazia (`FR-768`).

**Descartado.** *Uma terceira leitura do cronograma para o portal.* É exatamente o que a `R-1`
elimina.

---

## R-5 — O prazo público é o mesmo cálculo da interposição, extraído, e não copiado

**Decisão.** O ramo *publicação* de `_janelas_pertinentes`
(`recursos/application/interpor.py:164-205`) não depende da inscrição: ele lê o conteúdo vigente
do Edital, a declaração do marco da publicação e `janela_da_publicacao(publicacao, declaracao)`.
Esse ramo vira uma função pública, `janela_da_publicacao_divulgada(publicacao)`, em
`recursos/application/selectors.py`. Ela devolve `(abre, fecha)` ou `None`, e
`_janelas_pertinentes` passa a chamá-la. O portal chama a mesma função. Assim, a página pública, o
acompanhamento e a recusa da interposição **não têm como discordar** (`SC-284`).

**Achado desta pesquisa, que corrigiu a spec.** A primeira versão da `D-005` mandava ler a norma
citada pelo ato. O código lê a **vigente**, na interposição, no acompanhamento e na conferência da
divulgação (`divulgacao/domain/publicabilidade.py:455-472`). A spec foi emendada para *"o que a
interposição aplica"*, e a divergência vigente × citada ficou registrada como pergunta do domínio
de recursos. A janela é retificável (`mutabilidade.py:357-359`).

**Quando se mostra.**
- **Página da publicação vigente:** aberto ou encerrado, com as duas datas.
- **Lista de vigentes na página do Edital:** só o aberto, com a data de encerramento.
- **Publicação sucedida:** nada. Ela leva à vigente.
- **`admits: false` e declaração ausente ou não computável:** nada (`FR-771`).

**Descartado.** *Recalcular no portal com `declaracao_do_marco` e `janela_da_publicacao`
diretamente.* São as mesmas duas chamadas, mas numa segunda composição delas, e a primeira mudança
na regra da interposição deixaria a página para trás.

---

## R-6 — O histórico dos resultados sai de um selector público, sem autor

**Decisão.** `divulgacao/application/selectors.py` ganha `historico_publico_do_edital(edital)`: toda
`PublicacaoResultado` do Edital, com `prefetch_related("sucessoras")`, agrupada por `(marco,
lista)`, da mais recente para a mais antiga. Cada linha leva natureza, data, os rótulos de
`_rotulos` e `vigente`.

- **A página do Edital** mantém a seção de vigentes como está, e acrescenta sob cada marco e lista
  um bloco recolhido, *"Publicações anteriores"*, quando houver alguma sucedida (`FR-772`).
- **A página de uma publicação** acrescenta a lista das anteriores da mesma cadeia, subindo
  `publicacao_anterior` (`FR-773`).

**Por que não reusar `historico_do_marco`.** Ele não filtra a lista, e numa lista de PPI misturaria a
cadeia da ampla concorrência (a decisão do eixo da lista, da `021`). Além disso traz `ato` com o
autor, e a página pública não deve carregar o que não mostra. O selector novo lê o que o público
já vê: natureza, data e o cabeçalho do conteúdo publicado.

**Descartado.** *Uma página de histórico por marco.* Seria endereço novo para o que cabe num bloco
recolhido da página que a pessoa já abre.

---

## R-7 — Custo de consulta: constante por página, e medido nos testes que já medem

| Página | Hoje | Depois | Como |
|---|---|---|---|
| Seleção | N | N + 1 a 2 | uma consulta de atos, só se houver estado final; o histórico troca a consulta de vigentes por uma que traz todas, com `prefetch` |
| Vitrine | N | N ou N + 1 | uma consulta de atos para **todos** os cartões finais de uma vez |
| Resultado | N | N + profundidade da cadeia | a cadeia é curta (preliminar → definitiva → correção), e a janela já sobe a mesma cadeia para achar a âncora |

`tests/portal/test_resultado_publico.py:212` e `tests/portal/test_sorteio_na_pagina_do_edital.py:143`
já capturam as consultas. As tarefas acrescentam a mesma verificação à vitrine com cartões
finais, para provar que a contagem não cresce com o número de cartões.

---

## R-8 — O que os testes existentes prendem, e o que muda

Medido por `grep` de `em_curso`, `Acontecendo agora` e `leitura.cronograma` em `tests/`.

- **Não mudam**, porque a régua nova dá o mesmo resultado:
  - `test_cronograma_publico.py` (o Evento sem término de vinte dias atrás continua concluído; o
    período sem término continua em curso);
  - `test_acompanhamento.py:89`;
  - `test_acessibilidade_do_portal.py:189` (o Evento com término em curso continua *"Acontecendo
    agora"*).
- **Mudam de propósito:** nenhum caso afirma hoje que o Evento pontual fica em curso até a
  meia-noite. O comportamento do dia não está preso por teste, e é isso que a `D-004` troca.
- **Nascem:**
  - o Evento pontual iniciado há uma hora é *concluído*;
  - o cancelado é *cancelado*;
  - a fase é igual em portal e gestão para os quatro tipos de Evento (`SC-283`);
  - os três desfechos, na página e no cartão;
  - a precedência da `D-003`;
  - agora e próximo;
  - a janela (aberta, encerrada, ausente, `admits: false`, definitiva do mesmo ato);
  - o histórico alcançável a partir da página do Edital e da página do definitivo;
  - nenhum dado de ator na projeção (`FR-776`).
- **`test_leitura_sem_escrita.py`** continua valendo sem mudança: a feature não escreve.
- **Varreduras.** `test_citacoes_de_requisito.py` lê os templates, e os comentários novos citam
  `FR-760`+, que esta spec define. A varredura de vocabulário da composição não lê o portal
  (lista literal, `test_vocabulario_da_composicao.py`), e nenhuma regra dela se aplica. Nenhuma
  view nova levanta `Http404`, então o inventário de negativas da `033` não muda.

---

## R-9 — O que fica de fora do plano, e por quê

- **A docstring defasada de `portal/views.py:8-10`.** É registro da spec, e não escopo (RC-103).
  Tocar o arquivo não autoriza corrigir o que a governança não pediu.
- **A API pública.** Nenhum endpoint muda. A situação derivada não vai para o JSON (spec, *Out of
  Scope*).
