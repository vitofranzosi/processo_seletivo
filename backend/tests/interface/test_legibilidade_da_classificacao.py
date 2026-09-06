"""As telas da 015 lidas por gente: nome onde há significado, data em português, ato datado.

São as quatro telas que a instituição abre para responder a um recurso, e o que a auditoria E2E
encontrou nelas não foi regra errada — foi regra ilegível: UUID na coluna de modalidade, diff que
compara posições sem mostrar a nota que mudou, data em inglês no meio de uma interface em
português, e um ato já sucedido que não diz que foi.

A distinção que este arquivo guarda é **de qual versão vem cada nome**. A ordem calculada agora
lê-se com os nomes da norma vigente, porque é sob ela que ela foi calculada; o ato histórico
lê-se com os da versão que ele congelou, porque é o que impede uma Retificação posterior de
reescrever retroativamente como um ato antigo é lido.
"""

import re

import pytest
from django.urls import reverse

from tests.fixtures.divulgacao import MODALIDADE_NOME, emitir, montar_ato_publicavel
from tests.fixtures.edital import identificador
from tests.fixtures.publicacao import retify
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

SEED = 91
CODIGO = "0791"
ETAPA_DO_MARCO = identificador(411, SEED)
PERFIL = identificador(401, SEED)
CRITERIO = "00000000-0000-4000-8000-000000000491"

# O marco publica um critério de desempate sobre a própria Etapa que ele combina: é o que faz o
# ato gravar proveniência por critério em `PosicaoNaOrdem.desempate` — a coluna que imprimia o
# enum, e que a FR-050 manda nomear.
CRITERIOS = [
    {
        "id": CRITERIO,
        "order": 1,
        "type": "MAIOR_PONTUACAO_NA_ETAPA",
        "parameters": {"stageId": ETAPA_DO_MARCO},
        "whenMissing": "ULTIMO_NO_CRITERIO",
    }
]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    """Duas inscrições pontuadas, ato emitido e vigente — o ponto de partida das quatro telas."""
    return montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=SEED,
        codigo=CODIGO,
        pontuacoes=("90.0000", "70.0000"),
        primeiro=1901,
        criterios=CRITERIOS,
    )


def _como_presidente(client):
    identificar(client, "maria", ["gestor"])


def _ordenacao(cenario):
    return reverse("interface:ordenacao", args=[cenario["edital"].id, cenario["marco"]])


def _ato(cenario, ato=None):
    alvo = ato or cenario["ato"]
    return reverse(
        "interface:ato-de-ordenacao", args=[cenario["edital"].id, alvo.marco_id, alvo.id]
    )


def _secao(corpo, titulo):
    """O trecho da página a partir de um título — para afirmar sobre a tabela certa."""
    inicio = corpo.index(titulo)
    fim = corpo.find("</table>", inicio)
    return corpo[inicio : fim if fim != -1 else len(corpo)]


def _dobrar_o_peso(api_client, cenario):
    """A Retificação do peso da E2E: mesma ordem, nota dobrada — 90,00 vira 180,00.

    É o caso que expôs o defeito, e ele é escolhido de propósito: ninguém troca de lugar, então
    um diff que só compara posições não tem nada a dizer, embora a divergência seja real.
    """
    retify(
        api_client,
        cenario["edital"],
        [
            {
                "targetPath": f"/stages/id={ETAPA_DO_MARCO}/weight",
                "operation": "REPLACE",
                "newValue": "2.0000",
            }
        ],
        suffix=f"peso-{SEED}",
    )


# ---------------------------------------------------------------------------
# E2E15-006 — resolver identificadores onde se lê significado
# ---------------------------------------------------------------------------


def test_a_ordem_calculada_nomeia_a_modalidade_em_vez_de_imprimir_o_uuid(
    client, seletor_ligado, cenario
):
    _como_presidente(client)

    ordem = _secao(client.get(_ordenacao(cenario)).content.decode(), "Ordem calculada")

    assert MODALIDADE_NOME in ordem
    assert str(cenario["modalidade"]) not in ordem


def test_o_diff_identifica_a_inscricao_pelo_protocolo_como_as_outras_tabelas(
    client, seletor_ligado, cenario, api_client
):
    _dobrar_o_peso(api_client, cenario)
    _como_presidente(client)

    diff = _secao(client.get(_ordenacao(cenario)).content.decode(), "Mudanças posição a posição")

    for inscricao in cenario["inscricoes"]:
        assert inscricao.protocolo in diff
        assert str(inscricao.id) not in diff


def test_a_proveniencia_nomeia_sem_perder_o_identificador_que_a_ancora(
    client, seletor_ligado, cenario
):
    """Ali o UUID é a âncora de auditoria: o nome **acompanha**, não substitui."""
    _como_presidente(client)

    proveniencia = _secao(client.get(_ato(cenario)).content.decode(), "Proveniência do ato")

    assert f"Edital {CODIGO}/" in proveniencia
    assert "Classificação final" in proveniencia
    assert str(cenario["edital"].id) in proveniencia
    assert str(cenario["marco"]) in proveniencia
    assert str(cenario["ato"].versao_id) in proveniencia


def test_o_ato_historico_e_lido_com_os_nomes_da_versao_que_ele_congelou(
    client, seletor_ligado, cenario, api_client
):
    """A Retificação vale dali para a frente; ela não reescreve como um ato antigo se lê.

    Resolver a proveniência pela versão vigente faria o Perfil renomeado hoje aparecer num ato
    emitido ontem — e quem confere o ato contra o Edital daquela data não encontraria o nome.
    """
    retify(
        api_client,
        cenario["edital"],
        [
            {
                "targetPath": (
                    f"/profiles/id={PERFIL}/classificationMilestones/id={cenario['marco']}/name"
                ),
                "operation": "REPLACE",
                "newValue": "Classificação final (renomeada por Retificação)",
            }
        ],
        suffix=f"marco-{SEED}",
    )
    _como_presidente(client)

    do_ato = client.get(_ato(cenario)).content.decode()
    de_agora = client.get(_ordenacao(cenario)).content.decode()

    assert "Classificação final" in do_ato
    assert "renomeada por Retificação" not in do_ato
    # A proposta calculada agora é a de agora: ela lê a norma vigente, e é ali que o nome novo vale.
    assert "renomeada por Retificação" in de_agora


def test_o_criterio_de_desempate_sai_pela_frase_publicada_e_nao_pelo_enum(
    client, seletor_ligado, cenario
):
    """FR-050/SC-010: a consulta nomeia o critério que separou — e "nomear" não é imprimir o enum.

    O enum e o `criterionId` continuam à vista, como detalhe técnico: é por eles que se confere o
    ato contra a base, e removê-los trocaria uma ilegibilidade por outra.
    """
    _como_presidente(client)

    desempate = _secao(
        client.get(_ato(cenario)).content.decode(), "Posições e valores de desempate"
    )

    assert "maior pontuação na Etapa Prova didática" in desempate
    assert "MAIOR_PONTUACAO_NA_ETAPA" in desempate
    assert CRITERIO in desempate
    # A mesma nota escrita do mesmo jeito na mesma tabela: `90`, e não `90` ao lado de `90.0000`.
    # O filtro não arredonda — tira os zeros que não informam e usa vírgula.
    assert "valor 90" in desempate
    assert "90.0000" not in desempate


def test_o_criterio_e_nomeado_pela_versao_que_o_ato_congelou(
    client, seletor_ligado, cenario, api_client
):
    """Mesmo princípio das modalidades: renomear a Etapa hoje não muda o que o ato
    diz ter comparado.
    """
    retify(
        api_client,
        cenario["edital"],
        [
            {
                "targetPath": f"/stages/id={ETAPA_DO_MARCO}/name",
                "operation": "REPLACE",
                "newValue": "Prova didática (renomeada por Retificação)",
            }
        ],
        suffix=f"etapa-{SEED}",
    )
    _como_presidente(client)

    desempate = _secao(
        client.get(_ato(cenario)).content.decode(), "Posições e valores de desempate"
    )

    assert "maior pontuação na Etapa Prova didática" in desempate
    assert "renomeada por Retificação" not in desempate


# ---------------------------------------------------------------------------
# E2E15-011 — o diff de obsolescência mostra o que mudou
# ---------------------------------------------------------------------------


def test_o_diff_traz_a_pontuacao_de_antes_e_a_de_agora(client, seletor_ligado, cenario, api_client):
    """1º → 1º não explica nada; 90 → 180 explica a divergência que `comparar()` apontou."""
    _dobrar_o_peso(api_client, cenario)
    _como_presidente(client)

    diff = _secao(client.get(_ordenacao(cenario)).content.decode(), "Mudanças posição a posição")
    celulas = [
        re.sub(r"<[^>]+>", "", celula).strip()
        for celula in re.findall(r"<td>(.*?)</td>", diff, re.DOTALL)
    ]

    assert "90" in celulas and "180" in celulas
    assert "70" in celulas and "140" in celulas


def test_sem_divergencia_de_regra_nao_ha_tabela_de_mudancas(client, seletor_ligado, cenario):
    """A tabela é consequência da obsolescência, e não decoração permanente da tela."""
    _como_presidente(client)

    corpo = client.get(_ordenacao(cenario)).content.decode()

    assert "Mudanças posição a posição" not in corpo


# ---------------------------------------------------------------------------
# E2E15-010 — o ato sucedido diz que foi sucedido
# ---------------------------------------------------------------------------


def test_o_ato_sucedido_declara_quando_e_por_qual_ato_foi_sucedido(
    client, seletor_ligado, cenario, api_client, gestor
):
    _dobrar_o_peso(api_client, cenario)
    sucessor = emitir(
        cenario,
        gestor,
        chave=f"emitir-sucessor-{SEED}",
        motivo="Retificação do peso da Etapa.",
    )
    _como_presidente(client)

    superado = client.get(_ato(cenario)).content.decode()

    assert "Este ato foi sucedido" in superado
    assert "Retificação do peso da Etapa." in superado
    assert _ato(cenario, sucessor) in superado
    assert sucessor.emitido_em.astimezone().strftime("%d/%m/%Y %H:%M") in superado


def test_os_valores_congelados_nao_mudam_quando_o_ato_e_sucedido(
    client, seletor_ligado, cenario, api_client, gestor
):
    """O aviso é leitura acrescentada; o snapshot continua sendo o que o ato registrou."""
    _como_presidente(client)
    antes = _secao(client.get(_ato(cenario)).content.decode(), "Posições e valores de desempate")
    _dobrar_o_peso(api_client, cenario)
    emitir(cenario, gestor, chave=f"emitir-sucessor-b-{SEED}", motivo="Retificação do peso.")

    depois = _secao(client.get(_ato(cenario)).content.decode(), "Posições e valores de desempate")

    assert antes == depois


def test_o_ato_vigente_nao_anuncia_sucessor_nenhum(client, seletor_ligado, cenario):
    _como_presidente(client)

    corpo = client.get(_ato(cenario)).content.decode()

    assert "Este ato foi sucedido" not in corpo


# ---------------------------------------------------------------------------
# E2E15-009 — datas em português, no formato que o resto da interface escreve
# ---------------------------------------------------------------------------


def test_as_datas_da_classificacao_saem_no_formato_da_instituicao(client, seletor_ligado, cenario):
    _como_presidente(client)
    emitido_em = cenario["ato"].emitido_em.astimezone().strftime("%d/%m/%Y %H:%M")

    do_ato = client.get(_ato(cenario)).content.decode()
    da_ordem = client.get(_ordenacao(cenario)).content.decode()

    assert emitido_em in do_ato
    assert emitido_em in da_ordem
    # Os meses abreviados do `en-us` que a auditoria leu na tela — "Sept. 5, 2026, 11:30 p.m.".
    for mes in (
        "Jan.",
        "Feb.",
        "March",
        "April",
        "May",
        "June",
        "July",
        "Aug.",
        "Sept.",
        "Oct.",
        "Nov.",
        "Dec.",
    ):
        assert mes not in do_ato
        assert mes not in da_ordem
