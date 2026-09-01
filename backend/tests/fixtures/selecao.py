"""Uma seleção publicada, do jeito que o candidato a encontra.

O `complete_draft` das features anteriores tem um Perfil mínimo, o suficiente para exercitar
publicação e retificação. A jornada do candidato precisa de outra coisa: dois Perfis, para que
escolher signifique algo, e uma modalidade reservada ao lado da ampla concorrência, para que a
aplicabilidade de documento tenha as quatro combinações a partir da entrega 2.
"""

from datetime import timedelta

from tests.fixtures.edital import identificador
from tests.fixtures.publicacao import publish_original

PERFIL_DOCENTE = "DOC-INFO"
PERFIL_TECNICO = "TEC-LAB"


def rascunho_de_selecao(seed=0):
    return {
        "profiles": [
            {
                "id": identificador(401, seed),
                "code": PERFIL_DOCENTE,
                "name": "Professor de Informática",
                "description": "Docência em Informática no ensino técnico e superior.",
                "requirements": [
                    "Mestrado em Computação ou área afim",
                    "Experiência docente de dois anos",
                ],
                "immediateVacancies": 2,
                "reserveType": "LIMITED",
                "reserveLimit": 6,
                "locality": "Campus Serra",
                "competitionModalities": [
                    {"id": identificador(403, seed), "code": "AC", "name": "Ampla concorrência"},
                    {
                        "id": identificador(404, seed),
                        "code": "PPP",
                        "name": "Pessoas pretas, pardas e indígenas",
                        "normativeRule": {
                            "id": identificador(405, seed),
                            "foundation": "Lei 12.990/2014",
                            "version": "2014-06-09",
                            "percentage": "20.0000",
                            "rounding": {"modo": "PARA_CIMA"},
                        },
                    },
                ],
            },
            {
                "id": identificador(406, seed),
                "code": PERFIL_TECNICO,
                "name": "Técnico de Laboratório",
                "description": "Apoio técnico aos laboratórios de informática.",
                "requirements": ["Curso técnico em Informática"],
                "immediateVacancies": 0,
                "reserveType": "UNLIMITED",
                "locality": "Campus Vitória",
                "competitionModalities": [
                    {"id": identificador(407, seed), "code": "AC", "name": "Ampla concorrência"}
                ],
            },
        ],
        "schedule": [
            {
                "id": identificador(402, seed),
                "type": "Inscrições",
                "description": "Período de inscrições",
                "startAt": "2026-09-01T09:00:00-03:00",
                "endAt": "2026-09-29T23:59:00-03:00",
                "order": 1,
            }
        ],
    }


def publicar_selecao(api_client, manager_headers, process_payload, *, seed=0, rascunho=None):
    """Cria, elabora, submete, homologa e publica a seleção — pelo canal administrativo."""
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho or rascunho_de_selecao(seed)
    )


# Os três documentos do cenário emblemático: um de todos, um do Perfil docente, um da modalidade
# reservada. É o que faz o candidato de ampla concorrência receber dois pedidos e o da modalidade,
# três — a diferença que a aplicabilidade existe para produzir.
DOCUMENTO_DE_TODOS = identificador(408, 0)
DOCUMENTO_DO_PERFIL = identificador(409, 0)
DOCUMENTO_DA_MODALIDADE = identificador(410, 0)


def documentos_exigidos():
    return [
        {
            "id": DOCUMENTO_DE_TODOS,
            "key": "identificacao",
            "name": "Documento de identificação",
            "instructions": "Frente e verso em arquivo único.",
            "required": True,
            "order": 1,
        },
        {
            "id": DOCUMENTO_DO_PERFIL,
            "key": "diploma",
            "name": "Diploma de graduação",
            "required": True,
            "order": 2,
            "profileId": identificador(401, 0),
        },
        {
            "id": DOCUMENTO_DA_MODALIDADE,
            "key": "autodeclaracao",
            "name": "Autodeclaração étnico-racial",
            "required": True,
            "order": 3,
            "modalityId": identificador(404, 0),
        },
    ]


def rascunho_aberto_com_documentos(agora):
    """Seleção com período aberto e os três documentos — o rascunho de toda a entrega 4."""
    rascunho = rascunho_de_selecao()
    rascunho["schedule"][0]["startAt"] = (agora - timedelta(days=1)).isoformat()
    rascunho["schedule"][0]["endAt"] = (agora + timedelta(days=10)).isoformat()
    rascunho["schedule"][0]["isRegistrationPeriod"] = True
    rascunho["documentRequirements"] = documentos_exigidos()
    return rascunho
