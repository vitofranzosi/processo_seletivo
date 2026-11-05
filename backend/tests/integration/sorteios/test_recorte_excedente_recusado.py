"""Os comandos recusam o recorte excedente (122, FR-3897 a FR-3899, D-003, D-006; SC-1169).

A Modalidade que o Perfil aponta como a ampla deixou de ter relação, sorteio e divulgação próprios.
A recusa mora no comando, sob a trava — a tela que esconde o botão não fecha a porta de quem tem o
formulário antigo aberto ou chama o comando direto.
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.editais.domain.recortes import CODIGO_DA_RECUSA
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.models import RelacaoDeHabilitados, Sorteio
from tests.fixtures.recorte_excedente import (
    LISTA_AC,
    certame_com_ac,
    divulgar,
    sem_a_recusa,
)
from tests.fixtures.sorteio import presidente

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _relacao_de_ac(certame, *, chave, motivo=""):
    return publicar_relacao(
        actor=presidente(),
        processo_id=certame["edital"].processo_id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        lista_id=LISTA_AC,
        idempotency_key=chave,
        correlation_id="teste-122",
        motivo=motivo,
    )


def _recusa(funcao):
    with pytest.raises(DomainError) as erro:
        funcao()
    assert erro.value.code == CODIGO_DA_RECUSA
    assert erro.value.status == 422
    assert "aponta como a ampla concorrência" in erro.value.detail
    return erro.value


# --- FR-3897 · congelar a relação ----------------------------------------------------------------


def test_congelar_a_relacao_da_modalidade_apontada_e_recusado(
    gestor, api_client, manager_headers, process_payload
):
    certame = certame_com_ac(gestor, api_client, manager_headers, process_payload)
    trilha_antes = RegistroAuditoria.objects.count()

    _recusa(lambda: _relacao_de_ac(certame, chave="relacao-ac-122"))

    assert not RelacaoDeHabilitados.objects.filter(
        edital=certame["edital"], lista_id=LISTA_AC
    ).exists()
    assert RegistroAuditoria.objects.count() == trilha_antes


def test_suceder_a_relacao_excedente_com_motivo_tambem_e_recusado(
    gestor, api_client, manager_headers, process_payload
):
    """D-006: a sucessão no recorte excedente é recusada como o primeiro gesto."""
    certame = certame_com_ac(
        gestor, api_client, manager_headers, process_payload, acervo=True, prefixo="suc-122"
    )

    _recusa(lambda: _relacao_de_ac(certame, chave="relacao-ac-suc", motivo="Corrigir universo"))

    assert (
        RelacaoDeHabilitados.objects.filter(edital=certame["edital"], lista_id=LISTA_AC).count()
        == 1
    )


def test_o_pedido_repetido_devolve_o_desfecho_anterior(
    gestor, api_client, manager_headers, process_payload
):
    """A repetição vem antes da recusa: ela não é ato novo, e devolve o que já foi."""
    certame = certame_com_ac(gestor, api_client, manager_headers, process_payload, prefixo="rep")
    with sem_a_recusa():
        primeiro = _relacao_de_ac(certame, chave="relacao-ac-rep")

    assert _relacao_de_ac(certame, chave="relacao-ac-rep") == primeiro


# --- FR-3898 · sortear a relação excedente já congelada ------------------------------------------


def test_a_relacao_excedente_congelada_nao_sorteia(
    gestor, api_client, manager_headers, process_payload
):
    """T6 da `research.md`: retirá-la dos botões não basta; o comando recusa."""
    certame = certame_com_ac(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        acervo=True,
        sortear_ac=False,
        prefixo="t6-122",
    )

    _recusa(
        lambda: constituir_sorteio(
            actor=presidente(),
            processo_id=certame["edital"].processo_id,
            edital_id=certame["edital"].id,
            relacao_id=certame["relacoes"][LISTA_AC],
            ocorrencia_id=certame["ocorrencia"],
            idempotency_key="sorteio-ac-t6",
            correlation_id="teste-122",
        )
    )

    assert not Sorteio.objects.filter(edital=certame["edital"], lista_id=LISTA_AC).exists()


def test_anular_e_sortear_de_novo_no_recorte_excedente_e_recusado(
    gestor, api_client, manager_headers, process_payload
):
    """D-006: constituir com `sorteio_anterior_id` também passa pela recusa."""
    certame = certame_com_ac(
        gestor, api_client, manager_headers, process_payload, acervo=True, prefixo="anul-122"
    )
    anterior = Sorteio.objects.get(edital=certame["edital"], lista_id=LISTA_AC)

    _recusa(
        lambda: constituir_sorteio(
            actor=presidente(),
            processo_id=certame["edital"].processo_id,
            edital_id=certame["edital"].id,
            relacao_id=certame["relacoes"][LISTA_AC],
            ocorrencia_id=certame["ocorrencia"],
            idempotency_key="sorteio-ac-anul",
            correlation_id="teste-122",
            sorteio_anterior_id=anterior.id,
            motivo_da_anulacao="Refazer",
        )
    )


# --- FR-3899 · divulgar o ato excedente ----------------------------------------------------------


def test_divulgar_o_ato_excedente_e_recusado_e_nada_se_grava(
    gestor, api_client, manager_headers, process_payload
):
    certame = certame_com_ac(
        gestor, api_client, manager_headers, process_payload, acervo=True, prefixo="div-122"
    )

    _recusa(lambda: divulgar(certame, LISTA_AC, chave="divulgar-ac-122"))

    assert not PublicacaoResultado.objects.filter(
        edital=certame["edital"], lista_id=LISTA_AC
    ).exists()


def test_a_publicacao_excedente_feita_antes_fica_como_esta(
    gestor, api_client, manager_headers, process_payload
):
    certame = certame_com_ac(
        gestor, api_client, manager_headers, process_payload, acervo=True, prefixo="ant-122"
    )
    feita = divulgar(certame, LISTA_AC, chave="divulgar-ac-antes", recusa_desligada=True)

    _recusa(lambda: divulgar(certame, LISTA_AC, chave="divulgar-ac-depois"))

    feita.refresh_from_db()
    assert not feita.sucessoras.exists()
    assert (
        PublicacaoResultado.objects.filter(edital=certame["edital"], lista_id=LISTA_AC).count() == 1
    )


def test_os_recortes_operacionais_continuam_divulgaveis(
    gestor, api_client, manager_headers, process_payload
):
    certame = certame_com_ac(gestor, api_client, manager_headers, process_payload, prefixo="ok")

    for indice, lista in enumerate(certame["atos"]):
        assert divulgar(certame, lista, chave=f"divulgar-op-{indice}") is not None
