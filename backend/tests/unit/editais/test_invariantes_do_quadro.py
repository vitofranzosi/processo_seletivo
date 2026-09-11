"""Os oito invariantes da §5 da spec da `025`, um teste por invariante.

Eles são verificáveis **a qualquer momento, em qualquer estado do acervo** — é o que a spec exige
para fechar a feature. Três deles são de **ausência**, e é por isso que este arquivo existe em vez
de a verificação ficar espalhada: ausência não se prova exercitando um caminho, e sim varrendo os
que existem. Um caminho novo que os viole nasce com este arquivo vermelho.
"""

import re
from pathlib import Path

import pytest

from processo_seletivo.editais.domain.perfis import ProfileValidationError, validate_profiles
from processo_seletivo.editais.domain.validation import blocking_findings, validate_for_publication
from processo_seletivo.publicacoes.domain import colecoes
from processo_seletivo.publicacoes.domain.elevacao import DEGRAUS_DE_PERFIL

CODIGO = Path(__file__).resolve().parents[3] / "processo_seletivo"
PERFIL = "aaaaaaaa-0000-4000-8000-000000000501"
PCD = "aaaaaaaa-0000-4000-8000-000000000502"
PPI = "aaaaaaaa-0000-4000-8000-000000000503"


def perfil(**alteracoes):
    dados = {
        "id": PERFIL,
        "code": "C1",
        "name": "Curso",
        "immediateVacancies": 80,
        "reserveType": "NONE",
        "reserveLimit": None,
        "competitionModalities": [
            {"id": PCD, "code": "PCD", "name": "Pessoa com deficiência"},
            {"id": PPI, "code": "PPI", "name": "Pretos, pardos e indígenas"},
        ],
    }
    return {**dados, **alteracoes}


def linha(quantidade, modalidade_id=None, identidade="aaaaaaaa-0000-4000-8000-00000000050a"):
    return {"id": identidade, "modalityId": modalidade_id, "immediateVacancies": quantidade}


def snapshot(um_perfil):
    return {
        "title": "Edital",
        "description": "…",
        "schedule": [{"id": PERFIL, "type": "X", "description": "…"}],
        "profiles": [um_perfil],
    }


def do_quadro(um_perfil):
    return [
        item
        for item in blocking_findings(validate_for_publication(snapshot(um_perfil)))
        if item.code.startswith("vacancy_")
    ]


def fontes():
    """Todo módulo de produção, para as varreduras de ausência."""
    return {caminho: caminho.read_text(encoding="utf-8") for caminho in CODIGO.rglob("*.py")}


# --- 1 · nenhuma quantidade de vaga é derivada de percentual (FR-157) ------------------------


def test_invariante_1_nenhuma_quantidade_e_derivada_de_percentual():
    """Varredura de **ausência de caminho de escrita**, e não de comportamento.

    `vagas_imediatas` e `immediateVacancies` só são escritos a partir do que alguém declarou — o
    formulário, o serializer, o payload da Retificação. Nenhuma atribuição os deriva de
    `percentage`, e é a ausência desse caminho que sustenta o invariante: um caminho novo que o
    criasse faria este teste falhar antes de qualquer Edital ser publicado errado.
    """
    escrita = re.compile(
        r"(vagas_imediatas|immediateVacancies\"?\]?)\s*=\s*[^\n]*"
        r"(percentage|percentual|regra_normativa|normativeRule)"
    )
    infratores = [
        f"{caminho}:{numero}"
        for caminho, fonte in fontes().items()
        for numero, texto in enumerate(fonte.splitlines(), 1)
        if escrita.search(texto)
    ]

    assert infratores == [], f"quantidade derivada de percentual: {infratores}"


# --- 2 · a ampla concorrência aparece uma vez por Perfil (FR-154) ----------------------------


def test_invariante_2_a_ampla_concorrencia_aparece_uma_vez_por_perfil():
    """Duas camadas independentes, e as duas verificadas: elaboração e conteúdo publicado."""
    duas = perfil(vacancyTable=[linha(56), linha(20, identidade=f"{PPI[:-1]}b")])

    with pytest.raises(ProfileValidationError):
        validate_profiles([duas])
    assert [item.code for item in do_quadro(duas)] == ["vacancy_general_row_duplicated"]


# --- 3 · toda linha reservada referencia Modalidade do próprio Perfil (FR-155, FR-158) -------


def test_invariante_3_toda_linha_reservada_aponta_modalidade_do_proprio_perfil():
    alheia = perfil(
        vacancyTable=[linha(4, "aaaaaaaa-0000-4000-8000-0000000005ff")],
    )

    with pytest.raises(ProfileValidationError):
        validate_profiles([alheia])
    assert [item.code for item in do_quadro(alheia)] == ["vacancy_row_modality_missing"]


def test_invariante_3_uma_modalidade_tem_no_maximo_uma_linha():
    repetida = perfil(
        vacancyTable=[linha(4, PCD), linha(6, PCD, identidade=f"{PCD[:-1]}b")],
    )

    with pytest.raises(ProfileValidationError):
        validate_profiles([repetida])
    assert [item.code for item in do_quadro(repetida)] == ["vacancy_modality_row_duplicated"]


# --- 4 · toda linha publicada é alcançável por identidade, e nenhuma por posição (FR-170) ----


def test_invariante_4_a_colecao_e_enderecada_por_identidade_e_nunca_por_posicao():
    assert colecoes.tem_chave("/profiles/*/vacancyTable")
    assert not colecoes.e_atomica("/profiles/*/vacancyTable")


# --- 5 · quadro ausente nunca significa zero (D-005, FR-159) ---------------------------------


def test_invariante_5_quadro_ausente_nunca_significa_zero():
    """A conversão escreve lista **vazia**, e nenhum caminho lê ausência como `0`."""
    assert DEGRAUS_DE_PERFIL[12] == {"vacancyTable": []}
    assert do_quadro(perfil()) == [], "Perfil sem quadro continua publicável"
    assert do_quadro(perfil(vacancyTable=[linha(4, PCD)])) == [], "quadro parcial é legítimo"


# --- 6 · a soma nunca excede o total de vagas imediatas do Perfil (FR-177) -------------------


def test_invariante_6_a_soma_nunca_excede_o_total():
    excedente = perfil(vacancyTable=[linha(4, PCD), linha(200, PPI, identidade=f"{PPI[:-1]}b")])

    assert [item.code for item in do_quadro(excedente)] == ["vacancy_sum_exceeds_total"]


# --- 7 · nenhum valor publicado é reescrito por esta feature (FR-165, FR-173, D-001) ---------


def test_invariante_7_o_quadro_nao_e_publicavel_como_anexo_binario():
    """Nenhum caminho oferece o quadro como anexo: nem na composição, nem na Retificação, nem no
    documento (FR-165, D-001).

    Publicado como binário, o quadro não seria legível por máquina — e publicação é ato imutável,
    de modo que o Edital que o publicasse assim ficaria assim para sempre. Não seria migração
    adiada, e sim bifurcação permanente do acervo.
    """
    suspeitas = re.compile(r"(quadro|vacancy)[^\n]{0,60}(anexo|attachment|artefato|artifact)", re.I)
    infratores = [
        f"{caminho}:{numero}"
        for caminho, fonte in fontes().items()
        for numero, texto in enumerate(fonte.splitlines(), 1)
        # A prosa que **recusa** o anexo é legítima e cita os dois termos de propósito.
        if suspeitas.search(texto) and not texto.lstrip().startswith(("#", '"', "*"))
    ]

    assert infratores == [], f"o quadro tratado como anexo binário: {infratores}"


# --- 8 · nenhuma tela desta feature atribui pessoa a linha do quadro (FR-175) ----------------


def test_invariante_8_nenhuma_tela_atribui_pessoa_a_linha_do_quadro():
    """A feature **declara** o quadro. Não o ocupa, não o consome e não convoca por ele.

    É o corte que a spec repete duas vezes, e o mais tentador de violar: não existe caminho de
    escrita entre `Inscricao` e a linha, e nenhum módulo do quadro conhece inscrição, ordenação ou
    convocação.
    """
    pessoa = re.compile(
        r"(LinhaDoQuadroDeVagas|quadro_de_vagas|vacancyTable)[^\n]{0,80}"
        r"(Inscricao|inscricao|candidato|AtoDeOrdenacao|convoca)"
    )
    infratores = [
        f"{caminho}:{numero}"
        for caminho, fonte in fontes().items()
        for numero, texto in enumerate(fonte.splitlines(), 1)
        if pessoa.search(texto)
    ]

    assert infratores == [], f"pessoa atribuída a linha do quadro: {infratores}"


def test_invariante_8_o_ato_de_ordenacao_nao_e_tocado_por_esta_feature():
    """`sorteios/` não é tocado: reconciliar as duas grafias da ampla concorrência é outra feature.

    A §7 da spec põe isso fora de escopo, e este teste é o que impede a tentação de resolvê-lo de
    passagem — o ato de ordenação continua exatamente como estava.
    """
    do_sorteio = (CODIGO / "sorteios").rglob("*.py")
    infratores = [
        str(caminho)
        for caminho in do_sorteio
        if "vacancyTable" in caminho.read_text(encoding="utf-8")
        or "quadro_de_vagas" in caminho.read_text(encoding="utf-8")
    ]

    assert infratores == [], f"a `025` tocou o domínio do sorteio: {infratores}"
