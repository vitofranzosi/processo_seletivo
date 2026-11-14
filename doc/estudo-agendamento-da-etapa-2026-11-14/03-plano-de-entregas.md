# 3. Plano de entregas

*Proposta [P]. Cada entrega fecha com uma jornada demonstrável pela interface do ator (Constituição,
VI), e não só com domínio. A complexidade é relativa: P, M ou G.*

## Marco 0 — a experiência aprovada, antes de qualquer código

O protótipo (`prototipo/`) é percorrido pela comissão com um caso real. O critério de saída é a
pergunta do pedido: **"consigo sair de uma lista de 43 pessoas para uma agenda conferida e publicada
sem abrir uma planilha?"**, mais a confirmação da Q-1 do README (Q-2, Q-3 e Q-5 já decididas). Ajustes de tela entram aqui, e
custam um arquivo de HTML.

## As entregas

Uma spec (`specs/166-agendamento-da-etapa/`), três PRs, como a `110` (A, B, C). Cada PR cabe numa
sessão.

| # | Entrega | O que o ator consegue ao fim | Complexidade | Depende de |
|---|---|---|---|---|
| **A** | Configurar e montar | A comissão configura, vê a capacidade, preenche com prévia e ajusta à mão, sem publicar | **G** | Marco 0 |
| **B** | Conferir, publicar e mostrar | Publica com conferência e autoridade; página pública e área do candidato mostram o horário | **G** | A |
| **C** | Avisar e remarcar | Avisos por pessoa, reenvio das falhas; remarcação, inclusão e cancelamento individuais | **M** | B; o texto revisto da FR-084 (decidido, `D-010` da spec) |
| D | Orientação | "Montar a agenda" e "Publicar a agenda" como pendência no Centro (`136`) e em Minhas atividades (`160`); horário na tela da Ocorrência | **P** | B |

**A** concentra o modelo (três tabelas operacionais), a derivação dos horários, as recusas da
configuração e a montagem com as duas unicidades. **B** traz as duas append-only, a página pública
e o degrau novo do acompanhamento. **C** é sobretudo reuso: origem nova na `066` e o ato individual
sobre as tabelas da B.

A heteroidentificação (cenário B) **não é entrega**: com a `163` mergeada, ela usa a agenda sem
nada a mais, salvo a identificação pública só por protocolo (R-25), que está na B.

## Riscos já visíveis no código

| Risco | Onde | Mitigação |
|---|---|---|
| A participação muda depois da publicação | `prontidao.py`, projeção | R-13 impede publicar divergente; a tela publicada mostra quem entrou e quem saiu (R-21, R-22) |
| Fuso | Constituição II: zona institucional | horário gravado como instante com `America/Sao_Paulo`; a derivação usa a data local da janela |
| Evento retificado depois da configuração | `EventoCronograma` retificável | a conferência relê o Evento vigente (R-13); dia fora vira impedimento |
| Novas tabelas append-only mudam o `M` do provisionamento | `CLAUDE.md`, "N de M" | atualizar o CLAUDE.md e os testes de `TABELAS_APPEND_ONLY` na B |
| Guardião da FR-084 | `tests/test_situacoes_de_mensagem.py` | origem nova pelo app de avisos, que já está na lista; revisar o texto da FR-084 na C |
| Varredura de vocabulário com lista literal | memória do projeto | acrescentar as telas novas à lista na A e na B |
| `FOR UPDATE` em append-only | role de runtime sem `UPDATE` | travar `AgendaDaEtapa` (operacional), nunca o ato |
| Inventário de negativas cobra 404 novo | `033` | cada `raise Http404` novo ganha linha no inventário |
| CSP | `shared/politica_de_conteudo.py` | nenhum estilo ou script em linha; grade por servidor e htmx, como as telas de composição |
| Grade grande | 3 dias × 2 bancas × 32 = 192 células | uma aba por dia; consulta da agenda inteira em duas leituras (agendamentos, participação) |

## Testes que cada entrega deve trazer

- **Domínio**: derivação dos horários (janelas, sobras, bancas), as recusas da R-05, a ordem da
  R-09 com empate, a prévia que recusa versão velha.
- **Persistência e concorrência** (PostgreSQL): as duas unicidades sob duas transações; append-only
  das tabelas da B; idempotência da publicação.
- **Autorização**: só quem pode gerir a Etapa configura, monta e publica; 404 fora do escopo.
- **Interface**: as telas sob a CSP; a grade no estreito; os estados vazios; o caminho do
  impedimento até a correção.
- **Ponta a ponta**: o cenário A inteiro pela interface, e a remarcação com um aviso só.
