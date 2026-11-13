"""As frentes de trabalho que os cenários exercitam — para validar "quem faz o quê" (V-8).

**O achado** (V-8 da validação do estudo "Minhas atividades", de 12/11/2026): os cenários só
usavam a presidência e a avaliação. A alocação à conferência não aparecia em nenhum, e o C08 abria
com a fila do Julgador vazia — a visão de quem cobre cada frente não tinha o que mostrar.

Cada caso carrega **um** cenário e lê o que a pessoa da frente lê, pela tela e com a identidade que
o guia da equipe manda usar: o membro alocado em "Minhas atividades", o Julgador na faixa da Lista.
A designação para a formalização já vinha do C16; aqui se prova só que ela é de alguém de fora da
comissão, que é o que a frente precisa mostrar.
"""

import pytest
from django.urls import reverse

from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.comissoes.models import AlocacaoAConferencia, MembroComissao
from processo_seletivo.interface import andamento as a
from processo_seletivo.interface import atividades as at
from processo_seletivo.recursos.models import Recurso
from processo_seletivo.treinamento import construcao as c
from processo_seletivo.treinamento.catalogo import RECORRENTE_DO_C08
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.treinamento import carregar, retomar
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

AUTORIDADE = str(AUTORIDADE_DA_SUITE)


@pytest.fixture
def cenario(treinamento):
    treinamento.INTERFACE_SELETOR_IDENTIDADE = True

    def montar(codigo):
        saida = carregar(codigo, autoridade=AUTORIDADE)
        assert f"{codigo}  CRIADO" in saida, saida
        return retomar(CenarioDeTreinamento.objects.get(codigo=codigo), autoridade=AUTORIDADE)

    return montar


def _minhas_atividades(client, subject, papeis=()):
    identificar(client, subject, list(papeis))
    resposta = client.get(reverse("interface:minhas-etapas"))
    assert resposta.status_code == 200
    return resposta.context["atividades"], resposta.content.decode()


# --- C12: a conferência por alocação (115) -----------------------------------------------------


def test_c12_um_membro_que_nao_preside_esta_alocado_a_conferencia_de_todos_os_perfis(cenario):
    m = cenario("C12")
    [alocacao] = AlocacaoAConferencia.objects.filter(edital=m.edital, ativo=True)
    assert alocacao.membro.identity_subject == c.AVALIACAO_2
    assert alocacao.membro.funcao == Funcao.MEMBRO
    assert alocacao.perfil_id is None, "todos os Perfis"
    assert alocacao.criado_por == c.GESTAO


def test_c12_o_membro_alocado_ve_conferir_com_a_marca_alocacao(cenario, client):
    """A frente da conferência tem alguém que não é a presidência, e essa pessoa sabe disso."""
    m = cenario("C12")
    atividades, html = _minhas_atividades(client, c.AVALIACAO_2)

    assert atividades.para_fazer, "três convocados com documentos a conferir"
    assert {grupo.base for grupo in atividades.para_fazer} == {at.ALOCACAO}
    assert {grupo.providencia.responsavel for grupo in atividades.para_fazer} == {a.CONFERE}
    assert all(grupo.ato.startswith("Conferir") for grupo in atividades.para_fazer)
    assert f"Edital {m.edital.number}/{m.edital.year}" in html
    assert "· pela alocação</span>" in html


def test_c12_dois_membros_de_subject_com_o_mesmo_final_tem_alocacoes_distintas(cenario):
    """A chave levava só o último caractere do subject, e a segunda alocação de quem também
    termina em "2" voltava a primeira, sem erro (revisão do #513)."""
    from processo_seletivo.comissoes.application.comissao import adicionar_membro

    m = cenario("C12")
    outro = "treino.revisao2"
    m.membros[outro], _ = adicionar_membro(
        actor=m.ator(c.GESTAO),
        processo_id=m.processo.id,
        identity_subject=outro,
        funcao=Funcao.MEMBRO,
        idempotency_key=m.chave("v8-membro-revisao2"),
        correlation_id=m.correlacao,
    )
    alocacao = m.alocar_a_conferencia(outro)

    assert alocacao.membro.identity_subject == outro
    ativas = AlocacaoAConferencia.objects.filter(edital=m.edital, ativo=True)
    assert set(ativas.values_list("membro__identity_subject", flat=True)) == {c.AVALIACAO_2, outro}


def test_c12_a_presidencia_continua_conferindo_pela_presidencia(cenario, client):
    cenario("C12")
    atividades, _ = _minhas_atividades(client, c.PRESIDENCIA)

    conferir = [g for g in atividades.para_fazer if g.providencia.responsavel == a.CONFERE]
    assert conferir and {g.base for g in conferir} == {at.PRESIDENCIA}


def test_c12_o_membro_alocado_confere_e_nao_desfecha(cenario):
    """D-010 da `115`: alocar dá a conferência, e não o desfecho."""
    from processo_seletivo.convocacao.application.desfechar import desfechar
    from processo_seletivo.convocacao.application.documentos import conferir
    from processo_seletivo.convocacao.models import Convocacao
    from processo_seletivo.shared.api.problems import DomainError

    m = cenario("C12")
    convocacao = Convocacao.objects.get(edital=m.edital, inscricao=m.inscricoes[0])
    item = m.itens(convocacao)[m.id(c.DOC_RESIDENCIA)]

    conferir(
        actor=m.ator(c.AVALIACAO_2),
        item_id=item.id,
        apresentacao_id=item.apresentacoes.get().id,
        resultado="PENDENTE",
        motivo="Comprovante sem data de emissão (exercício).",
        idempotency_key=m.chave("v8-conferir"),
        correlation_id=m.correlacao,
    )
    assert item.conferencias.get().conferido_por == c.AVALIACAO_2

    with pytest.raises(DomainError):
        desfechar(
            actor=m.ator(c.AVALIACAO_2),
            processo_id=m.processo.id,
            convocacao_id=convocacao.id,
            especie="ACEITE",
            fundamento="Exercício.",
            idempotency_key=m.chave("v8-desfechar"),
            correlation_id=m.correlacao,
        )


# --- C08: o recurso admitido, à espera do mérito (018) -----------------------------------------


def test_c08_ha_um_recurso_admitido_e_sem_decisao(cenario):
    m = cenario("C08")
    [recurso] = Recurso.objects.filter(inscricao__edital=m.edital)
    assert recurso.inscricao_id == m.inscricoes[RECORRENTE_DO_C08 - 1].id
    [juizo] = recurso.juizos.all()
    assert juizo.admitido and juizo.decidido_por == c.JULGAMENTO
    assert not recurso.decisoes.exists(), "o mérito é o exercício do Julgador"
    assert c.MARCA in recurso.fundamentacao


def test_c08_o_julgador_ve_o_recurso_na_faixa_da_lista(cenario, client):
    m = cenario("C08")
    identificar(client, "julgadora.c08", ["julgador"])
    resposta = client.get(reverse("interface:lista"))
    assert resposta.status_code == 200
    itens = [(objeto.chave, objeto.ato) for objeto in resposta.context["faixa"].objetos]
    assert (("recursos", m.edital.id), "Decidir recursos (1)") in itens


def test_c08_o_candidato_08_continua_podendo_recorrer_pela_montagem_retomada(cenario):
    """O exercício do candidato não colide com o recurso já interposto: são pessoas diferentes.

    **Pela montagem retomada**, que não divulgou nada no próprio objeto: `recorrer` lia a publicação
    só do atributo que `divulgar` grava, e dava `AttributeError` (revisão do #513).
    """
    from processo_seletivo.divulgacao.models import PublicacaoResultado

    m = cenario("C08")
    assert m.resultado_divulgado is None
    recurso = m.recorrer(m.inscricoes[7], "Peço a revisão da prova (exercício)", "08")
    assert recurso.publicacao_atacada == PublicacaoResultado.objects.get(edital=m.edital)
    assert Recurso.objects.filter(inscricao__edital=m.edital).count() == 2
    assert recurso.inscricao_id == m.inscricoes[7].id


# --- C16: a designação é de quem não integra a comissão (117) ---------------------------------


def test_c16_a_designada_para_a_formalizacao_nao_integra_a_comissao(cenario):
    from processo_seletivo.formalizacao.models import DesignacaoParaFormalizacao

    m = cenario("C16")
    [designacao] = DesignacaoParaFormalizacao.objects.filter(edital=m.edital)
    assert designacao.pessoa == c.FORMALIZACAO
    comissao = set(
        MembroComissao.objects.filter(processo=m.processo).values_list(
            "identity_subject", flat=True
        )
    )
    assert comissao and c.FORMALIZACAO not in comissao
