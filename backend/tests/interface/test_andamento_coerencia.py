"""O que a orientação diz, a tela do ato confirma (127, US4, SC-1230, SC-1236).

**Prever não é autorizar** (contrato de derivação, §1.4). A tela do ato continua sendo quem recusa;
a derivação antecipa o que ela diria. Se as duas divergirem, a derivação está errada — e é este
arquivo que diz qual das duas.

Dois sentidos, por Edital e por papel:

- toda providência *Pendente* ou *Obsoleto* **da pessoa** leva a uma tela cujo GET, com a identidade
  dela, mostra o controle daquele ato;
- toda *Aguarda* ou *Impedido* que tem tela leva a uma que não oferece o ato, ou que diz a mesma
  razão.

E, nos testes de transição, a orientação anda quando o ato acontece (SC-1236).
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface import andamento as a
from tests.fixtures.andamento import certame_p1, certame_s1
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.recortes import montar_cenario_7_1_2
from tests.fixtures.sorteio import certame_de_sorteio
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

#: O controle de cada ato na tela de destino: o destino do formulário, ou o campo que o distingue.
#: Por ato, e não por natureza, onde uma tela tem vários (a convocação).
MARCADORES = {
    a.RELACAO: "/sorteio/relacao",
    a.SEMENTE: "/sorteio/ocorrencia",
    a.SORTEIO: "/sorteio/realizar",
    a.ORDEM: "/emitir",
    a.CORTE: "/corte/emitir",
    a.APURACAO: "/ocupacao/apurar",
    a.DISTRIBUIR: 'name="acao" value="propor"',
    a.CONSOLIDAR: "/consolidar",
    a.AVALIAR: "/inscricoes/",
    a.RESULTADO: "/publicar",
    a.CONFERIR: "/documentos",
    a.RECURSO: "/recursos/",
}
MARCADORES_DA_CONVOCACAO = {
    "Convocar": "/convocacao/titulares",
    "Emitir": "/convocacao/pendentes",
    "Registrar a publicação": "/convocacao/pendentes",
    "Registrar o não atendimento": "/convocacao/vencidos",
    "Chamar a próxima": "/convocacao/convocar",
    "Registrar o desfecho": "/desfecho",
    "Pedir a faixa seguinte": "/ocupacao/faixa-seguinte",
}


def marcador(item):
    if item.natureza == a.CONVOCACAO or item.ato == "Pedir a faixa seguinte":
        return next(
            m for prefixo, m in MARCADORES_DA_CONVOCACAO.items() if item.ato.startswith(prefixo)
        )
    return MARCADORES[item.natureza]


def nivel_1(client, edital):
    resposta = client.get(reverse("interface:detalhe", args=[edital.id]))
    assert resposta.status_code == 200
    return resposta.context["nivel_1"], resposta.context["andamento"]


def conferir_coerencia(client, edital, *, espera_alguma_sua=True):
    """As duas direções, para a identidade que está na sessão do `client`."""
    nivel, andamento = nivel_1(client, edital)
    suas = [item for item in nivel.itens if item.sua]
    if espera_alguma_sua:
        assert suas, "o cenário deveria ter ao menos uma providência da pessoa"
    for item in suas:
        assert item.url, f"providência sua sem caminho: {item.ato}"
        tela = client.get(item.url)
        assert tela.status_code == 200, (item.ato, item.url, tela.status_code)
        assert marcador(item) in tela.content.decode(), (
            f"'{item.ato}' é dita sua, e {item.url} não oferece o ato"
        )
    for perfil in andamento.perfis:
        for ponto in perfil.pontos:
            for celula in {id(c): c for c in ponto.celulas.values()}.values():
                if celula.situacao not in (a.AGUARDA, a.IMPEDIDO) or not celula.url:
                    continue
                if celula.natureza not in MARCADORES or celula.natureza == a.CONVOCACAO:
                    continue
                corpo = client.get(celula.url).content.decode()
                assert celula.razao in corpo or MARCADORES[celula.natureza] not in corpo, (
                    f"'{celula.ato}' espera ({celula.razao}), e {celula.url} oferece o ato"
                )
    return nivel


# --- os cenários, um por família, e os papéis que agem neles -----------------------------------


@pytest.fixture
def base(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    return gestor, api_client, manager_headers, process_payload


@pytest.mark.parametrize(
    ("subject", "papeis"), [("carlos", ["gestor"]), ("maria", [])], ids=["gestor", "presidencia"]
)
def test_s1_quem_conduz(client, base, subject, papeis):
    certame = certame_s1(*base)
    identificar(client, subject, papeis)
    conferir_coerencia(client, certame["edital"])


def test_s1_com_as_inscricoes_abertas_a_tela_diz_a_mesma_espera(client, base):
    certame = certame_de_sorteio(*base, periodo_aberto=True)
    identificar(client, "carlos", ["gestor"])
    nivel = conferir_coerencia(client, certame["edital"], espera_alguma_sua=False)
    assert any(item.situacao == a.AGUARDA for item in nivel.itens)


@pytest.mark.parametrize(
    ("subject", "papeis"), [("maria", []), ("joao", [])], ids=["presidencia", "avaliador"]
)
def test_p1_a_presidencia_e_o_avaliador(client, base, subject, papeis):
    certame = certame_p1(*base)
    identificar(client, subject, papeis)
    conferir_coerencia(client, certame["edital"])


def test_p2_o_corte_depois_da_ordem(client, base):
    edital, _, _ = montar_cenario_7_1_2(*base, prefixo="coerencia-127")
    identificar(client, "carlos", ["gestor"])
    nivel = conferir_coerencia(client, edital)
    assert any(item.natureza == a.CORTE and item.sua for item in nivel.itens)


@pytest.mark.parametrize(
    ("subject", "papeis"),
    [("carlos", ["gestor"]), ("paula.publicadora", ["publicador"])],
    ids=["gestor", "publicador"],
)
def test_p2_a_convocacao_e_a_publicacao(client, base, subject, papeis):
    edital, _, _ = montar_cenario_da_convocacao(*base, prefixo="coerencia-127-conv")
    identificar(client, subject, papeis)
    conferir_coerencia(client, edital)


# --- as transições: a orientação anda quando o ato acontece (SC-1236) --------------------------


def test_convocar_troca_convocar_por_emitir_a_comunicacao(client, base):
    gestor = base[0]
    edital, _, inscricoes = montar_cenario_da_convocacao(*base, prefixo="transicao-127")
    identificar(client, "carlos", ["gestor"])
    antes, _ = nivel_1(client, edital)
    assert any(item.ato.startswith("Convocar 2 titulares") for item in antes.itens)

    convocar(edital, gestor, inscricoes[0], idempotency_key="transicao-127-convocar")

    depois, _ = nivel_1(client, edital)
    atos = [item.ato for item in depois.itens]
    assert "Convocar 1 titular" in atos
    assert "Emitir 1 comunicação" in atos, atos


def test_avaliar_e_consolidar_libera_a_ordem(client, base):
    """Depois da Etapa feita, a ordem deixa de ser *Depois* e vira providência de quem conduz."""
    from processo_seletivo.resultados.application.consolidacao import consolidar
    from tests.fixtures.mesa import concluir_como, distribuir_para

    gestor = base[0]
    certame = certame_p1(*base)
    identificar(client, "maria", [])
    antes, andamento = nivel_1(client, certame["edital"])
    assert not any(item.natureza == a.ORDEM for item in antes.itens)

    distribuir_para(certame, gestor, ["joao"], certame["inscricoes"][2:], chave="transicao-resto")
    for inscricao in certame["inscricoes"]:
        concluir_como(certame, "joao", inscricao, pontuacao="70")
    meio, _ = nivel_1(client, certame["edital"])
    assert any(item.ato == "Consolidar 3 inscrições prontas" for item in meio.itens)

    consolidar(
        actor=gestor,
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        etapa_id=certame["etapa"],
        inscricao_ids=[i.id for i in certame["inscricoes"]],
        idempotency_key="transicao-127-consolidar",
        correlation_id="teste-127",
    )
    depois, _ = nivel_1(client, certame["edital"])
    assert any(item.natureza == a.ORDEM and item.sua for item in depois.itens)
    conferir_coerencia(client, certame["edital"])
