"""Quantas chamadas a vaga faltante cobre — e por que o número da apuração não basta (019).

**O defeito que esta guarda impede não dá erro: dá duas pessoas na mesma vaga.** Convocar não
produz efeito nenhum na porta da `016`, de modo que a apuração vigente continua dizendo o mesmo
número enquanto ninguém responde. Lido cru, ele autorizaria chamar dois suplentes para a mesma vaga.

E o pior vem depois: os dois aceitariam, o conjunto de ocupantes passaria do teto, e o
`min(ocupantes, efetivas)` da contagem devolveria o número **certo** — escondendo o fato. Nada
acusaria, e a instituição descobriria pela pessoa que ficou sem a vaga que lhe foi prometida.
"""

from types import SimpleNamespace

import pytest

from processo_seletivo.convocacao.application.convocar import _recusar_por_deficit
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.shared.api.problems import DomainError

TITULAR = "p1"
SUPLENTE = "p2"
OUTRO_SUPLENTE = "p3"


def apuracao(faltando):
    return SimpleNamespace(faltando=faltando)


def contexto(*, ocupando=(TITULAR,), em_aberto=()):
    return {"ocupando": {str(i) for i in ocupando}, "emAberto": set(em_aberto)}


def recusar(*, especie=nomes.SUPLENCIA, inscricao=SUPLENTE, faltando=1, em_aberto=(), sucede=None):
    _recusar_por_deficit(
        contexto(em_aberto=em_aberto),
        especie=especie,
        inscricao=inscricao,
        apuracao=apuracao(faltando),
        sucede=sucede,
    )


def test_o_titular_passa_mesmo_sem_vaga_faltante():
    """**A primeira convocação de todo certame acontece com `faltando` em zero.**

    Pela contagem da `016` o titular ocupa vaga desde a emissão da apuração, antes de ser chamado:
    convocá-lo é formalizar o que o número já diz. Exigir déficit ali recusaria a chamada de quem
    já tem a vaga — que é exatamente o ato que a `US1` existe para praticar.
    """
    recusar(especie=nomes.VAGA_INICIAL, inscricao=TITULAR, faltando=0)


def test_o_suplente_passa_quando_ha_vaga_faltante():
    recusar(faltando=1)


def test_o_suplente_e_recusado_sem_vaga_faltante():
    with pytest.raises(DomainError) as erro:
        recusar(faltando=0)

    assert erro.value.code == nomes.SEM_DEFICIT


def test_a_vaga_faltante_nao_cobre_duas_chamadas_em_aberto():
    """A segunda chamada para a mesma vaga é recusada **antes** de alguém aceitar.

    É a única janela em que o defeito ainda tem conserto: depois dos dois aceites, as duas pessoas
    foram alcançadas de verdade, e nenhuma delas fez nada de errado.
    """
    with pytest.raises(DomainError) as erro:
        recusar(faltando=1, em_aberto=(SUPLENTE,), inscricao=OUTRO_SUPLENTE)

    assert erro.value.code == nomes.SEM_DEFICIT
    assert "já estão cobertas por 1 convocação" in erro.value.detail


def test_a_chamada_em_aberto_de_um_titular_nao_consome_vaga_faltante():
    """**Ela não acrescenta ocupante nenhum**: o titular já está contado.

    Contá-la bloquearia a suplência sem razão — e no recorte do 77/2026, com 40 titulares chamados
    e uma vaga vaga, nenhuma suplente poderia ser convocada.
    """
    recusar(faltando=1, em_aberto=(TITULAR,))


def test_corrigir_a_propria_chamada_nao_conta_contra_quem_a_corrige():
    """Suceder uma convocação não é abrir uma segunda: a vaga continua sendo a mesma."""
    recusar(
        faltando=1,
        em_aberto=(SUPLENTE,),
        inscricao=SUPLENTE,
        sucede=SimpleNamespace(inscricao_id=SUPLENTE),
    )


def test_a_convocacao_para_regularizar_exige_vaga_faltante():
    """A regra da `US3` é esta mesma, dita de outro jeito.

    *"Admitida só quando as matrículas deferidas do recorte são menos que as vagas"* é exatamente
    `faltando > 0` — e o indeferido não é ocupante, logo acrescenta. Chamar alguém para regularizar
    num recorte com todas as vagas ocupadas prometeria uma vaga que não existe, e a pessoa faria o
    trabalho de corrigir a documentação para nada.
    """
    recusar(especie=nomes.PARA_REGULARIZAR, faltando=1)

    with pytest.raises(DomainError) as erro:
        recusar(especie=nomes.PARA_REGULARIZAR, faltando=0)

    assert erro.value.code == nomes.SEM_DEFICIT
