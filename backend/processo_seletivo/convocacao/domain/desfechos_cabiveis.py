"""Que desfecho cabe agora nesta chamada — uma verificação, lida pela tela e pelo comando (152).

**Um predicado por guarda do comando de desfecho** (R-005, FR-5838). Cada um recebe o que a
chamada é e o que já se leu dela, e devolve `None` ou um `Impedimento` com o código e a frase que
o comando usa na recusa. As guardas de `desfechar.py` levantam a recusa a partir daqui; a tela da
convocação monta o seletor e a nota a partir daqui. Sem isso, o seletor ofereceria uma espécie
pela leitura dele e o comando a recusaria pela sua, e a nota diria uma razão que a recusa não diz.

**Funções puras, sem consulta.** A tela monta dezenas de linhas a partir do que já carregou, e uma
consulta por linha reprovaria o orçamento da tela (R-006). O comando lê o mesmo sob a trava, e
passa os valores.

**O que fica fora daqui é o que não é "ainda não cabe"**: a lista da convocação incompleta e as
assinaturas da `131` são falha de registro ou mudança concorrente, e o atestado de outra Inscrição
é dado forjado. Continuam só no comando.
"""

from typing import NamedTuple

from processo_seletivo.convocacao.domain import nomes, prazo


class Impedimento(NamedTuple):
    """Por que uma espécie não cabe agora: o código e a frase da recusa do comando.

    `a_partir_de` é o instante a partir do qual o impedimento deixa de valer, quando ele é só o
    prazo (FR-5836); `None` quando nenhum relógio o resolve.
    """

    codigo: str
    frase: str
    a_partir_de: object = None


#: A recusa da comunicação que não partiu é a do canal, completada aqui (125, FR-4001).
_COMPLEMENTO_SEM_ENVIO = "correr, e não há não atendimento a registrar."


def admite(*, especie_da_chamada, especie):
    """A espécie da chamada admite este desfecho, pela tabela do domínio (019)."""
    return especie in nomes.DESFECHOS_POR_ESPECIE.get(especie_da_chamada, ())


def admite_inercia(especie_da_chamada):
    """O gesto do atestado só onde a inércia cabe (FR-5840): não há matrícula a cancelar antes de
    a pessoa regularizar."""
    return admite(especie_da_chamada=especie_da_chamada, especie=nomes.INERCIA)


def desfecho_incompativel(*, especie_da_chamada, especie, rotulo_da_chamada):
    """A guarda de compatibilidade (`DESFECHO_INCOMPATIVEL_COM_A_CHAMADA`)."""
    if admite(especie_da_chamada=especie_da_chamada, especie=especie):
        return None
    return Impedimento(
        nomes.DESFECHO_INCOMPATIVEL_COM_A_CHAMADA,
        f"Uma convocação da espécie {rotulo_da_chamada.lower()} não admite este desfecho.",
    )


def nao_atendimento_prematuro(*, especie, enviado_em, vencimento, agora, canal):
    """Não atender pressupõe ter tido como atender (`FR-269a`, `FR-269b` da `019`).

    `canal` é o `vocabulario_do_canal.Canal` da convocação: a recusa sem envio diz a palavra dele.
    Sem vencimento informado, basta o envio — o Edital que não publica prazo deixa o juízo a quem
    conduz.
    """
    if especie != nomes.NAO_ATENDIMENTO:
        return None
    if not prazo.prazo_corre(enviado_em=enviado_em):
        return Impedimento(
            nomes.NAO_ATENDIMENTO_ANTES_DO_VENCIMENTO,
            canal.recusa_do_nao_atendimento + _COMPLEMENTO_SEM_ENVIO,
        )
    if vencimento is not None and not prazo.decorrido(
        vencimento=vencimento, enviado_em=enviado_em, agora=agora
    ):
        return Impedimento(
            nomes.NAO_ATENDIMENTO_ANTES_DO_VENCIMENTO,
            "O vencimento informado nesta convocação ainda não passou: a pessoa está dentro do "
            "prazo dela.",
            vencimento,
        )
    return None


def inercia_sem_ocupacao(*, especie, ocupando):
    """O cancelamento por inércia alcança quem já ocupava (§6 da `019`)."""
    if especie != nomes.INERCIA or ocupando:
        return None
    return Impedimento(
        nomes.INERCIA_SEM_OCUPACAO,
        "Esta Inscrição não consta ocupando vaga neste recorte: não há matrícula a cancelar por "
        "inércia. Quem foi chamado e não respondeu tem desfecho próprio — não atendimento à "
        "convocação.",
    )


def inercia_sem_atestado(*, especie, tem_atestado):
    """A inércia exige atestado de fato externo (`FR-277` da `019`)."""
    if especie != nomes.INERCIA or tem_atestado:
        return None
    return Impedimento(
        nomes.ATESTADO_OBRIGATORIO,
        "O cancelamento de matrícula por inércia exige atestado de fato externo: registre "
        "quem atestou e o que concluiu.",
    )


def inclusao_por_conferir(*, especie, pendentes):
    """Aceite e regularização só com os obrigatórios conferidos (FR-3592 da `115`).

    `pendentes` são os itens de `pendencias_para_incluir`, com `nome` e `sem_condicao_publicada`.
    O "não se aplica" registrado sem condição publicada não atende (131, FR-4470), e a frase diz
    por quê: sem isto, a comissão leria "falta" num item que a tela mostra como conferido.
    """
    if especie not in nomes.DESFECHOS_QUE_INCLUEM or not pendentes:
        return None
    nomes_dos_itens = ", ".join(
        f'{lido.nome} ("não se aplica" registrado sem condição publicada)'
        if lido.sem_condicao_publicada
        else lido.nome
        for lido in pendentes
    )
    return Impedimento(
        nomes.DOCUMENTOS_NAO_CONFERIDOS,
        "Para registrar este desfecho, todo documento obrigatório da convocação precisa estar "
        "conferido como conforme, ou como não se aplica quando o Edital publicou a condição. "
        f"Falta: {nomes_dos_itens}.",
    )


def impedimento(
    *,
    especie,
    enviado_em,
    vencimento,
    agora,
    canal,
    ocupando,
    tem_atestado,
    pendentes,
):
    """O primeiro impedimento de uma espécie que a chamada admite, na ordem das guardas do comando.

    A ordem é a de `desfechar.registrar`: não atendimento, ocupação, documentos, atestado. Duas
    razões para a mesma espécie — inércia sem ocupação e sem atestado — dizem a que o comando diria.
    """
    for verificar in (
        lambda: nao_atendimento_prematuro(
            especie=especie, enviado_em=enviado_em, vencimento=vencimento, agora=agora, canal=canal
        ),
        lambda: inercia_sem_ocupacao(especie=especie, ocupando=ocupando),
        lambda: inclusao_por_conferir(especie=especie, pendentes=pendentes),
        lambda: inercia_sem_atestado(especie=especie, tem_atestado=tem_atestado),
    ):
        achado = verificar()
        if achado is not None:
            return achado
    return None


def cabiveis(
    *,
    especie_da_chamada,
    enviado_em,
    vencimento,
    agora,
    canal,
    ocupando,
    tem_atestado,
    pendentes,
):
    """As espécies que cabem agora, e as que a chamada admite e ainda não cabem (FR-5835 a FR-5837).

    Devolve `(cabem, ainda_nao)`, na ordem de `ESPECIES_DE_DESFECHO`. `ainda_nao` são pares
    `(especie, Impedimento)`. A espécie que a chamada nunca admite não está em nenhuma das duas: ela
    não aparece no seletor nem na nota (FR-5837).

    **O indeferimento sempre cabe.** A ciência do prazo é exigência dele, e não impedimento
    (FR-5808): o seletor o oferece, e o formulário pede a marca.
    """
    cabem = []
    ainda_nao = []
    for especie in nomes.ESPECIES_DE_DESFECHO:
        if not admite(especie_da_chamada=especie_da_chamada, especie=especie):
            continue
        achado = impedimento(
            especie=especie,
            enviado_em=enviado_em,
            vencimento=vencimento,
            agora=agora,
            canal=canal,
            ocupando=ocupando,
            tem_atestado=tem_atestado,
            pendentes=pendentes,
        )
        if achado is None:
            cabem.append(especie)
        else:
            ainda_nao.append((especie, achado))
    return cabem, ainda_nao


def exige_ciencia_do_prazo(*, especie, pendentes, enviado_em, vencimento, agora):
    """O indeferimento com o prazo em curso e obrigatório não atendido pede ciência (R-002).

    **"Em curso" é a negação de `prazo.decorrido`**, a mesma leitura que libera o não atendimento:
    o indeferimento passa a pedir ciência exatamente onde o não atendimento ainda é recusado. Isso
    cobre o vencimento por vir (FR-5803), a convocação sem vencimento (FR-5804) e a ainda não
    comunicada, cujo relógio nem começou.

    **"Não conforme" é o obrigatório não atendido** (`pendencias_para_incluir`): o facultativo não
    decide desfecho nenhum (FR-3592 da `115`), e pedir ciência por ele seria aviso sem consequência.
    """
    if especie != nomes.INDEFERIMENTO or not pendentes:
        return False
    return not prazo.decorrido(vencimento=vencimento, enviado_em=enviado_em, agora=agora)


__all__ = [
    "Impedimento",
    "admite",
    "admite_inercia",
    "cabiveis",
    "desfecho_incompativel",
    "exige_ciencia_do_prazo",
    "impedimento",
    "inclusao_por_conferir",
    "inercia_sem_atestado",
    "inercia_sem_ocupacao",
    "nao_atendimento_prematuro",
]
