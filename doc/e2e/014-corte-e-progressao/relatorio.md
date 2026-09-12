# Percurso conduzido — SPEC 014 · Corte e Progressão entre Etapas

**Data:** 11/09/2026 · **Branch:** `claude/spec-014-corte-progressao-b8aa7a` · **Base:** commit `fab0b40`
**Ambiente:** banco isolado `ps_demo_014`, papéis `ps014_migration`/`ps014_runtime` provisionados
pelo superusuário local (24 de 24 tabelas append-only sem `UPDATE` nem `DELETE` para o runtime),
`INTERFACE_SELETOR_IDENTIDADE=true`, servidor em `http://localhost:8014` (entrada `corte-014`
acrescentada ao `launch.json`, sem reescrevê-lo).

**Escopo:** o percurso do [quickstart](../../../specs/014-corte-e-progressao-entre-etapas/quickstart.md),
conduzido pela interface administrativa contra o servidor real — declarar a regra, publicar, cortar,
ver o efeito na Etapa seguinte, continuar, suceder e auditar. O Edital `14/2026` foi montado à mão
pela tela: o `seed_demo` não produz este certame.

## Sobre as evidências

**Não há PNGs em `screenshots/`, e é limitação da sessão, não esquecimento** — o mesmo registrado
pelas auditorias da `020` e da `025`. O painel de navegador desta ferramenta devolve as capturas
para a conversa e não as grava em disco. Cada achado abaixo traz, no lugar da imagem, a **URL, o
controle e o texto literal observado**, que é o que o torna reproduzível.

**Duas coisas foram montadas fora da tela, e as duas são jornada de outra feature.** As inscrições,
as avaliações, a consolidação e os atos de ordenação (computado e por sorteio) foram criados pelos
**mesmos commands da aplicação** que o `seed_demo` usa — nada entrou direto no banco, de modo que
autoria, segregação e auditoria ficam verdadeiras. O que a `014` entrega — declarar a regra,
publicar, cortar, ver o efeito, continuar, suceder e auditar — foi percorrido pela interface.

**O Perfil B roda em escala reduzida, e a redução está declarada.** O quickstart descreve 40 vagas
com 30 suplentes sobre 70 participantes; aqui são **4 vagas com 3 suplentes sobre 10**. A forma é a
mesma — alvo derivado do quadro, empate que admite excedente, continuação admitida —, e o teto de
abertura com mil participantes é medido por teste automatizado (`tests/performance/test_corte.py`),
não pelo percurso.

---

## 1. Veredito

**A feature está entregue pelo canal do ator, e o percurso do gate fecha inteiro.** Declarar a regra
no marco, ser impedido de publicar sem ela, publicar, ler a regra no documento, calcular a faixa,
ser recusado pelo empate estrito, retificar o desfecho, emitir, conduzir a Etapa seguinte com quem
progrediu, ver quem ficou fora **nomeado como tal**, continuar a faixa, suceder a geração e auditar
o corte histórico — os treze passos acontecem pela interface, sem shell e sem banco.

**Oito defeitos foram encontrados, e os oito foram corrigidos nesta sessão, com teste que os
prende.** Três deles impediam o percurso de terminar: a tela do corte devolvia **500** no caso
exato que a feature existe para não resolver sozinha; salvar os Perfis **apagava o marco inteiro**,
levando junto a regra recém-declarada; e quem ficou fora da faixa **sumia** das telas da Etapa
seguinte, que é o que a `UX-026` proíbe em letras. Nenhum seria pego por teste de domínio.

**Quatro tarefas que estavam abertas foram fechadas porque o percurso esbarrou nelas**: a
obsolescência ao abrir o marco (`T085`), a leitura do corte histórico (`T091`), a visão agregada dos
recortes (`T058`) e os testes de reingresso e de remoção da regra (`T078`, `T080`, `T080a`, `T082`).
O teto de abertura (`T093`) também foi medido e prendido.

---

## 2. Os oito achados

### `E2E14-001` — gravar os Perfis apagava os marcos do Perfil

**Onde:** `/gestao/editais/<id>/compor/perfis`, botão **Salvar rascunho**.

Declarada a regra de corte no passo **Classificação**, bastava voltar ao passo **Perfis** — que é
exatamente o que a regra de alvo derivado exige, para declarar qual Modalidade é a ampla
concorrência — e salvar: o `MarcoClassificatorio` desaparecia do banco, com a regra dentro dele.
Observado: `MarcoClassificatorio.objects.count()` passava de 1 para **0**, sem erro nenhum na tela.

**Causa:** `ler_perfis` devolve `classificationMilestones: []` — aquela tela não desenha marcos —, e
`PRESERVADO_DA_ETAPA["perfis"]` não os listava. Como `replace_draft` **apaga e recria**, a coleção
ausente do envio morre em silêncio. É a classe de defeito que o cabeçalho de
`test_round_trip_do_rascunho.py` descreve, encontrada num par que ninguém havia coberto.

**Correção:** `classificationMilestones` entra na lista de preservados do passo dos Perfis — pela
razão **oposta** à do quadro de vagas: quem desenha o marco é a etapa `classificacao`, que tem ramo
próprio na gravação.

**Fechado por:** `tests/interface/test_round_trip_do_rascunho.py::test_regravar_os_perfis_pela_tela_preserva_os_marcos`.

### `E2E14-002` — as recusas da regra de corte não nomeavam o marco

**Onde:** `/gestao/editais/<id>/compor/revisao`, com a regra incompleta.

A Revisão mostrava *"IMPEDE A regra de corte não declara o que acontece com o empate…"* e um atalho
para a tela dos Perfis. Num Perfil com três marcos, a recusa não dizia **qual** abrir. A `FR-182`
pede achado que nomeia o marco, e a `UX-025` proíbe fazê-lo por identificador interno — o caminho
JSON do achado tem o UUID, e ele não é resposta.

**Correção:** as dez recusas da regra (`cut_rule_*`) passam a nomear o marco pelo `code` — o que
quem elabora digitou e o que o documento publica. Observado depois: *"A regra de corte do marco
TITULOS não declara o que acontece com o empate…"*.

**Fechado por:** `tests/unit/editais/test_regra_de_corte.py::test_as_recusas_da_regra_de_corte_nomeiam_o_marco`.

### `E2E14-003` — a tela do corte devolvia 500 no empate que atravessa a faixa

**Onde:** `/gestao/editais/<id>/marcos/<marco>/corte`, com alvo estrito e empate na fronteira.

Com oito participantes acima e três empatados na nona posição sob alvo dez, abrir a tela devolvia
`EmpateAtravessaOCorte at /gestao/…/corte` — traceback do Django, e não a recusa. **É o caso que a
feature existe para não resolver sozinha**, e ele derrubava a página em vez de explicá-la.

**Causa:** `faixa.calcular` levanta uma exceção de domínio própria; a view traduz apenas
`DomainError`, e ninguém convertia uma na outra.

**Correção:** `calcular_corte` traduz o empate em recusa nomeada, com as posições. Observado na
tela logo depois: *"O empate na posição 9, com 2 participantes, atravessa a última posição da faixa,
e este Edital publicou alvo estrito: o sistema não escolhe entre empatados. O caminho é julgar o
desempate ou retificar o desfecho declarado no marco."* — o número errado dessa frase é o achado
seguinte.

**Fechado por:** `tests/integration/classificacao/test_emissao_do_corte.py::test_o_empate_que_atravessa_a_faixa_sob_alvo_estrito_recusa_em_vez_de_estourar`.

### `E2E14-004` — a recusa contava o empate errado

**Onde:** a mesma recusa, depois de corrigida a `E2E14-003`.

A mensagem dizia *"com 2 participantes"* para um empate de **três**. A conta era "os que sobraram
fora da faixa, mais um", e ela só vale quando exatamente um empatado está dentro. Com dois dentro e
um fora, quem lê a recusa subestima quantos desempates terá de julgar.

**Correção:** conta-se quantos empataram **naquela posição**, e não quantos sobraram.

**Fechado por:** `tests/unit/classificacao/test_faixa.py::test_a_recusa_conta_todos_os_empatados_na_posicao_e_nao_so_os_de_fora`.

### `E2E14-005` — a Retificação não alcançava o desfecho do empate

**Onde:** `/gestao/editais/<id>/retificar`.

O passo 3 do Percurso 2 manda *"retificar o marco para admite excedente"* — e não havia campo. A
Retificação oferecia `targetCount` e `surplusCount` e mais nada do corte. O comentário do módulo
explica por que a espécie do alvo, a Etapa governada e a continuação ficam de fora (caixa de texto
publicaria valor que o cálculo não interpreta); **o desfecho do empate não tem esse problema** —
são dois valores fechados — e simplesmente faltava.

**Correção:** `cutRule/tieOutcome` entra como `REFERENCIA`, com as duas opções escritas como a tela
de composição as escreve, e a escolha conferida contra a lista. Observado depois, na Retificação
publicada: `…/cutRule/tieOutcome · REPLACE · STRICT → ADMITS_SURPLUS`.

**Fechado por:** `tests/interface/test_corte.py::test_a_retificacao_alcanca_o_desfecho_do_empate_com_as_duas_opcoes`.

**Aberto, e é governança do usuário:** a espécie do alvo, a Etapa governada e a continuação
continuam fora da tela. Os três são igualmente enumeráveis hoje, e a mesma solução serviria —
mas ampliá-la sem decisão sua seria decidir por você.

### `E2E14-006` — a tela do corte identificava quem progride por UUID

**Onde:** a tabela **Participantes considerados**.

A coluna *Inscrição* imprimia `7e70b0c1-bbb1-4b51-a0e0-4e8882a078fc`. Catorze linhas assim, e
conferir quem progrediu exigia traduzir os identificadores por fora. A casa inteira escreve
`protocolo — nome` nessa coluna, inclusive a tela do ato de ordenação; o corte era a exceção, e a
`UX-025` proíbe identificador interno.

**Correção:** uma consulta só hidrata protocolo e nome. Observado depois: `1º · INS-2026-1401 —
Candidata 1401 · Progride`.

**Fechado por:** `tests/interface/test_corte.py::test_a_tela_do_corte_identifica_quem_progride_pelo_protocolo`.

### `E2E14-007` — quem ficou fora da faixa sumia das telas da Etapa seguinte

**Onde:** `/gestao/editais/<id>/distribuicao/<etapa-governada>`.

O painel dizia **14 inscrições submetidas** e a tabela listava **11**. Os três que a faixa não
alcançou não apareciam em número nenhum, em filtro nenhum, em lugar nenhum — e o comentário do
próprio template promete que *"participantes, eliminadas antes e aguardando a anterior somam o total
submetido"*. Com o corte, a identidade deixou de fechar, e o defeito é exatamente o que a `UX-026`
nomeia: **não sumir da tela**.

**Causa:** o estado `fora-do-corte` existia no panorama desde a implementação, mas `contagens` não o
expunha e a tela não tinha filtro para ele.

**Correção:** a contagem entra na partição e a Mesa ganha o filtro **fora do corte**. Observado
depois: *"3 fora do corte"*, e as três linhas com a causa *"fora da faixa que progride para esta
Etapa"*.

**Fechado por:** `tests/integration/resultados/test_progressao_com_corte.py::test_a_particao_da_etapa_governada_fecha_com_o_total_submetido`.

### `E2E14-008` — a recusa de distribuir dizia a causa errada

**Onde:** a mesma tela, ao selecionar alguém fora da faixa e distribuir.

A recusa era *"Uma ou mais inscrições selecionadas não participam desta Etapa: elas foram eliminadas
numa Etapa anterior ou ainda aguardam o resultado da anterior."* — e **nenhuma das duas coisas era
verdade**. Quem ficou fora foi considerado, tem posição na ordem, e a norma publicada o deixou de
fora. A frase era anterior à feature e mandava quem conduz o certame procurar uma eliminação
inexistente.

**Correção:** os três pontos que repetiam a frase — distribuir, consolidar e registrar ocorrência —
passam a dizer qual causa incide, e cobrem o caso misto. Observado depois: *"Uma ou mais inscrições
selecionadas estão fora do corte: a faixa publicada para esta Etapa não as alcançou. Elas continuam
registradas no corte emitido, com posição e causa."*

**Fechado por:** `tests/integration/resultados/test_progressao_com_corte.py::test_a_recusa_de_distribuir_quem_ficou_fora_diz_o_corte_e_nao_a_eliminacao`.

---

## 3. O percurso, passo a passo

### Percurso 1 — declarar a regra (`US1`, `SC-058`)

| Passo | Observado |
|---|---|
| A seção **Regra de corte** no marco | Seis controles, com a ajuda de cada um: *"Este marco não corta"*, *"Uma quantidade fixa, publicada abaixo"*, *"Quantas vagas o quadro publicar no recorte"*, *"Todos os empatados progridem"*, *"A faixa para no alvo"*, *"Etapa que o corte alimenta"*, *"Faixa seguinte"* |
| Declarar e recarregar | Os seis valores voltam: `FIXED / 10 / 0 / STRICT / Entrevista / NONE` |
| A ampla concorrência, no passo dos Perfis | O seletor nasce com as três Modalidades e o rótulo do vazio — *"Nenhuma — a ampla concorrência é só a linha geral do quadro"* |
| Alvo **derivado** com número digitado | A tela **normaliza**: escolhida a espécie derivada, o alvo fixo não viaja. É decisão registrada em `_regra_de_corte`, e o quickstart previa recusa — a divergência é de redação do guia, não de comportamento |
| Desfecho do empate em branco → publicar | Impedida: *"A regra de corte do marco TITULOS não declara o que acontece com o empate…"* |
| Governar uma Etapa que alimenta a própria ordem | Impedida: *"…governa uma Etapa que alimenta a própria ordem do marco: o universo da ordem passaria a depender do corte que ela produz"* |
| Alvo derivado com quadro parcial | Impedida, **nomeando o recorte**: *"…e não há linha para Preto, pardo ou indígena"* — e **nenhuma linha é exigida da Modalidade AC declarada como ampla concorrência**, que é a armadilha da `D-014` |
| Publicar | Passa. No documento: *"Corte: Progridem para Entrevista os 10 (dez) primeiros desta ordem."* e *"Corte: Progridem para Análise documental os primeiros desta ordem, até o número de vagas ofertadas no recorte, mais 3 (três) suplentes."* |

### Percurso 2 — emitir o corte (`US2`, `SC-055`, `SC-059`)

Com catorze inscritos, oito pontuações distintas e **três empatados na nona posição**:

1. Alvo estrito → **recusa** nomeando a posição e o tamanho do empate (`E2E14-003`, `E2E14-004`).
2. Retificação do desfecho para *admite excedente* (`E2E14-005`), publicada com segregação de
   funções observada — `ana.elaboradora` cria, `beatriz.presidencia` homologa, `carlos.publicador`
   publica; a tentativa de acumular os três foi recusada com *"Uma pessoa não pode elaborar,
   homologar e publicar."*
3. A tela recalcula: **alvo apurado 10, suplentes 0, progridem 11, ficam fora 3, última posição
   alcançada 9º** — e a décima primeira linha traz **Excedente por empate**.
4. Emitido. *"Corte emitido. O ato é imutável, e quem ficou fora continua legível nele."*
5. Os **catorze** considerados constam, cada um com posição, consequência e causa.

### Percurso 3 — conduzir a Etapa seguinte (`US3`, `SC-056`)

- A Entrevista lista **11** — a faixa —, e a contagem confere com alvo mais excedente por empate.
- Os **3** de fora aparecem no filtro **fora do corte**, com a causa (`E2E14-007`).
- Distribuir um deles é recusado, dizendo que está **fora do corte** (`E2E14-008`).

### Percurso 4 — a faixa seguinte (`US4`, `SC-064`, `SC-065`)

- No Perfil B: **alvo apurado 4**, com *"lido da linha do quadro de vagas deste recorte"* à vista, e
  suplentes 3 — faixa de **7**.
- Continuação com quantidade 2 e motivo: *"11/09 21:01 — faixa inicial, até a posição 7"* e
  *"11/09 21:01 — continuação, da posição 8 em diante — Indeferimento de duas inscrições da 1ª
  faixa."* As duas na mesma geração; a anterior continua vigente.
- No Perfil A, que publicou `continuation: NONE`, **o formulário da faixa seguinte não existe**.
- **A fronteira**: em nenhuma tela, mensagem ou documento deste percurso aparecem as palavras *vaga
  ocupada*, *vaga preenchida* ou *déficit*.

### Percurso 5 — a obsolescência (`US5`, `SC-062`, `SC-063`)

- Sucedida a ordem, o marco mostra **A faixa emitida está obsoleta**, com a causa *"A ordem que este
  corte leu foi sucedida"* — era a `T085`, que estava aberta.
- A Etapa governada recusa trabalho novo: *"Esta Etapa não pode ser consolidada: a faixa que governa
  esta Etapa está para trás, e o caminho é emitir a geração sucessora — …"*.
- Sucedida a geração no Perfil B, a Etapa governada passa a ler **apenas** a geração nova: sete
  participantes, e não os nove das duas faixas anteriores.

### Percurso 6 — auditar (`US6`, `SC-061`, `SC-070`)

A rota `cortes/<corte_id>` era a `T091`, aberta. Implementada e percorrida:

- O corte sucedido continua legível, com **Esta geração foi sucedida** no alto.
- A regra aparece na **versão que o corte congelou**, e os nomes vêm dali — não da vigente.
- A reprodução a partir do universo declarado: *"A faixa reproduz: 7 progridem, até a posição 7."*
- A auditoria da emissão está na mesma tela, sem tocar no banco: **ator, instante, recorte, ordem
  citada e alvo apurado** (`SC-070`).

---

## 4. O que fica aberto

| Item | Situação |
|---|---|
| `T035` — a regra na tela de conferência | **Não se aplica.** `revisao.py` não desenha marco nenhum: a Revisão lista Identificação, Perfis, Cronograma, Etapas, Documentos, Anexos e Conteúdo. Acrescentar só a regra de corte ali criaria uma seção de marco que existe para um campo |
| `T092` — fixture de bytes do documento | **Nada a regenerar.** O Edital da fixture de contrato não declara regra de corte, e os bytes não mudaram — a suíte fecha verde sem tocá-la |
| Retificação da espécie do alvo, da Etapa governada e da continuação | **Aberto, e é decisão sua** (`E2E14-005`) |
| A redação do quickstart sobre o alvo derivado com número digitado | **Aberto**: o guia promete recusa onde a tela normaliza, e a normalização é decisão registrada em código |

## 5. Verificação

```
cd backend && DB_NAME=ps_demo_014 make lint check test-pg
```

O resultado da execução final está registrado no commit que fecha este percurso.
