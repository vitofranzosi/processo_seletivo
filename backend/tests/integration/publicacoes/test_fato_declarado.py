"""O Edital declara os fatos que exige, e a identidade deles atravessa tudo (015, D-2).

Três provas. A primeira é o percurso: declarar, publicar, retificar — com os identificadores
**preservados**, porque é por eles que o valor congelado na inscrição dirá de qual fato é.

A segunda é a guarda de identidade alheia, no nível do contêiner: um fato de outro Perfil não pode
ser reparentado por uma gravação de rascunho.

A terceira é a semântica que o tipo carrega: **mudar o tipo é criar fato novo**. A Retificação não
oferece esse campo, e a razão está escrita no catálogo — reinterpretar um valor já congelado seria
o sistema decidindo o que a pessoa quis dizer.
"""

import pytest

from processo_seletivo.editais.models.perfis import FatoDeclarado
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import create_retification, publish_original, publish_retification
from tests.fixtures.snapshot import PERFIL, rascunho_com_etapas

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

NASCIMENTO = "00000000-0000-0000-0000-000000000561"
EXPERIENCIA = "00000000-0000-0000-0000-000000000562"


def fato(identificador, sigla, rotulo, tipo):
    return {"id": identificador, "code": sigla, "label": rotulo, "type": tipo}


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    rascunho = rascunho_com_etapas()
    perfil = next(item for item in rascunho["profiles"] if item["id"] == PERFIL["B"])
    perfil["declaredFacts"] = [
        fato(NASCIMENTO, "NASCIMENTO", "Data de nascimento", "DATA"),
        fato(EXPERIENCIA, "EXPERIENCIA", "Meses de experiência", "INTEIRO"),
    ]
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho)


def fatos_publicados(edital):
    conteudo = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content
    perfil = next(item for item in conteudo["profiles"] if item["id"] == PERFIL["B"])
    return perfil["declaredFacts"]


def test_os_fatos_declarados_chegam_ao_conteudo_publicado(publicado):
    # A emissão ordena por `code`, e não pela ordem de declaração: dois snapshots do mesmo
    # conteúdo precisam ter os mesmos bytes, e a ordem de inserção não é determinística.
    assert [item["id"] for item in fatos_publicados(publicado)] == [EXPERIENCIA, NASCIMENTO]
    assert [item["code"] for item in fatos_publicados(publicado)] == ["EXPERIENCIA", "NASCIMENTO"]


def test_retificar_o_rotulo_preserva_a_identidade_do_fato(api_client, publicado):
    """O que a inscrição congelou continua apontando para o mesmo fato depois da Retificação."""
    mudanca = [
        {
            "targetPath": f"/profiles/id={PERFIL['B']}/declaredFacts/id={NASCIMENTO}/label",
            "operation": "REPLACE",
            "newValue": "Data de nascimento (dd/mm/aaaa)",
        }
    ]

    publish_retification(api_client, create_retification(api_client, publicado, mudanca))

    depois = {item["id"]: item for item in fatos_publicados(publicado)}
    assert set(depois) == {NASCIMENTO, EXPERIENCIA}, "os identificadores são os mesmos de antes"
    assert depois[NASCIMENTO]["label"] == "Data de nascimento (dd/mm/aaaa)"
    assert depois[NASCIMENTO]["type"] == "DATA", "retificar o rótulo não toca o tipo"


def test_a_identidade_de_fato_de_outro_perfil_e_recusada(
    api_client, manager_headers, process_payload
):
    """A guarda é no nível do contêiner: o fato pertence ao Perfil, e não ao Edital.

    Sem ela, dois Perfis irmãos trocariam a identidade dos seus fatos sem que nada acusasse — e a
    identidade estável passaria a designar outra exigência normativa. A verificação acontece na
    **gravação do rascunho**, que é onde a identidade é recebida de fora.
    """
    from processo_seletivo.processos.models import Edital

    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    preparador = actor_headers("preparador", ["edital:elaborar"], key="rascunho-fato")

    primeiro = rascunho_com_etapas()
    perfil_b = next(item for item in primeiro["profiles"] if item["id"] == PERFIL["B"])
    perfil_b["declaredFacts"] = [fato(NASCIMENTO, "NASCIMENTO", "Data de nascimento", "DATA")]
    gravado = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        primeiro,
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"1"'},
    )
    assert gravado.status_code == 200, gravado.content

    segundo = rascunho_com_etapas()
    perfil_a = next(item for item in segundo["profiles"] if item["id"] == PERFIL["A"])
    perfil_a["declaredFacts"] = [fato(NASCIMENTO, "ROUBADO", "Fato de outro Perfil", "DATA")]
    recusa = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        segundo,
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="rascunho-alheio"),
            "HTTP_IF_MATCH": '"2"',
        },
    )

    # 409, e não 422: reparentar identidade é conflito com o que já está gravado, e a casa já
    # nomeia a recusa — `identifier_belongs_to_another_edital`, a mesma da Modalidade.
    assert recusa.status_code == 409, recusa.content
    assert recusa.json()["code"] == "identifier_belongs_to_another_edital"
    assert str(FatoDeclarado.objects.get(pk=NASCIMENTO).perfil_id) == PERFIL["B"]


NOVO = "00000000-0000-0000-0000-000000000563"


def test_trocar_o_tipo_do_fato_no_lugar_e_recusado(api_client, publicado):
    """Mudar o tipo não é editar o fato — é criar outro (FR-058).

    O catálogo da interface não oferece o campo, mas a API não é a interface: sem esta recusa,
    publicava-se por Retificação um `type` novo sobre um fato cujo valor já podia estar congelado,
    e o valor antigo passaria a ser lido sob outra grandeza.
    """
    base = VersaoConsolidada.objects.filter(edital=publicado).latest("materialized_at")

    recusa = api_client.post(
        f"/api/v1/admin/editais/{publicado.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Trocar o tipo do fato",
            "changes": [
                {
                    "targetPath": f"/profiles/id={PERFIL['B']}/declaredFacts/id={NASCIMENTO}/type",
                    "operation": "REPLACE",
                    "newValue": "INTEIRO",
                }
            ],
        },
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"], key="retificacao-tipo-0001"),
    )

    assert recusa.status_code == 422, recusa.content
    assert recusa.json()["code"] == "invalid_change"
    assert {item["id"]: item["type"] for item in fatos_publicados(publicado)}[NASCIMENTO] == "DATA"


def test_remover_o_fato_e_acrescentar_outro_continua_permitido(api_client, publicado):
    """A contraprova, e é ela que faz a recusa acima ser uma regra e não um bloqueio.

    O caminho normativo para mudar o tipo existe: remove-se um fato e acrescenta-se outro, com
    identidade própria. O que foi congelado sob o primeiro continua apontando para ele.
    """
    troca = [
        {
            "targetPath": f"/profiles/id={PERFIL['B']}/declaredFacts/id={NASCIMENTO}",
            "operation": "REMOVE",
        },
        {
            "targetPath": f"/profiles/id={PERFIL['B']}/declaredFacts/-",
            "operation": "ADD",
            "newValue": {
                "id": NOVO,
                "code": "NASCIMENTO_ANO",
                "label": "Ano de nascimento",
                "type": "INTEIRO",
            },
        },
    ]

    publish_retification(api_client, create_retification(api_client, publicado, troca))

    depois = {item["id"]: item for item in fatos_publicados(publicado)}
    assert NASCIMENTO not in depois, "o fato antigo saiu do conteúdo vigente"
    assert depois[NOVO]["type"] == "INTEIRO"
    assert depois[NOVO]["code"] == "NASCIMENTO_ANO"
