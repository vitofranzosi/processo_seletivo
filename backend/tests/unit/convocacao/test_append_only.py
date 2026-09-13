"""A convocação e o desfecho nascem e não mudam mais — e a garantia não é da aplicação (019).

**Três camadas, e nenhuma basta sozinha.** O `save()` do modelo recusa a alteração vinda do ORM; o
gatilho recusa a que vem por `QuerySet.update()` e por `psql`; e o privilégio ausente recusa a que
viesse de qualquer código escrito depois, mesmo contornando as duas primeiras.

**Por que estas tabelas em particular.** É sobre elas que se decide quem ocupa vaga. Reescrever um
desfecho mudaria, sem rastro, o que a pessoa respondeu; reescrever uma comunicação moveria o
instante de onde o prazo corre — que é o que decide se alguém perdeu a vaga (`FR-272`, `FR-288a`).

**Correção é sucessão**, e é por isso que a imutabilidade não custa nada aqui: o erro de digitação
se conserta criando a linha seguinte, com motivo, e a anterior continua legível.
"""

import uuid

import pytest
from django.db import connection

from processo_seletivo.convocacao.models import (
    AtestadoDeFatoExterno,
    ComunicacaoEmitida,
    Convocacao,
    DesfechoDaConvocacao,
)
from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY, comandos_de_privilegios

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="gatilho e privilégio existem só no PostgreSQL"
)

TABELAS = (
    ("convocacao_convocacao", Convocacao),
    ("convocacao_desfechodaconvocacao", DesfechoDaConvocacao),
    ("convocacao_comunicacaoemitida", ComunicacaoEmitida),
    ("convocacao_atestadodefatoexterno", AtestadoDeFatoExterno),
)


@pytest.mark.parametrize(("tabela", "modelo"), TABELAS)
class TestAPrimeiraCamadaEOModelo:
    def test_recusa_alteracao_pelo_orm(self, tabela, modelo):
        instancia = modelo(id=uuid.uuid4())
        instancia._state.adding = False

        with pytest.raises(TypeError, match="append-only"):
            instancia.save()

    def test_recusa_exclusao_pelo_orm(self, tabela, modelo):
        with pytest.raises(TypeError, match="append-only"):
            modelo(id=uuid.uuid4()).delete()


@pytest.mark.parametrize(("tabela", "modelo"), TABELAS)
class TestATerceiraCamadaEOPrivilegioAusente:
    """**O ataque de verdade mora em `tests/integration/test_database_permissions.py`**, que
    percorre `TABELAS_APPEND_ONLY` inteira com uma role de runtime real. O que se prende aqui é o
    que faz aquele teste alcançar estas tabelas: estarem declaradas. Sem a declaração, a
    conformidade continua verde e a tabela fica sem a camada, em silêncio.
    """

    def test_a_tabela_esta_declarada_como_append_only(self, tabela, modelo):
        assert tabela in TABELAS_APPEND_ONLY

    def test_a_politica_revoga_update_e_delete_sobre_ela(self, tabela, modelo):
        comandos = " ".join(comandos_de_privilegios(migration_role="m", runtime_role="r"))

        assert "REVOKE UPDATE, DELETE" in comandos
        assert tabela in comandos


class TestVigenciaNaoEColuna:
    """**A ausência é a regra, e este teste a prende.**

    Uma flag `vigente` exigiria `UPDATE`, operação proibida nesta tabela. Quem a acrescentar não é
    barrado ao criá-la — é barrado quando tentar atualizá-la, que é o modo de falha mais tardio
    possível. Aqui o erro aparece no lugar mais cedo que existe.
    """

    def test_a_convocacao_nao_tem_coluna_de_vigencia(self):
        colunas = {campo.name for campo in Convocacao._meta.get_fields()}

        assert not colunas & {"vigente", "obsoleta", "esta_vigente", "ativa"}

    def test_nenhum_campo_diz_recebido_lido_ou_entregue(self):
        """`UX-039`: o campo que não existe é a metade da garantia.

        A outra metade é a varredura sobre as telas — prosa mente sem precisar de coluna —, mas
        esta metade é a que impede o campo de nascer e a prosa de ficar verdadeira.
        """
        colunas = {campo.name for campo in ComunicacaoEmitida._meta.get_fields()}

        assert not colunas & {"recebido_em", "lido_em", "entregue_em", "confirmado_em"}
        assert "enviado_em" in colunas

    def test_nao_existe_entidade_de_vaga(self):
        """`D-011`: há quantidade publicada e conjunto de pessoas, e nenhuma vaga numerada.

        Modelar `Vaga` resolveria a contagem trivialmente e custaria a pergunta de qual vaga cada
        pessoa ocupa — que nenhum Edital lido responde.
        """
        from django.apps import apps

        modelos = {m.__name__ for m in apps.get_app_config("convocacao").get_models()}

        assert "Vaga" not in modelos
        assert modelos == {
            "AtestadoDeFatoExterno",
            "ComunicacaoEmitida",
            "Convocacao",
            "DesfechoDaConvocacao",
        }
