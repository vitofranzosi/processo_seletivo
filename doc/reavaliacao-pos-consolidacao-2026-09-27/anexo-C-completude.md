# Reavaliação C — completude ponta a ponta por natureza de Edital

Código: origin/main 79aeb847 (HEAD f77e8aa9 só difere em doc/). 048 em PR #197.
Método: leitura do código atual + Editais em ~/Downloads (pdftotext). Somente leitura.

## Relatório

### 1. O que os Editais pedem (pdftotext + grep; sem dados pessoais)

- **78/2026 e 59/2026 (Libras A1, FIC presencial)** e **77/2026 (FIC remanescentes)**: inscrição online com
  7 documentos (inclusive o *Requerimento de Matrícula – Anexo II* anexado já na inscrição, 5.4.g);
  sorteio eletrônico com lista de habilitados 2 dias antes (6.4); análise documental dos sorteados até
  o nº de vagas + até 30 suplentes por código (6.3, 6.10); recurso só do resultado preliminar (7.1);
  "Resultado Final e homologação das matrículas"; matrícula feita pela instituição "pelo Sistema
  Acadêmico" (8.1.a); **regularização** do indeferido por e-mail com 2 dias úteis (8.2–8.3);
  **desistência por inércia** (AVA 6 dias / faltar à 1ª semana); validade 6 meses prorrogável, suplente
  para turma nova (6.11). Sem cota. 78: cronograma abre inscrição (04/08) antes da publicação (05/08).
- **28/2026 (e 149/2024), pós EaD**: 7 polos × {AC, PPI 25%, PcD 5%}; reversão *dentro do polo* (4.3);
  concorrência concomitante e sorteio AC primeiro, depois reservas (8.7–8.9); **verificação da
  autodeclaração** por CLVA (videoconferência p/ pretos e pardos, análise documental p/ indígenas) com
  recurso à CPVA (6.x); indeferido na heteroidentificação sai da lista PPI e fica na AC (8.10); recurso
  só da heteroidentificação e do resultado preliminar documental (9.1); 15 suplentes por código; matrícula
  pelo Sistema Acadêmico; matrícula cancelada de quem não comparecer à verificação (10.1.d).
- **140/2025 (tutor presencial UAB)** e **173/2025 (designer educacional)**: cadastro de reserva puro
  ("convocados conforme interesse da Administração", "diante da necessidade institucional e da
  existência de bolsas" — 140 15.4); prova de títulos por ficha com "expectativa de pontuação" (173 5.h:
  "não sendo atribuída pontuação que exceda à informada"); modalidades AC/PPIQ/PcD/PTT (140) e
  AC/PPIQ/PcD (173); heteroidentificação por videoconferência (140: até 3 por código, 8.2); **ordem
  nominal de convocação** (140 10.5: 1ª AC, 2ª PcD, … 26ª PPIQ-Quilombolas …); reversão entre
  submodalidades PPIQ antes da AC (140 10.5.1); **mobilidade entre perfis** (140 §11); curso de formação
  exigido na convocação (140 §12); vinculação UAB/FAPES com termo de compromisso e bolsa (140 §13,
  173 §11); validade 2 anos (140 §14).
- **14/2026 (orientador de TFC)**: três grupos (1: Ifes do campus; 2: Ifes de outros campi; 3: externos),
  três listas; **Entrevista só para os 10 melhores do Grupo 1 por código** na prova de títulos, e só se
  faltar gente chamam-se Grupo 2 e 3 (4, 6.1, 6.6); quem não é convocado à entrevista "não será
  classificado"; nota final = média aritmética de títulos e entrevista (9.1); desempate idade → meses de
  docência EaD → curso Moodle (9.2); mobilidade entre perfis por grupo (§10); vinculação UAB; validade 2
  anos.
- **57/2026 (aperfeiçoamento unificado)**: 2 cursos × {AC, PPI, PcD}, 80 vagas cada; heteroidentificação
  CLVA/CPVA (§6); sem remanejamento entre cursos (4.5); requerimento de matrícula como documento (5.g).
- **76/2026 (técnico subsequente Secretaria Escolar)**: inscrição **pelo SIGAA** (4.1); 6 polos com "CR" em
  vez de número (2.1); sorteio; impugnação por qualquer cidadão (7.2); deriva do 52/2026.
- **69/2026 (Multimeios, chamada pública)**: CR sobre 6 vagas remanescentes; entrega **presencial** de
  documentos com procuração (Anexo II); **reclassificação** para o fim da lista de quem não comparece;
  impugnação; matrícula presencial.

### 2. A 048 (PR #197, aberto; `test` do CI em andamento na consulta) — o que muda

Lida por `git show origin/claude/retificacao-cobertura-auditoria-b7eabb:…` (subagente, conferido por
amostragem). Não mexe em `editais/domain/mutabilidade.py`: dá **porta de tela** ao que o contrato já
permitia nascer.
- Passa a acrescentar por Retificação: **Modalidade** num Perfil existente, inclusive cota
  (`interface/retificacao.py:610` na branch; validação em `publicacoes/application/retificacoes.py:228`);
  **janela recursal** quando não existia (nasce `admits=True`, dias corridos — `retificacao.py:496-501`);
  **regra de corte** quando não existia (recusada se a Etapa governada já tem Resultado —
  `retificacoes.py:298-330`); **reversão** sempre visível; **critério de desempate** acrescentável.
- Declara fechar **RC-37 e RC-38**; **não** fecha o RC-111 (o "O que mudou" público) e diz que o amplia;
  não trata o RC-121.
- Fora: Documento Exigido/Fato/Marco/Etapa novos por Retificação; regra normativa de Modalidade já
  publicada; inscrições já enviadas não mudam de Modalidade e o período não reabre (a Modalidade nova
  só serve a inscrições novas — FR-781, Edge Cases); convocação não é tratada; reversão retificada não
  torna a apuração obsoleta (achado A-2 da própria spec).
- **Consequência para a completude**: com a 048, um Edital publicado **sem janela recursal, sem corte ou
  sem uma cota** ganha conserto normativo; sem ela (a `main` de hoje), esses três casos não têm conserto
  pela tela (`interface/retificacao.py:1054`, `SECOES_QUE_ACRESCENTAM`, e os campos que só aparecem se o
  objeto existe). Mas o conserto é **só normativo e só para frente**: quem já se inscreveu na AC não
  migra para a cota nova, e o período não reabre.

### 3. Rupturas transversais — valem para TODA natureza (conferidas no código de 79aeb847)

Caminhos relativos a `backend/processo_seletivo/` salvo indicação.

**T1 · Não há como operar a gestão em produção (C7 / RC-92).** Pré-condição de qualquer natureza.
- A interface administrativa só identifica pelo seletor de demonstração: sem ele, `identificar`
  devolve 503 (`interface/views.py:597-600`); a sessão é o que o seletor gravou
  (`interface/identidade.py:107-124`, papéis escolhidos pelo próprio usuário).
- Produção recusa subir com o seletor ligado (`config/settings/production.py:87-91`) e exige uma
  classe de autenticação institucional que **não existe no repositório** (`production.py:199-219`;
  o único adaptador é o provisório `seguranca/api/authentication.py:7-23`, recusado por
  `MODULO_DE_DESENVOLVIMENTO`, `production.py:44`).
- Consequência: em produção nenhum Gestor, Elaborador, Homologador, Publicador, avaliador, julgador ou
  exportador consegue entrar. Fora de produção, qualquer pessoa declara qualquer identidade e papel. O
  que existe é "piloto assistido em ambiente de desenvolvimento".

**T2 · Não há caminho de produção (RC-124).** `config/wsgi.py:5` e `config/asgi.py:5` caem em
`config.settings.development` sem a variável; a única imagem é de desenvolvimento
(`Dockerfile:8-10`, "Não é imagem de produção", `runserver`, `DEBUG`); nenhum servidor WSGI de
produção em `backend/pyproject.toml`.

**T3 · Correio é o único fator do candidato.** O acesso ao portal é código por e-mail
(`identidade/application/mensagem.py:95-110`); produção recusa backend que não entrega
(`production.py:134-164`), mas nada prova entrega. Sem SMTP institucional o candidato não entra, e a
convocação por mensagem individual (`convocacao/application/comunicar.py:345`) não chega.

**T4 · Encerramento não é conclusão.** `ensure_edital_can_be_closed` só olha o status
(`processos/domain/finalizacao.py:55-60`); `ensure_processo_can_be_closed` idem (`:33-37`) — nenhum
confere recurso pendente, convocação sem desfecho, requerimento não enviado ou exportação feita.
Encerrar o **Processo** bloqueia todo comando de comissão — convocar, desfechar, apurar, consolidar,
sortear (`comissoes/application/__init__.py:76-91`, `ensure_processo_accepts_changes`) — mas **não**
fecha as inscrições dos Editais publicados (`inscricoes/domain/periodo.py:77-84`; RC-118). Encerrar o
**Edital** fecha inscrições e **não** bloqueia convocação. Não há prazo de validade do processo (grep
por validade/prorrogação: nada em `processos/`, `editais/`, `convocacao/`): a "validade de 6 meses /
2 anos" dos Editais só se cumpre mantendo o Processo ATIVO, e o encerramento corta a cauda. O
cancelamento do Edital grava `AtoAdministrativo` e trilha, e nenhuma Publicação
(`processos/application/finalizacao.py:40-70`; RC-120). Auditoria/trilha existe
(`interface/urls.py` `auditoria` de Edital e Processo).

**T5 · O sistema não publica fora de si.** Convocação "por publicação": o sistema exige que se
declare **onde** ela foi publicada, porque "o sistema não publica por conta própria"
(`convocacao/application/comunicar.py:175-188`). Os Editais publicam nos sítios do Ifes/Cefor; o
portal é outro endereço.

**T6 · Resultado de Etapa não é publicável como lista.** `017` D-002 ("A V1 publica apenas
`AtoDeOrdenacao`", `specs/017-publicacao-de-resultados/spec.md:110-115`) e `018` FR-017/FR-019
(`specs/018-recursos-e-superacao-de-resultados/spec.md:921-925`); homologação de resultado fora
(`017` D-003). O titular vê o seu Resultado **só** se um marco publicado enumerar aquela Etapa
(`resultados/application/selectors.py:168-…`, `resultados_visiveis`), e só então pode recorrer dele
(`recursos/application/interpor.py:302-318`, `_recusar_se_invisivel`, 404). Os Editais publicam
"Resultado Preliminar (após análise da documentação)" e "Resultado Final e homologação das
matrículas" como listas: não há ato no sistema para isso.

**T7 · Registro Acadêmico: arquivo, não integração.** A exportação é um `.xlsx` de 34 colunas,
devolvido na resposta e não guardado (`matriculas/infrastructure/planilha.py:46-63`); `COD_CURSO`,
`COD_TURNO` e `COD_POLO` saem **sempre vazias** — "Preencher no destino"
(`matriculas/domain/colunas.py:198-215`); a importação real nunca foi feita
(`specs/031-exportacao-de-matriculas/tasks.md:222`, T038 aberta; Q-1, Q-2, Q-3 da spec 031
abertas). A matrícula efetivada acontece no Sistema Acadêmico, fora. A capacidade existe só onde o
Edital declara requerimento — "confina a feature a processos de alunos"
(`matriculas/application/populacao.py:68-78`).

**T8 · Sorteio só por fonte pública externa.** Vocabulário de produção = `{"Loteria Federal"}`
(`sorteios/infrastructure/fontes/__init__.py:83-87 e :99-115`, `fontes_publicadas`). Os Editais do Cefor
descrevem *"software… Semente utilizada"* gerada no ato (78/2026 6.2): para rodar no sistema, o
Edital tem de ser redigido pela D-G3 (decisão institucional, `doc/reavaliacao-ux-2026-09-18.md:732-743`),
e o sorteio espera a extração da Caixa. O E2E contra a fonte real não roda em lugar nenhum (RC-74).

**T9 · Retificação.** Na `main`, Modalidade, janela recursal, corte e reversão **não nascem** pela
tela (`interface/retificacao.py:1108` `SECOES_QUE_ACRESCENTAM`; campos condicionados à existência em
`:817`, `:905`, `:912`; `retificar.html:159` "Modalidades de Concorrência ainda não são definidas por
aqui"). A 048 (PR #197) abre essas portas, só para frente. O "O que mudou" público cala o quadro por
Modalidade, o percentual da cota, a janela, o método do sorteio e o corte (`publicacoes/domain/
alteracoes.py:42-100` — `CAMPOS` sem `vacancyTable`, `normativeRule`, `appealWindow`, `drawMethod`,
`cutRule`; RC-111): a Retificação muda e o candidato não é avisado do que mais pesa.

**T10 · Composição de Edital grande.** Restaurar o rascunho local perde coleções aninhadas
(`interface/static/interface/rascunho.js:81-133`, inalterado desde 08/09; RC-08 `[VALIDAR]`) — risco
proporcional ao número de Perfis × Modalidades (28/2026: 7 polos × 3).

### 4. Por natureza — etapa a etapa (✔ no sistema · ◐ com contorno/fragilidade · ✘ fora do sistema)

As rupturas T1–T10 valem para todas e não são repetidas linha a linha.

#### N1 · Curso FIC por sorteio, com vagas remanescentes (78/2026, 59/2026, 77/2026; família 58/2026, 158/2024)

| Etapa | Estado | Evidência |
|---|---|---|
| criação, composição, reuso do Edital anterior | ✔ | turma = Perfil (59/78); `023` clona o 59 no 78 |
| requerimento de matrícula na inscrição | ✔ | momento `NA_INSCRICAO` (`requerimentos/domain/disponibilidade.py:86-124`), recusa a submissão sem ele (`requerimentos/application/exigencia.py:60-73`); oito campos do Anexo II não são coletados por decisão (`requerimentos/models.py:13-16`) |
| "Alistamento militar, sexo masculino >17" | ◐ | sai "(facultativo)" — decisão D2 de 25/09 (RC-91) |
| publicação | ✔ (T1) | fecho do PDF sem nome/portaria `[VALIDAR com o Cefor]` (RC-23) |
| inscrição, documentos | ✔ (T3) | portal com código por e-mail |
| relação de habilitados, sorteio | ◐ (T8) | executável só com Loteria Federal declarada; o texto do 78 (6.2) descreve outra coisa |
| corte "até o nº de vagas + 30 por código" | ✔ | alvo `FROM_VACANCY_TABLE` + excedente (`classificacao/domain/faixa.py:18-23`) |
| comissão, distribuição, análise documental, consolidação | ✔ | Mesa decisória |
| "Resultado preliminar (após análise da documentação)" público | ✘ (T6) | não há ato; o titular vê o seu **se** o marco publicado enumerar a Etapa documental — composição tácita `[VALIDAR por percurso]` |
| recurso do indeferimento documental | ◐ | só com a Etapa enumerada no marco publicado (`recursos/application/interpor.py:302-318`) |
| apuração, convocação, suplência, regularização (8.2–8.3), inércia (AVA) | ✔ | `convocar.py:134-154` (`PARA_REGULARIZAR`), `convocacao/domain/nomes.py:104-111` (atestados de fato externo); faixa seguinte pelo déficit (`ocupacao/application/causar_faixa.py:22-86`) |
| chamada de suplentes "publicada no sítio" (6.9) | ◐ (T5) | publicação fora + referência digitada |
| exportação, matrícula | ◐ (T7) | `.xlsx`, 3 colunas preenchidas à mão no destino, importação nunca validada |
| "homologação das matrículas" | ✘ (T6) | sem ato |
| validade 6 meses, suplente em turma nova (6.11) | ✘ | nenhum conceito de validade; turma nova = Edital novo, sem herança (P-3, P-6) |
| encerramento | ◐ (T4) | status sem conferência |

**Classificação: completo com dependências externas** — a cadeia interna fecha de ponta a ponta, mas
só fora de produção (T1, T2), e com a Caixa, o SMTP, o Sistema Acadêmico e duas listas publicadas fora.

#### N2 · Pós-graduação EaD multipolo com cotas, sorteio e verificação de autodeclaração (28/2026, 149/2024; 35/2026)

| Etapa | Estado | Evidência |
|---|---|---|
| 7 polos × {AC, PPI, PcD} | ✔ | polo = Perfil; quadro por Modalidade (025/027) |
| sorteio da AC e depois das reservas, concorrência concomitante (8.7–8.9) | ✔ | três atos raiz por marco; `ocupantes_da_ampla` (`ocupacao/domain/apuracao.py:100-120`) |
| reversão *dentro do polo* (4.3) | ✔ | cota → ampla do mesmo Perfil (`ocupacao/domain/reversao.py:18-38`), duas espécies |
| **verificação da autodeclaração (CLVA), recurso à CPVA** | ✘ | zero ocorrência de `heteroidentifica` no código de produção; a Etapa é do Edital inteiro e alcança todos os Perfis e Modalidades (`editais/models/etapas.py:11-20`; participação = toda inscrição submetida menos eliminadas/fora do corte, `resultados/application/prontidao.py:98-162`) — não há Etapa só de quem declarou PPI; órgão recursal distinto contraditado na V1 (RC-90) |
| efeito do indeferimento (sai da lista PPI, **fica na AC** — 8.10) | ✘ / ◐ | a Modalidade da inscrição só muda no rascunho (`inscricoes/application/rascunho.py:270,475`); como Etapa eliminatória, eliminaria da AC também. O único contorno é registrar desfecho `INDEFERIMENTO` na convocação da lista PPI, com o fundamento digitado — a verificação vira fato da convocação, e não Etapa com recurso |
| matrícula cancelada de quem não comparece à verificação (10.1.d) | ◐ | desfecho com fundamento |
| exportação com `COD_POLO` | ◐ (T7) | 7 polos preenchidos à mão no destino |
| demais etapas | como N1 | |

**Classificação: parcialmente suportado** — a oferta executa (sorteio por lista, concomitância,
reversão por polo, convocação); a verificação da autodeclaração, que o Edital põe **antes** do
resultado e com recurso próprio, é inteira fora, e o efeito dela só entra por contorno.

#### N3 · Cadastro de reserva de bolsistas/tutores UAB com prova de títulos, cotas por código, sem vaga imediata (140/2025, 173/2025)

| Etapa | Estado | Evidência |
|---|---|---|
| composição e publicação de Perfil só de reserva | ✔ publica | `reserveType`/`reserveLimit` saem no PDF (`publicacoes/infrastructure/pdf.py:1684-1686`) e no portal (`portal/views.py:188-199`); **nenhum** aviso de que a convocação não executa (DP-05 opção B não feita) |
| inscrição (1 código, último envio vale), documentos, autodeclarações | ✔ | |
| prova de títulos | ◐ | a nota é **um total** por Avaliação (`avaliacoes/models.py:109`), conferido só contra a máxima da Etapa (`avaliacoes/domain/pontuacao.py:67-80`); a ficha/barema fica fora; zero ocorrência de "barema" no código de produção (RC-64) |
| teto pela autopontuação (173 5.h, "não sendo atribuída pontuação que exceda") | ✘ | nada confronta a nota com a expectativa declarada (P-7) |
| desempate por idade | ✔ | `FatoDeclarado` DATA (`editais/models/perfis.py:209-211`) |
| heteroidentificação (140: até 3 por código) | ✘ | como N2 |
| classificação, resultado, recurso | ✔ | |
| **convocação da reserva** | ✘ | com `immediateVacancies = 0`: `efetivas = publicadas` (`ocupacao/domain/apuracao.py:265-267`), `titulares = []`, `faltando = 0`; `convocar` recusa `sem_deficit` a quem não é ocupante (`convocacao/application/convocar.py:249-297`); sem apuração, recusa `apuracao_ausente` (`:100-109`). Nenhum consumidor de `reserveType`/`reserveLimit` em `ocupacao/`, `convocacao/`, `classificacao/` (RC-58, confirmado pelo código) |
| ordem nominal de convocação (140 10.5: 1ª AC, 2ª PcD, … 26ª Quilombola) | ✘ | `call_rules` é JSON publicado e opaco (`editais/models/perfis.py:387`; `publicacoes/application/publish_edital.py:141`), sem consumidor na execução (RC-59) |
| reversão entre submodalidades PPIQ antes da AC (10.5.1) | ✘ | Modalidade plana; reversão tem um destino só (RC-55) |
| mobilidade entre perfis (140 §11) | ✘ | a fila é do recorte (Perfil × marco × lista); convocar fora dele = `fora_da_faixa` (`convocar.py:362-368`) |
| curso de formação exigido na convocação (140 §12) | ◐ | desfecho com fundamento |
| vinculação UAB/FAPES, termo, bolsa | ✘ (legítimo) | outro sistema; requerimento de matrícula não se aplica (`matriculas/application/populacao.py:68-78`) |
| validade 2 anos | ✘ (T4) | |

Contorno possível para a parte mais simples (reserva só de AC): **retificar as vagas imediatas a
cada chamada** — cada chamada vira ato normativo com elaboração, homologação e publicação, e o "O que
mudou" cala a mudança se ela for no quadro por Modalidade (T9). É o que a DP-05 descreve como "usar um
ato normativo para registrar um fato operacional".

**Classificação: impossível sem trabalho externo** — até o resultado final o sistema conduz (com
barema e teto fora); a convocação, que é a razão de ser do cadastro de reserva, não acontece.

#### N4 · Seleção de orientadores com títulos + entrevista e grupos de prioridade em cascata (14/2026; o 146/2025 — bolsista, títulos + entrevista, sem cascata — é da mesma família)

| Etapa | Estado | Evidência |
|---|---|---|
| Perfil por código de inscrição, 1 vaga cada | ✔ | |
| títulos (total) + entrevista como Etapa | ✔ / ◐ | Entrevista é Etapa pontuada comum; barema como em N3 |
| entrevista só para os 10 melhores **do Grupo 1** por código | ◐ | corte `FIXED 10` governando a Entrevista, por recorte (`resultados/application/prontidao.py:311-354`) — mas só se os grupos forem listas (Modalidades) do Perfil, o que exige quadro por Modalidade e declaração da ampla |
| Grupo 2 e 3 só se o Grupo 1 tiver menos de 10 (6.6) | ✘ | nenhuma prioridade entre listas (RC-59); recorte sem corte emitido fica **dormente** e deixa todos participarem da Etapa (`prontidao.py:326-354`, FR-214) — a regra do Edital só se imita emitindo cortes à mão, com quantidades calculadas fora |
| "não convocado à entrevista não é classificado" | ✔ | `continuation: NONE` (`classificacao/domain/faixa.py:31-37`) |
| nota = média de títulos e entrevista | ✔ | `MEDIA_PONDERADA` (`classificacao/domain/combinacao.py:29-31`) |
| desempate idade → meses de EaD → curso Moodle | ◐ | DATA e INTEIRO; o curso (sim/não) só como inteiro 0/1 (L-4) |
| convocação "diante da necessidade" | ✔ | há vaga publicada; fundamento obrigatório (`convocar.py:76-85`) |
| convocação em cascata entre grupos, mobilidade por grupo (§10) | ✘ | como N3 |
| vinculação UAB | ✘ (legítimo) | |

**Classificação: parcialmente suportado** — o núcleo títulos + entrevista + média + desempate
executa para um grupo; a regra que define o Edital (a cascata) não.

#### N5 · Edital unificado de cursos de aperfeiçoamento (57/2026)

Mesma forma de N2 com dois cursos no lugar de sete polos: 2 Perfis × {AC, PPI, PcD}, sorteio por
lista, 20 suplentes por código, "sem remanejamento entre cursos" (4.5) — que o sistema cumpre por
construção (reversão só dentro do Perfil, e ausência de declaração = não reverte,
`ocupacao/domain/reversao.py:10-12`), reversão "por não preenchimento total" (a segunda espécie).
Ruptura idêntica: verificação da autodeclaração CLVA/CPVA (§6) e recurso contra ela (9.1).

**Classificação: parcialmente suportado.**

#### N6 · Chamada pública técnico subsequente com cadastro de reserva (76/2026)

| Etapa | Estado | Evidência |
|---|---|---|
| **inscrição "somente pelo Sistema de Inscrições" do SIGAA** (4.1) | ✘ | nenhuma porta de entrada de inscrição originada fora: não há comando de carga (os únicos comandos são `seed_demo`, `carregar_ceps`, `situacao_dos_ceps`, `provisionar_papeis`), e a decisão sem carga retroativa (`doc/decisao-sem-carga-retroativa.md`) fecha o caminho (P-8; RC-110 registra que falta decidir se o 76 sai do alvo) |
| "CR" no lugar do número, por polo (2.1) | ✘ | RC-58, como N3 |
| impugnação por qualquer cidadão (7.2) | ✘ (decidido) | RC-90 |

**Classificação: impossível sem trabalho externo** — rompe na primeira etapa que envolve o
candidato, e de novo na convocação.

#### N7 · Chamada pública com reserva sobre vagas conhecidas e entrega presencial (69/2026)

Sorteia, publica, convoca e manda comparecer: corte com `governedStage: NONE`. O RC-113 está
**corrigido no código**: com `NONE` declarado, quem progrediu é habilitado
(`ocupacao/application/selectors.py:401-421`, `habilitadas_pelo_corte`), e com 6 vagas publicadas a
apuração tem déficit a convocar. Entrega presencial: não há a forma "conferido presencialmente, não
retido" (P-12), mas o **não** comparecimento tem atestado próprio (`ATESTADO_NAO_ENTREGA_PRESENCIAL`,
`convocacao/domain/nomes.py:106`) e a **reclassificação** para o fim da fila existe
(`convocar.py:385-406`). Procurador e menor de idade: fora do modelo de identidade (P-12).
Impugnação: fora (RC-90). Inscrição: o 69 aponta "link na página" — se for o portal, entra.

**Classificação: completo com dependências externas** (a conferência presencial e o procurador
acontecem fora; o sistema registra o desfecho).

#### Fora do alvo
- **46/2026** (técnicos integrados, prova objetiva, 3.587 vagas, nove modalidades): fora por decisão
  (RC-110).
- **62/2026** (Mediador TSE): PDF digitalizado, sem texto extraível — não avaliado.

### 5. Capacidades que existem e não formam fluxo coerente entre si

1. **Cadastro de reserva declarado × convocação.** `reserveType`/`reserveLimit` são compostos pela
   tela (`interface/templates/interface/_perfil.html:105-120`), validados (`editais/domain/perfis.py:
   68-94`), publicados e exibidos (PDF, portal, visão institucional) — e nada os executa. Quem governa
   quantos suplentes há é o `cutRule`; o "limitado em N" é uma segunda declaração da mesma norma sem
   confronto (DP-05).
2. **`callRules` publicado e opaco** (`editais/models/perfis.py:387`, `publish_edital.py:141`,
   não retificável em `mutabilidade.py:292`): a "ordem de convocação" que dois Editais de reserva
   publicam em tabela não tem leitor.
3. **Cota com documento de autodeclaração, sem verificação.** A autodeclaração é exigida por
   Modalidade (044) e conferida na análise documental como papel; a verificação que o Edital manda
   fazer por comissão própria (CLVA) não tem Etapa aplicável, e o efeito (sair da reserva, ficar na
   AC) não tem forma.
4. **Etapa do Edital inteiro × recorte.** O corte recorta por Perfil × lista; a Etapa não. Uma Etapa
   que o Edital aplica a um grupo (entrevista do Grupo 1; verificação dos PPI) só se restringe pela
   faixa de um corte, e recorte sem corte emitido fica dormente — todos participam.
5. **Ordem sorteada × resultado documental.** O sorteio emite o ato de ordenação; a análise
   documental produz Resultados por inscrição que não viram lista pública, e só ficam visíveis e
   recorríveis se o marco publicado **enumerar** a Etapa documental — uma regra de composição que não
   aparece como exigência (`recursos/application/interpor.py:302-318`). `[VALIDAR por percurso]`
6. **Requerimento → exportação → matrícula.** O requerimento é estruturado e append-only; a
   exportação sai em planilha com três colunas em branco para o destino, e a efetivação da matrícula
   e a "matrícula homologada" que o Edital publica não voltam para o sistema.
7. **Encerrar × validade × convocar.** O Edital pode ser encerrado a qualquer momento depois de
   publicado; o Processo encerrado recusa convocar mas continua recebendo inscrição; não há validade.
   As três coisas não se falam.
8. **Retificação que acrescenta (048) × o que mudou.** A 048 dá porta de tela ao acréscimo; o resumo
   público continua calando o quadro por Modalidade, a cota, a janela, o corte e o método (RC-111), e
   o acréscimo de Modalidade não alcança quem já se inscreveu.
9. **Convocação por publicação × o sistema não publica.** A forma é declarada no Edital e executada
   como "diga onde publicou".
10. **Sorteio auditável × Edital como o Cefor o escreve.** O método executável (Loteria Federal) não
    é o descrito pelos Editais lidos.

### 6. Dependências fora do sistema

| Tipo | O quê | Onde se vê |
|---|---|---|
| decisão/obra externa (Ifes) | provedor de autenticação institucional; artefato e servidor de produção | T1, T2 |
| serviço externo | SMTP institucional (código de acesso, convocação) | T3 |
| serviço externo | Loteria Federal/Caixa (semente) | T8 |
| decisão institucional | redigir os Editais pela D-G3; fecho do documento com o Cefor (RC-23) | T8 |
| ferramenta externa + intervenção manual | importar o `.xlsx` no Sistema Acadêmico; preencher `COD_CURSO/TURNO/POLO`; importação nunca validada | T7 |
| publicação fora | "resultado preliminar da análise documental", "homologação das matrículas", convocação por publicação, cancelamento do Edital | T5, T6, RC-120 |
| execução administrativa fora | verificação da autodeclaração (CLVA/CPVA, videoconferência RNP); impugnação; procuração; entrega presencial; vinculação UAB/FAPES e bolsa | N2, N3, N6, N7 |
| planilha/papel | barema e ficha de títulos; teto de autopontuação; ordem nominal de convocação; cascata de grupos | N3, N4 |
| conhecimento tácito | enumerar a Etapa documental no marco para o candidato ver/recorrer; manter o Processo ATIVO durante a validade; não restaurar rascunho local em Edital com muitas coleções; retificar vagas a cada chamada da reserva | §5, T4, T10, N3 |
| comando de linha | `carregar_ceps` (auxiliar; sem ele o código IBGE sai vazio e o envio conclui — `doc/runbook-base-de-cep.md`) | — |

### 7. Conferências e correções à auditoria de 26/09

- **RC-58 confirmado pelo código** (sem percurso): `apuracao.py:265-287` + `convocar.py:249-297`.
- **RC-113 fechado no código**: `ocupacao/application/selectors.py:401-421`.
- **RC-37/RC-38**: a linha citada pela auditoria (`retificacao.py:1054`) está desatualizada; hoje é
  `interface/retificacao.py:1108`. A 048 os fecha **se** mesclada.
- **C7 é mais do que "pré-condição de operação real"**: sem ela a gestão responde 503 fora do modo
  demonstração (`interface/views.py:597-600`), então não existe hoje ambiente em que a instituição
  opere com identidades verdadeiras.
- **Barema**: a única ocorrência de "barema" no backend é um teste (`tests/acceptance/test_ciclo_do_173.py`,
  que exclui o barema do escopo); heteroidentificação aparece só como nome de Etapa num teste de porta
  decisória (`tests/integration/classificacao/test_porta_decisoria_enumerada.py:40`).
- Manual (`doc/manual/00-arquitetura-do-manual.md`, 12/09) diz que "o ciclo termina na divulgação" —
  vencido: convocação, requerimento e exportação existem desde a 016/019/029/031.

## 8. Síntese

**Nenhuma natureza roda de ponta a ponta em produção hoje**: a gestão não autentica fora do modo
demonstração (T1) e não há caminho de produção (T2). Fora de produção, num piloto assistido, a
resposta por natureza é:

| Natureza | Classificação | Primeiro ponto de ruptura (além de T1/T2) |
|---|---|---|
| N1 FIC por sorteio, remanescentes (78, 59, 77; 58, 158) | completo com dependências externas | sorteio só com Loteria Federal (`sorteios/infrastructure/fontes/__init__.py:83-87`); listas "resultado da documentação" e "homologação das matrículas" sem ato (017 D-002; 018 FR-017); matrícula por `.xlsx` com 3 colunas vazias, nunca importado (`matriculas/domain/colunas.py:198-215`; 031 T038) |
| N2 Pós EaD multipolo com cotas e verificação da autodeclaração (28, 149, 35) | parcialmente suportado | verificação CLVA/CPVA inexistente: Etapa do Edital inteiro (`editais/models/etapas.py:11-20`), Modalidade fixa após o envio (`inscricoes/application/rascunho.py:270,475`) |
| N3 Cadastro de reserva UAB com títulos (140, 173) | impossível sem trabalho externo | convocação: 0 vagas ⇒ `faltando = 0` ⇒ `sem_deficit` (`ocupacao/domain/apuracao.py:265-287`; `convocacao/application/convocar.py:249-297`); `callRules` sem leitor (`editais/models/perfis.py:387`); barema/teto fora (`avaliacoes/domain/pontuacao.py:67-80`) |
| N4 Orientadores com títulos + entrevista e cascata (14) | parcialmente suportado | cascata Grupo 1→2→3 sem forma; recorte sem corte fica dormente (`resultados/application/prontidao.py:326-354`) |
| N5 Unificado de aperfeiçoamento (57) | parcialmente suportado | mesma ruptura de N2 |
| N6 Técnico subsequente com CR, inscrição no SIGAA (76) | impossível sem trabalho externo | inscrição fora do sistema, sem porta de entrada (P-8); "CR" sem número (RC-58) |
| N7 Chamada pública com reserva sobre vagas conhecidas e entrega presencial (69) | completo com dependências externas | conferência presencial e procuração fora; o sistema registra o desfecho (`convocacao/domain/nomes.py:106`) — RC-113 corrigido (`ocupacao/application/selectors.py:401-421`) |

Transversal a todas: T3 (correio único fator), T4 (encerramento sem conclusão, sem validade;
Processo encerrado recusa convocar e continua recebendo inscrição), T5 (convocação por publicação
feita fora), T9 (Retificação: sem a 048 não acrescenta Modalidade/janela/corte; com ela, só para
frente; "O que mudou" cala o que mais pesa).
