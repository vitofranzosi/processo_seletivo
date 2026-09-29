"""O "aplicar a todos" na tela de Retificação, ponta a ponta (051, US5, FR-938 a FR-942, SC-347).

Um Edital publicado de três Perfis com o mesmo marco — o do Edital máximo, repetido com identidades
e fatos próprios em cada Perfil. O gesto é um envio do formulário da Retificação: declara, a tela
volta com a conferência agrupada, e *Criar Retificação* confirma com a impressão do que foi
mostrado. O que se prende aqui é o ato: um só, com as Alterações digitadas e as de cada destino
marcado, e nada de quem ficou fora ou foi desmarcado.
"""

import copy
import re
from uuid import NAMESPACE_URL, uuid5

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.interface.retificacao import campos_editaveis
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import fato, rascunho_completo
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _uuid(*partes):
    return str(uuid5(NAMESPACE_URL, "teste-051-p2/" + "/".join(partes)))


def _rascunho():
    """O Edital máximo com o marco do Perfil principal repetido nos outros dois.

    Prazo recursal de 2 dias em todos. Cada Perfil declara os mesmos fatos, com identidade própria:
    o critério que compara fato precisa achar, no destino, o fato de mesmo código e tipo (FR-914).
    """
    base = rascunho_completo()
    principal = base["profiles"][0]
    modelo = principal["classificationMilestones"][0]
    modelo["appealWindow"]["durationDays"] = 2
    fatos_da_origem = {f["id"]: f["code"] for f in principal["declaredFacts"]}
    for n, perfil in enumerate(base["profiles"][1:], 2):
        perfil["declaredFacts"] = [
            fato(_uuid(str(n), f["code"]), f["code"], f["label"], f["type"])
            for f in principal["declaredFacts"]
        ]
        por_codigo = {f["code"]: f["id"] for f in perfil["declaredFacts"]}
        marco = copy.deepcopy(modelo)
        marco["id"] = _uuid(str(n), "marco")
        for criterio in marco["tiebreakers"]:
            criterio["id"] = _uuid(str(n), "criterio", str(criterio["order"]))
            if "factId" in criterio["parameters"]:
                codigo = fatos_da_origem[criterio["parameters"]["factId"]]
                criterio["parameters"] = {"factId": por_codigo[codigo]}
        perfil["classificationMilestones"] = [marco]
    return base


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=_rascunho(), anexos=1
    )
    return edital, VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def _grupo(vigente, tipo, *, perfil=0):
    perfis = vigente.content["profiles"]
    alvo = f"/profiles/id={perfis[perfil]['id']}"
    return next(
        g
        for g in campos_editaveis(vigente.content)
        if g["tipo"] == tipo and (g["caminho"] == alvo or g["caminho"].startswith(f"{alvo}/"))
    )


def _formulario(vigente, *, alteracoes=None, **extra):
    """O que a tela envia sem ninguém tocar em nada, mais os campos alterados, por caminho."""
    grupos = campos_editaveis(vigente.content)
    enviados = {"base": str(vigente.id), "chave_idempotencia": "ui-teste-051-p2"}
    enviados |= {f"campo:{c['referencia']}": c["valor"] for g in grupos for c in g["campos"]}
    referencia = {c["caminho"]: c["referencia"] for g in grupos for c in g["campos"]}
    for caminho, valor in (alteracoes or {}).items():
        enviados[f"campo:{referencia[caminho]}"] = valor
    enviados |= extra
    return enviados


def _caminho(vigente, sufixo, *, perfil=0):
    perfil_ = vigente.content["profiles"][perfil]
    marco = perfil_["classificationMilestones"][0]
    return f"/profiles/id={perfil_['id']}/classificationMilestones/id={marco['id']}/{sufixo}"


def _do_gesto(corpo, valor):
    """Os campos que a conferência devolve para o gesto: o que o próximo envio carrega."""
    campos = {"gesto": [valor]}
    impressao = re.search(rf'name="gesto_impressao:{re.escape(valor)}" value="([0-9a-f]+)"', corpo)
    assert impressao, "a conferência devolve a impressão do gesto"
    campos[f"gesto_impressao:{valor}"] = impressao.group(1)
    campos[f"gesto_mostrado:{valor}"] = "1"
    campos[f"gesto_destino:{valor}"] = re.findall(
        rf'name="gesto_destino:{re.escape(valor)}"\s+id="[^"]+"\s+value="([^"]+)" checked', corpo
    )
    return campos


def _juntar(*partes):
    enviados = {}
    for parte in partes:
        for chave, valor in parte.items():
            if chave == "gesto" and chave in enviados:
                enviados[chave] = enviados[chave] + valor
            else:
                enviados[chave] = valor
    return enviados


def _janela_em_tres(vigente):
    return _formulario(vigente, alteracoes={_caminho(vigente, "appealWindow/durationDays"): "3"})


def test_o_botao_diz_a_unidade_e_quantos_perfis_alcanca(client, seletor_ligado, publicado):
    """UX-110."""
    edital, _ = publicado
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()

    assert "Aplicar a janela recursal aos demais Perfis (2)" in corpo
    assert "Aplicar os critérios de desempate aos demais Perfis (2)" in corpo
    assert "Aplicar a forma de convocação aos demais Perfis (2)" in corpo
    assert "Aplicar a Modalidade aos demais Perfis (2)" in corpo


def test_quem_nao_elabora_nao_recebe_o_gesto(client, seletor_ligado, publicado):
    edital, _ = publicado
    identificar(client, "bruno.homologador", ["homologador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()
    assert "aos demais Perfis" not in corpo


def test_declarar_mostra_a_conferencia_agrupada_e_nao_cria_nada(client, seletor_ligado, publicado):
    """FR-916, FR-941, UX-111, UX-113 — e nada gravado."""
    edital, vigente = publicado
    identificar(client, "ana.elaboradora", ["elaborador"])
    valor = f"janela:{_grupo(vigente, 'Marco')['referencia']}"

    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {**_janela_em_tres(vigente), "aplicar": valor},
    )

    corpo = resposta.content.decode()
    assert resposta.status_code == 200
    assert "A janela recursal do Perfil P1 aos demais Perfis" in corpo
    assert "2 mudam" in corpo
    assert 'Prazo em dias: <span class="antes">2</span> → <span class="depois">3</span>' in corpo
    assert "Criar Retificação (3 Alterações)" in corpo, "o botão repete o número (UX-113)"
    assert "appealWindow" not in corpo, "o caminho normativo não chega ao HTML (FR-019)"
    assert not Retificacao.objects.filter(edital=edital).exists()


def _confirmar(client, edital, *partes):
    return client.post(
        reverse("interface:retificar", args=[edital.id]),
        _juntar(*partes, {"justificativa": "Prazo recursal da norma.", "confirmar": "1"}),
    )


def test_prazo_e_forma_de_convocacao_para_todos_num_ato_so(client, seletor_ligado, publicado):
    """SC-347, FR-941, FR-921: dois gestos, uma Retificação, uma Alteração por destino e campo."""
    edital, vigente = publicado
    identificar(client, "ana.elaboradora", ["elaborador"])
    forma = f"/profiles/id={vigente.content['profiles'][0]['id']}/callForm"
    digitado = _formulario(
        vigente,
        alteracoes={
            _caminho(vigente, "appealWindow/durationDays"): "3",
            forma: "INDIVIDUAL_MESSAGE",
        },
    )
    janela = f"janela:{_grupo(vigente, 'Marco')['referencia']}"
    convocacao = f"callForm:{_grupo(vigente, 'Perfil')['referencia']}"
    url = reverse("interface:retificar", args=[edital.id])

    primeira = client.post(url, {**digitado, "aplicar": janela}).content.decode()
    segunda = client.post(
        url, _juntar(digitado, _do_gesto(primeira, janela), {"aplicar": convocacao})
    ).content.decode()
    assert "A forma de convocação do Perfil P1 aos demais Perfis" in segunda
    resposta = _confirmar(
        client, edital, digitado, _do_gesto(segunda, janela), _do_gesto(segunda, convocacao)
    )

    assert resposta.status_code == 302, resposta.content.decode()[:3000]
    retificacao = Retificacao.objects.get(edital=edital)
    caminhos = sorted(a.target_path for a in retificacao.alteracoes.all())
    assert len(caminhos) == 6
    assert sum(c.endswith("/appealWindow/durationDays") for c in caminhos) == 3
    assert sum(c.endswith("/callForm") for c in caminhos) == 3
    registros = RegistroAuditoria.objects.filter(
        aggregate_id=retificacao.pk, operation="APLICAR_A_TODOS"
    ).order_by("occurred_at")
    assert [r.detalhe["unidade"] for r in registros] == ["janela", "callForm"]
    assert all(r.detalhe["etapa"] == "retificacao" for r in registros)
    assert [len(r.detalhe["destinos"]) for r in registros] == [2, 2]

    # Um ato, uma versão: publicada, a Retificação faz vigorar as seis de uma vez (FR-941).
    def ato(acao, **campos):
        url = reverse("interface:retificacao-ato", args=[retificacao.id, acao])
        chave = client.get(url).context["chave_idempotencia"]
        return client.post(url, {"chave_idempotencia": chave, **campos})

    versoes = VersaoConsolidada.objects.filter(edital=edital).count()
    assert ato("submeter").status_code == 302
    identificar(client, "bruno.homologador", ["homologador"])
    assert ato("homologar", motivo="Conferido").status_code == 302
    identificar(client, "carla.publicadora", ["publicador"])
    assert ato("publicar", signatario="reitoria").status_code == 302
    assert VersaoConsolidada.objects.filter(edital=edital).count() == versoes + 1
    vigente_depois = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    for perfil in vigente_depois.content["profiles"]:
        assert perfil["callForm"] == "INDIVIDUAL_MESSAGE"
        assert perfil["classificationMilestones"][0]["appealWindow"]["durationDays"] == 3


def test_a_repeticao_da_confirmacao_nao_registra_de_novo(client, seletor_ligado, publicado):
    edital, vigente = publicado
    identificar(client, "ana.elaboradora", ["elaborador"])
    valor = f"janela:{_grupo(vigente, 'Marco')['referencia']}"
    url = reverse("interface:retificar", args=[edital.id])
    corpo = client.post(url, {**_janela_em_tres(vigente), "aplicar": valor}).content.decode()

    for _ in range(2):
        assert (
            _confirmar(
                client, edital, _janela_em_tres(vigente), _do_gesto(corpo, valor)
            ).status_code
            == 302
        )

    assert Retificacao.objects.filter(edital=edital).count() == 1
    assert RegistroAuditoria.objects.filter(operation="APLICAR_A_TODOS").count() == 1


def test_o_criterio_trocado_vira_remocao_e_acrescimo_em_cada_destino(
    client, seletor_ligado, publicado
):
    """US5, cenário 1; FR-792 da `048`; FR-914: o fato é o do destino."""
    edital, vigente = publicado
    identificar(client, "ana.elaboradora", ["elaborador"])
    perfis = vigente.content["profiles"]
    marco = perfis[0]["classificationMilestones"][0]
    por_fato = next(c for c in marco["tiebreakers"] if "factId" in c["parameters"])
    nascimento = next(f for f in perfis[0]["declaredFacts"] if f["code"] == "NASCIMENTO")
    remover = next(
        g["referencia"]
        for g in campos_editaveis(vigente.content)
        if g["caminho"].endswith(f"/tiebreakers/id={por_fato['id']}")
    )
    digitado = _formulario(
        vigente,
        **{
            f"remover:{remover}": "1",
            "novo-criterio-0-id": "00000000-0000-4000-8000-000000051001",
            "novo-criterio-0-milestone": f"{perfis[0]['id']}|{marco['id']}",
            "novo-criterio-0-type": "MENOR_VALOR_DE_FATO",
            "novo-criterio-0-target": f"fato|{nascimento['id']}",
            "novo-criterio-0-whenMissing": "ULTIMO_NO_CRITERIO",
            "novo-criterio-0-order": "2",
        },
    )
    valor = f"criterios:{_grupo(vigente, 'Marco')['referencia']}"
    url = reverse("interface:retificar", args=[edital.id])
    corpo = client.post(url, {**digitado, "aplicar": valor}).content.decode()

    assert "Critérios de desempate" in corpo
    resposta = _confirmar(client, edital, digitado, _do_gesto(corpo, valor))

    assert resposta.status_code == 302, resposta.content.decode()[:3000]
    alteracoes = list(Retificacao.objects.get(edital=edital).alteracoes.all())
    for n in (1, 2):
        destino = perfis[n]
        doDestino = [
            a for a in alteracoes if a.target_path.startswith(f"/profiles/id={destino['id']}/")
        ]
        assert sorted(a.operation for a in doDestino) == ["ADD", "REMOVE"]
        acrescimo = next(a for a in doDestino if a.operation == "ADD")
        nascimento_do_destino = next(
            f["id"] for f in destino["declaredFacts"] if f["code"] == "NASCIMENTO"
        )
        assert acrescimo.new_value["parameters"] == {"factId": nascimento_do_destino}


def test_o_destino_com_campo_nao_retificavel_fica_inteiro_fora(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-939: a espécie do alvo do corte difere em P3, e nada dele entra no ato."""
    rascunho = _rascunho()
    corte = rascunho["profiles"][2]["classificationMilestones"][0]["cutRule"]
    corte.update(targetKind="FROM_VACANCY_TABLE", targetCount=None)
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho, anexos=1
    )
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    identificar(client, "ana.elaboradora", ["elaborador"])
    digitado = _formulario(vigente, alteracoes={_caminho(vigente, "cutRule/surplusCount"): "2"})
    valor = f"corte:{_grupo(vigente, 'Marco')['referencia']}"
    url = reverse("interface:retificar", args=[edital.id])

    corpo = client.post(url, {**digitado, "aplicar": valor}).content.decode()

    assert "1 muda, 1 fica fora do alcance" in corpo
    assert "a espécie do alvo do corte difere da origem, e não se corrige por Retificação" in corpo
    assert (
        "aqui: Quantas vagas o quadro publicar no recorte; na origem: Uma quantidade fixa" in corpo
    )
    assert _confirmar(client, edital, digitado, _do_gesto(corpo, valor)).status_code == 302
    caminhos = [a.target_path for a in Retificacao.objects.get(edital=edital).alteracoes.all()]
    fora = vigente.content["profiles"][2]["id"]
    assert len(caminhos) == 2
    assert not any(fora in caminho for caminho in caminhos)


def test_a_confirmacao_sobre_tela_que_mudou_e_recusada(client, seletor_ligado, publicado):
    """FR-919, SC-343: a origem mudou depois da conferência — nada criado, a de agora na tela."""
    edital, vigente = publicado
    identificar(client, "ana.elaboradora", ["elaborador"])
    valor = f"janela:{_grupo(vigente, 'Marco')['referencia']}"
    url = reverse("interface:retificar", args=[edital.id])
    corpo = client.post(url, {**_janela_em_tres(vigente), "aplicar": valor}).content.decode()
    outra = _formulario(vigente, alteracoes={_caminho(vigente, "appealWindow/durationDays"): "4"})

    resposta = _confirmar(client, edital, outra, _do_gesto(corpo, valor))

    assert resposta.status_code == 200
    assert "O que estava na tela mudou depois da conferência" in resposta.content.decode()
    assert not Retificacao.objects.filter(edital=edital).exists()


def test_o_destino_desmarcado_fica_intocado(client, seletor_ligado, publicado):
    """FR-918, SC-342."""
    edital, vigente = publicado
    identificar(client, "ana.elaboradora", ["elaborador"])
    valor = f"janela:{_grupo(vigente, 'Marco')['referencia']}"
    url = reverse("interface:retificar", args=[edital.id])
    corpo = client.post(url, {**_janela_em_tres(vigente), "aplicar": valor}).content.decode()
    gesto = _do_gesto(corpo, valor)
    so_p2 = vigente.content["profiles"][1]["id"]
    gesto[f"gesto_destino:{valor}"] = [so_p2]

    assert _confirmar(client, edital, _janela_em_tres(vigente), gesto).status_code == 302

    caminhos = [a.target_path for a in Retificacao.objects.get(edital=edital).alteracoes.all()]
    assert len(caminhos) == 2
    assert not any(vigente.content["profiles"][2]["id"] in c for c in caminhos)


def test_nenhum_destino_marcado_e_recusado(client, seletor_ligado, publicado):
    edital, vigente = publicado
    identificar(client, "ana.elaboradora", ["elaborador"])
    valor = f"janela:{_grupo(vigente, 'Marco')['referencia']}"
    url = reverse("interface:retificar", args=[edital.id])
    corpo = client.post(url, {**_janela_em_tres(vigente), "aplicar": valor}).content.decode()
    gesto = _do_gesto(corpo, valor)
    gesto[f"gesto_destino:{valor}"] = []

    resposta = _confirmar(client, edital, _janela_em_tres(vigente), gesto)

    assert resposta.status_code == 200
    assert "Nenhum Perfil marcado" in resposta.content.decode()
    assert not Retificacao.objects.filter(edital=edital).exists()


def test_desfazer_tira_o_gesto_da_tela(client, seletor_ligado, publicado):
    edital, vigente = publicado
    identificar(client, "ana.elaboradora", ["elaborador"])
    valor = f"janela:{_grupo(vigente, 'Marco')['referencia']}"
    url = reverse("interface:retificar", args=[edital.id])
    corpo = client.post(url, {**_janela_em_tres(vigente), "aplicar": valor}).content.decode()

    depois = client.post(
        url, _juntar(_janela_em_tres(vigente), _do_gesto(corpo, valor), {"desfazer_gesto": valor})
    ).content.decode()

    assert "aos demais Perfis</h3>" not in depois
    assert f'name="gesto" value="{valor}"' not in depois


def test_a_origem_sem_a_declaracao_nao_tem_o_que_aplicar(client, seletor_ligado, publicado):
    """R-013: o P2 não declara reversão."""
    edital, vigente = publicado
    identificar(client, "ana.elaboradora", ["elaborador"])
    valor = f"vacancyReversion:{_grupo(vigente, 'Perfil', perfil=1)['referencia']}"

    corpo = client.post(
        reverse("interface:retificar", args=[edital.id]), {**_formulario(vigente), "aplicar": valor}
    ).content.decode()

    assert "O Perfil P2 não declara reversão de vaga reservada: não há o que aplicar." in corpo
    assert f'name="gesto" value="{valor}"' not in corpo


def test_o_gesto_forjado_para_cartao_de_outra_especie_e_descartado(
    client, seletor_ligado, publicado
):
    edital, vigente = publicado
    identificar(client, "ana.elaboradora", ["elaborador"])
    valor = f"janela:{_grupo(vigente, 'Perfil')['referencia']}"

    corpo = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {**_janela_em_tres(vigente), "aplicar": valor},
    ).content.decode()

    assert f'name="gesto" value="{valor}"' not in corpo
