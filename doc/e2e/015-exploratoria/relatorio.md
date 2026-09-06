# Auditoria exploratória E2E — do Processo à Classificação (015)

**Data:** 05–06/09/2026 · **Base:** `origin/main` @ `616ad20` · **Ambiente:** runserver local (porta 8123, banco `ps015_audit`, mailpit) · **Método:** navegação real via Playwright, um contexto de navegador por ator, evidência primária em screenshot (94 imagens em `screenshots/`).

---

## 1. Resumo executivo

O ciclo vertical **fecha**. Foi possível, só pelo navegador e alternando atores, criar o Processo e o Edital, compor o conteúdo normativo completo (perfil com fatos declarados, cronograma, duas Etapas — uma decisória e uma pontuada —, marco classificatório com três critérios de desempate, documentos exigidos), submeter, homologar e publicar com PDF íntegro; retificar três vezes; inscrever sete candidatos e manter um rascunho; compor comissão, alocar, distribuir por rodízio; avaliar nas duas formas da Mesa; registrar ocorrência (D‑1), consolidar as duas Etapas (013); e, na 015, calcular a ordem, emitir o ato, consultar a proveniência, provocar obsolescência por Retificação e emitir o ato sucessor com motivo. O cálculo classificatório saiu **exatamente** como a regra publicada mandava, incluindo desempate por fato declarado e empate residual com posição compartilhada (1º, 2º, 3º, 3º).

A borda institucional, que na primeira redação era o que **não** fechava, fechou depois dela: o produto produzia a classificação e não a comunicava, e a 017 (PRs #41 e #42, commit `cb0f44c`) entregou justamente a comunicação — a publicação do ato pela autoridade competente, a página pública estável, o documento oficial e a situação de cada participante na Área do Candidato. Fora dela permanecem, **por decisão da própria 017**, o resultado de Etapa (o candidato continua sem ver "Habilitada na Etapa 1") e o recurso administrativo. Os outros defeitos apontados aqui também foram corrigidos: o documento oficial publicava os critérios de desempate **sem dizer o que eles comparam** e não anunciava os fatos que a inscrição exigirá (PR #39); as telas da 015 falavam em UUID e em enum onde a instituição precisa ler nomes, e mostravam data em inglês (corrigidos em `claude/e2e-015-audit-readability-288630`, 06/09/2026 — ver §4). E um defeito real de operação, encontrado aqui e corrigido primeiro: o critério de desempate de um marco recém‑criado nascia **sem opções de alvo**, bloqueando o caminho principal da composição da regra classificatória.

> **Depois da primeira redação (06/09/2026):**
> - **E2E15‑002 retratado** — "a tela de Retificação não tem link" era **falso**. A ação existe e está corretamente condicionada a `retificacao:elaborar`; ver o registro em §4.
> - **E2E15‑001 corrigido** — a causa era a que a hipótese apontava, e a correção entrou em `main` pelo PR #37 (commit `36d1683`). O achado permanece registrado como observado, com a resolução anotada.
> - **E2E15‑004, ‑005 e ‑008 corrigidos** — os três eram a mesma lacuna vista de três lugares, e foram juntos pelo PR #39 (commit `40130e3`): o documento publicado passa a nomear o alvo de cada critério de desempate, a anunciar os fatos que a inscrição exigirá e a trazer os parâmetros que fecham a conta. Na mesma entrega, a fixture byte a byte do documento publicado foi elevada da versão canônica 3 para a 7 (`a7de388`) — estava quatro degraus atrás e já não cobria nenhuma composição posterior à `009`.
>
> **Depois da 017 (06/09/2026):**
> - **E2E15‑006, ‑009, ‑010 e ‑011 corrigidos** — os quatro eram legibilidade das mesmas telas de ordenação/ato, e foram juntos na branch `claude/e2e-015-audit-readability-288630`: modalidade, proveniência e **critério de desempate** passam a trazer o nome que a **versão citada pelo ato** lhes dá, o diff de obsolescência identifica por protocolo e mostra a pontuação de antes e de agora, o ato sucedido anuncia por qual ato e quando o foi, e a interface deixou de formatar data em `en-us`. Nenhuma regra de domínio, modelo ou rota mudou.
> - **E2E15‑014 retratado** — "a lista não mostra o rascunho" era **falso**: ela não filtra por situação, e as duas evidências foram lidas fora de ordem. Ver o registro em §4.
>
> Os demais achados continuam abertos: **E2E15‑003** (governança), **‑007**, **‑012**, **‑013**, **‑016**.

**Resposta à pergunta central:** sim — uma instituição consegue conduzir o certame até a classificação *dentro* do produto, do Edital ao ato de ordenação, sem manipular dado por fora e sem depender de conhecimento de implementação. **E, desde a 017, consegue também divulgá‑la**: publicar o ato pela autoridade competente, oferecer a página pública estável e o documento oficial, e mostrar a cada candidato a sua situação na própria Inscrição. Dois degraus anteriores já haviam sido fechados: o Edital publicado **não bastava para reconstruir a ordem que o sistema calculou** (E2E15‑004/005/008 — o documento agora nomeia o alvo de cada critério, anuncia os fatos exigidos e publica os parâmetros que fecham a conta), e as telas do ato **não eram apresentáveis a ninguém de fora** (E2E15‑006/009/010/011). Juntos, esses três passos são o que separa "o sistema classificou certo" de "a instituição consegue publicar e defender a classificação".

O que **ainda** fica por fora do produto é menor e nomeado: a divulgação do **resultado de Etapa** ao candidato (a 017 publica o ato de ordenação, e a publicação de `ResultadoEtapa` é out of scope declarado, D‑002) e o **recurso administrativo**, que o próprio PDF do Edital promete ("Caberá recurso…") — a 017 cria o marco público contra o qual ele se interpõe e remete a decisão à 018. Nenhum dos dois é defeito: são as duas fronteiras que a feature seguinte herda.

---

## 2. Escopo executado

| Fase | Conteúdo | Situação |
|---|---|---|
| A | Processo + Edital + Perfil (2 modalidades, 2 fatos) + cronograma (5 eventos) + 2 Etapas (decisória e pontuada) + marco FINAL (3 critérios) + 4 documentos + conteúdo + revisão + submissão | ✅ completa |
| B | Negativo de autorização (elaboradora × homologar), homologação com fundamento, publicação com autoridade signatária, PDF verificado (3 páginas, hash) | ✅ completa |
| C | Retificação nº 2 (remuneração), por identidade estável (`/profiles/id=…/compensation`), fluxo submeter→homologar→publicar próprio | ✅ completa |
| D | 7 candidatos inscritos + 1 rascunho; PPI acrescenta autodeclaração; fatos congelados no envio; gate de reconhecimento de Retificação; negativos (acesso cruzado, UUID adulterado, anônimo, envio pós‑encerramento) | ✅ completa |
| E | Comissão (presidente + 2 avaliadores), inclusão idempotente, alocação por Etapa via matriz | ✅ completa |
| F | Distribuição por rodízio nas 2 Etapas (proposta → confirmação), com inscrições já encerradas | ✅ completa¹ |
| G | Mesa decisória (rótulos do Edital, parecer obrigatório no desfavorável) e Mesa pontuada; releitura imutável; negativo (mesa de outro avaliador) | ✅ completa |
| H | Ocorrência D‑1 (eliminada sem avaliação), consolidação em lote das 2 Etapas, reconsolidação idempotente, prontidão×oficial, guarda D‑003 (eliminada antes some da Mesa seguinte) | ✅ completa |
| I | 015: (1) ordenação simples emitida; (2) desempate com proveniência por critério; (3) ato imutável consultável; (4) obsolescência por Retificação do peso ("regra publicada mudou" + diff); (5) sucessão com motivo, cadeia no histórico; negativos (auditor sem emitir, candidata sem acesso, emissão dupla com página velha → 409) | ✅ completa² |

¹ A guarda E2E‑017 (distribuir com inscrições abertas) **não foi re‑testada diretamente**: quando a comissão ficou pronta, o período já tinha encerrado (pela Retificação nº 3). Nenhuma regressão observada, mas sem evidência nova.
² Obsolescência por **universo alterado** (participantes/resultados) não foi provocada — só a por regra alterada. "Múltiplos marcos" não foi exercitado (o cenário tem 1 marco; ver Lacunas).

**Preparação fora do produto** (registrada como manda o roteiro): banco novo + migrações, variável `INTERFACE_SELETOR_IDENTIDADE=true` (o seletor de identidade é infraestrutura de demonstração — não há autenticação real), mailpit para capturar os códigos de acesso, e os 4 PDFs fictícios dos candidatos. Nada do **domínio** foi criado fora da UI.

---

## 3. Jornada observada (síntese)

- **elena.elaboradora** compôs tudo no assistente de 8 passos. O assistente orienta bem (pendências com link, contadores, "o que falta para submeter"). Tropeço: o defeito do critério de desempate (E2E15‑001).
- **wagner.homologador / paula.publicadora** praticaram atos com confirmação explícita, fundamento e autoridade signatária; a linha do tempo do Edital ("Quem atuou") ficou completa e legível. A elaboradora, tentando homologar, recebeu recusa nominal à permissão (`edital:homologar`) — excelente.
- **Candidatos**: acesso sem senha por código de e‑mail funcionou 8 vezes; o fluxo inscrição→documentos→revisão→fatos→declarações→comprovante é claro; o PPI viu a autodeclaração aparecer ao escolher a modalidade. O gate "O Edital foi atualizado… Li as alterações" segurou o rascunho do Hugo como especificado. Isolamento perfeito entre candidatos (404 uniforme).
- **gustavo.gestor** criou comissão e alocação; **paulo.presidente** distribuiu por rodízio (proposta com carga por avaliador antes de gravar), registrou a ocorrência com revisão em dois passos ("Registrar mesmo assim"), consolidou em lote e emitiu os dois atos de ordenação.
- **alice.avaliadora / otavio.avaliador** trabalharam só sobre o que lhes foi atribuído; a Mesa decisória usou os rótulos do Edital (Deferida/Indeferida) e exigiu parecer no desfavorável; a pontuada validou faixa. Depois de concluída, a avaliação vira leitura ("Para alterar, a reabertura é ato da presidência").
- **aurora.auditora** leu ordenação, ato e proveniência sem botão de emitir.
- **Responsividade**: nas páginas amostradas (edital público, comprovante, detalhe da gestão, inscrições) a 375px não houve rolagem horizontal (`scrollWidth` = 375).

Ordem final emitida (ato sucessor, peso 2): **1º Carla 185,00 · 2º Ana 170,00 · 3º Bruno e 3º Fábio 170,00 (empate residual) · Diego sem posição (eliminado por nota) · Edite e Gilda eliminadas na Etapa 1** (fora do universo do ato — ver E2E15‑015).

---

## 4. Achados

Formato: **Observado / Esperado / Impacto / Reproduzir / Evidência / Hipótese / Recomendação**.

### P1

**E2E15‑001 · bug · composição (015) · Elaborador — Critério de desempate nasce sem opções de alvo em marco recém‑acrescentado**
- **Observado:** no passo Classificação, "Acrescentar marco" → "Acrescentar critério" produz um select "O que ele compara" **vazio** (só "—") e `required` — impossível preencher; o botão carrega `hx-get=…/criterio?edital=` (parâmetro vazio).
- **Esperado:** o critério nascer com as Etapas classificatórias e os fatos declarados, como nasce quando a página vem inteira do servidor.
- **Impacto:** bloqueia o caminho principal de composição da regra classificatória; o contorno (salvar rascunho do marco, recarregar, então acrescentar critérios) exige conhecimento interno.
- **Reproduzir:** `/gestao/editais/<id>/compor/classificacao` → Acrescentar marco → Acrescentar critério.
- **Evidência:** `06a-ACHADO-criterio-sem-alvo.png`.
- **Hipótese:** `fragmento_marco` não põe `edital` no contexto do template ([views.py:1025](../../backend/processo_seletivo/interface/views.py)), e `_marco.html:83` interpola `{{ edital.id }}` vazio no `hx-get` do botão de critério.
- **Recomendação:** passar `edital` ao contexto do fragmento (ou derivar o parâmetro no servidor); cobrir com teste de fragmento.
- **Resolução (06/09/2026):** corrigido exatamente assim em `36d1683` (PR #37), com teste que percorre os dois saltos do htmx — pede o fragmento de marco e segue o endereço que o botão montou — para afirmar que o critério nascido de um marco novo enxerga as Etapas classificatórias e os fatos declarados.

**E2E15‑002 · ~~bug (navegação)~~ → RETRATADO · retificação — "A tela de Retificação não é alcançável por nenhum link"**
- **Retratação (06/09/2026):** o achado **não procede**. A ação "Retificar" existe no cartão "O que fazer agora" do Edital publicado, montada em [`acoes.py`](../../backend/processo_seletivo/interface/acoes.py) (`_navegacao`) e condicionada — corretamente — a `edital.status == "PUBLICADO" and ator.can("retificacao:elaborar")`.
- **Como o erro ocorreu:** durante a auditoria abri o Edital publicado apenas como `gustavo.gestor`, cujo conjunto de permissões inclui `retificacao:cancelar` mas **não** `retificacao:elaborar` — logo a ação não lhe é oferecida, e isso é o comportamento desejado. A conferência no código foi um `grep` por `interface:retificar` nos templates, que nada encontra porque a URL é construída em Python (`reverse(...)`), não em `{% url %}`.
- **Verificação:** como `elena.elaboradora`, o cartão mostra "Retificar → /gestao/editais/<id>/retificar". Evidência: `87-CORRECAO-link-retificar-existe-para-elaborador.png`.
- **Nada a fazer.** O número é preservado para que as citações anteriores continuem resolvendo.

### P2

**E2E15‑003 · bug (integração 012×013) · Mesa/Resultado · Avaliador — A Mesa aceita concluir avaliação de inscrição que já tem Resultado na Etapa**
- **Observado:** após a ocorrência eliminar Gilda na Etapa 1 (Resultado oficial registrado), a Mesa de Alice continuou listando a inscrição como "Não iniciada", com formulário vivo; a conclusão "Deferida" foi **aceita sem aviso**. Ficou registrado: avaliação concluída "Deferida" + Resultado oficial "Eliminada / não avaliada".
- **Esperado:** a Mesa refletir que a Etapa já deu consequência àquela inscrição (bloquear, ou no mínimo avisar) — o mesmo espírito da guarda que já remove da Mesa quem foi eliminado em Etapa **anterior**.
- **Impacto:** trabalho morto do avaliador e um par contraditório nos registros — ruim para auditoria e para resposta a recurso. O Resultado em si permanece íntegro (imutável).
- **Reproduzir:** registrar ocorrência numa inscrição com avaliação pendente; abrir a Mesa dela; concluir.
- **Evidência:** `69-mesa-gilda-apos-ocorrencia.png`, `70-mesa-gilda-conclusao-tardia.png`, `66-resultados-etapa1.png`.
- **Hipótese:** `pode_avaliar_inscricao` ganhou a condição `participa_da_etapa()` (que barra eliminados **antes**), mas não conhece Resultado **na própria** Etapa.
- **Recomendação:** decidir a regra (governança) e alinhar a Mesa; o contorno "reabertura é ato da presidência" não cobre este caso.

**E2E15‑004 · bug (conteúdo publicado) · publicação/PDF · Candidato/Instituição — O PDF imprime os critérios de desempate sem dizer o que comparam**
- **Observado:** Tabela 2 do PDF: "1º maior pontuação na Etapa; 2º maior valor declarado; 3º menor valor declarado" — sem nomear **qual** Etapa nem **quais** fatos (experiência? nascimento?). A seção "7. CRITÉRIOS DE CLASSIFICAÇÃO" é texto genérico.
- **Esperado:** a regra publicada ser legível no documento oficial: "2º maior número de meses de experiência em EaD; 3º candidato mais velho (data de nascimento)".
- **Impacto:** juridicamente frágil: o desempate aplicado pelo sistema não é o que um leitor do Edital consegue reconstituir.
- **Reproduzir:** publicar Edital com marco e critérios; baixar o PDF.
- **Evidência:** PDF da Publicação nº 1 (via `16-edital-publicado.png` → documento) — texto extraído na auditoria.
- **Recomendação:** o gerador do documento resolver `stageId`/`factId` para os nomes publicados.
- **Resolução (06/09/2026):** corrigido exatamente assim em `40130e3` (PR #39). `parameters` deixou de ser descartado na tradução do enum, e cada critério passa a nomear o que compara — "1º maior pontuação na Etapa Prova didática", "2º maior valor declarado em Meses de experiência no ensino a distância". Junto veio o `whenMissing` por extenso ("sem o valor, fica por último neste critério"), sem o qual dois candidatos em que um não tem o dado continuariam inseparáveis no papel. Alvo que o snapshot não resolve é dito como ausente, nunca como UUID: a publicação já recusa o critério pendurado (FR‑017), e o que resta é a prévia de um rascunho.

**E2E15‑005 · bug (contrato entre features) · publicação×D‑2 · Candidato — Os fatos exigidos não são anunciados em lugar nenhum antes do envio**
- **Observado:** o Edital declara `declaredFacts` (nascimento, meses de EaD), a inscrição os exige e congela, o desempate os consome — mas o PDF e a página pública não os mencionam. O candidato os descobre na tela de revisão, no momento do envio ("registrados no momento do envio e não podem ser alterados depois").
- **Esperado:** o documento normativo anunciar os dados que serão coletados e usados no desempate.
- **Impacto:** surpresa no envio de um dado irreversível; a transparência da regra de desempate depende disso.
- **Evidência:** PDF sem "nascimento"/rotulos dos fatos; `30-ana-revisao-fatos.png`.
- **Recomendação:** seção própria no documento gerado ("Dados exigidos na inscrição"), derivada dos `declaredFacts`.
- **Resolução (06/09/2026):** corrigido em `40130e3` (PR #39), com o título que a recomendação sugeriu e no lugar onde o candidato procura **antes** de se inscrever: um bloco no Perfil que os declara, ao lado dos Requisitos e antes das Modalidades e do marco que os consome — e não na seção institucional "CRITÉRIOS DE CLASSIFICAÇÃO", que é texto padrão vindo de `sections` e não recebe dado derivado. Cada fato sai com rótulo e tipo publicados. O documento anuncia o que **será exigido** e não afirma o congelamento na submissão: aquilo é comportamento da inscrição, não viaja no conteúdo publicado, e escrevê‑lo seria o Edital afirmando regra que a Publicação não contém.

**E2E15‑006 · UX · 015 · Presidência/Auditor — As telas da classificação falam UUID onde a instituição lê nome**
- **Observado:** coluna MODALIDADE da ordem calculada mostra `f584b9db-…` em vez de "Ampla concorrência"; a proveniência do ato lista Processo/Edital/Perfil/Marco/Versão como UUIDs; o diff de obsolescência identifica inscrições por UUID (não INS‑…/nome); os critérios aparecem como enum (`MAIOR_VALOR_DE_FATO`) sem o rótulo do fato.
- **Esperado:** identificadores legíveis (código INS, nomes publicados), com o UUID como detalhe técnico.
- **Impacto:** a página do ato — exatamente a que responde recurso — não é apresentável a ninguém de fora.
- **Evidência:** `76-ordenacao-calculada.png`, `80-ato-proveniencia.png`, `82-ato-obsoleto-divergencias.png`.
- **Resolução (06/09/2026):** corrigido na branch `claude/e2e-015-audit-readability-288630`, reusando o que a 017 já tinha resolvido em `divulgacao/domain/conteudo.py::compor()` — o helper foi extraído para `classificacao/domain/nomes.py` e agora serve às duas leituras. A coluna MODALIDADE da ordem calculada traz o nome; o diff identifica por protocolo, como as outras tabelas; e a proveniência do ato **acrescenta** o nome ao lado do identificador em vez de substituí‑lo, porque ali o UUID é a âncora de auditoria. **A fonte é a versão que o ato cita**, e não a vigente: um ato histórico lê‑se com os nomes que ele congelou, e resolver pela vigente faria uma Retificação que renomeia uma modalidade reescrever retroativamente como um ato antigo é lido — há teste que retifica o nome do marco e afirma as duas leituras lado a lado. **Os critérios de desempate também**: a tabela do ato imprimia `MAIOR_VALOR_DE_FATO` porque `PosicaoNaOrdem.desempate` congela `type` e `criterionId`, e não a grafia — o critério passou a ser localizado por `criterionId` na versão que o ato cita, e sai pela frase publicada ("maior pontuação na Etapa Prova didática"), com o enum e o identificador mantidos ao lado como detalhe técnico. A grafia não foi reinventada: as três frases que o PR #39 criou para o documento do Edital foram extraídas para `publicacoes/domain/vocabulario_da_regra.py` e agora servem às duas peças — que são justamente as duas que a instituição põe lado a lado para responder a um recurso. Com isso **FR‑050 e SC‑010 da 015 ficam observáveis pela tela**, que é o que elas exigem. O achado está **integralmente corrigido**.

**E2E15‑007 · UX/fluxo · portal · Candidato — Depois do encerramento, o rascunho não diz que acabou**
- **Observado:** com as inscrições encerradas, a revisão do rascunho de Hugo continuou mostrando o gate "O Edital foi atualizado… Li as alterações e quero continuar" — nenhuma menção a período encerrado; o convite é a prosseguir.
- **Esperado:** o rascunho declarar "o período de inscrições terminou em …" antes de qualquer outro convite.
- **Impacto:** o candidato reconhece retificações e preenche dados para descobrir só no envio (ou nunca) que não pode mais enviar; informação chega tarde.
- **Evidência:** `45-NEG-hugo-envio-apos-encerramento.png`.

**E2E15‑008 · conteúdo publicado · PDF — Arredondamento, normalização e pesos do marco não constam do documento**
- **Observado:** a Tabela 2 traz só "soma ponderada"; casas decimais (2), modo (meio para cima) e o peso de cada Etapa na combinação não são impressos juntos da regra classificatória (o peso aparece longe, na seção da Etapa).
- **Impacto:** a nota combinada (185,00) não é reconstruível a partir do documento público.
- **Evidência:** PDF (Tabela 2) vs. `84-ato-sucessor-emitido.png`.
- **Resolução (06/09/2026):** corrigido em `40130e3` (PR #39). O marco publica normalização, escala e modo de arredondamento por extenso ("2 casas decimais, meio para cima"), e o peso de cada Etapa enumerada volta para junto da regra que o consome: ele já estava publicado na seção da própria Etapa — que continua sendo a fonte autoritativa (FR‑009) —, mas folhear o documento para reunir os fatores não é reconstruir a conta. O bloco **deixou de ser tabela**: três colunas cabiam enquanto o marco dizia só "soma ponderada"; com o alvo, a regra de ausência, os pesos e o arredondamento, a grade viraria parágrafo espremido em célula, e marcos não se comparam entre si — cada um é uma regra que se lê inteira.

### P3

**E2E15‑009 · l10n · 015 — Datas em inglês nas telas de ordenação** — "Ato vigente emitido em Sept. 5, 2026, 11:30 p.m." em meio a uma interface toda em "05/09/2026 23:04". Evidência: `78-ato-emitido.png`, `80-ato-proveniencia.png`.
- **Resolução (06/09/2026):** a causa era `settings/base.py` declarar `TIME_ZONE` e **nenhum** `LANGUAGE_CODE`, caindo em `en-us`; agora declara `LANGUAGE_CODE = "pt-br"`. A mudança é global e governa também o separador decimal — a suíte inteira foi executada contra PostgreSQL antes e depois, sem diferença (3284 testes; nenhum assertava formato em inglês). Só isso, porém, trocaria "Sept. 5, 2026" por "5 de Setembro de 2026 às 23:30", que continua não sendo o que a interface escreve: as três datas cruas das telas da 015 passaram a usar o `|date:"d/m/Y H:i"` que o resto do sistema já usava.

**E2E15‑010 · UX · 015 — O ato histórico não declara que foi sucedido** — a página do ato 1 (aberta pela auditora após a sucessão) mostra os valores antigos sem nenhum banner "sucedido por … em …"; dá para citar um ato superado sem perceber. Evidência: `85-ato-historico-imutavel.png`.
- **Resolução (06/09/2026):** o aviso entra **antes** dos valores, e não ao lado do histórico: quem chega por um link guardado lê o número da posição primeiro. Traz quando, por quem, o motivo declarado da sucessão e o link para o ato sucessor, lido da relação reversa de `ato_anterior` — nenhum valor congelado muda, e há teste que compara byte a byte a seção de posições antes e depois da sucessão para afirmá‑lo.

**E2E15‑011 · UX · 015 — O diff de obsolescência não mostra o que mudou de fato** — "Mudanças posição a posição" listou 1º→1º, 2º→2º…, tudo igual; a mudança real (pontuação 92,5→185) não aparece, e o gestor fica sem ver por que o ato está obsoleto além da frase "a regra publicada do marco mudou". Evidência: `82-ato-obsoleto-divergencias.png`.
- **Resolução (06/09/2026):** a tabela ganhou "Pontuação no ato" e "Pontuação agora". O diff já **detectava** a divergência — `comparar()` compara a nota, e era por isso que a linha aparecia —, mas exibia só a posição, que era justamente a coluna que não tinha mudado. Os dois lados vinham com nomes diferentes (`pontuacao_combinada` no snapshot, `pontuacao` na proposta) e passaram a ser uniformizados no selector, e não na tela. Teste: Retificação que dobra o peso da Etapa, com asserção sobre as quatro células (90/180 e 70/140).

**E2E15‑012 · consistência · gestão — 404 técnico do Django na recusa da Mesa alheia** — a avaliadora acessando inscrição de outro avaliador recebe a página "Page not found (404)" crua (artefato de DEBUG), enquanto o portal tem 404 institucional ("Recurso não encontrado"). Evidência: `59-NEG-alice-mesa-do-otavio.png` vs `36-NEG-bruno-tenta-inscricao-da-ana.png`.

**E2E15‑013 · UX · portal — Candidato deslogado recebe 404 em vez de convite a entrar** — abrir a URL da própria inscrição sem sessão devolve 404; um link guardado no celular vira beco. (O 404 uniforme é correto contra terceiros; para anônimo, redirecionar ao acesso não vazaria nada.)

**E2E15‑014 · ~~UX (portal)~~ → RETRATADO · "Minhas inscrições" não mostra o rascunho**
- **Retratação (06/09/2026):** o achado **não procede**. `portal/views.py::inscricoes` consulta `Inscricao.objects.filter(identity_subject=…)` **sem filtro de situação**, e `inscricoes.html` desenha o rascunho explicitamente — "Inscrição não enviada", com a ação "Continuar inscrição". Três suítes já afirmam isso (`tests/integration/portal/test_minhas_inscricoes.py`, `test_convite_por_vaga.py`, `test_recusas_de_abertura.py`).
- **Como o erro ocorreu:** as duas evidências foram lidas fora de ordem. `24-candidata-apos-login.png` é **anterior** a `28-inscricao-modalidade.png`: a lista foi consultada no minuto seguinte ao acesso, **antes** de o rascunho existir — o rascunho só nasce ao escolher a vaga —, e ali "Você ainda não possui inscrições" é o estado vazio correto, e não uma consulta que esconde.
- **Nada a fazer.** O número é preservado para que as citações anteriores continuem resolvendo, como no 002.
- **Fica como oportunidade de UX, não como achado:** o convite de retomada não distingue "ainda não comecei" de "comecei e não terminei" — a mensagem pós‑acesso não diz que o rascunho passa a existir só depois da escolha da vaga. Não foi observado como defeito nesta auditoria; entra no §6 se alguém quiser persegui‑lo.

**E2E15‑015 · registro de desenho · 015 — Eliminados em Etapa anterior à última ficam fora do universo do ato** — Edite e Gilda (eliminadas na Etapa 1) não aparecem nem em "Participantes considerados sem posição" (só Diego, eliminado na última Etapa). É coerente com o desenho (universo = participantes da última Etapa enumerada), mas quem espera que o ato final liste todos os eliminados vai procurá‑los ali; os Resultados por Etapa é que contam essa história. Evidência: `76-ordenacao-calculada.png` + `66-resultados-etapa1.png`.

**E2E15‑016 · UX · gestão — O caminho da presidência até distribuir/consolidar não é anunciado** — "Minhas Etapas" do presidente diz "você não possui Etapas atribuídas" e o caminho real (Alocação por Etapa → Distribuir → painel da Etapa) só se descobre explorando. Evidência: `50-presidente-home.png`.

---

## 5. Severidade — visão geral

| Sev. | Qtde | Achados |
|---|---|---|
| P0 | 0 | — |
| P1 | 1 | 001 — **corrigido** em `36d1683` (PR #37) |
| P2 | 6 | 003 (governança) e 007 abertos · 004, 005, 008 — **corrigidos** em `40130e3` (PR #39) · 006 — **corrigido** em `claude/e2e-015-audit-readability-288630` |
| P3 | 7 | 009, 010, 011 — **corrigidos** em `claude/e2e-015-audit-readability-288630` · 012, 013, 016 abertos · 015 é registro de desenho |
| — | 2 | 002 e 014 (retratados — não eram defeitos) |

Abertos ao fim desta rodada: **003** (depende de decisão de governança), **007**, **012**, **013** e **016**. Tudo o mais está corrigido ou retratado.

O que funcionou **bem** e merece registro: recusas de autorização nominais e uniformes (404 institucional entre candidatos; permissão citada na gestão); idempotência em toda parte (inclusão repetida na comissão, reconsolidação, emissão dupla com página velha → 409 com mensagem exata); gate de retificação no rascunho; D‑003 (eliminada antes some da Mesa seguinte, lista e rota); a Mesa nas duas formas com vocabulário do Edital; ocorrência D‑1 com revisão em dois passos; e o cálculo/desempate/empate residual da 015 **corretos ao decimal**, com proveniência que registra o critério que separou cada par.

---

## 6. Oportunidades de produto

1. ~~**Divulgação é o elo que falta**~~ — **entregue pela 017** (PRs #41 e #42, commit `cb0f44c`): a classificação chega ao candidato pela sua própria Inscrição, e ao público por uma página estável. **O que resta da oportunidade original** é o resultado **de Etapa**: "sua participação: Habilitada na Etapa 1" continua não existindo, e a publicação de `ResultadoEtapa` é out of scope declarado da 017 (D‑002). Enquanto ela não existir, a instituição divulga o intermediário por fora.
2. ~~**Ato publicável**~~ — **entregue pela 017**: a publicação produz documento oficial (PDF) a partir dos mesmos bytes que a página lê, com nomes e modalidades resolvidos pela versão que o ato cita. O que **não** existe é exportação **administrativa** do ato (CSV para conferência interna), que é outra necessidade e outro público.
3. **Recursos** *(continua aberta — por decisão da própria 017)*: o texto institucional do PDF já promete "Caberá recurso contra os resultados divulgados" — o produto gera a promessa sem oferecer o meio. A 017 declarou Contestação fora de escopo e remeteu à **018**, criando o marco público contra o qual o recurso se interpõe; a página publicada não oferece ação de recurso (FR‑055) justamente para não fingir que oferece. Ou a seção sai do template do Edital, ou a 018 entra no roteiro.
4. **Retificação guiada pelo dado**: a tela de retificar é ótima (endereçamento por identidade, diff antes de criar) — só falta ganhar os campos que hoje só a API tem (ex.: `max_inscricoes_por_candidato`, sem campo no assistente).
5. **Encerramento do certame**: "Encerrar" existe no detalhe mas nenhuma orientação diz quando encerrá‑lo em relação ao ato de classificação; o pós‑015 (homologação do resultado final) é o próximo degrau natural.
6. ~~**Legibilidade da 015**~~ — **feita** em `claude/e2e-015-audit-readability-288630`, inclusive os critérios de desempate com os rótulos publicados: as telas de ato e proveniência viraram, como a oportunidade previa, documento de resposta a recurso. A grafia dos critérios é a mesma do documento oficial do Edital, por construção — ela mora num lugar só.
7. **Retomada anunciada** *(nova, vinda da retratação do E2E15‑014)*: a lista de "Minhas inscrições" mostra rascunho corretamente, mas o convite pós‑acesso não distingue "ainda não comecei" de "comecei e não terminei" — a mensagem não diz que o rascunho passa a existir só depois de escolher a vaga. Custo baixo, e evita exatamente a leitura equivocada que o achado registrou.

---

## 7. Lacunas de cobertura

**a) Coisas que não existem porque são de features futuras (não são defeitos):**
- ~~Divulgação da classificação ao candidato~~ — **fechada pela 017**. Continuam fora: a divulgação do **resultado de Etapa** (D‑002 da 017) e a **comunicação ativa** — e‑mail, SMS, push —, também out of scope declarado.
- Recursos administrativos (interposição, resposta, efeito sobre Resultados — a reabertura pela presidência existe como ato interno). A 017 remeteu à **018**.
- Corte por alvo e progressão entre etapas (014 — nada em código além do que a 013/015 já fazem).
- Nomeação/convocação pós‑classificação (016+); a 017 fornece o marco público que a 019 poderá referenciar.
- Homologação do resultado final (D‑003 da 017).

**b) Coisas que a feature coberta deveria ter e não tem:**
- ~~Nomes legíveis nas telas da 015 (E2E15‑006) e datas localizadas (E2E15‑009)~~ — **corrigidos** em `claude/e2e-015-audit-readability-288630`, junto com o diff legível (E2E15‑011) e o aviso de sucessão (E2E15‑010). Inclui o rótulo publicado dos critérios de desempate, que é o que torna FR‑050 e SC‑010 verificáveis pela tela.
- ~~Fatos declarados e alvos do desempate no documento publicado (E2E15‑004/005/008)~~ — **corrigido** (PR #39).
- Aviso de encerramento no rascunho (E2E15‑007).
- Guarda 012×013 na própria Etapa (E2E15‑003) — **depende de decisão de governança**, e não de implementação.

**c) Capacidades que o domínio tem mas nenhuma tela alcança:**
- `reproduzir_ato` / `divergencias_da_reproducao` (classificacao/application/reproducao.py) — a prova de reprodutibilidade, valor central da 015, vive só em teste; nenhuma rota a expõe. (A 017 **afere** publicabilidade reproduzindo o estado classificatório, mas não expõe a reprodução como leitura.)
- `max_inscricoes_por_candidato` (teto D‑3) — só via API/seed; o assistente não tem o campo.
- Obsolescência por universo alterado e `CRITERIO_NAO_SE_APLICA` com fato ausente: no fluxo real, fatos são obrigatórios no envio, então a ausência que ativaria o `whenMissing` de fato praticamente só ocorre via pontuação de Etapa‑porta; o comportamento existe no domínio e não foi observável pela UI neste cenário.
- Cenário de **múltiplos marcos** por perfil: o compor aceita, mas nada na jornada sugere quando usar mais de um; não exercitado.

**Dados que o produto não criou** (transparência da preparação): identidades de gestão (seletor de demonstração), SMTP/mailpit, arquivos PDF dos candidatos. Todo o resto — do Processo ao ato sucessor — nasceu pela interface.

---

## 8. Evidências

`screenshots/` — 94 imagens numeradas na ordem da jornada (`00-gestao-vazia.png` → `87-CORRECAO-link-retificar-existe-para-elaborador.png`), incluindo os negativos prefixados `NEG` e o achado `06a-ACHADO-criterio-sem-alvo.png`.
