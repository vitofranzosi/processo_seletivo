"""A jornada da análise das inscrições: preliminar, recurso, correção e homologação (148).

O recurso é o que existe — contra o `ResultadoEtapa` —, e o que esta feature acrescenta é o fato
que o torna possível: o preliminar publicado autoriza a visibilidade e abre a janela (D-003). A
homologação espera a disputa acabar (D-004), e publica a situação vigente, já corrigida. O
preliminar continua legível como foi publicado, byte a byte (SC-1705).
"""

from datetime import timedelta

import pytest
from django.db import connection
from django.utils import timezone

from processo_seletivo.divulgacao.application.inscricoes import divergencia_do_vigente
from processo_seletivo.divulgacao.models import InscricaoNaPublicacao, PublicacaoDasInscricoes
from processo_seletivo.portal.identidade import IdentidadeDoCandidato
from processo_seletivo.recursos.application.interpor import interpor, objetos_recorriveis
from processo_seletivo.recursos.application.selectors import pareceres_do_titular
from processo_seletivo.resultados.application.selectors import resultados_visiveis
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.habilitacao import habilitadas_na_etapa
from tests.fixtures.inscricoes_publicadas import (
    analisar,
    evento_de_recurso,
    inscrever_no,
    montar,
    publicar,
)
from tests.fixtures.recursos import admitir, decidir, superar

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def analisado(gestor, api_client, manager_headers):
    """Três inscrições: duas deferidas e uma indeferida, consolidadas."""
    cenario = montar(gestor, api_client, manager_headers, seed=1490, codigo="1490")
    inscricoes = inscrever_no(cenario, 3, primeiro=201)
    analisar(
        cenario,
        gestor,
        [
            (inscricoes[0], "FAVORAVEL"),
            (inscricoes[1], "DESFAVORAVEL"),
            (inscricoes[2], "FAVORAVEL"),
        ],
        sufixo="jornada",
    )
    cenario["inscricoes"] = inscricoes
    return cenario


def titular(inscricao):
    return IdentidadeDoCandidato(
        inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "c@ex.br"
    )


def recorrer(cenario, inscricao, chave="recurso-148"):
    alvo = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    return interpor(
        identidade=titular(inscricao),
        inscricao=inscricao,
        resultado=alvo,
        fundamentacao="O diploma foi anexado no campo de outro documento.",
        assinatura_do_objeto=str(alvo.pk),
        idempotency_key=chave,
    )


def _encerrar_o_prazo(ato):
    """Empurra o término congelado para o passado, sem esperar o relógio.

    O padrão de `tests/integration/recursos/test_janela.py`: o gatilho append-only desligado só pelo
    tempo da escrita. O que se prova é a **aplicação** do prazo, e ela lê o que o banco tem.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "ALTER TABLE divulgacao_publicacaodasinscricoes "
            "DISABLE TRIGGER publicacao_das_inscricoes_append_only"
        )
        cursor.execute(
            "UPDATE divulgacao_publicacaodasinscricoes SET recurso_ate = %s WHERE id = %s",
            [timezone.now() - timedelta(minutes=1), ato.pk],
        )
        cursor.execute(
            "ALTER TABLE divulgacao_publicacaodasinscricoes "
            "ENABLE TRIGGER publicacao_das_inscricoes_append_only"
        )


def test_antes_do_preliminar_o_indeferido_nao_ve_nem_recorre(analisado):
    """Existir não é ter sido publicado: sem ato, o resultado da análise não é do titular ainda."""
    indeferida = analisado["inscricoes"][1]

    assert resultados_visiveis(indeferida) == []
    assert objetos_recorriveis(indeferida) == []
    with pytest.raises(DomainError) as excinfo:
        recorrer(analisado, indeferida)
    assert excinfo.value.status == 404


@pytest.mark.skipif("connection.vendor != 'postgresql'")
def test_a_jornada_inteira_do_indeferimento_a_homologacao(analisado):
    deferida, indeferida, _outra = analisado["inscricoes"]
    preliminar = publicar(
        analisado, "PRELIMINAR", prazo=evento_de_recurso(analisado["seed"]), chave="preliminar"
    )
    bytes_do_preliminar = bytes(preliminar.conteudo_publico)
    documento_do_preliminar = bytes(preliminar.documento)

    # O titular indeferido vê o próprio resultado, com o motivo, e a ação de recorrer (FR-5415).
    (visivel,) = resultados_visiveis(indeferida)
    assert visivel["etapa"] == "Análise documental"
    assert visivel["habilitada"] is False
    assert "Indeferido" in visivel["motivo"]
    # E o parecer do avaliador, enquanto o prazo corre — a regra da 036, pela janela do preliminar.
    (parecer,) = pareceres_do_titular(indeferida, [visivel]).values()
    assert "Faltou o diploma" in parecer["texto"]
    (recorrivel,) = objetos_recorriveis(indeferida)
    assert recorrivel["tipo"] == "resultado"
    assert recorrivel["fecha_em"] == preliminar.recurso_ate

    # O recurso é o existente, e grava a janela do preliminar (FR-5416, FR-5417).
    recurso = recorrer(analisado, indeferida)
    assert recurso.janela_fecha_em == preliminar.recurso_ate

    # Recurso pendente impede a homologação, e ela diz por quê (FR-5418).
    with pytest.raises(DomainError) as excinfo:
        publicar(analisado, "HOMOLOGACAO", chave="homologa-cedo")
    assert excinfo.value.code == "inscricoes_recurso_pendente"

    # Julgado com correção, o resultado é sucedido pelo mecanismo existente.
    superado = ResultadoEtapa.vigentes.get(inscricao=indeferida, etapa_id=analisado["etapa"])
    admitir(recurso)
    decisao = decidir(
        recurso,
        protegido=superado,
        consequencia="HABILITADA",
        forma="DECISORIA",
        sentido="FAVORAVEL",
    )
    superar(superado, decisao, consequencia="HABILITADA")

    # O prazo ainda corre: a homologação espera, com a data.
    with pytest.raises(DomainError) as excinfo:
        publicar(analisado, "HOMOLOGACAO", chave="homologa-no-prazo")
    assert excinfo.value.code == "inscricoes_prazo_correndo"
    assert "31/12/2099" in excinfo.value.detail

    _encerrar_o_prazo(preliminar)
    homologacao = publicar(analisado, "HOMOLOGACAO", chave="homologa")

    assert homologacao.publicacao_anterior_id == preliminar.id
    situacoes = dict(
        InscricaoNaPublicacao.objects.filter(publicacao=homologacao).values_list(
            "inscricao_id", "situacao"
        )
    )
    assert set(situacoes.values()) == {"DEFERIDA"}
    assert indeferida.protocolo in bytes(homologacao.conteudo_publico).decode()

    # O preliminar continua o que foi, byte a byte (SC-1705).
    preliminar = PublicacaoDasInscricoes.objects.get(pk=preliminar.pk)
    assert bytes(preliminar.conteudo_publico) == bytes_do_preliminar
    assert bytes(preliminar.documento) == documento_do_preliminar
    assert indeferida.protocolo not in bytes_do_preliminar.decode()

    # Depois da homologação, o prazo fechou: a ação some, e a interposição é recusada.
    assert objetos_recorriveis(deferida) == []
    assert divergencia_do_vigente(analisado["edital"])["total"] == 0


def test_a_homologacao_e_a_relacao_do_sorteio_leem_a_mesma_fonte(analisado):
    """SC-1706: a Etapa de análise como `qualifyingStageId` dá o conjunto homologado."""
    publicar(analisado, "PRELIMINAR", prazo="SEM_RECURSO", chave="preliminar-sorteio")
    homologacao = publicar(analisado, "HOMOLOGACAO", chave="homologa-sorteio")

    homologadas = {
        str(inscricao_id)
        for inscricao_id in InscricaoNaPublicacao.objects.filter(
            publicacao=homologacao, situacao="DEFERIDA"
        ).values_list("inscricao_id", flat=True)
    }
    assert homologadas == habilitadas_na_etapa(
        analisado["edital"], {"qualifyingStageId": analisado["etapa"]}
    )
    assert len(homologadas) == 2


def test_preliminar_sem_recurso_nega_a_interposicao(analisado):
    """Declarado que o Edital não prevê recurso, o titular vê o motivo e não recorre por aqui."""
    indeferida = analisado["inscricoes"][1]
    publicar(analisado, "PRELIMINAR", prazo="SEM_RECURSO", chave="sem-recurso")

    assert resultados_visiveis(indeferida)[0]["habilitada"] is False
    assert objetos_recorriveis(indeferida) == []
    with pytest.raises(DomainError):
        recorrer(analisado, indeferida, chave="negado")


def test_homologacao_direta_e_definitiva(analisado):
    """Sem preliminar, a homologação publica a análise e não abre prazo (US3, cenário 4)."""
    indeferida = analisado["inscricoes"][1]
    publicar(analisado, "HOMOLOGACAO", chave="direta")

    assert resultados_visiveis(indeferida)[0]["habilitada"] is False
    assert objetos_recorriveis(indeferida) == []


def test_resultado_corrigido_depois_da_homologacao_aparece_como_divergencia(analisado):
    """O ato não muda; a gestão vê que ele envelheceu, e corrige por sucessor (US4, FR-5427)."""
    indeferida = analisado["inscricoes"][1]
    publicar(analisado, "HOMOLOGACAO", chave="homologa-antes")

    from tests.fixtures.recursos import interpor as interpor_por_fora

    superado = ResultadoEtapa.vigentes.get(inscricao=indeferida, etapa_id=analisado["etapa"])
    recurso = interpor_por_fora(inscricao=indeferida, versao=superado.versao, resultado=superado)
    admitir(recurso)
    decisao = decidir(
        recurso,
        protegido=superado,
        consequencia="HABILITADA",
        forma="DECISORIA",
        sentido="FAVORAVEL",
    )
    superar(superado, decisao, consequencia="HABILITADA")

    assert divergencia_do_vigente(analisado["edital"]) == {
        "novas": 0,
        "sairam": 0,
        "mudadas": 1,
        "total": 1,
    }
    corrigida = publicar(
        analisado,
        "HOMOLOGACAO",
        motivo="Recurso julgado depois da homologação.",
        chave="homologa-corrigida",
    )
    assert corrigida.quantidade == 3
    assert divergencia_do_vigente(analisado["edital"])["total"] == 0
