"""FR-023 — o documento publicado corresponde integralmente à versão homologada.

A cadeia "dados estruturados → versão homologada → PDF publicado" precisa ser demonstrável:
cada Perfil, vaga, modalidade e Evento do snapshot tem de aparecer no documento, o mesmo
snapshot tem de produzir os mesmos bytes, e qualquer mudança tem de mudar o documento.
"""

import re

import pytest

from processo_seletivo.publicacoes.infrastructure.pdf import render_edital_pdf

HASH = "a" * 64
TEXTO_PDF = re.compile(rb"\((.*?)\) Tj", re.DOTALL)


def texto_de(pdf: bytes) -> str:
    """Extrai o texto realmente desenhado, não o que se supõe ter sido escrito."""
    return "\n".join(
        parte.replace(b"\\(", b"(").replace(b"\\)", b")").decode("cp1252")
        for parte in TEXTO_PDF.findall(pdf)
    )


def snapshot(**alteracoes):
    base = {
        "schemaVersion": 1,
        "editalId": "11111111-1111-1111-1111-111111111111",
        "processoId": "22222222-2222-2222-2222-222222222222",
        "number": "07",
        "year": 2026,
        "title": "Edital 07/2026 — Professor Substituto",
        "description": "Seleção simplificada para docência.",
        "profiles": [
            {
                "id": "33333333-3333-3333-3333-333333333333",
                "code": "DOC-INFO",
                "name": "Professor de Informática",
                "description": "Docência em Informática.",
                "requirements": ["Mestrado em Computação"],
                "immediateVacancies": 3,
                "reserveType": "LIMITED",
                "reserveLimit": 6,
                "locality": "Campus Serra",
                "classificationInformation": {},
                "callInformation": {},
                "competitionModalities": [
                    {
                        "id": "44444444-4444-4444-4444-444444444444",
                        "code": "PPP",
                        "name": "Pessoas pretas, pardas e indígenas",
                        "description": "",
                        "normativeRule": {
                            "id": "55555555-5555-5555-5555-555555555555",
                            "foundation": "Lei 12.990/2014",
                            "version": "2014-06-09",
                            "percentage": "20.0000",
                            "calculation": {},
                            "rounding": {},
                            "distribution": {},
                            "callRules": {},
                            "effectiveFrom": None,
                        },
                    }
                ],
            }
        ],
        "schedule": [
            {
                "id": "66666666-6666-6666-6666-666666666666",
                "type": "INSCRICAO",
                "description": "Período de inscrições",
                "startAt": "2026-09-01T09:00:00-03:00",
                "endAt": "2026-09-20T23:59:00-03:00",
                "order": 1,
                "status": "PLANEJADO",
            }
        ],
    }
    return {**base, **alteracoes}


def test_document_reproduces_every_profile_of_the_homologated_version():
    texto = texto_de(render_edital_pdf(snapshot(), HASH))
    perfil = snapshot()["profiles"][0]
    assert perfil["code"] in texto
    assert perfil["name"] in texto
    assert perfil["description"] in texto
    assert perfil["locality"] in texto
    assert perfil["requirements"][0] in texto
    assert "Vagas imediatas: 3" in texto
    assert "limitado em 6" in texto


def test_document_reproduces_competition_modalities_and_their_normative_rule():
    """FR-013: a Regra Normativa é conteúdo do Edital e precisa constar do documento."""
    texto = texto_de(render_edital_pdf(snapshot(), HASH))
    assert "PPP" in texto
    assert "Pessoas pretas, pardas e indígenas" in texto
    assert "Lei 12.990/2014" in texto
    assert "2014-06-09" in texto
    assert "20.0000" in texto


def test_document_reproduces_the_schedule_with_institutional_dates():
    texto = texto_de(render_edital_pdf(snapshot(), HASH))
    assert "Período de inscrições" in texto
    assert "INSCRICAO" in texto
    # America/Sao_Paulo, conforme a zona institucional.
    assert "01/09/2026 09:00" in texto
    assert "20/09/2026 23:59" in texto


def test_document_preserves_portuguese_accents():
    """Documento oficial brasileiro não pode trocar acento por interrogação."""
    texto = texto_de(render_edital_pdf(snapshot(), HASH))
    for esperado in ("Informática", "inscrições", "indígenas", "Seleção", "ESPÍRITO"):
        assert esperado in texto, esperado
    # A versão anterior codificava em ASCII e produzia exatamente estas formas mutiladas.
    for mutilado in ("Inform?tica", "inscri??es", "ind?genas", "Sele??o", "ESP?RITO"):
        assert mutilado not in texto, mutilado


def test_document_carries_the_content_hash_and_identifiers():
    pdf = render_edital_pdf(snapshot(), HASH)
    texto = texto_de(pdf)
    assert HASH in texto
    assert "11111111-1111-1111-1111-111111111111" in texto
    assert "22222222-2222-2222-2222-222222222222" in texto
    assert HASH[:16] in texto  # rodapé de cada página


def test_the_same_snapshot_always_produces_the_same_bytes():
    """Determinismo é o que torna a cadeia verificável: o hash do documento não pode variar."""
    assert render_edital_pdf(snapshot(), HASH) == render_edital_pdf(snapshot(), HASH)


@pytest.mark.parametrize(
    "alteracao",
    [
        {"title": "Outro título"},
        {"profiles": []},
        {"schedule": []},
    ],
)
def test_any_change_in_the_version_changes_the_document(alteracao):
    assert render_edital_pdf(snapshot(), HASH) != render_edital_pdf(snapshot(**alteracao), HASH)


def test_long_content_paginates_and_every_page_is_numbered():
    muitos = snapshot(
        profiles=[
            {**snapshot()["profiles"][0], "code": f"P{indice:02d}", "id": str(indice)}
            for indice in range(1, 26)
        ]
    )
    pdf = render_edital_pdf(muitos, HASH)
    paginas = pdf.count(b"/Type /Page ")
    assert paginas >= 3, paginas
    texto = texto_de(pdf)
    for numero in range(1, paginas + 1):
        assert f"Página {numero} de {paginas}" in texto
    for indice in range(1, 26):
        assert f"P{indice:02d}" in texto, f"perfil P{indice:02d} não foi impresso"


def test_empty_sections_are_declared_instead_of_omitted():
    """Seção vazia precisa dizer que está vazia; silêncio num edital é ambíguo."""
    texto = texto_de(render_edital_pdf(snapshot(profiles=[], schedule=[]), HASH))
    assert "Nenhum Perfil registrado nesta versão." in texto
    assert "Nenhum Evento registrado nesta versão." in texto


def test_parentheses_in_content_do_not_corrupt_the_document():
    """Parêntese é delimitador de string em PDF: sem escape, o arquivo quebra."""
    pdf = render_edital_pdf(snapshot(title="Edital (retificado) 07/2026"), HASH)
    assert b"%%EOF" in pdf
    assert "Edital (retificado) 07/2026" in texto_de(pdf)
