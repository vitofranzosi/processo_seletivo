"""Tela de desfecho do Processo Seletivo (US5 da 002).

O cenário que dá nome à história: quando o cancelamento é impedido, a tela precisa identificar
o que impede e permitir alcançar cada pendência — antes da tentativa, não depois da recusa.
"""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

GESTOR = ["gestor"]


@pytest.fixture
def cenario(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)
    return ProcessoSeletivo.objects.get(), edital


@pytest.fixture
def sem_publicacao(client, seletor_ligado):
    """Processo criado e nada mais — o único estado em que "Ativar" ainda é ato de alguém.

    Depois de E2E-005, publicar o primeiro Edital **é** a abertura formal do certame, e o ato
    explícito sobra para quem abre antes de publicar. Testar "ativar" sobre Processo publicado
    passou a testar o impossível.
    """
    identificar(client, "gestora", ["gestor"])
    client.post(
        reverse("interface:processo-criar"),
        {
            "codigo": "PS-2028-009",
            "titulo": "Processo sem publicação",
            "numero": "09",
            "ano": "2028",
            "titulo_edital": "Edital em elaboração",
            "descricao": "Ainda não publicado",
            "chave_idempotencia": "ui-criacao-000000009",
        },
    )
    return ProcessoSeletivo.objects.get(institutional_code="PS-2028-009")


def ato(client, processo, acao, motivo="Ato motivado"):
    url = reverse("interface:processo-ato", args=[processo.id, acao])
    chave = client.get(url).context["chave_idempotencia"]
    return client.post(url, {"chave_idempotencia": chave, "motivo": motivo})


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_detalhe_mostra_a_trilha_e_os_editais(client, seletor_ligado, cenario):
    processo, edital = cenario
    identificar(client, "marcia.gestora", GESTOR)
    corpo = client.get(reverse("interface:processo-detalhe", args=[processo.id])).content.decode()

    assert processo.institutional_code in corpo
    assert f"{edital.number}/{edital.year}" in corpo
    assert 'class="e-atual"' in corpo
    # Publicar o primeiro Edital já abriu o certame (E2E-005): o que resta é encerrá-lo.
    assert "Encerrar Processo" in corpo
    assert "Ativar Processo" not in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_impedimento_do_cancelamento_e_mostrado_antes_da_tentativa(client, seletor_ligado, cenario):
    """FR-018: identificar o que impede e permitir alcançar cada pendência."""
    processo, edital = cenario
    identificar(client, "marcia.gestora", GESTOR)

    detalhe = client.get(reverse("interface:processo-detalhe", args=[processo.id])).content.decode()
    assert "O cancelamento do Processo está impedido" in detalhe
    assert f"{edital.number}/{edital.year}" in detalhe
    assert reverse("interface:detalhe", args=[edital.id]) in detalhe, "link para a pendência"

    confirmacao = client.get(
        reverse("interface:processo-ato", args=[processo.id, "cancelar"])
    ).content.decode()
    assert "Este ato será recusado" in confirmacao
    assert "Encerrado ou Cancelado" in confirmacao


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_cancelamento_e_recusado_pelo_dominio_e_explicado(client, seletor_ligado, cenario):
    processo, _ = cenario
    identificar(client, "marcia.gestora", GESTOR)
    resposta = ato(client, processo, "cancelar", "Tentativa prematura")

    assert resposta.status_code == 409
    assert "Cancele ou encerre cada Edital" in resposta.content.decode()
    assert ProcessoSeletivo.objects.get().status == processo.status


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_cancelamento_e_admitido_quando_os_editais_sao_finalizados(client, seletor_ligado, cenario):
    processo, edital = cenario
    identificar(client, "marcia.gestora", ["gestor"])
    # Encerrar o Edital exige permissão própria; o gestor a possui.
    url = reverse("interface:ato", args=[edital.id, "encerrar"])
    chave = client.get(url).context["chave_idempotencia"]
    client.post(url, {"chave_idempotencia": chave, "motivo": "Etapas concluídas"})
    assert Edital.objects.get().status == Edital.Status.ENCERRADO

    processo.refresh_from_db()
    detalhe = client.get(reverse("interface:processo-detalhe", args=[processo.id])).content.decode()
    assert "está impedido" not in detalhe

    assert ato(client, processo, "cancelar", "Todos finalizados").status_code == 302
    assert ProcessoSeletivo.objects.get().status == ProcessoSeletivo.Status.CANCELADO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_ativar_e_encerrar_seguem_o_fluxo_ordinario(client, seletor_ligado, sem_publicacao):
    """A abertura declarada continua existindo, para quem abre o certame antes de publicar."""
    processo = sem_publicacao
    identificar(client, "marcia.gestora", GESTOR)

    assert ato(client, processo, "ativar", "Abertura formal").status_code == 302
    processo.refresh_from_db()
    assert processo.status == ProcessoSeletivo.Status.ATIVO

    corpo = client.get(reverse("interface:processo-detalhe", args=[processo.id])).content.decode()
    assert "Encerrar Processo" in corpo
    assert "Ativar Processo" not in corpo, "não se ativa o que já está ativo"

    assert ato(client, processo, "encerrar", "Certame concluído").status_code == 302
    processo.refresh_from_db()
    assert processo.status == ProcessoSeletivo.Status.ENCERRADO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_encerrar_avisa_que_os_editais_deixam_de_aceitar_alteracao(client, seletor_ligado, cenario):
    processo, _ = cenario
    identificar(client, "marcia.gestora", GESTOR)
    ato(client, processo, "ativar", "Abertura")
    processo.refresh_from_db()

    corpo = client.get(
        reverse("interface:processo-ato", args=[processo.id, "encerrar"])
    ).content.decode()
    assert "Este ato não pode ser desfeito" in corpo
    assert "deixam de aceitar qualquer alteração" in corpo
    assert "permanecem disponíveis na consulta pública" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_cancelamento_avisa_que_nao_propaga_para_os_editais(client, seletor_ligado, cenario):
    """FR-034: cancelar o Processo não cancela Editais; cada um exige ato próprio."""
    processo, _ = cenario
    identificar(client, "marcia.gestora", GESTOR)
    corpo = client.get(
        reverse("interface:processo-ato", args=[processo.id, "cancelar"])
    ).content.decode()
    assert "Nenhum Edital é cancelado por consequência" in corpo
    assert "não é o mesmo que encerramento regular" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_motivo_e_obrigatorio_em_todo_ato_do_processo(client, seletor_ligado, sem_publicacao):
    processo = sem_publicacao
    identificar(client, "marcia.gestora", GESTOR)
    resposta = ato(client, processo, "ativar", motivo="   ")
    assert resposta.status_code == 422
    assert "é obrigatório" in resposta.content.decode()
    processo.refresh_from_db()
    assert processo.status == ProcessoSeletivo.Status.EM_ELABORACAO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_ato_do_processo_exige_permissao(client, seletor_ligado, sem_publicacao):
    processo = sem_publicacao
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:processo-detalhe", args=[processo.id])).content.decode()
    assert "Ativar Processo" not in corpo

    resposta = ato(client, processo, "ativar", "Tentativa")
    assert resposta.status_code == 403
    processo.refresh_from_db()
    assert processo.status == ProcessoSeletivo.Status.EM_ELABORACAO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_processo_de_outro_escopo_nao_e_alcancavel(client, seletor_ligado, cenario):
    processo, _ = cenario
    identificar(client, "marcia.gestora", GESTOR)
    sessao = client.session
    sessao["interface_identidade"] = {
        "subject": "marcia.gestora",
        "escopo": "outra-instituicao",
        "papeis": ["gestor"],
    }
    sessao.save()
    assert client.get(reverse("interface:processo-detalhe", args=[processo.id])).status_code == 404


@pytest.mark.django_db(transaction=True)
def test_criar_processo_com_o_primeiro_edital(client, seletor_ligado):
    """FR-025 da 003 — o requisito existia na 002 e o botão apontava para `#`."""
    identificar(client, "gestora", ["gestor"])

    resposta = client.post(
        reverse("interface:processo-criar"),
        {
            "codigo": "PS-2027-001",
            "titulo": "Processo Seletivo 2027",
            "numero": "01",
            "ano": "2027",
            "titulo_edital": "Primeiro Edital",
            "descricao": "Seleção de docentes",
            "chave_idempotencia": "ui-criacao-000000001",
        },
    )

    assert resposta.status_code == 302
    processo = ProcessoSeletivo.objects.get(institutional_code="PS-2027-001")
    assert resposta["Location"] == reverse("interface:processo-detalhe", args=[processo.id])
    edital = Edital.objects.get(processo=processo)
    assert (edital.number, edital.year, edital.status) == ("01", 2027, Edital.Status.EM_ELABORACAO)
    assert processo.created_by == "gestora"


@pytest.mark.django_db(transaction=True)
def test_reenviar_o_formulario_com_a_mesma_chave_nao_cria_dois_processos(client, seletor_ligado):
    identificar(client, "gestora", ["gestor"])
    dados = {
        "codigo": "PS-2027-002",
        "titulo": "Processo Seletivo 2027",
        "numero": "02",
        "ano": "2027",
        "titulo_edital": "Primeiro Edital",
        "chave_idempotencia": "ui-criacao-000000002",
    }

    client.post(reverse("interface:processo-criar"), dados)
    client.post(reverse("interface:processo-criar"), dados)

    assert ProcessoSeletivo.objects.filter(institutional_code="PS-2027-002").count() == 1


@pytest.mark.django_db(transaction=True)
def test_campo_obrigatorio_ausente_preserva_o_que_foi_digitado(client, seletor_ligado):
    identificar(client, "gestora", ["gestor"])

    resposta = client.post(
        reverse("interface:processo-criar"),
        {
            "codigo": "",
            "titulo": "Processo Seletivo 2027",
            "numero": "03",
            "ano": "2027",
            "titulo_edital": "Primeiro Edital",
            "chave_idempotencia": "ui-criacao-000000003",
        },
    )

    assert resposta.status_code == 422
    conteudo = resposta.content.decode()
    assert "Identificação institucional" in conteudo
    # O que já estava preenchido volta na tela: refazer tudo por um campo é retrabalho evitável.
    assert "Processo Seletivo 2027" in conteudo
    assert not ProcessoSeletivo.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_identificacao_repetida_e_recusada_pelo_dominio(client, seletor_ligado):
    identificar(client, "gestora", ["gestor"])
    dados = {
        "codigo": "PS-2027-004",
        "titulo": "Processo Seletivo 2027",
        "numero": "04",
        "ano": "2027",
        "titulo_edital": "Primeiro Edital",
    }
    client.post(
        reverse("interface:processo-criar"), {**dados, "chave_idempotencia": "ui-a-00000001"}
    )

    resposta = client.post(
        reverse("interface:processo-criar"),
        {**dados, "titulo": "Outro", "chave_idempotencia": "ui-b-00000002"},
    )

    assert resposta.status_code == 409
    assert "já utilizada" in resposta.content.decode()
    assert ProcessoSeletivo.objects.count() == 1


@pytest.mark.django_db(transaction=True)
def test_sem_permissao_a_criacao_e_recusada_pelo_command(client, seletor_ligado):
    """A tela não oferece o caminho, mas a URL é alcançável — quem recusa é o domínio."""
    identificar(client, "auditora", ["auditor"])

    resposta = client.post(
        reverse("interface:processo-criar"),
        {
            "codigo": "PS-2027-005",
            "titulo": "T",
            "numero": "05",
            "ano": "2027",
            "titulo_edital": "E",
            "chave_idempotencia": "ui-criacao-000000005",
        },
    )

    assert resposta.status_code == 403
    assert not ProcessoSeletivo.objects.exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    ("campo", "tamanho"),
    [("codigo", 101), ("titulo", 256), ("numero", 51), ("titulo_edital", 256)],
)
def test_campo_maior_que_a_coluna_e_recusado_na_borda(client, seletor_ligado, campo, tamanho):
    """SC-007 da 003: nenhuma requisição malformada de borda pode produzir 500.

    A tela de criação entrava direto no command, sem o serializer que a API usa, e o excesso
    chegava ao PostgreSQL como `StringDataRightTruncation` — 500 que o cliente não consegue usar
    e cuja mensagem não deveria sair da aplicação.
    """
    identificar(client, "gestora", ["gestor"])
    dados = {
        "codigo": "PS-2027-900",
        "titulo": "Processo Seletivo 2027",
        "numero": "90",
        "ano": "2027",
        "titulo_edital": "Primeiro Edital",
        "chave_idempotencia": "ui-borda-00000000001",
    }

    resposta = client.post(reverse("interface:processo-criar"), {**dados, campo: "X" * tamanho})

    corpo = resposta.content.decode()
    assert resposta.status_code == 422
    # A recusa deixou de ser uma frase agregada ("Encurte: A, B.") e passou a ser por campo, com
    # âncora no resumo e marca junto do controle (FR-033).
    assert "excede o máximo" in corpo
    assert f'href="#{campo}"' in corpo, "o resumo precisa levar até o campo"
    assert f'id="recusa-{campo}"' in corpo, "falta a marca junto do campo"
    assert not ProcessoSeletivo.objects.exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("ano", ["1999", "10000"])
def test_ano_fora_da_faixa_e_recusado_na_borda(client, seletor_ligado, ano):
    """`year` é PositiveSmallIntegerField: fora da faixa estoura na coluna, não na aplicação."""
    identificar(client, "gestora", ["gestor"])

    resposta = client.post(
        reverse("interface:processo-criar"),
        {
            "codigo": "PS-2027-901",
            "titulo": "T",
            "numero": "91",
            "ano": ano,
            "titulo_edital": "E",
            "chave_idempotencia": "ui-borda-00000000002",
        },
    )

    assert resposta.status_code == 422
    assert "entre 2000 e 9999" in resposta.content.decode()
    assert not ProcessoSeletivo.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_o_limite_vem_do_modelo_e_nao_de_um_numero_copiado(client, seletor_ligado):
    """Se a coluna crescer, o limite da tela cresce junto — não fica para trás em silêncio."""
    from processo_seletivo.interface.views import TEXTOS_DA_CRIACAO

    for _, _, modelo, campo in TEXTOS_DA_CRIACAO:
        assert modelo._meta.get_field(campo).max_length


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_publicar_o_primeiro_edital_abre_o_certame(cenario):
    """E2E-005: publicar o primeiro Edital **é** a abertura formal, e não precisa de ato à parte.

    Antes, o certame rodava inteiro em "Em elaboração" — Edital publicado, inscrições correndo —
    e no fim não podia ser encerrado sem uma ativação retroativa sobre fato consumado.
    """
    processo, _ = cenario

    assert processo.status == ProcessoSeletivo.Status.ATIVO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_ativacao_derivada_e_registrada_com_a_autoria_de_quem_publicou(cenario):
    """Derivada não é silenciosa.

    A trilha precisa distinguir a abertura declarada da que veio da publicação, e é o motivo que
    faz essa distinção.
    """
    from processo_seletivo.processos.models import AtoAdministrativo

    processo, _ = cenario

    ato_registrado = AtoAdministrativo.objects.get(
        aggregate_type="ProcessoSeletivo", aggregate_id=processo.pk, operation="ATIVAR"
    )
    assert ato_registrado.actor_subject == "publicador"
    assert "publicação do primeiro Edital" in ato_registrado.reason


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_processo_aberto_antes_nao_e_reativado_pela_publicacao(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """Quem já abriu o certame declaradamente não ganha um segundo ato de abertura."""
    from processo_seletivo.processos.models import AtoAdministrativo

    publish_original(api_client, manager_headers, process_payload)
    processo = ProcessoSeletivo.objects.get()

    assert processo.status == ProcessoSeletivo.Status.ATIVO
    assert (
        AtoAdministrativo.objects.filter(
            aggregate_type="ProcessoSeletivo", aggregate_id=processo.pk, operation="ATIVAR"
        ).count()
        == 1
    )
