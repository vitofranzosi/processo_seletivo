# Verificação: Minhas atividades (160)

O que se conferiu na implementação, fora do que a suíte prende. É o registro das medições, dos
desvios das tarefas e do que fica pendente.

## O custo medido (T034, FR-6878, SC-2274)

Medido em 12/11/2026 contra PostgreSQL. A página de quem preside o Edital do cenário, menos a de uma
identidade sem vínculo nenhum, no mesmo banco (R-012):

| Cenário | Sem a versão por requisição | Com ela (R-009) | Teto gravado |
|---|---|---|---|
| sorteio (`certame_s1`), 3 e 30 inscrições | 23 e 23 | 19 e 19 | 23 |
| pontuação (`certame_p1`) | 29 | 27 | 33 |
| convocação (`montar_cenario_da_convocacao`) | 163 | 117 | 141 |

O termo não cresce com as inscrições. A versão vigente por requisição (incremento B, FR-6879) poupa
de 7% a 28%, e mais onde a derivação lê mais listas: a convocação relia a versão em cada leitura de
recorte e em cada prévia.

**O Centro ganhou o mesmo** (SC-2280): o detalhe do Edital abre o contexto, e
`test_andamento_em_escala.py` mediu 44, 56 e 152 consultas (sorteio, pontuação e convocação), contra
46, 57 e 199 antes. O teto da convocação baixou de 240 para 185. As providências são as mesmas com e
sem o contexto: `test_a_versao_por_requisicao_nao_muda_o_que_a_derivacao_diz` compara as duas
leituras, e o teste de coerência compara a página, que abre o contexto, com a página anterior do
Edital, que não abre. A convocação continua o caso caro, no Centro e aqui: cada lista apurada lê o
recorte e as prévias.

O estudo tinha medido, nos cenários de treinamento, cerca de 98 consultas por Edital presidido.
Os cenários da suíte são menores; a diferença é de formato, e não de regra.

**O membro** paga o mesmo com 1 e com 11 comissões, e a derivação não é chamada nenhuma vez
(SC-2272). A página ganhou **uma** consulta fixa, a das alocações à conferência da pessoa (R-002):
o teto de `test_minhas_etapas_nao_custa_pelo_tamanho_da_comissao`, que prende que a página não
cresce com o tamanho da banca, foi de 10 para 11.

## Desvios das tarefas

- **T009 e o agrupamento entre dois Editais pela tela.** Dois cenários no mesmo banco colidem pela
  idempotência da publicação (a memória do projeto e o cabeçalho de `test_andamento_em_escala.py`).
  O agrupamento é prendido pelos testes puros de `test_atividades.py`, com as mesmas providências
  que a derivação emite; a junção nos cenários de treinamento, com vários Editais da mesma
  presidência, fica para a verificação no quickstart.
- **T021 e as esperas iguais em dois Editais**: pela mesma razão, prendidas no teste puro
  `test_as_esperas_juntam_pela_razao_inteira_com_a_data`.
- **T002 e T036, as capturas**: feitas pela sessão que pediu a implementação, para mostrar ao
  usuário.
- **O incremento B no mesmo PR.** As tarefas o punham num PR próprio, depois do A na `main`. Ele é
  pequeno (um contexto em `publicacoes/application/selectors.py` e duas views que o abrem), foi
  medido junto, e vai num commit próprio, para ser revisto ou revertido à parte.
- **A memória da versão é por `edital_id` e pelo instante da requisição.** `do_edital` passou a ler
  com o instante do contexto quando há um (`agora_da_requisicao`), para que as funções de outras
  features que recebem o `at` dela encontrem a versão já lida. Uma chamada com outro `at` vai ao
  banco. Cada chamada recebe uma cópia do conteúdo, para que quem o altera em memória não contamine
  a seguinte.

## Documentos (FR-6853)

- `doc/cenarios-de-treinamento/guia-da-equipe.md`: a presidência começa em "Minhas atividades", e
  não precisa abrir Edital por Edital.
- `doc/manual/00-arquitetura-do-manual.md`: o fluxo da avaliação, o cabeçalho, os assuntos, as telas
  e a captura SS-050. Os achados antigos (E2E15-016 e a nota de 28/09) ficam como estão: são
  registro.

## Pendências

- **SC-2281** é humano: a tarefa "sem abrir nenhum Edital, diga o que você tem a fazer e faça o
  primeiro", com a comissão real.
- **UX-714** (375 px) é conferida pelas capturas da sessão que pediu a implementação.
