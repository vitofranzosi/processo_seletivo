# Verificação: Minhas atividades (160)

O que se conferiu na implementação, fora do que a suíte prende. É o registro das medições, dos
desvios das tarefas e do que fica pendente.

## O custo medido (T034, FR-6878, SC-2274)

Medido em 12/11/2026 contra PostgreSQL. A página de quem preside o Edital do cenário, menos a de uma
identidade sem vínculo nenhum, no mesmo banco (R-012):

| Cenário | Sem a versão por requisição | Com ela (R-009) | Teto gravado |
|---|---|---|---|
| sorteio (`certame_s1`), 3 e 30 inscrições | 23 e 23 | 20 e 20 | 23 |
| pontuação (`certame_p1`) | 29 | 28 | 33 |
| convocação (`montar_cenario_da_convocacao`) | 163 | 118 | 141 |

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
- **A memória da versão vale entre a abertura da requisição e a próxima vigência do Edital**
  (revisão de código do #511). A primeira versão congelava o instante da requisição em `do_edital`;
  agora cada leitura usa o seu `now()`, e a memória custa uma consulta a mais por Edital — os
  números da tabela acima já a incluem (eram 19, 27 e 117). Antes da abertura vai ao banco. Cada
  chamada recebe uma cópia do conteúdo, para que quem o altera em memória não contamine a seguinte.

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

## A revisão visual de 12/11 (cenários de treinamento, banco `ps_minhas_atividades`)

O usuário pediu quatro correções no PR ("Sim, corrigir no #511"):

1. **A espera não tem marca de base.** Como `treino.presidencia`, "Publicar o resultado definitivo"
   (do Publicador) e "Resposta de 3 convocações" (do candidato) apareciam com "Presidência". A
   espera não é ato de ninguém agora; a marca de base fica só onde a pessoa pratica (FR-6861). Preso
   em `test_a_espera_fica_recolhida_com_a_origem_da_data_e_sem_atraso`.
2. **O prazo da convocação diz de quem é.** A derivação dizia "o prazo corre até …", que se lia
   como prazo da comissão; passou a dizer "o prazo do candidato corre até …" (e "o prazo do
   candidato está correndo", sem data). A mudança é na `127`, e vale também no Centro (FR-6869).
3. **As Etapas concluídas ou sem inscrição ficam recolhidas.** Com 27 Etapas, quase todas
   "Concluída 100%", a página do avaliador passava de 4500 px. As com avaliação pendente ficam
   abertas; as demais, em `details`, com a contagem. Sem script.
4. **Menos ruído.** Em "Para fazer agora", a situação só aparece quando não é *Pendente*, e a lista
   perdeu o fundo de destaque. Na Lista, a nota da faixa ficou mais curta: `FORA_DA_FAIXA` é uma
   frase só, que nomeia as oito famílias da FR-4324 da `129`, diz que ficam no detalhe de cada
   Edital e termina no link "Minhas atividades".

Na segunda passada ("Sim, enxugar"), a constante deixou de repetir o que a faixa reúne: a frase
vazia já o diz, e a nota com itens volta a dizê-lo na frase dela, como antes da `160`. A enumeração
aparecia duas vezes no estado vazio, que ocupava cinco linhas a 1280 px.

Depois das correções: `make lint` e `make check` passam; `tests/interface`, `tests/unit/interface`,
os testes de desempenho da página, do Centro, da faixa, da Lista e da comissão, e os guardiões de
citação e do README deram 6288 passados e 1 pulado, contra PostgreSQL.

## A revisão de UX de 12/11 (FR-6885 a FR-6888)

O usuário trouxe dois feedbacks de UX e pediu as melhorias julgadas certas; a sessão que pediu a
implementação os avaliou. Entraram:
- a marca de base só quando distingue, e no título quando a base é uma só (D-012);
- o filtro por Edital, em formulário GET, sem script e sem recusa para valor que não serve (D-011),
  no lugar de agrupar por Edital, que desfaria o mesmo ato entre Editais;
- a nota de cobertura numa frase, com "Onde encontro as outras operações?" recolhido;
- a avaliação sem atribuição numa linha, sem o quadro de estado vazio;
- as comissões recolhidas, abertas só quando são o único conteúdo, com os caminhos da presidência
  como links de texto.

Ficaram fora, por decisão da avaliação: priorização ou ordem nova, que não tem prioridade de negócio
validada; designação; e mudança na derivação.

## A revisão de código do #511 (12/11)

Oito achados, todos tratados:
- **Instante congelado** e **falta de versão sem memória**: corrigidos no contexto da versão vigente
  (R-009, revisto).
- **Ordem dos Editais pelo número em texto** (10/2026 antes do 9/2026): a ordem é natural, por
  `ordem_do_edital`, nas linhas, no filtro e na leitura.
- **As alocações da pessoa relidas por Edital presidido**: a `104` é lida uma vez para todos os
  Editais da página, e entregue a cada `do_edital` (`trabalho=`), como o estudo propunha (R3).
- **Os grupos recalculavam as mesmas propriedades a cada acesso do modelo**: `cached_property`.
- **Nenhum teste de página da espera da convocação**: entrou
  `test_a_espera_da_convocacao_nao_tem_base_e_o_prazo_e_do_candidato`.
- **A cópia do conteúdo a cada leitura memorizada**: medida e mantida. Num conteúdo de 10 KB dos
  cenários de treinamento, a cópia custa 0,075 ms, e a consulta que ela poupa, 0,85 ms; sem a
  cópia, quem altera o conteúdo em memória contaminaria a leitura seguinte.
- **Os Editais encerrados lidos a cada abertura**: mantidos. Um Edital encerrado pode ter pendência
  (o relatório do Edital diz "encerrado com pendências"), e nenhum comando da comissão recusa ato por
  o Edital estar encerrado; tirá-los da leitura poderia esconder um ato que o Centro diz ser da
  pessoa, contra a FR-6860.

