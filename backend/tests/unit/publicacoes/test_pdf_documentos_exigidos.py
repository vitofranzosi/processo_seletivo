"""A seção gerada que enuncia os documentos exigidos (US2 da 009, FR-010).

O que se prova aqui é o que separa a lista útil da lista que engana: cada bloco diz **a quem** se
dirige. Sem o cabeçalho de alcance, um laudo exigido só de uma modalidade pareceria exigido de
todo mundo — o defeito clássico do Edital escrito à mão, que a derivação dos dados estruturados
existe para não repetir.
"""

import pytest

from processo_seletivo.publicacoes.infrastructure.pdf import render_edital_pdf
from processo_seletivo.shared.canonical import canonical_sha256
from tests.fixtures.snapshot import DOCUMENTO, MODALIDADE, PERFIL, rascunho_completo
from tests.unit.publicacoes.test_pdf import texto_de

EDITAL_ID = "00000000-0000-0000-0000-0000000005f1"


def _secoes():
    """As seções como o snapshot as materializa — o compositor lê daqui, não do catálogo.

    O construtor de rascunho não as carrega: elas nascem em `edital_snapshot`, a partir do
    catálogo declarado. Reproduzi-las aqui é o que permite provar a composição sem publicar.
    """
    from processo_seletivo.editais.domain import secoes as catalogo

    return [
        {
            "id": str(catalogo.identidade(EDITAL_ID, secao.key)),
            "key": secao.key,
            "title": secao.title,
            "order": secao.order,
            "type": secao.type,
            **({"source": secao.source} if secao.gerada else {"content": secao.default_text}),
        }
        for secao in catalogo.CATALOGO
    ]


def _snapshot(documentos):
    base = rascunho_completo()
    base.update(
        {
            "sections": _secoes(),
            "schemaVersion": 4,
            "editalId": EDITAL_ID,
            "processoId": "00000000-0000-0000-0000-0000000005f2",
            "processoCode": "PS-2026-001",
            "processoTitle": "Processo Seletivo 2026",
            "number": "01",
            "year": 2026,
            "title": "Edital de teste",
            "description": "Descrição",
            "documentRequirements": documentos,
        }
    )
    return base


def _texto(snapshot):
    """O texto **realmente desenhado**, e não os bytes do arquivo — como o teste do compositor.

    Procurar a string no PDF cru passaria por acaso quando ela aparecesse em metadado, e falharia
    sempre que o fluxo a escrevesse escapada.
    """
    from processo_seletivo.publicacoes.infrastructure import pdf as compositor

    documento = render_edital_pdf(
        snapshot,
        canonical_sha256(snapshot),
        autoridade=compositor.AutoridadeSignataria(nome="Diretora", cargo="Diretora-Geral"),
    )
    return texto_de(documento)


DOCUMENTOS = [
    {
        "id": DOCUMENTO["A"],
        "key": "identificacao",
        "name": "Documento de identificacao",
        "instructions": "Frente e verso.",
        "required": True,
        "order": 1,
        "profileId": None,
        "modalityId": None,
    },
    {
        "id": DOCUMENTO["B"],
        "key": "laudo",
        "name": "Laudo comprobatorio",
        "instructions": "",
        "required": True,
        "order": 2,
        "profileId": None,
        "modalityId": MODALIDADE["A"],
    },
]


@pytest.mark.parametrize(
    ("trecho", "porque"),
    [
        ("De todos os candidatos", "o bloco sem restrição se anuncia como de todos"),
        ("Documento de identificacao", "o nome do requisito vai para o documento"),
        ("Frente e verso", "a instrução ao candidato também"),
        ("modalidade", "o bloco restrito nomeia a modalidade a que se dirige"),
        ("Laudo comprobatorio", "e o requisito daquela modalidade"),
    ],
)
def test_a_secao_enuncia_cada_documento_sob_o_alcance_a_que_pertence(trecho, porque):
    texto = _texto(_snapshot(DOCUMENTOS))

    assert trecho in texto, porque


def test_o_bloco_de_um_perfil_nomeia_o_perfil():
    documentos = [dict(DOCUMENTOS[0], profileId=PERFIL["A"], modalityId=None)]

    texto = _texto(_snapshot(documentos))

    assert "perfil" in texto


def test_sem_documento_exigido_a_secao_nao_e_composta():
    """Título sobre nada informaria que alguém esqueceu de preencher — e seria falso.

    A omissão não é regra nova: `_materializaveis` já não compõe seção gerada de fonte vazia, e a
    coleção nova herda esse comportamento sem uma linha a mais.
    """
    texto = _texto(_snapshot([]))

    assert "DOCUMENTOS EXIGIDOS" not in texto.upper()
