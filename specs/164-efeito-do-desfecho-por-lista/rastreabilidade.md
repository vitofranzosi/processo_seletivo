# Rastreabilidade — 164 · O efeito do desfecho da Etapa por lista

**Frase que governa**: *a retirada da reserva tira a inscrição só da lista reservada, e o faz pelo
mesmo caminho, e até o mesmo ponto, por onde a eliminação a tira de todas.*

Cada linha aponta onde o requisito entrou e o teste que o prende **pelo nome**. As abreviações dos
arquivos de teste são:

- **UE** — `tests/unit/resultados/test_efeito_do_desfecho.py`
- **UP** — `tests/unit/editais/test_efeito_na_publicacao.py`
- **US** — `tests/unit/portal/test_situacao_com_retirada.py`
- **TC** — `tests/interface/test_composicao_do_efeito.py`
- **IR** — `tests/integration/resultados/test_retirada_da_reserva.py`
- **IL** — `tests/integration/classificacao/test_listas_com_retirada.py`
- **IF** — `tests/integration/publicacoes/test_retificacao_do_efeito.py`
- **GL** — `tests/test_leitores_da_consequencia.py`, o guardião da FR-7018
- **G** — os guardiões que o campo novo atravessou:
  - `tests/contract/test_forma_publicada.py`;
  - `tests/contract/test_retificacoes_api.py`;
  - `tests/unit/interface/test_revisao.py`;
  - `tests/unit/publicacoes/test_alteracoes_legiveis.py`;
  - `tests/unit/duvidas/test_cobertura.py`;
  - `tests/unit/avaliacoes/test_elevacao.py`;
  - `tests/integration/publicacoes/test_elevacao_de_versao.py`;
  - `tests/migrations/test_migrations.py`.

---

## 1. Requisitos

| Requisito | Onde entrou | Teste |
|---|---|---|
| FR-7000 | `editais/models/etapas.py`, `draft.py`, `forms.py`, `_etapa.html` | TC `test_a_escolha_elimina_e_gravada`; UE `test_o_explicito_vale` |
| FR-7001 | `resultados/domain/efeito.py` (`publicar`, `efeito_desfavoravel`) | UE `test_a_publicacao_grava_o_padrao_so_onde_ha_reserva`, `test_o_nulo_do_acervo_restrito_e_eliminatorio_se_le_elimina`; IR `test_o_desfavoravel_retira_da_reserva_pelo_padrao`; TC `test_a_etapa_restrita_nasce_retirando_da_reserva` |
| FR-7002 | `editais/domain/validation.py` (`efeito_sem_reserva`), `forms._efeito` | UP `test_efeito_em_etapa_sem_reserva_impede_a_publicacao`; UE `test_sem_reserva_nao_ha_efeito`; TC `test_a_etapa_para_todas_descarta_o_efeito`; IR `test_a_etapa_para_todas_continua_eliminando` |
| FR-7003 | `resultados/domain/regra.py` (`_desfavoravel`) | UE `test_a_regra_aplica_o_efeito_ao_desfavoravel` |
| FR-7004 | `efeito.efeito_da_ausencia` | UE `test_a_ausencia_tem_o_mesmo_efeito_pelo_padrao`; IR `test_a_ausencia_tem_o_mesmo_efeito_pelo_padrao` |
| FR-7005 | degrau 23 (`elevacao.py`, `canonical.py`), `publish_edital._stages` | UP `test_o_nulo_nao_e_achado`; G `test_elevacao_de_versao.py` |
| FR-7006 | `editais/domain/mutabilidade.py`, `interface/retificacao.py` | G `test_retificacoes_api.py`, `test_alteracoes_legiveis.py` |
| FR-7007 | `regra.py`, `consolidacao.py` | IR `test_o_desfavoravel_retira_da_reserva_pelo_padrao`; UE `test_a_regra_aplica_o_efeito_ao_desfavoravel` |
| FR-7008 | `efeito.motivo_com_a_reserva` na consolidação, na Ocorrência e no recurso | IR `test_o_desfavoravel_retira_da_reserva_pelo_padrao` |
| FR-7009 | `resultados/application/ocorrencia.py` | IR `test_a_ausencia_elimina_quando_o_edital_o_declara`, `test_a_ausencia_retira_mesmo_quando_o_desfavoravel_elimina` |
| FR-7010 | `calculo._sem_retirada_anterior` filtra pela Modalidade da lista | IL `test_retirada_antes_da_ultima_enumerada_sai_so_da_reservada` |
| FR-7011 | `prontidao.py` (`SEGUEM`, `seguem_de`) | IR `test_a_retirada_segue_para_a_etapa_seguinte`, `test_o_efeito_declarado_elimina_como_antes`; US `test_retirada_e_depois_eliminada_e_eliminado` |
| FR-7012 | `calculo._sem_retirada_anterior`, `universo_classificavel.que_tiram`, `reproducao.py` | IL `test_retirada_antes_da_ultima_enumerada_sai_so_da_reservada`, `test_retirada_na_ultima_enumerada_fica_sem_posicao_so_na_reservada`, `test_retirada_depois_da_ultima_enumerada_nao_muda_a_ordem` |
| FR-7013 | `prontidao._dentro_da_faixa` (`retiram`) | **sem caso de integração**: o corte exige um ato de ordenação emitido sobre um marco que enumere Etapa, e o cenário da `163` é de sorteio. Fica pendente, e a condição é a mesma subconsulta que a FR-7014 exercita |
| FR-7014 | `ocupacao/application/selectors.retiradas_da_reserva` em `habilitadas_pelo_corte` | IL `test_a_reserva_nao_conta_a_retirada_ate_o_horizonte`, `test_a_ampla_conta_a_retirada_como_qualquer_inscricao` |
| FR-7015 | *por construção*: a subtração é do conjunto de habilitadas, e não da sequência da faixa | IL `test_a_reserva_nao_conta_a_retirada_ate_o_horizonte` |
| FR-7016 | *por construção*: a superação muda o universo gravado no ato, e a obsolescência de hoje o compara | IF `test_o_desfavoravel_superado_continua_travando` (a superação da retirada) |
| FR-7017 | *por construção*: a parte pública lista só quem tem posição (`divulgacao/domain/conteudo.py`) | IL `test_retirada_na_ultima_enumerada_fica_sem_posicao_so_na_reservada` |
| FR-7018 | o inventário | GL |
| FR-7019 | `recursos/application/julgar.py` (motivo); a derivação de hoje | IF `test_o_desfavoravel_superado_continua_travando` |
| FR-7020 | `retificacoes._recusar_efeito_mudado_apos_desfavoravel`, `selectors.desfavoraveis_registrados` | IF `test_com_desfavoravel_o_efeito_nao_se_retifica`, `test_o_efeito_da_ausencia_tambem_se_trava`, `test_o_desfavoravel_superado_continua_travando` |
| FR-7021 | idem: só a mudança do efeito resolvido impede | IF `test_ampliar_o_alcance_nao_muda_o_efeito`, `test_sem_desfavoravel_o_efeito_se_retifica` |
| FR-7022 | a recusa roda de novo na publicação | IF `test_a_retificacao_elaborada_antes_e_recusada_na_publicacao` |
| FR-7023 | `efeito.frase_do_efeito` em `pdf.py`, `apresentacao.py`, `revisao.py` | TC `test_o_documento_diz_o_efeito_declarado`, `test_o_acervo_sem_declaracao_lido_como_elimina_nao_ganha_frase_nova`; UE `test_as_frases_do_documento` |
| FR-7024 | `portal/situacao.py`, `resultados/application/selectors.py` | US `test_a_retirada_nao_e_eliminacao`, `test_sem_ordem_publicada_a_linha_aparece_mesmo_assim`, `test_a_eliminacao_continua_eliminado` |
| FR-7025 | `relatorio_do_edital.py`, `relatorio_pdf._eliminadas`, `resultados.html`, `conferencia_da_ordem.py` | TC `test_o_relatorio_conta_a_retirada_a_parte` |
| FR-7026 | *por construção*: a prévia não gera retirada | os testes de equivalência da prévia, inalterados |
| FR-7027 | `ocupacao/application/selectors._ordem_do_horizonte` | IL `test_a_retirada_depois_do_horizonte_nao_alcanca_a_reserva`, `test_retirada_depois_da_ultima_enumerada_nao_muda_a_ordem` |
| FR-7028 | `recursos/domain/pejus.piora` (gravidade) | UE `test_a_vedacao_de_piora_segue_a_gravidade` |
| FR-7029 | *por construção*: a reavaliação consolida por avaliação, e a regra aplica o efeito do desfavorável | UE `test_a_regra_aplica_o_efeito_ao_desfavoravel`, `test_a_vedacao_de_piora_segue_a_gravidade` |
| FR-7030 | `sorteios/application/habilitacao.para_o_recorte` | IL `test_a_relacao_do_sorteio_da_reserva_nao_traz_a_retirada`, `test_sem_etapa_de_habilitacao_a_relacao_nao_muda` |
| UX-740 | `_etapa.html`, `telas.css` (`.so-eliminatoria`) | TC `test_a_etapa_restrita_nasce_retirando_da_reserva`, `test_a_folha_esconde_o_grupo_fora_da_etapa_restrita_e_eliminatoria` |
| UX-741 | `_etapa.html` | TC `test_a_etapa_restrita_nasce_retirando_da_reserva` |
| UX-742 | `portal/situacao._linha_da_retirada` | US `test_a_retirada_nao_e_eliminacao` |
| UX-743 | `views._por_consequencia`, `consolidacao_confirmar.html` | TC `test_a_confirmacao_da_consolidacao_diz_cada_efeito_pelo_nome` |

## 2. Critérios

| Critério | Teste |
|---|---|
| SC-2330 | TC `test_o_acervo_sem_declaracao_lido_como_elimina_nao_ganha_frase_nova`; G `test_elevacao_de_versao.py` |
| SC-2331 | IL (as oito), IR `test_a_retirada_segue_para_a_etapa_seguinte` |
| SC-2332 | IR `test_o_efeito_declarado_elimina_como_antes`; os testes da `163` que declaram "elimina" |
| SC-2333 | US `test_a_retirada_nao_e_eliminacao` |
| SC-2334 | IF `test_o_desfavoravel_superado_continua_travando` |
| SC-2335 | GL |
| SC-2336 | *humano*, pendente |

## 3. Casos-limite

Estão na tabela do `checklists/requirements.md`, cada um ligado ao requisito que o resolve. O teste
de cada requisito está acima.
