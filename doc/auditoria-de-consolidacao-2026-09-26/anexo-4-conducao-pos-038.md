# Lote 4 — Condução pós-038, governança e prontidão

**Contra:** `bb774d9` (= origin/main de 25/09/2026), worktree `auditoria-consolidacao-seletivo-8dba99`.
**Método:** somente leitura — código, testes, specs, `git log`, `git show` de branch não mesclada, `gh` leitura.
Nada executado (sem suíte, sem servidor, sem manage.py).

**Fato de fundo que governa quase todo o lote.** Desde a auditoria de 20/09, os arquivos do painel
(`interface/supervisao.py`, `processo_detalhe.html`, `supervisao.html`, `_sinal.html`) receberam **um único
commit**: `4ec1cbb` (fix N-03) — `git log --since=2026-09-19` sobre esses caminhos. As specs 040–042 declaram
expressamente que **não tocam** a região de Atenção (`specs/040-visao-institucional-dos-processos/spec.md:34-37`,
`:76-80`, `:214`). Portanto, das sete condicionantes C1–C7, **só a C3 fechou**.

---

### C1 · N-01 — "Nenhuma condição de atenção" afirma ausência global a partir de leitura parcial (+ "a vista parcial não se declara", §22-Q4)
- Origem: `doc/auditoria-de-convergencia-pos-038-2026-09-20.md` §1 (C1), §12 (N-01, S3), §22 Q4 e Q12 (20/09)
- Problema original: a região Atenção suprime por papel (correto), mas quando o ator alcança ≥1 espécie e nenhuma dispara, a frase é absoluta. Publicador lia "Nenhuma condição…" com 15 condições visíveis ao gestor. Nenhum papel isolado vê o Processo inteiro e nenhuma tela avisa.
- Recomendação original: a frase deve parar de afirmar fato global; declarar que a vista é relativa ao que o ator alcança (C1, condição de saída do piloto).
- Rastro posterior: `docs/visao-sistema/index.html` (20/09, §"Ausência afirmada a partir de leitura parcial") repete o achado; nenhum commit posterior.
- Specs relacionadas: 022 (FR-004, FR-025), 038 (FR-558, FR-559).
- Implementação encontrada: nenhuma mudança.
- Evidência no código atual: `backend/processo_seletivo/interface/views.py:3946-3960` — `atencao_visivel = any(alcancadas.values())`; basta alcançar uma espécie para a região aparecer. `interface/templates/interface/processo_detalhe.html:139-141` e `supervisao.html:139-141` — `<p class="nenhuma">Nenhuma condição de atenção neste Processo.</p>`, sem qualificação. `interface/supervisao.py:1302-1337` — `alcance` concede `UX_066` só com `resultado:publicar` e `UX_005/UX_064` só com a permissão de recurso: o publicador alcança uma espécie, o gestor não alcança três. O teste `tests/interface/test_supervisao.py:592-604` prende a frase como está; o caso de zero espécies (`:533-569`) está coberto, o de "alcança uma, nenhuma dispara" não.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim — é o único ponto em que o padrão mais forte do produto (ausência honesta) é quebrado, e a 040 mostra que o próprio produto já sabe fazê-lo ("O que esta página não mede", `visao_geral.html:350-369`).
- Lacuna residual: a frase de ausência precisa dizer que é relativa ao alcance do leitor (ou nomear o que não é mostrado), sem revelar o que foi suprimido. Mudança de texto + condição no template; nenhum cálculo novo.
- Grupo do resíduo: A
- Impacto atual: baixo com equipe de 2–3 pessoas que acumulam papéis (quem acumula não recebe a frase falsa); vira falso "tudo em dia" assim que houver segregação de funções — que é exatamente o que a operação institucional exige.
- Próxima ação sugerida: corrigir (cabe em fix pequeno com revisão do FR-559; decidir a redação)
- Relações: C1; E-6/ACH-25 (vista parcial); raiz = supressão por sinal (FR-004) sem declaração de parcialidade.
- Confiança: alta — código e template lidos, nenhum commit desde 20/09.

### C2 · N-02 — Recurso aguardando admissibilidade não produz sinal em nenhuma superfície
- Origem: auditoria 20/09 §1 (C2), §6 "O que ainda permanece fora", §12 (N-02, S3), §20 item 1 e §22 Q8
- Problema original: `sinais_do_recurso` só lê peças `AGUARDANDO_JULGAMENTO`; recurso recém-interposto (a fase com latência humana) fica invisível até ser admitido.
- Recomendação original: decidir se vira espécie nova ou se `UX-064` passa a cobrir as duas situações; "vale mais do que sorteio e matrícula juntos".
- Rastro posterior: visão-sistema 20/09 ("Metade de um ciclo sem superfície de condução"); nenhum commit.
- Specs relacionadas: 038 FR-561 (escrito só para "aguardando julgamento"), FR-565 (catálogo fechado), 018.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `interface/supervisao.py:1162-1167` — `recursos_do_edital(edital, situacao=recursos_selectors.AGUARDANDO_JULGAMENTO)`. O estado existe e é derivável: `recursos/application/selectors.py:24,30,105-110` (`AGUARDANDO_ADMISSIBILIDADE`). A recuperação lateral: `interface/acoes.py:120-127` mostra "Recursos recebidos (N)" ao julgador — mas N conta **todos** os recursos do Edital, inclusive decididos (`Recurso.objects.filter(inscricao__edital=edital).count()`), então não diz quantos esperam.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim — a regra de impedimento vale igualmente para admitir e julgar (`doc/descoberta-conducao-por-presidencia-unica.md` §2.2, `recursos/application/admitir.py:54`), então a mesma partição UX-005/UX-064 serve; o custo é um filtro. Não contradiz FR escrito (FR-561 é estreito), mas deixa a cauda que a 038 promete cobrir incompleta.
- Lacuna residual: incluir `AGUARDANDO_ADMISSIBILIDADE` na leitura de pendentes (ou espécie própria), com revisão do FR-561/FR-565; opcionalmente fazer o contador da lista contar só pendentes.
- Grupo do resíduo: A
- Impacto atual: o recurso tempestivo não aparece no painel exatamente enquanto o prazo de resposta institucional corre; mitigado pelo contador da lista de Processos, que porém não distingue pendente de decidido.
- Próxima ação sugerida: criar spec curta (ou emenda da 038) — decisão embutida: espécie nova × ampliar UX-064
- Relações: C2; §6 "admissibilidade fora do painel"; §22 Q8; inventário 09/09 (recursos).
- Confiança: alta.

### C3 · N-03 (+ commit `4ec1cbb`) — "Abrir a Supervisão" oferecido a quem a Supervisão recusa
- Origem: auditoria 20/09 §1 (C3), §12 (N-03, S2, regressão de `32cd6d9`), §14
- Problema original: o segundo link para a Supervisão, dentro do Pulso, não tinha a guarda `pode_gerir_comissao` e devolvia 404 a auditor, publicador, julgador e elaborador.
- Recomendação original: aplicar a mesma guarda do botão vizinho.
- Rastro posterior: `4ec1cbb` (20/09, "fix(038): a Supervisão deixa de ser oferecida a quem ela recusa").
- Specs relacionadas: 033 FR-476, 038 FR-558.
- Implementação encontrada: guarda no template + teste reforçado.
- Evidência no código atual: `interface/templates/interface/processo_detalhe.html:72` — `{% if pode_gerir_comissao %}<a …>Abrir a Supervisão</a>{% endif %}`; `:14-23` já guardado. Teste `tests/interface/test_supervisao.py:533-569` (`test_quem_alcanca_o_processo_le_o_estado_e_nao_recebe_caminho`) exige `url(processo_a) not in corpo` e `"Abrir a Supervisão" not in lido`; contraprova `:586-590`. Não há outro link para `interface:supervisao` em templates (`visao_geral.html:361` só menciona em texto, sem link).
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não — fechado.
- Lacuna residual: nenhuma. (A resposta 404 da própria view permanece — ver D-G2.)
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma
- Relações: E-2 "reaberta em um ponto" (§17) volta a ✅; D-G2.
- Confiança: alta.

### C4 · N-04 — Sinais sem caminho não dizem a quem pedir
- Origem: auditoria 20/09 §1 (C4), §6 "Quais estados são acionáveis", §12 (N-04, S2), §15 item 4, §16 "Responsabilidade"
- Problema original: para o gestor, 9 de 15 sinais (UX-001/UX-002) saem sem link e sem dizer qual capacidade pedir; o padrão "Peça a alguém com a permissão de X" já existe no Edital.
- Recomendação original: levar ao painel o padrão "dizer a quem pedir" (capacidade, não pessoa); não modelar responsável individual.
- Rastro posterior: visão-sistema 20/09 §D; nenhum commit.
- Specs relacionadas: 038 FR-564 (não nomear pessoa), FR-566, 037 ("peça a alguém…").
- Implementação encontrada: nenhuma.
- Evidência no código atual: `interface/templates/interface/_sinal.html:16-18` — link só `{% if sinal.destino %}`, sem ramo alternativo. `interface/supervisao.py:1240-1259` (`admite_encaminhamento`) devolve `None` para UX-001/002/046 quando falta `retificacao:elaborar`, e nada substitui o caminho.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente — sim para UX-046 (Retificação resolve) e para quando o Processo/Edital não admite o ato; para UX-001/UX-002, dizer "peça a quem retifica" encaminharia a pessoa a um ato que não resolve (N-05). O resíduo só é limpo depois de N-05/N-06.
- Lacuna residual: frase de capacidade no sinal sem destino, reaproveitando a redação da 037; nenhum dado novo.
- Grupo do resíduo: B
- Impacto atual: sinais que parecem acionáveis e não são para o leitor; com papéis acumulados o impacto some.
- Próxima ação sugerida: corrigir (depois de N-05/N-06)
- Relações: C4; §16 (a decisão de não nomear pessoa segue certa — FR-564 intacto, `supervisao.py:1141-1145`).
- Confiança: alta.

### C6 · N-06 — `schedule.status` declarado `derivado()` e nada o deriva
- Origem: auditoria 20/09 §1 (C6), §7 ("estado declarado × relógio"), §12 (N-06), §17 (E-4), §19 "Estrutural", §20 item 2
- Problema original: o contrato de mutabilidade chama o status do Evento de derivado; nada o deriva; ele fica `PLANEJADO` e o `UX-002` compara esse valor congelado com o relógio → sinal permanente.
- Recomendação original: derivar o status (não acrescentá-lo à Retificação); "a menor mudança com o maior efeito sobre sinal/ruído".
- Rastro posterior: visão-sistema 20/09 §A ("schedule.status não é derivado"); nenhum commit.
- Specs relacionadas: 026 (contrato de mutabilidade), 022 (FR-027, D-004 — "as duas informações são apresentadas, nenhuma é arbitrada"), 038.
- Implementação encontrada: nenhuma derivação.
- Evidência no código atual: `editais/domain/mutabilidade.py:432` — `("schedule", "status"): derivado()`. `editais/models/cronograma.py:29` — `default=Status.PLANEJADO`. A composição **não expõe** o campo (`interface/templates/interface/_evento.html` não tem input de status; `interface/forms.py:1330` só o preserva) e a Retificação não o oferece (derivado). Publicação congela o valor do modelo: `publicacoes/application/publish_edital.py:293`. Nenhuma escrita de `EM_ANDAMENTO`/`CONCLUIDO` fora de enum e serializer (`rg` sobre `processo_seletivo`; só `editais/api/serializers.py:186` aceita o valor pela API). `interface/supervisao.py:635-662` + `COERENTES` `:546-552`: todo Evento com término cujo início já passou vira `UX-002`.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, com uma correção de diagnóstico: há **duas doutrinas** no repositório. O inventário de 09/09 (`doc/inventario-supervisao-do-processo.md:257-262, 443-446`) trata o status como **declarado à mão** e recomenda "não agora" derivá-lo; o contrato da 026 o chama de **derivado**. Pela interface ninguém consegue declará-lo, então ele não é nem declarado nem derivado — é constante. Qualquer das duas saídas (derivar na leitura; ou tirar o status da comparação/do conteúdo) fecha o ruído; manter as duas doutrinas não.
- Lacuna residual: decidir a doutrina (derivado × declarado) e aplicá-la; se derivado, `UX-002` passa a disparar só em contradição real (Evento cancelado/datas incoerentes).
- Grupo do resíduo: A
- Impacto atual: um `UX-002` por Evento com término já iniciado, em todo Edital publicado pela interface — ruído permanente que treina a ignorar a região; a página do Processo também exibe "declarado planejado" nos próximos marcos (`processo_detalhe.html:121`).
- Próxima ação sugerida: criar spec curta (decisão de doutrina + derivação)
- Relações: C6; E-4 (fonte declarada derivada que nada deriva); causa de N-05 (parte UX-002); ACH-08 deslocado (§14).
- Confiança: alta — leitura de modelo, form, template, publicação e sinal.

### C5 · N-05 — `UX-001` e `UX-002` encaminham à Retificação, que não alcança os campos que os causam
- Origem: auditoria 20/09 §1 (C5), §12 (N-05), §19, §21 ("não acrescentar scheduleEventId e status à Retificação")
- Problema original: "Retificar as Etapas" / "Retificar o cronograma" abrem tela sem o campo que o sinal reporta (`stages.scheduleEventId` é estrutural; `schedule.status` é derivado).
- Recomendação original: não encaminhar à Retificação enquanto ela não alcançar a causa; resolver derivando (N-06) — não abrindo o campo.
- Rastro posterior: nenhum commit.
- Specs relacionadas: 022 FR-035/FR-036, 038 FR-557, 026.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `interface/supervisao.py:1222-1223` (rótulos) e `:1273-1274` (`reverse("interface:retificar")`) inalterados; `editais/domain/mutabilidade.py:447` — `("stages", "scheduleEventId"): estrutural()`; `interface/retificacao.py:1054` — `SECOES_QUE_ACRESCENTAM` não inclui Etapas. O próprio código diz que Etapa sem marco "é publicável e legítimo" (`supervisao.py:604-615`).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, e a parte UX-001 **não se resolve com N-06**: uma Etapa publicada sem Evento continuará sem Evento para sempre (estrutural, sem acréscimo de Etapa), e o sinal aponta uma tela que nunca a corrige. Precisa decisão: UX-001 em Edital publicado é condição de Atenção (então sem destino, dito como fato estrutural) ou só aviso de composição (então sai do painel e vira validação — ver N-08/D-G1)?
- Lacuna residual: parte UX-002 — some com N-06; parte UX-001 — decisão sobre o destino/natureza do sinal.
- Grupo do resíduo: A
- Impacto atual: para quem tem `retificacao:elaborar`, dois de cada três sinais levam a um beco (Previsibilidade caiu 1 ponto por isso em 20/09).
- Próxima ação sugerida: criar spec (junto com N-06)
- Relações: C5; N-06 (causa de UX-002); N-04; E-4; §21 respeitado (os campos continuam fora da Retificação).
- Confiança: alta.

### N-07 · ACH-27 (deslocado) — "2 de 5 sem avaliador suficiente" conta inscrição eliminada na Etapa anterior
- Origem: auditoria 20/09 §4 (ACH-27 "PARCIAL / DESLOCADO"), §7, §12 (N-07, S2), §14
- Problema original: o contador do painel (e o mosaico da distribuição) conta todas as submetidas; a lista abaixo exclui as "eliminadas antes".
- Recomendação original: "correção com decisão embutida" (§19) — o denominador deve ser o universo participante.
- Rastro posterior: visão-sistema 20/09 ("Contador que contradiz a própria lista"); nenhum commit em `avaliacoes/application/selectors.py` desde 19/09.
- Specs relacionadas: 013 (panorama/prontidão), 022 FR-028/FR-033, 038.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `interface/supervisao.py:686` chama `resumo_da_etapa(edital=edital, etapa=etapa)` sem `panorama`; `avaliacoes/application/selectors.py:193-238` agrega sobre `Inscricao.status=SUBMETIDA` inteiro (`carentes = total - completas`, `:227`). A listagem, ao contrário, filtra por participantes (`selectors.py:174-190`, `_recorte_da_prontidao`), e a tela mostra "eliminadas antes" (`distribuicao.html:127-129`). Mesmo com `panorama`, `carentes` continuaria sobre o total — o panorama só acrescenta contagens.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim — número que contradiz a lista logo abaixo, em Etapas posteriores à primeira (qualquer Edital com corte).
- Lacuna residual: `carentes`/`sem_conclusao` sobre participantes (ou medida explícita "de N participantes"), nas duas superfícies ao mesmo tempo (é uma leitura só).
- Grupo do resíduo: B
- Impacto atual: sobrestima o trabalho faltante a partir da 2ª Etapa; induz a alocar avaliador para quem já saiu.
- Próxima ação sugerida: corrigir
- Relações: ACH-27 (16/09, outro lote) — o deslocamento para dentro da distribuição continua; Processo↔Supervisão seguem concordando.
- Confiança: alta (lógica lida; não reproduzido em execução).

### N-08 · §6 "avisos de validação do Edital fora do painel"
- Origem: auditoria 20/09 §5 Cenário A, §6, §7, §12 (N-08, S2), §21 ("não juntar sem decidir a fronteira")
- Problema original: avisos de *Validação do conteúdo* (ex.: marco sem regra de corte, PPP 10×8) só aparecem na página do Edital; Atenção e validação são conjuntos disjuntos.
- Recomendação original: **não** transformá-los em sinais sem decidir a fronteira (imperfeição de composição × trabalho parado).
- Rastro posterior: visão-sistema 20/09 §C; nenhuma decisão registrada.
- Specs relacionadas: 032, 038 FR-565 (catálogo fechado).
- Implementação encontrada: nenhuma.
- Evidência no código atual: `interface/supervisao.py:495-506` — `ESPECIES` continua com as dez espécies, nenhuma derivada de `ValidationFinding`.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente — a própria auditoria desaconselha a junção cega; o caminho mais barato é reduzir a classe (D-G1 torna um dos dois exemplos impeditivo; o outro é E-4). Um *indicador* "este Edital tem N avisos de composição" com link para o Edital seria o máximo defensável.
- Lacuna residual: decisão de fronteira; nenhum código até lá.
- Grupo do resíduo: C
- Impacto atual: quem conduz pelo painel não vê avisos de composição; precisa abrir cada Edital.
- Próxima ação sugerida: nenhuma (aguarda decisão de governança; revisitar após D-G1)
- Relações: D-G1; E-4; N-05 (UX-001 talvez pertença a este lado da fronteira).
- Confiança: alta.

### N-09 · §8/§11 — Identificadores internos (`cand:…`, UUIDs crus) na tela do recurso
- Origem: auditoria 20/09 §8, §11, §12 (N-09, S1)
- Problema original: "INTERPOSTO POR" mostra o `subject` (`cand:seed-…`) e três UUIDs a quem julga.
- Recomendação original: correção de varredura (§19).
- Rastro posterior: visão-sistema 20/09 §C; nenhum commit em `recurso.html` desde 19/09.
- Specs relacionadas: 018 FR-092 (proveniência para administração e auditoria), FR-093 (candidato não vê trilha técnica).
- Implementação encontrada: nenhuma.
- Evidência no código atual: `interface/templates/interface/recurso.html:27` (`proveniencia.interposto_por`), `:33` (`objeto_identidade`), `:35` (`ato_vigente.id`), `:37` (`versao.id`); origem em `recursos/application/selectors.py:252-259`, cujo docstring (`:246-248`) declara a exposição **deliberada**: "aqui aparecem identificadores técnicos… porque quem lê é a administração" (FR-092).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente — FR-092 exige que a proveniência seja **respondível**, não que o UUID seja a forma; o nome e o protocolo já estão na linha seguinte (`recurso.html:28-29`). Um rótulo legível com o identificador técnico secundário resolveria sem violar FR-092.
- Lacuna residual: apresentar o interponente pelo nome/“o próprio candidato”; UUIDs em detalhe recolhível.
- Grupo do resíduo: C
- Impacto atual: estético/cognitivo para o julgador; nenhum dado pessoal exposto a quem não devia.
- Próxima ação sugerida: corrigir (polish)
- Relações: §8 glossário.
- Confiança: alta.

### N-10 — Exportação: submeter sem escolher a população recarrega sem mensagem
- Origem: auditoria 20/09 §12 (N-10, S1), §19
- Problema original: o formulário de população submetido vazio volta à mesma tela sem aviso.
- Recomendação original: correção de varredura.
- Rastro posterior: visão-sistema 20/09 §D; `matriculas.html` sem commit desde 19/09.
- Specs relacionadas: 031 (FR-433 — sem população padrão).
- Implementação encontrada: nenhuma.
- Evidência no código atual: `interface/views.py:4186-4187` — `if not escolha: return … render(…)` sem erro; `interface/templates/interface/matriculas.html:41-44` — `<select>` sem `required` e com opção vazia "Escolha".
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, é barato (atributo `required` e/ou mensagem quando `GET` traz `populacao=` vazio).
- Lacuna residual: mensagem ou `required`.
- Grupo do resíduo: C
- Impacto atual: pequeno — o exportador repete a ação.
- Próxima ação sugerida: corrigir
- Relações: nenhuma.
- Confiança: alta.

### C7 · §18 — Autenticação institucional real
- Origem: auditoria 20/09 §1 (C7, "herdado"), §18 ("identidade real ⛔"), §22 Q10, recomendação final
- Problema original: o seletor de identidade é demonstração; o adaptador da API aceita `subject|escopo|permissões` sem assinatura.
- Recomendação original: integrar autenticação real como condição de saída do piloto.
- Rastro posterior: visão-sistema 20/09 §B ("Herdado desde a 002; o módulo de fronteira já está isolado para isso").
- Specs relacionadas: 002, 003 (FR-016 a FR-018 — produção recusa subir insegura), 009 FR-024.
- Implementação encontrada: só a barreira de produção.
- Evidência no código atual: `seguranca/api/authentication.py:7-23` — `InstitutionalBearerAuthentication` "Adaptador provisório"; `interface/identidade.py:107-120` — ator vem da sessão preenchida pelo seletor; `config/settings/production.py:1-20, 92-103` — produção recusa subir com seletor/adaptador de desenvolvimento (14 `_exigir`). Nenhuma dependência de OIDC/SAML/LDAP (`rg` em `processo_seletivo`, `config`, `pyproject.toml`).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim — sem ela o sistema não sobe em produção (por desenho). Parte da responsabilidade é do diretório institucional (outro sistema).
- Lacuna residual: adaptador contra o provedor do Ifes (gestão) e, separadamente, para o candidato (o portal tem provedor de demonstração próprio); vínculo identidade→papel continua inexistente (a 038 e a 040 dependem disso para não nomear responsável).
- Grupo do resíduo: A
- Impacto atual: bloqueia qualquer operação além de piloto assistido.
- Próxima ação sugerida: criar spec (depende de definição externa do provedor)
- Relações: C7; FR-564/D-003 da 038 (responsável não modelável sem ligação identidade→papel).
- Confiança: alta.

### ACH-25 · E-6 — Visão global do Processo vivo (+ "qual Edital precisa de atenção", "qual prazo vence primeiro")
- Origem: auditoria 20/09 §4 (PARCIAL), §6 ("Reduziu, não fechou"; nota 6), §9 (E2 nas intenções "qual Edital precisa de atenção" e "qual prazo vence primeiro"), §17, §22 Q7
- Problema original: o painel da 038 concorda com a Supervisão, mas é parcial por papel sem se declarar, 60% dos sinais do gestor não são acionáveis, recurso novo/sorteio/matrícula ficam fora, a Atenção é lista plana sem agregação por Edital, e não há ordenação global de prazos entre Editais.
- Recomendação original: "Fechar a 038 — não ampliá-la" (N-01…N-04); "Não recomendo outro painel".
- Rastro posterior: 040 (visão institucional, `7ac2c76`), 041 (Perfil na visão), 042 (hierarquia do detalhe) — sobem um nível (entre Processos) e **declaram não tocar** a Atenção (`specs/040-…/spec.md:34-37, 64-80, 214, 832`).
- Specs relacionadas: 022, 038, 040, 041, 042.
- Implementação encontrada: 040–042 entregam panorama cross-Processo (demanda × oferta, marcas "sem procura"/"demanda abaixo da oferta", filtro `atencao=1`), capacidade própria `visao:consultar` (`interface/visao_geral.py:34-45`; `interface/identidade.py:61-75`, dada ao Gestor), custo fixo de 5 leituras (`visao_geral.py:799-835`) e uma seção honesta "O que esta página não mede" (`visao_geral.html:350-369`). O "atenção" da 040 é **aritmética de demanda**, não sinal de condução (spec 040 D-007, `:35-37`).
- Evidência no código atual: dentro do Processo nada mudou — `supervisao.py:1391-1398` ordena espécie→Edital→alvo (sem agregação por Edital); `processo_detalhe.html:90-126` lista próximos marcos por Edital, sem ordenação global; N-01, N-02, N-04, N-05/06, N-07 abertos (blocos acima).
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: parcialmente — a visão de **conjunto** (entre Processos), que a E-6 também nomeava, passou a existir e é boa; a **condução** dentro do Processo continua no estado de 20/09. Não recomendo agregação por Edital nem ordenação global de prazos antes de limpar o ruído (N-05/N-06 respondem por 9 de 15 linhas do gestor): com o ruído fora, a lista plana encolhe e a agregação pode deixar de ser necessária.
- Lacuna residual: fechar N-01, N-02, N-04, N-05/N-06, N-07; reavaliar agregação por Edital depois.
- Grupo do resíduo: B (os componentes A estão nos blocos próprios)
- Impacto atual: visão global medida em 6/10 em 20/09; a 040 não move a nota de condução, move a de panorama institucional (dimensão que a auditoria não media).
- Próxima ação sugerida: validar (remedir após os fixes da 038)
- Relações: E-6; C1–C6; §22 Q4/Q7.
- Confiança: alta para "não tocou a Atenção"; média para o julgamento de que a 040 cobre a metade "conjunto" da E-6.

### Sete recusas fora das portas · D-G2 — fronteira 403/404
- Origem: auditoria 20/09 §4 ("ABERTO / GOVERNANÇA"), §6-bis (Recuperação de erros retida em 8), §11 (tabela de recusas), §16, §21; decisão `D-G2` em `doc/reavaliacao-ux-2026-09-18.md` §14-bis (`:699-722`), 19/09
- Problema original: `criar_edital`, `reaproveitar` e `supervisao` recusam falta de capacidade sobre objeto visível com 404.
- Recomendação original: D-G2 — as três passam a **403**; `anexo_do_rascunho`, `minha_etapa`, `inscricao_da_mesa`, `documento_da_mesa` ficam em 404; a spec curta registra a fronteira e **substitui explicitamente** a doutrina anterior citada por três delas.
- Rastro posterior: 038 lista como fora de escopo (`specs/038-…/spec.md:270-274`); visão-sistema §B "não executado"; nenhuma spec escrita (`rg D-G2 specs` só acha 022 e 038).
- Specs relacionadas: 033 (inventário das negativas), 022 FR-003, 007/009 (doutrina citada nas docstrings).
- Implementação encontrada: nenhuma.
- Evidência no código atual: `interface/views.py:400-403` (`criar_edital`: `if not ator.can("edital:criar"): raise Http404`, com o comentário "distinguir 'não existe' de 'você não pode'…"), `:1460-1461` (`reaproveitar`, `edital:elaborar`), `:4020-4021` (`supervisao`, `pode_supervisionar`). O inventário da 033 ainda as classifica como "recusa de autorização" em 404 (`specs/033-navegacao-por-capacidade/inventario-das-negativas.md:44-50, 116-142`), e `tests/test_gramatica_das_portas.py` cobra o inventário. A interface já não oferece os três caminhos a quem não pode: `views.py:3973-3975` (`pode_criar_edital`), `processo_detalhe.html:14,72` (Supervisão).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente — a decisão é do usuário e está tomada; mas depois do fix N-03 e das guardas de oferta, o 404 só aparece a quem digita a URL. O ganho é de coerência de taxonomia e de mensagem (a página de 403 nomeia a permissão), não de jornada.
- Lacuna residual: spec curta que registra a fronteira, troca os três `raise Http404` por recusa 403 explicada, e atualiza inventário + docstrings no mesmo commit.
- Grupo do resíduo: C (impacto); a legitimidade é de decisão já tomada — ver Incertezas
- Impacto atual: baixo.
- Próxima ação sugerida: criar spec curta (se o usuário mantiver a D-G2)
- Relações: E-2; N-03; §21 ("não trocar em bloco" — respeitado: as quatro de vínculo seguem 404).
- Confiança: alta.

### D-G1 — `FR-461` impeditiva (marco sem declaração de corte)
- Origem: `doc/reavaliacao-ux-2026-09-18.md` §14-bis (`:687-697`), 19/09; auditoria 20/09 §16 ("não executada")
- Problema original: marco sem `cutRule` publica com **aviso**; a 032 já distingue ausência de regra × regra que declara não governar Etapa, então o falso positivo que justificava o aviso não existe mais.
- Recomendação original: o aviso vira impedimento de publicação (spec curta).
- Rastro posterior: visão-sistema §B ("hoje é aviso"); nenhuma spec.
- Specs relacionadas: 032 FR-461, 014 FR-224, 026 (`PODE_PASSAR_A_EXISTIR`).
- Implementação encontrada: nenhuma.
- Evidência no código atual: `editais/domain/validation.py:1706-1747` — `severity=Severity.WARNING`, `code="milestone_without_cut_rule"`, docstring "Aviso, e não impedimento"; teste prende o aviso: `tests/interface/test_hardening_pos_auditoria.py:1100` (`== Severity.WARNING`). Atenuante: a regra de corte **pode nascer por Retificação** (`editais/domain/mutabilidade.py:515-520`), então o Edital publicado sem ela tem conserto.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, é decisão tomada e barata (trocar severidade na publicação, manter aviso na Retificação do acervo). O atenuante rebaixa a urgência.
- Lacuna residual: severidade `BLOCKING_ERROR` no ato de publicação + ajuste do teste que prende o aviso.
- Grupo do resíduo: B
- Impacto atual: Edital publicado "classifica e não convoca" até alguém retificar.
- Próxima ação sugerida: criar spec curta
- Relações: N-08 (reduz a classe de avisos); ACH-46.
- Confiança: alta.

### D-G3 — Sorteio declara fonte pública externa; regra do reaproveitamento
- Origem: `doc/reavaliacao-ux-2026-09-18.md` §14-bis (`:724-736`), 19/09; auditoria 20/09 §4 ("GOVERNANÇA"), §16 ("não executada; produto já suporta o modelo forte; a regra do reaproveitamento é a parte não óbvia")
- Problema original: os Editais correntes do Cefor declaram "o software sorteia e publica a semente"; o modelo do produto exige ocorrência externa declarada antes.
- Recomendação original: prospectivamente, inclusive para reaproveitados, exigir fonte pública externa; o produto não acomoda a semente própria como equivalente auditável.
- Rastro posterior: 035 registrou a pergunta sem responder (`specs/035-sorteio-executavel/spec.md:355-373`); nenhuma spec da D-G3.
- Specs relacionadas: 021 FR-076, 032 FR-467, 035, 023 (reaproveitamento).
- Implementação encontrada: a exigência já é do produto, por especificações anteriores à decisão.
- Evidência no código atual: publicação recusa marco de sorteio sem método (`editais/domain/validation.py:1752`, FR-467, só no ato de publicação); o método só aceita fonte do vocabulário fechado (`editais/domain/perfis.py:526-541` → `sorteios/infrastructure/fontes/__init__.py:83-92`). O reaproveitamento copia o `drawMethod` (`editais/domain/reaproveitamento.py:156-161, 310-320`) e o Edital reaproveitado passa de novo pela publicação, então a "cláusula antiga" estruturada não escapa: sem método, é recusado. O que escapa é **prosa** das Seções copiadas (família E-3/E-4, outro lote).
- Estado atual: RESOLVIDO POR OUTRO CAMINHO
- Ainda faz sentido?: parcialmente — a spec da D-G3 como tal é desnecessária no produto; o resíduo é (a) o vocabulário de fontes aceitar **"Fonte de demonstração"** em qualquer ambiente (ver NOVO-1) e (b) a redação dos Editais, que é ato institucional, não de software.
- Lacuna residual: NOVO-1; texto de Seção reaproveitada que contradiga o método estruturado.
- Grupo do resíduo: B (pelo NOVO-1)
- Impacto atual: baixo para o modelo; o NOVO-1 é o furo.
- Próxima ação sugerida: corrigir (NOVO-1); registrar a D-G3 como atendida pela 021/032
- Relações: NOVO-1; E-3.
- Confiança: média-alta — o caminho da publicação do reaproveitado foi lido, não percorrido.

### D-G4 — O peso continua da Etapa
- Origem: `doc/reavaliacao-ux-2026-09-18.md` §14-bis (`:738-749`); auditoria 20/09 §4, §16 ("encerrada, sem trabalho")
- Problema original: pergunta se o peso deveria ser do par marco×Etapa.
- Recomendação original: não mover sem Edital real que precise; encerrar a pergunta.
- Rastro posterior: nenhum.
- Specs relacionadas: 037 D-003.
- Implementação encontrada: nada a implementar.
- Evidência no código atual: `editais/domain/mutabilidade.py:449` — `("stages", "weight"): retificavel()`; nenhum "Peso (opcional)" em `interface/templates`.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não — encerrada por decisão.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma
- Relações: —
- Confiança: alta.

### D-G5 · "Retificação sem Modalidade" — Retificação passa a acrescentar Modalidade de Concorrência
- Origem: `doc/reavaliacao-ux-2026-09-18.md` §14-bis (`:751-764`, "a coisa mais grave da lista"); auditoria 20/09 §4, §5 Cenário B, §9 (E4), §16, §20 item 3
- Problema original: Edital publicado sem a ampla (ou sem uma cota) não tem conserto; a tela diz "Modalidades de Concorrência ainda não são definidas por aqui".
- Recomendação original: spec própria, "não pequena", com cinco restrições (preservar versões, efeito só pela nova versão, validar dependentes, não reescrever inscrições/ordens, recorte novo sem ordem própria).
- Rastro posterior: rascunho **não mesclado** em `claude/spec-039-alcance:specs/039-catalogo-de-modalidades/spec.md:65-85` (US2 "Acrescentar reserva a Edital publicado", P2, cita a D-G5); visão-sistema §A/§B.
- Specs relacionadas: 026 (`PODE_PASSAR_A_EXISTIR`), 034, 039 (rascunho).
- Implementação encontrada: nenhuma na main.
- Evidência no código atual: `interface/retificacao.py:1054` — `SECOES_QUE_ACRESCENTAM = frozenset({"perfis", "cronograma", "anexos"})`; `interface/templates/interface/retificar.html:158-159` — "Modalidades de Concorrência ainda não são definidas por aqui."; nenhum commit nesses arquivos desde 19/09.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim — é o único caso de Edital publicado sem correção possível no escopo deste lote (o outro, duas avaliações sem regra, é de outro lote).
- Lacuna residual: mesclar/concluir a spec (a 039 rascunho a embute num catálogo de Modalidades maior) e implementar.
- Grupo do resíduo: A
- Impacto atual: uma omissão de Modalidade na publicação impede a inscrição de não-cotistas (ou de cotistas) até o fim do certame; único remédio é cancelar e republicar.
- Próxima ação sugerida: criar spec (decidir se entra como US da 039 ou isolada)
- Relações: E-4 (três grafias da ampla); `ampla-concorrencia-tem-duas-grafias`.
- Confiança: alta.

### §6 — Sorteio fora do painel de condução
- Origem: auditoria 20/09 §6 ("Ausência declarada. Impacto real, mas menor"), §9 (E2), §20 ("não recomendo outro painel"), §22 Q8 ("Ainda não")
- Problema original: sorteio congelado e não executado, ou com data vencida e ocorrência não observada, não produz sinal.
- Recomendação original: **não** acrescentar agora; a tela do sorteio já conta a viagem inteira.
- Rastro posterior: 038 D-002 registra a exclusão (`specs/038-painel-de-conducao/spec.md:255-256`).
- Specs relacionadas: 021, 035, 038.
- Implementação encontrada: nenhuma (por decisão).
- Evidência no código atual: `interface/supervisao.py:495-506` — nenhuma espécie de sorteio; `UX-004` e `UX-065/066` só existem depois de haver ato de ordenação.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente — o único estado com valor real é "data publicada da ocorrência vencida sem observação/execução"; o resto é bem servido pela tela do sorteio. Não antes de limpar o ruído (N-05/N-06).
- Lacuna residual: eventual espécie "sorteio com ocorrência vencida e não executado".
- Grupo do resíduo: C
- Impacto atual: baixo (sorteio é ato com momento próprio e presença de quem o conduz).
- Próxima ação sugerida: nenhuma (revisitar após fechar a 038)
- Relações: E-6.
- Confiança: alta.

### §6 · §13 — Matrícula fora do painel de condução
- Origem: auditoria 20/09 §6 ("Impacto baixo hoje"), §9 (E2), §13 ("o Processo vivo mostra essa fase ❌"; "baixo hoje, crescente")
- Problema original: "quantos convocados ainda não enviaram Requerimento" não tem onde ser perguntado na condução.
- Recomendação original: ainda não; vira risco com dezenas de convocados.
- Rastro posterior: 038 D-002 (exclusão registrada); 040 declara que requerimentos "estão definidos e ainda não são apresentados" (`visao_geral.html:363-365`).
- Specs relacionadas: 029, 031, 038, 040.
- Implementação encontrada: nenhuma.
- Evidência no código atual: nenhuma espécie de matrícula em `supervisao.py:495-506`; a exportação é alcançável pelo Edital a quem tem `matricula:exportar` (`interface/acoes.py:128-…`).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente — só com volume real de convocados; é mais pulso (contagem) do que sinal.
- Lacuna residual: contagem "convocados × requerimentos enviados" por Edital, se o piloto mostrar necessidade.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma (medir no piloto)
- Relações: §13.
- Confiança: alta.

### §7 — Prazo restante renderizado de três formas
- Origem: auditoria 20/09 §6, §7 (S0), §19 "Polish"
- Problema original: "Faltam 19 dias" (portal) · "Encerra em 2 semanas, 5 dias" (Supervisão) · só a data (página do Processo).
- Recomendação original: uniformizar (polish).
- Rastro posterior: visão-sistema §C.
- Specs relacionadas: 022, 024, 038.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `interface/templates/interface/supervisao.html:102` (`|timeuntil`); `portal/templates/portal/_periodo.html:16` ("Faltam N dias"); `interface/templates/interface/processo_detalhe.html:97-98` (só data).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente — divergência de forma, não de valor; o `timeuntil` do Django é a forma mais fraca (semanas+dias).
- Lacuna residual: uma forma de prazo restante na gestão.
- Grupo do resíduo: C
- Impacto atual: mínimo.
- Próxima ação sugerida: corrigir (polish, junto de outro fix na mesma tela)
- Relações: FR-557 (mesma leitura, forma diferente).
- Confiança: alta.

### §7 — Prazo recursal ausente da página pública do resultado
- Origem: auditoria 20/09 §6-bis (Experiência do candidato e Resultado retidos por isto), §7 (S1, "divergência operacional"), §19 "Polish"
- Problema original: o acompanhamento diz "Cabe recurso até…"; a página pública do resultado não diz nada.
- Recomendação original: declarar a janela na página do resultado, como o acompanhamento já faz.
- Rastro posterior: visão-sistema §A ("Prazo recursal ausente da página pública do resultado").
- Specs relacionadas: 017 FR-055 ("Se a versão citada declarar prazo recursal, a informação normativa existente **pode** ser apresentada, sem mecanismo transacional" — `specs/017-publicacao-de-resultados/spec.md:515-516`), 018 FR-022/FR-023.
- Implementação encontrada: nenhuma na página pública.
- Evidência no código atual: `portal/templates/portal/resultado.html` — nenhuma ocorrência de recurso/prazo/janela exceto a causa de correção (`:38-41`); `portal/templates/portal/acompanhamento.html:160` mostra "Cabe recurso contra este resultado até …" ao candidato identificado.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim — FR-055 autoriza (MAY) e a janela já é computada (018 FR-022); quem chega pela lista pública, ou quem não conseguiu entrar na área do candidato, não sabe que há prazo correndo.
- Lacuna residual: exibir a janela (início/fim) do marco na página pública, sem ação.
- Grupo do resíduo: B
- Impacto atual: direito de recurso depende de a pessoa entrar na área do candidato ou ler o Edital.
- Próxima ação sugerida: corrigir
- Relações: 018.
- Confiança: alta.

### §8 — Glossário: "7 de 7" sem unidade, "sem marco no cronograma" sem consequência, seletor em vocabulário de código
- Origem: auditoria 20/09 §6-bis (Clareza conceitual não vai a 10), §8
- Problema original: a medida do sinal é número sem unidade; "sem marco no cronograma" não diz o que implica; o seletor lista permissões como `edital:elaborar`.
- Recomendação original: implícita — dar unidade e consequência (polish).
- Rastro posterior: nenhum.
- Specs relacionadas: 022 FR-032 (medida é par), 038.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `interface/templates/interface/_sinal.html:13-15` — `{{ numerador }} de {{ denominador }}` sem unidade (a `Medida` não carrega unidade, `supervisao.py:175-…`); `interface/supervisao.py:624-627` — "está sem marco no cronograma."; `interface/templates/interface/identificar.html:55-56` — `papel.1|join:", "` (permissões cruas).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente — unidade na medida sim (barato); o seletor é demonstração e desaparece com C7.
- Lacuna residual: unidade da medida por espécie ("inscrições sem cobertura de N submetidas"); consequência de UX-001 depende da decisão de N-05.
- Grupo do resíduo: C
- Impacto atual: pequeno, cognitivo.
- Próxima ação sugerida: corrigir (junto de N-05/N-07)
- Relações: N-05, N-07, N-09, C7.
- Confiança: alta.

### §13 · §18 "integrações" — Registro Acadêmico: importação/validação no destino não validada
- Origem: auditoria 20/09 §2 ("O que esta auditoria NÃO fez"), §13 (`[NÃO VALIDADO]`), §18, §19 "Integração", condição de saída do piloto
- Problema original: o arquivo sai honesto (colunas vazias explicadas), mas ninguém importou no destino.
- Recomendação original: validação ponta a ponta com o Registro Acadêmico, incluindo vocabulário de códigos.
- Rastro posterior: visão-sistema §E; nenhum documento posterior de validação (`git log --since=2026-09-20 -- doc docs` não traz nenhum).
- Specs relacionadas: 029, 031.
- Implementação encontrada: exportação completa do lado de cá.
- Evidência no código atual: `interface/views.py:4152-4247` (`exportar_matriculas`: permissão própria, prévia registrada em trilha, arquivo não guardado); `visao_geral.html:350-354` repete o limite ("não sabe se a matrícula foi criada lá").
- Estado atual: IMPLEMENTADO, MAS NÃO VALIDADO
- Ainda faz sentido?: sim — é integração com outro sistema; `COD_CURSO/COD_TURNO/COD_POLO` e a semântica de `CLASSIF_CURSO_FINAL` só o destino resolve.
- Lacuna residual: rodada de importação real com o setor responsável e registro do resultado.
- Grupo do resíduo: B (responsabilidade compartilhada com o sistema de destino)
- Impacto atual: risco de retrabalho na primeira matrícula real.
- Próxima ação sugerida: validar
- Relações: C7 (ambos condição de saída do piloto).
- Confiança: alta.

### §18 — Custo de consulta ~17 por Edital publicado
- Origem: auditoria 20/09 §2 ("Custo de consulta, medido"), §18, condição de saída ("medição num Processo de dez ou mais Editais")
- Problema original: Processo 64 consultas e Supervisão 61 com 3 Editais; linear; 20 Editais projetam ~350.
- Recomendação original: medir antes de um Processo grande.
- Rastro posterior: nenhuma medição posterior.
- Specs relacionadas: 022 FR-031/D-008, 038 T021, 040 SC-209 (a visão institucional tem custo **fixo** de 5 leituras).
- Implementação encontrada: guarda de invariância só contra número de **recursos** (`tests/integration/supervisao/test_sinais.py:346-407`), não contra número de Editais.
- Evidência no código atual: `interface/supervisao.py:1364-1384` — laço por Edital publicado com `resumo_da_etapa` por Etapa (`:685-686`) e `versao_vigente_do_edital` por Edital (`:1381`); logo, o custo cresce com Editais × Etapas.
- Estado atual: IMPLEMENTADO, MAS NÃO VALIDADO
- Ainda faz sentido?: parcialmente — Processos do Cefor têm tipicamente poucos Editais; linear com constante ~17 é aceitável até dezenas. Vale uma medição única, não otimização.
- Lacuna residual: medir com 10+ Editais e registrar.
- Grupo do resíduo: C
- Impacto atual: nenhum observado.
- Próxima ação sugerida: validar
- Relações: condição de saída do piloto.
- Confiança: média — cardinalidade inferida do código, não medida.

### §18 — Observabilidade: sem métrica de condução
- Origem: auditoria 20/09 §18 ("log estruturado JSON existe; não há métrica de condução")
- Problema original: nenhuma métrica operacional (sinais abertos, idade dos recursos etc.).
- Recomendação original: implícita.
- Rastro posterior: nenhum.
- Specs relacionadas: 003.
- Implementação encontrada: log JSON.
- Evidência no código atual: `backend/config/settings/base.py:248-255` (`JsonFormatter` de `processo_seletivo.shared.observability`).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: não agora — com equipe de 2–3 pessoas, o painel é a métrica; exportar contadores seria overengineering antes do piloto.
- Lacuna residual: nenhuma relevante hoje.
- Grupo do resíduo: C
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma
- Relações: —
- Confiança: média.

### §18 — Fonte real do sorteio só com E2E atrás de flag
- Origem: auditoria 20/09 §18 ("fonte do sorteio tem E2E real atrás de flag")
- Problema original: o adaptador da Loteria Federal não roda no CI.
- Recomendação original: implícita (validar integração).
- Rastro posterior: `doc/achado-fonte-real-do-sorteio-sem-gatilho.md` (registro próprio; ver CLAUDE.md).
- Specs relacionadas: 021, 035.
- Implementação encontrada: E2E existente e pulado por padrão.
- Evidência no código atual: `backend/tests/interface/test_sorteio_com_a_fonte_de_producao.py:23, 49` (`SORTEIO_E2E_FONTE_REAL`).
- Estado atual: DUPLICADO / ABSORVIDO (em `doc/achado-fonte-real-do-sorteio-sem-gatilho.md`)
- Ainda faz sentido?: —
- Lacuna residual: a do achado dono.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma aqui
- Relações: NOVO-1 (a fonte falsa aceita em produção é o outro lado do mesmo tema).
- Confiança: alta.

### ACH-60 · §16 "Organização por Perfil/polo" — só cruzar
- Origem: auditoria 20/09 §4 ("ABERTO"), §5 Cenário D (🔴), §10, §16 ("pergunta aberta, não decidida"), §21 ("não abstrair polo antes do Edital real")
- Problema original: distribuição/alocação sem recorte por Perfil, polo ou Modalidade.
- Recomendação original: pesquisa antes de abstração.
- Rastro posterior: 040 registra o mesmo limite (`specs/040-…/spec.md:847`, G-004); 044 (recorte transversal documental) é só spec e trata documento, não polo.
- Specs relacionadas: 011, 012, 040, 044.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `interface/templates/interface/distribuicao.html` e `alocacoes.html` — **0** ocorrências de "perfil|polo|modalidade" (`grep -ci`); único commit recente em `avaliacoes/` (`a2b1e1f`, 25/09) não toca distribuição.
- Estado atual: DUPLICADO / ABSORVIDO (ACH-60 do lote de 16/09 e AX-6 do lote de 15/09)
- Ainda faz sentido?: —
- Lacuna residual: a dos lotes donos.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma aqui
- Relações: AX-6, ACH-60, G-004 da 040.
- Confiança: alta.

### "Recurso sem prova" (sem anexo do recorrente) — só cruzar
- Origem: auditoria 20/09 §4 ("ABERTO"), §6-bis (Recursos retido em 7, Experiência do candidato em 8)
- Problema original: `/selecoes/…/recorrer` tem `select` de objeto e `textarea`; nenhum anexo.
- Recomendação original: campo de anexo com o regime de arquivo da inscrição (visão-sistema §A).
- Rastro posterior: visão-sistema §A; 036 (instrução do recurso, prova por ato de terceiro).
- Specs relacionadas: 018, 036.
- Implementação encontrada: nenhuma no portal.
- Evidência no código atual: `portal/templates/portal/recorrer.html` — nenhum `type="file"` nem `enctype`.
- Estado atual: DUPLICADO / ABSORVIDO (lote dos relatórios de 16/09–19/09 — recurso sem prova / 036)
- Ainda faz sentido?: —
- Lacuna residual: a do lote dono.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma aqui
- Relações: 036.
- Confiança: alta.

### §12 (fora da lista) · `doc/achado-seed-demo-numero-nao-numerico.md` — `seed_demo --numero` quebra fora de dois dígitos
- Origem: `doc/achado-seed-demo-numero-nao-numerico.md` (15/09); auditoria 20/09 §12 ("fora da lista… 3 dígitos quebra"), §19
- Problema original: o número é interpolado em UUIDs literais; valor não numérico **ou** de 3 dígitos produz UUID inválido e traceback — inclusive no primeiro Edital.
- Recomendação original: recusar no `add_argument` com mensagem (a saída "que menos promete").
- Rastro posterior: nenhum; último commit no comando é `add08d1` (18/09).
- Specs relacionadas: 028.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `processos/management/commands/seed_demo.py:579-582` (`--numero`, `default="01"`, sem `type`/validação); interpolação `f"00000000-0000-0000-00{numero}-…"` em `:82, 97, 105…348`; `_numero_do_segundo_edital` `:371-380` só trata o não numérico (e nunca chega lá).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, é ferramenta de demonstração e o conserto é de uma linha (validar `^\d{2}$`).
- Lacuna residual: validação na entrada.
- Grupo do resíduo: C
- Impacto atual: só para quem prepara demonstração/estudo.
- Próxima ação sugerida: corrigir
- Relações: —
- Confiança: alta.

### §2 · §19 — Teste instável: "CPF" no token CSRF
- Origem: auditoria 20/09 §2 ("A falha da suíte não é regressão"), §19; visão-sistema §C
- Problema original: `assert "CPF" not in corpo` é substring sobre o HTML inteiro; o token CSRF sorteado pode conter "CPF".
- Recomendação original: corrigir a asserção (varredura).
- Rastro posterior: nenhum; arquivo sem commit desde `e0ce2d1` (02/09).
- Specs relacionadas: 010.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `backend/tests/integration/identidade/test_adicionar_credencial.py:46-52` — `assert "CPF" not in corpo` sobre `client.get(...).content`.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim — probabilidade baixa por execução (~62 posições × 62⁻³ ≈ 0,03%), mas derruba CI sem causa; conserto trivial (casar rótulo/campo, não substring).
- Lacuna residual: asserção sobre o texto visível ou sobre `name="cpf"`.
- Grupo do resíduo: C
- Impacto atual: falso vermelho ocasional.
- Próxima ação sugerida: corrigir
- Relações: `varredura-le-o-comentario` (mesma família).
- Confiança: alta.

### `docs/visao-sistema/index.html` (20/09) — lacunas próprias declaradas além da auditoria de 20/09
- Origem: `docs/visao-sistema/index.html` §"Auditoria de consistência" (linhas ~3272-3467) e §"Lacunas e oportunidades" A–E (~3610-3730), commit `12bc8fd` (20/09)
- Problema original: o documento reconstrói o produto do código e repete N-01…N-10, D-G*, C7; acrescenta quatro itens: (1) README diz "31 de 31" append-only; (2) teto de inscrições por candidato aplicado e não publicado (AX-9); (3) leitura múltipla não consolida; (4) AX-1 (sentido do desempate não retificável).
- Recomendação original: por item (§A–§E); nada decidido.
- Rastro posterior: (3) virou `doc/achado-duas-avaliacoes-sem-regra-de-combinacao.md` (21/09).
- Specs relacionadas: —
- Implementação encontrada / Evidência no código atual:
  - (1) `README.md:73` ainda diz `31 de 31`; `seguranca/papeis.py:26-171` tem **33** tabelas em `TABELAS_APPEND_ONLY` → NÃO IMPLEMENTADO (deriva de doc; C). O CLAUDE.md já diz 33.
  - (2) `maxInscricoesPorCandidato` aparece em 6 `.py` e em **0** templates (`rg -l`) → aberto; DUPLICADO / ABSORVIDO em AX-9 (lote de 15/09).
  - (3) `resultados/domain/regra.py:71-75` — `REGRA_DE_COMBINACAO_AUSENTE` para `previstas > 1` → aberto; DUPLICADO / ABSORVIDO no achado de 21/09 (outro lote).
  - (4) `interface/retificacao.py:335` — `CAMPOS_CRITERIO = [("order", …)]` → aberto; DUPLICADO / ABSORVIDO em AX-1.
- Estado atual: DUPLICADO / ABSORVIDO (itens 2–4); o item 1 é residual próprio, NÃO IMPLEMENTADO
- Ainda faz sentido?: item 1 sim (trivial).
- Lacuna residual: corrigir `README.md:73` para 33 (ou para a forma "N de M" sem número, como o CLAUDE.md recomenda vigiar o zero).
- Grupo do resíduo: C (item 1)
- Impacto atual: quem sobe o ambiente pelo README vê 33 e pensa que algo está errado.
- Próxima ação sugerida: corrigir (item 1)
- Relações: AX-1, AX-9, achado das duas avaliações; o documento em si não se atualiza e já está vencido em N-03 (fechado depois).
- Confiança: alta.

### `doc/inventario-supervisao-do-processo.md` (09/09) — achados colaterais da Parte 3 e as duas perguntas não decididas
- Origem: inventário 09/09, Parte 1 §018 ("`interface:recursos` não é alcançada por nenhuma tela"), Parte 3 (tabela), "O que este inventário não decidiu"
- Problema original: (a) tela de recursos inalcançável; (b) "ato emitido e não divulgado" candidato a sinal; (c) "Em preenchimento" × "rascunho"; (d) Etapa com ciclo de vida?; (e) `EventoCronograma.status` deixa de ser declarado? — "não agora".
- Recomendação original: (a) link em `acoes.py`; (b) semântica a definir; (d)(e) governança.
- Rastro posterior: 022 e 038 implementadas; auditoria 20/09 N-06 contradiz a premissa de (e).
- Specs relacionadas: 022, 033, 038.
- Implementação encontrada / Evidência no código atual: (a) `interface/acoes.py:117-127` — "Recursos recebidos (N)" → RESOLVIDO; (b) `interface/supervisao.py:490-493, 997-…` — `UX-066` → RESOLVIDO; (c) `interface/templates/interface/inscricoes.html:93` e `processo_detalhe.html:76` usam "Em preenchimento" consistentemente na interface, "rascunho" só em comentários → cosmético, sem ação; (d) sem ciclo de vida de Etapa — decisão mantida; (e) ver N-06: a premissa "declarado à mão" não se sustenta porque a interface não oferece o campo.
- Estado atual: RESOLVIDO (a, b); (e) absorvido em N-06
- Ainda faz sentido?: não para a–d; (e) segue em N-06.
- Lacuna residual: nenhuma além de N-06.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: N-06; UX-066; N-02 (o contador de (a) conta todos os recursos, não os pendentes).
- Confiança: alta.

### `doc/descoberta-conducao-por-presidencia-unica.md` (08/09) — piso de duas identidades não dito; recurso sem julgador não antecipado
- Origem: descoberta 08/09, §2–§4
- Problema original: segregação ternária (FR-021 da 001) e impedimento recursal (018) exigem ≥2 identidades com divisão específica; a interface não diz o piso antes do 403, e nada avisa, antes da divulgação, que o Processo caminha para recurso sem julgador elegível.
- Recomendação original: nenhuma — três perguntas de governança (piso aceitável? arranjo legítimo? antecipar a recusa?).
- Rastro posterior: 022 criou `UX-005` (recurso **existente** com comissão inteira impedida); memória do usuário: equipe inicial de 2–3 pessoas, gargalo é o julgador.
- Specs relacionadas: 001 FR-021, 017, 018 (Decisão 018 §5B), 022, 038.
- Implementação encontrada: a interface antecipa a segregação na publicação (`publicacoes/application/selectors.py:267`, `impede_por_segregacao`); `UX-005`/`UX-064` em `interface/supervisao.py:1130-1199` — só com peça já interposta e só olhando **membros da comissão** (o julgador de fora não entra na conta, como a docstring `:1141-1145` admite).
- Evidência no código atual: acima; nenhuma verificação preventiva de julgador elegível antes da divulgação (`rg` sem ocorrência na prévia de publicação).
- Estado atual: NÃO IMPLEMENTADO (as três perguntas seguem sem resposta registrada)
- Ainda faz sentido?: parcialmente — com a equipe real de 2–3 pessoas e o julgador como gargalo, "avisar na prévia de divulgação que nenhum julgador conhecido está desimpedido" é útil, mas o sistema não sabe quem tem `recurso:julgar` (papéis vêm da sessão) — a mesma limitação de C7.
- Lacuna residual: decisão de governança sobre o piso e sobre a antecipação; só implementável de forma honesta depois de identidade→papel existir.
- Grupo do resíduo: C
- Impacto atual: o piso é descoberto no 403.
- Próxima ação sugerida: nenhuma (governança; depende de C7)
- Relações: C7; UX-005; D-003 da 038.
- Confiança: média — a verificação da antecipação foi por ausência de código, não por percurso.

### §16 — Responsabilidade no painel (não nomear pessoa)
- Origem: auditoria 20/09 §16 ("a decisão da 038 está certa… Manter a decisão"), §21
- Problema original: pergunta se o painel deveria nomear responsável.
- Recomendação original: manter; o que falta é a capacidade a pedir (N-04).
- Rastro posterior: 040 mantém (`specs/040-…/spec.md:218`).
- Specs relacionadas: 038 FR-564, D-003.
- Implementação encontrada: mantida.
- Evidência no código atual: `interface/supervisao.py:1141-1145, 1231-1232` — nenhum sinal nomeia pessoa.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não há o que fazer.
- Lacuna residual: nenhuma (o resíduo é N-04).
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: N-04, C7.
- Confiança: alta.

---

## Verificação do §21 "O que não fazer" — respeitado até `bb774d9`
- `scheduleEventId`/`status` **não** entraram na Retificação (`mutabilidade.py:432, 447`).
- 404→403 **não** foi trocado em bloco (as quatro de vínculo seguem 404, inventário da 033 `:45-50`).
- `UX-001`/`UX-002` **não** foram silenciados (`supervisao.py:1368-1371`).
- Avisos de validação **não** foram jogados na Atenção (`ESPECIES`, `supervisao.py:495-506`).
- Nenhum responsável individual modelado (FR-564).
- Polo **não** foi abstraído (040 G-004 registra e não oferece filtro).

---

## 1. Tabela-resumo

| ID | Título | Estado | Grupo | Próxima ação |
|---|---|---|---|---|
| C1 · N-01 | Frase de ausência absoluta sobre leitura parcial; vista parcial não se declara | NÃO IMPLEMENTADO | A | corrigir |
| C2 · N-02 | Recurso aguardando admissibilidade sem sinal | NÃO IMPLEMENTADO | A | criar spec curta / emenda da 038 |
| C3 · N-03 · `4ec1cbb` | Link "Abrir a Supervisão" sem guarda | RESOLVIDO | — | nenhuma |
| C4 · N-04 | Sinal sem caminho não diz a quem pedir | NÃO IMPLEMENTADO | B | corrigir (após N-05/N-06) |
| C6 · N-06 | `schedule.status` derivado que nada deriva → UX-002 permanente | NÃO IMPLEMENTADO | A | criar spec (decidir doutrina) |
| C5 · N-05 | UX-001/UX-002 encaminham à Retificação que não os resolve | NÃO IMPLEMENTADO | A | criar spec (com N-06; decidir UX-001) |
| N-07 · ACH-27 | Contador de cobertura inclui eliminados antes | NÃO IMPLEMENTADO | B | corrigir |
| N-08 | Avisos de validação fora da Atenção | NÃO IMPLEMENTADO | C | nenhuma (fronteira a decidir) |
| N-09 | `cand:…` e UUIDs na tela do recurso | NÃO IMPLEMENTADO | C | corrigir (polish) |
| N-10 | Exportação vazia sem mensagem | NÃO IMPLEMENTADO | C | corrigir |
| C7 | Autenticação institucional real | NÃO IMPLEMENTADO | A | criar spec (depende do provedor) |
| ACH-25 · E-6 | Visão global do Processo vivo | PARCIALMENTE RESOLVIDO | B | validar (remedir após fixes) |
| D-G2 · sete recusas | 403 para `criar_edital`, `reaproveitar`, `supervisao` | NÃO IMPLEMENTADO | C | criar spec curta (se mantida) |
| D-G1 | FR-461 impeditiva | NÃO IMPLEMENTADO | B | criar spec curta |
| D-G3 | Fonte pública externa do sorteio / reaproveitamento | RESOLVIDO POR OUTRO CAMINHO | B (NOVO-1) | corrigir NOVO-1 |
| D-G4 | Peso da Etapa | RESOLVIDO | — | nenhuma |
| D-G5 | Retificação acrescenta Modalidade | NÃO IMPLEMENTADO | A | criar spec (rascunho na 039) |
| §6 sorteio | Sorteio fora do painel | NÃO IMPLEMENTADO | C | nenhuma |
| §6/§13 matrícula | Matrícula fora do painel | NÃO IMPLEMENTADO | C | nenhuma (medir no piloto) |
| §7 prazo | Prazo restante em três formas | NÃO IMPLEMENTADO | C | corrigir (polish) |
| §7 recurso público | Prazo recursal ausente da página pública do resultado | NÃO IMPLEMENTADO | B | corrigir |
| §8 glossário | "7 de 7" sem unidade; "sem marco" sem consequência; seletor cru | NÃO IMPLEMENTADO | C | corrigir |
| §13 · §18 RA | Registro Acadêmico sem validação no destino | IMPLEMENTADO, MAS NÃO VALIDADO | B | validar |
| §18 custo | ~17 consultas por Edital no painel | IMPLEMENTADO, MAS NÃO VALIDADO | C | validar |
| §18 observabilidade | Sem métrica de condução | NÃO IMPLEMENTADO | C | nenhuma |
| §18 fonte real | E2E da Loteria atrás de flag | DUPLICADO / ABSORVIDO (achado-fonte-real-do-sorteio-sem-gatilho) | — | nenhuma aqui |
| ACH-60 · polo | Organização por Perfil/polo | DUPLICADO / ABSORVIDO (ACH-60, AX-6) | — | nenhuma aqui |
| Recurso sem prova | Recorrente não anexa documento | DUPLICADO / ABSORVIDO (lote 16–19/09, 036) | — | nenhuma aqui |
| seed_demo `--numero` | Número fora de 2 dígitos quebra | NÃO IMPLEMENTADO | C | corrigir |
| Teste CSRF | "CPF" no token CSRF | NÃO IMPLEMENTADO | C | corrigir |
| visão-sistema (1) | README diz 31 de 31; são 33 | NÃO IMPLEMENTADO | C | corrigir |
| visão-sistema (2–4) | AX-9 teto, duas avaliações, AX-1 | DUPLICADO / ABSORVIDO (AX-9, achado de 21/09, AX-1) | — | nenhuma aqui |
| Inventário 09/09 | Recursos inalcançável; ato não divulgado; status declarado | RESOLVIDO (e absorvido em N-06) | — | nenhuma |
| Presidência única | Piso de 2 identidades não dito; julgador não antecipado | NÃO IMPLEMENTADO | C | nenhuma (governança; depende de C7) |
| §16 responsabilidade | Não nomear pessoa no painel | RESOLVIDO | — | nenhuma |

## 2. Contagens por estado (35 linhas)

| Estado | Nº |
|---|---|
| RESOLVIDO | 4 |
| RESOLVIDO POR OUTRO CAMINHO | 1 |
| PARCIALMENTE RESOLVIDO | 1 |
| NÃO IMPLEMENTADO | 23 |
| IMPLEMENTADO, MAS NÃO VALIDADO | 2 |
| SUPERADO / OBSOLETO | 0 |
| DUPLICADO / ABSORVIDO | 4 |
| CONTRADITO POR DECISÃO POSTERIOR | 0 |

Resíduos por grupo: **A = 6** (N-01, N-02, N-05, N-06, C7, D-G5) · **B = 7** (N-04, N-07, E-6, D-G1, D-G3/NOVO-1, prazo recursal público, RA) · **C = 14**.

Condicionantes C1–C7 de 20/09: **1 de 7 fechada** (C3). As demais estão exatamente como em 20/09.
Decisões D-G1…D-G5: D-G4 encerrada; D-G3 atendida por specs anteriores (com furo NOVO-1); **D-G1, D-G2 e D-G5 não executadas e sem spec na main** (D-G5 tem rascunho na branch não mesclada `claude/spec-039-alcance`).

## 3. Achados NOVOS encontrados de passagem

- **NOVO-1 — "Fonte de demonstração" é fonte publicável em produção.** `sorteios/infrastructure/fontes/__init__.py:83-92` registra o falso sem condição de ambiente; `interface/forms.py:318-322` o oferece no seletor da composição (`sorted(FONTES)`); `editais/domain/perfis.py:526-541` o aceita; `config/settings/production.py` não o recusa (as 14 guardas cobrem segredo, hosts, HTTPS, banco, seletores e autenticação, não a fonte). O falso devolve material fixo `12345 67890 11223 44556 77889` (`sorteios/infrastructure/fontes/loteria_federal.py:150-162`) — semente previsível e não externa. Um Edital publicado em produção pode sortear com ela. É o furo que resta na D-G3 e no FR-076 da 021. Atenuante: o nome aparece no manifesto e na tela pública. Saída provável: a mesma barreira de produção que já existe para os seletores de identidade (sem quebrar `seed_demo`). Grupo B.
- **NOVO-2 — "Recursos recebidos (N)" conta recursos decididos.** `interface/acoes.py:120-127` usa `Recurso.objects.filter(inscricao__edital=edital).count()`; o comentário justifica o número porque "o recurso corre contra prazo", mas o total não distingue pendente de decidido — e é a única recuperação de N-02. Grupo C.
- **Refinamento de N-06 (não é achado novo, é premissa corrigida):** o inventário de 09/09 trata o status do Evento como declarado à mão, o contrato da 026 o chama de derivado, e a interface não oferece o campo nem na composição nem na Retificação — só a API o aceita (`editais/api/serializers.py:186`). O conserto começa por escolher a doutrina.

## 4. Incertezas que exigem validação humana

1. **D-G2 rebaixada para C por impacto**, e não por legitimidade: é decisão já tomada pelo usuário. Se a prioridade for coerência de taxonomia, sobe; o custo é pequeno (três `raise Http404`, inventário da 033, docstrings).
2. **N-02 como A**: o FR-561 é escrito só para "aguardando julgamento"; incluir a admissibilidade é decisão de produto (espécie nova × ampliar UX-064) e exige revisar o catálogo fechado (FR-565).
3. **N-06 — derivar ou declarar?** Duas doutrinas escritas se contradizem (inventário 09/09 × contrato 026). A escolha é do usuário, e qualquer uma basta.
4. **N-05 — o destino do UX-001** em Edital publicado (Etapa sem Evento é estrutural e legítima): sinal sem destino, ou sair da Atenção para a validação? Decisão de fronteira ligada a N-08.
5. **E-6 "parcialmente resolvido"** conta a 040 como a metade "conjunto" da visão global. Se a E-6 for lida só como condução dentro do Processo, o estado seria NÃO IMPLEMENTADO desde 20/09.
6. **NOVO-1**: confirmar se algum controle fora do repositório (processo de implantação, revisão de Edital) já impede declarar a fonte de demonstração em produção.
7. **Nada foi reproduzido em execução** (regra do lote): N-01, N-02, N-07 e o custo de consulta foram confirmados só pela leitura de código e testes, sem percorrer a interface.
8. **RA**: a validação depende do sistema de destino e do setor dono; não cabe ao software sozinho.

