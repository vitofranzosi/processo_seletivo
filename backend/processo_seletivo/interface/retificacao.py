"""Composição de Retificação por diferença sobre o conteúdo vigente.

A Alteração Normativa do domínio é um caminho JSON Pointer com operação e valor novo. Pedir
isso a quem elabora um Edital seria transferir uma decisão de representação para quem tem um
problema administrativo. Aqui a pessoa edita o conteúdo que está vigorando, e a diferença entre
o que ela viu e o que ela deixou é traduzida nas alterações — que é o que US4 descreve como
"o conteúdo vigente ao lado da alteração proposta".

Só campos de valor são editáveis. Acrescentar ou remover Perfil e Evento muda a estrutura do
snapshot e desloca índices; fica para quando houver desenho próprio para isso.
"""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

ZONA = ZoneInfo("America/Sao_Paulo")
TEXTO, INTEIRO, INSTANTE = "texto", "inteiro", "instante"

# (sufixo do caminho, rótulo, tipo) — aplicado a cada Perfil e a cada Evento.
CAMPOS_PERFIL = [
    ("name", "Denominação", TEXTO),
    ("locality", "Localidade", TEXTO),
    ("immediateVacancies", "Vagas imediatas", INTEIRO),
    ("reserveLimit", "Limite do Cadastro Reserva", INTEIRO),
]
CAMPOS_EVENTO = [
    ("description", "Descrição", TEXTO),
    ("startAt", "Início", INSTANTE),
    ("endAt", "Término", INSTANTE),
]
CAMPOS_RAIZ = [("title", "Título do Edital", TEXTO), ("description", "Descrição", TEXTO)]


def _ler(conteudo, caminho):
    atual = conteudo
    for token in caminho.lstrip("/").split("/"):
        atual = atual[int(token)] if isinstance(atual, list) else atual.get(token)
        if atual is None:
            return None
    return atual


def _para_formulario(valor, tipo):
    if valor is None:
        return ""
    if tipo == INSTANTE:
        return datetime.fromisoformat(str(valor)).astimezone(ZONA).strftime("%Y-%m-%dT%H:%M")
    return str(valor)


def campos_editaveis(conteudo):
    """Campos que uma Retificação pode alterar, agrupados como a pessoa os enxerga."""
    grupos = [
        {
            "titulo": "Edital",
            "campos": [
                {
                    "caminho": f"/{chave}",
                    "rotulo": rotulo,
                    "tipo": tipo,
                    "valor": _para_formulario(conteudo.get(chave), tipo),
                }
                for chave, rotulo, tipo in CAMPOS_RAIZ
            ],
        }
    ]
    for indice, perfil in enumerate(conteudo.get("profiles") or []):
        grupos.append(
            {
                "titulo": f"Perfil {perfil.get('code', '')} — {perfil.get('name', '')}",
                "campos": [
                    {
                        "caminho": f"/profiles/{indice}/{chave}",
                        "rotulo": rotulo,
                        "tipo": tipo,
                        "valor": _para_formulario(perfil.get(chave), tipo),
                    }
                    for chave, rotulo, tipo in CAMPOS_PERFIL
                ],
            }
        )
    for indice, evento in enumerate(conteudo.get("schedule") or []):
        grupos.append(
            {
                "titulo": f"Evento {evento.get('order', '')} — {evento.get('type', '')}",
                "campos": [
                    {
                        "caminho": f"/schedule/{indice}/{chave}",
                        "rotulo": rotulo,
                        "tipo": tipo,
                        "valor": _para_formulario(evento.get(chave), tipo),
                    }
                    for chave, rotulo, tipo in CAMPOS_EVENTO
                ],
            }
        )
    return grupos


def _converter(bruto, tipo, rotulo):
    bruto = (bruto or "").strip()
    if bruto == "":
        return None
    if tipo == INTEIRO:
        try:
            return int(bruto)
        except ValueError as exc:
            raise ValueError(f"{rotulo}: '{bruto}' não é um número inteiro.") from exc
    if tipo == INSTANTE:
        try:
            # O snapshot guarda instantes em UTC; converter mantém a comparação honesta.
            return datetime.fromisoformat(bruto).replace(tzinfo=ZONA).astimezone(UTC).isoformat()
        except ValueError as exc:
            raise ValueError(f"{rotulo}: '{bruto}' não é uma data e hora válidas.") from exc
    return bruto


def _mesmo_instante(anterior, novo):
    if anterior is None or novo is None:
        return anterior == novo
    return datetime.fromisoformat(str(anterior)) == datetime.fromisoformat(str(novo))


def diferencas(conteudo, dados):
    """Alterações Normativas derivadas do que mudou entre o vigente e o que foi submetido."""
    alteracoes, resumo = [], []
    for grupo in campos_editaveis(conteudo):
        for campo in grupo["campos"]:
            enviado = dados.get(f"campo:{campo['caminho']}")
            if enviado is None:
                continue
            novo = _converter(enviado, campo["tipo"], campo["rotulo"])
            anterior = _ler(conteudo, campo["caminho"])
            if campo["tipo"] == INSTANTE:
                if _mesmo_instante(anterior, novo):
                    continue
            elif str(anterior if anterior is not None else "") == str(
                novo if novo is not None else ""
            ):
                continue
            alteracoes.append(
                {"targetPath": campo["caminho"], "operation": "REPLACE", "newValue": novo}
            )
            resumo.append(
                {
                    "grupo": grupo["titulo"],
                    "rotulo": campo["rotulo"],
                    "caminho": campo["caminho"],
                    "antes": _para_formulario(anterior, campo["tipo"]) or "—",
                    "depois": _para_formulario(novo, campo["tipo"]) or "—",
                }
            )
    return alteracoes, resumo
