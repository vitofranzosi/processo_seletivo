"""O teto de inscrições por candidato, declarado na composição (015, FR-063; RC-12).

**O teto já era executado, publicado e retificável, e não tinha onde nascer.** A `FR-063` diz que o
Edital MUST poder publicá-lo; até esta correção, o valor só chegava ao Edital pelo ORM, pelo
`seed_demo` ou por Retificação depois de publicado. O que impede de acontecer de novo é o que a 029
já fez para o Requerimento de Matrícula: compor **pela tela**, publicar, e ler o resultado no
conteúdo publicado, no documento e na submissão.

**O formulário é reenviado como a tela o devolve**, e não como o teste o imaginaria. É o que prova o
round-trip: o valor gravado volta no campo, e reenviar a etapa sem tocá-lo não o perde.
"""

import re
from datetime import timedelta
from html.parser import HTMLParser

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.editais.application.teto import OPERACAO, atualizar_teto_de_inscricoes
from processo_seletivo.editais.domain.teto import teto_declarado
from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    gravar_dados,
)
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.interface import forms
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import DocumentoPublicado
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, PERFIL_DOCENTE, PERFIL_TECNICO, pdf
from tests.fixtures.edital import actor_headers
from tests.fixtures.selecao import (
    DOCUMENTO_DE_TODOS,
    DOCUMENTO_DO_PERFIL,
    publicar_selecao,
    rascunho_aberto_com_documentos,
    rascunho_de_selecao,
)
from tests.interface.conftest import identificar
from tests.unit.publicacoes.test_pdf import texto_de

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

DECLARACOES = {"veracidade": True, "ciencia": True}
FRASE_DE_UM = "Cada candidato poderá ter apenas 1 inscrição enviada neste Edital."


class _Campos(HTMLParser):
    """Os pares nome → valor que o navegador enviaria a partir do formulário da etapa."""

    def __init__(self):
        super().__init__()
        self.campos = {}
        self._textarea = None
        self._select = None

    def handle_starttag(self, tag, atributos):
        atributos = dict(atributos)
        nome = atributos.get("name")
        if tag == "input" and nome and "form" not in atributos:
            marcavel = atributos.get("type") in ("radio", "checkbox")
            if marcavel and "checked" not in atributos:
                return
            # Marcado e sem `value`, o navegador envia "on" — e é isso que o servidor lê.
            self.campos[nome] = atributos.get("value") or ("on" if marcavel else "")
        elif tag == "textarea" and nome:
            self._textarea = nome
            self.campos[nome] = ""
        elif tag == "select" and nome:
            self._select = nome
            self.campos.setdefault(nome, "")
        elif tag == "option" and self._select and "selected" in atributos:
            self.campos[self._select] = atributos.get("value") or ""

    def handle_endtag(self, tag):
        if tag == "textarea":
            self._textarea = None
        elif tag == "select":
            self._select = None

    def handle_data(self, dados):
        if self._textarea:
            self.campos[self._textarea] += dados


def _url(edital, etapa="inscricao"):
    return reverse("interface:compor-etapa", args=[edital.id, etapa])


def formulario_da_etapa(client, edital, etapa="inscricao"):
    """O formulário da etapa, só ele: a página tem outros, e os campos deles não viajam juntos."""
    corpo = client.get(_url(edital, etapa)).content.decode()
    inicio = corpo.index('id="formulario"')
    leitor = _Campos()
    leitor.feed(corpo[inicio : corpo.index("</form>", inicio)])
    leitor.campos.pop("csrfmiddlewaretoken", None)
    return leitor.campos


def reenviar(client, edital, etapa="inscricao", **ajustes):
    """Grava a etapa com o que a tela mostra, alterado só no que o teste nomeia."""
    campos = formulario_da_etapa(client, edital, etapa)
    campos.update(ajustes)
    return client.post(_url(edital, etapa), campos)


def declarar_teto(client, edital, valor):
    return reenviar(client, edital, **{"teto-inscricoes": valor})


@pytest.fixture
def em_elaboracao(api_client, manager_headers, process_payload):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho_aberto_com_documentos(timezone.now()),
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="teto-etapa-0001"),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    edital.refresh_from_db()
    return edital


@pytest.fixture
def elaboradora(client, seletor_ligado):
    identificar(client, "ana.elaboradora", ["elaborador"])
    return client


class TestAEtapa:
    def test_o_campo_esta_na_secao_do_periodo_e_nasce_vazio(self, elaboradora, em_elaboracao):
        """**Nada de valor por omissão**: vazio é sem limite, que é o comportamento de sempre."""
        corpo = elaboradora.get(_url(em_elaboracao)).content.decode()

        inicio = corpo.index('id="inscricao-periodo"')
        periodo = corpo[inicio : corpo.index("</section>", inicio)]
        assert 'for="teto-inscricoes"' in periodo
        assert "Inscrições por candidato neste Edital" in periodo
        assert "Deixe em branco para não limitar" in periodo
        assert "rascunho abandonado não consome" in periodo
        assert formulario_da_etapa(elaboradora, em_elaboracao)["teto-inscricoes"] == ""

    def test_o_campo_e_descrito_pela_ajuda(self, elaboradora, em_elaboracao):
        corpo = elaboradora.get(_url(em_elaboracao)).content.decode()
        campo = corpo[corpo.index('id="teto-inscricoes"') - 200 : corpo.index('id="ajuda-teto"')]

        assert 'aria-describedby="ajuda-teto"' in campo
        assert 'min="1"' in campo


class TestGravar:
    def test_o_teto_declarado_fica_gravado_e_volta_no_campo(self, elaboradora, em_elaboracao):
        resposta = declarar_teto(elaboradora, em_elaboracao, "1")

        em_elaboracao.refresh_from_db()
        assert resposta.status_code == 302, resposta.content
        assert em_elaboracao.max_inscricoes_por_candidato == 1
        assert formulario_da_etapa(elaboradora, em_elaboracao)["teto-inscricoes"] == "1"

    def test_reenviar_a_etapa_sem_tocar_no_campo_preserva_o_teto(self, elaboradora, em_elaboracao):
        """O round-trip: o que a tela devolve, gravado de novo, é o mesmo Edital."""
        declarar_teto(elaboradora, em_elaboracao, "2")

        resposta = reenviar(elaboradora, em_elaboracao)

        em_elaboracao.refresh_from_db()
        assert resposta.status_code == 302, resposta.content
        assert em_elaboracao.max_inscricoes_por_candidato == 2

    def test_esvaziar_o_campo_volta_a_sem_limite(self, elaboradora, em_elaboracao):
        declarar_teto(elaboradora, em_elaboracao, "1")

        declarar_teto(elaboradora, em_elaboracao, "")

        em_elaboracao.refresh_from_db()
        assert em_elaboracao.max_inscricoes_por_candidato is None

    def test_gravar_o_teto_nao_apaga_perfis_nem_documentos(self, elaboradora, em_elaboracao):
        """**Ato próprio, e não `replace_draft`**: aquele apagaria o que não viajasse junto."""
        perfis = em_elaboracao.perfis.count()
        documentos = forms.documentos_do_edital(em_elaboracao)
        assert perfis and len(documentos) == 3, "sem nada gravado, o teste não provaria nada"

        declarar_teto(elaboradora, em_elaboracao, "1")

        em_elaboracao.refresh_from_db()
        assert em_elaboracao.perfis.count() == perfis
        assert forms.documentos_do_edital(em_elaboracao) == documentos

    @pytest.mark.parametrize("etapa", ["cronograma", "conteudo"])
    def test_salvar_outra_etapa_nao_apaga_o_teto(self, elaboradora, em_elaboracao, etapa):
        """As outras etapas passam por `replace_draft`, que não carrega a coluna: ela fica."""
        declarar_teto(elaboradora, em_elaboracao, "1")

        resposta = reenviar(elaboradora, em_elaboracao, etapa)

        em_elaboracao.refresh_from_db()
        assert resposta.status_code == 302, resposta.content
        assert em_elaboracao.max_inscricoes_por_candidato == 1

    def test_o_rascunho_pela_api_nao_apaga_o_teto(self, api_client, elaboradora, em_elaboracao):
        declarar_teto(elaboradora, em_elaboracao, "1")
        em_elaboracao.refresh_from_db()

        gravado = api_client.put(
            f"/api/v1/admin/editais/{em_elaboracao.id}/rascunho",
            rascunho_de_selecao(),
            format="json",
            **{
                **actor_headers("preparador", ["edital:elaborar"], key="teto-etapa-0002"),
                "HTTP_IF_MATCH": f'"{em_elaboracao.revision}"',
            },
        )

        em_elaboracao.refresh_from_db()
        assert gravado.status_code < 400, gravado.content
        assert em_elaboracao.max_inscricoes_por_candidato == 1


class TestRecusar:
    @pytest.mark.parametrize("valor", ["0", "-1", "1.5", "dois", "+2", "99999999999"])
    def test_valor_fora_da_regra_e_recusado_junto_do_campo(self, elaboradora, em_elaboracao, valor):
        revisao = em_elaboracao.revision

        resposta = declarar_teto(elaboradora, em_elaboracao, valor)

        em_elaboracao.refresh_from_db()
        corpo = resposta.content.decode()
        assert resposta.status_code == 200
        assert em_elaboracao.max_inscricoes_por_candidato is None
        assert em_elaboracao.revision == revisao, "a recusa interrompe antes de gravar"
        assert 'id="recusa-teto-inscricoes"' in corpo
        assert 'aria-invalid="true"' in corpo[corpo.index('id="teto-inscricoes"') - 300 :]
        assert f'value="{valor}"' in corpo, "o digitado volta, para a pessoa ver o que foi recusado"

    @pytest.mark.parametrize("valor", [0, -3, True, 1.0])
    def test_o_comando_recusa_sem_passar_pela_tela(self, valor):
        """A regra mora no domínio: o `min` do HTML não é o que impede o teto zero."""
        with pytest.raises(DomainError) as recusa:
            teto_declarado(valor)

        assert recusa.value.campo == "max_inscricoes_por_candidato"

    @pytest.mark.parametrize(("bruto", "esperado"), [("", None), ("  ", None), (None, None)])
    def test_vazio_e_sem_limite(self, bruto, esperado):
        assert teto_declarado(bruto) is esperado

    @pytest.mark.parametrize(("bruto", "esperado"), [("1", 1), (" 3 ", 3), (2, 2)])
    def test_inteiro_a_partir_de_um(self, bruto, esperado):
        assert teto_declarado(bruto) == esperado

    def test_edital_publicado_nao_muda_por_aqui(self, selecao):
        """Depois de publicado, o caminho é a Retificação — com ato publicado dizendo a mudança."""
        with pytest.raises(DomainError) as recusa:
            atualizar_teto_de_inscricoes(
                actor=ator_institucional("ana.elaboradora", "edital:elaborar"),
                edital_id=selecao.id,
                expected_revision=selecao.revision,
                teto=1,
            )

        selecao.refresh_from_db()
        assert recusa.value.code == "invalid_state"
        assert selecao.max_inscricoes_por_candidato is None


class TestATrilha:
    def test_o_ato_fica_na_trilha_com_o_valor(self, elaboradora, em_elaboracao):
        declarar_teto(elaboradora, em_elaboracao, "1")

        registro = RegistroAuditoria.objects.filter(operation=OPERACAO).latest("occurred_at")
        assert registro.reason == "teto 1"

    def test_regravar_o_mesmo_valor_nao_e_ato(self, elaboradora, em_elaboracao):
        """A etapa chama o comando a cada gravação; a trilha só registra o que mudou."""
        declarar_teto(elaboradora, em_elaboracao, "1")
        reenviar(elaboradora, em_elaboracao)
        reenviar(elaboradora, em_elaboracao)

        assert RegistroAuditoria.objects.filter(operation=OPERACAO).count() == 1

    def test_a_operacao_tem_rotulo_legivel_na_trilha(self):
        from processo_seletivo.interface.views import OPERACOES

        assert OPERACOES.get(OPERACAO, OPERACAO) != OPERACAO


class TestARevisao:
    def blocos_de(self, edital):
        from processo_seletivo.interface.revisao import blocos
        from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot

        return blocos(edital_snapshot(edital))

    def test_o_bloco_diz_a_frase_do_documento_e_leva_a_etapa_inscricao(
        self, elaboradora, em_elaboracao
    ):
        declarar_teto(elaboradora, em_elaboracao, "1")
        em_elaboracao.refresh_from_db()

        bloco = next(
            b for b in self.blocos_de(em_elaboracao) if b["titulo"] == "Inscrições por candidato"
        )

        assert bloco["etapa"] == "inscricao", "o caminho de volta leva a onde se corrige"
        assert bloco["itens"][0]["titulo"] == FRASE_DE_UM
        identificacao = self.blocos_de(em_elaboracao)[0]
        assert identificacao["etapa"] == "identificacao"
        assert not any("inscri" in linha for linha in identificacao["itens"][0]["linhas"])

    def test_sem_teto_o_bloco_nao_aparece(self, elaboradora, em_elaboracao):
        titulos = [b["titulo"] for b in self.blocos_de(em_elaboracao)]

        assert "Inscrições por candidato" not in titulos

    def test_a_tela_da_revisao_mostra_o_declarado(self, elaboradora, em_elaboracao):
        declarar_teto(elaboradora, em_elaboracao, "1")

        corpo = elaboradora.get(_url(em_elaboracao, "revisao")).content.decode()

        assert FRASE_DE_UM in corpo

    def test_cada_bloco_da_revisao_tem_nome_proprio(self, elaboradora, em_elaboracao):
        """Três blocos voltam para a etapa Inscrição, e o `id` do título não pode ser a etapa.

        Era: com o teto declarado, o bloco dele e o dos Documentos Exigidos tinham o mesmo `id`, e
        a seção dos documentos era anunciada com o título do teto.
        """
        declarar_teto(elaboradora, em_elaboracao, "1")

        corpo = elaboradora.get(_url(em_elaboracao, "revisao")).content.decode()

        ids = re.findall(r'\bid="([^"]+)"', corpo)
        assert len(ids) == len(set(ids)), sorted({i for i in ids if ids.count(i) > 1})
        for rotulo in re.findall(r'aria-labelledby="([^"]+)"', corpo):
            assert f'id="{rotulo}"' in corpo


def _pronta(edital, perfil):
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=perfil)
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao, dados={"modality_id": MODALIDADE_AC}
    )
    exigidos = [(DOCUMENTO_DE_TODOS, "rg.pdf")]
    if perfil == PERFIL_DOCENTE:
        exigidos.append((DOCUMENTO_DO_PERFIL, "dip.pdf"))
    for requisito, nome in exigidos:
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return inscricao


def _enviar(inscricao, chave):
    return enviar_inscricao(
        identidade=MARIA, inscricao=inscricao, declaracoes=DECLARACOES, idempotency_key=chave
    )


def _publicada_pela_tela(client, api_client, manager_headers, process_payload, teto):
    """Rascunho pela API, teto pela etapa Inscrição, e a publicação de sempre."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    def compor_pela_tela(edital):
        resposta = declarar_teto(client, edital, teto)
        assert resposta.status_code == 302, resposta.content

    return publicar_selecao(
        api_client,
        manager_headers,
        process_payload,
        rascunho=rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)),
        antes_de_submeter=compor_pela_tela,
    )


class TestDaComposicaoASubmissao:
    """O percurso inteiro: o que se declara na tela é o que se publica e o que se executa."""

    def test_teto_um_composto_pela_tela_recusa_a_segunda_inscricao(
        self,
        client,
        seletor_ligado,
        api_client,
        manager_headers,
        process_payload,
        raiz_de_arquivos,
        candidatos_registrados,
    ):
        edital = _publicada_pela_tela(client, api_client, manager_headers, process_payload, "1")

        conteudo = VersaoConsolidada.objects.get(edital=edital).content
        assert conteudo["maxInscricoesPorCandidato"] == 1
        documento = DocumentoPublicado.objects.get(publicacao__edital=edital)
        assert FRASE_DE_UM in " ".join(texto_de(bytes(documento.bytes)).split())

        _enviar(_pronta(edital, PERFIL_DOCENTE), "teto-tela-a")
        with pytest.raises(DomainError) as recusa:
            _enviar(_pronta(edital, PERFIL_TECNICO), "teto-tela-b")

        assert recusa.value.code == "registration_limit_reached"
        assert (
            Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA).count() == 1
        )

    def test_sem_teto_composto_nao_ha_limite(
        self,
        client,
        seletor_ligado,
        api_client,
        manager_headers,
        process_payload,
        raiz_de_arquivos,
        candidatos_registrados,
    ):
        edital = _publicada_pela_tela(client, api_client, manager_headers, process_payload, "")

        conteudo = VersaoConsolidada.objects.get(edital=edital).content
        assert conteudo["maxInscricoesPorCandidato"] is None
        documento = DocumentoPublicado.objects.get(publicacao__edital=edital)
        assert "inscrição enviada neste Edital" not in texto_de(bytes(documento.bytes))

        _enviar(_pronta(edital, PERFIL_DOCENTE), "sem-teto-a")
        _enviar(_pronta(edital, PERFIL_TECNICO), "sem-teto-b")

        assert (
            Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA).count() == 2
        )
