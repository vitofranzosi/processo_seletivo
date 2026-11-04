"""Nada sobra no disco e a trava sai, em todo desfecho da operação (117, FR-3688, FR-3692, SC-1106).

**Transacional**, porque a trava é de transação: num caso que termina em `ROLLBACK` ela ficaria
presa até o fim do teste, e "está livre depois" não seria observável. Pela mesma razão, a trava é
conferida de **outra conexão**, como outro worker a veria.
"""

import pytest
from django.db import connection
from django.utils import timezone

from processo_seletivo.formalizacao.application import exportar
from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.formalizacao.infrastructure import pacote as modulo_do_pacote
from processo_seletivo.formalizacao.models import ExportacaoDeFormalizacao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.formalizacao import (
    definir_documentos,
    designar_direto,
    falhar_na_montagem,
    montar_cenario_da_formalizacao,
    servido,
)
from tests.integration.formalizacao.apoio import apagar, documentos_de

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def _postgresql():
    if connection.vendor != "postgresql":
        pytest.skip("trava consultiva só no PostgreSQL")


def outra_conexao():
    """Uma conexão nova ao banco de teste, fora da do Django — a de outro worker."""
    import psycopg

    dados = connection.get_connection_params()
    dados.pop("cursor_factory", None)
    dados.pop("context", None)
    return psycopg.connect(**dados, autocommit=True)


def trava_livre(subject="rui"):
    with outra_conexao() as conexao:
        livre = conexao.execute(
            "SELECT pg_try_advisory_lock(%s, %s)",
            [nomes.CLASSE_DA_TRAVA, nomes.chave_da_trava(subject)],
        ).fetchone()[0]
        if livre:
            conexao.execute(
                "SELECT pg_advisory_unlock(%s, %s)",
                [nomes.CLASSE_DA_TRAVA, nomes.chave_da_trava(subject)],
            )
    return livre


def arquivos_sob(raiz):
    from pathlib import Path

    return sorted(str(p) for p in Path(raiz).rglob("*") if p.is_file())


@pytest.fixture
def pronto(gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    cenario = montar_cenario_da_formalizacao(
        gestor, api_client, manager_headers, process_payload, aptas=3, prefixo="ciclo-117"
    )
    definir_documentos(cenario.edital, gestor)
    designar_direto(cenario.edital, "rui")
    return cenario


@pytest.fixture
def pacotes(monkeypatch):
    """Cada `Pacote` criado, para conferir que o temporário de cada um foi fechado."""
    criados = []
    original = modulo_do_pacote.Pacote.__init__

    def iniciar(self):
        original(self)
        criados.append(self)

    monkeypatch.setattr(modulo_do_pacote.Pacote, "__init__", iniciar)
    return criados


def test_o_temporario_nao_tem_nome_no_disco(pacotes, pronto, rui):
    """FR-3688: `TemporaryFile` sem caminho legível; o nome é o descritor, e não um arquivo."""
    _postgresql()
    _, comprovante = exportar.verificar(rui, edital_id=pronto.edital.id, alcance=nomes.RECORTE)
    gerado = exportar.baixar(rui, edital_id=pronto.edital.id, token=comprovante)
    try:
        assert isinstance(gerado.arquivo.name, int)
    finally:
        gerado.arquivo.close()


def test_sucesso_fecha_o_temporario_solta_a_trava_e_nada_sobra(
    pacotes, pronto, rui, raiz_de_arquivos, client, settings
):
    _postgresql()
    from django.urls import reverse

    from tests.interface.conftest import identificar

    antes = arquivos_sob(raiz_de_arquivos)
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, "rui", ["formalizacao"])
    resposta = client.post(
        reverse("interface:formalizacao-verificar", args=[pronto.edital.id]), {"alcance": "todos"}
    )
    import re

    comprovante = re.search(r'name="comprovante" value="([^"]+)"', resposta.content.decode())
    download = client.post(
        reverse("interface:formalizacao-baixar", args=[pronto.edital.id]),
        {"comprovante": comprovante.group(1)},
    )
    assert trava_livre(), "a trava sai no commit, antes da transferência"
    servido(download)

    assert all(p.arquivo.closed for p in pacotes)
    assert arquivos_sob(raiz_de_arquivos) == antes
    assert ExportacaoDeFormalizacao.objects.count() == 1


def test_recusa_solta_a_trava_e_nada_sobra(pacotes, pronto, rui, raiz_de_arquivos):
    _postgresql()
    antes = arquivos_sob(raiz_de_arquivos)
    _, comprovante = exportar.verificar(rui, edital_id=pronto.edital.id, alcance=nomes.RECORTE)
    definir_documentos(pronto.edital, _gestor(), motivo="Outra")

    with pytest.raises(exportar.VerificacaoDefasada):
        exportar.baixar(rui, edital_id=pronto.edital.id, token=comprovante)

    assert trava_livre()
    assert all(p.arquivo.closed for p in pacotes)
    assert arquivos_sob(raiz_de_arquivos) == antes
    assert not ExportacaoDeFormalizacao.objects.exists()


def test_excecao_injetada_desfaz_fecha_e_solta(pacotes, pronto, rui, monkeypatch):
    """FR-3714, SC-1106: o registro está ausente quando a montagem não comita."""
    _postgresql()
    _, comprovante = exportar.verificar(rui, edital_id=pronto.edital.id, alcance=nomes.RECORTE)
    falhar_na_montagem(monkeypatch)

    with pytest.raises(exportar.ExportacaoInterrompida):
        exportar.baixar(rui, edital_id=pronto.edital.id, token=comprovante)

    assert pacotes and all(p.arquivo.closed for p in pacotes)
    assert trava_livre()
    assert not ExportacaoDeFormalizacao.objects.exists()


def test_o_cliente_que_desconecta_fecha_o_temporario_e_o_registro_continua(pacotes, pronto, rui):
    """FR-3698: a transferência cortada não altera o registro, que diz só *disponibilizado*.

    A desconexão é o servidor fechando a resposta sem ter enviado tudo: o `FileResponse` fecha o
    arquivo, e o temporário sem nome deixa de existir.
    """
    _postgresql()
    from django.http import FileResponse

    _, comprovante = exportar.verificar(rui, edital_id=pronto.edital.id, alcance=nomes.RECORTE)
    gerado = exportar.baixar(rui, edital_id=pronto.edital.id, token=comprovante)
    resposta = FileResponse(gerado.arquivo, as_attachment=True, filename=gerado.nome)
    next(iter(resposta.streaming_content))
    for fechar in resposta._resource_closers:
        fechar()

    assert gerado.arquivo.closed
    assert ExportacaoDeFormalizacao.objects.get().resultado == nomes.COMPLETO
    assert trava_livre()


def test_a_conexao_fechada_solta_a_trava():
    """FR-3692: a trava de transação sai com a conexão, inclusive com o processo morto."""
    _postgresql()
    conexao = outra_conexao()
    conexao.autocommit = False
    conexao.execute(
        "SELECT pg_try_advisory_xact_lock(%s, %s)",
        [nomes.CLASSE_DA_TRAVA, nomes.chave_da_trava("rui")],
    )
    assert not trava_livre()
    conexao.close()
    assert trava_livre()


def test_arquivo_ausente_nao_deixa_temporario_aberto(pacotes, pronto, rui):
    _postgresql()
    apagar(documentos_de(pronto.edital, pronto.inscricoes_aptas[0])[0])
    with pytest.raises(DomainError):
        exportar.exportar_pessoa(
            rui, edital_id=pronto.edital.id, inscricao_id=pronto.inscricoes_aptas[0].id
        )
    assert pacotes and all(p.arquivo.closed for p in pacotes)
    assert trava_livre()


def _gestor():
    from tests.conftest import ator_institucional

    return ator_institucional("carlos", "comissao:gerir")


def test_o_registro_existe_so_depois_do_pacote(pronto, rui, monkeypatch):
    """FR-3698: gravado depois de o pacote estar montado e antes de a resposta começar."""
    _postgresql()
    _, comprovante = exportar.verificar(rui, edital_id=pronto.edital.id, alcance=nomes.RECORTE)
    momentos = []
    original = modulo_do_pacote.Pacote.fechar

    def fechar(self):
        momentos.append(("pacote", ExportacaoDeFormalizacao.objects.count()))
        return original(self)

    monkeypatch.setattr(modulo_do_pacote.Pacote, "fechar", fechar)
    gerado = exportar.baixar(rui, edital_id=pronto.edital.id, token=comprovante)
    gerado.arquivo.close()

    assert momentos == [("pacote", 0)]
    assert gerado.exportacao.exportado_em <= timezone.now()
