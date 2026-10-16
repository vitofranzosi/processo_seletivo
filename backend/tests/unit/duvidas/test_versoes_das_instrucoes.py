"""As instruções são versionadas, e a versão anterior fica como foi (`FR-1515`).

Uma troca gravada com a versão 1 só se relê com o texto da versão 1; uma nota de qualidade não
atravessa versões. A versão 2 (14/10) fala ao candidato, e não ao setor de seleção; a 3, no mesmo
dia, só distingue explicação de citação literal; a 4 só acrescenta o alcance das regras.
"""

from processo_seletivo.duvidas.domain import mensagens


def test_a_versao_vigente_e_a_4_e_as_anteriores_ficam_guardadas():
    assert mensagens.VERSAO_DAS_INSTRUCOES == "4"
    assert set(mensagens.INSTRUCOES_ANTERIORES) == {"1", "2", "3"}
    anterior = mensagens.INSTRUCOES_ANTERIORES["1"]
    assert anterior != mensagens.INSTRUCOES
    assert anterior.startswith("Você explica um Edital publicado do Ifes a servidores do setor")


def test_a_2_mantem_as_regras_de_fundamentacao_da_1():
    """O que muda é a forma da resposta; responder só pelas fontes e citá-las continua igual."""
    regras = [
        linha
        for linha in mensagens.INSTRUCOES_ANTERIORES["1"].split("\n")
        if linha[:2] in {f"{n}." for n in range(1, 10)} or linha.startswith("10.")
    ]
    for regra in regras:
        assert regra in mensagens.INSTRUCOES, regra


def test_o_registro_da_conversa_vai_antes_da_pergunta():
    class Lido:
        numero, ano = "91", 2026

        class versao:
            identificador_curto = "abc"

    montadas = mensagens.montar(Lido, (), [], "Preciso enviar todos?", da_conversa="opção X.")

    assert [m["role"] for m in montadas.mensagens] == ["system", "user", "user", "user"]
    assert montadas.mensagens[2]["content"] == "Registrado pelo sistema nesta conversa: opção X."
    assert montadas.mensagens[3]["content"] == "Preciso enviar todos?"
    sem = mensagens.montar(Lido, (), [], "Preciso enviar todos?")
    assert len(sem.mensagens) == 3


def test_a_3_muda_so_a_distincao_entre_explicacao_e_citacao():
    """O dado calculado fundamenta a explicação, com a referência, e não é citação do Edital."""
    anterior, vigente = mensagens.INSTRUCOES_ANTERIORES["2"], mensagens.INSTRUCOES_ANTERIORES["3"]
    assert "a não ser numa citação literal" in anterior
    assert "a não ser numa citação literal" not in vigente
    regra = vigente.split("Explicação e citação:")[1]
    for natureza in ("Dado da versão vigente", "Calculado pelo sistema no instante"):
        assert natureza in regra
    assert 'Nunca as marque como "citacao"' in regra
    assert "A citação literal é opcional" in regra
    # Fora a regra 12 sem a frase e a seção nova, a 3 é a 2, palavra por palavra.
    sem_a_secao = vigente.split("\n\nExplicação e citação:")[0]
    assert sem_a_secao == anterior.replace(", a não ser numa citação literal.", ".")


def test_a_4_e_a_3_com_o_alcance_das_regras_e_nada_proprio_de_um_edital():
    """A regressão de 14/10 (`CB-17`, `CB-18`): a regra de um subgrupo estendida ao grupo todo."""
    anterior, vigente = mensagens.INSTRUCOES_ANTERIORES["3"], mensagens.INSTRUCOES
    antes, secao = vigente.split("\n\nAlcance das regras:\n")
    assert antes == anterior
    assert secao.startswith("21. Preserve o alcance de cada regra")
    assert "Não estenda uma exigência de um subgrupo ao grupo inteiro" in secao
    for proprio_de_um_edital in ("pretos", "indígena", "PPI", "autodeclaração"):
        assert proprio_de_um_edital not in secao
