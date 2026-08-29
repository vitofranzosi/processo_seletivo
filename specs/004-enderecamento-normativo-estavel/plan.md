# Implementation Plan: Endereçamento Normativo por Chave Estável

**Branch**: `004-enderecamento-normativo-estavel` | **Date**: 2026-08-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-enderecamento-normativo-estavel/spec.md`

**Status**: Escopo reduzido em 2026-08-29. Desenho concluído; implementação não iniciada.

## Summary

Trocar o endereçamento das Alterações Normativas de posição para chave estável, eliminando a causa
do defeito que a `003` conteve.

Uma Alteração hoje diz `/profiles/1/name`. O `1` é a posição no momento da elaboração, e qualquer
Retificação publicada no intervalo que remova ou insira um Perfil anterior faz o ato falar de outro
Perfil. A `003` tornou isso impossível de passar em silêncio — recusa com `409` —, mas recusar é
tudo o que ela alcança: quando a lista muda de forma, a Retificação precisa ser refeita mesmo que o
Perfil dela não tenha sido tocado.

O caminho passa a ser `/profiles/id=<uuid>/name`. Acréscimo é `/profiles/-`, ao fim. Coleção sem
chave é substituída inteira. Endereçar por posição deixa de ser admitido onde há chave.

Disso decorre o resultado que a `003` não podia entregar: **a âncora de identidade dela sai**. Com
todo caminho nomeando a entidade ou sendo atômico, não sobra índice para deslocar — que era a única
pergunta que a âncora respondia. A precondição por hash fica, porque responde outra.

**O sistema não está em produção e não há dado a preservar.** É o que torna esta feature pequena:
não há conversão, não há duas formas convivendo, não há migração de dados. A remoção de
`expected_anchors` é migração de esquema e nada mais.

## Technical Context

**Language/Version**: Python 3.13 — o mesmo do backend, mesmo projeto

**Primary Dependencies**: nenhuma nova. Django 5.2 LTS, DRF 3.16, psycopg 3. A extensão de caminho é
gramática própria, resolvida no domínio

**Storage**: PostgreSQL 16+. Nenhuma coluna nova. Uma migração de esquema que remove
`AlteracaoNormativa.expected_anchors`, sem conversão de dados

**Testing**: pytest e pytest-django, nas duas execuções — SQLite e PostgreSQL, esta última sem
ignorados

**Target Platform**: mesmo processo Django do backend

**Project Type**: monólito modular existente; nenhuma estrutura nova

**Performance Goals**: nenhuma meta própria. A resolução por chave troca acesso por índice por
varredura da coleção, e as coleções normativas têm dezenas de elementos — a spec declara isso fora
de escopo, e inventar meta antes de haver medida seria ruído

**Constraints**: a recusa do endereçamento posicional acontece na elaboração; a precondição por hash
permanece intacta; nenhuma migração aplicada pode ser reescrita

**Scale/Scope**: o mesmo da `001`. Um Edital tem dezenas de Perfis e Eventos

**Questões em aberto**: nenhuma.

## Constitution Check

| Princípio | Situação |
| --- | --- |
| I — Linguagem ubíqua e integridade do domínio | **Atendido, e esta é a feature que o atende.** "Entidades DEVEM possuir identificadores estáveis" era a ressalva registrada na `003`; o endereçamento passa a usar os identificadores que as entidades já carregam. |
| II — Integridade normativa, imutabilidade e temporalidade | **Atendido.** Nenhum registro publicado é reescrito — não há nenhum. A migração toca esquema, não conteúdo normativo. |
| III — Segurança, proteção de dados e auditoria | **Neutro.** A feature não altera autorização nem trilha. Sai um código de recusa, entram três. |
| IV — Regras explícitas e consistência operacional | **Reforçado.** A recusa acontece na elaboração: ato que nasce instável não chega a existir. |
| V — Qualidade, rastreabilidade e simplicidade | **Atendido.** Mapa de rastreabilidade nos dois sentidos na spec. A redução de escopo é aplicação direta de "a arquitetura DEVE preferir a solução mais simples que preserve os requisitos". |
| Fluxo de desenvolvimento | **Atendido, sem exceção.** Especificação, clarificação, portão de qualidade, plano, tarefas, análise. Nenhuma linha de código escrita. |

## Decisões técnicas

### Decisão 1 — A gramática do segmento, e onde ela é interpretada

Um segmento de caminho admite quatro formas, e **qual delas vale depende do contêiner**:

| Forma | Contêiner | Significado |
| --- | --- | --- |
| `nome` | objeto | chave literal, como sempre |
| `0`, `1`, … | lista | índice — recusado na escrita sobre coleção com chave |
| `-` | lista | acréscimo ao fim |
| `id=<uuid>` | lista | o elemento cujo `id` é `<uuid>` |

Interpretar o seletor apenas em lista (FR-002) é o que preserva a expressividade: em objeto, uma
chave chamada `id=algo` continua endereçável. Sem essa regra, a extensão tiraria do RFC 6901 algo
que ele permitia.

A resolução vive em `publicacoes/domain/changes.py`, junto de `parse_path` e `_descend`, porque é
onde a semântica de caminho já mora. Nada disso sobe para a aplicação.

### Decisão 2 — Quais coleções têm chave é declaração, não descoberta

`profiles`, `schedule` e `competitionModalities` carregam `id`; `requirements` não. Detectar isso em
tempo de execução — "se o elemento é dict e tem `id`" — funcionaria hoje e falharia em silêncio no
dia em que uma coleção nova nascesse sem identificador.

A declaração fica explícita no domínio e é **verificada por teste** contra um snapshot real
(FR-012). Uma migration futura que acrescente coleção sem chave faz a suíte falhar.

### Decisão 3 — Recusar na elaboração, verificar na Publicação

São dois momentos e duas perguntas, como a `003` estabeleceu:

- **Elaboração**: o caminho usa índice numa coleção com chave? Recusa
  (`positional_addressing_refused`). Ato que nasce instável não chega a existir.
- **Publicação**: a entidade endereçada ainda existe no conteúdo vigente no início da vigência?
  Recusa (`target_key_not_found`).

A precondição por hash da `003` continua rodando nos dois momentos, sem alteração.

### Decisão 4 — A âncora sai numa migração de esquema

A versão anterior deste plano previa duas migrações: uma que convertia caminhos a partir de
`expected_anchors`, com lógica congelada, e outra que removia a coluna sob condição comprovada. Sem
dado a preservar, as duas colapsam numa só: `RemoveField`.

Some junto tudo o que existia para sustentar a conversão — critério de inequivocidade, devolução
auditada, relatório por origem. Nada disso tinha objeto.

### Decisão 5 — Não construir `before=` e `after=`

A versão anterior previa referências de posição para inserir um Perfil antes ou depois de outro. A
interface não oferece essa operação, e ninguém a pediu. Acréscimo é `/colecao/-`, ao fim.

Vale o mesmo para o identificador: o seletor aceita **UUID**, que é o que as entidades carregam.
Aceitar "qualquer texto" seria construir para um caso que não existe.

### Decisão 6 — A interface fica mais simples, não mais complexa

`interface/retificacao.py` documenta hoje que a ordem de emissão das alterações **é a garantia de
correção**: primeiro os `REPLACE` com os índices do vigente, depois os `REMOVE` em ordem
decrescente, por último os `ADD`. Toda essa coreografia existe porque índice desloca.

Com chave, ela some. `REPLACE` e `REMOVE` passam a ser independentes de ordem, e é exatamente o que
a US2, cenário 2, pede. A tela não muda para quem usa (FR-019); o que ela emite muda, e o código que
emite encolhe.

### Decisão 7 — O contrato continua tendo uma fonte só

Como na `003`, a alteração entra no `openapi.yaml` da `001`, que segue sendo o contrato único. O
`contracts/` desta feature descreve a **gramática** do caminho e os códigos de recusa — o que um
arquivo OpenAPI não expressa bem — e aponta o que alterar lá, sem duplicar o documento.

## Project Structure

### Documentation (this feature)

```text
specs/004-enderecamento-normativo-estavel/
├── spec.md              # 19 requisitos, 7 critérios, 2 histórias
├── plan.md              # este documento
├── research.md          # Fase 0: alternativas de resolvedor e de declaração
├── data-model.md        # Fase 1: gramática, coleções com chave, a migração de esquema
├── quickstart.md        # Fase 1: como validar, com o resultado esperado de cada passo
├── contracts/
│   └── enderecamento.md # Fase 1: gramática do caminho, códigos de recusa, delta do openapi
└── checklists/
    └── normativo.md     # portão de qualidade, reavaliado após a redução de escopo
```

### Source Code (repository root)

```text
backend/
├── processo_seletivo/
│   ├── publicacoes/
│   │   ├── domain/
│   │   │   ├── changes.py          # gramática do segmento e resolução por chave
│   │   │   ├── conflicts.py        # precondição fica; âncora sai por completo
│   │   │   └── colecoes.py         # NOVO: quais coleções têm chave, declarado
│   │   ├── application/
│   │   │   └── retificacoes.py     # recusa na elaboração; verificação na Publicação
│   │   ├── api/serializers.py      # validação de forma do targetPath
│   │   ├── models_retificacao.py   # remove o campo expected_anchors
│   │   └── migrations/
│   │       └── 0008_remover_ancoras.py   # RemoveField, sem conversão
│   └── interface/
│       └── retificacao.py          # emite por chave; a coreografia de ordem some
└── tests/
    ├── unit/publicacoes/           # gramática, resolução, coleções declaradas
    ├── integration/publicacoes/    # os dois momentos de recusa, composição
    └── interface/                  # a tela emite por chave sem expor caminho
```

**Structure Decision**: monólito modular existente, sem estrutura nova. Um módulo novo —
`publicacoes/domain/colecoes.py` — porque a declaração de quais coleções têm chave é conhecimento de
domínio consultado por três lugares (resolução, recusa na elaboração, teste de guarda), e deixá-la
dentro de `changes.py` a esconderia num arquivo já denso.

## Fases

| Fase | Conteúdo | Situação |
| --- | --- | --- |
| — | Especificação e clarificação | Concluída |
| — | Portão de qualidade dos requisitos | Concluído |
| 0 | Pesquisa: alternativas de resolvedor e de declaração | Concluída |
| 1 | Desenho: gramática, modelo, contrato, validação | Concluída |
| 2 | Tarefas | Concluída |
| 3 | Análise de consistência | Concluída |
| 4 | Implementação | **Não iniciada** |

## Complexity Tracking

| Desvio | Por quê | Alternativa descartada |
| --- | --- | --- |
| Extensão local do JSON Pointer | Não há seleção por atributo no RFC 6901, e alguma extensão é inevitável. A escolha foi torná-la **declarada** em vez de disfarçada: o UUID como token cru pareceria padrão e não seria, porque resolver identificador dentro de array também é semântica customizada | `/profiles/<uuid>/name`. Descartada por ser dialeto que se esconde, num campo que fica gravado para sempre no ato publicado |
| Remoção de coluna sem período de convivência | Não há dado na coluna que importe preservar, e manter mecanismo sem função vira armadilha: alguém volta a preenchê-lo achando que protege algo | Depreciar e remover depois. Descartada por acrescentar etapa a um sistema sem usuários |
