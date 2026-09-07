"""O candidato vê o próprio Resultado da Etapa — e é isto que fecha o E2E17-004.

A auditoria registrou a lacuna em uma frase: publicada a classificação, a candidata eliminada na
Etapa 1 **não via absolutamente nada** — nem que houve resultado, nem por que saiu. Ela não tem
linha em `SituacaoDivulgada`, porque essa tabela só existe para quem estava no universo do ato.

O fato que autoriza mostrar não é a participação: é a **enumeração normativa** do marco. Havendo
publicação vigente de um marco do Perfil, e enumerando esse marco a Etapa N, o titular vê o seu
Resultado vigente da Etapa N — consequência, motivo e, quando a forma o tiver, pontuação (D-003).

A prova está na ordem inversa, e é o primeiro teste: **antes de publicar, nada aparece**. Sem ele,
"aparece depois" não distinguiria a feature de uma tela que sempre mostrou alguma coisa (FR-056).
"""

import re
from decimal import Decimal

import pytest
from django.urls import reverse

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.divulgacao import (
    emitir,
    entrar_como_titular,
    montar_marco,
    pontuar,
    publicar_o_ato,
)
from tests.fixtures.recursos import deferir_corrigindo

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    """Duas com nota e uma eliminada por Ocorrência — e a eliminação vem **antes** da emissão.

    A ordem não é detalhe: registrar a Ocorrência depois de emitir o ato acrescenta um Resultado ao
    universo, `comparar()` emite `resultados_alterados`, o ato fica obsoleto e a publicação é
    recusada. A cascata da 015/017 funcionando é o que obriga esta fixture a montar o cenário na
    ordem em que a instituição de fato o vive.
    """
    cenario = montar_marco(
        gestor, api_client, manager_headers, process_payload, seed=80, codigo="0780"
    )
    cenario["inscricoes"] = pontuar(
        cenario, gestor, ["90.0000", "70.0000", None], primeiro=801, sufixo="80"
    )
    registrar_ocorrencia(
        actor=gestor,
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[cenario["inscricoes"][2].id],
        motivo="não compareceu à prova didática",
        idempotency_key="ocorrencia-018-us1",
        correlation_id="ocorrencia-018-us1",
    )
    cenario["ato"] = emitir(cenario, gestor, chave="emitir-018-us1")
    return cenario


def abrir(client, inscricao):
    entrar_como_titular(client, inscricao)
    resposta = client.get(reverse("portal:acompanhamento", args=[inscricao.id]))
    corpo = resposta.content.decode()
    return re.search(r"<main[^>]*>(.*)</main>", corpo, re.DOTALL).group(1)


def test_sem_publicacao_o_resultado_da_etapa_nao_aparece(client, cenario):
    """O ato **está emitido** e os Resultados existem — e mesmo assim a tela não os antecipa.

    É a FR-056 dita para o dado individual: existir `ResultadoEtapa` no banco não torna a
    informação visível. Quem abre a porta é a publicação, e ela ainda não aconteceu.
    """
    conteudo = abrir(client, cenario["inscricoes"][0])

    assert "Resultado das etapas" not in conteudo
    assert "Habilitada" not in conteudo


def test_publicado_o_marco_a_eliminada_ve_o_proprio_resultado(client, cenario, gestor):
    """A candidata **sem posição no ato** passa a ver a própria eliminação, com o motivo.

    É o fecho do E2E17-004: ela pertence ao Perfil, o marco do Perfil foi publicado, o marco
    enumera a Etapa — e é isso que autoriza, sem que ela tenha recebido posição alguma. O motivo
    é obrigatório por constraint desde a 013, e até esta feature ninguém o lia.

    **Desfecho sem grandeza**: a Ocorrência não pontua, e a tela não inventa um zero.
    """
    eliminada = cenario["inscricoes"][2]
    publicar_o_ato(cenario, chave="publicar-018-us1")

    conteudo = abrir(client, eliminada)

    assert "Resultado das etapas" in conteudo
    assert "Eliminada" in conteudo
    assert "não compareceu" in conteudo
    assert "pontuação" not in conteudo


def test_a_classificada_ve_a_propria_pontuacao(client, cenario):
    publicar_o_ato(cenario, chave="publicar-018-us1b")

    conteudo = abrir(client, cenario["inscricoes"][0])

    assert "Habilitada" in conteudo
    assert "90" in conteudo


def test_etapa_que_nenhum_marco_publicado_enumera_nao_aparece(client, cenario):
    """A autorização é por Etapa enumerada, e não por Edital.

    O cenário tem duas Etapas e o marco enumera uma. A outra tem Resultado no banco — e continua
    invisível, porque nenhum ato administrativo autorizou mostrá-la.
    """
    publicar_o_ato(cenario, chave="publicar-018-us1c")
    enumerada = cenario["etapa"]

    conteudo = abrir(client, cenario["inscricoes"][0])
    fora = ResultadoEtapa.objects.filter(inscricao=cenario["inscricoes"][0]).exclude(
        etapa_id=enumerada
    )

    assert conteudo.count("resultado-da-etapa") == 1
    assert not fora.exists() or "resultado-da-etapa" in conteudo


def test_a_correcao_por_recurso_e_explicada(client, cenario, gestor):
    """Mostrar a nota nova sem dizer por que ela mudou transformaria a correção em erro aparente."""
    eliminada = cenario["inscricoes"][2]
    publicar_o_ato(cenario, chave="publicar-018-us1d")
    superado = ResultadoEtapa.objects.get(inscricao=eliminada, etapa_id=cenario["etapa"])
    versao = VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("valid_from")
    deferir_corrigindo(
        superado,
        versao=versao,
        pontuacao=Decimal("80.0000"),
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        protocolo="REC-2026-US10001",
    )

    conteudo = abrir(client, eliminada)

    assert "Habilitada" in conteudo
    assert "Resultado corrigido" in conteudo
    assert "julgamento do seu recurso" in conteudo


def test_o_vigente_e_o_que_aparece_e_nao_o_superado(client, cenario, gestor):
    eliminada = cenario["inscricoes"][2]
    publicar_o_ato(cenario, chave="publicar-018-us1e")
    superado = ResultadoEtapa.objects.get(inscricao=eliminada, etapa_id=cenario["etapa"])
    versao = VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("valid_from")
    deferir_corrigindo(
        superado,
        versao=versao,
        pontuacao=Decimal("80.0000"),
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        protocolo="REC-2026-US10002",
    )

    conteudo = abrir(client, eliminada)

    assert "Eliminada" not in conteudo
    assert conteudo.count("resultado-da-etapa") == 1


# ── A fronteira ───────────────────────────────────────────────────────────────────────────────


def test_nada_de_terceiro_atravessa(client, cenario, gestor):
    """Nem nome, nem nota alheia, nem parecer, nem avaliador — nem por engano de template."""
    eliminada = cenario["inscricoes"][2]
    publicar_o_ato(cenario, chave="publicar-018-us1f")
    outras = [item for item in cenario["inscricoes"] if item.id != eliminada.id]

    conteudo = abrir(client, eliminada)

    for outra in outras:
        assert outra.nome not in conteudo
        assert str(outra.id) not in conteudo
        assert (outra.protocolo or "—") not in conteudo
    assert "parecer" not in conteudo.lower()
    assert "joao" not in conteudo


def test_identificador_de_outra_inscricao_devolve_404(client, cenario):
    """A titularidade é a porta, e a resposta é a mesma 404 uniforme de sempre.

    404 e não 403: dizer "existe, mas não é seu" já entrega que existe.
    """
    publicar_o_ato(cenario, chave="publicar-018-us1g")
    eliminada, outra = cenario["inscricoes"][2], cenario["inscricoes"][0]
    entrar_como_titular(client, eliminada)

    resposta = client.get(reverse("portal:acompanhamento", args=[outra.id]))

    assert resposta.status_code == 404


def test_sem_sessao_o_acompanhamento_nao_entrega_resultado(client, cenario, gestor):
    eliminada = cenario["inscricoes"][2]
    publicar_o_ato(cenario, chave="publicar-018-us1h")

    resposta = client.get(reverse("portal:acompanhamento", args=[eliminada.id]))

    assert resposta.status_code in (302, 404)
    if resposta.status_code == 302:
        assert "Eliminada" not in resposta.content.decode()
