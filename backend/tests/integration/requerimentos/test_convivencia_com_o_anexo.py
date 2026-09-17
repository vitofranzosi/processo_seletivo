"""O requerimento estruturado convive com o Anexo em papel, e não decide nada por conta própria.

`FR-395` e `FR-402` são garantias de **não fazer** — e garantia de não fazer envelhece no primeiro
refactor, porque nada a exercita. Estas asserções são o que as mantêm de pé.

**As três coisas que esta feature MUST NOT fazer.** Não remover, por conta própria, o Documento
Exigido em que o Anexo hoje consiste; não passar a exigi-lo implicitamente quando o Edital não o
declarar; e não criar um **segundo acervo** de documentos — o documento de matrícula continua sendo
Documento Exigido do Edital, e não anexo do requerimento.

**Quem decide é o Edital.** Se o aceite eletrônico substitui a assinatura perante o Registro
Acadêmico é validação normativa daquele certame, e quem elabora a exerce — com a frase do
`como-preencher` da etapa Inscrição dizendo que o Anexo passa a ser dispensável (T048). O sistema
oferece a decisão; não a toma.

**A T048 cobre o texto; isto cobre o comportamento.** Um teste sobre a frase de ajuda provaria que
alguém escreveu a orientação, e não que o sistema a respeita.
"""

import pytest

from processo_seletivo.inscricoes.models import DocumentoSubmetido
from processo_seletivo.requerimentos.application import preencher
from processo_seletivo.requerimentos.domain import nomes
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula
from tests.fixtures.candidato import MARIA
from tests.fixtures.requerimento import DECLARACAO, pronta_para_enviar, submeter

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def enviar_o_requerimento(inscricao, campos):
    preencher.abrir_rascunho(inscricao=inscricao)
    preencher.gravar(inscricao=inscricao, dados=campos, expected_revision=None)
    return preencher.enviar(
        identidade=MARIA,
        inscricao=inscricao,
        versao_exibida_id=preencher._conteudo(inscricao).id,
        declaracao_exibida=DECLARACAO,
        aceite=True,
    )


def documentos_do_edital(edital):
    from processo_seletivo.publicacoes.application import selectors

    conteudo = selectors.selecao_publica(edital_id=edital.id).content
    return conteudo.get("documentRequirements") or []


class TestOsDoisConvivem:
    def test_o_edital_com_os_dois_funciona_do_comeco_ao_fim(
        self, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        """O caso da transição: o Edital ainda pede o Anexo **e** já coleta o estruturado.

        É o estado real de um certame que adota a feature sem reescrever o Edital inteiro, e ele
        tem de funcionar — senão a adoção exigiria uma Retificação antes de qualquer benefício.
        """
        assert documentos_do_edital(selecao_na_inscricao), "o Edital declara Documentos Exigidos"
        inscricao = pronta_para_enviar(selecao_na_inscricao)

        enviar_o_requerimento(inscricao, campos_declarados)
        enviada = submeter(inscricao)

        assert enviada.status == enviada.Status.SUBMETIDA
        assert DocumentoSubmetido.objects.filter(inscricao=inscricao).count() == 2

    def test_enviar_o_requerimento_nao_remove_documento_exigido_nenhum(
        self, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        """**O sistema não retira o Anexo por conta própria** (`FR-395`).

        Ele não pode: o Documento Exigido é conteúdo **publicado**, e removê-lo seria reescrever um
        ato imutável. Quem o retira é uma Retificação, praticada por quem elabora — e a asserção
        aqui é sobre o que o envio faz, que é nada.
        """
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        antes = list(documentos_do_edital(selecao_na_inscricao))
        submetidos_antes = DocumentoSubmetido.objects.filter(inscricao=inscricao).count()

        enviar_o_requerimento(inscricao, campos_declarados)

        assert documentos_do_edital(selecao_na_inscricao) == antes
        assert DocumentoSubmetido.objects.filter(inscricao=inscricao).count() == submetidos_antes

    def test_o_requerimento_nao_pede_reenvio_do_que_a_inscricao_ja_recebeu(
        self, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        """`FR-402`: o envio conclui sem tocar num único documento.

        A pessoa já entregou RG e diploma na inscrição. Pedi-los de novo aqui seria o retrabalho
        que esta feature existe para eliminar — e a prova é o envio concluir com a contagem
        intacta.
        """
        inscricao = pronta_para_enviar(selecao_na_inscricao)

        enviado = enviar_o_requerimento(inscricao, campos_declarados)

        assert enviado.status == nomes.ENVIADO
        assert DocumentoSubmetido.objects.filter(inscricao=inscricao).count() == 2


class TestNaoHaSegundoAcervo:
    def test_o_requerimento_nao_tem_relacao_com_arquivo(self):
        """`FR-402`: nenhuma chave estrangeira do requerimento aponta documento ou arquivo.

        **A asserção é sobre o modelo**, e não sobre a tela: um segundo acervo nasceria como um
        campo — `anexo`, `comprovante`, `arquivo` — e a tela viria depois. Prendê-lo aqui é pegá-lo
        no momento em que ele é uma linha de modelo, e não uma feature inteira.
        """
        campos = {campo.name for campo in RequerimentoDeMatricula._meta.get_fields()}
        suspeitos = {
            campo
            for campo in campos
            if any(
                palavra in campo
                for palavra in ("arquivo", "anexo", "documento", "comprovante", "upload")
            )
        }

        assert suspeitos == set(), f"o requerimento criou acervo próprio de documentos: {suspeitos}"

    def test_nenhum_campo_do_requerimento_guarda_caminho_de_arquivo(self):
        """`FileField` e `ImageField` são o outro jeito de o segundo acervo nascer."""
        from django.db import models

        guardam_arquivo = [
            campo.name
            for campo in RequerimentoDeMatricula._meta.get_fields()
            if isinstance(campo, models.FileField)
        ]

        assert guardam_arquivo == []


class TestOEditalSemAnexo:
    def test_edital_que_nao_declara_o_anexo_funciona_igual(
        self,
        api_client,
        manager_headers,
        process_payload,
        raiz_de_arquivos,
        candidatos_registrados,
        campos_declarados,
    ):
        """**O requerimento não passa a exigir o Anexo implicitamente** (`FR-395`).

        É a metade que envelhece mal: um Edital que adota o estruturado e retira o papel é o
        destino natural da feature, e ele tem de funcionar sem que nada procure o Documento que
        deixou de existir.
        """
        from tests.fixtures.requerimento import pronta_sem_documentos, publicar_sem_documentos

        edital = publicar_sem_documentos(
            api_client, manager_headers, process_payload, "AT_ENROLLMENT"
        )
        assert documentos_do_edital(edital) == [], "o cenário é o Edital que não exige nada"
        inscricao = pronta_sem_documentos(edital)

        enviado = enviar_o_requerimento(inscricao, campos_declarados)
        enviada = submeter(inscricao)

        assert enviado.status == nomes.ENVIADO
        assert enviada.status == enviada.Status.SUBMETIDA
        assert DocumentoSubmetido.objects.filter(inscricao=inscricao).count() == 0
