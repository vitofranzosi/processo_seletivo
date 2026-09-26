# Implementation Plan: Duplicar Perfil

**Branch**: `claude/busy-wing-3e9314` | **Date**: 2026-09-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/043-duplicar-perfil/spec.md`

## Summary

Na etapa Perfis do assistente de composição, cada cartão de Perfil ganha *Duplicar este Perfil*:
quem compõe informa Código e Localidade, e um cartão novo aparece logo abaixo com tudo o que a
origem tinha — Modalidades com Regra, quadro, fatos e marcos —, com identidades novas e referências
internas remapeadas. Nada é gravado até a pessoa gravar a etapa.

A abordagem técnica cabe em três frases. **O remapeamento é o da `023`**, reusado com o mapa
estendido pela identidade das Etapas do Edital (`R-001`). **Os marcos não estão na tela da etapa
Perfis** — são da Classificação —, e por isso viajam num campo oculto em trânsito que a gravação já
aceita para Perfil novo, sem tocar nela (`R-003`). **O fragmento é GET**, como todos os da
composição, e a recusa volta como `200` com `HX-Retarget`, porque o htmx do repositório não troca
4xx (`R-004`). Nenhuma migration, nenhuma dependência, nenhum campo novo no contrato.

## Technical Context

**Language/Version**: Python 3.13 · Django 5.2 · htmx 2.0.4 (já vendorizado) — nenhuma dependência
nova.

**Primary Dependencies**: as do repositório. Nada de JavaScript novo: a CSP da interface proíbe
`unsafe-eval`, e o comportamento cabe em `hx-include`, `hx-swap` e `autofocus`.

**Storage**: PostgreSQL. **Sem migration**: a cópia é um Perfil comum no contrato do rascunho que já
existe, gravado por `replace_draft` como qualquer Perfil acrescentado.

**Testing**: pytest + pytest-django contra PostgreSQL (`make test-pg`, com `DB_NAME=ps_043`), em três
famílias — `tests/unit/editais/`, `tests/interface/`, `tests/authorization/`.

**Target Platform**: a interface administrativa sob `/gestao/`.

**Project Type**: monólito Django, projeto único.

**Performance Goals**: o fragmento faz **cinco** consultas além da sessão e do Edital — a origem
gravada, os marcos e os critérios dela (por `prefetch`), as Etapas do Edital e a contagem de
Documentos —, e **nenhuma** que cresça com o número de Perfis do Edital. *A primeira redação dizia
"no máximo três"; a medida da implementação deu cinco, e o número que importa é não crescer* — provado por contagem igual entre
Editais de 2 e de 16 Perfis (`T033`). A medida de produto é a de `SC-230`/
`SC-231`: interações, não milissegundos.

**Constraints**: duplicar não grava (`FR-638`); a origem não muda (`FR-646`); nenhum `hx-vals='js:…'`
(CSP); os campos do diálogo fora do formulário da etapa (`R-007`); o vocabulário das mensagens
passa pela varredura de composição.

**Scale/Scope**: um módulo de domínio novo (`duplicacao.py`, função pura), uma view de fragmento e
uma rota, um ramo novo em `forms.ler_perfis` e em `views._reexibir_perfis`, e um bloco novo em
`_perfil.html`. O Edital-alvo é o de 16 Perfis; o de 66 é projeção.

## Constitution Check

*GATE: verificado antes da Fase 0 e reavaliado após a Fase 1. Nenhuma violação.*

| Princípio | Como esta feature o atende | Verificado por |
|---|---|---|
| **I — Linguagem ubíqua** | *Perfil de Vaga*, *Modalidade*, *marco*, *Documento Exigido* — os termos do domínio. A cópia é um Perfil, e não um conceito novo: nenhuma entidade, nenhum estado | `test_vocabulario_da_composicao.py` sobre as três frases do contrato |
| **II — Integridade normativa** | Conteúdo normativo continua **por Perfil** (Cotas definidas por Perfil). Identidades novas para tudo o que é do Perfil, referências externas intocadas, campos sem tela excluídos (`FR-640` a `FR-643`). Nada publicado é alcançado (`FR-649`) | `tests/unit/editais/test_duplicacao.py` · `SC-232` · `SC-233` |
| **III — Segurança** | Negar por padrão: `edital` obrigatório, escopo por `_edital_do_fragmento` (404), `pode_compor` (403); origem gravada lida **dentro** do Edital (`R-006`). Nenhum dado pessoal. Sem auditoria própria: duplicar não grava, e a gravação da etapa já é auditada (`D-006`) | `tests/authorization/test_duplicar_perfil.py` |
| **IV — Regras explícitas e consistência** | Toda regra continua no domínio: a cópia atravessa **as mesmas** validações de gravação, Revisão e publicação (`FR-647`). A colisão de Código conferida no diálogo é conveniência; a autoridade continua em `validate_profiles`. Concorrência: nenhum risco novo — duplicar não grava (`G-004`) | teste de gravação com Código repetido forjado no formulário |
| **V — Qualidade e simplicidade** | Reusa `remapear` em vez de uma segunda travessia (`R-001`); sem migration, sem campo novo, sem JavaScript. O único transporte novo — o campo em trânsito — é o menor que cumpre `FR-636`/`FR-638` (`R-003`) | teste de completude contra o contrato (`FR-639`) · teste de travessia |
| **VI — Jornada e valor** | *Compor um Edital multipolo sem redigitar cada Perfil* — observável pela interface administrativa, publicado de ponta a ponta sem shell (`SC-235`), e medido contra o baseline do estudo (`SC-230`, `SC-231`) | [quickstart.md](./quickstart.md) §3 e §4 |

**Reavaliação pós-Fase 1.** O desenho acrescentou duas coisas que o gate precisa ver:
1. **Um quinto ponto de travessia dos marcos** (`R-003`). A `025` registrou os quatro anteriores
   porque cada um que falta apaga dado em silêncio. Este é coberto pelo teste de travessia **e** pelo
   de reexibição na recusa — é na recusa que ele se perderia sem aviso.
2. **Resposta `200` para recusa** (`R-004`). Não é afrouxar a semântica HTTP de uma API: é o
   contrato de um fragmento de tela, e `404`/`403` continuam sendo status de verdade.

Nenhuma das duas é violação.

## Project Structure

### Documentation (this feature)

```text
specs/043-duplicar-perfil/
├── spec.md
├── plan.md                        # este arquivo
├── research.md                    # R-001 a R-011
├── data-model.md                  # a transformação origem → cópia, campo a campo
├── quickstart.md                  # validação, demonstração e medição
├── contracts/
│   └── duplicar-perfil.md         # o fragmento: pedido, respostas, cartão devolvido
├── checklists/
│   └── requirements.md
└── tasks.md                       # $speckit-tasks — não criado aqui
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/domain/
│   ├── duplicacao.py              # NOVO — duplicar_perfil(): pura; reusa reaproveitamento
│   ├── reaproveitamento.py        # reusado, não alterado
│   ├── perfis.py                  # reusado: identidade_da_linha_geral
│   └── marcos.py                  # reusado: identidade_derivada
└── interface/
    ├── urls.py                    # + fragmentos/perfil/<indice>/duplicar
    ├── views.py                   # + fragmento_perfil_duplicado; _reexibir_perfis devolve o trânsito
    ├── forms.py                   # ler_perfis lê perfil-<i>-marcosEmTransito
    └── templates/interface/
        ├── _perfil.html           # + diálogo "Duplicar este Perfil"; + campo em trânsito; + status
        └── _duplicar_perfil.html  # NOVO — o diálogo, reexibível sozinho na recusa

backend/tests/
├── unit/editais/test_duplicacao.py
├── interface/test_duplicar_perfil.py
└── authorization/test_duplicar_perfil.py
```

**Structure Decision**: o projeto único do repositório. A transformação é **domínio**, pura, ao
lado de `reaproveitamento.py` — que é a operação irmã —, e não na interface: é ela que carrega o
risco de errar em silêncio, e o lugar de prová-la é o teste unitário sem banco. A interface só lê o
formulário, chama o domínio e desenha.

## Ordem de construção

Não é a lista de tarefas — essa sai do `$speckit-tasks`. É a dependência que a lista precisa
respeitar:

1. **`duplicar_perfil`** com os testes de [data-model.md](./data-model.md), antes de qualquer tela.
   É onde mora o risco silencioso; tudo o mais é transporte.
2. **O campo em trânsito** — `ler_perfis`, `_reexibir_perfis`, `_perfil.html` — com o teste de
   travessia por gravação **e** por recusa. Sem ele, a cópia grava sem marcos e ninguém percebe.
3. **O fragmento e a autorização**, com o contrato.
4. **O diálogo**, a posição, o foco e os anúncios.
5. **A demonstração e a medição** do [quickstart.md](./quickstart.md).

## Riscos técnicos

| # | Risco | Mitigação |
|---|---|---|
| **T-1** | O campo em trânsito se perde numa das travessias (gravação, recusa, cadeia) | um teste por travessia; o de recusa é o que pega o silêncio |
| **T-2** | Identidade vazia do formulário colapsa duas Regras numa (`R-002`) | atribuição prévia de identidade distinta, com teste de duas Regras sem `ruleId` |
| **T-3** | URL do GET grande demais sob um servidor com limite de linha (`R-004`) | nenhum configurado hoje; troca para POST sem mudar o contrato de resposta |
| **T-4** | Marco escrito à mão confundido com derivado quando o Código da origem mudou na tela | comparação contra o código digitado **e** o gravado (`R-005`), com teste do caso |
| **T-5** | O rascunho local não recupera Modalidades, quadro e fatos da cópia (`G-006`) | registrado; limitação anterior, de qualquer Perfil |
| **T-6** | `_duplicar_perfil.html` escapa da varredura de vocabulário, que tem **lista literal** de templates, e não `glob` | acrescentá-lo à lista de `test_vocabulario_da_composicao.py` no mesmo commit do template |

## Complexity Tracking

Nenhuma violação a justificar.
