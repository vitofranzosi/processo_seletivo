# Rastreabilidade — 176 · A detecção do giro do rosto na gravação do vídeo

**Frase que governa**: *o aparelho estima o giro para guiar; nada dessa leitura sai dele, e o toque vale sempre.*

Caminhos de código relativos a `backend/processo_seletivo/`. As abreviações dos arquivos de teste:

- **DG** — `tests/portal/test_deteccao_do_giro.py` (o manifesto, as chaves, a política e a página)
- **SI** — `tests/test_sem_inferencia_sobre_o_video.py` (o guardião da FR-7150 da `166`, ampliado)
- **JD** — `tests/javascript/deteccao.test.js` (as funções puras e o vigia simulado)
- **JG** — `tests/javascript/gravacao.test.js` (a imagem de teste que gira)
- **NV** — `tests/navegador/test_jornada_do_video.py` (o motor de verdade, a escolha de tocar e os perfis
  com a imagem de teste, a 375 e a 1280 px)
- **CP** — `tests/test_configuracao_producao.py` (a recusa em produção)
- **G** — os guardiões que passaram a ler o motor copiado (`tests/test_armazenamento_no_navegador.py`,
  `tests/interface/test_politica_de_conteudo.py`)
- **166** — os testes de envio e de contrato da `166`, que não mudaram
- **doc** — `doc/deteccao-do-giro-2026-11/` (medidas e bancada)
- **humano** — pendente de verificação por pessoa

---

## Requisitos funcionais

| Requisito | Onde entrou | Teste |
|---|---|---|
| FR-8000 | `portal/static/portal/deteccao.js` (leituras só na memória, no máximo 20); nada no envio | NV (sem pedido a outra origem; corpo do envio), SI (sem registrador de uso) |
| FR-8001 | `giroDosPontos`, `caixaDosPontos`; `outputFaceBlendshapes: false` | JD |
| FR-8002 | o servidor sem visão computacional | SI |
| FR-8003 | `desligarDeteccao` ao sair do palco; `Vigia.parar` | SI (só a gravação), DG (comprovante e acompanhamento sem o motor) |
| FR-8004, FR-8005 | `[data-aviso-deteccao]` em `verificacao.html`; `soTocando` em `gravacao.js` | DG, NV |
| FR-8006 | as frases do contrato | DG |
| FR-8010 | `rostoNoOval`; `aoRosto`; `.oval[data-rosto="dentro"]` | JD, NV |
| FR-8011 | `avaliarGiro`, `LIMIAR_DO_GIRO`, `INSTANTE_MANTIDO` | JD |
| FR-8012 | `aoGiro` (confirmação e `avancar()`); o prefixo do anúncio | NV |
| FR-8013 | sem `data-giro` no documento e na frente; `[data-ouvindo]` | DG, NV (a frente não termina sozinha) |
| FR-8014 | `avancar()` cancela a confirmação; `aceitaAvanco` da `174` | NV (motor sem rosto, pelo toque) |
| FR-8015 | "Para o outro lado" | JD |
| FR-8016 | `Vigia.carregar` depois do palco; estados `indisponivel` e `desligada` | NV, JD |
| FR-8017 | `Orcamento`; o aquecimento no carregamento | JD, doc |
| FR-8018 | `podeCarregar` com `saveData` | JD |
| FR-8020 | `portal/deteccao.py` (`ligada`); `config/settings/base.py`, `test.py` | DG |
| FR-8021 | `config/settings/production.py` | CP |
| FR-8022 | `shared/politica_de_conteudo.py` (`compilar_wasm`) | DG, NV (sem violação) |
| FR-8023 | `portal/deteccao.py` (`ARQUIVOS`); `portal/static/portal/deteccao/` | DG, SI |
| FR-8024 | o guardião ampliado | SI |
| FR-8030 | nenhum campo novo no envio | DG, NV, 166 |
| FR-8031 | nada da detecção no vídeo nem na trilha | DG |
| FR-8032 | o oval e a confirmação por CSS, sobre a prévia; nenhum ponto desenhado | NV (capturas) |
| FR-8033 | as frases novas na página da gravação | DG |
| FR-8040 | `giroDaImagemDeTeste` e `estado.sintetica.ler` em `gravacao.js` | JG, NV |
| FR-8041 | a bancada e as medidas | doc |
| FR-8042 | `doc/verificacao-por-video-porta-do-piloto.md` | doc |

## Requisitos de experiência

| Requisito | Onde entrou | Teste |
|---|---|---|
| UX-920 | "Perfil esquerdo visto" | NV |
| UX-921 | `.confirmacao-do-giro`, na faixa da instrução | NV (capturas) |
| UX-922 | o traço do oval e a frase mudam juntos | NV |
| UX-923 | tudo `hidden` até a detecção estar pronta; a ajuda da `174` volta sem ela | DG, NV |
| UX-924 | nenhuma frase de falha | DG |

## Critérios de sucesso

| Critério | Como se verifica |
|---|---|
| SC-2750 | NV: dois toques além de "Começar a gravar", com a imagem de teste |
| SC-2751 | DG: sem a chave, a página e a política da `174`; NV: sem rosto, pelo toque |
| SC-2752 | NV: as chaves e as marcas do corpo do envio |
| SC-2753 | doc, **humano** (celular de entrada) |
| SC-2754 | NV: nenhum pedido a outra origem; cada arquivo do motor uma vez |
| SC-2755 | doc: 15,4 MB sem compressão, cerca de 6,7 MB com gzip |
| SC-2756 | DG, SI |
| SC-2757 | **humano** (câmera real; a bancada de `doc/deteccao-do-giro-2026-11/`) |
| SC-2758 | NV (motor sem rosto, pelo toque) e **humano** |
