"""A tela de Retificação alcança a declaração de reversão (016, `FR-250`).

O Princípio VI diz que capacidade que nenhuma interface alcança não está entregue — e aqui há um
agravante que a `025` registrou em letras: **endereço de retificação não se conserta depois**,
porque publicação é ato imutável. Sem esta entrada no catálogo, o primeiro Edital publicado com
reversão nasceria irretificável naquele campo.

**O campo é `REFERENCIA`, e não caixa de texto**, pelo precedente literal do `cutRule/tieOutcome`:
são dois valores fechados, e a referência os oferece conferindo a escolha contra a lista. Texto
livre publicaria gatilho que o cálculo não interpreta — e reversão sob gatilho errado é vaga que
saiu do recorte reservado sem fundamento.

**E ele só aparece onde o objeto existe**, como os campos do corte: um caminho de referência para
dentro de objeto ausente não tem o que oferecer.
"""

import pytest

from processo_seletivo.interface.retificacao import campos_editaveis
from processo_seletivo.ocupacao.domain import nomes
from tests.fixtures.edital import complete_draft
from tests.fixtures.publicacao import publish_original

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


def test_o_campo_nao_aparece_onde_o_objeto_nao_existe(api_client, manager_headers, process_payload):
    """**A mesma regra dos campos do corte.**

    Um caminho de referência para dentro de objeto ausente não oferece nada, e ainda ofereceria um
    `select` cujo envio em branco não teria o que apagar. Criar a declaração é acréscimo de campo,
    e não alteração dele.
    """
    do_perfil = campos_do_perfil(api_client, manager_headers, process_payload, reversao=None)

    assert [c for c in do_perfil["campos"] if c["caminho"] == CAMINHO] == []


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
