"""Composição de Retificação por diferença sobre o conteúdo vigente.

A Alteração Normativa do domínio é um caminho JSON Pointer com operação e valor novo. Pedir
isso a quem elabora um Edital seria transferir uma decisão de representação para quem tem um
problema administrativo. Aqui a pessoa edita o conteúdo que está vigorando, e a diferença entre
o que ela viu e o que ela deixou é traduzida nas alterações — que é o que US4 descreve como
"o conteúdo vigente ao lado da alteração proposta".

Além de alterar valores, é possível remover e acrescentar Perfis e Eventos. Isso já exigiu uma
coreografia: os REPLACE primeiro, com os índices do vigente; os REMOVE em ordem decrescente,
para que apagar um não movesse os seguintes; os ADD por último. **Ela não existe mais.** Cada
alteração nomeia a entidade de que fala, e nenhuma ordem de emissão muda o resultado.

Nada disso aparece na tela. O formulário identifica seus campos por uma **referência opaca** —
posição no formulário que o servidor acabou de gerar, não caminho normativo —, e é aqui que a
referência volta a ser caminho. Quem elabora um Edital tem um problema administrativo, não um
problema de representação (FR-019).
"""

from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from uuid import uuid4
from zoneinfo import ZoneInfo

from processo_seletivo.editais.domain import secoes as catalogo
from processo_seletivo.publicacoes.domain.changes import ABSENT, resolve_path

ZONA = ZoneInfo("America/Sao_Paulo")
TEXTO, INTEIRO, INSTANTE = "texto", "inteiro", "instante"
# A `006` publicou Etapas, Seções e a Regra Normativa das modalidades, e a tela ficou para trás:
# o motor endereçava os três, a interface alcançava nenhum. Estes três tipos são o que faltava
# para descrevê-los — decimal canônico, texto longo e booleano.
DECIMAL, TEXTO_LONGO, BOOLEANO = "decimal", "texto_longo", "booleano"

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

# A modalidade sem Regra Normativa não recebe os campos dela: o caminho não existiria no
# conteúdo, e endereçá-lo seria recusado por caminho inexistente. A tela oferece exatamente o
# que a gramática admite.
CAMPOS_MODALIDADE = [("name", "Denominação", TEXTO), ("description", "Descrição", TEXTO)]
CAMPOS_REGRA = [
    ("normativeRule/percentage", "Percentual (%)", DECIMAL),
    ("normativeRule/foundation", "Fundamento normativo", TEXTO),
    ("normativeRule/version", "Versão do fundamento", TEXTO),
]
CAMPOS_ETAPA = [
    ("name", "Nome da Etapa", TEXTO),
    ("weight", "Peso", DECIMAL),
    ("minimumScore", "Nota mínima", DECIMAL),
    ("eliminatory", "Eliminatória", BOOLEANO),
    ("classificatory", "Classificatória", BOOLEANO),
]
# Só o conteúdo. O catálogo de seções é fixo: título, ordem, tipo e origem divergentes são
# recusados pela verificação de topologia, e uma seção gerada nem campo de conteúdo tem.
CAMPOS_SECAO = [("content", "Texto da seção", TEXTO_LONGO)]

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

    Delega ao próprio domínio: a resolução do seletor `id=` mora lá, e uma segunda cópia dela
    aqui divergiria da primeira no dia em que a gramática mudasse.
    """
    valor = resolve_path(conteudo, caminho)
    return None if valor is ABSENT else valor


def _valor(item, chave):
    """Valor de `chave`, que pode atravessar objetos — `normativeRule/percentage`.

    A Regra Normativa é objeto dentro da modalidade, e não item de lista: o caminho até ela é
    composto por nomes de chave, e é assim que a gramática já a endereça.
    """
    atual = item
    for parte in chave.split("/"):
        if not isinstance(atual, dict):
            return None
        atual = atual.get(parte)
    return atual


def _para_formulario(valor, tipo):
    if tipo == BOOLEANO:
        return "1" if valor else "0"
    if valor is None:
        return ""
    if tipo == INSTANTE:
        return datetime.fromisoformat(str(valor)).astimezone(ZONA).strftime("%Y-%m-%dT%H:%M")
    return str(valor)


def _grupo(titulo, caminho, item, campos, *, removivel=True):
    return {
        "titulo": titulo,
        "caminho": caminho,
        "removivel": removivel,
        "campos": [
            {
                "caminho": f"{caminho}/{chave}",
                "rotulo": rotulo,
                "tipo": tipo,
                "valor": _para_formulario(_valor(item, chave), tipo),
            }
            for chave, rotulo, tipo in campos
        ],
    }


def _referenciar(grupos):
    """Dá a cada grupo e a cada campo o nome pelo qual o formulário os chama.

    A referência é a posição no formulário — `g2c3` —, e não o caminho normativo. É a primeira
    das duas condições de FR-019: o HTML entregue não contém caminho algum. Ela vale só para o
    par requisição/resposta que a gerou, porque o POST reconstrói os mesmos grupos a partir da
    mesma versão base.
    """
    for ordem_grupo, grupo in enumerate(grupos, 1):
        grupo["referencia"] = f"g{ordem_grupo}"
        # A tela precisa saber se a linha pode ser removida sem precisar olhar o caminho — que
        # é justamente o que ela não deve receber. Seção não é removível: o catálogo é fixo, e
        # oferecer a marcação seria oferecer o que a publicação recusa.
        grupo["removivel"] = grupo["removivel"] and bool(grupo["caminho"])
        for ordem_campo, campo in enumerate(grupo["campos"], 1):
            campo["referencia"] = f"g{ordem_grupo}c{ordem_campo}"
    return grupos


def campos_editaveis(conteudo):
    """Campos que uma Retificação pode alterar, agrupados como a pessoa os enxerga.

    Cobre tudo o que o conteúdo publicado carrega e a gramática endereça. A `006` publicou
    Etapas, Seções e a Regra Normativa e não trouxe nenhuma das três para cá; corrigir uma cota
    depois de publicada exigia chamada de API, o que a Constituição não admite como jornada
    concluída.
    """
    grupos = [_grupo("Edital", "", conteudo, CAMPOS_RAIZ, removivel=False)]

    for perfil in conteudo.get("profiles") or []:
        caminho = f"/profiles/id={perfil.get('id', '')}"
        grupos.append(
            _grupo(
                f"Perfil {perfil.get('code', '')} — {perfil.get('name', '')}",
                caminho,
                perfil,
                CAMPOS_PERFIL,
            )
        )
        for modalidade in perfil.get("competitionModalities") or []:
            campos = CAMPOS_MODALIDADE + (
                CAMPOS_REGRA if isinstance(modalidade.get("normativeRule"), dict) else []
            )
            grupos.append(
                _grupo(
                    f"Modalidade {modalidade.get('code', '')} — {perfil.get('code', '')}",
                    f"{caminho}/competitionModalities/id={modalidade.get('id', '')}",
                    modalidade,
                    campos,
                )
            )

    for evento in conteudo.get("schedule") or []:
        grupos.append(
            _grupo(
                f"Evento {evento.get('order', '')} — {evento.get('type', '')}",
                f"/schedule/id={evento.get('id', '')}",
                evento,
                CAMPOS_EVENTO,
            )
        )

    for etapa in conteudo.get("stages") or []:
        grupos.append(
            _grupo(
                f"Etapa {etapa.get('order', '')} — {etapa.get('name', '')}",
                f"/stages/id={etapa.get('id', '')}",
                etapa,
                CAMPOS_ETAPA,
            )
        )

    for secao in conteudo.get("sections") or []:
        # Seção gerada não tem conteúdo próprio: ela é composta a partir do dado que a origina,
        # e é lá que se corrige.
        if secao.get("type") == catalogo.GERADA:
            continue
        grupos.append(
            _grupo(
                f"Seção {secao.get('order', '')} — {secao.get('title', '')}",
                f"/sections/id={secao.get('id', '')}",
                secao,
                CAMPOS_SECAO,
                removivel=False,
            )
        )

    return _referenciar(grupos)


def reexibir(grupos, dados):
    """Devolve os grupos com o que a pessoa digitou, para o formulário voltar como ela o deixou.

    Resolver isto aqui — e não com um filtro repetido em cada controle do template — é o que
    permite que a tela trate texto, número, instante, decimal, texto longo e booleano pelo mesmo
    caminho. O booleano é o que obriga: um `checkbox` desmarcado não é enviado, e a reexibição
    por filtro não teria como distinguir "desmarcado" de "ausente".
    """
    if dados is None:
        return grupos
    for grupo in grupos:
        grupo["marcado_para_remover"] = bool(dados.get(f"remover:{grupo['referencia']}"))
        for campo in grupo["campos"]:
            enviado = dados.get(f"campo:{campo['referencia']}")
            if enviado is not None:
                campo["valor"] = enviado
    return grupos


def _converter(bruto, tipo, rotulo):
    bruto = (bruto or "").strip()
    if tipo == BOOLEANO:
        return bruto == "1"
    if bruto == "":
        return None
    if tipo == DECIMAL:
        # **A forma canônica não é escolha de apresentação.** O conteúdo publicado materializa
        # decimais com quatro casas e sem zero à esquerda, e a verificação de publicação recusa
        # qualquer outra forma. Escrever "2" aqui produziria um conteúdo que a própria
        # Publicação rejeita — e, onde não rejeitasse, faria uma Retificação semanticamente nula
        # alterar o hash. Formatar para leitura humana é assunto da materialização, não daqui.
        try:
            return f"{Decimal(bruto.replace(',', '.')):.4f}"
        except InvalidOperation as exc:
            raise ValueError(f"{rotulo}: '{bruto}' não é um número válido.") from exc
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


def _marcados_para_remover(dados, grupos):
    """Caminhos que a pessoa marcou para remover.

    Sem ordem nenhuma: cada caminho nomeia a entidade, e apagar um não move os outros. Era
    exatamente essa a razão de a ordem decrescente existir.
    """
    return [
        grupo
        for grupo in grupos
        if grupo["removivel"] and dados.get(f"remover:{grupo['referencia']}")
    ]


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

    **A ordem de emissão deixou de ser a garantia de correção.** Cada alteração nomeia a
    entidade de que fala, então remover um Perfil não move os outros e nenhuma sequência produz
    resultado diferente de outra. A ordem abaixo é a que fica legível no resumo, e só isso.
    """
    alteracoes, resumo = [], []
    grupos = campos_editaveis(conteudo)
    grupos_removidos = _marcados_para_remover(dados, grupos)
    removidos = [grupo["caminho"] for grupo in grupos_removidos]

    def dentro_de_removido(caminho):
        """Remover um Perfil leva junto as modalidades dele: alterá-las não teria efeito."""
        return any(
            caminho == removido or caminho.startswith(f"{removido}/") for removido in removidos
        )

    for grupo in grupos:
        # Alterar campo de linha que será removida não tem efeito e confundiria o resumo.
        if grupo["caminho"] and dentro_de_removido(grupo["caminho"]):
            continue
        for campo in grupo["campos"]:
            enviado = dados.get(f"campo:{campo['referencia']}")
            if enviado is None:
                continue
            novo_valor = _converter(enviado, campo["tipo"], campo["rotulo"])
            anterior = _ler(conteudo, campo["caminho"])
            if campo["tipo"] == INSTANTE:
                if _mesmo_instante(anterior, novo_valor):
                    continue
            elif str(anterior if anterior is not None else "") == str(
                novo_valor if novo_valor is not None else ""
            ):
                continue
            alteracoes.append(
                {"targetPath": campo["caminho"], "operation": "REPLACE", "newValue": novo_valor}
            )
            resumo.append(
                {
                    "grupo": grupo["titulo"],
                    "rotulo": campo["rotulo"],
                    "antes": _para_formulario(anterior, campo["tipo"]) or "—",
                    "depois": _para_formulario(novo_valor, campo["tipo"]) or "—",
                }
            )

    for grupo in grupos_removidos:
        atual = _ler(conteudo, grupo["caminho"]) or {}
        nome = atual.get("name") or atual.get("type") or atual.get("code")
        alteracoes.append({"targetPath": grupo["caminho"], "operation": "REMOVE"})
        resumo.append(
            {
                # O título do grupo já nomeia a entidade em qualquer coleção; derivar o rótulo
                # do prefixo do caminho errava para modalidade, que também começa em /profiles.
                "grupo": grupo["titulo"],
                "rotulo": "Remoção",
                "antes": nome or "—",
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
                "grupo": f"Perfil {valores.get('code') or ''}".strip(),
                "rotulo": "Acréscimo",
                "antes": "—",
                "depois": valores.get("name") or "novo Perfil",
            }
        )

    eventos_removidos = [caminho for caminho in removidos if caminho.startswith("/schedule/")]
    proxima_ordem = len(conteudo.get("schedule") or []) - len(eventos_removidos)
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
                "grupo": f"Evento {valores.get('type') or ''}".strip(),
                "rotulo": "Acréscimo",
                "antes": "—",
                "depois": valores.get("description") or "novo Evento",
            }
        )

    return alteracoes, resumo
