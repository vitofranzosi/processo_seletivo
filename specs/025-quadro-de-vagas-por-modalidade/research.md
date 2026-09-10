# Pesquisa — 025 · Quadro de Vagas por Modalidade

Fase 0 do plano. As onze decisões da §3 da spec chegam **fechadas** e não são reabertas aqui: o que
esta pesquisa faz é dar forma a elas contra o código que já existe, e dizer o custo onde ele existe.

Duas coisas a spec deixou explicitamente para o plano — o **nome da coleção e das chaves** (`D-010`)
e **qual degrau de schema** esta feature ocupa. Ficam decididas na `R-001` e na `R-004`.

Três coisas esta pesquisa **encontrou** e que ninguém tinha pedido:

- a `R-006` mostra que a conferência da `FR-161` não roda no formato de Edital mais comum, por
  interação entre a `FR-161` e a `D-004`. Fica **registrada como achado**, com o custo dito — não
  como escopo desta feature;
- a `R-011` encontrou o nome `_quadro_de_vagas` **já ocupado** no gerador do documento, significando
  outra coisa;
- a `R-007` encontrou que o mecanismo que a `FR-172` precisa **já existe**, e que o precedente mais
  próximo dela no repositório é justamente o que a `D-008` recusa.

---

## R-001 · O nome da coleção e das chaves da linha

**Problema.** A `D-010` fixa a convenção e manda o plano fixar os nomes: chave em inglês no conteúdo
publicado, vocabulário do domínio em português no código. E fixa a permanência — a chave **não muda
depois de publicada**, porque mudá-la mudaria o endereço de retificação de tudo o que já saiu.

**Decisão.**

| Onde | Nome |
|---|---|
| Coleção no conteúdo publicado | `vacancyTable`, irmã de `competitionModalities` dentro de `profiles[]` |
| Campos da linha publicada | `id`, `modalityId` (nulo na linha geral), `immediateVacancies` |
| Modelo relacional | `LinhaDoQuadroDeVagas`, em `editais/models/perfis.py` |
| Campos do modelo | `id`, `perfil`, `modalidade` (nulo), `vagas_imediatas`, `ordem` |
| `related_name` | `perfil.quadro_de_vagas` |
| Caminho de retificação | `/profiles/id=…/vacancyTable/id=…/immediateVacancies` |

**Rationale.**

*`vacancyTable`* é o termo do próprio domínio: os Editais reais imprimem **QUADRO DE VAGAS** como
título de seção. É o nome do artefato, não da tela que o mostra — e o Princípio I manda o vocabulário
do código ser o do domínio.

*`modalityId`* não é nome novo: `documentRequirements[].modalityId` já existe e já significa "aponta
uma Modalidade por identidade" (`editais/domain/documentos.py:92`). Uma segunda grafia para a mesma
referência seria exatamente o defeito que o Princípio I nomeia.

*`immediateVacancies` na linha, e não `quantity`*, é o que torna a `D-011` legível sem nota de
rodapé: a linha carrega vaga imediata, e só ela. O nome genérico convidaria a segunda quantidade que
a `D-011` recusa admitir de antemão — e faria a conferência da `FR-161` comparar `quantity` com
`immediateVacancies`, isto é, duas palavras diferentes que precisariam significar a mesma coisa.

**Alternativas consideradas.**

- *`vacancyDistribution`.* Recusada por colisão de significado: `normativeRule.distribution` já
  existe e já é a **regra** de distribuição da cota. Duas chaves com a mesma raiz, uma sendo o
  fundamento e a outra o número, é a confusão que a `D-003` existe para não deixar acontecer.
- *`vacancyBreakdown`.* Correto e sem colisão, mas não é o que o Edital imprime. Entre um termo
  neutro e o termo do domínio, o Princípio I decide.
- *Guardar a quantidade na `ModalidadeConcorrencia` ou na `RegraNormativa`.* Recusadas **na spec**
  (`D-002`), não aqui.

---

## R-002 · Onde a linha mora, e como a linha geral fica única

**Problema.** A `FR-154` exige no máximo **uma** linha geral por Perfil, e a `FR-155` no máximo
**uma** linha por Modalidade. A linha geral é identificada pela **ausência** de referência — e no
PostgreSQL dois `NULL` não colidem, de modo que uma `UniqueConstraint(perfil, modalidade)` sozinha
deixaria passar duas linhas gerais.

**Decisão.** `LinhaDoQuadroDeVagas` em `editais/models/perfis.py`, ao lado das demais coleções do
Perfil, com **duas** constraints parciais:

```python
UniqueConstraint(fields=["perfil", "modalidade"], name="uq_linha_por_modalidade",
                 condition=Q(modalidade__isnull=False))
UniqueConstraint(fields=["perfil"], name="uq_linha_geral_por_perfil",
                 condition=Q(modalidade__isnull=True))
```

A referência é `ForeignKey(ModalidadeConcorrencia, null=True, on_delete=PROTECT)`, e a quantidade é
`PositiveIntegerField` — que é a `FR-156` (inteiro absoluto ≥ 0) escrita no banco.

**Rationale.** É a mesma cirurgia que a `021` aplicou em `uq_ato_raiz_por_marco`
(`classificacao/models.py:86-100`), e pela mesma razão: uma constraint só, com o campo anulável
dentro, seria **mais fraca** do que a garantia que se quer. Duas parciais dizem as duas regras
separadamente, e cada uma é verdadeira sozinha. O padrão já se repete em `divulgacao/models.py:91` e
`sorteios/models.py:71`.

*`PROTECT` e não `CASCADE`* é a `D-008` escrita no banco, para o caminho da **elaboração**: remover a
Modalidade não pode fazer a quantidade sumir como efeito colateral. A `ModalidadeConcorrencia`
continua `CASCADE` a partir do Perfil, e isso não muda — remover o Perfil inteiro leva tudo, o que é
outra coisa.

*Nulo com significado não é convenção inventada aqui.* `Inscricao.modality_id`,
`PosicaoNaOrdem.modalidade_id` e `AtoDeOrdenacao.lista_id` já são anuláveis com exatamente este
sentido, e `classificacao/models.py:34` escreve a frase: *`NULL` = ampla concorrência*. A linha geral
herda a grafia que o sorteio já pratica, e é isso que faz a `D-004` ser reconhecível em vez de
arbitrária.

---

## R-003 · A ordem: campo no relacional, posição no publicado

**Problema.** A `D-009` diz que a ordem é declarada, preservada e **não** normativa. Mas a `FR-168`
exige que dois conteúdos idênticos produzam o mesmo resumo canônico, e o resumo é calculado sobre o
dicionário inteiro com `sort_keys=True` (`shared/canonical.py:117-121`) — o que ordena **chaves**, e
não listas. A ordem das listas vem do emissor, e um `QuerySet` sem `ordering` a deixaria indefinida.

**Decisão.** `ordem` é campo do **modelo** (`PositiveIntegerField`, `Meta.ordering = ["ordem",
"id"]`) e **não** é publicado na linha. A ordem publicada é a posição no array.

O renderizador do documento exibe a linha geral em primeiro lugar (`FR-169`) independentemente da
posição dela no array — é apresentação, e é o que a `D-009` autoriza.

**Rationale.** A determinização de lista é feita **no emissor**, e não no resumo: é o que
`publish_edital.py:128-130` já registra — *"a ordem do snapshot não pode depender da ordem de
inserção, ou dois snapshots do mesmo conteúdo teriam bytes diferentes"*. As Modalidades saem por
`order_by("code")` e os Perfis por `order_by("code")`, pela mesma razão.

Publicar um campo `order` na linha faria o quadro afirmar uma ordem **normativa**, que é precisamente
o que a `D-009` recusa: não é ordem de convocação nem de precedência entre listas, e prometê-la aqui
seria prometer a feature de convocação. O `tiebreakers` publica `order` justamente porque **lá** a
ordem é a norma (`015`, `FR-015`, e `serializers.py:56-61` escreve o argumento) — a diferença entre
os dois casos é o argumento, e não uma inconsistência.

**Custo declarado.** Sem `order` publicado, uma Retificação **não reordena** o quadro: ela
acrescenta ao fim, altera e remove — que é exatamente o que a `FR-171` pede, e nada além. Reordenar
exigiria publicar a ordem, e publicar a ordem exigiria reabrir a `D-009`. Fica assim, e o custo está
dito.

**Alternativa considerada.** *Ordenar a emissão por `modalidade.code`, como as Modalidades.*
Recusada: a ordem passaria a ser derivada de outro campo, e retificar o código de uma Modalidade
reordenaria o quadro publicado sem que ninguém tivesse pedido. A linha geral, além disso, não tem
código.

---

## R-004 · O degrau 12, e por que ele é de Perfil

**Problema.** A `FR-167` manda o conteúdo publicado passar a ser emitido na versão de schema
seguinte, e a conversão fazer a coleção nascer **vazia** para todo conteúdo publicado antes, sem
inventar quantidade.

**Decisão.** `SCHEMA_VERSION` vai de **11 para 12** (`shared/canonical.py:105`), e o degrau entra em
`DEGRAUS_DE_PERFIL` (`publicacoes/domain/elevacao.py:57`):

```python
DEGRAUS_DE_PERFIL = {
    7: {"classificationMilestones": [], "declaredFacts": []},
    12: {"vacancyTable": []},
}
```

**Rationale.** É o precedente literal que a `D-005` invoca, no mesmo nível da árvore. A docstring de
`elevar_perfil` (`elevacao.py:169-171`) já diz a frase que governa: *as coleções nascem vazias, e a
lista vazia é a grafia da ausência*. Nenhum mecanismo novo, nenhuma função nova — uma entrada num
dicionário que já existe, e `elevar_perfil` a aplica sem alteração.

A régua que o repositório declara para converter ou não está em `elevacao.py:63-71`: converte-se
quando a ausência tem significado **declarado e verdadeiro** sobre todo o acervo anterior; recusa-se
quando escrever o valor da ausência seria afirmação normativa nova — foi por isso que
`documentRequirements`, no 3→4, **não** foi convertido. Aqui a afirmação é verdadeira sobre todo
Edital publicado até hoje: nenhum declarou quadro, porque a capacidade não existia.

**O degrau é de Perfil, e não de raiz**, porque o quadro é do Perfil: um Edital de 7 polos publica 7
quadros, e uma coleção de raiz teria de carregar a referência ao Perfil em cada linha — inventando
uma segunda forma de dizer o que o aninhamento já diz.

**Duas consequências que caem de graça, e uma que não.**

- `tests/fixtures/legado.py:45` (`rebaixar`) deriva as chaves a remover de `DEGRAUS`,
  `DEGRAUS_DE_PERFIL` e `DEGRAUS_DA_RAIZ` — **o degrau 12 está coberto** por ser de Perfil. Fosse de
  Modalidade ou de Evento, não estaria, e o fixture rebaixaria para uma grafia que nunca existiu.
- Não é preciso criar `elevar_modalidade`: a coleção é do Perfil, e `elevar_perfil` já existe.
- **A que não cai de graça:** `elevar_valor` (`elevacao.py:418`) eleva o `newValue` dos atos
  classificando o caminho por predicados declarados. Como a coleção **nasce** no degrau 12, não
  existe Alteração anterior a ela — é o mesmo argumento que `elevacao.py:440-445` escreve para os
  Anexos, e por isso nenhum predicado novo é necessário. Vale confirmar isso por teste, e não por
  leitura.

---

## R-005 · As duas declarações que a coleção precisa

**Problema.** Uma coleção nova morre de duas mortes diferentes se não for declarada em dois lugares
distintos, e as duas são silenciosas.

**Decisão.**

**(a) Endereçamento** — `publicacoes/domain/colecoes.py:19`, em `COLECOES_COM_CHAVE`:

```python
"/profiles/*/vacancyTable",
```

**(b) Forma publicada** — `editais/domain/validation.py:90`, na tupla `PERFIL_PUBLICADO` (que abre em `:71`), ao lado de
`Campo("competitionModalities", list, tipo_do_item=dict)`:

```python
Campo("vacancyTable", list, tipo_do_item=dict),
```

**Rationale.**

*Sem (a)*, a gramática de `changes.py` recusa o seletor `id=`, sobra o endereçamento por posição —
que o sistema proíbe —, e a coleção nasce **irretificável**. É a razão literal registrada para
`/attachments` (`colecoes.py:41-47`) e para as duas coleções da `015` (`colecoes.py:25-30`), que
foram declaradas **antes** de o snapshot as emitir. Aqui é o mesmo: declarar depois deixaria o
primeiro Edital publicado com quadro sem endereço.

*Sem (b)*, os guardas de `tests/fixtures/snapshot.py:275` e `:301` acusam coleção não declarada. Note
que `COLECOES_PUBLICADAS` (`validation.py:207`) só percorre coleções de **raiz** — o quadro é
aninhado no Perfil, e por isso entra em `PERFIL_PUBLICADO` e não ali.

**Nada entra em `CAMPOS_NAO_RETIFICAVEIS`.** `modalityId` da linha é tentador — mudá-lo transforma a
linha da PPI na linha da PcD —, mas a `D-008` já governa o caso pelo lado certo, e proibir a
alteração obrigaria quem retifica a remover e acrescentar para corrigir um apontamento errado,
trocando a identidade da linha sem necessidade. A régua que `colecoes.py:96-98` declara é estreita:
*um campo entra ali quando mudá-lo significaria reinterpretar algo já gravado — não quando ele é
apenas importante.*

---

## R-006 · O que é "quadro completo" — e a lacuna que a `D-004` abre nele

**Problema.** A `FR-161` define quadro completo como *linha geral e uma linha para cada Modalidade
declarada no Perfil*, e só então confere a soma contra o total. A `FR-176` e a `D-004` proíbem que
uma Modalidade usada como ampla concorrência carregue linha reservada. **No Edital normal — o que
declara uma Modalidade chamada "Ampla concorrência", e a spec diz literalmente que é o caso normal —
as duas regras se encontram: seguir a `FR-176` deixa uma Modalidade sem linha, o quadro nunca é
completo, e a conferência nunca roda.**

**Decisão de plano.** A completude é implementada **ao pé da letra da `FR-161`**: linha geral
presente e nenhuma Modalidade declarada sem linha. O sistema **não** tenta identificar
mecanicamente qual Modalidade é a ampla concorrência.

**Rationale.** Identificá-la exigiria casar o nome — "Ampla concorrência", "AMPLA CONCORRÊNCIA",
"Ampla Concorrência/Universal" — e a §7 da spec põe **fora de escopo** reconciliar as duas grafias da
ampla concorrência. Uma heurística de string aqui seria decidir, no plano, uma questão que a spec
declarou aberta; e erraria em Edital que chame a Modalidade de outra coisa. A correção anterior
daquele mesmo defeito, na prévia do sorteio (`sorteios/application/previa.py:35-44`), foi
explicitamente **de rótulo e não de identidade** — copiar dali uma identificação seria copiar o que
não foi feito.

**O que sobra, dito sem rodeio.** No Edital normal, a conferência da `FR-161` e a recusa da `SC-054`
só rodam se quem compõe declarar linha com `0` para a Modalidade "Ampla concorrência" — que é
justamente o que a `FR-176` proíbe e o que a advertência da `R-010` vai desaconselhá-lo a fazer. O caminho existe e fecha a conta
(`56 + 0 + 4 + 20 = 80`), mas é o caminho desaconselhado.

**Uma terceira saída, que o plano adota e que não fecha a lacuna inteira.** A `FR-177` recusa toda
soma que **exceda** o total, em quadro completo ou parcial, sem identificar Modalidade nenhuma. Ela
converte "a conferência nunca roda no Edital normal" em "a conferência pega o erro perigoso e deixa
passar o conservador": um `PPI 200` digitado no lugar de `20` passa a ser recusado; um quadro somando
`79` contra `80` continua passando. As duas saídas abaixo seguem sendo as que fechariam o resto.

**Fica registrado como achado, e não como escopo.** Fechá-lo pede uma de duas coisas, e as duas são
decisão do usuário, não do plano:

1. marcar a Modalidade de ampla concorrência **explicitamente** no Perfil — campo novo, degrau novo,
   e a reconciliação das duas grafias que a §7 adiou; ou
2. redefinir completude como *linha geral presente e no máximo uma Modalidade sem linha* — barato, e
   frouxo o bastante para deixar passar o esquecimento genuíno de uma cota.

O plano não escolhe. A `UX-023` continua dizendo a diferença em números **onde a conferência roda**, e
a advertência da `R-010` continua valendo linha a linha em todo caso.

---

## R-007 · A recusa de remover Modalidade referenciada (`FR-172`)

**Problema.** A `D-008` manda recusar a Retificação que remova uma Modalidade ainda referenciada por
uma linha, dizendo **qual** linha a impede. `changes.py` é gramática pura: sabe descer caminho,
recusar posição e recusar coleção atômica, e **não** conhece referência entre coleções.

**Decisão.** Nenhum mecanismo novo. A regra é um *finding* **impeditivo** em
`editais/domain/validation.py`, ao lado dos cinco que já existem:

| Referência já verificada hoje | Código | Onde |
|---|---|---|
| requisito → Anexo | `attachment_reference_dangling` | `validation.py:995` |
| marco → Etapa enumerada | `milestone_stage_missing` | `validation.py:638` |
| critério → Etapa | `tiebreaker_stage_missing` | `validation.py:661` |
| critério → fato declarado | `tiebreaker_fact_missing` | `validation.py:670` |
| requisito → Perfil / Modalidade | `document_requirement_*_unknown` | `validation.py:1031`, `:1049` |
| **linha do quadro → Modalidade** | **`vacancy_row_modality_missing`** | **novo** |

Um só código, aplicado em três pontos que **já chamam** `validate_for_publication`:

- `retificacoes.py:515` (`_assert_well_formed`), sobre o conteúdo que a Retificação **produziria** —
  é a `FR-172`;
- `retificacoes.py:555` (`_assert_structurally_publishable`), por fronteira de vigência;
- `publish_edital.py:376` e `:594`, na submissão e na publicação — é a `FR-166`.

**Rationale.** O mecanismo verifica o **resultado** e não a **operação**, e é isso que faz a regra
valer para os dois movimentos que a `D-008` prevê: remover a Modalidade sozinha é recusado; remover a
Modalidade **e** a linha, no mesmo ato, passa — e a `D-008` diz literalmente que "remover as duas é
um ato só". Uma verificação que olhasse a operação teria de entender que outra operação do mesmo ato
a conserta, que é o modo de falha mais caro possível. `validation.py:571-586` já escreve esse
argumento para o marco: *"uma Retificação que remova a Etapa enumerada sem ajustar o marco não
publica"*.

**A armadilha, e é grande: o precedente mais próximo é o que a `D-008` recusa.**
`interface/retificacao.py:920-966` faz o contrário disto para os Anexos — quando o ato remove um
Anexo, a tela **emite automaticamente** o `REPLACE …/attachmentId → None` que desfaz o vínculo, e o
mostra no resumo. É o padrão que um implementador copiaria sem pensar, e aqui ele está proibido: lá
a emissão automática **desfaz um vínculo**; aqui ela **apagaria uma quantidade publicada** como
efeito colateral de outro movimento, que é exatamente a alternativa que a `D-008` recusou por escrito.
A recusa é a resposta certa, e a mensagem tem de nomear a linha.

**Manter `changes.py` genérica é decisão, não omissão.** A gramática vale para toda coleção;
ensiná-la uma referência específica faria a próxima referência ter de ser ensinada lá também, e a
gramática viraria catálogo de regras de domínio.

---

## R-008 · A referência cruzada na elaboração (`FR-158`)

**Problema.** A `FR-158` exige recusar linha que referencie Modalidade de outro Perfil ou de Perfil
nenhum, **com mensagem que diga qual dos dois casos é**. A spec manda copiar o padrão que já existe,
"inclusive a mensagem".

**Decisão.** Duas verificações, em dois lugares que já existem e que verificam coisas diferentes:

**(a) A referência cruzada**, em `editais/domain/perfis.py`, chamada de `validate_profile`, com a
frase montada como `documentos.py:85-89` a monta:

```python
motivo = ("não pertence ao Perfil declarado" if perfil_declarado
          else "não é de nenhum Perfil deste Edital")
```

A recusa é `ProfileValidationError` com `campo="modalityId"` e `identidade=<id da linha>` — a forma
que `RecusaDeCampo` (`perfis.py:4-20`) define para a interface ancorar o erro na linha certa, e que
`draft.py:189-200` já propaga como `DomainError(..., 422, campo=…, identidade=…)`.

**(b) A identidade aninhada alheia**, em `draft.py:34` (`_identidades_aninhadas_alheias`), que hoje
confere Modalidade contra Perfil, Regra contra Modalidade, Fato contra Perfil, Marco contra Perfil e
Critério contra Marco. A linha do quadro entra nesse mapa, contra o Perfil.

**Rationale.** No quadro o Perfil é **sempre** declarado — a linha mora dentro dele —, de modo que o
caso "não é de nenhum Perfil deste Edital" só aparece quando o `modalityId` não existe em Edital
algum. Os dois casos continuam distinguíveis, e a correção que cada um pede continua sendo outra, que
é a razão de a mensagem os separar.

**A validação roda no domínio, e não só no serializer**, pela razão que `perfis.py:29-31` já
registra: a interface administrativa invoca o command diretamente e não atravessa o serializer da
API. Validar só ali deixaria sem verificação justamente o canal onde o dado é digitado.

**Esquecer (b) é o defeito silencioso.** Sem ela, um `id` de linha pertencente a outro Edital seria
aceito na gravação, e o 409 `identifier_belongs_to_another_edital` que o contrato promete não
aconteceria para esta coleção.

---

## R-009 · A seção na tela, e as quatro travessias do rascunho

**Problema.** A `UX-020` põe o quadro como **seção da tela de composição do Perfil**, e a `UX-021`
exige que só as quantidades sejam digitadas. E a gravação do rascunho **apaga e recria tudo**:
`replace_draft` (`editais/application/draft.py:145`) faz `PerfilVaga.objects.filter(...).delete()` e
recria a partir do que recebeu. O que não for reenviado **some**.

**Decisão.** A seção vive dentro do cartão do Perfil (`interface/templates/interface/_perfil.html`),
com nomes de campo `linha-{i}-{j}-…` no padrão de prefixo composto que `forms._indices` (`forms.py:27`)
já usa para Modalidades e Fatos.

**As quatro travessias, e todas são obrigatórias.** Uma coleção do Perfil que falte em qualquer uma
delas morre em silêncio na gravação da etapa seguinte:

| # | Onde | Função | O que faz |
|---|---|---|---|
| 1 | `interface/forms.py:338` | `ler_perfis` → `_linhas` (novo) | lê o formulário |
| 2 | `interface/forms.py:598` | `perfis_persistidos` | **reenvia** ao gravar outra etapa |
| 3 | `interface/forms.py:543` | `perfis_do_edital` | reexibe na tela |
| 4 | `editais/application/draft.py:218` | recriação | grava, preservando o `id` recebido |

O quadro **não** entra em `PRESERVADO_DA_ETAPA["perfis"]` (`views.py:1153`), porque essa tupla é para
o que a tela não desenha — e esta tela desenha o quadro.

**As linhas são oferecidas, não digitadas.** A tela deriva uma linha geral mais uma por Modalidade já
declarada **no formulário**, e só o campo de quantidade é editável. Quantidade em branco **não grava
linha** (`FR-159`, `D-006`). É o que faz a `UX-021` e a `SC-052` fecharem: 7 polos × (1 geral + 3
modalidades) = 28 campos, e nenhum rótulo redigitado.

**Rationale.** Uma tela à parte seria mais fácil de escrever, violaria a `UX-020`, e — pior — a
gravação de uma apagaria o que a outra tinha acabado de gravar, porque o rascunho é substituído
inteiro. Estando na mesma seção e no mesmo POST, o problema não existe.

**Três armadilhas, ditas para não serem atropeladas.**

1. **`_indices` só enxerga a linha que envia um campo `…-id`** (`forms.py:27`). Linha sem `id` no
   POST é linha que não existe para o servidor.
2. **As linhas nascem das Modalidades do formulário, não do banco.** Quem acrescenta uma Modalidade
   por htmx e digita a quantidade dela antes de gravar precisa ver a linha aparecer. O índice da
   linha nova nasce no **servidor** (`views.py:1247`, `secrets.randbelow`), porque a CSP não admite
   `hx-vals='js:'` — o fragmento novo segue o padrão de `views.py:1408` (`fragmento_modalidade`).
3. **`tests/interface/test_round_trip_do_rascunho.py` é o teste que esta seção tem de satisfazer.**
   Ele compara a coleção **inteira**, campo a campo, depois de gravar outra etapa — existe
   exatamente para pegar "o campo de que ninguém se lembrou" (`E2E17-001`).

---

## R-010 · A advertência do percentual (`FR-163`)

**Problema.** A `D-003` preserva o uso do percentual para **advertir** — dizer que `4` não é 20% de
`80` é serviço legítimo — sem transformar cálculo em norma. A `FR-163` é `MAY`, e a advertência
`MUST NOT` bloquear a gravação nem alterar a quantidade.

**Decisão.** A advertência é um *finding* de nível **aviso** em `editais/domain/validation.py`,
produzido por `validate_for_publication`. `blocking_findings` continua sendo quem decide o que
impede, e o aviso não entra lá.

**Rationale.** O mecanismo de três níveis existe exatamente para isto, e é o que o Princípio IV da
Constituição exige da operação de publicar: validar inconsistências, classificá-las como informação,
aviso ou erro impeditivo, e bloquear apenas diante de erro impeditivo. `validation.py:946-1003` já
pratica a distinção no caso dos Anexos — referência pendurada é impeditiva, rótulo repetido é aviso.
Escrever esta advertência como exceção e capturá-la seria construir um segundo mecanismo ao lado do
que já funciona.

**A advertência nunca toca a quantidade.** Ela compara e reporta; a `FR-157` proíbe derivar, calcular
ou recalcular quantidade a partir de percentual, e a implementação não tem caminho de escrita. A
mesma classificação serve à advertência sobre declarar linha reservada para uma Modalidade que o
Edital use como ampla concorrência: o número dela mora na linha geral (`FR-176`, `D-004`).

---

## R-011 · O quadro no documento publicado — e um nome já ocupado

**Problema.** A `FR-169` manda o documento exibir o quadro na ordem declarada, com a linha geral em
primeiro lugar, e **omitir a seção inteira** quando não houver quadro, sem frase de ausência.

**O achado.** `publicacoes/infrastructure/pdf.py:1332` **já tem** uma função chamada
`_quadro_de_vagas`, e ela é outra coisa: a tabela comparativa de **Perfis** — `["Perfil",
"Localidade", "Vagas", "Cadastro reserva", "Carga horária"]` —, composta só quando há mais de um
Perfil. O nome do domínio está ocupado por um artefato que não é o do domínio.

**Decisão.**

1. **Renomear** `_quadro_de_vagas` para `_quadro_de_perfis`. É função privada; o PDF sai byte a byte
   idêntico, e `tests/contract/test_documento_publicado.py:136` continua verde — o que prova o
   contrário do risco.
2. O quadro novo é um **bloco próprio dentro da subseção de cada Perfil**, com duas colunas —
   `["Lista de concorrência", "Vagas imediatas"]` —, composto logo antes de `_modalidades`
   (`pdf.py:1289`) e omitido inteiro quando `vacancyTable` é vazia.
3. A linha geral vem primeiro, rotulada **"Ampla concorrência"**. As reservadas trazem denominação e
   código no formato que a prévia do sorteio já usa — `f"{name} ({code})"`
   (`sorteios/application/previa.py:46`).

**Rationale.** O Princípio I proíbe que o mesmo termo nomeie dois conceitos: publicar um "quadro de
vagas" ao lado de uma função `_quadro_de_vagas` que tabula Perfis é a ambiguidade que a linguagem
ubíqua existe para não ter. A função renomeada passa a dizer o que faz.

*Bloco próprio, e não coluna nova na tabela de Modalidades.* A tabela de `_modalidades`
(`pdf.py:1289`) já omite coluna sem valor (`pdf.py:1315-1318`), e acrescentar "Vagas" ali seria
tentador e barato. Mas ela é uma tabela de **Modalidades**, e a linha geral não é Modalidade nenhuma
— o `AC 56` não teria linha onde morar, que é precisamente o defeito que a `D-002` recusou no modelo
de dados. Repeti-lo na apresentação publicaria um quadro que não fecha.

*A omissão é da seção do quadro, e não da seção do Perfil.* O mecanismo de omissão por origem vazia
já existe um nível acima (`pdf.py:1696`, `_materializaveis`) e vale para seções de raiz; aqui a
omissão é local ao bloco. Omitir a seção inteira é o que a `SC-050` cobra: nenhum Edital publicado
antes desta feature pode passar a afirmar zero vaga em lugar nenhum, e uma frase do tipo "quadro não
declarado" seria uma afirmação nova sobre um documento que não a fez.

**Nota de custo.** Mudar a composição do PDF obriga a regenerar a fixture de bytes por
`backend/scripts/gerar_fixture_documento.py`, e só na mesma tarefa que muda a composição de propósito
— é a regra que `tests/contract/test_documento_publicado.py` impõe.

---

## R-012 · O reaproveitamento entre Editais (`023`)

**Problema.** `editais/domain/reaproveitamento.py` copia um Edital para o seguinte trocando **toda**
identidade por uma nova, e recusa referência não mapeada (`ReferenciaNaoMapeada`). Uma coleção nova
com identidade própria **e** uma referência a outra identidade tem de entrar nos dois passos, e o
segundo é o que quebra em silêncio se for esquecido — a linha copiada continuaria apontando a
Modalidade do Edital **anterior**.

**Decisão.** Os dois passos, explicitamente:

1. No registro de identidades (`reaproveitamento.py:56-67`), registrar o `id` de cada linha.
2. Na troca (`reaproveitamento.py:95-111`), trocar o `id` da linha **e** o `modalityId` dela, pelo
   mesmo `trocar(...)` que já mapeia a Modalidade — que é o que garante que a linha copiada aponte a
   Modalidade **nova**.

`modalityId` nulo atravessa intocado: a linha geral não referencia nada.

**Rationale.** Este é o ponto do plano com maior chance de passar despercebido e o menor custo de não
passar. A função já faz as duas coisas para `normativeRule.id`; é o mesmo padrão, mais duas linhas.

---

## R-013 · O contrato de API

**Problema.** `tests/contract/test_openapi_conformance.py` verifica o comportamento observável contra
`specs/001-processo-seletivo-editais/contracts/openapi.yaml`, e
`tests/contract/test_forma_publicada.py:194` confronta as declarações de `validation.py` contra ele
campo a campo. O `ProfileSerializer` (`editais/api/serializers.py:93`) ganha uma coleção, e o
contrato tem de acompanhar em dois lugares.

**Decisão.**

| Lugar | O que muda |
|---|---|
| `PerfilInput` (`openapi.yaml:630`) | `vacancyTable`: array de `LinhaDoQuadroInput`, **opcional** |
| `PerfilPublicado` (`openapi.yaml:735`) | `vacancyTable` em `properties` **e** em `required` |
| `LinhaDoQuadroInput` (novo) | `required: [id, immediateVacancies]`; `modalityId` anulável |
| `LinhaDoQuadroPublicada` (novo) | os três campos, `modalityId` com `type: [string, 'null']` |

**Rationale.** Entrar em `required` do publicado é a `D-005` escrita no contrato: depois do degrau 12,
todo conteúdo publicado **tem** a chave — vazia nos anteriores. Deixá-la opcional admitiria duas
grafias para a ausência, ausente e vazia, e é justamente a distinção que a `D-005` existe para não
permitir. É também como `competitionModalities`, `declaredFacts` e `classificationMilestones` já
estão (`openapi.yaml:735`).

No **input** ela é opcional, porque o rascunho legitimamente não a traz (`FR-160`), exatamente como
`classificationMilestones` e `declaredFacts`.

`id` obrigatório no input segue o que `ModalidadeInput` já documenta (`openapi.yaml:633-643`):
identidade estável entre gravações — opcional, ela reabriria o defeito que a estabilidade veio fechar
—, e identificador de outro contêiner responde `409 identifier_belongs_to_another_edital`.

**Diferença deliberada em relação à Modalidade.** `competitionModalities` é a única coleção do
snapshot cuja forma **interna** não é verificada (`validation.py:88-90`: *a forma de dentro de cada
Modalidade não é declarada*). O quadro **não** herda essa folga: `LinhaDoQuadroPublicada` é declarada
e verificada, porque a linha carrega um número que a conferência da `FR-161` vai somar, e somar campo
não verificado é somar o que ninguém garantiu ser inteiro.

---

## R-014 · As duas telas que a Retificação precisa

**Problema.** `interface/retificacao.py` mantém um catálogo de campos por coleção — tuplas
`(chave, rótulo, tipo)` — que é o que a tela oferece a quem retifica. Coleção fora do catálogo é
retificável pela API e invisível na tela, e o Princípio VI diz que capacidade que nenhuma interface
alcança não está entregue.

**Decisão.**

1. Catálogo novo `CAMPOS_DA_LINHA`, ao lado de `CAMPOS_MODALIDADE` (`retificacao.py:73`), com
   `immediateVacancies` (`INTEIRO`) e `modalityId` (`REFERENCIA`).
2. `NOVO_PERFIL` (`retificacao.py:140`, e o gabarito de `:714-726`) ganha `"vacancyTable": []` ao lado
   de `"competitionModalities": []`.
3. `modalityId` usa o tipo `REFERENCIA`, que oferece as Modalidades como opções em vez de pedir UUID
   digitado — a razão está escrita em `retificacao.py:34-41`: *digitar UUID à mão faria um erro de
   digitação mudar em silêncio quem precisa enviar o quê*.

**Rationale.** É a diferença entre a `US3` existir e a `US3` ser demonstrável pelo canal do ator — que
é o que a Constituição exige e o que o gate da §9 da spec percorre. A tela de Revisão do assistente
(`interface/revisao.py:31`) monta as linhas a partir do próprio snapshot, de propósito para que
coleção nova apareça sem alguém lembrar; mesmo assim o rótulo do quadro precisa ser escrito.

---

## Questões que não precisaram de pesquisa

- **Autorização.** Nenhuma permissão nova. A composição exige `edital:elaborar`
  (`draft.py:158`), a publicação exige `edital:publicar` (`publish_edital.py:565`), e a segregação de
  funções (`publish_edital.py:581`) continua valendo. O quadro é seção das telas que já as exigem, e
  não há ator novo.
- **Concorrência.** Nenhum risco novo: `replace_draft` já roda sob `select_for_update` e
  `expected_revision` (412 `stale_revision`), e a Retificação já tem `expectedPreviousHash`.
- **LGPD.** O quadro não tem dado pessoal. É contagem de vagas.
- **Desempenho.** O maior caso do alvo é 7 Perfis × 4 linhas. A emissão já faz
  `prefetch_related("modalidades__regra_normativa", …)` (`publish_edital.py:99`); o quadro entra no
  mesmo prefetch e não acrescenta consulta por Perfil.
- **Verificação end-to-end.** Não há suíte de navegador no repositório, e não é omissão: o E2E deste
  projeto é percurso exploratório conduzido contra o servidor real, com relatório versionado em
  `doc/e2e/`. Os achados recebem identificador `E2E25-NNN` e são citados na docstring do teste que os
  fecha — é o que `tests/interface/test_round_trip_do_rascunho.py:1` faz com o `E2E17-001`.
