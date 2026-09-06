"""As telas de publicar: onde a ação aparece, onde ela não aparece, e o que a prévia não faz.

Três coisas se prendem aqui, e a terceira é a menos óbvia:

1. a ação é oferecida a quem tem a capacidade e some para quem não tem (FR-069);
2. a prévia **não grava linha alguma** — não há rascunho de publicação a persistir (FR-035, D-008);
3. a **tela de cálculo do marco não oferece publicar**. Ali existe uma proposta calculada, e não um
   ato: ela não tem identidade a que apontar a ação, e oferecer o botão convidaria a divulgar
   aquilo que ainda não foi constituído (FR-002, FR-007, FR-036, SC-002).
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.divulgacao.models import (
    DocumentoDoResultado,
    PublicacaoResultado,
    SituacaoDivulgada,
)
from tests.fixtures.divulgacao import montar_ato_publicavel, montar_marco, pontuar
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    return montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=56,
        codigo="0756",
        pontuacoes=("90.0000", "70.0000", None),
        primeiro=701,
    )


def _tela_do_ato(cenario):
    return reverse(
        "interface:ato-de-ordenacao",
        args=[cenario["edital"].id, cenario["marco"], cenario["ato"].id],
    )


def _previa(cenario):
    return reverse(
        "interface:previa-de-publicacao",
        args=[cenario["edital"].id, cenario["marco"], cenario["ato"].id],
    )


def test_a_acao_aparece_para_quem_tem_a_capacidade(client, seletor_ligado, cenario):
    identificar(client, "paula.publicadora", ["publicador", "auditor"])
    corpo = client.get(_tela_do_ato(cenario)).content.decode()

    assert "Publicar resultado" in corpo
    assert _previa(cenario) in corpo


def test_a_acao_nao_aparece_para_quem_nao_tem_a_capacidade(client, seletor_ligado, cenario):
    """Quem emitiu o ato abre a tela dele e **não** recebe a ação de divulgá-lo (SC-014)."""
    identificar(client, "paulo.presidente", ["gestor"])
    corpo = client.get(_tela_do_ato(cenario)).content.decode()

    assert "Publicar resultado" not in corpo
    assert _previa(cenario) not in corpo


def test_a_tela_de_calculo_do_marco_nao_oferece_publicar(client, seletor_ligado, cenario):
    """SC-002: ali há proposta, e não ato — não existe identidade a que apontar a ação.

    Mesmo para quem tem as duas capacidades: o que falta não é autorização, é objeto.
    """
    identificar(client, "paula.publicadora", ["publicador", "gestor"])
    corpo = client.get(
        reverse("interface:ordenacao", args=[cenario["edital"].id, cenario["marco"]])
    ).content.decode()

    assert "Publicar resultado" not in corpo
    assert "/publicar" not in corpo


def test_a_previa_nao_grava_linha_alguma(client, seletor_ligado, cenario):
    """FR-035 e D-008: a prévia é leitura, e sair dela não deixa nada para trás."""
    identificar(client, "paula.publicadora", ["publicador"])

    resposta = client.get(_previa(cenario))

    assert resposta.status_code == 200
    assert not PublicacaoResultado.objects.exists()
    assert not SituacaoDivulgada.objects.exists()
    assert not DocumentoDoResultado.objects.exists()


def test_a_previa_mostra_o_que_sera_divulgado_e_as_consequencias(client, seletor_ligado, cenario):
    """FR-005 e FR-034: natureza, autoridade, a lista e o que acontece ao confirmar."""
    identificar(client, "paula.publicadora", ["publicador"])
    corpo = client.get(_previa(cenario)).content.decode()

    assert "prévia" in corpo and "nada foi gravado" in corpo
    assert "Resultado preliminar" in corpo and "Resultado definitivo" in corpo
    assert "Diretora do Cefor" in corpo
    assert "O que acontece ao confirmar" in corpo
    assert "não se despublica" in corpo
    assert "Candidata 701" in corpo, "a lista exata que será divulgada aparece na prévia"


def test_a_previa_nao_nomeia_quem_nao_recebeu_posicao_na_lista_publica(
    client, seletor_ligado, cenario
):
    """A prévia mostra **o que será divulgado**; a lista pública não nomeia quem não pontuou."""
    identificar(client, "paula.publicadora", ["publicador"])
    corpo = client.get(_previa(cenario)).content.decode()
    sem_posicao = cenario["inscricoes"][2]

    linhas = re.search(r"O que será divulgado(.*)$", corpo, re.DOTALL).group(1)
    assert sem_posicao.nome not in linhas
    assert "3 participantes considerados" in corpo, (
        "a contagem dos considerados é dita, para que a diferença fique visível"
    )


def test_a_previa_nao_traz_valor_de_desempate(client, seletor_ligado, cenario):
    """SC-015: nem data de nascimento, nem meses de experiência — a coluna não é lida (FR-020)."""
    identificar(client, "paula.publicadora", ["publicador"])
    corpo = client.get(_previa(cenario)).content.decode()

    assert "desempate" not in corpo.lower()
    assert "Critério que separou" not in corpo


def test_publicar_pela_tela_cria_a_publicacao_e_leva_ao_historico(client, seletor_ligado, cenario):
    identificar(client, "paula.publicadora", ["publicador"])
    corpo = client.get(_previa(cenario)).content.decode()
    confirmacao = re.search(r'name="confirmacao_da_previa" value="([^"]+)"', corpo).group(1)
    chave = re.search(r'name="chave_idempotencia" value="([^"]+)"', corpo).group(1)

    resposta = client.post(
        reverse(
            "interface:publicar-resultado",
            args=[cenario["edital"].id, cenario["marco"], cenario["ato"].id],
        ),
        {
            "natureza": "PRELIMINAR",
            "autoridade": "diretoria-cefor",
            "confirmacao_da_previa": confirmacao,
            "chave_idempotencia": chave,
        },
    )

    assert resposta.status_code == 302
    assert resposta.url == reverse(
        "interface:publicacoes-do-marco", args=[cenario["edital"].id, cenario["marco"]]
    )
    publicacao = PublicacaoResultado.objects.get()
    assert publicacao.publicado_por == "paula.publicadora"


def test_a_previa_de_ato_impedido_mostra_a_recusa_e_nao_oferece_o_botao(
    client, seletor_ligado, cenario, gestor
):
    """D-001: não existe publicar mediante confirmação adicional."""
    from tests.fixtures.divulgacao import emitir

    antigo = cenario["ato"]
    emitir(cenario, gestor, chave="emitir-0756-b", motivo="Resultado tardio.")
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(
        reverse(
            "interface:previa-de-publicacao",
            args=[cenario["edital"].id, cenario["marco"], antigo.id],
        )
    ).content.decode()

    assert "Este ato não pode ser divulgado" in corpo
    assert "foi sucedido" in corpo
    assert "ato sucessor" in corpo, "a recusa nomeia o caminho (FR-006)"
    assert "Publicar este resultado" not in corpo


def test_o_marco_sem_ato_emitido_nao_tem_tela_de_publicar(
    gestor, api_client, manager_headers, process_payload, client, seletor_ligado
):
    """FR-007: sem ato constituído não há o que divulgar, e não há endereço a alcançar."""
    cenario = montar_marco(
        gestor, api_client, manager_headers, process_payload, seed=57, codigo="0757"
    )
    pontuar(cenario, gestor, ["90.0000"], primeiro=801, sufixo="57")
    identificar(client, "paula.publicadora", ["publicador", "gestor"])

    corpo = client.get(
        reverse("interface:ordenacao", args=[cenario["edital"].id, cenario["marco"]])
    ).content.decode()

    assert "Publicar resultado" not in corpo


def test_os_tres_niveis_de_publicabilidade_sao_apresentados_ao_operador(
    client, seletor_ligado, cenario, gestor
):
    """FR-005 exige classificar **e apresentar os três**, e não só os dois que pedem atenção.

    O nível normal precisa de texto próprio: sem ele, "a verificação rodou e nada impede" e "a
    verificação não aconteceu" ficam indistinguíveis na tela — e a diferença entre as duas é
    exatamente o que a autoridade precisa saber antes de confirmar um ato irreversível.
    """
    from tests.fixtures.divulgacao import emitir, publicar_o_ato

    identificar(client, "paula.publicadora", ["publicador"])
    url = _previa(cenario)

    # 1. informação — o caso normal.
    informacao = client.get(url).content.decode()
    assert "nada impede esta divulgação" in informacao
    assert "Publicar este resultado" in informacao

    # 2. aviso — o marco já tem divulgação, e publicar de novo sucede.
    publicar_o_ato(cenario, chave="publicar-0756-niveis")
    aviso = client.get(url).content.decode()
    assert "já tem resultado divulgado" in aviso
    assert "nada impede esta divulgação" not in aviso, "os níveis não se acumulam"
    assert "Publicar este resultado" in aviso, "aviso informa; não impede"

    # 3. impedimento — o ato foi sucedido.
    antigo = cenario["ato"]
    emitir(cenario, gestor, chave="emitir-0756-niveis", motivo="Resultado tardio.")
    impedimento = client.get(
        reverse(
            "interface:previa-de-publicacao",
            args=[cenario["edital"].id, cenario["marco"], antigo.id],
        )
    ).content.decode()
    assert "Este ato não pode ser divulgado" in impedimento
    assert "nada impede esta divulgação" not in impedimento
    assert "Publicar este resultado" not in impedimento


def _confirmar(cenario, ato=None):
    return reverse(
        "interface:publicar-resultado",
        args=[cenario["edital"].id, cenario["marco"], (ato or cenario["ato"]).id],
    )


def _formulario(client, url, **campos):
    """Lê a prévia e devolve o formulário dela, com o que o teste quiser sobrescrever."""
    corpo = client.get(url).content.decode()
    return {
        "natureza": "PRELIMINAR",
        "autoridade": "diretoria-cefor",
        "confirmacao_da_previa": re.search(
            r'name="confirmacao_da_previa" value="([^"]+)"', corpo
        ).group(1),
        "chave_idempotencia": re.search(r'name="chave_idempotencia" value="([^"]+)"', corpo).group(
            1
        ),
        **campos,
    }


def test_a_recusa_do_post_devolve_o_status_declarado_no_contrato(
    client, seletor_ligado, cenario, gestor
):
    """Cada recusa volta com o seu status, e não com um 302 (contracts/publicacao.md §4).

    Responder "redirecione-se" a um 409 esconde de quem chamou — pessoa, script ou proxy — que o
    ato **não aconteceu**. E a tela recomposta traz a assinatura recalculada, que é justamente o
    que a autoridade precisa para reconfirmar depois de uma prévia obsoleta.
    """
    from tests.fixtures.divulgacao import emitir, publicar_o_ato

    identificar(client, "paula.publicadora", ["publicador"])

    # 409 — a projeção ou a cadeia mudaram entre a prévia e a confirmação.
    stale = client.post(
        _confirmar(cenario), _formulario(client, _previa(cenario), confirmacao_da_previa="0" * 64)
    )
    assert stale.status_code == 409
    assert "confira o que será divulgado" in stale.content.decode()
    assert not PublicacaoResultado.objects.exists(), "recusa não grava"

    # 422 — autoridade fora do catálogo.
    autoridade = client.post(
        _confirmar(cenario), _formulario(client, _previa(cenario), autoridade="prefeitura-alheia")
    )
    assert autoridade.status_code == 422

    # 409 — o ato já foi divulgado nesta natureza, por outra chave.
    publicar_o_ato(cenario, chave="publicar-0756-status")
    duplicada = client.post(
        _confirmar(cenario), _formulario(client, _previa(cenario), natureza="PRELIMINAR")
    )
    assert duplicada.status_code == 409
    assert PublicacaoResultado.objects.count() == 1

    # 409 — o ato foi sucedido; a recusa é da publicabilidade.
    antigo = cenario["ato"]
    emitir(cenario, gestor, chave="emitir-0756-status", motivo="Resultado tardio.")
    sucedido = client.post(
        _confirmar(cenario, ato=antigo),
        {
            "natureza": "DEFINITIVA",
            "autoridade": "diretoria-cefor",
            "confirmacao_da_previa": "0" * 64,
            "chave_idempotencia": "chave-0756-sucedido",
        },
    )
    assert sucedido.status_code == 409


def test_a_recusa_recompoe_a_assinatura_para_a_reconfirmacao(client, seletor_ligado, cenario):
    """Uma prévia obsoleta só é reconfirmável se a tela devolver a assinatura **de agora**."""
    identificar(client, "paula.publicadora", ["publicador"])

    recusada = client.post(
        _confirmar(cenario), _formulario(client, _previa(cenario), confirmacao_da_previa="0" * 64)
    )
    corpo = recusada.content.decode()
    assinatura = re.search(r'name="confirmacao_da_previa" value="([^"]+)"', corpo).group(1)
    chave = re.search(r'name="chave_idempotencia" value="([^"]+)"', corpo).group(1)

    assert assinatura != "0" * 64
    aceita = client.post(
        _confirmar(cenario),
        {
            "natureza": "PRELIMINAR",
            "autoridade": "diretoria-cefor",
            "confirmacao_da_previa": assinatura,
            "chave_idempotencia": chave,
        },
    )

    assert aceita.status_code == 302, "reconfirmar a partir da tela recusada precisa funcionar"
    assert PublicacaoResultado.objects.count() == 1
