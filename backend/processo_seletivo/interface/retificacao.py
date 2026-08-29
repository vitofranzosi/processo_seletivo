"""Composição de Retificação por diferença sobre o conteúdo vigente.

A Alteração Normativa do domínio é um caminho JSON Pointer com operação e valor novo. Pedir
isso a quem elabora um Edital seria transferir uma decisão de representação para quem tem um
problema administrativo. Aqui a pessoa edita o conteúdo que está vigorando, e a diferença entre
o que ela viu e o que ela deixou é traduzida nas alterações — que é o que US4 descreve como
"o conteúdo vigente ao lado da alteração proposta".

Além de alterar valores, é possível remover e acrescentar Perfis e Eventos. Remover desloca
índices, então a ordem em que as alterações são emitidas importa: primeiro os REPLACE, que usam
os índices do conteúdo vigente; depois os REMOVE em ordem decrescente, para que apagar um não
mova os seguintes; por último os ADD, que acrescentam ao fim com o token `-`.
"""

from datetime import UTC, datetime
from uuid import uuid4
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

LISTA = "lista"
# Um Perfil ou Evento acrescentado entra no snapshot publicado; precisa nascer com a mesma
# forma que `edital_snapshot` produz, e não com um subconjunto que a consulta pública quebraria.
NOVO_PERFIL = [
    ("code", "Código", TEXTO),
    ("name", "Denominação", TEXTO),
    ("locality", "Localidade", TEXTO),
    ("description", "Descrição", TEXTO),
    ("immediateVacancies", "Vagas imediatas", INTEIRO),
    ("reserveLimit", "Limite do Cadastro Reserva", INTEIRO),
    ("requirements", "Requisitos", LISTA),
]
NOVO_EVENTO = [
    ("type", "Tipo", TEXTO),
    ("description", "Descrição", TEXTO),
    ("startAt", "Início", INSTANTE),
    ("endAt", "Término", INSTANTE),
]


def _ler(conteudo, caminho):
    """Valor em `caminho`, ou None quando ele não resolve.

    `-` é a posição de acréscimo do RFC 6901: nada existe ali, e é por isso que um ADD não tem
    "antes". Índice fora da lista tem o mesmo destino — nenhum dos dois é erro de programa.
    """
    atual = conteudo
    for token in caminho.lstrip("/").split("/"):
        if isinstance(atual, list):
            if not token.isdigit() or int(token) >= len(atual):
                return None
            atual = atual[int(token)]
        elif isinstance(atual, dict):
            atual = atual.get(token)
        else:
            return None
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
                "caminho": f"/profiles/{indice}",
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
                "caminho": f"/schedule/{indice}",
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
    """O campo `datetime-local` tem precisão de minuto; o snapshot guarda segundos.

    Comparar com precisão total acusava alteração em todo Evento cujo instante não terminasse
    em zero segundos: abrir a tela e não tocar em nada listava quatro mudanças inexistentes.
    Diferença abaixo de um minuto não foi a pessoa que fez — ela não tem como fazê-la.
    """
    if anterior is None or novo is None:
        return anterior == novo

    def ao_minuto(valor):
        return datetime.fromisoformat(str(valor)).replace(second=0, microsecond=0)

    return ao_minuto(anterior) == ao_minuto(novo)


def _indices_marcados(dados, prefixo):
    """Índices que a pessoa marcou para remover, do maior para o menor.

    Decrescente porque as alterações são aplicadas em sequência: remover `/profiles/0` primeiro
    faria `/profiles/2` virar `/profiles/1`, e o segundo REMOVE apagaria o Perfil errado.
    """
    marcados = []
    for chave in dados:
        if chave.startswith(f"remover:{prefixo}/"):
            token = chave.split("/")[-1]
            if token.isdigit():
                marcados.append(int(token))
    return sorted(marcados, reverse=True)


def _indices_novos(dados, prefixo):
    return sorted(
        {
            chave.split("-")[2]
            for chave in dados
            if chave.startswith(f"novo-{prefixo}-") and chave.count("-") >= 3
        }
    )


def novas_para_formulario(dados, prefixo, campos):
    """Linhas acrescentadas com o que foi digitado, para reexibir depois do POST.

    Sem isto, ver o resumo devolvia um formulário sem as linhas novas e sem as marcações de
    remoção: a pessoa lia "vai remover e acrescentar" e confirmava um conjunto vazio.
    """
    return [
        {
            "indice": indice,
            "campos": [
                {
                    "chave": chave,
                    "rotulo": rotulo,
                    "tipo": tipo,
                    "valor": dados.get(f"novo-{prefixo}-{indice}-{chave}") or "",
                }
                for chave, rotulo, tipo in campos
            ],
        }
        for indice in _indices_novos(dados, prefixo)
    ]


def _linhas_novas(dados, prefixo, campos):
    """Linhas acrescentadas, agrupadas pelo índice que o servidor deu a cada uma."""
    indices = _indices_novos(dados, prefixo)
    linhas = []
    for indice in indices:
        valores = {}
        vazia = True
        for chave, rotulo, tipo in campos:
            bruto = (dados.get(f"novo-{prefixo}-{indice}-{chave}") or "").strip()
            if bruto:
                vazia = False
            if tipo == LISTA:
                valores[chave] = [linha.strip() for linha in bruto.splitlines() if linha.strip()]
            else:
                valores[chave] = _converter(bruto, tipo, rotulo)
        # Linha em branco é a que a pessoa acrescentou e desistiu de preencher.
        if not vazia:
            linhas.append(valores)
    return linhas


def _perfil_completo(valores):
    """Forma que `edital_snapshot` produz — um subconjunto quebraria a consulta pública."""
    return {
        "id": str(uuid4()),
        "code": valores.get("code") or "",
        "name": valores.get("name") or "",
        "description": valores.get("description") or "",
        "requirements": valores.get("requirements") or [],
        "immediateVacancies": valores.get("immediateVacancies") or 0,
        "reserveType": "NONE",
        "reserveLimit": valores.get("reserveLimit"),
        "locality": valores.get("locality") or "",
        "classificationInformation": {},
        "callInformation": {},
        "competitionModalities": [],
    }


def _evento_completo(valores, ordem):
    return {
        "id": str(uuid4()),
        "type": valores.get("type") or "",
        "description": valores.get("description") or "",
        "startAt": valores.get("startAt"),
        "endAt": valores.get("endAt"),
        "order": ordem,
        "status": "PLANEJADO",
    }


def diferencas(conteudo, dados):
    """Alterações Normativas derivadas do que mudou entre o vigente e o que foi submetido.

    A ordem de emissão é a garantia de correção, porque o domínio aplica em sequência:
    REPLACE usando os índices do vigente, REMOVE do maior índice para o menor, e ADD por
    último, acrescentando ao fim.
    """
    alteracoes, resumo = [], []
    removidos = {
        "/profiles": _indices_marcados(dados, "/profiles"),
        "/schedule": _indices_marcados(dados, "/schedule"),
    }
    for grupo in campos_editaveis(conteudo):
        caminho_grupo = grupo.get("caminho") or ""
        lista, _, indice = caminho_grupo.rpartition("/")
        # Alterar campo de linha que será removida não tem efeito e confundiria o resumo.
        if indice.isdigit() and int(indice) in removidos.get(lista, []):
            continue
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

    for lista, rotulo, nome in (("/profiles", "Perfil", "name"), ("/schedule", "Evento", "type")):
        for indice in removidos[lista]:
            atual = _ler(conteudo, f"{lista}/{indice}") or {}
            alteracoes.append({"targetPath": f"{lista}/{indice}", "operation": "REMOVE"})
            resumo.append(
                {
                    "grupo": f"{rotulo} {atual.get(nome, '')}",
                    "rotulo": "Remoção",
                    "caminho": f"{lista}/{indice}",
                    "antes": atual.get(nome, "") or "—",
                    "depois": "removido do Edital",
                }
            )

    for valores in _linhas_novas(dados, "perfil", NOVO_PERFIL):
        alteracoes.append(
            {
                "targetPath": "/profiles/-",
                "operation": "ADD",
                "newValue": _perfil_completo(valores),
            }
        )
        resumo.append(
            {
                "grupo": f"Perfil {valores.get('code') or ''}",
                "rotulo": "Acréscimo",
                "caminho": "/profiles/-",
                "antes": "—",
                "depois": valores.get("name") or "novo Perfil",
            }
        )

    proxima_ordem = len(conteudo.get("schedule") or []) - len(removidos["/schedule"])
    for deslocamento, valores in enumerate(_linhas_novas(dados, "evento", NOVO_EVENTO)):
        alteracoes.append(
            {
                "targetPath": "/schedule/-",
                "operation": "ADD",
                "newValue": _evento_completo(valores, proxima_ordem + deslocamento + 1),
            }
        )
        resumo.append(
            {
                "grupo": f"Evento {valores.get('type') or ''}",
                "rotulo": "Acréscimo",
                "caminho": "/schedule/-",
                "antes": "—",
                "depois": valores.get("description") or "novo Evento",
            }
        )

    return alteracoes, resumo
