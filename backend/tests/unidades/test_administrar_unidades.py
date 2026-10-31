"""Administrar o registro de Unidades pela aplicação: cadastrar, editar, desativar e reativar (110).

Os casos de uso chamados sem tela, contra o banco: a regra, a trilha, a concorrência e o efeito em
quem cria Processo, concede acesso e cadastra autoridade na unidade. A tela tem os dela, em
`tests/interface/test_telas_de_unidades.py`; a autorização, em
`tests/authorization/test_administrar_unidades.py`.
"""

import threading

import pytest
from django.db import connection
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avisos.models import ModeloDeAviso
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.seguranca.models import Vinculo
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.unidades.application import autoridades, registro
from processo_seletivo.unidades.models import AutoridadeHabilitada, Unidade
from tests.fixtures.autoridades import CEFOR
from tests.fixtures.edital import actor_headers, complete_draft
from tests.seguranca.apoio import pessoa

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ADMINISTRADORA = Actor(
    "pessoa-administradora",
    "institucional",
    frozenset({"acesso:administrar", "unidade:administrar"}),
)
SERRA = {
    "codigo": "serra",
    "sigla": "Serra",
    "nome": "Campus Serra",
    "cabecalho": ["Campus Serra"],
    "local": "Serra (ES)",
    "atendimento": "atendimento@serra.example",
}


def _registrar(**campos):
    return registro.registrar(
        ADMINISTRADORA, campos={**SERRA, **campos}, motivo="Portaria nº 1/2026"
    )


def _editaveis(unidade, **mudancas):
    return {
        "sigla": unidade.sigla,
        "nome": unidade.nome,
        "cabecalho": list(unidade.cabecalho),
        "local": unidade.local,
        "atendimento": unidade.atendimento,
        **mudancas,
    }


def _alterar(codigo="serra", **mudancas):
    unidade = Unidade.objects.get(codigo=codigo)
    campos = _editaveis(unidade, **mudancas)
    conferencia = registro.conferir_alteracao(ADMINISTRADORA, codigo=codigo, campos=campos)
    return registro.alterar(
        ADMINISTRADORA,
        codigo=codigo,
        campos=campos,
        versao_conferida=conferencia["versao"],
        motivo="Ofício nº 2/2026",
    )


def _situacao(ato, codigo="serra"):
    versao = registro.consequencias(ADMINISTRADORA, codigo=codigo, ato=ato)["versao"]
    funcao = registro.desativar if ato == "desativar" else registro.reativar
    return funcao(ADMINISTRADORA, codigo=codigo, versao_conferida=versao, motivo=f"Motivo de {ato}")


def _criar_processo(api_client, codigo, chave):
    return api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": f"PS-{codigo}-{chave}",
            "title": "Processo",
            "firstEdital": {"number": chave, "year": 2026, "title": "Edital"},
        },
        format="json",
        HTTP_AUTHORIZATION=f"Bearer gestor-{codigo}|{codigo}|processo:criar,edital:criar",
        HTTP_IDEMPOTENCY_KEY=f"110-processo-{codigo}-{chave}",
        HTTP_X_CORRELATION_ID="110",
    )


def _erro(funcao, *argumentos, **nomeados):
    with pytest.raises(DomainError) as recusa:
        funcao(*argumentos, **nomeados)
    return recusa.value


# --- Cadastrar (US1) ---------------------------------------------------------------------------


def test_registrar_uma_unidade():
    """FR-3316, item 2 do pedido: a segunda unidade pela aplicação, ativa, sem tocar o arquivo."""
    unidade = _registrar()

    assert Unidade.objects.get(codigo="serra") == unidade
    assert unidade.ativa is True
    assert unidade.atendimento == "atendimento@serra.example"
    assert unidade.registrada_em is not None


def test_cada_ato_grava_o_evento_no_escopo_da_unidade():
    """FR-3313, FR-3331, SC-1044, item 13 do pedido: pessoa, permissão, motivo, antes e depois."""
    unidade = _registrar()
    _alterar(nome="Campus Serra — Sede")
    _situacao("desativar")
    _situacao("reativar")

    eventos = list(
        RegistroAuditoria.objects.filter(
            aggregate_type="Unidade", aggregate_id=unidade.pk
        ).order_by("occurred_at", "event_id")
    )
    assert [e.operation for e in eventos] == ["REGISTRAR_UNIDADE"] + ["ALTERAR_UNIDADE"] * 3
    assert {e.institution_scope for e in eventos} == {"serra"}
    assert {e.actor_subject for e in eventos} == {ADMINISTRADORA.subject}
    assert {e.permission for e in eventos} == {"unidade:administrar"}
    assert [e.reason for e in eventos] == [
        "Portaria nº 1/2026",
        "Ofício nº 2/2026",
        "Motivo de desativar",
        "Motivo de reativar",
    ]
    sem_codigo = {k: v for k, v in SERRA.items() if k != "codigo"}
    assert eventos[0].detalhe == {"depois": {**sem_codigo, "ativa": True}}
    assert eventos[1].detalhe["antes"]["nome"] == "Campus Serra"
    assert eventos[1].detalhe["depois"]["nome"] == "Campus Serra — Sede"
    assert [(e.previous_state, e.new_state) for e in eventos[2:]] == [
        ("ATIVA", "DESATIVADA"),
        ("DESATIVADA", "ATIVA"),
    ]


def test_os_modelos_iniciais_nascem_uma_vez_com_a_pessoa_como_autora():
    """FR-3319, item 14 do pedido, `D-006`: a trilha não diz que a implantação os criou."""
    _registrar()

    modelos = ModeloDeAviso.objects.filter(institution_scope="serra", modelo_inicial=True)
    assert modelos.count() == 3
    assert set(modelos.values_list("criado_por", flat=True)) == {ADMINISTRADORA.subject}
    autores = set(
        RegistroAuditoria.objects.filter(
            aggregate_type="ModeloDeAviso", institution_scope="serra"
        ).values_list("actor_subject", flat=True)
    )
    assert autores == {ADMINISTRADORA.subject}


def test_sem_motivo_nada_e_gravado():
    recusa = _erro(registro.registrar, ADMINISTRADORA, campos=SERRA, motivo="  ")

    assert (recusa.code, recusa.campo) == ("motivo_obrigatorio", "motivo")
    assert not Unidade.objects.filter(codigo="serra").exists()


def test_falha_no_evento_desfaz_o_ato(monkeypatch):
    """FR-3332: sem evento, nada muda."""

    def falhar(**_):
        raise RuntimeError("a trilha caiu")

    monkeypatch.setattr(registro, "record_event", falhar)
    with pytest.raises(RuntimeError):
        _registrar()

    assert not Unidade.objects.filter(codigo="serra").exists()
    assert not ModeloDeAviso.objects.filter(institution_scope="serra").exists()


def test_codigo_repetido_e_recusado():
    """FR-3317."""
    _registrar()

    recusa = _erro(_registrar, nome="Outro nome")

    assert (recusa.code, recusa.campo) == ("codigo_ja_registrado", "codigo")
    assert Unidade.objects.get(codigo="serra").nome == "Campus Serra"


@pytest.mark.django_db(transaction=True)
def test_dois_cadastros_do_mesmo_codigo_gravam_um():
    """EC-2: o segundo recebe a recusa, e nada dele fica."""
    if connection.vendor != "postgresql":
        pytest.skip("a corrida é do PostgreSQL")
    resultados = []

    def cadastrar(nome):
        try:
            resultados.append(_registrar(nome=nome).nome)
        except DomainError as recusa:
            resultados.append(recusa.code)
        finally:
            connection.close()

    threads = [threading.Thread(target=cadastrar, args=(nome,)) for nome in ("Um", "Dois")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert resultados.count("codigo_ja_registrado") == 1, resultados
    assert Unidade.objects.filter(codigo="serra").count() == 1
    assert ModeloDeAviso.objects.filter(institution_scope="serra").count() == 3


def test_reitoria_e_unidade_como_as_outras_sem_leitura_dos_campi(api_client, manager_headers):
    """EC-13, decisão de produto 6: unidade emissora, e nenhuma supervisão transversal."""
    reitoria = _registrar(
        codigo="reitoria", sigla="Reitoria", nome="Reitoria", cabecalho=["Reitoria"]
    )
    do_cefor = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": "PS-CEFOR-110",
            "title": "Processo do Cefor",
            "firstEdital": {"number": "1", "year": 2026, "title": "Edital"},
        },
        format="json",
        **manager_headers,
    )
    assert do_cefor.status_code == 201, do_cefor.content
    edital = Edital.objects.get(processo_id=do_cefor.json()["id"])

    da_reitoria = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{
            **actor_headers(
                "reitor", ["edital:elaborar"], escopo="reitoria", key="110-rascunho-da-reitoria"
            ),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )

    assert reitoria.ativa is True
    assert da_reitoria.status_code == 404


def test_unidade_nova_nao_herda_autoridade_nem_acesso():
    """Item 11 do pedido: duas unidades não compartilham autorização nem autoridade."""
    _registrar()

    assert not AutoridadeHabilitada.objects.filter(unidade__codigo="serra").exists()
    assert not Vinculo.objects.filter(escopo="serra").exists()


def test_unidade_nova_disponivel_para_acesso_processo_e_autoridade(api_client):
    """FR-3320: na requisição seguinte, sem reinício."""
    _registrar()
    administrador = pessoa("admin-serra", nome="Administrador da Serra")

    vinculo = acessos.conceder(
        ADMINISTRADORA,
        pessoa=administrador,
        escopo="serra",
        papel=acessos.ADMINISTRADOR_DE_ACESSOS,
        motivo="Portaria nº 3/2026",
        now=timezone.now(),
    )
    criado = _criar_processo(api_client, "serra", "1")
    autoridade = autoridades.cadastrar(
        actor=Actor("gestor-serra", "serra", frozenset({"autoridade:gerir"})),
        cargo="Diretor-Geral do Campus Serra",
        inicio_vigencia=timezone.localdate(),
        idempotency_key="110-autoridade-da-serra",
        correlation_id="110",
    )

    assert vinculo.escopo == "serra"
    assert criado.status_code == 201, criado.content
    assert autoridade.unidade.codigo == "serra"


# --- Editar (US2) ------------------------------------------------------------------------------


def test_alterar_grava_antes_e_depois():
    """FR-3321."""
    _registrar()

    unidade = _alterar(nome="Campus Serra — Sede", cabecalho=["Campus Serra", "Sede"])

    assert (unidade.nome, unidade.cabecalho) == ("Campus Serra — Sede", ["Campus Serra", "Sede"])
    assert unidade.alterada_em is not None


def test_o_codigo_enviado_na_alteracao_e_ignorado():
    """EC-9, item 7 do pedido: o código vem da rota."""
    unidade = _registrar()
    campos = _editaveis(unidade, nome="Outro nome", codigo="vitoria")
    versao = registro.conferir_alteracao(ADMINISTRADORA, codigo="serra", campos=campos)["versao"]

    registro.alterar(
        ADMINISTRADORA, codigo="serra", campos=campos, versao_conferida=versao, motivo="Teste"
    )

    assert Unidade.objects.get(pk=unidade.pk).codigo == "serra"
    assert not Unidade.objects.filter(codigo="vitoria").exists()


def test_nada_mudou_e_recusado_sem_evento():
    """FR-3322, EC-3, EC-4: aparados, os valores são os mesmos."""
    unidade = _registrar()
    antes = RegistroAuditoria.objects.filter(aggregate_type="Unidade").count()
    campos = _editaveis(unidade, nome=f"  {unidade.nome}  ")

    recusa = _erro(registro.conferir_alteracao, ADMINISTRADORA, codigo="serra", campos=campos)

    assert recusa.code == "nada_mudou"
    assert RegistroAuditoria.objects.filter(aggregate_type="Unidade").count() == antes


def test_duas_alteracoes_concorrentes_a_segunda_e_recusada():
    """FR-3325, `D-007`: a segunda conferiu uma versão que não existe mais."""
    unidade = _registrar()
    primeira = _editaveis(unidade, nome="Primeira")
    segunda = _editaveis(unidade, nome="Segunda")
    versao = registro.conferir_alteracao(ADMINISTRADORA, codigo="serra", campos=primeira)["versao"]
    registro.alterar(
        ADMINISTRADORA, codigo="serra", campos=primeira, versao_conferida=versao, motivo="1"
    )

    recusa = _erro(
        registro.alterar,
        ADMINISTRADORA,
        codigo="serra",
        campos=segunda,
        versao_conferida=versao,
        motivo="2",
    )

    assert recusa.code == "unidade_alterada"
    assert Unidade.objects.get(codigo="serra").nome == "Primeira"


def test_canal_apagado_volta_ao_institucional():
    """EC-12."""
    _registrar()

    unidade = _alterar(atendimento="")

    assert unidade.atendimento == ""


def test_editar_o_cefor_nao_toca_o_arquivo():
    """FR-3301: a fonte é o banco; o arquivo continua o de antes."""
    from processo_seletivo.unidades.application.semente import ler

    _alterar("cefor", nome="Cefor com nome novo")

    assert ler()["cefor"]["nome"] == CEFOR["nome"]


# --- Desativar e reativar (US3) ----------------------------------------------------------------


def test_desativada_nao_recebe_processo_e_conduz_o_existente(api_client):
    """FR-3326, item 9 do pedido."""
    _registrar()
    existente = _criar_processo(api_client, "serra", "1")
    assert existente.status_code == 201, existente.content
    edital = Edital.objects.get(processo_id=existente.json()["id"])

    _situacao("desativar")
    novo = _criar_processo(api_client, "serra", "2")
    conduzido = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{
            **actor_headers(
                "elaboradora", ["edital:elaborar"], escopo="serra", key="110-rascunho-conduzido"
            ),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )
    concessao = _erro(
        acessos.conceder,
        ADMINISTRADORA,
        pessoa=pessoa("outra"),
        escopo="serra",
        papel=acessos.ADMINISTRADOR_DE_ACESSOS,
        motivo="Teste",
        now=timezone.now(),
    )

    assert novo.status_code == 422 and "desativada" in novo.json()["detail"]
    assert conduzido.status_code < 400, conduzido.content
    assert concessao.code == "unidade_nao_registrada"


def test_desativar_a_unica_ativa_e_permitido():
    """EC-5: nada se exclui, e a reativação devolve."""
    _situacao("desativar", "cefor")

    assert not Unidade.objects.filter(ativa=True).exists()


def test_autoridade_de_desativada_continua_editavel():
    """EC-14: o certame em curso precisa de quem assine."""
    _registrar()
    _situacao("desativar")

    autoridade = autoridades.cadastrar(
        actor=Actor("gestor-serra", "serra", frozenset({"autoridade:gerir"})),
        cargo="Diretor-Geral",
        inicio_vigencia=timezone.localdate(),
        idempotency_key="110-autoridade-desativada",
        correlation_id="110",
    )

    assert autoridade.unidade.codigo == "serra"


def test_reativada_volta_a_receber_processo(api_client):
    """FR-3327, item 10 do pedido."""
    _registrar()
    _situacao("desativar")
    _situacao("reativar")

    assert _criar_processo(api_client, "serra", "3").status_code == 201


def test_transicoes_repetidas_sao_recusadas():
    """FR-3328."""
    unidade = _registrar()
    versao = registro.versao(unidade)

    ja_ativa = _erro(
        registro.reativar, ADMINISTRADORA, codigo="serra", versao_conferida=versao, motivo="x"
    )
    _situacao("desativar")
    versao = registro.versao(Unidade.objects.get(codigo="serra"))
    ja_desativada = _erro(
        registro.desativar, ADMINISTRADORA, codigo="serra", versao_conferida=versao, motivo="x"
    )

    assert (ja_ativa.code, ja_desativada.code) == ("unidade_ja_ativa", "unidade_ja_desativada")


def test_as_consequencias_dizem_os_processos_e_a_moldura(api_client):
    """FR-3326, FR-3330, EC-6, EC-7."""
    sozinho = registro.consequencias(ADMINISTRADORA, codigo="cefor", ato="desativar")
    assert sozinho["moldura"] == ("Cefor/Ifes", "Ifes"), "a única ativa deixa de sê-lo"

    _registrar()
    assert _criar_processo(api_client, "serra", "4").status_code == 201
    da_serra = registro.consequencias(ADMINISTRADORA, codigo="serra", ato="desativar")

    assert da_serra["processos_nao_encerrados"] == 1
    assert da_serra["moldura"] == ("Ifes", "Cefor/Ifes"), "sobra uma ativa"
    assert (
        registro.mudanca_da_moldura(codigo="cefor", ativa_depois=True, sigla_depois="CEFOR") is None
    )


def test_a_mudanca_da_sigla_da_unica_ativa_muda_a_moldura():
    """FR-3330, terceira situação."""
    assert registro.mudanca_da_moldura(
        codigo="cefor", ativa_depois=True, sigla_depois="Cefor-Ifes"
    ) == ("Cefor/Ifes", "Cefor-Ifes/Ifes")
