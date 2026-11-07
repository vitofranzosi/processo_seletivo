"""O vocabulário da entrega documental à formalização (117): capacidade, recusas, trilha.

**Um lugar só para cada nome**, pela razão que fez a `115` escrever o dela: a tela, o comando, o
manifesto e a trilha dizem as mesmas coisas, e duas grafias de "arquivo indisponível" divergiriam na
primeira correção.

**Nenhum nome afirma o que o GPS não sabe** (FR-3699, FR-3701, D-015). Ele sabe que serviu um
arquivo `inline`, que serviu um anexo e que gerou um pacote e o disponibilizou para download. Não
sabe se a
transferência terminou, se o setor recebeu nem se a matrícula foi efetivada — e por isso nenhuma
dessas palavras existe aqui.
"""

import hashlib

#: O papel do catálogo e a capacidade única dele (FR-3661). Escritos aqui e repetidos, por extenso,
#: no `PAPEIS` da fronteira de identidade, que não importa quem a consome.
PAPEL = "formalizacao"
CAPACIDADE = "formalizacao:acessar"
NOME_DO_PAPEL = "Formalização"

# ---------------------------------------------------------------------------
# As recusas
# ---------------------------------------------------------------------------

MOTIVO_OBRIGATORIO = "formalizacao_motivo_obrigatorio"
REQUISITO_FORA_DO_EDITAL = "formalizacao_requisito_fora_do_edital"
EDITAL_SEM_PUBLICACAO = "formalizacao_edital_sem_publicacao"
DESIGNADO_SEM_PAPEL = "formalizacao_designado_sem_papel"
AUTODESIGNACAO = "formalizacao_autodesignacao"
PERFIL_FORA_DO_EDITAL = "formalizacao_perfil_fora_do_edital"
DESIGNACAO_JA_VIGENTE = "formalizacao_designacao_ja_vigente"
DESIGNACAO_JA_REVOGADA = "formalizacao_designacao_ja_revogada"
PESSOA_INDISPONIVEL = "formalizacao_pessoa_indisponivel"
EXPORTACAO_EM_ANDAMENTO = "formalizacao_exportacao_em_andamento"
LIMITE_EXCEDIDO = "formalizacao_limite_excedido"
VERIFICACAO_DEFASADA = "formalizacao_verificacao_defasada"
VERIFICACAO_INVALIDA = "formalizacao_verificacao_invalida"
VERIFICACAO_EXPIRADA = "formalizacao_verificacao_expirada"
PESSOA_INCOMPLETA = "formalizacao_pessoa_incompleta"
SEM_DOCUMENTO = "formalizacao_sem_documento"
SEM_PESSOA = "formalizacao_sem_pessoa"
ALCANCE_INVALIDO = "formalizacao_alcance_invalido"

#: As frases das recusas que a tela repete. A da trava é a da spec, palavra por palavra (FR-3692).
EM_ANDAMENTO = "Uma exportação sua já está em andamento. Espere ela terminar e tente de novo."
DEFASADA = (
    "Algo mudou desde a verificação: um resultado, um arquivo, a definição dos documentos ou a sua "
    "designação. Nada foi baixado. Verifique de novo para ver o que vai receber."
)
INVALIDA = "Esta verificação não vale. Nada foi baixado. Verifique de novo."
EXPIRADA = "Esta verificação passou de 15 minutos. Nada foi baixado. Verifique de novo."
INTERROMPIDA = "A exportação não foi concluída. Nada foi baixado nem registrado."

# ---------------------------------------------------------------------------
# A situação de cada documento de uma pessoa (FR-3672)
# ---------------------------------------------------------------------------

INCLUIDO = "INCLUIDO"
NAO_SE_APLICA = "NAO_SE_APLICA"
# **O "não se aplica" que alguém decidiu** (131, FR-4473, D-016): a conferência afastou um
# obrigatório cuja condição publicada não alcança a pessoa. Distinto do que o recorte excluiu, para
# o setor saber que o documento não veio por decisão da comissão, e quando. O motivo não vai
# (FR-3687 da `117`).
NAO_SE_APLICA_APOS_ANALISE = "NAO_SE_APLICA_APOS_ANALISE"
NAO_APRESENTADO = "NAO_APRESENTADO"
NAO_CONFERIDO = "NAO_CONFERIDO"
INDISPONIVEL = "INDISPONIVEL"
INTEGRIDADE = "INTEGRIDADE"

SITUACOES = (
    INCLUIDO,
    NAO_SE_APLICA,
    NAO_SE_APLICA_APOS_ANALISE,
    NAO_APRESENTADO,
    NAO_CONFERIDO,
    INDISPONIVEL,
    INTEGRIDADE,
)
#: Só estas duas tornam a pessoa incompleta, e só se conhecem lendo o arquivo (FR-3672, FR-3694).
QUE_EXCLUEM = (INDISPONIVEL, INTEGRIDADE)

ROTULO_DA_SITUACAO = {
    INCLUIDO: "disponível",
    NAO_SE_APLICA: "não se aplica",
    NAO_SE_APLICA_APOS_ANALISE: "não se aplica após análise",
    NAO_APRESENTADO: "não apresentado",
    NAO_CONFERIDO: "não conferido",
    INDISPONIVEL: "arquivo indisponível",
    INTEGRIDADE: "arquivo diferente do conferido",
}

#: O documento da inscrição sai sem conferência, e a tela e o manifesto dizem isso (FR-3671).
SEM_CONFERENCIA_NA_CONVOCACAO = "enviado na inscrição; sem conferência na convocação"

#: Os dois momentos, ditos para gente.
DA_CONVOCACAO = "convocação"
DA_INSCRICAO = "inscrição"

#: De onde vem o arquivo: a apresentação da convocação ou o documento da inscrição.
ORIGEM_APRESENTACAO = "apresentacao"
ORIGEM_DOCUMENTO = "documento"
ORIGENS = (ORIGEM_APRESENTACAO, ORIGEM_DOCUMENTO)

# ---------------------------------------------------------------------------
# A exportação
# ---------------------------------------------------------------------------

COMPLETO = "COMPLETO"
PARCIAL = "PARCIAL"
RESULTADOS = (COMPLETO, PARCIAL)

PESSOA = "PESSOA"
SELECAO = "SELECAO"
RECORTE = "RECORTE"
ALCANCES = (PESSOA, SELECAO, RECORTE)

ROTULO_DO_ALCANCE = {
    PESSOA: "uma pessoa",
    SELECAO: "pessoas selecionadas",
    RECORTE: "todos os aptos",
}

INCLUIDA = "INCLUIDA"
NAO_INCLUIDA = "NAO_INCLUIDA"

#: O motivo codificado de uma exclusão, que entra no resumo da verificação (FR-3689b).
MOTIVO_DA_EXCLUSAO = {INDISPONIVEL: "INDISPONIVEL", INTEGRIDADE: "INTEGRIDADE"}

# ---------------------------------------------------------------------------
# A trilha (FR-3699)
# ---------------------------------------------------------------------------

DEFINIR = "FORMALIZACAO_DEFINIR"
DESIGNAR = "FORMALIZACAO_DESIGNAR"
REVOGAR = "FORMALIZACAO_REVOGAR"
VISUALIZAR = "FORMALIZACAO_VISUALIZAR"
DOWNLOAD = "FORMALIZACAO_DOWNLOAD"
VERIFICAR = "FORMALIZACAO_VERIFICAR"
EXPORTAR = "FORMALIZACAO_EXPORTAR"
RECUSAR = "FORMALIZACAO_RECUSAR"
INTERROMPER = "FORMALIZACAO_INTERROMPER"
#: O evento de arquivo ausente (FR-3695). **Sem prefixo**, porque vale também nas views da
#: inscrição, da mesa e da convocação, como o `INTEGRIDADE` que já existe.
ARQUIVO_INDISPONIVEL = "ARQUIVO_INDISPONIVEL"

ROTULOS_DA_TRILHA = {
    DEFINIR: "Definição dos documentos para a formalização gravada",
    DESIGNAR: "Designação para a formalização concedida",
    REVOGAR: "Designação para a formalização revogada",
    VISUALIZAR: "Documento visualizado pela formalização",
    DOWNLOAD: "Download individual disponibilizado à formalização",
    VERIFICAR: "Verificação de exportação à formalização",
    EXPORTAR: "Pacote gerado e disponibilizado para download",
    RECUSAR: "Exportação à formalização recusada",
    INTERROMPER: "Exportação à formalização interrompida",
    ARQUIVO_INDISPONIVEL: "Arquivo indisponível",
}

#: Os motivos da recusa, como a trilha os grava (data-model).
RECUSA_DEFASADA = "verificacao_defasada"
RECUSA_INVALIDA = "verificacao_invalida"
RECUSA_EXPIRADA = "verificacao_expirada"
RECUSA_LIMITE = "limite"
RECUSA_PESSOA_INCOMPLETA = "pessoa_incompleta"

# ---------------------------------------------------------------------------
# A trava consultiva (FR-3692)
# ---------------------------------------------------------------------------


def _int4(texto):
    """Um inteiro de 32 bits com sinal, estável, a partir de um texto: o que o PostgreSQL pede."""
    bruto = int.from_bytes(hashlib.sha256(texto.encode()).digest()[:4], "big")
    return bruto - (1 << 32) if bruto >= (1 << 31) else bruto


#: A classe fixa da feature, o primeiro inteiro da trava de duas chaves.
CLASSE_DA_TRAVA = _int4("processo_seletivo.formalizacao.exportacao")


def chave_da_trava(subject):
    """O segundo inteiro: o resumo do identificador do servidor. A colisão recusa sem motivo, e é
    rara: o texto é o mesmo e repetir resolve (FR-3692)."""
    return _int4(f"servidor:{subject}")


#: O sal do comprovante (FR-3689a). Próprio da feature: um valor assinado por outra parte do sistema
#: com a mesma chave não vale aqui.
SAL_DO_COMPROVANTE = "processo_seletivo.formalizacao.verificacao"
VALIDADE_DO_COMPROVANTE = 15 * 60
VERSAO_DO_COMPROVANTE = 1
