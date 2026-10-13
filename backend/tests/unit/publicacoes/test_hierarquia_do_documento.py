"""A hierarquia tipográfica do Edital (069, FR-1382, contrato do documento §6).

- título de seção em 12,5 pt, negrito, com um fio fino abaixo;
- subseção em 11 pt, negrito;
- rótulo de grupo em negrito, no corpo do texto;
- item de lista com o marcador na margem e a continuação alinhada à primeira palavra (ED-16);
- bloco destacado — fundo cinza 0,95 e contorno — para os dados do sorteio e a declaração do
  Requerimento (e o resumo, na apresentação por perguntas);
- nenhuma informação dependendo de cor: só cinza.

A forma é afirmada sobre o arquivo composto, onde ela existe: o corpo e a fonte de cada linha, a
posição dela, e os traços desenhados.
"""

import re

from processo_seletivo.publicacoes.infrastructure import fonte, pdf
from tests.unit.publicacoes.test_pdf import documento, snapshot
from tests.unit.publicacoes.test_pdf_classificacao import ETAPAS, marco

DESENHADA = re.compile(rb"BT (?:[\d.]+ Tw )?/(F\d) ([\d.]+) Tf ([\d.]+) ([\d.]+) Td \((.*?)\) Tj")
FLUXO = re.compile(rb"<< /Length \d+ >>\nstream\n(.*?)\nendstream", re.DOTALL)
SEGMENTO = re.compile(rb"([\d.]+) ([\d.]+) m ([\d.]+) ([\d.]+) l S")
CAIXA = re.compile(rb"0\.95 g ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) re f")


def _paginas(pdf_):
    return FLUXO.findall(pdf_)


def _linhas(fluxo):
    return [
        (texto.decode("cp1252"), recurso.decode(), float(corpo), float(x), float(y))
        for recurso, corpo, x, y, texto in DESENHADA.findall(fluxo)
    ]


def _completo():
    sorteio = marco(
        code="SORT",
        name="Sorteio público",
        orderProduction="POR_SORTEIO",
        stages=[],
        tiebreakers=[],
        appealWindow={"admits": True, "durationDays": 2, "unit": "DIAS_CORRIDOS"},
        drawMethod={
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
        },
    )
    conteudo = snapshot(stages=ETAPAS)
    perfil = conteudo["profiles"][0]
    perfil["classificationMilestones"] = [sorteio]
    perfil["requirements"] = [
        "Graduação em qualquer área, com diploma registrado e reconhecido pelo Ministério da "
        "Educação, e experiência mínima de um ano em docência na educação a distância, comprovada",
        "Disponibilidade",
    ]
    conteudo["matriculationRequest"] = {
        "moment": "AT_ENROLLMENT",
        "declarationText": "Declaro que as informações prestadas são verdadeiras.",
    }
    return conteudo


def test_o_titulo_de_secao_e_maior_negrito_e_tem_um_fio_abaixo():
    pdf_ = documento(_completo())
    for fluxo in _paginas(pdf_):
        titulos = [
            linha
            for linha in _linhas(fluxo)
            if re.match(r"^\d+\. \S", linha[0]) and linha[1] == pdf.NEGRITO
        ]
        segmentos = [tuple(map(float, s)) for s in SEGMENTO.findall(fluxo)]
        for texto, _, corpo, _, y in titulos:
            assert corpo == pdf.CORPO_TITULO_DE_SECAO, texto
            assert any(
                x1 == pdf.MARGEM and x2 == pdf.LARGURA - pdf.MARGEM and 0 < y - y1 <= 6
                for x1, y1, x2, _ in segmentos
            ), f"sem fio abaixo de {texto!r}"


def test_a_subsecao_e_negrito_de_onze_pontos():
    linhas = [linha for fluxo in _paginas(documento(_completo())) for linha in _linhas(fluxo)]
    subsecoes = [linha for linha in linhas if re.match(r"^\d+\.\d+ \S", linha[0])]
    assert subsecoes
    for texto, recurso, corpo, _, _ in subsecoes:
        assert (recurso, corpo) == (pdf.NEGRITO, pdf.CORPO_SUBSECAO), texto


def test_o_rotulo_de_grupo_e_negrito_no_corpo_do_texto():
    linhas = [linha for fluxo in _paginas(documento(_completo())) for linha in _linhas(fluxo)]
    for rotulo in ("Regras de classificação", "Requisitos", "Sorteio", "Recurso"):
        (encontrada,) = [linha for linha in linhas if linha[0] == rotulo]
        assert (encontrada[1], encontrada[2]) == (pdf.NEGRITO, pdf.CORPO_TEXTO), rotulo


def test_o_item_de_lista_continua_alinhado_ao_texto_e_nao_ao_marcador():
    """ED-16: a segunda linha do requisito começa sob a primeira palavra, e não sob o "•"."""
    linhas = [linha for fluxo in _paginas(documento(_completo())) for linha in _linhas(fluxo)]
    indice = next(i for i, linha in enumerate(linhas) if linha[0].startswith("• Graduação"))
    primeira, segunda = linhas[indice], linhas[indice + 1]
    pendente = fonte.METRICA.largura("• ", pdf.CORPO_TEXTO)
    assert abs(segunda[3] - (primeira[3] + pendente)) < 0.1


def test_os_dados_do_sorteio_e_a_declaracao_saem_em_bloco_destacado():
    """Fundo 0,95 com contorno, desenhado antes do texto, em volta de cada um."""
    pdf_ = documento(_completo())
    destacados = {"Sorteio": False, "Declaro que as informações": False}
    for fluxo in _paginas(pdf_):
        caixas = [tuple(map(float, c)) for c in CAIXA.findall(fluxo)]
        for texto, _, _, _, y in _linhas(fluxo):
            for inicio in destacados:
                if texto.startswith(inicio) and any(
                    base <= y <= base + altura for _, base, _, altura in caixas
                ):
                    destacados[inicio] = True
        primeiro_texto = fluxo.find(b"BT ")
        for caixa in CAIXA.finditer(fluxo):
            assert caixa.start() < primeiro_texto, "o fundo vem antes do texto"
    assert all(destacados.values()), destacados


def test_nenhuma_informacao_depende_de_cor():
    """Só tons de cinza (`g`/`G`): nenhum operador de cor RGB ou CMYK no desenho das páginas."""
    for fluxo in _paginas(documento(_completo())):
        # O que está dentro de `( … ) Tj` é texto, e pode ter "k" — sai antes da varredura.
        desenho = re.sub(rb"\((?:\\.|[^\\)])*\) Tj", b"", fluxo)
        assert not re.search(rb"\b(rg|RG|k|K|sc|SC|scn|SCN)\b", desenho)
