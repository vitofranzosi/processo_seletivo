"""A tabela do barema no PDF do Edital, e o PDF sem barema intocado (146, T013).

O Edital com barema é publicado pelo caminho real — rascunho, submissão, homologação, publicação — e
o que se afirma sobre o documento é lido dos bytes que a publicação guardou, com o barema do 14/2026
(quickstart §1). A apresentação plana, que só os Editais anteriores ao catálogo da `069` usam, é
composta direto pelo compositor, nas duas redações.

**Sem barema, o documento não muda** (FR-5209, SC-1624). Não há como rodar aqui o código de antes
da feature; o que se prova é o equivalente verificável: o mesmo conteúdo, com a lista vazia que o
degrau 21 escreve e sem a chave que o acervo não tinha, produz o mesmo texto — e nenhuma tabela a
mais. A comparação com o documento do código anterior foi feita à mão, sobre a `main`, e está no PR.
"""

import copy
from decimal import Decimal

import pytest

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from processo_seletivo.publicacoes.infrastructure import pdf
from processo_seletivo.publicacoes.infrastructure.pdf import (
    MODO_PREVIA,
    REDACAO_1,
    Composicao,
    render_edital_pdf,
)
from processo_seletivo.publicacoes.models import DocumentoPublicado
from tests.fixtures.autoridades import UNIDADE_DA_SUITE
from tests.fixtures.edital import complete_draft
from tests.fixtures.publicacao import publish_original
from tests.interface.test_fluxo import texto_de_pdf_bytes

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ETAPA = "aaaaaaaa-0000-4000-8000-000000014650"
TITULOS = "aaaaaaaa-0000-4000-8000-000000014651"
DECLARACAO = "aaaaaaaa-0000-4000-8000-000000014652"


def _criterio(indice, nome, maxima, pontos=None, unidade=None, documento=None, descricao=""):
    return {
        "id": f"aaaaaaaa-0000-4000-8000-00000001466{indice}",
        "name": nome,
        "description": descricao,
        "maximumScore": maxima,
        "pointsPerUnit": pontos,
        "unitLabel": unidade,
        "documentRequirementId": documento,
    }


#: O Anexo IV do 14/2026 (Orientador de TFC), como o quickstart §1 o compõe.
BAREMA_DO_14_2026 = [
    _criterio(0, "Diploma de Doutorado", "20", "20", "diploma", TITULOS),
    _criterio(1, "Diploma de Mestrado", "15", "15", "diploma", TITULOS),
    _criterio(2, "Especialização", "10", "5", "certificado", TITULOS, "Lato sensu."),
    _criterio(3, "Curso de formação de orientadores", "15", "15", "certificado", TITULOS),
    _criterio(4, "Exercício de docência em EaD", "40", "1", "mês", DECLARACAO),
]


def rascunho(barema=BAREMA_DO_14_2026):
    draft = complete_draft()
    draft["stages"] = [
        {
            "id": ETAPA,
            "name": "Prova de Títulos",
            "order": 1,
            "classificatory": True,
            "maximumScore": str(sum((Decimal(c["maximumScore"]) for c in barema), Decimal("0")))
            if barema
            else None,
            "criteria": barema,
        }
    ]
    draft["documentRequirements"] = [
        {
            "id": TITULOS,
            "key": "titulos",
            "name": "Títulos acadêmicos",
            "required": False,
            "order": 1,
        },
        {
            "id": DECLARACAO,
            "key": "docencia",
            "name": "Declaração de exercício de docência",
            "required": False,
            "order": 2,
        },
    ]
    return draft


def texto_publicado(edital):
    documento = DocumentoPublicado.objects.get(publicacao__edital=edital)
    return texto_de_pdf_bytes(bytes(documento.bytes))


def corrido(texto):
    return " ".join(texto.split())


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho())


# --- o Edital publicado com barema (FR-5208, FR-5209, SC-1620) -----------------------------------


def test_o_conteudo_publicado_leva_o_barema_na_ordem_da_ficha(publicado):
    from processo_seletivo.publicacoes.application.selectors import effective_version

    etapa = effective_version(edital_id=publicado.id).content["stages"][0]

    assert etapa["maximumScore"] == "100.0000"
    assert [c["name"] for c in etapa["criteria"]] == [c["name"] for c in BAREMA_DO_14_2026]
    assert etapa["criteria"][2] == {
        **BAREMA_DO_14_2026[2],
        "maximumScore": "10.0000",
        "pointsPerUnit": "5.0000",
    }


def test_o_pdf_publicado_imprime_a_ficha_como_tabela(publicado):
    linhas = texto_publicado(publicado).splitlines()
    texto = corrido("\n".join(linhas))

    assert any(
        linha.startswith("Tabela ") and "Barema da Etapa Prova de Títulos" in linha
        for linha in linhas
    )
    for cabecalho in ("Critério", "Pontuação", "Máxima", "Comprovação"):
        assert cabecalho in linhas
    for trecho in (
        "Diploma de Doutorado",
        "20 pontos por diploma",
        "Especialização — Lato sensu.",
        "5 pontos por certificado, até 10",
        "1 ponto por mês, até 40",
        "Títulos acadêmicos",
        "Declaração de exercício de docência",
    ):
        assert trecho in texto, trecho
    depois_da_legenda = linhas[
        next(i for i, linha in enumerate(linhas) if "Barema da Etapa" in linha) :
    ]
    total = depois_da_legenda.index("Total")
    assert depois_da_legenda[total + 1] == "100", "o total ao pé da ficha"


def test_a_tabela_vem_depois_da_frase_da_etapa(publicado):
    texto = corrido(texto_publicado(publicado))

    assert texto.index("pontuação máxima de 100") < texto.index("Barema da Etapa Prova de Títulos")


def test_a_conta_das_tabelas_inclui_a_do_barema(publicado):
    """A remissão a "Tabela N" é conferida contra esta conta (065, D-004)."""
    from processo_seletivo.publicacoes.application.selectors import effective_version

    snapshot = effective_version(edital_id=publicado.id).content
    sem = copy.deepcopy(snapshot)
    sem["stages"][0]["criteria"] = []

    assert pdf.tabelas_do_documento(snapshot) == pdf.tabelas_do_documento(sem) + 1


# --- a apresentação plana, nas duas redações ------------------------------------------------------


def _etapas_compostas(snapshot, redacao=None):
    composicao = Composicao(**({"redacao": redacao} if redacao is not None else {}))
    tabelas = pdf._Numerador()
    pdf._etapas(composicao, snapshot, 6, tabelas)
    return [item[1] for item in composicao.itens if item[0] == "texto"], tabelas


@pytest.mark.parametrize("redacao", [None, REDACAO_1], ids=["vigente", "redacao-1"])
def test_a_apresentacao_plana_imprime_o_barema_nas_duas_redacoes(redacao):
    snapshot = {
        "stages": [{**rascunho()["stages"][0], "maximumScore": "100.0000", "forma": "PONTUADA"}],
        "documentRequirements": rascunho()["documentRequirements"],
        "schedule": [],
    }

    textos, tabelas = _etapas_compostas(snapshot, redacao)

    assert "Tabela 1 — Barema da Etapa Prova de Títulos" in textos
    assert "5 pontos por certificado, até 10" in textos
    assert tabelas.contagem == 1


def test_a_conta_da_apresentacao_plana_acompanha_a_composicao():
    """`tabelas_do_documento` na plana conta pela régua de `tabela_do_barema`, e não por outra."""
    etapa = {**rascunho()["stages"][0], "maximumScore": "100.0000", "forma": "PONTUADA"}
    snapshot = {"stages": [etapa, {**etapa, "id": TITULOS, "criteria": []}]}

    assert pdf.linhas_do_barema(snapshot["stages"][0], snapshot) is not None
    assert pdf.linhas_do_barema(snapshot["stages"][1], snapshot) is None


# --- sem barema, o documento é o de antes (FR-5209, SC-1624) -------------------------------------


@pytest.fixture
def sem_barema(api_client, manager_headers, process_payload):
    draft = rascunho(barema=[])
    for etapa in draft["stages"]:
        etapa.pop("criteria")
        etapa["maximumScore"] = "100.0000"
    return publish_original(api_client, manager_headers, process_payload, draft=draft)


def _previa(snapshot):
    return texto_de_pdf_bytes(
        render_edital_pdf(snapshot, "", modo=MODO_PREVIA, unidade=UNIDADE_DA_SUITE)
    )


def test_sem_barema_o_conteudo_traz_a_lista_vazia(sem_barema):
    from processo_seletivo.publicacoes.application.selectors import effective_version

    assert effective_version(edital_id=sem_barema.id).content["stages"][0]["criteria"] == []


def test_sem_barema_o_texto_do_pdf_e_o_de_antes_do_degrau(sem_barema):
    """A lista vazia do degrau 21 e a chave ausente do acervo compõem o mesmo documento."""
    snapshot = edital_snapshot(Edital.objects.get(pk=sem_barema.id))
    do_acervo = copy.deepcopy(snapshot)
    for etapa in do_acervo["stages"]:
        del etapa["criteria"]

    atual = _previa(snapshot)

    assert atual == _previa(do_acervo)
    assert "Barema" not in atual
    assert "Comprovação" not in atual


def test_tirar_o_barema_tira_so_a_tabela(publicado):
    """O mesmo Edital, com e sem a ficha: a diferença é uma tabela, e só ela."""
    from processo_seletivo.publicacoes.application.selectors import effective_version

    com = effective_version(edital_id=publicado.id).content
    sem = copy.deepcopy(com)
    sem["stages"][0]["criteria"] = []
    texto_com, texto_sem = _previa(com), _previa(sem)

    assert "Barema da Etapa" in texto_com
    assert "Barema da Etapa" not in texto_sem
    assert (
        sum(1 for linha in texto_com.splitlines() if linha.startswith("Tabela "))
        == sum(1 for linha in texto_sem.splitlines() if linha.startswith("Tabela ")) + 1
    )
