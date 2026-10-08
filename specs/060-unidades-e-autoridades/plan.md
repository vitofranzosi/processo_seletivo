# Implementation Plan: Unidades institucionais e autoridades de publicação

**Branch**: `claude/edital-signature-responsible-60ecf3` | **Date**: 2026-10-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/060-unidades-e-autoridades/spec.md`

## Summary

Quatro frentes, numa ordem que mantém a suíte verde a cada passo:

1. **O registro** — um app novo, `unidades`, com `Unidade` (declarada em `unidades.json` e aplicada
   por `sincronizar_unidades`, com trilha) e `AutoridadeHabilitada` (cadastrada pelo Gestor da
   unidade, nunca excluída, imutável depois do primeiro uso). Gatilhos recusam exclusão e reescrita
   ([research](research.md) R-001 a R-006).
2. **O documento** — `ORGAO` e `LOCAL` saem de `pdf.py`; o compositor do Edital recebe a Unidade como
   contexto do ato, o do Resultado a lê do conteúdo congelado, e o comprovante a lê da Publicação que
   originou a versão aceita. Para o Cefor, os bytes não mudam (R-008).
3. **A publicação** — os três comandos recebem o identificador da autoridade e a conferem no domínio,
   sob trava: unidade do Edital, vigência na data do ato. A Publicação congela a Unidade e a
   autoridade; a de Resultado passa a congelar o ato de nomeação (R-005, R-007).
4. **A tela** — `/gestao/autoridades`, para cadastrar, corrigir e encerrar; as telas de publicação
   oferecem só as vigentes da unidade. O catálogo em código e o teste que proibia o modelo saem
   (R-009, R-010, R-012).

## Technical Context

**Language/Version**: Python 3.12, Django 5 — o monólito existente; templates do servidor, sem build
de JavaScript.

**Primary Dependencies**: nenhuma nova.

**Storage**: PostgreSQL. Migrations: `unidades/0001` (as duas tabelas), `unidades/0002` (os cinco
gatilhos, `RunPython` com reverso, no-op fora do PostgreSQL), `publicacoes/0010` (cinco colunas de
unidade) e `divulgacao/0004` (cinco colunas de unidade e o ato de nomeação). `ADD COLUMN` com padrão
constante nas tabelas append-only não dispara gatilho de `UPDATE`. Nenhuma tabela nova é append-only;
o `M` do provisionamento continua 34.

**Testing**: pytest contra PostgreSQL (`make lint check test-pg DB_NAME=ps_060`). A fixture de bytes da
`054` é a prova de não regressão do Cefor. Os gatilhos e a trava só são verificáveis no PostgreSQL, e
os testes deles são pulados fora dele.

**Target Platform**: servidor Django; PDF pelo renderizador próprio.

**Project Type**: web — `backend/processo_seletivo/`.

**Performance Goals**: nenhuma meta nova. A escolha da autoridade é uma consulta indexada por unidade;
a publicação ganha uma leitura com trava de uma linha.

**Constraints**: publicação imutável e documento publicado que não se regenera; contexto do ato fora
do conteúdo normativo (`008`, FR-034); guardiões estruturais — contagem de migrations por app
(`publicacoes` 9 → 10, `divulgacao` 3 → 4, com justificativa), `TRIGGERS_POR_APP`, `APPS`, trilha
legível (`OPERACOES`), inventário de negativas da `033`, gramática das portas, citações de requisito,
README que acompanha o código; 2.599 casos transacionais que truncam as tabelas (R-012).

**Scale/Scope**: ~26 Unidades; poucas autoridades vigentes por Unidade; 4 documentos; 3 fluxos de
publicação mais o gesto do marco; ~400 referências de teste à publicação, concentradas em dois
helpers.

## Constitution Check

| Princípio | Como esta feature o cumpre |
|---|---|
| I. Linguagem ubíqua | *Unidade*, *Autoridade habilitada*, *ato de nomeação*, *vigência*. O modelo se chama `AutoridadeHabilitada` porque é habilitação na unidade, e não pessoa nem cargo (`D-003`). |
| II. Imutabilidade e temporalidade | A Publicação continua autocontida: congela Unidade e autoridade, e nenhuma mudança posterior a alcança (FR-1129). Vigência por data, no fuso institucional; a data do ato é o `now` da transação. Documento publicado não se regenera. |
| III. Segurança, dados, auditoria | Negar por padrão: permissão própria (`autoridade:gerir`), escopo da unidade, recusa no domínio e não só na tela, autoridade alheia indistinguível de inexistente. O modelo de autorização continua desacoplado de cargo: a Autoridade Signatária é escolhida, não inferida do papel. Mínimo de dado pessoal: cargo, nome e ato de nomeação, já exigidos pela Constituição. Toda mudança de Unidade e de Autoridade gera evento com antes e depois. |
| IV. Regras explícitas | A regra de vigência e de unidade é uma função do domínio, chamada pelos três comandos sob trava (R-005). Nada se exclui — o banco recusa (R-006). Situação da autoridade derivada da vigência, sem flag paralela. |
| V. Simplicidade | Duas tabelas, um comando, uma tela. Sem pessoa, mandato, delegação, hierarquia nem papel novo (`D-003`, `D-005`). O escopo existente não é reinventado (`D-001`). |
| VI. Jornada | Demonstrável pelo quickstart: duas unidades, dois documentos, troca de autoridade sem mudar o código. |

**Gate: passa.** Três requisitos de specs anteriores são revogados ou emendados por esta spec, que os
nomeia (`007` FR-039, `054` FR-989, `017` FR-029), com nota no próprio texto (R-015).

**Re-check depois do desenho**: passa. O único ponto que poderia pedir justificativa — proteger a
exclusão só por gatilho, sem a segunda camada de privilégio — está decidido em R-006, com a
alternativa registrada.

## Ordem de implementação

A suíte tem de ficar verde ao fim de cada passo; por isso o registro e a fixture vêm antes de
qualquer regra que os exija.

1. **App `unidades`, modelos, gatilhos, `unidades.json` e `sincronizar_unidades`** — sem consumidor
   ainda. Guardiões: `APPS`, `TRIGGERS_POR_APP`, README, `INSTALLED_APPS`.
2. **A fixture `autouse` da suíte** (R-012) e `tests/fixtures/autoridades.py` — antes de qualquer
   regra que leia a Unidade.
3. **O compositor com a Unidade** (R-008) — Edital, prévia, Resultado, comprovante. A fixture de bytes
   passa sem ser refeita; as chamadas diretas nos testes passam `UNIDADE_DA_SUITE`.
4. **Os comandos de publicação e as colunas congeladas** (R-005, R-007, R-014) — migrations de
   `publicacoes` e `divulgacao`; os helpers dos testes passam a mandar o identificador.
5. **A criação exige Unidade ativa** (R-011).
6. **A tela das autoridades e as telas de publicação** (R-009, R-010) — permissão no Gestor,
   inventário de negativas, `OPERACOES`.
7. **O catálogo sai** — `publicacoes/domain/autoridades.py` reduzido a nada; `quem_assinou` em
   `unidades/domain/`; `test_autoridades.py` substituído; `seed_demo` (R-013).
8. **Emendas e pendências** (R-015, R-016) — notas nas specs anteriores, `openapi.yaml`, README.

## Project Structure

### Documentation (this feature)

```text
specs/060-unidades-e-autoridades/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── registro-de-unidades.md
│   ├── autoridades-e-publicacao.md
│   └── documentos.md
├── checklists/requirements.md
└── tasks.md              # /speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/unidades/                 # app novo — R-001
├── models.py                    # Unidade, AutoridadeHabilitada — data-model
├── unidades.json                # o registro declarado — R-003
├── domain/
│   ├── nomes.py                 # GERIR = "autoridade:gerir"; códigos de recusa
│   ├── vigencia.py              # vigente(autoridade, data); situação derivada
│   └── rotulos.py               # quem_assinou (movido), rotulo_da_autoridade — UX-148
├── application/
│   ├── autoridades.py           # cadastrar, corrigir, encerrar; autoridade_para_o_ato — R-005
│   ├── sincronizacao.py         # aplicar o arquivo, com trilha — R-003
│   └── selectors.py             # unidade_ativa, autoridades_vigentes, da_unidade
├── management/commands/sincronizar_unidades.py
└── migrations/0001_initial.py, 0002_nada_se_exclui.py

backend/processo_seletivo/publicacoes/
├── domain/autoridades.py                       # removido — R-012
├── models.py                                   # Publicacao.unidade_* — R-007
├── migrations/0010_unidade_do_ato.py
├── infrastructure/pdf.py                       # INSTITUICAO, UnidadeDoAto; ORGAO e LOCAL saem — R-008
├── application/publish_edital.py               # autoridade_id; congela unidade e autoridade
├── application/retificacoes.py                 # idem
├── application/selectors.py                    # quem_assinou de unidades.domain
└── api/{serializers,public_serializers}.py     # signatory só com authorityId; unit — R-014

backend/processo_seletivo/divulgacao/
├── models.py, migrations/0004_*.py             # unidade_*, signatario_ato_de_nomeacao
├── domain/conteudo.py                          # cabecalho.unidade e ato de nomeação
├── application/publicar.py                     # autoridade por identificador
└── infrastructure/documento.py                 # timbre a partir do conteúdo

backend/processo_seletivo/inscricoes/infrastructure/comprovante_pdf.py   # timbre a partir dos dados
backend/processo_seletivo/portal/{views.py,templates/portal/comprovante.html}  # unidade da Publicação
backend/processo_seletivo/processos/application/commands.py              # unidade ativa — R-011
backend/processo_seletivo/processos/management/commands/seed_demo.py     # R-013

backend/processo_seletivo/interface/
├── identidade.py                # gestor ganha autoridade:gerir — D-005
├── views.py                     # autoridades (tela nova); _executar e as três publicações; OPERACOES
├── conducao_do_marco.py         # conferir_natureza_e_autoridade pelo identificador
├── forms.py                     # ler_autoridade
├── urls.py                      # autoridades
└── templates/interface/
    ├── autoridades.html         # nova
    ├── lista.html               # botão, sob pode_gerir_autoridades
    └── confirmar.html, retificacao_confirmar.html, previa_de_publicacao.html, marco.html, marco_conferir.html

backend/config/settings/base.py  # INSTALLED_APPS
backend/Makefile                 # preparar roda sincronizar_unidades

backend/tests/
├── conftest.py                  # fixture autouse — R-012
├── fixtures/autoridades.py      # AUTORIDADE_DA_SUITE, AUTORIDADE_DO_RESULTADO, UNIDADE_DA_SUITE
├── fixtures/{publicacao,divulgacao}.py         # identificador no lugar do dicionário e da chave
├── unidades/                    # os testes da 060
├── contract/test_documento_publicado.py + fixtures/unidade_publicada.json
├── migrations/test_migrations.py               # APPS, TRIGGERS_POR_APP, contagens
└── interface/test_autoridades.py               # substituído

specs/033-navegacao-por-capacidade/inventario-das-negativas.md   # a tela nova
specs/001-*/contracts/openapi.yaml, specs/007-*/spec.md, specs/017-*/spec.md, specs/054-*/spec.md  # emendas — R-015
README.md                         # módulo unidades
```

**Structure Decision**: o monólito Django existente, com um app novo para o que é da unidade; as telas
continuam em `interface/`, como todas.

## Complexity Tracking

Nenhuma violação da Constituição a justificar. Registro o que poderia parecer excesso e não é:

| Item | Por que é necessário | Alternativa mais simples descartada porque |
|---|---|---|
| App novo `unidades` | quatro apps leem a Unidade e nenhum é dono dela | `publicacoes` inverteria a dependência de `processos`; os guardiões de contagem a tratariam como invasão (R-001) |
| Arquivo + comando para Unidades | trilha de cada mudança (FR-1108) e revisão em diff | data migration não pode gravar auditoria (R-003) |
| Coluna `usada_em` | o banco e o domínio precisam saber, sob trava, se já houve ato | consulta a `Publicacao` faria `unidades` depender de `publicacoes` (R-004) |
