"""Os três modelos com que a unidade começa (066, `D-008`, `FR-1260a`).

**Eles passam pela mesma validação que o modelo que a seleção escreve.** Um modelo inicial com
variável desconhecida chegaria à primeira prévia como recusa — e a primeira impressão da feature
seria um erro do próprio sistema.
"""

import pytest

from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.domain.modelos_iniciais import ASSUNTO_NEUTRO, MODELOS_INICIAIS
from processo_seletivo.avisos.domain.variaveis import usadas, validar


def test_sao_os_tres_nomeados_pela_spec():
    assert [nome for nome, _, _ in MODELOS_INICIAIS] == [
        "Divulgação de resultado",
        "Publicação retificadora",
        "Nova chamada publicada",
    ]


@pytest.mark.parametrize(("nome", "assunto", "corpo"), MODELOS_INICIAIS, ids=lambda v: v[:12])
def test_cada_um_passa_pela_validacao_do_modelo(nome, assunto, corpo):
    validar(assunto)
    validar(corpo)


@pytest.mark.parametrize(("nome", "assunto", "corpo"), MODELOS_INICIAIS, ids=lambda v: v[:12])
def test_o_assunto_e_neutro(nome, assunto, corpo):
    """`D-007`: o assunto aparece no celular, e não diz lista, modalidade nem procedimento."""
    assert assunto == ASSUNTO_NEUTRO
    for palavra in ("ppi", "cota", "reserva", "heteroidentifica", "modalidade", "lista"):
        assert palavra not in assunto.lower()


def test_o_terceiro_serve_a_chamada_e_os_dois_primeiros_ao_resultado():
    divulgacao, retificadora, chamada = (corpo for _, _, corpo in MODELOS_INICIAIS)

    validar(chamada, origem=nomes.CHAMADA)
    validar(divulgacao, origem=nomes.RESULTADO, publicacoes_citadas=2)
    validar(retificadora, origem=nomes.RESULTADO, publicacoes_citadas=1)
    assert "etapa" in usadas(divulgacao)


def test_nenhum_diz_a_situacao_de_alguem():
    for _, _, corpo in MODELOS_INICIAIS:
        for proibido in ("posição", "classificad", "aprovad", "eliminad", "sem posição"):
            assert proibido not in corpo.lower()
        assert "{area_do_candidato}" in corpo
