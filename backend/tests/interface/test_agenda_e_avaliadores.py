"""A remarcação diz quem avalia e quem fica em conflito (179, FR-8209, FR-8232, Q-A).

A agenda pode criar conflito, mas nunca em silêncio: a tela diz quem avalia a pessoa, marca os
horários livres em que um avaliador dela já tem entrevista, e a confirmação anuncia quem passa a ter
duas. Confirmar sem o anúncio volta com ele; confirmar com ele remarca. A Atribuição não muda, e a
trilha do ato guarda quem ficou em conflito.
"""

import re

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.agendamento.domain.nomes import REMARCACAO_DA_AGENDA
from processo_seletivo.agendamento.models import AtoDaAgenda
from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avaliacoes.models import Atribuicao
from tests.fixtures.avaliacoes_com_agenda import agenda, atribuir, comissao, por_sessao
from tests.fixtures.comissao import inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def presidente(client, seletor_ligado):
    identificar(client, "carlos", ["gestor"])
    return client


@pytest.fixture
def cenario(gestor, edital_a, etapa_a2):
    """Duas bancas de oito horários (08:00 a 09:45); quatro pessoas em cada uma, das 08:00 às 08:45.
    A Ana avalia as da Banca 01; o Bruno, as da Banca 02. Os horários das 09:00 em diante estão
    livres nas duas bancas."""
    inscrever(edital_a, 8)
    agenda(gestor, edital_a, etapa_a2, quantas_bancas=2)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana", "bruno"])
    banca1, banca2 = (v for _, v in sorted(por_sessao(edital_a, etapa_a2).items()))
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca1, chave="ana")
    atribuir(gestor, edital_a, etapa_a2, [membros["bruno"]], banca2, chave="bruno")
    return membros, banca1, banca2


def _url(edital, etapa, inscricao):
    return reverse("interface:agenda-remarcar", args=[edital.id, etapa, inscricao.id])


def _opcoes(corpo):
    """`[(valor, hora, marca)]` dos horários livres do seletor do dia mostrado."""
    return re.findall(
        r'<input type="radio" name="horario" value="([^"]+)"[^>]*><span>([^<]+)</span>'
        r'(?:<span class="ocupado-na-opcao">([^<]+)</span>)?',
        corpo,
    )


def _campo(corpo, nome):
    return re.search(rf'name="{nome}" value="([^"]*)"', corpo).group(1)


def _remarcar(cliente, url, horario, assinatura, chave):
    return cliente.post(
        url,
        {
            "horario": horario,
            "motivo": "falha de conexão",
            "chave_idempotencia": chave,
            "assinatura_dos_conflitos": assinatura,
        },
    )


def test_a_tela_diz_quem_avalia(presidente, edital_a, etapa_a2, cenario):
    _, banca1, _ = cenario
    corpo = presidente.get(_url(edital_a, etapa_a2, banca1[0])).content.decode()
    assert "Avaliam esta pessoa: ana." in corpo
    assert all(not marca for _, _, marca in _opcoes(corpo)), "livres das 09:00 em diante"


def test_sem_conflito_a_remarcacao_passa_de_primeira(presidente, edital_a, etapa_a2, cenario):
    _, banca1, _ = cenario
    url = _url(edital_a, etapa_a2, banca1[0])
    corpo = presidente.get(url).content.decode()
    valor = _opcoes(corpo)[0][0]
    resposta = _remarcar(presidente, url, valor, _campo(corpo, "assinatura_dos_conflitos"), "r1")
    assert resposta.status_code == 302
    assert AtoDaAgenda.objects.filter(especie="REMARCACAO").count() == 1


def test_o_conflito_criado_pela_remarcacao_e_dito_conferido_e_registrado(
    presidente, gestor, edital_a, etapa_a2, cenario
):
    """O caso de Q-A, de ponta a ponta.

    A Ana tem a primeira da Banca 01 às 08:00. Ela passa a avaliar também a última da Banca 02
    (08:45), que é remarcada para as 08:00 da Banca 02 — liberada antes, levando a primeira de lá
    para as 09:45. Às 08:00, a Ana fica em dois lugares.
    """
    membros, banca1, banca2 = cenario
    # 1. Libera as 08:00 da Banca 02.
    url_b2 = _url(edital_a, etapa_a2, banca2[0])
    corpo = presidente.get(url_b2).content.decode()
    ultimo = _opcoes(corpo)[-1][0]
    liberou = _remarcar(presidente, url_b2, ultimo, _campo(corpo, "assinatura_dos_conflitos"), "l")
    assert liberou.status_code == 302
    # 2. A Ana passa a avaliar a última da Banca 02 (08:45, livre para ela). Gravada direto: a Etapa
    #    da fixture prevê um avaliador por pessoa, e o lote recusaria a segunda pelo teto.
    alvo = banca2[3]
    Atribuicao.objects.create(
        membro=membros["ana"],
        edital=edital_a,
        etapa_id=etapa_a2,
        inscricao=alvo,
        criado_em=timezone.now(),
        criado_por=gestor.subject,
    )
    # 3. Na remarcação do alvo, as 08:00 vêm marcadas: a Ana tem entrevista ali.
    url = _url(edital_a, etapa_a2, alvo)
    corpo = presidente.get(url).content.decode()
    assert "Avaliam esta pessoa: ana e bruno." in corpo
    oito = next(o for o in _opcoes(corpo) if o[1] == "08:00")
    assert oito[2] == "ana: outra entrevista"
    # Confirmar com a assinatura de antes da escolha: volta, dizendo quem fica em conflito.
    recusa = _remarcar(presidente, url, oito[0], _campo(corpo, "assinatura_dos_conflitos"), "c1")
    assert recusa.status_code == 409
    texto = recusa.content.decode()
    assert "ana passa a ter duas entrevistas às 08:00 de 23/11" in texto
    assert AtoDaAgenda.objects.filter(especie="REMARCACAO").count() == 1
    # Confirmar com o anúncio: remarca; a Atribuição fica; a trilha guarda a Ana.
    feita = _remarcar(
        presidente,
        url,
        oito[0],
        _campo(texto, "assinatura_dos_conflitos"),
        _campo(texto, "chave_idempotencia"),
    )
    assert feita.status_code == 302
    assert AtoDaAgenda.objects.filter(especie="REMARCACAO").count() == 2
    assert Atribuicao.objects.filter(membro=membros["ana"], inscricao=alvo, ativo=True).exists()
    evento = (
        RegistroAuditoria.objects.filter(operation=REMARCACAO_DA_AGENDA)
        .order_by("-occurred_at")
        .first()
    )
    assert evento.detalhe["avaliadores_em_conflito"] == ["ana"]
    # E a pendência fica visível na agenda publicada.
    publicada = presidente.get(
        reverse("interface:agenda-publicada", args=[edital_a.id, etapa_a2])
    ).content.decode()
    assert "1 conflito de horário" in publicada
    assert "ana, às 08:00 de 23/11 (Banca 01 e Banca 02)" in publicada


def test_sem_a_funcao_injetada_a_remarcacao_e_a_da_167(gestor, edital_a, etapa_a2, cenario):
    """O comando sem `conflitos_no_horario` não confere nem registra conflito: é o de antes."""
    from processo_seletivo.agendamento.application import atos_individuais, leitura

    _, banca1, _ = cenario
    agenda_ = leitura.agenda_da_etapa(edital_a, etapa_a2)
    livre = leitura.montagem(edital_a, etapa_a2, agenda_).livres[0]
    atos_individuais.remarcar(
        actor=gestor,
        edital=edital_a,
        etapa_id=etapa_a2,
        inscricao_id=banca1[0].id,
        inicio=livre.inicio,
        banca_id=livre.banca_id,
        motivo="sem função",
        idempotency_key="sem-funcao",
    )
    evento = RegistroAuditoria.objects.filter(operation=REMARCACAO_DA_AGENDA).latest("occurred_at")
    assert evento.detalhe["avaliadores_em_conflito"] == []
    assert timezone.now() >= evento.occurred_at
