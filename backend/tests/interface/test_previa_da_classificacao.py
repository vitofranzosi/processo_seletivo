"""A prévia da classificação na etapa Classificação da composição (094).

O botão no cartão, o painel fora dele, a jornada como visão principal, o detalhe a um clique, o
recálculo sobre o que está digitado com o que mudou, e nenhuma escrita. O cálculo em si é testado em
`tests/unit/classificacao/test_previa.py` e a equivalência com o caminho oficial em
`tests/integration/classificacao/test_previa_equivale_ao_oficial.py`; aqui se confere a tela.
"""

import json
import re

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from tests.interface.conftest import ETAPA_CLASSIFICATORIA, ETAPA_SO_ELIMINATORIA, identificar
from tests.interface.folha import folha_da_pagina
from tests.interface.test_compor import PERFIL

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

MARCO = "aaaaaaaa-0000-4000-8000-00000000e051"
B = f"marco-{PERFIL}-0"


def marco_form(**alteracoes):
    """O cartão do marco como o formulário o envia — pela pontuação, com corte para a Análise."""
    base = {
        "perfil_id": PERFIL,
        f"{B}-id": MARCO,
        f"{B}-code": "PARCIAL",
        f"{B}-name": "Classificação para a análise",
        f"{B}-orderProduction": "POR_PONTUACAO",
        f"{B}-stages": ETAPA_CLASSIFICATORIA,
        f"{B}-operation": "SOMA_PONDERADA",
        f"{B}-normalization": "NENHUMA",
        f"{B}-scale": "2",
        f"{B}-mode": "MEIO_PARA_CIMA",
        f"criterio-{PERFIL}-0-0-order": "1",
        f"criterio-{PERFIL}-0-0-type": "MAIOR_PONTUACAO_NA_ETAPA",
        f"criterio-{PERFIL}-0-0-target": ETAPA_CLASSIFICATORIA,
        f"criterio-{PERFIL}-0-0-whenMissing": "ULTIMO_NO_CRITERIO",
        f"{B}-cutTargetKind": "FIXED",
        f"{B}-cutTargetCount": "10",
        f"{B}-cutSurplusCount": "5",
        f"{B}-cutTieOutcome": "ADMITS_SURPLUS",
        f"{B}-cutGovernedStage": ETAPA_SO_ELIMINATORIA,
        f"{B}-cutContinuation": "ALLOWED",
    }
    return {**base, **alteracoes}


@pytest.fixture
def com_marco(client, com_etapas):
    resposta = client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]), marco_form()
    )
    assert resposta.status_code == 302, resposta.content
    com_etapas.refresh_from_db()
    return com_etapas


def previa(client, edital, **dados):
    url = reverse("interface:fragmento-previa-da-classificacao", args=[PERFIL, "0"])
    resposta = client.get(url, {"edital": str(edital.id), **marco_form(), **dados})
    assert resposta.status_code == 200, resposta.content
    return resposta.content.decode()


def texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


# --- O acesso: o botão no cartão, o painel fora dele (FR-2200 a FR-2203) -----------------------


def test_o_botao_esta_no_cartao_do_marco_pela_pontuacao(client, com_marco):
    pagina = client.get(reverse("interface:compor-etapa", args=[com_marco.id, "classificacao"]))
    corpo = pagina.content.decode()
    assert "Simular classificação" in corpo
    assert 'aria-controls="painel-da-previa"' in corpo
    assert f'hx-include="#cartao-{PERFIL}"' in corpo


def test_o_botao_nao_aparece_no_marco_por_sorteio(client, com_marco):
    """Emendada pela `098` (FR-2477): o marco por sorteio ganha o botão dele, e não este."""
    cartao = client.get(
        reverse("interface:fragmento-marco-recomposto", args=[PERFIL, "0"]),
        {"edital": str(com_marco.id), **marco_form(**{f"{B}-orderProduction": "POR_SORTEIO"})},
    ).content.decode()
    assert "Simular classificação" not in cartao
    assert "Simular sorteio" in cartao


def test_o_painel_mora_fora_do_formulario_e_de_todo_cartao(client, com_marco):
    corpo = client.get(
        reverse("interface:compor-etapa", args=[com_marco.id, "classificacao"])
    ).content.decode()
    fim_do_formulario = corpo.index("</form>")
    painel = corpo.index('id="painel-da-previa"')
    assert painel > fim_do_formulario
    assert "previa-da-classificacao.css" in corpo and "previa-da-classificacao.js" in corpo


# --- A jornada: a visão principal (FR-2247 a FR-2255) -----------------------------------------


def test_a_jornada_abre_com_as_etapas_reais_e_o_marco_aberto(client, com_marco):
    corpo = previa(client, com_marco)
    visivel = texto(corpo)
    assert "Simulação do processo seletivo" in visivel
    assert "Exemplo fictício" in visivel
    assert "TEC-ADM" in visivel, "o Perfil é nomeado (FR-2255)"
    assert "Prova didática" in visivel and "Análise documental" in visivel
    assert "Classificação para a análise" in visivel
    assert "Avançariam" in visivel and "Não avançariam nesta faixa" in visivel
    assert "poderiam participar" in visivel
    assert "Explorar classificação e desempate" in visivel
    assert "O que esta prévia simula, e o que não" in visivel
    assert visivel.index("Simulação do processo seletivo") < visivel.index("Avançariam")


def test_a_etapa_alimentada_diz_que_as_notas_dela_nao_sao_simuladas(client, com_marco):
    visivel = texto(previa(client, com_marco))
    assert "As notas da Análise documental não são simuladas aqui." in visivel
    assert "quem chega é calculado" in visivel


def test_a_manchete_nao_separa_a_pontuacao(client, com_marco):
    """O negrito e o resto se juntam com um espaço, e o resto não pode começar por vírgula."""
    corpo = previa(client, com_marco, vista="detalhe")
    manchete = re.search(r'<p class="manchete[^>]*>(.*?)</p>', corpo, re.S).group(1)
    assert not re.search(r"\s[,.;]", re.sub(r"<[^>]+>", "", manchete))


def test_o_detalhe_esta_a_um_clique_e_volta(client, com_marco):
    detalhe = texto(previa(client, com_marco, vista="detalhe"))
    assert "classificação e desempate" in detalhe
    assert "Voltar ao processo" in detalhe
    assert "Quem está perto dos limites" in detalhe
    assert "Linha do alvo (10)" in detalhe
    assert "Linha do fim da faixa (10 + 5 suplentes)" in detalhe
    assert "Depois do corte: a apuração das vagas" in detalhe and "hipótese" in detalhe
    assert "Classificação completa" in detalhe
    assert "Como a prévia chega a este resultado" in detalhe


# --- Recálculo, população e o que mudou (FR-2223, FR-2243, FR-2244) ----------------------------


def _oculto(corpo, nome):
    return re.search(rf'name="{nome}" value="([^"]*)"', corpo).group(1)


def test_mudar_o_desfecho_recalcula_sobre_a_mesma_populacao_e_diz_o_que_mudou(client, com_marco):
    primeiro = previa(client, com_marco)
    populacao, anterior = _oculto(primeiro, "populacao"), _oculto(primeiro, "anterior")
    segundo = previa(
        client,
        com_marco,
        populacao=populacao,
        anterior=anterior,
        **{f"{B}-cutTieOutcome": "STRICT"},
    )
    assert _oculto(segundo, "populacao") == populacao
    visivel = texto(segundo)
    assert "O que mudou com a sua alteração" in visivel
    assert "Ninguém avançaria por enquanto." in visivel
    assert "Corte: emitível → impedido na 15ª." in visivel


def test_alteracao_sem_efeito_diz_que_nada_mudou(client, com_marco):
    primeiro = previa(client, com_marco)
    segundo = previa(
        client,
        com_marco,
        populacao=_oculto(primeiro, "populacao"),
        anterior=_oculto(primeiro, "anterior"),
        **{f"{B}-cutContinuation": "NONE"},
    )
    assert "a consequência não mudou para ninguém" in texto(segundo)


def test_mudar_o_alvo_mantem_a_populacao_e_oferece_remontar(client, com_marco):
    primeiro = previa(client, com_marco)
    segundo = previa(
        client,
        com_marco,
        populacao=_oculto(primeiro, "populacao"),
        **{f"{B}-cutTargetCount": "30"},
    )
    assert _oculto(segundo, "populacao") == _oculto(primeiro, "populacao")
    assert "Remontar para esta configuração" in texto(segundo)


def test_o_caso_limite_avisa_que_acompanha_a_fronteira(client, com_marco):
    visivel = texto(previa(client, com_marco, candidatos="caso:empate_na_faixa"))
    assert "Caso construído para demonstração" in visivel


def test_campo_apagado_diz_o_que_falta(client, com_marco):
    visivel = texto(previa(client, com_marco, **{f"{B}-cutTargetCount": ""}))
    assert "A prévia ainda não calcula." in visivel
    assert "Declare o alvo" in visivel


def test_marco_por_sorteio_pedido_a_mao_responde_a_previa_do_sorteio(client, com_marco):
    """Emendada pela `098` (R-010): antes a resposta era "fora da fatia"; agora a mesma rota
    despacha pela forma, e o marco por sorteio recebe a prévia dele, com semente fictícia."""
    visivel = texto(previa(client, com_marco, **{f"{B}-orderProduction": "POR_SORTEIO"}))
    assert "A prévia cobre marcos que ordenam pela pontuação." not in visivel
    assert "Simulação do sorteio" in visivel
    assert "Semente fictícia" in visivel


# --- Vocabulário, comportamento atual e CSP (FR-2229, FR-2237, FR-2245) ------------------------


def test_o_rotulo_do_desfecho_no_cartao_continua_o_de_hoje(client, com_marco):
    """A prévia não decide a DP-1: o rótulo de `STRICT` no cartão é o mesmo."""
    corpo = client.get(
        reverse("interface:compor-etapa", args=[com_marco.id, "classificacao"])
    ).content.decode()
    assert "A faixa para no alvo" in corpo


def test_suplente_nao_e_situacao_de_candidato(client, com_marco):
    detalhe = previa(client, com_marco, vista="detalhe")
    assert not re.search(r'class="marca[^"]*">\s*Suplente', detalhe)
    assert "Dentro do alvo" not in detalhe
    assert "comportamento atual do sistema" in texto(detalhe)


@pytest.mark.parametrize("vista", ["processo", "detalhe"])
def test_nada_escrito_no_modelo_que_a_csp_recusaria(client, com_marco, vista):
    corpo = previa(client, com_marco, vista=vista)
    assert not re.search(r"\sstyle=|<style|<script|\son[a-z]+=", corpo, re.I)


def test_no_estreito_o_painel_cobre_a_tela_e_as_linhas_viram_blocos(client, com_marco):
    """SC-846, pela folha que a página aplica: abaixo de 64rem o painel é a tela inteira, com
    rolagem própria, e a 40rem as tabelas deixam de ter colunas — é o que segura os 375 px sem
    rolagem lateral, conferidos no navegador em 20/10 (`capturas-da-interface/`)."""
    folha = re.sub(
        r"\s+",
        "",
        folha_da_pagina(
            client, reverse("interface:compor-etapa", args=[com_marco.id, "classificacao"])
        ),
    )
    # A folha comum também tem blocos desses: o da prévia é o que fala do painel.
    estreito = "".join(re.findall(r"@medianotalland\(min-width:64rem\)\{(.*?)\}\}", folha))
    assert ".painel-da-previa:has(>*){position:fixed;inset:0" in estreito
    assert "overflow:auto" in estreito
    celular = "".join(re.findall(r"@media\(max-width:40rem\)\{(.*?)\}\}", folha))
    assert ".painel-da-previa.fronteirathead,.painel-da-previa.detalhadathead{display:none}" in (
        celular
    )
    assert "white-space:normal" in celular


def test_o_resumo_e_anunciado_fora_de_banda(client, com_marco):
    corpo = previa(client, com_marco)
    assert 'id="anuncio-da-previa"' in corpo and 'hx-swap-oob="true"' in corpo
    assert 'aria-label="A jornada dos candidatos neste Perfil"' in corpo


# --- Sem efeito, e a mesma autorização (FR-2234, FR-2235) --------------------------------------


def test_abrir_recalcular_e_fechar_nao_escrevem_nada(client, com_marco):
    rascunho = json.dumps(edital_snapshot(com_marco), sort_keys=True, default=str)
    with CaptureQueriesContext(connection) as consultas:
        primeiro = previa(client, com_marco)
        previa(
            client,
            com_marco,
            anterior=_oculto(primeiro, "anterior"),
            populacao=_oculto(primeiro, "populacao"),
            **{f"{B}-cutTieOutcome": "STRICT"},
        )
        previa(client, com_marco, vista="detalhe", candidatos="caso:valor_ausente")
        client.get(reverse("interface:fragmento-previa-da-classificacao-fechar"))
    escritas = [
        c["sql"]
        for c in consultas.captured_queries
        if re.match(r"\s*(INSERT|UPDATE|DELETE)", c["sql"], re.I)
        and "django_session" not in c["sql"]
    ]
    assert escritas == []
    # O rascunho que a prévia lê sai igual, byte a byte (SC-843).
    com_marco.refresh_from_db()
    assert json.dumps(edital_snapshot(com_marco), sort_keys=True, default=str) == rascunho


def test_o_recalculo_custa_as_mesmas_consultas_que_a_abertura(client, com_marco):
    """O cálculo é em memória (SC-841): quem digita não paga consulta a mais por recálculo, nem
    por um caso-limite maior. O número é o do snapshot do rascunho e da sessão, e só."""

    def consultas(**dados):
        with CaptureQueriesContext(connection) as capturadas:
            previa(client, com_marco, **dados)
        return len(capturadas.captured_queries)

    primeiro = previa(client, com_marco)
    abertura = consultas()
    assert (
        consultas(
            populacao=_oculto(primeiro, "populacao"),
            anterior=_oculto(primeiro, "anterior"),
            **{f"{B}-cutTieOutcome": "STRICT"},
        )
        == abertura
    )
    assert consultas(**{f"{B}-cutTargetCount": "400", f"{B}-cutSurplusCount": "100"}) == abertura
    assert consultas(vista="detalhe", candidatos="caso:valor_ausente") == abertura


def test_edital_fora_do_escopo_recebe_404(client, com_marco):
    identificar(client, "outra.elaboradora", ["elaborador"], escopo="outro-instituto")
    url = reverse("interface:fragmento-previa-da-classificacao", args=[PERFIL, "0"])
    resposta = client.get(url, {"edital": str(com_marco.id), **marco_form()})
    assert resposta.status_code == 404


def test_sem_edital_na_query_nao_ha_o_que_simular(client, com_marco):
    url = reverse("interface:fragmento-previa-da-classificacao", args=[PERFIL, "0"])
    assert client.get(url, marco_form()).status_code == 204
