"""O desfecho da convocação em linguagem simples, para o portal (156, R-001).

**O fundamento é o ato; a frase simples é a leitura dele** (D-002). O portal mostrava ao candidato
só o fundamento — *"…o vencimento informado no ato da convocação decorreu sem desfecho
registrado"* —, que está certo como motivação e que ninguém fora da comissão entende (achado 18 do
estudo da jornada final). A frase sai daqui, derivada da espécie e dos dados do ato no momento da
leitura, e **nunca se grava**: o ato continua palavra por palavra, recolhido logo abaixo dela
(FR-6400 a FR-6402).

**Puro, como `situacao.py` e `obrigacoes.py`**: sem banco e sem relógio. Quem chama passa o que já
leu, e é por isso que o acompanhamento continua sem consulta nova (`TestCusto` da `063`). A data é
a local do instante gravado, e não a de agora.

**As varreduras de vocabulário leem este arquivo** (da convocação, dos documentos e do
Requerimento): nenhuma frase daqui diz *homologa*, *dentro das vagas* nem promete o que nenhum ato
declarou (FR-6408). *"Esta convocação está encerrada para você"* diz o efeito do desfecho sobre a
chamada, e não sobre o certame (FR-1177 da `063`, acrescida pela `156`).
"""

from django.utils import formats, timezone

from processo_seletivo.convocacao.domain import nomes

#: O rótulo sob o qual o fundamento do desfecho fica recolhido (FR-6400).
FUNDAMENTO_DO_REGISTRO = "Fundamento do registro"

ENCERRADA = "Esta convocação está encerrada para você."
NAO_E_MATRICULA = "Este registro não é matrícula, bolsa nem contrato."

#: O fato atestado, dito como a pessoa o diria (FR-6407): um por espécie de atestado da `019`.
FATO_ATESTADO = {
    nomes.ATESTADO_NAO_ACESSO_AO_AMBIENTE: "não houve acesso ao ambiente do curso",
    nomes.ATESTADO_AUSENCIA_NA_PRIMEIRA_SEMANA: "não houve presença na primeira semana do curso",
    nomes.ATESTADO_NAO_ENTREGA_PRESENCIAL: "a entrega presencial não foi feita",
}


def frase_do_desfecho(especie, *, registrado_em, fim_do_prazo=None, atestado=""):
    """A frase simples da espécie, pela tabela da FR-6406, ou vazio para espécie desconhecida.

    `fim_do_prazo` é o vencimento da convocação vigente, e só o não atendimento o diz; `atestado`
    é a espécie do atestado que fundamentou o cancelamento por inércia. No máximo duas frases
    (UX-620): o próximo passo, quando houver, vem depois, de quem chama.
    """
    data = _data(registrado_em)
    if especie == nomes.ACEITE:
        return f"A comissão registrou o resultado da sua convocação em {data}. {NAO_E_MATRICULA}"
    if especie == nomes.REGULARIZACAO:
        return (
            "A comissão registrou a regularização da sua situação nesta convocação em "
            f"{data}. {NAO_E_MATRICULA}"
        )
    if especie == nomes.INDEFERIMENTO:
        return (
            f"A comissão registrou o indeferimento desta convocação em {data}: ela concluiu que o "
            "que o Edital pede nesta etapa não foi cumprido. O motivo está no fundamento, abaixo."
        )
    if especie == nomes.DESISTENCIA_EXPRESSA:
        return f"A comissão registrou a sua desistência desta convocação em {data}. {ENCERRADA}"
    if especie == nomes.NAO_ATENDIMENTO:
        # O não atendimento só se registra depois do vencimento (`019`); sem ele, a frase não
        # inventa data.
        quando = f" em {_data(fim_do_prazo)}" if fim_do_prazo is not None else ""
        return (
            f"O prazo desta convocação terminou{quando} sem que ela fosse atendida, e a comissão "
            f"registrou isso em {data}. {ENCERRADA}"
        )
    if especie == nomes.INERCIA:
        fato = FATO_ATESTADO.get(atestado or "")
        porque = f", porque {fato}" if fato else ""
        return f"A comissão registrou o cancelamento em {data}{porque}. {ENCERRADA}"
    if especie == nomes.RECLASSIFICACAO:
        return (
            f"A comissão registrou a sua reclassificação em {data}. Esta convocação está "
            "encerrada para você; o que acontece depois é o que o Edital diz."
        )
    return ""


def do_desfecho(desfecho, convocacao):
    """A frase de um desfecho lido, com a convocação a que ele pertence.

    O atestado só é lido no cancelamento por inércia — o único que o tem —, e chega pelo `prefetch`
    de `vigentes_por_inscricao`, sem consulta.
    """
    atestado = desfecho.atestado if desfecho.especie == nomes.INERCIA else None
    return frase_do_desfecho(
        desfecho.especie,
        registrado_em=desfecho.registrado_em,
        fim_do_prazo=convocacao.vencimento,
        atestado=atestado.especie if atestado is not None else "",
    )


def fundamento_do_registro(desfecho):
    """O que fica recolhido: o fundamento gravado, sem edição, com a data do registro (FR-6401)."""
    return f"Registrado em {_data(desfecho.registrado_em)}: {desfecho.fundamento.strip()}"


def _data(instante):
    return formats.date_format(timezone.localtime(instante), "d/m/Y")


__all__ = [
    "ENCERRADA",
    "FATO_ATESTADO",
    "FUNDAMENTO_DO_REGISTRO",
    "NAO_E_MATRICULA",
    "do_desfecho",
    "frase_do_desfecho",
    "fundamento_do_registro",
]
