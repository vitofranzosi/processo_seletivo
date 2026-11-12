# Implementation Plan: O desfecho da convocação comunicado ao candidato (156)

**Branch**: `claude/156-plano-e-tarefas`, sobre a revisão da spec (PR #488) e a `main` em `17e9665c` |
**Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)

## Summary

O portal passa a explicar cada desfecho em duas camadas — uma frase simples por espécie e o fundamento
do ato recolhido —, aponta o próximo passo para a seção aplicável do Edital publicado, mostra o
contato só quando há canal, e troca o rótulo *"Espécie"*. O candidato ganha o pedido de desistência,
cancelável até o desfecho, que não suspende prazo nem envios; a comissão o homologa ao registrar a
desistência expressa pelo comando de sempre. A mensagem da convocação perde *"contado do envio desta
mensagem"*. O aviso do desfecho é uma origem nova da `066`, gravado na transação do desfecho quando
quem registra o pede, e enviado pelo despacho dela — implementado e testado, mas desligado por padrão
e condicionado a `AVISOS_DE_DESFECHO` **e** `AVISOS_AOS_CANDIDATOS`. A validação institucional
continua pendente (PI-1 a PI-6), e nada no código ou nos textos a dá por resolvida.

## Technical Context

- **Linguagem e base**: Python 3.13, Django 5.2, PostgreSQL. Sem dependência nova.
- **Armazenamento**: duas tabelas append-only na app `convocacao` (`0008`); uma coluna e uma origem na
  app `avisos` (`0003`). O `M` do provisionamento vai de 58 a 60 ([data-model](data-model.md)).
- **Testes**: pytest contra PostgreSQL (`make test-pg`, 4 workers, `DB_NAME` próprio); unitários das
  funções puras, integração transacional dos comandos e do despacho, interface do portal e da
  gestão, uma varredura nova (`test_vocabulario_do_desfecho.py`).
- **Restrições**: CSP sem inline (as duas camadas são `<details>` nativo, com regra na folha); regra
  na folha para toda classe nova; sem `raise Http404` novo (recusa de inexistente por `DomainError`);
  sem `select_for_update` em tabela append-only (`guardiao_de_travas`); orçamento de consultas das
  telas do portal (`situacao_da_inscricao` sem consulta; o acompanhamento constante em itens); nada de
  e-mail real.
- **Escala**: os recortes da convocação têm dezenas de pessoas; o pedido, o cartão e o lote leem os
  pedidos em consulta única por recorte.

## Constitution Check

| Princípio | Como a 156 o cumpre | Situação |
|---|---|---|
| Publicação imutável | nenhum ato gravado muda: a frase simples é derivada na leitura (R-001, D-002); o fundamento recolhido é o gravado, palavra por palavra (FR-6401) | ✓ |
| Nada se exclui | pedido e cancelamento são tabelas append-only nas três camadas; o estado é derivado (R-007) | ✓ |
| Negar por padrão, escopo | o pedido exige identidade autenticada e titularidade, e responde inexistente para o resto; a homologação e o aviso passam pelo comando de desfecho (`pode_gerir_comissao`, escopo filtrado) | ✓ |
| LGPD | o pedido não tem motivo nem texto livre (D-007); a trilha não copia endereço; o aviso é neutro, sem espécie, nome, CPF, protocolo nem modalidade (FR-6435); o envio fica desligado até as pendências institucionais (FR-6440) | ✓, com a pendência institucional declarada |
| Auditoria | pedido, cancelamento, desfecho, gravação do aviso e cada resultado de envio entram na trilha | ✓ |
| Regras explícitas | a sexta situação de envio está escrita na FR-084 da `010` (revista) e contada pela guarda; a ciência do pedido é conferida no comando, e não só na tela | ✓ |
| Rastreabilidade | FR-6400 a FR-6445, SC-2120 a SC-2131 e UX-620 a UX-623, nas [tarefas](tasks.md) | ✓ |

Nenhuma violação a justificar.

## Project Structure

### Documentation

```text
specs/156-comunicacao-do-desfecho/
├── spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md
├── contracts/telas-e-comandos.md
└── checklists/requirements.md
```

### Source Code

```text
backend/processo_seletivo/
├── portal/
│   ├── desfecho.py                      # novo: frases, próximo passo, recursos (R-001)
│   ├── situacao.py, obrigacoes.py       # chamam desfecho.py; o porquê em duas camadas; o canal
│   ├── views.py                         # convocação, acompanhamento, desistir, cancelar
│   ├── urls.py
│   ├── templates/portal/
│   │   ├── convocacao.html, _chamada_da_convocacao.html, _obrigacoes_da_convocacao.html,
│   │   │   _convocacao_da_inscricao.html, acompanhamento.html
│   │   ├── _fundamento_do_ato.html      # novo: o <details> das duas camadas
│   │   ├── _atendimento_da_convocacao.html  # novo: o canal, ou nada
│   │   └── desistir.html                # novo: confirmação e cancelamento
│   └── static/portal/portal.css
├── convocacao/
│   ├── models.py, migrations/0008_pedido_de_desistencia.py
│   ├── application/desistencia.py       # novo: pedir, cancelar, pendentes, estado
│   ├── application/desfechar.py         # ciencia_do_pedido, avisar
│   ├── application/fluxo.py, domain/alcance.py   # o lote sem os pedidos pendentes
│   ├── application/comunicar.py         # o canal sem padrão de texto
│   ├── application/selectors.py         # prefetch do atestado
│   └── templates/convocacao/mensagem/*  # o prazo e o atendimento
├── avisos/
│   ├── domain/nomes.py, domain/desfecho.py (novo), models.py, migrations/0003_origem_desfecho.py
│   ├── application/desfechos.py         # novo: gravar, motivo_para_nao_enviar
│   ├── application/comando.py           # envio_do_desfecho_habilitado
│   └── application/despacho.py          # releitura, trilha, chave, REVISAO_DA_FR_084_PELA_156
├── interface/
│   ├── views.py, conducao_da_convocacao.py, andamento.py, encerramento.py, relatorio_do_edital.py
│   └── templates/interface/convocacao.html, _conferir_o_texto.html, aviso.html, avisos_do_edital.html
├── processos/application/pendencias_do_edital.py
├── seguranca/papeis.py
├── treinamento/                          # o canal fictício (R-014)
└── config/settings/base.py, development.py, test.py
```

## Decisões de implementação

Estão em [research.md](research.md) (R-001 a R-016). As que mais pesam:

- **Frases num módulo puro** (R-001) e **duas camadas em `<details>`** (R-002).
- **A seção aplicável vem do plano do documento publicado**, e o caminho é o bloco do documento na
  página pública do Edital, porque nem a página nem o PDF têm âncora por seção (R-003).
- **O pedido é append-only com estado derivado do desfecho** (R-007), travado no Processo e na
  Inscrição, idempotente pelo estado (R-008).
- **A homologação é o comando de desfecho**, com a ciência do pedido conferida nele (R-009).
- **O aviso do desfecho é uma origem da `066`**, gravado na transação do desfecho, relido pelo despacho
  antes de cada tentativa, e atrás das duas chaves (R-011, R-012).

## Dependências e cruzamentos

- **Antes de implementar**: a revisão da spec (PR #488) na `main`. As tarefas são escritas sobre ela.
- **A `152`** (o MVP, história 1, entrou na `main` pelo #489 em 12/11; o resto segue em curso) toca `desfechar.py`,
  `conducao_da_convocacao.py` e o cartão. A ciência do pedido é marca própria, que se soma à dela.
- **A `154`** (#484) e a **`150`** (#483) tocam o portal da convocação: a `154` nas chamadas abertas, a
  `150` no cartão do documento. Esta toca o estado decidido, o fundamento e os rótulos.
- **Antes da validação final**: integrar o que dessas três já estiver na `main` e resolver os
  conflitos preservando os requisitos de cada uma ([R-015](research.md)).

## Pendências que não são deste código

- **PI-1 a PI-6** (spec, *A validação institucional do envio*): condicionam só a ligação de
  `AVISOS_DE_DESFECHO` em produção.
- **SC-2121**: rodada do estudo com pessoas.

## Complexity Tracking

Nenhuma violação da Constituição.
