"""A tela de Retificação alcança a declaração de reversão (016, `FR-250`).

O Princípio VI diz que capacidade que nenhuma interface alcança não está entregue — e aqui há um
agravante que a `025` registrou em letras: **endereço de retificação não se conserta depois**,
porque publicação é ato imutável. Sem esta entrada no catálogo, o primeiro Edital publicado com
reversão nasceria irretificável naquele campo.

**O campo é `REFERENCIA`, e não caixa de texto**, pelo precedente literal do `cutRule/tieOutcome`:
são dois valores fechados, e a referência os oferece conferindo a escolha contra a lista. Texto
livre publicaria gatilho que o cálculo não interpreta — e reversão sob gatilho errado é vaga que
saiu do recorte reservado sem fundamento.

**E ele aparece também onde o objeto não existe** (048, FR-791). Até a 048 só aparecia com a
reversão já declarada, e o Perfil publicado sem ela não tinha como declará-la pela tela — o
G16-001. O vazio é "este Edital não reverte", e nada nasce enquanto ele fica ali.
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface.retificacao import campos_editaveis, diferencas
from processo_seletivo.ocupacao.domain import nomes
from tests.fixtures.edital import complete_draft
from tests.fixtures.legado import antes_do_quadro
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

PERFIL = "00000000-0000-0000-0000-000000000401"
GERAL = "00000000-0000-0000-0000-000000252001"
CAMINHO = f"/profiles/id={PERFIL}/vacancyReversion/kind"


def rascunho(reversao=None):
    dados = complete_draft()
    perfil = dados["profiles"][0]
    perfil["immediateVacancies"] = 60
    perfil["vacancyTable"] = [{"id": GERAL, "modalityId": None, "immediateVacancies": 60}]
    if reversao is not None:
        perfil["vacancyReversion"] = {"kind": reversao}
    return dados


def campos_do_perfil(api_client, manager_headers, process_payload, *, reversao):
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho(reversao)
    )
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    grupos = campos_editaveis(vigente.content)
    return next(g for g in grupos if g["tipo"] == "Perfil")


def test_a_declaracao_e_retificavel_por_referencia_com_as_duas_especies(
    api_client, manager_headers, process_payload
):
    do_perfil = campos_do_perfil(
        api_client, manager_headers, process_payload, reversao=nomes.REVERSAO_POR_SALDO
    )
    campo = next(c for c in do_perfil["campos"] if c["caminho"] == CAMINHO)

    assert campo["tipo"] == "referencia"
    assert [identificador for identificador, _ in campo["opcoes"]] == [
        nomes.REVERSAO_POR_ESGOTAMENTO,
        nomes.REVERSAO_POR_SALDO,
    ]
    # As opções levam as **mesmas palavras da tela de composição**: quem retifica escolhe entre o
    # que já leu ao declarar, e não entre dois códigos.
    assert dict(campo["opcoes"])[nomes.REVERSAO_POR_SALDO] == "A quantidade que ficou sem preencher"


def test_o_rotulo_do_vazio_diz_o_que_o_vazio_provoca(api_client, manager_headers, process_payload):
    """O `select` de referência sempre desenha o vazio; dizer o que ele faz é o mínimo.

    Sem gatilho, a reversão declarada **não publica** — e a ausência do objeto inteiro é "este
    Edital não reverte vaga reservada".
    """
    do_perfil = campos_do_perfil(
        api_client, manager_headers, process_payload, reversao=nomes.REVERSAO_POR_ESGOTAMENTO
    )
    campo = next(c for c in do_perfil["campos"] if c["caminho"] == CAMINHO)

    assert campo["rotulo_do_vazio"] == "Nenhum — este Edital não reverte vaga reservada"


def test_o_campo_aparece_onde_o_objeto_nao_existe(api_client, manager_headers, process_payload):
    """048, FR-791 — a premissa deste caso se inverteu.

    Ele prendia a **ausência**: *"criar a declaração é acréscimo de campo, e não alteração dele"*. O
    contrato já dizia que a reversão pode nascer (`PODE_PASSAR_A_EXISTIR`), e a tela não oferecia
    o caminho — é o G16-001. O campo aparece vazio, com o rótulo do que o vazio significa.
    """
    do_perfil = campos_do_perfil(api_client, manager_headers, process_payload, reversao=None)
    campo = next(c for c in do_perfil["campos"] if c["caminho"] == CAMINHO)

    assert campo["valor"] == ""
    assert campo["rotulo_do_vazio"] == "Nenhum — este Edital não reverte vaga reservada"


def _publicado(api_client, manager_headers, process_payload, *, quadro=True):
    """Sem quadro, só o acervo: desde a `027` a composição materializa a linha geral."""
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    publicar = publish_original if quadro else antes_do_quadro
    edital = publicar(api_client, manager_headers, process_payload, draft=rascunho(None))
    return edital, VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def _formulario(vigente, **alteracoes):
    """O que o formulário envia sem ninguém tocar em nada, mais as alterações por caminho."""
    do_formulario = [c for g in campos_editaveis(vigente.content) for c in g["campos"]]
    enviados = {f"campo:{c['referencia']}": c["valor"] for c in do_formulario}
    referencia = {c["caminho"]: c["referencia"] for c in do_formulario}
    enviados.update({f"campo:{referencia[c]}": valor for c, valor in alteracoes.items()})
    return enviados


def test_deixado_em_nenhum_nada_nasce(api_client, manager_headers, process_payload):
    _, vigente = _publicado(api_client, manager_headers, process_payload)

    alteracoes, _ = diferencas(vigente.content, _formulario(vigente))

    assert alteracoes == []


def test_escolhida_a_especie_a_reversao_nasce_inteira(api_client, manager_headers, process_payload):
    _, vigente = _publicado(api_client, manager_headers, process_payload)

    alteracoes, resumo = diferencas(
        vigente.content, _formulario(vigente, **{CAMINHO: nomes.REVERSAO_POR_SALDO})
    )

    assert alteracoes == [
        {
            "targetPath": f"/profiles/id={PERFIL}/vacancyReversion",
            "operation": "REPLACE",
            "newValue": {"kind": nomes.REVERSAO_POR_SALDO},
        }
    ]
    # FR-800: o resumo diz, por extenso, o que nasceu — e que antes não havia nada.
    assert [(linha["antes"], linha["depois"]) for linha in resumo] == [
        ("—", "A quantidade que ficou sem preencher")
    ]


def _retificar(client, edital, dados, chave):
    identificar(client, "ana.elaboradora", ["elaborador"])
    return client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **dados,
            "justificativa": "O Edital não declarou como reverte a vaga reservada.",
            "confirmar": "1",
            "chave_idempotencia": chave,
        },
    )


def test_sem_quadro_a_reversao_que_nasce_e_recusada(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """A validação que já existe vale para o que nasce: reversão pressupõe quadro (016)."""
    from processo_seletivo.publicacoes.models_retificacao import Retificacao

    edital, vigente = _publicado(api_client, manager_headers, process_payload, quadro=False)

    corpo = _retificar(
        client,
        edital,
        {"base": str(vigente.id), **_formulario(vigente, **{CAMINHO: nomes.REVERSAO_POR_SALDO})},
        "reversao-sem-quadro-01",
    ).content.decode()

    assert not Retificacao.objects.exists()
    assert "não publica quadro" in corpo


def test_com_a_linha_acrescentada_no_mesmo_ato_a_reversao_nasce(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    from processo_seletivo.publicacoes.models_retificacao import Retificacao

    edital, vigente = _publicado(api_client, manager_headers, process_payload, quadro=False)

    resposta = _retificar(
        client,
        edital,
        {
            "base": str(vigente.id),
            **_formulario(vigente, **{CAMINHO: nomes.REVERSAO_POR_ESGOTAMENTO}),
            "novo-linha-do-quadro-0-profileId": PERFIL,
            "novo-linha-do-quadro-0-modalityId": "",
            "novo-linha-do-quadro-0-immediateVacancies": "60",
        },
        "reversao-com-quadro-01",
    )

    assert resposta.status_code == 302, resposta.content.decode()
    caminhos = set(Retificacao.objects.get().alteracoes.values_list("target_path", flat=True))
    assert f"/profiles/id={PERFIL}/vacancyReversion" in caminhos


def test_os_demais_campos_do_perfil_continuam_retificaveis(
    api_client, manager_headers, process_payload
):
    """A entrada nova não desloca as que já existiam — é o defeito que a `014` apanhou uma vez."""
    do_perfil = campos_do_perfil(
        api_client, manager_headers, process_payload, reversao=nomes.REVERSAO_POR_SALDO
    )
    caminhos = {c["caminho"] for c in do_perfil["campos"]}

    assert f"/profiles/id={PERFIL}/name" in caminhos
    assert f"/profiles/id={PERFIL}/generalCompetitionModalityId" in caminhos
