# Research: Mesa de Avaliação

**Feature**: `012-mesa-de-avaliacao` | **Data**: 2026-09-01 | **Spec**: [spec.md](./spec.md)

As decisões abaixo são **técnicas**, e por isso levam o prefixo `T-`. As decisões de produto já
estão fechadas na §5 da spec, com o prefixo `D-`; este documento não as reabre — ele responde
*como*, e confronta a única que a spec mandou confrontar antes de qualquer migration.

A verificação foi feita contra `ae86b6e`, com a 011 já mergeada em `main`.

---

## T-001 — A elevação de versão canônica, e por que ela é possível

**A spec mandou confrontar isto antes de escrever migration** (D-002, FR-098): o Edital publicado
antes do incremento tem de continuar retificável, sem que a Publicação original seja tocada.

### O que o mecanismo faz hoje

`_assert_versao_canonica` compara o `schemaVersion` **do próprio conteúdo** com a constante global
`SCHEMA_VERSION`, e recusa com 409 quando divergem. Ela roda em dois pontos do fluxo de
Retificação:

```text
publish_retification
  └─ _assert_versao_canonica(item.base_snapshot.content, "O conteúdo-base desta Retificação")

_materialize_affected_versions
  └─ para cada fronteira de vigência:
       _consolidate(_original_version(edital).content, acts)
       └─ _assert_structurally_publishable(content, boundary)
            └─ _assert_versao_canonica(...)
```

O conteúdo consolidado herda o `schemaVersion` do conteúdo-base, porque consolidar é aplicar atos
sobre ele — e `schemaVersion` está em `CAMPOS_DE_IDENTIDADE`, que nenhuma Alteração endereça. Logo,
sem intervenção, todo Edital publicado em v4 fica travado no primeiro dos dois pontos.

### Por que elevar é legítimo aqui, e não era antes

O comentário que justifica a recusa diz que a alternativa "construiria compatibilidade para conteúdo
que não existe". Isso era exato para 2→3 e 3→4: eles acrescentaram seções ao catálogo e a coleção
`documentRequirements` inteira, e qualquer valor que uma conversão inventasse seria afirmação
normativa — dizer que um Edital não exige documento algum **é dizer alguma coisa**.

O incremento da 012 é de outra espécie: aditivo, sobre uma coleção que já existe, e com a leitura da
ausência **declarada na própria spec** — sem a declaração, uma avaliação por inscrição (FR-009); sem
o limite, limite não declarado (FR-066). A função de elevação não escolhe nada: ela escreve na forma
nova o que o conteúdo já dizia por omissão.

### O que uma primeira leitura deixou passar, e que muda a decisão

Elevar o conteúdo-base **não basta**, e a razão está em como a consolidação funciona.
`_materialize_affected_versions` e `_content_in_force` não partem da última versão consolidada:
partem de `_original_version(edital).content` e **reaplicam todos os atos publicados**, em ordem, a
cada fronteira de vigência. Os atos são reaplicados sempre, e o que eles carregam é o valor
literal — `AlteracaoNormativa.new_value`, gravado quando o ato foi elaborado.

Disso decorrem dois históricos mistos que uma elevação só da base não cobre:

1. **Ato v4 que acrescenta ou substitui Etapa.** `newValue` é o objeto Etapa como ele era antes do
   incremento, sem as duas propriedades. Reaplicá-lo sobre base elevada **reintroduz** uma Etapa
   fora de forma, e a materialização passa a falhar por campo obrigatório ausente — o Edital fica
   inconsolidável, que é pior do que o problema original.
2. **Ato v5 sobre conteúdo v4 não elevado.** Um ato que endereça `/stages/id=X/maximumScore` não
   encontra o caminho, e a alteração é rejeitada.

### A decisão

Uma função pura em `publicacoes/domain/elevacao.py`, sem efeito colateral e sem autoria, em duas
formas:

```text
elevar(conteúdo) -> conteúdo'
  schemaVersion: 4 -> 5
  stages[*].evaluationsPerRegistration: ausente -> 1
  stages[*].maximumScore:               ausente -> null

elevar_valor(targetPath, valor) -> valor'
  o caminho endereça uma Etapa ou a coleção /stages  -> eleva a entidade
  qualquer outro caminho                             -> devolve intacto
```

**A segunda forma é o que torna a consolidação consciente dos atos.** Ela é **path-aware** de
propósito, e a classificação é explícita — descobrir "é dict, então é entidade" acertaria hoje e
falharia em silêncio amanhã, que é exatamente o que `colecoes.py` já recusa fazer:

| caminho | o que `newValue` é | eleva? |
|---|---|---|
| `/stages/-` | uma Etapa nova — **é assim que o ADD endereça**, com o token de acréscimo, e não por `id=` | sim |
| `/stages/id=<uuid>` | uma Etapa inteira, substituída | sim |
| `/stages` | a coleção inteira, se algum dia for admitida | sim, item a item |
| `/stages/id=<uuid>/<campo>` | um escalar — decimal, booleano, texto | **não** |
| qualquer outro caminho | outra coleção do conteúdo | não |
| `REMOVE`, em qualquer caminho | não há `newValue` | nada a fazer |

Não é preciso etiquetar cada ato com a versão em que nasceu, e essa é a simplificação que sustenta o
desenho: **a elevação é idempotente**. Entidade que já tem as duas propriedades atravessa a função
inalterada, e `null` continua `null` — porque ausente e nulo significam a mesma coisa (T-002).
Aplicá-la incondicionalmente a toda base e a todo `newValue` de Etapa produz o mesmo resultado que
uma consolidação etiquetada por versão produziria, sem armazenar versão por ato nem manter uma
tabela de conversões entre pares de versões.

### Onde ela é aplicada — e por que "três pontos" era pouco

A primeira redação desta decisão listou três pontos de aplicação, e isso deixava metade do fluxo
descoberta. O conteúdo e as alterações são lidos em mais lugares do que a consolidação:

- `create_retification` e `edit_retification` usam `base.content` diretamente, em
  `_apply_declared_changes` e em `_replace_changes` — e é `_replace_changes` que **deriva as
  precondições** por `derive_preconditions`. Precondição derivada sobre base não elevada é
  precondição que não vai bater quando a publicação usar a base elevada;
- `publish_retification` aplica `_changes_payload(item)` **diretamente** sobre
  `item.base_snapshot.content`, e não pelo caminho de `_acts`;
- `_content_in_force` e `_materialize_affected_versions` partem de `_original_version(...)`.

**O caso perigoso, e ele não é teórico.** `derive_preconditions` devolve cadeia vazia para `ADD` —
acréscimo não tem conteúdo anterior a hashear, e a spec da 004 diz isso de propósito. Logo, uma
Retificação v4 **em voo** com `ADD` de Etapa **não tem precondição que a recuse**. Sem elevar as
alterações antes de aplicá-las, `publish_retification` produziria conteúdo com Etapa em forma v4 e
criaria a `Publicacao` carimbando `canonical_schema_version = 5` — um registro afirmando uma versão
que o conteúdo não tem, que é exatamente o que `_assert_versao_canonica` existe para impedir. E não
há conferência de forma entre `apply_changes` e a criação da `Publicacao`: quem valida é
`_materialize_affected_versions`, que roda depois.

**A regra, então, é de fronteira e não de ponto**, e cabe em duas linhas:

> Todo conteúdo lido da persistência passa por `elevar()` antes de qualquer uso.
> Todo conjunto de alterações — vindo do banco ou da requisição — passa por `elevar_alteracoes()`
> antes de qualquer uso.

Concretamente, isso alcança as sete fronteiras do fluxo: criar Retificação, editar ou rebasear,
publicar, gerar o documento da publicação, verificar efeito prático e conflito, reconstruir o
conteúdo vigente, e materializar as versões futuras reaplicando os atos publicados.

A economia que torna isso viável é que os dois pontos de leitura são poucos e nomeados:
`_changes_payload` já é o único lugar que carrega alterações do banco — e é chamado tanto por
`_acts` quanto por `publish_retification` —, e a base sempre chega como `VersaoConsolidada.content`.
Elevar dentro desses dois é o que faz nenhuma fronteira depender de alguém lembrar. As alterações
que chegam pela requisição, em criar e editar, passam pela mesma função antes de serem derivadas e
gravadas: idempotente, é inócua quando o cliente já mandou a forma nova, e fecha a lacuna quando não
mandou.

As linhas gravadas não mudam: `VersaoConsolidada`, `Publicacao` e `AlteracaoNormativa` continuam
append-only e com trigger no banco, e a Publicação original permanece byte a byte o que foi
publicado. A elevação acontece **na leitura**, e o que ela produz vai para uma Versão Consolidada
nova — que é artefato novo, com hash próprio, como toda Versão Consolidada já é.

A nova `VersaoConsolidada` nasce em v5, com hash próprio — como toda Versão Consolidada nova já
nasce. Os dois campos elevados **não entram em `ProvenienciaConteudo`**, porque proveniência mapeia
caminho a Publicação que o alterou, e nenhuma Publicação os alterou. É precisamente o que D-002
exige: elevação sem autor, porque não é retificação.

### A consequência que precisa ser dita

Precondição de conteúdo por hash (`HASH_MISMATCH`) é calculada sobre a **entidade endereçada**. Uma
Retificação cujo rascunho foi montado antes do incremento carrega hash de Etapa sem os dois campos
novos; depois do incremento, a mesma Etapa elevada tem outro hash, e a publicação dela é recusada.

Isso não é defeito: é a proteção de FR-036 fazendo o que existe para fazer, e o próprio código já
nomeia a saída — "devolver e reenviar o rascunho sobre a versão vigente reconstrói a precondição".

O alcance é a janela de implantação, e só ela: Retificação **em elaboração ou homologada** no
momento do deploy. Retificação **já publicada** é reaplicada a cada materialização — e é por isso
que a elevação alcança os atos —, mas as precondições dela não são reconferidas na reaplicação:
`_reject_stale_changes` roda em `publish_retification`, e não em `_materialize_affected_versions`.
Ato já publicado, portanto, não é derrubado retroativamente por hash.

### Os testes que esta decisão obriga

Histórico misto não é hipótese; é o caso normal de qualquer Edital publicado antes do incremento e
retificado depois. São quatro cenários, e nenhum deles é opcional:

**Histórico misto** — Edital publicado antes do incremento e retificado depois:

1. Edital v4 **sem** Retificação, retificado pela primeira vez depois do incremento.
2. Edital v4 **com** Retificação publicada que **acrescentou** Etapa por `/stages/-`, retificado de
   novo depois.
3. Edital v4 com Retificação publicada que **substituiu** Etapa inteira por `/stages/id=<uuid>`,
   idem.
4. Edital v4 com Retificação publicada que substituiu **um campo** de Etapa — o caso que prova que
   a elevação não toca escalar.

**Retificação atravessando o deploy** — os três que a lista original não tinha, e que cobrem o caso
sem precondição:

5. Retificação v4 **em elaboração** com `ADD` de Etapa, publicada depois do incremento.
6. Retificação v4 **homologada** com `ADD` de Etapa, publicada depois do incremento — a que não
   pode ser reelaborada sem devolver, e por isso a que mais dói se falhar.
7. Retificação **criada depois** do incremento sobre `baseSnapshot` v4: as precondições nascem
   sobre base elevada e batem na publicação.

Em todos os sete: a `Publicacao` e a Versão Consolidada nova nascem na versão vigente **e bem
formadas** — nenhuma Etapa sem as duas propriedades —, e o `content_hash` de toda `Publicacao` e de
toda `VersaoConsolidada` anterior permanece idêntico ao que era antes do deploy.

**Alternativas recusadas.** Migrar as linhas de `VersaoConsolidada` para v5 — reescreve artefato
publicado e seu hash, contra a Constituição e contra as triggers de `0007`. Aceitar a
irretificabilidade — é o que a spec recusou, com razão: seria consequência de produto disfarçada de
precondição de implantação.

---

## T-002 — A leitura da Etapa, e por que ela não é a elevação

A elevação resolve **retificar**. Ela não resolve **ler**, e não deve: elevar no caminho de leitura
pública faria a tela mostrar conteúdo que o `content_hash` publicado não cobre, e a verificação de
integridade da 005 passaria a comparar coisas diferentes.

Então convivem, legitimamente, Etapas publicadas com e sem os dois campos. Quem lê não pode precisar
saber disso:

```text
avaliacoes_previstas(etapa) -> int         # ausente => 1   (FR-009)
pontuacao_maxima(etapa)     -> Decimal|None # ausente => None (FR-066)
```

Dois leitores de domínio, num módulo só, usados por todos os consumidores — Mesa, distribuição,
validação da pontuação e documento materializado. Nenhum consumidor testa presença de chave por
conta própria; a regra de ausência tem um lugar, e é este.

---

## T-003 — Onde o código vive

App novo `processo_seletivo.avaliacoes`, pelo mesmo critério que criou `comissoes` na 011: é domínio
operacional próprio — atribuição, avaliação, impedimento —, e não ciclo de vida normativo de Edital
nem organização de comissão.

As telas continuam em `interface`. Não há canal novo: os dois atores da 012 — presidência e
avaliador — são institucionais, autenticados pelo mesmo mecanismo, na mesma base visual. `portal`
existe porque a 009 tinha um ator de fora; aqui não há.

O incremento canônico é a exceção, e ele **não** mora no app novo: ele toca `editais` (modelo,
serializer, rascunho, validação), `publicacoes` (snapshot, elevação, PDF) e o contrato da 001. É
conteúdo normativo, e conteúdo normativo mora onde sempre morou.

---

## T-004 — A forma da Atribuição

Espelha `AlocacaoEtapa`, com a inscrição a mais:

```text
Atribuicao
  membro     FK MembroComissao (PROTECT)
  edital     FK Edital (PROTECT)
  etapa_id   UUID            # identidade no conteúdo publicado, não FK
  inscricao  FK Inscricao (PROTECT)
  ativo, criado_em/por, inativado_em/por
```

`etapa_id` não é chave estrangeira pela razão que a 011 já escreveu e que continua valendo: existe
Etapa real no Edital vigente sem linha de elaboração para uma FK apontar, porque a Retificação sabe
acrescentar item a coleção com chave e não escreve de volta em `editais`.

A FK para `MembroComissao` — e não para `AlocacaoEtapa` — é D-004 da spec. Consequência técnica
direta: **perder a alocação não escreve em Atribuição nenhuma**. A revogação é a conjunção sendo
avaliada (T-005), e devolver a alocação restaura o acesso às mesmas linhas. Perder o **vínculo de
comissão** é outra coisa: o vínculo novo é outra linha, e as Atribuições do antigo não revivem
(EC-013).

Unicidade parcial sobre `(membro, edital, etapa_id, inscricao) WHERE ativo` — FR-003, e o mesmo
padrão da 011: readicionar cria linha nova e o histórico permanece.

---

## T-005 — A Mesa, e o custo dela

A autorização composta é resolvida em duas consultas, e nunca por linha:

```text
etapas_autorizadas(ator, edital)      # 1 consulta — a forma em lote que a 011 entregou
  ∩ {etapa pedida}                    # em memória
Atribuicao.filter(membro=…, edital=…, etapa_id=…, ativo=True)
  .select_related("avaliacao")        # 1 consulta paginada
```

`pode_atuar_na_etapa` continua sendo o guard da rota individual — abrir **uma** inscrição, **um**
documento —, onde custa duas a três consultas e é chamado uma vez. Nas listagens, só a forma em
lote. Um teste deve exigir que as duas nunca divirjam, como o que a 011 já tem.

Contagens da Mesa e da distribuição saem de agregação no banco, nunca de laço sobre linhas.

---

## T-006 — A porta do avaliador, e a mecânica que já existe

`documento_da_inscricao` na `interface` já faz tudo o que a US3 pede: confere o hash **antes do
primeiro byte**, serve a cópia conferida — e não o arquivo reaberto —, registra `CONSULTAR_DOCUMENTO`
e registra `INTEGRIDADE` quando diverge. O que não serve é a autorização: `inscricao:consultar` é do
Gestor e alcança o Edital inteiro (D-005 da spec).

Então: rota nova, autorização composta, e as mesmas funções por baixo — `copia_verificada`,
`entregar`, `marcar_como_privada`, `record_event`. Nada disso é reescrito, e nada de `portal` ou da
consulta administrativa muda.

O documento é apresentado sob o Documento Exigido que ele atende, usando `requisitos_da_inscricao`
sobre o conteúdo da **versão que a inscrição aceitou** — a mesma escolha que a consulta
administrativa já faz, e pela mesma razão: usar a vigente reescreveria o passado na tela de quem
confere.

---

## T-007 — A Avaliação, a conclusão e o que a reabertura não pode destruir

```text
Avaliacao
  atribuicao  OneToOne (PROTECT)          # FR-005, garantia de banco
  estado      RASCUNHO | CONCLUIDA
  pontuacao   Decimal(7,4) null
  parecer     text
  versao      FK VersaoConsolidada null   # preenchida na conclusão (FR-071)
  revision    PositiveBigInteger          # compare_and_swap
  identity_subject / etapa_id / inscricao_id   # cópia imutável, e a identidade é a da pessoa
  concluida_em / concluida_por
```

**Por que a tripla copiada, e por que ela não usa `membro_id`.** FR-074 exige, como garantia e não
como disciplina de tela, no máximo uma Avaliação **concluída** por pessoa, inscrição e Etapa. A
condição atravessa `Avaliacao → Atribuicao → membro`, e índice não atravessa junção — daí a cópia.

Mas a coluna copiada é `identity_subject`, e **não** `membro_id`, porque `MembroComissao` é
**vínculo**, não pessoa: remover alguém inativa a linha e readicionar cria outra, pelo padrão que a
011 adotou de propósito. Um índice sobre `membro_id` deixaria remover-e-readicionar liberar uma
segunda conclusão da mesma pessoa sobre a mesma inscrição — exatamente o contorno que FR-074 fecha.

`(identity_subject, etapa_id, inscricao_id) WHERE estado = 'CONCLUIDA'` é a garantia certa, e ela
conversa com FR-006: a autoria já é histórica e já se registra pelo identificador estável.

O risco usual de denormalizar — divergir — não existe: os três valores são escritos uma vez, na
criação, a partir da Atribuição, cuja quádrupla nunca muda.

**A reabertura não destrói o que foi concluído** (FR-094). Cada conclusão grava uma linha
append-only:

```text
ConclusaoAvaliacao   (append-only, como AtoAdministrativo e VersaoConsolidada)
  avaliacao, ordem, pontuacao, parecer, versao, concluida_em, concluida_por
```

Depois de quantas reaberturas vierem, "o que João havia concluído antes da terceira" é uma consulta,
e não uma arqueologia de trilha. A trilha continua registrando que o ato aconteceu; o conteúdo do
ato vive no domínio, como FR-054 já manda.

---

## T-008 — Ato com motivo, e o que cada registro responde

O projeto já separa duas coisas que parecem uma, e a 012 usa as duas exatamente como
`processos/application/commands.py` faz:

| | responde |
|---|---|
| `AtoAdministrativo` | **o ato**: agregado, operação, ator, **motivo obrigatório**, instante |
| `RegistroAuditoria` | **a trilha**: mais a base de autorização, o escopo e a correlação |

Os atos da 012 que exigem motivo — impedimento, reabertura e a inativação de Atribuição sob
Avaliação concluída (FR-092) — gravam os dois. É de `AtoAdministrativo` que FR-093 lê o motivo para
mostrar ao lado da avaliação invalidada, e é por ele já existir, genérico por
`aggregate_type`/`aggregate_id` e protegido por trigger, que a 012 não cria tabela de motivos.

`record_event` recebe `new_state=""` e `new_revision=None` para os agregados sem ciclo de vida, como
a 011 fez — nenhuma coluna nova, nenhum estado inventado para satisfazer a forma do registrador
(FR-070).

---

## T-009 — Impedimento

Entidade própria, porque é consultada como regra antes de cada distribuição:

```text
Impedimento
  identity_subject, inscricao FK, motivo (obrigatório), criado_em/por
```

**Ancorado na pessoa, não no vínculo** (FR-099). Um impedimento preso a `MembroComissao` morreria
quando a pessoa saísse da comissão, e readicioná-la seria o caminho para contorná-lo — o mesmo
buraco que FR-074 fecha, pela mesma razão. Impedimento nomeia o que não muda por reorganização
administrativa; ele não pode depender de uma linha que a reorganização recria.

**Sem coluna `ativo`.** Revogar impedimento não está na spec, e criar o campo agora seria inventar
ciclo de vida sem caso de uso. A consulta é "existe Impedimento para este par", e não "existe
Impedimento ativo".

O ato de registrar impedimento faz **duas** coisas na mesma transação: cria o Impedimento e inativa
as Atribuições ativas daquele par, gravando `AtoAdministrativo` por Atribuição inativada (FR-041). A
confirmação declara antes quantas serão inativadas — a contagem é uma consulta, e retirar trabalho
de alguém não pode ser efeito colateral silencioso de registrar um motivo.

O efeito sobre a Avaliação já concluída é o de FR-079, no vocabulário de FR-075: **preservada e
tornada inelegível**. Preservada porque nada nela é apagado ou alterado, e ela continua consultável
com o ato ao lado; inelegível porque deixa de integrar o conjunto que a 013 consome, o que libera a
vaga (FR-090). A 012 não se pronuncia sobre o mérito da nota — tirar do conjunto quem não podia
estar nele não é julgar o que ele escreveu.

A autorização continua com **duas** condições (FR-080): o impedimento age removendo a Atribuição, e
não somando verificação por linha. Isso é o que impede que FR-048 seja violado justamente na
listagem mais cara da feature.

---

## T-010 — Concorrência, repetição e idempotência

Nenhum mecanismo novo. Os três que existem, e onde cada um entra:

| risco | mecanismo | onde |
|---|---|---|
| perda de atualização, julgamento conflitante | `compare_and_swap` sobre `revision` | gravar e concluir Avaliação (FR-081, FR-087) |
| conclusão sobre estado que mudou | a mesma comparação | concluir contra reabertura (FR-082) |
| duplicidade por reenvio | `reserve()` / `IdempotencyRecord` | os quatro atos da presidência (FR-084) |
| autorização obsoleta | `comando_de_comissao` da 011 | distribuir, **remover Atribuição**, impedir, reabrir (FR-086) |
| dado normativo obsoleto | leitura da versão **dentro** da transação | conclusão (FR-088, FR-096) |

Os **quatro** atos de quem gere a comissão — distribuir, remover Atribuição, impedir e reabrir —
reutilizam `comando_de_comissao` inteiro: transação, `select_for_update` no Processo, reavaliação de
`pode_gerir_comissao` **depois** do bloqueio, recusa de Processo final e reserva de idempotência
depois de autorizar. Herdar isso é herdar a razão de cada passo, que a 011 documentou. A remoção
entra na lista pelo mesmo motivo dos outros três: ela altera quem tem acesso a quê, e concluí-la sob
autorização que deixou de existir durante a transação seria retirar trabalho sem poder para tal.

A gravação do avaliador não bloqueia contêiner nenhum: é linha própria, e `compare_and_swap` basta.

---

## T-011 — O lote

Uma submissão, N atribuições. Cada uma gera seu evento de auditoria, porque a trilha responde por
agregado — a mesma decisão da alocação em lote da 011, que trocou 160 envios por quatro.

O resultado é declarado (FR-097): quantas atribuídas, quantas recusadas, e o motivo de cada recusa
nomeando a linha. As duas naturezas de recusa de FR-085 caem naturalmente em código: regra sobre a
linha é acumulada e relatada; erro sobre o pedido levanta `DomainError` e a transação inteira
desfaz.

Repetição da mesma chave devolve o desfecho original **sem gravar evento novo** — o curto-circuito
por `ctx.repetido` que a 011 já implementa, e cujo critério é o status, e não o resultado.

---

## T-012 — O nome que a 011 ocupou

`interface/urls.py` tem hoje `path("minhas-etapas/<uuid:edital_id>/<uuid:etapa_id>", views.atribuicao,
name="atribuicao")`, e essa página mostra a **Etapa** do membro. Com `Atribuição` virando entidade
(D-003), o nome é renomeado para `minha_etapa` / `minha-etapa`.

**O caminho da URL não muda** — `minhas-etapas/<edital>/<etapa>` continua igual —, então nada que
esteja fora do repositório quebra. Muda o nome da view e o `name` do reverse, e as referências em
templates.

E é essa mesma página que a 012 preenche: a 011 deixou nela o aviso de que a avaliação seria
disponibilizada quando a Etapa fosse habilitada, e recusou-se a desenhar UI falsa antecipando esta
feature. A Mesa é o que substitui aquele aviso.

---

## T-013 — Escala

Os números da spec, traduzidos em consultas:

- **Mesa com 500 atribuições**: 1 consulta de autorização em lote + 1 paginada + 1 de contagens.
  Nenhuma por linha.
- **Distribuir 1000 inscrições**: uma submissão por lote; carga por pessoa e déficit por inscrição
  saem de agregação, não de laço.
- **Retirar uma pessoa de uma Etapa**: uma escrita — a alocação. Zero escritas em Atribuição
  (FR-069), porque a revogação é computada.
- **Trilha**: filtro por inscrição (`aggregate_id`), por avaliador (`actor_subject`) e por operação,
  que é o que a trilha já indexa e o que a tela de auditoria da 011 já sabe filtrar.

---

## T-014 — O contrato da 001 muda

`ETAPA_PUBLICADA` em `editais/domain/validation.py` é **transcrição** do esquema `EtapaPublicada` do
`openapi.yaml` da 001, e `tests/contract/test_forma_publicada.py` falha se as duas divergirem. O
incremento, portanto, alcança também `specs/001-processo-seletivo-editais/contracts/openapi.yaml`
— `EtapaPublicada` e `EtapaInput` — e a descrição da versão canônica que ele carrega.

Não é exceção a FR-061: é a mesma mudança do FR-007 chegando ao lugar onde a forma publicada é
declarada. O que continua valendo é o resto — nenhuma outra coleção do conteúdo publicado muda.

---

## O que esta pesquisa não decidiu

- **A forma da tela de distribuição.** Se é matriz de pessoas por faixa, seleção de conjunto e
  destino, ou as duas, é decisão de UX que os requisitos não fixam. O que eles fixam é o custo:
  nenhuma submissão por atribuição.
- **Se impedimento deve poder ser revogado.** A spec não pede, e por isso `Impedimento` nasce sem
  coluna de estado (T-009). Se a operação real pedir revogação, é ciclo de vida novo e volta à spec
  — não vira booleano acrescentado em silêncio.
- **A ordenação padrão da Mesa.** Por protocolo, por instante de atribuição ou por perfil — decidida
  na implementação, com o filtro de FR-021 valendo em qualquer uma.
