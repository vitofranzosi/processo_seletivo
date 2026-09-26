# Lote 1 — Fundação e capacidade (02/09 a 12/09) — auditoria de consolidação

Base verificada: `bb774d9` (= origin/main de 25/09/2026). Somente leitura. Caminhos de código
relativos a `backend/processo_seletivo/` salvo indicação; `tests/…` e `config/…` são relativos a `backend/`; `specs/…`, `doc/…` e `README.md` à raiz do repositório.

Documentos cobertos: `doc/auditoria-exploratoria-e2e-2026-09-02.md` (E2E-0xx),
`doc/avaliacao-de-capacidade-editais-2026-09-07/08/09/11/12.md` (L-1…L-6, lacunas com endereço,
pressões, resíduos), `doc/achados-editais-externos.md` (P-1…P-13, Edital grande), `doc/e2e/*/`
(014, 015, 016, 017, 018, 019, 020, 025 — só o que ficou aberto).

Convenção: "verificado" = li o código/teste citado nesta sessão. Não rodei suíte nem servidor.

---

## Parte A — Auditoria E2E de 02/09 (`E2E-0xx`)

### E2E-001, E2E-002, E2E-021 — Devolução do Edital e da Retificação; quem cancela Retificação
- Origem: `doc/auditoria-exploratoria-e2e-2026-09-02.md` §10, §14, pendência E2E-021 (02/09)
- Problema original: Edital em revisão sem caminho de volta; `devolver` de Retificação só na API; `retificacao:cancelar` sem papel.
- Recomendação original: ato "Devolver à elaboração" (Edital e Retificação); decidir dono do cancelamento.
- Rastro posterior: corrigidos em 02–04/09 (preâmbulo do próprio doc); decisão de governança E2E-021 de 02/09 (Gestor cancela, só em elaboração).
- Specs relacionadas: 001/002, 004.
- Implementação encontrada: atos `devolver` no Edital e na Retificação; `TRANSITIONS` do domínio estreitado.
- Evidência no código atual: `interface/atos.py:76-88` (Devolver para elaboração, `edital:homologar`, EM_REVISAO); `interface/atos_retificacao.py:87-100` (devolver) e `:101-110` (cancelar, `CANCELAVEL`); `publicacoes/application/retificacoes.py:333-349` (`cancelar` só de EM_ELABORACAO; `devolver` exige `retificacao:homologar`); `interface/identidade.py:57` (`retificacao:cancelar` no Gestor). Testes: `tests/interface/test_devolucao.py`, `tests/interface/test_devolucao_da_retificacao.py`.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não — fechado.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma
- Relações: E2E-021 nasceu da correção do E2E-002; a lição "metade da causa no domínio" repetiu-se depois (E2E17-001, E2E18-005).
- Confiança: alta — código e testes nomeados.

### E2E-003 — Lista de Inscrições recebidas sem paginação/filtro/contadores
- Origem: E2E 02/09 §9, §10 (02/09)
- Problema original: 60 linhas numa página, sem busca, filtro nem contagem por Perfil/modalidade.
- Recomendação original: paginar + filtrar (perfil, modalidade, situação, busca) + contadores.
- Rastro posterior: corrigido em 02/09 (preâmbulo).
- Specs relacionadas: 009 (FR-066/067).
- Implementação encontrada: `consulta_de_inscricoes` paginada, com busca, Perfil e Modalidade; rascunhos em seção própria fora do total; cartões por Perfil.
- Evidência no código atual: `interface/views.py:4079-4125` (`pagina`, `pagina_rascunhos`, `busca`, `perfil`, `modalidade`, filtro preservado nos links).
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma (filtro por "situação" virou separação submetidas × rascunhos, que é a distinção que importa).
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma
- Relações: a exportação continua deliberadamente fora (§12 do doc); a 031 criou exportação de matrículas, que é outra coisa.
- Confiança: alta.

### E2E-004 — Retificação pela tela não alcança Documentos Exigidos (acrescentar/remover)
- Origem: E2E 02/09 §10 e pendência E2E-004 (02/09; implementado em parte em 04/09)
- Problema original: Retificar não alcançava `documentRequirements`, `maximumScore`, `evaluationsPerRegistration`, marca de período.
- Recomendação original: cobrir as coleções retificáveis restantes.
- Rastro posterior: 04/09 — edição dos campos do Documento Exigido entrou (tipo `REFERENCIA` para Perfil/Modalidade); acrescentar/remover ficou fora "por razão normativa". 13/09 — contrato de mutabilidade (`doc/decisao-mutabilidade-normativa.md`, spec 026) classifica cada campo. 25/09 — 044 (só spec) reafirma: "Acrescentar e remover Documento Exigido continuam fora da Retificação" (`specs/044-…/spec.md:400`, `D-009` em `:564-572`).
- Specs relacionadas: 004, 012, 026, 044.
- Implementação encontrada: campos do documento retificáveis; grupo não removível e sem acréscimo.
- Evidência no código atual: `interface/retificacao.py:966-981` (`removivel=False`, comentário com a razão normativa); `interface/retificacao.py:1054` (`SECOES_QUE_ACRESCENTAM` não inclui documentos); `editais/domain/mutabilidade.py:481-493` (name/instructions/required/order/profileId/modalityId/attachmentId retificáveis; `key` não).
- Estado atual: CONTRADITO POR DECISÃO POSTERIOR — a parte "acrescentar/remover" foi recusada com razão normativa registrada no código (04/09) e reafirmada como `D-009` da 044 (25/09); a parte de edição está RESOLVIDA.
- Ainda faz sentido?: parcialmente — a razão normativa é boa (acrescentar obrigatório torna incompleta inscrição já enviada); mas "remover" um documento facultativo, ou acrescentar um facultativo, não tem o mesmo problema e nunca foi decidido separadamente.
- Lacuna residual: acrescentar/remover Documento Exigido **facultativo** por Retificação não tem decisão própria; hoje exige cancelar/novo Edital ou conviver com o erro.
- Grupo do resíduo: C
- Impacto atual: baixo; o caso real (documento pedido errado) se corrige editando `required`/`instructions`/recorte.
- Próxima ação sugerida: nenhuma (registrar a distinção obrigatório × facultativo se a questão voltar)
- Relações: E2E14-005 e G16-001 (mesma família: o que a Retificação alcança) → contrato 026.
- Confiança: alta.

### E2E-005 — Estado "Ativo" do Processo sem significado operacional
- Origem: E2E 02/09 §10 (02/09)
- Problema original: Processo corria inteiro "Em elaboração"; Encerrar exigia ativar antes.
- Recomendação original: inferir ativação na 1ª publicação, ou dar consequência real ao estado.
- Rastro posterior: `c6d2187 fix(E2E-005): publicar o primeiro Edital abre o certame`.
- Specs relacionadas: 001/002.
- Implementação encontrada: ativação derivada da publicação do primeiro Edital, com `AtoAdministrativo` próprio e motivo.
- Evidência no código atual: `publicacoes/application/publish_edital.py:789-835` (`_ativar_o_processo_na_primeira_publicacao`). Testes que citam E2E-005: `tests/interface/test_processo.py`, `tests/interface/test_lista.py`.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma
- Relações: —
- Confiança: alta.

### E2E-006, E2E-007 — Rascunho local contraditório; resumo de congelamento incompleto
- Origem: E2E 02/09 §10 (02/09)
- Problema original: banner "preenchimento não enviado" depois de salvar; Revisão omitia `maximumScore`/`evaluationsPerRegistration`.
- Recomendação original: limpar rascunho local no save; incluir os campos no resumo.
- Rastro posterior: corrigidos em 02/09.
- Specs relacionadas: 006/007, 012.
- Implementação encontrada: `rascunho.js` limpa a chave quando o renderizado coincide com o guardado ou há recibo de gravação; `revisao.py` imprime os campos da 012.
- Evidência no código atual: `interface/static/interface/rascunho.js:51,151,196,210` (`removeItem`); `interface/revisao.py:131-138` (pontuação máxima e demais, com comentário do incremento da 012).
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma no escopo destes dois (o AX-16 de 15/09 — restaurar rascunho perde coleções aninhadas — é defeito vizinho, de outro lote).
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma
- Relações: AX-16 (15/09) é da mesma família do rascunho local.
- Confiança: média-alta — não rodei o JS; a leitura do código confirma a limpeza.

### E2E-008 — Mesa: contadores não filtram; lista sem nome do candidato
- Origem: E2E 02/09 §6, §10 (02/09)
- Problema original: com 500 atribuições, achar "as 3 em rascunho" era paginação manual; linha só com protocolo.
- Recomendação original: contadores clicáveis como filtros; nome na linha.
- Rastro posterior: nenhum documento posterior o reabre.
- Specs relacionadas: 012.
- Implementação encontrada: filtros por estado com contagem (total, não iniciadas, rascunho, concluídas); a linha continua só com protocolo e situação.
- Evidência no código atual: `avaliacoes/application/selectors.py:266-330` (filtros `CONCLUIDAS`, `RASCUNHOS`, `NAO_INICIADAS`, `PENDENTES`); `interface/templates/interface/minha_etapa.html:65-73` (contadores como links de filtro), `:84-92` (tabela: Inscrição = protocolo, Situação).
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: parcialmente — a metade de maior valor (filtrar) está feita; o nome na linha é conveniência, e o protocolo é a identificação que o resto do sistema usa.
- Lacuna residual: nome do candidato ausente na lista da Mesa.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma
- Relações: —
- Confiança: alta.

### E2E-009 — Impedimentos/Conclusões: inscrição indicada digitando protocolo exato
- Origem: E2E 02/09 §5, §10 (02/09; "Apenas registrar")
- Problema original: erro de digitação vira recusa; cópia manual entre telas.
- Recomendação original: picker/autocomplete de inscrição.
- Rastro posterior: nenhum.
- Specs relacionadas: 012.
- Implementação encontrada: o campo continua texto livre, mas aceita protocolo ou UUID, e o ato de impedimento passa por tela de confirmação.
- Evidência no código atual: `interface/templates/interface/impedimentos.html:71-75` (input texto, ajuda "Protocolo da inscrição … ou o identificador"), `:26-36` (confirmação com alcance); `interface/views.py:7113-7129` (`_inscricao_do_filtro` aceita protocolo ou UUID); filtro de Conclusões em `interface/templates/interface/conclusoes.html:25`.
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: pouco — com a confirmação antes de gravar, o erro de digitação não produz ato errado; o custo é só redigitar.
- Lacuna residual: sem seletor/autocomplete.
- Grupo do resíduo: C
- Impacto atual: baixo (volume de impedimentos é pequeno).
- Próxima ação sugerida: nenhuma
- Relações: —
- Confiança: alta.

### E2E-010 — Forma canônica vazando nas telas administrativas (`20.0000%`, `1.0000`, UUID de versão)
- Origem: E2E 02/09 §3, §10 (02/09; "Apenas registrar")
- Problema original: decimais de 4 casas e UUID de versão em Revisão e Conclusões preservadas.
- Recomendação original: humanizar pelo mesmo helper do compositor.
- Rastro posterior: retomado como **ACH-17** (P3) em `doc/auditoria-exploratoria-ux-2026-09-16.md:1042` (e `diario-reauditoria-2026-09-16.md:190`: "40 reexibe como 40.0000").
- Specs relacionadas: 007, 012.
- Implementação encontrada: nenhuma na Revisão.
- Evidência no código atual (checagem pontual): `interface/revisao.py:50-51` (`f"{regra['percentage']}%"`), `:129-130` (`Peso: {etapa['weight']}`), `:131-138` (nota mínima/pontuação máxima crus); a forma é de 4 casas por construção (`publicacoes/application/publish_edital.py:35-42`, `_decimal_canonico`). UUID da versão ainda impresso como `<span class="codigo">` em `interface/templates/interface/conclusoes.html:64-65`.
- Estado atual: DUPLICADO / ABSORVIDO (ACH-17, 16/09)
- Ainda faz sentido?: sim, como polimento.
- Lacuna residual: decimais canônicos na Revisão; UUID de versão ao lado da data em Conclusões (este último é "detalhe técnico" ao lado do instante, aceitável).
- Grupo do resíduo: C
- Impacto atual: ruído na tela de quem submete.
- Próxima ação sugerida: corrigir (no lote que cuida de ACH-17)
- Relações: E2E15-006/E2E17-003 (mesma classe nas telas da 015, já fechada).
- Confiança: alta.

### E2E-011 — Comprovante do candidato com SHA-256 e instruções de terminal em bloco aberto
- Origem: E2E 02/09 §4, §8, §10 (02/09; "Apenas registrar")
- Problema original: integridade competindo com a tarefa.
- Recomendação original: progressive disclosure ("verificar integridade").
- Rastro posterior: a auditoria de UX de 13/09 lista o comprovante (protocolo, código de verificação, SHA-256 por arquivo) entre os pontos fortes (`doc/auditoria-exploratoria-ux-2026-09-13.md:120,634`).
- Specs relacionadas: 009, 010.
- Implementação encontrada: sem mudança; o comentário do template defende o hash como prova.
- Evidência no código atual: `portal/templates/portal/comprovante.html:66-91` (SHA-256 por documento, sempre visível), `:114-119` (`shasum`/`certutil` abertos), `:134-138` (SHA-256 do PDF).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: pouco — auditoria posterior avaliou o comprovante como forte; a mudança seria só recolher as instruções de terminal num `<details>`.
- Lacuna residual: instruções técnicas sempre expostas.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma
- Relações: —
- Confiança: alta.

### E2E-012 — "3 documentos que serão pedidos" ignora a modalidade
- Origem: E2E 02/09 §4, §10 (02/09; "Apenas registrar")
- Problema original: o resumo contava documento de outra modalidade.
- Recomendação original: "2 a 3 documentos, conforme a concorrência".
- Rastro posterior: 024 (descoberta no portal) reorganizou o bloco.
- Specs relacionadas: 009, 024.
- Implementação encontrada: o bloco aberto separa "sempre" de "Se concorrer em X, também:"; o resumo fechado ainda soma tudo.
- Evidência no código atual: `portal/views.py:249-258` (`total` = sempre + soma por modalidade); `portal/templates/portal/selecao.html:154` (summary com o total), `:155-166` (lista por modalidade).
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: parcialmente — quem abre o bloco lê certo; o número do resumo continua superestimando.
- Lacuna residual: o `summary` deveria dizer "N (mais M conforme a concorrência)".
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma (ou ajuste de uma linha se alguém tocar a tela)
- Relações: —
- Confiança: alta.

### E2E-013 — Pós-publicação: nada leva à vitrine nem sugere constituir a comissão
- Origem: E2E 02/09 §7, §10 (02/09)
- Problema original: o próximo passo do fluxo inteiro ficava na cabeça das pessoas.
- Recomendação original: CTA pós-publicação (ver na vitrine) e painel do Processo apontando comissão/alocação pendentes.
- Rastro posterior: retomado pela melhoria 13.6 da reauditoria de 16/09 ("não desligar o guia") → spec **038** (painel de condução); sinais de Atenção da 022/038.
- Specs relacionadas: 022, 038.
- Implementação encontrada: Supervisão/Painel com sinais de cobertura de avaliação e trabalho pendente; nenhum link "ver na vitrine" no detalhe do Edital.
- Evidência no código atual (pontual): `interface/supervisao.py:467-493` (`UX-003` cobertura, `UX-063` trabalho pendente, `UX-065` ordem sem apuração…); `interface/acoes.py:85-160` (`_navegacao` não oferece link à página pública).
- Estado atual: DUPLICADO / ABSORVIDO (melhoria 13.6 / spec 038)
- Ainda faz sentido?: parcialmente — o guia pós-publicação é do outro lote; o link "ver na vitrine" é detalhe.
- Lacuna residual: sem atalho do Edital publicado para a página pública.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma (verificação do guia fica com o lote de 038)
- Relações: E2E-016 (handoffs sem sinal ativo); E2E15-016 (caminho da presidência não anunciado).
- Confiança: média — não conferi se o sinal "comissão não constituída" existe literalmente; `UX-003` mede cobertura por Etapa.

### E2E-014 — Seletor de identidade: "Ou entre por outro nome" sem lista acima
- Origem: E2E 02/09 §10 (02/09; "Apenas registrar")
- Problema original: rótulo "Ou" sem alternativa anterior em ambiente sem vínculos.
- Recomendação original: esconder o "Ou" quando a lista está vazia.
- Rastro posterior: nenhum.
- Specs relacionadas: 002 (FR-058: o seletor some com o diretório).
- Implementação encontrada: inalterado.
- Evidência no código atual: `interface/templates/interface/identificar.html:17-41` (lista condicionada a `com_trabalho`; o rótulo "Ou entre por outro nome" é incondicional).
- Estado atual: SUPERADO / OBSOLETO — superfície de demonstração que produção recusa e que desaparece com a integração do diretório.
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma relevante.
- Grupo do resíduo: —
- Impacto atual: nenhum para usuário real.
- Próxima ação sugerida: nenhuma
- Relações: T056 da 002 (LDAP) — ver resíduos da capacidade.
- Confiança: alta.

### E2E-015 — Matriz de recusa HTTP dos POSTs da 012
- Origem: E2E 02/09 §8, §10, §14 (02/09)
- Problema original: escrita da Mesa, `distribuicao-remover`, `impedimentos`, `compor`/`retificar` sem teste de recusa.
- Recomendação original: fechar a matriz nos testes.
- Rastro posterior: corrigido em 02/09.
- Specs relacionadas: 012.
- Implementação encontrada: testes de autorização por POST.
- Evidência: `tests/authorization/test_mesa_por_post.py`, `tests/authorization/test_impedimento_superveniente.py`, `tests/authorization/test_julgamento_de_recurso.py` (e o restante de `tests/authorization/`).
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma que eu tenha verificado (não conferi rota a rota).
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma
- Relações: 033 (navegação por capacidade) e o inventário de negativas da 033 cobram 404 novo.
- Confiança: média — confirmei a existência dos arquivos, não a cobertura de cada rota.

### E2E-016 — Nenhuma notificação nas passagens de bastão
- Origem: E2E 02/09 §7, §10, §12 (02/09; "Feature futura — registrar, não implementar")
- Problema original: handoffs dependem de combinação informal.
- Recomendação original: registrar; não implementar por ora.
- Rastro posterior: 017 e 018 declaram "comunicação ativa" fora de escopo (`specs/018-…/spec.md:1242`); 040 exclui notificações (`specs/040-…/spec.md:636,895`); a 019 criou comunicação **da convocação** ao candidato (`convocacao/application/comunicar.py`); a 038 respondeu com guia/painel, não com aviso.
- Specs relacionadas: 010, 017, 018, 019, 022, 038, 040.
- Implementação encontrada: e-mail só para código de acesso, mensagens de inscrição e comunicação de convocação.
- Evidência no código atual: remetentes de e-mail apenas em `identidade/application/mensagem.py`, `inscricoes/application/mensagem.py`, `convocacao/application/comunicar.py`.
- Estado atual: NÃO IMPLEMENTADO (por decisão de adiamento repetida)
- Ainda faz sentido?: parcialmente — para a gestão, com equipe de 2–3 pessoas acumulando papéis, aviso de handoff vale pouco; para o **candidato** (resultado publicado, recurso decidido), comunicação ativa tem valor real mas depende de SMTP institucional.
- Lacuna residual: comunicação ativa ao candidato fora da convocação.
- Grupo do resíduo: C (gestão) / B (candidato, quando houver SMTP real)
- Impacto atual: candidato precisa voltar ao portal para saber de resultado/recurso.
- Próxima ação sugerida: nenhuma agora; reavaliar com o gate de produção (SMTP)
- Relações: E2E-020, E2E17 §9 "comunicação ativa", G1.
- Confiança: alta.

### E2E-017 — Inscrições que chegam depois da distribuição
- Origem: E2E 02/09 §5, pendência E2E-017 (02/09; corrigido 04/09)
- Problema original: distribuir com prazo aberto era admitido.
- Recomendação original: registrar (a correção foi além: invariante).
- Rastro posterior: `d5e4b01`, `d38f47a` (guarda nos dois caminhos); reconfirmado sem regressão em E2E-017 §8 (06/09).
- Specs relacionadas: 011, 012.
- Implementação encontrada: recusa enquanto o período estiver aberto ou por começar.
- Evidência no código atual: `avaliacoes/application/distribuicao.py:141` (`_exigir_conjunto_fechado`), chamada em `:309`.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma
- Relações: E2E17-006 (horário UTC na recusa, corrigido).
- Confiança: alta.

### E2E-018 — Detalhe da Retificação sem "Aguardando quem homologa/publica"
- Origem: E2E 02/09 §10 (02/09; "Apenas registrar")
- Problema original: assimetria de orientação com o Edital.
- Recomendação original: reusar o padrão do Edital.
- Rastro posterior: nenhum.
- Specs relacionadas: 004.
- Implementação encontrada: o Edital tem o aviso (`interface/templates/interface/detalhe.html:94`); a Retificação não.
- Evidência no código atual: `interface/templates/interface/retificacao_detalhe.html` — cartões "Vigência" e "O que fazer agora", com "Nenhum ato disponível para seus papéis nesta situação" e nenhum `proximo_passo`.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, como polimento barato.
- Lacuna residual: quem não tem o ato vê "nenhum ato disponível" sem saber quem deve agir.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: corrigir quando a tela for tocada
- Relações: —
- Confiança: alta.

### E2E-019 — Toda identidade institucional vê todos os Processos/Editais do escopo
- Origem: E2E 02/09 §10 (02/09; "Confirmar como decisão consciente")
- Problema original: avaliadora vê Processo do qual não participa (só metadados, sem ações).
- Recomendação original: confirmar como decisão.
- Rastro posterior: nenhuma decisão nova; a 040 aplica o mesmo filtro por escopo.
- Specs relacionadas: 002 FR-003 ("lista de Processos Seletivos e Editais do escopo institucional da pessoa", `specs/002-frontend-administrativo/spec.md:225-226`).
- Implementação encontrada: filtro por `institution_scope`, sem filtro por vínculo.
- Evidência no código atual: `processos/application/selectors.py:12-21`; `interface/views.py:225-240`.
- Estado atual: SUPERADO / OBSOLETO — o comportamento é o que o requisito escrito da 002 pede.
- Ainda faz sentido?: não como defeito.
- Lacuna residual: nenhuma (se a instituição quiser reduzir a visibilidade, é decisão nova).
- Grupo do resíduo: —
- Impacto atual: exposição só de metadados institucionais públicos em boa parte.
- Próxima ação sugerida: nenhuma
- Relações: —
- Confiança: alta.

### E2E-020 — Código de acesso por e-mail é ponto único de falha do candidato
- Origem: E2E 02/09 §4, §10, régua final (02/09; "Feature futura")
- Problema original: spam/atraso; reenvio só após 60 s; depende do SMTP real (G1).
- Recomendação original: registrar; monitorar com e-mail real.
- Rastro posterior: produção recusa backend de e-mail que não entrega.
- Specs relacionadas: 010.
- Implementação encontrada: espera de 60 s entre envios; produção exige backend real.
- Evidência no código atual: `identidade/application/desafio.py:36` (`ESPERA_ENTRE_ENVIOS = 60s`); `config/settings/production.py:140-141` (recusa `EMAIL_BACKEND` que não entrega; caminho relativo a `backend/`).
- Estado atual: NÃO IMPLEMENTADO (depende de infraestrutura)
- Ainda faz sentido?: sim, mas é responsabilidade da implantação (SMTP institucional, SPF/DKIM), não de feature.
- Lacuna residual: nenhuma alternativa de acesso; entregabilidade nunca medida.
- Grupo do resíduo: B (gate de implantação)
- Impacto atual: nulo hoje (não há produção); alto no primeiro certame real se o SMTP falhar.
- Próxima ação sugerida: validar na implantação
- Relações: E2E-016; resíduo T056 da 002; memória "código de acesso exige correio local".
- Confiança: alta.

### E2E §12/§13 — Perguntas do gate para a 013 (reabertura de avaliação consumida EC-010; quórum/déficit) e pendências "não corrigir agora"
- Origem: E2E 02/09 §12, §13 (02/09)
- Problema original: a 013 precisava decidir o que fazer com reabertura de avaliação já consumida e com "avaliações por inscrição" não atingidas.
- Recomendação original: entrar na spec da 013 como decisões explícitas.
- Rastro posterior: decididas na 013; a 018 trocou a mensagem da recusa (FR-111).
- Specs relacionadas: 012 (D-006, sem retirada de inscrição), 013, 018.
- Implementação encontrada: reabrir avaliação que fundamenta Resultado é recusado; Etapa com mais de uma avaliação prevista e sem regra de combinação não consolida.
- Evidência no código atual: `avaliacoes/application/avaliacao.py:333-372` (`_recusar_se_fundamenta_resultado`); `resultados/domain/regra.py:71-76` (`REGRA_DE_COMBINACAO_AUSENTE` quando `previstas > 1`); `specs/012-mesa-de-avaliacao/spec.md:241-250` (D-006: não existe retirada de inscrição).
- Estado atual: RESOLVIDO (decidido e implementado)
- Ainda faz sentido?: não como pergunta; o resíduo "Etapa com duas avaliações não consolida" é o avulso `doc/achado-duas-avaliacoes-sem-regra-de-combinacao.md`, de outro lote.
- Lacuna residual: nenhuma neste lote.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `achado-duas-avaliacoes-sem-regra-de-combinacao.md`; E2E15-003 (Mesa × Resultado na própria Etapa).
- Confiança: alta.

---

## Parte B — Relatórios por feature em `doc/e2e/` (só o que ficou aberto)

### E2E14-005 (resíduo) — Retificação não alcança espécie do alvo, Etapa governada e continuação do corte
- Origem: `doc/e2e/014-corte-e-progressao/relatorio.md` §2 E2E14-005 e §4 (11/09)
- Problema original: só `tieOutcome`, `targetCount` e `surplusCount` eram retificáveis; os outros três "igualmente enumeráveis" ficaram fora "por decisão do usuário".
- Recomendação original: decidir; a mesma solução `REFERENCIA` serviria.
- Rastro posterior: `doc/decisao-mutabilidade-normativa.md` (13/09) → spec 026 (matriz aprovada em 13/09).
- Specs relacionadas: 014, 026.
- Implementação encontrada: os três declarados **não retificáveis**, com razão normativa escrita.
- Evidência no código atual: `editais/domain/mutabilidade.py:381-385` (`cutRule/targetKind`: "são duas regras diferentes"), `:391-399` (`governedStage`, `continuation`: "decide quem segue no certame… reescreveria o resultado de um ato já praticado"); `tests/contract/test_mutabilidade.py`.
- Estado atual: CONTRADITO POR DECISÃO POSTERIOR (contrato de mutabilidade, `doc/decisao-mutabilidade-normativa.md` + `editais/domain/mutabilidade.py`)
- Ainda faz sentido?: não — a recusa tem razão normativa sólida.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma
- Relações: E2E-004, G16-001 (mesma família: o que a Retificação alcança).
- Confiança: alta.

### E2E14 §4 (resíduo) — Quickstart da 014 promete recusa onde a tela normaliza
- Origem: `doc/e2e/014-…/relatorio.md` §3 Percurso 1 e §4 (11/09)
- Problema original: guia diz que alvo derivado com número digitado é recusado; a tela descarta o número (decisão em `_regra_de_corte`).
- Recomendação original: aberto (corrigir a redação do guia).
- Rastro posterior: nenhum.
- Specs relacionadas: 014.
- Implementação encontrada: guia inalterado.
- Evidência: `specs/014-corte-e-progressao-entre-etapas/quickstart.md:122` ("recusa: o alvo tem uma fonte só").
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, trivial (documentação).
- Lacuna residual: quickstart divergente do comportamento.
- Grupo do resíduo: C
- Impacto atual: quem segue o guia estranha a ausência da recusa.
- Próxima ação sugerida: corrigir (uma linha; atenção ao guardião de citações `FR-`)
- Relações: —
- Confiança: alta.

### E2E15-003 — A Mesa aceita concluir avaliação de inscrição que já tem Resultado na própria Etapa
- Origem: `doc/e2e/015-exploratoria/relatorio.md` §4 P2 (05–06/09) — "depende de governança"
- Problema original: após ocorrência eliminar a inscrição na Etapa, a Mesa manteve o formulário vivo e aceitou "Deferida" → par contraditório (avaliação Deferida + Resultado Eliminada).
- Recomendação original: decidir a regra e alinhar a Mesa (bloquear ou avisar).
- Rastro posterior: nenhum documento posterior o retoma; o manual ainda o lista como aberto (`doc/manual/00-arquitetura-do-manual.md:1257`).
- Specs relacionadas: 012, 013, 018 (a reavaliação determinada é o caso **legítimo** de avaliar com Resultado vigente).
- Implementação encontrada: nenhuma guarda.
- Evidência no código atual: `avaliacoes/domain/autorizacao.py:42-54` (`pode_avaliar_inscricao` = alocação + `participa_da_etapa` + atribuição); `resultados/application/prontidao.py:450-480` (`participa_da_etapa` olha Resultado **eliminatório em Etapas anteriores** e a faixa do corte, não Resultado na própria Etapa); `avaliacoes/application/avaliacao.py:195-260` (`concluir` sem checagem de Resultado).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim — é a mesma classe de "trabalho morto + registro contraditório" que a 013 fechou para Etapas anteriores. **Mas a regra não pode ser "bloquear sempre"**: a reavaliação determinada (018) exige justamente avaliar de novo quem tem Resultado vigente; a guarda precisa excetuar a pendência de reavaliação.
- Lacuna residual: avaliação concluível depois do Resultado da própria Etapa (por ocorrência ou consolidação), sem aviso.
- Grupo do resíduo: B
- Impacto atual: trilha com par contraditório; nenhum Resultado é alterado (imutável), a avaliação tardia fica inelegível.
- Próxima ação sugerida: corrigir (decisão curta de governança: aviso ou bloqueio com exceção da reavaliação)
- Relações: E2E18-001 (a exceção legítima); `participa_da_etapa` da 013.
- Confiança: alta quanto ao código; média quanto à severidade.

### E2E15-007 — Rascunho aberto depois do encerramento não diz que o prazo acabou
- Origem: `doc/e2e/015-…/relatorio.md` §4 P2 (06/09)
- Problema original: a revisão do rascunho convidava a reconhecer Retificação e continuar, sem mencionar o encerramento.
- Recomendação original: declarar "o período de inscrições terminou em …" antes de qualquer convite.
- Rastro posterior: nenhum; manual ainda o lista como aberto (`doc/manual/00-arquitetura-do-manual.md:1248`).
- Specs relacionadas: 009, 010.
- Implementação encontrada: nenhuma nas telas de rascunho; a recusa existe no domínio (anexar/enviar fora do período).
- Evidência no código atual: `portal/views.py:1183-1270` (`inscricao`) e `:1887-1960` (`revisao`) sem leitura de período; `portal/templates/portal/inscricoes.html:29-35` ("Inscrição não enviada" + ação de continuar, sem condição de prazo); a recusa está em `inscricoes/application/rascunho.py:382` ("fora do período não se anexa nada").
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim — barato, e é informação que o candidato precisa antes de preencher.
- Lacuna residual: nenhum aviso de prazo encerrado no rascunho nem em "Minhas inscrições".
- Grupo do resíduo: B
- Impacto atual: candidato descobre o encerramento só ao tentar anexar/enviar.
- Próxima ação sugerida: corrigir
- Relações: `portal/templates/portal/_periodo.html:22-23` já sabe dizer "Inscrições encerradas em …" — é reuso.
- Confiança: alta.

### E2E15-012 — 404 técnico do Django na recusa da Mesa alheia
- Origem: `doc/e2e/015-…/relatorio.md` §4 P3 (06/09)
- Problema original: página de depuração do Django na gestão, contra o 404 institucional do portal.
- Recomendação original: (implícita) 404 institucional na gestão.
- Rastro posterior: hardening pós-017 (`17ab044`) criou `404.html` institucional para os dois canais.
- Specs relacionadas: 017 (hardening).
- Evidência no código atual: `shared/templates/404.html` (comentário cita E2E17-002; não diz por quê, de propósito).
- Estado atual: RESOLVIDO POR OUTRO CAMINHO (correção do E2E17-002)
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma
- Relações: E2E17-002.
- Confiança: alta.

### E2E15-013 — Candidato sem sessão recebe 404 ao abrir o link da própria inscrição
- Origem: `doc/e2e/015-…/relatorio.md` §4 P3 (06/09)
- Problema original: link guardado vira beco; para anônimo, redirecionar ao acesso não vazaria nada.
- Recomendação original: convidar a entrar (com retorno ao destino).
- Rastro posterior: nenhum; manual o lista como aberto (`doc/manual/00-arquitetura-do-manual.md:1253`).
- Specs relacionadas: 010.
- Implementação encontrada: recusa uniforme mantida; o cabeçalho do portal oferece "Entrar", mas sem retorno ao endereço pedido.
- Evidência no código atual: `inscricoes/domain/titularidade.py:19-22` (não titular → 404, inclusive sem sessão); `portal/views.py:1190-1197`; `portal/templates/portal/recusa.html` (só "Voltar às seleções"); `portal/templates/portal/base.html:848` ("Entrar" no topo).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, com cuidado: distinguir "sem sessão" de "outra sessão" não vaza existência se o convite for dado a **qualquer** anônimo, exista ou não o recurso.
- Lacuna residual: sem redirecionamento ao acesso com retorno.
- Grupo do resíduo: C
- Impacto atual: candidato com link salvo precisa refazer o caminho pela vitrine/área.
- Próxima ação sugerida: corrigir (baixo custo) ou nenhuma
- Relações: —
- Confiança: alta.

### E2E15-016 — O caminho da presidência até distribuir/consolidar não é anunciado
- Origem: `doc/e2e/015-…/relatorio.md` §4 P3 (06/09)
- Problema original: "Minhas Etapas" do presidente dizia "você não possui Etapas atribuídas".
- Recomendação original: (implícita) anunciar o caminho.
- Rastro posterior: 038 (painel de condução) reforça; o manual ainda o lista como aberto (desatualizado).
- Specs relacionadas: 011, 012, 038.
- Evidência no código atual: `interface/templates/interface/minhas_etapas.html:17-20` ("Gerir comissão" para presidente), `:100-107` ("presidir uma comissão … use **Gerir comissão** e **Alocação por Etapa**, acima").
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma (atualizar o manual, que o dá como aberto)
- Relações: E2E-013; 038.
- Confiança: alta.

### E2E15-015 — Eliminados em Etapa anterior ficam fora do universo do ato de ordenação
- Origem: `doc/e2e/015-…/relatorio.md` §4 (registro de desenho, 06/09)
- Problema original: quem espera ver todos os eliminados no ato final não os encontra.
- Recomendação original: nenhuma (registro).
- Rastro posterior: decisão B da 018 — Resultado de Etapa visível ao candidato; E2E18 §8 confirma ("Helena vê Resultado das etapas").
- Evidência no código atual: `portal/views.py:1369-1389` (`resultados_visiveis`); `portal/templates/portal/acompanhamento.html:48`.
- Estado atual: SUPERADO / OBSOLETO — era registro de desenho, e a lacuna de comunicação que ele sugeria foi fechada pela 018.
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma
- Relações: E2E17-004.
- Confiança: alta.

### E2E15 §6/§7 — Oportunidades: teto de inscrições no assistente; reprodução do ato sem rota
- Origem: `doc/e2e/015-…/relatorio.md` §6 item 4, §7(c) (06/09); repetido em `doc/e2e/017-…/relatorio.md` §9
- Problema original: (a) `max_inscricoes_por_candidato` só via API/seed; (b) `reproduzir_ato` vive só em teste.
- Recomendação original: dar campo ao assistente; expor a reprodução.
- Rastro posterior: (a) retomado como **AX-9** (15/09) — "o teto é executado, é retificável e não é publicado em canal nenhum"; (b) a própria 015 decidiu nas Clarifications: "Reproduzir uma ordem antiga é … garantia interna, verificada por teste" (`specs/015-ordenacao-e-classificacao/spec.md:161-163`).
- Implementação encontrada: (a) teto retificável pela tela (`interface/retificacao.py:116-119`) e publicado no snapshot (`publicacoes/application/publish_edital.py:316-318`), mas **ausente** de `interface/forms.py` (composição); (b) `classificacao/application/reproducao.py:14` sem nenhum importador fora de `tests/`; a 014 expõe a reprodução do **corte** (`interface/views.py:6106,6124`).
- Estado atual: (a) DUPLICADO / ABSORVIDO (AX-9, 15/09); (b) CONTRADITO POR DECISÃO POSTERIOR — a decisão está nas Clarifications da própria 015, que governam; o relatório a contestou sem saber dela.
- Ainda faz sentido?: (a) sim, é do lote do AX-9; (b) pouco — com a proveniência inteira na tela, a reprodução é garantia de teste; nota-se só a assimetria com o corte, que reproduz na tela.
- Lacuna residual: (a) teto não compõe pela elaboração; (b) nenhuma exigida.
- Grupo do resíduo: (a) B (no outro lote); (b) C
- Impacto atual: (a) teto só se declara por API ou Retificação; (b) nenhum.
- Próxima ação sugerida: (a) ver AX-9; (b) nenhuma
- Relações: AX-9; 014 (corte histórico reproduzível).
- Confiança: alta.

### G16-001 — Edital publicado sem cláusula de reversão não pode passar a declará-la por Retificação
- Origem: `doc/e2e/016-ocupacao-de-vagas/relatorio.md` §3 G16-001 (12/09) — "decisão do usuário"
- Problema original: o catálogo da Retificação só endereça campos de objeto existente; `vacancyReversion` nulo não ganha campo.
- Recomendação original: decidir (Retificação que acrescenta cláusula ausente é caso real).
- Rastro posterior: contrato 026 decidiu que **pode** nascer por Retificação.
- Specs relacionadas: 016, 026 (FR-313).
- Implementação encontrada: decisão no contrato; a tela continua oferecendo o campo só quando o objeto existe. O mesmo vale para `cutRule` e `appealWindow`, que o contrato também declara "pode passar a existir".
- Evidência no código atual: `editais/domain/mutabilidade.py:515-548` (`PODE_PASSAR_A_EXISTIR`: `vacancyReversion` True, `cutRule` True, `appealWindow` True, `drawMethod` True; `normativeRule` False); `interface/retificacao.py:764` (reversão só `if isinstance(perfil.get("vacancyReversion"), dict)`), `:852` (corte idem), `:859` (janela idem); `tests/interface/test_retificar_reversao.py:84` (`test_o_campo_nao_aparece_onde_o_objeto_nao_existe` prende a ausência). O domínio só recusa o nascimento de `normativeRule` (`publicacoes/domain/colecoes.py:259-316`), então o caminho existe pela API.
- Estado atual: PARCIALMENTE RESOLVIDO — decidido a favor, sem porta na interface.
- Ainda faz sentido?: sim — pela própria Constituição (Princípio VI: capacidade que nenhuma interface alcança não é entregue) e pela FR-313 ("se pode passar a existir **e por qual caminho**"). Custo moderado (declarar objeto inteiro num ato, com validação já existente).
- Lacuna residual: nenhuma tela declara reversão, regra de corte ou janela recursal num Edital publicado que não as tinha; só a API.
- Grupo do resíduo: B
- Impacto atual: Edital publicado sem janela recursal fica sem prazo computável até o fim (a definitiva cai no ramo da declaração escrita); sem reversão, a vaga reservada não reverte.
- Próxima ação sugerida: criar spec (ou incremento da 026) para os três "podem nascer" na tela
- Relações: E2E-004, E2E14-005; E2E18-005 (a janela que sumia); contrato 026.
- Confiança: alta.

### G16-002 — Reversão e concorrência concomitante inalcançáveis em certame calculado
- Origem: `doc/e2e/016-…/relatorio.md` §3 G16-002 (12/09)
- Problema original: só o sorteio emitia ordem por lista; recortes reservados de marco calculado recusavam "sem ordem vigente".
- Recomendação original: corrigir o guia (feito) — a limitação de produto ficou registrada.
- Rastro posterior: **ACH-47** (16/09) → spec **034** (ordem por recorte em marco computado); revisou a decisão do PR #85.
- Specs relacionadas: 015, 016, 034.
- Evidência no código atual (pontual): `classificacao/application/emissao.py:83-101` (`lista_id=recorte`, com o comentário "Aqui havia `lista_id=None` fixo…").
- Estado atual: DUPLICADO / ABSORVIDO (ACH-47 / spec 034)
- Ainda faz sentido?: não neste lote.
- Lacuna residual: nenhuma aqui.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: "ordem computada por lista de concorrência" das avaliações de 09/09 e 11/09 (mesmo item).
- Confiança: alta.

### O16-001 — A trilha de auditoria do Edital não lista os atos da condução
- Origem: `doc/e2e/016-…/relatorio.md` §4 O16-001 (12/09) — "decisão do usuário"
- Problema original: `/auditoria` promete "todo ato" e mostra só o ciclo normativo.
- Recomendação original: ampliar é decisão do usuário.
- Rastro posterior: 019 (`FR-296`) e 036 acrescentaram apuração, convocação e instrução do recurso à trilha do Edital.
- Specs relacionadas: 016, 019, 036, 011 (trilha da comissão).
- Evidência no código atual: `auditoria/selectors.py:86-107` (`trilha_do_edital` reúne Edital, Retificações e `_atos_da_conducao`), `:110-130` (apuração, convocação, desfecho, instrução; admitir/julgar recurso "continuam fora").
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: parcialmente — ordenação, corte e consolidação estão na trilha da comissão/nas telas próprias; admitir/julgar recurso seguem fora por escolha declarada.
- Lacuna residual: uma pergunta "o que aconteceu com este Edital" ainda exige juntar duas trilhas.
- Grupo do resíduo: C
- Impacto atual: baixo (a informação existe).
- Próxima ação sugerida: nenhuma
- Relações: —
- Confiança: média — não conferi que ordenação/corte estão na trilha da comissão.

### O16-002 — A composição oferece linha de quadro para a Modalidade declarada como ampla
- Origem: `doc/e2e/016-…/relatorio.md` §4 O16-002 (12/09)
- Problema original: linha "Ampla concorrência (AC)" ao lado da geral; preenchê-la torna o Edital impublicável.
- Recomendação original: conveniência — dizer no ponto de entrada.
- Rastro posterior: 027 (estrutural de vagas) reconstrói o quadro ao escolher a ampla (FR-317).
- Evidência no código atual: `interface/templates/interface/_quadro_do_perfil.html:1-18` ("Escolher qual Modalidade é a ampla muda quantas listas reservadas existem" → reconstrução durante a edição).
- Estado atual: RESOLVIDO POR OUTRO CAMINHO (027)
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma aqui (a "segunda grafia" da ampla continua como armadilha de dados — `doc/achado-ampla-declarada-nao-remapeada.md`, outro lote).
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: R-006; `achado-ampla-declarada-nao-remapeada.md`.
- Confiança: média-alta (li o template, não percorri a tela).

### E2E17-004, E2E17-005 — Eliminado cedo sem notícia; "definitivo" por escolha livre
- Origem: `doc/e2e/017-exploratoria/relatorio.md` §6, §14 A/B (06/09)
- Problema original: candidato eliminado antes do marco não via nada; "Resultado definitivo" era um `<select>`.
- Recomendação original: decisão de governança (018).
- Rastro posterior: decisões A e B da 018 (`doc/decisao-018-escopo-institucional-do-recurso.md` §11, aprovadas 06/09); E2E18 §8 confirma.
- Evidência no código atual: `portal/views.py:1369-1405` (`resultados_visiveis`, `pareceres_do_titular`); `divulgacao/domain/publicabilidade.py:406-445` (porta da definitiva: recurso, reavaliação, providência, janela).
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: E2E15-015; E2E18-004.
- Confiança: alta.

### E2E17-007 — Não há como criar um segundo Edital num Processo existente
- Origem: `doc/e2e/017-…/relatorio.md` §6 (06/09)
- Problema original: a tela do Processo não oferecia a ação.
- Recomendação original: (implícita) dar a porta.
- Rastro posterior: `6f0f988 fix(ux): o segundo Edital tem porta, e o julgador alcança o que se contesta` (16/09).
- Evidência no código atual: `interface/templates/interface/processo_detalhe.html:158-167` ("Novo Edital neste Processo", `interface:edital-criar`).
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: 023 (criar a partir de Edital anterior) é outro caminho.
- Confiança: alta.

### E2E17 §13 (resíduo) — `classificationInformation` e `callInformation` sem tela que os escreva
- Origem: `doc/e2e/017-…/relatorio.md` §6 (auditoria dos serializadores) e §13 (06/09)
- Problema original: conteúdo normativo do contrato que nenhuma tela escreve; "decisão de produto".
- Recomendação original: decidir.
- Rastro posterior: contrato 026 os declarou **opacos e não retificáveis**: "o domínio não reconhece forma nem semântica … atribuir-lhe significado normativo exige decisão e especificação próprias".
- Evidência no código atual: `editais/domain/mutabilidade.py:152-161` (`OPACOS`), `:247-260` (razões).
- Estado atual: CONTRADITO POR DECISÃO POSTERIOR (026)
- Ainda faz sentido?: não como tela; a pergunta passou a ser se os campos deveriam existir no contrato — e a razão escrita diz que não há o que corrigir neles.
- Lacuna residual: dois campos normativos mortos no contrato publicado (herança da 001).
- Grupo do resíduo: C
- Impacto atual: nenhum para o usuário.
- Próxima ação sugerida: nenhuma
- Relações: P-1 (`callRules` também é opaco).
- Confiança: alta.

### E2E17 §10.3 — A publicação vigente não se declara vigente
- Origem: `doc/e2e/017-…/relatorio.md` §10 item 3 (06/09)
- Evidência no código atual: `portal/templates/portal/resultado.html:22-23` ("**A vigente diz que é a vigente** (FR-090)").
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não. · Lacuna residual: nenhuma · Grupo: — · Próxima ação: nenhuma · Confiança: alta.
- Relações: —; Rastro: FR-090 (018). Specs: 017, 018. Impacto atual: nenhum. Problema/recomendação: selo positivo na publicação vigente.

### E2E18-001 — A reavaliação determinada "não tem como ser cumprida" e trava a definitiva
- Origem: `doc/e2e/018-exploratoria/relatorio.md` §6 (07/09) — P1 aberto; manual ainda o dá como aberto (`doc/manual/00-arquitetura-do-manual.md:1208`)
- Problema original: julgado `REAVALIACAO_DETERMINADA`, a reabertura em Conclusões preservadas é recusada; "não há rota, botão ou tela que cumpra uma reavaliação".
- Recomendação original: (a) autorizar reabertura nominal; (b) criar a atribuição de reavaliação; (c) retirar a espécie.
- Rastro posterior: nenhum documento posterior o retoma. **Mas o código mostra que a via (b) já existia no commit auditado**: `4e8ab4c` (07/09, antepassado de `368d9cd`, base da auditoria) abriu uma vaga extra de distribuição enquanto a reavaliação está pendente e uma exceção única na consolidação.
- Specs relacionadas: 018 (US5, FR-067, FR-068), 013.
- Implementação encontrada: a inscrição com reavaliação pendente continua participante, aparece no filtro de prontidão da distribuição com o motivo nomeado, aceita **nova atribuição a outro avaliador** (teto +1), e a consolidação em cumprimento cria o sucessor citando a decisão.
- Evidência no código atual: `avaliacoes/application/distribuicao.py:317-341` (vaga extra por `reavaliacoes_pendentes`); `resultados/application/prontidao.py:66-68,511,576` (estado `REAVALIACAO`, "reavaliação determinada por recurso, ainda não cumprida"); `resultados/application/consolidacao.py:131-165,196-215` (`_decisao_a_cumprir`, exclui a avaliação original); `avaliacoes/application/selectors.py:178-190` (filtro de prontidão da distribuição alcança o grupo). Testes de domínio: `tests/integration/resultados/test_reavaliacao.py:123` (`test_a_inscricao_e_distribuivel_e_avaliavel_pelas_operacoes_existentes`), `:148` (sucessor citando a decisão), `:187` (quem avaliou a original não reavalia). **Nenhum teste de interface percorre o caminho**; `tests/interface/test_reabilitacao.py:158` só prova que a Mesa abre.
- Estado atual: IMPLEMENTADO, MAS NÃO VALIDADO
- Ainda faz sentido?: parcialmente — o diagnóstico "inexequível" parece errado (a auditoria tentou só a reabertura, que por desenho não é o caminho); o que continua de pé é a **orientação**: a recusa da reabertura manda ao "julgamento de recurso" (`avaliacoes/application/avaliacao.py:366-369`) — circular justamente no caso da reavaliação — e a peça do recurso não diz "distribua a outro avaliador".
- Lacuna residual: (1) caminho da tela nunca percorrido de ponta a ponta; (2) mensagem de recusa da reabertura enganosa quando há reavaliação pendente; (3) nenhum atalho da decisão/peça para a distribuição.
- Grupo do resíduo: B
- Impacto atual: risco de a presidência concluir, como a auditoria concluiu, que a definitiva está travada para sempre.
- Próxima ação sugerida: validar (percurso na tela) + corrigir a mensagem
- Relações: E2E15-003 (a guarda que falta precisa excetuar este caso); porta da definitiva (`divulgacao/domain/publicabilidade.py:430-431`).
- Confiança: média — domínio e testes lidos; a navegação real não foi exercida.

### E2E18-003 — A peça do recurso mostra identificadores técnicos a quem julga
- Origem: `doc/e2e/018-…/relatorio.md` §6 P3 (07/09)
- Problema original: "Interposto por — cand:745c…", identidade do objeto e versão por UUID.
- Recomendação original: (implícita) legibilidade.
- Rastro posterior: a 036 mexeu na peça (instrução) sem mudar a ficha.
- Evidência no código atual: `interface/templates/interface/recurso.html:26-38` (`interposto_por` cru; "Identidade do objeto"; "Ato vigente naquele instante" e "Versão consolidada citada" como `id`); o nome e o protocolo estão logo abaixo (`:28-29`).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, como polimento — a ficha é a que instrui a decisão; os UUIDs podiam ir para detalhe técnico como na tela do ato (E2E15-006).
- Lacuna residual: "Interposto por" responde "quem" com opaco.
- Grupo do resíduo: C
- Impacto atual: baixo (nome ao lado).
- Próxima ação sugerida: corrigir quando a tela for tocada
- Relações: E2E-010, E2E15-006 (mesma classe).
- Confiança: alta.

### E2E18-004 — Docstring desatualizada na porta da definitividade
- Origem: `doc/e2e/018-…/relatorio.md` §6 P3 (07/09)
- Evidência no código atual: `divulgacao/domain/publicabilidade.py:414` ("O quarto fato — janela aberta — é do degrau 8, e entra quando ele existir") com `_janela_aberta` já chamada em `:440`.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, trivial. · Lacuna residual: comentário falso · Grupo: C · Impacto: leitura · Próxima ação: corrigir · Relações: — · Confiança: alta.
- Problema/recomendação: comentário descreve estado anterior. Rastro: nenhum. Specs: 018.

### 019 §4.2 — Entrada no portal com o e-mail da inscrição não chega à confirmação de CPF
- Origem: `doc/e2e/019-convocacao/relatorio.md` §4.2 (13/09) — "fica como achado da 010"
- Problema original: conta criada não vinculada à inscrição; "Vincular participação anterior" volta a pedir o código sem chegar ao CPF.
- Recomendação original: registrar como achado da 010.
- Rastro posterior: nenhum commit em `identidade/` nem na reconciliação desde 13/09; nenhum relatório posterior o cita.
- Specs relacionadas: 010.
- Implementação encontrada: fluxo de reconciliação com prova de código, CPF e retomada.
- Evidência no código atual: `portal/views.py:766-835` (`acesso_reconciliar`: sem desafio provado volta a `portal:acesso`; `confirmar_cpf`; retomada `RETOMAR`).
- Estado atual: IMPLEMENTADO, MAS NÃO VALIDADO — o percurso que falhou usava inscrições criadas por script (identidade sem credencial de e-mail), cenário que o candidato real não produz; ninguém reproduziu nem descartou.
- Ainda faz sentido?: sim, verificar — se reproduzir com inscrição criada pelo próprio portal, é defeito sério da 010.
- Lacuna residual: incerteza sobre o laço "vincular → código → código".
- Grupo do resíduo: B
- Impacto atual: potencialmente o candidato não alcança a própria convocação.
- Próxima ação sugerida: validar
- Relações: memória "código de acesso exige correio local".
- Confiança: baixa — não reproduzível por leitura.

### POLISH020-015, POLISH020-016 — Endereço `/api/v1/` nos anexos; nenhuma página HTML da publicação histórica
- Origem: `doc/e2e/020-polish/relatorio.md` §3 e §8 (07–08/09) — mantido / não feito
- Problema original: (015) vocabulário de sistema no endereço público; (016) a versão histórica só existe em JSON e a página não diz qual versão se lê.
- Recomendação original: (015) mudança de rota para todos os artefatos; (016) oportunidade, superfície nova.
- Rastro posterior: 024 (descoberta e transparência) passou a mostrar no portal o **histórico de retificações** antes da identificação (avaliação de 11/09, §024).
- Specs relacionadas: 020, 024.
- Evidência no código atual: `publicacoes/api/public_urls.py:42` (`anexos/<uuid:artefato_id>`, sob `/api/v1/public/`); para 016, `portal/templates/portal/selecao.html:35-42` passou a dizer, quando houve Retificação, que a página mostra a versão vigente (024, FR-131a); `portal/urls.py` não tem rota HTML de conteúdo histórico por instante.
- Estado atual: (015) NÃO IMPLEMENTADO (mantido por decisão de consistência); (016) PARCIALMENTE RESOLVIDO (024)
- Ainda faz sentido?: (015) não; (016) parcialmente — a versão histórica legível por pessoa é valor de transparência, não urgente.
- Lacuna residual: (016) ler "o Edital como estava em tal data" continua exigindo API.
- Grupo do resíduo: (015) —; (016) C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma
- Relações: P-4/transparência; 024.
- Confiança: média (016 não verificado a fundo).

### E2E25 §4 — Resíduos da 025: recusa de referência cruzada sem âncora; emissão do snapshot cresce por Perfil; quadro ausente da página pública
- Origem: `doc/e2e/025-quadro-de-vagas/relatorio.md` §4 (10/09); avaliação de 11/09 §024
- Problema original: (a) recusa fica no resumo; (b) 16→38 consultas de 1 a 7 Perfis por `profile.modalidades.order_by("code")`; (c) a vitrine não mostra o quadro.
- Recomendação original: registrar; (c) pergunta para a próxima feature de transparência.
- Rastro posterior: 027 revisou o quadro; a avaliação de 12/09 mediu escala (performance ok).
- Evidência no código atual: não verificado linha a linha — (b) é custo fixo por Perfil na **publicação**, fora do caminho quente.
- Estado atual: NÃO IMPLEMENTADO (os três são registro, não compromisso)
- Ainda faz sentido?: (a) não; (b) só se Edital com dezenas de Perfis for publicado com frequência (AX-7 fala de 9 Perfis; 46/2026 fora do alvo); (c) parcialmente — a vitrine diz vagas imediatas, e a repartição por modalidade é informação útil ao cotista.
- Lacuna residual: (c) quadro por modalidade invisível no portal (está no PDF).
- Grupo do resíduo: (a) —; (b) C; (c) C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma
- Relações: R-006 (fechada pela 014); 027.
- Confiança: baixa-média — não li o código de (b) e (c).

---

## Parte C — Avaliações de capacidade (07/09 a 12/09): lacunas `L-x`, lacunas com endereço, pressões, resíduos

A série é cumulativa; o último estado declarado é o de `doc/avaliacao-de-capacidade-editais-2026-09-12.md`
(em `daded41`). Conferi cada item contra `bb774d9`.

### L-1, R-006, Q-2 — Quadro de vagas por modalidade; a "Ampla concorrência" declarada como Modalidade
- Origem: avaliação 07/09 §L-1; 09/09 (Q-2); 11/09 (R-006 da 025); fechamentos em 11/09 e 12/09
- Problema original: a Modalidade não tinha quantidade; 57, 28 e 173 impublicáveis; depois, o Edital que declara "Ampla concorrência" como Modalidade deixava o quadro sem igualdade.
- Recomendação original: quadro estruturado (e não anexo binário); declarar qual Modalidade é a ampla.
- Rastro posterior: 025 (quadro), 014 (`generalCompetitionModalityId`), 027 (estrutural de vagas, uma declaração só).
- Specs relacionadas: 025, 014, 027.
- Evidência no código atual: `editais/models/perfis.py:126` (`LinhaDoQuadroDeVagas`), `:54` (`modalidade_ampla_concorrencia`); `interface/templates/interface/_quadro_do_perfil.html:1-18` (027, FR-317).
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma neste lote (a "segunda grafia" da ampla no sorteio é `doc/achado-ampla-declarada-nao-remapeada.md`, outro lote).
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: O16-002; `achado-igualdade-da-soma-sem-a-ampla-declarada.md` (avulso).
- Confiança: alta.

### L-5, L-6 — Anexos do Edital; local do evento no cronograma
- Origem: avaliação 07/09 §L-5, §L-6; fechadas em 08/09 (020) e 09/09 (021)
- Problema original: o documento publicado não tinha anexos nem local de evento.
- Recomendação original: anexos como conteúdo publicado; campo de local.
- Specs relacionadas: 020, 021.
- Evidência no código atual: `editais/models/anexos.py:69` (`AnexoEdital`); `editais/models/cronograma.py:50` (`location`).
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não. · Lacuna residual: nenhuma (o `achado-anexo-sem-destinatario` é tratado abaixo) · Grupo: — · Impacto: — · Próxima ação: nenhuma
- Rastro posterior: POLISH020 (008/09) fechou 15 de 17 achados visuais. · Relações: AX-12. · Confiança: alta.

### Lacunas com endereço no arco (sorteio 021, corte 014, ocupação 016, convocação 019) e a `Q-1`
- Origem: avaliação 07/09 §"Lacunas com endereço"; 09/09, 11/09, 12/09 (arco `015 → 014 → 016 → 019`); `Q-1` (fronteira 016/019)
- Problema original: nenhum Edital de sorteio produzia ordem; nada cortava, ocupava ou convocava; duas frases incompatíveis sobre quem ocupa vaga.
- Recomendação original: specs próprias, na ordem do arco; decidir a `Q-1` antes da 016 e da 019.
- Rastro posterior: 021 (09/09), 014 (11/09), 016 (12/09), 019 (13/09); `Q-1` decidida pela emenda de 12/09 autorizada pelo usuário em `specs/018-recursos-e-superacao-de-resultados/spec.md` §6 ("Convocação, aceite, posse e matrícula — são da 019", com a nota da emenda) e `D-002` da 014.
- Evidência no código atual: `sorteios/models.py:29,197` (`RelacaoDeHabilitados`, `Sorteio`); `classificacao/models.py:217,360` (`Corte`, `ItemDoCorte`); `ocupacao/models.py:25,140,206` (`ApuracaoDeOcupacao`, `MovimentoDeVaga`, `EfeitoDeOcupacao`); `convocacao/models.py:84,220,349` (`Convocacao`, `DesfechoDaConvocacao`, `ComunicacaoEmitida`).
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não como lacuna de existência; os resíduos que cada spec deixou estão nos blocos próprios (P-2, P-3, P-10, cascata, reversão hierárquica).
- Lacuna residual: nenhuma aqui.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: G16-002 → 034 (ordem por recorte em marco computado, ACH-47) fechou o elo "ordem" fora da ampla.
- Confiança: alta quanto à existência; não reavaliei o comportamento de cada feature (outro lote cobre 030–038).

### Ordem computada por lista de concorrência (decisão do PR #85, 10/09)
- Origem: avaliação 09/09 §"lacunas com endereço" e adendo PR #85; 11/09 (pressão)
- Problema original: `emitir_ordem` fixava `lista_id=None`; a necessidade do 173 ficou "contra uma decisão declarada".
- Recomendação original: registrar; revisitar quando a ocupação chegar.
- Rastro posterior: ACH-47 (16/09) → spec 034 revisitou explicitamente a decisão.
- Evidência no código atual: `classificacao/application/emissao.py:83-101` (`lista_id=recorte`; comentário "Aqui havia `lista_id=None` fixo").
- Estado atual: DUPLICADO / ABSORVIDO (ACH-47 / 034)
- Ainda faz sentido?: não. · Lacuna residual: nenhuma aqui · Grupo: — · Impacto: — · Próxima ação: nenhuma · Relações: G16-002 · Confiança: alta.
- Specs relacionadas: 015, 021, 034.

### L-2 e heteroidentificação — a Etapa não tem aplicabilidade por Modalidade (nem por Perfil)
- Origem: avaliação 07/09 §L-2; reconferida aberta em 08, 09, 11 e 12/09 ("a metade que era da 014 fechou")
- Problema original: `EtapaAvaliacao` é do Edital e alcança todo inscrito; uma Etapa de heteroidentificação criaria Atribuição para todos e a prontidão esperaria avaliação de quem nunca foi convocado.
- Recomendação original: a Etapa declarar a quem se aplica (a dimensão que o Documento Exigido já tem); heteroidentificação em spec própria.
- Rastro posterior: a metade "aos primeiros de cada código" fechou pela 014 (Etapa governada, FR-208). Heteroidentificação e aplicabilidade por modalidade seguem declaradas fora de escopo em `specs/021-…/spec.md:787`, `specs/019-…/spec.md` §7 ("spec própria, dependente da L-2") e `doc/decisao-encadeamento-l1-e-o-arco-operacional.md:212`. 15/09: **AX-4** (a ficha varia por curso; a Etapa é do Edital inteiro). 16/09: registro "heteroidentificação (L-2 + spec própria)" e **ACH-60** (comissão local por polo).
- Specs relacionadas: 006, 013, 014, 021, 019.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `editais/models/etapas.py:11-20` (docstring: "Pertence ao Edital e vale para todos os seus Perfis … preço que se paga quando houver um Edital real que precise disso"); nenhum campo de aplicabilidade no modelo; `rg -i heteroidentifica backend/processo_seletivo` sem ocorrências.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, condicionado — só vale quando um Edital com cota e heteroidentificação entrar na operação. A amostra de 12/09 (6 Editais) não tem cota nenhuma; a de 07/09 tinha quatro (57, 28, 173, 46). Hoje a comissão faria a heteroidentificação fora do sistema, e o sistema não tem onde registrar a consequência dela para quem se declarou.
- Lacuna residual: Etapa restrita a quem declarou modalidade; Etapa por Perfil (AX-4); a Etapa de verificação étnico-racial em si.
- Grupo do resíduo: B
- Impacto atual: Editais com cota e heteroidentificação (57, 28, 173, 140/2025 do estudo de 21/09) não conduzem essa Etapa pelo sistema.
- Próxima ação sugerida: criar spec (quando a instituição priorizar o primeiro Edital com cota)
- Relações: AX-4 (15/09), ACH-60 (16/09); pressão "custo de autoria da modalidade por Perfil".
- Confiança: alta.

### L-3 e D-4 — Parcela nomeada de Etapa no desempate; barema estruturado
- Origem: avaliação 07/09 §L-3 e tabela "com endereço" (D-4 da 015); 11/09 ("L-3 e D-4 são a mesma estrutura vista de dois lados")
- Problema original: `MAIOR_PONTUACAO_NA_ETAPA` endereça a Etapa inteira; `Avaliacao.pontuacao` é um número só; as fichas de títulos (14, 173) têm item, teto por item e teto global.
- Recomendação original: parcelas nomeadas da Etapa, produzidas pelo barema e endereçáveis pelo desempate — numa mudança só.
- Rastro posterior: 15/09 **AX-4** (a ficha não existe como objeto); 16/09 **ACH-56** revalidado (S2) — "o barema não é representável" (`doc/auditoria-exploratoria-ux-2026-09-16.md:420`).
- Specs relacionadas: 012 (vedou barema estruturado na V1), 015 (D-4).
- Evidência no código atual (pontual): `avaliacoes/models.py:109` (`pontuacao` decimal único); `editais/models/perfis.py:349-352` (`CriterioDesempate.Tipo`: pontuação na Etapa, maior/menor valor de fato).
- Estado atual: DUPLICADO / ABSORVIDO (ACH-56, AX-4)
- Ainda faz sentido?: sim, e o outro lote deve manter a observação de 11/09: fazer barema e desempate por parcela separados paga a mesma migration duas vezes.
- Lacuna residual: barema e parcela; o avaliador soma a ficha fora e digita o total.
- Grupo do resíduo: B
- Impacto atual: a nota não é auditável item a item; desempate por disciplina/item inexequível.
- Próxima ação sugerida: ver ACH-56
- Relações: P-7 (autopontuação é teto sobre o barema).
- Confiança: alta.

### L-4 — Fato declarado que não é número nem data
- Origem: avaliação 07/09 §L-4; aberta em 08, 09, 11 e 12/09
- Problema original: o 14/2026 desempata por "ter realizado o curso Moodle" — fato booleano comprovado por documento; `FatoDeclarado.Tipo` só tem `DATA` e `INTEIRO`, e `CriterioDesempate` só compara grandeza.
- Recomendação original: tipo novo no fato **e** critério que o consuma (duas mudanças).
- Rastro posterior: nenhum documento posterior o retoma; `doc/decisao-encadeamento-l1-…md:212` o deixa fora do encadeamento.
- Specs relacionadas: 015.
- Evidência no código atual: `editais/models/perfis.py:209-211` (`DATA`, `INTEIRO`); `:349-356` (tipos de critério).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: pouco — evidência de um Edital só (14/2026, 3º critério). Há um contorno legível: fato `INTEIRO` 0/1 com `MAIOR_VALOR_DE_FATO`, com a comprovação como Documento Exigido; o custo é o rótulo do fato dizer "(0 = não, 1 = sim)".
- Lacuna residual: grafia booleana do fato.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma (reavaliar se um segundo Edital exigir)
- Relações: —
- Confiança: alta.

### Cascata Grupo 1 → 2 → 3 na convocação (14/2026)
- Origem: avaliação 07/09 §"O 14/2026, em detalhe"; repetido até 12/09 ("cascata Grupo 1→2→3 (016/019)")
- Problema original: o Edital convoca o Grupo 2 só esgotado o Grupo 1.
- Recomendação original: endereço 016/019.
- Rastro posterior: `specs/019-…/spec.md` §7 — "Cascata entre recortes por contagem de classificados — é alvo derivado da 014 pela decisão de 12/09/2026 registrada na 016, e continua não construída"; 16/09 **ACH-59** ("cascata de grupos" não representável).
- Evidência no código atual (pontual): `ocupacao/domain/reversao.py:18-40` (reversão cota → ampla com duas espécies; nenhuma cadeia de recortes).
- Estado atual: DUPLICADO / ABSORVIDO (ACH-59)
- Ainda faz sentido?: sim, para seleções de pessoal com grupos de prioridade.
- Lacuna residual: cascata entre recortes.
- Grupo do resíduo: B
- Impacto atual: o 14/2026 não fecha a convocação pelo sistema.
- Próxima ação sugerida: ver ACH-59
- Relações: "reversão hierárquica" (Parte D); AX-15.
- Confiança: alta.

### Segunda instância recursal (57 e 46: órgão distinto julga o recurso)
- Origem: avaliação 07/09 tabela "com endereço" (D-011 da 018); 11/09 ("escopo recusado por decisão vigente")
- Problema original: CLVA decide, CPVA julga o recurso; o sistema tem uma instância.
- Recomendação original: registrar.
- Rastro posterior: `specs/018-…/spec.md:444-451` (D-011: "Sem segunda instância e sem pedido de reconsideração") e §6 Out of Scope; reafirmado em `specs/019-…/spec.md` §7.
- Estado atual: CONTRADITO POR DECISÃO POSTERIOR (D-011 da 018, 06–07/09)
- Ainda faz sentido?: não por ora (equipe de 2–3 pessoas; o gargalo é o julgador).
- Lacuna residual: nenhuma além da decisão.
- Grupo do resíduo: —
- Impacto atual: Edital com duas instâncias conduz a segunda fora do sistema.
- Próxima ação sugerida: nenhuma
- Relações: ACH-60 (CPVA sem lugar, 16/09); `decisao-018-escopo-institucional-do-recurso.md`.
- Confiança: alta.

### Pressão — o limite de arquivo é da aplicação, e os Editais publicam outro (7 MB, 10 MB, 50 páginas)
- Origem: avaliação 07/09 §"Pressões"; 08/09 (dois lugares: candidato e anexo); 09, 11/09
- Problema original: "um limite publicado que o sistema não honra é norma que o próprio sistema contradiz na tela do candidato".
- Recomendação original: registrar, não decidir.
- Rastro posterior: nenhuma revisão da decisão.
- Specs relacionadas: 009 (FR-046), 020 (FR-013).
- Evidência no código atual: `config/settings/base.py:189-193` (10 MB, "um Edital não negocia tamanho de arquivo"), `:196-200` (5 MB para anexo) — caminho relativo a `backend/`; nenhum ponto do documento publicado declara o limite (`rg LIMITE_BYTES publicacoes/` vazio), só o portal o diz.
- Estado atual: NÃO IMPLEMENTADO (decisão vigente, não revista)
- Ainda faz sentido?: parcialmente — não recomendaria tornar o limite do Edital, mas recomendaria o inverso: o documento publicado **declarar** o limite da aplicação, para que texto institucional e tela não divirjam. O limite de páginas não tem grafia e pode continuar sem.
- Lacuna residual: o PDF do Edital pode afirmar um limite (em seção textual) e o portal outro.
- Grupo do resíduo: C
- Impacto atual: baixo; depende da redação que a instituição escreve.
- Próxima ação sugerida: nenhuma (registrar a alternativa)
- Relações: —
- Confiança: alta.

### Pressões absorvidas por relatórios posteriores (terceira dimensão do Documento Exigido; modalidade por Perfil; texto que repete dado estruturado; catálogo fixo de Seções; cronograma × data de publicação)
- Origem: avaliações 07/09 e 12/09 §"Pressões"
- Problema original: (a) "reservista, no caso de candidatos do sexo masculino maiores de 18" — condição sobre a pessoa, que não é Perfil nem Modalidade; (b) nove modalidades × setenta ofertas = 630 linhas (46/2026); (c) número/título do Edital redigitados no texto (59/78); (d) doze Seções fixas, sem Matrícula/Certificado/AVA e sem como dizer "não cabe recurso"; (e) 78/2026 abre inscrição antes da publicação.
- Recomendação original: registrar, não decidir (em todos).
- Rastro posterior: (a) **AX-10** (15/09), estudo de 21/09 §13/E6 e `doc/achado-documento-condicional-no-portal.md` (25/09); (b) **AX-7** (15/09), 043 (duplicar Perfil, implementada em `0479f4e`) e 044 (recorte transversal, só spec); (c) **AX-8** (15/09); (d) **AX-3** (15/09); (e) auditoria de 13/09 fricção #2 → **028** (cronograma vencido não publica).
- Evidência no código atual (pontual): (a) `editais/models/documentos.py:32-45` (só `perfil` e `modalidade`); (e) `editais/domain/validation.py:1904-2004` (`_eventos_vencidos` só no ato de publicação; advertência, não recusa, para evento no passado).
- Estado atual: DUPLICADO / ABSORVIDO (AX-10, AX-7/043/044, AX-8, AX-3, 028)
- Ainda faz sentido?: sim para (a), (c), (d) — nos lotes respectivos; (b) parcialmente endereçado; (e) só o caso "início antes da publicação e término depois" não é advertido, e é inofensivo (as inscrições abrem com a publicação).
- Lacuna residual: nos lotes dos AX.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma neste lote
- Relações: ver IDs.
- Confiança: média — confirmei os IDs de destino e dois pontos de código, não o estado de cada AX.

### Escala — 2719 vagas numa lista (158/2024) e `T059` da 002
- Origem: avaliação 12/09 §"A escala"; resíduo 6
- Problema original: Edital fora da faixa medida; números medidos num laptop.
- Recomendação original: medir (feito, até 10 000/20 000); medir no servidor do Cefor (`T059`).
- Rastro posterior: nenhum.
- Evidência: `backend/tests/performance/escala.py` (`PERF_ESCALA`, conforme a avaliação); `specs/002-frontend-administrativo/tasks.md:144` (`T059` aberto: "Nunca medidos").
- Estado atual: PARCIALMENTE RESOLVIDO — a forma da curva está medida; o valor na infraestrutura real, não.
- Ainda faz sentido?: sim, mas é tarefa de implantação.
- Lacuna residual: `SC-001/002/008` nunca medidos com servidores do Cefor; relação de habilitados fora da medição.
- Grupo do resíduo: B (gate de implantação)
- Impacto atual: nulo antes da produção.
- Próxima ação sugerida: validar (na homologação da implantação)
- Relações: T056 (abaixo).
- Confiança: média (não abri `escala.py`).

### Resíduo — a `002` tem sete tarefas abertas, e a `T056` (LDAP) é bloqueio de implantação
- Origem: avaliações 11/09 e 12/09 §Resíduos
- Problema original: autenticação institucional inexistente; `ator_da_sessao` é o seletor de demonstração; leitor de tela, ASES, design system do SUAP, CSP e medição pendentes.
- Recomendação original: registrar (dependem de decisão ou de pessoas).
- Rastro posterior: nenhum; produção recusa subir com o seletor (CLAUDE.md).
- Specs relacionadas: 002.
- Evidência no código atual: `specs/002-frontend-administrativo/tasks.md:133-144` (T053–T059 abertos); `interface/identidade.py:107-112` (`ator_da_sessao` lê o papel declarado na sessão); nenhuma ocorrência de LDAP em `backend/processo_seletivo` nem em `backend/config`.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim — é o único item deste lote que **impede a finalidade** do sistema em produção. Não é feature de domínio; depende do Ifes (diretório, SUAP).
- Lacuna residual: autenticação institucional; verificações de acessibilidade oficiais; CSP.
- Grupo do resíduo: A (gate de implantação — o sistema não é implantável sem ele)
- Impacto atual: nenhum certame real pode rodar.
- Próxima ação sugerida: criar spec/decisão institucional (LDAP/SUAP) — responsabilidade compartilhada com a TI do Ifes
- Relações: E2E-014, E2E-020, E2E-016; G1–G4 do §12 da E2E de 02/09.
- Confiança: alta.

### Resíduos menores das avaliações (README desatualizado; `T063` da 013; `achado-anexo-sem-destinatario`; `achado-teste-com-data-em-utc`)
- Origem: avaliações 09, 11 e 12/09 §Resíduos
- Problema original: (a) a tabela de incrementos do README fica para trás a cada feature ("quarta vez"; "enquanto nada o verificar, ele volta"); (b) conferir `distribuicao.html` e `resultados.html` a 375 px; (c) o anexo publicado não diz a quem serve; (d) a classe "teste compara data em UTC com a tela" ficou sem proteção.
- Recomendação original: (a) corrigir e, implicitamente, verificar; (b)–(d) registrar.
- Rastro posterior: (c) **AX-12** (15/09) "já coberto em parte por achado-anexo-sem-destinatario".
- Evidência no código atual: (a) `README.md` lista specs só até a `025` e diz "5402 passando e 2 pulados" (`README.md:214`), contra 7594/11 no `CLAUDE.md` — **a recorrência continua**; (b) `specs/013-consolidacao-resultado-etapa/tasks.md:203` (`[ ] T063`); (c) `portal/templates/portal/_documentos_do_edital.html:50-57` (anexo listado só pelo rótulo); (d) `doc/achado-teste-com-data-em-utc.md` ("a classe fica registrada. Protegê-la é decisão de escopo").
- Estado atual: (a) NÃO IMPLEMENTADO; (b) NÃO IMPLEMENTADO; (c) DUPLICADO / ABSORVIDO (AX-12); (d) NÃO IMPLEMENTADO — o bloco leva o rótulo de (a).
- Ainda faz sentido?: (a) sim — é documentação de entrada do repositório, e está 19 features e ~2 200 testes atrás; um teste que compare a tabela com `specs/` fecharia a classe; (b) sim, barato; (d) parcialmente.
- Lacuna residual: README desatualizado; T063 sem execução.
- Grupo do resíduo: C
- Impacto atual: quem chega sem contexto lê números e escopo errados no README.
- Próxima ação sugerida: corrigir (a); validar (b)
- Relações: —
- Confiança: alta.

---

## Parte D — Perguntas de domínio (`doc/achados-editais-externos.md`: P-1…P-13, formas de regra, Edital grande)

Classificadas pelo que o sistema faz hoje com cada pergunta — respondida por spec, decidida fora de
escopo, ou aberta. Pergunta aberta não é backlog: o resíduo só entra como A/B quando há Edital no
alvo que o sistema hoje não conduz por causa dela.

### P-1, P-2 — Como se declara quem é chamado em seguida; oferta sem quantidade conhecida (cadastro de reserva)
- Origem: `doc/achados-editais-externos.md` §P-1, §P-2 (07/09; P-2 reconfirmada em 12/09 pelo 69/2026)
- Problema original: dois modos — quantidade por modalidade + destinos; ou, sem quantidade, **sequência nominal** do chamamento (1ª AC · 2ª PcD · 3ª PPIQ · 4ª AC…). `reserve_type` admite `UNLIMITED` e "nada executa"; "ocupar sem quantidade é caso normal, não borda".
- Recomendação original: um lugar onde a regra é declarada e executada (o `callRules` que nunca foi consumido), sem dois motores.
- Rastro posterior: 016 (quadro, reversão, concomitância), 019 (fila por recorte), 027 ("Perfil só de cadastro de reserva — continua sem repartição", `specs/027-estrutural-de-vagas/spec.md:415-416`); 026 declarou `callRules` **opaco** e não retificável.
- Specs relacionadas: 016, 019, 025, 027, 026.
- Implementação encontrada: o modo "quantidade conhecida" executa; o modo "sequência nominal sem quantidade" não existe, e convocar exige vaga faltante apurada.
- Evidência no código atual: `convocacao/application/convocar.py:100-109` (sem apuração → "não há vaga faltante conhecida para a qual convocar") e `:146-152` (`_recusar_por_deficit`); `editais/domain/mutabilidade.py:152-161,292` (`normativeRule/callRules` opaco); `rg callRules` só encontra serialização e formulário (`publicacoes/application/publish_edital.py:141`, `interface/forms.py:1201`). O único caminho para convocar de um cadastro de reserva é **Retificar as vagas imediatas** (retificável) até existir déficit.
- Estado atual: PARCIALMENTE RESOLVIDO — P-1 respondida para quantidade conhecida; P-2 (execução do cadastro de reserva) não implementada.
- Ainda faz sentido?: sim. Cadastro de reserva puro é a natureza do 173/2025 e do 140/2025 (este no estudo de 21/09), e parcial no 69 e no 76. Não recomendaria o motor genérico de `callRules`; recomendaria a pergunta estreita: "convocar do cadastro de reserva, na ordem publicada, por necessidade declarada, dentro da validade" — que depende da P-3.
- Lacuna residual: convocação a partir de cadastro de reserva sem vaga imediata; sequência nominal entre modalidades para CR.
- Grupo do resíduo: B
- Impacto atual: Editais de cadastro de reserva terminam no resultado publicado; a convocação corre fora, ou por Retificação de vagas a cada chamada.
- Próxima ação sugerida: criar spec (junto da P-3)
- Relações: P-3; estudo de 21/09 §5.1 (tipo de cadastro reserva inalcançável — outro lote).
- Confiança: média-alta — li as guardas da convocação; não percorri o contorno pela Retificação.

### P-3 — Validade do Edital, prorrogação e suplente convocável para turma futura
- Origem: §P-3 (07/09); cinco Editais repetem a cláusula palavra por palavra (12/09)
- Problema original: a classificação sobrevive ao processo por 6 meses/2 anos, e pode alimentar oferta que não existia.
- Recomendação original: pergunta (incide em convocação e chamadas).
- Rastro posterior: `specs/019-…/spec.md` §7 — "Validade do Edital e prorrogação (P-3) … criá-lo é incremento próprio"; edge case "vaga liberada no último dia da validade … fora de escopo".
- Evidência no código atual: `processos/models.py:35-80` (`Edital` sem campo de validade).
- Estado atual: NÃO IMPLEMENTADO (fora de escopo declarado da 019)
- Ainda faz sentido?: sim — sem validade, o sistema permite convocar depois de expirado o prazo publicado e não avisa quando ele se aproxima; e a P-2 depende dela.
- Lacuna residual: prazo de validade como conteúdo normativo com consequência (aviso/recusa de convocação fora dele). O "suplente para a turma seguinte" (reuso da classificação noutra oferta) é a parte cara e pode ficar fora.
- Grupo do resíduo: B
- Impacto atual: validade vive em prosa; controle manual.
- Próxima ação sugerida: criar spec (com P-2)
- Relações: P-2, P-6, P-10.
- Confiança: alta.

### P-4 — Impugnação do Edital por qualquer cidadão; recurso contra a lista de inscritos / relação de habilitados
- Origem: §P-4 (07/09); terceira evidência em 12/09 (69/2026); avaliações 09 e 11/09 ("a relação de habilitados é artefato publicado sem via de contestação")
- Problema original: `Recurso` exige Inscrição e só ataca `PublicacaoResultado` ou `ResultadoEtapa`.
- Recomendação original: pergunta; "a única que aponta para fora do arco previsto".
- Rastro posterior: 018 exclui "Recurso contra Edital, Retificação, convocação, heteroidentificação…" e "impugnação por concorrente" (`specs/018-…/spec.md` §6, D-002); 021 exclui "Recurso ou impugnação contra a relação de habilitados" e "Relação de inscritos como artefato universal" (`specs/021-…/spec.md:92-95` D-002, `:786-787`); decisão 2A de `doc/decisao-018-escopo-institucional-do-recurso.md` §11 (só o titular recorre).
- Evidência no código atual: `recursos/models.py:48-69` (`inscricao` obrigatória; `publicacao_atacada` XOR `resultado_atacado`).
- Estado atual: CONTRADITO POR DECISÃO POSTERIOR (018 D-002/§6 e decisão 2A; 021 D-002)
- Ainda faz sentido?: parcialmente — a impugnação por cidadão pode continuar fora (protocolo no campus; exige identidade de terceiro e notificação, que o produto não tem). A contestação da **relação de habilitados** é outra coisa: é movida por candidato, contra artefato que o próprio sistema publica em todo Edital de sorteio, e costuma ter janela no cronograma.
- Lacuna residual: recurso do candidato contra a relação de habilitados (não constar, modalidade errada).
- Grupo do resíduo: B (relação de habilitados) / C (impugnação por terceiro)
- Impacto atual: o erro na relação corrige-se por sucessão administrativa, sem peça recursal do candidato no sistema.
- Próxima ação sugerida: nenhuma agora; registrar como candidato a incremento da 018/021 se a instituição quiser
- Relações: `decisao-018-escopo-institucional-do-recurso.md`; 036 (instrução do recurso).
- Confiança: alta.

### P-5 — A unidade sobre a qual vagas são contadas, ocupadas e revertidas (polo, curso)
- Origem: §P-5 (07/09)
- Problema original: vagas por polo com quadro próprio, reversão dentro do polo; a "oferta localizada" é bidimensional.
- Recomendação original: pergunta.
- Rastro posterior: 15/09 **AX-5** (curso/área/campus inexistentes) e **AX-6** (o código não é o polo); a 016 conta por Perfil × lista e "nenhuma vaga atravessa Perfil" (`doc/e2e/016-…/relatorio.md` §6; `test_nenhuma_vaga_atravessa_perfil_em_certame_de_sorteio`).
- Estado atual: DUPLICADO / ABSORVIDO (AX-5, AX-6)
- Ainda faz sentido?: sim, no lote dos AX. O modelo "polo = Perfil" responde contagem e reversão; o que falta é o eixo curso/campus acima do Perfil.
- Lacuna residual: nos AX.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma neste lote
- Relações: P-10 (a mesma pergunta no eixo do tempo); ACH-60 (comissão por polo).
- Confiança: média.

### P-6 — Um processo deriva de outro (vagas remanescentes)
- Origem: §P-6 (07/09); 12/09 confirma as duas formas (com e sem citação da origem)
- Problema original: "ninguém consegue perguntar quantas vagas sobraram de onde".
- Recomendação original: pergunta.
- Rastro posterior: 023 declarou por escrito que não toca a derivação normativa (adendo da avaliação 09/09); o vínculo de composição vive só na trilha (`editais/application/reaproveitamento.py`, operação `REAPROVEITAR_EDITAL`).
- Evidência no código atual: `processos/models.py:35-80` (sem referência a Edital de origem).
- Estado atual: NÃO IMPLEMENTADO (fora de escopo declarado da 023)
- Ainda faz sentido?: pouco — a instituição sabe de onde vêm as remanescentes; o ganho é relatório, e o custo é norma nova (herdar vagas). Faria sentido só se a visão institucional (040–042) precisar somar oferta através de Editais.
- Lacuna residual: relação normativa entre Editais.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma
- Relações: P-3; 040 (visão institucional).
- Confiança: alta.

### P-7 — Autopontuação vinculante (teto declarado pelo candidato)
- Origem: §P-7 (07/09); tabela "com endereço" de 07–11/09
- Problema original: o 173/2025 proíbe atribuir pontuação acima da informada pelo candidato.
- Recomendação original: pergunta.
- Rastro posterior: 15/09 AX-4 ("vizinho de P-7"); 16/09 ACH-56 lista "autopontuação (P-7)" como pendência do barema.
- Evidência no código atual: nenhuma ocorrência de autopontuação/expectativa no código (`rg -i autopontua` vazio); `avaliacoes/models.py:109`.
- Estado atual: DUPLICADO / ABSORVIDO (ACH-56)
- Ainda faz sentido?: só junto do barema; sozinho, o avaliador aplica o teto manualmente lendo a ficha anexada.
- Lacuna residual: no ACH-56.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma neste lote
- Relações: L-3/D-4.
- Confiança: alta.

### P-8 — Inscrição originada fora do sistema (SIGAA)
- Origem: §P-8 (07/09); 09/09 "virou bloqueio operacional" do 76/2026; 11/09 e 12/09 ("a única inversão da amostra")
- Problema original: a relação de habilitados é projeção das inscrições deste sistema; as do 76 estão no SIGAA.
- Recomendação original: pergunta (protocolo, comprovante e versão aceita de inscrição importada).
- Rastro posterior: nenhum; `decisao-encadeamento-l1-…md:212` o deixa fora.
- Evidência no código atual: nenhuma importação de inscrição (`rg -i "sigaa|importar inscri"` vazio).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: pouco — é integração com outro sistema institucional para um Edital da amostra; o sistema foi desenhado como porta de entrada. Recomendaria decidir explicitamente "fora do alvo" como se fez com o 46/2026.
- Lacuna residual: nenhuma que se deva construir sem decisão.
- Grupo do resíduo: C
- Impacto atual: o 76/2026 (e Editais análogos) não é conduzível por aqui.
- Próxima ação sugerida: nenhuma (decisão de alvo, do usuário)
- Relações: 019 §7 (integração acadêmica também é de outro sistema).
- Confiança: alta.

### P-9 — Requisito que o sistema registra e não verifica
- Origem: §P-9 (07/09); 12/09 ("não é peculiaridade de Edital de bolsa")
- Problema original: Fapes, Lattes, adimplência, "ter acesso a computador" — inverificáveis.
- Recomendação original: o domínio saber a diferença entre requisito que confere e que só declara.
- Rastro posterior: 15/09 AX-2 (requisito de formação com duas fontes) e AX-3 citam P-9.
- Evidência no código atual: `editais/models/perfis.py:20` (`requirements` = lista de texto); nenhum requisito é conferido automaticamente — a conferência é humana, em Etapa.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: pouco — hoje **todo** requisito é "declarado" e a verificação é da Etapa; a distinção só pagaria se o sistema passasse a verificar algum requisito sozinho.
- Lacuna residual: nenhuma operacional.
- Grupo do resíduo: C
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma
- Relações: AX-2, P-13.
- Confiança: alta.

### P-10 — A oferta se reparte em turmas, e a turma nem sempre é o recorte de vaga
- Origem: §P-10 (12/09)
- Problema original: 59 (turma = código) cabe como Perfil; 58 (turma abaixo do código) cabe como texto de cronograma.
- Recomendação original: nenhuma feature precisa responder hoje.
- Rastro posterior: `specs/019-…/spec.md` §7 — "Turma como recorte (P-10) … só tem consequência quando alguém for alocado a uma delas, e nenhum Edital lido diz como".
- Estado atual: CONTRADITO POR DECISÃO POSTERIOR (fora de escopo, com razão, na 019)
- Ainda faz sentido?: não por ora.
- Lacuna residual: nenhuma.
- Grupo do resíduo: —
- Impacto atual: nenhum (os dois Editais publicam).
- Próxima ação sugerida: nenhuma
- Relações: P-5.
- Confiança: alta.

### P-11 — Reclassificação, regularização e desistência por inércia na convocação
- Origem: §P-11 (12/09)
- Problema original: três desfechos que não são recurso nem eliminação; a regularização é a Administração desfazendo ato desfavorável sem recurso.
- Recomendação original: a 019 decidir se usa a superação da 018.
- Rastro posterior: 019 `Q-3`/`D-008` — regularização sucede o Resultado pela superação com origem nova; reclassificação e inércia são atos próprios.
- Evidência no código atual: `convocacao/models.py:115` (convocar "Para regularizar o indeferimento"), `:246-251` (desfechos Regularização, Desistência expressa, Cancelamento por inércia, Reclassificação), `:31-60` (`AtestadoDeFatoExterno`: não acessou o ambiente, ausente na primeira semana, não entregou presencialmente); relatório `doc/e2e/019-convocacao/relatorio.md` §2 (regularização percorrida na tela).
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: P-12.
- Confiança: alta.

### P-12 — Cumprimento de exigência que o sistema não guarda (entrega presencial, procurador, menor de idade)
- Origem: §P-12 (12/09)
- Problema original: documento entregue presencialmente e retido pela instituição; procurador; menor representado.
- Recomendação original: pergunta — registrar que houve, quem atestou e o que concluiu, sem deter o artefato.
- Rastro posterior: 019 `D-004` (atestado de fato externo); `specs/019-…/spec.md` §7 ("entrega presencial como acervo (P-12) — esta feature registra atestado de fato externo, e não passa a deter documento").
- Evidência no código atual: `convocacao/models.py:31-60` (`ATESTADO_NAO_ENTREGA_PRESENCIAL`, `atestado_por` obrigatório); `editais/models/documentos.py:22-60` (Documento Exigido só descreve o que se anexa); nenhuma representação (procurador/responsável) no domínio (também excluída na decisão 2A da 018).
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: parcialmente — o desfecho negativo tem registro; a forma "exigido, conferido presencialmente, não retido" e a representação continuam sem modelo, e só um Edital da amostra as pede.
- Lacuna residual: Documento Exigido de conferência presencial; representação.
- Grupo do resíduo: C
- Impacto atual: baixo (o 69/2026 é conduzível com atestado e prosa).
- Próxima ação sugerida: nenhuma
- Relações: P-8 (espelho), decisão 2A da 018.
- Confiança: alta.

### P-13 — Requisito satisfeito por uma entre várias vias (elegibilidade alternativa)
- Origem: §P-13 (12/09) — evidência de **um** Edital, e defeituosa (158/2024)
- Problema original: "professor … OU licenciando", cada via com sua prova; o Edital publicou exigência impossível para metade do público.
- Recomendação original: pergunta.
- Rastro posterior: 019 §7 fora de escopo; 15/09 AX-2 ("vizinho de P-13"); 044 (recorte transversal) não trata vias.
- Evidência no código atual: `editais/models/perfis.py:20` (requisitos em lista plana); `editais/models/documentos.py:30-45` (`required` booleano + Perfil + Modalidade).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: pouco por ora — evidência única; o contorno honesto é dois Perfis, ou documento facultativo com instrução por via.
- Lacuna residual: "um destes" na exigência documental.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma
- Relações: AX-2; terceira dimensão do Documento Exigido (AX-10).
- Confiança: alta.

### Formas de regra — reversão hierárquica e percentual como faixa
- Origem: `doc/achados-editais-externos.md` §"Duas formas novas de regra" (07/09) e §"O Edital grande" (a lista de destinos)
- Problema original: (a) vaga não preenchida num subgrupo vai para os outros subgrupos da mesma reserva e só depois para a ampla; (b) percentual mínimo–máximo contra `RegraNormativa.percentage` de valor único.
- Recomendação original: modelar "o Edital declara os destinos, e aqui há um só", para não gravar no domínio a regra rasa.
- Rastro posterior: (a) 15/09 **AX-15** (submodalidades de PPIQ como listas distintas — "evidência adicional para a reversão hierárquica"); a 016 implementou reversão de **um destino**, com duas espécies de gatilho; (b) a 025 tornou o quadro absoluto a fonte da quantidade.
- Evidência no código atual: `ocupacao/domain/reversao.py:1-40` (cota → ampla, `REVERSAO_POR_ESGOTAMENTO` e saldo; sem lista de destinos); `editais/models/perfis.py:383` (`percentage` decimal único) — e nenhum leitor de `percentage` em `ocupacao`, `classificacao`, `convocacao`, `sorteios` ou `divulgacao`.
- Estado atual: (a) DUPLICADO / ABSORVIDO (AX-15); (b) SUPERADO / OBSOLETO — com o quadro absoluto da 025, o percentual deixou de ser entrada de cálculo; é só texto da regra.
- Ainda faz sentido?: (a) sim, no lote do AX-15 — e vale lembrar o aviso de 07/09: a reversão de um destino "grava no domínio uma regra que era do Edital"; (b) não.
- Lacuna residual: (a) destinos em cadeia.
- Grupo do resíduo: (a) B (no outro lote); (b) —
- Impacto atual: (a) Editais com subgrupos de cota revertem direto para a ampla.
- Próxima ação sugerida: (a) ver AX-15; (b) nenhuma
- Relações: cascata do 14/2026 (ACH-59) é a mesma estrutura entre grupos de prioridade.
- Confiança: alta.

### Edital grande (46/2026) e as confirmações da amostra
- Origem: §"O Edital grande" e §"O que estes Editais confirmaram" (07/09 e 12/09)
- Problema original: forma completa de modalidade (conjunção de fatos) e de remanejamento (8 destinos); prova objetiva, taxa, treineiro, nome social, recurso de efeito coletivo — "registrado para que ninguém o leia como requisito".
- Recomendação original: nenhuma; fora do alvo por decisão.
- Rastro posterior: fora do alvo em todas as avaliações (07–12/09).
- Estado atual: CONTRADITO POR DECISÃO POSTERIOR — "fora do alvo do produto por decisão" (`doc/avaliacao-de-capacidade-editais-2026-09-07.md`, tabela por Edital; reiterado em 08, 09, 11 e 12/09; `doc/achados-editais-externos.md` §"O Edital grande": "Ele não é objetivo do produto"). A decisão é anterior ao registro e foi mantida; nenhuma posterior a reabriu.
- Ainda faz sentido?: não como escopo. As confirmações (Modalidade como dado publicado, retificação como rotina, janela recursal por marco, teto de inscrições por Edital) seguem verdadeiras no código.
- Lacuna residual: nenhuma.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: reversão hierárquica, P-5.
- Confiança: alta.

---

## Parte E — Complemento da E2E de 02/09: gates de produção e privacidade (§8, §12)

### G1–G4, G22 — SMTP real, retenção/descarte, provedor de identidade, rascunhos com dado pessoal visíveis à gestão
- Origem: `doc/auditoria-exploratoria-e2e-2026-09-02.md` §8 e §12 ("gates de produção conhecidos, não escopo de feature") (02/09)
- Problema original: pendências de implantação herdadas das specs anteriores; rascunhos de candidato visíveis à gestão (G22).
- Recomendação original: não corrigir agora; são gates.
- Rastro posterior: produção recusa backend de e-mail que não entrega (`config/settings/production.py:140-141`) e o seletor de identidade; a 031 declarou retenção própria para a planilha de matrícula (`matriculas/models.py:5`).
- Evidência no código atual: G3 = `T056` (bloco da Parte C); G22 — `interface/templates/interface/inscricoes.html:86-97` (seção "Em preenchimento", com a mesma tabela das recebidas); G2 — nenhuma política de retenção/expurgo de inscrição ou documento de candidato no código (`rg -i "retenc|expurg"` só acha `matriculas/` e dois comentários).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim — G2 (LGPD: prazo de guarda e descarte de documento de candidato) e G3 são condições de produção; G22 é decisão de privacidade que continua não tomada por escrito (a tela a justifica por FR-067, que é operacional).
- Lacuna residual: política de retenção e descarte; decisão explícita sobre rascunhos visíveis.
- Grupo do resíduo: B (G2, G22); A para G3 (ver T056)
- Impacto atual: nenhum antes da produção; risco LGPD depois.
- Próxima ação sugerida: criar spec/decisão (retenção) e registrar decisão (G22)
- Relações: T056; E2E-020.
- Confiança: média — não procurei política de retenção fora do código (documentos institucionais).

---

## 1. Tabela-resumo

Blocos com dois estados distintos aparecem em duas linhas.

| ID | título | estado | grupo | próxima ação |
|---|---|---|---|---|
| E2E-001/002/021 | devolução do Edital e da Retificação; quem cancela | RESOLVIDO | — | nenhuma |
| E2E-003 | lista de inscrições sem paginação/filtro | RESOLVIDO | — | nenhuma |
| E2E-004 | Retificação acrescentar/remover Documento Exigido | CONTRADITO POR DECISÃO POSTERIOR (razão normativa no código; D-009 da 044) | C | nenhuma |
| E2E-005 | estado Ativo do Processo | RESOLVIDO | — | nenhuma |
| E2E-006/007 | rascunho local; resumo de congelamento | RESOLVIDO | — | nenhuma |
| E2E-008 | Mesa: filtros e nome na linha | PARCIALMENTE RESOLVIDO | C | nenhuma |
| E2E-009 | inscrição digitada em Impedimentos | PARCIALMENTE RESOLVIDO | C | nenhuma |
| E2E-010 | decimais canônicos/UUID nas telas | DUPLICADO / ABSORVIDO (ACH-17) | C | corrigir (outro lote) |
| E2E-011 | hash e terminal no comprovante | NÃO IMPLEMENTADO | C | nenhuma |
| E2E-012 | contagem de documentos ignora modalidade | PARCIALMENTE RESOLVIDO | C | nenhuma |
| E2E-013 | guia pós-publicação / comissão | DUPLICADO / ABSORVIDO (13.6 → 038) | C | nenhuma |
| E2E-014 | "Ou entre por outro nome" | SUPERADO / OBSOLETO | — | nenhuma |
| E2E-015 | matriz de recusa HTTP | RESOLVIDO | — | nenhuma |
| E2E-016 | notificações de handoff / comunicação ativa | NÃO IMPLEMENTADO | C/B | nenhuma agora |
| E2E-017 | distribuir com inscrições abertas | RESOLVIDO | — | nenhuma |
| E2E-018 | Retificação sem "Aguardando quem…" | NÃO IMPLEMENTADO | C | corrigir (oportunista) |
| E2E-019 | todos veem todos os Processos do escopo | SUPERADO / OBSOLETO (é o FR-003 da 002) | — | nenhuma |
| E2E-020 | código por e-mail, ponto único de falha | NÃO IMPLEMENTADO | B | validar na implantação |
| Gate 013 | reabertura consumida; quórum | RESOLVIDO | — | nenhuma |
| G1–G4/G22 | retenção, SMTP, identidade, rascunhos visíveis | NÃO IMPLEMENTADO | B (A no G3) | criar spec/decisão |
| E2E14-005 | Retificar espécie do alvo, Etapa governada, continuação | CONTRADITO POR DECISÃO POSTERIOR (026) | — | nenhuma |
| E2E14 §4 | quickstart da 014 promete recusa | NÃO IMPLEMENTADO | C | corrigir |
| E2E15-003 | Mesa conclui com Resultado na própria Etapa | NÃO IMPLEMENTADO | B | corrigir (decisão curta) |
| E2E15-007 | rascunho não avisa prazo encerrado | NÃO IMPLEMENTADO | B | corrigir |
| E2E15-012 | 404 técnico na gestão | RESOLVIDO POR OUTRO CAMINHO (E2E17-002) | — | nenhuma |
| E2E15-013 | anônimo recebe 404 no próprio link | NÃO IMPLEMENTADO | C | corrigir ou nenhuma |
| E2E15-016 | caminho da presidência não anunciado | RESOLVIDO | — | atualizar o manual |
| E2E15-015 | eliminados antes fora do universo do ato | SUPERADO / OBSOLETO | — | nenhuma |
| E2E15 opp. (a) | teto de inscrições fora do assistente | DUPLICADO / ABSORVIDO (AX-9) | B | ver AX-9 |
| E2E15 opp. (b) | `reproduzir_ato` sem rota | CONTRADITO POR DECISÃO POSTERIOR (Clarifications da 015) | C | nenhuma |
| G16-001 | declarar reversão (e corte, e janela) por Retificação | PARCIALMENTE RESOLVIDO | B | criar spec |
| G16-002 | reversão/concomitância em certame calculado | DUPLICADO / ABSORVIDO (ACH-47 / 034) | — | nenhuma |
| O16-001 | trilha do Edital sem atos da condução | PARCIALMENTE RESOLVIDO | C | nenhuma |
| O16-002 | linha de quadro para a AC declarada | RESOLVIDO POR OUTRO CAMINHO (027) | — | nenhuma |
| E2E17-004/005 | eliminado cedo sem notícia; definitiva livre | RESOLVIDO | — | nenhuma |
| E2E17-007 | segundo Edital no Processo | RESOLVIDO | — | nenhuma |
| E2E17 §13 | `classificationInformation`/`callInformation` sem tela | CONTRADITO POR DECISÃO POSTERIOR (026, opacos) | C | nenhuma |
| E2E17 §10.3 | publicação vigente sem selo | RESOLVIDO | — | nenhuma |
| E2E18-001 | reavaliação determinada "inexequível" | IMPLEMENTADO, MAS NÃO VALIDADO | B | validar + corrigir mensagem |
| E2E18-003 | ids técnicos na peça do recurso | NÃO IMPLEMENTADO | C | corrigir (oportunista) |
| E2E18-004 | docstring da porta da definitiva | NÃO IMPLEMENTADO | C | corrigir |
| 019 §4.2 | reconciliação do portal não chega ao CPF | IMPLEMENTADO, MAS NÃO VALIDADO | B | validar |
| POLISH020-015 | `/api/v1/` no endereço do anexo | NÃO IMPLEMENTADO | — | nenhuma |
| POLISH020-016 | página HTML da versão histórica | PARCIALMENTE RESOLVIDO (024) | C | nenhuma |
| E2E25 §4 | âncora da referência cruzada; snapshot por Perfil; quadro fora da vitrine | NÃO IMPLEMENTADO | C | nenhuma |
| L-1/R-006/Q-2 | quadro por modalidade; ampla declarada | RESOLVIDO | — | nenhuma |
| L-5/L-6 | anexos; local do evento | RESOLVIDO | — | nenhuma |
| Arco + Q-1 | sorteio, corte, ocupação, convocação; fronteira 016/019 | RESOLVIDO | — | nenhuma |
| PR #85 | ordem computada por lista | DUPLICADO / ABSORVIDO (ACH-47 / 034) | — | nenhuma |
| L-2 | aplicabilidade da Etapa; heteroidentificação | NÃO IMPLEMENTADO | B | criar spec (quando houver Edital com cota) |
| L-3/D-4 | parcela nomeada; barema | DUPLICADO / ABSORVIDO (ACH-56, AX-4) | B | ver ACH-56 |
| L-4 | fato booleano | NÃO IMPLEMENTADO | C | nenhuma |
| Cascata 14/2026 | Grupo 1 → 2 → 3 | DUPLICADO / ABSORVIDO (ACH-59) | B | ver ACH-59 |
| 2ª instância | órgão recursal distinto | CONTRADITO POR DECISÃO POSTERIOR (D-011 da 018) | — | nenhuma |
| Limite de arquivo | limite da aplicação × do Edital | NÃO IMPLEMENTADO | C | nenhuma |
| Pressões | 3ª dimensão do documento; modalidade por Perfil; texto × dado; Seções fixas; cronograma | DUPLICADO / ABSORVIDO (AX-10, AX-7/043/044, AX-8, AX-3, 028) | — | nenhuma |
| Escala / T059 | 2719 vagas; medição no Cefor | PARCIALMENTE RESOLVIDO | B | validar |
| T056 (002) | LDAP e demais tarefas de implantação | NÃO IMPLEMENTADO | **A** | criar spec/decisão institucional |
| README | tabela de incrementos e contagem da suíte | NÃO IMPLEMENTADO | C | corrigir |
| T063 (013) | 375 px em distribuição/resultados | NÃO IMPLEMENTADO | C | validar |
| Anexo sem destinatário | anexo não diz a quem serve | DUPLICADO / ABSORVIDO (AX-12) | — | nenhuma |
| Teste com data em UTC | classe sem proteção | NÃO IMPLEMENTADO | C | nenhuma |
| P-1/P-2 | quem é chamado; cadastro de reserva | PARCIALMENTE RESOLVIDO | B | criar spec (com P-3) |
| P-3 | validade e prorrogação | NÃO IMPLEMENTADO | B | criar spec |
| P-4 | impugnação; recurso contra a relação de habilitados | CONTRADITO POR DECISÃO POSTERIOR (018, 021) | B/C | nenhuma agora |
| P-5 | unidade de contagem (polo/curso) | DUPLICADO / ABSORVIDO (AX-5, AX-6) | — | nenhuma |
| P-6 | Edital que deriva de outro | NÃO IMPLEMENTADO | C | nenhuma |
| P-7 | autopontuação vinculante | DUPLICADO / ABSORVIDO (ACH-56) | C | nenhuma |
| P-8 | inscrição originada fora | NÃO IMPLEMENTADO | C | nenhuma (decisão de alvo) |
| P-9 | requisito declarado e não verificado | NÃO IMPLEMENTADO | C | nenhuma |
| P-10 | turma como recorte | CONTRADITO POR DECISÃO POSTERIOR (019 §7) | — | nenhuma |
| P-11 | reclassificação, regularização, inércia | RESOLVIDO | — | nenhuma |
| P-12 | entrega presencial, procurador, menor | PARCIALMENTE RESOLVIDO | C | nenhuma |
| P-13 | elegibilidade alternativa | NÃO IMPLEMENTADO | C | nenhuma |
| Reversão hierárquica | destinos em cadeia | DUPLICADO / ABSORVIDO (AX-15) | B | ver AX-15 |
| Percentual como faixa | mínimo–máximo | SUPERADO / OBSOLETO (quadro absoluto da 025) | — | nenhuma |
| Edital grande (46/2026) | forma completa | CONTRADITO POR DECISÃO POSTERIOR (fora do alvo) | — | nenhuma |

## 2. Contagens por estado (77 linhas)

| Estado | Quantidade |
|---|---:|
| RESOLVIDO | 15 |
| RESOLVIDO POR OUTRO CAMINHO | 2 |
| PARCIALMENTE RESOLVIDO | 9 |
| NÃO IMPLEMENTADO | 25 |
| IMPLEMENTADO, MAS NÃO VALIDADO | 2 |
| SUPERADO / OBSOLETO | 4 |
| DUPLICADO / ABSORVIDO | 12 |
| CONTRADITO POR DECISÃO POSTERIOR | 8 |

Resíduos por grupo (coluna "grupo" da tabela): **A = 1** (T056 — implantação; o G3 do bloco
G1–G4 é o mesmo item); **B = 14**, mais 3 linhas mistas (G1–G4 "B, A no G3"; E2E-016 "C/B"; P-4
"B/C") — os B incluem itens que moram em outro lote (ACH-56, ACH-59, AX-9, AX-15); **C = 28**;
**— = 31** (sem resíduo). Dos 25 "NÃO IMPLEMENTADO", 16 são C — quase todos polimento ou pergunta de
domínio sem Edital no alvo que a exija —, 5 são B, 1 é A.

## 3. Achados NOVOS encontrados de passagem

1. **O contrato de mutabilidade diz que três objetos "podem nascer" por Retificação, e a tela não
   oferece caminho para nenhum deles.** `editais/domain/mutabilidade.py:515-548` declara
   `vacancyReversion`, `cutRule` e `appealWindow` como "pode passar a existir" (FR-313 da 026, "e por
   qual caminho"); `interface/retificacao.py:764,852,859` só desenha os campos quando o objeto já
   existe, e `tests/interface/test_retificar_reversao.py:84` prende essa ausência. Resultado: um Edital
   publicado sem janela recursal não ganha prazo computável pela interface — só pela API. É o
   G16-001 generalizado; Princípio VI.
2. **A recusa da reabertura manda ao lugar errado quando há reavaliação determinada.**
   `avaliacoes/application/avaliacao.py:366-369` diz que "o julgamento de recurso o supera por um
   Resultado novo" — o julgamento já aconteceu e, nessa espécie, não cria sucessor; o caminho real
   é distribuir a outro avaliador (`avaliacoes/application/distribuicao.py:317-341`). Foi essa
   frase que levou o E2E18-001 a um diagnóstico de "inexequível".
3. **A guarda que falta na Mesa (E2E15-003) não pode ser um bloqueio simples**: a reavaliação
   determinada é o caso legítimo de avaliar quem já tem Resultado vigente na própria Etapa. Quem
   corrigir precisa excetuar `reavaliacoes_pendentes`.
4. **O manual está atrás do código em dois achados**: `doc/manual/00-arquitetura-do-manual.md:1242`
   dá o E2E15-016 como aberto (está corrigido em `minhas_etapas.html:100-107`) e `:1208` dá o
   E2E18-001 como inexequível (o caminho existe e tem teste de domínio).
5. **README 19 features atrás**: tabela de incrementos para na `025` e a suíte aparece como
   "5402 passando e 2 pulados" (`README.md:214`), contra 7594/11 no `CLAUDE.md`. A avaliação de
   12/09 já previa: "enquanto nada o verificar, ele volta".
6. **Cadastro de reserva não é convocável pelo sistema** sem Retificar as vagas imediatas: convocar
   exige déficit apurado (`convocacao/application/convocar.py:100-152`). Nenhum relatório posterior
   o registra com essa forma; aparece aqui como resíduo da P-2.

## 4. Incertezas que exigem validação humana

1. **E2E18-001**: percorrer na tela "julgar como reavaliação → filtrar a Etapa por prontidão →
   distribuir a outro avaliador → avaliar → consolidar → publicar definitiva". Se fechar, o achado
   vira RESOLVIDO (com a mensagem a corrigir); se não, volta a P1.
2. **019 §4.2**: reproduzir a reconciliação com uma inscrição **criada pelo próprio portal**. O
   relatório usou inscrições criadas por script, e o laço pode ser artefato do cenário.
3. **Decisões de governança pendentes, que este lote não toma**: a regra da Mesa depois do Resultado
   (E2E15-003); se os três "podem nascer" da 026 ganham porta na tela (NOVO 1); se cadastro de
   reserva e validade (P-2/P-3) entram no roadmap; se o 76/2026 (P-8) sai formalmente do alvo, como o
   46/2026; se rascunhos continuam visíveis à gestão (G22).
4. **E2E-013**: não confirmei se a Atenção/painel da 038 sinaliza literalmente "comissão não
   constituída" (confirmei `UX-003` de cobertura e `UX-063` de trabalho pendente).
5. **O16-001**: não conferi que ordenação, corte e consolidação estão na trilha da comissão.
6. **E2E25 §4 (b)(c)** e **POLISH020-016**: lidos pelo relatório e por um ponto do template; não
   medi as consultas da emissão nem procurei rota de versão histórica além de `portal/urls.py`.
7. **Escala/T059** e **T056**: dependem de infraestrutura e de decisão do Ifes; nada no repositório
   os resolve.
