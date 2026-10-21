"""A tela da vaga acrescida: o formulário na ocupação, a conferência, o ato e o desfazimento (097).

**O que só a tela prova é o que aparece antes do ato** (`FR-2456`, `UX-221`, `UX-222`): quem a
ordem alcança, pelo nome; quantas vagas ficam sem pessoa; e que abrir a conferência não grava nada.
"""

from pathlib import Path

import pytest
from django.urls import reverse

from processo_seletivo.ocupacao.models import AcrescimoDeVagas
from tests.fixtures.convocacao import convocar, habilitar_na_etapa_governada
from tests.fixtures.corte import MARCO
from tests.fixtures.ocupacao import montar_cenario_da_ocupacao
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

ORIGEM = "Edital Multicampi nº 20/2026, Campus Vitória"
FUNDAMENTO = "Vaga não preenchida no Edital regular"


@pytest.fixture
def reserva(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """O Perfil do TMD: 0 vagas, cadastro de reserva, faixa de dois e três habilitadas."""
    edital, _, inscricoes = montar_cenario_da_ocupacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="interface-097",
        geral=0,
        reserva="UNLIMITED",
    )
    habilitar_na_etapa_governada(edital, inscricoes[:3])
    return edital, inscricoes


def abrir(client, edital):
    return client.get(reverse("interface:ocupacao", args=[edital.id, MARCO])).content.decode()


def conferir(client, edital, quantidade=1, **campos):
    dados = {
        "lista": "",
        "chave": "tela-097",
        "quantidade": quantidade,
        "origem": ORIGEM,
        "fundamento": FUNDAMENTO,
        **campos,
    }
    return client.post(reverse("interface:acrescentar-vagas", args=[edital.id, MARCO]), dados)


def assinatura_de(pagina):
    marcador = 'name="leitura" value="'
    inicio = pagina.index(marcador) + len(marcador)
    return pagina[inicio : pagina.index('"', inicio)]


def confirmar(client, edital, pagina, quantidade=1):
    return conferir(client, edital, quantidade, confirmar="1", leitura=assinatura_de(pagina))


def test_quem_apura_ve_o_formulario_e_quem_audita_nao(client, seletor_ligado, reserva):
    """`FR-2465`: a autoridade é a de quem apura."""
    edital, _ = reserva

    identificar(client, "carlos", ["gestor"])
    da_gestao = abrir(client, edital)
    identificar(client, "aud", ["auditor"])
    da_auditoria = abrir(client, edital)

    assert "Conferir o acréscimo" in da_gestao
    assert "Não escreva o nome de pessoas do outro Edital" in da_gestao, "`FR-2467`"
    assert "Conferir o acréscimo" not in da_auditoria


def test_a_conferencia_diz_quem_a_ordem_alcanca_e_nao_grava_nada(client, seletor_ligado, reserva):
    """`FR-2456`, `UX-221`, `UX-222`."""
    edital, inscricoes = reserva
    identificar(client, "carlos", ["gestor"])

    pagina = conferir(client, edital).content.decode()

    assert "Conferir o acréscimo de 1 vaga" in pagina
    assert inscricoes[0].nome in pagina
    assert "na 1ª posição da ordem" in pagina
    assert "Efetivas depois deste ato" in pagina
    assert "A apuração seguinte será emitida por este ato, em seu nome" in pagina
    assert "Acrescentar 1 vaga" in pagina
    assert AcrescimoDeVagas.objects.count() == 0


def test_com_mais_vagas_do_que_a_faixa_a_conferencia_diz_quantas_ficam_sem_pessoa(
    client, seletor_ligado, reserva
):
    edital, _ = reserva
    identificar(client, "carlos", ["gestor"])

    pagina = conferir(client, edital, 3).content.decode()

    assert "3 vagas; a ordem publicada alcança só 2 pessoas" in pagina
    assert "Acrescentar 3 vagas" in pagina


def test_confirmar_grava_e_volta_a_ocupacao_com_o_numero_e_a_lista(client, seletor_ligado, reserva):
    """`UX-220`: publicadas, acrescidas e efetivas, e a lista dos atos com origem e autor."""
    edital, _ = reserva
    identificar(client, "carlos", ["gestor"])
    pagina = conferir(client, edital).content.decode()

    resposta = confirmar(client, edital, pagina)
    depois = client.get(resposta["Location"]).content.decode()

    assert resposta.status_code == 302
    assert AcrescimoDeVagas.objects.count() == 1
    assert "Vaga acrescida: 1 vaga." in depois
    assert "A apuração seguinte foi emitida por este ato, em seu nome." in depois
    assert "Acrescidas depois da publicação" in depois
    assert f"Origem: {ORIGEM}." in depois
    assert "Registrado por carlos." in depois


def test_a_recusa_volta_a_ocupacao_com_a_frase_do_dominio(client, seletor_ligado, reserva):
    edital, _ = reserva
    identificar(client, "carlos", ["gestor"])

    resposta = conferir(client, edital, origem="")
    depois = client.get(resposta["Location"]).content.decode()

    assert "Não foi possível acrescentar a vaga:" in depois
    assert "Diga de onde a vaga veio" in depois
    assert AcrescimoDeVagas.objects.count() == 0


def test_a_leitura_mudada_volta_a_conferencia_recalculada(client, seletor_ligado, reserva, gestor):
    """`FR-2457`: confirmar sobre a prévia que outro acréscimo mudou devolve a conferência nova."""
    edital, _ = reserva
    identificar(client, "carlos", ["gestor"])
    velha = conferir(client, edital).content.decode()
    nova = conferir(client, edital, chave="tela-097-outro").content.decode()
    confirmar(client, edital, nova)  # outro acréscimo entra antes da confirmação da velha

    resposta = conferir(
        client, edital, confirmar="1", leitura=assinatura_de(velha), chave="tela-097-velha"
    )
    pagina = resposta.content.decode()

    assert resposta.status_code == 200
    assert "mudaram desde que a conferência foi aberta" in pagina
    assert "Acrescidas até agora" in pagina
    assert AcrescimoDeVagas.objects.count() == 1


def test_perfil_sem_cadastro_de_reserva_nao_oferece_o_acrescimo(client, seletor_ligado, cenario):
    """`FR-2463`: no Perfil sem reserva, o acréscimo não é caminho de nada, e não aparece."""
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital)

    assert "Conferir o acréscimo" not in pagina
    assert "Acrescidas depois da publicação" not in pagina


def test_nada_fora_da_gestao_le_a_vaga_acrescida():
    """`FR-2467`, `FR-2468`: origem, fundamento e quantidade acrescida ficam na gestão.

    Prova de import, como a da `016`: o que o portal, a publicação e a divulgação não leem, eles não
    mostram. A página pública continua dizendo as vagas que o Edital publicou.
    """
    raiz = Path(__file__).resolve().parents[2] / "processo_seletivo"
    leitores = [
        caminho.relative_to(raiz).as_posix()
        for pasta in ("portal", "publicacoes", "divulgacao", "duvidas", "avisos")
        for caminho in (raiz / pasta).rglob("*.py")
        if "AcrescimoDeVagas" in caminho.read_text(encoding="utf-8")
        or "acrescimos_do_recorte" in caminho.read_text(encoding="utf-8")
    ]

    assert leitores == []


# --- O desfazimento (US3) ----------------------------------------------------------------------


def acrescentar_pela_tela(client, edital, quantidade=1):
    pagina = conferir(client, edital, quantidade, chave=f"tela-097-{quantidade}").content.decode()
    conferir(
        client,
        edital,
        quantidade,
        chave=f"tela-097-{quantidade}",
        confirmar="1",
        leitura=assinatura_de(pagina),
    )
    return AcrescimoDeVagas.objects.latest("registrado_em")


def desfazer(client, edital, acrescimo, quantidade=1, **campos):
    dados = {"acrescimo": acrescimo.id, "quantidade": quantidade, "chave": "tela-097-d", **campos}
    return client.post(reverse("interface:desfazer-acrescimo", args=[edital.id, MARCO]), dados)


def test_o_desfazimento_tem_porta_na_lista_e_conferencia_com_motivo(
    client, seletor_ligado, reserva
):
    """`FR-2460`: o acréscimo com saldo tem a porta, e a conferência pede o motivo."""
    edital, _ = reserva
    identificar(client, "carlos", ["gestor"])
    acrescimo = acrescentar_pela_tela(client, edital)

    assert "Conferir o desfazimento" in abrir(client, edital)
    pagina = desfazer(client, edital, acrescimo).content.decode()

    assert "Desfazer 1 vaga do acréscimo de" in pagina
    assert "Motivo do desfazimento" in pagina
    assert AcrescimoDeVagas.objects.count() == 1, "conferir não grava"

    resposta = desfazer(
        client,
        edital,
        acrescimo,
        confirmar="1",
        motivo="Matrícula efetivada no Edital regular",
        leitura=assinatura_de(pagina),
    )
    depois = client.get(resposta["Location"]).content.decode()

    assert "Vaga acrescida desfeita: 1 vaga." in depois
    assert "Motivo: Matrícula efetivada no Edital regular." in depois
    assert AcrescimoDeVagas.objects.count() == 2
    assert "Conferir o desfazimento" not in depois, "o acréscimo não tem mais saldo"


def test_desfazer_a_vaga_de_quem_foi_chamado_e_recusado_com_a_frase(
    client, seletor_ligado, reserva, gestor
):
    """`FR-2462`, pela trava real: a convocação diz quem foi chamado."""
    edital, inscricoes = reserva
    identificar(client, "carlos", ["gestor"])
    acrescimo = acrescentar_pela_tela(client, edital)
    convocar(edital, gestor, inscricoes[0], idempotency_key="097-tela-convoca")

    resposta = desfazer(client, edital, acrescimo)
    depois = client.get(resposta["Location"]).content.decode()

    assert "Não foi possível desfazer a vaga acrescida:" in depois
    assert "já chamada(s) para as vagas deste recorte" in depois
    assert AcrescimoDeVagas.objects.count() == 1
