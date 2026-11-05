"""Os mesmos recortes em toda superfície, e o acervo excedente à parte (122).

O cenário é o do Edital 35/2026 que motivou a feature: um Perfil com AC, PPI e PcD, AC apontada como
a ampla, e um marco por sorteio. Os recortes operacionais são três — a ampla, PPI e PcD —, e cada
superfície tem de dizer três.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.sorteios.application.selectors import marcos_sorteados_em_todos_os_recortes
from tests.fixtures.recorte_excedente import LISTA_AC, certame_com_ac
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

FRASE_DA_APONTADA = "que este Perfil aponta como a ampla concorrência, não tem sorteio próprio"


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    return certame_com_ac(gestor, api_client, manager_headers, process_payload, prefixo="tela")


def _tela_do_sorteio(client, certame):
    resposta = client.get(
        reverse("interface:sorteio", args=[certame["edital"].id, certame["marco"]])
    )
    assert resposta.status_code == 200
    return resposta.content.decode()


def _recortes_da_tela_do_sorteio(corpo):
    secao = corpo.split('id="titulo-recortes"', 1)[1]
    secao = secao.split('id="titulo-historico-excedente"', 1)[0]
    return re.findall(r"<h3>(.*?)</h3>", secao)


# --- US1 · FR-3893, FR-3895, FR-3896 -------------------------------------------------------------


class TestOSorteioTrabalhaNosTresRecortes:
    def test_a_tela_mostra_tres_recortes_e_nenhum_bloco_de_ac(self, client, certame):
        identificar(client, "maria", [])

        corpo = _tela_do_sorteio(client, certame)
        recortes = _recortes_da_tela_do_sorteio(corpo)

        assert len(recortes) == 3, recortes
        assert recortes[0].startswith("Todos os inscritos")
        assert not any("(AC)" in nome for nome in recortes)
        assert FRASE_DA_APONTADA in corpo

    def test_o_marco_esta_sorteado_sem_esperar_por_ac(self, certame):
        """FR-3896: a Retificação pergunta isso, e não pode esperar por recorte que não existe."""
        conteudo = effective_version(edital_id=certame["edital"].id).content

        sorteados = marcos_sorteados_em_todos_os_recortes(certame["edital"], conteudo)

        assert str(certame["marco"]) in {str(marco) for marco in sorteados}

    def test_perfil_sem_apontamento_trata_ac_como_recorte(
        self, client, gestor, api_client, manager_headers, process_payload, seletor_ligado
    ):
        """Caso-limite: sem apontamento, a Modalidade "AC" é recorte como as outras (FR-3894)."""
        sem_apontamento = certame_com_ac(
            gestor, api_client, manager_headers, process_payload, apontada=False, prefixo="sem"
        )
        identificar(client, "maria", [])

        corpo = _tela_do_sorteio(client, sem_apontamento)

        assert len(_recortes_da_tela_do_sorteio(corpo)) == 4
        assert FRASE_DA_APONTADA not in corpo
        assert LISTA_AC in sem_apontamento["atos"]


# --- US2 · FR-3899, FR-3901, FR-3904, FR-3906 a FR-3908 ------------------------------------------

_SECAO_CLASSIFICACAO = re.compile(
    r'<section aria-labelledby="classificacao-titulo".*?</section>', re.DOTALL
)


@pytest.fixture
def com_acervo(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    """Os três recortes sorteados **e** o ato de AC do caminho antigo — o Edital 35/2026."""
    return certame_com_ac(
        gestor, api_client, manager_headers, process_payload, acervo=True, prefixo="acervo"
    )


def _previa(certame, lista):
    ato = certame["atos"][lista]
    return reverse(
        "interface:previa-de-publicacao", args=[certame["edital"].id, certame["marco"], ato.id]
    )


def _quadro(certame):
    return reverse("interface:marco", args=[certame["edital"].id, certame["marco"]])


class TestQuemDivulgaEncontraCadaRecorte:
    def test_a_pagina_do_edital_tem_um_caminho_de_divulgacao_por_marco(self, client, com_acervo):
        identificar(client, "paula.publicadora", ["publicador"])

        corpo = client.get(reverse("interface:detalhe", args=[com_acervo["edital"].id]))
        secao = _SECAO_CLASSIFICACAO.search(corpo.content.decode()).group(0)

        assert secao.count(">divulgar o resultado</a>") == 1
        assert f'href="{_quadro(com_acervo)}#divulgacao"' in secao
        assert "previa" not in secao

    def test_o_publicador_puro_chega_a_previa_de_cada_recorte_pelo_quadro(self, client, com_acervo):
        """SC-1167: página do Edital → quadro → prévia, em dois cliques, para os três recortes."""
        identificar(client, "paula.publicadora", ["publicador"])

        quadro = client.get(_quadro(com_acervo))

        assert quadro.status_code == 200
        corpo = quadro.content.decode()
        for lista in (None, *[k for k in com_acervo["atos"] if k not in (None, LISTA_AC)]):
            assert _previa(com_acervo, lista) in corpo, lista
        assert _previa(com_acervo, LISTA_AC) not in corpo

    def test_o_recorte_divulgado_leva_aos_resultados_divulgados(self, client, com_acervo):
        from tests.fixtures.recorte_excedente import divulgar

        divulgar(com_acervo, None, chave="divulgar-ampla-quadro")
        identificar(client, "paula.publicadora", ["publicador"])

        corpo = client.get(_quadro(com_acervo)).content.decode()

        assert _previa(com_acervo, None) not in corpo
        assert (
            reverse(
                "interface:publicacoes-do-marco",
                args=[com_acervo["edital"].id, com_acervo["marco"]],
            )
            in corpo
        )

    def test_a_previa_do_ato_excedente_explica_e_nao_oferece_o_botao(self, client, com_acervo):
        identificar(client, "paula.publicadora", ["publicador"])

        corpo = client.get(_previa(com_acervo, LISTA_AC)).content.decode()

        assert "Este ato está fora da operação atual" in corpo
        assert "dava lista própria à Modalidade apontada como a ampla" in corpo
        assert "Publicar este resultado" not in corpo

    def test_a_tela_do_ato_excedente_explica_e_nao_oferece_publicar(self, client, com_acervo):
        identificar(client, "maria", ["publicador"])
        ato = com_acervo["atos"][LISTA_AC]

        corpo = client.get(
            reverse(
                "interface:ato-de-ordenacao",
                args=[com_acervo["edital"].id, com_acervo["marco"], ato.id],
            )
        ).content.decode()

        assert "Fora da operação atual." in corpo
        assert _previa(com_acervo, LISTA_AC) not in corpo

    def test_a_tela_do_sorteio_nao_oferece_publicar_o_ato_excedente(self, client, com_acervo):
        identificar(client, "maria", ["publicador"])

        corpo = _tela_do_sorteio(client, com_acervo)

        assert _previa(com_acervo, LISTA_AC) not in corpo
        assert _previa(com_acervo, None) in corpo


# --- US4 · FR-3902 a FR-3905, FR-3916 ------------------------------------------------------------


@pytest.fixture
def tornado(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    """AC operacional, sorteada e divulgada; depois uma Retificação a aponta como a ampla."""
    from tests.fixtures.recorte_excedente import divulgar, retificar_o_apontamento

    certame = certame_com_ac(
        gestor, api_client, manager_headers, process_payload, apontada=False, prefixo="torn"
    )
    divulgar(certame, LISTA_AC, chave="divulgar-ac-operacional")
    retificar_o_apontamento(api_client, certame["edital"], LISTA_AC, suffix="aponta-ac")
    return certame


def _historico(corpo):
    if 'id="titulo-historico-excedente"' not in corpo:
        return ""
    return corpo.split('id="titulo-historico-excedente"', 1)[1].split("</section>", 1)[0]


class TestOAcervoContinuaConsultavelEExplicado:
    def test_o_acervo_nascido_aparece_a_parte_com_a_frase_dele(self, client, com_acervo):
        identificar(client, "maria", [])

        corpo = _tela_do_sorteio(client, com_acervo)
        historico = _historico(corpo)

        assert len(_recortes_da_tela_do_sorteio(corpo)) == 3
        for especie in ("Relação de habilitados", "Sorteio", "Ato de classificação"):
            assert especie in historico
        assert "dava lista própria à Modalidade apontada como a ampla" in historico
        assert "<button" not in historico
        assert "<form" not in historico

    def test_o_acervo_tornado_nomeia_a_retificacao(self, client, tornado):
        identificar(client, "maria", [])

        corpo = _tela_do_sorteio(client, tornado)
        historico = _historico(corpo)

        assert len(_recortes_da_tela_do_sorteio(corpo)) == 3
        assert "Resultado divulgado" in historico
        assert "Produzido quando esta Modalidade tinha recorte próprio" in historico
        assert re.search(r"A Retificação nº \d+ passou a apontá-la", historico)

    def test_resultados_divulgados_marca_a_publicacao_excedente(self, client, tornado):
        identificar(client, "maria", ["publicador"])

        corpo = client.get(
            reverse("interface:publicacoes-do-marco", args=[tornado["edital"].id, tornado["marco"]])
        ).content.decode()

        assert corpo.count("Fora da operação atual.") == 1

    def test_sem_acervo_nao_ha_secao(self, client, certame):
        identificar(client, "maria", [])

        assert _historico(_tela_do_sorteio(client, certame)) == ""

    def test_quem_nao_alcanca_o_marco_nao_ve_o_registro(self, client, com_acervo):
        identificar(client, "estranho", [])

        resposta = client.get(
            reverse("interface:sorteio", args=[com_acervo["edital"].id, com_acervo["marco"]])
        )

        assert "Registros fora da operação atual" not in resposta.content.decode()


class TestORelatorioDoEditalContaOsRecortesOperacionais:
    def _fatos(self, certame):
        from django.utils import timezone

        from processo_seletivo.interface.relatorio_do_edital import (
            fatos_do_edital,
            leitura_consistente,
        )

        with leitura_consistente():
            return fatos_do_edital(certame["edital"], agora=timezone.now())

    def test_o_ato_excedente_nao_divulgado_nao_vira_linha_nem_pendencia(self, com_acervo):
        """FR-3916: três linhas, nenhuma marcada, e a pendência é só a do definitivo que falta."""
        from processo_seletivo.processos.application.pendencias_do_edital import (
            DEFINITIVO_NAO_PUBLICADO,
        )
        from tests.fixtures.recorte_excedente import divulgar

        for indice, lista in enumerate(k for k in com_acervo["atos"] if k != LISTA_AC):
            divulgar(com_acervo, lista, chave=f"rel-{indice}")

        fatos = self._fatos(com_acervo)

        (perfil,) = [p for p in fatos.perfis if p.listas]
        assert len(perfil.listas) == 3
        assert not any("fora da operação" in linha.lista for linha in perfil.listas)
        assert [p.tipo for p in fatos.pendencias if p.marco] == [DEFINITIVO_NAO_PUBLICADO]

    def test_a_publicacao_excedente_feita_aparece_marcada(self, tornado):
        fatos = self._fatos(tornado)

        (perfil,) = [p for p in fatos.perfis if p.listas]
        marcadas = [linha for linha in perfil.listas if "fora da operação atual" in linha.lista]
        assert len(marcadas) == 1


# --- SC-1166 · seis superfícies, o mesmo número -------------------------------------------------


def test_seis_superficies_contam_os_mesmos_tres_recortes(com_acervo):
    """SC-1166: sorteio, condução, resumo, ocupação, Supervisão e relatório dizem três."""
    from django.utils import timezone

    from processo_seletivo.interface import conducao_do_marco, supervisao
    from processo_seletivo.interface.relatorio_do_edital import (
        fatos_do_edital,
        leitura_consistente,
    )
    from processo_seletivo.ocupacao.application.selectors import (
        recortes_do_marco as recortes_da_ocupacao,
    )
    from processo_seletivo.sorteios.application.previa import recortes_do_marco
    from tests.fixtures.recorte_excedente import divulgar

    edital, perfil_id, marco_id = com_acervo["edital"], com_acervo["perfil"], com_acervo["marco"]
    conteudo = effective_version(edital_id=edital.id).content
    perfil = next(p for p in conteudo["profiles"] if str(p["id"]) == str(perfil_id))
    marco = next(m for m in perfil["classificationMilestones"] if str(m["id"]) == str(marco_id))
    for indice, lista in enumerate(k for k in com_acervo["atos"] if k != LISTA_AC):
        divulgar(com_acervo, lista, chave=f"seis-{indice}")
    with leitura_consistente():
        fatos = fatos_do_edital(edital, agora=timezone.now())

    contagens = {
        "sorteio": len(
            recortes_do_marco(edital=edital, perfil_id=perfil_id, marco_id=marco_id)["recortes"]
        ),
        "conducao": len(conducao_do_marco.recortes_do_marco(conteudo, perfil)),
        "resumo": conducao_do_marco.resumo_dos_marcos(edital, conteudo)[str(marco_id)]["recortes"],
        "ocupacao": len(
            recortes_da_ocupacao(edital=edital, perfil_id=perfil_id, marco_id=marco_id)
        ),
        "supervisao": len(supervisao.listas_do_marco(perfil, marco, conteudo)),
        "relatorio": len(next(p for p in fatos.perfis if p.listas).listas),
    }

    assert set(contagens.values()) == {3}, contagens
