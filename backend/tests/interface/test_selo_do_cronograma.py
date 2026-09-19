"""O selo da etapa Cronograma passa a considerar validade (028, US1).

**O achado que este arquivo prende.** O selo era derivado de `eventos.exists()` — existe Evento,
logo concluída. Um Edital criado a partir de outro nascia, portanto, com as nove etapas verdes
carregando o cronograma inteiro da oferta anterior: na auditoria de 13/09/2026, o Edital 12/2027
tinha todas as etapas CONCLUÍDA e um período de inscrição de 13/09/2026 08:00 a 09:00 — uma janela
de uma hora, do ano anterior, já encerrada.
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.editais.models import EventoCronograma
from processo_seletivo.processos.models import Edital
from tests.fixtures.edital import actor_headers
from tests.fixtures.selecao import rascunho_de_selecao
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db


@pytest.fixture
def composto(api_client, manager_headers, process_payload):
    """Um Edital em elaboração com Cronograma, para o selo ter o que julgar."""
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho_de_selecao(),
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="selo-cronograma-0001"),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    edital.refresh_from_db()
    return edital


def datar(edital, *, inicio, fim=None):
    EventoCronograma.objects.filter(cronograma__edital=edital).update(start_at=inicio, end_at=fim)


def progresso(client, edital, etapa="cronograma"):
    resposta = client.get(reverse("interface:compor-etapa", args=[edital.id, etapa]))
    assert resposta.status_code == 200, resposta.content
    passos = {passo["chave"]: passo for passo in resposta.context["progresso"]}
    return passos, resposta


# --- T012 · o selo (FR-359, FR-360, FR-361, FR-362) ---------------------------------------------


def test_cronograma_com_evento_no_passado_fica_pendente(client, seletor_ligado, composto):
    identificar(client, "ana.elaboradora", ["elaborador"])
    agora = timezone.now()
    datar(composto, inicio=agora - timedelta(days=9), fim=agora - timedelta(days=1))

    passos, _ = progresso(client, composto, etapa="identificacao")

    assert passos["cronograma"]["estado"] == "pendente"


def test_cronograma_inteiro_no_futuro_continua_concluido(client, seletor_ligado, composto):
    """O critério não ficou mais severo para quem está certo: existir Evento válido basta."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    agora = timezone.now()
    datar(composto, inicio=agora + timedelta(days=1), fim=agora + timedelta(days=9))

    passos, _ = progresso(client, composto, etapa="identificacao")

    assert passos["cronograma"]["estado"] == "concluida"


def test_corrigir_as_datas_devolve_o_selo_sem_gravacao_nenhuma(client, seletor_ligado, composto):
    """O estado é derivado e não persistido — é a mesma razão de ele estar certo na primeira
    abertura depois do reaproveitamento, sem que ninguém tenha gravado coisa alguma (FR-360)."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    agora = timezone.now()
    datar(composto, inicio=agora - timedelta(days=9), fim=agora - timedelta(days=1))
    assert progresso(client, composto, etapa="identificacao")[0]["cronograma"]["estado"] == (
        "pendente"
    )

    datar(composto, inicio=agora + timedelta(days=1), fim=agora + timedelta(days=9))

    passos, _ = progresso(client, composto, etapa="identificacao")
    assert passos["cronograma"]["estado"] == "concluida"


def test_os_outros_oito_selos_nao_mudam_de_criterio(client, seletor_ligado, composto):
    """**A generalização acidental é o risco desta mudança.** Cada etapa tem uma noção própria de
    "válida", e decidi-las em bloco produz regra que ninguém revisou. Só o Cronograma muda."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    agora = timezone.now()

    datar(composto, inicio=agora + timedelta(days=1), fim=agora + timedelta(days=9))
    antes, _ = progresso(client, composto, etapa="identificacao")

    datar(composto, inicio=agora - timedelta(days=9), fim=agora - timedelta(days=1))
    depois, _ = progresso(client, composto, etapa="identificacao")

    mudaram = {chave for chave in antes if antes[chave]["estado"] != depois[chave]["estado"]}
    assert mudaram == {"cronograma"}


def test_pendente_nao_impede_avancar_entre_etapas_nem_submeter(client, seletor_ligado, composto):
    """FR-362. Pendente **orienta** quem retoma o trabalho; ele não fecha porta.

    Quem fecha porta é o achado impeditivo do período encerrado, e ele é um só — aqui o período
    está aberto, então nada deve impedir.

    **O arranjo mudou com a `037`, e o que o caso afirma não.** Ele produzia o selo pendente com
    um período de início vencido e término futuro — o que a régua antiga chamava de vencido e a
    nova, corretamente, não chama mais (`FR-545`). Um segundo Evento, **pontual e já ocorrido**,
    é o que hoje mantém o selo pendente com o prazo de inscrições aberto: as duas condições que
    este caso precisa ter ao mesmo tempo deixaram de caber num Evento só.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    agora = timezone.now()
    # O período de inscrições **em curso**: aberto, e por isso nada impede.
    datar(composto, inicio=agora - timedelta(days=1), fim=agora + timedelta(days=9))
    EventoCronograma.objects.filter(cronograma__edital=composto).update(is_registration_period=True)
    periodo = EventoCronograma.objects.get(cronograma__edital=composto)
    # E o Evento que mantém o selo pendente: sem término declarado, e o instante dele já passou —
    # ausência de término não é fim no futuro (`FR-546`).
    EventoCronograma.objects.create(
        cronograma=periodo.cronograma,
        type="Divulgação",
        description="Divulgação do resultado preliminar",
        start_at=agora - timedelta(days=9),
        end_at=None,
        order=2,
    )

    passos, resposta = progresso(client, composto)

    assert passos["cronograma"]["estado"] == "pendente"
    # A etapa seguinte continua alcançável: a navegação do assistente não é travada pelo selo.
    seguinte = client.get(reverse("interface:compor-etapa", args=[composto.id, "etapas"]))
    assert seguinte.status_code == 200
    # E a Revisão não exibe impedimento nenhum — só as advertências.
    revisao = client.get(reverse("interface:compor-etapa", args=[composto.id, "revisao"]))
    impeditivas = [p for p in revisao.context["pendencias"] if p["severidade"] == "erro"]
    assert impeditivas == [], impeditivas
    assert resposta.context["pendencias_aqui"], "a etapa precisa dizer por que está pendente"


# --- T013 · o Edital reaproveitado, na primeira abertura ----------------------------------------


@pytest.fixture
def origem(api_client, manager_headers, process_payload):
    """Um Edital publicado cujo cronograma já venceu — a oferta anterior de que se parte.

    Publicado com o prazo aberto e encerrado por Retificação, porque é como acontece na vida e
    porque a `028` recusa publicar Edital cujas inscrições já fecharam (FR-346, FR-355).
    """
    from tests.fixtures.publicacao import encerrar_inscricoes, publish_original

    agora = timezone.now()
    rascunho = rascunho_de_selecao()
    rascunho["schedule"][0]["startAt"] = (agora - timedelta(days=60)).isoformat()
    rascunho["schedule"][0]["endAt"] = (agora + timedelta(days=1)).isoformat()
    rascunho["schedule"][0]["isRegistrationPeriod"] = True
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    return encerrar_inscricoes(api_client, edital, agora - timedelta(days=30), suffix="selo-origem")


def test_o_edital_reaproveitado_nasce_com_o_cronograma_pendente(
    client, seletor_ligado, api_client, manager_headers, process_payload, origem
):
    """**O cenário do 12/2027, na primeira abertura e sem gravação nenhuma.**

    Quatro coisas são exigidas de uma vez porque é assim que a pessoa as encontra: o selo pendente,
    a etapa dizendo por quê, o aviso permanente da `023` ainda no lugar, e — a que importa mais —
    nenhuma data diferente da que a origem publicou.
    """
    from processo_seletivo.editais.application.reaproveitamento import reaproveitar_edital
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
    from tests.conftest import ator_institucional

    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            **process_payload,
            "institutionalCode": "PS-SELO-028",
            "firstEdital": {**process_payload["firstEdital"], "number": "12", "year": 2027},
        },
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "selo-cronograma-destino-0001"},
    )
    assert criado.status_code == 201, criado.content
    destino = Edital.objects.get(processo_id=criado.json()["id"])

    reaproveitar_edital(
        actor=ator_institucional("ana.elaboradora", "edital:elaborar"),
        edital_id=destino.id,
        origem_id=origem.id,
        expected_revision=destino.revision,
        idempotency_key="selo-cronograma-reaproveitar-0001",
        correlation_id="selo",
    )
    destino.refresh_from_db()

    identificar(client, "ana.elaboradora", ["elaborador"])
    passos, resposta = progresso(client, destino)

    assert passos["cronograma"]["estado"] == "pendente", "o cronograma copiado veio do ano passado"
    assert resposta.context["pendencias_aqui"], "a etapa tem de dizer quais Eventos já passaram"
    assert resposta.context["origem_reaproveitada"], "o aviso permanente da 023 continua no lugar"

    publicada = VersaoConsolidada.objects.filter(edital=origem).latest("materialized_at").content
    copiados = {
        (evento.start_at, evento.end_at)
        for evento in EventoCronograma.objects.filter(cronograma__edital=destino)
    }
    for evento in publicada["schedule"]:
        from django.utils.dateparse import parse_datetime

        par = (parse_datetime(evento["startAt"]), parse_datetime(evento["endAt"] or "") or None)
        assert par in copiados, f"a data de '{evento['description']}' mudou na cópia"


# --- T025 · a Revisão, e o Edital composto do zero (UX-050, FR-363) -----------------------------


def test_a_revisao_nao_diz_que_nada_esta_pendente_com_cronograma_vencido(
    client, seletor_ligado, composto
):
    """UX-050. A frase que a auditoria leu no Edital 12/2027 era "Nada pendente — o Edital pode ser
    submetido", com o cronograma do ano anterior logo acima."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    agora = timezone.now()
    datar(composto, inicio=agora - timedelta(days=9), fim=agora - timedelta(days=1))

    corpo = client.get(
        reverse("interface:compor-etapa", args=[composto.id, "revisao"])
    ).content.decode()

    assert "Nada pendente" not in corpo
    assert "já passou" in corpo, "a Revisão precisa dizer qual Evento venceu"


def test_o_edital_composto_do_zero_produz_os_mesmos_achados(client, seletor_ligado, composto):
    """FR-363. É regra de **todo** Edital, e não remendo do reaproveitamento — que é exatamente o
    que a `023` escreveu ao deixar esta regra fora do escopo dela: *"Se a instituição a quiser, ela
    tem spec própria e protege o acervo inteiro."*

    O Edital deste teste nunca partiu de outro: foi composto do zero, e recebe os mesmos achados.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    agora = timezone.now()
    datar(composto, inicio=agora - timedelta(days=9), fim=agora - timedelta(days=1))

    resposta = client.get(reverse("interface:compor-etapa", args=[composto.id, "revisao"]))

    assert resposta.context["origem_reaproveitada"] is None, "este Edital não veio de cópia nenhuma"
    codigos = {p["campo"] for p in resposta.context["pendencias"]}
    assert any("/schedule/id=" in caminho for caminho in codigos), codigos


# --- T036 · a frase que liga os avisos ao selo (UX-049) ------------------------------------------


def test_a_etapa_diz_por_que_esta_pendente_e_quantos_eventos_a_mantem_assim(
    client, seletor_ligado, composto
):
    """UX-049 tem duas metades, e só uma estava satisfeita.

    Os avisos já nomeavam cada Evento vencido — *"quais Eventos a mantêm assim"*. O que faltava era
    a frase que diz **por que** a etapa está pendente: quem lia via PENDENTE no topo e os avisos
    embaixo, e tinha de ligar os dois sozinho. É a mesma classe do achado de microcópia invisível da
    auditoria — a explicação existia e não estava dita.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    agora = timezone.now()
    datar(composto, inicio=agora - timedelta(days=9), fim=agora - timedelta(days=1))

    corpo = client.get(
        reverse("interface:compor-etapa", args=[composto.id, "cronograma"])
    ).content.decode()

    assert "fica <strong>pendente</strong> enquanto o Cronograma" in corpo
    assert "<strong>1 dele</strong>" in corpo, "a frase diz quantos Eventos a mantêm pendente"
    assert "o sistema não as altera nem as sugere" in corpo, "a FR-351 dita em voz alta"


def test_a_frase_nao_aparece_quando_nenhum_evento_venceu(client, seletor_ligado, composto):
    """Ruído numa etapa correta é o defeito simétrico: a frase só existe quando explica algo."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    agora = timezone.now()
    datar(composto, inicio=agora + timedelta(days=1), fim=agora + timedelta(days=9))

    corpo = client.get(
        reverse("interface:compor-etapa", args=[composto.id, "cronograma"])
    ).content.decode()

    assert "fica <strong>pendente</strong> enquanto o Cronograma" not in corpo


def test_a_frase_nao_aparece_num_cronograma_sem_evento_nenhum(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """**A etapa também fica pendente por não ter Evento algum, e aí a frase seria mentira.**

    Foi por isso que a tela recebeu a lista de vencidos, e não o estado do selo: os dois motivos de
    pendência são distintos, e explicar um com a razão do outro é pior do que não explicar.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    criado = api_client.post(
        "/api/v1/admin/processos",
        {**process_payload, "institutionalCode": "PS-SEM-EVENTO"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "selo-sem-evento-0001"},
    )
    vazio = Edital.objects.get(processo_id=criado.json()["id"])

    resposta = client.get(reverse("interface:compor-etapa", args=[vazio.id, "cronograma"]))
    corpo = resposta.content.decode()

    passos = {p["chave"]: p for p in resposta.context["progresso"]}
    assert passos["cronograma"]["estado"] == "pendente", "sem Evento também é pendente"
    assert "fica <strong>pendente</strong> enquanto o Cronograma" not in corpo


# --- 037 · a etapa que era impossível de concluir (SC-190) ---------------------------------------


def test_periodo_em_curso_conclui_a_etapa(client, seletor_ligado, composto):
    """`SC-190`: hoje esta etapa é impossível de concluir, e não por defeito de quem preenche.

    **O Edital que abre inscrições no dia em que é publicado é legítimo** — a conferência de
    publicação já dizia isso por escrito —, e ainda assim o selo ficava eternamente `PENDENTE`:
    a régua vencia pelo **ou** dos dois instantes, e um período em curso tem início no passado.
    Não havia data a corrigir; só havia a etapa vermelha.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    agora = timezone.now()
    datar(composto, inicio=agora - timedelta(days=1), fim=agora + timedelta(days=9))

    passos, _ = progresso(client, composto, etapa="identificacao")

    assert passos["cronograma"]["estado"] == "concluida"


def test_evento_pontual_no_passado_continua_mantendo_a_etapa_pendente(
    client, seletor_ligado, composto
):
    """A contraprova que impede a correção errada (`FR-546`).

    Trocar a régua por *"o término passou"* é a leitura imediata do defeito, e ela silenciaria o
    Evento **pontual**: sem término, nenhum Evento venceria nunca, e o Cronograma inteiro de uma
    oferta anterior voltaria a nascer verde — que é o achado que a `028` existe para ter fechado.

    Sem este caso, a correção errada passaria por todos os outros deste arquivo.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    agora = timezone.now()
    datar(composto, inicio=agora - timedelta(days=9), fim=None)

    passos, _ = progresso(client, composto, etapa="identificacao")

    assert passos["cronograma"]["estado"] == "pendente"
