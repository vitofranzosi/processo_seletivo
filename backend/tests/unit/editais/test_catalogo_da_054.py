"""O catálogo da 054 e a numeração de uma regra só (FR-980 a FR-985; SC-361, SC-362, SC-363).

O que estes testes protegem: que as seções do 28/2026 — o Edital do teste operacional — têm lugar
no catálogo; que a textual vazia não sai no documento e não abre buraco na numeração; que o
documento só publica texto que alguém escreveu; e que o número que as telas mostram é o que o
documento imprime, porque sai da mesma função.
"""

import re

import pytest

from processo_seletivo.editais.domain import secoes
from processo_seletivo.publicacoes.infrastructure.pdf import MODO_PREVIA, numeracao
from tests.unit.publicacoes.test_pdf import documento, snapshot, texto_de

# As 15 seções numeradas do Edital 28/2026, e a entrada do catálogo que recebe cada uma (research,
# R-001). Os títulos são os do original, em caixa alta como ele os imprime.
SECOES_DO_28_2026 = {
    "INFORMAÇÕES GERAIS": "informacoes-gerais",
    "PÚBLICO-ALVO": "publico-alvo",
    "REQUISITOS": "requisitos-gerais",
    "VAGAS": "perfis",
    "INSCRIÇÕES": "inscricao",
    "DA VERIFICAÇÃO DA VERACIDADE DA AUTODECLARAÇÃO": "verificacao-autodeclaracao",
    "DO PROCEDIMENTO COMPLEMENTAR DE VERIFICAÇÃO DA AUTODECLARAÇÃO": "verificacao-autodeclaracao",
    "PROCESSO SELETIVO": "classificacao",
    "RECURSO": "recursos",
    "MATRÍCULA NO CURSO": "matricula",
    "ACESSO E INFORMAÇÕES SOBRE O CURSO": "acesso-ao-curso",
    "HOMOLOGAÇÃO DA MATRÍCULA": "homologacao-matricula",
    "CERTIFICADO": "certificado",
    "DA ENTREVISTA DOS CANDIDATOS INSCRITOS COMO PESSOA COM DEFICIÊNCIA": "atendimento-pcd",
    "DISPOSIÇÕES FINAIS": "disposicoes-finais",
}


def _com_textos(**textos):
    """O snapshot da suíte do compositor, com as textuais vazias salvo as dadas."""
    base = snapshot()
    for secao in base["sections"]:
        if secao["type"] == secoes.TEXTUAL:
            secao["content"] = textos.get(secao["key"].replace("-", "_"), "")
    return base


def _titulos_numerados(texto):
    """Os títulos de seção: o número, e um texto todo em caixa alta."""
    return [
        (numero, titulo)
        for numero, titulo in re.findall(r"^(\d+)\. (.+)$", texto, re.M)
        if titulo == titulo.upper()
    ]


def test_as_quinze_secoes_do_28_2026_tem_lugar_no_catalogo():
    """SC-361: 15 de 15, e na ordem do original, salvo a entrevista PcD (R-001)."""
    assert len(SECOES_DO_28_2026) == 15
    assert set(SECOES_DO_28_2026.values()) <= set(secoes.POR_CHAVE)

    ordem = [secoes.POR_CHAVE[chave].order for chave in SECOES_DO_28_2026.values()]
    sem_a_entrevista = [
        secoes.POR_CHAVE[chave].order
        for titulo, chave in SECOES_DO_28_2026.items()
        if chave != "atendimento-pcd"
    ]
    assert sem_a_entrevista == sorted(sem_a_entrevista)
    assert len(ordem) == 15


def test_a_oferta_vem_antes_da_inscricao():
    assert secoes.POR_CHAVE["perfis"].order < secoes.POR_CHAVE["inscricao"].order


def test_a_textual_vazia_nao_sai_e_a_numeracao_nao_abre_buraco():
    """FR-982 e FR-985, com textuais e geradas vazias intercaladas."""
    conteudo = _com_textos(
        apresentacao="A Diretora do Cefor faz saber.",
        publico_alvo="Graduados em qualquer área.",
        certificado="Certificado a quem for aprovado.",
        disposicoes_finais="Os casos omissos serão avaliados pela Comissão.",
    )
    conteudo["stages"] = []  # a gerada vazia, entre as textuais
    texto = texto_de(documento(conteudo))

    numerados = _titulos_numerados(texto)
    assert [int(numero) for numero, _ in numerados] == list(range(1, len(numerados) + 1))
    titulos = [titulo for _, titulo in numerados]
    assert "PÚBLICO-ALVO" in titulos
    assert "DO CERTIFICADO" in titulos
    assert "DA MATRÍCULA" not in titulos
    assert "ETAPAS DE AVALIAÇÃO" not in titulos
    assert "INFORMAÇÕES GERAIS SOBRE O CURSO" not in titulos


def test_o_edital_intocado_nao_publica_texto_que_ninguem_escreveu():
    """SC-362: sem nada escrito, só as geradas e os metadados do ato saem."""
    texto = texto_de(documento(_com_textos()))

    for secao in secoes.CATALOGO:
        if not secao.gerada:
            assert f". {secao.title.upper()}" not in texto, secao.key
    # As frases das redações padrão de antes da 054, nenhuma delas.
    for frase in (
        "O Instituto Federal do Espírito Santo, por meio",
        "observará a pontuação obtida nas Etapas",
        "resolvidos pela autoridade responsável pelo processo seletivo",
    ):
        assert frase not in texto


@pytest.mark.parametrize(
    "textos",
    [
        {},
        {"apresentacao": "Preâmbulo."},
        {"inscricao": "Pelo sistema.", "matricula": "Na secretaria."},
        {
            chave.replace("-", "_"): "Texto."
            for chave in secoes.CHAVES_TEXTUAIS
            if chave not in ("publico-alvo", "convocacao")
        },
    ],
    ids=["nada", "so-o-preambulo", "duas", "quase-todas"],
)
def test_a_numeracao_das_telas_e_a_que_o_documento_imprime(textos):
    """SC-363: `numeracao` é a regra das telas, e o documento imprime o mesmo número."""
    conteudo = _com_textos(**textos)
    numeros = numeracao(conteudo)
    impressos = {
        titulo: int(numero)
        for numero, titulo in _titulos_numerados(texto_de(documento(conteudo, modo=MODO_PREVIA)))
    }

    for secao in conteudo["sections"]:
        numero = numeros[secao["key"]]
        titulo = secao["title"].upper()
        if numero is None or numero == 0:
            assert titulo not in impressos, secao["key"]
        else:
            assert impressos.get(titulo) == numero, secao["key"]
    assert numeros["apresentacao"] == (0 if textos.get("apresentacao") else None)
