# Pesquisa técnica — 015 Ordenação e Classificação

**Fase 0.** As decisões herdadas que a feature consome, e as questões técnicas que o desenho
precisava resolver antes da Fase 1.

## Decisões herdadas de `doc/decisoes-pre-vertical.md`

Estas quatro **não foram tomadas por esta feature**. Estão declaradas aqui porque a 015 as cita, e
uma decisão citada precisa ser legível dentro da feature que a lê — é o que
`backend/tests/test_citacoes_de_requisito.py` cobra, e a razão dele é a mesma que a Constituição dá
no Princípio V: citação que o leitor não consegue resolver quebra a rastreabilidade. O texto
integral, com o argumento completo de cada uma, está no documento de origem.

### D-1 — Resultado de Etapa sem Avaliação

`ResultadoEtapa.avaliacao` passa a ser anulável, com `origem` discriminando `AVALIACAO` de
`OCORRENCIA`, e `versao` passa a ser campo do próprio Resultado, exigido sempre — porque sem
Avaliação não existe o caminho `avaliacao__versao` que hoje reproduz a norma histórica.

**Consumida pela 015 assim:** a ordem lê `ResultadoEtapa.versao` como âncora normativa, e não a
alcança pela Avaliação. É extensão da 013, e precisa cair antes ou junto — sem ela, o Resultado por
Ocorrência ficaria fora de qualquer ordem.

### D-2 — Fatos do candidato que as regras consomem

O Edital declara quais fatos exige; a inscrição os coleta e os **congela na submissão**, contra a
`versao_aceita`. Cada fato tem identidade estável, mudar o tipo cria fato novo, e o escopo mínimo é
data e número inteiro.

**Consumida pela 015 assim:** é a fonte dos critérios de desempate por idade e por tempo de
experiência. Sem ela a feature não serve os Editais em vista. A coleta é território da 009.

### D-3 — Quantas inscrições um candidato pode ter num Edital

Campo publicado `maxInscricoesPorCandidato`, anulável, onde ausência significa sem limite.

**Consumida pela 015 assim:** não é dependência funcional — é dependência de **leva**. D-2, D-3 e o
conteúdo normativo desta feature elevam a mesma versão canônica, e planejá-las juntas é a diferença
entre uma elevação e três.

### D-4 — Barema fica fora do primeiro vertical

A apuração por critério e item permanece externa; a banca registra o total.

**Consumida pela 015 assim:** a pontuação de Etapa que os critérios de desempate leem é o total
consolidado, e não uma parcela. Nenhum critério pode apontar item de barema, porque não existe item.

## T-001 — O ato de emitir não inventa mecanismo nenhum

**Decisão:** emitir é `comando_de_comissao(actor, processo_id, operation="classificacao:emitir",
payload, idempotency_key)`, exatamente como `resultado:consolidar`.

**Racional:** o invólucro da 011 já entrega, nesta ordem, o que a spec exige: transação com
`timezone.now()` compartilhado, `select_for_update` sobre o `ProcessoSeletivo`, **reavaliação de
`pode_gerir_comissao` depois do bloqueio** e só então a reserva da chave
(`comissoes/application/__init__.py:45-63`). A inversão reserva-depois-de-autorizar é deliberada e
documentada em `:19-22` — reservar primeiro faria a repetição responder a quem perdeu a presidência.
FR-028, que pede reavaliação da autorização depois do bloqueio, está satisfeito por construção.

**Uma armadilha de nome, registrada para não se repetir:** `ATO = "resultado:consolidar"` em
`resultados/application/consolidacao.py:32` **não é uma permissão** — é o `operation` da reserva. Não
existe em `interface/identidade.py:PAPEIS`. A 015 não cria permissão nova (D-007): a autorização é
`comissao:gerir` **ou** presidência ativa no Processo
(`comissoes/domain/autorizacao.py:39-55`), e a recusa é 404 uniforme.

**Alternativas consideradas:** permissão própria `classificacao:emitir` — rejeitada porque a spec
manda consumir a autoridade constituída, e criar capacidade nova seria a 015 legislando sobre
segregação de poderes; ato sem bloqueio do Processo — rejeitado porque FR-030 exige que duas
emissões concorrentes produzam uma recusa, e sem `select_for_update` as duas leriam o mesmo estado.

## T-002 — Emissão concorrente recusada: onde a recusa nasce

**Decisão:** a segunda emissão é recusada por **uma constraint de unicidade parcial** sobre o ato
vigente do marco, e não apenas pela verificação em Python.

**Racional:** a clarificação fixou recusa, e não sucessão (FR-030). O bloqueio do Processo serializa
as duas transações, mas a garantia que sobrevive a um caminho de escrita futuro é a do banco — é o
mesmo raciocínio de `uq_resultado_inscricao_etapa`, e o projeto já trata invariante persistente como
constraint (Princípio I). A idempotência **não** cobre este caso: chaves diferentes são pedidos
diferentes, e `ctx.repetido` só responde pela repetição do mesmo pedido
(`shared/idempotency.py:6-17`).

**Alternativas consideradas:** confiar só no `select_for_update` do Processo — rejeitada porque o
bloqueio é do contêiner e some no dia em que outro caminho gravar a tabela; suceder em vez de recusar
— rejeitada pela clarificação, que exige recálculo e confirmação explícita (FR-031).

## T-003 — Imutabilidade do ato: append-only nas três camadas

**Decisão:** a tabela do ato entra em `TABELAS_APPEND_ONLY` (`seguranca/papeis.py:36`), ganha trigger
`BEFORE UPDATE OR DELETE` e trigger de coerência `BEFORE INSERT`, no molde de
`resultados/migrations/0001_initial.py:23-63`.

**Racional:** FR-029 exige que 100% das tentativas de alteração sejam recusadas sem efeito, e
`backend/tests/integration/resultados/test_imutabilidade_do_resultado.py` já prova esse tipo de
garantia com SQL cru, por fora do ORM. A coerência importa tanto quanto a imutabilidade: sem uma
trigger que impeça a linha de **nascer** errada, a append-only apenas congelaria o erro — é o
argumento textual de `0001_initial.py:1-14`, e vale igual aqui, porque a posição do ato afirma coisas
sobre Resultados de outra tabela.

**O que a trigger de coerência confere:** que cada posição aponte inscrição do mesmo Edital e do
mesmo Perfil do ato, e que os Resultados citados na proveniência sejam os da Etapa enumerada pelo
marco. O nome entra em `TRIGGERS_POR_APP` de `backend/tests/migrations/test_migrations.py:21-38`,
sem o que o teste estrutural não a enxerga.

**Alternativas consideradas:** confiar na função de emissão como único ponto de inserção — rejeitada
pelo mesmo motivo que a 013 registrou: a feature seguinte também escreverá nessa tabela.

## T-004 — Cálculo puro, leitura única, laço sem consulta

**Decisão:** o cálculo é função de domínio pura sobre `(participantes, resultados, regra_publicada)`,
e os conjuntos vêm de um seletor com número de consultas constante.

**Racional:** é o desenho de `resultados/domain/regra.py` mais `application/selectors.py`, cuja regra
declarada é "um conjunto por consulta, uma vez por listagem" (`selectors.py:3-7`). SC-002 dá 3
segundos a 1.000 participantes, e o teto só se sustenta se nada consultar por linha. Dois detalhes
que o código já aprendeu e que esta feature herda:

- **desduplicação por versão** (`selectors.py:66-79`): `conteudos_das_versoes` resolve uma linha por
  versão distinta. `select_related("versao")` traria mil cópias do Edital em JSON **sem mudar a
  contagem de consultas** — nenhum teste de orçamento denunciaria;
- **restringir o queryset em vez de materializar o conjunto** (`prontidao.py:113-156`), com
  `Exists`/`OuterRef`, por causa do defeito conhecido do `exclude()` com dois campos.

**Como se prova:** teste em `backend/tests/performance/` medindo a **derivada** com
`CaptureQueriesContext` em dois tamanhos, no molde de `test_resumo_da_etapa.py:35-50`. O teto de 3
segundos vira teste de orçamento de consultas, não de cronômetro: cronômetro em CI mede a máquina.

## T-005 — Auditoria: um evento por emissão, sem pontuação

**Decisão:** `auditar(actor, permissao=ctx.base.permissao, operation="CLASSIFICACAO_EMITIR",
aggregate=ato, now=ctx.now, correlation_id, reason, idempotency_key)`, **uma vez por ato** — e não
uma vez por posição.

**Racional:** `comando_de_comissao` não audita; a gravação é chamada explícita
(`avaliacoes/application/trilha.py:3-5`). A 013 audita por Resultado porque cada Resultado é um ato;
aqui o ato é a ordem inteira, e mil eventos por emissão inflariam a trilha sem acrescentar
responsabilização. O motivo é obrigatório (`trilha.py:47-48`), e a assinatura de `auditar` **não tem
por onde pontuação ou parecer caberem** — a omissão é de projeto, e serve a FR-048.

**Em aberto para a Fase 1:** se a emissão grava `AtoAdministrativo` além do `RegistroAuditoria`
(`com_ato_administrativo=True`). A consolidação usa o default `False`; emitir uma classificação é
ato com motivo próprio e é candidato natural ao registro completo.

## T-006 — A interface reusa o molde de POST da 013

**Decisão:** rota POST própria pendurada no caminho do marco, com
`@require_http_methods(["POST"])`, helper de guarda devolvendo `(ator, edital, marco)` ou `Http404`,
desfecho e erro na sessão, e POST-redirect-GET — o molde de
`interface/views.py:2206-2235`.

**Racional:** seis elementos, nenhum novo. A chave de idempotência é fresca por render e vem do
contexto (`views.py:2372-2375`), e o botão de emitir usa `formaction` sobre a mesma seleção quando
couber (`distribuicao.html:343-347`). A separação "consultar é de dois, agir é de um" vale igual:
ler o ato abre para `auditoria:consultar` (`_etapa_para_auditar`, `views.py:2806-2834`), emitir exige
a base de gestão. A resposta que carrega posição e fatos de desempate é `marcar_como_privada`, como
`resultados_da_etapa` já faz (`views.py:2690-2691`), o que atende FR-048.

## T-007 — Onde o marco mora no conteúdo publicado

**Decisão:** coleção nova aninhada no Perfil — `/profiles/*/classificationMilestones` —, com
identidade estável por item, no molde exato de `competitionModalities`.

**Racional:** FR-001 declara marcos **por Perfil**, e o aninhamento já tem precedente vivo: a
modalidade é emitida dentro do laço do Perfil (`publish_edital.py:101-125`), endereçada como
`/profiles/id=…/competitionModalities/id=…` (`retificacao.py:249`) e declarada em
`COLECOES_COM_CHAVE` (`publicacoes/domain/colecoes.py:18-30`). Coleção de raiz com `profileId`
exigiria uma referência a resolver onde o aninhamento resolve por posição na árvore, e criaria a
possibilidade de marco órfão que a topologia hoje impede.

Dentro do marco, os critérios de desempate são **lista ordenada** — a ordem é normativa (FR-014), e
por isso a posição no array é significativa, ao contrário das demais coleções, onde posição nunca
endereça. Cada critério tem `id` próprio para que a Retificação o alcance por identidade e não por
índice.

**Alternativas consideradas:** reusar `RegraNormativa.call_rules`, que é JSON reservado e nunca
consumido — rejeitada porque P-1 dos achados registra que aquele campo é o lugar da regra de
**chamamento**, que é da 016, e porque `RegraNormativa` pende da modalidade, não do Perfil: o marco
ficaria replicado por modalidade e a ordem única do Perfil (Assumptions) deixaria de ser
expressável.

## T-008 — A elevação 6→7, e por que ela é legítima aqui

**Decisão:** `SCHEMA_VERSION` vai a 7 e `elevacao.DEGRAUS` ganha o degrau `7`, com a coleção nova
elevando para **lista vazia**.

**Racional:** o módulo de elevação é explícito sobre quando a conversão é legítima e quando é
invenção: 2→3 e 3→4 não ganharam degrau porque *"dizer que um Edital não exige documento algum **é
dizer alguma coisa**"* (`publicacoes/domain/elevacao.py:8-14`). Aqui a ausência **tem** significado
declarável e verdadeiro: Edital publicado antes desta feature não declarou marco nenhum, e um Edital
sem marco não classifica. É a mesma forma da decisão D-2, que diz que "um Edital que não declara
fato nenhum continua sem campo nenhum".

**O que isso custa, e que não é opcional:** `elevar()` hoje só reescreve `conteudo["stages"]`
(`elevacao.py:101-112`), porque todos os degraus anteriores foram de campo de Etapa. Elevar uma
coleção **dentro de `profiles`** exige estender a função — é a primeira vez que a elevação desce um
nível. Sem isso, todo conteúdo v6 publicado fica irretificável por
`canonical_schema_version_mismatch` (`retificacoes.py:542-543`).

**Alternativas consideradas:** aceitar a irretificabilidade, como a 007 e a 009 aceitaram — rejeitada
porque aqueles Editais eram de implantação, e agora há conteúdo publicado em uso; deixar a coleção
fora do canônico — rejeitada porque contraria o Princípio II, que exige fonte autoritativa única
para critérios e regras de avaliação.

## T-009 — A verificação da forma não desce sozinha até o marco

**Decisão:** a validação do marco é função dedicada registrada em `validate_for_publication`, no
molde de `_faixa_do_percentual` (`editais/domain/validation.py:441-481`, registrada em `:627-633`).

**Racional:** `COLECOES_PUBLICADAS` só percorre coleções **de raiz** — `_violacoes_da_colecao` faz
`snapshot.get(colecao)` (`validation.py:312-350`) —, e a forma de dentro de `competitionModalities`
não é verificada campo a campo por decisão registrada (`validation.py:88-90`). Uma coleção aninhada
nova **herda essa lacuna por padrão**, e aqui ela não é aceitável: FR-010, FR-016 e FR-017 são todos
recusas na publicação (Etapa não classificatória enumerada, critério apontando item inexistente,
critério sem comportamento para valor ausente). Sem função dedicada, as três viram promessa de
código.

**O único guarda que pega coleção aninhada esquecida** é
`tests/integration/publicacoes/test_enderecamento.py:249-250`, que roda `colecoes_nao_declaradas`
sobre um snapshot realmente publicado. Ele entra na lista de testes desta feature de propósito.

## T-010 — O ato e suas posições: app novo, duas tabelas

**Decisão:** app `classificacao`, com `AtoDeOrdenacao` e `PosicaoNaOrdem`.

**Racional:** o Princípio I pede conceitos distintos com ciclos de vida distintos, e foi o mesmo
argumento que pôs `ResultadoEtapa` em app próprio. Duas tabelas, e não uma com JSON de posições: a
posição é consultada, filtrada e contada — SC-016 exige que posições atribuídas mais considerados sem
posição fechem com o universo —, e um JSON tornaria isso agregação em memória sobre mil linhas.

A proveniência de cada posição (valores usados em cada critério) fica **na posição**, porque é dela
que a consulta de FR-045 precisa; a proveniência do ato (Resultados que entraram, versão normativa,
regra) fica no ato.

**Alternativas consideradas:** posições como JSON no ato — rejeitada pela consulta; ato dentro do app
`resultados` — rejeitada porque ordenar não é resultado de Etapa, e a 016 crescerá em torno do ato,
não do Resultado.

## T-011 — Obsolescência: o que se compara, e como não fica caro

**Decisão:** o ato grava um **resumo do universo** — identidade do marco, versão normativa que o
governou, e o conjunto de Resultados que entraram, identificados e datados. A verificação de
obsolescência compara esse resumo com o universo de agora, em consulta de custo constante.

**Racional:** FR-033 e FR-034 pedem duas comparações distintas: entradas novas e **regra alterada**.
A segunda é barata e decisiva — basta a versão normativa gravada divergir da vigente, e o
`compatibilidade.py` da 013 já ensina a não comparar identidade de versão quando a diferença é
irrelevante (`resultados/domain/compatibilidade.py:1-6`). A primeira exige saber se apareceu
Resultado novo no universo, o que é uma consulta de existência sobre `(edital, etapa_id)`, não uma
por participante.

**A armadilha registrada:** não usar `select_related("versao")` para trazer o conteúdo do Edital de
cada Resultado. `conteudos_das_versoes` resolve uma linha por versão distinta, e o alerta de
`selectors.py:69-72` é que a alternativa errada **não muda a contagem de consultas** — nenhum teste
de orçamento denunciaria.

## T-012 — O tamanho real desta feature, dito antes do plano

**Constatação:** esta é a maior feature desde a 012, e o peso **não** está no cálculo — está no
conteúdo publicado.

O levantamento mapeou **19 pontos de toque** para acrescentar uma coleção aninhada ao Perfil: modelo,
migration, serializer, `replace_draft` com a guarda de identidade alheia
(`editais/application/draft.py:30-58`), validação de elaboração, emissão no snapshot, elevação de
versão, declaração em `COLECOES_COM_CHAVE`, validação de publicação, quatro funções em `forms.py`,
fragmento HTMX e reexibição, template, catálogo de Retificação, PDF, consulta pública, `openapi.yaml`,
fixtures e `seed_demo`. Só depois disso existe regra publicada para o cálculo ler.

**Consequência de planejamento, e ela é do usuário:** D-2 acrescenta outra coleção normativa (os
fatos declarados) e sobe a mesma versão. Feitas em levas separadas, são duas elevações, dois degraus
em `elevacao.py` e dois caminhos de leitura — e, pior, os critérios de desempate por idade e por
tempo de experiência ficam sem valor para ler até a segunda cair. O plano assume a leva conjunta como
hipótese e a declara na §Fases; se a decisão for outra, o que muda é o fatiamento, não o desenho.
