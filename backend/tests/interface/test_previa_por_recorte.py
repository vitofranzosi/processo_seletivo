"""A prévia da classificação com recortes, concomitância e ocupação das vagas (095).

O Perfil declara PPI e PcD, com 10 vagas na linha geral, 3 na PPI e 2 na PcD, e o marco corta pelo
quadro. O cálculo é testado em `tests/unit/classificacao/test_previa_por_recorte.py` e a
equivalência com o caminho oficial em
`tests/integration/classificacao/test_previa_por_recorte_equivale_ao_oficial.py`; aqui se confere a
tela: o resumo por recorte na jornada, o seletor no detalhe, o bloco da ocupação, a reversão e as
marcas das linhas.
"""

import re

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from tests.interface.conftest import (
    ETAPA_CLASSIFICATORIA,
    ETAPA_SO_ELIMINATORIA,
    FATO_DO_DESEMPATE,
    compor_rascunho,
    identificar,
)
from tests.interface.test_compor import PERFIL
from tests.interface.test_previa_da_classificacao import B, marco_form

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

PPI = "aaaaaaaa-0000-4000-8000-00000000e931"
PCD = "aaaaaaaa-0000-4000-8000-00000000e932"


def perfis_com_reserva(reversao=""):
    from tests.interface.test_compor import perfis

    return perfis(
        **{
            "perfil-0-immediateVacancies": "15",
            "perfil-0-vacancyReversion": reversao,
            "modalidade-0-0-id": PPI,
            "modalidade-0-0-code": "PPI",
            "modalidade-0-0-name": "Pretos, pardos e indígenas",
            "modalidade-0-1-id": PCD,
            "linha-0-0-id": "aaaaaaaa-0000-4000-8000-00000000e941",
            "linha-0-0-modalityId": "",
            "linha-0-0-immediateVacancies": "10",
            "linha-0-1-id": "aaaaaaaa-0000-4000-8000-00000000e942",
            "linha-0-1-modalityId": PPI,
            "linha-0-1-immediateVacancies": "3",
            "linha-0-2-id": "aaaaaaaa-0000-4000-8000-00000000e943",
            "linha-0-2-modalityId": PCD,
            "linha-0-2-immediateVacancies": "2",
            "fato-0-0-id": FATO_DO_DESEMPATE,
            "fato-0-0-code": "EXPERIENCIA",
            "fato-0-0-label": "Meses de experiência em EaD",
            "fato-0-0-type": "INTEIRO",
        }
    )


def do_quadro(**alteracoes):
    """O cartão com o alvo do quadro e sem suplentes: cada recorte corta nas vagas da linha dele."""
    return marco_form(
        **{
            f"{B}-cutTargetKind": "FROM_VACANCY_TABLE",
            f"{B}-cutTargetCount": "",
            f"{B}-cutSurplusCount": "0",
            **alteracoes,
        }
    )


def montar(client, edital, reversao=""):
    from tests.interface.test_compor import EVENTO, eventos

    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis=perfis_com_reserva(reversao), eventos=eventos())
    edital.refresh_from_db()
    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital.id, "etapas"]),
        {
            "etapa-0-id": ETAPA_CLASSIFICATORIA,
            "etapa-0-name": "Prova didática",
            "etapa-0-order": "1",
            "etapa-0-weight": "2",
            "etapa-0-classificatory": "on",
            "etapa-0-scheduleEventId": EVENTO,
            "etapa-1-id": ETAPA_SO_ELIMINATORIA,
            "etapa-1-name": "Análise documental",
            "etapa-1-order": "2",
            "etapa-1-weight": "1",
            "etapa-1-eliminatory": "on",
            "etapa-1-scheduleEventId": "",
        },
    )
    assert resposta.status_code == 302, resposta.content
    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital.id, "classificacao"]), do_quadro()
    )
    assert resposta.status_code == 302, resposta.content
    edital.refresh_from_db()
    return edital


@pytest.fixture
def com_reservas(client, seletor_ligado, edital):
    return montar(client, edital)


@pytest.fixture
def com_saldo(client, seletor_ligado, edital):
    return montar(client, edital, "ON_BALANCE")


@pytest.fixture
def com_esgotamento(client, seletor_ligado, edital):
    return montar(client, edital, "ON_EXHAUSTION")


def previa(client, edital, cartao=None, **dados):
    url = reverse("interface:fragmento-previa-da-classificacao", args=[PERFIL, "0"])
    resposta = client.get(url, {"edital": str(edital.id), **(cartao or do_quadro()), **dados})
    assert resposta.status_code == 200, resposta.content
    return resposta.content.decode()


def texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _oculto(corpo, nome):
    return re.search(rf'name="{nome}" value="([^"]*)"', corpo).group(1)


CONCOMITANTE = {"candidatos": "caso:concomitante"}


# --- A jornada: um resumo por recorte e a união na Etapa seguinte (FR-2310 a FR-2312) ----------


def test_o_marco_mostra_um_resumo_por_recorte(client, com_reservas):
    corpo = previa(client, com_reservas)
    visivel = texto(corpo.split('class="recortes-do-marco"')[1].split("</ul>")[0])
    ampla = visivel.index("Ampla concorrência (linha geral do quadro), todos os candidatos:")
    pcd = visivel.index("Pessoa com deficiência (PCD):")
    ppi = visivel.index("Pretos, pardos e indígenas (PPI):")
    assert ampla < pcd < ppi, "na ordem da derivação oficial (FR-2301)"
    assert "autodeclarados" in visivel


def test_a_etapa_seguinte_recebe_a_uniao_das_faixas(client, com_reservas):
    visivel = texto(previa(client, com_reservas, **CONCOMITANTE))
    assert "poderiam participar" in visivel
    assert "que só a faixa de uma reservada alcança" in visivel
    assert "Quem está em duas faixas conta uma vez." in visivel


def test_a_ocupacao_fica_fora_da_sequencia_e_e_hipotese(client, com_reservas):
    corpo = previa(client, com_reservas)
    fim_da_jornada = corpo.index("</ol>", corpo.index('class="jornada"'))
    bloco = corpo.index('id="titulo-ocupacao-dos-recortes"')
    assert bloco > fim_da_jornada
    assert "hipótese" in texto(corpo[bloco:])


def test_o_empate_da_ultima_vaga_da_ampla_para_as_reservadas_e_o_painel_diz_como_ver(
    client, com_reservas
):
    """A população estável planta um empate na última vaga da ampla (decisão 003 da 094), e o motor
    não apura as reservadas sem saber quem ocupa pela ampla."""
    visivel = texto(previa(client, com_reservas))
    assert "Pararia na 10ª posição" in visivel
    assert "depende de quem ocupa pela ampla" in visivel
    assert "“Autodeclarado dentro das vagas da ampla”" in visivel
    assert not re.search(r"Pessoa com deficiência \(PCD\): \d+ publicadas", visivel)


# --- A concomitância e a ocupação (FR-2316 a FR-2325) -----------------------------------------


def test_quem_ocupa_pela_ampla_nao_conta_na_reservada(client, com_reservas):
    visivel = texto(previa(client, com_reservas, **CONCOMITANTE))
    assert "ocupa pela ampla: não conta aqui, e a vaga reservada continua de" in visivel
    assert "Vale para todo Perfil com reserva, e não é campo do Edital." in visivel
    assert "publicadas" in visivel and "sem ocupante nesta hipótese" in visivel


def test_a_faixa_tomada_pela_ampla_e_dita_como_comportamento_atual(client, com_reservas):
    visivel = texto(previa(client, com_reservas, **CONCOMITANTE))
    assert "são de quem ocupa pela ampla" in visivel or "é de quem ocupa pela ampla" in visivel
    assert "faixa seguinte, que a prévia não simula" in visivel
    assert "É como o sistema calcula hoje" in visivel


# --- A reversão (FR-2326 a FR-2330) ------------------------------------------------------------


def test_sem_reversao_declarada_a_vaga_continua_reservada(client, com_reservas):
    visivel = texto(previa(client, com_reservas, **CONCOMITANTE))
    assert "Este Perfil não declara reversão" in visivel
    assert "cedida" not in visivel


def test_por_saldo_diz_o_que_seria_cedido_e_nao_refaz_a_ampla(client, com_saldo):
    visivel = texto(previa(client, com_saldo, **CONCOMITANTE))
    assert "Pela reversão declarada, “A quantidade que ficou sem preencher”" in visivel
    assert "cedida à ampla concorrência deste Perfil" in visivel
    assert "A próxima apuração da ampla leria" in visivel and "a prévia não a refaz" in visivel


def test_por_esgotamento_e_o_comportamento_atual(client, com_esgotamento):
    visivel = texto(previa(client, com_esgotamento, **CONCOMITANTE))
    assert "“Só quando a lista reservada esgota”" in visivel
    assert "nenhuma vaga seria cedida" in visivel
    assert "a conta inclui quem ocupa pela ampla" in visivel
    assert "comportamento atual do sistema" in visivel


# --- O detalhe: o seletor e as marcas (FR-2313 a FR-2315) -------------------------------------


def test_o_detalhe_tem_um_seletor_nativo_com_a_ampla_escolhida(client, com_reservas):
    corpo = previa(client, com_reservas, vista="detalhe")
    assert '<label for="recorte-da-previa">Recorte</label>' in corpo
    assert '<select id="recorte-da-previa" name="recorte"' in corpo
    assert re.search(r'<option value="" selected>Ampla concorrência', corpo)
    assert "Modalidade" in texto(corpo), "a coluna da Modalidade na classificação completa"


def test_na_reservada_cada_linha_diz_a_posicao_na_ampla_e_quem_ocuparia_por_ela(
    client, com_reservas
):
    corpo = previa(client, com_reservas, vista="detalhe", recorte=PCD, **CONCOMITANTE)
    visivel = texto(corpo)
    assert re.search(rf'<option value="{PCD}" selected>', corpo)
    assert "na ampla" in visivel
    assert "ocuparia pela ampla" in visivel
    assert "Na ampla" in visivel, "a coluna da posição na ampla na classificação completa"


def test_o_recalculo_mantem_o_recorte_em_vista(client, com_reservas):
    corpo = previa(client, com_reservas, vista="detalhe", recorte=PCD)
    assert "#recorte-da-previa" in corpo.split('class="recalculo"')[1].split(">")[0]


def test_recorte_que_nao_existe_volta_a_ampla_e_diz(client, com_reservas):
    visivel = texto(
        previa(
            client, com_reservas, vista="detalhe", recorte="aaaaaaaa-0000-4000-8000-000000000000"
        )
    )
    assert "O recorte pedido não existe mais no rascunho" in visivel


def test_alvo_fixo_diz_os_dois_numeros_na_reservada(client, com_reservas):
    cartao = do_quadro(**{f"{B}-cutTargetKind": "FIXED", f"{B}-cutTargetCount": "10"})
    visivel = texto(previa(client, com_reservas, cartao, vista="detalhe", recorte=PCD))
    assert "o alvo fixo vale em todo recorte: a faixa é de 10" in visivel
    assert "esta reservada tem 2 vagas na linha dela" in visivel


# --- Os casos-limite, o que mudou e o anúncio (FR-2332, FR-2334, FR-2344) ---------------------


def test_os_casos_de_reserva_estao_no_seletor(client, com_reservas):
    corpo = previa(client, com_reservas)
    assert 'label="Caso-limite de reserva — demonstração dirigida"' in corpo
    assert "Reserva sem autodeclarados" in texto(corpo)


def test_reserva_vazia_nao_parece_pendencia(client, com_reservas):
    visivel = texto(previa(client, com_reservas, candidatos="caso:reserva_vazia"))
    assert "ninguém concorreu neste recorte na população fictícia" in visivel


def test_mudar_o_desfecho_diz_o_que_mudou_no_recorte(client, com_reservas):
    caso = {"candidatos": "caso:empate_vaga_reservada"}
    primeiro = previa(client, com_reservas, **caso)
    segundo = previa(
        client,
        com_reservas,
        do_quadro(**{f"{B}-cutTieOutcome": "STRICT"}),
        anterior=_oculto(primeiro, "anterior"),
        **caso,
    )
    assert "Pessoa com deficiência (PCD): corte emitível → impedido" in texto(segundo)


def test_o_anuncio_tem_o_resumo_de_cada_recorte(client, com_reservas):
    corpo = previa(client, com_reservas)
    anuncio = re.search(r'id="anuncio-da-previa"[^>]*>(.*?)</p>', corpo, re.S).group(1)
    assert (
        "Pessoa com deficiência (PCD):" in anuncio
        and "Pretos, pardos e indígenas (PPI):" in anuncio
    )


@pytest.mark.parametrize("vista", ["processo", "detalhe"])
def test_nada_escrito_no_modelo_que_a_csp_recusaria(client, com_saldo, vista):
    corpo = previa(client, com_saldo, vista=vista, recorte=PCD, **CONCOMITANTE)
    assert not re.search(r"\sstyle=|<style|<script|\son[a-z]+=", corpo, re.I)


# --- Sem efeito e sem dado real (FR-2341, FR-2342) --------------------------------------------


def test_abrir_trocar_recorte_e_recalcular_nao_escrevem_nem_leem_inscricao(client, com_saldo):
    import json

    from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot

    rascunho = json.dumps(edital_snapshot(com_saldo), sort_keys=True, default=str)
    with CaptureQueriesContext(connection) as consultas:
        primeiro = previa(client, com_saldo, **CONCOMITANTE)
        previa(client, com_saldo, vista="detalhe", recorte=PPI, **CONCOMITANTE)
        previa(
            client,
            com_saldo,
            anterior=_oculto(primeiro, "anterior"),
            **{**CONCOMITANTE, f"{B}-cutTieOutcome": "STRICT"},
        )
    sql = [c["sql"] for c in consultas.captured_queries]
    escritas = [
        c
        for c in sql
        if re.match(r"\s*(INSERT|UPDATE|DELETE)", c, re.I) and "django_session" not in c
    ]
    assert escritas == []
    # Nenhuma inscrição, autodeclaração, fato congelado ou documento de candidato é lido: os
    # documentos exigidos que o snapshot lê são configuração do Edital, e não de ninguém.
    assert not [c for c in sql if '"inscricoes_' in c]
    com_saldo.refresh_from_db()
    assert json.dumps(edital_snapshot(com_saldo), sort_keys=True, default=str) == rascunho
