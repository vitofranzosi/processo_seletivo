"""A vaga acrescida nasce e não muda mais — e a garantia não depende da aplicação (097).

**Três camadas, como as do efeito de ocupação.** O `save()` do modelo recusa a alteração vinda do
ORM; o gatilho recusa a que vem por `QuerySet.update()`; e o privilégio ausente recusa a que viesse
de qualquer código escrito depois. Aqui ficam a primeira e a terceira; o gatilho e as `CHECK`
precisam de linha gravada, e moram em `tests/integration/ocupacao/test_acrescimo.py`.

**Por que esta tabela em particular.** Ela é o que explica por que um recorte de 0 vagas publicadas
tem 3 efetivas. Reescrever um acréscimo faria a diferença ficar sem causa — e o desfazimento existe
justamente para que o erro se corrija sem apagar o que foi declarado.
"""

import uuid

import pytest

from processo_seletivo.ocupacao.models import AcrescimoDeVagas
from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY, comandos_de_privilegios


class TestAPrimeiraCamadaEOModelo:
    def test_recusa_alteracao_pelo_orm(self):
        acrescimo = AcrescimoDeVagas(id=uuid.uuid4())
        acrescimo._state.adding = False

        with pytest.raises(TypeError, match="append-only"):
            acrescimo.save()

    def test_recusa_exclusao_pelo_orm(self):
        with pytest.raises(TypeError, match="append-only"):
            AcrescimoDeVagas(id=uuid.uuid4()).delete()

    def test_o_desfazimento_cita_o_acrescimo_pela_mesma_tabela(self):
        """**Uma tabela para os dois** (`T-001`): o desfazimento cita o acréscimo, e não um id.

        Um `UUIDField` aqui deixaria citar acréscimo que não existe, e a trava do saldo (`FR-2462`)
        somaria desfazimentos de nada.
        """
        campo = AcrescimoDeVagas._meta.get_field("desfaz")
        assert campo.related_model is AcrescimoDeVagas
        assert campo.null

    def test_o_recorte_nao_e_chave_estrangeira_para_a_classificacao(self):
        """Perfil, marco e lista são identidades do conteúdo publicado, como na apuração."""
        for nome in ("perfil_id", "marco_id", "lista_id"):
            assert AcrescimoDeVagas._meta.get_field(nome).get_internal_type() == "UUIDField"


class TestATerceiraCamadaEOPrivilegioAusente:
    """O ataque de verdade mora em `tests/integration/test_database_permissions.py`, que percorre a
    lista inteira com a role de runtime. O que se prende aqui é estar declarada."""

    def test_a_tabela_esta_declarada_como_append_only(self):
        assert "ocupacao_acrescimodevagas" in TABELAS_APPEND_ONLY

    def test_a_politica_revoga_update_e_delete_sobre_ela(self):
        comandos = " ".join(comandos_de_privilegios(migration_role="m", runtime_role="r"))
        assert "REVOKE UPDATE, DELETE" in comandos
        assert "ocupacao_acrescimodevagas" in comandos
