PROFILE_ID = "00000000-0000-0000-0000-000000000401"
EVENT_ID = "00000000-0000-0000-0000-000000000402"


def identificador(base, seed):
    """Ids distintos por Edital: Perfil e Evento são únicos globalmente."""
    return f"00000000-0000-0000-0000-{base + seed * 10:012d}"


def complete_draft(seed=0):
    return {
        "profiles": [
            {
                "id": identificador(401, seed),
                "code": "P1",
                "name": "Perfil",
                "immediateVacancies": 1,
                "reserveType": "NONE",
                "competitionModalities": [],
            }
        ],
        "schedule": [
            {
                "id": identificador(402, seed),
                "type": "INSCRICAO",
                "description": "Inscrições",
                "startAt": "2026-09-01T09:00:00-03:00",
                "order": 1,
            }
        ],
    }


def actor_headers(subject, permissions, *, if_match=None, key="publication-key-0001"):
    headers = {
        "HTTP_AUTHORIZATION": f"Bearer {subject}|cefor|{','.join(permissions)}",
        "HTTP_IDEMPOTENCY_KEY": key,
        "HTTP_X_CORRELATION_ID": f"correlation-{subject}",
    }
    if if_match is not None:
        headers["HTTP_IF_MATCH"] = f'"{if_match}"'
    return headers


def caminho_perfil(campo="", seed=0):
    """Caminho por chave do Perfil de `complete_draft`, na forma que a gramática admite.

    Os testes conheciam `/profiles/0`. O índice deixou de ser forma admitida onde há chave, e
    concentrar a construção aqui evita que cada arquivo repita a montagem do seletor.
    """
    caminho = f"/profiles/id={identificador(401, seed)}"
    return f"{caminho}/{campo}" if campo else caminho


def caminho_linha_geral(campo="", seed=0):
    """Caminho da linha geral do quadro do Perfil de `complete_draft`.

    A identidade é reproduzível sem ler o conteúdo publicado porque a linha derivada nasce de um
    `uuid5` sobre a identidade do Perfil (027, T-001) — que é o mesmo recurso que torna a gravação
    idempotente para quem grava por API.
    """
    from processo_seletivo.editais.domain.perfis import identidade_da_linha_geral

    linha = identidade_da_linha_geral(identificador(401, seed))
    caminho = f"{caminho_perfil(seed=seed)}/vacancyTable/id={linha}"
    return f"{caminho}/{campo}" if campo else caminho


def mudanca_de_vagas(novo_total, *, seed=0):
    """As **duas** operações que alterar as vagas imediatas exige (027, FR-335).

    Num Perfil sem lista reservada o total e a linha da ampla concorrência são o mesmo número, e
    mover um sem o outro publicaria um quadro que não fecha — a conferência recusa dizendo os dois.
    Os testes que usam "mudar as vagas" como retificação genérica passam por aqui em vez de repetir
    o par, e quem lê vê de uma vez que é um ato só.
    """
    return [
        {
            "targetPath": caminho_perfil("immediateVacancies", seed),
            "operation": "REPLACE",
            "newValue": novo_total,
        },
        {
            "targetPath": caminho_linha_geral("immediateVacancies", seed),
            "operation": "REPLACE",
            "newValue": novo_total,
        },
    ]


def caminho_evento(campo="", seed=0):
    caminho = f"/schedule/id={identificador(402, seed)}"
    return f"{caminho}/{campo}" if campo else caminho
