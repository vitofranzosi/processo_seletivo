# Matriz de conformidade das oito ratificações

Data: 16/10/2026. Condições humanas: [consolidação da Fase 2](../fase-2-consolidacao-dec-15.md)
e registros R1–R4 ali vinculados. Análise estática, sem teste executado nesta fase.

Classificações solicitadas: **IT** Implementada e testada; **IH** Implementada, mas sem homologação;
**PA** Parcialmente atendida; **NA** Não atendida; **NV** Não verificável com as evidências disponíveis.
IH significa comportamento localizado no código, não comprovação de execução atual. IT exigiria
resultado executado e correspondente à condição, não apenas teste existente. Nenhuma condição
recebeu IT com base só em leitura. Ausência de evidência não foi classificada automaticamente NA.
Condições institucionais/documentais usam NV/PA quando não há aprovação ou rito demonstrado.

## Catálogo de fontes precisas

Paths relativos ao repositório, com links de arquivo e símbolos/linhas para localizar a evidência.
Testes abaixo foram consultados, **não executados nesta fase**. Não ampliar evidência de um teste
para cortes, recursos, convocações ou autorizações que sua asserção não cobre.

| Ref. | Implementação ou teste consultado / localização |
|---|---|
| C1 | [classificação/emissão](../../../backend/processo_seletivo/classificacao/application/emissao.py), `emitir_ordem`, linha 21: confirmação, motivo, autor e sucessão explícita |
| C2 | [selectors de classificação](../../../backend/processo_seletivo/classificacao/application/selectors.py), `estado_do_marco`, resultados `obsoleto`/`divergencias`; [reprodução](../../../backend/processo_seletivo/classificacao/application/reproducao.py) |
| T1 | [test_calculo.py](../../../backend/tests/integration/classificacao/test_calculo.py): `test_retificacao_da_regra_obsoleta_sem_resultado_novo` (330); `test_resultado_tardio_do_universo_obsoleta_e_nao_substitui_o_vigente` (401); `test_reproduz_o_ato_sem_consultar_o_estado_vigente` (505); `test_sucessao_cria_linha_nova_e_preserva_o_ato_anterior` (608); `test_emite_um_ato_com_tres_posicoes_e_uma_unica_auditoria` (115) |
| C3 | [contrato de mutabilidade](../../../backend/processo_seletivo/editais/domain/mutabilidade.py): `classificationMilestones/operation`, `normalization` (345–346), `schedule/isRegistrationPeriod` (443), `documentRequirements/key`/`name`/`instructions` (483–488); [changes.py](../../../backend/processo_seletivo/publicacoes/domain/changes.py), guarda antes de aplicação |
| T2 | [test_arredondamento.py](../../../backend/tests/unit/classificacao/test_arredondamento.py), entradas `normalizacao`; [test_numeracao_e_ausencia.py](../../../backend/tests/unit/classificacao/test_numeracao_e_ausencia.py), composição de marco com normalização (147). Cobrem cálculo em casos específicos, não toda sucessão normativa |
| C4 | [retificacoes.py](../../../backend/processo_seletivo/publicacoes/application/retificacoes.py), `_assert_conteudo_publicavel` (692), publicação/materialização e validação por ato; [publish_edital.py](../../../backend/processo_seletivo/publicacoes/application/publish_edital.py), validações de primeira publicação (496/720) |
| T3 | [test_contrato_de_inscricao.py](../../../backend/tests/integration/editais/test_contrato_de_inscricao.py), `test_a_retificacao_alcanca_o_documento_e_a_designacao` (112); [test_fatos_congelados.py](../../../backend/tests/integration/inscricoes/test_fatos_congelados.py), casos de preservação (82, 96, 138). Não provam sozinhos transição de calendário e todos os impactos |
| C5 | [validation.py](../../../backend/processo_seletivo/editais/domain/validation.py), `_denominacoes_do_codigo` (2979), achado `modality_code_name_divergent` (3015) e recorte documental; [044](../../../specs/044-recorte-transversal-documental/spec.md), D1/D-001 e lista gravada |
| T4 | [test_retificar_recorte_transversal.py](../../../backend/tests/integration/publicacoes/test_retificar_recorte_transversal.py), `test_renomear_a_modalidade_num_perfil_so_e_impedido` (129), `test_renomear_nos_dois_perfis_passa` (144); [test_lista_exigida.py](../../../backend/tests/integration/inscricoes/test_lista_exigida.py), casos entre envios (112) e leitura da lista (127) |
| C6 | [pdf.py](../../../backend/processo_seletivo/publicacoes/infrastructure/pdf.py), `_habilitacao_ao_sorteio` (1706) e inclusão da linha (2675); [relacao.py](../../../backend/processo_seletivo/sorteios/application/relacao.py), método declarado na formação da relação |
| T5 | [test_pdf_classificacao.py](../../../backend/tests/unit/publicacoes/test_pdf_classificacao.py), `test_o_sorteio_sem_etapa_de_habilitacao_diz_que_todas_participam` (805), `test_a_habilitacao_fica_no_bloco_do_sorteio_e_nao_no_marco_de_pontuacao` (814); teste de equivalência completa PDF/relação ainda não demonstrado aqui |
| C7 | [sincronizacao.py](../../../backend/processo_seletivo/unidades/application/sincronizacao.py), `sincronizar`: ator genérico de implantação, `REGISTRAR_UNIDADE`/`ALTERAR_UNIDADE`, instante e antes/depois; [unidades.json](../../../backend/processo_seletivo/unidades/unidades.json); [060](../../../specs/060-unidades-e-autoridades/spec.md), D-002 |
| T6 | [test_sincronizacao.py](../../../backend/tests/unidades/test_sincronizacao.py), `test_unidade_nova_e_registrada_com_trilha` (48), `test_mudanca_e_aplicada_com_antes_e_depois` (63); [test_documento_da_unidade.py](../../../backend/tests/unidades/test_documento_da_unidade.py), `test_a_retificacao_diz_a_unidade_do_dia_dela_e_o_original_a_do_seu` (83), `test_o_resultado_congela_a_unidade_e_o_documento_a_le_dos_bytes` (130) |
| C8 | [identidade.py](../../../backend/processo_seletivo/interface/identidade.py), mapa `exportador` (116); [exportar.py](../../../backend/processo_seletivo/matriculas/application/exportar.py), `compor` exige `matricula:exportar` e escopo; [views.py](../../../backend/processo_seletivo/interface/views.py), view de matrículas (5110 em diante) |
| T7 | [test_exportacao_de_matriculas.py](../../../backend/tests/interface/test_exportacao_de_matriculas.py), sem permissão (102/113), escopo alheio (120), geração (155), prévia nominal (175) |
| D | [029](../../../specs/029-requerimento-de-matricula/spec.md), [026 matriz](../../../specs/026-contrato-de-mutabilidade-normativa/matriz.md), [015](../../../specs/015-ordenacao-e-classificacao/spec.md), [Constituição](../../../.specify/memory/constitution.md), e deliberações expressas da Fase 2 |

## Condições por decisão

### DEC-15.02 — operação das pontuações

| Condição ratificada | Classe | Evidência / lacuna e próximo aceite |
|---|---|---|
| 1. Preservar versões/atos | IH | C1/C2/C4; T1 reprodução/sucessão. Demonstrar preservação no percurso completo |
| 2. Identificar classificação, cortes, recursos, convocações e demais dependentes | PA | C2 identifica divergências da ordem; T1 cobre regra alterada. Inventário transversal completo não comprovado |
| 3. Sem substituição automática de atos oficiais | IH | C1; T1 resultado tardio e sucessão. Não estender a todos os módulos sem conferir |
| 4. Emissão explícita de sucessores | IH | C1 `emitir_ordem`; T1 sucessão. Homologar confirmação e efeitos |
| 5. Autoria/data/justificativa/rastreabilidade | PA | C1 motivo/autor/auditoria; T1 evento. Cobertura ponta a ponta da Retificação e dependentes ainda precisa ser mapeada |
| 6. Efeitos administrativos à autoridade competente | NV | Deliberação D estabelece limite; não há autorização concreta nem rito completo comprovado |

### DEC-15.03 — normalização das pontuações

| Condição ratificada | Classe | Evidência / lacuna e próximo aceite |
|---|---|---|
| 1. Preservar cálculos/resultados históricos | IH | C2 reprodução e T1 reprodução do ato; homologar caso específico de normalização |
| 2. Registrar versões dos critérios | PA | C3/C4 retificam conteúdo versionado; não demonstrado ciclo completo de versões por normalização |
| 3. Identificar resultados/classificações/cortes afetados | PA | C2/T1 identificam divergência da ordem, sem inventário completo de dependentes |
| 4. Sem substituir resultado oficial automaticamente | IH | C1/T1 mantêm ato vigente; conferir também resultado divulgado, não apenas ordem |
| 5. Reavaliação explícita dos dependentes quando necessária | PA | C1 sucessor explícito; recursos, cortes e convocações não comprovados integralmente |
| 6. Rastreabilidade e auditoria | PA | C1/C4 e T1 evento; homologação do caso específico e cadeia completa pendentes |

Escopo ratificado exclui números da fonte de sorteio; C3 distingue `normalization` de pontuações
de `drawMethod/normalization`. Essa distinção técnica não autoriza novos efeitos administrativos.

### DEC-15.05 — designação do Evento de inscrições

| Condição ratificada | Classe | Evidência / lacuna e próximo aceite |
|---|---|---|
| 1. Preservar Eventos/versões/inscrições anteriores | PA | C4 versionamento; T3 designação e fatos preservados não cobrem juntos todo cenário pedido |
| 2. Distinguir designação de alteração efetiva do período | PA | C3 distingue campo de designação; rito e comunicação completos ainda não demonstrados |
| 3. Sem excluir/invalidar automaticamente submetidas | PA | C4 modifica conteúdo; T3 preserva inscrições em outro caso de Retificação; evidência específica de troca de Evento ainda pendente |
| 4. Capacidade não autoriza reabrir/prorrogar/reduzir | NV | Limite humano D; autorização/rito institucional do caso não apresentado |
| 5. Registrar efeitos no calendário público e inscrições | PA | C4 versões e T3 caminho de designação; relatório completo de impactos e interface não demonstrado |
| 6. Alterações administrativas à autoridade | NV | Consulta I-04 e autoridade pendentes; não inferir de permissão técnica |

### DEC-15.08 — coerência transversal

| Condição ratificada | Classe | Evidência / lacuna e próximo aceite |
|---|---|---|
| 1. Sem catálogo global para Perfis independentes | IH | C5 D-001 e filtro documental; T4 cobre recorte, não validação humana da clareza |
| 2. Coerência em documento ou regra transversal | PA | C5/T4 comprovam suporte documental por leitura. Cobertura de qualquer regra transversal não demonstrada |
| 3. Rastreabilidade das validações | PA | C5 achado com código/caminho; prova de histórico de cada aplicação da validação não localizada |
| 4. Mensagens compreensíveis | PA | C5 nomeia divergências; T4 impeditivo. Compreensão por elaborador depende de homologação |
| 5. Incluir na homologação de elaboradores | PA | Plano preparado nas Fases 3/4; inclusão aprovada, agenda e execução ainda pendentes |

### DEC-15.09 — apresentação da habilitação no PDF

| Condição ratificada | Classe | Evidência / lacuna e próximo aceite |
|---|---|---|
| 1. Correspondência ao método declarado | IH | C6 lê método que governa; T5 exemplos. Conferência operacional pendente |
| 2. Etapa habilitante correta | IH | C6 referência e nome; T5 apresentação no bloco. Conferir casos válidos/inválidos |
| 3. Mesmo universo efetivo do sorteio | PA | C6 usa regra comum; comparação completa PDF/relação congelada ainda não demonstrada |
| 4. PDF sem requisitos novos | IH | C6 deriva frase da declaração; T5 exemplos. Comissão precisa confirmar equivalência normativa |
| 5. Comissão validar em homologação | NV | Nenhum aceite de comissão disponível; plano não é validação |
| 6. Não antecipar alcance .06 | PA | Separação explícita nas decisões/planos D; .06 segue sem ratificação e execução correspondente |

### DEC-15.10 — chave do documento publicado

| Condição ratificada | Classe | Evidência / lacuna e próximo aceite |
|---|---|---|
| 1. Preservar chave estrutural | IH | C3 `documentRequirements/key`, recusa de campo não retificável. Ensaio específico não executado |
| 2. Retificar nome/instruções com versões | IH | C3/C4 caminhos próprios; prova específica de ciclo completo a coletar |
| 3. Não remapear vínculos históricos automaticamente | PA | C3 bloqueia chave; T4 lista por envio preservada. Integridade de todos os arquivos/vínculos ainda a demonstrar |
| 4. Erros estruturais por procedimento/análise/autorização | NV | Não foi localizado procedimento aprovado; decisão não implementa o rito |
| 5. Não confundir inclusão/remoção (DEC-07) | PA | Distinção documentada D; DEC-07 permanece aberta, sem nova funcionalidade aprovada |

### DEC-15.11 — catálogo de unidades

| Condição ratificada | Classe | Evidência / lacuna e próximo aceite |
|---|---|---|
| 1. Cefor aprovar informações | NV | C7 arquivo existente não comprova aprovação editorial; evidência humana necessária |
| 2. Técnica aplicar sem competência editorial própria | PA | C7 separa implantação técnica; rito de aprovação/editor nomeado não demonstrado |
| 3. Autoria/data/justificativa/versão de cada alteração | PA | C7/T6 antes/depois e instante; ator genérico de implantação, sem justificativa humana/versão do expediente comprovadas para cada mudança |
| 4. Preservar conteúdo histórico publicado | IH | T6 original/Retificação e bytes congelados; execução e homologação não feitas aqui |
| 5. Reavaliar interface após homologação | NV | Possibilidade de governança D; homologação e decisão futura não existem como evidência nesta entrega |

### DEC-15.14 — permissão separada de exportação

| Condição ratificada | Classe | Evidência / lacuna e próximo aceite |
|---|---|---|
| 1. Permissão separada para lote | IH | C8 `matricula:exportar`; T7 acesso direto/sem permissão |
| 2. Usuários autorizados por validação institucional | NV | Mapa local não é lista de usuários aprovada; manifestação institucional ausente |
| 3. Concessão/revogação/controles por validação institucional | PA | C8/T7 verificam permissão/escopo; integração e rito reais não demonstrados |
| 4. Não conceder automaticamente a outros papéis | IH | C8 papel local próprio; T7 negação. Isso não ratifica nome do papel nem concessão institucional |

## Conclusão documental

São **43 condições examinadas**, sem convertê-las em 43 requisitos novos. Evidências estáticas
indicam comportamentos e testes relacionados; nenhuma condição foi declarada homologada. Classes
podem mudar somente mediante evidência nova, registrada com versão e alcance. Não executar
correções para preencher PA/NV sem decisão e autorização próprias.
