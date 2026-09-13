"""O efeito de ocupação nasce e não muda mais — e a garantia não depende da aplicação (019).

**Três camadas, e nenhuma basta sozinha.** O `save()` do modelo recusa a alteração vinda do ORM; o
gatilho recusa a que vem por `QuerySet.update()` e por `psql`; e o privilégio ausente recusa a que
viesse de qualquer código escrito depois, mesmo contornando as duas primeiras.

**Por que esta tabela em particular.** Ela é a única linha que explica por que a contagem de
ocupação de hoje difere da de ontem. Reescrever um efeito faria a diferença ficar sem causa, e o
número que alguém vai contestar deixaria de ser reconstruível a partir dos atos.
"""

import uuid

import pytest
from django.db import connection
from django.db.utils import DatabaseError
from django.utils import timezone

from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import EfeitoDeOcupacao
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY, comandos_de_privilegios

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="gatilho e privilégio existem só no PostgreSQL"
)


class TestAPrimeiraCamadaEOModelo:
    def test_recusa_alteracao_pelo_orm(self):
        efeito = EfeitoDeOcupacao(id=uuid.uuid4(), registrado_em=timezone.now())
        efeito._state.adding = False

        with pytest.raises(TypeError, match="append-only"):
            efeito.save()

    def test_recusa_exclusao_pelo_orm(self):
        with pytest.raises(TypeError, match="append-only"):
            EfeitoDeOcupacao(id=uuid.uuid4()).delete()

    def test_o_ato_de_origem_e_a_inscricao_nao_sao_chaves_estrangeiras(self):
        """**A ausência das FKs é a decisão** (019, `R-003`), e este teste a prende.

        Uma FK de `ocupacao` para `convocacao` inverteria a dependência no grafo de migrations, que
        é onde ela é irreversível: a `016` passaria a não poder migrar sem a `019`. Quem trocar o
        `UUIDField` por `ForeignKey` não é barrado ao escrever a linha — é barrado meses depois, ao
        descobrir que os dois apps não migram mais separados.
        """
        campos = {campo.name: campo for campo in EfeitoDeOcupacao._meta.get_fields()}
        assert campos["inscricao_id"].get_internal_type() == "UUIDField"
        assert campos["ato_de_origem_id"].get_internal_type() == "UUIDField"
        assert "inscricao" not in campos
        assert "ato_de_origem" not in campos

    def test_nao_ha_unicidade_por_inscricao_e_recorte(self):
        """**A ausência é deliberada** (019, `R-003`).

        Duas exclusões da mesma pessoa em ciclos diferentes são fatos distintos, e os dois
        aconteceram. O que a apuração faz com eles é conjunto, não soma — e é isso que evita o `−2`.
        """
        unicidades = [
            c
            for c in EfeitoDeOcupacao._meta.constraints
            if c.__class__.__name__ == "UniqueConstraint"
        ]
        assert unicidades == []


class TestATerceiraCamadaEOPrivilegioAusente:
    """A camada que recusa até o código escrito depois, contornando as outras duas.

    **O ataque de verdade mora em `tests/integration/test_database_permissions.py`**, que percorre
    `TABELAS_APPEND_ONLY` inteira com uma role de runtime real e tenta `UPDATE` e `DELETE` em cada
    uma. O que se prende aqui é o que faz aquele teste alcançar esta tabela: estar declarada. Sem a
    declaração, a conformidade continua verde — e a tabela fica sem a camada, em silêncio.
    """

    def test_a_tabela_esta_declarada_como_append_only(self):
        assert "ocupacao_efeitodeocupacao" in TABELAS_APPEND_ONLY

    def test_a_politica_revoga_update_e_delete_sobre_ela(self):
        comandos = " ".join(comandos_de_privilegios(migration_role="m", runtime_role="r"))
        assert "REVOKE UPDATE, DELETE" in comandos
        assert "ocupacao_efeitodeocupacao" in comandos


@pytest.mark.django_db
@postgresql_only
class TestASegundaCamadaEOGatilho:
    """`QuerySet.update()` não passa pelo `save()` do modelo, e o gatilho é quem o barra."""

    @pytest.fixture
    def efeito(self):
        agora = timezone.now()
        processo = ProcessoSeletivo.objects.create(
            institution_scope="cefor",
            institutional_code="PS-019-EFEITO",
            title="Processo do efeito",
            created_at=agora,
            created_by="teste",
            last_changed_at=agora,
        )
        edital = Edital.objects.create(
            processo=processo,
            institution_scope="cefor",
            number="019",
            year=2026,
            title="Edital do efeito",
            created_at=timezone.now(),
            created_by="teste",
            last_edited_by="teste",
        )
        return EfeitoDeOcupacao.objects.create(
            edital=edital,
            perfil_id=uuid.uuid4(),
            marco_id=uuid.uuid4(),
            lista_id=None,
            inscricao_id=uuid.uuid4(),
            especie=nomes.EFEITO_EXCLUSAO,
            fundamento="Desistência expressa",
            ato_de_origem_id=uuid.uuid4(),
            rotulo_da_origem="desfecho de convocação",
            registrado_por="teste",
            registrado_em=timezone.now(),
        )

    def test_o_gatilho_recusa_alteracao_por_queryset(self, efeito):
        with pytest.raises(DatabaseError, match="immutable"):
            EfeitoDeOcupacao.objects.filter(id=efeito.id).update(especie=nomes.EFEITO_INCLUSAO)

    def test_o_gatilho_recusa_exclusao_por_queryset(self, efeito):
        with pytest.raises(DatabaseError, match="immutable"):
            EfeitoDeOcupacao.objects.filter(id=efeito.id).delete()
