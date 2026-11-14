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
preenchimento automático e ajuste à mão sem arrastar. A entrega **B** traz as duas tabelas append-only
— o ato e o horário publicado —, a conferência na moldura da `140`, a publicação no molde da `149` com
o veículo da `159`, a página pública e o horário na área do candidato. A entrega **C** acrescenta a
origem `AGENDA` aos avisos da `066` (um aviso por pessoa, como a pendência da `134`), revê a FR-084 da
`010` e traz remarcação, inclusão e cancelamento como atos individuais. A **D**, opcional, põe a agenda
nas pendências do Centro e de Minhas atividades, e o horário na tela da Ocorrência.

As decisões técnicas estão em [research.md](research.md) (`T-001` a `T-023`); o modelo, em
[data-model.md](data-model.md); as telas e as frases, em [contracts/](contracts/); o roteiro, em
[quickstart.md](quickstart.md).

## Technical Context

**Language/Version**: Python 3.13, Django 5.2; htmx servido de arquivo; nenhum JavaScript novo.

**Primary Dependencies**: as do projeto; nenhuma nova.

**Storage**: PostgreSQL, com três migrations:

- `agendamento/0001_agenda_da_etapa` (A): `AgendaDaEtapa`, `JanelaDaAgenda`, `BancaDaAgenda`,
  `Agendamento`;
- `agendamento/0002_atos_da_agenda` (B): `AtoDaAgenda`, `HorarioPublicado`, os gatilhos append-only e o
  de coerência;
- `avisos/0003_origem_agenda` (C): a origem, as constraints refeitas e `marco_id` anulável.

Duas tabelas append-only novas: o `M` da preparação do banco vai de 61 a **63**.

**Testing**: pytest contra PostgreSQL (`make test-pg`, com `DB_NAME` próprio):

- unidade para `horarios`, `configuracao`, `capacidade`, `preenchimento`, `conteudo` e `mensagem`
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
| V. Rastreabilidade e simplicidade | cada FR- e SC- tem tarefa e teste; nenhum JavaScript que duplique a regra; o `M` novo no `CLAUDE.md` e no README; nenhuma tabela além das do modelo do estudo |
| VI. Completude de jornada | cada entrega fecha com uma jornada pela interface: A, configurar e montar; B, conferir, publicar e o candidato ver; C, avisar e remarcar |

**Gate: aprovado.** Duas leituras a registrar, nenhuma violação:

- **Exclusão física do `Agendamento`.** A linha operacional é apagada ao liberar um horário em
  montagem e ao a configuração remover um horário. A Constituição proíbe a exclusão que compromete a
  rastreabilidade; aqui a trilha guarda estado anterior e posterior, e o que foi publicado mora no
  append-only (data-model, *Agendamento*). É o mesmo estatuto do rascunho.
- **A FR-084 da `010` é revista**, pela `D-010`, na entrega C — revisão de regra declarada na spec,
  com a redação anterior preservada, como fizeram a `019`, a `066`, a `134` e a `156`.

**Re-check pós-desenho: aprovado.** As duas tabelas append-only entram nas três camadas (classe,
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
│   │                                                 # B: AtoDaAgenda, HorarioPublicado (_AppendOnly)
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
│   └── application/
│       ├── leitura.py                                # a agenda, a participação, os vigentes (T-007, T-017)
│       ├── configurar.py                             # A: salvar, devolver quem perdeu o horário (FR-7208)
│       ├── montar.py                                 # A: agendar, mudar, liberar, prévia e aplicação
│       ├── conferir.py                               # B: conferência e assinatura (T-010)
│       ├── publicar.py                               # B: o ato (T-012)
│       └── atos_individuais.py                       # C: remarcar, incluir, cancelar
├── avisos/
│   ├── domain/nomes.py                               # C: AGENDA
│   ├── models.py, migrations/0003_origem_agenda.py   # C
│   └── application/{confirmar,despacho}.py           # C: reenvio e estado visual da origem nova
├── seguranca/papeis.py                               # B: TABELAS_APPEND_ONLY (63)
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
│   ├── urls.py, views.py                             # B: agendas/<id>/, seção da seleção, bloco na inscrição
│   ├── templates/portal/agenda_da_etapa.html, _agendas_da_selecao.html, _horario_da_inscricao.html
│   └── static/portal/portal.css                      # B
└── interface/{centro,atividades}.py, templates/interface/ocorrencia.html   # D
specs/010-area-do-candidato/spec.md                   # C: FR-084 revista (sete situações)
specs/033-navegacao-por-capacidade/inventario-das-negativas.md   # A, B, C: um 404 por linha
backend/tests/
├── unit/agendamento/                                 # A, B, C
├── integration/agendamento/                          # A, B, C
├── interface/test_agenda_da_etapa_*.py, test_vocabulario_da_agenda_da_etapa.py
├── portal/test_agenda_publica.py, test_horario_na_area_do_candidato.py
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
| **B** | Conferir, publicar e mostrar | publicar com conferência, veículo e autoridade; a página pública e a área do candidato mostram o horário | A |
| **C** | Avisar e remarcar | um aviso por pessoa, as falhas com reenvio; remarcação, inclusão e cancelamento | B |
| D | Orientação | a agenda como pendência no Centro e em Minhas atividades; o horário na Ocorrência | B |

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
| O `M` do provisionamento | `CLAUDE.md` | 61 → 63 na B, com o README e `test_database_permissions.py` |
| Guardião da FR-084 e a ordem com a `156` | `test_situacoes_de_mensagem.py` | reler o guardião no dia da C (T-018) |
| Varredura de vocabulário com lista literal | `tests/**/test_vocabulario_*` | varredura própria das telas novas (T-020) |
| Inventário de negativas | `033` | uma linha por `Http404` novo, em cada entrega |
| CSP e classe sem regra na folha | `politica_de_conteudo.py`, `test_acessibilidade` | nenhum estilo em linha; toda classe nova com regra; `}}` e `%}` fora da folha |
| Nome "agenda" | `interface/agenda.py` (`101`) | "agenda da Etapa" em arquivo, rota e folha (T-001) |
| Limpeza por `DELETE` muda a ordem física | `tests/conftest.py` | toda consulta da agenda com `ORDER BY` completo |

## Pontos para o usuário

O `/speckit-analyze` de 14/11 não teve achado crítico. Três leituras do plano interpretam a spec, e
são do usuário; nenhuma bloqueia a entrega A.

1. **Avisos com a chave da `066` desligada.** A FR-7230 diz que a publicação MUST criar um aviso por
   pessoa; o plano não cria aviso nenhum com `AVISOS_AOS_CANDIDATOS` desligada — o padrão de produção
   até a validação de LGPD da `066` —, porque o aviso é origem daquele app e herda a chave dele, e um
   aviso criado agora sairia dias depois, quando a chave fosse ligada (T-018). A alternativa é revisar
   a FR-7230 para dizer isso, ou ligar a chave só para a origem `AGENDA`.
2. **Sem documento PDF.** A FR-7224 dá à publicação "a mesma natureza da relação de convocados da
   `149`", que tem PDF; ela não pede PDF, e o plano não o gera (T-013). Se o PDF for o documento
   oficial também aqui, é revisão da FR-7224, com uma tabela append-only a mais (o `M` iria a 64).
3. **Quem publica.** A spec chama de presidência quem publica; a FR-7255 pede a permissão de gerir a
   Etapa e o escopo do Edital, e o plano aceita as duas bases da gestão da comissão — a permissão
   `comissao:gerir` e a presidência (T-021). Uma porta só da presidência seria revisão da FR-7255.

## Complexity Tracking

| Violação | Por que é necessária | Alternativa mais simples descartada porque |
|---|---|---|
| Gatilho de coerência no `HorarioPublicado` | o `substitui` atravessa tabelas (a mesma inscrição, a mesma agenda) | só na aplicação, a cadeia de remarcações poderia apontar outra pessoa sem que o banco recusasse |
| `marco_id` anulável no `Aviso` da `066` | a agenda é da Etapa, e não de um marco | um marco fictício seria dado falso numa tabela append-only |
