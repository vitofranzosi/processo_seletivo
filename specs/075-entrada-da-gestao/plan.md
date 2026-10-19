# Implementation Plan: A entrada da gestão

**Branch**: `claude/redesign-acesso-entrada-f8c894` | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

## Summary

Trocar a tela técnica de `/gestao/identificar` pela página de acesso do conceito A do estudo de
16/10, com a escolha de identidades em etapa própria; fazer as 90 portas da gestão mandarem à
identificação com o destino; gravar a origem da identidade na sessão; e dar ao portal as duas
portas — "Minhas inscrições" e, só com método de entrada, "Área de gestão". Nenhuma migration,
nenhum domínio novo, nenhuma permissão mudada. As telas operacionais só mudam o nome do produto no
cabeçalho.

## Technical Context

Django 5, PostgreSQL, a fronteira de identidade (`processo_seletivo/interface/identidade.py`), o
seletor de vínculos de comissão (`comissoes/application/selectors.py::identidades_com_trabalho`) e
a trilha de auditoria (`auditoria/models.py::RegistroAuditoria`). Frente sem dependência nova: CSS
nos templates, como o resto da gestão, um sprite SVG inline e um script curto para a busca. Os
protótipos do estudo (`interface/prototipo_do_acesso.py`) são a referência de desenho e saem.

## Constitution Check

- **Negar por padrão**: a demonstração continua existindo só com `INTERFACE_SELETOR_IDENTIDADE`;
  sem ela, a página de acesso responde 503 sem ação de entrar, o envio responde 503 sem gravar, a
  escolha de identidades responde 503, e uma sessão de demonstração deixa de valer (`FR-1698`).
  Produção continua recusando subir com a chave.
- **Segurança e auditoria**: o destino é conferido contra redirecionamento aberto (`FR-1696`); a
  auditoria continua gravando o sujeito escolhido, como hoje; nenhum código de permissão vai à tela.
- **Linguagem ubíqua**: presidência e avaliação continuam vínculo, e a interface diz isso; "Etapa
  alocada" é o termo do domínio, e não "atribuída".
- **Rastreabilidade**: requisitos em `spec.md`, matriz em `rastreabilidade.md`.
- **Simplicidade**: sem middleware novo, sem decorator novo; um auxiliar substitui as 90 chamadas.

Sem violação a justificar.

## Design

| Peça | Mudança |
|---|---|
| `interface/identidade.py` | `DESCRICOES` ao lado de `PAPEIS`; `metodos_disponiveis()`; `pedir_identificacao(request)`, que monta o redirecionamento com `?proximo=`; `destino_seguro(request, valor)`; a origem gravada em `identificar` e conferida em `ator_da_sessao` (`FR-1698`); `contexto_identidade` passa `metodos_de_acesso` |
| `interface/demonstracao.py` (novo) | as entradas de comissão a partir de `identidades_com_trabalho` e as de responsabilidade com o nome sugerido pela trilha (`D-003`) |
| `interface/views.py` | `identificar` (GET: acesso; POST: identifica e segue o destino; 422 sem nome), `identificar_demonstracao` (GET: a escolha); as 79 chamadas passam ao auxiliar |
| `interface/avisos.py`, `duvidas.py`, `assistente.py` | as 11 chamadas passam ao auxiliar |
| `interface/urls.py` | `identificar/demonstracao`; saem as rotas `prototipos/acesso/` |
| `interface/templates/interface/base_de_acesso.html` (novo) | a página de duas colunas, sem o cabeçalho da gestão, com o sprite |
| `interface/templates/interface/_estilo_do_acesso.html` (novo) | a folha das três telas de acesso, incluída pelo bloco `estilo_da_pagina` de cada uma — o guardião de classes resolve o `include` |
| `identificar.html`, `identificar_demonstracao.html` (novo), `sem_autenticacao.html` | as três telas sobre `base_de_acesso.html` |
| `interface/templates/interface/base.html` | o nome do produto no cabeçalho |
| `portal/templates/portal/base.html` | "Minhas inscrições" no lugar de "Entrar"; "Área de gestão" com `metodos_de_acesso`; o nome do produto |
| saem | `interface/prototipo_do_acesso.py`, `templates/interface/prototipo_acesso/`, `tests/interface/test_prototipo_do_acesso.py`, a entrada `redesign-acesso` do `.claude/launch.json` passa a abrir `/gestao/identificar` |

**A escolha na página própria, o envio no endereço de sempre.** Os formulários da escolha enviam
para `interface:identificar`, como hoje — o auxiliar `identificar` dos testes e os testes de CSRF
continuam valendo para o envio. O destino viaja como campo oculto.

**Destino só por GET.** Uma porta alcançada por POST sem identidade não guarda o destino: o POST não
se repete por redirecionamento, e reenviar um ato depois de identificar-se seria praticar algo que a
pessoa não confirmou.

## Testes que mudam, e por quê

| Teste | Mudança |
|---|---|
| `tests/interface/test_caminho_ate_a_mesa.py` | a lista de identidades passa a `identificar-demonstracao`; "preside" vira "Presidência" |
| `tests/interface/test_csrf.py` | o token vem da página de escolha, que é a que tem formulário |
| `tests/interface/test_lista.py`, `tests/authorization/test_mesa_por_post.py`, `tests/interface/test_duvidas.py` | o `Location` passa a trazer o destino; conferem o começo |
| `tests/integration/portal/test_porta_de_entrada.py` | "Entrar" vira "Minhas inscrições" |

Os outros que citam a identificação conferem com `in` e continuam valendo.

## Verificação

`make lint check test-pg`, e o percurso no navegador pela entrada `redesign-acesso` do
`.claude/launch.json` (`quickstart.md`), a 1280 e a 375 px.
