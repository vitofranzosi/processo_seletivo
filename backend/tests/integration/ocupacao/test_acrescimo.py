"""A vaga acrescida depois da publicação: o banco, a leitura da apuração e os dois atos (097).

**O que estes testes protegem não é a soma** — ela é de unidade, em `tests/unit/ocupacao` — e sim o
que torna o número contestável: que a apuração diz quais acréscimos leu, que a antiga relida devolve
o dela, que acréscimo novo a torna obsoleta, e que os atos recusam o que não podem fazer sem gravar
nada.
"""

import uuid

import pytest
from django.db import connection
from django.db.utils import DatabaseError, IntegrityError
from django.utils import timezone

from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import AcrescimoDeVagas, ApuracaoDeOcupacao
from processo_seletivo.publicacoes.application.selectors import effective_version
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.integration.ocupacao.test_emissao import apurar

pytestmark = pytest.mark.django_db(transaction=True)

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="gatilho e nome de constraint só no PostgreSQL"
)


def gravar(edital, quantidade=1, *, lista_id=None, especie=nomes.ACRESCIMO, desfaz=None, **campos):
    """Um acréscimo gravado à mão, sem o ato: é o que a leitura da apuração tem de enxergar."""
    padrao = {
        "origem": "" if especie == nomes.DESFAZIMENTO else "Edital Multicampi nº 20/2026",
        "fundamento": "Vaga não preenchida no Edital regular",
    }
    padrao.update(campos)
    return AcrescimoDeVagas.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        especie=especie,
        quantidade=quantidade,
        desfaz=desfaz,
        versao=effective_version(edital_id=edital.id),
        registrado_por="teste",
        registrado_em=timezone.now(),
        **padrao,
    )


def causas(apuracao):
    return {c["causa"] for c in selectors.causas_de_obsolescencia(apuracao)}


@postgresql_only
class TestAsGarantiasDoBanco:
    """Só no PostgreSQL: a mensagem do SQLite não nomeia a constraint, e o gatilho não existe lá."""

    def test_o_gatilho_recusa_alteracao_e_exclusao_por_queryset(self, cenario):
        edital, _, _ = cenario
        acrescimo = gravar(edital)

        with pytest.raises(DatabaseError, match="immutable"):
            AcrescimoDeVagas.objects.filter(id=acrescimo.id).update(quantidade=2)
        with pytest.raises(DatabaseError, match="immutable"):
            AcrescimoDeVagas.objects.filter(id=acrescimo.id).delete()

    @pytest.mark.parametrize(
        ("campos", "constraint"),
        [
            ({"quantidade": 0}, "ck_acrescimo_quantidade_positiva"),
            ({"especie": "OUTRA"}, "ck_acrescimo_especie"),
            ({"origem": ""}, "ck_acrescimo_com_origem"),
            ({"fundamento": ""}, "ck_acrescimo_com_fundamento"),
        ],
    )
    def test_as_constraints_recusam_o_acrescimo_malformado(self, cenario, campos, constraint):
        edital, _, _ = cenario

        with pytest.raises(IntegrityError, match=constraint):
            gravar(edital, **campos)

    def test_o_desfazimento_sem_citacao_e_recusado(self, cenario):
        edital, _, _ = cenario

        with pytest.raises(IntegrityError, match="ck_desfazimento_cita_o_acrescimo"):
            gravar(edital, especie=nomes.DESFAZIMENTO)


class TestAApuracaoLeOAcrescimo:
    def test_acrescimo_posterior_torna_a_apuracao_obsoleta(self, cenario, gestor):
        """A sexta causa (`FR-2453`): o número que ela diz já não é o do recorte."""
        edital, _, _ = cenario
        apurar(edital, gestor)
        vigente = selectors.apuracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
        assert causas(vigente) == set()

        gravar(edital, 2)

        assert causas(vigente) == {nomes.CAUSA_ACRESCIMO_POSTERIOR}

    def test_a_emissao_seguinte_le_congela_e_soma(self, cenario, gestor):
        """`FR-2452`: as efetivas sobem, e os ids lidos ficam no universo."""
        edital, _, _ = cenario
        apurar(edital, gestor)
        acrescimo = gravar(edital, 2)

        declarado = apurar(edital, gestor, chave="097-seguinte", motivo="Vaga acrescida")

        assert declarado["publicadas"] == 3
        assert declarado["efetivas"] == 5
        assert declarado["universo"]["acrescimosLidos"] == [str(acrescimo.id)]
        nova = ApuracaoDeOcupacao.objects.get(id=declarado["id"])
        assert causas(nova) == set()

    def test_o_desfazimento_e_descontado(self, cenario, gestor):
        edital, _, _ = cenario
        acrescimo = gravar(edital, 2)
        gravar(edital, 1, especie=nomes.DESFAZIMENTO, desfaz=acrescimo, fundamento="Engano")

        declarado = apurar(edital, gestor)

        assert declarado["efetivas"] == 4
        assert len(declarado["universo"]["acrescimosLidos"]) == 2

    def test_a_apuracao_antiga_relida_continua_com_o_numero_dela(self, cenario, gestor):
        """`SC-922`: a reprodução é pelo congelado, e não pelos acréscimos de hoje."""
        edital, _, _ = cenario
        gravar(edital, 1)
        antiga = apurar(edital, gestor)
        gravar(edital, 4)
        apurar(edital, gestor, chave="097-depois", motivo="Mais vagas")

        relida = ApuracaoDeOcupacao.objects.get(id=antiga["id"])

        assert relida.efetivas == 4
        assert relida.universo["acrescimosLidos"] == antiga["universo"]["acrescimosLidos"]
        lidos = selectors.acrescimos_lidos_por(relida)
        assert [quantidade for _, quantidade in lidos] == [1]

    def test_acrescimo_de_outro_recorte_nao_alcanca_este(self, cenario, gestor):
        """**O recorte exato** (`T-002`): a vaga vale onde foi registrada, e não em toda a ampla."""
        edital, _, _ = cenario
        apurar(edital, gestor)
        vigente = selectors.apuracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)

        gravar(edital, 1, lista_id=uuid.uuid4())

        assert causas(vigente) == set()

    def test_apuracao_sem_a_lista_congelada_so_e_obsoleta_com_acrescimo(self, cenario, gestor):
        """As apurações anteriores à `097` não têm `acrescimosLidos`, e não mudam de estado sem
        motivo: só a vaga acrescida no recorte as torna obsoletas."""
        edital, _, _ = cenario
        apurar(edital, gestor)
        vigente = selectors.apuracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
        universo = dict(vigente.universo)
        universo.pop("acrescimosLidos", None)
        # Em memória: a apuração é append-only, e o que se simula é a linha gravada antes da `097`.
        vigente.universo = universo

        assert causas(vigente) == set()
        gravar(edital, 1)
        assert causas(vigente) == {nomes.CAUSA_ACRESCIMO_POSTERIOR}
