"""O que esta feature custa por tela, medido — e o **zero** que ela não pode gastar (T063).

**Orçamento declarado e não medido é intenção.** O plano afirma um custo por tela; sem teste, a
afirmação envelhece no primeiro `select_related` esquecido, e o custo cresce onde ninguém olha.

**O número que mais importa é o zero da listagem.** Exibir o estado do requerimento por linha de
`Minhas inscrições` é *leitura por listagem* — uma consulta por linha, invisível com três inscrições
e fatal com trezentas —, e este repositório já reprovou esse padrão uma vez (`T-009`). O zero não é
meta de desempenho: é a decisão de **não** colocar o dado ali.

**A medição conta as consultas que tocam as tabelas desta feature**, e não o total da página. O
total varia com o conteúdo do Edital e com o que outras features acrescentam; prendê-lo faria este
teste falhar por mudança alheia, e a primeira redação a corrigir seria a asserção — que é como um
orçamento vira número decorativo.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.portal.identidade import CHAVE_SESSAO
from processo_seletivo.requerimentos.application import preencher
from tests.fixtures.requerimento import DECLARACAO, pronta_para_enviar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

# Os nomes das duas tabelas desta feature, como o SQL as escreve.
NOSSAS = "requerimentos_"


def entrar_como(client, inscricao):
    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=inscricao.identity_subject, defaults={"created_at": timezone.now()}
    )
    sessao = client.session
    sessao[CHAVE_SESSAO] = str(registro.pk)
    sessao.save()


def consultas_da_feature(client, url):
    """Quantas consultas desta requisição tocam as tabelas do requerimento.

    A página é carregada **duas vezes**, e só a segunda é contada: a primeira aquece o que houver
    de cache de conteúdo publicado, e medir a fria atribuiria a esta feature um custo que é de
    outra.
    """
    client.get(url)
    with CaptureQueriesContext(connection) as capturadas:
        resposta = client.get(url)
    assert resposta.status_code == 200, f"{url} devolveu {resposta.status_code}"
    return len([consulta for consulta in capturadas if NOSSAS in consulta["sql"]])


def enviar_tudo(edital, campos):
    """Requerimento enviado e inscrição submetida — o estado de quem concluiu a jornada."""
    from tests.fixtures.candidato import MARIA
    from tests.fixtures.requerimento import submeter

    inscricao = pronta_para_enviar(edital)
    preencher.abrir_rascunho(inscricao=inscricao)
    preencher.gravar(inscricao=inscricao, dados=campos, expected_revision=None)
    preencher.enviar(
        identidade=MARIA,
        inscricao=inscricao,
        versao_exibida_id=preencher._conteudo(inscricao).id,
        declaracao_exibida=DECLARACAO,
        aceite=True,
    )
    submeter(inscricao)
    inscricao.refresh_from_db()
    return inscricao


@pytest.fixture
def inscricao_com_requerimento(client, selecao_na_inscricao, candidatos_registrados):
    inscricao = pronta_para_enviar(selecao_na_inscricao)
    entrar_como(client, inscricao)
    return inscricao


class TestOCanalDoCandidato:
    def test_a_lista_de_inscricoes_nao_toca_a_feature(self, client, inscricao_com_requerimento):
        """**Zero, e é o número que esta feature existe para não gastar** (`T-009`).

        Uma consulta por linha aqui é invisível com três inscrições e mata com trezentas. E o
        remédio não é `prefetch_related`: é não exibir o dado numa listagem — o estado do
        requerimento é do requerimento, e se lê na tela dele.
        """
        assert consultas_da_feature(client, reverse("portal:inscricoes")) == 0

    def test_o_cartao_na_tela_da_inscricao_custa_uma_consulta(
        self, client, inscricao_com_requerimento
    ):
        """O cartão anuncia o bloqueio antes da tentativa (`UX-054`), e cobra **uma** leitura.

        Uma só porque a política pergunta em ordem: o Edital declara na inscrição? A resposta sai
        do conteúdo publicado, que a tela já tinha lido. Só quando ela é *sim* é que a linha
        vigente do requerimento é buscada. Edital que não coleta não paga nada.
        """
        custo = consultas_da_feature(
            client, reverse("portal:inscricao", args=[inscricao_com_requerimento.id])
        )

        assert custo == 1, f"o cartão passou a custar {custo} consultas"

    def test_o_acompanhamento_nao_toca_a_feature(
        self, client, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        """**Zero, e a razão é que o requerimento não aparece ali.**

        O plano previa `+2` também nesta tela, e a previsão não se confirmou: o acompanhamento
        segue o andamento do certame, e o caminho para o requerimento é o cartão da inscrição e a
        tela da convocação. Acrescentá-lo aqui só para gastar o orçamento previsto seria produzir
        leitura para satisfazer um número.

        **A inscrição precisa estar enviada** para esta tela existir — e enviá-la, neste Edital,
        exige o requerimento enviado antes. O cenário é o caminho inteiro, e não um atalho.
        """
        inscricao = enviar_tudo(selecao_na_inscricao, campos_declarados)
        entrar_como(client, inscricao)

        assert (
            consultas_da_feature(client, reverse("portal:acompanhamento", args=[inscricao.id])) == 0
        )

    def test_a_tela_do_requerimento_custa_duas(self, client, inscricao_com_requerimento):
        """A tela própria: a linha vigente, e a leitura sob a qual o rascunho é aberto.

        É a única tela desta feature que **deve** custar — e duas é o piso: menos do que isso
        significaria não ler o que se vai exibir.
        """
        custo = consultas_da_feature(
            client, reverse("portal:requerimento", args=[inscricao_com_requerimento.id])
        )

        assert custo <= 3, f"a tela do requerimento passou a custar {custo} consultas"


class TestOCanalDeQuemConduz:
    def test_o_dossie_custa_uma_consulta(
        self,
        client,
        selecao_na_inscricao,
        candidatos_registrados,
        campos_declarados,
        seletor_ligado,
    ):
        """`+1` no dossiê: a linha vigente do requerimento, e mais nada.

        Os vinte campos vêm dessa mesma linha — o bloco do dossiê não faz uma consulta por grupo,
        que seria a forma óbvia de escrever sete `dl` e a forma cara de lê-los.
        """
        from tests.fixtures.candidato import MARIA
        from tests.interface.conftest import identificar

        inscricao = pronta_para_enviar(selecao_na_inscricao)
        preencher.abrir_rascunho(inscricao=inscricao)
        preencher.gravar(inscricao=inscricao, dados=campos_declarados, expected_revision=None)
        preencher.enviar(
            identidade=MARIA,
            inscricao=inscricao,
            versao_exibida_id=preencher._conteudo(inscricao).id,
            declaracao_exibida=DECLARACAO,
            aceite=True,
        )
        identificar(client, "ana.gestora", ["gestor"])

        custo = consultas_da_feature(
            client, reverse("interface:inscricao-recebida", args=[inscricao.id])
        )

        assert custo == 1, f"o bloco do dossiê passou a custar {custo} consultas"


def test_a_medicao_enxerga_o_que_mede(client, inscricao_com_requerimento):
    """Uma medição que sempre devolve zero aprova tudo, calada.

    Se o filtro por nome de tabela deixasse de casar — uma renomeação, um `schema` na frente —,
    todos os zeros acima continuariam verdes e o orçamento passaria a não medir nada.
    """
    custo = consultas_da_feature(
        client, reverse("portal:requerimento", args=[inscricao_com_requerimento.id])
    )

    assert custo > 0, "o filtro por nome de tabela deixou de casar: a medição virou decorativa"
