"""A publicação da agenda (167, T044, FR-7223, FR-7224, FR-7240, FR-7256, SC-2396, US3 5 e 6).

O ato com autor, autoridade congelada, instante, conteúdo e resumo, e um horário publicado por
pessoa; o veículo e o que ele exige; a assinatura velha recusada; a confirmação repetida devolvendo
o mesmo ato; e, depois, a montagem fechada e a configuração que só cresce.
"""

import json
from datetime import date, time

import pytest

from processo_seletivo.agendamento.application import configurar, leitura, montar
from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.domain.horarios import Banca
from processo_seletivo.agendamento.domain.recusas import ConfiguracaoRecusada
from processo_seletivo.agendamento.models import AtoDaAgenda, HorarioPublicado
from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.canonical import canonical_sha256
from tests.fixtures.agenda_da_etapa import (
    DECLARACAO,
    DUAS_HORAS,
    SEG,
    TER,
    configuracao,
    montar_completa,
    publicar_agenda,
)
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_a_publicacao_grava_o_ato_e_um_horario_por_pessoa(
    gestor, edital_a, etapa_a2, inscricoes, publicada
):
    ato = AtoDaAgenda.objects.get()
    assert ato == publicada
    assert ato.especie == nomes.PUBLICACAO
    assert ato.praticado_por == gestor.subject
    assert ato.signatario_id == AUTORIDADE_DA_SUITE
    assert ato.signatario_cargo == "Diretora-Geral"
    assert ato.unidade_sigla == "Cefor"
    assert ato.veiculo == nomes.VEICULO_GPS and ato.declaracao_do_veiculo == DECLARACAO
    conteudo = json.loads(bytes(ato.conteudo_publico))
    assert ato.conteudo_publico_hash == canonical_sha256(conteudo)
    assert conteudo["cabecalho"]["signatario"]["cargo"] == "Diretora-Geral"
    assert conteudo["cabecalho"]["publicadoEm"]
    horarios = HorarioPublicado.objects.filter(ato=ato)
    assert sorted(h.inscricao_id for h in horarios) == sorted(i.id for i in inscricoes)
    assert all(h.situacao == nomes.AGENDADO and h.aviso_id is None for h in horarios)
    # O ato é o que foi conferido: os pares do horário publicado são os do agendamento.
    assert {(h.inscricao_id, h.banca_id, h.inicio) for h in horarios} == {
        (a.inscricao_id, a.banca_id, a.inicio)
        for a in leitura.agendamentos(leitura.agenda_da_etapa(edital_a, etapa_a2))
    }


def test_a_trilha_registra_a_publicacao_sem_sala_nem_email(
    edital_a, etapa_a2, inscricoes, publicada
):
    registro = RegistroAuditoria.objects.get(operation=nomes.PUBLICACAO_DA_AGENDA)
    assert registro.new_state == "PUBLICADA"
    assert registro.detalhe["ato"] == str(publicada.id)
    assert len(registro.detalhe["posterior"]) == len(inscricoes)
    texto = json.dumps(registro.detalhe) + registro.reason
    assert "sala.exemplo" not in texto
    assert "@exemplo.br" not in texto


def test_a_publicacao_sobe_a_revisao_da_agenda(gestor, edital_a, etapa_a2, inscricoes):
    montar_completa(gestor, edital_a, etapa_a2)
    antes = leitura.agenda_da_etapa(edital_a, etapa_a2).revision

    publicar_agenda(gestor, edital_a, etapa_a2)

    assert leitura.agenda_da_etapa(edital_a, etapa_a2).revision == antes + 1


@pytest.mark.parametrize(
    ("campos", "codigo"),
    [
        ({"veiculo": ""}, nomes.VEICULO_NAO_ESCOLHIDO),
        ({"veiculo": "GPS", "declaracao": "  "}, nomes.DECLARACAO_DO_VEICULO_AUSENTE),
        (
            {"veiculo": "EXTERNO", "declaracao": "", "onde": "Site"},
            nomes.PUBLICACAO_EXTERNA_INCOMPLETA,
        ),
        (
            {"veiculo": "EXTERNO", "declaracao": "", "quando": "2026-11-20"},
            nomes.PUBLICACAO_EXTERNA_INCOMPLETA,
        ),
        ({"autoridade_id": ""}, nomes.AUTORIDADE_INVALIDA),
        ({"autoridade_id": "00000000-0000-0000-0000-000000000999"}, nomes.AUTORIDADE_INVALIDA),
    ],
)
def test_o_veiculo_e_a_autoridade_incompletos_recusam_sem_gravar(
    gestor, edital_a, etapa_a2, inscricoes, campos, codigo
):
    montar_completa(gestor, edital_a, etapa_a2)

    with pytest.raises(DomainError) as recusa:
        publicar_agenda(gestor, edital_a, etapa_a2, **campos)

    assert recusa.value.code == codigo
    assert not AtoDaAgenda.objects.exists()
    assert not HorarioPublicado.objects.exists()


def test_publicar_fora_do_gps_grava_onde_e_quando(gestor, edital_a, etapa_a2, inscricoes):
    montar_completa(gestor, edital_a, etapa_a2)

    ato = publicar_agenda(
        gestor,
        edital_a,
        etapa_a2,
        veiculo="EXTERNO",
        declaracao="",
        onde="Site do campus",
        quando="2026-11-20",
    )

    assert ato.veiculo == nomes.VEICULO_EXTERNO
    assert ato.publicado_fora_onde == "Site do campus"
    assert ato.publicado_fora_em == date(2026, 11, 20)
    assert ato.declaracao_do_veiculo == ""


def test_a_assinatura_velha_recusa_e_nada_se_grava(gestor, edital_a, etapa_a2, inscricoes):
    """US3, cenário 5: a agenda mudou noutra sessão entre a conferência e a confirmação."""
    from processo_seletivo.agendamento.application import conferir

    montar_completa(gestor, edital_a, etapa_a2)
    velha = conferir.conferencia(actor=gestor, edital=edital_a, etapa_id=etapa_a2).assinatura
    montar.liberar(actor=gestor, edital=edital_a, etapa_id=etapa_a2, inscricao_id=inscricoes[0].id)
    horario = next(
        h
        for h in leitura.montagem(
            edital_a, etapa_a2, leitura.agenda_da_etapa(edital_a, etapa_a2)
        ).livres
    )
    montar.agendar(
        actor=gestor,
        edital=edital_a,
        etapa_id=etapa_a2,
        inscricao_id=inscricoes[0].id,
        banca_id=horario.banca_id,
        inicio=horario.inicio,
    )

    with pytest.raises(DomainError) as recusa:
        publicar_agenda(gestor, edital_a, etapa_a2, assinatura=velha)

    assert recusa.value.code == nomes.AGENDA_MUDOU_DESDE_A_CONFERENCIA
    assert recusa.value.detail == "A agenda mudou desde esta conferência. Confira de novo."
    assert not AtoDaAgenda.objects.exists()


def test_com_impedimento_a_publicacao_recusa(gestor, edital_a, etapa_a2, inscricoes, configurada):
    """SC-2393: cinco pessoas sem horário — a confirmação recusa, mesmo com a assinatura certa."""
    with pytest.raises(DomainError) as recusa:
        publicar_agenda(gestor, edital_a, etapa_a2)

    assert recusa.value.code == nomes.PUBLICACAO_IMPEDIDA
    assert "5 pessoas estão sem horário" in recusa.value.detail
    assert not AtoDaAgenda.objects.exists()


def test_a_confirmacao_repetida_devolve_o_mesmo_ato(gestor, edital_a, etapa_a2, inscricoes):
    """US3, cenário 6, SC-2396: com a mesma chave e com outra, um ato só."""
    montar_completa(gestor, edital_a, etapa_a2)
    primeiro = publicar_agenda(gestor, edital_a, etapa_a2, chave="clique-1")
    # A segunda confirmação leva a assinatura que a tela tinha — a da conferência de antes.
    assinatura = primeiro.assinatura_conferida

    mesma_chave = publicar_agenda(
        gestor, edital_a, etapa_a2, chave="clique-1", assinatura=assinatura
    )
    outra_chave = publicar_agenda(
        gestor, edital_a, etapa_a2, chave="clique-2", assinatura=assinatura
    )

    assert mesma_chave == primeiro == outra_chave
    assert AtoDaAgenda.objects.count() == 1
    assert HorarioPublicado.objects.count() == len(inscricoes)
    assert RegistroAuditoria.objects.filter(operation=nomes.PUBLICACAO_DA_AGENDA).count() == 1


def test_depois_da_publicacao_a_montagem_recusa(gestor, edital_a, etapa_a2, inscricoes, publicada):
    """FR-7240: preencher, agendar e liberar recusam `agenda_publicada`."""
    gestos = [
        lambda: montar.previa_do_preenchimento(actor=gestor, edital=edital_a, etapa_id=etapa_a2),
        lambda: montar.aplicar_preenchimento(
            actor=gestor, edital=edital_a, etapa_id=etapa_a2, assinatura="x"
        ),
        lambda: montar.liberar(
            actor=gestor, edital=edital_a, etapa_id=etapa_a2, inscricao_id=inscricoes[0].id
        ),
        lambda: montar.agendar(
            actor=gestor,
            edital=edital_a,
            etapa_id=etapa_a2,
            inscricao_id=inscricoes[0].id,
            banca_id=publicada.horarios.first().banca_id,
            inicio=publicada.horarios.first().inicio,
            mudanca=True,
        ),
    ]
    for gesto in gestos:
        with pytest.raises(DomainError) as recusa:
            gesto()
        assert recusa.value.code == nomes.AGENDA_PUBLICADA
        assert "use Remarcar na agenda publicada" in recusa.value.detail


def _configuracao_publicada(edital, etapa, **mudancas):
    """A configuração gravada, como o formulário a reenviaria, com as mudanças pedidas."""
    atual = leitura.configuracao_da_agenda(leitura.agenda_da_etapa(edital, etapa))
    valores = {
        "forma": atual.forma,
        "duracao": atual.duracao,
        "intervalo": atual.intervalo,
        "dias": atual.dias,
        "bancas": atual.bancas,
        "orientacoes": atual.orientacoes,
    }
    valores.update(mudancas)
    return type(atual)(**valores)


def _salvar(gestor, edital, etapa, config):
    return configurar.salvar(actor=gestor, edital=edital, etapa_id=etapa, configuracao=config)


def test_depois_da_publicacao_a_configuracao_aceita_acrescentar(
    gestor, edital_a, etapa_a2, inscricoes, publicada
):
    """FR-7208: dia, janela num dia existente e banca nova — os três acréscimos."""
    atual = _configuracao_publicada(edital_a, etapa_a2)
    mais = _configuracao_publicada(
        edital_a,
        etapa_a2,
        dias=(
            (SEG, (*DUAS_HORAS, (time(13), time(14)))),
            (TER, DUAS_HORAS),
        ),
        bancas=(*atual.bancas, Banca("nova-2", "Banca 2", "https://sala.exemplo/2", 2)),
    )

    salva = _salvar(gestor, edital_a, etapa_a2, mais)

    assert salva.devolvidos == []
    assert len(leitura.agenda_da_etapa(edital_a, etapa_a2).bancas_em_ordem) == 2


@pytest.mark.parametrize(
    "mudanca",
    [
        {"duracao": 20},
        {"intervalo": 0},
        {"forma": "PRESENCIAL"},
        {"orientacoes": "Outro texto."},
        {"dias": ((SEG, ((time(8), time(11)),)),)},
    ],
)
def test_depois_da_publicacao_mudar_parametro_recusa(
    gestor, edital_a, etapa_a2, inscricoes, publicada, mudanca
):
    with pytest.raises(ConfiguracaoRecusada) as recusa:
        _salvar(gestor, edital_a, etapa_a2, _configuracao_publicada(edital_a, etapa_a2, **mudanca))

    codigos = [problema.codigo for problema in recusa.value.problemas]
    assert codigos[0] == nomes.PARAMETRO_PUBLICADO_ALTERADO
    assert "A agenda já foi publicada com 10 minutos e 5 de intervalo" in recusa.value.detail


def test_depois_da_publicacao_mudar_o_endereco_da_banca_recusa(
    gestor, edital_a, etapa_a2, inscricoes, publicada
):
    atual = _configuracao_publicada(edital_a, etapa_a2)
    banca = atual.bancas[0]
    trocada = Banca(banca.id, banca.nome, "https://outra.sala/9", banca.ordem)

    with pytest.raises(ConfiguracaoRecusada) as recusa:
        _salvar(
            gestor,
            edital_a,
            etapa_a2,
            _configuracao_publicada(edital_a, etapa_a2, bancas=(trocada,)),
        )

    assert recusa.value.problemas[0].codigo == nomes.PARAMETRO_PUBLICADO_ALTERADO


def test_depois_da_publicacao_remover_o_horario_publicado_recusa_e_nomeia(
    gestor, edital_a, etapa_a2, inscricoes, publicada
):
    """Tirar o dia publicado inteiro: cada pessoa publicada é nomeada, e nada se grava."""
    revisao = leitura.agenda_da_etapa(edital_a, etapa_a2).revision

    with pytest.raises(ConfiguracaoRecusada) as recusa:
        _salvar(
            gestor,
            edital_a,
            etapa_a2,
            _configuracao_publicada(edital_a, etapa_a2, dias=((TER, DUAS_HORAS),)),
        )

    removidos = [p for p in recusa.value.problemas if p.codigo == nomes.HORARIO_PUBLICADO_REMOVIDO]
    assert len(removidos) == len(inscricoes)
    assert removidos[0].frase.startswith("A agenda já foi publicada, e ")
    assert "para mudar uma pessoa, use Remarcar" in removidos[0].frase
    assert leitura.agenda_da_etapa(edital_a, etapa_a2).revision == revisao
    assert configuracao  # a fixture de partida continua a do cenário
