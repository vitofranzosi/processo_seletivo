"""Tela de Retificação (US4 da 002).

O que se verifica: a pessoa edita o conteúdo vigente e o sistema deriva as Alterações
Normativas; o antes e o depois são apresentados; a vigência futura é dita explicitamente; e
nada muda para o público antes da Publicação.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.edital import caminho_perfil
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

TODOS = ["elaborador", "homologador", "publicador"]
VAGAS = caminho_perfil("immediateVacancies")


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.fixture
def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def campos(vigente, **alteracoes):
    """Todos os campos como estão hoje, com as alterações pedidas por cima.

    O teste fala em caminho normativo porque é o que se lê; o formulário fala em referência
    opaca, porque é o que a tela entrega (FR-019). A tradução entre os dois é o que este helper
    faz — e é a mesma que a tela faz, ao contrário.
    """
    from processo_seletivo.interface.retificacao import campos_editaveis

    grupos = campos_editaveis(vigente.content)
    campos_do_formulario = [campo for grupo in grupos for campo in grupo["campos"]]
    # A versão base acompanha o formulário: sem ela as referências não significam nada.
    enviados = {"base": str(vigente.id)}
    enviados |= {f"campo:{campo['referencia']}": campo["valor"] for campo in campos_do_formulario}
    referencia = {campo["caminho"]: campo["referencia"] for campo in campos_do_formulario}
    enviados.update(
        {f"campo:{referencia[caminho]}": valor for caminho, valor in alteracoes.items()}
    )
    return enviados


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_editar_o_vigente_deriva_as_alteracoes(client, seletor_ligado, edital, vigente):
    """A pessoa não digita caminho JSON Pointer; ela edita o conteúdo e o sistema deduz."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{VAGAS: "9"}),
            "justificativa": "Ampliação de vagas",
        },
    )
    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "O que vai mudar (1)" in corpo
    assert "Vagas imediatas" in corpo
    assert not Retificacao.objects.exists(), "ver o que muda não cria a Retificação"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_confirmar_cria_a_retificacao_com_as_alteracoes_derivadas(
    client, seletor_ligado, edital, vigente
):
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{VAGAS: "9", "/title": "Novo título"}),
            "justificativa": "Ampliação de vagas e ajuste de título",
            "confirmar": "1",
        },
    )
    assert resposta.status_code == 302

    retificacao = Retificacao.objects.get()
    caminhos = {a.target_path: a.new_value for a in retificacao.alteracoes.all()}
    assert caminhos == {VAGAS: 9, "/title": "Novo título"}
    assert retificacao.status == Retificacao.Status.EM_ELABORACAO
    assert retificacao.justification == "Ampliação de vagas e ajuste de título"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_sem_alteracao_nenhuma_a_tela_recusa_antes_do_dominio(
    client, seletor_ligado, edital, vigente
):
    """Retificação sem efeito é recusada pelo domínio; a tela evita chegar até lá."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {**campos(vigente), "justificativa": "Nada muda", "confirmar": "1"},
    )
    assert resposta.status_code == 200
    assert "Nenhum campo foi alterado" in resposta.content.decode()
    assert not Retificacao.objects.exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_vigencia_futura_e_dita_explicitamente(client, seletor_ligado, edital, vigente):
    """FR-015: a tela precisa dizer a partir de quando o novo conteúdo passa a valer."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{VAGAS: "9"}),
            "justificativa": "Vigência futura",
            "vigencia": "2027-03-01T09:00",
            "confirmar": "1",
        },
    )
    retificacao = Retificacao.objects.get()
    assert retificacao.effective_at.year == 2027

    corpo = client.get(
        reverse("interface:retificacao-detalhe", args=[retificacao.id])
    ).content.decode()
    assert "01/03/2027" in corpo
    assert "o conteúdo atual continua valendo" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_detalhe_mostra_antes_e_depois_de_cada_alteracao(client, seletor_ligado, edital, vigente):
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{VAGAS: "9"}),
            "justificativa": "Ampliação",
            "confirmar": "1",
        },
    )
    corpo = client.get(
        reverse("interface:retificacao-detalhe", args=[Retificacao.objects.get().id])
    ).content.decode()
    assert VAGAS in corpo, "o detalhe do ato mostra o caminho, que nomeia a entidade"
    assert 'class="antes">1<' in corpo, "o valor vigente aparece como antes"
    assert 'class="depois">9<' in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_fluxo_da_retificacao_ate_a_publicacao(client, seletor_ligado, edital, vigente):
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{VAGAS: "9"}),
            "justificativa": "Ampliação",
            "confirmar": "1",
        },
    )
    retificacao = Retificacao.objects.get()
    antes = client.get(f"/api/v1/public/editais/{edital.id}/versao-vigente").json()["content"][
        "profiles"
    ][0]["immediateVacancies"]
    assert antes == 1, "nada muda para o público antes da Publicação"

    def ato(acao, **campos_extra):
        url = reverse("interface:retificacao-ato", args=[retificacao.id, acao])
        chave = client.get(url).context["chave_idempotencia"]
        return client.post(url, {"chave_idempotencia": chave, **campos_extra})

    assert ato("submeter").status_code == 302
    identificar(client, "bruno.homologador", ["homologador"])
    retificacao.refresh_from_db()
    assert ato("homologar", motivo="Conferido").status_code == 302
    identificar(client, "carla.publicadora", ["publicador"])
    retificacao.refresh_from_db()
    resposta = ato(
        "publicar",
        signatario_nome="Reitora",
        signatario_cargo="Reitora",
        signatario_id="00000000-0000-0000-0000-0000000000a1",
    )
    assert resposta.status_code == 302

    depois = client.get(f"/api/v1/public/editais/{edital.id}/versao-vigente").json()["content"][
        "profiles"
    ][0]["immediateVacancies"]
    assert depois == 9, "publicada, a Retificação passa a compor o conteúdo vigente"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_retificar_exige_edital_publicado(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    from processo_seletivo.processos.models import Edital

    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    em_elaboracao = Edital.objects.get()
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.get(reverse("interface:retificar", args=[em_elaboracao.id]))

    # O Edital existe e está no escopo de quem pediu: 404 diria "não existe" e esconderia
    # a razão real, que é a situação em que ele está.
    assert resposta.status_code == 409
    assert "Só é possível retificar um Edital publicado" in resposta.content.decode()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_confirmacao_de_publicacao_mostra_o_que_passara_a_vigorar(
    client, seletor_ligado, edital, vigente
):
    identificar(client, "joao.completo", TODOS)
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{VAGAS: "9"}),
            "justificativa": "Ampliação",
            "confirmar": "1",
        },
    )
    retificacao = Retificacao.objects.get()
    corpo = client.get(
        reverse("interface:retificacao-ato", args=[retificacao.id, "publicar"])
    ).content.decode()
    assert "Este ato não pode ser desfeito" in corpo
    assert "Conteúdo que passará a vigorar" in corpo
    assert "continuam preservadas e consultáveis" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_tela_nao_entrega_caminho_normativo_no_html(client, seletor_ligado, edital, vigente):
    """FR-019, primeira condição (SC-004).

    Quem elabora um Edital tem um problema administrativo, não um problema de representação. O
    formulário identifica seus campos por referência opaca — `g2c3` —, e o caminho normativo é
    reconstruído no servidor. Se um caminho voltar ao HTML, a tela terá passado a ensinar uma
    sintaxe que ninguém pediu para aprender.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()

    for vestigio in ("/profiles", "/schedule", "targetPath"):
        assert vestigio not in corpo, f"a tela entregou {vestigio!r} para quem elabora"
    # `id="conteudo"` é atributo HTML e não seletor; o que não pode aparecer é `id=<uuid>`.
    assert re.search(r"id=[0-9a-f]{8}-", corpo) is None, "a tela entregou um seletor de identidade"
    assert 'name="campo:g1c1"' in corpo, "os campos são identificados por referência opaca"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_tela_emite_alteracoes_pela_chave_da_entidade(client, seletor_ligado, edital, vigente):
    """FR-019, segunda condição (SC-004): o que ela emite usa a forma por chave."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {**campos(vigente, **{VAGAS: "9"}), "justificativa": "Ampliação", "confirmar": "1"},
    )

    alteracoes = Retificacao.objects.get().alteracoes.all()
    assert [item.target_path for item in alteracoes] == [VAGAS]
    assert all("id=" in item.target_path for item in alteracoes)


@pytest.fixture
def edital_com_tres_perfis(api_client, manager_headers, process_payload):
    from tests.fixtures.snapshot import rascunho_publicavel

    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_publicavel()
    )


def referencia_do_campo(conteudo, caminho):
    from processo_seletivo.interface.retificacao import campos_editaveis

    return next(
        campo["referencia"]
        for grupo in campos_editaveis(conteudo)
        for campo in grupo["campos"]
        if campo["caminho"] == caminho
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_publicacao_concorrente_nao_desloca_o_alvo_do_formulario(
    client, api_client, seletor_ligado, edital_com_tres_perfis
):
    """SC-002 pelo lado da tela: a referência do formulário não pode mudar de dono.

    A referência `g3c1` é a posição do campo no formulário, e só significa alguma coisa contra o
    conteúdo que a gerou. Se o POST for resolvido contra a versão vigente do momento, uma
    Publicação que remova um Perfil anterior entre abrir a tela e confirmar faz a mesma
    referência apontar para outra entidade — a pessoa edita o Perfil que viu e o ato sai sobre
    outro. É o mesmo defeito que a feature veio eliminar, reaparecendo uma camada acima.
    """
    from tests.fixtures.publicacao import retify
    from tests.fixtures.snapshot import PERFIL

    edital = edital_com_tres_perfis
    base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    referencia = referencia_do_campo(base.content, f"/profiles/id={PERFIL['B']}/name")

    # Entre abrir a tela e confirmar, outra pessoa remove o primeiro Perfil.
    retify(
        api_client,
        edital,
        [{"targetPath": f"/profiles/id={PERFIL['A']}", "operation": "REMOVE"}],
        suffix="z",
    )
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert [p["id"] for p in vigente.content["profiles"]] == [PERFIL["B"], PERFIL["C"]]

    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            "base": str(base.id),
            f"campo:{referencia}": "B editado",
            "justificativa": "Ajuste no Perfil B",
            "confirmar": "1",
        },
    )

    pela_tela = Retificacao.objects.exclude(status=Retificacao.Status.PUBLICADA).get()
    alteracao = pela_tela.alteracoes.get()
    assert alteracao.target_path == f"/profiles/id={PERFIL['B']}/name"
    assert PERFIL["C"] not in alteracao.target_path, (
        "a referência do formulário passou a apontar para outro Perfil"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_formulario_transporta_a_versao_de_que_partiu(client, seletor_ligado, edital, vigente):
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()

    assert f'name="base" value="{vigente.id}"' in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_versao_base_desconhecida_nao_e_recomposta_em_silencio(
    client, seletor_ligado, edital, vigente
):
    """Cair de volta na versão vigente produziria alterações sobre conteúdo que ninguém viu."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {"base": "00000000-0000-0000-0000-0000000009ff", "justificativa": "x"},
    )

    assert resposta.status_code == 409
    assert "não está mais disponível" in resposta.content.decode()
    assert not Retificacao.objects.exists()


@pytest.mark.parametrize("base_enviada", ["", "abc", "../etc/passwd", "00000000-0000-0000-0000"])
@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_versao_base_ilegivel_e_recusada_e_nao_estoura(
    client, seletor_ligado, edital, vigente, base_enviada
):
    """A versão vinha do formulário, e o que vem do formulário pode chegar torto.

    Consultar o banco com um texto que não é UUID levantava `ValidationError` fora de qualquer
    tratamento — 500 onde a resposta certa é a mesma recusa da versão desconhecida.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {"base": base_enviada, "justificativa": "x"},
    )

    assert resposta.status_code == 409
    assert "não está mais disponível" in resposta.content.decode()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_post_sem_a_versao_base_nao_cai_na_vigente(client, seletor_ligado, edital, vigente):
    """Formulário antigo que não envie a versão resolveria as referências contra outro conteúdo.

    Cair para a vigente era exatamente o defeito que o campo veio impedir; a omissão precisa
    doer tanto quanto a versão desconhecida.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(reverse("interface:retificar", args=[edital.id]), {"justificativa": "x"})

    assert resposta.status_code == 409
    assert not Retificacao.objects.exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_retificacao_alcanca_modalidade_etapa_e_secao_pela_interface(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """A `006` publicou as três e não trouxe nenhuma para a tela.

    O motor já as endereçava — `/stages/id=…`, `/sections/id=…/content` e
    `…/normativeRule/percentage` têm teste desde a `006`. Corrigir uma cota errada depois de
    publicada exigia chamada de API, e a Constituição não admite jornada concluída por canal
    alheio ao ator.
    """
    from processo_seletivo.editais.domain import secoes as catalogo
    from tests.fixtures.snapshot import ETAPA, MODALIDADE, PERFIL, rascunho_com_etapas

    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas()
    )
    base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    identificar(client, "ana.elaboradora", ["elaborador"])

    caminhos = {
        "percentual": (
            f"/profiles/id={PERFIL['A']}/competitionModalities/id={MODALIDADE['B']}"
            "/normativeRule/percentage"
        ),
        "etapa": f"/stages/id={ETAPA['A']}/name",
        "secao": f"/sections/id={catalogo.identidade(edital.id, 'recursos')}/content",
    }
    referencias = {
        nome: referencia_do_campo(base.content, caminho) for nome, caminho in caminhos.items()
    }

    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            "base": str(base.id),
            f"campo:{referencias['percentual']}": "25",
            f"campo:{referencias['etapa']}": "Prova didática e arguição",
            f"campo:{referencias['secao']}": "Prazo recursal de três dias úteis.",
            "justificativa": "Ajuste de cota, etapa e texto",
        },
    )

    resumo = resposta.context["resumo"]
    alterados = {item["rotulo"] for item in resumo}
    assert {"Percentual (%)", "Nome da Etapa", "Texto da seção"} <= alterados, resumo
    # A forma canônica do decimal é preservada: "25" digitado vira "25.0000" no conteúdo.
    percentual = next(item for item in resumo if item["rotulo"] == "Percentual (%)")
    assert percentual["depois"] == "25.0000"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_secao_nao_e_removivel_pela_retificacao(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """O catálogo é fixo: a topologia recusa remover seção, e a tela não pode oferecer o que a
    publicação recusa."""
    from processo_seletivo.interface import retificacao as ui

    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")

    grupos = ui.campos_editaveis(base.content)
    secoes = [grupo for grupo in grupos if grupo["caminho"].startswith("/sections/")]

    assert secoes, "as seções textuais precisam estar editáveis"
    assert [grupo for grupo in secoes if grupo["removivel"]] == []
    # E as geradas não aparecem: elas não têm conteúdo próprio a endereçar.
    assert len(secoes) == len(catalogo_textuais())


def catalogo_textuais():
    from processo_seletivo.editais.domain import secoes as catalogo

    return [secao for secao in catalogo.CATALOGO if not secao.gerada]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@pytest.mark.parametrize("chave", ["apresentacao", "requisitos-gerais", "classificacao"])
def test_retificar_alcanca_as_secoes_institucionais_novas(
    client, seletor_ligado, api_client, manager_headers, process_payload, chave
):
    """T015 — as três seções da `007` entram na Retificação **sozinhas**, e isto prova que sim.

    A tela deriva do catálogo, então elas *deveriam* aparecer sem código novo. "Deveriam" não é
    cobertura: sem este teste, o dia em que a derivação virar lista fixa passaria em silêncio, e
    corrigir a apresentação de um Edital publicado voltaria a exigir chamada de API.
    """
    from processo_seletivo.editais.domain import secoes as catalogo

    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    identificar(client, "ana.elaboradora", ["elaborador"])

    caminho = f"/sections/id={catalogo.identidade(edital.id, chave)}/content"
    referencia = referencia_do_campo(base.content, caminho)
    texto_novo = f"Redação institucional revista para {chave}."

    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            "base": str(base.id),
            f"campo:{referencia}": texto_novo,
            "justificativa": f"Revisão da seção {chave}",
        },
    )

    resumo = resposta.context["resumo"]
    alterado = next(item for item in resumo if item["depois"] == texto_novo)
    assert alterado["rotulo"] == "Texto da seção"

    # E o caminho da seção nova é de fato editável na tela — não é o rótulo que coincide.
    from processo_seletivo.interface import retificacao as ui

    editaveis = {
        campo["caminho"] for grupo in ui.campos_editaveis(base.content) for campo in grupo["campos"]
    }
    assert caminho in editaveis
