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

A saída é o padrão **remeter** à declaração de cada marco, em vez de afirmar por todos. A frase
continua verdadeira nos três estados: declarada, negada e não declarada.
"""

from processo_seletivo.editais.domain.secoes import POR_CHAVE


def test_o_padrao_remete_ao_marco_em_vez_de_afirmar_por_todos():
    texto = POR_CHAVE["recursos"].default_text

    assert "Caberá recurso contra os resultados divulgados, nos prazos do Cronograma" not in texto
    assert "marco" in texto.lower(), (
        "o padrão precisa remeter ao que cada marco classificatório declara"
    )


def test_o_texto_continua_editavel_pelo_elaborador():
    """Remeter não é engessar: a seção segue textual, e o Edital pode dizer o que precisar."""
    assert POR_CHAVE["recursos"].gerada is False
