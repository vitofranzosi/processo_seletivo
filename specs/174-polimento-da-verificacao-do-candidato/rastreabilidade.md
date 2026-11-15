# Rastreabilidade — 174 · O polimento das telas do candidato na verificação por vídeo

**Frase que governa**: *forma, e não comportamento — o que se grava e o que se envia ficam como estão.*

Caminhos de código relativos a `backend/processo_seletivo/`. As abreviações dos arquivos de teste:

- **PV** — `tests/portal/test_verificacao_por_video.py` (as páginas renderizadas)
- **VP** — `tests/portal/test_vocabulario_do_passo.py` (a varredura do candidato)
- **NV** — `tests/navegador/test_jornada_do_video.py` (a jornada com câmera simulada, a 375, 768, 1280 e
  1920 px)
- **JS** — `tests/javascript/gravacao.test.js` (as funções puras do script)
- **DU** — `tests/unit/portal/test_duracao_do_video.py`
- **MS** — `tests/unit/verificacao/test_modalidade_na_situacao.py`
- **166** — os testes de envio e de contrato da `166` (`tests/integration/verificacao/`,
  `tests/unit/verificacao/test_conteiner.py`, `test_r11.py`, `test_roteiro_e_intervalo.py`), que não
  mudaram
- **G** — os guardiões de folha e de acessibilidade (`tests/interface/test_acessibilidade.py`,
  `test_acessibilidade_do_portal.py`, `test_folha_estatica.py`, `test_politica_de_conteudo.py`)
- **doc** — `doc/polimento-da-verificacao-2026-11/` (capturas e registros)
- **humano** — pendente de verificação por pessoa

---

## Requisitos funcionais

| Requisito | Onde entrou | Teste |
|---|---|---|
| FR-7850 | `.jornada` em `portal/templates/portal/verificacao.html` e `verificacao_comprovante.html`; `portal.css` | NV (margens), PV |
| FR-7851 | `.jornada .principal` com `--controle-g`; `.acoes-da-tela`; `.forma-acao` iguais | NV, PV |
| FR-7852 | `h1` com `situacao.nome_da_etapa`; `ol.jornada-momentos`; `MOMENTO_DA_TELA` em `gravacao.js` | PV, NV (`aria-current`) |
| FR-7853 | `Situacao.modalidade` (`verificacao/application/disponibilidade.py`); `alcance.nome_da_modalidade` | PV, MS |
| FR-7854 | `.jornada [hidden]{display:none !important}` | NV (escondidos), PV |
| FR-7855 | tokens `--coluna`, `--raio-pilula`, `--controle-g` em `shared/static/shared/tokens.css`; nenhum estilo ou script no template | G |
| FR-7856 | `.rotulo-da-situacao` em pílula com ícone (`portal/_icone.html`) | PV, NV |
| FR-7857 | `Situacao.prazo_do_passo` em `portal/situacao.py`; `.prazo-do-passo` | PV |
| FR-7858 | `ESCOLHER_VIDEO_OU_AO_VIVO` em `portal/situacao.py` | PV, NV |
| FR-7859 | as frases da `171` intactas em `_situacao_do_passo` | `tests/unit/portal/test_situacao_do_passo.py`, VP |
| FR-7860 | `article.forma` × 2 | PV |
| FR-7861 | prazo e substituição acima dos cartões | PV |
| FR-7862 | "Voltar ao acompanhamento" como principal em `ao-vivo`, `menor`, `nao-consigo` | PV |
| FR-7863 | `ul.preparo` com o documento | PV |
| FR-7864 | `section.quem-ve` com as quatro frases | PV |
| FR-7865 | `.opcao-grande`; a recusa e o foco em `gravacao.js` | NV |
| FR-7866 | `data-tela="palco"`; "Continuar" chama `abrirCamera()` | PV, NV |
| FR-7867 | `ol.passos-do-roteiro` só com títulos, escondido gravando | NV |
| FR-7868 | `.faixa-de-cima`, `desenharPassos()` | NV, JS (`rotuloDoPasso`) |
| FR-7869 | `.proximo`, o foco em `avancar()` | NV (Espaço e toque) |
| FR-7870 | `aceitaAvanco()` | JS |
| FR-7871 | `.linha-do-selo`, `.recomecar` | NV (captura) |
| FR-7872 | `.oval` com `cq*`; `.guia-do-oval` | NV (captura) |
| FR-7873 | `medirSom()`, `ouviuFala()`, `data-estado-do-som` | JS |
| FR-7874 | a frase do espelho no preparo | PV |
| FR-7875 | `.palco-da-gravacao` fixo abaixo de 40rem; "Começar a gravar", "Próximo" e "Não consigo" na `.faixa-de-baixo` | NV (375 px) |
| FR-7876 | `.palco` em 16:9 na coluna; `scrollIntoView` ao entrar | NV (768, 1280, 1920) |
| FR-7877 | `pedirTelaAcesa()` e `soltarTelaAcesa()`; `data-aviso-tela-acesa` | humano (aparelho real) |
| FR-7878 | `@media (orientation:landscape) and (max-height:30rem)` | humano (aparelho real) |
| FR-7879 | `@media (prefers-reduced-motion:reduce)` | G |
| FR-7880 | `aoParar()` com `duracaoPorExtenso` e `megabytes` | NV, JS |
| FR-7881 | a porcentagem por extenso no envio; a frase de não fechar | NV |
| FR-7882 | `verificacao_comprovante.html` na ordem nova | PV, NV |
| FR-7883 | `portal/templatetags/duracao_do_video.py` | DU, PV, JS |
| FR-7884 | `@media print` no bloco da `166` | humano (impressão) |
| FR-7885 | a frase da eliminação na confirmação | PV |
| FR-7886 | a situação sem gravação na moldura | PV |
| FR-7887 | nenhum arquivo de envio, rota ou contrato mudou | 166, NV (corpo do envio) |
| FR-7888 | a chave sem mudança | PV (`test_com_a_chave_desligada_*`) |
| FR-7889 | `politica_de_conteudo.py` sem mudança | PV, G |
| FR-7890 | nenhuma leitura de imagem; o medidor é nível de sinal | revisão; o guardião de visão computacional da `166` |
| FR-7891 | as frases novas nas telas da varredura | VP |
| FR-7892 | — | humano (quickstart, passo 5) |
| FR-7893 | `doc/polimento-da-verificacao-2026-11/antes` e `depois` | doc |

A faixa reservada além do último requisito gasto (até o requisito sete mil oitocentos e noventa e nove)
não foi usada.

## Critérios de sucesso

| Critério | Como se mede | Onde |
|---|---|---|
| SC-2650 | margens iguais a 768, 1280 e 1920 px | NV |
| SC-2651 | o palco na altura da janela; instrução, "Próximo" e "Não consigo" à vista | NV (375 px) |
| SC-2652 | zero gestos entre "Continuar" e "Começar a gravar" | NV |
| SC-2653 | nenhum `[hidden]` visível | NV |
| SC-2654 | o corpo do início do envio | NV, 166 |
| SC-2655 | aparelho real | humano |
| SC-2656 | contraste calculado ≥ 4,5:1 | NV |
| SC-2657 | política de conteúdo igual; nada embutido | PV, G |
| SC-2658 | três pessoas de fora da equipe | humano |
| SC-2659 | a confirmação no primeiro quadro, os dados depois | NV, PV |

## Requisitos de experiência

| Requisito | Onde |
|---|---|
| UX-870 | as frases de `contracts/telas.md`; VP |
| UX-871 | `.faixa-de-baixo`; NV a 375 px |
| UX-872 | `.faixa-de-cima` sobre a prévia |
| UX-873 | o selo "Gravando", "Passo N de 4", o ícone do provisório |
| UX-874 | `--controle-g`, `.opcao-grande`, `.recomecar` com 32 px |
| UX-875 | `data-anuncio`; NV |
| UX-876 | as frases da `166` mantidas; PV |
| UX-877 | o selo sem tracejado, o oval sem tracejado; doc |

A faixa reservada dos critérios (até o dois mil seiscentos e sessenta e nove) e dos requisitos de
experiência (até o oitocentos e oitenta e nove) não foi usada além do listado.
