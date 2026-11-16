# Implementation Plan: A distribuição coerente com a agenda e a programação de quem avalia

**Branch**: `claude/agenda-bancas-comunicacao-078bfc` (worktree `nifty-dhawan-f179bd`), sobre a `main`
em `619a4ae0` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

**Input**: a spec da `179`, com as decisões Q-A, Q-B e Q-C aprovadas pelo usuário em 16/11; o estudo
`doc/estudo-agenda-para-as-bancas-2026-11-16.md` (três rodadas, com a simulação do rodízio); e o
pedido do usuário de manter os dois incrementos com entregas e validações separadas, detalhando a
concorrência, a revisão dos requisitos anteriores e a extensão do despacho.

## Summary

**Incremento 1 — a distribuição coerente e a programação no GPS.** Nenhuma migration. Um módulo de
domínio puro calcula o conflito de horário de uma pessoa (sobreposição de início e fim, no mesmo
Edital); a Distribuição o recusa como regra sobre a linha, ao lado do impedimento; o rodízio percorre
a agenda e trata o par em conflito como inelegível; a remarcação e a inclusão dizem, antes, quem
ficará em conflito, e conferem isso sob a trava; a agenda publicada, a conferência e a Distribuição
mostram a coerência da Etapa. A Mesa ganha a visão **Programação**, e Minhas atividades, a próxima
entrevista. Revê a FR-085 e a FR-107 da `012` e a FR-7229 e a FR-7240 da `167`.

**Incremento 2 — o aviso por e-mail ao avaliador.** Uma migration em `avisos`: a origem
`PROGRAMACAO` e o destinatário que pode ser um membro da comissão, com o resumo da programação
avisada. Um gesto da comissão na agenda publicada avisa quem nunca foi avisado e quem teve a
programação mudada, pelo despacho da `066`, sem remetente novo. Revê a FR-084 da `010`. Começa
quando o Incremento 1 estiver na `main`, e não reformula nada dele: lê a mesma programação.

## Technical Context

**Language/Version**: Python 3.13, Django 5 (o do repositório)

**Primary Dependencies**: nenhuma nova. htmx e as folhas da gestão, como hoje.

**Storage**: PostgreSQL. Incremento 1 sem migration; Incremento 2 com `avisos/0005_origem_programacao`
(colunas e constraints em tabelas append-only existentes; nenhuma tabela nova; o `M` continua 69).

**Testing**: pytest contra PostgreSQL (`make test-pg`), com os casos transacionais onde a garantia é do
banco (concorrência do lote, append-only, constraints novas). Testes de domínio puros para o conflito
e o rodízio. Testes de orçamento de consulta da Mesa e de Minhas atividades.

**Target Platform**: o monólito da gestão (`/gestao/`), e o despacho de avisos (`despachar_avisos`, timer
de um minuto).

**Project Type**: aplicação web, monólito Django.

**Performance Goals**: a Programação paga o mesmo número de consultas com 5 e com 500 Atribuições;
Minhas atividades, o mesmo com uma e com onze comissões; a coerência da Etapa em consultas fixas
(T-002, T-009, T-010).

**Constraints**: CSP sem `unsafe-inline` (estilo em arquivo); 375 px sem rolagem horizontal; a varredura
de vocabulário; a varredura das situações de envio; o inventário de negativas para 404 novo (nenhum é
previsto).

**Scale/Scope**: Etapa de entrevista com dezenas de pessoas por banca e dia, 2 a 10 avaliadores,
até 3 bancas simultâneas; a Distribuição continua dimensionada para 600+ inscrições (a `012`).

## Constitution Check

*GATE: antes da pesquisa, e de novo depois do desenho.*

| Princípio | Como o plano o atende | Situação |
|---|---|---|
| I. Linguagem ubíqua | Atribuição, Etapa, banca, agenda, programação, conflito — o vocabulário da `012` e da `167`; "banca" continua ponto de atendimento | ✅ |
| II. Integridade normativa | nada publicado muda; a agenda publicada e os atos dela não são tocados; a programação é derivada (`D-001`), sem segunda fonte | ✅ |
| III. Segurança e dados | negar por padrão: as guardas de hoje (Distribuição, agenda, Mesa); sala só ao avaliador atribuído (`D-006`); nenhum avaliador no público (`D-007`); e-mail sem dado de candidato (`D-008`); trilha sem e-mail nem sala (FR-8232); LGPD na seção abaixo | ✅ |
| IV. Regras explícitas | o conflito é regra de domínio, verificada no comando sob trava (T-004, T-006); o lote declara o que recusou; a remarcação e o aviso mostram o alcance antes e o conferem por assinatura (T-006, T-019) | ✅ |
| V. Rastreabilidade e simplicidade | sem tabela nova, sem fila nova, sem remetente novo; requisitos revistos nas specs donas, datados (T-013) | ✅ |
| VI. Jornada | Inc. 1: a comissão distribui por sessão e o avaliador acha a programação, pela tela; Inc. 2: o avaliador recebe o aviso e chega à Mesa pelo link | ✅ |

**LGPD.** Dados novos expostos: (a) ao avaliador, o horário, a banca e a sala de entrevistas que ele já
avalia — finalidade: executar a avaliação; minimização: só as dele; (b) à comissão, quem avalia cada
pessoa — dado que a Distribuição já mostra; (c) por e-mail, ao avaliador, contagem, datas e bancas,
sem candidato; o endereço é o institucional que a `106` já guarda. Nada novo é gravado sobre o
candidato. A retenção da `auth_user` continua pendência da ativação do SSO, e não desta feature.

**Reavaliação depois do desenho**: sem violação; nada em *Complexity Tracking*.

## Project Structure

### Documentation (this feature)

```text
specs/179-distribuicao-e-programacao-do-avaliador/
├── spec.md
├── plan.md              # este
├── research.md          # T-001 a T-019
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── telas.md         # telas, rotas e frases
│   └── validacao.md     # onde o conflito é conferido, concorrência, testes
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── avaliacoes/
│   ├── domain/conflito.py                  # novo, puro (Inc. 1)
│   ├── domain/rodizio.py                   # horário e compromissos (Inc. 1)
│   ├── domain/mensagem_da_programacao.py   # novo, puro (Inc. 2)
│   ├── application/programacao.py          # novo: programação, coerência, próximas (Inc. 1)
│   ├── application/distribuicao.py         # recusa por conflito; rodízio com a agenda (Inc. 1)
│   ├── application/selectors.py            # mesa(): a visão Programação (Inc. 1)
│   └── application/aviso_da_programacao.py # novo: estados, gesto (Inc. 2)
├── agendamento/
│   ├── application/leitura.py              # horarios_do_edital (Inc. 1)
│   ├── application/atos_individuais.py     # assinatura dos conflitos; trilha (Inc. 1)
│   └── application/conferir.py             # conflitos como aviso (Inc. 1)
├── avisos/
│   ├── domain/nomes.py                     # PROGRAMACAO (Inc. 2)
│   ├── models.py                           # destinatário inscrição ou membro (Inc. 2)
│   ├── migrations/0005_origem_programacao.py (Inc. 2)
│   └── application/despacho.py             # três pontos; REVISAO_DA_FR_084_PELA_179 (Inc. 2)
└── interface/
    ├── views.py                            # distribuicao (filtro), minha_etapa (visão)
    ├── agenda_da_etapa.py                  # remarcar, conferir, publicada, avisar (Inc. 2)
    ├── atividades.py                       # próxima entrevista
    ├── templates/interface/{distribuicao,agenda_remarcar,agenda_conferir,agenda_publicada,minha_etapa,_atividade}.html
    ├── templates/interface/agenda_avisar_avaliadores.html (Inc. 2)
    └── static/interface/telas/{minhas-etapas,agenda-da-etapa}.css

backend/tests/
├── unit/avaliacoes/test_conflito.py, test_rodizio_com_agenda.py
├── integration/avaliacoes/test_distribuicao_com_agenda.py, test_programacao.py
├── interface/test_distribuicao_por_sessao.py, test_programacao_na_mesa.py, test_agenda_e_avaliadores.py
├── performance/test_escala_da_mesa.py, test_minhas_atividades_em_escala.py   # casos novos
├── unit/avisos/, integration/avisos/test_aviso_da_programacao.py (Inc. 2)
└── test_situacoes_de_mensagem.py (Inc. 2)

specs/012-mesa-de-avaliacao/spec.md      # FR-085, FR-107 revistas (Inc. 1)
specs/167-agendamento-da-etapa/spec.md   # FR-7229, FR-7240 revistas (Inc. 1)
specs/010-area-do-candidato/spec.md      # FR-084 revista (Inc. 2)
```

**Structure Decision**: nenhum app novo. O conflito e a programação em `avaliacoes`, que já depende
de quem avalia; a leitura dos horários em `agendamento`, que continua sem importar `avaliacoes` (T-001).
O aviso em `avaliacoes` gravando nas tabelas de `avisos`, como a `167` grava pelo `agendamento`.

## Entregas e validações

### Incremento 1 — um PR

| Fase | Conteúdo | Validação da fase |
|---|---|---|
| 1.1 Domínio | `conflito.py`; rodízio com horário e compromissos | testes puros; a simulação 43 × 6 × 3 em dez ordens com zero conflito (SC-2842) |
| 1.2 Leitura | `horarios_do_edital`; `programacao.py` (programação, coerência, próximas) | consultas fixas; as duas fontes; conflito entre Etapas do Edital |
| 1.3 Distribuição | recusa por linha; conflito dentro do lote; ordem da agenda; filtro de sessão | caso transacional de dois lotes concorrentes; SC-2840, SC-2841 |
| 1.4 Agenda | remarcação/inclusão com "Avaliam", marca de ocupado, assinatura dos conflitos, trilha; conferência com aviso; agenda publicada com coluna e coerência | SC-2845; `conflitos_mudaram`; SC-2846 (varredura dos três canais) |
| 1.5 Avaliador | Mesa: visão Programação; Minhas atividades: próxima entrevista | SC-2843; orçamento de consulta; 375 px; política de conteúdo (SC-2850) |
| 1.6 Normas | FR-085 e FR-107 na `012`; FR-7229 e FR-7240 na `167`; README; Visão do Sistema se tocada | `test_citacoes_de_requisito.py`; `test_readme_acompanha_o_codigo.py` |

**Fecha o incremento:** `make lint check` (os dois passos do `ruff`), a suíte inteira contra PostgreSQL
uma vez, o percurso do quickstart pela tela, e o SC-2844 deixado como validação humana.

### Incremento 2 — outro PR, depois do merge do primeiro

| Fase | Conteúdo | Validação da fase |
|---|---|---|
| 2.1 Modelo e demonstração | `avisos/0005`; `nomes.PROGRAMACAO`; constraints; o C20 com a comissão da Entrevista com conta e e-mail (research T-020) | migration aplicada e revertida; append-only nas três camadas; constraints recusam os casos inválidos |
| 2.2 Despacho | os três pontos (T-015); a guarda dos leitores de `destinatario.inscricao` | as origens de hoje sem mudança; a nova despachada, com retentativa e reenvio |
| 2.3 Aviso | `mensagem_da_programacao.py`; `aviso_da_programacao.py` (destinatários, estados, resumo, gesto) | SC-2847, SC-2848; um por pessoa por gesto; zero sem mudança |
| 2.4 Tela | seção Avaliadores com o gesto; confirmação; reenvio | `alcance_mudou`; habilitação desligada; 375 px |
| 2.5 Norma | FR-084 na `010`; `REVISAO_DA_FR_084_PELA_179`; par em `test_situacoes_de_mensagem.py` | SC-2849 |

**Fecha o incremento:** idem, e o quickstart do Incremento 2 com `despachar_avisos` à mão.

## Riscos

| Risco | Onde morde | Mitigação |
|---|---|---|
| A ordem nova do lote muda a ordem de um resultado declarado que algum teste lê | `tests/interface/test_distribuicao.py`, testes da `012` | só muda com horário; Etapa sem agenda percorre como hoje (T-004) |
| O rodízio com agenda muda propostas que testes de hoje fixam | `test_progressao_no_rodizio.py` | sem `horario`, `propor` é byte a byte o de hoje (T-005); os testes de hoje não têm agenda |
| A Programação estoura o orçamento da Mesa | `test_escala_da_mesa.py` | uma consulta a mais, fixa (T-007); caso de 500 Atribuições |
| A próxima entrevista estoura Minhas atividades | `test_minhas_atividades_em_escala.py` | consulta agregada única (T-009) |
| Texto novo fere a varredura de vocabulário | `test_vocabulario_da_agenda_da_etapa.py` e as listas literais | rodar as varreduras na fase 1.4 e 1.5; acrescentar as telas novas às listas, se a regra o pedir |
| Classe nova sem regra na folha | `test_acessibilidade` | toda classe com regra em `telas/*.css`, sem `}}` nem `%}` |
| `destinatario.inscricao` nulo quebra um leitor esquecido da `066` | Inc. 2 | a guarda dos leitores (T-015) e os testes das origens de hoje rodando com um aviso de programação na mesma fila |
| A pessoa institucional não existe na demonstração | percurso do Inc. 2 (Princípio VI) | o C20 cria os membros da comissão com conta e e-mail de exemplo (research T-020), e o percurso se faz pela tela |
| Revisão de norma desalinhada do código | as cinco FR revistas | cada revisão no PR que a torna verdade (T-013) |

## Complexity Tracking

Nenhuma violação a justificar.
