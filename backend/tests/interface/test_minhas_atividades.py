""" "Minhas atividades" pela tela (160): a presidência, o avaliador, o Gestor, as esperas e o nome.

Cada caso monta **um** cenário (a idempotência da publicação faz dois colidirem) e lê a página
como a pessoa a lê: pelo contexto, para o que a página decidiu, e pelo HTML, para o que chega ao
navegador.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.interface import andamento as a
from processo_seletivo.interface import atividades as at
from tests.fixtures.andamento import certame_p1, certame_s1
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

PAGINA = "/gestao/minhas-etapas"


@pytest.fixture
def base(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    return gestor, api_client, manager_headers, process_payload


def abrir(client):
    resposta = client.get(reverse("interface:minhas-etapas"))
    assert resposta.status_code == 200
    return resposta.context["atividades"], resposta.content.decode()


def atos(atividades):
    return [grupo.ato for grupo in atividades.para_fazer]


def secao_para_fazer(html):
    return html.split('id="para-fazer-titulo"', 1)[1].split("</section>", 1)[0]


@pytest.fixture
def espiao(monkeypatch):
    """Conta as chamadas à derivação do andamento, sem mudar o que ela devolve."""
    chamadas = []
    original = a.do_edital

    def do_edital(edital, ator, **kwargs):
        chamadas.append(edital.id)
        return original(edital, ator, **kwargs)

    monkeypatch.setattr(a, "do_edital", do_edital)
    return chamadas


# --- US1: a presidência ----------------------------------------------------------------------


def test_a_presidencia_ve_os_atos_dela_com_a_base_e_o_link(client, base):
    certame = certame_p1(*base)
    identificar(client, "maria", [])
    atividades, html = abrir(client)

    assert atividades.para_fazer, "a presidência do P1 tem a distribuição em aberto"
    assert {grupo.base for grupo in atividades.para_fazer} == {at.PRESIDENCIA}
    secao = secao_para_fazer(html)
    assert 'class="base-da-atividade">Presidência<' in secao
    primeira = atividades.para_fazer[0]
    assert f'href="{primeira.providencia.url}"' in secao
    assert f"Edital {certame['edital'].number}/{certame['edital'].year}" in secao
    assert at.COBERTURA in html


def test_o_ato_praticado_sai_da_pagina_na_leitura_seguinte(client, base):
    from processo_seletivo.resultados.application.consolidacao import consolidar
    from tests.fixtures.mesa import concluir_como, distribuir_para

    gestor = base[0]
    certame = certame_p1(*base)
    distribuir_para(certame, gestor, ["joao"], certame["inscricoes"][2:], chave="160-resto")
    for inscricao in certame["inscricoes"]:
        concluir_como(certame, "joao", inscricao, pontuacao="70")
    identificar(client, "maria", [])
    antes, _ = abrir(client)
    assert "Consolidar 3 inscrições prontas" in atos(antes)

    consolidar(
        actor=gestor,
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        etapa_id=certame["etapa"],
        inscricao_ids=[i.id for i in certame["inscricoes"]],
        idempotency_key="160-consolidar",
        correlation_id="teste-160",
    )
    depois, _ = abrir(client)
    assert "Consolidar 3 inscrições prontas" not in atos(depois)


def test_o_edital_que_nao_pode_ser_lido_e_dito_e_nao_vira_nada_a_fazer(client, base, monkeypatch):
    certame = certame_s1(*base)

    def falha(self, **kwargs):
        raise RuntimeError("conteúdo que a derivação não espera")

    monkeypatch.setattr(a._Leitor, "andamento", falha)
    identificar(client, "maria", [])
    atividades, html = abrir(client)

    assert atividades.nao_lidos == [certame["edital"]]
    assert "1 Edital não pôde ser lido agora" in html
    assert reverse("interface:detalhe", args=[certame["edital"].id]) in html
    assert at.NADA_PARA_FAZER not in html


def test_processo_encerrado_nao_e_lido(client, base, espiao):
    from processo_seletivo.processos.models import ProcessoSeletivo

    certame = certame_s1(*base)
    ProcessoSeletivo.objects.filter(pk=certame["edital"].processo_id).update(status="ENCERRADO")
    identificar(client, "maria", [])
    atividades, _ = abrir(client)

    assert espiao == []
    assert atividades.para_fazer == []


def test_a_presidente_que_publica_nao_ve_publicar_o_resultado(client, base):
    """D-004 da `160`: o papel da unidade fica fora, mesmo nos Editais que ela preside."""
    from processo_seletivo.interface import identidade
    from tests.fixtures.convocacao import montar_cenario_da_convocacao

    edital, _, _ = montar_cenario_da_convocacao(*base, prefixo="160-publica")
    identificar(client, "maria", ["publicador"])
    atividades, html = abrir(client)

    resposta = client.get(reverse("interface:minhas-etapas"))
    ator = identidade.ator_da_sessao(resposta.wsgi_request)
    andamento = a.do_edital(edital, ator)
    suas = [item for item in andamento.nivel_1.itens if item.sua]
    assert any(item.responsavel == a.PUBLICA for item in suas), "o Centro diria sua a publicação"
    assert not any(grupo.providencia.responsavel == a.PUBLICA for grupo in atividades.para_fazer)
    assert "publicar o resultado" in at.COBERTURA
    assert at.COBERTURA in html


# --- US2: o avaliador, sem a derivação -------------------------------------------------------


def test_o_avaliador_ve_avaliar_com_a_alocacao_e_o_link_da_mesa(client, base, espiao):
    certame = certame_p1(*base, distribuidas=2)
    identificar(client, "joao", [])
    atividades, html = abrir(client)

    assert espiao == [], "quem não preside não paga a derivação (FR-6856)"
    assert atos(atividades) == ["Avaliar 2 inscrições"]
    grupo = atividades.para_fazer[0]
    assert grupo.base == at.ALOCACAO
    assert grupo.providencia.url == reverse(
        "interface:minha-etapa", args=[certame["edital"].id, certame["etapa"]]
    )
    assert "2</strong>\n          pendentes" in html or "<strong>2</strong>" in html


def test_o_membro_sem_pendencia_le_que_nada_depende_dele_no_que_a_pagina_cobre(client, base):
    certame_p1(*base, distribuidas=0)
    identificar(client, "joao", [])
    atividades, html = abrir(client)

    assert atividades.para_fazer == []
    assert at.NADA_PARA_FAZER in html
    assert at.COBERTURA in html


# --- US3: o Gestor -----------------------------------------------------------------------------


def test_o_gestor_sem_presidencia_nao_ve_conducao_e_a_derivacao_nao_roda(client, base, espiao):
    certame_s1(*base)
    identificar(client, "carlos", ["gestor"])
    atividades, html = abrir(client)

    assert espiao == []
    assert atividades.para_fazer == []
    assert at.COBERTURA_DO_GESTOR in html


def test_o_gestor_que_preside_ve_os_atos_do_processo_dele(client, base):
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from tests.fixtures.comissao import constituir

    gestor = base[0]
    certame = certame_s1(*base)
    constituir(gestor, certame["edital"].processo, [("gina", Funcao.MEMBRO)], prefixo="160-g")
    # O Gestor passa a presidir: a presidência é lida no vínculo, e não na permissão (D-002).
    from processo_seletivo.comissoes.models import MembroComissao

    MembroComissao.objects.filter(
        processo=certame["edital"].processo, identity_subject="gina"
    ).update(funcao=Funcao.PRESIDENTE)
    identificar(client, "gina", ["gestor"])
    atividades, html = abrir(client)

    assert atividades.para_fazer
    assert {grupo.base for grupo in atividades.para_fazer} == {at.PRESIDENCIA}
    assert at.COBERTURA_DO_GESTOR in html


# --- US4: as esperas -----------------------------------------------------------------------------


def test_a_espera_fica_recolhida_com_a_origem_da_data_e_sem_atraso(client, base):
    from tests.fixtures.sorteio import certame_de_sorteio

    certame_de_sorteio(*base, periodo_aberto=True)
    identificar(client, "maria", [])
    atividades, html = abrir(client)

    assert atividades.em_espera, "com as inscrições abertas, a relação espera o fim delas"
    assert all(grupo.situacao in (a.AGUARDA, a.IMPEDIDO) for grupo in atividades.em_espera)
    assert not any(grupo.situacao == a.AGUARDA for grupo in atividades.para_fazer)
    espera = html.split('<details class="em-espera-da-pagina">', 1)[1].split("</details>", 1)[0]
    assert "<summary>Em espera nos seus Editais · " in espera
    assert '<details class="em-espera-da-pagina" open' not in html
    for grupo in atividades.em_espera:
        assert grupo.providencia.razao in espera
    texto = re.sub(r"<[^>]+>", " ", html).lower()
    assert "atrasad" not in texto
    assert "seu prazo" not in texto


# --- US5: o nome ---------------------------------------------------------------------------------


def test_o_nome_visivel_e_minhas_atividades_e_o_endereco_fica(client, base):
    certame = certame_p1(*base)
    identificar(client, "joao", [])
    assert reverse("interface:minhas-etapas") == PAGINA

    pagina = client.get(PAGINA).content.decode()
    mesa = client.get(
        reverse("interface:minha-etapa", args=[certame["edital"].id, certame["etapa"]])
    )
    assert mesa.status_code == 200
    for html in (pagina, mesa.content.decode()):
        assert "Minhas Etapas" not in html
        assert "Minhas atividades" in html
    assert "<title>Minhas atividades" in pagina


# --- a conferência por alocação (FR-6857) ---------------------------------------------------------


@pytest.fixture
def chamada(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, settings):
    """Uma convocação com a certidão apresentada: a conferência está em aberto (115)."""
    from tests.fixtures import documentos_da_convocacao as cenarios
    from tests.fixtures.documentos_da_convocacao import CERTIDAO, apresentar

    settings.INTERFACE_SELETOR_IDENTIDADE = True
    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="160-conferencia",
    )
    edital, _, _ = cenario
    pessoa, convocacao = cenarios.convocar_primeira(cenario, gestor)
    apresentar(pessoa, convocacao, CERTIDAO)
    return {"edital": edital, "convocacao": convocacao}


def alocar_a_conferencia(gestor, edital, subject, *, perfil=None, funcao=None):
    from processo_seletivo.comissoes.application.alocacao import alocar_a_conferencia as alocar
    from processo_seletivo.comissoes.models import MembroComissao
    from tests.fixtures.comissao import constituir

    if funcao is not None:
        constituir(gestor, edital.processo, [(subject, funcao)], prefixo=f"160-{subject}")
    membro = MembroComissao.objects.get(processo=edital.processo, identity_subject=subject)
    alocar(
        actor=gestor,
        processo_id=edital.processo_id,
        membro_id=membro.id,
        edital_id=edital.id,
        perfil_id=perfil,
        idempotency_key=f"160-conferencia-{subject}-{perfil}",
        correlation_id="teste-160",
    )


def conferencias(atividades):
    return [g for g in atividades.para_fazer if g.providencia.responsavel == a.CONFERE]


def test_quem_preside_e_esta_alocada_a_conferencia_tem_uma_linha_so(chamada, client, gestor):
    alocar_a_conferencia(gestor, chamada["edital"], "maria")
    identificar(client, "maria", [])
    atividades, _ = abrir(client)

    linhas = conferencias(atividades)
    assert len(linhas) == 1, [g.ato for g in linhas]
    assert linhas[0].base == at.PRESIDENCIA


def test_o_gestor_alocado_a_um_perfil_ve_so_a_conferencia_dele(chamada, client, gestor):
    from processo_seletivo.comissoes.domain.funcoes import Funcao

    edital, convocacao = chamada["edital"], chamada["convocacao"]
    alocar_a_conferencia(gestor, edital, "gina", perfil=convocacao.perfil_id, funcao=Funcao.MEMBRO)
    identificar(client, "gina", ["gestor"])
    atividades, html = abrir(client)

    assert [g.base for g in atividades.para_fazer] == [at.ALOCACAO]
    assert conferencias(atividades) == atividades.para_fazer
    assert at.COBERTURA_DO_GESTOR in html


def test_o_membro_alocado_a_outro_perfil_nao_ve_a_conferencia(chamada, client):
    from tests.integration.comissoes.test_alocacao_a_conferencia import _alocar_a_outro_perfil

    _alocar_a_outro_perfil(chamada["edital"], "joao")
    identificar(client, "joao", [])
    atividades, _ = abrir(client)

    assert conferencias(atividades) == []
