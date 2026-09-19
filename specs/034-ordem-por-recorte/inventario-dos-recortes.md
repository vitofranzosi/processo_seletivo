# Inventário dos recortes — `T003` e `T004` · 034

**Método**: varredura de `backend/processo_seletivo/` em 18/09/2026, sobre a `main` `d30f6d8` — que
é a `af97d4c` da medição do [research.md](research.md) acrescida dos merges de documentação `#134` e
`#135`. Nenhum dos dois toca código. Cada linha abaixo saiu do `if` que decide, e não da definição
da função.

---

## (a) Todo ponto que deriva conjunto de recortes

| Onde | O que deriva | Inclui a Modalidade declarada como ampla? |
|---|---|---|
| `ocupacao/application/selectors.py:281` · `recortes_do_marco` | ampla + reservadas, com rótulo | **não** — `continue` explícito quando a identidade bate com `generalCompetitionModalityId` |
| `sorteios/application/previa.py:43` · `recortes_do_marco` | `listas = [(None, …)] + [cada Modalidade declarada]` | **sim** — nenhum filtro |
| `classificacao/application/corte.py:53` · `linha_do_quadro` | não deriva conjunto; **resolve um** recorte pedido | **apelido** — `alvo = None` quando bate |

**São três tratamentos, em três módulos, exatamente como `research.md` `R-3` mediu.** Nenhum
quarto apareceu.

### Consumidores da derivação

| Quem chama | Qual das três |
|---|---|
| `interface/views.py:5553` · tela de ocupação | a da ocupação |
| `interface/views.py:7003` e `:7136` · telas do sorteio | a do sorteio |

A classificação **não chama nenhuma**: é exatamente a ausência que a `FR-491` fecha.

---

## (b) Todo ponto que fixa `lista_id` na classificação

| Onde | O que fixa | Consequência |
|---|---|---|
| `classificacao/application/emissao.py:63` | `lista_id=None` na busca do vigente | a emissão nunca vê ato de recorte reservado |
| `classificacao/application/emissao.py`, no `objects.create` | **não informa** a lista — a coluna nasce nula | o ato computado é sempre o da ampla |
| `classificacao/application/calculo.py:20` | a assinatura **não tem** recorte | o universo é sempre o Perfil inteiro |
| `interface/views.py:5109` · `ordenacao` | chama `estado_do_marco` sem `lista_id` | a tela só sabe a ampla |
| `interface/views.py:5315` · confirmação da emissão | idem | idem |
| `interface/views.py:5156` · `historico_da_ordenacao` | `historico()` não filtra por lista | o histórico misturaria os três recortes |
| `interface/views.py:5229` · `_corte_do_marco` | chama `estado_do_corte` sem `lista_id` | só a faixa da ampla aparece no marco |
| `interface/views.py:5173` · `_divulgacao_do_marco` | compara todas as publicações contra **um** ato vigente | o docstring já declara a premissa e o limite dela |
| `processos/management/commands/seed_demo.py:1381` | chama `calcular_ordem` sem recorte | quebra na assinatura nova |

**Nove pontos.** Nenhum deles é de autorização, e nenhum é recusa de emissão que o `research.md`
não previsse — a única recusa por recorte que existe é `_recusar_marco_de_sorteio`, em
`emissao.py:175`, e ela é por **marco**, não por recorte.

### A cauda, em contraprova

`ato_vigente` tem **9 chamadas** em `processo_seletivo/`, e as 9 passam `lista_id` explicitamente:
`ocupacao/selectors.py` (×2), `ocupacao/emissao.py`, `ocupacao/movimento.py`,
`interface/supervisao.py`, `classificacao/selectors.py`, `classificacao/corte.py` (×2),
`convocacao/convocar.py`. Zero herdam o padrão — `research.md` `R-7` confirmado linha a linha.

---

## (c) Todo ponto que lê `generalCompetitionModalityId`

**38 ocorrências em `processo_seletivo/`**, contadas por varredura completa e repartidas assim:

| Módulo | Ocorrências |
|---|---|
| `interface` | 17 |
| `editais` | 14 |
| `processos` | 3 |
| `publicacoes` | 2 |
| `ocupacao` | 1 |
| `classificacao` | 1 |
| **`sorteios`** | **0** |

Os números batem, um a um, com a tabela de `research.md` `R-3` — inclusive o zero do sorteio, que é
o que torna a derivação dele divergente: ele é o único módulo do caminho que não conhece o campo, e
por isso dá recorte próprio à Modalidade que os outros excluem ou apelidam.

---

## `T004` — o portão de escopo, reconfirmado

**A superfície não mudou.** As três derivações continuam sendo três, nos mesmos três módulos e com
os mesmos três tratamentos; a contagem de `generalCompetitionModalityId` fecha em 38 com a mesma
repartição; nenhuma derivação de recortes nova apareceu; e nenhuma recusa de emissão por recorte
existe além da recusa **por marco** do sorteio, que a medição já previa.

**Logo: segue, com o escopo ratificado em `D-004`** — a `034` alinha classificação e ocupação, e o
sorteio fica fora. A fase 2 está liberada.

### O registro que a `FR-491a` exige

**A divergência**: `sorteios/application/previa.py::recortes_do_marco` monta `listas` a partir de
`perfil["competitionModalities"]` **sem excluir** a Modalidade apontada em
`generalCompetitionModalityId`. `ocupacao/application/selectors.py::recortes_do_marco` a exclui. Para
o mesmo Perfil — e a declaração da Modalidade como ampla é o caso normal do acervo —, o sorteio
oferece **um recorte a mais** do que a ocupação tem linha para consumir.

**O risco, nomeado**: o sorteio pode emitir hoje, e pôde emitir desde a `021`, um ato de ordenação
num recorte que a apuração não enxerga — o mesmo defeito que a `FR-491` fecha do lado computado,
vivo do lado sorteado e **anterior** a esta spec.

**Por que não se corrige aqui**: a `021` construiu sobre o recorte por lista decisões, telas,
relações publicadas, verificadores e **cadeias históricas**. Retirar o recorte excedente obriga a
responder como os atos já emitidos nele continuam alcançáveis — e ato publicado não se apaga nem se
reescreve. Isso é desenho, não migração, e é spec própria. É `D-004`, ratificado em 18/09/2026 por
quem governa o backlog.

**O que esta feature faz com ele**: registra, e não toca. A `SC-172` compara **duas** listas — a da
classificação e a da ocupação — exatamente por isso.

---

## Uma correção de endereço que a medição produziu

O `plan.md` situa o documento que precisa nomear o recorte (`FR-506`) em
`publicacoes/infrastructure/pdf.py`. **Não é lá.** Esse arquivo compõe o documento do **Edital**;
quem compõe o documento do **ato de ordenação divulgado** é
`divulgacao/infrastructure/documento.py`, que importa daquele a costura (`Composicao`,
`render_documento`) e monta a própria moldura em `_identificacao`.

E o conteúdo já carrega o recorte: `divulgacao/domain/conteudo.py:121` grava
`cabecalho["lista"]` desde a `021`, e `portal/templates/portal/resultado.html:5` já o exibe na
página pública. **O que falta é só o documento imprimi-lo** — a moldura de `_identificacao` não tem
a linha. A `FR-506` é, portanto, menor do que o plano supôs, e está num arquivo vizinho ao que ele
nomeia.
