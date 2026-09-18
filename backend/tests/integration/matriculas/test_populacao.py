"""Quem entra no arquivo, e sob qual norma (`FR-433`, `FR-434`, Princípio II).

**Estes são os dois erros que produziriam um arquivo plausível e errado**: exportar gente que o
certame não selecionou, e exportar sob a norma de hoje o que foi decidido sob a de ontem. Nenhum
dos dois aparece na conferência de quem lê o arquivo — as duas colunas estariam preenchidas, com
valores que parecem certos.
"""

import uuid

import pytest
from django.utils import timezone

from processo_seletivo.classificacao.models import AtoDeOrdenacao
from processo_seletivo.divulgacao.models import Natureza, SituacaoDivulgada
from processo_seletivo.matriculas.application.exportar import compor
from processo_seletivo.matriculas.application.populacao import alcancados_de, escolher, opcoes
from processo_seletivo.matriculas.domain import colunas, nomes
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.divulgacao import publicar_o_ato

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def ato_do_cenario(edital):
    return AtoDeOrdenacao.objects.filter(edital=edital).latest("emitido_em")


def divulgar(edital, *, natureza, chave):
    """Publica o resultado do ato que o cenário emitiu, pelo comando de verdade."""
    return publicar_o_ato(
        {"edital": edital, "ato": ato_do_cenario(edital)}, natureza=natureza, chave=chave
    )


# ---------------------------------------------------------------------------
# Nem toda publicação serve para matricular
# ---------------------------------------------------------------------------


def test_o_resultado_preliminar_nao_e_oferecido(cenario):
    """Preliminar existe **para ser contestado**, e o recurso pode reordenar quem está dentro.

    Matricular a partir dele levaria ao Registro Acadêmico uma lista que o julgamento ainda pode
    mudar — e a matrícula, uma vez feita, não se desfaz por reordenação.
    """
    edital, _ = cenario
    divulgar(edital, natureza=Natureza.PRELIMINAR, chave="031-preliminar")

    assert [opcao for opcao in opcoes(edital) if opcao.especie == nomes.RESULTADO] == []


def test_apontar_para_um_resultado_preliminar_e_recusado(cenario):
    """A tela não o oferece, e a aplicação **também** o recusa (Princípio IV).

    Quem tiver o identificador da publicação — ele é público — não contorna a regra colando-o.
    """
    edital, _ = cenario
    preliminar = divulgar(edital, natureza=Natureza.PRELIMINAR, chave="031-preliminar-post")

    with pytest.raises(DomainError) as recusa:
        escolher(edital, nomes.RESULTADO, str(preliminar.id))
    assert recusa.value.code == nomes.POPULACAO_NAO_ESCOLHIDA


def test_o_definitivo_e_oferecido_e_a_preliminar_sucedida_some(cenario):
    """Corrigir é suceder, e a sucedida continua legível **por não ser a que vale**.

    Oferecer as duas faria quem conduz escolher, numa lista, entre o resultado e a versão dele que
    já foi corrigida.
    """
    edital, _ = cenario
    divulgar(edital, natureza=Natureza.PRELIMINAR, chave="031-pre")
    divulgar(edital, natureza=Natureza.DEFINITIVA, chave="031-def")

    resultados = [opcao for opcao in opcoes(edital) if opcao.especie == nomes.RESULTADO]
    assert len(resultados) == 1
    assert resultados[0].rotulo.startswith("Resultado definitivo")


def test_quem_ficou_sem_posicao_nao_entra_no_arquivo(cenario):
    """`SEM_POSICAO` é quem o ato **considerou e não posicionou**.

    Ele está na publicação porque tem direito de ler a própria situação — e não porque vai se
    matricular. Exportá-lo mandaria ao Registro Acadêmico gente que o certame não selecionou.
    """
    edital, _ = cenario
    divulgado = divulgar(edital, natureza=Natureza.DEFINITIVA, chave="031-sem-posicao")
    populacao = next(opcao for opcao in opcoes(edital) if opcao.especie == nomes.RESULTADO)
    sem_posicao = SituacaoDivulgada.objects.filter(
        publicacao=divulgado,
        situacao=SituacaoDivulgada.Situacao.SEM_POSICAO,
    )
    assert sem_posicao.exists(), "o cenário precisa ter alguém sem posição para o teste medir algo"

    alcancados = alcancados_de(edital, populacao)
    protocolos = {alcancado.inscricao.protocolo for alcancado in alcancados}
    for situacao in sem_posicao.select_related("inscricao"):
        assert situacao.inscricao.protocolo not in protocolos


# ---------------------------------------------------------------------------
# A norma é a do ato, e não a de hoje (Princípio II)
# ---------------------------------------------------------------------------


def _retificar_o_polo(edital, novo_polo):
    """Uma versão consolidada **posterior**, com o polo do Perfil trocado.

    Montada à mão, e não por Retificação: o que se exercita aqui é de qual versão a exportação lê,
    e uma Retificação de verdade traria junto meia dúzia de regras que não têm nada a ver com isso.
    O efeito no que importa é o mesmo — a versão vigente passa a dizer outra coisa.
    """
    atual = VersaoConsolidada.objects.filter(edital=edital).latest("valid_from")
    conteudo = dict(atual.content)
    conteudo["profiles"] = [
        {**perfil, "locality": novo_polo} for perfil in conteudo.get("profiles") or []
    ]
    agora = timezone.now()
    return VersaoConsolidada.objects.create(
        edital=edital,
        valid_from=agora,
        materialized_at=agora,
        source_publication=atual.source_publication,
        content=conteudo,
        canonical_content=b"{}",
        content_hash=uuid.uuid4().hex * 2,
    )


def test_o_arquivo_traz_o_polo_da_versao_que_convocou(cenario, quem_exporta):
    """Princípio II: *"regras atuais NÃO PODEM substituir regras históricas"*.

    A pessoa foi chamada para o polo que o Edital publicava **naquele dia**. Uma Retificação
    posterior vale para o que vier depois dela — e não pode reescrever, em silêncio, o arquivo de
    quem já foi convocado.
    """
    edital, _ = cenario
    escolhida = opcoes(edital)[0]
    antes = compor(
        ator=quem_exporta,
        edital=edital,
        especie=escolhida.especie,
        referencia=escolhida.referencia,
    )
    coluna = colunas.CABECALHOS.index("NOME_POLO")
    polo_original = antes.linhas[0][coluna]

    _retificar_o_polo(edital, "Campus Que Ainda Não Existia")

    depois = compor(
        ator=quem_exporta,
        edital=edital,
        especie=escolhida.especie,
        referencia=escolhida.referencia,
    )
    assert depois.linhas[0][coluna] == polo_original
    assert depois.linhas[0][coluna] != "Campus Que Ainda Não Existia"


def test_a_modalidade_removida_por_retificacao_nao_derruba_a_geracao(cenario, quem_exporta):
    """O caso mais feio da leitura pela norma de hoje, e ele é silencioso até acontecer.

    Uma Retificação que remova a lista de concorrência faria a exportação **não encontrar** a
    Modalidade de quem concorreu por ela — e recusar a geração inteira, nomeando uma pessoa que não
    fez nada de errado. Sob a versão do ato que a alcançou, a Modalidade está lá.
    """
    edital, _ = cenario
    atual = VersaoConsolidada.objects.filter(edital=edital).latest("valid_from")
    conteudo = dict(atual.content)
    conteudo["profiles"] = [
        {**perfil, "competitionModalities": []} for perfil in conteudo.get("profiles") or []
    ]
    agora = timezone.now()
    VersaoConsolidada.objects.create(
        edital=edital,
        valid_from=agora,
        materialized_at=agora,
        source_publication=atual.source_publication,
        content=conteudo,
        canonical_content=b"{}",
        content_hash=uuid.uuid4().hex * 2,
    )

    escolhida = opcoes(edital)[0]
    composicao = compor(
        ator=quem_exporta,
        edital=edital,
        especie=escolhida.especie,
        referencia=escolhida.referencia,
    )
    assert composicao.quantidade
