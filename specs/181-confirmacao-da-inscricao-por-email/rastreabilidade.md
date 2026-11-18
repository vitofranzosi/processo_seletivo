# Rastreabilidade — 181 · A confirmação da inscrição por e-mail

**Frase que governa**: *a confirmação diz "enviada", sai uma vez, e cada tentativa deixa rastro.*

Caminhos de código relativos a `backend/processo_seletivo/`. As abreviações:

- **CE** — `tests/integration/inscricoes/test_confirmacao_por_email.py` (o comando, sem tela)
- **CI** — `tests/integration/portal/test_confirmacao_de_inscricao.py` (a jornada pela tela)
- **AE** — `tests/unit/test_apresentacao_dos_emails.py` (a mensagem composta)
- **SM** — `tests/test_situacoes_de_mensagem.py` (nenhum remetente novo)

**Estado em 18/11**: implementado. A suíte inteira contra PostgreSQL, com 4 workers, fechou em
**21797 passando e 29 pulados, sem falha** (sem os grupos `assistente` e `navegador`); depois das correções da revisão de código, **21804 passando e 29 pulados, sem falha**. A primeira
passada acusou três guardiões — o rótulo da operação na trilha legível, a linha no `README` e o caso
sem sessão de `tests/authorization/test_idor_area.py` —, corrigidos antes da segunda. A verificação no
navegador, com as capturas em `capturas/`, está descrita ao fim.

---

## Requisitos funcionais

| Requisito | Onde | Prova |
|---|---|---|
| FR-8350 | `inscricoes/application/confirmacao.py` (`confirmar`: só `SUBMETIDA`); `portal/views.py` `revisao` (só depois de `enviar_inscricao`) | CE: `test_o_rascunho_nao_recebe_confirmacao`; CI: `test_envio_recusado_nao_manda_mensagem` |
| FR-8351 | `confirmacao.confirmar` (trava consultiva sem espera, leitura das tentativas antes de enviar) | CE: `test_a_segunda_chamada_nao_envia_nem_registra`, `test_duas_requisicoes_simultaneas_mandam_uma_mensagem`, `test_com_outra_tentativa_em_curso_volta_sem_esperar_e_sem_enviar`; CI: `test_a_aba_antiga_nao_manda_a_segunda`, `test_voltar_ao_comprovante_nao_reenvia_a_mensagem`, `test_dois_cliques_simultaneos_no_envio_mandam_uma_mensagem` |
| FR-8352 | `portal/views.py` `_confirmar_por_email`, depois do commit; `confirmacao.confirmar` contém toda exceção | CI: `test_falha_no_envio_da_mensagem_nao_custa_a_inscricao`, `test_falhou_a_tela_avisa_e_a_titular_tenta_de_novo`, `test_falha_de_banco_na_confirmacao_nao_derruba_o_envio`; CE: `test_a_falha_e_registrada_como_nao_enviada`, `test_nenhuma_falha_do_caminho_escapa_de_confirmar` |
| FR-8353 | `inscricoes/templates/inscricoes/mensagem/comprovante.txt` (primeira linha); `mensagem.compor_comprovante` (`edital`) | AE: `test_o_assunto_do_comprovante_diz_enviada_e_o_edital`; CI: `test_o_assunto_diz_enviada_e_nomeia_o_edital` |
| FR-8354 | os dois modelos da mensagem | CI: `test_a_mensagem_nao_usa_as_palavras_de_outros_degraus` |
| FR-8355 | os dois modelos ("O que acontece agora", sem "nada a fazer") | CI: `test_a_mensagem_traz_o_que_a_pessoa_precisa_guardar`; AE: `test_o_comprovante_nao_leva_cpf_nem_telefone_e_guarda_o_que_os_testes_guardam` |
| FR-8356 | `portal/views.py` `_dados_da_confirmacao` (sem CPF, telefone e anexo) | CI: `test_a_mensagem_nao_carrega_CPF_nem_telefone`, `test_sem_anexo_e_sem_link_que_autentica` |
| FR-8357 | `_dados_da_confirmacao` (`endereco`); `portal/views.py` `comprovante` (sem sessão, ao acesso) | CI: `test_o_link_leva_ao_comprovante_de_quem_esta_com_sessao`, `test_o_link_sem_sessao_leva_ao_acesso_e_volta_ao_comprovante`, `test_sem_sessao_o_identificador_inventado_recebe_o_mesmo_redirecionamento`; `tests/authorization/test_idor_area.py`: `test_sem_sessao_o_comprovante_leva_ao_acesso_e_nada_dele` |
| FR-8358 | `confirmacao.confirmar` (`record_event`, `detalhe`) | CE: `test_a_enviada_recebe_e_a_tentativa_fica_na_trilha`, `test_a_trilha_nao_guarda_endereco_nome_nem_protocolo` |
| FR-8359 | `confirmacao.ENVIADA`; `portal/templates/portal/comprovante.html` ("Enviamos", "caixa de spam") | CI: `test_o_comprovante_diz_inscricao_enviada_e_para_onde_foi_a_mensagem` |
| FR-8360 | `mensagem.enviar_comprovante` (conta o retorno) | CE: `test_a_falha_e_registrada_como_nao_enviada[nao-aceita]` |
| FR-8361 | `mensagem.enviar_comprovante` (log com `inscricao_id`) | CE: `test_o_log_diz_a_inscricao_e_nao_o_endereco` |
| FR-8362 | `comprovante` (`confirmacao.ultima`); `comprovante.html` | CI: `test_o_comprovante_diz_inscricao_enviada_e_para_onde_foi_a_mensagem`, `test_falhou_a_tela_avisa_e_a_titular_tenta_de_novo`, `test_sem_tentativa_o_comprovante_nao_fala_da_mensagem` |
| FR-8363 | `portal/views.py` `confirmar_de_novo` (`ESPERE_PARA_TENTAR_DE_NOVO`); `portal/urls.py` `comprovante-confirmacao`; `confirmacao.INTERVALO_ENTRE_TENTATIVAS` | CI: `test_falhou_a_tela_avisa_e_a_titular_tenta_de_novo`, `test_dentro_do_intervalo_a_tela_pede_para_esperar_e_nada_sai`; CE: `test_depois_da_falha_a_nova_tentativa_envia_e_e_a_segunda`, `test_dentro_do_intervalo_a_nova_tentativa_nao_sai` |
| FR-8364 | `confirmar_de_novo` (`_inscricao_do_titular`, só enviada) | CI: `test_nova_tentativa_so_da_titular_e_da_enviada` |
| FR-8365 | `comprovante.html` ("✓ Inscrição enviada") | CI: `test_o_comprovante_diz_inscricao_enviada_e_para_onde_foi_a_mensagem`; `tests/integration/portal/test_revisao_e_comprovante.py`; `tests/acceptance/test_jornada_do_candidato.py` |
| FR-8366 | `comprovante.html` (`nao-imprime`); o PDF não lê a tentativa | CI: `test_o_aviso_da_mensagem_fica_fora_do_papel` |
| FR-8367 | um caminho só até `SUBMETIDA` (`revisao` → `enviar_inscricao` → `_confirmar_por_email`), sem ramo por Processo, Perfil ou concorrência | CE e CI exercitam dois Perfis (docente e técnico) e a concorrência ampla; o diagnóstico da `research.md` mostra que não há outro caminho |
| FR-8368 | a trava e as tentativas são por inscrição | CE: `test_duas_inscricoes_da_mesma_pessoa_tem_cada_uma_a_sua` |

## Requisitos de experiência

| Requisito | Onde | Prova |
|---|---|---|
| UX-1020 | `comprovante.html` da mensagem (ordem dos blocos) | `capturas/1-mensagem.jpg`; AE: `test_o_html_nao_diz_nada_que_o_texto_nao_diga`, `test_todo_endereco_e_do_portal_ou_o_canal` |
| UX-1021 | os dois modelos e o aviso da tela | CI: `test_a_mensagem_nao_usa_as_palavras_de_outros_degraus`; leitura das capturas |
| UX-1022 | `comprovante.html` (classe `secundario`, depois do aviso; "Baixar o comprovante em PDF" continua `principal`) | `capturas/3-comprovante-falha.jpg`, `capturas/4-comprovante-falha-celular.jpg` |

## Critérios de sucesso

| Critério | Prova |
|---|---|
| SC-2920 | todo envio pela tela chama `confirmar`, que registra antes de responder — CI: `test_o_envio_deixa_recibo_na_caixa_de_quem_enviou`; CE: `test_a_enviada_recebe_e_a_tentativa_fica_na_trilha` |
| SC-2921 | as provas da FR-8351 |
| SC-2922 | as provas da FR-8356; SM: nenhum remetente novo |
| SC-2923 | CI: `test_o_comprovante_diz_inscricao_enviada_e_para_onde_foi_a_mensagem`, `test_o_assunto_diz_enviada_e_nomeia_o_edital`; a área do candidato já dizia "Inscrição enviada" (`portal/situacao.py`) |
| SC-2924 | CI: `test_o_link_sem_sessao_leva_ao_acesso_e_volta_ao_comprovante` |
| SC-2925 | CE: `test_depois_da_falha_a_nova_tentativa_envia_e_e_a_segunda` |

## Casos-limite

| Caso | Prova |
|---|---|
| Servidor que aceita a conexão e não a mensagem | CE: `test_a_falha_e_registrada_como_nao_enviada[nao-aceita]` |
| Servidor que demora | `EMAIL_TIMEOUT` (já existente); verificado no navegador com `EMAIL_TIMEOUT=2` e porta fechada — sem caso automatizado de demora |
| Trilha que falha depois de a mensagem sair | CE: `test_a_trilha_que_falha_nao_derruba_quem_pediu` |
| E-mail principal trocado depois do envio | `confirmar` usa `inscricao.email`, congelado no envio (FR-013 da `010`) — sem caso próprio |
| Duas inscrições da mesma pessoa | CE: `test_duas_inscricoes_da_mesma_pessoa_tem_cada_uma_a_sua` |
| Nova tentativa alheia ou em rascunho | CI: `test_nova_tentativa_so_da_titular_e_da_enviada` |
| Nova tentativa durante outra da mesma inscrição | CE: `test_com_outra_tentativa_em_curso_volta_sem_esperar_e_sem_enviar`, `test_duas_requisicoes_simultaneas_mandam_uma_mensagem` |
| Dois cliques no envio, e a primeira tentativa falhou | CE: `test_dentro_do_intervalo_a_nova_tentativa_nao_sai` |
| Inscrição sem endereço | CE: `test_sem_endereco_nao_tenta_nem_registra` |
| Edital retificado depois do envio | `_dados_da_confirmacao` lê a versão aceita, como o comprovante; nenhuma Retificação chama `confirmar` |
| Cenários de treinamento da `134` | criam enviadas sem chamar `confirmar`; CI: `test_sem_tentativa_o_comprovante_nao_fala_da_mensagem` cobre a tela sem tentativa |
| Chave dos avisos da `066` desligada | `confirmar` não a lê |

## Verificação no navegador (18/11)

Banco `ps_181_demo` (`seed_demo`), entradas `confirmacao-181` (correio de console) e
`confirmacao-181-correio-fora` (SMTP numa porta fechada) do `.claude/launch.json`, sobre o mesmo banco:

1. Maria enviou pela tela: o comprovante disse "Enviamos a confirmação para m@ex.br", e o terminal do
   servidor mostrou **uma** mensagem, de assunto "Sua inscrição foi enviada — Edital 01/2026"
   (`capturas/1-mensagem.jpg`, `capturas/2-comprovante-enviada.jpg`).
2. Sem sessão, o link da mensagem levou ao acesso com o comprovante como destino.
3. João enviou pelo servidor sem correio: o comprovante mostrou o aviso e o botão
   (`capturas/3-comprovante-falha.jpg`, e a 375 px em `capturas/4-comprovante-falha-celular.jpg`, sem
   rolagem horizontal); o log técnico disse a inscrição pelo identificador, sem o endereço.
4. A nova tentativa pelo servidor com correio enviou, e a tela passou a "Enviamos". A trilha: Maria,
   tentativa 1 enviada; João, tentativa 1 não enviada e tentativa 2 enviada.
5. Nenhuma violação de CSP no console.
