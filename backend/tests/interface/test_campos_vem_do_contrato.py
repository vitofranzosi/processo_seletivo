"""A tela de Retificação e o contrato de mutabilidade, conferidos nos dois sentidos (026).

FR-298 exige que a declaração de natureza viva em local único e seja lida por quem monta a tela;
FR-304 exige que todo campo retificável seja alcançável **pelo canal do ator**, e não só pela API.

A conferência tem dois donos, e a razão é de método:

- *nada se oferece sem decisão* vale desde já, e é conferido na **carga** de
  `interface/retificacao` — quem acrescentar um campo à apresentação descobre no `import`;
- *todo retificável é oferecido* é o que este arquivo guarda, com o conjunto dos que ainda não têm
  tela declarado nominalmente.

**O conjunto encolheu até esvaziar, e a asserção mudou.** São 68 campos retificáveis; a tela
oferecia 49 quando o contrato nasceu, os quatro canários acrescentaram 15, e a fase 10 fechou os
quatro que sobravam. `AINDA_SEM_TELA` existiu para que cada fase fechasse **verde** — afirmar a
FR-304 inteira no primeiro commit deixaria a suíte vermelha por seis fases, e suíte que fica
vermelha deixa de acusar regressão, que é o oposto do que esta feature entrega.

Vazio, ele deixa de ser andaime e passa a ser guarda: classificar um campo como retificável e não
lhe dar tela derruba a suíte a partir daqui, **sem exceção**.
"""

from processo_seletivo.editais.domain.mutabilidade import CONTRATO, Natureza
from processo_seletivo.interface import retificacao

#: Os campos que o contrato classifica como retificáveis e a tela ainda não oferece.
#:
#: **Vazio, e é o ponto.** Ele nasceu com 19 e encolheu a cada fase; a última o esvaziou. Voltar a
#: pôr linha aqui é admitir que um campo classificado deixou de ter caminho pela tela — e isso não
#: é ajuste de implementação, é a FR-304 deixando de valer. Quem o fizer precisa dizer por quê.
AINDA_SEM_TELA: set[tuple[str, str]] = set()


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


def test_todo_campo_retificavel_tem_tela():
    """FR-304, **sem exceção**.

    Falhar aqui significa que um campo classificado como retificável perdeu — ou nunca teve — o
    caminho pela tela. É a regressão que a FR-304 proíbe, e a partir daqui ela derruba a suíte.
    """
    assert AINDA_SEM_TELA == set(), (
        "o conjunto dos pendentes voltou a ter linha: a FR-304 vale sem exceção desde a fase 10"
    )
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


def test_a_conta_fecha_com_a_matriz():
    """68 retificáveis, e 68 com tela. O número está na matriz aprovada e no contrato.

    Escrito como asserção porque é a promessa que a feature faz: não "quase todos", não "os que
    importam" — todos.
    """
    assert len(_retificaveis()) == 68
    assert _retificaveis() <= _oferecidos()
