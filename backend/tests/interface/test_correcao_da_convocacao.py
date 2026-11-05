"""A correção da convocação pelo cartão da chamada, na tela da condução (120).

**O que só a tela prova** é o que aparece antes do ato e o que volta depois dele: a ação no cartão
certo, a prévia com a origem de cada valor, a limitação quando o recorte não admite correção, o
resultado com os dois vencimentos e a recusa no cartão com o que foi digitado (`FR-3837` a
`FR-3850`). As regras do comando estão em `integration/convocacao/test_correcao_da_convocacao.py`.
"""

import re
import uuid
from datetime import timedelta
from unittest import mock

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import Convocacao
from tests.fixtures.convocacao import apurar, convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

TRES_DIAS = timedelta(days=3)
MOTIVO = "A mensagem saiu com dois dias de atraso; o prazo é dado de novo."
ACAO = "Corrigir esta convocação"


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    mail.outbox.clear()
    return montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="interface-120"
    )


def campo(instante):
    return timezone.localtime(instante).strftime("%Y-%m-%dT%H:%M")


def fila(edital):
    from processo_seletivo.convocacao.application import selectors

    return selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]


def chamar(edital, gestor, *, chave="raiz", vencimento="padrao", comunicar=True):
    from tests.fixtures.documentos_da_convocacao import comunicar as emitir

    if vencimento == "padrao":
        vencimento = timezone.now() + TRES_DIAS
    raiz = Convocacao.objects.get(
        id=convocar(edital, gestor, fila(edital)[0], idempotency_key=chave, vencimento=vencimento)[
            "id"
        ]
    )
    if comunicar:
        emitir(edital, gestor, raiz, chave=f"comunicar-{chave}")
    return raiz


def abrir(client, edital):
    return client.get(reverse("interface:convocacao", args=[edital.id, MARCO])).content.decode()


def formulario_de(pagina, convocacao):
    """O formulário de correção do cartão desta convocação, ou `None`."""
    achado = re.search(
        r'<form[^>]*data-correcao[^>]*>(?:(?!</form>).)*?name="corrige" value="'
        + str(convocacao.id)
        + r'">(?:(?!</form>).)*</form>',
        pagina,
        re.S,
    )
    return achado.group(0) if achado else None


def assinatura_em(formulario):
    return re.search(r'name="previa" value="([0-9a-f]+)"', formulario).group(1)


def postar(client, edital, convocacao, *, assinatura, chave="tela-corrigir", **campos):
    dados = {
        "chave": chave,
        "inscricao": str(convocacao.inscricao_id),
        "corrige": str(convocacao.id),
        "previa": assinatura,
        "motivo": MOTIVO,
        "vencimento": campo(timezone.now() + 2 * TRES_DIAS),
        **campos,
    }
    return client.post(reverse("interface:convocar", args=[edital.id, MARCO]), dados)


def corrigir_pela_tela(client, edital, convocacao, **campos):
    formulario = formulario_de(abrir(client, edital), convocacao)
    assert formulario, "o cartão oferece a correção"
    resposta = postar(client, edital, convocacao, assinatura=assinatura_em(formulario), **campos)
    assert resposta.status_code == 302, resposta.content
    return client.get(resposta["Location"]).content.decode()


def sucessora_de(convocacao):
    return Convocacao.objects.filter(convocacao_anterior=convocacao).first()


# --- A ação (FR-3837, FR-3838) ------------------------------------------------------------------


class TestAAcao:
    def test_a_acao_aparece_com_prazo_em_curso(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])

        pagina = abrir(client, edital)

        assert "Prazo em curso" in pagina
        assert ACAO in pagina and formulario_de(pagina, raiz)

    def test_a_acao_aparece_com_vencimento_decorrido(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor, vencimento=timezone.now() + timedelta(minutes=1))
        identificar(client, "carlos", ["gestor"])

        with mock.patch("django.utils.timezone.now", return_value=timezone.now() + TRES_DIAS):
            pagina = abrir(client, edital)

        assert "Vencimento decorrido" in pagina
        formulario = formulario_de(pagina, raiz)
        assert formulario and "O que reabre" in formulario

    def test_a_acao_aparece_sem_comunicacao_enviada(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor, comunicar=False)
        identificar(client, "carlos", ["gestor"])

        pagina = abrir(client, edital)

        assert "Sem comunicação enviada" in pagina
        assert formulario_de(pagina, raiz)

    def test_sem_acao_na_chamada_com_desfecho(self, client, cenario, gestor):
        from tests.fixtures.documentos_da_convocacao import desfechar

        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        desfechar(edital, gestor, raiz, nomes.DESISTENCIA_EXPRESSA, chave="desistiu")
        identificar(client, "carlos", ["gestor"])

        assert ACAO not in abrir(client, edital)

    def test_sem_acao_na_chamada_sem_vencimento(self, client, cenario, gestor):
        edital, _, _ = cenario
        chamar(edital, gestor, vencimento=None)
        identificar(client, "carlos", ["gestor"])

        assert ACAO not in abrir(client, edital)

    def test_sem_acao_com_o_processo_encerrado(self, client, cenario, gestor):
        from tests.fixtures.jornada_do_convocado import encerrar_o_processo

        edital, _, _ = cenario
        chamar(edital, gestor)
        encerrar_o_processo(edital)
        identificar(client, "carlos", ["gestor"])

        assert ACAO not in abrir(client, edital)

    def test_sem_acao_para_o_membro_da_conferencia(self, client, cenario, gestor):
        from processo_seletivo.comissoes.application.alocacao import alocar_a_conferencia
        from processo_seletivo.comissoes.models import MembroComissao

        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        membro = MembroComissao.objects.get(processo=edital.processo, identity_subject="joao")
        alocar_a_conferencia(
            actor=gestor,
            processo_id=edital.processo_id,
            membro_id=membro.id,
            edital_id=edital.id,
            perfil_id=None,
            idempotency_key="alocar-120",
            correlation_id="teste-120",
        )
        identificar(client, "joao", [])

        pagina = abrir(client, edital)

        assert raiz.chamada and ACAO not in pagina

    def test_sem_acao_para_a_auditoria(self, client, cenario, gestor):
        edital, _, _ = cenario
        chamar(edital, gestor)
        identificar(client, "auditora", ["auditor"])

        resposta = client.get(reverse("interface:convocacao", args=[edital.id, MARCO]))

        assert resposta.status_code == 200
        assert ACAO not in resposta.content.decode()

    def test_a_sucedida_nao_tem_cartao(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])

        pagina = corrigir_pela_tela(client, edital, raiz)

        assert formulario_de(pagina, raiz) is None
        assert formulario_de(pagina, sucessora_de(raiz))


# --- A prévia (FR-3841, FR-3844, FR-3845, FR-3856) ----------------------------------------------


class TestAPrevia:
    def test_a_previa_mostra_cada_valor_com_a_origem(self, client, cenario, gestor):
        edital, _, inscricoes = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])

        formulario = formulario_de(abrir(client, edital), raiz)

        assert "chamada nº 1" in formulario
        assert "Vencimento atual" in formulario
        assert timezone.localtime(raiz.vencimento).strftime("%d/%m/%Y %H:%M") in formulario
        assert "(da posição na fila" in formulario
        assert "(derivado" in formulario
        assert "(da forma que o Perfil publicado declara)" in formulario
        assert "A lista de documentos, os envios e as conferências desta chamada" in formulario

    def test_a_previa_diz_que_reabre_so_na_chamada_vencida(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])

        assert "O que reabre" not in formulario_de(abrir(client, edital), raiz)

    def test_a_previa_diz_a_comunicacao_pela_forma(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])

        formulario = formulario_de(abrir(client, edital), raiz)

        assert "A mensagem da convocação sai de novo, com o prazo novo." in formulario
        assert "Ela não diz que corrige a anterior." in formulario

    def test_a_previa_diz_as_tres_regras_sem_vencimento(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])

        formulario = formulario_de(abrir(client, edital), raiz)

        assert "posterior ao atual estende o prazo" in formulario
        assert "o antecipa; igual, o mantém" in formulario
        assert f'data-vencimento-atual="{campo(raiz.vencimento)}"' in formulario

    def test_a_previa_diz_quando_a_especie_muda(self, client, cenario, gestor):
        """A posição que mudou desde a chamada é dita: simulada pela espécie que a função devolve,
        cuja regra a unidade prende."""
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])
        outra = nomes.VAGA_INICIAL if raiz.especie != nomes.VAGA_INICIAL else nomes.SUPLENCIA

        with mock.patch(
            "processo_seletivo.convocacao.domain.especie.especie_da_sucessora",
            return_value=outra,
        ):
            formulario = formulario_de(abrir(client, edital), raiz)

        assert "a convocação corrigida era" in formulario

    def test_a_previa_diz_quando_o_fundamento_muda(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        apurar(edital, gestor, chave="seguinte-120", motivo="Conferência da contagem.")
        identificar(client, "carlos", ["gestor"])

        formulario = formulario_de(abrir(client, edital), raiz)

        assert "cita a apuração e o Edital vigentes hoje" in formulario

    def test_o_vencimento_nao_vem_preenchido(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])

        formulario = formulario_de(abrir(client, edital), raiz)

        campo_do_vencimento = re.search(r'<input type="datetime-local"[^>]*>', formulario).group(0)
        assert "value=" not in campo_do_vencimento
        assert "Obrigatório: a correção informa o vencimento novo." in formulario

    def test_o_formulario_declara_a_irreversibilidade(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])

        formulario = formulario_de(abrir(client, edital), raiz)

        assert "Corrigir é irreversível." in formulario
        assert "encurta um prazo já comunicado" in formulario

    def test_o_botao_nomeia_o_protocolo(self, client, cenario, gestor):
        from processo_seletivo.inscricoes.models import Inscricao

        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        protocolo = Inscricao.objects.get(id=raiz.inscricao_id).protocolo
        identificar(client, "carlos", ["gestor"])

        assert f"Corrigir a convocação de {protocolo}</button>" in formulario_de(
            abrir(client, edital), raiz
        )

    def test_o_ato_se_chama_corrigir_esta_convocacao(self, client, cenario, gestor):
        """`FR-3856`: os atos que não existem não aparecem como nome de ato."""
        edital, _, _ = cenario
        chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])

        pagina = abrir(client, edital)
        visivel = re.sub(r"<[^>]+>", " ", pagina).lower()

        assert "<summary>Corrigir esta convocação</summary>" in pagina
        assert "prorroga" not in visivel
        assert "reabertura de prazo" not in visivel


# --- O ato pela tela (FR-3849, FR-3852, FR-3853) ------------------------------------------------


class TestOAto:
    def test_o_resultado_diz_estendido(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])
        novo = timezone.now() + 2 * TRES_DIAS

        pagina = corrigir_pela_tela(client, edital, raiz, vencimento=campo(novo))

        anterior = timezone.localtime(raiz.vencimento).strftime("%d/%m/%Y %H:%M")
        assert "corrigida. O vencimento passou de " + anterior in pagina
        assert "o prazo foi estendido" in pagina
        assert "1 comunicação enviada" in pagina
        assert sucessora_de(raiz).motivo_da_sucessao == MOTIVO

    def test_o_resultado_diz_antecipado(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor, vencimento=timezone.now() + 3 * TRES_DIAS)
        identificar(client, "carlos", ["gestor"])

        pagina = corrigir_pela_tela(
            client, edital, raiz, vencimento=campo(timezone.now() + TRES_DIAS)
        )

        assert "o prazo foi antecipado" in pagina

    def test_o_resultado_diz_mantido(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])

        pagina = corrigir_pela_tela(client, edital, raiz, vencimento=campo(raiz.vencimento))

        assert "o prazo foi mantido" in pagina

    def test_o_cartao_mostra_a_sucessora_corrigida(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])
        novo = timezone.now() + 2 * TRES_DIAS

        pagina = corrigir_pela_tela(client, edital, raiz, vencimento=campo(novo))

        assert "<dt>Correção</dt><dd>Corrigida em" in pagina
        assert "ver o histórico</a>" in pagina
        assert timezone.localtime(novo).strftime("%d/%m/%Y %H:%M") in pagina

    def test_duas_correcoes_deixam_tres_linhas_no_historico(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])
        corrigir_pela_tela(client, edital, raiz, chave="c1")
        corrigir_pela_tela(client, edital, sucessora_de(raiz), chave="c2", motivo="Outro atraso.")

        historico = client.get(
            reverse("interface:convocacao-historico", args=[edital.id, MARCO])
        ).content.decode()

        assert Convocacao.objects.filter(inscricao_id=raiz.inscricao_id).count() == 3
        assert f"sucedida — {MOTIVO}" in historico
        assert "sucedida — Outro atraso." in historico

    def test_quem_tem_chamada_em_aberto_continua_fora_da_fila(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])

        pagina = corrigir_pela_tela(client, edital, raiz)

        assert f'<option value="{raiz.inscricao_id}"' not in pagina

    def test_a_pendente_da_corrigida_sai_das_comunicacoes_que_nao_sairam(
        self, client, cenario, gestor
    ):
        from processo_seletivo.convocacao.application import fluxo

        edital, _, _ = cenario
        raiz = chamar(edital, gestor, comunicar=False)
        identificar(client, "carlos", ["gestor"])

        corrigir_pela_tela(client, edital, raiz)

        pendentes = fluxo.previa_das_pendentes(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
        assert raiz.id not in {linha["convocacao"].id for linha in pendentes["linhas"]}


# --- O impedimento e as recusas no cartão (FR-3839, FR-3847, FR-3850) ---------------------------


def _deixar_a_apuracao_para_tras(edital):
    from processo_seletivo.ocupacao.application.efeitos import registrar_efeito
    from processo_seletivo.ocupacao.domain import nomes as nomes_da_ocupacao

    registrar_efeito(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=None,
        inscricao_id=uuid.uuid4(),
        especie=nomes_da_ocupacao.EFEITO_EXCLUSAO,
        fundamento="Desistência expressa da titular",
        ato_de_origem_id=uuid.uuid4(),
        rotulo_da_origem="desfecho de convocação",
        registrado_por="teste",
        registrado_em=timezone.now(),
    )


class TestAsRecusas:
    def test_apuracao_superada_mostra_a_limitacao_e_o_caminho(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        _deixar_a_apuracao_para_tras(edital)
        identificar(client, "carlos", ["gestor"])

        pagina = abrir(client, edital)

        assert formulario_de(pagina, raiz) is None
        assert "A correção está impedida." in pagina
        assert "um desfecho de convocação mudou quem ocupa vaga neste recorte depois dela" in pagina
        ocupacao = reverse("interface:ocupacao", args=[edital.id, MARCO])
        assert pagina.count(f'href="{ocupacao}">Emitir a apuração seguinte') >= 2

    def test_motivo_vazio_volta_ao_cartao_com_o_vencimento(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])
        formulario = formulario_de(abrir(client, edital), raiz)
        vencimento = campo(timezone.now() + 2 * TRES_DIAS)

        resposta = postar(
            client,
            edital,
            raiz,
            assinatura=assinatura_em(formulario),
            motivo="  ",
            vencimento=vencimento,
        )
        pagina = client.get(resposta["Location"]).content.decode()
        de_novo = formulario_de(pagina, raiz)

        assert sucessora_de(raiz) is None
        assert "Declare o motivo da correção" in de_novo
        assert f'value="{vencimento}"' in de_novo
        assert 'aria-invalid="true"' in de_novo
        assert '<details class="como-preencher" open>\n  <summary>Corrigir esta convocação' in (
            pagina
        )

    def test_vencimento_passado_volta_ao_cartao_com_o_motivo(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])
        formulario = formulario_de(abrir(client, edital), raiz)

        resposta = postar(
            client,
            edital,
            raiz,
            assinatura=assinatura_em(formulario),
            vencimento=campo(timezone.now() - timedelta(hours=2)),
        )
        de_novo = formulario_de(client.get(resposta["Location"]).content.decode(), raiz)

        assert "O vencimento informado já passou" in de_novo
        assert f">{MOTIVO}</textarea>" in de_novo

    def test_a_recusa_do_dominio_volta_ao_cartao_com_os_campos(self, client, cenario, gestor):
        """Sem vencimento: a recusa nomeia o campo, e o motivo e o complemento continuam."""
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])
        formulario = formulario_de(abrir(client, edital), raiz)

        resposta = postar(
            client,
            edital,
            raiz,
            assinatura=assinatura_em(formulario),
            vencimento="",
            complemento="Ofício 12/2026.",
        )
        de_novo = formulario_de(client.get(resposta["Location"]).content.decode(), raiz)

        assert "Informe o vencimento novo" in de_novo
        assert f">{MOTIVO}</textarea>" in de_novo
        assert ">Ofício 12/2026.</textarea>" in de_novo

    def test_a_previa_superada_volta_com_a_previa_nova_e_os_campos(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])
        velha = assinatura_em(formulario_de(abrir(client, edital), raiz))
        apurar(edital, gestor, chave="seguinte-no-intervalo", motivo="Conferência.")

        resposta = postar(client, edital, raiz, assinatura=velha)
        de_novo = formulario_de(client.get(resposta["Location"]).content.decode(), raiz)

        assert sucessora_de(raiz) is None
        assert "A prévia mudou desde que você abriu este formulário" in de_novo
        assert assinatura_em(de_novo) != velha, "a prévia é a nova"
        assert f">{MOTIVO}</textarea>" in de_novo

    def test_impedimento_no_intervalo_volta_com_a_orientacao(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])
        assinatura = assinatura_em(formulario_de(abrir(client, edital), raiz))
        _deixar_a_apuracao_para_tras(edital)

        resposta = postar(client, edital, raiz, assinatura=assinatura)
        pagina = client.get(resposta["Location"]).content.decode()

        assert sucessora_de(raiz) is None
        assert "A correção não foi feita." in pagina
        assert "emita a apuração seguinte antes de convocar" in pagina
        assert "A correção está impedida." in pagina

    def test_o_cartao_sucedido_cita_o_motivo_e_nao_o_preenche(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])
        velha = assinatura_em(formulario_de(abrir(client, edital), raiz))
        corrigir_pela_tela(client, edital, raiz, chave="outra-aba", motivo="Corrigida antes.")

        resposta = postar(client, edital, raiz, assinatura=velha, chave="aba-velha")
        pagina = client.get(resposta["Location"]).content.decode()

        assert "já foi corrigida em" in pagina
        assert f'<blockquote class="nota">{MOTIVO}</blockquote>' in pagina
        assert "Corrigida por" in pagina
        formulario_da_sucessora = formulario_de(pagina, sucessora_de(raiz))
        assert formulario_da_sucessora and MOTIVO not in formulario_da_sucessora
        assert Convocacao.objects.filter(inscricao_id=raiz.inscricao_id).count() == 2

    def test_o_cartao_com_desfecho_cita_o_motivo_sem_formulario(self, client, cenario, gestor):
        from tests.fixtures.documentos_da_convocacao import desfechar

        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])
        velha = assinatura_em(formulario_de(abrir(client, edital), raiz))
        desfechar(edital, gestor, raiz, nomes.ACEITE, chave="aceitou-no-intervalo")
        if "A correção está impedida." in abrir(client, edital):
            apurar(edital, gestor, chave="em-dia-120", motivo="Depois do aceite.")

        resposta = postar(client, edital, raiz, assinatura=velha)
        pagina = client.get(resposta["Location"]).content.decode()

        assert "teve desfecho em" in pagina
        assert f'<blockquote class="nota">{MOTIVO}</blockquote>' in pagina
        assert formulario_de(pagina, raiz) is None
        assert Convocacao.objects.filter(inscricao_id=raiz.inscricao_id).count() == 1

    def test_o_post_sem_base_recebe_403_e_nada_grava(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])
        assinatura = assinatura_em(formulario_de(abrir(client, edital), raiz))
        identificar(client, "auditora", ["auditor"])

        resposta = postar(client, edital, raiz, assinatura=assinatura)

        assert resposta.status_code == 403
        assert sucessora_de(raiz) is None
        assert "recusa_da_correcao" not in client.session

    def test_o_post_de_outra_unidade_recebe_404_e_nada_grava(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"], escopo="campus-alegre")

        resposta = postar(client, edital, raiz, assinatura="x")

        assert resposta.status_code == 404
        assert sucessora_de(raiz) is None

    def test_a_nomeada_de_outro_recorte_recebe_404(self, client, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        identificar(client, "carlos", ["gestor"])

        resposta = postar(client, edital, raiz, assinatura="x", corrige=str(uuid.uuid4()))

        assert resposta.status_code == 404
        assert sucessora_de(raiz) is None


# --- Um ato, uma vez (FR-3848, US4) -------------------------------------------------------------


def test_o_duplo_post_corrige_uma_vez(client, cenario, gestor):
    edital, _, _ = cenario
    raiz = chamar(edital, gestor)
    identificar(client, "carlos", ["gestor"])
    assinatura = assinatura_em(formulario_de(abrir(client, edital), raiz))

    primeira = postar(client, edital, raiz, assinatura=assinatura, chave="duplo-clique")
    segunda = postar(client, edital, raiz, assinatura=assinatura, chave="duplo-clique")
    pagina = client.get(segunda["Location"]).content.decode()

    assert primeira.status_code == segunda.status_code == 302
    assert Convocacao.objects.filter(convocacao_anterior=raiz).count() == 1
    assert len(mail.outbox) == 2, "a da raiz e a da sucessora — nenhuma segunda da sucessora"
    assert "corrigida. O vencimento passou de" in pagina
    assert "A correção não foi feita." not in pagina

    corrigir_pela_tela(client, edital, sucessora_de(raiz), chave="de-novo", motivo="Outra razão.")

    assert Convocacao.objects.filter(inscricao_id=raiz.inscricao_id).count() == 3
