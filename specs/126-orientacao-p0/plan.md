# Implementation Plan: Correções de orientação e segurança operacional depois da publicação (P0)

**Branch**: `claude/126-orientacao-p0-307906` | **Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)

**Input**: a spec desta pasta; o estudo de orientação da jornada de 06/11/2026 (PR #412).

## Summary

Cinco correções de apresentação, todas derivadas de leituras que já existem, sem migration e sem
mudar comando nenhum:

- **A1**: nas telas do corte, da ordem, da ocupação e do sorteio, o formulário que sucede o ato vigente
  passa para um `<details class="sucessao">` com rótulo próprio, aberto só quando o ato é obsoleto. As
  mensagens de sucesso passam a nomear o recorte e os números gravados.
- **A2**: uma função só, `recortes_sem_inscrito`, em `interface/conducao_do_marco.py`, diz quais
  recortes de um marco de sorteio não têm inscrição. A condução, a conferência dos gestos, a convocação
  e a ocupação a leem. A frase da faixa seguinte da convocação passa a depender de haver corte.
- **A4**: o relatório do Edital classifica as convocações por `prazo.estado`, e ganha a espécie
  `CONVOCACAO_SEM_COMUNICACAO`, que o Encerrar e o consolidado repetem.
- **A5**: a prévia do sorteio diz se há relação a congelar pela primeira vez; o template mostra o aviso
  no topo só nesse caso (ou com as inscrições correndo), e dentro do bloco de sucessão nos demais.
- **A6**: `interface/conferencia_da_ordem.py` resume, da proposta que a confirmação já calcula, quantas
  inscrições estão sem resultado em cada Etapa enumerada e os grupos de motivo. A confirmação o mostra.

## Technical Context

**Language/Version**: Python 3.13, Django (monólito do repositório)

**Primary Dependencies**: as do projeto; nenhuma nova

**Storage**: PostgreSQL. **Sem migration**, sem tabela, sem coluna (FR-4040)

**Testing**: pytest contra PostgreSQL (`make test-pg`); antes e depois no navegador com Playwright, num
clone descartável do banco pseudonimizado do Edital 35

**Target Platform**: a gestão, em navegador, renderizada no servidor

**Project Type**: aplicação web

**Performance Goals**: a condução do marco de sorteio ganha uma leitura das inscrições enviadas do Perfil
e uma da relação vigente por recorte (R-2); o relatório ganha o `prefetch` das comunicações (uma
consulta por Edital, R-5); as demais telas não ganham consulta, salvo a ordem, que lê as contagens do ato
recém-emitido no POST (R-7)

**Constraints**: CSP sem `inline` (o estilo do `details` vai para `telas.css`); classe citada em
template exige regra na folha; vocabulário pela varredura; `views.py` e `sorteio.html` são tocados também
pelo PR #410 (`124`), e as mudanças aqui ficam em trechos distantes dos dele (R-9)

**Scale/Scope**: oito templates, quatro módulos de `interface/`, a prévia do sorteio e o tipo novo em
`pendencias_do_edital`

## Constitution Check

| Princípio | Leitura | Situação |
|---|---|---|
| I — linguagem ubíqua | "recorte", "relação", "sucessão", "convocação", "comunicação" são os termos do código e das telas; nenhum termo novo | ✅ |
| II — imutabilidade e temporalidade | nada se grava; recolher a sucessão não muda o que ela exige (FR-4012); o critério de sem inscrito é derivado a cada leitura, e uma Retificação que reabre as inscrições o desfaz | ✅ |
| III — negar por padrão | nenhuma porta nova; a sucessão continua só para quem emite; a conferência dos gestos continua recusando no comando | ✅ |
| III — LGPD | a espécie nova é fato não público, com a regra de privacidade das outras da convocação (D-003) | ✅ |
| IV — regra explícita | uma função para sem inscrito, lida por quatro telas; a classificação da convocação é a do domínio (`prazo.estado`), e não uma segunda conta | ✅ |
| V — simplicidade | sem rota, tela ou estado novo; a G-01 não vira regra aqui: decidida pelo usuário (opção b), ela é da `128` (D-004) | ✅ |
| VI — jornada demonstrável | antes e depois no navegador, no Edital 35 (quickstart) | ✅ |

Nenhuma entrada em *Complexity Tracking*. Reavaliado depois do desenho: sem mudança.

## Project Structure

### Documentation (this feature)

```text
specs/126-orientacao-p0/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/telas.md
├── rastreabilidade.md
├── tasks.md
├── verificacao.md
├── capturas/
└── checklists/requirements.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── interface/
│   ├── conducao_do_marco.py        # recortes_sem_inscrito; células e alcance (A2)
│   ├── conferencia_da_ordem.py     # novo: resumo de quem está sem resultado (A6)
│   ├── relatorio_do_edital.py      # convocações por prazo.estado (A4)
│   ├── relatorio_consolidado.py    # a espécie nova somada (A4)
│   ├── relatorio_consolidado_pdf.py
│   ├── encerramento.py             # a espécie nova nas advertências (A4)
│   ├── views.py                    # contexto de marco, convocação, ocupação, ordem, corte
│   ├── static/interface/gestao/telas.css   # .sucessao
│   └── templates/interface/
│       ├── corte.html  ordenacao.html  ordenacao_confirmar.html  ocupacao.html
│       ├── sorteio.html  marco.html  convocacao.html
├── processos/application/pendencias_do_edital.py   # CONVOCACAO_SEM_COMUNICACAO
└── sorteios/application/previa.py  # inclui_congelamento (A5)

backend/tests/
├── interface/test_orientacao_p0.py           # novo: A1, A2, A5, A6 pelas telas
├── unit/interface/test_conferencia_da_ordem.py
└── integration/relatorio/test_convocacao_sem_comunicacao.py
```

**Structure Decision**: tudo em `interface/`, que é a camada que já lê sorteio, classificação, ocupação e
convocação juntos (R-2 da `049`). A única mudança fora dela é um campo a mais na leitura da prévia do
sorteio e um tipo a mais em `pendencias_do_edital`.

## Ordem de implementação

1. Testes que falham para cada item (TDD), um arquivo por camada.
2. A2 (`recortes_sem_inscrito`) — a base das telas de condução, convocação e ocupação.
3. A1 (sucessão recolhida e mensagens) e a regra de CSS.
4. A5 (aviso no lugar), depois de A1, porque vive dentro do bloco de sucessão do sorteio.
5. A4 (relatório, consolidado, Encerrar) e o ajuste das fixtures que convocavam sem comunicar.
6. A6 (confirmação da ordem).
7. `make lint check test-pg`, capturas, revisão independente.

## Complexity Tracking

Nenhuma violação a justificar.
