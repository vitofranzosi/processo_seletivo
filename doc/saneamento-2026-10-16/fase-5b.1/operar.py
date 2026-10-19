"""Operador revisado em 5B.2-A.2. Execução operacional permanece não autorizada.

O arquivo de autorização documenta aprovação humana externa; não é assinatura ou substituto dela.
Todas as chamadas Docker usam manifesto exclusivo e ambiente de subprocesso com lista permitida.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "isolamento"))
from contrato import IDENTIDADE, LABEL, PROJETO
from politica_operacional import REVISAO, validar_escopo

RAIZ = Path(__file__).resolve().parent
COMPOSE = RAIZ / "compose.homologacao.yaml"
DONO = {LABEL: IDENTIDADE, "br.edu.ifes.cefor.finalidade": "homologacao-sintetica"}
SERVICOS = {"banco-homologacao": "cefor-f4-pg-20261016",
            "aplicacao-homologacao": "cefor-f4-app-20261016"}
VOLUMES = ["cefor_f4_pg_20261016", "cefor_f4_midia_20261016"]
REDE = "cefor-f4-rede-20261016"
CHAVES = {"HOM_APP_IMAGE", "HOM_POSTGRES_IMAGE", "HOM_ADMIN_PASSWORD", "HOM_RUNTIME_PASSWORD"}
RECIBO = RAIZ / "recibo-recursos.json"
OBRIGATORIOS = {"autorizacao.example.json", "baseline.json", "cenarios.json",
               "compose.homologacao.yaml", "homologacao.env.example", "operar.py",
               "isolamento/contrato.py", "isolamento/settings_homologacao.py",
               "isolamento/iniciar_aplicacao.py", "isolamento/tarefas.py",
               "isolamento/politica-protecoes.json", "isolamento/politica_operacional.py"}
BLOQUEADAS = {"provisionar", "iniciar-postgres", "criar-banco", "papeis", "migrar",
              "esquema", "baseline", "iniciar", "demonstrar", "descartar",
              "bootstrap-postgres", "adquirir-imagens", "construir-imagens", "proteger-esquema"}
PERMITIDAS = {"inspecionar", "criar-recursos", "conferir", "evidencias", "preservar", "encerrar"}
DOCKER_ALVO = None


def sha(caminho):
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def ler_json(caminho):
    return json.loads(caminho.read_text(encoding="utf-8-sig"))


def gravar_novo(caminho, dados):
    with caminho.open("x", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def sem_atalho(caminho):
    atual = caminho.absolute()
    while atual != atual.parent:
        if atual.is_symlink() or (hasattr(atual, "is_junction") and atual.is_junction()):
            raise RuntimeError("Atalho/junção não autorizado")
        atual = atual.parent


def verificar_integridade():
    sem_atalho(RAIZ)
    integridade = ler_json(RAIZ / "integridade.json")
    if not isinstance(integridade, dict) or set(integridade) != OBRIGATORIOS:
        raise RuntimeError("Conjunto de integridade incompleto ou inesperado")
    for nome, resumo in integridade.items():
        caminho = RAIZ / nome
        sem_atalho(caminho)
        if not caminho.resolve().is_relative_to(RAIZ) or sha(caminho) != resumo:
            raise RuntimeError("Artefato mudou; requer revisão e novo manifesto de integridade")


def validar(configuracao):
    verificar_integridade()
    sem_atalho(configuracao)
    if configuracao.absolute() != RAIZ / "homologacao.env":
        raise RuntimeError("Somente homologacao.env independente é aceito; backend/.env é proibido")
    valores = {}
    for linha in configuracao.read_text(encoding="utf-8-sig").splitlines():
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        chave, separador, valor = linha.partition("=")
        if not separador or chave not in CHAVES or chave in valores:
            raise RuntimeError("Configuração contém chave inesperada ou duplicada")
        if not valor or any(c in valor for c in ('$', '\\', '"', "'", ' ', '\t')):
            raise RuntimeError("Valor ausente ou interpolação proibida")
        valores[chave] = valor
    if set(valores) != CHAVES:
        raise RuntimeError("Configuração incompleta")
    for chave in ("HOM_APP_IMAGE", "HOM_POSTGRES_IMAGE"):
        if not re.fullmatch(r"(?:[a-zA-Z0-9._:/-]+@)?sha256:[a-f0-9]{64}", valores[chave]):
            raise RuntimeError("Imagem precisa de digest imutável, sem tag solta")
        if valores[chave].endswith("0" * 64):
            raise RuntimeError("Digest fictício não comprova imagem")
    if len({valores[c] for c in CHAVES if c.endswith("PASSWORD")}) != 2:
        raise RuntimeError("Papéis precisam de credenciais sintéticas distintas")
    if any(os.environ.get(chave) for chave in CHAVES | {"HOM_MIGRATION_PASSWORD"}):
        raise RuntimeError("Variável herdada pode sobrepor configuração; usar sessão limpa")
    # PyYAML é dependência de desenvolvimento, nunca baixada automaticamente.
    import yaml
    manifesto = yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))
    if manifesto["name"] != PROJETO or set(manifesto["services"]) != set(SERVICOS) | {"preparacao-homologacao"}:
        raise RuntimeError("Serviços ou projeto inesperados")
    for servico in manifesto["services"].values():
        if "env_file" in servico or "build" in servico or servico["labels"] != DONO:
            raise RuntimeError("Manifesto não independente")
        if servico.get("privileged") or servico.get("network_mode"):
            raise RuntimeError("Privilégio/rede não autorizado")
    tarefa = manifesto["services"]["preparacao-homologacao"]["environment"]
    if any(chave in tarefa for chave in ("HOM_ADMIN_PASSWORD", "HOM_MIGRATION_PASSWORD")):
        raise RuntimeError("Tarefa comum com credencial privilegiada")
    rede = manifesto["networks"]["rede-homologacao"]
    if rede.get("internal") is not True or rede["labels"] != DONO:
        raise RuntimeError("Rede não isolada")
    return valores


def autorizar(acao, aprovacao, configuracao=None):
    validar_escopo(acao, aprovacao)
    if acao not in PERMITIDAS or aprovacao.get("revisao_operador") != REVISAO:
        raise RuntimeError("Ação/revisão não autorizável nesta versão")
    if (aprovacao.get("identidade") != IDENTIDADE or type(aprovacao.get("acoes")) is not list
        or not all(isinstance(x, str) and x in PERMITIDAS for x in aprovacao["acoes"])
        or acao not in aprovacao["acoes"]):
        raise RuntimeError("Autorização específica ausente")
    for chave in ("aprovador", "referencia_da_deliberacao"):
        if not isinstance(aprovacao.get(chave), str) or aprovacao[chave].strip() in ("", "PENDENTE"):
            raise RuntimeError("Deliberação humana ausente")
    if (aprovacao.get("manifesto_sha256") != sha(COMPOSE)
        or aprovacao.get("integridade_sha256") != sha(RAIZ / "integridade.json")):
        raise RuntimeError("Artefatos não aprovados")
    if configuracao is not None and aprovacao.get("configuracao_sha256") != sha(configuracao):
        raise RuntimeError("Configuração não aprovada")
    endpoint = aprovacao.get("endpoint_local", "")
    if not isinstance(endpoint, str) or not endpoint.startswith(("npipe://", "unix://")):
        raise RuntimeError("Endpoint local explícito obrigatório")
    cliente = RAIZ / "docker-cliente"
    sem_atalho(cliente)
    arquivo = cliente / "config.json"
    sem_atalho(arquivo)
    if (not cliente.is_dir() or {p.name for p in cliente.iterdir()} != {"config.json"}
        or ler_json(arquivo) != {} or aprovacao.get("cliente_sha256") != sha(arquivo)):
        raise RuntimeError("Cliente exclusivo vazio e aprovado obrigatório")
    return str(cliente), endpoint


def docker(*argumentos):
    if DOCKER_ALVO is None:
        raise RuntimeError("Docker bloqueado antes da autorização")
    # Não herdar DOCKER_HOST/CONTEXT/TLS de uma sessão; contexto precisa ser o padrão local aprovado.
    if any(os.environ.get(k) for k in ("DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_TLS_VERIFY", "DOCKER_CONFIG", "COMPOSE_FILE")):
        raise RuntimeError("Contexto Docker/Compose herdado não autorizado")
    permitidas = ("PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "USERPROFILE", "LOCALAPPDATA", "APPDATA")
    ambiente = {k: os.environ[k] for k in permitidas if k in os.environ}
    cliente, endpoint = DOCKER_ALVO
    resultado = subprocess.run(["docker", "--config", cliente, "--host", endpoint, *argumentos], env=ambiente, capture_output=True, text=True, encoding="utf-8")
    if resultado.returncode:
        raise RuntimeError("Operação Docker falhou; saída restrita não anexada automaticamente")
    return resultado.stdout.strip()


def campo(tipo, recurso, expressao):
    valor = docker(tipo, "inspect", "--format", expressao, recurso)
    dado = json.loads(valor)
    if dado is None or (isinstance(dado, str) and (not dado.strip() or dado == "<no value>")):
        raise RuntimeError("Metadata nula não comprova isolamento")
    return dado


def nomes(tipo):
    argumentos = [tipo, "ls"]
    if tipo == "container":
        argumentos.append("--all")
    linhas = docker(*argumentos, "--format", "{{json .Names}}" if tipo == "container" else "{{json .Name}}")
    itens = [json.loads(linha) for linha in linhas.splitlines()]
    if any(not isinstance(item, str) or not item for item in itens) or len(set(itens)) != len(itens):
        raise RuntimeError("Inventário ambíguo ou incompleto")
    return set(itens)


def compose(configuracao, *args):
    return docker("compose", "--project-name", PROJETO, "--file", str(COMPOSE),
                  "--env-file", str(configuracao), *args)


def conferir_recursos(recibo, valores, app=False):
    if (set(recibo.get("redes", {})) != {REDE} or set(recibo.get("volumes", {})) != set(VOLUMES)
        or not set(SERVICOS.values()).issubset(recibo.get("containers", {}))
        or set(recibo["containers"]) - (set(SERVICOS.values()) | {"cefor-f4-tarefa-conferir-20261016"})):
        raise RuntimeError("Recibo incompleto ou com recursos desconhecidos")
    if (recibo["configuracao_sha256"] != sha(RAIZ / "homologacao.env")
        or recibo["integridade_sha256"] != sha(RAIZ / "integridade.json")):
        raise RuntimeError("Configuração ou artefatos mudaram desde o provisionamento")
    if recibo["engine"] != docker("info", "--format", "{{.ID}}") or recibo["identidade"] != IDENTIDADE:
        raise RuntimeError("Daemon ou identidade mudou")
    for tipo, recursos, formato in (
        ("network", recibo["redes"], "{{json .Labels}}"),
        ("volume", recibo["volumes"], "{{json .Labels}}"),
        ("container", recibo["containers"], "{{json .Config.Labels}}"),
    ):
        for nome, identidade in recursos.items():
            if not isinstance(identidade, str) or not identidade:
                raise RuntimeError("Identidade de recurso ausente")
            rotulos = campo(tipo, nome, formato)
            if any(rotulos.get(k) != v for k, v in DONO.items()):
                raise RuntimeError("Recurso não pertence ao laboratório")
            if rotulos.get("com.docker.compose.project") != PROJETO:
                raise RuntimeError("Propriedade Compose divergente")
            if tipo != "volume" and campo(tipo, nome, "{{json .Id}}") != identidade:
                raise RuntimeError("Recurso substituído desde o recibo")
            if tipo == "volume" and campo(tipo, nome, "{{json .CreatedAt}}") != identidade:
                raise RuntimeError("Volume substituído desde o recibo")
            if tipo == "volume":
                opcoes = json.loads(docker(tipo, "inspect", "--format", "{{json .Options}}", nome))
                if campo(tipo, nome, "{{json .Driver}}") != "local" or opcoes not in (None, {}):
                    raise RuntimeError("Volume usa driver/opções de montagem não autorizados")
    rede = campo("network", REDE, "{{json .Internal}}")
    if rede is not True:
        raise RuntimeError("Rede permite saída externa")
    conectados = campo("network", REDE, "{{json .Containers}}")
    if not isinstance(conectados, dict):
        raise RuntimeError("Endpoints de rede incompletos")
    if set(conectados) - set(recibo["containers"].values()):
        raise RuntimeError("Rede compartilhada com outro container")
    for nome in recibo["containers"]:
        redes = campo("container", nome, "{{json .NetworkSettings.Networks}}")
        if set(redes) != {REDE}:
            raise RuntimeError("Container ligado a rede extra")
        montagens = campo("container", nome, "{{json .Mounts}}")
        banco = nome == SERVICOS["banco-homologacao"]
        if not isinstance(montagens, list) or len(montagens) != (1 if banco else 2):
            raise RuntimeError("Conjunto de montagens incompleto")
        destinos = {m.get("Destination") for m in montagens}
        if destinos != ({"/var/lib/postgresql"} if banco else {"/isolamento", "/var/lib/processo-seletivo/arquivos"}):
            raise RuntimeError("Destinos de montagem divergentes")
        for montagem in montagens:
            if montagem["Type"] == "volume":
                esperado_volume = "cefor_f4_pg_20261016" if banco else "cefor_f4_midia_20261016"
                if montagem["Name"] != esperado_volume:
                    raise RuntimeError("Volume compartilhado/desconhecido")
            elif not (montagem["Type"] == "bind" and not montagem["RW"]
                      and Path(montagem["Source"]).resolve() == (RAIZ / "isolamento").resolve()):
                raise RuntimeError("Bind ou socket não autorizado")
        portas = json.loads(docker("container", "inspect", "--format", "{{json .HostConfig.PortBindings}}", nome))
        esperado = {"8000/tcp": [{"HostIp": "127.0.0.1", "HostPort": "18084"}]} if nome == SERVICOS["aplicacao-homologacao"] else {}
        if portas != esperado and not (not esperado and portas is None):
            raise RuntimeError("Porta pública ou inesperada")
    if app and SERVICOS["aplicacao-homologacao"] not in recibo["containers"]:
        raise RuntimeError("App não registrada")


def main():
    global DOCKER_ALVO
    DOCKER_ALVO = None
    parser = argparse.ArgumentParser()
    parser.add_argument("acao", choices=sorted(PERMITIDAS | BLOQUEADAS | {"validar"}))
    parser.add_argument("--cenario")
    opcoes = parser.parse_args()
    if opcoes.acao in BLOQUEADAS:
        raise RuntimeError("Operacao bloqueada nesta revisao; ver plano de separacao e pendencias A2")
    if opcoes.cenario:
        raise RuntimeError("Este operador nao restringe sessoes web por cenario")
    configuracao = RAIZ / "homologacao.env"
    if opcoes.acao == "validar":
        validar(configuracao)
        print("Validacao estatica apenas; isolamento operacional nao comprovado")
        return
    verificar_integridade()
    aprovacao = ler_json(RAIZ / "autorizacao.json")
    DOCKER_ALVO = autorizar(opcoes.acao, aprovacao, None if opcoes.acao == "inspecionar" else configuracao)
    valores = None if opcoes.acao == "inspecionar" else validar(configuracao)
    engine = docker("info", "--format", "{{.ID}}")
    if not engine or engine == "<no value>":
        raise RuntimeError("Identidade da engine ausente")
    if opcoes.acao == "inspecionar":
        print(json.dumps({"engine": engine, "identidade": IDENTIDADE}))
        return
    if aprovacao.get("engine_id") != engine:
        raise RuntimeError("Engine nao aprovada")
    if opcoes.acao == "criar-recursos":
        if RECIBO.exists() or aprovacao.get("exclusividade_engine") is not True:
            raise RuntimeError("Recibo existente ou exclusividade operacional nao declarada")
        for tipo, reservados in (("container", set(SERVICOS.values()) | {"cefor-f4-preparacao-20261016"}),
                                 ("network", {REDE}), ("volume", set(VOLUMES))):
            if nomes(tipo) & reservados:
                raise RuntimeError("Nome ocupado; nao adotar nem sobrescrever")
        for chave in ("HOM_APP_IMAGE", "HOM_POSTGRES_IMAGE"):
            campo("image", valores[chave], "{{json .Id}}")
        rotulos = campo("image", valores["HOM_APP_IMAGE"], "{{json .Config.Labels}}")
        if rotulos.get("org.opencontainers.image.revision") != "6fc3a85a9ce58a973dc0e29bc38085dfd055f171":
            raise RuntimeError("Revisao da imagem divergente")
        gravar_novo(RAIZ / "evento-criar-recursos.json", evento("iniciada"))
        try:
            compose(configuracao, "--profile", "operacional", "create", "--no-build", "--pull", "never",
                    "banco-homologacao", "aplicacao-homologacao")
            recibo = {"engine": engine, "identidade": IDENTIDADE,
                      "configuracao_sha256": sha(configuracao), "integridade_sha256": sha(RAIZ / "integridade.json"),
                      "containers": {n: campo("container", n, "{{json .Id}}") for n in SERVICOS.values()},
                      "redes": {REDE: campo("network", REDE, "{{json .Id}}")},
                      "volumes": {n: campo("volume", n, "{{json .CreatedAt}}") for n in VOLUMES}}
            gravar_novo(RECIBO, recibo)
            conferir_recursos(recibo, valores)
            for nome in SERVICOS.values():
                if campo("container", nome, "{{json .State.Running}}") is not False:
                    raise RuntimeError("Container inesperadamente iniciado")
        except Exception:
            gravar_novo(RAIZ / "resultado-criar-recursos.json", evento("falha; preservar e inventariar, nao repetir"))
            raise
        gravar_novo(RAIZ / "resultado-criar-recursos.json", evento("sucesso; recursos parados"))
        return
    recibo = ler_json(RECIBO)
    for caminho in sorted(RAIZ.glob("recibo-tarefa-*.json")):
        tarefa = ler_json(caminho)
        if tarefa.get("engine") != engine or tarefa.get("identidade") != IDENTIDADE:
            raise RuntimeError("Recibo de tarefa divergente")
        if set(tarefa["containers"]) & set(recibo["containers"]):
            raise RuntimeError("Container duplicado")
        recibo["containers"].update(tarefa["containers"])
    conferir_recursos(recibo, valores)
    if opcoes.acao == "conferir":
        nome = "cefor-f4-tarefa-conferir-20261016"
        if nome in nomes("container"):
            raise RuntimeError("Tarefa preexistente; preservar em vez de repetir")
        gravar_novo(RAIZ / "evento-conferir.json", evento("iniciada"))
        try:
            compose(configuracao, "--profile", "manutencao", "run", "--pull", "never", "--name", nome,
                    "--no-deps", "preparacao-homologacao", "conferir", IDENTIDADE)
            rotulos = campo("container", nome, "{{json .Config.Labels}}")
            if any(rotulos.get(k) != v for k, v in DONO.items()):
                raise RuntimeError("Tarefa de propriedade desconhecida")
            gravar_novo(RAIZ / "recibo-tarefa-conferir.json", {"engine": engine, "identidade": IDENTIDADE,
                        "containers": {nome: campo("container", nome, "{{json .Id}}")}, "resultado": evento("sucesso")})
        except Exception:
            gravar_novo(RAIZ / "resultado-conferir.json", evento("falha; inventariar tarefa sem adotar nem repetir"))
            raise
        gravar_novo(RAIZ / "resultado-conferir.json", evento("sucesso"))
    elif opcoes.acao == "evidencias":
        gravar_novo(RAIZ / "evidencia-recursos.json", {"recibo": recibo, "resultado": evento("metadados; nao prova cenarios")})
    elif opcoes.acao == "preservar":
        docker("container", "stop", recibo["containers"][SERVICOS["aplicacao-homologacao"]])
    elif opcoes.acao == "encerrar":
        for identidade in recibo["containers"].values():
            docker("container", "stop", identidade)


def evento(estado):
    from datetime import datetime, timezone
    return {"estado": estado, "instante": datetime.now(timezone.utc).isoformat()}


if __name__ == "__main__":
    try:
        main()
    except Exception as erro:
        # Exceções de biblioteca podem incluir parâmetros; não publicar detalhes/segredos.
        print("Operação recusada ou interrompida: " + type(erro).__name__, file=sys.stderr)
        raise SystemExit(1)
