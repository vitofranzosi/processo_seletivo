"""Duplicar Perfil na etapa Perfis do assistente (043).

Três famílias, na ordem em que o risco aparece:

- **o transporte dos marcos** — eles não são desenhados nesta etapa (R-003), e a cópia os leva num
  campo oculto que a gravação aceita para Perfil novo. É aqui que a cópia perderia dado **sem que
  nada acusasse**: na recusa da gravação;
- **o fragmento** — o cartão devolvido, a recusa no diálogo, os avisos;
- **o que não pode mudar** — a origem, os Documentos Exigidos, a revisão do Edital.
"""

import html
import json
import re
from html.parser import HTMLParser

import pytest
from django.urls import reverse

from processo_seletivo.editais.domain.duplicacao import duplicar_perfil
from processo_seletivo.editais.domain.reaproveitamento import CAMPOS_SEM_TELA
from processo_seletivo.interface import forms
from tests.interface.conftest import (
    FATO_DO_DESEMPATE,
    compor_rascunho,
    marco_de_sorteio_no_formulario,
)
from tests.interface.test_compor import PERFIL, perfis

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

COPIA = "aaaaaaaa-0000-4000-8000-000000043c01"
AC = "aaaaaaaa-0000-4000-8000-00000000e031"
PCD = "aaaaaaaa-0000-4000-8000-00000000e032"


def perfis_completos(**alteracoes):
    """O Perfil de `test_compor` com **tudo** o que se copia: fato, ampla declarada e quadro.

    O fato precisa viajar em todo reenvio da etapa — ela o desenha, e o que não for reenviado é
    apagado. Sem ele, o critério de desempate do marco apontaria fato que não existe.
    """
    return perfis(
        **{
            "fato-0-0-id": FATO_DO_DESEMPATE,
            "fato-0-0-code": "EXPERIENCIA",
            "fato-0-0-label": "Meses de experiência em EaD",
            "fato-0-0-type": "INTEIRO",
            "perfil-0-generalCompetitionModalityId": AC,
            "linha-0-0-id": "aaaaaaaa-0000-4000-8000-000000043c31",
            "linha-0-0-modalityId": "",
            "linha-0-0-immediateVacancies": "1",
            "linha-0-1-id": "aaaaaaaa-0000-4000-8000-000000043c32",
            "linha-0-1-modalityId": PCD,
            "linha-0-1-immediateVacancies": "1",
            **alteracoes,
        }
    )


def _etapa(edital, nome="perfis"):
    return reverse("interface:compor-etapa", args=[edital.id, nome])


@pytest.fixture
def com_marco(client, com_etapas):
    """O rascunho de `com_etapas`, com um marco gravado pela etapa Classificação.

    O critério de desempate cita o fato declarado do Perfil — é a referência interna do marco, e a
    única que prova o remapeamento dele.
    """
    marco = {
        **marco_de_sorteio_no_formulario(PERFIL),
        f"criterio-{PERFIL}-0-0-id": "aaaaaaaa-0000-4000-8000-000000043c21",
        f"criterio-{PERFIL}-0-0-order": "1",
        f"criterio-{PERFIL}-0-0-type": "MAIOR_VALOR_DE_FATO",
        f"criterio-{PERFIL}-0-0-target": FATO_DO_DESEMPATE,
        f"criterio-{PERFIL}-0-0-whenMissing": "ULTIMO_NO_CRITERIO",
    }
    compor_rascunho(client, com_etapas, perfis=perfis_completos(), marcos=marco)
    com_etapas.refresh_from_db()
    return com_etapas


def _marcos_gravados(edital, perfil_id=PERFIL):
    perfil = edital.perfis.get(pk=perfil_id)
    return [forms._marco_persistido(marco) for marco in perfil.marcos.order_by("code")]


def _em_transito(edital):
    """Os marcos do Perfil gravado, como uma cópia os levaria: mesma forma, identidade nova."""
    marcos = _marcos_gravados(edital)
    # Sem critério: ele cita o fato da **origem**, e remapeá-lo é da duplicação, não do transporte.
    return [
        {**marco, "id": "aaaaaaaa-0000-4000-8000-000000043c11", "tiebreakers": []}
        for marco in marcos
    ]


def _copia_no_formulario(marcos, **alteracoes):
    """Um Perfil **novo** no formulário da etapa, levando marcos em trânsito."""
    base = {
        "perfil-1-id": COPIA,
        "perfil-1-code": "TEC-ADM-2",
        "perfil-1-name": "Técnico-Administrativo",
        "perfil-1-locality": "Campus Serra",
        "perfil-1-immediateVacancies": "1",
        "perfil-1-reserveType": "NONE",
        "perfil-1-marcosEmTransito": _transito(marcos),
    }
    return {**base, **alteracoes}


def _transito(marcos, derivados=None):
    """O campo oculto como a tela o emite: os marcos e se código e nome de cada um são derivados."""
    return json.dumps(
        {"marcos": marcos, "derivados": derivados or [[False, False] for _ in marcos]}
    )


def _campo_em_transito(corpo, indice):
    achado = re.search(rf'name="perfil-{indice}-marcosEmTransito"\s+value="([^"]*)"', corpo)
    return json.loads(html.unescape(achado.group(1)))["marcos"] if achado else None


# --- T015: a travessia pela gravação -------------------------------------------------------------


def test_perfil_novo_com_marcos_em_transito_grava_com_eles(client, com_marco):
    marcos = _em_transito(com_marco)

    digitado = {**perfis_completos(), **_copia_no_formulario(marcos)}

    resposta = client.post(_etapa(com_marco), digitado)

    assert resposta.status_code == 302, resposta.content
    gravados = _marcos_gravados(com_marco, COPIA)
    assert [marco["id"] for marco in gravados] == [marcos[0]["id"]]
    assert gravados[0]["drawMethod"] == marcos[0]["drawMethod"]
    assert gravados[0]["cutRule"] == marcos[0]["cutRule"]


def test_perfil_ja_gravado_que_carregue_o_campo_continua_com_os_marcos_gravados(client, com_marco):
    """A preservação vence: o campo só vale para quem ainda não tem par gravado (R-003)."""
    antes = _marcos_gravados(com_marco)
    forjado = [{**antes[0], "id": "aaaaaaaa-0000-4000-8000-000000043c12", "code": "FORJADO"}]

    resposta = client.post(
        _etapa(com_marco),
        {**perfis_completos(), "perfil-0-marcosEmTransito": _transito(forjado)},
    )

    assert resposta.status_code == 302, resposta.content
    assert _marcos_gravados(com_marco) == antes


# --- T016: a travessia pela recusa ---------------------------------------------------------------


def test_a_recusa_devolve_a_copia_com_os_mesmos_marcos_em_transito(client, com_marco):
    """É aqui que os marcos sumiriam sem aviso: a tela que devolve o digitado precisa devolvê-los,
    ou a gravação seguinte grava a cópia sem marco nenhum (FR-650)."""
    marcos = _em_transito(com_marco)
    # O erro está no **outro** Perfil: limitado sem limite.
    digitado = {
        **perfis_completos(**{"perfil-0-reserveLimit": ""}),
        **_copia_no_formulario(marcos),
    }

    resposta = client.post(_etapa(com_marco), digitado)

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "limite" in corpo.lower()
    assert _campo_em_transito(corpo, 1) == marcos


def test_perfil_gravado_nao_emite_o_campo_em_transito(client, com_marco):
    resposta = client.get(_etapa(com_marco))

    assert "marcosEmTransito" not in resposta.content.decode()


# --- T017: JSON malformado -----------------------------------------------------------------------


def test_campo_em_transito_malformado_e_recusa_com_mensagem_e_nao_erro(client, com_marco):
    digitado = {
        **perfis_completos(),
        **_copia_no_formulario([], **{"perfil-1-marcosEmTransito": "{não é json"}),
    }

    resposta = client.post(_etapa(com_marco), digitado)

    assert resposta.status_code == 200
    assert "não puderam ser lidos" in resposta.content.decode()
    assert not com_marco.perfis.filter(pk=COPIA).exists()


# --- T008: completude contra o contrato ----------------------------------------------------------

# Cada caminho do contrato do Perfil, e o que a cópia faz com ele (data-model). `[]` é "cada item
# da lista". Os dicionários opacos — normas publicadas inteiras — são folhas: comparados inteiros.
NOVA, INFORMADA, IGUAL, REMAPEADA, AUSENTE, DERIVADA = (
    "nova",
    "informada",
    "igual",
    "remapeada",
    "ausente",
    "derivada",
)
OPACOS = {
    "vacancyReversion",
    "competitionModalities[].normativeRule.distribution",
    "competitionModalities[].normativeRule.callRules",
    "classificationMilestones[].rounding",
    "classificationMilestones[].appealWindow",
    "classificationMilestones[].drawMethod",
    "classificationMilestones[].cutRule",
    "classificationMilestones[].tiebreakers[].parameters",
    "classificationInformation",
    "callInformation",
}
CATEGORIAS = {
    "id": NOVA,
    "code": INFORMADA,
    "locality": INFORMADA,
    **{
        campo: IGUAL
        for campo in (
            "name",
            "description",
            "requirements",
            "immediateVacancies",
            "reserveType",
            "reserveLimit",
            "vacancyReversion",
            "callForm",
            "duties",
            "workload",
            "compensation",
        )
    },
    "generalCompetitionModalityId": REMAPEADA,
    "competitionModalities[].id": NOVA,
    **{f"competitionModalities[].{campo}": IGUAL for campo in ("code", "name", "description")},
    "competitionModalities[].normativeRule.id": NOVA,
    **{
        f"competitionModalities[].normativeRule.{campo}": IGUAL
        for campo in (
            "foundation",
            "version",
            "percentage",
            "calculation",
            "rounding",
            "distribution",
            "callRules",
            "effectiveFrom",
        )
    },
    "declaredFacts[].id": NOVA,
    **{f"declaredFacts[].{campo}": IGUAL for campo in ("code", "label", "type")},
    "vacancyTable[].id": NOVA,
    "vacancyTable[].modalityId": REMAPEADA,
    "vacancyTable[].immediateVacancies": IGUAL,
    "classificationMilestones[].id": NOVA,
    "classificationMilestones[].code": DERIVADA,
    "classificationMilestones[].name": DERIVADA,
    **{
        f"classificationMilestones[].{campo}": IGUAL
        for campo in (
            "orderProduction",
            "stages",
            "operation",
            "normalization",
            "rounding",
            "appealWindow",
            "drawMethod",
            "cutRule",
        )
    },
    "classificationMilestones[].tiebreakers[].id": NOVA,
    **{
        f"classificationMilestones[].tiebreakers[].{campo}": IGUAL
        for campo in ("order", "type", "whenMissing")
    },
    # `factId` é remapeado e `stageId` preservado: o teste de conteúdo abaixo distingue os dois.
    "classificationMilestones[].tiebreakers[].parameters": REMAPEADA,
    **{campo: AUSENTE for campo in CAMPOS_SEM_TELA},
}


def _caminhos(valor, prefixo=""):
    if prefixo in OPACOS or not isinstance(valor, dict | list):
        yield prefixo
        return
    if isinstance(valor, list):
        if valor and all(isinstance(item, dict) for item in valor):
            for item in valor:
                yield from _caminhos(item, f"{prefixo}[]")
        else:
            yield prefixo
        return
    for chave, item in valor.items():
        yield from _caminhos(item, f"{prefixo}.{chave}" if prefixo else chave)


def test_todo_campo_do_contrato_do_perfil_tem_categoria(com_marco):
    """`FR-639`: a lista vem do **contrato** — o que a gravação reenvia —, e não de uma lista
    escrita aqui nem do leitor da tela, que não conhece os campos sem tela. Campo novo no contrato
    sem categoria reprova, e é esse o ponto."""
    (perfil,) = forms.perfis_persistidos(com_marco)

    caminhos = set(_caminhos(perfil))

    assert caminhos - set(CATEGORIAS) == set(), "campo do contrato sem categoria na duplicação"
    # E a fixture exercita as coleções que importam: sem elas o teste passaria vazio.
    assert {
        "competitionModalities[].normativeRule.id",
        "declaredFacts[].id",
        "vacancyTable[].id",
        "classificationMilestones[].tiebreakers[].id",
    } <= caminhos


def test_cada_categoria_faz_o_que_diz(com_marco):
    (origem,) = forms.perfis_persistidos(com_marco)
    etapas = [str(etapa) for etapa in com_marco.etapas.values_list("id", flat=True)]

    copia = duplicar_perfil(origem, codigo="TEC-ADM-2", localidade="Serra", etapas_do_edital=etapas)

    def valores(conteudo, caminho):
        partes = caminho.split(".")
        atuais = [conteudo]
        for parte in partes:
            lista = parte.endswith("[]")
            chave = parte.removesuffix("[]")
            atuais = [item.get(chave) for item in atuais if isinstance(item, dict)]
            if lista:
                atuais = [elemento for item in atuais for elemento in (item or [])]
        return atuais

    for caminho in set(_caminhos(origem)):
        categoria = CATEGORIAS[caminho]
        antes, depois = valores(origem, caminho), valores(copia, caminho)
        if categoria == IGUAL:
            assert depois == antes, caminho
        elif categoria == NOVA:
            assert set(depois).isdisjoint(antes), caminho
        elif categoria == AUSENTE:
            assert caminho not in copia, caminho
    assert (copia["code"], copia["locality"]) == ("TEC-ADM-2", "Serra")
    (criterio,) = copia["classificationMilestones"][0]["tiebreakers"]
    assert criterio["parameters"]["factId"] == copia["declaredFacts"][0]["id"]
    assert criterio["parameters"]["factId"] != FATO_DO_DESEMPATE


# --- O fragmento (US1) ---------------------------------------------------------------------------


def _duplicar(client, edital, formulario, *, indice="0", codigo="TEC-ADM-2", localidade="Serra"):
    parametros = {
        **formulario,
        "edital": str(edital.id),
        "duplicar-codigo": codigo,
        "duplicar-localidade": localidade,
    }
    return client.get(reverse("interface:fragmento-perfil-duplicado", args=[indice]), parametros)


class _Campos(HTMLParser):
    """Os pares nome → valor que o navegador enviaria a partir de um pedaço de formulário.

    Existe para gravar **a cópia como a tela a devolveu**, e não como o teste a imaginaria: o que
    prova a travessia é o cartão real voltar ao servidor.
    """

    def __init__(self):
        super().__init__()
        self.campos = {}
        self._textarea = None
        self._select = None

    def handle_starttag(self, tag, atributos):
        atributos = dict(atributos)
        nome = atributos.get("name")
        if tag == "input" and nome and "form" not in atributos:
            if atributos.get("type") in ("radio", "checkbox") and "checked" not in atributos:
                return
            self.campos[nome] = atributos.get("value") or ""
        elif tag == "textarea" and nome:
            self._textarea = nome
            self.campos[nome] = ""
        elif tag == "select" and nome:
            self._select = nome
            self.campos.setdefault(nome, "")
        elif tag == "option" and self._select and "selected" in atributos:
            self.campos[self._select] = atributos.get("value") or ""

    def handle_endtag(self, tag):
        if tag == "textarea":
            self._textarea = None
        elif tag == "select":
            self._select = None

    def handle_data(self, dados):
        if self._textarea:
            self.campos[self._textarea] += dados


def _campos_do_cartao(corpo):
    leitor = _Campos()
    leitor.feed(corpo)
    return leitor.campos


def _indice_do_cartao(corpo):
    return re.search(r'name="perfil-([^-"]+)-id"', corpo).group(1)


def test_sucesso_devolve_o_cartao_da_copia_com_indice_novo_foco_e_anuncio(client, com_marco):
    resposta = _duplicar(client, com_marco, perfis_completos())

    assert resposta.status_code == 200
    assert "HX-Retarget" not in resposta
    corpo = resposta.content.decode()
    campos = _campos_do_cartao(corpo)
    indice = _indice_do_cartao(corpo)
    assert indice != "0"
    assert campos[f"perfil-{indice}-code"] == "TEC-ADM-2"
    assert campos[f"perfil-{indice}-locality"] == "Serra"
    assert campos[f"perfil-{indice}-name"] == "Técnico-Administrativo"
    assert campos[f"perfil-{indice}-id"] != PERFIL
    assert re.search(rf'id="perfil-{indice}-code"[^>]*autofocus', corpo)
    assert 'role="status"' in corpo
    assert "Perfil TEC-ADM-2 criado a partir de TEC-ADM." in corpo


@pytest.mark.parametrize(
    ("codigo", "mensagem"),
    [
        ("", "Informe o Código do novo Perfil."),
        ("TEC-ADM", "Já existe um Perfil com o Código TEC-ADM"),
        ("NOVO-NA-TELA", "Já existe um Perfil com o Código NOVO-NA-TELA"),
    ],
)
def test_codigo_vazio_ou_ja_na_tela_e_recusado_no_dialogo(client, com_marco, codigo, mensagem):
    """Inclusive o Código de um Perfil **ainda não gravado**: a colisão é com a tela (FR-635)."""
    formulario = {**perfis_completos(), "perfil-7-id": COPIA, "perfil-7-code": "NOVO-NA-TELA"}

    resposta = _duplicar(client, com_marco, formulario, codigo=codigo)

    assert resposta.status_code == 200
    assert resposta["HX-Retarget"] == "#duplicar-0"
    assert resposta["HX-Reswap"] == "outerHTML"
    corpo = resposta.content.decode()
    assert mensagem in corpo
    assert 'aria-invalid="true"' in corpo
    assert 'name="perfil-' not in corpo


def test_localidade_vazia_nao_e_recusa_e_nao_herda_a_da_origem(client, com_marco):
    resposta = _duplicar(client, com_marco, perfis_completos(), localidade="")

    corpo = resposta.content.decode()
    assert "HX-Retarget" not in resposta
    assert _campos_do_cartao(corpo)[f"perfil-{_indice_do_cartao(corpo)}-locality"] == ""


def test_origem_com_valor_ilegivel_e_recusada_no_dialogo(client, com_marco):
    formulario = perfis_completos(**{"perfil-0-immediateVacancies": "dez"})

    resposta = _duplicar(client, com_marco, formulario)

    assert resposta["HX-Retarget"] == "#duplicar-0"
    assert "precisa ser corrigido" in resposta.content.decode()


def test_origem_com_erro_de_regra_e_copiada_com_o_erro_e_a_gravacao_o_recusa(client, com_marco):
    formulario = perfis_completos(**{"perfil-0-reserveLimit": ""})

    resposta = _duplicar(client, com_marco, formulario)

    assert "HX-Retarget" not in resposta
    copia = _campos_do_cartao(resposta.content.decode())
    gravacao = client.post(_etapa(com_marco), {**formulario, **copia})
    assert gravacao.status_code == 200
    assert "limite" in gravacao.content.decode().lower()


def test_a_copia_parte_do_digitado_e_os_marcos_do_gravado(client, com_marco):
    formulario = perfis_completos(**{"perfil-0-name": "Denominação digitada agora"})

    corpo = _duplicar(client, com_marco, formulario).content.decode()

    indice = _indice_do_cartao(corpo)
    campos = _campos_do_cartao(corpo)
    assert campos[f"perfil-{indice}-name"] == "Denominação digitada agora"
    (marco,) = _campo_em_transito(corpo, indice)
    assert marco["drawMethod"] == _marcos_gravados(com_marco)[0]["drawMethod"]
    (criterio,) = marco["tiebreakers"]
    fato_da_copia = campos[f"fato-{indice}-0-id"]
    assert criterio["parameters"]["factId"] == fato_da_copia != FATO_DO_DESEMPATE


def test_duplicar_uma_copia_nao_gravada_leva_os_marcos_dela_remapeados_de_novo(client, com_marco):
    primeira = _duplicar(client, com_marco, perfis_completos()).content.decode()
    indice_1 = _indice_do_cartao(primeira)
    formulario = {**perfis_completos(), **_campos_do_cartao(primeira)}

    segunda = _duplicar(client, com_marco, formulario, indice=indice_1, codigo="TEC-ADM-3")

    corpo = segunda.content.decode()
    indice_2 = _indice_do_cartao(corpo)
    campos = _campos_do_cartao(corpo)
    assert campos[f"perfil-{indice_2}-code"] == "TEC-ADM-3"
    (marco,) = _campo_em_transito(corpo, indice_2)
    (anterior,) = _campo_em_transito(primeira, indice_1)
    assert marco["id"] != anterior["id"]
    fato = campos[f"fato-{indice_2}-0-id"]
    assert marco["tiebreakers"][0]["parameters"]["factId"] == fato
    assert fato != _campos_do_cartao(primeira)[f"fato-{indice_1}-0-id"]


def _documento(edital, chave, **recorte):
    from processo_seletivo.editais.models.documentos import DocumentoExigido

    return DocumentoExigido.objects.create(edital=edital, key=chave, name=chave, **recorte)


def test_os_avisos_dizem_quantos_marcos_e_quantos_documentos_nao_replicados(client, com_marco):
    _documento(com_marco, "laudo", order=1, perfil_id=PERFIL)
    _documento(com_marco, "laudo-pcd", order=2, modalidade_id=PCD)
    _documento(com_marco, "identidade", order=3)  # Todos os Perfis: vale para a cópia, não conta.

    corpo = _duplicar(client, com_marco, perfis_completos()).content.decode()

    assert "Leva 1 marco de classificação" in corpo
    assert "2 documentos exigidos restritos a TEC-ADM não foram replicados" in corpo


def test_origem_nao_gravada_nao_anuncia_documento_nenhum(client, com_marco):
    _documento(com_marco, "laudo", perfil_id=PERFIL)
    primeira = _duplicar(client, com_marco, perfis_completos()).content.decode()
    formulario = {**perfis_completos(), **_campos_do_cartao(primeira)}

    corpo = _duplicar(
        client, com_marco, formulario, indice=_indice_do_cartao(primeira), codigo="TEC-ADM-3"
    ).content.decode()

    assert "não foram replicados" not in corpo
    assert "não foi replicado" not in corpo


def test_duplicar_nao_grava_nada(client, com_marco):
    from processo_seletivo.auditoria.models import RegistroAuditoria

    _documento(com_marco, "laudo", perfil_id=PERFIL)
    antes = (
        com_marco.revision,
        com_marco.perfis.count(),
        com_marco.documentos_exigidos.count(),
        RegistroAuditoria.objects.count(),
    )

    _duplicar(client, com_marco, perfis_completos())

    com_marco.refresh_from_db()
    assert antes == (
        com_marco.revision,
        com_marco.perfis.count(),
        com_marco.documentos_exigidos.count(),
        RegistroAuditoria.objects.count(),
    )


def _origem_gravada(edital):
    (origem,) = (item for item in forms.perfis_persistidos(edital) if item["id"] == PERFIL)
    return origem


@pytest.mark.parametrize("desfecho", ["grava com a copia", "grava sem a copia", "nao grava"])
def test_a_origem_fica_identica_nos_tres_desfechos(client, com_marco, desfecho):
    """`SC-234`: gravar sem a cópia é o "removeu o cartão antes de gravar"."""
    client.post(_etapa(com_marco), perfis_completos())
    antes = _origem_gravada(com_marco)
    copia = _campos_do_cartao(_duplicar(client, com_marco, perfis_completos()).content.decode())

    if desfecho == "grava com a copia":
        resposta = client.post(_etapa(com_marco), {**perfis_completos(), **copia})
        assert resposta.status_code == 302, resposta.content
        assert com_marco.perfis.count() == 2
    elif desfecho == "grava sem a copia":
        assert client.post(_etapa(com_marco), perfis_completos()).status_code == 302

    assert _origem_gravada(com_marco) == antes


def _identidades_do_perfil(perfil):
    marcos = perfil.get("classificationMilestones") or []
    return {
        perfil["id"],
        *(item["id"] for item in perfil.get("competitionModalities") or []),
        *(
            item["normativeRule"]["id"]
            for item in perfil.get("competitionModalities") or []
            if item.get("normativeRule")
        ),
        *(item["id"] for item in perfil.get("declaredFacts") or []),
        *(item["id"] for item in perfil.get("vacancyTable") or []),
        *(item["id"] for item in marcos),
        *(criterio["id"] for marco in marcos for criterio in marco.get("tiebreakers") or []),
    }


def test_tres_copias_gravadas_nao_partilham_identidade_nem_referencia(client, com_marco):
    """`SC-232` e `SC-233` sobre o conteúdo canônico — o mesmo de que a publicação deriva.

    A publicação em si é percorrida na demonstração (`SC-235`); aqui se prova a propriedade que ela
    herdaria, e em segundos."""
    from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot

    formulario = perfis_completos()
    for codigo in ("TEC-ADM-2", "TEC-ADM-3", "TEC-ADM-4"):
        corpo = _duplicar(client, com_marco, formulario, codigo=codigo).content.decode()
        formulario = {**formulario, **_campos_do_cartao(corpo)}
    resposta = client.post(_etapa(com_marco), formulario)
    assert resposta.status_code == 302, resposta.content

    com_marco.refresh_from_db()
    perfis_gravados = edital_snapshot(com_marco)["profiles"]
    assert len(perfis_gravados) == 4
    identidades = [_identidades_do_perfil(perfil) for perfil in perfis_gravados]
    for posicao, conjunto in enumerate(identidades):
        for outro in identidades[posicao + 1 :]:
            assert conjunto.isdisjoint(outro)
    for perfil, proprias in zip(perfis_gravados, identidades, strict=True):
        alheias = set().union(*(outro for outro in identidades if outro is not proprias))
        assert not alheias & set(re.findall(r"[0-9a-f-]{36}", json.dumps(perfil, default=str)))
    origem = next(perfil for perfil in perfis_gravados if perfil["code"] == "TEC-ADM")
    for perfil in perfis_gravados:
        if perfil is origem:
            continue
        assert perfil["locality"] == "Serra"
        assert _sem_identidades(perfil) == _sem_identidades(
            {**origem, "code": perfil["code"], "locality": "Serra"}
        )


def _sem_identidades(perfil):
    texto = json.dumps(perfil, sort_keys=True, default=str)
    texto = re.sub(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", "<id>", texto)
    return json.loads(texto)


def test_duas_copias_forjadas_com_o_mesmo_codigo_sao_recusadas_pela_gravacao(client, com_marco):
    """A conferência do diálogo é conveniência; a autoridade continua em `validate_profiles`."""
    copia = _campos_do_cartao(_duplicar(client, com_marco, perfis_completos()).content.decode())
    indice = next(chave.split("-")[1] for chave in copia if chave.endswith("-code"))
    forjada = {
        chave.replace(f"-{indice}-", "-99-", 1): valor
        for chave, valor in copia.items()
        if f"-{indice}-" in chave
    }
    forjada["perfil-99-id"] = "aaaaaaaa-0000-4000-8000-000000043c99"

    resposta = client.post(_etapa(com_marco), {**perfis_completos(), **copia, **forjada})

    assert resposta.status_code == 200
    assert "não podem se repetir" in resposta.content.decode()


def test_o_orcamento_de_consultas_nao_cresce_com_o_numero_de_perfis(client, com_marco):
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    def contar():
        with CaptureQueriesContext(connection) as consultas:
            assert _duplicar(client, com_marco, perfis_completos()).status_code == 200
        return len(consultas)

    com_dois = perfis_completos(
        **{"perfil-1-id": COPIA, "perfil-1-code": "OUTRO", "perfil-1-name": "Outro"}
    )
    assert client.post(_etapa(com_marco), com_dois).status_code == 302
    pequeno = contar()

    muitos = dict(perfis_completos())
    for posicao in range(1, 16):
        muitos |= {
            f"perfil-{posicao}-id": f"aaaaaaaa-0000-4000-8000-0000000431{posicao:02d}",
            f"perfil-{posicao}-code": f"P{posicao:02d}",
            f"perfil-{posicao}-name": "Perfil",
        }
    assert client.post(_etapa(com_marco), muitos).status_code == 302
    assert com_marco.perfis.count() == 16

    assert contar() == pequeno


def test_o_cartao_acrescentado_tambem_oferece_duplicar(client, com_marco):
    corpo = client.get(
        reverse("interface:fragmento-perfil"), {"edital": str(com_marco.id)}
    ).content.decode()

    assert "Duplicar este Perfil" in corpo


def test_sem_o_edital_o_cartao_acrescentado_nasce_sem_o_dialogo(client, com_marco):
    corpo = client.get(reverse("interface:fragmento-perfil")).content.decode()

    assert "Duplicar este Perfil" not in corpo


def test_a_etapa_em_leitura_nao_oferece_duplicar(client, com_marco):
    from tests.interface.conftest import identificar

    identificar(client, "hugo.homologador", ["homologador"])

    corpo = client.get(_etapa(com_marco)).content.decode()

    # O diálogo, e não a explicação do `como-preencher`, que a etapa mostra a quem lê também.
    assert "<summary>Duplicar este Perfil</summary>" not in corpo


def test_a_etapa_em_composicao_oferece_duplicar_em_cada_cartao(client, com_marco):
    corpo = client.get(_etapa(com_marco)).content.decode()

    assert corpo.count("<summary>Duplicar este Perfil</summary>") == com_marco.perfis.count()


# --- R-012: a reexibição após recusa perdia fatos e reversão -------------------------------------


def test_a_recusa_devolve_os_fatos_e_a_reversao_digitados(client, com_marco):
    """Achado da `043`, anterior a ela: a tela que devolve o digitado desenhava o cartão sem os
    fatos e com a reversão desmarcada, e a gravação seguinte apagava os dois (R-012)."""
    digitado = perfis_completos(
        **{"perfil-0-reserveLimit": "", "perfil-0-vacancyReversion": "ON_EXHAUSTION"}
    )

    corpo = client.post(_etapa(com_marco), digitado).content.decode()

    campos = _campos_do_cartao(corpo)
    assert campos["fato-0-0-id"] == FATO_DO_DESEMPATE
    assert campos["fato-0-0-code"] == "EXPERIENCIA"
    assert campos["perfil-0-vacancyReversion"] == "ON_EXHAUSTION"


# --- Acessibilidade e o diálogo fora do formulário (T042, T044) ---------------------------------


def test_o_dialogo_tem_rotulos_botao_que_nao_submete_e_campos_fora_do_formulario(client, com_marco):
    """`FR-637` e `R-007`. Que o navegador de fato exclua os campos de `form.elements` é
    comportamento do HTML — o dono do campo é o `form` que o atributo nomeia, e nenhum tem aquele
    `id` —, verificado no navegador na demonstração: o shim de `tests/javascript/dom.js` não modela
    o atributo, e um teste lá provaria o shim, não a tela."""
    corpo = client.get(_etapa(com_marco)).content.decode()
    padrao = r'<details class="como-preencher" id="duplicar-0".*?</details>'
    dialogo = re.search(padrao, corpo, re.S)

    assert dialogo is not None
    trecho = dialogo.group(0)
    for campo in ("codigo", "localidade"):
        assert f'<label for="duplicar-0-{campo}">' in trecho
        assert re.search(rf'id="duplicar-0-{campo}"[^>]*form="duplicar-0-fora"', trecho, re.S)
    assert 'id="duplicar-0-fora"' not in corpo
    assert re.search(r'<button type="button" class="acao"\s+hx-get="[^"]*/duplicar', trecho)


def test_a_gravacao_da_etapa_ignora_os_campos_do_dialogo(client, com_marco):
    """Mesmo que um navegador os enviasse, a leitura da etapa não os conhece: nada muda."""
    antes = _origem_gravada(com_marco)

    resposta = client.post(
        _etapa(com_marco),
        {**perfis_completos(), "duplicar-codigo": "X", "duplicar-localidade": "Y"},
    )

    assert resposta.status_code == 302
    assert com_marco.perfis.count() == 1
    assert _origem_gravada(com_marco) == antes


def test_o_sucesso_devolve_o_dialogo_da_origem_fechado_e_vazio_fora_de_banda(client, com_marco):
    """Visto no navegador: sem isto, o diálogo da origem ficava aberto com a recusa anterior e o
    Código da cópia ainda digitados."""
    corpo = _duplicar(client, com_marco, perfis_completos()).content.decode()

    dialogo = re.search(r'<details class="como-preencher" id="duplicar-0"[^>]*>', corpo)
    assert dialogo is not None
    assert 'hx-swap-oob="outerHTML"' in dialogo.group(0)
    assert " open" not in dialogo.group(0)
    assert 'id="duplicar-0-recusa"' not in corpo
    assert re.search(r'id="duplicar-0-codigo"[^>]*value=""', corpo, re.S)


# --- Correções da revisão de código --------------------------------------------------------------


def test_a_modalidade_sem_regra_da_copia_nasce_com_identidade_de_regra(client, com_marco):
    """A ampla concorrência de toda cópia não tem Regra; digitar um fundamento nela e gravar não
    pode produzir Regra de identidade vazia."""
    corpo = _duplicar(client, com_marco, perfis_completos()).content.decode()
    copia = _campos_do_cartao(corpo)
    indice = _indice_do_cartao(corpo)
    regras = {
        chave: valor
        for chave, valor in copia.items()
        if chave.startswith(f"modalidade-{indice}-") and chave.endswith("-ruleId")
    }
    assert regras and all(regras.values())

    ampla = next(
        chave.removesuffix("-code")
        for chave, valor in copia.items()
        if chave.startswith(f"modalidade-{indice}-") and chave.endswith("-code") and valor == "AC"
    )
    copia |= {
        f"{ampla}-foundation": "Resolução CS/Ifes",
        f"{ampla}-version": "2024-01-01",
    }
    resposta = client.post(_etapa(com_marco), {**perfis_completos(), **copia})

    assert resposta.status_code == 302, resposta.content
    gravada = com_marco.perfis.get(code="TEC-ADM-2").modalidades.get(code="AC")
    assert gravada.regra_normativa.foundation == "Resolução CS/Ifes"


def test_codigo_corrigido_no_cartao_antes_de_gravar_leva_o_marco_derivado_junto(client, com_marco):
    """FR-644 depois da cópia: quem corrige o Código da cópia antes de gravar não publica o marco
    com o Código de antes da correção."""
    MarcoClassificatorio = com_marco.perfis.get(pk=PERFIL).marcos.model
    MarcoClassificatorio.objects.filter(perfil_id=PERFIL).update(
        code="TEC-ADM", name="Classificação final — Técnico-Administrativo"
    )
    corpo = _duplicar(client, com_marco, perfis_completos(), codigo="TEC-ADM2").content.decode()
    indice = _indice_do_cartao(corpo)
    copia = _campos_do_cartao(corpo) | {f"perfil-{indice}-code": "TEC-ADM-2"}

    resposta = client.post(_etapa(com_marco), {**perfis_completos(), **copia})

    assert resposta.status_code == 302, resposta.content
    (marco,) = _marcos_gravados(com_marco, com_marco.perfis.get(code="TEC-ADM-2").id)
    assert marco["code"] == "TEC-ADM-2"


def test_codigo_corrigido_numa_copia_nao_gravada_vale_para_a_copia_dela(client, com_marco):
    MarcoClassificatorio = com_marco.perfis.get(pk=PERFIL).marcos.model
    MarcoClassificatorio.objects.filter(perfil_id=PERFIL).update(code="TEC-ADM")
    primeira = _duplicar(client, com_marco, perfis_completos(), codigo="X").content.decode()
    indice_1 = _indice_do_cartao(primeira)
    formulario = {
        **perfis_completos(),
        **_campos_do_cartao(primeira),
        f"perfil-{indice_1}-code": "TEC-ADM-2",
    }

    segunda = _duplicar(client, com_marco, formulario, indice=indice_1, codigo="TEC-ADM-3")

    corpo = segunda.content.decode()
    (marco,) = _campo_em_transito(corpo, _indice_do_cartao(corpo))
    assert marco["code"] == "TEC-ADM-3"


@pytest.mark.parametrize("alvo", ["etapa", "fato"])
def test_marco_em_transito_que_cita_o_que_nao_e_do_edital_nem_do_perfil_e_recusado(
    client, com_marco, alvo
):
    """Um campo oculto forjado não grava num Perfil novo marco que cite Etapa de outro Edital ou
    fato de outro Perfil — o leitor da Classificação não passa por ele."""
    (marco,) = _em_transito(com_marco)
    alheia = "aaaaaaaa-0000-4000-8000-0000000430ff"
    if alvo == "etapa":
        marco = {**marco, "stages": [alheia]}
    else:
        marco = {
            **marco,
            "tiebreakers": [
                {
                    "id": "aaaaaaaa-0000-4000-8000-000000043c41",
                    "order": 1,
                    "type": "MAIOR_VALOR_DE_FATO",
                    "parameters": {"factId": FATO_DO_DESEMPATE},
                    "whenMissing": "ULTIMO_NO_CRITERIO",
                }
            ],
        }
    digitado = {**perfis_completos(), **_copia_no_formulario([marco])}

    resposta = client.post(_etapa(com_marco), digitado)

    assert resposta.status_code == 200
    assert "não são deste Edital nem deste Perfil" in resposta.content.decode()
    assert not com_marco.perfis.filter(pk=COPIA).exists()


def test_o_cartao_da_tela_e_o_da_recusa_tem_as_mesmas_chaves(com_marco):
    """A raiz do R-012: dois conversores para o mesmo cartão, mantidos à mão. O que um desenha e o
    outro esquece some na recusa e na cópia. `marcos` é do cartão da Classificação, e não deste."""
    (da_tela,) = forms.perfis_do_edital(com_marco)
    (lido,) = forms.ler_perfis(
        {**perfis_completos(), "perfil-0-reserveType": "UNLIMITED", "perfil-0-reserveLimit": ""}
    )
    from processo_seletivo.interface.views import _reexibir_perfis

    (da_recusa,) = _reexibir_perfis([lido])

    assert set(da_tela) - {"marcos"} <= set(da_recusa)
    assert set(da_tela["modalidades"][0]) == set(da_recusa["modalidades"][0])
    assert set(da_tela["fatos"][0]) == set(da_recusa["fatos"][0])
