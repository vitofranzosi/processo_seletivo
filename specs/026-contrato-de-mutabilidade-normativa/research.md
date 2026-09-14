# Pesquisa — Fase 0

**Feature**: Contrato de mutabilidade normativa
**Data**: 2026-09-13

Seis perguntas precisavam de resposta antes do desenho. Todas foram respondidas contra o
repositório, e duas mudaram o escopo previsto pela spec.

---

## R-001 — Onde o contrato mora

**Decisão**: módulo próprio no domínio, `editais/domain/mutabilidade.py`, ao lado de
`validation.py`. `interface/retificacao.py` passa a **lê-lo** em vez de manter as listas
`CAMPOS_*` como fonte.

**Racional**: a natureza de mutabilidade é norma — "este campo pode ser corrigido depois de
publicado" é afirmação sobre o ato administrativo, não sobre a tela. Mantê-la na interface é o que
produziu o estado de hoje: a decisão vive numa lista de rótulos de formulário, e quem acrescenta
campo ao conteúdo publicado não passa por lá. FR-298 exige fonte única lida pelos três — o
guardião, a tela e a aplicação do ato —, e o domínio é o único lugar de onde os três podem ler sem
inversão de dependência.

**Emenda da revisão do PR #114.** Esta seção dizia "pelos dois — o guardião e a tela", e a
implementação a seguiu ao pé da letra: `publicacoes/domain/colecoes.py` continuou com um literal
de um item só, e `REPLACE /number` era aceito pela API apesar de o contrato dizer que o número do
Edital não se corrige. O terceiro consumidor não é acréscimo de escopo — é o canal onde a decisão
tem efeito jurídico, e deixá-lo de fora tornava o contrato uma convenção de formulário. O texto
acima fica registrado como estava; o que mudou é o número de leitores, não o racional.

**Alternativas consideradas**:

- **Dentro de `Campo`, em `validation.py`.** Rejeitada. `Campo` é *transcrição* do `openapi.yaml`
  — `test_forma_publicada.py` existe para impedir que ela vire segunda verdade —, e acrescentar
  natureza ali obrigaria o contrato OpenAPI a declarar mutabilidade, que não é assunto dele. São
  duas perguntas diferentes sobre o mesmo campo: *que forma ele tem* e *o que pode acontecer com
  ele depois de publicado*.
- **Tabela no banco.** Rejeitada. É decisão de código, revista em revisão de código e versionada
  com ele; em tabela, mudaria sem passar por revisão.
- **Manter em `interface/retificacao.py`, só completando as listas.** Rejeitada: é exatamente o
  que já foi feito duas vezes — na `012` e na `019` — e falhou as duas.

---

## R-002 — De onde sai a enumeração dos campos publicados

**Decisão**: da **travessia recursiva do snapshot** de um Edital publicado de verdade, e não das
tuplas `Campo`.

**Racional**: `test_toda_colecao_de_entidades_do_snapshot_esta_declarada` já faz exatamente isso —
publica um Edital com `rascunho_completo()` e enumera as coleções do conteúdo — **mas só no nível
raiz**: ele lê `conteudo.items()`. As coleções aninhadas (`classificationMilestones`,
`competitionModalities`, `declaredFacts`, `vacancyTable`, `tiebreakers`) vivem dentro de
`profiles` e são invisíveis para ele.

O mecanismo existe e está **um nível raso demais** — e é exatamente onde moram os campos sem
decisão: o marco sozinho responde por dez dos vinte e três do Edital 26/2026.

Enumerar pela travessia é estritamente mais forte do que enumerar pelas tuplas `Campo`: um campo
que `publish_edital.py` emite e que ninguém declarou em lugar nenhum aparece na travessia e não
apareceria na tupla.

**Alternativas consideradas**:

- **Enumerar de `COLECOES_PUBLICADAS` / tuplas `Campo`.** Rejeitada como fonte única: três
  coleções deliberadamente não declaram forma interna, com razão escrita (015, T-009: a coerência
  do marco precisa do conteúdo inteiro e não caberia numa forma de campo). Um guardião fundado
  nelas seria cego justamente onde o problema está.
- **Enumerar do `openapi.yaml`.** Rejeitada: o contrato declara nove esquemas publicados e
  **nenhum** para marco, critério de desempate, fato declarado, método do sorteio, regra de corte
  ou janela recursal — `classificationMilestones` aparece como `array` de `object`.
- **Análise estática de `publish_edital.py`.** Rejeitada: frágil e indireta.

**Risco conhecido, e como fica gerido**: a travessia só enxerga o que a fixture exercita. Um campo
que `rascunho_completo()` não preenche não aparece. O risco já existe hoje, para as coleções-raiz,
e a mitigação é a mesma: a fixture é parte do contrato, e um campo novo que não passe por ela é
achado do teste que conferir a própria fixture.

---

## R-003 — Declarar `Campo` para as coleções aninhadas é necessário?

**Decisão**: **não**, e a FR-300 da spec precisava ser corrigida antes de `$speckit-tasks`. **Foi**.

**Racional**: a spec escreveu FR-300 como "a forma publicada MUST estar declarada para toda coleção
normativa". A pesquisa mostra que isso confunde duas coisas:

1. **Enumerar os campos** — de que o contrato precisa, e que R-002 resolve pela travessia.
2. **Declarar a forma deles** (tipo, nulidade, restrições) — que é outra feature, com razão escrita
   para não ter sido feita: *"o que vai dentro do fato e do marco é verificado por
   `_coerencia_dos_marcos`, que precisa do conteúdo inteiro e não caberia numa forma de campo"*.

Declarar `Campo` para marco e modalidade é possível — `LINHA_DO_QUADRO_PUBLICADA` é o precedente, e
a razão escrita para aquela exceção foi específica: a linha carrega um número que a conferência vai
**somar**. Mas não é o que este contrato precisa, e arrastá-lo para cá transforma uma feature de
política numa feature de verificação de forma.

**Recomendação**: FR-300 passa a exigir que **toda coleção normativa esteja enumerada pelo
contrato de mutabilidade**, e não que tenha forma declarada em `validation.py`. A declaração de
forma das coleções aninhadas fica registrada como limite, e vira insumo de priorização — nunca a
priorização em si (princípio VI).

**Alternativas consideradas**: declarar `Campo` para as cinco coleções faltantes junto. Rejeitada
por escopo: acrescenta verificação de forma, `openapi.yaml` novo e sincronização em
`test_forma_publicada.py` a uma feature cujo objeto é decidir corrigibilidade.

---

## R-004 — Como o guardião falha por omissão sem lista a manter à mão

**Decisão**: o guardião compara **dois conjuntos derivados**: os campos que a travessia do snapshot
encontra, e os campos que o contrato classifica. Falha nos dois sentidos, nomeando campo e coleção.

**Racional**: FR-301 a FR-303. A diferença em relação ao guardião de hoje é que ele falha por
**omissão**, e não por divergência: divergência se corrige escolhendo qualquer um dos lados;
omissão obriga alguém a decidir e a escrever a razão. Nenhuma lista de coleções é mantida à mão —
a travessia descobre a coleção nova, e a coleção nova sem classificação derruba a suíte.

**Alternativas consideradas**: um teste parametrizado por coleção, como o de hoje. Rejeitada: é
exatamente a lista à mão que a FR-303 proíbe, e foi assim que `vacancyReversion` passou despercebido
até `test_forma_publicada.py` procurá-lo.

---

## R-005 — A fronteira do congelamento no método do sorteio já existe?

**Decisão**: **sim**, e isso reduz o custo do canário 4 a acrescentar campos à Retificação.

**Racional**: `RelacaoDeHabilitados.metodo_hash` grava o resumo do método **no instante do
congelamento** (`sorteios/models.py:48`), e `Sorteio.metodo_hash` é *"copiado de
`relacao.metodo_hash` e conferido contra ele na constituição"* (`:213`). A garantia da FR-309 é
estrutural e já está no domínio: uma Retificação do método não alcança relação congelada porque a
relação não lê o método vigente — ela carrega o que vigorava quando foi congelada.

**Consequência para o desenho**: o canário 4 não precisa de proteção nova. Ele precisa de campos na
tela e de um teste que demonstre a fronteira. Isso justifica reavaliar a prioridade dele — a spec o
pôs em P2 por presumir custo de domínio que não existe.

**Alternativas consideradas**: nenhuma. É verificação, não escolha.

---

## R-006 — Como a tela declara o que não alcança

**Decisão**: `interface/retificacao.py` monta cada bloco lendo o contrato, e o bloco que tiver
campos não retificáveis imprime a razão normativa deles.

**Racional**: FR-312. Hoje a tela promete "Altere os campos que precisam mudar" e cala sobre o
resto; quem procura arredondamento varre a página e conclui que o sistema esqueceu. Com o contrato
lido pela tela, a razão já está escrita — não é texto novo a redigir, é texto a exibir.

**Restrição herdada**: `test_medida_dos_campos` guarda que explicação que não muda de um cartão
para o outro não se imprime uma vez por cartão. A razão de exclusão **muda por coleção, não por
entidade** — todo marco tem as mesmas exclusões —, então ela cabe uma vez por bloco de coleção, e
não uma vez por marco. O desenho precisa respeitar isso desde o início; foi o que o PR #113 aprendeu
tarde.

---

## Resumo das mudanças que a pesquisa provoca

| | Efeito |
|---|---|
| **R-003** | **FR-300 foi corrigida** antes de `$speckit-tasks`: misturava enumerar com declarar forma. |
| **R-005** | O canário 4 é mais barato do que a spec presumiu; a prioridade P2 merece revisão. |
| **R-002** | O caminho é aprofundar um mecanismo que já existe, e não construir um novo. |
