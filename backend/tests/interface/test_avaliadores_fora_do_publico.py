"""Quem avalia é informação interna (179, FR-8215, SC-2846, `D-007`).

Com nomes de avaliador semeados — nomes que não aparecem em nenhum outro lugar —, a página pública
da agenda, o documento PDF do ato, a área do candidato e o aviso de agenda ao candidato não contêm
nenhum. A gestão os mostra; o resto, não.
"""

import pytest
from django.urls import reverse

from processo_seletivo.agendamento.models import DocumentoDoAtoDaAgenda, HorarioPublicado
from processo_seletivo.avisos.models import Aviso
from processo_seletivo.comissoes.application.comissao import adicionar_membro
from tests.fixtures.avaliacoes_com_agenda import agenda, atribuir, por_sessao
from tests.fixtures.comissao import alocar_em, constituir, inscrever

pytestmark = [pytest.mark.django_db]

NOMES = ("Zuleica Avaliadora Oculta", "Wanderley Avaliador Oculto")


@pytest.fixture
def publicada_com_avaliadores(gestor, edital_a, etapa_a2):
    pessoas = inscrever(edital_a, 4)
    processo = edital_a.processo
    constituir(gestor, processo, [("presidencia-179", "PRESIDENTE")], prefixo="p")
    membros = []
    for indice, nome in enumerate(NOMES):
        membro, _ = adicionar_membro(
            actor=gestor,
            processo_id=processo.id,
            identity_subject=f"oculto-{indice}",
            display_label=nome,
            funcao="MEMBRO",
            idempotency_key=f"oculto-{indice}",
            correlation_id="teste",
        )
        alocar_em(gestor, processo, membro, edital_a, etapa_a2)
        membros.append(membro)
    ato = agenda(gestor, edital_a, etapa_a2, quantas_bancas=2)
    banca1, banca2 = (v for _, v in sorted(por_sessao(edital_a, etapa_a2).items()))
    atribuir(gestor, edital_a, etapa_a2, [membros[0]], banca1, chave="z")
    atribuir(gestor, edital_a, etapa_a2, [membros[1]], banca2, chave="w")
    return ato, pessoas


def _sem_nomes(texto):
    return not any(nome in texto for nome in NOMES) and "Avaliam" not in texto


def test_a_gestao_mostra_os_nomes(
    client, seletor_ligado, edital_a, etapa_a2, publicada_com_avaliadores
):
    from tests.interface.conftest import identificar

    identificar(client, "carlos", ["gestor"])
    corpo = client.get(
        reverse("interface:agenda-publicada", args=[edital_a.id, etapa_a2])
    ).content.decode()
    assert all(nome in corpo for nome in NOMES)


def test_a_pagina_publica_nao_tem_avaliador(client, publicada_com_avaliadores):
    ato, _ = publicada_com_avaliadores
    corpo = client.get(reverse("portal:agenda-da-etapa", args=[ato.agenda_id])).content.decode()
    assert "Agenda:" in corpo
    assert _sem_nomes(corpo)


def test_o_documento_do_ato_nao_tem_avaliador(publicada_com_avaliadores):
    ato, _ = publicada_com_avaliadores
    from tests.interface.test_fluxo import texto_de_pdf_bytes

    texto = texto_de_pdf_bytes(bytes(DocumentoDoAtoDaAgenda.objects.get(ato=ato).bytes))
    assert texto.strip()
    assert _sem_nomes(texto)


def test_o_aviso_ao_candidato_nao_tem_avaliador(publicada_com_avaliadores):
    ato, _ = publicada_com_avaliadores
    avisos = Aviso.objects.filter(
        id__in=HorarioPublicado.objects.filter(ato=ato).values("aviso_id")
    )
    assert avisos.exists()
    for aviso in avisos:
        assert _sem_nomes(aviso.assunto + aviso.corpo)


def test_a_area_do_candidato_nao_tem_avaliador(client, publicada_com_avaliadores):
    """A área mostra o bloco "Seu horário" de `horarios_da_inscricao`, que não lê Atribuição."""
    from processo_seletivo.agendamento.application.leitura import horarios_da_inscricao

    _, pessoas = publicada_com_avaliadores
    blocos = horarios_da_inscricao(pessoas[0])
    assert blocos and blocos[0].publicado
    texto = " ".join(str(vars(bloco)) for bloco in blocos)
    assert _sem_nomes(texto)
