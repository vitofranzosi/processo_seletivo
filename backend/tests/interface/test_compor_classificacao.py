"""O passo que declara a classificação, e a regra que sai dele precisa rodar (015, T072-T075).

**Por que este passo é separado do de Perfis.** O marco enumera Etapas, e seus critérios apontam
Etapa ou fato declarado. No passo de Perfis, que vem antes das Etapas, isso seria oferecer uma lista
vazia e chamá-la de escolha — a mesma razão pela qual a Inscrição veio depois do Cronograma.

O teste que fecha a fatia não confere campos: confere que a regra que a tela produz é
**executável**.
Antes desta correção a tela publicava marco sem Etapa e critério sem alvo, e o cálculo não tinha o
que combinar.
"""

from decimal import Decimal

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.domain.combinacao import SEM_PONTUACAO, combinar
from processo_seletivo.editais.models.perfis import MarcoClassificatorio
from tests.interface.conftest import identificar
from tests.interface.test_compor import PERFIL

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ETAPA_CLASSIFICATORIA = "aaaaaaaa-0000-4000-8000-00000000e021"
ETAPA_SO_ELIMINATORIA = "aaaaaaaa-0000-4000-8000-00000000e023"
MARCO = "aaaaaaaa-0000-4000-8000-00000000e051"
CRITERIO = "aaaaaaaa-0000-4000-8000-00000000e061"
FATO = "aaaaaaaa-0000-4000-8000-00000000e071"


def marco_form(**alteracoes):
    base = {
        "perfil_id": PERFIL,
        f"marco-{PERFIL}-0-id": MARCO,
        f"marco-{PERFIL}-0-code": "FINAL",
        f"marco-{PERFIL}-0-name": "Classificação final",
        f"marco-{PERFIL}-0-stages": ETAPA_CLASSIFICATORIA,
        f"marco-{PERFIL}-0-operation": "SOMA_PONDERADA",
        f"marco-{PERFIL}-0-normalization": "NENHUMA",
        f"marco-{PERFIL}-0-scale": "2",
        f"marco-{PERFIL}-0-mode": "MEIO_PARA_CIMA",
        f"criterio-{PERFIL}-0-0-id": CRITERIO,
        f"criterio-{PERFIL}-0-0-order": "1",
        f"criterio-{PERFIL}-0-0-type": "MAIOR_PONTUACAO_NA_ETAPA",
        f"criterio-{PERFIL}-0-0-target": ETAPA_CLASSIFICATORIA,
        f"criterio-{PERFIL}-0-0-whenMissing": "ULTIMO_NO_CRITERIO",
    }
    return {**base, **alteracoes}


def test_o_passo_vem_depois_das_etapas():
    from processo_seletivo.interface.views import CHAVES_ETAPA

    assert CHAVES_ETAPA.index("classificacao") > CHAVES_ETAPA.index("etapas")


def test_get_oferece_so_etapas_classificatorias(client, com_etapas):
    client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]), marco_form()
    )

    resposta = client.get(reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]))
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    assert "Marcos classificatórios" in corpo
    assert '<form method="post" id="formulario">' in corpo
    assert 'name="destino" value="classificacao"' in corpo
    assert f'hx-get="/gestao/fragmentos/perfil/{PERFIL}/marco' in corpo
    assert f'hx-target="#marcos-{PERFIL}"' in corpo
    assert 'src="/static/interface/htmx.min.js"' in corpo
    assert "Prova didática" in corpo
    assert "Análise documental" not in corpo


def test_recusa_reexibe_o_que_foi_digitado(client, com_etapas):
    nome_digitado = "Classificação digitada e ainda não salva"

    resposta = client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]),
        marco_form(
            **{
                f"marco-{PERFIL}-0-name": nome_digitado,
                f"criterio-{PERFIL}-0-0-target": "",
            }
        ),
    )

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert nome_digitado in corpo
    assert f'<option value="{ETAPA_CLASSIFICATORIA}" selected>' in corpo
    assert 'value="2" required' in corpo
    assert '<option value="MEIO_PARA_CIMA" selected>' in corpo


def test_o_percurso_produz_regra_executavel(client, com_etapas):
    """Interface → rascunho → domínio: o que a tela grava, o cálculo consegue rodar.

    É a prova que faltava. Sem Etapa enumerada, `combinar` devolve `SEM_PONTUACAO` para todo mundo
    — e era exatamente isso que a tela publicava antes desta correção.
    """
    resposta = client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]), marco_form()
    )

    assert resposta.status_code == 302, resposta.content
    marco = MarcoClassificatorio.objects.get(pk=MARCO)
    assert [str(item) for item in marco.etapas] == [ETAPA_CLASSIFICATORIA]
    assert marco.arredondamento == {"scale": 2, "mode": "MEIO_PARA_CIMA"}
    assert marco.criterios.get().parametros == {"stageId": ETAPA_CLASSIFICATORIA}

    combinada = combinar(
        {
            "stages": [str(item) for item in marco.etapas],
            "operation": marco.operacao,
            "normalization": marco.normalizacao,
            "rounding": marco.arredondamento,
        },
        {ETAPA_CLASSIFICATORIA: {"weight": "2.0000"}},
        {ETAPA_CLASSIFICATORIA: Decimal("8.5")},
    )

    assert combinada is not SEM_PONTUACAO
    assert combinada == Decimal("17.00")


def test_marco_sem_etapa_e_recusado(client, com_etapas):
    resposta = client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]),
        marco_form(**{f"marco-{PERFIL}-0-stages": ""}),
    )

    assert resposta.status_code == 200, "recusa reexibe o formulário"
    assert not MarcoClassificatorio.objects.filter(pk=MARCO).exists()


def test_criterio_sem_alvo_e_recusado(client, com_etapas):
    resposta = client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]),
        marco_form(**{f"criterio-{PERFIL}-0-0-target": ""}),
    )

    assert resposta.status_code == 200
    assert not MarcoClassificatorio.objects.filter(pk=MARCO).exists()


def test_gravar_a_classificacao_preserva_o_resto_do_perfil(client, com_etapas):
    """`replace_draft` substitui o rascunho inteiro: este passo funde marcos sobre o persistido."""
    perfil = com_etapas.perfis.get()
    antes = (perfil.name, perfil.locality, perfil.immediate_vacancies)

    client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]), marco_form()
    )

    perfil.refresh_from_db()
    assert (perfil.name, perfil.locality, perfil.immediate_vacancies) == antes


def test_marco_recem_acrescentado_leva_o_edital_ate_o_criterio(client, com_etapas):
    """O caminho principal da composição: acrescentar marco **e** critérios de uma vez (E2E15-001).

    O fragmento de marco não é folha — dele nasce o botão que pede o fragmento de critério, e é
    esse pedido que carrega o Edital na query. Sem o Edital no contexto do marco, o `hx-get` saía
    com o parâmetro vazio, o critério nascia com o select "O que ele compara" só com o `—`, e como
    ele é obrigatório o formulário não podia ser enviado. O contorno — preencher o marco, salvar o
    rascunho e recarregar, para que o marco viesse do servidor dentro da tela inteira — exige
    conhecimento interno, de modo que o defeito atingia exatamente quem seguia o caminho óbvio.

    O teste anda os dois saltos do htmx, e não só o primeiro: o que importa não é o parâmetro estar
    no atributo, é o critério que vem dele enxergar as Etapas classificatórias e os fatos.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    marco = client.get(
        reverse("interface:fragmento-marco", args=[PERFIL]),
        {"edital": str(com_etapas.id), "indice": "0"},
    ).content.decode()

    assert f"?edital={com_etapas.id}" in marco, "o botão de critério precisa levar o Edital adiante"
    endereco = marco.split('hx-get="')[1].split('"')[0]
    assert endereco.startswith(reverse("interface:fragmento-criterio", args=[PERFIL, "0"]))

    # O endereço vai inteiro, com a query que o botão montou: passar `data` ao cliente de teste
    # descartaria a query do caminho, e o teste deixaria de exercitar justamente o que se corrigiu.
    criterio = client.get(f"{endereco}&indice=0").content.decode()

    assert f'<option value="{ETAPA_CLASSIFICATORIA}"' in criterio
    assert "Prova didática" in criterio
    assert f'<option value="{FATO}"' in criterio, "o desempate por fato precisa do fato na lista"
    assert f'<option value="{ETAPA_SO_ELIMINATORIA}"' not in criterio


def test_fragmento_de_marco_sem_edital_nao_quebra(client, com_etapas):
    """A rota é pública ao assistente e o parâmetro pode faltar; faltar é lista vazia, não erro."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.get(reverse("interface:fragmento-marco", args=[PERFIL]), {"indice": "0"})

    assert resposta.status_code == 200
    assert "?edital=" in resposta.content.decode()
