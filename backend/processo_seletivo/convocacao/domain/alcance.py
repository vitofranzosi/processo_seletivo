"""O alcance de cada gesto da `050`: quem ele toca, quem fica de fora e por quê, e a assinatura.

**O gesto é o começo da fila, e nunca a fila filtrada** (`D-001` da `050`). Convocar os titulares
num ato só vai da primeira pessoa da fila até a primeira que não é titular, e para ali. Pular quem
não cabe e seguir adiante faria o sistema decidir precedência — e a `FR-267` só a admite com
fundamento registrado por uma pessoa, na chamada individual.

**A assinatura é a identidade do que foi declarado** (`D-007`). A prévia a calcula, a confirmação a
carrega, e o comando a recalcula sob a trava. É o padrão da `014` (`assinatura_da_proposta`): o que
se confirma é o que se viu, e não o que o banco tiver no instante do clique.

Puro: recebe o que a leitura do recorte já produziu, e não consulta nada.
"""

from dataclasses import dataclass, field

from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.ocupacao.domain.apuracao import chave_da_inscricao
from processo_seletivo.shared.canonical import canonical_sha256

#: Por que o gesto dos titulares parou antes do fim da fila.
PARADA_SUPLENTE = "suplente"
PARADA_REABILITADO = "reabilitado"


@dataclass(frozen=True)
class Titulares:
    """O alcance do gesto dos titulares: quem entra, em ordem, e quem o interrompeu."""

    pessoas: tuple
    parada: object = None
    motivo_da_parada: str = ""


@dataclass(frozen=True)
class Particao:
    """Quem o gesto alcança, e as exclusões contadas por razão (`FR-878`, `UX-102`)."""

    alcancadas: tuple
    fora: dict = field(default_factory=dict)


def titulares_do_comeco_da_fila(fila, *, ocupando, reabilitados=()):
    """O prefixo da fila de quem ocupa vaga pela contagem, e o primeiro que não ocupa.

    **Titular é quem a `016` conta como ocupante antes de qualquer chamada**, e é só ele que o gesto
    formaliza. O primeiro que não ocupa é suplente — chamá-lo é escolher quando chamar a vaga que
    vagou, e continua sendo a chamada individual, por decisão do usuário (clarificação de 28/09).

    **O reabilitado por deferimento é nomeado à parte** (`FR-292b`): ele está no topo da fila porque
    a decisão recursal devolveu a vez, e quando não ocupa vaga pela contagem, o gesto para nele — a
    frase certa não é "é suplente", é "a decisão recursal o pôs à frente".
    """
    ocupantes = {chave_da_inscricao(i) for i in ocupando}
    reabilitados_de = {chave_da_inscricao(i) for i in reabilitados}
    pessoas = []
    for inscricao in fila:
        chave = chave_da_inscricao(inscricao)
        if chave in ocupantes:
            pessoas.append(inscricao)
            continue
        motivo = PARADA_REABILITADO if chave in reabilitados_de else PARADA_SUPLENTE
        return Titulares(pessoas=tuple(pessoas), parada=inscricao, motivo_da_parada=motivo)
    return Titulares(pessoas=tuple(pessoas))


def vencidas(linhas):
    """As convocações com o vencimento decorrido e sem desfecho, e as outras sem desfecho, por
    razão.

    **O estado é o que a `019` já deriva** (`R-009`): vencido só existe quando o prazo chegou a
    correr, e prazo não iniciado não vence, por mais antiga que seja a data (`FR-269a`). As
    exclusões são contadas porque a prévia diz quantas ficaram e por quê.
    """
    alcancadas, fora = [], {"emCurso": 0, "naoIniciado": 0, "semVencimento": 0}
    for linha in linhas:
        if linha["desfecho"] is not None:
            continue
        estado = linha["estado"]
        if estado == nomes.CONVOCADO_VENCIMENTO_DECORRIDO:
            alcancadas.append(linha)
        elif estado == nomes.CONVOCADO_PRAZO_NAO_INICIADO:
            fora["naoIniciado"] += 1
        elif linha["convocacao"].vencimento is None:
            fora["semVencimento"] += 1
        else:
            fora["emCurso"] += 1
    return Particao(alcancadas=tuple(alcancadas), fora=fora)


def pendentes(linhas):
    """As convocações sem desfecho e sem envio com sucesso — as que o prazo ainda não alcançou."""
    return Particao(
        alcancadas=tuple(
            linha for linha in linhas if linha["desfecho"] is None and linha["enviadaEm"] is None
        )
    )


def assinatura(*, gesto, apuracao_id, versao_id, forma, identidades):
    """A identidade do alcance declarado: o gesto, os atos que o fundam e quem ele toca, em ordem.

    **A ordem entra na assinatura**: a mesma gente em outra ordem é outra chamada, porque a espécie
    e o fundamento de cada um dependem de onde ela está na fila.
    """
    return canonical_sha256(
        {
            "gesto": gesto,
            "apuracao": str(apuracao_id) if apuracao_id else None,
            "versao": str(versao_id) if versao_id else None,
            "forma": forma or None,
            "identidades": [str(i) for i in identidades],
        }
    )


__all__ = [
    "PARADA_REABILITADO",
    "PARADA_SUPLENTE",
    "Particao",
    "Titulares",
    "assinatura",
    "pendentes",
    "titulares_do_comeco_da_fila",
    "vencidas",
]
