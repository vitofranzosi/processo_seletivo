# Implementation Plan: A verificação da autodeclaração por vídeo, só em desenvolvimento

**Branch**: `claude/166-verificacao-por-video`, sobre `claude/165-regras-de-deliberacao-9f8a47`
| **Date**: 2026-11-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/166-verificacao-por-video/spec.md`

## Summary

A Etapa decisória colegiada da `165` ganha a **admissão do vídeo**: a coluna `admite_video` e o campo
`videoOption` do degrau 25, no caminho que a `164` e a `165` abriram (rascunho, publicação,
mutabilidade, Retificação, documento), com quatro recusas impeditivas e a chave
`VERIFICACAO_POR_VIDEO`, recusada em produção.

Uma app nova, `verificacao`, guarda o envio em partes (transitório), o vídeo (append-only), a abertura
(append-only), o encaminhamento (append-only) e a eliminação (append-only). O portal ganha a página de
gravação — com a única exceção de CSP do sistema, `media-src 'self' blob:` — e o comprovante; a Mesa
ganha o vídeo no painel do documento, aberto como ato registrado e entregue com `Range`.

**Nada paralelo**: o parecer pelo vídeo é a Avaliação da `012`, com os rótulos "Confirmo" e "Não dá para
confirmar pelo vídeo"; a deliberação é a da `165`; a R-11 é um ramo no plano da consolidação da `165`,
que separa "encaminhar à entrevista ao vivo"; o encaminhamento usa a reabertura da `012`. O meio de
cada parecer é derivado, e não copiado (D-004).

A retenção é um comando com prazo sem valor padrão (P-10). A porta do piloto é documentação e a
recusa de produção.

As decisões estão em [research.md](research.md); o modelo, em [data-model.md](data-model.md); as rotas
e recusas, em [contracts/](contracts/); o roteiro, em [quickstart.md](quickstart.md).

## Technical Context

**Language/Version**: Python 3.13, Django 5.2; JavaScript sem build (`MediaRecorder`,
`crypto.subtle`, `fetch`).

**Primary Dependencies**: as do projeto; **nenhuma nova**. A conferência do contêiner é leitura de
caixas e elementos (T-003).

**Storage**: PostgreSQL e o armazenamento privado dos arquivos dos candidatos. Migrations:

- `editais/0032_admite_video`: a coluna;
- `verificacao/0001_inicial`: as cinco tabelas e os quatro gatilhos append-only.

O `M` da preparação do banco vai de 61 a **65**.

**Testing**: pytest contra PostgreSQL (`make test-pg`, `DB_NAME` próprio):

- unidade: contêiner (MP4 e WebM gerados à mão), intervalo de bytes, roteiro e marcas, a tabela da
  R-11 (três regras × três e cinco pareceres);
- integração: envio em partes, retomada, troca, abertura, autorização, conclusão sem abertura,
  consolidação e encaminhamento, recusa do desfavorável, gatilhos append-only, retenção;
- interface: composição, publicação, página de gravação (CSP e `Permissions-Policy`), Mesa,
  conferência, acompanhamento;
- `tests/javascript`: a máquina de estados da página, com o shim de DOM do projeto;
- navegador do painel: a jornada do candidato com fonte sintética.

**Target Platform**: o monólito Django: portal em `/selecoes/`, gestão em `/gestao/`.

**Project Type**: aplicação web, backend com templates.

**Performance Goals**: a consolidação de uma Etapa sem vídeo não ganha consulta; a de Etapa com vídeo
ganha uma (as inscrições em modo vídeo da seleção). Os pedidos com `Range` não conferem o resumo
(T-006). Cada parte do envio é uma escrita de ≤ 8 MiB, dentro dos 120 s do gunicorn.

**Constraints**: CSP sem `unsafe-inline`; nada de `Permissions-Policy` global; os limites globais de
envio intocados; tudo em português; nenhuma dependência de visão computacional (FR-7150).

**Scale/Scope**: dezenas a centenas de vídeos por Edital, de ~1 a 3 minutos (≤ 25 MB cada).

## Constitution Check

| Princípio | Como o plano o cumpre |
|---|---|
| I. Linguagem ubíqua | "verificação da autodeclaração", "Confirmo", "a comissão quer conversar com você"; "heteroidentificação" só na gestão (UX-770) |
| II. Fonte única e imutabilidade | a admissão é campo publicado, com degrau, elevação e mutabilidade; vídeo, abertura, encaminhamento e eliminação são append-only; o Resultado continua o da `165` |
| III. Negar por padrão, LGPD, auditoria | chave desligada e recusada em produção; titularidade e Atribuição em toda rota, com resposta indistinguível; nada de data de nascimento nova; tomadas não enviadas nunca saem do aparelho; trilha sem conteúdo; retenção como parâmetro |
| IV. Regras no domínio, concorrência, ato explícito | a R-11 no plano e no ato; encaminhamento explícito com alcance; trava da inscrição na conclusão e do vídeo na troca e na abertura |
| V. Rastreabilidade e simplicidade | matriz em `rastreabilidade.md`; sem dependência nova, sem protocolo de terceiros, sem player próprio; a app nova é a menor fronteira que não mistura donos (T-001) |
| VI. Jornada completa | o candidato chega pelo acompanhamento, grava e recebe o comprovante; a comissão abre e dá parecer na Mesa; a presidência encaminha na conferência — tudo pelo canal do ator. A orientação da entrega 4 fica de fora, declarada |

**Gate**: sem violação. A única exceção de segurança — a CSP da página de gravação — é a que a spec
exige (FR-7117), em uma função e uma página.

**Pós-desenho**: o gate continua sem violação. A dependência da entrega 4 está declarada na spec, e o
acesso pelo acompanhamento (FR-7145) é um cartão de informação, e não o degrau da situação.

## Project Structure

### Documentation (this feature)

```text
specs/166-verificacao-por-video/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── rastreabilidade.md
├── contracts/
│   ├── rotas.md
│   └── recusas.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code

```text
backend/config/settings/{base,production,test}.py       # a chave, o teto, a retenção
backend/processo_seletivo/
├── verificacao/                                       # app nova
│   ├── models.py
│   ├── migrations/0001_inicial.py
│   ├── domain/{conteiner,roteiro,admissao,intervalo}.py
│   ├── application/{disponibilidade,envio,abertura,encaminhamento,retencao}.py
│   ├── infrastructure/entrega.py
│   └── management/commands/eliminar_videos_da_verificacao.py
├── editais/{models/etapas.py, domain/{etapas,validation,mutabilidade}.py, application/draft.py,
│            api/serializers.py, migrations/0032_admite_video.py}
├── publicacoes/{application/publish_edital.py, domain/{elevacao,alteracoes}.py,
│                infrastructure/{pdf,apresentacao}.py, application/retificacoes.py}
├── shared/{canonical.py, politica_de_conteudo.py}
├── seguranca/papeis.py                                # TABELAS_APPEND_ONLY
├── avaliacoes/application/avaliacao.py                # FR-7134 (gancho)
├── resultados/application/consolidacao.py             # FR-7138, FR-7139 (gancho)
├── portal/{verificacao.py, urls.py, templates/portal/verificacao*.html,
│           static/portal/{gravacao,assistir}.js, static/portal/portal.css}
└── interface/{verificacao.py, urls.py, views.py (Mesa, conferência, trilha), forms.py,
               templates/interface/{_video_da_mesa.html, encaminhar.html, _etapa.html},
               static/interface/{video_da_mesa.js, telas/...css}}
backend/tests/{unit,integration,interface}/verificacao/, tests/javascript/gravacao.test.js
doc/verificacao-por-video-porta-do-piloto.md          # FR-7153
```

**Structure Decision**: a app `verificacao` é dona dos cinco registros; o portal e a interface são donos
das telas, como em toda capacidade do projeto. As apps existentes ganham dois ganchos por importação
local, e não dependência de módulo.

## Increments

- **A — a admissão (US1, US7)**: coluna, degrau 25, recusas, mutabilidade, composição, documento; a
  chave nas settings e a recusa de produção; o guardião da R-19.
- **B — o candidato (US2, US5)**: app `verificacao` com modelos e migration; envio em partes;
  conferência do contêiner; comprovante; acesso no acompanhamento; página de gravação; entrega ao
  titular.
- **C — a comissão (US3, US4)**: abertura e entrega na Mesa; rótulos e exigência de abertura; R-11 no
  plano e no ato; encaminhamento na conferência.
- **D — a retenção (US6)** e a documentação da porta do piloto.

## Complexity Tracking

| Violação | Por que é necessária | Alternativa mais simples recusada porque |
|---|---|---|
| App nova | cinco registros de uma capacidade sem dono entre as apps existentes | pô-los em `avaliacoes` faria a Avaliação conhecer o envio de arquivo do candidato, e em `inscricoes`, a Inscrição conhecer a Mesa |
| Tabela mutável (`EnvioDoVideo`) num sistema append-only | o deslocamento de um upload muda a cada parte | registrar cada parte em linha append-only guardaria o rastro de um upload que não é ato |
