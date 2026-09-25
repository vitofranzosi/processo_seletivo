"""A pendência nomeia a entidade e o campo, e não o caminho normativo (estudo de esforço, §12, 4).

O estudo registrou `IMPEDE A Etapa decisória deve publicar os rótulos do resultado em
/stages/id=3338c19f-…/rotuloFavoravel` como o ponto em que a interface mais exigia do operador o
modelo interno: UUID e nome de campo em inglês, numa frase dirigida a quem compõe o Edital.
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface.views import mensagem_legivel
from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_compor import etapa, etapas_form, eventos, perfis

ETAPA = "aaaaaaaa-0000-4000-8000-00000000e021"


@pytest.mark.django_db
@pytest.mark.integration
def test_a_revisao_nomeia_a_etapa_e_o_campo(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    client.post(etapa(edital, "etapas"), etapas_form(**{"etapa-0-forma": "DECISORIA"}))

    corpo = client.get(etapa(edital, "revisao")).content.decode()

    assert "«Etapa 1 — Prova didática», campo «Rótulo do resultado favorável»" in corpo
    assert "«Etapa 1 — Prova didática», campo «Rótulo do resultado desfavorável»" in corpo
    assert f"/stages/id={ETAPA}" not in corpo
    # E o caminho continua levando ao lugar: a tradução é da frase, e não do destino.
    assert f'href="{reverse("interface:compor-etapa", args=[edital.id, "etapas"])}' in corpo


GRUPOS = {f"/stages/id={ETAPA}": "Etapa Prova didática"}
CAMPOS = {
    f"/stages/id={ETAPA}/weight": ("Etapa Prova didática", "Peso"),
}


def test_campo_que_a_retificacao_nao_nomeia_recua_para_a_entidade():
    frase = mensagem_legivel(f"Algo falta em /stages/id={ETAPA}/campoNovo.", GRUPOS, CAMPOS)

    assert frase == "Algo falta em «Etapa Prova didática»."


def test_caminho_sem_entidade_conhecida_fica_como_esta():
    """Inventar nome seria pior do que mostrar o caminho."""
    frase = "Algo falta em /stages/id=outra/weight."

    assert mensagem_legivel(frase, GRUPOS, CAMPOS) == frase


def test_frase_sem_caminho_nao_muda():
    assert mensagem_legivel("Ao menos um Perfil é obrigatório.", GRUPOS, CAMPOS) == (
        "Ao menos um Perfil é obrigatório."
    )
