# Implementation Plan: O efeito do desfecho da Etapa por lista

**Branch**: `claude/164-efeito-do-desfecho-por-lista`, sobre `claude/163-alcance-da-etapa` | **Date**:
2026-11-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/164-efeito-do-desfecho-por-lista/spec.md`

## Summary

A Etapa restrita e eliminatória ganha duas colunas: o efeito do desfecho desfavorável e o do não
comparecimento. O valor atravessa o caminho que a `163` abriu: rascunho, degrau 23 do conteúdo
publicado, mutabilidade, Retificação, Revisão e documento.

O Resultado da Etapa ganha a terceira consequência, `RETIRADA_DA_RESERVA`. Um módulo puro novo,
`resultados/domain/efeito.py`, diz qual efeito a Etapa produz e a gravidade de cada consequência. A
regra da consolidação, a Ocorrência e o recurso o consultam.

Depois, cada leitor da consequência decide o que faz com a terceira, e um guardião cobra que nenhum
a esqueça. A progressão a deixa seguir. A faixa do corte a conta só pela ampla. A ordem a tira, ou a
deixa sem posição, só na lista reservada. A ocupação, a fila, a situação da vaga e a relação do
sorteio a subtraem da reserva até o horizonte do marco.

As decisões técnicas estão em [research.md](research.md) (`T-001` a `T-017`); o modelo, em
[data-model.md](data-model.md); as recusas e as frases, em [contracts/](contracts/); o roteiro, em
[quickstart.md](quickstart.md).

## Technical Context

**Language/Version**: Python 3.13, Django 5.2; JavaScript sem build na composição das Etapas.

**Primary Dependencies**: as do projeto; nenhuma nova.

**Storage**: PostgreSQL, com três migrations:

- `editais/0030`: duas colunas na Etapa;
- `resultados/0007`: a constraint da consequência;
- `recursos/0004`: a constraint da decisão.

Nenhuma tabela append-only nova, e o `M` da preparação do banco não muda.

**Testing**: pytest contra PostgreSQL (`make test-pg`):

- unidade para `efeito.py`, `regra.py` e `pejus.py`;
- integração para consolidação, Ocorrência, progressão, faixa, ordem, ocupação, fila, sorteio,
  recurso e Retificação;
- interface para composição, Retificação, consolidação, relatório e portal;
- documento pelo compositor;
- o guardião da FR-7018.

**Target Platform**: o monólito Django: gestão em `/gestao/`, portal e documento PDF.

**Project Type**: aplicação web, backend com templates.

**Performance Goals**: nenhuma consulta nova nas superfícies com orçamento declarado da `011`, da
`012` e da `015`.

- A progressão e a faixa mudam dentro do `Exists` que já existe (T-006, T-007).
- A ordem ganha um `~Exists` só no recorte reservado (T-008).
- A subtração na ocupação é **uma** consulta por apuração (T-009).

**Constraints**:

- CSP sem inline;
- classe nova com regra na folha;
- o vocabulário do documento nas recusas;
- publicação imutável: o acervo se recompõe idêntico (SC-2330);
- Resultado lido por `vigentes`, salvo o impedimento histórico da Retificação (T-012).

**Scale/Scope**: dois campos, um degrau, uma consequência, um achado, uma recusa de Retificação e
cerca de quinze leitores classificados.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o plano o atende | Situação |
|---|---|---|
| **I. Linguagem ubíqua** | "Retirada da reserva", "deixa de concorrer pela reserva", "continua na ampla concorrência", as palavras dos Editais 28/2026 e 57/2026. As recusas falam assim | ✅ |
| **II. Imutabilidade e temporalidade** | O efeito é norma publicada num degrau novo. O acervo é lido como "elimina" sem regravação (T-002). O Resultado guarda a consequência, que se lê por si (D-003). O impedimento de retificar é histórico (T-012) | ✅ |
| **III. Segurança e auditoria** | Nenhuma permissão nova. A parte pública não leva o motivo (FR-7017) | ✅ |
| **IV. Regras explícitas e concorrência** | A consequência é derivada da regra, nunca digitada (T-005). O efeito sobre muitos é mostrado antes da confirmação (UX-743). A Retificação e a consolidação se serializam pelo bloqueio do Processo (T-012) | ✅ |
| **V. Rastreabilidade e simplicidade** | Um módulo puro. Nenhuma tabela nova. A subtração da reserva entra num ponto só, `habilitadas_pelo_corte` (T-009). Um guardião classifica todo leitor (T-016). Matriz `rastreabilidade.md` na implementação | ✅ |
| **VI. Jornada demonstrável** | O quickstart percorre as seis histórias. A jornada do candidato é verificada no navegador | ✅ |

**Re-check depois do desenho: sem violação.** O desenho trouxe dois refinamentos à spec:

- **FR-7019 e o cenário 6 da US4.** Na `018`, a decisão fixa a conclusão, e não a consequência, que é
  derivada (FR-059 da `018`). A FR-7019 e o cenário foram reescritos (T-011).
- **FR-7030, nova.** A relação de habilitados do sorteio é um leitor que a spec não nomeava: na Etapa
  de habilitação, a inscrição retirada chega `HABILITADA` (T-010).

## Project Structure

### Documentation (this feature)

```text
specs/164-efeito-do-desfecho-por-lista/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── recusas.md
│   └── telas-e-documento.md
├── checklists/requirements.md
├── rastreabilidade.md    # escrito na implementação
└── tasks.md              # $speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/
│   ├── models/etapas.py                 # efeito_desfavoravel, efeito_da_ausencia
│   ├── migrations/0030_efeito_do_desfecho.py
│   ├── domain/etapas.py                 # validate_stage
│   ├── domain/validation.py             # efeito_sem_reserva
│   ├── domain/mutabilidade.py           # os dois campos, retificáveis
│   ├── domain/reaproveitamento.py       # a cópia leva o efeito
│   ├── application/draft.py             # grava os dois campos
│   └── api/serializers.py
├── publicacoes/
│   ├── application/publish_edital.py    # o efeito explícito na Etapa restrita e eliminatória
│   ├── application/retificacoes.py      # impedimento histórico
│   ├── domain/elevacao.py               # degrau 23
│   └── infrastructure/pdf.py, apresentacao.py  # a frase do efeito
├── shared/canonical.py                  # SCHEMA_VERSION = 23
├── resultados/
│   ├── models.py, migrations/0007_retirada_da_reserva.py
│   ├── domain/efeito.py                 # NOVO
│   ├── domain/regra.py                  # o desfavorável lê o efeito
│   ├── application/ocorrencia.py        # o efeito da ausência
│   ├── application/consolidacao.py      # o motivo com a reserva; a contagem da confirmação
│   ├── application/prontidao.py         # Regra 2 aceita a retirada; faixa só pela ampla
│   └── application/selectors.py         # "retirada" ao lado de "habilitada"
├── classificacao/
│   ├── application/calculo.py           # universo reservado sem a retirada anterior
│   ├── domain/universo_classificavel.py # sem posição por retirada no recorte reservado
│   └── application/reproducao.py
├── ocupacao/application/selectors.py    # habilitadas_pelo_corte subtrai na reserva
├── sorteios/application/habilitacao.py, relacao.py, previa.py
├── recursos/
│   ├── models.py, migrations/0004_retirada_da_reserva.py
│   └── domain/pejus.py                  # gravidade
├── portal/situacao.py, templates/portal/acompanhamento.html
└── interface/
    ├── forms.py, views.py, retificacao.py, revisao.py
    ├── relatorio_do_edital.py, conferencia_da_ordem.py
    ├── static/interface/alcance.js      # mostra o grupo do efeito
    └── templates/interface/_etapa.html, resultados.html, consolidacao_confirmar.html

backend/tests/
├── test_leitores_da_consequencia.py     # o guardião da FR-7018
├── unit/resultados/test_efeito_do_desfecho.py
├── integration/resultados/test_retirada_da_reserva.py
├── integration/classificacao/test_ordem_com_retirada.py
├── integration/ocupacao/test_ocupacao_com_retirada.py
├── integration/sorteios/test_relacao_com_retirada.py
├── integration/recursos/test_recurso_da_retirada.py
├── integration/publicacoes/test_retificacao_do_efeito.py
├── integration/editais/test_publicacao_do_efeito.py
└── interface/test_telas_da_retirada.py
```

**Structure Decision**: o monólito existente. Nenhum app novo: o efeito é atributo da Etapa, e a
consequência é do Resultado, que já tem dono em `resultados`.

## Increments

Um PR, o #543, empilhado sobre o #542. Os commits seguem a ordem da dependência:

1. **A — a norma.**
   - Colunas, gravação, validação, degrau 23, mutabilidade.
   - Documento, Revisão, composição, tela de Retificação (US1).
   - Impedimento histórico da Retificação (US5).
2. **B — o Resultado e as listas.**
   - Consequência nova, regra, Ocorrência.
   - Progressão, faixa, ordem, ocupação, fila, sorteio (US2, US6).
   - O guardião.
3. **C — o recurso.** Gravidade na vedação de piora; reavaliação contra ausência (US4).
4. **D — o que se lê.** Portal (US3) e gestão: relatório, Resultados, confirmação da consolidação.

**A sozinho não vai para produção.** Ele publica um efeito que a operação ainda não aplicaria. Os
quatro vão juntos, como o A e o B da `163`.

## Complexity Tracking

Sem violação a justificar.
