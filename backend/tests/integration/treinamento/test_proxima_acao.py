"""Cada ficha cumpre o que promete: o estado inicial, e a próxima ação que funciona (18.5).

**A próxima ação é executada, e não só anunciada.** Um cenário que pareça pronto e recuse o primeiro
passo do roteiro é o defeito que o pedido mais teme — "não declare cenários como funcionais sem
verificar que o operador realmente consegue executar a ação pretendida". Cada caso monta o cenário
pelo comando de carga e pratica a ação da ficha com o ator que ela nomeia, pelo mesmo comando que a
tela chama. O C07, prioritário, é exercitado **pela tela** em `test_carga_e_restauracao.py`.

E o avesso (18.6): a mesma ação, tentada por quem a ficha **não** nomeia, é recusada.
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.treinamento import construcao as c
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.treinamento import carregar, retomar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def cenario(treinamento):
    def montar(codigo):
        saida = carregar(codigo, autoridade=str(AUTORIDADE_DA_SUITE))
        assert f"{codigo}  CRIADO" in saida, saida
        return retomar(
            CenarioDeTreinamento.objects.get(codigo=codigo), autoridade=str(AUTORIDADE_DA_SUITE)
        )

    return montar


def test_c01_o_edital_em_elaboracao_se_completa_e_publica(cenario):
    m = cenario("C01")
    assert m.edital.status == Edital.Status.EM_ELABORACAO
    assert not m.edital.documentos_exigidos.exists()
    m.elaborar(
        perfis=c.perfil_de_notas(),
        inicio=timezone.now() + timedelta(days=7),
        duracao_dias=30,
        documentos=c.documentos_de_notas(),
    )
    m.publicar()
    assert m.edital.status == Edital.Status.PUBLICADO


def test_c02_as_inscricoes_estao_abertas_e_recebem_mais_uma(cenario):
    m = cenario("C02")
    assert m.edital.status == Edital.Status.PUBLICADO
    assert len(m.inscricoes) == 3
    [nova] = m.inscrever(1)
    assert nova.protocolo and nova.status == "SUBMETIDA"


def test_c03_encerradas_as_inscricoes_a_gestao_constitui_a_comissao(cenario):
    m = cenario("C03")
    assert len(m.inscricoes) == 8
    with pytest.raises(DomainError):
        m.inscrever(1)
    m.constituir_comissao(alocar_em=(c.ETAPA_PROVA,))
    assert len(m.membros) == 3


def test_c04_a_presidencia_emite_a_ordem_com_o_desempate_e_o_empate_residual(cenario):
    from processo_seletivo.classificacao.models import AtoDeOrdenacao

    m = cenario("C04")
    assert not AtoDeOrdenacao.objects.filter(edital=m.edital).exists()
    # Quem avalia não emite: a ordem é ato da presidência (18.6).
    with pytest.raises(DomainError):
        m.emitir_ordem(quem=c.AVALIACAO_1)
    ato = m.emitir_ordem()
    posicoes = {str(p.inscricao_id): p.posicao for p in ato.posicoes.all()}
    um, dois, tres, quatro = (str(i.id) for i in m.inscricoes[:4])
    oito = str(m.inscricoes[7].id)
    assert posicoes[um] == 1 and posicoes[dois] == 2, "o desempate pela prova separa 01 de 02"
    assert posicoes[tres] == posicoes[quatro] == 3, "03 e 04 permanecem empatados"
    assert posicoes.get(oito) is None, "08, eliminado na prova, fica fora da ordem"
    m.emitir_ordem(c.RESERVADA)
    m.divulgar(ato)


def test_c05_a_avaliacao_conclui_as_pendentes_e_a_presidencia_consolida(cenario):
    from processo_seletivo.avaliacoes.application.avaliacao import concluir
    from processo_seletivo.publicacoes.application.selectors import effective_version
    from processo_seletivo.resultados.application.consolidacao import consolidar

    m = cenario("C05")
    versao = effective_version(edital_id=m.edital.id)
    for inscricao in m.inscricoes[3:]:
        concluir(
            ator=m.ator(c.AVALIACAO_1),
            edital=m.edital,
            etapa_id=m.id(c.ETAPA_PROVA),
            inscricao_id=inscricao.id,
            pontuacao=Decimal("7.0"),
            parecer="Exercício.",
            expected_revision=1,
            versao_reconhecida=versao.id,
            correlation_id="exercicio",
        )
    consolidar(
        actor=m.ator(c.PRESIDENCIA),
        processo_id=m.processo.id,
        edital_id=m.edital.id,
        etapa_id=m.id(c.ETAPA_PROVA),
        inscricao_ids=[i.id for i in m.inscricoes],
        idempotency_key="exercicio-c05-consolidar",
        correlation_id="exercicio",
    )


def test_c06_a_presidencia_congela_a_relacao(cenario):
    from processo_seletivo.sorteios.models import RelacaoDeHabilitados

    m = cenario("C06")
    assert not RelacaoDeHabilitados.objects.filter(edital=m.edital).exists()
    m.congelar_relacao()
    assert RelacaoDeHabilitados.objects.filter(edital=m.edital).count() == 1


def test_c07_o_sorteio_se_realiza_sem_esperar_e_so_pela_presidencia(cenario):
    from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
    from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
    from processo_seletivo.sorteios.models import Sorteio
    from processo_seletivo.treinamento.catalogo import concurso_da_rodada

    m = cenario("C07")
    manifesto = CenarioDeTreinamento.objects.get(codigo="C07")
    ocorrencia = observar_ocorrencia(
        actor=m.ator(c.PRESIDENCIA),
        processo_id=m.processo.id,
        fonte="Fonte de demonstração",
        referencia=concurso_da_rodada("cefor", "C07", 1),
        idempotency_key="exercicio-c07-ocorrencia",
        correlation_id="exercicio",
    )
    argumentos = {
        "processo_id": m.processo.id,
        "edital_id": m.edital.id,
        "relacao_id": manifesto.registros["relacao_do_sorteio"][0],
        "ocorrencia_id": ocorrencia["ocorrencia"],
        "correlation_id": "exercicio",
    }
    with pytest.raises(DomainError):
        constituir_sorteio(
            actor=m.ator(c.AVALIACAO_1), idempotency_key="exercicio-c07-intruso", **argumentos
        )
    constituir_sorteio(
        actor=m.ator(c.PRESIDENCIA), idempotency_key="exercicio-c07-sorteio", **argumentos
    )
    assert Sorteio.objects.filter(edital=m.edital).count() == 1


def test_c08_o_candidato_recorre_do_resultado_preliminar(cenario):
    from processo_seletivo.divulgacao.models import PublicacaoResultado
    from processo_seletivo.recursos.application.interpor import interpor

    m = cenario("C08")
    publicacao = PublicacaoResultado.objects.get(edital=m.edital)
    assert publicacao.natureza == "PRELIMINAR"
    recurso = interpor(
        identidade=m.identidade(m.pessoas[6]),
        inscricao=m.inscricoes[6],
        publicacao=publicacao,
        fundamentacao="Peço a revisão da nota de títulos (exercício de treinamento).",
        assinatura_do_objeto=str(publicacao.pk),
        idempotency_key="exercicio-c08-recurso",
    )
    assert recurso.pk


def test_c09_o_definitivo_esta_divulgado_e_a_etapa_documental_avanca(cenario):
    from processo_seletivo.divulgacao.models import PublicacaoResultado

    m = cenario("C09")
    assert PublicacaoResultado.objects.get(edital=m.edital).natureza == "DEFINITIVA"
    m.avaliar(c.ETAPA_DOCUMENTAL, {inscricao: "FAVORAVEL" for inscricao in m.inscricoes})
    m.cortar_e_apurar()


def test_c10_a_presidencia_convoca_com_a_lista_de_documentos(cenario):
    m = cenario("C10")
    convocacao = m.convocar(m.inscricoes[0], 1)
    m.comunicar(convocacao, 1)
    itens = m.itens(convocacao)
    assert {m.id(c.DOC_DIPLOMA), m.id(c.DOC_RESIDENCIA)} <= set(itens)
    assert m.id(c.DOC_AUTODECLARACAO) not in itens, "a autodeclaração não se aplica à ampla"


def test_c11_os_convocados_estao_em_tres_situacoes_e_entregam(cenario):
    from processo_seletivo.convocacao.models import Convocacao

    m = cenario("C11")
    convocacoes = {conv.inscricao_id: conv for conv in Convocacao.objects.filter(edital=m.edital)}
    assert len(convocacoes) == 3
    primeira = convocacoes[m.inscricoes[0].id]
    assert not any(item.apresentacoes.exists() for item in m.itens(primeira).values())
    m.apresentar(primeira, m.inscricoes[0], c.DOC_DIPLOMA)
    segunda = convocacoes[m.inscricoes[1].id]
    diploma = m.itens(segunda)[m.id(c.DOC_DIPLOMA)]
    assert diploma.conferencias.get().resultado == "PENDENTE"
    m.apresentar(segunda, m.inscricoes[1], c.DOC_DIPLOMA, versao=2)
    assert diploma.apresentacoes.count() == 2


def test_c12_a_conferencia_registra_pendencia(cenario):
    from processo_seletivo.convocacao.models import Convocacao

    m = cenario("C12")
    convocacao = Convocacao.objects.get(edital=m.edital, inscricao=m.inscricoes[0])
    item = m.itens(convocacao)[m.id(c.DOC_RESIDENCIA)]
    apresentacao = item.apresentacoes.get()
    m.conferir(convocacao, c.DOC_RESIDENCIA, apresentacao, "PENDENTE", motivo="Exercício.")
    assert item.conferencias.count() == 1


def test_c13_a_retificacao_se_elabora_e_so_quem_elabora_a_cria(cenario):
    from processo_seletivo.publicacoes.application.retificacoes import create_retification
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    m = cenario("C13")
    base = VersaoConsolidada.objects.filter(edital=m.edital).latest("materialized_at")
    dados = {
        "baseSnapshotId": base.id,
        "justification": "Prorrogação (exercício).",
        "changes": [
            {
                "targetPath": f"/schedule/id={m.id(c.EVENTO_INSCRICOES)}/endAt",
                "operation": "REPLACE",
                "newValue": (timezone.now() + timedelta(days=40)).isoformat(),
            }
        ],
    }
    with pytest.raises(DomainError):
        create_retification(
            actor=m.ator(c.PUBLICACAO),
            edital_id=m.edital.id,
            data=dados,
            idempotency_key="exercicio-c13-intruso",
            correlation_id="exercicio",
        )
    retificacao, _ = create_retification(
        actor=m.ator(c.ELABORACAO),
        edital_id=m.edital.id,
        data=dados,
        idempotency_key="exercicio-c13-retificacao",
        correlation_id="exercicio",
    )
    assert retificacao.pk


def test_c14_o_gestor_encerra_o_edital_e_o_processo(cenario):
    from processo_seletivo.processos.application.finalizacao import close_edital, close_process

    m = cenario("C14")
    gestor = m.ator(c.GESTAO, "edital:encerrar", "processo:encerrar")
    edital, _ = close_edital(
        actor=gestor,
        edital_id=m.edital.id,
        expected_revision=m.edital.revision,
        reason="Encerramento (exercício).",
        idempotency_key="exercicio-c14-edital",
        correlation_id="exercicio",
    )
    assert edital.status == Edital.Status.ENCERRADO
    m.processo.refresh_from_db()
    if m.processo.status == ProcessoSeletivo.Status.ATIVO:
        close_process(
            actor=gestor,
            processo_id=m.processo.id,
            expected_revision=m.processo.revision,
            reason="Encerramento (exercício).",
            idempotency_key="exercicio-c14-processo",
            correlation_id="exercicio",
        )


def test_c15_so_os_habilitados_sao_convocados(cenario):
    m = cenario("C15")
    m.convocar(m.inscricoes[0], 1)
    m.convocar(m.inscricoes[1], 2)
    with pytest.raises(DomainError):
        m.convocar(m.inscricoes[2], 3)
