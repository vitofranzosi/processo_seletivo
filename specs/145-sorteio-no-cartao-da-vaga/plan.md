# Implementation Plan: O sorteio de cada vaga no cartão dela (145)

**Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md)

## Summary

Uma função de leitura reorganiza em memória o que a página já lê; o modelo da página troca o bloco
lateral por lista por um bloco no cartão de cada vaga e um resumo do Edital; a folha do portal ganha
as regras das classes novas e a ordem das áreas em tela estreita.

## Technical Context

Django, modelos de página do portal, folha estática `portal.css`. Sem script, sem migration, sem
rota. A política de conteúdo recusa estilo e script embutidos (UX-402).

## Constitution Check

- Publicação imutável: nada é escrito. A página lê relações e sorteios vigentes.
- Nada é excluído: a relação de vaga retirada continua apontada (FR-5160).
- Negar por padrão: a página é pública e continua lendo só o que já era público.

## O desenho

| Onde | O que |
|---|---|
| `portal/leitura.py` | `sorteios_por_vaga(sorteios, conteudo)` devolve o sorteio por vaga e o resumo |
| `portal/views.py` | cada Perfil do contexto recebe `sorteio`; o contexto recebe `resumo_do_sorteio` |
| `portal/templates/portal/selecao.html` | o bloco do Edital antes das vagas; o bloco da vaga no fim do cartão |
| `portal/static/portal/portal.css` | regras das classes novas; áreas da grade; linhas da grade larga |

## Testes e verificação

- `tests/unit/portal/test_sorteios_por_vaga.py`: a reorganização, sem banco.
- `tests/portal/test_sorteio_na_pagina_do_edital.py`: os seis casos da `021`, intactos, e os da 145.
- `tests/interface/test_polish_da_055.py`: a grade larga continua com as três áreas.
- Preview: 1280 e 375, antes e depois do sorteio.

## Complexity Tracking

Nada a justificar.
