"""A tela do recorte da convocação: os estados distintos, a confirmação, e o que ela não diz (019).

**O que só um teste de interface alcança** é a prosa. O campo que não existe é metade da garantia da
`UX-039`; a outra metade é esta — porque uma tela mente dizendo *"recebido em"* sem precisar de
coluna nenhuma para isso.

**E a confirmação antes do ato irreversível** (`UX-036`) só existe aqui: o domínio não tem tela, e
foi o defeito `E2E16-004` da `016` — três ações voltando para a mesma página com um aviso único, e
quem acabara de desfechar lendo "Apuração emitida".
"""

import pytest
from django.urls import reverse

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.domain import nomes
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

# As palavras que esta feature não diz, e a razão de cada uma:
#
# - *recebido*, *lido*, *entregue*: o sistema registra que **enviou** (`UX-039`, `FR-288a`);
# - *direito à vaga*: convocar chama para cumprir uma etapa, e não entrega a vaga (`FR-292c`).
PROIBIDAS = ("recebido em", "recebida em", "lido em", "entregue em", "direito à vaga")


@pytest.fixture
def cenario_da_tela(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="interface-019"
    )


def abrir(client, edital):
    return client.get(reverse("interface:convocacao", args=[edital.id, MARCO]))


def proximo(edital):
    contexto = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    return contexto["fila"][0]


def test_a_rota_pende_do_marco_como_a_da_ocupacao():
    """O recorte é o do marco, e o `?lista=` escolhe qual — o mesmo precedente da `016`."""
    caminho = reverse(
        "interface:convocacao",
        args=["00000000-0000-4000-8000-000000000001", "00000000-0000-4000-8000-000000000002"],
    )

    assert caminho.endswith("/convocacao")
    assert "/marcos/" in caminho


def test_as_rotas_de_leitura_e_de_ato_sao_distintas():
    edital = "00000000-0000-4000-8000-000000000001"
    marco = "00000000-0000-4000-8000-000000000002"

    leitura = reverse("interface:convocacao", args=[edital, marco])
    ato = reverse("interface:convocar", args=[edital, marco])

    assert leitura != ato
    assert ato.endswith("/convocacao/convocar")


class TestOsEstadosDistintos:
    def test_a_tela_mostra_os_quatro_numeros_da_016(self, client, seletor_ligado, cenario_da_tela):
        """**Os quatro juntos** (`UX-031`), e vindos da `016` — esta tela não os recalcula."""
        edital, _, _ = cenario_da_tela
        identificar(client, "carlos", ["gestor"])

        pagina = abrir(client, edital).content.decode()

        for rotulo in ("Publicadas", "Efetivas", "Ocupadas", "A ocupar"):
            assert rotulo in pagina

    def test_sem_convocacao_praticada_a_tela_o_diz_com_palavras(
        self, client, seletor_ligado, cenario_da_tela
    ):
        """Nenhuma convocação **não** é desenhado como zero solto numa tabela vazia."""
        edital, _, _ = cenario_da_tela
        identificar(client, "carlos", ["gestor"])

        pagina = abrir(client, edital).content.decode()

        assert "Nenhuma convocação praticada neste recorte" in pagina

    def test_convocado_sem_envio_e_um_estado_proprio(
        self, client, seletor_ligado, cenario_da_tela, gestor
    ):
        """`R-009`: sem este estado, falha de infraestrutura vira silêncio da pessoa.

        E o desfecho que decorre de silêncio é perda de vaga — por um servidor de SMTP fora do ar.
        """
        edital, _, _ = cenario_da_tela
        convocar(edital, gestor, proximo(edital), idempotency_key="tela-sem-envio")
        identificar(client, "carlos", ["gestor"])

        pagina = abrir(client, edital).content.decode()

        assert "prazo não iniciado" in pagina

    def test_o_prazo_sai_em_data_e_hora_locais_dizendo_de_onde_corre(
        self, client, seletor_ligado, cenario_da_tela, gestor
    ):
        """`UX-038`: um prazo sem referência é uma data solta.

        A diferença entre 17h e 14h decide se alguém perde a vaga, e ISO com fuso não é legível
        para quem conduz o certame.
        """
        from datetime import timedelta

        from django.utils import timezone

        edital, _, _ = cenario_da_tela
        vencimento = timezone.localtime(timezone.now() + timedelta(days=3))
        convocar(
            edital,
            gestor,
            proximo(edital),
            vencimento=vencimento,
            idempotency_key="tela-prazo",
        )
        identificar(client, "carlos", ["gestor"])

        pagina = abrir(client, edital).content.decode()

        assert vencimento.strftime("%d/%m/%Y %H:%M") in pagina
        assert "contado do envio da comunicação" in pagina

    def test_a_fila_esgotada_nao_oferece_botao_que_esta_feature_nao_cumpre(
        self, client, seletor_ligado, cenario_da_tela, gestor
    ):
        """`UX-037`: ampliar a faixa é ato da `014`, e um botão aqui prometeria o que não se cumpre.

        A tela diz onde o ato acontece, em vez de oferecer um controle que responderia com recusa.
        """
        edital, _, _ = cenario_da_tela
        while True:
            contexto = selectors.contexto_do_recorte(
                edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
            )
            if not contexto["fila"]:
                break
            convocar(
                edital,
                gestor,
                contexto["fila"][0],
                idempotency_key=f"tela-esgota-{len(contexto['convocacoes'])}",
            )
        identificar(client, "carlos", ["gestor"])

        pagina = abrir(client, edital).content.decode()

        assert "Não há mais quem chamar dentro da faixa" in pagina
        assert "Ampliar a faixa é ato do corte" in pagina


class TestAConfirmacaoAntesDoAtoIrreversivel:
    def test_convocar_pede_confirmacao_e_diz_que_e_irreversivel(
        self, client, seletor_ligado, cenario_da_tela
    ):
        edital, _, _ = cenario_da_tela
        identificar(client, "carlos", ["gestor"])

        pagina = abrir(client, edital).content.decode()

        assert 'class="confirmar"' in pagina
        assert "Convocar é irreversível" in pagina

    def test_desfechar_pede_confirmacao(self, client, seletor_ligado, cenario_da_tela, gestor):
        edital, _, _ = cenario_da_tela
        convocar(edital, gestor, proximo(edital), idempotency_key="tela-desfecho")
        identificar(client, "carlos", ["gestor"])

        pagina = abrir(client, edital).content.decode()

        assert "Registrar o desfecho é irreversível" in pagina

    def test_a_mensagem_de_sucesso_nomeia_o_ato_praticado(
        self, client, seletor_ligado, cenario_da_tela, gestor
    ):
        """**Foi o defeito `E2E16-004`** (`UX-036`): três ações, um aviso único, e a frase errada.

        Aqui as três voltam para a mesma tela, e cada uma diz o que aconteceu.
        """
        edital, _, _ = cenario_da_tela
        identificar(client, "carlos", ["gestor"])

        resposta = client.post(
            reverse("interface:convocar", args=[edital.id, MARCO]),
            {
                "inscricao": str(proximo(edital)),
                "especie": nomes.VAGA_INICIAL,
                "fundamento": "No interesse da Administração, item 8.2.",
                "chave": "tela-sucesso",
            },
        )

        assert resposta.status_code == 302
        pagina = client.get(resposta["Location"]).content.decode()
        assert "Convocação praticada" in pagina
        assert "Apuração emitida" not in pagina, "a frase da 016 não pode aparecer aqui"


class TestOVocabularioDaTela:
    @pytest.mark.parametrize("proibida", PROIBIDAS)
    def test_a_tela_nao_afirma_recebimento_nem_direito_a_vaga(
        self, client, seletor_ligado, cenario_da_tela, gestor, proibida
    ):
        edital, _, _ = cenario_da_tela
        convocar(edital, gestor, proximo(edital), idempotency_key="tela-vocab")
        identificar(client, "carlos", ["gestor"])

        pagina = abrir(client, edital).content.decode().lower()

        assert proibida.lower() not in pagina

    def test_a_tela_diz_enviada_em_e_nao_recebida_em(
        self, client, seletor_ligado, cenario_da_tela, gestor, settings
    ):
        """A frase positiva, para que a ausência acima não passe por tela vazia."""
        from processo_seletivo.convocacao.application.comunicar import comunicar

        settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
        edital, _, _ = cenario_da_tela
        convocada = convocar(edital, gestor, proximo(edital), idempotency_key="tela-enviada")
        comunicar(
            actor=gestor,
            processo_id=edital.processo_id,
            convocacao_id=convocada["id"],
            idempotency_key="tela-enviada-comunicar",
            correlation_id="teste",
        )
        identificar(client, "carlos", ["gestor"])

        pagina = abrir(client, edital).content.decode()

        assert "Enviada em" in pagina


def test_a_tela_nao_afirma_numero_de_ocupacao_diferente_do_apurado(
    client, seletor_ligado, cenario_da_tela, gestor
):
    """`FR-278a`, e é a janela entre o desfecho e a emissão seguinte (`T046a`).

    Registrada a desistência, a apuração vigente **não é reescrita**: ela continua dizendo o número
    que apurou, e a tela o mostra com a obsolescência declarada. O modo de errar aqui é a tela
    calcular o número novo por conta própria — e passaria a existir duas respostas para *"quantas
    vagas estão ocupadas"*, que é exatamente o que a `Q-1` recusou.
    """
    from processo_seletivo.convocacao.application.desfechar import desfechar
    from processo_seletivo.ocupacao.application.selectors import apuracao_vigente

    edital, _, _ = cenario_da_tela
    convocada = convocar(edital, gestor, proximo(edital), idempotency_key="tela-obsoleta")
    desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocada["id"],
        especie=nomes.DESISTENCIA_EXPRESSA,
        fundamento="Desistência expressa registrada em processo.",
        idempotency_key="tela-obsoleta-desfecho",
        correlation_id="teste",
    )
    vigente = apuracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None)
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital).content.decode()

    assert "A apuração deste recorte está obsoleta" in pagina
    assert "um desfecho de convocação mudou quem ocupa vaga" in pagina
    assert f"<dt>Ocupadas</dt><dd>{vigente.ocupadas}</dd>" in pagina, (
        "o número exibido é o que a apuração vigente apurou, e não um recalculado pela tela"
    )


def test_o_historico_mostra_a_reclassificacao_com_fundamento_e_posicao_nova(
    client, seletor_ligado, cenario_da_tela, gestor
):
    """`T077`, `FR-291`: quem lê o histórico precisa saber onde o reclassificado está **agora**.

    **A posição é derivada, e não guardada**: cada chamada seguinte a desloca, e uma coluna exigiria
    `UPDATE` numa tabela append-only. E a linha diz, com todas as letras, que ele continua
    habilitado — porque a reclassificação não afirma perda de habilitação (`D-008`).
    """
    from processo_seletivo.convocacao.application.desfechar import desfechar

    edital, _, _ = cenario_da_tela
    convocada = convocar(edital, gestor, proximo(edital), idempotency_key="hist-reclass")
    desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocada["id"],
        especie=nomes.RECLASSIFICACAO,
        fundamento="Não compareceu à chamada do item 7.2 do Edital 69/2026.",
        idempotency_key="hist-reclass-desfecho",
        correlation_id="teste",
    )
    identificar(client, "carlos", ["gestor"])

    pagina = client.get(
        reverse("interface:convocacao-historico", args=[edital.id, MARCO])
    ).content.decode()

    assert "Reclassificação" in pagina
    assert "item 7.2 do Edital 69/2026" in pagina
    assert "na fila de chamada" in pagina
    assert "continua habilitado" in pagina


def test_a_trilha_do_edital_lista_os_atos_da_019_em_linguagem_humana(
    client, seletor_ligado, cenario_da_tela, gestor, settings
):
    """`T091`, `FR-296`: quem audita não tem por que aprender o vocabulário interno do sistema.

    **A trilha exibia `OCUPACAO_APURAR` cru**, e a `019` teria acrescentado mais quatro códigos à
    mesma tela. As frases dizem o ato praticado — *"Convocação praticada"* —, e não o nome da função
    que o praticou.
    """
    from processo_seletivo.convocacao.application.comunicar import comunicar
    from processo_seletivo.convocacao.application.desfechar import desfechar
    from processo_seletivo.interface.views import OPERACOES

    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    edital, _, _ = cenario_da_tela
    convocada = convocar(edital, gestor, proximo(edital), idempotency_key="trilha-conv")
    comunicar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocada["id"],
        idempotency_key="trilha-comunicar",
        correlation_id="teste",
    )
    desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocada["id"],
        especie=nomes.ACEITE,
        fundamento="Matrícula efetivada.",
        idempotency_key="trilha-desfecho",
        correlation_id="teste",
    )
    identificar(client, "carlos", ["gestor", "auditor"])

    pagina = client.get(reverse("interface:auditoria", args=[edital.id])).content.decode()

    assert "Convocação praticada" in pagina
    assert "Comunicação de convocação emitida" in pagina
    assert "Desfecho de convocação registrado" in pagina
    assert "Apuração de ocupação de vagas" in pagina
    for cru in ("CONVOCACAO_CONVOCAR", "CONVOCACAO_DESFECHAR", "OCUPACAO_APURAR"):
        assert cru not in pagina, "o código interno não aparece na tela de quem audita"
    for operacao in (
        "CONVOCACAO_CONVOCAR",
        "CONVOCACAO_DESFECHAR",
        "CONVOCACAO_COMUNICAR",
        "CONVOCACAO_ATESTAR",
    ):
        assert operacao in OPERACOES


def test_a_tela_identifica_a_pessoa_por_protocolo_e_nome_e_nao_por_uuid(
    client, seletor_ligado, cenario_da_tela, gestor
):
    """**Achado do percurso conduzido**: a fila e os dois seletores saíam em UUID.

    Tecnicamente exato e operacionalmente inútil — quem vai convocar confere contra a lista
    publicada, e a lista publicada tem protocolo e nome. É a mesma lição que a fixture de inscrição
    da `009` registra ao gerar `INS-<ano>-NNNN` em vez de quatro dígitos nus: identificador sorteado
    é indistinguível de ruído.

    **O identificador continua sendo o valor que o formulário envia.** O que mudou é o que a pessoa
    lê — e é por isso que a asserção olha o texto, e não o `value` do `option`.
    """
    from processo_seletivo.inscricoes.models import Inscricao

    edital, _, _ = cenario_da_tela
    alguem = proximo(edital)
    registro = Inscricao.objects.get(id=alguem)
    identificar(client, "carlos", ["gestor"])

    antes = abrir(client, edital).content.decode()

    assert registro.protocolo in antes, "a fila e o seletor nomeiam a pessoa"
    assert registro.nome in antes
    assert f'value="{alguem}"' in antes, "o formulário continua enviando o identificador"
    assert f">{alguem}<" not in antes, "mas nenhum UUID é oferecido como texto ao leitor"

    convocar(edital, gestor, alguem, idempotency_key="tela-protocolo")
    depois = abrir(client, edital).content.decode()

    assert f"{registro.protocolo} — {registro.nome}" in depois, (
        "e a chamada praticada também é lida por protocolo e nome"
    )
