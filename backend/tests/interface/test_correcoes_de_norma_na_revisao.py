"""As telas das correções de norma da `067`: Revisão, cartão do marco e Retificação.

O documento é o que a candidata lê; a Revisão é o que quem elabora confere antes de submeter; o
cartão do marco é onde a regra se declara. As três têm de dizer a mesma coisa sobre o mesmo marco e
o mesmo Perfil — e a tela não pode exigir o que a validação deixou de exigir.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.editais.models.perfis import MarcoClassificatorio
from processo_seletivo.interface import revisao
from processo_seletivo.interface.retificacao import campos_editaveis
from tests.fixtures.snapshot import rascunho_completo
from tests.interface.conftest import marco_de_sorteio_no_formulario
from tests.interface.test_aplicar_a_todos import P1, _url

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def _texto_da_classificacao(conteudo):
    bloco = next(bloco for bloco in revisao.blocos(conteudo) if bloco["etapa"] == "classificacao")
    return "\n".join(
        "\n".join([item["titulo"], *item["linhas"], item.get("diverge", "")])
        for item in bloco["itens"]
    )


# ---- ED-03: a Revisão do marco por sorteio (FR-1315) --------------------------------------------


def test_a_revisao_do_marco_por_sorteio_nao_lista_arredondamento_nem_empate():
    conteudo = rascunho_completo()
    for perfil in conteudo["profiles"]:
        for marco in perfil["classificationMilestones"]:
            assert marco["orderProduction"] == "POR_SORTEIO"
            assert marco["rounding"] and marco["cutRule"]["tieOutcome"], "declarados"
    tudo = _texto_da_classificacao(conteudo)

    assert "Arredondamento" not in tudo
    assert "Empate no corte" not in tudo
    assert "Ordem: por sorteio" in tudo


def test_a_revisao_do_marco_por_pontuacao_continua_listando():
    conteudo = rascunho_completo()
    conteudo["profiles"] = conteudo["profiles"][:1]
    marco = conteudo["profiles"][0]["classificationMilestones"][0]
    marco.update(orderProduction="POR_PONTUACAO", drawMethod=None)
    conteudo.pop("drawMethod")
    tudo = _texto_da_classificacao(conteudo)

    assert "Arredondamento: 2 casas decimais, meio para cima" in tudo
    assert "Empate no corte: Havendo empate na última posição" in tudo


# ---- ED-03: o cartão do marco (FR-1316, UX-193, D-008) ------------------------------------------


def _recomposto(client, edital, **campos):
    url = reverse("interface:fragmento-marco-recomposto", args=[P1, 0])
    consulta = {"edital": str(edital.id), f"marco-{P1}-0-id": "m"}
    consulta.update({f"marco-{P1}-0-{chave}": valor for chave, valor in campos.items()})
    return client.get(url, consulta).content.decode()


def _visivel(corpo, campo):
    """O controle que a pessoa vê: `input type=number` da escala, ou `select` do modo."""
    if campo == "scale":
        return re.search(rf'<input type="number"[^>]*name="marco-{P1}-0-scale"', corpo, re.S)
    return re.search(rf'<select[^>]*name="marco-{P1}-0-mode"', corpo)


def _oculto(corpo, campo, valor):
    return re.search(rf'<input type="hidden" name="marco-{P1}-0-{campo}" value="{valor}"', corpo)


def test_o_cartao_por_sorteio_nao_mostra_o_arredondamento_e_o_leva_oculto(client, tres_perfis):
    corpo = _recomposto(client, tres_perfis, orderProduction="POR_SORTEIO")

    assert not _visivel(corpo, "scale") and not _visivel(corpo, "mode")
    assert "Casas decimais" not in corpo
    # Sem arredondamento no marco, os ocultos levam o padrão de marco novo: é o que a troca para
    # pontuação devolve à tela, sem campo em branco que a pessoa não esvaziou.
    assert _oculto(corpo, "scale", "2") and _oculto(corpo, "mode", "MEIO_PARA_CIMA")


def test_o_cartao_por_sorteio_leva_oculto_o_arredondamento_que_o_marco_tinha(client, tres_perfis):
    corpo = _recomposto(
        client, tres_perfis, orderProduction="POR_SORTEIO", scale="3", mode="TRUNCAR"
    )

    assert _oculto(corpo, "scale", "3") and _oculto(corpo, "mode", "TRUNCAR")


def test_ao_passar_para_pontuacao_os_campos_voltam_preenchidos(client, tres_perfis):
    """O `htmx` recompõe o cartão com o que o formulário enviou — inclusive os ocultos."""
    corpo = _recomposto(
        client, tres_perfis, orderProduction="POR_PONTUACAO", scale="2", mode="MEIO_PARA_CIMA"
    )

    assert _visivel(corpo, "scale") and _visivel(corpo, "mode")
    assert re.search(rf'name="marco-{P1}-0-scale"\s+value="2"', corpo)
    assert '<option value="MEIO_PARA_CIMA" selected>' in corpo


def test_salvar_o_marco_por_sorteio_nao_grava_arredondamento(client, tres_perfis):
    """D-008: a regra inerte sai do conteúdo, e não só do documento."""
    dados = marco_de_sorteio_no_formulario(P1)
    assert dados[f"marco-{P1}-0-scale"] == "2", "o formulário ainda a envia, oculta"
    resposta = client.post(_url(tres_perfis, "classificacao"), dados)

    assert resposta.status_code == 302, resposta.content
    assert MarcoClassificatorio.objects.get(perfil_id=P1).arredondamento == {}


def test_a_ajuda_diz_que_o_arredondamento_e_da_ordem_por_pontuacao(client, tres_perfis):
    """UX-193. A ajuda só aparece com um marco na tela, e por isso o marco é gravado antes."""
    resposta = client.post(_url(tres_perfis, "classificacao"), marco_de_sorteio_no_formulario(P1))
    assert resposta.status_code == 302, resposta.content
    corpo = " ".join(client.get(_url(tres_perfis, "classificacao")).content.decode().split())

    assert "O arredondamento só se aplica à ordem por pontuação" in corpo


# ---- ED-03: a Retificação (FR-1317) -------------------------------------------------------------


def _rotulo_do_vazio_do_modo(conteudo, codigo_do_perfil):
    for grupo in campos_editaveis(conteudo):
        if grupo["tipo"] == "Marco" and grupo["nome"].endswith(codigo_do_perfil):
            campo = next(c for c in grupo["campos"] if c["chave"] == "rounding/mode")
            return campo["rotulo_do_vazio"]
    raise AssertionError("marco não encontrado")


def test_na_retificacao_o_vazio_do_modo_sob_sorteio_nao_anuncia_impedimento():
    conteudo = rascunho_completo()
    conteudo["profiles"][0]["classificationMilestones"][0]["rounding"] = {}

    rotulo = _rotulo_do_vazio_do_modo(conteudo, conteudo["profiles"][0]["code"])
    assert "impedida" not in rotulo
    assert "sorteada" in rotulo


def test_na_retificacao_o_vazio_do_modo_sob_pontuacao_continua_anunciando():
    conteudo = rascunho_completo()
    marco = conteudo["profiles"][0]["classificationMilestones"][0]
    marco.update(orderProduction="POR_PONTUACAO", rounding={})

    rotulo = _rotulo_do_vazio_do_modo(conteudo, conteudo["profiles"][0]["code"])
    assert rotulo == "Não declarado — a publicação será impedida"


# ---- ED-12: a Revisão do Perfil sem vaga imediata (UX-192) --------------------------------------


def _linhas_do_perfil(conteudo, codigo):
    bloco = next(bloco for bloco in revisao.blocos(conteudo) if bloco["etapa"] == "perfis")
    item = next(item for item in bloco["itens"] if item["titulo"].startswith(f"{codigo} "))
    return item["linhas"]


def _zerado(conteudo):
    perfil = conteudo["profiles"][0]
    perfil["immediateVacancies"] = 0
    for linha in perfil["vacancyTable"]:
        linha["immediateVacancies"] = 0
    assert perfil["vacancyReversion"], "a reversão continua declarada"
    return conteudo, perfil["code"]


def test_a_reversao_do_perfil_sem_vaga_diz_que_nao_sai_no_documento():
    conteudo, codigo = _zerado(rascunho_completo())
    linha = next(
        linha
        for linha in _linhas_do_perfil(conteudo, codigo)
        if linha.startswith("Reverter vaga reservada")
    )

    assert linha.endswith("não sai no documento: o Perfil não tem vaga imediata")
    assert "só quando a lista reservada esgota" in linha, "o que foi escolhido continua dito"


def test_a_reversao_do_perfil_com_vaga_nao_tem_a_nota():
    conteudo = rascunho_completo()
    codigo = conteudo["profiles"][0]["code"]
    linhas = _linhas_do_perfil(conteudo, codigo)

    assert not [linha for linha in linhas if "não sai no documento" in linha]


# ---- ED-02: o aviso de conferência de recurso na Revisão (UX-191) -------------------------------


def test_a_revisao_mostra_o_aviso_com_link_para_o_cronograma_e_nao_impede(
    client, seletor_ligado, edital
):
    from tests.interface.conftest import compor_rascunho, identificar
    from tests.interface.test_compor import PERFIL, eventos, perfis

    identificar(client, "ana.elaboradora", ["elaborador"])
    marco = marco_de_sorteio_no_formulario(PERFIL)
    base = f"marco-{PERFIL}-0"
    marco.update({f"{base}-appealDeclaration": "admite", f"{base}-appealDurationDays": "2"})
    compor_rascunho(client, edital, perfis(), eventos(), marco)
    edital.refresh_from_db()

    resposta = client.get(reverse("interface:compor-etapa", args=[edital.id, "revisao"]))
    pendencias = resposta.context["pendencias"]
    (aviso,) = [p for p in pendencias if p["codigo"] == "appeal_schedule_review"]
    html = " ".join(resposta.content.decode().split())

    assert "Prazos de recurso a conferir." in html
    assert "O Cronograma não tem Evento de recurso" in html
    assert reverse("interface:compor-etapa", args=[edital.id, "cronograma"]) in html
    assert aviso["etapa"] == "cronograma" and aviso["corrigivel"]
    assert aviso["severidade"] == "aviso"
