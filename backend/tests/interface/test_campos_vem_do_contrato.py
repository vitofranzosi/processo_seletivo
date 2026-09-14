"""A tela de Retificação e o contrato de mutabilidade, conferidos nos dois sentidos (026).

FR-298 exige que a declaração de natureza viva em local único e seja lida por quem monta a tela;
FR-304 exige que todo campo retificável seja alcançável **pelo canal do ator**, e não só pela API.

A conferência tem dois donos, e a razão é de método:

- *nada se oferece sem decisão* vale desde já, e é conferido na **carga** de
  `interface/retificacao` — quem acrescentar um campo à apresentação descobre no `import`;
- *todo retificável é oferecido* é o que este arquivo guarda, com o conjunto dos que ainda não têm
  tela declarado nominalmente.

**Por que um conjunto que encolhe, e não a asserção inteira de uma vez.** São 68 campos
retificáveis e a tela oferecia 49 quando o contrato nasceu. Afirmar a FR-304 inteira no primeiro
commit deixaria a suíte vermelha por seis fases — e suíte que fica vermelha deixa de acusar
regressão, que é o oposto do que esta feature entrega. Cada jornada remove os seus do conjunto, e a
última tarefa o esvazia e troca a asserção.
"""

import pytest

from processo_seletivo.editais.domain.mutabilidade import CONTRATO, Natureza
from processo_seletivo.interface import retificacao

#: Os campos que o contrato classifica como retificáveis e a tela **ainda** não oferece.
#:
#: O conjunto só encolhe. Acrescentar linha aqui é admitir que um campo classificado deixou de ter
#: caminho pela tela — e isso não é ajuste de implementação: é a FR-304 deixando de valer.
AINDA_SEM_TELA = {
    # Canário 4 — o método do sorteio, dez campos (US4).
    ("classificationMilestones", "drawMethod/algorithm"),
    ("classificationMilestones", "drawMethod/source"),
    ("classificationMilestones", "drawMethod/occurrence"),
    ("classificationMilestones", "drawMethod/occurrenceAt"),
    ("classificationMilestones", "drawMethod/derivation"),
    ("classificationMilestones", "drawMethod/normalization/rule"),
    ("classificationMilestones", "drawMethod/normalization/text"),
    ("classificationMilestones", "drawMethod/substitutionRule/rule"),
    ("classificationMilestones", "drawMethod/substitutionRule/text"),
    ("classificationMilestones", "drawMethod/qualifyingStageId"),
    # Os residuais: nenhum é canário, e todos são obrigatórios porque o contrato os classificou.
    ("profiles", "description"),
    ("competitionModalities", "normativeRule/effectiveFrom"),
    ("classificationMilestones", "rounding/scale"),
    ("classificationMilestones", "rounding/mode"),
}


def _oferecidos():
    return {
        (colecao, caminho)
        for nome, colecao in retificacao.COLECAO_DA_LISTA.items()
        for caminho, *_ in getattr(retificacao, nome)
    }


def _retificaveis():
    return {
        chave for chave, decisao in CONTRATO.items() if decisao.natureza is Natureza.RETIFICAVEL
    }


def test_todo_campo_oferecido_pela_tela_esta_no_contrato():
    """A direção que já vale sem exceção. Repete o que a carga do módulo confere, por escrito."""
    fora = sorted(f"({colecao}, {caminho})" for colecao, caminho in _oferecidos() - set(CONTRATO))
    assert fora == [], "a tela oferece campo sem entrada no contrato:\n  " + "\n  ".join(fora)


def test_nenhum_campo_oferecido_esta_classificado_como_nao_retificavel():
    """Oferecer o que o contrato exclui é pior do que não oferecer o que ele admite.

    O segundo é lacuna; o primeiro é a tela contradizendo a norma que ela mesma deveria aplicar.
    """
    indevidos = sorted(
        f"({colecao}, {caminho}) — {CONTRATO[(colecao, caminho)].natureza}"
        for colecao, caminho in _oferecidos()
        if (colecao, caminho) in CONTRATO
        and CONTRATO[(colecao, caminho)].natureza is not Natureza.RETIFICAVEL
    )
    assert indevidos == [], "\n  ".join(indevidos)


def test_todo_campo_retificavel_fora_do_conjunto_declarado_tem_tela():
    """FR-304, com o alcance que o conjunto declara.

    Falhar aqui significa que um campo classificado como retificável perdeu — ou nunca teve — o
    caminho pela tela, **e não foi declarado como pendente**. É a regressão que a FR-304 proíbe.
    """
    faltando = sorted(
        f"({colecao}, {caminho})"
        for colecao, caminho in _retificaveis() - _oferecidos() - AINDA_SEM_TELA
    )
    assert faltando == [], (
        "campo classificado como retificável e sem caminho pela tela de Retificação — a FR-304 "
        "exige o canal do ator, e não só a API:\n  " + "\n  ".join(faltando)
    )


def test_o_conjunto_dos_pendentes_nao_lista_campo_que_ja_tem_tela():
    """O conjunto só encolhe, e não pode mentir sobre o que já foi feito."""
    ja_feitos = sorted(
        f"({colecao}, {caminho})" for colecao, caminho in AINDA_SEM_TELA & _oferecidos()
    )
    assert ja_feitos == [], (
        "estes campos já têm tela e continuam declarados como pendentes — remova-os de "
        "`AINDA_SEM_TELA`:\n  " + "\n  ".join(ja_feitos)
    )


def test_o_conjunto_dos_pendentes_so_cita_campo_retificavel():
    """Campo não retificável não fica 'pendente': ele fica de fora, com razão escrita."""
    assert AINDA_SEM_TELA <= _retificaveis()


@pytest.mark.parametrize("colecao", sorted({colecao for colecao, _ in AINDA_SEM_TELA}))
def test_o_tamanho_do_vao_por_colecao(colecao):
    """Torna o vão legível por coleção, em vez de um número só.

    Não é redundância com o teste acima: quando uma jornada fecha, é aqui que se vê **qual**
    coleção deixou de ter pendência.
    """
    pendentes = {caminho for outra, caminho in AINDA_SEM_TELA if outra == colecao}
    assert pendentes, f"coleção sem pendência declarada continua no conjunto: {colecao}"
