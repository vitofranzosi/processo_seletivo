"""Uma rodada da matriz do piloto do assistente, e o relatório dela (071, `R-016`).

**Pela mesma `perguntar` da tela**, com `origem = AVALIACAO` e o instante do caso: o que se avalia é
o que o participante vê, e não uma cópia. Cada repetição é uma conversa nova, e as trocas ficam
gravadas como as da tela, e são excluídas com elas (`R-021`).

**O gasto é limitado pela credencial, e não aqui** (`FR-1507`, emendado em 14/10). Quando o serviço
recusa pelo limite de gasto, a rodada para ali, e os casos restantes saem "por rodar": seguir
mandando perguntas a um serviço que recusa todas só encheria o relatório de recusas.

**Os Editais são os do banco** — o corpus publicado por `scripts/publicar_corpus_do_piloto.py` —, e
o comando não fabrica conteúdo: um caso cujo Edital não está lá sai "não rodado".

**Nada de tokens, tempo ou custo por troca no relatório** (`FR-1510`). Eles vão ao log, como na
tela; o comando lê da própria linha de log só o custo, para o total da rodada (`SC-560`).
"""

from __future__ import annotations

import csv
import json
import logging
import subprocess
import uuid
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from processo_seletivo.duvidas.application.consultar import SemVersaoVigente, consultar
from processo_seletivo.duvidas.application.perguntar import logger as logger_do_piloto
from processo_seletivo.duvidas.application.perguntar import perguntar
from processo_seletivo.duvidas.domain import catalogo
from processo_seletivo.duvidas.domain.conferencia import DATA_NUMERICA, _legivel, _valores
from processo_seletivo.duvidas.domain.estruturas import DADO
from processo_seletivo.duvidas.domain.estruturas_do_piloto import (
    AVALIACAO,
    ORCAMENTO_ESGOTADO,
    RESPONDIDA_E_CONFERIDA,
    TELA,
)
from processo_seletivo.duvidas.domain.mensagens import VERSAO_DAS_INSTRUCOES
from processo_seletivo.duvidas.infrastructure import inferencia
from processo_seletivo.duvidas.models import TrocaDoPiloto
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

MATRIZ = Path(__file__).resolve().parents[2] / "avaliacao" / "matriz.json"
SEM_VERSAO_VIGENTE = "SEM_VERSAO_VIGENTE"
SEM_GASTO = "o serviço recusou pelo limite de gasto da credencial antes deste caso"
COLUNAS_DA_REVISAO = (
    "caso",
    "repeticao",
    "pergunta",
    "trecho",
    "natureza",
    "texto",
    "fontes",
    "conteudo_das_fontes",
    # A revisão humana (`FR-1513`, `FR-1514`): vazias, para quem revisa.
    "julgamento",
    "omissao",
    "origem_da_falha",
    "nota",
)


class _Custos(logging.Handler):
    """O custo de cada troca, lido da linha de log dela — o único lugar em que ele existe."""

    def __init__(self):
        super().__init__(logging.INFO)
        self.custos = []

    def emit(self, registro):
        mensagem = registro.getMessage()
        if mensagem.startswith("troca_do_piloto "):
            self.custos.append(json.loads(mensagem.split(" ", 1)[1]).get("custo"))


class Command(BaseCommand):
    help = "Roda a matriz do piloto do assistente do Edital e escreve o relatório da rodada."

    def add_arguments(self, parser):
        parser.add_argument("--saida", required=True, help="Diretório dos três arquivos.")
        parser.add_argument("--repeticoes", type=int, default=5)
        parser.add_argument("--casos", default="", help="Identificadores, separados por vírgula.")
        parser.add_argument("--deslocamento-dias", type=int, default=0)
        parser.add_argument("--rodada-anterior", default=None)
        parser.add_argument("--exportar-conversas", action="store_true")

    def handle(self, *args, **opcoes):
        saida = Path(opcoes["saida"])
        saida.mkdir(parents=True, exist_ok=True)
        if opcoes["exportar_conversas"]:
            quantas = _exportar_conversas(saida / "conversas.json")
            self.stdout.write(f"{quantas} trocas das sessões exportadas em {saida}.")
            return
        if not settings.ASSISTENTE_PILOTO:
            raise CommandError("O piloto do assistente está desligado (ASSISTENTE_PILOTO).")
        anterior = _rodada_anterior(opcoes["rodada_anterior"])
        matriz = json.loads(MATRIZ.read_text(encoding="utf-8"))
        casos = _selecionados(matriz["casos"], opcoes["casos"])

        rodada = Rodada(matriz, opcoes)
        custos = _Custos()
        nivel = logger_do_piloto.level
        logger_do_piloto.addHandler(custos)
        if not logger_do_piloto.isEnabledFor(logging.INFO):
            logger_do_piloto.setLevel(logging.INFO)
        try:
            resultados = [rodada.rodar(caso) for caso in casos]
        finally:
            logger_do_piloto.removeHandler(custos)
            logger_do_piloto.setLevel(nivel)

        relatorio = {
            "configuracao": _configuracao(),
            "commit": _commit(),
            "versao_das_instrucoes": VERSAO_DAS_INSTRUCOES,
            "iniciada_em": rodada.iniciada_em.isoformat(),
            "repeticoes": opcoes["repeticoes"],
            "deslocamento_dias": opcoes["deslocamento_dias"],
            "casos": resultados,
        }
        (saida / "rodada.json").write_text(
            json.dumps(relatorio, ensure_ascii=False, indent=2, default=str) + "\n",
            encoding="utf-8",
        )
        _escrever_revisao(saida / "revisao.csv", resultados)
        (saida / "resumo.md").write_text(
            _resumo(relatorio, anterior, rodada, custos.custos), encoding="utf-8"
        )
        self.stdout.write(
            f"{rodada.chamadas} chamadas; {len(resultados)} casos, "
            f"{rodada.por_rodar} por rodar. Relatório em {saida}."
        )


class Rodada:
    def __init__(self, matriz, opcoes):
        self.padrao = matriz.get("instante_padrao")
        self.repeticoes = opcoes["repeticoes"]
        self.deslocamento = timedelta(days=opcoes["deslocamento_dias"])
        self.identificador = uuid.uuid4().hex[:8]
        self.iniciada_em = timezone.now()
        self.chamadas = 0
        self.por_rodar = 0
        self.parada = False
        self.trocas = []

    def rodar(self, caso):
        resultado = {"id": caso["id"], "categoria": caso["categoria"], "edital": caso["edital"]}
        motivo = self._motivo_para_nao_rodar(caso)
        edital = None if motivo else _edital(caso["edital"])
        if not motivo and edital is None:
            motivo = "o Edital não está publicado neste banco"
        instantes = None if motivo else self._instantes(caso, edital)
        if not motivo and instantes is None:
            motivo = "a versão pedida pelo caso não está neste banco"
        if motivo:
            return {**resultado, "rodado": False, "motivo": motivo}

        repeticoes = []
        for repeticao in range(1, self.repeticoes + 1):
            if self.parada:
                break
            repeticoes.append(self._repetir(caso, edital, instantes, repeticao))
        if not repeticoes:
            self.por_rodar += 1
            return {**resultado, "rodado": False, "motivo": SEM_GASTO}
        return {
            **resultado,
            "rodado": True,
            "repeticoes": repeticoes,
            "impressoes": sorted(
                {
                    troca["impressao_das_fontes"]
                    for item in repeticoes
                    for troca in item["trocas"]
                    if troca.get("impressao_das_fontes")
                }
            ),
        }

    def _motivo_para_nao_rodar(self, caso):
        if self.parada:
            self.por_rodar += 1
            return SEM_GASTO
        if caso.get("rodar") is False:
            return caso.get("motivo") or "o caso não roda contra o serviço"
        servico = caso.get("servico")
        if servico and servico != settings.ASSISTENTE_SERVICO:
            return f"o caso só roda com o serviço {servico}"
        return None

    def _instantes(self, caso, edital):
        brutos = caso.get("instantes") or [caso.get("instante")] * len(caso["perguntas"])
        instantes = []
        for bruto in brutos:
            bruto = bruto or self.padrao
            if bruto.startswith("versao:"):
                # O início da vigência da N-ésima versão consolidada: instante real, da publicação
                # no banco, e por isso não deslocado.
                ordem = int(bruto.split(":", 1)[1])
                versoes = list(
                    VersaoConsolidada.objects.filter(edital=edital)
                    .order_by("materialized_at")
                    .values_list("valid_from", flat=True)
                )
                if ordem > len(versoes):
                    return None
                instantes.append(versoes[ordem - 1])
            else:
                instantes.append(datetime.fromisoformat(bruto) + self.deslocamento)
        return instantes

    def _repetir(self, caso, edital, instantes, repeticao):
        conversa = uuid.uuid4()
        trocas = []
        for pergunta, instante in zip(caso["perguntas"], instantes, strict=True):
            try:
                troca = perguntar(
                    edital_id=edital.id,
                    conversa=conversa,
                    pergunta=pergunta,
                    instante=instante,
                    origem=AVALIACAO,
                    correlacao=f"{self.identificador}:{caso['id']}:{repeticao}",
                )
            except SemVersaoVigente:
                trocas.append(
                    {"pergunta": pergunta, "instante": instante, "estado": SEM_VERSAO_VIGENTE}
                )
                break
            self.chamadas += int(troca.chamou_o_servico)
            self.trocas.append(troca)
            trocas.append(_troca(troca))
            if troca.estado == ORCAMENTO_ESGOTADO:
                self.parada = True
                break
        return {
            "repeticao": repeticao,
            "trocas": trocas,
            "comparacoes": _comparar(caso, trocas[-1], edital, self.deslocamento),
        }


def _selecionados(casos, filtro):
    if not filtro:
        return casos
    pedidos = [item.strip() for item in filtro.split(",") if item.strip()]
    por_id = {caso["id"]: caso for caso in casos}
    desconhecidos = [pedido for pedido in pedidos if pedido not in por_id]
    if desconhecidos:
        raise CommandError(f"Casos que a matriz não tem: {', '.join(desconhecidos)}.")
    return [por_id[pedido] for pedido in pedidos]


def _edital(referencia):
    if not referencia:
        return None
    editais = list(
        Edital.objects.filter(
            number=referencia["numero"], year=referencia["ano"], versoes_consolidadas__isnull=False
        ).distinct()[:2]
    )
    # Dois Editais com o mesmo número e ano, em unidades diferentes: o caso não sabe de qual fala.
    return editais[0] if len(editais) == 1 else None


def _troca(troca):
    """O que a rodada guarda de uma troca: a resposta e a conferência, sem tokens, tempo, custo."""
    return {
        "ordem": troca.ordem,
        "instante": troca.instante,
        "versao": troca.versao_curta,
        "pergunta": troca.pergunta,
        "estado": troca.estado,
        "tipo": troca.tipo or None,
        "trechos": troca.trechos or [],
        "fontes_citadas": troca.fontes_citadas or [],
        "conferencia": troca.conferencia or [],
        "historico_desde": troca.historico_desde,
        "modelo_que_respondeu": troca.modelo_que_respondeu or None,
        "impressao_das_fontes": troca.impressao_das_fontes or None,
    }


def _deslocar(valor, deslocamento):
    """As datas esperadas do caso, deslocadas como o corpus foi."""

    def trocar(achado):
        dia, mes, ano = (int(parte) for parte in achado.groups())
        data = datetime(ano, mes, dia) + deslocamento
        return data.strftime("%d/%m/%Y")

    return DATA_NUMERICA.sub(trocar, valor)


def _comparar(caso, ultima, edital, deslocamento):
    """As comparações automáticas, na última resposta (contracts/comandos.md §1)."""
    esperado = caso["esperado"]
    estado = esperado.get("estado") or RESPONDIDA_E_CONFERIDA
    comparacoes = {"estado": {"esperado": estado, "obtido": ultima["estado"]}}
    if ultima["estado"] != RESPONDIDA_E_CONFERIDA:
        return comparacoes
    obtidos = _valores(" ".join(trecho["texto"] for trecho in ultima["trechos"]))
    valores = [_deslocar(valor, deslocamento) for valor in esperado.get("valores") or []]
    proibidos = [_deslocar(valor, deslocamento) for valor in esperado.get("nenhum_valor") or []]
    comparacoes.update(
        {
            "tipo": {"esperado": esperado.get("tipo"), "obtido": ultima["tipo"]},
            "valores_presentes": [valor for valor in valores if _valores(valor) <= obtidos],
            "valores_ausentes": [valor for valor in valores if not _valores(valor) <= obtidos],
            "proibidos_presentes": [valor for valor in proibidos if _valores(valor) & obtidos],
        }
    )
    if caso.get("referencia_070"):
        comparacoes["070"] = _com_a_070(caso["referencia_070"], edital, ultima, obtidos)
    return comparacoes


def _com_a_070(referencia, edital, ultima, obtidos):
    """Os números e datas dos cartões de dado da `070`, e o tipo, contra a resposta (`SC-554`).

    Os códigos de tipo são os mesmos nos dois: o rótulo de `RESPONDIDA` é que muda no piloto.
    """
    try:
        resposta = consultar(
            edital_id=edital.id,
            instante=ultima["instante"],
            pergunta=referencia["pergunta"],
            perfil=referencia.get("perfil"),
            modalidade=referencia.get("modalidade"),
        )
    except catalogo.ParametroRecusado as recusa:
        return {"recusada": str(recusa)}
    dados = set()
    for cartao in resposta.referencias:
        if cartao.natureza == DADO:
            dados |= _valores(cartao.conteudo)
    return {
        "tipo": resposta.tipo,
        "tipo_coincide": resposta.tipo == ultima["tipo"],
        "faltando": sorted(_legivel(valor) for valor in dados - obtidos),
        "a_mais": sorted(_legivel(valor) for valor in obtidos - dados),
    }


def _configuracao():
    """A configuração da rodada, **sem credencial** (`FR-1502`)."""
    return {
        "servico": settings.ASSISTENTE_SERVICO,
        "endereco": settings.ASSISTENTE_ENDERECO,
        "modelo": settings.ASSISTENTE_MODELO,
        "quantizacao": settings.ASSISTENTE_QUANTIZACAO,
        "parametros": inferencia.parametros_configurados(),
        "tokens_por_mensagem": settings.ASSISTENTE_TOKENS_POR_MENSAGEM,
        "tolerancia_de_tokens": settings.ASSISTENTE_TOLERANCIA_DE_TOKENS,
        "ollama_sem_corte": settings.ASSISTENTE_OLLAMA_SEM_CORTE,
        "zdr": settings.ASSISTENTE_ZDR,
    }


def _commit():
    try:
        feito = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=settings.BASE_DIR,
        )
    except (OSError, subprocess.CalledProcessError):
        return "desconhecido"
    return feito.stdout.strip()


def _rodada_anterior(caminho):
    if not caminho:
        return None
    arquivo = Path(caminho)
    if arquivo.is_dir():
        arquivo = arquivo / "rodada.json"
    try:
        return json.loads(arquivo.read_text(encoding="utf-8"))
    except (OSError, ValueError) as falha:
        raise CommandError(f"Não foi possível ler a rodada anterior: {falha}") from None


def _outra_versao(relatorio, anterior):
    """Os casos cuja fonte ou instrução difere da rodada anterior (`FR-1515`, `D-010`)."""
    if anterior is None:
        return set()
    antes = {caso["id"]: caso.get("impressoes") for caso in anterior.get("casos") or []}
    mudou_a_instrucao = anterior.get("versao_das_instrucoes") != relatorio["versao_das_instrucoes"]
    return {
        caso["id"]
        for caso in relatorio["casos"]
        if caso.get("rodado")
        and (mudou_a_instrucao or antes.get(caso["id"]) != caso.get("impressoes"))
    }


def _escrever_revisao(arquivo, resultados):
    with arquivo.open("w", encoding="utf-8", newline="") as saida:
        escritor = csv.writer(saida)
        escritor.writerow(COLUNAS_DA_REVISAO)
        for caso in resultados:
            for repeticao in caso.get("repeticoes") or []:
                for troca in repeticao["trocas"]:
                    if troca["estado"] != RESPONDIDA_E_CONFERIDA:
                        continue
                    por_id = {fonte["id"]: fonte for fonte in troca["fontes_citadas"]}
                    for indice, trecho in enumerate(troca["trechos"], start=1):
                        fontes = trecho.get("fontes") or []
                        conteudo = "\n".join(
                            _fonte_para_revisar(por_id[fonte])
                            for fonte in fontes
                            if fonte in por_id
                        )
                        escritor.writerow(
                            (
                                caso["id"],
                                repeticao["repeticao"],
                                troca["ordem"],
                                indice,
                                trecho["natureza"],
                                trecho["texto"],
                                ", ".join(fontes),
                                conteudo,
                                "",
                                "",
                                "",
                                "",
                            )
                        )


def _fonte_para_revisar(fonte):
    """A fonte como o revisor a procura no Edital: o lugar, o rótulo e o conteúdo."""
    rotulo = f" — {fonte['rotulo']}" if fonte.get("rotulo") else ""
    return f"{fonte['id']} — {fonte['lugar']}{rotulo}: {fonte['conteudo']}"


def _resumo(relatorio, anterior, rodada, custos):
    casos = relatorio["casos"]
    rodados = [caso for caso in casos if caso.get("rodado")]
    outra = _outra_versao(relatorio, anterior)
    estados = Counter(troca.estado for troca in rodada.trocas)
    motivos = Counter(
        motivo["regra"] for troca in rodada.trocas for motivo in troca.conferencia or []
    )
    informados = [custo for custo in custos if custo is not None]
    configuracao = relatorio["configuracao"]
    linhas = [
        f"# Rodada da matriz do piloto — {relatorio['iniciada_em'][:10]}",
        "",
        f"- Serviço: `{configuracao['servico']}`; modelo: `{configuracao['modelo']}`",
        f"- Commit: `{relatorio['commit']}`; versão das instruções: "
        f"`{relatorio['versao_das_instrucoes']}`",
        f"- Repetições: {relatorio['repeticoes']}; deslocamento: "
        f"{relatorio['deslocamento_dias']} dias",
        "- Só o Ollama da L4, com a configuração que vai rodar, conta para a conclusão (`SC-555`).",
        "",
        "## Totais da rodada",
        "",
        f"- Casos: {len(casos)}; rodados: {len(rodados)}; por rodar: {rodada.por_rodar}",
        f"- Trocas: {len(rodada.trocas)}; chamadas ao serviço: {rodada.chamadas}",
        "- Estados: "
        + (", ".join(f"`{estado}` {n}" for estado, n in sorted(estados.items())) or "nenhum"),
        "- Custo total informado pelo serviço: "
        + (f"{sum(informados):.6f}" if informados else "não informado"),
        "",
        "## Recusas da conferência, por motivo",
        "",
    ]
    linhas += [f"- `{regra}`: {n}" for regra, n in sorted(motivos.items())] or ["- nenhuma"]
    linhas += [
        "",
        "Recusas indevidas, a preencher na revisão: ___ de "
        f"{estados.get('NAO_PASSOU_NA_CONFERENCIA', 0)}.",
        "",
        "## Por caso",
        "",
        "| Caso | Estado da última resposta | Tipo esperado × obtido | Com todos os valores "
        "esperados | Com valor proibido | Valores e tipo da `070` | Versão da fonte |",
        "|---|---|---|---|---|---|---|",
    ]
    for caso in casos:
        if not caso.get("rodado"):
            continue
        linhas.append(_linha_do_caso(caso, caso["id"] in outra))
    nao_rodados = [caso for caso in casos if not caso.get("rodado")]
    if nao_rodados:
        linhas += ["", "## Não rodados", ""]
        linhas += [f"- `{caso['id']}`: {caso['motivo']}" for caso in nao_rodados]
    return "\n".join(linhas) + "\n"


def _linha_do_caso(caso, de_outra_versao):
    repeticoes = caso["repeticoes"]
    total = len(repeticoes)
    estados = Counter(item["trocas"][-1]["estado"] for item in repeticoes)
    comparadas = [item["comparacoes"] for item in repeticoes if "tipo" in item["comparacoes"]]
    tipos = Counter(
        f"{item['tipo']['esperado'] or '—'} × {item['tipo']['obtido']}" for item in comparadas
    )
    com_valores = sum(1 for item in comparadas if not item["valores_ausentes"])
    com_proibido = sum(1 for item in comparadas if item["proibidos_presentes"])
    da_070 = [item["070"] for item in comparadas if "070" in item]
    coincide = sum(1 for item in da_070 if item.get("tipo_coincide") and not item.get("faltando"))
    return (
        f"| `{caso['id']}` | "
        + ", ".join(f"{estado} {n}/{total}" for estado, n in sorted(estados.items()))
        + " | "
        + (", ".join(f"{par} {n}" for par, n in sorted(tipos.items())) or "—")
        + f" | {com_valores}/{len(comparadas)} | {com_proibido}/{len(comparadas)} | "
        + (f"{coincide}/{len(da_070)}" if da_070 else "—")
        + " | "
        + ("outra versão da fonte" if de_outra_versao else "—")
        + " |"
    )


def _exportar_conversas(arquivo):
    """As trocas das sessões da tela, mascaradas como estão, para a revisão na máquina da equipe."""
    trocas = [
        {
            "conversa": str(troca.conversa),
            "ordem": troca.ordem,
            "edital": f"{troca.edital.number}/{troca.edital.year}",
            "instante": troca.instante,
            "versao": troca.versao_curta,
            "pergunta": troca.pergunta,
            "estado": troca.estado,
            "tipo": troca.tipo or None,
            "trechos": troca.trechos or [],
            "fontes_citadas": [fonte["id"] for fonte in troca.fontes_citadas or []],
            "conferencia": troca.conferencia or [],
        }
        for troca in TrocaDoPiloto.objects.filter(origem=TELA).select_related("edital")
    ]
    arquivo.write_text(
        json.dumps(trocas, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8"
    )
    return len(trocas)
