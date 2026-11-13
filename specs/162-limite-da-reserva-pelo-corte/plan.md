# Implementation Plan: O limite do cadastro de reserva lido do corte

**Branch**: `claude/reserve-limit-enforcement-a5f079` | **Date**: 2026-11-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/162-limite-da-reserva-pelo-corte/spec.md`

## Summary

Um módulo puro novo em `editais/domain` deriva, do corte do marco que convoca, o número do cadastro
de reserva limitado em cada lista de concorrência, e diz se o Perfil é legado (publicou número
digitado). Todos os lugares que hoje leem `reserveLimit` passam a ler esse valor: o documento, o
portal, a Revisão, o relatório, a visão institucional, a tabela da etapa, o assistente e a
Retificação. A publicação ganha cinco recusas de coerência, recortadas pelo ato; nenhum caminho grava
mais o número; e o Perfil legado ganha uma nota na ocupação e na convocação. O documento do Perfil só
de reserva troca a abertura da unidade do corte, e a frase dos suplentes passa a depender do Perfil.
Nenhum motor muda, e nenhuma tabela.

As decisões técnicas estão em [research.md](research.md) (`T-001` a `T-013`); o modelo, em
[data-model.md](data-model.md); as frases, em [contracts/](contracts/); o roteiro, em
[quickstart.md](quickstart.md).

## Technical Context

**Language/Version**: Python 3.13 (o do `pyproject.toml`), Django 5.2; JavaScript sem build para a
Etapa Perfis

**Primary Dependencies**: as do projeto; nenhuma nova

**Storage**: PostgreSQL — nenhuma tabela nem coluna; uma migration, `editais/0028`, que afrouxa a
metade limitada de `ck_perfil_reserve_limit_compatible` (`data-model.md`). *Revisto na
implementação*: a constraint da `0001` exigia número em todo limitado, e a primeira medição o acusou
em 358 casos.

**Testing**: pytest contra PostgreSQL (`make test-pg`), com unidade para a derivação e as frases,
integração para a publicação, a Retificação e o legado, interface para as telas, e `node --test` para
`perfis.js` e `validacao.js`

**Target Platform**: o monólito Django — gestão em `/gestao/`, portal, documento PDF

**Project Type**: aplicação web, backend com templates

**Performance Goals**: a derivação é pura e lê só o Perfil já carregado; nenhuma consulta nova nas
telas que a usam (os orçamentos de consulta existentes continuam valendo)

**Constraints**: CSP sem inline (`091`/`092`) — a linha de ajuda e a nota usam classes que já têm
regra na folha; o vocabulário do documento nas recusas (UX-726); a seta `convocacao → ocupacao`;
`domain` não importa `interface`

**Scale/Scope**: oito leitores do número, cinco achados novos, uma nota, quatro funções do documento

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o plano o atende | Situação |
|---|---|---|
| **I. Linguagem ubíqua** | "Cadastro de reserva", "corte", "continuação", "marco que convoca" — os termos do documento e da `133`; as recusas falam assim (UX-726) | ✅ |
| **II. Imutabilidade e temporalidade** | É o princípio que motiva a feature: uma fonte só para o número (`D-001`). Nada publicado muda: o legado continua dizendo o que disse (FR-6944), e é marcado pelo próprio conteúdo, e não por data (T-002) | ✅ |
| **III. Segurança e auditoria** | Nenhuma permissão nova; as telas que mudam são as de quem já as acessa; nenhum dado pessoal | ✅ |
| **IV. Regras explícitas e concorrência** | As recusas moram no domínio (`validate_for_publication`), com código, frase e caminho; recortadas pelo ato, como a `027` registrou (T-004); nada de concorrência nova | ✅ |
| **V. Rastreabilidade e simplicidade** | Um módulo, um valor, nenhuma tabela; os motores intocados (T-013); a matriz `rastreabilidade.md` liga cada FR e cada caso-limite a teste | ✅ |
| **VI. Jornada demonstrável** | A demonstração muda junto (T-012) e passa a ser o exemplo do SC-2302 (`quickstart.md`) | ✅ |

Re-check depois do desenho: sem violação. A **FR-6943** foi refinada ao planejar: o Perfil só de
reserva cujo corte governa uma Etapa perderia, com a letra anterior, a frase que diz quem participa
dela; a spec agora proíbe só a **abertura** "Seguem no processo"/"Passam para" e pede a menção à Etapa.

## Project Structure

### Documentation (this feature)

```text
specs/162-limite-da-reserva-pelo-corte/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── documento.md      # C1–C4: as frases do documento
│   └── telas.md          # recusas, gravação, Etapa Perfis, gestão, portal, assistente, nota, Retificação
├── checklists/requirements.md
├── rastreabilidade.md    # escrito na implementação
└── tasks.md              # $speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/domain/
│   ├── cadastro_de_reserva.py      # NOVO: Cadastro, do_perfil, descricao_curta, incoerencias
│   ├── perfis.py                   # validate_profile recusa número em LIMITED (T-003)
│   ├── validation.py               # os cinco achados; _alcance_da_faixa lê o Cadastro
│   ├── duplicacao.py               # a cópia não leva o número
│   └── reaproveitamento.py         # idem
├── editais/application/draft.py    # a advertência da FR-6940, pelas linhas do rascunho; chamada por _pendencias
├── publicacoes/
│   ├── application/publish_edital.py   # edital_snapshot: reserveLimit None em LIMITED
│   └── infrastructure/
│       ├── pdf.py                  # frase_do_cadastro, _reserva, frases_do_corte, C4
│       └── apresentacao.py         # passa o Cadastro a frases_do_corte
├── portal/
│   ├── views.py                    # _oferta
│   └── situacao.py                 # frase_da_reserva
├── duvidas/domain/
│   ├── respostas.py                # o cartão do cadastro
│   └── cobertura.py                # o caminho do cutRule
├── ocupacao/application/selectors.py   # nota_do_cadastro_legado
├── interface/
│   ├── forms.py                    # deixa de ler o número
│   ├── revisao.py                  # a linha do cadastro; passa o Cadastro ao corte
│   ├── relatorio_do_edital.py      # _reserva
│   ├── visao_geral.py              # Reserva.do_perfil
│   ├── retificacao.py              # o campo só no legado; NOVO_PERFIL; a linha derivada
│   ├── views.py                    # a nota nas telas da ocupação e da convocação
│   ├── static/interface/perfis.js, validacao.js
│   └── templates/interface/
│       ├── _perfil.html            # sem o campo; a linha de ajuda
│       ├── ocupacao.html           # a nota
│       └── convocacao.html         # a nota
└── processos/management/commands/seed_demo.py   # DOC-INFO sem número; TEC-LAB com continuação

backend/tests/
├── unit/editais/test_cadastro_de_reserva.py              # a derivação, por caso de C1 e da T-006
├── unit/editais/test_coerencia_do_cadastro.py            # os cinco achados e o recorte pelo ato
├── unit/publicacoes/test_cadastro_de_reserva_no_documento.py  # C1–C4 e os exemplos
├── integration/editais/test_cadastro_de_reserva_na_publicacao.py  # rascunho, cópias, snapshot, legado
├── integration/publicacoes/test_cadastro_de_reserva_na_retificacao.py  # (existe) + FR-6948, 6950, 6951
├── interface/test_cadastro_de_reserva.py                 # Etapa Perfis, Revisão, nota, Retificação
├── portal/…                                              # as frases do portal
└── javascript/validacao.test.js, perfis.test.js          # o número deixa de ser exigido
```

**Structure Decision**: o monólito como está. A derivação mora em `editais/domain`, que todos os
leitores já importam (T-001); cada leitor só troca a leitura do campo pela do valor.

## Riscos

| Risco | Sinal | Mitigação |
|---|---|---|
| A regra impeditiva quebra fixtures em bloco | dezenas de falhas `reserve_*` na suíte | rodar primeiro `tests/unit/editais`, `tests/unit/publicacoes` e `tests/integration/editais`; corrigir nas fixtures (T-012), e nunca afrouxar a regra |
| Fixture de conteúdo **publicado** perder o número | o caso do legado deixa de ser testado | o corpus da `070` e `snapshot_publicado.json` ficam como estão (T-012) |
| O agrupamento por Perfil da `068` mudar | testes de consolidação esperando um grupo só | é efeito pedido (T-007); atualizar a expectativa com o motivo no teste |
| Rascunho antigo tratado como legado | a Revisão mostra o número digitado | `edital_snapshot` zera o número em `LIMITED` (T-003), com teste |
| O assistente citar caminho sem cobertura | `test_cobertura` do `duvidas` reprova | acrescentar o caminho do `cutRule` em `cobertura.py` (T-008) |
| Classe nova sem regra na folha | `test_acessibilidade` reprova | usar `nota` e a classe de ajuda que o fieldset já usa |

## Complexity Tracking

Sem violação a justificar.
