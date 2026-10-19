# Implementation Plan: As telas de uso diário, primeiro incremento

**Branch**: `claude/determined-jennings-37b730` | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

## Summary

Três mudanças de apresentação, cada uma restrita às telas que nomeia. Na lista de Processos, a
faixa de ações perde os três botões que a barra da `076` já oferece, e fica com "Novo Processo
Seletivo". Nas cinco telas que estouram a 375 px, uma regra na folha da própria tela — e, no
detalhe da Retificação, a moldura que rola em volta da tabela — faz a página caber, sem mudar
texto, campo ou coluna. Nas quatro telas de uso diário, a trilha sai do conteúdo e vai para o
cabeçalho de contexto, por um bloco que o `base.html` passa a oferecer (R-001). Nenhuma migration,
nenhuma permissão, nenhum endereço novo.

## Technical Context

Django 5 sobre PostgreSQL; nada de servidor muda além da view `lista`, que deixa de entregar três
chaves que o template não lê mais. Frente sem dependência nova: templates, a folha inline do
`base.html` e o bloco `estilo_da_pagina` de cada tela. A linha de base visual é o inventário com o
shell (`doc/inventario-visual-da-gestao-2026-10-16/com-o-shell/resultados.json`, barra expandida, e
`com-o-shell/recolhida/resultados.json`), medido no banco `ps_inventario_telas`.

Detalhes, causas medidas e alternativas descartadas em [research.md](research.md). Não há entidade
nem contrato externo: `data-model.md` e `contracts/` não se aplicam.

## Constitution Check

- **Negar por padrão (III, IV)**: tirar os botões da lista não muda quem chega a cada destino; os
  itens da barra continuam saindo dos mesmos predicados de `navegacao.py`, e a view de cada
  destino continua decidindo (`FR-1742`; `FR-482` da `033`).
- **Linguagem ubíqua (I)**: os rótulos da trilha são os que as telas já usavam — Minhas Etapas,
  Minha Mesa, Alocação por Etapa, o nome da Etapa, o protocolo da inscrição.
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py`.
- **Simplicidade (V)**: um bloco de template, regras de página, uma `div` em volta de uma tabela.
  Nenhum script, nenhuma regra global nova além da cor dos links da trilha no cabeçalho.
- **Completude de jornada (VI)**: o percurso das telas de uso diário é provado no navegador a 1280
  e a 375 px, e o inventário inteiro é refeito e comparado tela a tela.

Sem violação a justificar.

## Design

| Peça | Mudança |
|---|---|
| `interface/templates/interface/lista.html` | a faixa de ações só com "Novo Processo Seletivo", e só para quem pode criar; o bloco `caminho_do_contexto` com a trilha de um nível |
| `interface/views.py::lista` | sem `pode_ver_visao`, `pode_gerir_autoridades` e `pode_gerir_modelos` no contexto |
| `interface/navegacao.py` | a docstring deixa de dizer que a lista lê os predicados; eles continuam sendo os da barra |
| `interface/navegacao.py::declarar_secao` e `views.py::minha_etapa` (emenda de 17/10) | pela gestão, a view declara Processos Seletivos como a seção da Etapa, e a barra a usa no lugar da do endereço (R-005; `FR-1752`) |
| `interface/templates/interface/base.html` | o bloco `caminho_do_contexto` no `header.cabecalho-de-contexto`, cujo conteúdo padrão é o caminho da `076`; a regra `.caminho-da-secao a` |
| `minhas_etapas.html`, `minha_etapa.html`, `mesa_inscricao.html` | a `nav.trilha` sai do conteúdo e vai para o bloco, com os mesmos níveis e rótulos; pela gestão, a da Etapa começa na seção e no Processo, como a da Alocação (R-005) |
| `conclusoes.html` | `.tabela-rolavel{position:relative}` na folha da página (R-002) |
| `reaproveitar.html` | `fieldset{min-width:0}` na folha da página |
| `sorteio.html` | `.imutavel code{overflow-wrap:anywhere}` na folha da página |
| `compor_anexos.html` | `fieldset.linha.anexo-novo{min-width:0}` no bloco que a tela já tem |
| `retificacao_detalhe.html` | a tabela das alterações dentro de `div.tabela-rolavel` |
| `doc/inventario-visual-da-gestao-2026-10-16.md` e `depois-da-077/` | o inventário refeito nos dois estados da barra, a comparação e as capturas das telas tocadas |

**Uma trilha por página.** Nas quatro telas, a trilha é a mesma `nav aria-label="Trilha de
navegação"` de sempre, e só muda de lugar: sai do `main` e vai para o cabeçalho de contexto. Nas
outras 55 telas o bloco não é sobrescrito, e o cabeçalho é o da `076`, byte a byte.

## Testes que mudam, e por quê

| Guardião | O que muda |
|---|---|
| `test_shell_da_gestao.py::test_a_lista_e_a_barra_oferecem_as_mesmas_secoes` | a lista já não oferece as seções: o teste vira `test_a_lista_deixou_as_secoes_para_a_barra`, e prova, papel a papel, que o conteúdo não tem nenhum dos três links; o que a barra oferece continua provado contra o destino (`FR-1740`, `FR-1742`) |
| `test_acessibilidade_da_012.py::test_as_telas_tem_titulo_e_trilha_de_navegacao` | continua igual — a trilha está na página, no cabeçalho |
| `test_tela_de_autoridades.py`, `authorization/test_visao_institucional.py` | continuam iguais — leem a página inteira, e o link está na barra |
| `test_caminho_ate_a_mesa.py`, `test_mesa.py` (o texto "Minha Mesa") | continuam iguais — o rótulo é o mesmo, no cabeçalho |
| `performance/test_escala_da_mesa.py` (120 000 bytes) | medido antes e depois; a distribuição ganha só a regra da cor dos links |

Testes novos em `tests/interface/test_telas_de_uso_diario.py`: a faixa de ações da lista; a trilha
no cabeçalho, e só uma, nas quatro telas; o cabeçalho da `076` nas demais; as cinco correções
presentes, cada uma só na sua tela.

## Verificação

`make lint check test-pg` com `DB_NAME` próprio; o percurso do [quickstart](quickstart.md) no
navegador, a 1280 e a 375 px; o inventário refeito com `BARRA=expandida` e `BARRA=recolhida`, e
comparado por `comparar.py` com as duas linhas de base do shell.
