# Rastreabilidade — 010 Área do Candidato e Acesso sem Senha

**Spec**: [spec.md](./spec.md) · **Tarefas**: [tasks.md](./tasks.md)

Do requisito ao teste que o sustenta. A Constituição exige que requisito crítico seja rastreável
entre especificação, plano, tarefas, implementação e testes (Princípio V); esta é a última ponte.

Caminhos são relativos a `backend/`.

## Identidade do candidato

| Requisito | Onde vive | Testes |
|---|---|---|
| FR-001, FR-002 identificador estável e opaco | `identidade/models.py` | `tests/unit/identidade/test_subject.py` |
| FR-003 nenhuma permissão institucional | `portal/identidade.py` | `tests/authorization/test_sessao_candidata.py` |
| FR-004, FR-005 núcleo mínimo pedido uma vez | `identidade/application/credenciais.py` | `tests/integration/identidade/test_nucleo_minimo.py` |
| FR-006, FR-007 CPF validado, declarado, sem decidir acesso | `inscricoes/domain/pessoais.py` | `tests/integration/identidade/test_nucleo_minimo.py`, `tests/authorization/test_demonstracao_de_seguranca.py` |
| FR-008 correção de nome e congelamento do CPF | `identidade/application/credenciais.py` | `tests/integration/identidade/test_correcao.py` |
| FR-009 CPF fora de endereço e de registro | `identidade/migrations/0002_reconciliacao.py` | `tests/integration/identidade/test_higiene_de_log.py`, `tests/migrations/test_reconciliacao_recusas.py` |

## Credenciais

| Requisito | Onde vive | Testes |
|---|---|---|
| FR-010, FR-011 exclusividade por restrição de banco | `identidade/models.py` | `tests/integration/identidade/test_modelos.py`, `tests/integration/identidade/test_credencial_concorrente.py` |
| FR-012 forma canônica conservadora | `identidade/domain/enderecos.py` | `tests/unit/identidade/test_enderecos.py` |
| FR-013, FR-014 principal alimenta a Inscrição; rascunho acompanha | `portal/identidade.py`, `identidade/application/credenciais.py` | `tests/integration/identidade/test_email_do_rascunho.py`, `tests/integration/identidade/test_principal_e_remocao.py` |
| FR-015 endereço histórico não é verificado | `identidade/migrations/0002_reconciliacao.py` | `tests/migrations/test_reconciliacao.py` |
| FR-016, FR-017 adicionar por desafio; recusa que não revela | `portal/views.py` | `tests/integration/identidade/test_adicionar_credencial.py` |
| FR-018, FR-019 última não sai; remover não altera inscrição | `identidade/application/credenciais.py` | `tests/integration/identidade/test_ultima_credencial.py`, `tests/integration/identidade/test_principal_e_remocao.py` |

## Desafio e sessão

| Requisito | Onde vive | Testes |
|---|---|---|
| FR-020, FR-021 resposta e janela equivalentes | `identidade/application/desafio.py` | `tests/integration/identidade/test_equivalencia.py` |
| FR-022 a FR-027 forma, prazo, uso único, resumo | `identidade/domain/codigo.py`, `identidade/application/desafio.py` | `tests/unit/identidade/test_codigo.py`, `tests/integration/identidade/test_desafio.py`, `tests/integration/identidade/test_consumo_atomico.py` |
| FR-028 endereço **e** finalidade | `identidade/application/desafio.py` | `tests/integration/identidade/test_finalidade.py` |
| FR-029 a FR-031 tetos e recusa indistinguível | `identidade/application/desafio.py` | `tests/integration/identidade/test_limites.py`, `tests/integration/identidade/test_teto_concorrente.py` |
| FR-030 origem não escolhida por quem é contado | `portal/views.py` | `tests/integration/identidade/test_origem_da_solicitacao.py` |
| FR-030a topologia declarada, nunca adivinhada | `config/settings/production.py` | `tests/test_configuracao_producao.py` |
| FR-032, FR-033 estado compartilhado e limpeza por estado | `identidade/application/desafio.py` | `tests/integration/identidade/test_limpeza.py` |
| FR-034 a FR-039 sessão, rotação, saída, eixos distintos | `portal/identidade.py` | `tests/authorization/test_rotacao_de_sessao.py`, `tests/authorization/test_sessao_candidata.py` |

## Reconciliação com a jornada anterior

| Requisito | Onde vive | Testes |
|---|---|---|
| FR-040 a FR-043 na implantação, preservando o titular | `identidade/migrations/0002_reconciliacao.py` | `tests/migrations/test_reconciliacao.py` |
| FR-044 a FR-047 grupos irreconciliáveis e interrupção | `identidade/migrations/0002_reconciliacao.py` | `tests/migrations/test_reconciliacao_recusas.py` |
| FR-048 identificação por declaração aposentada | `portal/urls.py`, `config/settings/production.py` | `tests/acceptance/portal/test_minhas_inscricoes.py`, `tests/test_configuracao_producao.py` |
| FR-049 a FR-052c convite, decisão antes do vínculo, tentativas | `identidade/application/associacao.py` | `tests/integration/identidade/test_correspondencia.py`, `tests/integration/identidade/test_sem_beco.py`, `tests/integration/identidade/test_tentativas_cpf.py` |
| FR-053 a FR-055 retomada limitada, atômica, sob bloqueio | `identidade/application/associacao.py`, `inscricoes/application/rascunho.py` | `tests/integration/identidade/test_retomada.py`, `tests/integration/identidade/test_retomada_concorrente.py` |
| FR-056, FR-057 não funde; indício não vira autoridade | `identidade/application/associacao.py` | `tests/integration/identidade/test_sem_beco.py`, `tests/authorization/test_demonstracao_de_seguranca.py` |

## Área pessoal

| Requisito | Onde vive | Testes |
|---|---|---|
| FR-058 a FR-061 lista, continuidade, estado vazio | `portal/views.py` | `tests/integration/portal/test_minhas_inscricoes.py` |
| FR-062, FR-063 restrições preservada e acrescentada | `inscricoes/models.py` | `tests/integration/inscricoes/test_idempotencia_preservada.py`, `tests/integration/inscricoes/test_cpf_na_submetida.py` |
| FR-064 a FR-066 duplicidade aceita, assinalada, não decidida | `inscricoes/application/consulta.py` | `tests/integration/inscricoes/test_cpf_coincidente.py` |
| FR-067 a FR-075 conferência, documentos, comprovante, imutabilidade | `portal/views.py` | `tests/integration/portal/test_conferir_inscricao.py`, `tests/integration/portal/test_comprovante_preservado.py` |
| FR-074a instante único, no fuso da instituição | `inscricoes/infrastructure/comprovante_pdf.py` | `tests/integration/portal/test_hora_do_envio.py` |
| FR-076 a FR-079 acompanhamento e aviso de versão | `portal/views.py` | `tests/integration/portal/test_acompanhamento.py`, `tests/integration/portal/test_aviso_de_versao.py` |

## Canal de e-mail, acesso e auditoria

| Requisito | Onde vive | Testes |
|---|---|---|
| FR-080 a FR-083 mecanismo, recusa de boot, conteúdo da mensagem do desafio | `config/settings/production.py`, `identidade/application/mensagem.py` | `tests/test_configuracao_producao.py`, `tests/integration/identidade/test_mensagem.py` |
| FR-084 a FR-084b confirmação do envio: uma só, sem CPF, fora da transação | `inscricoes/application/mensagem.py`, `portal/views.py` | `tests/integration/portal/test_confirmacao_de_inscricao.py` |
| FR-085 a FR-087 titularidade, recusa que não enumera, nada por afirmação | `inscricoes/domain/titularidade.py`, `portal/views.py` | `tests/authorization/test_idor_area.py`, `tests/authorization/test_acesso_sem_prova.py` |
| FR-088, FR-089 auditoria dos atos, e o que não vira evento | `identidade/application/credenciais.py` | `tests/integration/identidade/test_auditoria_de_credencial.py` |
| FR-090 recuperação fora da V1, com caminho nomeado | `portal/templates/portal/acesso_reconciliar.html` | `tests/contract/portal/test_reconciliacao.py` |

## Experiência

| Requisito | Testes |
|---|---|
| UX-001 a UX-004 percurso curto, sem CPF, sem redigitação | `tests/acceptance/portal/test_entrar_sem_senha.py`, `tests/acceptance/portal/test_minhas_inscricoes.py` |
| UX-005 a UX-008 campo único, reenvio informado, erro que não apaga | `tests/interface/test_acessibilidade_do_portal.py`, `tests/acceptance/portal/test_entrar_sem_senha.py` |
| UX-006a porta de entrada em toda página pública | `tests/integration/portal/test_porta_de_entrada.py` |
| UX-009, UX-010 375 px e teclado | `tests/interface/test_acessibilidade_do_portal.py` |

## Critérios de sucesso

| Critério | Testes |
|---|---|
| SC-001 a SC-006 acesso recorrente, tetos, equivalência, sem CPF | `tests/acceptance/portal/test_entrar_sem_senha.py`, `tests/integration/identidade/test_equivalencia.py`, `tests/integration/identidade/test_teto_concorrente.py` |
| SC-007 a SC-011c preservação do titular e do que foi submetido | `tests/migrations/test_reconciliacao.py`, `tests/authorization/test_titularidade_preservada.py`, `tests/integration/identidade/test_correcao.py` |
| SC-012 a SC-017a proteção, concorrência, recusa de produção | `tests/authorization/test_idor_area.py`, `tests/authorization/test_acesso_sem_prova.py`, `tests/integration/identidade/test_credencial_concorrente.py`, `tests/test_configuracao_producao.py` |
| SC-028 a SC-032 recusa nomeada, reenvio que responde, recibo do envio, instante único, porta de entrada | `tests/integration/identidade/test_recusa_do_codigo.py`, `tests/integration/identidade/test_reenvio.py`, `tests/integration/portal/test_confirmacao_de_inscricao.py`, `tests/integration/portal/test_hora_do_envio.py`, `tests/integration/portal/test_porta_de_entrada.py` |
| SC-018 a SC-026 valor para o candidato | `tests/acceptance/portal/` (todas), `tests/interface/test_acessibilidade_do_portal.py` |
| SC-027 duplicidade não recusa e é assinalada | `tests/integration/inscricoes/test_cpf_coincidente.py` |

## Demonstração de segurança

Os seis casos do §25 da spec, mais o sétimo que a revisão acrescentou, estão em
`tests/authorization/test_demonstracao_de_seguranca.py` e `tests/authorization/test_acesso_sem_prova.py`.

## O que permanece fora, e por decisão

- **Recuperação de acesso** (FR-090): fora da V1, com caminho institucional nomeado na tela.
- **Política de retenção** (PC-003): gate de implantação, não de código.
- **Auditoria de credencial na consulta por escopo** (D-012): o ato não pertence a Edital algum, e
  a consequência é verificada em teste, não escondida.
