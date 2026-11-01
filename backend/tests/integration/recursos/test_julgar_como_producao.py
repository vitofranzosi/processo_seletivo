"""O julgamento com os privilégios da role de produção (A-01 da auditoria de prontidão de 31/10).

**O defeito.** `_protegido` travava o Resultado vigente com `select_for_update`, e
`resultados_resultadoetapa` é append-only: a política nega `UPDATE` à role de runtime, e o
PostgreSQL exige `UPDATE` para `FOR UPDATE`. Toda correção fixada e toda reavaliação determinada
terminavam em `permission denied` — `500` na tela de quem julga —, e a suíte, que roda como
superusuário, nunca viu. Estes casos rodam o ato sob `SET ROLE` da role de conformidade
(`tests/fixtures/papel_de_producao.py`), e foram eles que reproduziram o defeito antes da correção.

**Por que a trava saiu, e nada a substituiu.** A serialização já existia um degrau acima: `travar`
toma `FOR UPDATE` no `ProcessoSeletivo`, e todo caminho que cria Resultado — consolidar, registrar
ocorrência, desfechar convocação, julgar — passa por esse mesmo bloqueio. Quem chega em segundo
espera o primeiro terminar e só então lê o vigente, que já é o sucessor; a assinatura do que a tela
leu não confere, e a resposta é `409`. Atrás disso, `uq_resultado_sucessor_unico` e
`uq_decisao_por_recurso` continuam respondendo no banco. Os dois casos simultâneos abaixo provam a
fila com duas conexões de verdade, ambas como a role de produção.
"""

import threading
import time
from decimal import Decimal

import pytest
from django.db import connection, transaction
from django.urls import reverse

from processo_seletivo.processos.models import ProcessoSeletivo
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.papel_de_producao import assumir, como_producao, devolver  # noqa: F401
from tests.fixtures.recursos_us4 import JULGADORA, assinatura_de, cenario_julgavel, julgador
from tests.interface.conftest import identificar, seletor_ligado  # noqa: F401

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="privilégios validados somente em PostgreSQL"
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration, postgresql_only]


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    return cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=701, codigo="0701"
    )


def _argumentos(peca, **extra):
    return {
        "actor": julgador(),
        "recurso_id": peca["recurso"].id,
        "especie": DecisaoRecurso.Especie.CORRECAO_FIXADA,
        "motivacao": "O parecer não enfrentou o documento juntado na inscrição.",
        "etapa_id": peca["cenario"]["etapa"],
        "pontuacao": Decimal("82.0000"),
        "assinatura_do_resultado": str(peca["superado"].id),
        "idempotency_key": "julgar-como-producao",
        **extra,
    }


def _sucessores(peca):
    return ResultadoEtapa.objects.filter(resultado_anterior=peca["superado"])


# ---------------------------------------------------------------------------
# As espécies
# ---------------------------------------------------------------------------


def test_a_correcao_fixada_grava_decisao_e_sucessor(peca, como_producao):  # noqa: F811
    with como_producao():
        decisao, sucessor = julgar(**_argumentos(peca))

    assert decisao.especie == DecisaoRecurso.Especie.CORRECAO_FIXADA
    assert sucessor.resultado_anterior_id == peca["superado"].id
    assert sucessor.decisao_id == decisao.id
    assert sucessor.pontuacao == Decimal("82.0000")
    assert list(_sucessores(peca)) == [sucessor]


def test_a_reavaliacao_determinada_grava_a_decisao_sem_sucessor(peca, como_producao):  # noqa: F811
    with como_producao():
        decisao, sucessor = julgar(
            **_argumentos(
                peca,
                especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
                motivacao="Reavalie-se a prova didática por avaliador diverso.",
                pontuacao=None,
            )
        )

    assert sucessor is None
    assert decisao.resultado_protegido_id == peca["superado"].id
    assert not _sucessores(peca).exists()


def test_o_indeferimento_grava_a_decisao(peca, como_producao):  # noqa: F811
    with como_producao():
        decisao, sucessor = julgar(
            **_argumentos(
                peca,
                especie=DecisaoRecurso.Especie.INDEFERIDO,
                motivacao="A nota corresponde ao que foi entregue.",
                etapa_id=None,
                pontuacao=None,
                assinatura_do_resultado="",
            )
        )

    assert sucessor is None
    assert decisao.especie == DecisaoRecurso.Especie.INDEFERIDO


def test_a_tela_de_julgamento_conclui_a_correcao_fixada(
    client,
    seletor_ligado,  # noqa: F811
    peca,
    como_producao,  # noqa: F811
):
    """O caminho em que a auditoria viu o `500`: o `POST` da tela, como a julgadora o faz."""
    identificar(client, JULGADORA, ["julgador"])
    etapa = str(peca["cenario"]["etapa"])

    with como_producao():
        resposta = client.post(
            reverse("interface:recurso-julgar", args=[peca["recurso"].id]),
            {
                "especie": "CORRECAO_FIXADA",
                "motivacao": "Conferido o acervo, o documento consta e não foi pontuado.",
                "etapa": f"{etapa}|{peca['superado'].id}",
                f"pontuacao-{etapa}": "82,0000",
            },
        )

    assert resposta.status_code == 302, resposta.content[:400]
    assert DecisaoRecurso.objects.get(recurso=peca["recurso"]).especie == "CORRECAO_FIXADA"
    assert _sucessores(peca).count() == 1


# ---------------------------------------------------------------------------
# Repetição e revisão
# ---------------------------------------------------------------------------


def test_repetir_o_comando_devolve_a_mesma_decisao(peca, como_producao):  # noqa: F811
    """A segunda chamada com a mesma chave é resposta guardada, e não segundo ato."""
    argumentos = _argumentos(
        peca,
        especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
        motivacao="Reavalie-se a prova didática por avaliador diverso.",
        pontuacao=None,
    )
    with como_producao():
        primeira, _ = julgar(**argumentos)
        repetida, _ = julgar(**argumentos)

    assert repetida.pk == primeira.pk
    assert DecisaoRecurso.objects.count() == 1


# ---------------------------------------------------------------------------
# A repetição da correção fixada (doc/achado-repeticao-da-correcao-fixada.md)
#
# O sucessor que a correção cria é consolidado pela própria julgadora. Enquanto o impedimento era
# perguntado antes da reserva, a repetição a acusava de ter consolidado o Resultado que a decisão
# alcança, e respondia `403`. A reserva passou para antes do impedimento; os casos abaixo prendem
# o que isso pode e o que não pode mudar.
# ---------------------------------------------------------------------------


def _eventos():
    from processo_seletivo.auditoria.models import RegistroAuditoria

    return RegistroAuditoria.objects.count()


def test_repetir_a_correcao_fixada_recupera_a_decisao_sem_novo_ato(peca, como_producao):  # noqa: F811
    """FR-097: o desfecho original, sem linha nem evento novos — e não `403`."""
    with como_producao():
        primeira, sucessor = julgar(**_argumentos(peca))
        eventos = _eventos()
        repetida, _ = julgar(**_argumentos(peca))

    assert repetida.pk == primeira.pk
    assert DecisaoRecurso.objects.count() == 1
    assert list(_sucessores(peca)) == [sucessor]
    assert _eventos() == eventos


def test_a_mesma_chave_com_outro_conteudo_continua_em_conflito(peca, como_producao):  # noqa: F811
    """FR-098 — e a resposta não depende de a pessoa estar impedida agora."""
    with como_producao():
        julgar(**_argumentos(peca))
        with pytest.raises(DomainError) as recusa:
            julgar(**_argumentos(peca, pontuacao=Decimal("85.0000")))

    assert (recusa.value.code, recusa.value.status) == ("idempotency_conflict", 409)
    assert _sucessores(peca).count() == 1


def test_outra_pessoa_com_a_mesma_chave_nao_recupera_a_decisao(peca, como_producao):  # noqa: F811
    """A reserva é de quem praticou o ato: a mesma chave, em outra pessoa, é pedido novo."""
    with como_producao():
        julgar(**_argumentos(peca))
        with pytest.raises(DomainError) as recusa:
            julgar(**_argumentos(peca, actor=julgador("outra.julgadora")))

    assert recusa.value.status == 409
    assert recusa.value.code in {"stale_stage_result", "appeal_already_judged"}
    assert DecisaoRecurso.objects.count() == 1
    assert _sucessores(peca).count() == 1


@pytest.mark.parametrize("alvo", ["o mesmo recurso", "outro recurso do mesmo par"])
def test_quem_consolidou_pela_correcao_continua_impedida_de_ato_novo(
    peca,
    como_producao,  # noqa: F811
    alvo,
):
    """FR-039 intacta: só a repetição passou a ser respondida antes do impedimento."""
    recurso = peca["recurso"] if alvo == "o mesmo recurso" else None
    if recurso is None:
        recurso = _outro_recurso_sobre_o_mesmo_resultado(peca)
    with como_producao():
        _, sucessor = julgar(**_argumentos(peca))
        with pytest.raises(DomainError) as recusa:
            julgar(
                **_argumentos(
                    peca,
                    recurso_id=recurso.id,
                    assinatura_do_resultado=str(sucessor.id),
                    pontuacao=Decimal("88.0000"),
                    idempotency_key="ato-novo-de-quem-consolidou",
                )
            )

    assert (recusa.value.code, recusa.value.status) == ("appeal_judge_barred", 403)
    assert DecisaoRecurso.objects.count() == 1


def test_o_reenvio_da_tela_depois_do_sucesso_nao_mostra_impedimento(
    client,
    seletor_ligado,  # noqa: F811
    peca,
    como_producao,  # noqa: F811
):
    """O caminho em que o defeito aparecia: a chave da tela é fixa por peça."""
    identificar(client, JULGADORA, ["julgador"])
    etapa = str(peca["cenario"]["etapa"])
    formulario = {
        "especie": "CORRECAO_FIXADA",
        "motivacao": "Conferido o acervo, o documento consta e não foi pontuado.",
        "etapa": f"{etapa}|{peca['superado'].id}",
        f"pontuacao-{etapa}": "82,0000",
    }
    destino = reverse("interface:recurso-julgar", args=[peca["recurso"].id])

    with como_producao():
        primeira = client.post(destino, formulario)
        reenvio = client.post(destino, formulario)

    assert (primeira.status_code, reenvio.status_code) == (302, 302), reenvio.content[:400]
    assert reenvio["Location"] == primeira["Location"]
    assert DecisaoRecurso.objects.count() == 1
    assert _sucessores(peca).count() == 1


def test_o_resultado_lido_obsoleto_recusa_com_409(peca, como_producao):  # noqa: F811
    with como_producao(), pytest.raises(DomainError) as recusa:
        julgar(**_argumentos(peca, assinatura_do_resultado="outro-identificador"))

    assert (recusa.value.code, recusa.value.status) == ("stale_stage_result", 409)
    assert not DecisaoRecurso.objects.exists()


def test_a_segunda_decisao_sobre_o_mesmo_recurso_recusa_com_409(peca, como_producao):  # noqa: F811
    with como_producao():
        julgar(**_argumentos(peca))
        with pytest.raises(DomainError) as recusa:
            julgar(
                **_argumentos(
                    peca,
                    actor=julgador("outra.julgadora"),
                    idempotency_key="julgar-como-producao-b",
                )
            )

    assert recusa.value.status == 409
    assert DecisaoRecurso.objects.count() == 1
    assert _sucessores(peca).count() == 1


# ---------------------------------------------------------------------------
# A concorrência, com duas conexões de verdade
# ---------------------------------------------------------------------------


def _outro_recurso_sobre_o_mesmo_resultado(peca):
    """A mesma pessoa recorreu também da publicação do marco, e o recurso foi admitido.

    É o caminho real pelo qual duas decisões disputam o mesmo Resultado: a unicidade de decisão é
    por recurso, e não por par — só a fila do Processo e `uq_resultado_sucessor_unico` as separam.
    """
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato
    from processo_seletivo.recursos.application.admitir import admitir
    from processo_seletivo.recursos.application.interpor import interpor

    inscricao = peca["inscricao"]
    outro = interpor(
        identidade=IdentidadeDoCandidato(
            inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "c@ex.br"
        ),
        inscricao=inscricao,
        publicacao=peca["publicacao"],
        fundamentacao="A divulgação omitiu a minha posição.",
        assinatura_do_objeto=str(peca["publicacao"].pk),
        idempotency_key="interpor-outro-como-producao",
    )
    admitir(
        actor=julgador(),
        recurso_id=outro.id,
        admitido=True,
        motivo="Tempestivo.",
        assinatura_do_estado=assinatura_de(outro),
        idempotency_key="admitir-outro-como-producao",
    )
    return outro


def _esperando_trava(quantas, prazo=15.0):
    limite = time.monotonic() + prazo
    while time.monotonic() < limite:
        with connection.cursor() as cursor:
            # Dentro de uma transação a visão das estatísticas é congelada na primeira leitura;
            # sem limpá-la, o laço relia para sempre o instante em que ninguém esperava.
            cursor.execute("SELECT pg_stat_clear_snapshot()")
            cursor.execute(
                "SELECT count(*) FROM pg_stat_activity "
                "WHERE datname = current_database() AND wait_event_type = 'Lock'"
            )
            if cursor.fetchone()[0] >= quantas:
                return
        time.sleep(0.05)
    raise AssertionError(f"as {quantas} conexões não chegaram à trava do Processo")


def _simultaneos(peca, pedidos):
    """Roda cada pedido numa *thread*, com conexão própria e como a role de produção.

    O caso segura a trava do Processo até que todas estejam esperando por ela, e só então solta:
    sem isso, a primeira podia terminar antes de a segunda começar, e o caso provaria uma
    sequência, e não uma corrida.
    """
    desfechos = [None] * len(pedidos)

    def rodar(indice, argumentos):
        from django.db import connection as propria

        try:
            assumir(propria)
            try:
                desfechos[indice] = julgar(**argumentos)
            except Exception as exc:  # noqa: BLE001 — o desfecho é o que se examina
                desfechos[indice] = exc
            finally:
                devolver(propria)
        finally:
            propria.close()

    processo_id = peca["inscricao"].edital.processo_id
    threads = [
        threading.Thread(target=rodar, args=(indice, argumentos))
        for indice, argumentos in enumerate(pedidos)
    ]
    # **As threads terminam antes do caso, falhe a espera ou não.** Sem o `finally`, uma espera
    # vencida soltava a trava e saía com as threads ainda dentro de `julgar`: a fixture derrubava a
    # role debaixo delas (`invalid role OID`) e a conexão que sobrava travava o `DROP DATABASE`.
    try:
        with transaction.atomic():
            ProcessoSeletivo.objects.select_for_update().get(pk=processo_id)
            for thread in threads:
                thread.start()
            _esperando_trava(len(pedidos))
    finally:
        for thread in threads:
            if thread.ident is not None:  # só as que chegaram a começar
                thread.join(timeout=30)
        presas = [thread for thread in threads if thread.is_alive()]
        assert not presas, "uma thread não terminou: a conexão dela continua aberta"
    return desfechos


@pytest.mark.parametrize("disputa", ["mesmo recurso", "outro recurso do mesmo par"])
def test_dois_julgamentos_simultaneos_produzem_um_unico_sucessor(
    peca,
    como_producao,  # noqa: F811
    disputa,
):
    segundo = (
        peca["recurso"]
        if disputa == "mesmo recurso"
        else _outro_recurso_sobre_o_mesmo_resultado(peca)
    )
    desfechos = _simultaneos(
        peca,
        [
            _argumentos(peca, idempotency_key="corrida-a"),
            _argumentos(
                peca,
                actor=julgador("outra.julgadora"),
                recurso_id=segundo.id,
                pontuacao=Decimal("84.0000"),
                idempotency_key="corrida-b",
            ),
        ],
    )

    vitorias = [desfecho for desfecho in desfechos if isinstance(desfecho, tuple)]
    recusas = [desfecho for desfecho in desfechos if isinstance(desfecho, DomainError)]
    assert len(vitorias) == 1 and len(recusas) == 1, desfechos
    assert recusas[0].status == 409
    assert recusas[0].code in {"stale_stage_result", "appeal_already_judged"}
    assert DecisaoRecurso.objects.count() == 1
    assert list(_sucessores(peca)) == [vitorias[0][1]]
    # E o vigente do par é o da vitória: a fila não deixou dois "últimos".
    assert (
        ResultadoEtapa.vigentes.get(inscricao=peca["inscricao"], etapa_id=peca["cenario"]["etapa"])
        == vitorias[0][1]
    )
