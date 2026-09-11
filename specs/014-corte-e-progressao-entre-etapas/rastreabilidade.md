# Rastreabilidade — 014 · Corte e Progressão entre Etapas

Cada requisito da spec, a tarefa que o realiza e o arquivo onde ele vive. É o que o Princípio V pede,
e é o que `tests/test_citacoes_de_requisito.py` cobra: **onde existe matriz, ela alcança cada
requisito** — linha perdida é invisível de outro jeito, e a `010` perdeu duas num script abortado.

A coluna **Fechado** diz se **todas** as tarefas daquele requisito estão marcadas em
[tasks.md](tasks.md). "Não" não significa requisito quebrado: significa que alguma tarefa que o cita
continua aberta, e o relatório de conclusão diz quais.

A coluna **Onde vive** traz os arquivos que as tarefas nomeiam, e no máximo três: ela é um atalho de
leitura, e não o inventário — quem quer o inventário lê o `git log` da feature.

### Requisitos funcionais

| Requisito | Tarefas | Onde vive | Fechado |
|---|---|---|---|
| **FR-178** | T003, T096 | `editais/models/perfis.py` | sim |
| **FR-179** | T014 | `tests/unit/editais/test_regra_de_corte.py` | sim |
| **FR-180** | T015, T036a | `tests/unit/classificacao/test_faixa.py`, `tests/unit/editais/test_regra_de_corte.py` | sim |
| **FR-181** | T016 | `tests/unit/editais/test_regra_de_corte.py` | sim |
| **FR-182** | T016 | `tests/unit/editais/test_regra_de_corte.py` | sim |
| **FR-183** | T017, T018c, T097, T098 | `editais/domain/validation.py`, `editais/migrations/0018_ampla_concorrencia_declarada.py`, `editais/models/perfis.py` | sim |
| **FR-184** | T033 | `interface/retificacao.py` | sim |
| **FR-185** | T034 | `publicacoes/infrastructure/pdf.py` | sim |
| **FR-186** | T009 | `publicacoes/domain/elevacao.py`, `shared/canonical.py` | sim |
| **FR-224** | T018a, T025, T042a, T068 | `classificacao/domain/faixa.py`, `tests/integration/classificacao/test_emissao_do_corte.py`, `tests/unit/editais/test_regra_de_corte.py` | sim |
| **FR-225** | T018a | `tests/unit/editais/test_regra_de_corte.py` | sim |
| **FR-229** | T018d | `tests/unit/editais/test_regra_de_corte.py` | sim |
| **FR-226** | T018b, T073 | `tests/integration/classificacao/test_faixa_seguinte.py`, `tests/unit/editais/test_regra_de_corte.py` | sim |
| **FR-187** | T052 | `classificacao/application/corte.py` | sim |
| **FR-188** | T052 | `classificacao/application/corte.py` | sim |
| **FR-189** | T038 | `tests/unit/classificacao/test_faixa.py` | sim |
| **FR-190** | T049 | `tests/interface/test_corte.py` | sim |
| **FR-191** | T042 | `tests/unit/classificacao/test_faixa.py` | sim |
| **FR-192** | T043 | `tests/unit/classificacao/test_corte_append_only.py` | sim |
| **FR-193** | T055 | — | sim |
| **FR-194** | T007, T044 | `classificacao/models.py`, `tests/integration/classificacao/test_emissao_do_corte.py` | sim |
| **FR-195** | T039 | `tests/unit/classificacao/test_faixa.py` | sim |
| **FR-196** | T039 | `tests/unit/classificacao/test_faixa.py` | sim |
| **FR-197** | T045 | `tests/integration/classificacao/test_emissao_do_corte.py` | sim |
| **FR-198** | T045 | `tests/integration/classificacao/test_emissao_do_corte.py` | sim |
| **FR-199** | T086 | `tests/integration/classificacao/test_reproducao_do_corte.py` | sim |
| **FR-200** | T047 | `tests/integration/classificacao/test_emissao_do_corte.py` | sim |
| **FR-227** | T006, T054a, T081b | `tests/integration/classificacao/test_corte_obsoleto.py` | sim |
| **FR-201** | T006, T046 | `tests/integration/classificacao/test_emissao_do_corte.py` | sim |
| **FR-202** | T071, T101 | `classificacao/application/emissao_do_corte.py`, `tests/integration/classificacao/test_faixa_seguinte.py` | sim |
| **FR-203** | T073 | `tests/integration/classificacao/test_faixa_seguinte.py` | sim |
| **FR-204** | T073, T073a, T100 | `classificacao/application/corte.py`, `tests/integration/classificacao/test_faixa_seguinte.py` | sim |
| **FR-205** | T073 | `tests/integration/classificacao/test_faixa_seguinte.py` | sim |
| **FR-206** | T074 | `tests/integration/classificacao/test_faixa_seguinte.py` | sim |
| **FR-207** | T075 | `tests/test_vocabulario_do_corte.py`, `tests/test_vocabulario_do_resultado.py` | sim |
| **FR-208** | T059 | `tests/integration/resultados/test_progressao_com_corte.py` | sim |
| **FR-209** | T060 | `tests/integration/resultados/test_progressao_com_corte.py` | sim |
| **FR-210** | T061 | `tests/integration/resultados/test_progressao_com_corte.py` | sim |
| **FR-211** | T062 | `tests/integration/resultados/test_progressao_com_corte.py` | sim |
| **FR-212** | T063 | `tests/integration/resultados/test_progressao_com_corte.py` | sim |
| **FR-213** | T065, T068 | — | sim |
| **FR-214** | T003, T064 | `editais/models/perfis.py`, `tests/integration/resultados/test_progressao_com_corte.py` | sim |
| **FR-215** | T078, T104 | `classificacao/application/corte.py`, `tests/integration/classificacao/test_corte_obsoleto.py` | **não** |
| **FR-216** | T078 | `tests/integration/classificacao/test_corte_obsoleto.py` | **não** |
| **FR-217** | T079 | `tests/integration/classificacao/test_corte_obsoleto.py` | sim |
| **FR-218** | T080 | `tests/integration/classificacao/test_corte_obsoleto.py` | **não** |
| **FR-230** | T080a, T096 | `tests/integration/classificacao/test_corte_obsoleto.py` | **não** |
| **FR-231** | T097, T098, T099 | `classificacao/application/corte.py`, `editais/domain/validation.py`, `editais/migrations/0018_ampla_concorrencia_declarada.py` | sim |
| **FR-232** | T102 | `resultados/application/prontidao.py` | sim |
| **FR-233** | T100 | `classificacao/application/corte.py` | sim |
| **FR-234** | T103 | `resultados/application/prontidao.py` | sim |
| **FR-235** | T104 | `classificacao/application/corte.py` | sim |
| **FR-219** | T081, T084 | `divulgacao/domain/publicabilidade.py`, `tests/integration/classificacao/test_corte_obsoleto.py` | sim |
| **FR-228** | T081a, T085a | `resultados/application/prontidao.py`, `tests/integration/classificacao/test_corte_obsoleto.py` | sim |
| **FR-220** | T054, T105 | `classificacao/application/emissao_do_corte.py`, `interface/templates/interface/corte.html`, `interface/views.py` | sim |
| **FR-221** | T051 | `tests/interface/test_corte.py` | sim |
| **FR-222** | T054, T089, T107 | `classificacao/application/emissao_do_corte.py`, `tests/integration/classificacao/test_reproducao_do_corte.py` | sim |
| **FR-223** | T008, T043 | `classificacao/migrations/0006_corte.py`, `tests/unit/classificacao/test_corte_append_only.py` | sim |

### Critérios de sucesso

| Requisito | Tarefas | Onde vive | Fechado |
|---|---|---|---|
| **SC-055** | T096 | — | sim |
| **SC-056** | T059 | `tests/integration/resultados/test_progressao_com_corte.py` | sim |
| **SC-057** | T061 | `tests/integration/resultados/test_progressao_com_corte.py` | sim |
| **SC-058** | T045 | `tests/integration/classificacao/test_emissao_do_corte.py` | sim |
| **SC-059** | T039 | `tests/unit/classificacao/test_faixa.py` | sim |
| **SC-060** | T039 | `tests/unit/classificacao/test_faixa.py` | sim |
| **SC-061** | T086 | `tests/integration/classificacao/test_reproducao_do_corte.py` | sim |
| **SC-062** | T079 | `tests/integration/classificacao/test_corte_obsoleto.py` | sim |
| **SC-063** | T081 | `tests/integration/classificacao/test_corte_obsoleto.py` | sim |
| **SC-064** | T071 | `tests/integration/classificacao/test_faixa_seguinte.py` | sim |
| **SC-065** | T074 | `tests/integration/classificacao/test_faixa_seguinte.py` | sim |
| **SC-066** | T075 | `tests/test_vocabulario_do_corte.py`, `tests/test_vocabulario_do_resultado.py` | sim |
| **SC-067** | T093 | — | **não** |
| **SC-068** | T065 | — | sim |
| **SC-069** | T064 | `tests/integration/resultados/test_progressao_com_corte.py` | sim |
| **SC-070** | T089, T107 | `classificacao/application/emissao_do_corte.py`, `tests/integration/classificacao/test_reproducao_do_corte.py` | sim |
| **SC-071** | T036a | `tests/unit/classificacao/test_faixa.py` | sim |
| **SC-072** | T081b | `tests/integration/classificacao/test_corte_obsoleto.py` | sim |
| **SC-073** | T081a, T096 | `tests/integration/classificacao/test_corte_obsoleto.py` | sim |
| **SC-074** | T101, T108 | `classificacao/application/emissao_do_corte.py`, `tests/integration/classificacao/test_corte_obsoleto.py`, `tests/integration/classificacao/test_faixa_seguinte.py` | sim |
| **SC-075** | T102, T108 | `resultados/application/prontidao.py`, `tests/integration/classificacao/test_corte_obsoleto.py`, `tests/integration/classificacao/test_faixa_seguinte.py` | sim |

### Requisitos de apresentação

| Requisito | Tarefas | Onde vive | Fechado |
|---|---|---|---|
| **UX-024** | T020, T050, T091, T096, T106 | `tests/interface/test_corte.py` | **não** |
| **UX-025** | T024, T077 | `editais/domain/validation.py` | sim |
| **UX-026** | T061, T070 | `tests/integration/resultados/test_progressao_com_corte.py` | sim |
| **UX-027** | T085 | — | **não** |
| **UX-028** | T050, T057 | `interface/templates/interface/corte.html`, `tests/interface/test_corte.py` | sim |
| **UX-029** | T058, T106 | — | **não** |
| **UX-030** | T081a, T085a, T096 | `resultados/application/prontidao.py`, `tests/integration/classificacao/test_corte_obsoleto.py` | sim |
