# Verificação: 143

Banco descartável `ps143` (migrado, Unidade semeada, autoridade da suíte, os quinze cenários da
`134`, rodada 1), servidor na entrada `convocacao-143` do `.claude/launch.json` (porta 8143). Os
passeios são do Playwright, por `passeio/passeio.py` (o do estudo de continuidade, com o passo
`buscar` para abrir o arquivo sem navegar). Capturas em `capturas/`: `antes-*` sobre a `main` em
`daba322f`, `depois-*` sobre esta branch, no mesmo banco.

**A proposta visual é a própria tela.** Em vez de um protótipo à parte, o desenho foi feito sobre o
HTML real e comparado com as capturas do antes; as decisões que ele pediu estão na spec (D-001 a
D-007).

## Antes e depois, a 1440 × 900

| Medida | Antes | Depois |
|---|---|---|
| C12 — onde o operador descobre o que há a fazer | as pastilhas das chamadas, a y≈1.900 | o índice "Neste recorte, agora", a y=430, inteiro na primeira tela (UX-370, SC-1560) |
| C12 — título "Chamadas praticadas" | y=1.873 | y=1.358; e cada pergunta do índice leva à **chamada** certa, e não ao título |
| C12 — o formulário do desfecho de quem está pronto | y≈3.020, recolhido, no topo da convocação | um clique a partir dos documentos: `select` a y=557 da dobra, já aberto (SC-1561) |
| C12 — altura da página | 3.549 px | 3.930 px — o índice, o passo e o aviso de cada cartão acrescentam ~380 px; o que está longe é alcançável pelo índice |
| C10 — "3 Ocupadas · 0 A ocupar · 0 Convocadas" | três ladrilhos iguais, sem dizer de onde vêm | "Pela apuração da ocupação — calculado" (tracejado) × "Pelas chamadas praticadas" (contínuo), e a frase que separa as três leituras |
| C11 — a pendência do 02 | "Documentos com pendência — 1 pendente"; o aviso, noutra seção | "Pendência registrada em … Nenhum aviso desde esta pendência … O aviso pode ser pedido agora", com o link, no cartão dele |
| Documentos da convocação | pessoa e vencimento; Edital, Perfil e lista só na migalha; a volta ia ao topo | contexto completo, situação, resumo, "Pessoa 2 de 3", anterior, seguinte, próxima a conferir, e o desfecho no cartão |

## Os doze cenários pedidos

| # | Cenário | Onde | Resultado | Captura |
|---|---|---|---|---|
| 1 | Vagas antes da convocação | C10, ampla | 3 publicadas, 3 efetivas, **3 consideradas ocupadas na apuração**, 0 a ocupar; **0 pessoas convocadas** em grupo à parte | `depois-01-c10-*` |
| 2 | Titulares prontos | C10, ampla | "3 titulares a convocar" → `#titulares` (o gesto da `140`) | `depois-01-c10-dobra` |
| 3 | Conferência prévia em lote (`140`) | C10 | "Conferir e convocar as 3" abriu a conferência da `140`, sem ato; confirmada, "3 convocações praticadas" | `depois-03-c10-conferencia-da-140` |
| 4 | Convocações aguardando resposta | C10 depois | "3 aguardando resposta … o primeiro vence em 20/11/2026 18:00"; cada cartão "Aguardando o candidato enviar 2 documentos" | `depois-04-c10-*` |
| 5 | Documentos recebidos e pendentes | C11, C12 | índice "1 com documento a conferir", "1 com pendência", "1 aguardando o envio"; cada um leva ao cartão | `depois-05-*` |
| 6 | Pendência que exige aviso | C12, 2ª pessoa | três momentos: "Nenhum aviso desde esta pendência … pode ser pedido agora" → gesto → "registrado … ainda não foi enviado" → `despachar_avisos` → "aceito pelo servidor de correio em …" | `depois-06-c12-*` |
| 7 | Documento reenviado | C11, 02 (reenvio pela função da `115`, como o portal faz) | "Conferir de novo: o candidato reenviou 1 documento que estava pendente"; o aviso não é oferecido | `depois-07-c11-documento-reenviado` |
| 8 | Pronta para desfecho | C12, 1ª pessoa | dois "conforme" pela página → "Pronta para o desfecho" → "Registrar o desfecho desta convocação" → cartão com o formulário aberto, a y=557 | `depois-08-c12-*` |
| 9 | Desfecho registrado | C12, 1ª pessoa | aceite pela conferência do texto da `125`; "Desfecho registrado. A apuração seguinte … 0 a ocupar"; o índice: "1 com desfecho registrado — 1 apta para formalização" | `depois-09-c12-*` |
| 10 | Fila de suplentes | C11 | a fila na área "Fila, suplentes e regularização", depois das chamadas, com o formulário de sempre e a explicação da sucessão | `depois-10-c11-convocacao-com-fila` |
| 11 | Ninguém mais elegível | C15, depois de convocar as 2 | "Não há mais quem chamar dentro da faixa que o corte alcançou", com a explicação do corte e o caminho da ocupação | `depois-11-c15-ninguem-mais-elegivel` |
| 12 | Operador sem permissão | C11, `auditor` | lê o índice, as vagas e os cartões; nenhum formulário, nenhuma linha marcada como trabalho, nenhum "Conferir os documentos" | `depois-12-c11-auditoria-sem-acao` |

**Mais de uma lista em estados diferentes:** no C10, a ampla estava apurada com 3 titulares a
convocar, e a PPP sem apuração — o índice dela diz "a ocupação dele ainda não foi apurada", e a área
"Convocar" diz por que não há gesto (`depois-02-c10-ppp-outra-lista`).

## A 375 px

Convocação no C10, C11, C12 e C15 e documentos no C11 e C12: sem rolagem horizontal
(`scrollWidth = 375`). A primeira medida achou o link "Próxima com documento a conferir" da página
dos documentos estourando a 433 px — `.acao` não quebra linha —, corrigido na folha.

## CSP

`csp=0` em todos os passos dos passeios: nenhum estilo nem script no template.

## Suíte

`make lint check test-pg DB_NAME=ps143t` (4 workers, com os grupos `assistente` e `navegador`):
**17.868 passando, 12 pulados e 3 falhas**, em 1.505 s. As três eram guardiões que pediam registro, e
não defeito:

- `test_telas_de_resultado_e_atos.py` (dois casos): a lista de botões da convocação, na ordem do
  código. A primeira versão tirara o formulário da emissão para um parcial, e o guardião deixou de
  vê-lo; ele voltou ao template, na linha das exceções, e a lista registra a ordem nova das áreas —
  nenhum rótulo nem desenho mudou.
- `test_readme_acompanha_o_codigo.py`: a linha da `143` na tabela de incrementos.

Corrigidas as três, a pasta `tests/interface` inteira, os avisos, as jornadas de navegador da
convocação, os guardiões de citação, vocabulário e README e os testes desta spec: **5.251 passando,
1 pulado**, sem falha (250 s).

## Revisão do #453 (10/11)

Oito achados da revisão, corrigidos sem mudar regra das `115`, `117`, `118` e `140`, e sem estado
persistido:

| # | Achado | Correção | Regressão |
|---|---|---|---|
| 1 | aviso oferecido com o envio desabilitado | `oferece_o_aviso` e o detalhe do índice exigem o envio habilitado | `unit::test_com_envio_desabilitado_o_aviso_nao_e_oferecido_nem_contado`, `t::test_c11` |
| 2 | "titulares a convocar" com o gesto impedido | sem trabalho nem âncora; o índice diz o impedimento | `unit::test_titulares_com_o_gesto_impedido_nao_sao_trabalho_e_o_indice_diz_o_impedimento`, `t::test_c10` (PPP) |
| 3 | "Nenhum ato a praticar" com ato pendente | a frase vale só sem ato para ninguém; quem não convoca lê "titulares a convocar, por quem conduz a convocação"; o aviso alcançável conta | `unit::test_quem_nao_convoca_le_que_ha_titulares_por_outro_papel`, `unit::test_o_aviso_alcancavel_e_ato_a_praticar`, `t::test_c10` (auditoria) |
| 4 | link dos documentos para quem não confere (A-2) | sob `confere`; o rótulo e as contagens ficam | `t::test_c11` (auditoria) |
| 5 | tentativas de envio sem ordem | `Prefetch` ordenado pelo número, como o seletor da `066`; a raiz por `raizes_das` | `t::test_c11` (tentativas gravadas fora de ordem — falha sem o `order_by`, conferido) |
| 6 | "com pendência" e "pode ser avisada" em conjuntos diferentes | os dois contam a chamada com documento pendente, a que o gesto da `134` seleciona | `unit::test_pendencia_e_aviso_contam_o_mesmo_conjunto` |
| 7 | rótulo do canal escrito à mão | `linha.canal.pastilha_sem_comunicacao` (a FR-4000 da `125`) | — |
| 8 | leituras repetidas nos documentos | a leitura e a identidade vêm das vizinhas; `pendencias_a_avisar` saiu do contexto | — |

`make lint check` limpo; `tests/interface`, `tests/unit/interface`, `tests/integration/avisos`,
`tests/integration/convocacao`, os testes desta spec e da `139`, os de desempenho da condução, as
jornadas de navegador da convocação e os guardiões: **6.196 passando, 1 pulado**, sem falha (356 s).
A suíte inteira sobre a integração dos três PRs fica com a revisão.
