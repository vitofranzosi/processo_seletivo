"""As telas filhas da Distribuição e a auditoria da comissão, quarto incremento (080).

Nas seis telas que se abrem a partir da Distribuição e na Auditoria da comissão a trilha mora no
cabeçalho de contexto, e só lá — a das filhas é a da Distribuição com a tela no fim; a Auditoria
do Edital, que divide o modelo de página, ficou com o cabeçalho da 076 até a 083. O que acabou de
acontecer vem logo abaixo do título, Impedimentos ganha título para o registro e "Filtrar" é a ação
principal das consultas. O desenho em si é provado no navegador e pelo inventário visual refeito
(quickstart): aqui fica o que a marcação garante.
"""

import pytest
from django.urls import reverse

from tests.interface.conftest import identificar
from tests.interface.test_acessibilidade_da_012 import cenario  # noqa: F401 — fixture
from tests.interface.test_telas_da_presidencia import (
    abrir,
    ate_o_processo,
    comeca_pelo_titulo,
    niveis_em_ordem,
)
from tests.interface.test_telas_de_uso_diario import (
    conteudo,
    trilha_unica_no_cabecalho,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

FILHAS = {
    "interface:impedimentos": "Impedimentos",
    "interface:registrar-ocorrencia": "Ocorrência",
    "interface:resultados-da-etapa": "Resultados",
    "interface:trilha-da-avaliacao": "Trilha da avaliação",
    "interface:conclusoes-preservadas": "Conclusões preservadas",
}
# As três que a auditoria também abre (`FR-091` da 012).
DA_AUDITORIA_TAMBEM = (
    "interface:resultados-da-etapa",
    "interface:trilha-da-avaliacao",
    "interface:conclusoes-preservadas",
)


def ate_a_etapa(contexto):
    edital, etapa, processo = contexto["edital"], contexto["etapa"], contexto["processo"]
    alocacoes = reverse("interface:alocacoes", args=[processo.id])
    distribuicao = reverse("interface:distribuicao", args=[edital.id, etapa])
    return [
        *ate_o_processo(processo),
        f'<a href="{alocacoes}">Alocação por Etapa</a> ›',
        f'<a href="{distribuicao}">',
    ]


def entre(pagina, inicio, fim):
    return pagina[pagina.index(inicio) : pagina.index(fim, pagina.index(inicio))]


# ---- a trilha no cabeçalho -------------------------------------------------------------------


@pytest.mark.parametrize(("rota", "atual"), FILHAS.items())
def test_nas_filhas_a_trilha_e_a_da_distribuicao_com_a_tela(
    client,
    seletor_ligado,
    cenario,  # noqa: F811
    rota,
    atual,
):
    """`FR-1800`, `FR-1801`, `FR-1802`, `SC-702`, `SC-703`: GPS › Processos Seletivos › código ›
    Alocação por Etapa › Etapa › tela, uma vez só, e o conteúdo começa pelo título."""
    identificar(client, "maria", [])
    corpo = abrir(client, rota, cenario["edital"].id, cenario["etapa"])

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_a_etapa(cenario))
    assert trilha.rstrip().endswith(f'<span aria-current="page">{atual}</span>')
    assert comeca_pelo_titulo(corpo)
    # A seção é a do endereço: a barra e a trilha dizem a mesma coisa.
    assert f'<a href="{reverse("interface:lista")}" aria-current="true">' in corpo


def test_na_conferencia_da_retirada_a_trilha_passa_pela_etapa(client, seletor_ligado, cenario):  # noqa: F811
    """`FR-1800`, `FR-1801`, `FR-1809`: a conferência termina em Conferir, com a Etapa a um
    clique, como a da inclusão na comissão; o alcance e "Retirar" não mudam."""
    from processo_seletivo.avaliacoes.models import Atribuicao

    identificar(client, "maria", [])
    edital, etapa = cenario["edital"], cenario["etapa"]
    atribuicao = Atribuicao.objects.get(ativo=True, inscricao=cenario["inscricao"])
    corpo = client.post(
        reverse("interface:distribuicao-remover", args=[edital.id, etapa]),
        {"chave_idempotencia": "conferir-080", "atribuicao_id": [str(atribuicao.id)]},
    ).content.decode()

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_a_etapa(cenario))
    assert trilha.rstrip().endswith('<span aria-current="page">Conferir</span>')
    assert comeca_pelo_titulo(corpo)
    assert "<h1>Confira antes de retirar</h1>" in corpo
    assert '<button type="submit" class="botao perigoso">Retirar 1 atribuição</button>' in corpo
    assert "Cancelar e voltar" in conteudo(corpo)
    assert Atribuicao.objects.filter(ativo=True).count() == 1, "conferir não retira nada"


def test_na_auditoria_da_comissao_a_trilha_sobe_ao_cabecalho(client, seletor_ligado, cenario):  # noqa: F811
    """`FR-1800`, `FR-1801`, `FR-1802`: GPS › Processos Seletivos › código › Auditoria da
    comissão."""
    identificar(client, "carlos", ["gestor", "auditor"])
    processo = cenario["processo"]
    corpo = abrir(client, "interface:auditoria-comissao", processo.id)

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_processo(processo))
    assert trilha.rstrip().endswith('<span aria-current="page">Auditoria da comissão</span>')
    assert comeca_pelo_titulo(corpo)


# A Auditoria do Edital tinha aqui o guardião da `FR-1803`, com o cabeçalho da 076 e a trilha no
# conteúdo. A 083 a levou ao cabeçalho (`FR-1850` da 083), e o modelo das três auditorias não tem
# mais trilha no conteúdo: a prova está em `test_telas_do_edital.py`, e a das demais telas, na
# Supervisão, em `test_telas_de_uso_diario.py`.


@pytest.mark.parametrize("rota", DA_AUDITORIA_TAMBEM)
def test_quem_audita_le_a_mesma_trilha_de_quem_preside(
    client,
    seletor_ligado,
    cenario,  # noqa: F811
    rota,
):
    """`FR-1804`: nenhum nível aparece, some ou deixa de ser link conforme quem lê (D-003)."""
    argumentos = (cenario["edital"].id, cenario["etapa"])
    identificar(client, "maria", [])
    da_presidencia = trilha_unica_no_cabecalho(abrir(client, rota, *argumentos))
    identificar(client, "ana.auditora", ["auditor"])
    da_auditoria = trilha_unica_no_cabecalho(abrir(client, rota, *argumentos))

    assert da_auditoria == da_presidencia


# ---- o que acabou de acontecer ---------------------------------------------------------------


def test_na_ocorrencia_o_erro_vem_antes_da_explicacao(client, seletor_ligado, cenario):  # noqa: F811
    """`FR-1806`: logo depois do título e da Etapa, com o mesmo papel e o mesmo foco; a
    explicação continua antes do formulário."""
    identificar(client, "maria", [])
    edital, etapa = cenario["edital"], cenario["etapa"]
    pagina = conteudo(
        client.post(
            reverse("interface:registrar-ocorrencia", args=[edital.id, etapa]),
            {"motivo": "", "inscricao_id": [str(cenario["inscricao"].id)]},
        ).content.decode()
    )

    erro = pagina.index('<p class="erro" role="alert" tabindex="-1" autofocus>')
    assert pagina.index('<p class="sub">') < erro < pagina.index("Não há desfazer.")
    assert pagina.index("Não há desfazer.") < pagina.index('<form method="post">')


def test_nas_conclusoes_a_resposta_da_reabertura_vem_antes_do_filtro(
    client,
    seletor_ligado,
    cenario,  # noqa: F811
):
    """`FR-1806`: a resposta à reabertura antes da explicação e do filtro."""
    identificar(client, "maria", [])
    sessao = client.session
    sessao["erro_da_reabertura"] = "Esta avaliação mudou desde que a página foi aberta."
    sessao.save()
    pagina = conteudo(
        abrir(client, "interface:conclusoes-preservadas", cenario["edital"].id, cenario["etapa"])
    )

    erro = pagina.index("Não foi possível reabrir:")
    assert pagina.index('<p class="sub">') < erro < pagina.index('<p class="ajuda">')
    assert erro < pagina.index('<form method="get" class="filtro">')


def test_nas_conclusoes_o_erro_do_filtro_fica_no_filtro(client, seletor_ligado, cenario):  # noqa: F811
    """`FR-1806`: o erro do filtro continua junto do campo a que se refere."""
    identificar(client, "maria", [])
    url = reverse("interface:conclusoes-preservadas", args=[cenario["edital"].id, cenario["etapa"]])
    pagina = conteudo(client.get(url, {"inscricao": "nao-existe"}).content.decode())
    filtro = entre(pagina, '<form method="get" class="filtro">', "</form>")

    assert 'class="erro"' in filtro
    assert 'class="erro"' not in pagina.split('<form method="get" class="filtro">')[0]


# ---- títulos por região ----------------------------------------------------------------------


def test_impedimentos_tem_titulo_para_o_registro(client, seletor_ligado, cenario):  # noqa: F811
    """`FR-1807`: o formulário numa seção com título, antes das avaliações fora do conjunto; os
    campos e o botão não mudam."""
    identificar(client, "maria", [])
    pagina = conteudo(
        abrir(client, "interface:impedimentos", cenario["edital"].id, cenario["etapa"])
    )
    secao = entre(pagina, '<section aria-labelledby="registrar-titulo">', "</section>")

    assert '<h2 id="registrar-titulo">Registrar um impedimento</h2>' in secao
    for campo in ('id="identity_subject"', 'id="inscricao_id"', 'id="motivo"'):
        assert campo in secao
    assert '<button type="submit" class="botao">Registrar impedimento</button>' in secao
    assert pagina.index("registrar-titulo") < pagina.index('<h2 id="inelegiveis">')


# ---- a hierarquia das ações ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("rota", "identidade"),
    [
        ("interface:trilha-da-avaliacao", ("maria", [])),
        ("interface:conclusoes-preservadas", ("maria", [])),
        ("interface:auditoria-comissao", ("carlos", ["gestor", "auditor"])),
    ],
)
def test_nas_consultas_filtrar_e_a_acao_principal(
    client,
    seletor_ligado,
    cenario,  # noqa: F811
    rota,
    identidade,
):
    """`FR-1808`: "Filtrar" com o desenho de ação principal (`FR-1008` da 055, D-004)."""
    identificar(client, *identidade)
    argumentos = (
        (cenario["processo"].id,)
        if rota == "interface:auditoria-comissao"
        else (cenario["edital"].id, cenario["etapa"])
    )
    filtro = entre(
        conteudo(abrir(client, rota, *argumentos)), '<form method="get" class="filtro">', "</form>"
    )

    assert '<button type="submit" class="botao">Filtrar</button>' in filtro
    assert 'class="acao">Filtrar' not in filtro


def test_as_acoes_que_nao_se_desfazem_nao_mudam_de_desenho():
    """`FR-1809`: o perigo continua perigo, e "Reabrir" continua ação de linha (D-005)."""
    from tests.interface.test_polish_da_055 import GESTAO

    esperados = {
        "impedimentos.html": [
            '<button type="submit" class="botao perigoso">Registrar mesmo assim</button>',
            '<button type="submit" class="botao">Registrar impedimento</button>',
        ],
        "ocorrencia.html": [
            '<button type="submit" class="botao perigoso">Registrar mesmo assim</button>',
            '<button type="submit" class="botao">Revisar antes de registrar</button>',
        ],
        "distribuicao_remover_confirmar.html": [
            '<button type="submit" class="botao perigoso">Retirar'
        ],
        "conclusoes.html": ['<button type="submit" class="acao">Reabrir</button>'],
    }
    for template, botoes in esperados.items():
        corpo = (GESTAO / template).read_text()
        for botao in botoes:
            assert corpo.count(botao) == 1, (template, botao)
