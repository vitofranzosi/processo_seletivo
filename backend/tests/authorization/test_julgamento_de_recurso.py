"""Julgar é autoridade própria — e quem produziu o ato atacado não decide sobre ele.

Duas garantias distintas, e é preciso as duas:

```text
capacidade   sem `recurso:julgar` ninguém julga — nem quem preside a comissão
impedimento  tendo a capacidade, quem praticou o ato atacado ainda assim é recusado
```

A primeira sozinha permitiria conceder o papel a quem avaliou; a segunda sozinha permitiria julgar
a quem nunca recebeu autoridade para isso. A D-005 fecha as duas: papel **próprio**, porque cada
papel existente reúne justamente quem tende a estar impedido, e cinco perguntas pontuais no
instante da gravação (T-005, T-006, FR-037, FR-039, FR-043).
"""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.models import Impedimento
from processo_seletivo.publicacoes.application.selectors import selecao_publica
from processo_seletivo.recursos.application.admitir import admitir
from processo_seletivo.recursos.domain.elegibilidade import BARRADO
from processo_seletivo.recursos.models import JuizoDeAdmissibilidade
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.divulgacao import (
    PUBLICADORA,
    emitir,
    montar_marco,
    pontuar,
    publicar_o_ato,
)
from tests.fixtures.recursos import interpor
from tests.fixtures.recursos_us4 import assinatura_de
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.authorization]

JULGADORA = "helena.julgadora"


def julgador(subject=JULGADORA):
    return ator_institucional(subject, "recurso:julgar")


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    """Um recurso contra o `ResultadoEtapa`, e outro contra a publicação do marco."""
    cenario = montar_marco(
        gestor, api_client, manager_headers, process_payload, seed=98, codigo="0798"
    )
    cenario["inscricoes"] = pontuar(
        cenario, gestor, ["90.0000", "70.0000"], primeiro=981, sufixo="98"
    )
    cenario["ato"] = emitir(cenario, gestor, chave="emitir-018-us3")
    publicacao = publicar_o_ato(cenario, chave="publicar-018-us3")
    inscricao, outra = cenario["inscricoes"]
    versao = selecao_publica(edital_id=inscricao.edital_id)
    contra_resultado = interpor(
        inscricao=inscricao,
        versao=versao,
        resultado=ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"]),
        protocolo="REC-2026-US30001",
    )
    contra_publicacao = interpor(
        inscricao=outra,
        versao=versao,
        publicacao=publicacao,
        protocolo="REC-2026-US30002",
    )
    return {
        "cenario": cenario,
        "resultado": contra_resultado,
        "publicacao": contra_publicacao,
        "inscricao": inscricao,
    }


def apreciar(ator, recurso, *, chave="apreciar-us3"):
    return admitir(
        actor=ator,
        recurso_id=recurso.id,
        admitido=True,
        motivo="Tempestivo e regularmente instruído.",
        assinatura_do_estado=assinatura_de(recurso),
        idempotency_key=chave,
    )


# ---------------------------------------------------------------------------
# T053 — a capacidade
# ---------------------------------------------------------------------------


def test_quem_tem_a_capacidade_julga(peca):
    """A prova de que as recusas abaixo não são uma rota quebrada."""
    juizo = apreciar(julgador(), peca["resultado"])

    assert juizo.admitido
    assert juizo.decidido_por == JULGADORA


def test_sem_a_capacidade_e_403(peca, gestor):
    with pytest.raises(DomainError) as recusa:
        apreciar(gestor, peca["resultado"])

    assert recusa.value.code == "forbidden"
    assert recusa.value.status == 403
    assert not JuizoDeAdmissibilidade.objects.exists()


def test_presidir_a_comissao_nao_concede_julgamento(peca):
    """**Nem o presidente da comissão** (FR-038).

    É a derivação mais tentadora — quem preside a comissão conduz o certame —, e é justamente a
    que a D-005 recusa: a comissão produziu o ato atacado, e quem a preside responde por ele.
    """
    presidente = ator_institucional("maria", "comissao:gerir")

    with pytest.raises(DomainError) as recusa:
        apreciar(presidente, peca["resultado"])

    assert recusa.value.code == "forbidden"


def test_a_lista_nao_e_alcancavel_sem_a_capacidade(client, seletor_ligado, peca):
    identificar(client, "carlos", ["gestor"])
    edital = peca["cenario"]["edital"]

    resposta = client.get(reverse("interface:recursos", args=[edital.id]))

    assert resposta.status_code == 403


def test_a_peca_nao_e_alcancavel_sem_a_capacidade(client, seletor_ligado, peca):
    identificar(client, "carlos", ["gestor"])

    resposta = client.get(reverse("interface:recurso", args=[peca["resultado"].id]))

    assert resposta.status_code == 403


def test_o_papel_julgador_alcanca_a_lista(client, seletor_ligado, peca):
    identificar(client, JULGADORA, ["julgador"])
    edital = peca["cenario"]["edital"]

    resposta = client.get(reverse("interface:recursos", args=[edital.id]))

    assert resposta.status_code == 200
    assert "REC-2026-US30001" in resposta.content.decode()


# ---------------------------------------------------------------------------
# T052 — o impedimento
# ---------------------------------------------------------------------------


def test_quem_concluiu_a_avaliacao_fonte_e_recusado(peca):
    """A primeira das cinco perguntas: julgar o recurso contra o próprio parecer."""
    avaliadora = julgador(peca["cenario"]["membros"]["joao"].identity_subject)

    with pytest.raises(DomainError) as recusa:
        apreciar(avaliadora, peca["resultado"])

    assert recusa.value.code == BARRADO
    assert recusa.value.status == 403
    assert "Avaliação" in recusa.value.detail


def test_quem_consolidou_o_resultado_e_recusado(peca):
    """Consolidar é ato: quem o praticou responde pelo Resultado que o recurso ataca."""
    consolidadora = julgador("carlos")

    with pytest.raises(DomainError) as recusa:
        apreciar(consolidadora, peca["resultado"])

    assert recusa.value.code == BARRADO
    assert "consolidou" in recusa.value.detail


def test_quem_emitiu_o_ato_atacado_e_recusado(peca):
    """No ramo da publicação, o ato de ordenação é parte do que se contesta."""
    emitente = julgador("carlos")

    with pytest.raises(DomainError) as recusa:
        apreciar(emitente, peca["publicacao"])

    assert recusa.value.code == BARRADO
    assert "emitiu" in recusa.value.detail


def test_quem_publicou_e_recusado(peca):
    publicadora = julgador(PUBLICADORA)

    with pytest.raises(DomainError) as recusa:
        apreciar(publicadora, peca["publicacao"])

    assert recusa.value.code == BARRADO
    assert "publicação" in recusa.value.detail


def test_o_impedimento_declarado_da_012_tambem_recusa(peca):
    """Sem conceito novo: é o mesmo `Impedimento` que a 012 já grava (T-006, FR-040)."""
    from django.utils import timezone

    Impedimento.objects.create(
        identity_subject=JULGADORA,
        inscricao=peca["inscricao"],
        motivo="Parentesco declarado.",
        criado_em=timezone.now(),
        criado_por="carlos",
    )

    with pytest.raises(DomainError) as recusa:
        apreciar(julgador(), peca["resultado"])

    assert recusa.value.code == BARRADO
    assert "impedimento declarado" in recusa.value.detail


def test_o_impedimento_e_nomeado_na_tela_antes_de_qualquer_botao(client, seletor_ligado, peca):
    """Nomear só depois do clique faria escrever a motivação inteira à toa (FR-042)."""
    identificar(client, "carlos", ["julgador"])

    corpo = client.get(reverse("interface:recurso", args=[peca["resultado"].id])).content.decode()

    assert "Você não pode julgar este recurso" in corpo
    assert "consolidou" in corpo
    assert "Não admitir" not in corpo, "o botão não é oferecido a quem está impedido"


def test_sem_impedimento_a_tela_oferece_a_apreciacao(client, seletor_ligado, peca):
    identificar(client, JULGADORA, ["julgador"])

    corpo = client.get(reverse("interface:recurso", args=[peca["resultado"].id])).content.decode()

    assert "Você não pode julgar este recurso" not in corpo
    assert "Não admitir" in corpo
