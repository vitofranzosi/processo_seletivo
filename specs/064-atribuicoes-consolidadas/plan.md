# Implementation Plan: As atribuições idênticas saem uma vez no documento do Edital

**Branch**: `claude/064-atribuicoes-consolidadas` | **Date**: 2026-10-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/064-atribuicoes-consolidadas/spec.md`

## Summary

Quando dois ou mais Perfis têm o mesmo texto de atribuições — igual na forma do FR-1187 —, o
documento do Edital imprime o texto uma vez, numa subseção comum ao fim da seção de Perfis, e cada
Perfil remete ao número dela. A mudança é **uma função do renderizador**: `_perfis` passa a calcular
os grupos antes de compor (D-001), com a chave de identidade feita das mesmas peças que a impressão
usa (D-002). Nada fora da composição muda — nem modelo, nem conteúdo, nem tela, nem documento já
guardado.

## Technical Context

**Language/Version**: Python 3.13, Django 5.2

**Primary Dependencies**: nenhuma nova. O renderizador de PDF é próprio e sem dependência externa
(`publicacoes/infrastructure/pdf.py`).

**Storage**: nenhuma mudança. PostgreSQL continua guardando os documentos publicados, que não são
regerados.

**Testing**: pytest, contra PostgreSQL (`make test-pg`, com `DB_NAME` próprio da worktree).

**Target Platform**: o monólito Django; o documento é lido em qualquer leitor de PDF.

**Project Type**: aplicação web (monólito).

**Performance Goals**: compor não fica perceptivelmente mais lento — o agrupamento é uma passada
sobre os Perfis, com um dicionário por chave. Nenhuma consulta nova: o renderizador não lê o banco.

**Constraints**: o documento de um Perfil só sai com os mesmos bytes (FR-1194); a prévia e o
publicado quebram nas mesmas páginas; nenhum número de Perfil, seção ou tabela se move (FR-1192).

**Scale/Scope**: Editais de até algumas dezenas de Perfis; o maior caso conhecido é o 90/2026, com
dez.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o atende | Resultado |
|---|---|---|
| **I. Linguagem ubíqua** | As frases do documento são as de um Edital — "Atribuições comuns aos Perfis A e B", "as descritas no item 4.11" —, e não vocabulário do sistema ([contrato](contracts/documento.md)). | ✅ |
| **II. Integridade normativa e imutabilidade** | O documento continua derivado só da versão; o conteúdo e a impressão digital não mudam; documento guardado não é regerado (FR-1195, FR-1196). O FR-1191 é a demonstração, por teste, de que nada se perde no caminho versão → documento. | ✅ |
| **III. Segurança e auditoria** | Nenhuma permissão, rota, ator ou registro novo. | ✅ (não se aplica) |
| **IV. Regras explícitas** | A regra de identidade é escrita (FR-1187) e única (D-002); não há configuração nem decisão manual. | ✅ |
| **V. Rastreabilidade e simplicidade** | Emenda declarada aos FR-016 e FR-021 da `008`, anotada lá; uma função alterada e um auxiliar puro; nenhuma entidade, serviço ou abstração nova. Testes de regressão para cada FR e caso-limite. | ✅ |
| **VI. Jornada e valor demonstrável** | O pedido nasceu de uma elaboradora com um Edital real; o quickstart mostra o resultado na prévia. | ✅ |

**Reavaliação depois do desenho (Phase 1)**: sem mudança. O desenho não introduziu persistência,
contrato de API nem caminho paralelo de composição.

## Componentes afetados

| Componente | O que muda |
|---|---|
| `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` | Um auxiliar puro que agrupa os Perfis pela chave de D-002; em `_perfis`, a remissão no lugar do bloco de atribuições do Perfil agrupado (D-004) e as subseções comuns depois do último Perfil (D-005). |
| `backend/tests/unit/publicacoes/test_atribuicoes_consolidadas.py` | **Novo.** A regra de identidade, a forma do documento, a numeração, a paginação e a integridade (D-006). |
| `backend/tests/contract/test_documento_publicado.py` | O teste de prévia × publicado ganha um cenário com subseção comum; a fixture byte a byte **não** é regerada. |
| `backend/tests/integration/publicacoes/test_retificacoes.py` | Um teste de ponta a ponta da Retificação (D-007). |
| `specs/064-atribuicoes-consolidadas/rastreabilidade.md` | **Novo**, ao fim: uma linha por FR, por SC e por caso-limite. |

**Preservados, e conferidos por teste que já existe ou por teste novo**: `PerfilVaga` e as
migrations; `edital_snapshot` e o conteúdo canônico; `numeracao()` e as telas que a leem;
`_Numerador`; o portal e a Revisão; `publish_edital`, `retificacoes` e `DocumentoPublicado`; a
fixture `documento_publicado_v1.pdf`.

## Testes existentes expostos à mudança

Medido em 08/10/2026 com um plugin descartável que registra cada documento composto com dois ou mais
Perfis de texto igual, sobre `tests/unit/publicacoes` e `tests/contract` (932 casos):

- **52 casos** compõem esse documento. Quase todos compõem de passagem e afirmam outra coisa —
  recusas de borda, mutabilidade, endereçamento, documentos exigidos — e não leem as atribuições.
- **Um** mede o bloco do Perfil: `test_a_medicao_de_um_bloco_atravessa_os_quadros_que_ele_contem`,
  com dois Perfis de mesmo texto. A remissão encurta o bloco, e o que ele afirma — nenhum Perfil
  partido entre páginas — deve continuar valendo. Se falhar, a correção é dar ao segundo Perfil um
  texto próprio, para que o cenário volte a medir o que media, e **nunca** afrouxar a asserção.
- `test_a_previa_se_identifica_em_todas_as_paginas` tem 25 Perfis iguais; afirma pelo menos três
  páginas e a marca em todas, o que a consolidação não deve tornar falso.
- `tests/integration` e `tests/interface` não foram medidos — exigem PostgreSQL. A suíte completa
  na implementação é a medida; `test_quadro_na_publicacao.py` também clona Perfil e é o candidato a
  conferir primeiro.

## Compatibilidade com a `063`

A `063` (PR #263, aberto) não toca o renderizador nem os testes de PDF; o único arquivo em comum é a
tabela de incrementos do `README.md`, onde as duas acrescentam uma linha no mesmo ponto — conflito
de texto, resolvido pondo a `064` depois da `063`. A faixa desta feature (`FR-1186` em diante,
`SC-457` em diante) começa logo depois da dela, e as duas não se sobrepõem. **Depois do merge da
`063`**: atualizar a branch, resolver a linha do README e rodar `test_citacoes_de_requisito.py` e
`test_readme_acompanha_o_codigo.py`.

## Project Structure

### Documentation (this feature)

```text
specs/064-atribuicoes-consolidadas/
├── spec.md
├── plan.md               # este arquivo
├── research.md           # D-001 a D-007
├── data-model.md         # nenhuma entidade; o grupo transitório
├── contracts/
│   └── documento.md      # as frases que o documento imprime
├── quickstart.md
├── checklists/
│   └── requirements.md
└── tasks.md              # /speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── processo_seletivo/publicacoes/infrastructure/
│   └── pdf.py                                   # alterado: _perfis + auxiliar de agrupamento
└── tests/
    ├── unit/publicacoes/
    │   └── test_atribuicoes_consolidadas.py     # novo
    ├── contract/
    │   └── test_documento_publicado.py          # um cenário a mais em prévia × publicado
    └── integration/publicacoes/
        └── test_retificacoes.py                 # um teste a mais
```

**Structure Decision**: o monólito existente; nenhum diretório novo além do arquivo de teste.

## Complexity Tracking

Nenhuma violação a justificar.
