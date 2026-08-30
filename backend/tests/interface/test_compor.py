"""Tela de composição do Edital (US2 e US3 da 002).

O que a tela promete: compor Perfis e Cronograma, mostrar o que falta para submeter, e recusar
com explicação sem perder o que a pessoa digitou. A validação real continua sendo do domínio.
"""

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.editais.models.cronograma import EventoCronograma
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
        "perfil-0-modalidades": "AC — Ampla concorrência\nPCD — Pessoa com deficiência",
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
def test_modalidade_sem_sigla_volta_para_a_tela_como_foi_digitada(
    client, seletor_ligado, edital
):
    """Sem separador, código e nome ficam iguais — devolver os dois só polui o campo."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(
        client, edital, perfis(**{"perfil-0-modalidades": "Ampla concorrência"}), eventos()
    )

    corpo = client.get(etapa(edital, "perfis")).content.decode()
    assert "Ampla concorrência — Ampla concorrência" not in corpo
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
