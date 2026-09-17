"""As 34 colunas do formato de destino têm origem declarada — ou questão aberta nomeada.

`FR-403` manda **manter o mapa**, e a `SC-133` o verifica. O mapa vive em
`specs/029-requerimento-de-matricula/contrato-de-saida.md`, e este teste é o que impede que ele
envelheça em silêncio.

**Por que um mapa precisa de teste.** Um documento de correspondência é a coisa mais fácil de deixar
para trás: acrescenta-se um campo ao requerimento, e a linha correspondente não é escrita. O mapa
continua parecendo completo — ele não tem como acusar o que não sabe que falta. O que o prende é a
contagem: 34 colunas, e a conta por origem tem de fechar nelas.

**Onde não há regra, o mapa diz que não há — e isso é resposta, não lacuna.** Seis colunas não têm
fonte, e cada uma nomeia a questão aberta correspondente. Uma tabela de correspondência escrita de
memória produziria dado errado com aparência de dado certo, e o erro só apareceria no Registro
Acadêmico, depois da matrícula, com a pessoa no meio.
"""

import re
from pathlib import Path

import pytest

MAPA = (
    Path(__file__).resolve().parents[2] / "specs/029-requerimento-de-matricula/contrato-de-saida.md"
)

TOTAL_DE_COLUNAS = 34
SEM_FONTE = "**sem fonte**"


def linhas_da_tabela():
    """As linhas da tabela numerada — só as que começam por um número de ordem."""
    encontradas = []
    for linha in MAPA.read_text(encoding="utf-8").splitlines():
        if not linha.startswith("|"):
            continue
        celulas = [celula.strip() for celula in linha.strip("|").split("|")]
        if len(celulas) == 5 and celulas[0].isdigit():
            encontradas.append(
                {
                    "ordem": int(celulas[0]),
                    "coluna": celulas[1].strip("`"),
                    "origem": celulas[2],
                    "de_onde": celulas[3],
                    "ressalva": celulas[4],
                }
            )
    return encontradas


def test_o_mapa_existe_e_e_legivel():
    """Renomear o arquivo não pode transformar a garantia em silêncio aprovado."""
    assert MAPA.exists(), f"o mapa que a FR-403 manda manter não está em {MAPA}"


def test_sao_trinta_e_quatro_colunas_e_a_ordem_nao_tem_buraco():
    """A ordem é a da planilha: uma coluna esquecida no meio aparece como salto na numeração."""
    linhas = linhas_da_tabela()

    assert len(linhas) == TOTAL_DE_COLUNAS, f"o mapa descreve {len(linhas)} colunas"
    assert [linha["ordem"] for linha in linhas] == list(range(1, TOTAL_DE_COLUNAS + 1))


def test_nenhum_nome_de_coluna_se_repete():
    """Duas linhas para a mesma coluna esconderiam uma ausente atrás de uma duplicata."""
    nomes = [linha["coluna"] for linha in linhas_da_tabela()]

    assert len(set(nomes)) == TOTAL_DE_COLUNAS, f"nomes repetidos: {sorted(nomes)}"


@pytest.mark.parametrize("linha", linhas_da_tabela(), ids=lambda item: item["coluna"])
def test_cada_coluna_tem_origem_declarada_ou_ausencia_nomeada(linha):
    """Célula vazia é o defeito: ela não distingue *"não há fonte"* de *"ninguém olhou"*."""
    assert linha["origem"], f"{linha['coluna']}: origem em branco"
    assert linha["de_onde"], f"{linha['coluna']}: sem dizer de onde o valor sai"


@pytest.mark.parametrize("linha", linhas_da_tabela(), ids=lambda item: item["coluna"])
def test_coluna_sem_fonte_nomeia_a_questao_aberta(linha):
    """*"Sem fonte"* sozinho é lacuna; com a questão nomeada, é decisão registrada.

    A diferença aparece no dia em que alguém for implementar a exportação: ou ele encontra a
    pergunta que precisa levar a quem define o formato, ou encontra um espaço em branco e inventa
    uma resposta.
    """
    if SEM_FONTE not in linha["de_onde"]:
        return

    assert linha["origem"] == "—", "coluna sem fonte não pode declarar origem"
    assert re.search(r"`Q-\d+`", linha["ressalva"]), (
        f"{linha['coluna']}: sem fonte e sem questão aberta nomeada — "
        "quem for implementar a exportação não terá o que perguntar"
    )


def test_a_conta_por_origem_fecha_nas_trinta_e_quatro():
    """A tabela do resumo é o que envelhece primeiro: ela é escrita à mão e ninguém a recalcula."""
    linhas = linhas_da_tabela()
    contagem = {}
    for linha in linhas:
        chave = "sem fonte" if SEM_FONTE in linha["de_onde"] else linha["origem"]
        contagem[chave] = contagem.get(chave, 0) + 1

    declarado = {}
    for linha in MAPA.read_text(encoding="utf-8").splitlines():
        casado = re.match(r"\|\s*\**([\wç ]+?)\**\s*\|\s*\**(\d+)\**\s*\|$", linha.strip())
        if casado and casado.group(1).strip() != "Colunas":
            declarado[casado.group(1).strip()] = int(casado.group(2))

    total = declarado.pop("total", None)
    assert total == TOTAL_DE_COLUNAS, f"o resumo declara total {total}"
    assert sum(declarado.values()) == TOTAL_DE_COLUNAS, (
        f"as parcelas somam {sum(declarado.values())}"
    )
    assert declarado == contagem, (
        f"o resumo escrito à mão discorda da tabela: resumo={declarado}, tabela={contagem}"
    )


def test_a_divergencia_de_significado_esta_nomeada_onde_ela_acontece():
    """`R-7`: a coluna per capita recebe uma faixa que mede a soma da família.

    A decisão foi coletar como o formulário institucional já coleta e **nomear** a divergência — e
    o lugar dela é a linha da coluna, não só a prosa: quem for implementar lê a tabela.
    """
    renda = next(linha for linha in linhas_da_tabela() if linha["coluna"] == "RENDA_PER_CAPITA_PNP")

    assert "`R-7`" in renda["ressalva"]
    assert "soma da família" in renda["ressalva"]


def test_o_caminho_inverso_tambem_esta_mapeado():
    """O que se coleta e o destino **não** pede é a outra metade do mapa.

    Sem ela, alguém olharia `codigo_ibge` sem coluna correspondente e concluiria que sobra — quando
    o propósito dele é interno e demonstrado.
    """
    corpo = MAPA.read_text(encoding="utf-8")

    assert "## O caminho inverso" in corpo
    for campo in ("codigo_ibge", "uf_natal", "endereco_conferido_por_referencia"):
        assert f"`{campo}`" in corpo, f"{campo} é coletado e não tem coluna: precisa estar no mapa"
