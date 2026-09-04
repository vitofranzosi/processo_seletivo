"""Retificar Documento Exigido pela tela (E2E-004, metade da edição).

**Por que existe.** A auditoria de 02/09/2026 registrou que a tela de Retificação alcançava
Perfis, Modalidades, Eventos, Etapas e Seções — e não `documentRequirements`. O domínio sempre
alcançou: `/documentRequirements` é coleção com chave declarada em `colecoes.py`. Era a interface
que parava na metade, e a consequência era concreta: documento exigido publicado errado só se
corrigia por chamada de API.

**O que este grupo tem de diferente de todos os outros.** `profileId` e `modalityId` não são
escalares digitados — referenciam entidades do próprio conteúdo, `null` neles significa "sem
restrição", e é deles que `documentos.aplicaveis` deriva quem precisa enviar o quê. Oferecê-los
como campo de texto faria um erro de digitação mudar em silêncio a obrigação documental de um
grupo de candidatos.

**O que fica de fora, e não por esquecimento.** Acrescentar e remover Documento Exigido:
acrescentar um obrigatório depois de publicado torna incompleta a inscrição de quem já enviou tudo
o que se pedia, e o que fazer com essas pessoas é decisão normativa.
"""

import pytest
from django.urls import reverse

from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.edital import complete_draft, identificador
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar
from tests.interface.test_retificar import campos

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

PERFIL = identificador(401, 0)
MODALIDADE = "00000000-0000-0000-0000-000000000404"
DOCUMENTO = "00000000-0000-0000-0000-000000000801"
CAMINHO_NOME = f"/documentRequirements/id={DOCUMENTO}/name"
CAMINHO_PERFIL = f"/documentRequirements/id={DOCUMENTO}/profileId"


def rascunho_com_documento():
    rascunho = complete_draft()
    rascunho["profiles"][0]["competitionModalities"] = [
        {"id": MODALIDADE, "code": "AC", "name": "Ampla Concorrência"}
    ]
    rascunho["documentRequirements"] = [
        {
            "id": DOCUMENTO,
            "key": "diploma",
            "name": "Diploma de graduação",
            "instructions": "Frente e verso.",
            "required": True,
            "order": 1,
        }
    ]
    return rascunho


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_documento()
    )


@pytest.fixture
def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


@pytest.fixture
def tela(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    return reverse("interface:retificar", args=[edital.id])


def test_o_documento_publicado_aparece_no_formulario(client, tela):
    corpo = client.get(tela).content.decode()

    assert "Documento 1 — Diploma de graduação" in corpo
    assert "Exigido apenas do Perfil" in corpo


def test_a_aplicabilidade_e_escolhida_entre_o_que_o_conteudo_publicou(client, tela):
    """A opção vazia é normativa: `null` significa "sem restrição", e não "não preenchido"."""
    corpo = client.get(tela).content.decode()

    assert "Sem restrição" in corpo
    assert "P1 — Perfil" in corpo
    assert "P1 — Perfil · AC — Ampla Concorrência" in corpo


def test_corrigir_o_nome_do_documento_produz_a_alteracao(client, tela, vigente):
    resposta = client.post(
        tela,
        {
            **campos(vigente, **{CAMINHO_NOME: "Diploma de graduação (frente e verso)"}),
            "justificativa": "Correção de redação",
            "confirmar": "1",
        },
    )

    assert resposta.status_code == 302
    alteracao = Retificacao.objects.get().alteracoes.get()
    assert alteracao.target_path == CAMINHO_NOME
    assert alteracao.new_value == "Diploma de graduação (frente e verso)"


def test_restringir_o_documento_a_um_perfil_produz_a_alteracao(client, tela, vigente):
    resposta = client.post(
        tela,
        {
            **campos(vigente, **{CAMINHO_PERFIL: PERFIL}),
            "justificativa": "O diploma só vale para o P1",
            "confirmar": "1",
        },
    )

    assert resposta.status_code == 302
    alteracao = Retificacao.objects.get().alteracoes.get()
    assert (alteracao.target_path, alteracao.new_value) == (CAMINHO_PERFIL, PERFIL)


def test_o_resumo_mostra_o_rotulo_e_nunca_o_identificador(client, tela, vigente):
    """O resumo é o que a pessoa confirma; conferir UUID de cor é o mesmo que não conferir."""
    resposta = client.post(
        tela,
        {
            **campos(vigente, **{CAMINHO_PERFIL: PERFIL}),
            "justificativa": "O diploma só vale para o P1",
        },
    )

    linha = next(
        item for item in resposta.context["resumo"] if item["rotulo"] == "Exigido apenas do Perfil"
    )
    assert (linha["antes"], linha["depois"]) == ("sem restrição", "P1 — Perfil")


def test_referencia_fabricada_e_recusada_porque_o_select_nao_e_fronteira(client, tela, vigente):
    """A verificação de publicação aceita a **forma** do UUID.

    O que ela não confere é se ele endereça alguma coisa: um identificador bem formado que não
    aponta para Perfil nenhum passaria, e o documento se aplicaria a ninguém, sem recusa.
    """
    forjado = "00000000-0000-0000-0000-000000000999"

    corpo = client.post(
        tela,
        {
            **campos(vigente, **{CAMINHO_PERFIL: forjado}),
            "justificativa": "Tentativa",
            "confirmar": "1",
        },
    ).content.decode()

    assert "não existe neste Edital" in corpo
    assert not Retificacao.objects.exists()


def test_o_documento_nao_e_removivel_pela_tela(client, tela):
    """Remover é decisão normativa sobre quem já se inscreveu, e não detalhe de interface."""
    from processo_seletivo.interface.retificacao import campos_editaveis

    versao = VersaoConsolidada.objects.latest("materialized_at")
    grupos = campos_editaveis(versao.content)
    documentos = [g for g in grupos if g["caminho"].startswith("/documentRequirements/")]

    assert documentos and not any(grupo["removivel"] for grupo in documentos)
