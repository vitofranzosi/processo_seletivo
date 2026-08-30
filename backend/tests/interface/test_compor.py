"""Tela de composição do Edital (US2 e US3 da 002).

O que a tela promete: compor Perfis e Cronograma, mostrar o que falta para submeter, e recusar
com explicação sem perder o que a pessoa digitou. A validação real continua sendo do domínio.
"""

import re
from decimal import Decimal
from uuid import UUID

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.editais.models.cronograma import EventoCronograma
from processo_seletivo.editais.models.etapas import EtapaAvaliacao
from processo_seletivo.editais.models.perfis import ModalidadeConcorrencia
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import compor_rascunho, identificar

PERFIL = "aaaaaaaa-0000-4000-8000-00000000e001"
EVENTO = "aaaaaaaa-0000-4000-8000-00000000e002"


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def perfis(**alteracoes):
    base = {
        "perfil-0-id": PERFIL,
        "perfil-0-code": "TEC-ADM",
        "perfil-0-name": "Técnico-Administrativo",
        "perfil-0-locality": "Campus Vitória",
        "perfil-0-immediateVacancies": "2",
        "perfil-0-reserveType": "LIMITED",
        "perfil-0-reserveLimit": "5",
        "perfil-0-requirements": "Ensino médio\nExperiência",
        # As modalidades são linhas próprias, indexadas dentro do índice do Perfil.
        "modalidade-0-0-id": "aaaaaaaa-0000-4000-8000-00000000e031",
        "modalidade-0-0-ruleId": "aaaaaaaa-0000-4000-8000-00000000e041",
        "modalidade-0-0-code": "AC",
        "modalidade-0-0-name": "Ampla concorrência",
        "modalidade-0-1-id": "aaaaaaaa-0000-4000-8000-00000000e032",
        "modalidade-0-1-ruleId": "aaaaaaaa-0000-4000-8000-00000000e042",
        "modalidade-0-1-code": "PCD",
        "modalidade-0-1-name": "Pessoa com deficiência",
        "modalidade-0-1-percentage": "5",
        "modalidade-0-1-foundation": "Lei 13.146/2015",
        "modalidade-0-1-version": "2015-07-06",
    }
    return {**base, **alteracoes}


def eventos(**alteracoes):
    base = {
        "evento-0-id": EVENTO,
        "evento-0-type": "INSCRICAO",
        "evento-0-description": "Período de inscrições",
        "evento-0-startAt": "2026-10-01T09:00",
        "evento-0-endAt": "2026-10-20T23:59",
    }
    return {**base, **alteracoes}


def etapa(edital, nome):
    return reverse("interface:compor-etapa", args=[edital.id, nome])


@pytest.mark.django_db
@pytest.mark.integration
def test_compor_salva_perfis_e_cronograma(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    resposta = client.get(etapa(edital, "revisao"))
    assert resposta.status_code == 200

    edital.refresh_from_db()
    perfil = edital.perfis.get()
    assert perfil.code == "TEC-ADM"
    assert perfil.immediate_vacancies == 2
    assert perfil.reserve_limit == 5
    assert perfil.requirements == ["Ensino médio", "Experiência"]
    assert sorted(m.code for m in perfil.modalidades.all()) == ["AC", "PCD"]

    evento = edital.cronograma.eventos.get()
    assert evento.type == "INSCRICAO"
    # 09:00 em America/Sao_Paulo é 12:00 UTC — a zona institucional é aplicada na tradução.
    assert evento.start_at.isoformat().startswith("2026-10-01T12:00")


@pytest.mark.django_db
@pytest.mark.integration
def test_recusa_do_dominio_e_explicada_sem_perder_o_que_foi_digitado(
    client, seletor_ligado, edital
):
    """FR-016 e FR-020: explicar o conflito e preservar o trabalho."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(etapa(edital, "perfis"), perfis())
    resposta = client.post(
        etapa(edital, "cronograma"),
        eventos(**{"evento-0-startAt": "2026-11-30T09:00", "evento-0-endAt": "2026-11-01T09:00"}),
    )
    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "Não foi possível salvar" in corpo
    assert "posterior ao término" in corpo
    assert "Período de inscrições" in corpo, "o Evento digitado precisa continuar na tela"
    assert "2026-11-30T09:00" in corpo, "a data digitada precisa continuar na tela"
    assert not edital.cronograma.eventos.exists(), "nada é gravado quando o domínio recusa"


@pytest.mark.django_db
@pytest.mark.integration
def test_reserva_limitada_sem_limite_e_recusada(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(
        etapa(edital, "perfis"),
        perfis(**{"perfil-0-reserveType": "LIMITED", "perfil-0-reserveLimit": ""}),
    )
    assert "Cadastro Reserva limitado exige limite" in resposta.content.decode()


@pytest.mark.django_db
@pytest.mark.integration
def test_data_malformada_e_explicada_antes_de_chegar_ao_dominio(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(etapa(edital, "cronograma"), eventos(**{"evento-0-startAt": "ontem"}))
    assert "não é uma data e hora válidas" in resposta.content.decode()


@pytest.mark.django_db
@pytest.mark.integration
def test_pendencias_mostram_o_que_falta_e_somem_quando_resolvidas(
    client, seletor_ligado, edital
):
    """FR-008: a tela diz o que falta para submeter, separando erro impeditivo de aviso."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    url = etapa(edital, "revisao")

    vazio = client.get(url).content.decode()
    assert "Ao menos um Perfil é obrigatório." in vazio
    assert "Ao menos um Evento é obrigatório." in vazio
    assert 'class="p-erro"' in vazio

    compor_rascunho(client, edital, perfis(), eventos())
    completo = client.get(url).content.decode()
    assert "Ao menos um Perfil é obrigatório." not in completo
    assert "Ao menos um Evento é obrigatório." not in completo
    # A descrição ausente continua sendo aviso, não impedimento.
    assert 'class="p-aviso"' in completo


@pytest.mark.django_db
@pytest.mark.integration
def test_sem_permissao_a_tela_e_somente_leitura(client, seletor_ligado, edital):
    identificar(client, "bruno.homologador", ["homologador"])
    corpo = client.get(etapa(edital, "perfis")).content.decode()
    assert "Somente leitura" in corpo
    assert "Salvar rascunho" not in corpo

    resposta = client.post(etapa(edital, "perfis"), perfis())
    assert resposta.status_code == 200
    assert "não tem permissão" in resposta.content.decode()
    assert not edital.perfis.exists()


@pytest.mark.django_db
@pytest.mark.integration
def test_edital_de_outro_escopo_nao_e_alcancavel(client, seletor_ligado, edital):
    """Anti-IDOR: conhecer o identificador não concede acesso."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    sessao = client.session
    sessao["interface_identidade"] = {
        "subject": "ana.elaboradora",
        "escopo": "outra-instituicao",
        "papeis": ["elaborador"],
    }
    sessao.save()
    assert client.get(etapa(edital, "perfis")).status_code == 404


@pytest.mark.django_db
@pytest.mark.integration
def test_fragmentos_htmx_trazem_linha_nova_com_identificador_proprio(
    client, seletor_ligado, edital
):
    identificar(client, "ana.elaboradora", ["elaborador"])
    primeiro = client.get(reverse("interface:fragmento-perfil"), {"indice": "7"}).content.decode()
    segundo = client.get(reverse("interface:fragmento-perfil"), {"indice": "8"}).content.decode()

    assert 'name="perfil-7-code"' in primeiro
    assert 'name="perfil-8-code"' in segundo
    assert primeiro != segundo, "cada linha nasce com identificador próprio"

    evento = client.get(reverse("interface:fragmento-evento"), {"indice": "3"}).content.decode()
    assert 'name="evento-3-startAt"' in evento
    assert client.get(reverse("interface:fragmento-remover")).content == b""


@pytest.mark.django_db
@pytest.mark.integration
def test_estrutura_acessivel_da_composicao(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    corpo = client.get(etapa(edital, "perfis")).content.decode()

    assert corpo.count("<h1>") == 1
    assert '<nav aria-label="Trilha de navegação"' in corpo
    assert '<nav aria-label="Etapas da composição"' in corpo
    assert 'aria-current="step"' in corpo, "a etapa atual precisa ser anunciada"
    assert "<fieldset" in corpo and "<legend>" in corpo, "grupos de campo precisam de rótulo"
    assert 'aria-describedby="ajuda-req-0"' in corpo, "texto de ajuda associado ao campo"
    assert corpo.count("<label for=") >= 8, "todo campo do Perfil precisa de rótulo associado"


@pytest.mark.django_db
@pytest.mark.integration
def test_edital_publicado_nao_e_editavel_pela_composicao(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-013: depois de publicado, o caminho é Retificação — não este formulário."""
    from tests.fixtures.publicacao import publish_original

    publicado = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.get(reverse("interface:compor-etapa", args=[publicado.id, "perfis"]))
    corpo = resposta.content.decode()
    assert "Somente leitura" in corpo
    assert "Retificação" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_identificacao_mostra_o_processo_e_oferece_titulo_e_descricao(
    client, seletor_ligado, edital
):
    """FR-006: a etapa deixou de ser somente leitura quando o ato de domínio nasceu.

    O que continua imutável é o que identifica o Edital perante o Processo — número e ano.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(etapa(edital, "identificacao")).content.decode()
    assert ProcessoSeletivo.objects.get().institutional_code in corpo
    assert 'name="title"' in corpo
    assert 'name="description"' in corpo
    assert "Não é editável nesta tela" not in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_modalidade_tem_campos_proprios_e_nao_texto_livre(client, seletor_ligado, edital):
    """A `002` lia as modalidades de uma caixa de texto no formato `CÓDIGO — Nome`.

    O formato perdia tudo o que não coubesse em duas palavras: percentual, fundamento e versão do
    fundamento não tinham onde ser digitados. O teste anterior verificava um detalhe daquele
    formato — que um nome sem separador não fosse repetido —, e o formato deixou de existir.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())

    corpo = client.get(etapa(edital, "perfis")).content.decode()
    assert 'name="perfil-0-modalidades"' not in corpo, "a caixa de texto livre saiu"
    for campo in ("code", "name", "percentage", "foundation", "version"):
        assert f'name="modalidade-0-0-{campo}"' in corpo
    assert 'name="modalidade-0-0-id"' in corpo and 'name="modalidade-0-0-ruleId"' in corpo
    assert "Ampla concorrência" in corpo


@pytest.mark.django_db(transaction=True)
def test_a_validacao_antes_do_envio_e_carregada_nas_telas_que_editam(
    client, seletor_ligado, edital
):
    """FR-026 da 003: as regras que dão para saber na tela não precisam de ida ao servidor."""
    from django.contrib.staticfiles import finders

    identificar(client, "ana.elaboradora", ["elaborador"])
    assert finders.find("interface/validacao.js")
    for etapa in ("perfis", "cronograma"):
        corpo = client.get(
            reverse("interface:compor-etapa", args=[edital.id, etapa])
        ).content.decode()
        assert "interface/validacao.js" in corpo


def test_a_validacao_da_tela_se_declara_como_nao_sendo_fronteira_de_seguranca():
    """O comportamento é verificado executando o script, em tests/javascript/validacao.test.js.

    O que sobra aqui é a única coisa que um teste de fonte prova de verdade: que o arquivo diz a
    quem for mexer nele que a decisão continua sendo do domínio. Regra de tela que se acredita
    autoridade é como uma invariante deixa de ser verificada no servidor.
    """
    from pathlib import Path

    fonte = (
        Path(__file__).resolve().parents[2]
        / "processo_seletivo/interface/static/interface/validacao.js"
    ).read_text(encoding="utf-8")

    assert "NÃO é fronteira de segurança" in fonte


@pytest.mark.django_db(transaction=True)
def test_o_servidor_recusa_mesmo_sem_a_validacao_da_tela(client, seletor_ligado, edital):
    """FR-026: a tela pode ser burlada; o domínio é quem decide.

    O POST vai direto ao endpoint, como faria qualquer cliente sem JavaScript. As duas regras
    testadas são as que a tela verifica — e o servidor precisa recusar as duas do mesmo jeito.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    reserva = client.post(
        reverse("interface:compor-etapa", args=[edital.id, "perfis"]),
        {
            "perfil-0-id": "00000000-0000-0000-0000-000000000801",
            "perfil-0-code": "P1",
            "perfil-0-name": "Perfil",
            "perfil-0-immediateVacancies": "1",
            "perfil-0-reserveType": "LIMITED",
            "perfil-0-reserveLimit": "",
        },
    )

    assert reserva.status_code == 200
    # A mensagem exata do domínio, não uma palavra que o próprio formulário já contém.
    assert "Cadastro Reserva limitado exige limite não negativo." in reserva.content.decode()
    assert not edital.perfis.exists()

    codigos = client.post(
        reverse("interface:compor-etapa", args=[edital.id, "perfis"]),
        {
            "perfil-0-id": "00000000-0000-0000-0000-000000000802",
            "perfil-0-code": "P1",
            "perfil-0-name": "Um",
            "perfil-0-immediateVacancies": "1",
            "perfil-0-reserveType": "NONE",
            "perfil-1-id": "00000000-0000-0000-0000-000000000803",
            "perfil-1-code": "P1",
            "perfil-1-name": "Outro",
            "perfil-1-immediateVacancies": "1",
            "perfil-1-reserveType": "NONE",
        },
    )

    assert codigos.status_code == 200
    assert "Códigos de Perfil não podem se repetir no Edital." in codigos.content.decode()
    assert not edital.perfis.exists()


@pytest.mark.django_db(transaction=True)
def test_pendencia_aponta_para_a_etapa_que_a_resolve(client, seletor_ligado, edital):
    """FR-027 da 003: a interface descartava o campo que o domínio informa em cada achado."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    revisao = client.get(
        reverse("interface:compor-etapa", args=[edital.id, "revisao"])
    ).content.decode()

    perfis = reverse("interface:compor-etapa", args=[edital.id, "perfis"])
    cronograma = reverse("interface:compor-etapa", args=[edital.id, "cronograma"])
    assert f'href="{perfis}#perfis-titulo"' in revisao
    assert f'href="{cronograma}#cronograma-titulo"' in revisao


@pytest.mark.django_db(transaction=True)
def test_cada_etapa_mostra_apenas_a_pendencia_que_resolve(client, seletor_ligado, edital):
    """Pendência exibida onde não há como agir vira ruído que a pessoa aprende a ignorar."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    em_perfis = client.get(
        reverse("interface:compor-etapa", args=[edital.id, "perfis"])
    ).content.decode()
    em_cronograma = client.get(
        reverse("interface:compor-etapa", args=[edital.id, "cronograma"])
    ).content.decode()

    assert "Ao menos um Perfil é obrigatório." in em_perfis
    assert "Ao menos um Evento é obrigatório." not in em_perfis
    assert "Ao menos um Evento é obrigatório." in em_cronograma
    assert "Ao menos um Perfil é obrigatório." not in em_cronograma


@pytest.mark.django_db(transaction=True)
def test_pendencia_de_identificacao_passa_a_ter_caminho(client, seletor_ligado, edital):
    """FR-007: a `002` declarava esta pendência incorrigível, e estava certa — não havia ato.

    Com `update_edital_identification`, o caminho existe e termina em algum lugar: o link da
    pendência leva à etapa, com a âncora da seção. Declarar incorrigível o que a etapa resolve
    seria pior do que a situação anterior, porque agora seria falso.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    revisao = client.get(
        reverse("interface:compor-etapa", args=[edital.id, "revisao"])
    ).content.decode()
    identificacao = reverse("interface:compor-etapa", args=[edital.id, "identificacao"])

    assert "O Edital não possui descrição." in revisao
    assert f'href="{identificacao}#ident-titulo"' in revisao
    assert "Não corrigível aqui" not in revisao


@pytest.mark.django_db
@pytest.mark.integration
def test_identificacao_alterada_persiste_e_e_auditada(client, seletor_ligado, edital):
    """FR-006: o ato existe, é do domínio, e deixa rastro como qualquer outro."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(
        etapa(edital, "identificacao"),
        {"title": "Edital revisado", "description": "Descrição informada depois da criação."},
    )
    assert resposta.status_code == 302, resposta.content

    edital.refresh_from_db()
    assert edital.title == "Edital revisado"
    assert edital.description == "Descrição informada depois da criação."
    assert edital.last_edited_by == "ana.elaboradora"

    registro = RegistroAuditoria.objects.filter(operation="ALTERAR_IDENTIFICACAO").get()
    assert registro.actor_subject == "ana.elaboradora"
    assert registro.aggregate_id == edital.id


@pytest.mark.django_db
@pytest.mark.integration
def test_identificacao_sem_titulo_e_recusada_sem_perder_o_digitado(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    anterior = edital.title
    resposta = client.post(
        etapa(edital, "identificacao"), {"title": "   ", "description": "Vale guardar"}
    )

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "título do Edital é obrigatório" in corpo
    assert "Vale guardar" in corpo, "o que foi digitado precisa sobreviver à recusa"
    edital.refresh_from_db()
    assert edital.title == anterior


@pytest.mark.django_db
@pytest.mark.integration
def test_identificacao_nao_e_alteravel_fora_da_elaboracao(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """A recusa é do domínio; a tela apenas deixa de oferecer o formulário."""
    publicado = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "ana.elaboradora", ["elaborador"])
    anterior = publicado.title

    resposta = client.post(
        etapa(publicado, "identificacao"), {"title": "Tentativa", "description": ""}
    )

    assert resposta.status_code == 200
    assert "não está em elaboração" in resposta.content.decode()
    publicado.refresh_from_db()
    assert publicado.title == anterior


@pytest.mark.django_db
@pytest.mark.integration
def test_reordenar_muda_a_ordem_persistida_e_preserva_a_identidade(
    client, seletor_ligado, edital
):
    """FR-003 e FR-004, e a correção de uma afirmação errada do plano.

    A primeira versão dizia que bastava mover a linha no DOM, porque a gravação derivaria a ordem
    da posição. Não derivaria: `_indices` devolve os índices ordenados numericamente, então a
    posição visual era descartada antes da leitura. O teste que prova isso é o da **ordem
    persistida** — o da identidade sozinho passaria mesmo com o defeito.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    tres = {
        f"evento-{indice}-{campo}": valor
        for indice, (identificador, tipo) in enumerate(
            [
                ("aaaaaaaa-0000-4000-8000-00000000e011", "INSCRICAO"),
                ("aaaaaaaa-0000-4000-8000-00000000e012", "PROVA"),
                ("aaaaaaaa-0000-4000-8000-00000000e013", "RESULTADO"),
            ]
        )
        for campo, valor in {
            "id": identificador,
            "type": tipo,
            "description": f"Etapa {tipo}",
            "startAt": f"2026-1{indice}-01T09:00",
            "order": str(indice + 1),
        }.items()
    }
    compor_rascunho(client, edital, perfis(), tres)

    antes = list(EventoCronograma.objects.order_by("order").values_list("id", "type"))
    assert [tipo for _, tipo in antes] == ["INSCRICAO", "PROVA", "RESULTADO"]

    # O terceiro vai para a primeira posição — é o que os botões fazem ao campo `order`.
    edital.refresh_from_db()
    movido = dict(tres, **{"evento-2-order": "0"})
    resposta = client.post(etapa(edital, "cronograma"), movido)
    assert resposta.status_code == 302, resposta.content

    depois = list(EventoCronograma.objects.order_by("order").values_list("id", "type", "order"))
    assert [tipo for _, tipo, _ in depois] == ["RESULTADO", "INSCRICAO", "PROVA"]
    assert [ordem for _, _, ordem in depois] == [1, 2, 3], "a numeração fica sem buraco"
    assert {identificador for identificador, _, _ in depois} == {
        identificador for identificador, _ in antes
    }, "reordenar não pode trocar a identidade de nenhum Evento"


def etapas_form(**alteracoes):
    base = {
        "etapa-0-id": "aaaaaaaa-0000-4000-8000-00000000e021",
        "etapa-0-name": "Prova didática",
        "etapa-0-order": "1",
        "etapa-0-weight": "2",
        "etapa-0-minimumScore": "7",
        "etapa-0-eliminatory": "on",
        "etapa-0-classificatory": "on",
        "etapa-0-scheduleEventId": EVENTO,
        "etapa-1-id": "aaaaaaaa-0000-4000-8000-00000000e022",
        "etapa-1-name": "Análise de títulos",
        "etapa-1-order": "2",
        "etapa-1-weight": "",
        "etapa-1-minimumScore": "",
        "etapa-1-scheduleEventId": "",
    }
    return {**base, **alteracoes}


@pytest.mark.django_db
@pytest.mark.integration
def test_etapas_sao_acrescentadas_editadas_e_preservam_identidade(
    client, seletor_ligado, edital
):
    """US2: o ciclo inteiro do assistente, incluindo a ida e volta por outra etapa."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    edital.refresh_from_db()

    resposta = client.post(etapa(edital, "etapas"), etapas_form())
    assert resposta.status_code == 302, resposta.content

    gravadas = list(EtapaAvaliacao.objects.order_by("order"))
    assert [item.name for item in gravadas] == ["Prova didática", "Análise de títulos"]
    assert gravadas[0].weight == Decimal("2.0000")
    assert gravadas[0].minimum_score == Decimal("7.0000")
    assert gravadas[0].eliminatory and gravadas[0].classificatory
    assert str(gravadas[0].evento_id) == EVENTO
    # A segunda não pondera e não tem nota mínima — a ausência é que diz isso.
    assert gravadas[1].weight is None and gravadas[1].minimum_score is None
    assert gravadas[1].evento_id is None
    identidades = {item.id for item in gravadas}

    # Salvar outra etapa do assistente não pode apagar o que foi configurado aqui.
    edital.refresh_from_db()
    assert client.post(etapa(edital, "cronograma"), eventos()).status_code == 302
    assert {item.id for item in EtapaAvaliacao.objects.all()} == identidades

    corpo = client.get(etapa(edital, "etapas")).content.decode()
    assert "Prova didática" in corpo and "Análise de títulos" in corpo
    # As datas não são digitadas na Etapa: elas vêm do Evento vinculado.
    assert 'name="etapa-0-startAt"' not in corpo
    assert f'value="{EVENTO}"' in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_reordenar_etapas_preserva_identidade(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    edital.refresh_from_db()
    client.post(etapa(edital, "etapas"), etapas_form())
    antes = {item.id: item.name for item in EtapaAvaliacao.objects.all()}

    edital.refresh_from_db()
    resposta = client.post(etapa(edital, "etapas"), etapas_form(**{"etapa-1-order": "0"}))
    assert resposta.status_code == 302, resposta.content

    depois = list(EtapaAvaliacao.objects.order_by("order"))
    assert [item.name for item in depois] == ["Análise de títulos", "Prova didática"]
    assert [item.order for item in depois] == [1, 2]
    assert {item.id: item.name for item in depois} == antes


@pytest.mark.django_db
@pytest.mark.integration
def test_remover_etapa_e_gravar_deixa_apenas_a_restante(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    edital.refresh_from_db()
    client.post(etapa(edital, "etapas"), etapas_form())

    edital.refresh_from_db()
    restante = {
        chave: valor for chave, valor in etapas_form().items() if not chave.startswith("etapa-1-")
    }
    assert client.post(etapa(edital, "etapas"), restante).status_code == 302

    assert [item.name for item in EtapaAvaliacao.objects.all()] == ["Prova didática"]


@pytest.mark.django_db
@pytest.mark.integration
def test_peso_zero_e_recusado_sem_perder_o_digitado(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    edital.refresh_from_db()

    resposta = client.post(etapa(edital, "etapas"), etapas_form(**{"etapa-0-weight": "0"}))

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "maior que zero" in corpo
    assert "Prova didática" in corpo, "o que foi digitado precisa sobreviver à recusa"
    assert not EtapaAvaliacao.objects.exists()


@pytest.mark.django_db
@pytest.mark.integration
def test_fragmento_de_etapa_nasce_com_identidade_e_com_os_eventos_do_edital(
    client, seletor_ligado, edital
):
    """Sem UUID gerado aqui, a linha nova nasceria sem identidade e não haveria o que preservar."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())

    corpo = client.get(
        reverse("interface:fragmento-etapa", args=[edital.id]), {"indice": "5"}
    ).content.decode()

    assert 'name="etapa-5-id"' in corpo
    identificador = corpo.split('name="etapa-5-id" value="')[1].split('"')[0]
    assert UUID(identificador)
    assert 'name="etapa-5-order"' in corpo
    assert EVENTO in corpo, "o vínculo precisa oferecer os Eventos deste Cronograma"


@pytest.mark.django_db
@pytest.mark.integration
def test_regra_normativa_sobrevive_a_gravacao_de_outra_etapa(client, seletor_ligado, edital):
    """O defeito de linha de base do `quickstart.md`, e o miolo da US3.

    Três defeitos encadeados produziam a perda: a modalidade era criada sem o `id` recebido, a
    serialização de preservação levava só `code` e `name`, e a leitura vinha de uma caixa de texto
    que não tinha onde guardar fundamento nem percentual. Configurar cotas, ir ao Cronograma e
    salvar apagava as regras.

    O que se afirma aqui é a ida e volta inteira — inclusive **a identidade da Regra**, que é a
    metade do defeito que a primeira versão desta spec não via.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())

    antes = {
        modalidade.code: (modalidade.id, getattr(modalidade, "regra_normativa", None))
        for modalidade in ModalidadeConcorrencia.objects.all()
    }
    assert antes["PCD"][1] is not None, "a regra precisa ter sido gravada"
    assert antes["PCD"][1].percentage == Decimal("5.0000")
    assert antes["PCD"][1].foundation == "Lei 13.146/2015"
    assert antes["PCD"][1].version == "2015-07-06"
    identidades = {
        codigo: (item[0], item[1].id if item[1] else None) for codigo, item in antes.items()
    }

    # Salvar o Cronograma relê os Perfis e os reenvia. É aqui que tudo se perdia.
    edital.refresh_from_db()
    assert client.post(etapa(edital, "cronograma"), eventos()).status_code == 302

    depois = {
        modalidade.code: (modalidade.id, getattr(modalidade, "regra_normativa", None))
        for modalidade in ModalidadeConcorrencia.objects.all()
    }
    assert set(depois) == {"AC", "PCD"}
    assert depois["PCD"][1] is not None, "a Regra Normativa não pode desaparecer"
    assert depois["PCD"][1].percentage == Decimal("5.0000")
    assert {
        codigo: (item[0], item[1].id if item[1] else None) for codigo, item in depois.items()
    } == identidades, "as identidades da modalidade e da regra são as mesmas"


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize("percentual", ["0", "120"])
def test_percentual_fora_da_faixa_e_recusado_pela_interface(
    client, seletor_ligado, edital, percentual
):
    """FR-030: a recusa é do domínio, e a interface a atravessa como qualquer outra."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(
        etapa(edital, "perfis"), perfis(**{"modalidade-0-1-percentage": percentual})
    )

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "maior que zero e menor ou igual a cem" in corpo
    assert "Lei 13.146/2015" in corpo, "o que foi digitado precisa sobreviver à recusa"
    assert not ModalidadeConcorrencia.objects.exists()


@pytest.mark.django_db
@pytest.mark.integration
def test_fragmento_de_modalidade_nasce_com_os_dois_identificadores(
    client, seletor_ligado, edital
):
    """Sem os dois UUID, a linha nova nasceria sem identidade e não haveria o que preservar."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(
        reverse("interface:fragmento-modalidade", args=["2"]), {"indice": "9"}
    ).content.decode()

    assert 'name="modalidade-2-9-id"' in corpo
    assert 'name="modalidade-2-9-ruleId"' in corpo
    identificadores = [
        corpo.split(f'name="modalidade-2-9-{campo}" value="')[1].split('"')[0]
        for campo in ("id", "ruleId")
    ]
    assert all(UUID(item) for item in identificadores)
    assert identificadores[0] != identificadores[1]


@pytest.mark.django_db
@pytest.mark.integration
def test_secao_textual_editada_e_gravada_e_reexibida(client, seletor_ligado, edital):
    """FR-037: o texto institucional nasce padrão e passa a ser o que quem elabora escreveu."""
    from processo_seletivo.editais.domain import secoes as catalogo
    from processo_seletivo.editais.models.secoes import SecaoEdital

    identificar(client, "ana.elaboradora", ["elaborador"])
    # `replace_draft` é substituição total e exige ao menos um Perfil: gravar qualquer etapa
    # reenvia o rascunho inteiro, e um rascunho sem Perfil é recusado pelo domínio.
    compor_rascunho(client, edital, perfis(), eventos())
    edital.refresh_from_db()

    padrao = catalogo.POR_CHAVE["disposicoes-preliminares"].default_text
    inicial = client.get(etapa(edital, "conteudo")).content.decode()
    assert padrao in inicial
    assert 'name="secao-cronograma"' not in inicial, "seção gerada não tem texto a redigir"
    assert 'name="secao-disposicoes-preliminares"' in inicial

    resposta = client.post(
        etapa(edital, "conteudo"),
        {"secao-disposicoes-preliminares": "Redação revisada pela Procuradoria."},
    )
    assert resposta.status_code == 302, resposta.content

    linha = SecaoEdital.objects.get()
    assert linha.key == "disposicoes-preliminares"
    assert linha.content == "Redação revisada pela Procuradoria."
    # Uma identidade só: a da linha é a mesma que o snapshot publica.
    assert linha.id == catalogo.identidade(edital.id, "disposicoes-preliminares")

    depois = client.get(etapa(edital, "conteudo")).content.decode()
    assert "Redação revisada pela Procuradoria." in depois
    assert padrao not in depois


@pytest.mark.django_db
@pytest.mark.integration
def test_secao_textual_sobrevive_a_gravacao_de_outra_etapa(client, seletor_ligado, edital):
    from processo_seletivo.editais.models.secoes import SecaoEdital

    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    edital.refresh_from_db()
    client.post(etapa(edital, "conteudo"), {"secao-recursos": "Prazo de três dias úteis."})

    edital.refresh_from_db()
    assert client.post(etapa(edital, "cronograma"), eventos()).status_code == 302

    assert SecaoEdital.objects.get().content == "Prazo de três dias úteis."


@pytest.mark.django_db
@pytest.mark.integration
def test_salvar_conteudo_sem_editar_nada_nao_congela_o_texto_do_catalogo(
    client, seletor_ligado, edital
):
    """O que a demonstração de ponta a ponta revelou, e o `quickstart` não previa.

    A tela mostra as sete seções e envia as quatro textuais preenchidas. Gravar todas criava linha
    para seção que ninguém tocou, e "ausência de linha significa texto padrão do catálogo" deixava
    de valer no primeiro salvamento — congelando a redação institucional, de modo que corrigi-la em
    código não alcançaria nenhum Edital que já tivesse passado por aqui.
    """
    from processo_seletivo.editais.domain import secoes as catalogo
    from processo_seletivo.editais.models.secoes import SecaoEdital

    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    edital.refresh_from_db()

    # Exatamente o que a tela reenviaria sem nenhuma edição.
    intocado = {
        f"secao-{secao.key}": secao.default_text
        for secao in catalogo.CATALOGO
        if not secao.gerada
    }
    assert client.post(etapa(edital, "conteudo"), intocado).status_code == 302
    assert not SecaoEdital.objects.exists(), "nada foi editado; nada precisa de linha"

    edital.refresh_from_db()
    editado = dict(intocado, **{"secao-recursos": "Três dias úteis, pelo sistema."})
    assert client.post(etapa(edital, "conteudo"), editado).status_code == 302

    assert [item.key for item in SecaoEdital.objects.all()] == ["recursos"]


# ---------------------------------------------------------------------------
# 007 — o Edital diz o que a vaga é, e tem as seções que um Edital tem
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_a_etapa_de_conteudo_mostra_as_dez_secoes_do_catalogo(client, seletor_ligado, edital):
    """T013/T014: a etapa deriva do catálogo, então as três novas entram sem código de tela."""
    from processo_seletivo.editais.domain import secoes as catalogo

    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.get(reverse("interface:compor-etapa", args=[edital.id, "conteudo"]))

    exibidas = [secao["key"] for secao in resposta.context["secoes"]]
    assert exibidas == [secao.key for secao in catalogo.CATALOGO]
    assert len(exibidas) == 10
    for nova in ("apresentacao", "requisitos-gerais", "classificacao"):
        assert nova in exibidas


@pytest.mark.django_db(transaction=True)
def test_texto_de_secao_nova_e_gravado_e_chega_a_previa(client, seletor_ligado, edital):
    """T014: editar `apresentacao` e encontrá-la na prévia, na posição declarada pelo catálogo."""
    from processo_seletivo.editais.domain import secoes as catalogo

    identificar(client, "ana.elaboradora", ["elaborador"])
    texto = "Redação institucional própria deste Edital de demonstração."

    # A gravação reenvia o rascunho inteiro, e o command exige ao menos um Perfil.
    compor_rascunho(
        client,
        edital,
        perfis={
            "perfil-0-id": PERFIL,
            "perfil-0-code": "PROF",
            "perfil-0-name": "Professor",
            "perfil-0-immediateVacancies": "1",
            "perfil-0-reserveType": "NONE",
        },
    )

    campos = {
        f"secao-{secao.key}": (texto if secao.key == "apresentacao" else secao.default_text)
        for secao in catalogo.CATALOGO
        if not secao.gerada
    }
    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital.id, "conteudo"]), campos
    )
    assert resposta.status_code == 302, resposta.content

    documento = client.get(reverse("interface:previa-documento", args=[edital.id]))
    conteudo = documento.content.decode("latin-1")
    assert "Reda" in conteudo, "a seção editada precisa chegar ao documento"


@pytest.mark.django_db(transaction=True)
def test_os_tres_campos_do_perfil_sobrevivem_a_gravacao_de_outra_etapa(
    client, seletor_ligado, edital
):
    """T023: o defeito que a `006` teve com as modalidades não pode renascer com estes campos.

    Salvar o Cronograma relê os Perfis e os reenvia. Se `perfis_persistidos` não levar os três, a
    ida e volta os apaga — em silêncio, como apagava a Regra Normativa antes da `006`.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    atribuicoes = "Ministrar aulas.\n\nOrientar projetos de extensão."

    compor_rascunho(
        client,
        edital,
        perfis={
            "perfil-0-id": PERFIL,
            "perfil-0-code": "PROF",
            "perfil-0-name": "Professor",
            "perfil-0-immediateVacancies": "1",
            "perfil-0-reserveType": "NONE",
            "perfil-0-duties": atribuicoes,
            "perfil-0-workload": "20 horas semanais",
            "perfil-0-compensation": "R$ 3.000,00 mensais",
        },
        eventos={
            "evento-0-id": EVENTO,
            "evento-0-type": "Inscrições",
            "evento-0-description": "Inscrições pelo sistema",
            "evento-0-startAt": "2027-03-01T10:00",
            "evento-0-order": "1",
        },
    )

    perfil = edital.perfis.get()
    assert perfil.duties == atribuicoes, "gravar o Cronograma não pode apagar as atribuições"
    assert perfil.workload == "20 horas semanais"
    assert perfil.compensation == "R$ 3.000,00 mensais"

    # E voltam à tela para quem retoma o trabalho.
    resposta = client.get(reverse("interface:compor-etapa", args=[edital.id, "perfis"]))
    exibido = resposta.context["perfis"][0]
    assert exibido["duties"] == atribuicoes
    assert exibido["workload"] == "20 horas semanais"
    assert exibido["compensation"] == "R$ 3.000,00 mensais"


@pytest.mark.django_db(transaction=True)
def test_o_seletor_de_evento_mostra_a_data_que_a_etapa_herda(client, seletor_ligado, edital):
    """FR-036, e o teste que faltava.

    A Etapa se vincula a um Evento **para herdar as datas** — é o que a ajuda promete. A lista
    mostrava "tipo — descrição", cortava por falta de largura e não mostrava data nenhuma.

    Este teste existe por um motivo concreto: ao trocar o texto da opção, o template passou a ler
    `evento.rotulo` e o campo não chegou a ser criado em `forms.py`. A suíte inteira continuou
    verde — nenhum teste olhava o texto da opção — e o defeito só apareceu no navegador, com um
    `<option>` vazio. Uma opção sem texto é pior do que a lista truncada que existia antes.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(
        client,
        edital,
        perfis={
            "perfil-0-id": PERFIL,
            "perfil-0-code": "P",
            "perfil-0-name": "Perfil",
            "perfil-0-immediateVacancies": "1",
            "perfil-0-reserveType": "NONE",
        },
        eventos={
            "evento-0-id": EVENTO,
            "evento-0-type": "Prova didática",
            "evento-0-description": "Aplicação da prova",
            "evento-0-startAt": "2027-04-10T14:00",
            "evento-0-order": "1",
        },
    )

    resposta = client.get(reverse("interface:fragmento-etapa", args=[edital.id]))
    corpo = resposta.content.decode()

    assert "Prova didática · 10/04/2027 14:00" in corpo
    # E nenhuma opção fica sem texto — foi assim que o defeito passou.
    assert not re.search(r'<option value="[0-9a-f-]{36}"[^>]*>\s*</option>', corpo), (
        "opção de Evento sem texto"
    )
