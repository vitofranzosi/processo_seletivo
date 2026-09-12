"""Fluxos completos de Publicação e Retificação reutilizados pelos testes de US4 a US6."""

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.edital import actor_headers, complete_draft

SIGNATORY = {
    "authorityId": "00000000-0000-0000-0000-000000000601",
    "name": "Diretora",
    "role": "Diretora-Geral",
}


def publish_original(
    api_client, manager_headers, process_payload, *, draft=None, anexos=0, antes_de_submeter=None
):
    """Cria Processo e primeiro Edital e o leva até a primeira Publicação.

    `anexos` cria essa quantidade de Anexos entre o rascunho e a submissão. Não é opção de
    conveniência: a coleção fica fora do `replace_draft`, então não há como pedi-la pelo payload —
    e o padrão é zero porque Edital sem anexo continua sendo Edital (020, FR-024).

    `antes_de_submeter` recebe o Edital na mesma janela, e existe pela mesma razão: o vínculo entre
    requisito e modelo é campo de elaboração, e precisa estar de pé **antes** de o snapshot ser
    congelado para que o conteúdo publicado o carregue. Sem isso, testar o modelo publicado
    dependeria de uma Retificação — e de um congelamento que só a US3 traz.
    """
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    # Escopado ao Processo: o helper precisa servir a testes com mais de um Edital.
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    return levar_a_publicacao(
        api_client,
        edital,
        draft=draft,
        anexos=anexos,
        antes_de_submeter=antes_de_submeter,
    )


def levar_a_publicacao(
    api_client,
    edital,
    *,
    draft=None,
    anexos=0,
    antes_de_submeter=None,
    chave="publication-key-0001",
):
    """De rascunho a publicado, sobre um Edital que já existe.

    Saiu de dentro de `publish_original` quando a `022` precisou de **dois Editais no mesmo
    Processo**: o helper anterior criava sempre um Processo novo, e a soma acima do Edital não tinha
    como ser montada. Duplicar as quatro chamadas num segundo lugar faria o ciclo de publicação ter
    duas versões que envelheceriam separadamente.

    `chave` distingue as reservas de idempotência: elas são por ator, operação e chave, e repetir a
    mesma com outro conteúdo é conflito — corretamente.
    """
    preparer = actor_headers("preparador", ["edital:elaborar", "edital:submeter"], key=chave)
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        draft or complete_draft(),
        format="json",
        **{**preparer, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )
    if anexos:
        from tests.fixtures.anexos import criar_anexo

        for posicao in range(anexos):
            criar_anexo(
                edital,
                rotulo=f"ANEXO {posicao + 1} — FORMULÁRIO",
                order=posicao + 1,
                marca=chr(ord("A") + posicao),
            )
    if antes_de_submeter is not None:
        antes_de_submeter(edital)
    edital.refresh_from_db()
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparer, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )
    edital.refresh_from_db()
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{
            **actor_headers("homologador", ["edital:homologar"], key=chave),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )
    edital.refresh_from_db()
    published = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes",
        {"signatory": SIGNATORY},
        format="json",
        **{
            **actor_headers("publicador", ["edital:publicar"], key=chave),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )
    assert published.status_code == 201, published.content
    return Edital.objects.get(pk=edital.pk)


def create_retification(
    api_client, edital, changes, *, effective_at=None, suffix="a", base=None, esperar=201
):
    """`base` é a versão sobre a qual o ato é elaborado; por padrão, a mais recente.

    Quando a Retificação vigora antes de outra já publicada, a versão mais recente não é a que
    vigora no início da sua vigência — e a precondição de conteúdo é verificada contra esta,
    não contra aquela. Nesse caso o teste declara a base explicitamente, como faria o cliente.
    """
    base = base or VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    payload = {
        "baseSnapshotId": str(base.id),
        "justification": f"Retificação {suffix}",
        "changes": changes,
    }
    if effective_at is not None:
        payload["effectiveAt"] = effective_at
    created = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        payload,
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"], key=f"retificacao-{suffix}-0001"),
    )
    assert created.status_code == esperar, created.content
    if esperar != 201:
        # O caso negativo devolve o corpo do problema, e não uma Retificação — quem chama quer
        # afirmar **qual** recusa aconteceu, e não que alguma aconteceu.
        return created.json()
    return Retificacao.objects.get(pk=created.json()["id"])


def try_publish_retification(api_client, retificacao, *, suffix="a"):
    """Submete, homologa e tenta publicar, devolvendo a resposta **sem exigir sucesso**.

    Existe para os cenários que só se enxergam na Publicação: a Retificação precisa atravessar
    o ciclo inteiro para que a recusa aconteça no momento certo, e o teste quer ler a recusa.
    """
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/submissoes",
        format="json",
        **{
            **actor_headers(
                "retificador", ["retificacao:submeter"], key=f"retificacao-{suffix}-0002"
            ),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{
            **actor_headers(
                "homologador-r", ["retificacao:homologar"], key=f"retificacao-{suffix}-0003"
            ),
            "HTTP_IF_MATCH": '"2"',
        },
    )
    return api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/publicacoes",
        {"signatory": SIGNATORY},
        format="json",
        **{
            **actor_headers(
                "publicador-r", ["retificacao:publicar"], key=f"retificacao-{suffix}-0004"
            ),
            "HTTP_IF_MATCH": '"3"',
        },
    )


def publish_retification(api_client, retificacao, *, suffix="a"):
    """Submete, homologa e publica uma Retificação já criada, exigindo que ela publique."""
    published = try_publish_retification(api_client, retificacao, suffix=suffix)
    assert published.status_code == 201, published.content
    retificacao.refresh_from_db()
    return retificacao


def retify(api_client, edital, changes, *, effective_at=None, suffix="a"):
    """Cria e publica uma Retificação em um passo."""
    retificacao = create_retification(
        api_client, edital, changes, effective_at=effective_at, suffix=suffix
    )
    return publish_retification(api_client, retificacao, suffix=suffix)
