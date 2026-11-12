"""O movimento de vaga com o recorte próprio: as colunas e as constraints da `155` (R-001).

**O que se prende é forma de banco, e não norma.** A destinação passa a ser ato próprio, e o
movimento que ela grava carrega o recorte, o gatilho, o fundamento e a versão do Edital lida; a
apuração pode faltar, na lista de sorteio sem relação (R-007). As linhas anteriores à `155` não têm
nada disso, e continuam válidas — as integrações de `tests/integration/ocupacao/test_reversao.py`
as gravam pelo caminho antigo e são a prova de que as constraints novas não as recusam.

**Uma transação só por caso, com *savepoint* em volta de cada recusa.** O erro de constraint ou de
gatilho invalida a transação corrente; dentro de `transaction.atomic()` ele desfaz só o
*savepoint*, e o caso continua podendo consultar. Um caso transacional custaria a limpeza inteira da
suíte a cada um, para provar o que um *savepoint* prova igual.
"""

import uuid

import pytest
from django.db import connection, transaction
from django.db.utils import DatabaseError, IntegrityError
from django.utils import timezone

from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import MovimentoDeVaga
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.publicacoes.models import Publicacao, VersaoConsolidada

pytestmark = pytest.mark.django_db

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="gatilho e nome de constraint só no PostgreSQL"
)

PERFIL = uuid.uuid4()
MARCO = uuid.uuid4()
PPI = uuid.uuid4()


def edital_com_versao(sufixo):
    """Um Edital e uma versão consolidada mínimos: o conteúdo é irrelevante aqui.

    Montados à mão, e não pelo percurso da publicação, porque o que se exercita é a tabela: o
    percurso inteiro custaria segundos por caso para chegar às mesmas duas linhas.
    """
    agora = timezone.now()
    processo = ProcessoSeletivo.objects.create(
        institution_scope="cefor",
        institutional_code=f"PS-155-{sufixo}",
        title="Processo da destinação",
        created_at=agora,
        created_by="teste",
        last_changed_at=agora,
    )
    edital = Edital.objects.create(
        processo=processo,
        institution_scope="cefor",
        number=f"155-{sufixo}",
        year=2026,
        title="Edital da destinação",
        created_at=agora,
        created_by="teste",
        last_edited_by="teste",
    )
    publicacao = Publicacao.objects.create(
        edital=edital,
        publication_order=1,
        published_at=agora,
        effective_at=agora,
        content_hash="0" * 64,
        canonical_content=b"{}",
        published_by="teste",
        signatory_id=uuid.uuid4(),
        signatory_name="Autoridade de teste",
        signatory_role="Diretora-Geral",
    )
    versao = VersaoConsolidada.objects.create(
        edital=edital,
        valid_from=agora,
        materialized_at=agora,
        source_publication=publicacao,
        content={},
        canonical_content=b"{}",
        content_hash="0" * 64,
    )
    return edital, versao


@pytest.fixture
def edital_e_versao():
    return edital_com_versao("movimento")


def gravar(edital_, versao_, **campos):
    """Um movimento novo, com o recorte próprio e sem apuração: a forma da `155`."""
    padrao = {
        "apuracao": None,
        "edital": edital_,
        "perfil_id": PERFIL,
        "marco_id": MARCO,
        "especie": nomes.MOVIMENTO_REVERSAO,
        "origem_lista_id": PPI,
        "destino_lista_id": None,
        "quantidade": 2,
        "causa": "Lista reservada sem concorrente",
        "gatilho": nomes.REVERSAO_POR_ESGOTAMENTO,
        "fundamento": "Item 4.3 do Edital: a vaga reservada sem candidato vai à ampla.",
        "versao": versao_,
        "desfaz": None,
        "registrado_por": "teste",
        "registrado_em": timezone.now(),
    }
    padrao.update(campos)
    return MovimentoDeVaga.objects.create(**padrao)


class TestAInsercaoValida:
    def test_sem_apuracao_e_com_o_recorte_proprio_grava(self, edital_e_versao):
        """A lista de sorteio sem relação não tem apuração de origem (R-007): o recorte basta."""
        edital, versao = edital_e_versao

        movimento = gravar(edital, versao)

        relido = MovimentoDeVaga.objects.get(id=movimento.id)
        assert relido.apuracao_id is None
        assert relido.edital_id == edital.id
        assert relido.gatilho == nomes.REVERSAO_POR_ESGOTAMENTO
        assert relido.versao_id == versao.id

    def test_o_desfazimento_cita_o_movimento_e_inverte_o_sentido(self, edital_e_versao):
        """O ato contrário é outro movimento (R-005): a quantidade igual, o sentido invertido."""
        edital, versao = edital_e_versao
        destinacao = gravar(edital, versao)

        desfeito = gravar(
            edital,
            versao,
            especie=nomes.MOVIMENTO_DESFAZIMENTO,
            origem_lista_id=None,
            destino_lista_id=PPI,
            gatilho="",
            fundamento="Destinação registrada no recorte errado.",
            desfaz=destinacao,
        )

        assert list(destinacao.desfazimentos.all()) == [desfeito]

    def test_as_colunas_novas_sao_opcionais_para_as_linhas_antigas(self):
        """Nulas ou com padrão: a migration as acrescenta sem tocar linha antiga."""
        for nome in ("apuracao", "edital", "perfil_id", "marco_id", "versao", "desfaz"):
            assert MovimentoDeVaga._meta.get_field(nome).null, nome
        assert MovimentoDeVaga._meta.get_field("gatilho").default == ""
        assert MovimentoDeVaga._meta.get_field("fundamento").default == ""


@postgresql_only
class TestAsGarantiasDoBanco:
    """Só no PostgreSQL: a mensagem do SQLite não nomeia a constraint, e o gatilho não existe lá."""

    def test_o_gatilho_recusa_alteracao_e_exclusao_por_queryset(self, edital_e_versao):
        edital, versao = edital_e_versao
        movimento = gravar(edital, versao)

        with pytest.raises(DatabaseError, match="immutable"), transaction.atomic():
            MovimentoDeVaga.objects.filter(id=movimento.id).update(quantidade=3)
        with pytest.raises(DatabaseError, match="immutable"), transaction.atomic():
            MovimentoDeVaga.objects.filter(id=movimento.id).delete()

    @pytest.mark.parametrize(
        ("campos", "constraint"),
        [
            ({"especie": "OUTRA"}, "ck_movimento_especie"),
            ({"edital": None}, "ck_movimento_com_recorte"),
            ({"perfil_id": None}, "ck_movimento_com_recorte"),
            ({"marco_id": None}, "ck_movimento_com_recorte"),
            ({"fundamento": ""}, "ck_movimento_com_fundamento"),
            ({"quantidade": 0}, "ck_movimento_quantidade_positiva"),
            ({"origem_lista_id": None}, "ck_movimento_recortes_distintos"),
        ],
    )
    def test_as_constraints_recusam_o_movimento_malformado(
        self, edital_e_versao, campos, constraint
    ):
        edital, versao = edital_e_versao

        with pytest.raises(IntegrityError, match=constraint), transaction.atomic():
            gravar(edital, versao, **campos)

    def test_o_desfazimento_sem_citacao_e_recusado(self, edital_e_versao):
        edital, versao = edital_e_versao

        with (
            pytest.raises(IntegrityError, match="ck_desfazimento_cita_o_movimento"),
            transaction.atomic(),
        ):
            gravar(edital, versao, especie=nomes.MOVIMENTO_DESFAZIMENTO)

    def test_a_reversao_que_cita_outro_movimento_e_recusada(self, edital_e_versao):
        """Só o desfazimento cita: uma reversão com `desfaz` seria um desfazimento disfarçado."""
        edital, versao = edital_e_versao
        anterior = gravar(edital, versao)

        with (
            pytest.raises(IntegrityError, match="ck_desfazimento_cita_o_movimento"),
            transaction.atomic(),
        ):
            gravar(edital, versao, desfaz=anterior)
