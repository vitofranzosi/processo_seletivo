# Implementation Plan: Acompanhamento pela situação do candidato

**Branch**: `claude/063-acompanhamento-pela-situacao` | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/063-acompanhamento-pela-situacao/spec.md`

## Summary

Pôr no topo do acompanhamento um bloco **Situação → Por quê → O que fazer**, calculado por uma
função pura nova (`portal/situacao.py`) a partir do que a view já lê: convocação vigente e desfecho,
estado do prazo, chamado do Requerimento, Resultados de Etapa visíveis, situações divulgadas por
lista, objetos recorríveis e o Perfil no conteúdo vigente ([D-001](research.md)). A precedência é
fechada e tem sete degraus ([D-002](research.md)). O corte e a apuração de ocupação não entram, por
decisão do usuário (Clarifications). Abaixo do topo, o bloco "Resultado divulgado" vira
"Classificação por lista", com um cartão por lista e por marco, intitulado pelo nome da lista
([D-006](research.md), [D-009](research.md)). As frases de consequência, canal e cadastro reserva são
constantes do módulo, e o template não escreve nenhuma ([D-005](research.md)).

Nenhuma migration, nenhum ato novo, nenhuma consulta nova ([D-007](research.md)).

## Technical Context

**Language/Version**: Python 3.12, Django 5 (templates server-rendered); CSS à mão na folha do
portal

**Primary Dependencies**: nenhuma nova

**Storage**: N/A — nenhuma migration, nenhum modelo; leitura do que já é lido

**Testing**: pytest (`make test-pg`). Novos: `tests/unit/portal/test_situacao_da_inscricao.py`
(matriz pura de estados, sem banco) e `tests/portal/test_acompanhamento_pela_situacao.py` (cenários
com banco, ordem na página, vocabulário renderizado, contagem de consultas). Adaptados
([D-012](research.md)): `tests/portal/test_acompanhamento_resultado.py`,
`tests/interface/test_portal_caminho_da_convocacao.py` e o que mais ler as frases antigas. Listas
literais acrescidas ([D-010](research.md)): `tests/test_vocabulario_da_convocacao.py`,
`tests/test_vocabulario_do_requerimento.py`. Guardas que já existem: `test_acessibilidade_do_portal.py`,
`test_citacoes_de_requisito.py`, `test_orcamento_de_consulta.py`

**Target Platform**: navegador atual; 1280 × 900 e 375 px

**Project Type**: monólito web Django — portal do candidato (área autenticada)

**Performance Goals**: consultas do acompanhamento constantes no número de listas e marcos (SC-454)

**Constraints**: nenhuma afirmação sem ato (FR-1169); frases de consequência só das constantes
(FR-1177); 375 px sem rolagem horizontal (UX-157); zero consulta ao requerimento sem convocação
(decisão 006 da `059`)

**Scale/Scope**: um módulo novo (`portal/situacao.py`), a view `acompanhamento`, dois templates
(`acompanhamento.html`, `_convocacao_da_inscricao.html`), uma frase em `convocacao.html`, duas chaves
em `situacoes_do_candidato`, a folha do portal

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como a feature o respeita | Situação |
|---|---|---|
| I. Linguagem ubíqua | Os rótulos são os nomes dos atos (convocação, desfecho, resultado preliminar/definitivo); "Cadastro Reserva" só como atributo do Perfil, que é como o domínio o conhece; "lista de espera" não entra porque o domínio não a tem (L-5). A tela não cria estado de domínio: a situação é projeção, sem persistência. | ✓ |
| II. Imutabilidade e temporalidade | Nenhum ato muda. A posição de cada lista é a oficial e não é reordenada. O canal e o cadastro reserva vêm do vigente, como o Cronograma da mesma tela (D-004). Um `agora` para a leitura inteira. | ✓ |
| III. Segurança e privacidade | Mesma titularidade e resposta privada. Nada de terceiro: nenhuma posição alheia, nenhum "último convocado". O corte, ato interno, não chega à pessoa (FR-1171). | ✓ |
| IV. Regras explícitas | Precedência fechada e tabelada (data-model §1.1); a tela não infere — a FR-1169 e a ausência de corte e apuração entre as entradas da função são a prova estrutural. | ✓ |
| V. Rastreabilidade e simplicidade | Uma função pura, sem camada nova; matriz de estados testada sem banco; varreduras de vocabulário estendidas; regressões da `059` e da `017` reescritas sem afrouxar (D-012). | ✓ |
| VI. Jornada demonstrável | Os cinco casos pelo portal, com o candidato de cada um, e o desfecho registrado pela gestão no canal dela (quickstart §3). | ✓ |

Sem violação; *Complexity Tracking* vazio.

**Re-check depois do desenho:** o contrato e o data-model não acrescentam leitura, persistência nem
afirmação além do que a tabela da spec ("O que o domínio já fornece") lista. ✓

## Project Structure

### Documentation (this feature)

```text
specs/063-acompanhamento-pela-situacao/
├── spec.md
├── plan.md
├── research.md          # D-001 a D-013
├── data-model.md        # Situacao, CartaoDeLista
├── quickstart.md
├── contracts/
│   └── bloco-de-situacao.md
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── portal/
│   ├── situacao.py                         # novo — D-001, D-002, D-005
│   ├── views.py                            # acompanhamento: monta e passa a situação
│   ├── static/portal/…                     # a folha: .situacao, .cartao-de-lista
│   └── templates/portal/
│       ├── acompanhamento.html             # topo + cartões por lista (D-009)
│       ├── _convocacao_da_inscricao.html   # só os dados da convocação (D-008)
│       └── convocacao.html                 # a frase neutra (D-011)
└── divulgacao/application/selectors.py     # situacoes_do_candidato: lista e lista_id (D-006)

backend/tests/
├── unit/portal/test_situacao_da_inscricao.py        # novo
├── portal/test_acompanhamento_pela_situacao.py      # novo
├── portal/test_acompanhamento_resultado.py          # adaptado
├── interface/test_portal_caminho_da_convocacao.py   # adaptado
├── test_vocabulario_da_convocacao.py                # lista literal acrescida
└── test_vocabulario_do_requerimento.py              # lista literal acrescida
```

**Structure Decision**: monólito existente; o módulo novo fica em `portal/`, onde os cinco contextos
que a situação lê já se encontram (D-001).

## Complexity Tracking

Nenhuma violação a justificar.
