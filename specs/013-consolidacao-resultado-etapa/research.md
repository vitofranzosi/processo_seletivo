# Phase 0 — Pesquisa: Consolidação do Resultado da Etapa

**Feature**: 013 | **Data**: 2026-09-02 | **Spec**: [spec.md](./spec.md)

Esta feature foi especificada depois de a 012 estar mergeada, e a spec já nasceu reconciliada
contra o código. Esta pesquisa não redescobre o domínio: ela responde as decisões técnicas que a
spec deliberadamente não tomou, e confirma — lendo o código, não a spec da 012 — que os contratos
que a §1 declara herdados existem com a forma declarada.

Cada item traz **Decisão**, **Racional** e **Alternativas rejeitadas**, e nenhum deixa
`NEEDS CLARIFICATION` para trás.

---

## T-001 — Onde o Resultado mora, e por que o guard não cria ciclo

**Decisão.** App novo `processo_seletivo.resultados`, com um modelo, `ResultadoEtapa`. O guard de
D-002 vive no app `avaliacoes`, onde os comandos protegidos já estão, e importa `resultados`
**dentro da função**, não no topo do módulo.

**Racional.** As duas direções de dependência são reais e opostas: consolidar lê
`avaliacoes.application.selectors.avaliacoes_elegiveis`, e reabrir precisa perguntar se existe
Resultado. Import no topo dos dois lados seria ciclo. O import local já é idioma da casa e não uma
concessão: `avaliacoes/application/avaliacao.py:284` importa `comando_de_comissao` dentro de
`reabrir` exatamente por isso, e `comissoes/application/__init__.py:93` importa `finish_batch`
dentro do método. A dependência de módulo fica num sentido só — `resultados` → `avaliacoes` —, e o
sentido inverso existe apenas no corpo de duas funções.

App novo, e não modelo em `avaliacoes`, por três motivos verificáveis:

1. o princípio I exige conceitos distintos com ciclos de vida distintos, e `ResultadoEtapa` não é
   uma avaliação: é a consequência dela, com autoria, imutabilidade e destino próprios;
2. a 014 crescerá em torno do Resultado — classificação, publicação, recurso —, e mover tabela
   depois é caro num projeto onde migration aplicada não se reescreve;
3. é o padrão da casa: a 012 abriu `avaliacoes` para três entidades operacionais pelo mesmo
   critério, e a 011 manteve `comissoes` separada de `editais`.

**Alternativas rejeitadas.** *Modelo dentro de `avaliacoes`*: elimina o ciclo por completo e custa
zero apps, mas hospeda em "avaliações" um agregado que não é avaliação e que a próxima feature vai
expandir — troca uma linha de import por uma migration de renomeação no futuro. *Camada de serviço
intermediária que ninguém importa diretamente*: abstração especulativa que o princípio V recusa; há
duas funções a proteger, não vinte.

---

## T-002 — O Resultado é registro histórico, e o projeto já sabe protegê-los

**Decisão.** `ResultadoEtapa` entra no regime append-only que o projeto já opera, nas três camadas
que ele usa hoje: `save()`/`delete()` recusando mutação no modelo, trigger `BEFORE UPDATE OR
DELETE` criada na própria migration, e o nome da tabela — `resultados_resultadoetapa` — na tupla
`TABELAS_APPEND_ONLY` de `seguranca/papeis.py:26`.

**Racional.** FR-029 diz que o Resultado não pode ser editado nem fisicamente excluído pela
aplicação, e o projeto tem exatamente um mecanismo para isso, com três camadas independentes de
propósito: o modelo recusa, a trigger recusa mesmo quem tem privilégio, e o papel de runtime não
recebe `UPDATE` nem `DELETE`. O precedente literal é `ConclusaoAvaliacao`, criada pela 012 pelo
mesmo raciocínio, e o molde de SQL está em `publicacoes/migrations/0002_retificacoes.py:16`.

Há um teste que fecha a coerência: `tests/integration/test_imutabilidade_do_historico.py:225`
afirma que todo modelo que recusa mutação está na tupla. Esquecer a tupla é falha de suíte, não
descoberta de auditoria — e é por isso que a decisão é barata.

**Alternativas rejeitadas.** *Só o `save()` do modelo*: cai para qualquer escrita que não passe pelo
ORM, e o teste acima falharia. *Nada disso, confiando na ausência de rota de edição*: a
imutabilidade seria uma propriedade da ausência de código, que a próxima feature reintroduz sem
perceber.

---

## T-003 — A regra da V1, e onde a consequência é decidida

**Decisão.** Uma função pura no domínio de `resultados`, recebendo a Etapa vigente (dicionário do
conteúdo publicado) e a pontuação da Avaliação, devolvendo consequência ou a razão do impedimento.
Nenhuma consulta, nenhum modelo — testável sem banco.

A tabela-verdade que a spec fixou, escrita por extenso porque o modelo admite combinações que a
spec precisa nomear:

| `eliminatory` | `minimum_score` | Previstas | Consequência |
|---|---|---|---|
| `true` | declarada | 1 | `ELIMINADA` se `pontuacao < minimum_score`; senão `HABILITADA` |
| `true` | ausente | 1 | **impedimento**: eliminatória sem nota mínima não tem regra suficiente |
| `false` | qualquer | 1 | `HABILITADA`; a nota mínima, se houver, não elimina |
| qualquer | qualquer | > 1 | **impedimento**: o Edital não declara como combinar |

`classificatory` não entra: ele descreve o destino da nota na composição entre Etapas, que a §5
recusa, e não a consequência local.

**Racional.** As duas leituras normativas já existem e já resolvem a ausência num lugar só —
`avaliacoes_previstas` devolve 1 quando o Edital não declarou (`avaliacoes/domain/previsao.py:20`) e
`pontuacao_maxima` devolve `None` quando não há teto publicado, distinguindo "não declarado" de "sem
limite". Consumi-las é o que FR-002 exige; reimplementar o significado da ausência seria a sexta
cópia que aquele módulo existe para impedir.

Comparação decimal e não float: `minimum_score` é `decimal(7,4)` no modelo e string canônica de
quatro casas no conteúdo publicado (`editais/domain/validation.py:134`). Nota exatamente igual à
mínima habilita, e é um caso de teste, não um comentário.

**Alternativas rejeitadas.** *Um motor de regras configurável*: a spec o proíbe e o princípio V
também. *Decidir a consequência no serviço, junto da escrita*: mistura a regra com a transação e
obriga o teste da regra a montar Edital, Inscrição e Avaliação para verificar uma comparação.

---

## T-004 — Compatibilidade semântica: de onde sai "a norma que governou a Avaliação"

**Decisão.** De `Avaliacao.versao.content["stages"]`, localizando a Etapa pela identidade, e
comparando **valores normalizados** dos quatro campos de D-005 contra os mesmos campos da Etapa
vigente devolvida por `etapas_vigentes(edital)`. Ausência de `evaluationsPerRegistration` vale 1 e
ausência de `maximumScore` vale "não declarada", pelos leitores de T-003 — os dois lados passam
pelos mesmos leitores antes de comparar.

**Racional.** A 012 deliberadamente **não copia** máxima, mínima e caráter para dentro da Avaliação
(`avaliacoes/models.py:101`), porque a versão os reproduz e uma segunda cópia divergiria. A
consequência é que a norma histórica é sempre uma leitura da `VersaoConsolidada` apontada pela
Avaliação — que é `PROTECT` e não nula quando concluída, garantido por check no banco. Não há
caminho em que a norma histórica se perca.

A normalização não é detalhe: o conteúdo publicado guarda decimal como **string canônica** de quatro
casas, e a comparação ingênua `"60.0000" != "60.00"` produziria incompatibilidade onde não há
diferença normativa. Comparar `Decimal` dos dois lados, com `None` distinto de zero.

Um caso precisa de resposta explícita, e a spec já a deu: se a versão que governou a Avaliação **não
contém** aquela identidade de Etapa — Retificação que a removeu e reintroduziu com outro id, por
exemplo —, não há norma histórica a reproduzir e FR-014 impede o Resultado.

A versão é lida **pela Avaliação**, e não copiada para o Resultado: `select_related` traz
`avaliacao__versao` na mesma consulta que traz a fonte, e materializar uma segunda referência criaria
a possibilidade de gravar uma que não fosse a da fonte — ver T-011.

**Alternativas rejeitadas.** *Comparar `content_hash` das versões*: é o que D-005 recusa; qualquer
Retificação em qualquer trecho do Edital bloquearia tudo. *Comparar o subdicionário inteiro da
Etapa*: reintroduz nome e cronograma pela porta dos fundos e ressuscita o defeito que a revisão da
spec corrigiu.

---

## T-005 — A progressão: duas regras, duas camadas

**Decisão.** A Etapa anterior é a de **maior `order` estritamente menor** que o da Etapa corrente,
no conteúdo vigente — nunca `order - 1`. E a progressão se parte em duas regras com alcances
diferentes, servidas por duas camadas com naturezas diferentes.

As duas regras:

1. **Exclusão por eliminação, transitiva e sem gate.** Inscrição com Resultado `ELIMINADA` em
   **qualquer** Etapa de `order` menor está fora, sempre.
2. **Exigência de habilitação, só na imediatamente anterior e só depois do primeiro Resultado
   dela.** É aqui que o gate incide.

Uma redação anterior fundia as duas e produzia um buraco concreto: eliminada na Etapa 1, com a
Etapa 2 ainda não consolidada, a inscrição **reaparecia na Etapa 3** — o gate ficava dormente
porque olhava só a Etapa 2, e a eliminação da Etapa 1 era esquecida. Separar as regras fecha isso
sem perder o motivo do gate, que é não travar a Etapa seguinte de um Edital que a V1 não consolida.

As duas camadas:

- **`resultados/domain/progressao.py` — puro.** Recebe o dicionário de Etapas vigentes e a
  identidade corrente; devolve a Etapa imediatamente anterior e a lista de todas as anteriores.
  Nenhuma consulta, nenhum modelo; testável com dicionários, inclusive nos casos que importam —
  ordem não contígua, Etapa ausente do vigente, primeira Etapa.
- **`resultados/application/selectors.py` — consulta.** Recebe aquelas identidades e devolve os
  conjuntos: `eliminadas_em(edital, etapas_anteriores)` e `habilitadas_em(edital, etapa_anterior)`,
  mais a existência que arma a segunda regra. Duas consultas por listagem, nenhuma por linha.

**Racional.** `order` é `PositiveIntegerField` único por Edital, mas não é contíguo: a Retificação
pode remover uma Etapa do conteúdo publicado sem reordenar as demais, e `order - 1` apontaria para
o vazio.

A separação em duas camadas não é purismo. O plano afirmava que as três funções de domínio eram
puras e não tocavam banco, e esta prescrevia `exists` e `values_list` — as duas coisas não podiam
ser verdade ao mesmo tempo, e a que tinha de ceder era a localização, não a pureza: a escolha da
Etapa anterior é lógica sobre conteúdo publicado, e merece teste sem banco; a leitura dos conjuntos
é consulta, e merece teste de custo.

A forma em conjunto é o que satisfaz a progressão sem violar a invariante de escala da 012 —
nenhuma listagem verifica autorização por linha (012, FR-048), e o docstring de
`avaliacoes/domain/autorizacao.py:11` explica que foi para preservá-la que o impedimento ficou fora
da cadeia. A progressão entra pela mesma porta que a 011 usou para as Etapas autorizadas.

**A superfície alcançada, por inteiro.** A primeira versão desta pesquisa citou a organização da
Etapa e parou ali. A exclusão precisa valer em toda porta que hoje devolve inscrição por Etapa:

| Superfície | Onde | O que muda |
|---|---|---|
| distribuição | `avaliacoes/application/distribuicao.py:175` | `_inscricoes_atribuiveis` recusa a excluída **como erro do pedido**, na mesma classificação que já usa para inscrição não submetida |
| rota individual | `avaliacoes/domain/autorizacao.py:42` | `pode_avaliar_inscricao` ganha a terceira pergunta — e só ela, porque listagem não usa esta função |
| Mesa do avaliador | `avaliacoes/application/selectors.py:220` | `mesa` filtra pelo conjunto, uma vez |
| próxima pendente | `avaliacoes/application/selectors.py:337` | `proxima_pendente` filtra pelo conjunto — sem isso, entregaria a inscrição eliminada sem que ninguém a pedisse |
| carga em Minhas Etapas | `avaliacoes/application/selectors.py:276` | `carga_nas_etapas` deixa de contar trabalho que não existe mais |
| inscrição e documento | `avaliacoes/application/mesa.py:102` | `_autorizar` herda a decisão de `pode_avaliar_inscricao` |

A terceira condição em `pode_avaliar_inscricao` **não** contradiz o docstring que diz "duas
condições, e não três". O argumento dele é sobre custo em listagem, e ele mesmo registra que
"rota individual usa esta função; listagem nunca usa". Uma consulta a mais na rota de item é o preço
correto; o mesmo custo numa listagem seria o gargalo que a 011 antecipou.

**Alternativas rejeitadas.** *Materializar a participação numa tabela*: cria estado a manter a cada
consolidação e duplica um fato derivado, contra D-006. *Deixar a exclusão só na organização da
Etapa*: a Mesa e a próxima pendente continuariam entregando inscrição eliminada, e nenhuma delas
passa pela organização. *Consultar apenas a Etapa imediatamente anterior*: é a redação que
produzia o buraco da Etapa 3.

---

## T-006 — O lote: nada de mecanismo novo

**Decisão.** `comando_de_comissao(actor, processo_id, operation="resultado:consolidar", payload,
idempotency_key)`, `ctx.repetido` devolvendo `ctx.desfecho_anterior` antes de qualquer trabalho,
`resultado_declarado(criados, recusas, "consolidada")` para a forma do desfecho, e
`ctx.concluir_sem_resultado(201, resultado)` para preservá-lo no `result_payload`. Um evento de
auditoria por Resultado criado, dentro do laço.

**Racional.** Os quatro existem e foram construídos para este caso. O invólucro abre transação,
bloqueia o Processo, reavalia a autorização **depois** do bloqueio e reserva a chave
(`comissoes/application/__init__.py:46`). O `result_payload` nasceu na 012 pela razão que vale igual
aqui: sem ele, repetir um lote responde "zero criados, zero recusados", e recusa não é reconstruível
depois porque o estado que a produziu mudou. `resultado_declarado` já agrupa recusas por motivo em
vez de repetir a mesma frase por linha (`avaliacoes/application/distribuicao.py:78`).

O padrão de laço é o da distribuição, inclusive na parte que mais importa: contexto de recusa
resolvido **por conjunto** antes do laço — elegíveis, Resultados existentes, habilitados da Etapa
anterior — e nenhuma consulta por inscrição dentro dele.

**Alternativas rejeitadas.** *Uma requisição por inscrição*: SC-002 e a 012 (FR-047) a proíbem.
*Chave de idempotência derivada do conteúdo*: a reserva já distingue chave repetida com conteúdo
diferente (conflito) de repetição legítima; derivar a chave apagaria essa distinção.

---

## T-007 — Onde o guard incide, e por que só a reabertura é recusada

**Decisão.** Em `reabrir`, logo após localizar a Avaliação e antes do `compare_and_swap`: existe
Resultado cuja fonte é esta Avaliação → `DomainError` 409, ato inteiro recusado. Em
`registrar_impedimento`, **nada é recusado e nada é preservado**: o impedimento registra e inativa
tudo o que alcança, inclusive a Atribuição da Avaliação fonte. O que ele não faz é tocar o
Resultado — e o desfecho declara quais Resultados passaram a ter origem contestada.

**Racional.** Uma redação anterior desta pesquisa preservava a Atribuição que fundamentava
Resultado, para manter a fonte elegível. Ela abria um buraco de segurança que o próprio código
denuncia: a cadeia de autorização **não consulta Impedimento** — ela depende de o impedimento ter
inativado a Atribuição, e o docstring de `avaliacoes/domain/autorizacao.py:11` diz isso com todas as
letras ao explicar por que são duas condições e não três. Preservar a Atribuição deixaria a pessoa
recém-declarada impedida com acesso mantido à inscrição e aos documentos dela — exatamente a porta
que o impedimento existe para fechar, mantida aberta em nome de proteger a proveniência de um
Resultado que ninguém estava tentando alterar.

E não era preciso: o Resultado **já está materializado**. Ele guarda a Avaliação fonte por
`OneToOne` com `PROTECT`, e reproduz a norma pela versão daquela Avaliação. Nada disso depende de a
Atribuição continuar ativa. O que a inativação muda é o conjunto elegível **corrente**, que serve
para decidir novas consolidações — e é correto que ele mude: a partir dali, aquela conclusão não
deve fundamentar mais nada.

A consequência é uma invariante mais honesta. "A fonte continua elegível" era uma afirmação sobre o
presente que a operação podia legitimamente desmentir; "a fonte era elegível quando consolidada" é
uma afirmação sobre um ato passado, que nada desmente. A diferença aparece na consulta: um Resultado
com impedimento superveniente **exibe o fato**, porque quem lê precisa saber que a origem foi
contestada depois — é a única forma pela qual a V1, sem anulação, registra que algo saiu errado.

A implementação fica mais simples do que a versão anterior, e essa é a segunda razão para aceitá-la:
`registrar_impedimento` não ganha classificação de alcance, `alcance_confirmado` não ganha lista
paralela, e a tela de confirmação continua com uma lista só. O que se acrescenta é uma consulta —
quais das Atribuições alcançadas fundamentam Resultado — usada apenas para **declarar**, não para
decidir.

**Alternativas rejeitadas.** *Preservar a Atribuição fonte*: o buraco descrito acima. *Recusar o
impedimento por inteiro*: era a redação original da spec, e deixaria um conflito de interesse
descoberto tarde sem registro possível. *Inativar a Atribuição e invalidar o Resultado
automaticamente*: é anulação com outro nome, fora da V1, e apagaria a autoria do ato original.

---

## T-008 — Um resumo, não dois

**Decisão.** As contagens de D-004 entram em `resumo_da_etapa`, e o filtro de prontidão em
`inscricoes_da_etapa`, ambos em `avaliacoes/application/selectors.py`. A tela é a que já existe:
`interface/views.py:2257` monta `distribuicao.html` com `resumo`, `linhas`, `carga` e `orfas`.

**Racional.** `resumo_da_etapa` já é uma agregação única sobre as inscrições submetidas, com `Count`
condicional por dimensão (`selectors.py:154`), e já distingue cobertura de progresso porque "tem
avaliador" e "tem avaliação" são perguntas diferentes. Prontidão é a terceira pergunta da mesma
população, e vive na mesma agregação: contá-la noutro lugar produziria dois números para a mesma
Etapa, que é o que D-004 proíbe.

Uma consequência que precisa estar no plano: o seletor passa a receber a Etapa **e** o conjunto
habilitador da Etapa anterior, porque o total de participantes deixa de ser "todas as submetidas"
quando o filtro está vigente. É um parâmetro a mais, não uma segunda consulta por linha.

**Alternativas rejeitadas.** *Rota e template próprios para Resultado*: painel concorrente.
*Calcular prontidão em Python sobre as linhas paginadas*: os totais passariam a descrever a página,
e não a Etapa.

---

## T-009 — Autorização: nenhuma capacidade nova

**Decisão.** Consolidar passa por `comando_de_comissao`, cuja base é `pode_gerir_comissao` — a mesma
de reabrir, impedir e distribuir. O ato canônico é `resultado:consolidar`, no formato
`agregado:verbo` que a 012 usa (`avaliacao:reabrir`, `avaliacao:distribuir`). A consulta de Resultado
abre para presidência e para `auditoria:consultar`, o papel que já existe em
`interface/identidade.py:49`, pela mesma porta das conclusões preservadas.

**Racional.** FR-035 exige a mesma base da reabertura, e FR-036 pede reavaliação da autorização
dentro do ato protegido — que o invólucro já faz, depois do bloqueio, por construção. Criar
capacidade nova para um ato da presidência sobre o Processo que ela preside seria inventar
segregação que a Constituição não pede e que a 011 já resolveu.

**Alternativas rejeitadas.** *Capacidade `resultado:consolidar` como permissão de papel*: duplica a
autorização contextual por um nome. *Reusar a permissão de consulta administrativa da 009*: alcança
o Edital inteiro, e a 012 já a recusou pelo mesmo motivo (menor privilégio).

---

## T-010 — Concorrência: cinto e suspensório, ambos já existentes

**Decisão.** Unicidade `(inscricao, etapa_id)` em constraint de banco, e nada além disso de novo. A
serialização por Processo já vem de graça: `comando_de_comissao` faz
`ProcessoSeletivo.objects.select_for_update()` antes de qualquer coisa.

**Racional.** Os quatro riscos que a Constituição nomeia se resolvem por mecanismo existente:
duplicidade pela unicidade, perda de atualização pelo bloqueio do Processo, dado obsoleto pela
releitura dentro da transação, e julgamento conflitante pela recusa nomeada do item já consolidado.
Dois lotes concorrentes sobre a mesma inscrição não disputam: o segundo espera o bloqueio do Processo
e depois encontra o Resultado, recusando o item como já consolidado — que é o desfecho explícito que
a spec pede, e não uma exceção de integridade vazando para a tela.

O custo a declarar: o bloqueio é do Processo inteiro, e um lote de mil inscrições o segura pela
duração da transação. Não é problema novo — a distribuição da 012 tem a mesma forma e a mesma escala
—, mas é o motivo de o lote não crescer indefinidamente sem paginação de trabalho.

**Alternativas rejeitadas.** *Bloqueio por inscrição*: mais fino e desnecessário, já que o invólucro
serializa por Processo de todo modo. *Só o botão desabilitado na tela*: a spec o recusa
explicitamente, e o princípio IV também.

---

## T-011 — Coerência interna do Resultado: garantida, não presumida

**Decisão.** Reduzir o que é materializado, e verificar no `INSERT` o que sobra. Sai `versao`, que é
alcançável pela fonte na mesma consulta. Ficam `inscricao`, `edital`, `etapa_id`, `avaliacao` e
`pontuacao` — e uma trigger `BEFORE INSERT` confere que os quatro primeiros correspondem à Avaliação
fonte, que `pontuacao` é igual à dela, que ela está `CONCLUIDA` e que **a Atribuição que a governa
está ativa**.

Essa última condição não é enfeite: elegibilidade, na 012, é conclusão sob Atribuição ativa, e sem
ela a trigger provaria que o Resultado aponta para a Avaliação certa sem provar que essa Avaliação
podia fundamentar coisa alguma. É o que torna a invariante 2 — "a fonte era elegível quando
consolidada" — uma garantia de banco e não uma promessa da função de consolidação. Custa zero
junções a mais: `Avaliacao.atribuicao` é `OneToOne`, e é a Atribuição que carrega `inscricao_id`,
`etapa_id` e `edital_id`, de modo que a mesma junção que confere a coerência lê o `ativo`.

**Racional.** Uma redação anterior do modelo justificava a redundância dizendo que a divergência era
"impossível porque as linhas de origem são imutáveis". O argumento não se sustenta, e reconhecê-lo é
o ponto: imutabilidade impede que uma linha **correta** se torne incorreta depois; não impede que
uma linha **errada** seja inserida uma vez. E como o Resultado é append-only, uma combinação errada
inserida uma vez é incorrigível pela aplicação — o pior lugar possível para confiar numa promessa de
código.

Por que redundância nenhuma seria pior: `etapa_id` e `inscricao` sustentam a unicidade
`(inscricao, etapa_id)` que é a invariante 1 da spec, e essa unicidade precisa ser constraint, não
consulta. `edital` acompanha `etapa_id` pelo mesmo padrão que `AlocacaoEtapa` já usa
(`comissoes/models.py:81`) e sustenta o escopo das listagens. `pontuacao` é materializada porque a
V1 a copia mas a feature seguinte não necessariamente copiará — o campo descreve o Resultado, não a
fonte.

Por que trigger e não verificação em Python: a Constituição pede que invariante persistente use
constraint quando aplicável, e este é o caso em que "aplicável" precisa de trigger porque uma
`CHECK` não atravessa tabelas em PostgreSQL. O mecanismo já está na migration — a mesma que cria a
trigger append-only — e o custo é uma verificação por linha inserida, num caminho que insere em
lote uma vez por Etapa.

**Alternativas rejeitadas.** *Manter `versao` no Resultado por economia de junção*: a junção é um
`select_related` na mesma consulta, e o campo abria uma quinta forma de o Resultado se contradizer.
*Remover `edital` também*: `etapa_id` é globalmente único e bastaria, mas romperia o padrão que a
011 e a 012 já usam e obrigaria toda listagem a alcançar o Edital pela inscrição. *Confiar na função
de consolidação, que é o único ponto de inserção*: é verdade hoje, e a próxima feature escreve nessa
tabela também.

---

## Confirmações de contrato

Lidas no código, não na spec da 012:

| Contrato | Onde | Forma confirmada |
|---|---|---|
| `avaliacoes_previstas(etapa)` | `avaliacoes/domain/previsao.py:20` | nunca `None`, nunca zero; ausência = 1 |
| `pontuacao_maxima(etapa)` | `avaliacoes/domain/previsao.py:30` | `None` = "não declarada", distinto de "sem limite" |
| `avaliacoes_elegiveis(edital, etapa_id, inscricao_id=None)` | `avaliacoes/application/selectors.py:413` | concluídas sob Atribuição ativa, com `versao` e autoria |
| `resumo_da_etapa(edital, etapa)` | `avaliacoes/application/selectors.py:154` | agregação única sobre submetidas |
| `etapas_vigentes(edital)` | `comissoes/domain/etapas.py:42` | `{UUID: dados}` do conteúdo vigente |
| `comando_de_comissao(...)` | `comissoes/application/__init__.py:46` | bloqueia, autoriza, reserva; `repetido`, `desfecho_anterior` |
| `resultado_declarado(feitas, recusas, verbo)` | `avaliacoes/application/distribuicao.py:78` | serializável, recusas agrupadas por motivo |
| `IdempotencyRecord.result_payload` | `auditoria/models.py:46` | desfecho de ato em lote, nulo para ato singular |
| `auditar(...)` | `avaliacoes/application/trilha.py:52` | um evento por agregado, com correlação e chave |

Nenhuma divergiu do que a §1 da spec declara.
