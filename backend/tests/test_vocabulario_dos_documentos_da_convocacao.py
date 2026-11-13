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
    PORTAL / "convocacao.html",
    # A `118`: a lista da `115` virou cinco blocos e um cartão por documento, e os textos de cada
    # item e de cada momento da chamada moram na projeção (FR-3751). O parcial de antes,
    # `_documentos_da_convocacao.html`, saiu.
    PORTAL / "_obrigacoes_da_convocacao.html",
    PORTAL / "_cartao_do_documento_da_convocacao.html",
    PORTAL / "_requerimento_nas_obrigacoes.html",
    PORTAL / "acompanhamento.html",
    RAIZ / "portal/obrigacoes.py",
    RAIZ / "portal/situacao.py",
    # A `121` (FR-3892): a chamada, com a confirmação do envio — que diz "o arquivo aguarda", e
    # nunca aceito, aprovado nem atendido (FR-3870) — e os modelos da mensagem.
    PORTAL / "_chamada_da_convocacao.html",
    RAIZ / "convocacao/templates/convocacao/mensagem/inicial.html",
    RAIZ / "convocacao/templates/convocacao/mensagem/inicial.txt",
    RAIZ / "convocacao/templates/convocacao/mensagem/correcao.html",
    RAIZ / "convocacao/templates/convocacao/mensagem/correcao.txt",
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
    # A `118` (FR-3751): o documento não é dito atendido, aprovado nem aceito antes da conferência,
    # e nenhuma frase diz que a pessoa enviou tudo — o aproveitado da inscrição não foi reenviado.
    r"atendid[oa] pelo": '"atendido" antes da conferência era a falsa conclusão de um item (118)',
    r"documento aprovad": "a conferência diz conforme ao exigido, e nunca aprovado (FR-3589)",
    r"documento aceit": "idem",
    r"enviou tudo": "o aproveitado não foi reenviado, e a frase apagaria a diferença (D-005)",
    r"apto para formaliza": "o termo é da gestão; no portal soaria como promessa (D-014 da 118)",
}

#: A frase da gestão, que o portal não diz (D-014 da `118`): só as superfícies da gestão a usam.
DA_GESTAO = {
    TEMPLATES / "convocacao_documentos.html",
    TEMPLATES / "convocacao.html",
    TEMPLATES / "alocacoes.html",
}


@pytest.mark.parametrize("caminho", DA_115, ids=lambda item: f"{item.parent.name}/{item.name}")
def test_nenhuma_tela_dos_documentos_afirma_vinculo_nem_autenticidade(caminho):
    corpo = visivel(caminho).lower()
    achados = [
        f"{termo!r} — {porque}"
        for termo, porque in PROIBIDOS.items()
        if re.search(termo, corpo)
        and not (termo == r"apto para formaliza" and caminho in DA_GESTAO)
    ]
    assert achados == [], f"{caminho.name}: " + "; ".join(achados)


def test_a_conducao_diz_apto_para_formalizacao():
    """A ausência não basta: a frase certa precisa estar lá (D-005)."""
    assert "apto para formalização" in visivel(TEMPLATES / "convocacao.html").lower()


def test_a_conferencia_diz_conforme_ao_exigido():
    # O formulário saiu da página para o cartão de cada item na 157
    # (`_documento_da_convocacao.html`), que o registro sem recarga devolve sozinho.
    assert (
        "conforme ao exigido pelo edital"
        in visivel(TEMPLATES / "_documento_da_convocacao.html").lower()
    )


# --- O documento reenviado tem um nome só (154, FR-6214) -----------------------------------------

#: Os nomes que o mesmo fato tinha antes da `154` (achado 23 do estudo da jornada final).
NOMES_ANTIGOS_DO_REENVIADO = (
    "complementado, aguardando conferência",
    r"reenviados?(\(s\))?, a conferir de novo",
    "documento reenviado, a conferir de novo",
    "documento reenviado: nova conferência",
    "documento reenviado, aguardando conferência",
)

#: Onde o nome é dito: as telas da `115`, o resumo da página de documentos (parcial desde a `157`),
#: o passo e a frase da condução, o rótulo do item e a exclusão do aviso de pendência.
DO_REENVIADO = [
    *DA_115,
    TEMPLATES / "_situacao_dos_documentos.html",
    RAIZ / "interface/conducao_da_convocacao.py",
    RAIZ / "interface/views.py",
    RAIZ / "avisos/application/pendencias.py",
    # A Visão do Sistema, que a gestão serve em "Documentação do Sistema" (105): texto visível dela.
    RAIZ.parents[1] / "docs/visao-sistema/index.html",
]


@pytest.mark.parametrize(
    "caminho", DO_REENVIADO, ids=lambda item: f"{item.parent.name}/{item.name}"
)
def test_nenhum_nome_antigo_do_reenviado(caminho):
    corpo = visivel(caminho).lower()
    achados = [nome for nome in NOMES_ANTIGOS_DO_REENVIADO if re.search(nome, corpo)]
    assert achados == [], f"{caminho.name}: {achados}"


def test_o_aviso_do_arquivo_repetido_nao_afirma_conferencia():
    """150, FR-5615, contrato §4: as duas frases do aviso estão no script, e nenhuma diz aceito,
    aprovado nem conferido — o aviso é de coincidência, e não de juízo sobre o arquivo."""
    script = (RAIZ / "portal/static/portal/varios.js").read_text(encoding="utf-8")
    frases = re.findall(r'"(Atenção: este arquivo é o mesmo que você [^"]+)"', script)

    assert frases == [
        "Atenção: este arquivo é o mesmo que você escolheu para ",
        "Atenção: este arquivo é o mesmo que você já enviou para ",
    ]
    assert not [f for f in frases if re.search(r"aceit|aprovad|conferid", f.lower())]
