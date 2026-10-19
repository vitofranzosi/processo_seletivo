"""Operações futuras do laboratório. Não executar na Fase 5B.1, nem mesmo validar.

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

RAIZ = Path(__file__).resolve().parent
COMPOSE = RAIZ / "compose.homologacao.yaml"
DONO = {LABEL: IDENTIDADE, "br.edu.ifes.cefor.finalidade": "homologacao-sintetica"}
SERVICOS = {"banco-homologacao": "cefor-f4-pg-20261016",
            "aplicacao-homologacao": "cefor-f4-app-20261016"}
VOLUMES = ["cefor_f4_pg_20261016", "cefor_f4_midia_20261016"]
REDE = "cefor-f4-rede-20261016"
CHAVES = {"HOM_APP_IMAGE", "HOM_POSTGRES_IMAGE", "HOM_ADMIN_PASSWORD",
          "HOM_MIGRATION_PASSWORD", "HOM_RUNTIME_PASSWORD"}
RECIBO = RAIZ / "recibo-recursos.json"


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


def validar(configuracao):
    sem_atalho(RAIZ)
    integridade = ler_json(RAIZ / "integridade.json")
    for nome, resumo in integridade.items():
        caminho = RAIZ / nome
        if not caminho.resolve().is_relative_to(RAIZ) or sha(caminho) != resumo:
            raise RuntimeError("Artefato mudou; requer revisão e novo manifesto de integridade")
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
    if len({valores[c] for c in CHAVES if c.endswith("PASSWORD")}) != 3:
        raise RuntimeError("Papéis precisam de credenciais sintéticas distintas")
    if any(os.environ.get(chave) for chave in CHAVES):
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
    rede = manifesto["networks"]["rede-homologacao"]
    if rede.get("internal") is not True or rede["labels"] != DONO:
        raise RuntimeError("Rede não isolada")
    return valores


def docker(*argumentos, ausente=False):
    # Não herdar DOCKER_HOST/CONTEXT/TLS de uma sessão; contexto precisa ser o padrão local aprovado.
    if any(os.environ.get(k) for k in ("DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_TLS_VERIFY", "COMPOSE_FILE")):
        raise RuntimeError("Contexto Docker/Compose herdado não autorizado")
    permitidas = ("PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "USERPROFILE", "LOCALAPPDATA", "APPDATA")
    ambiente = {k: os.environ[k] for k in permitidas if k in os.environ}
    resultado = subprocess.run(["docker", *argumentos], env=ambiente, capture_output=True, text=True, encoding="utf-8")
    if resultado.returncode:
        if ausente:
            return None
        raise RuntimeError("Operação Docker falhou; saída restrita não anexada automaticamente")
    return resultado.stdout.strip()


def campo(tipo, recurso, expressao):
    valor = docker(tipo, "inspect", "--format", expressao, recurso)
    return json.loads(valor)


def compose(configuracao, *args):
    return docker("compose", "--project-name", PROJETO, "--file", str(COMPOSE),
                  "--env-file", str(configuracao), *args)


def conferir_recursos(recibo, valores, app=False):
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
            rotulos = campo(tipo, nome, formato)
            if any(rotulos.get(k) != v for k, v in DONO.items()):
                raise RuntimeError("Recurso não pertence ao laboratório")
            if rotulos.get("com.docker.compose.project") != PROJETO:
                raise RuntimeError("Propriedade Compose divergente")
            if tipo != "volume" and campo(tipo, nome, "{{json .Id}}") != identidade:
                raise RuntimeError("Recurso substituído desde o recibo")
            if tipo == "volume" and campo(tipo, nome, "{{json .CreatedAt}}") != identidade:
                raise RuntimeError("Volume substituído desde o recibo")
            if tipo == "volume" and (campo(tipo, nome, "{{json .Driver}}") != "local"
                                     or campo(tipo, nome, "{{json .Options}}")):
                raise RuntimeError("Volume usa driver/opções de montagem não autorizados")
    rede = campo("network", REDE, "{{json .Internal}}")
    if rede is not True:
        raise RuntimeError("Rede permite saída externa")
    conectados = campo("network", REDE, "{{json .Containers}}") or {}
    if set(conectados) - set(recibo["containers"].values()):
        raise RuntimeError("Rede compartilhada com outro container")
    for nome in recibo["containers"]:
        redes = campo("container", nome, "{{json .NetworkSettings.Networks}}")
        if set(redes) != {REDE}:
            raise RuntimeError("Container ligado a rede extra")
        montagens = campo("container", nome, "{{json .Mounts}}")
        for montagem in montagens:
            if montagem["Type"] == "volume":
                if montagem["Name"] not in VOLUMES:
                    raise RuntimeError("Volume compartilhado/desconhecido")
            elif not (montagem["Type"] == "bind" and not montagem["RW"]
                      and Path(montagem["Source"]).resolve() == (RAIZ / "isolamento").resolve()):
                raise RuntimeError("Bind ou socket não autorizado")
        portas = campo("container", nome, "{{json .HostConfig.PortBindings}}") or {}
        esperado = {"8000/tcp": [{"HostIp": "127.0.0.1", "HostPort": "18084"}]} if nome == SERVICOS["aplicacao-homologacao"] else {}
        if portas != esperado:
            raise RuntimeError("Porta pública ou inesperada")
    if app and SERVICOS["aplicacao-homologacao"] not in recibo["containers"]:
        raise RuntimeError("App não registrada")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("acao", choices=["validar", "inspecionar", "provisionar", "esquema", "conferir", "baseline", "iniciar", "demonstrar", "evidencias", "preservar", "encerrar", "descartar"])
    parser.add_argument("--cenario", choices=["P01-A", "P01-B", "P01-C", "P06-A", "P06-B", "P06-C",
                                              "P07-A", "P07-B", "P15-A", "P15-B", "P15-C", "P15-D", "P15-E", "P15-F"])
    opcoes = parser.parse_args()
    configuracao = RAIZ / "homologacao.env"
    valores = validar(configuracao)
    if opcoes.acao == "validar":
        print("Artefatos válidos estaticamente; isolamento de execução NÃO comprovado")
        return
    endpoint = json.loads(docker("context", "inspect", "--format", "{{json .Endpoints.docker.Host}}"))
    if not endpoint.startswith(("npipe://", "unix://")):
        raise RuntimeError("Somente daemon local por socket/pipe é autorizado")
    aprovacao = ler_json(RAIZ / "autorizacao.json")
    if (type(aprovacao.get("acoes")) is not list or type(aprovacao.get("cenarios")) is not list
        or not all(isinstance(item, str) for item in aprovacao["acoes"] + aprovacao["cenarios"])):
        raise RuntimeError("Autorização exige listas explícitas de ações e cenários")
    if (aprovacao.get("identidade") != IDENTIDADE or not aprovacao.get("aprovador")
        or aprovacao["aprovador"] == "PENDENTE" or aprovacao.get("referencia_da_deliberacao") in (None, "", "PENDENTE")
        or aprovacao.get("manifesto_sha256") != sha(COMPOSE)
        or aprovacao.get("integridade_sha256") != sha(RAIZ / "integridade.json")
        or aprovacao.get("configuracao_sha256") != sha(configuracao)
        or opcoes.acao not in aprovacao.get("acoes", [])):
        raise RuntimeError("Autorização humana específica não registrada")
    if opcoes.acao == "inspecionar":
        print(json.dumps({"engine": docker("info", "--format", "{{.ID}}"), "identidade": IDENTIDADE}))
        return
    if aprovacao.get("engine_id") != docker("info", "--format", "{{.ID}}"):
        raise RuntimeError("Engine não foi expressamente aprovada")
    if opcoes.acao == "provisionar":
        if RECIBO.exists():
            raise RuntimeError("Recibo existente; não reaproveitar recursos")
        # Verificar disponibilidade do daemon antes de interpretar inspect ausente.
        engine = docker("info", "--format", "{{.ID}}")
        for tipo, nomes in (("container", list(SERVICOS.values()) + ["cefor-f4-preparacao-20261016"]), ("network", [REDE]), ("volume", VOLUMES)):
            for nome in nomes:
                if docker(tipo, "inspect", "--format", "{{.Name}}", nome, ausente=True) is not None:
                    raise RuntimeError("Nome já ocupado; não adotar nem sobrescrever recurso")
        for chave in ("HOM_APP_IMAGE", "HOM_POSTGRES_IMAGE"):
            docker("image", "inspect", "--format", "{{.Id}}", valores[chave])
        rotulos = campo("image", valores["HOM_APP_IMAGE"], "{{json .Config.Labels}}") or {}
        if rotulos.get("org.opencontainers.image.revision") != "6fc3a85a9ce58a973dc0e29bc38085dfd055f171":
            raise RuntimeError("Procedência da imagem da aplicação não comprovada")
        compose(configuracao, "--profile", "operacional", "create", "--pull", "never", "banco-homologacao", "aplicacao-homologacao")
        recibo = {"engine": engine, "identidade": IDENTIDADE,
                  "configuracao_sha256": sha(configuracao), "integridade_sha256": sha(RAIZ / "integridade.json"),
                  "containers": {n: campo("container", n, "{{json .Id}}") for n in SERVICOS.values()},
                  "redes": {REDE: campo("network", REDE, "{{json .Id}}")},
                  "volumes": {n: campo("volume", n, "{{json .CreatedAt}}") for n in VOLUMES}}
        gravar_novo(RECIBO, recibo)
        conferir_recursos(recibo, valores)
        # PostgreSQL inicializa cluster/banco novos somente nesta ação expressamente autorizada.
        compose(configuracao, "--profile", "operacional", "start", "banco-homologacao")
        print("Banco iniciado; esquema e aplicação ainda não iniciados")
        return
    recibo = ler_json(RECIBO)
    for caminho in sorted(RAIZ.glob("recibo-tarefa-*.json")):
        tarefa = ler_json(caminho)
        if tarefa["engine"] != recibo["engine"] or tarefa["identidade"] != IDENTIDADE:
            raise RuntimeError("Recibo de tarefa não pertence à execução")
        if set(tarefa["containers"]) & set(recibo["containers"]):
            raise RuntimeError("Container duplicado em recibos")
        recibo["containers"].update(tarefa["containers"])
    conferir_recursos(recibo, valores)
    if opcoes.acao in {"esquema", "baseline", "conferir"}:
        nome_tarefa = f"cefor-f4-tarefa-{opcoes.acao}-20261016"
        caminho_recibo = RAIZ / f"recibo-tarefa-{opcoes.acao}.json"
        if caminho_recibo.exists() or docker("container", "inspect", "--format", "{{.Name}}", nome_tarefa, ausente=True) is not None:
            raise RuntimeError("Tarefa já registrada; preservar em vez de repetir")
        try:
            compose(configuracao, "--profile", "manutencao", "run", "--name", nome_tarefa,
                    "--no-deps", "preparacao-homologacao", opcoes.acao, IDENTIDADE)
        finally:
            # Não usar --rm: mesmo falha deixa container/evidências para descarte autorizado.
            existente = docker("container", "inspect", "--format", "{{.Id}}", nome_tarefa, ausente=True)
            if existente:
                rotulos = campo("container", nome_tarefa, "{{json .Config.Labels}}")
                if any(rotulos.get(k) != v for k, v in DONO.items()):
                    raise RuntimeError("Container de tarefa tem propriedade inesperada")
                gravar_novo(caminho_recibo, {"engine": recibo["engine"], "identidade": IDENTIDADE,
                                           "containers": {nome_tarefa: existente}})
    elif opcoes.acao == "iniciar":
        compose(configuracao, "--profile", "operacional", "start", "aplicacao-homologacao")
    elif opcoes.acao == "demonstrar":
        if not opcoes.cenario or opcoes.cenario not in aprovacao.get("cenarios", []):
            raise RuntimeError("Cenário não autorizado")
        receitas = ler_json(RAIZ / "cenarios.json")
        if receitas["identidade"] != IDENTIDADE:
            raise RuntimeError("Receita não pertence ao laboratório")
        caso = next(c for c in receitas["casos"] if c["id"] == opcoes.cenario)
        print(f"Sessão manual autorizada para {opcoes.cenario}: http://127.0.0.1:18084; seguir roteiro F4 sem alterar código")
        print(json.dumps(caso, ensure_ascii=False))
    elif opcoes.acao == "evidencias":
        gravar_novo(RAIZ / "evidencia-recursos.json", {"recibo": recibo, "manifesto_sha256": sha(COMPOSE), "configuracao_sha256": sha(configuracao)})
    elif opcoes.acao == "preservar":
        compose(configuracao, "--profile", "operacional", "stop", "aplicacao-homologacao")
    elif opcoes.acao == "encerrar":
        for identidade in recibo["containers"].values():
            docker("container", "stop", identidade)
    elif opcoes.acao == "descartar":
        # Não há remoção recursiva de caminhos nem Compose down -v.
        confirmacao = "DESCARTAR " + IDENTIDADE + " " + " ".join(sorted(recibo["containers"].values()))
        if input("Confirme literalmente os IDs: " + confirmacao + "\n") != confirmacao:
            raise RuntimeError("Descarte não confirmado")
        conferir_recursos(recibo, valores)
        # Somente containers previamente parados podem ser removidos. Não parar banco em uso
        # como efeito colateral de descarte: a decisão deve preparar o encerramento explicitamente.
        for nome in recibo["containers"]:
            if campo("container", nome, "{{json .State.Running}}"):
                raise RuntimeError("Container ainda ativo; autorização de encerramento necessária")
        for identidade in recibo["containers"].values():
            docker("container", "rm", identidade)
        docker("network", "rm", recibo["redes"][REDE])
        for nome in recibo["volumes"]:
            # O Docker recusa volume ainda em uso; não forçar e não remover outros containers.
            if campo("volume", nome, "{{json .CreatedAt}}") != recibo["volumes"][nome]:
                raise RuntimeError("Volume mudou antes da remoção")
            rotulos = campo("volume", nome, "{{json .Labels}}")
            if any(rotulos.get(k) != v for k, v in DONO.items()):
                raise RuntimeError("Propriedade do volume mudou")
            docker("volume", "rm", nome)


if __name__ == "__main__":
    try:
        main()
    except Exception as erro:
        # Exceções de biblioteca podem incluir parâmetros; não publicar detalhes/segredos.
        print("Operação recusada ou interrompida: " + type(erro).__name__, file=sys.stderr)
        raise SystemExit(1)
