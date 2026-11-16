# Research: A distribuição coerente com a agenda e a programação de quem avalia

Decisões técnicas do plano, em `T-NNN`. As decisões de produto são as `D-NNN` da [spec](spec.md).
Cada questão diz o que foi decidido, por quê, e o que foi descartado. A evidência é o código da
`main` em `619a4ae0`.

---

## Incremento 1

### T-001 — O conflito e a programação moram em `avaliacoes`, e leem a agenda

**Decisão.** Um módulo de domínio puro, `avaliacoes/domain/conflito.py` (sobreposição, varredura por
pessoa, sem banco), e um de aplicação, `avaliacoes/application/programacao.py` (Atribuições ativas ×
horários, a programação de uma pessoa, a coerência de uma Etapa). Os horários vêm de uma função nova
de leitura em `agendamento/application/leitura.py`, `horarios_do_edital(edital)`.

**Por quê.** A dependência já corre neste sentido: a Distribuição é de `avaliacoes`, e é ela que
precisa do horário; `agendamento` não importa `avaliacoes` em lugar nenhum, e continua sem importar.
A agenda não sabe quem avalia (a decisão da `167` de que a banca não é grupo de pessoas); quem cruza
é quem distribui. A tela da remarcação, que é de `agendamento`, chega à programação pela camada de
interface, que já compõe os dois apps (a tela da Ocorrência faz isso desde a `167`).

**Descartado.** Pôr o conflito em `agendamento`: faria a agenda importar a Atribuição, e o app que
hoje é só "quando e onde" passaria a saber "quem avalia".

### T-002 — Um horário por inscrição e Etapa, de uma de duas fontes, em quatro consultas

**Decisão.** `horarios_do_edital(edital, *, so_publicados=False)` devolve, para cada agenda do Edital,
os pares `(etapa_id, inscricao_id) → HorarioMarcado(inicio, fim, banca_id, banca_nome, fonte, remarcado_em)`:
`fonte = PUBLICADO` com os vigentes (`_vigentes`, que já existe) quando a agenda tem publicação, e
`fonte = MONTAGEM` com os `Agendamento` quando não tem (FR-8201). Quatro consultas fixas: agendas,
publicações, vigentes, agendamentos — nenhuma por pessoa.

A Programação e o aviso chamam com `so_publicados=True`; a Distribuição, o conflito e a coerência,
sem.

**Por quê.** O `Agendamento` também tem `inicio` e `fim`, e as duas fontes nunca coexistem para a
mesma agenda: publicada, o rascunho deixa de valer (a `167` lê só o publicado depois do ato). Uma
função só evita que a Distribuição e a Mesa discordem sobre o que é "o horário".

### T-003 — O conflito é uma varredura por pessoa, e a pessoa é o identificador

**Decisão.** `conflito.conflitos(compromissos)` recebe, por pessoa, a lista de
`(inicio, fim, inscricao_id, etapa_id, banca_nome)` e devolve os pares que se sobrepõem
(`a.inicio < b.fim and b.inicio < a.fim`), ordenando por início e varrendo — O(n log n) por pessoa.
`conflito.cabe(compromissos_da_pessoa, horario)` responde a pergunta do lote e do rodízio.

**A pessoa é o `identity_subject`**, e não a linha de `MembroComissao`: quem saiu e voltou à comissão
tem duas linhas e uma agenda só. É o mesmo critério que a `012` usa para a conclusão única e o
impedimento.

**Os compromissos de uma pessoa** são as Atribuições ativas dela **em todo o Edital** (FR-8202),
cruzadas com `horarios_do_edital`: duas consultas a mais, Atribuições e horários, para a Etapa
inteira.

**Conflito passado** (Edge Cases): o par em que as duas entrevistas já terminaram vem marcado
`passado=True`; ele aparece, e não impede o aviso (FR-8221).

### T-004 — A recusa no lote é mais uma regra sobre a linha, ao lado do impedimento

**Decisão.** Em `distribuir`, depois de `_motivo_da_recusa` e da exposição, um terceiro teste por par
`(membro, inscrição)`: se a inscrição tem horário nesta Etapa e o horário não `cabe` nos compromissos
da pessoa, a linha é recusada com `CONFLITO` — "Ana Lima já tem entrevista das 08:30 às 08:45 de
25/11, na Banca 02". Os compromissos são lidos **depois** da trava (dentro do `comando_de_comissao`,
T-006) e **crescem dentro do lote**: cada atribuição criada acrescenta o horário dela aos
compromissos da pessoa, de modo que duas linhas simultâneas do mesmo lote não passam juntas
(FR-8205).

As inscrições do lote passam a ser percorridas **na ordem da agenda** — dia, horário, banca;
protocolo para as sem horário, depois —, para que a linha recusada num conflito interno do lote seja
sempre a mais tarde, e o resultado seja reprodutível.

**A recusa entra no resultado declarado**, agrupada como as outras (`_agrupar`). A trilha continua
registrando o que foi criado, um evento por Atribuição; as recusas por impedimento não vão à trilha
hoje, e a de conflito segue a mesma regra (a FR-8232 foi ajustada a isso).

**Inscrição sem horário** não passa pelo teste (FR-8206, `D-002`).

### T-005 — O rodízio recebe os horários e os compromissos, e continua puro e assinado

**Decisão.** `rodizio.propor(...)` ganha dois parâmetros opcionais: `horario` (inscrição → intervalo,
ou ausente) e `compromissos` (pessoa → intervalos que ela já tem). Com eles:

1. as inscrições são percorridas na ordem da agenda (as sem horário depois, por protocolo);
2. o membro cujo intervalo não `cabe` é **inelegível** para aquela inscrição, como o impedido;
3. a projeção acrescenta o intervalo à pessoa escolhida, como já acrescenta a carga;
4. a inscrição que fica sem cobertura por isso sai em `fora`, com o motivo "Todas as pessoas
   selecionadas têm entrevista neste horário" — e, se o motivo for misto, o de hoje.

Sem os parâmetros, o comportamento é o de hoje, byte a byte: Etapa sem agenda não muda.

**O que não muda** (Q-C): menor carga projetada, desempate pelo identificador, impedimento,
exposição, conferência sob trava pela `assinar(pares)`. A assinatura continua sobre os pares; como a
proposta é determinística sobre o mesmo estado, uma remarcação entre ver e confirmar muda os pares, e
a confirmação recusa com `proposta_mudou`, como já recusa hoje.

**A evidência** é a simulação do estudo, que vira teste (SC-2842): 43 × 6 × 3 com dupla avaliação,
dez ordens de protocolo, zero conflito.

### T-006 — A concorrência: o Processo já serializa quase tudo, e o que sobra é aceitável por construção

**O que o código já faz.** `comando_de_comissao` (`comissoes/application/__init__.py`) abre a
transação com `ProcessoSeletivo.objects.select_for_update()`. Passam por ele:

| Gesto | Trava |
|---|---|
| Distribuir em lote, confirmar o rodízio, remover atribuição | Processo → Edital |
| Publicar a agenda | Processo → agenda |
| Remarcar, incluir, cancelar | Processo → agenda |
| Configurar, preencher, agendar à mão, liberar (montagem) | **só a agenda** (`_agenda_travada`) |

**Consequências:**

1. **Distribuir × distribuir** e **distribuir × remarcar/incluir/cancelar** são serializados pelo
   Processo. A distribuição lê os compromissos depois da trava; a remarcação, também. Nenhuma das
   duas vê o estado de antes da outra. Não é preciso trava nova.
2. **Distribuir × montagem** não é serializado: a montagem trava só a agenda, e uma mudança da
   montagem no meio de uma distribuição pode criar um conflito que nenhuma das duas viu. É aceitável
   **por construção**: a montagem já pode criar conflito (`D-003`, FR-8208), e ele aparece na
   leitura seguinte, na Distribuição e na conferência da agenda. Pôr a montagem sob a trava do
   Processo serializaria a comissão inteira durante o ajuste da grade, que é o gesto mais frequente
   da `167`, para proteger um caso que já é permitido.
3. **Ordem das travas.** Nenhum gesto novo trava em ordem diferente: Processo antes de Edital, e
   Processo antes de agenda. A distribuição não passa a travar a agenda — só lê.

**A confirmação da remarcação diz quem ficará em conflito — e confere que é isso mesmo.** Q-A exige
que a confirmação identifique quem ficará em conflito. Entre a tela e o POST, uma distribuição pode
criar ou desfazer um conflito. Por isso o POST leva a **assinatura dos conflitos anunciados** (o
resumo dos pares pessoa × horário que a tela mostrou), e o comando, sob a trava do Processo,
recalcula: se diferir, recusa com `conflitos_mudaram` (409) e a tela volta com a lista nova.

**Como o comando recalcula sem importar `avaliacoes`.** `remarcar(...)` e `incluir(...)` ganham dois
argumentos: `assinatura_dos_conflitos` (o que a tela anunciou) e `conflitos_no_horario` — uma função
`(edital, etapa_id, inscricao_id, inicio, fim) → (assinatura, avaliadores)` que a interface injeta,
apontando para `avaliacoes.application.programacao`. O comando a chama **dentro** da transação,
depois de `comando_de_comissao` e da trava da agenda, e grava `avaliadores` no `reason` do evento do
ato (FR-8232). Sem a função (chamadas de hoje, testes da `167`), não há conferência nem registro: o
comportamento é o de hoje. É a mesma inversão que a `167` já usa para a participação, lida por
função e não por import do app que a calcula. É o mesmo
mecanismo da `assinatura` da prévia da `167` e da proposta do rodízio. A remarcação **nunca** é
recusada por haver conflito — só por ele ter mudado sem ser dito.

**Avisar × mudar (Incremento 2).** O gesto de aviso passa por `comando_de_comissao`; o estado da
programação que ele grava é o do instante, sob a mesma trava das mudanças. Uma montagem não muda o
que é publicado, e por isso não toca a programação do aviso.

### T-007 — A Mesa ganha uma visão, e não outra tela nem outra consulta por linha

**Decisão.** `minha_etapa` aceita `?visao=programacao|inscricoes`. Numa Etapa com agenda publicada, o
padrão é `programacao`; sem, a visão não existe e a Mesa é a de hoje. A programação reaproveita a
consulta das Atribuições da `mesa()` (`_so_participantes`, a mesma autorização da FR-020 da `012`) e
acrescenta uma consulta, os vigentes dessas inscrições nesta Etapa, com `select_related("banca")`.
Os filtros-contagem valem para as duas visões.

**Sem paginação na Programação.** Ela é agrupada por dia; dias passados vêm recolhidos no fim. Uma
pessoa numa Etapa de entrevista tem dezenas de entrevistas, e não centenas; o teste de escala da Mesa
(`tests/performance/test_escala_da_mesa.py`, quinhentas atribuições) ganha o caso da Programação,
que tem de pagar o mesmo número de consultas com 5 e com 500.

**O nome do candidato** sai de `Inscricao.nome`, que a ficha da Mesa já mostra a quem avalia.

### T-008 — A sala vem da banca do horário vigente, só como botão, só na resposta privada

**Decisão.** O acesso é `HorarioPublicado.banca.acesso`, como a área do candidato já lê
(`HorarioDaInscricao.sala`, que só aceita `http(s)://`); no presencial, o local por extenso. A
resposta já é marcada privada pela `minha_etapa` (`marcar_como_privada`). Nenhum outro caminho — a
agenda publicada da gestão, a Distribuição — passa a mostrar a sala por causa desta feature.

**A redação da FR-7229 da `167`** é revista no PR do Incremento 1 (T-013).

### T-009 — A próxima entrevista em Minhas atividades sai numa consulta agregada

**Decisão.** `programacao.proximas(ator, atribuicoes)` devolve `{(edital_id, etapa_id): (inicio,
banca_nome)}` numa consulta: os vigentes com `inicio >= agora` das inscrições com Atribuição ativa do
ator, com `Min` por Etapa. `linhas_de_avaliacao` acrescenta o trecho "próxima entrevista …" ao
`lugar`.

**Por quê.** `tests/performance/test_minhas_atividades_em_escala.py` exige que o membro pague o
mesmo com uma e com onze comissões; uma consulta por Etapa quebraria isso.

### T-010 — "Avaliam" e a coerência na gestão, em leituras fixas

**Decisão.** `programacao.coerencia(edital, etapa_id)` devolve, numa passada: quem avalia cada
inscrição com horário (nomes pelo `rotulo_ou_nome` da comissão), quantas têm menos avaliadores do que
a Etapa prevê (`avaliacoes_previstas`), e os conflitos de quem atua na Etapa. A agenda publicada, o
cartão "Agenda" da Distribuição e "Quem está alocado" leem dela. A página pública e o PDF do ato têm
templates e leitores próprios (`portal/agenda_da_etapa.html`, `agendamento/infrastructure/documento.py`)
e não a chamam; o teste da SC-2846 varre os três canais com nomes de avaliador semeados.

### T-011 — O filtro de sessão não pagina a sessão

**Decisão.** A lista "Inscrições, uma a uma" ganha os parâmetros `dia` e `banca`. Com os dois, a
lista vem em ordem de horário e sem paginação até 200 linhas (uma sessão de banca tem dezenas), para
"selecionar todas desta página" alcançar a sessão inteira (UX-970). Sem eles, a lista é a de hoje.

### T-012 — A conferência da agenda mostra o conflito como aviso

**Decisão.** `conferir.conferencia(...)` ganha a lista de conflitos que a agenda conferida criaria
com as Atribuições que existem (fonte `MONTAGEM`), na seção de avisos, e não na de impedimentos
(FR-8208). Não entra na assinatura da conferência: a publicação não depende dela.

### T-013 — Os requisitos anteriores são revistos nos PRs que os tornam verdade

**Decisão.** Cada revisão é escrita na spec dona, datada, com a redação anterior preservada em
citação, como a FR-084 da `010` faz desde a `019` — e vigora com a implementação:

| Requisito | Onde | Incremento | O que entra |
|---|---|---|---|
| FR-085 | `specs/012-mesa-de-avaliacao/spec.md` | 1 | o conflito de horário como regra sobre a linha, ao lado do impedimento e do teto |
| FR-107 | idem | 1 | o rodízio percorre a agenda e trata o conflito como inelegibilidade; o resto da regra, intacto |
| FR-7229 | `specs/167-agendamento-da-etapa/spec.md` | 1 | "e ao avaliador autenticado e atribuído àquela entrevista, na Mesa" |
| FR-7240 | idem | 1 | a remarcação e a inclusão dizem quem avalia e quem ficará em conflito |
| FR-084 | `specs/010-area-do-candidato/spec.md` | 2 | a oitava situação (texto em *Requisitos de outras features afetados* da spec) |

**Por quê no PR, e não agora.** A `156` e a `167` revisaram a FR-084 na spec "com vigência na
implementação"; escrever agora a revisão das outras quatro deixaria a norma dizendo o que o código
ainda não faz, por um intervalo indeterminado. A spec da `179` já registra o que vai mudar e por quê.

---

## Incremento 2

### T-014 — O aviso ao avaliador é uma origem nova dos avisos da `066`, e o destinatário passa a ser inscrição ou membro

**Decisão.** Em `avisos`:

1. **Origem `PROGRAMACAO`** em `nomes.ORIGENS`, com `ORIGEM_POR_EXTENSO` "programação de
   entrevistas". No `Aviso`: `natureza=""`, `referencia_da_publicacao=""`, `marco_id` nulo,
   `etapa_id` obrigatório, `perfil_id` nulo — a mesma forma do `PASSO` da `171`. As três constraints
   da origem (`ck_aviso_ato_da_origem`, `ck_aviso_marco_da_origem`, `ck_aviso_etapa_da_origem`)
   ganham o ramo dela.
2. **`DestinatarioDoAviso.inscricao` passa a anulável**, e nasce `DestinatarioDoAviso.membro`
   (`MembroComissao`, anulável, `PROTECT`), com `ck_destinatario_inscricao_ou_membro`: exatamente um
   dos dois. `uq_destinatario_do_aviso` (aviso, inscrição) continua; nasce `uq_destinatario_membro`
   (aviso, membro).
3. **`DestinatarioDoAviso.resumo_da_programacao`** (`CharField(64)`, vazio por padrão): o resumo do
   estado avisado (FR-8224); `ck_destinatario_resumo_so_do_membro`: preenchido se e só se há membro.
4. **Um aviso por avaliador por gesto**, como a agenda e a pendência fazem por pessoa: o corpo é final
   e leva o nome do avaliador e os números dele; não há `{nome_do_candidato}` no texto.

Uma migration, `avisos/0005_origem_programacao`. **Nenhuma tabela nova**: o `M` da preparação
continua 69. As tabelas são append-only; acrescentar coluna anulável ou com padrão constante não
reescreve linha e não toca o gatilho, que é de `UPDATE` e `DELETE`. O guardião da contagem de
migrations por app sobe um em `avisos`.

**Por quê.** É o que a `D-010` pede: a fila, o limite por minuto — que é global, e um segundo
remetente o contornaria —, a tentativa gravada antes do envio, a retentativa, o reenvio de falhas e a
moldura já existem. O que é do candidato (elegibilidade do universo, convocação, `{nome_do_candidato}`)
continua só no ramo da inscrição.

**Descartado.** (a) Um remetente próprio, na requisição, como a convocação da `019`: duplicaria
retentativa e reenvio, e furaria o limite por minuto. (b) Uma tabela nova de destinatário de
avaliador: a mesma fila em duas tabelas, e o despacho com dois `_selecionar`.

### T-015 — O despacho passa a admitir destinatário sem inscrição, em três pontos

**Decisão.** Em `avisos/application/despacho.py`:

1. `_selecionar`: `select_related("aviso", "inscricao", "membro")` (as duas são `LEFT JOIN` depois de
   anuláveis), e a ordenação `inscricao__protocolo` passa a `F(...).asc(nulls_last=True)`;
2. `_mensagem`: `nome_do_candidato=destinatario.inscricao.nome if destinatario.inscricao_id else ""`;
3. `_auditar_o_envio`: hoje é só da pendência; não muda.

Fora do despacho, todo leitor que segue `destinatario.inscricao` em `avisos/application/` (doze
ocorrências, varridas no plano) é conferido: ou só roda para as origens de candidato — e ganha o
filtro `inscricao__isnull=False` —, ou passa a tratar o nulo. Um teste de guarda lista os leitores
e exige que cada um declare o que faz com a origem nova, no molde do
`test_leitores_da_consequencia.py` da `164`.

A constante `REVISAO_DA_FR_084_PELA_179` entra no despacho, e o par "o aviso de programação ao
avaliador (179)" em `tests/test_situacoes_de_mensagem.py`.

### T-016 — O endereço é o da pessoa institucional, congelado no gesto

**Decisão.** No gesto, para cada avaliador: `User` com `username == identity_subject` — sem exigir
o prefixo `pessoa-`, para que a conta de treinamento (T-020) resolva do mesmo jeito que a
institucional; e-mail
`User.email`; suspensa se `seguranca.application.suspensao.suspensas([...])` a inclui. O endereço é
congelado em `DestinatarioDoAviso.endereco`, como a `066` congela o do candidato. Sem pessoa, sem
e-mail ou suspensa: **nenhum aviso é criado** para ela, e a seção mostra o motivo, lido na hora
(FR-8226). Três consultas para a Etapa inteira, nenhuma por pessoa.

### T-017 — "Mudou depois do aviso" é comparação de resumo, e o último aviso é o de referência

**Decisão.** `resumo(programacao) = sha256` dos bytes canônicos da lista ordenada
`[(inscricao_id, inicio ISO, fim ISO, banca_id)]` dos vigentes publicados da pessoa naquela Etapa. O
**avisado** é o `resumo_da_programacao` do destinatário mais recente daquela pessoa, Etapa e origem
`PROGRAMACAO`. Estados (FR-8228), na ordem em que se decidem: suspenso; sem e-mail; com conflito
futuro; nunca avisado; mudou (resumo diferente); e, quando igual, o estado de entrega do último
aviso, lido pelo `estado_.estado_do_destinatario` da `066` (na fila, avisado, não entregue).

O gesto cria aviso para quem está em "nunca avisado" ou "mudou" — e para nenhum outro. Repetir sem
mudança não cria nada (FR-8225). O reenvio de quem "não foi entregue" é o `REENVIO_DE_FALHAS` da
`066`, que reaproveita o texto e o resumo do anterior.

### T-018 — O texto é fixo, do domínio, sem modelo editável

**Decisão.** `avaliacoes/domain/mensagem_da_programacao.py`, função pura `(avaliador, edital, etapa,
contagem, primeiro_dia, ultimo_dia, bancas, link, mudou_em) → (assunto, corpo)`, com o rodapé comum da
`066` (`RODAPE`). A conferência do gesto mostra o texto exato da primeira pessoa (FR-8222), da mesma
função. Sem `ModeloDeAviso`: como o aviso de agenda da `167`, o texto é do sistema, e não da unidade.

### T-019 — O gesto passa pela trava do Processo, e a confirmação confere o alcance

**Decisão.** `avisar_os_avaliadores(actor, edital, etapa_id, assinatura, idempotency_key)`, dentro de
`comando_de_comissao` (permissão de gerir a comissão, FR-8230). A tela de confirmação mostra o alcance
e manda a assinatura dele (os pares pessoa × resumo); o comando recalcula sob a trava e recusa com
`alcance_mudou` se diferir. Recusa também com a habilitação desligada (`recusar_se_desabilitado`, da
`066`). A trilha registra o gesto com a contagem e os identificadores dos avaliadores, sem e-mail
(FR-8232).

### T-020 — A demonstração do Incremento 2 tem avaliadores com conta e e-mail

**Decisão.** O cenário de treinamento C20 (`treinamento/catalogo.py`, `treinamento/construcao.py`)
passa a incluir a comissão da Entrevista: membros `treino.avaliacao.N` alocados à Etapa, cada um com
uma conta (`User`, senha inutilizável, `email=avaliacao.N@<DOMINIO>`), criada como a da Formalização
do C16 e do C17 (`_pessoa_da_formalizacao`): idempotente, resistente a duas cargas simultâneas. Os
membros entram pela página de acesso da demonstração, pelo campo livre, como a Formalização.

**Por quê.** Sem isso, todo membro da demonstração aparece como "sem e-mail", e o Incremento 2 só se
provaria na suíte — o que o Princípio VI não aceita como entrega. Não é exceção nova à regra "o
gerador não concede papel": a conta não tem papel; o que ela faz vem da comissão, como qualquer
membro. Os atores `treino.*` continuam fora das sugestões da página de acesso.

**Descartado.** Pedir à equipe que crie as pessoas pelo comando de implantação: é shell, e o
Princípio VI o exclui.
