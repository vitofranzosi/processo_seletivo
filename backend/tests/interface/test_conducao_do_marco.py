"""A condução por marco: o indicador e os quatro gestos (049).

**O que se prova aqui é o que a spec promete a quem conduz**, e pela tela: o indicador diz o que
falta sem abrir recorte nenhum (`SC-301`); cada gesto declara o alcance antes de gravar (`FR-818`),
pratica um ato por recorte pelo comando de hoje (`FR-820`), e a recusa de um não apaga nem esconde
os outros (`FR-823`, `SC-302`).

**O formulário da confirmação é lido da página da conferência**, e nunca montado pelo teste. Um
teste que soubesse de antemão os campos passaria mesmo com a conferência mostrando outra coisa — e
o que a `SC-303` exige é justamente que só o que foi mostrado seja praticado.

O cenário é o 7/1/2 da `034` — um Perfil, a ampla e duas cotas —, sem nenhuma ordem emitida: o
gesto emite a da ampla junto com as reservadas.
"""

import re
from html import unescape

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.classificacao.models import AtoDeOrdenacao, Corte
from processo_seletivo.divulgacao.models import (
    DocumentoDoResultado,
    Natureza,
    PublicacaoResultado,
)
from processo_seletivo.interface import conducao_do_marco
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao
from processo_seletivo.publicacoes.domain.autoridades import escolher
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.corte import MARCO
from tests.fixtures.recortes import (
    MODALIDADE_PCD,
    MODALIDADE_PPI,
    declarar,
    emitir_recorte,
    montar_cenario_7_1_2,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

AMPLA = "Ampla concorrência (linha geral do quadro)"
PCD = "Pessoas com deficiência (PCD)"
PPI = "Pretos, pardos e indígenas (PPI)"


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    """O 7/1/2 sem ordem nenhuma: os três recortes do marco estão em falta."""
    edital, _, inscricoes = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="marco-049",
        emitir_a_ordem=False,
    )
    return edital, inscricoes


@pytest.fixture
def com_pcd_vazio(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    """O mesmo, e ninguém se autodeclarou PcD: o recorte existe e ninguém concorreu nele."""
    edital, _, inscricoes = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="marco-049-vazio",
        emitir_a_ordem=False,
        autodeclarar=False,
    )
    declarar(inscricoes[2], MODALIDADE_PPI)
    return edital, inscricoes


# --- apoio -------------------------------------------------------------------------------------


def tela(client, edital):
    return client.get(reverse("interface:marco", args=[edital.id, MARCO]))


def conferir(client, edital, operacao, **dados):
    return client.post(
        reverse("interface:gesto-do-marco", args=[edital.id, MARCO, operacao]), dados
    )


_FORM = re.compile(r'<form method="post"[^>]*class="confirmar">(.*?)</form>', re.S)
_OCULTO = re.compile(r'<input type="hidden" name="([^"]+)" value="([^"]*)">')


def formulario_da_confirmacao(pagina):
    """Os campos que a conferência devolve — lidos da página, e não montados aqui."""
    bloco = _FORM.search(pagina)
    assert bloco is not None, "a conferência não ofereceu confirmação"
    dados = {}
    for nome, valor in _OCULTO.findall(bloco.group(1)):
        if nome == "csrfmiddlewaretoken":
            continue
        dados.setdefault(nome, []).append(unescape(valor))
    return dados


def confirmar(client, edital, operacao, pagina, **extra):
    dados = formulario_da_confirmacao(pagina)
    dados.update({chave: [valor] for chave, valor in extra.items()})
    return client.post(
        reverse("interface:gesto-do-marco", args=[edital.id, MARCO, operacao]), dados
    )


def estados(pagina, operacao):
    return re.findall(rf'data-operacao="{operacao}" data-estado="([a-z_]+)"', pagina)


def gerir(client):
    identificar(client, "carlos", ["gestor"])


def publicar(client):
    identificar(client, "paula.publicadora", ["publicador"])


def ordenar_tudo(client, edital):
    gerir(client)
    pagina = conferir(client, edital, "ordenar").content.decode()
    return confirmar(client, edital, "ordenar", pagina)


# --- US1 · o indicador --------------------------------------------------------------------------


def test_a_tela_do_marco_mostra_cada_recorte_em_cada_operacao(client, cenario, gestor):
    """`FR-810`, `FR-812`, `UX-091`: um recorte por linha, na ordem da derivação."""
    edital, _ = cenario
    emitir_recorte(edital, gestor, chave="marco-049-ampla-por-fora")
    gerir(client)

    pagina = tela(client, edital).content.decode()

    assert pagina.index(AMPLA) < pagina.index(PCD) < pagina.index(PPI)
    assert estados(pagina, "ordenar") == ["feito", "falta", "falta"]
    assert estados(pagina, "apurar") == ["falta", "falta", "falta"]
    assert "ordem 1 de 3" in pagina
    # A célula leva à tela do recorte, com o recorte no endereço.
    assert f"/marcos/{MARCO}?lista={MODALIDADE_PPI}" in pagina


def test_sem_ordem_nao_ha_o_que_publicar_e_isso_conta_como_falta(client, cenario):
    """`data-model.md`: a publicação sem ordem é falta, com a nota do porquê."""
    edital, _ = cenario
    gerir(client)

    pagina = tela(client, edital).content.decode()

    assert estados(pagina, "publicar") == ["falta", "falta", "falta"]
    assert "falta a ordem" in pagina


def test_o_recorte_em_que_ninguem_concorreu_esta_feito_e_diz_por_que(client, com_pcd_vazio):
    """`D-003`: a ordem vazia é feita, e a nota diz que ninguém concorreu — não é pendência."""
    edital, _ = com_pcd_vazio
    ordenar_tudo(client, edital)

    pagina = tela(client, edital).content.decode()

    assert estados(pagina, "ordenar") == ["feito", "feito", "feito"]
    assert "ninguém concorreu" in pagina


def test_ordem_obsoleta_nao_e_contada_como_feita(client, cenario, gestor, monkeypatch):
    """`FR-811`, `FR-814`: obsoleto não é feito, e o marco não fica completo com ele."""
    edital, _ = cenario
    emitir_recorte(edital, gestor, chave="marco-049-obsoleta")
    monkeypatch.setattr(
        conducao_do_marco,
        "estado_do_marco",
        lambda **_: {"obsoleto": True},
    )
    gerir(client)

    pagina = tela(client, edital).content.decode()

    assert estados(pagina, "ordenar")[0] == "obsoleto"
    assert "ordem 0 de 3" in pagina


def test_o_publico_lendo_um_ato_anterior_aparece_como_obsoleto(client, cenario, gestor):
    """`FR-811`: publicação defasada é outra coisa que falta, e a nota a nomeia."""
    edital, _ = cenario
    ordenar_tudo(client, edital)
    publicar(client)
    pagina = conferir(
        client, edital, "publicar", natureza="PRELIMINAR", autoridade="diretoria-cefor"
    ).content.decode()
    confirmar(client, edital, "publicar", pagina)
    emitir_recorte(edital, gestor, chave="marco-049-sucessora", motivo="Recurso deferido.")

    pagina = tela(client, edital).content.decode()

    assert estados(pagina, "publicar") == ["obsoleto", "feito", "feito"]
    assert "o público lê um ato anterior" in pagina


def test_recorte_acrescentado_aparece_como_falta(cenario):
    """`FR-813`: o indicador segue a norma vigente — Modalidade nova é recorte novo, em falta."""
    edital, _ = cenario
    conteudo, perfil, marco = conducao_do_marco.marco_publicado(edital, MARCO)
    perfil = {
        **perfil,
        "competitionModalities": [
            *perfil["competitionModalities"],
            {"id": "00000000-0000-4000-8000-000000000999", "code": "QLB", "name": "Quilombolas"},
        ],
    }
    conteudo = {**conteudo, "profiles": [perfil]}

    indicador = conducao_do_marco.indicador_do_marco(
        edital, conteudo, perfil, marco, pode_classificar=True, pode_publicar=True
    )

    assert [linha["rotulo"] for linha in indicador["linhas"]][-1] == "Quilombolas (QLB)"
    assert indicador["linhas"][-1]["celulas"]["ordenar"]["estado"] == "falta"


def test_marco_que_a_norma_nao_publica_e_404(client, cenario):
    """`FR-813`: marco removido, ou identificador de nada, não tem recortes a operar."""
    edital, _ = cenario
    gerir(client)

    resposta = client.get(
        reverse("interface:marco", args=[edital.id, "00000000-0000-4000-8000-000000000777"])
    )

    assert resposta.status_code == 404


def test_a_pagina_do_edital_resume_cada_marco_e_leva_a_ele(client, cenario, gestor):
    """`UX-090`: o resumo de presença e o destino da tela do marco."""
    edital, _ = cenario
    emitir_recorte(edital, gestor, chave="marco-049-resumo")
    gerir(client)

    pagina = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()

    assert "Recortes: 3 · com ordem 1 · com corte 0 · apurados 0 · publicados 0" in pagina
    assert reverse("interface:marco", args=[edital.id, MARCO]) in pagina
    assert "conduzir o marco" in pagina


def test_o_resumo_nao_cresce_com_o_numero_de_marcos(cenario):
    """`SC-305`: quatro consultas para o Edital inteiro, com 1 marco ou com 16."""
    edital, _ = cenario
    conteudo, perfil, _ = conducao_do_marco.marco_publicado(edital, MARCO)
    dezesseis = {
        **conteudo,
        "profiles": [
            {
                **perfil,
                "id": f"00000000-0000-4000-8000-{indice:012d}",
                "classificationMilestones": [
                    {**marco, "id": f"00000000-0000-4000-9000-{indice:012d}"}
                    for marco in perfil["classificationMilestones"]
                ],
            }
            for indice in range(16)
        ],
    }

    with CaptureQueriesContext(connection) as um:
        conducao_do_marco.resumo_dos_marcos(edital, conteudo)
    with CaptureQueriesContext(connection) as muitos:
        resumo = conducao_do_marco.resumo_dos_marcos(edital, dezesseis)

    assert len(resumo) == 16
    assert len(um.captured_queries) == len(muitos.captured_queries) == 4


# --- US2 · ordenar ------------------------------------------------------------------------------


def test_a_conferencia_declara_o_alcance_e_nao_grava_nada(client, cenario):
    """`FR-818`, `FR-819`, `UX-092`: três grupos, o botão com a quantidade, nada gravado."""
    edital, _ = cenario
    gerir(client)

    resposta = conferir(client, edital, "ordenar")

    pagina = resposta.content.decode()
    assert resposta.status_code == 200
    assert "Serão praticados (3)" in pagina
    assert "Emitir 3 ordens" in pagina
    assert not AtoDeOrdenacao.objects.filter(edital=edital).exists()


def test_um_gesto_emite_uma_ordem_por_recorte_com_autor_e_rastro(client, cenario):
    """`FR-816`, `FR-820`, `FR-825`, `SC-304`: três atos, o mesmo autor, a mesma correlação."""
    edital, _ = cenario

    resposta = ordenar_tudo(client, edital)

    assert resposta.status_code == 302
    atos = AtoDeOrdenacao.objects.filter(edital=edital)
    assert atos.count() == 3
    assert {ato.lista_id and str(ato.lista_id) for ato in atos} == {
        None,
        MODALIDADE_PCD,
        MODALIDADE_PPI,
    }
    assert {ato.emitido_por for ato in atos} == {"carlos"}
    correlacoes = set(
        RegistroAuditoria.objects.filter(aggregate_id__in=[ato.id for ato in atos]).values_list(
            "correlation_id", flat=True
        )
    )
    assert len(correlacoes) == 1 and next(iter(correlacoes)).startswith("gesto-")
    desfecho = tela(client, edital).content.decode()
    assert "Ordenar o marco: 3 feitos, 0 recusados" in desfecho


def test_recorte_com_ordem_fica_de_fora_com_a_razao(client, cenario, gestor):
    """`D-002`: o gesto pratica só o primeiro ato; a sucessão continua na tela do recorte."""
    edital, _ = cenario
    emitir_recorte(edital, gestor, chave="marco-049-ja-tem")
    gerir(client)

    pagina = conferir(client, edital, "ordenar").content.decode()

    assert "Ficam de fora (1)" in pagina
    assert "Suceder uma ordem exige motivo" in pagina
    assert "Emitir 2 ordens" in pagina


def test_recorte_vazio_entra_declarado_e_recebe_a_ordem_vazia(client, com_pcd_vazio):
    """`D-003`: a conferência diz que ninguém concorreu, e o ato vazio é emitido."""
    edital, _ = com_pcd_vazio
    gerir(client)

    pagina = conferir(client, edital, "ordenar").content.decode()
    assert "ninguém concorreu" in pagina
    confirmar(client, edital, "ordenar", pagina)

    ato = AtoDeOrdenacao.objects.get(edital=edital, lista_id=MODALIDADE_PCD)
    assert not ato.posicoes.exists()


def test_recorte_que_o_calculo_recusa_e_impedido(client, cenario, monkeypatch):
    """`FR-818`: a recusa do domínio aparece na conferência, e o recorte não entra no alcance."""
    edital, _ = cenario
    original = conducao_do_marco.calcular_ordem

    def recusa_o_ppi(**kwargs):
        if kwargs.get("lista_id") == MODALIDADE_PPI:
            raise DomainError("empate", "Há empate a julgar antes de ordenar.", 409)
        return original(**kwargs)

    monkeypatch.setattr(conducao_do_marco, "calcular_ordem", recusa_o_ppi)
    gerir(client)

    pagina = conferir(client, edital, "ordenar").content.decode()

    assert "Impedidos (1)" in pagina
    assert "Há empate a julgar antes de ordenar." in pagina
    assert "Emitir 2 ordens" in pagina


def test_marco_de_sorteio_nao_oferece_ordenar(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """`FR-815`, `FR-817`: a ordem nasce do sorteio, e a célula leva à tela dele."""
    from tests.fixtures.sorteio import certame_com_cotas

    certame = certame_com_cotas(gestor, api_client, manager_headers, process_payload)
    identificar(client, "maria", [])
    endereco = reverse("interface:marco", args=[certame["edital"].id, certame["marco"]])

    pagina = client.get(endereco).content.decode()

    assert "Ordenar o marco" not in pagina
    assert reverse("interface:sorteio", args=[certame["edital"].id, certame["marco"]]) in pagina
    recusa = client.post(
        reverse(
            "interface:gesto-do-marco",
            args=[certame["edital"].id, certame["marco"], "ordenar"],
        )
    )
    assert recusa.status_code == 302
    assert "nasce do sorteio" in client.get(endereco).content.decode()


# --- US5 · a falha de um não apaga nem esconde os outros ---------------------------------------


def test_recusa_parcial_preserva_os_feitos(client, cenario, gestor):
    """`FR-821`, `FR-823`, `FR-824`, `SC-302`: dois feitos, um recusado, e os três no indicador."""
    edital, _ = cenario
    gerir(client)
    pagina = conferir(client, edital, "ordenar").content.decode()
    # Entre a conferência e a confirmação, alguém emite a ordem do PPI pela tela do recorte.
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="marco-049-por-fora")

    confirmar(client, edital, "ordenar", pagina)

    assert AtoDeOrdenacao.objects.filter(edital=edital).count() == 3
    marco = tela(client, edital).content.decode()
    assert "Ordenar o marco: 2 feitos, 1 recusado" in marco
    assert marco.index("<strong>Recusado</strong>") < marco.index("<strong>Feito</strong>"), (
        "os recusados vêm primeiro"
    )
    assert estados(marco, "ordenar") == ["feito", "feito", "feito"]


def test_repetir_o_envio_nao_pratica_de_novo(client, cenario):
    """`FR-822`, `SC-303`: duplo clique não emite seis ordens, e devolve o mesmo desfecho."""
    edital, _ = cenario
    gerir(client)
    pagina = conferir(client, edital, "ordenar").content.decode()

    confirmar(client, edital, "ordenar", pagina)
    confirmar(client, edital, "ordenar", pagina)

    assert AtoDeOrdenacao.objects.filter(edital=edital).count() == 3
    assert "3 feitos, 0 recusados" in tela(client, edital).content.decode()


def test_depois_de_parar_no_meio_a_conferencia_so_traz_o_que_falta(client, cenario):
    """US5, cenário 4: o que foi feito fica fora do alcance seguinte."""
    edital, _ = cenario
    gerir(client)
    pagina = conferir(client, edital, "ordenar").content.decode()
    dados = formulario_da_confirmacao(pagina)
    dados["recorte"] = ["ampla"]
    client.post(reverse("interface:gesto-do-marco", args=[edital.id, MARCO, "ordenar"]), dados)

    seguinte = conferir(client, edital, "ordenar").content.decode()

    assert "Ficam de fora (1)" in seguinte
    assert "Emitir 2 ordens" in seguinte


def test_recorte_forjado_e_404_antes_de_praticar_qualquer_um(client, cenario):
    """`SC-303`: o que não é recorte do marco recusa o gesto inteiro, e nada é gravado."""
    edital, _ = cenario
    gerir(client)
    pagina = conferir(client, edital, "ordenar").content.decode()
    dados = formulario_da_confirmacao(pagina)
    dados["recorte"].append("00000000-0000-4000-8000-000000000888")

    resposta = client.post(
        reverse("interface:gesto-do-marco", args=[edital.id, MARCO, "ordenar"]), dados
    )

    assert resposta.status_code == 404
    assert not AtoDeOrdenacao.objects.filter(edital=edital).exists()


def test_operacao_inexistente_e_404(client, cenario):
    edital, _ = cenario
    gerir(client)

    assert conferir(client, edital, "sortear").status_code == 404


# --- US3 · publicar -----------------------------------------------------------------------------


def _conferir_publicacao(client, edital, natureza="PRELIMINAR"):
    return conferir(
        client, edital, "publicar", natureza=natureza, autoridade="diretoria-cefor"
    ).content.decode()


def test_um_gesto_publica_um_resultado_por_recorte(client, cenario):
    """`FR-826`, `D-004`: natureza e autoridade uma vez; três publicações, três documentos."""
    edital, _ = cenario
    ordenar_tudo(client, edital)
    publicar(client)

    pagina = _conferir_publicacao(client, edital)
    assert "Publicar 3 resultados" in pagina
    confirmar(client, edital, "publicar", pagina)

    publicacoes = PublicacaoResultado.objects.filter(edital=edital)
    assert publicacoes.count() == 3
    assert {item.natureza for item in publicacoes} == {Natureza.PRELIMINAR}
    assert {item.publicado_por for item in publicacoes} == {"paula.publicadora"}
    assert {item.signatario_id for item in publicacoes} == {
        escolher("diretoria-cefor").identificador
    }
    assert DocumentoDoResultado.objects.filter(publicacao__in=publicacoes).count() == 3


def test_ja_publicado_na_natureza_fica_de_fora(client, cenario):
    """`FR-826`: o recorte já divulgado naquela natureza não é republicado pelo gesto."""
    edital, _ = cenario
    ordenar_tudo(client, edital)
    publicar(client)
    confirmar(client, edital, "publicar", _conferir_publicacao(client, edital))

    pagina = _conferir_publicacao(client, edital)

    assert "Ficam de fora (3)" in pagina
    assert "Não há recorte a praticar neste marco." in pagina
    assert 'class="confirmar"' not in pagina


def test_a_definitiva_pede_a_declaracao_uma_vez_e_a_grava_em_cada_uma(client, cenario):
    """`FR-827`: sem janela computável, a declaração vai para as três publicações."""
    edital, _ = cenario
    ordenar_tudo(client, edital)
    publicar(client)
    confirmar(client, edital, "publicar", _conferir_publicacao(client, edital))

    pagina = _conferir_publicacao(client, edital, natureza="DEFINITIVA")
    assert "declaracao_de_encerramento" in pagina, "o marco do cenário não declara janela"
    confirmar(
        client,
        edital,
        "publicar",
        pagina,
        declaracao_de_encerramento="O prazo recursal encerrou em 25/09.",
    )

    definitivas = PublicacaoResultado.objects.filter(edital=edital, natureza=Natureza.DEFINITIVA)
    assert definitivas.count() == 3
    assert {item.prazo_encerrado_fundamento for item in definitivas} == {
        "O prazo recursal encerrou em 25/09."
    }


def test_preliminar_depois_da_definitiva_fica_de_fora(client, cenario):
    edital, _ = cenario
    ordenar_tudo(client, edital)
    publicar(client)
    pagina = _conferir_publicacao(client, edital, natureza="DEFINITIVA")
    confirmar(client, edital, "publicar", pagina, declaracao_de_encerramento="Prazo encerrado.")

    pagina = _conferir_publicacao(client, edital)

    assert "um preliminar não sucede um definitivo" in pagina


def test_recorte_sem_ordem_e_impedido_na_publicacao(client, cenario, gestor):
    """`FR-828`: o impedimento aparece na conferência, e o recorte não entra no alcance."""
    edital, _ = cenario
    emitir_recorte(edital, gestor, chave="marco-049-so-a-ampla")
    publicar(client)

    pagina = _conferir_publicacao(client, edital)

    assert "Impedidos (2)" in pagina
    assert "Publicar 1 resultado" in pagina


def test_sem_natureza_a_conferencia_nao_e_composta(client, cenario):
    edital, _ = cenario
    ordenar_tudo(client, edital)
    publicar(client)

    resposta = conferir(client, edital, "publicar", natureza="", autoridade="diretoria-cefor")

    assert resposta.status_code == 302
    assert "natureza" in tela(client, edital).content.decode()


# --- a autoridade de cada gesto (`FR-829`, `FR-830`) ----------------------------------------------


def test_quem_gere_nao_ve_publicar_e_le_a_quem_pedir(client, cenario):
    edital, _ = cenario
    gerir(client)

    pagina = tela(client, edital).content.decode()

    assert "Ordenar o marco" in pagina and "Apurar a ocupação do marco" in pagina
    assert "Publicar o resultado do marco…" not in pagina
    assert "publicar resultado" in pagina, "a frase de a quem pedir nomeia a permissão"
    assert conferir(client, edital, "publicar", natureza="PRELIMINAR").status_code == 403


def test_quem_publica_nao_ve_os_gestos_da_comissao(client, cenario):
    edital, _ = cenario
    publicar(client)

    pagina = tela(client, edital).content.decode()

    assert "Publicar o resultado do marco" in pagina
    assert "Ordenar o marco" not in pagina
    assert conferir(client, edital, "ordenar").status_code == 403


def test_quem_so_audita_ve_o_indicador_e_nenhum_gesto(client, cenario):
    edital, _ = cenario
    identificar(client, "auditora", ["auditor"])

    pagina = tela(client, edital).content.decode()

    assert estados(pagina, "ordenar") == ["falta", "falta", "falta"]
    assert "Conduzir o marco inteiro" not in pagina


def test_quem_nao_alcanca_nenhuma_tela_do_marco_e_recusado(client, cenario):
    edital, _ = cenario
    identificar(client, "estranho", ["elaborador"])

    assert tela(client, edital).status_code == 403


# --- US4 · cortar e apurar ----------------------------------------------------------------------


def test_um_gesto_emite_uma_faixa_por_recorte(client, cenario):
    """US4, cenário 1: três recortes ordenados, três cortes."""
    edital, _ = cenario
    ordenar_tudo(client, edital)

    pagina = conferir(client, edital, "cortar").content.decode()
    assert "Emitir 3 cortes" in pagina
    confirmar(client, edital, "cortar", pagina)

    assert Corte.objects.filter(edital=edital).count() == 3
    assert estados(tela(client, edital).content.decode(), "cortar") == ["feito"] * 3


def test_corte_sem_ordem_e_impedido_e_com_faixa_fica_de_fora(client, cenario, gestor):
    """US4, cenários 2 e 5."""
    edital, _ = cenario
    emitir_recorte(edital, gestor, chave="marco-049-corte-ampla")
    gerir(client)
    confirmar(client, edital, "cortar", conferir(client, edital, "cortar").content.decode())

    pagina = conferir(client, edital, "cortar").content.decode()

    assert "Ficam de fora (1)" in pagina
    assert "Impedidos (2)" in pagina


def test_um_gesto_apura_cada_recorte(client, cenario):
    """US4, cenário 4, sem o recorte sem quadro: três apurações."""
    edital, _ = cenario
    ordenar_tudo(client, edital)

    pagina = conferir(client, edital, "apurar").content.decode()
    assert "Apurar 3 recortes" in pagina
    confirmar(client, edital, "apurar", pagina)

    assert ApuracaoDeOcupacao.objects.filter(edital=edital).count() == 3


def test_recorte_sem_quadro_e_impedido_na_apuracao(client, cenario, monkeypatch):
    """US4, cenário 4: a recusa da apuração aparece na conferência, e não depois do clique."""
    edital, _ = cenario
    ordenar_tudo(client, edital)
    original = conducao_do_marco.linha_do_quadro

    def sem_linha_para_o_ppi(conteudo, *, perfil_id, lista_id):
        if lista_id == MODALIDADE_PPI:
            return None
        return original(conteudo, perfil_id=perfil_id, lista_id=lista_id)

    monkeypatch.setattr(conducao_do_marco, "linha_do_quadro", sem_linha_para_o_ppi)

    pagina = conferir(client, edital, "apurar").content.decode()

    assert "Impedidos (1)" in pagina
    assert "não publicou quadro de vagas para este recorte" in pagina


def test_apuracao_que_mudou_desde_a_conferencia_e_recusada(client, cenario, gestor):
    """`R-4`: a apuração não tinha assinatura; o gesto confere o que ela lê, sob a trava."""
    edital, _ = cenario
    ordenar_tudo(client, edital)
    pagina = conferir(client, edital, "apurar").content.decode()
    # A ordem da ampla é sucedida entre a conferência e a confirmação.
    emitir_recorte(edital, gestor, chave="marco-049-sucede", motivo="Correção.")

    confirmar(client, edital, "apurar", pagina)

    assert ApuracaoDeOcupacao.objects.filter(edital=edital).count() == 2
    marco = tela(client, edital).content.decode()
    assert "2 feitos, 1 recusado" in marco
    assert conducao_do_marco.MUDOU_DESDE_A_CONFERENCIA in marco


def test_repetir_a_apuracao_nao_recusa_nem_apura_de_novo(client, cenario):
    """`FR-822` na apuração: a repetição não é conferida de novo, e devolve a primeira."""
    edital, _ = cenario
    ordenar_tudo(client, edital)
    pagina = conferir(client, edital, "apurar").content.decode()

    confirmar(client, edital, "apurar", pagina)
    confirmar(client, edital, "apurar", pagina)

    assert ApuracaoDeOcupacao.objects.filter(edital=edital).count() == 3
    assert "3 feitos, 0 recusados" in tela(client, edital).content.decode()


def test_onde_nada_falta_o_gesto_nao_e_oferecido(client, cenario):
    """Percurso de 28/09: num marco completo, os botões levavam à conferência vazia."""
    edital, _ = cenario
    ordenar_tudo(client, edital)

    pagina = tela(client, edital).content.decode()

    assert "Ordenar o marco…" not in pagina
    assert "Cortar o marco…" in pagina and "Apurar a ocupação do marco…" in pagina
