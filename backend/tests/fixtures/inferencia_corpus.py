"""Ajudantes dos testes do piloto que leem as fontes que o modelo recebeu (071).

A porta falsa recebe as mensagens; estes ajudantes acham nelas o identificador de uma fonte pelo
lugar e pelo rótulo, como o modelo acharia — e é com esse identificador que a saída fabricada cita.
"""

import json


def fontes_recebidas(mensagens):
    """As fontes da segunda mensagem, uma por linha em JSON (contracts/saida-do-modelo.md §1)."""
    return [json.loads(linha) for linha in mensagens[1]["content"].split("\n")[1:]]


def fonte(mensagens, *, lugar, rotulo=None, natureza=None):
    for item in fontes_recebidas(mensagens):
        if lugar not in item["lugar"]:
            continue
        if rotulo is not None and item.get("rotulo") != rotulo:
            continue
        if natureza is not None and item["natureza"] != natureza:
            continue
        return item
    raise AssertionError(f"nenhuma fonte com lugar {lugar!r} e rótulo {rotulo!r}")
