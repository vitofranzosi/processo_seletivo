# Rastreabilidade — 025 Quadro de Vagas por Modalidade

Cada identificador definido em [spec.md](spec.md), com onde ele foi implementado e onde é
verificado. O teste `tests/test_citacoes_de_requisito.py` cobra esta matriz inteira.

Caminhos relativos a `backend/`.

## Requisitos funcionais

### Declaração do quadro

| Requisito | Implementação | Verificação |
|---|---|---|
| **FR-153** | `processo_seletivo/editais/models/perfis.py` (`LinhaDoQuadroDeVagas`), `editais/migrations/0016_quadro_de_vagas.py`, `editais/application/draft.py` | `tests/unit/editais/test_quadro_de_vagas.py`, `tests/contract/test_edital_draft_api.py` |
| **FR-154** | `editais/models/perfis.py` (`uq_linha_geral_por_perfil`), `editais/domain/perfis.py` (`validate_vacancy_table`), `editais/domain/validation.py` (`vacancy_general_row_duplicated`) | `tests/unit/editais/test_quadro_de_vagas.py`, `tests/unit/editais/test_invariantes_do_quadro.py` |
| **FR-155** | `editais/models/perfis.py` (`uq_linha_por_modalidade`), `editais/domain/perfis.py`, `editais/domain/validation.py` (`vacancy_modality_row_duplicated`) | `tests/unit/editais/test_quadro_de_vagas.py`, `tests/unit/editais/test_invariantes_do_quadro.py` |
| **FR-156** | `editais/models/perfis.py` (`vagas_imediatas`), `editais/domain/perfis.py`, `editais/api/serializers.py` (`VacancyTableRowSerializer`) | `tests/unit/editais/test_quadro_de_vagas.py` |
| **FR-157** | ausência de caminho de escrita; `editais/domain/validation.py` (`_divergencia_do_percentual`, que só reporta) | `tests/unit/editais/test_invariantes_do_quadro.py`, `tests/unit/editais/test_quadro_de_vagas.py` |
| **FR-158** | `editais/domain/perfis.py` (`validate_vacancy_table`), `editais/application/draft.py` (`_identidades_aninhadas_alheias`) | `tests/unit/editais/test_quadro_de_vagas.py`, `tests/contract/test_edital_draft_api.py` |
| **FR-159** | `interface/forms.py` (`_linhas`, `_quadro_para_o_formulario`) | `tests/interface/test_compor_quadro.py` |
| **FR-160** | `editais/api/serializers.py` (campo opcional), `editais/domain/validation.py` (`_coerencia_do_quadro_de_vagas` ignora quadro ausente) | `tests/unit/editais/test_quadro_de_vagas.py`, `tests/contract/test_edital_draft_api.py` |
| **FR-161** | `editais/domain/validation.py` (`vacancy_sum_mismatch`) | `tests/unit/editais/test_quadro_de_vagas.py`, `tests/integration/publicacoes/test_quadro_na_retificacao.py`, `tests/acceptance/test_us2_perfis.py` |
| **FR-162** | `editais/domain/validation.py` (a soma confere e não escreve) | `tests/unit/editais/test_quadro_de_vagas.py`, `tests/integration/publicacoes/test_quadro_na_retificacao.py` |
| **FR-163** | `editais/domain/validation.py` (`vacancy_row_percentage_divergence`, nível aviso) | `tests/unit/editais/test_quadro_de_vagas.py` |

### Publicação

| Requisito | Implementação | Verificação |
|---|---|---|
| **FR-164** | `publicacoes/application/publish_edital.py` (`edital_snapshot`) | `tests/integration/publicacoes/test_quadro_na_publicacao.py`, `tests/unit/editais/test_forma_do_snapshot.py` |
| **FR-165** | ausência de caminho: nenhuma tela, rota ou emissão trata o quadro como anexo | `tests/unit/editais/test_invariantes_do_quadro.py` |
| **FR-166** | `editais/domain/validation.py` (`vacancy_row_modality_missing`), aplicado por `publish_edital.py` | `tests/integration/publicacoes/test_quadro_na_publicacao.py` |
| **FR-167** | `shared/canonical.py` (`SCHEMA_VERSION` 12), `publicacoes/domain/elevacao.py` (`DEGRAUS_DE_PERFIL[12]`) | `tests/contract/test_elevacao_degrau_12.py`, `tests/integration/publicacoes/test_quadro_na_publicacao.py` |
| **FR-168** | `publish_edital.py` (ordenação determinística no emissor) | `tests/integration/publicacoes/test_quadro_na_publicacao.py` |
| **FR-169** | `publicacoes/infrastructure/pdf.py` (`_quadro_de_vagas_do_perfil`) | `tests/contract/test_documento_publicado.py` |

### Retificação

| Requisito | Implementação | Verificação |
|---|---|---|
| **FR-170** | `publicacoes/domain/colecoes.py` (`/profiles/*/vacancyTable` em `COLECOES_COM_CHAVE`) | `tests/unit/publicacoes/test_colecoes.py`, `tests/integration/publicacoes/test_quadro_na_retificacao.py` |
| **FR-171** | `interface/retificacao.py` (`CAMPOS_DA_LINHA`, `NOVA_LINHA_DO_QUADRO`, `diferencas`), `interface/views.py` (`fragmento_retificacao_linha_do_quadro`) | `tests/integration/publicacoes/test_quadro_na_retificacao.py`, `tests/interface/test_retificar_quadro.py` |
| **FR-172** | `editais/domain/validation.py` (`vacancy_row_modality_missing`), aplicado por `publicacoes/application/retificacoes.py` sem código novo | `tests/integration/publicacoes/test_quadro_na_retificacao.py` |
| **FR-173** | a Retificação materializa versão nova; nada é reescrito | `tests/integration/publicacoes/test_quadro_na_retificacao.py`, `tests/acceptance/test_us2_perfis.py` |

### Preservação e alcance

| Requisito | Implementação | Verificação |
|---|---|---|
| **FR-174** | `editais/migrations/0016_quadro_de_vagas.py` (aditiva; nenhum campo da `RegraNormativa` é tocado) | `tests/migrations/test_migrations.py` |
| **FR-175** | ausência de caminho de escrita entre `Inscricao` e a linha | `tests/unit/editais/test_invariantes_do_quadro.py` |
| **FR-176** | `editais/models/perfis.py` (a linha geral é única), `interface/templates/interface/_linha_do_quadro.html` (a tela diz onde mora o número da ampla concorrência) | `tests/unit/editais/test_quadro_de_vagas.py`, `tests/interface/test_compor_quadro.py` |
| **FR-177** | `editais/domain/validation.py` (`vacancy_sum_exceeds_total`) | `tests/unit/editais/test_quadro_de_vagas.py`, `tests/interface/test_compor_quadro.py` |

## Requisitos de apresentação

| Requisito | Implementação | Verificação |
|---|---|---|
| **UX-020** | `interface/templates/interface/_perfil.html` (`<section class="quadro">`) | `tests/interface/test_compor_quadro.py` |
| **UX-021** | `interface/forms.py` (`_quadro_para_o_formulario`, `quadro_do_formulario`), `interface/templates/interface/_linha_do_quadro.html` | `tests/interface/test_compor_quadro.py` |
| **UX-022** | `interface/templates/interface/_linha_do_quadro.html` (rótulo textual e peso tipográfico, sem cor) | `tests/interface/test_compor_quadro.py` |
| **UX-023** | `editais/domain/validation.py` (as duas mensagens da soma dizem os três números) | `tests/unit/editais/test_quadro_de_vagas.py`, `tests/interface/test_compor_quadro.py`, `tests/integration/publicacoes/test_quadro_na_retificacao.py` |

## Critérios de sucesso

| Critério | Verificação |
|---|---|
| **SC-048** | `tests/interface/test_compor_quadro.py` (quatro quantidades, nenhum rótulo redigitado) |
| **SC-049** | `tests/acceptance/test_us2_perfis.py` (o ciclo completo do `57/2026`) |
| **SC-050** | `tests/integration/publicacoes/test_quadro_na_publicacao.py`, `tests/contract/test_documento_publicado.py` |
| **SC-051** | `tests/integration/publicacoes/test_quadro_na_publicacao.py` (`Q 1`, `PCD 1`) |
| **SC-052** | `tests/interface/test_compor_quadro.py` (7 Perfis × 3 Modalidades, 28 campos) |
| **SC-053** | `tests/acceptance/test_us2_perfis.py` (documento inteiro, sem anexo binário), `tests/unit/editais/test_invariantes_do_quadro.py` |
| **SC-054** | `tests/unit/editais/test_quadro_de_vagas.py`, `tests/interface/test_compor_quadro.py` |

## Decisões

As decisões `D-001` a `D-011` da §3 da spec são normativas e não têm implementação isolada: cada
uma governa um ou mais requisitos acima, e o comentário do código que a aplica a cita pelo
identificador. `D-003` e `D-011` são decisões de **não fazer**, e a verificação delas é a ausência
— `tests/unit/editais/test_invariantes_do_quadro.py` e `tests/migrations/test_migrations.py`.
