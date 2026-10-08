# Research: As atribuições idênticas saem uma vez no documento do Edital

**Feature**: [spec.md](spec.md) · **Plano**: [plan.md](plan.md) · **Data**: 2026-10-08

As decisões desta feature nascem em `D-001`. Decisão de outra feature é citada pela feature e pelo
número dela, por extenso. Os sete ajustes do responsável pelo produto, que a spec cita como 1º a 7º,
não são repetidos aqui: estas são as decisões de **como**, tomadas dentro deles.

---

## O que foi conferido antes de decidir

Conferido sobre a `main` `d7d3fe0b`, na auditoria de 08/10/2026.

| Pergunta | Onde se respondeu | Resposta |
|---|---|---|
| O que são as atribuições? | `editais/models/perfis.py`, `PerfilVaga.duties` | Texto livre do Perfil. Sem entidade, sem identificador por item, sem relação entre Perfis. |
| "Associar a outro Perfil" liga os textos? | `editais/domain/duplicacao.py` (cópia profunda); teste da `043` que classifica `duties` como copiado igual | Não. São cópias independentes. |
| Quem compõe o documento? | `publicacoes/infrastructure/pdf.py`, `render_edital_pdf` | Uma função só, chamada pela prévia (`interface/views.py::previa_documento`), pela Publicação (`publish_edital.py`) e pela Retificação (`retificacoes.py`). |
| Onde as atribuições são impressas? | `pdf.py::_perfis`, o bloco sob `if perfil.get("duties")` | Rótulo "Atribuições" em negrito (recuo 18) e um parágrafo justificado por linha do texto (recuo 32). |
| Como o texto vira parágrafos? | `pdf.py::_paragrafos` | Qualquer sequência de quebras de linha separa; cada bloco é aparado; bloco vazio é descartado. |
| Como o parágrafo vira linhas? | `pdf.py::_quebrar` | Por `str.split()`: a quantidade de espaço entre palavras some. |
| De onde vem o número da subseção do Perfil? | `pdf.py::_perfis`, `f"{secao}.{ordem}"` | Da posição do Perfil, que o snapshot ordena por código. Só o documento conhece esse número. |
| E o das seções e o das tabelas? | `pdf.py::numeracao` (lida também pelas telas) e `pdf.py::_Numerador` | Seções contam só as de topo; tabelas contam cada `legenda()`. Uma subseção sem tabela não move nenhum dos dois. |
| O documento publicado é regerado? | `publicacoes/models.py::DocumentoPublicado` (append-only); `seguranca/papeis.py` | Não. Os bytes ficam guardados; gatilho e privilégio ausente impedem a alteração. |
| A Retificação usa o renderizador do dia? | `retificacoes.py`, `render_edital_pdf(content, …, consolidacao=…)` | Sim: compõe o documento consolidado inteiro, a partir do conteúdo-base com as mudanças. |
| O que a fixture byte a byte guarda? | `tests/contract/fixtures/snapshot_publicado.json` | Um Perfil só. Esta feature não a alcança. |
| Já existe precedente de comparar pelo que se publica? | `pdf.py::_publica_a_mesma_norma`, da `032` | Sim: o método do sorteio é comparado campo a campo pelo valor impresso, e não pelo dicionário cru. |

---

## D-001 — A consolidação mora em `_perfis`, com um auxiliar puro no mesmo módulo

**Decisão**: `_perfis` passa a perguntar, antes de compor, quais Perfis se agrupam; a pergunta é uma
função pura do módulo do renderizador, que recebe a lista de Perfis do snapshot e devolve os grupos.

**Por quê**: a prévia, a Publicação e a Retificação já passam pela mesma função; pôr a regra em
qualquer outro lugar criaria o segundo caminho que o FR-1194 proíbe. A função pura deixa a regra de
identidade testável sem compor PDF.

**Alternativas descartadas**:
- *Serviço ou módulo de domínio novo* — não há regra de domínio: o cadastro, o conteúdo e o portal
  ficam como estão (FR-1195). Seria uma camada para uma pergunta de composição.
- *Gravar o grupo no snapshot* — mudaria o conteúdo canônico e a impressão digital da versão,
  contra o FR-1195 e o 2º ajuste.

---

## D-002 — A chave de identidade é a lista de parágrafos, cada um reduzido às suas palavras

**Decisão**: a chave de um Perfil é a tupla dos parágrafos de `_paragrafos(duties)`, cada parágrafo
reduzido a `" ".join(parágrafo.split())`. Perfis com a mesma chave não vazia formam grupo.

**Por quê**: é exatamente a estrutura que o documento imprime — `_paragrafos` define as fronteiras e
`_quebrar` descarta o espaço —, e por isso é o que o FR-1187 descreve: a quebra de linha conta
(é fronteira), o espaço e a quantidade de linhas em branco não. Reusar `_paragrafos` em vez de
reescrever a separação garante que chave e impressão nunca divergem.

**Emenda de 08/10/2026, ao integrar a correção do "?" (#265).** A primeira versão comparava o texto
registrado, antes de qualquer codificação, para que dois símbolos que o documento trocava pelo mesmo
"?" dessem chaves diferentes. O #265 passou a normalizar o snapshot antes de compor — marcadores
cheios viram `•`, invisíveis somem, o texto é composto em NFC — e a recusar na publicação o que não
normaliza. Integrada a `main`, o documento agrupava `●` com `•` e a função testada não: as duas
divergiam. O responsável pelo produto escolheu a comparação normalizada, e a chave passou a aplicar
`grafia.normalizar` ela mesma, para valer igual em qualquer caminho de chamada.

**Alternativas descartadas**:
- *Comparar a string crua* — dois Perfis colados em momentos diferentes divergem num espaço final
  que ninguém vê, e a consolidação não dispararia no caso real.
- *Normalizar caixa, acento ou pontuação* — juntaria textos que o leitor vê diferentes.
- *Ordenar os parágrafos* — o sistema não tem como saber que a ordem é indiferente (spec, casos-limite).
- *Comparar o que sai impresso* — descartada na primeira versão, porque juntaria textos distintos
  que perderam o mesmo símbolo para o "?". Com o #265 essa perda não existe mais, e a normalizada
  passou a ser a decisão (emenda acima).

---

## D-003 — Os grupos e as subseções seguem a ordem do primeiro Perfil de cada grupo

**Decisão**: os grupos são produzidos percorrendo os Perfis na ordem do snapshot; cada grupo nasce
no primeiro Perfil que o tem, e as subseções comuns saem nessa ordem, numeradas de `{s}.{N+1}` em
diante. O título nomeia os códigos na ordem do documento, enumerados como `_enumerar` enumera —
*"A, B e C"* —, mas montado em linhas que quebram entre códigos (`_linhas_sem_partir`), e com todos
os códigos entre aspas quando algum contém o separador da enumeração (`_codigos_enumerados`).

**Emenda da revisão de código, 08/10/2026.** A primeira versão passava o título inteiro a
`escrever`, e `_quebrar` partia "ADS - P06" em "ADS" e "- P06"; o espaço inseparável não serve,
porque `str.split` também divide nele. E um código como "Tutor e Mediador" fazia o título se ler
como três Perfis. As duas correções ficam no título, e não em `_quebrar`: mudar a quebra de todo o
documento mudaria a paginação de todo Edital que tem espaço inseparável colado do editor de texto.

**Por quê**: é determinístico (o snapshot já ordena por código) e é a ordem em que o leitor
encontra as remissões. `_enumerar` é a enumeração que o documento já usa.

---

## D-004 — A remissão é um par rótulo-valor, no lugar do bloco

**Decisão**: o Perfil agrupado imprime, onde ficava o bloco de atribuições, o par
**"Atribuições:"** *as descritas no item {s}.{N+k}.*, com `_pares` — o mesmo desenho de
"Localidade:" e "Cadastro reserva:" no Edital de um Perfil.

**Por quê**: o rótulo continua onde o candidato o procura, em negrito como hoje; a remissão é um
valor de uma linha, e `_pares` é a forma que o documento já usa para isso. Um cabeçalho seguido de
uma linha solta gastaria duas linhas para dizer uma coisa.

---

## D-005 — A subseção comum é um bloco coeso, com o desenho da subseção de Perfil

**Decisão**: título em negrito, com o corpo e o espaçamento do título de Perfil
(`f"{s}.{N+k} Atribuições comuns aos Perfis …"`, `junto=True`); os parágrafos com o desenho dos
parágrafos de atribuições de hoje (corpo de texto, justificados), com recuo 18, que é o do conteúdo
direto de uma subseção. O conjunto vai num `composicao.bloco()` **coeso** — o padrão —, com cada
parágrafo num `bloco()` próprio dentro dele.

**Por quê**: é o que o FR-1193 pede, e o que a paginação já sabe fazer. Em `Composicao.paginar`, só
o bloco coeso salta de página: `if coeso and not cabe_aqui and altura <= util` abre página nova
quando ele não cabe no que resta mas cabe numa página inteira; quando não cabe nem numa página
inteira, a cascata desce para os blocos de dentro — os parágrafos —, e o último degrau quebra entre
linhas. As três frases do FR-1193 saem dessa linha, sem regra nova. O título com `junto=True`
garante que ele nunca fica sozinho no rodapé (FR-022 da `008`). Recuo 32 era o de quem está abaixo
de um rótulo de sub-bloco; aqui o rótulo é o próprio título.

**Alternativa descartada**: `bloco(coeso=False)`, como abre o Perfil. Um bloco não coeso começa onde
estiver e nunca salta inteiro, e a subseção comum começaria no rodapé de uma página mesmo cabendo
inteira na seguinte — contra o FR-1193, e a T015 nasceria vermelha.

**Registro, fora do escopo**: o próprio Perfil abre com `bloco(coeso=False)` desde a `008`
(`_perfis`), e por isso, no código de hoje, só o primeiro sub-bloco dele — título e descrição — salta
de página; o FR-020 da `008` pede que o Perfil inteiro salte quando couber na página seguinte.
Nenhum artefato da `008` registra essa troca. Não é desta feature mexer nisso: fica como achado para
o responsável pelo produto.

---

## D-006 — O teste de integridade reconstrói pelo documento, e não pela função de agrupar

**Decisão**: o teste do FR-1191 extrai o texto do PDF composto e, para cada Perfil do snapshot,
acha a subseção dele, lê ou o bloco próprio ou o número da remissão, segue até a subseção comum e
compara os parágrafos com a chave de D-002 do snapshot. Os cenários usam só caracteres que o
documento representa, para que o defeito de codificação, tratado fora (1º ajuste), não entre no
resultado.

**Por quê**: testar só a função de agrupar provaria a regra, e não o documento. O que o FR-1191
afirma é sobre o artefato que o candidato lê; a reconstrução pelo PDF é o que demonstra a cadeia
"versão → documento" que a Constituição pede.

**Como as fronteiras de parágrafo saem do PDF**: os cenários de integridade usam itens que cabem
numa linha cada um, de modo que cada linha desenhada é um parágrafo; um cenário à parte, com um item
de várias linhas, confere a sequência de palavras. Depender do espaçamento justificado para achar o
fim do parágrafo tornaria o teste frágil a uma mudança de métrica que não é desta feature.

---

## D-007 — A Retificação é provada de ponta a ponta numa integração, e o resto em unidade

**Decisão**: um teste de integração publica um Edital de três Perfis de mesmo texto (pelo `draft=`
de `publish_original`), retifica as atribuições de um deles e confere: o documento original com os
mesmos bytes, o documento da Retificação agrupando só dois, e a alteração nomeando o Perfil e o
campo. Os demais casos de Retificação (Perfil acrescentado, grupo que se desfaz) são de unidade,
compondo o conteúdo depois da mudança.

**Por quê**: o único comportamento que só existe ponta a ponta é "o guardado não muda e o novo sai
reagrupado"; o resto é a mesma função de composição sobre outro conteúdo. Os casos transacionais
são o custo caro da suíte (ver as instruções do repositório), e um basta.
