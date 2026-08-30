"""Tradução entre o que a pessoa digita e o payload que os commands esperam.

Aqui não há regra de domínio: a validação real acontece em `editais.domain`, invocada pelo
command. O que existe aqui é conversão de tipo e agrupamento de campos indexados — e as
mensagens que tornam um erro de conversão compreensível antes de chegar ao domínio.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

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


def _instante(dados, chave):
    """`datetime-local` chega sem fuso; a zona institucional é aplicada aqui."""
    bruto = _texto(dados, chave)
    if not bruto:
        return None
    try:
        return datetime.fromisoformat(bruto).replace(tzinfo=ZONA)
    except ValueError as exc:
        raise ValueError(f"'{bruto}' não é uma data e hora válidas.") from exc


def _modalidades(bruto):
    """Uma modalidade por linha, no formato `CÓDIGO — Nome`."""
    modalidades = []
    for linha in bruto.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        codigo, _, nome = linha.partition("—")
        if not nome:
            codigo, _, nome = linha.partition("-")
        modalidades.append({"code": codigo.strip() or linha, "name": nome.strip() or linha})
    return modalidades


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
                "competitionModalities": _modalidades(_texto(dados, f"{base}-modalidades")),
            }
        )
    return perfis


def ler_eventos(dados):
    eventos = []
    for ordem, indice in enumerate(_indices(dados, "evento"), 1):
        base = f"evento-{indice}"
        eventos.append(
            {
                "id": _texto(dados, f"{base}-id"),
                "type": _texto(dados, f"{base}-type"),
                "description": _texto(dados, f"{base}-description"),
                "startAt": _instante(dados, f"{base}-startAt"),
                "endAt": _instante(dados, f"{base}-endAt"),
                "order": ordem,
            }
        )
    return eventos


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
            "modalidades": "\n".join(
                # Linha sem separador vira código e nome iguais; repeti-la só faz ruído.
                m.name if m.code == m.name else f"{m.code} — {m.name}"
                for m in perfil.modalidades.order_by("code")
            ),
        }
        for perfil in edital.perfis.prefetch_related("modalidades").order_by("code")
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
            "competitionModalities": [
                {"code": m.code, "name": m.name}
                for m in perfil.modalidades.order_by("code")
            ],
        }
        for perfil in edital.perfis.prefetch_related("modalidades").order_by("code")
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
