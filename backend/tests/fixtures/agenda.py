"""Editais publicados com cronogramas que se cruzam no tempo — o cenário da Agenda (101).

As datas são sempre relativas a hoje e futuras (ou já em curso), porque publicar Edital com prazo
vencido é recusado (028): a agenda é lida no relógio de verdade, como a pessoa a lê.
"""

from datetime import datetime, time, timedelta

from django.utils import timezone

from processo_seletivo.shared.tempo import ZONA
from tests.fixtures.edital import identificador
from tests.fixtures.selecao import publicar_selecao, rascunho_de_selecao


def em(dias, hora=9, minuto=0):
    """Um instante a `dias` de hoje, na zona institucional."""
    hoje = timezone.now().astimezone(ZONA).date()
    return datetime.combine(hoje + timedelta(days=dias), time(hora, minuto), tzinfo=ZONA)


def evento(seed, n, descricao, inicio, fim=None, **extra):
    return {
        "id": identificador(510 + n, seed),
        "type": descricao.split()[0],
        "description": descricao,
        "startAt": inicio.isoformat(),
        "endAt": fim.isoformat() if fim else None,
        "order": n,
        **extra,
    }


def cronograma(seed, *, prova=3):
    return [
        evento(seed, 0, "Período de inscrições", em(1), em(10, 18), isRegistrationPeriod=True),
        evento(seed, 1, "Prova objetiva", em(prova, 14)),
    ]


def publicar(api_client, manager_headers, process_payload, seed, eventos=None, *, titulo=None):
    """Um Processo com um Edital publicado, de número `seed`, com o cronograma pedido."""
    rascunho = rascunho_de_selecao(seed)
    rascunho["schedule"] = eventos or cronograma(seed)
    carga = {
        **process_payload,
        "institutionalCode": f"PS-AGENDA-{seed}",
        "title": titulo or f"Processo da agenda {seed}",
        "firstEdital": {**process_payload["firstEdital"], "number": f"{seed}"},
    }
    cabecalhos = {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"agenda-101-selecao-{seed:04d}"}
    return publicar_selecao(api_client, cabecalhos, carga, rascunho=rascunho)
