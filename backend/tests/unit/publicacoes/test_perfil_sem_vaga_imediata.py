"""Perfil sem vaga imediata: sem quadro zerado e sem frase de reversão (067, ED-12, D-003).

No cenário B da auditoria de 08/10/2026, os 16 Perfis de tutor presencial — 0 vaga imediata,
cadastro de reserva limitado a 15 — imprimiam uma tabela "Quadro de vagas" com as quatro listas em 0
e a frase *"Na hipótese do não preenchimento total das vagas reservadas…"*: reserva de vaga onde não
há vaga. O documento deixa de imprimir as duas coisas e **não** põe frase nova no lugar — a regra da
reserva no cadastro (RC-58) não é declarada pelo sistema (`D-003`). `FR-1320` a `FR-1323`.
"""

import copy
import re

import pytest

from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes.cenarios_da_auditoria import composto, congelado
from tests.unit.publicacoes.test_pdf import documento, snapshot, texto_de

REVERSOES = ("Na hipótese do não preenchimento total", "Havendo ausência de candidatos aprovados")
LEGENDA = re.compile(r"^Tabela (\d+) — (.+)$")


def _corrido(pdf_):
    return " ".join(texto_de(pdf_).split())


def _legendas(pdf_):
    return [
        (int(numero), titulo)
        for linha in texto_de(pdf_).splitlines()
        if (casada := LEGENDA.match(linha.strip()))
        for numero, titulo in [casada.groups()]
    ]


def _perfil(codigo, total, linhas, *, reserva="LIMITED", reversao="ON_BALANCE"):
    """Um Perfil com Modalidades AC e PPI, o quadro pedido e a reversão declarada."""
    base = copy.deepcopy(snapshot()["profiles"][0])
    ac, ppi = f"{codigo}-ac", f"{codigo}-ppi"
    base.update(
        id=f"{codigo}-id",
        code=codigo,
        name=f"Perfil {codigo}",
        immediateVacancies=total,
        reserveType=reserva,
        reserveLimit=15 if reserva == "LIMITED" else None,
        generalCompetitionModalityId=ac,
        competitionModalities=[
            {"id": ac, "code": "AC", "name": "Ampla concorrência", "normativeRule": None},
            {
                "id": ppi,
                "code": "PPI",
                "name": "Pretos, pardos e indígenas",
                "normativeRule": {
                    "foundation": "Lei nº 12.711, de 29 de agosto de 2012",
                    "percentage": "30.0000",
                    "version": "2016-12-28",
                },
            },
        ],
        vacancyTable=[
            {"id": f"{codigo}-l0", "modalityId": None, "immediateVacancies": linhas[0]},
            {"id": f"{codigo}-l1", "modalityId": ppi, "immediateVacancies": linhas[1]},
        ],
        vacancyReversion={"kind": reversao} if reversao else None,
        callForm="PUBLICATION",
        classificationMilestones=[],
    )
    return base


def _texto_com(*perfis):
    return documento(snapshot(profiles=list(perfis)))


def test_sem_vaga_imediata_nem_quadro_nem_reversao_e_o_resto_fica():
    gerado = _texto_com(_perfil("TP-01", 0, [0, 0]))
    corrido = _corrido(gerado)

    assert "Quadro de vagas" not in corrido
    for frase in REVERSOES:
        assert frase not in corrido
    # O que é verdade continua: a tabela de Modalidades com percentual e fundamento (FR-1322).
    assert "Modalidades de concorrência" in corrido
    assert "30%" in corrido and "Lei nº 12.711" in corrido
    assert "A convocação dos classificados será feita por publicação" in corrido


def test_nenhuma_frase_nova_sobre_a_reserva_no_cadastro():
    """D-003: a regra de reserva no cadastro não é declarada pelo sistema."""
    corrido = _corrido(_texto_com(_perfil("TP-01", 0, [0, 0])))

    assert "vaga imediata" not in corrido.lower().replace("vagas imediatas", "")
    assert "cadastro de reserva" not in corrido.lower()


def test_com_vaga_o_quadro_sai_inteiro_com_a_linha_em_zero_e_a_reversao():
    corrido = _corrido(_texto_com(_perfil("TD-ADM", 6, [6, 0])))

    assert "Quadro de vagas" in corrido
    assert "Pretos, pardos e indígenas (PPI) 0" in corrido
    assert "Na hipótese do não preenchimento total das vagas reservadas" in corrido


def test_o_incoerente_continua_com_quadro_para_que_o_erro_se_veja():
    corrido = _corrido(_texto_com(_perfil("X", 0, [0, 2])))

    assert "Quadro de vagas" in corrido


def test_sem_vaga_e_sem_cadastro_tambem_nao_tem_quadro_nem_reversao():
    corrido = _corrido(_texto_com(_perfil("Z", 0, [0, 0], reserva="NONE")))

    assert "Quadro de vagas" not in corrido
    for frase in REVERSOES:
        assert frase not in corrido


def test_as_tabelas_seguintes_sao_numeradas_sem_lacuna():
    gerado = _texto_com(_perfil("TD-ADM", 6, [6, 0]), _perfil("TP-01", 0, [0, 0]))
    numeros = [numero for numero, _ in _legendas(gerado)]

    assert numeros == list(range(1, len(numeros) + 1))
    titulos = [titulo for _, titulo in _legendas(gerado)]
    # Desde a `068`, o quadro de cada Perfil é uma linha da tabela de vagas, e o Perfil sem vaga
    # imediata não tem linha nela; as modalidades dele continuam, na tabela comum.
    assert not [titulo for titulo in titulos if titulo.startswith("Quadro de vagas")]
    assert titulos == [
        "Perfis de vaga",
        "Vagas por lista de concorrência",
        "Modalidades de concorrência",
        "Cronograma",
    ]
    assert _linhas_da_tabela_de_vagas(gerado) == [["TD-ADM", "6", "0"]]


def _linhas_da_tabela_de_vagas(pdf_):
    """As linhas da tabela de vagas, célula a célula, até a legenda seguinte (068)."""
    linhas = [linha.strip() for linha in texto_de(pdf_).splitlines() if linha.strip()]
    inicio = next(
        i for i, linha in enumerate(linhas) if linha.endswith("por lista de concorrência")
    )
    fim = next(
        i for i, linha in enumerate(linhas[inicio + 1 :], inicio + 1) if LEGENDA.match(linha)
    )
    corpo = [
        linha
        for linha in linhas[inicio + 1 : fim]
        if not linha.startswith(("Na hipótese", "Havendo", "destinado", "preenchido"))
    ]
    colunas = corpo.index(next(linha for linha in corpo if linha[:2] in ("TD", "TP")))
    celulas = corpo[colunas:]
    return [celulas[i : i + colunas] for i in range(0, len(celulas) - colunas + 1, colunas)]


def test_a_contagem_de_tabelas_segue_o_documento():
    """A lista de itens da `065` (FR-1205) conta o quadro só quando ele sai."""
    conteudo = snapshot(profiles=[_perfil("TD-ADM", 6, [6, 0]), _perfil("TP-01", 0, [0, 0])])
    assert pdf.tabelas_do_documento(conteudo) == len(_legendas(documento(conteudo)))


def test_a_tabela_de_perfis_continua_sem_total_quando_o_edital_nao_tem_vaga():
    corrido = _corrido(_texto_com(_perfil("TP-01", 0, [0, 0]), _perfil("TP-02", 0, [0, 0])))

    assert "Perfis de vaga" in corrido or "Tabela 1 —" in corrido
    assert "Total" not in corrido


# ---- o cenário B da auditoria ------------------------------------------------------------------


def test_o_cenario_b_tem_vagas_so_dos_dois_perfis_com_vaga_e_uma_reversao():
    """Os 16 Perfis de tutor presencial não têm linha na tabela de vagas nem são alcançados pela
    reversão; os dois de tutor a distância, que têm vaga, sim — com a frase dita uma vez (068)."""
    gerado = composto("B")
    corrido = _corrido(gerado)
    titulos = [titulo for _, titulo in _legendas(gerado)]

    assert not [t for t in titulos if t.startswith("Quadro de vagas")]
    assert [linha[0] for linha in _linhas_da_tabela_de_vagas(gerado)] == ["TD-ADM", "TD-INFO-EDU"]
    assert corrido.count("Na hipótese do não preenchimento total das vagas reservadas") == 1
    assert "Nos Perfis" not in corrido
    assert [t for t in titulos if t.startswith("Modalidades de concorrência")] == [
        "Modalidades de concorrência"
    ]
    assert pdf.tabelas_do_documento(congelado("B")["content"]) == len(titulos)


@pytest.mark.parametrize("cenario", ["A", "B"])
def test_a_contagem_de_tabelas_dos_cenarios_segue_o_documento(cenario):
    assert pdf.tabelas_do_documento(congelado(cenario)["content"]) == len(
        _legendas(composto(cenario))
    )


def test_a_validacao_do_perfil_sem_vaga_nao_muda():
    """FR-1324: a reversão declarada continua aceita, e o aviso da convocação externa, o mesmo."""
    from processo_seletivo.editais.domain.validation import validate_for_publication

    achados = validate_for_publication(congelado("B")["content"])
    codigos = [achado.code for achado in achados]

    assert codigos.count("reserve_only_convocation_external") == 16
    assert not [
        achado
        for achado in achados
        if achado.severity.name == "BLOCKING_ERROR"
        and ("reversion" in achado.code or "vacancy" in achado.code)
    ]
