"""O registro de unidades e de autoridades, e o que o banco recusa (060, R-006).

As restrições de `CHECK` valem nos dois bancos. Os gatilhos só existem no PostgreSQL, e os testes
deles são pulados fora dele: fingir o gatilho no SQLite afirmaria uma garantia que não existe ali.
"""

from datetime import UTC, date, datetime, timedelta

import pytest
from django.db import DatabaseError, IntegrityError, connection, transaction
from django.utils import timezone

from processo_seletivo.unidades.models import AutoridadeHabilitada, Unidade
from tests.fixtures.autoridades import registrar_autoridade, registrar_unidade

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

so_postgresql = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="gatilho validado somente no PostgreSQL"
)


def _cefor():
    return Unidade.objects.get(codigo="cefor")


# ---------------------------------------------------------------------------
# O que o registro guarda
# ---------------------------------------------------------------------------


def test_a_autoridade_guarda_cargo_nome_ato_e_vigencia_e_nada_alem():
    """FR-1116: sem CPF, matrícula, contato ou foto — o teto da `007`, FR-044, continua."""
    campos = {campo.name for campo in AutoridadeHabilitada._meta.get_fields()}
    assert campos == {
        "id",
        "unidade",
        "cargo",
        "nome",
        "ato_de_nomeacao",
        "inicio_vigencia",
        "fim_vigencia",
        "cadastrada_por",
        "cadastrada_em",
        "encerrada_por",
        "encerrada_em",
        "usada_em",
    }


def test_a_mesma_pessoa_pode_estar_habilitada_em_duas_unidades():
    """FR-1118: habilitação na unidade, e não lotação; o Reitor responde por várias (D-003)."""
    serra = registrar_unidade("serra")
    registrar_autoridade(_cefor(), cargo="Reitor", nome="João Exemplo")
    registrar_autoridade(serra, cargo="Reitor", nome="João Exemplo")

    assert AutoridadeHabilitada.objects.filter(nome="João Exemplo").count() == 2


def test_o_codigo_da_unidade_e_unico():
    with pytest.raises(IntegrityError), transaction.atomic():
        Unidade.objects.create(
            codigo="cefor",
            sigla="Outra",
            nome="Outra",
            cabecalho=["Outra"],
            local="Vitória (ES)",
            registrada_em=timezone.now(),
        )


def test_o_fim_nao_pode_ser_anterior_ao_inicio():
    """FR-1120, no banco: o `CHECK` recusa mesmo quem não passa pelo comando."""
    with pytest.raises(IntegrityError), transaction.atomic():
        registrar_autoridade(_cefor(), inicio=date(2026, 10, 6), fim=date(2026, 10, 5))


def test_o_encerramento_e_completo_ou_nao_existe():
    """Quem e quando andam juntos, e só com um fim declarado."""
    autoridade = registrar_autoridade(_cefor())
    with pytest.raises(IntegrityError), transaction.atomic():
        AutoridadeHabilitada.objects.filter(pk=autoridade.pk).update(encerrada_em=timezone.now())


def test_o_cargo_e_obrigatorio():
    with pytest.raises(IntegrityError), transaction.atomic():
        registrar_autoridade(_cefor(), cargo="")


# ---------------------------------------------------------------------------
# Os gatilhos (R-006)
# ---------------------------------------------------------------------------


@so_postgresql
def test_nenhuma_unidade_se_exclui():
    """FR-1109."""
    with pytest.raises(DatabaseError), transaction.atomic():
        Unidade.objects.filter(codigo="cefor").delete()


@so_postgresql
def test_nenhuma_autoridade_se_exclui():
    """FR-1120: encerrar é a única forma de retirar de uso."""
    autoridade = registrar_autoridade(_cefor())
    with pytest.raises(DatabaseError), transaction.atomic():
        AutoridadeHabilitada.objects.filter(pk=autoridade.pk).delete()


@so_postgresql
def test_o_codigo_da_unidade_nao_muda():
    """FR-1108: o código é o escopo institucional."""
    with pytest.raises(DatabaseError), transaction.atomic():
        Unidade.objects.filter(codigo="cefor").update(codigo="outro")


@so_postgresql
def test_o_resto_da_unidade_muda():
    """Nome, sigla, cabeçalho, local e situação mudam — e é a sincronização que os muda."""
    Unidade.objects.filter(codigo="cefor").update(nome="Outro nome", ativa=False)
    assert Unidade.objects.get(codigo="cefor").nome == "Outro nome"


@so_postgresql
def test_a_unidade_da_autoridade_nao_muda_nem_antes_do_uso():
    """FR-1121: a tela não expõe o campo, e o banco não deixa um `update()` distraído mudá-lo."""
    autoridade = registrar_autoridade(_cefor())
    serra = registrar_unidade("serra")
    with pytest.raises(DatabaseError), transaction.atomic():
        AutoridadeHabilitada.objects.filter(pk=autoridade.pk).update(unidade=serra)


@so_postgresql
@pytest.mark.parametrize(
    "campo, valor",
    [
        ("nome", "Outra"),
        ("cargo", "Outro"),
        ("ato_de_nomeacao", "Portaria nº 9"),
        ("inicio_vigencia", date(2020, 1, 1)),
        ("usada_em", None),
    ],
)
def test_a_autoridade_usada_nao_se_reescreve(campo, valor):
    """FR-1121, D-004: depois do primeiro ato, o identificador liga uma Publicação ao registro."""
    autoridade = registrar_autoridade(_cefor(), usada_em=timezone.now())
    with pytest.raises(DatabaseError), transaction.atomic():
        AutoridadeHabilitada.objects.filter(pk=autoridade.pk).update(**{campo: valor})


@so_postgresql
def test_a_autoridade_ainda_nao_usada_se_corrige():
    autoridade = registrar_autoridade(_cefor())
    AutoridadeHabilitada.objects.filter(pk=autoridade.pk).update(nome="Corrigida")
    assert AutoridadeHabilitada.objects.get(pk=autoridade.pk).nome == "Corrigida"


@so_postgresql
def test_a_autoridade_usada_se_encerra():
    """Encerrar é `UPDATE` do fim, e continua possível depois do uso."""
    hoje = timezone.now().date()
    autoridade = registrar_autoridade(_cefor(), usada_em=timezone.now())
    AutoridadeHabilitada.objects.filter(pk=autoridade.pk).update(
        fim_vigencia=hoje + timedelta(days=1), encerrada_em=timezone.now(), encerrada_por="t"
    )
    assert AutoridadeHabilitada.objects.get(pk=autoridade.pk).fim_vigencia is not None


@so_postgresql
def test_o_banco_recusa_fim_antes_do_dia_do_primeiro_ato_mesmo_gravado_direto():
    """FR-1120 (N1): o registro não pode dizer que a autoridade não respondia quando assinou.

    O primeiro uso fica perto da meia-noite em UTC, que no fuso institucional ainda é o dia
    anterior: o gatilho conta o dia no fuso de São Paulo, e não no do servidor.
    """
    # 02:30 UTC de 07/10 é 23:30 de 06/10 em São Paulo.
    usada = datetime(2026, 10, 7, 2, 30, tzinfo=UTC)
    autoridade = registrar_autoridade(_cefor(), inicio=date(2026, 1, 1), usada_em=usada)
    with pytest.raises(DatabaseError), transaction.atomic():
        AutoridadeHabilitada.objects.filter(pk=autoridade.pk).update(
            fim_vigencia=date(2026, 10, 5), encerrada_em=timezone.now(), encerrada_por="t"
        )
    # O dia do primeiro ato, no fuso institucional, é aceito — o fim é inclusivo.
    AutoridadeHabilitada.objects.filter(pk=autoridade.pk).update(
        fim_vigencia=date(2026, 10, 6), encerrada_em=timezone.now(), encerrada_por="t"
    )
