"""`UX-046`: quem supervisiona encontra os Editais que precisam do ato (027, US5, FR-331).

**É a metade que faz a US4 ser praticada, e não só possível.** A advertência da Retificação só
aparece para quem já abriu a Retificação daquele Edital, e a frase da Ocupação só para quem foi
apurar. Quem supervisiona não tinha como saber quais Editais estão nessa condição sem abrir um por
um — e, até esta feature, estavam **todos**.

O sinal reusa a forma que a `022` fixou: espécie, Edital, alvo, medida e destino, com supressão por
alcance. Nenhuma tela nova, nenhuma porta nova.
"""

import pytest

from processo_seletivo.interface import supervisao
from tests.conftest import ator_institucional
from tests.fixtures.legado import publicar_na_versao_anterior

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def supervisora():
    """Quem alcança a supervisão pela permissão sistêmica — uma das duas bases da `011`."""
    return ator_institucional("maria", "comissao:gerir")


@pytest.fixture
def do_acervo(api_client, manager_headers, process_payload):
    """Edital publicado antes de o quadro existir — a condição de 100% do acervo."""
    return publicar_na_versao_anterior(api_client, manager_headers, process_payload, versao=11)


def do_quadro(processo, ator):
    return [
        sinal for sinal in supervisao.sinais(processo, ator) if sinal.especie == supervisao.UX_046
    ]


def test_o_edital_do_acervo_produz_o_sinal_com_o_numero_e_o_ato(do_acervo, supervisora):
    """FR-331: nomeia o Edital, o Perfil e quantos recortes ficam sem quantidade."""
    sinais = do_quadro(do_acervo.processo, supervisora)

    assert len(sinais) == 1, "um Perfil afetado, um sinal"
    sinal = sinais[0]
    assert sinal.edital == do_acervo
    assert "não publica quantidade" in sinal.mensagem
    assert "não têm o que apurar" in sinal.mensagem
    # A medida é por **recorte**, que é o que a Ocupação apura — e não por Perfil.
    assert sinal.medida.numerador == 1 and sinal.medida.denominador == 1


def test_o_destino_e_a_retificacao_para_quem_a_pratica(do_acervo):
    """FR-332: o caminho leva onde a linha se acrescenta, e não a uma tela de leitura."""
    quem_retifica = ator_institucional("bruno", "comissao:gerir", "retificacao:elaborar")

    sinal = do_quadro(do_acervo.processo, quem_retifica)[0]

    assert sinal.destino is not None
    assert "Retificar o quadro de vagas" in sinal.destino.rotulo
    assert str(do_acervo.id) in sinal.destino.url


def test_quem_nao_elabora_retificacao_ve_o_sinal_e_nao_o_caminho(do_acervo, supervisora):
    """A distinção que a `022` fixou, e que continua valendo (FR-036).

    Ver o sinal é uma decisão; praticar o ato é outra. Oferecer o caminho a quem não elabora
    Retificação trocaria o beco sem saída por um beco sinalizado — e a supressão do sinal inteiro
    esconderia de quem supervisiona um fato do Edital que ele alcança.
    """
    sinal = do_quadro(do_acervo.processo, supervisora)[0]

    assert sinal.destino is None
    assert sinal.mensagem, "o sinal continua aparecendo: o que falta é o caminho"


def test_o_edital_com_quadro_nao_produz_sinal(api_client, manager_headers, process_payload):
    """A outra metade: composto hoje, o Edital já nasce com a linha, e não há o que dizer."""
    from tests.fixtures.publicacao import publish_original

    edital = publish_original(api_client, manager_headers, process_payload)

    assert do_quadro(edital.processo, ator_institucional("maria", "comissao:gerir")) == []


def test_quem_nao_supervisiona_o_processo_nao_ve_o_sinal(do_acervo):
    """A supressão é silenciosa, e é por espécie (`022`, FR-004).

    Anunciar que existe um sinal suprimido diria a quem não pode vê-lo que **há** algo para ver,
    que é vazamento por agregação.
    """
    de_fora = ator_institucional("estranho", "inscricao:consultar")

    assert do_quadro(do_acervo.processo, de_fora) == []


def test_o_sinal_some_depois_de_a_linha_ser_declarada(do_acervo, supervisora, api_client):
    """O ciclo fecha: declarada a quantidade, o Edital sai da lista."""
    from processo_seletivo.publicacoes.application.selectors import effective_version
    from processo_seletivo.publicacoes.domain.elevacao import elevar
    from tests.fixtures.publicacao import retify

    perfil = elevar(effective_version(edital_id=do_acervo.id).content)["profiles"][0]
    retify(
        api_client,
        do_acervo,
        [
            {
                "operation": "ADD",
                "targetPath": f"/profiles/id={perfil['id']}/vacancyTable/-",
                "newValue": {
                    "id": "00000000-0000-0000-0000-0000000009d1",
                    "modalityId": None,
                    "immediateVacancies": perfil["immediateVacancies"],
                },
            }
        ],
    )

    assert do_quadro(do_acervo.processo, supervisora) == []


def test_o_perfil_do_acervo_com_zero_vagas_tambem_aparece(
    api_client, manager_headers, process_payload, supervisora
):
    """**Zero é uma declaração, e ausência não é zero** (`025`, D-005; 027, FR-331, SC-108).

    Um Perfil legado que publica `0` vaga imediata e nenhuma linha continua sem dizer quanto a
    ampla concorrência tem: a Ocupação responde "não publicou quadro", e não "zero". São
    afirmações diferentes, e é a distinção que a `025` fixou.

    Descartar o `0` faria a FR-331 alcançar **quase** todo o acervo em vez de todo ele — e a forma
    existe: o `TEC-LAB` da própria demonstração publica zero vaga imediata.
    """
    from tests.fixtures.edital import complete_draft

    rascunho = complete_draft()
    rascunho["profiles"][0]["immediateVacancies"] = 0
    edital = publicar_na_versao_anterior(
        api_client, manager_headers, process_payload, draft=rascunho, versao=11
    )

    sinais = do_quadro(edital.processo, supervisora)

    assert len(sinais) == 1, "o Perfil de zero vaga sem quadro não pode ficar invisível"
    assert "publica 0 vaga(s) imediata(s)" in sinais[0].mensagem


# ---------------------------------------------------------------------------
# O sinal que fica diz a quem pedir (045, US4)
# ---------------------------------------------------------------------------


def test_quem_nao_retifica_recebe_a_quem_pedir(do_acervo, supervisora):
    """`045`, `FR-740` — o teste 8 da proposta: sem caminho, o sinal diz a permissão e o que pedir.

    Era a frase solta que a convergência de 20/09 contou nove vezes na Atenção do gestor. Sai do
    mecanismo único, e não é redigida no painel.
    """
    from processo_seletivo.interface.conducao import CONDUCAO_DA_RETIFICACAO

    sinal = do_quadro(do_acervo.processo, supervisora)[0]

    assert sinal.destino is None
    assert sinal.conducao == CONDUCAO_DA_RETIFICACAO


def test_quem_retifica_recebe_o_caminho_e_nao_a_frase(do_acervo):
    """037, `FR-544`: "peça a alguém" a quem tem o formulário à frente é falso."""
    quem_retifica = ator_institucional("bruno", "comissao:gerir", "retificacao:elaborar")

    sinal = do_quadro(do_acervo.processo, quem_retifica)[0]

    assert sinal.destino is not None
    assert sinal.conducao == ""


@pytest.mark.parametrize("estado", ["ENCERRADO", "CANCELADO"])
def test_onde_ninguem_pode_retificar_o_sinal_nao_e_condicao_de_atencao(
    do_acervo, supervisora, estado
):
    """`045`, `FR-741` e `D-003`: Retificação só incide sobre Edital publicado.

    Num Edital encerrado ou cancelado ninguém pratica o ato, e não há a quem pedir: o sinal que
    apontava para ele ficava para sempre, sem caminho e sem frase. O fato continua no conteúdo
    publicado; o que sai é a pendência que nenhuma tela resolve.
    """
    from processo_seletivo.processos.models import Edital

    quem_retifica = ator_institucional("bruno", "comissao:gerir", "retificacao:elaborar")
    Edital.objects.filter(pk=do_acervo.pk).update(status=getattr(Edital.Status, estado))

    assert do_quadro(do_acervo.processo, supervisora) == []
    assert do_quadro(do_acervo.processo, quem_retifica) == []


def test_num_processo_em_estado_final_o_sinal_nao_e_condicao_de_atencao(do_acervo, supervisora):
    """`045`, `FR-741`: Processo em estado final não admite alteração dos seus Editais."""
    from processo_seletivo.processos.models import ProcessoSeletivo

    ProcessoSeletivo.objects.filter(pk=do_acervo.processo_id).update(
        status=ProcessoSeletivo.Status.CANCELADO
    )
    do_acervo.processo.refresh_from_db()

    assert do_quadro(do_acervo.processo, supervisora) == []


def test_a_medida_diz_o_que_conta(do_acervo, supervisora):
    """`045`, `FR-743`, `UX-087`: *"1 de 1 recorte"*, e a mensagem não repete os números."""
    sinal = do_quadro(do_acervo.processo, supervisora)[0]

    assert sinal.medida.unidade_legivel == "recorte"
    assert "1 de 1" not in sinal.mensagem
