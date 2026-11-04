"""Nenhuma tela dos documentos da convocação afirma vínculo, encaminhamento ou autenticidade (115).

Três fronteiras, cada uma de uma decisão:

- **D-005 e FR-3610** — o aceite é *"apto para formalização"*, e nunca matrícula efetivada, bolsa
  concedida, vínculo ou contratação: isso é fato do sistema ou setor do vínculo, e não do GPS.
  *"Encaminhado"* só com registro de entrega, que esta feature não cria.
- **FR-3589** — *"conforme"* quer dizer conforme ao exigido pelo Edital. O arquivo é cópia simples
  enviada pelo interessado, e a tela não diz autêntico nem original.
- **D-001** — a capacidade é transversal: a tela não diz matrícula a quem vai se vincular a um
  programa de bolsas.

**Por que não a varredura da `019`.** Lá, *"recebido em"* é proibido porque o sistema não sabe
quando a **mensagem** chegou. Aqui, o sistema recebeu o **arquivo**, e a frase *"Recebido em"* é a
que a FR-3612 escreve. As duas regras são verdadeiras, cada uma sobre o que a sua tela afirma.

**A lista é literal**, como nas outras varreduras: tela nova escaparia dela em silêncio.
"""

import re
from pathlib import Path

import pytest

from tests.test_vocabulario_da_convocacao import visivel

RAIZ = Path(__file__).resolve().parents[1] / "processo_seletivo"
TEMPLATES = RAIZ / "interface/templates/interface"
PORTAL = RAIZ / "portal/templates/portal"

DA_115 = [
    TEMPLATES / "convocacao_documentos.html",
    TEMPLATES / "convocacao.html",
    TEMPLATES / "alocacoes.html",
    PORTAL / "_documentos_da_convocacao.html",
    PORTAL / "convocacao.html",
]

PROIBIDOS = {
    r"encaminhad[oa]": "encaminhado só com registro de entrega, que esta feature não cria (D-005)",
    r"matriculad[oa]": "o aceite é apto para formalização, e não matrícula (FR-3610)",
    r"matr[íi]cula efetivada": "idem — a efetivação é do sistema acadêmico",
    r"bolsa concedida": "a concessão é da agência, e não do GPS (FR-3610)",
    r"vinculad[oa]": "o vínculo é do setor competente (FR-3610)",
    r"contratad[oa]": "idem",
    r"autentic": "conforme é conforme ao exigido, e o arquivo é cópia simples (FR-3589)",
    r"documento original": "idem",
    r"documentos de matr[íi]cula": "a lista serve a qualquer vínculo, e não só à matrícula (D-001)",
}


@pytest.mark.parametrize("caminho", DA_115, ids=lambda item: f"{item.parent.name}/{item.name}")
def test_nenhuma_tela_dos_documentos_afirma_vinculo_nem_autenticidade(caminho):
    corpo = visivel(caminho).lower()
    achados = [
        f"{termo!r} — {porque}" for termo, porque in PROIBIDOS.items() if re.search(termo, corpo)
    ]
    assert achados == [], f"{caminho.name}: " + "; ".join(achados)


def test_a_conducao_diz_apto_para_formalizacao():
    """A ausência não basta: a frase certa precisa estar lá (D-005)."""
    assert "apto para formalização" in visivel(TEMPLATES / "convocacao.html").lower()


def test_a_conferencia_diz_conforme_ao_exigido():
    assert (
        "conforme ao exigido pelo edital"
        in visivel(TEMPLATES / "convocacao_documentos.html").lower()
    )
