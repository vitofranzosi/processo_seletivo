"""Um exemplar de cada tipo de documento que o GPS compõe em PDF/A (178, FR-8150, FR-8168).

**Os nove da FR-8150, e um só de cada**: é o lote que o job `pdfa` do CI entrega ao veraPDF, e o que
`tests/unit/publicacoes/test_conformidade_pdfa.py` confere sem ele. Nenhum toca o banco — cada um
sai dos mesmos conteúdos fixos que os testes daquele documento já usam, para que o exemplar seja um
documento que a suíte conhece, e não um inventado para passar.

Cada exemplar diz o nível que **declara**: o veraPDF valida contra a declaração (`--flavour 0`), e o
teste confere que a declaração é a esperada — assim, um documento que passasse a declarar 2b por
engano não passaria calado.
"""

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from types import SimpleNamespace

from processo_seletivo.publicacoes.infrastructure import pdfa

CONTRATO = Path(__file__).resolve().parent.parent / "contract" / "fixtures"


@dataclass(frozen=True)
class Exemplar:
    nome: str
    nivel: str
    compor: object

    @property
    def arquivo(self):
        return f"{self.nome}.pdf"


def _json(nome):
    return json.loads((CONTRATO / nome).read_text(encoding="utf-8"))


def _contexto_do_edital():
    from processo_seletivo.publicacoes.infrastructure.pdf import AutoridadeSignataria, UnidadeDoAto

    unidade = _json("unidade_publicada.json")
    return {
        "unidade": UnidadeDoAto(cabecalho=tuple(unidade["cabecalho"]), local=unidade["local"]),
        "autoridade": AutoridadeSignataria(**_json("autoridade_publicada.json")),
        "data_do_ato": date.fromisoformat(_json("contexto_publicado.json")["data_do_ato"]),
    }


def edital():
    from processo_seletivo.publicacoes.infrastructure.pdf import render_edital_pdf
    from processo_seletivo.shared.canonical import canonical_sha256

    snapshot = _json("snapshot_publicado.json")
    return render_edital_pdf(snapshot, canonical_sha256(snapshot), **_contexto_do_edital())


def retificacao():
    """O documento consolidado de uma Retificação: o mesmo escritor, com a consolidação no topo."""
    from processo_seletivo.publicacoes.infrastructure.pdf import Consolidacao, render_edital_pdf
    from processo_seletivo.shared.canonical import canonical_sha256

    snapshot = _json("snapshot_publicado.json")
    contexto = _contexto_do_edital()
    consolidacao = Consolidacao(
        publicado_em=contexto["data_do_ato"], retificado_em=(date(2026, 11, 16),)
    )
    contexto["data_do_ato"] = date(2026, 11, 16)
    return render_edital_pdf(
        snapshot, canonical_sha256(snapshot), consolidacao=consolidacao, **contexto
    )


def comprovante():
    from processo_seletivo.inscricoes.infrastructure.comprovante_pdf import render_comprovante_pdf

    return render_comprovante_pdf(_json("comprovante_v1.json"), pdfa=True)


def resultado():
    from processo_seletivo.divulgacao.infrastructure.documento import render_resultado_pdf

    return render_resultado_pdf(_json("divulgacao_v1.json"))


def inscricoes():
    from processo_seletivo.divulgacao.domain import inscricoes as dominio
    from processo_seletivo.divulgacao.infrastructure.documento_das_inscricoes import (
        render_inscricoes_pdf,
    )
    from tests.unit.divulgacao.test_projecao_das_inscricoes import COTAS, LISTAS, PERFIS

    projecao = dominio.projetar(
        natureza=dominio.RECEBIDAS,
        inscricoes=COTAS,
        resultados=None,
        perfis=PERFIS[:1],
        listas=LISTAS,
    )
    conteudo = dominio.conteudo_publico(
        projecao=projecao,
        natureza=dominio.RECEBIDAS,
        processo="Processo 2026",
        edital="Edital 01/2026",
        etapa="",
        prazo=None,
        publicado_em=datetime(2026, 11, 12, 12, tzinfo=UTC),
        signatario=SimpleNamespace(nome="", cargo="Diretoria", ato_de_nomeacao=""),
        unidade=SimpleNamespace(sigla="Cefor", nome="Cefor", cabecalho=("Cefor",)),
    )
    return render_inscricoes_pdf(conteudo)


PESSOAS_CONVOCADAS = (("Beatriz Souza", "INS-2026-0002"), ("Íris Araújo", "INS-2026-0007"))
CEFOR = "Centro de Referência em Formação e em Educação a Distância"


def convocados():
    from processo_seletivo.convocacao.domain import publicacao as dominio
    from processo_seletivo.convocacao.infrastructure.documento import render_convocados_pdf

    vencimento = datetime(2026, 11, 20, 23, 59, tzinfo=UTC)
    linhas = [
        {
            "chave": "ampla",
            "ordem": 0,
            "perfil": "Professor de Matemática",
            "lista": "Ampla concorrência",
            "marco": "Resultado definitivo",
            "efeito": dominio.CONVOCA,
            "canal": "",
            "vencimento": vencimento,
            "nome": nome,
            "protocolo": protocolo,
            "corrige": None,
        }
        for nome, protocolo in PESSOAS_CONVOCADAS
    ]
    conteudo = dominio.conteudo(
        cabecalho={
            "titulo": "1ª publicação de convocados",
            "processo": "Processo 2026",
            "edital": "Edital 01/2026",
            "publicadoEm": "2026-11-16T13:00:00+00:00",
            "unidade": {"cabecalho": [CEFOR]},
            "signatario": {
                "nome": "Maria Diretora",
                "cargo": "Diretora-Geral",
                "atoDeNomeacao": "",
            },
        },
        grupos=dominio.compor_grupos(linhas),
    )
    return render_convocados_pdf(conteudo)


def agenda():
    from processo_seletivo.agendamento.infrastructure.documento import render_agenda_pdf
    from tests.unit.agendamento.test_documento import _conteudo

    return render_agenda_pdf(_conteudo())


def relatorio_do_edital():
    from processo_seletivo.interface import relatorio_pdf
    from tests.unit.interface.test_diagramacao_do_relatorio_do_edital import _relatorio

    return relatorio_pdf.compor(_relatorio(), emissao=1)


def relatorio_consolidado():
    from processo_seletivo.interface import relatorio_consolidado_pdf
    from tests.unit.interface.test_diagramacao_do_consolidado import _conjunto_de

    return relatorio_consolidado_pdf.compor(_conjunto_de(3), emissao=1)


EXEMPLARES = (
    Exemplar("edital", pdfa.NIVEL_U, edital),
    Exemplar("retificacao", pdfa.NIVEL_U, retificacao),
    Exemplar("comprovante", pdfa.NIVEL_U, comprovante),
    Exemplar("resultado", pdfa.NIVEL_U, resultado),
    Exemplar("inscricoes", pdfa.NIVEL_U, inscricoes),
    Exemplar("convocados", pdfa.NIVEL_U, convocados),
    Exemplar("agenda", pdfa.NIVEL_U, agenda),
    Exemplar("relatorio-do-edital", pdfa.NIVEL_A, relatorio_do_edital),
    Exemplar("relatorio-consolidado", pdfa.NIVEL_A, relatorio_consolidado),
)
