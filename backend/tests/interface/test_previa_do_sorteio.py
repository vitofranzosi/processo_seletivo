"""A prévia do sorteio no painel da etapa Classificação (098).

O Perfil é o da `095`: PPI e PcD, com 10 vagas na linha geral, 3 na PPI e 2 na PcD, e o marco corta
pelo quadro — aqui, com a forma trocada para sorteio. O cálculo é testado em `tests/unit/sorteios/`
e a equivalência com o caminho oficial em
`tests/integration/sorteios/test_previa_do_sorteio_equivale_ao_oficial.py`; aqui se confere a tela:
o botão, a semente fictícia e a recusa da forjada, a ordem de cada lista, a ocupação, o resumo das
rodadas, a população informada e a ausência de efeito.
"""

import json
import re

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.interface import previa_do_sorteio
from tests.interface.test_compor import PERFIL
from tests.interface.test_previa_da_classificacao import B
from tests.interface.test_previa_por_recorte import PCD, PPI, do_quadro, montar, texto

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

SORTEIO = {f"{B}-orderProduction": "POR_SORTEIO"}


# As três fixtures são as da `095`, redeclaradas: importar uma fixture de outro módulo de teste a
# redefine aqui, e o ruff acusa cada uso como redefinição (a regra de `tests/fixtures/corte.py`).
@pytest.fixture
def com_reservas(client, seletor_ligado, edital):
    return montar(client, edital)


@pytest.fixture
def com_saldo(client, seletor_ligado, edital):
    return montar(client, edital, "ON_BALANCE")


@pytest.fixture
def com_esgotamento(client, seletor_ligado, edital):
    return montar(client, edital, "ON_EXHAUSTION")


GRUPOS = re.compile(r'<p class="grupos-da-semente">(.*?)</p>', re.S)


def cartao(**alteracoes):
    return do_quadro(**{**SORTEIO, **alteracoes})


def previa(client, edital, cartao_=None, **dados):
    url = reverse("interface:fragmento-previa-da-classificacao", args=[PERFIL, "0"])
    resposta = client.get(url, {"edital": str(edital.id), **(cartao_ or cartao()), **dados})
    assert resposta.status_code == 200, resposta.content
    return resposta.content.decode()


def semente(corpo):
    return re.search(r'name="semente" value="([^"]*)"', corpo).group(1)


def grupos(corpo):
    return re.findall(r"<span>(\d+)</span>", GRUPOS.search(corpo).group(1))


def bloco(corpo, classe):
    """O texto de uma seção do painel, para que uma frase não seja achada noutra."""
    inicio = corpo.index(f'class="{classe}"')
    return texto(corpo[inicio : corpo.index("</section>", inicio)])


# --- US1: o botão, a semente fictícia e a ordem de cada lista (FR-2477 a FR-2496) ---------------


def test_o_cartao_do_marco_por_sorteio_oferece_simular_sorteio(client, com_reservas):
    resposta = client.get(
        reverse("interface:fragmento-marco-recomposto", args=[PERFIL, "0"]),
        {"edital": str(com_reservas.id), **cartao()},
    )
    corpo = resposta.content.decode()

    assert "Simular sorteio" in corpo
    assert "Simular classificação" not in corpo
    assert 'aria-controls="painel-da-previa"' in corpo


def test_a_semente_e_ficticia_tem_cinco_grupos_de_seis_digitos_e_nao_tem_campo(
    client, com_reservas
):
    corpo = previa(client, com_reservas)

    assert [len(g) for g in grupos(corpo)] == [6, 6, 6, 6, 6]
    assert "selo-ficticio" in bloco(corpo, "semente-ficticia") or "fictícia" in texto(corpo)
    assert "a semente sairá do concurso que o Edital declarar, e a ordem será outra" in texto(corpo)
    # O único campo de semente é o oculto, com o token; nenhum se digita (FR-2483).
    campos = re.findall(r'<input[^>]*name="(semente|seed|material)"[^>]*>', corpo)
    assert campos == ["semente"]
    assert 'type="hidden" id="semente-da-previa"' in corpo


def test_sortear_de_novo_troca_a_semente(client, com_reservas):
    primeiro = previa(client, com_reservas)

    segundo = previa(client, com_reservas, semente=semente(primeiro), sortear="1")

    assert grupos(segundo) != grupos(primeiro)
    assert "Semente nova." in segundo


def test_mudar_a_quantidade_mantem_a_semente_e_diz(client, com_reservas):
    primeiro = previa(client, com_reservas)

    segundo = previa(client, com_reservas, semente=semente(primeiro), **{f"inscritos-{PPI}": "15"})

    assert grupos(segundo) == grupos(primeiro)
    assert "Semente mantida." in segundo
    assert "o que mudou é efeito da sua alteração, e não da sorte" in texto(segundo)
    assert "A ampla será sorteada com os 39" in texto(segundo)


def test_a_mesma_semente_e_a_mesma_populacao_dao_o_mesmo_painel(client, com_reservas):
    primeiro = previa(client, com_reservas)
    token = semente(primeiro)

    assert previa(client, com_reservas, semente=token) == previa(
        client, com_reservas, semente=token
    )


def test_o_painel_diz_cada_lista_e_a_ampla_com_todos(client, com_reservas):
    visivel = bloco(previa(client, com_reservas), "ocupacao")

    assert "todos os 30 inscritos, autodeclarados inclusive; 10 avançariam" in visivel
    assert "Pretos, pardos e indígenas (PPI): 6 autodeclarados; 3 avançariam" in visivel
    assert "Pessoa com deficiência (PCD): 4 autodeclarados; 2 avançariam" in visivel
    assert "cada lista é sorteada à parte, com a mesma semente" in visivel


def test_o_detalhe_da_reservada_diz_a_posicao_na_ampla(client, com_reservas):
    corpo = previa(client, com_reservas, vista="detalhe", recorte=PPI)
    visivel = texto(corpo)

    assert "a ordem sorteada de cada lista" in visivel
    assert len(re.findall(r"\d+ª na ampla", visivel)) == 6
    assert "a posição de alguém aqui e a posição dele na ampla são diferentes" in visivel
    assert f'<option value="{PPI}" selected>' in corpo


def test_a_lista_pedida_que_nao_existe_mostra_a_ampla_e_diz(client, com_reservas):
    visivel = texto(previa(client, com_reservas, vista="detalhe", recorte="nao-existe"))

    assert "A lista pedida não existe mais no rascunho; a prévia mostra a ampla." in visivel
    assert "ª na ampla" not in visivel


def test_menos_inscritos_que_vagas_sorteia_mesmo_assim(client, com_reservas):
    visivel = texto(
        previa(client, com_reservas, **{"inscritos-ampla": "0", f"inscritos-{PPI}": "1"})
    )

    assert "Há menos inscritos que vagas, e o sistema sorteia mesmo assim" in visivel


def test_sem_regra_de_normalizacao_a_suposta_e_dita(client, com_reservas):
    assert "a prévia supôs a da Loteria Federal" in texto(previa(client, com_reservas))


AMPLA_DECLARADA = "aaaaaaaa-0000-4000-8000-00000000e031"


@pytest.fixture
def sem_reserva(client, seletor_ligado, edital):
    """Um Perfil sem lista reservada: a Modalidade AC é a apontada como ampla, e a PcD sai."""
    from tests.interface.test_compor import eventos, perfis

    dados = perfis(
        **{
            "perfil-0-immediateVacancies": "10",
            "perfil-0-generalCompetitionModalityId": AMPLA_DECLARADA,
            "linha-0-0-id": "aaaaaaaa-0000-4000-8000-00000000e951",
            "linha-0-0-modalityId": "",
            "linha-0-0-immediateVacancies": "10",
        }
    )
    for chave in [c for c in dados if c.startswith("modalidade-0-1-")]:
        del dados[chave]
    return montar(client, edital, perfis_=dados, eventos_=eventos())


def test_perfil_sem_reserva_tem_uma_lista_e_nao_fala_de_cotas(client, sem_reserva):
    corpo = previa(client, sem_reserva)
    visivel = texto(corpo)

    assert "Este Perfil não declara reserva" in visivel
    assert 'id="recorte-da-previa"' not in previa(client, sem_reserva, vista="detalhe")
    assert "Quem concorre por uma reservada" not in visivel
    assert "rodadas com esta população" not in visivel
    # A D-005: a Modalidade apontada como ampla teria lista própria no certame, e a prévia diz.
    assert "ganha uma lista própria no sorteio do certame, e esta prévia não a sorteia" in visivel


def test_o_marco_pela_pontuacao_continua_na_previa_da_classificacao(client, com_reservas):
    corpo = previa(client, com_reservas, cartao_=do_quadro())

    assert "Simulação do processo seletivo" in corpo
    assert "Semente fictícia" not in corpo


# --- A recusa da semente que o servidor não gerou (FR-2483, SC-931) -----------------------------


@pytest.mark.parametrize("forjada", ["qualquer-coisa", "eyJtYXRlcmlhbCI6IjEyMyJ9:abc:def"])
def test_token_forjado_e_recusado_sem_ordem(client, com_reservas, forjada):
    corpo = previa(client, com_reservas, semente=forjada)
    visivel = texto(corpo)

    assert "A semente desta prévia não foi reconhecida." in visivel
    assert "Sortear de novo" in visivel
    assert "avançariam" not in visivel and "rodadas" not in visivel


def test_token_de_outro_marco_e_recusado(client, com_reservas):
    from processo_seletivo.processos.models import Edital

    edital = Edital.objects.get(pk=com_reservas.pk)
    outro = previa_do_sorteio.assinar(
        "111111 222222 333333 444444 555555",
        edital=edital,
        perfil_id=PERFIL,
        marco_id="aaaaaaaa-0000-4000-8000-0000000000ff",
    )

    assert "A semente desta prévia não foi reconhecida." in previa(
        client, com_reservas, semente=outro
    )


def test_material_e_seed_na_query_sao_ignorados(client, com_reservas):
    corpo = previa(client, com_reservas, material="111111 111111 111111 111111 111111", seed="1")

    assert grupos(corpo) != ["111111"] * 5
    assert "avançariam" in texto(corpo)


# --- US2: a ocupação da rodada e a reversão (FR-2497 a FR-2500) ---------------------------------


def test_o_bloco_da_ocupacao_e_o_da_095_marcado_como_hipotese(client, com_reservas):
    corpo = previa(client, com_reservas, **{f"inscritos-{PPI}": "20"})
    ocupacao = bloco(corpo, "ocupacao ocupacao-dos-recortes")

    assert "hipótese" in ocupacao
    assert "Quem concorre por uma reservada concorre também pela ampla" in ocupacao
    assert "Uma rodada só" in ocupacao
    # Com 20 PPI entre 44, quase certamente algum cai entre os 10 da ampla.
    assert "ocupa pela ampla" in ocupacao or "ocupam pela ampla" in ocupacao


def test_sem_regra_de_corte_ha_ordem_mas_nao_ha_ocupacao(client, com_reservas):
    corpo = previa(client, com_reservas, cartao_=cartao(**{f"{B}-cutTargetKind": ""}))
    visivel = texto(corpo)

    assert "Este marco não declara regra de corte" in visivel
    assert "ocupacao-dos-recortes" not in corpo
    assert "rodadas-do-sorteio" not in corpo


def test_reservada_sem_inscritos_diz_que_nao_seria_sorteada_nem_cedida(client, com_saldo):
    corpo = previa(client, com_saldo, **{f"inscritos-{PCD}": "0"})
    ocupacao = bloco(corpo, "ocupacao ocupacao-dos-recortes")

    assert "ninguém concorreu nesta lista na população fictícia" in texto(corpo)
    assert "não seria cedida à ampla, nem pela reversão declarada" in ocupacao
    assert "nenhuma rodada a apura: ninguém concorreu nela" in bloco(corpo, "rodadas-do-sorteio")


# --- US3: o resumo das rodadas (FR-2501 a FR-2505) ---------------------------------------------


def test_o_resumo_diz_quantas_rodadas_e_que_nao_e_previsao(client, com_reservas):
    rodadas = bloco(previa(client, com_reservas), "rodadas-do-sorteio")

    assert "Em 1.000 rodadas com esta população" in rodadas
    assert "sobraria ao menos uma vaga sem ocupante em" in rodadas
    assert "das 10 vagas da ampla seriam ocupadas por autodeclarados" in rodadas
    assert "não são previsão do certame" in rodadas
    assert "pendente de decisão na spec 095" in rodadas


def test_por_saldo_o_resumo_diz_as_cedidas(client, com_saldo):
    rodadas = bloco(previa(client, com_saldo), "rodadas-do-sorteio")

    assert "seriam cedidas à ampla" in rodadas or "seria cedida à ampla" in rodadas


def test_por_esgotamento_nada_e_cedido_e_e_comportamento_atual(client, com_esgotamento):
    rodadas = bloco(previa(client, com_esgotamento), "rodadas-do-sorteio")

    assert "nenhuma vaga seria cedida à ampla em rodada nenhuma" in rodadas
    assert "comportamento atual, pendente de decisão na spec 095" in rodadas


def test_resultado_igual_em_todas_as_rodadas_nao_vira_porcentagem(client, com_reservas):
    """Uma PPI para 3 vagas: sobra vaga em toda rodada (FR-2503)."""
    rodadas = bloco(previa(client, com_reservas, **{f"inscritos-{PPI}": "1"}), "rodadas-do-sorteio")

    assert "Pretos, pardos e indígenas (PPI): sobraria vaga sem ocupante em todas as rodadas" in (
        rodadas
    )


# --- US4: a população informada (FR-2487 a FR-2491) ---------------------------------------------


def test_a_populacao_sugerida_e_o_dobro_das_vagas(client, com_reservas):
    corpo = previa(client, com_reservas)

    assert re.search(r'id="inscritos-ampla"[^>]*value="20"', corpo)
    assert re.search(rf'id="inscritos-{PPI}"[^>]*value="6"', corpo)
    assert re.search(rf'id="inscritos-{PCD}"[^>]*value="4"', corpo)
    assert "Os números começam no dobro das vagas de cada lista" in texto(corpo)
    assert len(re.findall(r'<label for="inscritos-', corpo)) == 3


def test_valor_invalido_cai_na_sugestao_e_e_dito(client, com_reservas):
    corpo = previa(client, com_reservas, **{f"inscritos-{PPI}": "-3"})

    assert re.search(rf'id="inscritos-{PPI}"[^>]*value="6"', corpo)
    assert "a prévia usou a sugestão" in texto(corpo)


def test_acima_do_limite_nao_calcula(client, com_reservas):
    visivel = texto(previa(client, com_reservas, **{"inscritos-ampla": "595"}))

    assert "A prévia sorteia até 600 candidatos fictícios" in visivel
    assert "avançariam" not in visivel


# --- US5 e a política de conteúdo (FR-2510 a FR-2512) -------------------------------------------


def test_sem_estilo_nem_script_embutido(client, com_reservas):
    for corpo in (
        previa(client, com_reservas),
        previa(client, com_reservas, vista="detalhe", recorte=PPI),
    ):
        assert "style=" not in corpo
        assert "<style" not in corpo and "<script" not in corpo
        assert not re.search(r"\son[a-z]+=", corpo)


def test_o_anuncio_diz_se_a_semente_mudou_ou_foi_mantida(client, com_reservas):
    primeiro = previa(client, com_reservas)
    anuncio = re.search(r'id="anuncio-da-previa"[^>]*>([^<]*)<', primeiro).group(1)
    assert anuncio.startswith("Semente nova.")
    assert "Em 1.000 rodadas" in anuncio

    segundo = previa(client, com_reservas, semente=semente(primeiro))
    assert re.search(r'id="anuncio-da-previa"[^>]*>Semente mantida\.', segundo)


def test_a_semente_quebra_entre_grupos_e_nunca_dentro_de_um():
    """A 375 px, os cinco grupos empilham inteiros (FR-2510): a regra está na folha da prévia."""
    from tests.interface.folha import folha_da_pagina  # noqa: F401 — só para garantir o módulo

    folha = (
        __import__("pathlib")
        .Path(previa_do_sorteio.__file__)
        .parent.joinpath("static/interface/telas/previa-da-classificacao.css")
        .read_text(encoding="utf-8")
    )
    assert ".grupos-da-semente{display:flex;flex-wrap:wrap" in folha
    assert ".grupos-da-semente span{white-space:nowrap}" in folha


# --- Sem efeito (FR-2509, SC-930) ---------------------------------------------------------------


def test_nada_e_gravado_e_ninguem_e_lido(client, com_saldo):
    from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot

    rascunho = json.dumps(edital_snapshot(com_saldo), sort_keys=True, default=str)
    with CaptureQueriesContext(connection) as consultas:
        primeiro = previa(client, com_saldo)
        token = semente(primeiro)
        previa(client, com_saldo, semente=token, sortear="1")
        previa(client, com_saldo, semente=token, vista="detalhe", recorte=PPI)
        previa(client, com_saldo, semente=token, **{f"inscritos-{PCD}": "0"})
        client.get(reverse("interface:fragmento-previa-da-classificacao-fechar"))
    sql = [c["sql"] for c in consultas.captured_queries]
    escritas = [
        c
        for c in sql
        if re.match(r"\s*(INSERT|UPDATE|DELETE)", c, re.I) and "django_session" not in c
    ]
    assert escritas == []
    assert not [c for c in sql if '"inscricoes_' in c or '"sorteios_' in c]
    com_saldo.refresh_from_db()
    assert json.dumps(edital_snapshot(com_saldo), sort_keys=True, default=str) == rascunho


def test_o_vocabulario_nao_diz_o_que_o_ato_nao_faz(client, com_saldo):
    visivel = texto(previa(client, com_saldo)).lower()

    for palavra in ("convocad", "aprovad", "matriculad"):
        assert palavra not in visivel
