"""A correção da convocação pelo caminho da tela (120): a convocação nomeada e a prévia assinada.

**O comando corrige o que foi visto, ou nada.** Pela tela, o formulário aberto pode ficar para trás:
outra pessoa corrige a chamada, um desfecho chega, a apuração seguinte é emitida. Sem as duas
conferências, o formulário velho corrigiria a sucessora, praticaria chamada nova ou gravaria um
fundamento que ninguém viu (`FR-3843`, `FR-3857`). Cada recusa abaixo grava zero (`SC-1143`).

**A repetição vem antes das conferências** (`R-002`): o segundo clique do mesmo formulário recebe o
resultado do primeiro, e não a recusa de "já corrigida" — que seria verdadeira e enganosa.
"""

import uuid
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from django.core import mail
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.convocacao.application import fluxo, selectors
from processo_seletivo.convocacao.application.convocar import CONVOCAR
from processo_seletivo.convocacao.domain import alcance, nomes
from processo_seletivo.convocacao.models import (
    ComunicacaoEmitida,
    Convocacao,
    ItemDaListaDaConvocacao,
)
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.convocacao import apurar, convocar
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)

TRES_DIAS = timedelta(days=3)
MOTIVO = "A mensagem saiu com dois dias de atraso; o prazo é dado de novo."


@pytest.fixture
def caixa_de_saida(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


def leitura_de(edital):
    return selectors.leitura_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )


def previa_de(edital, convocacao_id):
    """A prévia que a tela montaria para este cartão, agora."""
    leitura = leitura_de(edital)
    fundamentos = fluxo.fundamentos_por_especie(
        edital=edital, perfil_id=PROFILE_ID, lista_id=None, apuracao=leitura["apuracao"]
    )
    return fluxo.previa_das_correcoes(
        leitura,
        versao=effective_version(edital_id=edital.id),
        perfil_id=PROFILE_ID,
        fundamentos=fundamentos,
    )[str(convocacao_id)]


def chamar(edital, gestor, *, posicao=0, chave="raiz", vencimento=None):
    """A primeira convocação da pessoa, com vencimento: só ela se corrige pela tela (`D-004`)."""
    fila = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]
    declarado = convocar(
        edital,
        gestor,
        fila[posicao],
        idempotency_key=chave,
        vencimento=vencimento or timezone.now() + TRES_DIAS,
    )
    return Convocacao.objects.get(id=declarado["id"])


def corrigir(
    edital,
    gestor,
    corrigida,
    *,
    chave="corrigir",
    motivo=MOTIVO,
    vencimento="padrao",
    assinatura=None,
    inscricao_id=None,
    complemento="",
):
    if vencimento == "padrao":
        vencimento = timezone.now() + 2 * TRES_DIAS
    return fluxo.convocar_e_comunicar(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        inscricao_id=inscricao_id or corrigida.inscricao_id,
        idempotency_key=chave,
        correlation_id="teste-120",
        vencimento=vencimento,
        complemento=complemento,
        motivo=motivo,
        endereco_do_portal="http://testserver/selecoes/inscricoes/",
        correcao={
            "convocacao_id": str(corrigida.id),
            "assinatura": assinatura
            if assinatura is not None
            else previa_de(edital, corrigida.id)["assinatura"],
        },
    )


def contagem():
    return (
        Convocacao.objects.count(),
        ComunicacaoEmitida.objects.count(),
        RegistroAuditoria.objects.filter(operation=CONVOCAR).count(),
    )


def recusada(codigo, praticar):
    """A recusa, com o código nomeado, e a prova de que nada foi gravado (`SC-1143`)."""
    antes = contagem()
    with pytest.raises(DomainError) as erro:
        praticar()
    assert erro.value.code == codigo, erro.value.detail
    assert contagem() == antes, "a recusa não grava convocação, comunicação nem trilha"
    return erro.value


# --- A convocação nomeada (FR-3843) -------------------------------------------------------------


class TestANomeada:
    def test_a_nomeada_sucedida_e_recusada_e_nao_corrige_a_sucessora(self, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        assinatura_velha = previa_de(edital, raiz.id)["assinatura"]
        corrigir(edital, gestor, raiz, chave="primeira-aba")

        erro = recusada(
            nomes.CONVOCACAO_CORRIGIDA_SUCEDIDA,
            lambda: corrigir(
                edital, gestor, raiz, chave="segunda-aba", assinatura=assinatura_velha
            ),
        )

        assert "já foi corrigida em" in erro.detail
        assert not Convocacao.objects.filter(convocacao_anterior__convocacao_anterior=raiz).exists()

    def test_a_nomeada_com_desfecho_e_recusada_e_nao_pratica_chamada_nova(self, cenario, gestor):
        """**O caminho de hoje praticaria chamada nova**, com o motivo ignorado: sem nada em aberto,
        o comando chamaria a pessoa de novo. A conferência para o ato antes disso."""
        from tests.fixtures.documentos_da_convocacao import desfechar

        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        assinatura = previa_de(edital, raiz.id)["assinatura"]
        desfechar(edital, gestor, raiz, nomes.DESISTENCIA_EXPRESSA, chave="desistiu")

        with pytest.raises(DomainError) as erro:
            corrigir(edital, gestor, raiz, chave="depois-do-desfecho", assinatura=assinatura)

        # A desistência pode ter deixado a apuração para trás; as duas recusas param o ato, e a que
        # importa aqui é que nenhuma chamada nova nasceu.
        assert erro.value.code in {
            nomes.CONVOCACAO_CORRIGIDA_COM_DESFECHO,
            nomes.APURACAO_OBSOLETA,
        }
        assert Convocacao.objects.filter(inscricao_id=raiz.inscricao_id).count() == 1

    def test_com_desfecho_e_apuracao_em_dia_a_recusa_nomeia_o_desfecho(self, cenario, gestor):
        from tests.fixtures.documentos_da_convocacao import desfechar

        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        assinatura = previa_de(edital, raiz.id)["assinatura"]
        desfechar(edital, gestor, raiz, nomes.ACEITE, chave="aceitou")
        if leitura_de(edital)["causasDeObsolescencia"]:
            apurar(edital, gestor, chave="em-dia", motivo="Depois do aceite.")

        erro = recusada(
            nomes.CONVOCACAO_CORRIGIDA_COM_DESFECHO,
            lambda: corrigir(edital, gestor, raiz, chave="aceita", assinatura=assinatura),
        )

        assert "teve desfecho em" in erro.detail

    def test_a_nomeada_de_outra_inscricao_e_nao_encontrada(self, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        outra = chamar(edital, gestor, posicao=0, chave="outra")

        recusada(
            "not_found",
            lambda: corrigir(edital, gestor, raiz, inscricao_id=outra.inscricao_id),
        )

    def test_a_nomeada_de_outro_recorte_e_nao_encontrada(self, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        de_fora = SimpleNamespace(id=uuid.uuid4(), inscricao_id=raiz.inscricao_id)

        recusada("not_found", lambda: corrigir(edital, gestor, de_fora, assinatura="x"))

    def test_a_nomeada_sem_vencimento_e_recusada(self, cenario, gestor):
        """A tela não oferece a correção ali (`D-004`); o formulário montado à mão é recusado."""
        edital, _, _ = cenario
        fila = selectors.contexto_do_recorte(
            edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
        )["fila"]
        sem_prazo = Convocacao.objects.get(
            id=convocar(edital, gestor, fila[0], idempotency_key="sem-prazo")["id"]
        )

        recusada(
            nomes.CORRECAO_SEM_VENCIMENTO,
            lambda: corrigir(edital, gestor, sem_prazo, assinatura="x"),
        )


# --- As recusas do formulário (FR-3840, FR-3841) ------------------------------------------------


class TestOFormulario:
    @pytest.mark.parametrize("motivo", ["", "   "])
    def test_sem_motivo_a_correcao_e_recusada_pelo_campo(self, cenario, gestor, motivo):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)

        erro = recusada(
            nomes.MOTIVO_DA_CORRECAO_OBRIGATORIO,
            lambda: corrigir(edital, gestor, raiz, motivo=motivo),
        )

        assert erro.campo == "motivo"

    def test_sem_vencimento_a_correcao_e_recusada_pelo_campo(self, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)

        recusada(
            nomes.VENCIMENTO_DA_CORRECAO_OBRIGATORIO,
            lambda: corrigir(edital, gestor, raiz, vencimento=None),
        )

    def test_vencimento_passado_e_recusado(self, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)

        recusada(
            nomes.VENCIMENTO_ANTERIOR_AO_ENVIO,
            lambda: corrigir(edital, gestor, raiz, vencimento=timezone.now() - timedelta(hours=1)),
        )

    def test_com_o_processo_encerrado_a_correcao_e_recusada(self, cenario, gestor):
        from tests.fixtures.jornada_do_convocado import encerrar_o_processo

        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        assinatura = previa_de(edital, raiz.id)["assinatura"]
        encerrar_o_processo(edital)
        antes = contagem()

        with pytest.raises(DomainError):
            corrigir(edital, gestor, raiz, assinatura=assinatura)

        assert contagem() == antes


# --- A prévia confirmada (FR-3857) --------------------------------------------------------------


class TestAPrevia:
    def test_apuracao_seguinte_no_intervalo_recusa_a_previa(self, cenario, gestor):
        """A apuração nova muda a data que o fundamento cita sem tocar na convocação."""
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        assinatura = previa_de(edital, raiz.id)["assinatura"]
        apurar(edital, gestor, chave="seguinte", motivo="Conferência da contagem.")
        assert leitura_de(edital)["causasDeObsolescencia"] == []

        recusada(
            nomes.PREVIA_DA_CORRECAO_SUPERADA,
            lambda: corrigir(edital, gestor, raiz, assinatura=assinatura),
        )

    def test_retificacao_no_intervalo_recusa_a_previa(self, cenario, gestor):
        """**A versão lida sob a trava é outra**, como depois de uma Retificação publicada.

        Simulada pela versão que o comando lê, e não por uma Retificação inteira: o que se prende é
        que a versão entra na conferência, e a unidade já prova que ela muda a assinatura.
        """
        from processo_seletivo.convocacao.application import convocar as modulo

        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        assinatura = previa_de(edital, raiz.id)["assinatura"]
        real = effective_version(edital_id=edital.id)
        retificada = SimpleNamespace(id=uuid.uuid4(), content=real.content)

        with mock.patch.object(modulo, "effective_version", return_value=retificada):
            recusada(
                nomes.PREVIA_DA_CORRECAO_SUPERADA,
                lambda: corrigir(edital, gestor, raiz, assinatura=assinatura),
            )

    def test_especie_mudada_no_intervalo_recusa_a_previa(self, cenario, gestor):
        """A prévia que assinou outra espécie não confirma a de agora."""
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        previa = previa_de(edital, raiz.id)
        outra_especie = (
            nomes.SUPLENCIA if previa["especie"] != nomes.SUPLENCIA else nomes.VAGA_INICIAL
        )
        assinatura = alcance.assinatura_da_correcao(
            convocacao_id=raiz.id,
            apuracao_id=leitura_de(edital)["apuracao"].id,
            versao_id=effective_version(edital_id=edital.id).id,
            forma=previa["forma"],
            especie=outra_especie,
        )

        recusada(
            nomes.PREVIA_DA_CORRECAO_SUPERADA,
            lambda: corrigir(edital, gestor, raiz, assinatura=assinatura),
        )


# --- O ato (FR-3842, FR-3846, FR-3853) ----------------------------------------------------------


class TestOAto:
    def test_a_sucessora_aponta_a_corrigida_e_reaproveita_a_chamada(self, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        novo = timezone.now() + 4 * TRES_DIAS

        declarado = corrigir(edital, gestor, raiz, vencimento=novo)

        sucessora = Convocacao.objects.get(id=declarado["convocacao"]["id"])
        assert sucessora.convocacao_anterior_id == raiz.id
        assert sucessora.chamada == raiz.chamada
        assert sucessora.vencimento == novo
        assert sucessora.motivo_da_sucessao == MOTIVO
        raiz.refresh_from_db()
        assert raiz.vencimento != novo, "a corrigida não muda"

    def test_o_complemento_entra_no_fundamento_gravado(self, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        previa = previa_de(edital, raiz.id)

        declarado = corrigir(edital, gestor, raiz, complemento="Ofício 12/2026 da comissão.")

        gravado = Convocacao.objects.get(id=declarado["convocacao"]["id"]).fundamento
        assert gravado.startswith(previa["fundamento"]), "o texto gravado é o mostrado"
        assert gravado.endswith("Complemento: Ofício 12/2026 da comissão.")

    def test_a_sucessora_tambem_se_corrige_com_a_mesma_chamada(self, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        segunda = Convocacao.objects.get(
            id=corrigir(edital, gestor, raiz, chave="c1")["convocacao"]["id"]
        )

        terceira = Convocacao.objects.get(
            id=corrigir(edital, gestor, segunda, chave="c2", motivo="Outro atraso.")["convocacao"][
                "id"
            ]
        )

        assert terceira.convocacao_anterior_id == segunda.id
        assert {raiz.chamada, segunda.chamada, terceira.chamada} == {raiz.chamada}

    def test_vencimento_anterior_futuro_e_admitido(self, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor, vencimento=timezone.now() + 3 * TRES_DIAS)
        antecipado = timezone.now() + TRES_DIAS

        declarado = corrigir(edital, gestor, raiz, vencimento=antecipado)

        assert Convocacao.objects.get(id=declarado["convocacao"]["id"]).vencimento == antecipado
        assert fluxo.efeito_do_vencimento(raiz.vencimento, antecipado) == "antecipado"

    def test_o_efeito_do_vencimento(self):
        # **Do minuto cheio**: o campo tem minuto, e não segundo, e somar segundos a um instante
        # qualquer cruzava a virada do minuto com o relógio depois dos 40: falhou assim uma vez.
        agora = timezone.now().replace(second=0, microsecond=0)
        assert fluxo.efeito_do_vencimento(agora, agora + TRES_DIAS) == "estendido"
        assert fluxo.efeito_do_vencimento(agora + TRES_DIAS, agora) == "antecipado"
        assert fluxo.efeito_do_vencimento(agora, agora + timedelta(seconds=20)) == "mantido"

    def test_a_correcao_nao_toca_a_lista_da_chamada(self, cenario, gestor):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        antes = ItemDaListaDaConvocacao.objects.count()

        corrigir(edital, gestor, raiz)

        assert ItemDaListaDaConvocacao.objects.count() == antes, "a sucessora usa a da chamada"

    def test_o_lote_continua_sem_sucessao(self, cenario_do_77, gestor):
        """Quem tem chamada em aberto não entra no gesto dos titulares (`FR-861` da `050`)."""
        edital, _, _ = cenario_do_77
        raiz = chamar(edital, gestor)
        corrigir(edital, gestor, raiz)

        pessoas = fluxo.previa_dos_titulares(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)[
            "pessoas"
        ]

        assert str(raiz.inscricao_id) not in {str(p["id"]) for p in pessoas}


# --- A idempotência (FR-3848, SC-1144) ----------------------------------------------------------


class TestARepeticao:
    def test_a_repeticao_devolve_o_resultado_por_mensagem_individual(
        self, cenario, gestor, caixa_de_saida
    ):
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        assinatura = previa_de(edital, raiz.id)["assinatura"]

        primeira = corrigir(edital, gestor, raiz, chave="duplo", assinatura=assinatura)
        segunda = corrigir(edital, gestor, raiz, chave="duplo", assinatura=assinatura)

        assert segunda["convocacao"] == primeira["convocacao"]
        assert Convocacao.objects.filter(convocacao_anterior=raiz).count() == 1
        assert primeira["enviadas"] == 1 and len(caixa_de_saida) == 1, "uma mensagem só"
        assert RegistroAuditoria.objects.filter(operation=CONVOCAR).count() == 2  # raiz + sucessora

    def test_a_repeticao_devolve_o_resultado_por_publicacao(
        self, cenario_por_publicacao, gestor, caixa_de_saida
    ):
        edital, _, _ = cenario_por_publicacao
        raiz = chamar(edital, gestor)
        assinatura = previa_de(edital, raiz.id)["assinatura"]

        primeira = corrigir(edital, gestor, raiz, chave="duplo-pub", assinatura=assinatura)
        segunda = corrigir(edital, gestor, raiz, chave="duplo-pub", assinatura=assinatura)

        assert primeira["aguardandoPublicacao"] == segunda["aguardandoPublicacao"] == 1
        assert Convocacao.objects.filter(convocacao_anterior=raiz).count() == 1
        assert caixa_de_saida == []

    def test_a_repeticao_devolve_a_falha_sem_reenviar(self, cenario, gestor, settings):
        settings.EMAIL_BACKEND = "tests.unit.convocacao.test_mensagem.CorreioQueFalha"
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        assinatura = previa_de(edital, raiz.id)["assinatura"]

        primeira = corrigir(edital, gestor, raiz, chave="duplo-falha", assinatura=assinatura)
        segunda = corrigir(edital, gestor, raiz, chave="duplo-falha", assinatura=assinatura)

        assert primeira["falhas"] == segunda["falhas"] == 1
        assert ComunicacaoEmitida.objects.filter(convocacao__convocacao_anterior=raiz).count() == 1

    def test_duas_correcoes_de_formularios_diferentes_so_uma_grava(self, cenario, gestor):
        """Duas abas, duas chaves: a segunda passa pela conferência, e a recusa diz por quê."""
        edital, _, _ = cenario
        raiz = chamar(edital, gestor)
        assinatura = previa_de(edital, raiz.id)["assinatura"]
        corrigir(edital, gestor, raiz, chave="aba-1", assinatura=assinatura)

        recusada(
            nomes.CONVOCACAO_CORRIGIDA_SUCEDIDA,
            lambda: corrigir(edital, gestor, raiz, chave="aba-2", assinatura=assinatura),
        )


# --- A trilha (FR-3851, SC-1149) ----------------------------------------------------------------


def test_a_trilha_nomeia_a_corrigida_o_motivo_e_os_dois_vencimentos(cenario, gestor):
    edital, _, _ = cenario
    raiz = chamar(edital, gestor)
    novo = timezone.now() + 4 * TRES_DIAS

    declarado = corrigir(edital, gestor, raiz, vencimento=novo)

    registro = RegistroAuditoria.objects.get(
        operation=CONVOCAR, aggregate_id=declarado["convocacao"]["id"]
    )
    assert registro.actor_subject == gestor.subject
    assert f"Motivo da sucessão: {MOTIVO}" in registro.reason
    assert f"Sucede a convocação {raiz.id}, de vencimento {raiz.vencimento.isoformat()}." in (
        registro.reason
    )
    assert timezone.localtime(novo).strftime("%d/%m/%Y %H:%M") in registro.reason


# --- Com documentos e com regularização (casos-limite) ------------------------------------------


@pytest.fixture
def aluno(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Os documentos do aluno na convocação, e o Requerimento declarado *na convocação*."""
    from tests.fixtures import documentos_da_convocacao as cenarios
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.requerimento import declarar

    def publicar(api_client, manager_headers, process_payload, *, draft=None):
        return publish_original(
            api_client,
            manager_headers,
            process_payload,
            draft=draft,
            antes_de_submeter=declarar("AT_CALL"),
        )

    return cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="aluno-120",
        publicar=publicar,
    )


@pytest.fixture
def com_indeferidos(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    from tests.fixtures.convocacao import montar_cenario_da_convocacao

    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="regularizacao-120",
        indeferidas=(0, 1),
    )


def _com_pendencia(aluno, gestor):
    from tests.fixtures.documentos_da_convocacao import (
        HISTORICO,
        apresentar,
        comunicar,
        conferir,
        convocar_primeira,
    )

    edital, _, _ = aluno
    pessoa, raiz = convocar_primeira(
        aluno, gestor, chave="raiz-120", vencimento=timezone.now() + TRES_DIAS
    )
    comunicar(edital, gestor, raiz)
    apresentar(pessoa, raiz, HISTORICO, corpo=b"sem a pagina 2")
    conferir(gestor, raiz, HISTORICO, "PENDENTE", chave="h1", motivo="Falta a página 2.")
    return edital, pessoa, raiz


def test_a_correcao_nao_toca_lista_apresentacoes_nem_conferencias(aluno, gestor):
    """A sucessora usa a lista, as apresentações e as conferências da chamada (`FR-3573`)."""
    from processo_seletivo.convocacao.models import (
        ApresentacaoDeDocumento,
        ConferenciaDeDocumento,
    )
    from tests.fixtures.documentos_da_convocacao import HISTORICO, lido

    edital, _, raiz = _com_pendencia(aluno, gestor)
    antes = (
        ItemDaListaDaConvocacao.objects.count(),
        ApresentacaoDeDocumento.objects.count(),
        ConferenciaDeDocumento.objects.count(),
    )

    sucessora = Convocacao.objects.get(id=corrigir(edital, gestor, raiz)["convocacao"]["id"])

    assert (
        ItemDaListaDaConvocacao.objects.count(),
        ApresentacaoDeDocumento.objects.count(),
        ConferenciaDeDocumento.objects.count(),
    ) == antes
    assert lido(sucessora, HISTORICO).estado == nomes.ITEM_PENDENTE, "a pendência continua"


def test_o_desfecho_se_registra_na_sucessora_e_a_pendencia_bloqueia(aluno, gestor):
    from tests.fixtures.documentos_da_convocacao import desfechar

    edital, _, raiz = _com_pendencia(aluno, gestor)
    sucessora = Convocacao.objects.get(id=corrigir(edital, gestor, raiz)["convocacao"]["id"])

    with pytest.raises(DomainError) as recusa:
        desfechar(edital, gestor, sucessora, nomes.ACEITE, "aceite-com-pendencia")

    assert recusa.value.code == nomes.DOCUMENTOS_NAO_CONFERIDOS


def test_vencido_o_novo_prazo_tudo_fecha_junto(aluno, gestor):
    """Corrigida depois do vencimento, a chamada reabre documento e Requerimento juntos, e o
    vencimento novo, decorrido, fecha os dois de novo (`FR-3622` da `115`, `SC-1142`)."""
    from processo_seletivo.requerimentos.application import preencher
    from tests.fixtures.documentos_da_convocacao import HISTORICO, apresentar, comunicar

    edital, pessoa, raiz = _com_pendencia(aluno, gestor)
    depois = timezone.now() + 2 * TRES_DIAS
    novo = depois + TRES_DIAS

    with mock.patch("django.utils.timezone.now", return_value=depois):
        with pytest.raises(DomainError):
            apresentar(pessoa, raiz, HISTORICO, corpo=b"fora do prazo")
        declarado = corrigir(edital, gestor, raiz, vencimento=novo, chave="depois-do-prazo")
        sucessora = Convocacao.objects.get(id=declarado["convocacao"]["id"])
        comunicar(edital, gestor, sucessora, chave="comunicar-sucessora")
        apresentar(pessoa, sucessora, HISTORICO, corpo=b"historico completo")
        assert preencher.abrir_rascunho(inscricao=pessoa) is not None

    with mock.patch("django.utils.timezone.now", return_value=novo + timedelta(days=1)):
        with pytest.raises(DomainError):
            apresentar(pessoa, sucessora, HISTORICO, corpo=b"de novo fora do prazo")
        assert preencher.apurar(pessoa).prazo_decorrido, "o Requerimento fecha junto"


def test_a_chamada_para_regularizar_se_corrige_sem_a_guarda_de_ordem(com_indeferidos, gestor):
    edital, _, _ = com_indeferidos
    primeiro, _ = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["regularizaveis"]
    raiz = Convocacao.objects.get(
        id=convocar(
            edital,
            gestor,
            primeiro,
            especie=nomes.PARA_REGULARIZAR,
            idempotency_key="regularizar",
            vencimento=timezone.now() + TRES_DIAS,
        )["id"]
    )

    sucessora = Convocacao.objects.get(id=corrigir(edital, gestor, raiz)["convocacao"]["id"])

    assert sucessora.especie == nomes.PARA_REGULARIZAR
    assert sucessora.convocacao_anterior_id == raiz.id
