"""As conduções que mais de uma superfície diz — produzidas uma vez, e importadas por quem as diz.

**Mudou de casa na `045`**, e só por isso existe. A frase da Retificação nasceu em `views.py`, na
`037`; a Atenção passou a precisar dela (`FR-740`), e `supervisao.py` não pode importar `views.py`
— seria ciclo, porque a view importa a supervisão. Redigi-la de novo no painel seria a segunda
maneira de dizer a mesma coisa, que a `037` (`FR-543`) proíbe.
"""

from processo_seletivo.seguranca.application.authorization import base_de_permissao, frase_do_aviso

# A base de quem propõe Retificação, e a condução que ela produz (037, `FR-541`, `FR-543`).
#
# **A frase é produzida, e não redigida.** Imitar o texto numa tela nova derrotaria a guarda que a
# `033` deixou — existe uma maneira de dizer isto, e ela é pública exatamente para que não nasça
# uma segunda. A forma é a **cheia**, com a oração do ato (`FR-543a`), e ela nomeia a permissão e
# nunca uma pessoa (`FR-543b`).
#
# **Aviso, e não recusa** (`FR-543d`): é dita em telas onde ninguém tentou operação alguma — ao
# lado de "Conteúdo imutável", e ao lado da recusa do corte que fala de outra coisa.
BASE_DE_RETIFICAR = base_de_permissao("retificar")
CONDUCAO_DA_RETIFICACAO = frase_do_aviso(
    (BASE_DE_RETIFICAR,), acao="A Retificação", que="a proponha"
)

__all__ = ["BASE_DE_RETIFICAR", "CONDUCAO_DA_RETIFICACAO"]
