"""A palavra da comunicação da convocação, pelo canal (125, FR-3998 a FR-4004).

**Publicada na publicação, enviada na mensagem** (3ª decisão do usuário, 06/11/2026). O registro da
publicação é gravado como comunicação com resultado `ENVIADA` — é o que inicia o prazo nas duas
formas —, e por isso as telas liam *"Comunicação enviada em"* de uma convocação que ninguém enviou.
O registro não muda; muda a leitura, e ela mora aqui, uma fonte só, para que o portal, a gestão e as
recusas não escrevam cada um a sua.

**A forma é a da convocação**, e não a vigente do Edital: a da última comunicação, ou a que a
convocação citou quando nenhuma houve. Sem forma declarada, as frases são as da mensagem — as de
sempre: a 1ª e a 3ª decisões alcançam só a publicação.
"""

from dataclasses import dataclass

from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMA_POR_PUBLICACAO


@dataclass(frozen=True)
class Canal:
    """As frases de um canal. `publicacao` só escolhe o ramo do template; o texto está aqui."""

    publicacao: bool
    # --- Portal ---------------------------------------------------------------------------------
    # O rótulo da data (mensagem) ou da referência (publicação) nos dados do ato (D-005).
    rotulo_da_comunicacao: str
    contado_de: str
    prazo_nao_iniciado: str
    # --- Gestão ---------------------------------------------------------------------------------
    pastilha_sem_comunicacao: str
    situacao_sem_comunicacao: str
    rotulo_do_registro: str
    contado_de_na_gestao: str
    titulo_das_pendentes: str
    sem_comunicacao_no_recorte: str
    sem_comunicacao_no_vencido: str
    emitir: str
    emitir_de_novo: str
    a_partir_de: str
    sai_no_ato: str
    estado_indeterminado: str
    nao_iniciado_na_correcao: str
    # --- Recusas --------------------------------------------------------------------------------
    recusa_do_nao_atendimento: str
    recusa_do_vencimento: str
    recusa_do_estado_indeterminado: str
    recusa_sem_pendente: str


MENSAGEM = Canal(
    publicacao=False,
    rotulo_da_comunicacao="Comunicação enviada em",
    contado_de="contado do envio da comunicação",
    prazo_nao_iniciado=(
        "O prazo ainda não começou a correr: ele conta a partir do envio da comunicação."
    ),
    pastilha_sem_comunicacao="Sem comunicação enviada",
    situacao_sem_comunicacao=(
        "Convocado, prazo não iniciado — a comunicação ainda não foi enviada com sucesso"
    ),
    rotulo_do_registro="Enviada em",
    contado_de_na_gestao="contado do envio da comunicação",
    titulo_das_pendentes="Comunicações que ainda não saíram",
    sem_comunicacao_no_recorte="sem comunicação enviada",
    sem_comunicacao_no_vencido="porque a comunicação não foi enviada com sucesso",
    emitir="Emitir a comunicação",
    emitir_de_novo="Emitir a comunicação de novo",
    a_partir_de="a partir do envio da comunicação",
    sai_no_ato="A comunicação sai no mesmo ato.",
    estado_indeterminado=(
        "a mensagem pode ter saído sem registro. Confira o histórico antes de emitir de novo"
    ),
    nao_iniciado_na_correcao="prazo ainda não iniciado: a comunicação não foi enviada com sucesso",
    recusa_do_nao_atendimento=(
        "A comunicação desta convocação não foi enviada com sucesso: o prazo não começou a "
    ),
    recusa_do_vencimento="O vencimento informado nesta convocação é anterior ao envio: ",
    recusa_do_estado_indeterminado=(
        "Já há uma emissão desta convocação em curso com esta chave, ou uma que não chegou a "
        "ser registrada. A mensagem pode ter saído: confira o histórico da convocação antes de "
        "emitir de novo, e use a tela recarregada — ela traz chave nova."
    ),
    recusa_sem_pendente="Não há convocação sem comunicação enviada neste recorte.",
)

PUBLICACAO = Canal(
    publicacao=True,
    rotulo_da_comunicacao="Publicada em",
    contado_de="contado da publicação",
    prazo_nao_iniciado=(
        "O prazo ainda não começou a correr: ele conta a partir da publicação da convocação."
    ),
    pastilha_sem_comunicacao="Publicação não registrada",
    situacao_sem_comunicacao=(
        "Convocado, prazo não iniciado — a publicação ainda não foi registrada, e o candidato "
        "ainda não vê esta convocação"
    ),
    rotulo_do_registro="Publicação registrada em",
    contado_de_na_gestao="contado do registro da publicação",
    titulo_das_pendentes="Publicações a registrar",
    sem_comunicacao_no_recorte="sem publicação registrada",
    sem_comunicacao_no_vencido="porque a publicação ainda não foi registrada",
    emitir="Registrar a publicação",
    emitir_de_novo="Registrar outra publicação",
    a_partir_de="a partir do registro da publicação",
    sai_no_ato=(
        "A publicação, você registra depois; o candidato só vê a convocação a partir do registro."
    ),
    estado_indeterminado=(
        "o registro da publicação pode ter sido gravado. Confira o histórico antes de registrar "
        "de novo"
    ),
    nao_iniciado_na_correcao="prazo ainda não iniciado: a publicação ainda não foi registrada",
    recusa_do_nao_atendimento=(
        "A publicação desta convocação ainda não foi registrada: o prazo não começou a "
    ),
    recusa_do_vencimento=(
        "O vencimento informado nesta convocação é anterior ao registro da publicação: "
    ),
    recusa_do_estado_indeterminado=(
        "Já há um registro desta publicação em curso com esta chave, ou um que não chegou a "
        "ser concluído. O registro da publicação pode ter sido gravado: confira o histórico da "
        "convocação antes de registrar de novo, e use a tela recarregada — ela traz chave nova."
    ),
    recusa_sem_pendente="Não há convocação com publicação a registrar neste recorte.",
)


def canal(forma):
    """As frases do canal de uma forma; sem forma, as da mensagem, que são as de sempre."""
    return PUBLICACAO if forma == FORMA_POR_PUBLICACAO else MENSAGEM
