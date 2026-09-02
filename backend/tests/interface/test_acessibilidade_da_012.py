"""As cinco telas da 012, nos critérios transversais que a casa já cobra.

Rótulo associado, foco anunciado na recusa, nenhuma tabela que force rolagem horizontal em 375 px,
e nenhuma cor sozinha carregando significado. Não substitui revisão manual — verifica o que dá
para verificar, que é justamente o que costuma regredir sem ninguém ver.
"""

import re

import pytest
from django.urls import reverse

from tests.fixtures.comissao import DOCUMENTO_A, alocar_em, constituir, inscrever
from tests.fixtures.edital import identificador
from tests.fixtures.mesa import distribuir_para
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]

SEED = 20


@pytest.fixture
def cenario(gestor, api_client, manager_headers, raiz_de_arquivos):
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from tests.fixtures.comissao import ETAPA_A1, publicar_processo_com_etapas

    edital = publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"mvp-test-key-{SEED:04d}"},
        {
            "institutionalCode": "PS-2026-K1",
            "title": "Processo acessível",
            "firstEdital": {"number": "K1", "year": 2026, "title": "Edital acessível"},
        },
        seed=SEED,
        com_documentos=True,
        avaliacoes=2,
        maxima="100.0000",
    )
    etapa = identificador(ETAPA_A1, SEED)
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo="acess",
    )
    alocar_em(gestor, edital.processo, membros["joao"], edital, etapa, chave="acess")
    inscricao = inscrever(edital, 1, primeiro=2800, documentos=[identificador(DOCUMENTO_A, SEED)])[
        0
    ]
    contexto = {"edital": edital, "etapa": etapa, "processo": edital.processo, "membros": membros}
    distribuir_para(contexto, gestor, ["joao"], [inscricao], chave="acess")
    return {**contexto, "inscricao": inscricao}


def telas_da_presidencia(cenario):
    return {
        "distribuicao": reverse(
            "interface:distribuicao", args=[cenario["edital"].id, cenario["etapa"]]
        ),
        "impedimentos": reverse(
            "interface:impedimentos", args=[cenario["edital"].id, cenario["etapa"]]
        ),
    }


def telas_do_avaliador(cenario):
    return {
        "mesa": reverse("interface:minha-etapa", args=[cenario["edital"].id, cenario["etapa"]]),
        "inscricao": reverse(
            "interface:mesa-inscricao",
            args=[cenario["edital"].id, cenario["etapa"], cenario["inscricao"].id],
        ),
    }


def corpos(client, seletor_ligado, cenario):
    paginas = {}
    identificar(client, "carlos", ["gestor", "auditor"])
    for nome, url in telas_da_presidencia(cenario).items():
        paginas[nome] = client.get(url).content.decode()
    paginas["trilha"] = client.get(
        reverse("interface:trilha-da-avaliacao", args=[cenario["edital"].id, cenario["etapa"]])
    ).content.decode()
    paginas["conclusoes"] = client.get(
        reverse("interface:conclusoes-preservadas", args=[cenario["edital"].id, cenario["etapa"]])
    ).content.decode()
    identificar(client, "joao", [])
    for nome, url in telas_do_avaliador(cenario).items():
        paginas[nome] = client.get(url).content.decode()
    return paginas


def test_todo_campo_tem_rotulo_associado(client, seletor_ligado, cenario):
    """Rótulo sem `for` é rótulo que o leitor de tela não liga ao campo."""
    for nome, corpo in corpos(client, seletor_ligado, cenario).items():
        for campo in re.finditer(r"<(input|select|textarea)\b([^>]*)>", corpo):
            atributos = campo.group(2)
            if 'type="hidden"' in atributos or 'type="checkbox"' in atributos:
                continue
            identificador_do_campo = re.search(r'id="([^"]+)"', atributos)
            assert identificador_do_campo, f"{nome}: campo sem id — {campo.group(0)[:70]}"
            tem_rotulo = f'for="{identificador_do_campo.group(1)}"' in corpo
            tem_aria = "aria-label" in atributos
            assert tem_rotulo or tem_aria, f"{nome}: {identificador_do_campo.group(1)} sem rótulo"


def test_toda_tabela_rola_dentro_do_proprio_conteiner(client, seletor_ligado, cenario):
    """375 px sem rolagem horizontal da **página**: quem rola é a tabela, no seu contêiner.

    A classe já existe na base desde a 011; o que este teste impede é a 012 acrescentar tabela
    solta, que empurraria a página inteira para o lado no celular.
    """
    for nome, corpo in corpos(client, seletor_ligado, cenario).items():
        for tabela in re.finditer(r'<table class="tabela">', corpo):
            antes = corpo[: tabela.start()]
            # A classe pode vir acompanhada — `lista-da-mesa` limita a largura da lista —, e o
            # que importa é que o contêiner rolável seja o pai imediato da tabela.
            assert re.search(r'<div class="tabela-rolavel[^"]*">\s*$', antes), nome


def test_as_recusas_anunciam_se_e_recebem_foco(client, seletor_ligado, cenario):
    """Recusa que não é anunciada obriga a pessoa a procurar o que deu errado."""
    identificar(client, "carlos", ["gestor"])
    url = reverse("interface:impedimentos", args=[cenario["edital"].id, cenario["etapa"]])

    corpo = client.post(
        url,
        {"identity_subject": "joao", "inscricao_id": str(cenario["inscricao"].id), "motivo": ""},
    ).content.decode()

    assert 'role="alert"' in corpo
    assert 'tabindex="-1"' in corpo


def test_o_estado_de_conclusao_nao_depende_so_de_cor(client, seletor_ligado, cenario):
    """A situação da inscrição é **palavra**, e não um ponto colorido."""
    identificar(client, "joao", [])
    corpo = client.get(
        reverse("interface:minha-etapa", args=[cenario["edital"].id, cenario["etapa"]])
    ).content.decode()

    # Três estados, três palavras: pendente virou "não iniciada" e "em rascunho", que é o que a
    # coluna precisa distinguir para quem retoma o trabalho.
    assert "Não iniciada" in corpo


def test_as_telas_tem_titulo_e_trilha_de_navegacao(client, seletor_ligado, cenario):
    """Saber onde se está, e como voltar — em todas elas."""
    for nome, corpo in corpos(client, seletor_ligado, cenario).items():
        assert "<h1>" in corpo, nome
        assert 'aria-label="Trilha de navegação"' in corpo, nome
