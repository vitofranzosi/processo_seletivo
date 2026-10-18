# Inventário visual da gestão — 16/10/2026

Linha de base de **todas as telas de `/gestao/`**, a 1280×900 e a 375×812, tirada antes de
qualquer mudança no shell da gestão (etapa 2 da `075`). Serve para comparar antes e depois: o
rebranding e a barra lateral não podem mudar o que uma tela mostra nem fazê-la estourar a largura
sem que alguém veja.

Nenhuma linha de código de produto mudou. Medido na `main` em `bc6a7388`, **depois** da etapa 1 da
`075` (a entrada da gestão, PR 288). A primeira medição, de `6fc3a85a`, foi feita antes dela e está
no histórico deste arquivo. Entre as duas, só a tela `identificar` mudou de título e de `h1`, e
`identificar-demonstracao` é nova. Nenhum `scrollWidth`, `status` ou identidade mudou nas demais.
Todas as capturas foram refeitas, porque a marca do cabeçalho passou a dizer **Gestão de Processos
Seletivos** em toda tela.

## Como foi tirado

- **Banco próprio**, `ps_inventario_telas`: `createdb`, `migrate`, `sincronizar_unidades` e
  `seed_demo`, com `DB_USER=$USER DB_RUNTIME_USER=$USER LC_ALL=pt_BR.UTF-8
  DJANGO_SETTINGS_MODULE=config.settings.development INTERFACE_SELETOR_IDENTIDADE=true`.
- **Três objetos a mais que o seed não cria**, para que as telas que dependem deles tivessem o
  que mostrar: dois recursos contra a publicação do resultado do Edital 51/2026 (Bruno Costa,
  pendente; Clara Dias, admitido), gravados pelos comandos de aplicação `interpor` e `admitir`; e um
  aviso de resultado, confirmado pela própria tela `aviso-do-resultado` depois de capturá-la.
- **Identidade.** Cada tela tem uma identidade preferida — a que a alcança no uso real. Se ela não
  carregasse, o roteiro tentava as outras na ordem e guardava a primeira que deu 200. Nenhuma tela
  precisou do fallback. As identidades `inventario.*` não existem no seed: o seletor aceita qualquer
  nome, e só os papéis contam.

  | Identidade | Papéis | Para quê |
  |---|---|---|
  | `gustavo.gestor` | gestor | lista, Processo, comissão, inscrições, avisos |
  | `ana.elaboradora` | elaborador | composição, prévia, Retificação |
  | `bruno.homologador` | homologador | confirmações de homologar e devolver |
  | `paula.publicadora` | publicador | confirmações de publicar, divulgação do resultado |
  | `paulo.presidente` | nenhum (presidente da comissão) | distribuição, classificação, corte, ocupação, convocação, sorteio |
  | `joana.avaliadora` | nenhum (membro alocado) | Minhas Etapas e a Mesa |
  | `inventario.auditora` | auditor | auditoria do Edital e da comissão |
  | `inventario.julgadora` | julgador | recursos |
  | `inventario.exportadora` | exportador | exportação de matrículas |
  | `inventario.piloto` | gestor + participante do piloto | assistente e protótipo (com `ASSISTENTE_PILOTO=true`) |

- **Captura.** Chrome 155 por Playwright, contra um servidor WSGI numa thread do próprio roteiro.
  Página inteira (`full_page`), com escala 1. A 375 px a janela é estreita mas **não** emula
  dispositivo móvel. A captura tem a largura do conteúdo: uma tela que estoura sai mais larga que
  375 px, e o estouro aparece na imagem.
- **Medida.** `document.documentElement.scrollWidth` contra `clientWidth`. Estoura quando o primeiro
  passa do segundo. A coluna de culpados lista o elemento mais externo que passa da borda e não está
  dentro de um contêiner que rola.
- **PNG comprimido**: 128 cores, sem pontilhado. As 168 capturas somam ~13 MB, abaixo dos 20 MB
  combinados. Por isso ficaram **todas**, e não só as de 375 px.

### Para repetir

O roteiro e o gerador desta página estão na pasta ao lado. Os UUIDs de Processo e Edital no topo de
`capturar.py` são os deste seed: um `seed_demo` novo sorteia outros, e eles precisam ser trocados.
Os de Etapa e marco são fixos. Rode a partir de `backend/`, com o ambiente acima e
`ASSISTENTE_PILOTO=true`. No mesmo banco, passe também `AVISO=` com o id do aviso que a primeira
passada confirmou (está no caminho da linha `aviso` do `resultados.json`): sem ela o roteiro
confirma outro aviso, e a tela `avisos-do-edital` muda entre o antes e o depois sem que o shell
tenha nada com isso.

```bash
uv run --with playwright --with pillow python ../doc/inventario-visual-da-gestao-2026-10-16/capturar.py /caminho/de/saida
```

O depois do shell se compara pelo `resultados.json`, tela a tela: o `scrollWidth` de cada uma e o
título (`h1`), e não o total.

<!-- gerado por inventario-visual-da-gestao-2026-10-16/gerar_doc.py a partir de inventario-visual-da-gestao-2026-10-16/resultados.json -->

| Números | |
|---|---|
| Rotas em `interface/urls.py` | 117 |
| Rotas que renderizam tela por GET | 61 |
| Variantes capturadas (rota × slug ou estado) | 84 de 85 |
| Estouram a 375 px | 5 |
| Estouram a 1280 px | 0 |
| Rotas sem tela (POST, fragmento htmx, download) | 56 |

## Telas

| # | Rota (`name`) | Caminho medido | Identidade | Carregou | Estoura a 375 | Capturas |
|---|---|---|---|---|---|---|
| 1 | `lista` | `/gestao/` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/lista--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/lista--1280.png) |
| 2 | `identificar`<br>sem identidade | `/gestao/identificar` | sem identidade | sim | não | [375](inventario-visual-da-gestao-2026-10-16/identificar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/identificar--1280.png) |
| 3 | `identificar-demonstracao`<br>sem identidade; etapa da página de acesso (075) | `/gestao/identificar/demonstracao` | nenhuma | sim | não | [375](inventario-visual-da-gestao-2026-10-16/identificar-demonstracao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/identificar-demonstracao--1280.png) |
| 4 | `visao-geral` | `/gestao/visao-geral` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/visao-geral--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/visao-geral--1280.png) |
| 5 | `autoridades` | `/gestao/autoridades` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/autoridades--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/autoridades--1280.png) |
| 6 | `processo-criar` | `/gestao/processos/criar` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/processo-criar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/processo-criar--1280.png) |
| 7 | `processo-detalhe` | `/gestao/processos/6bb9dc91-75bd-48c1-9994-344cabc538d0/` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/processo-detalhe--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/processo-detalhe--1280.png) |
| 8 | `edital-criar` | `/gestao/processos/6bb9dc91-75bd-48c1-9994-344cabc538d0/editais/criar` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/edital-criar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/edital-criar--1280.png) |
| 9 | `processo-ato`<br>acao=ativar, Processo 2027 | `/gestao/processos/214d989f-3a43-4c89-9427-3e633623ebb8/atos/ativar` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/processo-ato-ativar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/processo-ato-ativar--1280.png) |
| 10 | `processo-ato`<br>acao=encerrar | `/gestao/processos/6bb9dc91-75bd-48c1-9994-344cabc538d0/atos/encerrar` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/processo-ato-encerrar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/processo-ato-encerrar--1280.png) |
| 11 | `processo-ato`<br>acao=cancelar | `/gestao/processos/6bb9dc91-75bd-48c1-9994-344cabc538d0/atos/cancelar` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/processo-ato-cancelar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/processo-ato-cancelar--1280.png) |
| 12 | `supervisao` | `/gestao/processos/6bb9dc91-75bd-48c1-9994-344cabc538d0/supervisao` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/supervisao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/supervisao--1280.png) |
| 13 | `detalhe`<br>Edital 51, publicado | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/detalhe-51--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/detalhe-51--1280.png) |
| 14 | `detalhe`<br>Edital 76, em elaboração | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/` | `ana.elaboradora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/detalhe-76--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/detalhe-76--1280.png) |
| 15 | `detalhe`<br>Edital 26, sorteio | `/gestao/editais/bd6e4985-c88c-4b8f-a04d-ea380376d781/` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/detalhe-26--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/detalhe-26--1280.png) |
| 16 | `duvidas`<br>Edital 01 | `/gestao/editais/ec6018d1-6970-4bfb-8697-350922669a20/duvidas/` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/duvidas--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/duvidas--1280.png) |
| 17 | `assistente`<br>Edital 01 | `/gestao/editais/ec6018d1-6970-4bfb-8697-350922669a20/assistente/` | `inventario.piloto` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/assistente--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/assistente--1280.png) |
| 18 | `assistente-prototipo`<br>Edital 01 | `/gestao/editais/ec6018d1-6970-4bfb-8697-350922669a20/assistente/prototipo/` | `inventario.piloto` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/assistente-prototipo--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/assistente-prototipo--1280.png) |
| 19 | `compor`<br>Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/compor` | `ana.elaboradora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/compor--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/compor--1280.png) |
| 20 | `compor-etapa`<br>etapa=identificacao, Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/compor/identificacao` | `ana.elaboradora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/compor-identificacao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/compor-identificacao--1280.png) |
| 21 | `compor-etapa`<br>etapa=perfis, Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/compor/perfis` | `ana.elaboradora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/compor-perfis--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/compor-perfis--1280.png) |
| 22 | `compor-etapa`<br>etapa=cronograma, Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/compor/cronograma` | `ana.elaboradora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/compor-cronograma--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/compor-cronograma--1280.png) |
| 23 | `compor-etapa`<br>etapa=etapas, Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/compor/etapas` | `ana.elaboradora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/compor-etapas--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/compor-etapas--1280.png) |
| 24 | `compor-etapa`<br>etapa=classificacao, Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/compor/classificacao` | `ana.elaboradora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/compor-classificacao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/compor-classificacao--1280.png) |
| 25 | `compor-etapa`<br>etapa=inscricao, Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/compor/inscricao` | `ana.elaboradora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/compor-inscricao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/compor-inscricao--1280.png) |
| 26 | `compor-etapa`<br>etapa=anexos, Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/compor/anexos` | `ana.elaboradora` | sim | **sim** (432 px) | [375](inventario-visual-da-gestao-2026-10-16/compor-anexos--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/compor-anexos--1280.png) |
| 27 | `compor-etapa`<br>etapa=conteudo, Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/compor/conteudo` | `ana.elaboradora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/compor-conteudo--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/compor-conteudo--1280.png) |
| 28 | `compor-etapa`<br>etapa=revisao, Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/compor/revisao` | `ana.elaboradora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/compor-revisao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/compor-revisao--1280.png) |
| 29 | `reaproveitar`<br>Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/reaproveitar` | `ana.elaboradora` | sim | **sim** (994 px) | [375](inventario-visual-da-gestao-2026-10-16/reaproveitar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/reaproveitar--1280.png) |
| 30 | `previa`<br>Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/previa` | `ana.elaboradora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/previa--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/previa--1280.png) |
| 31 | `ato`<br>acao=submeter, Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/atos/submeter` | `ana.elaboradora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/ato-submeter--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/ato-submeter--1280.png) |
| 32 | `ato`<br>acao=homologar, Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/atos/homologar` | `bruno.homologador` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/ato-homologar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/ato-homologar--1280.png) |
| 33 | `ato`<br>acao=devolver, Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/atos/devolver` | `bruno.homologador` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/ato-devolver--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/ato-devolver--1280.png) |
| 34 | `ato`<br>acao=revogar-homologacao, Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/atos/revogar-homologacao` | `bruno.homologador` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/ato-revogar-homologacao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/ato-revogar-homologacao--1280.png) |
| 35 | `ato`<br>acao=publicar, Edital 76 | `/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/atos/publicar` | `paula.publicadora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/ato-publicar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/ato-publicar--1280.png) |
| 36 | `ato`<br>acao=encerrar, Edital 51 | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/atos/encerrar` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/ato-encerrar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/ato-encerrar--1280.png) |
| 37 | `ato`<br>acao=cancelar, Edital 51 | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/atos/cancelar` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/ato-cancelar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/ato-cancelar--1280.png) |
| 38 | `retificar`<br>Edital 01 | `/gestao/editais/ec6018d1-6970-4bfb-8697-350922669a20/retificar` | `ana.elaboradora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/retificar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/retificar--1280.png) |
| 39 | `auditoria` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/auditoria` | `inventario.auditora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/auditoria--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/auditoria--1280.png) |
| 40 | `exportar-matriculas` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/matriculas` | `inventario.exportadora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/exportar-matriculas--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/exportar-matriculas--1280.png) |
| 41 | `inscricoes` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/inscricoes` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/inscricoes--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/inscricoes--1280.png) |
| 42 | `inscricao-recebida`<br>Ana Silva | `/gestao/inscricoes/3cd5294d-bbf6-4fbe-88fc-95c3a62b927b/` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/inscricao-recebida--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/inscricao-recebida--1280.png) |
| 43 | `retificacao-detalhe`<br>Retificação publicada | `/gestao/retificacoes/392c15f3-8d3d-4552-b5dc-b83a1ca84cae/` | `ana.elaboradora` | sim | **sim** (388 px) | [375](inventario-visual-da-gestao-2026-10-16/retificacao-detalhe--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/retificacao-detalhe--1280.png) |
| 44 | `retificacao-ato`<br>acao=submeter, Retificação publicada | `/gestao/retificacoes/392c15f3-8d3d-4552-b5dc-b83a1ca84cae/atos/submeter` | `ana.elaboradora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/retificacao-ato-submeter--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/retificacao-ato-submeter--1280.png) |
| 45 | `retificacao-ato`<br>acao=homologar, Retificação publicada | `/gestao/retificacoes/392c15f3-8d3d-4552-b5dc-b83a1ca84cae/atos/homologar` | `bruno.homologador` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/retificacao-ato-homologar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/retificacao-ato-homologar--1280.png) |
| 46 | `retificacao-ato`<br>acao=publicar, Retificação publicada | `/gestao/retificacoes/392c15f3-8d3d-4552-b5dc-b83a1ca84cae/atos/publicar` | `paula.publicadora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/retificacao-ato-publicar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/retificacao-ato-publicar--1280.png) |
| 47 | `retificacao-ato`<br>acao=devolver, Retificação publicada | `/gestao/retificacoes/392c15f3-8d3d-4552-b5dc-b83a1ca84cae/atos/devolver` | `bruno.homologador` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/retificacao-ato-devolver--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/retificacao-ato-devolver--1280.png) |
| 48 | `retificacao-ato`<br>acao=cancelar, Retificação publicada | `/gestao/retificacoes/392c15f3-8d3d-4552-b5dc-b83a1ca84cae/atos/cancelar` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/retificacao-ato-cancelar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/retificacao-ato-cancelar--1280.png) |
| 49 | `comissao` | `/gestao/processos/6bb9dc91-75bd-48c1-9994-344cabc538d0/comissao` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/comissao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/comissao--1280.png) |
| 50 | `alocacoes` | `/gestao/processos/6bb9dc91-75bd-48c1-9994-344cabc538d0/alocacoes` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/alocacoes--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/alocacoes--1280.png) |
| 51 | `auditoria-comissao` | `/gestao/processos/6bb9dc91-75bd-48c1-9994-344cabc538d0/auditoria` | `inventario.auditora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/auditoria-comissao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/auditoria-comissao--1280.png) |
| 52 | `distribuicao`<br>Prova objetiva, Edital 51 | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/distribuicao/00000000-0000-0000-0051-0000000000d1` | `paulo.presidente` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/distribuicao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/distribuicao--1280.png) |
| 53 | `registrar-ocorrencia` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/distribuicao/00000000-0000-0000-0051-0000000000d1/ocorrencia` | `paulo.presidente` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/registrar-ocorrencia--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/registrar-ocorrencia--1280.png) |
| 54 | `impedimentos` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/distribuicao/00000000-0000-0000-0051-0000000000d1/impedimentos` | `paulo.presidente` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/impedimentos--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/impedimentos--1280.png) |
| 55 | `trilha-da-avaliacao` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/distribuicao/00000000-0000-0000-0051-0000000000d1/trilha` | `paulo.presidente` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/trilha-da-avaliacao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/trilha-da-avaliacao--1280.png) |
| 56 | `resultados-da-etapa` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/distribuicao/00000000-0000-0000-0051-0000000000d1/resultados` | `paulo.presidente` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/resultados-da-etapa--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/resultados-da-etapa--1280.png) |
| 57 | `ordenacao`<br>marco FINAL, Edital 51 | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/marcos/00000000-0000-0000-0051-0000000000a1` | `paulo.presidente` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/ordenacao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/ordenacao--1280.png) |
| 58 | `corte-historico` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/cortes/47f4cc31-35d4-440a-9a9c-2c1db924fd97` | `paulo.presidente` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/corte-historico--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/corte-historico--1280.png) |
| 59 | `ato-de-ordenacao` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/marcos/00000000-0000-0000-0051-0000000000a1/atos/ac2080d5-e5a7-47ac-b251-246e03fbde81` | `paulo.presidente` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/ato-de-ordenacao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/ato-de-ordenacao--1280.png) |
| 60 | `corte` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/marcos/00000000-0000-0000-0051-0000000000a1/corte` | `paulo.presidente` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/corte--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/corte--1280.png) |
| 61 | `ocupacao` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/marcos/00000000-0000-0000-0051-0000000000a1/ocupacao` | `paulo.presidente` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/ocupacao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/ocupacao--1280.png) |
| 62 | `ocupacao-historico` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/marcos/00000000-0000-0000-0051-0000000000a1/ocupacao/historico` | `paulo.presidente` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/ocupacao-historico--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/ocupacao-historico--1280.png) |
| 63 | `convocacao` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/marcos/00000000-0000-0000-0051-0000000000a1/convocacao` | `paulo.presidente` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/convocacao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/convocacao--1280.png) |
| 64 | `convocacao-historico` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/marcos/00000000-0000-0000-0051-0000000000a1/convocacao/historico` | `paulo.presidente` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/convocacao-historico--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/convocacao-historico--1280.png) |
| 65 | `sorteio`<br>Edital 26 | `/gestao/editais/bd6e4985-c88c-4b8f-a04d-ea380376d781/marcos/00000000-0000-0000-0026-0000000000a1/sorteio` | `paulo.presidente` | sim | **sim** (643 px) | [375](inventario-visual-da-gestao-2026-10-16/sorteio--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/sorteio--1280.png) |
| 66 | `previa-de-publicacao` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/marcos/00000000-0000-0000-0051-0000000000a1/atos/ac2080d5-e5a7-47ac-b251-246e03fbde81/publicar` | `paula.publicadora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/previa-de-publicacao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/previa-de-publicacao--1280.png) |
| 67 | `publicacoes-do-marco` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/marcos/00000000-0000-0000-0051-0000000000a1/publicacoes` | `paula.publicadora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/publicacoes-do-marco--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/publicacoes-do-marco--1280.png) |
| 68 | `aviso-do-resultado` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/marcos/00000000-0000-0000-0051-0000000000a1/avisos/novo` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/aviso-do-resultado--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/aviso-do-resultado--1280.png) |
| 69 | `aviso-da-chamada` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/marcos/00000000-0000-0000-0051-0000000000a1/convocacao/avisos/novo` | nenhuma | **não** — 404 | — | — |
| 70 | `avisos-do-edital`<br>antes de qualquer aviso | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/avisos` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/avisos-do-edital-antes--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/avisos-do-edital-antes--1280.png) |
| 71 | `avisos-do-edital`<br>depois do aviso | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/avisos` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/avisos-do-edital--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/avisos-do-edital--1280.png) |
| 72 | `aviso`<br>aviso de resultado confirmado para o inventário | `/gestao/avisos/c1841d6c-924b-41a8-8d9a-99a17aacb900` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/aviso--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/aviso--1280.png) |
| 73 | `aviso-interromper` | `/gestao/avisos/c1841d6c-924b-41a8-8d9a-99a17aacb900/interromper` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/aviso-interromper--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/aviso-interromper--1280.png) |
| 74 | `aviso-reenviar` | `/gestao/avisos/c1841d6c-924b-41a8-8d9a-99a17aacb900/reenviar` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/aviso-reenviar--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/aviso-reenviar--1280.png) |
| 75 | `modelos-de-aviso` | `/gestao/modelos-de-aviso` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/modelos-de-aviso--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/modelos-de-aviso--1280.png) |
| 76 | `modelo-de-aviso-novo` | `/gestao/modelos-de-aviso/novo` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/modelo-de-aviso-novo--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/modelo-de-aviso-novo--1280.png) |
| 77 | `modelo-de-aviso` | `/gestao/modelos-de-aviso/87c71c47-4017-4aed-b8fe-f29e379c3359` | `gustavo.gestor` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/modelo-de-aviso--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/modelo-de-aviso--1280.png) |
| 78 | `marco`<br>condução do marco | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/marcos/00000000-0000-0000-0051-0000000000a1/conducao` | `paulo.presidente` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/marco--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/marco--1280.png) |
| 79 | `conclusoes-preservadas` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/distribuicao/00000000-0000-0000-0051-0000000000d1/conclusoes` | `paulo.presidente` | sim | **sim** (835 px) | [375](inventario-visual-da-gestao-2026-10-16/conclusoes-preservadas--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/conclusoes-preservadas--1280.png) |
| 80 | `recursos` | `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/recursos` | `inventario.julgadora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/recursos--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/recursos--1280.png) |
| 81 | `recurso`<br>recurso aguardando admissibilidade (criado para o inventário) | `/gestao/recursos/6539ef46-cee4-4d45-b9f8-8fe605b312ac` | `inventario.julgadora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/recurso-pendente--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/recurso-pendente--1280.png) |
| 82 | `recurso`<br>recurso admitido (criado para o inventário) | `/gestao/recursos/c7b47be9-fdcd-488d-8e3d-fe6be445072e` | `inventario.julgadora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/recurso-admitido--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/recurso-admitido--1280.png) |
| 83 | `minhas-etapas` | `/gestao/minhas-etapas` | `joana.avaliadora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/minhas-etapas--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/minhas-etapas--1280.png) |
| 84 | `mesa-inscricao` | `/gestao/minhas-etapas/af86be76-27f3-4e6a-b621-2b0771c323b2/00000000-0000-0000-0051-0000000000d1/inscricoes/3cd5294d-bbf6-4fbe-88fc-95c3a62b927b` | `joana.avaliadora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/mesa-inscricao--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/mesa-inscricao--1280.png) |
| 85 | `minha-etapa` | `/gestao/minhas-etapas/af86be76-27f3-4e6a-b621-2b0771c323b2/00000000-0000-0000-0051-0000000000d1` | `joana.avaliadora` | sim | não | [375](inventario-visual-da-gestao-2026-10-16/minha-etapa--375.png) · [1280](inventario-visual-da-gestao-2026-10-16/minha-etapa--1280.png) |

### Não montadas

- `aviso-da-chamada` (`/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/convocacao/avisos/novo`): exige `?comunicacao=` de uma `ComunicacaoEmitida` **por publicação** e enviada; o `seed_demo` convoca, mas não emite comunicação nessa forma. Responde 404 sem ela, para qualquer identidade. Tentativas: gustavo.gestor:404, ana.elaboradora:404, bruno.homologador:404, paula.publicadora:404, paulo.presidente:404, joana.avaliadora:404, inventario.auditora:404, inventario.julgadora:404, inventario.exportadora:404, inventario.piloto:404.

## Rotas sem tela

Listadas para que a conta feche com o `urls.py`. Nenhuma foi capturada.

| Rota (`name`) | Caminho | Por que não é tela |
|---|---|---|
| `sair` | `/gestao/sair` | só POST |
| `assistente-nova` | `/gestao/editais/<uuid:edital_id>/assistente/nova/` | só POST |
| `assistente-prototipo-perguntar` | `/gestao/editais/<uuid:edital_id>/assistente/prototipo/perguntar` | só POST |
| `assistente-prototipo-sugestao` | `/gestao/editais/<uuid:edital_id>/assistente/prototipo/sugestao` | só POST |
| `assistente-prototipo-nova` | `/gestao/editais/<uuid:edital_id>/assistente/prototipo/nova` | só POST |
| `previa-documento` | `/gestao/editais/<uuid:edital_id>/previa/documento` | download: PDF da prévia do Edital |
| `anexos` | `/gestao/editais/<uuid:edital_id>/anexos` | só POST |
| `anexo-arquivo` | `/gestao/editais/<uuid:edital_id>/anexos/<uuid:anexo_id>/arquivo` | download: arquivo do Anexo do rascunho |
| `documento-da-inscricao` | `/gestao/inscricoes/<uuid:inscricao_id>/documentos/<uuid:requirement_id>` | download: arquivo enviado pelo candidato |
| `fragmento-etapa` | `/gestao/editais/<uuid:edital_id>/fragmentos/etapa` | fragmento htmx |
| `fragmento-documento` | `/gestao/editais/<uuid:edital_id>/fragmentos/documento` | fragmento htmx |
| `fragmento-perfil` | `/gestao/fragmentos/perfil` | fragmento htmx |
| `fragmento-modalidade` | `/gestao/fragmentos/perfil/<str:indice>/modalidade` | fragmento htmx |
| `fragmento-perfil-duplicado` | `/gestao/fragmentos/perfil/<str:indice>/duplicar` | fragmento htmx |
| `fragmento-quadro` | `/gestao/fragmentos/perfil/<str:indice>/quadro` | fragmento htmx |
| `fragmento-fato` | `/gestao/fragmentos/perfil/<str:indice>/fato` | fragmento htmx |
| `fragmento-marco` | `/gestao/fragmentos/perfil/<str:indice>/marco` | fragmento htmx |
| `fragmento-marco-recomposto` | `/gestao/fragmentos/perfil/<str:indice>/marco/<str:sub>/recompor` | fragmento htmx |
| `fragmento-criterio` | `/gestao/fragmentos/perfil/<str:indice>/marco/<str:sub>/criterio` | fragmento htmx |
| `fragmento-evento` | `/gestao/fragmentos/evento` | fragmento htmx |
| `fragmento-retificacao-perfil` | `/gestao/fragmentos/retificacao/perfil` | fragmento htmx |
| `fragmento-retificacao-evento` | `/gestao/fragmentos/retificacao/evento` | fragmento htmx |
| `fragmento-retificacao-anexo` | `/gestao/fragmentos/retificacao/anexo` | fragmento htmx |
| `fragmento-retificacao-linha-do-quadro` | `/gestao/fragmentos/retificacao/<uuid:edital_id>/linha-do-quadro` | fragmento htmx |
| `fragmento-retificacao-modalidade` | `/gestao/fragmentos/retificacao/<uuid:edital_id>/modalidade` | fragmento htmx |
| `fragmento-retificacao-criterio` | `/gestao/fragmentos/retificacao/<uuid:edital_id>/criterio` | fragmento htmx |
| `fragmento-remover` | `/gestao/fragmentos/remover` | fragmento htmx |
| `consolidar-resultados` | `/gestao/editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/consolidar` | só POST |
| `distribuicao-remover` | `/gestao/editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/remover` | só POST |
| `reabrir-avaliacao` | `/gestao/editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/reabrir` | só POST |
| `emitir-ordenacao` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/emitir` | só POST |
| `emitir-corte` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/corte/emitir` | só POST |
| `emitir-apuracao` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/ocupacao/apurar` | só POST |
| `causar-faixa` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/ocupacao/faixa-seguinte` | só POST |
| `convocar` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/convocacao/convocar` | só POST |
| `convocar-titulares` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/convocacao/titulares` | só POST |
| `nao-atendimento-dos-vencidos` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/convocacao/vencidos` | só POST |
| `emitir-pendentes` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/convocacao/pendentes` | só POST |
| `desfechar` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/convocacao/<uuid:convocacao_id>/desfecho` | só POST |
| `comunicar-convocacao` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/convocacao/<uuid:convocacao_id>/comunicar` | só POST |
| `atestar` | `/gestao/inscricoes/<uuid:inscricao_id>/atestado` | só POST |
| `continuar-corte` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/corte/continuar` | só POST |
| `publicar-relacao-do-sorteio` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/sorteio/relacao` | só POST |
| `observar-ocorrencia-do-sorteio` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/sorteio/ocorrencia` | só POST |
| `realizar-sorteio` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/sorteio/realizar` | só POST |
| `anular-sorteio` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/sorteio/anular` | só POST |
| `publicar-resultado` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/atos/<uuid:ato_id>/publicar/confirmar` | só POST |
| `modelo-de-aviso-situacao` | `/gestao/modelos-de-aviso/<uuid:modelo_id>/situacao` | só POST |
| `gesto-do-marco` | `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/conducao/<str:operacao>` | só POST |
| `recurso-admitir` | `/gestao/recursos/<uuid:recurso_id>/admitir` | só POST |
| `recurso-julgar` | `/gestao/recursos/<uuid:recurso_id>/julgar` | só POST |
| `recurso-instruir` | `/gestao/recursos/<uuid:recurso_id>/instruir` | só POST |
| `recurso-documento-instruido` | `/gestao/recursos/<uuid:recurso_id>/instrucao/<uuid:documento_id>` | download: arquivo juntado na instrução do recurso |
| `mesa-avaliacao-gravar` | `/gestao/minhas-etapas/<uuid:edital_id>/<uuid:etapa_id>/inscricoes/<uuid:inscricao_id>/avaliacao` | só POST |
| `mesa-avaliacao-concluir` | `/gestao/minhas-etapas/<uuid:edital_id>/<uuid:etapa_id>/inscricoes/<uuid:inscricao_id>/avaliacao/concluir` | só POST |
| `mesa-documento` | `/gestao/minhas-etapas/<uuid:edital_id>/<uuid:etapa_id>/inscricoes/<uuid:inscricao_id>/documentos/<uuid:requirement_id>` | download: arquivo da inscrição, aberto na Mesa |

## Medições dos estouros

| Tela | `scrollWidth` a 375 | Elemento mais externo que passa da borda |
|---|---|---|
| `compor-anexos` | 432 | `fieldset.linha.anexo-novo (432px)` |
| `reaproveitar` | 994 | `fieldset (994px)` |
| `retificacao-detalhe` | 388 | `table (388px)` |
| `sorteio` | 643 | `code (639px)`, `code (639px)` |
| `conclusoes-preservadas` | 835 | (ver abaixo) |

### O que cada estouro é

Fica registrado aqui. A correção é decisão do produto, e não entra no shell sem ser pedida.

- **`conclusoes-preservadas`, 835 px.** A tabela está dentro de `.tabela-rolavel`, que rola. Mas cada
  linha tem um `label.oculto` (`position:absolute`), e o contêiner que rola não é posicionado: o
  rótulo invisível toma como referência um ancestral de fora e alarga a **página**. Nenhum elemento
  visível passa da borda, e por isso a coluna de culpados ficou vazia. Achado pela sonda, e não pela
  imagem.
- **`reaproveitar`, 994 px.** A tabela das origens fica dentro de um `fieldset`, que cresce até o
  conteúdo mínimo da tabela. A página inteira alarga, e não só a tabela.
- **`sorteio`, 643 px.** Os dois `code` com hash SHA-256 (método e manifesto) não quebram linha.
- **`compor-anexos`, 432 px.** A linha de Anexo novo (`fieldset.linha.anexo-novo`) não se ajusta à
  largura.
- **`retificacao-detalhe`, 388 px.** A tabela das alterações passa 13 px da borda.

A 1280 px nenhuma tela estoura.

## Depois do shell (076)

O inventário foi refeito com a barra lateral e o cabeçalho de contexto da
[`076`](../specs/076-shell-da-gestao/spec.md), no mesmo banco, com o mesmo roteiro e o mesmo
`AVISO`. As capturas e o `resultados.json` estão em
[`com-o-shell/`](inventario-visual-da-gestao-2026-10-16/com-o-shell/), e a comparação tela a tela
sai de `comparar.py`, ao lado do roteiro:

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/resultados.json doc/inventario-visual-da-gestao-2026-10-16/com-o-shell/resultados.json
```

| | Linha de base | Com o shell |
|---|---|---|
| Variantes que carregam | 84 de 85 | 84 de 85 — a mesma `aviso-da-chamada` fica de fora |
| `status` diferente | — | nenhum |
| Estouram a 375 px | 5 | os mesmos 5, com o mesmo `scrollWidth` |
| Estouram a 1280 px | 0 | 0 |

**A primeira medição achou uma regressão.** Com a barra sempre aberta, a matriz da Alocação por
Etapa (~1.213 px com as nove Etapas do seed) não cabia na área de conteúdo a 1280 px, e a página
passou a ter 1.477 px — contra a `FR-1062` da `057`, que quer a matriz sem rolagem interna e com o
cabeçalho preso à janela. O responsável pelo produto decidiu (DP-4 da `076`) que, nessa tela, a
barra fica recolhida em qualquer largura, como no celular. Com isso a página voltou a 1280.

Os cinco estouros a 375 px continuam registrados acima e fora do escopo do shell (DP-3).

**Depois da barra retrátil (emenda da 076).** A barra passou a ter dois estados na tela larga —
expandida, de 16rem, e recolhida, de 4,25rem —, com a escolha guardada no navegador. O roteiro
ganhou `BARRA=expandida|recolhida`, que grava a preferência antes de cada página, e o inventário foi
refeito nos dois estados. Em [`com-o-shell/`](inventario-visual-da-gestao-2026-10-16/com-o-shell/)
estão as capturas com a barra expandida; em
[`com-o-shell/recolhida/`](inventario-visual-da-gestao-2026-10-16/com-o-shell/recolhida/), o
`resultados.json` e as capturas a 1280 px com ela recolhida — a 375 px a preferência não vale, e as
capturas seriam as mesmas.

| | Linha de base | Expandida | Recolhida |
|---|---|---|---|
| Variantes que carregam | 84 de 85 | 84 de 85 | 84 de 85 |
| `status` diferente | — | nenhum | nenhum |
| Estouram a 375 px | 5 | os mesmos 5 | os mesmos 5 |
| Estouram a 1280 px | 0 | 0 | 0 |

## Depois da 077

O primeiro incremento da modernização por tela ([`077`](../specs/077-telas-de-uso-diario/spec.md))
corrigiu os cinco estouros a 375 px, tirou da lista de Processos os três botões que a barra já
oferece e levou a trilha das quatro telas de uso diário — a lista, Minhas Etapas, a Etapa e a
inscrição da Mesa — para o cabeçalho de contexto. O inventário foi refeito sobre a `main` em
`5c729dd0` com a mudança aplicada, no mesmo banco, com o mesmo roteiro e o mesmo `AVISO`, nos
dois estados da barra. Em [`depois-da-077/`](inventario-visual-da-gestao-2026-10-16/depois-da-077/)
estão o `resultados.json` com a barra expandida, o de
[`recolhida/`](inventario-visual-da-gestao-2026-10-16/depois-da-077/recolhida/), e as capturas das
nove telas tocadas, a 1280 e a 375 px, com a barra expandida. As capturas das demais seriam as de
`com-o-shell/`: o `resultados.json` mostra que nenhuma delas mudou.

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/com-o-shell/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-077/resultados.json
```

| | Com o shell | Depois da 077, expandida | Depois da 077, recolhida |
|---|---|---|---|
| Variantes que carregam | 84 de 85 | 84 de 85 | 84 de 85 |
| `status` diferente | — | nenhum | nenhum |
| Estouram a 375 px | 5 | **0** | **0** |
| Estouram a 1280 px | 0 | 0 | 0 |

**Só as nove telas tocadas mudaram.** Comparando campo a campo — `scrollWidth`, título, `h1` e
altura da página —, as diferenças estão todas nelas:

| Tela | O que mudou |
|---|---|
| `conclusoes-preservadas` | `scrollWidth` a 375: 835 → 375 |
| `reaproveitar` | `scrollWidth` a 375: 994 → 375 |
| `sorteio` | `scrollWidth` a 375: 643 → 375; a página cresce 49 px, porque os resumos quebram a linha |
| `compor-anexos` | `scrollWidth` a 375: 432 → 375 |
| `retificacao-detalhe` | `scrollWidth` a 375: 388 → 375; a página cresce 8 px, com a tabela na moldura que rola |
| `lista` | a página encurta 48 px a 1280 e 96 a 375: os três botões saíram da faixa |
| `minha-etapa` | encurta 23 px a 375: a trilha subiu ao cabeçalho |
| `mesa-inscricao` | encurta 37 px a 1280 e 23 a 375: a trilha subiu ao cabeçalho |
| `minhas-etapas` | nada medido muda: o cabeçalho passa a ser a trilha, com o mesmo texto |

Os cinco estouros descritos em *O que cada estouro é*, acima, ficam como registro da linha de base.
A causa medida de cada um e a correção estão no `R-002` da
[pesquisa da 077](../specs/077-telas-de-uso-diario/research.md).

## Depois da 078

O segundo incremento da modernização por tela ([`078`](../specs/078-telas-de-quem-elabora/spec.md))
levou à folha comum as duas causas que a `077` tinha corrigido tela a tela — a moldura que rola sem
posição e o `fieldset` que não encolhe —, tirou as três regras pontuais, e mudou as telas de quem
elabora: a trilha do detalhe do Processo, do detalhe do Edital e das nove etapas da composição subiu
ao cabeçalho de contexto, "O que fazer agora" vem antes do resto, e os Editais do Processo são a
tabela da lista. O inventário foi refeito sobre a `main` em `a41b67c0` com a mudança aplicada, no
mesmo banco, com o mesmo roteiro e o mesmo `AVISO`, nos dois estados da barra. Antes da mudança, o
mesmo roteiro reproduziu `depois-da-077/` sem diferença nenhuma.

Em [`depois-da-078/`](inventario-visual-da-gestao-2026-10-16/depois-da-078/) estão o
`resultados.json` com a barra expandida, o de
[`recolhida/`](inventario-visual-da-gestao-2026-10-16/depois-da-078/recolhida/), e as capturas, a
1280 e a 375 px, do detalhe do Processo, dos três detalhes de Edital e de duas etapas da composição
— a Identificação e os Anexos, que perderam a regra própria. As outras sete etapas mudam do mesmo
jeito que a Identificação: só o cabeçalho de contexto.

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-077/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-078/resultados.json
```

| | Depois da 077 | Depois da 078, expandida | Depois da 078, recolhida |
|---|---|---|---|
| Variantes que carregam | 84 de 85 | 84 de 85 | 84 de 85 |
| `status` diferente | — | nenhum | nenhum |
| Estouram a 375 px | 0 | 0 | 0 |
| Estouram a 1280 px | 0 | 0 | 0 |

**Só as telas de quem elabora mudaram de medida.** Campo a campo — `scrollWidth`, título, `h1` e
altura —, as diferenças estão nas 14 variantes desta feature, e em nenhuma outra:

| Tela | O que mudou |
|---|---|
| `processo-detalhe` | cresce 76 px a 1280 (14 com a barra recolhida) e 181 a 375: os Editais em tabela ocupam mais altura que a lista corrida; "O que fazer agora" sobe de y ≈ 1700 para y ≈ 345 a 1280 |
| `detalhe-26`, `detalhe-51`, `detalhe-76` | encurtam 37 px a 1280 e 23 a 375: a trilha subiu ao cabeçalho |
| `compor` e as nove etapas | encurtam 37 px a 1280 e 2 a 375: a trilha subiu ao cabeçalho |

As conclusões preservadas, reaproveitar e os anexos da composição continuam com `scrollWidth` de
375 a 375 px, agora pela regra da folha comum; as conclusões saem idênticas pixel a pixel.

**Pixel a pixel.** As capturas de antes e de depois foram tiradas no mesmo dia, no mesmo banco. Fora
das 14 variantes, as que diferem são de dois tipos: o que muda entre duas capturas seguidas do
mesmo código — a hora da leitura na Supervisão, na Visão Geral e nas dúvidas, cantos arredondados,
o cursor —, e a suavização do texto dentro das molduras que rolam a 375 px, que a posição nova muda
em até 67 de 255, sem mover caixa nenhuma. A medição está no `R-001` e nos achados da
[pesquisa da 078](../specs/078-telas-de-quem-elabora/research.md).

**Depois da revisão do PR.** A revisão levou à folha comum a regra do cartão em `.colunas` e tirou a
cópia da regra das molduras da vista do conjunto (Perfis e Classificação). Refeito nos dois estados
da barra e comparado com `depois-da-078/`, o inventário dá as mesmas medidas campo a campo, sem
estouro; pixel a pixel, só o que muda entre duas capturas do mesmo código — a hora da leitura e o
cursor. As capturas de `depois-da-078/` continuam valendo.

## Depois da 079

O terceiro incremento da modernização por tela ([`079`](../specs/079-telas-da-presidencia/spec.md))
mudou as telas da presidência da comissão: a trilha da Comissão, da conferência da inclusão, da
Alocação por Etapa e da Distribuição subiu ao cabeçalho de contexto; na Distribuição, os lugares da
Etapa — Impedimentos, Registrar ocorrência, Resultados e Trilha — vêm logo abaixo do título; a
Comissão tem a seção "Membros (N)"; e o botão da Alocação diz "Salvar alocação". Nenhuma regra da
folha comum mudou. O inventário foi refeito sobre a branch da `078` (`e781dfb3`, PR 293) com a
mudança aplicada, no mesmo banco, com o mesmo roteiro e o mesmo `AVISO`, nos dois estados da barra.
Antes da mudança, o mesmo roteiro reproduziu `depois-da-078/` sem diferença nenhuma.

Em [`depois-da-079/`](inventario-visual-da-gestao-2026-10-16/depois-da-079/) estão o
`resultados.json` com a barra expandida, o de
[`recolhida/`](inventario-visual-da-gestao-2026-10-16/depois-da-079/recolhida/), e as capturas, a
1280 e a 375 px, das três telas que mudaram. A conferência da inclusão não está no inventário — é a
resposta a um envio, e o roteiro só abre telas pelo endereço —, e foi vista no navegador.

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-078/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-079/resultados.json
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-078/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-079/resultados.json
```

O [`medidas.py`](inventario-visual-da-gestao-2026-10-16/medidas.py) é novo: compara largura, altura,
título e `h1`, variante a variante, que o `comparar.py` não compara e que a `078` conferiu à mão.

| | Depois da 078 | Depois da 079, expandida | Depois da 079, recolhida |
|---|---|---|---|
| Variantes que carregam | 84 de 85 | 84 de 85 | 84 de 85 |
| `status` diferente | — | nenhum | nenhum |
| Estouram a 375 px | 0 | 0 | 0 |
| Estouram a 1280 px | 0 | 0 | 0 |

**Só as telas da presidência mudaram de medida**, e só de altura — nenhuma largura, título ou `h1`:

| Tela | O que mudou |
|---|---|
| `alocacoes` | encurta 37 px a 1280 e 23 a 375: a trilha subiu ao cabeçalho; a barra continua no topo e a matriz, sem rolagem interna a 1280 |
| `distribuicao` | encurta 37 px a 1280 e 23 a 375: a trilha subiu; a faixa dos lugares da Etapa sai de y ≈ 644 para y ≈ 170 a 1280, e de y ≈ 998 para y ≈ 284 a 375 |
| `comissao` | cresce 11 px a 1280 e 46 a 375: o título "Membros (3)" ocupa mais do que a trilha que saiu |

**Pixel a pixel.** Fora das três telas, as capturas de antes e de depois diferem só no que muda entre
duas capturas do mesmo código: a hora da leitura na Supervisão, na Visão Geral, nas dúvidas e no
pulso do Processo, cantos arredondados (até 28 de 255) e o cursor num campo da ocorrência. É também o
que o diff permite: ele só toca os quatro templates da presidência.

## Depois da 080

O quarto incremento da modernização por tela ([`080`](../specs/080-telas-filhas-da-distribuicao/spec.md))
mudou as telas que se abrem a partir da Distribuição e a Auditoria da comissão: a trilha de
Impedimentos, Registrar ocorrência, Resultados, Trilha da avaliação, Conclusões preservadas, da
conferência da retirada e da Auditoria da comissão subiu ao cabeçalho de contexto — a das filhas é a
da Distribuição com a tela no fim; o resultado do último envio sobe para logo abaixo do título em
Registrar ocorrência e nas Conclusões; Impedimentos ganha a seção "Registrar um impedimento"; e
"Filtrar" tem o desenho de ação principal na Trilha, na Auditoria da comissão e nas Conclusões.
Nenhuma regra da folha comum mudou.

O inventário foi refeito sobre a `main` em `fbe5bba3`, num banco próprio, `ps_inventario_080` —
cópia do `ps_inventario_telas` —, com o mesmo roteiro e o mesmo `AVISO`, nos dois estados da barra,
antes e depois da mudança. **O de antes não reproduz `depois-da-079/` em duas telas, por dado e não
por código**: a Auditoria da comissão tem as duas alocações que o percurso da `079` gravou depois da
captura dela (+359 px a 375, +132 a 1280), e o aviso, a hora da leitura. Nenhum arquivo de
`backend/processo_seletivo/` mudou entre o merge da `079` e `fbe5bba3`. A linha de base desta
comparação é, por isso, o de antes, guardado em
[`depois-da-080/antes/`](inventario-visual-da-gestao-2026-10-16/depois-da-080/antes/).

Em [`depois-da-080/`](inventario-visual-da-gestao-2026-10-16/depois-da-080/) estão o
`resultados.json` com a barra expandida, o de
[`recolhida/`](inventario-visual-da-gestao-2026-10-16/depois-da-080/recolhida/), e as capturas, a
1280 e a 375 px e com a barra expandida, das seis telas do escopo — e as de antes, em `antes/`. A
conferência da retirada não está no inventário — é a resposta a um envio —, e foi vista no navegador.

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-080/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-080/resultados.json
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-080/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-080/resultados.json
```

| | Antes da 080 | Depois da 080, expandida | Depois da 080, recolhida |
|---|---|---|---|
| Variantes que carregam | 84 de 85 | 84 de 85 | 84 de 85 |
| `status` diferente | — | nenhum | nenhum |
| Estouram a 375 px | 0 | 0 | 0 |
| Estouram a 1280 px | 0 | 0 | 0 |

**Só as telas da 080 mudaram de medida**, e só de altura — nenhuma largura, título ou `h1`. Com a
barra expandida:

| Tela | 1280 px | 375 px | Por quê |
|---|---|---|---|
| `trilha-da-avaliacao` | 1682 → 1645 | 3349 → 3347 | a trilha saiu do conteúdo |
| `auditoria-comissao` | 1233 → 1196 | 2649 → 2626 | a trilha saiu do conteúdo |
| `conclusoes-preservadas` | 1347 → 1310 | 1574 → 1572 | a trilha saiu do conteúdo |
| `resultados-da-etapa` | 901 → 900 | 1425 → 1423 | a trilha saiu; a 1280 a página cabe na janela |
| `impedimentos` | 900 → 900 | 992 → 1045 | a trilha saiu, e o título "Registrar um impedimento" entrou |
| `registrar-ocorrencia` | 900 → 900 | 812 → 812 | cabe na janela nas duas larguras; muda o desenho, não a medida |

Com a barra recolhida, as mesmas telas e as mesmas diferenças, menos as que a 1280 cabem na janela
(`conclusoes-preservadas` e `resultados-da-etapa` ficam em 900): `trilha-da-avaliacao` 1507 → 1470 e
`auditoria-comissao` 1154 → 1117.

**Pixel a pixel.** Fora das seis telas, as capturas de antes e de depois diferem só no que muda entre
duas capturas do mesmo código: a hora da leitura na Supervisão, na Visão Geral, nas dúvidas e no
pulso do Processo, e marcas de cursor e de suavização em Minhas Etapas, na devolução do ato e em
pontos isolados (até 4 de 255). É também o que o diff permite: ele só toca os seis templates do
escopo.

## Depois da 081

A [`081`](../specs/081-achados-das-revisoes-077-079/spec.md) corrigiu os achados das revisões da
`077` e da `079` que cabiam em apresentação: na Distribuição, "Consolidar as selecionadas" passou ao
desenho secundário, com a marca "irreversível" logo depois — o desenho dos atos do Processo —, e
"Distribuir as selecionadas" ficou como o único botão cheio sobre a seleção; na Alocação sem
presidência, o aviso diz "antes de alocar". A folha comum ganhou `align-self:center`
na própria marca, para ela não esticar em linha flexível. Na revisão do PR, a marca passou a descrever
o botão para o leitor de tela, e "Consolidar as N prontas" ganhou o mesmo desenho e a mesma marca.

O inventário foi refeito sobre a `main` em `cf6d7372`, num banco próprio, `ps_inventario_081` — cópia
do `ps_inventario_080` —, com o mesmo roteiro e o mesmo `AVISO`, nos dois estados da barra, antes e
depois da mudança. O de antes não difere em medida nenhuma de `depois-da-080/`, pelo `medidas.py`.

Em [`depois-da-081/`](inventario-visual-da-gestao-2026-10-16/depois-da-081/) estão os dois
`resultados.json`, de antes e de depois, com a barra expandida e recolhida, e as capturas da
Distribuição e da Alocação, a 1280 e a 375 px. A Alocação do banco do inventário tem presidência, e o
aviso não aparece nela: a frase é provada pelos testes.

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-081/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-081/resultados.json
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-081/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-081/resultados.json
```

| | Antes da 081 | Depois da 081, expandida | Depois da 081, recolhida |
|---|---|---|---|
| Variantes que carregam | 84 de 85 | 84 de 85 | 84 de 85 |
| `status` diferente | — | nenhum | nenhum |
| Estouram a 375 px | 0 | 0 | 0 |
| Estouram a 1280 px | 0 | 0 | 0 |

**Só a Distribuição mudou de medida**, e só a 375 px: 3306 → 3332, nos dois estados da barra. Ali os
dois botões já ficavam um sobre o outro, e a marca, que acompanha o segundo, ocupa uma linha a mais. A
1280 px a altura não muda (2168): a marca cabe na linha dos botões, centrada, e o botão secundário tem
a altura do principal (40 px, medido no navegador).

**Pixel a pixel.** Fora da Distribuição, as capturas de antes e de depois diferem só no que muda entre
duas capturas do mesmo código: a hora da leitura na Supervisão, na Visão Geral, nas dúvidas, no aviso
e no pulso do Processo, e marcas de cursor e de suavização em pontos isolados. O depois foi refeito
depois da revisão do PR, já em 18/10, e o pulso do Processo e as Autoridades mostram também a data
nova (a série de submissões passou de 2 para 3 dias). O detalhe do Processo, que também usa a marca,
a põe num `li` da `.lista-acoes`, que já centraliza: mover `align-self` para a marca não o move. O
botão das prontas não aparece no banco do inventário, que não tem inscrição pronta: é provado pelos
testes.

## Depois da 083

O quinto incremento da modernização por tela ([`083`](../specs/083-telas-do-edital/spec.md)) mudou as
telas que se abrem do detalhe do Edital e que a `078` não cobriu: em Novo Edital, Retificar, no
detalhe da Retificação e na conferência de cada ato, na Prévia, em Partir de um Edital anterior e na
conferência da troca, na Condução do marco e na conferência do gesto, na Prévia de publicação, nos
Resultados divulgados e na Auditoria do Edital, a trilha subiu ao cabeçalho de contexto, com o
Processo entre a seção e o Edital; a recusa do último envio sobe para logo abaixo do título em
Retificar e na Prévia de publicação; no detalhe da Retificação, "O que fazer agora" vem antes da
Vigência; e "Filtrar", em Partir de um Edital anterior, tem o desenho de ação principal. Nenhuma
regra da folha comum mudou.

O inventário foi refeito sobre a `main` em `cf6d7372`, num banco próprio, `ps_inventario_083` — cópia
do `ps_inventario_telas` —, com o mesmo roteiro e o mesmo `AVISO`, nos dois estados da barra, antes e
depois da mudança. O de antes é **idêntico**, campo a campo, a `depois-da-080/` (`comparar.py`: zero
variantes mudaram, nos dois estados), e está guardado em
[`depois-da-083/antes/`](inventario-visual-da-gestao-2026-10-16/depois-da-083/antes/).

Em [`depois-da-083/`](inventario-visual-da-gestao-2026-10-16/depois-da-083/) estão o
`resultados.json` com a barra expandida, o de
[`recolhida/`](inventario-visual-da-gestao-2026-10-16/depois-da-083/recolhida/), e as capturas, a
1280 e a 375 px e com a barra expandida, das telas do escopo — e as de antes, em `antes/`. Da
conferência de um ato da Retificação ficam duas das cinco variantes (publicar e submeter: o mesmo
template); de Retificar, só o topo, os primeiros 1400 px de uma página de 15 a 27 mil. As conferências
da troca de origem e do gesto do marco não estão no inventário — são a resposta a um envio —, e foram
vistas no navegador.

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-083/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-083/resultados.json
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-083/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-083/resultados.json
```

| | Antes da 083 | Depois da 083, expandida | Depois da 083, recolhida |
|---|---|---|---|
| Variantes que carregam | 84 de 85 | 84 de 85 | 84 de 85 |
| `status` diferente | — | nenhum | nenhum |
| Estouram a 375 px | 0 | 0 | 0 |
| Estouram a 1280 px | 0 | 0 | 0 |

**Só as telas da 083 mudaram de medida**, e só de altura — nenhuma largura, título ou `h1`. Com a
barra expandida:

| Tela | 1280 px | 375 px | Por quê |
|---|---|---|---|
| `retificar` | 14889 → 14852 | 26986 → 26984 | a trilha saiu do conteúdo |
| `retificacao-detalhe` | 900 → 900 | 1471 → 1469 | a trilha saiu; "O que fazer agora" trocou de lugar com a Vigência, sem mudar a soma, e os cartões vão pelo topo¹ |
| `retificacao-ato-publicar` | 1429 → 1392 | 2168 → 2166 | a trilha saiu do conteúdo |
| `retificacao-ato-devolver` | 966 → 929 | 1395 → 1393 | idem |
| `retificacao-ato-cancelar`, `-homologar` | 937 → 900 | 1300 → 1298 | idem; a 1280 a página passa a caber na janela |
| `retificacao-ato-submeter` | 900 → 900 | 1242 → 1240 | idem |
| `reaproveitar` | 1516 → 1479 | 2090 → 2088 | idem |
| `previa-de-publicacao` | 1282 → 1245 | 1901 → 1900 | idem |
| `auditoria` | 1033 → 996 | 2310 → 2309 | idem |
| `edital-criar` | 900 → 900 | 1071 → 1048 | idem; a trilha do conteúdo tinha duas linhas a 375 |
| `marco` | 900 → 900 | 1308 → 1285 | idem |
| `previa`, `publicacoes-do-marco` | 900 → 900 | sem mudança | cabem na janela; muda o desenho, não a medida |

¹ Recapturada depois da revisão do PR, com `SO=retificacao-detalhe` nos dois estados da barra: o
`ao-topo` muda o desenho a 1280 px (o cartão sem ato deixa de se esticar à altura da Vigência), e não
a medida.

Com a barra recolhida, as mesmas telas e as mesmas diferenças; mudam só as alturas de partida a 1280
(`reaproveitar` 1301 → 1264, `retificacao-ato-publicar` 1389 → 1352, `retificar` 13952 → 13915).

**Pixel a pixel.** Fora das telas do escopo, as capturas de antes e de depois diferem só no que muda
entre duas capturas do mesmo código: a hora da leitura nas Dúvidas, na Supervisão, na Visão Geral e
no pulso do Processo; o cursor de texto no título das Autoridades, com a barra recolhida; e
suavização em pontos isolados das Inscrições e das Conclusões preservadas (até 20 de 255). É também o
que o diff permite: ele só toca os doze templates do escopo.

## Depois da 084

Um dos três incrementos paralelos da modernização por tela ([`084`](../specs/084-telas-de-resultado-e-atos/spec.md))
mudou as telas de resultado e dos atos depois da inscrição: na Classificação, na conferência da
emissão, no Ato de classificação, no Sorteio, no Corte e no corte histórico, na Ocupação e no
histórico dela, na Convocação e no histórico dela e em Exportar para matrícula, a trilha subiu ao
cabeçalho de contexto — a do Edital, com os níveis que cada tela já tinha depois dele e a tela no
fim. Nada mais mudou: nenhum texto, nenhum botão, nenhuma regra da folha comum.

O inventário foi refeito sobre a `main` em `cf6d7372`, num banco próprio, `ps_inventario_084` —
cópia do `ps_inventario_telas` —, com o mesmo roteiro e o mesmo `AVISO`, nos dois estados da barra,
antes e depois da mudança. **O de antes reproduz `depois-da-080/` sem nenhuma variante diferente**,
nos dois estados; ele é a linha de base desta comparação, guardado em
[`depois-da-084/antes/`](inventario-visual-da-gestao-2026-10-16/depois-da-084/antes/).

Em [`depois-da-084/`](inventario-visual-da-gestao-2026-10-16/depois-da-084/) estão o
`resultados.json` com a barra expandida, o de
[`recolhida/`](inventario-visual-da-gestao-2026-10-16/depois-da-084/recolhida/), e as capturas, a
1280 e a 375 px e com a barra expandida, das dez telas do escopo que o inventário abre — e as de
antes, em `antes/`. A conferência da emissão não está no inventário — é a resposta a um envio —, e foi
vista no navegador.

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-084/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-084/resultados.json
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-084/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-084/resultados.json
```

| | Antes da 084 | Depois da 084, expandida | Depois da 084, recolhida |
|---|---|---|---|
| Variantes que carregam | 84 de 85 | 84 de 85 | 84 de 85 |
| `status` diferente | — | nenhum | nenhum |
| Estouram a 375 px | 0 | 0 | 0 |
| Estouram a 1280 px | 0 | 0 | 0 |

**Só as telas da 084 mudaram de medida**, e só de altura — nenhuma largura, título ou `h1`. Com a
barra expandida:

| Tela | 1280 px | 375 px | Por quê |
|---|---|---|---|
| `ordenacao` | 1360 → 1323 | 1959 → 1936 | a trilha saiu do conteúdo |
| `ato-de-ordenacao` | 1703 → 1666 | 2578 → 2577 | a trilha saiu; a 375, a do cabeçalho ganhou o Processo e o Edital, e o identificador do ato quebra em duas linhas |
| `sorteio` | 2593 → 2556 | 3550 → 3527 | a trilha saiu do conteúdo |
| `corte` | 1264 → 1227 | 2015 → 2013 | a trilha saiu do conteúdo |
| `corte-historico` | 1158 → 1121 | 1842 → 1819 | a trilha saiu do conteúdo |
| `ocupacao` | 1147 → 1110 | 1503 → 1480 | a trilha saiu do conteúdo |
| `ocupacao-historico` | 900 → 900 | 1138 → 1115 | a trilha saiu; a 1280 a página cabe na janela |
| `convocacao` | 2640 → 2603 | 3871 → 3848 | a trilha saiu do conteúdo |
| `exportar-matriculas` | 900 → 900 | 854 → 831 | a trilha saiu; a 1280 a página cabe na janela |
| `convocacao-historico` | 900 → 900 | 812 → 812 | cabe na janela nas duas larguras; muda o desenho, não a medida |

Com a barra recolhida, as mesmas telas e as mesmas diferenças; três partem, a 1280, de outra altura,
e perdem o mesmo: `ato-de-ordenacao` 1613 → 1576, `corte` 1240 → 1203 e `ordenacao` 1336 → 1299.

**Pixel a pixel.** Fora das dez telas, as capturas de antes e de depois diferem só no que muda entre
duas capturas do mesmo código: a hora da leitura na Supervisão, na Visão Geral, nas dúvidas e no
pulso do Processo, e marcas de suavização em pontos isolados da composição, das inscrições, da Mesa,
do recurso, dos avisos e da Retificação (até 28 de 255). É também o que o diff permite: ele só toca
os onze templates do escopo.

## Depois da 085

O sétimo incremento ([`085`](../specs/085-telas-de-inscricoes-e-recursos/spec.md)) mudou as telas de
inscrições e de recursos: a trilha das Inscrições, da Inscrição recebida, dos Recursos e do Recurso
subiu ao cabeçalho de contexto — a do Edital com a tela no fim, passando pelo Processo —; sem
inscrição recebida, a lista mostra o estado vazio; e os rascunhos são região nomeada. A tela de
recusa ficou fora (a decisão 002 da spec). Nenhuma regra da folha comum mudou.

O inventário foi refeito sobre a `main` em `cf6d7372`, num banco próprio, `ps_inventario_085` — cópia
do `ps_inventario_080` —, com o mesmo roteiro e o mesmo `AVISO`, nos dois estados da barra, antes e
depois da mudança. **O de antes reproduz `depois-da-080/`**: nenhuma variante muda de medida, nos dois
estados da barra. Ele está em [`depois-da-085/antes/`](inventario-visual-da-gestao-2026-10-16/depois-da-085/antes/);
em [`depois-da-085/`](inventario-visual-da-gestao-2026-10-16/depois-da-085/), o de depois, com
[`recolhida/`](inventario-visual-da-gestao-2026-10-16/depois-da-085/recolhida/), e as capturas, a 1280
e a 375 px e com a barra expandida, das cinco variantes do escopo, antes e depois.

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-085/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-085/resultados.json
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-085/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-085/resultados.json
```

| | Antes da 085 | Depois da 085, expandida | Depois da 085, recolhida |
|---|---|---|---|
| Variantes que carregam | 84 de 85 | 84 de 85 | 84 de 85 |
| `status` diferente | — | nenhum | nenhum |
| Estouram a 375 px | 0 | 0 | 0 |
| Estouram a 1280 px | 0 | 0 | 0 |

**Só as telas da 085 mudaram de medida**, e só de altura — nenhuma largura, título ou `h1`. Com a
barra expandida:

| Tela | 1280 px | 375 px | Por quê |
|---|---|---|---|
| `inscricao-recebida` | 1924 → 1887 | 2452 → 2450 | a trilha saiu do conteúdo |
| `inscricoes` | 1021 → 984 | 1336 → 1335 | a trilha saiu do conteúdo |
| `recurso-admitido` | 1527 → 1490 | 2108 → 2106 | a trilha saiu do conteúdo |
| `recurso-pendente` | 1067 → 1030 | 1670 → 1669 | a trilha saiu do conteúdo |
| `recursos` | 900 → 900 | 812 → 812 | cabe na janela nas duas larguras; muda o desenho, não a medida |

A 375 px a página quase não encurta: a trilha sai do conteúdo e cresce no cabeçalho, onde quebra em
duas ou três linhas. Com a barra recolhida, as mesmas diferenças, menos `inscricoes` a 1280, que cabe na
janela (900 → 900). O estado vazio das Inscrições não aparece: o Edital do inventário tem inscrições.

**Pixel a pixel.** Fora das cinco variantes, as capturas de antes e de depois diferem só no que muda
entre duas capturas do mesmo código: a hora da leitura na Supervisão, na Visão Geral, nas dúvidas e no
pulso do Processo, e pontos isolados de suavização (de 6 a 151 px, espalhados) na lista, em duas
confirmações da Retificação, no novo modelo de aviso e na Revisão da composição. O diff de
`backend/processo_seletivo/` toca os quatro templates do escopo e uma função de consulta.

## Depois da 086

O grupo das telas dos avisos aos candidatos ([`086`](../specs/086-telas-dos-avisos-aos-candidatos/spec.md))
mudou os Avisos aos candidatos de um Edital, o histórico de um aviso, a prévia (de resultado, de
chamada e de reenvio), a conferência da interrupção, os Modelos de aviso e a edição de um modelo: a
trilha subiu ao cabeçalho de contexto — as telas de um Edital passam pelo Processo, a prévia diz a
porta por onde se chegou, e os modelos começam na seção da barra —; os três estados vazios passaram a
`.vazio`, os botões de dois formulários a `.salvar`, e "Novo modelo" a `.acoes-do-painel`. Nenhuma
regra da folha comum mudou.

O inventário foi refeito sobre a `main` em `cf6d7372`, num banco próprio, `ps_inventario_086` —
cópia do `ps_inventario_telas` —, com o mesmo roteiro e o mesmo `AVISO`, nos dois estados da barra,
antes e depois da mudança. O de antes é igual, variante a variante, a `depois-da-080/`, e está em
[`depois-da-086/antes/`](inventario-visual-da-gestao-2026-10-16/depois-da-086/antes/).

Em [`depois-da-086/`](inventario-visual-da-gestao-2026-10-16/depois-da-086/) estão o
`resultados.json` com a barra expandida, o de
[`recolhida/`](inventario-visual-da-gestao-2026-10-16/depois-da-086/recolhida/), e as capturas, a
1280 e a 375 px e com a barra expandida, das nove variantes do escopo — e as de antes, em `antes/`. A
prévia da chamada continua fora do inventário (pede uma comunicação por publicação que o seed não
emite), e os estados vazios não aparecem nele (o banco tem resultado, aviso e modelos): foram vistos
no navegador e são provados pelos testes.

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-086/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-086/resultados.json
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-086/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-086/resultados.json
```

| | Antes da 086 | Depois da 086, expandida | Depois da 086, recolhida |
|---|---|---|---|
| Variantes que carregam | 84 de 85 | 84 de 85 | 84 de 85 |
| `status` diferente | — | nenhum | nenhum |
| Estouram a 375 px | 0 | 0 | 0 |
| Estouram a 1280 px | 0 | 0 | 0 |

**Só as telas da 086 mudaram de medida**, e só de altura — nenhuma largura, título ou `h1`. As telas
dos avisos têm a largura de leitura, e por isso as medidas são as mesmas nos dois estados da barra:

| Tela | 1280 px | 375 px | Por quê |
|---|---|---|---|
| `aviso` | 1188 → 1151 | 1674 → 1672 | a trilha saiu do conteúdo |
| `aviso-do-resultado` | 2031 → 1994 | 2819 → 2817 | a trilha saiu do conteúdo |
| `aviso-reenviar` | 1442 → 1405 | 2146 → 2144 | a trilha saiu do conteúdo |
| `aviso-interromper` | 900 → 900 | 902 → 948 | a trilha saiu, e os botões ganharam o rodapé, que a 375 quebra o rótulo |
| `avisos-do-edital`, `avisos-do-edital-antes` | 900 → 900 | 814 → 812 | a trilha saiu; a 1280 a página cabe na janela |
| `modelos-de-aviso` | 900 → 900 | 904 → 875 | a trilha saiu; a 1280 a página cabe na janela |
| `modelo-de-aviso` | 1288 → 1315 | 1837 → 1858 | a trilha saiu, e os botões ganharam o rodapé |
| `modelo-de-aviso-novo` | 1216 → 1243 | 1741 → 1762 | a trilha saiu, e os botões ganharam o rodapé |

**Pixel a pixel.** Fora das nove variantes, as capturas de antes e de depois diferem só no que muda
entre duas capturas do mesmo código — a hora da leitura na Supervisão, na Visão Geral, nas dúvidas e
no pulso do Processo, e marcas de suavização isoladas (até 39 de 255) —, nos dois estados da barra. É
também o que o diff permite: ele só toca os seis templates do escopo.

## Depois da 087

O último grupo da modernização por tela ([`087`](../specs/087-paineis-e-telas-de-apoio/spec.md)) mudou
os dois painéis e as telas de apoio: a trilha da Visão Geral e das Autoridades da unidade — a seção,
como página atual —, da Supervisão, da conferência dos atos do Processo, das Respostas do assistente
de dúvidas, do Assistente do Edital, da conferência dos atos do Edital e de Criar Processo Seletivo
subiu ao cabeçalho de contexto; a das telas do Edital passa pelo Processo; e "Perguntar" tem o
desenho de ação principal no Assistente. Nenhuma regra da folha comum mudou, e nenhum número entrou
nos painéis.

O inventário foi refeito sobre a `main` em `cf6d7372`, num banco próprio, `ps_inventario_087` — cópia
do `ps_inventario_080` —, com o mesmo roteiro e o mesmo `AVISO`, nos dois estados da barra, antes e
depois da mudança. **O de antes reproduz `depois-da-080/` em todas as medidas**, variante a variante,
nos dois estados.

Em [`depois-da-087/`](inventario-visual-da-gestao-2026-10-16/depois-da-087/) estão o `resultados.json`
com a barra expandida, o de [`recolhida/`](inventario-visual-da-gestao-2026-10-16/depois-da-087/recolhida/),
e as capturas, a 1280 e a 375 px e com a barra expandida, de uma variante por tela do escopo — as
conferências pela de encerrar o Processo e pela de publicar o Edital — e as de antes, em `antes/`.

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-087/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-087/resultados.json
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-087/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-087/resultados.json
```

| | Antes da 087 | Depois da 087, expandida | Depois da 087, recolhida |
|---|---|---|---|
| Variantes que carregam | 84 de 85 | 84 de 85 | 84 de 85 |
| `status` diferente | — | nenhum | nenhum |
| Estouram a 375 px | 0 | 0 | 0 |
| Estouram a 1280 px | 0 | 0 | 0 |

**Só as telas da 087 mudaram de medida**, e só de altura — nenhuma largura, título ou `h1`; 21
variantes, as mesmas nos dois estados da barra. Com a barra expandida:

| Tela | 1280 px | 375 px | Por quê |
|---|---|---|---|
| `supervisao` | 2077 → 2040 | 3089 → 3066 | a trilha saiu do conteúdo |
| `duvidas` | 1281 → 1244 | 1952 → 1950 | a trilha saiu; a 375 a do cabeçalho, mais longa, quebra em mais linhas |
| `assistente` | 900 → 900 | 906 → 898 | idem; a 1280 a página cabe na janela |
| `processo-criar` | 923 → 900 | 1343 → 1321 | a trilha saiu do conteúdo |
| `processo-ato-encerrar`, `-cancelar` | 967 → 930, 938 → 901 | 1528 → 1505, 1477 → 1454 | a trilha saiu do conteúdo |
| `processo-ato-ativar` | 900 → 900 | 885 → 862 | idem; a 1280 cabe na janela |
| `ato-submeter`, `ato-publicar` | 2082 → 2045, 2294 → 2257 | 3209 → 3186, 3551 → 3550 | a trilha saiu; a 375 a do cabeçalho tem cinco níveis |
| `ato-homologar`, `-devolver`, `-revogar-homologacao`, `-encerrar`, `-cancelar` | 900 → 900 | entre −1 e −23 | idem; a 1280 cabem na janela |
| `visao-geral`, `autoridades` | sem mudança | sem mudança | o texto do cabeçalho virou trilha de um nível, da mesma altura; não havia trilha no conteúdo |

Com a barra recolhida, as mesmas 21 variantes e as mesmas diferenças; só `duvidas` a 1280 parte de
outra altura (1257 → 1220).

## Depois da 088

As quatro decisões do usuário de 18/10/2026 ([`088`](../specs/088-decisoes-da-etapa-4/spec.md)): a
trilha do cabeçalho de contexto passa a sair no papel; o rótulo do aviso na trilha ganha a hora; e
"Classificação", na trilha do Ato, leva ao recorte do ato. A quarta — o landmark sem link da lista e
de Minhas Etapas — não muda nada.

O inventário foi refeito sobre a `main` em `c97ff8af` (com a `081` à `087`), num banco próprio,
`ps_inventario_088` — cópia do `ps_inventario_080` —, com o mesmo roteiro e o mesmo `AVISO`, nos dois
estados da barra, antes e depois da mudança. Em
[`depois-da-088/`](inventario-visual-da-gestao-2026-10-16/depois-da-088/) estão os dois
`resultados.json`, as capturas das telas que a feature toca — os três avisos e o Ato — e as de antes,
em `antes/`.

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-088/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-088/resultados.json
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-088/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-088/resultados.json
```

| | Antes da 088 | Depois da 088, expandida | Depois da 088, recolhida |
|---|---|---|---|
| Variantes que carregam | 84 de 85 | 84 de 85 | 84 de 85 |
| `status` diferente | — | nenhum | nenhum |
| Estouram a 375 px | 0 | 0 | 0 |
| Estouram a 1280 px | 0 | 0 | 0 |

**Na tela, só uma variante mudou de medida**: `aviso-reenviar` a 1280 px, com a barra expandida,
1405 → 1419 — o rótulo do aviso anterior, agora com a hora, leva a trilha a uma segunda linha. No
histórico e na interrupção o rótulo cabe na mesma linha; com a barra recolhida, nenhuma variante
muda. A regra de impressão não mexe em medida nenhuma da tela.

### No papel

O [`imprimir.py`](inventario-visual-da-gestao-2026-10-16/imprimir.py), no mesmo banco, abre seis
telas, emula a mídia de impressão, lê o que fica visível do cabeçalho e da barra, e imprime cada uma
em A4 pelo Chrome sem interface. Os resultados, as capturas com a mídia emulada (`--papel`) e a
primeira página de cada PDF (`--a4`) estão em
[`depois-da-088/impressao/`](inventario-visual-da-gestao-2026-10-16/depois-da-088/impressao/), e os
de antes em `impressao/antes/`.

| Tela | Antes, no papel | Depois, no papel, antes do título |
|---|---|---|
| Inscrição da Mesa | nada | GPS › Minhas Etapas › Minha Mesa › Inscrição INS-2026-AF86BE7601 |
| Ato de classificação | nada | GPS › Processos Seletivos › PS-DEMO-2026 › Edital 51/2026 › Classificação › Ato … |
| Inscrição recebida | nada | GPS › Processos Seletivos › PS-DEMO-2026 › Edital 51/2026 › Inscrições › INS-2026-AF86BE7601 |
| Recurso | nada | GPS › Processos Seletivos › PS-DEMO-2026 › Edital 51/2026 › Recursos › REC-2026-K97GMU9C |
| Aviso | nada | GPS › … › Avisos aos candidatos › Aviso de 16/10/2026 às 16:19 |
| Recusa (cabeçalho da `076`) | nada | GPS › Processos Seletivos |

Nas seis, a barra lateral e "Trocar identidade" continuam fora do papel. No Ato, a trilha não cabe
numa linha do A4 e quebra no identificador do ato, sem cortar nível. Com a mídia emulada a 1280 px, a
coluna da barra continua pintada na `.shell` — fio e fundo cinza a 16rem —, como antes da `088`; no
A4, que é mais estreito que a largura em que a regra da coluna vale, ela não aparece.
