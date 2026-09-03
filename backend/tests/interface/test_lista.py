"""Tela de lista de Processos e Editais (US1 da 002).

Verifica o que a tela promete: escopo institucional respeitado, ações filtradas por permissão,
e o mínimo de acessibilidade estrutural exigido por FR-023 e FR-024 desde a primeira tela.
"""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import ProcessoSeletivo
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar


@pytest.fixture
def cenario(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.mark.django_db
@pytest.mark.integration
def test_lista_exige_identificacao(client, seletor_ligado):
    resposta = client.get(reverse("interface:lista"))
    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("interface:identificar")


@pytest.mark.django_db
@pytest.mark.integration
def test_lista_mostra_processos_e_editais_do_escopo(client, seletor_ligado, cenario):
    identificar(client, "bruno.homologador", ["homologador"])
    corpo = client.get(reverse("interface:lista")).content.decode()

    processo = ProcessoSeletivo.objects.get()
    assert processo.institutional_code in corpo
    assert processo.title in corpo
    assert f"{cenario.number}/{cenario.year}" in corpo
    assert cenario.title in corpo
    assert "Publicado" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_criar_processo_continua_visivel_com_a_lista_cheia(client, seletor_ligado, cenario):
    """FR-001: a ação existia e o template só a renderizava dentro do bloco `{% empty %}`.

    Com um Processo cadastrado ela desaparecia — a rota continuava lá, alcançável só por quem
    soubesse a URL. É o beco sem saída mais barato de fechar, e o mais visível.
    """
    identificar(client, "marcia.gestora", ["gestor"])
    corpo = client.get(reverse("interface:lista")).content.decode()

    assert ProcessoSeletivo.objects.exists(), "o cenário precisa ter lista não vazia"
    assert "Novo Processo Seletivo" in corpo
    assert reverse("interface:processo-criar") in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_criar_processo_nao_aparece_para_quem_nao_pode_criar(client, seletor_ligado, cenario):
    """Ocultar é conveniência, não fronteira — mas oferecer o que será recusado é ruído."""
    identificar(client, "iris.auditora", ["auditor"])
    corpo = client.get(reverse("interface:lista")).content.decode()

    assert "Novo Processo Seletivo" not in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_lista_nao_revela_processo_de_outro_escopo(client, seletor_ligado, cenario, settings):
    """Anti-IDOR: a listagem não pode ser a brecha por onde se enxerga o que não se alcança."""
    identificar(client, "gestor.externo", ["gestor"])
    sessao = client.session
    sessao["interface_identidade"] = {
        "subject": "gestor.externo",
        "escopo": "outra-instituicao",
        "papeis": ["gestor"],
    }
    sessao.save()

    corpo = client.get(reverse("interface:lista")).content.decode()
    assert ProcessoSeletivo.objects.get().institutional_code not in corpo
    assert "Nenhum Processo Seletivo no seu escopo" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_acoes_seguem_a_permissao_de_quem_olha(client, seletor_ligado, cenario):
    """FR-002: a tela oferece só o que a pessoa pode fazer — sem que isso substitua o backend."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    elaborador = client.get(reverse("interface:lista")).content.decode()
    assert "Retificar" in elaborador
    assert "Encerrar" not in elaborador

    client.post(reverse("interface:sair"))
    identificar(client, "marcia.gestora", ["gestor"])
    gestor = client.get(reverse("interface:lista")).content.decode()
    assert "Encerrar" in gestor
    assert "Retificar" not in gestor


@pytest.mark.django_db
@pytest.mark.integration
def test_pessoa_sem_papel_recebe_orientacao_e_nao_area_vazia(client, seletor_ligado, cenario):
    """FR-028 da 002: sem papel reconhecido, orientar a quem pedir acesso.

    **A forma mudou com a 011, e a garantia não.** Antes, quem não escolhia papel era barrado na
    identificação com 422 — e o aviso "Sem permissões" do template era inalcançável. A 011 trouxe
    um ator que é exatamente esse: quem integra uma comissão sem capacidade sistêmica nenhuma,
    cuja autorização vem do vínculo e que precisa entrar para ver `Minhas Etapas`. Barrá-lo na
    porta o tornaria irrepresentável. A orientação, que é o que o requisito pede, passou a ser
    dada onde ela sempre esteve escrita.
    """
    resposta = client.post(
        reverse("interface:identificar"),
        {"subject": "servidor.novo", "papeis": []},
        follow=True,
    )

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    # A orientação precisa estar **onde a pessoa chega**, e não numa tela que ela não tem motivo
    # para abrir: seguir o redirecionamento é o que torna este teste sobre a jornada.
    assert "não possui papel de responsabilidade nem atribuição" in corpo
    assert "solicite acesso" in corpo.lower()


@pytest.mark.django_db
@pytest.mark.integration
def test_estrutura_acessivel_da_lista(client, seletor_ligado, cenario):
    """FR-023 e FR-024 desde a primeira tela, não como retrabalho no fim."""
    identificar(client, "bruno.homologador", ["homologador"])
    corpo = client.get(reverse("interface:lista")).content.decode()

    assert 'lang="pt-BR"' in corpo
    assert 'class="pular" href="#conteudo"' in corpo, "link de pular para o conteúdo"
    assert corpo.count("<h1>") == 1, "exatamente um h1 por página"
    assert 'scope="col"' in corpo and 'scope="row"' in corpo, "cabeçalhos de tabela associados"
    assert "<caption>" in corpo, "tabela precisa de legenda"
    assert "aria-label" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_ambiente_de_demonstracao_e_anunciado(client, seletor_ligado, cenario):
    """A pessoa precisa saber que a identidade não veio do diretório institucional."""
    identificar(client, "bruno.homologador", ["homologador"])
    corpo = client.get(reverse("interface:lista")).content.decode()
    assert "Ambiente de demonstração" in corpo
    assert "não pode ser usada em produção" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_seletor_de_identidade_nao_existe_com_a_configuracao_desligada(client, settings):
    """Fora de desenvolvimento o seletor não existe: ele substitui a autenticação."""
    settings.INTERFACE_SELETOR_IDENTIDADE = False
    resposta = client.get(reverse("interface:identificar"))
    assert resposta.status_code == 503
    corpo = resposta.content.decode()
    assert "Autenticação institucional não configurada" in corpo
    assert "checkbox" not in corpo, "nenhum papel pode ser escolhido"


@pytest.mark.django_db
@pytest.mark.integration
def test_plural_de_edital_em_portugues(
    client, seletor_ligado, cenario, api_client, manager_headers
):
    """Plural em português não sai de sufixo: 'Editalis' apareceu na tela antes disto."""
    identificar(client, "bruno.homologador", ["homologador"])
    corpo = client.get(reverse("interface:lista")).content.decode()
    assert "1 Edital neste Processo" in corpo
    assert "Editalis" not in corpo

    api_client.post(
        f"/api/v1/admin/processos/{cenario.processo_id}/editais",
        {"number": "31", "year": 2026, "title": "Segundo"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "plural-key-00000001"},
    )
    corpo = client.get(reverse("interface:lista")).content.decode()
    assert "2 Editais neste Processo" in corpo


def folha(corpo):
    return corpo[corpo.index("<style>") : corpo.index("</style>")]


@pytest.mark.django_db
@pytest.mark.integration
def test_a_acao_indisponivel_nao_se_parece_com_a_disponivel(client, seletor_ligado):
    """`.desabilitado` só existia para `.botao`.

    A ação de linha continuava com a borda verde e a cor de link: oferecia o que não se pode
    fazer, que é pior do que não oferecer. FR-024 manda mostrar o controle **e** o motivo — o
    controle mostrado precisa parecer o que é.
    """
    identificar(client, "carlos", ["gestor"])

    css = folha(client.get(reverse("interface:lista")).content.decode())

    regra = css.split(".acao.desabilitado{")[1].split("}")[0]
    assert "cursor:not-allowed" in regra
    assert "var(--verde)" not in regra


@pytest.mark.django_db
@pytest.mark.integration
def test_a_contagem_diz_o_que_ela_conta(client, seletor_ligado, edital_a):
    """ "5 Publicado, 2 Cancelado, 7 no total" — de quê?

    A página se chama Processos Seletivos e lista Processos; quem conta são os Editais dentro
    deles. O nome acessível já dizia; quem vê a tela é que ficava sem saber.
    """
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(reverse("interface:lista")).content.decode()

    assert "Editais no total" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_o_estado_do_processo_fica_com_o_nome_dele(client, seletor_ligado, edital_a):
    """Os seis itens do cabeçalho saíam numa fileira só, e o estado caía **depois** dos botões.

    Para saber se aquele Processo está em elaboração era preciso atravessar as ações até o
    extremo oposto do título que o estado qualifica.
    """
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(reverse("interface:lista")).content.decode()

    cabeca = corpo.split('<article class="processo">')[1].split("</header>")[0]
    # O estado vem **antes** do grupo de ações, e não depois dele.
    identidade = cabeca.split('<span class="acoes">')[0]
    assert "s-EM_ELABORACAO" in identidade or "s-PUBLICADO" in identidade
    assert "/comissao" in cabeca and "/comissao" not in identidade
