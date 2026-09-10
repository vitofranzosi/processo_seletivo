"""O histórico normativo, visível para quem ainda não é candidato (024, FR-129 a FR-133).

**Por que existe.** Pela Constituição, Edital publicado só muda por Retificação — e o portal
mostrava o conteúdo vigente sem nenhum sinal de que ele tivesse mudado. Quem leu a página na semana
passada e voltou hoje lia outra coisa: sem aviso, sem data, sem motivo, e sem caminho para
descobrir o quê. Não é preferência de leitura; é o dano que a imutabilidade do ato existe para
evitar.

Nenhum dado precisou ser produzido. A Retificação já registra justificativa, instantes e o que
alterou; o que faltava era mostrar.
"""

import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.publicacoes.application import selectors
from processo_seletivo.publicacoes.models_retificacao import Retificacao
from tests.fixtures.edital import identificador
from tests.fixtures.publicacao import create_retification, retify
from tests.fixtures.selecao import publicar_selecao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

PERFIL = identificador(401, 0)


def mais_uma_vaga(edital, api_client, *, effective_at=None, suffix="a"):
    """Publica uma Retificação que amplia as vagas do primeiro Perfil, e devolve o ato."""
    return retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/profiles/id={PERFIL}/immediateVacancies",
                "operation": "REPLACE",
                "newValue": 3,
            }
        ],
        effective_at=effective_at,
        suffix=suffix,
    )


def corpo(client, edital):
    return client.get(reverse("portal:selecao", args=[edital.id])).content.decode()


def test_o_historico_mostra_cada_ato_com_data_justificativa_e_o_que_mudou(
    client, api_client, manager_headers, process_payload
):
    """FR-129, FR-130, FR-132 — e tudo isso sem sessão.

    Três coisas na mesma linha, porque é a leitura que resolve a dúvida de quem chega: **quando**
    mudou, **por quê** e **o quê**. Faltando qualquer uma, sobra a pergunta seguinte.
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)
    retificacao = mais_uma_vaga(edital, api_client)

    pagina = corpo(client, edital)

    assert "Edital e documentos" in pagina
    assert "Edital de abertura" in pagina
    assert "Retificação" in pagina
    assert retificacao.justification in pagina
    # O que mudou, em termos do Edital — e não em termos do sistema.
    assert "Perfil “Professor de Informática”" in pagina
    assert "Vagas imediatas" in pagina
    # O documento de **cada** ato continua alcançável, a partir da própria linha: dois atos, dois
    # links para `public-document`.
    assert pagina.count("/publicacoes/") == 3, "abertura, retificação e o botão do Edital no topo"


def test_o_enderecamento_estrutural_nunca_atravessa_para_a_tela(
    client, api_client, manager_headers, process_payload
):
    """D-005 — a prova mecânica, no lugar onde o vazamento aconteceria.

    A tela da gestão devolveu `/attachments/id=…` cru a quem homologava por meses. O tradutor
    existe para isso não se repetir numa página pública, e esta asserção é o que impede a regressão
    silenciosa: um campo novo copiado do caminho passaria despercebido.
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)
    mais_uma_vaga(edital, api_client)

    pagina = corpo(client, edital)
    historico = pagina[pagina.index('id="documentos-titulo"') :]

    assert "/profiles/" not in historico
    assert not re.search(r"id=[0-9a-f]{8}-", historico), "o seletor da gramática vazou para a tela"
    assert str(PERFIL) not in historico


def test_retificacao_com_vigencia_futura_e_ato_publicado_que_ainda_nao_vale(
    client, api_client, manager_headers, process_payload
):
    """FR-131, FR-131a — publicar e entrar em vigor são instantes distintos.

    É o caso que o `seed_demo` produz sozinho, e o mais fácil de errar: uma Retificação assinada
    hoje, vigente daqui a quinze dias, **já é ato publicado** e ainda **não** é o que vale. A tela
    tem de anunciar o ato e continuar mostrando o conteúdo de hoje.

    Fundir os dois faria a página exibir regra que ainda não vigora — e alguém se inscreveria sob
    ela.
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)
    daqui_a_quinze = timezone.now() + timedelta(days=15)
    mais_uma_vaga(edital, api_client, effective_at=daqui_a_quinze)

    pagina = corpo(client, edital)

    # O ato aparece, com a data em que passa a valer.
    assert "Retificação" in pagina
    assert f"vigente desde {daqui_a_quinze.strftime('%d/%m/%Y')}" in pagina
    # E o conteúdo continua sendo o de hoje: duas vagas, e não três.
    primeira_vaga = pagina[
        pagina.index("Professor de Informática") : pagina.index("Técnico de Lab")
    ]
    assert "<strong>2</strong>" in primeira_vaga
    assert "<strong>3</strong>" not in primeira_vaga


def test_o_conteudo_vigente_e_anunciado_como_tal_quando_houve_retificacao(
    client, api_client, manager_headers, process_payload
):
    """FR-131a — e o aviso fica onde a decisão acontece, colado ao Edital.

    É neste ponto que alguém está prestes a baixar um PDF, e é aqui que precisa saber que existe
    versão mais nova do que a que talvez já tenha lido.
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)
    mais_uma_vaga(edital, api_client)

    pagina = corpo(client, edital)

    assert "Este Edital foi retificado" in pagina
    assert "conteúdo vigente" in pagina
    # O aviso vem antes do histórico, e não depois: quem lê de cima para baixo encontra a notícia
    # antes de encontrar o detalhe dela.
    assert pagina.index("Este Edital foi retificado") < pagina.index('id="documentos-titulo"')


def test_edital_com_ato_unico_nao_desenha_secao_nem_frase_de_negacao(
    client, api_client, manager_headers, process_payload
):
    """FR-133, D-009 — com um ato só não há história a contar.

    O documento daquele ato já está no alto da página. Uma seção "Histórico" com uma linha só
    ensinaria que houve mudança onde não houve; "sem retificações" seria afirmação sobre o Edital
    feita pela tela.
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    pagina = corpo(client, edital)

    assert "Edital e documentos" not in pagina
    assert "Este Edital foi retificado" not in pagina
    assert "sem retificações" not in pagina.lower()
    assert "nenhuma retificação" not in pagina.lower()


def test_so_retificacao_publicada_entra_no_historico(
    client, api_client, manager_headers, process_payload
):
    """FR-129 — em elaboração, em revisão, homologada e cancelada não são atos publicados.

    Anunciá-las diria ao público que o Edital mudou antes de ele ter mudado — e a que está em
    elaboração pode nunca ser publicada.
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)
    create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": f"/profiles/id={PERFIL}/immediateVacancies",
                "operation": "REPLACE",
                "newValue": 9,
            }
        ],
        suffix="rascunho",
    )

    atos = selectors.atos_publicados(edital_id=edital.id)
    pagina = corpo(client, edital)

    assert Retificacao.objects.filter(edital=edital).count() == 1
    assert Retificacao.objects.get(edital=edital).status == Retificacao.Status.EM_ELABORACAO
    assert len(atos) == 1, "a Retificação em elaboração entrou no histórico"
    assert "Edital e documentos" not in pagina
