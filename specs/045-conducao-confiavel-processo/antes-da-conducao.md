# O "antes" da `045` — medido antes de qualquer edição

**Quando**: 26/09/2026, na worktree `conducao-confiavel-processo-a5a78b`, depois de integrar a `main`
(`cfecb0d`, com o #179). Banco próprio (`ps045`), `make preparar` com **34 de 34**, `migrate --check`
limpo.

## A suíte

`make test-pg`: **7837 passando, 11 pulados**, em 13min42s. É o mesmo número que o #179 registrou —
a worktree está em dia com a `main`.

## Os arquivos que a feature reescreve, contados caso a caso

A contagem é de funções `def test_` por arquivo; os parametrizados contam uma vez aqui.

| Arquivo | Casos |
|---|---|
| `tests/integration/supervisao/test_sinais.py` | 31 |
| `tests/interface/test_supervisao.py` | 20 |
| `tests/unit/interface/test_supervisao.py` | 3 |
| `tests/acceptance/test_supervisao_do_processo.py` | 2 |
| `tests/integration/supervisao/test_autorizacao.py` | 8 |
| `tests/integration/supervisao/test_pulso.py` | 11 |
| `tests/interface/test_distribuicao.py` | 15 |
| `tests/interface/test_round_trip_do_rascunho.py` | 12 |
| `tests/integration/editais/test_reaproveitamento.py` | 39 |
| `tests/unit/editais/test_etapas.py` | 17 |
| `tests/integration/supervisao/test_sinal_do_acervo_sem_quadro.py` | 7 |
| `tests/contract/test_edital_draft_api.py` | 23 |
| `tests/unit/editais/test_calendario.py` | 14 |
| `tests/interface/test_hardening_pos_auditoria.py` | 36 |
| `tests/interface/test_compor.py` | 44 |

## A frase de ausência que cada papel lê hoje

Lida do código (`alcance` e `processo_detalhe.html`), e não de percurso — o percurso é o da `T035`.
Num Processo sem condição alguma:

| Leitor | Espécies que alcança | O que lê |
|---|---|---|
| Gestor, ou presidência | todas menos `UX-005`, `UX-064` e `UX-066` | *"Nenhuma condição de atenção neste Processo."* |
| Publicador | só `UX-066` | *"Nenhuma condição de atenção neste Processo."* |
| Julgador | só `UX-005` e `UX-064` | *"Nenhuma condição de atenção neste Processo."* |
| Auditor | só `UX-004` e `UX-065` | *"Nenhuma condição de atenção neste Processo."* |
| quem não alcança espécie nenhuma | — | a região não aparece |

**Todos os quatro papéis ouvem a frase global, e nenhum deles alcança o catálogo inteiro.** É o `RC-78`
medido: a frase afirmava o que nenhum papel sozinho tinha como saber.

---

## Depois — o percurso pela interface (`T035`)

26/09/2026, servidor local sobre um banco de demonstração próprio (`ps_045_demo`, `seed_demo`),
cada papel numa identidade separada pelo seletor. O painel do navegador estava oculto, e as páginas
foram lidas e acionadas pelo próprio formulário de cada tela — a mesma requisição que o clique faz.

**1 — A ausência respeita o alcance.** O Julgador, sem recurso pendente, leu *"Nenhuma condição de
atenção entre as que você acompanha neste Processo."* O Gestor e a presidência viram cinco sinais,
todos com caminho, e nenhum de Cronograma. O Publicador viu o ato por divulgar; o Auditor, a
ocupação por apurar. **Nenhum leitor ouviu a frase global.**

**2 — O recurso aparece desde que chega.** Como a candidata Bruno Costa, pelo portal, com o código
de acesso lido nos logs do servidor, foi interposto `REC-2026-NUX4RA3B` contra a classificação final
do Edital 51/2026. Antes de qualquer ato, o Julgador leu *"Há recurso aguardando admissibilidade no
Edital 51/2026 com membro da comissão desimpedido para decidi-lo. 1 de 1 recurso"*, e o cartão do
Edital, *"Recursos aguardando decisão (1)"*. Admitido pela tela, o **mesmo** sinal passou a dizer
*"aguardando julgamento"*. Julgado (indeferido), a Atenção voltou à frase relativa, e a contagem, a
**0**.

**3 — O Cronograma deixou de produzir alarme.** O seed tem Eventos vencidos no segundo Edital e
Etapas sem Evento nos dois — antes, `UX-002` e `UX-001` na Atenção do gestor. Agora nenhum dos dois.
Os próximos marcos do pulso não dizem *"declarado"*; o período em curso diz *"em andamento"*. A
página do Edital 26/2026 publicado diz, em *Validação do conteúdo*, *"Aviso — A Etapa não está
vinculada a nenhum Evento do Cronograma, em «Etapa 2 — Análise de títulos»"*.

**4 — O sinal que fica diz o que conta e a quem pedir.** As medidas dizem *"7 de 7 inscrições"* e
*"1 de 4 inscrições"*. O Auditor, seguindo o `UX-065` até a ocupação, leu *"Apurar a ocupação deste
marco depende da permissão de gerir a comissão ou da presidência deste Processo — cada uma basta
sozinha. Peça a alguém com a permissão de gerir a comissão ou a quem preside este Processo que a
apure."*; no sorteio, a mesma frase, *"que o conduza"*. A presidência, que apura, não recebeu a
frase.

**Não percorrido pela interface**: o `UX-046` — o seed não publica acervo sem quadro — e a recusa
da fase pela API. Os dois estão presos por teste (`rastreabilidade.md`).

## Depois — os testes alterados (`T036`)

| Arquivo | Antes | Depois |
|---|---|---|
| `tests/integration/supervisao/test_sinais.py` | 31 | 33 — quatro apagados, seis acrescentados |
| `tests/interface/test_supervisao.py` | 20 | 22 — três apagados, cinco acrescentados |
| `tests/unit/interface/test_supervisao.py` | 3 | 3 |
| `tests/acceptance/test_supervisao_do_processo.py` | 2 | 2 |
| `tests/integration/supervisao/test_autorizacao.py` | 8 | 8 |
| `tests/integration/supervisao/test_pulso.py` | 11 | 15 |
| `tests/interface/test_distribuicao.py` | 15 | 16 |
| `tests/interface/test_round_trip_do_rascunho.py` | 12 | 13 |
| `tests/integration/editais/test_reaproveitamento.py` | 39 | 39 |
| `tests/unit/editais/test_etapas.py` | 17 | 17 |
| `tests/integration/supervisao/test_sinal_do_acervo_sem_quadro.py` | 7 | 12 |
| `tests/contract/test_edital_draft_api.py` | 23 | 25 |
| `tests/unit/editais/test_calendario.py` | 14 | 18 |
| `tests/interface/test_hardening_pos_auditoria.py` | 36 | 37 |
| `tests/interface/test_compor.py` | 44 | 46 |
| `tests/unit/editais/test_etapa_sem_evento.py` | — | 4 (novo) |
| `tests/interface/test_ocupacao.py`, `test_console_do_sorteio.py`, `test_marco_removido.py` | — | um cada |
| `tests/integration/resultados/test_progressao_com_corte.py` | — | um |

Caso a caso, com o motivo, em [rastreabilidade.md](rastreabilidade.md), seção 6.
