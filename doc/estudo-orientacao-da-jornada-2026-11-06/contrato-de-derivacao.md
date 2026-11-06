# Contrato de derivação das situações

Parte do [estudo de orientação da jornada](README.md). Pedido na revisão de 06/11/2026: documentar
**exatamente** como cada situação se deriva dos registros que já existem, sem estado persistido, para
que a orientação não vire uma segunda lógica de workflow.

Referências relativas a `backend/processo_seletivo/`, conferidas na base `250efe97`.

- **[C]**: a derivação existe e é usada hoje por alguma tela.
- **[N]**: composição nova de predicados existentes; não cria regra, mas precisa de teste que a
  confronte com a tela do ato.
- **[D]**: diverge do que o código faz hoje, e a mudança é decisão (ver o fim).

---

## 1. Os princípios

1. **Ausência de ato não é pendência.** Uma célula sem ato vigente nunca é exibida crua. Antes, ela é
   classificada numa das situações da §2, e só uma delas, *Pendente*, diz que alguém deve agir agora.
2. **Nenhum estado novo.** Cada situação é a resposta de uma função que já decide alguma coisa numa
   tela de ato, ou uma composição delas ([N]). Nada é gravado, e nada é calculado de novo com regra
   própria. É a lição da `103` e da `104`: duas regras para a mesma pergunta divergem na primeira
   mudança.
3. **Não há "próximo passo" único.** A derivação devolve um **conjunto** de providências, e cada uma diz
   a natureza, o responsável, se a pessoa que olha pode praticá-la e, se não puder, por quê. Quem
   escolhe o que mostrar primeiro é a apresentação, por regra fixa (§4). Não existe `proximo_passo()`
   que escolha um ato.
4. **Prever não é autorizar.** A tela do ato continua sendo quem recusa (FR-025 da `002`). A derivação
   antecipa o que ela diria. Se as duas divergirem, a derivação está errada.
5. **O custo é por Edital, e não por inscrição.** As leituras são em lote (`resumo_dos_marcos`: 4
   consultas; `sorteios_do_edital`: 2).

---

## 2. As situações de apresentação

São sete, para cada par (ato, lista de concorrência). **Nenhuma é coluna nem estado do domínio**: são
rótulos de leitura.

| Situação | Significa | Responde à pergunta |
|---|---|---|
| **Feito** | Há ato vigente, e o sistema não o sabe para trás | "O que já aconteceu?" |
| **Obsoleto** | Há ato vigente que o sistema sabe estar para trás (Retificação, sucessão, movimento posterior) | "O que precisa ser refeito?" |
| **Pendente** | O ato é esperado e os pré-requisitos estão satisfeitos: alguém pode praticá-lo agora | "O que precisa acontecer?" e, cruzado com o responsável, "o que **eu** posso fazer agora?" |
| **Aguarda** | Os pré-requisitos do sistema estão satisfeitos, mas falta um fato externo ou uma hora: a extração publicada, o fim do período, o fim do prazo recursal, a resposta do convocado | "O que está esperando o mundo?" |
| **Impedido** | Há uma condição que a sequência normal não resolve e que pede outro ato, quase sempre uma Retificação: extração anterior ao congelamento, forma de convocação não declarada, quadro de vagas ausente | "O que está bloqueado, e por quê?" |
| **Depois** | Falta um ato anterior da mesma lista | "O que ainda não é a vez?" |
| **Não se aplica** | O ato não vai acontecer nesta lista: ninguém se inscreveu nela, o marco não corta, ninguém concorreu | "O que não precisa acontecer?" |

**"Depende de outra pessoa" não é situação, é responsabilidade.** Uma providência *Pendente* tem um
responsável, que é "você" ou um papel. A pergunta da revisão ("o que depende de outra pessoa?") é
*Pendente* com outro responsável.

### As perguntas da revisão, respondidas pelo contrato

| Pergunta | Situações | Filtro |
|---|---|---|
| O que ainda precisa acontecer? | Pendente, Obsoleto, Aguarda, Impedido | só providências esperadas ou condicionais ativas (§3) |
| O que posso executar agora? | Pendente, Obsoleto | o responsável é a pessoa (§3.2) |
| O que depende de outra pessoa? | Pendente, Obsoleto | o responsável é outro papel |
| O que está impedido? | Impedido, Aguarda | com a razão e, no Impedido, quem a resolve |
| O que não se aplica? | Não se aplica | com a razão |

---

## 3. A providência

A unidade que a orientação mostra é a **providência**, e não a célula. Ela segue a forma do
`ObjetoDeTrabalho` da `104` (`interface/trabalho.py`), com quatro campos a mais:

| Campo | Conteúdo | Origem |
|---|---|---|
| natureza (104) | relação, semente, sorteio, ordem, corte, apuração, resultado, convocação, conferência, recurso, avaliação, Retificação | o ato |
| título, onde | "Edital 35/2026", "Cefor · Ampla concorrência" | Perfil, marco, lista |
| ato | o verbo da tela ("Emitir a comunicação", "Congelar a relação") | o rótulo do botão da tela do ato |
| situação | uma das sete da §2 | §5 |
| **responsável** | "você" ou o papel ("quem publica resultado", "a presidência da comissão") | §3.2 |
| **expectativa** | esperada · condicional · facultativa | §3.1 |
| **razão** | por que está Aguarda, Impedido ou Não se aplica, com a frase que a tela do ato já usa | §5 |
| url | a tela do ato, nunca a confirmação (D-003 da `104`) | a mesma da condução |
| desde · até | desde quando espera; prazo, se houver | o ato anterior; o vencimento |

### 3.1 Expectativa: o que é obrigatório, condicional ou facultativo

O sistema não sabe o que o Edital *obriga* juridicamente; sabe o que o rito declarado **espera**. A
expectativa vem do conteúdo vigente, e não de opinião:

| Expectativa | Quando | Exemplos |
|---|---|---|
| **Esperada** | O conteúdo vigente declara o ato para aquela lista | Relação e sorteio (marco com `drawMethod`); corte (marco com regra de corte, `corta(marco)`); apuração (lista com linha no quadro); resultado (todo marco); desfecho de convocação vencida |
| **Condicional** | Só existe se uma condição derivada é verdadeira | Faixa seguinte: há déficit apurado e a fila acabou (`fila.esgotou`). Nova chamada: desfecho que abre vaga e fila com gente. Sucessão: ato obsoleto |
| **Facultativa** | O sistema oferece e nada depende dela | Aviso aos candidatos (066); definição dos documentos da formalização (117) |

**A facultativa não entra em "Em aberto"** (o nível 1 da apresentação). Ela continua onde está hoje,
como ação secundária.

### 3.2 Responsável e "você"

| Ato | Responsável | Como saber se é você |
|---|---|---|
| Relação, semente, sorteio, ordem, corte, apuração, convocação, desfecho | quem conduz (Gestor ou a presidência da comissão) | `pode_gerir_comissao(ator, processo)`, a porta de `_edital_para_classificar` (`interface/views.py:7327`) [C] |
| Resultado | quem publica resultado | `ator.can("resultado:publicar")` (`views.py:9403`) [C] |
| Conferência de documento | quem conduz, ou o alocado à conferência | `views.py:7356-7365` [C] |
| Avaliação | o avaliador alocado | a carga de Minhas Etapas, a mesma da `104` [C] |
| Recurso | quem julga | `recursos_admitir.PERMISSAO` [C] |
| Retificação (a saída do Impedido) | quem elabora Retificações | `acoes.pode_retificar` [C] |
| Encerrar | Gestor | `edital:encerrar`; o Encerrar nunca é providência, só ação |

A segregação de funções entra como entra hoje no bastão (`acoes.proximo_passo`): quem não pode por
segregação não é "você", e a razão é dita.

---

## 4. A regra fixa de apresentação

A derivação não escolhe; a apresentação ordena, sempre do mesmo jeito:

1. **As suas**, *Pendente* ou *Obsoleto*: primeiro as que têm prazo, pelo prazo mais próximo; depois as
   demais, pela espera mais antiga, como a faixa da `104`.
2. **As de outros papéis**, agrupadas por papel, com a contagem.
3. **As que aguardam ou estão impedidas**, com a razão.
4. **Não se aplica** só aparece no nível 2, e só para dizer que nada falta ali.

O nível 1 mostra até cinco itens (o `MOSTRADOS` da `104`) e "mais N".

---

## 5. Derivação por ato

Para cada ato e lista: em que condição o registro existente produz cada situação. O que não está numa
linha cai em *Depois*.

### Inscrições (marco de qualquer espécie)

| Situação | Quando | Fonte |
|---|---|---|
| Aguarda | O período está aberto ou por abrir | `recusa_por_inscricoes_em_curso` (`avaliacoes/domain/conjunto.py:68`) [C]; `PERIODO_EM_CURSO`/`PERIODO_POR_ABRIR` de `pendencias_do_edital` [C] |
| Feito | O período terminou | a mesma função devolve `None` [C] |
| Impedido | Não há término declarado | `PERIODO_SEM_TERMINO` [C] |

### Relação (marco com sorteio)

| Situação | Quando | Fonte |
|---|---|---|
| Depois | O método declara uma Etapa de habilitação (`qualifyingStageId`) que não está consolidada | `sorteios/application/habilitacao.habilitadas_na_etapa` [C, composição N] |
| Não se aplica | Nenhuma inscrição enviada declarou a lista: `projetados == 0` e a relação não está congelada. Congelar seria recusado (`relation_would_be_empty`) | `previa.recortes_do_marco`, campo `projetados` e `congelada` (`sorteios/application/previa.py:307-329`) [C]; o texto é o da tela ("Não há universo a comprometer aqui") **[D1-a]** |
| Aguarda | O período de inscrições não terminou | `inscricoes_em_curso` do mesmo retorno [C] |
| Pendente | O período terminou, `projetados > 0`, a relação não está congelada, e congelar agora não condena o sorteio | `congelada == False` e `congelar_agora_inviavel is None` [C, composição N] |
| Impedido | Congelar hoje condenaria o sorteio (a extração declarada é do mesmo dia ou anterior) | `congelar_agora_inviavel` (102, FR-2659) [C]; a saída é a Retificação, com o `primeiro_dia` |
| Feito | `congelada == True` e `diagnostico_da_relacao is None` | [C] |
| Obsoleto | `diagnostico_da_relacao` preenchido: a relação congelada nunca sorteará | `_diagnostico_da_relacao` (`previa.py:254-292`) [C] |

### Semente (extração)

| Situação | Quando | Fonte |
|---|---|---|
| Depois | Nenhuma relação do marco está congelada | as relações acima [N] |
| Aguarda | Há relação congelada, a ocorrência da vez não foi observada, e o instante declarado ainda não chegou | `ocorrencia`, `proxima_referencia` e `ocorre_em` de `recortes_do_marco` [C]; é o `occurrence_not_due_yet` (`sorteios/application/ocorrencia.py:88-100`) [C] |
| Pendente | Há relação congelada, a ocorrência não foi observada, e ou o instante passou, ou o Edital não o declara | os mesmos campos [N]. **Sem instante declarado, o sistema não sabe se é cedo**: a providência diz "observe depois da extração; antes dela, nada é gravado" |
| Impedido | Toda a cadeia de substituição foi consumida | `recusa_da_ocorrencia` [C]; a saída é a Retificação ("Prosseguir exige Retificação que declare outro método") |
| Feito | Há `OcorrenciaDaFonte` válida para a referência da vez | [C] |

A falha de acesso à fonte (`source_unreachable`) **não muda a situação**: nada é gravado, e ela
continua *Pendente* (P0, J-12).

### Sorteio

| Situação | Quando | Fonte |
|---|---|---|
| Não se aplica | A relação não se aplica | acima |
| Depois | A relação ou a semente não estão feitas | acima |
| Impedido | A extração é anterior ao congelamento (`occurrence_precedes_freeze`) | `diagnostico_da_relacao` [C] |
| Pendente | Relação congelada, semente observada, sem sorteio vigente | `sorteio` do recorte é `None` [C] |
| Feito / Obsoleto | Há sorteio vigente; obsoleto se a relação foi sucedida | `sorteio`; `_divergencias_do_sorteio` (`classificacao/application/selectors.py:177-224`) [C] |

### Etapa de avaliação (incluída no complemento de generalidade)

A Etapa vale para o Edital, por inscrição, e não por lista. No nível 2 ela ocupa todas as listas do
Perfil. Os números são os que a tela da distribuição já mostra (captura `33`): participantes, sem
nenhum avaliador, sem avaliador suficiente, com avaliação pendente, prontas para consolidar, já
consolidadas.

| Situação | Quando | Responsável | Fonte |
|---|---|---|---|
| Não se aplica | A Etapa é governada por um corte, e a inscrição não está na faixa; ou o Perfil não tem inscrito | — | `faixa.etapa_governada`; contagem do Perfil |
| Depois | A Etapa é governada e o corte que a alimenta não foi emitido | — | `jornada()` (094) e o corte vigente |
| Aguarda | A Etapa aponta um Evento do cronograma (`scheduleEventId`) que ainda não chegou | — | o Evento, como a Agenda o lê; a Etapa **não** tem convocação para comparecer ([registro de 09/10](../registro-convocacao-para-etapas-2026-10-09.md)) |
| Pendente: distribuir | Há inscrição sem avaliador suficiente | a presidência da comissão ou quem gere comissão | a distribuição; o sinal UX-003 da Supervisão [C] |
| Pendente: avaliar | Há avaliação pendente atribuída | o avaliador alocado | a carga de Minhas Etapas, a mesma da `104` [C] |
| Pendente: consolidar | Há inscrição pronta para consolidar | a presidência | a distribuição [C] |
| Feito | Toda inscrição da Etapa consolidada | — | a distribuição [C] |
| Obsoleto | Resultado sucedido por reavaliação, ou providência de recurso pendente | a presidência | `REAVALIACAO_PENDENTE`, `PROVIDENCIA_PENDENTE` de `pendencias_do_edital` [C] |

A contagem é parte da providência ("8 de 12 avaliadas"), e não um estado novo. A partição completa é a
de `prontidao.panorama_da_etapa` (eliminada antes, aguardando a anterior, fora do corte, consolidada,
pronta, não consolidável, reavaliação determinada); ver o [mapa das Etapas](mapa-das-etapas.md) §1.5.

**Impedido** na Etapa: `regra_de_combinacao_ausente` (mais de uma avaliação prevista),
`regra_insuficiente` (decisória não eliminatória; pontuada eliminatória sem mínima) e o corte obsoleto
que governa a Etapa (`resultados/domain/regra.py:57-97`; `prontidao.py:164-201`).

**A expectativa vem da ligação da Etapa com os marcos** (`editais/domain/validation.py:2024-2067`):

- é **esperada** se for enumerada por marco de pontuação, governada pelo corte, de habilitação do
  sorteio, ou se filtrar, pela progressão, uma Etapa esperada;
- enumerada por marco de sorteio, é esperada **só se for consolidável**;
- sem nenhuma dessas ligações, ela é **declarada, sem efeito no GPS**: não é providência, e aparece
  como "Atenção" (D9).

### Ordem (marco por pontuação)

| Situação | Quando | Fonte |
|---|---|---|
| Depois | Alguma Etapa enumerada pelo marco não está consolidada para o universo do recorte | a seção acima [N]. **Hoje nada diz isso**: a condução mostra *Falta*, e `calcular_ordem` emite uma ordem vazia sem recusa (captura `32`; G-01 do complemento) |
| Pendente | Sem ato vigente e a proposta é calculável | `estado_do_marco` sem exceção [C] |
| Feito, com a nota "ninguém concorreu" | Há ato vigente sem posição | D-003 da `049`, `_celula_da_ordem` (`interface/conducao_do_marco.py:236-256`) [C] |
| Obsoleto | `estado_do_marco(...)["obsoleto"]` | [C] |

**Diferença entre as duas espécies, e ela importa**: no marco de sorteio, a lista vazia **não chega**
a ter ato (congelar é recusado), e a cadeia inteira é *Não se aplica*. No marco por Etapas, a lista
vazia **tem** ordem emitida, e ela é *Feito*, "ninguém concorreu". Hoje a condução mostra a primeira
como *Falta* (J-06).

### Corte

| Situação | Quando | Fonte |
|---|---|---|
| Não se aplica | O marco não corta | `corta(marco)`; `_celula_do_corte` (`conducao_do_marco.py:274-284`) [C] |
| Depois | Sem ordem vigente | `sem_ato_vigente` (`classificacao/application/corte.py`) [C] |
| Pendente | Ordem vigente e sem geração | `estado_do_corte(...)["geracao"]` vazio [C] |
| Feito / Obsoleto | Geração vigente; obsoleto se `estado["obsoleto"]` | [C] |

### Apuração

| Situação | Quando | Fonte |
|---|---|---|
| Não se aplica | Sem linha no quadro de vagas | `linha_do_quadro(...) is None`, `_celula_da_apuracao` (`conducao_do_marco.py:287-303`) [C] |
| Depois | Sem ordem vigente | `ordem_nao_vigente` [C] |
| Pendente | Ordem vigente, sem apuração | `apuracao_vigente is None` [C] |
| Feito / Obsoleto | Apuração vigente; obsoleta se `causas_de_obsolescencia(vigente)` | `ocupacao/application/selectors.py:125` [C] |

### Resultado

| Situação | Quando | Fonte |
|---|---|---|
| Depois | Sem ordem vigente | `_celula_da_publicacao` diz hoje *Falta*, "falta a ordem" **[D2]** |
| Pendente | Ordem vigente nunca divulgada; ou só preliminar, e a definitiva é publicável | `divulgacao_do_ato(...)["nunca_divulgado"]` [C]; `publicabilidade.aferir(natureza="DEFINITIVA")` sem impedimento [C]. No 35, aferido em 06/11, a definitiva do Cefor é publicável |
| Aguarda | Só preliminar, e a definitiva espera o prazo recursal ou um recurso | `janela_aberta_ate`; `impede_a_definitiva` de `aferir` [C] |
| Obsoleto | `divulgacao_do_ato(...)["defasadas"]` | [C] |
| Feito | Definitiva vigente; ou preliminar, se o Edital não pede definitiva | [C]. **Se "preliminar" conta como Feito ou Pendente é decisão do Edital** (D8) |

### Convocação (por convocação, e agregada por lista)

O domínio já tem os quatro estados (`convocacao/domain/prazo.py:59`), e a derivação os usa como estão:

| Estado do domínio | Situação da providência | Responsável |
|---|---|---|
| `CONVOCADO_PRAZO_NAO_INICIADO` | **Pendente**: emitir a comunicação (ou registrar a publicação, na forma por publicação) | quem conduz |
| `CONVOCADO_PRAZO_EM_CURSO` | **Aguarda** a resposta, até o vencimento | o convocado |
| `CONVOCADO_VENCIMENTO_DECORRIDO` | **Pendente**: registrar o desfecho (não atendimento) | quem conduz |
| `DESFECHADO` | Feito | — |

E, por lista:

| Situação | Quando | Fonte |
|---|---|---|
| Depois | Sem apuração vigente | `apuracao_ausente` (`convocacao/application/fluxo.py:425-431`) [C] |
| Impedido | Apuração obsoleta; ou forma de convocação não declarada | `apuracao_obsoleta`; `forma_de_comunicacao_nao_declarada` (`comunicar.py:177-183`) [C] |
| Pendente | Há titular não chamado (`leitura_do_recorte(...)["fila"]` com titular); ou vaga a ocupar com gente na fila | `leitura_do_recorte` (`convocacao/application/selectors.py:359`) [C, composição N] |
| Pendente, condicional | Vaga a ocupar e a fila acabou: pedir a faixa seguinte na ocupação | `esgotou` + `ocupacao_do_recorte` [C] |
| Não se aplica | Apuração sem vaga a ocupar, e nenhuma convocação | `ocupacao_do_recorte` [N] |
| Feito | Nenhuma vaga a ocupar, e toda convocação com desfecho | [N] |

**O relatório e o Encerrar não fazem essa distinção hoje**: `CONVOCACAO_AGUARDANDO`
(`interface/relatorio_do_edital.py:1194`) conta junto a convocação cuja comunicação nunca saiu, e
diz "aguardando resposta, até 10/11" de uma convocação cujo prazo, pela regra do próprio domínio,
não começou (J-07). A derivação usa `prazo.estado`.

### Conferência de documentos (115/117)

| Situação | Quando | Fonte |
|---|---|---|
| Aguarda | Documento obrigatório não apresentado, com prazo correndo | `leitura_da_chamada` [C] |
| Pendente | Documento apresentado e não conferido | `pendencias_para_incluir` (`convocacao/application/documentos.py`, usada em `desfechar.py:199`) [C] |
| Pendente: registrar o desfecho | Todos os obrigatórios conferidos e sem desfecho | a mesma leitura; é o "Falta: <itens>" de `documentos_nao_conferidos` ao contrário [N] |
| Não se aplica | O Edital não pede documento na convocação | conteúdo vigente [C] |

### Recurso, Retificação e avaliação

Como a `104` já faz, e pelas mesmas funções: `recursos_por_edital`, `atos_retificacao.ofertas` e a
carga de Minhas Etapas [C]. A orientação **não** reimplementa nenhuma: chama `trabalho.py`.

---

## 6. Onde o contrato muda o comportamento de hoje

Divergências entre o contrato e o código atual. Nenhuma é regra de negócio, mas todas são decisões de
apresentação que hoje estão escritas de outro jeito.

| | Hoje | Pelo contrato | Onde | Decisão |
|---|---|---|---|---|
| D1-a | Lista sem inscrito, num marco de sorteio: *Falta* em todas as células, e gestos oferecidos | *Não se aplica*, sem gesto | `_celula_da_ordem`, que não distingue "sem ato" de "não haverá ato" | P0 |
| D2 | Resultado sem ordem: *Falta*, "falta a ordem", decisão escrita no `data-model.md` da `049` | *Depois*. A contagem "0 de 3" não muda: só muda a palavra | `_celula_da_publicacao` | **D7** |
| J-07 | "Aguardando resposta" inclui prazo não iniciado | Os quatro estados de `prazo.estado` | `relatorio_do_edital.py:1194` | P0 |
| J-10 | O aviso de congelamento inviável no topo dos recortes, valendo também para a sucessão (decisão da `102`, FR-2659: "A sucessão também congela") | Mesma regra, mostrada junto do formulário de sucessão, e não como primeira frase da tela | `sorteio.html` | P0 |

---

## 7. Como se prova que não virou outra lógica

- **Teste de coerência por Edital**: para cada um dos seis Editais do banco de demonstração (35, 57,
  26, 51, 91, 72) e cada papel, toda providência *Pendente* para "você" leva a uma tela que oferece
  o ato habilitado; toda *Aguarda*/*Impedido* leva a uma tela que o recusa com a mesma razão.
- **Nenhum import novo de modelo em `interface/andamento.py`** além dos selectors citados: a
  derivação lê funções, e não tabelas.
- **Orçamento de consultas fixo por Edital**, medido como os da `104`.
