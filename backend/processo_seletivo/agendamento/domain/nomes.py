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
PUBLICACAO_DA_AGENDA = "agenda.publicacao"
ROTULOS_DA_TRILHA = {
    CONFIGURACAO_SALVA: "Configuração da agenda da Etapa salva",
    AGENDAMENTO: "Agendamento à mão na agenda da Etapa",
    PREENCHIMENTO_APLICADO: "Preenchimento automático da agenda da Etapa aplicado",
    PUBLICACAO_DA_AGENDA: "Agenda da Etapa publicada",
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
# A distribuição mudou entre a tela da remarcação e a confirmação (179, research T-006).
CONFLITOS_MUDARAM = "conflitos_mudaram"
PESSOA_JA_AGENDADA = "pessoa_ja_agendada"
PESSOA_NAO_PARTICIPA = "pessoa_nao_participa"
HORARIO_INEXISTENTE = "horario_inexistente"
AGENDA_MUDOU_DESDE_A_PREVIA = "agenda_mudou_desde_a_previa"
SEM_CONFIGURACAO = "sem_configuracao"
SEM_HORARIO_PARA_LIBERAR = "sem_horario_para_liberar"
AGENDA_PUBLICADA = "agenda_publicada"

# --- os atos da agenda (entrega B) ----------------------------------------------------------------
PUBLICACAO = "PUBLICACAO"
REMARCACAO = "REMARCACAO"
INCLUSAO = "INCLUSAO"
CANCELAMENTO = "CANCELAMENTO"
ESPECIES = (PUBLICACAO, REMARCACAO, INCLUSAO, CANCELAMENTO)

# A situação de cada pessoa num ato: no horário, ou fora da agenda vigente (o cancelamento, na C).
AGENDADO = "AGENDADO"
CANCELADO = "CANCELADO"

# O veículo da publicação (`D-008`), como na `159`: a página pública do GPS, com a declaração do
# item do Edital que a admite, ou a publicação feita fora dele, com onde e quando.
VEICULO_GPS = "GPS"
VEICULO_EXTERNO = "EXTERNO"

# Como o conteúdo público identifica a pessoa (FR-7225, `D-009`): nome e protocolo, ou só o
# protocolo na Etapa restrita por Modalidade.
NOME_E_PROTOCOLO = "NOME_E_PROTOCOLO"
PROTOCOLO = "PROTOCOLO"

# --- §1 depois da publicação (FR-7208) -----------------------------------------------------------
HORARIO_PUBLICADO_REMOVIDO = "horario_publicado_removido"
PARAMETRO_PUBLICADO_ALTERADO = "parametro_publicado_alterado"

# --- §4 a conferência: impedimentos e recusas da confirmação ------------------------------------
PARTICIPANTES_SEM_HORARIO = "participantes_sem_horario"
AGENDADOS_QUE_NAO_PARTICIPAM = "agendados_que_nao_participam"
CONFIGURACAO_INVALIDA = "configuracao_invalida"
BANCA_SEM_LOCAL = "banca_sem_local"
SEM_AUTORIDADE_VIGENTE = "sem_autoridade_vigente"
PUBLICACAO_IMPEDIDA = "publicacao_impedida"
AGENDA_MUDOU_DESDE_A_CONFERENCIA = "agenda_mudou_desde_a_conferencia"
VEICULO_NAO_ESCOLHIDO = "veiculo_nao_escolhido"
DECLARACAO_DO_VEICULO_AUSENTE = "declaracao_do_veiculo_ausente"
PUBLICACAO_EXTERNA_INCOMPLETA = "publicacao_externa_incompleta"
AUTORIDADE_INVALIDA = "autoridade_invalida"

# --- §5 a agenda publicada: os atos individuais (entrega C) -------------------------------------
MOTIVO_AUSENTE = "motivo_ausente"
HORARIO_NAO_ESCOLHIDO = "horario_nao_escolhido"
MESMO_HORARIO = "mesmo_horario"
PESSOA_JA_TEM_HORARIO_PUBLICADO = "pessoa_ja_agendada"
INCLUSAO_DE_QUEM_NAO_PARTICIPA = "inclusao_de_quem_nao_participa"
CANCELAMENTO_DE_QUEM_PARTICIPA = "cancelamento_de_quem_participa"
AGENDA_NAO_PUBLICADA = "agenda_nao_publicada"
SEM_HORARIO_PUBLICADO = "sem_horario_publicado"
AVISO_NAO_REENVIAVEL = "aviso_nao_reenviavel"

# As operações da trilha dos atos individuais e do reenvio (FR-7256).
REMARCACAO_DA_AGENDA = "agenda.remarcacao"
INCLUSAO_NA_AGENDA = "agenda.inclusao"
CANCELAMENTO_NA_AGENDA = "agenda.cancelamento"
REENVIO_DO_AVISO_DA_AGENDA = "agenda.reenvio"
ROTULOS_DA_TRILHA.update(
    {
        REMARCACAO_DA_AGENDA: "Remarcação na agenda da Etapa",
        INCLUSAO_NA_AGENDA: "Inclusão na agenda da Etapa",
        CANCELAMENTO_NA_AGENDA: "Cancelamento na agenda da Etapa",
        REENVIO_DO_AVISO_DA_AGENDA: "Reenvio do aviso da agenda da Etapa",
    }
)
