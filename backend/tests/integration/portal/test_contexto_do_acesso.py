"""As telas de acesso dizem para qual vaga a pessoa está se identificando (072, FR-1619 a FR-1621).

Quem tocava "Inscrever-se nesta vaga" sem sessão caía numa tela "Entrar" que não dizia vaga
nenhuma; a do código e "Seus dados" também não. O contexto vem do **destino da identificação**, que
já passa pelas validações de hoje (`_destino_seguro`, a rota resolvida, o Perfil da versão vigente),
e nunca do e-mail — é por isso que a resposta continua a mesma exista ou não identidade (010,
FR-020, FR-021).
"""

import re
import uuid

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.identidade.models import CandidateIdentity, novo_subject
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import MARIA, PERFIL_DOCENTE, registrar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

CONTEXTO = "Professor de Informática"


@pytest.fixture
def canal(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


def a_vaga(selecao, perfil=PERFIL_DOCENTE):
    return reverse("portal:inscrever", args=[selecao.id, perfil])


def texto(resposta):
    corpo = resposta.content.decode()
    corpo = re.sub(r'<input type="hidden" name="csrfmiddlewaretoken"[^>]*>', "", corpo)
    main = re.search(r"<main[^>]*>(.*)</main>", corpo, re.S).group(1)
    return " ".join(re.sub(r"<[^>]+>", " ", main).split())


def codigo(caixa):
    return re.search(r"\b(\d{6})\b", caixa[-1].body).group(1)


def test_a_caminho_de_uma_vaga_o_acesso_e_o_codigo_nomeiam_a_vaga(client, selecao, canal):
    acesso = texto(client.get(reverse("portal:acesso"), {"destino": a_vaga(selecao)}))

    assert "Confirme seu e-mail para se inscrever" in acesso
    assert CONTEXTO in acesso
    assert "Edital 01/2026" in acesso and "Primeiro Edital" in acesso

    codigo_ = texto(
        client.post(reverse("portal:acesso"), {"email": "nova@exemplo.test"}, follow=True)
    )

    assert CONTEXTO in codigo_ and "Edital 01/2026" in codigo_
    assert "spam" in codigo_, "onde procurar o código que não chegou (FR-1621)"


def test_sem_destino_de_vaga_o_acesso_continua_como_esta(client, selecao, canal):
    """Q7 — "Entrar" é mantido; o contexto só existe quando há vaga a nomear."""
    acesso = texto(client.get(reverse("portal:acesso")))

    assert acesso.startswith("Entrar")
    assert CONTEXTO not in acesso


@pytest.mark.parametrize(
    "destino",
    [
        "https://exemplo.invalido/selecoes/",
        "/selecoes/nao-existe/",
        "pagina-do-edital",
        "perfil-de-outro-edital",
    ],
)
def test_destino_que_nao_e_vaga_valida_nao_nomeia_nada(client, selecao, canal, destino):
    """Nenhuma validação nova: o que não chega como vaga do próprio Edital não vira contexto."""
    if destino == "pagina-do-edital":
        destino = reverse("portal:selecao", args=[selecao.id])
    elif destino == "perfil-de-outro-edital":
        destino = a_vaga(selecao, perfil=uuid.uuid4())

    acesso = texto(client.get(reverse("portal:acesso"), {"destino": destino}))

    assert CONTEXTO not in acesso
    assert "para se inscrever" not in acesso


def test_a_resposta_ao_pedir_o_codigo_e_a_mesma_exista_ou_nao_identidade(client, selecao, canal):
    """FR-1620 — o contexto vem do destino; com ele, as duas telas continuam indistinguíveis."""
    registrar(MARIA)

    def tela_do_codigo(endereco):
        client.cookies.clear()
        client.get(reverse("portal:acesso"), {"destino": a_vaga(selecao)})
        resposta = client.post(reverse("portal:acesso"), {"email": endereco}, follow=True)
        return texto(resposta).replace(endereco, "<endereço>")

    assert tela_do_codigo(MARIA.email) == tela_do_codigo("ninguem@exemplo.test")


def test_a_reconciliacao_tambem_nomeia_a_vaga(client, selecao, canal):
    """A pessoa com participação anterior passa por mais uma tela — e ela também diz a vaga."""
    endereco = "maria.antiga@exemplo.test"
    identidade = CandidateIdentity.objects.create(
        subject=novo_subject(),
        nome="Maria Silva",
        cpf_normalizado="12345678909",
        created_at=timezone.now(),
    )
    Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=identidade.subject,
        edital_id=selecao.id,
        profile_id=PERFIL_DOCENTE,
        nome="Maria Silva",
        cpf="123.456.789-09",
        cpf_normalizado="12345678909",
        email=endereco,
        created_at=timezone.now(),
    )

    client.get(reverse("portal:acesso"), {"destino": a_vaga(selecao)})
    client.post(reverse("portal:acesso"), {"email": endereco})
    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)}, follow=True)

    assert resposta.redirect_chain[-1][0] == reverse("portal:acesso-reconciliar")
    assert CONTEXTO in texto(resposta)


def test_seus_dados_nomeia_a_vaga_e_diz_para_que_servem_nome_e_cpf(client, selecao, canal):
    """FR-1619, FR-1627 — a finalidade dita no ponto da coleta (texto a validar, ver
    `validacao-humana.md`)."""
    client.get(reverse("portal:acesso"), {"destino": a_vaga(selecao)})
    client.post(reverse("portal:acesso"), {"email": "nova@exemplo.test"})
    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)}, follow=True)

    assert resposta.redirect_chain[-1][0] == reverse("portal:meus-dados")
    dados = texto(resposta)
    assert CONTEXTO in dados
    assert "identificam você nas inscrições e nos resultados" in dados
    assert "uma única vez" in dados


def test_o_numero_nao_se_repete_quando_o_titulo_do_edital_ja_o_traz(
    client, raiz_de_arquivos, api_client, manager_headers, process_payload
):
    """O mesmo cuidado da FR-1606 no contexto: "Edital 01/2026 — Edital 01/2026 — …" foi visto no
    navegador, com o seed, depois da primeira implementação."""
    from datetime import timedelta

    from tests.fixtures.selecao import publicar_selecao, rascunho_aberto_com_documentos

    edital = publicar_selecao(
        api_client,
        manager_headers,
        {
            **process_payload,
            "firstEdital": {**process_payload["firstEdital"], "title": "Edital 01/2026 — Docentes"},
        },
        rascunho=rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)),
    )

    resposta = client.get(reverse("portal:acesso"), {"destino": a_vaga(edital)})
    contexto = re.search(r'<p class="vaga-do-destino">(.*?)</p>', resposta.content.decode(), re.S)

    assert contexto.group(1).count("01/2026") == 1
    assert "Edital 01/2026 — Docentes" in contexto.group(1)
    assert "<title>Confirme seu e-mail" in resposta.content.decode()
