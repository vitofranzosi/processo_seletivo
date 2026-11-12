"""A condição do esgotamento no caminho oficial: V-1, V-2, V-4 e US1.4, com o resultado novo.

(155, T022.) A verificação do levantamento
(`specs/155-destinacao-da-vaga-sem-concorrente/verificacao-do-levantamento.md`) mediu o que o
código fazia antes da `155`: a reserva sem mais ninguém nunca esgotava, porque quem saiu por
desfecho, o inabilitado e quem ocupa pela ampla contavam como "quem ocupar". Estes casos
são os mesmos cenários, com o resultado que a FR-6304 manda — e com os fatos externos lidos de
verdade, pela composição da interface, sobre o resultado definitivo publicado.

**V-5** — todos eliminados antes da ordem — não tem caminho oficial no sorteio, que não elimina: o
caso puro está em `tests/unit/ocupacao/test_destinacao_dominio.py::test_posicao_vazia_nao_conta`.
"""

import uuid

import pytest
from django.utils import timezone

from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.application.destinacao import leitura_da_vaga
from processo_seletivo.ocupacao.application.efeitos import registrar_efeito
from processo_seletivo.ocupacao.domain import destinacao, nomes
from processo_seletivo.ocupacao.models import MovimentoDeVaga
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao_sorteada import LISTA_PPI, certame_sorteado_com_quadro
from tests.fixtures.sorteio import MARCO
from tests.integration.ocupacao.test_concomitancia import apurar, emitir_cortes, habilitar

pytestmark = pytest.mark.django_db(transaction=True)


def montar(gestor, api_client, manager_headers, process_payload, prefixo, **quadro):
    return certame_sorteado_com_quadro(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        com_corte=True,
        reversao=nomes.REVERSAO_POR_ESGOTAMENTO,
        **quadro,
    )


def publicar_definitivo(certame, lista_id=LISTA_PPI, chave="definitivo"):
    """O resultado definitivo da lista, pelo comando — sem ele, a destinação não cabe (FR-6306)."""
    from processo_seletivo.classificacao.application.selectors import ato_vigente
    from processo_seletivo.divulgacao.application.publicar import (
        assinatura_da_previa,
        publicar_resultado,
    )
    from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
    from processo_seletivo.divulgacao.domain.conteudo import compor
    from tests.fixtures.autoridades import AUTORIDADE_DO_RESULTADO
    from tests.fixtures.divulgacao import ator_publicador

    edital = certame["edital"]
    ato = ato_vigente(edital=edital, marco_id=MARCO, lista_id=lista_id)
    anterior = vigente_do_marco(edital=edital, marco_id=MARCO, lista_id=lista_id)
    publicar_resultado(
        actor=ator_publicador(),
        processo_id=edital.processo_id,
        edital_id=edital.id,
        marco_id=MARCO,
        ato_id=ato.id,
        natureza="DEFINITIVA",
        autoridade=str(AUTORIDADE_DO_RESULTADO),
        confirmacao_da_previa=assinatura_da_previa(
            ato=ato, publicacao_anterior=anterior, projecao=compor(ato)
        ),
        idempotency_key=f"{certame['edital'].id}-{chave}-{lista_id}",
        correlation_id="teste-155",
    )


def efeito(certame, inscricao, especie, *, lista_id=LISTA_PPI, rotulo="desfecho de convocação"):
    return registrar_efeito(
        edital=certame["edital"],
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        inscricao_id=getattr(inscricao, "id", inscricao),
        especie=especie,
        fundamento="Fato registrado no teste da 155",
        ato_de_origem_id=uuid.uuid4(),
        rotulo_da_origem=rotulo,
        registrado_por="teste",
        registrado_em=timezone.now(),
    )


def eliminar(certame, inscricoes):
    versao = effective_version(edital_id=certame["edital"].id)
    for inscricao in inscricoes:
        ResultadoEtapa.objects.create(
            inscricao=inscricao,
            edital=certame["edital"],
            versao=versao,
            etapa_id=certame["etapa_governada"],
            origem=ResultadoEtapa.Origem.OCORRENCIA,
            consequencia=ResultadoEtapa.Consequencia.ELIMINADA,
            motivo="Documentação indeferida",
            consolidado_em=timezone.now(),
            consolidado_por="teste",
        )


def ler(certame, *, depois_do_prazo=True):
    """A leitura pela composição da interface — e, por padrão, depois do prazo de recurso.

    **O marco do sorteio declara prazo recursal computável**, e ele corre da publicação do
    definitivo: lida agora, toda vaga estaria impedida por ele, que é o comportamento certo
    (FR-6306) e não o que estes casos medem.
    """
    from datetime import timedelta

    from processo_seletivo.interface.destinacao_da_vaga import Composicao

    at = timezone.now() + timedelta(days=120) if depois_do_prazo else None
    return leitura_da_vaga(
        edital=certame["edital"],
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=LISTA_PPI,
        fatos_externos=Composicao(at=at),
        at=at,
    )


def sem_concomitancia(certame, inscricao):
    """Garante o cotista fora da ampla, que é o que V-1 e V-2 pedem.

    **A ordem do sorteio depende das identidades sorteadas**, e com uma vaga na ampla o cotista
    cai como titular dela em uma rodada a cada oito — a primeira versão destes casos falhava assim,
    de vez em quando. Quando cai, a saída dele da ampla é registrada como efeito, e a concomitância,
    que é o cenário de V-4, fica fora deste.
    """
    if not fora_da_ampla(certame, inscricao):
        efeito(certame, inscricao, nomes.EFEITO_EXCLUSAO, lista_id=None)
    assert fora_da_ampla(certame, inscricao)


def fora_da_ampla(certame, inscricao):
    versao = effective_version(edital_id=certame["edital"].id)
    return str(inscricao.id) not in {
        str(i)
        for i in selectors.ocupantes_da_ampla(
            edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, versao=versao
        )
    }


def test_o_prazo_do_definitivo_impede_enquanto_corre(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """US3.5: com o prazo recursal aberto, a destinação não é oferecida, e diz até quando."""
    certame = montar(
        gestor, api_client, manager_headers, process_payload, "prazo-155", quantos=8, geral=1
    )
    emitir_cortes(certame, gestor)
    apurar(certame, gestor, chave="prazo-ampla")
    apurar(certame, gestor, lista_id=LISTA_PPI, chave="prazo-ppi")
    publicar_definitivo(certame)

    impedimentos = ler(certame, depois_do_prazo=False)["situacao"]["impedimentos"]

    prazo = next(i for i in impedimentos if i.codigo == destinacao.PRAZO_RECURSAL_ABERTO)
    assert prazo.ate is not None


class TestV1Desistencia:
    @pytest.fixture
    def certame(self, db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
        return montar(
            gestor, api_client, manager_headers, process_payload, "v1-155", quantos=8, geral=1
        )

    def test_o_unico_cotista_desiste_e_a_destinacao_e_oferecida(self, certame, gestor):
        """V-1: antes, 0 ocupadas e 1 a ocupar para sempre; agora, a reserva está esgotada."""
        cotista = certame["cotista_ppi"]
        emitir_cortes(certame, gestor)
        habilitar(certame, [cotista])
        apurar(certame, gestor, chave="v1-ampla")
        sem_concomitancia(certame, cotista)
        antes = apurar(certame, gestor, lista_id=LISTA_PPI, chave="v1-ppi")
        assert (antes["ocupadas"], antes["faltando"]) == (1, 0)

        efeito(certame, cotista, nomes.EFEITO_EXCLUSAO)
        depois = apurar(
            certame, gestor, lista_id=LISTA_PPI, chave="v1-ppi-2", motivo="Desistência registrada"
        )
        publicar_definitivo(certame)

        assert (depois["ocupadas"], depois["faltando"], depois["reverteu"]) == (0, 1, 0)
        assert MovimentoDeVaga.objects.count() == 0, "a emissão não move vaga (FR-6315)"
        situacao = ler(certame)["situacao"]
        assert situacao["estado"] == destinacao.DESTINACAO_DISPONIVEL, situacao
        assert situacao["quantidade"] == 1

    def test_sem_o_definitivo_a_destinacao_esta_impedida(self, certame, gestor):
        """US3.6: com o resultado do marco não definitivo, em nenhum dos gatilhos."""
        cotista = certame["cotista_ppi"]
        emitir_cortes(certame, gestor)
        habilitar(certame, [cotista])
        apurar(certame, gestor, chave="v1b-ampla")
        sem_concomitancia(certame, cotista)
        efeito(certame, cotista, nomes.EFEITO_EXCLUSAO)
        apurar(certame, gestor, lista_id=LISTA_PPI, chave="v1b-ppi")

        situacao = ler(certame)["situacao"]

        assert situacao["estado"] == destinacao.IMPEDIDA
        assert [i.codigo for i in situacao["impedimentos"]] == [destinacao.RESULTADO_NAO_DEFINITIVO]


class TestV2Inabilitacao:
    @pytest.fixture
    def certame(self, db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
        return montar(
            gestor, api_client, manager_headers, process_payload, "v2-155", quantos=8, geral=1
        )

    def test_o_inabilitado_sem_recurso_nem_prazo_nao_ocupa(self, certame, gestor):
        """V-2: inabilitação é eliminação (155, D-007); sem prazo nem recurso, a lista esgota."""
        cotista = certame["cotista_ppi"]
        emitir_cortes(certame, gestor)
        eliminar(certame, [cotista])
        apurar(certame, gestor, chave="v2-ampla")
        sem_concomitancia(certame, cotista)
        apurado = apurar(certame, gestor, lista_id=LISTA_PPI, chave="v2-ppi")
        publicar_definitivo(certame)

        assert (apurado["ocupadas"], apurado["faltando"]) == (0, 1)
        situacao = ler(certame)["situacao"]
        assert situacao["estado"] == destinacao.DESTINACAO_DISPONIVEL, situacao

    def test_com_o_prazo_da_eliminacao_aberto_a_destinacao_espera(self, certame, gestor):
        """US3.5: enquanto o recurso pode devolver o eliminado à lista, a vaga não é destinada.

        O prazo chega pelos fatos externos, como a composição o entrega; o que se prova aqui é o
        lado da ocupação: quem ela pergunta, e o que faz com a resposta.
        """
        from datetime import timedelta

        cotista = certame["cotista_ppi"]
        emitir_cortes(certame, gestor)
        eliminar(certame, [cotista])
        apurar(certame, gestor, chave="v2c-ampla")
        sem_concomitancia(certame, cotista)
        apurar(certame, gestor, lista_id=LISTA_PPI, chave="v2c-ppi")
        perguntas = []
        fecha = timezone.now() + timedelta(days=3)

        def fatos_externos(**pergunta):
            perguntas.append(pergunta)
            return {"natureza_do_resultado": "DEFINITIVA", "prazo_da_eliminacao_ate": fecha}

        situacao = leitura_da_vaga(
            edital=certame["edital"],
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=LISTA_PPI,
            fatos_externos=fatos_externos,
        )["situacao"]

        assert {str(i) for i in perguntas[0]["eliminados"]} == {str(cotista.id)}
        assert str(perguntas[0]["etapa_governada_id"]) == str(certame["etapa_governada"])
        assert situacao["estado"] == destinacao.IMPEDIDA
        (impedimento,) = situacao["impedimentos"]
        assert (impedimento.codigo, impedimento.ate) == (
            destinacao.PRAZO_DA_ELIMINACAO_ABERTO,
            fecha,
        )

    def test_sem_resultado_na_etapa_ainda_pode_ocupar(self, certame, gestor):
        """Quem ainda não foi analisado não foi inabilitado: ausência de resultado não elimina."""
        cotista = certame["cotista_ppi"]
        emitir_cortes(certame, gestor)
        apurar(certame, gestor, chave="v2b-ampla")
        sem_concomitancia(certame, cotista)
        apurar(certame, gestor, lista_id=LISTA_PPI, chave="v2b-ppi")
        publicar_definitivo(certame)

        leitura = ler(certame)
        assert leitura["situacao"]["estado"] == destinacao.SEM_VAGA_A_DESTINAR
        assert [str(i) for i in leitura["restantes"]] == [str(cotista.id)]


class TestV4Concomitancia:
    @pytest.fixture
    def certame(self, db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
        # Quatro sorteados e quatro vagas na ampla: o único cotista PPI é titular da ampla.
        return montar(
            gestor, api_client, manager_headers, process_payload, "v4-155", quantos=4, geral=4
        )

    def _preparar(self, certame, gestor, prefixo):
        emitir_cortes(certame, gestor)
        habilitar(certame, [certame["cotista_ppi"]])
        apurar(certame, gestor, chave=f"{prefixo}-ampla")
        assert not fora_da_ampla(certame, certame["cotista_ppi"])

    def test_com_a_ocupacao_pela_ampla_confirmada_a_destinacao_e_oferecida(self, certame, gestor):
        """US3.1 e V-4: antes, nunca esgotava; agora, quem confirmou a ampla não ocupa a reserva."""
        self._preparar(certame, gestor, "v4")
        efeito(certame, certame["cotista_ppi"], nomes.EFEITO_INCLUSAO, lista_id=None)
        cota = apurar(certame, gestor, lista_id=LISTA_PPI, chave="v4-ppi")
        publicar_definitivo(certame)

        assert (cota["ocupadas"], cota["faltando"]) == (0, 1)
        situacao = ler(certame)["situacao"]
        assert situacao["estado"] == destinacao.DESTINACAO_DISPONIVEL, situacao

    def test_sem_a_confirmacao_a_destinacao_esta_impedida(self, certame, gestor):
        """US3.2: a ocupação pela ampla ainda pode mudar, e a tela diz isso."""
        self._preparar(certame, gestor, "v4b")
        apurar(certame, gestor, lista_id=LISTA_PPI, chave="v4b-ppi")
        publicar_definitivo(certame)

        situacao = ler(certame)["situacao"]

        assert situacao["estado"] == destinacao.IMPEDIDA
        assert [i.codigo for i in situacao["impedimentos"]] == [
            destinacao.OCUPACAO_PELA_AMPLA_PODE_MUDAR
        ]
        assert situacao["quantidade"] == 0


class TestChamadaEmCurso:
    @pytest.fixture
    def certame(self, db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
        # Duas vagas PPI e uma cotista só: ela ocupa uma, e a outra sobra.
        return montar(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            "chamada-155",
            quantos=8,
            geral=1,
            ppi=2,
        )

    def test_a_pessoa_chamada_com_prazo_em_curso_impede_e_e_nomeada(self, certame, gestor):
        """US1.4: o ato não é oferecido, e a situação diz qual chamada o impede."""
        from tests.integration.convocacao.test_suplencia import chamar

        cotista = certame["cotista_ppi"]
        emitir_cortes(certame, gestor)
        habilitar(certame, [cotista])
        apurar(certame, gestor, chave="chamada-ampla")
        sem_concomitancia(certame, cotista)
        cota = apurar(certame, gestor, lista_id=LISTA_PPI, chave="chamada-ppi")
        assert (cota["ocupadas"], cota["faltando"]) == (1, 1)
        publicar_definitivo(certame)
        chamar(certame, gestor, cotista.id, lista_id=LISTA_PPI, chave="chamada-chamar")

        situacao = ler(certame)["situacao"]

        assert situacao["estado"] == destinacao.IMPEDIDA
        (impedimento,) = situacao["impedimentos"]
        assert impedimento.codigo == destinacao.CHAMADA_EM_CURSO
        assert cotista.protocolo in impedimento.frase
