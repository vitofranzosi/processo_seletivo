---

description: "Implementation plan — 049 · Operar o resultado por marco"
---

# Implementation Plan: Operar o resultado por marco, e não por recorte

**Branch**: `claude/nova-spec-049-marco-048300` · **Date**: 2026-09-28 · **Spec**: [spec.md](spec.md)

## Summary

Uma **tela do marco** reúne o indicador recorte × operação e quatro gestos — ordenar, cortar, apurar,
publicar. Cada gesto tem duas fases, como a emissão da ordem de hoje: a **conferência** declara o
alcance recorte a recorte e não grava nada; a **confirmação** chama, recorte a recorte, o mesmo
comando de domínio que a tela do recorte chama, cada um na sua transação. O desfecho diz o que foi
feito e o que foi recusado, e o indicador continua dizendo depois.

**Nada novo no domínio.** Nenhuma entidade, nenhuma migration, nenhuma capacidade, nenhum comando de
gravação. O que se escreve:
- `interface/conducao_do_marco.py` — o indicador, o alcance e o laço do gesto (`R-2`);
- três views e duas rotas;
- dois templates e o resumo por marco na página do Edital.

**O risco está na conferência, e não no laço.** O gesto só é seguro se nenhum recorte for praticado
sobre um estado diferente do que foi mostrado. A ordem, o corte e a publicação já têm assinatura; a
apuração não tem, e o coordenador a confere sob a mesma trava (`R-4`).

## Technical Context

Python 3.13 · Django 5.2 · PostgreSQL · htmx, templates do servidor.

| Pergunta | Resposta |
|---|---|
| Entidade nova? | **não** — o gesto deixa rastro nos N atos, pelo `correlation_id` (`R-5`) |
| Migration? | **não** — `make preparar` continua em `N de 34` |
| Capacidade nova? | **não** — ordenar, cortar e apurar pedem a gestão da comissão; publicar pede `resultado:publicar` (`R-7`) |
| Comando de gravação novo? | **não** — `emitir_ordem`, `emitir_corte`, `emitir_apuracao`, `publicar_resultado` (`R-1`) |
| Assinatura nova? | **uma**, a da apuração, no coordenador (`R-4`) |
| Dependência nova entre apps? | **não** — o coordenador mora em `interface/`, que já lê os quatro (`R-2`) |
| URL nova? | **duas**: `marco` (GET) e `gesto-do-marco` (POST, `<operacao>`) |
| Escala | ≤ ~5 recortes por marco; 16 marcos no 140/2025. Página do Edital com número fixo de consultas (`SC-305`) |

**Nenhum `NEEDS CLARIFICATION`.** As decisões de domínio foram tomadas pelo usuário em 28/09
(`D-001` a `D-005`); as de desenho estão em [research.md](research.md).

## Constitution Check

| Princípio | Como se respeita | Onde |
|---|---|---|
| **III · Autoria e auditoria** | cada ato do gesto é gravado com quem confirmou; o gesto é uma confirmação humana, não um agendamento | `FR-820`, `SC-304` |
| **II · Publicação é ato imutável** | o gesto não sucede nada: só pratica o primeiro ato de cada recorte; o documento continua por recorte | `D-002`, `D-004`, `R-3` |
| **II · Uma fonte autoritativa** | recortes pela derivação única; assinaturas das telas de hoje; nenhum segundo caminho de gravação | `FR-812`, `FR-820`, `R-3` |
| **III · Negar por padrão; LGPD** | cada gesto pela porta do ato unitário; a tela do marco só oferece o que a pessoa pratica; o comando reautoriza sob a trava; nenhum dado pessoal novo na tela do marco | `FR-829`, `FR-830`, `R-7` |
| **IV · Regras explícitas / DP-17** | alcance declarado recorte a recorte antes da confirmação; o que fica fora diz por quê | `FR-818`, `FR-819`, `UX-092` |
| **IV · Concorrência** | assinatura por recorte conferida na gravação; transação por recorte; chave por recorte | `FR-821`, `FR-822`, `R-3` a `R-5` |
| **V · Simplicidade** | um laço sobre comandos existentes; nenhuma fila, nenhum estado novo | `R-1` |
| **VI · Completude de jornada** | a página do Edital leva à tela do marco; cada célula leva à tela do recorte | `UX-090`, `UX-091` |
| **Nada é excluído** | nenhuma migration; nenhuma linha apagada | [data-model.md](data-model.md) |

## Project Structure

```text
backend/processo_seletivo/interface/
├── conducao_do_marco.py          # novo: indicador, resumo, alcance, laço do gesto
├── views.py                      # três views: marco, gesto_do_marco; detalhe ganha o resumo
├── urls.py                       # duas rotas
└── templates/interface/
    ├── marco.html                # novo: indicador, gestos, desfecho
    ├── marco_conferir.html       # novo: a conferência do alcance
    └── detalhe.html              # resumo por marco e caminho para a tela do marco

backend/tests/interface/
└── test_conducao_do_marco.py     # indicador, gestos, recusa parcial, idempotência, portas

specs/033-navegacao-por-capacidade/inventario-das-negativas.md   # linhas das negativas novas
```

## Phase 0 — Research

[research.md](research.md), `R-1` a `R-11`.

## Phase 1 — Design

- [data-model.md](data-model.md): as leituras derivadas; nenhuma tabela.
- [contracts/o-gesto-do-marco.md](contracts/o-gesto-do-marco.md): rotas, formulários, estados e
  desfechos.
- [quickstart.md](quickstart.md): o percurso pelo navegador com um Edital de vários Perfis e cotas.

**Re-check da Constituição depois do desenho**: sem violação. Nenhuma linha em *Complexity Tracking*.

## Complexity Tracking

Nenhuma violação a justificar.
