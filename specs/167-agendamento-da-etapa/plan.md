# Implementation Plan: O agendamento dos participantes da Etapa

**Branch**: `claude/167-plano-agendamento`, sobre `claude/agendamento-etapa-gps-9bca12` (#546)
| **Date**: 2026-11-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/167-agendamento-da-etapa/spec.md`; o estudo
`doc/estudo-agendamento-da-etapa-2026-11-14/` (regras R-01 a R-26, modelo do §2.5, concorrência do
§2.6, entregas, redesign e protótipo aprovados).

## Summary

Uma Etapa ganha, se a comissão quiser, uma **agenda**: operacional, referida pelo `etapa_id` como a
alocação da comissão, sem lista própria de participantes — quem precisa de horário é quem
`participacao_detalhada` põe na Etapa, a cada leitura. Os horários são uma função pura da
configuração (dias, janelas, duração, intervalo, bancas), e só o agendamento é gravado, com as duas
unicidades no banco.

Um app novo, `agendamento`, guarda quatro tabelas operacionais — a agenda, as janelas e as bancas,
que são a configuração, e o agendamento corrente — na entrega **A**, com a
configuração que calcula a capacidade ao digitar (htmx sobre o mesmo domínio) e a montagem com prévia,
preenchimento automático e ajuste à mão sem arrastar. A entrega **B** traz as três tabelas append-only
— o ato, o horário publicado e o documento PDF do ato —, a conferência na moldura da `140`, a
publicação no molde da `149` com o veículo da `159` e o documento gravado como o dela, a página
pública e o horário na área do candidato. A entrega **C** acrescenta a
origem `AGENDA` aos avisos da `066` (um aviso por pessoa, como a pendência da `134`), revê a FR-084 da
`010` e traz remarcação, inclusão e cancelamento como atos individuais. A **D**, opcional, põe a agenda
nas pendências do Centro e de Minhas atividades, e o horário na tela da Ocorrência; por decisão do
usuário de 14/11, ficava fora desta implementação, e foi feita no mesmo dia, num PR empilhado sobre o
da C.

As decisões técnicas estão em [research.md](research.md) (`T-001` a `T-023`); o modelo, em
[data-model.md](data-model.md); as telas e as frases, em [contracts/](contracts/); o roteiro, em
[quickstart.md](quickstart.md).

## Technical Context

**Language/Version**: Python 3.13, Django 5.2; htmx servido de arquivo; nenhum JavaScript novo.

**Primary Dependencies**: as do projeto; nenhuma nova.

**Storage**: PostgreSQL, com três migrations:

- `agendamento/0001_agenda_da_etapa` (A): `AgendaDaEtapa`, `JanelaDaAgenda`, `BancaDaAgenda`,
  `Agendamento`;
- `agendamento/0002_atos_da_agenda` (B): `AtoDaAgenda`, `HorarioPublicado`, `DocumentoDoAtoDaAgenda`,
  os gatilhos append-only e o de coerência;
- a origem `AGENDA` nos avisos (C): a origem, as constraints refeitas e `marco_id` anulável — a
  `avisos/0003`, ou a `0004` se a `168` entrar antes (*Coordenação com a 168*).

Três tabelas append-only novas: o `M` da preparação do banco vai de 65 a **68**.

**Testing**: pytest contra PostgreSQL (`make test-pg`, com `DB_NAME` próprio):

- unidade para `horarios`, `configuracao`, `capacidade`, `preenchimento`, `conteudo`, `documento` e
  `mensagem`
  (SC-2391, SC-2392 na parte pura);
- integração para os comandos, as unicidades sob duas transações, a publicação, os gatilhos, os
  privilégios, os avisos e os atos individuais;
- interface para as telas da gestão sob a CSP, o estreito, o vocabulário e a gramática das portas;
- portal para a página pública, a busca, a privacidade dos bytes e do HTML, e a área do candidato.

**Target Platform**: o monólito Django: gestão em `/gestao/`, portal público e área do candidato, e o
correio do despacho.

**Project Type**: aplicação web, backend com templates.

**Performance Goals**: a montagem lê a agenda inteira em número fixo de consultas — a agenda com as
janelas e as bancas, os agendamentos com a inscrição, a participação uma vez por requisição —, e não
por célula (3 dias × 2 bancas × 32 horários = 192 células). A capacidade ao digitar não toca o banco
além da participação, que cabe em cache por requisição. A página pública e a área do candidato em
número fixo de consultas (o orçamento do portal da `118`).

**Constraints**: a CSP sem `unsafe-inline` (estilo em arquivo; o htmx com `allowEval:false`); tudo em
português; as garantias que hoje são do banco continuam do banco; o htmx não troca 4xx, e o fragmento
recusado volta 200 com `HX-Retarget`; nada de `<table>` no portal.

**Scale/Scope**: Etapas de dezenas a poucas centenas de pessoas atendidas (43 no cenário A, 23 no B),
com uma a três bancas e até alguns dias.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como a feature o cumpre |
|---|---|
| I. Linguagem ubíqua | agenda, janela, banca, agendamento, ato da agenda, horário publicado, remarcação, inclusão, cancelamento — o vocabulário da spec; banca é ponto de atendimento, e não grupo de avaliadores (`D-004`); o nome "Agenda" sozinho fica com a `101` (T-001) |
| II. Integridade normativa e imutabilidade | a agenda é operacional e não toca o Edital nem pede Retificação (`D-001`); a participação tem fonte única (`D-002`); os horários são derivados (`D-003`); a publicação e cada ato individual são append-only, e a remarcação substitui sem apagar (`D-006`); a zona é a institucional |
| III. Segurança, LGPD e auditoria | negar por padrão, com escopo do Edital e base da gestão da comissão (T-021); o endereço da sala só à própria pessoa (FR-7229); a página pública sem CPF, e-mail, telefone ou Modalidade, e só o protocolo na Etapa por Modalidade (`D-009`); a trilha sem e-mail nem sala (T-019); os avisos sob a chave da `066` (T-018) |
| IV. Regras explícitas | as oito recusas da configuração, a ordem do preenchimento escrita na tela, os impedimentos da publicação nomeados com o caminho, a confirmação conferida por assinatura e idempotente |
| V. Rastreabilidade e simplicidade | cada FR- e SC- tem tarefa e teste; nenhum JavaScript que duplique a regra; o `M` novo no `CLAUDE.md` e no README; uma só tabela além das do modelo do estudo, a do documento, justificada pelo que preserva (T-013) |
| VI. Completude de jornada | cada entrega fecha com uma jornada pela interface: A, configurar e montar; B, conferir, publicar e o candidato ver; C, avisar e remarcar |

**Gate: aprovado.** Duas leituras a registrar, nenhuma violação:

- **Exclusão física do `Agendamento`.** A linha operacional é apagada ao liberar um horário em
  montagem e ao a configuração remover um horário. A Constituição proíbe a exclusão que compromete a
  rastreabilidade; aqui a trilha guarda estado anterior e posterior, e o que foi publicado mora no
  append-only (data-model, *Agendamento*). É o mesmo estatuto do rascunho.
- **A FR-084 da `010` é revista**, pela `D-010`, na entrega C — revisão de regra declarada na spec,
  com a redação anterior preservada, como fizeram a `019`, a `066`, a `134` e a `156`.

**Re-check depois das decisões de 14/11 (`D-011` a `D-013`): aprovado.** O documento PDF é gerado uma
vez, no ato, e servido como foi gerado (Princípio II); os avisos não ganham chave nem envio próprios
(Princípio V); a autorização continua a da gestão da comissão, negada por padrão, com o escopo do
Edital no servidor (Princípio III).

**Re-check pós-desenho: aprovado.** As três tabelas append-only entram nas três camadas (classe,
gatilho, privilégio ausente), e nenhuma recebe `FOR UPDATE` (T-009). A `avisos` não passa a conhecer a
`agendamento`: o vínculo fica no `HorarioPublicado` (T-018).

## Project Structure

### Documentation (this feature)

```text
specs/167-agendamento-da-etapa/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── recusas.md
│   └── telas.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/config/settings/base.py                       # INSTALLED_APPS + agendamento (A)
backend/processo_seletivo/
├── agendamento/                                      # app novo (T-001)
│   ├── models.py                                     # A: AgendaDaEtapa, JanelaDaAgenda, BancaDaAgenda, Agendamento
│   │                                                 # B: AtoDaAgenda, HorarioPublicado, DocumentoDoAtoDaAgenda (_AppendOnly)
│   ├── migrations/0001_agenda_da_etapa.py            # A
│   ├── migrations/0002_atos_da_agenda.py             # B, gatilhos em SQL
│   ├── domain/
│   │   ├── nomes.py                                  # formas, origens, espécies, situações
│   │   ├── horarios.py                               # Configuracao, Horario, derivar, sobras (T-003, T-004)
│   │   ├── configuracao.py                           # problemas (T-005)
│   │   ├── capacidade.py                             # Capacidade, atalhos (T-006)
│   │   ├── preenchimento.py                          # propor (T-011)
│   │   ├── recusas.py                                # códigos e frases (T-008)
│   │   ├── conteudo.py                               # B: o conteúdo público (T-014)
│   │   └── mensagem.py                               # C: assunto e corpo por pessoa (T-018)
│   ├── infrastructure/documento.py                   # B: render_agenda_pdf, sem banco (T-013)
│   └── application/
│       ├── leitura.py                                # a agenda, a participação, os vigentes (T-007, T-017)
│       ├── configurar.py                             # A: salvar, devolver quem perdeu o horário (FR-7208)
│       ├── montar.py                                 # A: agendar, mudar, liberar, prévia e aplicação
│       ├── conferir.py                               # B: conferência e assinatura (T-010)
│       ├── publicar.py                               # B: o ato (T-012)
│       └── atos_individuais.py                       # C: remarcar, incluir, cancelar
├── avisos/
│   ├── domain/nomes.py                               # C: AGENDA
│   ├── models.py, migrations/000N_origem_agenda.py   # C: 0003, ou 0004 depois da 168
│   └── application/{confirmar,despacho}.py           # C: reenvio e estado visual da origem nova
├── seguranca/papeis.py                               # B: TABELAS_APPEND_ONLY (68)
├── interface/
│   ├── agenda_da_etapa.py                            # as views da gestão (T-020)
│   ├── urls.py                                       # as rotas de contracts/telas.md
│   ├── views.py                                      # a guarda comum extraída (T-021); seção na Distribuição
│   ├── templates/interface/
│   │   ├── distribuicao.html                         # A: a seção "Agenda"
│   │   ├── agenda_configurar.html, _agenda_capacidade.html          # A
│   │   ├── agenda_montar.html, _agenda_grade.html, _agenda_painel.html  # A
│   │   ├── agenda_conferir.html                      # B
│   │   ├── agenda_publicada.html                     # B, C
│   │   └── agenda_remarcar.html, agenda_cancelar.html  # C
│   └── static/interface/
│       ├── gestao/componentes.css                    # controle segmentado, seletor de horário, painel de ação, veredito
│       └── telas/agenda-da-etapa.css                 # grade, simulador, estreito
├── portal/
│   ├── urls.py, views.py                             # B: agendas/<id>/, o documento de cada ato, seção da seleção, bloco na inscrição
│   ├── templates/portal/agenda_da_etapa.html, _agendas_da_selecao.html, _horario_da_inscricao.html
│   └── static/portal/portal.css                      # B
└── interface/{centro,atividades}.py, templates/interface/ocorrencia.html   # D
specs/010-area-do-candidato/spec.md                   # C: FR-084 revista (sete situações)
specs/033-navegacao-por-capacidade/inventario-das-negativas.md   # A, B, C: um 404 por linha
backend/tests/
├── unit/agendamento/                                 # A, B, C
├── integration/agendamento/                          # A, B, C
├── interface/test_agenda_da_etapa_*.py, test_vocabulario_da_agenda_da_etapa.py
├── portal/test_agenda_publica.py, test_horario_na_area_do_candidato.py, test_documento_da_agenda.py
└── migrations/test_migrations.py, integration/test_database_permissions.py, test_situacoes_de_mensagem.py
```

**Structure Decision**: o monólito existente, com um app novo, `agendamento`, porque o ato é outro e
as migrations de `comissoes`, `editais` e `resultados` têm contagem guardada (T-001). As telas da
gestão num módulo próprio de `interface`, porque `views.py` passa de 13 mil linhas; as do portal no
`views.py` dele, como a `149`.

## Entregas e ordem

Uma spec, três PRs obrigatórios e um opcional, como a `110` (A, B, C). Cada PR cabe numa sessão e
fecha com uma jornada demonstrável pela interface do ator (Constituição, VI).

| # | Entrega | O ator consegue | Depende de |
|---|---|---|---|
| **A** | Configurar e montar | configurar, ver a capacidade, preencher com prévia e ajustar à mão, sem publicar | — |
| **B** | Conferir, publicar e mostrar | publicar com conferência, veículo e autoridade, com o documento PDF; a página pública e a área do candidato mostram o horário | A |
| **C** | Avisar e remarcar | um aviso por pessoa, as falhas com reenvio; remarcação, inclusão e cancelamento | B |
| D | Orientação *(opcional)* | a agenda como pendência no Centro e em Minhas atividades; o horário na Ocorrência | B |

Dentro de cada entrega: o domínio puro e os testes de unidade, o modelo e a migration, os comandos e
os testes de integração, as telas e os de interface, os guardiões, e por fim a jornada no navegador.

## Riscos

| Risco | Onde | Mitigação |
|---|---|---|
| A participação muda entre a prévia, a conferência e a confirmação | `prontidao.py` | assinatura com os pares, e não só a `revision` (T-010) |
| Dois operadores no mesmo horário | montagem e remarcação | trava da agenda + `UNIQUE`, com o `IntegrityError` traduzido em `atomic()` próprio (T-009) |
| Deadlock com a convocação | trava do Processo | ordem fixa Processo → agenda; a montagem não pega a do Processo (T-009) |
| `FOR UPDATE` em append-only | role de runtime | travar só a `AgendaDaEtapa` (T-009) |
| Fuso | horários derivados | data e hora locais em `America/Sao_Paulo`, convertidas uma vez (T-003) |
| Evento retificado depois | `EventoCronograma` | a conferência relê o Evento vigente; publicada, a gestão é avisada e o horário vale (Edge Cases) |
| O `M` do provisionamento | `CLAUDE.md` | 65 → 68 na B, com o README e `test_database_permissions.py` |
| O compositor do PDF muda depois | `publicacoes/infrastructure/pdf.py` | o portal serve os bytes gravados, nunca recompostos (T-013) |
| A `168` mexe nos mesmos avisos e no mesmo acompanhamento | `avisos/migrations`, `portal` | *Coordenação com a 168*, abaixo |
| Guardião da FR-084 e a ordem com a `156` | `test_situacoes_de_mensagem.py` | reler o guardião no dia da C (T-018) |
| Varredura de vocabulário com lista literal | `tests/**/test_vocabulario_*` | varredura própria das telas novas (T-020) |
| Inventário de negativas | `033` | uma linha por `Http404` novo, em cada entrega |
| CSP e classe sem regra na folha | `politica_de_conteudo.py`, `test_acessibilidade` | nenhum estilo em linha; toda classe nova com regra; `}}` e `%}` fora da folha |
| Nome "agenda" | `interface/agenda.py` (`101`) | "agenda da Etapa" em arquivo, rota e folha (T-001) |
| Limpeza por `DELETE` muda a ordem física | `tests/conftest.py` | toda consulta da agenda com `ORDER BY` completo |

## Decisões do usuário sobre os pontos do plano (14/11)

O primeiro `/speckit-analyze` não teve achado crítico, e o plano levou ao usuário três leituras da
spec. As três foram decididas no mesmo dia, e a spec foi revista com elas (*Clarifications*, segunda
rodada):

1. **Avisos** (`D-011`). A habilitação dos avisos aos candidatos da `066` é o controle único.
   Desligada, a publicação acontece sem aviso, e as telas dizem isso; ligada depois, nenhum aviso de
   ato anterior nasce. Ligada, a conferência mostra quantos avisos, para quem e a prévia (T-018, T088).
2. **PDF** (`D-012`). Cada ato tem documento PDF, gerado uma vez e gravado, no molde da `149`; a
   página pública mostra o vigente e os documentos em ordem. Uma tabela a mais, justificada pelo que
   preserva (T-013, T086, T087, T091).
3. **Quem publica** (`D-013`). Quem gere a comissão, a presidência inclusive, com o escopo do Edital
   conferido no servidor; a autoridade signatária é escolha distinta. Nenhum papel novo (T-021, T089).

A implementação faz **A, B e C**; a **D** ficava fora, e foi feita depois, num PR próprio.

## Coordenação com a 168

A `168` (orientação da verificação da autodeclaração, #551, sem merge) mexe em dois lugares que a
`167` também toca. Nenhuma das duas bloqueia a outra; quem entrar **depois** acomoda a primeira, e as
regras abaixo valem nos dois sentidos.

| Ponto | `168` | `167` | Regra comum |
|---|---|---|---|
| Migration dos avisos | `avisos/0003_origem_passo`: origem `PASSO`, `marco_id` anulável, `etapa_id` novo | origem `AGENDA`, `marco_id` anulável | uma migration por feature, na ordem do merge; `marco_id` nulo **só** em `PASSO` e `AGENDA`; com o `etapa_id` presente, o aviso da agenda o preenche (T063) |
| CHECKs do `Aviso` | `ck_aviso_origem_conhecida` com quatro origens | idem, com `AGENDA` | quem entra depois refaz o CHECK com as cinco, e não com as suas |
| Acompanhamento do candidato | o degrau da Etapa restrita, que é "o lugar" do horário quando houver agenda (o requisito da `168` que faz do degrau o lugar do horário) | o bloco do horário na inscrição (T054) | **um cartão por Etapa**: na Etapa restrita, o horário entra no degrau da `168`; nas outras, o bloco da `167`. A fonte é `horarios_da_inscricao` (T050, T090) |
| Avisos ao candidato | o aviso do passo ("há um passo a mais") | o aviso da agenda (o horário) | são fatos diferentes, e não duplicata; nenhum dos dois substitui o outro |

## Complexity Tracking

| Violação | Por que é necessária | Alternativa mais simples descartada porque |
|---|---|---|
| Gatilho de coerência no `HorarioPublicado` | o `substitui` atravessa tabelas (a mesma inscrição, a mesma agenda) | só na aplicação, a cadeia de remarcações poderia apontar outra pessoa sem que o banco recusasse |
| `marco_id` anulável no `Aviso` da `066` | a agenda é da Etapa, e não de um marco | um marco fictício seria dado falso numa tabela append-only |
| `DocumentoDoAtoDaAgenda`, sétima tabela | os bytes do documento publicado, que o compositor não reproduz depois (`D-012`) | gerar sob demanda do conteúdo daria outro arquivo para o mesmo ato quando o compositor mudasse |
