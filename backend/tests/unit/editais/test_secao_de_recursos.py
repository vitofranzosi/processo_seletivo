"""O texto padrão da seção "Dos Recursos" não pode contradizer o que o marco declara (FR-113).

A caminhada da T125 pôs as duas frases na mesma página do documento publicado:

```text
marco FINAL   "Recurso: Não caberá recurso contra o resultado deste marco."
seção 9       "Caberá recurso contra os resultados divulgados, nos prazos do Cronograma…"
```

Um Edital que se contradiz não é norma legível: quem lê a seção 9 acredita numa coisa, e quem lê o
marco acredita no oposto — e as duas são o mesmo ato publicado. O texto da seção é **editável**, e o
elaborador pode reescrevê-lo; o que não pode é o padrão do sistema afirmar, por conta própria, o que
o marco talvez negue.

A saída foi o padrão **remeter** à declaração de cada marco, em vez de afirmar por todos. Desde a
`054` não há padrão nenhum (FR-983): a seção nasce vazia, e o sistema deixa de afirmar qualquer
coisa sobre recurso por conta própria — que é a garantia desta regra, levada até o fim.
"""

from processo_seletivo.editais.domain.secoes import POR_CHAVE


def test_o_sistema_nao_afirma_nada_sobre_recurso_por_conta_propria():
    """Sem redação padrão, nenhuma frase do sistema pode contradizer o marco."""
    assert not hasattr(POR_CHAVE["recursos"], "default_text")


def test_o_texto_continua_editavel_pelo_elaborador():
    """Remeter não é engessar: a seção segue textual, e o Edital pode dizer o que precisar."""
    assert POR_CHAVE["recursos"].gerada is False
