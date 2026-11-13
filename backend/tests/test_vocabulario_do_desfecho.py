"""O vocabulário do ato só dentro do fundamento recolhido (156, FR-6403, SC-2120).

As outras varreduras de vocabulário leem os arquivos-fonte. Esta lê **a tela renderizada**, e é a
única que pode: a frase do ato não está em arquivo nenhum do portal — está no fundamento gravado
(*"…o vencimento informado no ato da convocação decorreu sem desfecho registrado"*), e chega ao
candidato pelo banco. A pergunta é onde ela aparece: dentro do `<details
class="fundamento-do-ato">`, pode; fora dele, a tela voltou a explicar o desfecho em jargão (achado
18 do estudo da jornada final).

**As sete espécies, nas duas telas e nos dois ramos da convocação** — sem documento pedido, e com
documento (a chamada da `121`). Cada espécie é um desfecho que sucede o anterior na mesma chamada,
montado por ORM a partir de um aceite real, como faz `test_as_sete_especies_fecham_a_escrita_igual`
da `029`: registrar sete desfechos pelo comando exigiria sete chamadas e sete apurações, e provaria
de novo a `019`, que já tem os seus testes. O fundamento de cada um é o mais técnico que existe — o
derivado do não atendimento em lote —, para que a varredura tenha o que achar.

**E as três espécies de convocação** (FR-6442; FR-3740 da `118`, revista pela `156` em 13/11): o
fundamento da convocação — o que diz *"na faixa vigente deste recorte"* — também só aparece
recolhido, sob a frase que diz por que a pessoa foi chamada. A vaga inicial é a da própria chamada
do cenário; a vaga que vagou e a de regularizar são chamadas seguintes da mesma pessoa, montadas por
ORM pelo mesmo motivo, com o fundamento derivado da `050`.
"""

import html
import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.convocacao.domain import fundamento as fundamento_derivado
from processo_seletivo.convocacao.domain import nomes

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

#: Os termos da FR-6403, que só podem estar dentro do fundamento recolhido.
DO_ATO = (
    "faixa vigente",
    "recorte",
    "apuração",
    "decorreu",
    "desfecho registrado",
    "vencimento informado no ato",
    "espécie",
)

RECOLHIDO = re.compile(r'<details class="fundamento-do-ato">.*?</details>', re.S)
#: O mais técnico dos fundamentos que um desfecho grava: o derivado do não atendimento em lote.
FUNDAMENTO = fundamento_derivado.do_nao_atendimento(
    edital="Edital 01/2026", recorte="Perfil 1, ampla concorrência"
)


@pytest.fixture
def fx(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    from tests.fixtures import jornada_do_convocado as jornada

    return jornada.Montagem(gestor, api_client, manager_headers, process_payload)


def entrar_como(client, inscricao):
    from processo_seletivo.identidade.models import CandidateIdentity
    from processo_seletivo.portal.identidade import CHAVE_SESSAO

    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=inscricao.identity_subject, defaults={"created_at": timezone.now()}
    )
    sessao = client.session
    sessao[CHAVE_SESSAO] = str(registro.pk)
    sessao.save()


def sem_documento(fx):
    """A chamada sem documento pedido, com o aceite registrado pelo comando."""
    from tests.fixtures import documentos_da_convocacao as cenarios
    from tests.fixtures import jornada_do_convocado as jornada

    certame = jornada.certame(fx, prefixo="vocabulario-156")
    pessoa, convocacao = jornada.convocar(certame, fx.gestor, letra="v156")
    cenarios.desfechar(certame[0], fx.gestor, convocacao, nomes.ACEITE, chave="v156-aceite")
    return pessoa, convocacao


def com_documento(fx):
    """A chamada com documento pedido (I1 da `118`): o aceite depois de tudo conferido."""
    from tests.fixtures import jornada_do_convocado as jornada

    cenario = jornada.montar("I1", fx)
    return cenario.pessoa, cenario.convocacao


def suceder(convocacao, pessoa, especie):
    """O desfecho da espécie, sucedendo o vigente da chamada — por ORM, como na `029`."""
    from processo_seletivo.convocacao.application.selectors import desfecho_de
    from processo_seletivo.convocacao.models import AtestadoDeFatoExterno, DesfechoDaConvocacao
    from processo_seletivo.resultados.models import ResultadoEtapa

    anterior = desfecho_de(convocacao)
    agora = timezone.now()
    atestado = None
    if especie == nomes.INERCIA:
        atestado = AtestadoDeFatoExterno.objects.create(
            inscricao=pessoa,
            especie=nomes.ATESTADO_AUSENCIA_NA_PRIMEIRA_SEMANA,
            conclusao="Ausente em toda a primeira semana letiva.",
            referencia_do_prazo="Item 8.4 do Edital.",
            atestado_por="teste",
            atestado_em=agora,
        )
    return DesfechoDaConvocacao.objects.create(
        convocacao=convocacao,
        especie=especie,
        fundamento=FUNDAMENTO,
        efeito=anterior.efeito,
        resultado_sucessor=(
            ResultadoEtapa.objects.filter(inscricao=pessoa).first()
            if especie == nomes.REGULARIZACAO
            else None
        ),
        atestado=atestado,
        desfecho_anterior=anterior,
        motivo_da_sucessao="Cenário da varredura de vocabulário.",
        registrado_por="teste",
        registrado_em=agora,
    )


def fora_do_recolhido(client, rota, pessoa):
    resposta = client.get(reverse(rota, args=[pessoa.id]))
    assert resposta.status_code == 200
    principal = re.search(r"<main[^>]*>(.*)</main>", resposta.content.decode(), re.S).group(1)
    recolhidos = RECOLHIDO.findall(principal)
    principal = RECOLHIDO.sub(" ", principal)
    texto = " ".join(re.sub(r"<[^>]+>", " ", principal).split())
    return html.unescape(texto), recolhidos


@pytest.mark.parametrize("montar", [sem_documento, com_documento], ids=["sem-doc", "com-doc"])
def test_o_vocabulario_do_ato_so_aparece_recolhido(client, fx, montar):
    pessoa, convocacao = montar(fx)
    entrar_como(client, pessoa)
    achados = []
    for especie in nomes.ESPECIES_DE_DESFECHO:
        if especie != nomes.ACEITE:
            suceder(convocacao, pessoa, especie)
        for rota in ("portal:convocacao", "portal:acompanhamento"):
            texto, recolhidos = fora_do_recolhido(client, rota, pessoa)
            achados += [
                f"{especie} em {rota}: {termo!r}" for termo in DO_ATO if termo in texto.lower()
            ]
            # A ausência não basta: o fundamento continua na tela, recolhido (FR-6401).
            if especie != nomes.ACEITE:
                assert any("decorreu sem desfecho registrado" in r for r in recolhidos), (
                    especie,
                    rota,
                )
            assert "Fundamento do registro" in " ".join(recolhidos), (especie, rota)
        texto, recolhidos = fora_do_recolhido(client, "portal:convocacao", pessoa)
        assert "Você foi chamado para uma das vagas" in texto, especie
        assert any("Fundamento da convocação" in r for r in recolhidos), especie
    for numero, especie in enumerate((nomes.SUPLENCIA, nomes.PARA_REGULARIZAR), start=2):
        chamada_seguinte(convocacao, especie, numero)
        texto, recolhidos = fora_do_recolhido(client, "portal:convocacao", pessoa)
        achados += [f"{especie}: {termo!r}" for termo in DO_ATO if termo in texto.lower()]
        assert "Você foi chamado" in texto, especie
        assert any("Fundamento da convocação" in r and "apuração" in r for r in recolhidos), especie
    assert achados == []


def chamada_seguinte(modelo, especie, numero):
    """Uma chamada seguinte da mesma pessoa, da espécie dada, sem desfecho — por ORM, como na `029`.

    Mais recente que a anterior, para ser a que o portal mostra; o fundamento é o derivado da
    `050`, com a apuração e a faixa de que a frase do ato fala.
    """
    from processo_seletivo.convocacao.models import Convocacao

    return Convocacao.objects.create(
        edital=modelo.edital,
        perfil_id=modelo.perfil_id,
        marco_id=modelo.marco_id,
        lista_id=modelo.lista_id,
        inscricao=modelo.inscricao,
        especie=especie,
        fundamento=fundamento_derivado.da_convocacao(
            especie=especie,
            edital="Edital 01/2026",
            recorte="Perfil 1, ampla concorrência",
            data_da_apuracao="10/11/2026",
        ),
        apuracao=modelo.apuracao,
        ato_de_ordenacao_id=modelo.ato_de_ordenacao_id,
        corte_id=modelo.corte_id,
        versao=modelo.versao,
        chamada=numero,
        criado_por="teste",
        criado_em=timezone.now() + timedelta(seconds=numero),
    )
