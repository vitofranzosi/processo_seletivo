"""A fonte de consulta num Edital que nasce no catálogo da `069` (070, `FR-1417`, `FR-1431`).

Os Editais do corpus nasceram no catálogo da `054`, e é com ele que o corpus se republica
(`tests/fixtures/corpus.py`). Todo Edital novo, porém, nasce agora no catálogo da `069`: as mesmas
chaves, com outros títulos e outra ordem, e o documento por perguntas. A consulta lê pelas chaves,
e a localização diz o título que o Edital publicou — este caso prende as duas coisas.
"""

import pytest
from django.utils import timezone

from processo_seletivo.duvidas.application.consultar import consultar, contexto
from processo_seletivo.duvidas.domain import catalogo
from processo_seletivo.editais.domain import secoes
from tests.fixtures.corpus import publicar_do_corpus

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def test_toda_pergunta_responde_e_a_secao_e_dita_pelo_titulo_da_069(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="catalogo-069", catalogo_vigente=True)
    agora = timezone.now()
    lido = contexto(edital_id=edital.id, instante=agora)
    titulos = {secao["key"]: secao["title"] for secao in lido.conteudo["sections"]}
    assert titulos["recursos"] == secoes.POR_CHAVE["recursos"].title == "Como recorrer?"

    secoes_citadas = set()
    for pergunta in catalogo.oferecidas(lido.conteudo):
        perfil = "INF-BJN" if pergunta.parametros else None
        resposta = consultar(
            edital_id=edital.id, instante=agora, pergunta=pergunta.codigo, perfil=perfil
        )
        secoes_citadas |= {
            r.localizacao for r in resposta.referencias if r.localizacao.startswith("Seção")
        }
    assert "Seção “Como recorrer?”" in secoes_citadas
    assert not [lugar for lugar in secoes_citadas if "Dos Recursos" in lugar]
