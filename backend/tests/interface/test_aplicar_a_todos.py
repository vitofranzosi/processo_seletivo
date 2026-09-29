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


# ---- a etapa Perfis: a Modalidade pelo código e o controle do Edital (US2) -----------------------

PCD = {
    "modalidade-0-0-id": "aaaaaaaa-0000-4000-8000-000000051d01",
    "modalidade-0-0-ruleId": "aaaaaaaa-0000-4000-8000-000000051d11",
    "modalidade-0-0-code": "PCD",
    "modalidade-0-0-name": "Pessoa com deficiência",
    "modalidade-0-0-percentage": "5",
    "modalidade-0-0-foundation": "Lei 13.146/2015",
    "modalidade-0-0-version": "2015-07-06",
}


def test_a_modalidade_nasce_nos_demais_pelo_codigo_e_nao_toca_o_quadro(client, tres_perfis):
    from processo_seletivo.editais.models.perfis import ModalidadeConcorrencia

    formulario = _perfis_no_formulario(**PCD)
    previa = client.post(_url(tres_perfis, "perfis"), {**formulario, "aplicar": "modalidade:0:0"})

    assert previa.status_code == 200
    corpo = _texto(previa)
    assert "Aplicar a Modalidade aos demais Perfis" in corpo
    assert "2 nascem" in corpo
    assert "Já declara: nenhuma" in corpo
    assert not ModalidadeConcorrencia.objects.filter(perfil_id=P2).exists()

    resposta = client.post(
        _url(tres_perfis, "perfis"),
        {
            **formulario,
            "confirmar_aplicacao": "modalidade:0:0",
            "aplicar_destino": ["1", "2"],
            "aplicar_impressao": _impressao(previa.content.decode()),
        },
    )

    assert resposta.status_code == 302, resposta.content
    for perfil in (P2, P3):
        modalidade = ModalidadeConcorrencia.objects.get(perfil_id=perfil)
        assert modalidade.code == "PCD"
        assert str(modalidade.id) != PCD["modalidade-0-0-id"]
        assert modalidade.regra_normativa.percentage == 5
        assert (
            not PerfilVaga.objects.get(pk=perfil)
            .quadro_de_vagas.filter(modalidade=modalidade)
            .exists()
        )
    registro = RegistroAuditoria.objects.get(operation="APLICAR_A_TODOS")
    assert registro.detalhe["origem"]["modalidade"] == "PCD"
    assert {item["perfil"] for item in registro.detalhe["destinos"]} == {P2, P3}


def test_a_forma_de_convocacao_declarada_uma_vez_vai_a_todos(client, tres_perfis):
    formulario = _perfis_no_formulario()
    previa = client.post(
        _url(tres_perfis, "perfis"),
        {**formulario, "edital-callForm": "INDIVIDUAL_MESSAGE", "aplicar": "edital:callForm"},
    )
    assert "3 nascem" in _texto(previa)

    resposta = client.post(
        _url(tres_perfis, "perfis"),
        {
            **formulario,
            "edital-callForm": "INDIVIDUAL_MESSAGE",
            "confirmar_aplicacao": "edital:callForm",
            "aplicar_destino": ["0", "1", "2"],
            "aplicar_impressao": _impressao(previa.content.decode()),
        },
    )

    assert resposta.status_code == 302, resposta.content
    assert set(PerfilVaga.objects.values_list("forma_de_convocacao", flat=True)) == {
        "INDIVIDUAL_MESSAGE"
    }
    corpo = client.get(_url(tres_perfis, "perfis")).content.decode()
    assert re.search(r'<option value="INDIVIDUAL_MESSAGE" selected>', corpo)


def test_o_perfil_novo_nasce_com_a_forma_que_todos_declaram(client, tres_perfis):
    PerfilVaga.objects.update(forma_de_convocacao="PUBLICATION")

    corpo = client.get(
        reverse("interface:fragmento-perfil") + f"?edital={tres_perfis.id}"
    ).content.decode()

    assert re.search(r'<option value="PUBLICATION" selected>', corpo)


def test_a_reversao_deixa_fora_o_perfil_sem_lista_reservada(client, tres_perfis):
    formulario = _perfis_no_formulario(**PCD)
    previa = client.post(
        _url(tres_perfis, "perfis"),
        {
            **formulario,
            "edital-vacancyReversion": "ON_BALANCE",
            "aplicar": "edital:vacancyReversion",
        },
    )

    corpo = _texto(previa)
    assert "1 nasce, 2 ficam fora do alcance" in corpo
    assert "não declara lista reservada" in corpo


# **A escolha do Edital que não passou pela prévia** (051, FR-916). O controle é origem de um gesto,
# e não campo: *Salvar* que o ignorasse a descartaria em silêncio, e *Salvar* que o aplicasse
# pularia a prévia. Por isso a escolha pendente impede gravar, e fica na tela com o aviso.
AVISO_PENDENTE = "Esta escolha ainda não foi aplicada. Confira o alcance antes de confirmar."


@pytest.mark.parametrize("botao", [{}, {"destino": "classificacao"}], ids=["salvar", "avancar"])
def test_salvar_com_a_escolha_do_edital_pendente_nao_grava(client, tres_perfis, botao):
    revisao = tres_perfis.revision
    resposta = client.post(
        _url(tres_perfis, "perfis"),
        {**_perfis_no_formulario(**PCD), "edital-callForm": "INDIVIDUAL_MESSAGE", **botao},
    )

    assert resposta.status_code == 200
    tres_perfis.refresh_from_db()
    assert tres_perfis.revision == revisao
    assert set(PerfilVaga.objects.values_list("forma_de_convocacao", flat=True)) == {""}
    corpo = _texto(resposta)
    assert AVISO_PENDENTE in corpo
    assert 'href="#edital-callForm"' in corpo
    # O formulário inteiro volta: a escolha e a Modalidade que ainda não estava gravada.
    assert re.search(r'<option value="INDIVIDUAL_MESSAGE" selected>', corpo)
    assert 'value="Pessoa com deficiência"' in corpo
    # Nenhuma prévia abre sozinha.
    assert 'name="aplicar_impressao"' not in corpo


def test_as_duas_escolhas_pendentes_sao_ditas_cada_uma_no_seu_controle(client, tres_perfis):
    resposta = client.post(
        _url(tres_perfis, "perfis"),
        {
            **_perfis_no_formulario(**PCD),
            "edital-callForm": "PUBLICATION",
            "edital-vacancyReversion": "ON_BALANCE",
        },
    )

    corpo = _texto(resposta)
    assert 'id="pendente-edital-callForm"' in corpo
    assert 'id="pendente-edital-vacancyReversion"' in corpo
    assert corpo.count(AVISO_PENDENTE) == 2
    assert 'name="aplicar_impressao"' not in corpo


def test_o_controle_intocado_nao_impede_mudar_um_perfil_no_cartao(client, tres_perfis):
    """Quem muda um Perfil no cartão não toca o controle, que continua mostrando o comum."""
    PerfilVaga.objects.update(forma_de_convocacao="PUBLICATION")
    formulario = _perfis_no_formulario(
        **{
            "perfil-0-callForm": "INDIVIDUAL_MESSAGE",
            "perfil-1-callForm": "PUBLICATION",
            "perfil-2-callForm": "PUBLICATION",
        }
    )

    resposta = client.post(
        _url(tres_perfis, "perfis"), {**formulario, "edital-callForm": "PUBLICATION"}
    )

    assert resposta.status_code == 302, resposta.content
    assert sorted(PerfilVaga.objects.values_list("forma_de_convocacao", flat=True)) == [
        "INDIVIDUAL_MESSAGE",
        "PUBLICATION",
        "PUBLICATION",
    ]


def test_a_escolha_que_os_cartoes_ja_declaram_nao_esta_pendente(client, tres_perfis):
    formulario = _perfis_no_formulario(
        **{f"perfil-{posicao}-callForm": "PUBLICATION" for posicao in range(3)}
    )

    resposta = client.post(
        _url(tres_perfis, "perfis"), {**formulario, "edital-callForm": "PUBLICATION"}
    )

    assert resposta.status_code == 302, resposta.content


def test_confirmar_uma_escolha_nao_apaga_a_outra(client, tres_perfis):
    """A forma e a reversão mudaram juntas; confirmar a forma grava e redireciona, e a reversão
    escolhida continua na tela, com o aviso — em vez de sumir com o redirecionamento."""
    formulario = {
        **_perfis_no_formulario(**PCD),
        "edital-callForm": "INDIVIDUAL_MESSAGE",
        "edital-vacancyReversion": "ON_BALANCE",
    }
    previa = client.post(_url(tres_perfis, "perfis"), {**formulario, "aplicar": "edital:callForm"})
    resposta = client.post(
        _url(tres_perfis, "perfis"),
        {
            **formulario,
            "confirmar_aplicacao": "edital:callForm",
            "aplicar_destino": ["0", "1", "2"],
            "aplicar_impressao": _impressao(previa.content.decode()),
        },
    )
    assert resposta.status_code == 302, resposta.content

    corpo = _texto(client.get(resposta["Location"]))

    assert re.search(r'<option value="ON_BALANCE" selected>', corpo)
    assert 'id="pendente-edital-vacancyReversion"' in corpo
    assert 'id="pendente-edital-callForm"' not in corpo
    # A notícia é de uma tela só: recarregar não a traz de volta.
    recarregada = _texto(client.get(_url(tres_perfis, "perfis")))
    assert 'id="pendente-edital-vacancyReversion"' not in recarregada


def test_o_botao_do_controle_diz_que_confere(client, tres_perfis):
    corpo = _texto(client.get(_url(tres_perfis, "perfis")))

    assert corpo.count("Conferir aplicação a todos os Perfis") == 2
    assert "Aplicar a todos os Perfis" not in corpo
    assert AVISO_PENDENTE not in corpo


def test_a_reversao_que_so_falta_onde_nao_cabe_nao_esta_pendente():
    """O Perfil sem lista reservada fica fora do alcance, e nunca a receberia: contá-lo tornaria a
    recusa perpétua depois de aplicada a reversão a todos os que a admitem."""
    from processo_seletivo.interface.aplicacao import escolhas_pendentes

    com_lista = {
        "code": "LP01",
        "competitionModalities": [{"id": "m1", "code": "PCD"}],
        "vacancyReversion": {"kind": "ON_BALANCE"},
    }
    sem_lista = {"code": "LP02", "competitionModalities": []}
    perfis = [com_lista, sem_lista]

    assert (
        escolhas_pendentes(perfis, {"edital-vacancyReversion": "ON_BALANCE"}, gravados=perfis) == {}
    )
    assert escolhas_pendentes(
        [{**com_lista, "vacancyReversion": None}, sem_lista],
        {"edital-vacancyReversion": "ON_BALANCE"},
        gravados=perfis,
    ) == {"vacancyReversion": "ON_BALANCE"}
