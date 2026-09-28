# Reavaliação D — carga cognitiva e complexidade acumulada

Código lido: worktree em f77e8aa9 (= origin/main 79aeb847 + só doc da auditoria). Somente leitura.

## Notas brutas (em construção)

### Assistente — sequência (views.py:899-924)
Identificação → Perfis → Cronograma → Etapas → Classificação → Inscrição → Anexos → Conteúdo → Revisão.
- A ordem é justificada por dependência de referência (comentários views.py:902-918): o sistema já
  guia a sequência pela ordem das telas. Bom.
- Selo de progresso (views.py:1053-1090): "concluída" = "tem conteúdo" para etapas, classificação,
  inscrição, anexos — não diz se o Edital *precisa* daquilo. Operador não sabe se "pendente" em
  Classificação é problema (Edital sem classificação é legítimo, views.py:1068-1072).

### Perfis (_perfil.html, _modalidade.html, _fato.html)
- Por Perfil: Código/Denominação/Localidade; Vagas imediatas; Cadastro Reserva (rádio, NONE pré-marcado
  `_perfil.html:107`); Modalidades (código, denominação, %, fundamento, versão AAAA-MM-DD); "Qual delas é
  a ampla concorrência" (`:173-202`, só se há Modalidade); reversão (`:214-225`); forma de convocação
  (`:241-252`); quadro (derivado se não há lista reservada, `_linha_do_quadro.html:29-31`); Fatos exigidos.
- `callForm` e `vacancyReversion` são por Perfil mas nos Editais são do Edital (comentários citam "o 69/2026
  convoca por publicação" — decisão de Edital). Repetição por Perfil; mitigada por Duplicar (043).
- Modalidade: `code` é ESTRUTURAL (`mutabilidade.py:266`) e desde a 044 é a chave do recorte transversal
  (`forms.py:1495-1530`, agrupa por `modalidade.code.strip()`); "PcD" vs "PCD" = duas modalidades. Nada na
  tela avisa. Denominação divergente é acusada na publicação (FR-706), grafia do código não.
- "Qual delas é a ampla concorrência": o operador que declara uma Modalidade "AC" precisa saber apontá-la;
  se não apontar, AC vira lista reservada e exige linha de quadro. Grafia-armadilha documentada no próprio
  comentário (`_perfil.html:165-167`) e na memória do projeto. Sistema recusou inferir por nome (025).
- `reserveType` NÃO retificável (`mutabilidade.py:233-238`), default NONE pré-marcado, nenhum aviso na tela.
- Fato: Código (placeholder NASCIMENTO) + rótulo + tipo DATA/INTEIRO; tipo não retificável
  (`mutabilidade.py:303-307`). Ajuda: "Só o que uma regra publicada consome" — o operador precisa saber
  no passo 2 que o desempate do passo 5 vai consumir o fato. Dependência para trás.

### Classificação (_marco.html 596 linhas; compor_classificacao.html)
- Pergunta de entrada `orderProduction` (`_marco.html:47-68`) — bom: revelação progressiva (030 FR-413).
- Código + Denominação do marco obrigatórios (`:69-83`) — "FINAL"/"Classificação final" inventados;
  `code` estrutural (`mutabilidade.py:311`).
- Casas decimais + Arredondamento SEMPRE visíveis, inclusive em marco POR_SORTEIO (`:154-172`, sem
  condição) — RC-15 parcialmente resolvido. Default 2 casas/meio p/ cima (ajuda `_como_preencher_o_marco.html:27-29`).
- Etapas: `<select multiple>` (`:104`) só lista Etapas marcadas Classificatória no passo 4 — dupla declaração.
- Peso: aviso derivado quando Etapa enumerada sem peso (`:140-144`) — bom (037).
- Combinação/normalização só com ≥2 Etapas (`:461-492`) — bom, inferência (030 FR-415).
- Recurso: 3 estados admite/nao_admite/nao_declarada (`:200-248`); distinção "silêncio × negativa" exige
  entender juízo de admissibilidade.
- Método do sorteio: 10 campos (`:300-420`) + bloco comum no passo (`compor_classificacao.html:58-141`):
  - occurrenceAt = texto livre ISO com fuso (`:345-353`, placeholder `2026-11-20T20:00:00-03:00`) — pensar
    como banco; sem vínculo com Evento do Cronograma.
  - occurrence: armadilha de formato (número no fim; não repetir fonte) `:338-342`.
  - normalizationRule (enum) + normalizationText (prosa) e substitutionRule (enum com UMA opção,
    `:390-392`) + substitutionText — o operador escreve a mesma regra duas vezes (código e prosa).
  - derivation: texto livre sem ajuda (`:354-358`).
- Corte (`:504-581`): cutTargetKind (interruptor) / Alvo / Suplentes / Empate (sem padrão, impede) /
  Etapa governada (NONE × Etapa, "nunca deduzida") / Faixa seguinte (sem padrão).
  - "sem corte não há geração, sem geração não há faixa, e sem faixa não há convocação"
    (`_como_preencher_o_marco.html:54-65`). O operador precisa declarar um "corte" para CONVOCAR, mesmo que
    o Edital diga só "serão convocados os N classificados". 046 tornou impeditivo o Perfil sem corte.
- Critério de desempate (`_criterio.html`): Ordem digitada (`:10-14`), Tipo (3) + Alvo (Etapa|Fato)
  acoplados ("Escolha coerente…", `:41-42`) + whenMissing obrigatório. "Maior idade" = MENOR_VALOR de fato
  DATA — inversão não explicada.

### Etapas (_etapa.html)
- Forma PONTUADA/DECISORIA com campos aninhados (bom). Caráter: 2 checkboxes eliminatória/classificatória.
- "Avaliações por inscrição" >1 oferecido e sem Resultado — publica-se bloqueado se eliminatória ou
  enumerada (`compor_etapas.html:42-45`). Campo oferecido cujo valor ≠1 é beco.
- Peso "(opcional até um marco enumerar esta Etapa)" (`_etapa.html:146`).

### Cronograma / Inscrição / Anexos
- Evento: Tipo texto livre (`_evento.html:19-22`); sistema não sabe qual é "Inscrições" até a designação
  no passo Inscrição (`compor_inscricao.html:15-27`). Bom: "nada é digitado duas vezes".
- ORDEM INVERTIDA: Documento exigido aponta "Modelo que o Edital fornece" (`_documento.html:92-103`) mas
  os anexos são cadastrados no passo 7 (Anexos), depois do 6 (Inscrição) — `views.py:912-915` justifica
  ao contrário. Para vincular: ir ao 7, subir, voltar ao 6.
- Documento: "Chave" obrigatória, "sem espaços", identidade entre versões (`_documento.html:6-16`) —
  conceito de banco; derivável do nome.
- Alcance: dois selects (Perfil; Modalidade com optgroups "Em todos os Perfis" por código e "Modalidade de
  um Perfil") — combinação Perfil=Todos + Modalidade de um Perfil é oferecida e recusada na publicação
  (comentário `_documento.html:55-60`).
- Nenhuma tela de composição avisa quais campos NÃO se retificam; só a tela de Retificação
  (`retificar.html:129`). Campos: Perfil.code, reserveType, Modalidade.code, fato.type, marco.code,
  marco.stages, matriculationRequest/moment (`mutabilidade.py`).

### Etapas — combinações que a tela oferece e a consolidação recusa (046)
- `impedimento_da_regra` (`resultados/domain/regra.py:57-99`): (a) >1 avaliação; (b) pontuada+eliminatória
  sem nota mínima; (c) decisória não eliminatória. Nova Etapa nasce PONTUADA com as duas caixas de Caráter
  desmarcadas (`_etapa.html:67,175-184`); escolher "Com decisão, sem nota" sem marcar Eliminatória produz
  (c). "Nota mínima (opcional)" (`_etapa.html:73`) não tem a ressalva que o Peso ganhou na 037 (`:146`).
- 046 torna (a)-(c) impeditivo só quando "o fluxo exige o Resultado" (4 consumidores; decisória enumerada
  é "porta" e não conta — RC-114) (`validation.py:1787-1930`). O operador não tem como prever se a mesma
  Etapa impede ou só avisa: depende de marco a enumerar, corte a governar, sorteio a habilitar.
- Classificatória: marco só lista Etapas marcadas classificatórias (`_marco.html:103-115`), e
  `milestone_stage_not_classificatory` impede. `regra.py:12` diz que `classificatory` "não entra" na
  consequência local — a caixa só serve para filtrar o seletor do marco. Redundante com "o marco enumera".

### Mensagens de validação (validation.py) — vocabulário do modelo
- `cut_rule_sem_especie_de_alvo` (`:905`): "não declara a espécie do alvo".
- `cut_rule_com_etapa_circular` (`:878`): "o universo da ordem passaria a depender do corte que ela produz".
- `general_competition_modality_undeclared` (`:1151`, WARNING): "todas contam como lista reservada … cuja
  quantidade mora na linha geral".
- `profile_without_cut_rule` (`:1976`, IMPEDE): "sem corte não há faixa … ela pode declarar que não governa
  Etapa alguma" — o conserto exige declarar alvo, empate, Etapa governada e continuação.
- `milestone_without_cut_rule` (`:2028`, AVISO): "Sem corte não há geração, sem geração não há faixa…".
- `order_production_nao_declarada` (`:1722`): explica que "o sistema volta a inferir a forma da presença do
  método" — fala de implementação ao operador.
- Mensagens de forma genéricas: "O campo não satisfaz o formato {campo.formato} em {caminho}" (`:369`);
  `mensagem_legivel` (`views.py:776-787`) troca o caminho por nome, mas `{campo.formato}` fica.

### Operação — uma emissão por recorte, e a cadeia ordem→corte→ocupação→convocação
- Ordenação (`ordenacao.html:80-86`): um ato por recorte; recorte vazio também é emitido à mão ("Emitir
  continua sendo ato seu — nada foi constituído automaticamente").
- Corte (`corte.html:77`): idem por recorte. Sorteio (`sorteio.html:212-406`): por recorte, publicar relação
  → observar ocorrência → realizar → publicar classificação; anulação em 4 passos incluindo Retificação.
- Ocupação (`ocupacao.html:149,156-164`): apurar por recorte; nova apuração exige MOTIVO digitado.
- Convocação (`convocacao.html:30,54`): cada desfecho torna a apuração OBSOLETA e convocar é recusado até
  emitir nova apuração (com motivo). Ciclo de suplência = desfecho → apurar (motivo) → convocar → comunicar.
- Convocação pede "Espécie" (VAGA_INICIAL/SUPLENCIA/PARA_REGULARIZAR) (`:120-125`) — derivável do estado
  da vaga; "Vencimento do prazo" à mão (`:133-135`); "Fundamento" livre a cada chamada (`:138-140`);
  atestado pede "Prazo que o Edital publicou … O sistema não guarda esse prazo" (`:325-327`).
- Distribuição: filtro "Avaliador — Identificador institucional, exato" (`distribuicao.html:306-309`).
- Recurso: "Identidade do objeto", "Ato vigente naquele instante" e "Versão consolidada citada" exibem
  UUID cru (`recurso.html:33-37`; `recursos/application/selectors.py:258-261`, deliberado: FR-092).
- "marco" tem dois referentes: "Próximos marcos" do pulso = Eventos do Cronograma
  (`processo_detalhe.html:110-124`); "marco classificatório" na composição. Linguagem ubíqua (Const. §I).

### Onde já infere / dá default (bom)
- Código e denominação do marco derivados do Perfil (`editais/domain/marcos.py:53-75`, FR-420).
- 2 casas / meio para cima no marco novo (`marcos.py:50`, FR-419).
- Combinação com 1 Etapa não é perguntada (`_marco.html:461-492`).
- Linha geral do quadro derivada = vagas imediatas sem lista reservada (027; `_linha_do_quadro.html:29-31`).
- Período de inscrições aponta Evento (`compor_inscricao.html:15-27`).
- Fase do Evento derivada das datas (045 D-001) — removeu declaração.
- Situação pública derivada (047) — nenhuma configuração nova.
- Duplicar Perfil (043) pede só Código e Localidade (`compor_perfis.html:85-88`).
- Método do sorteio comum (030 FR-429); vocabulário fechado de algoritmo/fonte (035).
- Sugestão de local como placeholder (`_evento.html:42`); "Obrigatório" marcado por padrão (`_documento.html:106`).
- Pendência leva à etapa e âncora (`views.py:660-707`); caminho → nome (`views.py:727-787`).
- Ajuda da Classificação só aparece quando há marco (030 FR-426).

### Achados verificados depois (evidência adicional)
- **Ampla concorrência em três grafias** — linha geral (modalityId nulo), Modalidade declarada ("AC") e o
  ponteiro `generalCompetitionModalityId`. A tela sugere que não precisa declarar ("Nenhuma — a ampla
  concorrência é só a linha geral do quadro", `_perfil.html:195`). Mas a inscrição só oferece as Modalidades
  declaradas: 1 declarada = assumida para todos; ≥2 sem AC = candidato obrigado a escolher uma cota
  (`inscricoes/application/rascunho.py:280-313`). A validação só AVISA e manda "declarar qual delas é a
  ampla" (`validation.py:1124-1160`), sem dizer que o não-cotista não consegue se inscrever. É a causa-raiz
  do RC-37; a 048 constrói o remédio a jusante (Retificação que acrescenta Modalidade).
- **Forma de convocação ausente publica em silêncio**: `_forma_de_convocacao_declarada` devolve `[]` para
  `None` (`validation.py:1011-1013`) — nem aviso — e `comunicar` recusa depois: "declare a forma por
  Retificação antes de emitir" (`convocacao/application/comunicar.py:164-170`). O anexo 2 da auditoria diz
  "aviso" — está errado contra o código. Mesmo gênero do contrato da 046, não coberto.
- **Empate na última posição exigido em marco de sorteio**, onde a ordem é total
  (`sorteios/application/sorteio.py:353-354`): `_marco.html:539-549` sempre visível, `validation.py:823-831`
  impede sem condição. Também visíveis e vazios no sorteio: casas/arredondamento (`_marco.html:154-172`) e
  critérios de desempate (`:582-590`). Contraria a SC-139 da 030.
- **Instante da ocorrência em RFC 3339 digitado** (`_marco.html:345-353`); recusa cita o formato e o nome do
  campo em inglês: "(`occurrenceAt`) deve ser publicado no formato RFC 3339 com fuso"
  (`editais/domain/perfis.py:560-573`); faltas citam `algorithm`, `rule`, `text` (`perfis.py:444-455`).
  O Cronograma usa `datetime-local` em horário de Brasília (`compor_cronograma.html:28-29`). Nenhum vínculo
  com o Evento "Sorteio" do Cronograma.
- **Enum + prosa para a mesma regra**: normalização (2 opções) e substituição (1 opção,
  `_marco.html:390-392`) pedem também "Como a regra … será publicada" em texto livre (`:379-401`).
- **Fato do desempate oferecido de todos os Perfis**: `_etapas_e_fatos_do_edital` lista fatos do Edital
  inteiro (`views.py:2278-2282`); `_criterio.html:35-39` não filtra; `tiebreaker_fact_missing` impede
  (`validation.py:766`). O Duplicar remapeia (`duplicacao.py`), a composição manual não.
- **Tipo do Evento**: texto livre obrigatório (`_evento.html:19-22`), NÃO retificável com a razão "liga o
  Cronograma às regras que dependem dele" (`mutabilidade.py:423-427`) — mas "Nada procura texto em `type`"
  (`inscricoes/domain/periodo.py:7`). Erro de digitação no Tipo fica publicado para sempre.
- **Não retificáveis sem aviso na composição** (lista completa): Perfil.code (`:226`), reserveType (`:236`),
  Modalidade.code (`:266`), fato.type (`:304`), marco.stages (`:326`), cutRule/targetKind (`:381`),
  governedStage (`:391`), continuation, tiebreakers type/stageId/factId/whenMissing (`:403-420`),
  schedule.type (`:423`), documentRequirements.key (`:483`), matriculationRequest/moment (`:197`),
  normativeRule calculation/rounding/distribution/callRules. Só `retificar.html:127-139` os lista.
- **Estrutura sem consumidor**: `normativeRule.calculation/rounding/distribution/callRules` são JSON
  gravados e publicados (`publish_edital.py:138-141`), não retificáveis com razão constitucional, sem tela e
  sem leitor na execução (grep: só serialização). `reserveLimit` publicado sem efeito (RC-58).
- **Duas palavras com dois referentes**: "marco" (Evento no pulso: `processo_detalhe.html:110-124`,
  `supervisao.html:95,109`) × "marco classificatório"; "Geração" (faixas: `ordenacao.html:21`) × (arquivo de
  exportação: `matriculas.html:19`). Constituição §I.
- **Link principal do marco lê a chave, não a resolução**: `_destinos_do_marco` usa `marco.get("drawMethod")`
  (`views.py:2862`), e o marco que usa o método comum publica `drawMethod: None`
  (`publish_edital.py:104-114`) — cai em "ordenação" e é redirecionado (`views.py:5775-5776`,
  `_e_marco_de_sorteio` resolve certo). Terceira leitura de "este marco sorteia?". Menor.
- **Sem eixo de tipo de processo**: "O sistema não tem taxonomia de natureza do Processo, e criá-la seria
  inventar um eixo que nenhuma outra feature consome" (`processos/models.py:73-77`, 029 D-002). O único reuso
  exige Edital publicado (023). A Constituição admite "Modelos reutilizáveis … origem controlada".
- Processo × Edital: criar exige inventar "Identificação institucional" e "Título" do Processo
  (`processo_criar.html:33-50`), que 4 de 5 Editais da amostra não nomeiam (estudo §7.1).
- **Selo da Classificação desatualizado**: `views.py:1068-1072` ("Um Edital pode não classificar, e nesta
  versão isso é legítimo"; "concluída" se existe QUALQUER marco no Edital) × `profile_without_milestone`
  (IMPEDE por Perfil, `validation.py:1740-1780`, 032) e `profile_without_cut_rule` (IMPEDE por Perfil,
  `:1955-1985`, 046). 16 Perfis com 1 marco num só = passo "concluída" e 15 impedimentos na Revisão.
- `reserveType/reserveLimit`: só exibição (portal `views.py:199`, `visao_geral.py:193`, `revisao.py:42`);
  nenhum leitor em convocacao/ocupacao/classificacao. O "Suplentes" do corte é o que executa.

---

# RELATÓRIO

## Pergunta 1 — O servidor que conhece o Edital consegue compor e operar sem o modelo?

**Resposta curta: compõe um Edital simples de ampla concorrência pura com pouca ajuda; não compõe
corretamente um Edital com cotas, sorteio ou convocação sem saber quatro coisas do modelo que a tela não
diz no ponto da decisão** — (1) que a ampla concorrência precisa existir como Modalidade declarada para o
não-cotista se inscrever; (2) que "regra de corte" é o que habilita a convocação, mesmo quando o Edital não
corta nada; (3) que a forma de convocação ausente publica e trava a convocação; (4) que ~15 campos não se
corrigem depois de publicados. Na operação, precisa saber a cadeia ordem → corte → ocupação → convocação
por recorte, e que cada desfecho obriga nova apuração com motivo.

### Tabela — onde o operador precisa saber de antemão

Legenda: **B** = pensar como o banco (identidade, forma, chave, invariante interna); **T** = orientação de
tarefa legítima (o Edital decide, a tela precisa dizer); → proposta.

| # | Ponto | Evidência | Tipo | Poderia virar |
|---|---|---|---|---|
| 1 | Ampla concorrência em 3 grafias (linha geral, Modalidade "AC", ponteiro); a tela sugere que não precisa declarar; sem AC declarada, 1 cota = todos assumidos cotistas, ≥2 = não-cotista não se inscreve | `_perfil.html:195`; `rascunho.py:280-313`; `validation.py:1124-1160` (só aviso, e a mensagem fala do quadro, não da inscrição) | **B** | inferência: Perfil com lista reservada oferece "Ampla concorrência" ao candidato pela linha geral, sem Modalidade AC; no mínimo, IMPEDE/aviso que nomeie a consequência na inscrição; pré-selecionar como ampla a única Modalidade sem percentual (a própria ajuda diz que vazio "é o caso da ampla", `compor_perfis.html:43-44`) |
| 2 | "Corte" é pré-condição da convocação: "sem corte não há geração, sem geração não há faixa, e sem faixa não há convocação"; para convocar sem cortar é preciso declarar um corte que "não governa Etapa alguma" com alvo, empate e continuação | `_como_preencher_o_marco.html:54-65`; `validation.py:1955-1985` (IMPEDE 046); `:823-853` | **B** | default no marco final/único: alvo "o que o quadro publicar", "não governa Etapa alguma", suplentes 0; perguntar em linguagem de Edital ("quantos são chamados?") |
| 3 | Forma de convocação "Não declarado" é opção válida, publica sem achado, e a comunicação é recusada depois ("declare por Retificação") | `_perfil.html:241-252`; `validation.py:1011-1013`; `comunicar.py:164-170` | T (com consequência escondida) | declarar uma vez no Edital e aplicar aos Perfis; aviso/IMPEDE na publicação quando há corte (convocação esperada) |
| 4 | Etapa decisória nasce **não** eliminatória (caixas desmarcadas) e a consolidação a recusa sempre; pontuada+eliminatória exige nota mínima rotulada "(opcional)"; "Avaliações por inscrição" >1 nunca tem Resultado | `_etapa.html:73,158-167,175-184`; `resultados/domain/regra.py:57-99`; 046 `validation.py:1787-1930` | **B** | default: decisória ⇒ eliminatória marcada (default não é exigência — FR-047 da 013 proíbe exigir, não sugerir); ressalva no rótulo da nota mínima como a 037 fez no peso; esconder avaliações>1 até existir regra de combinação |
| 5 | "Classificatória" só filtra o seletor de Etapas do marco; esquecê-la no passo 4 esvazia o passo 5 | `_marco.html:103-115,145-151`; `views.py:2276`; `regra.py:12` | **B** | derivar: Etapa enumerada por marco é classificatória |
| 6 | Fato do desempate declarado no passo 2 (Perfis) para ser consumido no passo 5; "maior idade" = MENOR_VALOR de fato DATA; seletor oferece fatos de todos os Perfis e a publicação recusa o de outro | `_fato.html:27-28`; `_criterio.html:17-43`; `views.py:2278-2282`; `validation.py:766` | **B** | catálogo de critérios na língua do Edital ("maior idade" cria o fato); tipo inferido do alvo; filtrar fatos do Perfil; ordem pela posição (`_criterio.html:10-14` pede número) |
| 7 | Método do sorteio: instante ISO/RFC 3339 com fuso digitado; ocorrência com armadilha de formato; regra enum + prosa duplicadas (substituição tem 1 opção); derivação livre sem ajuda; recusas citam `occurrenceAt`, `rule`, `text` | `_marco.html:322-401`; `compor_classificacao.html:70-139`; `editais/domain/perfis.py:444-455,560-573` | **B** | instante pelo Evento "Sorteio" do Cronograma (datetime-local, fuso institucional); prosa gerada do enum; substituição pré-selecionada |
| 8 | Marco de sorteio pergunta empate na última posição (obrigatório) numa ordem total; mostra casas/arredondamento e critérios de desempate | `_marco.html:154-172,539-549,582-590`; `validation.py:823-831`; `sorteios/application/sorteio.py:353-354` | **B** | ocultar e derivar para POR_SORTEIO (contraria a SC-139 da 030) |
| 9 | Documento "Chave" obrigatória, sem espaços, não retificável | `_documento.html:6-16`; `mutabilidade.py:483-487` | **B** | derivar do nome na criação, oculta |
| 10 | Anexo é cadastrado no passo 7 mas vinculado ao documento no passo 6 | `_documento.html:92-103`; `views.py:912-915` (justificativa invertida) | T (ordem) | inverter a ordem ou permitir subir o modelo no cartão do documento |
| 11 | Alcance do documento: 5 formas, uma delas oferecida e recusada (Todos + Modalidade de um Perfil); o recorte transversal depende do **código** da Modalidade igual em todos os Perfis e da denominação idêntica (maiúscula e acento contam) | `_documento.html:41-83`; `forms.py:1495-1530`; `validation.py:2600,2638`; 044 D-005 | **B** | não oferecer a combinação recusada; aviso de códigos quase iguais (PcD/PCD) |
| 12 | Tipo **e** Descrição do Evento obrigatórios; o Tipo é texto livre, não retificável, e nada o lê | `_evento.html:19-27`; `mutabilidade.py:423-427`; `inscricoes/domain/periodo.py:7` | **B** | tornar retificável (a razão escrita não confere com o código) ou fundir com a descrição |
| 13 | ~15 campos não retificáveis sem aviso no ponto de decisão (Perfil.code, reserveType, Modalidade.code, fato.type, marco.stages, targetKind, governedStage, continuation, tipo/alvo/whenMissing do desempate, schedule.type, key, momento do requerimento) | `mutabilidade.py:197,226,236,266,304,326,381,391,403-420,423,483`; só `retificar.html:127-139` os lista | T | marca "não se corrige depois de publicado" no rótulo/`como-preencher` |
| 14 | Cadastro Reserva limitado/limite: publicado, espécie não retificável, sem efeito na execução; o que executa é "Suplentes" do corte | `_perfil.html:101-127`; RC-58; consumidores só de exibição (`portal/views.py:199`) | T/B | ligar os dois, ou dizer no cartão que o limite é só publicado |
| 15 | `callForm`, reversão, método (divergência) e desempate por Perfil/marco quando o Edital os declara uma vez | `_perfil.html:214-252`; estudo §6.2 | T (repetição) | Edital declara, Perfil herda (como o método comum já faz) |
| 16 | Processo × Edital: inventar código e título do Processo | `processo_criar.html:33-50`; estudo §7.1 | **B** | default do Edital único |
| 17 | Selo "Classificação concluída" com um marco em qualquer Perfil; comentário diz que classificar é opcional, a publicação exige marco e corte por Perfil | `views.py:1068-1072` × `validation.py:1740-1780,1955-1985` | T (guia errado) | selo por Perfil e pela executabilidade |
| 18 | Operação por recorte: ordem, corte, apuração, cada um um ato por recorte; recorte vazio emitido à mão; cada desfecho torna a apuração obsoleta e convocar é recusado até nova apuração com motivo | `ordenacao.html:80-86`; `corte.html:77`; `ocupacao.html:149-164`; `convocacao.html:30,54` | T (cadeia) / B (obsolescência) | emissão em lote por marco; recorte vazio constituído; apuração seguinte automática quando a causa é desfecho registrado |
| 19 | Convocação: espécie (vaga inicial/suplência/regularizar), vencimento e fundamento a cada chamada; prazo do Edital "o sistema não guarda" | `convocacao.html:120-140,325-327` | T | espécie derivada do estado da vaga; prazo estruturado no Edital; fundamento pré-preenchido |
| 20 | UUID cru na tela do recurso (objeto, ato vigente, versão) | `recurso.html:33-37`; `selectors.py:258-261` (deliberado, FR-092) | **B** | rótulo legível com UUID em detalhe |
| 21 | "marco" = Evento no pulso/Supervisão e = marco classificatório; "Geração" = faixas e = arquivo exportado | `processo_detalhe.html:110-124`; `supervisao.html:95,109`; `ordenacao.html:21`; `matriculas.html:19` | Const. §I | renomear um dos dois |

### Onde o sistema já infere, restringe e guia (manter)
- Revelação progressiva do marco pela forma da ordem (`_marco.html:47-68`, 030 FR-413), combinação e
  normalização só com ≥2 Etapas (`:461-492`), código e denominação do marco derivados do Perfil
  (`editais/domain/marcos.py:53-75`), 2 casas/meio para cima (`marcos.py:50`).
- Linha geral derivada das vagas imediatas sem lista reservada, e a notícia da rederivação
  (`_linha_do_quadro.html:29-31`; `compor_base.html:56-58`).
- Período de inscrições designado por Evento, sem redigitar datas (`compor_inscricao.html:15-27`); fase do
  Evento derivada (045 D-001); situação pública derivada (047).
- Ampla e reversão só depois da 1ª Modalidade (`_perfil.html:173-229`); peso antecipado no cartão
  (`_marco.html:140-144`); "Peso (opcional até um marco enumerar)" (`_etapa.html:146`).
- Método comum (030 FR-429); vocabulário fechado de algoritmo e fonte (035).
- Seções geradas da estrutura (`compor_conteudo.html:20-24`); Duplicar Perfil (043); Partir de Edital
  anterior (023).
- Pendência com etapa, âncora e nome legível (`views.py:660-787`); definições `<dfn>` no primeiro uso
  (030 FR-424); telas de operação dizem "abrir não constitui ato" e apontam o passo anterior
  (`ocupacao.html:149`).

## Pergunta 2 — Complexidade transferida e over-engineering (030–048)

### Conceitos novos que o operador passou a carregar
| Spec | Conceito para o operador | Reduziu? | Custo novo |
|---|---|---|---|
| 030 | pergunta de entrada (forma da ordem); método comum × divergência implícita (qualquer campo preenchido no marco = método próprio, que precisa estar inteiro) | sim (28→<10 controles) | a divergência é inferida do conteúdo (`_marco.html:262-287`); campo oculto que viaja (FR-418) e, na Retificação, `order_production_contradiz_o_metodo` manda "retirar o método" que a composição escondeu (`validation.py:2131`); terceira leitura de "sorteia?" (`views.py:2862`) |
| 032 | "Perfil sem marco" impede; corte "que não governa Etapa alguma" | executabilidade | o corte vira pré-requisito de convocação |
| 034 | recorte como unidade de ato; "ordem única do marco" × ordem do recorte | fecha a cadeia das cotas | N recortes × (ordem + corte + apuração), sem lote |
| 035 | ocorrência "terminando no número"; vocabulário executável | sorteio reproduzível | armadilha de formato ensinada por ajuda longa |
| 036 | ato de instrução do recurso | prova chega ao julgador sem ampliar papel | um ato a mais por recurso numa equipe de 2–3 |
| 043 | duplicar (código + localidade) | 530→101 interações | as N cópias continuam N na Retificação e no PDF (RC-13); documentos restritos não vão |
| 044 | código da Modalidade como identidade entre Perfis; 5ª forma de recorte; denominação idêntica (IMPEDE); lista exigida gravada | 112→7 linhas | a 4ª forma continua oferecida e recusada; o código estrutural passa a ter efeito documental invisível na digitação |
| 045 | fase derivada; ausência relativa ao alcance | **remove** declaração | — (o bom exemplo) |
| 046 | Resultado "exigido pelo fluxo" (4 consumidores), decisória "porta × parcela", invariante de corte por Perfil | fecha RC-29/30 | a mesma Etapa impede ou só avisa conforme marco/corte/sorteio; 2 códigos para a mesma condição; corrigido no mesmo dia (RC-114) |
| 047 | nenhum para o operador | derivação pública | — |
| 048 (PR) | "pode passar a existir": nascer inteiro, janela que nasce só concede (D-003), corte que não nasce se a Etapa governada já tem Resultado (D-002) | fecha RC-37/38 | assimetrias novas na Retificação; conserta a jusante o que a composição deixou publicar (RC-37 nasce do item 1 da P1) |

### Onde a redução de esforço criou outro conceito ou revisão
1. **Método comum (030)**: menos repetição, mais um estado implícito (comum × divergente pelo conteúdo) e
   uma contradição possível na Retificação que o operador não vê na composição.
2. **Duplicar (043)**: tirou 80% da digitação, mas manteve N cópias independentes; a correção de uma cláusula
   comum depois de publicar custa N edições, e a divergência entre cópias não é conferida (RC-31, só nome é
   comparado na 044).
3. **Recorte transversal (044)**: para não mover a Modalidade ao Edital (decisão de 25/09), o **código**
   digitado passou a ser a chave entre Perfis — e com ele o IMPEDE de denominação idêntica. É o catálogo da
   039 implementado por convenção de digitação.
4. **Contrato de executabilidade (046)**: em vez de impedir as três combinações no cartão da Etapa, a spec as
   deixa compor e decide na publicação por quem consome o Resultado — mais regra, mais mensagem, mais
   exceção (porta), e o operador só descobre na Revisão.
5. **048**: a porta da Retificação para acrescentar Modalidade responde a um Edital que não deveria ter sido
   publicado sem a ampla (item 1 da P1).

### Flexibilidade maior que a dos Editais (estudo §2, §6.2; achados externos)
- Por Perfil o que os Editais declaram uma vez: forma de convocação, reversão, desempate, método (estudo
  §6.2; "a cláusula do corte é idêntica, palavra por palavra", achados-editais-externos.md:47).
- Tipos genéricos de fato e de critério (MAIOR/MENOR_VALOR_DE_FATO) para um repertório real pequeno
  (maior idade, pontuação numa Etapa, tempo de experiência).
- "Avaliações por inscrição" aberto sem regra de combinação (beco declarado, `compor_etapas.html:42-45`).
- Recurso em três estados, e na Retificação com assimetria (048 D-003).
- Sorteio: 10 campos, dois pares enum+prosa, um enum de uma opção; empate exigido onde não existe.

### Sinais de over-engineering acumulado
- **Estrutura sem consumidor**: `normativeRule.calculation/rounding/distribution/callRules` — JSON gravado,
  publicado, não retificável com razão constitucional, sem tela e sem leitor (`editais/models/perfis.py:387`;
  `publish_edital.py:138-141`). `reserveLimit` publicado sem efeito (RC-58). A Constituição §V pede o
  contrário para estrutura antes de consumidor.
- **Razão normativa que o código desmente**: `schedule/type` não retificável por "ligar o Cronograma às
  regras" (`mutabilidade.py:423-427`) × "Nada procura texto em `type`" (`periodo.py:7`).
- **Validação como lugar da regra de forma**: 98 construtores de achado em `validation.py` (2.978 linhas);
  várias combinações que o cartão poderia impedir (decisória não eliminatória, empate em sorteio, fato de
  outro Perfil, Todos + Modalidade de um Perfil) são recusadas só na publicação.
- **Máquina do contrato**: 4 naturezas + `PODE_PASSAR_A_EXISTIR` + `fechou_caminho` (`mutabilidade.py`).
  Justificável pela imutabilidade; o custo aparece para o operador só como surpresa na Retificação.
- **Proporção spec × jornada**: 040 tem 1.132 linhas para uma tabela de leitura; 047 anota que 13 de 26
  frentes já estavam atendidas; comentários de template maiores que o markup (`_marco.html`, 596 linhas).
  Carga de manutenção, não do operador.
- **Não é over-engineering (justificado)**: congelamento e manifesto do sorteio (auditabilidade pública), a
  separação julgar × ver prova (contraditório), a imutabilidade das publicações, a derivação da fase (045) e
  da situação pública (047).

## Pergunta 3 — Oportunidades de inferência (priorizadas: decisão que o operador toma sem ter como saber)
1. **Ampla concorrência implícita** quando o Perfil tem lista reservada (ou IMPEDE com a consequência na
   inscrição) — elimina Modalidade AC, ponteiro e a grafia-armadilha (`rascunho.py:280-313`).
2. **Forma de convocação no Edital, herdada pelos Perfis, e cobrada na publicação** quando há corte
   (`validation.py:1011`; `comunicar.py:164`).
3. **Caráter derivado da forma**: decisória ⇒ eliminatória pré-marcada; ressalva "obrigatória se
   eliminatória" na nota mínima; esconder avaliações>1; classificatória derivada da enumeração.
4. **Regra de corte com default de contexto**: marco único/final → "o que o quadro publicar", "não governa
   Etapa alguma", suplentes 0; marco de sorteio seguido de Etapa decisória → sugere governá-la; empate
   derivado (ou oculto) em POR_SORTEIO.
5. **Modelo de Edital (origem controlada, Const. "Modelos reutilizáveis")** por família — FIC/sorteio antes da
   análise documental; seleção por títulos — com Etapas, marco, corte, desempate, forma de convocação e
   método já declarados. Contorna a objeção da 029 D-002 (não é eixo que regra consome, é rascunho de
   partida) e o "primeira oferta sempre do zero" (estudo §1.5).
6. **Método do sorteio**: instante do Evento do Cronograma; prosa gerada do enum; substituição
   pré-selecionada.
7. **Desempate em linguagem de Edital**: "maior idade" cria o fato; tipo pelo alvo; ordem pela posição; fatos
   filtrados pelo Perfil.
8. **Operação**: emitir ordem/corte de todos os recortes do marco num ato; constituir o recorte vazio;
   apuração seguinte automática após desfecho; espécie da convocação derivada; fundamento pré-preenchido.
9. **Quadro sugerido pelo percentual** (o sistema já calcula piso/teto em `validation.py:2934-2960`), editável.
10. **Chave do documento derivada do nome**; Processo derivado do Edital único; Tipo do Evento retificável.
11. **Disclosure barato**: marcar no rótulo, na composição, os campos que não se retificam.
