"""Os passos que os testes da identidade institucional repetem (106)."""

from datetime import UTC, datetime
from urllib.parse import urlencode

from django.test import RequestFactory
from django.urls import reverse

from processo_seletivo.interface import identidade
from processo_seletivo.seguranca.autenticacao import IdentidadeAutenticada, resolver_pessoa
from processo_seletivo.seguranca.models import Vinculo
from tests.fixtures import provedor_simulado

AGORA = datetime(2026, 10, 30, 12, 0, tzinfo=UTC)


def pessoa(identificador, *, nome="", email=""):
    """A pessoa desta identidade do provedor simulado, criada se preciso — sem entrar."""
    return resolver_pessoa(
        IdentidadeAutenticada(provedor_simulado.NOME, identificador, nome, email)
    )[0]


def vincular(alguem, escopo, papel, *, por="fixture"):
    """Um vínculo gravado direto: estado de partida, e não o ato de conceder."""
    return Vinculo.objects.create(
        pessoa=alguem,
        escopo=escopo,
        papel=papel,
        concedido_em=AGORA,
        concedido_por=por,
        motivo="estado de partida do teste",
    )


def entrar(client, identificador, *, nome="", email="", proximo=None):
    """A entrada inteira pela tela: a ida, o provedor que autentica, e o retorno com o bilhete."""
    ida = reverse("interface:entrar-institucional")
    if proximo:
        ida += "?" + urlencode({"proximo": proximo})
    resposta = client.get(ida)
    assert resposta.status_code == 302, resposta.content
    estado = provedor_simulado.ultima_ida()["estado"]
    bilhete = provedor_simulado.emitir(identificador, nome=nome, email=email)
    return client.get(
        reverse("interface:retorno-institucional"), {"estado": estado, "bilhete": bilhete}
    )


def ator_do_cliente(client):
    """O `Actor` que a gestão resolveria para a sessão deste cliente, numa requisição nova."""
    request = RequestFactory().get("/gestao/")
    request.session = client.session
    return identidade.ator_da_sessao(request)
