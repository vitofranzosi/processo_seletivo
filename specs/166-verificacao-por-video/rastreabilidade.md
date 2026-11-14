# Rastreabilidade — 166 · A verificação da autodeclaração por vídeo

**Frase que governa**: *o vídeo só confirma: ou a deliberação pelo vídeo confirma, ou a inscrição vai
à entrevista ao vivo — e só ela pode concluir pela não confirmação.*

Caminhos de código relativos a `backend/processo_seletivo/`. As abreviações dos arquivos de teste:

- **UV** — `tests/unit/verificacao/` (contêiner, roteiro, intervalo, R-11 com cinco pareceres)
- **UP** — `tests/unit/editais/test_video_na_publicacao.py`
- **TC** — `tests/interface/test_composicao_do_video.py`
- **IE** — `tests/integration/verificacao/test_envio.py`
- **IM** — `tests/integration/verificacao/test_mesa_e_r11.py`
- **IR** — `tests/integration/verificacao/test_r11_por_regra.py`
- **IT** — `tests/integration/verificacao/test_retencao_e_gatilhos.py`
- **IG** — os gatilhos append-only, no mesmo arquivo, e `tests/integration/test_database_permissions.py`
- **PV** — `tests/portal/test_verificacao_por_video.py`
- **PR** — `tests/test_configuracao_producao.py`
- **GR** — `tests/test_sem_inferencia_sobre_o_video.py`
- **JS** — `tests/javascript/gravacao.test.js`
- **G** — os guardiões que o campo novo atravessou (migrations, elevação, homologação preservada)
- **navegador** — a jornada no painel com a imagem de teste (`quickstart.md`, passo 3)

---

## Requisitos funcionais

| Requisito | Onde entrou | Teste |
|---|---|---|
| FR-7100 | `config/settings/base.py`, `verificacao/application/envio.py`, `portal/verificacao.py` | IE, PV |
| FR-7101 | `config/settings/production.py` | PR |
| FR-7102 | `editais/models/etapas.py`, `verificacao/domain/admissao.py`, `publicacoes/domain/elevacao.py` | UP, TC, G |
| FR-7103 | `editais/domain/validation.py` (`_coerencia_do_video`) | UP |
| FR-7104 | `editais/domain/validation.py`, `publicacoes/application/retificacoes.py`, `_etapa.html` | UP, TC |
| FR-7105 | `publicacoes/application/retificacoes.py` (`_recusar_video_retirado_apos_recebido`) | IE (indireta; ver *Pendências*) |
| FR-7106 | `verificacao/domain/admissao.py` (`frase`), `pdf.py`, `apresentacao.py`, `revisao.py` | UP, TC |
| FR-7107 | `verificacao/application/disponibilidade.py` | IE |
| FR-7108 | `portal/templates/portal/verificacao.html` | PV |
| FR-7109 | `verificacao/application/envio.py` (`_validar_declaracao`), `verificacao.html` | IE, PV |
| FR-7110 | `verificacao/application/envio.py` (`contexto_do_titular`) | IE, PV |
| FR-7111 | `portal/static/portal/gravacao.js` | JS, navegador |
| FR-7112 | `verificacao/domain/roteiro.py` | UV, IE |
| FR-7113 | `verificacao/domain/roteiro.py` (`conferir_marcas`), `gravacao.js` | UV, JS |
| FR-7114 | `verificacao.html` (`.oval`), `portal.css` | navegador |
| FR-7115 | `gravacao.js` (`visibilitychange`) | navegador |
| FR-7116 | `gravacao.js` (`regravar`) | navegador |
| FR-7117 | `shared/politica_de_conteudo.py` (`com_midia_local`), `portal/verificacao.py` | PV |
| FR-7118 | `verificacao/application/envio.py` (`receber_parte`), `portal/verificacao.py` (`parte`) | IE, JS |
| FR-7119 | `envio.py` (`consultar`), `gravacao.js` (`Envio.retomar`) | IE, JS |
| FR-7120 | `verificacao/domain/conteiner.py`, `envio.py` (`concluir`) | UV, IE |
| FR-7121 | `verificacao/models.py` (`VideoDaVerificacao`), `envio.py` | IE, IG |
| FR-7122 | `config/settings/base.py` (`VERIFICACAO_POR_VIDEO_LIMITE_BYTES`) | IE |
| FR-7123 | `portal/templates/portal/verificacao_comprovante.html` | PV |
| FR-7124 | `envio.py` (`_recusar_se_indisponivel`), `abertura.py` | IE, IM |
| FR-7125 | `envio.py` (`iniciar`) | IE |
| FR-7126 | `disponibilidade.py` (`TOLERANCIA`), `envio.py` | IE (indireta) |
| FR-7127 | `abertura.py` (`abrir_pelo_titular`), `portal/verificacao.py` | IM, PV |
| FR-7128 | `interface/templates/interface/_video_da_mesa.html`, `verificacao/application/mesa.py` | IM |
| FR-7129 | `abertura.py` (`abrir_pela_comissao`, `entregar_a_comissao`) | IM |
| FR-7130 | `abertura.py`, `AberturaDoVideo` | IM |
| FR-7131 | `verificacao/infrastructure/entrega.py`, `verificacao/domain/intervalo.py` | UV, IM |
| FR-7132 | `interface/static/interface/video_da_mesa.js`, `_video_da_mesa.html` | IM, navegador |
| FR-7133 | `verificacao/application/mesa.py` (`CONFIRMO`, `NAO_DA`), `interface/views.py` | IM |
| FR-7134 | `verificacao/application/ganchos.py` (`exigir_abertura_para_concluir`), `avaliacoes/application/avaliacao.py` | IM |
| FR-7135 | sem mudança na `165`: a Mesa não mostra parecer alheio | IM |
| FR-7136 | `resultados/application/consolidacao.py` (`_planejar`), `ganchos.py` | IM, IR |
| FR-7137 | `consolidacao.py` | IM, IR |
| FR-7138 | `consolidacao.py`, `consolidacao_confirmar.html`, `encaminhar_ao_vivo.html` | IM, IR |
| FR-7139 | `ganchos.py` (`recusar_desfavoravel_pelo_video`), `consolidacao.py`, `recursos/application/julgar.py` | IM, IR |
| FR-7140 | `verificacao/application/encaminhamento.py`, `interface/verificacao.py` (`encaminhar`) | IM |
| FR-7141 | `encaminhamento.py` (reabertura da `012`) | IM |
| FR-7142 | `encaminhamento.py`, `disponibilidade.py` | IM |
| FR-7143 | `EncaminhamentoAoVivo` (`uq_um_encaminhamento`) | IM |
| FR-7144 | `disponibilidade.py`, `_verificacao_por_video.html` | IM |
| FR-7145 | `portal/templates/portal/_verificacao_por_video.html`, `portal/views.py` (`acompanhamento`) | PV |
| FR-7146 | `config/settings/base.py`, `verificacao/application/retencao.py` | IT |
| FR-7147 | `retencao.py`, `eliminar_videos_da_verificacao.py` | IT |
| FR-7148 | `retencao.py`, `EliminacaoDoVideo` | IT |
| FR-7149 | `verificacao_comprovante.html`, `_video_da_mesa.html`, `abertura.py` | IT (indireta) |
| FR-7150 | `tests/test_sem_inferencia_sobre_o_video.py` | GR |
| FR-7151 | `envio.py`, `abertura.py`, `encaminhamento.py`, `retencao.py` (`detalhe` sem conteúdo) | IE, IM, IT |
| FR-7152 | travas da inscrição em `envio.py`, `abertura.py`, `ganchos.py`; `uq_um_envio_por_inscricao`, `substitui` único | IE |
| FR-7153 | `doc/verificacao-por-video-porta-do-piloto.md` | — |

## Critérios de sucesso

| Critério | Como se mede | Teste |
|---|---|---|
| SC-2370 | a jornada no navegador, a 375 px, console sem violação | navegador |
| SC-2371 | resumo final igual ao do aparelho, com retomada | IE, JS |
| SC-2372 | um evento por abertura com N pedidos `Range` | IM |
| SC-2373 | zero desfavoráveis pelo vídeo nas três regras | IR, UV |
| SC-2374 | nenhum byte a quem não tem a Atribuição | IM |
| SC-2375 | sem prazo, zero eliminados | IT |
| SC-2376 | chave desligada fecha o portal; produção recusa | PV, IE, PR |
| SC-2377 | a matriz de navegadores com câmera real | **humano, aberto** |

## Requisitos de experiência

| Requisito | Onde entrou | Teste |
|---|---|---|
| UX-770 | `verificacao.html`, `admissao.frase`, `_etapa.html` | PV, UP |
| UX-771 | `portal.css` (coluna única, 375 px) | navegador |
| UX-772 | `verificacao.html` (`aria-live`, «Não consigo usar a câmera») | PV, navegador |
| UX-773 | `verificacao.html`, `verificacao_comprovante.html` | PV |
| UX-774 | `_video_da_mesa.html`, `video_da_mesa.js` | IM |

## Pendências

- **FR-7105** e **FR-7126** estão no código e não têm teste dedicado: a Retificação que retira o vídeo depois do primeiro recebido, e a hora de tolerância depois do fim do período.
- **SC-2377** é humano: a matriz de navegadores com câmera real, critério de saída da entrega 0 do estudo.
- **P-0, P-7, P-8 e P-10** continuam abertas (spec, *Dependências*).
