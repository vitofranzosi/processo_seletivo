"""Cada membro dá o parecer sem ver o dos outros, e quem viu não avalia (165, US2).

O Edital de `tests/fixtures/deliberacao.py`, com `maria` — a presidência — alocada também na
Heteroidentificação: a equipe pequena, em que quem preside dá parecer.

```text
FR-7056  às cegas      quem tem parecer pendente não recebe o sentido nem o texto alheio
FR-7057  Mesa          nunca mostra o parecer dos colegas, antes ou depois de concluir
FR-7059  candidato     a Mesa continua mostrando os dados da inscrição
FR-7082  exposição     o que é entregue fica registrado, e barra a atribuição
FR-7083  reabertura    o parecer do autor exposto não se reabre
UX-751   Mesa          "Os demais membros não veem o seu parecer, e você não vê o deles."
UX-754   Mesa          o desfavorável chega ao candidato sem o nome
```
"""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application import cegas
from processo_seletivo.avaliacoes.application.avaliacao import reabrir
from processo_seletivo.avaliacoes.models import ExposicaoAoParecer
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.deliberacao import (
    concluir_pareceres,
    distribuir_na_hetero,
    montar_colegiada,
    na_hetero,
)
from tests.fixtures.mesa import distribuir_para
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

F, D = "FAVORAVEL", "DESFAVORAVEL"


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    """A candidata com dois pareceres de três, e o de `maria`, a presidência, pendente; Joana com os
    três pareceres de Ana, Bruno e Carla."""
    cenario = montar_colegiada(
        gestor, api_client, manager_headers, seed=1681, presidencia_parecerista=True
    )
    candidata, joana, _ = cenario["inscricoes"]
    distribuir_na_hetero(cenario, gestor, [candidata], nomes=("maria", "ana", "bruno"), chave="h1")
    distribuir_na_hetero(cenario, gestor, [joana], chave="h2")
    concluir_pareceres(cenario, candidata, {"ana": D, "bruno": D})
    concluir_pareceres(cenario, joana, {"ana": D, "bruno": F, "carla": F})
    cenario["gestor"] = gestor
    return cenario


def _url(cenario, nome, **kw):
    return reverse(f"interface:{nome}", args=[cenario["edital"].id, cenario["hetero"]], **kw)


def test_as_conclusoes_preservadas_ocultam_o_parecer_alheio_a_quem_esta_pendente(
    client, seletor_ligado, cenario
):
    """FR-7056: o servidor não entrega o sentido nem o texto de Ana e Bruno sobre a candidata."""
    identificar(client, "maria", ["gestor"])
    candidata, joana, _ = cenario["inscricoes"]

    corpo = client.get(_url(cenario, "conclusoes-preservadas")).content.decode()

    assert cegas.OCULTO in corpo
    # Ana indeferiu as duas; o texto dela sobre Joana aparece uma vez, e o sobre a candidata, não.
    assert corpo.count("Parecer de ana: desfavoravel.") == 1
    assert "Parecer de bruno: desfavoravel." not in corpo
    # Joana não tem pendência de `maria`: as conclusões dela aparecem como hoje.
    assert "Parecer de carla: favoravel." in corpo
    expostas = set(
        ExposicaoAoParecer.objects.filter(pessoa="maria").values_list("inscricao_id", flat=True)
    )
    assert expostas == {joana.id}


def test_o_filtro_direto_da_inscricao_tambem_oculta(client, seletor_ligado, cenario):
    """FR-7056: o link direto, filtrado pelo protocolo, não abre o que a lista esconde."""
    identificar(client, "maria", ["gestor"])
    candidata = cenario["inscricoes"][0]

    corpo = client.get(
        _url(cenario, "conclusoes-preservadas"), {"inscricao": candidata.protocolo}
    ).content.decode()

    assert "Parecer de ana" not in corpo and "Parecer de bruno" not in corpo
    assert cegas.OCULTO in corpo
    assert not ExposicaoAoParecer.objects.filter(pessoa="maria", inscricao=candidata).exists()


def test_a_exposicao_barra_a_atribuicao(client, seletor_ligado, cenario):
    """FR-7082, D-010: `maria` leu os pareceres de Joana, e não pode avaliá-la."""
    identificar(client, "maria", ["gestor"])
    client.get(_url(cenario, "conclusoes-preservadas"))
    joana = cenario["inscricoes"][1]

    resultado = distribuir_para(
        na_hetero(cenario), cenario["gestor"], ["maria"], [joana], chave="exposta"
    )

    texto = str(resultado)
    assert "já teve acesso aos pareceres dos colegas" in texto
    assert not joana.atribuicoes.filter(membro__identity_subject="maria", ativo=True).exists()


def test_o_parecer_do_autor_exposto_nao_se_reabre(cenario):
    """FR-7083: Ana concluiu sobre Joana e depois leu os colegas; a reabertura é recusada."""
    joana = cenario["inscricoes"][1]
    avaliacao = joana.atribuicoes.get(membro__identity_subject="ana").avaliacao
    cegas.registrar_exposicao("ana", cenario["edital"], cenario["hetero"], [joana.id])

    with pytest.raises(DomainError) as recusa:
        reabrir(
            actor=ator_institucional("maria"),
            processo_id=cenario["processo"].id,
            avaliacao_id=avaliacao.id,
            motivo="erro material",
            expected_revision=avaliacao.revision,
            idempotency_key="reabrir-exposta",
            correlation_id="teste",
        )
    assert recusa.value.code == "parecer_exposto"


def test_o_parecer_do_autor_nao_exposto_volta_a_pendencia(cenario):
    """FR-7058: reaberto, Bruno volta a ter parecer pendente, e o às cegas volta a valer."""
    joana = cenario["inscricoes"][1]
    avaliacao = joana.atribuicoes.get(membro__identity_subject="bruno").avaliacao

    reabrir(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        avaliacao_id=avaliacao.id,
        motivo="erro material",
        expected_revision=avaliacao.revision,
        idempotency_key="reabrir-limpa",
        correlation_id="teste",
    )

    assert joana.id in cegas.pendentes("bruno", cenario["edital"], cenario["hetero"])


def test_a_mesa_nao_mostra_o_parecer_dos_colegas(client, seletor_ligado, cenario):
    """FR-7057, FR-7059, UX-751, UX-754: antes e depois de concluir, e com o candidato à vista."""
    candidata = cenario["inscricoes"][0]
    url = reverse(
        "interface:mesa-inscricao",
        args=[cenario["edital"].id, cenario["hetero"], candidata.id],
    )
    # Ana já concluiu: o formulário não aparece mais, e a Mesa continua sem o parecer de Bruno.
    identificar(client, "ana", ["avaliador"])
    corpo = client.get(url).content.decode()
    assert "Os demais membros não veem o seu parecer, e você não vê o deles." in corpo
    assert "Parecer de bruno" not in corpo
    assert candidata.protocolo in corpo

    # `maria` ainda vai preencher: a instrução de preenchimento diz o que o candidato lerá.
    identificar(client, "maria", ["avaliador"])
    corpo = client.get(url).content.decode()
    assert "o candidato o lê sem o seu nome" in corpo
    assert "Parecer de ana" not in corpo and "Parecer de bruno" not in corpo


def test_na_etapa_de_uma_avaliacao_nada_se_oculta_nem_se_registra(client, seletor_ligado, cenario):
    """O às cegas é da Etapa colegiada: a Análise, de uma avaliação, segue como hoje."""
    identificar(client, "maria", ["gestor"])
    url = reverse(
        "interface:conclusoes-preservadas", args=[cenario["edital"].id, cenario["analise"]]
    )

    corpo = client.get(url).content.decode()

    assert cegas.OCULTO not in corpo
    assert not ExposicaoAoParecer.objects.filter(etapa_id=cenario["analise"]).exists()
