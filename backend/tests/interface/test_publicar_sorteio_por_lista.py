"""A prévia de publicação conhece a lista de concorrência (021, D-015, FR-068).

**O defeito que este arquivo fecha, e por que a suíte anterior não o via.** A `021` ensinou o
domínio a divulgar por lista, e a tela continuou lendo a cadeia sem o eixo: a vigente do marco e a
aferição eram consultadas sem `lista_id`.

Publicada a ampla concorrência, a prévia de um ato de PPI lia a publicação **dela** como
predecessora — o ato aparecia como sucedido, ou a assinatura nascia do predecessor errado —, e as
listas de reserva simplesmente não se publicavam pela interface.

O teste das três listas não pegava isso porque chamava o domínio diretamente, já com `lista_id`.
Este entra pela tela, que é onde o defeito morava.
"""

import pytest
from django.urls import reverse

from processo_seletivo.divulgacao.application.publicar import assinatura_da_previa
from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
from processo_seletivo.divulgacao.domain.conteudo import compor
from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import FonteDeTeste
from processo_seletivo.sorteios.models import Sorteio
from tests.fixtures.sorteio import LISTA_PCD, LISTA_PPI, METODO, certame_com_cotas, presidente
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def sorteadas(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    certame = certame_com_cotas(gestor, api_client, manager_headers, process_payload)
    relacoes = {
        lista: publicar_relacao(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            lista_id=lista,
            idempotency_key=f"tela-relacao-{indice}",
            correlation_id="teste-021",
        )["relacao"]
        for indice, lista in enumerate((None, LISTA_PPI, LISTA_PCD))
    }
    ocorrencia = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key="tela-ocorrencia",
        correlation_id="teste-021",
        fonte_externa=FonteDeTeste(),
    )["ocorrencia"]
    sorteios = {
        lista: Sorteio.objects.get(
            pk=constituir_sorteio(
                actor=presidente(),
                processo_id=certame["processo"].id,
                edital_id=certame["edital"].id,
                relacao_id=relacao,
                ocorrencia_id=ocorrencia,
                idempotency_key=f"tela-sorteio-{indice}",
                correlation_id="teste-021",
            )["sorteio"]
        )
        for indice, (lista, relacao) in enumerate(relacoes.items())
    }
    return certame, sorteios


def _publicar_pela_tela(client, certame, sorteio):
    """Pela tela, e não pelo domínio: é onde o eixo da lista se perdia."""
    identificar(client, "paula.publicadora", ["publicador"])
    previa = client.get(
        reverse(
            "interface:previa-de-publicacao",
            args=[certame["edital"].id, sorteio.marco_id, sorteio.ato_id],
        )
    )
    assert previa.status_code == 200, previa.content
    projecao = compor(sorteio.ato)
    anterior = vigente_do_marco(
        edital=certame["edital"], marco_id=sorteio.marco_id, lista_id=sorteio.lista_id
    )
    return client.post(
        reverse(
            "interface:publicar-resultado",
            args=[certame["edital"].id, sorteio.marco_id, sorteio.ato_id],
        ),
        {
            "natureza": "PRELIMINAR",
            "autoridade": "diretoria-cefor",
            "confirmacao_da_previa": assinatura_da_previa(
                ato=sorteio.ato, publicacao_anterior=anterior, projecao=projecao
            ),
            "chave_idempotencia": f"tela-publicar-{sorteio.id}",
        },
    ), previa.content.decode()


def test_as_tres_listas_se_publicam_pela_tela(client, sorteadas):
    certame, sorteios = sorteadas

    for sorteio in sorteios.values():
        resposta, _corpo = _publicar_pela_tela(client, certame, sorteio)
        assert resposta.status_code in (302, 303), resposta.content

    assert PublicacaoResultado.objects.count() == 3


def test_a_previa_de_uma_lista_nao_le_a_publicacao_de_outra_como_predecessora(client, sorteadas):
    """O sintoma exato: publicada a ampla, a prévia da PPI a via como a sua antecessora."""
    certame, sorteios = sorteadas
    _publicar_pela_tela(client, certame, sorteios[None])

    resposta, corpo = _publicar_pela_tela(client, certame, sorteios[LISTA_PPI])

    assert resposta.status_code in (302, 303), corpo
    publicada = PublicacaoResultado.objects.get(ato=sorteios[LISTA_PPI].ato)
    assert publicada.publicacao_anterior_id is None, "a PPI não sucede a ampla concorrência"
    assert str(publicada.lista_id) == LISTA_PPI


def test_a_previa_da_lista_nao_toma_a_publicacao_de_outra_como_predecessora(client, sorteadas):
    """A asserção é sobre o **predecessor que a prévia calculou**, e não sobre a prosa da página.

    A tela explica, em texto, que um definitivo não é sucedido por um preliminar — e uma varredura
    por substring acusaria essa frase. O que importa é o valor: sem publicação anterior **daquela
    lista**, `sucede` é nulo, e é dele que saem a assinatura da prévia e as naturezas oferecidas.
    """
    certame, sorteios = sorteadas
    _publicar_pela_tela(client, certame, sorteios[None])

    identificar(client, "paula.publicadora", ["publicador"])
    resposta = client.get(
        reverse(
            "interface:previa-de-publicacao",
            args=[
                certame["edital"].id,
                sorteios[LISTA_PCD].marco_id,
                sorteios[LISTA_PCD].ato_id,
            ],
        )
    )

    assert resposta.status_code == 200
    assert resposta.context["sucede"] is None, (
        "a prévia da PcD tomou a publicação de outra lista como predecessora"
    )
    assert resposta.context["publicabilidade"].publicavel is True
