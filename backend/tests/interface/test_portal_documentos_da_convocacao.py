"""Os documentos da convocação no portal do candidato (115, US1, US2, US3, US4).

Pela tela da convocação da `059`, e pelo canal do ator: o titular vê a lista, envia, lê a pendência
e o resultado, e quem não é titular recebe a recusa de inexistente (FR-3577, FR-3582, FR-3584,
FR-3600, FR-3612, FR-3613).
"""

from datetime import timedelta
from unittest import mock

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.portal.identidade import CHAVE_SESSAO
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.comissao import abrir_arquivo
from tests.fixtures.documentos_da_convocacao import (
    CERTIDAO,
    CERTIFICADO,
    CERTIFICADO_DO_MEDIO,
    CERTIFICADO_NA_CONVOCACAO,
    FICHA,
    HISTORICO,
    IDENTIDADE,
    RESIDENCIA,
    apresentar,
    comunicar,
    conferir,
    item,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

TERMOS_DE_VINCULO = (
    "matriculad",
    "matrícula efetivada",
    "bolsa concedida",
    "vinculad",
    "contratad",
)


def entrar_como(client, inscricao):
    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=inscricao.identity_subject, defaults={"created_at": timezone.now()}
    )
    sessao = client.session
    sessao[CHAVE_SESSAO] = str(registro.pk)
    sessao.save()


def tela(client, pessoa):
    resposta = client.get(reverse("portal:convocacao", args=[pessoa.id]))
    assert resposta.status_code == 200
    return resposta.content.decode()


@pytest.fixture
def aluno(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="portal-aluno-115",
    )


def test_a_convocada_ve_o_que_apresentar_e_ate_quando(aluno, gestor, client):
    pessoa, _ = cenarios.convocar_primeira(
        aluno, gestor, vencimento=timezone.now() + timedelta(days=3)
    )
    entrar_como(client, pessoa)

    corpo = tela(client, pessoa)

    # Os blocos da `118` (FR-3735) no lugar da lista única, e "Envie até…" saiu da lista. Esta
    # convocação não teve a comunicação enviada: a tela antiga mostrava a data como prazo de um
    # prazo que não corria (F12); a de agora diz que ele não começou, e a data fica só nos dados do
    # ato (FR-3749 da `118`).
    # A chamada da 121 no lugar de "O que fazer agora" (FR-3735 da 118, revista).
    assert "Você foi convocado!" in corpo and "O que falta" in corpo
    assert "O que fazer agora" not in corpo
    assert "Certidão de nascimento ou casamento" in corpo
    assert "Todas as páginas, em arquivo único." in corpo
    assert corpo.count("Falta enviar") == 4
    assert "O prazo ainda não começou a correr" in corpo
    assert "Você já pode enviar." in corpo
    assert "Envie até" not in corpo
    assert "Prazo desta convocação" not in corpo
    assert "Documento de identificação" not in corpo.split('class="chamada-da-convocacao"')[1]


def test_a_convocada_envia_pelo_portal_e_le_o_resultado(aluno, gestor, client):
    edital, _, _ = aluno
    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    entrar_como(client, pessoa)
    alvo = item(convocacao, HISTORICO)

    resposta = client.post(
        reverse("portal:apresentar-documento-da-convocacao", args=[pessoa.id, alvo.id]),
        {"arquivo": cenarios.pdf(b"historico")},
    )
    # A volta é a confirmação, e não o cartão (121, FR-3870): ela diz o documento e a data, e que
    # o arquivo aguarda a conferência da comissão.
    assert resposta.status_code == 302
    assert resposta["Location"].endswith("#confirmacao")
    corpo = tela(client, pessoa)
    assert "Recebemos: Histórico escolar do ensino médio, em " in corpo
    assert "O arquivo aguarda a conferência da comissão." in corpo
    # O selo e a frase da FR-3746 da `118`, no lugar do sufixo "aguardando conferência".
    assert "Aguardando conferência" in corpo
    assert "A comissão vai conferir; você não precisa fazer nada agora." in corpo

    conferir(gestor, convocacao, HISTORICO, "PENDENTE", chave="pp", motivo="Falta a página 2.")
    corpo = tela(client, pessoa)
    assert "Precisa de correção: Falta a página 2. Envie um novo arquivo" in corpo
    assert "carlos" not in corpo, "a tela não diz quem conferiu (FR-3584)"
    assert not any(termo in corpo.lower() for termo in TERMOS_DE_VINCULO)


def test_o_arquivo_invalido_volta_com_a_recusa_da_inscricao(aluno, gestor, client):
    from django.core.files.uploadedfile import SimpleUploadedFile

    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    entrar_como(client, pessoa)
    alvo = item(convocacao, CERTIDAO)

    client.post(
        reverse("portal:apresentar-documento-da-convocacao", args=[pessoa.id, alvo.id]),
        {"arquivo": SimpleUploadedFile("foto.jpg", b"\xff\xd8\xff", content_type="image/jpeg")},
    )

    corpo = tela(client, pessoa)
    assert 'role="alert"' in corpo
    assert not alvo.apresentacoes.exists()


def test_outro_candidato_nao_alcanca_nem_a_lista_nem_o_arquivo(aluno, gestor, client):
    edital, _, inscricoes = aluno
    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    feita = apresentar(pessoa, convocacao, CERTIDAO).apresentacao
    outra = next(i for i in inscricoes if i.id != pessoa.id)
    entrar_como(client, outra)

    envio = client.post(
        reverse(
            "portal:apresentar-documento-da-convocacao",
            args=[pessoa.id, item(convocacao, CERTIDAO).id],
        ),
        {"arquivo": cenarios.pdf()},
    )
    arquivo = client.get(reverse("portal:documento-da-convocacao", args=[pessoa.id, feita.id]))
    alheio = client.get(reverse("portal:documento-da-convocacao", args=[outra.id, feita.id]))

    assert envio.status_code == 404
    assert arquivo.status_code == 404
    assert alheio.status_code == 404, "a apresentação de outra inscrição é inexistente"


def test_o_titular_ve_o_arquivo_que_apresentou(aluno, gestor, client):
    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    feita = apresentar(pessoa, convocacao, CERTIDAO, corpo=b"minha certidao").apresentacao
    entrar_como(client, pessoa)

    resposta = abrir_arquivo(
        client, reverse("portal:documento-da-convocacao", args=[pessoa.id, feita.id])
    )

    assert resposta.status_code == 200
    assert b"minha certidao" in resposta.conteudo_servido
    assert "no-store" in resposta["Cache-Control"]


def test_depois_do_vencimento_a_tela_diz_o_prazo_e_nao_oferece_envio(aluno, gestor, client):
    edital, _, _ = aluno
    pessoa, convocacao = cenarios.convocar_primeira(
        aluno, gestor, vencimento=timezone.now() + timedelta(minutes=1)
    )
    comunicar(edital, gestor, convocacao)
    entrar_como(client, pessoa)

    with mock.patch("django.utils.timezone.now", return_value=timezone.now() + timedelta(days=2)):
        corpo = tela(client, pessoa)

    # O núcleo único do vencido (FR-3748 da `118`), no lugar de "A comissão vai decidir.".
    assert "O prazo terminou em" in corpo
    assert (
        "O fim do prazo não decide nada sozinho: quem registra o resultado é a comissão." in corpo
    )
    assert "A comissão vai decidir." not in corpo
    assert "Escolher arquivo PDF" not in corpo


def test_mostrar_a_lista_nao_registra_leitura_alem_da_convocacao(aluno, gestor, client):
    """FR-3613: a tela da convocação já registra a leitura dela, e a lista não acrescenta outra."""
    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    entrar_como(client, pessoa)

    tela(client, pessoa)

    operacoes = set(
        RegistroAuditoria.objects.filter(actor_subject=pessoa.identity_subject).values_list(
            "operation", flat=True
        )
    )
    assert operacoes == {"CONVOCACAO_LER"}


def test_sem_documento_na_convocacao_a_tela_e_a_de_antes(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, client
):
    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=[cenarios.documentos_do_aluno()[0]],
        prefixo="portal-sem-115",
    )
    pessoa, _ = cenarios.convocar_primeira(cenario, gestor)
    entrar_como(client, pessoa)

    corpo = tela(client, pessoa)
    # Sem documento, a estrutura de antes (FR-3574 da `115`; FR-3743 da `118`): nenhum bloco novo.
    # O título de primeiro nível é o da chamada (121, FR-3868), e "O que fazer" é de segundo nível.
    assert "O que fazer agora" not in corpo
    assert "<h2>O que fazer</h2>" in corpo


def test_o_certificado_da_inscricao_aparece_atendido(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, client
):
    """US3 no portal: nenhum envio, e a frase do aproveitamento."""
    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_certificado(),
        documentos_da_inscricao=(IDENTIDADE, CERTIFICADO),
        prefixo="portal-cert-115",
    )
    pessoa, convocacao = cenarios.convocar_primeira(cenario, gestor)
    entrar_como(client, pessoa)

    corpo = tela(client, pessoa)

    # "Atendido" antes da conferência era a falsa conclusão de um item (118, FR-3746): o texto diz
    # que a pessoa já o enviou e que a comissão vai conferir. A garantia de antes continua — nenhum
    # envio, e a referência é uma só.
    assert "Você já enviou este documento na inscrição, em " in corpo
    assert "Não precisa enviar de novo. A comissão vai conferir." in corpo
    assert "tendid" not in corpo.lower()
    assert item(convocacao, CERTIFICADO_NA_CONVOCACAO).apresentacoes.count() == 1


def test_o_bolsista_baixa_o_modelo_anexo_e_nada_diz_bolsa_concedida(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, client
):
    """US2: o modelo da Ficha/Termo é oferecido na própria tela, e não há requerimento."""
    from tests.fixtures.publicacao import publish_original

    def ligar_o_modelo(edital):
        from processo_seletivo.editais.models.documentos import DocumentoExigido
        from tests.fixtures.anexos import criar_anexo

        anexo = criar_anexo(edital, rotulo="ANEXO I — FICHA E TERMO DO BOLSISTA")
        DocumentoExigido.objects.filter(edital=edital, key="ficha-termo").update(anexo=anexo)

    def com_o_modelo(api_client, manager_headers, process_payload, *, draft=None):
        return publish_original(
            api_client,
            manager_headers,
            process_payload,
            draft=draft,
            antes_de_submeter=ligar_o_modelo,
        )

    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_bolsista(),
        prefixo="portal-bolsista-115",
        publicar=com_o_modelo,
    )
    pessoa, convocacao = cenarios.convocar_primeira(cenario, gestor)
    entrar_como(client, pessoa)

    corpo = tela(client, pessoa)

    assert "Ficha de Cadastramento e Termo de Compromisso do Bolsista" in corpo
    assert "Baixar o modelo:" in corpo
    assert "Requerimento de Matrícula" not in corpo
    assert not any(termo in corpo.lower() for termo in TERMOS_DE_VINCULO)
    assert item(convocacao, FICHA).situacao == "OBRIGATORIO"


def test_a_pendencia_sobre_o_que_nao_chegou_mostra_o_motivo(aluno, gestor, client):
    """Revisão do #369: antes, o item dizia só "Falta enviar", e o motivo sumia."""
    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    conferir(gestor, convocacao, CERTIDAO, "PENDENTE", chave="pp0", motivo="Envie a de casamento.")
    entrar_como(client, pessoa)

    corpo = tela(client, pessoa)

    # O motivo continua, agora com o convite certo: não há arquivo anterior (118, cenário J).
    assert "Precisa de correção: Envie a de casamento. Envie o arquivo" in corpo
    assert "outro arquivo" not in corpo.split("Envie a de casamento.")[1].split("</p>")[0]


def test_a_pagina_publica_avisa_o_que_a_convocacao_pedira(aluno, client):
    edital, _, _ = aluno

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert "Se for convocado, a convocação pedirá também:" in corpo
    assert "Certidão de nascimento ou casamento" in corpo


# --- A volta do envio (121, FR-3870 a FR-3872, R-006) ---------------------------------------------


def _postar(client, pessoa, alvo, arquivo=None):
    return client.post(
        reverse("portal:apresentar-documento-da-convocacao", args=[pessoa.id, alvo.id]),
        {"arquivo": arquivo} if arquivo is not None else {},
    )


def _chamada(corpo):
    return corpo.split('<section class="chamada-da-convocacao"', 1)[1].split("</section>", 1)[0]


def _confirmacao(corpo):
    return corpo.split('id="confirmacao"', 1)[1].split(">", 1)[1].split("</div>", 1)[0]


def _texto(html):
    import re

    return " ".join(re.sub(r"<[^>]+>", " ", html).split())


class TestAConfirmacao:
    def test_o_envio_aceito_volta_a_confirmacao(self, aluno, gestor, client):
        """FR-3870, D-010: o primeiro elemento da chamada, focável pela âncora, com o documento, a
        data e a hora, "o arquivo aguarda a conferência" e a próxima tarefa."""
        from processo_seletivo.portal import obrigacoes

        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        alvo = item(convocacao, CERTIDAO)

        resposta = _postar(client, pessoa, alvo, cenarios.pdf(b"certidao"))

        destino = reverse("portal:convocacao", args=[pessoa.id])
        assert resposta.status_code == 302 and resposta["Location"] == f"{destino}#confirmacao"
        corpo = tela(client, pessoa)
        chamada = _chamada(corpo)
        assert (
            '<div class="confirmacao-do-envio" id="confirmacao" tabindex="-1" role="status">'
            in (chamada)
        )
        assert chamada.index('id="confirmacao"') < chamada.index('class="contexto-da-chamada"')
        recebida = alvo.apresentacoes.get().apresentado_em
        confirmacao = _texto(_confirmacao(corpo))
        assert (
            f"Recebemos: Certidão de nascimento ou casamento, em {obrigacoes.data(recebida)}, às "
            f"{obrigacoes.hora(recebida)}. O arquivo aguarda a conferência da comissão."
        ) in confirmacao
        historico = item(convocacao, HISTORICO)
        assert "Próxima tarefa: Histórico escolar do ensino médio" in confirmacao
        assert f'href="#item-{historico.id}"' in _confirmacao(corpo)
        for proibido in ("aceito", "aprovado", "conferido", "atendido"):
            assert proibido not in confirmacao.lower(), proibido

    def test_cada_volta_mostra_so_o_seu_envio(self, aluno, gestor, client):
        """D-010: a confirmação se consome ao exibir, e o andamento mostra o acumulado."""
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        _postar(client, pessoa, item(convocacao, CERTIDAO), cenarios.pdf(b"um"))
        tela(client, pessoa)

        _postar(client, pessoa, item(convocacao, HISTORICO), cenarios.pdf(b"dois"))
        corpo = tela(client, pessoa)

        confirmacao = _texto(_confirmacao(corpo))
        assert "Histórico escolar do ensino médio" in confirmacao.split("Próxima tarefa")[0]
        assert "Certidão" not in confirmacao
        assert 'id="confirmacao"' not in tela(client, pessoa)
        assert "Aguardando conferência: 2" in _texto(corpo)

    def test_o_ultimo_documento_diz_a_conclusao(self, aluno, gestor, client):
        from tests.fixtures.documentos_da_convocacao import CERTIFICADO_DO_MEDIO, RESIDENCIA

        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        for requisito in (CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO):
            apresentar(pessoa, convocacao, requisito, corpo=f"c-{requisito}".encode())

        _postar(client, pessoa, item(convocacao, RESIDENCIA), cenarios.pdf(b"residencia"))
        confirmacao = _texto(_confirmacao(tela(client, pessoa)))

        assert "Próxima tarefa" not in confirmacao
        assert (
            "Você não tem mais documentos para enviar agora. A comissão ainda vai concluir a "
            "análise." in confirmacao
        )

    def test_o_mesmo_arquivo_de_novo(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        alvo = item(convocacao, CERTIDAO)
        _postar(client, pessoa, alvo, cenarios.pdf(b"igual"))
        tela(client, pessoa)

        resposta = _postar(client, pessoa, alvo, cenarios.pdf(b"igual"))

        assert resposta["Location"].endswith("#confirmacao")
        confirmacao = _texto(_confirmacao(tela(client, pessoa)))
        assert confirmacao == "Este arquivo já tinha sido recebido."

    def test_a_volta_de_outra_inscricao_fica_para_ela(self, aluno, gestor, client):
        """A sessão é da pessoa, e não da inscrição: a convocação de uma não consome a volta do
        envio feito na outra, que continua guardada para quando aquela abrir."""
        import uuid

        from processo_seletivo.portal.views import (
            CHAVE_DA_CONFIRMACAO_DA_CONVOCACAO,
            CHAVE_DA_RECUSA_DA_CONVOCACAO,
        )

        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        outra = str(uuid.uuid4())
        sessao = client.session
        sessao[CHAVE_DA_CONFIRMACAO_DA_CONVOCACAO] = {
            "inscricao": outra,
            "item_id": str(item(convocacao, CERTIDAO).id),
            "apresentacao_id": str(uuid.uuid4()),
            "ja_recebido": True,
        }
        sessao[CHAVE_DA_RECUSA_DA_CONVOCACAO] = {
            "inscricao": outra,
            "ancora": f"item-{item(convocacao, CERTIDAO).id}",
            "frase": "Recusa de outra inscrição.",
        }
        sessao.save()

        corpo = tela(client, pessoa)

        assert 'id="confirmacao"' not in corpo and "Recusa de outra inscrição." not in corpo
        guardado = client.session
        assert guardado[CHAVE_DA_CONFIRMACAO_DA_CONVOCACAO]["inscricao"] == outra
        assert guardado[CHAVE_DA_RECUSA_DA_CONVOCACAO]["inscricao"] == outra


class TestARecusaNoCartao:
    """FR-3871: a volta é o cartão do item, com a recusa nele e o foco nela, e sem confirmação."""

    def _recusa(self, client, pessoa, alvo, arquivo=None):
        resposta = _postar(client, pessoa, alvo, arquivo)
        destino = reverse("portal:convocacao", args=[pessoa.id])
        assert resposta.status_code == 302
        assert resposta["Location"] == f"{destino}#item-{alvo.id}"
        return resposta

    def _cartao(self, corpo, alvo):
        return corpo.split(f'id="item-{alvo.id}"', 1)[1].split("</li>", 1)[0]

    def test_sem_arquivo(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        alvo = item(convocacao, CERTIDAO)

        self._recusa(client, pessoa, alvo)
        corpo = tela(client, pessoa)

        cartao = self._cartao(corpo, alvo)
        assert 'role="alert" tabindex="-1" data-recusa>Escolha um arquivo PDF antes de enviar.' in (
            cartao
        )
        assert 'id="confirmacao"' not in corpo
        assert corpo.count("data-recusa") == 1

    def test_nao_pdf(self, aluno, gestor, client):
        from django.core.files.uploadedfile import SimpleUploadedFile

        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        alvo = item(convocacao, CERTIDAO)
        foto = SimpleUploadedFile("foto.jpg", b"\xff\xd8\xff", content_type="image/jpeg")

        self._recusa(client, pessoa, alvo, foto)

        assert "data-recusa" in self._cartao(tela(client, pessoa), alvo)
        assert not alvo.apresentacoes.exists()

    def test_acima_do_limite(self, aluno, gestor, client, settings):
        settings.ARQUIVOS_CANDIDATOS_LIMITE_BYTES = 20
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        alvo = item(convocacao, CERTIDAO)

        self._recusa(client, pessoa, alvo, cenarios.pdf(b"x" * 200))

        assert "data-recusa" in self._cartao(tela(client, pessoa), alvo)

    def test_fora_do_prazo(self, aluno, gestor, client):
        """A recusa com o núcleo do vencido da FR-3748 da 118, e a página já no estado encerrado."""
        edital, _, _ = aluno
        pessoa, convocacao = cenarios.convocar_primeira(
            aluno, gestor, vencimento=timezone.now() + timedelta(minutes=1)
        )
        comunicar(edital, gestor, convocacao)
        entrar_como(client, pessoa)
        alvo = item(convocacao, CERTIDAO)

        with mock.patch(
            "django.utils.timezone.now", return_value=timezone.now() + timedelta(days=2)
        ):
            self._recusa(client, pessoa, alvo, cenarios.pdf(b"tarde"))
            corpo = tela(client, pessoa)

        recusa = _texto(self._cartao(corpo, alvo).split("data-recusa>", 1)[1].split("</p>")[0])
        assert recusa.startswith("O prazo terminou em")
        assert "O prazo desta convocação terminou" in corpo, "a página já está encerrada"
        assert 'id="confirmacao"' not in corpo


def test_a_convocacao_carrega_os_quatro_scripts_e_nenhum_outro(aluno, gestor, client):
    """FR-3872 da `121`, revista pela FR-5614 da `150`: os três da inscrição e o do envio de
    vários, antes de `envio.js` (R-001), por arquivo estático, e nenhum script embutido."""
    import re

    pessoa, _ = cenarios.convocar_primeira(aluno, gestor)
    entrar_como(client, pessoa)

    corpo = tela(client, pessoa)
    scripts = re.findall(r'<script src="([^"]+)"', corpo)
    proprios = [s.rsplit("/", 1)[1].split("?")[0] for s in scripts if "/portal/" in s]

    assert proprios[-4:] == ["arquivo.js", "varios.js", "envio.js", "recusa.js"]
    assert not re.search(r"<script(?![^>]*\bsrc=)", corpo), "nenhum script embutido"


# --- O envio de vários (150, US1, US2; contrato §1 e §2) -----------------------------------------


def _no_lote(client, pessoa, alvo, posicao, arquivo=None, **campos):
    dados = dict(campos)
    if arquivo is not None:
        dados["arquivo"] = arquivo
    return client.post(
        reverse("portal:apresentar-documento-da-convocacao", args=[pessoa.id, alvo.id]),
        dados,
        HTTP_X_ENVIO_DE_VARIOS=posicao,
    )


def _foto():
    from django.core.files.uploadedfile import SimpleUploadedFile

    return SimpleUploadedFile("foto.jpg", b"\xff\xd8\xff", content_type="image/jpeg")


class TestORamoDoLote:
    """R-002: com o cabeçalho, o resultado de cada documento em JSON; sem ele, nada muda."""

    def test_recebido_responde_json_com_a_volta_da_confirmacao(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        alvo = item(convocacao, CERTIDAO)

        resposta = _no_lote(client, pessoa, alvo, "1/2", cenarios.pdf(b"certidao"))

        assert resposta.status_code == 200
        assert resposta["Content-Type"].startswith("application/json")
        destino = reverse("portal:convocacao", args=[pessoa.id])
        assert resposta.json() == {
            "resultado": "recebido",
            "ancora": f"item-{alvo.id}",
            "volta": f"{destino}?lote=2#confirmacao",
        }
        assert alvo.apresentacoes.count() == 1

    def test_recusado_traz_a_frase_de_hoje_e_volta_ao_cartao(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        alvo = item(convocacao, CERTIDAO)

        dados = _no_lote(client, pessoa, alvo, "1/2", _foto()).json()

        assert dados["resultado"] == "recusado"
        assert "imagem" in dados["frase"].lower()
        assert dados["volta"].endswith(f"?lote=2#item-{alvo.id}")
        assert not alvo.apresentacoes.exists()

    def test_o_mesmo_arquivo_de_novo_e_ja_recebido(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        alvo = item(convocacao, CERTIDAO)
        _postar(client, pessoa, alvo, cenarios.pdf(b"igual"))

        dados = _no_lote(client, pessoa, alvo, "1/2", cenarios.pdf(b"igual")).json()

        assert dados["resultado"] == "ja_recebido"
        assert alvo.apresentacoes.count() == 1

    def test_sem_arquivo_e_a_recusa_de_hoje(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)

        dados = _no_lote(client, pessoa, item(convocacao, CERTIDAO), "1/2").json()

        assert (dados["resultado"], dados["frase"]) == (
            "recusado",
            "Escolha um arquivo PDF antes de enviar.",
        )

    def test_o_tamanho_declarado_acima_do_limite_e_a_recusa_de_tamanho(
        self, aluno, gestor, client, settings
    ):
        """R-009: o arquivo grande não viaja, e a recusa é a de `shared.arquivos.aceitar`."""
        settings.ARQUIVOS_CANDIDATOS_LIMITE_BYTES = 1024 * 1024
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        alvo = item(convocacao, CERTIDAO)

        grande = str(15 * 1024 * 1024)
        dados = _no_lote(client, pessoa, alvo, "1/2", tamanho_declarado=grande).json()

        assert dados["resultado"] == "recusado"
        assert dados["frase"].startswith("O arquivo tem 15")
        assert dados["frase"].endswith("Reduza o tamanho e envie novamente.")
        assert not alvo.apresentacoes.exists()
        corpo = tela(client, pessoa)
        assert dados["frase"] in corpo, "a recusa chegou à sessão, e ao cartão"

    def test_o_tamanho_declarado_abaixo_do_limite_vale_como_ausencia(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)

        dados = _no_lote(
            client, pessoa, item(convocacao, CERTIDAO), "1/2", tamanho_declarado="10"
        ).json()

        assert dados["frase"] == "Escolha um arquivo PDF antes de enviar."

    def test_o_tamanho_declarado_fora_do_lote_e_ignorado(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        alvo = item(convocacao, CERTIDAO)

        resposta = _postar(client, pessoa, alvo)
        corpo = tela(client, pessoa)

        assert resposta.status_code == 302
        assert "Escolha um arquivo PDF antes de enviar." in corpo

    @pytest.mark.parametrize("cabecalho", ["x/0", "3/2", "abc", "0/2", "1-2", ""])
    def test_cabecalho_malformado_e_o_envio_de_hoje(self, aluno, gestor, client, cabecalho):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        alvo = item(convocacao, CERTIDAO)

        resposta = _no_lote(client, pessoa, alvo, cabecalho, cenarios.pdf(b"c"))

        destino = reverse("portal:convocacao", args=[pessoa.id])
        assert resposta.status_code == 302
        assert resposta["Location"] == f"{destino}#confirmacao"

    def test_o_item_inexistente_continua_404(self, aluno, gestor, client):
        import uuid

        pessoa, _ = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)

        resposta = client.post(
            reverse("portal:apresentar-documento-da-convocacao", args=[pessoa.id, uuid.uuid4()]),
            {"arquivo": cenarios.pdf(b"x")},
            HTTP_X_ENVIO_DE_VARIOS="1/2",
        )

        assert resposta.status_code == 404


class TestASessaoDoLote:
    """R-003: o lote acumula na sessão, `1/n` zera, e a volta lê também a forma antiga."""

    def test_a_primeira_posicao_zera_e_as_seguintes_acumulam(self, aluno, gestor, client):
        from processo_seletivo.portal.views import (
            CHAVE_DA_CONFIRMACAO_DA_CONVOCACAO,
            CHAVE_DA_RECUSA_DA_CONVOCACAO,
        )

        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        _postar(client, pessoa, item(convocacao, RESIDENCIA), _foto())
        _no_lote(client, pessoa, item(convocacao, CERTIDAO), "1/3", cenarios.pdf(b"a"))
        _no_lote(client, pessoa, item(convocacao, HISTORICO), "2/3", _foto())
        _no_lote(client, pessoa, item(convocacao, CERTIFICADO_DO_MEDIO), "3/3", cenarios.pdf(b"c"))

        confirmacao = client.session[CHAVE_DA_CONFIRMACAO_DA_CONVOCACAO]
        recusa = client.session[CHAVE_DA_RECUSA_DA_CONVOCACAO]
        assert confirmacao["total"] == 3
        assert [e["item_id"] for e in confirmacao["envios"]] == [
            str(item(convocacao, CERTIDAO).id),
            str(item(convocacao, CERTIFICADO_DO_MEDIO).id),
        ]
        assert [r["ancora"] for r in recusa["recusas"]] == [
            f"item-{item(convocacao, HISTORICO).id}"
        ], "a recusa do envio anterior, de fora do lote, foi zerada"

    def test_o_envio_de_um_grava_a_lista_com_um(self, aluno, gestor, client):
        from processo_seletivo.portal.views import CHAVE_DA_CONFIRMACAO_DA_CONVOCACAO

        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        _postar(client, pessoa, item(convocacao, CERTIDAO), cenarios.pdf(b"a"))
        _postar(client, pessoa, item(convocacao, HISTORICO), cenarios.pdf(b"b"))

        confirmacao = client.session[CHAVE_DA_CONFIRMACAO_DA_CONVOCACAO]
        assert confirmacao["total"] == 1
        assert [e["item_id"] for e in confirmacao["envios"]] == [
            str(item(convocacao, HISTORICO).id)
        ], "fora do lote, cada envio começa o seu, como antes"

    def test_a_forma_antiga_ainda_e_lida(self, aluno, gestor, client):
        """A sessão aberta durante a implantação traz a forma de antes da `150`."""
        from processo_seletivo.portal.views import (
            CHAVE_DA_CONFIRMACAO_DA_CONVOCACAO,
            CHAVE_DA_RECUSA_DA_CONVOCACAO,
        )

        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        feita = apresentar(pessoa, convocacao, CERTIDAO, corpo=b"antes")
        historico = item(convocacao, HISTORICO)
        sessao = client.session
        sessao[CHAVE_DA_CONFIRMACAO_DA_CONVOCACAO] = {
            "inscricao": str(pessoa.id),
            "item_id": str(item(convocacao, CERTIDAO).id),
            "apresentacao_id": str(feita.apresentacao.id),
            "ja_recebido": False,
        }
        sessao[CHAVE_DA_RECUSA_DA_CONVOCACAO] = {
            "inscricao": str(pessoa.id),
            "ancora": f"item-{historico.id}",
            "frase": "Recusa guardada antes da 150.",
        }
        sessao.save()

        corpo = tela(client, pessoa)

        assert "Recebemos: Certidão de nascimento ou casamento" in _texto(_confirmacao(corpo))
        cartao = corpo.split(f'id="item-{historico.id}"', 1)[1].split("</li>", 1)[0]
        assert "data-recusa>Recusa guardada antes da 150." in cartao
        assert 'id="confirmacao"' not in tela(client, pessoa), "consumida uma vez"


class TestAMarcacaoDoLote:
    """Contrato §3, só o que o envio de vários usa: o nome do documento e o limite."""

    def test_o_cartao_diz_o_documento_e_o_formulario_o_limite(
        self, aluno, gestor, client, settings
    ):
        import re

        settings.ARQUIVOS_CANDIDATOS_LIMITE_BYTES = 3 * 1024 * 1024
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        alvo = item(convocacao, CERTIDAO)

        corpo = tela(client, pessoa)

        assert re.search(
            rf'id="item-{alvo.id}" tabindex="-1" data-documento="Certidão de nascimento ou '
            r'casamento"',
            corpo,
        )
        formularios = re.findall(r"<form[^>]*data-envio[^>]*>", corpo)
        assert formularios and all('data-limite-em-bytes="3145728"' in f for f in formularios), (
            formularios
        )
        assert '<p class="oculto" role="status" aria-live="polite" data-anuncio-de-varios></p>' in (
            corpo
        )


class TestAVoltaDoLote:
    """FR-5608, FR-5609: a confirmação de vários, e a recusa no cartão de cada um."""

    def test_quatro_recebidos(self, aluno, gestor, client):
        from processo_seletivo.portal import obrigacoes

        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        requisitos = (CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO, RESIDENCIA)
        for posicao, requisito in enumerate(requisitos, start=1):
            dados = _no_lote(
                client,
                pessoa,
                item(convocacao, requisito),
                f"{posicao}/4",
                cenarios.pdf(f"doc-{posicao}".encode()),
            ).json()

        destino = reverse("portal:convocacao", args=[pessoa.id])
        assert dados["volta"] == f"{destino}?lote=4#confirmacao"
        corpo = _texto(_confirmacao(tela(client, pessoa)))
        assert corpo.startswith(
            "Recebemos 4 de 4 documentos. Os arquivos aguardam a conferência da comissão."
        )
        for requisito in requisitos:
            alvo = item(convocacao, requisito)
            recebida = alvo.apresentacoes.get().apresentado_em
            assert f"em {obrigacoes.data(recebida)}, às {obrigacoes.hora(recebida)}." in corpo
        assert "Certidão de nascimento ou casamento, em" in corpo
        assert "Comprovante de residência, em" in corpo
        assert "Você não tem mais documentos para enviar agora." in corpo, "a conclusão de hoje"
        assert "não foi recebido" not in corpo and "não foram recebidos" not in corpo
        for proibido in ("aceito", "aprovado", "conferido", "atendido"):
            assert proibido not in corpo.lower(), proibido

    def test_um_recusado_no_meio(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        historico = item(convocacao, HISTORICO)
        _no_lote(client, pessoa, item(convocacao, CERTIDAO), "1/4", cenarios.pdf(b"a"))
        _no_lote(client, pessoa, historico, "2/4", _foto())
        _no_lote(client, pessoa, item(convocacao, CERTIFICADO_DO_MEDIO), "3/4", cenarios.pdf(b"c"))
        dados = _no_lote(
            client, pessoa, item(convocacao, RESIDENCIA), "4/4", cenarios.pdf(b"d")
        ).json()

        assert dados["volta"].endswith("#confirmacao")
        corpo = tela(client, pessoa)
        confirmacao = _confirmacao(corpo)
        assert _texto(confirmacao).startswith("Recebemos 3 de 4 documentos.")
        assert "1 documento não foi recebido:" in _texto(confirmacao)
        ligacao = f'<a href="#item-{historico.id}">Histórico escolar do ensino médio</a>'
        assert ligacao in confirmacao
        assert "Próxima tarefa: Histórico escolar do ensino médio" in _texto(confirmacao)
        cartao = corpo.split(f'id="item-{historico.id}"', 1)[1].split("</li>", 1)[0]
        assert 'role="alert" tabindex="-1" data-recusa>' in cartao
        assert corpo.count("data-recusa") == 1

    def test_dois_recusados_no_plural(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        _no_lote(client, pessoa, item(convocacao, CERTIDAO), "1/3", _foto())
        _no_lote(client, pessoa, item(convocacao, HISTORICO), "2/3", cenarios.pdf(b"b"))
        _no_lote(client, pessoa, item(convocacao, RESIDENCIA), "3/3", _foto())

        corpo = tela(client, pessoa)

        confirmacao = _texto(_confirmacao(corpo))
        assert confirmacao.startswith(
            "Recebemos 1 de 3 documentos. O arquivo aguarda a conferência da comissão."
        )
        assert "2 documentos não foram recebidos:" in confirmacao
        assert corpo.count("data-recusa") == 2

    def test_todos_recusados_voltam_ao_cartao_do_primeiro(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        certidao, historico = item(convocacao, CERTIDAO), item(convocacao, HISTORICO)
        _no_lote(client, pessoa, certidao, "1/2", _foto())
        dados = _no_lote(client, pessoa, historico, "2/2", _foto()).json()

        destino = reverse("portal:convocacao", args=[pessoa.id])
        assert dados["volta"] == f"{destino}?lote=2#item-{certidao.id}"
        corpo = tela(client, pessoa)
        assert 'id="confirmacao"' not in corpo
        primeira = corpo.index("data-recusa")
        assert corpo.rfind(f'id="item-{certidao.id}"', 0, primeira) > corpo.rfind(
            f'id="item-{historico.id}"', 0, primeira
        ), "a primeira recusa da página é a do primeiro recusado, que recusa.js foca"
        assert corpo.count("data-recusa") == 2

    def test_a_volta_com_o_parametro_do_lote_e_a_mesma_tela(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)

        resposta = client.get(reverse("portal:convocacao", args=[pessoa.id]) + "?lote=3")

        assert resposta.status_code == 200


def _secao(corpo, ident):
    """O trecho da `<section id=ident>` até o fechamento dela."""
    inicio = corpo.index(f'id="{ident}"')
    return corpo[inicio : corpo.index("</section>", inicio)]


class TestUmBotaoDeEnvioSo:
    """150, D-001 revista em 12/11/2026: um seletor por documento e um botão de envio só.

    O que o servidor desenha. Quem mostra a área, esconde o botão de cada cartão e diz o que foi
    escolhido é `varios.js` (`tests/javascript/varios.test.js`); aqui se prova que tudo nasce no
    lugar certo, e escondido, para que a tela sem script continue a de antes (FR-5612).
    """

    def test_a_area_e_uma_so_no_fim_do_que_falta_e_nasce_escondida(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)

        corpo = tela(client, pessoa)

        assert corpo.count("data-envio-dos-documentos") == 1, "FR-5621, SC-1808"
        falta = _secao(corpo, "o-que-falta")
        assert "data-envio-dos-documentos" in falta
        assert falta.rindex("cartao-do-documento") < falta.index("data-envio-dos-documentos"), (
            "depois do último cartão"
        )
        assert (
            '<div class="envio-dos-documentos" id="envio-dos-documentos" tabindex="-1" '
            "data-envio-dos-documentos hidden>"
        ) in corpo
        assert "data-enviar-os-escolhidos disabled>Enviar documentos</button>" in corpo
        assert ">Escolha o arquivo PDF de cada documento acima.</p>" in corpo

    def test_a_frase_de_como_se_envia_com_e_sem_script(self, aluno, gestor, client, settings):
        settings.ARQUIVOS_CANDIDATOS_LIMITE_BYTES = 10 * 1024 * 1024
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)

        falta = _secao(tela(client, pessoa), "o-que-falta")

        com_script = falta.index("data-instrucao-com-script hidden>")
        assert "Escolha um arquivo PDF, de até 10 MB, para cada documento." in falta
        assert '<noscript><p class="instrucao-do-envio">Envie um documento de cada vez' in falta
        assert com_script < falta.index("cartao-do-documento"), "antes do primeiro cartão (FR-5612)"

    def test_o_cartao_traz_o_estado_da_escolha_e_o_remover_escondidos(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        alvo = item(convocacao, CERTIDAO)

        cartao = tela(client, pessoa).split(f'id="item-{alvo.id}"')[1].split("</li>")[0]

        assert "data-estado-da-escolha hidden>Selecionado — ainda não enviado.</span>" in cartao
        assert "data-remover-escolha hidden>Remover a escolha" in cartao
        assert '<span class="oculto">: Certidão de nascimento ou casamento</span>' in cartao
        assert "data-rotulo-trocar hidden>Trocar arquivo</span>" in cartao
        assert "Ir ao botão de envio" not in cartao, "o cartão está acima do botão"
        assert 'data-envio-do-cartao>Enviar<span class="oculto">' in cartao, "o envio sem script"

    def test_a_substituicao_depois_do_botao_liga_a_ele(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        enviada = item(convocacao, CERTIDAO)
        _no_lote(client, pessoa, enviada, "1/1", cenarios.pdf(b"certidao"))

        corpo = tela(client, pessoa)

        assert "data-envio-dos-documentos" in _secao(corpo, "o-que-falta")
        apresentou = _secao(corpo, "o-que-voce-ja-apresentou")
        assert "data-envio-dos-documentos" not in apresentou
        assert f'id="item-{enviada.id}"' in apresentou
        assert (
            '<a class="ir-ao-envio" href="#envio-dos-documentos">Ir ao botão de envio</a>'
            in apresentou
        )

    def test_sem_nada_a_enviar_no_que_falta_a_area_vai_ao_que_ja_apresentou(
        self, aluno, gestor, client
    ):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        requisitos = (CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO, RESIDENCIA)
        for posicao, requisito in enumerate(requisitos, start=1):
            _no_lote(
                client,
                pessoa,
                item(convocacao, requisito),
                f"{posicao}/4",
                cenarios.pdf(b"%d" % posicao),
            )

        corpo = tela(client, pessoa)

        assert corpo.count("data-envio-dos-documentos") == 1
        apresentou = _secao(corpo, "o-que-voce-ja-apresentou")
        assert "data-envio-dos-documentos" in apresentou
        assert "data-instrucao-com-script" in apresentou
        assert "data-envio-dos-documentos data-so-com-escolha hidden>" in apresentou
        assert "Para substituir um arquivo enviado, escolha o novo PDF" in apresentou
        assert "para cada documento" not in apresentou, "quem já mandou tudo não tem tarefa"
        assert "Ir ao botão de envio" not in apresentou, "o botão está no mesmo bloco"

    def test_depois_do_prazo_nao_ha_area(self, aluno, gestor, client):
        edital, _, _ = aluno
        pessoa, convocacao = cenarios.convocar_primeira(
            aluno, gestor, vencimento=timezone.now() + timedelta(minutes=1)
        )
        comunicar(edital, gestor, convocacao)
        entrar_como(client, pessoa)

        with mock.patch(
            "django.utils.timezone.now", return_value=timezone.now() + timedelta(days=2)
        ):
            corpo = tela(client, pessoa)

        assert "data-envio-dos-documentos" not in corpo
        assert "data-instrucao-com-script" not in corpo


class TestOPolishDoEnvioUnico:
    """150, revisão de 12/11/2026: as marcas que o polish do envio único pôs no servidor."""

    def test_a_tarefa_e_a_situacao_que_some_com_a_escolha(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        enviada = item(convocacao, CERTIDAO)
        _no_lote(client, pessoa, enviada, "1/1", cenarios.pdf(b"certidao"))
        a_enviar = item(convocacao, HISTORICO)

        corpo = tela(client, pessoa)

        cartao = corpo.split(f'id="item-{a_enviar.id}"')[1].split("</li>")[0]
        assert cartao.startswith(
            ' tabindex="-1" data-documento="Histórico escolar do ensino médio" data-tarefa>'
        )
        assert f'id="situacao-{a_enviar.id}" data-some-com-a-escolha>Falta enviar.</p>' in cartao
        recebido = corpo.split(f'id="item-{enviada.id}"')[1].split("</li>")[0]
        assert "data-tarefa" not in recebido.split(">")[0], "o recebido não é tarefa"
        assert "data-some-com-a-escolha" not in recebido, "a frase do recebido fica"

    def test_a_frase_no_singular_com_um_documento_so(self, aluno, gestor, client):
        pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
        entrar_como(client, pessoa)
        corpo = tela(client, pessoa)
        assert "para cada documento. Depois, envie todos de uma vez" in corpo

        from processo_seletivo.portal import obrigacoes

        with mock.patch.object(
            obrigacoes.Obrigacoes, "um_so_com_envio", new_callable=mock.PropertyMock
        ) as um_so:
            um_so.return_value = True
            corpo = tela(client, pessoa)

        assert "e envie pelo botão logo abaixo." in corpo
        assert "data-orientacao-da-escolha>Escolha o arquivo PDF acima.</p>" in corpo
        assert "para cada documento" not in corpo
