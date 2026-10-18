"""A trilha da conferência da consolidação no cabeçalho de contexto (082).

A tela que "Consolidar as selecionadas" e "Consolidar as N prontas" abrem era a última das que se
abrem da Distribuição a dizer o caminho no conteúdo, e o dizia sem o Processo nem a Alocação. Agora
é a da Distribuição com "Conferir" no fim, como a da retirada desde a 080 — e nada do que a tela
declara, nem o botão do ato, muda. O desenho em si é provado no navegador (quickstart): a tela é
resposta a um envio, e o inventário visual não a abre.

O cenário é montado aqui, e não importado do módulo da 012: com inscrições prontas de verdade, o
botão que consolida aparece, e é ele que precisa continuar igual.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.comissao import inscrever
from tests.fixtures.resultado import montar_etapa_de_leitura_unica, semear_prontas
from tests.interface.conftest import identificar
from tests.interface.test_telas_da_presidencia import (
    ate_o_processo,
    comeca_pelo_titulo,
    niveis_em_ordem,
)
from tests.interface.test_telas_de_uso_diario import conteudo, trilha_unica_no_cabecalho

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

PRONTAS = 3
PENDENTES = 2


@pytest.fixture
def etapa(gestor, api_client, manager_headers):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=8200, codigo="8200"
    )
    cenario["prontas"] = semear_prontas(cenario, PRONTAS, primeiro=1)
    # Sem avaliação: participam da Etapa e ficam de fora, com o motivo na conferência.
    cenario["pendentes"] = inscrever(cenario["edital"], PENDENTES, primeiro=100)
    return cenario


def _conferir(client, etapa, dados):
    resposta = client.post(
        reverse("interface:consolidar-resultados", args=[etapa["edital"].id, etapa["primeira"]]),
        {"chave_idempotencia": "conferir-8200", **dados},
    )
    assert resposta.status_code == 200, "a conferência não abriu"
    return resposta.content.decode()


def _pela_selecao(client, etapa):
    marcadas = etapa["prontas"] + etapa["pendentes"]
    return _conferir(client, etapa, {"inscricao_id": [str(i.id) for i in marcadas]})


def _por_todas_as_prontas(client, etapa):
    return _conferir(client, etapa, {"alcance": "prontas"})


def ate_a_etapa(etapa):
    processo = etapa["processo"]
    alocacoes = reverse("interface:alocacoes", args=[processo.id])
    distribuicao = reverse("interface:distribuicao", args=[etapa["edital"].id, etapa["primeira"]])
    return [
        *ate_o_processo(processo),
        f'<a href="{alocacoes}">Alocação por Etapa</a> ›',
        f'<a href="{distribuicao}">',
    ]


@pytest.mark.parametrize("abrir", [_pela_selecao, _por_todas_as_prontas])
def test_a_trilha_e_a_da_distribuicao_com_conferir(client, seletor_ligado, etapa, abrir):
    """`FR-1840`, `FR-1841`, `FR-1842`, `FR-1843`, `SC-720`, `SC-721`: GPS › Processos Seletivos ›
    código › Alocação por Etapa › Etapa › Conferir, uma vez só, pelos dois caminhos."""
    identificar(client, "maria", [])
    corpo = abrir(client, etapa)

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_a_etapa(etapa))
    assert trilha.rstrip().endswith('<span aria-current="page">Conferir</span>')
    assert comeca_pelo_titulo(corpo)
    assert "<h1>Confira antes de consolidar</h1>" in corpo
    # A seção é a do endereço: a barra e a trilha dizem a mesma coisa.
    assert f'<a href="{reverse("interface:lista")}" aria-current="true">' in corpo


@pytest.mark.parametrize("abrir", [_pela_selecao, _por_todas_as_prontas])
def test_o_alcance_e_o_ato_continuam_os_mesmos(client, seletor_ligado, etapa, abrir):
    """`FR-1844`: o botão de perigo, depois da explicação e do alcance, e "Cancelar e voltar" à
    Etapa; conferir não consolida nada."""
    identificar(client, "maria", [])
    pagina = conteudo(abrir(client, etapa))

    botao = f'<button type="submit" class="botao perigoso">Consolidar {PRONTAS} inscrições</button>'
    assert pagina.count(botao) == 1
    niveis_em_ordem(
        pagina,
        [
            '<p class="sub">',
            "<strong>Não há desfazer</strong>",
            f'<h2 id="alcance">O que será consolidado — {PRONTAS} inscrições</h2>',
            botao,
            "Cancelar e voltar",
        ],
    )
    distribuicao = reverse("interface:distribuicao", args=[etapa["edital"].id, etapa["primeira"]])
    assert f'<a href="{distribuicao}" class="acao">Cancelar e voltar</a>' in pagina
    assert 'class="botao">Consolidar' not in pagina, "o ato não ganha o desenho de ação principal"
    assert ResultadoEtapa.objects.count() == 0, "conferir não consolida nada"


def test_o_que_fica_de_fora_continua_declarado(client, seletor_ligado, etapa):
    """`FR-1844`: pela seleção, as pendentes continuam listadas com o motivo, antes do botão."""
    identificar(client, "maria", [])
    pagina = conteudo(_pela_selecao(client, etapa))

    fora = f'<h2 id="fora">O que ficará de fora — {PENDENTES} inscrições</h2>'
    niveis_em_ordem(pagina, ['<h2 id="alcance">', fora, '<button type="submit"'])
    for inscricao in etapa["pendentes"]:
        assert f"<strong>{inscricao.protocolo or inscricao.id}</strong> —" in pagina


def test_a_trilha_abre_com_a_mesma_navegacao_das_outras_telas():
    """`FR-1840`: a grafia que a 081 passa a conferir em todo template que sobrescreve a trilha —
    a `nav` nomeada com a classe do cabeçalho, e o produto pelo parcial."""
    from tests.interface.test_polish_da_055 import GESTAO

    texto = re.sub(r"\s+", "", (GESTAO / "consolidacao_confirmar.html").read_text())
    bloco = texto.split("{%blockcaminho_do_contexto%}")[1].split("{%endblock%}")[0]
    assert bloco.startswith(
        '<navaria-label="Trilhadenavegação"class="caminho-da-secao">'
        '{%include"interface/_produto_na_trilha.html"%}'
    )
    assert 'class="trilha"' not in texto, "a trilha do conteúdo saiu"
