"""Correções de orientação e segurança operacional depois da publicação (126).

Cada caso parte de um achado do estudo de orientação da jornada de 06/11/2026, conferido no código:
a sucessão em destaque logo depois do ato (A1), *Falta* em lista sem inscrito (A2), o aviso de
congelamento fora do lugar (A5) e a confirmação da ordem sem o motivo (A6). O rótulo da convocação
(A4) está em `tests/integration/relatorio/test_convocacao_sem_comunicacao.py`.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.interface import conducao_do_marco
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

SUCESSAO = re.compile(r'<details class="sucessao"( open)?>\s*<summary>([^<]+)</summary>')


def _texto(resposta):
    assert resposta.status_code == 200, resposta.status_code
    return " ".join(resposta.content.decode().split())


def _blocos_de_sucessao(pagina):
    """`[(aberto, rótulo)]` de cada bloco de sucessão da página."""
    return [(bool(aberto), rotulo.strip()) for aberto, rotulo in SUCESSAO.findall(pagina)]


def _depois(pagina, marcador):
    return pagina[pagina.index(marcador) :]


# --- cenários ------------------------------------------------------------------------------------


@pytest.fixture
def cotas_com_pcd_vazia(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    """Marco de sorteio, três listas, e ninguém declarou PcD — o Polo Vitória numa lista só."""
    from tests.fixtures.sorteio import LISTA_PPI, certame_com_cotas

    return certame_com_cotas(
        gestor, api_client, manager_headers, process_payload, quantos=3, modalidades={0: LISTA_PPI}
    )


@pytest.fixture
def cotas_sem_ninguem(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    """O Polo Vitória inteiro: o Perfil não teve inscrição nenhuma."""
    from tests.fixtures.sorteio import certame_com_cotas

    return certame_com_cotas(
        gestor, api_client, manager_headers, process_payload, quantos=0, modalidades={}
    )


@pytest.fixture
def ordem_emitida(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    """Marco por pontuação com ordem emitida e corte por emitir."""
    from tests.fixtures.corte import montar_cenario_do_corte

    edital, _, inscricoes = montar_cenario_do_corte(
        gestor, api_client, manager_headers, process_payload, prefixo="orientacao-126"
    )
    return edital, inscricoes


@pytest.fixture
def ordem_por_emitir(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    """Marco por pontuação, uma inscrição com resultado e outra sem: a ordem ainda não emitida."""
    from tests.fixtures.corte import montar_cenario_do_corte

    edital, _, inscricoes = montar_cenario_do_corte(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="orientacao-126-ordem",
        pontuacoes=("90.0000",),
        emitir_a_ordem=False,
    )
    return edital, inscricoes


def _marco(client, certame):
    return client.get(reverse("interface:marco", args=[certame["edital"].id, certame["marco"]]))


# --- A2 · lista sem inscrito ------------------------------------------------------------------


def test_o_criterio_e_a_lista_que_ninguem_declarou_com_as_inscricoes_encerradas(
    cotas_com_pcd_vazia,
):
    """FR-4019, D-002: só a PcD; a ampla e a PPI têm inscrição, ainda sem relação nenhuma."""
    from tests.fixtures.sorteio import LISTA_PCD

    certame = cotas_com_pcd_vazia
    conteudo, perfil, marco = conducao_do_marco.marco_publicado(certame["edital"], certame["marco"])

    vazios = conducao_do_marco.recortes_sem_inscrito(certame["edital"], conteudo, perfil, marco)

    assert vazios == {LISTA_PCD}, "ausência de ato não basta: a ampla e a PPI não têm relação"


def test_com_as_inscricoes_abertas_nada_e_sem_inscrito(
    gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """Alguém ainda pode declarar a lista: dizer *Não se aplica* seria cedo demais."""
    from tests.fixtures.sorteio import certame_de_sorteio

    certame = certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, quantos=0, periodo_aberto=True
    )
    conteudo, perfil, marco = conducao_do_marco.marco_publicado(certame["edital"], certame["marco"])

    assert conducao_do_marco.recortes_sem_inscrito(certame["edital"], conteudo, perfil, marco) == (
        set()
    )


def test_relacao_congelada_nao_e_sem_inscrito(cotas_com_pcd_vazia):
    """Há ato: a cadeia segue a regra de hoje, mesmo que a lista tenha ficado vazia depois."""
    from processo_seletivo.publicacoes.application.selectors import effective_version
    from tests.fixtures.sorteio import LISTA_PCD, relacao

    certame = cotas_com_pcd_vazia
    edital = certame["edital"]
    relacao(
        edital,
        versao=effective_version(edital_id=edital.id),
        perfil_id=certame["perfil"],
        lista_id=LISTA_PCD,
    )
    conteudo, perfil, marco = conducao_do_marco.marco_publicado(edital, certame["marco"])

    assert LISTA_PCD not in conducao_do_marco.recortes_sem_inscrito(edital, conteudo, perfil, marco)


def test_marco_por_pontuacao_nao_tem_recorte_sem_inscrito(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client
):
    """FR-4023: no marco por Etapas a lista vazia tem ordem, e emitida é *Feito*."""
    from tests.fixtures.corte import MARCO
    from tests.fixtures.recortes import MODALIDADE_PPI, montar_cenario_7_1_2

    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="orientacao-126-pontuacao",
        emitir_a_ordem=False,
        autodeclarar=False,
        modalidades={2: MODALIDADE_PPI},
    )
    conteudo, perfil, marco = conducao_do_marco.marco_publicado(edital, MARCO)

    assert conducao_do_marco.recortes_sem_inscrito(edital, conteudo, perfil, marco) == set()
    identificar(client, "carlos", ["gestor"])
    pagina = client.get(reverse("interface:marco", args=[edital.id, MARCO])).content.decode()
    estados = re.findall(r'data-operacao="ordenar" data-estado="([a-z_]+)"', pagina)
    assert "nao_se_aplica" not in estados


def test_a_conducao_diz_nao_se_aplica_na_lista_sem_inscrito_e_tira_dos_totais(
    client, cotas_com_pcd_vazia
):
    """FR-4020: as quatro células, sem link, e fora dos totais."""
    identificar(client, "maria", [])
    pagina = _marco(client, cotas_com_pcd_vazia).content.decode()

    linha = _depois(pagina, "Pessoas com deficiência (PCD)</th>")
    linha = linha[: linha.index("</tr>")]
    assert linha.count('data-estado="nao_se_aplica"') == 4
    assert linha.count("nenhuma inscrição nesta lista") == 4
    assert "<a href" not in linha
    assert "ordem 0 de 2" in " ".join(pagina.split()), "duas listas se aplicam, e não três"


def test_a_conferencia_poe_a_lista_sem_inscrito_fora_e_nao_impedida(client, cotas_com_pcd_vazia):
    """FR-4021: *impedido* diria que falta algo; aqui não haverá ato."""
    certame = cotas_com_pcd_vazia
    identificar(client, "maria", [])

    pagina = client.post(
        reverse(
            "interface:gesto-do-marco",
            args=[certame["edital"].id, certame["marco"], "apurar"],
        )
    )

    assert conducao_do_marco.SEM_INSCRITO in _texto(pagina)


def test_marco_sem_inscrito_nenhum_nao_tem_nada_a_conduzir(client, cotas_sem_ninguem):
    """FR-4022, SC-1212: o Polo Vitória do Edital 35."""
    identificar(client, "maria", [])
    pagina = _texto(_marco(client, cotas_sem_ninguem))

    assert "Nada a conduzir neste marco." in pagina
    assert "Nenhuma operação se aplica a este marco." in pagina
    assert 'data-estado="falta"' not in pagina
    assert "Conduzir o marco inteiro" not in pagina
    assert "Cortar o marco" not in pagina
    assert "Apurar a ocupação do marco" not in pagina
    assert "Nenhum recorte deste marco está em falta" not in pagina
    assert "0 de 0" not in pagina


def test_a_convocacao_da_lista_sem_inscrito_nao_manda_a_lugar_nenhum(client, cotas_com_pcd_vazia):
    """FR-4024, SC-1213: nem a apuração, nem a faixa seguinte."""
    from tests.fixtures.sorteio import LISTA_PCD

    certame = cotas_com_pcd_vazia
    identificar(client, "maria", [])
    endereco = reverse("interface:convocacao", args=[certame["edital"].id, certame["marco"]])

    pagina = _texto(client.get(f"{endereco}?lista={LISTA_PCD}"))

    assert "Não se aplica." in pagina
    assert "Nenhuma inscrição enviada declarou esta lista" in pagina
    assert "Ir para a apuração de ocupação" not in pagina
    assert "faixa seguinte" not in pagina
    assert "Quem pode ser chamado" not in pagina


def test_sem_corte_a_convocacao_nao_fala_em_faixa(client, cotas_com_pcd_vazia):
    """FR-4025: a ampla tem inscritos e ainda não tem ordem; a fila vazia não é faixa esgotada."""
    certame = cotas_com_pcd_vazia
    identificar(client, "maria", [])

    pagina = _texto(
        client.get(reverse("interface:convocacao", args=[certame["edital"].id, certame["marco"]]))
    )

    assert "Ainda não há fila neste recorte" in pagina
    assert "faixa que o corte alcançou" not in pagina
    assert "pedir a faixa seguinte" not in pagina
    assert "Ir para a apuração de ocupação" in pagina, "a ampla continua precisando da apuração"


def test_a_ocupacao_da_lista_sem_inscrito_nao_manda_emitir_a_ordem(client, cotas_com_pcd_vazia):
    """FR-4026: a ordem dela nunca existirá."""
    certame = cotas_com_pcd_vazia
    identificar(client, "maria", [])

    pagina = _texto(
        client.get(reverse("interface:ocupacao", args=[certame["edital"].id, certame["marco"]]))
    )

    assert pagina.count("Não se aplica.") == 1
    assert pagina.count("emita a ordem deste recorte") == 2, "a ampla e a PPI continuam"


# --- A1 · a sucessão recolhida ----------------------------------------------------------------


def _campo(pagina, nome):
    return re.search(rf'name="{nome}" value="([^"]*)"', pagina).group(1)


def test_depois_de_emitir_o_corte_a_sucessao_vem_recolhida_e_a_mensagem_diz_o_que_foi_feito(
    client, ordem_emitida
):
    """FR-4010, FR-4014, SC-1210: o caso `13b` do estudo."""
    from tests.fixtures.corte import MARCO

    edital, _ = ordem_emitida
    identificar(client, "carlos", ["gestor"])
    endereco = reverse("interface:corte", args=[edital.id, MARCO])
    antes = client.get(endereco).content.decode()
    assert _blocos_de_sucessao(antes) == [], "a primeira emissão não é sucessão"

    client.post(
        reverse("interface:emitir-corte", args=[edital.id, MARCO]),
        {
            "chave_idempotencia": _campo(antes, "chave_idempotencia"),
            "confirmacao_do_calculo": _campo(antes, "confirmacao_do_calculo"),
        },
    )
    depois = client.get(endereco).content.decode()

    assert _blocos_de_sucessao(depois) == [(False, "Suceder este corte (exige motivo)")]
    emitir = depois.index(reverse("interface:emitir-corte", args=[edital.id, MARCO]))
    assert depois.index('<details class="sucessao">') < emitir, "o formulário está no bloco"
    texto = " ".join(depois.split())
    assert re.search(r"Corte emitido</strong>: \d+ progride", texto)
    assert "sucedendo" not in texto


def test_o_corte_obsoleto_abre_a_sucessao(client, ordem_emitida, gestor, monkeypatch):
    """FR-4011: obsoleto, suceder é o passo esperado."""
    from processo_seletivo.interface import views
    from tests.fixtures.corte import MARCO, emitir

    edital, _ = ordem_emitida
    emitir(edital, gestor, chave="orientacao-126-corte")
    original = views.estado_do_corte
    monkeypatch.setattr(
        views, "estado_do_corte", lambda **kw: {**original(**kw), "obsoleto": True, "causas": []}
    )
    identificar(client, "carlos", ["gestor"])

    pagina = client.get(reverse("interface:corte", args=[edital.id, MARCO])).content.decode()

    assert _blocos_de_sucessao(pagina) == [(True, "Suceder este corte (exige motivo)")]


def test_depois_de_emitir_a_ordem_a_sucessao_vem_recolhida_com_as_contagens(
    client, ordem_por_emitir
):
    """FR-4010, FR-4015."""
    from tests.fixtures.corte import MARCO

    edital, _ = ordem_por_emitir
    identificar(client, "carlos", ["gestor"])
    endereco = reverse("interface:ordenacao", args=[edital.id, MARCO])
    antes = client.get(endereco).content.decode()
    assert _blocos_de_sucessao(antes) == []

    client.post(
        reverse("interface:emitir-ordenacao", args=[edital.id, MARCO]),
        {
            "confirmar": "1",
            "lista": "",
            "chave_idempotencia": _campo(antes, "chave_idempotencia"),
            "confirmacao_do_calculo": _campo(antes, "confirmacao_do_calculo"),
        },
    )
    depois = client.get(endereco).content.decode()

    assert _blocos_de_sucessao(depois) == [(False, "Suceder esta ordem (exige motivo)")]
    assert "Ordem emitida</strong>: 1 com posição, 1 sem posição." in " ".join(depois.split())


def test_a_apuracao_vigente_traz_a_sucessao_recolhida_e_a_mensagem_nomeia_o_recorte(
    client, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, seletor_ligado
):
    """FR-4010, FR-4016: a ocupação mostra todos os recortes, e a mensagem diz qual mudou."""
    from tests.fixtures.convocacao import montar_cenario_da_convocacao
    from tests.fixtures.corte import MARCO

    edital, _, _ = montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="orientacao-126-apuracao"
    )
    identificar(client, "carlos", ["gestor"])
    endereco = reverse("interface:ocupacao", args=[edital.id, MARCO])
    antes = client.get(endereco).content.decode()
    assert _blocos_de_sucessao(antes) == [(False, "Suceder esta apuração (exige motivo)")]

    client.post(
        reverse("interface:emitir-apuracao", args=[edital.id, MARCO]),
        {"lista": "", "chave": "orientacao-126-nova", "motivo": "Conferência da comissão."},
    )
    texto = " ".join(client.get(endereco).content.decode().split())

    assert re.search(r"Apuração emitida</strong> para [^:]+: \d+ vagas? efetivas?, ", texto)


# --- A6 · a confirmação da ordem --------------------------------------------------------------


def test_a_confirmacao_da_ordem_diz_quem_esta_sem_resultado_e_em_qual_etapa(
    client, ordem_por_emitir
):
    """FR-4035, FR-4037, FR-4039, SC-1216."""
    from tests.fixtures.corte import MARCO

    edital, _ = ordem_por_emitir
    identificar(client, "carlos", ["gestor"])
    antes = client.get(reverse("interface:ordenacao", args=[edital.id, MARCO])).content.decode()

    pagina = _texto(
        client.post(
            reverse("interface:emitir-ordenacao", args=[edital.id, MARCO]),
            {
                "lista": "",
                "chave_idempotencia": _campo(antes, "chave_idempotencia"),
                "confirmacao_do_calculo": _campo(antes, "confirmacao_do_calculo"),
            },
        )
    )

    assert "Inscrições sem resultado nas Etapas deste marco" in pagina
    assert "1 das 2 inscrições consideradas está sem resultado" in pagina
    assert re.search(r"<li>[^<]+: 1 sem resultado</li>", pagina)
    assert "esta ordem ficará obsoleta, e sucedê-la exigirá motivo" in pagina
    assert "Sem pontuação nas Etapas enumeradas" in pagina, "o motivo, e não só a contagem"
    assert "Emitir a ordem</button>" in pagina, "a emissão continua possível (D-004)"


def test_a_relacao_publicada_nomeia_o_recorte_e_a_sucessao_vem_recolhida(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """FR-4010, FR-4017: a tela do sorteio mostra todos os recortes do marco."""
    from tests.fixtures.sorteio import LISTA_PPI, certame_com_cotas

    certame = certame_com_cotas(gestor, api_client, manager_headers, process_payload)
    identificar(client, "maria", [])
    endereco = reverse("interface:sorteio", args=[certame["edital"].id, certame["marco"]])
    assert _blocos_de_sucessao(client.get(endereco).content.decode()) == []

    client.post(
        reverse(
            "interface:publicar-relacao-do-sorteio",
            args=[certame["edital"].id, certame["marco"]],
        ),
        {"lista_id": LISTA_PPI, "chave_idempotencia": "orientacao-126-relacao"},
    )
    pagina = client.get(endereco).content.decode()

    assert re.search(
        r"Relação publicada e congelada — <strong>[^<]*PPI[^<]*</strong>", " ".join(pagina.split())
    )
    assert _blocos_de_sucessao(pagina) == [(False, "Suceder esta relação (exige motivo)")]


def test_a_marca_da_faixa_seguinte_nao_sobra_para_o_corte_seguinte(client, ordem_emitida):
    """Revisão da 126: a marca que ficasse na sessão diria "faixa seguinte" de um corte novo."""
    from tests.fixtures.corte import MARCO

    edital, _ = ordem_emitida
    identificar(client, "carlos", ["gestor"])
    sessao = client.session
    sessao["acao_do_corte"] = "continuacao"
    sessao.save()
    endereco = reverse("interface:corte", args=[edital.id, MARCO])
    antes = client.get(endereco).content.decode()

    client.post(
        reverse("interface:emitir-corte", args=[edital.id, MARCO]),
        {
            "chave_idempotencia": _campo(antes, "chave_idempotencia"),
            "confirmacao_do_calculo": _campo(antes, "confirmacao_do_calculo"),
        },
    )
    texto = " ".join(client.get(endereco).content.decode().split())

    assert "Corte emitido</strong>" in texto
    assert "Faixa seguinte emitida" not in texto
