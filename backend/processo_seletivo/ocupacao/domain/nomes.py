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

# --- Espécies de movimento de vaga --------------------------------------------------------------
# **Os dois sentidos são opostos, e trocá-los mantém a soma certa com o recorte errado** — o
# defeito que só asserção de recorte pega. A reversão move quantidade da cota para a linha geral; a
# liberação devolve ao recorte reservado a vaga de quem ocupou pela ampla (016, FR-253).
MOVIMENTO_REVERSAO = "REVERSAO_DE_COTA"
MOVIMENTO_LIBERACAO = "LIBERACAO_POR_CONCOMITANCIA"
ESPECIES_DE_MOVIMENTO = (MOVIMENTO_REVERSAO, MOVIMENTO_LIBERACAO)

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
