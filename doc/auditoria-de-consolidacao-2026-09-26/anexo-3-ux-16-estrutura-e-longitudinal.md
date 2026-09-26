# Lote 3 — UX de 16/09 (cenários 3–6, top 10, raízes E-1…E-7), reavaliação de 18–19/09 e retrato longitudinal

Base: `bb774d9` (= origin/main de 25/09/2026). Somente leitura. Caminhos de código relativos a
`backend/processo_seletivo/` salvo quando indicado. Nenhuma suíte foi rodada: "teste que cobre" quer
dizer que o arquivo existe e referencia o requisito/código, não que foi executado nesta auditoria.

Fontes do lote: `doc/auditoria-exploratoria-ux-2026-09-16.md` (§5-bis em diante),
`doc/diario-reauditoria-2026-09-16.md` (Sessões 2, 3 e 5: linhas 901, 1000, 1210, 1441, 1515),
`doc/reavaliacao-ux-2026-09-18.md` (inteiro, para o rastro),
`doc/relatorio-longitudinal-produto-001-a-037-2026-09-19.md` (preâmbulo de 21/09 e corpo).

---

## Parte A — Achados dos cenários 3–6 (ACH-46…ACH-61)

### ACH-46 — Convocação e suplência inalcançáveis num Edital sem regra de corte
- Origem: auditoria-exploratoria-ux-2026-09-16 §6 item 1, §11 E-1, §13.1 (16/09)
- Problema original: sem `cutRule` não havia tela de corte (link condicionado em `detalhe.html:146`), nem geração, nem faixa, nem convocação; a ocupação oferecia "Pedir a faixa seguinte" que sempre falhava; a etapa 5 silenciava a consequência.
- Recomendação original: 13.1 (a) ocupação não oferecer botão impossível e explicar a cadeia; (b) etapa 5 dizer que sem corte não há convocação; (c) link do corte deixar de depender de `cutRule`.
- Rastro posterior: reavaliação 18/09 §5 e §11 — (a) e (b) pela `032`, (c) aberto; §14 (19/09) — (c) fechada pela `037`. `D-G1` (reavaliação §14-bis, 19/09) decidiu tornar a `FR-461` **impeditiva**; convergência 20/09 §16: não executada.
- Specs relacionadas: 014, 032 (FR-461, FR-463), 037 (FR-538…540).
- Implementação encontrada: aviso na publicação + razão no lugar do botão na ocupação + destino do corte sempre oferecido a quem classifica.
- Evidência no código atual: `editais/domain/validation.py:1706-1751` — `_marco_sem_regra_de_corte` emite `milestone_without_cut_rule` com `Severity.WARNING` (`:1735-1736`) e a mensagem nomeia a cadeia inteira; `interface/views.py:2855-2868` — "O destino do corte não pende mais da regra de corte (037, FR-538)"; `ocupacao/application/selectors.py:216` — `faixaDisponivel` falso quando não há regra. Testes: `tests/interface/test_corte.py`, `tests/interface/test_destinos_do_edital.py`, `tests/unit/editais/test_executabilidade.py`.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não como achado — as três partes da 13.1 estão no código. O que sobra é a decisão `D-G1` (aviso → impedimento), que é trabalho criado por governança, não resíduo do achado.
- Lacuna residual: nenhuma do achado; `D-G1` não executada (a mensagem continua `WARNING`) — lote 4.
- Grupo do resíduo: —
- Impacto atual: quem ignora o aviso ainda publica um marco que classifica e não convoca; é exatamente o risco que `D-G1` quis fechar.
- Próxima ação sugerida: nenhuma aqui; `D-G1` segue no lote 4.
- Relações: E-1 (raiz), E-7 (família), `D-G1`, reavaliação §15 "decisão de governança que continua aberta".
- Confiança: alta — código e testes lidos.

### ACH-47 — Reserva de vagas publicada sem apuração nem convocação por recorte
- Origem: 16/09 §5-bis.1, §6 item 0 (S4/P0); diário linha 901
- Problema original: marco computado emitia uma ordem única (`emissao.py:58-63`, `lista_id=None` fixo: "só o sorteio emite por lista"); corte e ocupação dos recortes reservados sempre falhavam.
- Recomendação original: emitir por lista quando o Perfil declara reserva, ou impedir reserva em marco pontuado.
- Rastro posterior: reavaliação 18/09 §5 — "nomeado, não resolvido" (aviso + frase "a apuração acontece fora do sistema"); §13 (19/09) — `034` implementada, `SC-169/170` percorridos: convocação pelos três recortes; convergência 20/09 §4 "Ordem por recorte — FECHADO".
- Specs relacionadas: 015, 016, 021, 032, 034 (FR-490…499, D-004).
- Implementação encontrada: uma ordem por recorte em marco computado; derivação única dos recortes para classificação e ocupação.
- Evidência no código atual: `classificacao/application/emissao.py:20-47` (docstring "Uma ordem por recorte (034, FR-490)") e `:80-100` (vigente filtrado por `lista_id=recorte`; o comentário antigo foi removido junto da decisão); `editais/domain/recortes.py:33-60` (`recortes_do_perfil`, ampla primeiro, AC declarada reduzida à linha geral); a frase "acontece fora do sistema" não existe mais no código (grep vazio). Testes: `tests/interface/test_ocupacao.py`, `tests/fixtures/recortes.py`, `tests/interface/test_navegacao_entre_recortes.py`.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma no computado. A divergência do **sorteio** (recorte próprio para a AC declarada) ficou fora por `D-004` — ver ACH-54.
- Grupo do resíduo: —
- Impacto atual: nenhum para marco computado.
- Próxima ação sugerida: nenhuma.
- Relações: E-1, E-7; ACH-54 (a metade do sorteio); `D-G5` (Retificação não acrescenta Modalidade, nascida no percurso da 034 — lote 4). **Não confundir com `cf18a6b` (25/09)**: aquele commit é sobre **Cadastro Reserva** (suplentes, `reserveType`/`reserveLimit`), não sobre reserva de vagas por Modalidade — ver NOVO-1 no fim.
- Confiança: alta.

### ACH-48 — A validação proibia o sorteio sem Etapa que a ajuda descrevia
- Origem: 16/09 §5-bis.2; diário linha 1000
- Problema original: marco de sorteio em Edital sem Etapas recusado ("deve enumerar ao menos uma Etapa"), contra a ajuda da mesma tela; obrigava Etapa fictícia.
- Recomendação original: alinhar regra e ajuda.
- Rastro posterior: reavaliação 18/09 §4.2 — ✅ pela `030`.
- Specs relacionadas: 030 (FR-432).
- Implementação encontrada: exigência condicionada à forma da ordem.
- Evidência no código atual: `editais/domain/marcos.py:91-104` — `exige_etapa` devolve `False` para `POR_SORTEIO`; `interface/templates/interface/_marco.html:65` — ajuda diz que o sorteio "pode não ter Etapa alguma"; `interface/forms.py:233`. Testes: `tests/interface/test_campos_que_a_escolha_governa.py`.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: E-7 (a regra afirmada em prosa e não aplicada, invertida aqui).
- Confiança: alta.

### ACH-49 — Edital publicado sem marco algum, sem impedimento
- Origem: 16/09 §5-bis.2, §6 item 0 (S4/P0)
- Problema original: `IMPEDE: []` para Perfil sem marco; Edital "Sorteio público" publicado com `classificationMilestones = []`.
- Recomendação original: 13.7 (a) `IMPEDE` para Perfil sem marco.
- Rastro posterior: reavaliação 18/09 §5 — ✅ pela `032`; convergência 20/09 §17 E-7 ✅.
- Specs relacionadas: 032 (FR-457, FR-460).
- Implementação encontrada: impeditivo só no ato de publicação (Retificação do acervo preservada).
- Evidência no código atual: `editais/domain/validation.py:1660-1703` — `_perfil_sem_marco`, `code="profile_without_milestone"` (`:1695`), `BLOCKING_ERROR`, recortado a `ATO_DE_PUBLICACAO`. Testes: `tests/unit/editais/test_executabilidade.py`, `tests/integration/editais/test_acervo_inexecutavel_continua_retificavel.py`.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: E-7, 13.7(a).
- Confiança: alta.

### ACH-50 — Documento de sorteio publicava método falso e omitia a regra do sorteio
- Origem: 16/09 §5-bis.2, §6 item 0 (S4/P0)
- Problema original: PDF imprimia "soma ponderada da Etapa … (peso 1)" para marco de sorteio e nenhum dado do método (algoritmo, fonte, semente, substituição).
- Recomendação original: 13.7 (b) `IMPEDE` para sorteio sem método publicável e inclusão do método no documento.
- Rastro posterior: reavaliação 18/09 §5 ✅ (`032`), §3 "o documento imprime os sete dados do método".
- Specs relacionadas: 021, 026, 030 (método comum), 032 (FR-464…468).
- Implementação encontrada: impeditivo `drawn_milestone_without_method` + renderização do método e de "como a ordem nasce".
- Evidência no código atual: `editais/domain/validation.py:1752-1805` (`_metodo_do_sorteio_publicavel`, `code="drawn_milestone_without_method"` em `:1798`); `publicacoes/infrastructure/pdf.py:1238-1330` (como a ordem nasce, método que governa) e `:1402` ("Aquela ordem não vem de nota (032, FR-468)"). Testes: `tests/unit/editais/test_executabilidade.py`.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: E-7, 13.7(b); `D-G3` (a fonte externa como regra institucional — lote 4).
- Confiança: alta.

### ACH-51 — Fonte da semente em texto livre; só dois nomes exatos funcionavam
- Origem: 16/09 §5-bis.2 (S3/P1)
- Problema original: na composição a fonte era texto livre, na Retificação um `select`; qualquer variação publicava fonte inexecutável.
- Recomendação original: oferecer a lista fechada onde o valor nasce.
- Rastro posterior: reavaliação 18/09 §9 — 🟡 "continua texto livre, mas em um lugar em vez de sete"; fechado pela `035` em 19/09 (`81956f7`, "a sexta guarda").
- Specs relacionadas: 021 (FR-076), 030, 035 (FR-507/509).
- Implementação encontrada: `select` alimentado pelo vocabulário fechado nos dois lugares de composição.
- Evidência no código atual: `sorteios/infrastructure/fontes/__init__.py:83-92` (`FONTES`) e `:95-110` (`fonte_declarada` recusa `draw_source_not_supported`); `interface/forms.py:322` (`"drawMethod/source": tuple(... sorted(FONTES))`); `interface/templates/interface/compor_classificacao.html:81-88` e `_marco.html:312-317` (`<select>`). Testes: `tests/interface/test_metodo_do_marco.py`, `tests/interface/test_retificar_metodo_de_sorteio.py`.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: ACH-55 (mesma família); `D-G3`.
- Confiança: alta.

### ACH-52 — O Perfil tem vocabulário de vaga de trabalho; turma/horário não existem
- Origem: 16/09 §5-ter.1 (S2/P2); diário linha 1210; longitudinal §6 ("Perfil — D2"), §9.2, §20.2
- Problema original: para o Edital 78/2026 (turmas de Libras), criam-se dois Perfis de mesmo "público" e o horário vai à Descrição; o Perfil oferece carga horária, remuneração e atribuições, e não turma, horário, polo ou modalidade de ensino. "Não impede nada; é artificialidade de modelagem."
- Recomendação original: nenhuma mudança concreta; registrado como borda de vocabulário (§18 3-bis). Longitudinal §15: "não colocar tooltip em Perfil"; §20.4: "contextualizar Perfil pelo tipo de oferta real".
- Rastro posterior: nenhum documento posterior o retoma por ID; `AX-6` (código = par perfil × polo) é o parente normativo, lote 5. A `043` (duplicar Perfil) reduz o custo de criar Perfis irmãos, não o vocabulário.
- Specs relacionadas: 007, 024 (FR-134/135), 043.
- Implementação encontrada: nenhuma de vocabulário; os campos de vaga de trabalho somem do portal quando vazios.
- Evidência no código atual: `interface/templates/interface/_perfil.html:33-56` — campos `locality`, `workload`, `compensation` (e `duties`, `requirements`, `description`); nenhum campo de turma/horário (grep vazio por `turma`/`horário` em `editais/domain/perfis.py` e `_perfil.html`). `portal/templates/portal/selecao.html:125-138` mostra Atribuições/Carga horária/Remuneração só se preenchidos (024, FR-135) — o curso não exibe rótulo de vaga vazio.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente. O próprio achado diz que nada impede; o portal já esconde o que não se aplica e a Descrição carrega o horário. Um campo de turma/horário só se justificaria se algo a jusante precisasse **ler** o horário (conflito de turmas, filtro no portal), o que nenhum Edital da amostra exige.
- Lacuna residual: rótulo "Perfil de Vaga" e campos de trabalho num Edital de curso; sem dano funcional.
- Grupo do resíduo: C
- Impacto atual: estranhamento do elaborador de curso; nenhum erro no documento ou no portal.
- Próxima ação sugerida: nenhuma (reavaliar só se `AX-6`/polo virar eixo).
- Relações: `AX-6` (lote 5), ACH-60 (polo como eixo de trabalho), ACH-61; longitudinal §6/§9.2.
- Confiança: alta.

### ACH-53 — O portal rotula o Edital com o título do Processo (e a repartição não chega ao candidato)
- Origem: 16/09 §5-ter.1 e §5-ter.3 "Terceira e quarta ocorrências" (S2/P2)
- Problema original: a página pública do Edital de Libras e a do 28/2026 se chamavam "Seleção de Tutores a Distância", nome do Processo; num Processo que reúne objetos distintos, o portal rotula todos pelo nome do Processo. Na mesma seção: cada oferta mostra "40 vagas imediatas" e a lista de concorrências **sem as quantidades** (o candidato PcD não sabe que há 2 vagas para ele), e o total do Edital não é somado.
- Recomendação original: implícita — nomear a página pelo Edital (backlog P2, esforço P).
- Rastro posterior: nenhum documento posterior retoma. Último commit no template: `4925827` (16/09, anterior à auditoria).
- Specs relacionadas: 010, 024.
- Implementação encontrada: o cartão da vitrine mostra o título do Edital como linha secundária; a página da seleção não.
- Evidência no código atual: `portal/templates/portal/selecao.html:2` e `:23` — `<title>` e `<h1>` são `{{ processo_titulo }}`; `:24` traz "Edital N/ANO · Unidade"; o `titulo` do Edital (campo obrigatório "Título do Edital", `interface/templates/interface/compor_identificacao.html:49`) é lido em `portal/views.py:121-125` e **não é renderizado** em `selecao.html` (só em `_cartao_da_selecao.html:30`, como `chamada`, abaixo do título do Processo em `:29`). Repartição: `portal/views.py:188-190` passa só os **nomes** das Modalidades; `selecao.html:144` imprime "Concorrência: A; B; C", sem quantidades.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim. É barato e é o nome da página que o candidato lê; o Cefor publica unificados anuais, e o caso da amostra é o comum, não o raro. As quantidades por concorrência já estão no conteúdo publicado (quadro de vagas) e no PDF — levá-las ao cartão é leitura, não regra nova.
- Lacuna residual: `<h1>` da seleção com o título do Processo; título do Edital ausente da página; quantidade por Modalidade ausente do portal.
- Grupo do resíduo: B
- Impacto atual: páginas diferentes com o mesmo título no portal; candidato cotista não vê quantas vagas há na sua lista sem abrir o PDF.
- Próxima ação sugerida: corrigir (quick win no portal: `h1` = título do Edital, Processo como contexto; quantidades do quadro ao lado de cada concorrência).
- Relações: padrão "repartição não chega ao candidato" (4ª ocorrência em 16/09); longitudinal não o cita.
- Confiança: alta.

### ACH-54 — O sorteio oferece recorte à Modalidade AC declarada, que não tem vagas
- Origem: 16/09 §5-ter.1 (S2/P2)
- Problema original: a tela de sorteio oferece "Publicar e congelar a relação" para a Modalidade declarada como ampla, cujas vagas passaram à linha geral; falta dizer quantas vagas cada recorte tem.
- Recomendação original: não oferecer o recorte sem vagas; mostrar a quantidade por recorte.
- Rastro posterior: a `034` mediu a divergência (ocupação exclui, corte trata como apelido, sorteio dá recorte próprio), unificou classificação e ocupação e **deixou o sorteio de fora por decisão** (`D-004`, `FR-491a`); reavaliação 19/09 §15 item 6 "derivação de recortes do sorteio" sem posição; `035` e `036` repetem o registro fora de escopo.
- Specs relacionadas: 021 (D-006), 034 (FR-491, FR-491a, D-004), 035 (spec.md:388).
- Implementação encontrada: nenhuma no sorteio.
- Evidência no código atual: `sorteios/application/previa.py:43-50` — `listas` = "Todos os inscritos…" **mais todas** as `competitionModalities`, sem excluir `generalCompetitionModalityId`; `previa.py:168-203` (`_recorte`) não carrega quantidade de vagas; `interface/templates/interface/sorteio.html` não menciona "vaga" (grep vazio). Contraste: `editais/domain/recortes.py:33-60` exclui a AC declarada; o docstring em `:20-23` registra a divergência.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, e ficou mais nítido: hoje a mesma AC declarada é **recorte** no sorteio e **apelido da linha geral** na ocupação. Um sorteio feito nesse recorte produz ordem que a apuração não consome. O custo que travou a correção (atos históricos por lista da `021`) é real, mas mostrar a quantidade de vagas por recorte e avisar "este recorte não tem linha no quadro" é barato e não mexe em ato nenhum.
- Lacuna residual: derivação de recortes do sorteio divergente da ocupação; ausência de vagas por recorte na tela do sorteio.
- Grupo do resíduo: B
- Impacto atual: presidência pode congelar/sortear num recorte que não alimenta ocupação nem convocação, sem aviso; confusão entre "Todos os inscritos" e "Ampla (linha geral)".
- Próxima ação sugerida: criar spec (curta: vagas por recorte + aviso; a retirada do recorte excedente com preservação dos atos históricos é a parte grande).
- Relações: ACH-47 (metade computada, fechada); memória "ampla concorrência tem duas grafias"; `D-G5`.
- Confiança: alta — código lido; comportamento de tela inferido do template, não percorrido.

### ACH-55 — O método do sorteio pedia prosa e precisava de dado; a mensagem culpava a fonte
- Origem: 16/09 §5-ter.1 (S3/P1); diário linha 1210
- Problema original: `Ocorrência` e `Derivação` em prosa; sem referência derivável não havia "Observar a ocorrência" e a tela dizia que a fonte estava indisponível e prescrevia Retificação; nada validava na composição.
- Recomendação original: 13.7 — validar executabilidade do método antes de publicar e não atribuir a falha à fonte.
- Rastro posterior: reavaliação 18/09 §9 🔴; §13 (19/09) — `035` implementada, `SC-176` do congelamento à verificação pública.
- Specs relacionadas: 021, 035 (FR-507, FR-509, FR-515, FR-516).
- Implementação encontrada: a composição aplica a própria regra de derivação à referência; a tela distingue "espere a fonte" de "corrija a declaração"; ajuda de campo "Só a referência, terminando no número".
- Evidência no código atual: `sorteios/domain/substituicao.py:113-136` — `derivavel` (FR-515) aplica a regra publicada; `editais/domain/perfis.py:617` a consome na validação; `sorteios/application/previa.py:60-64` — `recusa_da_ocorrencia` com duas razões (FR-516); `interface/templates/interface/compor_classificacao.html:89-103` (placeholder `5900` e ajuda). Testes: `tests/unit/sorteios/test_forma_da_ocorrencia.py`, `tests/integration/sorteios/test_ocorrencia_declarada.py`, `tests/interface/test_recusa_do_sorteio.py`.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não. `Como a ocorrência decorre da data programada` continua texto livre, mas é prosa publicada, não insumo de cálculo.
- Lacuna residual: nenhuma do achado. A prática real (10 de 10 Editais sem ocorrência externa) é `D-G3`, lote 4.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: ACH-51; E-7; `D-G3`.
- Confiança: alta.

### ACH-56 — Barema não é representável (e autopontuação não tem onde ser declarada)
- Origem: 16/09 §5-ter.2 (S2/P2, "revalidado"); diário linha 1486; longitudinal preâmbulo item 3
- Problema original: a Etapa tem 11 campos e nenhum de critério/item/limite; a Mesa tem um campo de nota; o barema do 14/2026 só cabe como anexo PDF e a banca lança a soma.
- Recomendação original: nenhuma nova — o auditor aponta as pendências já registradas "barema (D-4)" e "autopontuação (P-7)".
- Rastro posterior: longitudinal 21/09 item 3: "zero ocorrências de `barema` no código de produto".
- Specs relacionadas: 012 §21 (barema recusado como "spec própria"), 015 (D-4).
- Implementação encontrada: nenhuma.
- Evidência no código atual: `grep -ril barema backend/processo_seletivo` → 0 arquivos; `grep -ril autopontua` → 0. Decisão: `doc/decisoes-pre-vertical.md:133-147` — "D-4 · Barema fica fora do primeiro vertical", apuração externa, custo escrito ("o sistema não demonstra que o total está certo").
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente. D-4 **adia**, não recusa, e registra o custo com honestidade. Barema serve a uma família (14/2026, 173/2025) e é spec inteira (critérios, limites, autopontuação vinculante). Com equipe de 2–3 pessoas e a amostra dominada por sorteio, não é o próximo passo; continua sendo a borda que impede o sistema de conferir a nota de Editais pontuados por títulos.
- Lacuna residual: nota por item, limite por item, autopontuação.
- Grupo do resíduo: B
- Impacto atual: nos Editais de prova de títulos, a conferência do cálculo continua fora do sistema; o recurso contra a nota só pode ser instruído com o PDF.
- Próxima ação sugerida: nenhuma agora; criar spec quando a família de prova de títulos entrar no alvo.
- Relações: D-4, P-7 (lote 1), `AX` do barema (auditoria de granularidade 15/09, lote 5: "Ficha de avaliação (barema) … não existe").
- Confiança: alta.

### ACH-59 — Grupo de prioridade em cascata não é Modalidade, e os avisos empurram para repartir o que o Edital não reparte
- Origem: 16/09 §5-ter.2 (S3/P2); diário linha 1460; longitudinal preâmbulo item 3
- Problema original: no 14/2026 os grupos 1→2→3 são ordem de chamada ("até 10 por código"), não reserva; modelados como Modalidades, os avisos do quadro cobram repartição e as três saídas afirmam algo falso.
- Recomendação original: nenhuma nova — pendência "cascata Grupo 1→2→3 (016/019)" já registrada.
- Rastro posterior: `doc/decisao-encadeamento-l1-e-o-arco-operacional.md:55-60` classifica o 14/2026 como "cascata de chamada, não vaga reservada … o que ele precisa é de regra de ordem de chamada — `callRules`".
- Specs relacionadas: 016, 019, 025, 027.
- Implementação encontrada: nenhuma. `callRules` existe só como regra de convocação **dentro** de uma Modalidade (`interface/retificacao.py:1104`, "Regras de convocação da reserva"), não entre grupos; `vacancyReversion` tem `ON_EXHAUSTION`/`ON_BALANCE` (`_perfil.html:219-221`), reversão de reservada para geral.
- Evidência no código atual: `editais/domain/validation.py:2480` — o aviso "Sem linha no quadro: … a ocupação e a convocação não terão quantidade a apurar" continua disparando para Modalidade sem linha; nenhum conceito de prioridade entre listas (grep por `cascata` só encontra usos não relacionados em `ocupacao`, `pdf.py`, `comissoes`).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, mas como evolução de modelo: é uma das onze famílias da amostra e a decisão do encadeamento já nomeou a forma (`callRules`). Um paliativo barato — o aviso dizer que Modalidade sem linha é legítima quando a lista é só de prioridade — seria texto que afirma norma; melhor não.
- Lacuna residual: prioridade de chamada entre listas sem quantidade reservada.
- Grupo do resíduo: B
- Impacto atual: o 14/2026 não se compõe sem declarar algo falso; ocupação/convocação da cascata ficam fora do sistema.
- Próxima ação sugerida: criar spec (quando a família entrar no alvo), partindo de `decisao-encadeamento-l1…:55-60`.
- Relações: L-/P- da avaliação de capacidade (lote 1); ACH-56 (mesmo Edital).
- Confiança: alta.

### ACH-60 — A organização do trabalho não conhece o Perfil/polo/modalidade
- Origem: 16/09 §5-ter.3 (S3/P1); diário linha 1531; longitudinal §7 (presidência), §8 ("organizar comissão por polo — E4"), §9.6, §10 fricção 3, §12 "Escopo de trabalho por recorte", §14.3, §19 (P1)
- Problema original: alocação é matriz Etapa × avaliador; distribuição filtra só por cobertura e avaliador, sem coluna de Perfil; num Edital de 7 polos cada comissão local recebe inscrições dos sete; CLVA/CPVA sem representação (comissão única por Processo).
- Recomendação original: longitudinal §14.3 — escopo opcional de alocação/distribuição por Perfil ou lista, com negar-por-padrão e contraprova entre recortes.
- Rastro posterior: reavaliação 18/09 §9 🔴 "intocado" e §14-ter "`ACH-60` (P1)"; convergência 20/09 §4/§10 "ABERTO … zero ocorrências em `distribuicao.html`" e §16 "pergunta aberta, não decidida"; §19/§21 "não abstrair polo antes de ter o Edital real de múltiplos polos na mão".
- Specs relacionadas: 011 (comissão/alocação), 012 (distribuição), 040–042 (visão institucional — **não** tocam organização do trabalho), 043.
- Implementação encontrada: nenhuma. As `040`–`042` agregam **demanda** por Perfil na Visão Geral (`interface/visao_geral.py`), não trabalho.
- Evidência no código atual: `comissoes/models.py:76-83` — `AlocacaoEtapa(membro, edital, etapa_id)`, sem Perfil; `interface/templates/interface/distribuicao.html:292` (`cobertura`) e `:306` (`avaliador`) são os únicos filtros; cabeçalhos `:332-346` (Inscrição, Participante, Atribuídas, Concluídas, Prontidão, Quem avalia) sem Perfil; `grep -i "perfil|polo|modalidade|profile"` em `distribuicao.html` e `alocacoes.html` → vazio. Últimos commits nesses templates: `d9d47ed` (030) e `dcc4e45` (036), nenhum sobre recorte.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente. Uma **coluna e um filtro de Perfil** na distribuição são leitura de dado já presente (`Inscricao.profile_id`) e não mexem em autorização — isso eu recomendaria hoje sem hesitar. O **escopo de trabalho por Perfil** (comissão local só enxerga seu polo) é mudança de autorização com risco de vazamento horizontal, e a convergência pede Edital real multipolo antes; a equipe inicial de 2–3 pessoas (memória do projeto) reduz a urgência de comissões locais separadas.
- Lacuna residual: (1) sem coluna/filtro de Perfil na distribuição e na alocação; (2) sem escopo de trabalho por Perfil; (3) sem CLVA/CPVA (heteroidentificação — ver L-2/lote 1).
- Grupo do resíduo: B
- Impacto atual: presidência distribui inscrições de vários polos sem ver de qual polo cada uma é; 7 polos → a comissão inteira alcança todos.
- Próxima ação sugerida: corrigir a parte (1) (quick win de leitura); decisão de governança para (2) antes de spec.
- Relações: `AX-6` (lote 5), `doc/achado-atribuicoes-repetidas-por-polo.md` (lote 7), heteroidentificação (longitudinal item 2, L-2), convergência §16.
- Confiança: alta.

### ACH-61 — Escala da composição: 7 polos = ~19 mil px, 399 controles; método do sorteio declarado 7 vezes
- Origem: 16/09 §5-ter.3 (S2/P2); diário linha 1552
- Problema original: etapa de Perfis com 7 polos × 3 modalidades media 18.943 px, 399 controles e 14 avisos simultâneos; o método do sorteio morava no marco e era declarado sete vezes (98 campos), com risco de divergência.
- Recomendação original: implícita — declarar o método uma vez; reduzir densidade.
- Rastro posterior: reavaliação 18/09 §4.3 — parcial pela `030` (método comum por Edital, 98 → 9 campos); "a etapa de Perfis com 7 polos … intocada". A `043` (duplicar Perfil, `0479f4e`) entrou em 25/09. O estudo de esforço de 21/09 mediu a composição (lote 6).
- Specs relacionadas: 030 (FR-429/430), 043.
- Implementação encontrada: método comum no Edital; "Duplicar este Perfil" copia o Perfil inteiro com Modalidades e marcos, pedindo só Código e Localidade.
- Evidência no código atual: `interface/templates/interface/compor_classificacao.html:60-140` (bloco "Método do sorteio comum a este Edital"); `editais/domain/duplicacao.py:1-15` e `interface/templates/interface/_duplicar_perfil.html`; `compor_perfis.html:93` renderiza **todos** os `_perfil.html` expandidos (0 `<details>` em `_perfil.html`; 18 controles por Perfil + 7 por Modalidade em `_modalidade.html`).
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: parcialmente. O custo de **autoria** caiu duas vezes (método único; duplicação). A densidade da página não caiu, e a duplicação cria sete cópias independentes das mesmas Modalidades — o mesmo risco de divergência que o achado apontava no método, agora no quadro/modalidades. Recolher os cartões de Perfil é polish; o risco de integridade é o que interessa, e já tem dono no achado avulso das atribuições repetidas por polo.
- Lacuna residual: página longa com todos os Perfis abertos; repetição por Perfil de conteúdo que o Edital declara uma vez.
- Grupo do resíduo: C
- Impacto atual: rolagem longa em Editais multipolo; divergência possível entre cópias.
- Próxima ação sugerida: nenhuma isolada; tratar junto de `AX-6`/atribuições repetidas se aquela decisão for tomada.
- Relações: ACH-60, `AX-6`, `doc/achado-atribuicoes-repetidas-por-polo.md`, estudo de esforço §5.x (lote 6).
- Confiança: média-alta — densidade inferida do template, não medida no DOM.

---

## Parte B — Top 10 de 16/09 (§6): os itens com atenção especial do lote

### ACH-40 — Quem pode publicar o resultado não tinha caminho até a ação
- Origem: 16/09 §6 item 2 (S3/P0), §13.3
- Problema original: o Publicador puro (`resultado:publicar`, sem vínculo de comissão) não via o bloco Classificação; a tela de divulgação abria por URL, mas a navegação não a oferecia.
- Recomendação original: listar marcos e atos a quem tem `resultado:publicar`, com a ação de divulgar.
- Rastro posterior: reavaliação 18/09 §6 ✅ pela `033`; convergência 20/09 §4 "Navegação por capacidade — FECHADO [MEDIDO]".
- Specs relacionadas: 033 (FR-473, FR-476).
- Implementação encontrada: derivação por destino, e não por porta.
- Evidência no código atual: `interface/views.py:2887-2940` (`_marcos_publicados`; `pode_divulgar = ator.can("resultado:publicar")`) e `:2822-2884` (`_destinos_do_marco`, "divulgar o resultado" para cada ato vigente); `interface/templates/interface/detalhe.html:147-165` só apresenta o que a view derivou. Teste: `tests/interface/test_destinos_do_edital.py`.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: E-2, 13.3; `N-03` (convergência, regressão análoga no painel — fechada por `4ec1cbb`, 20/09).
- Confiança: alta.

### ACH-41 — Duas datas-limite contraditórias para o mesmo recurso
- Origem: 16/09 §6 item 5 (S3/P1), §11 E-4, §13.5; longitudinal §9.1 e §10 fricção 2
- Problema original: o acompanhamento mostra "Cabe recurso … até 18/09" (janela do marco) e o Cronograma "Prazo para interposição de recursos 06/10–07/10"; nada confronta as duas fontes.
- Recomendação original: validação que confronte janela recursal × Evento de recurso e AVISO na publicação do resultado. §14: "não resolver obrigando o Cronograma a ter Evento de recurso".
- Rastro posterior: reavaliação §9/§10 🔴 intocado; longitudinal §14.2 acrescenta a mitigação decisiva: "validar somente relações semânticas já declaradas pelo modelo; **não casar eventos por texto livre**"; convergência 20/09 §4 E-4 ABERTO.
- Specs relacionadas: 018 (degrau 8, FR-020…029), 026 (US3).
- Implementação encontrada: nenhuma validação cruzada. A única conferência da janela é de forma (computável), não de coerência com o Cronograma.
- Evidência no código atual: `recursos/domain/janela.py:1-18` — a janela é **relativa** à publicação que divulgou o ato ("a âncora é o ato, e não uma data absoluta"); `editais/domain/validation.py:1497-1532` (`_coerencia_da_janela_recursal`) só verifica que é computável; `interface/templates/interface/_evento.html:19-20` — o **tipo** do Evento é `input type="text"` livre, sem vínculo com marco; `portal/templates/portal/acompanhamento.html:160` imprime o prazo computado ao lado do Cronograma.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente. A recomendação original **não é executável como escrita**: não existe relação declarada entre um Evento do Cronograma e um marco (tipo é texto livre), e a janela só vira data no instante da publicação do resultado. Casar por texto é justamente o que o longitudinal §14.2 proíbe. O que continua valendo: (a) na **prévia de divulgação** do resultado, dizer a data-limite que aquele ato abrirá, para quem publica comparar com o Cronograma; (b) se um dia o Evento ganhar vínculo tipado com o marco, aí sim confrontar.
- Lacuna residual: a contradição continua possível e silenciosa; o candidato vê as duas datas.
- Grupo do resíduo: B
- Impacto atual: risco de candidato perder prazo confiando no Cronograma publicado; ocorre quando a divulgação se desloca do planejado — caso comum.
- Próxima ação sugerida: criar spec pequena para (a); (b) depende de decisão de modelo (lote 5, E-4).
- Relações: E-4 (raiz, lote 5), ACH-13/ACH-18 (lote 2), `N-05`/`N-06` (mesma família, lote 6), NOVO-1 abaixo.
- Confiança: alta quanto ao estado; média quanto ao desenho da saída.

### ACH-42 — O parecer não chegava ao candidato
- Origem: 16/09 §6 item 4 (S3/P1), §13.2
- Problema original: o acompanhamento do eliminado mostrava "30,0000 < 40,0000" e nunca o parecer, embora a `012` justificasse o parecer obrigatório pela necessidade do candidato de recorrer.
- Recomendação original: exibir o parecer ao titular quando o resultado lhe for desfavorável e houver prazo recursal.
- Rastro posterior: reavaliação §14 (19/09) — fechado pela `036`; convergência 20/09 §4 "Parecer do candidato — FECHADO [MEDIDO]".
- Specs relacionadas: 012 (spec.md:369), 036 (FR-522, FR-524, FR-525a, D-001).
- Implementação encontrada: parecer do titular, só no desfavorável, enquanto houver prazo aberto ou peça dele em curso contra aquele resultado; a tela explica quando ele sai.
- Evidência no código atual: `recursos/application/selectors.py:617-700` (`pareceres_do_titular`, recorte exatamente o da recomendação, com a peça inadmitida excluída); `portal/views.py:1390-1405` (`parecer_por_resultado`); `portal/templates/portal/acompanhamento.html:60-70` (parecer de terceiro continua proibido) e `:90-97`. Teste: `tests/portal/test_parecer_do_titular.py`.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: ACH-43, 13.2.
- Confiança: alta.

### ACH-43 — O julgador decidia sem poder ver a prova (e: o recorrente anexa prova?)
- Origem: 16/09 §6 item 3 (S3/P0), §13.2, §14 ("não conceder documentos ao papel `recurso:julgar`")
- Problema original: pela FR-105 da `018`, julgar não concede acesso a documentos; o julgador fixava nota sem ver o documento citado na razão do recurso.
- Recomendação original: **ato de instrução** com escopo por recurso — a presidência anexa parecer e documento citado, auditado, visível só naquele recurso.
- Rastro posterior: reavaliação §14 (19/09) — `036` fechou "o último P0"; longitudinal §7 "Julgador … agora recebe exatamente o que foi instruído"; convergência 20/09 §4 registra "Recurso sem prova — ABERTO: a tela `/selecoes/.../recorrer` tem um `select` e um `textarea`, nenhum campo de anexo" — que é **outra pergunta** (prova do recorrente, não do julgador).
- Specs relacionadas: 018 (FR-102, FR-105, FR-007, D-011), 036 (FR-527…531a, FR-537).
- Implementação encontrada: `AtoDeInstrucao` append-only (parecer ou documento por referência), alcance derivado do recurso e fechado pela decisão.
- Evidência no código atual: `recursos/models.py:314-416` (espécies `PARECER`/`DOCUMENTO`, FK ao `DocumentoSubmetido` original, sem cópia, sem lista de quem vê); `recursos/application/instruir.py:191`; `interface/urls.py:413` e `interface/views.py:7765` (`instruir_recurso`); `interface/templates/interface/recurso.html:164` ("Anexar o documento — {{ documento.nome_original }}"). Testes: `tests/interface/test_instrucao_na_peca.py`, `tests/integration/recursos/test_alcance_da_instrucao.py`, `tests/integration/recursos/test_trilha_da_instrucao.py`. Recorrente: `portal/templates/portal/recorrer.html:36` (`select` objeto) e `:54` (`textarea`) — sem `type="file"`; `specs/018-recursos-e-superacao-de-resultados/spec.md:896` — "**FR-007**: A interposição MUST NOT aceitar anexos na V1 (D-011)", com a razão em `:446-448` e `:519-521` ("admitir prova nova em recurso é questão normativa que nenhum Edital lido declarou").
- Estado atual: RESOLVIDO (o achado de 16/09). A leitura da convergência — "recorrente sem campo de anexo" — é CONTRADITO POR DECISÃO: `D-011`/`FR-007` da `018`.
- Ainda faz sentido?: não para o julgador. Para o recorrente, só se a instituição decidir admitir prova nova em recurso — é pergunta normativa, não lacuna de UX. A prova que o recurso do cenário cita ("o currículo, página 2") já é documento da inscrição e é alcançável pela instrução.
- Lacuna residual: nenhuma do achado.
- Grupo do resíduo: —
- Impacto atual: nenhum; o caso de juntada de documento novo segue fora do sistema por decisão.
- Próxima ação sugerida: nenhuma; se a governança quiser revisitar `D-011`, é decisão, não correção.
- Relações: ACH-42, 13.2, E-2; convergência §4 "Recurso sem prova" (lote 6).
- Confiança: alta.

### ACH-02/30/38 · ACH-35 · ACH-39/31/45 · ACH-08 · ACH-10/16 — demais itens do top 10 (session 1; verificação pontual)
- Origem: 16/09 §6 itens 6–10, §12 quick wins 1–4 e 9 — achados da **primeira sessão** (cenários 1–2), que cabem ao lote 2; aqui só a conferência pontual porque aparecem no top 10 e nas raízes.
- Rastro posterior e evidência pontual:
  - **ACH-38** (presidência mandada divulgar) — ✅ `033` (reavaliação §6). **ACH-02**, **ACH-30** — ✅ `037` (reavaliação §14; percurso com `ana.gestora`).
  - **ACH-35** (404 mudo de vínculo) — ✅ nas portas pela `033` (`require_authorization_base`); **sete recusas fora das portas** continuam: `interface/views.py:384-403` (`criar_edital`) ainda faz `raise Http404` com o comentário "distinguir 'não existe' de 'você não pode'…"; `D-G2` (19/09) mandou `criar_edital`, `reaproveitar`, `supervisao` para 403 — não executada (lote 4).
  - **ACH-39/31/45** (UUID nas telas de ato) — parcial; ver E-3 abaixo: `interface/templates/interface/ato_ordenacao.html:77-78` ainda tem quatro colunas de UUID em "Resultados que entraram na ordem" (inalterado desde `432112c3`, 06/09); `:91` já mostra "protocolo — nome" na ordem.
  - **ACH-08** — ✅ `037`: `editais/domain/calendario.py:18-40` (`vencido`: com término vence pelo término). Deslocado para o painel como `N-06` (lote 6).
  - **ACH-10** — ✅ `030` (reavaliação §4.1: 28 → 17 controles, 7 → 2 perguntas). **ACH-16** — ✅ `037`: `interface/templates/interface/_etapa.html:146` "Peso (opcional até um marco enumerar esta Etapa)"; `D-G4` encerrou a questão.
- Estado atual: DUPLICADO / ABSORVIDO — pertencem ao lote 2 (UX 16/09 cenários 1–2); estados acima conferidos pontualmente.
- Grupo do resíduo: — (os resíduos são `D-G2` e E-3, tratados nos blocos próprios)
- Confiança: alta nas checagens pontuais; não refeitas em profundidade.

---

## Parte C — Raízes estruturais E-1…E-7 (16/09 §11) e melhorias §13.x

### E-1 · 13.1 — A cauda do processo não fecha
- Origem: 16/09 §11 E-1, §13.1; §18 "cinco mudanças" item 2
- Problema original: convocação e suplência dependiam de uma cadeia (corte → geração → faixa) cujo primeiro elo era opcional e invisível; reserva e sorteio sem execução.
- Recomendação original: 13.1 (a)(b)(c); e fechar reserva e sorteio.
- Rastro posterior: reavaliação §10 — parcial em 18/09; ✅ em 19/09 após `034`+`035` (`SC-169`, `SC-170`, `SC-176` percorridos); §14 "os seis P0 fecharam"; convergência 20/09 §17 "E-1 ✅ percorrida hoje".
- Specs relacionadas: 014, 016, 019, 032, 034, 035, 037.
- Implementação encontrada: ver ACH-46, ACH-47, ACH-55.
- Evidência no código atual: `classificacao/application/emissao.py:20-47` (ordem por recorte); `interface/views.py:2855-2868` (corte sempre oferecido); `sorteios/domain/substituicao.py:113-136` (referência derivável conferida na composição).
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não como raiz. Bordas que ainda não fecham a cauda são de **modelo**, não da cadeia: cascata de grupos (ACH-59) e barema (ACH-56).
- Lacuna residual: nenhuma da raiz; `D-G1` (aviso → impedimento) segue com o lote 4.
- Grupo do resíduo: —
- Impacto atual: nenhum para as três famílias percorridas.
- Próxima ação sugerida: nenhuma.
- Relações: ACH-46, ACH-47, ACH-51, ACH-55; `D-G1`.
- Confiança: alta (código); o percurso é herdado da reavaliação e da convergência, não refeito.

### E-2 · 13.3 — Autorização e navegação discordam
- Origem: 16/09 §11 E-2, §13.3
- Problema original: navegação montada por um eixo (vínculo) e permissões pelo outro (papel); o Publicador não chegava à ação; negativa por vínculo em 404 mudo.
- Recomendação original: navegação derivada da permissão; recusa nomeada para vínculo; 404 só para outro escopo.
- Rastro posterior: reavaliação §6/§10 — ✅ "com ressalva" (`033`); §8 — **sete recusas fora das portas** medidas e deixadas de fora por decisão; `D-G2` (19/09) deu a fronteira 403/404; convergência 20/09 §17 "⚠️ reaberta em um ponto" (`N-03`), fechado por `4ec1cbb` (20/09); `N-04` (painel sem "a quem pedir") aberto.
- Specs relacionadas: 022, 033 (FR-473, FR-476, inventário das negativas), 037, 038.
- Implementação encontrada: `require_authorization_base`; derivação por destino; detector que reprova `raise Http404` fora do inventário.
- Evidência no código atual: `interface/views.py:2887-2940` (derivação por destino); `interface/views.py:384-403` (`criar_edital` ainda `raise Http404` — `D-G2` não executada); `interface/templates/interface/processo_detalhe.html` com a guarda de `4ec1cbb` (commit lido).
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: sim para o resíduo, e ele já tem dono: `D-G2` (três recusas que devem virar 403) e `N-04` (painel sem capacidade a pedir).
- Lacuna residual: `criar_edital`, `reaproveitar`, `supervisao` em 404; sinais do painel sem "peça a alguém".
- Grupo do resíduo: B
- Impacto atual: operador que tenta criar Edital/reaproveitar sem capacidade lê "não encontrado".
- Próxima ação sugerida: nenhuma aqui — executar `D-G2` (lote 4) e `N-04` (lote 6).
- Relações: ACH-35, ACH-38, ACH-40; `D-G2`; `N-03`, `N-04`.
- Confiança: alta.

### E-3 · 13.4 — Duas gramáticas para o mesmo fato normativo (preâmbulo longitudinal item 5)
- Origem: 16/09 §11 E-3, §13.4; longitudinal §10 fricção 7, §12, §13 quick win 7; preâmbulo 21/09 item 5 ("o conserto é **uma tabela**, não um renderizador")
- Problema original: o público lia "ALTERADO — Evento do cronograma… — Término"; a gestão lia `/schedule/id=…/endAt`, `REPLACE`, colunas de UUID.
- Recomendação original: 13.4 — reaproveitar o renderizador público nas telas de ato, com o identificador ao lado. Revisão de 21/09: não se aplica (a gestão precisa do antes/depois, que o portal recusa por `D-009`); unificar a **tabela de vocabulário**.
- Rastro posterior: reavaliação §10/§14 🔴 "intocado"; §15 "O que eu não faria agora: E-3"; convergência §17 🔴 "[NÃO REAUDITADO a fundo]", `N-09` (S1: `cand:…` e UUIDs na tela do recurso); `7b04cb3` (25/09) levou à Revisão o vocabulário da Retificação.
- Specs relacionadas: 024 (FR-130, D-005, D-009), 004.
- Implementação encontrada: na gestão, tradução por uma única fonte (`retificacao_ui`): `_onde_e_campo` para Retificação e, desde 25/09, `nomes_dos_caminhos`/`mensagem_legivel` para as pendências da Revisão. No portal, tabela própria.
- Evidência no código atual: `interface/views.py:3387-3408` (`CAMPO_EM_PORTUGUES` derivado de `retificacao_ui.CAMPOS_*`; `COLECAO_EM_PORTUGUES`); `interface/views.py:727-775` (`nomes_dos_caminhos` lê `retificacao_ui.campos_editaveis` — "o vocabulário é o da Retificação, e não um segundo"); `publicacoes/domain/alteracoes.py:24-52` (`OPERACOES`, `COLECOES`, `CAMPOS` do portal). **Já divergem**: gestão "Modalidade" × portal "Modalidade de concorrência"; "Marco classificatório" × "Marco de classificação"; "Etapa de avaliação" × "Etapa"; "Seção do texto" × "Seção". Telas de ato: `ato_ordenacao.html:7` (`Ato {{ ato.id }}` na trilha), `:77-78` (quatro colunas de UUID, inalteradas desde 06/09); `recurso.html:27,35,37` (`interposto_por`, `ato_vigente.id`, `versao.id` crus).
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: parcialmente. O caminho cru sumiu das telas onde se decide (Retificação, Revisão). O que sobra é (1) **duas tabelas** que já nomeiam a mesma coleção de jeitos diferentes — barato unificar, e a deriva é silenciosa; (2) tabelas de proveniência com UUID sem nome ao lado, onde o UUID é auditabilidade (16/09 §14 pede manter) — falta só a coluna legível.
- Lacuna residual: duas tabelas de vocabulário (gestão × portal); UUIDs sem rótulo em `ato_ordenacao.html:77-78` e na proveniência do recurso.
- Grupo do resíduo: C
- Impacto atual: baixo — nomes ligeiramente diferentes entre gestão e portal; tela do ato pouco legível para quem assina.
- Próxima ação sugerida: corrigir quando se tocar nessas telas (unificar a tabela; coluna com nome ao lado do UUID).
- Relações: ACH-31, ACH-39, ACH-45 (lote 2), `N-09` (lote 6); irmã de E-4 (reavaliação §14-ter).
- Confiança: alta.

### E-4 · 13.5 — Fontes normativas que ninguém confronta
- Origem: 16/09 §11 E-4, §13.5; longitudinal §10 fricção 2, §12, §14.2, §19 (P1)
- Problema original: janela recursal × Evento de recurso; término de inscrições × designação; numeração de seção tela × documento.
- Recomendação original: família de verificações cruzadas na "Validação do conteúdo".
- Rastro posterior: reavaliação §10/§14/§14-ter 🔴; convergência §4/§17 🔴, com forma nova (`N-05`, `N-06`: campo declarado derivado que nada deriva); `AX-7` (duas linhas citando a mesma lei com percentuais diferentes) — lote 5.
- Specs relacionadas: 026, 032.
- Implementação encontrada: confronto **dentro** da fonte (quadro × percentual normativo), não entre fontes.
- Evidência no código atual: ver ACH-41 (`recursos/domain/janela.py:1-18`; `_evento.html:19-20` tipo livre; `validation.py:1497-1532`). Nova instância, NOVO-1 abaixo (`reserveLimit` publicado × `cutRule` que governa a suplência).
- Estado atual: NÃO IMPLEMENTADO — raiz do lote 5; aqui só a checagem pontual e a relação com ACH-41.
- Ainda faz sentido?: sim, com a condição do longitudinal §14.2: só onde o modelo **declara** a relação. Várias instâncias não têm relação declarada (Evento de tipo livre), e aí o remédio é modelar o vínculo ou mostrar as duas fontes lado a lado no ato — não inferir.
- Lacuna residual: nenhuma verificação cruzada.
- Grupo do resíduo: B
- Impacto atual: contradições publicáveis em ato imutável.
- Próxima ação sugerida: validar no lote 5 (E-4/AX) antes de spec.
- Relações: ACH-41, ACH-13, ACH-18 (lote 2), `AX-7`, `N-05`, `N-06`, NOVO-1.
- Confiança: média — não refeita em profundidade (lote 5).

### E-5 — A explicação desgrudou do campo
- Origem: 16/09 §11 E-5
- Problema original: o bloco "Como preencher" coletivo, distante e anterior aos campos.
- Recomendação original: aproximar a explicação sem desfazer a regra de ajuda fora dos cartões (§14).
- Rastro posterior: reavaliação §4.2/§10 ✅ `030` ("as 8 âncoras resolvem para os campos certos"); convergência §17 ✅.
- Specs relacionadas: 030.
- Implementação encontrada: `como-preencher` por etapa, recolhido, com âncoras.
- Evidência no código atual: `interface/templates/interface/compor_perfis.html:23-90` (`<details class="como-preencher">`, com o comentário da decisão); `interface/templates/interface/compor_classificacao.html` idem.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: ACH-04 (lote 2); memória "ajuda visível é proibida nos cartões".
- Confiança: alta (pontual).

### E-6 · 13.6 — A visão global some quando o Processo fica vivo
- Origem: 16/09 §11 E-6, §13.6; longitudinal §1 (visão global 5), §10 fricção 1, §14.1, §19 (P1), §21 item 1
- Problema original: "O que fazer agora" reduz-se a Encerrar/Cancelar depois da publicação.
- Recomendação original: manter o guia ligado depois da publicação, derivando da mesma consulta das telas de destino; não fazer dashboard separado.
- Rastro posterior: `038` (19/09) construiu o painel; convergência 20/09 §4/§6 "PARCIAL" — nota 6, não 8; `N-01`…`N-08`; `4ec1cbb` (20/09) fechou `N-03`.
- Specs relacionadas: 022, 038.
- Implementação encontrada: Pulso e sinais no Processo e na Supervisão, lendo o mesmo módulo.
- Evidência no código atual: `interface/supervisao.py:1130-1170` — `sinais_do_recurso` consulta só `AGUARDANDO_JULGAMENTO` (`:1165`), de modo que o recurso aguardando admissibilidade continua sem sinal (`N-02`); `interface/templates/interface/processo_detalhe.html:140` — "Nenhuma condição de atenção neste Processo." (`N-01`); `git log` de `supervisao.py`/`processo_detalhe.html`: nada depois de `4ec1cbb`.
- Estado atual: DUPLICADO / ABSORVIDO — em `N-01`, `N-02`, `N-04`…`N-08` (convergência de 20/09, lote 6). A raiz saiu do estado "intocado" para "parcial".
- Ainda faz sentido?: sim, pelos N-IDs; não criar outro painel (convergência §20).
- Lacuna residual: a dos N-IDs.
- Grupo do resíduo: B (pelos N-IDs, a confirmar no lote 6)
- Impacto atual: ver lote 6.
- Próxima ação sugerida: nenhuma aqui.
- Relações: ACH-25, ACH-27 (lote 2); `N-01`…`N-08`.
- Confiança: alta quanto ao absorvimento; não refiz a medição do painel.

### E-7 · 13.7 — A validação não pergunta se o Edital é executável
- Origem: 16/09 §11 E-7, §13.7; §18 "cinco mudanças" item 1
- Problema original: `IMPEDE` cobria "ao menos um Perfil/Evento" e nada do que faz o certame funcionar (ACH-49, ACH-50, ACH-47, ACH-46).
- Recomendação original: família de verificações de executabilidade: (a) Perfil sem marco; (b) sorteio sem método publicado; (c) reserva sem via de apuração; (d) aviso de marco sem corte.
- Rastro posterior: reavaliação §5/§10 ✅ (`032`), com `ACH-47` fechado depois pela `034`; convergência §17 ✅. Depois de 20/09 a família continuou crescendo: `01d9163` (25/09) acrescentou `IMPEDE` para documento de "todos os Perfis" restrito à Modalidade de um só; `643e865` (25/09) corrigiu cópia que levava `governedStage` do Edital anterior (a publicação acusava; o rascunho não). E o preâmbulo longitudinal item 1 (`doc/achado-duas-avaliacoes-sem-regra-de-combinacao.md`) é exatamente uma instância não coberta desta raiz.
- Specs relacionadas: 032 (FR-457…468), 034.
- Implementação encontrada: (a) e (b) impeditivos; (c) tornou-se desnecessária pela `034`; (d) aviso.
- Evidência no código atual: `editais/domain/validation.py:1660-1805`; `:2226` (`_recorte_que_o_documento_publicado_alarga`, de `01d9163`); `editais/domain/reaproveitamento.py:173-180` (troca de `governedStage`, de `643e865`). Instância aberta: `editais/domain/validation.py:234` — `evaluationsPerRegistration` só com `minimo=1`, nada na publicação; `resultados/domain/regra.py:71-76` — a consolidação recusa a Etapa inteira ("o Edital prevê N avaliações … e não declara como combiná-las").
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: sim. As quatro evidências de 16/09 fecharam; a classe não: ainda se publica, em ato imutável, Etapa com duas avaliações que nunca consolida.
- Lacuna residual: Etapa com `evaluationsPerRegistration > 1` publicável sem regra de combinação (lote 7); `D-G1` (lote 4).
- Grupo do resíduo: A (a instância das duas avaliações publica um ato que não se executa — mesma natureza que fez ACH-49/50 serem S4)
- Impacto atual: Edital publicado com Etapa que não consolida; saída só por Retificação.
- Próxima ação sugerida: corrigir — pela via do achado avulso (lote 7).
- Relações: ACH-46…ACH-50; `doc/achado-duas-avaliacoes-sem-regra-de-combinacao.md`; `D-G1`.
- Confiança: alta.

---

## Parte D — Reavaliação de 18–19/09: o que ela abriu e não é raiz nem ACH

### REAV-§8 — Sete recusas fora das portas continuam em 404 uniforme
- Origem: reavaliação-ux-2026-09-18 §8 (18/09); longitudinal §10 fricção 6, §13 quick win 6, §19 (P1)
- Problema original: a `033` inventariou 11 recusas de autorização em `views.py`; 4 nas portas foram corrigidas, 7 ficaram (`criar_edital`, `anexo_do_rascunho`, `reaproveitar`, `supervisao`, `minha_etapa`, duas da mesa).
- Recomendação original: decidir a semântica por classe (403 condutor × 404 anti-enumeração).
- Rastro posterior: `D-G2` (reavaliação §14-bis, 19/09): `criar_edital`, `reaproveitar`, `supervisao` → 403; as quatro restantes ficam 404. Convergência 20/09 §11/§16: "não executada".
- Specs relacionadas: 022, 033 (inventário das negativas).
- Evidência no código atual: `interface/views.py:384-403` — `criar_edital` ainda `raise Http404` ("O mesmo 404 que a composição devolve…").
- Estado atual: DUPLICADO / ABSORVIDO — em `D-G2` (lote 4). Checagem pontual: não executada.
- Grupo do resíduo: B (via `D-G2`)
- Próxima ação sugerida: nenhuma aqui.
- Relações: E-2, ACH-35; memória "inventário de negativas cobra 404 novo".
- Confiança: alta.

### REAV-§13 — Os dois achados que nasceram no percurso da 034/035 (Retificação sem Modalidade; prática do sorteio 10/10)
- Origem: reavaliação §13 (19/09); longitudinal §6, §8, §9.4–9.5, §10 fricções 4 e 5, §19 (P1), §21 item 5
- Problema original: (1) a Retificação não acrescenta Modalidade — Perfil de cotas sem ampla não recebe não-cotista e não tem conserto; (2) dez de dez Editais que sorteiam não declaram ocorrência de fonte externa.
- Rastro posterior: `D-G5` e `D-G3` (19/09); convergência §16: ambas não executadas.
- Evidência no código atual: `interface/retificacao.py:1054` — `SECOES_QUE_ACRESCENTAM = frozenset({"perfis", "cronograma", "anexos"})`; `interface/templates/interface/retificar.html:159` — "Modalidades de Concorrência ainda não são definidas por aqui."
- Estado atual: DUPLICADO / ABSORVIDO — em `D-G5` e `D-G3` (lote 4). Checagem pontual: `D-G5` não executada.
- Grupo do resíduo: A para `D-G5` (Edital publicado sem conserto possível — convergência §20 item 3), a confirmar no lote 4; `D-G3` é governança.
- Próxima ação sugerida: nenhuma aqui.
- Confiança: alta (pontual).

### REAV-§4.4 — `_edital_do_fragmento` lia Edital de outra unidade por UUID
- Origem: reavaliação §4.4 (18/09) — achado de revisão de código da `030`
- Problema original: fragmentos htmx filtravam o Edital por `pk`, sem ator e sem escopo.
- Evidência no código atual: `interface/views.py:2197-2215` — autorização "a mesma da tela que o contém", fora do escopo → 404.
- Estado atual: RESOLVIDO
- Grupo do resíduo: —
- Confiança: alta (pontual).

### REAV-§16 — A guarda de citações aceita identificador anunciado e nunca definido (`UX-062`)
- Origem: reavaliação §16 (19/09)
- Problema original: `tests/test_citacoes_de_requisito.py` trata qualquer identificador em negrito como definição; o `UX-062` foi reservado pela `037` e nunca especificado; o teste não acusa colisão de faixa entre worktrees.
- Rastro posterior: `specs/037-quatro-becos-conhecidos/rastreabilidade.md:95` registra o `UX-062` como "reservado e não usado"; `specs/038-painel-de-conducao/checklists/requirements.md:69` registra a armadilha.
- Estado atual: NÃO IMPLEMENTADO (registrado, sem mudança na guarda)
- Ainda faz sentido?: parcialmente — é higiene de processo; a matriz de rastreabilidade já registra o buraco à mão.
- Grupo do resíduo: C
- Próxima ação sugerida: nenhuma, ou endurecer a guarda quando ela for tocada.
- Relações: memórias "faixa de FR- passou a ser global", "numeração da spec não segue a pasta".
- Confiança: média — não li o teste da guarda nesta rodada.

---

## Parte E — Relatório longitudinal (19/09, preâmbulo de 21/09): os sete itens "que ninguém mais mede"

### LONG-1 — Duas avaliações da mesma inscrição sem regra de combinação
- Origem: longitudinal, preâmbulo 21/09 item 1; avulso `doc/achado-duas-avaliacoes-sem-regra-de-combinacao.md`
- Evidência no código atual: `editais/domain/validation.py:234` (`evaluationsPerRegistration`, `minimo=1`, sem teto e sem conferência na publicação); `resultados/domain/regra.py:71-76` (consolidação recusa a Etapa inteira); nenhuma função de `validation.py` consulta `avaliacoes_previstas`/`REGRA_DE_COMBINACAO_AUSENTE` (grep).
- Estado atual: DUPLICADO / ABSORVIDO — no achado avulso (lote 7). Checagem pontual: **continua aberto**.
- Grupo do resíduo: A (ver E-7)
- Confiança: alta (pontual).

### LONG-2 — Heteroidentificação como fluxo próprio
- Origem: longitudinal preâmbulo item 2; 16/09 §5-ter.3 (CLVA/CPVA); `doc/avaliacao-de-capacidade-editais-2026-09-12.md:127` e `:402` (L-2)
- Problema original: o 28/2026 e o 57/2026 exigem verificação da autodeclaração por comissão própria (CLVA do campus, recurso à CPVA); o sistema não tem o fluxo nem a comissão.
- Recomendação original: "heteroidentificação (L-2 + spec própria)".
- Evidência no código atual: `grep -ril heteroidentifica backend/processo_seletivo` → 0 arquivos; `comissoes/models.py:31-83` — comissão única por Processo; L-2 (Etapa aplicável só a quem declarou a Modalidade) continua aberta segundo `avaliacao-de-capacidade…:402`.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim. É etapa normativa real dos Editais com cota racial da amostra, e hoje só pode acontecer fora do sistema; depende de L-2 (lote 1) e de uma comissão distinta da do certame. Não é responsabilidade de outro sistema: o resultado da verificação muda a lista de concorrência do candidato, que é dado deste.
- Lacuna residual: Etapa restrita a Modalidade; comissão de heteroidentificação e instância recursal; consequência (migração de lista × eliminação).
- Grupo do resíduo: B
- Impacto atual: Editais com PPI da amostra executam essa fase fora do sistema; a ordem por recorte pode incluir quem a verificação indeferiria.
- Próxima ação sugerida: criar spec, depois de L-2 (lote 1).
- Relações: L-2 (lote 1), ACH-60 (comissões locais).
- Confiança: alta quanto à ausência.

### LONG-3 — Barema estruturado e grupos em cascata
- Estado atual: DUPLICADO / ABSORVIDO — em ACH-56 e ACH-59 (acima). Checagem: zero ocorrências de `barema`; nenhuma prioridade entre listas.
- Grupo do resíduo: B (nos blocos próprios)
- Confiança: alta.

### LONG-4 — Notificação que não alcança ator interno ("passagem de bastão")
- Origem: longitudinal §3 e preâmbulo item 4
- Problema original: `send_mail` existe só para o candidato (código de acesso, inscrição, convocação); avaliador, comissão, julgador e gestor só descobrem trabalho abrindo a tela.
- Recomendação original: não há proposta concreta; o preâmbulo liga o item a `N-04`.
- Rastro posterior: convergência `N-02`/`N-04` (painel).
- Specs relacionadas: `specs/012-mesa-de-avaliacao/spec.md:1396-1397` — §21 declara **fora de escopo** "Comunicação: aviso de nova atribuição, lembrete, cobrança de avaliação pendente".
- Evidência no código atual: módulos com envio: `identidade/application/mensagem.py`, `inscricoes/application/mensagem.py`, `convocacao/application/comunicar.py`; zero em `avaliacoes/`, `comissoes/`, `resultados/`, `recursos/`, `classificacao/`, `sorteios/`, `matriculas/` (grep).
- Estado atual: NÃO IMPLEMENTADO (fora de escopo declarado na `012` §21)
- Ainda faz sentido?: parcialmente. Com equipe de 2–3 pessoas que acumulam papéis, "Minhas Etapas" no login e a caixa "Recursos recebidos (n)" cobrem boa parte. O caso que pesa é o recurso com prazo correndo, que hoje nem o painel mostra (`N-02`) — corrigir o painel vem antes de e-mail. E-mail interno também depende de identidade real em produção, que ainda não existe.
- Lacuna residual: nenhum aviso ativo a ator interno.
- Grupo do resíduo: C
- Impacto atual: trabalho parado só aparece para quem abre a tela.
- Próxima ação sugerida: nenhuma agora; reavaliar depois de `N-02`/`N-04` e da autenticação real.
- Relações: `N-02`, `N-04` (lote 6); E-6.
- Confiança: alta.

### LONG-5 — `E-3`: duas gramáticas / duas tabelas de vocabulário
- Estado atual: DUPLICADO / ABSORVIDO — no bloco E-3 acima (PARCIALMENTE RESOLVIDO, grupo C). O diagnóstico do preâmbulo se confirma e ficou mais preciso: a gestão passou a ter **uma** fonte (`retificacao_ui`, usada também pela Revisão desde `7b04cb3`), e o portal a sua (`publicacoes/domain/alteracoes.py`), com nomes já divergentes.
- Confiança: alta.

### LONG-6 — A Classificação concentra decisão demais (`_marco.html` com 42 controles)
- Origem: longitudinal §10 fricção 8, §11, §19 (P2); preâmbulo item 6 ("aberto, e cresceu")
- Problema original: marco com muitos controles; 28 em 16/09.
- Recomendação original: agrupar pela pergunta de negócio e revelar só os blocos acionados.
- Rastro posterior: reavaliação §4.1 (18/09) mediu no DOM: 28 → 17 controles (27 se sorteia), 6 na chegada, 2 perguntas restantes.
- Specs relacionadas: 030, 035, 037.
- Evidência no código atual: contagem de `<input|<select|<textarea` no **fonte** de `_marco.html`: `5f37eec` = 29 (1 `hidden`); `0c96283` e `bb774d9` = 42 (**13 `hidden`**), 3 `<details>`. Os não ocultos passaram de 28 para 29; os 13 ocultos preservam valores de blocos recolhidos e do método comum.
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: parcialmente. O "cresceu" do preâmbulo é **artefato de contagem**: compara tags do fonte (incluindo 13 `hidden`) com controles visíveis no DOM de 16/09. A densidade real na chegada caiu (reavaliação §4.1). O que resta é o cartão continuar sendo formulário único por marco × Perfil.
- Lacuna residual: marco ainda denso quando o elaborador abre os blocos; repetido por Perfil.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma isolada; medir no DOM antes de qualquer spec.
- Relações: ACH-10 (lote 2), ACH-61.
- Confiança: média-alta — contagem de fonte feita; DOM não remedido.

### LONG-7 — Specs implementadas seguem `Status: Draft`
- Origem: longitudinal §17 (alerta); preâmbulo item 7 (32 de 39 em 21/09)
- Evidência no código atual: hoje **38 de 44** pastas de `specs/` têm `**Status**: Draft` — inclusive `040`–`043`, implementadas; `044` é Draft legítimo. Sem linha de Status: `012-013-revisao-formas-de-conclusao`, `016`, `019`. `031` ainda diz "pronta para implementação". Só `003` e `004` declaram conclusão.
- Estado atual: NÃO IMPLEMENTADO (piorou em números absolutos: +6 Draft)
- Ainda faz sentido?: parcialmente. Não afeta produto; afeta quem chega sem contexto (o próprio briefing desta auditoria precisou avisar que Status não indica implementação). Ou se mantém o campo e se atualiza ao mesclar, ou se remove o campo; o pior é o meio-termo.
- Lacuna residual: metadado enganoso em 38 specs.
- Grupo do resíduo: C
- Próxima ação sugerida: decisão de governança (manter e atualizar, ou abolir o campo).
- Confiança: alta.

---

## Parte F — Corpo do longitudinal e sobras de 16/09 sem ID próprio

### LONG-§7/§10.9 — Matrícula e exportação sem auditoria equivalente (persona Registro Acadêmico)
- Origem: longitudinal §7 "Registro Acadêmico", §10 fricção 9, §19 (P2); reavaliação §3 (`[NÃO REAUDITADO]`)
- Rastro posterior: convergência 20/09 §13 mediu a exportação — "FECHADO no que sai / `[NÃO VALIDADO]` no destino" (importação no sistema acadêmico indisponível).
- Estado atual: DUPLICADO / ABSORVIDO — convergência §13 (lote 6).
- Grupo do resíduo: B (validação no destino, pelo lote 6)
- Confiança: alta quanto ao absorvimento.

### LONG-§10.10/§18 — A `037` em deriva de integração
- Origem: longitudinal §10 fricção 10, §13 quick win 1, §18, §19 (P2)
- Evidência: `037` mesclada (`fcb448f`, PR #144, 19/09); o próprio preâmbulo de 21/09 registra "fechado"; CLAUDE.md fala em 33 de 33 tabelas protegidas.
- Estado atual: SUPERADO / OBSOLETO
- Grupo do resíduo: —
- Confiança: alta.

### LONG-§13 — Os sete quick wins seguros
- Origem: longitudinal §13 (19/09)
- Estado por item, conferido pontualmente:
  1. concluir a `037` — ✅ mesclada.
  2. aviso de conteúdo imutável diz ação e capacidade só a quem não recebe o caminho — ✅ `037` (`interface/views.py:2814`: `"" if acoes.pode_retificar(edital, ator) else CONDUCAO_DA_RETIFICACAO`).
  3. destino do corte sempre oferecido — ✅ `037` (`interface/views.py:2855-2868`).
  4. régua "vencido" — ✅ `037` (`editais/domain/calendario.py:18-40`).
  5. peso antecipado no marco — ✅ `037` (`_etapa.html:146`); `D-G4` encerrou.
  6. sete recusas 403/404 — ❌ `D-G2` não executada (ver REAV-§8).
  7. renderizador humano na Retificação interna — não se aplica: o preâmbulo de 21/09 já mostrou que a Retificação interna traduz o caminho (`_onde_e_campo`, `interface/views.py:3420`) e que o portal recusa antes/depois por `D-009`; o resíduo real é a tabela única (E-3).
- Estado atual: RESOLVIDO para 1–5; item 6 DUPLICADO / ABSORVIDO em `D-G2`; item 7 SUPERADO / OBSOLETO. (Rótulo do bloco: RESOLVIDO.)
- Grupo do resíduo: — (resíduos nos blocos próprios)
- Confiança: alta.

### LONG-§11 — Complexidade que pode ser eliminada ou adiada
- Origem: longitudinal §11 (19/09)
- Estado por item:
  - esconder sorteio quando o marco não sorteia — ✅ na composição: `_marco.html:271` (`<details class="bloco-do-marco">` aberto só se `declarou:"draw"`); na Retificação é `ACH-32` (lote 2).
  - esconder corte sem esconder o destino — ✅ `037`.
  - derivar ampla sem lista reservada — ✅ `027` (`editais/domain/recortes.py:33-60`).
  - exportar vazio o que não se conhece — ✅ `031` (convergência §13).
  - inferir o destino de correção pela recusa — ✅ `037`.
  - **uma única derivação de "pode Retificar"** — 🟡 a `037` criou `interface/acoes.py:68` (`pode_retificar`, "uma derivação, e não duas", com o estado no predicado), usada em `interface/views.py:2814` e `:6194`; mas a tela de ocupação ainda decide por conta própria: `interface/views.py:6320` — `"pode_retificar": ator.can("retificacao:elaborar")`, só a permissão.
  - mostrar no Processo só compromissos acionáveis — é `N-04`/`N-08` (lote 6).
  - não mover peso para marco×Etapa — ✅ `D-G4`.
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: sim para a derivação duplicada — é exatamente a classe de defeito que o próprio docstring de `acoes.py:76-78` descreve.
- Lacuna residual: `interface/views.py:6320` fora da derivação única.
- Grupo do resíduo: C
- Próxima ação sugerida: corrigir quando a tela de ocupação for tocada.
- Confiança: média-alta — não verifiquei se a diferença (estado/escopo) produz caso observável na ocupação, que só existe para Edital publicado.

### UX16-§10/§12 — Complexidade e quick wins sem ID próprio: coluna MODALIDADE e "Chave" do documento
- Origem: 16/09 §10 (tabela), §12 quick win 5
- Problema original: (a) a coluna `MODALIDADE` da classificação exibe "Não declarada" em todas as linhas quando o Perfil não declara Modalidade; (b) a `Chave` do documento exigido obriga a inventar identificador técnico.
- Recomendação original: (a) omitir a coluna sem Modalidade; (b) derivar a chave do nome, editável só quando preciso.
- Rastro posterior: nenhum documento posterior retoma (grep em reavaliação, convergência e estudo de esforço).
- Evidência no código atual: (a) `interface/templates/interface/ordenacao.html:166` (cabeçalho `Modalidade` incondicional) e `:174` (`Não declarada`); (b) `interface/templates/interface/_documento.html:7-15` — "Chave *" obrigatória, ajuda oculta "Identificação estável, sem espaços".
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, ambos baratos; nenhum afeta norma.
- Lacuna residual: as duas.
- Grupo do resíduo: C
- Próxima ação sugerida: corrigir numa varredura de polish.
- Relações: ACH-05, ACH-27, ACH-32 (demais itens da mesma tabela, lote 2).
- Confiança: alta.

---

## (1) Tabela-resumo

As melhorias de 16/09 estão dentro dos blocos: 13.1 → ACH-46/E-1; 13.2 → ACH-42/ACH-43; 13.3 → ACH-40/E-2; 13.4 → E-3; 13.5 → E-4/ACH-41; 13.6 → E-6; 13.7 → E-7.

| ID | título | estado | grupo | próxima ação |
|---|---|---|---|---|
| ACH-46 | convocação inalcançável sem corte | RESOLVIDO | — | nenhuma (`D-G1` no lote 4) |
| ACH-47 | reserva sem apuração por recorte | RESOLVIDO | — | nenhuma |
| ACH-48 | sorteio sem Etapa recusado | RESOLVIDO | — | nenhuma |
| ACH-49 | Edital sem marco publicável | RESOLVIDO | — | nenhuma |
| ACH-50 | documento omitia método do sorteio | RESOLVIDO | — | nenhuma |
| ACH-51 | fonte da semente em texto livre | RESOLVIDO | — | nenhuma |
| ACH-52 | Perfil com vocabulário de vaga; sem turma | NÃO IMPLEMENTADO | C | nenhuma |
| ACH-53 | portal com título do Processo; repartição ausente | NÃO IMPLEMENTADO | B | corrigir |
| ACH-54 | sorteio oferece recorte à AC declarada; sem vagas por recorte | NÃO IMPLEMENTADO | B | criar spec |
| ACH-55 | método do sorteio não computável | RESOLVIDO | — | nenhuma |
| ACH-56 | barema não representável | NÃO IMPLEMENTADO | B | nenhuma agora (D-4) |
| ACH-59 | grupos em cascata ≠ Modalidade | NÃO IMPLEMENTADO | B | criar spec quando no alvo |
| ACH-60 | trabalho sem Perfil/polo | NÃO IMPLEMENTADO | B | corrigir (coluna/filtro) + decisão (escopo) |
| ACH-61 | escala da composição multipolo | PARCIALMENTE RESOLVIDO | C | nenhuma |
| ACH-40 | publicador sem caminho | RESOLVIDO | — | nenhuma |
| ACH-41 | duas datas-limite de recurso | NÃO IMPLEMENTADO | B | criar spec pequena (prévia da divulgação) |
| ACH-42 | parecer não chegava ao candidato | RESOLVIDO | — | nenhuma |
| ACH-43 | julgador sem a prova | RESOLVIDO | — | nenhuma (anexo do recorrente: contradito por `D-011`/`FR-007` da 018) |
| ACH-02/30/38/35/39/31/45/08/10/16 | demais itens do top 10 | DUPLICADO / ABSORVIDO (lote 2) | — | nenhuma aqui |
| E-1 | cauda não fecha | RESOLVIDO | — | nenhuma |
| E-2 | autorização × navegação | PARCIALMENTE RESOLVIDO | B | via `D-G2` e `N-04` |
| E-3 | duas gramáticas / duas tabelas | PARCIALMENTE RESOLVIDO | C | corrigir oportunamente |
| E-4 | fontes normativas sem confronto | NÃO IMPLEMENTADO | B | validar (lote 5) |
| E-5 | explicação desgrudada do campo | RESOLVIDO | — | nenhuma |
| E-6 | visão global do Processo vivo | DUPLICADO / ABSORVIDO (`N-01`…`N-08`) | B | nenhuma aqui (lote 6) |
| E-7 | validação de executabilidade | PARCIALMENTE RESOLVIDO | A | corrigir (duas avaliações, lote 7) |
| REAV-§8 | sete recusas em 404 | DUPLICADO / ABSORVIDO (`D-G2`) | B | nenhuma aqui (lote 4) |
| REAV-§13 | Retificação sem Modalidade; sorteio 10/10 | DUPLICADO / ABSORVIDO (`D-G5`, `D-G3`) | A | nenhuma aqui (lote 4) |
| REAV-§4.4 | fragmento sem autorização | RESOLVIDO | — | nenhuma |
| REAV-§16 | guarda de citações aceita ID só anunciado | NÃO IMPLEMENTADO | C | nenhuma |
| LONG-1 | duas avaliações sem regra de combinação | DUPLICADO / ABSORVIDO (avulso, lote 7) | A | nenhuma aqui |
| LONG-2 | heteroidentificação | NÃO IMPLEMENTADO | B | criar spec após L-2 |
| LONG-3 | barema e cascata | DUPLICADO / ABSORVIDO (ACH-56, ACH-59) | B | — |
| LONG-4 | notificação a ator interno | NÃO IMPLEMENTADO | C | nenhuma agora |
| LONG-5 | E-3 como tabela de vocabulário | DUPLICADO / ABSORVIDO (E-3) | C | — |
| LONG-6 | Classificação densa (`_marco.html` 42) | PARCIALMENTE RESOLVIDO | C | medir no DOM antes de spec |
| LONG-7 | specs implementadas em `Status: Draft` | NÃO IMPLEMENTADO | C | decisão de governança |
| LONG-§7/§10.9 | matrícula/exportação sem validação no destino | DUPLICADO / ABSORVIDO (convergência §13) | B | nenhuma aqui (lote 6) |
| LONG-§10.10/§18 | `037` em deriva | SUPERADO / OBSOLETO | — | nenhuma |
| LONG-§13 | sete quick wins | RESOLVIDO (1–5; 6 em `D-G2`; 7 obsoleto) | — | nenhuma |
| LONG-§11 | complexidade eliminável | PARCIALMENTE RESOLVIDO | C | corrigir `views.py:6320` oportunamente |
| UX16-§10/§12 | coluna MODALIDADE; "Chave" do documento | NÃO IMPLEMENTADO | C | corrigir (polish) |

## (2) Contagens por estado (42 blocos)

| Estado | Quantos |
|---|---|
| RESOLVIDO | 14 |
| RESOLVIDO POR OUTRO CAMINHO | 0 |
| PARCIALMENTE RESOLVIDO | 6 |
| NÃO IMPLEMENTADO | 13 |
| IMPLEMENTADO, MAS NÃO VALIDADO | 0 |
| SUPERADO / OBSOLETO | 1 |
| DUPLICADO / ABSORVIDO | 8 |
| CONTRADITO POR DECISÃO POSTERIOR | 0 (como rótulo de bloco; a sub-leitura "recorrente sem anexo" do ACH-43 é contradita por `D-011`/`FR-007` da `018`) |

Resíduos por grupo (só abertos/parciais/absorvidos com resíduo): **A = 3** (E-7, REAV-§13/`D-G5`, LONG-1 — os dois últimos com dono em outro lote), **B = 13**, **C = 10**.

## (3) Achados NOVOS encontrados de passagem

- **NOVO-1 — "Cadastro Reserva limitado em N" é publicado e nada o aplica.** `cf18a6b` (25/09) tornou `LIMITED` alcançável pela tela, e o documento imprime "limitado em 30" (`publicacoes/infrastructure/pdf.py:1684-1685`, `:1807-1808`). Mas `reserveLimit` não tem consumidor na execução: grep em `classificacao/`, `ocupacao/`, `convocacao/`, `resultados/`, `sorteios/`, `matriculas/` → vazio. Quem governa quantos suplentes existem e até onde a chamada continua é o `cutRule` (`classificacao/domain/faixa.py:17-36`: `targetKind`, `surplusCount`, `continuation`; consumido em `classificacao/application/emissao_do_corte.py:193`). São duas declarações da mesma norma, sem confronto (família E-4), e a publicada no Perfil não tem efeito. Confiança **média**: falta confirmar se o resultado publicado lista mais suplentes do que o limite, ou se a intenção foi manter `reserveLimit` como texto normativo e deixar a execução ao corte.
- **NOVO-2 (menor) — derivação duplicada de "pode Retificar" na ocupação.** `interface/views.py:6320` usa `ator.can("retificacao:elaborar")` em vez de `acoes.pode_retificar` (`interface/acoes.py:68`), que a `037` criou para ser a única resposta e que inclui o estado do Edital. Registrado também em LONG-§11. Confiança média — sem caso observável confirmado.

## (4) Incertezas que exigem validação humana

1. **ACH-54** — o comportamento vem do código (`previa.py:43-50`); não percorri a tela para confirmar que o recorte da AC declarada aparece e aceita congelar/sortear num Edital real de hoje.
2. **ACH-41 / E-4** — a recomendação original pressupõe um vínculo entre Evento do Cronograma e marco que o modelo não tem (tipo do Evento é texto livre). Decidir se o caminho é mostrar a data-limite na prévia da divulgação ou modelar o vínculo é escolha de produto.
3. **ACH-60** — escopo de trabalho por Perfil é decisão de governança (a convergência pede Edital real multipolo antes); a coluna/filtro de Perfil na distribuição é leitura e eu a recomendaria sem essa decisão — confirmar se a governança concorda em separar as duas.
4. **ACH-43 / `D-011`** — admitir prova nova no recurso é pergunta normativa; a convergência a listou como "ABERTO", e a spec `018` a recusa por requisito. Quem governa deve dizer se `D-011` continua valendo.
5. **ACH-56 / ACH-59 / LONG-2** — as três dependem de quais famílias da amostra entram no alvo (14/2026, 173/2025, Editais com PPI e heteroidentificação). Não é verificável em código.
6. **LONG-6** — a contagem de 42 é do fonte (13 `hidden`); não remedi o DOM. Confirmar no navegador antes de qualquer spec de densidade.
7. **E-6** — não refiz a medição do painel; assumi que `N-01`, `N-02`, `N-04`…`N-08` continuam abertos porque `supervisao.py` e `processo_detalhe.html` não mudaram depois de `4ec1cbb`.
8. **NOVO-1** — ver acima: confirmar a semântica pretendida de `reserveLimit`.
