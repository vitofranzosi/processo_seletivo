"""O vocabulário do Requerimento de Matrícula e os códigos de recusa, ditos uma vez.

**Por que este módulo existe separado.** O mesmo código de recusa aparece na aplicação, na interface
e no teste que o prende; escrevê-lo três vezes é como um deles fica para trás numa renomeação. É a
forma que `convocacao/domain/nomes.py` e `ocupacao/domain/nomes.py` já usam.

**As listas fechadas moram aqui, e não no modelo**, para que o domínio possa validá-las sem importar
Django — e para que a migration possa **copiar** os valores em vez de importá-los: migration que
importa domínio faz uma alteração futura mudar retroativamente o efeito de uma migration já
executada, e a suíte recusa (`tests/migrations/test_migrations.py`).
"""

# --- Estados persistidos (029, §12) -------------------------------------------------------------
# **Dois, e só dois.** *Não aplicável*, *ainda indisponível* e *disponível* são derivados da
# ausência de linha vigente lida contra a declaração do Edital — é como a ocupação e a convocação
# já derivam vigência, e coluna para eles exigiria manter estado que ninguém escreve.
RASCUNHO = "RASCUNHO"
ENVIADO = "ENVIADO"
ESTADOS = (RASCUNHO, ENVIADO)

# --- Momento da coleta, declarado pelo Edital (`FR-368`) ----------------------------------------
# **Dois valores declaráveis.** *Não exigido* **não** é um terceiro valor: é a ausência de
# declaração — `""` na coluna, `null` no conteúdo publicado. Duas grafias do mesmo fato seriam a
# contradição que a regra evita.
NA_INSCRICAO = "AT_ENROLLMENT"
NA_CONVOCACAO = "AT_CALL"
MOMENTOS = (NA_INSCRICAO, NA_CONVOCACAO)

# --- Cor ou raça (`FR-383`) ---------------------------------------------------------------------
# **Cinco categorias do IBGE mais "não declarada" — seis valores.** `INDIGENA` está aqui **apesar**
# de o formato do Registro Acadêmico não a comportar hoje: a ausência lá é achado a levar a quem
# define o formato, e nunca categoria a suprimir na coleta. Suprimir seria fazer o defeito do
# destino virar defeito da origem.
BRANCA = "BRANCA"
PRETA = "PRETA"
PARDA = "PARDA"
AMARELA = "AMARELA"
INDIGENA = "INDIGENA"
COR_NAO_DECLARADA = "NAO_DECLARADA"
CORES = (BRANCA, PRETA, PARDA, AMARELA, INDIGENA, COR_NAO_DECLARADA)

# --- Sexo ---------------------------------------------------------------------------------------
# Dois valores porque é o que o formato de destino admite. **Não é identidade de gênero**, e nome
# social não é coletado aqui — a `Q-8` decidiu que os dois são spec própria, com alcance que
# atravessa comprovante, relação de habilitados, resultado e convocação.
FEMININO = "F"
MASCULINO = "M"
SEXOS = (FEMININO, MASCULINO)

# --- Estado civil -------------------------------------------------------------------------------
# A flexão que o destino exige — "Casada" ou "Casado" — é **derivada** na composição da saída, a
# partir deste valor e do sexo. Guardar as duas formas seria guardar o derivável.
SOLTEIRO = "SOLTEIRO"
CASADO = "CASADO"
DIVORCIADO = "DIVORCIADO"
VIUVO = "VIUVO"
ESTADOS_CIVIS = (SOLTEIRO, CASADO, DIVORCIADO, VIUVO)

# --- Faixa de renda familiar (`FR-412`) ---------------------------------------------------------
# **As sete faixas do formulário institucional, e elas medem a SOMA DA FAMÍLIA.** A coluna de
# destino — `RENDA_PER_CAPITA_PNP` — significa o valor **por pessoa**, e a divergência é conhecida,
# decidida em 16/09/2026 e registrada no contrato de saída (`R-7`). Não há conversão a fazer aqui:
# dividir uma faixa por um número não produz uma faixa.
#
# O rótulo de tela precisa dizer por extenso o que a faixa mede, ou a divergência se propaga por
# ambiguidade de redação.
ATE_MEIO = "ATE_0_5"
DE_MEIO_A_UM = "DE_0_5_A_1"
DE_UM_A_UM_E_MEIO = "DE_1_A_1_5"
DE_UM_E_MEIO_A_DOIS_E_MEIO = "DE_1_5_A_2_5"
DE_DOIS_E_MEIO_A_TRES_E_MEIO = "DE_2_5_A_3_5"
ACIMA_DE_TRES_E_MEIO = "ACIMA_DE_3_5"
RENDA_NAO_DECLARADA = "NAO_DECLARADA"
FAIXAS_DE_RENDA = (
    ATE_MEIO,
    DE_MEIO_A_UM,
    DE_UM_A_UM_E_MEIO,
    DE_UM_E_MEIO_A_DOIS_E_MEIO,
    DE_DOIS_E_MEIO_A_TRES_E_MEIO,
    ACIMA_DE_TRES_E_MEIO,
    RENDA_NAO_DECLARADA,
)

# --- Recusas de runtime (contrato §2.2) ---------------------------------------------------------
# **Seis, e nem uma a mais.** `field_required` e `field_constraint_violated` já existem no projeto e
# não se redeclaram aqui. `matriculation_request_without_declaration` **não** é recusa de runtime:
# é achado de publicação, e mora na conferência de conteúdo (contrato §1.2).
# **Reaproveitado, e não inventado.** `inscricoes/application/submissao.py` já recusa com este
# código exatamente o mesmo fato — o Edital mudou entre a leitura e a confirmação —, e um segundo
# nome para ele obrigaria a tela a tratar duas palavras como sinônimas. Uma redação anterior dizia
# `stale_version`, que não existe em lugar nenhum deste projeto.
EDITAL_ATUALIZADO = "edital_updated"
# A recusa da **submissão da inscrição** quando o Edital coleta na inscrição e o requerimento não
# foi enviado. Mora aqui, com as outras, para que o código seja escrito uma vez só — mas quem a
# levanta é `inscricoes`, e é por isso que ela não entra em `RECUSAS`, que são as das rotas desta
# feature.
REQUERIMENTO_EXIGIDO = "matriculation_request_required"
NAO_EXIGIDO = "matriculation_request_not_required"
INDISPONIVEL = "matriculation_request_unavailable"
ENCERRADO = "matriculation_request_closed"
JA_ENVIADO = "matriculation_request_already_sent"
SUCESSOR_NAO_AUTORIZADO = "successor_not_authorized"
DECLARACAO_NAO_ACEITA = "declaration_not_accepted"
RECUSAS = (
    NAO_EXIGIDO,
    INDISPONIVEL,
    ENCERRADO,
    JA_ENVIADO,
    SUCESSOR_NAO_AUTORIZADO,
    DECLARACAO_NAO_ACEITA,
)

# --- Estados de leitura, para a tela (`FR-405`) --------------------------------------------------
# Cinco, e os três primeiros **não** são coluna. A tela precisa distinguir *"este certame não pede
# requerimento"* de *"ainda não chegou a sua vez"*: colapsá-los diria a quem ainda tem chance que
# ela não tem — a mesma distinção que a tela de convocação já é obrigada a fazer.
NAO_APLICAVEL = "NOT_APPLICABLE"
AINDA_INDISPONIVEL = "NOT_YET_AVAILABLE"
DISPONIVEL = "AVAILABLE"
EM_PREENCHIMENTO = "IN_PROGRESS"
ESTADO_ENVIADO = "SENT"
ESTADOS_DE_LEITURA = (
    NAO_APLICAVEL,
    AINDA_INDISPONIVEL,
    DISPONIVEL,
    EM_PREENCHIMENTO,
    ESTADO_ENVIADO,
)

# --- A operação, para a trilha ------------------------------------------------------------------
# **Duas, e as duas têm rótulo em `interface/views.py::OPERACOES`** — conferido por asserção em
# `tests/integration/requerimentos/test_auditoria.py`.
#
# **A varredura global não alcança estas linhas, e o achado fica registrado aqui.**
# `test_trilha_legivel` coleta todo literal `operation="…"` passado a `record_event`; estes chegam
# como **constante**, e o `ast.Constant` daquela varredura não os vê. Ela não é falha desta feature
# e não vira escopo dela — mas quem confiar nela para garantir rótulo vai confiar em silêncio.
#
# **O nome segue a forma do resto do mapa** — `APP_ATO`, em maiúsculas, como `CONVOCACAO_CONVOCAR` e
# `OCUPACAO_APURAR`. A redação anterior usava `enviar_requerimento_de_matricula`, que é o nome da
# função, e deixaria a trilha falando duas línguas na mesma coluna.
OPERACAO_ENVIO = "REQUERIMENTO_ENVIAR"
OPERACAO_SUCESSAO = "REQUERIMENTO_SUCEDER"

# --- Unidades da Federação ----------------------------------------------------------------------
# **As 27, e a lista mora aqui porque a UF é campo de lista fechada como os demais.** Texto livre
# admitiria "ES", "Es", "Espírito Santo" e "espirito santo" na mesma coluna, e a `FR-387` — uma
# forma só, guardada uma vez — vale para a UF pela mesma razão que vale para o CEP.
#
# **Cuidado com a sigla `AC`**: neste repositório ela já significa *Ampla Concorrência* em outro
# vocabulário, e `editais/domain/validation.py` registra a armadilha. Aqui ela é o Acre, e os dois
# sentidos nunca se encontram — mas quem for pesquisar por `"AC"` vai achar os dois.
UFS = (
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
)
