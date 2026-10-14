"""As telas públicas não prometem o que nenhum ato registrou (072, FR-1638, research T-008).

A 072 escreveu texto novo na vitrine, na página da seleção e nas telas de acesso — resultado
publicado, prazo de recurso, a volta à vaga. O vocabulário que a área do candidato já proíbe
("classificado", "aprovado", "direito à vaga", "matriculado"…) passa a valer também aqui: o
dicionário é **importado** de onde nasceu, e não copiado, para que as duas varreduras não envelheçam
separadas.

A varredura lê o texto visível — sem comentário de template e sem a folha de estilo —, como a da
063.
"""

import re

import pytest
from django.core import mail
from django.urls import reverse

from tests.fixtures.candidato import PERFIL_DOCENTE
from tests.fixtures.divulgacao import publicar_o_ato
from tests.portal.test_acompanhamento_pela_situacao import PROIBIDAS
from tests.portal.test_prazo_recursal_publico import montar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def visivel(resposta):
    corpo = resposta.content.decode()
    main = re.search(r"<main[^>]*>(.*)</main>", corpo, re.S).group(1)
    return " ".join(re.sub(r"<[^>]+>", " ", main).split())


def proibidas_em(texto):
    return [
        f"{padrao!r}: {porque}" for padrao, porque in PROIBIDAS.items() if re.search(padrao, texto)
    ]


def test_vitrine_e_selecao_com_resultado_publicado(
    client, gestor, api_client, manager_headers, process_payload
):
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=98)
    publicar_o_ato(cenario, chave="publicar-072-98")

    for pagina in (
        client.get(reverse("portal:vitrine")),
        client.get(reverse("portal:selecao", args=[cenario["edital"].id])),
    ):
        assert proibidas_em(visivel(pagina)) == []


def test_selecao_aberta_e_telas_de_acesso_a_caminho_de_uma_vaga(client, selecao, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    mail.outbox.clear()
    destino = reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE])

    paginas = [
        client.get(reverse("portal:selecao", args=[selecao.id])),
        client.get(reverse("portal:acesso"), {"destino": destino}),
        client.post(reverse("portal:acesso"), {"email": "nova@exemplo.test"}, follow=True),
    ]
    codigo = re.search(r"\b(\d{6})\b", mail.outbox[-1].body).group(1)
    paginas.append(client.post(reverse("portal:acesso-codigo"), {"codigo": codigo}, follow=True))

    for pagina in paginas:
        assert proibidas_em(visivel(pagina)) == []
