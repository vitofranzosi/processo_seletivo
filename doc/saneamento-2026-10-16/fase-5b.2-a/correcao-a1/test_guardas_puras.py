"""Testes em memória: sem banco, rede, Docker, temporários ou execução de main operacional."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

BASE = Path(__file__).resolve().parents[2] / "fase-5b.1"


def carregar(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


# Importar apenas módulos sem efeitos operacionais. Qualquer subprocesso/rede é erro.
with patch.object(subprocess, "run", side_effect=AssertionError("Subprocesso real proibido")), \
     patch.object(socket, "socket", side_effect=AssertionError("Rede proibida")):
    contrato = carregar("contrato_a1", BASE / "isolamento/contrato.py")
    sys.modules["contrato"] = contrato
    operador = carregar("operador_a1", BASE / "operar.py")


class GuardasPuras(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {}, clear=True)
        self.env.start()
        self.rede = patch.object(socket, "socket", side_effect=AssertionError("Rede proibida"))
        self.rede.start()
        self.processo = patch.object(subprocess, "run", side_effect=AssertionError("Processo real proibido"))
        self.execucao = self.processo.start()
        operador.DOCKER_ALVO = None

    def tearDown(self):
        self.processo.stop()
        self.rede.stop()
        self.env.stop()

    def test_docker_sem_autorizacao_nao_invoca_processo(self):
        with self.assertRaises(RuntimeError):
            operador.docker("info")
        self.execucao.assert_not_called()

    def test_acoes_bloqueadas_nao_leem_config_nem_invocam_docker(self):
        for acao in sorted(operador.BLOQUEADAS):
            with self.subTest(acao=acao), patch.object(sys, "argv", ["operar.py", acao]), \
                 patch.object(operador, "validar") as validar, patch.object(operador, "ler_json") as ler:
                with self.assertRaises(RuntimeError):
                    operador.main()
                validar.assert_not_called()
                ler.assert_not_called()
        self.execucao.assert_not_called()

    def test_autorizacao_antiga_recusada_antes_de_cliente(self):
        with self.assertRaises(RuntimeError):
            operador.autorizar("criar-recursos", {"revisao_operador": "5B.1"})
        self.execucao.assert_not_called()

    def aprovacao(self):
        return {"revisao_operador": "5B.2-A.1", "identidade": operador.IDENTIDADE,
                "acoes": ["inspecionar"], "aprovador": "responsavel-ficticio",
                "referencia_da_deliberacao": "teste-em-memoria",
                "manifesto_sha256": "a" * 64, "integridade_sha256": "a" * 64,
                "endpoint_local": "unix:///socket-ficticio", "cliente_sha256": "a" * 64}

    def autorizar_ficticio(self, documento):
        with patch.object(operador, "sha", return_value="a" * 64), \
             patch.object(operador, "sem_atalho"), patch.object(operador, "ler_json", return_value={}), \
             patch.object(Path, "is_dir", return_value=True), \
             patch.object(Path, "iterdir", return_value=iter([Path("config.json")])):
            return operador.autorizar("inspecionar", documento)

    def test_inspecao_pode_ser_aprovada_sem_imagem_ou_config_banco(self):
        cliente, endpoint = self.autorizar_ficticio(self.aprovacao())
        self.assertTrue(cliente.endswith("docker-cliente"))
        self.assertEqual(endpoint, "unix:///socket-ficticio")
        self.execucao.assert_not_called()

    def test_acao_extra_bloqueada_na_lista_recusa_documento(self):
        doc = self.aprovacao()
        doc["acoes"].append("esquema")
        with self.assertRaises(RuntimeError):
            self.autorizar_ficticio(doc)

    def test_endpoint_remoto_recusado(self):
        doc = self.aprovacao()
        doc["endpoint_local"] = "tcp://base-real:2375"
        with self.assertRaises(RuntimeError):
            self.autorizar_ficticio(doc)

    def test_hash_divergente_recusado(self):
        doc = self.aprovacao()
        doc["manifesto_sha256"] = "b" * 64
        with self.assertRaises(RuntimeError):
            self.autorizar_ficticio(doc)

    def test_falha_de_comunicacao_e_permissao_nunca_e_ausencia(self):
        operador.DOCKER_ALVO = ("cliente-ficticio", "unix:///socket-ficticio")
        for codigo in (1, 125, 126):
            with self.subTest(codigo=codigo):
                self.execucao.side_effect = None
                self.execucao.return_value = Mock(returncode=codigo, stdout="", stderr="erro ficticio")
                with self.assertRaises(RuntimeError):
                    operador.nomes("container")

    def test_inventario_vazio_valido_nao_e_inspect_com_erro(self):
        with patch.object(operador, "docker", return_value=""):
            self.assertEqual(operador.nomes("container"), set())

    def test_inventario_positivo(self):
        with patch.object(operador, "docker", return_value='"um"\n"dois"'):
            self.assertEqual(operador.nomes("volume"), {"um", "dois"})

    def test_inventario_incompleto_ambiguo_nulo_recusado(self):
        for saida in ('"incompleto', 'null', '"um"\n"um"', '{}'):
            with self.subTest(saida=saida), patch.object(operador, "docker", return_value=saida):
                with self.assertRaises((RuntimeError, json.JSONDecodeError)):
                    operador.nomes("network")

    def test_metadata_nula_recusada(self):
        with patch.object(operador, "docker", return_value="null"):
            with self.assertRaises(RuntimeError):
                operador.campo("container", "ficticio", "{{json .Id}}")

    def test_manifesto_integridade_sem_item_recusado(self):
        with patch.object(operador, "sem_atalho"), patch.object(operador, "ler_json", return_value={}):
            with self.assertRaises(RuntimeError):
                operador.verificar_integridade()

    def test_recibo_incompleto_recusa_antes_de_docker(self):
        with self.assertRaises(RuntimeError):
            operador.conferir_recursos({}, {})
        self.execucao.assert_not_called()

    def test_politica_pendente_recusa_sem_conexao(self):
        conexao = Mock()
        with patch.object(Path, "read_text", return_value='{"estado":"PENDENTE"}'):
            with self.assertRaises(RuntimeError):
                contrato.verificar_banco(conexao)
        conexao.cursor.assert_not_called()

    def test_politica_incompleta_recusada(self):
        with self.assertRaises(RuntimeError):
            contrato.validar_politica({"estado": "APROVADA", "tabelas": {}}, {"tabela_ficticia"})

    def test_trigger_correto_aceito_e_alheio_desabilitado_alterado_recusado(self):
        definicao, funcao = "trigger ficticio", "funcao ficticia"
        esperado = {"append_only_ficticio": {
            "trigger_sha256": hashlib.sha256(definicao.encode()).hexdigest(),
            "funcao_sha256": hashlib.sha256(funcao.encode()).hexdigest()}}
        contrato.verificar_gatilhos([("append_only_ficticio", "O", definicao, funcao)], esperado)
        for linha in (("outro", "O", definicao, funcao),
                      ("append_only_ficticio", "D", definicao, funcao),
                      ("append_only_ficticio", "O", definicao, "alterada")):
            with self.subTest(linha=linha), self.assertRaises(RuntimeError):
                contrato.verificar_gatilhos([linha], esperado)

    def test_heranca_docker_recusada_sem_processo(self):
        operador.DOCKER_ALVO = ("cliente-ficticio", "unix:///socket-ficticio")
        with patch.dict(os.environ, {"DOCKER_CONFIG": "perfil-real-ficticio"}):
            with self.assertRaises(RuntimeError):
                operador.docker("info")
        self.execucao.assert_not_called()

    def test_criar_recursos_nao_inicia_nem_migra_nem_carrega(self):
        valores = {"HOM_APP_IMAGE": "imagem-ficticia", "HOM_POSTGRES_IMAGE": "pg-ficticio"}
        def metadata(tipo, recurso, expressao):
            if "Labels" in expressao:
                return {"org.opencontainers.image.revision": "6fc3a85a9ce58a973dc0e29bc38085dfd055f171"}
            if "Running" in expressao:
                return False
            return "identidade-ficticia"
        with patch.object(sys, "argv", ["operar.py", "criar-recursos"]), \
             patch.object(operador, "verificar_integridade"), \
             patch.object(operador, "ler_json", return_value={"engine_id": "engine-ficticia", "exclusividade_engine": True}), \
             patch.object(operador, "autorizar", return_value=("cliente-ficticio", "unix:///socket-ficticio")), \
             patch.object(operador, "validar", return_value=valores), \
             patch.object(operador, "docker", return_value="engine-ficticia"), \
             patch.object(Path, "exists", return_value=False), \
             patch.object(operador, "nomes", return_value=set()), \
             patch.object(operador, "campo", side_effect=metadata), \
             patch.object(operador, "sha", return_value="hash-ficticio"), \
             patch.object(operador, "gravar_novo") as gravar, \
             patch.object(operador, "conferir_recursos"), \
             patch.object(operador, "compose") as compose:
            operador.main()
            compose.assert_called_once()
            argumentos = compose.call_args.args
            self.assertIn("create", argumentos)
            self.assertIn("--no-build", argumentos)
            self.assertNotIn("start", argumentos)
            self.assertNotIn("up", argumentos)
            self.assertEqual(gravar.call_args_list[-1].args[1]["estado"], "sucesso; recursos parados")
        self.execucao.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
