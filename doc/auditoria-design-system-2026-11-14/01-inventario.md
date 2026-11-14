# A. Inventário de interfaces

*Gerado por `medicoes/gerar_inventario.py` a partir do resolvedor de URLs do Django e do rastreio no navegador. Base: `main` em `37ed0ad0`, 14/11/2026.*

## Como ler

- **Rota** é o padrão de URL; **tela** é a view que a serve. Uma rota conta como tela quando rende um template inteiro.
- **Estado** é uma variação da mesma tela: um parâmetro de consulta (aba, filtro, recorte) ou o momento do certame em que o Edital está. Estados não entram na contagem de telas.
- **Perfil** é o papel a que a seção se destina, pelo menu e pelas specs. A regra de autorização de cada rota não foi conferida uma a uma.
- **Situação**: *inspecionada* quer dizer aberta num Chromium real, medida e capturada; *captura da suíte* vem das jornadas de `tests/navegador/`; *não vista no navegador* foi só lida no template.

## Contagem

| O que | Quantas |
|---|---:|
| Rotas no resolvedor | 255 |
| **Rotas que rendem tela** | **135** |
| API REST (sem tela) | 33 |
| Gesto por POST, download ou redirecionamento (sem tela própria) | 56 |
| Fragmento htmx (parte de tela) | 31 |

| Situação da inspeção | Rotas |
|---|---:|
| inspecionada | 84 |
| não vista no navegador | 44 |
| captura da suíte | 7 |

| Arquétipo | Rotas |
|---|---:|
| Confirmação de ato | 35 |
| Formulário de configuração | 14 |
| Jornada do candidato | 13 |
| Registro e histórico | 12 |
| Lista administrativa | 10 |
| Operação com etapas | 10 |
| Central de trabalho | 8 |
| Acesso | 8 |
| Página de entidade | 7 |
| Avaliação ou conferência | 7 |
| Portal público | 7 |
| Guia incorporado | 2 |
| Relatório | 2 |

No navegador foram abertas **131 variações de tela** (rota + parâmetros), em 647 visitas com resposta 200, por nove identidades: a presidência com todos os papéis da demonstração (em dois Processos), um avaliador, o setor da formalização, quatro candidatos fictícios e o visitante sem autenticação.

## Telas por área

### Acesso à gestão

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/identificar` | `identificar` | identificar.html, identificar_demonstracao.html, sem_autenticacao.html | Acesso | qualquer pessoa | navegador · 2 estado(s) · anonimo, paulo.presidente, treino.avaliacao1, treino.formalizacao, treino.presidencia | inspecionada |
| `/gestao/identificar/demonstracao` | `identificar_demonstracao` | identificar_demonstracao.html, sem_autenticacao.html | Acesso | qualquer pessoa | navegador · 2 estado(s) · anonimo, paulo.presidente, treino.avaliacao1, treino.formalizacao, treino.presidencia | inspecionada |
| `/gestao/entrar/institucional` | `entrar_institucional` | sem_autenticacao.html | Acesso | qualquer pessoa | leitura do template | não vista no navegador |
| `/gestao/entrar/institucional/retorno` | `retorno_institucional` | sem_autenticacao.html | Acesso | qualquer pessoa | leitura do template | não vista no navegador |
| `/gestao/sem-acesso` | `sem_acesso` | sem_acesso.html | Acesso | qualquer pessoa | suíte: `sem-acesso` | captura da suíte |

### Acessos

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/acessos` | `lista` | acessos.html | Lista administrativa | administrador de acessos / institucional | suíte: `acessos-busca`, `acessos-historico` | captura da suíte |
| `/gestao/acessos/conceder` | `conceder` | acessos_conceder.html, acessos_confirmar.html | Confirmação de ato | administrador de acessos / institucional | suíte: `acessos-busca`, `acessos-confirmacao` | captura da suíte |
| `/gestao/acessos/vinculos/<uuid:vinculo_id>/revogar` | `revogar` | acessos_confirmar.html | Confirmação de ato | administrador de acessos / institucional | leitura do template | não vista no navegador |
| `/gestao/administracao-de-acessos` | `lista` | acessos.html | Lista administrativa | administrador de acessos / institucional | suíte: `acessos-administradores` | captura da suíte |
| `/gestao/administracao-de-acessos/conceder` | `conceder` | acessos_conceder.html, acessos_confirmar.html | Confirmação de ato | administrador de acessos / institucional | leitura do template | não vista no navegador |
| `/gestao/administracao-de-acessos/vinculos/<uuid:vinculo_id>/revogar` | `revogar` | acessos_confirmar.html | Confirmação de ato | administrador de acessos / institucional | leitura do template | não vista no navegador |
| `/gestao/administracao-de-acessos/pessoas` | `pessoas` | acessos_pessoas.html | Lista administrativa | administrador de acessos / institucional | leitura do template | não vista no navegador |
| `/gestao/administracao-de-acessos/pessoas/<str:identificador>/suspender` | `suspender` | acessos_suspensao.html | Confirmação de ato | administrador de acessos / institucional | suíte: `acessos-suspensao` | captura da suíte |
| `/gestao/administracao-de-acessos/pessoas/<str:identificador>/reativar` | `reativar` | acessos_suspensao.html | Confirmação de ato | administrador de acessos / institucional | suíte: `acessos-reativacao` | captura da suíte |

### Agenda

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/agenda` | `agenda` | agenda.html | Central de trabalho | todo perfil da gestão | navegador · 5 estado(s) · paulo.presidente, treino.avaliacao1, treino.formalizacao, treino.presidencia | inspecionada |

### Ajuda

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/documentacao/` | `visao_do_sistema` | index.html | Guia incorporado | todo perfil da gestão | navegador · 1 estado(s) · paulo.presidente, treino.avaliacao1, treino.formalizacao, treino.presidencia | inspecionada |
| `/gestao/documentacao/<path:arquivo>` | `visao_do_sistema` | index.html | Guia incorporado | todo perfil da gestão | leitura do template | não vista no navegador |

### Assistente de dúvidas

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/duvidas/` | `respostas_do_assistente` | duvidas.html | Central de trabalho | participante do piloto | navegador · 1 estado(s) · paulo.presidente, treino.avaliacao1, treino.formalizacao, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/assistente/` | `conversar` | assistente.html | Central de trabalho | participante do piloto | leitura do template | não vista no navegador |

### Auditoria

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/auditoria` | `auditoria` | auditoria.html | Registro e histórico | auditor | navegador · 2 estado(s) · paulo.presidente, treino.presidencia | inspecionada |

### Avaliação

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>` | `distribuicao` | distribuicao.html | Operação com etapas | presidência | navegador · 3 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/consolidar` | `consolidar_resultados` | consolidacao_confirmar.html | Confirmação de ato | presidência | leitura do template | não vista no navegador |
| `/gestao/editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/ocorrencia` | `registrar_ocorrencia` | ocorrencia.html | Confirmação de ato | presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/remover` | `remover_atribuicao` | distribuicao_remover_confirmar.html | Confirmação de ato | presidência | leitura do template | não vista no navegador |
| `/gestao/editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/impedimentos` | `impedimentos` | impedimentos.html | Registro e histórico | presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/trilha` | `trilha_da_avaliacao` | auditoria.html | Registro e histórico | presidência | navegador · 2 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/resultados` | `resultados_da_etapa` | resultados.html | Registro e histórico | presidência | navegador · 2 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/conclusoes` | `conclusoes_preservadas` | conclusoes.html | Registro e histórico | presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |

### Avisos

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/avisos/novo` | `aviso_do_resultado` | aviso_previa.html | Confirmação de ato | presidência, comunicação | navegador · 2 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/convocacao/avisos/novo` | `aviso_da_chamada` | aviso_previa.html | Confirmação de ato | presidência, comunicação | leitura do template | não vista no navegador |
| `/gestao/editais/<uuid:edital_id>/avisos` | `avisos_do_edital` | avisos_do_edital.html | Confirmação de ato | presidência, comunicação | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/avisos/<uuid:aviso_id>` | `aviso` | aviso.html | Confirmação de ato | presidência, comunicação | leitura do template | não vista no navegador |
| `/gestao/avisos/<uuid:aviso_id>/interromper` | `aviso_interromper` | aviso_interromper.html | Confirmação de ato | presidência, comunicação | leitura do template | não vista no navegador |
| `/gestao/avisos/<uuid:aviso_id>/reenviar` | `aviso_reenviar` | aviso_previa.html | Confirmação de ato | presidência, comunicação | leitura do template | não vista no navegador |
| `/gestao/modelos-de-aviso` | `modelos_de_aviso` | modelos_de_aviso.html | Lista administrativa | comunicação, presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/modelos-de-aviso/novo` | `modelo_de_aviso` | modelo_de_aviso.html | Formulário de configuração | comunicação, presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/modelos-de-aviso/<uuid:modelo_id>` | `modelo_de_aviso` | modelo_de_aviso.html | Formulário de configuração | comunicação, presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |

### Centro de Controle

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/` | `detalhe` | detalhe.html | Página de entidade | todo perfil da gestão | navegador · 2 estado(s) · paulo.presidente, treino.avaliacao1, treino.formalizacao, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/pagina-anterior/` | `pagina_anterior` | detalhe.html | Página de entidade | todo perfil da gestão | navegador · 1 estado(s) · paulo.presidente, treino.avaliacao1, treino.formalizacao, treino.presidencia | inspecionada |

### Classificação e vagas

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>` | `ordenacao` | ordenacao.html | Operação com etapas | presidência | navegador · 2 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/emitir` | `emitir_ordenacao` | ordenacao_confirmar.html | Confirmação de ato | presidência | leitura do template | não vista no navegador |
| `/gestao/editais/<uuid:edital_id>/cortes/<uuid:corte_id>` | `corte_historico` | corte_historico.html | Registro e histórico | presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/atos/<uuid:ato_id>` | `ato_de_ordenacao` | ato_ordenacao.html | Registro e histórico | presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/corte` | `corte` | corte.html | Operação com etapas | presidência | navegador · 2 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/corte/emitir` | `emitir_corte_view` | corte_confirmar.html | Confirmação de ato | presidência | leitura do template | não vista no navegador |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/ocupacao` | `ocupacao` | ocupacao.html | Operação com etapas | presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/ocupacao/acrescentar-vagas` | `acrescentar_vagas_view` | ocupacao_acrescimo.html | Confirmação de ato | presidência | leitura do template | não vista no navegador |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/ocupacao/desfazer-acrescimo` | `desfazer_acrescimo_view` | ocupacao_acrescimo.html | Confirmação de ato | presidência | leitura do template | não vista no navegador |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/ocupacao/declarar-nao-preenchida` | `declarar_nao_preenchida` | ocupacao_nao_preenchida.html | Confirmação de ato | presidência | leitura do template | não vista no navegador |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/ocupacao/desfazer-nao-preenchida` | `desfazer_nao_preenchida` | ocupacao_nao_preenchida.html | Confirmação de ato | presidência | leitura do template | não vista no navegador |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/ocupacao/historico` | `ocupacao_historico` | ocupacao_historico.html | Registro e histórico | presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/convocacao/convocar` | `convocar_view` | convocacao_conferir.html | Confirmação de ato | presidência | leitura do template | não vista no navegador |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/convocacao/titulares` | `convocar_titulares_view` | convocacao_conferir.html | Confirmação de ato | presidência | leitura do template | não vista no navegador |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/convocacao/historico` | `convocacao_historico` | convocacao_historico.html | Registro e histórico | presidência | navegador · 2 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/corte/continuar` | `continuar_corte_view` | corte_confirmar.html | Confirmação de ato | presidência | leitura do template | não vista no navegador |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/publicacoes` | `publicacoes_do_marco` | publicacoes_do_marco.html | Registro e histórico | presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/conducao` | `marco` | marco.html | Operação com etapas | presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/conducao/<str:operacao>` | `gesto_do_marco` | marco_conferir.html | Confirmação de ato | presidência | leitura do template | não vista no navegador |

### Comissão

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/processos/<uuid:processo_id>/comissao` | `comissao` | comissao.html, comissao_confirmar.html | Formulário de configuração | gestor, presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/processos/<uuid:processo_id>/alocacoes` | `alocacoes` | alocacoes.html | Formulário de configuração | presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/processos/<uuid:processo_id>/auditoria` | `auditoria_da_comissao` | auditoria.html | Registro e histórico | auditor, presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |

### Composição do Edital

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/reaproveitar` | `reaproveitar` | reaproveitar.html, reaproveitar_confirmar.html | Formulário de configuração | elaborador | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/previa` | `previa` | previa.html | Avaliação ou conferência | elaborador, homologador | navegador · 2 estado(s) · paulo.presidente, treino.presidencia | inspecionada |

### Convocação

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/convocacoes/publicacao` | `publicacao_de_convocados` | publicacao_de_convocados.html | Operação com etapas | presidência, publicador | navegador · 2 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/convocacao` | `convocacao` | convocacao.html | Operação com etapas | presidência | navegador · 3 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/convocacao/<uuid:convocacao_id>/documentos` | `documentos_da_convocacao` | convocacao_documentos.html | Avaliação ou conferência | presidência, conferência | navegador · 1 estado(s) · treino.presidencia | inspecionada |

### Divulgação

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/kit-de-divulgacao/` | `kit` | kit_de_divulgacao.html | Central de trabalho | comunicação | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |

### Formalização

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/acessos/formalizacao` | `formalizacao` | acessos_formalizacao.html | Lista administrativa | administrador de acessos | leitura do template | não vista no navegador |
| `/gestao/formalizacao/` | `lista` | formalizacao_lista.html | Lista administrativa | setor da formalização | navegador · 1 estado(s) · paulo.presidente, treino.formalizacao, treino.presidencia | inspecionada |
| `/gestao/formalizacao/editais/<uuid:edital_id>` | `edital` | formalizacao_edital.html | Página de entidade | setor da formalização | navegador · 1 estado(s) · treino.formalizacao | inspecionada |
| `/gestao/formalizacao/editais/<uuid:edital_id>/verificar` | `verificar` | formalizacao_recusa.html, formalizacao_verificacao.html | Confirmação de ato | setor da formalização | leitura do template | não vista no navegador |
| `/gestao/formalizacao/editais/<uuid:edital_id>/baixar` | `baixar` | formalizacao_recusa.html, formalizacao_verificacao.html | Confirmação de ato | setor da formalização | leitura do template | não vista no navegador |
| `/gestao/formalizacao/editais/<uuid:edital_id>/pessoas/<uuid:inscricao_id>/exportar` | `exportar_pessoa` | formalizacao_recusa.html, formalizacao_verificacao.html | Confirmação de ato | setor da formalização | leitura do template | não vista no navegador |
| `/gestao/editais/<uuid:edital_id>/formalizacao` | `definicao` | formalizacao_definicao.html | Formulário de configuração | presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |

### Inscrições

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/inscricoes` | `inscricoes_recebidas` | inscricoes.html | Lista administrativa | presidência, gestor | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/inscricoes/publicacoes` | `publicacoes_das_inscricoes` | publicacoes_das_inscricoes.html | Operação com etapas | presidência, publicador | navegador · 2 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/inscricoes/<uuid:inscricao_id>/` | `inscricao_recebida` | inscricao_detalhe.html | Página de entidade | presidência, gestor | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |

### Matrículas

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/matriculas` | `exportar_matriculas` | matriculas.html | Operação com etapas | exportador de matrículas | navegador (passada complementar) | inspecionada |

### Mesa de avaliação

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/minhas-etapas/<uuid:edital_id>/<uuid:etapa_id>/inscricoes/<uuid:inscricao_id>` | `inscricao_da_mesa` | mesa_inscricao.html | Avaliação ou conferência | avaliador | navegador · 1 estado(s) · treino.avaliacao1 | inspecionada |
| `/gestao/minhas-etapas/<uuid:edital_id>/<uuid:etapa_id>` | `minha_etapa` | minha_etapa.html | Lista administrativa | avaliador | navegador · 2 estado(s) · treino.avaliacao1 | inspecionada |

### Minhas atividades

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/minhas-etapas` | `minhas_etapas` | minhas_etapas.html | Central de trabalho | comissão | navegador · 1 estado(s) · paulo.presidente, treino.avaliacao1, treino.formalizacao, treino.presidencia | inspecionada |

### Portal — acesso

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/selecoes/acesso` | `acesso` | acesso_email.html | Acesso | candidato | navegador · 2 estado(s) · anonimo, cand5, paulo.presidente, treino.avaliacao1, treino.formalizacao, treino.presidencia | inspecionada |
| `/selecoes/acesso/codigo` | `acesso_codigo` | acesso_codigo.html | Acesso | candidato | navegador · 1 estado(s) · cand1, cand2, cand3, cand4, cand5 | inspecionada |
| `/selecoes/acesso/reconciliar` | `acesso_reconciliar` | acesso_reconciliar.html | Acesso | candidato | leitura do template | não vista no navegador |

### Portal — conta

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/selecoes/meus-dados` | `meus_dados` | meus_dados.html | Jornada do candidato | candidato | navegador · 1 estado(s) · cand1, cand2, cand3, cand4 | inspecionada |
| `/selecoes/conta` | `conta` | conta.html | Jornada do candidato | candidato | navegador · 1 estado(s) · cand1, cand2, cand3, cand4 | inspecionada |
| `/selecoes/conta/emails/<uuid:credencial_id>/remover` | `conta_remover` | conta_remover.html | Jornada do candidato | candidato | leitura do template | não vista no navegador |

### Portal — publicações

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/selecoes/resultados/<uuid:publicacao_id>/` | `resultado` | resultado.html | Portal público | sem autenticação | navegador · 1 estado(s) · cand1, cand2, cand3, cand4, paulo.presidente, treino.avaliacao1, treino.formalizacao, treino.presidencia | inspecionada |
| `/selecoes/inscricoes-publicadas/<uuid:publicacao_id>/` | `publicacao_das_inscricoes` | publicacao_das_inscricoes.html | Portal público | sem autenticação | leitura do template | não vista no navegador |
| `/selecoes/convocacoes/<uuid:publicacao_id>/` | `convocados` | convocados.html | Portal público | sem autenticação | leitura do template | não vista no navegador |
| `/selecoes/sorteio/relacoes/<uuid:relacao_id>/` | `relacao_de_habilitados` | relacao_de_habilitados.html | Portal público | sem autenticação | navegador · 1 estado(s) · treino.presidencia | inspecionada |
| `/selecoes/sorteio/<uuid:sorteio_id>/verificar` | `verificar_sorteio` | verificacao_de_sorteio.html | Portal público | sem autenticação | navegador (passada complementar) | inspecionada |

### Portal — vitrine e seleção

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/selecoes/` | `vitrine` | vitrine.html | Portal público | sem autenticação | navegador · 2 estado(s) · anonimo, cand1, cand2, cand3, cand4, cand5, paulo.presidente, treino.avaliacao1, treino.formalizacao, treino.presidencia | inspecionada |
| `/selecoes/<uuid:edital_id>/` | `selecao` | selecao.html | Portal público | sem autenticação | navegador · 2 estado(s) · anonimo, cand1, cand2, cand3, cand4, cand5, paulo.presidente, treino.avaliacao1, treino.formalizacao, treino.presidencia | inspecionada |

### Portal — área do candidato

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/selecoes/inscricoes/` | `inscricoes` | inscricoes.html | Jornada do candidato | candidato | navegador · 1 estado(s) · cand1, cand2, cand3, cand4 | inspecionada |
| `/selecoes/inscricoes/<uuid:inscricao_id>/` | `inscricao` | descarte.html, inscricao.html, inscricao_enviada.html | Jornada do candidato | candidato | navegador · 1 estado(s) · cand1, cand2, cand3, cand4 | inspecionada |
| `/selecoes/inscricoes/<uuid:inscricao_id>/revisao` | `revisao` | revisao.html | Jornada do candidato | candidato | leitura do template | não vista no navegador |
| `/selecoes/inscricoes/<uuid:inscricao_id>/acompanhamento` | `acompanhamento` | acompanhamento.html | Jornada do candidato | candidato | navegador · 1 estado(s) · cand1, cand2, cand3, cand4 | inspecionada |
| `/selecoes/inscricoes/<uuid:inscricao_id>/convocacao` | `convocacao` | convocacao.html | Jornada do candidato | candidato | navegador · 1 estado(s) · cand1, cand4 | inspecionada |
| `/selecoes/inscricoes/<uuid:inscricao_id>/recorrer` | `recorrer` | recorrer.html | Jornada do candidato | candidato | navegador · 1 estado(s) · cand1, cand2, cand3, cand4 | inspecionada |
| `/selecoes/recursos/<uuid:recurso_id>` | `recurso` | recurso.html | Jornada do candidato | candidato | navegador · 1 estado(s) · cand2 | inspecionada |
| `/selecoes/inscricoes/<uuid:inscricao_id>/requerimento` | `requerimento` | requerimento.html | Jornada do candidato | candidato | navegador · 2 estado(s) · cand4 | inspecionada |
| `/selecoes/inscricoes/<uuid:inscricao_id>/requerimento/anterior/<uuid:requerimento_id>` | `requerimento_anterior` | requerimento_anterior.html | Jornada do candidato | candidato | leitura do template | não vista no navegador |
| `/selecoes/inscricoes/<uuid:inscricao_id>/comprovante` | `comprovante` | comprovante.html | Jornada do candidato | candidato | navegador · 1 estado(s) · cand1, cand2, cand3, cand4 | inspecionada |

### Processos e Editais

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/` | `lista` | lista.html | Central de trabalho | todo perfil da gestão | navegador · 2 estado(s) · paulo.presidente, treino.avaliacao1, treino.formalizacao, treino.presidencia | inspecionada |
| `/gestao/processos/criar` | `criar_processo` | processo_criar.html | Formulário de configuração | gestor, elaborador | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/processos/<uuid:processo_id>/` | `processo_detalhe` | processo_detalhe.html | Página de entidade | todo perfil da gestão | navegador · 1 estado(s) · paulo.presidente, treino.avaliacao1, treino.formalizacao, treino.presidencia | inspecionada |
| `/gestao/processos/<uuid:processo_id>/editais/criar` | `criar_edital` | edital_criar.html | Formulário de configuração | gestor, elaborador | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/processos/<uuid:processo_id>/atos/<slug:acao>` | `praticar_ato_processo` | processo_confirmar.html | Confirmação de ato | gestor | navegador (passada complementar) | inspecionada |
| `/gestao/processos/<uuid:processo_id>/supervisao` | `supervisao` | supervisao.html | Central de trabalho | gestor | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |

### Publicação

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/atos/<slug:acao>` | `praticar_ato` | confirmar.html | Confirmação de ato | elaborador, homologador, publicador | navegador · 3 estado(s) · paulo.presidente, treino.presidencia | inspecionada |

### Recursos

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/recursos` | `recursos_do_edital` | recursos.html | Lista administrativa | julgador, presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/recursos/<uuid:recurso_id>` | `recurso_recebido` | recurso.html | Avaliação ou conferência | julgador, presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/recursos/<uuid:recurso_id>/admitir` | `admitir_recurso` | recurso.html | Avaliação ou conferência | julgador, presidência | leitura do template | não vista no navegador |
| `/gestao/recursos/<uuid:recurso_id>/julgar` | `julgar_recurso` | recurso.html | Avaliação ou conferência | julgador, presidência | leitura do template | não vista no navegador |
| `/gestao/recursos/<uuid:recurso_id>/instruir` | `instruir_recurso` | recurso.html | Avaliação ou conferência | julgador, presidência | leitura do template | não vista no navegador |

### Relatórios

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/relatorio` | `relatorio` | relatorio_do_edital.html | Relatório | gestor, presidência | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |

### Resultados

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/atos/<uuid:ato_id>/publicar` | `previa_de_publicacao` | previa_de_publicacao.html | Confirmação de ato | presidência, publicador | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/atos/<uuid:ato_id>/publicar/confirmar` | `publicar_resultado` | previa_de_publicacao.html | Confirmação de ato | presidência, publicador | leitura do template | não vista no navegador |

### Retificação

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/retificar` | `retificar` | retificar.html | Formulário de configuração | elaborador | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/retificacoes/<uuid:retificacao_id>/` | `retificacao_detalhe` | retificacao_detalhe.html | Página de entidade | todo perfil da gestão | navegador · 1 estado(s) · paulo.presidente, treino.avaliacao1, treino.formalizacao, treino.presidencia | inspecionada |
| `/gestao/retificacoes/<uuid:retificacao_id>/editar` | `retificacao_editar` | retificar.html | Formulário de configuração | elaborador | leitura do template | não vista no navegador |
| `/gestao/retificacoes/<uuid:retificacao_id>/atos/<slug:acao>` | `praticar_ato_retificacao` | retificacao_confirmar.html | Confirmação de ato | elaborador, homologador, publicador | navegador (passada complementar) | inspecionada |

### Sorteio

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/editais/<uuid:edital_id>/marcos/<uuid:marco_id>/sorteio` | `sorteio` | sorteio.html | Operação com etapas | presidência | navegador · 1 estado(s) · treino.presidencia | inspecionada |

### Unidade

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/trilha-da-unidade` | `trilha_da_unidade` | trilha_da_unidade.html | Registro e histórico | gestor, auditor | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/autoridades` | `autoridades` | autoridades.html | Formulário de configuração | gestor | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |

### Unidades

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/administracao-de-unidades` | `lista` | unidades.html | Lista administrativa | administrador institucional | leitura do template | não vista no navegador |
| `/gestao/administracao-de-unidades/cadastrar` | `cadastrar` | unidades_conferencia.html, unidades_formulario.html | Formulário de configuração | administrador institucional | suíte: `unidades-conferencia` | captura da suíte |
| `/gestao/administracao-de-unidades/unidades/<str:codigo>` | `ficha` | unidades_ficha.html | Página de entidade | administrador institucional | leitura do template | não vista no navegador |
| `/gestao/administracao-de-unidades/unidades/<str:codigo>/editar` | `editar` | unidades_conferencia.html, unidades_formulario.html | Formulário de configuração | administrador institucional | leitura do template | não vista no navegador |
| `/gestao/administracao-de-unidades/unidades/<str:codigo>/desativar` | `desativar` | unidades_situacao.html | Confirmação de ato | administrador institucional | leitura do template | não vista no navegador |
| `/gestao/administracao-de-unidades/unidades/<str:codigo>/reativar` | `reativar` | unidades_situacao.html | Confirmação de ato | administrador institucional | leitura do template | não vista no navegador |

### Visão Geral

| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |
|---|---|---|---|---|---|---|
| `/gestao/visao-geral` | `visao_geral` | visao_geral.html | Central de trabalho | gestor | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/visao-geral/relatorio` | `relatorio_consolidado_escolha` | relatorio_consolidado_escolha.html | Formulário de configuração | gestor | navegador · 1 estado(s) · paulo.presidente, treino.presidencia | inspecionada |
| `/gestao/visao-geral/relatorio/conjunto` | `relatorio_consolidado` | relatorio_consolidado.html | Relatório | gestor | navegador (passada complementar) | inspecionada |
