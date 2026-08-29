# Implementation Plan: Endereçamento Normativo por Chave Estável

**Branch**: `004-enderecamento-normativo-estavel` | **Date**: 2026-08-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-enderecamento-normativo-estavel/spec.md`

**Status**: Fase 1 concluída. Pronta para `speckit-tasks`.

## Summary

Trocar o endereçamento das Alterações Normativas de posição para chave estável, eliminando a causa
do defeito que a `003` conteve.

Uma Alteração hoje diz `/profiles/1/name`. O `1` é a posição no momento da elaboração, e qualquer
Retificação publicada no intervalo que remova ou insira um Perfil anterior faz o ato falar de outro
Perfil. A `003` tornou isso impossível de passar em silêncio — recusa com `409` —, mas recusar é
tudo o que ela alcança: quando a lista muda de forma, a Retificação precisa ser refeita mesmo que o
Perfil dela não tenha sido tocado.

O caminho passa a ser `/profiles/id=<uuid>/name`, com `before=`/`after=` para inserção e
substituição atômica para as coleções sem chave. Escrever por posição deixa de ser admitido onde há
identidade; ler continua aceitando as duas formas para sempre, porque ato publicado não se reescreve.

Disso decorre o resultado que a `003` não podia entregar: **a âncora de identidade dela pode ser
aposentada**. Com todo caminho gravável nomeando a entidade ou sendo atômico, não sobra índice para
deslocar — que era a única pergunta que a âncora respondia. A precondição por hash fica, porque
responde outra.

## Technical Context

**Language/Version**: Python 3.13 — o mesmo do backend, mesmo projeto

**Primary Dependencies**: nenhuma nova. Django 5.2 LTS, DRF 3.16, psycopg 3. A extensão de caminho é
gramática própria, resolvida no domínio; não há biblioteca de JSON Pointer envolvida hoje e não
passa a haver

**Storage**: PostgreSQL 16+. Nenhuma coluna nova. Uma migração de dados que converte
`AlteracaoNormativa.target_path` das Retificações não finais, e uma segunda que retira
`expected_anchors` depois de a conversão se confirmar

**Testing**: pytest e pytest-django, nas duas execuções — SQLite e PostgreSQL, esta última sem
ignorados. A migração de conversão exige teste sobre banco com dados nos três estados não finais,
que só o PostgreSQL exercita de verdade

**Target Platform**: mesmo processo Django do backend

**Project Type**: monólito modular existente; nenhuma estrutura nova

**Performance Goals**: nenhuma meta própria. A resolução por chave troca acesso por índice por
varredura da coleção, e as coleções normativas têm dezenas de elementos, não milhares — a spec
declara isso fora de escopo com justificativa, e inventar meta antes de haver medida seria ruído

**Constraints**: nenhum ato publicado pode mudar de efeito; nenhuma migração aplicada pode ser
reescrita; a conversão nunca infere — devolve; a leitura das duas formas é permanente

**Scale/Scope**: o mesmo da `001`. Um Edital tem dezenas de Perfis e Eventos; o número de
Retificações não finais no dia da virada é da ordem de unidades

**NEEDS CLARIFICATION**: nenhum. As cinco decisões abertas foram respondidas na sessão de
clarificação de 2026-08-29, e o portão de qualidade fechou 40 itens satisfeitos e 1 N/A antes deste
plano existir.

## Constitution Check

| Princípio | Situação |
| --- | --- |
| I — Linguagem ubíqua e integridade do domínio | **Atendido, e esta é a feature que o atende.** "Entidades DEVEM possuir identificadores estáveis" era a ressalva registrada na `003`; o endereçamento passa a usar os identificadores que as entidades já carregam. |
| II — Integridade normativa, imutabilidade e temporalidade | **Reforçado.** Ato publicado não é reescrito (FR-005); a leitura das duas formas preserva a reprodutibilidade do passado (FR-001d, SC-002, SC-003). |
| III — Segurança, proteção de dados e auditoria | **Reforçado.** A conversão é registrada com caminho antes e depois, inclusive em ato homologado (FR-005b) — mudança silenciosa em ato de autoridade é o que a trilha existe para impedir. |
| IV — Regras explícitas e consistência operacional | **Reforçado.** A recusa do endereçamento posicional acontece na elaboração (FR-001c): ato que nasce instável não chega a existir. |
| V — Qualidade, rastreabilidade e simplicidade | **Atendido.** Mapa de rastreabilidade nos dois sentidos na spec; nenhum requisito órfão, nenhum critério sem requisito. |
| Fluxo de desenvolvimento | **Atendido, sem exceção.** Ao contrário da `003`, aqui a ordem foi respeitada: especificação, clarificação, portão de qualidade, planejamento. Nenhuma linha de código foi escrita. |

## Decisões técnicas

### Decisão 1 — A gramática do segmento, e onde ela é interpretada

Um segmento de caminho passa a admitir quatro formas, e **qual delas vale depende do contêiner**:

| Forma | Contêiner | Significado |
| --- | --- | --- |
| `nome` | objeto | chave literal, como sempre |
| `0`, `1`, … | lista | índice — só na **leitura** de atos antigos |
| `-` | lista | posição de acréscimo ao fim |
| `id=<valor>` | lista | o elemento cujo `id` é `<valor>` |
| `before=<valor>` / `after=<valor>` | lista | posição relativa ao elemento nomeado; só em `ADD` |

Interpretar o seletor apenas em lista (FR-001a) é o que preserva a expressividade: em objeto, uma
chave chamada `id=algo` continua endereçável. Sem essa regra, a extensão tiraria do RFC 6901 algo
que ele permitia.

A resolução vive em `publicacoes/domain/changes.py`, junto de `parse_path` e `_descend`, porque é
onde a semântica de caminho já mora. Nada disso sobe para a aplicação.

### Decisão 2 — Quais coleções têm chave é declaração, não descoberta

`profiles`, `schedule` e `competitionModalities` carregam `id`; `requirements` não. Detectar isso em
tempo de execução — "se o elemento é dict e tem `id`" — funcionaria hoje e falharia em silêncio no
dia em que uma coleção nova nascesse sem identificador.

A declaração fica explícita no domínio e é **verificada por teste** contra um snapshot real
(FR-004c). Uma migration futura que acrescente coleção sem chave faz a suíte falhar, em vez de
tornar o pressuposto de FR-004a falso sem que nada acuse.

### Decisão 3 — Recusar na elaboração, verificar na Publicação

São dois momentos e duas perguntas, como a `003` estabeleceu:

- **Elaboração**: o caminho usa índice numérico numa coleção com chave? Recusa
  (`positional_addressing_refused`). Ato que nasce instável não chega a existir.
- **Publicação**: a entidade endereçada ainda existe no conteúdo vigente no início da vigência?
  Recusa (`target_key_not_found`). A referência de um `before=` ainda existe?
  (`position_reference_not_found`).

A precondição por hash da `003` continua rodando nos dois momentos, sem alteração.

### Decisão 4 — A conversão congela a própria lógica, como a `0006` da `003`

A migração que converte os caminhos das Retificações não finais reescreve ato em curso a partir de
`expected_anchors`. Vale a mesma regra que a `003` aprendeu na revisão: **migração aplicada tem de
continuar significando o que significava no dia em que rodou**, então a lógica de conversão é
copiada e congelada dentro dela, e o teste que recusa migration importando domínio ou aplicação
continua valendo.

O critério de inequivocidade é o de FR-005c — âncora existe, é única, corresponde à mesma entidade
no snapshot-base — e qualquer falha devolve com motivo, nunca infere.

### Decisão 5 — A âncora sai em duas etapas, não numa

Aposentar `expected_anchors` num movimento só juntaria três coisas de risco diferente: parar de
derivar, parar de verificar, e apagar a coluna. A ordem é:

1. Parar de derivar para atos novos, e parar de verificar — a âncora deixa de ter função quando
   nenhum caminho gravável tem índice.
2. Uma migração posterior **verifica** a condição de SC-007 — nenhuma Retificação não final com
   `expected_anchors` preenchido — e só então remove a coluna.

Separar permite que a etapa 1 seja revertida sem perder dado, e faz a remoção da coluna acontecer
sobre uma condição comprovada em vez de sobre uma expectativa.

### Decisão 6 — A interface fica mais simples, não mais complexa

`interface/retificacao.py` documenta hoje que a ordem de emissão das alterações **é a garantia de
correção**: primeiro os `REPLACE` com os índices do vigente, depois os `REMOVE` em ordem
decrescente, por último os `ADD`. Toda essa coreografia existe porque índice desloca.

Com chave, ela some. `REPLACE` e `REMOVE` passam a ser independentes de ordem, e é exatamente o que
a US3, cenário 2, pede. A tela não muda para quem usa (FR-007); o que ela emite muda, e o código que
emite encolhe.

### Decisão 7 — O contrato continua tendo uma fonte só

Como na `003`, a alteração entra no `openapi.yaml` da `001`, que segue sendo o contrato único. O
`contracts/` desta feature descreve a **gramática** do caminho e os códigos de recusa — o que um
arquivo OpenAPI não expressa bem — e aponta para o que deve ser alterado lá, sem duplicar o
documento.

## Project Structure

### Documentation (this feature)

```text
specs/004-enderecamento-normativo-estavel/
├── spec.md              # 28 requisitos, 11 critérios, 4 histórias, 10 casos de borda
├── plan.md              # este documento
├── research.md          # Fase 0: alternativas de resolvedor, migração e aposentadoria
├── data-model.md        # Fase 1: gramática, coleções com chave, o que muda em cada tabela
├── quickstart.md        # Fase 1: como validar, com o resultado esperado de cada passo
├── contracts/
│   └── enderecamento.md # Fase 1: gramática do caminho, códigos de recusa, delta do openapi
└── checklists/
    └── normativo.md     # portão de qualidade: 40 satisfeitos, 1 N/A
```

### Source Code (repository root)

```text
backend/
├── processo_seletivo/
│   ├── publicacoes/
│   │   ├── domain/
│   │   │   ├── changes.py          # gramática do segmento e resolução por chave
│   │   │   ├── conflicts.py        # precondição fica; derivação de âncora sai
│   │   │   └── colecoes.py         # NOVO: quais coleções têm chave, declarado
│   │   ├── application/
│   │   │   └── retificacoes.py     # recusa na elaboração; verificação na Publicação
│   │   ├── api/serializers.py      # validação de forma do targetPath
│   │   └── migrations/
│   │       ├── 0008_converter_caminhos.py    # conversão, lógica congelada
│   │       └── 0009_remover_ancoras.py       # remove a coluna sob condição verificada
│   └── interface/
│       └── retificacao.py          # emite por chave; a coreografia de ordem some
└── tests/
    ├── unit/publicacoes/           # gramática, resolução, coleções declaradas
    ├── integration/publicacoes/    # os dois momentos de recusa, composição
    ├── migrations/                 # conversão: converte, devolve, no-op, congelamento
    └── interface/                  # a tela emite por chave sem expor caminho
```

**Structure Decision**: monólito modular existente, sem estrutura nova. Um módulo novo —
`publicacoes/domain/colecoes.py` — porque a declaração de quais coleções têm chave é conhecimento de
domínio consultado por três lugares (resolução, recusa na elaboração, teste de guarda), e deixá-la
dentro de `changes.py` a esconderia num arquivo já denso.

## Fases

| Fase | Conteúdo | Situação |
| --- | --- | --- |
| — | Especificação e clarificação | Concluída — 5 decisões registradas |
| — | Portão de qualidade dos requisitos | Concluído — 40 satisfeitos, 1 N/A |
| 0 | Pesquisa: alternativas de resolvedor, migração, aposentadoria | Concluída — `research.md` |
| 1 | Desenho: gramática, modelo, contrato, validação | Concluída — `data-model.md`, `contracts/`, `quickstart.md` |
| 2 | Tarefas | Pendente — `speckit-tasks` |

## Complexity Tracking

| Desvio | Por quê | Alternativa descartada |
| --- | --- | --- |
| Extensão local do JSON Pointer | Não há seleção por atributo no RFC 6901, e alguma extensão é inevitável. A escolha foi torná-la **declarada** em vez de disfarçada: o UUID como token cru pareceria padrão e não seria, porque resolver identificador dentro de array também é semântica customizada | `/profiles/<uuid>/name`. Descartada por ser dialeto que se esconde, num campo que fica gravado para sempre no ato publicado |
| Duas formas de caminho convivendo na leitura, para sempre | Ato publicado não se reescreve — a Constituição proíbe e as triggers da `003` recusam. A forma antiga permanece no histórico por consequência da imutabilidade, não por escolha | Migrar o histórico. Descartada: seria alterar ato normativo já produzido |
| Migração de dados que reescreve ato em curso | Sem ela, os atos que atravessam a virada publicariam instáveis depois de a cura existir — justamente os de maior risco | Devolver todos. Descartada por custar retrabalho e, nas homologadas, desfazer ato de autoridade por motivo de representação e não de mérito |
| Duplicação da lógica de conversão dentro da migração | Migração aplicada não pode mudar de efeito porque o domínio evoluiu. É a mesma regra que a `003` aprendeu na revisão de fechamento | Importar do domínio. Descartada: é exatamente o acoplamento que quebra a reprodutibilidade histórica |
