"""O fundamento da convocação, derivado da norma e dos atos que a sustentam (050, `D-009`).

**O que motiva uma chamada o sistema já sabe**: o Edital, o recorte, a espécie, a ordem e a faixa
vigentes, e a apuração que registrou a vaga. Digitá-lo de novo em cada convocação era copiar o mesmo
parágrafo N vezes — e a cópia número 37, com um erro de digitação, ficava num ato append-only.

**O complemento é de quem convoca**, e entra depois, separado. É onde cabe o *"no interesse da
Administração"* do 77/2026, ou o item do Edital que a pessoa quiser citar. O texto gravado é o que a
prévia mostrou: a função é pura, e a prévia e o ato a chamam com os mesmos argumentos.

**O vocabulário é o da `019`**, e a varredura que o guarda lê este arquivo: a frase diz que a
apuração *registra* vaga, e nunca que esta feature conta ocupação; e não promete a vaga a ninguém.
"""

from processo_seletivo.convocacao.domain import nomes

_POR_ESPECIE = {
    nomes.VAGA_INICIAL: (
        "Convocação para vaga inicial no {edital}, {recorte}: a posição da pessoa na ordem de "
        "classificação vigente está dentro das vagas que a apuração de ocupação emitida em {data} "
        "considerou, na faixa vigente deste recorte."
    ),
    nomes.SUPLENCIA: (
        "Convocação para vaga que vagou no {edital}, {recorte}: a pessoa é chamada, na ordem de "
        "classificação vigente, para vaga que a apuração de ocupação emitida em {data} registra "
        "como faltante."
    ),
    nomes.PARA_REGULARIZAR: (
        "Convocação para regularizar o indeferimento no {edital}, {recorte}: a faixa vigente "
        "alcançou a pessoa, o Resultado dela está indeferido, e a apuração de ocupação emitida em "
        "{data} registra vaga faltante."
    ),
}

NAO_ATENDIMENTO = (
    "Não atendimento à convocação no {edital}, {recorte}: a comunicação foi enviada e o vencimento "
    "informado no ato da convocação decorreu sem desfecho registrado."
)


def da_convocacao(*, especie, edital, recorte, data_da_apuracao):
    """O texto derivado, sem complemento. `data_da_apuracao` já vem formatada em data local."""
    return _POR_ESPECIE[especie].format(edital=edital, recorte=recorte, data=data_da_apuracao)


def do_nao_atendimento(*, edital, recorte):
    """O fundamento do desfecho de não atendimento registrado pelo gesto dos vencidos (`FR-877`)."""
    return NAO_ATENDIMENTO.format(edital=edital, recorte=recorte)


def da_destinacao(destinacoes):
    """A citação da destinação que a apuração considerou, ou vazio (155, FR-6340).

    `destinacoes` é `[(quantidade, lista, data)]`, com a lista por extenso e a data já formatada. A
    frase diz o que a apuração registra — a vaga que saiu da reserva e passou à ampla —, e não que
    esta pessoa ocupa aquela vaga e não outra: a apuração não distingue uma vaga da outra.
    """
    if not destinacoes:
        return ""
    itens = "; ".join(
        f"{quantidade} {'vaga' if quantidade == 1 else 'vagas'} da lista «{lista}» "
        f"{'destinada' if quantidade == 1 else 'destinadas'} à ampla concorrência em {data}"
        for quantidade, lista, data in destinacoes
    )
    return f"As vagas que a apuração registra neste recorte incluem a destinação de {itens}."


def com_destinacao(texto, citacao):
    """O texto e a citação da destinação, uma vez só (155, FR-6340).

    **Idempotente**: o gesto dos titulares grava o fundamento que a prévia já compôs com a citação,
    e o comando a acrescenta de novo para o caminho que chega com o fundamento digitado.
    """
    if not citacao or citacao in (texto or ""):
        return texto
    return f"{texto} {citacao}" if texto else citacao


def com_complemento(texto, complemento):
    """O texto derivado, e o complemento depois dele — nunca no lugar dele."""
    extra = (complemento or "").strip()
    return f"{texto} Complemento: {extra}" if extra else texto


__all__ = [
    "NAO_ATENDIMENTO",
    "com_complemento",
    "com_destinacao",
    "da_convocacao",
    "da_destinacao",
    "do_nao_atendimento",
]
