"""O déficit apurado causa a faixa seguinte pela `014` (016, `FR-255`).

**A seta é desta feature para a `014`, e nunca o contrário.** É a leitura literal da decisão de
fronteira de 11/09/2026: *"a `016` calcula o déficit e **causa** uma nova progressão pela `014`"*.
Se `classificacao` lesse a apuração para descobrir a causa, a `014` deixaria de ser compreensível
sozinha — e é por isso que `ocupacao` importa `classificacao`, e `classificacao` nunca importa
`ocupacao` (`R-002`).

**Esta feature não escolhe ninguém.** Ela entrega quantidade e motivo; quem lê a ordem e seleciona
é a `014`. A `FR-257` proíbe o contrário, e a `T047` o verifica por varredura de import — porque
prova de texto não prova que nenhum caminho ordena.

**O que muda em relação à `D-003` da `014`** é a origem do motivo, e não a forma do ato. Aquela
decisão previu exatamente isto: *"quando a `016` existir, ela passa a ser a origem do motivo, sem
que o ato mude de forma"*. Antes, quem emitia digitava o motivo; agora o déficit o escreve.
"""

from processo_seletivo.classificacao.application.emissao_do_corte import continuar_corte
from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.shared.api.problems import DomainError


def causar_faixa_seguinte(
    *,
    actor,
    processo_id,
    edital,
    perfil_id,
    marco_id,
    idempotency_key,
    correlation_id,
    lista_id=None,
):
    """Lê o déficit da apuração vigente e pede à `014` a faixa seguinte daquele tamanho.

    Recusa quando não há apuração, quando o déficit é zero, e quando a apuração está obsoleta — as
    três pelo mesmo princípio: a faixa seguinte é ato que alcança pessoas, e pedi-la sobre número
    que ninguém apurou, ou que já se sabe para trás, é pedi-la sem fundamento.
    """
    vigente = selectors.apuracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    if vigente is None:
        raise DomainError(
            nomes.NAO_APURADO,
            "Este recorte não tem ocupação apurada: apure antes de pedir a faixa seguinte.",
            409,
        )
    causas = selectors.causas_de_obsolescencia(vigente)
    if causas:
        nomeadas = "; ".join(item["descricao"] for item in causas)
        raise DomainError(
            nomes.APURACAO_OBSOLETA,
            f"A apuração vigente deste recorte está obsoleta, e a faixa seguinte sairia dela. "
            f"{nomeadas}",
            409,
        )
    deficit = vigente.faltando
    if not deficit:
        raise DomainError(
            nomes.DEFICIT_ZERO,
            "Não há vaga a ocupar neste recorte: a faixa seguinte não tem o que preencher.",
            409,
        )
    # **O motivo é escrito pelo déficit, e não digitado.** A `014` exige motivo textual porque, sem
    # a `016`, ninguém sabia por que a faixa seguinte era necessária. Agora o número o diz — e a
    # frase cita a apuração, para que a auditoria chegue nela sem abrir o banco.
    motivo = (
        f"Déficit apurado de {deficit} vaga(s) na apuração {vigente.id}: "
        f"{vigente.efetivas} efetivas com {vigente.ocupadas} ocupadas."
    )
    return continuar_corte(
        actor=actor,
        processo_id=processo_id,
        edital_id=edital.id,
        perfil_id=perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
        quantidade=deficit,
        motivo=motivo,
    )


__all__ = ["causar_faixa_seguinte"]
