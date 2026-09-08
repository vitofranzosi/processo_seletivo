# Fase 0 — Pesquisa: Anexos do Edital

O que foi verificado no repositório antes de decidir, e o que foi descartado. Cada decisão cita o
código que a sustenta; nenhuma delas reabre as doze da §2 da spec.

---

## R-001 · Onde os bytes moram

**Decisão**: `BinaryField` na mesma base, como `DocumentoPublicado`.

**Racional**: a publicação é atômica (D-010), e o `publish_edital` inteiro roda dentro de
`command_context()` — uma `transaction.atomic()` com o Edital travado por `select_for_update`
(`publicacoes/application/publish_edital.py:478-487`, `shared/application/commands.py:7-10`). Com os
bytes no banco, o congelamento entra na mesma transação e um `rollback` leva tudo embora. Com
arquivo em disco, seria preciso repetir a coreografia da `009` — escrever antes, apagar no `except`,
remover o anterior só depois do commit (`inscricoes/application/rascunho.py:379-434`) — e um
`rollback` deixaria conteúdo publicado apontando para bytes que não existem, que é justamente o
defeito que a feature veio corrigir.

O critério é do próprio projeto. A docstring que recusou `BinaryField` para o arquivo do candidato
deu a razão da recusa, e ela não se aplica aqui: *"lá é um documento por publicação, imutável e
pequeno; aqui são até dez megabytes por requisito, por candidato, substituíveis durante o rascunho e
lidos em streaming"* (`inscricoes/storage.py:1-6`). O anexo é o primeiro caso, não o segundo.

**Alternativas consideradas**:
- *Armazenamento de arquivo público, espelhando o `ArmazenamentoPrivado`*: exigiria uma segunda raiz
  configurável, política de backup própria e a coreografia disco↔banco na publicação. Custo alto
  para um formulário de trezentos kilobytes.
- *Reusar a linha de `DocumentoPublicado`*: impossível sem alterá-la — `publicacao` é `OneToOne`
  (`publicacoes/models.py:88-90`), um documento por publicação. Herdamos as **garantias**, não a
  tabela.

---

## R-002 · Como o artefato fica imutável sem impedir a troca no rascunho

**Decisão**: uma tabela, uma coluna `congelado_em`, e uma **trigger condicional** que recusa `UPDATE`
e `DELETE` quando `OLD.congelado_em IS NOT NULL`.

**Racional**: é literalmente o desenho que a `0007` já escreveu para `Retificacao` e
`AlteracaoNormativa`, com a justificativa aplicável palavra por palavra — *"mudam legitimamente
enquanto o ato está em curso… o que precisa ser imutável é o que já produziu efeito, então a trigger
é condicional ao estado final"* (`publicacoes/migrations/0007_imutabilidade_do_historico.py:12-18`).
FR-010a é o "em curso"; FR-010 é o "já produziu efeito".

A mesma coluna responde a segunda pergunta de graça: **artefato congelado é artefato público**
(FR-017). A rota pública filtra por `congelado_em__isnull=False`, e não precisa consultar versão
nenhuma para saber se pode entregar.

**Alternativas consideradas**:
- *Duas tabelas, rascunho e publicado, com cópia na publicação*: dobra o modelo e obriga a decidir
  o que fazer quando a mesma versão referencia o artefato duas vezes. A trigger condicional entrega
  o mesmo com uma tabela.
- *Entrar em `TABELAS_APPEND_ONLY`* (`seguranca/papeis.py:26`): tiraria `UPDATE`/`DELETE` do papel de
  runtime e quebraria a troca no rascunho. `Retificacao` está fora da lista pela mesma razão.

---

## R-003 · Qual é o endereço público do anexo

**Decisão**: `GET /api/v1/public/anexos/<artefato_id>` — o endereço é o do **artefato**, não o do par
(publicação, anexo). A lista de qual artefato pertence a qual versão vem do conteúdo canônico.

**Racional**: satisfaz D-011 por construção — o artefato é imutável, então o endereço nunca "resolve
o vigente". Permite `Cache-Control: public, max-age=31536000, immutable`, o mesmo `IMMUTABLE_CACHE`
que as rotas de publicação e versão já usam (`publicacoes/api/public_views.py:18`). E evita um
detalhe hoje ambíguo: `_materialize_affected_versions` grava `source_publication=publication` em
**toda** fronteira rematerializada, inclusive nas futuras que pertencem a outros atos
(`publicacoes/application/retificacoes.py:579`) — um endereço por publicação herdaria essa ambiguidade.

**Alternativas consideradas**:
- `/publicacoes/<id>/anexos/<anexo_id>`: legível, e é como o portal já chega ao PDF
  (`portal/views.py:110`, `selecao.html:16`). Recusada pela ambiguidade acima e por exigir uma
  consulta ao conteúdo só para decidir se pode entregar.
- `/versoes/<versao_id>/anexos/<anexo_id>`: correto, e mais verboso; a resolução por versão continua
  disponível porque a **lista** vem do conteúdo daquela versão. Nada impede acrescentá-la depois se
  aparecer necessidade.

**Consequência registrada**: a rota nova honra `If-None-Match` e envia `Cache-Control`. A
`PublishedDocumentView` não faz nem uma coisa nem outra (`publicacoes/api/views.py:120-133`), sozinha
entre as rotas públicas. Não replicamos a assimetria, e não a corrigimos aqui.

---

## R-004 · O degrau 9, e por que ele é legítimo

**Decisão**: `SCHEMA_VERSION` 8 → 9 (`shared/canonical.py:77`), com dois degraus:
`attachments: []` na raiz e `attachmentId: null` em cada item de `documentRequirements`.

**Racional**: sem degrau, todo Edital publicado hoje passa a ser recusado por
`canonical_schema_version_mismatch` na Retificação (`retificacoes.py:534-551`) — a feature quebraria
o acervo. O critério declarado para converter é *"a ausência tem significado declarado e
verdadeiro"* (`publicacoes/domain/elevacao.py:8-14`), e as duas frases são verdadeiras sobre todo
Edital existente: nenhum declarou anexo, e nenhum requisito tem modelo. O precedente de forma é o
degrau 7, que introduziu `classificationMilestones: []` por `DEGRAUS_DE_PERFIL`.

`DEGRAUS_DA_RAIZ` já existe (`elevacao.py:61`). O nível do `documentRequirement` **não** existe e
exige uma tabela nova mais um laço em `elevar()`, no molde do que os degraus 7 e 8 fizeram — a
docstring recusa mecanismo genérico de compatibilidade por versão de propósito (`elevacao.py:91-101`).

**Alternativas consideradas**:
- *Não elevar, deixando o conteúdo antigo irretificável*, como o degrau 3→4 fez ao introduzir
  `documentRequirements`: recusada porque lá a coleção nova mudava o que o Edital exigia — converter
  inventaria norma. Aqui a lista vazia não inventa nada.
- *Omitir a chave quando não há anexo*: contraria a regra do snapshot, em que ausência é `null` e
  nunca chave omitida (`publish_edital.py:48-51,175-178`).

---

## R-005 · O que habilita as cinco operações de Retificação

**Decisão**: declarar `/attachments` em `COLECOES_COM_CHAVE` (`publicacoes/domain/colecoes.py:18-41`)
e nada mais no domínio.

**Racional**: não existe catálogo de caminhos retificáveis. A gramática de `changes.py` é permissiva
por resolução, com denylists declaradas, e `ADD`/`REPLACE`/`REMOVE` já servem as cinco operações da
D-008. O que a declaração compra é o essencial: sem ela, o seletor `id=<uuid>` seria recusado e só
restaria o endereçamento por posição, que `_posicao` proíbe (`changes.py:152-156`) — coleção
inendereçável é coleção irretificável. As quatro regras de identidade são verificadas **sobre o
resultado** e passam a valer automaticamente.

O trabalho real está na tela: `interface/retificacao.py` é uma enumeração explícita de campos
oferecidos, e Documento Exigido é hoje `removivel=False`, sem forma de acréscimo. Anexo precisa de
`CAMPOS_ANEXO`, `NOVO_ANEXO`, `_anexo_completo` e `removivel=True`, mais o bloco correspondente em
`diferencas`.

**Ponto que não tem precedente**: substituir o artefato **não é edição de campo tipado** — é upload
dentro do ato de Retificação. O artefato entra antes, com `congelado_em` nulo, e a `AlteracaoNormativa`
referencia `artifactId` e `artifactHash` no `newValue`, que é `JSONField` (FR-035). Congelar acontece
em `publish_retification`, ao lado da criação da `Publicacao` e do `DocumentoPublicado`
(`retificacoes.py:642-658`). Retificação cancelada deixa o artefato descongelado, e descongelado é
apagável.

---

## R-006 · Por que os Anexos ficam fora do `replace_draft`

**Decisão**: comandos próprios em `editais/application/anexos.py`, com `compare_and_swap` na revisão
do Edital, como o `replace_draft` faz.

**Racional**: `replace_draft` apaga e recria cada coleção inteira
(`editais/application/draft.py:359-375`), e a interface só não perde dados porque monta as cinco
coleções a cada gravação de etapa (`interface/views.py:922-928`). Uma coleção que carrega bytes não
sobrevive a esse contrato: ou o formulário reenviaria os artefatos a cada `Salvar`, ou uma etapa
gravada apagaria os anexos. Ficando de fora, `replace_draft` não os enxerga e não os toca.

O precedente é da `009`: `anexar_documento` grava na hora e sem `Salvar`, com validação e auditoria
próprias (`inscricoes/application/rascunho.py:379`). Aqui é o mesmo desenho, do lado de quem elabora.

**O que fica de fora é a coleção, e não o vínculo.** `attachmentId` é campo do `DocumentoExigido`, e
essas linhas continuam sendo apagadas e recriadas pelo `replace_draft`. O campo tem de viajar no
`bulk_create` e no formulário, como `profileId` e `modalityId` já viajam; esquecê-lo zera o vínculo a
cada gravação de etapa, sem erro nenhum.

**Alternativa considerada**: incluir `attachments` na montagem de `_gravar_etapa` — recusada em
`plan.md` §Complexity Tracking, com a razão de que a exceção continuaria existindo, só que escondida.

---

## R-007 · Validação de PDF: mover, não reescrever

**Decisão**: mover `aceitar()` e `resumo()` de `inscricoes/domain/arquivos.py` para
`shared/arquivos.py`, com `inscricoes` reimportando de lá.

**Racional**: as duas regras são exatamente as que o anexo precisa — é PDF pela assinatura, não pela
extensão, e cabe no limite —, e a mensagem de recusa já reconhece as assinaturas de imagem que um
celular produz (`inscricoes/domain/arquivos.py:20-30,50`). Copiar criaria duas fontes da mesma regra;
importar de `inscricoes` faria conteúdo público depender do app do candidato. `shared/` é onde
`canonical`, `tempo` e `concurrency` já moram.

**Consequência**: o limite é lido do `settings` por chamada, e o do anexo é **outro** — a `009` não
negocia o dela (FR-046) e esta feature não negocia a sua (FR-013). Duas constantes, uma função.

---

## R-008 · Onde o anexo aparece no PDF do Edital

**Decisão**: uma `Secao` de tipo `GERADA` com `source="attachments"` no catálogo
(`editais/domain/secoes.py:49-160`), corpo no molde de `_documentos_exigidos`
(`publicacoes/infrastructure/pdf.py:1615`), registrada em `_CORPO_GERADO` (`pdf.py:1654-1660`).
Lista rótulo e ordem; **não imprime endereço** (FR-027a).

**Racional**: é a mecânica que o Cronograma e os Documentos Exigidos já usam, e mantém o
determinismo, que é invariante testada byte a byte contra fixture
(`tests/contract/test_documento_publicado.py`). A fixture precisa ser regenerada pelo script que já
existe — `backend/scripts/gerar_fixture_documento.py` —, e isso vale para o degrau 9 mesmo que a
seção não existisse.

**Armadilha registrada**: origem gerada que não esteja em `_CORPO_GERADO` é **silenciosamente
omitida** do PDF (`pdf.py:1672-1674`), sem falha de suíte. A fase F4 traz um teste que prova que a
seção de anexos aparece no documento; o guarda genérico é outra tarefa.
