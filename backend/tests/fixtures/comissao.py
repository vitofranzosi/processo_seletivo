"""Um Processo publicado com Etapas — a precondição de tudo na 011.

`complete_draft` e `rascunho_de_selecao` não declaram Etapas: as features anteriores não
precisavam delas. A 011 precisa de duas no mesmo Edital, para que "alocado em A1 e não em A2"
seja demonstrável, e de um segundo Processo para que "Etapa de outro Processo" também seja.
"""

from tests.fixtures.edital import complete_draft, identificador
from tests.fixtures.publicacao import publish_original

ETAPA_A1 = 410
ETAPA_A2 = 411


def etapas(seed=0):
    return [
        {
            "id": identificador(ETAPA_A1, seed),
            "name": "Análise documental",
            "order": 1,
            "eliminatory": True,
            "classificatory": False,
            "scheduleEventId": identificador(402, seed),
        },
        {
            "id": identificador(ETAPA_A2, seed),
            "name": "Prova didática",
            "order": 2,
            "eliminatory": False,
            "classificatory": True,
        },
    ]


def rascunho_com_etapas(seed=0):
    return {**complete_draft(seed), "stages": etapas(seed)}


def publicar_processo_com_etapas(api_client, manager_headers, process_payload, *, seed=0):
    """Cria, elabora, submete, homologa e publica — pelo canal administrativo, como a 009 faz."""
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas(seed)
    )
