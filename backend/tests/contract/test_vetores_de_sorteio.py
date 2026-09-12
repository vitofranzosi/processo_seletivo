"""Os vetores normativos, exercitados em Python (FR-027, FR-028).

**Duas formas, duas coisas provadas.** O vetor de *chave* dá as entradas e cobra bytes canônicos,
resumo e ordem — exercita os §§ 2 a 4 do contrato. O de *ordenação* dá as chaves já iguais e cobra
só a ordem: é a única forma honesta de provar o desempate do § 4.2, porque entrada válida do
sistema nenhuma produz duas chaves iguais e colisão de SHA-256 ninguém constrói (R-004).

O mesmo diretório é lido por `tests/javascript/sorteio.test.js`. Um vetor que passe aqui e falhe lá
é o que a SC-002 existe para detectar.
"""

import json
import pathlib

import pytest

from processo_seletivo.sorteios.domain import chave as K

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "sorteio"
OBRIGATORIOS = {
    "tres-participantes",
    "acentos-e-nfc",
    "um-participante",
    "mesma-semente-recortes-distintos",
    "desempate-por-numero-publico",
}


def _vetores():
    return sorted(FIXTURES.glob("*.json"))


def _carregar(caminho):
    return json.loads(caminho.read_text(encoding="utf-8"))


def test_os_cinco_vetores_obrigatorios_existem():
    assert {v.stem for v in _vetores()} >= OBRIGATORIOS


def _conferir_bloco_de_chave(bloco):
    entrada = bloco["input"]
    for numero in entrada["participants"]:
        produzidos = K.bytes_canonicos(
            relation_hash=entrada["relationHash"],
            draw_scope_id=entrada["drawScopeId"],
            seed=entrada["seed"],
            public_number=numero,
        )
        assert produzidos.decode("utf-8") == bloco["canonicalBytes"][str(numero)]
        assert (
            K.chave(
                relation_hash=entrada["relationHash"],
                draw_scope_id=entrada["drawScopeId"],
                seed=entrada["seed"],
                public_number=numero,
            )
            == bloco["keys"][str(numero)]
        )
    assert (
        K.ordem(
            relation_hash=entrada["relationHash"],
            draw_scope_id=entrada["drawScopeId"],
            seed=entrada["seed"],
            public_numbers=entrada["participants"],
        )
        == bloco["expectedOrder"]
    )


@pytest.mark.parametrize("caminho", _vetores(), ids=lambda c: c.stem)
def test_vetor(caminho):
    vetor = _carregar(caminho)
    if "ordering" in vetor:
        # Vetor do § 4: as chaves vêm prontas, e o que se cobra é só a ordenação.
        assert K.ordenar(vetor["ordering"]["keys"]) == vetor["expectedOrder"]
        return
    _conferir_bloco_de_chave(vetor)
    if "contrast" in vetor:
        _conferir_bloco_de_chave(vetor["contrast"])
        assert vetor["expectedOrder"] != vetor["contrast"]["expectedOrder"]


def test_o_desempate_e_por_numero_publico_crescente():
    """A propriedade nomeada, e não só o vetor: chaves iguais saem em ordem de número."""
    vetor = _carregar(FIXTURES / "desempate-por-numero-publico.json")
    chaves = vetor["ordering"]["keys"]
    empatados = sorted(int(n) for n, v in chaves.items() if list(chaves.values()).count(v) > 1)
    ordem = K.ordenar(chaves)
    assert [n for n in ordem if n in empatados] == empatados


def test_a_normalizacao_nfc_e_aplicada():
    """NFD e NFC da mesma semente produzem a mesma chave — a regra do § 2.5 está implementada."""
    vetor = _carregar(FIXTURES / "acentos-e-nfc.json")
    entrada = vetor["input"]
    for numero in entrada["participants"]:
        assert (
            K.chave(
                relation_hash=entrada["relationHash"],
                draw_scope_id=entrada["drawScopeId"],
                seed=vetor["seedNFC"],
                public_number=numero,
            )
            == vetor["keys"][str(numero)]
        )
