"""T057 — o impedimento tira o acesso, inclusive o da inscrição que fundamentou Resultado.

**É a prova que justifica a decisão de D-002.** Uma redação anterior preservava a Atribuição da
fonte para proteger a proveniência do Resultado; a cadeia de autorização, porém, não pergunta por
impedimento — ela depende de ele ter inativado a Atribuição. Aquele desenho deixaria a pessoa
recém-declarada impedida abrindo a inscrição e os documentos dela, e é este arquivo que passaria a
falhar se alguém o reintroduzisse.
"""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application.impedimento import registrar_impedimento
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.authorization, pytest.mark.django_db]


@pytest.fixture
def impedido_depois(gestor, api_client, manager_headers):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1440, codigo="1440"
    )
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-1440")
    concluir_como(cenario, "joao", inscricao, pontuacao="75")
    consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["primeira"],
        inscricao_ids=[inscricao.id],
        idempotency_key="k-1440",
        correlation_id="teste",
    )
    registrar_impedimento(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        identity_subject="joao",
        inscricao_id=inscricao.id,
        motivo="Parentesco descoberto depois da consolidação.",
        idempotency_key="i-1440",
        correlation_id="teste",
    )
    cenario["inscricao"] = inscricao
    return cenario


def test_a_pessoa_impedida_nao_alcanca_a_inscricao_que_fundamentou_o_resultado(
    client, seletor_ligado, impedido_depois
):
    identificar(client, "joao", [])
    url = reverse(
        "interface:mesa-inscricao",
        args=[
            impedido_depois["edital"].id,
            impedido_depois["primeira"],
            impedido_depois["inscricao"].id,
        ],
    )
    assert client.get(url).status_code == 404


def test_a_mesa_da_pessoa_impedida_fica_vazia(client, seletor_ligado, impedido_depois):
    identificar(client, "joao", [])
    url = reverse(
        "interface:minha-etapa",
        args=[impedido_depois["edital"].id, impedido_depois["primeira"]],
    )
    resposta = client.get(url)
    assert resposta.status_code == 200
    assert impedido_depois["inscricao"].protocolo not in resposta.content.decode()


def test_o_resultado_permanece_e_a_consulta_declara_a_contestacao(
    client, seletor_ligado, impedido_depois
):
    """O Resultado é histórico: o impedimento o contesta, e não o apaga."""
    identificar(client, "maria", ["gestor"])
    resposta = client.get(
        reverse(
            "interface:resultados-da-etapa",
            args=[impedido_depois["edital"].id, impedido_depois["primeira"]],
        )
    )
    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "Origem contestada depois da consolidação" in corpo
    assert ResultadoEtapa.objects.filter(inscricao=impedido_depois["inscricao"]).count() == 1
