"""Nada do candidato é guardado no navegador (FR-042).

**Por que a verificação é do fonte, e não de comportamento.** A propriedade é negativa — "nunca
escreve" —, e um teste de comportamento só prova que não escreveu nos caminhos que ele percorreu.
Ler o fonte prova o que a promessa diz.

O precedente a não imitar está do outro lado: `rascunho.js` guarda o preenchimento do elaborador
em `localStorage` e caduca em 24 h justamente porque a máquina de um órgão público é compartilhada.
Com CPF e documentos, nenhum prazo compensa o risco.
"""

from pathlib import Path

import pytest

PORTAL = Path(__file__).resolve().parents[1] / "processo_seletivo" / "portal"
ARMAZENAMENTOS = ("localStorage", "sessionStorage", "indexedDB", "document.cookie")


def fontes_do_portal():
    return sorted(
        [*(PORTAL / "static").rglob("*.js"), *(PORTAL / "templates").rglob("*.html")]
    )


@pytest.mark.parametrize("arquivo", fontes_do_portal(), ids=lambda p: p.name)
def test_o_canal_do_candidato_nao_escreve_no_navegador(arquivo):
    corpo = arquivo.read_text()

    encontrados = [nome for nome in ARMAZENAMENTOS if nome in corpo]

    assert not encontrados, (
        f"{arquivo.name} usa {', '.join(encontrados)}; a tela do candidato carrega CPF e "
        "documentos, e o que fica guardado no navegador é o que vaza numa máquina compartilhada"
    )


def test_a_verificacao_cobre_algum_arquivo():
    """Sem isto, renomear a pasta transformaria a garantia em silêncio aprovado."""
    assert len(fontes_do_portal()) >= 5
