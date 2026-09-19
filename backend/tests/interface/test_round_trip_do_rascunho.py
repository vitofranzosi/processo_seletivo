"""O rascunho atravessa o assistente sem perder o que a etapa atual não edita (E2E17-001).

`replace_draft` substitui o rascunho inteiro: o que não for reenviado é apagado. O assistente
reenvia, a cada gravação, as coleções que a etapa não edita — e é por isso que **cada campo
omitido do serializador de reenvio é um campo que morre na etapa seguinte**, em silêncio, sem
recusa e sem aviso.

A auditoria exploratória da 017 encontrou o caso concreto: quem marca o Evento do período de
inscrições e segue o assistente na ordem natural publica um Edital que anuncia prazo de inscrição
e não recebe nenhuma. A da 018 encontrou o mesmo defeito um nível abaixo, no marco: quem declara
"admite recurso em 5 dias" e segue o assistente publica um Edital que nada declara sobre recurso,
e todo recurso nasce sem prazo computável (E2E18-005). Estes testes cobrem a **classe** do defeito
e não só aquelas duas marcas: para cada coleção, o estado persistido é comparado campo a campo com
o que o contrato de entrada declara e o que `draft.py` reconstrói.

Dois caminhos, e os dois precisam valer:

- gravar uma etapa **posterior** não pode perder o que a anterior gravou — é o reenvio do estado
  persistido (`*_persistidos`);
- gravar de novo a etapa **dona da coleção** não pode perder o que aquela tela não oferece — é a
  leitura do formulário, que conhece só os campos que desenha.
"""

from datetime import UTC
from zoneinfo import ZoneInfo

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils.dateparse import parse_datetime

from processo_seletivo.editais.models.cronograma import EventoCronograma
from processo_seletivo.editais.models.perfis import (
    LinhaDoQuadroDeVagas,
    MarcoClassificatorio,
    PerfilVaga,
)
from processo_seletivo.processos.models import Edital
from tests.fixtures.edital import actor_headers
from tests.interface.conftest import identificar

ZONA = ZoneInfo(settings.TIME_ZONE)

PERFIL = "aaaaaaaa-0000-4000-8000-0000000017a1"
MODALIDADE = "aaaaaaaa-0000-4000-8000-0000000017a2"
INSCRICOES = "aaaaaaaa-0000-4000-8000-0000000017b1"
RESULTADO = "aaaaaaaa-0000-4000-8000-0000000017b2"
ETAPA = "aaaaaaaa-0000-4000-8000-0000000018c1"
MARCO = "aaaaaaaa-0000-4000-8000-0000000018c2"
CRITERIO = "aaaaaaaa-0000-4000-8000-0000000018c3"
PPI = "aaaaaaaa-0000-4000-8000-0000000025d1"
LINHA_GERAL = "aaaaaaaa-0000-4000-8000-0000000025d2"
LINHA_PPI = "aaaaaaaa-0000-4000-8000-0000000025d3"

# O Evento do período, como a instituição o descreve. Cada chave é um campo do contrato
# operacional que precisa atravessar o assistente inteiro.
EVENTO_DO_PERIODO = {
    "id": INSCRICOES,
    "type": "Inscrições",
    "description": "Período de inscrições",
    "startAt": "2026-10-01T09:00:00-03:00",
    "endAt": "2026-10-20T23:59:00-03:00",
    "order": 1,
    "status": "EM_ANDAMENTO",
    "isRegistrationPeriod": True,
}

EVENTO_DO_RESULTADO = {
    "id": RESULTADO,
    "type": "Resultado",
    "description": "Divulgação do resultado preliminar",
    "startAt": "2026-11-10T09:00:00-03:00",
    "endAt": None,
    "order": 2,
    "status": "PLANEJADO",
    "isRegistrationPeriod": False,
}

ETAPA_CLASSIFICATORIA = {
    "id": ETAPA,
    "name": "Prova prática",
    "order": 1,
    "weight": "1.0000",
    "eliminatory": True,
    "classificatory": True,
    "minimumScore": "60.0000",
    "maximumScore": "100.0000",
    "evaluationsPerRegistration": 1,
    "forma": "PONTUADA",
    "rotuloFavoravel": "",
    "rotuloDesfavoravel": "",
    "scheduleEventId": None,
}

# O marco, com **a janela recursal declarada**. É o campo que nenhuma etapa posterior edita e que
# o reenvio precisa carregar: sem ele, o Edital publica `appealWindow: null` (E2E18-005).
MARCO_COMPLETO = {
    "id": MARCO,
    "code": "FINAL",
    "name": "Classificação final",
    "stages": [ETAPA],
    "operation": "SOMA_PONDERADA",
    "normalization": "NENHUMA",
    "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
    "appealWindow": {"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"},
    # **E a regra de corte, pelo mesmo motivo.** É o terceiro campo que nenhuma etapa posterior
    # edita e que o reenvio precisa carregar: sem ele, declarar o corte no passo Classificação e
    # gravar qualquer passo seguinte publicaria um Edital que não corta, e a Etapa governada
    # voltaria a receber todos os habilitados sem que ninguém pedisse (014, FR-178).
    "cutRule": {
        "targetKind": "FIXED",
        "targetCount": 10,
        "surplusCount": 0,
        "tieOutcome": "STRICT",
        "governedStage": "NONE",
        "continuation": "NONE",
    },
    "tiebreakers": [
        {
            "id": CRITERIO,
            "order": 1,
            "type": "MAIOR_PONTUACAO_NA_ETAPA",
            "parameters": {"stageId": ETAPA},
            "whenMissing": "ULTIMO_NO_CRITERIO",
        }
    ],
}

PERFIL_COMPLETO = {
    "id": PERFIL,
    "code": "TEC-LAB",
    "name": "Técnico de Laboratório",
    "description": "Apoio técnico aos laboratórios.",
    "requirements": ["Curso técnico em Informática"],
    "immediateVacancies": 2,
    "reserveType": "LIMITED",
    "reserveLimit": 5,
    "locality": "Campus Vitória",
    "duties": "Manutenção dos laboratórios.",
    "workload": "40h semanais",
    "compensation": "R$ 4.500,00",
    # Os dois objetos normativos que o contrato declara, que `draft.py` reconstrói e que o
    # conteúdo publicado carrega — e que nenhuma tela do assistente oferece.
    "classificationInformation": {"criterio": "Maior pontuação na prova prática."},
    "callInformation": {"prazo": "Cinco dias úteis a contar da convocação."},
    "competitionModalities": [
        {"id": MODALIDADE, "code": "AC", "name": "Ampla concorrência"},
        {"id": PPI, "code": "PPI", "name": "Pretos, pardos e indígenas"},
    ],
    "classificationMilestones": [MARCO_COMPLETO],
    # O quadro de vagas da `025`. É a quinta coleção do Perfil a atravessar este teste, e a razão
    # é a mesma das quatro anteriores: `replace_draft` apaga e recria, e uma coleção que falte em
    # qualquer uma das quatro travessias some na gravação da etapa seguinte, sem recusa e sem
    # aviso — só que aqui o que some é uma quantidade de vagas publicável.
    #
    # Parcial de propósito: a Modalidade "Ampla concorrência" não carrega linha reservada (D-004),
    # e por isso este quadro nunca fica completo — a igualdade da FR-161 não roda, e o limite
    # superior da FR-177 roda e passa (1 + 1 = 2).
    "vacancyTable": [
        {"id": LINHA_GERAL, "modalityId": None, "immediateVacancies": 1},
        {"id": LINHA_PPI, "modalityId": PPI, "immediateVacancies": 1},
    ],
}


def _rascunho():
    return {
        "profiles": [PERFIL_COMPLETO],
        "schedule": [EVENTO_DO_PERIODO, EVENTO_DO_RESULTADO],
        # O marco enumera esta Etapa: sem ela no rascunho, o marco apontaria para o vazio.
        "stages": [ETAPA_CLASSIFICATORIA],
    }


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    """Um rascunho gravado pelo canal que aceita o contrato inteiro, para depois atravessá-lo."""
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    resposta = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        _rascunho(),
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="round-trip-0001"),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    assert resposta.status_code == 200, resposta.content
    edital.refresh_from_db()
    return edital


def _etapa(edital, nome):
    return reverse("interface:compor-etapa", args=[edital.id, nome])


def _instante(valor):
    """O instante, e não a grafia dele: o mesmo momento em UTC.

    O contrato admite qualquer deslocamento explícito e a persistência devolve UTC. Comparar
    texto faria o teste falhar por notação e passar por acaso — é o instante que precisa
    sobreviver ao round-trip, não o fuso em que alguém o escreveu.
    """
    if valor is None:
        return None
    momento = parse_datetime(valor) if isinstance(valor, str) else valor
    return momento.astimezone(UTC)


def _eventos_como_o_contrato_os_declara(edital):
    """O Cronograma persistido, no vocabulário do contrato de entrada.

    Comparar a coleção inteira — e não campo a campo escolhido a dedo — é o que faz este teste
    falhar quando um campo novo entrar no contrato e o serializador de reenvio esquecer dele.
    """
    return [
        {
            "id": str(evento.id),
            "type": evento.type,
            "description": evento.description,
            "startAt": _instante(evento.start_at),
            "endAt": _instante(evento.end_at),
            "order": evento.order,
            "status": evento.status,
            "isRegistrationPeriod": evento.is_registration_period,
        }
        for evento in EventoCronograma.objects.filter(cronograma__edital=edital).order_by("order")
    ]


def _marcos_como_o_contrato_os_declara(edital):
    """Os marcos persistidos, no vocabulário do contrato de entrada.

    A coleção inteira, pela mesma razão do Cronograma: comparar campo a campo escolhido a dedo
    passaria a valer só para o campo que se lembrou de escolher, e o defeito desta classe é
    justamente o campo de que ninguém se lembrou.
    """
    return [
        {
            "id": str(marco.id),
            "code": marco.code,
            "name": marco.name,
            "stages": [str(etapa) for etapa in marco.etapas],
            "operation": marco.operacao,
            "normalization": marco.normalizacao,
            "rounding": marco.arredondamento,
            "appealWindow": marco.janela_recursal or None,
            "cutRule": marco.regra_de_corte or None,
            "tiebreakers": [
                {
                    "id": str(criterio.id),
                    "order": criterio.ordem,
                    "type": criterio.tipo,
                    "parameters": criterio.parametros,
                    "whenMissing": criterio.quando_ausente,
                }
                for criterio in marco.criterios.order_by("ordem")
            ],
        }
        for marco in MarcoClassificatorio.objects.filter(perfil__edital=edital).order_by("code")
    ]


def _quadro_como_o_contrato_o_declara(edital):
    """O quadro persistido, no vocabulário do contrato de entrada — a coleção **inteira**.

    Campo a campo escolhido a dedo passaria a valer só para o campo que se lembrou de escolher, e
    o defeito desta classe é justamente o campo de que ninguém se lembrou (025, R-009).
    """
    return [
        {
            "id": str(linha.id),
            "modalityId": str(linha.modalidade_id) if linha.modalidade_id else None,
            "immediateVacancies": linha.vagas_imediatas,
        }
        for linha in LinhaDoQuadroDeVagas.objects.filter(perfil__edital=edital).order_by(
            "ordem", "id"
        )
    ]


def _esperado():
    """O mesmo Cronograma que entrou — todos os campos, e não só a marca."""
    return [
        {
            **evento,
            "startAt": _instante(evento["startAt"]),
            "endAt": _instante(evento["endAt"]),
        }
        for evento in (EVENTO_DO_PERIODO, EVENTO_DO_RESULTADO)
    ]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_gravar_a_etapa_seguinte_preserva_o_cronograma_inteiro(client, seletor_ligado, edital):
    """A jornada real: marcar o período, seguir o assistente, e o período continuar marcado.

    `inscricao` é seguida de `conteudo` na ordem do assistente, e é obrigatório atravessá-la para
    chegar à Revisão. Era ali que a marca morria.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(
        _etapa(edital, "inscricao"),
        {"periodo-inscricoes": INSCRICOES},
    )
    assert resposta.status_code == 302, resposta.content

    edital.refresh_from_db()
    resposta = client.post(_etapa(edital, "conteudo"), {"secao-recursos": "Três dias úteis."})
    assert resposta.status_code == 302, resposta.content

    assert _eventos_como_o_contrato_os_declara(edital) == _esperado()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_regravar_o_cronograma_preserva_o_que_a_tela_nao_oferece(client, seletor_ligado, edital):
    """Corrigir uma data depois de designar o período não pode desdesignar o período.

    A tela do Cronograma não oferece a marca — ela é decisão da etapa `Inscrição` — nem o estado
    do Evento. O que a tela não oferece, ela não pode apagar.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(_etapa(edital, "inscricao"), {"periodo-inscricoes": INSCRICOES})
    assert resposta.status_code == 302, resposta.content

    edital.refresh_from_db()
    resposta = client.post(
        _etapa(edital, "cronograma"),
        {
            "evento-0-id": INSCRICOES,
            "evento-0-type": "Inscrições",
            "evento-0-description": "Período de inscrições",
            "evento-0-startAt": "2026-10-01T09:00",
            # A correção: o término passa para o dia 21.
            "evento-0-endAt": "2026-10-21T23:59",
            "evento-0-order": "1",
            "evento-1-id": RESULTADO,
            "evento-1-type": "Resultado",
            "evento-1-description": "Divulgação do resultado preliminar",
            "evento-1-startAt": "2026-11-10T09:00",
            "evento-1-endAt": "",
            "evento-1-order": "2",
        },
    )
    assert resposta.status_code == 302, resposta.content

    periodo = EventoCronograma.objects.get(pk=INSCRICOES)
    assert periodo.end_at.astimezone(ZONA).day == 21, "a correção que a tela oferece vale"
    assert periodo.is_registration_period is True, "a marca que a tela não oferece sobrevive"
    assert periodo.status == "EM_ANDAMENTO", "o estado que a tela não oferece sobrevive"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_gravar_outra_etapa_preserva_o_conteudo_normativo_do_perfil(client, seletor_ligado, edital):
    """Os dois objetos normativos do Perfil que nenhuma tela desenha, e que o contrato declara."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(_etapa(edital, "conteudo"), {"secao-recursos": "Três dias úteis."})
    assert resposta.status_code == 302, resposta.content

    perfil = PerfilVaga.objects.get(edital=edital)
    assert perfil.classification_information == PERFIL_COMPLETO["classificationInformation"]
    assert perfil.call_information == PERFIL_COMPLETO["callInformation"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_gravar_a_etapa_seguinte_preserva_o_marco_inteiro(client, seletor_ligado, edital):
    """A jornada real da 018: declarar o prazo recursal e seguir o assistente.

    `classificacao` é seguida de `inscricao` e de `conteudo` na ordem do assistente, e as duas são
    obrigatórias para chegar à Revisão. Era ali que a janela morria, e com ela o prazo que o
    documento publicado promete (E2E18-005).
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(_etapa(edital, "inscricao"), {"periodo-inscricoes": INSCRICOES})
    assert resposta.status_code == 302, resposta.content

    edital.refresh_from_db()
    resposta = client.post(_etapa(edital, "conteudo"), {"secao-recursos": "Cinco dias corridos."})
    assert resposta.status_code == 302, resposta.content

    assert _marcos_como_o_contrato_os_declara(edital) == [MARCO_COMPLETO]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_regravar_a_classificacao_preserva_a_janela_declarada(client, seletor_ligado, edital):
    """Reeditar o marco na tela que o desenha não pode apagar a declaração que ela mesma oferece.

    O caminho é o do formulário, e não o do reenvio: aqui quem lê é `ler_classificacao`, que
    conhece os campos desenhados. A janela é um deles, e precisa sobreviver à própria tela.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    perfil = PerfilVaga.objects.get(edital=edital)
    base = f"marco-{perfil.id}-0"

    resposta = client.post(
        _etapa(edital, "classificacao"),
        {
            "perfil_id": str(perfil.id),
            f"{base}-id": MARCO,
            f"{base}-code": "FINAL",
            # A correção que a tela oferece: a denominação muda.
            f"{base}-name": "Classificação final do certame",
            f"{base}-stages": ETAPA,
            f"{base}-operation": "SOMA_PONDERADA",
            f"{base}-normalization": "NENHUMA",
            f"{base}-scale": "2",
            f"{base}-mode": "MEIO_PARA_CIMA",
            f"{base}-appealDeclaration": "admite",
            # E a regra de corte, pelo mesmo motivo da janela: ela é um dos campos que **esta** tela
            # desenha, e o navegador os devolve preenchidos. Omiti-los aqui simularia um navegador
            # que não envia o que a tela mostra — e o que o teste protege é o contrário disso: que a
            # declaração sobreviva à própria tela que a oferece (014, FR-178).
            f"{base}-cutTargetKind": "FIXED",
            f"{base}-cutTargetCount": "10",
            f"{base}-cutSurplusCount": "0",
            f"{base}-cutTieOutcome": "STRICT",
            f"{base}-cutGovernedStage": "NONE",
            f"{base}-cutContinuation": "NONE",
            f"{base}-appealDurationDays": "5",
            f"{base}-appealUnit": "DIAS_CORRIDOS",
            f"criterio-{perfil.id}-0-0-id": CRITERIO,
            f"criterio-{perfil.id}-0-0-order": "1",
            f"criterio-{perfil.id}-0-0-type": "MAIOR_PONTUACAO_NA_ETAPA",
            f"criterio-{perfil.id}-0-0-target": ETAPA,
            f"criterio-{perfil.id}-0-0-whenMissing": "ULTIMO_NO_CRITERIO",
        },
    )
    assert resposta.status_code == 302, resposta.content

    marco = MarcoClassificatorio.objects.get(pk=MARCO)
    assert marco.name == "Classificação final do certame", "a correção que a tela oferece vale"
    assert marco.janela_recursal == MARCO_COMPLETO["appealWindow"], "a janela declarada sobrevive"
    assert marco.regra_de_corte == MARCO_COMPLETO["cutRule"], "a regra de corte declarada sobrevive"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_gravar_outra_etapa_preserva_o_quadro_de_vagas_inteiro(client, seletor_ligado, edital):
    """A travessia 2 de 4 da `025`: o reenvio do estado persistido carrega o quadro.

    Sem ela, quem declara `AC 1` e `PPI 1` no passo dos Perfis e segue o assistente publica um
    Edital que não declara quadro nenhum — e o número que separa o certame de existir como
    documento some numa visita ao Cronograma.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(_etapa(edital, "inscricao"), {"periodo-inscricoes": INSCRICOES})
    assert resposta.status_code == 302, resposta.content

    edital.refresh_from_db()
    resposta = client.post(_etapa(edital, "conteudo"), {"secao-recursos": "Três dias úteis."})
    assert resposta.status_code == 302, resposta.content

    assert _quadro_como_o_contrato_o_declara(edital) == PERFIL_COMPLETO["vacancyTable"]


def _perfil_como_a_tela_o_envia():
    """O POST do passo dos Perfis, com tudo o que aquela tela desenha — e só isso.

    Compartilhado pelos dois testes da travessia porque o defeito mora justamente no que **falta**
    aqui: um payload copiado e ajustado num teste só deixaria o outro provando outra coisa.
    """
    return {
        "perfil-0-id": PERFIL,
        "perfil-0-code": "TEC-LAB",
        # A correção que a tela oferece: a denominação muda.
        "perfil-0-name": "Técnico de Laboratório (Vitória)",
        "perfil-0-description": PERFIL_COMPLETO["description"],
        "perfil-0-requirements": PERFIL_COMPLETO["requirements"][0],
        "perfil-0-immediateVacancies": "2",
        "perfil-0-reserveType": "LIMITED",
        "perfil-0-reserveLimit": "5",
        "perfil-0-locality": PERFIL_COMPLETO["locality"],
        "perfil-0-duties": PERFIL_COMPLETO["duties"],
        "perfil-0-workload": PERFIL_COMPLETO["workload"],
        "perfil-0-compensation": PERFIL_COMPLETO["compensation"],
        "modalidade-0-0-id": MODALIDADE,
        "modalidade-0-0-code": "AC",
        "modalidade-0-0-name": "Ampla concorrência",
        "modalidade-0-1-id": PPI,
        "modalidade-0-1-code": "PPI",
        "modalidade-0-1-name": "Pretos, pardos e indígenas",
        # A seção do quadro, como a tela a desenha: a geral primeiro, e uma por Modalidade.
        # A da "Ampla concorrência" vai **em branco**, que é o que a D-004 manda — e em branco
        # não grava linha, e não vira zero.
        "linha-0-0-id": LINHA_GERAL,
        "linha-0-0-modalityId": "",
        "linha-0-0-immediateVacancies": "1",
        "linha-0-1-id": "aaaaaaaa-0000-4000-8000-0000000025d9",
        "linha-0-1-modalityId": MODALIDADE,
        "linha-0-1-immediateVacancies": "",
        "linha-0-2-id": LINHA_PPI,
        "linha-0-2-modalityId": PPI,
        "linha-0-2-immediateVacancies": "1",
    }


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_regravar_os_perfis_pela_tela_preserva_o_quadro(client, seletor_ligado, edital):
    """As travessias 1 e 3 da `025`: a tela lê o quadro que ela mesma desenha.

    O caminho é o do formulário, e não o do reenvio: quem lê é `ler_perfis`, que conhece só os
    campos desenhados. Se a seção do quadro não fosse lida, corrigir a denominação de um Perfil
    apagaria as quantidades — na própria tela que as mostra.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(_etapa(edital, "perfis"), _perfil_como_a_tela_o_envia())
    assert resposta.status_code == 302, resposta.content

    perfil = PerfilVaga.objects.get(pk=PERFIL)
    assert perfil.name == "Técnico de Laboratório (Vitória)", "a correção que a tela oferece vale"
    assert _quadro_como_o_contrato_o_declara(edital) == PERFIL_COMPLETO["vacancyTable"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_regravar_os_perfis_pela_tela_preserva_os_marcos(client, seletor_ligado, edital):
    """A travessia que o percurso E2E da 014 encontrou aberta (E2E14-001).

    Quem desenha o marco é a etapa `classificacao`; a dos Perfis não o oferece, e `ler_perfis`
    devolvia `classificationMilestones: []`. Como `replace_draft` apaga e recria, voltar aos
    Perfis para declarar qual Modalidade é a ampla concorrência — exatamente o que a regra de corte
    derivada do quadro exige — apagava o marco inteiro, sem recusa e sem aviso.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(_etapa(edital, "perfis"), _perfil_como_a_tela_o_envia())
    assert resposta.status_code == 302, resposta.content

    assert _marcos_como_o_contrato_os_declara(edital) == [MARCO_COMPLETO]


# ---------------------------------------------------------------------------------------------
# A revelação progressiva do marco (030, FR-418)
# ---------------------------------------------------------------------------------------------
#
# **A mesma classe de defeito, pela porta nova.** Os oito testes acima guardam o que o assistente
# perde ao **reenviar** o rascunho; estes três guardam o que ele perde ao **esconder** um campo.
# A causa é a mesma — `replace_draft` apaga e recria, e campo que não volta no envio é campo
# perdido em silêncio —, e por isso eles moram aqui e não num arquivo à parte.
#
# Esconder por CSS mantém o campo no formulário e o `required` ativo, que é o defeito que
# `_marco.html` já documenta; `disabled` tira o campo do envio, que é a perda outra vez. Sobra uma
# saída, e é a que o contrato do rascunho fixa: o campo impertinente sai da tela e do alcance do
# teclado como `<input type="hidden">` com o último valor declarado.
#
# O irmão deste bloco é `tests/unit/editais/test_forma_da_ordem.py`, que prende o outro lado: o
# que o rascunho guarda **não** alcança o conteúdo publicado. Os dois caminhos existem, e fechar
# só um deixa o defeito vivo.

import re  # noqa: E402

from tests.interface.test_compor import PERFIL as PERFIL_DO_ASSISTENTE  # noqa: E402

ETAPA_DA_030 = "aaaaaaaa-0000-4000-8000-00000000e021"
MARCO_DA_030 = "aaaaaaaa-0000-4000-8000-00000000e051"
CRITERIO_DA_030 = "aaaaaaaa-0000-4000-8000-00000000e061"

ALGORITMO = "IFES-SORTEIO-SHA256-v1"
FONTE = "Fonte de demonstração"


def _marco_de_sorteio(**alteracoes):
    """O marco de sorteio inteiro, como a tela o envia."""
    base = {
        "perfil_id": PERFIL_DO_ASSISTENTE,
        f"marco-{PERFIL_DO_ASSISTENTE}-0-id": MARCO_DA_030,
        f"marco-{PERFIL_DO_ASSISTENTE}-0-code": "FINAL",
        f"marco-{PERFIL_DO_ASSISTENTE}-0-name": "Classificação final",
        f"marco-{PERFIL_DO_ASSISTENTE}-0-orderProduction": "POR_SORTEIO",
        f"marco-{PERFIL_DO_ASSISTENTE}-0-stages": ETAPA_DA_030,
        f"marco-{PERFIL_DO_ASSISTENTE}-0-operation": "SOMA_PONDERADA",
        f"marco-{PERFIL_DO_ASSISTENTE}-0-normalization": "NENHUMA",
        f"marco-{PERFIL_DO_ASSISTENTE}-0-scale": "2",
        f"marco-{PERFIL_DO_ASSISTENTE}-0-mode": "MEIO_PARA_CIMA",
        f"marco-{PERFIL_DO_ASSISTENTE}-0-draw-algorithm": ALGORITMO,
        f"marco-{PERFIL_DO_ASSISTENTE}-0-draw-source": FONTE,
        f"marco-{PERFIL_DO_ASSISTENTE}-0-draw-occurrence": "5901",
        f"marco-{PERFIL_DO_ASSISTENTE}-0-draw-occurrenceAt": "2020-01-01T20:00:00-03:00",
        f"marco-{PERFIL_DO_ASSISTENTE}-0-draw-derivation": "A extração de sábado anterior.",
        f"marco-{PERFIL_DO_ASSISTENTE}-0-draw-normalizationRule": "DIGITOS_EM_SEQUENCIA",
        f"marco-{PERFIL_DO_ASSISTENTE}-0-draw-normalizationText": "Os cinco números.",
        f"marco-{PERFIL_DO_ASSISTENTE}-0-draw-substitutionRule": (
            "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE"
        ),
        f"marco-{PERFIL_DO_ASSISTENTE}-0-draw-substitutionText": "Vale a seguinte.",
        f"criterio-{PERFIL_DO_ASSISTENTE}-0-0-id": CRITERIO_DA_030,
        f"criterio-{PERFIL_DO_ASSISTENTE}-0-0-order": "1",
        f"criterio-{PERFIL_DO_ASSISTENTE}-0-0-type": "MAIOR_PONTUACAO_NA_ETAPA",
        f"criterio-{PERFIL_DO_ASSISTENTE}-0-0-target": ETAPA_DA_030,
        f"criterio-{PERFIL_DO_ASSISTENTE}-0-0-whenMissing": "ULTIMO_NO_CRITERIO",
    }
    return {**base, **alteracoes}


def _compor_a_classificacao(client, edital, **alteracoes):
    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital.id, "classificacao"]),
        _marco_de_sorteio(**alteracoes),
    )
    assert resposta.status_code == 302, resposta.content
    return resposta


def _tela_da_classificacao(client, edital):
    return client.get(
        reverse("interface:compor-etapa", args=[edital.id, "classificacao"])
    ).content.decode()


def _campo(corpo, nome):
    """O controle de nome exato, inteiro, como a página o escreve.

    **`<input>` ou `<select>`**, desde a `035` (FR-507): o algoritmo e a fonte deixaram de ser
    digitados na composição, e continuam `<input type="hidden">` quando o marco não sorteia — que é
    justamente a travessia que este arquivo guarda.

    Ler só o `<input>` faria o caso "reaparece quando a forma volta a ser sorteio" devolver string
    vazia e falhar por motivo que não é o dele; e, pior, faria uma asserção de ausência passar a não
    guardar nada, em silêncio.
    """
    achado = re.search(rf'<input[^>]*name="{re.escape(nome)}"[^>]*>', corpo)
    if achado:
        return achado.group(0)
    escolha = re.search(rf'<select[^>]*name="{re.escape(nome)}"[^>]*>.*?</select>', corpo, re.S)
    return escolha.group(0) if escolha else ""


@pytest.mark.django_db
@pytest.mark.integration
def test_o_metodo_declarado_some_da_tela_e_continua_no_envio(client, com_etapas):
    """O percurso inteiro de FR-418: declarar, tornar impertinente, e continuar declarado."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    _compor_a_classificacao(client, com_etapas)

    _compor_a_classificacao(
        client, com_etapas, **{f"marco-{PERFIL_DO_ASSISTENTE}-0-orderProduction": "POR_PONTUACAO"}
    )

    guardado = MarcoClassificatorio.objects.get(pk=MARCO_DA_030)
    assert guardado.forma_da_ordem == "POR_PONTUACAO"
    assert guardado.metodo_de_sorteio.get("algorithm") == ALGORITMO, (
        "o rascunho guarda o que a tela escondeu — trocar a resposta não descarta declaração"
    )

    corpo = _tela_da_classificacao(client, com_etapas)
    oculto = _campo(corpo, f"marco-{PERFIL_DO_ASSISTENTE}-0-draw-algorithm")

    assert 'type="hidden"' in oculto, "o campo impertinente sai da tela, e não do envio"
    assert ALGORITMO in oculto
    assert "disabled" not in oculto, (
        "campo `disabled` não é submetido pelo navegador: seria a perda que este contrato impede"
    )


@pytest.mark.django_db
@pytest.mark.integration
def test_o_metodo_guardado_reaparece_quando_a_forma_volta_a_ser_sorteio(client, com_etapas):
    """A outra metade: escondido não é apagado, e voltar atrás devolve o que estava lá."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    _compor_a_classificacao(client, com_etapas)
    _compor_a_classificacao(
        client, com_etapas, **{f"marco-{PERFIL_DO_ASSISTENTE}-0-orderProduction": "POR_PONTUACAO"}
    )

    _compor_a_classificacao(
        client, com_etapas, **{f"marco-{PERFIL_DO_ASSISTENTE}-0-orderProduction": "POR_SORTEIO"}
    )

    corpo = _tela_da_classificacao(client, com_etapas)
    visivel = _campo(corpo, f"marco-{PERFIL_DO_ASSISTENTE}-0-draw-algorithm")

    assert 'type="hidden"' not in visivel
    assert ALGORITMO in visivel
    assert MarcoClassificatorio.objects.get(pk=MARCO_DA_030).metodo_de_sorteio["source"] == FONTE


@pytest.mark.django_db
@pytest.mark.integration
def test_gravar_outra_etapa_nao_apaga_a_forma_da_ordem(client, com_etapas):
    """A nona travessia, e ela é da mesma família das oito acima.

    Sem a forma da ordem no marco persistido, declará-la aqui e visitar o Cronograma a apagaria —
    e o marco voltaria a ser lido por inferência, sem que nada acusasse.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    _compor_a_classificacao(client, com_etapas)

    from tests.interface.test_compor import eventos

    resposta = client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "cronograma"]), eventos()
    )
    assert resposta.status_code == 302, resposta.content

    assert MarcoClassificatorio.objects.get(pk=MARCO_DA_030).forma_da_ordem == "POR_SORTEIO"


# --- A gravação do rascunho continua aceitando o Edital pela metade (032, FR-459) --------------
#
# **O décimo caso, e ele não é sobre travessia.** Os nove acima prendem o que o reenvio não pode
# perder; este prende o que a gravação não pode passar a recusar. Mora aqui porque é o mesmo
# contrato — o que `replace_draft` aceita — visto do outro lado.
#
# A `032` acrescenta quatro achados de executabilidade, dois deles impeditivos. A primeira linha de
# cada um é o recorte por ato, e este teste é a contraprova dele: a `030` tentou recusar na
# gravação e **derrubou 759 testes**, porque tornava ilegal todo payload que este repositório
# produz. O rascunho pode estar pela metade; o Edital publicado não.
#
# Constantes próprias, e não as do topo: o que se grava aqui é o oposto do `PERFIL_COMPLETO`, e
# reusá-lo obrigaria a desmontá-lo campo a campo.

PERFIL_SEM_MARCO = "aaaaaaaa-0000-4000-8000-0000000032a1"
PERFIL_DOS_MARCOS = "aaaaaaaa-0000-4000-8000-0000000032a2"
MARCO_SEM_CORTE = "aaaaaaaa-0000-4000-8000-0000000032b1"
MARCO_SEM_METODO = "aaaaaaaa-0000-4000-8000-0000000032b2"


def _rascunho_inexecutavel():
    """As três ausências que a `032` passa a recusar **na publicação**, num rascunho só.

    Um Perfil sem marco algum (`FR-457`), um marco sem regra de corte (`FR-461`) e um marco que
    ordena por sorteio sem método declarado (`FR-467`) — e nenhum método comum na raiz, para que a
    terceira ausência seja mesmo ausência.
    """
    return {
        "profiles": [
            {
                "id": PERFIL_SEM_MARCO,
                "code": "SEM-MARCO",
                "name": "Perfil que ainda não classifica",
                "immediateVacancies": 1,
                "reserveType": "NONE",
                "reserveLimit": None,
                "competitionModalities": [],
                "classificationMilestones": [],
            },
            {
                "id": PERFIL_DOS_MARCOS,
                "code": "COM-MARCO",
                "name": "Perfil em composição",
                "immediateVacancies": 1,
                "reserveType": "NONE",
                "reserveLimit": None,
                "competitionModalities": [],
                "classificationMilestones": [
                    {
                        "id": MARCO_SEM_CORTE,
                        "code": "SEM-CORTE",
                        "name": "Classificação sem corte declarado",
                        "orderProduction": "POR_PONTUACAO",
                        "stages": [ETAPA],
                        "operation": "SOMA_PONDERADA",
                        "normalization": "NENHUMA",
                        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
                        "tiebreakers": [],
                    },
                    {
                        "id": MARCO_SEM_METODO,
                        "code": "SEM-METODO",
                        "name": "Sorteio ainda sem método",
                        # Sorteia, e ainda não declarou o método — que é exatamente o estado de
                        # quem acabou de acrescentar o marco (030, FR-414).
                        "orderProduction": "POR_SORTEIO",
                        "stages": [],
                        "operation": "SOMA_PONDERADA",
                        "normalization": "NENHUMA",
                        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
                        "tiebreakers": [],
                    },
                ],
            },
        ],
        "schedule": [EVENTO_DO_PERIODO],
        "stages": [ETAPA_CLASSIFICATORIA],
    }


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_gravar_rascunho_inexecutavel_continua_sendo_aceito(
    api_client, manager_headers, process_payload
):
    """`FR-459` e `SC-160`: nenhuma verificação nova alcança a gravação.

    O Edital que a `032` vai recusar na publicação continua **gravável** — e o que se afirma aqui
    é o estado persistido, e não só o código de resposta: uma recusa parcial que gravasse metade
    devolveria 200 e perderia o resto.
    """
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])

    resposta = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        _rascunho_inexecutavel(),
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="round-trip-032-0001"),
            "HTTP_IF_MATCH": '"1"',
        },
    )

    assert resposta.status_code == 200, resposta.content
    assert PerfilVaga.objects.filter(pk=PERFIL_SEM_MARCO).exists(), "o Perfil sem marco foi gravado"
    assert not MarcoClassificatorio.objects.filter(perfil_id=PERFIL_SEM_MARCO).exists()
    sem_corte = MarcoClassificatorio.objects.get(pk=MARCO_SEM_CORTE)
    sem_metodo = MarcoClassificatorio.objects.get(pk=MARCO_SEM_METODO)
    assert not sem_corte.regra_de_corte, "o corte em branco atravessa a gravação"
    assert not sem_metodo.metodo_de_sorteio, "e o sorteio sem método também"
    assert sem_metodo.forma_da_ordem == "POR_SORTEIO"
