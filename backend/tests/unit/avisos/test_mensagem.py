"""A composição do aviso: texto da seleção, linha de retificação e rodapé (contracts/mensagem.md).

**O rodapé é o que impede o aviso de ser lido como o ato** (`FR-1257`), e a linha de retificação diz
que houve retificação sem dizer que algo mudou para a pessoa (`FR-1248`).
"""

from datetime import UTC, datetime

import pytest

from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.domain.mensagem import (
    CABECALHOS,
    FRASE_DA_CHAMADA,
    congelar,
    destino_oficial,
    para_a_pessoa,
    validar_texto,
)
from processo_seletivo.shared.api.problems import DomainError

VALORES = {"edital": "Edital nº 57/2026", "perfil": "Técnico em Secretaria", "etapa": "Análise"}


def _congelar(origem=nomes.RESULTADO, datas=(), destino="https://x/selecoes/1/"):
    return congelar(
        assunto="Processo Seletivo Ifes — Nova publicação disponível",
        corpo="Olá, {nome_do_candidato}. Saiu a {etapa} do {perfil}.",
        valores=VALORES,
        origem=origem,
        datas_retificadas=datas,
        destino=destino,
        atendimento="selecao@exemplo.test",
    )


def test_o_texto_congelado_guarda_tudo_menos_o_nome():
    assunto, corpo = _congelar()

    assert assunto == "Processo Seletivo Ifes — Nova publicação disponível"
    assert "Saiu a Análise do Técnico em Secretaria." in corpo
    assert "{nome_do_candidato}" in corpo


def test_o_rodape_aponta_a_publicacao_e_diz_que_o_aviso_nao_a_substitui():
    _, corpo = _congelar(destino="https://x/selecoes/resultados/9/")

    assert "A publicação oficial está em https://x/selecoes/resultados/9/" in corpo
    assert "é a referência para prazos e" in corpo
    assert "Este aviso não substitui a publicação." in corpo
    assert "Edital nº 57/2026" in corpo
    assert "selecao@exemplo.test" in corpo
    assert "Esta mensagem é automática; não responda." in corpo


def test_so_a_chamada_diz_que_o_prazo_nao_corre_do_aviso():
    _, resultado = _congelar(origem=nomes.RESULTADO)
    _, chamada = _congelar(origem=nomes.CHAMADA)

    assert FRASE_DA_CHAMADA.strip() not in resultado
    assert FRASE_DA_CHAMADA.strip() in chamada


def test_a_linha_de_retificacao_nomeia_as_datas_e_nao_afirma_mudanca():
    datas = (datetime(2026, 10, 6, 17, 0, tzinfo=UTC), datetime(2026, 10, 7, 13, 30, tzinfo=UTC))

    _, corpo = _congelar(datas=datas)

    assert "Este aviso se refere a publicação que retifica a de 06/10/2026 às 14:00" in corpo
    assert "07/10/2026 às 10:30" in corpo, "no fuso da instalação, e não em UTC"
    for frase in ("sua situação mudou", "você foi reclassificad", "sua posição"):
        assert frase not in corpo.lower()


def test_sem_retificacao_nao_ha_linha():
    _, corpo = _congelar()

    assert "retifica" not in corpo


def test_a_pessoa_recebe_o_nome_e_nada_mais_muda():
    assunto, corpo = _congelar()

    final_assunto, final_corpo = para_a_pessoa(
        assunto=assunto, corpo=corpo, nome_do_candidato="Maria Souza"
    )

    assert final_assunto == assunto
    assert final_corpo == corpo.replace("{nome_do_candidato}", "Maria Souza")


def test_nome_vazio_nao_deixa_variavel_na_mensagem():
    _, corpo = _congelar()

    _, final = para_a_pessoa(assunto="a", corpo=corpo, nome_do_candidato="")

    assert "{nome_do_candidato}" not in final


@pytest.mark.parametrize(
    ("link", "referencia", "pagina", "esperado"),
    [
        ("L", "R", "P", "L"),
        ("", "R", "P", "R"),
        ("", "", "P", "P"),
    ],
)
def test_destino_oficial_na_ordem(link, referencia, pagina, esperado):
    assert (
        destino_oficial(link_da_publicacao=link, referencia_da_publicacao=referencia, pagina=pagina)
        == esperado
    )


@pytest.mark.parametrize(
    ("assunto", "corpo", "campo"),
    [
        ("", "texto", "assunto"),
        ("duas\nlinhas", "texto", "assunto"),
        ("x" * 151, "texto", "assunto"),
        ("assunto", "  ", "corpo"),
        ("assunto", "x" * 5001, "corpo"),
    ],
)
def test_texto_invalido_e_recusado_com_o_campo(assunto, corpo, campo):
    with pytest.raises(DomainError) as erro:
        validar_texto(assunto=assunto, corpo=corpo)

    assert erro.value.code == nomes.AVISO_TEXTO_INVALIDO
    assert erro.value.campo == campo


def test_auto_submitted_em_toda_mensagem():
    assert CABECALHOS == {"Auto-Submitted": "auto-generated"}
