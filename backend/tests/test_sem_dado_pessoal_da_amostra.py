"""A linha real da planilha não foi copiada para lugar nenhum deste repositório (`SC-137`).

**A investigação desta feature leu dado de uma pessoa real.** A linha `2` da planilha de importação
do Registro Acadêmico traz nome, CPF, RG, e-mail, filiação, endereço, CEP, telefone e título
eleitoral de uma candidata. O achado que a investigação produziu é sobre a **forma** daquele dado —
quais colunas existem, o que cada uma significa, onde o formato diverge do que se coleta. Um achado
sobre qualidade de dado não precisa do dado para ser verdadeiro.

**O que esta varredura alcança são quatro alvos, e não dois.** A `SC-137` nomeia spec, documento de
descoberta, **teste e fixture** — e varrer só os dois primeiros deixaria de fora exatamente onde um
valor de exemplo é copiado sem pensar: "vou usar um CPF de verdade na fixture, é mais realista".

**E o teste não contém o que procura.** Guardar o CPF, o CEP e o nome em claro aqui para varrê-los
faria dele o vazamento que ele existe para impedir — um arquivo versionado, lido por qualquer pessoa
com acesso ao repositório, com o dado que a própria feature trata com cuidado. O que está abaixo são
**resumos `sha256` de valores normalizados**; os originais permanecem fora da árvore, junto com a
planilha, como a §0 da descoberta registra.

**Resumo compara, e não revela.** Saber que um CPF resume para `309171…` não permite reconstituí-lo,
mas permite reconhecê-lo se ele aparecer — que é exatamente o que se quer. A normalização é o que
faz o reconhecimento sobreviver à formatação: `123.456.789-00` e `12345678900` são o mesmo CPF, e
`MARIA DA SILVA` é o mesmo nome que `Maria da Silva`.
"""

import hashlib
import re
import unicodedata
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
BACKEND = RAIZ / "backend"

# **Os resumos, nomeados pela coluna de origem** — o nome da coluna é a forma do dado, e é público;
# o valor não. `CPF` e `RG` compartilham o resumo porque **na linha real as duas colunas trazem o
# mesmo valor**: é um achado de qualidade do dado de origem, registrado aqui porque é onde ele ficou
# visível, e que não vira escopo desta feature.
#
# Duas famílias, porque duas normalizações: o que é identificado por **dígitos** sobrevive a
# pontuação; o que é **texto** sobrevive a acento e a caixa.
POR_DIGITOS = {
    "CPF / RG": "309171fc7bf5d7e1e5e8700e8d8020851e0e4b21372f96cde904e28c0eb9a237",
    "CEP": "ffbcd2486e338b073eb0f06a370235f47a819ce514336cec300bec2cf4a4244b",
    "CELULAR": "b7296261a18cc2365cde31345f07cfd01f878c13caeba76059610aaf8142e750",
    "TITULO_ELE": "f787321c868ac1924f56f85be086ceff4e6f1c6b52b5ed07aa7d602cf952be21",
    "DATA_NASCIMENTO": "b788797590c185eda0cf5e43da92e4bbe56c1db06e552e5d3aedcc0464928149",
    "IDENTIDADE_DATA": "016ecdea5be81c1c32f161634484f65b2ce63d23de8b0074cb9137894bf15868",
}

POR_TEXTO = {
    "NOME": "533308810c15c4b90292653bf9847e2e39eda9bcb0e2fe39161893dbed9d028d",
    "EMAIL": "11d2e5e9a1c592f6616a0f1825494b2d7d2959bdf44216ac3f11d95716da3d36",
    "NOME_MAE": "925eaaff8c2fa7c89fdf09f062272979b74f398e6cdc835c0ef05155932796e4",
    "NOME_PAI": "01a9174ddce55a60db7625b2a0da36b741eb5bbe4e9ff86ed00586a2a28425b7",
    "ENDERECO": "13442e2073434b65a226416c0dd30f7d935df89d0f58afb9fd6c315415e5b367",
    "BAIRRO": "6df526bd23eaf7f8ebee891ad3be57419ab53563b84f5158c06088704e9d8eca",
    "COMPLEMENTO": "93006b44f9f50f18e1b36555bdd70b6d8b16010ac48c1354d2d25e97a935ee26",
    "EMISSOR": "c1a31f0e4a4549637c8c7a4a9a4ef9b60bf617d21cab755fa8aea34ac745a6e6",
}

# Até quantas palavras seguidas formam um candidato. **Oito, e não seis**: o nome da linha real tem
# **seis** palavras, e uma janela de seis o alcançaria justamente no limite — o primeiro nome
# composto a mais escaparia da varredura sem que nada acusasse. Oito dá a folga, e o custo continua
# linear no tamanho do arquivo vezes a janela.
MAIOR_JANELA = 8
# Abaixo disto, um "identificador" é ruído: sete dígitos é o menor documento que interessa.
MENOR_NUMERO = 7


# **A mesma expressão dos dois lados.** Os resumos guardados abaixo são de valores tokenizados por
# ela: um complemento como `casa/fundos` vira `casa fundos`, e guardar o resumo da forma **não**
# tokenizada faria a varredura procurar uma cadeia que ela nunca produz — passando calada sobre o
# valor que existe para encontrar. Foi o que aconteceu na primeira redação, e só apareceu porque a
# conferência contra a planilha real foi feita antes de fechar.
TOKENS = re.compile(r"[\wÀ-ÿ@.\-]+")


def normalizar(valor: str) -> str:
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", valor) if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"\s+", " ", sem_acento).strip().lower()


def resumo(valor: str) -> str:
    return hashlib.sha256(valor.encode("utf-8")).hexdigest()


def numeros_do(texto: str) -> set:
    """Todo número longo do arquivo, com a pontuação removida.

    `123.456.789-00` e `12345678900` viram a mesma coisa: é o que faz o reconhecimento sobreviver à
    formatação com que alguém copiaria o valor.
    """
    encontrados = set()
    for bruto in re.findall(r"[\d][\d.\-/ ]{5,}[\d]|\d{7,}", texto):
        digitos = "".join(c for c in bruto if c.isdigit())
        if len(digitos) >= MENOR_NUMERO:
            encontrados.add(digitos)
            # Datas escritas por extenso ou em ISO perdem separador e viram um número só; o
            # inverso — o número colado — também precisa ser reconhecido.
            for tamanho in (8, 11):
                if len(digitos) > tamanho:
                    encontrados.update(
                        digitos[i : i + tamanho] for i in range(len(digitos) - tamanho + 1)
                    )
    return encontrados


def trechos_de(texto: str) -> set:
    """Todas as sequências de até `MAIOR_JANELA` palavras, normalizadas.

    Uma varredura por linha inteira não acharia nada: ninguém copia a linha da planilha: copia o
    **nome**, no meio de uma frase. É a janela deslizante que o encontra ali.
    """
    palavras = TOKENS.findall(normalizar(texto))
    janelas = set()
    for inicio in range(len(palavras)):
        for fim in range(inicio + 1, min(inicio + MAIOR_JANELA, len(palavras)) + 1):
            janelas.add(" ".join(palavras[inicio:fim]))
    return janelas


def arquivos_varridos():
    """Os quatro alvos da `SC-137`: spec, descoberta, **teste e fixture**."""
    alvos = sorted(
        {
            *(RAIZ / "specs").glob("029-*/**/*.md"),
            *(RAIZ / "doc").glob("descoberta-029-*.md"),
            *(BACKEND / "tests").rglob("*.py"),
        }
    )
    return [caminho for caminho in alvos if "__pycache__" not in caminho.parts]


def test_a_varredura_encontra_o_que_deveria_varrer():
    """Renomear uma pasta não pode transformar a garantia em silêncio aprovado."""
    varridos = arquivos_varridos()
    nomes = {caminho.name for caminho in varridos}

    assert len(varridos) > 200, f"a varredura encolheu para {len(varridos)} arquivos"
    assert "spec.md" in nomes, "a spec da feature precisa estar no alcance"
    assert "descoberta-029-requerimento-de-matricula.md" in nomes
    assert any("fixtures" in caminho.parts for caminho in varridos), "as fixtures também"


@pytest.mark.parametrize("caminho", arquivos_varridos(), ids=lambda p: p.name)
def test_nenhum_dado_da_linha_real_aparece(caminho):
    texto = caminho.read_text(encoding="utf-8", errors="ignore")
    resumos_de_numero = {resumo(n) for n in numeros_do(texto)}
    resumos_de_texto = {resumo(t) for t in trechos_de(texto)}

    achados = [
        f"{coluna} da linha 2 da planilha"
        for coluna, esperado in POR_DIGITOS.items()
        if esperado in resumos_de_numero
    ] + [
        f"{coluna} da linha 2 da planilha"
        for coluna, esperado in POR_TEXTO.items()
        if esperado in resumos_de_texto
    ]

    assert achados == [], (
        f"{caminho.name} reproduz dado pessoal da amostra: {', '.join(achados)}. "
        "O achado é sobre a forma do dado, e não precisa do dado para ser verdadeiro — "
        "substitua por um valor inventado."
    )


class TestAVarreduraEnxergaOQueProcura:
    """**Uma varredura que nunca acusa aprova tudo, calada.** Estes dois provam que ela acusa.

    Eles constroem um valor **sintético** cujo resumo é conhecido, e verificam que a mecânica o
    encontra — sem tocar em nenhum valor real.
    """

    def test_um_numero_formatado_e_reconhecido_apesar_da_pontuacao(self, tmp_path):
        arquivo = tmp_path / "sintetico.md"
        arquivo.write_text("O CEP informado foi 29.040-860 na ficha.", encoding="utf-8")

        encontrados = {resumo(n) for n in numeros_do(arquivo.read_text())}

        assert resumo("29040860") in encontrados

    def test_um_nome_e_reconhecido_apesar_do_acento_e_da_caixa(self, tmp_path):
        arquivo = tmp_path / "sintetico.md"
        arquivo.write_text("A candidata MARIA DA SILVA ÁVILA assinou.", encoding="utf-8")

        encontrados = {resumo(t) for t in trechos_de(arquivo.read_text())}

        assert resumo("maria da silva avila") in encontrados

    def test_um_valor_que_nao_esta_no_arquivo_nao_e_encontrado(self, tmp_path):
        """O complemento simétrico: sem ele, uma varredura que acusasse tudo passaria igual."""
        arquivo = tmp_path / "sintetico.md"
        arquivo.write_text("Nada de pessoal aqui.", encoding="utf-8")

        encontrados = {resumo(t) for t in trechos_de(arquivo.read_text())}

        assert resumo("maria da silva avila") not in encontrados


def test_este_arquivo_nao_guarda_valor_em_claro():
    """O teste não pode ser o vazamento que ele existe para impedir.

    A asserção é frágil de propósito: ela conta os resumos e confere que cada um tem **exatamente**
    sessenta e quatro caracteres hexadecimais. Um valor colado por engano no lugar de um resumo —
    um CPF, um nome — não passa por essa forma.
    """
    corpo = Path(__file__).read_text(encoding="utf-8")
    declarados = re.findall(r'"([0-9a-f]{64})"', corpo)

    assert len(declarados) == len(POR_DIGITOS) + len(POR_TEXTO)
    assert set(declarados) == set(POR_DIGITOS.values()) | set(POR_TEXTO.values())
