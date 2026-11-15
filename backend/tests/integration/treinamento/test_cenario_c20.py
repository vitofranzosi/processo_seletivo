"""O cenário C20: a Entrevista com vinte participantes e a agenda vazia, para agendar (167).

O teste confere o que a ficha promete — a lista fechada, o período de segunda a quarta, a agenda sem
configurar, o cronograma na ordem do certame —, e o roteiro do guia (`guia-da-equipe.md`, C20):
com 20 + 10 minutos num dia de manhã e tarde, o simulador diz que faltam 4 horários, e o atalho do
dia seguinte resolve. O percurso inteiro — configurar, preencher, publicar com a autoridade da
carga, despachar e remarcar — corre pelos mesmos comandos das telas, como a presidência os
praticaria, e termina na verificação que acusa o cenário exercitado e na restauração que devolve a
agenda vazia.
"""

from datetime import time

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.agendamento.application import (
    atos_individuais,
    conferir,
    configurar,
    leitura,
    montar,
    publicar,
)
from processo_seletivo.agendamento.domain.horarios import Banca, Configuracao
from processo_seletivo.avisos.application.despacho import despachar
from processo_seletivo.avisos.domain import nomes as nomes_dos_avisos
from processo_seletivo.avisos.models import Aviso
from processo_seletivo.comissoes.domain.etapas import conteudo_vigente
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.treinamento import catalogo
from processo_seletivo.treinamento import construcao as k
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from tests.conftest import ator_institucional
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.treinamento import carregar, restaurar, verificar
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

MANHA_E_TARDE = ((time(8), time(12)), (time(13), time(17)))


@pytest.fixture
def c20(treinamento):
    treinamento.INTERFACE_SELETOR_IDENTIDADE = True
    saida = carregar("C20", autoridade=str(AUTORIDADE_DA_SUITE))
    assert "C20  CRIADO" in saida, saida
    edital = Edital.objects.get(processo=CenarioDeTreinamento.objects.get(codigo="C20").processo)
    return edital, _entrevista(edital)


def _entrevista(edital):
    (etapa,) = [
        etapa
        for etapa in conteudo_vigente(edital)["stages"]
        if etapa["name"] == k.NOME_DA_ENTREVISTA
    ]
    return etapa["id"]


def _do_guia(dias):
    """A configuração do roteiro: 20 minutos, 10 de intervalo, manhã e tarde, uma banca."""
    banca = Banca("nova-1", "Banca 1", "https://sala.exemplo/treinamento", 1)
    return Configuracao(
        "REMOTA",
        20,
        10,
        tuple((dia, MANHA_E_TARDE) for dia in dias),
        (banca,),
        "Entre na sala 5 minutos antes.",
    )


def test_a_entrevista_tem_vinte_participantes_e_a_agenda_vazia(c20):
    """A Prova consolidada fecha a lista: vinte participam, e nada da agenda existe ainda."""
    edital, etapa_id = c20
    participacao = leitura.participacao(edital, etapa_id)
    assert len(participacao.participantes) == catalogo.PARTICIPANTES_DO_C20
    assert not participacao.lista_aberta
    assert leitura.agenda_da_etapa(edital, etapa_id) is None


def test_o_periodo_da_entrevista_vai_de_segunda_a_quarta(c20):
    edital, etapa_id = c20
    etapa = next(e for e in conteudo_vigente(edital)["stages"] if e["id"] == etapa_id)
    primeiro, ultimo = leitura.periodo_da_etapa(edital, etapa)
    assert primeiro.weekday() == 0
    assert (ultimo - primeiro).days == catalogo.DIAS_DA_ENTREVISTA_DO_C20 - 1
    hoje = timezone.localtime(timezone.now(), ZONA).date()
    assert (primeiro - hoje).days >= catalogo.INICIO_DA_ENTREVISTA_DO_C20


def test_o_cronograma_se_le_na_ordem_do_certame(c20):
    """A Entrevista entre a Prova e o Resultado final, e não depois dele (`ordem_cronologica`)."""
    edital, _ = c20
    tipos = [
        evento["type"]
        for evento in sorted(conteudo_vigente(edital)["schedule"], key=lambda e: e["order"])
    ]
    assert tipos == ["Inscrições", "Prova objetiva", k.NOME_DA_ENTREVISTA, "Resultado final"]


def test_o_simulador_acusa_a_falta_e_o_dia_seguinte_a_resolve(c20, client):
    """O roteiro do guia, pela tela: faltam 4 com um dia; o atalho do dia seguinte cabe todos."""
    edital, etapa_id = c20
    etapa = next(e for e in conteudo_vigente(edital)["stages"] if e["id"] == etapa_id)
    primeiro, _ = leitura.periodo_da_etapa(edital, etapa)
    identificar(client, k.PRESIDENCIA, [])
    dados = {
        "forma": "REMOTA",
        "duracao": "20",
        "intervalo": "10",
        "orientacoes": "",
        "dia-0": primeiro.isoformat(),
        "dia-0-janela-0-inicio": "08:00",
        "dia-0-janela-0-fim": "12:00",
        "dia-0-janela-1-inicio": "13:00",
        "dia-0-janela-1-fim": "17:00",
        "banca-0-id": "",
        "banca-0-nome": "Banca 1",
        "banca-0-acesso": "https://sala.exemplo/treinamento",
    }
    rota = reverse("interface:agenda-capacidade", args=[edital.id, etapa_id])
    corpo = client.post(rota, dados, HTTP_HX_REQUEST="true").content.decode()
    assert "Faltam 4 horários para as 20 pessoas." in corpo
    assert "Acrescentar Ter.," in corpo

    rota = reverse("interface:agenda-configurar", args=[edital.id, etapa_id])
    corpo = client.post(
        rota, {**dados, "acao": "atalho-dia"}, HTTP_HX_REQUEST="true"
    ).content.decode()
    assert "Cabem todas as 20 pessoas. Sobram 12 horários." in corpo


def test_o_percurso_inteiro_e_a_restauracao(c20):
    """Configurar, preencher, publicar, despachar e remarcar; depois, verificar e restaurar."""
    edital, etapa_id = c20
    etapa = next(e for e in conteudo_vigente(edital)["stages"] if e["id"] == etapa_id)
    primeiro, _ = leitura.periodo_da_etapa(edital, etapa)
    segundo = primeiro + timezone.timedelta(days=1)
    presidencia = ator_institucional(k.PRESIDENCIA)

    configurar.salvar(
        actor=presidencia, edital=edital, etapa_id=etapa_id, configuracao=_do_guia([primeiro])
    )
    configurar.salvar(
        actor=presidencia,
        edital=edital,
        etapa_id=etapa_id,
        configuracao=_do_guia([primeiro, segundo]),
    )
    previa = montar.previa_do_preenchimento(actor=presidencia, edital=edital, etapa_id=etapa_id)
    montar.aplicar_preenchimento(
        actor=presidencia, edital=edital, etapa_id=etapa_id, assinatura=previa.assinatura
    )
    conferencia = conferir.conferencia(actor=presidencia, edital=edital, etapa_id=etapa_id)
    # A autoridade da carga, já usada pela publicação do Edital, está entre as que a conferência
    # oferece.
    assert str(AUTORIDADE_DA_SUITE) in {str(a.pk) for a in conferencia.autoridades}
    ato = publicar.publicar(
        actor=presidencia,
        edital=edital,
        etapa_id=etapa_id,
        idempotency_key="c20-publicar-agenda",
        autoridade_id=AUTORIDADE_DA_SUITE,
        veiculo="GPS",
        declaracao="item 9.3 do Edital",
        assinatura=conferencia.assinatura,
    )
    avisos = Aviso.objects.filter(edital=edital, origem=nomes_dos_avisos.AGENDA)
    assert avisos.count() == catalogo.PARTICIPANTES_DO_C20
    despachar()
    assert len(mail.outbox) == catalogo.PARTICIPANTES_DO_C20

    horario = ato.horarios.order_by("inicio", "id").first()
    livre = _um_horario_livre(edital, etapa_id, segundo)
    atos_individuais.remarcar(
        actor=presidencia,
        edital=edital,
        etapa_id=etapa_id,
        inscricao_id=horario.inscricao_id,
        banca_id=livre.banca_id,
        inicio=livre.inicio,
        motivo="O candidato pediu outro dia (treinamento).",
        idempotency_key="c20-remarcar",
    )
    assert avisos.count() == catalogo.PARTICIPANTES_DO_C20 + 1

    assert "C20  EXERCITADO" in verificar("C20")
    restaurar("C20", confirmar="C20", autoridade=str(AUTORIDADE_DA_SUITE))
    nova = CenarioDeTreinamento.objects.get(codigo="C20", rodada=2)
    edital_novo = Edital.objects.get(processo=nova.processo)
    assert leitura.agenda_da_etapa(edital_novo, _entrevista(edital_novo)) is None
    assert "C20  INTACTO" in verificar("C20")


def _um_horario_livre(edital, etapa_id, dia):
    agenda = leitura.agenda_da_etapa(edital, etapa_id)
    montagem = leitura.montagem(edital, etapa_id, agenda)
    return next(horario for horario in montagem.livres if horario.dia == dia)
