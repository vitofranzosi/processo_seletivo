"""O ato novo nomeia a pessoa sem masculino genérico; o ato publicado antes continua como foi.

A decisão é do usuário (2026-11-13, achado 9 da auditoria dos e-mails): só atos futuros. As palavras
moram no conteúdo gravado do ato, e a página e o PDF as leem dali. O ato anterior não as tem, e por
isso continua dizendo *"Candidato"* e *"cada candidato"* — na página e no documento oficial, que
não podem divergir (Princípio II).
"""

import json
from pathlib import Path

import pytest
from django.urls import reverse

from processo_seletivo.divulgacao.domain import vocabulario_dos_atos as vocabulario
from processo_seletivo.divulgacao.infrastructure.documento import render_resultado_pdf
from processo_seletivo.divulgacao.infrastructure.documento_das_inscricoes import (
    render_inscricoes_pdf,
)
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato
from tests.fixtures.inscricoes_publicadas import (
    analisar,
    evento_de_recurso,
    inscrever_no,
    montar,
    publicar,
)
from tests.interface.test_fluxo import texto_de_pdf_bytes

RAIZ = Path(__file__).resolve().parents[3] / "processo_seletivo"


def _conteudo(ato):
    return json.loads(bytes(ato.conteudo_publico).decode("utf-8"))


def _sem(dicionario, *chaves):
    return {chave: valor for chave, valor in dicionario.items() if chave not in chaves}


# --- A leitura, sem banco ----------------------------------------------------------------------


def test_o_ato_sem_as_palavras_gravadas_diz_as_do_dia_em_que_foi_publicado():
    assert vocabulario.rotulo_da_pessoa({}) == "Candidato"
    assert vocabulario.quem_consulta({}) == "cada candidato"
    assert vocabulario.rotulo_da_pessoa({"rotulo_da_pessoa": "Nome"}) == "Nome"
    assert vocabulario.quem_consulta({"quem_consulta": "cada pessoa"}) == "cada pessoa"


@pytest.mark.parametrize(
    "modelo",
    [
        "portal/templates/portal/resultado.html",
        "portal/templates/portal/publicacao_das_inscricoes.html",
    ],
)
def test_a_pagina_nao_escreve_o_rotulo_le_o_do_ato(modelo):
    """O rótulo escrito no modelo valeria para todo ato, inclusive o já publicado."""
    fonte = (RAIZ / modelo).read_text(encoding="utf-8")
    assert ">Candidato<" not in fonte and 'data-rotulo="Candidato"' not in fonte
    assert "cada candidato consulta" not in fonte
    assert "{{ rotulo_da_pessoa }}" in fonte


# --- A publicação das inscrições (148) ---------------------------------------------------------


@pytest.mark.django_db(transaction=True)
class TestAsInscricoes:
    @pytest.fixture
    def preliminar(self, gestor, api_client, manager_headers):
        cenario = montar(gestor, api_client, manager_headers, seed=1530, codigo="1530")
        primeira, segunda = inscrever_no(cenario, 2, primeiro=531)
        analisar(cenario, gestor, [(primeira, "FAVORAVEL"), (segunda, "DESFAVORAVEL")], sufixo="v")
        return publicar(
            cenario, "PRELIMINAR", prazo=evento_de_recurso(cenario["seed"]), chave="vocab-p"
        )

    def test_o_ato_novo_grava_as_palavras_e_o_pdf_as_diz(self, preliminar):
        conteudo = _conteudo(preliminar)
        texto = texto_de_pdf_bytes(bytes(preliminar.documento))

        assert conteudo["rotulo_da_pessoa"] == "Nome"
        assert conteudo["quem_consulta"] == "cada pessoa"
        assert "Nome" in texto and "Candidato" not in texto
        assert "cada pessoa consulta a própria situação" in texto

    def test_a_pagina_diz_o_que_o_pdf_gravado_diz(self, client, preliminar):
        corpo = client.get(
            reverse("portal:publicacao-das-inscricoes", args=[preliminar.id])
        ).content.decode()

        assert '<th scope="col">Nome</th>' in corpo and 'data-rotulo="Nome"' in corpo
        assert ">Candidato<" not in corpo
        assert "cada pessoa consulta a própria situação" in corpo

    def test_o_ato_anterior_continua_dizendo_candidato(self, preliminar):
        """O conteúdo sem as chaves é o do ato publicado antes de 13/11."""
        anterior = _sem(_conteudo(preliminar), "rotulo_da_pessoa", "quem_consulta")
        texto = texto_de_pdf_bytes(render_inscricoes_pdf(anterior))

        assert "Candidato" in texto
        assert "cada candidato consulta a própria situação" in texto


# --- O resultado (017) -------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
class TestOResultado:
    @pytest.fixture
    def publicado(self, gestor, api_client, manager_headers, process_payload):
        cenario = montar_ato_publicavel(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            seed=65,
            codigo="0765",
            pontuacoes=("90.0000", "70.0000"),
            primeiro=1301,
        )
        return publicar_o_ato(cenario, chave="publicar-vocab")

    def test_o_ato_novo_grava_o_rotulo_no_cabecalho(self, publicado):
        conteudo = _conteudo(publicado)
        texto = texto_de_pdf_bytes(render_resultado_pdf(conteudo))

        assert set(conteudo) == {"cabecalho", "posicoes"}, "o primeiro nível é contrato da 017"
        assert conteudo["cabecalho"]["rotulo_da_pessoa"] == "Nome"
        assert "Nome" in texto and "Candidato" not in texto

    def test_a_pagina_diz_o_rotulo_do_ato(self, client, publicado):
        corpo = client.get(reverse("portal:resultado", args=[publicado.id])).content.decode()

        assert '<th scope="col">Nome</th>' in corpo and ">Candidato<" not in corpo

    def test_o_ato_anterior_continua_dizendo_candidato(self, publicado):
        conteudo = _conteudo(publicado)
        anterior = {**conteudo, "cabecalho": _sem(conteudo["cabecalho"], "rotulo_da_pessoa")}

        assert "Candidato" in texto_de_pdf_bytes(render_resultado_pdf(anterior))
