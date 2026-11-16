"""A composição das telas da inscrição no portal (177).

"Minhas inscrições", "Minha inscrição" e "Acompanhar" na coluna da jornada do candidato, com
o começo comum, um botão cheio por tela, o cartão na ordem da FR-8105 com o prazo da ação, e a
grade de rótulo e valor. A largura medida (margens iguais, bordas dos blocos, sem rolagem lateral)
é conferida no navegador e está nas capturas da spec; aqui fica o que o HTML e a folha garantem.
"""

import re
from datetime import timedelta
from types import SimpleNamespace

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.inscricoes.domain.periodo import periodo_de_inscricoes
from processo_seletivo.portal import views
from processo_seletivo.portal.templatetags.prazo_da_convocacao import ate_o_prazo
from processo_seletivo.publicacoes.application.selectors import selecao_publica
from tests.fixtures.candidato import MARIA, identificar
from tests.integration.portal.test_minhas_inscricoes import inscricao

pytestmark = pytest.mark.django_db


def _conteudo(selecao):
    return selecao_publica(edital_id=selecao.id).content


def _item(corpo, registro):
    destino = reverse("portal:inscricao", args=[registro.id])
    (item,) = [
        i
        for i in re.findall(r'<li class="selecao">.*?</li>', corpo, flags=re.S)
        if f'href="{destino}"' in i
    ]
    return item


def _visivel(trecho):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", trecho)).strip()


# --- Minhas inscrições --------------------------------------------------------------------------


def test_a_lista_fica_na_coluna_da_jornada(client, selecao):
    """FR-8100: a coluna das telas da verificação (174), e não a grade encostada à esquerda."""
    inscricao(selecao, MARIA)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:inscricoes")).content.decode()

    assert '<div class="jornada jornada-da-inscricao">' in corpo


def test_o_titulo_do_cartao_e_o_processo_e_a_linha_seguinte_o_edital_e_o_perfil(client, selecao):
    """FR-8105, D-002: o título era o Perfil, e o Processo vinha em cinza."""
    registro = inscricao(selecao, MARIA)
    identificar(client, MARIA)
    conteudo = _conteudo(selecao)
    perfil = views._perfil_do_conteudo(conteudo, registro.profile_id)["name"]

    item = _item(client.get(reverse("portal:inscricoes")).content.decode(), registro)

    (titulo,) = re.findall(r'<a class="titulo" href="[^"]+">([^<]+)</a>', item)
    assert titulo == conteudo["processoTitle"]
    (meta,) = re.findall(r'<span class="meta">([^<]+)</span>', item)
    assert meta == f"Edital {conteudo['number']}/{conteudo['year']} · {perfil}"


def test_a_ordem_do_cartao_e_titulo_situacao_prazo_e_acao(client, selecao):
    """FR-8105: de qual seleção é, em que pé está, até quando, e o que fazer."""
    registro = inscricao(selecao, MARIA)
    identificar(client, MARIA)

    item = _item(client.get(reverse("portal:inscricoes")).content.decode(), registro)

    posicoes = [
        item.find('class="titulo"'),
        item.find('class="meta"'),
        item.find("selo-da-inscricao"),
        item.find('class="prazo-do-cartao"'),
        item.find('class="principal"'),
    ]
    assert -1 not in posicoes, posicoes
    assert posicoes == sorted(posicoes)


def test_o_rascunho_aberto_diz_o_prazo_do_envio(client, selecao):
    """FR-8106: no rascunho, o término do período de inscrições, na forma da convocação (118)."""
    registro = inscricao(selecao, MARIA)
    identificar(client, MARIA)
    periodo = periodo_de_inscricoes(_conteudo(selecao), timezone.now())
    assert periodo.fim is not None and periodo.estado == "aberto", "a fixture precisa de prazo"

    item = _item(client.get(reverse("portal:inscricoes")).content.decode(), registro)

    assert _visivel(item).count("Prazo:") == 1
    assert f"Prazo: {ate_o_prazo(periodo.fim)}" in _visivel(item)


def test_a_enviada_sem_convocacao_nem_passo_nao_tem_prazo(client, selecao):
    registro = inscricao(selecao, MARIA, enviada=True)
    identificar(client, MARIA)

    item = _item(client.get(reverse("portal:inscricoes")).content.decode(), registro)

    assert "Prazo:" not in item
    assert "✓ Inscrição enviada" in item


def test_a_situacao_e_selo_com_a_marca_e_a_palavra(client, selecao):
    """FR-8107, UX-952: as frases de sempre, e a marca continua no texto."""
    registro = inscricao(selecao, MARIA, enviada=True)
    identificar(client, MARIA)

    item = _item(client.get(reverse("portal:inscricoes")).content.decode(), registro)

    assert '<span class="situacao enviada selo-da-inscricao">✓ Inscrição enviada</span>' in item


def test_o_acesso_a_conta_sai_do_subtitulo(client, selecao):
    """FR-8109, D-006: o link continua, na faixa do título, e não no lugar do subtítulo."""
    inscricao(selecao, MARIA)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:inscricoes")).content.decode()

    assert re.search(r'<p class="sub"><a href="[^"]+">Acesso à conta</a></p>', corpo) is None
    assert re.search(r'<a class="acesso-a-conta" href="[^"]+">Acesso à conta</a>', corpo)
    comeco = corpo[corpo.find('class="comeco-da-lista"') :]
    assert comeco.find("<h1>Minhas inscrições</h1>") < comeco.find("Acesso à conta")


def test_cada_cartao_tem_um_botao_cheio(client, selecao):
    """FR-8103, SC-2803: a regra da lista é por cartão."""
    rascunho = inscricao(selecao, MARIA)
    identificar(client, MARIA)

    item = _item(client.get(reverse("portal:inscricoes")).content.decode(), rascunho)

    assert item.count('class="principal"') == 1


# --- O prazo do cartão, regra pura (FR-8106, D-003) ---------------------------------------------


AGORA = timezone.now()
FUTURO = AGORA + timedelta(days=3)
PASSADO = AGORA - timedelta(days=1)


def _prazo(**kwargs):
    base = {
        "enviada": True,
        "fechada": None,
        "periodo": None,
        "agora": AGORA,
        "convocacao": None,
        "passo": None,
    }
    return views._prazo_do_cartao(**{**base, **kwargs})


def test_a_convocacao_aberta_da_o_prazo_e_vence_o_passo():
    convocacao = SimpleNamespace(vencimento=FUTURO)
    passo = SimpleNamespace(fim=FUTURO + timedelta(days=5))

    assert _prazo(convocacao=convocacao, passo=passo) == FUTURO


def test_o_passo_pendente_da_o_termino_da_etapa():
    assert _prazo(passo=SimpleNamespace(fim=FUTURO)) == FUTURO


def test_o_prazo_que_ja_passou_nao_aparece():
    """Um vencimento decorrido não é prazo a cumprir; a tela da convocação diz o vencido."""
    assert _prazo(convocacao=SimpleNamespace(vencimento=PASSADO)) is None
    assert _prazo(passo=SimpleNamespace(fim=PASSADO)) is None


def test_a_convocacao_sem_vencimento_nao_tem_prazo():
    """O prazo que ainda não começou a correr (a comunicação não saiu) não é inventado."""
    assert _prazo(convocacao=SimpleNamespace(vencimento=None)) is None


def test_o_rascunho_fechado_nao_tem_prazo():
    conteudo = {
        "schedule": [
            {
                "isRegistrationPeriod": True,
                "startAt": (AGORA - timedelta(days=9)).isoformat(),
                "endAt": PASSADO.isoformat(),
            }
        ]
    }
    fechado = periodo_de_inscricoes(conteudo, AGORA)

    assert _prazo(enviada=False, fechada=fechado, periodo=fechado) is None


def test_o_periodo_sem_termino_nao_tem_prazo():
    """Sem término declarado, o sistema não cria prazo que o Edital não fixou (009)."""
    conteudo = {
        "schedule": [
            {"isRegistrationPeriod": True, "startAt": (AGORA - timedelta(days=1)).isoformat()}
        ]
    }

    assert _prazo(enviada=False, periodo=periodo_de_inscricoes(conteudo, AGORA)) is None


def test_o_rascunho_aberto_da_o_termino_do_periodo():
    conteudo = {
        "schedule": [
            {
                "isRegistrationPeriod": True,
                "startAt": (AGORA - timedelta(days=1)).isoformat(),
                "endAt": FUTURO.isoformat(),
            }
        ]
    }

    assert _prazo(enviada=False, periodo=periodo_de_inscricoes(conteudo, AGORA)) == FUTURO


# --- Minha inscrição e Acompanhar ----------------------------------------------------------------


def _comeco_comum(corpo, titulo, selecao, registro):
    conteudo = _conteudo(selecao)
    perfil = views._perfil_do_conteudo(conteudo, registro.profile_id)["name"]
    trilha = corpo[corpo.find('<nav class="trilha-da-inscricao"') :]
    trilha = trilha[: trilha.find("</nav>")]
    assert f'href="{reverse("portal:inscricoes")}">Minhas inscrições</a>' in trilha
    assert (
        f"{conteudo['processoTitle']} · Edital {conteudo['number']}/{conteudo['year']}"
        in _visivel(trilha)
    )
    assert f"<h1>{titulo}</h1>" in corpo
    assert f"Perfil de Vaga: {perfil}" in corpo
    assert corpo.find("trilha-da-inscricao") < corpo.find(f"<h1>{titulo}</h1>")


def test_minha_inscricao_comeca_pela_trilha_e_pelo_perfil(client, selecao):
    """FR-8110, D-004, D-005."""
    registro = inscricao(selecao, MARIA, enviada=True)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:inscricao", args=[registro.id])).content.decode()

    assert '<div class="jornada jornada-da-inscricao">' in corpo
    _comeco_comum(corpo, "Minha inscrição", selecao, registro)


def test_minha_inscricao_tem_a_grade_e_um_botao_cheio(client, selecao):
    """FR-8115 a FR-8117."""
    registro = inscricao(selecao, MARIA, enviada=True)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:inscricao", args=[registro.id])).content.decode()

    assert '<dl class="campos campos-em-grade">' in corpo
    assert corpo.count('class="principal"') == 1
    assert re.search(r'<a class="principal" href="[^"]+">Baixar comprovante</a>', corpo)
    destino = reverse("portal:acompanhamento", args=[registro.id])
    assert f'<a class="secundario" href="{destino}">Acompanhar esta inscrição</a>' in corpo
    faixa = corpo[corpo.find('class="situacao-e-protocolo"') :]
    assert faixa.find("✓ Inscrição enviada") < faixa.find(registro.protocolo)


def test_acompanhar_comeca_pela_trilha_e_pelo_perfil(client, selecao):
    """FR-8110, FR-8111: o começo comum, e "Sua situação" logo depois."""
    registro = inscricao(selecao, MARIA, enviada=True)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:acompanhamento", args=[registro.id])).content.decode()

    assert '<div class="jornada jornada-da-inscricao">' in corpo
    _comeco_comum(corpo, "Acompanhar", selecao, registro)
    depois_do_comeco = corpo[corpo.find("<h1>Acompanhar</h1>") :]
    assert depois_do_comeco.find("<section") == depois_do_comeco.find(
        '<section class="situacao-da-inscricao"'
    )


def test_ver_o_que_enviei_e_secundario(client, selecao):
    """FR-8113, D-007: a ação da tela é a de "Sua situação"; conferir é consulta."""
    registro = inscricao(selecao, MARIA, enviada=True)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:acompanhamento", args=[registro.id])).content.decode()

    destino = reverse("portal:inscricao", args=[registro.id])
    assert f'<a class="secundario" href="{destino}">Ver o que enviei</a>' in corpo
    assert corpo.count('class="principal"') <= 1


def test_acompanhar_mantem_a_ordem_dos_blocos(client, selecao):
    """FR-8114: a composição muda a largura, e não a ordem da 063."""
    registro = inscricao(selecao, MARIA, enviada=True)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:acompanhamento", args=[registro.id])).content.decode()

    posicoes = [
        corpo.find("Sua situação"),
        corpo.find("Sua participação"),
        corpo.find("Cronograma do processo"),
        corpo.find("Ver o que enviei"),
    ]
    assert -1 not in posicoes and posicoes == sorted(posicoes)


# --- A folha ------------------------------------------------------------------------------------


@pytest.fixture
def folha():
    from django.contrib.staticfiles import finders

    with open(finders.find("portal/portal.css"), encoding="utf-8") as arquivo:
        return arquivo.read()


def test_a_medida_de_leitura_continua_no_paragrafo_da_coluna(folha):
    """FR-8104: dentro da coluna, `main>p` não alcança o parágrafo; a medida volta por ele."""
    assert re.search(r"\.jornada-da-inscricao p\{max-width:var\(--leitura\)\}", folha)
    assert re.search(r"main>p[^{]*\{[^}]*max-width:var\(--leitura\)", folha)


def test_os_blocos_vao_a_borda_da_coluna(folha):
    """FR-8102: os blocos que paravam na medida passam à borda, sob a marca da 177 só."""
    (regra,) = re.findall(r"([^}]*)\{max-width:none\}", folha[folha.find("(177)") :])[:1]
    for bloco in (".situacao-da-inscricao", ".cartao-de-lista", ".resultado-da-etapa", ".aviso"):
        assert f".jornada-da-inscricao {bloco}" in regra, bloco


def test_a_acao_do_cartao_tem_a_largura_do_rotulo_na_tela_larga(folha):
    """FR-8108: cheia no celular, do tamanho do rótulo a partir de 40rem."""
    secao = folha[folha.find("(177)") :]
    assert ".jornada-da-inscricao .minhas-inscricoes a.principal{align-self:stretch" in secao
    assert re.search(
        r"@media \(min-width:40rem\)\{\s*\.jornada-da-inscricao \.minhas-inscricoes "
        r"a\.principal\{align-self:flex-start",
        secao,
    )


# --- O prazo do cartão é o do Acompanhamento (revisão do #577, D-009) ----------------------------


@pytest.fixture
def jornada(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    from tests.fixtures import jornada_do_convocado

    return jornada_do_convocado.Montagem(gestor, api_client, manager_headers, process_payload)


@pytest.mark.parametrize("letra", ["C1", "E", "B2"])
def test_o_cartao_diz_o_mesmo_prazo_que_o_acompanhamento_com_e_sem_providencia(
    client, jornada, letra
):
    """D-009: com o Requerimento enviado (B2) ou tudo enviado (E), o Acompanhamento continua dizendo
    o prazo da convocação (FR-6208 da 154), e o cartão diz o mesmo. Com providência (C1), também."""
    from tests.fixtures import jornada_do_convocado
    from tests.interface.test_portal_convocacao import entrar_como

    cenario = jornada_do_convocado.montar(letra, jornada)
    with cenario.relogio():
        entrar_como(client, cenario.pessoa)
        lista = client.get(reverse("portal:inscricoes")).content.decode()
        acompanhamento = client.get(
            reverse("portal:acompanhamento", args=[cenario.pessoa.id])
        ).content.decode()

    item = _item(lista, cenario.pessoa)
    (no_cartao,) = re.findall(r"Prazo: (até [^.<]+?)(?: |$)", _visivel(item) + " ")
    situacao = re.search(
        r'<section class="situacao-da-inscricao".*?</section>', acompanhamento, re.S
    ).group(0)
    assert f"Prazo desta convocação: {no_cartao}" in _visivel(situacao)


# --- O começo das duas telas irmãs sai da mesma versão (revisão do #577, D-008) ------------------


def test_minha_inscricao_e_acompanhar_dizem_o_mesmo_perfil_depois_da_retificacao(
    client, selecao, api_client
):
    """O começo vem da vigente nas duas telas; "O que você informou" continua na aceita."""
    from tests.fixtures.candidato import PERFIL_DOCENTE
    from tests.fixtures.publicacao import retify

    registro = inscricao(selecao, MARIA, enviada=True)
    aceito = views._perfil_do_conteudo(_conteudo(selecao), PERFIL_DOCENTE)["name"]
    retify(
        api_client,
        selecao,
        [
            {
                "targetPath": f"/profiles/id={PERFIL_DOCENTE}/name",
                "operation": "REPLACE",
                "newValue": "Docente de Informática renomeado",
            }
        ],
    )
    identificar(client, MARIA)

    conferencia = client.get(reverse("portal:inscricao", args=[registro.id])).content.decode()
    acompanhamento = client.get(
        reverse("portal:acompanhamento", args=[registro.id])
    ).content.decode()

    for corpo in (conferencia, acompanhamento):
        assert "Perfil de Vaga: Docente de Informática renomeado" in corpo
    campos = conferencia[conferencia.find('<dl class="campos campos-em-grade">') :]
    campos = campos[: campos.find("</dl>")]
    assert aceito in campos and "renomeado" not in campos
