"""Os dois eixos, e o contorno que cada um fecha (FR-074, FR-099, D-004).

`MembroComissao` é **vínculo**: a remoção o inativa e a readmissão cria outro. Ancorar nele o que é
**fato sobre a pessoa** deixaria remover-e-readicionar contornar duas garantias — a conclusão única
e o impedimento. Por isso as duas se ancoram na identidade institucional estável.

A Atribuição segue no vínculo, e de propósito: ela é trabalho distribuído sob uma composição de
comissão, e não um fato sobre a pessoa.
"""

import pytest

from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.avaliacoes.application.impedimento import registrar_impedimento
from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao, Impedimento
from processo_seletivo.comissoes.application.comissao import adicionar_membro, remover_membro
from processo_seletivo.comissoes.domain.funcoes import Funcao
from tests.fixtures.comissao import alocar_em
from tests.fixtures.mesa import concluir_como, distribuir_para, inscricoes_de, montar_banca

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_banca(gestor, api_client, manager_headers, seed=11, codigo="B1")


def readicionar(gestor, cenario, subject, *, chave):
    """Remove da comissão e readiciona — o vínculo novo é **outra linha**."""
    remover_membro(
        actor=gestor,
        processo_id=cenario["processo"].id,
        membro_id=cenario["membros"][subject].id,
        idempotency_key=f"sai-{chave}",
        correlation_id="teste",
    )
    novo, _ = adicionar_membro(
        actor=gestor,
        processo_id=cenario["processo"].id,
        identity_subject=subject,
        funcao=Funcao.MEMBRO,
        idempotency_key=f"volta-{chave}",
        correlation_id="teste",
    )
    alocar_em(
        gestor, cenario["processo"], novo, cenario["edital"], cenario["etapa"], chave=f"al-{chave}"
    )
    return novo


def test_readicionar_nao_libera_uma_segunda_conclusao(gestor, cenario):
    """FR-074, e o motivo de a garantia não usar `membro_id`.

    Se o índice fosse pelo vínculo, o vínculo novo teria outro identificador e a segunda conclusão
    passaria — exatamente o contorno que o requisito existe para fechar.
    """
    inscricao = inscricoes_de(cenario, 1, primeiro=1100)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao])
    concluir_como(cenario, "joao", inscricao, pontuacao="95")
    novo_vinculo = readicionar(gestor, cenario, "joao", chave="a")

    resultado = distribuir(
        actor=gestor,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        membro_ids=[novo_vinculo.id],
        inscricao_ids=[inscricao.id],
        idempotency_key="depois-da-volta",
        correlation_id="teste",
    )

    assert resultado["feitas"] == 0
    assert "já concluiu" in resultado["motivos"][0]["motivo"]
    assert Avaliacao.objects.filter(inscricao_id=inscricao.id).count() == 1


def test_readicionar_nao_apaga_o_impedimento(gestor, cenario):
    """FR-099: impedimento nomeia razão que não muda por reorganização administrativa."""
    inscricao = inscricoes_de(cenario, 1, primeiro=1110)[0]
    registrar_impedimento(
        actor=gestor,
        processo_id=cenario["processo"].id,
        identity_subject="ana",
        inscricao_id=inscricao.id,
        motivo="Parentesco.",
        idempotency_key="imp-ana",
        correlation_id="teste",
    )
    novo_vinculo = readicionar(gestor, cenario, "ana", chave="b")

    resultado = distribuir(
        actor=gestor,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        membro_ids=[novo_vinculo.id],
        inscricao_ids=[inscricao.id],
        idempotency_key="ana-de-volta",
        correlation_id="teste",
    )

    assert Impedimento.objects.filter(identity_subject="ana").count() == 1
    assert resultado["feitas"] == 0
    assert "impedimento" in resultado["motivos"][0]["motivo"].lower()


def test_as_atribuicoes_do_vinculo_antigo_nao_revivem(gestor, cenario):
    """EC-013: a assimetria que D-004 produz de propósito.

    Perder a **alocação** é reversível — devolvê-la restaura o acesso às mesmas linhas. Perder o
    **vínculo de comissão** não é: readicionar alguém é constituir a comissão de novo, e as
    atribuições do vínculo antigo precisam ser redistribuídas.
    """
    inscricao = inscricoes_de(cenario, 1, primeiro=1120)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="antes")
    antiga = Atribuicao.objects.get(inscricao=inscricao)

    novo_vinculo = readicionar(gestor, cenario, "joao", chave="c")

    antiga.refresh_from_db()
    # A linha permanece — é registro do que foi distribuído —, e não pertence ao vínculo novo.
    assert antiga.membro_id != novo_vinculo.id
    assert not Atribuicao.objects.filter(membro=novo_vinculo, ativo=True).exists()
