"""O cenário montado como se tivesse ocorrido há N dias (`--dias-atras`, 134).

O pedido veio do treinamento: o C10 nasce com o preliminar divulgado na hora da carga, a janela
recursal de cinco dias corridos fica aberta, e o definitivo, a vaga não preenchida e o encerramento
esperam por ela. Com o relógio atrasado a janela nasce encerrada — pelos mesmos comandos.
"""

from datetime import timedelta

import pytest
from django.core.management import CommandError
from django.utils import timezone

from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.processos.application import pendencias_do_edital as p
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.treinamento import carregar, restaurar, verificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

AUTORIDADE = str(AUTORIDADE_DA_SUITE)


def _manifesto(codigo):
    return CenarioDeTreinamento.objects.get(codigo=codigo, situacao="PRONTO")


def _prazo_recursal_em_curso(manifesto):
    edital = Edital.objects.get(processo=manifesto.processo)
    return [
        situacao
        for situacao in p.impedimentos(edital, agora=timezone.now())
        if situacao.tipo == p.PRAZO_RECURSAL_EM_CURSO
    ]


def test_sem_atraso_o_prazo_recursal_do_c10_impede(treinamento):
    """A linha de base: é este impedimento que o atraso existe para tirar."""
    carregar("C10", autoridade=AUTORIDADE)
    assert _prazo_recursal_em_curso(_manifesto("C10"))


def test_com_seis_dias_de_atraso_a_janela_do_c10_nasce_encerrada(treinamento):
    antes = timezone.now()
    saida = carregar("C10", autoridade=AUTORIDADE, dias_atras=6)
    assert "CRIADO" in saida, saida
    manifesto = _manifesto("C10")
    assert not _prazo_recursal_em_curso(manifesto)
    # Os atos e o manifesto são do instante atrasado, e não um prazo afrouxado.
    publicacao = PublicacaoResultado.objects.get(edital__processo=manifesto.processo)
    assert publicacao.publicado_em < antes - timedelta(days=5)
    assert manifesto.criado_em < antes - timedelta(days=5)
    assert "há 6 dia(s)" in manifesto.criado_por
    assert "INTACTO" in verificar("C10")


def test_a_restauracao_atrasa_a_rodada_nova_e_cancela_a_anterior_agora(treinamento):
    carregar("C10", autoridade=AUTORIDADE)
    anterior = _manifesto("C10")
    antes = timezone.now()
    saida = restaurar("C10", confirmar="C10", autoridade=AUTORIDADE, dias_atras=6)
    assert "datados de 6 dia(s) atrás" in saida, saida
    novo = _manifesto("C10")
    assert novo.rodada == anterior.rodada + 1
    assert not _prazo_recursal_em_curso(novo)
    cancelado = ProcessoSeletivo.objects.get(pk=anterior.processo_id)
    assert cancelado.status == ProcessoSeletivo.Status.CANCELADO
    assert cancelado.last_changed_at >= antes


def test_atraso_que_venceria_o_estado_inicial_e_recusado_sem_gravar(treinamento):
    """O C08 vale cinco dias — a janela em que o candidato recorre. Há seis, nasceria fechada."""
    saida = carregar("C08", autoridade=AUTORIDADE, dias_atras=6)
    assert "FALHOU" in saida and "nasceria vencido" in saida, saida
    assert not CenarioDeTreinamento.objects.exists()
    assert not ProcessoSeletivo.objects.filter(institutional_code__startswith="SIM-").exists()


def test_atraso_anterior_a_vigencia_da_autoridade_e_recusado(treinamento):
    saida = carregar("C10", autoridade=AUTORIDADE, dias_atras=365 * 40)
    assert "FALHOU" in saida and "não era vigente" in saida, saida
    assert not CenarioDeTreinamento.objects.exists()


def test_atraso_negativo_e_recusado(treinamento):
    saida = carregar("C10", autoridade=AUTORIDADE, dias_atras=-1)
    assert "FALHOU" in saida and "negativo" in saida, saida


def test_a_restauracao_recusada_pelo_atraso_nao_cancela_a_rodada_em_uso(treinamento):
    carregar("C08", autoridade=AUTORIDADE)
    anterior = _manifesto("C08")
    with pytest.raises(CommandError, match="nasceria vencido"):
        restaurar("C08", confirmar="C08", autoridade=AUTORIDADE, dias_atras=6)
    assert _manifesto("C08").pk == anterior.pk
    assert ProcessoSeletivo.objects.get(pk=anterior.processo_id).status != "CANCELADO"


def test_o_catalogo_inteiro_monta_atrasado_menos_o_que_venceria(treinamento):
    """Seis dias: tudo menos o C08, recusado sozinho — os demais não dependem dele (FR-4612)."""
    saida = carregar(autoridade=AUTORIDADE, dias_atras=6)
    assert saida.count("CRIADO") == 16, saida
    assert saida.count("FALHOU") == 1 and "C08" in saida, saida
    assert verificar().count("INTACTO") == 16
