# Implementation Plan: O Edital do sistema como ato oficial

**Branch**: `claude/nova-spec-053-edital-b7660b` | **Date**: 2026-09-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/054-edital-como-ato-oficial/spec.md`

## Summary

Quatro frentes, sobre o mesmo compositor e o mesmo catálogo:

1. **O catálogo** (`editais/domain/secoes.py`) passa de 12 para 22 entradas, na ordem da amostra, sem
   redação padrão ([research](research.md) R-001, R-002). A textual vazia deixa de ser impeditivo e
   deixa de sair no documento; a numeração sai de uma função só, que o compositor, a etapa Conteúdo e
   a Revisão usam (R-003).
2. **A topologia na Retificação** passa a ser conferida contra a do conteúdo original do Edital, e não
   contra o catálogo vigente (R-004). É o que deixa o catálogo mudar sem trancar o acervo.
3. **O fecho**: local e data do ato, e a autoridade com nome opcional e ato de nomeação, chegam ao
   compositor como contexto do ato (R-005 a R-009). A `Publicacao` ganha uma coluna, e é a única
   migration.
4. **O que o documento calava**: a marca do consolidado (R-010), a declaração do Requerimento na
   Matrícula (R-011) e a linha de total na tabela de Perfis (R-012).

Os avisos da Revisão trocam o da redação padrão pelo das seções universais vazias (R-013); a etapa
Conteúdo mostra o número do documento, com um script pequeno que o acompanha enquanto se digita
(R-014). A fixture de bytes é refeita no mesmo commit que muda a composição (R-015).

## Technical Context

**Language/Version**: Python 3.12, Django 5 — o monólito existente; JavaScript sem build.

**Primary Dependencies**: nenhuma nova. O renderizador continua sem dependência externa.

**Storage**: PostgreSQL. **Uma** migration: `publicacoes.Publicacao.signatory_appointment`, texto
opcional com padrão vazio, numa tabela append-only — `ADD COLUMN` com padrão constante não reescreve
linha nem dispara gatilho de `UPDATE` (R-007).

**Testing**: pytest contra PostgreSQL (`make lint check test-pg DB_NAME=ps_054`); `node --test` para a
regra pura da numeração na tela; o documento gerado, lido com `pdftotext -layout` e comparado com o
original do 28/2026 (quickstart).

**Target Platform**: servidor Django; o documento é PDF composto pelo renderizador próprio.

**Project Type**: web — `backend/processo_seletivo/`.

**Performance Goals**: nenhuma meta nova. A numeração na etapa Conteúdo lê o snapshot do rascunho, que
a etapa já monta para as pendências.

**Constraints**: publicação é imutável e documento publicado não se regenera; `FR-034`, `FR-035` e
`FR-041` da `008` (contexto do ato fora do conteúdo, presença determinada pelo modo, prévia igual ao
publicado no corpo normativo); `FR-044` da `008` (fixture refeita só junto da mudança intencional);
guardiões estruturais — contagem de migrations por app, classe citada em template exige regra na
folha, varredura de citações de requisito, inventário de negativas; `replace_draft` apaga a linha de
seção não reenviada, e é isso que torna "apagar o texto" o mesmo que "esvaziar a seção".

**Scale/Scope**: o 28/2026 (15 seções, 7 Perfis) é o caso de verificação; o maior da amostra tem 22
seções (146/2025).

## Constitution Check

| Princípio | Como esta feature o cumpre |
|---|---|
| I. Linguagem ubíqua | Os títulos novos são os da amostra do Cefor; *ato de nomeação*, *versão consolidada* e *Retificação* são os termos do domínio. Nenhum termo novo nomeia conceito velho. |
| II. Imutabilidade e temporalidade | Nada publicado muda: a coluna nova nasce vazia nas Publicações existentes, e nenhum documento é regenerado. A data do fecho é o `now` da própria transação de publicação, no fuso institucional (`shared/tempo.ZONA`). A Retificação continua sem poder mexer na topologia — agora contra a do Edital, e não contra um catálogo que muda (`D-003`). |
| III. Auditoria e dados | O ato de nomeação é dado público de atribuição pública, como nome e cargo (`008`, FR-044); nenhum dado pessoal novo. Nenhum dado pessoal da amostra entra no repositório: a verificação usa cargo e portaria fictícios. |
| IV. Regras explícitas | A numeração tem **uma** regra, usada pelas três telas (R-003). A norma que o documento acrescenta a uma seção vem do conteúdo publicado, e não de texto livre. |
| V. Simplicidade | Nenhuma versão de catálogo, nenhum cadastro de autoridade, nenhuma entidade nova. O catálogo continua declarado em código. |
| VI. Jornada | Demonstrável pelo percurso do quickstart: compor o 28/2026, publicar, retificar e ler os dois documentos. |

**Gate: passa.** A emenda de três requisitos de specs anteriores (`FR-036` e `SC-001` da `008`,
`FR-037` e `FR-041` da `006`) é feita por esta spec, que os nomeia, e cada um recebe nota de emenda no
próprio texto (R-017).

## O prazo: antes da primeira publicação real

O catálogo precisa estar valendo **antes** do primeiro Edital real publicado pelo piloto. Três
consequências, em ordem:

1. **Esta feature entra inteira ou não entra.** O catálogo novo sem a regra de topologia da
   Retificação (R-004) tranca a Retificação de todo Edital publicado antes do deploy. Por isso as duas
   estão no mesmo PR, e a regra da topologia é a primeira tarefa de código.
2. **Se o piloto publicar antes do merge**, nada quebra: o Edital sai com as 12 seções de hoje, e a
   partir do merge continua retificável, com o consolidado na forma em que foi publicado (`SC-366`).
   O custo é o acervo com duas formas de documento — o que o prazo existe para evitar, e não um
   defeito. A conferência antes do merge é perguntar ao Cefor se já houve publicação real, e é do
   usuário.
3. **Edital homologado e não publicado no dia do deploy** precisa ser submetido de novo (spec, *Edge
   Cases*). O quickstart traz a consulta que os lista.

Depois do merge, uma mudança futura de catálogo continua possível sem versão: a Retificação confere a
topologia contra o Edital, e o Edital já publicado guarda a forma dele.

## Project Structure

### Documentation (this feature)

```text
specs/054-edital-como-ato-oficial/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/documento-publicado.md
├── rastreabilidade.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/editais/domain/
├── secoes.py            # o catálogo de 22, sem default_text — R-001, R-002
└── validation.py        # topologia com referência (R-004); textual pode ser vazia; avisos (R-013)

backend/processo_seletivo/publicacoes/
├── domain/autoridades.py          # cargo obrigatório, nome e ato de nomeação opcionais — R-008
├── models.py                      # Publicacao.signatory_appointment — R-007
├── migrations/0009_*.py           # a coluna
├── infrastructure/humano.py       # data por extenso — R-006
├── infrastructure/pdf.py          # numeração (R-003), fecho (R-005), marca (R-010), Matrícula (R-011), total (R-012)
├── application/publish_edital.py  # data do ato e ato de nomeação ao compositor e à Publicação
├── application/retificacoes.py    # topologia de referência; data, histórico e vigência do consolidado
├── application/selectors.py       # quem assinou, sem separador pendurado — R-009
└── api/{serializers,public_serializers}.py  # ato de nomeação, opcional — R-007

backend/processo_seletivo/interface/
├── forms.py                       # ler_secoes sem padrão; secoes_do_edital com número e norma acrescentada
├── revisao.py                     # a seção pelo número do documento — R-003
├── views.py                       # contexto da etapa Conteúdo; signatário com ato de nomeação; código do aviso novo
├── templatetags/interface_extras.py  # rótulo do aviso novo
├── templates/interface/compor_conteudo.html  # número, estado, norma acrescentada — R-014
└── static/interface/conteudo.js   # a numeração que acompanha o digitado

backend/scripts/gerar_fixture_documento.py     # contexto do ato versionado ao lado — R-015
backend/tests/contract/fixtures/               # snapshot, autoridade e documento refeitos
backend/tests/                                  # os testes da 054; os que prendiam o catálogo antigo, emendados
specs/006-*/spec.md, specs/008-*/spec.md        # notas de emenda — R-017
```

**Structure Decision**: o monólito de sempre; nenhuma camada nova.

## Complexity Tracking

Nenhuma violação a justificar.
