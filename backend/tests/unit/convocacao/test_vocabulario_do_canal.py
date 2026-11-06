"""A palavra da comunicação segue o canal (125, US3, FR-3998 a FR-4004).

**Publicada na publicação, enviada na mensagem** (3ª decisão do usuário, 06/11/2026). A tabela é a
fonte só das frases (FR-4004); estes casos prendem que nenhuma frase da publicação fale de envio, e
que a mensagem continue dizendo o que sempre disse (FR-4002).
"""

from dataclasses import fields

import pytest

from processo_seletivo.convocacao.domain import vocabulario_do_canal as v
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    FORMA_POR_MENSAGEM_INDIVIDUAL,
    FORMA_POR_PUBLICACAO,
)

FRASES = [f.name for f in fields(v.Canal) if f.name != "publicacao"]
ENVIO = ("envio", "enviada", "enviado", "emitir", "emissão", "mensagem pode ter saído")


@pytest.mark.parametrize("campo", FRASES)
def test_a_publicacao_nao_fala_de_envio(campo):
    frase = getattr(v.PUBLICACAO, campo).lower()

    assert not any(palavra in frase for palavra in ENVIO), frase


@pytest.mark.parametrize("campo", FRASES)
def test_a_mensagem_nao_fala_de_publicacao(campo):
    assert "publica" not in getattr(v.MENSAGEM, campo).lower()


def test_a_frase_do_prazo_nao_iniciado_e_a_de_sempre_na_mensagem():
    """FR-3999: a da mensagem é, palavra por palavra, a da FR-3749 da `118`."""
    assert v.MENSAGEM.prazo_nao_iniciado == (
        "O prazo ainda não começou a correr: ele conta a partir do envio da comunicação."
    )
    assert v.PUBLICACAO.prazo_nao_iniciado == (
        "O prazo ainda não começou a correr: ele conta a partir da publicação da convocação."
    )


def test_a_forma_escolhe_o_canal_e_sem_forma_vale_a_mensagem():
    assert v.canal(FORMA_POR_PUBLICACAO) is v.PUBLICACAO
    assert v.canal(FORMA_POR_MENSAGEM_INDIVIDUAL) is v.MENSAGEM
    assert v.canal(None) is v.MENSAGEM


def test_a_gestao_diz_que_o_candidato_ainda_nao_ve():
    """D-007: na publicação sem registro, o operador lê que o candidato ainda não vê."""
    assert "o candidato ainda não vê" in v.PUBLICACAO.situacao_sem_comunicacao
    assert "candidato" not in v.MENSAGEM.situacao_sem_comunicacao
