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

        # Sem documento pedido, a estrutura da 118 com as três mudanças da 121 (FR-3868): o título
        # por estado, que diz o que "Você foi convocada(o)" dizia, e o vencimento nos dados.
        assert "<h1" in pagina and "Você tem uma convocação!" in pagina
        assert "Você foi convocada(o)" not in pagina
        # O formato único do prazo (FR-3747 da `118`).
        assert vencimento.strftime("%d/%m/%Y, às %Hh%M") in pagina
        assert "O que fazer" in pagina

    def test_com_o_prazo_correndo_o_cartao_diz_a_data_o_dia_e_a_contagem(
        self, client, certame, gestor, settings
    ):
        """FR-3861 e FR-3868: o cartão do prazo no lugar da linha do prazo, também sem documento."""
        from datetime import timedelta

        from processo_seletivo.convocacao.application.comunicar import comunicar
        from processo_seletivo.portal import obrigacoes

        settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
        edital, _, inscricoes = certame
        chamada = proximo(edital)
        vencimento = timezone.now() + timedelta(days=4)
        convocada = convocar(
            edital, gestor, chamada, vencimento=vencimento, idempotency_key="portal-cartao"
        )
        comunicar(
            actor=gestor,
            processo_id=edital.processo_id,
            convocacao_id=convocada["id"],
            idempotency_key="portal-cartao-com",
            correlation_id="teste",
        )
        titular = next(i for i in inscricoes if i.id == chamada)
        entrar_como(client, titular)

        pagina = abrir(client, titular).content.decode()
        cartao = pagina.split('class="cartao-do-prazo"', 1)[1].split("</div>", 1)[0]
        prazo = obrigacoes.apresentado(vencimento, timezone.now())

        assert "Prazo desta convocação" in cartao
        assert f'<p class="data-do-prazo">{prazo.ate}</p>' in cartao
        assert f"{prazo.dia_da_semana} · " in cartao and "faltam 4 dias" in cartao
        assert "Você foi convocada(o)" not in pagina
        assert pagina.count("Prazo desta convocação") == 1, "o prazo é dito uma vez só"

    def test_antes_do_envio_a_tela_diz_que_o_prazo_nao_comecou(self, client, certame, gestor):
        """`R-009`, e aqui ele é o que impede a pessoa de contar um prazo que não corre."""
        edital, _, inscricoes = certame
        chamada = proximo(edital)
        convocar(edital, gestor, chamada, idempotency_key="portal-sem-envio")
        titular = next(i for i in inscricoes if i.id == chamada)
        entrar_como(client, titular)

        pagina = abrir(client, titular).content.decode()

        assert "prazo ainda não começou a correr" in pagina

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


def test_a_leitura_entra_na_trilha_do_edital(client, certame, gestor):
    """`FR-288b`: o acesso é **registrado**, e a pergunta que ele responde é auditável.

    **Trilha, e não linha de log.** *"A pessoa teve como saber?"* é respondida na mesma tela em que
    se responde por uma publicação — e não num arquivo do servidor que ninguém audita.

    O ator é o candidato, com o conjunto de permissões **vazio**: é o que impede a trilha de
    afirmar autoridade que ele não tem.
    """
    from processo_seletivo.auditoria.models import RegistroAuditoria

    edital, _, inscricoes = certame
    chamada = proximo(edital)
    convocada = convocar(edital, gestor, chamada, idempotency_key="trilha-portal")
    titular = next(i for i in inscricoes if i.id == chamada)
    entrar_como(client, titular)

    abrir(client, titular)

    registro = RegistroAuditoria.objects.filter(operation="CONVOCACAO_LER").latest("occurred_at")
    assert str(registro.aggregate_id) == convocada["id"]
    assert registro.actor_subject == titular.identity_subject
    assert registro.permission == "", "o candidato não carrega permissão institucional nenhuma"
    assert "não inicia nem reinicia prazo" in registro.reason


def test_a_leitura_de_quem_nao_foi_chamado_nao_enche_a_trilha(client, certame):
    """Auditar a ausência produziria linhas que não respondem pergunta nenhuma."""
    from processo_seletivo.auditoria.models import RegistroAuditoria

    _, _, inscricoes = certame
    entrar_como(client, inscricoes[0])

    abrir(client, inscricoes[0])

    assert not RegistroAuditoria.objects.filter(operation="CONVOCACAO_LER").exists()


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


# --- A chamada da 121 (FR-3858 a FR-3869) -------------------------------------------------------


@pytest.fixture
def fx(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    from tests.fixtures import jornada_do_convocado as jornada

    return jornada.Montagem(gestor, api_client, manager_headers, process_payload)


def _main(client, cenario, pessoa=None):
    import re

    with cenario.relogio():
        entrar_como(client, pessoa or cenario.pessoa)
        resposta = client.get(reverse("portal:convocacao", args=[cenario.pessoa.id]))
    assert resposta.status_code == 200
    return re.search(r"<main[^>]*>(.*)</main>", resposta.content.decode(), re.S).group(1)


def _texto(html):
    import re

    return " ".join(re.sub(r"<[^>]+>", " ", html).split())


def _montar(fx, letra):
    from tests.fixtures import jornada_do_convocado as jornada

    return jornada.montar(letra, fx)


# A ordem da FR-3859, pelas marcas que o parcial da chamada escreve, e o andamento logo depois.
ORDEM_DA_CHAMADA = (
    'class="contexto-da-chamada"',
    'id="titulo-da-chamada"',
    'class="etapa-da-chamada"',
    'class="cartao-do-prazo"',
    'class="resumo-da-chamada"',
    'class="acao-da-chamada"',
    'class="consequencia"',
    'class="ressalva"',
    'id="andamento"',
)
SO_DA_CHAMADA_ABERTA = (
    'class="etapa-da-chamada"',
    'class="cartao-do-prazo"',
    'class="acao-da-chamada"',
    'class="consequencia"',
    'class="ressalva"',
    'id="andamento"',
)


class TestAChamada:
    def test_a_ordem_da_chamada(self, client, fx):
        """FR-3859, SC-1151: contexto, título, etapa, prazo, resumo, ação, consequência e ressalva,
        e o andamento antes dos cartões e dos dados do ato."""
        cenario = _montar(fx, "C1")
        pagina = _main(client, cenario)

        posicoes = [pagina.index(marca) for marca in ORDEM_DA_CHAMADA]
        assert posicoes == sorted(posicoes), posicoes
        assert pagina.index('id="andamento"') < pagina.index('id="o-que-falta"')
        assert pagina.index('id="o-que-falta"') < pagina.index('id="sobre-esta-convocacao"')
        assert pagina.count("<h1") == 1
        assert "Você tem uma convocação!" in _texto(pagina)
        contexto = pagina.split('class="contexto-da-chamada">', 1)[1].split("</p>", 1)[0]
        edital = cenario.edital
        assert contexto.endswith(f" · Edital {edital.number}/{edital.year}"), contexto

    @pytest.mark.parametrize("letra", ["C1", "G"])
    def test_o_titulo_nao_se_repete_num_h2(self, client, fx, letra):
        """D-005: o título por estado absorve o do bloco 1."""
        import re

        pagina = _main(client, _montar(fx, letra))
        titulo = _texto(re.search(r"<h1[^>]*>(.*?)</h1>", pagina, re.S).group(1))
        secoes = [_texto(h) for h in re.findall(r"<h2[^>]*>(.*?)</h2>", pagina, re.S)]
        assert titulo not in secoes
        assert "O prazo terminou" not in secoes and "O que fazer agora" not in secoes

    @pytest.mark.parametrize(
        ("letra", "vezes"), [("C1", 1), ("K", 0), ("G", 0), ("I1", 0), ("M", 0)]
    )
    def test_a_consequencia_uma_vez_so(self, client, fx, letra, vezes):
        """FR-3864, FR-1177 da 063: a mesma frase, na mesma condição, e uma vez só."""
        from processo_seletivo.portal import situacao

        pagina = _texto(_main(client, _montar(fx, letra)))

        assert pagina.count(situacao.NAO_ATENDIMENTO_PODE_SER_REGISTRADO) == vezes

    @pytest.mark.parametrize(
        ("letra", "titulo"),
        [
            ("G", "O prazo desta convocação terminou"),
            ("M", "O envio pelo portal está encerrado"),
            ("I1", "Resultado da sua convocação"),
        ],
    )
    def test_fechada_so_conta_o_que_houve(self, client, fx, letra, titulo):
        """FR-3867: nenhuma etapa, contagem, ação, consequência, ressalva ou andamento."""
        pagina = _main(client, _montar(fx, letra))

        assert f'<h1 id="titulo-da-chamada">{titulo}</h1>' in pagina
        for marca in SO_DA_CHAMADA_ABERTA:
            assert marca not in pagina, marca
        assert "Ver o que preciso fazer" not in pagina

    def test_aberta_mantem_os_blocos_da_118_depois_do_andamento(self, client, fx):
        """FR-3866: *O que falta*, *O que você já apresentou* e *Sobre esta convocação*."""
        pagina = _main(client, _montar(fx, "F"))

        marcas = (
            'id="andamento"',
            'id="o-que-falta"',
            'id="o-que-voce-ja-apresentou"',
            'id="sobre-esta-convocacao"',
        )
        posicoes = [pagina.index(marca) for marca in marcas]
        assert posicoes == sorted(posicoes)

    def test_sem_documento_a_chamada_sem_a_frase_antiga(self, client, fx):
        """FR-3868: o título e o cartão do prazo, sem "Você foi convocada(o)"."""
        pagina = _main(client, _montar(fx, "B"))

        assert '<h1 id="titulo-da-chamada">Você tem uma convocação!</h1>' in pagina
        assert 'class="cartao-do-prazo"' in pagina
        assert "Você foi convocada(o)" not in pagina
        assert 'class="etapa-da-chamada"' not in pagina, "a etapa é da chamada com documento"

    def test_sem_convocacao_o_titulo_de_hoje(self, client, certame):
        """Caso-limite: aguardando ou não convocado, o título e o texto de hoje."""
        _, _, inscricoes = certame
        entrar_como(client, inscricoes[0])

        pagina = abrir(client, inscricoes[0]).content.decode()

        assert "<h1>Convocação</h1>" in pagina
        assert "chamada-da-convocacao" not in pagina


class TestACorrecaoNoPortal:
    """FR-3869, R-008, D-008: o cartão diz qual prazo vale, e os dados do ato, o que foi
    substituído."""

    PROIBIDOS = ("novo prazo", "prorrogação", "motivo")

    def _corrigir(self, cenario, gestor, chave):
        from processo_seletivo.convocacao.models import Convocacao
        from tests.integration.convocacao.test_correcao_da_convocacao import MOTIVO, corrigir

        corrigir(cenario.edital, gestor, cenario.convocacao, chave=chave)
        cenario.convocacao = Convocacao.objects.get(convocacao_anterior=cenario.convocacao)
        return MOTIVO

    def test_comunicada(self, client, fx, gestor):
        from processo_seletivo.convocacao.models import ComunicacaoEmitida
        from processo_seletivo.portal import obrigacoes

        cenario = _montar(fx, "A")
        anterior = cenario.convocacao
        motivo = self._corrigir(cenario, gestor, "p121-comunicada")
        enviada = ComunicacaoEmitida.objects.get(convocacao=anterior, resultado="ENVIADA")

        pagina = _texto(_main(client, cenario))

        assert "Convocação corrigida: este é o prazo válido." in pagina
        assert pagina.index("Convocação corrigida") < pagina.index(
            obrigacoes.ate(cenario.convocacao.vencimento)
        ), "acima da data"
        assert (
            f"Convocação substituída Enviada em {obrigacoes.data_e_hora(enviada.enviado_em)}, "
            f"com prazo {obrigacoes.ate(anterior.vencimento)}. Esse prazo não vale mais."
        ) in pagina
        assert motivo not in pagina
        for proibido in self.PROIBIDOS:
            assert proibido not in pagina.lower()

    def test_nao_comunicada(self, client, fx, gestor):
        from processo_seletivo.portal import obrigacoes

        cenario = _montar(fx, "K")
        anterior = cenario.convocacao
        self._corrigir(cenario, gestor, "p121-nao-comunicada")

        pagina = _texto(_main(client, cenario))

        assert (
            "Convocação substituída Não comunicada. O prazo registrado era "
            f"{obrigacoes.ate(anterior.vencimento)}, e não vale mais."
        ) in pagina

    def test_por_publicacao(self, client, fx, gestor):
        from django.utils import timezone as tz

        from processo_seletivo.convocacao.models import ComunicacaoEmitida

        cenario = _montar(fx, "K")
        ComunicacaoEmitida.objects.create(
            convocacao=cenario.convocacao,
            forma="PUBLICATION",
            referencia_da_publicacao="ifes.edu.br/editais, 05/11/2026",
            enviado_em=tz.now(),
            resultado="ENVIADA",
        )
        self._corrigir(cenario, gestor, "p121-publicada")

        pagina = _texto(_main(client, cenario))

        assert "Convocação substituída Publicada em ifes.edu.br/editais, 05/11/2026, com prazo" in (
            pagina
        )

    def test_a_linha_fica_em_todos_os_estados_e_a_frase_so_aberta(self, client, fx, gestor):
        from processo_seletivo.convocacao.domain import nomes
        from tests.fixtures import documentos_da_convocacao as cenarios

        cenario = _montar(fx, "A")
        self._corrigir(cenario, gestor, "p121-desfecho")
        cenarios.desfechar(
            cenario.edital,
            gestor,
            cenario.convocacao,
            nomes.INDEFERIMENTO,
            chave="p121-desfecho-d",
            fundamento="Documentação exigida na convocação não atendida.",
        )

        pagina = _texto(_main(client, cenario))

        assert "Convocação substituída Enviada em" in pagina
        assert "Convocação corrigida: este é o prazo válido." not in pagina

    def test_a_falha_no_meio_descreve_a_imediatamente_anterior(self, client, fx, gestor, settings):
        """D-008: A enviada, B falhada, C vigente — os dados do ato descrevem **B**."""
        from processo_seletivo.convocacao.models import Convocacao

        cenario = _montar(fx, "A")
        settings.EMAIL_BACKEND = "tests.unit.convocacao.test_mensagem.CorreioQueEngole"
        self._corrigir(cenario, gestor, "p121-b")
        b = cenario.convocacao
        settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
        self._corrigir(cenario, gestor, "p121-c")
        assert Convocacao.objects.get(id=cenario.convocacao.id).convocacao_anterior_id == b.id

        pagina = _texto(_main(client, cenario))

        assert "Convocação substituída Não comunicada." in pagina


def _frases_da_sc_1150(letra):
    """As respostas que a chamada dá pelo próprio texto, por cenário (SC-1150): o título, a etapa
    (abertos), o prazo ou o estado dele, o resumo ou o desfecho, e, abertos, a consequência e a
    ressalva; em P7, o selo *"Conferido"* nos cartões."""
    from processo_seletivo.convocacao.domain import nomes
    from processo_seletivo.portal import obrigacoes, situacao

    aberta = [situacao.NAO_ATENDIMENTO_PODE_SER_REGISTRADO, obrigacoes.RESSALVA_DA_MATRICULA]
    etapa = obrigacoes.ETAPAS[(True, True)]
    return {
        "C1": [
            "Você tem uma convocação!",
            etapa,
            "Prazo desta convocação",
            "Você ainda precisa enviar 4 documentos e preencher o Requerimento de Matrícula.",
            "Ver o que preciso fazer",
            *aberta,
        ],
        "F": [
            "Você tem uma convocação!",
            etapa,
            "Prazo desta convocação",
            "Você ainda precisa corrigir 1 documento e enviar 1 documento.",
            "Ver o que preciso fazer",
            "Conferido",
            *aberta,
        ],
        "G": [
            "O prazo desta convocação terminou",
            "O prazo terminou em",
            "Até o prazo, ficou assim",
        ],
        "I1": [
            "Resultado da sua convocação",
            f"Resultado registrado: {situacao.DESFECHOS[nomes.ACEITE]}",
            # A frase simples do aceite diz o que o registro não é (156, FR-6406; FR-6206 da `154`).
            "A comissão registrou o resultado da sua convocação em",
            "Este registro não é matrícula, bolsa nem contrato.",
            "Fundamento do registro",
            obrigacoes.ACEITE,
            "Conferido",
        ],
        "corr": [
            "Você tem uma convocação!",
            obrigacoes.CORRIGIDA,
            "Convocação substituída Enviada em",
            "Ver o que preciso fazer",
            obrigacoes.RESSALVA_DO_RESULTADO,
        ],
    }[letra]


@pytest.mark.parametrize("letra", ["C1", "F", "G", "I1", "corr"])
def test_a_chamada_responde_pelo_proprio_texto(client, fx, gestor, letra):
    """SC-1150: a lista de frases por cenário, lida na tela."""
    from processo_seletivo.convocacao.models import Convocacao

    if letra == "corr":
        from tests.integration.convocacao.test_correcao_da_convocacao import corrigir

        cenario = _montar(fx, "A")
        corrigir(cenario.edital, gestor, cenario.convocacao, chave="sc1150-corr")
        cenario.convocacao = Convocacao.objects.get(convocacao_anterior=cenario.convocacao)
    else:
        cenario = _montar(fx, letra)

    pagina = _texto(_main(client, cenario))

    faltam = [frase for frase in _frases_da_sc_1150(letra) if frase not in pagina]
    assert faltam == []
