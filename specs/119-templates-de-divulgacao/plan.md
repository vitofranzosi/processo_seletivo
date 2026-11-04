# Implementation Plan: Templates de Divulgação por Família e Formato

**Branch**: `claude/119-templates-de-divulgacao` | **Date**: 2026-11-04 | **Spec**: [spec.md](spec.md)

**Input**: a [spec](spec.md), as decisões do [research](research.md), o
[estudo de 04/11](../../doc/estudo-templates-de-divulgacao-2026-11-04.md) e o código do kit da `111`
na `main` (incrementos A e B) e no PR do incremento C (pacote e galeria).

## Summary

O compositor da peça (`interface/kit_peca.py`) deixa de ter tamanho, fonte e desenho fixos no código
e passa a ler três camadas declarativas: **formato**, **família** e **template** (família × formato).
A peça atual vira a família Institucional, e os SVG de referência dela não mudam — é o primeiro
incremento e a prova da generalização. A ficha ganha a carga horária publicada de cada Perfil e o
canal de atendimento da unidade, com a impressão na versão 2. A tela do kit ganha a escolha de
família, variante e imagem em listas fechadas, e a prévia e a exportação por formato. Cada família
traz os seus ativos versionados com a origem e a licença.

Não há migration, tabela nova, dependência nova nem mudança no fluxo de publicação.

A entrega segue a ordem do estudo (D-001):

1. **Motor generalizado**, sem mudar a peça atual;
2. **Pós Lato Sensu** nos três formatos, com a ficha versão 2 e a escolha na tela;
3. **as demais famílias, uma por PR**: FIC, Libras, UAB/bolsista, Aperfeiçoamento, Internos, TMD.

## Technical Context

| | |
|---|---|
| **Language/Version** | Python 3.13 |
| **Primary Dependencies** | Django 5.2; `resvg-py` (já dependência de execução desde a P-4 da `111`). **Nenhuma nova** |
| **Storage** | PostgreSQL; **nenhuma tabela nova**. Escolhas e template vão no `detalhe` do evento de exportação já existente (D-008) |
| **Testing** | pytest + pytest-django contra PostgreSQL (`make test-pg`); `node --test` para o script da tela |
| **Target Platform** | Gestão web (moldura da `076`); Linux na implantação |
| **Project Type** | Monólito Django (`backend/processo_seletivo`) |
| **Performance Goals** | Tela com três prévias < 2 s; ZIP com três formatos < 3 s; lote de 20 (SC-1137) |
| **Constraints** | CSP `'self'` sem inline; nenhum `import PIL`; só fontes livres; imagens ≤ 400 kB; determinismo byte a byte |
| **Scale/Scope** | 1 + 7 famílias, 3 formatos, 22 templates no máximo; dezenas de exportações por Edital |

## Constitution Check

| Princípio | Como o plano o cumpre |
|---|---|
| **I. Linguagem ubíqua** | "Perfil", "carga horária", "vagas" como a página pública. A família é escolha de quem divulga, não tipo de certame inferido (FR-3409 da `111` continua) |
| **II. Integridade normativa** | A carga horária vem do conteúdo publicado da versão vigente, com proveniência. Nenhuma frase afirma o que a publicação não traz (FR-3814). O contato vem do cadastro da unidade e é dito como tal na conferência (FR-3812) |
| **III. Segurança e auditoria** | Negar por padrão: listas fechadas validadas no servidor (FR-3805); família só da unidade do ato; sem envio de arquivo. Cada exportação registra família, formato, template e imagem (FR-3828) |
| **IV. Regras explícitas** | Formato, família e template são declarações versionadas no código, com testes que as leem; a recaída de título e a omissão do contato são regras escritas |
| **V. Simplicidade e testes** | Sem dependência nem tabela; o motor é o da `111`, generalizado por dados. Testes de geometria, de vocabulário, de determinismo, de referência byte a byte e de origem dos ativos |
| **VI. Jornada completa** | A comunicação escolhe e baixa os três formatos pela tela, sem shell; a galeria é a jornada de aprovação ([quickstart](quickstart.md)) |

**Gates**: nenhuma violação. Pós-desenho: o desenho não acrescentou tabela, dependência nem leitura
fora do publicado além da exceção declarada na FR-3810.

## Project Structure

### Documentation (this feature)

```text
specs/119-templates-de-divulgacao/
├── spec.md
├── plan.md               # este arquivo
├── research.md           # D-001 a D-012
├── data-model.md         # formato, família, template, escolha, ficha v2, evento
├── contracts/kit.md      # o que muda nas rotas e nos formulários do kit
├── quickstart.md         # verificação ponta a ponta e galeria
├── tasks.md
└── checklists/requirements.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── portal/
│   └── ficha.py                     # carga horária, contato, impressão v2 (FR-3809–FR-3812)
└── interface/
    ├── kit_peca.py                  # compositor por template; serialização SVG geral
    ├── kit_formatos.py              # NOVO: post, story, banner (FR-3801)
    ├── kit_familias/                # NOVO: uma declaração por família (D-003)
    │   ├── __init__.py              # registro, lista por unidade, liberação (FR-3805, FR-3808)
    │   ├── institucional.py         # a peça da 111, sem mudança de desenho (FR-3804)
    │   ├── pos_lato_sensu.py        # incremento 2
    │   └── ...                      # uma por PR no incremento 3
    ├── kit_fontes.py                # NOVO: métrica e subconjunto por fonte livre (D-005)
    ├── kit_ativos/
    │   ├── ORIGEM.md                # marcas, como hoje
    │   ├── fontes/                  # subconjuntos OFL + ORIGEM.md
    │   └── <familia>/               # imagens, ilustrações, padrões + ORIGEM.md (FR-3826)
    ├── kit_textos.py                # carga horária e contato nos textos (FR-3813)
    ├── kit_pacote.py                # ZIP com os formatos da família (FR-3829)
    ├── kit_de_divulgacao.py         # escolha, prévia e exportação por formato (FR-3830)
    └── templates/interface/kit_de_divulgacao.html

backend/scripts/galeria_do_kit.py    # todo template × cenário (FR-3831)

backend/tests/
├── unit/kit/                        # geometria, vocabulário, determinismo por template
├── integration/kit/                 # ficha v2, desatualização, exportação
├── authorization/test_kit_de_divulgacao.py   # listas fechadas, envio forjado
└── fixtures/kit_referencias/<familia>/<formato>/   # SVG de referência por template
```

**Structure Decision**: o kit continua em `interface/`, como na `111`. Família é módulo Python e não
arquivo de dados (D-003), para que a declaração seja verificada pelo mesmo `ruff` e pelos mesmos
testes, e para que uma família nova seja um PR legível.

## Increments

| # | Entrega | Depende de | Fecha |
|---|---|---|---|
| **1** | Formato, família, template e fontes como dados; Institucional; referências da `111` idênticas | `main` | US4, FR-3801–FR-3804, FR-3823, FR-3826, FR-3827, SC-1133 |
| **2** | Ficha v2; textos; escolha na tela; registro; Pós Lato Sensu post, story e banner; galeria por template | 1; incremento C da `111` mergeado para FR-3829 e FR-3831 | US1–US3, US5, demais FR, SC-1131, SC-1132, SC-1134, SC-1137–SC-1139 |
| **3a–3f** | FIC, Libras, UAB/bolsista, Aperfeiçoamento, Internos (variantes), TMD — um PR cada | 2; P-1 (imagens); P-2 para Libras, TMD e Internos | Liberação de cada família (SC-1135, humano) |

A liberação em produção é da operação, template a template, depois da aprovação (SC-1135, P-4). O
banner de toda família espera a P-3.

## Complexity Tracking

| Violação | Por que precisa | Alternativa mais simples recusada porque |
|---|---|---|
| Leitura do canal de atendimento do cadastro da unidade, fora do publicado (FR-3810) | T-7 aceita: o contato dos templates é o da unidade | Ler `PORTAL_ATENDIMENTO` daria o canal da instituição, que não é o da unidade; e nenhum dado publicado traz o canal |
