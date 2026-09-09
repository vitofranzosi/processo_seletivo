"""Publicar a relação **é** congelá-la, e no mesmo instante nasce o compromisso do método.

Os dois compromissos são um só ato (021, D-014, FR-001, FR-006, FR-067). O que este arquivo
exercita é o que a relação passa a garantir a partir dali: universo imutável, método citado por
resumo, sucessão com motivo, e nenhuma rota que edite participante.
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.canonical import canonical_sha256
from processo_seletivo.sorteios.application.relacao import PUBLICAR, publicar_relacao
from processo_seletivo.sorteios.domain import projecao
from processo_seletivo.sorteios.models import ParticipanteHabilitado, RelacaoDeHabilitados
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    return certame_de_sorteio(gestor, api_client, manager_headers, process_payload)


def _publicar(certame, *, chave="publicar-relacao-1", motivo="", lista_id=None):
    return publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        lista_id=lista_id,
        idempotency_key=chave,
        correlation_id="teste-021",
        motivo=motivo,
    )


def test_publicar_projeta_numera_e_congela(certame):
    declarado = _publicar(certame)

    relacao = RelacaoDeHabilitados.objects.get(pk=declarado["relacao"])
    numeros = list(
        ParticipanteHabilitado.objects.filter(relacao=relacao)
        .order_by("numero_publico")
        .values_list("numero_publico", "inscricao__protocolo")
    )
    assert relacao.quantidade == 3
    assert [n for n, _ in numeros] == [1, 2, 3]
    assert [p for _, p in numeros] == sorted(p for _, p in numeros), "numerado por protocolo"
    assert len(relacao.resumo) == 64


def test_a_relacao_cita_o_metodo_por_resumo_antes_de_existir_semente(certame):
    """O compromisso do método nasce com o do universo — não no instante do sorteio (FR-067)."""
    declarado = _publicar(certame)

    relacao = RelacaoDeHabilitados.objects.get(pk=declarado["relacao"])
    assert relacao.metodo_hash == canonical_sha256(METODO)
    assert declarado["algoritmo"] == "IFES-SORTEIO-SHA256-v1"


def test_o_resumo_cobre_a_projecao_publica_e_e_recalculavel(certame):
    """Quem lê a relação no portal consegue refazer o número, em vez de aceitá-lo (R-015)."""
    declarado = _publicar(certame)
    relacao = RelacaoDeHabilitados.objects.get(pk=declarado["relacao"])

    participantes = [
        (p.numero_publico, p.inscricao)
        for p in relacao.participantes.select_related("inscricao").order_by("numero_publico")
    ]
    recalculado = canonical_sha256(
        projecao.conteudo_canonico(
            relacao_id=relacao.id,
            edital_id=relacao.edital_id,
            versao_id=relacao.versao_id,
            perfil_id=relacao.perfil_id,
            marco_id=relacao.marco_id,
            lista_id=relacao.lista_id,
            metodo_hash=relacao.metodo_hash,
            criterio_publicado=relacao.criterio_de_projecao,
            participantes=participantes,
        )
    )

    assert recalculado == relacao.resumo


def test_a_relacao_publicada_e_imutavel(certame):
    declarado = _publicar(certame)
    relacao = RelacaoDeHabilitados.objects.get(pk=declarado["relacao"])

    relacao.quantidade = 99
    with pytest.raises(TypeError, match="append-only"):
        relacao.save()
    with pytest.raises(TypeError, match="append-only"):
        relacao.delete()


def test_relacao_vazia_e_recusada(gestor, api_client, manager_headers, process_payload):
    certame = certame_de_sorteio(gestor, api_client, manager_headers, process_payload, quantos=0)

    with pytest.raises(DomainError, match="relation_would_be_empty"):
        _publicar(certame)


def test_suceder_exige_motivo_e_preserva_a_anterior(certame):
    primeira = _publicar(certame)

    with pytest.raises(DomainError, match="relation_succession_reason_required"):
        _publicar(certame, chave="publicar-relacao-2")

    segunda = _publicar(certame, chave="publicar-relacao-3", motivo="Resultado de origem sucedido.")
    anterior = RelacaoDeHabilitados.objects.get(pk=primeira["relacao"])
    sucessora = RelacaoDeHabilitados.objects.get(pk=segunda["relacao"])

    assert sucessora.relacao_anterior_id == anterior.id
    assert anterior.resumo and anterior.quantidade == 3, "a anterior permanece íntegra"


def test_a_publicacao_e_idempotente(certame):
    primeira = _publicar(certame)
    repetida = _publicar(certame)

    assert repetida["relacao"] == primeira["relacao"]
    assert RelacaoDeHabilitados.objects.count() == 1


def test_a_publicacao_fica_na_trilha_com_ator_instante_e_correlacao(certame):
    declarado = _publicar(certame)

    registro = RegistroAuditoria.objects.filter(operation=PUBLICAR).latest("occurred_at")
    assert str(registro.aggregate_id) == declarado["relacao"]
    assert registro.actor_subject == "maria"
    assert registro.correlation_id == "teste-021"


def test_marco_sem_metodo_nao_congela(gestor, api_client, manager_headers, process_payload):
    """Congelar sob método indefinido seria escolher o método depois (FR-066)."""
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from tests.fixtures.comissao import constituir, inscrever, rascunho_com_etapas
    from tests.fixtures.edital import PROFILE_ID
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.sorteio import marco_com_metodo

    rascunho = rascunho_com_etapas()
    marco_com_metodo(
        rascunho, perfil_id=PROFILE_ID, etapa_id=rascunho["stages"][1]["id"], metodo=None
    )
    for perfil in rascunho["profiles"]:
        for marco in perfil.get("classificationMilestones") or []:
            marco["drawMethod"] = None
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    constituir(gestor, edital.processo, [("maria", Funcao.PRESIDENTE)], prefixo="sem-metodo")
    inscrever(edital, 2, primeiro=951)

    with pytest.raises(DomainError, match="draw_method_not_declared"):
        _publicar(
            {
                "processo": edital.processo,
                "edital": edital,
                "perfil": PROFILE_ID,
                "marco": "00000000-0000-4000-8000-000000000821",
            },
            chave="sem-metodo-1",
        )
