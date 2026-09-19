"""O peso deixa de ser "opcional" sem ressalva, e a cobrança antecipa nove etapas (037, US4).

**O rótulo mentia na única situação em que o peso importa.** *"Peso (opcional)"* é verdade para a
Etapa que nenhum marco enumera, e falso para a que algum enumera — e a conferência de publicação já
sabia disso: *"O marco enumera uma Etapa sem peso declarado. Quem enumera declara o peso."* Ela só
dizia na etapa 9.

**O que se prende aqui é o momento**, e não a existência da cobrança. Ela existe desde a `015`; o
que a `037` muda é quando ela é lida. O cartão do marco já se reconstrói a cada mudança da seleção,
e é esse ciclo — `fragmento-marco-recomposto` — que dá o *"no momento em que enumera"*: **não há
tela nova**, e é por isso que a `FR-551a` continua satisfeita.

**As quatro rotas.** A lista de Etapas classificatórias é montada por um helper só e consumida em
quatro pontos de `views.py`. Acrescentar o campo no helper cobre os quatro; acrescentá-lo em três
deixaria o cartão mudo numa das rotas — e a que ficaria mudo é justamente a do fragmento
recomposto, que é a que importa. É a conta que a `034` pagou para aprender, e por isso as quatro
são exercitadas uma a uma.
"""

import pytest
from django.urls import reverse

from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_compor import PERFIL, eventos, perfis

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

SEM_PESO = "aaaaaaaa-0000-4000-8000-000000000371"
COM_PESO = "aaaaaaaa-0000-4000-8000-000000000372"
MARCO = "aaaaaaaa-0000-4000-8000-000000000373"

#: O nome da Etapa que o cartão precisa **nomear**. "Aponta que falta peso" não basta: com duas
#: Etapas enumeradas e uma só sem peso, uma frase genérica manda a pessoa conferir as duas.
NOME_SEM_PESO = "Entrevista sem peso"
NOME_COM_PESO = "Prova didática"

COBRANCA = "Sem peso declarado:"


@pytest.fixture
def com_duas_etapas(client, seletor_ligado, edital):
    """Duas Etapas classificatórias: **uma com peso e uma sem**.

    As duas, e não uma: o caso que separa "nomeia a Etapa" de "avisa que falta peso" precisa de
    uma Etapa que **não** deve ser nomeada ao lado da que deve.
    """
    from tests.interface.test_compor import EVENTO

    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis=perfis(), eventos=eventos())
    edital.refresh_from_db()
    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital.id, "etapas"]),
        {
            "etapa-0-id": COM_PESO,
            "etapa-0-name": NOME_COM_PESO,
            "etapa-0-order": "1",
            "etapa-0-weight": "2",
            "etapa-0-classificatory": "on",
            "etapa-0-scheduleEventId": EVENTO,
            "etapa-1-id": SEM_PESO,
            "etapa-1-name": NOME_SEM_PESO,
            "etapa-1-order": "2",
            "etapa-1-weight": "",
            "etapa-1-classificatory": "on",
            "etapa-1-scheduleEventId": "",
        },
    )
    assert resposta.status_code == 302, resposta.content
    edital.refresh_from_db()
    return edital


def _pesar(client, edital, peso):
    """Declara o peso da Etapa que nasceu sem — é o passo 3 do cenário 4 do quickstart."""
    from tests.interface.test_compor import EVENTO

    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital.id, "etapas"]),
        {
            "etapa-0-id": COM_PESO,
            "etapa-0-name": NOME_COM_PESO,
            "etapa-0-order": "1",
            "etapa-0-weight": "2",
            "etapa-0-classificatory": "on",
            "etapa-0-scheduleEventId": EVENTO,
            "etapa-1-id": SEM_PESO,
            "etapa-1-name": NOME_SEM_PESO,
            "etapa-1-order": "2",
            "etapa-1-weight": peso,
            "etapa-1-classificatory": "on",
            "etapa-1-scheduleEventId": "",
        },
    )
    assert resposta.status_code == 302, resposta.content
    edital.refresh_from_db()


def _cartao_recomposto(client, edital, **campos):
    """O cartão reconstruído a partir do que está digitado agora — o caminho do htmx.

    **É esta a rota que dá o "no momento em que enumera"**: a seleção de Etapas dispara
    `hx-get` nela, e o cartão volta refeito sobre o que está no formulário. Um teste que passasse
    só pela composição gravada ficaria verde com o cartão mudo justamente aqui.
    """
    base = {
        f"marco-{PERFIL}-0-id": MARCO,
        f"marco-{PERFIL}-0-code": "FINAL",
        f"marco-{PERFIL}-0-name": "Classificação final",
        f"marco-{PERFIL}-0-orderProduction": "POR_PONTUACAO",
        f"marco-{PERFIL}-0-scale": "2",
        f"marco-{PERFIL}-0-mode": "MEIO_PARA_CIMA",
        "edital": str(edital.id),
    }
    resposta = client.get(
        reverse("interface:fragmento-marco-recomposto", args=[PERFIL, "0"]), {**base, **campos}
    )
    assert resposta.status_code == 200, resposta.status_code
    return resposta.content.decode()


# --- FR-550 · o rótulo declara a condição --------------------------------------------------------


def test_o_rotulo_do_peso_declara_a_condicao(client, com_duas_etapas):
    """`FR-550`: o vazio é legítimo **até que um marco enumere esta Etapa**.

    A ressalva é o que faltava, e não a palavra "opcional" — que continua verdadeira para a Etapa
    que ninguém enumera, e cuja remoção transformaria um campo legitimamente vazio em obrigatório.
    """
    pagina = client.get(
        reverse("interface:compor-etapa", args=[com_duas_etapas.id, "etapas"])
    ).content.decode()

    assert "opcional até um marco enumerar esta Etapa" in pagina


# --- FR-551 · a cobrança, no momento em que a Etapa é enumerada -----------------------------------


def test_enumerar_uma_etapa_sem_peso_nomeia_a_etapa(client, com_duas_etapas):
    """`FR-551` e `SC-192`: o cartão diz **qual** Etapa falta pesar, ali.

    Hoje isso só aparece na conferência, nove etapas adiante — quando quem enumerou já saiu da
    tela em que a decisão foi tomada.
    """
    cartao = _cartao_recomposto(
        client, com_duas_etapas, **{f"marco-{PERFIL}-0-stages": [COM_PESO, SEM_PESO]}
    )

    assert COBRANCA in cartao
    assert NOME_SEM_PESO in cartao.split(COBRANCA)[1]


def test_a_etapa_que_tem_peso_nao_e_nomeada(client, com_duas_etapas):
    """A contraprova do caso acima: a cobrança é **por Etapa**, e não do marco inteiro.

    Sem esta asserção, um cartão que listasse todas as Etapas enumeradas passaria — e mandaria a
    pessoa conferir uma que já está certa.
    """
    cartao = _cartao_recomposto(
        client, com_duas_etapas, **{f"marco-{PERFIL}-0-stages": [COM_PESO, SEM_PESO]}
    )

    assert NOME_COM_PESO not in cartao.split(COBRANCA)[1].split("</span>")[0]


def test_declarar_o_peso_some_com_a_cobranca(client, com_duas_etapas):
    """`FR-554a`: é **aviso derivado do estado**, e é isto que o prova.

    Ajuda instrucional não some quando o campo é preenchido; aviso derivado do estado, sim. É
    exatamente esta propriedade que faz a frase não desrespeitar a `FR-554`, e é por isso que ela
    é verificada e não apenas afirmada na spec.
    """
    _pesar(client, com_duas_etapas, "1.5")

    cartao = _cartao_recomposto(
        client, com_duas_etapas, **{f"marco-{PERFIL}-0-stages": [COM_PESO, SEM_PESO]}
    )

    assert COBRANCA not in cartao


def test_etapa_sem_peso_que_nenhum_marco_enumera_nao_e_acusada(client, com_duas_etapas):
    """O vazio continua legítimo (`FR-550`), e acusá-lo transformaria a correção em defeito novo.

    O marco existe e enumera **só** a Etapa que tem peso. A outra está lá, sem peso, e ninguém a
    cobra — porque ninguém a enumerou.
    """
    cartao = _cartao_recomposto(client, com_duas_etapas, **{f"marco-{PERFIL}-0-stages": COM_PESO})

    assert COBRANCA not in cartao
    assert NOME_SEM_PESO in cartao, "ela continua oferecida na lista — o que não há é cobrança"


def test_marco_que_ordena_por_sorteio_e_nao_enumera_nada_nao_acusa(client, com_duas_etapas):
    """O caso de borda da spec: sorteio sem Etapa alguma é arranjo legítimo e comum.

    Quem sorteia antes da análise documental não enumera Etapa nenhuma, e o cartão já diz isso na
    ajuda da lista. Acusar peso ali cobraria o que o marco não usa.
    """
    cartao = _cartao_recomposto(
        client,
        com_duas_etapas,
        **{
            f"marco-{PERFIL}-0-orderProduction": "POR_SORTEIO",
            f"marco-{PERFIL}-0-draw-declaration": "PROPRIO",
            f"marco-{PERFIL}-0-stages": "",
        },
    )

    assert COBRANCA not in cartao


# --- FR-551 · as quatro rotas que consomem a lista ------------------------------------------------


def _etapas_do_contexto(resposta):
    return resposta.context["etapas_classificatorias"]


def test_as_quatro_rotas_carregam_se_a_etapa_tem_peso(client, com_duas_etapas):
    """A falha que a `034` descreveu por inteiro: o campo acrescentado em três das quatro rotas.

    A lista é a mesma e o helper é um só, e é **isso** que este caso prende — não que as quatro
    desenhem a cobrança (a do critério não desenha cartão nenhum), mas que nenhuma delas receba
    uma lista mais pobre que as outras. Uma derivação repetida por rota divergiria na primeira
    mudança, e a rota esquecida ficaria muda sem nada acusar.
    """
    edital = com_duas_etapas
    rotas = {
        "composição": client.get(
            reverse("interface:compor-etapa", args=[edital.id, "classificacao"])
        ),
        "marco acrescentado": client.get(
            reverse("interface:fragmento-marco", args=[PERFIL]), {"edital": str(edital.id)}
        ),
        "marco recomposto": client.get(
            reverse("interface:fragmento-marco-recomposto", args=[PERFIL, "0"]),
            {
                f"marco-{PERFIL}-0-id": MARCO,
                f"marco-{PERFIL}-0-code": "FINAL",
                f"marco-{PERFIL}-0-name": "Classificação final",
                f"marco-{PERFIL}-0-orderProduction": "POR_PONTUACAO",
                f"marco-{PERFIL}-0-scale": "2",
                f"marco-{PERFIL}-0-mode": "MEIO_PARA_CIMA",
                f"marco-{PERFIL}-0-stages": SEM_PESO,
                "edital": str(edital.id),
            },
        ),
        "critério": client.get(
            reverse("interface:fragmento-criterio", args=[PERFIL, "0"]),
            {"edital": str(edital.id)},
        ),
    }

    for nome, resposta in rotas.items():
        assert resposta.status_code == 200, f"{nome}: {resposta.status_code}"
        etapas = _etapas_do_contexto(resposta)
        assert etapas, f"{nome}: a lista de Etapas chegou vazia"
        pesos = {item["id"]: item["tem_peso"] for item in etapas}
        assert pesos[COM_PESO] is True, f"{nome}: a Etapa com peso não foi reconhecida"
        assert pesos[SEM_PESO] is False, f"{nome}: a Etapa sem peso não foi reconhecida"
