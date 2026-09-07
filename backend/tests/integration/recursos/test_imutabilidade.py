"""As três camadas que tornam a peça, o juízo e a decisão imutáveis — e a coerência que os liga.

Três camadas porque cada uma cobre um caminho: o `save`/`delete` do modelo cobre o ORM, a trigger
cobre quem chega por fora dele, e o privilégio negado cobre quem chega com o cliente do banco na
mão. Num registro append-only isso importa mais que em qualquer outro: o inválido entra uma vez e
fica, porque nada o corrige depois.

A tabela da citação (`classificacao_citacaodedecisao`) entra na US7, e as suas duas triggers são
cobertas lá — ela não pertence à fundação, e pô-la aqui inflaria a fatia que a spec declara
indivisível.
"""

from decimal import Decimal

import pytest
from django.db import IntegrityError, connection, transaction
from django.utils import timezone

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.recursos.models import DecisaoRecurso, JuizoDeAdmissibilidade, Recurso
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.recursos import admitir, decidir, interpor
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

SOMENTE_POSTGRES = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="As triggers e os privilégios são de PostgreSQL.",
)


@pytest.fixture
def peca(gestor, api_client, manager_headers):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1810, codigo="1810"
    )
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-1810")
    concluir_como(cenario, "joao", inscricao, pontuacao="55")
    consolidar(
        actor=gestor,
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[inscricao.id],
        idempotency_key="consolidar-1810",
        correlation_id="teste-1810",
    )
    resultado = ResultadoEtapa.objects.get(inscricao=inscricao)
    versao = VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("valid_from")
    recurso = interpor(
        inscricao=inscricao, versao=versao, resultado=resultado, protocolo="REC-2026-IMUT0001"
    )
    return cenario, resultado, versao, recurso


# ── Camada 1: o modelo ────────────────────────────────────────────────────────────────────────


def test_o_modelo_recusa_alterar_a_peca(peca):
    _cenario, _resultado, _versao, recurso = peca
    recurso.fundamentacao = "outra coisa"
    with pytest.raises(TypeError):
        recurso.save()


def test_o_modelo_recusa_excluir_a_peca(peca):
    _cenario, _resultado, _versao, recurso = peca
    with pytest.raises(TypeError):
        recurso.delete()


def test_o_modelo_recusa_alterar_o_juizo_e_a_decisao(peca):
    _cenario, resultado, versao, recurso = peca
    juizo = admitir(recurso)
    decisao = decidir(recurso, protegido=resultado, consequencia="HABILITADA", versao=versao)

    juizo.admitido = False
    with pytest.raises(TypeError):
        juizo.save()
    decisao.motivacao = "outra"
    with pytest.raises(TypeError):
        decisao.save()


# ── Camada 2: as triggers ─────────────────────────────────────────────────────────────────────


@SOMENTE_POSTGRES
@pytest.mark.parametrize(
    ("tabela", "coluna", "valor"),
    [
        ("recursos_recurso", "fundamentacao", "'outra'"),
        ("recursos_juizodeadmissibilidade", "motivo", "'outro'"),
        ("recursos_decisaorecurso", "motivacao", "'outra'"),
    ],
)
def test_a_trigger_recusa_update_por_fora_do_orm(peca, tabela, coluna, valor):
    _cenario, resultado, versao, recurso = peca
    admitir(recurso)
    decidir(recurso, protegido=resultado, consequencia="HABILITADA", versao=versao)

    with (
        pytest.raises(Exception, match="append-only"),
        transaction.atomic(),
        connection.cursor() as cursor,
    ):
        cursor.execute(f"UPDATE {tabela} SET {coluna} = {valor}")


@SOMENTE_POSTGRES
@pytest.mark.parametrize(
    "tabela",
    ["recursos_decisaorecurso", "recursos_juizodeadmissibilidade", "recursos_recurso"],
)
def test_a_trigger_recusa_delete_por_fora_do_orm(peca, tabela):
    _cenario, resultado, versao, recurso = peca
    admitir(recurso)
    decidir(recurso, protegido=resultado, consequencia="HABILITADA", versao=versao)

    with (
        pytest.raises(Exception, match="append-only"),
        transaction.atomic(),
        connection.cursor() as cursor,
    ):
        cursor.execute(f"DELETE FROM {tabela}")


# ── A coerência que só a trigger consegue conferir ────────────────────────────────────────────


@SOMENTE_POSTGRES
def test_a_peca_nao_ataca_resultado_de_outra_inscricao(peca, gestor):
    """`ck_recurso_objeto_unico` só olha as duas nulidades; a pertinência é da trigger."""
    cenario, resultado, versao, _recurso = peca
    outra = inscrever(cenario["edital"], 1, primeiro=60)[0]

    with pytest.raises(Exception, match="another registration"), transaction.atomic():
        interpor(inscricao=outra, versao=versao, resultado=resultado, protocolo="REC-2026-IMUT0002")


@SOMENTE_POSTGRES
def test_a_decisao_exige_juizo_de_admissibilidade_positivo(peca):
    """Julgar o mérito do que não foi admitido inverte a ordem dos atos (FR-036)."""
    _cenario, resultado, versao, recurso = peca

    with pytest.raises(Exception, match="was not admitted"), transaction.atomic():
        decidir(recurso, protegido=resultado, consequencia="HABILITADA", versao=versao)


@SOMENTE_POSTGRES
def test_a_decisao_nao_e_julgada_depois_de_inadmitida(peca):
    _cenario, resultado, versao, recurso = peca
    admitir(recurso, admitido=False, motivo="Intempestivo.")

    with pytest.raises(Exception, match="was not admitted"), transaction.atomic():
        decidir(recurso, protegido=resultado, consequencia="HABILITADA", versao=versao)


@SOMENTE_POSTGRES
def test_um_juizo_e_uma_decisao_por_recurso(peca):
    """As duas unicidades são o que resolve "dois julgadores decidindo ao mesmo tempo"."""
    _cenario, resultado, versao, recurso = peca
    admitir(recurso)
    decidir(recurso, protegido=resultado, consequencia="HABILITADA", versao=versao)

    with pytest.raises(IntegrityError), transaction.atomic():
        admitir(recurso, motivo="de novo")
    with pytest.raises(IntegrityError), transaction.atomic():
        decidir(recurso, protegido=resultado, consequencia="ELIMINADA", versao=versao)


@SOMENTE_POSTGRES
def test_um_recurso_por_titular_e_objeto_atacado(peca):
    """A FR-011 no banco: a segunda peça equivalente não nasce, pendente ou já decidida."""
    _cenario, resultado, versao, _recurso = peca

    with pytest.raises(IntegrityError), transaction.atomic():
        interpor(
            inscricao=resultado.inscricao,
            versao=versao,
            resultado=resultado,
            protocolo="REC-2026-IMUT0003",
        )


@SOMENTE_POSTGRES
def test_a_decisao_nao_cita_versao_de_outro_edital(peca, gestor, api_client, manager_headers):
    """A norma sob a qual se decidiu é a do Edital do recurso, e o banco o exige.

    O Resultado sucessor **copia** essa versão: uma versão alheia atravessaria para um registro
    append-only, que nada corrige depois.
    """
    _cenario, resultado, _versao, recurso = peca
    admitir(recurso)
    outro = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1811, codigo="1811"
    )
    alheia = VersaoConsolidada.objects.filter(edital=outro["edital"]).latest("valid_from")

    with pytest.raises(Exception, match="version of another edital"), transaction.atomic():
        decidir(recurso, protegido=resultado, consequencia="HABILITADA", versao=alheia)


@SOMENTE_POSTGRES
@pytest.mark.parametrize(
    ("campos", "constraint"),
    [
        ({"consequencia": "APROVADA"}, "ck_decisao_consequencia"),
        ({"consequencia": "HABILITADA", "forma": "PONTUADA"}, "ck_decisao_conclusao_por_forma"),
        (
            {"consequencia": "HABILITADA", "forma": "DECISORIA", "pontuacao": Decimal("70")},
            "ck_decisao_conclusao_por_forma",
        ),
        (
            {"especie": "INDEFERIDO", "forma": "PONTUADA", "pontuacao": Decimal("70")},
            "ck_decisao_sem_grandeza_residual",
        ),
    ],
)
def test_o_banco_recusa_conclusoes_invalidas_na_decisao(peca, campos, constraint):
    """`choices` valida no formulário; num registro append-only isso não basta.

    `bulk_create`, SQL direto e código futuro gravariam qualquer texto — e o valor inventado entra
    uma vez e fica, porque nada o corrige depois. É a mesma razão de `ck_resultado_consequencia`
    na 013, aplicada aos três campos que carregam o que a decisão afirma.
    """
    _cenario, resultado, versao, recurso = peca
    admitir(recurso)
    base = {
        "recurso": recurso,
        "especie": DecisaoRecurso.Especie.CORRECAO_FIXADA,
        "motivacao": "motivada",
        "versao": versao,
        "decidido_por": "julgadora",
        "decidido_em": timezone.now(),
        "resultado_protegido": resultado,
        "etapa_id": resultado.etapa_id,
        "consequencia": "",
        "forma": "",
        "pontuacao": None,
        "sentido": "",
    }
    base.update(campos)
    if base["especie"] != DecisaoRecurso.Especie.CORRECAO_FIXADA:
        base["resultado_protegido"] = None
        base["etapa_id"] = None

    with pytest.raises(IntegrityError, match=constraint), transaction.atomic():
        DecisaoRecurso.objects.create(**base)


# ── Camada 3: o privilégio ────────────────────────────────────────────────────────────────────


@SOMENTE_POSTGRES
def test_as_tres_tabelas_estao_na_politica_de_privilegios():
    """O papel de runtime não tem `UPDATE` nem `DELETE` sobre elas.

    A trigger recusa mesmo quem tem privilégio; esta camada existe para que a conversa nem chegue
    lá — e para que a política de papéis não esqueça uma tabela nova, que é o modo de falha que a
    017 registrou (T-013).
    """
    from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY

    assert {
        "recursos_recurso",
        "recursos_juizodeadmissibilidade",
        "recursos_decisaorecurso",
    } <= set(TABELAS_APPEND_ONLY)


def test_os_tres_agregados_nao_tem_coluna_de_situacao():
    """D-010 em teste: a situação deriva dos atos que existem, e não de estado persistido.

    Uma coluna de situação seria estado a manter coerente onde a existência de linha já responde —
    e o primeiro lugar onde ela apareceria é aqui, por conveniência de uma tela de listagem.
    """
    suspeitos = {"situacao", "status", "estado", "vigente", "pendente", "cumprida"}

    for modelo in (Recurso, JuizoDeAdmissibilidade, DecisaoRecurso):
        campos = {campo.name for campo in modelo._meta.get_fields()}
        assert not (campos & suspeitos), f"{modelo.__name__} ganhou coluna de situação: {campos}"
