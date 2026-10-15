"""A §10.4 do guia de implantação, presa ao código a partir do próprio guia (073, `R-008`).

**Os exemplos são lidos do Markdown, e não copiados para cá.** Uma cópia ficaria verde enquanto o
guia apodrece — e o guia é o que a TI executa. O preço é o exemplo não poder ter aspas simples
dentro, que o `ps-manage` também não admite.

**E rodam como a TI os roda:** `manage.py shell -v 0 -c`, num processo próprio, e a última linha da
saída é o que se compara com a tabela. Processo próprio também porque, quando a conexão falha no
meio, o `smtplib` e o `urllib` deixam o socket aberto, e o `pyproject.toml` promove o
`ResourceWarning` a erro: no processo da suíte, o socket seria finalizado no caso que estivesse
rodando quando o coletor passasse — o acoplamento entre casos que o `AGENTS.md` descreve.

**Nenhum envio e nenhuma inferência.** Os servidores de correio e o Ollama daqui são falsos, locais
e de vida curta. Eles registram o que receberam, e é por esse registro que o teste prova que nada
foi enviado nem inferido.
"""

import http.server
import json
import os
import pathlib
import re
import socket
import socketserver
import subprocess
import sys
import threading

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[2]
GUIA = RAIZ / "doc" / "implantacao-em-producao-ubuntu.md"
SETTINGS = RAIZ / "backend" / "config" / "settings"

SENHA = "senha-plantada-do-smtp-073"
CREDENCIAL = "credencial-plantada-do-assistente-073"
CHAVE = "chave-plantada-da-aplicacao-073-" + "x" * 40
MODELO = "qwen3.8:27b"


def _secao():
    texto = GUIA.read_text(encoding="utf-8")
    return texto[texto.index("### 10.4") : texto.index("## 11. Migrations")]


def _exemplos():
    """Os quatro `shell -c`, na ordem dos passos 3 a 6."""
    exemplos = re.findall(r"shell -v 0 -c '(.*?)'", _secao(), re.S)
    assert len(exemplos) == 4, "a §10.4 deveria ter quatro exemplos de shell -c (passos 3 a 6)"
    return exemplos


def _blocos_sem_linguagem():
    """Os blocos de código sem linguagem declarada: os trechos de `app.env`."""
    blocos, bloco = [], None
    for linha in _secao().splitlines():
        if linha.startswith("```"):
            if bloco is None:
                bloco = [] if linha == "```" else False
            else:
                if bloco is not False:
                    blocos.append(bloco)
                bloco = None
        elif isinstance(bloco, list):
            bloco.append(linha)
    return blocos


def _tabela():
    """As linhas de "Quando algo falha": (o que aparece, causas, como distinguir)."""
    secao = _secao()
    tabela = secao[secao.index("#### Quando algo falha") :]
    linhas = [
        linha
        for linha in tabela.splitlines()
        if linha.startswith("|") and not re.fullmatch(r"\|[-| ]+\|", linha)
    ][1:]
    return [tuple(celula.strip() for celula in linha.strip("|").split(" | ")) for linha in linhas]


def _na_tabela(ultima_linha):
    """A linha da tabela cujos trechos em código aparecem todos na última linha da saída."""
    achadas = [
        trechos
        for aparece, _, _ in _tabela()
        if (trechos := re.findall(r"`([^`]+)`", aparece))
        and all(trecho in ultima_linha for trecho in trechos)
    ]
    assert achadas, f"nenhuma linha da tabela da §10.4 descreve: {ultima_linha}"


def _rodar(exemplo, **ambiente):
    """Código de saída, saída padrão e a última linha que a TI lê (`2>&1 | tail -n 1`).

    O ambiente é montado, e não herdado: só o que o cenário declara, sobre as settings de teste.
    """
    resultado = subprocess.run(
        [sys.executable, "manage.py", "shell", "-v", "0", "-c", exemplo],
        cwd=RAIZ / "backend",
        env={
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
            "DJANGO_SETTINGS_MODULE": "config.settings.test",
            **ambiente,
        },
        capture_output=True,
        text=True,
        timeout=60,
    )
    linhas = (resultado.stdout + resultado.stderr).strip().splitlines()
    return resultado.returncode, resultado.stdout, linhas[-1] if linhas else ""


def _porta_fechada():
    with socket.socket() as livre:
        livre.bind(("127.0.0.1", 0))
        return livre.getsockname()[1]


# ---- Os blocos de exemplo e a seção (FR-1651, FR-1657) -----------------------------------------


def test_toda_variavel_dos_blocos_e_lida_pelas_settings():
    lidas = set()
    for arquivo in ("base.py", "production.py"):
        texto = (SETTINGS / arquivo).read_text(encoding="utf-8")
        lidas |= set(re.findall(r"""(?:getenv|environ\.get)\(\s*["']([A-Z_]+)["']""", texto))
    declaradas = {
        linha.split("=", 1)[0]
        for bloco in _blocos_sem_linguagem()
        for linha in bloco
        if re.match(r"[A-Z_]+=", linha)
    }

    assert {"EMAIL_HOST", "EMAIL_HOST_PASSWORD", "ASSISTENTE_SERVICO"} <= declaradas
    assert declaradas - lidas == set()


def test_a_senha_do_bloco_e_so_marcador():
    assert "EMAIL_HOST_PASSWORD=<SMTP_SENHA>" in _secao()


def test_a_secao_nao_manda_ler_codigo_nem_specs():
    """A TI segue a seção sem abrir código nem documento de `specs/`."""
    secao = _secao()
    assert "specs/" not in secao
    assert not re.search(r"\b\w+\.py\b", secao)


# ---- A leitura da configuração (FR-1652, SC-621) -----------------------------------------------


def test_a_leitura_nao_imprime_segredo_nenhum():
    codigo, saida, _ = _rodar(
        _exemplos()[0],
        EMAIL_HOST="smtp.exemplo.test",
        EMAIL_HOST_PASSWORD=SENHA,
        ASSISTENTE_CREDENCIAL=CREDENCIAL,
        DJANGO_SECRET_KEY=CHAVE,
    )

    assert codigo == 0, saida
    for segredo in (SENHA, CREDENCIAL, CHAVE):
        assert segredo not in saida
    linhas = saida.splitlines()
    assert linhas[0] == "config.settings.test"
    assert "EMAIL_HOST = 'smtp.exemplo.test'" in linhas
    assert "EMAIL_HOST_PASSWORD presente: True" in linhas
    assert "ASSISTENTE_CREDENCIAL presente: True" in linhas


def test_a_secao_diz_que_a_leitura_e_do_processo_de_diagnostico():
    secao = _secao()
    assert "processo de diagnóstico" in secao
    assert "**Não** prova a dos workers do gunicorn" in secao


# ---- O correio: conexão, segurança e conta, sem enviar (FR-1653 a FR-1655, SC-622) -------------


class _Servidor(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class _Smtp(socketserver.StreamRequestHandler):
    """Um servidor SMTP falso; `comportamento` diz o defeito, e `recebidos` guarda os comandos."""

    comportamento = "aceita"
    recebidos: list

    def _linha(self, texto):
        self.wfile.write((texto + "\r\n").encode())

    def handle(self):
        if self.comportamento == "mudo":
            # Aceita a conexão e não manda a saudação, como a porta que espera TLS desde o início.
            self.rfile.read(1)
            return
        self._linha("220 falso ESMTP")
        for bruto in self.rfile:
            comando = bruto.decode(errors="replace").strip()
            verbo = comando.split(" ", 1)[0].upper()
            self.recebidos.append(verbo)
            if verbo == "EHLO":
                self._linha("250-falso")
                self._linha("250 AUTH PLAIN LOGIN")
            elif verbo == "AUTH":
                if self.comportamento == "recusa a conta":
                    self._linha("535 5.7.8 credencial recusada")
                else:
                    self._linha("235 2.7.0 aceita")
            elif verbo == "QUIT":
                self._linha("221 tchau")
                return
            else:
                self._linha("502 nao")


@pytest.fixture
def smtp():
    """Sobe um SMTP falso com o defeito pedido, e devolve o ambiente que aponta para ele."""
    servidores = []

    def subir(comportamento, *, tls=False):
        recebidos = []
        manipulador = type(
            "Smtp", (_Smtp,), {"comportamento": comportamento, "recebidos": recebidos}
        )
        servidor = _Servidor(("127.0.0.1", 0), manipulador)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        servidores.append(servidor)
        ambiente = {
            "DJANGO_EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
            "EMAIL_HOST": "127.0.0.1",
            "EMAIL_PORT": str(servidor.server_address[1]),
            "EMAIL_USE_TLS": "true" if tls else "false",
            "EMAIL_TIMEOUT": "1",
            "EMAIL_HOST_USER": "conta",
            "EMAIL_HOST_PASSWORD": SENHA,
        }
        return ambiente, recebidos

    yield subir
    for servidor in servidores:
        servidor.shutdown()
        servidor.server_close()


def test_a_conexao_aceita_nao_envia_nada(smtp):
    ambiente, recebidos = smtp("aceita")

    codigo, saida, ultima = _rodar(_exemplos()[1], **ambiente)

    assert codigo == 0, saida
    assert ultima == "conexão, segurança e conta aceitas; nada foi enviado"
    assert "AUTH" in recebidos
    assert not {"MAIL", "RCPT", "DATA"} & set(recebidos)
    assert SENHA not in saida


def test_a_conta_recusada_esta_na_tabela(smtp):
    ambiente, recebidos = smtp("recusa a conta")

    codigo, _, ultima = _rodar(_exemplos()[1], **ambiente)

    assert codigo != 0
    assert "SMTPAuthenticationError" in ultima
    _na_tabela(ultima)
    assert SENHA not in ultima
    assert "MAIL" not in recebidos


def test_sem_starttls_esta_na_tabela(smtp):
    ambiente, _ = smtp("aceita", tls=True)

    _, _, ultima = _rodar(_exemplos()[1], **ambiente)

    assert "SMTPNotSupportedError" in ultima
    _na_tabela(ultima)


def test_a_conexao_que_abre_e_nao_fala_esta_na_tabela(smtp):
    ambiente, _ = smtp("mudo")

    _, _, ultima = _rodar(_exemplos()[1], **ambiente)

    assert "SMTPServerDisconnected" in ultima and "timed out" in ultima
    _na_tabela(ultima)


def test_a_porta_fechada_esta_na_tabela():
    _, _, ultima = _rodar(
        _exemplos()[1],
        DJANGO_EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
        EMAIL_HOST="127.0.0.1",
        EMAIL_PORT=str(_porta_fechada()),
        EMAIL_TIMEOUT="1",
    )

    assert "ConnectionRefusedError" in ultima
    _na_tabela(ultima)


def test_o_nome_que_nao_resolve_esta_na_tabela():
    _, _, ultima = _rodar(
        _exemplos()[1],
        DJANGO_EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
        EMAIL_HOST="smtp.nao-existe.invalid",
        EMAIL_TIMEOUT="1",
    )

    assert "gaierror" in ultima
    _na_tabela(ultima)


def test_nenhum_tempo_esgotado_tem_causa_unica():
    """D-004: tempo esgotado é sintoma, e a tabela não conclui por nenhuma causa."""
    esgotados = [(aparece, causas) for aparece, causas, _ in _tabela() if "timed out" in aparece]

    assert len(esgotados) >= 3
    for aparece, causas in esgotados:
        assert causas.count(";") >= 1, f"{aparece}: uma causa só"


def test_a_porta_465_nao_e_causa_na_tabela():
    assert all("465" not in causas for _, causas, _ in _tabela())


# ---- O Ollama: conexão e modelo, sem inferência (FR-1653, SC-622) ------------------------------


class _Ollama(http.server.BaseHTTPRequestHandler):
    modelos: list
    caminhos: list

    def _responder(self):
        self.caminhos.append(self.path)
        corpo = {
            "/api/version": {"version": "0.12.3"},
            "/api/tags": {"models": [{"name": nome} for nome in self.modelos]},
        }.get(self.path)
        if corpo is None:
            self.send_error(404)
            return
        dados = json.dumps(corpo).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    # Um POST em /api/chat seria inferência, e cairia nos caminhos registrados.
    do_GET = do_POST = _responder

    def log_message(self, *args):
        pass


@pytest.fixture
def ollama():
    servidores = []

    def subir(modelos, *, sufixo=""):
        caminhos = []
        manipulador = type("Ollama", (_Ollama,), {"modelos": modelos, "caminhos": caminhos})
        servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), manipulador)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        servidores.append(servidor)
        ambiente = {
            "ASSISTENTE_ENDERECO": f"http://127.0.0.1:{servidor.server_address[1]}{sufixo}",
            "ASSISTENTE_MODELO": MODELO,
        }
        return ambiente, caminhos

    yield subir
    for servidor in servidores:
        servidor.shutdown()
        servidor.server_close()


def test_a_versao_responde_sem_inferencia(ollama):
    ambiente, caminhos = ollama(["outro:7b"])

    codigo, saida, ultima = _rodar(_exemplos()[2], **ambiente)

    assert codigo == 0, saida
    assert ultima.endswith("versão 0.12.3")
    assert caminhos == ["/api/version"]


def test_o_modelo_instalado_e_dito_sem_inferencia(ollama):
    ambiente, caminhos = ollama([MODELO, "outro:7b"])

    codigo, saida, ultima = _rodar(_exemplos()[3], **ambiente)

    assert codigo == 0, saida
    assert ultima == f"{MODELO} instalado"
    assert caminhos == ["/api/tags"]


def test_o_modelo_ausente_e_dito_e_esta_na_tabela(ollama):
    ambiente, caminhos = ollama(["outro:7b"])

    _, _, ultima = _rodar(_exemplos()[3], **ambiente)

    assert ultima == f"{MODELO} NÃO instalado; instalados: outro:7b"
    assert caminhos == ["/api/tags"]
    _na_tabela(ultima)


def test_o_endereco_com_caminho_esta_na_tabela(ollama):
    ambiente, _ = ollama([MODELO], sufixo="/api")

    _, _, ultima = _rodar(_exemplos()[2], **ambiente)

    assert "HTTPError" in ultima and "404" in ultima
    _na_tabela(ultima)


def test_o_ollama_recusado_esta_na_tabela():
    _, _, ultima = _rodar(
        _exemplos()[2], ASSISTENTE_ENDERECO=f"http://127.0.0.1:{_porta_fechada()}"
    )

    assert "URLError" in ultima and "Connection refused" in ultima
    _na_tabela(ultima)


def test_a_secao_diz_que_a_versao_nao_prova_o_modelo():
    assert "A versão, sozinha, não demonstra que o modelo está disponível" in _secao()


# ---- O reinício e o §16 (FR-1650, FR-1656) -----------------------------------------------------


def test_o_reinicio_confere_os_dois_instantes():
    secao = _secao()
    assert "systemctl show -p ActiveEnterTimestamp processoseletivo" in secao
    assert "stat -c '%y' /etc/processoseletivo/app.env" in secao


def test_o_16_remete_a_10_4_e_nao_a_duplica():
    texto = GUIA.read_text(encoding="utf-8")
    secao_16 = texto[texto.index("## 16. E-mail") : texto.index("## 17. Smoke test")]
    assert "§10.4" in secao_16
    assert "get_connection" not in secao_16
