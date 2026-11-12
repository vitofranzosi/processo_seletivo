"""A verificação e o download do pacote (117, US4, FR-3682 a FR-3698, SC-1105, SC-1107, SC-1108).

Pelo cliente do Django, com as telas: a verificação mostra o resultado antes de qualquer download,
e o download serve exatamente o verificado. Cada uma das cinco mudanças da FR-3689b entre os dois
passos é verificação defasada, sem servir nada e sem registro (SC-1113).
"""

import re

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.formalizacao.models import (
    ExportacaoDeFormalizacao,
    RevogacaoDaDesignacao,
)
from tests.fixtures.documentos_da_convocacao import IDENTIDADE
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.formalizacao import definir_documentos, designar_direto, servido
from tests.integration.formalizacao.apoio import (
    abrir_zip,
    adulterar,
    apagar,
    baixar,
    comprovante_da,
    contar_leituras,
    documentos_de,
    exportar_pessoa,
    guardar,
    manifesto,
    pastas,
    restaurar,
    sha,
    verificar,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def pronto(cenario, gestor, client, seletor):
    """Definição do Cenário A, Rui designado sem restrição e identificado no cliente."""
    definir_documentos(cenario.edital, gestor)
    designar_direto(cenario.edital, "rui")
    identificar(client, "rui", ["formalizacao"])
    return cenario


def _verificado(client, cenario, **dados):
    resposta = verificar(client, cenario.edital, **dados)
    assert resposta.status_code == 200, resposta.content.decode()[:2000]
    return resposta, comprovante_da(resposta)


def test_a_lista_comeca_sem_marcacao(pronto, client):
    """FR-3683: nenhuma pessoa pré-selecionada."""
    corpo = client.get(
        reverse("interface:formalizacao-edital", args=[pronto.edital.id])
    ).content.decode()
    assert 'name="pessoa"' in corpo
    assert "checked" not in corpo


def test_completo_mostra_o_resultado_e_o_zip_tem_o_verificado(pronto, client):
    resposta, comprovante = _verificado(client, pronto)
    corpo = resposta.content.decode()
    assert "Pacote completo: 5 de 5 pessoas incluídas" in corpo
    assert "Baixar pacote (5 pessoas)" in corpo
    assert corpo.index("Pacote completo") < corpo.index("Incluídas")

    download = baixar(client, pronto.edital, comprovante)
    assert download.status_code == 200
    assert download["Content-Disposition"].startswith("attachment;")
    assert "-parcial" not in download["Content-Disposition"]
    assert "no-store" in download["Cache-Control"]
    pacote = abrir_zip(download)
    assert len(pastas(pacote)) == 5
    assert len([n for n in pacote.namelist() if n != "manifesto.csv"]) == 20
    cabecalho, colunas, linhas = manifesto(pacote)
    assert cabecalho["Resultado"] == "Pacote completo: 5 de 5 pessoas incluídas"
    assert "CPF" not in colunas
    assert len(linhas) == 20
    registro = ExportacaoDeFormalizacao.objects.get()
    assert registro.resultado == nomes.COMPLETO
    assert registro.alcance == nomes.RECORTE
    # **Cada tamanho diz de que é** (problema novo N-06 da reavaliação de 12/11/2026): a
    # verificação soma os documentos, e o histórico mede o ZIP com o manifesto.
    assert re.search(r"20 documentos, \d+ (KB|MB) somados", corpo)
    historico = client.get(
        reverse("interface:formalizacao-edital", args=[pronto.edital.id])
    ).content.decode()
    assert re.search(r"20 arquivos · pacote de \d+ (KB|MB), com o manifesto", historico)


def test_o_sha256_de_cada_arquivo_e_do_pacote_confere(pronto, client):
    """SC-1107: cada arquivo bate com o manifesto e com o esperado; o pacote, com o registro."""
    _, comprovante = _verificado(client, pronto)
    download = baixar(client, pronto.edital, comprovante)
    conteudo = servido(download)
    import io
    import zipfile

    pacote = zipfile.ZipFile(io.BytesIO(conteudo))
    _, colunas, linhas = manifesto(pacote)
    caminho, resumo = colunas.index("Caminho no pacote"), colunas.index("SHA-256")
    for linha in linhas:
        assert sha(pacote.read(linha[caminho])) == linha[resumo]
    registro = ExportacaoDeFormalizacao.objects.get()
    assert sha(conteudo) == registro.hash_do_pacote
    assert len(conteudo) == registro.tamanho
    esperados = {d["sha256"] for d in registro.documentos}
    assert {linha[resumo] for linha in linhas} == esperados


def test_duas_exportacoes_iguais_dao_entradas_identicas(pronto, client):
    """SC-1108: sem mudança, as entradas de documento são idênticas byte a byte."""
    _, comprovante = _verificado(client, pronto)
    primeiro = abrir_zip(baixar(client, pronto.edital, comprovante))
    segundo = abrir_zip(baixar(client, pronto.edital, comprovante))

    nomes_do_primeiro = [n for n in primeiro.namelist() if n != "manifesto.csv"]
    assert nomes_do_primeiro == [n for n in segundo.namelist() if n != "manifesto.csv"]
    for nome in nomes_do_primeiro:
        a, b = primeiro.getinfo(nome), segundo.getinfo(nome)
        assert (a.date_time, a.external_attr, a.compress_type, a.flag_bits) == (
            b.date_time,
            b.external_attr,
            b.compress_type,
            b.flag_bits,
        )
        assert primeiro.read(nome) == segundo.read(nome)
    assert ExportacaoDeFormalizacao.objects.count() == 2


def test_parcial_nomeia_os_excluidos_antes_do_download(pronto, client):
    """SC-1105: 1 ausente e 1 divergente em 5 — 3 de 5, os dois nomeados, ZIP `-parcial`."""
    ausente, divergente = pronto.aptas[0][0], pronto.aptas[1][0]
    apagar(documentos_de(pronto.edital, ausente)[0])
    adulterar(documentos_de(pronto.edital, divergente)[2])

    resposta, comprovante = _verificado(client, pronto)
    corpo = resposta.content.decode()
    assert "Pacote parcial: 3 de 5 pessoas incluídas" in corpo
    assert f"{ausente.protocolo} {ausente.nome}" in corpo
    assert "arquivo indisponível" in corpo
    assert f"{divergente.protocolo} {divergente.nome}" in corpo
    assert "arquivo diferente do conferido" in corpo
    assert "Baixar pacote parcial (3 pessoas)" in corpo

    download = baixar(client, pronto.edital, comprovante)
    assert download.status_code == 200
    assert download["Content-Disposition"].endswith('-parcial.zip"')
    pacote = abrir_zip(download)
    assert len(pastas(pacote)) == 3
    assert not any(ausente.protocolo in nome for nome in pacote.namelist())
    cabecalho, colunas, linhas = manifesto(pacote)
    assert cabecalho["Resultado"] == "Pacote parcial: 3 de 5 pessoas incluídas"
    situacao, caminho = colunas.index("Situação"), colunas.index("Caminho no pacote")
    do_ausente = [linha for linha in linhas if linha[0] == ausente.protocolo]
    assert len(do_ausente) == 4
    assert {linha[caminho] for linha in do_ausente} == {""}
    assert "arquivo indisponível" in {linha[situacao] for linha in do_ausente}
    do_divergente = [linha for linha in linhas if linha[0] == divergente.protocolo]
    assert "arquivo diferente do conferido" in {linha[situacao] for linha in do_divergente}

    registro = ExportacaoDeFormalizacao.objects.get()
    assert registro.resultado == nomes.PARCIAL
    motivos = {p["inscricao"]: p.get("motivo") for p in registro.nao_incluidas}
    assert motivos == {str(ausente.id): "INDISPONIVEL", str(divergente.id): "INTEGRIDADE"}
    historico = client.get(
        reverse("interface:formalizacao-edital", args=[pronto.edital.id])
    ).content.decode()
    assert "Pacote parcial: 3 de 5 pessoas incluídas" in historico


def test_a_selecao_exporta_so_as_marcadas(pronto, client):
    marcadas = [str(i.id) for i in pronto.inscricoes_aptas[:2]]
    resposta, comprovante = _verificado(client, pronto, alcance="selecao", pessoa=marcadas)
    assert "Pacote completo: 2 de 2 pessoas incluídas" in resposta.content.decode()

    pacote = abrir_zip(baixar(client, pronto.edital, comprovante))
    assert len(pastas(pacote)) == 2
    assert ExportacaoDeFormalizacao.objects.get().alcance == nomes.SELECAO


def test_o_recorte_por_perfil(pronto, client):
    resposta, _ = _verificado(client, pronto, alcance="todos", perfil=str(PROFILE_ID))
    assert "Pacote completo: 5 de 5" in resposta.content.decode()

    fora = verificar(
        client, pronto.edital, alcance="todos", perfil="00000000-0000-0000-0000-00000000abcd"
    )
    assert fora.status_code == 404


def test_post_forjado_com_pessoa_fora_do_alcance_recusa_tudo(pronto, client, monkeypatch):
    """FR-3682: um id que não é de pessoa apta derruba a operação inteira, sem ler nada."""
    lidas = contar_leituras(monkeypatch)
    indeferida = pronto.indeferidas[0][0]
    resposta = verificar(
        client,
        pronto.edital,
        alcance="selecao",
        pessoa=[str(pronto.inscricoes_aptas[0].id), str(indeferida.id)],
    )
    assert resposta.status_code == 404
    assert lidas == []
    assert not RegistroAuditoria.objects.filter(operation=nomes.VERIFICAR).exists()


def test_pessoa_unica_completa_sai_num_clique(pronto, client):
    inscricao = pronto.inscricoes_aptas[0]
    resposta = exportar_pessoa(client, pronto.edital, inscricao)

    assert resposta.status_code == 200
    pacote = abrir_zip(resposta)
    assert pastas(pacote) == [f"{inscricao.protocolo} {inscricao.nome}"]
    registro = ExportacaoDeFormalizacao.objects.get()
    assert (registro.alcance, registro.resultado) == (nomes.PESSOA, nomes.COMPLETO)


def test_pessoa_unica_com_falha_recebe_pagina_e_nada_e_registrado(pronto, client):
    """FR-3685: com falha, uma página com o motivo, e não um ZIP; nenhum registro."""
    inscricao = pronto.inscricoes_aptas[0]
    apagar(documentos_de(pronto.edital, inscricao)[1])
    resposta = exportar_pessoa(client, pronto.edital, inscricao)

    assert resposta.status_code == 409
    assert resposta["Content-Type"].startswith("text/html")
    corpo = resposta.content.decode()
    assert "O pacote desta pessoa não foi gerado" in corpo
    assert "arquivo indisponível" in corpo
    assert not ExportacaoDeFormalizacao.objects.exists()
    recusa = RegistroAuditoria.objects.get(operation=nomes.RECUSAR)
    assert recusa.reason == nomes.RECUSA_PESSOA_INCOMPLETA


def test_verificacao_sem_pessoa_incluivel_nao_tem_botao(pronto, client):
    for inscricao in pronto.inscricoes_aptas:
        apagar(documentos_de(pronto.edital, inscricao)[0])
    resposta, comprovante = _verificado(client, pronto)

    corpo = resposta.content.decode()
    assert "Nenhuma pessoa pode entrar no pacote" in corpo
    assert "Baixar pacote" not in corpo
    assert comprovante is None
    assert not ExportacaoDeFormalizacao.objects.exists()


def _apta_sem_titulos(cenario, gestor):
    from tests.fixtures.formalizacao import (
        CERTIFICADO_DO_CURSO,
        convocar_direto,
        inscrever,
        tornar_apta,
    )

    inscricao = inscrever(cenario.edital, 900, documentos=(IDENTIDADE, CERTIFICADO_DO_CURSO))
    tornar_apta(
        cenario.edital, gestor, inscricao, convocar_direto(cenario.edital, inscricao), numero=900
    )
    return inscricao


def test_quem_nao_tem_documento_a_exportar_nao_entra_na_exportacao(pronto, client, gestor):
    """Revisão do PR #373: a apta sem documento definido aplicável não é "incluída" num pacote."""
    from tests.fixtures.formalizacao import TITULOS

    sem_titulos = _apta_sem_titulos(pronto, gestor)
    definir_documentos(pronto.edital, gestor, requisitos=[TITULOS], motivo="Só os títulos")
    apagar(documentos_de(pronto.edital, pronto.inscricoes_aptas[0])[0])

    resposta, comprovante = _verificado(client, pronto)
    corpo = resposta.content.decode()
    assert "Pacote parcial: 4 de 5 pessoas incluídas" in corpo
    assert sem_titulos.protocolo not in corpo

    download = baixar(client, pronto.edital, comprovante)
    assert download.status_code == 200
    abrir_zip(download)
    registro = ExportacaoDeFormalizacao.objects.get()
    assert str(sem_titulos.id) not in {p["inscricao"] for p in registro.pessoas}
    assert registro.quantidade_de_arquivos == 4


def test_so_quem_nao_tem_documento_sobra_e_nao_ha_o_que_baixar(pronto, client, gestor):
    """O caso que derrubava o download: as demais excluídas, e só a sem documento "incluída"."""
    from tests.fixtures.formalizacao import TITULOS

    _apta_sem_titulos(pronto, gestor)
    definir_documentos(pronto.edital, gestor, requisitos=[TITULOS], motivo="Só os títulos")
    for inscricao in pronto.inscricoes_aptas:
        apagar(documentos_de(pronto.edital, inscricao)[0])

    resposta, comprovante = _verificado(client, pronto)
    corpo = resposta.content.decode()
    assert "Pacote parcial: 0 de 5 pessoas incluídas" in corpo
    assert "Baixar pacote" not in corpo
    assert comprovante is None
    assert not RegistroAuditoria.objects.filter(operation=nomes.INTERROMPER).exists()


# --- A verificação defasada: as cinco mudanças da FR-3689b ---------------------------------------


def _defasada(client, cenario, comprovante):
    resposta = baixar(client, cenario.edital, comprovante)
    assert resposta.status_code == 409, resposta.status_code
    assert resposta["Content-Type"].startswith("text/html")
    corpo = resposta.content.decode()
    assert "Algo mudou desde a verificação" in corpo
    assert "Verificar de novo" in corpo
    assert not ExportacaoDeFormalizacao.objects.exists()
    assert RegistroAuditoria.objects.filter(
        operation=nomes.RECUSAR, reason=nomes.RECUSA_DEFASADA
    ).exists()


def test_defasada_pelo_desfecho(pronto, client, gestor):
    _, comprovante = _verificado(client, pronto)
    _, convocacao = pronto.aptas[2]
    desfechar(
        actor=gestor,
        processo_id=pronto.edital.processo_id,
        convocacao_id=convocacao.id,
        especie=nomes_da_convocacao.INDEFERIMENTO,
        fundamento="Correção.",
        motivo="Aceite registrado por engano",
        idempotency_key="defasa-117",
        correlation_id="teste-117",
    )
    _defasada(client, pronto, comprovante)


def test_defasada_pela_designacao_revogada_e_concedida_de_novo(pronto, client):
    _, comprovante = _verificado(client, pronto)
    designacao = pronto.edital.designacoes_da_formalizacao.get()
    RevogacaoDaDesignacao.objects.create(
        designacao=designacao,
        motivo="Troca",
        revogado_por="gil",
        unidade_de_atuacao="cefor",
        revogado_em=timezone.now(),
    )
    designar_direto(pronto.edital, "rui")
    _defasada(client, pronto, comprovante)


def test_defasada_pela_definicao(pronto, client, gestor):
    _, comprovante = _verificado(client, pronto)
    definir_documentos(pronto.edital, gestor, requisitos=[IDENTIDADE], motivo="Minimização")
    _defasada(client, pronto, comprovante)


def test_defasada_pelo_arquivo_trocado(pronto, client):
    _, comprovante = _verificado(client, pronto)
    adulterar(documentos_de(pronto.edital, pronto.inscricoes_aptas[3])[1])
    _defasada(client, pronto, comprovante)


def test_defasada_pelo_excluido_restaurado(pronto, client):
    """Caso-limite: a pessoa excluída por arquivo ausente teria o arquivo de volta (FR-3689b)."""
    documento = documentos_de(pronto.edital, pronto.inscricoes_aptas[0])[0]
    original = guardar(documento)
    apagar(documento)
    resposta, comprovante = _verificado(client, pronto)
    assert "Pacote parcial: 4 de 5" in resposta.content.decode()

    restaurar(documento, original)
    _defasada(client, pronto, comprovante)


def test_defasada_pelo_motivo_trocado(pronto, client):
    documento = documentos_de(pronto.edital, pronto.inscricoes_aptas[0])[0]
    original = guardar(documento)
    apagar(documento)
    _, comprovante = _verificado(client, pronto)

    restaurar(documento, original + b"diferente")
    _defasada(client, pronto, comprovante)


def test_a_revogacao_da_designacao_entre_os_passos_e_inexistente(pronto, client, monkeypatch):
    """A revogação dá a recusa da matriz, e não a defasada (US4, cenário 3)."""
    _, comprovante = _verificado(client, pronto)
    RevogacaoDaDesignacao.objects.create(
        designacao=pronto.edital.designacoes_da_formalizacao.get(),
        motivo="Saiu",
        revogado_por="gil",
        unidade_de_atuacao="cefor",
        revogado_em=timezone.now(),
    )
    lidas = contar_leituras(monkeypatch)
    assert baixar(client, pronto.edital, comprovante).status_code == 404
    assert lidas == []
