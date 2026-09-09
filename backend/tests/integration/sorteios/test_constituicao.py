"""O ato acontece uma vez, cobre todos, e a segunda é recusada (021, FR-025, FR-031, FR-032).

**A inversão que organiza a feature está exercitada aqui**: a ocorrência é posterior ao
congelamento, e o comando recusa o contrário. O resto são as garantias que decorrem dela — ordem
completa, ato único por tupla, e concorrência produzindo exatamente um ato.
"""

import threading
from datetime import timedelta

import pytest
from django.db import connections
from django.utils import timezone

from processo_seletivo.classificacao.models import AtoDeOrdenacao, OrigemDaOrdem, PosicaoNaOrdem
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.domain import chave as dominio_da_chave
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import FonteDeTeste
from processo_seletivo.sorteios.models import OcorrenciaDaFonte, RelacaoDeHabilitados, Sorteio
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def pronto(gestor, api_client, manager_headers, process_payload):
    """Relação congelada e ocorrência observada **depois** dela — a ordem dos fatos importa."""
    certame = certame_de_sorteio(gestor, api_client, manager_headers, process_payload, quantos=5)
    relacao = RelacaoDeHabilitados.objects.get(
        pk=publicar_relacao(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            idempotency_key="constituicao-relacao",
            correlation_id="teste-021",
        )["relacao"]
    )
    ocorrencia = OcorrenciaDaFonte.objects.get(
        pk=observar_ocorrencia(
            actor=presidente(),
            processo_id=certame["processo"].id,
            fonte="Loteria Federal",
            referencia="5900",
            idempotency_key="constituicao-ocorrencia",
            correlation_id="teste-021",
            fonte_externa=FonteDeTeste(),
        )["ocorrencia"]
    )
    return certame, relacao, ocorrencia


def _constituir(certame, relacao, ocorrencia, *, chave="constituir-1"):
    return constituir_sorteio(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        relacao_id=relacao.id,
        ocorrencia_id=ocorrencia.id,
        idempotency_key=chave,
        correlation_id="teste-021",
    )


def test_a_ordem_cobre_todos_os_participantes(pronto):
    certame, relacao, ocorrencia = pronto

    declarado = _constituir(certame, relacao, ocorrencia)

    ato = AtoDeOrdenacao.objects.get(pk=declarado["ato"])
    posicoes = list(
        PosicaoNaOrdem.objects.filter(ato=ato).order_by("posicao").values_list("posicao", flat=True)
    )
    assert declarado["quantidade"] == relacao.quantidade == 5
    assert posicoes == [1, 2, 3, 4, 5], "sem lacuna, e sem truncar pelo número de vagas"
    assert ato.origem == OrigemDaOrdem.SORTEIO


def test_a_ordem_e_a_que_o_algoritmo_publicado_produz(pronto):
    """A prova de que o ato **é** o algoritmo, e não uma implementação paralela."""
    certame, relacao, ocorrencia = pronto

    declarado = _constituir(certame, relacao, ocorrencia)

    esperada = dominio_da_chave.ordem(
        relation_hash=relacao.resumo,
        draw_scope_id=dominio_da_chave.recorte(perfil_id=relacao.perfil_id),
        seed=declarado["semente"],
        public_numbers=[p.numero_publico for p in relacao.participantes.all()],
    )
    numero_por_inscricao = {p.inscricao_id: p.numero_publico for p in relacao.participantes.all()}
    gravada = [
        numero_por_inscricao[p.inscricao_id]
        for p in PosicaoNaOrdem.objects.filter(ato_id=declarado["ato"]).order_by("posicao")
    ]
    assert gravada == esperada


def test_a_posicao_de_um_sorteio_nao_pontua_e_nao_deixa_empate(pronto):
    certame, relacao, ocorrencia = pronto

    declarado = _constituir(certame, relacao, ocorrencia)

    for posicao in PosicaoNaOrdem.objects.filter(ato_id=declarado["ato"]):
        assert posicao.pontuacao_combinada is None, "sorteio não pontua"
        assert posicao.empate_residual is False, "a ordem é total"
        assert posicao.desempate == []
        assert posicao.motivo == ""


def test_a_segunda_execucao_sobre_a_mesma_tupla_e_recusada(pronto):
    certame, relacao, ocorrencia = pronto
    _constituir(certame, relacao, ocorrencia)

    with pytest.raises(DomainError, match="draw_already_constituted"):
        _constituir(certame, relacao, ocorrencia, chave="constituir-2")


def test_a_repeticao_da_mesma_chave_devolve_o_desfecho_do_primeiro(pronto):
    certame, relacao, ocorrencia = pronto

    primeiro = _constituir(certame, relacao, ocorrencia)
    repetido = _constituir(certame, relacao, ocorrencia)

    assert repetido["sorteio"] == primeiro["sorteio"]
    assert Sorteio.objects.count() == 1


def test_requisicoes_concorrentes_produzem_exatamente_um_ato(pronto):
    """FR-032: duas abas ao mesmo tempo, um ato só — e a segunda recebe o desfecho da primeira."""
    certame, relacao, ocorrencia = pronto
    desfechos, falhas = [], []

    def executar(indice):
        try:
            desfechos.append(
                _constituir(certame, relacao, ocorrencia, chave=f"concorrente-{indice}")
            )
        except DomainError as recusa:
            falhas.append(recusa.code)
        finally:
            connections.close_all()

    linhas = [threading.Thread(target=executar, args=(i,)) for i in range(2)]
    for linha in linhas:
        linha.start()
    for linha in linhas:
        linha.join()

    assert Sorteio.objects.count() == 1
    assert AtoDeOrdenacao.objects.filter(origem=OrigemDaOrdem.SORTEIO).count() == 1
    assert len(desfechos) + len(falhas) == 2


def test_ocorrencia_anterior_ao_congelamento_e_recusada(
    gestor, api_client, manager_headers, process_payload
):
    """A semente é posterior ao compromisso, e não o contrário (FR-016)."""
    certame = certame_de_sorteio(gestor, api_client, manager_headers, process_payload)
    # A ocorrência **declarada** pelo Edital, e que aconteceu **antes** do congelamento: é a
    # combinação que a FR-016 recusa, e a única que este teste quer exercitar. Uma referência
    # diferente seria recusada antes, por outro motivo, e o teste mediria outra coisa.
    ocorrencia = OcorrenciaDaFonte.objects.create(
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        material_bruto="1 2 3 4 5",
        ocorrida_em=timezone.now() - timedelta(days=1),
        observada_em=timezone.now(),
        observada_por="cpf:presidente",
    )
    relacao = RelacaoDeHabilitados.objects.get(
        pk=publicar_relacao(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            idempotency_key="anterior-relacao",
            correlation_id="teste-021",
        )["relacao"]
    )

    with pytest.raises(DomainError, match="occurrence_precedes_freeze"):
        _constituir(certame, relacao, ocorrencia)


def test_relacao_sucedida_nao_e_sorteada(pronto):
    """FR-071: o universo comprometido já não é aquele."""
    certame, relacao, ocorrencia = pronto
    publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="sucede-relacao",
        correlation_id="teste-021",
        motivo="Resultado de origem sucedido.",
    )

    with pytest.raises(DomainError, match="relation_superseded"):
        _constituir(certame, relacao, ocorrencia, chave="sucedida-1")
