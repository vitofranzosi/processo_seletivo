"""Duas linhas de informação que não se confundem (FR-076, FR-077).

A tela responde "o que já aconteceu e o que vem agora?". O risco dela é específico e a spec o
nomeia: afirmar que **algo aconteceu com a pessoa** porque o Cronograma institucional chegou a uma
data. Uma etapa encerrada é fato sobre a etapa; a participação de alguém nela é outra coisa, e
nenhuma feature entregue até aqui a produz.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def enviada(inscricao_de_maria):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao_de_maria, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "d.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-acompanhamento",
    )


def abrir(client, inscricao):
    identificar(client, MARIA)
    return client.get(reverse("portal:acompanhamento", args=[inscricao.id])).content.decode()


def test_os_dois_blocos_existem_e_sao_distintos(client, enviada):
    corpo = abrir(client, enviada)

    assert "Sua participação" in corpo
    assert "Cronograma do processo" in corpo
    assert corpo.index("Sua participação") < corpo.index("Cronograma do processo")
    assert 'class="linha-do-tempo pessoal"' in corpo
    assert 'class="linha-do-tempo processo"' in corpo


def test_a_participacao_traz_o_envio_com_instante(client, enviada):
    corpo = abrir(client, enviada)

    assert "Inscrição enviada" in corpo
    assert enviada.submitted_at.astimezone().strftime("%d/%m/%Y") in corpo


def test_a_participacao_nao_inventa_fato_algum(client, enviada):
    """Só o que aconteceu. Nada de resultado, deferimento ou convocação — não existem ainda."""
    corpo = abrir(client, enviada)
    bloco = corpo[corpo.index("Sua participação") : corpo.index("Cronograma do processo")]

    for inventado in ("análise", "resultado", "classificação", "deferida", "aprovad"):
        assert inventado not in bloco.lower(), inventado


def test_o_cronograma_traz_os_eventos_publicados(client, enviada, selecao):
    from processo_seletivo.publicacoes.application import selectors

    conteudo = selectors.selecao_publica(edital_id=selecao.id).content
    nomes = [
        evento.get("description") or evento.get("type") for evento in conteudo.get("schedule") or []
    ]

    corpo = abrir(client, enviada)

    assert nomes, "o teste pressupõe cronograma publicado"
    for nome in nomes:
        assert nome in corpo, nome


def test_a_situacao_do_evento_nao_fala_da_pessoa(client, enviada, selecao):
    """O período de inscrições está aberto: o evento aparece em curso, e nada é dito sobre Maria."""
    corpo = abrir(client, enviada)
    bloco = corpo[corpo.index("Cronograma do processo") :]

    assert 'class="marco em_curso"' in bloco
    assert "sua" not in bloco.lower().replace("sua participação", "")


def test_a_situacao_aparece_por_texto_e_nao_so_por_cor(client, enviada):
    """Cor sozinha não informa quem não a distingue."""
    corpo = abrir(client, enviada)
    assert "✓" in corpo, "o concluído tem marca própria, além da cor"


def test_rascunho_nao_tem_acompanhamento(client, inscricao_de_maria):
    identificar(client, MARIA)
    resposta = client.get(reverse("portal:acompanhamento", args=[inscricao_de_maria.id]))
    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("portal:inscricao", args=[inscricao_de_maria.id])


def test_o_acompanhamento_de_outro_candidato_responde_404(client, enviada):
    from tests.fixtures.candidato import JOAO

    identificar(client, JOAO)
    resposta = client.get(reverse("portal:acompanhamento", args=[enviada.id]))
    assert resposta.status_code == 404
