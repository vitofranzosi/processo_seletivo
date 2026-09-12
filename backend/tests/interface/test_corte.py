"""A tela do corte: ela calcula, mostra e **não grava** (014, FR-190, UX-024).

Abrir a tela não pode mudar quem participa da Etapa seguinte. É o mesmo desenho da tela da ordem, e
pela mesma razão — e é a única garantia que um teste de domínio não alcança, porque o defeito nasce
no GET.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.models import Corte
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def test_a_rota_do_corte_existe_e_pende_do_marco():
    """Pende do marco, como as da 015 e as do sorteio: o recorte vem em `?lista=`."""
    caminho = reverse(
        "interface:corte",
        args=["00000000-0000-4000-8000-000000000001", "00000000-0000-4000-8000-000000000002"],
    )

    assert caminho.endswith("/corte")
    assert "/marcos/" in caminho


def test_as_tres_rotas_do_corte_sao_distintas():
    edital = "00000000-0000-4000-8000-000000000001"
    marco = "00000000-0000-4000-8000-000000000002"

    ler = reverse("interface:corte", args=[edital, marco])
    emitir = reverse("interface:emitir-corte", args=[edital, marco])
    continuar = reverse("interface:continuar-corte", args=[edital, marco])

    assert len({ler, emitir, continuar}) == 3
    assert emitir.endswith("/corte/emitir")
    assert continuar.endswith("/corte/continuar")


def test_quem_nao_se_identificou_e_mandado_para_a_identificacao(client):
    edital = "00000000-0000-4000-8000-000000000001"
    marco = "00000000-0000-4000-8000-000000000002"

    resposta = client.get(reverse("interface:corte", args=[edital, marco]))

    assert resposta.status_code == 302
    assert reverse("interface:identificar") in resposta.headers["Location"]


def test_abrir_a_tela_nao_grava_corte_algum(client, seletor_ligado):
    """A garantia que o domínio não alcança: o defeito nasceria no GET (FR-190)."""
    identificar(client, "ana.presidente", ["elaborador"])
    edital = "00000000-0000-4000-8000-000000000001"
    marco = "00000000-0000-4000-8000-000000000002"

    client.get(reverse("interface:corte", args=[edital, marco]))

    assert Corte.objects.count() == 0


def test_a_emissao_so_aceita_post(client, seletor_ligado):
    """Ler não emite, e a separação é de método — não de disciplina de quem chama (FR-221)."""
    identificar(client, "ana.presidente", ["elaborador"])
    edital = "00000000-0000-4000-8000-000000000001"
    marco = "00000000-0000-4000-8000-000000000002"

    resposta = client.get(reverse("interface:emitir-corte", args=[edital, marco]))

    assert resposta.status_code == 405


# --- os três do terceiro review, na porta da interface -----------------------------------------


def test_a_tela_entrega_a_chave_de_idempotencia_em_campo_oculto(cliente_no_corte):
    """Gerada no POST, cada clique virava pedido novo — e duplo clique, duas faixas."""
    client, edital, marco = cliente_no_corte

    corpo = client.get(reverse("interface:corte", args=[edital.id, marco])).content.decode()

    assert 'name="chave_idempotencia"' in corpo
    assert corpo.count('name="chave_idempotencia"') >= 1, "a emissão a carrega"


def test_a_continuacao_repetida_nao_emite_duas_faixas(cliente_no_corte):
    """**A continuação**, e não a emissão inicial — era ela o fluxo vulnerável.

    Na emissão, a confirmação do cálculo já recusaria o segundo POST sozinha, e o teste passaria
    mesmo sem idempotência nenhuma. A continuação não tem confirmação intermediária: o que segura o
    segundo clique é a chave, e ela precisa ser **a mesma** nas duas tentativas.
    """
    from processo_seletivo.classificacao.models import Corte

    client, edital, marco = cliente_no_corte
    corpo = client.get(reverse("interface:corte", args=[edital.id, marco])).content.decode()
    confirmacao = re.search(r'name="confirmacao_do_calculo" value="([^"]+)"', corpo).group(1)
    chave_da_emissao = re.search(r'name="chave_idempotencia" value="([^"]+)"', corpo).group(1)
    client.post(
        reverse("interface:emitir-corte", args=[edital.id, marco]),
        {"chave_idempotencia": chave_da_emissao, "confirmacao_do_calculo": confirmacao},
    )
    assert Corte.objects.count() == 1, "o cenário começa com a faixa inicial emitida"

    # A tela recarregada traz a chave da **próxima** tentativa, que é o que o navegador reenviaria.
    corpo = client.get(reverse("interface:corte", args=[edital.id, marco])).content.decode()
    formulario_da_continuacao = corpo[corpo.index("/corte/continuar") :]
    assert 'name="chave_idempotencia"' in formulario_da_continuacao, (
        "é o formulário da continuação que precisa dela: sem confirmação intermediária, é a chave "
        "que segura o segundo clique"
    )
    chave = re.search(r'name="chave_idempotencia" value="([^"]+)"', corpo).group(1)
    continuar = {"chave_idempotencia": chave, "quantidade": "1", "motivo": "um indeferimento"}

    client.post(reverse("interface:continuar-corte", args=[edital.id, marco]), continuar)
    client.post(reverse("interface:continuar-corte", args=[edital.id, marco]), continuar)

    assert Corte.objects.count() == 2, "duplo clique na continuação não emite duas faixas"


@pytest.mark.parametrize("lixo", ["abc", "1", "%%"])
def test_lista_que_nao_e_identidade_responde_404_e_nao_500(client, seletor_ligado, lixo):
    """`?lista=abc` chegava ao ORM como filtro de UUID e virava erro de servidor."""
    identificar(client, "ana.presidente", ["elaborador"])
    edital = "00000000-0000-4000-8000-000000000001"
    marco = "00000000-0000-4000-8000-000000000002"

    resposta = client.get(reverse("interface:corte", args=[edital, marco]), {"lista": lixo})

    assert resposta.status_code == 404


def test_quantidade_que_nao_e_numero_nao_derruba_a_rota(cliente_no_corte):
    """Texto no campo numérico é erro de quem preenche, e vira recusa de domínio — não 500.

    O percurso é o da rota inteira, e não o da função de conversão: era ali que o `ValueError`
    escapava, antes de o comando ter chance de recusar.
    """
    client, edital, marco = cliente_no_corte

    resposta = client.post(
        reverse("interface:continuar-corte", args=[edital.id, marco]),
        {"quantidade": "abc", "motivo": "tentativa"},
    )

    assert resposta.status_code == 302, "volta à tela pelo POST-redirect-GET, e não explode"


@pytest.fixture
def cliente_no_corte(client, seletor_ligado, gestor, api_client, manager_headers, process_payload):
    """Um Edital real com ordem emitida e corte por emitir, pela porta da interface."""
    from tests.fixtures.corte import MARCO, montar_cenario_do_corte, regra

    # **Com continuação admitida**: é ela o fluxo sem confirmação intermediária, e portanto o que
    # o teste de idempotência precisa exercitar.
    edital, _, _ = montar_cenario_do_corte(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        cut=regra(continuation="ALLOWED"),
        prefixo="corte-014-ui",
    )
    # A base de gestão é o que a rota exige para emitir — ler tem porta mais larga.
    identificar(client, "carlos", ["gestor"])
    return client, edital, MARCO


# --- T085 e T091, encontradas abertas pelo percurso E2E ----------------------------------------


def _emitir_pela_tela(client, edital, marco):
    corpo = client.get(reverse("interface:corte", args=[edital.id, marco])).content.decode()
    confirmacao = re.search(r'name="confirmacao_do_calculo" value="([^"]+)"', corpo).group(1)
    chave = re.search(r'name="chave_idempotencia" value="([^"]+)"', corpo).group(1)
    return client.post(
        reverse("interface:emitir-corte", args=[edital.id, marco]),
        {"confirmacao_do_calculo": confirmacao, "chave_idempotencia": chave},
    )


def test_a_tela_do_marco_mostra_a_faixa_obsoleta_com_a_causa(cliente_no_corte):
    """A `UX-027` pede que a obsolescência seja **vista ao abrir o marco** (T085).

    O percurso E2E sucedeu a ordem e abriu o marco: a tela não dizia nada. Quem sucede a ordem
    descobriria que a faixa ficou para trás só ao tentar conduzir a Etapa governada — a recusa
    chegaria no meio do trabalho, e não na tela que existe para conferir o marco.
    """
    from processo_seletivo.classificacao.application.calculo import calcular_ordem
    from processo_seletivo.classificacao.application.emissao import (
        assinatura_da_proposta,
        emitir_ordem,
    )
    from processo_seletivo.classificacao.models import AtoDeOrdenacao
    from tests.fixtures.edital import PROFILE_ID

    client, edital, marco = cliente_no_corte
    _emitir_pela_tela(client, edital, marco)
    vigente = AtoDeOrdenacao.objects.filter(
        edital=edital, marco_id=marco, lista_id=None, sucessores__isnull=True
    ).first()
    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=marco)
    emitir_ordem(
        actor=_ator_de_gestao(edital),
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=marco,
        idempotency_key="corte-014-ui-sucessor",
        correlation_id="teste-014",
        confirmacao_do_calculo=assinatura_da_proposta(proposta, ato_vigente=vigente),
        motivo="Reemissão após conferência.",
    )

    corpo = client.get(reverse("interface:ordenacao", args=[edital.id, marco])).content.decode()

    assert "A faixa emitida está obsoleta" in corpo
    assert "A ordem que este corte leu foi sucedida" in corpo


def test_o_corte_historico_e_lido_pelos_nomes_da_versao_que_ele_congelou(cliente_no_corte):
    """A rota `cortes/<id>` da `UX-024`, com a proveniência inteira (T091).

    **Pelos nomes congelados**: renomear o marco hoje não pode mudar como um corte antigo é lido —
    a mesma regra que a `015` aplica ao ato de ordenação. A reprodução aparece na mesma tela porque
    é ali que ela serve: registrar o que foi usado e chegar de novo ao mesmo resultado são coisas
    distintas, e a Constituição pede a segunda (`FR-199`).
    """
    client, edital, marco = cliente_no_corte
    _emitir_pela_tela(client, edital, marco)
    corte = Corte.objects.get(edital=edital, marco_id=marco)

    corpo = client.get(
        reverse("interface:corte-historico", args=[edital.id, corte.id])
    ).content.decode()

    assert "Proveniência" in corpo
    assert corte.emitido_por in corpo, "o ator da emissão (FR-222, SC-070)"
    assert "A regra que o governou" in corpo
    assert "A faixa reproduz" in corpo, "a reprodução a partir do universo (FR-199)"
    assert str(corte.ato_id) in corpo or "Ato de" in corpo, "a ordem citada"


def _ator_de_gestao(edital):
    from processo_seletivo.seguranca.domain import Actor

    return Actor(
        subject="carlos",
        institution_scope=edital.processo.institution_scope,
        permissions=frozenset({"classificacao:emitir", "comissao:gerir"}),
    )


def test_a_retificacao_alcanca_o_desfecho_do_empate_com_as_duas_opcoes(cliente_no_corte):
    """O passo que o percurso E2E não conseguiu dar pela tela (E2E14-005).

    O Percurso 2 do quickstart manda retificar o marco para *admite excedente* quando o empate
    atravessa a faixa — e a Retificação oferecia `targetCount` e `surplusCount` e mais nada do
    corte. A espécie do alvo, a Etapa governada e a continuação ficam de fora por decisão
    registrada; o desfecho não tinha razão para ficar: são dois valores fechados, e `REFERENCIA`
    os oferece conferindo a escolha contra a lista.
    """
    from processo_seletivo.interface.retificacao import campos_editaveis
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    _, edital, _ = cliente_no_corte
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("valid_from")

    campos = [campo for grupo in campos_editaveis(vigente.content) for campo in grupo["campos"]]
    desfecho = next(campo for campo in campos if campo["caminho"].endswith("/cutRule/tieOutcome"))

    assert {identificador for identificador, _ in desfecho["opcoes"]} == {
        "ADMITS_SURPLUS",
        "STRICT",
    }
    assert desfecho["rotulo"] == "Empate na última posição"


def test_a_tela_do_corte_identifica_quem_progride_pelo_protocolo(cliente_no_corte):
    """A coluna imprimia UUID, e a casa inteira escreve `protocolo — nome` ali (E2E14-006).

    Catorze linhas de identificador interno, e conferir quem progrediu exigia traduzi-las por
    fora. A `UX-025` proíbe nomear por identificador interno, e a tela do ato de ordenação já
    resolvia a mesma coluna do mesmo jeito.
    """
    from processo_seletivo.inscricoes.models import Inscricao

    client, edital, marco = cliente_no_corte
    protocolos = set(Inscricao.objects.filter(edital=edital).values_list("protocolo", flat=True))

    corpo = client.get(reverse("interface:corte", args=[edital.id, marco])).content.decode()

    assert protocolos, "o cenário grava protocolo"
    assert any(protocolo in corpo for protocolo in protocolos)
