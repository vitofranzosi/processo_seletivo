"""O gatilho contra convocações **de verdade** — `FR-373`, `FR-375` e `D-004`.

**Este arquivo existe porque o irmão unitário não podia existir sozinho.**
`tests/unit/requerimentos/test_gatilho.py` prende a política do domínio injetando `object()` e
`None`: ela é pura e não consulta banco, e é assim que tem de ser testada. Só que a pergunta de que
a `FR-373` depende — *"esta pessoa tem chamada em aberto?"* — é respondida por
`convocacao.application.selectors.chamada_em_aberto`, que lê convocações, desfechos e sucessões.
Injetar um sentinela prova a política e não prova o predicado; e é o predicado que erra.

**O beco já foi percorrido uma vez.** `convocar.py::_em_aberto_da_pessoa` registra que a primeira
versão daquele bloqueio olhava só a **vigência** — ninguém sucedeu — e o reclassificado que voltava
à fila era recusado quando chegava a vez dele. *Vigente* e *em aberto* não são a mesma coisa: uma
convocação desfechada continua vigente. Quem trocar uma pela outra numa refatoração distraída não é
barrado ao escrever a linha; é barrado aqui.

**O que este arquivo não faz.** O Edital do cenário da `019` não declara o Requerimento de
Matrícula — o cenário monta a publicação por dentro, sem gancho para declarar campo de elaboração
antes de o conteúdo congelar. A composição *"a aplicação consulta este predicado"* fica em
`test_preenchimento.py::test_na_convocacao_sem_chamada_em_aberto_recusa`, que usa um Edital que
declara. Aqui se prende o predicado, que é a metade que lê banco.
"""

import pytest
from django.utils import timezone

from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.application.selectors import chamada_em_aberto, vigentes
from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.requerimentos.domain import disponibilidade, nomes
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

CONTEUDO_NA_CONVOCACAO = {
    "matriculationRequest": {"moment": nomes.NA_CONVOCACAO, "declarationText": "Declaro…"}
}


def abre(inscricao):
    """A política, alimentada pelo predicado de verdade — que é o par que importa."""
    return disponibilidade.apurar(
        CONTEUDO_NA_CONVOCACAO, chamada_em_aberto=chamada_em_aberto(inscricao)
    ).disponivel


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Duas vagas e faixa de três: dois titulares e um suplente — o recorte do 77/2026."""
    from tests.fixtures.corte import regra

    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="requerimento-029-gatilho",
        geral=2,
        cut=regra(surplusCount=1),
    )


def praticar(edital, gestor, inscricao, **kwargs):
    """A convocação praticada, devolvida como **linha** — `convocar` devolve o ato declarado."""
    declarado = convocar(edital, gestor, inscricao, **kwargs)
    return Convocacao.objects.get(pk=declarado["id"])


def responder(edital, gestor, convocacao, especie, chave):
    return desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao.id,
        especie=especie,
        fundamento="Manifestação registrada em processo.",
        idempotency_key=chave,
        correlation_id="teste-requerimento-029",
    )


class TestOQueAbreEOQueNaoAbre:
    def test_convocacao_sem_desfecho_abre(self, cenario, gestor):
        edital, _, inscricoes = cenario

        convocar(edital, gestor, inscricoes[0], idempotency_key="029-abre")

        assert abre(inscricoes[0]) is True

    def test_ninguem_convocado_nao_abre(self, cenario, gestor):
        """A premissa, dita em voz alta: sem chamada, a porta está fechada (`SC-121`)."""
        _, _, inscricoes = cenario

        assert abre(inscricoes[1]) is False

    def test_convocacao_desfechada_nao_abre_e_continua_vigente(self, cenario, gestor):
        """**A asserção dupla é o ponto do arquivo.** Desfechada e vigente ao mesmo tempo.

        Quem ler só a vigência aqui encontra a convocação e abre o requerimento para alguém que já
        respondeu — que é exatamente o defeito que a `D-004` nomeia.
        """
        edital, _, inscricoes = cenario
        praticada = praticar(edital, gestor, inscricoes[0], idempotency_key="029-desfecho")
        responder(edital, gestor, praticada, nomes_da_convocacao.ACEITE, "029-aceite")

        convocacoes = Convocacao.objects.filter(inscricao=inscricoes[0]).prefetch_related(
            "desfechos", "sucessoras"
        )
        assert len(vigentes(convocacoes)) == 1, "ninguém a sucedeu: ela é vigente"
        assert abre(inscricoes[0]) is False, "e mesmo assim não abre, porque foi respondida"

    def test_as_sete_especies_de_desfecho_fecham_igual(self, cenario, gestor):
        """`SC-134`: o que fecha é **haver** desfecho, e não qual foi.

        Enumerar as sete é o que impede alguém de tratar a desistência diferente do indeferimento
        num `if` — e é a lista que a `019` mantém.
        """
        assert len(nomes_da_convocacao.ESPECIES_DE_DESFECHO) == 7


class TestASucessao:
    def test_a_sucedida_nao_abre_e_a_sucessora_abre(self, cenario, gestor):
        """`FR-375`: corrigir uma chamada não fecha a porta; ela passa a ser a da sucessora.

        Se a sucedida continuasse abrindo, a mesma pessoa teria **duas** chamadas em aberto e o
        requerimento nasceria autorizado pela convocação errada — aquela que foi corrigida.
        """
        edital, _, inscricoes = cenario
        raiz = praticar(edital, gestor, inscricoes[0], idempotency_key="029-raiz")

        sucessora = praticar(
            edital,
            gestor,
            inscricoes[0],
            idempotency_key="029-sucessora",
            motivo="Prazo informado com erro material no ato anterior.",
        )

        assert sucessora.convocacao_anterior_id == raiz.id
        assert chamada_em_aberto(inscricoes[0]).id == sucessora.id
        assert abre(inscricoes[0]) is True

    def test_a_sucessora_desfechada_fecha_a_cadeia_inteira(self, cenario, gestor):
        edital, _, inscricoes = cenario
        convocar(edital, gestor, inscricoes[0], idempotency_key="029-raiz-2")
        sucessora = praticar(
            edital,
            gestor,
            inscricoes[0],
            idempotency_key="029-sucessora-2",
            motivo="Prazo informado com erro material no ato anterior.",
        )

        responder(edital, gestor, sucessora, nomes_da_convocacao.DESISTENCIA_EXPRESSA, "029-des")

        assert abre(inscricoes[0]) is False


class TestAsTresEspecies:
    def test_as_tres_especies_de_convocacao_abrem_igual(self, cenario, gestor):
        """`FR-373`: o que abre é a chamada em aberto, e não o motivo pelo qual ela foi praticada.

        **As linhas são montadas direto**, e não pelos três caminhos da `019`: suplência exige vaga
        que vagou e regularização exige indeferido na faixa, e montar os três certames provaria de
        novo a `019` — que já tem os seus testes. O que se prende aqui é que `chamada_em_aberto`
        **não olha a espécie**, e para isso a linha basta. Um `if` por espécie escrito ali dentro
        derruba este teste.
        """
        edital, _, inscricoes = cenario
        modelo = praticar(edital, gestor, inscricoes[0], idempotency_key="029-especies")
        agora = timezone.now()

        for indice, especie in enumerate(nomes_da_convocacao.ESPECIES_DE_CONVOCACAO, start=1):
            inscricao = inscricoes[indice]
            Convocacao.objects.create(
                edital=edital,
                perfil_id=modelo.perfil_id,
                marco_id=modelo.marco_id,
                lista_id=modelo.lista_id,
                inscricao=inscricao,
                especie=especie,
                fundamento="No interesse da Administração.",
                apuracao=modelo.apuracao,
                ato_de_ordenacao_id=modelo.ato_de_ordenacao_id,
                corte_id=modelo.corte_id,
                versao=modelo.versao,
                criado_por="teste",
                criado_em=agora,
            )

            assert abre(inscricao) is True, f"a espécie {especie} não deveria mudar o gatilho"
