"""Os caminhos novos levam à convocação e ao requerimento **da própria** inscrição (059, `US4`).

**Mostrar o caminho a mais gente é o momento de conferir quem passa por ele.** Até a `059` a tela da
convocação só se alcançava digitando o endereço; agora a lista e o acompanhamento o oferecem. A
titularidade não mudou — `_inscricao_do_titular` continua sendo a porta de todas estas rotas —, e é
exatamente por isso que ela precisa de teste aqui: uma view nova escrita com `get(pk=…)` passaria
por qualquer teste de tela.

**A recusa não revela que a inscrição existe** (`FR-071`, `FR-399`). Status igual não basta: dois
corpos diferentes com o mesmo 404 continuam dizendo qual identificador existe. A comparação é do
corpo inteiro, com o que muda a cada requisição — o token de CSRF — neutralizado.
"""

import re
import uuid

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.portal.identidade import CHAVE_SESSAO
from processo_seletivo.requerimentos.application import exigencia, preencher
from tests.fixtures.candidato import MARIA
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO, regra
from tests.fixtures.edital import PROFILE_ID

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.authorization]

INEXISTENTE = uuid.UUID("00000000-0000-0000-0000-0000000009ff")


@pytest.fixture
def maria_e_joao(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Dois titulares convocados num Edital que pede o requerimento na convocação.

    João tem o requerimento enviado — é o que dá à rota do anterior um identificador real dele para
    Maria tentar.
    """
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.requerimento import campos_de_exemplo, declarar

    def publicar_declarando(api_client, manager_headers, process_payload, *, draft=None):
        return publish_original(
            api_client,
            manager_headers,
            process_payload,
            draft=draft,
            antes_de_submeter=declarar("AT_CALL"),
        )

    edital, _, inscricoes = montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="portal-059-alheia",
        geral=2,
        cut=regra(surplusCount=1),
        publicar=publicar_declarando,
    )
    fila = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]
    maria, joao = (next(i for i in inscricoes if i.id == alvo) for alvo in fila[:2])
    convocar(edital, gestor, maria.id, idempotency_key="alheia-maria")
    convocar(edital, gestor, joao.id, idempotency_key="alheia-joao")

    preencher.abrir_rascunho(inscricao=joao)
    preencher.gravar(inscricao=joao, dados=campos_de_exemplo(), expected_revision=None)
    versao = preencher._conteudo(joao)
    preencher.enviar(
        identidade=MARIA,
        inscricao=joao,
        versao_exibida_id=versao.id,
        declaracao_exibida=preencher.declaracao_publicada(versao.content),
        aceite=True,
    )
    return maria, joao, exigencia.vigente_de(joao)


def entrar_como(client, inscricao):
    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=inscricao.identity_subject, defaults={"created_at": timezone.now()}
    )
    sessao = client.session
    sessao[CHAVE_SESSAO] = str(registro.pk)
    sessao.save()


def corpo(resposta):
    """O corpo sem o que muda a cada requisição: o token de CSRF."""
    texto = resposta.content.decode()
    return re.sub(r'name="csrfmiddlewaretoken" value="[^"]+"', "", texto)


def rotas(inscricao_id, requerimento_id):
    return {
        "acompanhamento": reverse("portal:acompanhamento", args=[inscricao_id]),
        "convocacao": reverse("portal:convocacao", args=[inscricao_id]),
        "requerimento": reverse("portal:requerimento", args=[inscricao_id]),
        "requerimento-anterior": reverse(
            "portal:requerimento-anterior", args=[inscricao_id, requerimento_id]
        ),
    }


def test_a_lista_e_o_acompanhamento_de_maria_nao_mostram_nada_de_joao(client, maria_e_joao):
    maria, joao, _ = maria_e_joao
    entrar_como(client, maria)

    lista = client.get(reverse("portal:inscricoes")).content.decode()
    acompanhamento = client.get(reverse("portal:acompanhamento", args=[maria.id])).content.decode()

    assert reverse("portal:convocacao", args=[maria.id]) in lista, "a dela está lá"
    for pagina in (lista, acompanhamento):
        assert str(joao.id) not in pagina


@pytest.mark.parametrize(
    "rota", ["acompanhamento", "convocacao", "requerimento", "requerimento-anterior"]
)
def test_a_rota_de_joao_responde_a_maria_como_inscricao_inexistente(client, maria_e_joao, rota):
    maria, joao, requerimento_de_joao = maria_e_joao
    entrar_como(client, maria)

    alheia = client.get(rotas(joao.id, requerimento_de_joao.id)[rota])
    inexistente = client.get(rotas(INEXISTENTE, requerimento_de_joao.id)[rota])

    assert alheia.status_code == inexistente.status_code == 404
    assert corpo(alheia) == corpo(inexistente), "o corpo diferente diria qual identificador existe"


@pytest.mark.parametrize("rota", ["acompanhamento", "convocacao", "requerimento"])
def test_a_titular_alcanca_as_proprias(client, maria_e_joao, rota):
    """O contraponto: sem ele, uma rota que recusasse **todo mundo** passaria no teste acima."""
    maria, _, _ = maria_e_joao
    entrar_como(client, maria)

    assert client.get(rotas(maria.id, INEXISTENTE)[rota]).status_code == 200


@pytest.mark.parametrize(
    "rota", ["acompanhamento", "convocacao", "requerimento", "requerimento-anterior"]
)
def test_sem_sessao_nenhuma_rota_revela_se_a_inscricao_existe(client, maria_e_joao, rota):
    _, joao, requerimento_de_joao = maria_e_joao

    existente = client.get(rotas(joao.id, requerimento_de_joao.id)[rota])
    inexistente = client.get(rotas(INEXISTENTE, requerimento_de_joao.id)[rota])

    assert existente.status_code == inexistente.status_code
    assert corpo(existente) == corpo(inexistente)


def test_nenhum_endereco_novo_carrega_dado_pessoal(client, maria_e_joao):
    """`FR-1102`: o único identificador nos `href` é o da inscrição — nem CPF, nem nome, nem
    e-mail."""
    maria, _, _ = maria_e_joao
    entrar_como(client, maria)

    paginas = [
        client.get(reverse("portal:inscricoes")).content.decode(),
        client.get(reverse("portal:acompanhamento", args=[maria.id])).content.decode(),
        client.get(reverse("portal:convocacao", args=[maria.id])).content.decode(),
    ]
    enderecos = {href for pagina in paginas for href in re.findall(r'href="([^"]+)"', pagina)}
    pessoais = [maria.cpf_normalizado, maria.email, maria.nome.split()[0]]

    for href in enderecos:
        for dado in filter(None, pessoais):
            assert dado.lower() not in href.lower(), f"{dado!r} em {href}"
