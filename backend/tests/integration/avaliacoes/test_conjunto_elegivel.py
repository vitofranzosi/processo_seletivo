"""A proteção do conjunto elegível — e a sequência que FR-092 existe para impedir.

Sem esta recusa, a sequência abaixo seria possível e indistinguível de trabalho normal:

```text
dois avaliadores concluem
        ↓
a presidência não gosta de uma das notas
        ↓
remove aquela Atribuição
        ↓
a avaliação deixa de ser elegível
        ↓
distribui a inscrição a um terceiro
```

Isto é escolher qual avaliação conta no resultado, com a aparência de organizar o trabalho. **Se
este arquivo passar a falhar, a feature virou um mecanismo de seleção de notas.**
"""

import pytest

from processo_seletivo.avaliacoes.application.distribuicao import remover_atribuicao
from processo_seletivo.avaliacoes.application.impedimento import registrar_impedimento
from processo_seletivo.avaliacoes.application.selectors import avaliacoes_elegiveis
from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao
from tests.fixtures.mesa import concluir_como, distribuir_para, inscricoes_de, montar_banca

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_banca(gestor, api_client, manager_headers, seed=9, codigo="91")


@pytest.fixture
def avaliada(cenario, gestor):
    """Uma inscrição com **duas** avaliações concluídas — o caso da dupla avaliação."""
    inscricao = inscricoes_de(cenario, 1, primeiro=900)[0]
    distribuir_para(cenario, gestor, ["joao", "ana"], [inscricao])
    concluir_como(cenario, "joao", inscricao, pontuacao="95", parecer="Excelente")
    concluir_como(cenario, "ana", inscricao, pontuacao="60", parecer="Insuficiente")
    return inscricao


def test_a_sequencia_que_fr_092_impede(cenario, gestor, avaliada):
    """A presidência não gosta da nota 60 e tenta remover a atribuição da Ana. É recusada."""
    da_ana = Atribuicao.objects.get(inscricao=avaliada, membro__identity_subject="ana")

    resultado = remover_atribuicao(
        actor=gestor,
        processo_id=cenario["processo"].id,
        atribuicao_ids=[da_ana.id],
        idempotency_key="trocar-a-nota",
        correlation_id="teste",
    )

    assert resultado["feitas"] == 0
    assert resultado["recusadas"] == 1
    da_ana.refresh_from_db()
    assert da_ana.ativo
    assert len(avaliacoes_elegiveis(edital=cenario["edital"], etapa_id=cenario["etapa"])) == 2


def test_a_recusa_nomeia_os_atos_que_teriam_esse_efeito(cenario, gestor, avaliada):
    """Recusar sem dizer o caminho empurraria a presidência para fora do sistema.

    Invalidar uma avaliação concluída é legítimo quando há motivo — o que não pode existir é o
    efeito sem o ato.
    """
    da_ana = Atribuicao.objects.get(inscricao=avaliada, membro__identity_subject="ana")

    resultado = remover_atribuicao(
        actor=gestor,
        processo_id=cenario["processo"].id,
        atribuicao_ids=[da_ana.id],
        idempotency_key="nomeia",
        correlation_id="teste",
    )

    motivo = resultado["motivos"][0]["motivo"]
    assert "impedimento" in motivo.lower()
    assert "reabra" in motivo.lower() or "reabertura" in motivo.lower()
    assert "motivo" in motivo.lower()


def test_a_via_comum_alcanca_a_atribuicao_pendente(cenario, gestor):
    """A recusa é sobre a **concluída**, e não sobre redistribuir — que continua barato."""
    inscricao = inscricoes_de(cenario, 1, primeiro=910)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="pendente")
    pendente = Atribuicao.objects.get(inscricao=inscricao)

    resultado = remover_atribuicao(
        actor=gestor,
        processo_id=cenario["processo"].id,
        atribuicao_ids=[pendente.id],
        idempotency_key="remover-pendente",
        correlation_id="teste",
    )

    assert resultado["feitas"] == 1


def test_o_lote_misto_remove_a_pendente_e_recusa_a_concluida(cenario, gestor, avaliada):
    """Regra sobre a linha: a concluída é nomeada, e o restante segue (FR-085)."""
    outra = inscricoes_de(cenario, 1, primeiro=920)[0]
    distribuir_para(cenario, gestor, ["joao"], [outra], chave="mista")
    pendente = Atribuicao.objects.get(inscricao=outra)
    concluida = Atribuicao.objects.get(inscricao=avaliada, membro__identity_subject="joao")

    resultado = remover_atribuicao(
        actor=gestor,
        processo_id=cenario["processo"].id,
        atribuicao_ids=[pendente.id, concluida.id],
        idempotency_key="lote-misto",
        correlation_id="teste",
    )

    assert resultado["feitas"] == 1
    assert resultado["recusadas"] == 1


def test_o_conjunto_elegivel_e_exatamente_o_que_a_013_herda(cenario, gestor, avaliada):
    """Concluídas, sob Atribuição ativa — e nada além (contrato §6)."""
    elegiveis = list(avaliacoes_elegiveis(edital=cenario["edital"], etapa_id=cenario["etapa"]))

    assert len(elegiveis) == 2
    assert {a.identity_subject for a in elegiveis} == {"joao", "ana"}
    for avaliacao in elegiveis:
        assert avaliacao.estado == Avaliacao.Estado.CONCLUIDA
        assert avaliacao.atribuicao.ativo
        # Autoria, instante e a versão que governou o ato — o que a 013 precisa para confiar.
        assert avaliacao.concluida_por
        assert avaliacao.concluida_em is not None
        assert avaliacao.versao_id is not None


def test_o_rascunho_nao_entra_no_conjunto(cenario, gestor):
    """Salvar não é concluir, e a 013 consome conclusões."""
    inscricao = inscricoes_de(cenario, 1, primeiro=930)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="rascunho")
    Avaliacao.objects.create(
        atribuicao=Atribuicao.objects.get(inscricao=inscricao),
        identity_subject="joao",
        etapa_id=cenario["etapa"],
        inscricao_id=inscricao.id,
    )

    elegiveis = avaliacoes_elegiveis(
        edital=cenario["edital"], etapa_id=cenario["etapa"], inscricao_id=inscricao.id
    )

    assert list(elegiveis) == []


def test_o_ato_nomeado_tira_do_conjunto_e_a_avaliacao_permanece(cenario, gestor, avaliada):
    """O caminho legítimo: com motivo, com autoria, e sem apagar nada (FR-079, FR-092)."""
    registrar_impedimento(
        actor=gestor,
        processo_id=cenario["processo"].id,
        identity_subject="ana",
        inscricao_id=avaliada.id,
        motivo="Conflito de interesse declarado após a avaliação.",
        idempotency_key="ato-nomeado",
        correlation_id="teste",
    )

    elegiveis = list(avaliacoes_elegiveis(edital=cenario["edital"], etapa_id=cenario["etapa"]))
    da_ana = Avaliacao.objects.get(inscricao_id=avaliada.id, identity_subject="ana")

    assert [a.identity_subject for a in elegiveis] == ["joao"]
    assert da_ana.estado == Avaliacao.Estado.CONCLUIDA
    assert str(da_ana.pontuacao) == "60.0000"
