"""As invariantes do requerimento que o **banco** garante (029, `FR-376`, `FR-394`, `FR-408`).

**O que este arquivo deliberadamente não exercita: o sucessor que dá certo.** Criar um sucessor
válido exige uma `Convocacao`, que exige uma `ApuracaoDeOcupacao`, que exige um `AtoDeOrdenacao` — e
este último tem gatilho de proveniência que recusa ato montado à mão: *"ordering act universe does
not match the act it belongs to"*. Montar a cadeia inteira aqui faria um teste de **restrição de
banco** depender da classificação, do corte e da ocupação inteiras; quando qualquer uma delas
mudasse, este arquivo quebraria sem que nada do requerimento tivesse mudado.

O caminho feliz da sucessão — e com ele a `uq_requerimento_sucessor_unico` — é exercitado onde a
cadeia já existe montada pela aplicação: no teste de sucessão da `US5`, com
`montar_cenario_da_convocacao`. Aqui fica o que o banco recusa **sem** depender de nada disso.

**Por que no banco, e não só no comando.** Cada uma decide o que o Registro Acadêmico vai ler e o
que um indeferimento vai fundamentar. Confiá-las à aplicação é confiar que todo caminho futuro se
lembre — inclusive o comando de manutenção que ninguém escreveu ainda.
"""

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from processo_seletivo.requerimentos.domain import nomes
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula

pytestmark = pytest.mark.django_db


def _criar(inscricao, campos, **extra):
    agora = timezone.now()
    return RequerimentoDeMatricula.objects.create(
        inscricao=inscricao, disponibilizado_em=agora, created_at=agora, **campos, **extra
    )


class TestUmaRaizPorInscricao:
    def test_a_segunda_raiz_e_recusada(self, inscricao, campos_declarados, rascunho):
        with pytest.raises(IntegrityError), transaction.atomic():
            _criar(inscricao, campos_declarados)


class TestSucessorExigeChamadaQueOAutorize:
    def test_sucessor_sem_convocacao_e_recusado(self, inscricao, campos_declarados, rascunho):
        """Sem a chamada que o autoriza, sucessão seria edição com outro nome (`FR-408`)."""
        with pytest.raises(IntegrityError), transaction.atomic():
            _criar(inscricao, campos_declarados, requerimento_anterior=rascunho)


class TestEnviadoExigeOAceiteCompleto:
    """*Enviado* sem instante, versão, resumo ou aceite **não é alcançável** (`FR-394`).

    É o molde de `ck_inscricao_submetida_completa`: o que o estado significa dito no banco, e não
    prometido no código. Sem isto, um requerimento poderia constar como enviado sem que ninguém
    tivesse aceitado declaração alguma — e o aceite é o que o indeferimento por informação falsa
    invoca.
    """

    @pytest.mark.parametrize(
        "faltando",
        ["enviado_em", "versao_aceita", "declaracao_hash", "declaracao_aceita_em"],
    )
    def test_falta_uma_peca_do_aceite(self, rascunho, versao_consolidada, faltando):
        agora = timezone.now()
        completo = {
            "status": nomes.ENVIADO,
            "enviado_em": agora,
            "versao_aceita": versao_consolidada,
            "declaracao_hash": "a" * 64,
            "declaracao_aceita_em": agora,
        }
        completo[faltando] = "" if faltando == "declaracao_hash" else None

        with pytest.raises(IntegrityError), transaction.atomic():
            RequerimentoDeMatricula.objects.filter(pk=rascunho.pk).update(**completo)

    def test_com_todas_as_pecas_o_envio_passa(self, rascunho, versao_consolidada):
        agora = timezone.now()

        RequerimentoDeMatricula.objects.filter(pk=rascunho.pk).update(
            status=nomes.ENVIADO,
            enviado_em=agora,
            versao_aceita=versao_consolidada,
            declaracao_hash="a" * 64,
            declaracao_aceita_em=agora,
        )

        assert RequerimentoDeMatricula.objects.get(pk=rascunho.pk).status == nomes.ENVIADO


class TestEstadoFechado:
    def test_estado_fora_da_lista_e_recusado(self, rascunho):
        with pytest.raises(IntegrityError), transaction.atomic():
            RequerimentoDeMatricula.objects.filter(pk=rascunho.pk).update(status="EM_ANALISE")

    def test_em_analise_nao_e_estado_desta_feature(self):
        """**A ausência é a fronteira com a `019`**, e ela é escrita aqui de propósito.

        *Em análise*, *deferido* e *indeferido* são desfechos da convocação, com ator, fundamento e
        auditoria próprios. Recriá-los aqui seria uma segunda fonte de verdade sobre a mesma vaga —
        e o primeiro sintoma seria uma tela dizendo ao candidato algo que esta feature não decide.
        """
        assert nomes.ESTADOS == (nomes.RASCUNHO, nomes.ENVIADO)
