"""O acervo publicado sem quadro ganha quantidade por Retificação, e só por ela (027, US4).

`B4`–`B10` do [quickstart](../../../specs/027-estrutural-de-vagas/quickstart.md), no ponto em que
eles deixam de ser sobre a tela e passam a ser sobre o efeito: a Ocupação, que respondia "não há
quantidade declarada a apurar", passa a ter o que apurar — e nada do que já foi praticado se mexe.

**A Retificação vale para o que vier** (FR-334). Ordem emitida, resultado publicado e convocações
feitas permanecem como estavam: o Edital ganha a quantidade que não tinha, e é dali em diante que a
apuração existe. É a mesma regra que a `026` fixou para o método do sorteio, e pela mesma razão.
"""

import pytest

from processo_seletivo.ocupacao.application.emissao import emitir_apuracao
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.domain.elevacao import elevar
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.corte import MARCO, montar_cenario_do_corte
from tests.fixtures.corte import emitir as emitir_corte
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.legado import antes_do_quadro
from tests.fixtures.publicacao import retify

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def do_acervo(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Edital publicado antes de o quadro existir, com ordem e corte já emitidos.

    É a condição de 100% do acervo — e, até esta feature, a de 100% dos Editais do ambiente.
    """
    edital, _, _ = montar_cenario_do_corte(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="acervo-027",
        publicar=antes_do_quadro,
    )
    emitir_corte(edital, gestor, chave="acervo-027-corte")
    return edital


def apurar(edital, gestor, *, chave):
    return emitir_apuracao(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=None,
        idempotency_key=chave,
        correlation_id="acervo-027",
    )


def vigente(edital):
    return elevar(effective_version(edital_id=edital.id).content)


def test_o_acervo_nao_apura_e_depois_da_retificacao_apura(do_acervo, gestor, api_client):
    """`B6` e `SC-109`: o ciclo inteiro, pelo ato que a `025` abriu e a `026` obrigou a existir."""
    perfil = vigente(do_acervo)["profiles"][0]
    assert perfil["vacancyTable"] == [], "a premissa: o Edital nasce sem quadro"

    with pytest.raises(DomainError) as antes:
        apurar(do_acervo, gestor, chave="acervo-027-antes")
    assert antes.value.code == "sem_quadro_publicado"

    retify(
        api_client,
        do_acervo,
        [
            {
                "operation": "ADD",
                "targetPath": f"/profiles/id={perfil['id']}/vacancyTable/-",
                "newValue": {
                    "id": "00000000-0000-0000-0000-0000000009c1",
                    "modalityId": None,
                    "immediateVacancies": perfil["immediateVacancies"],
                },
            }
        ],
    )

    apuracao = apurar(do_acervo, gestor, chave="acervo-027-depois")
    assert apuracao["publicadas"] == perfil["immediateVacancies"], (
        "a quantidade que a apuração usa é a que a Retificação declarou"
    )


def test_a_retificacao_nao_alcanca_o_que_ja_foi_praticado(do_acervo, api_client):
    """`B7` e FR-334: ordem emitida e resultado publicado permanecem como estavam."""
    from processo_seletivo.classificacao.models import AtoDeOrdenacao

    perfil = vigente(do_acervo)["profiles"][0]
    antes = {
        (ato.id, ato.content_hash if hasattr(ato, "content_hash") else None)
        for ato in AtoDeOrdenacao.objects.all()
    }
    assert antes, "o cenário precisa ter ordem emitida para que este teste prove algo"

    retify(
        api_client,
        do_acervo,
        [
            {
                "operation": "ADD",
                "targetPath": f"/profiles/id={perfil['id']}/vacancyTable/-",
                "newValue": {
                    "id": "00000000-0000-0000-0000-0000000009c2",
                    "modalityId": None,
                    "immediateVacancies": perfil["immediateVacancies"],
                },
            }
        ],
    )

    depois = {
        (ato.id, ato.content_hash if hasattr(ato, "content_hash") else None)
        for ato in AtoDeOrdenacao.objects.all()
    }
    assert depois == antes, "a Retificação vale para o que vier, e não reescreve ato praticado"
