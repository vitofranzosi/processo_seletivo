# Phase 0 — Pesquisa: a visão institucional dos Processos Seletivos

**Feature**: `040-visao-institucional-dos-processos` · **Data**: 2026-09-21

**Método**: leitura do código contra a spec. Nenhum `NEEDS CLARIFICATION` permaneceu aberto; um
achado **corrige a spec** e está nomeado em `R-005`.

---

## R-001 — Onde a página vive, e como se chega a ela

**Decisão**: rota `GET /gestao/visao-geral`, view `visao_geral` em `interface/views.py`, derivações
em **`interface/visao_geral.py`** — módulo novo, só de leitura.

**Racional**. O `interface/urls.py` organiza as rotas por agregado: `processos/<id>/…`,
`editais/<id>/…`, e a raiz `""` é a lista. Esta página não pende de agregado nenhum — é do escopo,
como a lista —, e por isso é rota de primeiro nível.

**O módulo separado não é preferência**: `interface/supervisao.py` estabeleceu o padrão e escreveu a
razão — *"aqui vivem as derivações, e mantê-las separadas da montagem de contexto é o que permite
testá-las como domínio de leitura, sem requisição"*. `views.py` tem 7885 linhas; acrescentar
derivação lá é o que impede o teste sem cliente HTTP.

**O caminho**: um link em `lista.html`, ao lado de *"Novo Processo Seletivo"*, visível só para quem
detém a capacidade (`FR-605`). O cabeçalho de `base.html` **não** ganha entrada: ele tem hoje um
link só — *Minhas Etapas* — que não depende de papel, e pendurar ali um que depende reabriria o
`E-2` (autorização × navegação) que a `038` já reabriu uma vez com o `N-03`.

**Alternativas recusadas**. *Pendurar na lista de Processos como aba*: a lista é do escopo e a visão
também, mas misturá-las faria a lista carregar snapshots que ela não usa. *Rota sob `processos/`*:
mentiria sobre o nível — a página é **acima** do Processo (`D-002`).

---

## R-002 — O nome da capacidade, e onde ele mora

**Decisão**: `visao:consultar`, constante `CONSULTAR` no topo de `interface/visao_geral.py`, escrita
**literalmente** em `PAPEIS["gestor"]` e presa por teste de grafia.

**Racional**. O repositório tem o padrão pronto, com a razão escrita em `interface/identidade.py`:

> *"A permissão vai escrita, e não importada de `matriculas`, como todas as outras deste mapa: este
> módulo é a fronteira de identidade, e não deve conhecer o app que consome a permissão. A grafia é
> conferida por teste."*

A aplicação usa `require_permission(ator, visao_geral.CONSULTAR)` — o mesmo ponto único que
`exportar_matriculas` usa, com 403 para falta de capacidade e 404 para escopo alheio. Não é
`require_authorization_base`: aquela existe para o predicado composto *capacidade **ou** vínculo*, e
aqui não há vínculo que sirva — não existe *"presidir a instituição"*.

**A grafia `visao:consultar`** segue a forma `<recurso>:<verbo>` de todas as outras, e o verbo é
`consultar` porque é o que `inscricao:consultar` e `auditoria:consultar` já usam para leitura.

**Alternativas recusadas**. *Reusar `inscricao:consultar`*: daria o panorama por efeito colateral de
poder ler dossiê de candidato — exatamente o que a `031` recusou por escrito. *Reusar
`auditoria:consultar`*: o auditor lê trilha, não portfólio, e ampliá-lo mudaria o que aquele papel
significa. *Criar o papel `diretoria` agora*: é decisão institucional, e está registrada em `G-010`.

---

## R-003 — A extração compartilhada do resolvedor de versão vigente

**Decisão**: extrair `versoes_vigentes(*, editais=None, at=None, incluir_cancelados=True)` em
`publicacoes/application/selectors.py`, e reescrever `selecoes_publicas` para consumi-la.

**Racional**. `selecoes_publicas` já resolve *"a versão vigente de cada Edital"* em duas consultas,
com a razão medida no docstring: a primeira decide a vencedora lendo só identificador e vigência, a
segunda materializa apenas as vencedoras — *"ordenar e escolher em memória sobre o conteúdo inteiro
faria a vitrine crescer com o histórico"*. É exatamente o que esta feature precisa.

**Mas ela mistura duas perguntas**: *qual é a vigente* e *o que é público* — e a segunda exclui o
Edital cancelado, porque *"listar como oportunidade uma seleção cancelada convidaria alguém a se
inscrever no que não existe mais"*. A gestão **precisa** ver o cancelado: ele consumiu vagas
publicadas e recebeu inscrições, e escondê-lo faria o agregado mentir sobre o que houve.

A extração separa as duas: o resolvedor não conhece política de visibilidade, e
`selecoes_publicas` continua aplicando a dela. Copiar a lógica criaria a segunda verdade que
`FR-582` proíbe.

**O parâmetro `editais`** é o que torna `FR-598` exequível: sem ele, o resolvedor varre o acervo
inteiro antes de qualquer recorte.

**Alternativa recusada**. *Deixar `selecoes_publicas` como está e escrever um segundo resolvedor*:
duas implementações da mesma decisão de vigência, que divergiriam na primeira mudança.

---

## R-004 — Como a razão recortada sai de uma consulta

**Decisão**: a agregação de inscrições passa a agrupar por Perfil —
`values("edital_id", "profile_id", "status").annotate(Count("id"))` —, e o recorte do numerador
acontece em memória, contra o conjunto de Perfis com vaga imediata lido do snapshot.

**Racional**. `D-012` exige que o numerador use só os Perfis que publicam vaga imediata.
`Inscricao.profile_id` guarda a identidade **publicada** do Perfil — estável sob Retificação, pela
mesma razão que `ResultadoEtapa.etapa_id` —, e é a mesma identidade que aparece em
`profiles[].id` no snapshot. Os dois casam por construção.

**Continua sendo uma consulta.** O que cresce é o número de linhas devolvidas, limitado por
`Editais × Perfis × 2`, e o índice `(edital, status)` continua servindo. **A coluna *Submetidas* é a
soma das linhas do Edital**, de modo que o total e o numerador saem da **mesma** leitura e não podem
divergir — que é a metade de `D-012` fácil de perder na implementação.

**O teste de vaga imediata é `immediateVacancies > 0`**, e não a existência do Perfil: um Perfil de
cadastro de reserva publica `0`, e `LinhaDoQuadroDeVagas` reparte esse mesmo total.

**Alternativa recusada**. *Uma consulta por Edital com o recorte no SQL*: quebraria `SC-209`.

---

## R-005 — `institution_scope` **é** dimensão de unidade, e é constante dentro da gestão

> **Este achado corrige a spec.** A §3.1 e a `G-004` afirmam que *"não existe dimensão"* de unidade.
> A afirmação é forte demais, e o portal prova o contrário.

**O fato medido**. `portal/leitura.py` oferece um filtro **`unidade`** na vitrine pública, e
`portal/views.py:122` mostra de onde ele sai:

```python
"unidade": versao.edital.institution_scope.upper(),
```

com a razão escrita ao lado: *"A unidade vem do Edital porque escopo institucional é identificação
do ato, não conteúdo normativo."* E `opcoes_da_consulta` monta as opções a partir do catálogo, *"e
não de uma lista fixa"*.

**Por que isso não reabre o filtro na gestão.** A vitrine é **cross-scope** — `selecoes_publicas`
não filtra por escopo nenhum, e por isso lá a unidade varia. A visão institucional é confinada ao
`institution_scope` do ator por `FR-583`, e dentro dele **a unidade é constante**: o filtro teria
sempre exatamente uma opção.

**A redação correta**, que substitui a atual:

> A unidade existe como `institution_scope` e o portal já a usa como eixo. Ela **não serve de filtro
> aqui** porque a visão é confinada a um escopo — não por falta de dado, mas por definição do
> recorte. O que **não** existe é dimensão **abaixo** do escopo: campus, polo ou câmpus dentro da
> mesma unidade, que é o que `AX-6`/`ACH-60` discutem e o que `PerfilVaga.locality` guarda em texto
> livre.

**A decisão que isso abre**, e que é do usuário: *existe visão institucional cross-scope?* Se a
instituição vier a ter mais de um `institution_scope`, a pergunta *"diferenças entre unidades"*
passa a ser respondível — e **não** por esta página, que é escopada por princípio constitucional.
Registrada como `G-014`.

---

## R-006 — A varredura de vocabulário tem lista literal, e a tela nova escapa em silêncio

**Decisão**: a prosa visível da página **não usa** os três termos vigiados — *recorte*, *geração*,
*faixa*. Se alguma redação os usar, a tela entra em `TELAS` no **mesmo commit** e define o termo em
`<dfn>`.

**Racional**. `tests/test_vocabulario_da_composicao.py` cobra que o primeiro uso visível de
*recorte*, *geração* ou *faixa* esteja dentro de um `<dfn>` com definição. A lista de telas é
**literal e não `glob`**, com a razão escrita: *"uma lista calculada passaria a ignorar a tela que
deixasse de usar o termo"*. E a `matriculas.html` traz o comentário que é o aviso para esta feature:

> *"Entra na lista no mesmo commit em que nasce: a lista é literal e não `glob`, e sem esta linha a
> tela escaparia da regra em silêncio — ninguém veria falha nenhuma."*

**O risco é concreto**: a spec usa *recorte* dezenas de vezes. É palavra de especificação, não de
tela — quem lê a página quer ler *"Editais de 2026"*, e não *"o recorte"*. A prosa visível usa o ano
e a situação por extenso.

---

## R-007 — Onde o CSS mora

**Decisão**: as regras novas vão no `<style>` de `interface/templates/interface/base.html`.

**Racional**. Medido: `base.html` tem 1179 linhas, das quais 1145 são um `<style>` inline único
(linhas 7 a 1152). `interface/static/interface/` contém **só JavaScript** — nove arquivos, nenhum
`.css`. Não há folha externa a estender, e criar a primeira nesta feature seria mudança estrutural
que a spec não pede.

**A armadilha registrada**: memória do projeto e o achado `varredura-le-o-comentario` dizem que
regra nova na folha quebra asserção de substring em teste de template. O plano prevê rodar a suíte
de interface depois do CSS, e não só depois do Python.

---

## R-008 — Ordenação: não há precedente reusável

**Decisão**: ordenação **no servidor**, por parâmetro de consulta saneado, no padrão de
`portal/leitura.py`. Nada de JavaScript.

**Racional**. `interface/static/interface/ordenacao.js` **não** ordena tabela: ele move linhas de
formulário e mantém o campo `order` coerente — outro problema. O precedente aproveitável é o do
portal: `PARAMETROS`, `ORDENS`, `ORDEM_PADRAO`, `consulta_da_vitrine` saneando o que veio da URL, e
`filtrar` aplicando sobre o que a página já carregou.

**A regra que a spec acrescenta** (`FR-601`): ausência vai ao fim **nos dois sentidos**. Em Python
isso é uma chave de ordenação em tupla — `(valor is None, valor)` para crescente e
`(valor is None, -valor)` para decrescente —, e **não** `reverse=True` sobre a mesma chave, que
jogaria as ausências para o começo.

---

## R-009 — Auditoria: esta página não registra

**Decisão**: nenhum `RegistroAuditoria` é gravado ao abrir a página.

**Racional**. A Constituição exige auditoria de **operações sensíveis**. O precedente que separa os
dois casos está medido: `interface/supervisao.py` lê sete apps e **não audita** — *"este módulo só
lê"* —, enquanto a **prévia** da exportação de matrículas audita (`MATRICULA_PREVER`), e a razão é
que ela **nomeia pessoas**: o teste `test_a_previa_sem_ninguem_nomeado_nao_polui_a_trilha` prende
exatamente essa fronteira.

Esta página não nomeia ninguém (`FR-584`), e é agregada por construção. Auditá-la produziria trilha
sem fato — o oposto do que o Princípio III pede.

---

## R-010 — Como o orçamento de consulta é medido

**Decisão**: teste em `tests/performance/test_visao_institucional.py`, com
`CaptureQueriesContext`, comparando a contagem entre **3** e **60** Editais no recorte, e afirmando
**igualdade** — e não um teto.

**Racional**. `tests/performance/test_public_queries.py` estabelece a doutrina: *"contagem de
queries é determinística e detecta a degradação que importa — o custo crescer com o histórico —
enquanto tempo de parede em suíte de teste é ruidoso"*. Um teto absoluto envelhece a cada consulta
legítima acrescentada; a **igualdade entre dois tamanhos** prende a propriedade que `SC-209`
descreve, e continua valendo quando o número absoluto mudar.

O segundo teste (`T-21`) conta **snapshots abertos**, e não consultas: é o que prova `FR-598` e
`FR-599`, e a contagem de consultas sozinha não o pegaria.

---

## Orçamento de consulta projetado

| # | Leitura | Cresce com Editais? |
|---|---|---|
| 0 | anos disponíveis — `DISTINCT Edital.year` no escopo | não |
| 1 | Processos e Editais do recorte, com `prefetch` | não |
| 2–3 | versão vigente por Edital (`versoes_vigentes`) | não |
| 4 | inscrições por Edital, Perfil e estado | não |

**Quatro leituras e uma contagem auxiliar** — cinco consultas, constantes. Os indicadores registrados
acrescentariam três agregações, também constantes: a estrutura já está decidida (`D-011`).

