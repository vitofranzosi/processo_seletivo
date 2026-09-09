"""O Processo com **dois** Editais — a precondição da soma que a `022` existe para dar.

As fixtures anteriores publicam sempre um Processo por Edital, porque nenhuma feature anterior
precisou somar acima do Edital. A `022` precisa: sem dois Editais no mesmo Processo, "o total é a
soma" e "cada Edital aparece nomeado" não são demonstráveis, e o MVP não teria contraprova.
"""

from datetime import timedelta

from django.utils import timezone

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import identificador
from tests.fixtures.publicacao import levar_a_publicacao

# Ids distintos dos da `011`, que usa `seed` 0 e 1: Perfil e Evento são únicos globalmente.
SEGUNDO_SEED = 2
ETAPA_C1 = 430


def perfil_de(seed):
    return identificador(401, seed)


def evento_do_periodo(seed, *, inicio, fim, status=None):
    """O Evento **marcado** como período de inscrições — a marca, e nunca o texto do tipo.

    `status` viaja porque ele é metade da divergência de `UX-002`: um período em curso declarado
    `PLANEJADO` produz sinal, e um cenário que não escolhesse o estado o produziria sem querer —
    poluindo todo teste sobre os outros quatro sinais.
    """
    declarado = {} if status is None else {"status": status}
    return {
        "id": identificador(402, seed),
        "type": "INSCRICAO",
        "description": "Inscrições",
        "startAt": inicio.isoformat(),
        "endAt": None if fim is None else fim.isoformat(),
        "order": 1,
        "isRegistrationPeriod": True,
        **declarado,
    }


def evento_simples(seed, *, base, descricao, inicio, fim=None, ordem=2, status=None):
    """Um Evento comum do cronograma — o que a supervisão lê como marco.

    `status` viaja porque a divergência de `UX-002` é entre ele e a posição temporal: sem poder
    declará-lo, a tabela-verdade de `T-005` não teria como ser montada.
    """
    declarado = {} if status is None else {"status": status}
    return {
        "id": identificador(base, seed),
        "type": "MARCO",
        "description": descricao,
        "startAt": inicio.isoformat(),
        "endAt": None if fim is None else fim.isoformat(),
        "order": ordem,
        **declarado,
    }


def rascunho_com_periodo(
    seed, *, inicio=None, fim=None, eventos=None, etapas=None, status_do_periodo=None
):
    """Um Edital publicável com período de inscrições declarado.

    `eventos` substitui o cronograma inteiro quando o cenário precisa de mais de um Evento — é
    como os testes de `UX-002` montam a divergência temporal.
    """
    agora = timezone.now()
    inicio = agora - timedelta(days=5) if inicio is None else inicio
    fim = agora + timedelta(days=5) if fim is None else fim
    return {
        "profiles": [
            {
                "id": perfil_de(seed),
                "code": f"P{seed}",
                "name": "Perfil",
                "immediateVacancies": 1,
                "reserveType": "NONE",
                "competitionModalities": [],
            }
        ],
        "schedule": eventos
        or [evento_do_periodo(seed, inicio=inicio, fim=fim, status=status_do_periodo)],
        "stages": [] if etapas is None else etapas,
    }


def etapa_ligada(seed, *, evento=None, nome="Análise documental", ordem=1, avaliacoes=None):
    declaracao = {} if avaliacoes is None else {"evaluationsPerRegistration": avaliacoes}
    return {
        "id": identificador(ETAPA_C1, seed),
        "name": nome,
        "order": ordem,
        "eliminatory": True,
        "classificatory": False,
        "scheduleEventId": identificador(402, seed) if evento is None else evento,
        **declaracao,
    }


def publicar_no_processo(
    api_client,
    manager_headers,
    processo,
    *,
    draft,
    number="02",
    year=2026,
    title="Segundo Edital",
    chave="supervisao-segundo-edital",
):
    """Mais um Edital **no mesmo Processo**, publicado."""
    criado = api_client.post(
        f"/api/v1/admin/processos/{processo.id}/editais",
        {"number": number, "year": year, "title": title},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"{chave}-criar"},
    )
    assert criado.status_code == 201, criado.content
    edital = Edital.objects.get(pk=criado.json()["id"])
    return levar_a_publicacao(api_client, edital, draft=draft, chave=chave)


def submeter(edital, quantas, *, primeiro=1, quando=None, seed=0):
    """Inscrições **submetidas**, com o instante de submissão que a série lê.

    `quando` é o instante de submissão, e não o de criação: a série se constrói sobre ele e sobre
    mais nada (`FR-015`). Sem poder declará-lo, nenhum cenário de distribuição por dia seria
    montável.
    """
    agora = timezone.now()
    # O estado submetido é inalcançável sem versão aceita, aceite das declarações, protocolo e
    # instante — é `CheckConstraint`, e não disciplina de quem escreve (`T-007`). A fixture
    # atravessa a mesma porta: forjar o estado por fora faria a série se apoiar num registro que o
    # domínio não admite.
    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    criadas = []
    for numero in range(primeiro, primeiro + quantas):
        inscricao = Inscricao.objects.create(
            created_at=agora,
            identity_subject=f"cpf:candidato-{edital.number}-{numero:04d}",
            edital=edital,
            profile_id=perfil_de(seed),
            nome=f"Candidata {numero}",
            cpf="111.444.777-35",
            cpf_normalizado="11144477735",
            email=f"candidata{numero}@exemplo.br",
        )
        Inscricao.objects.filter(pk=inscricao.pk).update(
            status=Inscricao.Status.SUBMETIDA,
            protocolo=f"INS-{agora.year}-{edital.number}{numero:04d}",
            submitted_at=agora if quando is None else quando,
            versao_aceita=versao,
            declaracoes_aceitas_em=agora,
        )
        inscricao.refresh_from_db()
        criadas.append(inscricao)
    return criadas


def rascunhar(edital, quantos, *, primeiro=900, seed=0):
    """Inscrições em rascunho — a grandeza que **nunca** soma ao total (`FR-012`)."""
    agora = timezone.now()
    return [
        Inscricao.objects.create(
            created_at=agora,
            identity_subject=f"cpf:rascunho-{edital.number}-{numero:04d}",
            edital=edital,
            profile_id=perfil_de(seed),
        )
        for numero in range(primeiro, primeiro + quantos)
    ]
