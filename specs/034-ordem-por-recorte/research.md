# Phase 0 — Pesquisa e medição · 034 · Ordem por recorte em marco computado

**Método**: leitura dirigida e varredura de AST de `backend/`, em 18/09/2026, contra a `main`
`af97d4c`. Cada afirmação abaixo tem o arquivo e a linha em que foi conferida.

> **Por que este arquivo insiste em medir.** A `033` produziu **três** medições erradas seguidas da
> própria superfície, cada uma corrigindo a anterior, e as três vieram de **descrever a função pela
> definição** em vez de contar. Só pararam quando a medição virou varredura de AST. Aqui, tudo que é
> contagem foi contado; tudo que é comportamento foi lido no `if` que o decide.

---

## R-1 — O modelo já está pronto, e a ausência de migration é medida, não esperada

`classificacao/models.py`, no `Meta` de `AtoDeOrdenacao`, tem **duas** `UniqueConstraint` parciais:

| Constraint | Campos | Condição |
|---|---|---|
| `uq_ato_raiz_por_marco` | edital, perfil, marco | raiz **e** `lista_id` nulo |
| `uq_ato_raiz_por_marco_e_lista` | edital, perfil, marco, **lista** | raiz **e** `lista_id` não nulo |

O comentário que as acompanha é da `021` e descreve **exatamente** a forma que esta feature precisa:
*"três listas, três atos raiz, um marco só, porque a janela recursal é do marco e os Editais
publicam um período para as três."*

**E a prova de que o banco aceita um ato computado por lista já existe e roda hoje.**
`tests/integration/classificacao/test_ato_por_lista.py` constrói atos com
`origem=OrigemDaOrdem.COMPUTADO` **e** `lista_id` preenchido. O que impede a ordem por recorte não é
o esquema: é uma linha na aplicação.

**Decisão**: nenhuma migration. **Alternativa considerada**: acrescentar coluna ou índice para
distinguir a origem por recorte — descartada porque `origem` já existe e a constraint já separa.

---

## R-2 — Onde exatamente a emissão trava, e o que o cálculo não recebe

| Ponto | O que faz hoje | Arquivo |
|---|---|---|
| Busca do vigente | filtra `lista_id=None` fixo | `classificacao/application/emissao.py`, no `AtoDeOrdenacao.objects.filter` |
| Criação do ato | não informa lista — nasce nulo | mesmo arquivo, no `objects.create` |
| Cálculo | assinatura `calcular_ordem(*, edital, perfil_id, marco_id, at=None)` | `classificacao/application/calculo.py:20` |
| Universo do cálculo | `Inscricao.objects.filter(edital, profile_id, status=SUBMETIDA)` — **sem** modalidade | `calculo.py`, na montagem de `consulta` |

`Inscricao` carrega `modality_id` (`inscricoes/models.py:34`), e o campo é `null=True`: **quem não se
autodeclara tem modalidade nula**, e isso é o caso normal da ampla concorrência.

**Os consumidores de `calcular_ordem` são quatro, e foram contados:**
`classificacao/application/selectors.py:330`, `classificacao/application/emissao.py:67`,
`processos/management/commands/seed_demo.py:1381`, e o `__all__` do próprio módulo. Todos passam a
precisar dizer **de qual recorte** falam — ou herdar a ampla explicitamente, que é o que a `021` fez
e deu certo.

---

## R-3 — O achado que a spec nomeia, medido com mais precisão: são **três** tratamentos, não dois

A spec registrou que existem duas derivações homônimas de `recortes_do_marco` e que elas discordam.
A medição confirma, **e encontra um terceiro tratamento** do mesmo fato, num quarto módulo.

O fato em questão é a **Modalidade declarada como ampla concorrência** — o campo
`generalCompetitionModalityId` do Perfil, que é a grafia-armadilha: tem nome de Modalidade e a
quantidade dela mora na linha geral do Quadro.

| Módulo | Como trata a Modalidade declarada como ampla | Onde |
|---|---|---|
| **Ocupação** | **não é recorte** — excluída da lista | `ocupacao/application/selectors.py:296` |
| **Corte** | **é recorte, e é apelido**: pedir por ela lê a linha geral | `classificacao/application/corte.py:67` |
| **Sorteio** | **é recorte próprio**, como qualquer outra | `sorteios/application/previa.py`, na montagem de `listas` |
| Interface — composição, Revisão, Retificação, supervisão | leem o campo e o respeitam | 17 pontos em `interface/` |

**A varredura por `generalCompetitionModalityId` devolve 38 ocorrências em `processo_seletivo/`,
repartidas assim — `interface` 17, `editais` 14, `processos` 3, `publicacoes` 2, `ocupacao` 1,
`classificacao` 1 — e `sorteios/` devolve zero.** O sorteio é o único módulo do caminho que não
conhece o campo.

*(A primeira contagem desta linha dizia 20, porque foi lida de uma saída truncada em `head -20`. É o
erro exato contra o qual o cabeçalho deste arquivo adverte, cometido dentro dele e corrigido por
contagem — fica registrado em vez de apagado.)*

**A consequência é concreta e já existe hoje, antes desta feature.** Num Edital que declara uma
Modalidade como ampla — que é o caso normal —, a tela do sorteio oferece um recorte para ela, e a
tela de ocupação não tem linha própria para consumir o que for emitido ali. A `021` conviveu com isso
por outra via: ela **desambiguou os rótulos**, porque *"a tela mostrava dois blocos homônimos, um com
o sorteio feito e outro vazio, e quem conduz o certame não tinha como saber em qual publicar"*. O
rótulo resolveu quem lê; não resolveu quem consome.

### O que isto obriga esta feature a decidir

**`FR-491` manda derivar em um lugar só, e diz que classificação, ocupação e sorteio MUST responder
o mesmo.** A medição mostra que satisfazê-lo ao pé da letra significa **mudar o sorteio**, que é uma
feature que funciona, que tem telas em produção e cujo comportamento a `034` declarou fora de escopo.

**O que foi feito com esta medição, em 18/09/2026:**

1. A `034` adota a derivação da **ocupação** para o caminho computado — é a que a cauda consome, e é
   a que três dos quatro módulos já praticam.
2. A `FR-491` foi **estreitada** para *classificação e ocupação*, e a `SC-172` diz por que mede duas
   listas e não três. Isso não foi escolha deste arquivo: o `analyze` mostrou que a redação anterior
   exigia três e era medida por um critério de duas — **requisito que o próprio critério não
   alcança**, que é a mesma espécie de defeito que a `033` levou seis passadas para expulsar.
3. A divergência do sorteio virou requisito próprio, a **`FR-491a`**: ela obriga a **registrar** e
   proíbe **corrigir**.
4. **A pergunta que sobra é de governança, e está na `T004`**: ampliar a `FR-491` para alcançar o
   sorteio, ou manter a divergência registrada? Esta pesquisa não a responde.

**É parada de escopo, e não decisão de implementação.** Ela está na `T004` do `tasks.md` pela mesma
razão que a `033` pôs a dela lá: descobrir a diferença e resolvê-la em silêncio faz a feature crescer
sem que ninguém tenha decidido isso.

---

## R-4 — A coerência com a `032` custa **uma linha**, e isso foi verificado

`editais/domain/marcos.py:215` define `emite_ordem_no_recorte`, e o corpo dela é:

```
if lista_id is None:
    return True
return marco_ordena_por_sorteio(conteudo, perfil_id=perfil_id, marco_id=marco_id)
```

**Os consumidores são exatamente dois**, contados por varredura:

| Consumidor | O que ele decide | Arquivo |
|---|---|---|
| a validação da publicação | se o aviso `reserved_row_without_ordering` é produzido | `editais/domain/validation.py:2438` |
| o selector da ocupação | o campo `apuravel`, que a tela usa para oferecer ou não a apuração | `ocupacao/application/selectors.py:226` |

O docstring dela, escrito pela `032`, **anuncia esta feature**: *"A regra real vive em
`classificacao/application/emissao.py`, e este predicado apenas a lê… esta função não a muda: ela a
torna perguntável antes da publicação, em vez de descoberta no dia da apuração."*

**Decisão**: a `034` muda a **resposta** desse predicado, e o aviso e a tela seguem atrás. Nenhuma
segunda pergunta é criada — é a `FR-500`, e o custo dela é a segunda linha da função.

**Alternativa considerada e descartada**: acrescentar um predicado próprio na classificação. Criaria
duas verdades sobre "este marco emite aqui", que é literalmente o defeito que a `032` registrou como
razão de a função existir.

---

## R-5 — A superfície de teste que muda, contada caso a caso

A `033` mostrou que **contar não basta** — um caso pode manter o número de asserções e trocar o que
afirma. Por isso a tabela abaixo é por **função de teste**, e diz o que acontece com cada uma.

### Os dez casos de `reserved_row_without_ordering`, em `tests/unit/editais/test_executabilidade.py`

| Linha | Caso | Depois da `034` |
|---|---|---|
| 367 | `…reserva_em_marco_que_nao_sorteia_produz_aviso_e_nao_impedimento` | **muda** — não há mais aviso |
| 377 | `…o_aviso_da_reserva_nomeia_a_causa_e_nao_o_sintoma` | **muda** |
| 395 | `…o_aviso_da_reserva_nao_e_emitido_na_retificacao` | **muda** — vira vacuamente verdadeiro, e caso vacuamente verdadeiro é caso que não prende nada |
| 403 | `…perfil_cujo_marco_sorteia_nao_recebe_achado` | permanece |
| 414 | `…a_modalidade_declarada_como_ampla_nao_e_lida_como_reserva` | permanece, e **passa a passar vacuamente** — com o aviso aposentado, `achados(...) == []` é verdade qualquer que seja a derivação. Não é contraprova de nada; a da derivação única é a `SC-172`, que compara as duas listas. Mantenha-o, e **não** o cite como guarda |
| 430 | `…linha_reservada_zerada_nao_produz_aviso` | permanece |
| 448 | `…perfil_sem_marco_algum_nao_acumula_o_aviso_da_reserva` | permanece |
| 474 | `…o_aviso_alcanca_o_segundo_marco_quando_o_primeiro_sorteia` | **muda** |
| 492 | `…todos_os_marcos_sorteando_continua_sem_achado` | permanece |
| 506 | `…dois_marcos_em_lista_unica_saem_num_achado_so_que_nomeia_os_dois` | **muda** |

**Cinco mudam, cinco permanecem.** A conta vale porque a `FR-501` **aposenta** o aviso — decisão que
está na spec, e não na implementação. Enquanto ela dizia *"aposentar ou estreitar"*, esta conta não
existia: a escolha muda quais casos mudam, e spec que oferece duas saídas não está determinada.

**E há uma consequência que a aposentadoria arrasta.** Sem caso que produza o aviso,
`emite_ordem_no_recorte` passa a responder **sempre sim**, e o campo `apuravel` derivado dele deixa de
variar. Guarda que nunca reprova é pior do que guarda nenhum, porque o próximo a ler o código confia
nele — é a `FR-501a`, e ela manda **medir antes de remover**.

### Os três casos do `apuravel`, em `tests/interface/test_ocupacao.py`

| Linha | Caso | Depois da `034` |
|---|---|---|
| 524 | `…recorte_reservado_em_marco_computado_nao_oferece_apuracao` | **muda de sentido** — passa a oferecer |
| 539 | `…no_lugar_da_apuracao_a_tela_nomeia_a_causa_e_nao_o_sintoma` | **muda** — a frase sai, porque deixou de ser verdade |
| 556 | `…o_recorte_da_ampla_continua_apuravel` | permanece, e é a não-regressão |

**Os três casos vizinhos, de 472 a 500, são da família do corte (`FR-463`) e NÃO mudam.** Estão
nomeados aqui porque estão no mesmo arquivo e a semelhança convida ao erro.

### Os outros dois arquivos

| Arquivo · caso | Depois da `034` |
|---|---|
| `tests/interface/test_hardening_pos_auditoria.py:1055` · `…os_dois_avisos_da_familia_nao_impedem_a_publicacao` | **muda** — deixa de haver dois |
| `tests/integration/editais/test_acervo_inexecutavel_continua_retificavel.py:264` | permanece |

### E um que deixa de precisar existir

`tests/integration/ocupacao/test_reversao.py` constrói a apuração da cota **à mão**, e diz por quê:
*"O caminho do ator não a alcança em certame computado, porque não existe ordem com `lista_id`."*
Depois da `034` o caminho passa a existir. **O helper não deve ser apagado nesta feature** — ele é
chamado por **seis** casos de reversão, e trocá-lo mudaria o que eles exercitam —, mas a frase que o
justifica fica falsa, e deixá-la é deixar documentação que mente.

**Total medido: 8 casos mudam, em 3 arquivos** — cinco em `test_executabilidade.py` (367, 377, 395,
474, 506), dois em `test_ocupacao.py` (524, 539) e um em `test_hardening_pos_auditoria.py` (1055).
**Mais uma correção de prosa num quarto arquivo**, `test_reversao.py`, que não altera caso algum.
Nenhum dos oito é de autorização.

> **Esta linha dizia "11 casos em 4 arquivos", e o número nunca fechou com a tabela acima.** Ele
> atravessou três passadas de `analyze` e se replicou em nove lugares, porque cada artefato novo o
> copiou do anterior em vez de somar. O cabeçalho deste arquivo promete que *"tudo que é contagem foi
> contado"* — aqui não tinha sido. Fica registrado, e não apagado: é o alicerce dos dois portões
> desta feature, e quem grava o "antes" procurando onze e achando oito precisa saber por quê.

---

## R-6 — O que as telas já sabem, e é menos trabalho do que a spec supôs

A spec disse que as telas de ordenação e de corte não têm noção de recorte. **Metade disso está
errado**, e a correção reduz o escopo:

| Tela | Lê o recorte? | Onde |
|---|---|---|
| **Corte** | **sim**, de `?lista=` | `interface/views.py::corte`, primeira linha útil: `_identidade_ou_404(request.GET.get("lista"))` |
| **Ocupação** | não precisa — lista **todos** os recortes na mesma página | `interface/views.py::ocupacao` |
| **Ordenação** | **não** | `interface/views.py::ordenacao` não lê `request.GET` para lista |

A rota do corte declara isso por escrito: *"Pende do marco… e o recorte vem em `?lista=`: um marco de
cotas tem três, e cada um tem a sua faixa."*

**O que falta, então, é preciso:** a ordenação não sabe ler o recorte, e **nenhuma das duas telas
oferece caminho entre os recortes**. Uma sabe receber e não sabe navegar; a outra não sabe nem uma
coisa nem outra.

---

## R-7 — A cauda está parametrizada, e isso foi contado, não presumido

`ato_vigente(*, edital, marco_id, lista_id=None)` é o ponto por onde todo consumidor pergunta pela
ordem vigente de um recorte. A varredura de AST contou **9 chamadas em `processo_seletivo/`, e
todas as 9 passam `lista_id` explicitamente**:

`ocupacao/selectors.py` (×2) · `ocupacao/emissao.py` · `ocupacao/movimento.py` ·
`interface/supervisao.py` · `classificacao/selectors.py` · `classificacao/corte.py` (×2) ·
`convocacao/convocar.py`

**Zero chamadas herdam o padrão.** É o risco que o docstring da própria função nomeia — *"sem filtrar
pela lista, `.first()` escolheria uma das três pela ordem de emissão, que é sorteio de dado"* — e ele
não se materializou. A cauda não precisa de mudança para consumir a ordem nova.

---

## R-8 — O recorte reservado sem nenhum autodeclarado

É o primeiro *Edge Case* da spec, e a pesquisa não o fecha sozinha: é decisão de significado.

**As duas leituras**, e o que cada uma custa:

| | Ordem vazia emitida | Ausência de ato |
|---|---|---|
| O que declara | *"ninguém concorreu por este recorte"* — fato normativo, publicável | nada |
| Como se distingue de "ainda não emitiram" | pelo próprio ato | **não se distingue** |
| O que a ocupação faz com ela | apura zero ocupadas sobre zero classificados | não tem o que apurar |
| Custo | um ato a mais para conferir na Retificação | o operador não sabe se falta trabalho ou não há trabalho |

**Decidido, e a decisão foi para a spec: `FR-492a`.** Ordem vazia é emitível e **nunca automática** —
a emissão continua sendo ato de quem conduz, e o que muda é que passa a existir um ato que declara a
ausência. A tela do recorte vazio explica o que ele é, em vez de parecer pendência.

*Esta tabela é o caminho da decisão, e não a decisão em aberto.* A primeira redação a deixava como
"tarefa de decisão", e pesquisa que recomenda sem decidir empurra para dentro da implementação uma
escolha de significado — foi o `analyze` que pegou.

---

## R-9 — O que o percurso precisa, e o que o `seed_demo` não dá

A memória do projeto registra que o `seed_demo` **não produz o certame do manual** — o elenco colide
com os candidatos, e o cenário se monta à mão pela interface.

Para o `SC-169` — o Edital 7/1/2 indo da classificação à convocação pelos três recortes — o percurso
precisa de: um Perfil com Quadro de Vagas 7/1/2, duas Modalidades reservadas com fundamento legal, e
inscrições autodeclaradas em cada uma. O `quickstart.md` monta isso pela interface, e **não por
shell**, que é o que o Princípio VI cobra.

`seed_demo.py:1381` chama `calcular_ordem` diretamente; ele passa a precisar dizer de qual recorte
fala, ainda que seja a ampla. É mudança de uma linha, e está nomeada para não ser esquecida — comando
de semeadura que quebra só aparece na próxima vez que alguém semeia.

---

## Resumo das decisões

| | Decisão | Onde vira requisito |
|---|---|---|
| R-1 | Nenhuma migration; o esquema da `021` já serve | `FR-505` |
| R-3 | Derivação única é a da **ocupação**; `FR-491` **estreita** para classificação e ocupação, e a divergência do sorteio vira achado | parada de escopo, `T004` |
| R-4 | A coerência com a `032` passa pela resposta de `emite_ordem_no_recorte` | `FR-500` |
| R-5 | **8** casos mudam, em 3 arquivos — e uma correção de prosa num quarto —, nenhum de autorização | conferência caso a caso, na entrega |
| R-6 | O corte já lê o recorte; falta navegação nas duas telas, e leitura na ordenação | `FR-497`, `FR-498` |
| R-8 | Ordem vazia é emitível, nunca automática | tarefa de decisão |
