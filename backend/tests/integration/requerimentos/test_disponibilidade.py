"""Quando o requerimento abre, quando fecha, e o que continua legível (029, `US2`).

**O caso que este arquivo existe para prender é o do suplente.** A `D-004` recusou *classificado*
como gatilho justamente porque ele deixa a suplência de fora: quem é chamado depois de uma vaga
vagar não estava classificado dentro do número de vagas, e um gatilho por classificação lhe negaria
o requerimento na hora em que ele mais precisa. Aqui o suplente abre **pelo mesmo caminho** do
titular, sem exceção escrita em lugar nenhum — e é a ausência de exceção que se verifica.

**E a chamada desfechada não fecha a leitura.** O que a pessoa enviou continua visível para ela
depois de a convocação ser respondida (`FR-406`); o que acaba é a escrita.
"""

import pytest
from django.utils import timezone

from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.requerimentos.application import preencher, selectors
from processo_seletivo.requerimentos.domain import nomes
from tests.fixtures.convocacao import apurar, convocar, montar_cenario_da_convocacao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Duas vagas e faixa de três: dois titulares e **um suplente** — o recorte do 77/2026."""
    from tests.fixtures.corte import regra
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.requerimento import declarar

    def publicar_declarando(api_client, manager_headers, process_payload, *, draft=None):
        """O cenário da `019`, com **uma linha a mais**: o Edital declara o requerimento.

        `antes_de_submeter` roda entre a composição e a submissão, que é a única janela em que um
        campo de elaboração ainda pode entrar: depois da publicação o conteúdo é imutável, e
        declará-lo dependeria de uma Retificação.
        """
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
        prefixo="requerimento-029-disp",
        geral=2,
        cut=regra(surplusCount=1),
        publicar=publicar_declarando,
    )


CONTEUDO = {"matriculationRequest": {"moment": nomes.NA_CONVOCACAO, "declarationText": "Declaro…"}}


def ler(inscricao, requerimento=None):
    """A política com as duas leituras injetadas, e a tradução que a tela consome."""
    from processo_seletivo.convocacao.application.selectors import chamada_em_aberto
    from processo_seletivo.requerimentos.domain import disponibilidade

    apurado = disponibilidade.apurar(
        CONTEUDO,
        chamada_em_aberto=chamada_em_aberto(inscricao),
        requerimento=requerimento,
    )
    return selectors.leitura(apurado)


def praticar(edital, gestor, inscricao, **kwargs):
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


class TestOsEstadosDeTela:
    def test_sem_chamada_fica_ainda_indisponivel_e_nao_se_escreve(self, cenario, gestor):
        """`SC-121`, e a frase **não** é a do certame que não pede (`FR-405`)."""
        _, _, inscricoes = cenario

        lido = ler(inscricoes[0])

        assert lido.estado == nomes.AINDA_INDISPONIVEL
        assert lido.pode_escrever is False
        assert lido.titulo != selectors._FRASES[nomes.NAO_APLICAVEL][0]

    def test_com_chamada_em_aberto_fica_disponivel(self, cenario, gestor):
        """`SC-122`: a vez da pessoa é a chamada em aberto."""
        edital, _, inscricoes = cenario
        praticar(edital, gestor, inscricoes[0], idempotency_key="disp-abre")

        lido = ler(inscricoes[0])

        assert lido.estado == nomes.DISPONIVEL
        assert lido.pode_escrever is True

    def test_o_rascunho_aberto_e_em_preenchimento(self, cenario, gestor):
        edital, _, inscricoes = cenario
        praticar(edital, gestor, inscricoes[0], idempotency_key="disp-rascunho")
        rascunho = preencher.abrir_rascunho(inscricao=inscricoes[0])

        lido = ler(inscricoes[0], rascunho)

        assert lido.estado == nomes.EM_PREENCHIMENTO
        assert lido.pode_escrever is True


class TestAChamadaDesfechada:
    def test_desfechada_sem_envio_fecha_a_escrita(self, cenario, gestor):
        edital, _, inscricoes = cenario
        chamada = praticar(edital, gestor, inscricoes[0], idempotency_key="disp-fecha")
        responder(edital, gestor, chamada, nomes_da_convocacao.ACEITE, "disp-aceite")

        lido = ler(inscricoes[0])

        assert lido.pode_escrever is False

    def test_desfechada_depois_do_envio_continua_legivel(self, cenario, gestor, campos_declarados):
        """`FR-406`: o que a pessoa enviou não some da vista dela porque a chamada foi respondida.

        **A ordem da leitura é a regra.** Conferido `disponivel` antes de `enviado`, a tela diria
        *"ainda não é a hora"* a quem já enviou — e o que ela mandou desapareceria.
        """
        edital, _, inscricoes = cenario
        chamada = praticar(edital, gestor, inscricoes[0], idempotency_key="disp-envio")
        preencher.abrir_rascunho(inscricao=inscricoes[0])
        preencher.gravar(inscricao=inscricoes[0], dados=campos_declarados, expected_revision=None)
        enviado = preencher.enviar(
            identidade=_identidade_de(inscricoes[0]),
            inscricao=inscricoes[0],
            versao_exibida_id=preencher._conteudo(inscricoes[0]).id,
            declaracao_exibida=_declaracao_de(inscricoes[0]),
            aceite=True,
        )
        responder(edital, gestor, chamada, nomes_da_convocacao.ACEITE, "disp-aceite-2")

        lido = ler(inscricoes[0], enviado)

        assert lido.estado == nomes.ESTADO_ENVIADO
        assert lido.pode_escrever is False, "legível, e não mais enviável"

    def test_as_sete_especies_fecham_a_escrita_igual(self, cenario, gestor):
        """`SC-134`: o que fecha é **haver** desfecho, e não qual foi.

        **As sete são percorridas de verdade**, uma chamada por vez sobre a mesma pessoa: a lista é
        o que envelhece, e uma oitava espécie acrescentada sem passar por aqui abriria escrita para
        quem já respondeu. A cada volta o teste afirma os **dois** lados — aberta antes do desfecho,
        fechada depois —, porque só o segundo passaria também num gatilho que nunca abre nada.

        **As chamadas seguintes são montadas por ORM**, e não pelos comandos da `019`. Chamar sete
        vezes a mesma pessoa exigiria reemitir a apuração e justificar sucessão a cada volta —
        provaria de novo a `019`, que já tem os seus testes, e não diria nada sobre o gatilho. O
        desfecho real da primeira volta fornece o efeito que as demais reaproveitam.
        """
        from processo_seletivo.convocacao.models import (
            AtestadoDeFatoExterno,
            DesfechoDaConvocacao,
        )
        from processo_seletivo.resultados.models import ResultadoEtapa

        edital, _, inscricoes = cenario
        pessoa = inscricoes[0]
        modelo = praticar(edital, gestor, pessoa, idempotency_key="disp-especie-0")
        responder(edital, gestor, modelo, nomes_da_convocacao.ACEITE, "disp-desfecho-0")
        efeito = modelo.desfechos.get().efeito
        agora = timezone.now()
        # **A regularização exige Resultado sucessor** (`ck_desfecho_regularizacao_exige_sucessor`):
        # regularizar é corrigir o indeferimento, e o desfecho tem de apontar o Resultado que passou
        # a valer. O cenário já consolidou Resultados na Etapa governada, e é um deles que serve.
        sucessor = ResultadoEtapa.objects.filter(inscricao=pessoa).first()
        # **A inércia exige atestado de fato externo** (`ck_desfecho_inercia_exige_atestado`):
        # cancelar matrícula por inércia é concluir *por* alguém, e o fato que a fundamenta vem de
        # fora do sistema — quem o afirma assina por ele.
        atestado = AtestadoDeFatoExterno.objects.create(
            inscricao=pessoa,
            especie=nomes_da_convocacao.ATESTADO_AUSENCIA_NA_PRIMEIRA_SEMANA,
            conclusao="Ausente em toda a primeira semana letiva.",
            referencia_do_prazo="Item 8.4 do Edital.",
            atestado_por="teste",
            atestado_em=agora,
        )

        for numero, especie in enumerate(nomes_da_convocacao.ESPECIES_DE_DESFECHO, start=2):
            chamada = Convocacao.objects.create(
                edital=edital,
                perfil_id=modelo.perfil_id,
                marco_id=modelo.marco_id,
                lista_id=modelo.lista_id,
                inscricao=pessoa,
                especie=modelo.especie,
                fundamento="No interesse da Administração.",
                apuracao=modelo.apuracao,
                ato_de_ordenacao_id=modelo.ato_de_ordenacao_id,
                corte_id=modelo.corte_id,
                versao=modelo.versao,
                chamada=numero,
                criado_por="teste",
                criado_em=agora,
            )
            assert ler(pessoa).pode_escrever is True, "a chamada nova abre"

            DesfechoDaConvocacao.objects.create(
                convocacao=chamada,
                especie=especie,
                fundamento="Registrado em processo.",
                efeito=efeito,
                resultado_sucessor=(
                    sucessor if especie == nomes_da_convocacao.REGULARIZACAO else None
                ),
                atestado=atestado if especie == nomes_da_convocacao.INERCIA else None,
                registrado_por="teste",
                registrado_em=agora,
            )

            assert ler(pessoa).pode_escrever is False, f"{especie} deveria fechar a escrita"


class TestOSuplente:
    def test_o_suplente_convocado_depois_abre_pelo_mesmo_caminho(self, cenario, gestor):
        """`D-004` inteira, num teste: **nenhuma exceção** foi escrita para a suplência.

        O suplente não estava classificado dentro do número de vagas. Um gatilho por classificação
        lhe negaria o requerimento exatamente na hora em que a vaga é dele — e essa é a razão de a
        `D-004` ter recusado *classificado* como gatilho.
        """
        edital, _, inscricoes = cenario
        # **Os dois titulares são chamados**, e não só um: o recorte tem duas vagas, e convocar o
        # suplente com alguém à frente sem chamada é recusado por `precedencia_na_ordem` — a fila
        # não se pula, e é isso que faz a suplência ser suplência.
        titular, segundo, suplente = inscricoes[0], inscricoes[1], inscricoes[2]
        chamada = praticar(edital, gestor, titular, idempotency_key="disp-titular")
        praticar(edital, gestor, segundo, idempotency_key="disp-titular-2")
        assert ler(suplente).pode_escrever is False, "antes de ser chamado, não abre"
        responder(
            edital, gestor, chamada, nomes_da_convocacao.DESISTENCIA_EXPRESSA, "disp-desistiu"
        )
        # **A apuração seguinte é exigência da `019`, e não cerimônia do teste**: a desistência
        # escreveu um efeito novo na porta da ocupação, e a apuração vigente passou a estar para
        # trás. Convocar sobre ela seria chamar para uma vaga que ninguém recontou.
        apurar(
            edital,
            gestor,
            chave="disp-reapurar",
            motivo="A desistência do titular abriu a vaga que a suplência vem ocupar.",
        )

        praticar(
            edital,
            gestor,
            suplente,
            especie=nomes_da_convocacao.SUPLENCIA,
            idempotency_key="disp-suplente",
        )

        assert ler(suplente).pode_escrever is True
        assert ler(titular).pode_escrever is False, "quem desistiu não reabre"


def _identidade_de(inscricao):
    from tests.fixtures.candidato import MARIA

    return MARIA


def _declaracao_de(inscricao):
    return preencher.declaracao_publicada(preencher._conteudo(inscricao).content)
