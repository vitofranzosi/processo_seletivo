"""A lista reservada de sorteio sem relação, com a ausência comprovada (155, US5, T042, R-007).

O certame é o sorteio com cotas da `016`, com a PPI que **ninguém declarou**: não há relação dela,
nem ordem, nem apuração — `publicar_relacao` recusa a relação vazia. A prova da ausência é a relação
da ampla do marco, congelada e sem nenhum participante que tenha declarado a PPI (FR-6332). Sem ela,
a lista é "relação não congelada", e nenhum ato é oferecido (FR-6333).

Os fatos externos chegam pela composição de verdade (`interface.destinacao_da_vaga.Composicao`): é
ela que pergunta ao sorteio, e a ocupação não o importa.
"""

import pytest

from processo_seletivo.interface.destinacao_da_vaga import Composicao, situacao_do_recorte
from processo_seletivo.ocupacao.application.destinacao import (
    declarar_nao_preenchida,
    destinar_vaga,
    previa_da_destinacao,
    previa_da_nao_preenchida,
)
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import MovimentoDeVaga, VagaNaoPreenchida
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao_sorteada import LISTA_PCD, LISTA_PPI, rascunho_sorteado_com_quadro
from tests.fixtures.sorteio import MARCO, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def _certame(gestor, api_client, manager_headers, process_payload, prefixo, *, congelar, **quadro):
    """O Edital de sorteio com a PPI sem ninguém, e a relação da ampla congelada ou não."""
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from processo_seletivo.sorteios.application.relacao import publicar_relacao
    from tests.fixtures.comissao import constituir, inscrever
    from tests.fixtures.publicacao import publish_original

    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho_sorteado_com_quadro(**quadro),
    )
    constituir(gestor, edital.processo, [("maria", Funcao.PRESIDENTE)], prefixo=prefixo)
    # Só a PcD é declarada: a PPI fica sem ninguém, e é a lista sem relação.
    inscrever(edital, 4, primeiro=901, modalidades={0: LISTA_PCD})
    if congelar:
        publicar_relacao(
            actor=presidente(),
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=None,
            idempotency_key=f"{prefixo}-relacao-ampla",
            correlation_id="teste-155",
        )
    return edital


def _recorte(edital, lista_id=LISTA_PPI):
    return {"edital": edital, "perfil_id": PROFILE_ID, "marco_id": MARCO, "lista_id": lista_id}


def _destinar(edital, assinatura, chave):
    return destinar_vaga(
        actor=presidente(),
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=LISTA_PPI,
        assinatura=assinatura,
        fatos_externos=Composicao(),
        idempotency_key=chave,
        correlation_id="teste-155",
    )


def test_com_a_relacao_da_ampla_congelada_a_ppi_se_destina_sem_apuracao(
    gestor, api_client, manager_headers, process_payload
):
    """US5.3, FR-6332: a destinação disponível pela condição, sem apuração artificial, e o
    movimento com o recorte preenchido e sem apuração de origem."""
    edital = _certame(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        "sorteio-155-congelada",
        congelar=True,
        reversao=nomes.REVERSAO_POR_ESGOTAMENTO,
    )
    vaga = situacao_do_recorte(**_recorte(edital), rotulo="PPI", composicao=Composicao())
    assert vaga["disponivel"] and vaga["destinacao"] and vaga["quantidade"] == 1
    assert "como a relação da ampla concorrência congelada comprova" in vaga["frase"]

    previa = previa_da_destinacao(**_recorte(edital), fatos_externos=Composicao())
    assert previa["recusa"] is None and previa["apuracao"] is None
    declarado = _destinar(edital, previa["assinatura"], "sorteio-155-destinar")

    movimento = MovimentoDeVaga.objects.get(pk=declarado["movimento"])
    assert movimento.apuracao_id is None
    assert (str(movimento.edital_id), str(movimento.perfil_id), str(movimento.marco_id)) == (
        str(edital.id),
        PROFILE_ID,
        MARCO,
    )
    assert str(movimento.origem_lista_id) == LISTA_PPI and movimento.destino_lista_id is None
    assert movimento.quantidade == 1
    assert declarado["apuracaoSeguinte"] is None

    # **Destinada, não se destina de novo** (FR-6314): o movimento sai das efetivas da conta.
    depois = previa_da_destinacao(**_recorte(edital), fatos_externos=Composicao())
    assert depois["recusa"][0] == nomes.SEM_SALDO_A_DESTINAR
    assert (
        "já foi destinada"
        in situacao_do_recorte(**_recorte(edital), rotulo="PPI", composicao=Composicao())["frase"]
    )


def test_sem_a_relacao_da_ampla_a_ppi_e_relacao_nao_congelada(
    gestor, api_client, manager_headers, process_payload
):
    """US5.4, FR-6333: ausência de registro não é lista vazia — nenhum ato é oferecido."""
    edital = _certame(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        "sorteio-155-aberta",
        congelar=False,
        reversao=nomes.REVERSAO_POR_ESGOTAMENTO,
    )
    vaga = situacao_do_recorte(**_recorte(edital), rotulo="PPI", composicao=Composicao())
    assert vaga["frase"].startswith("Relação não congelada")
    assert not vaga["disponivel"] and not vaga["ato"]

    previa = previa_da_destinacao(**_recorte(edital), fatos_externos=Composicao())
    assert previa["recusa"][0] == nomes.SEM_SALDO_A_DESTINAR
    assert previa["recusa"][1].startswith("Relação não congelada")
    with pytest.raises(DomainError):
        _destinar(edital, previa["assinatura"], "sorteio-155-aberta-destinar")
    assert not MovimentoDeVaga.objects.filter(edital=edital).exists()


def test_a_lista_declarada_tem_o_caminho_de_sempre(
    gestor, api_client, manager_headers, process_payload
):
    """A PcD tem inscrito: a pergunta da ausência não se coloca, e nada muda nela."""
    edital = _certame(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        "sorteio-155-pcd",
        congelar=True,
        reversao=nomes.REVERSAO_POR_ESGOTAMENTO,
    )
    assert Composicao().ausencia_de_concorrente(**_recorte(edital, LISTA_PCD)) is None
    assert (
        situacao_do_recorte(**_recorte(edital, LISTA_PCD), rotulo="PcD", composicao=Composicao())
        is None
    )


def test_no_edital_silente_a_ppi_se_declara_nao_preenchida_sem_apuracao(
    gestor, api_client, manager_headers, process_payload
):
    """A declaração da FR-6323 sobre a mesma prova: `VagaNaoPreenchida.apuracao` nula."""
    edital = _certame(
        gestor, api_client, manager_headers, process_payload, "sorteio-155-silente", congelar=True
    )
    previa = previa_da_nao_preenchida(**_recorte(edital), fatos_externos=Composicao())
    assert previa["recusa"] is None and previa["quantidade"] == 1

    declarado = declarar_nao_preenchida(
        actor=presidente(),
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=LISTA_PPI,
        fundamento="Ninguém se autodeclarou PPI, e o Edital não declara para onde vai a vaga.",
        assinatura=previa["assinatura"],
        fatos_externos=Composicao(),
        idempotency_key="sorteio-155-silente-declarar",
        correlation_id="teste-155",
    )

    registro = VagaNaoPreenchida.objects.get(pk=declarado["naoPreenchida"])
    assert registro.apuracao_id is None and str(registro.lista_id) == LISTA_PPI
    assert registro.quantidade == 1
    depois = previa_da_nao_preenchida(**_recorte(edital), fatos_externos=Composicao())
    assert depois["recusa"][0] == nomes.SEM_SALDO_A_DESTINAR


def test_a_ocupacao_mostra_a_destinacao_com_a_prova(
    gestor, api_client, manager_headers, process_payload, client, settings
):
    """Com a prova, o botão e a frase que a cita."""
    from django.urls import reverse

    from tests.interface.conftest import identificar

    settings.INTERFACE_SELETOR_IDENTIDADE = True
    congelada = _certame(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        "sorteio-155-tela",
        congelar=True,
        reversao=nomes.REVERSAO_POR_ESGOTAMENTO,
    )
    identificar(client, "maria", [])
    pagina = client.get(reverse("interface:ocupacao", args=[congelada.id, MARCO])).content.decode()
    assert "Destinar à ampla concorrência" in pagina
    assert "como a relação da ampla concorrência congelada comprova" in pagina


def test_a_ocupacao_sem_a_relacao_da_ampla_nao_oferece_ato(
    gestor, api_client, manager_headers, process_payload, client, settings
):
    from django.urls import reverse

    from tests.interface.conftest import identificar

    settings.INTERFACE_SELETOR_IDENTIDADE = True
    aberta = _certame(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        "sorteio-155-tela-aberta",
        congelar=False,
        reversao=nomes.REVERSAO_POR_ESGOTAMENTO,
    )
    identificar(client, "maria", [])
    pagina = client.get(reverse("interface:ocupacao", args=[aberta.id, MARCO])).content.decode()
    assert "Relação não congelada" in pagina
    assert "Destinar à ampla concorrência" not in pagina


def test_a_destinacao_sem_apuracao_se_desfaz(gestor, api_client, manager_headers, process_payload):
    """FR-6334: o ato contrário devolve a vaga à PPI, e ela volta a ser destinável."""
    from processo_seletivo.interface.destinacao_da_vaga import chamadas_dependentes
    from processo_seletivo.ocupacao.application.destinacao import (
        desfazer_destinacao,
        previa_do_desfazimento_da_destinacao,
    )

    edital = _certame(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        "sorteio-155-desfazer",
        congelar=True,
        reversao=nomes.REVERSAO_POR_ESGOTAMENTO,
    )
    previa = previa_da_destinacao(**_recorte(edital), fatos_externos=Composicao())
    declarado = _destinar(edital, previa["assinatura"], "sorteio-155-desfazer-destinar")
    desfazer = previa_do_desfazimento_da_destinacao(
        edital=edital,
        movimento_id=declarado["movimento"],
        chamadas_dependentes=chamadas_dependentes,
    )
    assert desfazer["recusa"] is None
    desfazer_destinacao(
        actor=presidente(),
        processo_id=edital.processo_id,
        edital_id=edital.id,
        movimento_id=declarado["movimento"],
        motivo="Destinada por engano.",
        assinatura=desfazer["assinatura"],
        chamadas_dependentes=chamadas_dependentes,
        idempotency_key="sorteio-155-desfazer-ato",
        correlation_id="teste-155",
    )

    de_novo = previa_da_destinacao(**_recorte(edital), fatos_externos=Composicao())
    assert de_novo["recusa"] is None and de_novo["quantidade"] == 1


def test_a_relacao_da_ampla_com_quem_declarou_a_lista_nao_comprova_a_ausencia():
    """A terceira prova da R-007: participante da relação da ampla que declarou a lista. Só a
    divergência entre a relação congelada e as inscrições de hoje chega aqui, e ela não é lida como
    lista vazia (FR-6333)."""
    composicao = Composicao()
    composicao._do_sorteio[(PROFILE_ID, MARCO)] = {
        "semInscrito": {LISTA_PPI},
        "relacaoDaAmpla": "relacao-da-ampla",
        "declaradasNaAmpla": {LISTA_PPI},
    }
    ausencia = composicao.ausencia_de_concorrente(**_recorte(None))
    assert ausencia["comprovada"] is False and ausencia["relacao"] == "relacao-da-ampla"
