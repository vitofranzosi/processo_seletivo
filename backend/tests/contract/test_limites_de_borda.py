"""FR-020 e FR-021 da 003 — a borda recusa o que a persistência não aguenta.

Campo maior que a coluna, cabeçalho fora do formato e instante sem fuso chegavam ao PostgreSQL e
viravam erro interno. 500 não é contrato: o cliente não consegue fazer nada com ele, e a
mensagem de erro do banco não é informação que deva sair da aplicação.
"""

import pytest

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import publish_original

pytestmark = pytest.mark.contract


def _criar(api_client, edital, changes, **headers):
    base = VersaoConsolidada.objects.get(edital=edital)
    return api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Limites de borda",
            "changes": changes,
        },
        format="json",
        **{
            **actor_headers("retificador", ["retificacao:elaborar"], key="borda-000000001"),
            **headers,
        },
    )


@pytest.mark.django_db(transaction=True)
def test_target_path_acima_da_coluna_e_recusado_sem_erro_interno(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)

    resposta = _criar(
        api_client,
        edital,
        [{"targetPath": "/" + "a" * 1000, "operation": "REPLACE", "newValue": "x"}],
    )

    # 422 é como o projeto responde a violação de contrato de campo; o que importa aqui é que a
    # recusa aconteça na borda e chegue como problema descrito, não como erro do banco.
    assert resposta.status_code == 422
    assert resposta["Content-Type"].startswith("application/problem+json")


@pytest.mark.django_db(transaction=True)
def test_hash_declarado_acima_da_coluna_e_recusado(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)

    resposta = _criar(
        api_client,
        edital,
        [
            {
                "targetPath": "/title",
                "operation": "REPLACE",
                "newValue": "x",
                "expectedPreviousHash": "f" * 65,
            }
        ],
    )

    assert resposta.status_code == 422


@pytest.mark.django_db(transaction=True)
def test_correlation_id_inutilizavel_nao_impede_a_requisicao_nem_vaza_para_a_resposta(
    api_client, manager_headers, process_payload
):
    """O cabeçalho é de diagnóstico e opcional: recusar a requisição seria desproporcional.

    O que não pode é ser aceito. A resposta ecoa sempre o identificador em uso, então o cliente
    que enviou um valor inutilizável vê de volta um diferente — a substituição é visível.
    """
    for ordem, declarado in enumerate(("c" * 200, "com\r\nquebra", ""), 1):
        resposta = api_client.post(
            "/api/v1/admin/processos",
            {
                **process_payload,
                "institutionalCode": f"PS-2026-{ordem:03d}",
                "firstEdital": {**process_payload["firstEdital"], "number": f"{ordem:02d}"},
            },
            format="json",
            **{
                **manager_headers,
                "HTTP_IDEMPOTENCY_KEY": f"borda-correlacao-{ordem:04d}",
                "HTTP_X_CORRELATION_ID": declarado,
            },
        )
        assert resposta.status_code == 201, resposta.content
        assert resposta["X-Correlation-ID"] != declarado
        assert len(resposta["X-Correlation-ID"]) <= 100


@pytest.mark.django_db(transaction=True)
def test_correlation_id_utilizavel_e_preservado(api_client, manager_headers, process_payload):
    resposta = api_client.post(
        "/api/v1/admin/processos",
        process_payload,
        format="json",
        **{**manager_headers, "HTTP_X_CORRELATION_ID": "corr-2026-08-29-0001"},
    )

    assert resposta.status_code == 201
    assert resposta["X-Correlation-ID"] == "corr-2026-08-29-0001"


@pytest.mark.django_db(transaction=True)
def test_instante_sem_fuso_e_recusado_na_consulta_temporal(
    api_client, manager_headers, process_payload
):
    """FR-021: sem fuso não há instante, e o do servidor tornaria o passado irreprodutível."""
    edital = publish_original(api_client, manager_headers, process_payload)
    url = f"/api/v1/public/editais/{edital.id}/versao-vigente"

    ingenuo = api_client.get(url, {"em": "2026-03-01T10:00:00"}, format="json")

    assert ingenuo.status_code == 400
    assert ingenuo.json()["code"] == "invalid_instant"
    assert "fuso" in ingenuo.json()["detail"]


@pytest.mark.django_db(transaction=True)
def test_instante_com_fuso_continua_valendo(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)
    url = f"/api/v1/public/editais/{edital.id}/versao-vigente"

    com_fuso = api_client.get(url, {"em": "2099-03-01T10:00:00-03:00"}, format="json")
    sem_parametro = api_client.get(url, format="json")

    assert com_fuso.status_code == 200
    assert sem_parametro.status_code == 200


# --- A topologia das seções e a coerência das Etapas depois da publicação (FR-041, D-011) ---
#
# A forma declarada confere um campo por vez e não expressa coerência entre campos. Sem estas duas
# verificações, uma Retificação faria sobre o conteúdo publicado o que a interface impede:
# desmontar o catálogo fixo e romper a fonte única — onde mais importa, depois de público.


def _identidade_da_secao(edital, chave):
    from processo_seletivo.editais.domain import secoes

    return str(secoes.identidade(edital.id, chave))


def _tentar_publicar(api_client, edital, changes, sufixo):
    """A recusa pode acontecer na elaboração ou na Publicação; o teste quer a que acontecer.

    A elaboração já confere a forma do conteúdo que a Retificação produziria — é o que a `005`
    entregou —, então a maioria destes casos morre ali. Tentar publicar o que passou é o que
    garante que nenhum deles escapa para o momento seguinte.
    """
    from processo_seletivo.publicacoes.models_retificacao import Retificacao
    from tests.fixtures.publicacao import try_publish_retification

    base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    criada = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": f"Retificação {sufixo}",
            "changes": changes,
        },
        format="json",
        **actor_headers(
            "retificador", ["retificacao:elaborar"], key=f"retificacao-{sufixo}-0001"
        ),
    )
    if criada.status_code != 201:
        return criada
    return try_publish_retification(
        api_client, Retificacao.objects.get(pk=criada.json()["id"]), suffix=sufixo
    )


def _edital_com_etapas(api_client, manager_headers, process_payload):
    from tests.fixtures.snapshot import rascunho_com_etapas

    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas()
    )


def _hash_de(edital, caminho):
    from processo_seletivo.publicacoes.domain.conflicts import previous_hash

    base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    return previous_hash(base.content, caminho)


def _replace(edital, caminho, valor):
    return [
        {
            "targetPath": caminho,
            "operation": "REPLACE",
            "newValue": valor,
            "expectedPreviousHash": _hash_de(edital, caminho),
        }
    ]


@pytest.mark.django_db(transaction=True)
def test_acrescentar_secao_fora_do_catalogo_e_recusado(
    api_client, manager_headers, process_payload
):
    edital = _edital_com_etapas(api_client, manager_headers, process_payload)
    nova = {
        "id": "00000000-0000-0000-0000-0000000009a1",
        "key": "secao-inventada",
        "title": "Seção inventada",
        "order": 8,
        "type": "TEXT",
        "content": "Texto qualquer",
    }

    resposta = _tentar_publicar(
        api_client,
        edital,
        [{"targetPath": "/sections/-", "operation": "ADD", "newValue": nova}],
        "s1",
    )

    assert resposta.status_code == 422, resposta.content
    assert resposta.json()["code"] == "blocking_findings"
    assert "não pertence ao catálogo" in resposta.json()["detail"]


@pytest.mark.django_db(transaction=True)
def test_remover_secao_do_catalogo_e_recusado(api_client, manager_headers, process_payload):
    edital = _edital_com_etapas(api_client, manager_headers, process_payload)
    caminho = f"/sections/id={_identidade_da_secao(edital, 'recursos')}"

    resposta = _tentar_publicar(
        api_client,
        edital,
        [
            {
                "targetPath": caminho,
                "operation": "REMOVE",
                "expectedPreviousHash": _hash_de(edital, caminho),
            }
        ],
        "s2",
    )

    assert resposta.status_code == 422, resposta.content
    assert "não está presente" in resposta.json()["detail"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    ("chave", "campo", "valor"),
    [
        ("recursos", "type", "GENERATED"),
        # 99, e não 9: `recursos` **é** a seção 9 desde a `007`, e reordená-la para a
        # própria posição não seria alteração de topologia — o caso deixaria de testar a recusa.
        ("recursos", "order", 99),
        ("recursos", "title", "Outro título"),
        ("cronograma", "source", "profiles"),
    ],
)
def test_alterar_a_topologia_de_uma_secao_e_recusado(
    api_client, manager_headers, process_payload, chave, campo, valor
):
    """Só o `content` das seções textuais varia. Tudo o mais é o catálogo, e o catálogo é fixo."""
    edital = _edital_com_etapas(api_client, manager_headers, process_payload)
    caminho = f"/sections/id={_identidade_da_secao(edital, chave)}/{campo}"

    resposta = _tentar_publicar(api_client, edital, _replace(edital, caminho, valor), "s3")

    assert resposta.status_code == 422, resposta.content
    assert "diverge do catálogo" in resposta.json()["detail"]


@pytest.mark.django_db(transaction=True)
def test_esvaziar_o_conteudo_de_secao_textual_e_recusado(
    api_client, manager_headers, process_payload
):
    edital = _edital_com_etapas(api_client, manager_headers, process_payload)
    caminho = f"/sections/id={_identidade_da_secao(edital, 'recursos')}/content"

    resposta = _tentar_publicar(api_client, edital, _replace(edital, caminho, "   "), "s4")

    assert resposta.status_code == 422, resposta.content
    assert "precisa de conteúdo" in resposta.json()["detail"]


@pytest.mark.django_db(transaction=True)
def test_dar_conteudo_a_secao_gerada_e_recusado(api_client, manager_headers, process_payload):
    """FR-040: dois endereços para o mesmo conteúdo, e nenhum jeito de dizer qual vigora."""
    edital = _edital_com_etapas(api_client, manager_headers, process_payload)
    caminho = f"/sections/id={_identidade_da_secao(edital, 'cronograma')}/content"

    resposta = _tentar_publicar(
        api_client,
        edital,
        [{"targetPath": caminho, "operation": "ADD", "newValue": "Cronograma copiado à mão"}],
        "s5",
    )

    assert resposta.status_code == 422, resposta.content
    assert "não carrega conteúdo próprio" in resposta.json()["detail"]


@pytest.mark.django_db(transaction=True)
def test_etapa_que_referencia_evento_inexistente_e_recusada_na_publicacao(
    api_client, manager_headers, process_payload
):
    """A forma declarada confere que é um UUID, não que ele exista."""
    from tests.fixtures.snapshot import ETAPA

    edital = _edital_com_etapas(api_client, manager_headers, process_payload)
    caminho = f"/stages/id={ETAPA['A']}/scheduleEventId"

    resposta = _tentar_publicar(
        api_client,
        edital,
        _replace(edital, caminho, "00000000-0000-0000-0000-0000000009ff"),
        "e1",
    )

    assert resposta.status_code == 422, resposta.content
    assert "não existe no Cronograma" in resposta.json()["detail"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    ("campo", "valor", "razao"),
    [
        ("weight", "2", "casas de menos"),
        ("weight", "2.00", "casas de menos"),
        ("weight", "2.00000", "casas demais"),
        ("weight", "001.0000", "zero à esquerda, forma que o sistema nunca escreve"),
        ("weight", "1234.0000", "inteiro longo demais para decimal(7,4)"),
        ("weight", "banana", "nem número é"),
        ("minimumScore", "7", "casas de menos"),
    ],
)
def test_decimal_fora_da_forma_canonica_e_recusado(
    api_client, manager_headers, process_payload, campo, valor, razao
):
    """O padrão descreve a **forma** que a persistência materializa, e só ela.

    `001.0000` é o caso que a segunda versão do padrão deixava passar: forma que o sistema nunca
    escreve, e pela qual uma Retificação semanticamente nula alteraria o hash do conteúdo.
    """
    from tests.fixtures.snapshot import ETAPA

    edital = _edital_com_etapas(api_client, manager_headers, process_payload)
    caminho = f"/stages/id={ETAPA['A']}/{campo}"

    resposta = _tentar_publicar(api_client, edital, _replace(edital, caminho, valor), "e2")

    assert resposta.status_code == 422, f"{razao}: {resposta.content}"
    assert "formato decimal" in resposta.json()["detail"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    ("campo", "valor", "mensagem"),
    [
        ("weight", "0.0000", "maior que zero"),
        ("weight", "-2.0000", "maior que zero"),
        ("minimumScore", "-1.0000", "não pode ser negativa"),
    ],
)
def test_faixa_do_decimal_e_recusada_pela_verificacao_de_coerencia(
    api_client, manager_headers, process_payload, campo, valor, mensagem
):
    """A faixa não vem do padrão: o padrão admite o sinal de propósito.

    Deixar a expressão regular recusar o sinal misturaria forma com permissão, e foi assim que uma
    invariante não declarada entrou por uma regex numa versão anterior deste plano.
    """
    from tests.fixtures.snapshot import ETAPA

    edital = _edital_com_etapas(api_client, manager_headers, process_payload)
    caminho = f"/stages/id={ETAPA['A']}/{campo}"

    resposta = _tentar_publicar(api_client, edital, _replace(edital, caminho, valor), "e3")

    assert resposta.status_code == 422, resposta.content
    assert mensagem in resposta.json()["detail"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("percentual", ["0.0000", "150.0000", "-1.0000"])
def test_retificacao_nao_contorna_a_faixa_do_percentual(
    api_client, manager_headers, process_payload, percentual
):
    """FR-030 vale também depois da publicação.

    A faixa era verificada só na gravação do rascunho. A Retificação passa por
    `validate_for_publication`, que confere que cada modalidade é objeto e nada dentro dela — de
    modo que uma cota de zero por cento, ou de cento e cinquenta, podia ser publicada pelo caminho
    em que o conteúdo muda **depois** de público, que é justamente onde mais importa.
    """
    from processo_seletivo.publicacoes.domain.conflicts import previous_hash
    from tests.fixtures.snapshot import MODALIDADE, PERFIL
    from tests.fixtures.snapshot import rascunho_publicavel as rascunho

    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho())
    base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    caminho = (
        f"/profiles/id={PERFIL['A']}/competitionModalities/id={MODALIDADE['B']}"
        "/normativeRule/percentage"
    )

    resposta = _tentar_publicar(
        api_client,
        edital,
        [
            {
                "targetPath": caminho,
                "operation": "REPLACE",
                "newValue": percentual,
                "expectedPreviousHash": previous_hash(base.content, caminho),
            }
        ],
        "q1",
    )

    assert resposta.status_code == 422, resposta.content
    assert "maior que zero e menor ou igual a cem" in resposta.json()["detail"]
    assert caminho in resposta.json()["detail"]
