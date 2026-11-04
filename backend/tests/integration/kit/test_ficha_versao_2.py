"""A ficha versão 2: carga horária, contato e a desatualização por versão (119, FR-3809–FR-3812).

**A exportação versão 1 é a que a `111` grava hoje**: os `campos` sem carga horária nem contato, e a
impressão desses campos. A trilha é append-only, e por isso o registro antigo é montado em memória a
partir da ficha do instante da exportação — os `campos_v1` e a `impressao_v1` dela são exatamente o
que a `111` gravaria —, como `test_impressao_de_versao_anterior` faz com a versão 0.

Cada caso confere a faixa pela **lista exata** de mudanças (SC-1139), e não pela presença de uma.
"""

import copy
import uuid
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.portal import ficha as fichas
from processo_seletivo.unidades.models import Unidade
from tests.fixtures import kit
from tests.fixtures.publicacao import retify
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db


def _ler(edital):
    return fichas.ler(edital, agora=timezone.now(), base_url=None)


def _como_a_111(ficha):
    """O detalhe que a `111` gravaria para esta ficha: versão 1, sem carga horária nem contato."""
    return {
        "versao_da_impressao": 1,
        "impressao": ficha.impressao_v1,
        "campos": ficha.campos_v1,
        "exportado_em": "x",
    }


def _como_a_119(ficha):
    return {
        "versao_da_impressao": 2,
        "impressao": ficha.impressao,
        "campos": ficha.campos,
        "exportado_em": "y",
    }


def _mudancas(registro, ficha):
    faixas, _ = fichas.desatualizacoes([registro], ficha)
    return [(m.campo, m.de, m.para) for faixa in faixas for m in faixa.mudancas]


def _perfil(edital):
    return kit.vigente(edital).content["profiles"][0]


def _retificar(api_client, edital, mudancas, sufixo):
    retify(
        api_client,
        edital,
        [
            {"targetPath": caminho, "operation": "REPLACE", "newValue": valor}
            for caminho, valor in mudancas
        ],
        suffix=sufixo,
    )


def _carga(api_client, edital, valor, sufixo):
    perfil = _perfil(edital)
    _retificar(api_client, edital, [(f"/profiles/id={perfil['id']}/workload", valor)], sufixo)


def _atendimento(edital, valor):
    Unidade.objects.filter(codigo=edital.institution_scope).update(atendimento=valor)


# ---- FR-3809, FR-3810: o que a ficha lê ----------------------------------------------------


def _carga_no_corpus(valores):
    def mudar(conteudo):
        conteudo["profiles"] = conteudo["profiles"][: len(valores)]
        for perfil, valor in zip(conteudo["profiles"], valores, strict=True):
            perfil["workload"] = valor
        kit._podar_referencias(conteudo)

    return mudar


def test_carga_horaria_literal_aparada_e_vazia_onde_nao_declarada(api_client):
    valores = ["  360 horas, das quais 60 presenciais ", "", "180h"]
    edital = kit.publicar(api_client, chave="v2-carga", mudar=_carga_no_corpus(valores))
    ficha = _ler(edital)
    assert [o.carga_horaria for o in ficha.ofertas] == [
        "360 horas, das quais 60 presenciais",
        "",
        "180h",
    ]
    assert {o["perfil_id"]: o["carga_horaria"] for o in ficha.campos["ofertas"]} == {
        o.perfil_id: o.carga_horaria for o in ficha.ofertas
    }
    assert all("carga_horaria" not in o for o in ficha.campos_v1["ofertas"])
    # A origem pela regra da proveniência, só das declaradas (FR-3812).
    rotulos = [o.campo for o in ficha.origens if o.campo.startswith("Carga horária")]
    assert len(rotulos) == 2


def test_contato_do_cadastro_da_unidade_sem_recaida(api_client, settings):
    settings.PORTAL_ATENDIMENTO = "atendimento@instituicao.example"
    edital = kit.publicar(api_client, chave="v2-contato")
    _atendimento(edital, "")
    sem = _ler(edital)
    assert sem.contato == "" and sem.campos["contato"] == ""
    assert not [o for o in sem.origens if o.campo == "Contato"]

    _atendimento(edital, "  cefor@ifes.example — (27) 3333-0000 ")
    com = _ler(edital)
    assert com.contato == "cefor@ifes.example — (27) 3333-0000"
    (origem,) = [o for o in com.origens if o.campo == "Contato"]
    assert origem.atos == (fichas.ORIGEM_DO_CONTATO,)
    assert "contato" not in com.campos_v1
    assert com.versao_da_impressao == 2


# ---- FR-3811: a desatualização por versão (SC-1139) ----------------------------------------


def test_a_so_a_atualizacao_do_sistema_nao_acende(api_client):
    edital = kit.publicar(api_client, chave="v2-a")
    _atendimento(edital, "cefor@ifes.example")
    ficha = _ler(edital)
    assert _mudancas(_como_a_111(ficha), ficha) == []


def test_b_campos_da_versao_1_alterados_depois_de_exportacao_v1(api_client):
    edital = kit.publicar(api_client, chave="v2-b")
    antes = _ler(edital)
    evento = kit.evento_das_inscricoes(edital)
    novo_fim = kit.inicio(edital) + timedelta(days=40)
    _retificar(
        api_client,
        edital,
        [
            (f"/schedule/id={evento['id']}/endAt", novo_fim.isoformat()),
            ("/title", "Edital nº 91/2026 – Curso de Pós-graduação em Gestão Pública"),
        ],
        "v2b",
    )
    depois = _ler(edital)
    mudancas = _mudancas(_como_a_111(antes), depois)
    assert [campo for campo, _, _ in mudancas] == ["título do Edital", "término das inscrições"]
    (titulo,) = [m for m in mudancas if m[0] == "título do Edital"]
    assert titulo[1] == antes.titulo and titulo[2] == depois.titulo


def test_c_so_carga_ou_contato_depois_de_exportacao_v1_nao_acende(api_client):
    edital = kit.publicar(api_client, chave="v2-c")
    antes = _ler(edital)
    _carga(api_client, edital, "420 horas", "v2c")
    _atendimento(edital, "novo@ifes.example")
    assert _mudancas(_como_a_111(antes), _ler(edital)) == []


def test_d_misto_traz_o_titulo_e_nao_o_contato(api_client):
    edital = kit.publicar(api_client, chave="v2-d")
    antes = _ler(edital)
    _retificar(api_client, edital, [("/title", "Edital nº 91/2026 – Outro curso")], "v2d")
    _atendimento(edital, "novo@ifes.example")
    mudancas = _mudancas(_como_a_111(antes), _ler(edital))
    assert [campo for campo, _, _ in mudancas] == ["título do Edital"]


def test_e_contato_alterado_depois_de_exportacao_v2(api_client):
    edital = kit.publicar(api_client, chave="v2-e")
    _atendimento(edital, "antigo@ifes.example")
    antes = _ler(edital)
    _atendimento(edital, "novo@ifes.example")
    assert _mudancas(_como_a_119(antes), _ler(edital)) == [
        ("contato", "antigo@ifes.example", "novo@ifes.example")
    ]


def test_f_carga_horaria_alterada_depois_de_exportacao_v2(api_client):
    edital = kit.publicar(api_client, chave="v2-f")
    antes = _ler(edital)
    anterior = next(o for o in antes.ofertas if o.perfil_id == str(_perfil(edital)["id"]))
    _carga(api_client, edital, "999 horas", "v2f")
    mudancas = _mudancas(_como_a_119(antes), _ler(edital))
    assert len(mudancas) == 1
    campo, de, para = mudancas[0]
    assert campo.startswith("carga horária — ")
    assert (de, para) == (anterior.carga_horaria or "—", "999 horas")


def test_g_exportacao_com_a_impressao_v1_e_recusada(api_client, client, seletor_ligado):
    identificar(client, "cora.comunicacao", ["comunicacao"])
    edital = kit.publicar(api_client, chave="v2-g")
    ficha = _ler(edital)
    resposta = client.post(
        reverse("interface:kit-de-divulgacao-exportar", args=[edital.id, "md"]),
        {"impressao": ficha.impressao_v1},
    )
    assert resposta.status_code == 409
    assert "mudou" in resposta.content.decode()


# ---- FR-3812: a origem da carga horária, ato a ato ------------------------------------------


def _acrescentar_perfil(api_client, edital, carga, sufixo):
    """Um Perfil novo por `ADD /profiles/-`, cópia do primeiro com outro id, nome e carga."""
    novo = copy.deepcopy(_perfil(edital))
    novo["id"] = str(uuid.uuid4())
    novo["name"] = f"{novo['name']} acrescido"
    novo["workload"] = carga
    retify(
        api_client,
        edital,
        [{"targetPath": "/profiles/-", "operation": "ADD", "newValue": novo}],
        suffix=sufixo,
    )
    return novo


def _atos(ficha, campo, perfil):
    rotulo = " — ".join(filter(None, (perfil["name"], perfil.get("locality"))))
    return next(o for o in ficha.origens if o.campo == f"{campo} — {rotulo}")


def test_carga_horaria_cita_o_ato_que_a_introduziu(api_client):
    """Original, Perfil acrescentado e carga retificada depois: cada valor com o seu ato.

    Guarda a revisão do incremento 2, que suspeitou de "Publicação original" na carga de Perfil
    acrescentado. A suspeita veio do Polo Bom Jesus do corpus 91, cujas **vagas** a Retificação
    nº 1 acresceu: o Perfil e a carga dele são da original, e a origem estava certa. O acréscimo
    de Perfil passa por `origem.acrescimos`, da `070`, e este caso o prende.
    """
    edital = kit.publicar(api_client, ate=1, chave="v2-acrescido")
    original = _perfil(edital)
    novo = _acrescentar_perfil(api_client, edital, "420h", "acr")

    ficha = _ler(edital)
    assert _atos(ficha, "Carga horária", original).atos == ("Publicação original",)
    carga = _atos(ficha, "Carga horária", novo)
    assert (carga.valor, carga.atos) == ("420h", ("Retificação nº 1",))
    assert _atos(ficha, "Vagas", novo).atos == ("Retificação nº 1",)

    _retificar(api_client, edital, [(f"/profiles/id={novo['id']}/workload", "400h")], "car")
    ficha = _ler(edital)
    carga = _atos(ficha, "Carga horária", novo)
    assert (carga.valor, carga.atos) == ("400h", ("Retificação nº 2",))
    assert _atos(ficha, "Vagas", novo).atos == ("Retificação nº 1",)
    assert _atos(ficha, "Carga horária", original).atos == ("Publicação original",)
