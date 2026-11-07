# Implementation Plan: A inaplicabilidade documental tem fundamento publicado

**Branch**: `claude/nostalgic-gagarin-492fdc` | **Date**: 2026-11-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/131-inaplicabilidade-documental/spec.md`

**Estado**: plano escrito sobre as decisões D-001 a D-016 da spec, **propostas**, ainda não aceitas.
Nenhum código foi alterado. **A implementação espera a P-1 e a P-2.** Se a D-001 for recusada (opção
1), o incremento A sai inteiro, e os incrementos B e C ficam, com a FR-4457 trocada por *"o
'não se aplica' de obrigatório pede a ciência"* e a FR-4470 sem efeito.

## Summary

Três incrementos, nesta ordem, porque cada um lê o anterior.

- **A. A condição de exigência na composição** (P1, D-001 a D-004, D-012, D-013).
  - O Documento Exigido ganha `condicao` no rascunho e `requiredWhen` no publicado.
  - `SCHEMA_VERSION` sobe para 19, com o degrau de elevação aditivo.
  - O campo entra em todas as listas de campos que os guardiões obrigam (R-004), no PDF depois do
    nome, e na revisão.
  - Uma migration, na `editais`.
- **B. A conferência** (P1, D-005 a D-010).
  - `conferir` recusa o item fora do recorte (R-007).
  - Recusa o *"não se aplica"* sem condição, sem abertura e com motivo sem conteúdo.
  - Pede o motivo de substituição quando o *"não se aplica"* está envolvido.
  - A página dos documentos mostra a condição e só oferece o que cabe.
- **C. O aceite, a formalização e a transição** (P1/P2, D-011, D-014 a D-016).
  - A leitura documental separa as contagens e conhece a condição do item.
  - A guarda conta o *"não se aplica"* só no condicional.
  - O desfecho pede a ciência por assinatura e a cita na trilha.
  - A formalização ganha a situação *"não se aplica após análise"*.
  - O portal mostra a condição.

Sem tabela nova, sem coluna em tabela append-only, sem papel, sem rota nova (a ciência viaja no POST
do desfecho que já existe).

## Technical Context

**Language/Version**: Python 3.13, Django 5.x (o do `pyproject.toml`)

**Primary Dependencies**: as da `main`. Nenhuma nova.

**Storage**: PostgreSQL. Uma migration na `editais` (`0025`, coluna `condicao` em
`DocumentoExigido`, que é rascunho e não é append-only). O guardião da contagem de migrations por
app precisa do número novo.

**Testing**: pytest contra PostgreSQL (`make test-pg`). Domínio, integração e cliente de teste. Sem
caso novo de navegador (R-012).

**Target Platform**: o monólito Django; gestão e portal sem script novo (CSP `'self'`). A caixa de
ciência é HTML puro.

**Project Type**: aplicação web.

**Performance Goals**: a condução e a página dos documentos em número fixo de consultas
(SC-1377). A condição sai do conteúdo da versão que `leituras_por_chamada` já traz por `prefetch`.

**Constraints**:
- o PDF do documento sem condição sai byte a byte igual (`test_documento_publicado.py`);
- nenhum 404 novo fora do inventário da `033`: a recusa da FR-4464 é o `nao_encontrado` que `conferir`
  já devolve;
- o repositório é público, e nenhum nome real vai a teste ou captura.

**Scale/Scope**: ~20 pontos na composição (R-004), 1 comando de conferência, 1 guarda de desfecho, 3
templates da gestão, 1 do portal, 1 seletor da formalização.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o plano o atende | Situação |
|---|---|---|
| I. Linguagem ubíqua | *Condição publicada*, *não se aplica após análise* e *não se aplica* (recorte) nomeiam três coisas diferentes, em todas as superfícies | ✅ |
| II. Imutabilidade e versionamento | A condição é da versão; a lista lê a versão em que nasceu; degrau aditivo, literal publicado intocado; nenhuma conferência reescrita | ✅ |
| III. Negar por padrão, auditoria, LGPD | O fora do recorte é inexistente no comando; a ciência fica na trilha por identificador; nenhum motivo novo na trilha nem no manifesto | ✅ |
| IV. Regras explícitas | A regra mora no comando e no domínio (FR-4457, FR-4464), e não na tela. O que o sistema derivou é mostrado antes do ato irreversível (FR-4467): é a frase do princípio sobre decisões derivadas | ✅ |
| V. Rastreabilidade, simplicidade | Um campo de texto, sem semântica; nenhuma camada nova; um teste por requisito e por caso-limite | ✅ |
| VI. Jornada pelo canal do ator | O candidato vê a condição no portal; quem desfecha vê as inaplicabilidades no próprio formulário | ✅ |

Nenhuma violação. Reavaliado depois do desenho: igual.

## Project Structure

### Documentation (this feature)

```text
specs/131-inaplicabilidade-documental/
├── spec.md
├── plan.md                      # este arquivo
├── research.md                  # R-001 a R-012
├── data-model.md                # o campo, as figuras, o contrato de estados, a rastreabilidade
├── quickstart.md                # roteiro de verificação
├── contracts/
│   ├── cenarios.md              # os treze cenários e os da composição
│   └── conferencia.md           # o comando, os códigos de recusa e o POST do desfecho
├── checklists/requirements.md
├── rastreabilidade.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/
│   ├── models/documentos.py               # A: coluna `condicao`
│   ├── migrations/0025_condicao_do_documento_exigido.py
│   ├── api/serializers.py                 # A: campo aninhado
│   ├── application/draft.py               # A: persistência
│   └── domain/
│       ├── documentos.py                  # A: problemas_da_condicao, condicao_de(requisito)
│       ├── validation.py                  # A: forma publicada e regra impeditiva
│       └── mutabilidade.py                # A: retificável
├── publicacoes/
│   ├── application/publish_edital.py      # A: requiredWhen
│   ├── domain/elevacao.py                 # A: degrau 19
│   ├── domain/alteracoes.py               # A: rótulo
│   └── infrastructure/pdf.py              # A: texto_do_documento, redação 1
├── shared/canonical.py                    # A: SCHEMA_VERSION 19
├── duvidas/domain/cobertura.py            # A: classificação e versão do esquema
├── convocacao/
│   ├── domain/documentos.py               # B, C: impede_incluir, motivo_tem_conteudo
│   ├── domain/alcance.py                  # C: assinatura_das_inaplicabilidades
│   ├── domain/nomes.py                    # B, C: códigos novos
│   └── application/
│       ├── documentos.py                  # B, C: conferir, LeituraDocumental, contagens
│       └── desfechar.py                   # C: ciência e trilha
├── formalizacao/
│   ├── domain/nomes.py                    # C: NAO_SE_APLICA_APOS_ANALISE
│   └── application/conjunto.py            # C: _da_convocacao
├── interface/
│   ├── forms.py, retificacao.py, revisao.py, views.py
│   └── templates/interface/
│       ├── _documento.html                # A: campo
│       ├── convocacao_documentos.html     # B: condição, opções
│       └── convocacao.html                # C: contagens, bloco, ciência
└── portal/
    ├── obrigacoes.py                      # C: texto do condicional a apresentar
    └── templates/portal/_cartao_do_documento_da_convocacao.html

specs/001-processo-seletivo-editais/contracts/openapi.yaml   # A: DocumentoExigidoPublicado
```

**Structure Decision**: o monólito existente, sem app novo. Cada regra fica no módulo que já é dono
dela.

## Fases

### Fase 0 — Pesquisa

Feita: [research.md](research.md), R-001 a R-012.

### Fase 1 — Desenho

Feito:

- [data-model.md](data-model.md);
- [contracts/conferencia.md](contracts/conferencia.md);
- [contracts/cenarios.md](contracts/cenarios.md);
- [quickstart.md](quickstart.md).

### Fase 2 — Tarefas

[tasks.md](tasks.md). A ordem é A → B → C, e as revisões das specs anteriores vão com o incremento
que as torna verdadeiras.

## Riscos

| Risco | Mitigação |
|---|---|
| Um guardião de lista de campos esquecido | R-004 lista os dezenove; a suíte inteira roda depois do incremento A, antes de B |
| Os bytes do PDF mudam para documento sem condição | `texto_do_documento` só acrescenta quando há condição; o teste byte a byte prende |
| A P-1 (a) trava uma chamada aberta de demonstração | É o efeito pedido; a recusa nomeia o item e diz *"registrado sem condição publicada"* |
| A ciência vira clique automático | A assinatura prende o conjunto visto. A leitura do conteúdo é humana, e esta spec não finge resolvê-la |
| Conflito com o PR #425 em `desfechar.py` e `documentos.py` | Implementar depois do merge do #425; a guarda da lista vem antes de tudo o que esta spec acrescenta |
| Compositor usar a condição para documento que não é condicional | A condição é publicada no PDF e passa pela homologação: é norma do Edital, e não atalho da conferência |

## Complexity Tracking

Nenhuma violação a justificar.
