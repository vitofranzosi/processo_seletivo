"""Guardas do que a 015 deliberadamente não faz, e da regra de pesos não normalizados."""

import re
from pathlib import Path

from processo_seletivo.classificacao.domain.combinacao import combinar


def test_pesos_nao_precisam_somar_um():
    marco = {
        "stages": ["a", "b"],
        "orderProduction": "POR_PONTUACAO",
        "operation": "SOMA_PONDERADA",
        "normalization": "NENHUMA",
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
    }
    etapas = {
        "a": {"id": "a", "forma": "PONTUADA", "weight": "2"},
        "b": {"id": "b", "forma": "PONTUADA", "weight": "3"},
    }

    assert combinar(marco, etapas, {"a": 10, "b": 20}) == 80


def test_a_classificacao_nao_cria_corte_vaga_nem_rota_para_candidato():
    """A fronteira da `015`: ela emite a ordem, e não corta, não conta vaga e não fala ao candidato.

    **A busca por `corte` passou a ter fronteira de palavra** (034). Ela era por substring, e
    "recorte" a contém — de modo que a palavra do domínio que nomeia o par (Perfil, Modalidade)
    reprovava um guarda que existe para outra coisa. Corrigir a busca **não** afrouxa o guarda:
    "corte", "cortes" e "Corte" continuam sendo acusados, e é só o falso positivo que sai.

    *Estreitar uma varredura merece desconfiança, e por isso a conferência está escrita:* as
    ocorrências de `corte` em `emissao.py` hoje são zero, e as de `recorte` são as da ordem por
    recorte — o teste abaixo prova que a expressão nova ainda enxerga o termo proibido.
    """
    raiz = Path(__file__).resolve().parents[2] / "processo_seletivo"
    emissao = (raiz / "classificacao" / "application" / "emissao.py").read_text()
    urls_do_portal = (raiz / "portal" / "urls.py").read_text()

    assert "Vaga" not in emissao
    assert not re.search(r"\bcorte", emissao.casefold())
    assert "ordenacao" not in urls_do_portal
    assert "classificacao" not in urls_do_portal


def test_a_varredura_do_corte_distingue_corte_de_recorte():
    """Uma expressão que deixa de casar não falha: ela aprova tudo, calada.

    É a mesma precaução que `test_vocabulario_do_corte.py` toma com os termos dele, e ela vale ainda
    mais para uma expressão que acabou de ser estreitada.
    """
    assert re.search(r"\bcorte", "emitir o corte da faixa")
    assert re.search(r"\bcorte", "Corte e progressão".casefold())
    assert re.search(r"\bcorte", "os cortes emitidos")
    assert not re.search(r"\bcorte", "a ordem deste recorte")
