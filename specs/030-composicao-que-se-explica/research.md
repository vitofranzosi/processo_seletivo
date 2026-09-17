# Phase 0 — Pesquisa

Cinco perguntas ficaram em aberto ao ler a spec contra o código. Todas estão resolvidas abaixo.
Duas delas — R2 e R5 — eram travas: sem resposta, P3 e FR-418 não teriam plano.

---

## R1 — Como a "forma de produção da ordem" existe sem reescrever Edital publicado

**Decisão**: campo novo `forma_da_ordem` em `MarcoClassificatorio`, com as alternativas
`POR_PONTUACAO` e `POR_SORTEIO`, e chave `orderProduction` no conteúdo normativo. **A ausência da
chave é significativa**: Edital publicado antes desta feature não a tem, e os leitores derivam dele
o comportamento de hoje — sorteia se `drawMethod` está declarado.

**Racional**: hoje "este marco sorteia" é inferido da presença de `metodo_de_sorteio`. A inferência
não distingue **"não sorteia"** de **"sorteia e ainda não declarei o método"** — e é essa segunda
situação que FR-414 precisa reconhecer para apresentar os campos do sorteio a quem ainda não
preencheu nenhum. Uma pergunta de entrada que não se persiste seria a mesma inferência com outra
roupa.

Escrever a chave de volta em snapshot publicado está fora de questão: mudaria o conteúdo publicado e
o resumo dele. O que a Constituição preserva é o **valor publicado**, não a forma do modelo — então
o campo pode nascer, desde que nada retroaja.

**Alternativas recusadas**:

- *Derivar da presença do bloco*: mantém a ambiguidade que FR-414 existe para desfazer.
- *Migração que preenche o campo em Editais publicados*: reescreve conteúdo normativo. Recusada pela
  Constituição, princípio II.

---

## R2 — Onde mora o método do sorteio declarado uma vez (FR-429, FR-430)

**A trava**: `MarcoClassificatorio.metodo_de_sorteio` documenta, no próprio modelo, por que ele mora
no marco — *"Mora aqui, e não numa tabela de sorteio, porque a FR-014 exige que alterá-lo seja
Retificação. Uma tabela própria seria registro operacional que se diz normativo: sem versão
consolidada, sem autoridade signatária, fora do snapshot e fora da gramática de endereçamento."*

**Decisão**: o método comum vira **conteúdo normativo do Edital**, e não tabela operacional. Ele
entra no mesmo snapshot, sob a mesma autoridade signatária, endereçável por
`/drawMethod/…` no catálogo de mutabilidade — exatamente as quatro propriedades que o modelo cobra.
O marco que não declara método próprio **referencia o comum**; o marco que declara (FR-430) diverge,
e a divergência é explícita porque a chave existe no marco.

**Isto não contraria o modelo — atende ao argumento dele.** A objeção registrada era contra *tabela
operacional* e contra *método por lista*, não contra o Edital: o Edital é onde o conteúdo normativo
já mora, com versão consolidada e signatário.

**Consequências que o plano precisa carregar**:

- `mutabilidade.py` ganha nove entradas `("edital", "drawMethod/…")`, espelhando as nove que hoje
  existem sob `("classificationMilestones", "drawMethod/…")`.
- A resolução — método do marco, senão o do Edital — precisa acontecer **em um lugar só**. Os
  leitores são muitos: `classificacao/application/`, `sorteios/`, os serializers e a supervisão.
- Edital publicado **não muda**: cada marco continua carregando seu método literal. A resolução só
  se aplica a marco sem método próprio, que hoje não existe em Edital publicado nenhum.

**Alternativa recusada**: tabela `MetodoDeSorteio` própria — a recusa já estava escrita no modelo, e
continua valendo.

---

## R3 — Qual é o padrão de casas decimais e arredondamento (FR-419)

**Decisão**: `{"scale": 2, "mode": "MEIO_PARA_CIMA"}`.

**Racional**: é o que o próprio projeto pratica onde já escolheu — `seed_demo.py` usa esse par nos
dois Editais que semeia, e as fixtures de referência dos testes repetem. A Assumption da spec fica
confirmada, e a cláusula de escape dela permanece: se a amostra indicar outro padrão, o requisito
segue válido e só o valor muda.

---

## R4 — Como revelar progressivamente sem quebrar a submissão

**Decisão**: ida e volta ao servidor por fragmento htmx, como o assistente já faz em
`fragmento-criterio` e `fragmento-marco`. O campo impertinente **sai do formulário** — não é
escondido por CSS.

**Racional**: a regra já está escrita em `_marco.html` e custou caro — *"Nenhum campo obrigatório
entra nos blocos que fecham: campo `required` invisível é submissão que o navegador recusa sem
conseguir mostrar o que falta."* Esconder por CSS mantém o `required` ativo e reproduz exatamente o
defeito. O `required` precisa sair **junto** com o campo, e a cobrança passa para a validação da
publicação — que é onde ela já mora para as Etapas do marco.

**Alternativa recusada**: `display:none` mais `disabled`. Campo `disabled` não é submetido pelo
navegador, o que colide de frente com R5.

---

## R5 — Como preservar o declarado quando o campo deixa de ser pertinente (FR-418)

**A trava**: `replace_draft` **apaga e recria**. O payload substitui o conteúdo inteiro do rascunho;
não há atualização campo a campo. Campo que não volta no envio é campo perdido, em silêncio — que é
precisamente o que FR-418 proíbe, e precisamente o que R4 produziria se parasse no template.

**Decisão**: o campo que deixa de ser pertinente **continua no envio, como `<input type="hidden">`
carregando o último valor declarado**. Ele some da tela e do alcance do teclado; não some do
payload. `replace_draft` continua recebendo o marco inteiro e não precisa mudar.

**Racional**: é a resposta que não mexe na semântica de substituição do rascunho. Mudar
`replace_draft` para fusão parcial seria alterar o contrato de gravação do assistente inteiro —
muito além desta feature, e com risco em todas as coleções, não só nos marcos.

**A consequência que precisa de teste**: o valor guardado em campo oculto **não pode vazar para o
conteúdo publicado** quando a forma da ordem o tornou impertinente. Um marco que era de sorteio e
passou a ser de pontuação guarda o método no rascunho, mas **não o publica**. A fronteira é a
validação da publicação, e é ela que o teste precisa fixar.

**Alternativa recusada**: descartar o valor ao trocar a resposta. É o comportamento que FR-418
nomeia como proibido — "NÃO DEVE descartar declaração em silêncio".

---

## Riscos residuais

| Risco | Onde aparece | Mitigação no plano |
|---|---|---|
| A resolução do método comum se espalha por vários leitores | `classificacao/`, `sorteios/`, serializers, supervisão | Um único ponto de resolução, coberto por teste que varre os leitores |
| Campo oculto de R5 vaza para o publicado | validação da publicação | Teste de fronteira, obrigatório, antes de P3 |
| SC-138 conta "perguntas", e o código conta controles | aceitação | `quickstart.md` fixa o método de contagem |
