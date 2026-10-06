"""O caminho do candidato até a convocação e o Requerimento de Matrícula (059).

**A tela existia; o caminho, não.** A `019` criou a convocação do candidato escrevendo que ele *"não
deve depender da caixa de entrada para saber que foi chamado"*, e nenhuma tela do portal levava a
ela. A `029` criou o requerimento pedido *na convocação*, e nenhuma tela levava a ele. A mensagem
mandava a pessoa a "Minhas inscrições", que dizia só "Acompanhar".

Os testes aqui são de tela e de destino: **o texto certo, e o `href` certo**. Uma indicação sem
link, ou um link para a inscrição errada, passaria por qualquer verificação de domínio.
"""

import re
from datetime import timedelta
from pathlib import Path

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.portal.identidade import CHAVE_SESSAO
from processo_seletivo.requerimentos.application import preencher
from tests.fixtures.candidato import MARIA
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

RAIZ = Path(__file__).resolve().parents[2]


@pytest.fixture
def certame(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """O cenário da `019`: o Edital **não** pede o requerimento."""
    return montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="portal-059"
    )


@pytest.fixture
def certame_na_convocacao(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """O mesmo cenário, com o Edital pedindo o requerimento **na convocação** — o 69 e o 46.

    O gancho declara antes de o conteúdo congelar, que é o único momento em que dá: depois da
    publicação o conteúdo é imutável. É a forma de `test_portal_sucessao.py`.
    """
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.requerimento import declarar

    def publicar_declarando(api_client, manager_headers, process_payload, *, draft=None):
        return publish_original(
            api_client,
            manager_headers,
            process_payload,
            draft=draft,
            antes_de_submeter=declarar("AT_CALL"),
        )

    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="portal-059-req",
        publicar=publicar_declarando,
    )


def entrar_como(client, inscricao):
    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=inscricao.identity_subject, defaults={"created_at": timezone.now()}
    )
    sessao = client.session
    sessao[CHAVE_SESSAO] = str(registro.pk)
    sessao.save()


def primeira_da_fila(edital, inscricoes):
    """A inscrição que a fila chama primeiro — a fila guarda identificadores, e não linhas."""
    alvo = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"][0]
    return next(i for i in inscricoes if i.id == alvo)


def convocada(certame, gestor, client, chave, **kwargs):
    edital, _, inscricoes = certame
    pessoa = primeira_da_fila(edital, inscricoes)
    declarado = convocar(edital, gestor, pessoa.id, idempotency_key=chave, **kwargs)
    entrar_como(client, pessoa)
    return pessoa, declarado


def comunicar(edital, gestor, convocacao_id, chave):
    from processo_seletivo.convocacao.application.comunicar import comunicar as emitir

    return emitir(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao_id,
        idempotency_key=chave,
        correlation_id="teste-059",
    )


def responder(edital, gestor, convocacao_id, chave, especie=nomes_da_convocacao.ACEITE):
    return desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao_id,
        especie=especie,
        fundamento="Manifestação registrada em processo.",
        idempotency_key=chave,
        correlation_id="teste-059",
    )


def visivel(resposta):
    """O que a pessoa lê — sem a folha de estilo do `base.html`, cuja prosa cita o domínio."""
    corpo = resposta.content.decode()
    return re.sub(r"<style.*?</style>", " ", corpo, flags=re.S)


def item_da_lista(client, inscricao):
    """O `<li>` da inscrição em "Minhas inscrições" — a asserção é sobre **aquele** item."""
    pagina = visivel(client.get(reverse("portal:inscricoes")))
    itens = re.findall(r'<li class="selecao">.*?</li>', pagina, flags=re.S)
    destino = reverse("portal:inscricao", args=[inscricao.id])
    (item,) = [i for i in itens if f'href="{destino}"' in i]
    return item


def acao_principal(item):
    (acao,) = re.findall(r'<a class="principal" href="([^"]+)">([^<]+)</a>', item)
    return acao


class TestMinhasInscricoes:
    """`US1`, `FR-1089` a `FR-1091`."""

    def test_a_convocacao_aberta_e_indicada_e_leva_a_tela_dela(self, client, certame, gestor):
        edital, _, _ = certame
        pessoa, declarado = convocada(certame, gestor, client, "l-aberta")
        comunicar(edital, gestor, declarado["id"], "l-aberta-com")

        item = item_da_lista(client, pessoa)

        assert "Convocação aberta" in item
        assert acao_principal(item) == (
            reverse("portal:convocacao", args=[pessoa.id]),
            "Ver convocação",
        )
        assert reverse("portal:acompanhamento", args=[pessoa.id]) in item, (
            "o acompanhamento continua alcançável a partir do item (D-003)"
        )

    def test_antes_do_envio_a_convocacao_ja_e_indicada(self, client, certame, gestor):
        """O portal é o lugar onde a informação está sempre — inclusive antes da mensagem."""
        pessoa, _ = convocada(certame, gestor, client, "l-sem-envio")

        item = item_da_lista(client, pessoa)

        assert "Convocação aberta" in item
        assert acao_principal(item)[1] == "Ver convocação"

    def test_com_o_vencimento_decorrido_sem_desfecho_continua_aberta(self, client, certame, gestor):
        """O vencimento não decide nada sozinho (`FR-274`): a pessoa ainda pode ter atendido."""
        edital, _, _ = certame
        pessoa, declarado = convocada(
            certame,
            gestor,
            client,
            "l-vencida",
            vencimento=timezone.now() + timedelta(minutes=1),
        )
        comunicar(edital, gestor, declarado["id"], "l-vencida-com")

        from unittest import mock

        depois = timezone.now() + timedelta(days=2)
        with mock.patch("django.utils.timezone.now", return_value=depois):
            item = item_da_lista(client, pessoa)

        assert "Convocação aberta" in item

    def test_sem_convocacao_o_item_fica_como_estava(self, client, certame):
        _, _, inscricoes = certame
        pessoa = inscricoes[0]
        entrar_como(client, pessoa)

        item = item_da_lista(client, pessoa)

        assert "Convocação" not in item
        assert acao_principal(item) == (
            reverse("portal:acompanhamento", args=[pessoa.id]),
            "Acompanhar",
        )

    def test_a_concluida_vira_nota_e_a_acao_volta_a_ser_acompanhar(self, client, certame, gestor):
        """`FR-1091`, `D-004`: quem volta meses depois vê o que se registrou sem abrir nada."""
        edital, _, _ = certame
        pessoa, declarado = convocada(certame, gestor, client, "l-concluida")
        responder(edital, gestor, declarado["id"], "l-concluida-desf")

        item = item_da_lista(client, pessoa)

        assert "Convocação aberta" not in item
        assert "Convocação: Aceite" in item
        assert acao_principal(item) == (
            reverse("portal:acompanhamento", args=[pessoa.id]),
            "Acompanhar",
        )

    def test_a_mensagem_continua_apontando_minhas_inscricoes(self):
        """`FR-1104`, `D-009`: o endereço é montado na gestão, e a lista é o destino que serve aos
        gestos individuais e aos lotes da `050`. Mudar um deles em silêncio mandaria parte das
        pessoas a outro lugar — e é por isso que a regra fica presa aqui, e não num comentário.
        """
        views = (RAIZ / "processo_seletivo/interface/views.py").read_text(encoding="utf-8")
        enderecos = re.findall(r"endereco_do_portal=([^\n]+)", views)

        assert enderecos, "a varredura deixou de achar onde a gestão monta o endereço"
        assert set(enderecos) == {'request.build_absolute_uri(reverse("portal:inscricoes")),'}


class TestRequerimentoNaConvocacao:
    """`US2`, `FR-1096` a `FR-1099`, `D-007`."""

    PREENCHER = "Preencher Requerimento de Matrícula"
    CONFERIR = "Conferir o Requerimento de Matrícula enviado"

    def telas(self, client, pessoa):
        return [
            visivel(client.get(reverse("portal:convocacao", args=[pessoa.id]))),
            visivel(client.get(reverse("portal:acompanhamento", args=[pessoa.id]))),
        ]

    def test_convocada_sem_rascunho_ve_o_chamado_nas_duas_telas(
        self, client, certame_na_convocacao, gestor
    ):
        pessoa, _ = convocada(certame_na_convocacao, gestor, client, "r-aberto")
        destino = reverse("portal:requerimento", args=[pessoa.id])

        for pagina in self.telas(client, pessoa):
            assert f'<a class="principal" href="{destino}">{self.PREENCHER}</a>' in pagina
            assert self.CONFERIR not in pagina

    def test_com_rascunho_o_chamado_e_o_mesmo(
        self, client, certame_na_convocacao, gestor, campos_de_exemplo
    ):
        pessoa, _ = convocada(certame_na_convocacao, gestor, client, "r-rascunho")
        preencher.abrir_rascunho(inscricao=pessoa)
        preencher.gravar(inscricao=pessoa, dados=campos_de_exemplo, expected_revision=None)

        for pagina in self.telas(client, pessoa):
            assert self.PREENCHER in pagina

    def test_enviado_ve_a_conferencia_e_nao_o_chamado(
        self, client, certame_na_convocacao, gestor, campos_de_exemplo
    ):
        pessoa, declarado = convocada(certame_na_convocacao, gestor, client, "r-enviado")
        enviar(pessoa, campos_de_exemplo)
        destino = reverse("portal:requerimento", args=[pessoa.id])

        for pagina in self.telas(client, pessoa):
            assert f'href="{destino}">{self.CONFERIR}</a>' in pagina
            assert self.PREENCHER not in pagina

        # **Enviado é estado terminal de leitura** (`FR-406` da `029`): desfechada a chamada, o
        # que a pessoa mandou continua a um clique.
        edital, _, _ = certame_na_convocacao
        responder(edital, gestor, declarado["id"], "r-enviado-desf")
        for pagina in self.telas(client, pessoa):
            assert self.CONFERIR in pagina

    def test_desfechada_sem_envio_nao_oferece_nada(self, client, certame_na_convocacao, gestor):
        """Um botão que só levaria a recusa é pior do que nenhum (`FR-1098`)."""
        edital, _, _ = certame_na_convocacao
        pessoa, declarado = convocada(certame_na_convocacao, gestor, client, "r-desf")
        responder(
            edital,
            gestor,
            declarado["id"],
            "r-desf-desf",
            especie=nomes_da_convocacao.DESISTENCIA_EXPRESSA,
        )

        for pagina in self.telas(client, pessoa):
            assert self.PREENCHER not in pagina
            assert self.CONFERIR not in pagina
            assert reverse("portal:requerimento", args=[pessoa.id]) not in pagina

    def test_edital_que_nao_pede_nao_oferece_nada(self, client, certame, gestor):
        pessoa, _ = convocada(certame, gestor, client, "r-nao-pede")

        for pagina in self.telas(client, pessoa):
            assert reverse("portal:requerimento", args=[pessoa.id]) not in pagina


def enviar(pessoa, campos):
    preencher.abrir_rascunho(inscricao=pessoa)
    preencher.gravar(inscricao=pessoa, dados=campos, expected_revision=None)
    versao = preencher._conteudo(pessoa)
    return preencher.enviar(
        identidade=MARIA,
        inscricao=pessoa,
        versao_exibida_id=versao.id,
        declaracao_exibida=preencher.declaracao_publicada(versao.content),
        aceite=True,
    )


@pytest.fixture
def campos_de_exemplo():
    from tests.fixtures.requerimento import campos_de_exemplo

    return campos_de_exemplo()


class TestAcompanhamento:
    """`US3`, `FR-1093` a `FR-1095`, `FR-1103`."""

    def abrir(self, client, pessoa):
        return visivel(client.get(reverse("portal:acompanhamento", args=[pessoa.id])))

    def secao(self, pagina):
        (bloco,) = re.findall(
            r'<section class="painel convocacao-da-inscricao".*?</section>', pagina, flags=re.S
        )
        return bloco

    def test_a_secao_mostra_a_chamada_o_prazo_e_o_caminho(self, client, certame, gestor):
        edital, _, _ = certame
        vencimento = timezone.localtime(timezone.now() + timedelta(days=4))
        pessoa, declarado = convocada(certame, gestor, client, "a-aberta", vencimento=vencimento)
        comunicar(edital, gestor, declarado["id"], "a-aberta-com")

        secao = self.secao(self.abrir(client, pessoa))

        assert "Para vaga inicial" in secao
        assert vencimento.strftime("%d/%m/%Y %H:%M") in secao
        assert "contado do envio da comunicação" in secao
        assert f'href="{reverse("portal:convocacao", args=[pessoa.id])}">Ver convocação</a>' in (
            secao
        )

    def test_antes_do_envio_diz_que_o_prazo_nao_comecou(self, client, certame, gestor):
        pessoa, _ = convocada(certame, gestor, client, "a-sem-envio")

        secao = self.secao(self.abrir(client, pessoa))

        assert "ainda não foi enviada" in secao
        assert "não começou a correr" in secao

    def test_vencimento_decorrido_nao_decide_nada_sozinho(self, client, certame, gestor):
        edital, _, _ = certame
        pessoa, declarado = convocada(
            certame,
            gestor,
            client,
            "a-vencida",
            vencimento=timezone.now() + timedelta(minutes=1),
        )
        comunicar(edital, gestor, declarado["id"], "a-vencida-com")

        from unittest import mock

        with mock.patch(
            "django.utils.timezone.now", return_value=timezone.now() + timedelta(days=2)
        ):
            secao = self.secao(self.abrir(client, pessoa))

        assert "já passou" in secao
        assert "não decide nada sozinho" in secao

    def test_a_concluida_continua_consultavel(self, client, certame, gestor):
        edital, _, _ = certame
        pessoa, declarado = convocada(certame, gestor, client, "a-concluida")
        responder(edital, gestor, declarado["id"], "a-concluida-desf")

        secao = self.secao(self.abrir(client, pessoa))

        assert "Situação registrada: Aceite" in secao
        assert reverse("portal:convocacao", args=[pessoa.id]) in secao

    def test_a_sucessora_ocupa_o_lugar_da_sucedida(self, client, certame, gestor):
        """`FR-1100`: a lista, o acompanhamento e a tela mostram a mesma convocação."""
        edital, _, _ = certame
        antigo = timezone.localtime(timezone.now() + timedelta(days=3))
        novo = timezone.localtime(timezone.now() + timedelta(days=9))
        pessoa, _ = convocada(certame, gestor, client, "a-raiz", vencimento=antigo)
        convocar(
            edital,
            gestor,
            pessoa.id,
            vencimento=novo,
            motivo="Vencimento informado com o dia errado.",
            idempotency_key="a-sucessora",
        )

        secao = self.secao(self.abrir(client, pessoa))
        tela = visivel(client.get(reverse("portal:convocacao", args=[pessoa.id])))

        for pagina in (secao, tela):
            assert novo.strftime("%d/%m/%Y %H:%M") in pagina
            assert antigo.strftime("%d/%m/%Y %H:%M") not in pagina

    def test_sem_convocacao_nao_ha_secao(self, client, certame):
        _, _, inscricoes = certame
        entrar_como(client, inscricoes[0])

        pagina = self.abrir(client, inscricoes[0])

        assert "convocacao-da-inscricao" not in pagina
        assert reverse("portal:convocacao", args=[inscricoes[0].id]) not in pagina

    def test_so_a_tela_da_convocacao_registra_leitura(self, client, certame, gestor):
        """`FR-1103`, `D-008`: a trilha responde "a pessoa abriu a convocação?", e só isso."""
        pessoa, _ = convocada(certame, gestor, client, "a-trilha")

        def leituras():
            return RegistroAuditoria.objects.filter(operation="CONVOCACAO_LER").count()

        antes = leituras()
        client.get(reverse("portal:inscricoes"))
        client.get(reverse("portal:acompanhamento", args=[pessoa.id]))
        assert leituras() == antes

        client.get(reverse("portal:convocacao", args=[pessoa.id]))
        assert leituras() == antes + 1


class TestTelaEstreita:
    """`UX-146`: o que esta feature escreve não estoura 375 px — o molde da `019`."""

    TEMPLATES = RAIZ / "processo_seletivo/portal/templates/portal"

    @pytest.mark.parametrize(
        "nome",
        [
            "inscricoes.html",
            "acompanhamento.html",
            "_convocacao_da_inscricao.html",
            "_chamado_do_requerimento.html",
        ],
    )
    def test_sem_tabela_e_sem_estilo_embutido(self, nome):
        marcacao = (self.TEMPLATES / nome).read_text(encoding="utf-8")

        assert "<table" not in marcacao, "tabela é o que estoura a viewport estreita"
        assert "style=" not in marcacao, "nenhum estilo embutido, e portanto nenhuma largura fixa"

    def test_a_secao_sai_como_lista_de_definicao(self, client, certame, gestor):
        pessoa, _ = convocada(certame, gestor, client, "e-375")

        pagina = visivel(client.get(reverse("portal:acompanhamento", args=[pessoa.id])))

        assert '<meta name="viewport"' in client.get(reverse("portal:inscricoes")).content.decode()
        assert "<dl" in pagina
