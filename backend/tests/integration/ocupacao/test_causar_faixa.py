"""O déficit apurado causa a faixa seguinte pela `014` (016, `FR-255`, `FR-256`).

**O que estes testes fecham é o ciclo do 77/2026**: faixa emitida, documentação recusada, déficit
apurado, faixa seguinte emitida com o déficit **como causa** — e não com motivo digitado à mão.

A `D-003` da `014` previu exatamente isto: *"quando a `016` existir, ela passa a ser a origem do
motivo, sem que o ato mude de forma"*. O que muda é de onde o motivo vem.
"""

import pytest

from processo_seletivo.classificacao.models import Corte
from processo_seletivo.ocupacao.application.causar_faixa import causar_faixa_seguinte
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.corte import MARCO, regra
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao import montar_cenario_da_ocupacao
from tests.integration.ocupacao.test_emissao import apurar

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def com_continuacao(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """O cenário do 77/2026 reduzido: alvo 2, quadro de 3, e continuação **admitida**.

    O quadro maior que o alvo é o ponto: a faixa alcança 2, ninguém habilita na Etapa governada, e
    sobram 3 vagas a ocupar — que é o déficit que causa a faixa seguinte.
    """
    return montar_cenario_da_ocupacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ocupacao-016-faixa",
        geral=3,
        cut=regra(continuation="ALLOWED"),
    )


def causar(edital, gestor, *, chave="faixa-016"):
    return causar_faixa_seguinte(
        actor=gestor,
        processo_id=edital.processo_id,
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key=chave,
        correlation_id="teste-ocupacao-016",
    )


def test_o_ato_guarda_o_deficit_apurado_como_causa(com_continuacao, gestor):
    """**O motivo é escrito pelo déficit, e não digitado** (`FR-255`).

    A frase cita a apuração pela identidade, para que a auditoria chegue nela sem abrir o banco.
    """
    edital, _, _ = com_continuacao
    apurado = apurar(edital, gestor)
    assert apurado["faltando"] == 3

    causar(edital, gestor)

    continuacao = Corte.objects.exclude(faixa_anterior=None).get()
    assert "Déficit apurado de 3 vaga(s)" in continuacao.motivo
    assert "3 efetivas com 0 ocupadas" in continuacao.motivo
    assert str(apurado["id"]) in continuacao.motivo


def test_sem_apuracao_a_faixa_seguinte_e_recusada(com_continuacao, gestor):
    """Pedir a faixa sobre número que ninguém apurou é pedi-la sem fundamento."""
    edital, _, _ = com_continuacao

    with pytest.raises(DomainError) as erro:
        causar(edital, gestor)

    assert erro.value.code == nomes.NAO_APURADO


def test_com_deficit_zero_a_faixa_seguinte_e_recusada(com_continuacao, gestor):
    """**`FR-256`**: não há o que preencher, e a recusa o diz com essas palavras."""
    edital, _, _ = com_continuacao
    # Um quadro de 3 com 3 ocupadas não existe neste cenário; o caminho curto é apurar sobre um
    # recorte cujo quadro é zero — a linha zerada é declaração legítima do Edital.
    from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao

    apurar(edital, gestor)
    vigente = ApuracaoDeOcupacao.objects.get()
    ApuracaoDeOcupacao.objects.create(
        edital=edital,
        perfil_id=vigente.perfil_id,
        marco_id=vigente.marco_id,
        lista_id=None,
        ato=vigente.ato,
        corte=vigente.corte,
        versao=vigente.versao,
        apuracao_anterior=vigente,
        motivo_da_sucessao="Todas as vagas ocupadas",
        publicadas=3,
        efetivas=3,
        ocupadas=3,
        linha_do_quadro_id=vigente.linha_do_quadro_id,
        universo=vigente.universo,
        emitida_por="teste",
        emitida_em=vigente.emitida_em,
    )

    with pytest.raises(DomainError) as erro:
        causar(edital, gestor, chave="faixa-016-zero")

    assert erro.value.code == nomes.DEFICIT_ZERO


def test_sobre_apuracao_obsoleta_a_faixa_seguinte_e_recusada(com_continuacao, gestor):
    """**A apuração obsoleta não causa faixa** (`FR-263`), e a recusa nomeia as causas.

    É a mesma disciplina que a `014` aplica ao corte obsoleto: não se constrói sobre número que o
    próprio sistema já sabe estar para trás.
    """
    from django.utils import timezone

    from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao, MovimentoDeVaga

    edital, _, _ = com_continuacao
    apurar(edital, gestor)
    vigente = ApuracaoDeOcupacao.objects.get()
    MovimentoDeVaga.objects.create(
        apuracao=vigente,
        especie=nomes.MOVIMENTO_REVERSAO,
        origem_lista_id="00000000-0000-4000-8000-000000000473",
        destino_lista_id=None,
        quantidade=1,
        causa="Movimento que torna a apuração obsoleta",
        registrado_por="teste",
        registrado_em=timezone.now(),
    )

    with pytest.raises(DomainError) as erro:
        causar(edital, gestor, chave="faixa-016-obsoleta")

    assert erro.value.code == nomes.APURACAO_OBSOLETA
    assert "movimento de vaga alcançou" in erro.value.detail


def test_a_faixa_seguinte_nao_revoga_a_anterior(com_continuacao, gestor):
    """Continuação **acrescenta**; sucessão substitui. Trocar os dois eixos é o defeito da `014`."""
    edital, _, _ = com_continuacao
    apurar(edital, gestor)
    raiz = Corte.objects.get()

    causar(edital, gestor)

    assert Corte.objects.count() == 2
    continuacao = Corte.objects.exclude(id=raiz.id).get()
    assert continuacao.faixa_anterior_id == raiz.id
    assert continuacao.corte_anterior_id is None, "continuação não sucede: acrescenta"
