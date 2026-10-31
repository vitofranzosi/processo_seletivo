"""A semente do registro de Unidades: só registro vazio, e nenhuma subida desfaz a aplicação (110).

Substitui os testes da sincronização da `060`, que aplicava o arquivo em toda subida. Os casos de
registro vazio dispensam o Cefor da fixture da suíte (`sem_unidade_da_suite`); os demais partem
dele, como uma instalação que já existe.
"""

import json
import re
import threading
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.db import connection
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avisos.models import ModeloDeAviso
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.unidades.application import registro, semente
from processo_seletivo.unidades.management.commands.sincronizar_unidades import AVISO
from processo_seletivo.unidades.models import Unidade
from tests.fixtures.autoridades import CEFOR

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

vazio = pytest.mark.sem_unidade_da_suite

RAIZ = Path(__file__).resolve().parents[3]
SERRA = {
    "sigla": "Serra",
    "nome": "Campus Serra",
    "cabecalho": ["Campus Serra"],
    "local": "Serra (ES)",
    "ativa": True,
}
ADMINISTRADORA = Actor("ines.institucional", "institucional", frozenset({"unidade:administrar"}))


def _declarado(**extra):
    cefor = {chave: valor for chave, valor in CEFOR.items() if chave != "codigo"}
    return {"cefor": cefor, **extra}


def _arquivo(tmp_path, conteudo):
    caminho = tmp_path / "unidades.json"
    caminho.write_text(json.dumps(conteudo), encoding="utf-8")
    return str(caminho)


def _comando(nome="semear_unidades", *argumentos):
    saida, erro = StringIO(), StringIO()
    call_command(nome, *argumentos, stdout=saida, stderr=erro)
    return saida.getvalue().strip().splitlines(), erro.getvalue()


def _registro():
    return [
        (u.codigo, u.sigla, u.nome, u.cabecalho, u.local, u.atendimento, u.ativa)
        for u in Unidade.objects.order_by("codigo")
    ]


def _eventos_de_unidade():
    return RegistroAuditoria.objects.filter(aggregate_type="Unidade").count()


# --- O arquivo -----------------------------------------------------------------------------------


def test_o_arquivo_versionado_declara_so_o_cefor():
    """FR-1111 da `060`, e a regra 1 da migração: a release da 110 não muda o arquivo."""
    assert semente.ler() == _declarado()


@pytest.mark.parametrize("codigo", ["Serra", " serra", "serra campus", "serra_campus", "-serra"])
def test_codigo_fora_do_formato_e_recusado_sem_conversao(codigo):
    """EC-1: a semente não converte o código, como a tela não converte."""
    with pytest.raises(DomainError) as recusa:
        semente.validar(_declarado(**{codigo: SERRA}))
    assert recusa.value.code == "unidade_malformada"


# --- Registro vazio ------------------------------------------------------------------------------


@vazio
def test_registro_vazio_e_semeado_com_trilha_da_implantacao(tmp_path):
    """US5, FR-3302, FR-3304."""
    resultado = semente.semear(_arquivo(tmp_path, _declarado(serra=SERRA)))

    assert resultado == semente.Resultado(semeadas=2, registradas=2)
    serra = Unidade.objects.get(codigo="serra")
    evento = RegistroAuditoria.objects.get(operation="REGISTRAR_UNIDADE", aggregate_id=serra.pk)
    assert (evento.actor_subject, evento.institution_scope) == ("implantacao", "serra")
    assert evento.detalhe["depois"]["nome"] == "Campus Serra"


@vazio
@pytest.mark.parametrize(
    "entrada",
    [
        {**SERRA, "cabecalho": []},
        {**SERRA, "cabecalho": ["um", "dois", "três"]},
        {**SERRA, "cabecalho": ["", "dois"]},
        {**SERRA, "nome": "   "},
        {**SERRA, "ativa": "sim"},
        {k: v for k, v in SERRA.items() if k != "local"},
        {**SERRA, "sobrando": 1},
        {**SERRA, "atendimento": ""},
    ],
    ids=[
        "sem-linha",
        "tres-linhas",
        "linha-vazia",
        "nome-vazio",
        "ativa-texto",
        "falta",
        "sobra",
        "canal-vazio",
    ],
)
def test_arquivo_malformado_falha_com_registro_vazio_sem_gravar_nada(tmp_path, entrada):
    """EC-11, primeira metade: num banco novo o arquivo é do repositório, e a falha alta é certa."""
    with pytest.raises(DomainError) as recusa:
        semente.semear(_arquivo(tmp_path, _declarado(serra=entrada)))

    assert recusa.value.code == "unidade_malformada"
    assert not Unidade.objects.exists(), "tudo ou nada"


@vazio
def test_duas_sementes_simultaneas_gravam_uma_vez(tmp_path):
    """D-004: a segunda espera a primeira na trava e encontra o registro preenchido."""
    if connection.vendor != "postgresql":
        pytest.skip("a trava é do PostgreSQL")
    caminho = _arquivo(tmp_path, _declarado())
    erros = []

    def semear():
        try:
            semente.semear(caminho)
        except Exception as erro:  # noqa: BLE001 — o caso registra qualquer falha da corrida
            erros.append(erro)
        finally:
            connection.close()

    threads = [threading.Thread(target=semear) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert erros == []
    assert Unidade.objects.count() == 1
    assert _eventos_de_unidade() == 1


@vazio
def test_o_comando_diz_que_semeou_e_cria_os_modelos(tmp_path):
    """FR-3305, e a linha que o guia ensina a ler (D-004)."""
    linhas, _ = _comando("semear_unidades", "--arquivo", _arquivo(tmp_path, _declarado()))

    assert linhas == ["Unidades: 1 semeadas.", "Modelos de aviso: 3 criados."]


# --- Registro preenchido -------------------------------------------------------------------------


def test_registro_preenchido_nao_grava_nem_le_o_arquivo(tmp_path):
    """FR-3302, EC-11, segunda metade: o arquivo sem autoridade nem é aberto."""
    antes = (_registro(), _eventos_de_unidade())

    resultado = semente.semear(str(tmp_path / "nao-existe.json"))

    assert resultado == semente.Resultado(semeadas=0, registradas=1)
    assert (_registro(), _eventos_de_unidade()) == antes


def test_unidade_fora_do_arquivo_e_valores_diferentes_permanecem(tmp_path):
    """FR-3301, FR-3303 — item 3 do pedido: a unidade do banco sem estar no arquivo continua."""
    registro.registrar(
        ADMINISTRADORA, campos={**SERRA, "codigo": "serra"}, motivo="Cadastro de teste"
    )
    arquivo = _arquivo(tmp_path, _declarado(vitoria={**SERRA, "nome": "Campus Vitória"}))
    antes = (_registro(), _eventos_de_unidade())

    linhas, _ = _comando("semear_unidades", "--arquivo", arquivo)

    assert linhas[0] == "Unidades: registro com 2 unidades; a semente não se aplica."
    assert (_registro(), _eventos_de_unidade()) == antes


def test_a_semente_nao_desfaz_a_tela():
    """SC-1042 — item 5 do pedido: o nome e o canal editados pela aplicação sobrevivem ao deploy."""
    campos = {
        **{k: v for k, v in CEFOR.items() if k not in ("codigo", "ativa")},
        "nome": "Centro de Referência — nome novo",
        "atendimento": "atendimento.cefor@ifes.edu.br",
    }
    conferencia = registro.conferir_alteracao(ADMINISTRADORA, codigo="cefor", campos=campos)
    registro.alterar(
        ADMINISTRADORA,
        codigo="cefor",
        campos=campos,
        versao=conferencia["versao"],
        motivo="Mudança de nome",
    )
    antes = (_registro(), _eventos_de_unidade())

    _comando("semear_unidades")
    _comando("sincronizar_unidades")

    assert (_registro(), _eventos_de_unidade()) == antes
    cefor = Unidade.objects.get(codigo="cefor")
    assert (cefor.nome, cefor.atendimento) == (
        "Centro de Referência — nome novo",
        "atendimento.cefor@ifes.edu.br",
    )


def test_a_inicializacao_nao_altera_o_registro():
    """SC-1042 — item 4 do pedido: duas subidas seguidas, com uma unidade só do banco.

    O caso roda a semente como o `entrypoint.sh` a roda, e não o `entrypoint.sh` inteiro: os papéis
    do provisionamento são do cluster, e os workers da suíte colidiriam neles. Que a semente é o
    único passo do roteiro que toca unidade, confere-se lendo o roteiro.
    """
    Unidade.objects.filter(codigo="cefor").update(nome="Cefor editado no banco")
    Unidade.objects.create(registrada_em=timezone.now(), codigo="serra", **SERRA)
    antes = (_registro(), _eventos_de_unidade())

    primeira, _ = _comando("semear_unidades")
    segunda, _ = _comando("semear_unidades")

    assert (
        primeira[0] == segunda[0] == ("Unidades: registro com 2 unidades; a semente não se aplica.")
    )

    assert (_registro(), _eventos_de_unidade()) == antes
    roteiro = (RAIZ / "scripts" / "docker" / "entrypoint.sh").read_text(encoding="utf-8")
    comandos = re.findall(r"^python manage\.py (\S+)", roteiro, re.M)
    assert [c for c in comandos if "unidade" in c] == ["semear_unidades"]


def test_os_modelos_iniciais_sao_garantidos_uma_vez():
    """FR-3305 — item 14 do pedido."""
    primeira, _ = _comando("semear_unidades")
    segunda, _ = _comando("semear_unidades")

    assert primeira[1] == "Modelos de aviso: 3 criados."
    assert segunda[1] == "Modelos de aviso: 0 criados."
    assert ModeloDeAviso.objects.filter(institution_scope="cefor", modelo_inicial=True).count() == 3


# --- O apelido e os roteiros ---------------------------------------------------------------------


def test_o_nome_anterior_roda_a_semente_e_avisa():
    """EC-17, FR-3306, D-003: o roteiro antigo não falha; o aviso fica no stderr."""
    semeada, _ = _comando("semear_unidades")
    apelido, aviso = _comando("sincronizar_unidades")

    esperada = "Unidades: registro com 1 unidades; a semente não se aplica."
    assert apelido[0] == semeada[0] == esperada
    assert aviso.strip() == AVISO
    assert AVISO not in "\n".join(apelido)


def test_os_roteiros_do_repositorio_chamam_a_semente_pelo_nome_novo():
    """FR-3306: o Makefile, o entrypoint do compose e o guia de produção.

    O guia ainda pode **citar** o nome anterior, para explicar o apelido; o que ele não pode é
    **mandar rodar** o nome anterior.
    """
    makefile = (RAIZ / "backend" / "Makefile").read_text(encoding="utf-8")
    entrypoint = (RAIZ / "scripts" / "docker" / "entrypoint.sh").read_text(encoding="utf-8")
    guia = (RAIZ / "doc" / "implantacao-em-producao-ubuntu.md").read_text(encoding="utf-8")

    for nome, texto in (("Makefile", makefile), ("entrypoint.sh", entrypoint), ("guia", guia)):
        assert "semear_unidades" in texto, nome
        assert not re.search(r"(ps-manage|manage\.py)[^\n]*\bsincronizar_unidades", texto), nome


# --- A exportação, para reverter -----------------------------------------------------------------


def test_exportar_reproduz_o_registro_sem_gravar_e_a_semente_aceita():
    """D-016: `ativa` sempre; o canal só quando preenchido."""
    Unidade.objects.create(
        registrada_em=timezone.now(),
        codigo="serra",
        atendimento="serra@ifes.edu.br",
        **{**SERRA, "ativa": False},
    )
    antes = _eventos_de_unidade()

    linhas, _ = _comando("semear_unidades", "--exportar")
    exportado = json.loads("\n".join(linhas))

    assert exportado == semente.exportar()
    assert exportado["cefor"]["ativa"] is True and "atendimento" not in exportado["cefor"]
    assert exportado["serra"]["ativa"] is False
    assert exportado["serra"]["atendimento"] == "serra@ifes.edu.br"
    assert semente.validar(exportado)
    assert _eventos_de_unidade() == antes
