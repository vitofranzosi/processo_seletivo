"""Regressões A1 e escopos A2, exclusivamente em memória e com rede/processos simulados."""

import copy
import importlib.util
from pathlib import Path
import unittest

ORIGEM = Path(__file__).resolve().parents[1] / "correcao-a1/test_guardas_puras.py"
spec = importlib.util.spec_from_file_location("testes_anteriores_a1", ORIGEM)
anterior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(anterior)
politica = anterior.operador.validar_escopo.__globals__


class GuardasA2(anterior.GuardasPuras):
    def aprovacao(self):
        documento = super().aprovacao()
        documento["revisao_operador"] = politica["REVISAO"]
        documento["escopo"] = copy.deepcopy(politica["ESCOPOS"]["inspecionar"])
        documento["cenarios"] = []
        return documento

    def test_escopo_positivo_de_cada_acao_preparada(self):
        for acao, escopo in politica["ESCOPOS"].items():
            documento = self.aprovacao()
            documento["acoes"] = [acao]
            documento["escopo"] = copy.deepcopy(escopo)
            anterior.operador.validar_escopo(acao, documento)

    def test_autorizacao_nao_acumula_duas_acoes_preparadas(self):
        documento = self.aprovacao()
        documento["acoes"].append("criar-recursos")
        with self.assertRaises(RuntimeError):
            anterior.operador.validar_escopo("inspecionar", documento)

    def test_recurso_adicional_recusado(self):
        documento = self.aprovacao()
        documento["escopo"]["recursos"].append("base-desenvolvimento-ficticia")
        with self.assertRaises(RuntimeError):
            anterior.operador.validar_escopo("inspecionar", documento)

    def test_efeito_implicito_start_na_criacao_recusado(self):
        documento = self.aprovacao()
        documento["acoes"] = ["criar-recursos"]
        documento["escopo"] = copy.deepcopy(politica["ESCOPOS"]["criar-recursos"])
        documento["escopo"]["operacoes"].append("container.postgres-iniciar")
        with self.assertRaises(RuntimeError):
            anterior.operador.validar_escopo("criar-recursos", documento)

    def test_efeito_omitido_recusado(self):
        documento = self.aprovacao()
        documento["escopo"]["operacoes"] = []
        with self.assertRaises(RuntimeError):
            anterior.operador.validar_escopo("inspecionar", documento)

    def test_duplicacao_e_curinga_recusados(self):
        for valor in ("engine.ler-identidade", "*"):
            documento = self.aprovacao()
            documento["escopo"]["operacoes"].append(valor)
            with self.assertRaises(RuntimeError):
                anterior.operador.validar_escopo("inspecionar", documento)

    def test_cenario_nao_e_grant_de_sessao(self):
        documento = self.aprovacao()
        documento["cenarios"] = ["P01-A"]
        with self.assertRaises(RuntimeError):
            anterior.operador.validar_escopo("inspecionar", documento)

    def test_dependencia_nao_torna_operacao_implementada(self):
        for acao in set(politica["DEPENDENCIAS"]) - set(politica["ESCOPOS"]):
            documento = self.aprovacao()
            documento["acoes"] = [acao]
            with self.assertRaises(RuntimeError):
                anterior.operador.validar_escopo(acao, documento)

    def test_grafo_valido_e_ciclo_ou_referencia_ausente_recusados(self):
        validar = politica["validar_grafo"]
        validar(politica["DEPENDENCIAS"])
        for grafo in ({"a": ["a"]}, {"a": ["b"]}, {"a": ["b"], "b": ["a"]}):
            with self.assertRaises(RuntimeError):
                validar(grafo)

    def test_acoes_preparadas_correspondem_ao_operador(self):
        self.assertEqual(set(politica["ESCOPOS"]), anterior.operador.PERMITIDAS)
        self.assertFalse(set(politica["ESCOPOS"]) & anterior.operador.BLOQUEADAS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
