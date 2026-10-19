# Research: Prévia interativa da classificação — fatia 1

Questões técnicas da implementação. As decisões de produto estão na [spec](spec.md), em D-001 a
D-011; aqui ficam as questões técnicas, em `R-`, e a conferência de código que as sustenta. Tudo
conferido em 19/10/2026 contra a `main` em `745f115f`.

## R-001 — A extração de `calcular_ordem` é o caminho certo

**Pergunta**: a decisão 7 do usuário manda extrair a preparação do universo para uma função pura que o
caminho oficial e a prévia chamem. É o caminho certo, ou a prévia deveria chamar `combinar` e `ordenar`
direto?

**Conferido**: `classificacao/application/calculo.py`, `calcular_ordem`, tem 294 linhas no arquivo e
duas metades separáveis:

| Metade | O que faz | Toca banco? |
|---|---|---|
| Consulta | `effective_version`; `normalizar_recorte`; `Inscricao` filtrada por Edital, Perfil, `SUBMETIDA` e recorte; `restringir_a_participantes`; `ResultadoEtapa.vigentes` com o `order_by` que decide o colapso; `conteudos_das_versoes` e `_conferir_ancoras_dos_resultados`; `ValorDeFato` dos fatos consumidos | Sim |
| Decisão | por inscrição: pontuações por Etapa; `_eliminacao_mais_recente` → sem posição com consequência e motivo; `combinar` → `SEM_PONTUACAO` → sem posição com `_motivo_da_pontuacao_ausente`; senão classificável com `HABILITADA`; depois `ordenar(classificaveis, tiebreakers)` | Não — só dicionários |

A segunda metade depende de `ResultadoEtapa.Consequencia` só por duas constantes de texto
(`"ELIMINADA"`, `"HABILITADA"`), que o modelo declara como `TextChoices`.

**Decisão**: extrair a segunda metade para `classificacao/domain/universo_classificavel.py`,
`preparar(marco, etapas, inscritos, *, recorte=None) -> (classificaveis, sem_posicao)`. As duas
constantes passam a ser declaradas no próprio módulo puro (`ELIMINADA`, `HABILITADA`) — o
`classificacao/domain/nomes.py` que existe é de nomes do marco para exibição, e não de vocabulário —, e
um teste prende `ELIMINADA == ResultadoEtapa.Consequencia.ELIMINADA` e o mesmo para `HABILITADA`.

**Alternativa descartada**: a prévia montar classificáveis por conta própria. Seriam duas montagens, e a
primeira exclusão nova (por exemplo, um estado de inscrição) entraria numa e não na outra — que é o que
a equivalência existe para impedir. Ver D-004.

## R-002 — O que fica na consulta, e o recorte como parâmetro

**Decisão**: o filtro do recorte **continua** na consulta de `calcular_ordem` — o orçamento de consulta
é verificado por teste (`tests/performance/test_ordenacao.py`), e filtrar em memória leria o Perfil
inteiro por recorte. A função pura recebe `recorte` e o reaplica sobre `modalidade_id` de cada inscrito;
no caminho oficial isso é idempotente (todos já são do recorte), e um teste prova que a saída é igual
com e sem o reaplicar.

**Por que o parâmetro agora, se a fatia 1 não usa recorte**: é a porta da fatia 2 (D-008). A ampla é
`recorte=None`, o universo inteiro; a reservada filtra pela Modalidade. Acrescentar o parâmetro depois
seria mudar a assinatura de uma função que o caminho oficial já chama.

**`restringir_a_participantes` fica fora da função pura**: é consulta sobre a progressão real (quem foi
eliminado antes da Etapa do marco não entra). A prévia supõe todos participantes (spec, Assumptions).

## R-003 — A irmã de `ordenar` que devolve a trajetória

**Pergunta**: a frase "o 1º critério não separou, o 2º separou" precisa saber quais critérios foram
oferecidos ao grupo de cada candidato e o que fizeram. `ordenar` devolve só `separado_por`, o último.

**Decisão**: `desempate.ordenar_com_trajetoria(participantes, criterios)` devolve a mesma lista de
`ordenar` com a chave `trajetoria` — a sequência de `(passo, criterio, grupo)`, onde `passo` é
`"separou"` ou `"nao_separou"` — e `grupo_da_pontuacao`. `ordenar` passa a ser
`[sem_trajetoria(item) for item in ordenar_com_trajetoria(...)]`. O protótipo implementou a irmã fora
do módulo e a conferiu contra `ordenar` em todos os cenários: idêntica (posição, empate residual e
`separado_por`).

**Por que não acrescentar a chave em `ordenar` direto**: a saída de `ordenar` atravessa `calcular_ordem`
e chega à emissão do ato; uma chave nova com objetos de critério e listas de participantes viajaria
até onde ninguém a espera, e o universo do ato é comparado por hash.

## R-004 — O fragmento, o alvo do troco e o recálculo

**Decisão**: rota `fragmentos/perfil/<indice>/marco/<sub>/previa`, GET, irmã de
`fragmento-marco-recomposto`. O botão no cartão faz `hx-get` com `hx-include="closest fieldset"` — o
cartão do marco, o mesmo que a recomposição inclui — e `hx-target="#painel-da-previa"`. O painel traz um
contêiner com `hx-trigger="change from:#marco-<indice>-<sub>, input changed delay:400ms from:#marco-<indice>-<sub>"`
e o mesmo `hx-include`, mais o cenário e as fronteiras do painel.

**Por que o alvo é o painel, e não o cartão**: trocar o cartão a cada tecla perderia o foco do campo e o
que está no meio da digitação. A recomposição troca o cartão porque muda quais campos existem; a prévia
não muda campo nenhum.

**Por que `change` de todo o cartão**: a lista de campos que a prévia lê é a do marco inteiro; enumerar
campos no gatilho seria uma segunda lista para envelhecer. O protótipo validou o gatilho com
`from:#composicao`.

**Conteúdo incompleto**: diferente da recomposição, que responde 204, a prévia responde 200 com o que
falta (FR-2227): o painel está aberto e precisa dizer por que não calcula.

## R-005 — A geração dos cenários

**Decisão**: `cenarios_da_previa.gerar(chave, *, etapas_com_nota, portas, etapa_do_marco, fatos, alvo,
suplentes, vagas, corta)`, puro e determinístico. Regras validadas no protótipo:

- **Tamanho**: `min(max(alvo + suplentes, vagas, alvo, 8) + 4, 600)`.
- **Notas**: cada candidato tem **a mesma nota em toda Etapa com nota**, de 95 para baixo, inteiras até
  90 candidatos e com duas casas acima disso. Nota igual em todas as Etapas torna a ordem por pontuação
  independente dos pesos e da operação — a ordem entre os sem-empate não muda quando o elaborador mexe
  no peso, que é o que D-003 pede.
- **Fatos**: data de nascimento e inteiro distintos por candidato; o cenário os iguala ou remove onde
  precisa.
- **Âncoras**: empate de dois iguais em tudo na última posição da faixa (`empate_na_faixa`) ou das
  vagas (`empate_nas_vagas`); trio com notas iguais e fatos diferentes na posição `alvo − 1`
  (`criterios_sucessivos`); ausências na 2ª, 4ª e 7ª linhas (`valor_ausente`).

**Por que o trio difere só nos fatos**: um trio com notas diferentes empatado na soma só empata com um
conjunto de pesos — dependeria do peso, contrariando D-003. Com notas iguais, o critério por Etapa não
separa (e a linha diz por quê), e os critérios por fato separam em sequência. A primeira versão do
protótipo usava notas trocadas; foi descartada pela dependência do peso.

## R-006 — Limites

- **Até quatro Etapas com nota** enumeradas (spec, Assumptions). Acima, o painel diz que não cobre.
- **600 candidatos fictícios** no máximo: cobre faixa de 500 com folga para as âncoras (SC-841).
- **A tabela agrupa trechos sem nada a dizer** (FR-2228): mostra por inteiro as três primeiras, as duas
  últimas, as que estão a até duas posições de cada fronteira, as que empataram na pontuação e as sem
  posição; o resto vira uma linha "posições a a b". O agrupamento nunca junta linhas de situações
  diferentes.

## R-007 — A fronteira das vagas, na prévia

**Decisão**: depois do corte, `apuracao.titulares_iniciais(progrediram_em_ordem=…, efetivas=vagas,
empates_residuais={id: posição dos empatados})`, sem `habilitadas` (todos supostos habilitados, D-006).
`EmpateNaFronteiraDoAlvo` vira o aviso. Corte recusado → não avaliado, e o painel diz por quê. Marco sem
corte → a sequência é a ordem inteira, como `progrediram_em_ordem` faz no produto quando não há corte.

**Vagas**: linha geral do quadro do Perfil no rascunho gravado (`linha_do_quadro(conteudo, perfil_id,
lista_id=None)`, que já resolve o caso da Modalidade declarada como ampla). Sem linha → não avaliado.

**Reprodução do achado** (protótipo, motor oficial, 19/10):

| Configuração | `ADMITS_SURPLUS` | `STRICT` |
|---|---|---|
| 10 + 5, empate de dois na 10ª, 10 vagas | corte com 15, nenhum por empate; apuração **para** na 10 | idem |
| 10 + 5, empate de dois na 15ª | corte com 16, um por empate; apuração segue | corte **recusado** na 15 |
| 10 + 0, empate de dois na 10ª, 10 vagas | corte com 11, um por empate; apuração **para** na 10 | corte **recusado** na 10 |

É a tabela do achado, linha a linha.

## R-008 — CSP, foco e anúncio

- **Sem inline**: o painel abre por troca htmx; a coluna lateral acende por `:has(#painel-da-previa:not(:empty))`
  na folha da tela, sem script. O htmx usa a configuração do `base.html` (`includeIndicatorStyles:false`,
  `allowEval:false`).
- **Foco**: um script estático (`previa-da-classificacao.js`) escuta `htmx:afterSwap` — leva o foco ao
  título quando quem pediu foi o botão, e de volta ao botão quando o painel esvazia. No recálculo o foco
  fica no campo. Validado no protótipo.
- **Anúncio**: um `role="status"` **fora** do painel, atualizado por `hx-swap-oob`, com uma frase de
  resumo; o painel inteiro não é região viva, para não reler a tabela a cada tecla (FR-2236).
- **375 px**: abaixo de 64rem (a fronteira da gestão) o painel é `position:fixed; inset:0`, com a cabeça
  fixa no topo; abaixo de 40rem a tabela vira blocos com o rótulo da coluna em `::before`. Medido no
  protótipo: `scrollWidth == clientWidth` na página e no painel.

## R-009 — O protótipo e o que ele prova

`prototipo/` roda num servidor da biblioteca padrão (`.claude/launch.json`, entrada `previa-094`,
porta 8094), com a CSP da gestão no cabeçalho. Ele **prova**: que os núcleos puros importam e rodam sem
Django; que o recálculo por htmx sem regra no navegador funciona sob a CSP; que a trajetória reconstruída
bate com `ordenar`; que a matriz do achado sai igual; que o painel cabe em 375 px. Ele **não prova**: a
leitura por `marco_do_formulario` (lê com um leitor próprio, com os mesmos nomes de campo), a
autorização, a extração dentro de `calcular_ordem` (a função extraída é um esboço fora dele), nem o
orçamento de consulta.

**Defeitos que o protótipo pegou e que a implementação não pode repetir**:

1. **Marcar um empatado como suplente e o outro como excedente**: `faixa.calcular` devolve em
   `excedentes` quem ficou além da contagem, e quem é depende da ordem de entrada. A marca precisa ser do
   grupo (FR-2212).
2. **Parâmetro duplicado**: um `cenario` oculto no formulário vencia o do painel no `hx-include`. O
   painel é a única fonte do cenário.
3. **"E não a do alvo" sem suplentes**: com alvo igual à faixa, a frase afirmava uma diferença que não
   existe.
