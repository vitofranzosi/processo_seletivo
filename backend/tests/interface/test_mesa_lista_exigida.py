"""A Mesa mostra o que foi pedido, e o que não se aplicava (044, FR-718, UX-081 a UX-083).

As linhas da lista são gravadas à mão aqui, e **de propósito diferentes** do que o recorte do
Edital calcularia: é o que prova que a Mesa lê a lista, e não a regra (R-006). A fixture de
inscrição promove a inscrição sem passar pelo envio, e por isso nasce sem lista — que é o caso da
inscrição enviada antes da `044`, e o do aviso de reconstrução.
"""

import pytest
from django.urls import reverse

from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.inscricoes.models import ItemDaListaExigida
from tests.fixtures.comissao import (
    DOCUMENTO_A,
    DOCUMENTO_B,
    ETAPA_A1,
    alocar_em,
    constituir,
    inscrever,
    publicar_processo_com_etapas,
)
from tests.fixtures.edital import identificador
from tests.fixtures.mesa import distribuir_para
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

SEED = 94
AVISO = "foi reconstruída a partir da versão do Edital que ela aceitou"


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    edital = publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"lista-da-mesa-{SEED:04d}"},
        {
            "institutionalCode": f"PS-2026-{SEED}",
            "title": "Processo com lista",
            "firstEdital": {"number": "94", "year": 2026, "title": "Edital 94/2026"},
        },
        seed=SEED,
        com_documentos=True,
        avaliacoes=2,
        maxima="100.0000",
    )
    etapa = identificador(ETAPA_A1, SEED)
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO), ("ana", Funcao.MEMBRO)],
        prefixo=f"lista-{SEED}",
    )
    alocar_em(gestor, edital.processo, membros["joao"], edital, etapa, chave=f"aloc-{SEED}")
    alocar_em(gestor, edital.processo, membros["ana"], edital, etapa, chave=f"aloc-ana-{SEED}")
    return {"edital": edital, "etapa": etapa, "processo": edital.processo, "membros": membros}


def _gravar(inscricao, situacoes):
    """A lista do envio, gravada com o instante e a versão do envio — o que o gatilho exige."""
    for requisito, (situacao, forma, codigo) in situacoes.items():
        ItemDaListaExigida.objects.create(
            inscricao=inscricao,
            versao_id=inscricao.versao_aceita_id,
            requisito_id=requisito,
            chave=requisito[-4:],
            situacao=situacao,
            forma_do_recorte=forma,
            modalidade_codigo=codigo,
            gravada_em=inscricao.submitted_at,
        )


def _mesa(client, cenario, inscricao):
    return client.get(
        reverse(
            "interface:mesa-inscricao",
            args=[cenario["edital"].id, cenario["etapa"], inscricao.id],
        )
    )


@pytest.fixture
def inscricao(cenario, gestor, raiz_de_arquivos):
    (criada,) = inscrever(
        cenario["edital"], 1, primeiro=9400, documentos=[identificador(DOCUMENTO_A, SEED)]
    )
    distribuir_para(cenario, gestor, ["joao"], [criada], chave="lista")
    return criada


def test_a_mesa_mostra_os_tres_estados_com_a_razao(client, seletor_ligado, cenario, inscricao):
    _gravar(
        inscricao,
        {
            identificador(DOCUMENTO_A, SEED): ("OBRIGATORIO", "TODOS", ""),
            identificador(DOCUMENTO_B, SEED): (
                "NAO_SE_APLICA",
                "MODALIDADE_EM_TODOS_OS_PERFIS",
                "PcD",
            ),
        },
    )
    identificar(client, "joao", [])

    corpo = _mesa(client, cenario, inscricao).content.decode()

    assert "pedido de todos os candidatos" in corpo
    assert "Não se aplicam a esta inscrição" in corpo
    assert "Não se aplica: pedido de quem concorre em PcD, em todos os Perfis" in corpo
    assert corpo.index("Documento de identificação") < corpo.index(
        "Não se aplicam a esta inscrição"
    )
    assert corpo.index("Não se aplicam a esta inscrição") < corpo.index("Diploma de graduação")
    assert AVISO not in corpo, "a lista é gravada: nada a anunciar"


def test_o_facultativo_nao_apresentado_se_distingue_do_obrigatorio(
    client, seletor_ligado, cenario, inscricao
):
    """O Edital publicou os dois como obrigatórios; a lista gravada diz outra coisa, e vence."""
    _gravar(
        inscricao,
        {
            identificador(DOCUMENTO_A, SEED): ("OBRIGATORIO", "TODOS", ""),
            identificador(DOCUMENTO_B, SEED): ("FACULTATIVO", "TODOS", ""),
        },
    )
    identificar(client, "joao", [])

    corpo = _mesa(client, cenario, inscricao).content.decode()

    assert '<span class="marca">facultativo</span>' in corpo
    assert '<span class="marca">obrigatório</span>' in corpo
    assert "não apresentado" in corpo


def test_sem_lista_gravada_a_mesa_reconstroi_e_avisa_uma_vez(
    client, seletor_ligado, cenario, inscricao
):
    identificar(client, "joao", [])

    corpo = _mesa(client, cenario, inscricao).content.decode()

    assert corpo.count(AVISO) == 1
    assert "Diploma de graduação" in corpo, "nada some: os dois pedidos continuam na lista"


def test_quem_nao_recebeu_a_inscricao_nao_ve_a_lista(client, seletor_ligado, cenario, inscricao):
    """A lista não tem rota própria: ela aparece na Mesa, e a Mesa já recusa (FR-728)."""
    _gravar(inscricao, {identificador(DOCUMENTO_A, SEED): ("OBRIGATORIO", "TODOS", "")})
    identificar(client, "ana", [])

    resposta = _mesa(client, cenario, inscricao)

    assert resposta.status_code == 404
    assert "pedido de todos os candidatos" not in resposta.content.decode()
