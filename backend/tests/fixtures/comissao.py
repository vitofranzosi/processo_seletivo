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


def constituir(gestor, processo, pessoas):
    """Constitui a comissão pelo command, e devolve `{subject: membro}`."""
    from processo_seletivo.comissoes.application.comissao import adicionar_membro

    membros = {}
    for indice, (subject, funcao) in enumerate(pessoas):
        membro, _ = adicionar_membro(
            actor=gestor,
            processo_id=processo.id,
            identity_subject=subject,
            funcao=funcao,
            idempotency_key=f"constituir-{processo.id}-{indice}",
            correlation_id="fixture",
        )
        membros[subject] = membro
    return membros


def alocar_em(gestor, processo, membro, edital, etapa_id, *, chave=None):
    from processo_seletivo.comissoes.application.alocacao import alocar

    alocacao, _ = alocar(
        actor=gestor,
        processo_id=processo.id,
        membro_id=membro.id,
        edital_id=edital.id,
        etapa_id=etapa_id,
        idempotency_key=chave or f"alocar-{membro.id}-{etapa_id}",
        correlation_id="fixture",
    )
    return alocacao
