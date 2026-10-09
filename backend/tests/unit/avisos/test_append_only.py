"""O registro do envio nasce e não muda; o modelo de aviso muda e não se exclui (066, `FR-1277`).

**Três camadas, e nenhuma basta sozinha.** O `save()` do modelo recusa a alteração vinda do ORM; o
gatilho recusa a que vem por `QuerySet.update()` e por `psql`; e o privilégio ausente recusa a que
viesse de qualquer código escrito depois. O privilégio é atacado de verdade em
`tests/integration/test_database_permissions.py`, que percorre `TABELAS_APPEND_ONLY`, e a presença
dos sete gatilhos é conferida no catálogo por `tests/migrations/test_migrations.py`
(`TRIGGERS_POR_APP["avisos"]`). Aqui se prende que as seis estão declaradas, e o gatilho do modelo
de aviso numa linha real — a única das sete tabelas sem FK.

**Por que estas tabelas.** É este registro que diz se uma mensagem saiu. Reescrever uma tentativa
apagaria a prova de que o servidor de correio aceitou, ou faria o despacho tomar por pendente o que
já foi enviado — e reenviar.
"""

import pytest
from django.db import connection, transaction
from django.utils import timezone

from processo_seletivo.avisos.models import (
    Aviso,
    DestinatarioDoAviso,
    InterrupcaoDoAviso,
    ModeloDeAviso,
    PublicacaoDoAviso,
    ResultadoDaTentativa,
    TentativaDeEnvio,
)
from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY, comandos_de_privilegios

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="gatilho e privilégio existem só no PostgreSQL"
)

TABELAS = (
    ("avisos_aviso", Aviso),
    ("avisos_publicacaodoaviso", PublicacaoDoAviso),
    ("avisos_destinatariodoaviso", DestinatarioDoAviso),
    ("avisos_tentativadeenvio", TentativaDeEnvio),
    ("avisos_resultadodatentativa", ResultadoDaTentativa),
    ("avisos_interrupcaodoaviso", InterrupcaoDoAviso),
)


@pytest.mark.parametrize(("tabela", "modelo"), TABELAS)
class TestOModeloRecusa:
    def test_recusa_alteracao_pelo_orm(self, tabela, modelo):
        instancia = modelo()
        instancia._state.adding = False

        with pytest.raises(TypeError, match="append-only"):
            instancia.save()

    def test_recusa_exclusao_pelo_orm(self, tabela, modelo):
        with pytest.raises(TypeError, match="append-only"):
            modelo().delete()

    def test_a_tabela_esta_declarada_como_append_only(self, tabela, modelo):
        assert tabela in TABELAS_APPEND_ONLY
        comandos = " ".join(comandos_de_privilegios(migration_role="m", runtime_role="r"))
        assert "REVOKE UPDATE, DELETE" in comandos


class TestOModeloDeAvisoMudaENaoSeExclui:
    def test_recusa_exclusao_pelo_orm(self):
        with pytest.raises(TypeError, match="não se exclui"):
            ModeloDeAviso().delete()

    def test_fica_fora_da_lista_porque_muda(self):
        """Editar e inativar são `UPDATE` legítimos; tirá-lo da lista é o que os permite."""
        assert "avisos_modelodeaviso" not in TABELAS_APPEND_ONLY


class TestEstadoNaoEColuna:
    """**A ausência é a regra, e este teste a prende** (data-model §2).

    Uma coluna de estado no destinatário exigiria `UPDATE`, proibido aqui. Quem a acrescentar não é
    barrado ao criá-la — é barrado quando tentar atualizá-la, o modo de falha mais tardio possível.
    """

    def test_o_destinatario_nao_tem_coluna_de_estado(self):
        colunas = {campo.name for campo in DestinatarioDoAviso._meta.get_fields()}

        assert not colunas & {"estado", "status", "enviado", "pendente", "situacao"}

    def test_nenhum_campo_diz_entregue_recebida_ou_lida(self):
        """`UX-172`: o campo que não existe é metade da garantia; a varredura das telas, a outra."""
        colunas = set()
        for _, modelo in TABELAS:
            colunas |= {campo.name for campo in modelo._meta.get_fields()}

        assert not colunas & {"entregue_em", "recebido_em", "lido_em", "aberto_em", "entregue"}


@postgresql_only
@pytest.mark.django_db
def test_o_gatilho_recusa_excluir_o_modelo_e_aceita_edita_lo():
    modelo = ModeloDeAviso.objects.create(
        institution_scope="cefor",
        nome="Teste",
        assunto="Assunto",
        corpo="Corpo",
        criado_por="p",
        criado_em=timezone.now(),
    )

    ModeloDeAviso.objects.filter(pk=modelo.pk).update(ativo=False)
    with pytest.raises(Exception, match="não se exclui"), transaction.atomic():
        ModeloDeAviso.objects.filter(pk=modelo.pk)._raw_delete(using="default")
