"""O vocabulário dos avisos: origens, motivos, elegibilidades, resultados, estados e recusas (066).

**Num lugar só, e lido pelos modelos, pelo domínio e pelas telas.** As constraints do banco citam
estes valores; uma grafia diferente numa ponta faria o `CHECK` recusar o que a aplicação acha certo,
e o erro apareceria como `IntegrityError` longe da causa.
"""

# --- A origem: de que ato o aviso parte (FR-1241) -------------------------------------------------

RESULTADO = "RESULTADO"
CHAMADA = "CHAMADA"
ORIGENS = (RESULTADO, CHAMADA)

# --- O motivo: primeiro aviso, ou reenvio (R-011) -------------------------------------------------

PRIMEIRO_AVISO = "PRIMEIRO_AVISO"
# Terminar de entregar o que foi confirmado: falha definitiva e expirada sem envio. A mensagem não
# saiu, e por isso não há o que justificar; o texto é o do aviso anterior.
REENVIO_DE_FALHAS = "REENVIO_DE_FALHAS"
# Mandar de novo o que pode ter saído (indeterminada), o que alguém decidiu parar (interrompido), ou
# a publicação inteira já avisada. Exige justificativa, e o texto pode mudar.
REENVIO_JUSTIFICADO = "REENVIO_JUSTIFICADO"
MOTIVOS = (PRIMEIRO_AVISO, REENVIO_DE_FALHAS, REENVIO_JUSTIFICADO)

# --- Natureza do resultado citado ----------------------------------------------------------------

PRELIMINAR = "PRELIMINAR"
DEFINITIVA = "DEFINITIVA"
NATUREZAS = (PRELIMINAR, DEFINITIVA)

# --- A elegibilidade de cada destinatário do universo (D-003) -------------------------------------

ELEGIVEL = "ELEGIVEL"
NAO_ELEGIVEL_DESFECHO = "NAO_ELEGIVEL_DESFECHO"
NAO_ELEGIVEL_SUCEDIDA = "NAO_ELEGIVEL_SUCEDIDA"
NAO_ELEGIVEL_VENCIDA = "NAO_ELEGIVEL_VENCIDA"
ELEGIBILIDADES = (ELEGIVEL, NAO_ELEGIVEL_DESFECHO, NAO_ELEGIVEL_SUCEDIDA, NAO_ELEGIVEL_VENCIDA)

MOTIVO_DA_INELEGIBILIDADE = {
    NAO_ELEGIVEL_DESFECHO: "desfecho registrado",
    NAO_ELEGIVEL_SUCEDIDA: "convocação sucedida",
    NAO_ELEGIVEL_VENCIDA: "vencimento decorrido",
}

# --- O resultado de uma tentativa (R-004) --------------------------------------------------------

ACEITA = "ACEITA"
FALHA_TEMPORARIA = "FALHA_TEMPORARIA"
FALHA_DEFINITIVA = "FALHA_DEFINITIVA"
INDETERMINADA = "INDETERMINADA"
RESULTADOS = (ACEITA, FALHA_TEMPORARIA, FALHA_DEFINITIVA, INDETERMINADA)

# --- O estado derivado do destinatário (data-model §2) — nunca coluna ----------------------------

NAO_ELEGIVEL = "NAO_ELEGIVEL"
SEM_ENDERECO = "SEM_ENDERECO"
INTERROMPIDO_ANTES_DO_ENVIO = "INTERROMPIDO_ANTES_DO_ENVIO"
EXPIRADA_SEM_ENVIO = "EXPIRADA_SEM_ENVIO"
PENDENTE = "PENDENTE"
EM_ENVIO = "EM_ENVIO"
ESTADO_ACEITA = "ACEITA"
ESTADO_FALHA_TEMPORARIA = "FALHA_TEMPORARIA"
ESTADO_FALHA_DEFINITIVA = "FALHA_DEFINITIVA"
ESTADO_INDETERMINADA = "INDETERMINADA"

# **"Aceita pelo servidor de correio", e nunca "entregue", "recebida" ou "lida"** (`UX-172`). O
# sistema sabe o que o servidor respondeu; o que aconteceu na caixa de entrada ele não sabe.
ROTULO_DO_ESTADO = {
    NAO_ELEGIVEL: "não elegível para o aviso",
    SEM_ENDERECO: "sem endereço",
    INTERROMPIDO_ANTES_DO_ENVIO: "interrompido antes do envio",
    EXPIRADA_SEM_ENVIO: "expirado sem envio",
    PENDENTE: "pendente",
    EM_ENVIO: "em envio",
    ESTADO_ACEITA: "aceita pelo servidor de correio",
    ESTADO_FALHA_TEMPORARIA: "falha temporária",
    ESTADO_FALHA_DEFINITIVA: "falha",
    ESTADO_INDETERMINADA: "resultado indeterminado",
}

# Os estados que o reenvio alcança, por motivo (`FR-1264`, `R-011`).
ALCANCE_DO_REENVIO = {
    REENVIO_DE_FALHAS: (ESTADO_FALHA_DEFINITIVA, EXPIRADA_SEM_ENVIO),
    REENVIO_JUSTIFICADO: (ESTADO_INDETERMINADA, INTERROMPIDO_ANTES_DO_ENVIO),
}

# --- Recusas (contracts/telas.md) ----------------------------------------------------------------

AVISO_SEM_ATO = "aviso_sem_ato"
AVISO_SEM_PUBLICACAO_NOVA = "aviso_sem_publicacao_nova"
AVISO_JUSTIFICATIVA_OBRIGATORIA = "aviso_justificativa_obrigatoria"
AVISO_SEM_ELEGIVEL = "aviso_sem_elegivel"
AVISO_PREVIA_DEFASADA = "aviso_previa_defasada"
AVISO_VARIAVEL_DESCONHECIDA = "aviso_variavel_desconhecida"
AVISO_VARIAVEL_SEM_VALOR = "aviso_variavel_sem_valor"
AVISO_CHAMADA_POR_MENSAGEM_INDIVIDUAL = "aviso_chamada_por_mensagem_individual"
AVISO_PROCESSO_EM_ESTADO_FINAL = "aviso_processo_em_estado_final"
AVISO_CONCLUIDO = "aviso_concluido"
AVISO_FALHAS_JA_REENVIADAS = "aviso_falhas_ja_reenviadas"
AVISO_ENVIO_DESABILITADO = "aviso_envio_desabilitado"
AVISO_TEXTO_INVALIDO = "aviso_texto_invalido"
AVISO_NAO_ENCONTRADO = "aviso_nao_encontrado"
MODELO_NAO_ENCONTRADO = "modelo_de_aviso_nao_encontrado"
MODELO_COM_NOME_REPETIDO = "modelo_de_aviso_com_nome_repetido"

# --- Operações na trilha -------------------------------------------------------------------------

OPERACAO_CONFIRMAR = "AVISO_CONFIRMAR"
OPERACAO_INTERROMPER = "AVISO_INTERROMPER"
OPERACAO_MODELO = "AVISO_MODELO"
ATO_CONFIRMAR = "aviso:confirmar"
ATO_INTERROMPER = "aviso:interromper"

PERMISSAO = "aviso:enviar"

# --- Limites do texto (FR-1254) ------------------------------------------------------------------

ASSUNTO_MAXIMO = 150
CORPO_MAXIMO = 5000
NOME_DO_MODELO_MAXIMO = 120
