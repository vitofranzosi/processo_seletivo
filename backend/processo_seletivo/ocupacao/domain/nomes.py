"""O vocabulário da ocupação e os códigos de recusa, ditos uma vez.

**Por que este módulo existe separado.** O mesmo código de recusa aparece na aplicação, na
interface e no teste que o prende; escrevê-lo três vezes é como um deles fica para trás numa
renomeação. É a forma que `classificacao/domain/nomes.py` já usa.

**O vocabulário é verificado por varredura** (`016`, `UX-034`): termo de convocação, aceite ou
matrícula não pode aparecer em tela, ato ou mensagem desta feature, porque esses fatos não existem
antes da `019`. Os nomes abaixo são o que sobra depois dessa proibição.
"""

# --- Espécies de gatilho da reversão (016, D-007) -----------------------------------------------
# Os dois Editais da amostra escrevem a reversão de modo diferente: o 28/2026 (4.3) reverte
# "havendo ausência de candidatos aprovados", e o 57/2026 (4.3) "na hipótese do não preenchimento
# total". São gatilhos distintos, e o Edital declara qual usa — inferir seria decidir no código uma
# divergência de norma.
REVERSAO_POR_ESGOTAMENTO = "ON_EXHAUSTION"
REVERSAO_POR_SALDO = "ON_BALANCE"
ESPECIES_DE_REVERSAO = (REVERSAO_POR_ESGOTAMENTO, REVERSAO_POR_SALDO)

# --- Espécie de movimento de vaga ---------------------------------------------------------------
# **Uma só, e a ausência da segunda é o achado.** A reversão move quantidade da cota para a linha
# geral. A concorrência concomitante do item 8.9 do 28/2026 **não** é movimento: ela não transfere
# quantidade nenhuma — o autodeclarado que ocupa pela ampla simplesmente não é computado no
# preenchimento da reservada, que continua com as vagas que publicou. Modelá-la como transferência
# produzia 1 e 2 efetivas onde o Edital manda 2 e 1, e o erro era de leitura, não de conta.
#
# A exclusão mora no cálculo, em `apuracao.apurar`, e não aqui (016, FR-252).
MOVIMENTO_REVERSAO = "REVERSAO_DE_COTA"
ESPECIES_DE_MOVIMENTO = (MOVIMENTO_REVERSAO,)

# --- Estado de um recorte na leitura (016, contrato) --------------------------------------------
# **Quatro valores, e dois deles não são erro.** `NAO_APURADO` é recorte sem apuração emitida;
# `SEM_QUADRO` é Edital publicado antes do degrau 12, que não tem quadro. Colapsar os dois em
# "0 vagas" é exatamente o que a `UX-032` proíbe.
VIGENTE = "CURRENT"
OBSOLETO = "OBSOLETE"
NAO_APURADO = "NOT_APPRAISED"
SEM_QUADRO = "NO_VACANCY_TABLE"

# --- Recusas da emissão -------------------------------------------------------------------------
ORDEM_NAO_VIGENTE = "ordem_nao_vigente"
SEM_QUADRO_PUBLICADO = "sem_quadro_publicado"
RECORTE_SEM_LINHA = "recorte_sem_linha"
MOTIVO_DA_SUCESSAO_OBRIGATORIO = "motivo_da_sucessao_obrigatorio"
DEFICIT_ZERO = "deficit_zero"
APURACAO_OBSOLETA = "apuracao_obsoleta"

# --- Causas de obsolescência (016, FR-263) ------------------------------------------------------
# **Quatro, e a quarta é o que dispensa orquestração.** Movimento posterior à apuração vigente
# torna o recorte obsoleto, e quem quiser o número novo emite — em vez de a reversão ter de
# disparar, em cascata, a emissão do destino.
CAUSA_ORDEM_SUCEDIDA = "ordem_sucedida"
CAUSA_CORTE_OBSOLETO = "corte_obsoleto"
CAUSA_QUADRO_RETIFICADO = "quadro_retificado"
CAUSA_MOVIMENTO_POSTERIOR = "movimento_posterior"
# **A quinta, e ela chegou com a `019`.** Desfecho de convocação muda o conjunto de ocupantes do
# recorte, e nenhuma apuração é reescrita por causa disso: a apuração vigente passa a aparecer
# obsoleta, com a causa dita, e o número novo sai na emissão seguinte (`D-006`). É o mesmo desenho
# da quarta — obsolescência em vez de orquestração.
CAUSA_EFEITO_POSTERIOR = "efeito_posterior"

# --- Espécies de efeito de ocupação (019, R-003) ------------------------------------------------
# **A porta por onde a `019` mexe na contagem, e ela mora aqui porque a tabela mora aqui.** A `016`
# não sabe o que é convocação: sabe que uma inscrição foi excluída do conjunto de ocupantes ou
# incluída nele, com fundamento e proveniência. Quem dá sentido ao fundamento é quem o escreveu.
#
# **Duas, e a segunda é o que impede o número de só descer.** Sem a inclusão, quatro dos sete
# desfechos da `019` reduzem a contagem e nenhum a recompõe — a suplente que aceita nunca entraria.
EFEITO_EXCLUSAO = "EXCLUSAO"
EFEITO_INCLUSAO = "INCLUSAO"
ESPECIES_DE_EFEITO = (EFEITO_EXCLUSAO, EFEITO_INCLUSAO)

# --- Recusa da determinação de titulares (019, R-002) -------------------------------------------
# A `014` trata o empate na última posição **da faixa** (`alvo + excedente`), e o Edital declara
# `tieOutcome` para ela. Titular inicial é contado até o **alvo**, que é outra fronteira, e para
# essa a norma publicada não diz nada. Incluir todos os empatados faria `ocupadas > efetivas` e a
# constraint recusaria o ato; escolher por ordem de chegada inventaria desempate. Recusar é o que a
# `014` já faz quando o Edital publicou alvo estrito e o empate cruza a faixa.
EMPATE_NA_FRONTEIRA_DO_ALVO = "empate_na_fronteira_do_alvo"

# --- Recusas da porta de efeitos (019, R-003) ---------------------------------------------------
# Aqui, e não como literal em `application/efeitos.py`, pela razão que o topo deste módulo escreve:
# o mesmo código aparece na aplicação, na tela e no teste que o prende, e escrevê-lo três vezes é
# como um deles fica para trás numa renomeação.
ESPECIE_DE_EFEITO_INVALIDA = "especie_de_efeito_invalida"
FUNDAMENTO_OBRIGATORIO = "fundamento_obrigatorio"
PROVENIENCIA_OBRIGATORIA = "proveniencia_obrigatoria"
