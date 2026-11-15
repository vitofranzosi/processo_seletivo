"""O vocabulário da agenda da Etapa (167): formas, origens e os códigos de recusa.

**Os códigos são o contrato** (research T-008): os testes e as telas os conhecem pelo nome, e as
frases que eles carregam estão em `recusas.py`, transcritas de `contracts/recusas.md`. Mudar um
código aqui é mudar o contrato, e não arrumação.
"""

# A forma de atendimento (FR-7202). "Remota" é a videoconferência; o acesso da banca é então o
# endereço da sala, e nunca entra no que é público (FR-7226).
REMOTA = "REMOTA"
PRESENCIAL = "PRESENCIAL"
FORMAS = (REMOTA, PRESENCIAL)

# Quem pôs a pessoa no horário (FR-7216): a comissão, à mão, ou o preenchimento automático.
MANUAL = "MANUAL"
AUTOMATICA = "AUTOMATICA"
ORIGENS = (MANUAL, AUTOMATICA)

# As operações da trilha (FR-7256, T-019), e como a tela da trilha as nomeia.
CONFIGURACAO_SALVA = "agenda.configuracao_salva"
AGENDAMENTO = "agenda.agendamento"
PREENCHIMENTO_APLICADO = "agenda.preenchimento_aplicado"
ROTULOS_DA_TRILHA = {
    CONFIGURACAO_SALVA: "Configuração da agenda da Etapa salva",
    AGENDAMENTO: "Agendamento à mão na agenda da Etapa",
    PREENCHIMENTO_APLICADO: "Preenchimento automático da agenda da Etapa aplicado",
}

# --- §1 de `contracts/recusas.md`: a configuração ----------------------------------------------
DURACAO_NAO_POSITIVA = "duracao_nao_positiva"
INTERVALO_NEGATIVO = "intervalo_negativo"
SEM_DIA = "sem_dia"
SEM_BANCA = "sem_banca"
DIA_FORA_DO_PERIODO = "dia_fora_do_periodo"
JANELA_INVERTIDA = "janela_invertida"
JANELA_MENOR_QUE_A_DURACAO = "janela_menor_que_a_duracao"
JANELAS_SOBREPOSTAS = "janelas_sobrepostas"
BANCA_SEM_NOME = "banca_sem_nome"
BANCAS_COM_O_MESMO_NOME = "bancas_com_o_mesmo_nome"
DIA_REPETIDO = "dia_repetido"

# A configuração inteira recusada, com a lista dos problemas acima.
CONFIGURACAO_RECUSADA = "configuracao_recusada"

# --- §3: a montagem -------------------------------------------------------------------------------
HORARIO_OCUPADO = "horario_ocupado"
PESSOA_JA_AGENDADA = "pessoa_ja_agendada"
PESSOA_NAO_PARTICIPA = "pessoa_nao_participa"
HORARIO_INEXISTENTE = "horario_inexistente"
AGENDA_MUDOU_DESDE_A_PREVIA = "agenda_mudou_desde_a_previa"
SEM_CONFIGURACAO = "sem_configuracao"
SEM_HORARIO_PARA_LIBERAR = "sem_horario_para_liberar"
