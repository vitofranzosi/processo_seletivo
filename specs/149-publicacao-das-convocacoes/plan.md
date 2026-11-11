# Implementation Plan: A publicação das convocações no GPS (149)

**Branch**: `claude/gps-public-convocacoes-db0f9b` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)

## Summary

A publicação de convocados é um ato append-only no molde da divulgação do resultado (`017`), no app
`convocacao`, que reúne recortes de um Edital e, para as convocações por publicação ainda não
comunicadas, grava na mesma transação a `ComunicacaoEmitida` que a comissão hoje grava à mão. A
página pública e o PDF leem os mesmos bytes congelados; a seção *Convocações* entra na página da
seleção; a gestão ganha a página de publicação do Edital e o caminho a partir da tela do recorte.

## Technical Context

**Language/Version**: Python 3.12, Django 5 · **Storage**: PostgreSQL (append-only por gatilho e
privilégio) · **Testing**: pytest contra PostgreSQL (`make test-pg`), Playwright opcional ·
**Target**: monólito Django, templates sem script inline (CSP da `091`/`092`) · **Constraints**:
número fixo de consultas na prévia e na página pública (FR-5736); nada de `<table>` no portal; folhas
estáticas.

## Constitution Check

- **Publicação é ato imutável** — o ato nasce publicado e não muda; correção é da convocação (D-006).
- **Nada é excluído** — três tabelas append-only nas três camadas; nenhuma migração de dados.
- **Negar por padrão** — a porta da condução para ler, a base de gestão da comissão para publicar,
  a autoridade conferida pela `060`.
- **Rastreabilidade** — trilha do ato e de cada comunicação; requisitos na matriz.

## Project Structure

```text
backend/processo_seletivo/convocacao/
├── models.py                          # + PublicacaoDeConvocados, ConvocacaoPublicada, DocumentoDa…
├── migrations/0007_publicacao_de_convocados.py   # tabelas, gatilhos append-only e de coerência
├── domain/publicacao.py               # efeitos, composição do conteúdo, assinatura (puro)
├── application/publicar.py            # prévia do Edital e o comando de publicar
├── application/publicacoes.py         # leituras: do Edital, da página pública, do candidato
└── infrastructure/documento.py        # o PDF, no compositor comum
backend/processo_seletivo/seguranca/papeis.py      # + três tabelas append-only
backend/processo_seletivo/portal/
├── urls.py, views.py                  # convocacoes/<id>/ e documento.pdf; seção na seleção
└── templates/portal/convocados.html, _convocacoes_da_selecao.html
backend/processo_seletivo/interface/
├── urls.py, views.py                  # editais/<id>/convocacoes/publicacao (GET prévia, POST)
└── templates/interface/publicacao_de_convocados.html (+ ajuste em convocacao.html)
backend/tests/
├── integration/convocacao/test_publicacao_de_convocados.py   # ato, efeitos, prazos, recusas
├── integration/convocacao/test_publicacao_imutavel.py        # append-only e constraints (PG)
├── interface/test_publicacao_de_convocados_na_gestao.py
└── interface/test_convocacoes_publicas.py                    # portal, privacidade, consistência
```

## Ordem

1. Modelo, migration, append-only (FR-5707, FR-5710).
2. Domínio puro: efeitos e composição (FR-5702, FR-5704–FR-5706, FR-5712–FR-5717).
3. Comando e prévia (FR-5701–FR-5711).
4. Portal: página, PDF, seção, área do candidato (FR-5718–FR-5726).
5. Gestão: página de publicação e o caminho do recorte (FR-5727–FR-5732).
6. Guardiões: contagem de migrations, gatilhos, inventário de negativas, folhas, vocabulário.
7. Navegador: capturas em 375, 1280 e 1920 px.

## Riscos

- **Guardiões de leitura de texto** (folha, `<table>` no portal, citações, inventário de 404): rodar
  `tests/interface`, `tests/portal` e `tests/test_citacoes_de_requisito.py` antes da suíte inteira.
- **Consultas fixas no portal do candidato** (`118`): o caminho para a publicação vem pela mesma
  leitura das comunicações, sem consulta por linha.
