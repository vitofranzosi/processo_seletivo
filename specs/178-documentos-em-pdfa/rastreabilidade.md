# Rastreabilidade — 178 · Os documentos que o GPS compõe nascem em PDF/A

**Frase que governa**: *a conformidade é do arquivo; a página, o texto e os atos gravados continuam os
mesmos.*

Caminhos de código relativos a `backend/processo_seletivo/`. As abreviações:

- **CF** — `tests/unit/publicacoes/test_conformidade_pdfa.py` (os acréscimos em cada exemplar, sem o
  validador)
- **D178** — `tests/unit/publicacoes/test_documento_da_auditoria_depois_da_178.py` (antes e depois,
  gravados)
- **CT** — `tests/contract/test_comprovante_e_divulgacao_byte_a_byte.py` e
  `tests/contract/test_documento_publicado.py`
- **CP** — `tests/integration/portal/test_comprovante_em_pdfa.py`
- **VP** — o job `pdfa` do CI: `tests/pdfa/test_exemplares.py`, o veraPDF 1.30.4 e
  `scripts/conferir_o_verapdf.py`

A faixa da spec abre em FR-8150 e SC-2820; o que a reserva tinha acima do último requisito
(FR-8171) e do último critério (SC-2827) ficou reservado e não gasto.

---

## Requisitos funcionais

| Requisito | Onde | Prova |
|---|---|---|
| FR-8150 | `publicacoes/infrastructure/pdfa.py`; `pdf.py` (`_arquivo_do_edital`, `render_documento`); `interface/diagramacao.py` | VP (os nove PASS); CF `test_sao_os_nove_tipos_da_fr_8150` |
| FR-8151 | `pdfa.NIVEL_U`, `pdfa.NIVEL_A`; `diagramacao._arquivo` declara A | CF `test_os_metadados_declaram_a_parte_e_o_nivel_esperados`, `test_os_relatorios_continuam_marcados`; VP (2a) |
| FR-8152 | `pdfa.xmp` | CF `test_os_metadados_declaram…`; VP: `conferir_o_verapdf.py` recusa nível declarado diferente do esperado |
| FR-8153 | `pdfa.xmp` (título e autor só quando há `/Info`) | CF `test_os_metadados_repetem_o_info_e_nada_mais`, `test_o_xmp_sem_info_declara_so_a_conformidade`, `test_o_xmp_escapa_o_texto…` |
| FR-8154 | `pdfa.identificador`; `pdf._montar_o_arquivo(identificado=)` | CF `test_o_identificador_e_derivado_do_corpo`, `test_o_identificador_tem_dezesseis_bytes…`; `test_arquivo_do_edital.py::test_sem_marcacao_e_com_o_identificador_do_conteudo` |
| FR-8155 | sem data, sem produtor, `/ID` derivado | CF `test_o_mesmo_conteudo_da_os_mesmos_bytes`; `test_arquivo_do_edital.py::test_os_mesmos_bytes_em_duas_composicoes`; CP (página e download) |
| FR-8156 | `cor/sRGB2014.icc`, `cor/LICENSE`, `cor/ORIGEM.md`; `pdfa.objetos` | CF `test_o_perfil_e_o_que_a_origem_registra`, `test_o_perfil_e_um_icc_rgb_de_monitor`, `test_a_condicao_de_saida_aponta_o_perfil_versionado` |
| FR-8157 | `pdfa.ANOTACAO_IMPRIMIVEL` em `_arquivo_do_edital` e `diagramacao._arquivo` | CF `test_toda_anotacao_e_imprimivel`; D178 `test_links_marcadores_e_estrutura_ficam`; sabotagem local reprovada em 6.3.2-1 |
| FR-8158 | `render_documento` com `fonte.objetos`; a recusa da métrica; `Composicao(metrica=METRICA_DO_EDITAL)` nos cinco chamadores | CF `test_toda_fonte_e_embutida`, `test_a_composicao_medida_pela_helvetica_e_recusada`; CT `test_os_novos_embutem_a_fonte…` |
| FR-8159 | os objetos novos depois dos de sempre (research R-001) | D178 `test_nenhuma_pagina_muda` |
| FR-8160 | idem, na família | D178 `test_o_texto_e_o_mesmo_palavra_a_palavra`; CT `test_o_texto_da_178_e_o_de_antes_palavra_a_palavra` |
| FR-8161 | nenhum caminho recompõe documento gravado; a coluna nova não percorre linha | D178 compara arquivos gravados; CP `test_a_migration_nao_toca_a_enviada_pelo_gatilho` |
| FR-8162 | `render_edital_pdf(..., pdfa=not previa)` | CF `test_a_previa_nao_declara_pdfa` |
| FR-8163 | `inscricoes/models.py` (`comprovante_em_pdfa`); `inscricoes/migrations/0008_comprovante_em_pdfa.py`; `inscricoes/application/submissao.py` | CP `test_a_inscricao_enviada_depois_da_178…`, `test_o_rascunho_de_antes_enviado_depois_recebe_o_pdfa` |
| FR-8164 | `pdf._documento_com_a_helvetica` (congelado); `render_comprovante_pdf(pdfa=False)` | CT `test_o_comprovante_da_inscricao_enviada_antes_da_178_sai_com_os_bytes_de_sempre`; CP `test_a_inscricao_enviada_antes_da_178_continua…` |
| FR-8165 | `portal/views.py` (`comprovante`, `comprovante_em_pdf`) | CP: o resumo da página é o do arquivo baixado, nos dois escritores |
| FR-8166 | `specs/069-edital-linguagem-simples/spec.md` (FR-1383 e SC-522 revistos) | `tests/test_citacoes_de_requisito.py` |
| FR-8167 | nenhum objeto de assinatura; o `/ID` é resumo, não certificado | CF (o XMP e o catálogo só têm o que a FR-8152 a FR-8156 pedem) |
| FR-8168 | `.github/workflows/backend.yml` (job `pdfa`); `scripts/conferir_o_verapdf.py` | VP; sabotagem local: nível B e `/F` ausente reprovados com arquivo e regra |
| FR-8169 | uma execução do veraPDF sobre a pasta | VP |
| FR-8170 | nenhuma dependência nova em `pyproject.toml`; o veraPDF só no CI | CF `test_producao_nao_ganha_dependencia` |
| FR-8171 | `tests/pdfa/exemplares.py`, `tests/pdfa/leitura.py` | CF inteiro |

## Critérios de sucesso

| Critério | Prova |
|---|---|
| SC-2820 | VP: os nove PASS, 2u e 2a; `research.md`, tabela final |
| SC-2821 | CF `test_o_mesmo_conteudo_da_os_mesmos_bytes` |
| SC-2822 | D178 `test_nenhuma_pagina_muda` (cenário A e B, contrato, Edital, Retificação, relatórios) |
| SC-2823 | CT `test_o_comprovante_da_inscricao_enviada_antes_da_178…`; CP |
| SC-2824 | D178 `test_o_texto_e_o_mesmo_palavra_a_palavra`; CT |
| SC-2825 | D178 (arquivos gravados); os gatilhos append-only da suíte; CP (a enviada não é tocada) |
| SC-2826 | CF `test_producao_nao_ganha_dependencia` |
| SC-2827 | D178 `test_links_marcadores_e_estrutura_ficam` |
