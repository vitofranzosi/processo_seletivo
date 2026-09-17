"""Requerimento enviado não muda e não sai — e a garantia não depende da aplicação (029, `FR-396`).

**Duas camadas, e não três.** A guarda do modelo recusa o que vem pelo ORM; o gatilho recusa o que
vem por `QuerySet.update()` e por `psql`. A terceira camada das tabelas append-only — o privilégio
ausente — **não existe aqui de propósito**: a role de runtime precisa de `UPDATE` para o rascunho
existir, e privilégio de tabela não sabe ler `status`. É a mesma razão pela qual `Inscricao` e
`Retificacao` ficam fora de `TABELAS_APPEND_ONLY`, e é por isso que o provisionamento continua
dizendo `31 de 31`.

**A conexão da suíte é a mais privilegiada que existe**, e isso torna o teste do gatilho mais forte,
não mais fraco: se ele recusa aqui, recusa para qualquer papel. Um teste com a role de runtime
provaria menos — ela tem *menos* privilégio que esta.
"""

import pytest
from django.db import connection
from django.db.utils import DatabaseError
from django.utils import timezone

from processo_seletivo.requerimentos.domain import nomes
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula
from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="o gatilho existe só no PostgreSQL"
)


@pytest.fixture
def enviado(rascunho, versao_consolidada):
    RequerimentoDeMatricula.objects.filter(pk=rascunho.pk).update(
        status=nomes.ENVIADO,
        enviado_em=timezone.now(),
        versao_aceita=versao_consolidada,
        declaracao_hash="a" * 64,
        declaracao_aceita_em=timezone.now(),
    )
    return RequerimentoDeMatricula.objects.get(pk=rascunho.pk)


class TestAPrimeiraCamadaEOModelo:
    def test_recusa_alteracao_pelo_orm(self, enviado):
        enviado.telefone_celular = "(27) 98888-0000"

        with pytest.raises(TypeError, match="não é alterado"):
            enviado.save()

    def test_recusa_exclusao_pelo_orm(self, enviado):
        with pytest.raises(TypeError, match="não é excluído"):
            enviado.delete()

    def test_o_rascunho_continua_mudando(self, rascunho):
        """A imutabilidade é **condicional ao estado**, e o rascunho é o estado que muda.

        Sem esta metade, a guarda viraria append-only — e o candidato não conseguiria preencher em
        duas sessões, que é o caso normal de um formulário de vinte campos.
        """
        rascunho.telefone_celular = "(27) 98888-0000"
        rascunho.save()

        assert RequerimentoDeMatricula.objects.get(pk=rascunho.pk).telefone_celular.endswith("0000")


class TestATabelaNaoEAppendOnly:
    def test_a_tabela_fica_fora_da_politica_de_privilegios(self):
        """**A ausência é a decisão**, e este teste a prende.

        Quem acrescentar a tabela àquela tupla não é barrado ao escrever a linha: é barrado quando o
        candidato não conseguir mais gravar o próprio rascunho, porque a role de runtime terá
        perdido o `UPDATE`. E o provisionamento passaria a dizer `32 de 32`, quebrando a contagem
        que o `AGENTS.md` usa como sinal de que a segunda passada rodou.
        """
        assert "requerimentos_requerimentodematricula" not in TABELAS_APPEND_ONLY


@pytest.mark.django_db
@postgresql_only
class TestASegundaCamadaEOGatilho:
    """`QuerySet.update()` não passa pelo `save()` do modelo, e o gatilho é quem o barra."""

    def test_recusa_alteracao_por_queryset(self, enviado):
        with pytest.raises(DatabaseError, match="immutable"):
            RequerimentoDeMatricula.objects.filter(pk=enviado.pk).update(rg="7654321")

    def test_recusa_exclusao_por_queryset(self, enviado):
        with pytest.raises(DatabaseError, match="immutable"):
            RequerimentoDeMatricula.objects.filter(pk=enviado.pk).delete()

    def test_o_gatilho_nao_alcanca_o_rascunho(self, rascunho):
        RequerimentoDeMatricula.objects.filter(pk=rascunho.pk).update(rg="7654321")

        assert RequerimentoDeMatricula.objects.get(pk=rascunho.pk).rg == "7654321"
