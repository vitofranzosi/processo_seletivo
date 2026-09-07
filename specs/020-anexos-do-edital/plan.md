# Implementation Plan: Anexos do Edital

**Branch**: `claude/edital-anexos-spec-f9bdf2` | **Date**: 2026-09-07 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/020-anexos-do-edital/spec.md`

## Summary

O Edital passa a carregar o documento que ele próprio exige. A coleção `attachments` entra no
conteúdo canônico ao lado de `documentRequirements`, cada anexo referencia um artefato imutável, e
tudo o mais — vigência, Retificação, versão consolidada, consulta temporal — é o que já existe.

**A novidade conceitual é uma só, e ela é pequena: o conteúdo publicado passa a referenciar bytes
que não são o PDF do próprio Edital.** Todo o resto é uma coleção nova como as oito que já existem.

Quatro verificações que sustentam esse tamanho:

1. **A gramática de Retificação é genérica.** `changes.py` aceita `ADD`, `REPLACE` e `REMOVE` sobre
   qualquer coleção **declarada** em `COLECOES_COM_CHAVE`; não há allowlist de caminhos. Declarar
   `/attachments` ali é o que habilita as cinco operações da D-008 — e sem declarar, o seletor `id=`
   seria recusado e a coleção nasceria irretificável (`publicacoes/domain/colecoes.py:18-41`).
2. **A imutabilidade condicional tem precedente exato.** `Retificacao` e `AlteracaoNormativa` mudam
   enquanto o ato corre e congelam no estado final, por trigger condicional
   (`publicacoes/migrations/0007_imutabilidade_do_historico.py:20-58`). É a mesma forma do artefato:
   sobrescrevível no rascunho (FR-010a), imutável depois que uma versão o publicou (FR-010). **Uma
   tabela, uma trigger, nenhuma máquina de estados nova.**
3. **A validação de PDF já está escrita.** `aceitar()` e `resumo()` conferem assinatura `%PDF-`, não
   extensão, e explicam a recusa (`inscricoes/domain/arquivos.py:50,90`). Mudam de casa para
   `shared/`; não são reescritas.
4. **Nenhuma capacidade nova.** `edital:elaborar`, `retificacao:elaborar`, `retificacao:submeter` e
   `edital:publicar` já cobrem todos os atos desta feature (`interface/identidade.py:20-29`).

**A decisão que mais determina o desenho** é onde os bytes moram: `BinaryField` no mesmo banco, como
`DocumentoPublicado`. Não é preferência — é o que torna a **publicação atômica (D-010) verdadeira de
graça**. Com arquivo em disco, publicar exigiria a dança escrita-antes-do-commit e limpeza no
`except` que a `009` teve de fazer (`inscricoes/application/rascunho.py:379-434`), e um `rollback`
deixaria conteúdo publicado apontando para bytes que não existem. O critério é do próprio projeto: a
docstring que recusou `BinaryField` para o arquivo do candidato deu a razão — *"lá é um documento
por publicação, imutável e pequeno"* —, e o anexo é exatamente isso.

**A decisão que mais economiza** é o endereço público ser o do **artefato**, e não o do par
(publicação, anexo). O artefato é imutável e único: `GET /api/v1/public/anexos/<artefato_id>` já
resolve "o de então" por construção, sem consultar versão nenhuma, e é `immutable` para cache. O
endereço por publicação teria de escolher entre `Publicacao` e `VersaoConsolidada` e conviver com um
detalhe hoje ambíguo — `_materialize_affected_versions` grava `source_publication` da retificação
que rematerializou, inclusive em fronteiras futuras de outros atos (`retificacoes.py:579`).

**A que mais exigiu cuidado** é o rascunho. `replace_draft` **apaga toda coleção que não for
reenviada** (`editais/application/draft.py:359-375`), e a interface só se safa porque monta as cinco
coleções a cada gravação de etapa (`interface/views.py:922-928`). Bytes não fazem essa viagem de ida
e volta num POST de formulário. Por isso os Anexos ficam **fora** do `replace_draft`, com comandos
próprios e estreitos — é a exceção que a §Complexity Tracking justifica, e é o precedente do
`anexar_documento` da `009`, que também grava na hora e sem `Salvar`.

**A coleção fica de fora; o vínculo, não.** O `attachmentId` é campo do `DocumentoExigido`, e essas
linhas o `replace_draft` apaga e recria a cada gravação (`draft.py:359-375`). O campo novo tem de
entrar no `bulk_create`, senão salvar qualquer etapa do assistente zera o vínculo **em silêncio** —
o mesmo modo de falha, entrando pela porta que a exceção não cobre.

**O que não aparece no diagrama e custa mais que tudo** é o degrau 9. `attachments` na raiz e
`attachmentId` em cada `documentRequirement` são conteúdo canônico novo, e `SCHEMA_VERSION` sobe de
8 para 9 (`shared/canonical.py:77`). Sem o degrau, todo Edital já publicado vira **irretificável**
(`retificacoes.py:534-551`). O degrau é legítimo pelo critério declarado — *converter só quando a
ausência tem significado declarado e verdadeiro* (`publicacoes/domain/elevacao.py:8-14`): lista
vazia diz "este Edital não declarou anexo", e `attachmentId: null` diz "este requisito não tem
modelo". As duas frases são verdadeiras sobre todo Edital existente.

**E o que a feature não faz**, para que o `/plan` não seja lido como licença: não lê PDF, não
compara o que voltou com o modelo, não gera documento preenchido, não rastreia download, não expõe
verificação de integridade e não acrescenta máquina de avaliação nenhuma.

## Technical Context

**Language/Version**: Python 3.13 (`backend/pyproject.toml`)

**Primary Dependencies**: Django 5.2, DRF 3.16. **Nenhuma dependência nova.** Uma rota de API pública
nova (`/api/v1/public/anexos/<uuid>`), que é contrato e entra no `openapi.yaml`.

**Storage**: PostgreSQL. **Duas migrations**, e a ordem entre elas importa:

```text
editais/0012_anexo_do_edital ──▶ editais/0013_congelamento_do_artefato
   tabelas AnexoEdital e            trigger condicional em
   ArtefatoAnexo, FK anexo          editais_artefatoanexo
   em DocumentoExigido
```

Mais a política de papéis: `ArtefatoAnexo` **não** entra em `TABELAS_APPEND_ONLY`
(`seguranca/papeis.py:26-66`) — ela muda legitimamente enquanto o ato corre, exatamente como
`Retificacao`. Quem garante a imutabilidade do que já foi publicado é a trigger.

**Testing**: pytest + pytest-django. Suítes tocadas: `unit/`, `contract/`, `integration/`,
`interface/`, `portal/`, `acceptance/`, `authorization/`, `migrations/`.

**Target Platform**: servidor Linux; dois canais HTML (`/gestao/` administrativo, portal público) e
a API pública.

**Project Type**: aplicação web Django monolítica, por app de domínio.

**Performance Goals**: o artefato é servido do banco em resposta única, como o PDF do Edital já é.
Diferença deliberada: a rota nova honra `If-None-Match` e envia `Cache-Control: immutable`, que a
`PublishedDocumentView` hoje **não** faz (`publicacoes/api/views.py:120-133`) — ver §Achados.

**Constraints**: limite de tamanho do artefato é da aplicação (FR-013), em `settings`, no molde de
`ARQUIVOS_CANDIDATOS_LIMITE_BYTES`. Sugestão: 5 MB — os formulários da amostra têm centenas de
kilobytes, e o limite existe para proteger o banco, não para negociar com o Edital.

**Scale/Scope**: de dois a doze anexos por Edital na amostra dos sete Editais lidos; uma dúzia de
artefatos por versão, poucas versões por Edital.

## Constitution Check

*GATE: aprovado antes da Fase 0 e reavaliado depois da Fase 1.*

| Princípio | Como esta feature o atende |
|---|---|
| **I — Linguagem ubíqua** | "Anexo do Edital" é conceito distinto de Seção (D-003) e de Documento Submetido (regime, D-007). Identidade estável em UUID; o identificador público do artefato dá acesso a **conteúdo público**, e a rota recusa artefato não congelado (FR-017) — identificador não confere autorização a nada que já não fosse público. |
| **II — Integridade normativa** | Fonte única: a coleção no conteúdo canônico. Publicação imutável e append-only por trigger. Estado vigente em qualquer instante reproduzível pela versão consolidada, que já carrega o hash e o id do artefato. |
| **III — Segurança e auditoria** | Nega por padrão: artefato só é público depois de congelado. `edital:elaborar` e `retificacao:*` verificadas no comando, não na view. Auditoria com `record_event` em envio, vínculo, desvínculo e substituição. LGPD: o anexo é formulário institucional em branco — não carrega dado pessoal, e é essa a razão de ele poder ser público. |
| **IV — Regras explícitas** | Toda regra no domínio: `colecoes.py` declara a topologia, `validation.py` recusa referência pendurada, `changes.py` recusa endereçamento posicional. Publicação continua sendo operação explícita e atômica. Concorrência: `expected_previous_hash` herdado, sem controle novo. |
| **V — Simplicidade** | Nenhum mecanismo novo: trigger condicional (precedente 0007), coleção declarada (precedente das oito), degrau de elevação (precedente 7 e 8), validação de PDF movida e não reescrita. A única exceção ao padrão está na §Complexity Tracking. |
| **VI — Jornada demonstrável** | Três canais, três atores: o autor sobe e publica pela interface administrativa; o público baixa pela página da seleção; o candidato baixa do lado do requisito, no portal. Nada aqui se demonstra por shell. |

**Resultado: aprovado**, com uma exceção declarada abaixo.

## Project Structure

### Documentation (this feature)

```text
specs/020-anexos-do-edital/
├── plan.md              # este arquivo
├── research.md          # Fase 0 — as decisões técnicas e o que foi descartado
├── data-model.md        # Fase 1 — entidades, campos, forma canônica
├── quickstart.md        # Fase 1 — como verificar os sete passos
├── contracts/
│   └── anexos.yaml      # Fase 1 — rota pública e esquema da coleção publicada
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 — NÃO criado por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/
│   ├── models/anexos.py                  # NOVO — AnexoEdital, ArtefatoAnexo
│   ├── models/documentos.py              # + anexo (FK anulável, PROTECT ou SET_NULL)
│   ├── models/__init__.py                # + exports
│   ├── migrations/0012_anexo_do_edital.py        # NOVO
│   ├── migrations/0013_congelamento_do_artefato.py # NOVO — trigger condicional
│   ├── application/anexos.py             # NOVO — anexar, rotular, reordenar, remover
│   ├── application/draft.py              # + o campo `anexo` no bulk_create do DocumentoExigido
│   └── domain/secoes.py                  # + Secao GERADA source="attachments"
├── publicacoes/
│   ├── application/publish_edital.py     # + _attachments no snapshot; congelar no publish
│   ├── application/retificacoes.py       # + congelar artefato citado ao publicar a Retificação
│   ├── domain/colecoes.py                # + "/attachments" em COLECOES_COM_CHAVE
│   ├── domain/elevacao.py                # + degrau 9 (raiz e documentRequirement)
│   ├── infrastructure/pdf.py             # + _anexos e entrada em _CORPO_GERADO
│   ├── api/public_urls.py                # + rota do artefato
│   └── api/public_views.py               # + ArtefatoPublicoView (ETag + immutable)
├── editais/domain/validation.py          # + ANEXO_PUBLICADO, + referência pendurada
├── interface/
│   ├── urls.py, views.py                 # + etapa "anexos", upload, download do rascunho
│   ├── revisao.py                        # + attachments (e documentRequirements — ver §Achados)
│   ├── retificacao.py                    # + CAMPOS_ANEXO, NOVO_ANEXO, removivel=True
│   └── templates/interface/              # + compor_anexos.html, _anexo.html
├── portal/
│   ├── views.py                          # + anexos na selecao; modelo ao lado do requisito
│   └── templates/portal/                 # selecao.html, _documentos.html
└── shared/arquivos.py                    # MOVIDO de inscricoes/domain/arquivos.py

backend/tests/
├── unit/            publicacoes/test_colecoes.py, test_elevacao_*, editais/test_anexos.py
├── contract/        test_forma_publicada.py, test_documento_publicado.py (fixture regenerada)
├── interface/       elaboração, upload, retificação de anexo, acessibilidade
├── portal/          fronteira pública, modelo ao lado do requisito
├── authorization/   artefato não congelado, escopo institucional
└── acceptance/      test_us_anexos.py — os sete passos do 173/2025
```

**Structure Decision**: os modelos vivem em `editais` porque o Anexo é conteúdo do Edital em
elaboração, ao lado de `DocumentoExigido` e `SecaoEdital`; a publicação, o congelamento e a entrega
pública vivem em `publicacoes`, que é quem já sabe congelar e servir. Nenhum app novo.

## Fases de implementação sugeridas

Cada fase é entregável e verificável sozinha; a ordem é de dependência, não de valor.

**F1 · A coleção existe no conteúdo (sem tela).** `COLECOES_COM_CHAVE`, `ANEXO_PUBLICADO` na
validação, degrau 9 em `elevacao.py`, `attachmentId` no `documentRequirement`, `openapi.yaml`,
`ESQUEMA_DA_COLECAO` e as fixtures de snapshot. É a fase que mais quebra teste existente, e é
melhor que quebre sozinha.

**F2 · Os modelos e o congelamento.** `AnexoEdital`, `ArtefatoAnexo`, FK no `DocumentoExigido`, as
duas migrations, a trigger condicional e o teste de migração que prova que artefato congelado recusa
`UPDATE` e `DELETE` no banco.

**F3 · Elaboração.** `shared/arquivos.py`, comandos de `editais/application/anexos.py`, etapa nova
do assistente com upload e download do rascunho, `revisao.COLECOES`. Ao fim desta fase o autor
monta a coleção; ninguém de fora a vê.

**F4 · Publicação e canal público.** Congelamento no `publish_edital`, seção gerada no PDF com a
lista, rota pública do artefato, lista na página da seleção. **Aqui os passos 1, 6 e 7 do teste de
aceitação passam a ser demonstráveis.**

**F5 · O vínculo e o candidato.** Vínculo no `DocumentoExigido` pela tela, regra de referência
pendurada, modelo ao lado do campo de envio no portal, e o modelo sob a versão aceita na mesa de
avaliação. Fecha os passos 3, 4 e 5.

**F6 · Retificação.** `CAMPOS_ANEXO`, acréscimo e remoção, substituição do artefato por upload
dentro do ato, congelamento na publicação da Retificação. Fecha o passo 2 e o passo 7 na forma
emblemática — os dois artefatos coexistindo.

## Achados fora de escopo, registrados e não incorporados

Nenhum deles é trabalho desta feature, e nenhum vira prioridade automática (princípio VI).

1. **A tela de Revisão não lista os Documentos Exigidos.** `interface/revisao.py:115-120` declara
   quatro coleções e omite `documentRequirements`, que está no snapshot congelado. Quem homologa
   aprova sem ver o que o Edital exigirá. O teste não pega porque só compara coleções não vazias.
   *Toca esta feature*: a mesma linha ganha `attachments`, e o FR-018 exige que a revisão veja os
   anexos — mas corrigir a omissão do vizinho é outra tarefa.
2. **`PublishedDocumentView` não honra `If-None-Match` nem envia `Cache-Control`**
   (`publicacoes/api/views.py:120-133`), sozinha entre as rotas públicas. A rota do artefato **não
   replica** a assimetria; alinhar a antiga é decisão de outra hora.
3. **`publish_edital.py:535` grava atributo que não existe no modelo** (`publication.document_hash`).
   Inócuo e enganoso.
4. **Seção gerada com `source` fora de `_CORPO_GERADO` some do PDF em silêncio**
   (`pdf.py:1672-1674`), sem falha de suíte. Esta feature acrescenta uma origem nova e por isso traz
   o teste que fecha o buraco para a sua; o guarda geral é outra tarefa.

## Complexity Tracking

| Violação | Por que é necessária | Alternativa mais simples, e por que foi recusada |
|---|---|---|
| A coleção `attachments` fica **fora** do `replace_draft`, ao contrário das outras cinco | O `replace_draft` reescreve o rascunho a partir do que o formulário reenvia, e bytes não fazem a viagem de ida e volta num POST de etapa. Dentro dele, salvar outra etapa apagaria os anexos ou obrigaria a reenviar megabytes a cada gravação | Incluir `attachments` na montagem de `_gravar_etapa` como as demais: recusada porque o formulário teria de carregar os artefatos ou referenciá-los por id enquanto o upload acontece por fora — e aí a exceção continua existindo, só que escondida. O precedente honesto é o `anexar_documento` da `009`, que grava na hora, sem `Salvar` |
| `SCHEMA_VERSION` 8 → 9, com degrau em dois níveis | Sem o degrau, todo Edital publicado hoje deixa de ser retificável (`canonical_schema_version_mismatch`, 409) | Não elevar e deixar a coleção fora do canônico: recusada porque tira o anexo da vigência, da Retificação e da consulta histórica — é a feature inteira |
| Primeiro caminho de **escrita de arquivo** na interface administrativa | O autor precisa subir o PDF; hoje só o portal do candidato recebe arquivo | Subir por API e referenciar na tela: recusada porque o princípio VI exige o canal do ator, e o ator é quem elabora no navegador |
