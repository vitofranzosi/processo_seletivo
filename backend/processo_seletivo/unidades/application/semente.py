"""A semente do registro de Unidades: o arquivo só se aplica a um registro vazio (110, `D-001`).

**O banco é a fonte; o arquivo é semente de instalação.** Até a `110`, a sincronização aplicava o
`unidades.json` em toda subida e recusava unidade do banco ausente dele: uma correção feita no banco
voltava no deploy seguinte, e uma unidade criada no banco impedia a subida. Desde a `110`, quem
escreve no registro é a aplicação, com pessoa, motivo e trilha; o arquivo serve ao primeiro preparo
de um banco novo — desenvolvimento, teste, homologação — e a mais nada.

**Só vazio, e não "só os códigos ausentes".** Inserir o código ausente manteria o arquivo como
segundo caminho de criação: uma entrada nova no JSON faria uma unidade nascer no deploy seguinte,
com o autor `implantacao`, por fora da permissão e do motivo que a tela exige.

**Num registro preenchido, o arquivo nem é lido.** Um arquivo sem autoridade não pode derrubar uma
subida (EC-11).
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from django.db import connection

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.unidades.domain import nomes
from processo_seletivo.unidades.domain.registro import validar_campos, validar_codigo
from processo_seletivo.unidades.models import Unidade

ARQUIVO = Path(__file__).resolve().parents[1] / "unidades.json"

OBRIGATORIOS = ("sigla", "nome", "cabecalho", "local", "ativa")
# **Opcional, e só este** (109, FR-3211). Sem ele, vale o canal da instituição; declarado vazio é
# recusado — para não ter canal, omite-se, e a exportação (D-016) o omite pela mesma razão.
OPCIONAIS = ("atendimento",)
CAMPOS = (*OBRIGATORIOS, *OPCIONAIS)

# "O registro está vazio?" é pergunta sobre a tabela inteira, e a trava também: duas subidas do
# contêiner sobre um banco novo gravariam o Cefor duas vezes, e a segunda derrubaria a subida na
# unicidade. Com a trava, a segunda espera e encontra o registro preenchido (D-004).
TRAVA_DA_SEMENTE = int.from_bytes(hashlib.sha256(b"unidades:semente").digest()[:8], "big") >> 1


@dataclass(frozen=True)
class Resultado:
    """`semeadas` é zero quando a semente não se aplicou; `registradas`, o tamanho do registro."""

    semeadas: int
    registradas: int


def ler(caminho=ARQUIVO):
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def _malformada(codigo, campo, motivo):
    return DomainError(
        nomes.UNIDADE_MALFORMADA,
        f"A unidade {codigo} está malformada na semente: {campo} {motivo}.",
        422,
    )


def validar(declaradas):
    """Confere o arquivo inteiro pela regra única, antes de qualquer gravação. Devolve-o aparado."""
    if not isinstance(declaradas, dict) or not declaradas:
        raise _malformada("(semente)", "o arquivo", "precisa declarar ao menos uma unidade")
    normalizadas = {}
    for codigo, entrada in declaradas.items():
        if not isinstance(entrada, dict):
            raise _malformada(codigo, "a entrada", "deve ser um objeto")
        sobrando = set(entrada) - set(CAMPOS)
        faltando = set(OBRIGATORIOS) - set(entrada)
        if sobrando or faltando:
            raise _malformada(
                codigo,
                "os campos",
                f"devem ser exatamente {', '.join(OBRIGATORIOS)} e, se houver, "
                f"{', '.join(OPCIONAIS)}",
            )
        if not isinstance(entrada["ativa"], bool):
            raise _malformada(codigo, "ativa", "deve ser true ou false")
        if "atendimento" in entrada and not str(entrada["atendimento"] or "").strip():
            raise _malformada(codigo, "atendimento", "declarado vazio: para não ter canal, omita-o")
        try:
            validar_codigo(codigo)
            campos = validar_campos(entrada)
        except DomainError as recusa:
            raise _malformada(codigo, recusa.campo or "um campo", f"— {recusa.detail}") from recusa
        normalizadas[codigo] = {**campos, "ativa": entrada["ativa"]}
    return normalizadas


def _situacao(ativa):
    return "ATIVA" if ativa else "DESATIVADA"


def semear(caminho=ARQUIVO, *, correlation_id="semear-unidades"):
    """Registra as unidades do arquivo se o registro estiver vazio; senão, não grava nem lê nada."""
    with command_context() as now:
        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock(%s)", [TRAVA_DA_SEMENTE])
        registradas = Unidade.objects.count()
        if registradas:
            return Resultado(semeadas=0, registradas=registradas)
        normalizadas = validar(ler(caminho))
        for codigo, campos in normalizadas.items():
            unidade = Unidade.objects.create(codigo=codigo, registrada_em=now, **campos)
            record_event(
                actor=Actor(nomes.IMPLANTACAO, codigo),
                permission=nomes.IMPLANTACAO,
                operation="REGISTRAR_UNIDADE",
                aggregate=unidade,
                now=now,
                correlation_id=correlation_id,
                new_state=_situacao(unidade.ativa),
                new_revision=None,
                detalhe={"depois": campos},
            )
    return Resultado(semeadas=len(normalizadas), registradas=len(normalizadas))


def exportar():
    """O registro atual no formato da semente, por código — só para reverter (D-016).

    Todo campo obrigatório vai, inclusive `ativa`; o canal só quando preenchido, porque a semente
    recusa o canal declarado vazio. Não grava nada, e nenhum roteiro de implantação o chama.
    """
    registro = {}
    for unidade in Unidade.objects.order_by("codigo"):
        entrada = {
            "sigla": unidade.sigla,
            "nome": unidade.nome,
            "cabecalho": list(unidade.cabecalho),
            "local": unidade.local,
            "ativa": unidade.ativa,
        }
        if unidade.atendimento:
            entrada["atendimento"] = unidade.atendimento
        registro[unidade.codigo] = entrada
    return registro
