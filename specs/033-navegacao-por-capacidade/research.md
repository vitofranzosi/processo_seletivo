# Research — 033 · Navegação por capacidade

Fase 0. O que precisava ser descoberto antes de planejar, conferido na árvore em `0a93b75`
(`main` com a `032` mergeada), em 18/09/2026.

---

## R-1 · A contradição está escrita, e está prendida por teste

**Descoberta.** As duas doutrinas convivem **no mesmo arquivo**, a cerca de mil linhas uma da outra:

| Porta | O que o docstring declara |
|---|---|
| `interface/views.py::_edital_para_publicar` | *"Sem a capacidade é **403, e não 404**, inclusive para quem preside a comissão … O 404 fica para o que o ator **não alcança** — Edital de outro escopo institucional, que ele não deve sequer saber que existe (FR-026)."* |
| `interface/views.py::_edital_para_classificar` | *"Tudo que o ator não alcança responde **404**."* |

**E a suíte de autorização afirma as duas.** `tests/authorization/test_publicacao_de_resultado.py`
abre dizendo *"as duas recusas dizem coisas diferentes de propósito"* e prende 403 para capacidade;
`tests/authorization/test_distribuicao.py` prende 404 para vínculo, com um caso cujo **nome** é
`test_quem_nao_tem_vinculo_nenhum_recebe_inexistente`.

**Consequência para o plano, e é a mais importante:** esta feature **muda testes que passam hoje**.
Isso é território perigoso — é a forma que tem "afrouxar autorização por engano". A contenção é
`SC-168`: pode mudar **o status da recusa**, nunca **quem passa**. Todo caso alterado troca `404` por
`403` e mantém intacta a asserção de que aquele ator **não entra**.

**Alternativa descartada.** Deixar `_edital_para_classificar` como está e corrigir só a navegação.
Fecharia `ACH-40` e deixaria `ACH-35` vivo — e pior: a tela deixaria de oferecer o caminho, então o
404 mudo passaria a acontecer só para quem montasse a URL, ficando ainda mais difícil de descobrir.

---

## R-2 · A superfície autorizativa **não está medida**, e é o inventário que a mede

**O único número conferido é este:** `interface/views.py` tem **75** `raise Http404`. Tudo além
disso é o que T003 vai determinar.

As funções nomeadas que se pareciam com "as portas" são quatro, e a leitura delas desfez a própria
pergunta:

| Função | Telas que governa | É porta de autorização? | Gramática hoje |
|---|---|---|---|
| `_edital_para_classificar` | **23** | sim | ❌ 404 para vínculo e para capacidade |
| `_edital_para_publicar` | 4 | sim | ✅ 403 para capacidade, 404 para escopo |
| `_processo_para_gerir` | — | sim | a classificar |
| `_ato_para_publicar` | — | **não** | recebe `edital`, `marco_id` e `ato_id`, **sem `request` e sem ator**: busca o ato dentro de um Edital já autorizado. O 404 dela é objeto inexistente |

Elas somam **5** ocorrências de `raise Http404` — 1, 2, 1 e 1 —, e não 4. Das cinco, **quatro** estão
em funções que de fato autorizam, distribuídas por **três** portas.

**Decisão.** A spec **não antecipa** a repartição. Nem "4 e 71", nem "5 e 70": o que ela afirma é
que há 75 no arquivo e que a superfície autorizativa sai do inventário. O que se sabe hoje é o
suficiente para escrever os requisitos — a porta que erra a gramática está identificada e governa 23
telas — e não é suficiente para declarar o tamanho da feature.

**O gatilho que isso cria.** Se o inventário encontrar recusa de autorização fora das portas já
identificadas, o tamanho mudou, e isso é conversa de escopo com quem governa o backlog — não decisão
de quem implementa. Por isso a parada é **logo depois de T003**, antes da fase 2, e não às vésperas
de uma tarefa específica.

**Por que a primeira medição errou duas vezes.** A redação original afirmava *"a superfície real são
quatro portas, não 76 pontos"*, medindo só as **definições de função**. A correção seguinte trocou
por *"apenas 4 dos 75 vivem dentro das portas"* — e errou de novo, por duas razões: a varredura por
faixa de linhas cobriu três intervalos e deixou `_ato_para_publicar` de fora, e a lista de "portas"
incluía uma função que não autoriza ninguém. **Duas tentativas de estimar o que só se sabe contando**
— e é por isso que o inventário é tarefa, e não parágrafo.

---

## R-3 · A recusa explicada já existe, e alcança toda a gestão

**Decisão.** `FR-478` e `FR-479` não constroem mecanismo nenhum.

**Rationale.** `interface/erros.py::RecusaDoDominioMiddleware` intercepta `DomainError` e a renderiza
como página, com o status que o domínio declarou, escolhendo o template pelo prefixo do caminho:
`/gestao/` → `interface/recusa.html`, `/selecoes/` → `portal/recusa.html`. O título de 403 já é
*"Você não tem permissão para isto"*, e o template já fecha com *"Nenhuma alteração foi feita"*.

O docstring do middleware explica por que ele existe: o handler do DRF não alcança views renderizadas,
e uma `DomainError` não tratada virava 500 *"inclusive quando ela diz apenas 'você não tem essa
permissão'"*. A classe inteira já foi fechada; falta uma porta usá-la.

**O que muda, então:** o `detail` da `DomainError`. Hoje `_edital_para_publicar` levanta
*"A operação não é permitida."* — correto e mudo. `FR-481` pede que ele nomeie o que falta.

---

## R-4 · O canal do candidato **não** entra nesta feature

**Decisão.** A gramática nova vale para `/gestao/`. O portal mantém o 404 uniforme.

**Rationale.** `tests/authorization/test_publicacao_de_resultado.py` registra por escrito, no caso
`test_uma_candidata_nao_alcanca_a_situacao_de_outra`: *"A recusa é **404 uniforme**: quem tenta não
descobre pela resposta se a inscrição não existe ou se existe e é de outra pessoa."*

São doutrinas **diferentes de propósito**, e as duas estão certas. No canal institucional o ator já
sabe que o Edital existe e precisa entender por que a tela não abre; no canal do candidato, distinguir
"não existe" de "é de outra pessoa" seria oráculo de enumeração. Levar a recusa explicada ao portal
seria um vazamento, não uma melhoria.

---

## R-5 · De onde a lista de destinos é derivada hoje

**Descoberta.** `interface/views.py::_marcos_publicados(edital, ator)` devolve `[]` quando
`pode_gerir_comissao(ator, processo)` é `None` **e** o ator não tem `auditoria:consultar`. É a causa
direta do `ACH-40`.

O docstring dela tem a intenção **certa** e a aplicação **estreita**:

> *"A porta do marco é `_edital_para_classificar`: presidência ou auditoria lê, e o resto recebe 404.
> A lista era montada sem consultar o ator, então quem julga recursos … via 'Classificação final' na
> tela do Edital e recebia erro ao clicar. **Oferecer o que se vai recusar é pior do que não
> oferecer.**"*

O princípio é o de `FR-476`. O erro é ter derivado a lista de **uma** porta, quando os destinos são
vários e cada ator alcança um subconjunto.

**Decisão.** A lista passa a ser derivada por **destino**, não por porta: cada item carrega para onde
leva, e entra se — e só se — o ator alcança aquele destino. O ator que alcança mais de um vê mais de
um; o que não alcança nenhum não vê o bloco.

**Alternativa descartada.** Mostrar tudo e recusar no clique. É exatamente o defeito que o docstring
acima registra ter corrigido, e regredi-lo para resolver outro achado seria trocar um por outro.

---

## R-6 · O texto que manda o operador a uma tela que ele talvez não alcance

**Descoberta.** Está em `interface/templates/interface/ordenacao.html`, em três lugares:

- *"Consultar ato e proveniência"* — o link;
- *"A divulgação é ato do próprio ato emitido, e sai de lá — em Consultar ato e proveniência, acima."*
- *"Divulgar o ato vigente é ato dele, e sai de Consultar ato e proveniência, acima."*

É o alvo de `FR-477`. A instrução está correta sobre **onde** o ato mora, e silenciosa sobre **quem**
pode praticá-lo — e quem lê a tela de ordenação é a presidência, que é justamente quem **não** publica
na configuração segregada. Daí o `ACH-38`.

---

## R-7 · Quem sabe nomear o que falta

**Decisão.** A mensagem da recusa e a frase do "peça a alguém" saem da mesma fonte: a base de
autorização que a porta consultou.

**Rationale.** `comissoes/domain/autorizacao.py::pode_gerir_comissao` devolve uma `Base` — ou a
permissão sistêmica, ou a presidência **deste** Processo — e `None` quando não há nenhuma. É ela que
distingue *"falta a capacidade X"* de *"falta o vínculo de presidência"*, que é o que `FR-485` exige.

**Atenção a uma armadilha.** `pode_gerir_comissao` devolve `None` **também** quando o escopo
institucional diverge. Ler só o `None` faria a recusa de escopo virar 403, contra `FR-480`. As portas
já filtram o Edital por `institution_scope` **antes** de chamá-la — a ordem existente é a correta, e
o plano a preserva.

---

## R-8 · Como `SC-168` se verifica

**Decisão.** A suíte `tests/authorization/` — **197 casos** em 38 arquivos — é o instrumento. Ela já
é o conjunto de pares (ator, tela) que o critério descreve.

**Método.** Antes de mudar qualquer coisa, registrar a contagem. Depois, a regra é aritmética: **zero
casos removidos**, e todo caso alterado muda **apenas o status esperado**, de `404` para `403`, sem
tocar em quem entra. Um caso que passe a esperar `200` onde esperava recusa é, por definição, o
defeito que `SC-168` existe para impedir — e derruba a feature, não o teste.

**Um caso muda de nome, e é de propósito.**
`test_quem_nao_tem_vinculo_nenhum_recebe_inexistente` passa a se chamar pelo que afirma depois: a
recusa deixa de ser "inexistente". Renomear sem mudar a asserção de acesso é o registro de que a
mudança foi de gramática, e não de autorização.
