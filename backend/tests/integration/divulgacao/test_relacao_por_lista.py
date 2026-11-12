"""A relação das inscrições por lista de concorrência — revisão de 12/11/2026 da 148 (D-011).

**O Edital é publicado pelo caminho normal, com PcD, PPI e a Modalidade apontada como a ampla.** As
listas do ato vêm da derivação dos recortes da `122`, que só um Edital publicado exercita de
verdade: um conteúdo montado à mão provaria que o domínio reparte, e não que o ato lê os recortes
que a classificação lê.

A repartição das autodeclarações é entremeada — sem cota, PPI, PcD, PPI, a apontada —, para que
uma implementação que ordenasse a reservada pela posição no universo não passasse por acaso.
"""

import json

import pytest
from django.urls import reverse

from processo_seletivo.divulgacao.domain import inscricoes as dominio
from processo_seletivo.divulgacao.models import InscricaoNaPublicacao
from processo_seletivo.shared.canonical import canonical_sha256
from tests.fixtures.inscricoes_publicadas import (
    analisar,
    evento_de_recurso,
    inscrever_no,
    modalidade_ampla_apontada,
    modalidade_pcd,
    modalidade_ppi,
    montar,
    publicar,
)
from tests.unit.publicacoes.test_pdf import texto_de

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

SEED = 1490


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    cenario = montar(
        gestor, api_client, manager_headers, seed=SEED, codigo=str(SEED), com_cotas=True
    )
    cenario["inscricoes"] = inscrever_no(
        cenario,
        5,
        primeiro=601,
        modalidades={
            1: modalidade_ppi(SEED),
            2: modalidade_pcd(SEED),
            3: modalidade_ppi(SEED),
            4: modalidade_ampla_apontada(SEED),
        },
    )
    return cenario


def _listas(ato):
    (grupo,) = json.loads(bytes(ato.conteudo_publico))["perfis"]
    return {
        lista["lista"]: {
            "constam": [linha["protocolo"] for linha in lista["constam"]],
            "nao_constam": lista["nao_constam"],
        }
        for lista in grupo["listas"]
    }


def test_a_relacao_de_recebidas_reparte_por_lista_e_grava_cada_inscricao_uma_vez(client, cenario):
    """SC-1709 e SC-1711: cotista nas duas listas, apontada só na ampla, uma linha por inscrição."""
    sem_cota, ppi_1, pcd, ppi_2, apontada = cenario["inscricoes"]

    ato = publicar(cenario, "RECEBIDAS", chave="por-lista-recebidas")

    listas = _listas(ato)
    assert list(listas) == [
        "Ampla concorrência",
        "Pessoas com deficiência",
        "Pretos, pardos e indígenas",
    ]
    assert listas["Ampla concorrência"]["constam"] == [
        inscricao.protocolo for inscricao in cenario["inscricoes"]
    ]
    assert listas["Pessoas com deficiência"]["constam"] == [pcd.protocolo]
    assert listas["Pretos, pardos e indígenas"]["constam"] == [ppi_1.protocolo, ppi_2.protocolo]
    # A apontada como a ampla não abre lista, e quem a declarou não aparece em reservada nenhuma.
    reservadas = (
        listas["Pessoas com deficiência"]["constam"]
        + listas["Pretos, pardos e indígenas"]["constam"]
    )
    assert apontada.protocolo not in reservadas
    assert sem_cota.protocolo not in reservadas
    # FR-5444: o total e as linhas contam inscrições, e não aparições.
    assert ato.quantidade == 5
    assert InscricaoNaPublicacao.objects.filter(publicacao=ato).count() == 5

    texto_publico = bytes(ato.conteudo_publico).decode()
    for identidade in (modalidade_pcd(SEED), modalidade_ppi(SEED), modalidade_ampla_apontada(SEED)):
        assert identidade not in texto_publico

    texto = texto_de(bytes(ato.documento))
    assert "Ampla concorrência (5)" in texto
    assert "Pessoas com deficiência (1)" in texto
    assert "Pretos, pardos e indígenas (2)" in texto

    corpo = client.get(reverse("portal:publicacao-das-inscricoes", args=[ato.id])).content.decode()
    assert "Ampla concorrência (5)</h3>" in corpo
    assert "Pretos, pardos e indígenas (2)</h3>" in corpo
    assert dominio.FRASE_DAS_LISTAS in corpo
    assert 'style="' not in corpo


def test_o_preliminar_conta_a_indeferida_em_cada_lista_a_que_ela_pertence(cenario, gestor):
    """FR-5443: a cotista indeferida conta na ampla e na PPI, e não é nomeada em nenhuma."""
    sem_cota, ppi_1, pcd, ppi_2, apontada = cenario["inscricoes"]
    analisar(
        cenario,
        gestor,
        [
            (sem_cota, "FAVORAVEL"),
            (ppi_1, "DESFAVORAVEL"),
            (pcd, "FAVORAVEL"),
            (ppi_2, "FAVORAVEL"),
            (apontada, "FAVORAVEL"),
        ],
        sufixo="por-lista",
    )

    ato = publicar(
        cenario, "PRELIMINAR", prazo=evento_de_recurso(SEED), chave="por-lista-preliminar"
    )

    listas = _listas(ato)
    assert listas["Ampla concorrência"]["nao_constam"] == 1
    assert listas["Pretos, pardos e indígenas"] == {
        "constam": [ppi_2.protocolo],
        "nao_constam": 1,
    }
    assert listas["Pessoas com deficiência"]["nao_constam"] == 0
    texto_publico = bytes(ato.conteudo_publico).decode()
    assert ppi_1.protocolo not in texto_publico
    assert ppi_1.nome not in texto_publico
    assert ato.quantidade == 5


def test_o_ato_no_formato_anterior_a_revisao_continua_como_foi_publicado(
    client, cenario, monkeypatch
):
    """SC-1710 e FR-5447: o ato de 11/11, sem lista, tem os mesmos bytes e é lido por Perfil.

    O formato antigo é reproduzido trocando, só na publicação, a função que monta o conteúdo pela
    que dobra as listas de volta no Perfil — que é o que o comando gravava antes da revisão.
    """
    original = dominio.conteudo_publico

    def como_em_11_11(**argumentos):
        conteudo = original(**argumentos)
        conteudo["perfis"] = [
            {
                "perfil": grupo["perfil"],
                "constam": grupo["listas"][0]["constam"],
                "nao_constam": grupo["listas"][0]["nao_constam"],
            }
            for grupo in conteudo["perfis"]
        ]
        return conteudo

    monkeypatch.setattr(dominio, "conteudo_publico", como_em_11_11)
    ato = publicar(cenario, "RECEBIDAS", chave="formato-anterior")
    monkeypatch.undo()

    conteudo = json.loads(bytes(ato.conteudo_publico))
    assert "listas" not in conteudo["perfis"][0]
    assert ato.conteudo_publico_hash == canonical_sha256(conteudo)

    resposta = client.get(reverse("portal:publicacao-das-inscricoes", args=[ato.id]))
    corpo = resposta.content.decode()
    assert resposta.status_code == 200
    for inscricao in cenario["inscricoes"]:
        assert inscricao.protocolo in corpo
    assert "<h3" not in corpo
    assert dominio.FRASE_DAS_LISTAS not in corpo
    texto = texto_de(bytes(ato.documento))
    assert "Ampla concorrência" not in texto
    pdf = client.get(reverse("portal:publicacao-das-inscricoes-documento", args=[ato.id]))
    assert pdf.content == bytes(ato.documento)


def test_a_modalidade_ampla_sem_apontamento_nao_vira_uma_segunda_ampla(
    gestor, api_client, manager_headers
):
    """FR-5440a: o Edital do acervo declara "Ampla concorrência" sem apontá-la como a ampla.

    A regra dos recortes a trata como reservada — e o ato a mantém como lista, como a classificação
    —, mas o título leva o código, para que o leitor não veja duas amplas.
    """
    seed = 1491
    cenario = montar(
        gestor,
        api_client,
        manager_headers,
        seed=seed,
        codigo=str(seed),
        com_cotas=True,
        apontar_a_ampla=False,
    )
    inscrever_no(cenario, 2, primeiro=651, modalidades={1: modalidade_ampla_apontada(seed)})

    ato = publicar(cenario, "RECEBIDAS", chave="ampla-sem-apontamento")

    # A ordem das reservadas é a da versão publicada, que lista as Modalidades pelo código; o que o
    # caso prende é o título: uma só "Ampla concorrência", e a declarada distinguida pelo código.
    titulos = list(_listas(ato))
    assert titulos == [
        "Ampla concorrência",
        "Ampla concorrência (AC)",
        "Pessoas com deficiência",
        "Pretos, pardos e indígenas",
    ]
    assert "Ampla concorrência (AC) (1)" in texto_de(bytes(ato.documento))
