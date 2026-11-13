"""A versão do modelo gravada na comunicação emitida (121, D-009, FR-3889, SC-1172).

**Decidida pelo usuário sobre o plano** (opção A): o histórico de implantação não identifica a
versão exata do texto que saiu (R-001), e a comunicação passou a gravar o nome do modelo e o
SHA-256 das duas fontes que renderizaram o envio — também na tentativa que falhou.

**O resumo é recalculado aqui por implementação própria**, da regra escrita na R-009, e não pela
função de produção: uma conferência que chamasse a mesma função provaria só que ela concorda
consigo mesma.
"""

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from django.conf import settings as django_settings
from django.core import mail
from django.template.loader import get_template
from django.test import override_settings
from django.utils import timezone

from processo_seletivo.convocacao.application.comunicar import comunicar as emitir
from processo_seletivo.convocacao.models import ComunicacaoEmitida
from tests.integration.convocacao.test_correcao_da_convocacao import chamar, corrigir
from tests.integration.convocacao.test_mensagem_da_convocacao import (
    CorreioQueGuardaEFalha,
    falhar,
)

pytestmark = pytest.mark.django_db(transaction=True)

RAIZ = Path(__file__).resolve().parents[3]
MODELOS = RAIZ / "processo_seletivo/convocacao/templates/convocacao/mensagem"
ESTILOS = RAIZ / "processo_seletivo/shared/templates/correio/estilos.json"
FORMATO = re.compile(r"(inicial|correcao):sha256-com-estilos:[0-9a-f]{64}")


@pytest.fixture
def caixa(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    CorreioQueGuardaEFalha.guardadas = []
    return mail.outbox


def resumo(nome, html, texto, estilos=None):
    """A regra da R-009, escrita de novo: HTML, texto e estilos, rotulados, separados por NUL, em
    UTF-8. Os estilos, sem outro dado, são os do arquivo versionado — o que a conferência pelo Git
    lê.
    """
    estilos = ESTILOS.read_text(encoding="utf-8") if estilos is None else estilos
    conteudo = (
        b"html\0"
        + html.encode("utf-8")
        + b"\0texto\0"
        + texto.encode("utf-8")
        + b"\0estilos\0"
        + estilos.encode("utf-8")
    )
    return f"{nome}:sha256-com-estilos:{hashlib.sha256(conteudo).hexdigest()}"


def do_carregador(nome):
    """O resumo das fontes que o carregador entrega agora — as que renderizam o próximo envio."""
    return resumo(
        nome,
        get_template(f"convocacao/mensagem/{nome}.html").template.source,
        get_template(f"convocacao/mensagem/{nome}.txt").template.source,
    )


def do_disco(nome):
    return resumo(
        nome,
        (MODELOS / f"{nome}.html").read_text(encoding="utf-8"),
        (MODELOS / f"{nome}.txt").read_text(encoding="utf-8"),
    )


def comunicar(edital, gestor, convocacao, chave, **kwargs):
    return emitir(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao.id,
        idempotency_key=chave,
        correlation_id="teste-121-versao",
        **kwargs,
    )


def gravada(declarado):
    return ComunicacaoEmitida.objects.get(id=declarado["id"]).modelo_da_mensagem


class TestAGravacao:
    def test_enviada_grava_o_nome_e_o_resumo(self, caixa, cenario, gestor):
        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="v-env")

        valor = gravada(comunicar(edital, gestor, a, "v-env-com"))

        assert FORMATO.fullmatch(valor)
        assert valor == do_carregador("inicial") == do_disco("inicial")

    def test_falha_do_correio_grava_o_que_se_tentou(self, caixa, cenario, gestor, settings):
        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="v-falha")
        falhar(settings)

        declarado = comunicar(edital, gestor, a, "v-falha-com")

        assert declarado["resultado"] == "FALHA"
        assert gravada(declarado) == do_carregador("inicial")

    def test_falha_sem_destinatario_tambem_grava(self, caixa, cenario, gestor, monkeypatch):
        """A renderização vem antes da conferência do destinatário (plano, seção 5)."""
        from processo_seletivo.convocacao.application import comunicar as modulo

        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="v-sem")
        monkeypatch.setattr(modulo, "destinatario_de", lambda convocacao: "")

        declarado = comunicar(edital, gestor, a, "v-sem-com")

        assert declarado["resultado"] == "FALHA"
        assert gravada(declarado) == do_carregador("inicial")
        assert len(caixa) == 0, "sem endereço, nada sai"

    def test_a_correcao_grava_o_modelo_da_correcao(self, caixa, cenario, gestor):
        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="v-corr")
        comunicar(edital, gestor, a, "v-corr-com")

        corrigir(edital, gestor, a, chave="v-corr-c")

        sucessora = ComunicacaoEmitida.objects.filter(convocacao__convocacao_anterior=a).get()
        assert sucessora.modelo_da_mensagem == do_carregador("correcao") == do_disco("correcao")

    def test_a_publicacao_nao_tem_modelo(self, caixa, cenario_por_publicacao, gestor):
        edital, _, _ = cenario_por_publicacao
        a = chamar(edital, gestor, chave="v-pub")

        declarado = comunicar(
            edital, gestor, a, "v-pub-com", referencia_da_publicacao="https://ex.test, 05/11/2026"
        )

        assert gravada(declarado) == ""

    def test_a_repeticao_nao_grava_identificacao_nova(self, caixa, cenario, gestor):
        """`FR-3888`: a repetição concluída não grava linha, e por isso nem identificação."""
        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="v-rep")
        comunicar(edital, gestor, a, "v-rep-com")
        antes = list(ComunicacaoEmitida.objects.values_list("id", "modelo_da_mensagem"))

        comunicar(edital, gestor, a, "v-rep-com")

        assert list(ComunicacaoEmitida.objects.values_list("id", "modelo_da_mensagem")) == antes


class TestAPreservacao:
    def test_o_modelo_trocado_muda_o_envio_seguinte_e_nao_o_anterior(
        self, caixa, cenario, gestor, tmp_path
    ):
        """`SC-1172`: um diretório de modelos à frente do app, com o HTML alterado."""
        edital, _, inscricoes = cenario
        a = chamar(edital, gestor, chave="v-pre")
        primeira = comunicar(edital, gestor, a, "v-pre-com")
        original = gravada(primeira)

        pasta = tmp_path / "convocacao" / "mensagem"
        pasta.mkdir(parents=True)
        for arquivo in MODELOS.iterdir():
            shutil.copy(arquivo, pasta / arquivo.name)
        alterado = pasta / "inicial.html"
        alterado.write_text(
            alterado.read_text(encoding="utf-8").replace("Para a sua segurança", "Segurança"),
            encoding="utf-8",
        )
        modelos = [dict(django_settings.TEMPLATES[0])]
        modelos[0]["DIRS"] = [tmp_path, *modelos[0]["DIRS"]]

        with override_settings(TEMPLATES=modelos):
            segunda = comunicar(edital, gestor, a, "v-pre-de-novo")
            esperado = resumo(
                "inicial",
                alterado.read_text(encoding="utf-8"),
                (pasta / "inicial.txt").read_text(encoding="utf-8"),
            )

        assert gravada(segunda) == esperado != original
        assert gravada(primeira) == original, "o já gravado não muda"
        assert "Segurança" in caixa[-1].alternatives[0][0]


class TestSemRetroatividade:
    def test_a_linha_gravada_sem_a_coluna_le_vazio(self, cenario, gestor):
        """A comunicação gravada pela forma anterior à `121` fica sem identificação."""
        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="v-ret")

        anterior = ComunicacaoEmitida.objects.create(
            convocacao=a,
            forma="INDIVIDUAL_MESSAGE",
            destinatario="pessoa@exemplo.test",
            enviado_em=timezone.now(),
            resultado="ENVIADA",
        )

        assert ComunicacaoEmitida.objects.get(id=anterior.id).modelo_da_mensagem == ""

    def test_a_migration_so_acrescenta_a_coluna(self):
        """Sem `RunPython`, sem `UPDATE`: nenhuma linha anterior recebe valor (FR-3889)."""
        from importlib import import_module

        from django.db import migrations

        migration = import_module(
            "processo_seletivo.convocacao.migrations.0006_modelo_da_mensagem"
        ).Migration
        assert [type(op) for op in migration.operations] == [migrations.AddField]
        campo = migration.operations[0].field
        assert (migration.operations[0].name, campo.default, campo.blank) == (
            "modelo_da_mensagem",
            "",
            True,
        )


class TestRecuperavelPeloGit:
    """`FR-3889`: os modelos são versionados, nunca gerados nem ignorados."""

    ARQUIVOS = (
        *(
            MODELOS / nome
            for nome in ("inicial.html", "inicial.txt", "correcao.html", "correcao.txt")
        ),
        ESTILOS,
    )

    @pytest.fixture
    def git(self):
        if shutil.which("git") is None or not (RAIZ.parent / ".git").exists():
            pytest.skip("sem o repositório Git: a conferência é do checkout com histórico")

        def rodar(*argumentos):
            return subprocess.run(
                ["git", *argumentos], cwd=RAIZ.parent, capture_output=True, text=True
            )

        return rodar

    @pytest.mark.parametrize("arquivo", ARQUIVOS, ids=lambda caminho: caminho.name)
    def test_no_indice_e_nao_ignorado(self, git, arquivo):
        caminho = str(arquivo.relative_to(RAIZ.parent))

        assert git("ls-files", "--error-unmatch", caminho).returncode == 0, caminho
        assert git("check-ignore", caminho).stdout == "", caminho


class TestAFalhaNaMontagem:
    """A chave já está reservada quando a mensagem se monta: nada pode subir dali sem registro, ou
    a reserva ficaria aberta e cada nova tentativa diria "estado indeterminado"."""

    def test_a_escolha_que_quebra_vira_falha_gravada(self, caixa, cenario, gestor, monkeypatch):
        from processo_seletivo.convocacao.application import comunicar as modulo

        def quebrar(convocacao, *, instante):
            raise RuntimeError("banco fora")

        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="m-escolha")
        monkeypatch.setattr(modulo, "escolha_de", quebrar)

        declarado = comunicar(edital, gestor, a, "m-escolha-com")

        emitida = ComunicacaoEmitida.objects.get(id=declarado["id"])
        assert (emitida.resultado, emitida.modelo_da_mensagem) == ("FALHA", "")
        assert "falha na montagem da mensagem" in emitida.detalhe_tecnico
        assert len(caixa) == 0

    def test_a_renderizacao_que_quebra_grava_o_modelo(self, caixa, cenario, gestor, monkeypatch):
        from processo_seletivo.convocacao.application import comunicar as modulo

        def quebrar(dados):
            raise KeyError("link")

        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="m-render")
        monkeypatch.setattr(modulo, "_contexto", quebrar)

        declarado = comunicar(edital, gestor, a, "m-render-com")

        emitida = ComunicacaoEmitida.objects.get(id=declarado["id"])
        assert emitida.resultado == "FALHA"
        assert emitida.modelo_da_mensagem == do_carregador("inicial"), "o modelo carregou"

    def test_o_modelo_que_nao_carrega_vira_falha(self, caixa, cenario, gestor, tmp_path):
        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="m-modelo")
        pasta = tmp_path / "convocacao" / "mensagem"
        pasta.mkdir(parents=True)
        (pasta / "inicial.html").write_text("{% if %}", encoding="utf-8")
        modelos = [dict(django_settings.TEMPLATES[0])]
        modelos[0]["DIRS"] = [tmp_path, *modelos[0]["DIRS"]]

        with override_settings(TEMPLATES=modelos):
            declarado = comunicar(edital, gestor, a, "m-modelo-com")

        emitida = ComunicacaoEmitida.objects.get(id=declarado["id"])
        assert (emitida.resultado, emitida.modelo_da_mensagem) == ("FALHA", "")

        # A chave não ficou presa: outra emissão, com a chave nova da tela, sai.
        declarado = comunicar(edital, gestor, a, "m-modelo-de-novo")
        assert declarado["resultado"] == "ENVIADA"


class TestOsEstilosEntramNoResumo:
    """O mapa de estilos decide o HTML que sai, e entra no resumo (R-009, revista em 13/11).

    Sem ele, mudar uma cor mudava a mensagem sem mudar o resumo gravado, e a conferência pelo Git
    apontaria um commit cujo HTML não é o que saiu.
    """

    def test_o_resumo_gravado_e_o_das_tres_fontes(self, caixa, cenario, gestor):
        edital, _, _ = cenario
        declarado = comunicar(edital, gestor, chamar(edital, gestor, chave="estilos"), "estilos-c")

        assert gravada(declarado) == do_disco("inicial")
        assert gravada(declarado) != resumo(
            "inicial",
            (MODELOS / "inicial.html").read_text(encoding="utf-8"),
            (MODELOS / "inicial.txt").read_text(encoding="utf-8"),
            estilos="",
        )

    def test_o_resumo_usa_a_mesma_leitura_que_estiliza(self):
        from processo_seletivo.shared import correio

        assert correio.CAMINHO_DOS_ESTILOS == ESTILOS
        assert correio.FONTE_DOS_ESTILOS == ESTILOS.read_text(encoding="utf-8")
        assert correio.ESTILOS == json.loads(correio.FONTE_DOS_ESTILOS)
