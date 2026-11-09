"""O gerador sobre um banco já populado: preserva, não duplica, isola e restaura (134).

O banco preexistente é o do `seed_demo` — quatro Editais reais na forma, com inscrições, comissão,
avaliações, resultado divulgado, sorteio, convocação, Requerimento e Retificações: a maior
superfície que a suíte sabe produzir pelos comandos da aplicação. A prova de preservação é **linha
a linha**, sobre todas as tabelas do banco (`tests/fixtures/treinamento.instantaneo`).
"""

import pytest
from django.core.management import CommandError, call_command
from django.urls import reverse

from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.sorteios.models import OcorrenciaDaFonte, Sorteio
from processo_seletivo.treinamento import servico
from processo_seletivo.treinamento.catalogo import POR_CODIGO, concurso_da_rodada
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from processo_seletivo.treinamento.retrato import retratar
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.treinamento import carregar, instantaneo, removidas, restaurar, verificar
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

POC = ("C04", "C07", "C11")


@pytest.fixture
def banco_populado(treinamento):
    """Um banco com dados criados "à mão" — pelo `seed_demo`, que percorre o fluxo real."""
    from io import StringIO

    call_command("seed_demo", codigo="PS-REAL-0001", numero="70", ano=2026, stdout=StringIO())
    return instantaneo()


def _manifesto(codigo, situacao=CenarioDeTreinamento.Situacao.PRONTO):
    return CenarioDeTreinamento.objects.get(codigo=codigo, situacao=situacao)


def _sortear_pela_tela(client, manifesto):
    """O exercício do C07, como a presidência o faz: observar a ocorrência e realizar o sorteio."""
    edital = Edital.objects.get(processo=manifesto.processo)
    marco = POR_CODIGO["C07"] and servico.Montagem(
        codigo="C07", rodada=manifesto.rodada, unidade="cefor", autoridade_id="", titulo=""
    ).id("a1")
    identificar(client, "treino.presidencia", [])
    tela = reverse("interface:sorteio", args=[edital.id, marco])
    antes = client.get(tela)
    assert antes.status_code == 200
    assert "Realizar o sorteio" not in antes.content.decode(), "sem ocorrência não há o que sortear"
    client.post(reverse("interface:observar-ocorrencia-do-sorteio", args=[edital.id, marco]), {})
    assert "Realizar o sorteio" in client.get(tela).content.decode()
    ocorrencia = OcorrenciaDaFonte.objects.get(
        referencia=concurso_da_rodada("C07", manifesto.rodada)
    )
    client.post(
        reverse("interface:realizar-sorteio", args=[edital.id, marco]),
        {
            "relacao_id": manifesto.registros["relacao_do_sorteio"][0],
            "ocorrencia_id": str(ocorrencia.id),
        },
    )
    return Sorteio.objects.get(edital=edital)


def test_a_carga_acrescenta_sem_tocar_em_nada_e_a_segunda_nao_muda_nada(banco_populado):
    antes = banco_populado
    reais = set(ProcessoSeletivo.objects.values_list("id", flat=True))

    saida = carregar(*POC)
    assert saida.count("CRIADO") == 3, saida

    depois = instantaneo()
    assert removidas(antes, depois) == {}, "toda linha preexistente continua idêntica"
    novos = ProcessoSeletivo.objects.exclude(id__in=reais)
    assert sorted(p.institutional_code for p in novos) == [
        "SIM-TREINAMENTO-004",
        "SIM-TREINAMENTO-007",
        "SIM-TREINAMENTO-011",
    ]
    for processo in novos:
        assert "(FICTÍCIO)" in processo.title

    # A segunda execução reconhece os três e não grava **nada** — nem trilha, nem idempotência.
    saida = carregar(*POC)
    assert saida.count("MANTER") == 3, saida
    assert instantaneo() == depois
    assert "INTACTO" in verificar(*POC)


def test_o_exercicio_e_preservado_isolado_e_a_restauracao_so_alcanca_o_c07(
    banco_populado, client, seletor_ligado
):
    carregar("C04", "C07")
    c04 = _manifesto("C04")
    retrato_do_c04 = retratar(c04.processo)

    # Momento 2 — a presidência sorteia pela tela.
    primeiro = _sortear_pela_tela(client, _manifesto("C07"))
    relatorio = verificar("C04", "C07")
    assert "C07  EXERCITADO" in relatorio
    assert "C04  INTACTO" in relatorio, "exercitar um cenário não mexe no outro (18.3)"

    # A carga normal não desfaz o exercício.
    assert "MANTER" in carregar("C07")
    assert Sorteio.objects.filter(pk=primeiro.pk).exists()

    # Momento 3 — restaurar, primeiro sem confirmar: nada muda.
    antes = instantaneo()
    with pytest.raises(CommandError, match="--confirmar C07"):
        restaurar("C07")
    with pytest.raises(CommandError, match="--confirmar C07"):
        restaurar("C07", confirmar="C04")
    assert instantaneo() == antes
    previa = restaurar("C07", dry_run=True)
    assert "Será criada a rodada 2" in previa and "Nenhum registro será excluído" in previa
    assert instantaneo() == antes

    saida = restaurar("C07", confirmar="C07")
    assert "rodada 2" in saida

    anterior = _manifesto("C07", CenarioDeTreinamento.Situacao.SUBSTITUIDO)
    novo = _manifesto("C07")
    assert anterior.substituido_por_id == novo.id
    anterior.processo.refresh_from_db()
    assert anterior.processo.status == ProcessoSeletivo.Status.CANCELADO
    assert Sorteio.objects.filter(pk=primeiro.pk).exists(), "o sorteio feito fica na história"
    assert novo.processo.institutional_code == "SIM-TREINAMENTO-007-R2"
    assert "C07  INTACTO" in verificar("C07")

    # Só mudaram linhas da rodada anterior do C07: o Processo e o Edital cancelados, e o manifesto.
    mudadas = removidas(antes, instantaneo())
    do_c07 = {str(anterior.processo_id), *anterior.registros["edital"], str(anterior.id)}
    assert set(mudadas) == {
        "processos_processoseletivo",
        "processos_edital",
        "treinamento_cenariodetreinamento",
    }, mudadas.keys()
    for linhas in mudadas.values():
        assert {linha["id"] for linha in linhas} <= do_c07
    assert retratar(c04.processo) == retrato_do_c04

    # A rodada nova é exercitável de novo, do início.
    segundo = _sortear_pela_tela(client, novo)
    assert segundo.pk != primeiro.pk


def test_falha_no_meio_nao_deixa_rastro(banco_populado, monkeypatch):
    """Um passo que recusa desfaz o cenário inteiro, e só ele (4.5, 18.8)."""
    from processo_seletivo.shared.api.problems import DomainError
    from processo_seletivo.treinamento.construcao import Montagem

    def recusar(self):
        raise DomainError("falha_simulada", "Falha simulada no congelamento.", 409)

    monkeypatch.setattr(Montagem, "congelar_relacao", recusar)
    saida = carregar("C03", "C07")
    assert "C07  FALHOU" in saida and "falha_simulada" in saida
    assert "C03  CRIADO" in saida, "a falha de um não impede o outro"
    assert not ProcessoSeletivo.objects.filter(institutional_code="SIM-TREINAMENTO-007").exists()
    assert not CenarioDeTreinamento.objects.filter(codigo="C07").exists()
    assert removidas(banco_populado, instantaneo()) == {}

    monkeypatch.undo()
    assert "C07  CRIADO" in carregar("C07"), "e a próxima carga o cria"


def test_processo_com_o_codigo_reservado_sem_manifesto_e_relatado_e_nao_tocado(treinamento):
    """Alguém criou à mão um SIM-TREINAMENTO-004: o gerador não o reaproveita nem o altera."""
    from processo_seletivo.processos.application.commands import create_process_with_first_edital
    from processo_seletivo.seguranca.domain import Actor

    processo, _ = create_process_with_first_edital(
        actor=Actor("alguem.da.equipe", "cefor", frozenset({"processo:criar"})),
        data={
            "institutionalCode": "SIM-TREINAMENTO-004",
            "title": "Criado à mão",
            "firstEdital": {"number": "77", "year": 2026, "title": "Edital 77/2026"},
        },
        idempotency_key="processo-criado-a-mao-0001",
        correlation_id="teste-134",
    )
    antes = instantaneo()
    saida = carregar("C04")
    assert "RECUSAR" in saida and "sem manifesto" in saida
    assert instantaneo() == antes
    assert "CONFLITO" in verificar("C04")
    with pytest.raises(CommandError, match="não tem rodada"):
        restaurar("C04", confirmar="C04")
    processo.refresh_from_db()
    assert processo.title == "Criado à mão"


def test_propriedade_que_nao_se_comprova_bloqueia_a_restauracao(treinamento):
    carregar("C03", autoridade=str(AUTORIDADE_DA_SUITE))
    manifesto = _manifesto("C03")
    CenarioDeTreinamento.objects.filter(pk=manifesto.pk).update(correlation_id="outra-origem")
    antes = instantaneo()
    with pytest.raises(CommandError, match="propriedade"):
        restaurar("C03", confirmar="C03")
    assert instantaneo() == antes
    assert "INCONSISTENTE" in verificar("C03")


def test_a_carga_dos_quinze_cria_cenarios_independentes(treinamento):
    """O catálogo inteiro coexiste, cada um no seu Processo, sem identificador partilhado."""
    saida = carregar(autoridade=str(AUTORIDADE_DA_SUITE))
    assert saida.count("CRIADO") == 15, saida
    processos = ProcessoSeletivo.objects.filter(institutional_code__startswith="SIM-TREINAMENTO-")
    assert processos.count() == 15
    assert CenarioDeTreinamento.objects.filter(situacao="PRONTO").count() == 15
    assert Edital.objects.filter(number__startswith="SIM").count() == 15
    assert verificar().count("INTACTO") == 15


def test_autoridade_nunca_usada_so_com_escolha_expressa(treinamento):
    """O primeiro uso congela o cadastro da autoridade: o gerador não o faz sem que se peça."""
    from processo_seletivo.unidades.models import AutoridadeHabilitada

    antes = instantaneo()
    with pytest.raises(CommandError, match="--autoridade"):
        carregar("C03")
    assert instantaneo() == antes
    assert "C03  CRIADO" in carregar("C03", autoridade=str(AUTORIDADE_DA_SUITE))
    assert AutoridadeHabilitada.objects.get(pk=AUTORIDADE_DA_SUITE).usada_em is not None
