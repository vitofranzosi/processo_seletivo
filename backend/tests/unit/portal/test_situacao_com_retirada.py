"""O candidato retirado da reserva não lê "Eliminado" (164, US3, FR-7024, UX-742).

Pela mesma régua de `test_situacao_da_inscricao.py`: a função é pura, e os objetos são montados em
memória.
"""

import uuid

from processo_seletivo.portal import situacao
from tests.unit.portal.test_situacao_da_inscricao import PPI, calcular, cartao, eliminada, textos

MOTIVO = (
    "a avaliação concluiu Não confirmada; deixa de concorrer pela reserva Pretos e pardos e "
    "continua na ampla concorrência"
)


def retirada(etapa="Heteroidentificação", motivo=MOTIVO):
    return {
        "id": uuid.uuid4(),
        "etapa": etapa,
        "habilitada": False,
        "retirada": True,
        "motivo": motivo,
    }


def test_a_retirada_nao_e_eliminacao():
    """SC-2333: com a ordem publicada, o degrau segue a classificação na ampla."""
    resultado = calcular(
        resultados_das_etapas=[retirada()],
        cartoes=[
            cartao(posicao=8),
            cartao(lista_id=PPI, lista="Pretos e pardos", classificada=False, motivo=MOTIVO),
        ],
    )

    assert resultado.codigo != situacao.ELIMINADO
    assert resultado.codigo == situacao.AGUARDANDO_CHAMADA
    texto = textos(resultado)
    assert "deixou de concorrer pela reserva de vagas" in texto
    assert "continua concorrendo pela ampla concorrência" in texto
    assert "8º lugar" in texto
    assert "eliminad" not in texto.lower()


def test_sem_ordem_publicada_a_linha_aparece_mesmo_assim():
    """FR-7024: o titular lê a reserva perdida antes da ordem sair."""
    resultado = calcular(resultados_das_etapas=[retirada()])

    assert resultado.codigo != situacao.ELIMINADO
    assert "deixou de concorrer pela reserva de vagas" in textos(resultado)


def test_a_eliminacao_continua_eliminado():
    """FR-7024: sob o efeito "elimina", a frase de sempre."""
    resultado = calcular(resultados_das_etapas=[eliminada(etapa="Heteroidentificação")])

    assert resultado.codigo == situacao.ELIMINADO


def test_retirada_e_depois_eliminada_e_eliminado():
    """FR-7011: a eliminação posterior vale para todas as listas, e a retirada não a atenua."""
    resultado = calcular(resultados_das_etapas=[retirada(), eliminada()])

    assert resultado.codigo == situacao.ELIMINADO
