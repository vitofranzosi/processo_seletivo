"""Nenhum termo interno na redação que o sistema gera (069, FR-1360, FR-1366, SC-518, FR-1395).

A auditoria de 08/10/2026 apontou os termos do sistema que chegavam ao candidato: "Marcos
classificatórios", "recorte", "inscrições submetidas", os rótulos "Corte:", "Continuação:",
"Normalização:", "Combinação:", "Habilitação:" e "Ordem:", "valor declarado em" e o tipo do dado
entre parênteses. A regra vale para **toda a redação gerada** — frases, rótulos, títulos de
subseção e remissões — nas duas apresentações (D-007).

**O texto livre de quem elabora sai como foi escrito** (FR-1395): um "marcos classificatórios" que
o Elaborador escreveu não é redação gerada, e não conta. O teste separa os dois pela origem: tudo o
que vem de um campo de texto do snapshot é tirado do texto do documento antes da varredura, e o que
sobra é o que o sistema escreveu.
"""

import copy
import re

import pytest

from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes.cenarios_da_auditoria import composto, congelado
from tests.unit.publicacoes.test_pdf import documento, snapshot, texto_de
from tests.unit.publicacoes.test_pdf_classificacao import CRITERIOS, ETAPAS, FATOS, marco

# FR-1366, na grafia em que o sistema os escrevia.
TERMOS_INTERNOS = (
    "Marcos classificatórios",
    "marcos classificatórios",
    "recorte",
    "inscrições submetidas",
    "Corte:",
    "Continuação:",
    "Normalização:",
    "Combinação:",
    "Habilitação:",
    "Ordem:",
    "valor declarado em",
    "(número inteiro)",
    "(data)",
)

# Os campos de texto livre do snapshot: o que o Elaborador escreve, e o documento reproduz.
_LIVRES = (
    "content",
    "name",
    "description",
    "label",
    "locality",
    "workload",
    "compensation",
    "duties",
    "foundation",
    "instructions",
    "title",
    "processoTitle",
    "text",
    "declarationText",
    "derivation",
    "occurrence",
    "source",
    "rotuloFavoravel",
    "rotuloDesfavoravel",
)


def _normal(texto):
    return " ".join(str(texto).split())


def _livres(valor):
    """Cada texto livre do snapshot, e cada parágrafo dele."""
    if isinstance(valor, dict):
        for chave, item in valor.items():
            if chave in _LIVRES and isinstance(item, str) and item.strip():
                yield _normal(item)
                yield from (_normal(parte) for parte in pdf._paragrafos(item))
            elif chave == "requirements" and isinstance(item, list):
                yield from (_normal(requisito) for requisito in item if isinstance(requisito, str))
            else:
                yield from _livres(item)
    elif isinstance(valor, list):
        for item in valor:
            yield from _livres(item)


def redacao_gerada(conteudo, pdf_):
    """O texto do documento sem o que veio de texto livre do snapshot — o que o sistema escreveu."""
    texto = _normal(texto_de(pdf_))
    for livre in sorted(set(_livres(conteudo)), key=len, reverse=True):
        if len(livre) > 2:
            texto = texto.replace(livre, " ")
    return texto


def _completo():
    """Um Edital com toda variante que gera frase: sorteio e pontuação, corte, empate, desempate."""
    sorteio = {
        **marco(
            code="SORT",
            name="Sorteio público",
            orderProduction="POR_SORTEIO",
            stages=[],
            tiebreakers=[],
        ),
        "id": "sorteio",
        "cutRule": {
            "targetKind": "FROM_VACANCY_TABLE",
            "targetCount": None,
            "surplusCount": 3,
            "tieOutcome": "STRICT",
            "continuation": "ALLOWED",
            "governedStage": ETAPAS[1]["id"],
        },
        "appealWindow": {"admits": True, "durationDays": 2, "unit": "DIAS_CORRIDOS"},
        "drawMethod": {
            "algorithm": "IFES-SORTEIO-SHA256-v1",
            "source": "Loteria Federal",
            "occurrence": "Concurso 6100",
            "occurrenceAt": "2026-11-20T20:00:00-03:00",
            "derivation": "o primeiro concurso após a data do sorteio",
            "normalization": {"rule": "DIGITOS_EM_SEQUENCIA", "text": "os dígitos em sequência"},
            "substitutionRule": {
                "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
                "text": "a ocorrência seguinte",
            },
            "qualifyingStageId": ETAPAS[0]["id"],
        },
    }
    pontuacao = marco(
        normalization="PELA_SOMA_DOS_PESOS",
        tiebreakers=list(CRITERIOS),
        cutRule={
            "targetKind": "FIXED",
            "targetCount": 10,
            "surplusCount": 0,
            "tieOutcome": "ADMITS_SURPLUS",
            "continuation": "NONE",
            "governedStage": "NONE",
        },
        appealWindow={"admits": False},
    )
    base = snapshot(stages=ETAPAS, maxInscricoesPorCandidato=2)
    perfil = {
        **base["profiles"][0],
        "declaredFacts": FATOS,
        "classificationMilestones": [sorteio, pontuacao],
        "vacancyReversion": {"kind": "ON_BALANCE"},
        "callForm": "PUBLICATION",
        "vacancyTable": [
            {"id": "l0", "modalityId": None, "immediateVacancies": 2},
            {
                "id": "l1",
                "modalityId": base["profiles"][0]["competitionModalities"][0]["id"],
                "immediateVacancies": 1,
            },
        ],
    }
    segundo = {**copy.deepcopy(perfil), "id": "segundo", "code": "DOC-MAT"}
    base["profiles"] = [perfil, segundo]
    base["matriculationRequest"] = {"moment": "AT_ENROLLMENT", "declarationText": "Declaro X."}
    return base


def _documentos():
    for cenario in ("A", "B"):
        yield cenario, congelado(cenario)["content"], composto(cenario)
    conteudo = _completo()
    yield "completo", conteudo, documento(conteudo)
    yield "completo, prévia", conteudo, documento(conteudo, modo=pdf.MODO_PREVIA)


@pytest.mark.parametrize("caso", ["A", "B", "completo", "completo, prévia"])
def test_nenhum_termo_interno_na_redacao_gerada(caso):
    """SC-518: zero ocorrências, em todo documento composto, só na parte gerada."""
    conteudo, pdf_ = next((c, p) for nome, c, p in _documentos() if nome == caso)
    gerada = redacao_gerada(conteudo, pdf_)

    achados = [termo for termo in TERMOS_INTERNOS if termo in gerada]
    assert not achados, achados


def test_o_termo_escrito_pelo_elaborador_sai_literal_e_nao_conta():
    """Caso-limite da spec: "conforme os marcos classificatórios do item 5" sai como foi escrito."""
    conteudo = _completo()
    escrito = "Os casos omissos seguem os marcos classificatórios do item 5 e o recorte do polo."
    for secao in conteudo["sections"]:
        if secao["key"] == "disposicoes-finais":
            secao["content"] = escrito
    pdf_ = documento(conteudo)

    assert escrito in _normal(texto_de(pdf_)), "o texto livre saiu alterado"
    gerada = redacao_gerada(conteudo, pdf_)
    assert "marcos classificatórios" not in gerada and "recorte" not in gerada


def test_a_leitura_pega_o_termo_que_o_sistema_voltasse_a_gerar(monkeypatch):
    """A prova reprova o defeito que existe para pegar: um rótulo gerado com o termo antigo."""
    monkeypatch.setitem(pdf.ROTULO_DAS_REGRAS, pdf.REDACAO_2, "Marcos classificatórios")
    conteudo = _completo()

    gerada = redacao_gerada(conteudo, documento(conteudo))

    assert "Marcos classificatórios" in gerada


@pytest.mark.parametrize(
    "frase",
    [
        "Participam do sorteio só as inscrições habilitadas na Etapa “Prova didática”.",
        "A ordem de classificação segue a nota final.",
        "Depois, o resultado é dividido pela soma dos pesos.",
        "Passam para a Etapa “Análise de títulos” os primeiros classificados de cada lista de "
        "concorrência, em número igual ao das vagas dessa lista, mais 3 (três) suplentes.",
        "Seguem no processo os 10 (dez) primeiros classificados.",
        "Se houver empate na última posição, passam todos os empatados, mesmo que ultrapassem "
        "esse número.",
        "Depois, poderão ser chamados outros candidatos, além desses, seguindo a mesma ordem.",
        "Não serão chamados candidatos além desses.",
        "Contra o resultado de “Sorteio público”: no prazo de 2 (dois) dias corridos",
        "Não caberá recurso contra o resultado de “Classificação final”.",
        "Critérios de desempate, nesta ordem:",
        "2º maior número de meses de experiência em EaD, informado na inscrição",
        "As vagas reservadas de um código que não forem preenchidas passam para a ampla "
        "concorrência do mesmo código.",
        "A convocação dos classificados será feita por publicação.",
        "Cada candidato pode enviar no máximo 2 (duas) inscrições neste Edital.",
        "O Requerimento de Matrícula é enviado no ato da inscrição. Ao enviá-lo, o candidato "
        "declara:",
        "Regras de classificação",
        "Na inscrição, informe também:",
        "Autenticidade — este documento corresponde integralmente à versão homologada do Edital",
    ],
)
def test_cada_frase_do_contrato_sai_onde_a_variante_existe(frase):
    """FR-1360: a redação 2 é a que sai, variante a variante, no documento composto."""
    assert frase in _normal(texto_de(documento(_completo())))


def test_sem_cadastro_os_suplentes_sao_explicados_e_com_cadastro_nao():
    """K7 e K8 no documento (FR-1362): com cadastro de reserva, nada; sem ele, a frase."""
    k7 = "Os suplentes são chamados, na ordem, para as vagas deste Edital"
    com_cadastro = _completo()
    sem_cadastro = _completo()
    for perfil in sem_cadastro["profiles"]:
        perfil.update(reserveType="NONE", reserveLimit=None)

    assert k7 not in _normal(texto_de(documento(com_cadastro)))
    assert k7 in _normal(texto_de(documento(sem_cadastro)))


def test_o_cenario_a_diz_a_regra_do_sorteio_sem_condicao_acrescentada():
    """K9 no cenário A: a continuação sai, e nada gerado a condiciona a sobrar vaga."""
    gerada = redacao_gerada(congelado("A")["content"], composto("A"))

    assert "Depois, poderão ser chamados outros candidatos" in gerada
    assert not re.search(r"\bse (ainda )?sobrarem\b", gerada)
