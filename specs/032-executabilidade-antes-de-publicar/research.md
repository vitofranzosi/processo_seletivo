# Research — 032 · Executabilidade antes de publicar

Fase 0. O que precisava ser descoberto antes de planejar, e o que a leitura do código respondeu.
Tudo aqui foi conferido na árvore em `d9d47ed` (`main` com a `030` mergeada), em 18/09/2026.

---

## R-1 · Onde a família nova mora, e como ela distingue publicação de retificação

**Decisão.** As verificações entram em `editais/domain/validation.py`, como funções dedicadas
chamadas por `validate_for_publication`, e as que precisam distinguir o ato recebem `ato` e saem
cedo quando ele não é `ATO_DE_PUBLICACAO`.

**Rationale.** O padrão já existe e é da `030`: `_forma_da_ordem_declarada(snapshot, *, ato)` abre
com `if ato != ATO_DE_PUBLICACAO: return []`, e o docstring dela explica por quê — o rascunho pode
estar pela metade, e a Retificação do acervo não pode ser cobrada de uma declaração que a capacidade
não oferecia quando aquele Edital foi composto. `validate_for_publication` já recebe
`ato: str = ATO_DE_PUBLICACAO`, e o padrão erra pelo lado que recusa.

**Alternativas descartadas.** Recusar em `replace_draft` — a `030` tentou, derrubou 759 testes e
tornou ilegal todo payload que o repositório produz; foi revertido e registrado. Recusar só no
serializer — contraria o Princípio IV, porque a interface administrativa invoca o command
diretamente e não atravessa o DRF.

**Consequência para o plano.** `FR-457` e `FR-467` são impeditivos e recebem `ato`. `FR-461` e
`FR-470` são avisos: aviso não impede publicação nenhuma, então não precisam do recorte por ato —
mas recebê-lo mesmo assim é o que evita encher a Retificação do acervo de avisos sobre o que ele já
publicou. **Recebem.**

---

## R-2 · Como o achado chega à etapa certa do assistente

**Decisão.** Nenhuma infraestrutura nova. `FR-458` se cumpre escolhendo bem o `path` de cada achado,
e — só onde o campo a corrigir mora em outra etapa — acrescentando uma linha a `DESTINO_POR_CODIGO`.

**Rationale.** `interface/views.py::_destino(caminho, codigo)` já resolve o destino lendo o caminho
**de trás para frente**, do segmento mais profundo ao mais raso, contra `DESTINO_DA_PENDENCIA`. A
entrada `"classificationMilestones": ("classificacao", "#titulo-classificacao", True)` já existe, e
o comentário dela registra o defeito que a motivou: toda pendência de marco terminava na tela de
Perfis, que é a única do assistente onde o conteúdo do marco não se corrige.

Logo:

| Achado | `path` proposto | Onde cai |
|---|---|---|
| `FR-457` Perfil sem marco | `/profiles/id=…/classificationMilestones` | `classificacao` ✔ |
| `FR-461` marco sem corte | `/profiles/id=…/classificationMilestones/id=…/cutRule` | `classificacao` ✔ |
| `FR-467` sorteio sem método | `/profiles/id=…/classificationMilestones/id=…/drawMethod` | `classificacao` ✔ |
| `FR-470` reserva sem apuração | `/profiles/id=…/vacancyTable` | `perfis` ✔ |

**Alternativa descartada.** Um campo novo "etapa" no `ValidationFinding`. Duplicaria a autoridade:
o caminho já **é** o endereço, e um segundo endereço divergiria do primeiro na primeira mudança.

---

## R-3 · A diferença entre "sem regra de corte" e "regra que não governa Etapa"

**Decisão.** `FR-461` dispara **apenas** sobre a ausência de `cutRule`. Marco cuja regra declara
não governar Etapa alguma não recebe aviso.

**Rationale.** É requisito publicado: a `014`, `FR-224`, manda a Regra de Corte declarar qual Etapa
governa **ou declarar explicitamente que não governa Etapa alguma**, e a própria `014` registra que
*"um marco pode declarar que não governa Etapa alguma: o corte é legítimo e não tem efeito de
participação"*. É o Edital 69/2026 da amostra — sorteia, publica o resultado, convoca e manda
comparecer, sem análise documental entre a ordem e a chamada.

**O que isso evita.** Um aviso que dispararia no Edital mais simples e mais comum da amostra seria
ruído, e ruído treina a pessoa a ignorar a família inteira.

**Consequência para o plano.** A condição é `not marco.get("cutRule")`, e o teste que prende a
distinção é obrigatório — não é caso de borda, é o caso de um Edital real.

---

## R-4 · O método do sorteio no documento: onde entra e de onde sai

**Decisão.** `publicacoes/infrastructure/pdf.py::_marcos` ganha os pares do método, resolvidos por
`editais/domain/marcos.metodo_que_governa(conteudo, perfil_id=…, marco_id=…)`.

**Rationale.** Três fatos que a leitura confirmou:

1. `_marcos(composicao, snapshot, perfil, nomear_perfil)` **já recebe o snapshot inteiro**, e o
   docstring explica por quê: as Etapas são do Edital, não do Perfil. O método comum do Edital mora
   na raiz do mesmo snapshot, então está ao alcance sem mudar assinatura.
2. `marcos.metodo_que_governa` é **o ponto único de resolução** desde a `030` — o marco que não
   declara método próprio referencia o comum, e `sorteios/domain/metodo` delega para lá. Reimplementar
   a resolução no renderizador criaria a segunda leitura que a `030` existe para não ter.
3. `marcos.marco_ordena_por_sorteio` responde a pergunta de `FR-468` (não imprimir combinação de
   pontuações) pelo mesmo caminho que `classificacao/application/emissao.py` já usa para recusar
   emitir por cálculo a ordem de um marco sorteado.

**Vocabulário.** O documento do **resultado** do sorteio já imprime `Algoritmo` e `Semente`
(`divulgacao/infrastructure/documento.py`). O documento do **Edital** imprime a norma, não o
resultado: ele publica o método **antes** do sorteio acontecer, e por isso imprime a ocorrência que
*fixará* a semente, e não a semente. Os rótulos saem de `CAMPOS_DO_METODO`, em
`editais/domain/perfis.py`, que é onde os sete campos já estão nomeados em português.

**Alternativa descartada.** Uma seção própria "Do sorteio" no documento. O método é **do marco** —
um Edital pode ter marcos que sorteiam e marcos que não —, e uma seção de raiz obrigaria a repetir
o endereçamento que a seção do marco já tem.

---

## R-5 · O que identifica "reserva sem via de apuração"

**Decisão.** Linha do quadro (`vacancyTable`) com `modalityId` não nulo, diferente do
`generalCompetitionModalityId` do Perfil e com `immediateVacancies` maior que zero, num Perfil cujo
marco **não** ordena por sorteio.

**Rationale.** `LINHA_DO_QUADRO_PUBLICADA` declara `modalityId` anulável — e o `NULL` **é** o recorte
da ampla concorrência, que é o que o ato computado emite. A Modalidade "AC" declarada é outra coisa,
e é a grafia-armadilha registrada no projeto: condicionar pela Modalidade declarada e não pelo
recorte `NULL` produziria falso positivo em todo Edital que nomeia a ampla.

**Onde.** Ao lado de `vacancy_reserved_list_without_row`, dentro de `_coerencia_do_quadro_de_vagas`.
Aquele aviso já diz, no tom certo, *"a ocupação e a convocação não terão quantidade a apurar nesse(s)
recorte(s)"* — o novo é o irmão dele para o caso em que **há** linha e o que falta é a ordem.

**Alternativa descartada.** Derivar da presença de `competitionModalities` com `reserveType` ≠
`NONE`. Declarar a Modalidade não é declarar vaga reservada; o que cria a expectativa de apuração
por recorte é a **linha do quadro com quantidade**.

---

## R-6 · As duas ações que sempre falham, e onde elas são desenhadas

**Decisão.** As duas condições entram em `interface/templates/interface/ocupacao.html`, e a razão
ocupa o lugar da ação — não um `disabled`, não um alerta depois do clique.

**Rationale.** O template já é condicional por estado: o botão "Apurar a ocupação deste recorte" sai
sob `{% if pode_emitir and recorte.estado != "NO_VACANCY_TABLE" %}` com
`recorte.estado == "NOT_APPRAISED"`, e "Pedir a faixa seguinte com este déficit" sob
`{% if pode_emitir and recorte.estado == "CURRENT" and recorte.faltando %}`. A máquina de estados do
recorte existe; o que falta é o estado que diz *"este recorte não tem ordem porque o marco emite em
lista única"* e a leitura de `cutRule` para a faixa.

**Por que não `disabled`.** O produto já pratica o oposto em três telas desde o PR #120 — *o bloqueio
anunciado antes da tentativa* —, e a auditoria registrou isso como padrão a preservar. Botão
desabilitado não diz por quê.

**Alternativa descartada.** Resolver só na aplicação, devolvendo erro melhor. A auditoria mediu o
custo disso: a mensagem *"Este recorte não tem ordem emitida: não há o que cortar"* nomeia o sintoma,
e quem a lê no dia da apuração não tem mais o que fazer com ela.

---

## R-7 · Por que `FR-469` é conferência, e não construção

**Decisão.** Nenhuma tarefa produz `FR-469`; ela é provada por teste sobre um Edital do acervo.

**Rationale.** O documento publicado é gerado no ato da publicação e guardado — é conhecimento já
registrado neste projeto, na forma da armadilha *"documento publicado não se regenera: mudou o
renderizador? re-semeie o banco para ver"*. Mudar `_marcos` não alcança documento algum que já
exista. O requisito está na spec para que a feature **prove** que não contrariou isso, e o risco real
que ele cobre é outro: um degrau de elevação acrescentado por engano reescreveria conteúdo do acervo.
A `030` passou por essa porta e não acrescentou degrau nenhum; esta também não deve.

---

## R-8 · O que esta feature **não** resolve, e por que isso está decidido

`ACH-47` sai nomeado, não resolvido. A correção de fundo é emitir ordem por lista em marco computado,
e `classificacao/application/emissao.py` a recusa por escrito: *"Um ato computado é sempre o de ampla
concorrência — só o sorteio emite por lista"*, com `lista_id=None`. É decisão de escopo deliberada,
tomada entre a `015` e a `021`.

A medição que sustentou a escolha de **aviso** em vez de impedimento está na amostra real
(`doc/avaliacao-de-capacidade-editais-2026-09-12.md`): **57/2026** (três listas, três atos raiz),
**28/2026** (7 polos × 3 modalidades) e **173/2025** (computado, "ordem por lista — decisão
declarada") têm essa forma. Para os três, a publicação é a única parte da jornada que hoje funciona.
