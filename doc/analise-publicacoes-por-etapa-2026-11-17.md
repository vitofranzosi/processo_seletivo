# Publicações por etapa: o que o GPS publica, e onde a premissa de 17/11 não se cumpre

**Tarefa T15 do checklist de validação do TMD** (itens `5.09` e `9.01`). Análise, e não
implementação: nada aqui é escopo de spec. As lacunas viram registro, com opções; a escolha é da
equipe (Constituição; `CLAUDE.md`, *Governança é do usuário*).

A continuação, com o desenho da solução mínima (sem implementação), está em
[proposta-cobertura-de-publicacoes-2026-11-17.md](proposta-cobertura-de-publicacoes-2026-11-17.md).

Leitura do código da `main` em `31d93c47` (17/11/2026). Os caminhos são relativos a
`backend/processo_seletivo/`. Nada foi executado: as afirmações sobre comportamento vêm do código e
das docstrings, e os itens marcados **(a conferir na homologação)** pedem prova na 1ª execução
(T06).

## 1. A premissa e a resposta curta

A reunião de 17/11 disse, na fala sobre as etapas de avaliação, que o trabalho interno da comissão
"necessariamente vai gerar um resultado público", sem exceção. A sequência citada para cada tipo de
etapa é: trabalho, publicação do resultado, período de recurso, publicação da análise do recurso. A
convocação para entrevista ou prova também se publica. O e-mail seria um reforço, ligado por etapa
no Edital, só quando o candidato precisa agir.

**O GPS não segue essa premissa.** O que ele publica não é a etapa: é o **marco classificatório**,
isto é, a ordem de um Perfil numa lista. Uma etapa só chega à área pública se:

- um marco a lê, e o resultado desse marco é publicado; ou
- ela é a análise das inscrições (spec 148).

Hoje há sete atos públicos, listados na seção 2, e nenhum deles é "o resultado da etapa X".

**Correção da nota do item `5.09`.** A nota dizia "por marco do cronograma". O marco que publica é o
`MarcoClassificatorio` do Perfil (`editais/models/perfis.py`), e não um Evento do Cronograma. O
Cronograma não libera nem exige publicação de resultado:

- o prazo de recurso conta a partir da publicação, em dias corridos, e não de uma data digitada no
  Cronograma (`recursos/domain/janela.py`, docstring: "a âncora é o ato");
- o único uso do Cronograma numa publicação é a escolha do período de recurso do resultado
  preliminar das inscrições (`divulgacao/application/inscricoes.py`, `_prazo`).

## 2. Os sete atos públicos que existem

| # | Ato | Modelo e comando | Documento | Na página pública da seleção | O que **não** vai a público |
|---|---|---|---|---|---|
| A | Edital e Retificação | `publicacoes.Publicacao`; `publicacoes/application/publish_edital.py`, `retificacoes.py` | PDF/A | "Atos" (`portal/views.py:selecao`, `atos`) | — |
| B | Relação de inscrições: recebidas, resultado preliminar da análise, homologação (148) | `divulgacao.PublicacaoDasInscricoes`; `divulgacao/application/inscricoes.py:publicar_inscricoes` | PDF/A, na própria linha | `inscricoes_publicadas`; `portal:publicacao-das-inscricoes` | CPF, motivo e identificador interno; o indeferido só entra na contagem, sem nome (`divulgacao/domain/inscricoes.py`, D-010) |
| C | Relação de habilitados do sorteio, e o sorteio verificável (021) | `sorteios.RelacaoDeHabilitados`, `Sorteio`; `sorteios/application/relacao.py:publicar_relacao`, `sorteio.py` | **Sem PDF**: página, manifesto JSON e verificação | `sorteios`; `portal:relacao-de-habilitados`, `verificar-sorteio`, `manifesto-do-sorteio` | — |
| D | Resultado de um marco, preliminar ou definitivo, por lista (017) | `divulgacao.PublicacaoResultado` sobre `classificacao.AtoDeOrdenacao`; `divulgacao/application/publicar.py:publicar_resultado` | PDF/A (`DocumentoDoResultado`) | `resultados_divulgados`, com o histórico recolhido | Quem ficou sem posição (eliminado, retirado da reserva) não aparece. A situação individual vai para `SituacaoDivulgada`, que só o titular lê (`divulgacao/domain/conteudo.py`) |
| E | Agenda de uma Etapa com comparecimento (167) | `agendamento.AtoDaAgenda`, `HorarioPublicado`; `agendamento/application/publicar.py:publicar` | PDF/A (`DocumentoDoAtoDaAgenda`) | `agendas_publicadas`; `portal:agenda-da-etapa` | O motivo da remarcação (FR-7246) |
| F | Publicação de convocados (149) | `convocacao.PublicacaoDeConvocados`; `convocacao/application/publicar.py:publicar_na_transacao`, `publicar_do_gesto` | PDF/A | `convocacoes_publicadas`; `portal:convocados` | Desfecho da convocação: aceite, indeferimento, não atendimento, reclassificação |
| G | Encerramento e cancelamento do Edital ou do Processo | `processos.AtoAdministrativo`; `processos/application/finalizacao.py` | **Nenhum** | Só uma frase de estado com a data ("Edital encerrado em …", `portal/templates/portal/_periodo.html`; `processos/application/selectors.py:desfechos`) | Motivo e autor |

O comprovante de inscrição também é PDF/A, mas é do candidato, e não público. Os relatórios do Edital
e o consolidado são da gestão (`tests/pdfa/exemplares.py` lista os nove tipos).

**Nenhum dos sete se publica sozinho.** Cada um é um gesto de quem tem a permissão (por exemplo
`resultado:publicar`), com prévia assinada e autoridade signatária. O único efeito automático de um
ato é o aviso da agenda (seção 5).

## 3. Etapa por etapa (seções 4 a 10 do checklist)

Sobre a coluna **TMD**: o sorteio se aplica. Reserva e PPI estão como "Confirmar" na planilha e
dependem da minuta (T04). Títulos e didática não se aplicam.

| Item | Etapa | Trabalho da comissão | Publicação gerada | O que a publica ou libera | Obrigatória? | Aviso por e-mail | Observação / lacuna | TMD |
|---|---|---|---|---|---|---|---|---|
| `4.04`–`4.05` | Encerramento das inscrições | Conferir as inscrições enviadas | **Sim, B: relação de recebidas**, por Perfil e por lista de concorrência (ampla com todos; cada reservada com quem a declarou) | Gesto "Publicar as inscrições". Recusado enquanto o período corre (`CONSEQUENCIA`, `inscricoes.py`) | **Opcional**: nada a jusante exige a relação | Nenhum: não há origem de aviso para B | Atende "por modalidade" como lista. Não há CPF | Sim |
| `4.03` | Congelamento para o sorteio | Congelar quem participa | **Sim, C: relação de habilitados**, numerada por protocolo, com o método citado | `publicar_relacao`: publicar é congelar, num ato só | **Obrigatória para sortear**: o sorteio só lê relação congelada (`sorteio.py`) | Nenhum | Sem PDF; a página e o manifesto são o registro | Sim |
| `5.01` | Sorteio | Constituir o sorteio sobre a ocorrência da Loteria Federal | Página "verificar sorteio" e manifesto (C). A **ordem** é um `AtoDeOrdenacao` de origem `SORTEIO`, e ainda não é pública | `sorteios/application/sorteio.py` | — | Nenhum | — | Sim |
| `5.02`, `5.10` | Resultado do sorteio (classificação) | Publicar a ordem por lista | **Sim, D**, preliminar e depois definitivo, um por marco e lista | `publicar_resultado`. A definitiva é recusada com recurso pendente ou prazo aberto (`divulgacao/domain/publicabilidade.py`) | **Não exigida pelo sistema**: a apuração lê a ordem, e não a publicação (`interface/andamento.py:situacao_da_apuracao`). O andamento só a mostra como pendente (`situacao_do_resultado`) | RESULTADO, confirmado à parte com prévia (`avisos/application/confirmar.py:confirmar_aviso_do_resultado`) | Lacuna **L4** | Sim |
| `5.05` | Análise documental de reserva (antes da classificação) | Deferir ou indeferir quem declarou a reserva. É Etapa decisória **restrita** às Modalidades reservadas (163) | **Não** há ato próprio. O efeito "retira da reserva" ou "elimina" (164) muda a ordem do marco seguinte, que, quando publicada, já sai sem a pessoa na lista reservada | Indireto: a publicação D do marco **que lê** a Etapa | — | PASSO, se a Etapa pede algo do candidato (171); PENDÊNCIA, se a análise é na convocação | Lacunas **L1** e **L2**. B não serve: só publica Etapa decisória, eliminatória e **não restrita** (`divulgacao/domain/inscricoes.py:etapas_de_analise`) | Confirmar |
| `5.05` (variante) | Análise documental **na convocação** (115, 117), que é o caminho dos Editais de sorteio | Conferir documento por documento | **Não**. A conferência e o desfecho são individuais | — | — | PENDÊNCIA (`avisos/application/pendencias.py:avisar_pendencias`) | Lacuna **L5** | Provável |
| `5.06` | Heteroidentificação PPI | Convocar, avaliar (presencial, remota ou por vídeo, 166), deliberar (165) | Convocação: **sim, E (agenda)**, se a forma é com comparecimento. Resultado: **não** há ato próprio | Agenda: `agendamento/application/publicar.py`. Resultado: indireto, como na reserva | Agenda: opcional. A Etapa pode correr sem agenda | AGENDA, **automático** ao publicar. PASSO, para enviar o vídeo | Lacunas **L1**, **L2** e **L3** | Confirmar |
| `5.04` | Prova de títulos | Pontuar pelo barema (146) | Só como **parcela de um marco** (D), ou seja, a ordem e a pontuação combinada. Não há "resultado preliminar de títulos" separado da ordem | `publicar_resultado` do marco que enumera a Etapa | Opcional, como em D | RESULTADO | Lacuna **L1** (a Etapa fora de marco não tem saída) | Não |
| `5.07` | Prova didática ou entrevista | Agendar, avaliar, pontuar | Agenda: **sim, E**. Resultado: só via marco (D) | E + D | Opcionais | AGENDA (automático) + RESULTADO | Com duas Etapas no mesmo marco, sai uma ordem só, e não "resultado de cada prova" | Não |
| `5.09` | Toda etapa de avaliação | — | **Não, por construção** | — | — | — | A validação do Edital **avisa** e não impede a Etapa de que nada depende (`editais/domain/validation.py:_etapa_sem_resultado`, `stage_without_result`). O andamento a chama "Sem efeito no GPS" (`interface/andamento.py`, `SEM_EFEITO_NO_GPS`) | — |
| `5.11` | Área pública | — | Nas sete publicações, a fronteira é **de construção**: o conteúdo público é montado sem CPF, contato, motivo ou documento | `divulgacao/domain/conteudo.py`, `divulgacao/domain/inscricoes.py`, `convocacao/domain/publicacao.py` | — | — | Nome e protocolo são públicos em B, C, D, E e F (a conferir na homologação) | Sim |
| `6.01` | Abertura do recurso | Nenhum gesto: o prazo nasce da publicação | Embutido no ato: o prazo do marco conta da 1ª publicação do ato (`recursos/domain/janela.py`). O do preliminar das inscrições fica gravado em B (`recurso_ate`) | D ou B | — | Nenhum aviso de "abriu o prazo" além do aviso de resultado | O portal mostra o prazo ao lado de cada resultado (`portal/leitura.py:prazos_de_recurso`) | Confirmar |
| `6.04`–`6.06` | Julgamento dos recursos | Decidir; na correção, gerar `ResultadoEtapa` sucessor | **Não** há "resultado dos recursos". A decisão chega a público só quando o marco é republicado com o ato sucessor, e o documento cita "em razão do julgamento do recurso REC-…" (`divulgacao/infrastructure/documento.py`) | `recursos/application/julgar.py`; depois, `emitir_ordem` + `publicar_resultado` | — | Nenhum: não há origem de aviso para decisão de recurso | Lacuna **L3**. O recorrente lê a decisão no portal privado (`portal/views.py:recurso`) | Confirmar |
| `7.01`–`7.04`, `7.11`–`7.12` | Convocação, inclusive de suplente | Apurar, convocar | **Sim, F**, quando o Perfil comunica por publicação no GPS (efeito *convoca*). Fora disso, F pode ser só informativa (*divulga*), ou não existir (veículo "Fora do GPS") | `publicar_na_transacao` (convoca e publica juntos) ou `publicar_do_gesto` | **Opcional**. Convocar **não exige** resultado publicado (nada em `convocacao/application/convocar.py` o lê) | CHAMADA, confirmado à parte (`confirmar_aviso_da_chamada`) | Lacuna **L4** | Sim |
| `7.09`–`7.10` | Análise dos documentos e desfecho | Conferir; registrar desfecho (sete espécies, `DesfechoDaConvocacao`) | **Não** | — | — | PENDÊNCIA | Lacuna **L5**: eliminação ou reclassificação de quem não entrega não vai a público | Sim |
| `8.01`–`8.11` | Formalização | Definir, designar, exportar | **Não**, e é o esperado | — | — | PASSO (171), se configurado | — | Sim |
| (155) | Vaga não preenchida, apuração da ocupação | Destinar a vaga que sobra | **Não**: ato interno (`ocupacao/models.py`, `VagaNaoPreenchida`) | Exige resultado **definitivo** publicado (`ocupacao/domain/destinacao.py:impedimentos`) | — | Nenhum | É o único lugar em que a publicação definitiva é **pré-requisito** de outro ato | Múltiplas chamadas |
| `10.01`, `10.06` | Encerramento | Encerrar o Edital ou o Processo | **G**: frase de estado, sem documento | `processos/application/finalizacao.py` | — | Nenhum | Lacuna **L6** | Sim |

## 4. As sequências da reunião, confrontadas

| Sequência dita em 17/11 | Trabalho | Publica o resultado? | Abre recurso? | Publica a análise do recurso? |
|---|---|---|---|---|
| Análise documental de cotas, logo depois da inscrição | Etapa decisória restrita | **Não** (L1, L2) | Só se o titular **vê** o resultado; senão o recurso é recusado com 404 (`recursos/application/interpor.py:_recusar_se_invisivel`) | **Não** (L3) |
| Análise documental geral das inscrições (não restrita) | Etapa decisória eliminatória | **Sim**, B preliminar e homologação | **Sim**, prazo gravado em B | **Não** como ato; a homologação sai depois do julgamento (`_disputa_em_aberto`) |
| Convocação para a entrevista PPI | Agenda da Etapa | **Sim**, E | — | — |
| Resultado da PPI | Etapa restrita colegiada | **Não** (L1, L2) | Ver a primeira linha | **Não** |
| Convocação para a prova didática | Agenda | **Sim**, E | — | — |
| Resultado da prova didática, recurso e resultado final | Etapa pontuada num marco | **Sim**, como a ordem do marco (D), preliminar e definitiva | **Sim**, prazo do marco | **Não** como ato; a definitiva republicada cita a decisão |
| Sorteio (TMD) | Relação, sorteio, ordem | **Sim**: C, depois D | **Sim**, se o marco declara janela | **Não** como ato |

## 5. O e-mail, etapa por etapa

O mecanismo não é "uma caixa por etapa no Edital", como a reunião imaginou. Ele é um **gesto por
publicação**, com uma chave única por ambiente (`AVISOS_AOS_CANDIDATOS`). Há cinco origens
(`avisos/domain/nomes.py:ORIGENS`):

| Origem | Liga-se a | Como sai |
|---|---|---|
| RESULTADO | publicação D de um marco (`marco_id` obrigatório, `ck_aviso_marco_da_origem`) | A comissão confirma à parte, com prévia |
| CHAMADA | convocação | Confirmada à parte |
| PENDÊNCIA | conferência de documentos | Disparada na conferência |
| AGENDA | publicação, remarcação ou inclusão na agenda (E) | **Automática**, sem opção (`agendamento/application/avisar.py`) |
| PASSO | Etapa restrita que pede algo do candidato (171) | Confirmada à parte |

Sem origem de aviso nenhuma: a relação de inscrições (B), a relação de habilitados e o sorteio (C),
a decisão de recurso, a Retificação, a publicação de convocados (F) em si e o encerramento (G).

Pela regra que a equipe propôs (o e-mail vai quando o candidato precisa agir), o desenho atual
**quase** a atende por construção:

- CHAMADA, PENDÊNCIA, PASSO e AGENDA pedem ação;
- RESULTADO é opcional, e cabe à comissão.

A exceção é a agenda: ela avisa sempre, o que está de acordo com a regra, mas sem que a comissão
possa escolher. Isso é a T16 e a T17.

## 6. As lacunas, com risco e opções

Nenhuma opção abaixo é recomendação de escopo. A decisão é da equipe.

### L1. Etapa de avaliação sem saída pública

Uma Etapa que nenhum marco lê e que não é a análise das inscrições é publicada pelo Edital, avaliada
e consolidada, mas **nunca gera ato público**. A validação só avisa (`stage_without_result`), e o
andamento a rotula "Sem efeito no GPS". O próprio código registra a pendência:
`resultados/domain/efeito.py:etapas_lidas_pelo_marco` deixa a Etapa não restrita fora de marco "para
a spec da R-8".

- **Risco:** a premissa "sem exceção" falha sem nada que avise o operador na hora de publicar.
- **Opções:**
  - (a) aceitar, e no roteiro do operador modelar toda Etapa dentro de um marco;
  - (b) a validação passar a **impedir** a publicação do Edital com Etapa sem saída pública;
  - (c) spec da R-8: um ato "resultado da Etapa", no molde de B.

### L2. Etapa restrita (reserva, PPI) num Edital de sorteio: sem publicação e sem acesso do titular

O titular só vê o próprio resultado de Etapa por dois caminhos (`resultados/application/selectors.py:resultados_visiveis`):

1. a publicação D de um marco que a lê;
2. a publicação B das inscrições.

`etapas_lidas_pelo_marco` inclui a Etapa restrita só quando ela vem **antes da última Etapa que o
marco enumera**. Um marco de sorteio não enumera Etapa (`stages` vazio), e então a função não
devolve nenhuma. B, por sua vez, recusa Etapa restrita.

Lido o código, no Edital de sorteio com reserva ou PPI a Etapa restrita **não tem publicação nenhuma**:

- o titular não vê o próprio resultado;
- por isso o recurso é recusado com 404 (`_recusar_se_invisivel`).

**(a conferir na homologação: é o caso do TMD se reserva ou PPI forem confirmados na T04.)**

- **Risco:** é o mais alto para o TMD. Um ato que afeta direito, retirar da reserva ou eliminar, fica
  sem publicidade e sem caminho de recurso dentro do GPS.
- **Opções:**
  - (a) a análise de reserva e PPI ficar **na convocação** (115/117), depois do sorteio, que é o
    caminho que o código prevê para Editais de sorteio ("quem habilita é a análise documental, que
    vem depois", `sorteios/application/sorteio.py`), e o desfecho ser tratado como em L5;
  - (b) publicar fora do GPS, com o roteiro dizendo onde;
  - (c) spec: estender `etapas_lidas_pelo_marco` ao marco de sorteio, ou fazer o ato de L1(c)
    aceitar Etapa restrita.

### L3. Julgamento de recurso não é ato publicado

A sequência da reunião prevê "publica a análise do recurso". No GPS:

- a decisão é individual, e o recorrente a lê no portal;
- ela só aparece em público quando o ato sucessor do marco é publicado de novo, e o documento cita o
  recurso;
- o recurso que **nega** provimento não muda a ordem, então não gera republicação e nunca aparece em
  público;
- não há aviso por e-mail da decisão.

- **Risco:** se o Edital do TMD prevê publicar o "resultado dos recursos", hoje isso é feito fora do
  GPS.
- **Opções:**
  - (a) aceitar: a definitiva publicada depois do julgamento faz as vezes do resultado dos recursos,
    e o roteiro diz isso;
  - (b) publicação fora do GPS;
  - (c) spec de um ato "decisões de recurso", com nome e protocolo, sem fundamentação pessoal.

### L4. Publicar o resultado é passo esperado, e não pré-requisito

A apuração e a convocação leem a **ordem**, e não a publicação. Dá para convocar a partir de uma
ordem nunca publicada, ou publicada só como preliminar com o prazo de recurso ainda correndo. Isso
é exceção à regra que vale para a vaga não preenchida (155), que exige o definitivo. O andamento
mostra "Publicar o resultado" como pendente, mas não bloqueia.

- **Risco:** a convocação sai antes do resultado definitivo, e o recurso posterior muda a ordem de
  quem já foi chamado.
- **Opções:**
  - (a) regra do roteiro: só convocar depois do definitivo publicado;
  - (b) a apuração ou a convocação passarem a exigir resultado definitivo, como a `155` já exige;
  - (c) só um aviso na prévia da convocação.

### L5. Desfecho da convocação não é publicado

A eliminação por não entrega, o indeferimento documental e a reclassificação ficam no registro
individual. A publicação de convocados (F) não leva desfecho, e recusa incluir quem já tem desfecho.

- **Risco:** se o Edital manda publicar "relação de matriculados" ou "eliminados na habilitação",
  isso é feito fora do GPS.
- **Opções:**
  - (a) aceitar, e publicar fora;
  - (b) spec de um ato de "resultado da habilitação ou matrícula".

### L6. Encerramento sem documento

O encerramento aparece como frase de estado, com a data, sem ato publicado nem documento.

- **Risco:** baixo, se o Edital não pede ato de encerramento publicado.
- **Opções:**
  - (a) aceitar;
  - (b) gerar documento no molde dos outros sete.

### Observação sobre o e-mail (T16, T17)

O pedido da reunião ("um checkbox no Edital") não existe. Hoje a escolha é feita gesto a gesto,
salvo a agenda, que avisa sempre. Isso é a T17 e fica fora desta análise.

## 7. Texto para a planilha

**Coluna Q do `5.09`:**

> Agente (17/11): Corrigindo a nota anterior: a publicação do resultado é por marco classificatório
> do Perfil (a ordem de uma lista), e não por marco do cronograma, nem por etapa. A etapa só vira
> público se um marco a lê ou se é a análise das inscrições. Etapa fora de marco, e etapa de reserva
> ou PPI num Edital de sorteio, não geram publicação; no sorteio, o candidato nem vê o próprio
> resultado. Julgamento de recurso também não é ato publicado. Ver
> doc/analise-publicacoes-por-etapa-2026-11-17.md (lacunas L1 a L6).

**Coluna Q do `9.01`:**

> Agente (17/11): Mapa feito (T15). O sistema tem sete publicações: Edital/Retificação; relação de
> inscrições (recebidas, preliminar, homologação); relação do sorteio; resultado por marco
> (preliminar e definitivo); agenda da etapa; convocados; encerramento (só uma frase, sem
> documento). Sem publicação: resultado de etapa restrita (reserva e PPI), decisão de recurso e
> desfecho da convocação. CPF, contato e documentos nunca vão a público. Detalhe e opções em
> doc/analise-publicacoes-por-etapa-2026-11-17.md.
