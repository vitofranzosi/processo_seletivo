# Implementation Plan: O assistente na página do Edital, no desenvolvimento local

**Branch**: `claude/assistente-pagina-edital-local-d6f44f` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

## Summary

Ligar o painel do protótipo da Fase C à página pública da seleção, por uma chave de desenvolvimento
que produção recusa. Nenhum domínio novo, nenhuma migration: o contexto do painel e os três envios do
protótipo passam a receber a conversa e o destino, e o portal ganha três rotas finas que os chamam.

## Technical Context

Django 5, PostgreSQL, o portal (`processo_seletivo/portal`) e o protótipo da gestão
(`processo_seletivo/interface/prototipo_do_assistente.py`). Testes com a porta de inferência falsa da
`071` (`tests/fixtures/inferencia.py`), sem rede.

## Constitution Check

- **Negar por padrão**: a chave vem desligada em todo módulo; desligada, as rotas respondem 404 e a
  página não traz o painel. Produção recusa subir com ela (`FR-1683`).
- **Publicação imutável / nada excluído**: não toca ato publicado; lê a versão vigente pela `070`.
- **Rastreabilidade**: requisitos em `spec.md`, matriz em `rastreabilidade.md`.

## Design

| Peça | Mudança |
|---|---|
| `config/settings/base.py` | `ASSISTENTE_NA_PAGINA_DO_EDITAL`, desligada por padrão; `ASSISTENTE_CONVERSAS_POR_SESSAO` (3) |
| `config/settings/production.py` | `_exigir(not ASSISTENTE_NA_PAGINA_DO_EDITAL)` |
| `config/settings/test.py` | a chave fixada desligada: o `make test-pg` exporta o `.env` |
| `interface/painel_do_assistente.py` (novo) | o que era do protótipo e é do painel: o contexto do fragmento, a simulação, a conversa da sessão (que só lê, quando pedido) e os dois envios. Não importa o portal |
| `interface/prototipo_do_assistente.py` | só o acesso da gestão, a chave de sessão do protótipo e as quatro views |
| `interface/templates/interface/prototipo_do_assistente.html` | os envios vêm de `rotas`; o selo diz "Ambiente local de desenvolvimento" na página pública; a mensagem do teto de conversas |
| `portal/assistente.py` (novo) | `painel()` para a página e as rotas `perguntar`, `sugestao` e `nova`, com a chave de sessão `assistente_do_edital`, a conversa criada no primeiro envio e o teto de conversas |
| `portal/views.py` (`selecao`) | renderiza o painel com a chave ligada; a resposta passa a privada; `assistente=False` para o protótipo, que acrescenta o dele |
| `portal/urls.py` | as três rotas, sob `<edital_id>/assistente/` |

**Sem ciclo de importação.** O protótipo importa `portal.views` para mostrar a página de fundo; a
página importa `portal.assistente`, que importa `painel_do_assistente` — e este não importa nenhum
dos dois.

**Uma leitura a mais por página, aceita.** O painel lê a versão pela `contexto()` da `070`, que traz
as Retificações futuras e as proveniências que a leitura da página não traz. Reaproveitar a versão
da página exigiria uma segunda porta para a `070`; o custo só existe com a chave ligada, na máquina
de desenvolvimento.

## Verificação

`make lint check test-pg`, e o percurso no navegador pela entrada `assistente-074` do
`.claude/launch.json`, num banco próprio com o corpus do piloto (`quickstart.md`).
