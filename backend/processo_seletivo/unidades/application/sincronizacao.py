"""O registro de Unidades: declarado em arquivo versionado, aplicado com trilha (060, R-003, D-002).

**Arquivo, e não tela.** São ~26 unidades que mudam em anos, e as linhas do cabeçalho são decisão
editorial de documento oficial, que se revisa melhor em diff do que num formulário. O argumento que
derrubou o catálogo de autoridades em código — mudança frequente — não vale aqui.

**Comando, e não data migration.** A FR-1108 pede quem e quando de cada mudança, e migration não
pode importar `application` (`test_migrations_do_not_import_domain_or_application_code`): uma data
migration mudaria a Unidade sem deixar evento na trilha.

**Tudo ou nada.** O arquivo inteiro se aplica numa transação; uma Unidade retirada do arquivo ou uma
entrada malformada recusa a sincronização antes de gravar qualquer coisa.
"""

import json
import re
from pathlib import Path

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.unidades.domain import nomes
from processo_seletivo.unidades.models import Unidade

ARQUIVO = Path(__file__).resolve().parents[1] / "unidades.json"

CAMPOS = ("sigla", "nome", "cabecalho", "local", "ativa")

_CODIGO = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def ler(caminho=ARQUIVO):
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def _malformada(codigo, campo, motivo):
    return DomainError(
        nomes.UNIDADE_MALFORMADA,
        f"A unidade {codigo} está malformada no registro: {campo} {motivo}.",
        422,
    )


def validar(declaradas):
    """Confere o arquivo inteiro antes de qualquer gravação. Devolve-o normalizado."""
    if not isinstance(declaradas, dict) or not declaradas:
        raise _malformada("(registro)", "o arquivo", "precisa declarar ao menos uma unidade")
    normalizadas = {}
    for codigo, entrada in declaradas.items():
        if not isinstance(codigo, str) or not _CODIGO.match(codigo):
            raise _malformada(codigo, "o código", "deve ter só minúsculas, dígitos e hífen")
        if not isinstance(entrada, dict):
            raise _malformada(codigo, "a entrada", "deve ser um objeto")
        sobrando = set(entrada) - set(CAMPOS)
        faltando = set(CAMPOS) - set(entrada)
        if sobrando or faltando:
            raise _malformada(
                codigo,
                "os campos",
                f"devem ser exatamente {', '.join(CAMPOS)}",
            )
        for campo in ("sigla", "nome", "local"):
            if not isinstance(entrada[campo], str) or not entrada[campo].strip():
                raise _malformada(codigo, campo, "não pode ser vazio")
        linhas = entrada["cabecalho"]
        if (
            not isinstance(linhas, list)
            or not 1 <= len(linhas) <= 2
            or not all(isinstance(linha, str) and linha.strip() for linha in linhas)
        ):
            raise _malformada(codigo, "cabecalho", "deve ter uma ou duas linhas preenchidas")
        if not isinstance(entrada["ativa"], bool):
            raise _malformada(codigo, "ativa", "deve ser true ou false")
        normalizadas[codigo] = {
            "sigla": entrada["sigla"].strip(),
            "nome": entrada["nome"].strip(),
            "cabecalho": [linha.strip() for linha in linhas],
            "local": entrada["local"].strip(),
            "ativa": entrada["ativa"],
        }
    return normalizadas


def _campos(unidade):
    return {campo: getattr(unidade, campo) for campo in CAMPOS}


def _situacao(ativa):
    return "ATIVA" if ativa else "DESATIVADA"


def sincronizar(declaradas, *, correlation_id=""):
    """Aplica o registro declarado. Devolve `(criadas, alteradas, mantidas)`."""
    normalizadas = validar(declaradas)
    criadas = alteradas = mantidas = 0
    with command_context() as now:
        registradas = {unidade.codigo: unidade for unidade in Unidade.objects.select_for_update()}
        retiradas = sorted(set(registradas) - set(normalizadas))
        if retiradas:
            raise DomainError(
                nomes.UNIDADE_RETIRADA,
                f"A unidade {retiradas[0]} saiu do registro. Nenhuma unidade é excluída: "
                'desative-a com "ativa": false.',
                422,
            )
        for codigo, depois in normalizadas.items():
            ator = Actor(nomes.IMPLANTACAO, codigo)
            existente = registradas.get(codigo)
            if existente is None:
                unidade = Unidade.objects.create(codigo=codigo, registrada_em=now, **depois)
                record_event(
                    actor=ator,
                    permission=nomes.IMPLANTACAO,
                    operation="REGISTRAR_UNIDADE",
                    aggregate=unidade,
                    now=now,
                    correlation_id=correlation_id,
                    new_state=_situacao(unidade.ativa),
                    new_revision=None,
                    detalhe={"depois": depois},
                )
                criadas += 1
                continue
            antes = _campos(existente)
            if antes == depois:
                mantidas += 1
                continue
            for campo, valor in depois.items():
                setattr(existente, campo, valor)
            existente.alterada_em = now
            existente.save(update_fields=[*CAMPOS, "alterada_em"])
            record_event(
                actor=ator,
                permission=nomes.IMPLANTACAO,
                operation="ALTERAR_UNIDADE",
                aggregate=existente,
                now=now,
                correlation_id=correlation_id,
                previous_state=_situacao(antes["ativa"]),
                new_state=_situacao(existente.ativa),
                new_revision=None,
                detalhe={"antes": antes, "depois": depois},
            )
            alteradas += 1
    return criadas, alteradas, mantidas
