# Research: Prévia interativa da classificação — fatia 2

Questões técnicas da implementação. As decisões de produto estão na [spec](spec.md), em D-001 a D-008,
e as pendentes do usuário em DP-1 e DP-2; aqui ficam as questões técnicas, em `R-`, e a conferência de
código que as sustenta. Tudo conferido em 20/10/2026 contra a `main` em `e7e22b89`, que já tem o motor
compartilhado da `094` (`universo_classificavel.preparar` com recorte, #317).

## R-001 — O que o motor faz com recortes, medido

**Pergunta**: o que a prévia de um Perfil com reserva mostraria, se calculada pelo motor oficial?

**Como**: [`prototipo/reproducao.py`](prototipo/reproducao.py) monta populações fictícias com
Modalidade e as passa pelas funções do produto — `preparar` com recorte, `ordenar`, `faixa.calcular`,
`apuracao.apurar`, `titulares_iniciais`, `ocupantes`, `quantidade_a_reverter`. As duas decisões que o
caminho oficial toma em funções que leem banco (R-003) estão esboçadas no roteiro, marcadas como tal.
Hipóteses da rodada: todos os que avançaram habilitados; nenhum movimento nem efeito anterior.

**Perfil de referência**: 10 vagas na linha geral, 3 na PPI, 2 na PcD; 20 candidatos com notas
distintas; PPI nas posições 3, 8, 15 e 16 da ampla; PcD na 5 e na 18. Na coluna da direita, a faixa e
as quatro quantidades na ordem publicadas/efetivas/ocupadas/faltando.

| Cenário | Recorte | Universo | Resultado |
|---|---|---|---|
| Alvo do quadro, sem suplentes, qualquer espécie | ampla | 20 | faixa 10; 10/10/10/0 |
| | PPI | 4 | faixa 3, das quais 2 posições de quem ocupa pela ampla, 1 autodeclarado além; 3/3/1/2 |
| | PcD | 2 | faixa 2, 1 de quem ocupa pela ampla; 2/2/1/1 |
| … reversão ausente | PPI e PcD | | cederiam 0 |
| … *"A quantidade que ficou sem preencher"* (saldo) | PPI e PcD | | cederiam 2 e 1; a próxima apuração da ampla leria 13 |
| … *"Só quando a lista reservada esgota"* (esgotamento) | PPI e PcD | | há quem ocupar: sim; cederiam 0 |
| Alvo fixo 10, saldo | PPI | 4 | faixa 4 — o alvo fixo vale na PPI —; 3/3/2/1; cederia 1 |
| | PcD | 2 | faixa 2 (todos); 2/2/1/1; cederia 1 |
| PcD toda nas vagas da ampla, esgotamento | PcD | 2 | faixa 2, as 2 de quem ocupa pela ampla; 2/2/0/2; há quem ocupar: **sim**; cederia 0 |
| PPI na 12ª, alvo do quadro, 5 suplentes | ampla | 20 | faixa 15; 10/10/10/0 — o 12º está na faixa e **não** ocupa |
| | PPI | 4 | faixa 4 (3 + 5 suplentes, limitada aos 4); 3/3/3/0 |
| Empate de dois na 10ª da ampla, 5 suplentes | ampla | 20 | apuração pararia na 10ª |
| | PPI e PcD | | não avaliadas: dependem de quem ocupa pela ampla |
| Empate de dois na 3ª da PPI, nenhum PPI nas vagas da ampla | PPI | 4 | apuração pararia na 3ª |
| | ampla e PcD | | avaliadas normalmente |
| PcD sem autodeclarados, esgotamento | PcD | 0 | ordem vazia; 2/2/0/2; há quem ocupar: não; cederia 2 |

**Participantes da Etapa seguinte**, a união por pessoa das faixas: 12 no primeiro cenário, contra 10
só pela ampla; 13 com alvo fixo 10; 17 com 5 suplentes, contra 15.

**O que a medição estabelece para a spec**:

1. A faixa da reservada é calculada sobre a ordem inteira dela, e a concomitância só age depois, na
   apuração — daí as vagas sem ocupante com autodeclarado além da faixa (DP-1).
2. A reversão por saldo cede essas vagas na mesma apuração que as encontra (DP-1).
3. Sob esgotamento, "há quem ocupar" conta quem ocupa pela ampla (DP-2).
4. O alvo fixo e os suplentes são números da regra do marco, e não do recorte: `corte._alvo` só lê a
   linha do recorte com alvo do quadro, e `surplusCount` vale para todos.
5. O empate na fronteira das vagas da ampla impede a apuração das reservadas, porque os ocupantes da
   ampla são calculados por `titulares_iniciais` com os empates residuais da ampla.

## R-002 — Achados fora do escopo, registrados

Conferidos por leitura em 20/10. O primeiro foi **reproduzido** depois, no banco, pela equivalência da
T011 (`test_empate_na_ultima_vaga_da_ampla`, que prende a recusa crua como ela é); o segundo, só por
leitura e pela linha de base da T003. Não mudam o que a prévia
mostra sob as hipóteses dela, e por isso ficam registrados, e não são escopo (D-005 manda preservá-los
na extração).

| Achado | Onde | O que acontece |
|---|---|---|
| A recusa da fronteira da ampla escapa crua na apuração da reservada | `ocupacao/application/emissao.py::_apurar` | `selectors.ocupantes_da_ampla` é chamado **antes** do `try` que traduz `EmpateNaFronteiraDoAlvo` em `DomainError`. Com empate não julgado na última vaga da ampla, apurar uma reservada levanta a exceção de domínio sem tradução — o padrão que a `014` corrigiu no corte (E2E14-003). O mesmo vale para a chamada em `convocacao/application/selectors.py` |
| Quem ocupa pela ampla não filtra habilitação | `ocupacao/application/selectors.py::ocupantes_da_ampla` | `calculo.ocupantes(titulares=…, efeitos_lidos=…)` sem `habilitadas`: o titular da ampla eliminado na Etapa governada é excluído da reservada, embora a apuração da ampla não o conte como ocupante — ela filtra. A docstring diz "quem **ocupa vaga** pela ampla" |

A prévia supõe todos habilitados e não emite ato, de modo que nenhum dos dois altera um número dela.

## R-003 — A extração das duas decisões (D-005)

**Conferido**:

| Função de hoje | O que consulta | O que decide |
|---|---|---|
| `ocupacao/application/selectors.py::ocupantes_da_ampla(edital, perfil_id, marco_id, versao)` | `progrediram_em_ordem` (ordem, corte, empates), `habilitadas_pelo_corte`, `linha_do_quadro`, movimentos e efeitos da ampla | efetivas da ampla (`publicadas + recebidas − cedidas`) e `ocupantes(titulares_iniciais(...), efeitos)` |
| `ocupacao/application/movimento.py::ha_quem_ocupar(edital, marco_id, lista_id, ja_ocupadas)` | `ato_vigente` e as posições dele | `com_posicao > ja_ocupadas` |

**Decisão**: duas funções puras no domínio da ocupação.

- `apuracao.ocupantes_pela_ampla(*, progrediram_em_ordem, publicadas, movimentos_lidos, efeitos_lidos,
  empates_residuais, habilitadas)` — a conta das efetivas e a chamada a `titulares_iniciais` e
  `ocupantes`, exatamente como hoje: `habilitadas` vai a `titulares_iniciais` e **não** a `ocupantes`
  (R-002). `selectors.ocupantes_da_ampla` passa a consultar e chamá-la.
- `reversao.ha_quem_ocupar(*, posicoes, ja_ocupadas)` — `sum(1 for p in posicoes if p is not None) >
  ja_ocupadas`. `movimento.ha_quem_ocupar` passa a ler as posições e chamá-la.

A soma das efetivas, que hoje se repete em `ocupantes_da_ampla` e em `apuracao.apurar`, **não** é
unificada nesta feature: seria mudança de código sem efeito na prévia, e cada mudança no caminho
oficial é risco que a equivalência precisa cobrir.

**Alternativa descartada**: a prévia reimplementar as duas contas. É o defeito que a decisão 004 da
`094` existe para impedir — e aqui ele seria pior, porque uma das contas carrega um achado (R-002) que
uma reimplementação "corrigiria" em silêncio, e a prévia passaria a mostrar o que o motor não faz.

## R-004 — A rodada da prévia, passo a passo (D-002)

`application/previa.simular` (da `094`) ganha, depois da ordem e do corte de cada recorte:

1. `recortes = recortes_do_perfil(snapshot, perfil_id=…)` — a derivação única (`FR-491` da `034`).
2. Para cada recorte: `preparar(..., recorte=lista)`, `ordenar_com_trajetoria`, `faixa.calcular` com
   o alvo de `faixa.alvo_apurado` sobre a linha de `linha_do_quadro(snapshot, perfil_id, lista_id)`.
3. Ampla: `apuracao.apurar(publicadas=linha geral, progrediram_em_ordem=faixa, habilitadas=faixa,
   empates_residuais=…)`; depois `ocupantes_pela_ampla(...)` com as mesmas entradas.
4. Cada reservada: `apuracao.apurar(..., ocupantes_da_ampla=…)`, `reversao.ha_quem_ocupar(posições da
   ordem do recorte, ocupadas)`, `reversao.quantidade_a_reverter(especie=reversao.declarada(perfil),
   ...)`.
5. Resumo: soma do cedido e `publicadas da ampla + cedido` como "efetivas que a próxima apuração da
   ampla leria".

**Dependência**: a ampla parada (empate na fronteira, ou corte impedido) deixa as reservadas não
avaliadas no passo 4, com o motivo — e nunca com zero.

**`linha_do_quadro`** está em `classificacao/application/corte.py`, que importa modelos no topo do
módulo. A prévia é aplicação e pode importá-la; o protótipo não a importa, e lê as vagas de um
dicionário — por isso a tarefa de equivalência cobre a Modalidade apontada como ampla, que é o caso
que só aquela função resolve.

## R-005 — A população estável com Modalidades (D-003)

A população estável da `094` (`cenarios_da_previa.populacao_estavel`) planta empates nas fronteiras
da ampla. A fatia 2 acrescenta um passo **depois** dela, que só atribui Modalidade, sem mudar nota:

- para cada reservada, na ordem declarada: um candidato entre as vagas da ampla; um entre o fim das
  vagas e o fim da faixa da ampla, quando a faixa passa das vagas; e candidatos abaixo da faixa da
  ampla até preencher a faixa da reservada mais um;
- os candidatos já usados por uma reservada não são reusados por outra (FR-2333), e os plantados da
  fatia 1 — o trio dos fatos, a candidata sem nota, o eliminado — não recebem Modalidade, para que a
  explicação deles não mude;
- quando a população não comporta todas as atribuições (muitas reservadas, faixas grandes), o painel
  diz qual situação não foi plantada e por quê, como os casos-limite da fatia 1 já fazem.

Determinística: a mesma configuração na montagem produz as mesmas atribuições. As fronteiras de cada
reservada viajam no painel junto das da ampla.

## R-006 — Limites

- **Até 6 recortes reservados.** Os Editais da amostra declaram até 2 (PPI e PcD, 28/2026); o seletor
  nativo e o bloco de ocupação empilhado continuam legíveis com 6 a 375 px no esboço de medida da
  `094`. Acima disso o painel diz o limite (FR-2343).
- **500 candidatos e até 7 recortes em 1 segundo** (SC-876): cada recorte é uma ordenação sobre um
  subconjunto da mesma população, e a ampla é a maior; o custo é dominado por ela, que a `094` já
  mede.

## R-007 — O seletor de recorte e o fragmento

O fragmento da `094` ganha o parâmetro `recorte` (vazio para a ampla, o id da Modalidade para a
reservada), no mesmo formulário do painel que já carrega `vista` e `candidatos` — a única fonte, pela
lição do parâmetro duplicado (R-009 da `094`). Valor que não é recorte do Perfil volta à ampla e o
painel diz isso, em vez de 404: o rascunho pode ter perdido a Modalidade entre dois recálculos. A
jornada não usa o parâmetro: ela mostra todos os recortes (D-007).

## R-008 — Participantes da Etapa seguinte

**Conferido**: `resultados/application/prontidao.py::_dentro_da_faixa` deixa participar quem tem item
`PROGREDIU` num corte que governa a Etapa, **do Perfil dela, na ampla ou na Modalidade dela**
(`Q(corte__lista_id__isnull=True) | Q(corte__lista_id=modalidade)`). A prévia conta a união, por
pessoa, da faixa da ampla com a faixa da Modalidade de cada um — a mesma condição, em memória, sobre
a população fictícia (FR-2311). Como na `094`, as regras 1 e 2 de `restringir_a_participantes`
(eliminação anterior, habilitação na imediata) não são simuladas, e o "até" continua.

## R-009 — O que o protótipo prova, e o que não

**Prova**: que `preparar` com recorte, `ordenar`, `faixa.calcular`, `apurar`, `titulares_iniciais`,
`ocupantes` e `quantidade_a_reverter` rodam sem Django sobre candidatos fictícios com Modalidade; que
as cinco consequências da spec saem do motor oficial; que a rodada da D-002 é calculável na ordem
ampla → reservadas → reversão.

**Não prova**: a derivação dos recortes e a leitura da linha a partir do snapshot (o roteiro usa um
dicionário); as duas extrações (esboçadas); a tela. A extensão visual do protótipo da `094` é a
T030, depois do merge do #316.

## R-010 — O que a implementação acrescentou *(20/10, PR empilhado sobre o #320)*

1. **A apuração da reservada nasce com a efetiva líquida da cessão.** `emissao._apurar` desconta o
   que a cota cede antes de gravar, e a apuração registra `efetivas = publicadas − cedidas` e
   `faltando = 0`. A rodada da prévia faz o mesmo, e o painel mostra as vagas sem ocupante **antes**
   da cessão, dizendo à parte o que a apuração registraria depois — mostrar só o número líquido
   esconderia a vaga que a reversão levou.
2. **A rodada mora na `ocupacao`.** `classificacao` não importa `ocupacao`, e a rodada é decisão da
   ocupação: `ocupacao/domain/rodada_da_previa.py`, injetada em `simular` pela interface, como a
   fronteira das vagas da `094`.
3. **A população estável da `094` planta um empate na última vaga da ampla** (decisão 003 de lá), e
   ele para a apuração da ampla — e, com ela, a de toda reservada, que depende de saber quem ocupa
   pela ampla. Na abertura do painel de um Perfil com reserva, portanto, o bloco da ocupação diz que
   as reservadas não foram avaliadas. É o que o motor faria, e a prévia não o esconde nem o contorna;
   o painel aponta o caso-limite "Autodeclarado dentro das vagas da ampla" como o caminho para ver o
   resto. **Decidido pelo usuário em 20/10/2026: a população estável continua plantando o empate**
   também quando o Perfil tem reserva; o caminho para ver as reservadas é o caso-limite que o
   painel aponta.
4. **A Modalidade declarada e não apontada como a ampla vira recorte reservado**, como na
   classificação e na ocupação (`FR-503` da `034`). O Perfil padrão das fixtures de interface declara
   "Ampla concorrência (AC)" sem apontá-la, e a prévia dele mostra esse recorte, sem linha no quadro.
   O roteiro de compreensão manda apontá-la antes da sessão.
