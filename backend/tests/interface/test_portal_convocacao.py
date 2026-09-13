"""A convocação vista pelo candidato, no canal do ator dele (019, `US6`, `T066`, `T067`).

**O candidato não deve depender da caixa de entrada para saber que foi chamado.** Mensagem se
perde, cai em spam, chega a um endereço que a pessoa não usa mais — e o que está em jogo é a vaga
dela. Esta página é o lugar onde a informação está sempre.

**As duas ausências não são a mesma coisa**, e é a `FR-294`: *"não há convocação"* diz que o
certame ainda não chegou a essa fase; *"você não foi chamado"* diz que chegou e a pessoa não estava
entre os chamados. Colapsá-las faria quem ainda tem chance ler que não tem — e parar de acompanhar.
"""

from pathlib import Path

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.portal.identidade import CHAVE_SESSAO
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

# O que esta tela não diz, e por quê — as mesmas proibições da tela de gestão, porque a pessoa que
# lê aqui é justamente a que sofreria a consequência de uma afirmação falsa.
PROIBIDAS = (
    "recebido em",
    "recebida em",
    "lido em",
    "entregue em",
    "direito à vaga",
    "vaga garantida",
)


@pytest.fixture
def certame(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="portal-019"
    )


def entrar_como(client, inscricao):
    """A sessão do portal identificada como a titular — pelo registro, e não por declaração."""
    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=inscricao.identity_subject, defaults={"created_at": timezone.now()}
    )
    sessao = client.session
    sessao[CHAVE_SESSAO] = str(registro.pk)
    sessao.save()
    return registro


def abrir(client, inscricao):
    return client.get(reverse("portal:convocacao", args=[inscricao.id]))


def proximo(edital):
    return selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"][0]


class TestAsDuasAusencias:
    def test_sem_convocacao_no_certame_a_tela_diz_que_nao_ha(self, client, certame):
        """O certame ainda não chegou a essa fase — e quem lê continua acompanhando."""
        _, _, inscricoes = certame
        entrar_como(client, inscricoes[0])

        pagina = abrir(client, inscricoes[0]).content.decode()

        assert "não há convocação" in pagina
        assert "não foi chamado" not in pagina

    def test_com_convocacao_de_outro_a_tela_diz_que_esta_pessoa_nao_foi_chamada(
        self, client, certame, gestor
    ):
        """Chegou a fase, e ela não estava entre os chamados. **É outra informação.**"""
        edital, _, inscricoes = certame
        chamada = proximo(edital)
        convocar(edital, gestor, chamada, idempotency_key="portal-outro")
        outra = next(i for i in inscricoes if i.id != chamada)
        entrar_como(client, outra)

        pagina = abrir(client, outra).content.decode()

        assert "não foi chamado" in pagina
        assert "não há convocação" not in pagina

    def test_a_convocacao_de_terceiro_nao_atravessa(self, client, certame, gestor):
        """`FR-085` da `010`: titularidade é conferida no servidor, e a recusa não confirma nada."""
        edital, _, inscricoes = certame
        chamada = proximo(edital)
        convocar(edital, gestor, chamada, idempotency_key="portal-terceiro")
        outra = next(i for i in inscricoes if i.id != chamada)
        entrar_como(client, outra)

        resposta = client.get(reverse("portal:convocacao", args=[chamada]))

        assert resposta.status_code == 404


class TestAConvocacaoDaPropriaPessoa:
    def test_a_tela_mostra_a_chamada_o_prazo_e_o_que_fazer(self, client, certame, gestor):
        from datetime import timedelta

        edital, _, inscricoes = certame
        chamada = proximo(edital)
        vencimento = timezone.localtime(timezone.now() + timedelta(days=4))
        convocar(edital, gestor, chamada, vencimento=vencimento, idempotency_key="portal-minha")
        titular = next(i for i in inscricoes if i.id == chamada)
        entrar_como(client, titular)

        pagina = abrir(client, titular).content.decode()

        assert "Você foi convocada(o)" in pagina
        assert vencimento.strftime("%d/%m/%Y %H:%M") in pagina
        assert "O que fazer" in pagina

    def test_antes_do_envio_a_tela_diz_que_o_prazo_nao_comecou(self, client, certame, gestor):
        """`R-009`, e aqui ele é o que impede a pessoa de contar um prazo que não corre."""
        edital, _, inscricoes = certame
        chamada = proximo(edital)
        convocar(edital, gestor, chamada, idempotency_key="portal-sem-envio")
        titular = next(i for i in inscricoes if i.id == chamada)
        entrar_como(client, titular)

        pagina = abrir(client, titular).content.decode()

        assert "prazo não começou a correr" in pagina

    def test_a_tela_escreve_enviada_em_e_nunca_recebida_em(self, client, certame, gestor, settings):
        """`UX-039`, `T067`: o sistema afirma o envio, e não afirma o recebimento.

        A distância entre os dois é real, e é ela que o Edital resolve dando prazo em dias úteis a
        partir do recebimento. Afirmá-la aqui seria o sistema decidindo um fato que ele não observa.
        """
        from processo_seletivo.convocacao.application.comunicar import comunicar

        settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
        edital, _, inscricoes = certame
        chamada = proximo(edital)
        convocada = convocar(edital, gestor, chamada, idempotency_key="portal-enviada")
        comunicar(
            actor=gestor,
            processo_id=edital.processo_id,
            convocacao_id=convocada["id"],
            idempotency_key="portal-enviada-comunicar",
            correlation_id="teste",
        )
        titular = next(i for i in inscricoes if i.id == chamada)
        entrar_como(client, titular)

        pagina = abrir(client, titular).content.decode()

        assert "Comunicação enviada em" in pagina

    @pytest.mark.parametrize("proibida", PROIBIDAS)
    def test_a_tela_nao_afirma_recebimento_nem_promete_a_vaga(
        self, client, certame, gestor, proibida
    ):
        edital, _, inscricoes = certame
        chamada = proximo(edital)
        convocar(edital, gestor, chamada, idempotency_key=f"portal-vocab-{abs(hash(proibida))}")
        titular = next(i for i in inscricoes if i.id == chamada)
        entrar_como(client, titular)

        pagina = abrir(client, titular).content.decode().lower()

        assert proibida.lower() not in pagina


def test_ler_a_convocacao_nao_move_o_relogio(client, certame, gestor, settings):
    """`FR-288b`: abrir a página não é o envio nem o recebimento.

    **O acesso fica na trilha, e o prazo fica onde estava.** Se ler iniciasse ou reiniciasse o
    prazo, a pessoa seria punida por conferir — e quem não conferisse ficaria em vantagem.
    """
    from processo_seletivo.convocacao.application.comunicar import comunicar
    from processo_seletivo.convocacao.models import ComunicacaoEmitida

    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    edital, _, inscricoes = certame
    chamada = proximo(edital)
    convocada = convocar(edital, gestor, chamada, idempotency_key="portal-relogio")
    comunicar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocada["id"],
        idempotency_key="portal-relogio-comunicar",
        correlation_id="teste",
    )
    emitida = ComunicacaoEmitida.objects.get(convocacao_id=convocada["id"])
    antes = emitida.enviado_em
    titular = next(i for i in inscricoes if i.id == chamada)
    entrar_como(client, titular)

    abrir(client, titular)
    abrir(client, titular)

    emitida.refresh_from_db()
    assert emitida.enviado_em == antes, "ler não reescreve o instante de onde o prazo corre"
    assert ComunicacaoEmitida.objects.filter(convocacao_id=convocada["id"]).count() == 1


def test_a_tela_cabe_em_375_px(client, certame, gestor):
    """`T071`: verificada agora, e não no fim da fila — como a `013` deixou e pagou.

    **O alvo do portal é o celular.** A verificação aqui é estrutural: a página não traz tabela nem
    bloco de largura fixa, que são as duas coisas que estouram a viewport estreita e que só se
    descobre tarde. O `base.html` do portal já responde; o que esta tela não pode fazer é quebrá-lo.
    """
    edital, _, inscricoes = certame
    chamada = proximo(edital)
    convocar(edital, gestor, chamada, idempotency_key="portal-375")
    titular = next(i for i in inscricoes if i.id == chamada)
    entrar_como(client, titular)

    pagina = abrir(client, titular).content.decode()

    assert '<meta name="viewport"' in pagina, "a base do portal declara a viewport do celular"
    assert "<table" not in pagina, "tabela é o que estoura a viewport estreita"
    assert "<dl" in pagina, "a chamada sai como lista de definição, que reflui"
    # **A asserção é sobre o que esta tela escreve, e não sobre o CSS da base.** Varrer a página
    # inteira por `width:` acusaria a folha de estilo compartilhada — e o teste passaria a falhar
    # por prosa alheia, que é o modo de falha que este repositório já registrou uma vez.
    marcacao = Path("processo_seletivo/portal/templates/portal/convocacao.html").read_text(
        encoding="utf-8"
    )
    assert "style=" not in marcacao, "nenhum estilo embutido, e portanto nenhuma largura fixa"
    assert "<table" not in marcacao
