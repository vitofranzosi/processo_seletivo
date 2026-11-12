"""A vaga não preenchida nasce e não muda mais — e a garantia não depende da aplicação (155).

**Três camadas, como as da vaga acrescida.** O `save()` do modelo recusa a alteração vinda do ORM;
o gatilho recusa a que vem por `QuerySet.update()`; e o privilégio ausente recusa a que viesse de
qualquer código escrito depois. O ataque com a role de runtime mora em
`tests/integration/test_database_permissions.py`, que percorre `TABELAS_APPEND_ONLY` inteira;
aqui se prende que a tabela está lá.

**Por que esta tabela em particular.** Ela é a única linha que explica por que um recorte com vaga
efetiva não tem nada "a ocupar" (R-002). Reescrevê-la poria a vaga de volta na conta, ou a
tiraria, sem fundamento nem autor — e o desfazimento existe para que o erro se corrija com rastro.
"""

import uuid

import pytest
from django.db import connection, transaction
from django.db.utils import DatabaseError, IntegrityError
from django.utils import timezone

from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao, VagaNaoPreenchida
from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY, comandos_de_privilegios
from tests.unit.ocupacao.test_movimento_com_recorte import edital_com_versao

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="gatilho e nome de constraint só no PostgreSQL"
)

PERFIL = uuid.uuid4()
MARCO = uuid.uuid4()


@pytest.fixture
def edital_e_versao(db):
    return edital_com_versao("nao-preenchida")


def gravar(edital_, versao_, **campos):
    padrao = {
        "edital": edital_,
        "perfil_id": PERFIL,
        "marco_id": MARCO,
        # A linha geral: a declaração vale também para a ampla sem quem a ocupe (D-014).
        "lista_id": None,
        "apuracao": None,
        "especie": nomes.NAO_PREENCHIDA_DECLARACAO,
        "desfaz": None,
        "quantidade": 1,
        "fundamento": "Edital silente; a comissão declara a vaga não preenchida.",
        "versao": versao_,
        "registrado_por": "teste",
        "registrado_em": timezone.now(),
    }
    padrao.update(campos)
    return VagaNaoPreenchida.objects.create(**padrao)


class TestAPrimeiraCamadaEOModelo:
    def test_recusa_alteracao_pelo_orm(self):
        declaracao = VagaNaoPreenchida(id=uuid.uuid4())
        declaracao._state.adding = False

        with pytest.raises(TypeError, match="append-only"):
            declaracao.save()

    def test_recusa_exclusao_pelo_orm(self):
        with pytest.raises(TypeError, match="append-only"):
            VagaNaoPreenchida(id=uuid.uuid4()).delete()

    def test_o_desfazimento_cita_a_declaracao_pela_mesma_tabela(self):
        """Um `UUIDField` aqui deixaria citar declaração que não existe."""
        campo = VagaNaoPreenchida._meta.get_field("desfaz")
        assert campo.related_model is VagaNaoPreenchida
        assert campo.null

    def test_o_recorte_e_identidade_publicada_e_a_apuracao_pode_faltar(self):
        for nome in ("perfil_id", "marco_id", "lista_id"):
            assert VagaNaoPreenchida._meta.get_field(nome).get_internal_type() == "UUIDField"
        assert VagaNaoPreenchida._meta.get_field("apuracao").null

    def test_faltando_desconta_as_nao_preenchidas_e_nao_as_efetivas(self):
        """A vaga existe e ninguém a preencheu (FR-6326): sai do "a ocupar", e as efetivas ficam."""
        apuracao = ApuracaoDeOcupacao(efetivas=3, ocupadas=1, nao_preenchidas=1)

        assert apuracao.faltando == 1
        assert apuracao.efetivas == 3
        assert ApuracaoDeOcupacao(efetivas=3, ocupadas=1).faltando == 2


class TestATerceiraCamadaEOPrivilegioAusente:
    def test_a_tabela_esta_declarada_como_append_only(self):
        assert "ocupacao_vaganaopreenchida" in TABELAS_APPEND_ONLY

    def test_a_politica_revoga_update_e_delete_sobre_ela(self):
        comandos = " ".join(comandos_de_privilegios(migration_role="m", runtime_role="r"))
        assert "REVOKE UPDATE, DELETE" in comandos
        assert "ocupacao_vaganaopreenchida" in comandos


@pytest.mark.django_db
class TestAInsercaoValida:
    def test_a_declaracao_e_o_desfazimento_gravam(self, edital_e_versao):
        edital, versao = edital_e_versao
        declaracao = gravar(edital, versao, quantidade=2)

        desfazimento = gravar(
            edital,
            versao,
            especie=nomes.NAO_PREENCHIDA_DESFAZIMENTO,
            desfaz=declaracao,
            quantidade=1,
            fundamento="Uma das vagas tem quem a ocupe, afinal.",
        )

        assert list(declaracao.desfazimentos.all()) == [desfazimento]


@pytest.mark.django_db
@postgresql_only
class TestAsGarantiasDoBanco:
    def test_o_gatilho_recusa_alteracao_e_exclusao_por_queryset(self, edital_e_versao):
        edital, versao = edital_e_versao
        declaracao = gravar(edital, versao)

        with pytest.raises(DatabaseError, match="immutable"), transaction.atomic():
            VagaNaoPreenchida.objects.filter(id=declaracao.id).update(quantidade=2)
        with pytest.raises(DatabaseError, match="immutable"), transaction.atomic():
            VagaNaoPreenchida.objects.filter(id=declaracao.id).delete()

    @pytest.mark.parametrize(
        ("campos", "constraint"),
        [
            ({"quantidade": 0}, "ck_nao_preenchida_quantidade_positiva"),
            ({"especie": "OUTRA"}, "ck_nao_preenchida_especie"),
            ({"fundamento": ""}, "ck_nao_preenchida_com_fundamento"),
        ],
    )
    def test_as_constraints_recusam_a_declaracao_malformada(
        self, edital_e_versao, campos, constraint
    ):
        edital, versao = edital_e_versao

        with pytest.raises(IntegrityError, match=constraint), transaction.atomic():
            gravar(edital, versao, **campos)

    def test_o_desfazimento_sem_citacao_e_recusado(self, edital_e_versao):
        edital, versao = edital_e_versao

        with (
            pytest.raises(IntegrityError, match="ck_nao_preenchida_desfazimento_cita"),
            transaction.atomic(),
        ):
            gravar(edital, versao, especie=nomes.NAO_PREENCHIDA_DESFAZIMENTO)

    def test_a_declaracao_que_cita_outra_e_recusada(self, edital_e_versao):
        edital, versao = edital_e_versao
        anterior = gravar(edital, versao)

        with (
            pytest.raises(IntegrityError, match="ck_nao_preenchida_desfazimento_cita"),
            transaction.atomic(),
        ):
            gravar(edital, versao, desfaz=anterior)
