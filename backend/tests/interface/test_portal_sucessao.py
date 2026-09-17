"""*Conferir e atualizar* no canal do candidato, e o anterior que continua legível (029, `US5`).

**Duas coisas precisam coexistir para o botão aparecer** (`FR-410`): requerimento enviado **e**
chamada em aberto. Fora disso ele não aparece — e o comando recusa mesmo assim, porque a tela não é
fronteira de segurança.

**E o segundo identificador da rota é o lugar clássico de vazar.** `_inscricao_do_titular` confere a
**Inscrição**; o identificador do requerimento anterior ficaria sem dono se a view o resolvesse com
`get(pk=…)`. Aqui ele é procurado **dentro da cadeia da Inscrição do titular**, e o de outra pessoa
é indistinguível de inexistente (`FR-399`).
"""

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.portal.identidade import CHAVE_SESSAO
from processo_seletivo.requerimentos.application import exigencia, preencher
from processo_seletivo.requerimentos.domain import nomes
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula
from tests.fixtures.candidato import MARIA
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    from tests.fixtures.corte import regra
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
        prefixo="requerimento-029-portal-suc",
        geral=2,
        cut=regra(surplusCount=1),
        publicar=publicar_declarando,
    )


def entrar_como(client, inscricao):
    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=inscricao.identity_subject, defaults={"created_at": timezone.now()}
    )
    sessao = client.session
    sessao[CHAVE_SESSAO] = str(registro.pk)
    sessao.save()


def praticar(edital, gestor, inscricao, **kwargs):
    return Convocacao.objects.get(pk=convocar(edital, gestor, inscricao, **kwargs)["id"])


def enviar(inscricao):
    versao = preencher._conteudo(inscricao)
    return preencher.enviar(
        identidade=MARIA,
        inscricao=inscricao,
        versao_exibida_id=versao.id,
        declaracao_exibida=preencher.declaracao_publicada(versao.content),
        aceite=True,
    )


@pytest.fixture
def convocado_com_envio(cenario, gestor, campos_declarados, client):
    edital, _, inscricoes = cenario
    pessoa = inscricoes[0]
    chamada = praticar(edital, gestor, pessoa, idempotency_key="portal-suc-1")
    preencher.abrir_rascunho(inscricao=pessoa)
    preencher.gravar(inscricao=pessoa, dados=campos_declarados, expected_revision=None)
    enviado = enviar(pessoa)
    entrar_como(client, pessoa)
    return {"edital": edital, "pessoa": pessoa, "chamada": chamada, "requerimento": enviado}


def tela(client, inscricao):
    return client.get(reverse("portal:requerimento", args=[inscricao.id])).content.decode()


class TestAOfertaDeAtualizar:
    def test_enviado_com_chamada_em_aberto_oferece_conferir_e_atualizar(
        self, client, convocado_com_envio
    ):
        corpo = tela(client, convocado_com_envio["pessoa"])

        assert "Conferir e atualizar" in corpo
        assert "?atualizando=1" in corpo, "é um link, e não um botão que pratica ato"

    def test_desfechada_a_chamada_a_oferta_some(self, client, convocado_com_envio, gestor):
        """A vez passou: corrigir agora precisaria de uma chamada que não existe (`FR-408`)."""
        desfechar(
            actor=gestor,
            processo_id=convocado_com_envio["edital"].processo_id,
            convocacao_id=convocado_com_envio["chamada"].id,
            especie=nomes_da_convocacao.ACEITE,
            fundamento="Manifestação registrada em processo.",
            idempotency_key="portal-suc-aceite",
            correlation_id="teste",
        )

        corpo = tela(client, convocado_com_envio["pessoa"])

        assert "Conferir e atualizar" not in corpo
        assert "Recebemos em" in corpo, "o enviado continua legível"

    def test_o_comando_recusa_mesmo_sem_a_tela_oferecer(
        self, client, convocado_com_envio, gestor, campos_declarados
    ):
        """**A tela não é fronteira de segurança** (Princípio IV): o `POST` encontra a recusa.

        Esconder o botão é experiência; o que impede a sucessão não autorizada é o comando.
        """
        desfechar(
            actor=gestor,
            processo_id=convocado_com_envio["edital"].processo_id,
            convocacao_id=convocado_com_envio["chamada"].id,
            especie=nomes_da_convocacao.ACEITE,
            fundamento="Manifestação registrada em processo.",
            idempotency_key="portal-suc-aceite-2",
            correlation_id="teste",
        )

        resposta = client.post(
            reverse("portal:requerimento", args=[convocado_com_envio["pessoa"].id]),
            {**campos_declarados, "atualizando": "1", "bairro": "Tentando"},
        )

        assert "convocação aguardando a sua resposta" in resposta.content.decode()
        assert exigencia.vigente_de(convocado_com_envio["pessoa"]).status == nomes.ENVIADO

    def test_conferir_abre_os_campos_sem_criar_linha(
        self, client, convocado_com_envio, campos_declarados
    ):
        """**O achado que reabriu esta história.** Conferir é um `GET`, e não pratica ato.

        Enquanto ele criava a linha, bastava clicar e sair para o requerimento **enviado** sumir da
        tela da pessoa — vigente é a folha da cadeia — e o dossiê de quem conduz passar a exibir um
        rascunho que ninguém pediu (`FR-406`).
        """
        antes = RequerimentoDeMatricula.objects.count()

        corpo = client.get(
            reverse("portal:requerimento", args=[convocado_com_envio["pessoa"].id])
            + "?atualizando=1"
        ).content.decode()

        assert RequerimentoDeMatricula.objects.count() == antes, "conferir não cria linha"
        assert 'id="nome_da_mae"' in corpo, "os campos abrem para edição"
        assert campos_declarados["nome_da_mae"] in corpo, "preenchidos com o que foi enviado"
        assert exigencia.vigente_de(convocado_com_envio["pessoa"]).status == nomes.ENVIADO

    def test_salvar_sem_mudar_nada_recusa_e_nao_cria_linha(
        self, client, convocado_com_envio, campos_declarados
    ):
        """`FR-410`: sucessor sem mudança não nasce — e a recusa chega antes da gravação."""
        antes = RequerimentoDeMatricula.objects.count()

        corpo = client.post(
            reverse("portal:requerimento", args=[convocado_com_envio["pessoa"].id]),
            {**campos_declarados, "atualizando": "1"},
        ).content.decode()

        assert "Nada mudou" in corpo
        assert RequerimentoDeMatricula.objects.count() == antes
        assert exigencia.vigente_de(convocado_com_envio["pessoa"]).status == nomes.ENVIADO

    def test_salvar_com_mudanca_cria_o_sucessor(
        self, client, convocado_com_envio, campos_declarados
    ):
        client.post(
            reverse("portal:requerimento", args=[convocado_com_envio["pessoa"].id]),
            {**campos_declarados, "atualizando": "1", "bairro": "Praia do Canto"},
        )

        vigente = exigencia.vigente_de(convocado_com_envio["pessoa"])
        assert vigente.status == nomes.RASCUNHO
        assert vigente.requerimento_anterior_id == convocado_com_envio["requerimento"].id
        assert vigente.bairro == "Praia do Canto"
        assert vigente.nome_da_mae == campos_declarados["nome_da_mae"], "o resto veio copiado"


class TestOAnterior:
    def sucessor_enviado(self, client, contexto, campos_declarados):
        client.post(
            reverse("portal:requerimento", args=[contexto["pessoa"].id]),
            {**campos_declarados, "atualizando": "1", "bairro": "Outro Bairro"},
        )
        return enviar(contexto["pessoa"])

    def test_o_link_para_o_anterior_aparece_e_a_tela_dele_abre(
        self, client, convocado_com_envio, campos_declarados
    ):
        """`UX-059`: corrigir não apaga, e a pessoa precisa poder ver o que declarou antes."""
        self.sucessor_enviado(client, convocado_com_envio, campos_declarados)
        anterior = convocado_com_envio["requerimento"]

        corpo = tela(client, convocado_com_envio["pessoa"])

        endereco = reverse(
            "portal:requerimento-anterior",
            args=[convocado_com_envio["pessoa"].id, anterior.id],
        )
        assert endereco in corpo
        pagina = client.get(endereco).content.decode()
        assert campos_declarados["bairro"] in pagina, "o bairro antigo, e não o corrigido"
        assert "corrigir não apaga" in pagina
        assert 'id="bairro"' not in pagina, "sem campo editável"

    def test_um_requerimento_de_outra_pessoa_e_recusado_como_inexistente(
        self, client, cenario, gestor, convocado_com_envio, campos_declarados
    ):
        """`FR-399` e o IDOR do **segundo** identificador.

        A titularidade confere a Inscrição; o identificador do requerimento ficaria sem dono se a
        view o resolvesse com `get(pk=…)`. É o modo clássico de uma rota com dois identificadores
        vazar, e ele só aparece quando o segundo entra.
        """
        edital, _, inscricoes = cenario
        outra = inscricoes[1]
        praticar(edital, gestor, outra, idempotency_key="portal-suc-outra")
        preencher.abrir_rascunho(inscricao=outra)
        preencher.gravar(inscricao=outra, dados=campos_declarados, expected_revision=None)
        alheio = enviar(outra)

        resposta = client.get(
            reverse(
                "portal:requerimento-anterior",
                args=[convocado_com_envio["pessoa"].id, alheio.id],
            )
        )

        assert resposta.status_code == 404

    def test_identificador_inexistente_devolve_o_mesmo_404(self, client, convocado_com_envio):
        """As duas respostas são iguais — distinguir entregaria o mapa do que existe."""
        import uuid

        alheio = client.get(
            reverse(
                "portal:requerimento-anterior",
                args=[convocado_com_envio["pessoa"].id, uuid.uuid4()],
            )
        )

        assert alheio.status_code == 404

    def test_qualquer_enviado_da_cadeia_e_legivel_e_o_rascunho_nao(
        self, client, convocado_com_envio, campos_declarados
    ):
        """O filtro é **cadeia + enviado**, e não "foi sucedido".

        Manter a condição em "é da minha Inscrição e foi enviado" é o que torna a regra simples de
        conferir: um rascunho abandonado não é histórico — ninguém o declarou —, e um identificador
        de fora da cadeia é indistinguível de inexistente. Amarrar a condição a *"tem sucessor"*
        acrescentaria um terceiro caso sem acrescentar proteção nenhuma.
        """
        enviado = client.get(
            reverse(
                "portal:requerimento-anterior",
                args=[
                    convocado_com_envio["pessoa"].id,
                    convocado_com_envio["requerimento"].id,
                ],
            )
        )
        client.post(
            reverse("portal:requerimento", args=[convocado_com_envio["pessoa"].id]),
            {**campos_declarados, "atualizando": "1", "bairro": "Um Outro"},
        )
        rascunho = exigencia.vigente_de(convocado_com_envio["pessoa"])

        assert enviado.status_code == 200, "enviado e na cadeia — é legível"
        assert (
            client.get(
                reverse(
                    "portal:requerimento-anterior",
                    args=[convocado_com_envio["pessoa"].id, rascunho.id],
                )
            ).status_code
            == 404
        ), "rascunho não é histórico: ninguém o declarou"
