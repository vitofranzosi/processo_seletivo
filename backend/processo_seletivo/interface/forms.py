"""Tradução entre o que a pessoa digita e o payload que os commands esperam.

Aqui não há regra de domínio: a validação real acontece em `editais.domain`, invocada pelo
command. O que existe aqui é conversão de tipo e agrupamento de campos indexados — e as
mensagens que tornam um erro de conversão compreensível antes de chegar ao domínio.
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from uuid import uuid4
from zoneinfo import ZoneInfo

from processo_seletivo.editais.domain import secoes

ZONA = ZoneInfo("America/Sao_Paulo")

RESERVA = [
    ("NONE", "Não há cadastro reserva"),
    ("LIMITED", "Cadastro reserva limitado"),
    ("UNLIMITED", "Cadastro reserva ilimitado"),
]


def _indices(dados, prefixo):
    """Índices presentes no formulário, em ordem — as linhas podem ter buracos após remoções."""
    vistos = set()
    for chave in dados:
        if chave.startswith(f"{prefixo}-") and chave.endswith("-id"):
            vistos.add(chave[len(prefixo) + 1 : -3])
    return sorted(vistos, key=lambda valor: int(valor) if valor.isdigit() else valor)


def _texto(dados, chave):
    return (dados.get(chave) or "").strip()


def _inteiro(dados, chave, padrao=0):
    bruto = _texto(dados, chave)
    if not bruto:
        return padrao
    try:
        return int(bruto)
    except ValueError as exc:
        raise ValueError(f"'{bruto}' não é um número inteiro.") from exc


def _decimal(dados, chave):
    """Vazio é ausência, e ausência tem significado: 'esta Etapa não pondera'."""
    bruto = _texto(dados, chave)
    if not bruto:
        return None
    try:
        return Decimal(bruto.replace(",", "."))
    except InvalidOperation as exc:
        raise ValueError(f"'{bruto}' não é um número válido.") from exc


def _marcado(dados, chave):
    return bool(_texto(dados, chave))


def _instante(dados, chave):
    """`datetime-local` chega sem fuso; a zona institucional é aplicada aqui."""
    bruto = _texto(dados, chave)
    if not bruto:
        return None
    try:
        return datetime.fromisoformat(bruto).replace(tzinfo=ZONA)
    except ValueError as exc:
        raise ValueError(f"'{bruto}' não é uma data e hora válidas.") from exc


def _modalidades(dados, prefixo):
    """As modalidades de um Perfil, em campos próprios.

    Substitui a caixa de texto no formato `CÓDIGO — Nome`, que perdia tudo o que não coubesse em
    duas palavras: percentual, fundamento e versão do fundamento não tinham onde ser digitados, e
    a Regra Normativa era destruída a cada gravação.

    A Regra só é montada quando há fundamento. Ela é opcional; o que não é opcional é a `version`
    quando ela existe — o command a exige desde a `001`.
    """
    modalidades = []
    for indice in _indices(dados, prefixo):
        base = f"{prefixo}-{indice}"
        fundamento = _texto(dados, f"{base}-foundation")
        modalidade = {
            "id": _texto(dados, f"{base}-id"),
            "code": _texto(dados, f"{base}-code"),
            "name": _texto(dados, f"{base}-name"),
            "description": _texto(dados, f"{base}-description"),
        }
        if fundamento or _texto(dados, f"{base}-version") or _texto(dados, f"{base}-percentage"):
            modalidade["normativeRule"] = {
                "id": _texto(dados, f"{base}-ruleId"),
                "foundation": fundamento,
                "version": _texto(dados, f"{base}-version"),
                "percentage": _decimal(dados, f"{base}-percentage"),
            }
        modalidades.append(modalidade)
    return modalidades


def ler_identificacao(dados):
    """Título e descrição; número e ano continuam sendo da criação do Edital."""
    return {"title": _texto(dados, "title"), "description": _texto(dados, "description")}


def ler_perfis(dados):
    perfis = []
    for indice in _indices(dados, "perfil"):
        base = f"perfil-{indice}"
        reserva = _texto(dados, f"{base}-reserveType") or "NONE"
        limite = _texto(dados, f"{base}-reserveLimit")
        perfis.append(
            {
                "id": _texto(dados, f"{base}-id"),
                "code": _texto(dados, f"{base}-code"),
                "name": _texto(dados, f"{base}-name"),
                "description": _texto(dados, f"{base}-description"),
                "requirements": [
                    linha.strip()
                    for linha in _texto(dados, f"{base}-requirements").splitlines()
                    if linha.strip()
                ],
                "immediateVacancies": _inteiro(dados, f"{base}-immediateVacancies"),
                "reserveType": reserva,
                "reserveLimit": int(limite) if reserva == "LIMITED" and limite else None,
                "locality": _texto(dados, f"{base}-locality"),
                "duties": _texto(dados, f"{base}-duties"),
                "workload": _texto(dados, f"{base}-workload"),
                "compensation": _texto(dados, f"{base}-compensation"),
                # As linhas de modalidade são indexadas dentro do índice do Perfil, e não
                # renumeradas: `modalidade-3-…` pertence ao Perfil cujo prefixo é `perfil-3`.
                "competitionModalities": _modalidades(dados, f"modalidade-{indice}"),
            }
        )
    return perfis


def ler_eventos(dados):
    """A ordem é dado enviado, e não a posição de leitura das linhas.

    `_indices` devolve os índices **ordenados numericamente**, de modo que a posição da linha no
    documento é descartada antes de chegar aqui: mover a linha na tela, sozinho, não mudaria nada, e
    o defeito seria silencioso — a tela mostraria a ordem nova e o banco guardaria a antiga. Por
    isso cada linha carrega o próprio `order`, que os botões de subir e descer atualizam.

    A renumeração final é do servidor: o que vem do formulário estabelece a **sequência**, e não os
    números, que precisam ser 1..n sem buraco por causa da unicidade de `(cronograma, order)`.
    """
    eventos = []
    for indice in _indices(dados, "evento"):
        base = f"evento-{indice}"
        eventos.append(
            {
                "id": _texto(dados, f"{base}-id"),
                "type": _texto(dados, f"{base}-type"),
                "description": _texto(dados, f"{base}-description"),
                "startAt": _instante(dados, f"{base}-startAt"),
                "endAt": _instante(dados, f"{base}-endAt"),
                "order": _inteiro(dados, f"{base}-order", 0),
            }
        )
    return _renumerar(eventos)


def _renumerar(itens):
    """A sequência vem do formulário; os números, do servidor.

    A unicidade de `(edital, order)` não admite buraco nem repetição, e o formulário pode chegar
    com as duas coisas — uma remoção deixa buraco, e um navegador sem JavaScript manda tudo igual.
    A ordenação é estável, então nesse último caso a ordem de leitura prevalece, que é o
    comportamento anterior.
    """
    itens.sort(key=lambda item: item["order"])
    for ordem, item in enumerate(itens, 1):
        item["order"] = ordem
    return itens


def ler_etapas(dados):
    etapas = []
    for indice in _indices(dados, "etapa"):
        base = f"etapa-{indice}"
        etapas.append(
            {
                "id": _texto(dados, f"{base}-id"),
                "name": _texto(dados, f"{base}-name"),
                "order": _inteiro(dados, f"{base}-order", 0),
                "weight": _decimal(dados, f"{base}-weight"),
                "eliminatory": _marcado(dados, f"{base}-eliminatory"),
                "classificatory": _marcado(dados, f"{base}-classificatory"),
                "minimumScore": _decimal(dados, f"{base}-minimumScore"),
                # Vazio é "não vinculada a Evento", e não Evento inexistente.
                "scheduleEventId": _texto(dados, f"{base}-scheduleEventId") or None,
            }
        )
    return _renumerar(etapas)


def _modalidade_para_o_formulario(modalidade):
    regra = getattr(modalidade, "regra_normativa", None)
    return {
        "id": str(modalidade.id),
        "code": modalidade.code,
        "name": modalidade.name,
        "description": modalidade.description,
        # A linha carrega os dois identificadores. O da Regra existe mesmo quando ela ainda não
        # existe: a linha nova precisa nascer com identidade, ou não há o que preservar.
        "ruleId": str(regra.id) if regra else str(uuid4()),
        "foundation": regra.foundation if regra else "",
        "version": regra.version if regra else "",
        "percentage": ""
        if regra is None or regra.percentage is None
        else f"{regra.percentage:f}",
    }


def ler_secoes(dados):
    """Só as textuais, e só as que **mudaram** em relação ao catálogo.

    A tela mostra as sete seções e envia as quatro textuais preenchidas; gravar todas criaria linha
    para seção que ninguém tocou, e a regra "ausência de linha significa texto padrão do catálogo"
    deixaria de valer no primeiro salvamento desta etapa. O efeito prático seria congelar a redação
    institucional: corrigir o texto padrão em código não alcançaria mais nenhum Edital que tivesse
    passado por aqui, e não haveria como distinguir texto revisado de texto intocado.

    A comparação é sobre o texto sem espaço nas bordas: um `\\r\\n` que o navegador acrescenta não é
    edição.
    """
    editadas = []
    for chave in sorted(secoes.CHAVES_TEXTUAIS):
        digitado = _texto(dados, f"secao-{chave}")
        padrao = secoes.POR_CHAVE[chave].default_text
        if digitado and digitado != padrao.strip():
            editadas.append({"key": chave, "content": digitado})
    return editadas


def secoes_do_edital(edital):
    """O catálogo inteiro, na ordem, com o texto vigente de cada seção textual.

    As geradas aparecem para que quem elabora veja a estrutura do documento — e leia, ao lado de
    cada uma, de que dado ela vem. Elas não têm campo de texto: o conteúdo se corrige no dado que
    o origina.
    """
    redigidas = {item.key: item.content for item in edital.secoes.all()}
    return [
        {
            "key": secao.key,
            "title": secao.title,
            "order": secao.order,
            "gerada": secao.gerada,
            "source": secao.source,
            "origem": ORIGEM.get(secao.source, (secao.source, ""))[0],
            "etapa_da_origem": ORIGEM.get(secao.source, ("", ""))[1],
            "content": redigidas.get(secao.key, secao.default_text),
            "editada": secao.key in redigidas,
        }
        for secao in secoes.CATALOGO
    ]


# Como cada origem é lida por quem elabora, e onde ela se edita. A chave é a coleção do snapshot,
# e o valor liga o vocabulário do conteúdo publicado ao do assistente — que é o que permite
# oferecer, ao lado de uma seção gerada, o caminho para o dado que a origina.
ORIGEM = {
    "profiles": ("Perfis de Vaga", "perfis"),
    "schedule": ("Cronograma", "cronograma"),
    "stages": ("Etapas de Avaliação", "etapas"),
}


def secoes_persistidas(edital):
    """Seções textuais já editadas, no formato do command — para preservá-las ao salvar outra
    etapa. Ausência de linha continua significando "texto padrão do catálogo"."""
    return [{"key": item.key, "content": item.content} for item in edital.secoes.all()]


def perfis_do_edital(edital):
    """Perfis persistidos, no formato que o formulário renderiza."""
    return [
        {
            "id": str(perfil.id),
            "code": perfil.code,
            "name": perfil.name,
            "description": perfil.description,
            "requirements": "\n".join(perfil.requirements or []),
            "immediateVacancies": perfil.immediate_vacancies,
            "reserveType": perfil.reserve_type,
            "reserveLimit": perfil.reserve_limit,
            "locality": perfil.locality,
            "duties": perfil.duties,
            "workload": perfil.workload,
            "compensation": perfil.compensation,
            "modalidades": [
                _modalidade_para_o_formulario(m) for m in perfil.modalidades.order_by("code")
            ],
        }
        for perfil in edital.perfis.prefetch_related("modalidades__regra_normativa").order_by(
            "code"
        )
    ]


def eventos_do_edital(edital):
    cronograma = getattr(edital, "cronograma", None)
    if cronograma is None:
        return []
    return [
        {
            "id": str(evento.id),
            "type": evento.type,
            "description": evento.description,
            "startAt": evento.start_at.astimezone(ZONA).strftime("%Y-%m-%dT%H:%M"),
            "endAt": evento.end_at.astimezone(ZONA).strftime("%Y-%m-%dT%H:%M")
            if evento.end_at
            else "",
            "order": evento.order,
        }
        for evento in cronograma.eventos.order_by("order")
    ]


def perfis_persistidos(edital):
    """Perfis já salvos, no formato do command — para preservá-los ao salvar outra etapa."""
    return [
        {
            "id": str(perfil.id),
            "code": perfil.code,
            "name": perfil.name,
            "description": perfil.description,
            "requirements": perfil.requirements or [],
            "immediateVacancies": perfil.immediate_vacancies,
            "reserveType": perfil.reserve_type,
            "reserveLimit": perfil.reserve_limit,
            "locality": perfil.locality,
            "duties": perfil.duties,
            "workload": perfil.workload,
            "compensation": perfil.compensation,
            # A modalidade inteira, com a Regra e os dois identificadores. Antes daqui só `code` e
            # `name` viajavam: salvar o Cronograma relia os Perfis, reenviava metade da modalidade
            # e apagava a Regra Normativa — configurar cotas e ir a outra etapa destruía o que
            # tinha sido configurado.
            "competitionModalities": [
                _modalidade_persistida(m) for m in perfil.modalidades.order_by("code")
            ],
        }
        for perfil in edital.perfis.prefetch_related("modalidades__regra_normativa").order_by(
            "code"
        )
    ]


def _modalidade_persistida(modalidade):
    regra = getattr(modalidade, "regra_normativa", None)
    persistida = {
        "id": str(modalidade.id),
        "code": modalidade.code,
        "name": modalidade.name,
        "description": modalidade.description,
    }
    if regra is not None:
        persistida["normativeRule"] = {
            "id": str(regra.id),
            "foundation": regra.foundation,
            "version": regra.version,
            "percentage": regra.percentage,
            "calculation": regra.calculation,
            "rounding": regra.rounding,
            "distribution": regra.distribution,
            "callRules": regra.call_rules,
            "effectiveFrom": regra.effective_from,
        }
    return persistida


def etapas_do_edital(edital):
    """Etapas persistidas, no formato que o formulário renderiza."""
    return [
        {
            "id": str(etapa.id),
            "name": etapa.name,
            "order": etapa.order,
            "weight": "" if etapa.weight is None else f"{etapa.weight:f}",
            "eliminatory": etapa.eliminatory,
            "classificatory": etapa.classificatory,
            "minimumScore": "" if etapa.minimum_score is None else f"{etapa.minimum_score:f}",
            "scheduleEventId": "" if etapa.evento_id is None else str(etapa.evento_id),
        }
        for etapa in edital.etapas.order_by("order")
    ]


def etapas_persistidas(edital):
    """Etapas já salvas, no formato do command — para preservá-las ao salvar outra etapa."""
    return [
        {
            "id": str(etapa.id),
            "name": etapa.name,
            "order": etapa.order,
            "weight": etapa.weight,
            "eliminatory": etapa.eliminatory,
            "classificatory": etapa.classificatory,
            "minimumScore": etapa.minimum_score,
            "scheduleEventId": None if etapa.evento_id is None else str(etapa.evento_id),
        }
        for etapa in edital.etapas.order_by("order")
    ]


def eventos_persistidos(edital):
    cronograma = getattr(edital, "cronograma", None)
    if cronograma is None:
        return []
    return [
        {
            "id": str(evento.id),
            "type": evento.type,
            "description": evento.description,
            "startAt": evento.start_at,
            "endAt": evento.end_at,
            "order": evento.order,
        }
        for evento in cronograma.eventos.order_by("order")
    ]
