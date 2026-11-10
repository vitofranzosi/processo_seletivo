"""O Centro de Controle nos cenários de treinamento da `134` (136, SC-1471 a SC-1475).

**Os cenários são os do estudo** — C06 (sorteio antes do congelamento), C08 (resultado preliminar e
prazo de recurso) e C12 (conferência documental) — e os papéis são os quatro que o plano de produção
pede: presidência, avaliação, Gestor e Publicador. Cada caso monta **um** cenário pelo comando de
carga (dois no mesmo banco colidem) e lê a mesma página com as quatro identidades.

**A página é conferida no HTML**, e não só no contexto: "quem não vê a matriz não recebe a tabela"
é uma promessa sobre o que chega ao navegador.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.interface import andamento as a
from processo_seletivo.interface import conceitos as c
from processo_seletivo.processos.models import Edital
from processo_seletivo.treinamento import construcao as k
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.treinamento import carregar
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

PAPEIS = {
    "presidência": (k.PRESIDENCIA, []),
    "avaliação": (k.AVALIACAO_1, []),
    "Gestor": (k.GESTAO, ["gestor"]),
    "Publicador": (k.PUBLICACAO, ["publicador"]),
}
#: Quem conduz ou audita vê o detalhe por lista (a regra da `127`, D-007).
VEEM_A_MATRIZ = {"presidência", "Gestor"}


@pytest.fixture
def cenario(treinamento):
    treinamento.INTERFACE_SELETOR_IDENTIDADE = True

    def montar(codigo):
        saida = carregar(codigo, autoridade=str(AUTORIDADE_DA_SUITE))
        assert f"{codigo}  CRIADO" in saida, saida
        manifesto = CenarioDeTreinamento.objects.get(codigo=codigo)
        return Edital.objects.get(processo=manifesto.processo)

    return montar


def abrir(client, edital, papel, fase=None):
    identificar(client, *PAPEIS[papel])
    url = reverse("interface:detalhe", args=[edital.id])
    resposta = client.get(url + (f"?fase={fase}" if fase else ""))
    assert resposta.status_code == 200, (papel, resposta.status_code)
    return resposta


def html(resposta):
    return resposta.content.decode()


def mapa(texto):
    """O mapa só: a barra lateral também usa `aria-current`, para a seção em que se está."""
    return texto.split('<nav class="cc-mapa"', 1)[1].split("</nav>", 1)[0]


def cartao_da_fase(texto, chave):
    achado = re.search(rf'<li class="cc-fase[^"]*" data-fase="{chave}".*?</li>', texto, re.S)
    assert achado, chave
    return achado.group(0)


def conferir_coerencia(resposta):
    """SC-1473: o mapa e as providências dizem o mesmo que o `Andamento`."""
    centro, dados = resposta.context["centro"], resposta.context["andamento"]
    texto = html(resposta)
    assert sum(len(f.providencias) for f in centro.fases) == dados.nivel_1.total
    for fase in centro.fases:
        tem_sua = any(i.p.grupo == "sua" for i in fase.providencias)
        assert bool(fase.suas) == tem_sua, fase.chave
        assert ('class="cc-marca sua"' in cartao_da_fase(texto, fase.chave)) == tem_sua, fase.chave
        for fp in fase.perfis:
            for lista in fp.listas:
                celulas = [cn.celula for cn in lista.celulas]
                concluida = lista.andamento == c.CONCLUIDA
                assert concluida == (
                    bool(celulas)
                    and all(x.situacao in (a.FEITO, a.NAO_SE_APLICA) for x in celulas)
                    and any(x.situacao == a.FEITO for x in celulas)
                ), (fase.chave, lista.rotulo)


def conferir_papel(resposta, papel):
    """O que cada papel recebe, e o que não recebe (SC-1474)."""
    texto, centro = html(resposta), resposta.context["centro"]
    ve = papel in VEEM_A_MATRIZ
    assert centro.ve_a_matriz == ve, papel
    assert ('aria-labelledby="listas-titulo"' in texto) == ve, papel
    assert ('class="cc-tabela-da-fase"' in texto) == ve, papel
    assert ('class="cc-roteiro"' in texto) == ve, papel
    assert ('class="cc-tabela-das-listas"' in texto) == ve, papel
    if centro.total and not centro.suas:
        assert "Nenhuma ação é sua agora." in texto, papel
    if centro.suas:
        assert "Nenhuma ação é sua agora." not in texto, papel
    terminais = resposta.context["grupo"].terminais
    assert ('<details class="cc-terminais">' in texto) == bool(terminais), papel
    if terminais:
        recolhido = texto.split('<details class="cc-terminais">', 1)[1].split("</details>", 1)[0]
        for acao in terminais:
            assert acao.rotulo in recolhido
    # A fase consultada é a única com `true`; nenhuma leva `step`, que diria "o passo atual".
    assert mapa(texto).count('aria-current="true"') == 1, papel
    assert 'aria-current="step"' not in texto, papel
    conferir_coerencia(resposta)


# ---------------------------------------------------------------------------------------------
# C06 — sorteio antes do congelamento
# ---------------------------------------------------------------------------------------------


def test_c06(client, cenario):
    """Um cenário por caso: a carga custa perto de um minuto, e dois no mesmo banco colidem."""
    edital = cenario("C06")
    c06_destaca_fixar_os_participantes_e_diz_por_que(client, edital)
    for papel in PAPEIS:
        conferir_papel(abrir(client, edital, papel), papel)
    c06_quem_nao_pratica_nao_recebe_o_link_e_a_tela_real_recusa(client, edital)


def c06_destaca_fixar_os_participantes_e_diz_por_que(client, edital):
    """SC-1471, US2: a regra 2 do destaque, com os passos que esperam por ela."""
    resposta = abrir(client, edital, "presidência")
    texto, centro = html(resposta), resposta.context["centro"]

    assert centro.destaque.item.titulo == "Fixar os participantes"
    destaque = texto.split('<article class="cc-destaque"', 1)[1].split("</article>", 1)[0]
    assert "Sua próxima ação · Classificação" in destaque
    assert "<strong>Por que esta:</strong>" in destaque
    assert "Esperam por ela: Obter a semente pública → Realizar o sorteio." in destaque
    assert "no GPS: congelar a relação" in destaque
    assert f'href="{centro.destaque.item.p.url}"' in destaque
    assert c.PARALELA in texto, "a Etapa de títulos não segura o sorteio"
    # US3: a fase consultada, sem pedido, é a da ação em destaque.
    assert resposta.context["fase"].chave == c.CLASSIFICACAO
    assert "Ainda não começou: nenhuma relação deste marco está congelada" in texto


def c06_quem_nao_pratica_nao_recebe_o_link_e_a_tela_real_recusa(client, edital):
    """SC-1475, FR-4707: o link é da providência, e a tela do ato continua sendo quem recusa."""
    url = abrir(client, edital, "presidência").context["centro"].destaque.item.p.url
    assert url

    resposta = abrir(client, edital, "avaliação")
    assert f'href="{url}"' not in html(resposta)
    assert client.get(url).status_code in (403, 404)


# ---------------------------------------------------------------------------------------------
# C08 — resultado preliminar e prazo de recurso
# ---------------------------------------------------------------------------------------------


def test_c08(client, cenario):
    edital = cenario("C08")
    c08_destaca_classificar_a_lista(client, edital)
    for papel in PAPEIS:
        conferir_papel(abrir(client, edital, papel), papel)


def c08_destaca_classificar_a_lista(client, edital):
    """SC-1471: a única ação da presidência. A menção à lista sem inscritos é da `135`."""
    resposta = abrir(client, edital, "presidência")
    centro = resposta.context["centro"]

    assert len(centro.suas) == 1
    assert centro.destaque.item.titulo == "Classificar a lista"
    assert centro.destaque.porque == c.PORQUE_UNICA
    assert "É a única ação sua disponível agora." in html(resposta)
    # O corte espera o prazo de recurso: a marca de espera diz até quando.
    assert centro.aguardando


# ---------------------------------------------------------------------------------------------
# C12 — conferência documental
# ---------------------------------------------------------------------------------------------


def test_c12(client, cenario):
    edital = cenario("C12")
    c12_nao_destaca_e_diz_que_o_gps_nao_escolhe_a_ordem(client, edital)
    c12_classificacao_consultada_e_convocacao_em_curso_sao_distintas(client, edital)
    c12_a_lista_ppp_aparece_com_o_que_falta_nela(client, edital)
    for papel in PAPEIS:
        conferir_papel(abrir(client, edital, papel), papel)


def c12_nao_destaca_e_diz_que_o_gps_nao_escolhe_a_ordem(client, edital):
    resposta = abrir(client, edital, "presidência")
    texto, centro = html(resposta), resposta.context["centro"]

    assert centro.destaque is None
    assert '<article class="cc-destaque"' not in texto
    assert "o GPS não escolhe a ordem entre elas" in texto
    assert len(centro.suas) >= 2
    assert "Onde estamos" in texto and "aguardam prazo ou resposta" in centro.onde_detalhe


def c12_classificacao_consultada_e_convocacao_em_curso_sao_distintas(client, edital):
    """SC-1472, FR-4731: a fase consultada não é uma fase do Edital."""
    texto = html(abrir(client, edital, "presidência", fase="classificacao"))

    classificacao = cartao_da_fase(texto, "classificacao")
    convocacao = cartao_da_fase(texto, "convocacao")
    assert " consultada" in classificacao.split(">", 1)[0]
    assert 'aria-current="true"' in classificacao
    assert '<span class="oculto">fase consultada: </span>' in classificacao
    assert 'data-andamento="em_curso"' in convocacao
    assert "aria-current" not in convocacao and "consultada" not in convocacao
    assert mapa(texto).count('aria-current="true"') == 1


def c12_a_lista_ppp_aparece_com_o_que_falta_nela(client, edital):
    texto = html(abrir(client, edital, "presidência"))
    listas = texto.split('aria-labelledby="listas-titulo"', 1)[1].split("</section>", 1)[0]
    linha = re.search(r'<th scope="row">PPP</th>.*?</tr>', listas, re.S)
    assert linha, "a PPP tem a sua linha"
    assert 'class="cc-agora-da-lista"' in linha.group(0)
