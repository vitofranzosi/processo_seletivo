"""O link da mensagem leva à convocação, com ou sem sessão (121, FR-3876 a FR-3881).

`SC-1156`, `SC-1158`. Sem sessão, a convocação manda ao acesso com o destino; depois do código, a
pessoa chega a ela **sem passar pela lista**, nos três percursos que terminam em `_entrar`: a sessão
vencida, o primeiro acesso e a reconciliação de uma inscrição antiga.

**O destino é só um caminho** (FR-3879, `S4`): ele passa pela lista fechada, é reconstruído pela
rota, e não carrega autorização — a titularidade é conferida de novo pela convocação, ao abrir. E
nenhum link autentica (P-001 da `010`): a entrada continua sendo por e-mail e código.
"""

import re
import uuid
from urllib.parse import urlencode

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.convocacao.models import ComunicacaoEmitida, Convocacao
from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.domain.enderecos import canonizar
from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.portal.views import CHAVE_DO_DESTINO, _de_volta_a_vaga
from tests.fixtures import jornada_do_convocado as jornada

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

CPF = "12345678909"


@pytest.fixture
def canal(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


@pytest.fixture
def fx(gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return jornada.Montagem(gestor, api_client, manager_headers, process_payload)


@pytest.fixture
def cenario(fx, canal):
    return jornada.montar("A", fx)


def convocacao_de(inscricao_id):
    return reverse("portal:convocacao", args=[inscricao_id])


def titular(pessoa, *, com_credencial):
    """A identidade da inscrição: com a credencial (já entrou antes) ou sem (inscrição antiga)."""
    identidade, _ = CandidateIdentity.objects.get_or_create(
        subject=pessoa.identity_subject, defaults={"created_at": timezone.now()}
    )
    identidade.cpf_normalizado = CPF
    identidade.save(update_fields=["cpf_normalizado"])
    if com_credencial:
        associacao.associar_credencial(identidade, canonizar(pessoa.email), pessoa.email)
    return identidade


def pelo_codigo(client, canal, email):
    """O e-mail na tela de acesso e o código de seis dígitos que chegou numa mensagem separada."""
    client.post(reverse("portal:acesso"), {"email": email})
    codigo = re.search(r"\b(\d{6})\b", canal[-1].body).group(1)
    return client.post(reverse("portal:acesso-codigo"), {"codigo": codigo})


def pelo_link(client, destino):
    """O que o link faz sem sessão: a convocação manda ao acesso, que guarda o destino."""
    resposta = client.get(destino)
    assert resposta.status_code == 302
    assert resposta["Location"] == f"{reverse('portal:acesso')}?{urlencode({'destino': destino})}"
    assert client.get(resposta["Location"]).status_code == 200


class TestOsTresPercursos:
    """`SC-1156`: depois do código, a convocação, sem passar pela lista."""

    def test_sessao_vencida(self, client, canal, cenario):
        pessoa = cenario.pessoa
        titular(pessoa, com_credencial=True)
        destino = convocacao_de(pessoa.id)

        pelo_link(client, destino)
        chegada = pelo_codigo(client, canal, pessoa.email)

        assert chegada.status_code == 302 and chegada["Location"] == destino
        pagina = client.get(destino)
        assert pagina.status_code == 200
        assert "Você foi convocado!" in pagina.content.decode()

    def test_reconciliacao_de_inscricao_antiga(self, client, canal, cenario):
        pessoa = cenario.pessoa
        titular(pessoa, com_credencial=False)
        destino = convocacao_de(pessoa.id)

        pelo_link(client, destino)
        convite = pelo_codigo(client, canal, pessoa.email)
        assert convite["Location"] == reverse("portal:acesso-reconciliar")
        chegada = client.post(
            reverse("portal:acesso-reconciliar"), {"acao": "confirmar", "cpf": CPF}
        )

        assert chegada.status_code == 302 and chegada["Location"] == destino
        assert client.get(destino).status_code == 200

    def test_primeiro_acesso(self, client, canal, cenario):
        """Sem identidade para o endereço, ela nasce, e a chegada é o destino, que não autoriza:
        a identidade nova não é a titular, e a convocação responde como inexistente (FR-3879)."""
        destino = convocacao_de(cenario.pessoa.id)

        pelo_link(client, destino)
        chegada = pelo_codigo(client, canal, "primeira.vez@exemplo.test")

        assert chegada.status_code == 302 and chegada["Location"] == destino
        assert client.get(destino).status_code == 404


class TestOsDestinosHostis:
    """`SC-1158`, FR-3878: outro host, esquema estranho, rota fora da lista, consulta, fragmento."""

    @pytest.mark.parametrize(
        "destino",
        [
            "https://outro.exemplo/selecoes/inscricoes/{id}/convocacao",
            "javascript:alert(1)",
            "//outro.exemplo/selecoes/inscricoes/{id}/convocacao",
            "/selecoes/inscricoes/{id}/acompanhamento",
            "/selecoes/nao-existe/",
        ],
    )
    def test_vira_minhas_inscricoes(self, client, canal, cenario, destino):
        pessoa = cenario.pessoa
        titular(pessoa, com_credencial=True)

        client.get(reverse("portal:acesso"), {"destino": destino.format(id=pessoa.id)})
        chegada = pelo_codigo(client, canal, pessoa.email)

        assert chegada["Location"] == reverse("portal:inscricoes")

    def test_consulta_e_fragmento_sao_descartados(self, client, canal, cenario):
        pessoa = cenario.pessoa
        titular(pessoa, com_credencial=True)
        recebido = convocacao_de(pessoa.id) + "?depois=/selecoes/acesso&x=1#outro"

        client.get(reverse("portal:acesso"), {"destino": recebido})
        chegada = pelo_codigo(client, canal, pessoa.email)

        assert chegada["Location"] == convocacao_de(pessoa.id), "reconstruído pela rota"

    def test_sem_sessao_as_rotas_de_escrita_respondem_como_hoje(self, client, cenario):
        """D-002, FR-3877: nenhum redirecionamento leva a praticar ato."""
        from tests.fixtures import documentos_da_convocacao as cenarios

        pessoa = cenario.pessoa
        item = cenarios.item(cenario.convocacao, cenarios.CERTIDAO)
        envio = client.post(
            reverse("portal:apresentar-documento-da-convocacao", args=[pessoa.id, item.id]),
            {"arquivo": cenarios.pdf()},
        )
        arquivo = client.get(
            reverse("portal:documento-da-convocacao", args=[pessoa.id, uuid.uuid4()])
        )

        assert envio.status_code == 404 and arquivo.status_code == 404
        assert not item.apresentacoes.exists()


class TestODestinoNaoAutoriza:
    def test_destino_guardado_de_outra_visita(self, client, canal, cenario):
        """FR-3879, `S4`: um destino antigo leva só à rota que ele nomeia, e a convocação de outra
        pessoa nele continua recusada como inexistente depois do código."""
        alheia = convocacao_de(cenario.pessoa.id)
        sessao = client.session
        sessao[CHAVE_DO_DESTINO] = alheia
        sessao.save()

        chegada = pelo_codigo(client, canal, "outra.pessoa@exemplo.test")

        assert chegada["Location"] == alheia
        inexistente = client.get(convocacao_de(uuid.uuid4()))
        recusa = client.get(alheia)
        assert recusa.status_code == inexistente.status_code == 404

    def test_cada_inscricao_leva_a_propria_convocacao(self):
        """Caso-limite: o link é da inscrição, e a chegada é a convocação dela, nunca a de outra."""
        uma, outra = uuid.uuid4(), uuid.uuid4()

        assert _de_volta_a_vaga(convocacao_de(uma)) == convocacao_de(uma)
        assert _de_volta_a_vaga(convocacao_de(outra)) == convocacao_de(outra)


class TestNadaSeEscrevePorGet:
    def test_abrir_nao_move_prazo_e_so_registra_leitura_com_sessao_titular(
        self, client, canal, cenario
    ):
        """FR-3881, `S8`: sem sessão, nenhuma leitura registrada; com sessão titular, uma."""
        pessoa = cenario.pessoa
        destino = convocacao_de(pessoa.id)

        def leituras():
            return RegistroAuditoria.objects.filter(operation="CONVOCACAO_LER").count()

        def prazo():
            convocacao = Convocacao.objects.get(id=cenario.convocacao.id)
            enviados = ComunicacaoEmitida.objects.filter(convocacao=convocacao)
            return convocacao.vencimento, sorted(c.enviado_em for c in enviados if c.enviado_em)

        antes, prazo_antes = leituras(), prazo()
        client.get(destino)
        assert leituras() == antes, "sem sessão, nada se registra"

        titular(pessoa, com_credencial=True)
        pelo_link(client, destino)
        pelo_codigo(client, canal, pessoa.email)
        client.get(destino)

        assert leituras() == antes + 1
        assert prazo() == prazo_antes, "abrir não move prazo (FR-288b da 019)"
