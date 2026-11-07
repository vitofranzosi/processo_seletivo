# Implementation Plan: Cinco ajustes de leitura dos Documentos Exigidos

**Branch**: `claude/funny-benz-83fc71` | **Date**: 2026-11-07 | **Spec**: [spec.md](spec.md)

## Summary

Cinco ajustes de apresentação, sem regra de negócio, sem migration, sem rota nova. Quatro são da
gestão (Revisão, somente leitura, ajuda da etapa) e do portal (anúncio dos documentos); um é de
texto do domínio da convocação (o fundamento pré-redigido).

## Technical Context

Django 5, templates do servidor com htmx 2.0.4, CSP sem `unsafe-inline` (091/092): estilo só em
folha, script só em arquivo. PostgreSQL na suíte. Nenhuma dependência nova.

## Constitution Check

- **Publicação imutável, nada excluído.** Nada aqui escreve: a Revisão e a página pública leem; a
  composição somente leitura deixa de oferecer a edição; o fundamento é sugestão editável.
- **Negar por padrão.** A recusa da gravação no servidor fica intocada (FR-4508). A tela passa a
  concordar com ela.
- **Rastreabilidade.** Uma pasta, FR-4501 a FR-4516, SC-1401 a SC-1407, matriz em
  [rastreabilidade.md](rastreabilidade.md).

## Onde cada ajuste mora

| Ajuste | Arquivos |
|---|---|
| Revisão por momento (FR-4501–4503) | `interface/revisao.py` (`BLOCOS`, `_documento`, `blocos`) |
| Somente leitura (FR-4504–4509) | `interface/views.py` (contexto `somente_leitura`); `compor_inscricao.html`, `compor_perfis.html`, `compor_cronograma.html`, `compor_etapas.html` (o `fieldset` da D-003); `compor_classificacao.html`, `_marco.html`, `_criterio.html` (campo a campo, D-004); `_acoes_da_linha.html`, `_perfil.html`, `_modalidade.html`, `_fato.html`, `_navegacao_etapa.html`; `static/interface/somente-leitura.js`; a regra do `fieldset.somente-leitura` em `static/interface/gestao/` |
| Ajuda dos documentos (FR-4510–4512) | `compor_inscricao.html` |
| Página pública (FR-4513–4515) | `portal/views.py` (`_anunciados_do_momento`, `_documentos_anunciados`), `portal/templates/portal/selecao.html` |
| Fundamento (FR-4516) | `convocacao/domain/documentos.py` (`fundamento_das_pendencias`) |

## Testes

Integração e interface, sem E2E de navegador:

- `tests/interface/test_ajustes_dos_documentos.py` — Revisão, somente leitura nas cinco etapas, a
  navegação por link, a simulação em somente leitura (pelo fragmento, com os valores que a tela
  exibe), a ajuda.
- `tests/integration/portal/test_anuncio_dos_documentos.py` — a conta, a marca e os três resumos.
- `tests/unit/convocacao/test_fundamento_das_pendencias.py` — a pontuação.
- O script da D-004 tem a lógica de montar os valores; o comportamento no navegador fica na
  verificação manual (o pedido desta spec exclui E2E).

Os guardiões que este tipo de mudança acorda: CSP (sem estilo nem script inline), classe no
template com regra na folha, varredura de vocabulário, `test_citacoes_de_requisito` e
`test_medida_dos_campos`. Os testes que fixavam o texto antigo ("que serão pedidos", "Pedido: na
convocação") são revistos, com a razão no próprio caso.
