"""O juízo de admissibilidade — e a tempestividade, que é outra coisa.

**Receber a peça não é admiti-la.** Entre a interposição e o julgamento do mérito há um juízo
próprio, e ele é motivado **nas duas direções**: exigir motivo só na inadmissão faria a admissão
parecer automática, e ela não é — é a afirmação de que a peça é própria, tempestiva e regularmente
instruída (FR-031, FR-032).

**A tempestividade muda de lugar conforme a norma.** Onde o Edital declara janela, a interposição
fora do prazo já foi recusada e não há o que apreciar aqui (FR-033). Onde não declara — que é todo
Edital enquanto o degrau 8 não existir —, ela é juízo humano, e o motivo é onde ele se escreve
(FR-034, FR-035).
"""

import uuid
from datetime import timedelta

import pytest
from django.db.utils import ProgrammingError
from django.utils.timezone import now

from processo_seletivo.publicacoes.application.selectors import selecao_publica
from processo_seletivo.recursos.application.admitir import admitir
from processo_seletivo.recursos.application.selectors import (
    DENTRO,
    FORA,
    SEM_JANELA,
    assinatura_do_estado_da_peca,
    recursos_do_edital,
)
from processo_seletivo.recursos.models import DecisaoRecurso, JuizoDeAdmissibilidade
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.divulgacao import emitir, montar_marco, pontuar, publicar_o_ato
from tests.fixtures.recursos import interpor

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

JULGADORA = "helena.julgadora"


def julgador(subject=JULGADORA):
    return ator_institucional(subject, "recurso:julgar")


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    cenario = montar_marco(
        gestor, api_client, manager_headers, process_payload, seed=99, codigo="0799"
    )
    cenario["inscricoes"] = pontuar(cenario, gestor, ["90.0000"], primeiro=991, sufixo="99")
    cenario["ato"] = emitir(cenario, gestor, chave="emitir-018-us3b")
    publicar_o_ato(cenario, chave="publicar-018-us3b")
    inscricao = cenario["inscricoes"][0]
    recurso = interpor(
        inscricao=inscricao,
        versao=selecao_publica(edital_id=inscricao.edital_id),
        resultado=ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"]),
        protocolo="REC-2026-US30010",
    )
    return {"cenario": cenario, "recurso": recurso, "inscricao": inscricao}


def apreciar(peca, *, admitido=True, motivo="Tempestivo e regularmente instruído.", **extra):
    argumentos = {
        "actor": julgador(),
        "recurso_id": peca["recurso"].id,
        "admitido": admitido,
        "motivo": motivo,
        "assinatura_do_estado": "",
        "idempotency_key": "apreciar-us3b",
    }
    return admitir(**{**argumentos, **extra})


# ---------------------------------------------------------------------------
# T054 — o juízo
# ---------------------------------------------------------------------------


def test_o_juizo_nasce_motivado_com_autor_e_instante(peca):
    antes = now()

    juizo = apreciar(peca)

    assert juizo.admitido is True
    assert juizo.motivo == "Tempestivo e regularmente instruído."
    assert juizo.decidido_por == JULGADORA
    assert antes <= juizo.decidido_em <= now()


def test_a_inadmissao_tambem_e_motivada(peca):
    """A assimetria de exigir motivo só aqui faria a admissão parecer automática (FR-032)."""
    juizo = apreciar(peca, admitido=False, motivo="Interposto fora do prazo razoável.")

    assert juizo.admitido is False
    assert juizo.motivo == "Interposto fora do prazo razoável."


def test_motivo_vazio_e_recusado_nas_duas_direcoes(peca):
    for admitido in (True, False):
        with pytest.raises(DomainError) as recusa:
            apreciar(peca, admitido=admitido, motivo="   \n ")
        assert recusa.value.code == "appeal_reason_required"
        assert recusa.value.status == 422
    assert not JuizoDeAdmissibilidade.objects.exists()


def test_o_segundo_juizo_e_recusado_pela_constraint(peca):
    """Um juízo por recurso: `uq_juizo_por_recurso` responde, e a leitura prévia não existe.

    Consultar antes seria conforto de mensagem que a corrida desfaz de todo jeito — e a `409` é o
    que impede que a segunda apreciação vire erro 500 numa tela administrativa.
    """
    apreciar(peca)

    with pytest.raises(DomainError) as recusa:
        apreciar(peca, admitido=False, motivo="Mudei de ideia.", idempotency_key="outra-us3b")

    assert recusa.value.code == "appeal_already_reviewed"
    assert recusa.value.status == 409
    assert JuizoDeAdmissibilidade.objects.count() == 1


def test_a_mesma_chave_devolve_o_desfecho_da_primeira(peca):
    primeiro = apreciar(peca)
    segundo = apreciar(peca)

    assert segundo.pk == primeiro.pk
    assert JuizoDeAdmissibilidade.objects.count() == 1


def test_julgar_o_nao_admitido_e_recusado_pelo_gatilho(peca):
    """Julgar o mérito exige juízo positivo — e quem responde é o banco (FR-036).

    A garantia é da trigger `decisao_recurso_coerente`, e não do comando: ela vale para qualquer
    caminho de gravação, inclusive o que ainda não existe.
    """
    apreciar(peca, admitido=False, motivo="Intempestivo.")

    # `RAISE EXCEPTION` numa função PL/pgSQL chega como `ProgrammingError`, e não `IntegrityError`
    # — a distinção é do driver, e não do domínio. A asserção prende a **mensagem**, que é o que
    # diz qual invariante respondeu.
    with pytest.raises(ProgrammingError, match="not admitted"):
        DecisaoRecurso.objects.create(
            recurso=peca["recurso"],
            especie=DecisaoRecurso.Especie.INDEFERIDO,
            motivacao="Não deveria ser possível chegar aqui.",
            versao=peca["recurso"].versao,
            decidido_por=JULGADORA,
            decidido_em=now(),
        )


def test_o_estado_lido_obsoleto_recusa(peca):
    """Duas pessoas na mesma peça: a segunda não grava por cima do que a primeira decidiu."""
    lido = assinatura_do_estado_da_peca(peca["recurso"])
    apreciar(peca)

    with pytest.raises(DomainError) as recusa:
        apreciar(
            peca,
            admitido=False,
            motivo="Sem saber que já havia juízo.",
            assinatura_do_estado=lido,
            idempotency_key="obsoleto-us3b",
        )

    assert recusa.value.code == "stale_appeal_state"
    assert recusa.value.status == 409


def test_recurso_inexistente_responde_404(peca):
    with pytest.raises(DomainError) as recusa:
        apreciar(peca, recurso_id=uuid.uuid4())

    assert recusa.value.status == 404


# ---------------------------------------------------------------------------
# T055 — a tempestividade
# ---------------------------------------------------------------------------


def test_sem_janela_estruturada_a_tempestividade_e_juizo_humano(peca):
    """A tela **não inventa prazo**, e diz isso em vez de fingir um (D-004, FR-034, FR-035).

    Sem declaração no Edital não há prazo computável, e é no motivo do juízo que a tempestividade
    se decide. Escrever "dentro do prazo" onde não há prazo seria afirmar o que ninguém apurou.
    """
    linha = _linha(peca)

    assert peca["recurso"].janela_abriu_em is None
    assert peca["recurso"].janela_fecha_em is None
    assert linha["tempestividade"] == SEM_JANELA
    assert linha["tempestividade_rotulo"] == "Sem prazo computável"


def test_com_janela_a_tempestividade_deriva_da_que_a_peca_gravou(peca):
    """E é derivada do que a **peça gravou**, não recalculada com a norma de hoje (FR-024, FR-033).

    Havendo janela, a interposição fora do prazo já foi recusada lá atrás: aqui a tempestividade é
    informação, e não matéria de admissibilidade.
    """
    recurso = peca["recurso"]
    _forcar_janela(
        recurso,
        recurso.interposto_em - timedelta(days=1),
        recurso.interposto_em + timedelta(days=1),
    )
    assert _linha(peca)["tempestividade"] == DENTRO

    _forcar_janela(
        recurso,
        recurso.interposto_em - timedelta(days=3),
        recurso.interposto_em - timedelta(days=1),
    )
    assert _linha(peca)["tempestividade"] == FORA


def _linha(peca):
    linhas = recursos_do_edital(peca["cenario"]["edital"])
    return next(linha for linha in linhas if linha["recurso"].pk == peca["recurso"].pk)


def _forcar_janela(recurso, abriu, fecha):
    """Grava a janela **por SQL cru**, porque o agregado é append-only.

    Não é contorno da garantia: é o único jeito de exercitar hoje a **leitura** de uma janela que o
    degrau 8 ainda não sabe gravar. Quando ele existir, o teste da US6 percorre o caminho real e
    este continua respondendo pela derivação.
    """
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE recursos_recurso DISABLE TRIGGER recurso_append_only")
        cursor.execute(
            "UPDATE recursos_recurso SET janela_abriu_em = %s, janela_fecha_em = %s WHERE id = %s",
            [abriu, fecha, recurso.id],
        )
        cursor.execute("ALTER TABLE recursos_recurso ENABLE TRIGGER recurso_append_only")
    recurso.refresh_from_db()
