"""O aviso do passo de uma Etapa restrita (168, US2; FR-7315 a FR-7320; SC-2412).

O Edital é o da `166` sem o vídeo: a Etapa restrita a `PPI`, colegiada, com período. O aviso é o da
`066` com outra origem — prévia, gesto, despacho —, e o texto nunca diz a lista de ninguém.
"""

from datetime import timedelta

import pytest
from django.core import mail
from django.db import IntegrityError, transaction
from django.utils import timezone

from processo_seletivo.avisos.application import destinatarios
from processo_seletivo.avisos.application.despacho import despachar
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.models import Aviso
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.avisos import avisar_passo
from tests.fixtures.comissao import inscrever
from tests.fixtures.deliberacao import (
    concluir_pareceres,
    consolidar_na,
    distribuir_na_hetero,
    montar_colegiada,
)
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.verificacao import rascunho_com_video

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    agora = timezone.now()
    cenario = montar_colegiada(
        gestor,
        api_client,
        manager_headers,
        seed=6810,
        regra="UNANIMOUS_FOR_FAVORABLE",
        quantas=3,
        rascunho=rascunho_com_video(
            6810, inicio=agora + timedelta(days=2), fim=agora + timedelta(days=5), video=False
        ),
    )
    # Pedro, só na ampla: a Etapa não o alcança, e o aviso não o vê.
    (cenario["pedro"],) = inscrever(cenario["edital"], 1, primeiro=90, perfil=cenario["perfil"])
    return cenario


def _universo(cenario, **opcoes):
    return destinatarios.universo_do_passo(
        edital=cenario["edital"], etapa_id=cenario["hetero"], **opcoes
    )


def test_o_universo_e_quem_participa_sem_resultado(cenario, gestor):
    """FR-7318: os alcançados que participam e não têm Resultado; a ampla fica fora."""
    maria, joao, ana = cenario["inscricoes"]
    distribuir_na_hetero(cenario, gestor, [ana], chave="hetero-6810")
    concluir_pareceres(cenario, ana, {n: "FAVORAVEL" for n in ("ana", "bruno", "carla")})
    consolidar_na(cenario, cenario["hetero"], [ana], chave="consolidar-6810")
    universo = _universo(cenario)
    assert {linha.inscricao.id for linha in universo.linhas} == {maria.id, joao.id}
    assert universo.origem == nomes.PASSO
    assert universo.marco_id is None and universo.perfil_id is None


def test_um_aviso_cita_a_etapa_e_o_email_nao_diz_a_lista(cenario, settings):
    """FR-7315, FR-7319, SC-2412: o e-mail diz a etapa e o período, e nunca a Modalidade."""
    declarado = avisar_passo(cenario["edital"], cenario["hetero"])
    aviso = Aviso.objects.get(pk=declarado["aviso"])
    assert aviso.origem == nomes.PASSO
    assert str(aviso.etapa_id) == str(cenario["hetero"])
    assert aviso.marco_id is None
    assert declarado["destinatarios"] == 3
    assert mail.outbox == []  # a confirmação não envia nada (FR-1265 da `066`)
    despachar()
    assert len(mail.outbox) == 3
    for mensagem in mail.outbox:
        texto = f"{mensagem.subject} {mensagem.body}".lower()
        assert "heteroidentificação" in texto  # o nome publicado da Etapa, na fixture
        assert "de " in texto and "/20" in texto  # o período
        for proibido in ("pretos e pardos", "ppi", "cota", "reserva", "modalidade", "lista"):
            assert proibido not in texto, proibido


def test_o_primeiro_aviso_nao_repete_quem_ja_foi_avisado(cenario, gestor):
    """FR-7318: o segundo gesto sem justificativa só alcança quem o primeiro não viu."""
    avisar_passo(cenario["edital"], cenario["hetero"])
    assert _universo(cenario).linhas == []
    assert _universo(cenario).ja_avisado
    with pytest.raises(DomainError) as recusa:
        avisar_passo(cenario["edital"], cenario["hetero"], chave="de-novo")
    assert recusa.value.code == nomes.AVISO_SEM_PUBLICACAO_NOVA
    (novo,) = inscrever(
        cenario["edital"],
        1,
        primeiro=95,
        perfil=cenario["perfil"],
        modalidades=cenario["inscricoes"][0].modality_id,
    )
    # Ainda não participa: a Análise, anterior, não a consolidou.
    assert _universo(cenario).linhas == []
    distribuir_para(cenario, gestor, ["joao"], [novo], chave="analise-6810-novo")
    concluir_como(cenario, "joao", novo, pontuacao="80")
    consolidar_na(cenario, cenario["analise"], [novo], chave="consolidar-analise-6810-novo")
    assert {linha.inscricao.id for linha in _universo(cenario).linhas} == {novo.id}


def test_o_reenvio_justificado_alcanca_todos_e_aponta_o_anterior(cenario):
    primeiro = avisar_passo(cenario["edital"], cenario["hetero"])
    segundo = avisar_passo(
        cenario["edital"], cenario["hetero"], chave="reenvio", justificativa="Datas corrigidas."
    )
    aviso = Aviso.objects.get(pk=segundo["aviso"])
    assert aviso.motivo == nomes.REENVIO_JUSTIFICADO
    assert str(aviso.aviso_anterior_id) == primeiro["aviso"]
    assert segundo["destinatarios"] == 3


def test_a_etapa_que_nao_e_restrita_nao_tem_passo(cenario):
    with pytest.raises(DomainError) as recusa:
        destinatarios.universo_do_passo(edital=cenario["edital"], etapa_id=cenario["analise"])
    assert recusa.value.status == 404


def test_a_chave_dos_avisos_desligada_recusa(cenario, settings):
    """FR-7317: a mesma recusa dos outros avisos."""
    settings.AVISOS_AOS_CANDIDATOS = False
    with pytest.raises(DomainError) as recusa:
        avisar_passo(cenario["edital"], cenario["hetero"])
    assert recusa.value.code == nomes.AVISO_ENVIO_DESABILITADO


def test_o_banco_exige_a_etapa_no_passo_e_o_marco_nas_outras(cenario):
    """T-004: o CHECK da origem, como camada independente da aplicação."""
    declarado = avisar_passo(cenario["edital"], cenario["hetero"])
    base = Aviso.objects.get(pk=declarado["aviso"])
    campos = {
        f.attname: getattr(base, f.attname)
        for f in Aviso._meta.concrete_fields
        if f.attname != "id"
    }
    for errado in (
        {"etapa_id": None},
        {"marco_id": cenario["hetero"]},
        {"origem": nomes.RESULTADO, "natureza": nomes.PRELIMINAR},
    ):
        with pytest.raises(IntegrityError), transaction.atomic():
            Aviso.objects.bulk_create([Aviso(**{**campos, **errado, "idempotency_key": "x"})])


def test_a_unidade_que_ja_tem_os_tres_ganha_o_do_passo_uma_vez():
    """FR-7320, T-005: a marca própria cria o quarto também onde os três já existem."""
    from processo_seletivo.avisos.application.modelos import garantir_modelos_iniciais
    from processo_seletivo.avisos.models import ModeloDeAviso

    garantir_modelos_iniciais()
    ModeloDeAviso.objects.filter(chave_inicial=nomes.CHAVE_DO_MODELO_DO_PASSO).update(
        chave_inicial="", modelo_inicial=False, nome="Desfeito pelo teste"
    )
    # A unidade como era antes desta spec: os três, e nenhum do passo.
    assert garantir_modelos_iniciais() == 1
    assert garantir_modelos_iniciais() == 0
    do_passo = ModeloDeAviso.objects.get(chave_inicial=nomes.CHAVE_DO_MODELO_DO_PASSO)
    for proibido in ("ppi", "cota", "reserva", "modalidade", "lista", "heteroidentifica"):
        assert proibido not in f"{do_passo.assunto} {do_passo.corpo}".lower()


def test_a_previa_pela_tela_usa_o_modelo_do_passo(cenario, client, seletor_ligado):
    """US2, cenário 1: a prévia lista só os que participam, com o modelo do passo por padrão."""
    from django.urls import reverse

    from processo_seletivo.avisos.application.modelos import garantir_modelos_iniciais
    from tests.interface.conftest import identificar

    garantir_modelos_iniciais()
    identificar(client, "publicadora", ["publicador"])
    url = reverse("interface:aviso-do-passo", args=[cenario["edital"].id, cenario["hetero"]])
    corpo = client.get(url).content.decode()
    assert "participam da etapa" in corpo
    assert "Há um passo a mais para você" in corpo
    assert cenario["pedro"].protocolo not in corpo
    for inscricao in cenario["inscricoes"]:
        assert inscricao.protocolo in corpo
