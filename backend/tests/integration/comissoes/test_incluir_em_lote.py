"""Constituir a comissão em lote — o custo que sobrou depois de a alocação ficar barata.

Pessoa a pessoa eram dois envios por servidor, o formulário e a conferência: oitenta passos para
montar uma banca de quarenta.
"""

import pytest

from processo_seletivo.comissoes.application.comissao import adicionar_varios
from processo_seletivo.comissoes.models import MembroComissao
from processo_seletivo.shared.api.problems import DomainError

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def lote(gestor, processo, entradas, funcao="MEMBRO", chave="lote-1"):
    return adicionar_varios(
        actor=gestor,
        processo_id=processo.id,
        entradas=entradas,
        funcao=funcao,
        idempotency_key=chave,
        correlation_id="c",
    )


def test_inclui_a_lista_inteira_numa_submissao(gestor, processo_a):
    criados, ja = lote(
        gestor, processo_a, [("ana", "Ana Costa"), ("joao", "João Souza"), ("bia", "")]
    )

    assert len(criados) == 3 and ja == []
    assert MembroComissao.objects.filter(processo=processo_a, ativo=True).count() == 3
    assert MembroComissao.objects.get(identity_subject="ana").display_label == "Ana Costa"


def test_quem_ja_integra_nao_faz_o_lote_falhar(gestor, processo_a, comissao_de_a):
    """Recusar oitenta porque uma pessoa já estava seria punir o caminho normal."""
    criados, ja = lote(gestor, processo_a, [("joao", ""), ("ana", "Ana Costa")])

    assert [m.identity_subject for m in criados] == ["ana"]
    assert ja == ["joao"]


def test_a_mesma_pessoa_repetida_na_lista_entra_uma_vez(gestor, processo_a):
    """Repetir é engano de quem colou, e não conflito."""
    criados, _ = lote(gestor, processo_a, [("ana", "Ana Costa"), ("ana", "Ana C.")])

    assert len(criados) == 1
    assert MembroComissao.objects.get(identity_subject="ana").display_label == "Ana Costa"


def test_lista_vazia_e_recusada(gestor, processo_a):
    with pytest.raises(DomainError) as recusa:
        lote(gestor, processo_a, [("", ""), ("   ", "Nome sem identificador")])

    assert recusa.value.code == "identificador_ausente"


def test_cada_inclusao_do_lote_gera_o_seu_evento(gestor, auditor, processo_a):
    from processo_seletivo.auditoria.selectors import trilha_da_comissao

    lote(gestor, processo_a, [("ana", ""), ("joao", "")])

    registros, _ = trilha_da_comissao(actor=auditor, processo=processo_a, limit=100)
    inclusoes = [r for r in registros if r.operation == "COMISSAO_INCLUIR_MEMBRO"]
    assert len(inclusoes) == 2
    assert all("em lote" in r.reason for r in inclusoes)


def test_repetir_o_lote_com_a_mesma_chave_nao_duplica(gestor, processo_a):
    lote(gestor, processo_a, [("ana", "")], chave="k")
    criados, _ = lote(gestor, processo_a, [("ana", "")], chave="k")

    assert criados == []
    assert MembroComissao.objects.filter(processo=processo_a, ativo=True).count() == 1


def test_o_lote_respeita_o_estado_final_do_processo(gestor, processo_a):
    from processo_seletivo.processos.models import ProcessoSeletivo

    ProcessoSeletivo.objects.filter(pk=processo_a.pk).update(status="ENCERRADO")

    with pytest.raises(DomainError):
        lote(gestor, processo_a, [("ana", "")])
