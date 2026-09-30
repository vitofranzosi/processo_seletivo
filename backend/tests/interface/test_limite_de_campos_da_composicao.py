"""O maior Edital previsto cabe num envio só.

O achado é `doc/achado-etapa-perfis-recusa-acima-de-mil-campos.md`, e a decisão, a DP-21.

A composição grava a coleção inteira num POST (`replace_draft`), e o Django recusa, antes da view,
o envio com mais de `DATA_UPLOAD_MAX_NUMBER_FIELDS` campos. Com o padrão de mil, o 27º Perfil de
duas Modalidades já não gravava — um teto que nenhuma spec declara e que a Constituição proíbe: o
assistente organiza a experiência e *não pode limitar o domínio*.

**O limite subiu, e o que impede o teto de voltar é este arquivo.** Ele compõe o maior Edital que se
prevê — o multicampi da `051` — e lê o formulário como a tela o devolve, e não como o teste o
imaginaria: Modalidade nova, campo novo no cartão ou coluna nova no marco entram na conta sem que
ninguém se lembre deles. Se o envio passar do limite configurado, reprova aqui, e não na mão de quem
compõe o primeiro Edital grande.

**Os três envios mais pesados da gestão**: a etapa Perfis, a Classificação e a Retificação, que
envia o Edital publicado inteiro e é, das três, a maior (DP-21, "medir a Retificação").

E, para quando o limite ainda assim for passado, a recusa que diz o que aconteceu e o que fazer, no
lugar do 400 cru (FR-021 da 002; FR-801 da 048).
"""

import uuid
from datetime import timedelta
from html.parser import HTMLParser
from urllib.parse import urlencode

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.editais.models.perfis import MarcoClassificatorio, PerfilVaga
from processo_seletivo.processos.models import Edital
from tests.fixtures.edital import DRAW_METHOD, actor_headers
from tests.fixtures.publicacao import levar_a_publicacao
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

# **O maior Edital previsto**, e a forma de cada Perfil dele. Os 66 Perfis são os do multicampi que
# a `051` projeta (`spec.md`, *Por que esta feature existe*); as quatro Modalidades são a ampla e
# três listas reservadas; o quadro reparte as vagas por todas; e cada Perfil tem dois marcos —
# preliminar e final — com três critérios de desempate, sobre duas Etapas pontuadas. Mudar estes
# números é mudar o Edital de referência: a conta do comentário de `DATA_UPLOAD_MAX_NUMBER_FIELDS`
# muda junto.
PERFIS = 66
RESERVADAS = [
    ("PP", "Pessoas pretas e pardas", "Lei 15.142/2025", "25.0000"),
    ("IQ", "Pessoas indígenas e quilombolas", "Lei 15.142/2025", "5.0000"),
    ("PCD", "Pessoas com deficiência", "Decreto 9.508/2018", "5.0000"),
]
MARCOS_POR_PERFIL = 2
PROVA = str(uuid.UUID(int=0xE1))
TITULOS = str(uuid.UUID(int=0xE2))


def _id(*partes):
    """Identidade estável e única por Edital — Perfil, Modalidade e marco são únicos globalmente."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "limite-de-campos/" + "/".join(map(str, partes))))


def _marco(perfil, n, fato):
    return {
        "id": _id(perfil, "marco", n),
        "code": f"M{n}",
        "name": "Classificação final" if n == MARCOS_POR_PERFIL else f"Classificação {n}",
        "orderProduction": "POR_PONTUACAO",
        "stages": [PROVA, TITULOS],
        "operation": "SOMA_PONDERADA",
        "normalization": "NENHUMA",
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "appealWindow": {"admits": True, "durationDays": 2, "unit": "DIAS_CORRIDOS"},
        "cutRule": {
            "targetKind": "FIXED",
            "targetCount": 10,
            "surplusCount": 0,
            "tieOutcome": "STRICT",
            "governedStage": "NONE",
            "continuation": "NONE",
        },
        "drawMethod": dict(DRAW_METHOD),
        "tiebreakers": [
            {
                "id": _id(perfil, "marco", n, "criterio", ordem),
                "order": ordem,
                "type": tipo,
                "parameters": parametros,
                "whenMissing": "ULTIMO_NO_CRITERIO",
            }
            for ordem, tipo, parametros in (
                (1, "MAIOR_PONTUACAO_NA_ETAPA", {"stageId": PROVA}),
                (2, "MAIOR_PONTUACAO_NA_ETAPA", {"stageId": TITULOS}),
                (3, "MAIOR_VALOR_DE_FATO", {"factId": fato}),
            )
        ],
    }


def _perfil(i):
    perfil = _id("perfil", i)
    ampla = _id(perfil, "AC")
    fatos = [
        {
            "id": _id(perfil, "fato", 1),
            "code": "EXP",
            "label": "Meses de experiência",
            "type": "INTEIRO",
        },
        {
            "id": _id(perfil, "fato", 2),
            "code": "CONC",
            "label": "Data de conclusão",
            "type": "DATA",
        },
    ]
    return {
        "id": perfil,
        "code": f"P{i:02d}",
        "name": f"Professor da área {i}",
        "description": "Docência no ensino técnico e superior.",
        "requirements": ["Mestrado na área", "Experiência docente de dois anos"],
        "immediateVacancies": 10,
        "reserveType": "LIMITED",
        "reserveLimit": 20,
        "locality": f"Campus {i}",
        "competitionModalities": [
            {"id": ampla, "code": "AC", "name": "Ampla concorrência"},
            *(
                {
                    "id": _id(perfil, codigo),
                    "code": codigo,
                    "name": nome,
                    "normativeRule": {
                        "id": _id(perfil, codigo, "regra"),
                        "foundation": fundamento,
                        "version": "2025-06-03",
                        "percentage": percentual,
                        "rounding": {"modo": "PARA_CIMA"},
                    },
                }
                for codigo, nome, fundamento, percentual in RESERVADAS
            ),
        ],
        "generalCompetitionModalityId": ampla,
        "callForm": "PUBLICATION",
        "declaredFacts": fatos,
        "vacancyTable": [
            {"id": _id(perfil, "linha", "geral"), "modalityId": None, "immediateVacancies": 6},
            *(
                {
                    "id": _id(perfil, "linha", codigo),
                    "modalityId": _id(perfil, codigo),
                    "immediateVacancies": vagas,
                }
                for (codigo, *_), vagas in zip(RESERVADAS, (2, 1, 1), strict=True)
            ),
        ],
        "classificationMilestones": [
            _marco(perfil, n, fatos[0]["id"]) for n in range(1, MARCOS_POR_PERFIL + 1)
        ],
    }


def _etapa(identidade, nome, ordem):
    return {
        "id": identidade,
        "name": nome,
        "order": ordem,
        "weight": "1.0000",
        "eliminatory": True,
        "classificatory": True,
        "minimumScore": "60.0000",
        "maximumScore": "100.0000",
        "evaluationsPerRegistration": 1,
        "forma": "PONTUADA",
        "rotuloFavoravel": "",
        "rotuloDesfavoravel": "",
        "scheduleEventId": None,
    }


def _rascunho():
    # O período de inscrições é relativo ao relógio: a fixture publica o Edital, e com um término
    # fixo a publicação passaria a ser recusada por período encerrado no dia seguinte a ele.
    agora = timezone.now()
    return {
        "profiles": [_perfil(i) for i in range(1, PERFIS + 1)],
        "stages": [_etapa(PROVA, "Prova escrita", 1), _etapa(TITULOS, "Prova de títulos", 2)],
        "schedule": [
            {
                "id": _id("evento", "inscricoes"),
                "type": "Inscrições",
                "description": "Período de inscrições",
                "startAt": (agora - timedelta(days=1)).isoformat(timespec="seconds"),
                "endAt": (agora + timedelta(days=10)).isoformat(timespec="seconds"),
                "order": 1,
                "isRegistrationPeriod": True,
            }
        ],
    }


@pytest.fixture
def maior_edital(api_client, manager_headers, process_payload, client, seletor_ligado):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    resposta = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        _rascunho(),
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="limite-de-campos-0001"),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    assert resposta.status_code == 200, resposta.content
    edital.refresh_from_db()
    identificar(client, "ana.elaboradora", ["elaborador"])
    return edital


@pytest.fixture
def maior_edital_publicado(maior_edital, api_client):
    # **O rascunho vai de novo**: sem ele, `levar_a_publicacao` grava o rascunho mínimo por cima,
    # e a Retificação media um Edital de um Perfil — foi assim que este caso passou com limite mil.
    publicado = levar_a_publicacao(api_client, maior_edital, draft=_rascunho())
    assert PerfilVaga.objects.filter(edital=publicado).count() == PERFIS
    return publicado


class _Envio(HTMLParser):
    """Os pares nome → valor que o navegador enviaria a partir de um formulário, na ordem da tela.

    Uma lista, e não um dicionário: é o número de pares que o Django conta, e o `select` múltiplo
    das Etapas do marco envia um par por Etapa. Fica de fora o que o navegador não envia — campo
    desabilitado, caixa desmarcada, botão, arquivo não escolhido, e o que mora noutro formulário
    pelo atributo `form`.
    """

    def __init__(self, id_do_formulario):
        super().__init__(convert_charrefs=True)
        self.id_do_formulario = id_do_formulario
        self.dentro = False
        self.campos = []
        self._area = None
        self._escolha = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form":
            self.dentro = a.get("id") == self.id_do_formulario
            return
        if not self.dentro or "form" in a or "disabled" in a:
            return
        if tag == "input" and a.get("name"):
            tipo = a.get("type", "text")
            if tipo in ("submit", "button", "image", "reset", "file"):
                return
            if tipo in ("radio", "checkbox") and "checked" not in a:
                return
            self.campos.append((a["name"], a.get("value") or ("on" if tipo == "checkbox" else "")))
        elif tag == "textarea" and a.get("name"):
            self._area = [a["name"], ""]
        elif tag == "select" and a.get("name"):
            self._escolha = [a["name"], [], None, "multiple" in a]
        elif tag == "option" and self._escolha is not None:
            valor = a.get("value", "")
            if self._escolha[2] is None:
                self._escolha[2] = valor
            if "selected" in a:
                self._escolha[1].append(valor)

    def handle_data(self, dados):
        if self._area is not None:
            self._area[1] += dados

    def handle_endtag(self, tag):
        if tag == "form":
            self.dentro = False
        elif tag == "textarea" and self._area is not None:
            # O navegador descarta a quebra de linha logo depois de `<textarea>`.
            nome, valor = self._area
            self.campos.append((nome, valor.removeprefix("\n")))
            self._area = None
        elif tag == "select" and self._escolha is not None:
            nome, escolhidos, primeiro, multiplo = self._escolha
            if multiplo:
                self.campos.extend((nome, valor) for valor in escolhidos)
            else:
                self.campos.append((nome, escolhidos[-1] if escolhidos else primeiro or ""))
            self._escolha = None


def _envio_da_tela(client, url, id_do_formulario, *botao):
    """O envio que a tela produz quando se aperta `botao` sem mexer em nada."""
    resposta = client.get(url)
    assert resposta.status_code == 200
    leitor = _Envio(id_do_formulario)
    leitor.feed(resposta.content.decode())
    assert leitor.campos, f"o formulário #{id_do_formulario} não foi encontrado em {url}"
    return [*leitor.campos, *botao]


def _cabe_no_limite(envio, tela):
    campos = len(envio)
    limite = settings.DATA_UPLOAD_MAX_NUMBER_FIELDS
    assert campos <= limite, (
        f"{tela} do maior Edital previsto envia {campos} campos, e o limite é {limite}. Refaça a "
        "conta do comentário de DATA_UPLOAD_MAX_NUMBER_FIELDS em config/settings/base.py — e não "
        "diminua o Edital de referência para caber."
    )
    # O irmão do limite de campos, que também recusa antes da view e não muda com ele.
    corpo = len(urlencode(envio).encode())
    assert corpo <= settings.DATA_UPLOAD_MAX_MEMORY_SIZE, (
        f"{tela} do maior Edital previsto envia {corpo} bytes, acima de "
        "DATA_UPLOAD_MAX_MEMORY_SIZE."
    )


def _url(edital, etapa):
    return reverse("interface:compor-etapa", args=[edital.id, etapa])


def _enviar(client, url, envio, **extra):
    """Codificado como o navegador codifica o formulário da etapa, que não declara `enctype`."""
    return client.post(
        url, urlencode(envio), content_type="application/x-www-form-urlencoded", **extra
    )


# --- O maior Edital previsto cabe --------------------------------------------------------------


@pytest.mark.parametrize("etapa", ["perfis", "classificacao"])
def test_a_etapa_do_maior_edital_cabe_no_limite_e_grava(client, maior_edital, etapa):
    """Contado no formulário que a tela devolve, e gravado de volta pelo mesmo envio.

    Gravar prova que a conta é a do envio de verdade: um campo que o teste deixasse de ler faria a
    view recusar a etapa, ou perder o que ele leva — e o Perfil ou o marco sumiria da contagem.
    """
    url = _url(maior_edital, etapa)
    envio = _envio_da_tela(client, url, "formulario", ("destino", etapa))
    _cabe_no_limite(envio, f"A etapa {etapa}")

    resposta = _enviar(client, url, envio)

    assert resposta.status_code == 302, resposta.content.decode()[:2000]
    assert resposta["Location"].endswith(f"?salvo={etapa}")
    assert PerfilVaga.objects.filter(edital=maior_edital).count() == PERFIS
    assert (
        MarcoClassificatorio.objects.filter(perfil__edital=maior_edital).count()
        == PERFIS * MARCOS_POR_PERFIL
    )


def test_a_retificacao_do_maior_edital_cabe_no_limite(client, maior_edital_publicado):
    """A Retificação envia o Edital publicado inteiro, e é o maior dos três envios.

    *Ver o que vai mudar* não grava nada: o que se prova é que o envio chega à view — que devolve a
    tela da Retificação —, e não que morre antes dela.
    """
    url = reverse("interface:retificar", args=[maior_edital_publicado.id])
    envio = _envio_da_tela(client, url, "formulario-da-retificacao")
    _cabe_no_limite(envio, "A Retificação")

    multivalor = {}
    for nome, valor in envio:
        multivalor.setdefault(nome, []).append(valor)
    # Por `multipart`, como o formulário declara: o Django conta os campos dos dois jeitos.
    resposta = client.post(url, multivalor)

    assert resposta.status_code == 200
    assert "O envio passou do limite" not in resposta.content.decode()


# --- Quando o limite ainda assim é passado -----------------------------------------------------


@pytest.fixture
def limite_baixo(settings):
    """Um limite que o maior Edital passa — é o que o envio grande de amanhã encontraria."""
    settings.DATA_UPLOAD_MAX_NUMBER_FIELDS = 100
    return settings


def test_o_envio_acima_do_limite_volta_como_pagina_da_gestao(client, maior_edital, limite_baixo):
    revisao = maior_edital.revision
    url = _url(maior_edital, "perfis")
    envio = _envio_da_tela(client, url, "formulario", ("destino", "perfis"))

    resposta = _enviar(client, url, envio, HTTP_REFERER=f"http://testserver{url}")

    assert resposta.status_code == 413
    corpo = resposta.content.decode()
    assert "O envio passou do limite que o sistema aceita" in corpo
    # O que aconteceu: nada gravado, e por quê, com o número que quem administra precisa ler.
    assert "Nada foi gravado" in corpo
    assert "mais campos do que o sistema aceita num envio só, que são 100" in corpo
    # O que fazer: não perder o digitado, e o que pedir a quem.
    assert "botão Voltar do navegador" in corpo
    # O rascunho local sobrevive, mas restaurá-lo é reenviar tudo: a ajuda não o promete já.
    assert "só poderá ser restaurado depois que o limite for ampliado" in corpo
    assert "ampliação do limite de envio a quem administra o sistema no Cefor" in corpo
    # A volta é para a etapa, e não só para a lista.
    assert f'href="http://testserver{url}"' in corpo
    # É a página da gestão, e não a recusa por permissão.
    assert "Cefor/Ifes</title>" in corpo
    assert "deveria ter acesso" not in corpo
    maior_edital.refresh_from_db()
    assert maior_edital.revision == revisao


def test_a_classificacao_acima_do_limite_tambem_volta_como_pagina(
    client, maior_edital, limite_baixo
):
    url = _url(maior_edital, "classificacao")
    envio = _envio_da_tela(client, url, "formulario", ("destino", "classificacao"))

    resposta = _enviar(client, url, envio)

    assert resposta.status_code == 413
    assert "Nada foi gravado" in resposta.content.decode()


def test_a_recusa_e_a_mesma_com_debug_ligado(client, maior_edital, limite_baixo):
    """O `handler400` do Django é trocado pela página técnica: o preview mostraria outra coisa."""
    limite_baixo.DEBUG = True
    url = _url(maior_edital, "perfis")
    envio = _envio_da_tela(client, url, "formulario", ("destino", "perfis"))

    resposta = _enviar(client, url, envio)

    assert resposta.status_code == 413
    assert "O envio passou do limite que o sistema aceita" in resposta.content.decode()


def test_a_origem_de_outro_site_nao_vira_link(client, maior_edital, limite_baixo):
    url = _url(maior_edital, "perfis")
    envio = _envio_da_tela(client, url, "formulario", ("destino", "perfis"))

    resposta = _enviar(client, url, envio, HTTP_REFERER="https://outro.exemplo/pagina")

    assert resposta.status_code == 413
    assert "outro.exemplo" not in resposta.content.decode()


def test_fora_da_gestao_a_resposta_continua_a_do_django(client, limite_baixo):
    """O portal não passa pela página da gestão: o limite é o mesmo, a resposta não."""
    campos = [(f"campo-{i}", "x") for i in range(101)]

    resposta = _enviar(client, reverse("portal:acesso"), campos)

    assert resposta.status_code == 400
    assert "O envio passou do limite" not in resposta.content.decode()
