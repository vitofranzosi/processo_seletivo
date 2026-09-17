"""A declaração do Requerimento de Matrícula, composta por quem elabora (029, `US3`, T050).

**Este arquivo existe para esta feature não repetir o `maxInscricoesPorCandidato`.** Aquele campo
foi publicado sem caminho de escrita na interface: o conteúdo o carregava, o domínio o respeitava,
e quem elaborava não tinha onde declará-lo — o único jeito de defini-lo era por API ou fixture. A
`T-002` registrou o achado, e o que o impede de acontecer de novo é justamente um teste que compõe
**pela tela**, publica, e lê o resultado no conteúdo publicado.

**E a etapa é a `Inscrição`, não uma nova.** É onde o período e os Documentos Exigidos já são
compostos — onde quem elabora decide o que se pede ao candidato.
"""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from processo_seletivo.requerimentos.domain import nomes
from tests.fixtures.edital import actor_headers, identificador
from tests.fixtures.selecao import rascunho_de_selecao
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

DECLARACAO = "Declaro, sob as penas da Lei, que as informações prestadas são verdadeiras."


@pytest.fixture
def edital_com_perfis(api_client, manager_headers, process_payload):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho_de_selecao(),
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="requerimento-etapa-0001"),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    edital.refresh_from_db()
    return edital


def campos(**ajustes):
    base = {
        "periodo-inscricoes": identificador(402, 0),
        "documento-0-id": identificador(408, 0),
        "documento-0-key": "identificacao",
        "documento-0-name": "Documento de identificação",
        "documento-0-instructions": "Frente e verso.",
        "documento-0-required": "on",
        "documento-0-order": "1",
        "documento-0-profileId": "",
        "documento-0-modalityId": "",
        "requerimento-momento": "",
        "requerimento-declaracao": "",
    }
    base.update(ajustes)
    return base


def compor(client, edital, **ajustes):
    return client.post(
        reverse("interface:compor-etapa", args=[edital.id, "inscricao"]), campos(**ajustes)
    )


class TestAEtapaOferecOsCampos:
    def test_a_etapa_inscricao_oferece_o_momento_e_o_texto(
        self, client, seletor_ligado, edital_com_perfis
    ):
        """**Nenhuma etapa nova.** A decisão mora onde as outras sobre o candidato já moram."""
        identificar(client, "ana.elaboradora", ["elaborador"])

        corpo = client.get(
            reverse("interface:compor-etapa", args=[edital_com_perfis.id, "inscricao"])
        ).content.decode()

        assert 'id="requerimento-momento"' in corpo
        assert 'for="requerimento-momento"' in corpo
        assert 'id="requerimento-declaracao"' in corpo
        assert 'for="requerimento-declaracao"' in corpo
        assert "Este Edital não pede Requerimento de Matrícula" in corpo, "a ausência é o padrão"

    def test_o_como_preencher_diz_que_o_anexo_em_papel_fica_dispensavel(
        self, client, seletor_ligado, edital_com_perfis
    ):
        """T048 e `R-3`: sem esta frase, ninguém exerce a decisão e a pessoa faz as duas coisas.

        A mitigação é **texto**, e não mecanismo: o sistema não remove o Documento Exigido por
        conta própria nem o exige por conta própria — quem decide é o Edital (`FR-395`).
        """
        identificar(client, "ana.elaboradora", ["elaborador"])

        corpo = client.get(
            reverse("interface:compor-etapa", args=[edital_com_perfis.id, "inscricao"])
        ).content.decode()

        assert "passa a ser dispensável" in corpo
        assert "duas vezes" in corpo


class TestGravar:
    def test_o_momento_e_o_texto_ficam_gravados(self, client, seletor_ligado, edital_com_perfis):
        identificar(client, "ana.elaboradora", ["elaborador"])

        resposta = compor(
            client,
            edital_com_perfis,
            **{
                "requerimento-momento": nomes.NA_INSCRICAO,
                "requerimento-declaracao": DECLARACAO,
            },
        )

        edital_com_perfis.refresh_from_db()
        assert resposta.status_code == 302
        assert edital_com_perfis.requerimento_momento == nomes.NA_INSCRICAO
        assert edital_com_perfis.requerimento_declaracao == DECLARACAO

    def test_gravar_o_requerimento_nao_apaga_perfis_nem_documentos(
        self, client, seletor_ligado, edital_com_perfis
    ):
        """**Ato próprio, e não `replace_draft`**: aquele apagaria o que não viajasse junto.

        Os dois campos são de **raiz** do Edital, e `replace_draft` não os carrega. Sem o ato
        próprio, gravar a declaração exigiria passar pelo comando que substitui o rascunho inteiro
        — e é um caminho que já produziu perda de dado neste repositório.
        """
        identificar(client, "ana.elaboradora", ["elaborador"])

        compor(
            client,
            edital_com_perfis,
            **{
                "requerimento-momento": nomes.NA_CONVOCACAO,
                "requerimento-declaracao": DECLARACAO,
            },
        )

        edital_com_perfis.refresh_from_db()
        assert edital_com_perfis.perfis.count() == 2
        assert edital_com_perfis.requerimento_momento == nomes.NA_CONVOCACAO

    def test_apagar_o_momento_apaga_o_texto_junto(self, client, seletor_ligado, edital_com_perfis):
        """Texto de declaração sem momento é norma órfã: ninguém a lê e ninguém a aceita.

        Deixá-la para trás a faria aparecer na tela de Retificação como campo de um requerimento
        que o Edital não pede.
        """
        identificar(client, "ana.elaboradora", ["elaborador"])
        compor(
            client,
            edital_com_perfis,
            **{
                "requerimento-momento": nomes.NA_INSCRICAO,
                "requerimento-declaracao": DECLARACAO,
            },
        )

        compor(client, edital_com_perfis, **{"requerimento-momento": ""})

        edital_com_perfis.refresh_from_db()
        assert edital_com_perfis.requerimento_momento == ""
        assert edital_com_perfis.requerimento_declaracao == ""

    def test_o_ato_fica_na_trilha_com_o_momento(self, client, seletor_ligado, edital_com_perfis):
        """Quem audita precisa saber **quando** o Edital passou a pedir isto."""
        from processo_seletivo.auditoria.models import RegistroAuditoria

        identificar(client, "ana.elaboradora", ["elaborador"])

        compor(
            client,
            edital_com_perfis,
            **{
                "requerimento-momento": nomes.NA_INSCRICAO,
                "requerimento-declaracao": DECLARACAO,
            },
        )

        registro = RegistroAuditoria.objects.filter(operation="ALTERAR_REQUERIMENTO").latest(
            "occurred_at"
        )
        assert nomes.NA_INSCRICAO in registro.reason
        assert DECLARACAO not in registro.reason, "o texto inteiro já está no conteúdo publicado"

    def test_a_operacao_tem_rotulo_legivel_na_trilha(self):
        from processo_seletivo.interface.views import OPERACOES

        assert OPERACOES.get("ALTERAR_REQUERIMENTO", "ALTERAR_REQUERIMENTO") != (
            "ALTERAR_REQUERIMENTO"
        )


class TestAPublicacao:
    """`SC-136`: momento declarado sem texto **recusa a publicação**, e a pendência tem caminho.

    **Impeditivo, e não advertência.** O texto é o que o candidato aceita, e é o que o cancelamento
    por informação falsa invoca; sem ele, o aceite guardaria o resumo de uma string vazia — um
    aceite de nada, gravado como se fosse aceite de alguma coisa. E publicação é ato imutável: o
    Edital nasceria com um requerimento inaceitável, e a correção não seria digitar de novo.
    """

    def achados(self, edital):
        from processo_seletivo.editais.domain.validation import (
            ATO_DE_PUBLICACAO,
            validate_for_publication,
        )
        from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot

        return validate_for_publication(edital_snapshot(edital), ato=ATO_DE_PUBLICACAO)

    def test_momento_sem_texto_impede_a_publicacao(self, client, seletor_ligado, edital_com_perfis):
        identificar(client, "ana.elaboradora", ["elaborador"])
        # O texto é apagado **por fora** do comando: ele próprio recusa a combinação ao gravar, e o
        # que se exercita aqui é a conferência de publicação — a segunda camada, que vale também
        # para conteúdo que chegou por outro caminho.
        compor(
            client,
            edital_com_perfis,
            **{"requerimento-momento": nomes.NA_INSCRICAO, "requerimento-declaracao": "   "},
        )
        Edital.objects.filter(pk=edital_com_perfis.pk).update(
            requerimento_momento=nomes.NA_INSCRICAO, requerimento_declaracao=""
        )
        edital_com_perfis.refresh_from_db()

        codigos = [achado.code for achado in self.achados(edital_com_perfis)]

        assert "matriculation_request_without_declaration" in codigos

    def test_a_pendencia_leva_a_etapa_inscricao_e_e_corrigivel(self):
        """`FR-007`: apontar defeito e informar que não há caminho é pior do que não apontar."""
        from processo_seletivo.interface.views import _destino

        etapa, ancora, corrigivel = _destino(
            "matriculationRequest/declarationText", "matriculation_request_without_declaration"
        )

        assert etapa == "inscricao"
        assert ancora == "#inscricao-requerimento"
        assert corrigivel is True

    def test_edital_sem_declaracao_publica_normalmente(
        self, client, seletor_ligado, edital_com_perfis
    ):
        """A ausência é o padrão, e ela não é achado nenhum."""
        identificar(client, "ana.elaboradora", ["elaborador"])
        compor(client, edital_com_perfis)

        edital_com_perfis.refresh_from_db()
        codigos = [achado.code for achado in self.achados(edital_com_perfis)]

        assert "matriculation_request_without_declaration" not in codigos

    def test_com_texto_declarado_nao_ha_achado(self, client, seletor_ligado, edital_com_perfis):
        identificar(client, "ana.elaboradora", ["elaborador"])
        compor(
            client,
            edital_com_perfis,
            **{
                "requerimento-momento": nomes.NA_INSCRICAO,
                "requerimento-declaracao": DECLARACAO,
            },
        )

        edital_com_perfis.refresh_from_db()
        codigos = [achado.code for achado in self.achados(edital_com_perfis)]

        assert "matriculation_request_without_declaration" not in codigos


class TestARevisao:
    """T046: quem revisa antes de publicar um ato imutável precisa ver o que o Edital vai exigir.

    Sem o bloco, a única confirmação do texto da declaração seria a tela onde ele foi digitado — e
    depois da publicação a correção não é digitar de novo, e sim Retificar.
    """

    def blocos_de(self, edital):
        from processo_seletivo.interface.revisao import blocos
        from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot

        return blocos(edital_snapshot(edital))

    def test_o_bloco_mostra_o_momento_por_extenso_e_o_texto_inteiro(
        self, client, seletor_ligado, edital_com_perfis
    ):
        identificar(client, "ana.elaboradora", ["elaborador"])
        compor(
            client,
            edital_com_perfis,
            **{
                "requerimento-momento": nomes.NA_INSCRICAO,
                "requerimento-declaracao": DECLARACAO,
            },
        )
        edital_com_perfis.refresh_from_db()

        bloco = next(
            b
            for b in self.blocos_de(edital_com_perfis)
            if b["titulo"] == "Requerimento de Matrícula"
        )

        assert bloco["etapa"] == "inscricao", "o caminho de volta leva a onde se corrige"
        assert nomes.NA_INSCRICAO not in bloco["itens"][0]["titulo"], "por extenso, não o código"
        assert "no ato da inscrição" in bloco["itens"][0]["titulo"]
        assert DECLARACAO in bloco["itens"][0]["linhas"], "inteiro, e não cortado"

    def test_sem_declaracao_o_bloco_nao_aparece(self, client, seletor_ligado, edital_com_perfis):
        """A ausência é o padrão: uma linha dizendo *"não exige"* em todo Edital seria ruído."""
        identificar(client, "ana.elaboradora", ["elaborador"])
        compor(client, edital_com_perfis)
        edital_com_perfis.refresh_from_db()

        titulos = [b["titulo"] for b in self.blocos_de(edital_com_perfis)]

        assert "Requerimento de Matrícula" not in titulos
