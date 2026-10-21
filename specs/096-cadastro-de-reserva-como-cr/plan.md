# Implementation Plan: Cadastro de reserva sem vaga imediata impresso como CR

**Branch**: `claude/cadastro-reserva-zero-cr-45f542` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/096-cadastro-de-reserva-como-cr/spec.md`

## Summary

O Perfil continua guardando `0`, e só a composição muda:

- **Um predicado** de domínio, `cadastro_sem_vaga_imediata`, ao lado do `sem_vaga_imediata` da
  `067`, decide quem é `CR` (`D-005`).
- **Uma função de célula**, `vagas_impressas`, troca o `str(...)` dos quatro pontos que imprimem o
  número: dois na apresentação plana, dois na por perguntas (`D-006`).
- **Uma nota**, parâmetro novo de `_tabela`, sai logo depois da grade de toda tabela que tiver `CR`,
  e depois dos pares na ficha do Perfil único (`D-007`).
- **No portal**, sai a linha "0 vagas imediatas agora", e nada mais muda (`D-010`).
- **Na prévia**, o espaço exato do fecho do ato, para que o corpo normativo pagine igual nos dois
  modos (D-012, decisão do usuário na implementação; `D-013`). A nota acordou um defeito da `069` no
  cenário B: a última seção saltava com o fecho só no publicado.

Nada de modelo, campo, migration ou esquema. Os documentos publicados não mudam. Os bytes esperados do
cenário B passam a ser os da `096`, com um guardião que prova que a única diferença é `0` → `CR` mais
as notas. O cenário A e a fixture de contrato continuam byte a byte (`D-009`).

## Technical Context

**Language/Version**: Python 3.13, Django 5.2

**Primary Dependencies**: nenhuma nova.

**Storage**: nenhuma mudança: nenhum modelo, campo, migration ou versão de esquema (`FR-2400`).

**Testing**: pytest contra PostgreSQL (`make test-pg` com `DB_NAME` próprio):
- unidade do predicado e da célula;
- unidade do compositor nas duas apresentações e nas duas redações;
- os guardiões de bytes do cenário B, repontados para a `096`;
- o guardião novo de diferença de texto contra a `069`;
- integração do portal e da Retificação;
- a fixture de contrato, inalterada.

**Target Platform**: o monólito Django: o compositor do PDF e o portal (`/selecoes/`).

**Project Type**: aplicação web (monólito).

**Performance Goals**: nenhuma consulta nova. O predicado é função do snapshot, que o compositor já
tem em mãos.

**Constraints**:
- o documento só muda nos Perfis de cadastro de reserva sem vaga imediata (`SC-901`);
- a numeração de tabelas e a conferência de remissões da `065` não mudam (`FR-2410`);
- a gestão continua com o número (`FR-2417`).

**Scale/Scope**: o maior Edital medido, o cenário B, tem 18 Perfis, 16 deles em `CR`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como a feature o cumpre | Situação |
|---|---|---|
| I. Linguagem ubíqua | "vaga imediata" e "cadastro de reserva" no sentido de hoje; `CR` é a sigla que a equipe já usa, e sai explicada em toda tabela que a usa (D-002) | ✅ |
| II. Integridade normativa, imutabilidade | o dado não muda, e tem uma fonte só (D-001); documento publicado não se recompõe (`FR-2413`); o consolidado de Retificação é documento novo (`FR-2411`); o quadro de alterações registra o campo como ele é (D-003) | ✅ |
| III. Segurança e auditoria | nenhuma permissão, rota ou dado novo | ✅ |
| IV. Regras explícitas | um predicado de domínio, lido pelas quatro composições (D-005, D-006); nenhuma regra muda de comportamento (`FR-2401`) | ✅ |
| V. Qualidade, rastreabilidade, simplicidade | um predicado, uma função, um parâmetro, nenhuma dependência; a diferença de texto presa por teste contra a evidência da `069` (D-009); casos-limite com teste na matriz | ✅ |
| VI. Jornada demonstrável | o cenário B pelo fluxo real, antes e depois, com o portal ([quickstart.md](quickstart.md)) | ✅ |

**Re-check depois do desenho (Fase 1):** sem violação. A revisão de um trecho da `FR-136` da `024`
(`FR-2414`) é decisão do usuário, registrada em D-004. O teste que prendia o trecho muda no mesmo
commit, citando a `FR-2414` (D-010).

## Project Structure

### Documentation (this feature)

```text
specs/096-cadastro-de-reserva-como-cr/
├── spec.md
├── plan.md
├── research.md            # D-005 a D-011, e o mapa de onde o 0 sai
├── data-model.md          # nada muda; a tabela-verdade do predicado
├── quickstart.md
├── contracts/
│   └── celula-de-vagas-e-nota.md
├── checklists/requirements.md
├── demonstracao/          # os PDFs do cenário B depois da feature (na implementação)
├── rastreabilidade.md     # na implementação
└── tasks.md               # $speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/domain/
│   └── quadro.py                     # cadastro_sem_vaga_imediata (D-005)
├── publicacoes/infrastructure/
│   ├── pdf.py                        # SIGLA_DO_CADASTRO, NOTA_DO_CADASTRO, vagas_impressas,
│   │                                 # nota_da_sigla; _tabela(nota=); _quadro_de_perfis; _perfil_unico;
│   │                                 # render_edital_pdf(fechos_previstos=), _reservar_o_fecho (D-013)
│   └── apresentacao.py               # _vagas_em_partes: avulsos e grupos
├── publicacoes/application/
│   └── contexto_do_ato.py            # fechos_previstos(unidade, data) (D-013)
├── interface/
│   └── views.py                      # previa_documento passa as autoridades previstas
└── portal/templates/portal/
    └── selecao.html                  # a linha "N vagas imediatas agora" sai do ramo da oferta

backend/tests/
├── unit/editais/test_cadastro_sem_vaga_imediata.py           # NOVO — o predicado, a tabela-verdade
├── unit/publicacoes/test_cadastro_de_reserva_como_cr.py       # NOVO — célula, nota e total nas duas
│                                                              #   apresentações e redações; Perfil único
├── unit/publicacoes/test_documento_da_auditoria_depois_da_096.py  # NOVO — 069 → 096: só 0 → CR e notas
├── unit/publicacoes/test_previa_reserva_o_fecho.py           # NOVO — a regressão do B (SC-904)
├── contract/test_documento_publicado.py                       # a prévia com a autoridade prevista
├── unit/publicacoes/test_itens_do_documento.py               # ESPERADOS do B → specs/096-…/demonstracao/
├── unit/publicacoes/test_documento_da_auditoria_depois_da_069.py  # o B passa a ler os bytes da 096
├── integration/portal/test_detalhe_selecao.py                # o teste da FR-136 muda (D-010)
├── integration/publicacoes/                                   # NOVO ou acréscimo — Retificação 0 ↔ N
└── contract/fixtures/                                          # inalterados — SC-901
```

**Structure Decision**: monólito existente. Um predicado no domínio, uma função e um parâmetro no
compositor, um trecho de template no portal. Nenhum app, modelo, rota ou migration.

## Fases de implementação (para o `$speckit-tasks`)

1. **Ponto de partida**: medir a suíte das áreas tocadas e confirmar que o cenário A e a fixture de
   contrato não têm Perfil `CR`. Se tiverem, `SC-901` precisa ser revisto antes de seguir.
2. **Predicado** (`D-005`), com a tabela-verdade da [data-model.md](data-model.md).
3. **US1 e US2, apresentação plana**: `vagas_impressas`, `nota_da_sigla`, `_tabela(nota=)`,
   `_quadro_de_perfis`, `_perfil_unico`.
4. **US3, apresentação por perguntas**: os dois pontos de `_vagas_em_partes`.
5. **Bytes**: gravar os PDFs do B em `specs/096-…/demonstracao/`, repontar os dois guardiões e
   escrever o de diferença de texto contra a `069` (`D-009`).
6. **US4, portal**: o template, e o teste da `FR-136` revisto (`D-010`).
7. **US5, Retificação**: consolidado 0 → N e N → 0; a tela de homologação com os números.
8. **Fechamento**: o cenário B pelo fluxo real, com o portal; `rastreabilidade.md`; o README;
   `make lint check test-pg`.

## Riscos

| Risco | Mitigação |
|---|---|
| Um quinto ponto que imprime o número, não mapeado | o guardião de diferença de texto do B acusa qualquer `0` remanescente em Perfil de tutor presencial (`SC-900`) |
| Mudança acidental fora dos Perfis `CR` | o cenário A e a fixture de contrato byte a byte (`SC-901`); a diferença de texto do B presa por teste |
| A nota separada da tabela por quebra de página | aceito: o paginador não leva a grade com a linha seguinte, de propósito (`prender_a_ultima_linha`); a nota abre a página logo abaixo da tabela, como a frase de reversão (`D-007`, corrigido na implementação) |
| A nota contada como item, e a numeração deslocada | ela não abre tabela (`D-008`); o guardião de itens compõe de verdade |
| O teste da `FR-136` reprovando sem explicação | ele muda no mesmo commit, citando a `FR-2414` |
| `bool` lido como `0` | o predicado recusa `bool`, como o da `067`; caso na tabela-verdade |
| Suítes paralelas disputam o banco de teste | `DB_NAME` próprio da worktree |
| A prévia paginando diferente do publicado no fim (achado na implementação) | a prévia reserva o fecho real (D-012, `D-013`); regressão do B em três composições e três autoridades (`SC-904`) |
| Várias autoridades vigentes de alturas diferentes | reserva a mais alta (`FR-2420`); limite registrado na spec |

## Complexity Tracking

Sem violações a justificar.
