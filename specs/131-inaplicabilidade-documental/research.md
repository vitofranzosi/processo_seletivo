# Research: A inaplicabilidade documental tem fundamento publicado

**Feature**: [spec.md](spec.md) · **Plano**: [plan.md](plan.md) · **Data**: 2026-11-07, sobre a `main`
em `5fcbfa54`, com o PR #425 aberto (correção da `115`, Frente A)

O estudo de 07/11 ([`doc/estudo-nao-se-aplica-2026-11-07.md`](../../doc/estudo-nao-se-aplica-2026-11-07.md))
é o ponto de partida. Esta pesquisa **não repete** o diagnóstico: confere as afirmações dele que a
spec usa (R-009), corrige a que não se sustenta, e acrescenta o que ele não investigou — a composição
do Documento Exigido, o versionamento e os guardiões.

Marcas de evidência, as do estudo: **[T]** teste da suíte · **[X]** execução no banco descartável
`nsa_estudo` · **[C]** leitura do código · **[S]** só na spec · **[N]** norma ou Edital.

## R-001 — Opção 1 × opção 2: só a segunda impede

**Opção 1 — preservar o modelo documental.** Nada muda na composição. A conferência ganha:

- o motivo vinculado, com um campo *"qual cláusula do Edital"*;
- o piso de conteúdo;
- a abertura do arquivo;
- talvez a restrição à base de gestão;
- a ciência no aceite.

**Opção 2 — a condicionalidade explícita.** O Documento Exigido da convocação ganha a condição
publicada, e o *"não se aplica"* da conferência só existe onde ela existe. Leva junto o piso, a
abertura e a ciência da opção 1.

**A pergunta decisiva: o comando consegue recusar o *"não se aplica"* do laudo do PcD sem recusar o
do alistamento militar?**

- **Na opção 1, não.** Os dois são `required: true`, com o mesmo recorte possível, e a diferença
  está só no texto da instrução, que é livre e não normativo para o sistema (D-012). Tudo o que a
  opção 1 acrescenta é verificável só por gente:
  - a cláusula citada pode ser qualquer uma;
  - o motivo pode ser plausível e falso;
  - a ciência depende de quem desfecha ler.

  Ela torna o afastamento **visível e assinado**, e não **impossível**. Nos três obrigatórios do
  estudo, a opção 1 teria mostrado três inaplicabilidades ao gestor, e o aceite continuaria possível
  com um clique a mais.
- **Na opção 2, sim**, e sem julgamento: o laudo não tem condição publicada, logo não há *"não se
  aplica"* para ele, nem pela tela nem pelo comando.

| Critério | Opção 1 | Opção 2 |
|---|---|---|
| Impede o aceite indevido | **Não**: torna visível e depende de leitura | **Sim** no incondicional, por regra no comando; visível no condicional |
| Segurança jurídica | Média: o fundamento é o que o conferente escreveu | Alta: o fundamento é o que o Edital publicou, mais o fato |
| Simplicidade para quem confere | Igual a hoje, mais um campo | Menor: a opção só aparece onde cabe |
| Esforço | Pequeno: conferência e aceite | Médio: conferência e aceite, **mais** a composição (R-004) |
| Superfícies tocadas | ~6 | ~20, a maioria listas de campos com guardião (R-004) |
| Dados existentes | Nenhum efeito | Degrau de elevação, aditivo e sem invenção (R-003) |
| Risco de overengineering | Baixo | Baixo: um campo de texto, sem semântica no sistema (D-002) |
| Coerência com a decisão sobre a condição do candidato da `044` | Total | Total: o campo não é forma estruturada nem entra na aplicabilidade |

**Decisão:** opção 2 (D-001). O esforço a mais é quase todo mecânico — listas de campos que os
guardiões obrigam a manter coerentes — e é exatamente o que torna o campo seguro: nenhuma superfície
pode esquecê-lo em silêncio.

**Alternativas descartadas:**

- *Marcar o documento como "condicional" por um booleano, sem texto.* O conferente teria uma
  permissão sem saber a que condição ela se refere, e o PDF não teria o que imprimir. O booleano é
  derivável do texto, e não o contrário.
- *Ler a condição das instruções.* Ver D-012.
- *Lista fechada de condições* (sexo, idade, nacionalidade, vínculo). É o motor de regras pessoais
  que a 3ª decisão exclui. E não cobre o *"quando for o caso"*, que é o caso mais frequente da
  amostra.

## R-002 — A representação: `requiredWhen`, texto ou nulo

**Decisão:** a chave `requiredWhen` no Documento Exigido publicado. Texto não vazio é condição; `null`
é ausência. No modelo de rascunho, `DocumentoExigido.condicao` (`TextField`, `blank`), gravado vazio
e publicado `null`, no molde do `modalidade_codigo` (`editais/models/documentos.py:65`) [C].

**Por quê:**

- O conteúdo publicado não admite chave ausente:
  `test_todo_campo_do_conteudo_publicado_e_obrigatorio` (`tests/contract/test_forma_publicada.py:112`)
  exige toda propriedade declarada como obrigatória [T].
- O nulo diz *"não há condição"* sem fingir um texto, como o `modalityCode: null` do degrau 17 diz
  *"não recorta pelo código"*.
- O nome segue o `required` vizinho: *exigido quando*.

**Validação, num lugar só:** uma função `problemas_da_condicao` em `editais/domain/documentos.py`,
no molde de `problemas_do_momento` (`:89-146`) [C]. Ela é chamada na validação do rascunho e na da
publicação (`_momento_dos_documentos_exigidos`, `editais/domain/validation.py:3100-3117` [C]), com o
código `document_requirement_condition_incoherent` quando a condição está:

- em documento facultativo;
- em documento da inscrição.

Tamanho máximo de 300 caracteres: a maior condição da amostra tem menos de 150 [N].

## R-003 — O degrau 19 e o censo da elevação

**Decisão:** `SCHEMA_VERSION` 18 → 19. O degrau 19 entra em `DEGRAUS_DE_DOCUMENTO`
(`publicacoes/domain/elevacao.py:117-126`) com `{"requiredWhen": None}`.

**Por quê:** é *conversão sem invenção*, como os degraus 17 e 18. Todo documento publicado antes era
incondicional, porque a condição não existia. A elevação só roda no fluxo de Retificação e no
reaproveitamento, e o literal publicado não muda (FR-725, comentário em
`tests/integration/publicacoes/test_elevacao_de_versao.py:470-476`) [C].

O que acompanha a mudança, e é obrigatório pelos guardiões [C]:

- **o censo:** `CENSO_DOS_DEGRAUS_ANTES_DA_032`
  (`tests/integration/publicacoes/test_elevacao_de_versao.py:477-485`) ganha o 19, com o parágrafo
  *"E muda com a `131`…"*, como a `115` fez para o 18;
- **a cobertura das dúvidas:** `VERSAO_DO_ESQUEMA` da cobertura (`duvidas/domain/cobertura.py:23`)
  passa a 19, e a tabela `COBERTURA` classifica `/documentRequirements/*/requiredWhen`
  (`tests/unit/duvidas/test_cobertura.py:57,70`);
- **o snapshot publicado:** `tests/contract/test_documento_publicado.py:172` compara o PDF byte a byte
  com `snapshot_publicado.json`. O fixture ganha a chave nula, e os bytes não mudam, porque o
  documento sem condição imprime como hoje (FR-4454).

**Leitura nas convocações:** a lista lê `item.versao.content` (`convocacao/application/documentos.py:378-401`)
[C], sem elevar. A leitura da condição é `requisito.get("requiredWhen") or None`, e a versão antiga,
sem a chave, é incondicional (FR-4477).

## R-004 — As superfícies da composição: onde o campo precisa entrar

Levantado em 07/11 (relatório do agente de varredura, conferido por amostragem). Cada linha é uma
lista explícita de campos, e a maioria tem guardião [C]:

| # | Onde | Por quê |
|---|---|---|
| 1 | `editais/models/documentos.py` (`DocumentoExigido`) + migration | o rascunho persiste coluna a coluna |
| 2 | `editais/api/serializers.py:276-306` (`DocumentRequirementSerializer`) | o aninhado descarta chave desconhecida **em silêncio** |
| 3 | `editais/application/draft.py:478-501` | o `replace_draft` mapeia campo a campo |
| 4 | `publicacoes/application/publish_edital.py:386-415` (`_document_requirements`) | o conteúdo publicado |
| 5 | `editais/domain/validation.py:202-222` (`DOCUMENTO_EXIGIDO_PUBLICADO`) | a forma publicada |
| 6 | `specs/001-processo-seletivo-editais/contracts/openapi.yaml:977-1024` | `test_forma_publicada.py:94,100,112` |
| 7 | `editais/domain/mutabilidade.py:481-513` (`CONTRATO`), como retificável | `test_mutabilidade.py:303,324` |
| 8 | `tests/fixtures/snapshot.py:466+` (`rascunho_completo`) | o fixture máximo precisa emitir a chave |
| 9 | `interface/retificacao.py:438-455` (`CAMPOS_DOCUMENTO`) | `test_campos_vem_do_contrato.py:35,78-83` |
| 10 | `publicacoes/domain/alteracoes.py:135-152` (rótulo) | `test_alteracoes_legiveis.py:264` |
| 11 | `interface/revisao.py:935-946` (`LIDOS`) | `test_revisao.py:29,76` |
| 12 | `duvidas/domain/cobertura.py` | R-003 |
| 13 | `interface/forms.py:1631-1757` (`ler_inscricao`, `documentos_do_edital`, `documentos_persistidos`) | a tela reconstrói o documento a cada passo |
| 14 | `interface/templates/interface/_documento.html` | o campo, com a ajuda do UX-302 |
| 15 | `publicacoes/infrastructure/pdf.py:2227-2234` (`texto_do_documento`) e `:4318-4325` (redação 1) | FR-4454 |
| 16 | `publicacoes/domain/elevacao.py` e `shared/canonical.py:156` | R-003 |
| 17 | `editais/domain/documentos.py` (`problemas_da_condicao`) e `validation.py` | R-002 |
| 18 | portal: `_cartao_do_documento_da_convocacao.html` e `portal/obrigacoes.py` (`texto_do_item`) | FR-4475 |
| 19 | gestão: `convocacao_documentos.html` | FR-4454, FR-4459 |

**O reaproveitamento (`023`) não precisa de linha própria.** `remapear` leva toda chave do documento
(`editais/domain/reaproveitamento.py:217-235`), e `payload_do_conteudo` passa a coleção inteira
(`:360`). O que perderia a chave é o `replace_draft`, que é a linha 3 [C].

**A duplicação de Perfil (`043`) não cria Documento Exigido** (FR-645 da `043`;
`editais/domain/duplicacao.py`) [C][S]. A redação inicial desta spec dizia o contrário e foi
corrigida.

## R-005 — A ciência: assinatura do conjunto, no molde da prévia da correção da `120`

**Decisão:** uma função pura `assinatura_das_inaplicabilidades(convocacao_id, conferencias)`, com
`canonical_sha256` sobre o gesto, a convocação e os `id` ordenados das conferências vigentes *"não se
aplica"* de itens obrigatórios. O formulário de desfecho leva a assinatura num campo oculto e a caixa
de ciência. `_recusar_inclusao_sem_documentos` (`convocacao/application/desfechar.py:185`) a recalcula
sob a trava do desfecho, depois da guarda da lista do PR #425 e da guarda das pendências.

**Por quê:** é o padrão que já existe — `alcance.assinatura_da_correcao` e `_conferir_a_previa`
(`convocacao/domain/alcance.py:117-138`; `convocacao/application/convocar.py:405-430`) [C]. Ele dá
três propriedades que uma caixa sem assinatura não dá:

- a ciência é do conjunto **visto**;
- uma conferência registrada no intervalo invalida a ciência;
- nada novo se grava além da trilha.

**Onde fica a prova:** a trilha do desfecho (`record_event` do `CONVOCACAO_DESFECHAR`), cujo `reason`
ganha *"com ciência de N inaplicabilidades: ‹ids›"*, sem motivo (FR-3603 da `115`).

**Alternativas descartadas:**

- *Coluna no desfecho:* tabela append-only, migration e campo novo para guardar o que a trilha e as
  conferências já reconstituem (o conjunto vigente no `registrado_em`).
- *Tabela de ciência:* é a homologação documental que a 3ª decisão exclui.

## R-006 — A guarda conta o condicional, pela versão da lista

**Decisão:** `domain/documentos.py::impede_incluir` recebe se o item é condicional, e o
*"não se aplica"* só atende quando é. `LeituraDocumental` ganha a condição de cada item, lida da
versão no mesmo `prefetch` que já traz o conteúdo (`leituras_por_chamada`, sem consulta nova:
SC-1377).

**Por quê:** é o único ponto que alcança as conferências gravadas antes da feature. Sem ele, a regra
vale só daqui em diante, e o *"não se aplica"* do laudo gravado ontem continua abrindo o aceite
(D-015, P-1).

**Contagens:** `contagens["conformes"]` deixa de somar o *"não se aplica"*
(`convocacao/application/documentos.py:341`) [C][X], e entra `contagens["nao_se_aplica"]`.

## R-007 — A recusa sobre o item excluído pelo recorte

**Causa** [C][X]:

- `apresentar` recusa o item cuja situação na lista é `NAO_SE_APLICA`
  (`convocacao/application/documentos.py:482`).
- `conferir` lê o item (`:641`) e nunca olha a situação.
- `estado_da_convocacao` e `LeituraDocumental.pedidos` descartam esses itens, e por isso a
  conferência gravada não aparece em lugar nenhum.

**Decisão:** em `conferir`, logo depois de ler o item e **antes** da autorização, a mesma recusa de
inexistente que `apresentar` faz. Na abertura do arquivo (`interface:documento-da-convocacao`), a
mesma regra, embora hoje não exista apresentação em item excluído: `apresentar` recusa e
`_aproveitar` o pula (`:186`). A defesa fica no comando, e não na tela (9ª decisão).

## R-008 — As sete decisões de produto do estudo

O estudo deixou sete perguntas ao produto (§8). Cada uma, com a resposta que esta spec propõe:

| # | Pergunta | Recomendada | Por quê | Descartadas | Impacto técnico |
|---|---|---|---|---|---|
| 1 | A dispensa excepcional existe? | **Não no GPS**, até decisão institucional (2ª decisão; P-2) | Nenhum fundamento achado: os Editais têm só *casos omissos*, e o 89/2026 pune a falta com desclassificação [N] | Estado *"Dispensado"* com base de gestão (alternativa B do estudo) | Nenhum. O GPS não oferece substituto para a dispensa: correção com prazo novo, indeferimento e Retificação não são intercambiáveis, e cada uma exige o fundamento próprio. A limitação do GPS não fundamenta indeferimento |
| 2 | O "não se aplica" de obrigatório exige a base de gestão? | **Não**: o alocado registra, no condicional (D-005) | A âncora passa a ser a condição publicada, e o juízo é de fato, como o *conforme*; o controle é a ciência no aceite | Restringir à presidência e a `comissao:gerir` | Nenhum no predicado (FR-3595 da `115` intacta) |
| 3 | Fato já comprovado ao Ifes (Lei 14.129/2021, art. 3º, XIII)? | **No Edital, como condição** (*"exceto para quem concluiu no Ifes"*) (P-4) | Vira figura C sem caminho próprio; a aplicação da lei é da Procuradoria | Caminho próprio na conferência (*"comprovado ao órgão"*) | Nenhum além do campo |
| 4 | O "não se aplica" sobre arquivo exige abrir? | **Sim** (D-008; FR-4460) | O arquivo pode provar que a condição se aplica; a razão da `115` para dispensar a abertura não cobre o caso | Manter sem abertura (5ª decisão: o arquivo, sozinho, não decide; mas olhá-lo é o mínimo) | Uma consulta à trilha, a mesma do *conforme* |
| 5 | A Retificação que retira documento se antecipa na chamada aberta? | **Não** (D-013) | FR-3573 da `115`: a lista é da versão em que nasceu; antecipar seria o *"não se aplica"* sem condição publicada na versão da lista | Permitir o *"não se aplica"* citando a Retificação | Nenhum: a guarda lê a versão do item |
| 6 | O motivo vai à formalização? | **Não; vai a origem e o instante** (D-016) | A FR-3687 da `117` proíbe o motivo no manifesto, e a razão (minimização) continua. **O estudo recomendava levar o motivo, e errou nisso** | Levar o motivo; omitir a origem | Uma situação nova na `117`; nenhuma coluna nova no manifesto |
| 7 | O achado lateral entra? | **Sim, nesta spec** (9ª decisão; D-010) | Recusa de uma linha no comando, com teste | Registro em `doc/` | `conferir` e a abertura recusam o item excluído |

## R-009 — O que do estudo se confirmou, e o que não

| Afirmação do estudo | Status em 07/11 |
|---|---|
| Alocado registra *"não se aplica"* em obrigatório e o gestor aceita sem conforme | Confirmada [X]; continua sem teste na suíte |
| `"."` passa como motivo | Confirmada [X]: `strip` e verificação de vazio (`documentos.py:636,709`) [C] |
| Com arquivo, o *"não se aplica"* não pede abertura | Confirmada [X]; a regra de abertura é só do *conforme* (`:690-707`) [C] |
| A condução soma *"não se aplica"* aos conformes | Confirmada [C][X] (`:341`) |
| A formalização não distingue as origens | Confirmada [T] `test_a_conferencia_nao_se_aplica_e_situacao_nao_se_aplica`; [C] `conjunto.py:167-175` |
| A trilha não tem o motivo | Confirmada [X], e é **regra**, não lacuna: FR-3603 da `115` [S] |
| Recomendação de levar o motivo à formalização | **Não se sustenta**: a FR-3687 da `117` o proíbe [S]. Corrigida na D-016 |
| Recomendação de recusar o *"não se aplica"* no recorte por modalidade | **Substituída**: a condição publicada resolve o laudo do PcD sem regra por recorte, e admite a submodalidade (declaração da Funai em PPIQ) |
| A Retificação não alcança a chamada aberta | Confirmada [X] (gatilho append-only) e [S] (FR-3573 da `115`) |
| Conferência aceita sobre item fora do recorte | Confirmada [X]; causa em R-007 |

## R-010 — A situação nova na formalização

**Decisão:** `formalizacao/domain/nomes.py` ganha `NAO_SE_APLICA_APOS_ANALISE`, com o rótulo *"não se
aplica após análise"*. `_da_convocacao` (`formalizacao/application/conjunto.py:158-197`) a devolve
para a conferência vigente *"não se aplica"*, com `conferido_em` preenchido, e mantém `NAO_SE_APLICA`
para o item excluído pela lista.

O manifesto já tem a coluna do instante da conferência (FR-3687 da `117`;
`formalizacao/application/exportar.py:778-782`), e a usa sem coluna nova.

Fora de `QUE_EXCLUEM` (`nomes.py:68`): não torna a pessoa incompleta.

## R-011 — O piso do motivo

**Decisão:** `motivo_tem_conteudo(texto)`, verdadeira quando há ao menos uma sequência de letras ou
algarismos (`\w` com `re.UNICODE`, sem o sublinhado). Aplicada ao *pendente* e ao *"não se aplica"*
no comando `conferir`, com o código `motivo_sem_conteudo`.

**Por quê esta, e não um tamanho:** *"Não."* tem conteúdo e é ruim; *"................"* tem
tamanho e não tem conteúdo. O piso só exclui o que não diz nada. O que diz pouco é problema de quem
desfecha, e a ciência o põe diante dele (6ª decisão).

## R-012 — Os testes: domínio e integração, sem navegador

Os cenários são os treze do pedido ([contracts/cenarios.md](contracts/cenarios.md)), sobre as
fixtures da `115` (`tests/fixtures/documentos_da_convocacao.py`). Duas chaves novas entram nelas:

- **`ALISTAMENTO`**: obrigatório na convocação, com `requiredWhen`;
- **`LAUDO`**: obrigatório na convocação, por recorte de modalidade.

`_documento(...)` já aceita `**extra` (`:33-45`) [C].

- **Domínio puro:** `estado_do_item`, `impede_incluir`, `motivo_tem_conteudo`,
  `assinatura_das_inaplicabilidades`, `problemas_da_condicao`.
- **Integração:** `conferir`, `desfechar`, formalização, elevação.
- **Interface:** condução, confirmação, formulário de conferência, composição. Pelo cliente de
  teste, como os testes de permissão da `115` já fazem.
- **Nenhum caso novo de navegador.** As jornadas de `tests/navegador/` são do grupo opcional, e o que
  esta spec muda se verifica no HTML servido.
