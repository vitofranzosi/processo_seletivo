"""O método do sorteio se corrige pela tela, campo a campo (026, US4, FR-308).

**É a contradição mais visível do produto.** A `021` determina que alterar o método é Retificação;
a própria tela do sorteio manda o operador retificá-lo; e a Retificação não oferecia **um único**
dos seus dez campos.

Quatro deles são escolha conferida, e não texto: algoritmo, fonte e as duas regras identificam o
que este sistema **executa**. Texto livre ali publicaria um nome que o motor não conhece — e quem
reimplementasse a partir do publicado chegaria a outra ordem, concluindo, corretamente, que o
sorteio não confere.
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface.retificacao import CAMPOS_DO_METODO, campos_editaveis
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.publicacao import publish_original, publish_retification
from tests.fixtures.snapshot import ETAPA, MARCO, rascunho_completo
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=1
    )


@pytest.fixture
def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def _base_do_marco(conteudo):
    perfil = next(p for p in conteudo["profiles"] if p.get("classificationMilestones"))
    return f"/profiles/id={perfil['id']}/classificationMilestones/id={MARCO}"


def campos(vigente, **alteracoes):
    grupos = campos_editaveis(vigente.content)
    do_formulario = [campo for grupo in grupos for campo in grupo["campos"]]
    enviados = {"base": str(vigente.id)}
    enviados |= {f"campo:{campo['referencia']}": campo["valor"] for campo in do_formulario}
    referencia = {campo["caminho"]: campo["referencia"] for campo in do_formulario}
    enviados.update({f"campo:{referencia[c]}": valor for c, valor in alteracoes.items()})
    return enviados


def test_sao_dez_campos_e_a_conta_fecha_com_a_spec():
    assert len(CAMPOS_DO_METODO) == 10


def test_a_tela_oferece_os_dez_campos_do_metodo(client, seletor_ligado, edital, vigente):
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()

    grupos = campos_editaveis(vigente.content)
    do_marco = next(g for g in grupos if g["tipo"] == "Marco")
    do_metodo = [c for c in do_marco["campos"] if "/drawMethod/" in c["caminho"]]
    assert len(do_metodo) == 10

    for _, rotulo, _ in CAMPOS_DO_METODO:
        assert rotulo in corpo, f"a tela não exibe o rótulo '{rotulo}'"
    assert "drawMethod" not in corpo, "o caminho normativo não chega ao HTML (FR-019)"


def test_algoritmo_fonte_e_as_duas_regras_sao_escolha_conferida(
    client, seletor_ligado, edital, vigente
):
    """Texto livre publicaria nome que o motor não conhece.

    E o manifesto publicaria uma origem que a semente não teve.
    """
    grupos = campos_editaveis(vigente.content)
    do_marco = next(g for g in grupos if g["tipo"] == "Marco")
    por_caminho = {c["caminho"].rsplit("/id=", 1)[-1]: c for c in do_marco["campos"]}

    fechados = {
        "drawMethod/algorithm": "IFES-SORTEIO-SHA256-v1",
        "drawMethod/source": "Fonte de demonstração",
        "drawMethod/normalization/rule": "DIGITOS_EM_SEQUENCIA",
        "drawMethod/substitutionRule/rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
    }
    for sufixo, esperado in fechados.items():
        campo = next(c for c in do_marco["campos"] if c["caminho"].endswith(sufixo))
        assert campo["tipo"] == "referencia", f"{sufixo} precisa ser escolha, e não texto"
        assert esperado in [identificador for identificador, _ in campo["opcoes"]]
    assert por_caminho


def test_a_etapa_de_habilitacao_oferece_so_as_etapas_do_proprio_marco(
    client, seletor_ligado, edital, vigente
):
    """Etapa de fora seria critério de entrada que a norma do marco não declara (021, R-012)."""
    grupos = campos_editaveis(vigente.content)
    do_marco = next(g for g in grupos if g["tipo"] == "Marco")
    habilitacao = next(
        c for c in do_marco["campos"] if c["caminho"].endswith("/drawMethod/qualifyingStageId")
    )

    assert habilitacao["tipo"] == "referencia"
    assert {identificador for identificador, _ in habilitacao["opcoes"]} == {ETAPA["A"], ETAPA["B"]}
    # O vazio é legítimo aqui, e só aqui no método: `null` significa "nenhuma", que é o caso dos
    # quatro Editais da amostra — a análise documental vem depois do sorteio.
    assert habilitacao["rotulo_do_vazio"].startswith("Nenhuma")


def test_corrigir_a_ocorrencia_pela_tela_vira_replace_por_identidade(
    client, seletor_ligado, edital, vigente
):
    """SC-100 — o Edital publicou a ocorrência que fixa a semente e a data estava errada."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    caminho = f"{_base_do_marco(vigente.content)}/drawMethod/occurrence"

    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{caminho: "5999"}),
            "justificativa": "A extração citada estava errada.",
            "confirmar": "1",
            "chave_idempotencia": "retificar-metodo-000001",
        },
    )
    assert resposta.status_code in (200, 302), resposta.content

    alteracao = Retificacao.objects.get().alteracoes.get(target_path=caminho)
    assert alteracao.new_value == "5999"


def test_a_conferencia_exibe_o_metodo_em_portugues(client, seletor_ligado, edital, vigente):
    identificar(client, "ana.elaboradora", ["elaborador"])
    caminho = f"{_base_do_marco(vigente.content)}/drawMethod/occurrence"

    corpo = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{caminho: "5999"}),
            "justificativa": "A extração citada estava errada.",
        },
    ).content.decode()

    # **O rótulo é o mesmo da composição e o do documento publicado** (035, FR-507, Princípio I).
    # Ele dizia "Ocorrência que fixa a semente" aqui e "que fixará" nas outras duas: dois nomes
    # para o mesmo campo, e o que fica é o de `CAMPOS_DO_METODO`, que é de onde o documento tira
    # os dele desde a `032`.
    assert "Ocorrência que fixará a semente" in corpo
    assert "drawMethod" not in corpo


def test_a_tela_do_sorteio_aponta_o_caminho_que_ela_manda_seguir(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload
):
    """A contradição mais visível do produto, fechada (026, US4).

    A tela do sorteio dizia "alterá-lo é uma Retificação" e não dizia por onde — e até esta feature
    não havia por onde: a Retificação não oferecia um único dos dez campos. Agora o caminho existe,
    e a frase o nomeia; dizer a regra sem apontar o meio deixava quem lê exatamente onde estava.
    """
    from django.urls import reverse as url

    from tests.fixtures.sorteio import certame_de_sorteio

    certame = certame_de_sorteio(gestor, api_client, manager_headers, process_payload)
    edital = certame["edital"]
    endereco = url("interface:sorteio", args=[edital.id, certame["marco"]])
    caminho_da_retificacao = url("interface:retificar", args=[edital.id])

    # **A presidência abre esta tela e não elabora Retificação.** Para ela o link terminaria numa
    # tela que se anuncia somente leitura — trocar o beco sem saída por um beco sinalizado não é
    # ganho. A frase diz quem pode, e não oferece um caminho que não termina.
    identificar(client, "maria", [])
    da_presidencia = client.get(endereco).content.decode()
    assert "Alterá-lo é uma Retificação" in da_presidencia
    assert "quem elabora Retificações é quem pode alterá-lo" in da_presidencia
    assert caminho_da_retificacao not in da_presidencia

    # Para quem elabora, o caminho existe e a frase o nomeia. **É a mesma pessoa**, com o papel
    # acumulado: numa equipe de duas ou três, quem preside a comissão também elabora — e é
    # exatamente aí que o link vale a pena.
    identificar(client, "maria", ["elaborador"])
    de_quem_elabora = client.get(endereco).content.decode()
    assert "Alterá-lo é uma Retificação" in de_quem_elabora
    assert caminho_da_retificacao in de_quem_elabora


def test_o_marco_sem_metodo_oferece_os_dez_campos_em_branco(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-313 pelo canal do ator: é assim que o acervo anterior ao degrau 10 declara o método.

    Todo Edital publicado antes daquele degrau carrega `drawMethod` nulo. A primeira redação só
    mostrava os campos quando o objeto já existia — e, com isso, o acervo inteiro dependia da API
    para declarar o método, que é o que o princípio VI não admite.
    """
    rascunho = rascunho_completo()
    # **Marco declarado, método nulo** — é o retrato de todo Edital publicado antes do degrau 10.
    # Um rascunho sem marco nenhum não serviria: o caso é o do marco que existe e não sorteia, e um
    # teste que pulasse aqui não valeria nada.
    for perfil_ in rascunho["profiles"]:
        for marco_ in perfil_.get("classificationMilestones") or []:
            marco_["drawMethod"] = None
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho, anexos=1
    )
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    perfil = next(p for p in vigente.content["profiles"] if p.get("classificationMilestones"))
    assert perfil["classificationMilestones"][0]["drawMethod"] is None

    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()

    for _, rotulo, _ in CAMPOS_DO_METODO:
        assert rotulo in corpo, f"o marco sem método não oferece '{rotulo}'"


def test_o_marco_sem_metodo_declara_o_metodo_inteiro_e_o_ato_publica(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-313 até o fim: a tela oferecia os dez campos e o ato não saía do lugar (PR #114).

    Oferecer os campos não é oferecer o caminho. Cada um deles virava um `REPLACE` endereçado
    para dentro de `drawMethod`, que é nulo — e a gramática recusava o ato inteiro com
    `CaminhoInexistente`, num erro que não nomeia nada que o servidor possa corrigir. O teste
    anterior conferia a tela; este atravessa a jornada, que é onde o defeito vivia.

    O objeto que ainda não existe se declara **inteiro**, num `REPLACE` só — a mesma forma que a
    021 usa pela API para elevar o acervo anterior ao degrau 10.
    """
    rascunho = rascunho_completo()
    for perfil_ in rascunho["profiles"]:
        for marco_ in perfil_.get("classificationMilestones") or []:
            marco_["drawMethod"] = None
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho, anexos=1
    )
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    base = _base_do_marco(vigente.content)

    identificar(client, "ana.elaboradora", ["elaborador"])
    declarado = {
        f"{base}/drawMethod/algorithm": "IFES-SORTEIO-SHA256-v1",
        f"{base}/drawMethod/source": "Fonte de demonstração",
        f"{base}/drawMethod/occurrence": "5901",
        f"{base}/drawMethod/occurrenceAt": "2020-01-01T20:00",
        f"{base}/drawMethod/derivation": "A extração de sábado imediatamente anterior.",
        f"{base}/drawMethod/normalization/rule": "DIGITOS_EM_SEQUENCIA",
        f"{base}/drawMethod/normalization/text": "Os cinco números, na ordem dos prêmios.",
        f"{base}/drawMethod/substitutionRule/rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        f"{base}/drawMethod/substitutionRule/text": "Vale a seguinte da mesma fonte.",
        f"{base}/drawMethod/qualifyingStageId": ETAPA["A"],
    }
    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **declarado),
            "justificativa": "O Edital foi publicado antes do método existir.",
            "confirmar": "1",
            "chave_idempotencia": "retificar-metodo-nascendo",
        },
    )
    assert resposta.status_code in (200, 302), resposta.content

    # **Uma alteração, e não dez**: o objeto ausente se endereça inteiro.
    retificacao = Retificacao.objects.get()
    alteracao = retificacao.alteracoes.get(target_path=f"{base}/drawMethod")
    assert alteracao.new_value["algorithm"] == "IFES-SORTEIO-SHA256-v1"
    assert alteracao.new_value["normalization"]["rule"] == "DIGITOS_EM_SEQUENCIA"
    assert alteracao.new_value["qualifyingStageId"] == ETAPA["A"]

    publish_retification(api_client, retificacao)
    depois = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    perfil = next(p for p in depois.content["profiles"] if p.get("classificationMilestones"))
    metodo = perfil["classificationMilestones"][0]["drawMethod"]
    assert metodo["occurrence"] == "5901"
    assert metodo["substitutionRule"]["text"] == "Vale a seguinte da mesma fonte."
