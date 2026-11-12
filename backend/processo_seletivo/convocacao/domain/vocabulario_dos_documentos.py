"""O nome do documento reenviado, numa fonte só (154, FR-6211 e FR-6212, D-004).

**O achado 23 do estudo da jornada final**: o mesmo fato — conferência pendente sobre um arquivo
novo, enviado depois da correção pedida — tinha três nomes na gestão (*"Complementado, aguardando
conferência"* no item, *"Reenviado, a conferir de novo"* na contagem, *"1 complementado"* no
cartão) e um quarto no portal. A comissão e o candidato não falavam da mesma coisa. O nome mora
aqui para que o portal, a gestão e o aviso de pendência leiam dele, e o teste de identidade
(SC-2004) compare uma constante, e não seis cópias de texto.

**O travessão é U+2014**, com espaço dos dois lados: um hífen ou um meia-risca passariam no olho.
O identificador do estado (`ITEM_COMPLEMENTADO`) não é texto de tela, e fica (R-007).
"""

_ESPERA = "aguardando nova conferência"

#: O rótulo do item: abre o cartão do portal e a linha da página de documentos (FR-6211).
REENVIADO = f"Reenviado — {_ESPERA}"


def reenviado_em_frase(*, plural=False):
    """O nome dentro de frase, em minúscula: *"reenviado — aguardando nova conferência"*."""
    return f"{'reenviados' if plural else 'reenviado'} — {_ESPERA}"


def reenviados(quantos):
    """A contagem, com singular e plural naturais e sem "(s)" na tela (D-004)."""
    return f"{quantos} {reenviado_em_frase(plural=quantos != 1)}"
