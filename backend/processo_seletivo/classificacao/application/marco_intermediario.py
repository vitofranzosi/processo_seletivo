"""O marco intermediário não apura vagas nem convoca (133, FR-4532 a FR-4537, R1 do usuário).

**Uma regra, lida em todos os lugares** (FR-4531), como a `128` fez com a ordem sem resultado: os
comandos que apuram, acrescentam vaga, causam faixa por déficit e convocam chamam `recusar`, que é a
porta de gravação; a condução do marco, o andamento e as telas da ocupação e da convocação chamam
`impedimento`, para não oferecer o que o comando recusaria. Corrigir só o cartão deixaria o ato
acessível pela URL, pela API e pelo gesto da condução — foi por isso que o usuário pediu a recusa no
comando (decisão R1 de 07/11/2026).

**O que continua permitido** é encerrar o que já existe (D-002 da spec): desfecho, conferência de
documento, comunicação e atestado de convocação legada. Esta regra não é chamada por eles.
"""

from processo_seletivo.classificacao.domain.marco_intermediario import marco_que_le
from processo_seletivo.shared.api.problems import DomainError

CODIGO = "apuracao_em_marco_intermediario"


def _perfil(conteudo, perfil_id):
    alvo = str(perfil_id)
    return next(
        (p for p in (conteudo or {}).get("profiles") or [] if str(p.get("id")) == alvo), None
    )


def _nome_da_etapa(conteudo, etapa_id):
    etapa = next(
        (e for e in (conteudo or {}).get("stages") or [] if str(e.get("id")) == str(etapa_id)),
        None,
    )
    return (etapa or {}).get("name") or "seguinte"


def impedimento(conteudo, perfil_id, marco_id):
    """`None`, ou `{frase, nota, marco_que_le_id, nome_do_marco_que_le}` quando o marco é
    intermediário. `conteudo` é o conteúdo vigente do Edital, que quem chama já leu."""
    from processo_seletivo.classificacao.domain.faixa import etapa_governada

    perfil = _perfil(conteudo, perfil_id)
    if perfil is None:
        return None
    que_le = marco_que_le(perfil, marco_id)
    if que_le is None:
        return None
    marco = next(
        m for m in perfil.get("classificationMilestones") or [] if str(m.get("id")) == str(marco_id)
    )
    nome = marco.get("name") or "classificação deste marco"
    nome_que_le = que_le.get("name") or "classificação seguinte"
    etapa = _nome_da_etapa(conteudo, etapa_governada(marco.get("cutRule")))
    return {
        "frase": (
            f"A {nome} decide quem participa da Etapa {etapa}: ela não apura vagas nem convoca. "
            f"As vagas são apuradas e convocadas na {nome_que_le}."
        ),
        "nota": f"decide quem vai à {etapa}; as vagas são da {nome_que_le}",
        "marco_que_le_id": str(que_le.get("id")),
        "nome_do_marco_que_le": nome_que_le,
    }


def recusar(conteudo, perfil_id, marco_id):
    """Levanta a recusa quando o marco é intermediário; fora dele, não faz nada."""
    achado = impedimento(conteudo, perfil_id, marco_id)
    if achado is not None:
        raise DomainError(CODIGO, achado["frase"], 409, campo="marco")


__all__ = ["CODIGO", "impedimento", "recusar"]
