"""Os ajustes de leitura da composição (132): a Revisão por momento, o somente leitura de verdade e
a ajuda dos documentos.

O Edital publicado é o rascunho máximo dos testes: três Perfis com marco por sorteio, dois Eventos,
duas Etapas e três documentos — dois da inscrição e um da convocação. Publicado, ele é somente
leitura para qualquer um, que é o caso que o guia da seção C fotografou no 90/2026.
"""

import re
from html.parser import HTMLParser

import pytest
from django.urls import reverse

from processo_seletivo.interface import revisao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import rascunho_completo
from tests.interface.conftest import identificar

ETAPAS_DE_CARTOES = ("inscricao", "perfis", "cronograma", "etapas", "classificacao")


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo()
    )
    return Edital.objects.get(pk=edital.pk)


def _etapa(client, edital, nome):
    resposta = client.get(reverse("interface:compor-etapa", args=[edital.id, nome]))
    assert resposta.status_code == 200
    return resposta.content.decode()


# ------------------------------------------------------------------ o que a página tem, lido


class _Controles(HTMLParser):
    """Os controles do formulário da etapa, com o que decide se a pessoa os usa.

    `desabilitado` é o efetivo: o atributo no próprio controle **ou** num `fieldset` acima dele,
    que é como o navegador o lê. `dentro` são os `id` dos ancestrais, para recortar o cartão de um
    Perfil.
    """

    VAZIOS = {"input", "br", "img", "hr", "meta", "link", "source", "wbr", "area", "col"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pilha = []
        self.controles = []
        self._select = None
        self._textarea = None

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        desabilitado_acima = any(
            item["tag"] == "fieldset" and item["disabled"] for item in self.pilha
        )
        no_formulario = any(item["id"] == "formulario" for item in self.pilha)
        if tag in ("input", "select", "textarea", "button") and no_formulario:
            controle = {
                "tag": tag,
                "atributos": atributos,
                "desabilitado": "disabled" in atributos or desabilitado_acima,
                "dentro": {item["id"] for item in self.pilha if item["id"]},
                "valores": [],
                "texto": "",
            }
            self.controles.append(controle)
            if tag == "select":
                self._select = controle
            if tag in ("textarea", "button"):
                self._textarea = controle
        if tag == "option" and self._select is not None and "selected" in atributos:
            self._select["valores"].append(atributos.get("value", ""))
        if tag not in self.VAZIOS:
            self.pilha.append(
                {"tag": tag, "id": atributos.get("id"), "disabled": "disabled" in atributos}
            )

    def handle_endtag(self, tag):
        if tag == "select":
            self._select = None
        if tag in ("textarea", "button"):
            self._textarea = None
        if tag in self.VAZIOS:
            return
        while self.pilha:
            if self.pilha.pop()["tag"] == tag:
                break

    def handle_data(self, data):
        if self._textarea is not None:
            self._textarea["texto"] += data


def _controles(corpo):
    leitor = _Controles()
    leitor.feed(corpo)
    return leitor.controles


def _campos(controles):
    return [c for c in controles if c["tag"] != "button" and c["atributos"].get("type") != "hidden"]


def _consultas(controles):
    """Os botões que só leem: simular e conferir na Caixa (FR-4507)."""
    return [
        c
        for c in controles
        if c["tag"] == "button"
        and (
            "data-abre-previa" in c["atributos"]
            or "conferir-referencia" in (c["atributos"].get("hx-get") or "")
        )
    ]


# ------------------------------------------------------------------ US1: a Revisão por momento


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_revisao_separa_os_documentos_por_momento(publicado):
    """SC-1401: cada documento uma vez, no bloco do seu momento, e as contagens somam o total."""
    blocos = revisao.blocos(edital_snapshot(publicado))
    documentos = {b["titulo"]: b for b in blocos if b["titulo"].startswith("Documentos Exigidos")}

    assert list(documentos) == [
        "Documentos Exigidos na inscrição",
        "Documentos Exigidos na convocação",
    ], "inscrição antes da convocação, como no PDF"
    na_inscricao = [
        item["titulo"] for item in documentos["Documentos Exigidos na inscrição"]["itens"]
    ]
    na_convocacao = [
        item["titulo"] for item in documentos["Documentos Exigidos na convocação"]["itens"]
    ]
    assert na_inscricao == ["1. Documento de identificação", "2. Diploma de graduação"]
    assert na_convocacao == ["3. Documento de identificação atualizado"], "o número é o declarado"
    assert {b["etapa"] for b in documentos.values()} == {"inscricao"}


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_item_perde_a_linha_pedido_e_guarda_as_demais(publicado):
    """FR-4503: o bloco diz o momento; exigência, alcance e instruções continuam."""
    blocos = revisao.blocos(edital_snapshot(publicado))
    linhas = [
        str(linha)
        for bloco in blocos
        if bloco["titulo"].startswith("Documentos Exigidos")
        for item in bloco["itens"]
        for linha in item["linhas"]
    ]

    assert not [linha for linha in linhas if linha.startswith("Pedido")]
    assert "Exigência: obrigatória" in linhas
    assert "Aplica-se a: todos os candidatos" in linhas


def test_sem_documento_da_convocacao_a_revisao_tem_um_bloco_so():
    """FR-4502: como a seção do PDF, o bloco da convocação só existe quando há o que dizer."""
    sem_convocacao = revisao._documentos_por_momento(
        {"documentRequirements": [{"id": "d1", "name": "Diploma", "order": 1}]}
    )
    vazio = revisao._documentos_por_momento({"documentRequirements": []})

    assert [b["titulo"] for b in sem_convocacao] == ["Documentos Exigidos na inscrição"]
    assert [b["titulo"] for b in vazio] == ["Documentos Exigidos na inscrição"]
    assert vazio[0]["itens"] == [], "a tela diz 'Nada declarado.', como o bloco único dizia"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_tela_da_revisao_mostra_os_dois_blocos_com_a_contagem(client, seletor_ligado, publicado):
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = _etapa(client, publicado, "revisao")

    assert re.search(r">Documentos Exigidos na inscrição \(2\)</h3>", corpo)
    assert re.search(r">Documentos Exigidos na convocação \(1\)</h3>", corpo)
    assert "Pedido:" not in re.sub(r"<[^>]+>", "", corpo)


# ------------------------------------------------------------------ US2: somente leitura


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@pytest.mark.parametrize("nome", ETAPAS_DE_CARTOES)
def test_fora_de_elaboracao_nenhum_campo_aceita_digitacao(client, seletor_ligado, publicado, nome):
    """SC-1402, FR-4504: o aviso diz somente leitura, e agora os campos também."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = _etapa(client, publicado, nome)
    controles = _controles(corpo)
    campos = _campos(controles)

    assert "Somente leitura" in corpo
    assert campos, f"{nome} sem campo algum: o teste não leria nada"
    habilitados = [c["atributos"].get("name") for c in campos if not c["desabilitado"]]
    assert habilitados == [], f"{nome}: {habilitados}"
    botoes_ativos = [c for c in controles if c["tag"] == "button" and not c["desabilitado"]]
    assert [b for b in botoes_ativos if b not in _consultas(controles)] == [], (
        "só os botões que leem ficam ativos"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@pytest.mark.parametrize("nome", ETAPAS_DE_CARTOES)
def test_fora_de_elaboracao_a_lista_nao_oferece_mudar(client, seletor_ligado, publicado, nome):
    """FR-4505: setas, lixeira, acrescentar, remover, aplicar e duplicar não aparecem."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = _etapa(client, publicado, nome)
    formulario = corpo[corpo.index('id="formulario"') : corpo.index("</form>")]

    assert "data-mover" not in formulario
    assert "fragmento-remover" not in formulario
    assert ">Acrescentar" not in formulario
    assert 'name="aplicar"' not in formulario
    assert "Partir de outro" not in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@pytest.mark.parametrize("nome", [*ETAPAS_DE_CARTOES, "identificacao", "conteudo"])
def test_fora_de_elaboracao_avancar_e_link(client, seletor_ligado, publicado, nome):
    """FR-4506: "Avançar" enviava o formulário, e a resposta era "Não foi possível salvar"."""
    from processo_seletivo.interface.views import CHAVES_ETAPA

    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = _etapa(client, publicado, nome)
    proxima = CHAVES_ETAPA[CHAVES_ETAPA.index(nome) + 1]
    destino = reverse("interface:compor-etapa", args=[publicado.id, proxima])

    assert 'name="destino"' not in corpo
    assert re.search(rf'<a [^>]*href="{destino}"[^>]*>Avançar ›</a>', corpo)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_recusa_do_servidor_continua(client, seletor_ligado, publicado):
    """FR-4508: a tela deixou de oferecer; o servidor continua recusando quem envia assim mesmo."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(
        reverse("interface:compor-etapa", args=[publicado.id, "inscricao"]),
        {"destino": "inscricao", "teto-inscricoes": "3"},
    )

    assert resposta.status_code == 200
    assert "não está em elaboração ou você não tem permissão" in resposta.content.decode()


@pytest.mark.django_db
@pytest.mark.integration
def test_sem_permissao_de_elaborar_tambem_e_leitura(client, seletor_ligado, com_etapas):
    """O Edital em elaboração, aberto por quem homologa: o mesmo aviso, e os mesmos campos."""
    identificar(client, "bruno.homologador", ["homologador"])
    corpo = _etapa(client, com_etapas, "perfis")
    campos = _campos(_controles(corpo))

    assert campos and all(c["desabilitado"] for c in campos)
    assert "data-mover" not in corpo


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize("nome", ["perfis", "etapas", "classificacao"])
def test_a_composicao_editavel_nao_muda(client, seletor_ligado, com_etapas, nome):
    """FR-4509: quem elabora continua com campos, setas, acrescentar e o envio da etapa."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = _etapa(client, com_etapas, nome)
    campos = _campos(_controles(corpo))

    assert campos and not [c for c in campos if c["desabilitado"]]
    assert 'name="destino"' in corpo
    assert "data-somente-leitura" not in corpo
    assert "somente-leitura.js" not in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_classificacao_somente_leitura_ainda_simula(client, seletor_ligado, publicado):
    """SC-1403, FR-4507: os botões de consulta ficam, e o que o cartão mostra basta à prévia.

    O script que devolve ao pedido os campos desabilitados roda no navegador; aqui o pedido é
    montado com a mesma regra — cada campo do cartão, desabilitado ou não, com o valor que exibe —
    e a prévia tem de responder com o sorteio, e não com "sem marco".
    """
    identificar(client, "bruno.homologador", ["homologador"])
    corpo = _etapa(client, publicado, "classificacao")
    controles = _controles(corpo)
    simular = [c for c in _consultas(controles) if "data-abre-previa" in c["atributos"]]

    assert simular and not any(c["desabilitado"] for c in _consultas(controles))
    assert "data-somente-leitura" in corpo and "somente-leitura.js" in corpo

    botao = simular[0]
    perfil = re.search(r"#cartao-([0-9a-f-]+)", botao["atributos"]["hx-include"]).group(1)
    dados = {}
    for campo in controles:
        nome = campo["atributos"].get("name")
        if not nome or campo["tag"] == "button" or f"cartao-{perfil}" not in campo["dentro"]:
            continue
        tipo = campo["atributos"].get("type")
        if tipo in ("checkbox", "radio") and "checked" not in campo["atributos"]:
            continue
        if campo["tag"] == "select":
            valores = campo["valores"]
        elif campo["tag"] == "textarea":
            valores = [campo["texto"]]
        else:
            valores = [campo["atributos"].get("value", "")]
        dados.setdefault(nome, []).extend(valores)

    # O `edital` vem da query do botão: o cliente de teste troca a query inteira pelos `dados`.
    caminho, query = botao["atributos"]["hx-get"].split("?")
    dados["edital"] = query.removeprefix("edital=")
    resposta = client.get(caminho, dados)
    previa = resposta.content.decode()

    assert resposta.status_code == 200
    assert "não está no formulário desta tela" not in previa
    assert 'name="semente"' in previa, "a prévia do sorteio, com a semente fictícia"


# ------------------------------------------------------------------ US3: a ajuda dos documentos


def _so_texto(html):
    return " ".join(re.sub(r"<[^>]+>", " ", html).split())


@pytest.mark.django_db
@pytest.mark.integration
def test_a_ajuda_dos_documentos_explica_momento_aproveitamento_e_obrigatoriedade(
    client, seletor_ligado, edital
):
    """SC-1404, FR-4510, FR-4511: os quatro itens, cada um com a frase do campo."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = _etapa(client, edital, "inscricao")
    ajuda = _so_texto(re.search(r'<details class="como-preencher">(.*?)</details>', corpo, re.S)[1])
    cartao = client.get(
        reverse("interface:fragmento-documento", args=[edital.id]), {"indice": "0"}
    ).content.decode()
    descricoes = {
        alvo: _so_texto(texto)
        for alvo, texto in re.findall(
            r'<span class="oculto" id="([^"]+)">(.*?)</span>', cartao, re.S
        )
    }
    obrigatorio = _so_texto(re.search(r'<span class="perms">(.*?)</span>', cartao, re.S)[1])

    for termo in (
        "Quando é pedido",
        "Atendido pelo documento da inscrição",
        "Obrigatório",
        "Exigido somente quando",
    ):
        assert termo in ajuda, termo
    for alvo in ("ajuda-momento-0", "ajuda-aproveita-0", "ajuda-condicao-0"):
        assert descricoes[alvo] in ajuda, alvo
    assert obrigatorio in ajuda


@pytest.mark.django_db
@pytest.mark.integration
def test_o_cartao_do_documento_nao_ganha_ajuda(client, seletor_ligado, edital):
    """FR-4512: a ajuda nova mora na etapa; o cartão guarda as mesmas descrições escondidas."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    cartao = client.get(
        reverse("interface:fragmento-documento", args=[edital.id]), {"indice": "0"}
    ).content.decode()

    assert "como-preencher" not in cartao
    assert sorted(re.findall(r'<span class="oculto" id="([^"]+)"', cartao)) == sorted(
        f"ajuda-{nome}-0"
        for nome in ("chave", "instrucao", "alcance", "momento", "aproveita", "condicao", "modelo")
    )
