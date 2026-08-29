"""Tela de composição do Edital (US2 e US3 da 002).

O que a tela promete: compor Perfis e Cronograma, mostrar o que falta para submeter, e recusar
com explicação sem perder o que a pessoa digitou. A validação real continua sendo do domínio.
"""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital, ProcessoSeletivo
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
def test_identificacao_mostra_o_processo_e_diz_que_nao_e_editavel(client, seletor_ligado, edital):
    """Não há command que altere título ou descrição após a criação — a tela diz isso."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(etapa(edital, "identificacao")).content.decode()
    assert ProcessoSeletivo.objects.get().institutional_code in corpo
    assert "Não é editável nesta tela" in corpo


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


def test_as_regras_da_tela_espelham_as_do_dominio():
    """A validação da tela não pode inventar regra que o domínio não tem, nem o contrário.

    Compara o texto de `validacao.js` com o que `editais.domain` decide: o que se verifica aqui
    é que as quatro regras espelhadas estão nomeadas no arquivo, para que remover uma delas do
    domínio sem remover da tela apareça na revisão em vez de virar mensagem fantasma.
    """
    from pathlib import Path

    fonte = (
        Path(__file__).resolve().parents[2]
        / "processo_seletivo/interface/static/interface/validacao.js"
    ).read_text(encoding="utf-8")

    assert "Cadastro Reserva limitado exige um limite." in fonte
    assert "não admite limite" in fonte
    assert "Vagas imediatas não podem ser negativas." in fonte
    assert "O término do Evento não pode ser anterior ao início." in fonte
    assert "aparece mais de uma vez neste Perfil" in fonte
    # A tela não é fronteira de segurança e o arquivo precisa dizer isso a quem for mexer nele.
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
