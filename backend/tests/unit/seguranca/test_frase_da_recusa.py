"""O mecanismo único de dizer "a quem pedir", e as duas situações de fala (033, 037).

**Por que este arquivo nasce na `037` e não na `033`.** A varredura antes da implementação não
encontrou **um só** caso citando `frase_da_recusa` ou a frase que ela produz: o mecanismo que a
`FR-486` criou para impedir uma segunda formulação estava, ele próprio, sem rede. Ampliá-lo seria
mexer em código sem teste, e por isso a rede vem antes da ampliação.

**O que se prende aqui é o texto**, e não o comportamento de autorização. Quem decide o que pode é
`require_authorization_base`, e os testes dele estão noutro lugar — a `FR-553` promete que nenhuma
decisão de autorização muda nesta feature, e nada neste arquivo a exercita.
"""

from processo_seletivo.seguranca.application.authorization import (
    Base,
    base_de_permissao,
    frase_da_recusa,
    frase_do_aviso,
)

PUBLICAR = base_de_permissao("publicar")
RETIFICAR = base_de_permissao("retificar")
PRESIDENCIA = Base("a presidência deste Processo", "a quem preside este Processo")


# --- a recusa, que é a forma que já existia ------------------------------------------------------


def test_a_recusa_de_uma_base_continua_palavra_por_palavra():
    """A ampliação da `037` não pode ter mudado o que as portas já dizem (`FR-553`).

    É a asserção mais importante do arquivo: `frase_da_recusa` é chamada de
    `require_authorization_base`, que responde 403 em toda a gestão, e qualquer alteração aqui
    apareceria em telas que esta feature não toca.
    """
    assert frase_da_recusa((PUBLICAR,)) == (
        "Esta operação depende da permissão de publicar. Peça a alguém com a permissão de publicar."
    )


def test_duas_bases_dizem_que_cada_uma_basta_sozinha():
    """`FR-489`: o conjunto é de quem chama, e a frase precisa dizer que a alternativa existe.

    Sem o "cada uma basta sozinha", quem lê entende que precisa das duas — e vai pedir o que não
    resolve, ou desiste de uma alternativa que teria bastado.
    """
    assert frase_da_recusa((PUBLICAR, PRESIDENCIA)) == (
        "Esta operação depende da permissão de publicar ou da presidência deste Processo "
        "— cada uma basta sozinha. "
        "Peça a alguém com a permissão de publicar ou a quem preside este Processo."
    )


def test_a_contracao_que_o_portugues_exige():
    """Os nomes nascem com artigo, porque é assim que eles entram no "peça a alguém com…".

    Concatenados atrás de "depende de", produziriam *"depende de a permissão"*, que ninguém
    escreve. A contração é da frase, e não do nome — é o que faz o mesmo `Base` servir às duas
    posições.
    """
    frase = frase_da_recusa((PUBLICAR,))

    assert "depende da permissão de publicar" in frase
    assert "depende de a permissão" not in frase


def test_uma_base_sem_artigo_nao_ganha_contracao():
    """A contraprova da anterior: nem todo nome começa com artigo, e forçar "da" inventaria um.

    Sem este caso, `_com_de` poderia passar a contrair sempre e nada acusaria — as bases que o
    produto declara hoje começam todas com "a".
    """
    assert frase_da_recusa((Base("vínculo com esta comissão", "a quem tem vínculo"),)) == (
        "Esta operação depende de vínculo com esta comissão. Peça a quem tem vínculo."
    )


# --- 037 · a forma cheia, que o mecanismo não produzia --------------------------------------------


def test_a_recusa_aceita_a_oracao_do_ato():
    """`FR-543a` e `FR-543c`: *"peça a alguém com a permissão de X **que Y**"*.

    Das quatro ocorrências renderizadas que a `037` mediu, uma largava a oração final e dizia só a
    quem pedir, sem dizer o quê. O padrão passa a ser a cheia — e o mecanismo tem de produzi-la,
    senão a `FR-543` (não redija à mão) e a `FR-543a` (use a forma cheia) se contradizem.
    """
    assert frase_da_recusa((PUBLICAR,), que="conclua o ato") == (
        "Esta operação depende da permissão de publicar. "
        "Peça a alguém com a permissão de publicar que conclua o ato."
    )


# --- 037 · o aviso, que é a situação de fala nova -------------------------------------------------


def test_o_aviso_nomeia_a_acao_em_vez_de_pressupor_uma_operacao():
    """`FR-543d`: dizer *"esta operação"* onde ninguém tentou nada nomeia um ato que não houve.

    O aviso é dito ao lado de *"Conteúdo imutável"* e ao lado de uma recusa do domínio que fala de
    outra coisa. Quem avisa **nomeia a ação** — que é metade do que a `FR-541` cobra; a outra
    metade é a permissão, e ela sai das bases.
    """
    assert frase_do_aviso((RETIFICAR,), acao="A Retificação", que="a proponha") == (
        "A Retificação depende da permissão de retificar. "
        "Peça a alguém com a permissão de retificar que a proponha."
    )


def test_o_aviso_nunca_abre_com_esta_operacao():
    """A contraprova da anterior, dita como proibição — é ela que uma refatoração desatenta quebra.

    Reunir as duas frases numa só, com a de recusa como padrão, é a simplificação óbvia: o texto
    fica quase igual. Este caso é o que a acusa.
    """
    assert not frase_do_aviso((RETIFICAR,), acao="A Retificação", que="a proponha").startswith(
        "Esta operação"
    )


def test_as_duas_formas_nomeiam_o_destinatario_do_mesmo_jeito():
    """`FR-543` e `FR-543d`: são duas frases, e **uma** formulação.

    O que as separa é o sujeito da primeira oração. Se a construção do *a quem pedir* divergisse
    entre elas, o produto teria duas gramáticas para o mesmo ato de pedir — que é exatamente o que
    a `033` deixou um mecanismo público para não acontecer.
    """
    a_quem = "Peça a alguém com a permissão de retificar que a proponha."

    assert frase_da_recusa((RETIFICAR,), que="a proponha").endswith(a_quem)
    assert frase_do_aviso((RETIFICAR,), acao="A Retificação", que="a proponha").endswith(a_quem)


def test_o_aviso_de_duas_bases_tambem_diz_que_cada_uma_basta():
    """A alternativa não se perde na situação de fala nova: ela é do `_depende`, compartilhado."""
    frase = frase_do_aviso((PUBLICAR, PRESIDENCIA), acao="A divulgação", que="a conclua")

    assert frase.startswith("A divulgação depende da permissão de publicar ou da presidência")
    assert "cada uma basta sozinha" in frase


def test_nenhuma_das_duas_nomeia_pessoa():
    """`FR-543b`: a permissão, nunca alguém. Não há fila, designação nem nome próprio."""
    for frase in (
        frase_da_recusa((RETIFICAR,), que="a proponha"),
        frase_do_aviso((RETIFICAR,), acao="A Retificação", que="a proponha"),
    ):
        assert "a alguém com a permissão de" in frase or "a quem " in frase
