# Research — Recorte transversal do documento exigido

Fase 0 do plano. Cada decisão diz o que foi escolhido, por quê, e o que foi descartado. Nenhuma
reabre a decisão de 25/09 (D1 a D5); elas decidem **como** cumpri-la.

O levantamento do código foi feito em 25/09/2026, sobre `79e219d` (a `main` depois da #166).

---

## R-001 — O campo novo se chama `modalityCode`, e mora no Documento Exigido

**Decisão.** O conteúdo publicado ganha `documentRequirements[].modalityCode`: texto, anulável.
`null` diz "não recorta por código", como `null` em `profileId` e `modalityId` diz "não restringe".
No rascunho relacional, `DocumentoExigido.modalidade_codigo`, `CharField(max_length=100)` anulável,
com o mesmo tamanho de `ModalidadeConcorrencia.code`.

**Por quê.** O recorte transversal é um **valor**, o código, e não uma referência a entidade. Não há
UUID para apontar: o PcD do C1 e o PcD do C2 são objetos distintos, e o que eles têm em comum é
exatamente o código (D1). Um campo de texto com o código é a forma mais direta de dizer isso, e é
lido pelo mesmo mecanismo de ausência que já produz as quatro formas atuais (`documentos.py`, o
docstring do módulo: *"a aplicabilidade … se lê por ausência de campo, não por linguagem"*).

**Descartado.**
- *Reusar `modalityId` com um valor especial.* Seria a "quinta forma" que o comentário de
  `DOCUMENTO_EXIGIDO_PUBLICADO` diz que a nulidade impede, escondida num campo que já significa outra
  coisa.
- *Uma lista de `modalityId`, uma por Perfil.* São as N linhas de hoje, dentro de uma linha só. Não
  alcança o Perfil acrescentado depois, e cada Retificação de Modalidade teria de reescrevê-la.

## R-002 — A versão canônica sobe para 17, com um degrau de documento

**Decisão.** `SCHEMA_VERSION` passa de 16 para 17, e `DEGRAUS_DE_DOCUMENTO` ganha
`17: {"modalityCode": None}` em `publicacoes/domain/elevacao.py`. `DOCUMENTO_EXIGIDO_PUBLICADO` ganha
`Campo("modalityCode", str, admite_nulo=True)`. `_document_requirements`
(`publicacoes/application/publish_edital.py`) passa a escrevê-lo.

**Por quê.** É o molde do degrau 9, que acrescentou `attachmentId` ao mesmo objeto: aditivo, sobre
coleção que já existe, e com ausência que tem significado declarado. Todo Edital publicado antes
desta feature **não** recortava por código, porque a capacidade não existia, e escrever `null` não
afirma nada que o conteúdo já não dissesse. Sem o degrau, o primeiro Edital antigo retificado depois
da feature pararia em `_assert_versao_canonica`.

**Onde a elevação não roda**, e isso cobre `FR-725`: a consulta pública, o comprovante e o documento
de uma Publicação existente servem o conteúdo **literal**, que é o que o `content_hash` cobre
(docstring de `elevacao.py`). Nenhum documento publicado é regenerado.

**Verificação da vizinha.** A `043-duplicar-perfil` declara *"nenhuma migration, nenhum campo novo no
contrato"* (plano dela, linha 19). Não há disputa pelo degrau 17.

## R-003 — Uma função de aplicabilidade que devolve o veredito, e não só o filtro

**Decisão.** `editais/domain/documentos.py` ganha `aplicabilidade(conteudo, *, profile_id,
modality_id)`. Ela devolve, para **cada** Documento Exigido do conteúdo, um veredito:

- `situacao`: `OBRIGATORIO`, `FACULTATIVO` ou `NAO_SE_APLICA`;
- `recorte`: a forma (`TODOS`, `PERFIL`, `PERFIL_E_MODALIDADE`, `MODALIDADE_EM_TODOS_OS_PERFIS`,
  `TODOS_COM_MODALIDADE_DE_UM_PERFIL`) e os parâmetros (Perfil, Modalidade, código);
- `divergente_do_publicado`: o sinal de `D-007`.

`aplicaveis` continua existindo, com a assinatura trocada para receber o conteúdo (ela precisa dos
Perfis para ler o código da Modalidade escolhida), e passa a ser o filtro sobre `aplicabilidade`.

**Por quê.** `FR-705` exige uma regra só, e `FR-714`/`FR-717` exigem gravar também o "não se aplica"
com a razão. Uma função que só filtra obriga quem grava a **deduzir** a razão depois, que é o
recálculo que `D-003` recusa. Com o veredito completo, o portal (que só quer os aplicáveis), o envio
(que grava tudo) e a reconstrução (que mostra tudo) leem a mesma resposta.

**A regra do código.** O documento com `modalityCode` se aplica quando a Modalidade escolhida,
resolvida **no Perfil da inscrição**, tem aquele código (`FR-701`). Candidato sem modalidade: não se
aplica.

**Os chamadores.** `aplicaveis` tem seis chamadas diretas em produção (`portal/views.py`, duas;
`rascunho.py`, três; `submissao.py`, uma), e `requisitos_da_inscricao` espalha a regra por mais
nove pontos. Os do rascunho continuam sobre a versão vigente:
`_documentos_anunciados`, os descartes por troca de modalidade, `_requisito_aplicavel`,
`documentos_que_a_retificacao_invalida`, `pendencias_para_enviar` e `_conferir_documentos`. Os da
inscrição enviada passam a ler a lista (R-006). Todos trocam `aplicaveis(requisitos, …)` por
`aplicaveis(conteudo, …)`.

## R-004 — A divergência da #161 vira predicado de domínio, com dois leitores

**Decisão.** A detecção que hoje mora em `_recorte_que_o_documento_publicado_alarga`
(`editais/domain/validation.py`) é extraída para `documentos.py` como predicado puro: dado um
documento "Todos os Perfis + Modalidade de um Perfil" e os Perfis, quais Perfis têm Modalidade de
mesma denominação. A validação de publicação continua emitindo o IMPEDE, agora com a terceira saída
na mensagem (`FR-708`). A aplicabilidade usa o mesmo predicado para marcar `divergente_do_publicado`
(`FR-727`).

**Por quê.** A Mesa precisa dizer *"exigido pelo Edital publicado"* exatamente quando a validação
diria *"o Edital publicado o exigiria de todo candidato em X"*. Dois códigos para a mesma pergunta
divergiriam no primeiro ajuste de rótulo, que é o defeito que a #161 fechou.

## R-005 — A lista gravada é uma tabela append-only nova, com duas camadas

**Decisão.** `inscricoes.ItemDaListaExigida`, uma linha por Documento Exigido da versão aceita, gravada
por `enviar_inscricao` na mesma transação em que `_gravar_o_ato` põe a inscrição em `SUBMETIDA` e
`_congelar` grava os fatos (`inscricoes/application/submissao.py`). Proteção:

1. **Privilégio.** Entrada em `TABELAS_APPEND_ONLY` (`seguranca/papeis.py`). O runtime perde `UPDATE`
   e `DELETE`. `provisionar_papeis` passa a dizer "34 de 34".
2. **Gatilho.** `BEFORE UPDATE OR DELETE` que recusa, no molde de
   `recursos/migrations/0002_ato_de_instrucao.py`. E um `BEFORE INSERT` de coerência que exige: a
   inscrição em `SUBMETIDA`, `versao` igual a `versao_aceita` da inscrição, e `gravada_em` igual a
   `submitted_at`.
3. **Modelo.** `save` recusa quando não está adicionando e `delete` recusa, com "append-only" na
   mensagem, que é o que `test_imutabilidade_do_historico` procura.

**Por que o `BEFORE INSERT`.** Ele põe no banco três requisitos que, de outro modo, seriam só
disciplina de aplicação:
- *a versão da lista é a que o envio registrou* (`FR-714`, o caso-limite do envio concorrente com a
  Retificação);
- *nada se grava para rascunho*;
- *o instante da lista é o do ato*.

**O que o gatilho não garante: o preenchimento retroativo (`D-004`).** Quem copiar `submitted_at` para
`gravada_em` passa pelas três conferências. A análise de consistência apontou isso, e as duas saídas
de banco foram pesadas e descartadas:
- *Exigir que a inscrição tenha sido alterada na mesma transação* (`xmin` da linha contra a transação
  corrente). `_gravar_o_ato` grava dentro de um `atomic()` aninhado, que é um *savepoint*: o `xmin`
  seria o da subtransação, e não o da transação de fora. A conferência recusaria o próprio envio.
- *Cortar pelo instante da migration* (recusar inscrição enviada antes dela). A semente e as fixtures
  põem `submitted_at` no passado de propósito (o `--dias-atras` do `seed_demo`), e seriam recusadas.

A garantia fica na aplicação, e é dita assim: só `enviar_inscricao` e a semente chamam a gravação,
nenhuma migration a chama, e um teste prende as duas coisas. É menos que as duas camadas das
demais regras desta tabela, e o plano o diz em vez de fingir o contrário.

**Por que duas camadas, se o precedente tem uma.** `ValorDeFato`, os fatos congelados no mesmo ato,
é protegido só pelo privilégio. Não tem gatilho nem guarda de modelo. O CLAUDE.md descreve as
tabelas append-only com **duas camadas independentes**. A lista exigida é o que a
Constituição chama de *reproduzir os documentos exigidos*, e a reprodução não pode depender de uma
camada só. A falta da segunda camada em `ValorDeFato` é registro para a fila, não escopo daqui.

**Idempotência (`FR-716`).** Nada de novo: o reenvio com a mesma chave devolve a inscrição já
enviada antes de chegar à gravação (`submissao.py`, o `reserve`). A unicidade `(inscricao,
requisito_id)` é a segunda barreira.

**Descartado.**
- *Um JSON na própria `Inscricao`.* `inscricoes_inscricao` é mutável por decisão (o docstring de
  `save` diz que a tabela fica fora da lista append-only). A lista herdaria a mutabilidade.
- *Gravar só os aplicáveis.* Recusado em `D-003`.
- *Gravar o nome e a instrução do documento.* A versão aceita é imutável e está referida na linha.
  Ler o nome dela não é recalcular recorte nenhum. Copiar o texto seria uma segunda fonte para o
  mesmo valor (Princípio II).

## R-006 — Quem lê a lista, e quem continua recalculando

**Decisão.** Uma função de aplicação, `lista_exigida(inscricao, conteudo)`, em
`inscricoes/application/lista_exigida.py`, devolve os itens e um sinal `reconstruida`. Com linhas
gravadas, lê as linhas. Sem elas, reconstrói com `aplicabilidade` sobre a versão aceita (`FR-726`).
Leem por ela os leitores de inscrição **enviada**:

| Leitor | Onde | Hoje |
|---|---|---|
| Mesa | `avaliacoes/application/mesa.py`, `inscricao_para_avaliar` | `requisitos_da_inscricao` sobre `versao_aceita` |
| Consulta, lista | `inscricoes/application/consulta.py`, `_linhas` (seção "recebidas") | idem, por linha |
| Consulta, detalhe | `consulta.py`, `inscricao_para_consulta`, quando `SUBMETIDA` | idem |
| Portal, inscrição enviada | `portal/views.py`, `_documentos` chamado de `_conferencia`, `_dados_do_comprovante` e `comprovante` | idem |

Continuam recalculando sobre a versão **vigente**, porque são de rascunho: a seção "em
preenchimento" da consulta, a tela de inscrição, a Revisão, os descartes e o envio até o instante do
ato.

**O comprovante não muda (`FR-720`).** Ele lista só os documentos enviados, e o código de
verificação é calculado sobre `DocumentoSubmetido`, fora do recorte. Trocar a fonte das linhas não
muda o que ele imprime.

**Do que a lista protege, dito com precisão.** Os quatro leitores já leem a `versao_aceita`, que é
imutável: uma Retificação posterior **não** muda o que eles mostram, com ou sem lista. O que a lista
protege é a mudança da **regra** no código, como a que esta própria feature faz em `aplicaveis`. Foi
esse o motivo da decisão de 25/09 (D4): *"Sem ela, qualquer mudança de recorte de D1 muda
retroativamente a leitura das inscrições antigas."* Por isso o teste que prova a lista grava uma
linha diferente do que a regra de hoje calcularia, e confere que a Mesa mostra a linha. Um teste que
só retifica e compara passaria sem a feature.

**Orçamento de consultas.** A lista "Inscrições recebidas" tem um teste que exige o **mesmo** número
de consultas com 5 e com 300 inscrições (`tests/integration/interface/test_inscricoes_em_escala.py`).
A página lê os itens das 25 inscrições dela numa consulta só, `filter(inscricao__in=…)`, e agrupa em
Python. As inscrições sem lista reconstroem sobre o conteúdo que a página já carrega. Nenhuma
consulta por linha.

## R-007 — As recusas: o que é da gravação e o que é da publicação

**Decisão.**

| Regra | Na gravação do rascunho | Na publicação e na Retificação | Código do achado |
|---|---|---|---|
| `modalityCode` com `profileId` ou `modalityId` (`FR-702`) | recusa, `campo="modalityCode"` | IMPEDE | `document_requirement_scope_conflict` |
| código que nenhum Perfil tem (`FR-703`, `FR-724`) | recusa, em qualquer etapa (`D-010`) | IMPEDE | `document_requirement_modality_code_unknown` |
| código declarado ampla em algum Perfil (`FR-704`) | recusa, em qualquer etapa (`D-010`) | IMPEDE | `document_requirement_modality_code_general` |
| denominações diferentes para o código (`FR-706`) | — | IMPEDE, **um por código** | `modality_code_name_divergent` |
| "Todos os Perfis" + Modalidade de um Perfil (`FR-708`) | — (como hoje) | IMPEDE, mensagem com 3 saídas | `document_requirement_modality_scope_ambiguous` |

**Por que a coerência de denominação não é da gravação.** Ela se quebra na etapa **Perfis**, ao
renomear, e não na de Documentos. Recusar a gravação dos Perfis por causa de um documento seria
travar uma etapa por outra. A Revisão é o lugar em que as duas se encontram, e o IMPEDE é o que a
Constituição pede para divergência entre o que se configura e o que se publica.

**Um IMPEDE por código (`SC-266`).** Com 16 Perfis e um renomeado, o achado é um, e nomeia as duas
denominações com os Perfis de cada uma. Um achado por Perfil divergente daria 1 aqui, mas 8 num
empate de 8 a 8, e o operador leria oito problemas onde há um.

**Destino na Revisão.** `DESTINO_POR_CODIGO` (`interface/views.py`) manda
`modality_code_name_divergent` para a etapa **Perfis**, que é onde se corrige. Os demais vão para
Documentos, como os irmãos já vão.

**A comparação (`D-005`).** `strip()` nas pontas, e mais nada.

## R-008 — O documento publicado e a Revisão agrupam por código

**Decisão.** Em `publicacoes/infrastructure/pdf.py`, a chave do grupo em `_documentos_exigidos` passa
de `(profileId, modalityId)` para `(profileId, modalityId, modalityCode)`. `_titulo_do_grupo`, com
código, escreve *"Dos candidatos concorrentes na modalidade {denominação}:"*. A denominação é a de
qualquer Perfil que tem o código: a coerência de `R-007` garante que é uma só. O mesmo vale para
`_alcance` em `interface/revisao.py`, que descreve o que vai ser congelado.

**Por quê.** É o título que o PDF já imprime hoje para "Todos os Perfis + Modalidade". A diferença é
que agora ele é **verdadeiro**, porque o portal aplica pelo mesmo critério (`SC-262`).

## R-009 — A composição oferece o código no mesmo seletor da modalidade

**Decisão.** No passo de inscrição da composição (`interface/templates/interface/_documento.html`),
o seletor "Exigido apenas da modalidade" ganha dois `<optgroup>`:

- **Em todos os Perfis**, antes: uma opção por código presente no Edital, fora os declarados ampla em
  algum Perfil. O rótulo é o de `UX-080`: *"Pessoas com Deficiência (PcD) — em todos os Perfis que a
  têm (16 de 16)"*. O valor é `codigo:<código>`.
- **Modalidade de um Perfil**, depois: os pares Perfil × Modalidade de hoje, com o valor UUID de
  hoje. O rótulo não diz "Num Perfil só" porque, com o Perfil em "Todos", o par produz a forma que a
  #161 recusa, e o rótulo não pode prometer o contrário.

`alcance_da_aplicabilidade` (`interface/forms.py`) passa a devolver também os códigos. `ler_inscricao`
separa pelo prefixo: `codigo:` vai para `modalityCode`, UUID vai para `modalityId`.
`documentos_do_edital` e `documentos_persistidos` passam o campo nos dois sentidos.

**Por quê.** Um seletor só torna a exclusividade entre código e Modalidade exata natural: não há como
escolher os dois. O seletor de Perfil continua independente, como hoje, e a combinação "Perfil +
código" é recusada no servidor, com a mensagem ancorada no campo (o mecanismo de `_recusa`,
`views.py`).

**Descartado.** *Um terceiro seletor, só de código.* Três controles independentes para uma escolha
de cinco formas, e a tela teria de explicar que dois deles não se combinam.

**As opções vêm do banco**, como hoje: `edital.perfis` e `perfil.modalidades`, com
`PerfilVaga.modalidade_ampla_concorrencia` para excluir a ampla.

## R-010 — A Retificação oferece o código como campo próprio

**Decisão.** `CAMPOS_DOCUMENTO` (`interface/retificacao.py`) ganha `("modalityCode", "Modalidade em
todos os Perfis", REFERENCIA)`. `opcoes_de_aplicabilidade` passa a devolver os códigos do conteúdo
publicado, fora os declarados ampla, com o rótulo de `UX-080`. Trocar de exato para transversal são
duas alterações no mesmo ato: `modalityId → null` e `modalityCode → "PcD"`. A exclusividade é
conferida sobre o conteúdo resultante (`R-007`).

**Por quê um campo, e não o mesmo seletor da composição.** A Retificação é uma lista de campos, e
cada campo vira uma alteração com caminho próprio (`/documentRequirements/id=…/modalityCode`). Fundir
dois campos num seletor exigiria uma alteração que escreve dois caminhos, o que a gramática de
alterações não tem.

**A guarda de contrato.** `tests/interface/test_campos_vem_do_contrato.py` exige que todo campo
retificável seja oferecido na tela. Com `modalityCode` declarado retificável em
`editais/domain/mutabilidade.py`, esquecer a tela derruba a suíte, e é assim que tem de ser.

**Não entra.** Acrescentar e remover documento (`D-009`).

## R-011 — Mutabilidade e resumo público

**Decisão.**
- `CONTRATO[("documentRequirements", "modalityCode")] = retificavel()`, com comentário que dá a razão
  de `D-002`.
- `CAMPOS["documentRequirements"]["modalityCode"] = "Modalidade em todos os Perfis"` em
  `publicacoes/domain/alteracoes.py`. É a linha que `FR-721` exige, no formato do módulo: *onde* e
  *qual campo*, sem valor (`D-008`).
- `profileId` e `modalityId` continuam fora de `CAMPOS`. A correção deles está na fila das diretas.

**A matriz da `026`** (`specs/026-contrato-de-mutabilidade-normativa/matriz.md`) lista os 9 campos
de `documentRequirements`. É artefato de outra feature, e não é reescrita aqui. A fonte autoritativa
é `CONTRATO`, e a decisão fica registrada neste plano e no `data-model.md`.

## R-012 — A API de rascunho, o reuso, a semente

- **API.** `DocumentRequirementSerializer` (`editais/api/serializers.py`) ganha `modalityCode =
  CharField(required=False, allow_null=True, max_length=100)`. `specs/001-…/contracts/openapi.yaml`
  ganha `modalityCode` em `DocumentoExigidoPublicado`, **dentro** de `required`.
  `tests/contract/test_forma_publicada.py` exige que no conteúdo publicado não haja campo opcional
  (*"obrigatório aqui significa presente, e não preenchido"*), e o degrau 9 pôs `attachmentId` ali
  pelo mesmo caminho.
- **Reuso.** `remapear` já copia os campos que não são identidade (`**documento`), e o código não é
  identidade. Atravessa sem mudança. O teste do reuso ganha a asserção de que ele atravessa.
- **Semente.** `seed_demo` põe inscrições em `SUBMETIDA` escrevendo `versao_aceita` direto. Ele
  passa a chamar a mesma gravação da lista, com `gravada_em = submitted_at`, que é o que o gatilho
  de `R-005` exige. Sem isso, a demonstração mostraria só listas reconstruídas.

## R-013 — As guardas que a suíte já tem, e que esta feature precisa mover

| Guarda | O que muda |
|---|---|
| `tests/migrations/test_migrations.py`, guardião da `022` | `"inscricoes": 4 → 5` e `"editais": 21 → 22`, cada um com a justificativa ao lado |
| o mesmo arquivo, guardião da `017` | `"editais": 21 → 22`, com justificativa |
| `APPS` e `TRIGGERS_POR_APP` no mesmo arquivo | `inscricoes` entra, com os dois gatilhos |
| `tests/integration/test_database_permissions.py` | nada: é parametrizado sobre `TABELAS_APPEND_ONLY` |
| `tests/integration/test_imutabilidade_do_historico.py` | nada: a guarda de modelo põe a tabela no conjunto conferido |
| `tests/integration/requerimentos/test_nao_escreve_fora.py` | acrescentar `ItemDaListaExigida` às tabelas que o requerimento não escreve |
| `tests/contract/test_elevacao_degrau_*.py` | um `test_elevacao_degrau_17.py` novo |
| `AGENTS.md` (o `CLAUDE.md`) | "eram 18, são **33**" passa a **34** |

## R-014 — O que fica fora, e onde está registrado

- **`ValorDeFato` sem gatilho** (R-005). É registro para a fila.
- **Filtro de concorrência** da consulta administrativa (spec, Riscos e lacunas). Corrigido à parte,
  fora desta feature: `doc/achado-filtro-de-concorrencia-sem-perfil.md`.
- **O "O que mudou" do recorte exato**, e a **instrução na Mesa / o facultativo na Revisão**: fila
  das diretas. A segunda já está no PR #167 (`claude/instrucao-e-facultativo`), que mexe em
  `mesa.py` e `mesa_inscricao.html`. Quem for mergeado depois resolve o conflito preservando a
  instrução, que esta feature não remove.
