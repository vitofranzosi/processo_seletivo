# Coleções que crescem: N formulários abertos contra a visão do conjunto

**Data**: 2026-09-29 · **Natureza**: análise de arquitetura de interação — nada foi implementado.
**Base**: a branch da `051` (`claude/nova-051-edital-patterns-499aa7`, PR 226), porque é ela que tem
a tela da captura; o PR foi mergeado no mesmo dia, e as medições valem para a `main`. As medições são do sistema rodando, num banco próprio
(`ps_ux_colecoes`), com o Edital em elaboração do `seed_demo` multiplicado pelo mesmo POST da etapa.

---

## 1. Resumo executivo

A hipótese se confirma, e o problema é maior do que a captura mostra.

- **A etapa Perfis cresce 1.898 px por Perfil** a 1280 px de largura, ~2,1 telas cada. Com 7 Perfis a
  página tem 14.509 px e 212 controles visíveis; com 16, 482; com 26, 782. O primeiro Perfil começa a
  912 px, **abaixo da dobra**: quem abre a etapa não vê Perfil nenhum.
- **O cartão não diz de quem é.** A legenda de todos é *"Perfil de Vaga"*; o código e a localidade
  moram no `value` de um `input`, que a busca do navegador não encontra e o leitor de tela, navegando
  por grupos, anuncia sete vezes igual.
- **Achado fora do escopo visual: acima de 26 Perfis a etapa não grava.** Com a forma do Edital de
  demonstração (2 Modalidades por Perfil, 37 campos cada), o 27º Perfil faz o envio passar de mil
  campos e o Django recusa com **400** antes de chegar à view (`DATA_UPLOAD_MAX_NUMBER_FIELDS`). O
  multicampi que a própria `051` projeta tem 66 Perfis. Nenhuma solução de apresentação resolve
  isto; está registrado em [achado-etapa-perfis-recusa-acima-de-mil-campos.md](achado-etapa-perfis-recusa-acima-de-mil-campos.md).
- **Recomendação**: tabela resumida + **um** editor visível, **sobre o mesmo formulário**. Todos os
  Perfis continuam no DOM e continuam sendo enviados; só um fica visível. É isso que torna a mudança
  pura camada de interação: não abre caminho novo de gravação (o que a `D-001` da `051`, a `UX-020`
  da `027` e a `FR-638` da `043` recusam), não toca o `replace_draft` e preserva os gestos da `051`
  sem reescrevê-los.
- **Uma consequência muda a proposta original**: como trocar de Perfil não perde nada, *"Salvar e
  editar próximo"* vira **"Próximo Perfil"**, sem ida ao servidor. A gravação por registro é um
  modelo que este sistema não tem, de propósito.
- **Mínimo viável**: a legenda com o código (vale sem JavaScript, é uma linha), a tabela, o editor
  único e o tratamento dos campos inválidos escondidos. Merece spec própria, sobre a `main` que já
  tem a `051` — que mexe nos mesmos três templates.
- **Não é regra universal.** O problema aparece quando o item tem subcoleção e a etapa grava o
  conjunto inteiro: Perfis e Classificação. O Cronograma já é quase uma tabela editável (216 px por
  Evento, contra 1.898 por Perfil) e pede densidade, não mestre-detalhe; Etapas, Anexos, Conteúdo e a
  Retificação ficam como estão (§10).

---

## 2. Diagnóstico da interface atual

### O que a etapa renderiza

A etapa é **um formulário** (`compor_perfis.html`) que contém, nesta ordem: a prévia do gesto (quando
pedida), a ajuda da etapa em `<details>`, o contador, o controle *"Declarado uma vez para todos os
Perfis"* (`051`, só com mais de um Perfil), o botão *"Preencher pelo percentual as linhas vazias do
quadro"*, a lista `#perfis` com um `_perfil.html` por Perfil, *"Acrescentar Perfil"* e a navegação
(*Salvar*, *Avançar*), **que não é fixa**: fica depois do último Perfil.

Cada `_perfil.html` é um `fieldset` com:

| Bloco | Altura medida | Controles |
|---|---:|---|
| Código, Denominação, Localidade | 76 px | 3 |
| Descrição, Carga horária, Remuneração | 76 px | 3 |
| Atribuições, Requisitos (textareas) | 119 px | 2 |
| Vagas imediatas, Cadastro reserva (3 rádios + limite) | 201 px | 5 |
| Modalidades (cada uma 239 px, 6 controles + 2 botões) + ampla, reversão, forma de convocação | 792 px (com 2) | 12 + 3 |
| Quadro de vagas (só com lista reservada) | 331 px | 1 por lista |
| Fatos exigidos | 66 px | 3 por fato |
| Duplicar (recolhido) + Remover | 58 px | 2 |
| **Total por Perfil** | **1.898 px** | **~31 visíveis, 37 campos enviados** |

### Como a página cresce

Medido pelo mesmo POST da tela, a 1280×900 no navegador e pelo `Client` do Django:

| Perfis | Controles visíveis | Botões | HTML | Altura | Campos enviados |
|---:|---:|---:|---:|---:|---:|
| 1 | 30 | 11 | 107 KiB | ~3,1 mil px (proj.) | 39 |
| 3 | 92 | 31 | 144 KiB | — | — |
| 7 | 212 | 63 | 215 KiB | **14.509 px** | 261 |
| 16 | 482 | 135 | 376 KiB | ~31 mil px (proj.) | 594 |
| 26 | 782 | 215 | 554 KiB | ~50 mil px (proj.) | 964 |
| 27 | — | — | — | — | **1.001 → 400** |

A fórmula é linear e sem desconto: `altura ≈ 1,2 mil + 1,9 mil·N` px, `campos ≈ 2 + 37·N` (mais 8 por
Modalidade e 3 por linha de quadro a mais). Nada na página é compartilhado entre Perfis além do que a
`030` e a `051` já tiraram do cartão (as ajudas e o controle do Edital).

### O que se repete, e o que precisa ficar visível

**Repete-se sem diferença entre irmãos**, no caso típico de polos (28/2026): Denominação, Descrição,
Carga horária, Remuneração, Atribuições, Requisitos, as Modalidades inteiras (código, nome,
percentual, fundamento, versão, arredondamento), ampla, reversão e forma de convocação. É por isso que
a `043` criou o duplicar e a `051` o aplicar a todos.

**Varia de propósito**: Código, Localidade, Vagas imediatas, cadastro reserva e o quadro. É o que o
operador compara, e é o que hoje ele só vê rolando duas telas por Perfil.

**Varia por erro**, e é o que a tela mais deveria mostrar: a Modalidade esquecida numa cópia (o
`G-001` da `043`, que motivou metade da `051`), o percentual diferente num polo, a forma de convocação
que falta num Perfil que corta (o impeditivo `FR-943`). O controle do Edital diz *"Varia entre os
Perfis"*, mas não diz **quais** — a resposta está espalhada em 14 mil pixels.

### Análise pelos critérios pedidos

- **Carga cognitiva.** 212 controles simultâneos para 7 Perfis, sete deles com o mesmo rótulo
  *"Código"*. Nenhum sinal visual separa o que é igual em todos do que é particular.
- **Information scent.** Nulo no nível do cartão: legenda genérica, nenhum resumo. A Classificação já
  resolveu isto para ela (a legenda é `{{ code }} — {{ name }}`); os Perfis, não.
- **Scanning.** Impossível por coluna: vagas do polo 1 e do polo 5 estão a 7.600 px uma da outra.
- **Orientação espacial.** Sem âncora por Perfil; as pendências da etapa apontam para
  `#perfis-titulo`, o topo, mesmo quando o caminho do achado (`/profiles/id=…/…`) já diz qual Perfil é.
- **Progressive disclosure.** Existe dentro do marco (`details.bloco-do-marco` com
  `resumo-do-bloco`, da `030`) e na ajuda, mas não no nível do item da coleção.
- **Prevenção de erros.** A validação nativa foca o campo inválido, mas o operador que corrige o
  Perfil 6 precisa rolar 12 mil px até *Salvar*; e *"Remover este Perfil"* aparece sete vezes, a
  poucos pixels do *Duplicar* do mesmo cartão.
- **Usuário frequente.** Nenhum atalho para "ir ao Perfil X"; a busca do navegador não acha o código.
- **Escala.** 1 Perfil: bom. 2–3 (o 78/2026, provável primeiro Edital do piloto): tolerável. 7:
  ruim. 16 (140/2025): inviável como visão. 27+: não grava.

### O que já é bom e não pode se perder

A densidade **dentro** do cartão é resultado de trabalho medido (os comentários de `_perfil.html`
registram 1.098 px → bandas emparelhadas); as ajudas saíram do cartão para a etapa (`030`, `FR-428`);
o duplicar pede só Código e Localidade; o quadro é oferecido e só a quantidade se digita. O problema
não está no cartão, e sim em existirem N deles abertos ao mesmo tempo.

---

## 3. Problema de escalabilidade encontrado

Há dois, com a mesma raiz e soluções diferentes.

**Visual — a página é a soma dos cartões.** O custo de *entender* a coleção cresce com N vezes o
tamanho do cartão, quando deveria crescer com N vezes o tamanho de **uma linha**. Esse é o que a
hipótese resolve.

**De transporte — o envio é a soma dos campos.** A etapa grava a coleção inteira a cada POST, por
decisão (o `replace_draft` substitui o rascunho, e tela à parte apagaria o que outra gravou — `UX-020`
da `027`). Isso tem um teto que ninguém tinha medido nesta etapa: **mil campos**. O mesmo teto já
derrubou a confirmação da distribuição em 27/09 e foi contornado lá (`views.py`, *"As identidades
viajam num campo só"*). Aqui ele aparece com 27 Perfis de 2 Modalidades; com 3 Modalidades e quadro,
por volta de 18. Na Classificação, cada marco manda ~28 campos, mais 5 por critério: 16 Perfis com
marco de 3 critérios (o 140/2025) ficam perto do teto, e dois marcos por Perfil o passam.

**Esconder cartões não diminui o envio**, e é por isso que o segundo problema não pode entrar
escondido numa spec de UX: a correção dele (subir o limite, serializar a coleção num campo, ou gravar
por item) é decisão de outra natureza, e a terceira reabre `D-001`, `UX-020` e `FR-638`. É registro,
não escopo desta proposta: [achado-etapa-perfis-recusa-acima-de-mil-campos.md](achado-etapa-perfis-recusa-acima-de-mil-campos.md).

---

## 4. Comparação das alternativas

O critério principal é o fluxo real: compor N Perfis quase iguais, corrigir um, conferir o conjunto
antes de avançar, e voltar depois de uma recusa ou de uma prévia da `051`.

### A. Formulários permanentemente abertos (hoje)

- **A favor**: zero cliques para chegar a um campo; sem JavaScript; a busca do navegador acha rótulos;
  o formulário é um só e visível, o que casa com a gravação por substituição; ótimo com 1–2 Perfis.
- **Contra**: tudo do §2. A visão do conjunto não existe; a comparação é por memória.
- **Melhor quando**: N ≤ 2.

### B. Accordion — `<details>` por Perfil, com resumo no `<summary>`

Variante forte: `<details name="perfis">` (acordeão exclusivo nativo, Chrome 120+, Safari 17.2+,
Firefox 130+) entrega "zero ou um aberto" sem uma linha de script.

- **A favor**: padrão já usado no repositório (`bloco-do-marco`, com `resumo-do-bloco`); funciona sem
  JS; o editor abre **no lugar** da linha, sem salto espacial; acessível por padrão.
- **Contra**: o `<summary>` é um botão, não uma linha de tabela — sem cabeçalhos de coluna, a
  comparação vira leitura de frases (*"P03, Polo 3, 40 vagas, AC PPI PcD…"*), e o leitor de tela
  perde a navegação por coluna. Com um aberto, os demais resumos são empurrados 1,9 mil px para baixo.
  E muda contratos do htmx: *Duplicar* insere `afterend` do `fieldset` — cairia **dentro** do
  `<details>` de origem; *Remover* troca o `fieldset` e deixaria o `<details>` vazio; *Acrescentar*
  precisaria devolver o invólucro.
- **Melhor quando**: itens sem nada a comparar entre si (§10, documentos e seções).

### C. Tabela + editor único

- **A favor**: a tabela é a visão do conjunto — cabeçalhos, leitura por coluna, anomalia salta aos
  olhos (a linha sem `PcD` entre sete com `PcD`). O editor é o cartão de hoje, intacto. Se o editor
  for o próprio `fieldset` do Perfil, apenas com os outros escondidos, **nenhum contrato do htmx
  muda**: *Duplicar* continua inserindo depois da origem, *Remover* continua trocando o `fieldset`,
  e a tabela se atualiza observando `#perfis`, como o `assistente.js` já faz com o contador.
- **Contra**: exige JavaScript (sem ele, a página continua como hoje — degradação aceitável); um
  clique a mais para chegar a um campo; salto entre a linha e o editor quando a tabela é longa;
  campo inválido escondido precisa de tratamento (§7).
- **Melhor quando**: N ≥ 3 e os itens se comparam — é o caso.

### D. Tabela com edição na linha

- **A favor**: imbatível para campos simples e homogêneos editados em sequência.
- **Contra**: o Perfil tem textareas, rádios com campo dependente, duas subcoleções (Modalidades,
  fatos) e uma terceira derivada (quadro). Não cabe numa linha, e metade dele numa linha e metade num
  editor dá dois lugares para o mesmo campo.
- **Útil como complemento** (COULD): *Vagas imediatas* editável na própria linha, que é o número que
  muda de polo para polo.
- **Melhor quando**: Cronograma (§9).

### E. Mestre-detalhe lado a lado (lista estreita fixa + editor à direita)

- **A favor**: elimina o salto espacial; é o padrão clássico de clientes de e-mail.
- **Contra**: a 1280 px o editor perde ~300 px, e as bandas do cartão foram calibradas para a largura
  inteira (os comentários registram o teto de `68ch`); a lista estreita só cabe código e situação — e
  aí se perde a comparação, que é o ganho principal. No celular, degenera em C.
- **Veredito**: não compensa o custo agora.

### Quadro-resumo

| | A | B | C | D | E |
|---|---|---|---|---|---|
| Visão do conjunto | não | frases | **tabela** | tabela | lista curta |
| Comparar por coluna | não | não | **sim** | sim | não |
| Cliques até um campo | 0 | 1 | 1 | 0–1 | 1 |
| Salto espacial | rolagem longa | nenhum | tabela→editor | nenhum | nenhum |
| Sem JS | sim | sim | como hoje | não | não |
| Contratos htmx tocados | — | 3 | **0** | vários | 0 |
| Serve ao Perfil | até 2 | aceitável | **sim** | não | parcial |

---

## 5. Recomendação para Perfis de Vaga

**C, sobre o mesmo formulário.** A tabela lê o formulário; o editor é o `fieldset` de hoje; esconder é
o atributo `hidden`; o *Salvar* é o de sempre.

```
Perfis de Vaga                                                       Edital 76/2027
──────────────────────────────────────────────────────────────────────────────────────
▸ Como preencher estes campos

Declarado uma vez para todos os Perfis
  Como a convocação é comunicada  [Varia entre os Perfis ▾]  (Conferir aplicação a todos os Perfis)
  Reverter vaga reservada…        [Não reverte          ▾]  (Conferir aplicação a todos os Perfis)

(Preencher pelo percentual as linhas vazias do quadro)

┌ 7 Perfis de Vaga ───────────────────────────────────────────────────────────────────┐
│ Código │ Localidade │ Vagas │ Reserva      │ Modalidades        │ Convocação │ Situação               │        │
├────────┼────────────┼──────:┼──────────────┼────────────────────┼────────────┼────────────────────────┼────────┤
│ P01    │ Serra      │    40 │ limitada · 6 │ PPI 25% · PcD 5%   │ publicação │ sem pendência          │ Editar │
│ P02    │ Viana      │    40 │ limitada · 6 │ PPI 25%            │ publicação │ ⚠ 1 pendência          │ Editar │
│ P03  ◆ │ Vitória    │    35 │ limitada · 6 │ PPI 25% · PcD 5%   │ —          │ em edição · alterado   │ Editar │
│ P04    │ Cariacica  │    40 │ limitada · 6 │ PPI 25% · PcD 5%   │ publicação │ sem pendência          │ Editar │
│ …                                                                                                        │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
(Acrescentar Perfil)

┌ Editando P03 — Vitória ───────────────────── (← P02  ·  P04 →)  (Voltar à lista) ┐
│  [o cartão de hoje, inteiro: identidade, textos, vagas, Modalidades com         │
│   "Aplicar aos demais Perfis (6)", ampla, reversão, convocação, quadro com a     │
│   sugestão do percentual, fatos, Duplicar este Perfil, Remover este Perfil]      │
└──────────────────────────────────────────────────────────────────────────────────┘

                                                   (Salvar)  (Avançar →)
```

Decisões de desenho embutidas no rascunho:

- **Com um Perfil só, não há tabela**: o editor aparece aberto, como hoje. É a mesma regra que a
  `051` usou para o controle do Edital (*"Só com mais de um Perfil — com um, o cartão já é o lugar"*).
  A tabela nasce no segundo Perfil.
- **Zero ou um editor**, como proposto, com três exceções em que um abre sozinho: Perfil recém-criado
  (por *Acrescentar* ou *Duplicar*), Perfil com recusa do servidor, e âncora na URL (`#perfil-…`,
  vinda de uma pendência).
- **Denominação fora da tabela**, e dentro do título do editor. Em Editais de polos ela é igual em
  todas as linhas, e é a Localidade que distingue. Onde a Denominação distingue (140/2025, cargos
  diferentes), ela substitui a Localidade na segunda coluna — a regra é mostrar o par que identifica,
  e isso se decide olhando se a coluna varia, não por configuração.
- **A ordem da tabela é a ordem do Edital**, e não se ordena por coluna: reordenar a vista sugeriria
  reordenar o documento.

---

## 6. Campos recomendados para a visão consolidada

Cada coluna precisa responder a uma das cinco perguntas: identificar, comparar, perceber diferença,
achar pendência, agir.

| Coluna | Pergunta | Por que merece o espaço |
|---|---|---|
| **Código** (cabeçalho da linha, `th scope="row"`) | identificar | É o que o Edital, a Revisão, a prévia da `051` e as pendências usam para nomear o Perfil. |
| **Localidade** (ou Denominação, a que variar) | identificar | Nos Editais de polos é o que o operador tem na cabeça ("o de Viana"). |
| **Vagas imediatas** | comparar | É o número que mais varia entre irmãos, e o que o documento publica em destaque. |
| **Cadastro reserva** | comparar | Três formas e um limite; errar a forma num Perfil é invisível hoje. Texto curto: *"não há"*, *"ilimitado"*, *"limitada · 6"*. |
| **Modalidades** (códigos e percentuais) | perceber diferença | É onde o `G-001` mora: a cópia sem `PcD` salta aos olhos entre sete com `PcD`. Não traz fundamento nem versão — isso é igual em todas, e o aplicar a todos o garante. |
| **Convocação** | perceber diferença | Explica o *"Varia entre os Perfis"* do controle do Edital, e é impeditivo quando falta (`FR-943`). |
| **Situação** | achar pendência | Texto, nunca só cor: *"sem pendência"*, *"2 pendências"*, *"campo inválido"*, *"alterado — não salvo"*, *"em edição"*. Três fontes, detalhadas abaixo. |
| **Ações** | agir | *Editar* (com o código em texto oculto: *"Editar P03"*). *Duplicar* e *Remover* ficam no editor na primeira versão. |

**Fora da tabela, deliberadamente**: Descrição, Carga horária, Remuneração, Atribuições, Requisitos
(texto longo, igual entre irmãos), fundamento e versão das Modalidades, arredondamento, fatos, a
reversão (vai à Situação só se divergir do controle do Edital) e o quadro (vai à Situação como
*"quadro a repartir"* quando a soma não fecha, porque a validação já diz).

**A Situação tem três fontes, e nenhuma é regra nova**:

1. **Pendências da publicação**, que já são calculadas para a etapa (`_pendencias_da_etapa`) e já
   trazem o caminho `/profiles/id=<uuid>/…`: basta atribuí-las à linha pelo `id`. Hoje elas apontam
   todas para o topo da etapa.
2. **Validade local** — o `:invalid` que o `validacao.js` e a validação nativa já produzem no
   `fieldset`.
3. **Alterado — não salvo** — comparação de cada controle com o `defaultValue`/`defaultChecked` que
   o próprio DOM guarda, sem estado paralelo.

As pendências vêm do que está **gravado**; se a linha também está *"alterada"*, as duas aparecem, e
é honesto: a pendência pode já ter sido resolvida no que ainda não foi salvo.

**Responsividade**: abaixo de ~720 px a tabela vira lista de blocos (cada linha, os pares *rótulo:
valor* empilhados), sem rolagem horizontal da página. O repositório já tem tabela de Perfis
(`tabela-de-perfis`, da `041`, na visão institucional) e cabeçalho fixo em tabela longa
(`.distribuicao`): as regras de estilo se estendem, não se inventam.

---

## 7. Fluxo de criação/edição proposto

### Editar um Perfil existente

1. **Selecionar** — *Editar* na linha. O `fieldset` daquele Perfil perde o `hidden`, os demais o
   ganham; a linha recebe `aria-current="true"` e o texto *"em edição"*; o foco vai ao título do
   editor (*"Editando P03 — Vitória"*, `tabindex="-1"`), e a página rola até ele.
2. **Editar** — o cartão de hoje, sem mudança. A linha da tabela acompanha o que se digita
   (Localidade, vagas, Modalidades), porque ela lê o formulário.
3. **Trocar de registro** — *P04 →*, ou *Editar* noutra linha. **Não há pergunta de "alterações não
   salvas"**: nada se perde, porque o `fieldset` que sai continua no formulário e continua sendo
   enviado. A linha que ficou para trás diz *"alterado — não salvo"*.
4. **Voltar à lista** — fecha o editor e devolve o foco ao *Editar* da linha de onde saiu (WCAG
   2.4.3, o mesmo cuidado do `assistente.js`).
5. **Salvar** — o *Salvar* de sempre, que grava **todos**. O redirecionamento volta com zero editores
   abertos e o *"Rascunho salvo"* de hoje; as linhas deixam de dizer *"alterado"*.
6. **Recusa** — o servidor devolve o formulário inteiro, como hoje; o editor abre no Perfil da
   primeira recusa (as recusas já chegam com âncora por campo, `recusa-perfil-3-…`), e a linha diz
   *"recusado"*.

Por isso **"Salvar e editar próximo" vira "Próximo"**. A proposta pressupunha gravação por registro;
aqui gravar é da etapa inteira, e ir ao próximo não precisa de servidor. O ganho é duplo: um clique
em vez de uma ida e volta, e nenhum risco de gravação parcial.

**Cancelar** um Perfil (voltar os campos ao gravado) é **COULD**, não MUST: para campos simples é
restaurar o `defaultValue`, mas Modalidade e fato acrescentados pelo htmx precisariam ser removidos, e
a Modalidade leva junto a linha do quadro (`junto=`). Na primeira versão, *Voltar à lista* não
descarta; descartar tudo continua sendo recarregar a etapa, que é o que o rascunho local já protege.

### Acrescentar um Perfil

*Acrescentar Perfil* (abaixo da tabela) → o fragmento de hoje entra em `#perfis` → a tabela ganha a
linha *"novo — não salvo"* e o editor abre nela, com foco no Código (o `assistente.js` já faz o foco).
Com o primeiro campo preenchido, a linha já se identifica. *Salvar* grava.

### Duplicar

No editor, como hoje: *Duplicar este Perfil* pede Código e Localidade, a cópia entra logo depois da
origem, e **o editor passa para a cópia**, com o aviso da `043` (*"Perfil P08 criado a partir de
P03…"*) no topo dele. Na tabela, a cópia aparece logo abaixo da origem, marcada *"nova — não salva"*.

### Remover

No editor, como hoje, com a confirmação do `remocao.js`. Removido, o editor fecha, a linha some, e o
foco vai à linha seguinte (ou à anterior, se era a última).

### Os gestos da `051`

- **Aplicar aos demais Perfis** (Modalidade, no editor) e **Conferir aplicação** (controle do Edital)
  são envios da etapa; a prévia volta no topo do formulário, acima da tabela, como hoje. Confirmada,
  a tela volta com zero editores e a tabela mostra o efeito — **a coluna Modalidades é o "depois" do
  gesto**, que hoje só se confere abrindo sete cartões.
- **Preencher pelo percentual** continua global; a frase de resultado nomeia os Perfis, e as linhas
  alcançadas dizem *"alterado — não salvo"*.

### Campo inválido num Perfil escondido — o ponto que decide se isto funciona

A validação nativa, ao enviar, tenta focar o primeiro campo inválido; se ele está num `fieldset`
com `hidden`, o navegador **não consegue focá-lo** e o envio fica bloqueado sem mensagem visível. É
o modo de falha mais provável da proposta, e o mais silencioso — e o projeto já o conhece: a `030`
o escreveu como princípio para os blocos do marco (`FR-414`–`FR-418`), e
`test_acessibilidade_da_classificacao.py` o guarda para campo em `<details>` fechado. Aqui o
esconderijo é aplicado por script, e o teste de template não o vê. O tratamento é um ouvinte de
`invalid` (em captura, no formulário) que abre o Perfil do campo antes de o navegador reportar —
MUST, com teste no navegador real (o shim de DOM dos testes de JavaScript não reproduz foco nem
`hidden`).

O mesmo vale para âncoras: link de pendência para `#perfil-3-reserveLimit` precisa abrir o Perfil 3.

### Atalhos

Nenhum atalho de teclado na primeira versão. *Anterior/Próximo* e o *Editar* por linha já dão ao
usuário frequente o caminho curto, e atalho sem descoberta é custo de manutenção sem usuário.

---

## 8. Compatibilidade com a SPEC 051

| Comportamento da `051` | Depende da apresentação? | Efeito da proposta |
|---|---|---|
| `D-001` — o gesto lê o **digitado** na etapa e grava pela gravação da etapa | Depende de **todos** os Perfis estarem no formulário | **Preservado porque** os cartões escondidos continuam no DOM e no envio. Um editor que carregasse só o Perfil aberto quebraria isto. |
| `FR-916`–`FR-919` — prévia com efeito por destino, identidade do que foi mostrado, recusa se divergir | Não | Intacto. A prévia continua no topo do formulário. |
| `FR-920` — atomicidade, mesma revisão esperada | Não | Intacto. |
| `FR-924`/`FR-925` — Modalidade pelo código, ampla junto | Não | Intacto; o botão continua no cartão da Modalidade (`UX-110`). |
| `FR-926` — controle do Edital; escolha não conferida impede *Salvar* | Não | Intacto; o aviso continua junto do controle, acima da tabela. |
| `FR-932`/`FR-933` — sugestão do quadro, arredondamento | Não | Intacto; a conta continua na linha do quadro, dentro do editor. |
| `UX-110` — o gesto no cartão da origem, com o alcance no rótulo | Sim | O cartão é o editor; o rótulo *"(6)"* continua certo. |
| `UX-111`/`UX-113` — prévia lista destinos por código e denominação | Não | Intacto; e passa a ter a tabela como referência visual do conjunto. |
| `FR-937`/`FR-428` da `030` — nenhuma ajuda visível no cartão | Sim | Respeitado: a Situação é da **tabela**, não do cartão; nada se imprime no editor. |
| Duplicar da `043` (`FR-636`–`FR-650`) | Sim, no ponto de inserção | Intacto: `afterend` do `fieldset` continua certo, porque o editor é o `fieldset`. |
| Rascunho local (`rascunho.js`, `RC-08`) | Lista `#perfis`, item `.perfil` | Intacto: a lista e os itens são os mesmos; restaurar continua pelo servidor. |

**Pode ser feita como evolução de UX sem reabrir decisão de domínio?** Sim, com uma condição: o editor
ser uma **vista** sobre o formulário, e não um formulário. Qualquer variante que grave por Perfil
reabre `D-001` da `051`, `UX-020` da `027` e `FR-638` da `043`, e deixa de ser de UX.

**Risco de regressão operacional** — ver §11. O mais sério é o campo inválido escondido; o mais
provável, o clique a mais para quem compõe um Edital de 2 Perfis, que a regra *"a tabela nasce no
segundo Perfil"* só atenua.

**Contra a falsa melhoria**: a tabela não pode esconder ação que hoje custa zero cliques e que o
operador faz em série. A única candidata é digitar *Vagas imediatas* de polo em polo — por isso a
edição dessa coluna na linha fica registrada como COULD, a medir no roteiro antes de decidir.

---

## 9. Aplicabilidade ao cronograma

**O Cronograma já é quase uma tabela editável, e não pede mestre-detalhe.** Cada Evento tem cinco
campos visíveis (tipo, descrição, local, início, fim) numa banda só — e `test_medida_dos_campos`
prende isso —, mais ↑/↓/remover. Medido: **216 px por Evento**, 3 Eventos em 1,8 mil px de página; o
maior Cronograma citado nas specs (18 Eventos) daria ~3,9 mil px. É um nono do custo por item do
Perfil.

O que sobra ali é **densidade**, não arquitetura: dos 216 px, a maior parte é a legenda (*"Evento do
Cronograma 1 de 3"*), os cinco rótulos repetidos em cada linha e a linha de ações. Numa tabela de
verdade — rótulos como cabeçalho de coluna, e por linha só em texto oculto ligado por
`aria-labelledby` —, o Evento caberia em ~50 px, e os 18 Eventos numa tela e meia. A edição continua
na linha, que é o padrão certo para item simples, homogêneo e editado em sequência (datas).

Portanto: o princípio (*"coleção não é N formulários"*) vale; o componente, não. Cronograma é
**B — tabela editável**, de prioridade menor, e a mudança é de marcação e folha de estilo, sem
script novo. O cuidado a medir antes é a ordenação: o `ordenacao.js` reescreve a legenda *"N de M"*,
que numa tabela vira o número da linha.

---

## 10. Outras telas com o mesmo problema

Medido no navegador com o Edital de demonstração (7 Perfis) e contado nos templates. *Cresce com*
é o que multiplica o tamanho da página.

| Tela | Natureza do item | Problema atual | Padrão recomendado | Prioridade |
|---|---|---|---|---|
| **Composição · Perfis de Vaga** | Complexo: 13 campos, 3 subcoleções (Modalidades, quadro, fatos), ~1,9 mil px | Página linear em N; sem visão do conjunto; legenda genérica; *Salvar* a 14 mil px; **400 acima de 26 Perfis** | **A — mestre-detalhe** | **P1** |
| **Composição · Classificação** | Complexo: marco por Perfil (~29 controles, ~1,1 mil px), critérios aninhados; `details` internos já resumem Recurso, Sorteio e Corte | O mesmo dos Perfis, com N·K; o 051 aplica marco a todos e o "depois" só se vê abrindo N cartões; sem rascunho local | **A — mestre-detalhe**, linha por Perfil: marcos, forma da ordem, corte, critérios, recurso, origem (*"aplicado de P01"*, já calculada para a Revisão) | **P1**, logo depois dos Perfis e pelo mesmo script |
| **Composição · Cronograma** | Simples, homogêneo: 5 campos numa banda, 216 px | Rótulos e legenda repetidos por linha | **B — tabela editável** (§9) | P2 |
| **Composição · Inscrição (Documentos exigidos)** | Médio: 7 campos, 334 px; o seletor de Modalidade lista **todo Perfil × toda Modalidade** (16 opções com 7 Perfis; ~70 no 140/2025), em cada documento | Página cresce pouco (D ~3–12); o problema é o seletor, que escala em N·M por documento | **C — progressive disclosure** leve: manter a linha; o seletor agrupado por Perfil (`optgroup`) é o ganho real | P3 |
| **Composição · Etapas de Avaliação** | Médio: 13 campos com revelação por forma, ~390–460 px; tipicamente 2–4 | Nenhum relevante em escala real | **D — manter** | — |
| **Composição · Anexos** | Arquivo + rótulo; cada ação é um POST próprio | Nenhum: já é por item | **D — manter** | — |
| **Composição · Conteúdo** | Seções de texto, N fixo (≤ 12, do catálogo) | Não cresce com o Edital | **D — manter** | — |
| **Retificação** | Flat: até ~60 cartões (Perfil, Modalidade, linha, fato, marco, critério, Evento) | Grande, mas já tem índice por seção, filtro por nome, *"só o que eu mudei"* e a tabela *"O que vai mudar"* | **D — manter**; reavaliar junto da US5 da `051` (aplicar a todos na Retificação), que muda o fluxo dali | P3 |
| **Comissão, Convocação, Sorteio, Distribuição** | Ação por item (POST próprio, `details` com formulário pequeno) ou tabela com seleção | Já são lista + ação | **D — manter** | — |
| **Portal do candidato** | Documentos por linha com envio próprio; fatos da inscrição | Nenhum editor completo repetido | **D — manter** | — |

**Duas leituras transversais.**

1. **O problema tem forma, e não é "coleção"**: aparece quando o item é **complexo e tem subcoleção**
   (Perfil com Modalidades; marco com critérios) e o conjunto **grava inteiro** numa etapa. Cronograma
   e Etapas são coleções e não têm o problema; Anexos grava por item e também não. A regra de
   projeto que sai daqui é: *item com subcoleção, em coleção que passa de três, se apresenta por
   resumo e se edita um de cada vez*. Não é "tudo vira tabela".
2. **O "esconder e continuar enviando" já existe em produção.** O `retificacao.js` filtra até sessenta
   cartões do mesmo formulário com `linha.hidden` e continua enviando todos. A proposta não inventa
   mecanismo: reusa um que já passou por percurso — e herda a mesma obrigação com campo obrigatório
   escondido, que a `030` escreveu como princípio (`FR-414`–`FR-418`,
   `test_acessibilidade_da_classificacao.py`: *"campo `required` invisível é submissão que o navegador
   recusa sem conseguir mostrar o que falta"*).

**O que reusar, e não reinventar**: a tabela de Perfis da visão institucional (`tabela-de-perfis`, da
`041`) para a marcação e a folha; o `resumo-do-bloco` do marco para o texto do resumo; o agrupamento
de marcos com divergência da Revisão (`revisao._marcos_agrupados`) para a coluna *origem* da
Classificação; o `MutationObserver` do `assistente.js` para manter a tabela em dia; o `hidden` do
`retificacao.js`. Nenhuma biblioteca nova, nenhum componente genérico: o mesmo script serve às duas
telas **A** por atributos `data-`, e só se extrai quando a segunda tela entrar.

**Observações laterais** (não verificadas a fundo; registro, não escopo):

- `forms._modalidades` lê `modalidade-*-description`, e `_modalidade.html` não desenha esse campo nem
  o leva oculto. Se uma Modalidade chega ao rascunho com descrição (pela API), gravar a etapa Perfis
  pode apagá-la — é a mesma classe de perda do `replace_draft`, que apaga o que não é reenviado. Não conferido.
- A Classificação não tem `data-rascunho`: o rascunho local, que protege Perfis, Cronograma, Etapas e
  Inscrição, não protege a etapa de cartões mais longos.

---

## 11. Riscos de regressão

| Risco | Como aparece | Mitigação |
|---|---|---|
| **Campo inválido escondido** | *Salvar* não faz nada, sem mensagem — o defeito que a `030` já pagou uma vez (`FR-414`) | Ouvinte de `invalid` que abre o Perfil; teste no navegador real. MUST. |
| **Esquecer de salvar** | *"Próximo"* parece gravar | A linha diz *"alterado — não salvo"*; o *Salvar* continua único e visível abaixo do editor; o rascunho local continua protegendo a queda. |
| **Um clique a mais no Edital pequeno** | 78/2026, 2 Perfis | Tabela só a partir do segundo Perfil; Perfil novo abre sozinho. Medir no roteiro: se 2 Perfis piorar, subir o limiar para 3. |
| **Busca do navegador** | Hoje acha o rótulo em qualquer cartão; com `hidden`, não acha nos escondidos | Aceitável: o que se busca é o Perfil, e a tabela o mostra em texto — que hoje nem a busca acha. |
| **Duas renderizações da linha** | Template Django e JS divergem | A linha é montada **só** pelo JS, lendo o formulário; o servidor entrega só o que o JS não sabe (pendências por Perfil, em atributo `data-`). |
| **Lógica de domínio no JS** | A coluna Quadro refazendo a soma | A tabela ecoa campos; o que é regra (a soma, o impeditivo) vem das pendências, calculadas no servidor. |
| **Guardiões da suíte** | Classe nova sem regra na folha reprova `test_acessibilidade`; o teto de bytes da folha; a varredura de vocabulário com lista literal | Estender seletores existentes (`tabela-de-perfis`); medir o teto antes; incluir a tela na lista da varredura. |
| **Manual e roteiros** | `doc/manual` e o roteiro assistido descrevem os cartões | Atualizar na mesma spec. |
| **Base desatualizada** | A `051` (PR 226, já mergeado) editou `compor_perfis.html`, `_perfil.html` e `_modalidade.html` | Partir da `main` atual. |
| **O teto de mil campos** | Continua lá: esconder não reduz o envio | Registro próprio (§3); fora desta proposta. |

---

## 12. Recomendação mínima viável

Em ordem, cada passo entrega sozinho:

1. **A legenda diz quem é** — `<legend>Perfil {{ code }} — {{ locality|default:name }}</legend>`, como a
   Classificação já faz. Uma linha, sem JavaScript, e resolve a busca do navegador, a navegação por
   grupos do leitor de tela e o *"qual é este?"* de quem rola. Faz sentido mesmo que nada mais entre.
2. **A tabela + o editor único na etapa Perfis**, por um script pequeno que lê `#perfis` (o mesmo
   `MutationObserver` que o contador já usa), com as três fontes da Situação, *Anterior/Próximo*, o
   tratamento do `invalid`, a abertura por âncora e por recusa, e a regra de um Perfil sem tabela.
3. **Pendências atribuídas ao Perfil** — o servidor põe no `fieldset` as pendências cujo caminho é
   daquele Perfil; o link de cada pendência passa a abrir o Perfil em vez do topo da etapa.

Fica de fora da primeira versão: ações na linha, edição na linha, cancelar por Perfil, filtro, a
Classificação e o Cronograma. Tudo isso se mede depois do primeiro uso.

---

## 13. Possível próxima SPEC

**Sim, merece spec própria** — ela muda o que o operador vê em todas as composições de mais de um
Perfil, tem requisitos de acessibilidade verificáveis e um modo de falha silencioso (§7) que precisa
de critério de aceite escrito. Não merece ser nota de tarefa da `051`: a `051` fechou o escopo dela e já
foi mergeada.

- **Nome sugerido**: *Perfis de Vaga: a visão do conjunto e um editor por vez*.
- **Objetivo**: que a etapa Perfis responda primeiro *"o que já está cadastrado, e onde há problema"*,
  e depois *"o que estou editando"*, sem mudar o que se grava nem como.
- **Escopo**: a legenda identificada; a tabela resumida com as colunas do §6; zero ou um editor
  visível sobre o mesmo formulário; *Anterior/Próximo*; a Situação com as três fontes; o campo
  inválido e a âncora abrindo o Perfil; a regra de um Perfil só; responsividade; o manual.
- **Não escopo**: qualquer mudança de gravação (`replace_draft`, `D-001`, `UX-020`); o teto de mil
  campos; ações e edição na linha; a Classificação e o Cronograma (candidatas à spec seguinte, com
  a mesma medição); componente genérico de coleção.
- **Critérios de sucesso** (a medir no preview, antes e depois, pelo mesmo roteiro):
  - com 7 Perfis, a etapa abre com a tabela inteira na primeira tela a 1280×900, e a altura da página
    com um editor aberto fica abaixo de ~3,5 mil px, contra 14,5 mil;
  - achar e abrir um Perfil pelo código custa no máximo 1 clique, e as interações para compor o
    28/2026 não aumentam;
  - em 100% dos casos de teste, um envio com campo inválido num Perfil fechado abre esse Perfil e
    foca o campo;
  - nenhum teste da `043`, da `051` nem do rascunho local muda de comportamento;
  - toda linha é identificável sem cor, e a tabela é navegável por cabeçalho no leitor de tela.

Antes de escrever: medir o teto atual de `FR-`, `SC-` e `UX-` em todas as worktrees e branches (a
`051` abriu em `FR-910`, `SC-340`, `UX-110`), e decidir o destino do teto de mil campos, que é o
achado que esta análise produziu e que nenhuma spec cobre.
