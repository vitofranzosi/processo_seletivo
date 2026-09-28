"""O gesto de aplicar aos demais Perfis, pela tela do assistente (051, US1 e US2).

Três famílias, na ordem em que o risco aparece:

- **a prévia não grava** — é o invariante da Constituição 1.2.0: o alcance aparece antes, e nada
  muda até a confirmação;
- **a confirmação grava exatamente o que a prévia mostrou** — pelo caminho da etapa, com o registro
  do gesto na trilha, e recusando quando o que estava na tela mudou;
- **o que não pode mudar** — o Perfil excluído, o Perfil fora do alcance, o Edital de um Perfil só.
"""

import html
import re

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.editais.models.perfis import MarcoClassificatorio, PerfilVaga
from tests.interface.conftest import ETAPA_CLASSIFICATORIA, identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

P1 = "aaaaaaaa-0000-4000-8000-000000051a01"
P2 = "aaaaaaaa-0000-4000-8000-000000051a02"
P3 = "aaaaaaaa-0000-4000-8000-000000051a03"
FATO = {P1: "aaaaaaaa-0000-4000-8000-000000051f01", P2: "aaaaaaaa-0000-4000-8000-000000051f02"}
MARCO = "aaaaaaaa-0000-4000-8000-000000051b01"
CODIGOS = {P1: "LP01", P2: "LP02", P3: "LP03"}


def _perfis_no_formulario(**extra):
    dados = {}
    for posicao, perfil in enumerate((P1, P2, P3)):
        base = f"perfil-{posicao}"
        dados.update(
            {
                f"{base}-id": perfil,
                f"{base}-code": CODIGOS[perfil],
                f"{base}-name": "Professor",
                f"{base}-immediateVacancies": "2",
                f"{base}-reserveType": "NONE",
            }
        )
        # O LP03 não declara o fato que o desempate compara: é o destino fora do alcance.
        if perfil in FATO:
            dados.update(
                {
                    f"fato-{posicao}-0-id": FATO[perfil],
                    f"fato-{posicao}-0-code": "EXPERIENCIA",
                    f"fato-{posicao}-0-label": "Meses de experiência",
                    f"fato-{posicao}-0-type": "INTEIRO",
                }
            )
    dados.update(extra)
    return dados


def _marco_do_lp01(**extra):
    base = f"marco-{P1}-0"
    return {
        f"{base}-id": MARCO,
        f"{base}-code": "LP01",
        f"{base}-name": "Classificação final — Professor",
        f"{base}-orderProduction": "POR_PONTUACAO",
        f"{base}-stages": [ETAPA_CLASSIFICATORIA],
        f"{base}-operation": "MEDIA_PONDERADA",
        f"{base}-normalization": "NENHUMA",
        f"{base}-scale": "2",
        f"{base}-mode": "MEIO_PARA_CIMA",
        f"{base}-appealDeclaration": "admite",
        f"{base}-appealDurationDays": "2",
        f"{base}-cutTargetKind": "FROM_VACANCY_TABLE",
        f"{base}-cutSurplusCount": "0",
        f"{base}-cutTieOutcome": "STRICT",
        f"{base}-cutGovernedStage": "NONE",
        f"{base}-cutContinuation": "ALLOWED",
        f"criterio-{P1}-0-0-id": "aaaaaaaa-0000-4000-8000-000000051c01",
        f"criterio-{P1}-0-0-order": "1",
        f"criterio-{P1}-0-0-type": "MAIOR_VALOR_DE_FATO",
        f"criterio-{P1}-0-0-target": FATO[P1],
        f"criterio-{P1}-0-0-whenMissing": "ULTIMO_NO_CRITERIO",
        **extra,
    }


def _classificacao(**extra):
    return {"perfil_id": [P1, P2, P3], **_marco_do_lp01(), **extra}


def _url(edital, etapa="classificacao"):
    return reverse("interface:compor-etapa", args=[edital.id, etapa])


@pytest.fixture
def tres_perfis(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(_url(edital, "perfis"), _perfis_no_formulario())
    assert resposta.status_code == 302, resposta.content
    edital.refresh_from_db()
    resposta = client.post(
        _url(edital, "etapas"),
        {
            "etapa-0-id": ETAPA_CLASSIFICATORIA,
            "etapa-0-name": "Prova de títulos",
            "etapa-0-order": "1",
            "etapa-0-weight": "1",
            "etapa-0-classificatory": "on",
        },
    )
    assert resposta.status_code == 302, resposta.content
    edital.refresh_from_db()
    return edital


def _impressao(corpo):
    return re.search(r'name="aplicar_impressao" value="([0-9a-f]+)"', corpo).group(1)


def _texto(resposta):
    return html.unescape(resposta.content.decode())


def test_a_previa_declara_cada_perfil_e_nao_grava_nada(client, tres_perfis):
    resposta = client.post(_url(tres_perfis), _classificacao(aplicar=f"marco:{P1}:0"))

    assert resposta.status_code == 200
    corpo = _texto(resposta)
    assert "Aplicar o marco aos demais Perfis" in corpo
    assert "1 nasce, 1 fica fora do alcance" in corpo
    assert "LP02 — Professor" in corpo
    assert "não declara o fato EXPERIENCIA" in corpo
    # O código que o marco terá no destino é dito antes de ele existir.
    assert 'Código: <span class="antes">—</span> → <span class="depois">LP02</span>' in (
        resposta.content.decode()
    )
    assert not MarcoClassificatorio.objects.filter(perfil__edital=tres_perfis).exists()
    # O que estava digitado continua na tela.
    assert f'name="marco-{P1}-0-id" value="{MARCO}"' in resposta.content.decode()


def test_a_confirmacao_grava_o_marco_no_destino_e_registra_o_gesto(client, tres_perfis):
    previa = client.post(_url(tres_perfis), _classificacao(aplicar=f"marco:{P1}:0"))

    resposta = client.post(
        _url(tres_perfis),
        _classificacao(
            confirmar_aplicacao=f"marco:{P1}:0",
            aplicar_destino=[P2],
            aplicar_impressao=_impressao(previa.content.decode()),
        ),
    )

    assert resposta.status_code == 302, resposta.content
    assert "aplicado=1" in resposta["Location"]
    marco = MarcoClassificatorio.objects.get(perfil_id=P2)
    assert marco.code == "LP02"
    assert marco.name == "Classificação final — Professor"
    (criterio,) = marco.criterios.all()
    assert criterio.parametros == {"factId": FATO[P2]}
    assert not MarcoClassificatorio.objects.filter(perfil_id=P3).exists()
    # A origem foi gravada junto: é a mesma gravação da etapa.
    assert MarcoClassificatorio.objects.filter(perfil_id=P1, pk=MARCO).exists()
    registro = RegistroAuditoria.objects.get(operation="APLICAR_A_TODOS")
    assert registro.detalhe["unidade"] == "marco"
    assert registro.detalhe["origem"]["codigo"] == "LP01"
    assert [item["codigo"] for item in registro.detalhe["destinos"]] == ["LP02"]
    assert "LP01" in registro.reason


def test_a_confirmacao_sobre_tela_que_mudou_e_recusada_sem_gravar(client, tres_perfis):
    previa = client.post(_url(tres_perfis), _classificacao(aplicar=f"marco:{P1}:0"))

    resposta = client.post(
        _url(tres_perfis),
        {
            **_classificacao(
                confirmar_aplicacao=f"marco:{P1}:0",
                aplicar_destino=[P2],
                aplicar_impressao=_impressao(previa.content.decode()),
            ),
            # Depois da prévia, alguém trocou o prazo do recurso na origem.
            f"marco-{P1}-0-appealDurationDays": "5",
        },
    )

    assert resposta.status_code == 200
    assert "mudou depois da prévia" in _texto(resposta)
    assert not MarcoClassificatorio.objects.exists()
    assert not RegistroAuditoria.objects.filter(operation="APLICAR_A_TODOS").exists()


def test_sem_destino_marcado_nada_e_gravado(client, tres_perfis):
    previa = client.post(_url(tres_perfis), _classificacao(aplicar=f"marco:{P1}:0"))

    resposta = client.post(
        _url(tres_perfis),
        _classificacao(
            confirmar_aplicacao=f"marco:{P1}:0",
            aplicar_impressao=_impressao(previa.content.decode()),
        ),
    )

    assert resposta.status_code == 200
    assert "Nenhum Perfil está marcado" in _texto(resposta)
    assert not MarcoClassificatorio.objects.exists()


def test_o_destino_fora_do_alcance_nao_e_tocado_mesmo_forjado(client, tres_perfis):
    previa = client.post(_url(tres_perfis), _classificacao(aplicar=f"marco:{P1}:0"))

    resposta = client.post(
        _url(tres_perfis),
        _classificacao(
            confirmar_aplicacao=f"marco:{P1}:0",
            aplicar_destino=[P2, P3],
            aplicar_impressao=_impressao(previa.content.decode()),
        ),
    )

    assert resposta.status_code == 302
    assert not MarcoClassificatorio.objects.filter(perfil_id=P3).exists()


def test_cancelar_nao_grava_e_devolve_o_digitado(client, tres_perfis):
    resposta = client.post(_url(tres_perfis), _classificacao(cancelar_aplicacao=f"marco:{P1}:0"))

    assert resposta.status_code == 200
    assert "aplicar_impressao" not in resposta.content.decode()
    assert f'name="marco-{P1}-0-id" value="{MARCO}"' in resposta.content.decode()
    assert not MarcoClassificatorio.objects.exists()


def test_o_botao_diz_quantos_perfis_alcanca(client, tres_perfis):
    client.post(_url(tres_perfis), _classificacao())

    corpo = client.get(_url(tres_perfis)).content.decode()

    assert re.search(rf'name="aplicar"\s+value="marco:{P1}:0"', corpo)
    assert "Aplicar aos demais Perfis (2)" in corpo


def test_edital_de_um_perfil_nao_oferece_o_gesto(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    so_um = {
        k: v for k, v in _perfis_no_formulario().items() if k.startswith(("perfil-0", "fato-0"))
    }
    client.post(_url(edital, "perfis"), so_um)
    edital.refresh_from_db()

    corpo = client.get(_url(edital)).content.decode()

    assert 'name="aplicar"' not in corpo


def test_quem_nao_compoe_nao_aplica(client, tres_perfis):
    previa = client.post(_url(tres_perfis), _classificacao(aplicar=f"marco:{P1}:0"))
    identificar(client, "bruno.homologador", ["homologador"])

    resposta = client.post(
        _url(tres_perfis),
        _classificacao(
            confirmar_aplicacao=f"marco:{P1}:0",
            aplicar_destino=[P2],
            aplicar_impressao=_impressao(previa.content.decode()),
        ),
    )

    assert resposta.status_code in (200, 404)
    assert not MarcoClassificatorio.objects.exists()
    assert not RegistroAuditoria.objects.filter(operation="APLICAR_A_TODOS").exists()


def test_perfis_intocados_fora_da_unidade(client, tres_perfis):
    antes = {p.id: (p.locality, p.name, p.immediate_vacancies) for p in PerfilVaga.objects.all()}
    previa = client.post(_url(tres_perfis), _classificacao(aplicar=f"marco:{P1}:0"))
    client.post(
        _url(tres_perfis),
        _classificacao(
            confirmar_aplicacao=f"marco:{P1}:0",
            aplicar_destino=[P2],
            aplicar_impressao=_impressao(previa.content.decode()),
        ),
    )

    depois = {p.id: (p.locality, p.name, p.immediate_vacancies) for p in PerfilVaga.objects.all()}
    assert antes == depois
