"""A linha geral derivada sobrevive à gravação, e é a mesma linha (027, T-001, FR-318).

**As três travessias que este arquivo existe para pegar.** `replace_draft` apaga e recria o
rascunho inteiro, e essa é a classe de defeito que já custou quantidade publicável neste
repositório — o que não é reenviado some sem erro nenhum:

1. gravar a mesma carga duas vezes tem de produzir a mesma identidade e o mesmo resumo canônico,
   ou a Retificação perde o endereço da linha e o resumo muda sem o conteúdo mudar (FR-168 da 025);
2. gravar **outra etapa** do assistente não pode levar a linha embora;
3. **reaproveitar** um Edital — que hoje vem sempre de um Edital sem quadro — tem de nascer com a
   linha, porque é o caminho mais exposto que existe.
"""

from datetime import datetime

import pytest

from processo_seletivo.editais.application.draft import replace_draft
from processo_seletivo.editais.models.perfis import LinhaDoQuadroDeVagas
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from processo_seletivo.shared.canonical import canonical_sha256
from tests.conftest import ator_institucional
from tests.fixtures.edital import complete_draft


@pytest.fixture
def elaborador():
    return ator_institucional("elaborador", "edital:elaborar")


@pytest.fixture
def rascunho(db, api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def _com_instantes(eventos):
    """`replace_draft` recebe instantes já convertidos: quem converte é a borda — o serializer da
    API e o formulário da interface —, e não o command."""
    return [
        {
            **evento,
            **{
                campo: datetime.fromisoformat(evento[campo])
                for campo in ("startAt", "endAt")
                if isinstance(evento.get(campo), str)
            },
        }
        for evento in eventos
    ]


def gravar(edital, elaborador, carga, *, area="perfis"):
    edital.refresh_from_db()
    replace_draft(
        actor=elaborador,
        edital_id=edital.id,
        expected_revision=edital.revision,
        profiles=carga["profiles"],
        schedule=_com_instantes(carga["schedule"]),
        correlation_id=f"027-{area}",
        area=area,
    )
    edital.refresh_from_db()
    return edital


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_linha_geral_nasce_da_vaga_imediata_do_perfil(rascunho, elaborador):
    carga = complete_draft()
    carga["profiles"][0]["immediateVacancies"] = 2

    gravar(rascunho, elaborador, carga)

    linha = LinhaDoQuadroDeVagas.objects.get()
    assert linha.modalidade_id is None
    assert linha.vagas_imediatas == 2


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_gravar_a_mesma_carga_duas_vezes_preserva_identidade_e_resumo(rascunho, elaborador):
    carga = complete_draft()
    gravar(rascunho, elaborador, carga)
    identidade = LinhaDoQuadroDeVagas.objects.get().id
    resumo = canonical_sha256(edital_snapshot(rascunho))

    gravar(rascunho, elaborador, carga)

    assert LinhaDoQuadroDeVagas.objects.get().id == identidade
    assert canonical_sha256(edital_snapshot(rascunho)) == resumo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_gravar_outra_etapa_nao_leva_a_linha_embora(rascunho, elaborador):
    """A travessia que mata em silêncio: uma visita ao Cronograma apagando o quadro."""
    from processo_seletivo.interface.forms import perfis_persistidos

    gravar(rascunho, elaborador, complete_draft())
    identidade = LinhaDoQuadroDeVagas.objects.get().id

    # É assim que a interface grava uma etapa que não é a dos Perfis: relendo os Perfis do banco e
    # reenviando-os junto. Se `perfis_persistidos` não carregasse o quadro, ele sumiria aqui.
    gravar(
        rascunho,
        elaborador,
        {"profiles": perfis_persistidos(rascunho), "schedule": complete_draft()["schedule"]},
        area="cronograma",
    )

    assert LinhaDoQuadroDeVagas.objects.get().id == identidade


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_alterar_o_total_reafirma_a_linha_geral(rascunho, elaborador):
    """FR-322 pelo caminho mais comum: o total muda, e a projeção acompanha sem ser digitada."""
    carga = complete_draft()
    gravar(rascunho, elaborador, carga)

    carga["profiles"][0]["immediateVacancies"] = 9
    gravar(rascunho, elaborador, carga)

    assert LinhaDoQuadroDeVagas.objects.get().vagas_imediatas == 9
