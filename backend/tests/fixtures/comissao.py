"""Um Processo publicado com Etapas — a precondição de tudo na 011.

`complete_draft` e `rascunho_de_selecao` não declaram Etapas: as features anteriores não
precisavam delas. A 011 precisa de duas no mesmo Edital, para que "alocado em A1 e não em A2"
seja demonstrável, e de um segundo Processo para que "Etapa de outro Processo" também seja.
"""

from tests.fixtures.edital import complete_draft, identificador
from tests.fixtures.publicacao import publish_original

ETAPA_A1 = 410
ETAPA_A2 = 411


def etapas(seed=0, *, avaliacoes=None, maxima=None):
    """As duas Etapas dos cenários. `avaliacoes` e `maxima` declaram o que a `012` acrescentou.

    Ficam opcionais de propósito: a maioria dos testes fala de Etapa **sem** declaração, que é o
    caso do Edital publicado antes do incremento — e é ali que a leitura da ausência vale.
    """
    declaracao = {}
    if avaliacoes is not None:
        declaracao["evaluationsPerRegistration"] = avaliacoes
    if maxima is not None:
        declaracao["maximumScore"] = maxima
    return [
        {
            "id": identificador(ETAPA_A1, seed),
            "name": "Análise documental",
            "order": 1,
            "eliminatory": True,
            "classificatory": False,
            "scheduleEventId": identificador(402, seed),
            **declaracao,
        },
        {
            "id": identificador(ETAPA_A2, seed),
            "name": "Prova didática",
            "order": 2,
            "eliminatory": False,
            "classificatory": True,
        },
    ]


def rascunho_com_etapas(seed=0, **declaracao):
    return {**complete_draft(seed), "stages": etapas(seed, **declaracao)}


def publicar_processo_com_etapas(
    api_client, manager_headers, process_payload, *, seed=0, **declaracao
):
    """Cria, elabora, submete, homologa e publica — pelo canal administrativo, como a 009 faz."""
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas(seed, **declaracao)
    )


def constituir(gestor, processo, pessoas, *, prefixo="constituir"):
    """Constitui a comissão pelo command, e devolve `{subject: membro}`.

    `prefixo` existe porque a chave de idempotência é derivada da posição: constituir em duas
    chamadas separadas reusaria `...-0` com outro conteúdo, e a reserva recusaria — corretamente.
    """
    from processo_seletivo.comissoes.application.comissao import adicionar_membro

    membros = {}
    for indice, (subject, funcao) in enumerate(pessoas):
        membro, _ = adicionar_membro(
            actor=gestor,
            processo_id=processo.id,
            identity_subject=subject,
            funcao=funcao,
            idempotency_key=f"{prefixo}-{processo.id}-{indice}",
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


def inscrever(edital, quantos=1, *, primeiro=1):
    """Inscrições **submetidas** — o único estado atribuível (FR-012).

    O protocolo é o que a tela mostra e o que a trilha guarda, então ele nasce aqui em vez de
    ficar em branco: sem ele, as asserções teriam de falar por UUID.
    """
    from django.utils import timezone

    from processo_seletivo.inscricoes.models import Inscricao
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    agora = timezone.now()
    return [
        Inscricao.objects.create(
            created_at=agora,
            identity_subject=f"cpf:candidato-{numero:04d}",
            edital=edital,
            profile_id="00000000-0000-0000-0000-000000000401",
            status=Inscricao.Status.SUBMETIDA,
            nome=f"Candidata {numero}",
            cpf="111.444.777-35",
            cpf_normalizado="11144477735",
            email=f"candidata{numero}@exemplo.br",
            protocolo=f"{numero:04d}",
            submitted_at=agora,
            versao_aceita=versao,
            declaracoes_aceitas_em=agora,
        )
        for numero in range(primeiro, primeiro + quantos)
    ]
