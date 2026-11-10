# Research: O andamento diz o que cada providência é (135)

As decisões D-001 a D-004 estão na spec. Aqui ficam as leituras do código que sustentam o plano e as
escolhas de implementação.

## R-001 — A lista vazia é o universo vazio de `calcular_ordem`, perguntado uma vez por marco

**O que a tela faz.** A tela da ordenação diz "Ninguém concorreu por este recorte" quando o recorte é
reservado (`lista_id` não nulo) e a proposta de `calcular_ordem` não tem ninguém, nem com posição nem
sem posição (`views.ordenacao`, `recorte_sem_ninguem`).

**Por que o universo basta.** `universo_classificavel.preparar` põe **toda** inscrição do universo
filtrado numa das duas listas: ou é eliminada, ou fica sem pontuação, ou ganha posição. Não há
terceiro destino. A proposta é vazia, então, exatamente quando a consulta de inscrições de
`calcular_ordem` é vazia: as inscrições `SUBMETIDA` do Perfil, com `modality_id` igual ao recorte, e
restritas aos participantes da Etapa do marco (`restringir_a_participantes`).

**Decisão**: `listas_sem_concorrente(*, edital, conteudo, perfil_id, marco_id)` em
`classificacao/application/calculo.py`. A montagem do universo sai de `calcular_ordem` para uma função
privada que as duas chamam (`_universo`), e a nova pergunta com **uma** consulta as Modalidades
distintas desse universo sem o filtro do recorte. As listas reservadas do Perfil que não aparecem
nelas são as vazias. A ampla fica fora, como na tela.

**Custo** (FR-4686): até duas consultas por marco por pontuação — as Modalidades distintas e, quando
a Etapa anterior exige habilitação, o gate de `restringir_a_participantes`. O conteúdo vigente que o
andamento já leu é repassado à condição do corte, que de outro modo o releria (a revisão do PR #441
achou essa terceira leitura).
**Só é perguntada quando alguma lista lê a resposta**: a ordem a emitir sem Etapa por fazer, ou a
obsoleta. A ordem a emitir com Etapa por fazer é *Depois*, e não paga a pergunta. Só é feita quando alguma lista do marco tem a
ordem a emitir ou obsoleta — o que não acontece no marco já ordenado.

**Recusa da norma.** O marco sem Etapa executável faz `calcular_ordem` recusar com `marco_sem_etapa`.
A pergunta nova devolve "nenhuma lista vazia" nesse caso: a recusa é da tela do ato, e a lista vazia
não pode escondê-la.

**Alternativas descartadas.**
- **Chamar `calcular_ordem` por lista.** É o critério literal, mas lê Resultados e fatos de cada
  inscrição para depois só contá-las, uma vez por lista.
- **Reusar `previa.recortes_sem_inscrito` da `126`.** Ela é do sorteio, olha só as Modalidades
  declaradas (sem a progressão por Etapa) e exige o período encerrado. Na pontuação, quem foi
  eliminado antes da Etapa do marco não concorre, e a tela da ordenação já não o conta.

## R-002 — A frase entra no `ato`, e o dado viaja da célula à providência

O nível 1 desenha só o `ato` da providência que é da pessoa ou de outro papel (`_providencia.html`);
a razão aparece só na espera e no condicional. O "Próximo nesta lista" desenha também o `ato`
(`views._proximo_nesta_lista`). Por isso a frase da FR-4672 vai no próprio ato, e nenhum template
muda:

| Situação | Ato |
|---|---|
| *Pendente*, lista vazia | Emitir a ordem que declara que ninguém concorreu nesta lista |
| *Pendente*, duas ou mais vazias agrupadas | Emitir as ordens que declaram que ninguém concorreu nestas listas |
| *Obsoleto*, lista que ficou vazia | Emitir a ordem sucessora, que declara que ninguém concorreu nesta lista |
| *Obsoleto*, duas ou mais agrupadas | Emitir as ordens sucessoras, que declaram que ninguém concorreu nestas listas |

A nota da célula é **"lista em que ninguém concorre"**, na matriz.

**"Ninguém concorre", e não "sem inscritos"** (a revisão do PR #441). A primeira redação dizia "lista
sem inscritos". O critério é o universo **depois da progressão**: uma lista com quatro inscrições, todas
eliminadas na Etapa anterior à do marco, também é vazia, e "sem inscritos" faria ler que ninguém se
inscreveu. A tela da ordenação diz "Ninguém concorreu por este recorte", que é o fato. O dado é `Celula.lista_vazia`, que
`Providencia.da_celula` copia (FR-4673).

**O agrupamento** (FR-4674) já separa atos de texto diferente; a chave ganha também o `lista_vazia`,
para que a regra não dependa da redação. Ao juntar duas vazias, o ato passa ao plural.

**O que não muda.** *Depois* (Etapa não feita) e a recusa da condução continuam como hoje, sem a nota
(FR-4676 e o caso-limite da `128`): a lista vazia não decide situação. A ordem emitida vazia continua
*Feito* com "ninguém concorreu".

## R-003 — A natureza do divulgado é um campo da célula da publicação

`_celula_da_publicacao` já acha a publicação vigente do ato no histórico do marco para escrever a
nota ("resultado preliminar"). Passa a devolver também `natureza` (`PRELIMINAR`, `DEFINITIVA`, ou
vazio). No caso *Obsoleto* — o público lê um ato anterior —, a natureza é a da publicação vigente
defasada, a mais recente. Nenhuma consulta nova: as linhas são as do histórico já lido.

No andamento, `divulgado_da_celula` traduz o campo para `NADA`, `PRELIMINAR` ou `DEFINITIVO`, e a
célula do resultado o carrega em `Celula.divulgado` em todas as situações (FR-4677).

**As quatro leituras de texto que passam a ler o dado** (FR-4679):

| Onde | Hoje | Depois |
|---|---|---|
| `situacao_do_resultado` | `"preliminar" not in nota` → *Feito* | `divulgado != PRELIMINAR` → *Feito* |
| `_Leitor._resultado` | `"preliminar" in nota` → lê o ato vigente | `divulgado == PRELIMINAR` |
| `_Leitor._espera_do_corte` | `"preliminar" not in nota` → sem espera | `divulgado != PRELIMINAR` |
| `_resultado_em_palavras` | `"resultado" in nota`, `"definitivo" in nota` | `divulgado` |

**Os testes puros da `127` e da `133`** montam a célula da publicação só com a nota. Eles ganham o
campo `natureza` (ou, nas células prontas do resumo, `divulgado`) na entrada, e a expectativa não
muda — é o que a FR-4679 pede: a mesma decisão, tomada pelo dado. Um teste novo troca a redação das
notas e confere que nada muda (SC-1463).

## R-004 — A razão da espera é uma segunda redação, ao lado da primeira

As mensagens de `JANELA_ABERTA` e `RECURSO_PENDENTE` terminam com "ou publique como resultado
preliminar". `publicabilidade.py` ganha `MENSAGENS_COM_O_PRELIMINAR_PUBLICADO` e
`mensagem_com_o_preliminar_publicado(codigo, ate)`, que devolve a redação sem a alternativa, ou
`None` para os outros códigos:

- prazo aberto: *"O prazo recursal deste marco ainda está aberto: ele se encerra em 14/11/2026 às
  18h00. O resultado preliminar já está publicado, e o definitivo vem depois do encerramento"*;
- recurso pendente: *"Há recurso pendente de julgamento sobre este marco: chamar de definitivo o que
  ainda está em disputa afirma o que não aconteceu. O resultado preliminar já está publicado, e o
  definitivo vem depois do julgamento"*.

A primeira frase é a mesma da aferição — é por ela que o nível 1 agrupa as esperas (`_primeira_frase`),
e o agrupamento não muda. `MENSAGENS` não é tocado, e quem o lê (a prévia, o comando, a convocação)
continua igual (FR-4682). Só `situacao_do_resultado`, no ramo do preliminar publicado, usa a segunda
redação; as outras razões passam como hoje (FR-4683).

**Alternativa descartada**: cortar o final da mensagem por texto. É a leitura de redação que a G-3
condena, e quebraria em silêncio na primeira mudança da frase.

## R-005 — A contagem do Perfil diz "nos marcos"

"2 providências em aberto nos marcos", no lugar de "2 providências em aberto". O número é o mesmo
(FR-4685); as Etapas continuam em "Etapas X de Y" (D-004). O cartão "O que fazer agora" continua
"N providências em aberto · M são suas", do Edital inteiro.

## R-006 — O resumo do Perfil conta o preliminar com a ordem obsoleta

Uma consequência da R-003 que a spec não nomeia, registrada aqui. Com o preliminar publicado e a
ordem obsoleta (FR-4550 da `133`), a célula do resultado é *Depois* e **não tem nota**: hoje o resumo
diz "resultado não publicado" ou "publicado em 1 de 2 listas", quando o público lê o preliminar. É
o defeito da G-3 em ação — a decisão dependia de a nota existir. Lida pelo dado, a lista conta como
publicada (preliminar), que é o que o resumo diz que mede ("a natureza do que o público lê").

O *Obsoleto* continua contando como publicado e **nunca** como definitivo, como hoje: o definitivo de
um ato anterior não é o definitivo da lista.

Nenhum caso existente da `127` ou da `133` mede esse resumo (conferido na implementação); se algum
medir, a mudança volta ao usuário antes do merge.
