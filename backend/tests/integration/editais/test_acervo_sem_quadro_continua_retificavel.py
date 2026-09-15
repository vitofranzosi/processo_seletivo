"""O acervo publicado sem quadro continua retificável, e ganha linha por ato (027, FR-323, FR-332).

**A armadilha que este arquivo existe para travar.** `retificacoes.py` afere o conteúdo que o ato
produziria com `blocking_findings(validate_for_publication(content))`. A exigência da linha geral,
escrita sem o recorte do ato, bloquearia **toda** Retificação de **todo** Edital do acervo —
inclusive as que corrigem uma data e nada têm com vagas. O defeito não apareceria em nenhum teste
de composição: só apareceria no dia em que alguém tentasse corrigir um Edital antigo.

Por isso o par é obrigatório: a recusa da T009 e este teste entram no mesmo passo.

O acervo é simulado como ele realmente é — Publicação em versão canônica anterior ao degrau que
criou o quadro —, e não por `UPDATE`: publicação é append-only por trigger desde a `002`.
"""

import pytest

from processo_seletivo.publicacoes.domain.elevacao import elevar
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.legado import publicar_na_versao_anterior
from tests.fixtures.publicacao import retify

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def do_acervo(api_client, manager_headers, process_payload):
    """Edital publicado antes de o quadro de vagas existir — a condição de 100% do acervo."""
    return publicar_na_versao_anterior(api_client, manager_headers, process_payload)


def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def conteudo_vigente(edital):
    """Elevado, que é como todo leitor o enxerga.

    O que está **gravado** é o conteúdo da versão canônica em que foi publicado, e ele não é
    reescrito nunca; a elevação acontece na leitura. Um Edital do acervo tem `vacancyTable` ausente
    no que está gravado e **vazio** no que se lê — e vazio é a grafia da ausência (025, D-005).
    """
    return elevar(vigente(edital).content)


def test_o_acervo_nasce_sem_linha_de_quadro(do_acervo):
    """A premissa dos demais: sem isto, eles provariam outra coisa."""
    perfil = conteudo_vigente(do_acervo)["profiles"][0]
    assert perfil["vacancyTable"] == []
    assert perfil["immediateVacancies"] >= 1


def test_retificar_a_descricao_de_edital_sem_quadro_passa(api_client, do_acervo):
    """A armadilha 2, e a razão de a FR-323 recortar a exigência pelo ato.

    Esta Retificação não tem nada com vagas. Se a ausência de linha geral fosse impeditiva aqui, o
    acervo inteiro ficaria preso — e coagir a declarar o quadro seria o mecanismo errado: quem diz
    quem precisa do ato é a FR-331, e quem aponta o ato é a FR-332.
    """
    retify(
        api_client,
        do_acervo,
        [{"operation": "REPLACE", "targetPath": "/description", "newValue": "Descrição corrigida"}],
    )

    assert vigente(do_acervo).content["description"] == "Descrição corrigida"


def test_o_acervo_ganha_a_linha_geral_por_retificacao(api_client, do_acervo):
    """O caminho que a `025` abriu e a `026` obrigou a existir na tela (FR-332, SC-109)."""
    perfil = conteudo_vigente(do_acervo)["profiles"][0]
    total = perfil["immediateVacancies"]

    retify(
        api_client,
        do_acervo,
        [
            {
                "operation": "ADD",
                "targetPath": f"/profiles/id={perfil['id']}/vacancyTable/-",
                "newValue": {
                    "id": "00000000-0000-0000-0000-0000000009a1",
                    "modalityId": None,
                    "immediateVacancies": total,
                },
            }
        ],
    )

    linhas = conteudo_vigente(do_acervo)["profiles"][0]["vacancyTable"]
    assert [(linha["modalityId"], linha["immediateVacancies"]) for linha in linhas] == [
        (None, total)
    ]


def test_nenhum_conteudo_publicado_anterior_e_reescrito(api_client, do_acervo):
    """FR-333 e SC-110: o acervo só muda por ato, e o que ficou para trás continua legível."""
    original = vigente(do_acervo)
    antes = original.content

    retify(
        api_client,
        do_acervo,
        [{"operation": "REPLACE", "targetPath": "/description", "newValue": "Outra"}],
    )

    original.refresh_from_db()
    assert original.content == antes, "a versão anterior foi reescrita — publicação é ato imutável"
    assert vigente(do_acervo).id != original.id
