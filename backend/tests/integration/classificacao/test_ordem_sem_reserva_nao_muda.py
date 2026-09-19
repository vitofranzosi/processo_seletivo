"""A não-regressão da ampla concorrência (034, FR-493, SC-171).

**É a rede que impede a feature de alterar Edital que ela não deveria alcançar.** O mesmo cálculo
passou a receber um parâmetro, e um padrão errado mudaria a ordem de **todo** Edital do acervo — sem
que teste algum de recorte reservado acusasse, porque nenhum deles olha para o Perfil sem cota.

**A conferência é por comparação da ordem e da proveniência, e não por contagem de linhas**
(`SC-171`). Contar linhas passaria por uma implementação que trocasse quem está em cada posição.

A comparação com "antes da feature" é feita **dentro do mesmo Edital**, que é onde ela é mais forte
e onde ela é possível: a ordem da ampla concorrência calculada antes de existir autodeclaração
alguma, e depois de as autodeclarações entrarem. Se declarar cota movesse alguém na ampla, as duas
divergiriam — e é exatamente essa a alteração que a `FR-493` proíbe.

*Comparar dois Editais foi a primeira tentativa, e ela não se sustenta neste repositório: o rascunho
de teste carrega identidades fixas, e um segundo Edital com as mesmas identidades é recusado com
`identifier_belongs_to_another_edital` — recusa correta, sobre um cenário que não é o que se quer
medir. A comparação intra-Edital dispensa o segundo Edital e compara **as mesmas pessoas**, o que a
entre-Editais não conseguia fazer.*
"""

import pytest

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.models import AtoDeOrdenacao, PosicaoNaOrdem
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.recortes import montar_cenario_7_1_2

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

PONTUACOES = ("95.0000", "90.0000", "85.0000", "80.0000", "75.0000")


def sem_reserva(gestor, api_client, manager_headers, process_payload, *, prefixo):
    return montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        pontuacoes=PONTUACOES,
        sem_reserva=True,
    )


def com_reserva(gestor, api_client, manager_headers, process_payload, *, prefixo):
    return montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        pontuacoes=PONTUACOES,
    )


def retrato(proposta):
    """A ordem **e** a proveniência: quem, em que posição, com que nota, separado por qual critério.

    É o que `SC-171` chama de "comparação da ordem e da proveniência", e é por isso que a identidade
    da inscrição **entra**: contar linhas passaria por uma implementação que trocasse quem está em
    cada posição.

    `modalidade_id` fica de fora de propósito. Ela é dado declarado pelo candidato e muda quando a
    autodeclaração é gravada — o que não é mudança de ordem nem de proveniência, e prendê-la aqui
    faria este teste reprovar a própria premissa do cenário.
    """
    return [
        {
            "inscricao_id": item["inscricao_id"],
            "posicao": item["posicao"],
            "pontuacao": item["pontuacao"],
            "consequencia": item["consequencia"],
            "motivo": item["motivo"],
            "empate_residual": item["empate_residual"],
            "separado_por": (item.get("separado_por") or {}).get("id"),
        }
        for item in proposta["posicoes"] + proposta["sem_posicao"]
    ]


def test_declarar_cota_nao_move_ninguem_na_ampla(
    gestor, api_client, manager_headers, process_payload
):
    """`FR-493` e `SC-171`: a ampla é o universo inteiro, antes e depois da autodeclaração.

    O cenário nasce sem autodeclaração alguma; as três entram depois, e a ordem da ampla tem de
    sair **idêntica** — mesmas pessoas, mesmas posições, mesma proveniência.
    """
    from tests.fixtures.recortes import MODALIDADE_PCD, MODALIDADE_PPI, declarar

    edital, _, inscricoes = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="sem-reserva-034-cota",
        pontuacoes=PONTUACOES,
        autodeclarar=False,
    )
    antes = retrato(calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO))

    declarar(inscricoes[1], MODALIDADE_PCD)
    declarar(inscricoes[2], MODALIDADE_PPI)
    declarar(inscricoes[4], MODALIDADE_PPI)
    depois = retrato(calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO))

    assert depois == antes


def test_o_padrao_do_calculo_e_a_ampla_e_nada_mais(
    gestor, api_client, manager_headers, process_payload
):
    """Quem chama sem dizer o recorte recebe o que recebia: é o que torna a mudança compatível.

    Passar `lista_id=None` explicitamente e **não** passar nada têm de produzir a mesma coisa —
    senão a feature teria um padrão diferente do que declarou ter.
    """
    edital, _, _ = com_reserva(
        gestor, api_client, manager_headers, process_payload, prefixo="sem-reserva-034-padrao"
    )

    omitido = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    explicito = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None)

    assert retrato(omitido) == retrato(explicito)
    assert omitido["universo"] == explicito["universo"]


def test_o_ato_do_perfil_sem_reserva_continua_nascendo_sem_lista(
    gestor, api_client, manager_headers, process_payload
):
    """O recorte sem lista é a ampla, e é a mesma grafia de sempre (`FR-503`).

    O cenário já emite a ordem ao montar-se: o que se confere aqui é a coluna com que ela nasceu.
    """
    edital, _, inscricoes = sem_reserva(
        gestor, api_client, manager_headers, process_payload, prefixo="sem-reserva-034-ato"
    )

    atos = list(AtoDeOrdenacao.objects.filter(edital=edital, marco_id=MARCO))

    assert len(atos) == 1, "um Perfil sem reserva tem um recorte, e portanto um ato"
    assert atos[0].lista_id is None
    assert PosicaoNaOrdem.objects.filter(ato=atos[0]).count() == len(inscricoes)


def test_a_proveniencia_gravada_no_ato_da_ampla_nao_ganhou_campo_novo(
    gestor, api_client, manager_headers, process_payload
):
    """`SC-173` visto de dentro: o resumo do universo é o de antes, sem chave acrescentada.

    O recorte mora na coluna `lista_id` do ato, e **não** no resumo do universo. Acrescentá-lo lá
    faria a comparação de obsolescência de todo ato do acervo confrontar um universo gravado sem a
    chave com um calculado com ela — e o acervo inteiro apareceria obsoleto de uma vez.
    """
    edital, _, _ = sem_reserva(
        gestor, api_client, manager_headers, process_payload, prefixo="sem-reserva-034-universo"
    )

    ato = AtoDeOrdenacao.objects.get(edital=edital, marco_id=MARCO)

    assert set(ato.universo) == {
        "processoId",
        "editalId",
        "profileId",
        "milestoneId",
        "versionId",
        "participants",
        "stageResults",
    }
