"""Guardas do que a 015 deliberadamente não faz, e da regra de pesos não normalizados."""

from pathlib import Path

from processo_seletivo.classificacao.domain.combinacao import combinar


def test_pesos_nao_precisam_somar_um():
    marco = {
        "stages": ["a", "b"],
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
    raiz = Path(__file__).resolve().parents[2] / "processo_seletivo"
    emissao = (raiz / "classificacao" / "application" / "emissao.py").read_text()
    urls_do_portal = (raiz / "portal" / "urls.py").read_text()

    assert "Vaga" not in emissao
    assert "corte" not in emissao.casefold()
    assert "ordenacao" not in urls_do_portal
    assert "classificacao" not in urls_do_portal
