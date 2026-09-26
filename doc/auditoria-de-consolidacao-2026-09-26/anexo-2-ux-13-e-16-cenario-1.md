# Lote 2 — UX de 13/09 e Cenário 1 de 16/09 (ACH-01…ACH-45)

Auditoria de consolidação, somente leitura, contra `bb774d9` (origin/main de 25/09/2026).
Caminhos de código relativos a `backend/processo_seletivo/` salvo indicação. Linhas conferidas
nesta sessão. Nada foi executado (sem suíte, sem servidor); "confirmado" significa lido no código.

**Observação de método que muda a leitura de vários itens.** Boa parte do top 10 de 13/09 foi
corrigida **antes** do commit que a reauditoria de 16/09 auditou (`5f37eec`, 16/09 14:39), em sete
commits de 13–16/09: `5c6da90` (portas, roteamento de pendência, Retificação sem UTC, estado
ato×divulgação), `9000e57` (prontidão ≠ impedimento), `6f0f988` (segundo Edital, conferir o que se
contesta), `278c275` (marco por forma da ordem), `4925827` (sete microcópias: parecer, empate
residual, nome na distribuição, Mesa→Edital, formato da nota no portal, prosa de projeto,
interstício "Tudo certo"), `a2d5d6f` (consolidar/emitir/retirar com página de conferência) e
`888b3da` (três bloqueios anunciados antes). Por isso o §5 de 16/09 já os dava como fechados, e
eu os confirmo com checagem pontual.

---

## Parte A — Auditoria de 13/09 (top 10, §§5–12, quick wins, 11.x, backlog, anexo §16)

### 13/09 #1 · §9.1 · 11.1 · P0 — Vagas imediatas × linha do quadro (duas fontes do mesmo número)
- Origem: `doc/auditoria-exploratoria-ux-2026-09-13.md` §4.1, §9.1, §11.1, §14 P0 (13/09)
- Problema original: "Vagas imediatas" publicava N vagas e a linha do quadro vazia desligava ocupação/convocação; os 4 Editais do ambiente (inclusive seed) nessa condição.
- Recomendação original: derivar a linha geral de "Vagas imediatas" enquanto não houver Modalidade; bloco do quadro só com a 1ª Modalidade; AVISO; Revisão mostra os dois.
- Rastro posterior: 16/09 §5 #1 RESOLVIDO; reavaliação 18/09 não o reabre.
- Specs relacionadas: 025 (quadro), 027 (declaração única de vagas).
- Implementação encontrada: `027` (`484d64c`, `b857f2d`, `96c498a`).
- Evidência no código atual: `interface/templates/interface/compor_perfis.html:67-72` — a ajuda diz que "a quantidade da ampla concorrência **é** a de 'Vagas imediatas'" e que o bloco do quadro só aparece com lista reservada; `editais/domain/validation.py:2446` (`_listas_reservadas_sem_linha`), `:2525` (`_linha_geral_exigida`), `:2487` (`_acervo_sem_quadro`) — avisos de recorte sem quantidade.
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não — a direção proposta foi a adotada.
- Lacuna residual: nenhuma neste recorte (cascata de grupos sem repartição, `ACH-59`, é de outro lote).
- Grupo do resíduo: —
- Impacto atual: ocupação e convocação têm quantidade no caso simples.
- Próxima ação sugerida: nenhuma
- Relações: 16/09 §5 #1; 13/09 §5 "Vagas imediatas vs linha do quadro", §7 linha 1, §12 1º item.
- Confiança: alta — derivação e avisos lidos; confirmada pela reauditoria de 16/09 em percurso.

### 13/09 #2 · P0 — Reaproveitamento publica cronograma vencido
- Origem: 13/09 §4.2, §7 "Datas herdadas", §14 P0 (13/09)
- Problema original: Edital criado de outro nascia com Cronograma CONCLUÍDA e janela do ano anterior, sem pendência.
- Recomendação original: Cronograma nasce PENDENTE; AVISO para evento no passado; IMPEDE para inscrição encerrada antes da publicação.
- Rastro posterior: 16/09 §5 #2 PARCIAL (mecanismo criado, régua errada → `ACH-08`); `037` corrigiu a régua; memória do usuário "Sem cadastro retroativo de Edital" ratifica o IMPEDE.
- Specs relacionadas: 023, 028, 037 (FR-545/546).
- Implementação encontrada: `028` (`0f36374`) + `037`.
- Evidência no código atual: `interface/views.py:1034-1049` — selo "concluída" passou a significar "válida" (`_estado_do_cronograma`, `:1009-1026`); `editais/domain/calendario.py:18-47` — vence pelo término; `editais/domain/validation.py:1987` (`_eventos_vencidos`), `:2055-2101` (`registration_period_closed`, impeditivo, só no ato de publicação); teste `tests/integration/test_seed_demo.py:230-237`.
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma aqui; ver NOVO-1 (o mesmo impeditivo aparece em Edital já publicado).
- Grupo do resíduo: —
- Impacto atual: o reaproveitamento não publica mais um certame que ninguém pode disputar.
- Próxima ação sugerida: nenhuma
- Relações: `ACH-08` (régua), `ACH-29`/NOVO-1 (persistência pós-publicação).
- Confiança: alta.

### 13/09 #3 · §9.3 · QW1 · P1 — Microcópia de consequência invisível (`.oculto` sem equivalente)
- Origem: 13/09 §4.3, §9.3, §10 QW1, §12 ("não resolver com ícone ?") (13/09)
- Problema original: 17 de 18 dicas da Classificação e 4 do Perfil só em `span.oculto`.
- Recomendação original: renderizar a dica como texto auxiliar visível junto do controle, por triagem.
- Rastro posterior: 16/09 §5 #3 PARCIAL — frases foram para "Como preencher estes campos", longe do campo (`ACH-04`/`E-5`); 030 (FR-426/FR-428) fixou que ajuda visível **não** vai para o cartão; reavaliação 18/09 §10 dá `E-5` resolvido.
- Specs relacionadas: 030 (FR-426, FR-428).
- Implementação encontrada: `details.como-preencher` por etapa + âncoras; teste que proíbe `class="ajuda"` nos cartões.
- Evidência no código atual: `compor_perfis.html:23-80` (bloco por etapa com as quatro decisões do Perfil); `compor_classificacao.html` `#ajuda-da-classificacao` só com marco na tela; `_perfil.html:71,79,121,200,223,250` continuam `.oculto` com `aria-describedby`; `tests/interface/test_medida_dos_campos.py::test_nenhum_cartao_do_assistente_carrega_ajuda_visivel` (citado na memória do projeto).
- Estado atual: **RESOLVIDO POR OUTRO CAMINHO** — a direção literal ("visível junto do controle") foi recusada pela FR-428 da 030; a prosa chega a quem enxerga pelo bloco da etapa.
- Ainda faz sentido?: não na forma original — a regra dos cartões é decisão do usuário.
- Lacuna residual: a explicação continua distante do campo na etapa Perfis (ver `ACH-04`).
- Grupo do resíduo: —
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma (o resíduo está em `ACH-04`).
- Relações: `ACH-04`, `E-5`.
- Confiança: alta.

### 13/09 #4 · §9.2 · 11.4 · P1 — Processo não recebe segundo Edital
- Origem: 13/09 §4.4, §9.2, §11.4 (13/09)
- Problema original: sem rota para `edital:criar` na interface.
- Recomendação original: "Novo Edital neste Processo" no cartão Editais; "Partir de um Edital anterior" ali.
- Rastro posterior: 16/09 §5 #4 RESOLVIDO (reteste criou o 02/2026).
- Specs relacionadas: 002, 023.
- Implementação encontrada: `6f0f988`.
- Evidência no código atual: `interface/templates/interface/edital_criar.html` existe; commit `6f0f988` explica o redirecionamento ao Edital (não à composição) porque `edital:criar` é do Gestor. Recusa de `criar_edital` ainda é 404 para quem não pode (convergência §11; `D-G2`, outro lote).
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma aqui (403×404 das sete recusas é `D-G2`, outro lote).
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `D-G2`.
- Confiança: alta (confirmado em percurso em 16/09; template e commit conferidos).

### 13/09 #5 · QW6 · P0/P1 — Julgador de recurso sem porta nem contexto
- Origem: 13/09 §4.5, §6, §10 QW6, §14 P0 e P1 (13/09)
- Problema original: `/recursos` sem link; tela do recurso sem o resultado, a avaliação, o documento nem o Edital.
- Recomendação original: link no Edital e fila em "Minhas Etapas"; objeto ao lado na tela do recurso.
- Rastro posterior: 16/09 §5 #5 PARCIAL (porta ok, contexto → `ACH-43`); `036` (instrução do recurso) fechou `ACH-43`.
- Specs relacionadas: 018, 036, 038 (sinais `UX-005`/`UX-064`).
- Implementação encontrada: `5c6da90`, `6f0f988`, `036`.
- Evidência no código atual: `interface/acoes.py:118-128` — "Recursos recebidos (N)" na tela do Edital para quem tem a permissão; `interface/templates/interface/recurso.html:40-80` — "Conferir o que se contesta" (Edital, documentos, resultado, avaliação, cada um só a quem a tela de destino admite); `recurso.html:84-175` — instrução do recurso; `interface/supervisao.py:1280,1287` — sinais para a tela de recursos no painel.
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não. A fila única "Meu trabalho" (11.3) não foi feita; ver bloco 11.3.
- Lacuna residual: recurso **aguardando admissibilidade** não gera sinal no painel (`N-02`, outro lote).
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `ACH-43`, `ACH-42`, `N-02`, 11.3.
- Confiança: alta.

### 13/09 #6 · 11.2 · P1 — A etapa Classificação cobra 30 decisões na seleção mais simples
- Origem: 13/09 §4.6, §8, §11.2, §12 (13/09)
- Problema original: 30 controles num marco de 1 Etapa; casas/arredondamento sem padrão; combinação/normalização vazias com 1 Etapa.
- Recomendação original: pergunta de entrada "pontuação · sorteio"; sorteio só na segunda; corte só quando corta; combinação só com ≥2 Etapas; padrão 2 casas e meio para cima.
- Rastro posterior: 16/09 §5 #6 PARCIAL (28 controles; `ACH-10`); reavaliação 18/09 §4.1 mediu 28→17 no total e **7→6 na chegada, 4 já preenchidos**; preâmbulo do longitudinal (21/09) diz "aberto, e cresceu: `_marco.html` declara 42 input/select/textarea".
- Specs relacionadas: 030 (FR-413, FR-415, FR-416, FR-426, FR-428, FR-429).
- Implementação encontrada: `278c275` e `030`.
- Evidência no código atual (`interface/templates/interface/_marco.html`, conferido hoje): na chegada ficam à vista `orderProduction` (`:50`), código (`:72`), denominação (`:78`), Etapas (`:104`), casas (`:157`) e modo (`:163`); padrão `ARREDONDAMENTO_PADRAO = {"scale": 2, "mode": "MEIO_PARA_CIMA"}` em `editais/domain/marcos.py:50`; recurso em `<details>` fechado (`:200`); sorteio só `{% if marco|ordena_por_sorteio %}` (`:260`), senão 10 `hidden` (`:439-448`); combinação/normalização só com `pergunta_a_combinacao` (`:461`; `interface_extras.py:217` "Só com duas ou mais Etapas"), senão 2 `hidden` (`:490-491`); corte em `<details>` fechado (`:504`).
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não. **A contagem "42 e cresceu" do longitudinal não mede o que o operador enfrenta**: soma 12 `hidden`, o bloco de sorteio que só existe quando a ordem é por sorteio e a combinação que só existe com ≥2 Etapas.
- Lacuna residual: o bloco "Método do sorteio comum a este Edital" aparece (fechado, "não declarado") mesmo em Edital sem marco de sorteio (`compor_classificacao.html:59`); densidade com 7 Perfis (`ACH-61`, outro lote); `FR-461` segue aviso (`validation.py:1706-1735`, `D-G1`, outro lote).
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma (se quiser, ocultar o bloco comum quando nenhum marco sorteia).
- Relações: `ACH-10`, `ACH-09`, `ACH-61`, `D-G1`, `D-G4`.
- Confiança: alta — template e filtros lidos; medição de DOM de 18/09 coerente.

### 13/09 #7 · §9.5 · QW9 · 11.5 · P1 — Retificação em JSON Pointer e UTC na conferência
- Origem: 13/09 §4.7, §9.5, §10 QW9, §11.5 (13/09)
- Problema original: telas da Retificação, de homologação e de publicação mostravam `/schedule/id=…/endAt` e `2026-10-11T02:59:00+00:00` (dia errado).
- Recomendação original: reaproveitar o renderizador público; instantes na zona institucional; a página pública ganhar antes/depois.
- Rastro posterior: 16/09 §5 #7 PARCIAL (UTC eliminado; caminho e `REPLACE` na tela do ato → `ACH-31`); longitudinal (21/09) item 5: "as telas internas já não mostram caminho cru", duas tabelas de vocabulário paralelas (`E-3`, outro lote).
- Specs relacionadas: 004, 020, 024 (D-005/D-009).
- Implementação encontrada: `5c6da90`.
- Evidência no código atual: `interface/views.py:3336-3351` (`_resumo_de_linha` converte instante pelo fuso), `:3420-3458` (`_onde_e_campo`), `:3460-3490` (`_alteracoes_legiveis`); `retificacao_confirmar.html:42-62` (tela de publicar: Onde/Antes/Depois, sem coluna de operação); `retificacao_detalhe.html:53-78`. Página pública: `publicacoes/domain/alteracoes.py:1-17` — **não** devolve antes/depois, por decisão (024, D-005/D-009).
- Estado atual: **RESOLVIDO POR OUTRO CAMINHO** — tabela de vocabulário da gestão (`CAMPO_EM_PORTUGUES`), e não o renderizador público; a metade "página pública ganha antes/depois" foi recusada por decisão da 024.
- Ainda faz sentido?: não; o que sobra está em `ACH-31` e em `E-3`.
- Lacuna residual: ver `ACH-31`.
- Grupo do resíduo: —
- Impacto atual: quem assina lê data e campo corretos.
- Próxima ação sugerida: nenhuma
- Relações: `ACH-31`, `E-3` (duas tabelas de vocabulário), longitudinal item 5.
- Confiança: alta.

### 13/09 #8 · §5 "Impedimento" · P1 — "Impedimento" com dois sentidos
- Origem: 13/09 §4.8, §5 (13/09)
- Problema original: "6 com impedimento" significava "não consolidável ainda"; ao lado, "Impedimentos" = conflito de interesse.
- Recomendação original: renomear o estado de prontidão; colapsar contadores sobrepostos.
- Rastro posterior: 16/09 §5 #8 RESOLVIDO (nome) / PERSISTENTE (contadores → `ACH-27`); convergência §4 `ACH-27` PARCIAL/DESLOCADO (`N-07`).
- Specs relacionadas: 012, 013.
- Implementação encontrada: `9000e57` — estado `nao-consolidavel`.
- Evidência no código atual: commit `9000e57`; `resultados/domain/regra.py:57` (`impedimento_da_regra` fica no domínio, "não chega a tela nenhuma").
- Estado atual: **RESOLVIDO** (nomenclatura); contadores em `ACH-27`.
- Ainda faz sentido?: não.
- Lacuna residual: ver `ACH-27`.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `ACH-27`, `N-07`.
- Confiança: alta.

### 13/09 #9 · P2 — Atos operacionais irreversíveis em um clique
- Origem: 13/09 §4.9, §14 P2 (13/09)
- Problema original: "Consolidar as selecionadas", "Emitir ordem" e "Remover da comissão" sem conferência; marco silente sobre a divulgação depois do sucessor.
- Recomendação original: estender a página de ato a consolidar, emitir e remover membro; marco dizer "ato vigente × divulgação".
- Rastro posterior: 16/09 §5 #9 RESOLVIDO ("Confira antes de consolidar/emitir"; o marco avisa que a divulgação ficou para trás). **A remoção de membro não foi retestada** (16/09 §17: "remoção de membro com trabalho feito" em "não executado").
- Specs relacionadas: 011 (comissão), 013, 015, 017.
- Implementação encontrada: `a2d5d6f` (consolidar, emitir, retirar atribuições) e `5c6da90` (estado da divulgação).
- Evidência no código atual: `consolidacao_confirmar.html`, `ordenacao_confirmar.html`, `distribuicao_remover_confirmar.html` existem; `ordenacao.html:100-116` (nunca divulgado / "A divulgação pública ficou para trás"). **Mas** `comissao.html:101-111` posta `acao=remover` direto, e `interface/views.py:4489-4497` chama `comissao_app.remover_membro` sem página de conferência; o comando (`comissoes/application/comissao.py:236-281`) inativa o membro **e todas as alocações ativas dele** em cascata.
- Estado atual: **PARCIALMENTE RESOLVIDO**
- Ainda faz sentido?: parcialmente. A remoção é inativação auditada (nada se apaga, e a pessoa pode ser reincluída), mas desfaz a alocação de todas as Etapas da pessoa sem dizer quantas inscrições ficam sem avaliador — exatamente o que a conferência de "retirar atribuições" já nomeia.
- Lacuna residual: "Remover da comissão" sem conferência do trabalho afetado.
- Grupo do resíduo: C
- Impacto atual: baixo-médio; recuperável por reinclusão e realocação.
- Próxima ação sugerida: corrigir (pequeno: reaproveitar o padrão de `distribuicao_remover_confirmar.html`)
- Relações: padrão "página de ato" (13/09 §13.1).
- Confiança: alta (view e comando lidos).

### 13/09 #10 · P2 — Bloqueios corretos que chegam tarde
- Origem: 13/09 §4.10, §14 P2 (13/09)
- Problema original: distribuição, publicação definitiva e segregação só se revelavam na tentativa.
- Recomendação original: anunciar antes, como a tela da Comissão.
- Rastro posterior: 16/09 §5 #10 RESOLVIDO em 2 de 3 e a 3ª parcial (`ACH-19`).
- Specs relacionadas: 012, 017, 001 (FR-021).
- Implementação encontrada: `888b3da`.
- Evidência no código atual: `publicacoes/application/selectors.py:275-288` (`homologar_fecharia_a_publicacao`), usada em `interface/views.py:2962`; `acoes.py:287-313` (observação de segregação no Edital homologado).
- Estado atual: **RESOLVIDO** (o resíduo menor está em `ACH-19`).
- Ainda faz sentido?: não.
- Lacuna residual: ver `ACH-19`.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `ACH-19`, `ACH-26`.
- Confiança: alta.

### 13/09 §9.6 · anexo §16 · P1/P2 — A Retificação alcança ~40% do que publica e não declara o que fica de fora
- Origem: 13/09 §9.6, §16 (anexo), §14 P1 e P2 (13/09)
- Problema original: 13–23 campos normativos sem decisão de retificabilidade (requisitos, descrição, espécie do cadastro reserva, janela recursal, arredondamento, combinação, Etapas do marco, desempate, local, teto de inscrições, designação do período, vínculo Etapa↔Evento, método do sorteio, arredondamento da reserva, prosa institucional); guardião só para `CAMPOS_ETAPA`.
- Recomendação original: fechar primeiro a pergunta normativa; guardião que compare forma publicada × forma classificada; nota explícita do que não se alcança.
- Rastro posterior: `doc/decisao-mutabilidade-normativa.md`; 16/09 PP-50 ("O que não se corrige por Retificação nesta seção"); convergência §4 `AX-1` aberto (desempate), `D-G5` (Retificação não acrescenta Modalidade) — ambos de outros lotes.
- Specs relacionadas: 026 (contrato de mutabilidade), 029, 030, 035.
- Implementação encontrada: `026`.
- Evidência no código atual — o que a Retificação alcança hoje (`interface/retificacao.py`): requisitos (`:63-67`, `LISTA_DE_TEXTO`), descrição do Perfil (`:74`), forma de convocar (`:95`), local e designação do período (`:100-112`), teto de inscrições (`:113-126`), método do sorteio comum e do marco (`:139-149`, `:263-274`, oferecido sempre — `:861-873`), combinação/normalização (`:180-192`), forma da ordem (`:203`), arredondamento (`:231-234`), janela recursal (`:241-245`), corte parcial (`:286-301`), reversão (`:320-322`), regra da reserva (`:163-178`). Fica de fora **com razão escrita no contrato** e rótulo em português (`:1091-1119`, razões em `editais/domain/mutabilidade.py`, ex.: `:236` espécie do cadastro reserva, `:255` prosa institucional, `:326` Etapas do marco, `:417` desempate): espécie do cadastro reserva, arredondamento/cálculo da reserva, Etapas do marco, espécie/Etapa do alvo do corte, tipo e parâmetros do desempate, tipo do Evento, chave do documento. `stages.scheduleEventId` é `estrutural()` (`mutabilidade.py:447`). A tela declara as exclusões por seção (`retificar.html:113-135`). Guardião nos dois sentidos: `tests/contract/test_mutabilidade.py:1-20` (+ `test_contrato_governa_a_retificacao.py`, `tests/interface/test_retificar_exclusoes.py`).
- Estado atual: **RESOLVIDO** — todo campo publicado tem decisão escrita e guardada por teste; a tela diz o que não alcança.
- Ainda faz sentido?: não como achado. O mérito de algumas exclusões (desempate, Modalidade nova, vínculo Etapa↔Evento) está em `AX-1`, `D-G5` e `N-05`, de outros lotes.
- Lacuna residual: nenhuma **neste** achado.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `AX-1`…`AX-17`, `D-G5`, `N-05`, `ACH-32`, `ACH-34`.
- Confiança: alta.

### 13/09 QW2 · §9.4 · §6 · P1 — Pendência de marco roteada para "Perfis de Vaga"
- Origem: 13/09 §3, §6, §9.4, §10 QW2 (13/09)
- Problema original: `DESTINO_DA_PENDENCIA` sem `classificacao`; peso ausente mandado à tela errada.
- Recomendação original: entrada `classificacao` e entrada específica para o peso.
- Rastro posterior: 16/09 PP-16 ("Ir para Etapas de Avaliação" levou à etapa certa).
- Specs relacionadas: 002 (FR-007/FR-027), 028.
- Implementação encontrada: `5c6da90`.
- Evidência no código atual: `interface/views.py:659-712` — `classificationMilestones → classificacao`, `/schedule → inscricao`, `DESTINO_POR_CODIGO = {"milestone_stage_without_weight": ("etapas", …)}` e busca do segmento mais profundo para o mais raso.
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `ACH-16`.
- Confiança: alta.

### 13/09 QW3 · QW4 · QW5 · QW8 · P3 — Quatro correções pontuais (tokens em inglês na Revisão; etapa Anexos sem navegação; Edital não abre da lista; texto obsoleto sob "Revisar inscrição")
- Origem: 13/09 §10 QW3, QW4, QW5, QW8; §14 P2/P3 (13/09)
- Problema original: "Composta a partir de attachments"; etapa 7 sem ‹ Voltar / Avançar ›; número/título do Edital como texto puro; "depois de anexar o documento que falta" com o documento já anexado.
- Recomendação original: completar dicionários; dar navegação; tornar links; corrigir a condição.
- Rastro posterior: `5c6da90` (QW4, QW5), 16/09 não reabre.
- Specs relacionadas: 002, 008, 020, 040 (a lista foi refeita).
- Implementação encontrada: `5c6da90` e correções do portal.
- Evidência no código atual: `interface/forms.py:791-796` e `interface/revisao.py:216-219` (Documentos Exigidos, Anexos); `compor_anexos.html:182` inclui `_navegacao_etapa_links.html`; `_linha_do_edital.html:21` e `lista.html:96-97` com `interface:detalhe`; `portal/templates/portal/_ajuda_da_acao.html:1-20` atualizado fora de banda (`hx-swap-oob`).
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: —
- Confiança: alta.

### 13/09 QW7 · §9.8 · §6 "Publicar o resultado" · P1 — A ação mais consequente mora numa tela de auditoria
- Origem: 13/09 §4.9, §6, §9.8, §10 QW7 (13/09)
- Problema original: "Publicar resultado" atrás de "Consultar ato e proveniência"; marco sem o estado "emitido e não divulgado".
- Recomendação original: botão no marco + estado ato vigente × divulgação.
- Rastro posterior: `5c6da90` ("Estado, e não ação: a 017, SC-002, mantém a publicação na tela do ato"); 16/09 `ACH-37`/`ACH-40`; `033` (divulgação derivada por destino).
- Specs relacionadas: 017 (SC-002), 033 (FR-473/476).
- Implementação encontrada: estado no marco (`ordenacao.html:100-116`); destino "divulgar o resultado" na tela do Edital (`interface/views.py:2872-2883`), direto para a prévia de publicação; sinal `UX-066` do painel (038) para ato por divulgar.
- Evidência no código atual: as linhas acima; `detalhe.html:150-172` desenha os destinos por ator.
- Estado atual: **RESOLVIDO POR OUTRO CAMINHO** — o botão não foi ao marco por decisão da 017 (SC-002); o marco diz o estado e a tela do Edital leva à prévia.
- Ainda faz sentido?: não; sobra o rótulo (ver `ACH-37`).
- Lacuna residual: ver `ACH-37`.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `ACH-37`, `ACH-40`, `ACH-38`.
- Confiança: alta.

### 13/09 QW10 · §8 "Ativar Processo" · P3 — O botão "Ativar Processo" aparece como próximo passo
- Origem: 13/09 §3, §8, §10 QW10 (13/09)
- Problema original: publicação do 1º Edital já ativa; o botão se oferecia como o passo que falta.
- Recomendação original: remover.
- Rastro posterior: 16/09 PP-38 (a ativação derivada é anunciada e cumprida).
- Specs relacionadas: 002/003.
- Implementação encontrada: o ato continua, com explicação.
- Evidência no código atual: `interface/atos_processo.py:29-41` (ato `ativar` em `EM_ELABORACAO`); `processo_detalhe.html:196-206` — "Publicar o primeiro Edital deste Processo já o ativa. Este ato existe para quando a abertura formal precisa vir antes", com o comentário da decisão.
- Estado atual: **RESOLVIDO POR OUTRO CAMINHO** — mantido por razão escrita (abertura formal pode preceder a publicação), com a consequência dita ao lado.
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: —
- Confiança: alta.

### 13/09 QW12 · §7 "Admite recurso" — Prazo recursal só aparece dentro de "Recorrer"
- Origem: 13/09 §2 (nota de experiência do candidato), §10 QW12 (13/09)
- Problema original: o prazo recursal não aparecia junto do resultado.
- Recomendação original: prazo na página pública do resultado e em "Acompanhar".
- Rastro posterior: 16/09 PP-82 ("Cabe recurso contra este resultado até…" no acompanhamento); convergência 20/09 §7: "a página pública do resultado não diz nada" (S1).
- Specs relacionadas: 017, 018, 026 (janela recursal).
- Implementação encontrada: só a metade do acompanhamento.
- Evidência no código atual: `portal/templates/portal/acompanhamento.html:160` ("Cabe recurso… até"); `portal/templates/portal/resultado.html` sem menção a prazo (só às correções por recurso, `:40-41`); `divulgacao/infrastructure/documento.py` — o documento da divulgação cita decisões de recurso (`:113-126`) e não a janela.
- Estado atual: **PARCIALMENTE RESOLVIDO**
- Ainda faz sentido?: sim — o resultado preliminar é ato público e o prazo de recurso é o que a pessoa (ou quem a representa) precisa ler ali; quem não se inscreveu pelo portal ou só lê a relação pública não o encontra.
- Lacuna residual: página pública e documento do resultado preliminar não declaram a janela recursal.
- Grupo do resíduo: B
- Impacto atual: médio-baixo (o titular tem o prazo no acompanhamento).
- Próxima ação sugerida: criar spec curta (ou emenda à 017): a divulgação preliminar declara a janela do marco.
- Relações: `ACH-41` (duas datas), convergência §7.
- Confiança: alta (templates e documento lidos).

### 13/09 QW13 · P3 — E-mail de confirmação sai com "Concorrência:" vazio
- Origem: 13/09 §10 QW13 (13/09)
- Problema original: rótulo sem valor quando não há Modalidade.
- Recomendação original: preencher o valor.
- Rastro posterior: nenhum.
- Specs relacionadas: 010 (FR-084), 009.
- Implementação encontrada: o comprovante omite a linha vazia; o e-mail não.
- Evidência no código atual: `inscricoes/application/mensagem.py:50` (`Concorrência: {modalidade}` sempre impresso); `portal/views.py:2012` passa `campos["Concorrência"]`, que é `""` quando `modality_id is None` (`portal/views.py:2148-2150`); contraste `portal/templates/portal/comprovante.html:50` (`{% if modalidade %}`).
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim, mas é cosmético — o recibo por e-mail e o papel deveriam dizer a mesma coisa (o próprio docstring da `_confirmar_por_email` pede isso).
- Lacuna residual: linha vazia no e-mail; escrever "Ampla concorrência" ou omitir a linha.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: corrigir (uma linha)
- Relações: memória "Ampla concorrência tem duas grafias".
- Confiança: alta.

### 13/09 P2 "Distribuição sem nome" · "Parecer mal explicado" · "Mesa sem link para o Edital" · "Empate residual sem explicação" · §12 "Editais externos na microcópia" · §8 "Interstício 'Tudo certo'" — seis microcópias
- Origem: 13/09 §3, §7 (desempate), §8, §12, §14 P2/P3 (13/09)
- Problema original: protocolo sem nome na distribuição; "É o parecer que responde a um recurso"; Mesa sem o Edital; "Empate residual" sem o critério esgotado; microcópia citando 77/2026 etc.; interstício que não informava nada.
- Recomendação original: as seis correções literais do backlog.
- Rastro posterior: `4925827` e `278c275` (16/09, antes do baseline da reauditoria).
- Specs relacionadas: 012, 013, 015, 009.
- Implementação encontrada: os dois commits.
- Evidência no código atual: `distribuicao.html:358` (nome ao lado do protocolo); `mesa_inscricao.html:285` ("Registre o que fundamenta… É o que responderá a um eventual recurso"); `mesa_inscricao.html:23` (link ao Edital); `ordenacao.html:170-182` (nota "sobre o que sobrou" no empate residual); varredura dos templates `interface/` e `portal/` fora de comentários não achou citação de Edital da amostra (só um exemplo de data em `convocacao.html:204`); `portal/views.py:711-736` (`_de_volta_a_vaga` substitui o interstício).
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `ACH-22` (a retomada da intenção depois da identificação).
- Confiança: alta.

### 13/09 P2 "Candidato não vê vagas por modalidade" — A repartição não chega à página da vaga
- Origem: 13/09 §2 (experiência do candidato), §14 P2 (13/09); 4ª ocorrência em 16/09 §5-ter.3
- Problema original: a página pública lista as concorrências sem as quantidades.
- Recomendação original: quadro por lista na página pública.
- Rastro posterior: 16/09 §5-ter ("O candidato PcD de Iúna não sabe que há 2 vagas para ele").
- Specs relacionadas: 009, 024, 025, 027.
- Implementação encontrada: nenhuma na página da vaga (o PDF publica o quadro).
- Evidência no código atual: `portal/views.py:188-190` — `modalidades` é só a lista de nomes; `portal/templates/portal/selecao.html:144` imprime "Concorrência: A; B; C"; `:179-186` imprime só o total de vagas imediatas.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim — a família dominante da amostra é sorteio + cotas, e a escolha da modalidade acontece nessa página.
- Lacuna residual: quantidade por recorte na página da vaga.
- Grupo do resíduo: B
- Impacto atual: médio (a informação existe no PDF).
- Próxima ação sugerida: criar spec curta (leitura do quadro já publicado; sem regra nova)
- Relações: `ACH-54` (recorte sem vagas no sorteio, outro lote).
- Confiança: alta.

### 13/09 P3 "'Etapa' nomeia passo e objeto" · §5 "Marco (Supervisão)" · §5 "Providência a jusante" · P2 coluna MODALIDADE "Não declarada" — colisões de vocabulário remanescentes
- Origem: 13/09 §5, §8, §14 P3 (13/09); 16/09 §10 e §12 QW5 (coluna MODALIDADE)
- Problema original: "etapa atual" no assistente × "Etapas de Avaliação"; "Próximos marcos" (Cronograma) × "marco classificatório"; "providência a jusante" incompreensível; coluna MODALIDADE "Não declarada" em todas as linhas.
- Recomendação original: "Passo 4 de 9"; desfazer a colisão; traduzir o jargão; ocultar a coluna sem modalidades.
- Rastro posterior: 16/09 PP-87 chama "providência a jusante" de "vocabulário de domínio correto" — as duas auditorias discordam; convergência 20/09 §8: "sem marco no cronograma" continua sem consequência legível.
- Specs relacionadas: 002, 015, 018, 038.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `compor_base.html:14,27` ("Etapas da composição", "etapa atual"); `processo_detalhe.html:111` e `supervisao.html:109` ("Próximos marcos"), `interface/supervisao.py:601-626` ("está sem marco no cronograma"); `recurso.html:237` (opção "Deferir determinando providência a jusante", sem explicação); `ordenacao.html:166,174` (coluna Modalidade com "Não declarada").
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: parcialmente — a coluna vazia e "sem marco no cronograma" são ruído barato de tirar; "Etapa" no assistente e "providência a jusante" são debate de vocabulário, não defeito.
- Lacuna residual: quatro colisões de nome, sem efeito normativo.
- Grupo do resíduo: C
- Impacto atual: baixo (primeiro contato).
- Próxima ação sugerida: nenhuma isolada; cabe numa varredura de microcópia
- Relações: `ACH-09` (a assimetria Etapa×marco, resolvida), convergência §8.
- Confiança: alta.

### 13/09 §5 "Ampla concorrência" (três coisas com o mesmo nome)
- Origem: 13/09 §5 (13/09)
- Problema original: "qual delas é a ampla concorrência", "linha geral do quadro" e Modalidade "AC" com o mesmo nome.
- Recomendação original: implícita — a tela não amplificar a ambiguidade do domínio.
- Rastro posterior: 16/09 §5-bis.1 ("a linha duplicada some sozinha ao declarar qual modalidade é a AC"); `027` "a ampla declarada não recebe caixa"; convergência §7 classifica a tripla como "divergência normativa (S2) — `E-4`"; memória "Ampla concorrência tem duas grafias".
- Specs relacionadas: 014, 025, 027, 034.
- Implementação encontrada: `25ca019`, `25dea37`, `6b949e0` (027).
- Evidência no código atual: `compor_perfis.html` ("Qual Modalidade é a ampla concorrência — a declarada não recebe linha própria no quadro"); `validation.py:1076` e `:1117` (`_ampla_concorrencia_declarada`, `_ampla_por_declarar`).
- Estado atual: **DUPLICADO / ABSORVIDO** — em `E-4` (convergência §7) e `ACH-54` (outros lotes).
- Ainda faz sentido?: —
- Lacuna residual: ver `E-4`/`ACH-54`.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma aqui
- Relações: `E-4`, `ACH-54`.
- Confiança: média — checagem pontual; mérito é de outro lote.

### 13/09 §9.7 · P2 "Supervisão não vê resultado nem recurso" · 11.3 "Meu trabalho" · §12 "não criar dashboard" · P3 "Trilha de auditoria em cinco telas" — visão global
- Origem: 13/09 §4.5, §9.7, §11.3, §12, §14 P2/P3 (13/09)
- Problema original: a Supervisão não mencionava classificação, publicação nem recurso; cada papel sem fila; auditoria em cinco telas.
- Recomendação original: acrescentar classificação/publicação/recursos ao Pulso; "Meu trabalho" por ator; linha do tempo única.
- Rastro posterior: 16/09 `ACH-25`/`E-6`; `038` (painel de condução, "prolongar o Pulso, sem dashboard separado" — direção do §12 adotada); convergência 20/09 §4/§6: **PARCIAL** (`N-01`…`N-04`).
- Specs relacionadas: 038.
- Implementação encontrada: `038`; `4ec1cbb` (N-03).
- Evidência no código atual: `interface/supervisao.py:1280,1287` (sinais de recurso → tela de recursos); `processo_detalhe.html:111` (Próximos marcos por Edital); `auditoria/selectors.py:86-107` — a trilha do Edital reúne Edital, Retificações e atos de condução (ocupação, convocação, instrução).
- Estado atual: **DUPLICADO / ABSORVIDO** — em `ACH-25`/`E-6` e `N-01`…`N-04` (convergência), outro lote.
- Ainda faz sentido?: —
- Lacuna residual: ver `N-01`…`N-04`.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma aqui
- Relações: `ACH-25`, `E-6`, `N-01`…`N-04`.
- Confiança: média — checagem pontual.


---

## Parte B — Reauditoria de 16/09, Cenário 1 e §§1–5 (ACH-01…ACH-45)

O §5 de 16/09 (regressão contra 13/09) está coberto pelos blocos da Parte A: cada linha dele é
retomada ali com o estado de hoje. Abaixo, os achados `ACH-01`…`ACH-45`.

### ACH-01 · 13/09 §6 "Chegar à área administrativa" · §15.5 item 1 — Nenhum caminho da raiz pública para `/gestao/`
- Origem: 16/09 §4, §8, §16 P2; diário Fase A passo 1 (16/09); 13/09 §6 (E4) e §15.5
- Problema original: o único "Entrar" do portal leva ao acesso do candidato; a gestão só se acha pela URL.
- Recomendação original: "rodapé discreto".
- Rastro posterior: reavaliação 18/09 §9 "intocado"; `033` o menciona só como contexto.
- Specs relacionadas: 009, 033.
- Implementação encontrada: nenhuma — e a raiz foi **deliberadamente** apontada à vitrine.
- Evidência no código atual: `config/urls.py:12-16`; `shared/api/operacional.py:26-53` — o docstring do `IndexView` explica que quem digita a raiz "quase nunca é quem elabora Edital", e redireciona para `portal:vitrine`; `portal/templates/portal/base.html:809-848` — cabeçalho sem link para a gestão.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: pouco. Em produção o servidor chega pela URL institucional (e a identidade real não é o seletor de demonstração); um link público para a gestão só serve ao primeiro contato de quem já tem conta.
- Lacuna residual: nenhum caminho visível portal → gestão.
- Grupo do resíduo: C
- Impacto atual: baixo (treinamento de 1 frase; afeta sobretudo auditorias e demonstrações).
- Próxima ação sugerida: nenhuma (ou um link discreto no rodapé, decisão de produto)
- Relações: 13/09 §6.
- Confiança: alta.

### ACH-02 · 13/09 §6 "Preencher o Edital (só com papel Gestor)" — Gestor que criou o Edital não sabe o que falta nem a quem pedir
- Origem: 16/09 §6.6, §12 QW1, §16 P1; diário Fase A passo 9 (16/09)
- Problema original: validação lista IMPEDE e não há controle nem indicação de papel ausente.
- Recomendação original: generalizar "Peça a alguém com a permissão de…".
- Rastro posterior: `037` (FR-541…FR-544, SC-195); `specs/037-quatro-becos-conhecidos/achado-do-ach-02.md` (percurso de 19/09: saída (a)); reavaliação §14 "fechou inteiro".
- Specs relacionadas: 037.
- Implementação encontrada: condução nas pendências das etapas de composição (somente leitura), mecanismo único `frase_do_aviso`.
- Evidência no código atual: `interface/views.py:816-866` (`_pendencias(..., ator=)` monta `conducao` com `CONDUCAO_DA_COMPOSICAO`, `:4367`); `interface/acoes.py:260-264` ("Aguardando quem elabora para submeter o Edital para revisão"); teste `tests/interface/test_conducao_dos_bloqueios.py`.
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: as duas observações que o próprio `achado-do-ach-02.md` registrou e não viraram escopo — (1) a faixa de somente leitura nomeia o codename `edital:elaborar`; (2) a tela do Edital lista a pendência sem "Ir para" e sem condução (`detalhe.html:168-180` imprime só severidade e mensagem; `detalhe` chama `_pendencias(edital)` sem `ator`, `views.py:2787`).
- Grupo do resíduo: C
- Impacto atual: baixo — o cartão ao lado diz "Aguardando quem elabora".
- Próxima ação sugerida: nenhuma (registrado na 037)
- Relações: `ACH-30`, `ACH-38`, `ACH-31`/`ACH-45` (mesma família do codename).
- Confiança: alta.

### ACH-03 · ACH-15 · 13/09 P2 "CONCLUÍDA significa 'apertei Avançar'" — Selos das etapas que contradizem a própria tela
- Origem: 16/09 §12 QW8, §16 P3; diário Fase B (etapas 7 e 8) (16/09); 13/09 §14 P2
- Problema original: etapa 8 nasce "pronta para revisar" entre etapas pendentes; etapa 7 fica PENDENTE quando a própria tela diz que vazio "é legítimo"; "concluída" = "gravei".
- Recomendação original: Anexos deixar de ficar PENDENTE; refletir a validação no selo.
- Rastro posterior: `028` mudou só o Cronograma para "concluída = válida".
- Specs relacionadas: 002, 020, 028 (FR-359).
- Implementação encontrada: só a parte do Cronograma.
- Evidência no código atual: `interface/views.py:1032-1072` — `"anexos": CONCLUIDA if edital.anexos.exists() else PENDENTE` (`:1068`), `"conteudo": … else PRONTA` (`:1069`), `"cronograma": _estado_do_cronograma(...)` (`:1049`); `compor_anexos.html:148` mantém "É legítimo: nem todo Edital fornece formulário próprio".
- Estado atual: **PARCIALMENTE RESOLVIDO** (Cronograma sim; Anexos e Conteúdo não)
- Ainda faz sentido?: parcialmente — o selo de Anexos contradiz a frase da própria etapa; o "pronta para revisar" do Conteúdo é correto (o diário o rebaixou a S1).
- Lacuna residual: Anexos PENDENTE quando vazio é legítimo.
- Grupo do resíduo: C
- Impacto atual: baixo (o selo não impede nada).
- Próxima ação sugerida: corrigir (Anexos sem anexo = concluída, ou selo neutro)
- Relações: 13/09 #2 (o selo do Cronograma).
- Confiança: alta.

### ACH-04 — A explicação desgrudou do campo (bloco "Como preencher" distante e presente com zero cartões)
- Origem: 16/09 §5 #3, §11 `E-5`, §16 P2; diário Fase B etapa 2 e Fase 3 (16/09)
- Problema original: o bloco coletivo aparece antes de existir Perfil e fica longe dos campos que explica.
- Recomendação original: aproximar a explicação sem violar a regra de ajuda fora dos cartões.
- Rastro posterior: `030` FR-426 (bloco só com o objeto na tela) e âncoras; reavaliação 18/09 §4.2 ✅ e §10 `E-5` resolvido.
- Specs relacionadas: 030.
- Implementação encontrada: na **Classificação**: `compor_classificacao.html` `#ajuda-da-classificacao` só `{% if ancora_do_marco %}`, com âncoras por campo.
- Evidência no código atual: Classificação como acima; **Perfis**: `compor_perfis.html:23-24` — `<details class="como-preencher">` incondicional, fora de qualquer `{% if perfis %}`, e ainda com "Percentuais de modalidades distintas não somam cem por cento" (`:27`).
- Estado atual: **PARCIALMENTE RESOLVIDO** — a FR-426 foi aplicada à etapa de Classificação e não à de Perfis, que é justamente onde o achado foi observado.
- Ainda faz sentido?: parcialmente — o bloco nasce fechado, o custo é pequeno.
- Lacuna residual: bloco de Perfis presente com 0 Perfis e sem âncora por campo.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: validar se a FR-426 pretendia valer para todas as etapas; se sim, corrigir
- Relações: 13/09 #3, `E-5`.
- Confiança: alta (template lido); média sobre a intenção da FR-426.

### ACH-05 · 13/09 §8 "três seletores de modalidade" — Decisões de fases posteriores cobradas na composição do Perfil
- Origem: 16/09 §10, §16 P2 (linha `ACH-10/05`); diário Fase B etapa 2 (16/09)
- Problema original: "qual é a ampla concorrência", "reversão" e "como a convocação é comunicada" cobrados sem modalidade declarada.
- Recomendação original: os dois primeiros só após a 1ª Modalidade; a forma de convocação perguntada na convocação.
- Rastro posterior: reavaliação 18/09 §4.3 PARCIAL.
- Specs relacionadas: 014, 016, 019 (D-009, R-007), 030.
- Implementação encontrada: `030`.
- Evidência no código atual: `_perfil.html:173-228` — ampla e reversão só `{% if perfil.modalidades %}`, senão `hidden`; `_perfil.html:242-250` — "Como a convocação é comunicada" sempre presente; `interface/retificacao.py:84-99` — a forma de convocar é **norma publicada** e "declarada aqui antes da primeira emissão", porque o Edital publicado sem ela "nasceria irretificável nela"; `editais/domain/validation.py:994` (`_forma_de_convocacao_declarada`, aviso).
- Estado atual: **PARCIALMENTE RESOLVIDO**
- Ainda faz sentido?: não para a parte que sobra — a forma de convocação é conteúdo que o Edital publica (a amostra tem as duas formas), e perguntá-la só na convocação faria o Edital sair sem a norma.
- Lacuna residual: nenhuma que se recomende.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `ACH-10`, 13/09 §8.
- Confiança: alta.

### ACH-06 — `name` dos campos do formulário em inglês
- Origem: 16/09 §16 P3; diário Fase B (16/09)
- Problema original: `duties`, `requirements`, `reserveType`… num projeto "tudo em português".
- Recomendação original: nenhuma (S0, "registrado por consistência").
- Rastro posterior: nenhum.
- Specs relacionadas: —
- Implementação encontrada: —
- Evidência no código atual: `_perfil.html:67-78` (`perfil-{{ indice }}-duties` etc.): os nomes espelham as chaves do conteúdo canônico (`publish_edital.py`), que são contrato e também caminho de Retificação (`retificacao.py:63-99`).
- Estado atual: **SUPERADO / OBSOLETO** — não é defeito: o `name` é a chave do contrato normativo, e traduzi-lo criaria um mapeamento a mais.
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: nenhum (invisível ao usuário)
- Próxima ação sugerida: nenhuma
- Relações: —
- Confiança: alta.

### ACH-07 — "Rascunho salvo — Cronograma" enquanto o selo diz PENDENTE, sem sinal do porquê
- Origem: diário Fase B etapa 3 (16/09); não tem linha própria no §16
- Problema original: a confirmação de gravação não dizia que a etapa gravada ficou pendente.
- Recomendação original: implícita (sinalizar).
- Rastro posterior: `037` corrigiu a régua que produzia o caso observado (`ACH-08`).
- Specs relacionadas: 028 (UX-049), 037.
- Implementação encontrada: a frase de causa existe **dentro** da etapa Cronograma (`views.py:1272-1277`, `vencidos`), não na confirmação.
- Evidência no código atual: `compor_base.html:42-44` ("Rascunho salvo — {{ salvo }}." sem estado); `views.py:1255-1260` (a confirmação viaja para a etapa seguinte).
- Estado atual: **PARCIALMENTE RESOLVIDO** — a causa do caso observado (período em curso tratado como vencido) caiu; o padrão ficou.
- Ainda faz sentido?: pouco — com a régua certa, a etapa só fica pendente por Evento de fato vencido.
- Lacuna residual: confirmação não acrescenta "…e continua pendente".
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma
- Relações: `ACH-08`.
- Confiança: alta.

### ACH-08 — Período de inscrições em curso tratado como data vencida
- Origem: 16/09 §6.9, §12 QW2, §16 P2 (16/09)
- Problema original: régua pelo **início**; etapa 3 eternamente PENDENTE; gestão × portal discordavam.
- Recomendação original: olhar o término.
- Rastro posterior: `037` (FR-545/546); convergência §4 "FECHADO na validação / DESLOCADO para o painel" (`N-06`).
- Specs relacionadas: 028, 037.
- Implementação encontrada: `037`.
- Evidência no código atual: `editais/domain/calendario.py:18-47` ("Havendo término, vence quem terminou").
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não; o custo adjacente no painel é `N-06` (outro lote).
- Lacuna residual: nenhuma aqui
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `N-06`, `ACH-07`, `ACH-29`.
- Confiança: alta.

### ACH-09 · ACH-10 · ACH-36 — Marco sem explicação, 28 controles, "Consolidar" sem definição
- Origem: 16/09 §6.10, §7, §16 P2 (16/09)
- Problema original: assimetria Etapa→Edital × marco→Perfil nunca explicada; 28 controles com decisões vazias e obrigatórias sem padrão; "Consolidar" sem definição no ponto de uso.
- Recomendação original: frase de estrutura; combinação/normalização só com ≥2 Etapas; padrões 2 / meio para cima; definição de "consolidar" na distribuição.
- Rastro posterior: reavaliação 18/09 §4.2 ✅ para os três.
- Specs relacionadas: 030 (FR-413, FR-415, FR-416, FR-423).
- Implementação encontrada: `030`.
- Evidência no código atual: `compor_classificacao.html` `p.definicoes` (a Etapa pertence ao Edital, o marco ao Perfil — "Um Edital com sete Perfis tem uma Etapa e sete ordens"); `_marco.html` (ver bloco 13/09 #6); `editais/domain/marcos.py:50`; `distribuicao.html:400` (`<dfn>Consolidar</dfn>`).
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: 13/09 #6, `ACH-61`.
- Confiança: alta.

### ACH-11 — Resumo do bloco colapsado não acompanha a escolha feita na mesma página
- Origem: diário Fase B etapa 5 (16/09); §16 P3 (linha `ACH-22/37/44/11/32/24`)
- Problema original: marcar "Admite recurso" e o resumo continuar "nada declarado".
- Recomendação original: implícita.
- Rastro posterior: nenhum.
- Specs relacionadas: 030.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `_marco.html:200-202` (resumo renderizado no servidor); nenhum script em `interface/static/interface/` referencia `resumo-do-bloco`.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: pouco — o resumo se corrige ao gravar.
- Lacuna residual: resumo defasado até gravar.
- Grupo do resíduo: C
- Impacto atual: mínimo.
- Próxima ação sugerida: nenhuma
- Relações: —
- Confiança: alta.

### ACH-12 — Sem desempate por maior idade
- Origem: diário Fase B etapa 5; 16/09 §5-ter "Correção retroativa" e §16 (linha riscada) (16/09)
- Problema original: suposta ausência de desempate etário.
- Recomendação original: nenhuma — o próprio auditor o descartou (o fato tipo `Data` + "Menor valor de um fato declarado" resolve).
- Rastro posterior: —
- Specs relacionadas: 015.
- Implementação encontrada: —
- Evidência no código atual: não conferida além do registro de 16/09 (fora do recorte).
- Estado atual: **SUPERADO / OBSOLETO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: —
- Confiança: média (aceito o descarte do próprio relatório).

### ACH-13 · ACH-34 · 13/09 §6 "Definir o período de inscrições" (E2) — O período de inscrições é designado num lugar e dito em outro
- Origem: 16/09 §8, §13.5, §16 P2 (linha `ACH-13/34`); diário Fase B etapa 6 e Fase L (16/09); 13/09 §6
- Problema original: o aviso diz "Nenhum Evento… está **marcado** como período de inscrições", o que manda procurar no Cronograma; a designação é na etapa Inscrição; a Retificação edita o mesmo fato como campo Sim/Não do Evento.
- Recomendação original: validação entre fontes (13.5); na prática, dizer onde se designa.
- Rastro posterior: reavaliação 18/09 §9 intocado (`E-4`); `037` spec §fora de escopo o lista em `E-4`.
- Specs relacionadas: 009, 032 (fora de escopo), 037 (fora de escopo).
- Implementação encontrada: o "Ir para" já leva à etapa certa (`DESTINO_DA_PENDENCIA["/schedule"] → inscricao`, `views.py:665-668`, desde `f3dbc17`, 31/08).
- Evidência no código atual: `editais/domain/validation.py:1886-1893` (mensagem com "marcado"); `compor_cronograma.html`/`_evento.html` sem menção ao período de inscrições; `compor_inscricao.html:9-25` (designação); `interface/retificacao.py:110-112` (`isRegistrationPeriod`, "É o período de inscrições", BOOLEANO no Evento).
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: parcialmente — o link já corrige o destino; o que sobra é o verbo e a ausência de pista no Cronograma. A divergência de forma entre composição (escolha na etapa 6) e Retificação (Sim/Não por Evento) é aceitável: a conferência de publicação recusa dois marcados (`validation.py:1876-1883`).
- Lacuna residual: microcópia ("marcado" → "designado na etapa Inscrição") e uma linha no Cronograma.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: corrigir (microcópia)
- Relações: `E-4` (outro lote), `ACH-26`.
- Confiança: alta.

### ACH-14 · 13/09 §8 "Chave do documento" — O operador inventa um identificador técnico obrigatório
- Origem: 16/09 §10; diário Fase B etapa 6 (16/09); 13/09 §8
- Problema original: "Chave: identificação estável, sem espaços" obrigatória e manual.
- Recomendação original: derivar do nome, editável só quando preciso.
- Rastro posterior: nenhum; o estudo de esforço de 21/09 não o retoma.
- Specs relacionadas: 009, 026 (a chave é não retificável).
- Implementação encontrada: nenhuma.
- Evidência no código atual: `_documento.html:7-15` (campo `key` obrigatório, dica só `.oculto`); `retificacao.py:365-367` (a chave fica fora da Retificação: "trocá-la depois de publicado desligaria o documento do que os candidatos mandaram").
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim, em escala pequena — é obrigatório, técnico e irretificável depois de publicado, o que torna a derivação automática (com edição) mais segura que a digitação.
- Lacuna residual: derivar a chave do nome no fragmento novo.
- Grupo do resíduo: C
- Impacto atual: baixo por Edital; multiplica com 9 documentos por modalidade (estudo de esforço §5).
- Próxima ação sugerida: corrigir (pequeno)
- Relações: estudo de esforço (volume de documentos).
- Confiança: alta.

### ACH-16 — `Peso (opcional)` que vira impeditivo
- Origem: 16/09 §6.10, §9 item 1, §16 P1 (16/09)
- Problema original: rótulo "(opcional)" falso quando a Etapa é enumerada; contradição só na etapa 9.
- Recomendação original: deixar de ser "(opcional)"; pedir o peso quando a Etapa é enumerada.
- Rastro posterior: `037`; `D-G4` (reavaliação §14-bis): o peso continua da Etapa, e a pergunta se encerra.
- Specs relacionadas: 037 (D-003), D-G4.
- Implementação encontrada: `037`.
- Evidência no código atual: `_etapa.html:141-155` (rótulo "(opcional até um marco enumerar esta Etapa)"); `_marco.html:140-143` (aviso "Sem peso declarado: …" no cartão, no momento de enumerar); `views.py:687-689` (roteamento por código).
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `D-G4`, 13/09 QW2.
- Confiança: alta.

### ACH-17 · 13/09 QW11 — Precisão interna vazando (`40.0000`, `78,0000 ≥ 40,0000`)
- Origem: 16/09 §12 QW6, §16 P3; diário Fase B e Fase H (16/09); 13/09 §10 QW11
- Problema original: nota mínima reexibida como `40.0000`; motivo ao candidato com quatro casas enquanto a lista pública usa duas.
- Recomendação original: formatar com as casas declaradas em toda parte.
- Rastro posterior: `4925827` uniformizou a nota **no acompanhamento e na relação pública** (13/09 QW11); o motivo e o formulário ficaram.
- Specs relacionadas: 012, 013, 017.
- Implementação encontrada: filtro `pontuacao` (`interface/templatetags/interface_extras.py:132-147`) aplicado em parte das telas.
- Evidência no código atual: `resultados/domain/regra.py:41-43` — `_numero` "quatro casas, vírgula decimal", usado na frase do motivo (`:116`, `:122`) que chega ao candidato; `interface/forms.py:1268-1277` — `f"{etapa.minimum_score:f}"` reexibe `40.0000` no formulário.
- Estado atual: **PARCIALMENTE RESOLVIDO**
- Ainda faz sentido?: sim, cosmético — mas o motivo é texto que o candidato lê e cita em recurso.
- Lacuna residual: motivo da consolidação e reexibição do formulário com quatro casas.
- Grupo do resíduo: C
- Impacto atual: baixo (se o motivo for gravado no Resultado, só resultados novos mudam — não conferido).
- Próxima ação sugerida: corrigir
- Relações: —
- Confiança: alta para o código; média sobre onde o motivo é persistido.

### ACH-18 · ACH-33 — Numeração das seções: composição × documento × Retificação
- Origem: 16/09 §9 item 5, §13.5, §16 P2 (linha `ACH-18/33`); diário Fase B (prévia) e Fase L (16/09)
- Problema original: a composição numera 1–12 pela ordem do catálogo; o PDF numera na materialização (preâmbulo sem número, seções vazias omitidas); a Retificação diz "Seção 8 — …" pela ordem da composição.
- Recomendação original: a numeração exibida na composição passa a ser a do documento.
- Rastro posterior: reavaliação 18/09 §9 intocado (`E-4`); 032 e 037 fora de escopo.
- Specs relacionadas: 004/005 (seções), 032, 037.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `compor_conteudo.html:19` (`{{ secao.order }}. {{ secao.title }}`); `interface/retificacao.py:1007-1022` (`f"Seção {order} — {title}"`); `publicacoes/infrastructure/pdf.py:2095-2125` — preâmbulo sem número e `enumerate(numeraveis, 1)`: "O número é da materialização: ele não existe no conteúdo homologado".
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: parcialmente — a Retificação pública nomeia a seção pelo título (`publicacoes/domain/alteracoes.py`, coleção `sections` → "Seção", `title`), então o risco de endereçar a seção errada é de conversa entre pessoas, não de ato.
- Lacuna residual: número diferente para a mesma seção em três telas.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma (ou retirar o número das telas internas, que é mais barato que calculá-lo)
- Relações: `E-4` (outro lote).
- Confiança: alta.

### ACH-19 — A tela do Edital, antes de homologar, não menciona a segregação
- Origem: 16/09 §5 #10 (resíduo); diário Fase C (16/09)
- Problema original: "O próximo ato é seu: homologar" sem dizer que homologar consome a publicação para essa pessoa.
- Recomendação original: avisar em "Homologar" (feito na página do ato) — sobra o cartão do Edital.
- Rastro posterior: nenhum.
- Specs relacionadas: 001 (FR-021), 002 (FR-028).
- Implementação encontrada: aviso na página de confirmação do ato.
- Evidência no código atual: `interface/views.py:2962` (aviso só quando `ato.chave == "homologar"`, na confirmação); `interface/acoes.py:297-313` — em `EM_REVISAO` a observação é sempre `""`; a de segregação só existe para `HOMOLOGADO`.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: pouco — o aviso chega antes do ato irreversível, que era o que importava; em equipe de 2–3 pessoas o acúmulo é o caso comum e o aviso no cartão seria lido todo dia.
- Lacuna residual: frase no cartão.
- Grupo do resíduo: C
- Impacto atual: mínimo.
- Próxima ação sugerida: nenhuma
- Relações: 13/09 #10, `ACH-28`.
- Confiança: alta.

### ACH-20 — "A vigência é da versão consolidada, que não tem documento próprio" (densidade)
- Origem: diário Fase C (16/09); sem linha no §16
- Problema original: frase precisa e difícil.
- Recomendação original: nenhuma (classificado D1/D2).
- Rastro posterior: —
- Specs relacionadas: 002 (FR-002), 004.
- Implementação encontrada: a frase é deliberada.
- Evidência no código atual: `detalhe.html:130-132`; `interface/views.py:2750-2757` (docstring de `_documentos_publicados`: "Nenhum é apresentado como vigente, e a omissão é a parte que importa").
- Estado atual: **SUPERADO / OBSOLETO** — observação sem recomendação, sobre decisão registrada.
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: —
- Confiança: alta.

### ACH-21 — Atribuições viram parágrafo e Requisitos viram lista, e isso só se vê no documento
- Origem: 16/09 §9 item 4, §16 P3 (linha `ACH-21/23`); diário Fase D (16/09)
- Problema original: microcópias diferentes produzem formatos diferentes, descobertos no PDF publicado.
- Recomendação original: "prévia + link".
- Rastro posterior: nenhum.
- Specs relacionadas: 024, 026.
- Implementação encontrada: a prévia do PDF existia já em 16/09 (PP-17); os `placeholder` dizem a convenção.
- Evidência no código atual: `_perfil.html:66-80` (`placeholder="Uma linha em branco separa parágrafos"` / `"Um requisito por linha"`); `interface/views.py:2702-2746` (prévia como tela e PDF).
- Estado atual: **NÃO IMPLEMENTADO** (nada mudou; a mitigação já existia)
- Ainda faz sentido?: pouco — os dois formatos são deliberados e o `placeholder` diz cada um; e os requisitos passaram a ser retificáveis (`retificacao.py:63-67`), de modo que o erro não é mais irrecuperável.
- Lacuna residual: nenhuma relevante.
- Grupo do resíduo: C
- Impacto atual: mínimo.
- Próxima ação sugerida: nenhuma
- Relações: anexo §16 (requisitos retificáveis).
- Confiança: alta.

### ACH-22 — Depois de se identificar, a candidata precisa clicar "Inscrever-se" de novo
- Origem: 16/09 §16 P3 (linha `ACH-22/37/…`); diário Fase D (16/09)
- Problema original: a intenção original não é retomada sozinha.
- Recomendação original: retomar a intenção.
- Rastro posterior: `4925827` (16/09, antes do baseline da reauditoria) tirou o interstício e registrou por que o clique fica.
- Specs relacionadas: 009 (o `inscrever` é POST).
- Implementação encontrada: volta à página da vaga, com a vaga à vista.
- Evidência no código atual: `portal/views.py:711-736` — "**O clique não sumiu, e não podia sumir.** Abrir rascunho cria registro e pratica ato auditado… executar o destino sozinho… faria um endereço `?destino=…` compartilhado criar inscrição em nome de quem apenas se identificou".
- Estado atual: **NÃO IMPLEMENTADO** — por decisão de segurança registrada no código (anterior ao achado, que não a considerou).
- Ainda faz sentido?: não — a recomendação criaria um vetor de ato em nome de terceiro.
- Lacuna residual: nenhuma que se recomende.
- Grupo do resíduo: —
- Impacto atual: um clique.
- Próxima ação sugerida: nenhuma
- Relações: 13/09 §8 "interstício Tudo certo".
- Confiança: alta.

### ACH-23 — A declaração "li o Edital" não linka o Edital
- Origem: 16/09 §16 P3 (linha `ACH-21/23`); diário Fase D (16/09)
- Problema original: declara-se a leitura de um documento que não está ao alcance.
- Recomendação original: link ao Edital junto da declaração.
- Rastro posterior: nenhum.
- Specs relacionadas: 009 (FR-057).
- Implementação encontrada: link ao Edital vigente só quando ele mudou desde o início (`revisao.html:34-37`); resumo de declarações faltantes no topo (`:20`).
- Evidência no código atual: `portal/templates/portal/revisao.html:164-169` (label sem link).
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim, barato — é a declaração que dá fundamento à adesão, e o Edital está a um link.
- Lacuna residual: link ao PDF da versão que será aceita.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: corrigir
- Relações: —
- Confiança: alta.

### ACH-24 — "Este comprovante fica disponível enquanto as inscrições… estiverem sob análise"
- Origem: diário Fase D ("a verificar"); §16 P3 (16/09)
- Problema original: a frase sugere indisponibilidade futura de um documento que o candidato pode precisar depois.
- Recomendação original: verificar.
- Rastro posterior: nenhum.
- Specs relacionadas: 009/010.
- Implementação encontrada: nenhuma regra de expurgo encontrada nos módulos de inscrição/portal (varredura por "retenção/expurgo" sem resultado).
- Evidência no código atual: `portal/templates/portal/comprovante.html:139-140` (frase inalterada).
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim, como verificação — se não há regra que tire o comprovante do ar, a frase promete uma limitação que o sistema não tem (ou antecipa uma política de guarda que não está escrita).
- Lacuna residual: frase sem regra correspondente.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: validar (política de guarda) e corrigir a frase
- Relações: —
- Confiança: média — a ausência de regra foi inferida por busca.

### ACH-25 — "O que fazer agora" some quando o Processo fica vivo
- Origem: 16/09 §11 `E-6`, §13.6, §16 P2; diário Fase E (16/09)
- Problema original: publicado o Edital, o painel oferece só Encerrar e Cancelar.
- Recomendação original: painel de condução do Processo vivo.
- Rastro posterior: `038`; convergência 20/09 §4 e §6 **PARCIAL** (`N-01`…`N-04`), §12; `4ec1cbb` fecha `N-03`.
- Specs relacionadas: 038.
- Implementação encontrada: painel (Pulso) na tela do Processo.
- Evidência no código atual: `processo_detalhe.html:64,111` (pulso e próximos marcos); `interface/supervisao.py` (sinais `UX-001`…`UX-066`).
- Estado atual: **DUPLICADO / ABSORVIDO** — em `N-01`…`N-04` (convergência de 20/09), outro lote.
- Ainda faz sentido?: —
- Lacuna residual: ver `N-01`…`N-04`.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma aqui
- Relações: `E-6`, 13/09 §9.7, 11.3.
- Confiança: média — checagem pontual.

### ACH-26 — O término das inscrições governa quando a avaliação pode começar, e isso não é dito no Cronograma
- Origem: 16/09 §9 item 2, §16 P2 (16/09)
- Problema original: dependência descoberta na distribuição, com o Edital publicado.
- Recomendação original: validação entre fontes (13.5) / dizer no ponto da decisão.
- Rastro posterior: `037` spec lista `ACH-26` fora de escopo (`E-4`).
- Specs relacionadas: 012, 037.
- Implementação encontrada: o bloqueio na distribuição é anunciado antes e diz as saídas (`888b3da`).
- Evidência no código atual: `compor_cronograma.html`, `_evento.html`, `compor_inscricao.html` sem menção a avaliação/distribuição.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: pouco — no certame real a avaliação começa depois do fim das inscrições; o caso do percurso foi provocado para antecipar a avaliação. A tela que bloqueia já diz a saída.
- Lacuna residual: uma frase no Evento designado como período de inscrições.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma
- Relações: `E-4`, `ACH-13`.
- Confiança: alta.

### ACH-27 · 13/09 #8 (contadores) · P3 "Contadores redundantes" — Oito contadores concorrentes na distribuição
- Origem: 16/09 §10, §16 P2; diário Fase E (16/09); 13/09 §4.8
- Problema original: contadores sobrepostos e de nomes quase sinônimos.
- Recomendação original: colapsar em cobertura e conclusão.
- Rastro posterior: reavaliação §3 intocado; convergência §4 **PARCIAL / DESLOCADO** e `N-07` (um mosaico contradiz a lista).
- Specs relacionadas: 012, 013, 038 (fora de escopo).
- Implementação encontrada: os números passaram a fechar por soma (comentário `distribuicao.html:62-70`).
- Evidência no código atual: `distribuicao.html:62-70`.
- Estado atual: **DUPLICADO / ABSORVIDO** — em `N-07` (convergência §12), outro lote.
- Ainda faz sentido?: —
- Lacuna residual: ver `N-07`.
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma aqui
- Relações: `N-07`.
- Confiança: média — checagem pontual.

### ACH-28 — "Você não poderá publicar este Edital" continua exibido depois de publicado
- Origem: 16/09 §16 P3 (linha `ACH-28/29`); diário Fase L (16/09)
- Problema original: aviso de segregação obsoleto num Edital `Publicado`.
- Recomendação original: limpar por estado.
- Rastro posterior: nenhum.
- Specs relacionadas: 001 (FR-021), 002.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `publicacoes/application/selectors.py:267-272` — `impede_por_segregacao` não olha a situação do Edital; `interface/views.py:2788,2803` a passa sempre; `detalhe.html:58-62` a exibe com `{% if impedido_por_segregacao %}`, sem condição de estado. Para quem elaborou **e** homologou, o aviso "Você não poderá publicar… Peça a alguém… que conclua o ato" fica em toda tela do Edital publicado, retificado ou encerrado.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim — é afirmação falsa, e numa equipe de 2–3 pessoas (memória do projeto: papéis acumulados) quem elabora e homologa é justamente o operador mais frequente.
- Lacuna residual: condicionar o aviso a `HOMOLOGADO` (é o único estado em que ele é verdade).
- Grupo do resíduo: C (alta frequência, custo de uma condição)
- Impacto atual: baixo-médio — ruído que ensina a desconfiar dos avisos.
- Próxima ação sugerida: corrigir
- Relações: `ACH-29`/NOVO-1 (mesma família: validação da publicação lida depois da publicação), `ACH-19`.
- Confiança: alta.

### ACH-29 — Avisos da validação de publicação persistem depois da publicação
- Origem: 16/09 §16 P3 (linha `ACH-28/29`); diário Fase L (16/09)
- Problema original: o AVISO "o Evento … já passou" continuava depois de publicado.
- Recomendação original: limpar por estado.
- Rastro posterior: `028` já dizia que as verificações de cronograma "valem só no ato de publicação" (`validation.py:1900-1911`) — e é exatamente o ato que a tela do Edital simula sempre.
- Specs relacionadas: 002 (FR-008/FR-027), 028.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `interface/views.py:2787` chama `_pendencias(edital)` para **qualquer** situação; `_pendencias` usa `validate_for_publication(snapshot, ato=ATO_DE_PUBLICACAO, agora=agora)` (`views.py:845-847`) sobre `edital_snapshot(edital)` — o relacional, que depois de Retificação é o do dia da publicação (memória "Retificação não reescreve o relacional"); `detalhe.html:168-180` exibe "Validação do conteúdo" com `{% if pendencias %}`. Consequência lida no código (não percorrida): depois do fim das inscrições, um Edital publicado passa a exibir **"Impede — O período de inscrições encerrou em …. Publicado assim, o Edital não receberá inscrição alguma — corrija a data do Evento na etapa Cronograma antes de publicar"** (`validation.py:2093-2100`), mais um AVISO por Evento vencido.
- Estado atual: **NÃO IMPLEMENTADO** — e a classe cresceu desde 16/09 com os impeditivos de executabilidade e de cronograma, todos lidos no instante de agora.
- Ainda faz sentido?: sim.
- Lacuna residual: a tela do Edital publicado roda a conferência de publicação; deveria mostrá-la só nos estados em que ainda há publicação a fazer (ou rodar a do ato de Retificação).
- Grupo do resíduo: B
- Impacto atual: médio — todo Edital publicado cujo prazo de inscrição acabou passa a "impedir" e mandar corrigir o que não se corrige; confunde exatamente o gestor que conduz o Processo vivo.
- Próxima ação sugerida: validar pela interface (um Edital publicado com inscrições encerradas) e corrigir
- Relações: `ACH-28`, `N-08` (avisos da validação não chegam ao painel — o inverso, outro lote), NOVO-1.
- Confiança: média-alta — cadeia lida de ponta a ponta; não executada.

### ACH-30 — Gestor diante do Edital publicado: "Correções ocorrem por Retificação", sem ação nem a quem pedir
- Origem: 16/09 §6.6, §12 QW1, §16 P1 (16/09)
- Problema original: a frase parava no bloqueio.
- Recomendação original: "Peça a alguém com a permissão de retificar".
- Rastro posterior: `037` (FR-541, FR-541a/b/c); convergência §9 E0.
- Specs relacionadas: 037.
- Implementação encontrada: `037`.
- Evidência no código atual: `detalhe.html:64-82` + `interface/views.py:2804-2815` (`conducao_do_imutavel` só quando `not acoes.pode_retificar`), `views.py:4359-4361` (`CONDUCAO_DA_RETIFICACAO`).
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `ACH-02`, `ACH-38`.
- Confiança: alta.

### ACH-31 — Tela do ato de Retificação ainda mostra o caminho normativo e `REPLACE`
- Origem: 16/09 §5 #7, §6.8, §11 `E-3`, §13.4, §16 P1 (linha `ACH-39/31/45`); diário Fase L (16/09)
- Problema original: na tela da Retificação criada, `/schedule/id=…/endAt` e `REPLACE`, enquanto a prévia e o público eram legíveis.
- Recomendação original: renderizador normativo único, com o identificador **ao lado**.
- Rastro posterior: reavaliação §9 intocado; longitudinal 21/09 item 5: "as telas internas já não mostram caminho cru… o quick win 7 não se aplica… o conserto é **uma tabela**, não um renderizador".
- Specs relacionadas: 004, 020, 024.
- Implementação encontrada: o "onde/campo" em português já existia em 16/09 (`5c6da90`); nada mudou depois.
- Evidência no código atual: `retificacao_detalhe.html:53-78` — coluna "Onde" com entidade e campo em português **e** `<code>{{ item.caminho }}</code>` embaixo; coluna "Operação" com `alteracao.operation` cru (`interface/views.py:3482`, `:3538`, `:3552`) → `REPLACE`/`ADD`/`REMOVE`. A tela de **publicar** (`retificacao_confirmar.html:42-62`) não tem coluna de operação. O vocabulário legível já existe: `publicacoes/domain/alteracoes.py:23` (`OPERACOES = {"ADD": "acrescentado", "REPLACE": "alterado", "REMOVE": "removido"}`) e é usado na trilha (`views.py:3870`, `:7237`).
- Estado atual: **PARCIALMENTE RESOLVIDO**
- Ainda faz sentido?: parcialmente — o caminho em segundo plano atende a recomendação ("identificador ao lado"); `REPLACE` é o único vazamento, e o tradutor está a um import.
- Lacuna residual: traduzir a operação na tela de detalhe da Retificação.
- Grupo do resíduo: C
- Impacto atual: baixo (tela de quem homologa; a de quem assina já está limpa).
- Próxima ação sugerida: corrigir (uma linha, reusando `OPERACOES`)
- Relações: `E-3` (duas tabelas de vocabulário, outro lote), 13/09 #7.
- Confiança: alta.

### ACH-32 — A tela de Retificação expõe o bloco inteiro do sorteio num marco que não sorteia, com identificadores de máquina como opção
- Origem: 16/09 §5 ("complexidade nova"), §10, §12 QW4, §16 P3 (16/09)
- Problema original: dez campos de método em todo marco, com `DIGITOS_EM_SEQUENCIA`, `OCORRENCIA_SEGUINTE_DA_MESMA_FONTE` etc. visíveis.
- Recomendação original: não renderizar o bloco para marco que não sorteia.
- Rastro posterior: nenhum.
- Specs relacionadas: 021, 026 (FR-313), 030 (forma da ordem), 035 (FR-507).
- Implementação encontrada: o bloco é oferecido **sempre, por decisão**: `interface/retificacao.py:861-873` ("Sempre, e não só quando o marco já sorteia (026, FR-313, corrigido na segunda revisão do PR #114)… todo Edital publicado antes do degrau 10 carrega `drawMethod` nulo, e é por Retificação que ele passa a declarar o método").
- Evidência no código atual: acima; opções com o identificador como rótulo em `interface/forms.py:320-325` (`tuple((nome, nome) …)`), enquanto a composição usa frases (`_marco.html:365-366`, `:391`).
- Estado atual: **NÃO IMPLEMENTADO** — metade por decisão anterior ao achado (FR-313), metade por omissão.
- Ainda faz sentido?: parcialmente. Ocultar contraria a FR-313 para o acervo sem forma da ordem; mas desde a `030` o marco que declara `orderProduction = POR_PONTUACAO` diz que não sorteia, e ali o bloco é ruído puro. E os rótulos da Retificação podem usar as frases que a composição já usa.
- Lacuna residual: condicionar o bloco à forma da ordem quando ela existe; rótulos humanos nas opções.
- Grupo do resíduo: C
- Impacto atual: baixo (ruído numa tela longa).
- Próxima ação sugerida: corrigir (pequeno), respeitando a FR-313 para o acervo
- Relações: anexo §16, `ACH-51`/`ACH-55` (outro lote).
- Confiança: alta.

### ACH-35 — Negativa por vínculo vira 404 mudo
- Origem: 16/09 §6.7, §13.3, §16 P1; diário Fase F (16/09)
- Problema original: a URL da distribuição devolvia 404 a quem não tinha vínculo.
- Recomendação original: recusa nomeada onde a negativa é de vínculo.
- Rastro posterior: `033` (`require_authorization_base`); reavaliação §6/§8 — as **sete** recusas fora das portas seguem em 404; `D-G2` (19/09) decidiu 403 para três delas; convergência §11 mediu que continuam 404.
- Specs relacionadas: 033, D-G2.
- Implementação encontrada: `033`.
- Evidência no código atual: `seguranca/application/authorization.py:124` (`require_authorization_base`); usos em `interface/views.py:306, 4404, 4652, 5631, 6857, 7165`.
- Estado atual: **RESOLVIDO** (na porta observada); o resíduo é `D-G2`.
- Ainda faz sentido?: —
- Lacuna residual: `criar_edital`, `reaproveitar`, `supervisao` ainda 404 (outro lote, `D-G2`).
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma aqui
- Relações: `D-G2`, `N-03` (fechado em `4ec1cbb`), 13/09 §12 último item (a postura "não detalhar o 404" foi substituída pela fronteira 403/404 da `D-G2`).
- Confiança: alta.

### ACH-37 — "Consultar ato e proveniência" anuncia consulta onde mora a divulgação
- Origem: 16/09 §12 QW7, §16 P3; diário Fase G (16/09); 13/09 §9.8
- Problema original: o rótulo não sugere a ação de publicar.
- Recomendação original: trocar o rótulo.
- Rastro posterior: `033` acrescentou o destino "divulgar o resultado" na tela do Edital.
- Specs relacionadas: 017 (SC-002), 033.
- Implementação encontrada: caminho alternativo; o rótulo ficou.
- Evidência no código atual: `ordenacao.html:66` (link "Consultar ato e proveniência") e `:103-116` ("A divulgação é ato do próprio ato emitido, e sai de lá — em *Consultar ato e proveniência*"); `interface/views.py:2872-2883` ("divulgar o resultado" → prévia de publicação).
- Estado atual: **PARCIALMENTE RESOLVIDO**
- Ainda faz sentido?: parcialmente — quem tem a permissão chega pela tela do Edital; quem está no marco continua lendo um convite a consultar.
- Lacuna residual: rótulo/link direto à prévia no aviso do marco quando `pode_divulgar`.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: corrigir (microcópia)
- Relações: 13/09 QW7, `ACH-40`.
- Confiança: alta.

### ACH-38 — Presidência mandada divulgar encontra "Você não tem ação disponível" sem o "peça a alguém"
- Origem: 16/09 §6.6, §16 P1; diário Fase G (16/09)
- Problema original: beco sem condução.
- Recomendação original: generalizar "peça a alguém com a permissão de publicar".
- Rastro posterior: `033` (reavaliação §6 ✅).
- Specs relacionadas: 033.
- Implementação encontrada: `033`.
- Evidência no código atual: `ato_ordenacao.html:46-52` ("Peça a alguém com a permissão de publicar resultado que…"); `ordenacao.html:66`, `:105-116`.
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `ACH-02`, `ACH-30`, `ACH-40`.
- Confiança: alta.

### ACH-39 — "Ato de classificação": a tabela dos resultados que entraram na ordem é só UUID
- Origem: 16/09 §6.8, §12 QW9, §16 P1 (linha `ACH-39/31/45`); diário Fase G (16/09)
- Problema original: título com UUID; proveniência em UUID; tabela com quatro colunas de UUID e nenhum nome; desempate como `MAIOR_PONTUACAO_NA_ETAPA · e8e3…`.
- Recomendação original: uma coluna legível (nome do participante) ao lado dos identificadores.
- Rastro posterior: reavaliação §9 intocado; `E-3` aberto.
- Specs relacionadas: 015, 017 (E2E15-006).
- Implementação encontrada: parte já existia antes de 16/09 (`abd701a`, `120b19c`, 06/09): a proveniência traz nome ao lado do UUID e a tabela de posições traz protocolo + nome; o desempate imprime o rótulo com o tipo em segundo plano.
- Evidência no código atual: `ato_ordenacao.html:60-66` (nome + UUID em `.ajuda`), `:84` (protocolo — nome), `:91` (rótulo do critério); **mas** `:69-73` — "Resultados que entraram na ordem" continua com `item.id`, `item.registrationId`, `item.stageId`, `item.versionId` e nenhum nome; migalha `:7` "Ato {{ ato.id }}".
- Estado atual: **NÃO IMPLEMENTADO** (a parte recomendada — coluna legível nessa tabela — não mudou; o resto do achado já estava resolvido em 16/09, e o relatório o superestimou)
- Ainda faz sentido?: parcialmente — é tela de auditoria e resposta a recurso; nome da Etapa e do participante são o que quem responde procura.
- Lacuna residual: nome do participante e da Etapa na tabela dos resultados antecedentes.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: corrigir (pequeno)
- Relações: `E-3`, `ACH-45`.
- Confiança: alta.

### ACH-40 — Quem pode publicar o resultado não tem caminho até a ação
- Origem: 16/09 §6.2, §13.3, §16 P0; diário Fase G e Fase 2 (d) (16/09)
- Problema original: Publicador puro sem bloco "Classificação" e com 404 no ato.
- Recomendação original: a tela do Edital lista marcos e atos para quem tem `resultado:publicar`.
- Rastro posterior: `033`; reavaliação §6 ✅; convergência §9 (E0, sinal `UX-066`).
- Specs relacionadas: 033 (FR-473, FR-476).
- Implementação encontrada: `033`.
- Evidência no código atual: `interface/views.py:2822-2883` (`_destinos_do_marco` "por destino"; "divulgar o resultado" para cada ato vigente), `detalhe.html:150-172`.
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma aqui (o publicador ver "nenhuma condição de atenção" é `N-01`, outro lote).
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `ACH-37`, `ACH-38`, `N-01`.
- Confiança: alta.

### ACH-41 — Duas datas-limite contraditórias para o mesmo recurso
- Origem: 16/09 §6.5, §11 `E-4`, §13.5, §16 P1; diário Fase H (16/09)
- Problema original: janela do marco (18/09) × Evento "Prazo para recursos" do Cronograma (06–07/10) na mesma tela do candidato, sem confronto.
- Recomendação original: validação que confronte janela declarada × Evento de recurso; AVISO na publicação do resultado.
- Rastro posterior: reavaliação §9 intocado; `036` spec §fora de escopo ("vizinho desta feature"); varredura dos dezessete (19/09) aponta `E-4` como a próxima; convergência §4 `E-4` ABERTO.
- Specs relacionadas: 026, 032, 036 e 037 (fora de escopo).
- Implementação encontrada: nenhuma.
- Evidência no código atual: `editais/domain/validation.py:1497-1533` (`_coerencia_da_janela_recursal` confere só a forma da janela); o Evento do Cronograma não tem espécie "recurso" computável — o tipo é texto livre (`CAMPOS_EVENTO` não oferece `type`, e a Retificação o declara não retificável, `retificacao.py:1114`); `portal/templates/portal/acompanhamento.html:160` (a data do marco) convive com o Cronograma na mesma página.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim — a tempestividade é calculada pela janela do marco (`recursos/application/selectors.py`, `_tempestividade`), e quem confiar no Cronograma perde o prazo. Mas o confronto exige primeiro saber qual Evento é o de recurso, e hoje isso não é dado.
- Lacuna residual: confronto janela × Evento (ou derivar o Evento de recurso da janela), e aviso na publicação do resultado.
- Grupo do resíduo: B
- Impacto atual: médio quando ocorre (prazo perdido); frequência depende de como os Editais declaram o Cronograma.
- Próxima ação sugerida: criar spec (é a `E-4`, do outro lote — aqui só a confirmação)
- Relações: `E-4`, 13/09 QW12.
- Confiança: alta.

### ACH-42 — O parecer não chega ao candidato
- Origem: 16/09 §6.4, §13.2, §16 P1; diário Fase H e Fase 2 (c) (16/09)
- Problema original: o portal não exibia o parecer, contra a razão que a 012 deu para exigi-lo.
- Recomendação original: exibir o parecer ao titular quando o resultado lhe for desfavorável e houver prazo recursal.
- Rastro posterior: `036` (FR-524, FR-525, FR-525a); convergência §4 FECHADO.
- Specs relacionadas: 012, 036.
- Implementação encontrada: `036`.
- Evidência no código atual: `portal/templates/portal/acompanhamento.html:57-115` — "O parecer, ao lado do motivo e não no lugar dele"; estados encerrado/ausente dizem por quê; só resultado desfavorável; parecer de terceiro continua proibido (`:60-70`).
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `ACH-43`.
- Confiança: alta.

### ACH-43 · 13/09 #5 (contexto) — O julgador decide sem poder ver a prova
- Origem: 16/09 §6.3, §13.2, §14, §16 P0; diário Fase I e Fase 2 (b) (16/09)
- Problema original: `recurso:julgar` não dá acesso ao parecer nem aos documentos (FR-105 da 018, deliberado); nenhum ato de instrução.
- Recomendação original: ato de instrução com escopo por recurso, registrado na auditoria; **não** ampliar o papel.
- Rastro posterior: `036`; reavaliação §14 "os seis P0 fecham".
- Specs relacionadas: 018 (FR-102, FR-105), 036 (FR-527, FR-532).
- Implementação encontrada: `036`.
- Evidência no código atual: `interface/templates/interface/recurso.html:84-175` (bloco "Instrução do recurso": parecer e documentos anexados por instrução, alcance que termina, "nada foi apagado"; formulário `interface:recurso-instruir`; a quem pedir quando nada foi instruído); `auditoria/selectors.py:110-120` (a instrução entra na trilha do Edital).
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma aqui. (O "recurso sem campo de anexo" da convergência §4 é do **candidato** — outro achado, outro lote.)
- Grupo do resíduo: —
- Impacto atual: —
- Próxima ação sugerida: nenhuma
- Relações: `ACH-42`, 13/09 #5.
- Confiança: alta.

### ACH-44 — "o meu resultado da Análise Curricular" nas telas administrativas
- Origem: 16/09 §12 QW10, §16 P3; diário Fase I (16/09)
- Problema original: objeto do recurso em primeira pessoa do candidato na listagem e na tela do julgador.
- Recomendação original: terceira pessoa nas telas administrativas.
- Rastro posterior: nenhum.
- Specs relacionadas: 018.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `recursos/application/selectors.py:113-130` (`_objeto` → `f"o meu resultado da {nome}"`), usado em `resumo` (titular, `:75`), **e** em `_linha` (listagem da gestão, `:215`) e `proveniencia` (tela do julgador, `:258`); `recurso.html:12` e `:32` o imprimem.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim — é a mesma frase servindo a dois leitores; separar é trivial.
- Lacuna residual: variante em terceira pessoa para `_linha` e `proveniencia`.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: corrigir
- Relações: `ACH-45`.
- Confiança: alta.

### ACH-45 — `INTERPOSTO POR: cand:…` e UUIDs nus na tela do recurso
- Origem: 16/09 §6.8, §16 P1 (linha `ACH-39/31/45`); diário Fase I (16/09)
- Problema original: sujeito técnico no lugar do nome; identidade do objeto e versão citada como UUID.
- Recomendação original: nome ao lado do identificador.
- Rastro posterior: convergência 20/09 `N-09` (S1) — "identificador interno na cara de quem julga"; `achado-do-ach-02.md` o põe na mesma família do codename.
- Specs relacionadas: 018 (FR-092).
- Implementação encontrada: nenhuma.
- Evidência no código atual: `recurso.html:27` (`proveniencia.interposto_por` = `peca.interposto_por`, `recursos/application/selectors.py:255`), `:33` (identidade do objeto), `:35` e `:37` (UUIDs do ato e da versão). O nome da inscrição está na linha seguinte (`:28`).
- Estado atual: **DUPLICADO / ABSORVIDO** — em `N-09` (convergência de 20/09); estado confirmado aqui: inalterado.
- Ainda faz sentido?: parcialmente — a FR-092 quer os identificadores para a auditoria; falta só o rótulo legível ao lado (ou em primeiro plano).
- Lacuna residual: ver `N-09`.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: corrigir junto com `ACH-44` e `ACH-39`
- Relações: `N-09`, `ACH-39`, `ACH-44`, `E-3`.
- Confiança: alta.

Nota ao bloco 13/09 QW12: a `017` **admite** e não obriga a apresentação do prazo na página pública
(`specs/017-*/spec.md` FR-055: "Se a versão citada declarar prazo recursal, a informação normativa
existente **pode** ser apresentada") — por isso B, e não A.

---

## (1) Tabela-resumo

| ID | Título | Estado | Grupo | Próxima ação |
|---|---|---|---|---|
| 13/09 #1 · 11.1 | Vagas imediatas × linha do quadro | RESOLVIDO | — | nenhuma |
| 13/09 #2 | Reaproveitamento publica cronograma vencido | RESOLVIDO | — | nenhuma |
| 13/09 #3 · QW1 | Microcópia invisível (`.oculto`) | RESOLVIDO POR OUTRO CAMINHO | — | nenhuma |
| 13/09 #4 · 11.4 | Segundo Edital no Processo | RESOLVIDO | — | nenhuma |
| 13/09 #5 · QW6 | Julgador sem porta nem contexto | RESOLVIDO | — | nenhuma |
| 13/09 #6 · 11.2 | Classificação com 30 decisões | RESOLVIDO | — (C menor) | nenhuma |
| 13/09 #7 · QW9 · 11.5 | Retificação em JSON Pointer/UTC | RESOLVIDO POR OUTRO CAMINHO | — | nenhuma |
| 13/09 #8 | "Impedimento" com dois sentidos | RESOLVIDO | — | nenhuma |
| 13/09 #9 | Atos operacionais em um clique (resta "Remover da comissão") | PARCIALMENTE RESOLVIDO | C | corrigir |
| 13/09 #10 | Bloqueios que chegam tarde | RESOLVIDO | — | nenhuma |
| 13/09 §9.6 · §16 | Alcance da Retificação sem decisão | RESOLVIDO | — | nenhuma |
| 13/09 QW2 · §9.4 | Pendência de marco roteada errado | RESOLVIDO | — | nenhuma |
| 13/09 QW3/4/5/8 | Tokens em inglês, navegação Anexos, link do Edital, texto obsoleto | RESOLVIDO | — | nenhuma |
| 13/09 QW7 · §9.8 | Publicar resultado numa tela de auditoria | RESOLVIDO POR OUTRO CAMINHO | — | nenhuma |
| 13/09 QW10 | "Ativar Processo" | RESOLVIDO POR OUTRO CAMINHO | — | nenhuma |
| 13/09 QW12 | Prazo recursal fora da página pública do resultado | PARCIALMENTE RESOLVIDO | B | criar spec curta |
| 13/09 QW13 | E-mail com "Concorrência:" vazio | NÃO IMPLEMENTADO | C | corrigir |
| 13/09 P2/P3 (seis) | Nome na distribuição, parecer, Mesa→Edital, empate residual, prosa de projeto, interstício | RESOLVIDO | — | nenhuma |
| 13/09 P2 | Candidato não vê vagas por modalidade | NÃO IMPLEMENTADO | B | criar spec curta |
| 13/09 §5/§8/P3 | Colisões de vocabulário (Etapa, marco, providência a jusante, coluna Modalidade) | NÃO IMPLEMENTADO | C | nenhuma isolada |
| 13/09 §5 | Ampla concorrência com três nomes | DUPLICADO / ABSORVIDO (`E-4`, `ACH-54`) | — | outro lote |
| 13/09 §9.7 · 11.3 · P2/P3 | Visão global, "Meu trabalho", trilha única | DUPLICADO / ABSORVIDO (`ACH-25`, `N-01`…`N-04`) | — | outro lote |
| ACH-01 | Raiz pública sem caminho para a gestão | NÃO IMPLEMENTADO | C | nenhuma |
| ACH-02 | Gestor sem "a quem pedir" | RESOLVIDO | — (C menor) | nenhuma |
| ACH-03 · ACH-15 | Selos que contradizem a etapa (Anexos) | PARCIALMENTE RESOLVIDO | C | corrigir |
| ACH-04 | Explicação distante do campo (Perfis) | PARCIALMENTE RESOLVIDO | C | validar intenção da FR-426 |
| ACH-05 | Decisões prematuras no Perfil | PARCIALMENTE RESOLVIDO | — | nenhuma |
| ACH-06 | `name` em inglês | SUPERADO / OBSOLETO | — | nenhuma |
| ACH-07 | "Rascunho salvo" com etapa pendente | PARCIALMENTE RESOLVIDO | C | nenhuma |
| ACH-08 | Período em curso tratado como vencido | RESOLVIDO | — | nenhuma |
| ACH-09 · 10 · 36 | Marco sem explicação, 28 controles, "consolidar" | RESOLVIDO | — | nenhuma |
| ACH-11 | Resumo do bloco não acompanha a escolha | NÃO IMPLEMENTADO | C | nenhuma |
| ACH-12 | Desempate por idade | SUPERADO / OBSOLETO | — | nenhuma |
| ACH-13 · 34 | Período de inscrições "marcado" × designado | NÃO IMPLEMENTADO | C | corrigir (microcópia) |
| ACH-14 | "Chave" do documento inventada à mão | NÃO IMPLEMENTADO | C | corrigir |
| ACH-16 | `Peso (opcional)` | RESOLVIDO | — | nenhuma |
| ACH-17 · QW11 | Quatro casas no motivo e no formulário | PARCIALMENTE RESOLVIDO | C | corrigir |
| ACH-18 · 33 | Numeração de seções diverge | NÃO IMPLEMENTADO | C | nenhuma |
| ACH-19 | Segregação não dita no cartão antes de homologar | NÃO IMPLEMENTADO | C | nenhuma |
| ACH-20 | Vigência da versão consolidada, densa | SUPERADO / OBSOLETO | — | nenhuma |
| ACH-21 | Atribuições × Requisitos no PDF | NÃO IMPLEMENTADO | C | nenhuma |
| ACH-22 | Retomar a intenção de inscrição | NÃO IMPLEMENTADO (por decisão de segurança) | — | nenhuma |
| ACH-23 | Declaração "li o Edital" sem link | NÃO IMPLEMENTADO | C | corrigir |
| ACH-24 | Comprovante "disponível enquanto…" | NÃO IMPLEMENTADO | C | validar |
| ACH-25 | Visão global some com o Processo vivo | DUPLICADO / ABSORVIDO (`N-01`…`N-04`) | — | outro lote |
| ACH-26 | Término das inscrições governa a avaliação | NÃO IMPLEMENTADO | C | nenhuma |
| ACH-27 | Oito contadores | DUPLICADO / ABSORVIDO (`N-07`) | — | outro lote |
| ACH-28 | Aviso de segregação em Edital publicado | NÃO IMPLEMENTADO | C | corrigir |
| ACH-29 | Validação de publicação exibida depois de publicado (agora com IMPEDE) | NÃO IMPLEMENTADO | B | validar e corrigir |
| ACH-30 | "Correções por Retificação" sem a quem pedir | RESOLVIDO | — | nenhuma |
| ACH-31 | `REPLACE` na tela do ato de Retificação | PARCIALMENTE RESOLVIDO | C | corrigir |
| ACH-32 | Bloco de sorteio e códigos na Retificação | NÃO IMPLEMENTADO | C | corrigir (respeitando FR-313) |
| ACH-35 | 404 mudo por vínculo | RESOLVIDO | — | nenhuma (resto é `D-G2`) |
| ACH-37 | "Consultar ato e proveniência" | PARCIALMENTE RESOLVIDO | C | corrigir |
| ACH-38 | Presidência sem "peça a alguém" | RESOLVIDO | — | nenhuma |
| ACH-39 | Tabela de resultados antecedentes só em UUID | NÃO IMPLEMENTADO | C | corrigir |
| ACH-40 | Publicador sem caminho | RESOLVIDO | — | nenhuma |
| ACH-41 | Duas datas-limite do recurso | NÃO IMPLEMENTADO | B | criar spec (`E-4`) |
| ACH-42 | Parecer não chega ao candidato | RESOLVIDO | — | nenhuma |
| ACH-43 | Julgador sem a prova | RESOLVIDO | — | nenhuma |
| ACH-44 | "o meu resultado" na gestão | NÃO IMPLEMENTADO | C | corrigir |
| ACH-45 | `cand:…` e UUIDs na tela do recurso | DUPLICADO / ABSORVIDO (`N-09`) | C | corrigir com 44/39 |

## (2) Contagens por estado (62 blocos; `ACH-09/10/36`, `ACH-13/34`, `ACH-18/33`, `ACH-03/15` e os agrupamentos de 13/09 contam como um)

| Estado | Blocos |
|---|---:|
| RESOLVIDO | 21 |
| RESOLVIDO POR OUTRO CAMINHO | 4 |
| PARCIALMENTE RESOLVIDO | 9 |
| NÃO IMPLEMENTADO | 20 |
| IMPLEMENTADO, MAS NÃO VALIDADO | 0 |
| SUPERADO / OBSOLETO | 3 |
| DUPLICADO / ABSORVIDO | 5 |
| CONTRADITO POR DECISÃO POSTERIOR | 0 |

Resíduos dos 29 blocos abertos (9 parciais + 20 não implementados): **A 0 · B 4 · C 23 · — 2**
(os dois "—" são `ACH-05` e `ACH-22`, cujo resto não se recomenda). Nenhum resíduo deste lote contradiz requisito escrito nem impede a finalidade: o
que estava nessa classe (`ACH-40`, `ACH-43`, `ACH-42`, 13/09 #1, #2, #4, #5) fechou.

**Os quatro B**: `ACH-29` (validação de publicação exibida em Edital publicado, agora com
impeditivo falso), `ACH-41` (duas datas de recurso — é `E-4`), 13/09 QW12 (prazo recursal fora da
divulgação pública) e 13/09 P2 (vagas por modalidade fora da página da vaga).

## (3) Achados NOVOS encontrados de passagem

- **NOVO-1 — A tela do Edital publicado roda a conferência de publicação no instante de agora, e
  exibe impeditivo falso.** `interface/views.py:2787` → `_pendencias` → `validate_for_publication(
  …, ato=ATO_DE_PUBLICACAO, agora=agora)` (`:845-847`) sobre o relacional, para qualquer situação;
  `detalhe.html:168-180` a exibe. Terminado o prazo de inscrições, o Edital publicado mostra
  "Impede — O período de inscrições encerrou… corrija a data… antes de publicar"
  (`editais/domain/validation.py:2093-2100`). Depois de uma Retificação, julga ainda o conteúdo da
  publicação original (o relacional não é reescrito). É a forma atual e ampliada do `ACH-29`; fica
  registrado como novo porque o impeditivo (`028`) e a leitura do relacional pós-Retificação não
  estavam no achado de 16/09. **Não percorrido pela interface.**
- **NOVO-2 — A contagem "42 controles, e cresceu" do preâmbulo do longitudinal (21/09, item 6) não
  mede a tela.** Ela conta tags de `_marco.html`, incluindo 12 `hidden` e dois blocos que só
  existem sob condição (sorteio; combinação com ≥2 Etapas). Na chegada de um marco simples são 6
  controles, 4 preenchidos (confere com a reavaliação de 18/09 §4.1). Documento a corrigir, não
  produto.
- **NOVO-3 — "Remover da comissão" é o último ato operacional de efeito em cascata sem página de
  conferência** (`comissao.html:101-111`, `interface/views.py:4489-4497`,
  `comissoes/application/comissao.py:236-281`): inativa o membro e todas as alocações dele. Já
  estava no 13/09 #9 e a reauditoria de 16/09 o deu como fechado sem testá-lo (§17). Registrado
  como parcial no bloco 13/09 #9.

## (4) Incertezas que exigem validação humana

1. **NOVO-1/ACH-29**: confirmar pela interface (Edital publicado com inscrições encerradas) que o
   bloco "Validação do conteúdo" aparece com "Impede". A cadeia foi lida de ponta a ponta, mas nada
   foi executado.
2. **ACH-04**: a FR-426 da `030` pretendia valer só para a Classificação, ou para todas as etapas?
   A de Perfis ficou com o bloco incondicional.
3. **ACH-24**: existe política de guarda do comprovante? Se não, a frase do comprovante promete uma
   limitação que o sistema não tem.
4. **ACH-17**: o motivo ("78,0000 ≥ 40,0000") é gravado no Resultado ou recalculado na leitura?
   Define se a correção alcança resultados já consolidados.
5. **ACH-32**: aceitar que a FR-313 (bloco do método sempre oferecido) cede quando o marco declara
   `orderProduction = POR_PONTUACAO` é decisão de produto — o código registra a regra como
   deliberada.
6. **"Providência a jusante"**: 13/09 chamou de jargão; 16/09 (PP-87) chamou de vocabulário de
   domínio correto. Não há como decidir por código.
7. **ACH-01**: um link público para a gestão é desejado em produção? O `IndexView` registra a
   escolha contrária para a raiz.
