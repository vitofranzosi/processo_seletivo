# Implementation Plan: Publicação e homologação das inscrições

**Branch**: `claude/gps-inscricoes-publicacao-93355f` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)

## Summary

Um agregado novo no app `divulgacao` — `PublicacaoDasInscricoes`, com a projeção individual
`InscricaoNaPublicacao` — publicado por um comando que segue, passo a passo, a receita de
`publicar_resultado`: permissão fora da transação, trava do Processo, idempotência, aferição,
prévia assinada, autoridade e unidade congeladas, bytes canônicos, PDF gravado, trilha. A decisão
por inscrição continua no `ResultadoEtapa` da Etapa decisória; o ato só a projeta. Duas funções de
leitura existentes ganham o ato como fato autorizador — a visibilidade do resultado e a janela de
recurso —, e a situação do candidato ganha os degraus das inscrições.

## Technical Context

**Language/Version**: Python 3.12, Django 5 · **Storage**: PostgreSQL (gatilhos e privilégios) ·
**Testing**: pytest + pytest-django, `make test-pg` · **Target**: monólito web (gestão e portal) ·
**Constraints**: CSP sem inline; append-only em três camadas; consultas sem N+1 nas telas.

## Constitution Check

| Princípio | Como se cumpre |
|---|---|
| I — Linguagem | "homologação das inscrições" sempre qualificada (UX-461); nenhum sinônimo novo para a decisão, que continua `ResultadoEtapa` |
| II — Imutabilidade | ato append-only, bytes e PDF congelados, sucessão com motivo; divergência derivada |
| III — Segurança e LGPD | `resultado:publicar` + escopo; conteúdo público mínimo (D-010); trilha sem dado pessoal |
| IV — Regras explícitas | recusas nomeadas no domínio; prévia mostra alcance antes do ato; idempotência e trava |
| V — Simplicidade | um agregado; nenhum motor, nenhum genérico, nenhuma capacidade nova |
| VI — Jornada | gestão publica, portal consulta, candidato recorre — sem shell |

Sem violação a justificar.

## Project Structure

```text
backend/processo_seletivo/divulgacao/
├── models.py                       + PublicacaoDasInscricoes, InscricaoNaPublicacao
├── migrations/0005_publicacao_das_inscricoes.py   tabelas + gatilhos append-only e de coerência
├── domain/inscricoes.py            projeção pura, ordem, conteúdo público, recusas, divergência
├── application/inscricoes.py       prever, publicar, consultas (vigente, cadeia, autorização)
└── infrastructure/documento_das_inscricoes.py     PDF pelo compositor de pdf.py
backend/processo_seletivo/resultados/application/selectors.py   resultados_visiveis + fato novo
backend/processo_seletivo/recursos/application/interpor.py      _janelas_pertinentes + janela nova
backend/processo_seletivo/recursos/application/selectors.py     pendências por Etapa
backend/processo_seletivo/seguranca/papeis.py                   + 2 tabelas append-only
backend/processo_seletivo/interface/                            tela "Publicações das inscrições"
backend/processo_seletivo/portal/                               página pública, PDF, situação
backend/tests/…                                                 unidade, integração, autorização, portal
```

## Desenho

### Projeção (pura, `domain/inscricoes.py`)

Entrada: inscrições enviadas (id, Perfil, nome, protocolo), resultados vigentes da Etapa (por
inscrição), natureza, nomes dos Perfis da versão. Saída: `{perfis: [{nome, constam:[{protocolo,
nome}], indeferidas: n}], itens: [{inscricao_id, situacao, resultado_id}], pendentes: n}`. Ordem:
`(casefold sem acento do nome, protocolo)`. É a mesma função para a prévia, a publicação e a
divergência — três leituras de uma conta.

### Recusas (em ordem)

1. 404 fora do escopo; 403 sem `resultado:publicar`.
2. período em curso (`recusa_por_inscricoes_em_curso`).
3. nenhuma inscrição enviada.
4. natureza que regride; mesma natureza sem motivo.
5. Etapa ausente/indevida (não decisória-eliminatória, diferente da cadeia); homologação sem análise
   com Etapa decisória no Edital.
6. inscrições sem resultado na Etapa.
7. preliminar: período de recurso não escolhido, Evento inexistente ou já encerrado.
8. homologação com análise: recurso pendente, reavaliação pendente, prazo correndo.
9. prévia obsoleta (assinatura de `{natureza, etapa, anterior, itens}`).

### Integração com o recurso

- `resultados_visiveis(inscricao)`: além dos marcos divulgados, a Etapa do ato vigente da cadeia
  das inscrições (natureza ≠ recebidas) é autorizada, com o nome da versão que o ato cita.
- `_janelas_pertinentes`: para resultado da Etapa de análise, acrescenta a janela do último
  preliminar da cadeia — `(publicado_em, recurso_ate)` — ou a negativa quando ele declarou não
  prever recurso.
- Pendências da homologação: `recursos_pendentes_da_etapa` (nova, mesma regra de
  `recursos_pendentes_do_marco` restrita a resultado da Etapa) e `reavaliacoes_pendentes(edital,
  etapa_id)` (existente).

### Telas

- Gestão: `/gestao/editais/<id>/inscricoes/publicacoes` — GET com `natureza`, `etapa`, `evento`
  recompõe a prévia; POST publica e redireciona (PRG). Link na tela de Inscrições.
- Portal: `/selecao/…/inscricoes/<uuid>/` (página) e `…/documento.pdf`; lista dos atos na página da
  seleção; degraus novos no bloco de situação.

### Concorrência e idempotência

Trava `ProcessoSeletivo` (mesma linha que consolidar, julgar e publicar resultado travam);
`reserve`/`finish` com o pedido inteiro no payload; unicidade de raiz e de sucessor no banco como
segunda barreira.

## Fases

- **A** — modelo, migration, append-only, projeção e comando, com testes de domínio e integração.
- **B** — integração com visibilidade, janela e pendências; jornada do recurso de ponta a ponta.
- **C** — telas da gestão e do portal, situação do candidato, PDF; testes de view, autorização,
  CSP e vocabulário.
- **D** — validação no navegador, documentação operacional, rastreabilidade, PR.
