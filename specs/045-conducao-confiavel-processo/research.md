# Phase 0 — o que foi medido

**Quando**: 26/09/2026, contra a `main` `2ffe5a2`. **Método**: o da `038` — ler a **condição**, e não
a mensagem; e, para cada requisito, achar a regra que **já existe** antes de escrever a que falta.

**Placar**: a spec não tinha marcador de clarificação, e a medição não abriu nenhum. Das seis frentes,
**quatro são leitura de regra que já existe** (ausência, recurso, fase, cobertura), **uma é regra nova
pequena** (o aviso da Etapa sem Evento) e **uma é retirada** (o `UX-001` e o `UX-002` saem do
catálogo). O custo real está nos testes que prendem o comportamento antigo — contados em `R-8`.

---

## R-1 — A ausência: a decisão já está calculada, e é descartada

**Decisão**: a frase de ausência escolhe entre a global e a relativa por `all(alcancadas.values())`,
sobre o **mesmo** `alcance(ator, processo)` que a página do Processo já lê para decidir se mostra a
região (`views.py`, `processo_detalhe`, `alguma = any(...)`). A Supervisão faz a mesma conta.

**Por quê**: o alcance é a única entrada que depende só do leitor. `alcance_no_edital` retira espécies
pelo estado do Edital, e usá-lo aqui faria a frase variar com o que o Edital fez — uma informação
sobre objetos, e não sobre o leitor (`FR-731`, caso-limite *"O alcance muda com o estado do Edital"*).

**E o vazamento se fecha por construção**: a escolha é tomada **antes** de os sinais serem montados,
a partir de um dicionário de permissões. Não há caminho de dado entre o que o leitor não alcança e a
frase. O teste prende isso comparando a página de um mesmo leitor com e sem condição fora do alcance
— as duas respostas precisam ser **idênticas** no trecho da Atenção.

**Alternativa descartada**: enumerar na frase o que o leitor acompanha (*"entre recursos e
divulgação"*). Não vaza — sai das permissões dele —, mas cada espécie nova obrigaria a revisar uma
lista de nomes na frase, e a spec não o pede (`UX-084`).

---

## R-2 — O recurso: o impedimento da admissibilidade é o mesmo cálculo

**Decisão**: `sinais_do_recurso` passa a ler as peças `AGUARDANDO_ADMISSIBILIDADE` **e**
`AGUARDANDO_JULGAMENTO` de uma só chamada a `recursos_do_edital` (que já carrega todas e filtra em
Python), e a partição `travadas`/`soltas` corre sobre a união.

**Por quê — medido**: admitir chama `exigir_elegibilidade(actor, peca)` **sem** `etapa_id`
(`recursos/application/admitir.py:54`), e sem `etapa_id` a regra considera só o Resultado atacado
(`recursos/domain/elegibilidade.py:85-108`). É exatamente o alcance que `impedidos_por_recurso` já
usa (*"o Resultado atacado quando existe"*). **A mesma partição vale para as duas fases sem mudar uma
linha do cálculo** — e é isso que a `D-002` precisava para ser a opção barata.

**Custo**: nenhuma consulta nova. `recursos_do_edital` já trazia as peças de todas as situações; a
mudança é o filtro em Python, e o guarda de escala (`test_dobrar_os_recursos_pendentes_nao_dobra_as_
consultas`) continua valendo.

**A fase na mensagem** sai de contar as situações das peças que o sinal conta, sem consulta: as linhas
já trazem `situacao`. Três formas: só admissibilidade, só julgamento, as duas (`UX-085`, contrato).

**A contagem da ação** (`interface/acoes.py:118-128`) troca `Recurso.objects.filter(...).count()`
pela contagem das pendentes — **uma consulta**, como hoje: pendente é não ter juízo, ou ter juízo que
admitiu e não ter decisão. Cabe num `filter` com `Exists`, sem materializar peça.

**Alternativa descartada**: reusar `recursos_do_edital` na ação. Materializaria todas as peças do
Edital para contar, numa tela — a lista de Processos — que monta ações para vários Editais.

---

## R-3 — A fase: duas réguas que já existem, e nenhuma nova

**Decisão**: a fase ordinária é lida por uma função pura em `editais/domain/calendario.py` —
`fase(inicio, termino, *, agora)` —, que devolve planejado, em andamento ou concluído a partir de
`vencido`, que já está no mesmo módulo. O período de inscrições **não** passa por ela: a fase dele é o
estado de `periodo_de_inscricoes` (futuro → planejado, aberto → em andamento, encerrado → concluído),
que o pulso já calcula por Edital em `periodo_do_edital`. `CANCELADO` é decidido por quem chama, antes
das duas.

**Por quê**: a `037` (`FR-547`) fez da régua um módulo para que o selo e a Revisão não discordassem.
Uma terceira função com a mesma pergunta seria o defeito que ela removeu. E o período de inscrições
tem régua **própria** que decide direito — quem se inscreve —, com a qual a fase não pode discordar:
sem término, o período segue aberto, enquanto a régua geral vence o Evento pelo início.

**Onde a fase aparece**: só no pulso — os próximos marcos da Supervisão e da página do Processo, que
hoje escrevem *"declarado planejado"* (`supervisao.html:119`, `processo_detalhe.html:121`). A
`Marco.declarado` passa a `Marco.fase`, e o template diz *em andamento* do marco em curso (`UX-088`).

**E o corte dos próximos marcos se alinha**: `marcos_do_edital` tira o marco quando `termina <= agora`,
com `termina = fim or inicio` — uma quarta regra, com `<=` onde a régua usa `<`, e que tira da lista o
período de inscrições sem término no instante em que ele abre. Passa a tirar o marco **concluído**, e
só ele. É a linha *"alinha o pulso a elas"* da spec.

**O portal fica como está** (`portal/leitura.py`, `_situacao_do_evento`) — registrado na spec.

---

## R-4 — A entrada da fase: a API é o único caminho, e a tela já não oferece

**Medido**: a tela de composição não tem campo de `status` (`_evento.html`); ela **preserva** o valor
guardado ao regravar a etapa (`PRESERVADO_DA_ETAPA`, `views.py:1770-1771`). A Retificação não o
oferece (derivado na `026`) e grava `PLANEJADO` no Evento que acrescenta. O reaproveitamento o
reinicia em `PLANEJADO`. **O único caminho que aceita `EM_ANDAMENTO` ou `CONCLUIDO` é a API do
rascunho** (`editais/api/serializers.py:185-188`).

**Mas a tela não passa pela API.** A composição reenvia o `status` guardado direto a `replace_draft`
(`interface/forms.py:1314-1330`, `eventos_persistidos`). Uma recusa só no serializer deixaria a tela
carregar para sempre o `EM_ANDAMENTO` que a API gravou antes; uma recusa no domínio, sem mais nada,
faria a tela recusar gravar um rascunho antigo por um valor que a pessoa nunca digitou.

**Decisão**:

- **A regra mora no domínio**, em `replace_draft` (`editais/application/draft.py`): `status` aceita
  `PLANEJADO` e `CANCELADO`; os outros dois são recusados com *"A fase do Evento é derivada das datas;
  só o cancelamento é declarado."* A API herda a recusa como 400, e o `ChoiceField` do serializer
  passa a oferecer os mesmos dois valores, para que o erro chegue cedo e com o campo.
- **A tela normaliza o que só herdou**: ao preservar o `status` guardado, qualquer valor que não seja
  `CANCELADO` vira `PLANEJADO`. Não é apagar declaração: é um rascunho em elaboração, que nunca foi
  publicado, carregando um valor que a leitura não considera mais.
- `PLANEJADO` continua aceito porque é o valor que o próprio sistema escreve como *não cancelado* —
  recusá-lo quebraria o cliente que devolve o que leu.

**O que não muda**: a forma do conteúdo publicado (versão 17), o `derivado()` da `026`, e o conteúdo
já publicado com qualquer valor — que a leitura trata como *não cancelado*.

**Armadilha medida**: o ajudante de teste `levar_a_publicacao` (`tests/fixtures/publicacao.py:63-68`)
**não confere** o status do `PUT` do rascunho. Um 400 ali é engolido e aparece depois como
`blocking_findings` na submissão, com causa enganosa. Conferi-lo é a primeira tarefa desta frente —
antes de a recusa existir.

---

## R-5 — O aviso da Etapa sem Evento

**Decisão**: um achado `Severity.WARNING` com código **próprio** — `stage_without_schedule_event` —,
dentro de `_coerencia_das_etapas` (`editais/domain/validation.py:1238`), ao lado da conferência do
Evento **inexistente**, com caminho `/stages/id=<uuid>/scheduleEventId`. **Só para o ato de
publicação**: a função passa a receber o `ato`, como `_eventos_vencidos` e `_marco_sem_regra_de_corte`
já recebem.

**Por quê o código próprio**: `advertencias_do_ato` (`publicacoes/application/retificacoes.py:583-590`)
descarta aviso cujo código coincida com o de um impeditivo, e
`tests/unit/editais/test_invariantes_da_declaracao_unica.py:145-157` prende que os dois conjuntos não
se cruzam. Reusar `field_constraint_violated` faria o aviso sumir onde deveria aparecer.

**Por quê só na publicação**: na confirmação de uma Retificação o aviso seria irremediável — o
`scheduleEventId` é estrutural (`026`), a tela da Retificação não o oferece, e a `D-003` diz
exatamente que fato sem remédio naquele momento não se apresenta como pendência.

**Onde aparece, sem mudança de mapeamento** — `_destino` já leva `/stages/...` à etapa das Etapas:

- na etapa *Etapas* do assistente e na *Revisão*, como *"Aviso"*;
- na página do Edital, em *"Validação do conteúdo"*, **inclusive publicado** — `detalhe` chama
  `_pendencias` para qualquer estado (`views.py:2791`);
- na confirmação de submeter e de publicar, que listam avisos e só recusam por erro.

**Não bloqueia nada**: submeter e publicar recusam só por `blocking_findings`; `_motivo_previsivel`
olha só `"erro"`. **Não mexe no hash**: o conteúdo canônico não carrega achados.

**Agrupar as repetidas**: o seed tem duas Etapas sem Evento por Edital. O código entra em
`RESUMO_DAS_REPETIDAS` (`templatetags/interface_extras.py:335-372`), para que dez Etapas sem Evento
sejam uma linha, e não dez.

**Ressalva registrada**: a página do Edital monta o conteúdo a partir das linhas do rascunho, e não da
versão consolidada. Para este aviso não faz diferença — nenhuma Retificação muda o vínculo.

---

## R-6 — A cobertura: a população certa já existe, e a distribuição já a tem na mão

**Medido**: `resumo_da_etapa` agrega sobre **toda inscrição submetida** do Edital
(`avaliacoes/application/selectors.py:204-241`), com ou sem panorama — o panorama só acrescenta
chaves. `inscricoes_da_etapa`, a lista, filtra por `panorama["participantes"]`. O painel chama o
resumo **sem** panorama (`supervisao.py:686`).

**Decisão**:

- **Na distribuição**, o resumo restringe a agregação por `id__in=panorama["participantes"]` — o
  **mesmo** conjunto que a lista usa, já materializado, sem consulta nova. O teto de
  `tests/performance/test_resumo_da_etapa.py` (`<= 6`) continua valendo.
- **No painel**, que não monta panorama por Etapa, o resumo recebe a restrição como consulta:
  `restringir_a_participantes(..., prefixo="")`, que dobra as três regras na própria agregação. Custo
  **constante por Etapa** — a leitura do conteúdo e a pergunta do gate —, e os orçamentos da
  Supervisão são relativos à população, não absolutos (`test_fronteira.py`, `test_sinais.py`).
- **O resumo não importa `resultados`**: a restrição chega por parâmetro, como o panorama já chega, e
  pela mesma razão (`resultados` lê `avaliacoes`; o inverso seria ciclo).
- **O filtro da lista casa com o número**: *"sem avaliador suficiente"* conta `atribuidas < previstas`,
  inclusive zero; o filtro `incompleta` exclui zero. O link do número passa a um filtro que conta o
  mesmo conjunto — `carente`, `atribuidas < previstas` —, e `incompleta` continua existindo para quem
  o usa. *"Todas"* passa a mostrar os participantes, que é o que lista.

**E a coerência entre as duas formas da mesma regra fica presa por teste**: para um mesmo cenário com
eliminada antes, aguardando a anterior e fora do corte, o painel (consulta restrita) e a distribuição
(panorama) produzem o **mesmo** denominador.

---

## R-7 — O sinal que fica: quem pode, quem não pode, e onde se diz

**Medido**, espécie por espécie e papel por papel, para as oito que ficam no catálogo. *"Gestão"* é
`pode_gerir_comissao`: a permissão de gerir a comissão **ou** a presidência ativa
(`comissoes/domain/autorizacao.py:65-81`). Julgador, Auditor e Publicador não abrem a Supervisão
(404) e leem a Atenção só na página do Processo.

| Espécie | Leitor | Pratica o ato? | A condução existe? | O que esta feature faz |
|---|---|---|---|---|
| `UX-003`, `UX-063` | gestão | sim — a distribuição recusa só com inscrições abertas, e a tela o diz | n/a | nada |
| `UX-004`, ato calculado | gestão | sim | n/a | nada |
| `UX-004`, ato calculado | Auditor | não | **sim** — `ordenacao.html:223-249`, por `frase_do_aviso` | nada |
| `UX-004`, ato sorteado | Auditor | não | **não** — `sorteio.html` não tem condução | **acrescenta** a condução, pelo mecanismo único |
| `UX-005`, `UX-064` | Julgador livre | sim | n/a | nada |
| `UX-005`, `UX-064` | Julgador impedido | não — `appeal_judge_barred` | **sim** — a peça diz o impedimento e *"Aguardando apreciação por quem não esteja impedido"* | nada. *Corrigido na análise*: a primeira leitura contou isto como lacuna, mas o Julgador impedido **tem** a permissão de julgar, e *"peça a alguém com a permissão de julgar"* seria falso para ele (`037`, `FR-544`). O que lhe falta não é permissão, e a peça já diz o quê |
| `UX-046` | gestão sem a permissão de retificar | não | **não** — o sinal fica sem caminho e mudo | **acrescenta** `CONDUCAO_DA_RETIFICACAO` ao sinal (já existe, `views.py:4363`) |
| `UX-046` | quem pode retificar | sim | n/a | nada — recebe o caminho, e não a frase (`037`, `FR-544`) |
| `UX-065` | gestão | sim, havendo quadro e ordem | n/a | nada |
| `UX-065` | Auditor | não | **não** — `ocupacao.html` só diz *"Ocupação ainda não apurada"* | **acrescenta** a condução |
| `UX-066` | Publicador | sim, quando publicável | parcial — ver abaixo | **acrescenta** a condução no caso bloqueado |

**O Publicador diante de ato obsoleto** (`UX-066` e `UX-004` sobre o mesmo ato): a prévia bloqueia com
*"Emita o ato sucessor na tela de classificação do marco"*, e esconde o link de quem não abre a
classificação (`previa_de_publicacao.html:143`). É mandar a pessoa a uma tela que ela não abre, sem
dizer a quem pedir. Entra na `FR-740` pela mesma frase da ordenação: gestão ou presidência.

**Custo**: três frases novas, todas pelo mecanismo único (`037`, `FR-543`), e uma quarta que já existe.
Nenhuma consulta: as telas já sabem se o leitor pode agir (`pode_emitir`, a elegibilidade da peça).

**O `UX-004` e o `UX-005` num Edital encerrado não são o defeito da `D-003`.** A spec os deixou como
candidatos, e a medição os absolve: nenhum serviço de `classificacao/`, `recursos/` ou `ocupacao/`
consulta o estado do **Edital** — reemitir a ordem e julgar o recurso continuam possíveis enquanto o
**Processo** não estiver em estado final. A assimetria da `038` está certa para eles; o que estava
errado era a premissa escrita para o `UX-001` e o `UX-002`, que saem.

**Achados, registrados e não tomados** (entram na spec, *Out of Scope*):

- **O `UX-065` dispara em recorte sem quadro**, onde ninguém pode apurar (`sem_quadro_publicado`). A
  tela aponta a Retificação, e o fato se sobrepõe ao `UX-046`. É o defeito da `D-003` em outra espécie.
- **Num Processo em estado final**, o `UX-004` leva à ordenação, a tela oferece o formulário
  (`pode_emitir` só confere a gestão), e o envio recusa com 409. É oferta de ato impossível na tela
  de destino, e não no painel.
- **A tela do sorteio não mostra que o ato sorteado está obsoleto** — o único "obsoleto" dela é o do
  corte. O sinal leva a uma tela que não mostra a condição que o produziu.
- **A frase da ordenação para o Publicador** (*"Divulgá-lo não é ato seu: peça a alguém…"*,
  `ordenacao.html:66`) é redigida à mão, e não pelo mecanismo único.

---

## R-8 — O que prende o comportamento antigo

Lido, não executado. **Recontar na implementação**: a `034` previu oito casos alterados e entregou
doze.

| Frente | Apagados | Reescritos | Onde |
|---|---|---|---|
| `UX-001` e `UX-002` saem | 4 casos e a tabela-verdade inteira (`COMBINACOES`, `edital_da_tabela_verdade`); a fixture `edital_divergente` | ~8 | `integration/supervisao/test_sinais.py:38-175`; `interface/test_supervisao.py` (:271, :374, :407, :430, :572); `integration/supervisao/test_autorizacao.py:143-172`; `unit/interface/test_supervisao.py:10` (dez → oito) |
| o guarda do catálogo | — | 1 | `acceptance/test_supervisao_do_processo.py:112-146` — ver abaixo |
| o edital parado | — | 1, **provável** | `test_sinais.py:1010-1040`: as espécies antigas que ele espera ver hoje são o `UX-001` da *Prova didática* sem Evento; precisa de `UX-004` ou `UX-046` montado |
| `Marco.declarado` | — | 1 | `interface/test_supervisao.py:516-523` conta marcos pela regex `declarado (...)` |
| a recusa da fase | — | fixtures | `conftest.py:252-267` (`edital_c`, `status_do_periodo="EM_ANDAMENTO"`), `fixtures/supervisao.py:27-91`, `interface/test_supervisao.py:199`, `acceptance/...:65,78` — **o parâmetro deixa de ser necessário** e sai; `interface/test_round_trip_do_rascunho.py:357` passa a prender a normalização; `integration/editais/test_reaproveitamento.py:185,645` move o `CONCLUIDO` da origem para o ORM |
| o aviso novo | — | 1 | `unit/editais/test_etapas.py:162-164`: filtra por caminho, e não por severidade |

**O guarda do catálogo tem uma armadilha.** O teste lê o bloco da `FR-024` da `022` e compara
`re.findall(r"UX-\d{3}")` com `ESPECIES`. O texto riscado do bloco — `~~…UX-001 a UX-005~~` — contém
`UX-001`: tirar só as linhas da tabela deixa o teste vermelho. **Decisão**: o teste passa a ler o
requisito **vigente** — a `FR-744` desta spec —, como a `038` o fez passar da `FR-024` para a
`FR-565`, e continua exigindo `SUBSTITUÍDA` no bloco da `022`. O bloco da `022` ganha a nota de que a
`FR-565` foi substituída pela `FR-744`, sem apagar a tabela de 19/09 — ela é o que a decisão daquele
dia decidiu.

**E as fixtures que passam a emitir o aviso não quebram**: `comissao.py:50-56`, `snapshot.py:329-339`,
o seed e ~10 arquivos com `scheduleEventId: None` só conferem impeditivos ou filtram por código.
Conferido arquivo a arquivo pelo mapeamento; nenhum teste afirma *"Nada pendente"* nem zero avisos.
