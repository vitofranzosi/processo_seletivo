# Lote 6 — Estudo de esforço (21/09, revisto em 25/09) e a onda documental de 25/09

Auditoria de consolidação · base `bb774d9` (= origin/main de 25/09/2026) · somente leitura.

**Escopo.** `doc/estudo-esforco-de-cadastro-2026-09-21.md` inteiro (inclusive a revisão `15f587b` e o
§12 com os grupos A/B/C), o diário `doc/diario-estudo-esforco-2026-09-21.md`, os commits de 25/09
`cf18a6b` (#159), `8e4bc06` (#162, grupo A), `7b04cb3` (#163, grupo B), `d0352f5` (#164, grupo C),
`01d9163` (#161), `a2b1e1f` (#167), os avulsos `doc/achado-documento-condicional-no-portal.md` (#160),
`doc/conferencia-envio-e-analise-documental.md` (#165), `doc/decisao-recorte-documental.md` (#166),
a spec `043` (implementada em `0479f4e`, #170), a spec `044` (só especificada na `main`, #168) e o
PR aberto #171 (ValorDeFato).

**Mapa PR → commit** (conferido em `git log --merges`): #159 = `cf18a6b` · #160 = achado do portal ·
#161 = `01d9163` · #162 = `8e4bc06` · #163 = `7b04cb3` · #164 = `d0352f5` · #165 = conferência ·
#166 = decisão do recorte · #167 = `a2b1e1f` · #168 = spec 044 · #169 = `643e865` · #170 = 043.

**Separação pedida.** Cada bloco diz em "Rastro posterior" se o item (i) foi corrigido em 25/09,
(ii) ficou deliberadamente para a 044, ou (iii) ficou sem dono. A tabela final repete isso na coluna
"próxima ação".

**Aviso importante sobre a 044 (premissa corrigida pelo coordenador).** Na `main` ela é só spec. A
implementação existe **fora da main**, em `origin/claude/044-recorte-transversal-documental`
(commits `bccfda0`, `fe9780b`, `6e2aa5a`, `85ebd61`, `4ae22d1`, `dffb9db`, `46ac737`, `56649d4`, o
último em 25/09 23:28; ponta atual `683dc58`, que já mescla a `main` de `bb774d9` e contém a 043),
com `inscricoes/0005` e "suíte verde (7747 passando, 11 pulados)" na mensagem de `56649d4`. **Não há
PR aberto.** Para os achados que a 044 cobre, conferi o código da branch com `git show`/`git diff`
(sem checkout) e classifiquei como **IMPLEMENTADO, MAS NÃO VALIDADO** — a `main` de hoje continua com
a lacuna. Única tarefa aberta na branch: T065 (demonstrar SC-260/SC-261 no 140/2025).

**Atualização de 26/09:** a 044 foi mesclada pelo #173 (`47876ad`) com o CI verde, e a Mesa foi percorrida
pela tela depois (`0c4e6b0`). O #171 foi mesclado como registro, sem a correção. Os blocos que tocam os
dois — §5.9, #161, D4 e ValorDeFato —, a tabela-resumo e as contagens foram revistos; o que dizem da
branch é a leitura de antes do merge.

---

## Parte 1 — Atritos da composição (§5, §11 M/B), o que 25/09 fechou e o que sobrou

### §5.1 · A1 · Quick win 1 · §9.A.1 · §10 Caso 1 — "Cadastro Reserva limitado" inalcançável
- Origem: estudo §5.1, §9.A.1, §10 Caso 1, §11 A1, §12 item 1 (21/09); diário A2.
- Problema original: `validacao.js` lia o grupo de rádios `reserveType` sem `:checked`; o tipo era sempre `NONE`, LIMITED ficava inalcançável e o PDF publicava "Cadastro reserva: ilimitado" contra "até 30 suplentes" do Edital.
- Recomendação original: acrescentar `:checked`.
- Rastro posterior: corrigido em 25/09, `cf18a6b` (#159), com fixture e shim de DOM refeitos (a fixture antiga montava o rádio como campo único, e por isso os testes passavam com o defeito).
- Specs relacionadas: 007 (validação de cliente), 027.
- Implementação encontrada: leitura do rádio marcado; shim aprende `[name$="-x"]:checked`.
- Evidência no código atual: `backend/processo_seletivo/interface/static/interface/validacao.js:50` — `linha.querySelector('[name$="-reserveType"]:checked')`; `backend/tests/javascript/validacao.test.js:28,56,65` — o grupo NONE/LIMITED/UNLIMITED e os casos LIMITED vazio e LIMITED 10; `publicacoes/infrastructure/pdf.py:1683-1685` e `:1805-1809` imprimem "limitado em N".
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não — fechado.
- Lacuna residual: nenhuma. Documento já publicado com "ilimitado" não se regenera (e não deve).
- Grupo do resíduo: —
- Impacto atual: nenhum para publicações novas.
- Próxima ação sugerida: nenhuma.
- Relações: raiz comum com §5.9 ("o campo admite menos estados que a norma", §9-bis); memória `shim-de-dom-usa-tagname-minusculo`.
- Confiança: alta — código, teste e commit conferidos.

### §5.4 · M2 · M3 · Quick wins 3 e 4 — rótulos da Etapa decisória sem `*`; impedimento com caminho e UUID
- Origem: estudo §5.4, §11 M2/M3, §12 itens 3–4 (21/09).
- Problema original: "Rótulo do resultado favorável/desfavorável" eram obrigatórios na publicação sem se anunciar; o IMPEDE mostrava `/stages/id=<uuid>/rotuloFavoravel`.
- Recomendação original: marcar com `*`; nomear entidade e campo na mensagem.
- Rastro posterior: corrigido em 25/09 — `*` e `aria-required` em `8e4bc06` (#162); tradução do caminho em `7b04cb3` (#163), reusando o vocabulário da Retificação.
- Specs relacionadas: 012 (conclusão decisória), 027/028 (pendências com destino).
- Implementação encontrada: `nomes_dos_caminhos` + `mensagem_legivel` sobre cada pendência; a mensagem do domínio não muda.
- Evidência no código atual: `interface/templates/interface/_etapa.html:114` (`*` no rótulo favorável; idem desfavorável logo abaixo, sem `required` de propósito — o bloco só se oculta por CSS); `interface/views.py:727-775` (`nomes_dos_caminhos`, `_caminho_legivel`, `mensagem_legivel`) e `:846-852` (aplicado em `_pendencias`); testes `tests/interface/test_pendencia_nomeia_o_campo.py`, `tests/interface/test_acessibilidade.py`.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não — fechado na Revisão e nas etapas do assistente.
- Lacuna residual: a tradução vale só onde `_pendencias` é usado (`views.py:847` é o único consumidor de `validate_for_publication` na interface). A tela de confirmação da Retificação continua exibindo o caminho em `<code>` sob o rótulo (`retificacao_confirmar.html:55-57`), mas isso é desenho deliberado do 13/09 ("fica em segundo plano, para quem audita", comentário em `:45-51`), e não o defeito do estudo.
- Grupo do resíduo: —
- Impacto atual: nenhum relevante.
- Próxima ação sugerida: nenhuma.
- Relações: conferência de 25/09 ("A tela da Retificação mostra o caminho com UUID") é a mesma família em outra tela, já tratada por decisão do 13/09 (lote da auditoria UX 13/09).
- Confiança: alta.

### §5.5 · M1 · Quick win 2 — seletor de Evento das Etapas com opções idênticas
- Origem: estudo §5.5, §11 M1, §12 item 2 (21/09).
- Problema original: o seletor usava `Tipo · data`, e dois Eventos de mesmo tipo e data davam opções iguais; a Inscrição já usava `Tipo · data — Descrição`.
- Recomendação original: usar o rótulo da Inscrição.
- Rastro posterior: corrigido em 25/09, `8e4bc06` (#162).
- Specs relacionadas: 004/021.
- Evidência no código atual: `interface/templates/interface/_etapa.html:27` — `{{ evento.rotulo }} — {{ evento.description }}`; teste em `tests/interface/test_compor.py` (diff do commit).
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: —
- Confiança: alta.

### §5.6 · M5 · Quick win 5 — Casas decimais, Arredondamento e Alvo visíveis e obrigatórios num marco por sorteio
- Origem: estudo §5.6, §11 M5, §12 item 5 (21/09; revisto 25/09).
- Problema original: a divulgação progressiva do marco não alcançava três campos inaplicáveis ao sorteio.
- Recomendação original: escondê-los quando não se aplicam.
- Rastro posterior: **Alvo** corrigido em 25/09 (`8e4bc06`, #162), visível só sob "quantidade fixa". **Casas decimais e Arredondamento** registrados na revisão de 25/09 como decisão de domínio, **não tomada**: a publicação os exige em todo marco e FR-419 (030) manda oferecê-los com padrão.
- Specs relacionadas: 030 FR-419 (`specs/030-composicao-que-se-explica/spec.md:160`), 014 (regra de corte).
- Evidência no código atual: `interface/templates/interface/_marco.html:521` (`class="campo curto so-fixo"`) e `interface/templates/interface/base.html:1053` (oculta `.so-fixo` quando `cutTargetKind` ≠ FIXED); `_marco.html:156-167` — Casas decimais e Arredondamento com `*`, `required` e a ajuda "Aplicado uma vez, sobre a pontuação combinada" continuam incondicionais; teste `tests/interface/test_campos_que_a_escolha_governa.py`.
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: parcialmente — o custo é pequeno (os campos já nascem preenchidos pelo padrão da FR-419, então não exigem digitação), o dano é de coerência da tela: o cartão pede arredondamento "sobre a pontuação combinada" ao lado do texto que diz não haver pontuação a combinar.
- Lacuna residual: dispensar Casas decimais/Arredondamento no marco de sorteio é decisão de domínio pendente com o usuário (o que a publicação exige). Sem dono.
- Grupo do resíduo: C
- Impacto atual: baixo — valor padrão já preenchido; só ruído cognitivo.
- Próxima ação sugerida: nenhuma até o usuário decidir; se decidir, pequena mudança de validação + CSS.
- Relações: §5.10 (campo dependente).
- Confiança: alta.

### §5.7 · M4 — o quadro de vagas mostra "Modalidade nova" até gravar
- Origem: estudo §5.7, §11 M4 (21/09); diário E5.
- Problema original: Modalidades acrescentadas e ainda não gravadas aparecem no quadro todas como "Modalidade nova"; quem preenche quantidades antes de gravar preenche às cegas, e trocar números entre listas é erro normativo.
- Recomendação original: implícita — o rótulo acompanhar o que se digita.
- Rastro posterior: **nenhum**. Não entrou no §12 (quick wins) nem nos grupos A/B/C de 25/09. O #162 fez o quadro se reconstruir ao **remover** Modalidade (`_perfil.html:283-285`), não ao renomear/digitar.
- Specs relacionadas: 027 (FR-317, reconstrução do quadro durante a edição).
- Implementação encontrada: nenhuma para este caso.
- Evidência no código atual: `interface/views.py:2504` — a linha nova nasce com `"rotulo": "Modalidade nova"`; o docstring em `:2470-2475` justifica: "o código e a denominação estão sendo digitados agora — e a alternativa seria espelhá-los por JavaScript, que a CSP desta interface não admite". Os campos de código e denominação (`_modalidade.html:14,20`) não têm `hx-trigger`; o seletor da ampla concorrência já reconstrói o quadro por `hx-get` sem JS inline (`_perfil.html:187-192`), de modo que a mesma técnica serviria aqui.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim — a justificativa da CSP não se sustenta por inteiro (o mesmo `hx-get … hx-include="closest fieldset"` já é usado no mesmo cartão); o risco é normativo (quantidade na lista errada), embora mitigado porque a ordem das linhas segue a das Modalidades e o `modalityId` oculto está certo.
- Lacuna residual: rótulo do quadro não acompanha a Modalidade em edição. Sem dono.
- Grupo do resíduo: B
- Impacto atual: médio em Perfis com várias Modalidades novas (4 linhas idênticas no 140/2025); some depois de gravar.
- Próxima ação sugerida: corrigir (fila de diretas) — `hx-trigger="change"` nos campos de código/denominação reconstruindo `#quadro-<indice>`.
- Relações: mesma causa de §5.11/M12 (estado de tela derivado só se recalcula na gravação).
- Confiança: alta.

### §5.11 · M12 — o rótulo da Modalidade fica velho no seletor até gravar
- Origem: estudo §5.11, §11 M12 (21/09); diário E5.
- Problema original: renomeadas as Modalidades, o `<select>` logo abaixo continua oferecendo os rótulos antigos — no reuso, os de outro certame.
- Recomendação original: implícita — atualizar o seletor com o que se digita.
- Rastro posterior: nenhum (fora do §12 e dos grupos de 25/09).
- Specs relacionadas: 027 (FR-317), 023 (reuso).
- Evidência no código atual: `interface/templates/interface/_perfil.html:187-197` — "Qual delas é a ampla concorrência" renderiza `{{ modalidade.code }} — {{ modalidade.name }}` do que veio do servidor; nada o reconstrói quando código/denominação mudam.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim — a escolha da ampla concorrência é normativa (define a linha geral do quadro), e no reuso o nome velho é de outro Edital.
- Lacuna residual: seletor com rótulo defasado até gravar. Sem dono.
- Grupo do resíduo: B
- Impacto atual: médio, concentrado no reuso.
- Próxima ação sugerida: corrigir junto com §5.7 (mesmo gatilho reconstrói as duas coisas).
- Relações: §5.7/M4 (mesma causa).
- Confiança: alta.

### §5.8 · B2 · Quick win 8 — bloco "Quadro de vagas" não some ao remover a última Modalidade
- Origem: estudo §5.8, §11 B2, §12 item 8 (21/09).
- Problema original: título e explicação "Este Perfil declara lista reservada…" ficavam na tela depois de removida a última Modalidade.
- Recomendação original: ocultar o bloco.
- Rastro posterior: corrigido em 25/09, `8e4bc06` (#162) — remover Modalidade reconstrói o quadro pelo fragmento que o seletor da ampla já usava.
- Evidência no código atual: `interface/templates/interface/_perfil.html:281-285` — `hx-get` para `fragmento-quadro` com `hx-trigger="htmx:afterRequest from:#modalidades-{{ indice }}"`; teste `tests/interface/test_compor_quadro.py` (diff do commit).
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: §5.7 (a reconstrução cobre remover, não renomear).
- Confiança: alta.

### §5.10 · M11 · Quick win 11 — campo dependente não se limpa quando a regra muda
- Origem: estudo §5.10, §11 M11, §12 item 11 (21/09); diário E4.
- Problema original: Alvo `10` num marco que não corta; Pontuação máxima `100` numa Etapa decisória.
- Recomendação original: limpar o campo dependente.
- Rastro posterior: revisão de 25/09 conclui "sem mudança própria": o servidor já descartava os dois, e o #162 escondeu o Alvo; a Pontuação máxima já saía da tela sob a forma decisória.
- Evidência no código atual: `interface/forms.py:413-417` — `targetCount` só com espécie FIXED; `interface/forms.py:707` — `maximumScore` é `None` quando decisória; `_etapa.html:71` (`so-pontuada`) e `base.html:1043-1044` (oculta `.so-pontuada` sob DECISORIA).
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não — o valor órfão não chega ao conteúdo nem fica à vista.
- Lacuna residual: nenhuma.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: §5.6.
- Confiança: alta.

### §5.12 · M8 · M14 · Quick wins 6 e 13 — a Revisão soterra o IMPEDE sob avisos repetidos; âncora da regra do ano
- Origem: estudo §5.12, §8, §11 M8/M14, §12 itens 6 e 13 (21/09); diário E9 (54 AVISO × 1 IMPEDE: 16 "0 vaga(s) imediata(s)", 16 "marco sem regra de corte", 13 "Evento que já passou", 9 "não declara a ampla").
- Problema original: lista ordenada por objeto, não por severidade; 45 de 54 avisos repetidos por Perfil ou por Evento; 13 avisos de ano divergente logo após o reuso.
- Recomendação original: colapsar os avisos repetidos; ordenar por severidade; ancorar a regra do ano no período do certame.
- Rastro posterior: 25/09, `7b04cb3` (#163) — **colapso só das duas famílias por Evento** (`schedule_event_in_past`, `schedule_event_year_mismatch`), em `details`, sem descartar nenhum; a **âncora** foi registrada como decisão não tomada (FR-344 da 028, `specs/028-cronograma-reaproveitado-vencido/spec.md:456`).
- Specs relacionadas: 028 (FR-343a, FR-344), 037 (condução).
- Implementação encontrada: filtro `agrupar_repetidas`.
- Evidência no código atual: `interface/templatetags/interface_extras.py:335-338` — `RESUMO_DAS_REPETIDAS` só tem os dois códigos de Evento; `:350-351` — "O grupo fica onde estava o primeiro, para que a ordem da lista continue sendo a do domínio" (sem ordenação por severidade); `interface/views.py:847-866` e `editais/domain/validation.py:1422` (`return findings`) — nenhuma ordenação; `interface/templates/interface/compor_revisao.html:5-7` — sem contagem por severidade no topo; teste `tests/interface/test_advertencias_repetidas.py`.
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: sim para o que sobrou — das 45 repetições medidas, **32 são por Perfil** (16 + 16) e **9** também por Perfil, e nenhuma dessas famílias colapsa; com 16 Perfis o IMPEDE continua misturado a ~40 linhas. Pôr os impedimentos primeiro é barato e não esconde nada.
- Lacuna residual: (a) colapso das famílias por Perfil; (b) impedimentos antes dos avisos, ou contagem no topo; (c) âncora do ano — decisão do usuário sobre FR-344, pendente. Sem dono.
- Grupo do resíduo: B
- Impacto atual: médio em Editais multipolo — é exatamente onde a Revisão mais importa.
- Próxima ação sugerida: corrigir (a) e (b) como diretas (mesmo mecanismo do #163); (c) aguarda decisão.
- Relações: §5.2 (o paredão de datas herdadas); E8/M15 (os 16 avisos de "0 vaga imediata" nascem do cadastro de reserva sem quantidade).
- Confiança: alta.

## Parte 2 — Documento exigido sob condição (§5.9, E6) e a onda documental de 25/09

### §5.9 · A7 · E6 (condição de modalidade) · §10 Caso 5 · §9-bis · §15 frente 1 · achado do portal §1 e "o que muda" 1 · decisão D1/D1a/D3 — "todo candidato PcD" não tem forma; obrigatórios publicados como facultativos
- Origem: estudo §5.9, §9-bis, §10 Caso 5, §11 A7, §13 E6, §15 frente 1 (21/09); `doc/achado-documento-condicional-no-portal.md` (#160, 25/09); `doc/decisao-recorte-documental.md` D1, D1a, D3 (#166, 25/09).
- Problema original: o recorte do Documento Exigido aponta Modalidade por **identidade**, e cada Perfil tem as suas; "todo PcD" em 16 Perfis custa 7 × 16 = 112 linhas. O atalho do operador ("todas as modalidades" + desmarcar obrigatório + condição na instrução) publicou **9 obrigatórios como `(facultativo)`** no 140/2025, entre eles o laudo PcD.
- Recomendação original: um escopo por Modalidade que valha para todos os Perfis, ou um estado "obrigatório sob condição"; o estudo apontou o **código** da Modalidade (E6).
- Rastro posterior: decisão de 25/09 aceita **D1 = código com IMPEDE de coerência só de denominação**, **D1a = proibido para a ampla**, **D3 = sem exceção negativa, o recorte exato fica como escape**; **D5 = só recorte transversal + lista gravada**. Endereço: **spec 044** (#168, `specs/044-recorte-transversal-documental/spec.md:320-365`, FR-700…FR-713, UX-080). **(ii) deliberadamente para a 044.**
- Specs relacionadas: 044 (não implementada na main); 009/020 (documentos e modelo); 043 FR-645 (duplicar não copia documento restrito).
- Implementação encontrada: **na main, nenhuma** — `editais/domain/documentos.py:97-114` (`aplicaveis`) continua com as "quatro combinações", por identidade exata de `profileId`/`modalityId`; `grep` por `modalityCode`/`transversal` em `backend/processo_seletivo` não acha nada. **Fora da main**, na branch `origin/claude/044-recorte-transversal-documental` (`bccfda0`, `fe9780b`): campo `modalityCode` no Documento Exigido (`editais/migrations/0022_documento_modalidade_codigo.py`); regra única `aplicabilidade`/`_se_aplica` em `editais/domain/documentos.py:206-290` (da branch); recusas na gravação (`documentos.py:105-151`, código inexistente, ampla, combinação com Perfil/Modalidade); IMPEDE de coerência de denominação `_denominacoes_do_codigo` e `_recorte_por_codigo` em `editais/domain/validation.py:2234-2320` (da branch); grupo por código no PDF, `publicacoes/infrastructure/pdf.py:1974` (da branch); grupo `<optgroup label="Em todos os Perfis">` em `interface/templates/interface/_documento.html:69` (da branch); testes `tests/unit/inscricoes/test_aplicabilidade.py`, `tests/integration/inscricoes/test_recorte_transversal.py`, `tests/unit/editais/test_documentos_recusas.py`, `tests/unit/publicacoes/test_pdf_documentos_exigidos.py`.
- Evidência no código atual: main — `documentos.py:97-114`; `.specify/memory/constitution.md:200-201` ("Documentos Exigidos PODEM variar por … modalidade … e condição normativa"). Branch — rastreabilidade da 044 (`specs/044-recorte-transversal-documental/rastreabilidade.md:61-69` na branch): **SC-260 e SC-261 não recompostos** (a redução 112→7 e os "4 obrigatórios" no 140/2025 são afirmados "por construção", T065 aberta); SC-262 percorrido no navegador com a PPP no lugar do PcD, **sem a Mesa**; SC-268 com Perfis e cronograma entrando pela API de rascunho.
- Estado atual: RESOLVIDO — atualizado em 26/09: a 044 entrou na main pelo #173 (`47876ad`, CI verde). Evidência na main: `editais/domain/documentos.py:206-290` (recorte por código), `editais/domain/validation.py:2234-2321` (código inexistente, da ampla, denominação divergente), migration `editais/0022`; percurso pela tela em `specs/044-recorte-transversal-documental/rastreabilidade.md`. O que está acima descreve a branch como foi lida antes do merge.
- Ainda faz sentido?: sim — é o único achado do estudo, depois do #159, que faz o ato publicado dizer menos do que a norma sem erro do operador; e a 044 é o desenho mínimo (sem entidade nova). Não é overengineering: um campo no Documento Exigido e uma regra de publicação.
- Lacuna residual: a T065 não foi feita, e a redução 112 → 7 no 140/2025 (SC-260, SC-261) é afirmada por construção `[VALIDAR]`. Fora dela, e já com a 044, **3 dos 9** (declaração indígena, Funai, quilombola) seguem facultativos por falta de submodalidade (044 §1, `:60-76`; E7/AX-15), e **2** (militar, chefia) são condição sobre o candidato (bloco D2 abaixo).
- Grupo do resíduo: — (os 3 da submodalidade são do bloco A10/AX-15; os 2 do candidato, da D2)
- Impacto atual: nenhum de implementação; resta medir a redução no 140/2025.
- Próxima ação sugerida: demonstrar a T065, se a medição for pedida.
- Relações: E6 → causa estrutural "granularidade em que a regra é declarada" (E2); AX-10 ("Documentos exigidos funde quatro categorias", 15/09, lote 4); §9-bis "o campo admite menos estados que a norma" (mesma forma do §5.1).
- Confiança: alta.

### Achado do portal §3 · "o que muda" 2 · #161 — "Todos os Perfis" + Modalidade de um Perfil: PDF e portal divergem
- Origem: `doc/achado-documento-condicional-no-portal.md` §3 e "O que isso muda para a spec" item 2 (25/09); conferência §2, §7.
- Problema original: o PDF agrupa pelo **nome** da Modalidade ("Dos candidatos concorrentes na modalidade PcD", sem Perfil) e o portal aplica pela **identidade**; com dois Perfis, o Edital exige o laudo de todo PcD e o portal só no C1. O reuso produzia o recorte sozinho, e a Revisão não avisava.
- Recomendação original: validação que recuse (ou aviso na Revisão), sem decidir o desenho.
- Rastro posterior: corrigido em 25/09, `01d9163` (#161) — IMPEDE `document_requirement_modality_scope_ambiguous` na publicação e na Retificação, só quando o nome se repete em outro Perfil. A conferência (#165) confirmou que a contenção funciona e "não sobrevive à primeira Retificação".
- Specs relacionadas: 044 FR-708 (acrescentar a terceira saída "use a modalidade em todos os Perfis") e FR-727 (a Mesa denunciar a divergência em inscrições anteriores à #161).
- Implementação encontrada: `_recorte_que_o_documento_publicado_alarga`.
- Evidência no código atual: `editais/domain/validation.py:2225-2275` — compara `_rotulo_da_modalidade` do dono com os outros Perfis; mensagem com as duas saídas (`:2269-2274`); teste `tests/unit/editais/test_validacao_inscricao.py:102` e ajuste em `tests/integration/inscricoes/test_regressoes_da_entrega_6.py`.
- Estado atual: RESOLVIDO — atualizado em 26/09: (a) e (b) entraram na main com o #173.
- Ainda faz sentido?: não — a divergência não se publica mais, e o que faltava era da 044, que entrou: (a) a terceira saída na mensagem (depende do recorte transversal existir); (b) Editais **já publicados** antes da #161 com o recorte ambíguo continuam recebendo inscrições e a Mesa não sinaliza o documento que o portal dispensou (FR-727).
- Lacuna residual: nenhuma de implementação. (a) e (b) eram **(ii) para a 044**, e entraram na main com o #173 em 26/09. Como foram lidos na branch, antes do merge: a mensagem ganha a terceira saída ("'{rotulo}' ({codigo}) em todos os Perfis — ou, para exigi-lo em Perfis escolhidos…", `editais/domain/validation.py:2357` da branch), e a lista carrega `divergente_do_publicado` (`inscricoes/application/lista_exigida.py:64,106` da branch; teste `test_a_divergencia_da_161_aparece_na_lista_reconstruida`). A Mesa foi percorrida pela tela depois do merge (`0c4e6b0`).
- Grupo do resíduo: — (era A enquanto (a) e (b) estavam fora da main; resta saber se há Edital ambíguo publicado, que é validação, e a Mesa agora o denuncia)
- Impacto atual: baixo para Editais novos; médio para os publicados antes de 25/09 com esse recorte (desconhecido quantos).
- Próxima ação sugerida: conferir se há Edital publicado com o recorte ambíguo `[VALIDAR]`.
- Relações: AX-14 ("documento publicado × execução se contradizem", 15/09 — mesma forma, outro objeto); E-4 (validação cruzada entre fontes).
- Confiança: alta (código); média para o impacto em produção.

### Conferência §3/§6 · decisão D4 — a Mesa recalcula a lista; "não se aplica" não existe; nada registra o que foi pedido
- Origem: `doc/conferencia-envio-e-analise-documental.md` §1, §3, §4, §6, "O que isto muda" (25/09); decisão D4 (`decisao-recorte-documental.md`, D4.1).
- Problema original: a Mesa refaz o recorte sobre a versão aceita (`requisitos_da_inscricao`) e só distingue "com arquivo" e "não apresentado"; o inaplicável some, e com ele o que o portal dispensou por erro; o comprovante guarda só os apresentados; a consulta administrativa diz "1 de 1, completo" para o PcD sem laudo.
- Recomendação original: gravar na inscrição, no envio, a lista exigida com a razão de cada documento.
- Rastro posterior: decisão D4 = **sim** (25/09); spec 044 FR-714…FR-720, FR-726, US2/US4, UX-081…083. **(ii) para a 044.**
- Specs relacionadas: 044; 015/020 (versão aceita, modelo por versão).
- Evidência no código atual: `avaliacoes/application/mesa.py:113-141` — `inscricao_para_avaliar` lê `versao_aceita` e monta `documentos` recalculando; `inscricoes/application/rascunho.py:323` (`requisitos_da_inscricao`), usado também por `inscricoes/application/consulta.py:242` e `portal/views.py:1585,1622`; `interface/templates/interface/mesa_inscricao.html:91` — só a marca "obrigatório", sem estado "não se aplica"; `inscricoes/migrations/` na main vai até `0004` (sem tabela de lista exigida).
- Implementação fora da main (branch da 044, `6e2aa5a`, `85ebd61`): tabela `inscricoes_itemdalistaexigida` com duas triggers (append-only e coerência) em `inscricoes/migrations/0005_item_da_lista_exigida.py:1-33` (da branch), recusa em `save`/`delete` do modelo (`inscricoes/models.py:186`, `:305-310` da branch) e entrada em `TABELAS_APPEND_ONLY` (`seguranca/papeis.py:116-120` da branch) — as três camadas; `gravar_lista_exigida`/`lista_exigida` em `inscricoes/application/lista_exigida.py:38,72` (da branch); a Mesa passa a ler a lista, com "reconstruída" anunciada e o bloco "Não se aplicam a esta inscrição" (`avaliacoes/application/mesa.py:134-135,218` e `interface/templates/interface/mesa_inscricao.html:93-94,159` da branch); consulta administrativa (`inscricoes/application/consulta.py`) e portal também. Testes `tests/integration/inscricoes/test_lista_exigida*.py` (3 arquivos), `tests/interface/test_mesa_lista_exigida.py`.
- Estado atual: RESOLVIDO — atualizado em 26/09: a lista gravada entrou na main pelo #173. Evidência na main: `avaliacoes/application/mesa.py:135` lê a lista gravada, e `:171-217` monta "Não se aplicam"; `inscricoes/migrations/0005_item_da_lista_exigida.py`; `inscricoes_itemdalistaexigida` em `seguranca/papeis.py:120`; Mesa percorrida no navegador (`rastreabilidade.md` da 044, `0c4e6b0`). O que está acima descreve a branch e a main como foram lidas antes do merge.
- Ainda faz sentido?: sim — é o que a Constituição pede em texto (`constitution.md:200-201`, "O sistema DEVE reproduzir os documentos exigidos para cada Inscrição"), e sem a lista qualquer mudança de recorte (inclusive a própria 044) muda retroativamente a leitura das inscrições antigas.
- Lacuna residual: nenhuma. A Mesa, que faltava percorrer, foi percorrida depois do merge.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: PR #171 (ValorDeFato) nasceu do `research.md` da 044 ao decidir as camadas desta tabela nova.
- Confiança: alta.

### Conferência §1 e §3 · decisão D2 (correções diretas) · #167 — a instrução não chegava à Mesa; o facultativo perdia a marca na Revisão do portal
- Origem: conferência §1 e §3 (25/09); decisão D2, "duas correções … para a fila das diretas".
- Problema original: "Apenas para quem concorre na modalidade PcD" não aparecia na Mesa (a autodeclaração ausente do AC e a do PcD se liam iguais); na Revisão do portal o facultativo saía "Ainda não enviado.", com a grafia do obrigatório que falta.
- Recomendação original: as duas correções.
- Rastro posterior: corrigido em 25/09, `a2b1e1f` (#167). **(i) corrigido.**
- Evidência no código atual: `avaliacoes/application/mesa.py:131-135` (`"instrucoes"`); `interface/templates/interface/mesa_inscricao.html:90` (instrução abaixo do nome); `portal/templates/portal/revisao.html:97` (marca "(facultativo)") e o ramo `elif linha.obrigatorio` → "Ainda não enviado." / senão "Não enviado." neutro; testes `tests/integration/portal/test_revisao_marca_o_facultativo.py`, `tests/interface/test_mesa_modelo_exigido.py`.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não para o que se pediu.
- Lacuna residual: **o cartão público da vaga continua sem marca de facultativo** — o achado do portal §2, terceiro item ("no cartão público, sem marca nenhuma, na lista de '4 documentos que serão pedidos'"), não foi coberto pelo #167 nem pela 044 (conferi a branch da 044: nada em `portal/views.py`/`selecao.html` sobre obrigatoriedade). `portal/views.py:222-257` devolve só nomes e conta o facultativo no total "serão pedidos"; `portal/templates/portal/selecao.html:152-166`. Sem dono.
- Grupo do resíduo: C (a inscrição já marca; o cartão é antecipação)
- Impacto atual: baixo — o candidato vê o facultativo como exigido antes de entrar; na inscrição a marca aparece.
- Próxima ação sugerida: corrigir (direta, uma linha de dado + template), se o usuário quiser.
- Relações: D2 opção 1 ("facultativo com instrução" como estado assumido) — o custo dela é justamente essa marca aparecer em todas as superfícies.
- Confiança: alta.

### E6 (condição sobre o candidato) · decisão D2 · achado do portal "o que muda" 3 — sexo/idade (serviço militar) e vínculo de servidor sem forma
- Origem: estudo §5.9 (tabela), §13 E6 (21/09); achado do portal item 3; decisão D2 (25/09).
- Problema original: duas condições do 140/2025 não são de modalidade nem de Perfil — são do candidato; o único caminho é o "facultativo com instrução".
- Recomendação original: estado "obrigatório sob condição" com a condição em texto (E6), evitando coletar sexo/idade/vínculo de todo candidato.
- Rastro posterior: decisão D2 (25/09): **opção 1 (informativa, verificada à mão) como estado assumido**, com as duas correções diretas (feitas no #167); **opção 2 (autodeclarada) fica para spec própria, depois**, com avaliação de LGPD. A 044 exclui explicitamente (`spec.md:99-103`, `:615-616`).
- Specs relacionadas: nenhuma escrita para a opção 2.
- Evidência no código atual: não há campo de condição no Documento Exigido (`documentos.py:97-114` só lê `profileId`/`modalityId`; `required` é booleano); `alteracoes.py:89-95` confirma os campos do documento.
- Estado atual: CONTRADITO POR DECISÃO POSTERIOR — a decisão D2 de 25/09 (`doc/decisao-recorte-documental.md`, seção D2 e tabela "O que foi decidido") adotou o estado atual como o assumido e adiou a forma estruturada.
- Ainda faz sentido?: parcialmente — a decisão é razoável (minimização LGPD: modelar como atributo obrigaria coletar sexo, idade e vínculo de todos); o custo remanescente é que o analista verifica à mão e registra só em parecer.
- Lacuna residual: "obrigatório sob condição" como estado publicado (sem coletar atributo) continua sem forma; o documento sai "(facultativo)" no ato publicado, o que não é o que o Edital diz.
- Grupo do resíduo: B
- Impacto atual: baixo-médio — 2 documentos por Edital de pessoal, em média; verificação manual.
- Próxima ação sugerida: nenhuma até o usuário reabrir D2; quando reabrir, criar spec com LGPD.
- Relações: AX-11 (fatos declarados moram no Perfil) se o veículo for `declaredFacts`; conferência §5 (não há juízo por documento).
- Confiança: alta.

### Conferência "Achados fora do escopo" · decisão D4.3 — o "O que mudou" público omite a mudança de recorte do documento
- Origem: conferência, "Achados fora do escopo" (25/09); decisão D4.3 e lista final ("vão para a fila das diretas").
- Problema original: a Retificação declarou 7 alterações e o portal mostrou 6; faltou a do laudo que passou a valer só no C1 — a mais consequente para o candidato.
- Recomendação original: "O que mudou" passar a listar a mudança de recorte (`profileId`, `modalityId`).
- Rastro posterior: decidido em 25/09 para a fila das diretas; **não feito**. A 044 o exclui de propósito (`spec.md:111-113`, `:620`) e só cobre o campo novo (FR-721; na branch da 044, `alteracoes.py` ganha `"modalityCode"` com o comentário "`profileId` e `modalityId` continuam fora: a correção deles é da fila das diretas"). **(iii) sem dono.**
- Specs relacionadas: 024 FR-130 (`specs/024-descoberta-e-transparencia-no-portal/spec.md:365-366`: "Cada Retificação exibida MUST trazer … a identificação do que foi alterado").
- Evidência no código atual: `publicacoes/domain/alteracoes.py:89-95` — os campos do Documento Exigido são só nome, instruções, obrigatoriedade, ordem e modelo; `:14` — "Caminho não reconhecido não produz linha" (a omissão é silenciosa por desenho, D-009 da 024).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim — contradiz FR-130 da 024 e a decisão de 25/09; e é barato (duas entradas no dicionário com rótulo do domínio). O desenho da 024 (dizer o campo, não o valor) já basta.
- Lacuna residual: acrescentar `profileId` e `modalityId` do Documento Exigido ao `CAMPOS`.
- Grupo do resíduo: A
- Impacto atual: médio — o candidato não é avisado de que o documento passou a valer (ou deixou de valer) para ele; o documento da Retificação tem a mudança, o resumo não.
- Próxima ação sugerida: corrigir (fila das diretas).
- Relações: 024 D-009; 044 FR-721 (mesmo mecanismo para o campo novo). Vale conferir se outros campos retificáveis também faltam no dicionário (não verifiquei).
- Confiança: alta.

### Conferência §3 e §7 · 044 "Riscos e lacunas" — o filtro de concorrência da consulta administrativa repete "PcD" por Perfil sem nomeá-lo
- Origem: conferência §3 e §7 (25/09); 044 `spec.md:609-611` (registrado sem escopo).
- Problema original: o filtro lista "Ampla Concorrência" e "Pessoas com Deficiência" duas vezes, uma por Perfil, sem dizer de qual.
- Recomendação original: registrado como defeito de tela independente.
- Rastro posterior: **PR #172**, mesclado em 26/09 (`8e6fb4a`) — prefixa o nome do Perfil quando há mais de um, com teste em `tests/integration/interface/test_inscricoes_em_escala.py` e `doc/achado-filtro-de-concorrencia-sem-perfil.md`.
- Evidência no código atual (main): `interface/templates/interface/inscricoes.html:64` — a opção leva `{{ item.perfil }} · ` antes do nome da Modalidade quando o Edital tem mais de um Perfil.
- Estado atual: RESOLVIDO
- Ainda faz sentido?: sim — correção pequena e certa.
- Lacuna residual: o seletor não se restringe ao Perfil escolhido, registrado em `doc/achado-filtro-de-concorrencia-sem-perfil.md`.
- Grupo do resíduo: C
- Impacto atual: baixo (gestão; a contagem desambigua).
- Próxima ação sugerida: nenhuma.
- Relações: mesma causa do §7.2 (Modalidade é do Perfil, e a tela esquece de dizer de qual).
- Confiança: alta.

### Conferência §3–§5 — a Mesa mostra só protocolo e situação; não há juízo por documento; o parecer é o único registro da ausência
- Origem: conferência §3 (último item), §4, §5 (25/09).
- Problema original: a lista da Mesa não traz Perfil, modalidade nem completude; a conclusão é da inscrição inteira; deferir sem abrir documento é permitido.
- Recomendação original: nenhuma explícita — registrado como evidência para a decisão.
- Rastro posterior: a 044 exclui "juízo por documento" (`spec.md:109-110`, `:618`); a lista da Mesa não é tratada por ninguém.
- Evidência no código atual: `interface/templates/interface/mesa_inscricao.html:90-91` (por documento só nome, instrução e marca "obrigatório"); a conclusão por inscrição é desenho da 012 (`doc/decisao-012-conclusao-decisoria.md`).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente — juízo por documento é decisão de domínio (e a 044 a recusou com razão: a norma julga a inscrição); Perfil/modalidade na lista da Mesa é conveniência. Com a lista gravada da 044, o analista passa a ver estado e razão, que é o que importava.
- Lacuna residual: Perfil/modalidade/completude na lista da Mesa (conveniência).
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma (reavaliar depois da 044).
- Relações: 012; 044 US2.
- Confiança: média — não abri a view da lista da Mesa, só o detalhe.

## Parte 3 — Reaproveitamento e escala (§6, §8, §13 E1/E2/E3/E9)

### §6.2 · §6.4 · §8 · A2 · E1 · §15 frente 2 — não há reaproveitamento dentro do Edital; a curva de autoria é linear
- Origem: estudo §6.2, §6.4, §8, §11 A2, §13 E1, §15 frente 2 (21/09).
- Problema original: ~530 interações na etapa Perfis do 140/2025, ~430 sem informação nova; nenhuma operação de duplicar, aplicar-a-todos ou lote; fragmentos só criam linhas vazias.
- Recomendação original: "duplicar Perfil", "aplicar estas Modalidades a todos os Perfis", "aplicar este marco aos demais".
- Rastro posterior: **spec 043 implementada** (`0479f4e`, #170, 25/09) — só *duplicar Perfil*, por decisão do usuário (`specs/043-duplicar-perfil/spec.md` Clarifications); propagação em massa registrada como **TF-1** e redução documental como **TF-2** (`spec.md:244-264`). Decisão D5 de 25/09: "o lote é outra spec".
- Specs relacionadas: 043; 023 (remapear); TF-1 sem spec.
- Implementação encontrada: `editais/domain/duplicacao.py:30` (`duplicar_perfil`, identidades novas e referências remapeadas pelo `remapear` da 023); rota `interface/urls.py:111-116`; view `interface/views.py:1992-2113` (lê a origem do formulário, não do banco); cartão `interface/templates/interface/_perfil.html:5-7` (aviso da cópia, com quantos marcos e quantos documentos restritos não replicados) e `:298`; explicação uma vez em `compor_perfis.html:84-88`.
- Evidência no código atual: acima, mais `tests/interface/test_duplicar_perfil.py` (911 linhas), `tests/unit/editais/test_duplicacao.py`, `tests/authorization/test_duplicar_perfil.py`; `specs/043-duplicar-perfil/rastreabilidade.md:119-120` — medido pela interface: **101 interações contra ~530** (−81%), 4,4 por cópia. `grep` por "aplicar a todos|aplicar aos demais|em lote" em `interface/` e `editais/` não acha nada da composição.
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: parcialmente — duplicar já mudou a ordem de grandeza no caso medido. Propagação em massa (TF-1) ainda tem valor para **corrigir** um erro copiado 15 vezes (043 G-001) e para Editais cujos Perfis já existem (reuso), mas é evolução, com regra de conflito própria; não é lacuna que impede finalidade.
- Lacuna residual: TF-1 (aplicar Modalidades/marco a todos); a curva continua linear (043 G-002); a primeira oferta de cada família continua composta do zero (E3), agora a ~6 interações por Perfil depois do primeiro.
- Grupo do resíduo: B
- Impacto atual: médio-baixo depois da 043; alto só na correção de erro propagado.
- Próxima ação sugerida: nenhuma imediata; criar spec de TF-1 quando houver evidência de correção em massa (erro propagado) na operação real.
- Relações: E2 (o que é comum mora no Perfil); `doc/achado-atribuicoes-repetidas-por-polo.md` (15/09, mesmo 140/2025) e AX-11 (lote 4); B10 (botão no rodapé) é atenuado — a cópia nasce logo abaixo da origem.
- Confiança: alta.

### E2 · §6.2 (tabela) · §15 decisão 2 (parte "conteúdo comum") — o que o Edital declara uma vez mora no Perfil
- Origem: estudo §13 E2, §15 "Três decisões" item 2 (21/09).
- Problema original: Modalidades, desempate, requisitos gerais, carga horária e atribuições são do certame no Edital e do Perfil no sistema.
- Recomendação original: decidir quais podem migrar para o nível do Edital sem violar a razão de o marco ser do Perfil.
- Rastro posterior: decisão D5 (25/09) — "Mudar a propriedade para o Edital … Para Modalidades, a Constituição o impede; para o resto, é decisão que esta não toma." A 043 §2 reafirma que não move nada. Nenhuma decisão posterior sobre requisitos/carga/atribuições.
- Specs relacionadas: nenhuma.
- Evidência no código atual: `constitution.md:197` ("Cotas DEVEM ser definidas por Perfil"); `publicacoes/infrastructure/pdf.py:1711-1802` — requisitos, atribuições e remuneração continuam impressos por Perfil (a carga horária já vai só para a tabela comparativa quando há mais de um Perfil, `:1770-1784`).
- Estado atual: NÃO IMPLEMENTADO (decisão pendente, com a parte das Modalidades fechada pela Constituição)
- Ainda faz sentido?: parcialmente — para Modalidades, **não** (Constituição). Para requisitos gerais e atribuições, sim como pergunta de produto, porque é a única coisa que reduziria o **documento** (34 tabelas em 27 páginas), que duplicar não reduz.
- Lacuna residual: decisão do usuário sobre conteúdo comum não-cota.
- Grupo do resíduo: B
- Impacto atual: médio no documento gerado de Editais multipolo; baixo na autoria depois da 043.
- Próxima ação sugerida: decisão do usuário antes de qualquer spec.
- Relações: AX-11, `doc/achado-atribuicoes-repetidas-por-polo.md` (15/09, lote 4 — mesmo problema, anterior); causa estrutural da economia documental (Parte 4, A6/§9.D).
- Confiança: alta.

### §5.3 · A4 · E4 · §9.A.2 · §10 Caso 2 — o reuso herda em texto livre a cláusula de sorteio que a D-G3 manda substituir
- Origem: estudo §5.3, §9.A.2, §10 Caso 2, §11 A4, §13 E4 (21/09; revisto 25/09).
- Problema original: a cláusula de semente própria mora no texto livre; o reuso copia o texto inteiro sem marcar nada; a regra estruturada (fonte externa) e a prosa publicariam normas opostas, e nada acusa.
- Recomendação original: o reuso pedir a substituição (frente 3 do §15, "reuso com estado de revisão, inclusive a cláusula de sorteio").
- Rastro posterior: o banner do reuso passou a nomear as seções de texto (#163, bloco seguinte); **nada específico do sorteio**. A D-G3 (`doc/reavaliacao-ux-2026-09-18.md:724-736`) já dizia "a regra do reaproveitamento é a parte não óbvia" e "Cria: spec", e ficou "sem posição atribuída" (`:896`). A parte "Loteria Federal nos Editais antigos" é artefato do método (revisão 25/09). **(iii) sem dono.**
- Specs relacionadas: 021/035 (sorteio), 030 FR-429 (método comum copiado), 023.
- Evidência no código atual: `editais/domain/reaproveitamento.py:304-308` (copia as seções textuais com `content` inteiro) e `:310-320` (copia `drawMethod` comum como está, inclusive ocorrência e fonte); nenhuma verificação cruza texto livre com o método estruturado em `editais/domain/validation.py` (a coerência de sorteio, `_coerencia_do_metodo_de_sorteio`, é estrutural).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente — detectar contradição em prosa é inviável sem heurística frágil (overengineering). O que se sustenta é mais barato: no reuso, **não herdar a ocorrência** do sorteio (concurso/data da oferta anterior) e sinalizar a seção de Classificação/Disposições como herdada. Isso cabe no "estado de revisão" do bloco seguinte, e não precisa de spec própria de sorteio.
- Lacuna residual: nada impede publicar prosa herdada que contradiz o método estruturado; a ocorrência do sorteio anterior é copiada.
- Grupo do resíduo: B
- Impacto atual: médio, prospectivo — o primeiro reuso de um Edital de sorteio anterior à D-G3.
- Próxima ação sugerida: incluir na spec de "reuso com estado de revisão" (bloco seguinte); não criar spec separada.
- Relações: D-G3 (lote 18–19/09) — DUPLICADO na parte "regra do reaproveitamento" com a D-G3; E-4 (validação cruzada entre fontes, lote 16/09).
- Confiança: alta (código); média na recomendação.

### §10 Caso 7 · A8 · Quick win 15 · E9 · §15 frente 3 · B11 · §5.2 (resíduo) — o reuso copia tudo e avisa em bloco; não há estado "pendente de revisão"
- Origem: estudo §5.2 (último parágrafo), §10 Caso 7, §11 A8/B11, §12 item 15, §13 E9, §15 frente 3 (21/09); diário E1, E2, E4.
- Problema original: "Partir de um Edital anterior" copiou 10.900 caracteres de prosa de outro certame (função e curso do 14/2026) com banner que só nomeava "datas, vagas e prazos"; também herdou `immediateVacancies = 1`, a linha AC do quadro, códigos/denominações e regra de corte dos marcos, e datas sempre vencidas.
- Recomendação original: (a) nomear o texto no banner (QW15); (b) marcar campo a campo o que veio da origem, até alguém revisar (E9, frente 3).
- Rastro posterior: (a) **feito em 25/09**, `7b04cb3` (#163). (b) **sem dono** — nenhuma spec. A 023 já registrava o "quarto estado (*reaproveitada*)" como resíduo consciente, que "só se justifica depois de observar que alguém se confundiu" (`specs/023-criar-a-partir-de-edital-anterior/spec.md:238-243`) — o estudo é essa observação.
- Specs relacionadas: 023 FR-014 (aviso permanente, `spec.md:427-428`); 028 (cronograma reaproveitado vencido); `643e865` (#169, 25/09) corrigiu outro defeito de forma do reuso (`cutRule.governedStage` não remapeado).
- Evidência no código atual: `interface/templates/interface/compor_base.html:70-83` — o banner diz "datas, vagas e prazos e o texto de N seções de Conteúdo são da oferta anterior", com link; `interface/views.py:3662` — `secoes_de_texto = edital.secoes.exclude(content="").count()`: conta seções **com texto**, não seções **não revisadas** — depois de reescrever as sete, o banner continua dizendo que "são da oferta anterior"; teste `tests/interface/test_reaproveitar.py`.
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: sim para (b), no formato mínimo que a própria 023 esboçou (derivável da trilha, sem estado novo): etapa "reaproveitada" até ser gravada. Marcar **campo a campo** seria mais caro e provavelmente excessivo; por etapa (e por seção de texto) resolve o Caso 7.
- Lacuna residual: estado de revisão por etapa/seção; o banner não distingue o revisado do herdado; `immediateVacancies`/linha AC herdadas (B11) e códigos de marco de outro certame só são pegos por leitura humana.
- Grupo do resíduo: B
- Impacto atual: médio — risco de publicar prosa de outro certame é real e imutável depois de publicado; o banner reduziu o risco, não o eliminou.
- Próxima ação sugerida: criar spec (pequena) de "reuso com estado de revisão", absorvendo o resíduo do §5.3.
- Relações: B11 ABSORVIDO aqui; §5.2 (paredão de datas herdadas) é consequência do reuso, e o colapso do #163 já o mitiga (Parte 1, §5.12).
- Confiança: alta.

### §5.2 · E3 · §15 ("saíram desta lista") — Edital encerrado não publica; proposta de "registro de Edital já executado"
- Origem: estudo §5.2, §13 E3, §15 (21/09, primeira versão propunha spec de registro histórico).
- Problema original: o IMPEDE "o período de inscrições encerrou" impede publicar os cinco Editais reais; foi preciso falsear a data.
- Recomendação original (1ª versão): spec de registro de Edital já executado.
- Rastro posterior: **decisão do usuário de 25/09** (`doc/decisao-sem-carga-retroativa.md`): "O produto não terá fluxo de carga retroativa"; o IMPEDE é comportamento correto; estudos futuros compõem com datas futuras. Memória `sem-cadastro-retroativo-de-edital`.
- Evidência no código atual: o IMPEDE permanece (conferido pela decisão; não reabri a regra).
- Estado atual: CONTRADITO POR DECISÃO POSTERIOR — `doc/decisao-sem-carga-retroativa.md` (25/09).
- Ainda faz sentido?: não.
- Lacuna residual: consequência registrada — a primeira oferta de cada família é sempre composta do zero; mitigada pela 043.
- Grupo do resíduo: —
- Impacto atual: nenhum como defeito.
- Próxima ação sugerida: nenhuma.
- Relações: E1/043; D-G3 (distinta, a decisão diz por quê).
- Confiança: alta.

### B9 · Quick win 9 — "Partir de um Edital anterior" não copia a Descrição
- Origem: estudo §11 B9, §12 item 9 (21/09; revisto 25/09).
- Problema original: a descrição do Edital não vem no reuso.
- Recomendação original: copiá-la.
- Rastro posterior: revisão de 25/09 — "Não é quick win: a FR-007 da 023 diz que a identificação — número, ano, título e descrição — não deve ser copiada … registrado aqui, não tomado."
- Evidência no código atual: `specs/023-criar-a-partir-de-edital-anterior/spec.md:404` (FR-007); `editais/domain/reaproveitamento.py` `payload_do_conteudo` (`:289`) — "a identificação do Edital … não é conteúdo a copiar (`FR-007`)".
- Estado atual: NÃO IMPLEMENTADO (de propósito: contraria requisito escrito)
- Ainda faz sentido?: não — a descrição identifica o certame; copiá-la reproduziria o problema do Caso 7 (texto de outro certame) na capa.
- Lacuna residual: nenhuma.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: Caso 7/E9.
- Confiança: alta.

## Parte 4 — Edital original × documento gerado (§9, §9-bis, §10)

Renderizador conferido: `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (2.378 linhas;
`_tabela` `:972`, `_larguras_das_colunas` `:924`, `_cronograma` `:1831`, `_perfis` `:1711`,
`_metodo_do_marco` `:1308`, `_secoes` `:2095`, `_autoridade` `:2136`). Dos **três problemas de
fidelidade semântica** do §9.A: o 1 (reserva invertida) está **resolvido** (Parte 1, §5.1); o 2
(sorteio contraditório) é **artefato do método** quanto à origem e vive como risco de reuso (Parte 3,
§5.3); o 3 (hora inventada) **continua**. Dos **quatro defeitos de renderização** do §9-bis: os três
de tabela estão **resolvidos** pelo #164; o quarto (hora) é o mesmo do §9.A.3 e **continua**.

### B1 · Quick wins 7 e 14 · §9.C (Tabela 4) · §9-bis defeitos 1–3 — "Nº" cortado, datas em três linhas, linhas fundidas
- Origem: estudo §9.C, §9-bis ("Os defeitos de renderização"), §11 B1, §12 itens 7 e 14 (21/09); diário E7.D.
- Problema original: cabeçalho "Nº" cortado; números 10–13 e datas quebrando no meio; filete ausente entre linhas 7/8 (78/2026) e 6/7 (140/2025).
- Recomendação original: alargar colunas curtas; restaurar o filete ("células iguais", hipótese do estudo).
- Rastro posterior: corrigido em 25/09, `d0352f5` (#164). A causa do filete era outra — a linha levada à página seguinte perdia o início anotado e saía da grade; o estudo e o diário foram corrigidos (§9-bis item 2; diário `:511-515`). **(i) corrigido.**
- Specs relacionadas: 007/008 (documento), 021 (coluna Onde).
- Implementação encontrada: largura "curtas recebem o que pedem, longas repartem o resto"; início recuperado na quebra.
- Evidência no código atual: `publicacoes/infrastructure/pdf.py:751-759` (fio da linha que abre a página seguinte) e `:924-961` ("Longas no plural", `:934`); testes `tests/unit/publicacoes/test_tabela_do_documento.py:39` (duas colunas longas não espremem Nº/Início/Término), `:68`, `:85` (um fio por linha em cada página da tabela partida).
- Estado atual: RESOLVIDO
- Ainda faz sentido?: não.
- Lacuna residual: documentos já publicados não se regeneram (correto; memória `documento-publicado-nao-se-regenera`). Não conferi PDF renderizado nesta auditoria — a confirmação é pelos testes de composição, que medem a grade e as larguras, não a página rasterizada.
- Grupo do resíduo: —
- Impacto atual: nenhum para publicações novas.
- Próxima ação sugerida: nenhuma (opcional: gerar uma prévia de Edital grande e olhar a página, se houver dúvida).
- Relações: —
- Confiança: média-alta — código e testes sólidos; sem verificação visual.

### §9.A.3 · §9-bis defeito 4 · §10 Caso 3 — hora inventada impressa como norma ("às 00h")
- Origem: estudo §9.A.3, §9-bis item 4, §10 Caso 3 (21/09); diário A3, E7.A.2.
- Problema original: o Anexo I publica só data; o `datetime-local` obrigatório força uma hora, e o gerador a imprime ("05/08/2026, às 00h" em 9 de 11 eventos no 78/2026; 11 de 13 no 140/2025).
- Recomendação original: implícita — permitir Evento sem hora declarada (a frente 4 do §15 fala de "tabelas legíveis", não da hora).
- Rastro posterior: nenhum. Nenhum commit de 25/09 tocou nisso. **(iii) sem dono.**
- Specs relacionadas: 008 (instante em linguagem de Edital), 021/028 (Cronograma).
- Evidência no código atual: `interface/templates/interface/_evento.html:48-50` — Início é `datetime-local` com `required`; `publicacoes/infrastructure/humano.py:53-80` — `instante` sempre imprime a hora, e o docstring registra uma decisão anterior: "**Meia-noite é hora, e não ausência de hora** … agora diz `às 00h`"; `pdf.py:415-429` (`_instante`) e `:1845-1853` (Cronograma).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente — a regra "meia-noite é hora" é certa para prazo que termina à meia-noite; o que falta é o **estado** "sem hora declarada" (um Evento que o Edital data sem hora). Sem ele, o ato publicado afirma uma hora que a norma não fixou — pequeno em "Publicação do Edital", relevante em marcos de prazo.
- Lacuna residual: Evento só com data (modelo + tela + documento). Mexe no domínio de instantes (fuso, prazos calculados, janela recursal), por isso não é quick win.
- Grupo do resíduo: B
- Impacto atual: baixo-médio — toda publicação transcrita de Edital que só data eventos.
- Próxima ação sugerida: decisão do usuário (é modelagem de instante) antes de spec.
- Relações: §9-bis ("o campo admite menos estados do que a norma" — mesma forma de §5.1 e §5.9).
- Confiança: alta.

### A6 · Quick win 10 · §9.D · §10 Caso 4 — o bloco do método do sorteio sai uma vez por Perfil, rotulado "comum a este Edital"
- Origem: estudo §9.D, §10 Caso 4, §11 A6, §12 item 10 (21/09; revisto 25/09).
- Problema original: o gerador sabe que o método é comum e o imprime por marco (2× no 78/2026; 7× ou 16× nos grandes), cada cópia dizendo "Método: comum a este Edital".
- Recomendação original: imprimir uma vez na seção do Edital e fazer os marcos remeterem.
- Rastro posterior: revisão de 25/09 — "Não é quick win: a FR-465/466 da 032 e o contrato `marco-no-documento.md` exigem que a seção de cada marco de sorteio imprima o método que o governa … registrado aqui, não tomado."
- Specs relacionadas: 032 FR-465/466 (`specs/032-executabilidade-antes-de-publicar/spec.md:200-207`); 030 FR-429.
- Evidência no código atual: `publicacoes/infrastructure/pdf.py:1271-1288` (`_origem_do_metodo` → "comum a este Edital") e `:1308-1343` (`_metodo_do_marco` imprime os pares do método por marco).
- Estado atual: NÃO IMPLEMENTADO (de propósito: contraria requisito escrito; decisão do usuário pendente)
- Ainda faz sentido?: parcialmente — o requisito existe para que cada marco diga, no ato, que método o governa, e a 032 resolveu a divergência "próprio × comum" imprimindo sempre. Remeter ("comum a este Edital, ver item X") preserva essa garantia e economiza páginas; é mudança de requisito, pequena, e só vale nos Editais de sorteio multipolo.
- Lacuna residual: repetição documental do método.
- Grupo do resíduo: C
- Impacto atual: baixo — páginas a mais, sem erro normativo.
- Próxima ação sugerida: decisão do usuário sobre FR-465/466; se aprovada, spec curta ou emenda à 032.
- Relações: E2 (a repetição documental geral por Perfil — requisitos, convocação, modalidades — é a mesma causa, Parte 3); diário E7.E ("metade do documento dizendo dezesseis vezes o que o original diz uma vez").
- Confiança: alta.

### M6 · §9.B · §9.D — o total de vagas do Edital não aparece no documento
- Origem: estudo §9.B ("Perdidos por causa do sistema"), §9.D, §11 M6, §15 frente 4 (21/09).
- Problema original: o original publica "Total de Vagas: 61"; a Tabela "Perfis de vaga" não tem linha de total.
- Recomendação original: total de vagas no documento (frente 4).
- Rastro posterior: nenhum. **(iii) sem dono.**
- Evidência no código atual: `publicacoes/infrastructure/pdf.py:1658-1708` — `_quadro_de_perfis` monta uma linha por Perfil e nenhuma de total; com Perfil único não há tabela (`:1721-1722`).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim — é fato normativo do original, derivável da fonte estruturada (Princípio II), barato; o risco de overengineering é nulo. Cuidado: em cadastro de reserva (E8) o total é 0 e não deve sair como se fosse informação.
- Lacuna residual: linha de total (ou frase "Total: N vagas imediatas") quando há mais de um Perfil e alguma vaga.
- Grupo do resíduo: C
- Impacto atual: baixo — o leitor soma.
- Próxima ação sugerida: corrigir (direta) se o usuário quiser; conferir a fixture de bytes, que tem Perfil único e não pega a mudança (docstring `:1677-1680`).
- Relações: E8/M15.
- Confiança: alta.

### M7 · §9.B · §9-bis ("perdas de mesma natureza") — o documento publica o cargo, não a pessoa, a portaria, o local e a data
- Origem: estudo §9.B, §9-bis, §11 M7, §15 frente 4 (21/09); diário E7.B.
- Problema original: o original assina com o nome da diretora, "Portaria nº 797…", e "Vitória-ES, 05 de agosto de 2026"; o gerado traz só o cargo.
- Recomendação original: autoridade com nome e ato (frente 4).
- Rastro posterior: nenhum. **(iii) sem dono.**
- Specs relacionadas: 008 FR-033…FR-046 (autoridade como registro, não assinatura).
- Evidência no código atual: `publicacoes/domain/autoridades.py:27-40` — `Autoridade(chave, identificador, nome, cargo)`, sem portaria; `:43-63` — o catálogo **em código** traz cargos no campo `nome` ("Diretora do Cefor"); `publicacoes/infrastructure/pdf.py:2136-2165` (`_autoridade` imprime "Autoridade responsável pelo ato", nome e cargo) e `:2168-2193` (`_integridade`) — nada de local e data de expedição.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente — o **nome** já tem campo: é dado do catálogo (hoje de demonstração), não defeito de modelo; basta configurar. A **portaria de nomeação** e **local/data de expedição** não têm onde morar. Num ato administrativo real, identificar o signatário e o ato que o investe é esperado; mas o produto declarou (FR-036/037) que não é assinatura, e local/data é quase derivável da Publicação.
- Lacuna residual: portaria no catálogo; local e data de expedição no fecho (a data pode sair da Publicação; o local é constante institucional). Catálogo em código exige deploy a cada troca de dirigente — ponto a registrar.
- Grupo do resíduo: B
- Impacto atual: médio para uso real (o documento publicado não identifica a pessoa que praticou o ato, só o cargo, com o catálogo atual).
- Próxima ação sugerida: validar com o Cefor o que o fecho precisa conter; corrigir o catálogo antes de produção.
- Relações: `publicacoes/domain/autoridades.py` docstring ("declarado, e não cadastrado").
- Confiança: alta.

### M10 · A5 · E5 · §9.C · §9-bis ("estrutura documental") · §15 decisão 3 — seções fixas; inscrição e documentos antes dos Perfis; oito títulos viram parágrafos
- Origem: estudo §9.C, §9-bis, §11 A5/M10, §13 E5, §15 "Três decisões" item 3 (21/09).
- Problema original: 12 seções fixas não comportam matriz curricular, matrícula, certificado (78/2026) nem oito seções do 140/2025; a ordem põe DA INSCRIÇÃO e DOCUMENTOS antes de PERFIS.
- Recomendação original: decidir o conjunto de seções (conteúdo normativo) antes de spec.
- Rastro posterior: nenhum. A decisão 3 do §15 segue pendente com o usuário.
- Specs relacionadas: 006 FR-034/FR-036 (catálogo declarado, não gerenciável).
- Evidência no código atual: `editais/domain/secoes.py:1-10` ("O conjunto de seções e a ordem entre elas são definidos pelo sistema … É o que separa um documento institucional estruturado de um construtor de documentos") e `:83-110` — Da Inscrição (4), Documentos Exigidos (5), Perfis de Vaga (6).
- Estado atual: DUPLICADO / ABSORVIDO — em **AX-3** ("catálogo de Seções fechado, oito seções sem onde morar", `doc/auditoria-granularidade-normativa-2026-09-15.md`; re-varredura `doc/varredura-dos-dezessete-2026-09-19.md:35`, 🔴 aberto). Checagem pontual: catálogo inalterado.
- Ainda faz sentido?: sim como decisão — a ordem (vagas antes da inscrição) é o item mais barato e menos discutível; abrir o catálogo a seções livres é mais caro e toca o desenho da 006.
- Lacuna residual: decisão sobre o catálogo e a ordem.
- Grupo do resíduo: B
- Impacto atual: médio — hierarquia do documento normativo se perde em Editais com mais seções.
- Próxima ação sugerida: decisão do usuário (lote do AX-3).
- Relações: AX-3 (anterior, mesmo problema); B3 (numeração).
- Confiança: alta.

### B3 · §7.4 — a tela Conteúdo numera 12 seções; o PDF numera de outro jeito
- Origem: estudo §7.4, §11 B3 (21/09).
- Problema original: a tela mostra "1. Apresentação … 12. Disposições finais"; o PDF traz a apresentação sem número e renumera só as seções materializadas.
- Recomendação original: implícita — alinhar.
- Rastro posterior: nenhum. **(iii) sem dono.**
- Evidência no código atual: `interface/templates/interface/compor_conteudo.html:19` — `{{ secao.order }}. {{ secao.title }}`; `publicacoes/infrastructure/pdf.py:2088-2092` (preâmbulo sem número, FR-010) e `:2115-2118` (numera na materialização, FR-012).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, barato — a tela não precisa numerar (ou pode dizer que o número sai na materialização).
- Lacuna residual: número da tela ≠ número do documento.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: corrigir (direta).
- Relações: M10/AX-3.
- Confiança: alta.

### A9 · §9.B (citações não transcritas) · §9-bis ("A completude erra sempre no texto livre") · E10 · §15 decisão 1 — perda silenciosa do fundamento legal no texto livre
- Origem: estudo §1 item 6, §9.B, §9-bis, §11 A9, §13 E10, §15 decisão 1 (21/09; revisto 25/09 — "omissão do operador que o sistema não tem como perceber").
- Problema original: 0 de 7 atos normativos em dois Editais, LGPD entre eles; nada no fluxo percebe, porque o sistema não conhece a fonte.
- Recomendação original: primeiro decidir **redação no sistema ou transcrição** (E10); depois, se transcrição, anexar a fonte ou conferência estruturada.
- Rastro posterior: decisão E10 **pendente** (não há `doc/decisao-*` sobre isso; `grep -il transcri doc/decisao-*.md` vazio).
- Evidência no código atual: as seções textuais são `content` livre (`editais/domain/secoes.py`, `TEXTUAL`); nenhuma verificação de citação em `editais/domain/validation.py`.
- Estado atual: NÃO IMPLEMENTADO (aguarda decisão E10)
- Ainda faz sentido?: parcialmente — sem a decisão E10, qualquer mecanismo seria especulativo; um checklist de conferência antes de homologar é barato, "conhecer a fonte" é caro e provavelmente de outro sistema (redação).
- Lacuna residual: decisão de processo do Cefor.
- Grupo do resíduo: C
- Impacto atual: médio se o Cefor continuar transcrevendo do Word; nulo se redigir no sistema.
- Próxima ação sugerida: decisão do usuário (E10).
- Relações: AX-12 (numeração dos anexos não verificada) é da mesma família "o sistema não confere o texto que publica"; §9.B Anexo III LGPD citado sem existir.
- Confiança: alta.

### A10 · E7 · §10 Caso 8 · §9-bis ("tabelas que não têm objeto") — submodalidade de PPIQ e ordem de convocação sem forma; a publicação remete a item que não contém
- Origem: estudo §9-bis, §10 Caso 8, §11 A10, §13 E7 (21/09); diário E6, E7.B.
- Problema original: o 140/2025 convoca por PPIQ (Pretos/Pardos), (Indígenas), (Quilombolas) com cascata, numa tabela de 50 posições; Modalidade é plana; o texto publicado cita "tabela do item 10.5", que o documento não tem.
- Recomendação original: objeto para ordem de convocação e para submodalidade.
- Rastro posterior: a 044 o registra como limite e o deixa **fora** (`spec.md:60-76`, `:603-604`, `:617`).
- Evidência no código atual: nenhuma ocorrência de "submodalidade", "alternância" ou "ordem de convocação" em `backend/processo_seletivo/**/*.py`.
- Estado atual: DUPLICADO / ABSORVIDO — em **AX-15** (submodalidades de PPIQ, `doc/auditoria-granularidade-normativa-2026-09-15.md:918`; 🔴 aberto em `doc/varredura-dos-dezessete-2026-09-19.md:47`) e em **P-1/P-2** (`doc/achados-editais-externos.md:75-98`, "o de cadastro de reserva declara ordem").
- Ainda faz sentido?: sim — tem consequência executável (convocação), não só redacional. Mas é do lote 4/lote 2.
- Lacuna residual: como nos IDs de destino.
- Grupo do resíduo: B
- Impacto atual: médio nos Editais de pessoal com cotas por submodalidade; e 3 documentos do 140/2025 seguem facultativos mesmo com a 044.
- Próxima ação sugerida: tratar no lote do AX-15 / P-1.
- Relações: AX-15, P-1, P-2; 044 §1.
- Confiança: alta.

### M15 · E8 — cadastro de reserva sem quantidade: quadro "Ampla concorrência | 0" ao lado de 5%/30%/25%, e 32 avisos sem resposta certa
- Origem: estudo §11 M15, §13 E8 (21/09); diário E7.A.4, E9.
- Problema original: o sistema amarra convocação a quantidade publicada; Edital só de cadastro de reserva publica quadro degenerado e dispara avisos por Perfil.
- Recomendação original: nenhuma de desenho — questão estrutural.
- Rastro posterior: nenhum no escopo deste lote.
- Evidência no código atual: `editais/domain/validation.py:2479`, `:2516`, `:2547` (família "O Perfil X publica N vaga(s) imediata(s) …") e `:1738` ("não declara regra de corte") — continuam por Perfil; `publicacoes/infrastructure/pdf.py:1497-1550` (`_quadro_de_vagas_do_perfil`) imprime a linha geral com 0.
- Estado atual: DUPLICADO / ABSORVIDO — em **P-2** ("A oferta tem quantidade conhecida? … Ocupar sem quantidade é caso normal, não borda", `doc/achados-editais-externos.md:90-98`) e **P-1** (ordem nominal); lote 2.
- Ainda faz sentido?: sim — é o modelo; duas das quatro famílias de aviso da Revisão (§5.12) nascem daqui.
- Lacuna residual: como em P-1/P-2.
- Grupo do resíduo: B
- Impacto atual: médio para Editais de cadastro de reserva (a amostra tem dois: 140/2025 e 173/2025).
- Próxima ação sugerida: tratar no lote de P-1/P-2.
- Relações: §5.12 (avisos por Perfil), M6 (total 0).
- Confiança: alta.

## Parte 5 — Arquitetura de informação (§7) e agravantes de escala (§8), baixo impacto (§11 B)

Itens de baixo impacto, conferidos um a um, em blocos curtos.

### §7.1 — Processo × Edital: criar exige inventar duas strings que o Edital não tem
- Origem: estudo §7.1 (21/09); diário A1.
- Problema original: 4 de 5 Editais da amostra são Edital único; "Identificação institucional" e "Título" do Processo não existem no documento-fonte e acabam repetindo o título do Edital.
- Recomendação original: implícita — reduzir a redigitação no caso Edital único.
- Rastro posterior: nenhum. A 040–042 (visão institucional) reforçou o Processo como unidade de leitura, não simplificou a criação.
- Evidência no código atual: `interface/templates/interface/processo_criar.html:33-77` — Identificação institucional*, Título*, Número*, Ano*, Título do Edital*, Descrição.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente — o modelo Processo ⊃ Edital é do domínio (`constitution.md:43`) e não deve sumir; um padrão "Título do Processo = Título do Edital" quando vazio seria o bastante.
- Lacuna residual: redigitação de 2 campos por Processo novo.
- Grupo do resíduo: C
- Impacto atual: baixo (uma vez por Processo).
- Próxima ação sugerida: nenhuma (opcional).
- Relações: auditoria UX 13/09 ("A diferença entre Processo e Edital, ensinada em uma frase na tela que os cria", `doc/auditoria-exploratoria-ux-2026-09-13.md:699`) — lote 3.
- Confiança: alta.

### §7.2 — "Perfil de Vaga" colide com colunas "Perfil" dos Editais
- Origem: estudo §7.2 (21/09); diário A2.
- Problema original: nos Editais, "Perfil da Vaga"/"PERFIL" é uma coluna (público, formação); no sistema, é a oportunidade inteira.
- Recomendação original: nenhuma explícita.
- Evidência no código atual: termo fixado no vocabulário da Constituição, `.specify/memory/constitution.md:43` ("… Publicação, Perfil de Vaga, Vaga, …").
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: não — é termo constitucional; trocá-lo custaria o vocabulário inteiro por um ganho de ajuda de tela.
- Lacuna residual: nenhuma além de ajuda contextual.
- Grupo do resíduo: —
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma.
- Relações: —
- Confiança: alta.

### §7.3 · B4 — campos de vínculo de trabalho numa vaga de aluno; Descrição de uma linha
- Origem: estudo §7.3, §11 B4 (21/09); diário A2.
- Problema original: Remuneração e Atribuições ficam vazias nos Editais de curso; "Dias e horários" coube em `Descrição`, que é `<input>` de uma linha, enquanto Atribuições é `<textarea>`.
- Recomendação original: implícita.
- Rastro posterior: nenhum.
- Evidência no código atual: `interface/templates/interface/_perfil.html:45-47` (Descrição `<input type="text">`), `:55` (Remuneração, opcional), `:67-68` (Atribuições `<textarea>`); o PDF omite o que está vazio (`publicacoes/infrastructure/pdf.py:1752-1784`).
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente — os campos são opcionais e o PDF os omite, então o custo é só leitura; a Descrição como `<textarea>` é troca barata.
- Lacuna residual: Descrição de uma linha.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: nenhuma (opcional).
- Relações: AX-5 (Curso/Área/Campus não existem, lote 4) — mesma raiz: o Perfil foi modelado sobre o Edital de pessoal.
- Confiança: alta.

### §7.5 · B5 — Cronograma sem painel "Como preencher"; ajudas em `span.oculto`
- Origem: estudo §7.5, §11 B5 (21/09).
- Problema original: "Vazio para evento pontual" e "Sala, endereço, canal…" só para leitor de tela; a etapa é a única sem painel "Como preencher".
- Rastro posterior: nenhum.
- Evidência no código atual: `interface/templates/interface/_evento.html:44,65` (`span.oculto`); `como-preencher` existe em `compor_anexos.html`, `compor_etapas.html`, `compor_inscricao.html`, `compor_perfis.html` — não em `compor_cronograma.html`. A regra do repositório proíbe `class="ajuda"` nos cartões (`tests/interface/test_medida_dos_campos.py::test_nenhum_cartao_do_assistente_carrega_ajuda_visivel`; memória `ajuda-visivel-e-proibida-nos-cartoes`), então a correção é o painel, não a classe.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim, barato.
- Lacuna residual: painel `como-preencher` no Cronograma.
- Grupo do resíduo: C
- Impacto atual: baixo.
- Próxima ação sugerida: corrigir (direta).
- Relações: família "ajuda invisível" das auditorias UX 13/09 e 16/09 (lote 3).
- Confiança: alta.

### §8 (agravantes) · B10 · M16 — "Acrescentar" no rodapé; reordenar ↑/↓; `<select multiple>` de "Etapas que entram na ordem"
- Origem: estudo §8, §11 B10/M16 (21/09); diário A3, "O `<select multiple>`".
- Problema original: o botão desce a cada inserção; mover o 11º Evento para o 2º custa 9 cliques; no `<select multiple>` o clique simples reinicia a seleção, e no macOS só `cmd+clique` acrescenta.
- Rastro posterior: 043 atenuou o B10 para Perfis — a cópia nasce **logo abaixo** da origem (`specs/043-duplicar-perfil/spec.md` US1, cenário 1). Nada mais.
- Evidência no código atual: `interface/templates/interface/compor_perfis.html:98` e `compor_cronograma.html:39` (`hx-swap="beforeend"`); `interface/templates/interface/_marco.html:104-114` — `<select … multiple>` com `hx-trigger="change"` que **reconstrói o cartão** a cada mudança; nenhuma instrução de `cmd`/`ctrl` na tela.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: sim para o M16 — é campo obrigatório (salvo sorteio), repetido por marco (16× no 140/2025), e o comportamento nativo engana; caixas de marcação resolvem sem custo de domínio. B10/reordenar: conveniência.
- Lacuna residual: M16 (trocar por caixas de marcação); B10 e reordenar (conveniência).
- Grupo do resíduo: B (M16) · C (B10, reordenar)
- Impacto atual: M16 médio em Editais com vários marcos e mais de uma Etapa classificatória; B10 baixo.
- Próxima ação sugerida: corrigir M16 (direta); nenhuma para B10.
- Relações: —
- Confiança: alta.

### M9 · §6.2 (última linha) — Tipo **e** Descrição obrigatórios por Evento; Tipo é texto livre
- Origem: estudo §6.2, §11 M9 (21/09); diário A3.
- Problema original: o Anexo I traz um rótulo por linha; o formulário pede dois; Tipo sem vocabulário.
- Rastro posterior: nenhum.
- Evidência no código atual: `interface/templates/interface/_evento.html:18-26` — `type` e `description`, ambos `required`, `type` texto livre com placeholder.
- Estado atual: NÃO IMPLEMENTADO
- Ainda faz sentido?: parcialmente — o sistema não depende do Tipo para semântica (o período de inscrição é marcado por `isRegistrationPeriod`, e Etapas apontam Evento por identidade), então o Tipo obrigatório é redigitação; torná-lo opcional (ou derivar da Descrição) é barato, mas mexe no contrato do Evento.
- Lacuna residual: um campo redundante por Evento.
- Grupo do resíduo: C
- Impacto atual: baixo (~13 campos por Edital).
- Próxima ação sugerida: nenhuma (opcional).
- Relações: —
- Confiança: média — não conferi se algum consumidor lê `type` além do PDF (`pdf.py:1849` usa `description` e só recua para `type`).

### B6 — etapa Anexos sem "Salvar rascunho"
- Origem: estudo §11 B6 (21/09).
- Problema original: ao contrário das demais etapas, Anexos não tem "Salvar rascunho".
- Evidência no código atual: `interface/templates/interface/compor_anexos.html:110-137,177` — cada ação (salvar rótulo, substituir, mover, remover, acrescentar) é um `submit` próprio que grava na hora.
- Estado atual: SUPERADO / OBSOLETO — não há rascunho a salvar: a etapa é de ações imediatas por anexo, por desenho.
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: —
- Confiança: média — inferência pelo template; não percorri a tela.

### B7 · §3 ("nada na tela diz que são precisos dois papéis") — papéis pela string técnica no seletor de identidade
- Origem: estudo §3, §11 B7 (21/09); diário A0.
- Evidência no código atual: `interface/templates/interface/identificar.html:50-56` — lista `papel.1|join:", "` (capacidades técnicas).
- Estado atual: SUPERADO / OBSOLETO — o seletor de identidade é ferramenta de desenvolvimento/demonstração: exige `INTERFACE_SELETOR_IDENTIDADE=true`, e "produção recusa subir com eles" (`CLAUDE.md`, "`/gestao/` não abre sem o seletor de identidade").
- Ainda faz sentido?: não — não é tela de operador real.
- Lacuna residual: nenhuma no produto. A segregação de funções (dois papéis, duas pessoas) é explicada na tela de publicação, que é a que vai para produção (estudo §16).
- Grupo do resíduo: —
- Impacto atual: nenhum em produção.
- Próxima ação sugerida: nenhuma.
- Relações: —
- Confiança: alta.

### B8 — "Cancelar Processo — IRREVERSÍVEL — está impedido", sem dizer por quê
- Origem: estudo §11 B8 (21/09). **Sem registro no diário** (`grep -i cancelar` vazio).
- Evidência no código atual: `interface/templates/interface/processo_detalhe.html:218-229` — `<details>` "O cancelamento do Processo está impedido." com a lista dos Editais que precisam ser encerrados ou cancelados antes, e "Cancelar o Processo não cancela os Editais". O mesmo bloco já existia no commit-base do estudo (`git show 396e75c:…/processo_detalhe.html`, linha 220).
- Estado atual: SUPERADO / OBSOLETO — a explicação existia antes do estudo (038), recolhida num `details`; o achado provavelmente leu só o `summary`.
- Ainda faz sentido?: não como descrito; no máximo, abrir o `details` por padrão.
- Lacuna residual: nenhuma relevante.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: 038.
- Confiança: média — evidência fina no estudo.

## Parte 6 — PR #171, questões estruturais restantes e o complemento de investigação

### PR #171 · `doc/achado-valor-de-fato-sem-gatilho.md` (na main desde 26/09) — `ValorDeFato` é append-only por uma camada só
- Origem: PR aberto #171 (`claude/achado-valor-de-fato-sem-gatilho`, 25–26/09, só documentação), nascido de `research.md` R-005/R-014 da 044; memória `valor-de-fato-corrigir-depois-da-044`.
- Problema original: `inscricoes_valordefato` (fatos congelados no envio, entrada da classificação) está em `TABELAS_APPEND_ONLY`, mas **não tem** gatilho `BEFORE UPDATE OR DELETE` nem recusa em `save`/`delete`; quem conecta com privilégio (migration de dados, shell com credencial de migração, suíte como superusuário) reescreve em silêncio. Nenhum guardião vê.
- Recomendação original: gatilho + guarda de modelo como `inscricoes/0006`, **depois** da 044, para não abrir duas pontas no grafo de migrations. `PosicaoNaOrdem`, `RevisaoEdital`, `GeracaoDeArquivo` (duas camadas de três) ficam só registradas, por decisão do usuário.
- Rastro posterior: decisão do usuário de 25/09 (no corpo do PR e na memória) — corrigir depois da 044.
- Specs relacionadas: 015 (fatos declarados, D-2); 044 (dona da `0005`).
- Evidência no código atual: `backend/processo_seletivo/seguranca/papeis.py:39` (na lista append-only); `backend/processo_seletivo/inscricoes/models.py:137-183` — `ValorDeFato` sem `save`/`delete` sobrescritos (só `Meta` e `__str__`); `inscricoes/migrations/0004_valor_de_fato.py` sem `RunSQL`; `backend/tests/migrations/test_migrations.py:34-91` — `TRIGGERS_POR_APP` sem a chave `inscricoes`; única escrita é o `bulk_create` do envio, `inscricoes/application/submissao.py:368`. Na branch da 044, `ValorDeFato` continua igual (a 044 dá três camadas só à tabela nova).
- Estado atual: NÃO IMPLEMENTADO (achado registrado, e mesclado pelo #171 em 26/09; correção decidida, e livre desde que a `0005` entrou com o #173)
- Ainda faz sentido?: sim — contradiz a regra de engenharia do projeto ("duas camadas independentes, e nenhuma delas é contornável", `CLAUDE.md`; docstring de `papeis.py`) e o Princípio II (`constitution.md:65-75`: regras e entradas históricas reproduzíveis). Custo baixo, molde pronto (`recursos/migrations/0002_ato_de_instrucao.py`). Não há dano observado.
- Lacuna residual: gatilho e guarda de modelo; o guardião de `test_imutabilidade_do_historico.py:200` só confere uma direção.
- Grupo do resíduo: A
- Impacto atual: baixo na prática (ninguém escreve fora do envio), alto em garantia.
- Próxima ação sugerida: corrigir — `inscricoes/0006`. A implementação da 044 chegou à main pelo #173, com a `0005`.
- Relações: 044 R-005/R-014; `doc/descoberta-018-decisao-c-superacao-de-resultado.md:138` (descreve "papel + modelo", errado para menos).
- Confiança: alta.

### E11 — ficha de avaliação sem forma (tabela de títulos com pontos por item e teto por natureza)
- Origem: estudo §13 E11 (21/09).
- Problema original: a Etapa só tem nota mínima, máxima e peso; o Anexo IV (títulos) vira PDF ou texto livre, e o sistema não confere a pontuação que publica.
- Rastro posterior: nenhum neste lote.
- Evidência no código atual: não reabri o modelo de Etapa; a re-varredura de 19/09 dá o AX-4 como 🔴 aberto, "modelo inalterado" (`doc/varredura-dos-dezessete-2026-09-19.md:36`).
- Estado atual: DUPLICADO / ABSORVIDO — em **AX-4** ("Ficha de Avaliação varia por curso; a Etapa é do Edital", `doc/auditoria-granularidade-normativa-2026-09-15.md`), lote 4.
- Ainda faz sentido?: sim, como evolução — é o lote 4 que deve medir.
- Lacuna residual: como no AX-4.
- Grupo do resíduo: B
- Impacto atual: médio em Editais de prova de títulos.
- Próxima ação sugerida: tratar no lote do AX-4.
- Relações: AX-4.
- Confiança: média — checagem pontual pelo relatório de 19/09, não pelo código.

### §15 "Três decisões, antes de qualquer spec" — estado de cada uma
- Origem: estudo §15 (21/09, reordenado em 25/09).
- Problema original: três decisões de produto/processo precedem as specs: (1) redação no sistema ou transcrição (E10); (2) conteúdo comum e documento condicional, juntas (E2 + E6); (3) conjunto de seções do documento (E5).
- Rastro posterior: (2) **parte documental decidida** em 25/09 (`doc/decisao-recorte-documental.md`, D1–D5), virou a 044 e a 043 (duplicar); a parte "conteúdo comum" ficou explicitamente não tomada (D5). (1) e (3) **pendentes** — nenhum `doc/decisao-*` as registra.
- Evidência no código atual: `doc/decisao-recorte-documental.md` ("O que foi decidido"); ausência de decisão sobre transcrição e seções.
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: sim — as duas pendentes governam A9 e A5/M10/E5 (Parte 4).
- Lacuna residual: decisões 1 e 3; a metade "conteúdo comum" da 2.
- Grupo do resíduo: B
- Impacto atual: bloqueia as frentes de fidelidade e de estrutura documental.
- Próxima ação sugerida: levar ao usuário (governança é dele).
- Relações: E10, E2, E5; AX-3.
- Confiança: alta.

### §14 · §15 ("Antes da frente 1, um complemento pequeno") — lacunas de investigação do estudo
- Origem: estudo §14 e o último parágrafo do §15 (21/09): não exercitou Retificação; não enviou Anexo; não mediu tempo com operador; economia do reuso N→N+1 não sustentada; três Editais não contados; portal não avaliado. Complemento pedido: compor com datas futuras N e N+1 por reuso, uma Retificação, candidatos AC/PcD/PPIQ no portal, anexos enviados de verdade.
- Rastro posterior: **portal e análise documental feitos** em 25/09 (#160 e #165, Editais 902/903 com datas futuras, três inscrições enviadas com PDF, uma Retificação que abriu a análise). A 043 mediu autoria com duplicar (101 interações). **Não feitos**: N→N+1 por reuso medido com o método; Retificação do ponto de vista de custo de autoria; anexos do Edital (etapa Anexos) enviados; tempo com operador humano.
- Evidência no código atual: não se aplica (investigação); `doc/conferencia-envio-e-analise-documental.md` §"Cenário"; `specs/043-duplicar-perfil/rastreabilidade.md:106-120`.
- Estado atual: PARCIALMENTE RESOLVIDO
- Ainda faz sentido?: parcialmente — só o item do portal condicionava a frente 1, e está feito; o resto informa as frentes de reuso (E9) e de documento, e vale a pena antes de especificar a de "reuso com estado de revisão".
- Lacuna residual: medir N→N+1 por reuso e uma Retificação de autoria; enviar anexos reais.
- Grupo do resíduo: C
- Impacto atual: baixo (evidência, não defeito).
- Próxima ação sugerida: validar (percurso com datas futuras) antes da spec de reuso com estado de revisão.
- Relações: E9, A8.
- Confiança: alta.

---

## (1) Tabela-resumo

Legenda da origem do fechamento: **(i)** corrigido em 25/09 · **(ii)** deliberadamente para a 044 · **(iii)** sem dono.

| ID | Título | Estado | Grupo | Próxima ação |
|---|---|---|---|---|
| §5.1 · A1 · QW1 · §9.A.1 · Caso 1 | Cadastro Reserva limitado inalcançável | RESOLVIDO (i, #159) | — | nenhuma |
| §5.4 · M2 · M3 · QW3–4 | rótulos decisórios sem `*`; IMPEDE com UUID | RESOLVIDO (i, #162/#163) | — | nenhuma |
| §5.5 · M1 · QW2 | seletor de Evento ambíguo | RESOLVIDO (i, #162) | — | nenhuma |
| §5.6 · M5 · QW5 | Casas decimais/Arredondamento/Alvo no sorteio | PARCIALMENTE RESOLVIDO (Alvo i; resto decisão pendente) | C | decisão do usuário |
| §5.7 · M4 | quadro mostra "Modalidade nova" até gravar | NÃO IMPLEMENTADO (iii) | B | corrigir (direta) |
| §5.11 · M12 | seletor da ampla com rótulo velho até gravar | NÃO IMPLEMENTADO (iii) | B | corrigir junto com M4 |
| §5.8 · B2 · QW8 | bloco do quadro não some | RESOLVIDO (i, #162) | — | nenhuma |
| §5.10 · M11 · QW11 | campo dependente não se limpa | RESOLVIDO (servidor já descartava; #162) | — | nenhuma |
| §5.12 · M8 · M14 · QW6 · QW13 | Revisão soterra o IMPEDE; âncora do ano | PARCIALMENTE RESOLVIDO (colapso por Evento i; por Perfil e severidade iii; âncora decisão) | B | corrigir (direta) + decisão FR-344 |
| §5.9 · A7 · E6 (modalidade) · Caso 5 · frente 1 · D1/D1a/D3 | "todo PcD" sem forma; obrigatórios como facultativos | RESOLVIDO (ii, #173, mesclado em 26/09) | — | T065, se a medição for pedida |
| portal §3 · #161 | "Todos os Perfis" + Modalidade de um Perfil diverge | RESOLVIDO (i contenção; ii, #173, mesclado em 26/09) | — | conferir o acervo `[VALIDAR]` |
| conferência §3/§6 · D4 | Mesa recalcula; sem "não se aplica"; nada registra o pedido | RESOLVIDO (ii, #173, mesclado em 26/09; Mesa percorrida) | — | nenhuma |
| conferência §1/§3 · D2 diretas · #167 | instrução na Mesa; facultativo na Revisão | RESOLVIDO (i, #167) — resíduo: cartão público sem marca (iii) | C | corrigir (opcional) |
| E6 (candidato) · D2 | sexo/idade/vínculo sem forma | CONTRADITO POR DECISÃO POSTERIOR (D2, `doc/decisao-recorte-documental.md`) | B | nenhuma até reabrir D2 |
| conferência · D4.3 | "O que mudou" omite recorte do documento | NÃO IMPLEMENTADO (iii; decidido, não feito) | A | corrigir (direta) |
| conferência §3/§7 · 044 riscos | filtro de concorrência sem Perfil | RESOLVIDO (PR #172, mesclado em 26/09) | C | nenhuma |
| conferência §3–§5 | lista da Mesa sem Perfil; sem juízo por documento | NÃO IMPLEMENTADO | C | nenhuma (reavaliar após 044) |
| §6.2 · §6.4 · §8 · A2 · E1 · frente 2 | sem reuso dentro do Edital | PARCIALMENTE RESOLVIDO (043; TF-1 iii) | B | spec TF-1 só com evidência |
| E2 | o comum do Edital mora no Perfil | NÃO IMPLEMENTADO (decisão pendente; Modalidade fechada pela Constituição) | B | decisão do usuário |
| §5.3 · A4 · E4 · §9.A.2 · Caso 2 | reuso herda cláusula de sorteio em prosa | NÃO IMPLEMENTADO (iii) | B | incluir na spec de reuso com revisão |
| Caso 7 · A8 · QW15 · E9 · frente 3 · B11 | reuso sem estado de revisão | PARCIALMENTE RESOLVIDO (banner i; estado iii) | B | criar spec (pequena) |
| §5.2 · E3 | Edital encerrado não publica / registro histórico | CONTRADITO POR DECISÃO POSTERIOR (`doc/decisao-sem-carga-retroativa.md`) | — | nenhuma |
| B9 · QW9 | reuso não copia a Descrição | NÃO IMPLEMENTADO (de propósito, FR-007 da 023) | — | nenhuma |
| B1 · QW7 · QW14 · §9-bis 1–3 | tabela: Nº cortado, datas quebradas, linhas fundidas | RESOLVIDO (i, #164) | — | nenhuma |
| §9.A.3 · §9-bis 4 · Caso 3 | hora inventada "às 00h" | NÃO IMPLEMENTADO (iii) | B | decisão (modelo de instante) |
| A6 · QW10 · §9.D · Caso 4 | método do sorteio impresso por marco | NÃO IMPLEMENTADO (de propósito, FR-465/466 da 032) | C | decisão do usuário |
| M6 | total de vagas ausente | NÃO IMPLEMENTADO (iii) | C | corrigir (opcional) |
| M7 | cargo sem nome, portaria, local e data | NÃO IMPLEMENTADO (iii) | B | validar com o Cefor; catálogo antes de produção |
| M10 · A5 · E5 · §15 decisão 3 | seções fixas; ordem inscrição→perfis | DUPLICADO / ABSORVIDO (AX-3) | B | decisão (lote do AX-3) |
| B3 · §7.4 | numeração tela × PDF | NÃO IMPLEMENTADO (iii) | C | corrigir (direta) |
| A9 · E10 · §15 decisão 1 | citações legais perdidas no texto livre | NÃO IMPLEMENTADO (aguarda E10) | C | decisão do usuário |
| A10 · E7 · Caso 8 | submodalidade e ordem de convocação | DUPLICADO / ABSORVIDO (AX-15; P-1/P-2) | B | lote do AX-15 / P-1 |
| M15 · E8 | cadastro de reserva sem quantidade | DUPLICADO / ABSORVIDO (P-2; P-1) | B | lote de P-1/P-2 |
| §7.1 | Processo × Edital: duas strings inventadas | NÃO IMPLEMENTADO | C | nenhuma |
| §7.2 | "Perfil de Vaga" colide com colunas do Edital | NÃO IMPLEMENTADO (termo constitucional) | — | nenhuma |
| §7.3 · B4 | campos de vínculo em vaga de aluno; Descrição de uma linha | NÃO IMPLEMENTADO | C | nenhuma |
| §7.5 · B5 | Cronograma sem "Como preencher" | NÃO IMPLEMENTADO (iii) | C | corrigir (direta) |
| §8 · B10 · M16 | botão no rodapé; ↑/↓; `<select multiple>` | NÃO IMPLEMENTADO (B10 atenuado pela 043) | B (M16) · C | corrigir M16 |
| M9 | Tipo e Descrição obrigatórios por Evento | NÃO IMPLEMENTADO | C | nenhuma |
| B6 | Anexos sem "Salvar rascunho" | SUPERADO / OBSOLETO (ações imediatas por desenho) | — | nenhuma |
| B7 | papéis pela string técnica | SUPERADO / OBSOLETO (seletor é de demonstração) | — | nenhuma |
| B8 | cancelamento impedido sem dizer por quê | SUPERADO / OBSOLETO (explicação existe desde a 038) | — | nenhuma |
| PR #171 | ValorDeFato append-only por uma camada | NÃO IMPLEMENTADO (decidido; a 044 já está na main) | A | corrigir: `inscricoes/0006` |
| E11 | ficha de avaliação sem forma | DUPLICADO / ABSORVIDO (AX-4) | B | lote do AX-4 |
| §15 três decisões | redação×transcrição; comum+condicional; seções | PARCIALMENTE RESOLVIDO (documental decidido; 1 e 3 pendentes) | B | levar ao usuário |
| §14 · §15 complemento | lacunas de investigação | PARCIALMENTE RESOLVIDO (portal e análise feitos) | C | validar (N→N+1, Retificação, anexos) |

## (2) Contagens por estado (46 blocos)

| Estado | Quantos |
|---|---:|
| RESOLVIDO | 11 |
| RESOLVIDO POR OUTRO CAMINHO | 0 |
| PARCIALMENTE RESOLVIDO | 6 |
| NÃO IMPLEMENTADO | 20 |
| IMPLEMENTADO, MAS NÃO VALIDADO | 0 |
| SUPERADO / OBSOLETO | 3 |
| DUPLICADO / ABSORVIDO | 4 |
| CONTRADITO POR DECISÃO POSTERIOR | 2 |

Dos 20 "não implementados", **4 são de propósito** porque a recomendação contraria requisito escrito ou
termo constitucional (B9/FR-007 da 023, A6/FR-465–466 da 032, §7.2/Constituição, e a parte "âncora"
do §5.12/FR-344) — a revisão de 25/09 os registrou e não os tomou. Resíduo por grupo, nos itens ainda
abertos: **A = 2** ("O que mudou" sem o recorte, ValorDeFato; o recorte transversal, a contenção #161 e
a lista gravada saíram em 26/09, com o merge do #173); **B = 16** (inclui os 4 absorvidos por outros lotes e o resíduo da D2); **C = 14** (inclui B10 junto com M16 e o resíduo do #167).

Separação pedida — **(i) corrigido em 25/09**: §5.1, §5.4, §5.5, §5.8, §5.10, Alvo do §5.6, colapso
por Evento do §5.12, banner do reuso, tabela do documento (B1), contenção #161, instrução na Mesa e
facultativo na Revisão (#167), duplicar Perfil (043). **(ii) para a 044** (mesclada pelo
#173 em 26/09): recorte transversal, terceira saída da #161, divergência nas inscrições antigas, lista
gravada, "não se aplica", Mesa/consulta/portal lendo a lista. **(iii) sem dono**: M4, M12, §5.12 por
Perfil e por severidade, "O que mudou" com `profileId`/`modalityId`, cartão público sem marca de
facultativo, estado de revisão do reuso (E9) e sorteio herdado (A4), hora inventada, total de vagas,
autoridade com portaria/local/data, B3, B5, M16.

## (3) Achados NOVOS encontrados de passagem

1. **O banner do reuso conta seções com texto, não seções herdadas.** `interface/views.py:3662`
   (`edital.secoes.exclude(content="").count()`): depois de reescrever as sete seções, o aviso continua
   dizendo que "o texto de 7 seções de Conteúdo são da oferta anterior até que alguém os revise". O #163
   acertou o que nomear, mas a contagem não distingue revisado de herdado — o aviso vira ruído
   permanente, que é o risco de ele deixar de ser lido. Pequeno; entra na spec de E9.
2. **Precondição do conserto do ValorDeFato está ambígua.** O PR #171 e a memória
   `valor-de-fato-corrigir-depois-da-044` dizem "depois que a 044 (#168) for mergeada". O #168 **já está
   mesclado** (`bb774d9`), mas era só a spec; a `inscricoes/0005` está na branch da 044, não na main.
   Quem ler "#168 mesclado" e escrever a `0006` agora criaria a ponta dupla no grafo que a decisão quis
   evitar. A memória manda conferir `git log origin/main -- …/0005*`, o que protege — mas o texto do PR
   não. **Desfecho:** a `0005` entrou na main com o #173 em 26/09, e a ambiguidade deixou de importar.
3. **A justificativa do M4 no código não se sustenta por inteiro.** `interface/views.py:2470-2475` diz
   que atualizar o rótulo exigiria espelhar por JavaScript, "que a CSP desta interface não admite"; o
   mesmo cartão já reconstrói o quadro por `hx-get` + `hx-include="closest fieldset"` sem JS inline
   (`_perfil.html:187-192`). Não é defeito; é um comentário que desencoraja uma correção viável.

## (4) Incertezas que exigem validação humana

- **A 044 está implementada numa branch sem PR.** `origin/claude/044-recorte-transversal-documental`
  (ponta `683dc58`, que mesclou a `main` durante esta auditoria — antes a ponta era `56649d4` e a árvore
  não tinha a 043). Única tarefa aberta: T065 (SC-260/SC-261 no 140/2025 não recompostos). A Mesa não
  foi percorrida no navegador. Classifiquei os três achados que ela cobre como "implementado, mas não
  validado"; a `main` continua com a lacuna. Abrir o PR e mesclar é decisão do usuário.
- **Quantos Editais já publicados têm o recorte "Todos os Perfis + Modalidade de um Perfil".** A #161
  impede novos; os antigos seguem recebendo inscrições com a divergência até a 044 chegar. Só a base de
  produção responde.
- **Renderização do documento não conferida visualmente.** O B1 está resolvido pelos testes de
  composição (larguras e fios); não gerei nem olhei um PDF grande.
- **"O que mudou" pode omitir outros campos retificáveis além de `profileId`/`modalityId`.** Só conferi o
  Documento Exigido em `publicacoes/domain/alteracoes.py:89-95`; vale cruzar o dicionário `CAMPOS` com a
  matriz de mutabilidade.
- **B8 tem evidência fina** (não está no diário) e **B6** foi julgado pelo template, sem percurso.
- **M7 depende de configuração**: o catálogo de autoridades é código com cargos no campo `nome`; se a
  produção vai trazer nomes de pessoas (e com que processo de troca) é decisão do Cefor.
- **Decisões pendentes com o usuário, que travam resíduos deste lote**: E10 (redação × transcrição),
  conjunto e ordem das seções (E5/AX-3), conteúdo comum não-cota (E2), Casas decimais/Arredondamento no
  sorteio, âncora da regra do ano (FR-344), remeter o método comum (FR-465/466), e a reabertura da D2
  (condição sobre o candidato).
