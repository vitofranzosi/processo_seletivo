"""O que a 018 **não** faz — e os limites que ela declarou de propósito.

Uma feature se define tanto pelo que entrega quanto pelo que recusa entregar. Os limites abaixo não
são lacunas a preencher depois: cada um foi decidido, e o teste existe para que a próxima pessoa
que olhar para o código não os desfaça achando que eram esquecimento.

```text
terceiro, procurador, representação   não existem: recorre o titular (FR-005)
anexos na peça                        não existem: a fundamentação é o que se junta (FR-007)
divulgação de ResultadoEtapa          não nasce: o Resultado individual não é divulgado (FR-019)
espécie ou estado além dos declarados não existem (FR-050, D-010)
```

E a 018 **não altera agregado existente** (FR-107): conteúdo, autoria e estado de Avaliação,
Atribuição, Impedimento, `AtoDeOrdenacao`, `PosicaoNaOrdem` e `PublicacaoResultado` permanecem como
estavam. O que ela faz é criar linhas novas que citam as antigas.
"""

import inspect
from decimal import Decimal

import pytest

from processo_seletivo.recursos import models as modelos_de_recurso
from processo_seletivo.recursos.application import interpor as comando_de_interpor
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso, Recurso
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    return cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=131, codigo="0831"
    )


# ---------------------------------------------------------------------------
# T118 — os limites declarados
# ---------------------------------------------------------------------------


def test_a_peca_nao_tem_por_onde_receber_terceiro_nem_procurador(peca):
    """Recorre o **titular**, e mais ninguém (FR-005).

    Não é ausência de tela: é ausência de lugar onde a informação caberia. Uma coluna de
    representante, mesmo vazia, seria um convite a preenchê-la — e a autorização do candidato é
    justamente o controle do próprio e-mail e a titularidade da própria Inscrição.
    """
    campos = {campo.name for campo in Recurso._meta.get_fields()}

    assert not campos & {
        "procurador",
        "representante",
        "terceiro",
        "interessado",
        "procuracao",
    }
    assert "interposto_por" in campos

    argumentos = inspect.signature(comando_de_interpor.interpor).parameters
    assert not set(argumentos) & {"procurador", "representante", "em_nome_de"}


def test_a_peca_nao_aceita_anexo(peca):
    """A fundamentação **é** o que se junta (FR-007).

    Anexo traria armazenamento, antivírus, limite de tamanho, retenção e um regime de acesso
    próprio — uma feature inteira dentro de outra. A decisão foi explícita, e este teste a registra.
    """
    campos = {campo.name for campo in Recurso._meta.get_fields()}

    assert not campos & {"anexo", "anexos", "arquivo", "arquivos", "documento", "documentos"}
    assert "fundamentacao" in campos


def test_nenhum_ato_de_divulgacao_de_resultado_individual_nasce(peca):
    """O `ResultadoEtapa` é lido pelo titular, e não divulgado (FR-019).

    Divulgá-lo criaria um ato de publicação por inscrição — e um regime de sucessão paralelo ao da
    017 para um objeto que nunca foi público.
    """
    from processo_seletivo.divulgacao.models import PublicacaoResultado

    antes = PublicacaoResultado.objects.count()

    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="Revisão da pontuação.",
        etapa_id=peca["cenario"]["etapa_do_recurso"],
        pontuacao=Decimal("82.0000"),
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="limites-julgar",
    )

    assert PublicacaoResultado.objects.count() == antes


def test_as_especies_sao_exatamente_as_quatro_declaradas(peca):
    """Nenhuma taxonomia além da declarada (FR-050).

    Quatro espécies, e não cinco: o que a espécie discrimina é o **efeito**, e não o vício. Qual
    providência a decisão determina é fundamentação escrita, e não mais um valor no enum.
    """
    assert {str(item) for item in DecisaoRecurso.Especie} == {
        "INDEFERIDO",
        "CORRECAO_FIXADA",
        "REAVALIACAO_DETERMINADA",
        "PROVIDENCIA_A_JUSANTE",
    }


def test_nao_ha_coluna_de_estado_em_nenhum_dos_tres_agregados(peca):
    """A situação é derivada dos atos que alcançaram a peça (D-010).

    Uma coluna de estado seria estado a manter coerente onde a existência de linha já responde — e
    o primeiro lugar onde ela apareceria é por conveniência de uma tela de listagem.
    """
    proibidas = {"estado", "status", "situacao", "fase", "workflow"}
    for modelo in (
        modelos_de_recurso.Recurso,
        modelos_de_recurso.JuizoDeAdmissibilidade,
        modelos_de_recurso.DecisaoRecurso,
    ):
        campos = {campo.name for campo in modelo._meta.get_fields()}
        assert not campos & proibidas, f"{modelo.__name__} ganhou coluna de estado"


# ---------------------------------------------------------------------------
# T119 — a 018 não altera agregado existente
# ---------------------------------------------------------------------------


def test_nenhum_agregado_existente_e_alterado_pelo_ciclo_do_recurso(peca):
    """Ela cria linhas novas que citam as antigas — e não toca nas antigas (FR-107)."""
    from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao
    from processo_seletivo.classificacao.models import AtoDeOrdenacao, PosicaoNaOrdem
    from processo_seletivo.divulgacao.models import PublicacaoResultado

    antes = _retrato()

    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="Revisão da pontuação.",
        etapa_id=peca["cenario"]["etapa_do_recurso"],
        pontuacao=Decimal("82.0000"),
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="limites-intacto",
    )

    assert _retrato() == antes
    assert Avaliacao.objects.exists() and Atribuicao.objects.exists()
    assert AtoDeOrdenacao.objects.exists() and PosicaoNaOrdem.objects.exists()
    assert PublicacaoResultado.objects.exists()


def _retrato():
    """O conteúdo, a autoria e o estado dos agregados que a 018 lê e não escreve."""
    from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao, Impedimento
    from processo_seletivo.classificacao.models import AtoDeOrdenacao, PosicaoNaOrdem
    from processo_seletivo.divulgacao.models import PublicacaoResultado

    return {
        "avaliacoes": sorted(
            Avaliacao.objects.values_list("id", "estado", "pontuacao", "sentido", "concluida_por")
        ),
        "atribuicoes": sorted(Atribuicao.objects.values_list("id", "ativo", "inativado_por")),
        "impedimentos": sorted(Impedimento.objects.values_list("id", "motivo")),
        "atos": sorted(
            AtoDeOrdenacao.objects.values_list("id", "emitido_por", "motivo_da_sucessao")
        ),
        "posicoes": sorted(PosicaoNaOrdem.objects.values_list("id", "posicao", "motivo")),
        "publicacoes": sorted(
            PublicacaoResultado.objects.values_list("id", "natureza", "conteudo_publico_hash")
        ),
    }


# ---------------------------------------------------------------------------
# T120 — a recusa que deixou de prometer o que não existe
# ---------------------------------------------------------------------------


def test_a_recusa_de_reabertura_nomeia_o_ato_que_existe(peca):
    """Ela mandava procurar uma "anulação" que nunca houve (FR-111).

    Quem recebia a recusa saía atrás de uma tela inexistente. O ato que existe é o recurso — e ele
    não reabre a avaliação: **supera** o Resultado por outro que o sucede, deixando o anterior
    íntegro. A mensagem passa a dizer isso.
    """
    from processo_seletivo.avaliacoes.application.avaliacao import reabrir

    superado = peca["superado"]
    with pytest.raises(DomainError) as recusa:
        reabrir(
            actor=_presidencia(),
            processo_id=peca["cenario"]["edital"].processo_id,
            avaliacao_id=superado.avaliacao_id,
            motivo="Quero corrigir a nota.",
            expected_revision=2,
            idempotency_key="reabrir-limites",
            correlation_id="limites",
        )

    assert recusa.value.code == "avaliacao_fundamenta_resultado"
    assert "anulação" not in recusa.value.detail
    assert "supera" in recusa.value.detail
    assert str(superado.id) in recusa.value.detail


def _presidencia():
    from tests.conftest import ator_institucional

    return ator_institucional("carlos", "comissao:gerir")
