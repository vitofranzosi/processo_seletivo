# Rastreabilidade: Conferência com o documento à vista

Cada requisito, critério e requisito de experiência da [spec](spec.md), com o que o cobre. Caminhos
relativos a `backend/`. Abreviações: **CV** = `tests/interface/test_conferencia_com_o_documento_a_vista.py`;
**MV** = `tests/interface/test_mesa_visualizador.py`; **AP** = `tests/integration/avisos/test_aviso_de_uma_pessoa.py`;
**JS** = `tests/javascript/visualizador.test.js`; **CC** = `tests/unit/interface/test_conducao_da_convocacao.py`;
**QS** = verificação no navegador pelo [quickstart](quickstart.md).

## Requisitos funcionais

| Requisito | Onde se cumpre | Coberto por |
|---|---|---|
| FR-6500, FR-6544 | `portal/arquivos.py` (`entregar_e_registrar_ao_fim`), `documento_da_convocacao` | CV: abertura só depois do último bloco; entrega igual; a abertura ao fim autoriza o conforme |
| FR-6501 | `visualizador.js` (nada sem clique) | JS: nada é pedido sem clique; CV: entrar na página não abre arquivo |
| FR-6502 | `visualizador.js` (`pdfViewerEnabled`) | JS: a alternativa sem moldura |
| FR-6503 | rota do cartão; `visualizador.js` (`reler`) | CV: o cartão relido traz a marca; JS: releitura depois da entrega |
| FR-6504 | `@xframe_options_sameorigin` | CV: `X-Frame-Options: SAMEORIGIN` |
| FR-6505 a FR-6509 | `convocacao_documentos.html`, `visualizador.js`, `grupos/visualizador.css` | CV: a página traz o painel; JS: abrir no painel; QS |
| FR-6510 | `_recusa_no_painel.html`, ramo `?painel=1` | CV: recusa por integridade e indisponível no painel; JS: a recusa sobe para o painel |
| FR-6511 | `visualizador.js` (`aReler`, `voltou`) | JS: na volta, o cartão é relido |
| FR-6512 | `_arquivos_dos_documentos`, `data-tamanho` | CV: `data-tamanho`; JS: "Carregando o documento (1,2 MB)…" |
| FR-6513 | ajuda recolhida do cartão | CV: UX-645 na página |
| FR-6514, FR-6515 | `conferir_documento_view` (HX), `_conferencia_sem_recarga` | CV: registrar sem recarga; envio duplicado |
| FR-6516 | parcial do cartão; `HX-Refresh` | CV: recusa no cartão com o preenchimento; recusa sem cartão; `test_recusa_da_conferencia_documental.py` |
| FR-6517 | `method="post"` mantido | CV: sem htmx, o caminho de sempre |
| FR-6518 | `_mensagem_do_formulario`; `htmx:sendError` | CV: sem identidade; JS: falha de rede |
| FR-6519 a FR-6522 | `_confirmacao_da_conferencia`, `_confirmacao_da_conferencia.html` | CV: a confirmação oferece o próximo sem abri-lo; ao fim da pessoa |
| FR-6523 a FR-6525 | `visualizador.js` (foco, região viva) | JS: foco no título, no formulário ao fechar, na recusa, no retorno |
| FR-6526 | folhas da página | QS (320 px e 200 %) |
| FR-6527 a FR-6530 | `visualizador.js` (fora da página, `sessionStorage`) | JS: abaixo da tela larga; volta; recarga restaurada; não sobrescreve |
| FR-6531 | estáticos | CV: sem `style=` nem `<script>` embutido; `test_estaticos`, `test_acessibilidade` |
| FR-6532 | — | a suíte inteira (`make test-pg`) |
| FR-6533 | `visualizador.js` nas duas telas | JS: a barra; MV: a página usa o visualizador |
| FR-6534 | `conferir` não chama o aviso | CV e AP: registrar a pendência não grava aviso |
| FR-6535, FR-6536 | confirmação; `_situacao_dos_documentos.html` (oob) | CV: ao fim da pessoa com pendência; o fragmento diz o que a página diria |
| FR-6537 a FR-6542 | `pendencias.py` (`convocacao_id`), `pedir_aviso_de_pendencia_view` | AP: o mesmo aviso; limite comum; motivo e data; chave desligada; trilha; CV: pedir aviso |
| FR-6543 | `conducao_da_convocacao.frase_do_aviso` | CC: os três grupos, um caso por estado |
| FR-6545 | `documento_da_mesa` (`?painel=1`) | MV: recusa legível no painel |
| FR-6546 | `mesa_inscricao.html`, `visualizador.js` | MV: o download na barra; JS: alternativa |
| FR-6547 | rota `mesa-documentos`; `visualizador.js` | MV: a lista relida; JS: a volta na Mesa |
| FR-6548 | `documento_da_mesa` grava antes, como antes | MV: a abertura da Mesa continua registrada; `tests/integration/avaliacoes/` |
| FR-6549 | ajuda recolhida (UX-652) | CV: "Não comprova que ele foi exibido nem lido." |

## Critérios de sucesso

| Critério | Coberto por |
|---|---|
| SC-2140 | QS (contagem de gestos no C09) |
| SC-2141 | CV: a abertura ao fim autoriza o conforme; sem abertura, recusa |
| SC-2142 | JS: nada sem clique; CV: oferecer não é abrir |
| SC-2143 | JS: a alternativa |
| SC-2144 | CV: recusa por integridade no painel |
| SC-2145 | CV: envio duplicado |
| SC-2146 | CV: o fragmento diz o que a página recarregada diria |
| SC-2147 | QS (1440, 1280, 390, 320) |
| SC-2148 | CV: sem htmx, o caminho de sempre; QS sem script |
| SC-2149 a SC-2151 | verificação humana (pendente) |
| SC-2152 | AP: o mesmo aviso; limite comum |
| SC-2153 | CV: o fragmento e a página; CC |
| SC-2154 | AP: motivo e data só no "já avisada hoje" |
| SC-2155 | CV: abertura só depois do último bloco; recusa não é abertura |
| SC-2156 | JS: volta com e sem recarga |
| SC-2157 | MV: recusa legível no painel |
| SC-2158 | MV e `tests/integration/avaliacoes/` (avaliar sem abrir) |
| SC-2159 | verificação humana (pendente) |

## Requisitos de experiência

| Requisito | Coberto por |
|---|---|
| UX-640, UX-641 | CV: a página traz o painel e os links; JS: barra e título |
| UX-642, UX-647 | CV: confirmação |
| UX-643, UX-644 | JS: a alternativa; o carregamento |
| UX-645, UX-652 | CV: a ajuda recolhida |
| UX-646 | CV: sem identidade; JS: falha de rede |
| UX-648 a UX-650 | CV: pedir aviso; CC; AP |
| UX-651 | CV e `test_recusa_da_conferencia_documental.py` |
| UX-653 | JS: o retorno e a restauração |
| UX-654 | CV e MV: recusa no painel |
