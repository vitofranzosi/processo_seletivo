# Quickstart: A correção da convocação pela gestão

Roteiro para demonstrar a feature **depois de implementada**: a comissão pela gestão e o convocado
pelo portal, sem banco nem shell para **agir** (Constituição, VI). Os dados são fictícios. Os campos,
as recusas e as respostas estão em [data-model.md](data-model.md) e no
[contrato](contracts/correcao-da-convocacao.md).

## Preparação

- Ambiente local pelo `make preparar`, com `INTERFACE_SELETOR_IDENTIDADE=true` — sem ele `/gestao/`
  devolve 503.
- Um `DB_NAME` próprio da worktree, para a suíte e para o servidor.
- O código de acesso do portal sai no terminal do servidor, ou em <http://localhost:8025> no compose.
- **O estado inicial se monta pelos cenários da `118`** (`tests/fixtures/jornada_do_convocado.py`),
  como o teste no navegador faz: o cenário G é *um documento pendente, o prazo vencido sem desfecho,
  o Requerimento nunca enviado*. Para percorrer à mão, monta-se o mesmo pela gestão, pelo caminho da
  `115`: Edital com documentos e o Requerimento *na convocação*, inscrição, classificação, convocação
  com um vencimento de poucos minutos, conferência de um documento como pendente, e a espera do
  vencimento.

## A jornada principal (US1, US2)

| Passo | Quem, onde | O que fazer | O que ver |
|---|---|---|---|
| 1 | convocado, portal, 375 px | abrir a convocação | *"O prazo terminou"*; o reenvio e o Requerimento recusados com a mesma frase |
| 2 | presidência, gestão | abrir a condução do recorte | o cartão em *"Vencimento decorrido"*, com *"Corrigir esta convocação"* ao lado de *"Registrar desfecho"* |
| 3 | presidência | abrir a ação | a pessoa e a chamada; o vencimento atual; a espécie e o fundamento, com a origem; a forma de comunicação e o que ela fará; *"o que reabre"*; o que não muda; o parágrafo de irreversibilidade |
| 4 | presidência | informar um vencimento **posterior** ao atual | a linha do efeito: *"O prazo é estendido até …"* |
| 5 | presidência | trocar por um vencimento **anterior** ao atual, ainda futuro, e depois **igual** | *"antecipado … encurta um prazo já comunicado"*; *"mantido"* |
| 6 | presidência | voltar ao posterior, escrever o motivo, confirmar | *"Convocação de ‹protocolo› corrigida. O vencimento passou de … para …: o prazo foi estendido."* e o resultado da comunicação |
| 7 | presidência | ler o cartão | *"Prazo em curso"* (ou *"Sem comunicação enviada"*), o vencimento novo, *"Corrigida em … — ver o histórico"* |
| 8 | convocado, portal | recarregar a convocação | o prazo novo, no formato único da `118`; a recusa por prazo sumiu |
| 9 | convocado | complementar o documento pendente | aceito; a conferência anterior continua legível |
| 10 | convocado | preencher e enviar o Requerimento | aceito |
| 11 | presidência | abrir os documentos da convocação e o histórico | a complementação aguardando conferência; no histórico, a corrigida sucedida com o motivo e a sucessora vigente |

## As recusas (US3, US4)

| Situação | Como provocar | O que ver |
|---|---|---|
| motivo vazio | confirmar sem motivo | a recusa junto do motivo; vencimento e complemento preenchidos |
| vencimento ausente | confirmar sem vencimento nem Evento | a recusa junto do vencimento; o motivo preenchido |
| vencimento passado | informar um instante já passado | a recusa da FR-269b da `019`; o motivo preenchido |
| apuração superada | registrar um desfecho noutro cartão do mesmo recorte, sem a apuração seguinte | em todos os cartões em aberto, *"A correção está impedida: …"* e *"Emitir a apuração seguinte"*; nenhum formulário |
| prévia superada | abrir a ação; noutra aba, emitir a apuração seguinte; voltar e confirmar | a recusa *"A prévia mudou…"*, a prévia nova e os campos preenchidos |
| corrigida no intervalo | abrir a ação em duas abas; confirmar na primeira, depois na segunda | na segunda, a recusa com quem e quando, o motivo citado para copiar, e o formulário da sucessora vazio |
| desfecho no intervalo | abrir a ação; noutra aba, registrar o desfecho; confirmar | a recusa com o desfecho; o motivo citado; nenhuma chamada nova |
| duplo clique | confirmar com dois cliques rápidos | uma sucessora; uma mensagem, ou um *"aguardando publicação"*, ou uma falha — nunca duas mensagens |
| sem autorização | entrar como membro alocado à conferência | o cartão sem a ação; o POST montado à mão recebe 403 |
| outra unidade | o POST com um Edital de outra unidade | 404 |
| chamada sem vencimento | um Edital que não publica prazo | o cartão sem a ação |

## Pela suíte

```bash
cd backend && make lint check test-pg
```

A jornada no navegador pede o grupo `navegador` (`uv sync --extra dev --extra navegador` e
`uv run playwright install chromium`); sem ele, o arquivo pula inteiro. Para assistir:

```bash
cd backend && make test-navegador
```

## Critério de conclusão

A feature só se declara concluída com a **jornada principal demonstrada** do passo 1 ao 11. Se um
defeito do portal a impedir, ele é registrado em `doc/`, e a conclusão fica bloqueada até a decisão
do usuário (FR-3854).
