"""A tela da ordem e o gesto da condução preveem a recusa da `128` (US2, US3).

O comando recusa sozinho (`tests/integration/classificacao/test_ordem_sem_resultado.py`); aqui se
prova que nenhuma tela oferece o que ele recusaria, e que a frase é a mesma.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.application import ordem_sem_resultado
from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.interface import conducao_do_marco
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db(transaction=True)

BOTAO_DE_EMITIR = re.compile(r"<button[^>]*>\s*Emitir (a )?ordem\s*</button>")


def _texto(resposta):
    assert resposta.status_code == 200, resposta.status_code
    return " ".join(resposta.content.decode().split())


def _campo(pagina, nome):
    return re.search(rf'name="{nome}" value="([^"]*)"', pagina).group(1)


def _proposta(edital):
    from processo_seletivo.classificacao.application.calculo import calcular_ordem
    from tests.fixtures.corte import MARCO
    from tests.fixtures.edital import PROFILE_ID

    return calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)


def _frase(edital):
    return ordem_sem_resultado.impedimento(_proposta(edital))["frase"]


@pytest.fixture
def sem_avaliacao(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    """O Edital 91 do estudo, reduzido: marco por pontuação, ninguém avaliado."""
    from tests.fixtures.corte import montar_cenario_do_corte

    edital, pontuada, inscricoes = montar_cenario_do_corte(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ordem-128-tela",
        pontuacoes=(),
        emitir_a_ordem=False,
    )
    return edital, pontuada, inscricoes


@pytest.fixture
def parcial(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    from tests.fixtures.corte import montar_cenario_do_corte

    edital, _, _ = montar_cenario_do_corte(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ordem-128-parcial",
        pontuacoes=("90.0000",),
        emitir_a_ordem=False,
    )
    return edital


def _tela(client, edital):
    from tests.fixtures.corte import MARCO

    return client.get(reverse("interface:ordenacao", args=[edital.id, MARCO]))


# --- US2 · a tela da ordem ------------------------------------------------------------------------


def test_a_tela_nao_oferece_emitir_e_leva_a_distribuicao(client, sem_avaliacao):
    """FR-4212, FR-4213, FR-4214, UX-261, SC-1302."""
    edital, pontuada, _ = sem_avaliacao
    identificar(client, "carlos", ["gestor"])

    pagina = _texto(_tela(client, edital))

    assert not BOTAO_DE_EMITIR.search(pagina)
    assert 'name="confirmacao_do_calculo"' not in pagina
    assert "A ordem ainda não pode ser emitida" in pagina
    assert _frase(edital) in pagina
    distribuicao = reverse("interface:distribuicao", args=[edital.id, pontuada["id"]])
    assert f'<a href="{distribuicao}">Distribuir {pontuada["name"]}</a>' in pagina
    assert client.get(distribuicao).status_code == 200, "o link não leva a uma recusa (FR-476)"
    assert "Sem pontuação nas Etapas enumeradas" in pagina, "a prévia continua (FR-4214)"
    assert "é aqui que ele se emite" not in pagina, "o aviso do topo não contradiz o bloco"


def test_quem_nao_gere_le_a_frase_sem_link_nem_pedido(client, sem_avaliacao):
    """FR-4213: nem o link da distribuição, nem "peça a alguém que a emita"."""
    edital, _, _ = sem_avaliacao
    identificar(client, "auditora", ["auditor"])

    pagina = _texto(_tela(client, edital))

    assert _frase(edital) in pagina
    assert "Distribuir " not in pagina
    assert "que a emita" not in pagina
    assert not BOTAO_DE_EMITIR.search(pagina)


def test_a_ordem_do_acervo_nao_traz_o_bloco_de_sucessao(client, sem_avaliacao, gestor, monkeypatch):
    """US2, cenário 3: a sucessão também seria recusada."""
    from tests.integration.classificacao.test_ordem_sem_resultado import _emitir_como_no_acervo

    edital, _, _ = sem_avaliacao
    assert _emitir_como_no_acervo(monkeypatch, edital, gestor, chave="128-tela-acervo")
    identificar(client, "carlos", ["gestor"])

    pagina = _texto(_tela(client, edital))

    assert 'class="sucessao"' not in pagina
    assert 'name="motivo"' not in pagina
    assert "A ordem vigente ainda não pode ser sucedida" in pagina, "existe ordem; falta suceder"
    assert _frase(edital) in pagina


def test_a_confirmacao_nao_abre(client, sem_avaliacao):
    """FR-4215: a rota volta à tela, e a tela não repete a frase como erro (R-4)."""
    from tests.fixtures.corte import MARCO

    edital, _, _ = sem_avaliacao
    identificar(client, "carlos", ["gestor"])

    resposta = client.post(
        reverse("interface:emitir-ordenacao", args=[edital.id, MARCO]),
        {"lista": "", "chave_idempotencia": "128-confirmar", "confirmacao_do_calculo": "x"},
    )

    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("interface:ordenacao", args=[edital.id, MARCO])
    pagina = _texto(client.get(resposta["Location"]))
    assert pagina.count(_frase(edital)) == 1
    assert "Não foi possível emitir" not in pagina
    assert re.search(r'<section class="aviso" aria-labelledby="sem-resultado" role="alert"', pagina)


def test_o_formulario_antigo_e_recusado_pelo_comando(client, sem_avaliacao):
    """FR-4206: quem tinha a tela aberta antes da regra manda `confirmar=1`; nada é gravado."""
    from tests.fixtures.corte import MARCO

    edital, _, _ = sem_avaliacao
    identificar(client, "carlos", ["gestor"])

    resposta = client.post(
        reverse("interface:emitir-ordenacao", args=[edital.id, MARCO]),
        {
            "confirmar": "1",
            "lista": "",
            "chave_idempotencia": "128-antigo",
            "confirmacao_do_calculo": "assinatura-de-antes",
        },
    )

    assert resposta.status_code == 302
    assert ato_vigente(edital=edital, marco_id=MARCO) is None
    assert _texto(client.get(resposta["Location"])).count(_frase(edital)) == 1


def test_a_ordem_parcial_continua_com_formulario_e_confirmacao(client, parcial):
    """FR-4204, US2 cenário 5: a confirmação da `126` continua no caso parcial."""
    from tests.fixtures.corte import MARCO

    identificar(client, "carlos", ["gestor"])
    antes = _texto(_tela(client, parcial))
    assert BOTAO_DE_EMITIR.search(antes)
    assert "A ordem ainda não pode ser emitida" not in antes

    confirmacao = _texto(
        client.post(
            reverse("interface:emitir-ordenacao", args=[parcial.id, MARCO]),
            {
                "lista": "",
                "chave_idempotencia": _campo(antes, "chave_idempotencia"),
                "confirmacao_do_calculo": _campo(antes, "confirmacao_do_calculo"),
            },
        )
    )
    assert "1 das 2 inscrições consideradas está sem resultado" in confirmacao
    assert "Emitir a ordem</button>" in confirmacao


# --- US3 · a conferência do gesto -----------------------------------------------------------------


def test_a_conferencia_do_gesto_poe_o_recorte_entre_os_impedidos(client, sem_avaliacao):
    """FR-4216, UX-262, SC-1303."""
    from tests.fixtures.corte import MARCO

    edital, _, _ = sem_avaliacao
    identificar(client, "maria", [])

    pagina = _texto(
        client.post(reverse("interface:gesto-do-marco", args=[edital.id, MARCO, "ordenar"]))
    )

    assert "Impedidos (1)" in pagina
    assert f"— {_frase(edital)}" in pagina
    assert "Serão praticados (0)" in pagina


def test_a_confirmacao_do_gesto_recusa_no_comando(sem_avaliacao, gestor):
    """FR-4208: a assinatura lida antes não basta; o comando recusa o recorte, e diz por quê."""
    from tests.fixtures.corte import MARCO

    edital, _, _ = sem_avaliacao
    _, perfil, marco = conducao_do_marco.marco_publicado(edital, MARCO)

    desfechos = conducao_do_marco.praticar(
        ator=gestor,
        edital=edital,
        perfil=perfil,
        marco=marco,
        operacao=conducao_do_marco.ORDENAR,
        itens=[(None, "Ampla concorrência", "assinatura-lida-antes")],
        chave="128-gesto",
    )

    assert desfechos[0]["feito"] is False
    assert desfechos[0]["razao"] == _frase(edital)
    assert ato_vigente(edital=edital, marco_id=MARCO) is None


def test_o_recorte_em_que_ninguem_concorreu_continua_a_praticar(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """FR-4205: no mesmo marco, a ampla sem resultado é impedida e o recorte vazio pratica."""
    from tests.fixtures.corte import MARCO
    from tests.fixtures.recortes import montar_cenario_7_1_2

    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ordem-128-gesto-vazio",
        pontuacoes=(),
        autodeclarar=False,
        emitir_a_ordem=False,
    )
    identificar(client, "maria", [])

    pagina = _texto(
        client.post(reverse("interface:gesto-do-marco", args=[edital.id, MARCO, "ordenar"]))
    )

    assert "ninguém concorreu — a ordem vazia é emitida e registra isso" in pagina
    assert "Impedidos (1)" in pagina


# --- Coerência com a `127` (FR-4218, SC-1306) -----------------------------------------------------


def test_o_andamento_nunca_diz_pendente_para_a_ordem_que_o_comando_recusa(sem_avaliacao):
    """A `127` deriva a ordem como *Depois* das Etapas que ela lê; a `128` recusa o mesmo caso.

    Se um dia a derivação disser *Pendente* aqui, o cartão "O que fazer agora" e o "Próximo nesta
    lista" mandariam emitir o que o comando recusa — o beco que a FR-476 da `033` proíbe.
    """
    from processo_seletivo.interface import andamento
    from tests.conftest import ator_institucional

    edital, _, _ = sem_avaliacao
    assert ordem_sem_resultado.impedimento(_proposta(edital)) is not None

    [perfil] = andamento.do_edital(edital, ator_institucional("maria")).perfis
    ordem = next(p for p in perfil.pontos if p.tipo == andamento.ORDEM)

    assert ordem.celula(None).situacao == andamento.DEPOIS
