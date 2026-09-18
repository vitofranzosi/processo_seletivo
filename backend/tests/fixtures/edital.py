from uuid import NAMESPACE_URL, uuid5

PROFILE_ID = "00000000-0000-0000-0000-000000000401"
EVENT_ID = "00000000-0000-0000-0000-000000000402"


def identificador(base, seed):
    """Ids distintos por Edital: Perfil e Evento são únicos globalmente."""
    return f"00000000-0000-0000-0000-{base + seed * 10:012d}"


#: O método do sorteio do marco mínimo, inteiro — porque método pela metade não publica (021,
#: FR-013). Os valores saem dos vocabulários fechados que este sistema executa: trocar qualquer um
#: por texto inventado faz a publicação recusar, e a recusa é a certa.
DRAW_METHOD = {
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "source": "Fonte de demonstração",
    "occurrence": "5900",
    "occurrenceAt": "2020-01-01T20:00:00-03:00",
    "derivation": "a extração de sábado imediatamente anterior à data publicada",
    "normalization": {
        "rule": "DIGITOS_EM_SEQUENCIA",
        "text": "os cinco números sorteados, na ordem dos prêmios",
    },
    "substitutionRule": {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "não havendo extração na data, vale a extração seguinte da mesma fonte",
    },
}


def identidade_do_marco(perfil_id):
    """A identidade do marco mínimo, derivada da do Perfil.

    **Derivada, e não literal**, pela mesma razão que a linha geral do quadro é (027, T-001): o
    marco é único globalmente, e um identificador literal colide assim que dois construtores o
    escolhem — foi o que aconteceu na primeira tentativa, com um número que já pertencia a outra
    coleção deslocada por `seed`. Derivar do Perfil torna a colisão impossível sem tirar do teste
    a capacidade de reproduzir a identidade sem ler o conteúdo publicado.
    """
    return str(uuid5(NAMESPACE_URL, f"marco:{perfil_id}"))


def marco_minimo(identidade, *, codigo="M1", nome="Sorteio público"):
    """O marco que torna um Perfil **publicável**, e o mínimo que a `032` exige dele.

    Três decisões, e cada uma responde a um requisito:

    **Existe** — `FR-457` recusa a publicação de Edital em que algum Perfil não declare marco
    algum, porque sem marco ninguém é classificado por aquele Perfil. Era assim que a auditoria de
    16/09/2026 publicava um Edital inútil sem que nada acusasse.

    **Ordena por sorteio, e por isso não enumera Etapa** — marco que ordena pela pontuação precisa
    de Etapa, e exigi-la faria toda fixture mínima do repositório publicar um Cronograma de
    avaliação que ela não tem. A `030` fixou que sortear sem Etapa é legítimo (`FR-432`).

    **Publica o método inteiro** — `FR-467` recusa quem sorteia e não publica método, e a `021` já
    recusava o método pela metade. Os valores saem dos vocabulários fechados que este sistema
    executa; texto inventado faz a publicação recusar, e a recusa é a certa.

    **E declara que o corte não governa Etapa alguma** (`FR-224` da `014`) — que é a forma do
    69/2026, o Edital mais simples e mais comum da amostra: sorteia, publica, convoca e manda
    comparecer, sem análise documental entre a ordem e a chamada. A ausência da regra é estado
    legítimo e recebe aviso na publicação (`FR-461`); declará-la não silencia o aviso, apenas faz
    com que ele não tenha o que dizer sobre este marco.
    """
    return {
        "id": identidade,
        "code": codigo,
        "name": nome,
        "orderProduction": "POR_SORTEIO",
        "stages": [],
        "operation": "SOMA_PONDERADA",
        "normalization": "NENHUMA",
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "tiebreakers": [],
        "drawMethod": dict(DRAW_METHOD),
        "cutRule": {
            "targetKind": "FIXED",
            "targetCount": 1,
            "surplusCount": 0,
            "tieOutcome": "STRICT",
            "governedStage": "NONE",
            "continuation": "NONE",
        },
    }


def complete_draft(seed=0):
    """O Edital mínimo **publicável**, e a palavra que carrega peso aqui é a segunda.

    **Ele ganhou um marco na `032`, e o marco não é enfeite de fixture.** A `FR-457` passou a
    recusar a publicação de Edital em que algum Perfil não declare marco classificatório algum —
    porque sem marco ninguém é classificado por aquele Perfil, e foi assim que a auditoria de
    16/09/2026 publicou um Edital inútil sem que nada acusasse. Um rascunho sem marco continua
    sendo gravado; o que deixou de existir é o Edital **publicado** sem marco.

    **Por sorteio, e não por pontuação**, e a escolha é a que mantém este rascunho mínimo. Marco
    que ordena pela pontuação precisa enumerar Etapa — sem Etapa não há pontuação a combinar —, e
    exigi-la aqui obrigaria o rascunho mais simples do repositório a publicar um Cronograma de
    avaliação que ele não tem. A `030` fixou que um marco pode sortear sem enumerar Etapa alguma
    (`FR-432`), e a `032` exige apenas que quem sorteia publique o método (`FR-467`) — que é o que
    `DRAW_METHOD` declara, inteiro.
    """
    return {
        "profiles": [
            {
                "id": identificador(401, seed),
                "code": "P1",
                "name": "Perfil",
                "immediateVacancies": 1,
                "reserveType": "NONE",
                "competitionModalities": [],
                "classificationMilestones": [
                    marco_minimo(identidade_do_marco(identificador(401, seed)))
                ],
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
