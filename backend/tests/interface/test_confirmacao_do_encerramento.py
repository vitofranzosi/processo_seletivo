"""A confirmação de encerrar e de cancelar diz o que impede e o que continua (113, FR-3534 a 3543).

A tela é lida como a pessoa a lê: impedimento antes das consequências, sem "Confirmar"; caminho só a
quem a tela de destino aceita; advertências à parte; e nenhuma pessoa nomeada.
"""

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.interface import encerramento
from processo_seletivo.interface.relatorio_do_edital import fatos_do_edital, texto_da_pendencia
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import Retificacao
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador
from tests.integration.portal.test_desfecho_publico import publicar as publicar_com_periodo
from tests.integration.publicacoes.test_retificacao_de_edital_encerrado import levar_a
from tests.interface.test_auditoria_passagem_da_retificacao import sessao
from tests.unit.processos.test_pendencias_do_edital import criar

pytestmark = [pytest.mark.django_db(transaction=True)]

CONFIRMAR = "Confirmar: Encerrar"


def tela(cliente, edital, acao="encerrar"):
    resposta = cliente.get(reverse("interface:ato", args=[edital.id, acao]))
    assert resposta.status_code == 200
    return resposta.content.decode()


def bloco(corpo, titulo):
    inicio = corpo.index(titulo)
    return corpo[inicio : corpo.index("</div>", inicio)]


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    return cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=161, codigo="1161"
    )


# ---------------------------------------------------------------------------------------------
# Impedimentos (FR-3537, FR-3538, FR-3540, FR-3543; SC-1071)
# ---------------------------------------------------------------------------------------------


def test_recurso_aguardando_impede_e_o_gestor_ve_a_contagem_e_a_quem_pedir(peca):
    corpo = tela(sessao("gabi.gestora", ["gestor"]), peca["cenario"]["edital"])

    impedimentos = bloco(corpo, "Antes de encerrar, resolva 1 pendência.")
    assert "1 recurso aguarda decisão." in impedimentos
    assert "Peça a quem julga recursos." in impedimentos
    assert "Ir aos recursos" not in impedimentos
    assert CONFIRMAR not in corpo
    assert corpo.index("Antes de encerrar") < corpo.index("Este ato não pode ser desfeito")


def test_quem_julga_recebe_o_caminho_ate_os_recursos(peca):
    edital = peca["cenario"]["edital"]
    corpo = tela(sessao("gabi.gestora", ["gestor", "julgador"]), edital)

    assert f'href="{reverse("interface:recursos", args=[edital.id])}"' in corpo
    assert "Peça a quem julga recursos" not in corpo


def test_nenhum_dado_pessoal_na_confirmacao(peca):
    corpo = tela(sessao("gabi.gestora", ["gestor"]), peca["cenario"]["edital"])
    for inscricao in peca["cenario"]["inscricoes"]:
        assert inscricao.nome not in corpo
        assert inscricao.cpf_normalizado not in corpo
    assert peca["recurso"].protocolo not in corpo


def test_periodo_em_curso_oferece_retificar_so_a_quem_retifica(
    api_client, manager_headers, process_payload
):
    edital = publicar_com_periodo(api_client, manager_headers, process_payload)

    do_gestor = tela(sessao("gabi.gestora", ["gestor"]), edital)
    assert "O período de inscrições vai até" in do_gestor
    assert "Peça a quem elabora Retificações." in do_gestor
    assert CONFIRMAR not in do_gestor

    da_elaboradora = tela(sessao("gabi.gestora", ["gestor", "elaborador"]), edital)
    assert f'href="{reverse("interface:retificar", args=[edital.id])}"' in da_elaboradora


def test_o_post_com_impedimento_devolve_409_com_a_lista_de_agora(peca):
    edital = peca["cenario"]["edital"]
    cliente = sessao("gabi.gestora", ["gestor"])
    url = reverse("interface:ato", args=[edital.id, "encerrar"])
    chave = cliente.get(url).context["chave_idempotencia"]

    resposta = cliente.post(url, {"motivo": "Etapas concluídas", "chave_idempotencia": chave})

    assert resposta.status_code == 409
    corpo = resposta.content.decode()
    assert "Não foi possível concluir" in corpo
    assert "1 recurso aguarda decisão." in bloco(corpo, "Antes de encerrar, resolva")
    edital.refresh_from_db()
    assert edital.status == Edital.Status.PUBLICADO


# ---------------------------------------------------------------------------------------------
# Advertências e consequências (FR-3534, FR-3539, FR-3541, FR-3542)
# ---------------------------------------------------------------------------------------------


def test_sem_impedimento_as_advertencias_vem_a_parte_e_o_confirmar_aparece(
    api_client, manager_headers, process_payload
):
    from tests.fixtures.publicacao import publish_original

    edital = publish_original(api_client, manager_headers, process_payload)
    levar_a(criar(api_client, edital), Retificacao.Status.EM_REVISAO)

    corpo = tela(sessao("gabi.gestora", ["gestor"]), edital)

    continuam = bloco(corpo, "Continuam depois do encerramento")
    assert "em revisão, não poderá mais prosseguir." in continuam
    assert "Abrir a Retificação" in continuam
    assert "Antes de encerrar" not in corpo
    assert CONFIRMAR in corpo


def test_as_consequencias_nao_afirmam_conclusao(api_client, manager_headers, process_payload):
    from tests.fixtures.publicacao import publish_original

    edital = publish_original(api_client, manager_headers, process_payload)
    corpo = tela(sessao("gabi.gestora", ["gestor"]), edital)

    assert "conclusão regular" not in corpo
    assert "concluída" not in corpo
    assert "deixa de receber inscrição e Retificação" in corpo
    assert "consta do Relatório do Edital" in corpo


def test_sem_nada_a_dizer_a_frase_e_a_do_gps(api_client, manager_headers, process_payload):
    """FR-3541: sem período designado, sem inscrição, sem resultado e sem Retificação."""
    from tests.fixtures.publicacao import publish_original

    edital = publish_original(api_client, manager_headers, process_payload)

    corpo = tela(sessao("gabi.gestora", ["gestor"]), edital)

    assert "Nenhuma pendência registrada no GPS impede o encerramento." in corpo
    assert "Continuam depois do encerramento" not in corpo
    assert CONFIRMAR in corpo


# ---------------------------------------------------------------------------------------------
# A regra da 099 (FR-3535, SC-1069)
# ---------------------------------------------------------------------------------------------


def test_toda_providencia_do_relatorio_depois_do_ato_foi_dita_antes(peca):
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.INDEFERIDO,
        motivacao="Sem razão.",
        idempotency_key="indeferir-113-161b",
    )
    edital = peca["cenario"]["edital"]
    cliente = sessao("gabi.gestora", ["gestor"])
    url = reverse("interface:ato", args=[edital.id, "encerrar"])
    antes = cliente.get(url)
    corpo = antes.content.decode()
    resposta = cliente.post(
        url,
        {"motivo": "Etapas concluídas", "chave_idempotencia": antes.context["chave_idempotencia"]},
    )
    assert resposta.status_code == 302

    depois = fatos_do_edital(Edital.objects.get(pk=edital.id), agora=timezone.now()).pendencias
    conferidas = [p for p in depois if p.tipo in encerramento.DA_099]
    assert conferidas, "o cenário precisa de ao menos uma providência para a prova não ser vazia"
    for pendencia in conferidas:
        if True:
            texto = texto_da_pendencia(pendencia)
            if pendencia.tipo.startswith("CONVOCACAO"):
                texto = texto.split(" ", 1)[1].split(",")[0]
            assert texto[1:] in corpo, texto


# ---------------------------------------------------------------------------------------------
# Cancelar (FR-3536)
# ---------------------------------------------------------------------------------------------


def test_cancelar_lista_o_que_sera_atingido_e_deixa_confirmar(
    api_client, manager_headers, process_payload
):
    edital = publicar_com_periodo(api_client, manager_headers, process_payload)
    levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)

    corpo = tela(sessao("gabi.gestora", ["gestor"]), edital, acao="cancelar")

    atingidos = bloco(corpo, "Serão atingidos pelo cancelamento")
    assert "O período de inscrições iria até" in atingidos
    assert "o cancelamento põe fim ao recebimento agora" in atingidos
    assert "foi homologada e não poderá ser publicada" in atingidos
    assert "cancele o Edital" not in atingidos and "Publique-a" not in atingidos
    assert "Antes de encerrar" not in corpo
    assert "Confirmar: Cancelar" in corpo
