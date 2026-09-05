"""A leitura monta o universo uma vez e entrega dados puros ao motor (015, T082)."""

import re
import threading
from unittest.mock import patch

import pytest
from django.db import connection, connections
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.emissao import (
    EMITIR,
    assinatura_da_proposta,
    emitir_ordem,
)
from processo_seletivo.classificacao.application.reproducao import (
    divergencias_da_reproducao,
    reproduzir_ato,
)
from processo_seletivo.classificacao.application.selectors import ato_vigente, estado_do_marco
from processo_seletivo.classificacao.models import AtoDeOrdenacao, PosicaoNaOrdem
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.comissao import alocar_em, constituir, inscrever, rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.publicacao import publish_original, retify
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

MARCO = "00000000-0000-4000-8000-000000000451"


def _confirmacao(edital, *, vigente=None):
    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    return assinatura_da_proposta(proposta, ato_vigente=vigente)


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    rascunho = rascunho_com_etapas(avaliacoes=1, maxima="100.0000", minima="60.0000")
    etapa = rascunho["stages"][1]
    etapa["weight"] = "1.0000"
    rascunho["profiles"][0]["classificationMilestones"] = [
        {
            "id": MARCO,
            "code": "FINAL",
            "name": "Classificação final",
            "stages": [etapa["id"]],
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": [],
        }
    ]
    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho,
    )
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo="calculo-015",
    )
    alocar_em(gestor, edital.processo, membros["joao"], edital, etapa["id"])
    contexto = {
        "edital": edital,
        "processo": edital.processo,
        "membros": membros,
        "etapa": etapa["id"],
    }
    inscricoes = inscrever(edital, 3, primeiro=501)
    distribuir_para(contexto, gestor, ["joao"], inscricoes[:2], chave="calculo-015-lote")
    concluir_como(contexto, "joao", inscricoes[0], pontuacao="70.0000")
    concluir_como(contexto, "joao", inscricoes[1], pontuacao="90.0000")
    consolidar(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa["id"],
        inscricao_ids=[item.id for item in inscricoes[:2]],
        idempotency_key="calculo-015-consolidar",
        correlation_id="teste-calculo-015",
    )
    return edital, etapa, inscricoes


def test_calcula_a_ordem_e_nomeia_quem_nao_tem_pontuacao(cenario):
    edital, etapa, inscricoes = cenario

    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)

    assert [item["inscricao_id"] for item in proposta["posicoes"]] == [
        str(inscricoes[1].id),
        str(inscricoes[0].id),
    ]
    assert [item["pontuacao"] for item in proposta["posicoes"]] == [90, 70]
    assert proposta["sem_posicao"][0]["inscricao_id"] == str(inscricoes[2].id)
    assert etapa["name"] in proposta["sem_posicao"][0]["motivo"]
    assert len(proposta["universo"]["participants"]) == 3
    assert len(proposta["universo"]["stageResults"]) == 2


def test_emite_um_ato_com_tres_posicoes_e_uma_unica_auditoria(cenario, gestor):
    edital, _, _ = cenario
    confirmacao = _confirmacao(edital)

    desfecho = emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="emitir-ordem-015",
        correlation_id="teste-emissao-015",
        confirmacao_do_calculo=confirmacao,
    )

    ato = AtoDeOrdenacao.objects.get()
    assert desfecho["ids"] == [str(ato.id)]
    assert PosicaoNaOrdem.objects.filter(ato=ato).count() == 3
    assert (
        RegistroAuditoria.objects.filter(
            operation=EMITIR,
            aggregate_type="AtoDeOrdenacao",
            aggregate_id=ato.id,
        ).count()
        == 1
    )

    repetido = emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="emitir-ordem-015",
        correlation_id="outra-correlacao",
        confirmacao_do_calculo=confirmacao,
    )

    assert repetido == desfecho
    assert AtoDeOrdenacao.objects.count() == 1
    assert PosicaoNaOrdem.objects.count() == 3
    assert RegistroAuditoria.objects.filter(operation=EMITIR).count() == 1


def test_abrir_a_tela_calcula_sem_gravar(cenario, client, seletor_ligado):
    edital, _, _ = cenario
    identificar(client, "maria", ["gestor"])
    atos_antes = AtoDeOrdenacao.objects.count()
    posicoes_antes = PosicaoNaOrdem.objects.count()
    eventos_antes = RegistroAuditoria.objects.count()

    resposta = client.get(reverse("interface:ordenacao", args=[edital.id, MARCO]))

    assert resposta.status_code == 200
    assert AtoDeOrdenacao.objects.count() == atos_antes
    assert PosicaoNaOrdem.objects.count() == posicoes_antes
    assert RegistroAuditoria.objects.count() == eventos_antes
    assert "no-store" in resposta.headers["Cache-Control"]
    assert "private" in resposta.headers["Cache-Control"]
    corpo = resposta.content.decode()
    assert 'name="posicao"' not in corpo
    assert 'name="pontuacao"' not in corpo
    assert 'name="desempate"' not in corpo


def test_a_presidencia_emite_por_post_e_volta_para_a_consulta(
    cenario,
    client,
    seletor_ligado,
):
    edital, _, _ = cenario
    identificar(client, "maria", ["gestor"])
    pagina = client.get(reverse("interface:ordenacao", args=[edital.id, MARCO]))
    corpo = pagina.content.decode()
    confirmacao = re.search(
        r'name="confirmacao_do_calculo" value="([^"]+)"',
        corpo,
    ).group(1)

    resposta = client.post(
        reverse("interface:emitir-ordenacao", args=[edital.id, MARCO]),
        {
            "chave_idempotencia": "interface-emissao-015",
            "confirmacao_do_calculo": confirmacao,
        },
    )

    assert resposta.status_code == 302
    assert resposta.url == reverse("interface:ordenacao", args=[edital.id, MARCO])
    assert AtoDeOrdenacao.objects.count() == 1
    destino = client.get(resposta.url)
    assert "Ordem emitida" in destino.content.decode()


def test_eliminada_na_etapa_permanece_no_universo_sem_posicao(cenario, gestor):
    edital, etapa, inscricoes = cenario
    registrar_ocorrencia(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa["id"],
        inscricao_ids=[inscricoes[2].id],
        motivo="Não compareceu à Etapa.",
        idempotency_key="ocorrencia-ordem-015",
        correlation_id="teste-ocorrencia-ordem",
    )

    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="emitir-com-eliminada-015",
        correlation_id="teste-emissao-eliminada",
        confirmacao_do_calculo=_confirmacao(edital),
    )

    linhas = list(PosicaoNaOrdem.objects.order_by("posicao", "id"))
    eliminada = next(item for item in linhas if item.inscricao_id == inscricoes[2].id)
    assert len(linhas) == len(AtoDeOrdenacao.objects.get().universo["participants"]) == 3
    assert eliminada.posicao is None
    assert eliminada.consequencia == "ELIMINADA"
    assert eliminada.motivo == "Não compareceu à Etapa."


def test_a_tela_nomeia_o_grupo_empatado(cenario, client, seletor_ligado):
    edital, _, _ = cenario
    identificar(client, "maria", ["gestor"])
    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    empatadas = [{**item, "posicao": 1, "empate_residual": True} for item in proposta["posicoes"]]
    proposta = {**proposta, "posicoes": empatadas}

    with patch(
        "processo_seletivo.classificacao.application.selectors.calcular_ordem",
        return_value=proposta,
    ):
        corpo = client.get(reverse("interface:ordenacao", args=[edital.id, MARCO])).content.decode()

    assert corpo.count("Empate residual") == len(empatadas)
    assert corpo.count('class="grupo-empatado"') == len(empatadas)


def test_duas_emissoes_concorrentes_produzem_um_ato_e_uma_recusa(cenario, gestor):
    if connection.vendor != "postgresql":
        pytest.skip("concorrência validada somente no PostgreSQL")
    edital, _, _ = cenario
    partida = threading.Barrier(2, timeout=10)
    desfechos = {}
    confirmacao = _confirmacao(edital)

    def emitir(nome):
        try:
            partida.wait()
            emitir_ordem(
                actor=gestor,
                processo_id=edital.processo_id,
                edital_id=edital.id,
                perfil_id=PROFILE_ID,
                marco_id=MARCO,
                idempotency_key=f"emissao-concorrente-{nome}",
                correlation_id=f"teste-concorrente-{nome}",
                confirmacao_do_calculo=confirmacao,
            )
            desfechos[nome] = "emitida"
        except DomainError as recusa:
            desfechos[nome] = (recusa.status, recusa.code)
        finally:
            connections.close_all()

    fios = [threading.Thread(target=emitir, args=(nome,)) for nome in ("a", "b")]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join(timeout=20)

    assert not any(fio.is_alive() for fio in fios), desfechos
    assert sorted(desfechos.values(), key=str) == [
        (409, "ordering_act_already_exists"),
        "emitida",
    ]
    assert AtoDeOrdenacao.objects.count() == 1
    assert PosicaoNaOrdem.objects.count() == 3
    assert RegistroAuditoria.objects.filter(operation=EMITIR).count() == 1


def _emitir_cenario(cenario, gestor, *, chave="ato-para-obsolescencia"):
    edital, _, _ = cenario
    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key=chave,
        correlation_id="teste-obsolescencia",
        confirmacao_do_calculo=_confirmacao(edital),
    )
    return AtoDeOrdenacao.objects.get()


def test_retificacao_da_regra_obsoleta_sem_resultado_novo(cenario, gestor, api_client):
    edital, _, _ = cenario
    ato = _emitir_cenario(cenario, gestor)
    retify(
        api_client,
        edital,
        [
            {
                "targetPath": (
                    f"/profiles/id={PROFILE_ID}/classificationMilestones/id={MARCO}/operation"
                ),
                "operation": "REPLACE",
                "newValue": "MEDIA_PONDERADA",
            }
        ],
        suffix="regra-015",
    )

    estado = estado_do_marco(edital=edital, marco_id=MARCO)

    assert estado["vigente"] == ato
    assert estado["obsoleto"] is True
    assert estado["recomputavel"] is True
    assert [item["tipo"] for item in estado["divergencias"]] == ["regra_alterada"]


def test_resultado_tardio_do_universo_obsoleta_e_nao_substitui_o_vigente(cenario, gestor):
    edital, etapa, inscricoes = cenario
    ato = _emitir_cenario(cenario, gestor)
    registrar_ocorrencia(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa["id"],
        inscricao_ids=[inscricoes[2].id],
        motivo="Não compareceu à Etapa.",
        idempotency_key="resultado-tardio-015",
        correlation_id="teste-resultado-tardio",
    )

    estado = estado_do_marco(edital=edital, marco_id=MARCO)

    assert estado["obsoleto"] is True
    assert "resultados_alterados" in {item["tipo"] for item in estado["divergencias"]}
    assert ato_vigente(edital=edital, marco_id=MARCO) == ato
    assert AtoDeOrdenacao.objects.count() == 1


def test_marco_removido_fica_obsoleto_nao_recomputavel_e_integro(cenario, gestor, api_client):
    edital, _, _ = cenario
    ato = _emitir_cenario(cenario, gestor)
    universo = ato.universo.copy()
    retify(
        api_client,
        edital,
        [
            {
                "targetPath": (f"/profiles/id={PROFILE_ID}/classificationMilestones/id={MARCO}"),
                "operation": "REMOVE",
            }
        ],
        suffix="remove-marco-015",
    )

    estado = estado_do_marco(edital=edital, marco_id=MARCO)
    ato.refresh_from_db()

    assert estado["vigente"] == ato
    assert estado["obsoleto"] is True
    assert estado["recomputavel"] is False
    assert estado["proposta"] is None
    assert ato.universo == universo
    assert PosicaoNaOrdem.objects.filter(ato=ato).count() == 3


def test_resultado_fora_do_perfil_nao_obsoleta_o_ato(cenario, gestor):
    from uuid import uuid4

    from django.utils import timezone

    from processo_seletivo.inscricoes.models import Inscricao
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
    from processo_seletivo.resultados.models import ResultadoEtapa

    edital, etapa, _ = cenario
    ato = _emitir_cenario(cenario, gestor)
    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    agora = timezone.now()
    alheia = Inscricao.objects.create(
        identity_subject="cpf:fora-do-perfil",
        edital=edital,
        profile_id=uuid4(),
        nome="Participante de outro Perfil",
        cpf="111.444.777-35",
        cpf_normalizado="11144477735",
        email="fora@example.test",
        created_at=agora,
    )
    Inscricao.objects.filter(pk=alheia.pk).update(
        status=Inscricao.Status.SUBMETIDA,
        protocolo="0999",
        submitted_at=agora,
        versao_aceita=versao,
        declaracoes_aceitas_em=agora,
    )
    alheia.refresh_from_db()
    ResultadoEtapa.objects.create(
        inscricao=alheia,
        edital=edital,
        etapa_id=etapa["id"],
        origem=ResultadoEtapa.Origem.OCORRENCIA,
        avaliacao=None,
        versao=versao,
        forma="",
        pontuacao=None,
        sentido="",
        consequencia=ResultadoEtapa.Consequencia.ELIMINADA,
        motivo="Ocorrência fora do Perfil do marco.",
        consolidado_em=agora,
        consolidado_por=gestor.subject,
    )

    estado = estado_do_marco(edital=edital, marco_id=MARCO)

    assert estado["vigente"] == ato
    assert estado["obsoleto"] is False
    assert estado["divergencias"] == []


def test_reproduz_o_ato_sem_consultar_o_estado_vigente(cenario, gestor, api_client):
    edital, _, _ = cenario
    ato = _emitir_cenario(cenario, gestor)
    retify(
        api_client,
        edital,
        [
            {
                "targetPath": (f"/profiles/id={PROFILE_ID}/classificationMilestones/id={MARCO}"),
                "operation": "REMOVE",
            }
        ],
        suffix="reproduzir-sem-vigente-015",
    )

    reproduzido = reproduzir_ato(ato)

    assert divergencias_da_reproducao(ato, reproduzido=reproduzido) == []
    assert [item["posicao"] for item in reproduzido["posicoes"]] == [1, 2]
    assert len(reproduzido["sem_posicao"]) == 1


def test_mudanca_silenciosa_na_reproducao_e_detectavel(cenario, gestor):
    ato = _emitir_cenario(cenario, gestor)
    reproduzido = reproduzir_ato(ato)
    alterado = {
        **reproduzido,
        "posicoes": [{**item, "posicao": item["posicao"] + 1} for item in reproduzido["posicoes"]],
    }

    divergencias = divergencias_da_reproducao(ato, reproduzido=alterado)

    assert {item["inscricao_id"] for item in divergencias} == {
        item["inscricao_id"] for item in reproduzido["posicoes"]
    }


def test_consulta_nomeia_o_criterio_e_os_valores_que_separaram_vizinhas(
    cenario,
    client,
    seletor_ligado,
):
    from django.utils import timezone

    edital, _, inscricoes = cenario
    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    ato = AtoDeOrdenacao.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        versao=proposta["versao"],
        universo=proposta["universo"],
        emitido_por="maria",
        emitido_em=timezone.now(),
    )
    criterio = "00000000-0000-4000-8000-000000000499"
    PosicaoNaOrdem.objects.bulk_create(
        [
            PosicaoNaOrdem(
                ato=ato,
                inscricao=inscricoes[indice],
                posicao=indice + 1,
                pontuacao_combinada=80,
                consequencia="HABILITADA",
                motivo="",
                desempate=[
                    {
                        "criterionId": criterio,
                        "order": 1,
                        "type": "MAIOR_VALOR_DE_FATO",
                        "value": valor,
                        "separated": True,
                    }
                ],
            )
            for indice, valor in enumerate((42, 0))
        ]
        + [
            PosicaoNaOrdem(
                ato=ato,
                inscricao=inscricoes[2],
                posicao=None,
                pontuacao_combinada=None,
                consequencia="",
                motivo="Sem pontuação.",
                desempate=[],
            )
        ]
    )
    identificar(client, "iris", ["auditor"])

    corpo = client.get(
        reverse("interface:ato-de-ordenacao", args=[edital.id, MARCO, ato.id])
    ).content.decode()

    assert corpo.count("Critério que separou") == 2
    assert "MAIOR_VALOR_DE_FATO" in corpo
    assert "valor 42" in corpo
    assert "valor 0" in corpo
    assert "valor ausente" not in corpo


def test_sucessao_cria_linha_nova_e_preserva_o_ato_anterior(cenario, gestor):
    edital, etapa, inscricoes = cenario
    anterior = _emitir_cenario(cenario, gestor)
    congelado = {
        "universo": anterior.universo.copy(),
        "emitido_por": anterior.emitido_por,
        "emitido_em": anterior.emitido_em,
    }
    registrar_ocorrencia(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa["id"],
        inscricao_ids=[inscricoes[2].id],
        motivo="Resultado tardio constatado.",
        idempotency_key="resultado-para-sucessao-015",
        correlation_id="teste-sucessao",
    )
    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    confirmacao = assinatura_da_proposta(proposta, ato_vigente=anterior)

    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="sucessor-015",
        correlation_id="teste-sucessao",
        confirmacao_do_calculo=confirmacao,
        motivo="Incluir Resultado tardio.",
    )

    sucessor = ato_vigente(edital=edital, marco_id=MARCO)
    anterior.refresh_from_db()
    assert AtoDeOrdenacao.objects.count() == 2
    assert sucessor.ato_anterior == anterior
    assert sucessor.motivo_da_sucessao == "Incluir Resultado tardio."
    assert anterior.ato_anterior is None
    assert anterior.universo == congelado["universo"]
    assert anterior.emitido_por == congelado["emitido_por"]
    assert anterior.emitido_em == congelado["emitido_em"]


def test_sucessao_recusa_confirmacao_anterior_ao_vigente(cenario, gestor):
    edital, etapa, inscricoes = cenario
    primeiro = _emitir_cenario(cenario, gestor)
    registrar_ocorrencia(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa["id"],
        inscricao_ids=[inscricoes[2].id],
        motivo="Resultado tardio constatado.",
        idempotency_key="resultado-para-corrida-sucessao-015",
        correlation_id="teste-sucessao-obsoleta",
    )
    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    confirmacao_antiga = assinatura_da_proposta(proposta, ato_vigente=primeiro)
    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="segundo-ato-015",
        correlation_id="teste-sucessao-obsoleta",
        confirmacao_do_calculo=confirmacao_antiga,
        motivo="Incluir Resultado tardio.",
    )

    with pytest.raises(DomainError) as erro:
        emitir_ordem(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            idempotency_key="terceiro-ato-obsoleto-015",
            correlation_id="teste-sucessao-obsoleta",
            confirmacao_do_calculo=confirmacao_antiga,
            motivo="Tentativa baseada na leitura anterior.",
        )

    assert (erro.value.status, erro.value.code) == (409, "ordering_act_already_exists")
    assert AtoDeOrdenacao.objects.count() == 2


def test_tela_mostra_a_cadeia_e_o_motivo_da_sucessao(
    cenario,
    gestor,
    client,
    seletor_ligado,
):
    edital, etapa, inscricoes = cenario
    primeiro = _emitir_cenario(cenario, gestor)
    registrar_ocorrencia(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa["id"],
        inscricao_ids=[inscricoes[2].id],
        motivo="Resultado tardio constatado.",
        idempotency_key="resultado-para-historico-015",
        correlation_id="teste-historico",
    )
    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    motivo = "Resultado tardio incluído na ordem."
    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="sucessor-historico-015",
        correlation_id="teste-historico",
        confirmacao_do_calculo=assinatura_da_proposta(proposta, ato_vigente=primeiro),
        motivo=motivo,
    )
    identificar(client, "iris", ["auditor"])

    corpo = client.get(reverse("interface:ordenacao", args=[edital.id, MARCO])).content.decode()

    assert corpo.count("Ato de classificação") == 0
    assert "Histórico de atos" in corpo
    assert str(primeiro.id) in corpo
    assert motivo in corpo
