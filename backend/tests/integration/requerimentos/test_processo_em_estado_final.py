"""O Processo encerrado ou cancelado fecha o Requerimento *na convocação* (FR-373, FR-408, `029`).

**Decidido pelo usuário em 04/11/2026.** Com o Processo em estado final, o GPS já recusava o envio e
a conferência de documento da convocação e o registro do desfecho; o Requerimento seguia aberto, e o
que se enviasse não teria ato que o considerasse (FR-035 da `001`). Agora o preenchimento, o envio e
o sucessor se recusam, **com a mesma recusa** dos documentos — e a leitura e o rascunho ficam.

**Os dois casos vizinhos que não mudam, presos aqui para que não mudem por engano:** o Edital
encerrado com o Processo ativo continua seguindo a chamada (FR-3616 da `115`), e o Requerimento *na
inscrição* continua como estava — o sucessor dele com o Processo encerrado é decisão pendente.

**Chamado direto, sem passar por tela**, como em `test_sucessao.py`: o que se prende é o comando, e
um `POST` montado à mão encontra a mesma recusa (Princípio IV). A página tem a sua classe, ao fim.
"""

from datetime import timedelta
from unittest import mock

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.convocacao.application.selectors import chamada_em_aberto
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.requerimentos.application import exigencia, preencher
from processo_seletivo.requerimentos.application.selectors import leitura
from processo_seletivo.requerimentos.domain import nomes
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import MARIA
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

ESTADOS_FINAIS = [ProcessoSeletivo.Status.ENCERRADO, ProcessoSeletivo.Status.CANCELADO]


def _publicador(momento):
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.requerimento import declarar

    def publicar(api_client, manager_headers, process_payload, *, draft=None):
        return publish_original(
            api_client,
            manager_headers,
            process_payload,
            draft=draft,
            antes_de_submeter=declarar(momento),
        )

    return publicar


def _montar(gestor, api_client, manager_headers, process_payload, *, momento, prefixo):
    from tests.fixtures.corte import regra

    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        geral=2,
        cut=regra(surplusCount=1),
        publicar=_publicador(momento),
    )


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """O recorte do 77/2026, com o Edital declarando o requerimento **na convocação**."""
    return _montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        momento="AT_CALL",
        prefixo="requerimento-029-processo-final",
    )


def convocada(cenario, gestor, chave="processo-final-chamada"):
    edital, _, inscricoes = cenario
    pessoa = inscricoes[0]
    declarado = convocar(edital, gestor, pessoa, idempotency_key=chave)
    return pessoa, Convocacao.objects.get(pk=declarado["id"])


def encerrar_o_processo(inscricao, estado):
    """O estado final gravado direto, como o teste dos documentos da `115` faz.

    Encerrar pelo comando exigiria antes encerrar o Edital, e o que se prende aqui é o estado, não
    o caminho até ele.
    """
    ProcessoSeletivo.objects.filter(editais__id=inscricao.edital_id).update(status=estado)


def relida(inscricao):
    """A Inscrição de novo do banco: a de antes pode ter o Processo ativo em cache."""
    return Inscricao.objects.select_related("edital").get(pk=inscricao.pk)


def enviar(inscricao):
    versao = preencher._conteudo(inscricao)
    return preencher.enviar(
        identidade=MARIA,
        inscricao=inscricao,
        versao_exibida_id=versao.id,
        declaracao_exibida=preencher.declaracao_publicada(versao.content),
        aceite=True,
    )


def declarar_e_enviar(inscricao, campos):
    preencher.abrir_rascunho(inscricao=inscricao)
    preencher.gravar(inscricao=inscricao, dados=campos, expected_revision=None)
    return enviar(inscricao)


def recusa_do_processo():
    """A recusa que os documentos e o desfecho já davam — a referência da comparação."""
    with pytest.raises(DomainError) as recusa:
        ensure_processo_accepts_changes(ProcessoSeletivo(status=ProcessoSeletivo.Status.ENCERRADO))
    return recusa.value


def assert_mesma_recusa(recusa):
    referencia = recusa_do_processo()
    assert (recusa.code, recusa.detail, recusa.status) == (
        referencia.code,
        referencia.detail,
        referencia.status,
    )


@pytest.mark.parametrize("estado", ESTADOS_FINAIS)
class TestNaConvocacao:
    def test_sem_rascunho_nao_abre_e_nada_e_gravado(self, cenario, gestor, estado):
        pessoa, _ = convocada(cenario, gestor)
        encerrar_o_processo(pessoa, estado)

        with pytest.raises(DomainError) as recusa:
            preencher.abrir_rascunho(inscricao=relida(pessoa))

        assert_mesma_recusa(recusa.value)
        assert not RequerimentoDeMatricula.objects.filter(inscricao=pessoa).exists()

    def test_o_rascunho_nao_grava_nem_envia_e_continua_legivel(
        self, cenario, gestor, campos_declarados, estado
    ):
        pessoa, _ = convocada(cenario, gestor)
        preencher.abrir_rascunho(inscricao=pessoa)
        preencher.gravar(inscricao=pessoa, dados=campos_declarados, expected_revision=None)
        antes = RequerimentoDeMatricula.objects.filter(inscricao=pessoa).values().get()
        encerrar_o_processo(pessoa, estado)
        pessoa = relida(pessoa)

        with pytest.raises(DomainError) as ao_gravar:
            preencher.gravar(inscricao=pessoa, dados={"bairro": "Outro"}, expected_revision=None)
        with pytest.raises(DomainError) as ao_enviar:
            enviar(pessoa)

        assert_mesma_recusa(ao_gravar.value)
        assert_mesma_recusa(ao_enviar.value)
        depois = RequerimentoDeMatricula.objects.filter(inscricao=pessoa).values().get()
        assert depois == antes, "o rascunho não é apagado, convertido nem alterado"
        # **A leitura fica**: abrir devolve o rascunho que existe, sem gravar, e o estado é um dos
        # cinco da FR-405 — não há sexto estado para o Processo encerrado.
        assert preencher.abrir_rascunho(inscricao=pessoa).id == antes["id"]
        apurado = preencher.apurar(pessoa)
        assert apurado.estado_de_leitura == nomes.EM_PREENCHIMENTO
        assert apurado.fechado_pelo_processo
        lido = leitura(apurado)
        assert not lido.pode_escrever
        assert lido.titulo == "O envio pelo portal está encerrado"
        assert f"foi {estado.lower()}" in lido.explicacao
        assert "prazo" not in lido.explicacao, "a causa é o Processo, e não o prazo"

    def test_o_enviado_continua_legivel_e_o_sucessor_e_recusado(
        self, cenario, gestor, campos_declarados, estado
    ):
        pessoa, _ = convocada(cenario, gestor)
        enviado = declarar_e_enviar(pessoa, campos_declarados)
        encerrar_o_processo(pessoa, estado)
        pessoa = relida(pessoa)

        with pytest.raises(DomainError) as ao_conferir:
            preencher.autorizacao_para_atualizar(pessoa)
        with pytest.raises(DomainError) as ao_atualizar:
            preencher.atualizar(
                inscricao=pessoa, dados={**campos_declarados, "bairro": "Praia do Canto"}
            )

        assert_mesma_recusa(ao_conferir.value)
        assert_mesma_recusa(ao_atualizar.value)
        assert RequerimentoDeMatricula.objects.filter(inscricao=pessoa).count() == 1
        vigente = exigencia.vigente_de(pessoa)
        assert vigente.id == enviado.id
        assert preencher.apurar(pessoa).estado_de_leitura == nomes.ESTADO_ENVIADO


def test_o_processo_vale_antes_do_prazo_decorrido(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """Com os dois juntos, a recusa é a do Processo (D-015 e D-020 da `118`).

    A do prazo diria *"a comissão vai decidir"*, e com o Processo encerrado ninguém decide.
    """
    from tests.fixtures import documentos_da_convocacao as cenarios

    certame = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=[cenarios.documentos_do_aluno()[0]],
        prefixo="processo-final-e-prazo",
        publicar=_publicador("AT_CALL"),
    )
    edital, _, _ = certame
    pessoa, convocacao = cenarios.convocar_primeira(
        certame, gestor, vencimento=timezone.now() + timedelta(minutes=1)
    )
    cenarios.comunicar(edital, gestor, convocacao)
    encerrar_o_processo(pessoa, ProcessoSeletivo.Status.ENCERRADO)

    with mock.patch("django.utils.timezone.now", return_value=timezone.now() + timedelta(days=2)):
        apurado = preencher.apurar(relida(pessoa))
        with pytest.raises(DomainError) as recusa:
            preencher.abrir_rascunho(inscricao=relida(pessoa))

    assert apurado.prazo_decorrido and apurado.fechado_pelo_processo
    assert_mesma_recusa(recusa.value)
    assert leitura(apurado).titulo == "O envio pelo portal está encerrado"


def test_edital_encerrado_com_processo_ativo_o_requerimento_segue_a_chamada(
    cenario, gestor, campos_declarados
):
    """O par de `test_edital_encerrado_com_convocacao_em_aberto_continua_recebendo_e_conferindo`.

    O encerramento do Edital admite convocação em aberto (FR-3534 da `113`), e a chamada continua
    com tudo o que ela autoriza a escrever (FR-3616 da `115`): o Requerimento também.
    """
    pessoa, convocacao = convocada(cenario, gestor)
    Edital.objects.filter(pk=pessoa.edital_id).update(status=Edital.Status.ENCERRADO)
    pessoa = relida(pessoa)

    enviado = declarar_e_enviar(pessoa, campos_declarados)
    sucessor = preencher.atualizar(
        inscricao=pessoa, dados={**campos_declarados, "bairro": "Praia do Canto"}
    )

    assert enviado.status == nomes.ENVIADO
    assert sucessor.convocacao_autorizadora_id == convocacao.id
    assert not preencher.apurar(pessoa).fechado_pelo_processo


class TestNaInscricaoNaoMuda:
    """A decisão de 04/11/2026 alcançou só o *na convocação*; o sucessor do *na inscrição*, com o
    Processo encerrado, ficou pendente — e, até ela, se comporta como antes."""

    @pytest.fixture
    def declarou_na_inscricao(
        self,
        db,
        gestor,
        api_client,
        manager_headers,
        process_payload,
        raiz_de_arquivos,
        campos_declarados,
    ):
        edital, _, inscricoes = _montar(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            momento="AT_ENROLLMENT",
            prefixo="requerimento-029-processo-final-na-inscricao",
        )
        pessoa = inscricoes[0]
        enviado = declarar_e_enviar(pessoa, campos_declarados)
        declarado = convocar(edital, gestor, pessoa, idempotency_key="na-inscricao-final")
        encerrar_o_processo(pessoa, ProcessoSeletivo.Status.ENCERRADO)
        return {
            "pessoa": relida(pessoa),
            "enviado": enviado,
            "chamada": Convocacao.objects.get(pk=declarado["id"]),
        }

    def test_o_enviado_continua_legivel(self, declarou_na_inscricao):
        apurado = preencher.apurar(declarou_na_inscricao["pessoa"])

        assert apurado.estado_de_leitura == nomes.ESTADO_ENVIADO
        assert not apurado.fechado_pelo_processo

    def test_o_sucessor_segue_a_regra_de_antes(self, declarou_na_inscricao, campos_declarados):
        pessoa = declarou_na_inscricao["pessoa"]

        anterior, chamada = preencher.autorizacao_para_atualizar(pessoa)
        sucessor = preencher.atualizar(
            inscricao=pessoa, dados={**campos_declarados, "logradouro": "Rua Nova"}
        )

        assert anterior.id == declarou_na_inscricao["enviado"].id
        assert chamada.id == declarou_na_inscricao["chamada"].id
        assert sucessor.requerimento_anterior_id == anterior.id


class TestAPagina:
    """FR-3754 da `118`: *"O envio pelo portal está encerrado"*, *"Voltar à convocação"*, sem
    formulário, e o `GET` não cria rascunho."""

    @pytest.fixture
    def encerrada(self, client, cenario, gestor):
        from tests.integration.requerimentos.test_orcamento_de_consulta import entrar_como

        pessoa, _ = convocada(cenario, gestor)
        encerrar_o_processo(pessoa, ProcessoSeletivo.Status.CANCELADO)
        entrar_como(client, pessoa)
        return pessoa

    def test_o_get_diz_que_o_envio_esta_encerrado_e_nao_cria_rascunho(self, client, encerrada):
        resposta = client.get(reverse("portal:requerimento", args=[encerrada.id]))

        assert resposta.status_code == 200
        pagina = resposta.content.decode()
        assert "O envio pelo portal está encerrado" in pagina
        assert "Este Processo Seletivo foi cancelado" in pagina
        assert reverse("portal:convocacao", args=[encerrada.id]) in pagina
        assert "Voltar à convocação" in pagina
        assert 'id="formulario-do-requerimento"' not in pagina
        assert not RequerimentoDeMatricula.objects.filter(inscricao=encerrada).exists()

    def test_o_post_montado_a_mao_nao_grava(self, client, encerrada, campos_declarados):
        resposta = client.post(
            reverse("portal:requerimento", args=[encerrada.id]),
            {**campos_declarados, "enviar": "1", "aceite": "1"},
        )

        assert resposta.status_code == 200
        assert "O envio pelo portal está encerrado" in resposta.content.decode()
        assert not RequerimentoDeMatricula.objects.filter(inscricao=encerrada).exists()

    def test_a_convocacao_nao_chama_ao_preenchimento(self, encerrada):
        from processo_seletivo.portal.views import _requerimento_da_convocacao

        pessoa = relida(encerrada)
        chamada = chamada_em_aberto(pessoa)
        conteudo = preencher._conteudo(pessoa).content

        assert _requerimento_da_convocacao(pessoa, chamada, conteudo) == ""

    def test_o_enviado_nao_oferece_conferir_e_atualizar(
        self, client, cenario, gestor, campos_declarados
    ):
        from tests.integration.requerimentos.test_orcamento_de_consulta import entrar_como

        pessoa, _ = convocada(cenario, gestor)
        declarar_e_enviar(pessoa, campos_declarados)
        encerrar_o_processo(pessoa, ProcessoSeletivo.Status.ENCERRADO)
        entrar_como(client, pessoa)

        pagina = client.get(reverse("portal:requerimento", args=[pessoa.id])).content.decode()

        assert "Declaração aceita" in pagina, "o enviado continua legível"
        assert "atualizando=1" not in pagina
