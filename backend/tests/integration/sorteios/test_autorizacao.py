"""O caminho negativo de cada comando, e por que ele responde 404 (021, FR-062, FR-063, R-013).

**Quatro comandos, e a autorização de três deles é a mesma.** Observar a ocorrência, publicar a
relação e constituir o sorteio passam por `comando_de_comissao`, com a presidência **deste**
Processo como base suficiente — nenhum papel novo. O quarto, declarar o método, não está aqui:
ele é conteúdo do Edital, e segue a autorização do ato normativo que o carrega (D-013).

**404, e não 403.** Dizer "existe, mas você não pode" já entregaria que existe: é a defesa contra
IDOR que o Princípio III exige, e é o que o resto do acervo faz.
"""

import pytest

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import anular_sorteio, constituir_sorteio
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import FonteDeTeste
from tests.conftest import ator_institucional
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente

pytestmark = [
    pytest.mark.integration,
    pytest.mark.authorization,
    pytest.mark.django_db(transaction=True),
]


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    return certame_de_sorteio(gestor, api_client, manager_headers, process_payload)


def _sem_nada():
    """Uma identidade real, e sem base alguma sobre este Processo."""
    return ator_institucional("joao.qualquer")


def _de_outro_escopo():
    """A presidência existe, e é de outra unidade: escopo institucional não atravessa."""
    return ator_institucional("maria", escopo="outra-unidade")


@pytest.mark.parametrize("intruso", [_sem_nada, _de_outro_escopo], ids=["sem-base", "outro-escopo"])
def test_publicar_relacao_responde_404_para_quem_nao_alcanca(certame, intruso):
    with pytest.raises(DomainError) as recusa:
        publicar_relacao(
            actor=intruso(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            idempotency_key="autorizacao-relacao",
            correlation_id="teste-021",
        )

    assert recusa.value.status == 404


@pytest.mark.parametrize("intruso", [_sem_nada, _de_outro_escopo], ids=["sem-base", "outro-escopo"])
def test_observar_ocorrencia_responde_404_para_quem_nao_alcanca(certame, intruso):
    with pytest.raises(DomainError) as recusa:
        observar_ocorrencia(
            actor=intruso(),
            processo_id=certame["processo"].id,
            fonte=METODO["source"],
            referencia=METODO["occurrence"],
            idempotency_key="autorizacao-ocorrencia",
            correlation_id="teste-021",
            fonte_externa=FonteDeTeste(),
        )

    assert recusa.value.status == 404


@pytest.mark.parametrize("intruso", [_sem_nada, _de_outro_escopo], ids=["sem-base", "outro-escopo"])
def test_constituir_sorteio_responde_404_para_quem_nao_alcanca(certame, intruso):
    relacao = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="autorizacao-relacao-ok",
        correlation_id="teste-021",
    )["relacao"]
    ocorrencia = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key="autorizacao-ocorrencia-ok",
        correlation_id="teste-021",
        fonte_externa=FonteDeTeste(),
    )["ocorrencia"]

    with pytest.raises(DomainError) as recusa:
        constituir_sorteio(
            actor=intruso(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            relacao_id=relacao,
            ocorrencia_id=ocorrencia,
            idempotency_key="autorizacao-sorteio",
            correlation_id="teste-021",
        )

    assert recusa.value.status == 404


@pytest.mark.parametrize("intruso", [_sem_nada, _de_outro_escopo], ids=["sem-base", "outro-escopo"])
def test_anular_responde_404_para_quem_nao_alcanca(certame, intruso):
    """A anulação é a constituição do sucessor, e a autorização dela é a mesma."""
    with pytest.raises(DomainError) as recusa:
        anular_sorteio(
            actor=intruso(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            sorteio_anterior_id="00000000-0000-4000-8000-0000000000ff",
            relacao_id="00000000-0000-4000-8000-0000000000fe",
            ocorrencia_id="00000000-0000-4000-8000-0000000000fd",
            motivo="Motivo qualquer.",
            idempotency_key="autorizacao-anular",
            correlation_id="teste-021",
        )

    assert recusa.value.status == 404


def test_a_presidencia_deste_processo_e_base_suficiente(certame):
    """Nenhum papel novo: é o que a `013`, a `015` e a `017` já fazem (R-013)."""
    declarado = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="autorizacao-presidencia",
        correlation_id="teste-021",
    )

    assert declarado["relacao"]


class FonteQueRegistraChamada:
    """Uma fonte que anota ter sido chamada — é o que o teste precisa saber."""

    def __init__(self):
        self.chamadas = []

    def observar(self, *, fonte, referencia):
        from django.utils import timezone

        from processo_seletivo.sorteios.infrastructure.fontes import Observacao

        self.chamadas.append((fonte, referencia))
        return Observacao(material_bruto="1 2 3 4 5", ocorrida_nao_antes_de=timezone.now())


@pytest.mark.parametrize("intruso", [_sem_nada, _de_outro_escopo], ids=["sem-base", "outro-escopo"])
def test_o_intruso_nao_aciona_a_fonte_externa(certame, intruso):
    """**Autorizar depois de ir à rede não é autorizar** (Princípio III, FR-062).

    A recusa final já existia, e passava: o comando ia à fonte, voltava, e só então perguntava quem
    estava pedindo. Um ator sem base sobre o Processo fazia a instituição bater na fonte externa
    tantas vezes quanto quisesse — e o teste antigo, que só afirmava sobre a exceção, aprovava isso.
    """
    fonte = FonteQueRegistraChamada()

    with pytest.raises(DomainError) as recusa:
        observar_ocorrencia(
            actor=intruso(),
            processo_id=certame["processo"].id,
            fonte=METODO["source"],
            referencia=METODO["occurrence"],
            idempotency_key="intruso-nao-chama",
            correlation_id="teste-021",
            fonte_externa=fonte,
        )

    assert recusa.value.status == 404
    assert fonte.chamadas == [], "a fonte externa foi consultada por quem não tem base"


@pytest.mark.parametrize("intruso", [_sem_nada, _de_outro_escopo], ids=["sem-base", "outro-escopo"])
def test_o_intruso_nao_le_uma_ocorrencia_ja_registrada(certame, intruso):
    """O caminho em cache passava **inteiramente por fora** da autorização.

    A ocorrência já registrada era devolvida antes de qualquer verificação, com o material bruto
    dentro: quem não alcança o Processo lia a semente do certame só perguntando por ela.
    """
    from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import FonteDeTeste

    declarado = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key="cache-legitimo",
        correlation_id="teste-021",
        fonte_externa=FonteDeTeste(),
    )
    assert declarado["materialBruto"], "a leitura legítima devolve o material"

    with pytest.raises(DomainError) as recusa:
        observar_ocorrencia(
            actor=intruso(),
            processo_id=certame["processo"].id,
            fonte=METODO["source"],
            referencia=METODO["occurrence"],
            idempotency_key="cache-intruso",
            correlation_id="teste-021",
            fonte_externa=FonteDeTeste(),
        )

    assert recusa.value.status == 404
