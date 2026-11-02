"""Desempate pela nota de uma Etapa que o marco não enumera (achado A11).

O achado é do estudo da configuração da classificação
(`doc/estudo-configuracao-classificacao-2026-11-01/diario-de-construcao.md`, A11), e nasceu da
leitura do código: `calcular_ordem` só busca os Resultados das Etapas que o marco enumera
(`etapa_id__in=enumeradas`), e `universo_classificavel.preparar` monta as pontuações de cada
participante a partir desses Resultados. Um critério `MAIOR_PONTUACAO_NA_ETAPA` que aponta outra
Etapa encontraria o valor vazio para todos — e não separaria ninguém, mesmo com as notas lançadas.

O seletor de alvos oferece qualquer Etapa classificatória, e a publicação aceita o critério. Este
teste percorre o caminho inteiro — publica, avalia as duas Etapas, consolida — e pergunta ao
cálculo oficial se a nota da Entrevista desfaz o empate que o edital manda desfazer por ela.

**Ele afirma o que o edital diz, e está marcado como falha esperada.** Não prende o defeito como
comportamento: prende a evidência dele. A marca é estrita, para que a correção — qualquer das duas
— seja notada.
"""

from decimal import Decimal

import pytest

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.comissoes.models import MembroComissao
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.comissao import alocar_em
from tests.fixtures.corte import ENTREVISTA, MARCO, montar_cenario_do_corte, rascunho, regra
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.mesa import concluir_como, distribuir_para

pytestmark = pytest.mark.django_db(transaction=True)

CRITERIO = "00000000-0000-4000-8000-000000001101"


def rascunho_com_desempate_pela_entrevista(cut=None):
    """O marco enumera só a Etapa pontuada, e desempata pela nota da Entrevista."""
    base, pontuada = rascunho(cut=cut)
    base["profiles"][0]["classificationMilestones"][0]["tiebreakers"] = [
        {
            "id": CRITERIO,
            "order": 1,
            "type": "MAIOR_PONTUACAO_NA_ETAPA",
            "parameters": {"stageId": ENTREVISTA},
            "whenMissing": "ULTIMO_NO_CRITERIO",
        }
    ]
    return base, pontuada


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "A11: o cálculo só lê os Resultados das Etapas enumeradas, e a nota da Entrevista chega "
        "vazia ao desempate. Confirmado em 01/11/2026: os dois empatados ficam ambos em 1º, com "
        "`separado_por` nulo. Corrigir é decisão do usuário — ler a nota no universo, ou recusar o "
        "critério na validação; quando vier, este teste passa a falhar e a marca sai."
    ),
)
def test_a_nota_de_etapa_nao_enumerada_desfaz_o_empate(
    gestor, api_client, manager_headers, process_payload
):
    edital, pontuada, inscricoes = montar_cenario_do_corte(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        # Sem Etapa governada: a Entrevista recebe todos os habilitados, e o teste não depende de
        # emitir o corte para que os empatados cheguem a ela.
        cut=regra(governedStage="NONE"),
        prefixo="a11",
        pontuacoes=("80.0000", "80.0000", "70.0000"),
        draft_factory=rascunho_com_desempate_pela_entrevista,
        emitir_a_ordem=False,
    )
    primeiro, segundo = inscricoes[0], inscricoes[1]

    joao = MembroComissao.objects.get(processo=edital.processo, identity_subject="joao")
    alocar_em(gestor, edital.processo, joao, edital, ENTREVISTA)
    entrevista = {
        "edital": edital,
        "processo": edital.processo,
        "membros": {"joao": joao},
        "etapa": ENTREVISTA,
    }
    distribuir_para(entrevista, gestor, ["joao"], [primeiro, segundo], chave="a11-entrevista")
    # A ordem de protocolo põe `primeiro` à frente; a Entrevista o põe atrás. Se o critério
    # funcionar, a ordem se inverte — e a inversão não pode vir de desempate oculto por protocolo.
    concluir_como(entrevista, "joao", primeiro, pontuacao="70.0000")
    concluir_como(entrevista, "joao", segundo, pontuacao="90.0000")
    consolidar(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=ENTREVISTA,
        inscricao_ids=[primeiro.id, segundo.id],
        idempotency_key="a11-consolidar-entrevista",
        correlation_id="teste-a11",
    )

    # A guarda é do preparo, e não do achado: sem os dois Resultados vigentes na Entrevista, a falha
    # abaixo diria nada sobre o cálculo. `pytest.fail` não é `AssertionError`, e o `xfail` não a
    # engole.
    notas = dict(
        ResultadoEtapa.vigentes.filter(edital=edital, etapa_id=ENTREVISTA).values_list(
            "inscricao_id", "pontuacao"
        )
    )
    if notas.get(primeiro.id) != Decimal("70") or notas.get(segundo.id) != Decimal("90"):
        pytest.fail(f"o preparo não produziu as notas da Entrevista: {notas}")

    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    posicao = {str(item["inscricao_id"]): item["posicao"] for item in proposta["posicoes"]}

    assert posicao[str(segundo.id)] == 1
    assert posicao[str(primeiro.id)] == 2
