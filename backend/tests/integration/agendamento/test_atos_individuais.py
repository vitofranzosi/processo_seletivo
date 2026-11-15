"""Depois da publicação, só ato individual (167, T073, T091, FR-7240 a FR-7248, SC-2395, US5).

FR-7241 e FR-7244, a remarcação; FR-7242, a inclusão; FR-7243, o cancelamento; FR-7246, o motivo
fora do público; FR-7248, o documento de cada ato.

A remarcação cria o ato, o horário publicado que substitui o anterior, um aviso só e o documento, e
atualiza o `Agendamento`; sem motivo, para o mesmo horário ou para horário ocupado, recusa. A
inclusão agenda quem passou a participar depois, sem `substitui`. O cancelamento tira da agenda
vigente quem deixou de participar, sem aviso e sem apagar o publicado. O motivo fica na trilha, e
nunca no conteúdo público, no documento ou no aviso.
"""

import json

import pytest

from processo_seletivo.agendamento.application import atos_individuais, leitura
from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.models import (
    Agendamento,
    AtoDaAgenda,
    DocumentoDoAtoDaAgenda,
    HorarioPublicado,
)
from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avisos.models import Aviso
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.agenda_da_etapa import eliminar_na_primeira
from tests.fixtures.comissao import inscrever

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

MOTIVO = "falha de conexão comprovada"


def _livre(edital, etapa):
    agenda = leitura.agenda_da_etapa(edital, etapa)
    return leitura.montagem(edital, etapa, agenda).livres[0]


def _remarcar(gestor, edital, etapa, inscricao, horario, *, motivo=MOTIVO, chave="remarcar-1"):
    return atos_individuais.remarcar(
        actor=gestor,
        edital=edital,
        etapa_id=etapa,
        inscricao_id=inscricao.id,
        banca_id=horario.banca_id,
        inicio=horario.inicio,
        motivo=motivo,
        idempotency_key=chave,
    )


def _texto_do_pdf(ato):
    from tests.interface.test_fluxo import texto_de_pdf_bytes

    return texto_de_pdf_bytes(bytes(DocumentoDoAtoDaAgenda.objects.get(ato=ato).bytes))


def test_a_remarcacao_substitui_o_anterior_e_avisa_so_a_pessoa(
    gestor, edital_a, etapa_a2, inscricoes, publicada
):
    pessoa = inscricoes[0]
    anterior = HorarioPublicado.objects.get(ato=publicada, inscricao=pessoa)
    novo = _livre(edital_a, etapa_a2)
    avisos_antes = Aviso.objects.count()
    ato = _remarcar(gestor, edital_a, etapa_a2, pessoa, novo)

    assert ato.especie == nomes.REMARCACAO and ato.motivo == MOTIVO
    item = HorarioPublicado.objects.get(ato=ato)
    assert item.substitui_id == anterior.id
    assert (str(item.banca_id), item.inicio) == novo.chave
    assert item.aviso is not None and Aviso.objects.count() == avisos_antes + 1
    assert "O horário anterior não vale mais" in item.aviso.corpo
    agendamento = Agendamento.objects.get(agenda=publicada.agenda, inscricao=pessoa)
    assert (str(agendamento.banca_id), agendamento.inicio) == novo.chave
    # O anterior continua existindo, e o vigente é o novo, com a marca de remarcado.
    assert HorarioPublicado.objects.filter(pk=anterior.pk).exists()
    vigentes = {v.inscricao_id: v for v in leitura.vigentes_da_agenda(publicada.agenda)}
    assert vigentes[pessoa.id].pk == item.pk
    assert vigentes[pessoa.id].remarcado_em == ato.praticado_em


def test_o_motivo_fica_na_trilha_e_fora_do_publico(
    gestor, edital_a, etapa_a2, inscricoes, publicada
):
    ato = _remarcar(gestor, edital_a, etapa_a2, inscricoes[0], _livre(edital_a, etapa_a2))
    assert MOTIVO not in bytes(ato.conteudo_publico).decode("utf-8")
    assert MOTIVO not in _texto_do_pdf(ato)
    assert MOTIVO not in HorarioPublicado.objects.get(ato=ato).aviso.corpo
    registro = RegistroAuditoria.objects.get(operation=nomes.REMARCACAO_DA_AGENDA)
    assert registro.detalhe["motivo"] == MOTIVO
    assert registro.detalhe["anterior"]["protocolo"] == inscricoes[0].protocolo
    assert registro.detalhe["posterior"]["inicio"]
    assert "@" not in str(registro.detalhe) and "sala.exemplo" not in str(registro.detalhe)


def test_cada_ato_tem_documento_e_o_da_publicacao_nao_muda(
    gestor, edital_a, etapa_a2, inscricoes, publicada
):
    da_publicacao = DocumentoDoAtoDaAgenda.objects.get(ato=publicada)
    hash_antes = da_publicacao.documento_hash
    ato = _remarcar(gestor, edital_a, etapa_a2, inscricoes[0], _livre(edital_a, etapa_a2))
    assert DocumentoDoAtoDaAgenda.objects.get(ato=publicada).documento_hash == hash_antes
    texto = _texto_do_pdf(ato)
    assert "REMARCAÇÃO NA AGENDA DA ETAPA" in texto
    assert inscricoes[0].protocolo in texto
    assert inscricoes[1].protocolo not in texto
    assert "sala.exemplo" not in texto
    documentos = [d["ato"].especie for d in leitura.documentos_da_agenda(publicada.agenda)]
    assert documentos == [nomes.PUBLICACAO, nomes.REMARCACAO]
    conteudo = json.loads(bytes(ato.conteudo_publico))
    assert conteudo["cabecalho"]["especie"] == nomes.REMARCACAO
    assert "substitui" in conteudo["cabecalho"]["nota"]


def test_sem_motivo_o_mesmo_horario_e_o_ocupado_recusam(
    gestor, edital_a, etapa_a2, inscricoes, publicada
):
    pessoa, outra = inscricoes[0], inscricoes[1]
    livre = _livre(edital_a, etapa_a2)
    casos = [
        (dict(inscricao=pessoa, horario=livre, motivo="  "), nomes.MOTIVO_AUSENTE),
    ]
    atual = Agendamento.objects.get(agenda=publicada.agenda, inscricao=pessoa)
    agenda = publicada.agenda
    montagem = leitura.montagem(edital_a, etapa_a2, agenda)
    proprio = next(h for h in montagem.horarios if h.chave == (str(atual.banca_id), atual.inicio))
    da_outra = Agendamento.objects.get(agenda=agenda, inscricao=outra)
    ocupado = next(
        h for h in montagem.horarios if h.chave == (str(da_outra.banca_id), da_outra.inicio)
    )
    casos += [
        (dict(inscricao=pessoa, horario=proprio), nomes.MESMO_HORARIO),
        (dict(inscricao=pessoa, horario=ocupado), nomes.HORARIO_OCUPADO),
    ]
    for indice, (campos, codigo) in enumerate(casos):
        with pytest.raises(DomainError) as recusa:
            _remarcar(
                gestor,
                edital_a,
                etapa_a2,
                campos["inscricao"],
                campos["horario"],
                motivo=campos.get("motivo", MOTIVO),
                chave=f"recusa-{indice}",
            )
        assert recusa.value.code == codigo
    assert recusa.value.status == 409
    assert AtoDaAgenda.objects.filter(especie=nomes.REMARCACAO).count() == 0


def test_antes_da_publicacao_o_ato_individual_recusa(
    gestor, edital_a, etapa_a2, inscricoes, configurada
):
    agenda = leitura.agenda_da_etapa(edital_a, etapa_a2)
    horario = leitura.montagem(edital_a, etapa_a2, agenda).horarios[0]
    with pytest.raises(DomainError) as recusa:
        _remarcar(gestor, edital_a, etapa_a2, inscricoes[0], horario)
    assert recusa.value.code == nomes.AGENDA_NAO_PUBLICADA


def test_a_inclusao_agenda_quem_passou_a_participar_depois(
    gestor, edital_a, etapa_a2, inscricoes, publicada
):
    (nova,) = inscrever(edital_a, 1, primeiro=90)
    livre = _livre(edital_a, etapa_a2)
    ato = atos_individuais.incluir(
        actor=gestor,
        edital=edital_a,
        etapa_id=etapa_a2,
        inscricao_id=nova.id,
        banca_id=livre.banca_id,
        inicio=livre.inicio,
        motivo="recurso deferido",
        idempotency_key="incluir-1",
    )
    item = HorarioPublicado.objects.get(ato=ato)
    assert ato.especie == nomes.INCLUSAO and item.substitui_id is None
    assert item.aviso is not None and "agendou o seu horário" in item.aviso.corpo
    assert Agendamento.objects.filter(agenda=publicada.agenda, inscricao=nova).exists()
    assert nova.id in {v.inscricao_id for v in leitura.vigentes_da_agenda(publicada.agenda)}
    # Incluir de novo quem já tem horário publicado recusa, e manda usar Remarcar.
    outro = _livre(edital_a, etapa_a2)
    with pytest.raises(DomainError) as recusa:
        atos_individuais.incluir(
            actor=gestor,
            edital=edital_a,
            etapa_id=etapa_a2,
            inscricao_id=nova.id,
            banca_id=outro.banca_id,
            inicio=outro.inicio,
            motivo="de novo",
            idempotency_key="incluir-2",
        )
    assert recusa.value.code == nomes.PESSOA_JA_TEM_HORARIO_PUBLICADO


def test_o_cancelamento_de_quem_ainda_participa_recusa(
    gestor, edital_a, etapa_a2, inscricoes, publicada
):
    with pytest.raises(DomainError) as recusa:
        atos_individuais.cancelar(
            actor=gestor,
            edital=edital_a,
            etapa_id=etapa_a2,
            inscricao_id=inscricoes[0].id,
            motivo="engano",
            idempotency_key="cancelar-0",
        )
    assert recusa.value.code == nomes.CANCELAMENTO_DE_QUEM_PARTICIPA


def test_o_cancelamento_tira_da_vigente_sem_aviso_e_sem_apagar(
    gestor, edital_a, etapa_a1, etapa_a2, inscricoes, publicada
):
    saiu = inscricoes[1]
    eliminar_na_primeira(gestor, edital_a, etapa_a1, [saiu])
    anterior = HorarioPublicado.objects.get(ato=publicada, inscricao=saiu)
    avisos_antes = Aviso.objects.count()
    ato = atos_individuais.cancelar(
        actor=gestor,
        edital=edital_a,
        etapa_id=etapa_a2,
        inscricao_id=saiu.id,
        motivo="eliminada na Etapa anterior",
        idempotency_key="cancelar-1",
    )
    item = HorarioPublicado.objects.get(ato=ato)
    assert item.situacao == nomes.CANCELADO and item.substitui_id == anterior.id
    assert item.aviso is None and Aviso.objects.count() == avisos_antes
    assert HorarioPublicado.objects.filter(pk=anterior.pk).exists()
    assert not Agendamento.objects.filter(agenda=publicada.agenda, inscricao=saiu).exists()
    assert saiu.id not in {v.inscricao_id for v in leitura.vigentes_da_agenda(publicada.agenda)}
    assert DocumentoDoAtoDaAgenda.objects.filter(ato=ato).exists()
    assert "eliminada" not in _texto_do_pdf(ato)
    assert RegistroAuditoria.objects.get(operation=nomes.CANCELAMENTO_NA_AGENDA).detalhe[
        "motivo"
    ] == ("eliminada na Etapa anterior")


def test_a_repeticao_com_a_mesma_chave_devolve_o_mesmo_ato(
    gestor, edital_a, etapa_a2, inscricoes, publicada
):
    livre = _livre(edital_a, etapa_a2)
    primeiro = _remarcar(gestor, edital_a, etapa_a2, inscricoes[0], livre)
    segundo = _remarcar(gestor, edital_a, etapa_a2, inscricoes[0], livre)
    assert primeiro.pk == segundo.pk
    assert AtoDaAgenda.objects.filter(especie=nomes.REMARCACAO).count() == 1


def test_com_os_avisos_desligados_o_ato_acontece_sem_aviso(
    gestor, edital_a, etapa_a2, inscricoes, publicada, settings
):
    settings.AVISOS_AOS_CANDIDATOS = False
    avisos_antes = Aviso.objects.count()
    ato = _remarcar(gestor, edital_a, etapa_a2, inscricoes[0], _livre(edital_a, etapa_a2))
    assert HorarioPublicado.objects.get(ato=ato).aviso is None
    assert Aviso.objects.count() == avisos_antes
