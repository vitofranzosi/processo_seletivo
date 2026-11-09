# Contrato: a página do Centro de Controle

## Rota

`GET /gestao/editais/<uuid:edital_id>/centro/` — nome `interface:centro-do-edital`.
Parâmetro opcional `?fase=<chave>`, com `chave` em `publicacao`, `inscricoes`, `avaliacao`,
`classificacao`, `resultado`, `vagas`, `convocacao`, `conclusao`.

| Situação | Resposta |
|---|---|
| Sem identidade na sessão | a mesma do detalhe (pedir identificação) |
| Edital inexistente ou de outra unidade | **404**, pela mesma porta do detalhe (`obter_edital`) |
| Edital em elaboração, homologado, cancelado, ou andamento indisponível | **302** para `interface:detalhe` (D-002) |
| Edital publicado ou encerrado | **200**, `interface/centro_do_edital.html` |

Nenhum `POST`. Nenhuma escrita.

## Contexto do template

| Chave | Origem |
|---|---|
| `edital` | `obter_edital` |
| `centro` | `centro.compor(...)` (ver [data-model](../data-model.md)) |
| `fase` | `centro.fase_consultada(centro, request.GET.get("fase"))` |
| `andamento` | `andamento.do_edital(edital, ator, em_curso=…)` |
| `linha_das_inscricoes` | `andamento.linha_das_inscricoes` |
| `porque_nada` | `providencias.porque_nada`, quando não há providência |
| `documentos` | `views._documentos_publicados` |
| `retificacoes_em_curso` | `atos_retificacao.em_curso` |
| `participantes`, `pendencias` | `views.participantes_do_edital`, `views._pendencias` |
| `grupo` | `acoes.hierarquia(acoes.do_edital(...))` |
| `pode_ver_avisos` | `views._pode_ver_avisos` |

## O HTML que os testes prendem

- `<h1>` com "Edital N/AAAA" e a linha "Onde estamos" (`.cc-onde`).
- O mapa: `<nav aria-labelledby="mapa-titulo">`, um `<ol class="cc-fases">` por grupo, um `<li>` por
  fase com `data-fase="<chave>"` e `data-andamento="<valor>"`.
- A fase consultada: o link do cartão tem `aria-current="true"` e contém
  `<span class="cc-oculto">fase consultada</span>`; o `<li>` tem a classe `consultada`. Nenhum outro
  cartão tem `aria-current`.
- As marcas: `.cc-marca.sua`, `.cc-marca.outro`, `.cc-marca.espera`, `.cc-marca.impedida`,
  `.cc-marca.nada`.
- O destaque: `<article class="cc-destaque">` com "Por que esta:".
- O detalhe da fase: `<section id="detalhe-da-fase">`; a tabela por lista é `table.cc-tabela-da-fase`,
  e o roteiro `ol.cc-roteiro`.
- "Onde cada lista está": `<section aria-labelledby="listas-titulo">`, ausente para quem não vê a
  matriz.
- Encerrar e Cancelar: dentro de `<details class="cc-terminais">`.
- O link de volta: `href` de `interface:detalhe`. No detalhe, o link de ida: `href` de
  `interface:centro-do-edital`, só com andamento.
