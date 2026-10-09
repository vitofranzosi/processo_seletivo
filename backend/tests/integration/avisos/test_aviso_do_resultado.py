"""O aviso de resultado: os destinatários saem do ato, e a confirmação não envia nada (066, US1).

**O modo de errar aqui não dá erro nenhum.** Uma inscrição a mais ou a menos na lista, uma mensagem
saída no clique, um aviso duplicado pelo duplo clique — tudo isso chega à caixa de entrada de
alguém e não se desfaz. Os casos prendem cada uma dessas portas.
"""

import pytest
from django.core import mail

from processo_seletivo.avisos.application import destinatarios
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.models import Aviso, DestinatarioDoAviso, PublicacaoDoAviso
from processo_seletivo.divulgacao.models import SituacaoDivulgada
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.avisos import avisar_resultado
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def publicado(gestor, api_client, manager_headers, process_payload):
    """Resultado preliminar publicado: duas classificadas e uma considerada sem posição."""
    cenario = montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        pontuacoes=("90.0000", "70.0000", None),
    )
    cenario["publicacao"] = publicar_o_ato(cenario)
    return cenario


def _marco(cenario):
    return cenario["publicacao"].marco_id


def test_os_destinatarios_sao_todos_os_considerados_inclusive_sem_posicao(publicado):
    """`FR-1246`: o universo é o da `SituacaoDivulgada`, e quem ficou sem posição está nele."""
    edital = publicado["edital"]

    declarado = avisar_resultado(edital, _marco(publicado))

    aviso = Aviso.objects.get(pk=declarado["aviso"])
    considerados = set(
        SituacaoDivulgada.objects.filter(publicacao=publicado["publicacao"]).values_list(
            "inscricao_id", flat=True
        )
    )
    assert set(aviso.destinatarios.values_list("inscricao_id", flat=True)) == considerados
    assert SituacaoDivulgada.objects.filter(
        publicacao=publicado["publicacao"], situacao=SituacaoDivulgada.Situacao.SEM_POSICAO
    ).exists()
    assert declarado["destinatarios"] == len(considerados)


def test_o_corpo_nao_diz_a_situacao_de_ninguem(publicado):
    """`D-007`: sem posição, sem pontuação, sem "sem posição"."""
    declarado = avisar_resultado(publicado["edital"], _marco(publicado))

    corpo = Aviso.objects.get(pk=declarado["aviso"]).corpo.lower()
    for proibido in ("sem posição", "classificad", "posição", "90,00", "eliminad"):
        assert proibido not in corpo


def test_sem_endereco_fica_registrado_e_fora_do_envio(publicado):
    sem = publicado["inscricoes"][0]
    Inscricao.objects.filter(pk=sem.pk).update(email="")

    declarado = avisar_resultado(publicado["edital"], _marco(publicado))

    destinatario = DestinatarioDoAviso.objects.get(aviso_id=declarado["aviso"], inscricao=sem)
    assert destinatario.endereco == ""
    assert (
        declarado["destinatarios"]
        == DestinatarioDoAviso.objects.filter(aviso_id=declarado["aviso"])
        .exclude(endereco="")
        .count()
    )


def test_a_confirmacao_nao_envia_nada(publicado):
    """`FR-1265`: nenhuma mensagem sai na requisição; quem envia é o despacho."""
    mail.outbox.clear()

    avisar_resultado(publicado["edital"], _marco(publicado))

    assert mail.outbox == []


def test_publicar_nao_dispara_aviso(publicado):
    """`FR-1243`: publicar não envia nada, e nenhum aviso nasce sozinho."""
    assert Aviso.objects.count() == 0
    assert mail.outbox == []


def test_avisada_a_publicacao_nao_ha_publicacao_nova(publicado):
    """`FR-1262`: avisar de novo sem justificativa é recusado."""
    edital = publicado["edital"]
    avisar_resultado(edital, _marco(publicado), chave="primeiro")

    with pytest.raises(DomainError) as erro:
        avisar_resultado(edital, _marco(publicado), chave="segundo")

    assert erro.value.code == nomes.AVISO_SEM_PUBLICACAO_NOVA
    assert destinatarios.naturezas_pendentes(edital=edital, marco_id=_marco(publicado)) == []


def test_com_justificativa_e_reenvio_ligado_ao_anterior(publicado):
    edital = publicado["edital"]
    primeiro = avisar_resultado(edital, _marco(publicado), chave="primeiro")

    segundo = avisar_resultado(
        edital,
        _marco(publicado),
        chave="segundo",
        justificativa="O primeiro saiu com o modelo errado.",
    )

    aviso = Aviso.objects.get(pk=segundo["aviso"])
    assert aviso.motivo == nomes.REENVIO_JUSTIFICADO
    assert str(aviso.aviso_anterior_id) == primeiro["aviso"]
    assert aviso.justificativa == "O primeiro saiu com o modelo errado."


def test_o_duplo_clique_devolve_o_mesmo_aviso(publicado):
    """`FR-1263`: a mesma confirmação repetida não cria outro aviso."""
    from processo_seletivo.avisos.application import previa

    edital = publicado["edital"]
    # O mesmo formulário enviado duas vezes: a assinatura é a da prévia que o operador viu.
    assinatura = previa.assinatura(
        destinatarios.universo_do_resultado(
            edital=edital, marco_id=_marco(publicado), natureza=nomes.PRELIMINAR
        )
    )

    primeiro = avisar_resultado(edital, _marco(publicado), chave="mesma", assinatura=assinatura)
    segundo = avisar_resultado(edital, _marco(publicado), chave="mesma", assinatura=assinatura)

    assert primeiro == segundo
    assert Aviso.objects.count() == 1


def test_previa_defasada_e_recusada(publicado):
    """`FR-1259`: a lista que o operador viu não é a que seria enviada."""
    with pytest.raises(DomainError) as erro:
        avisar_resultado(publicado["edital"], _marco(publicado), assinatura="outra")

    assert erro.value.code == nomes.AVISO_PREVIA_DEFASADA
    assert Aviso.objects.count() == 0


def test_variavel_sem_valor_na_origem_recusa(publicado):
    with pytest.raises(DomainError) as erro:
        avisar_resultado(
            publicado["edital"], _marco(publicado), corpo="Veja {referencia_da_publicacao}."
        )

    assert erro.value.code == nomes.AVISO_VARIAVEL_SEM_VALOR


def test_o_texto_congelado_tem_o_link_da_publicacao_e_o_rodape(publicado):
    """Uma publicação só: o rodapé aponta o endereço dela (`R-008`)."""
    declarado = avisar_resultado(publicado["edital"], _marco(publicado))

    aviso = Aviso.objects.get(pk=declarado["aviso"])
    assert f"/selecoes/resultados/{publicado['publicacao'].id}/" in aviso.corpo
    assert "Este aviso não substitui a publicação." in aviso.corpo
    assert "{nome_do_candidato}" in aviso.corpo
    assert PublicacaoDoAviso.objects.filter(aviso=aviso).count() == 1


def test_a_trilha_nao_copia_os_enderecos(publicado):
    """`FR-1278`: a trilha diz o que foi decidido, e não para quem."""
    from processo_seletivo.auditoria.models import RegistroAuditoria

    avisar_resultado(publicado["edital"], _marco(publicado))

    registro = RegistroAuditoria.objects.get(operation=nomes.OPERACAO_CONFIRMAR)
    assert "@" not in registro.reason
