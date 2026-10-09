"""As variáveis do aviso: lista fechada, valor por origem, sem linguagem de template (`FR-1255`).

**O modo de errar aqui é silencioso.** Uma variável sem valor que passasse viraria `{etapa}` literal
na caixa de quinhentas pessoas; uma variável sensível aceita viraria dado pessoal numa mensagem que
é encaminhada. As duas falhas aparecem depois do envio, que não se desfaz.
"""

import pytest

from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.domain.variaveis import (
    VARIAVEIS,
    escapar,
    resolver,
    resolver_no_envio,
    usadas,
    validar,
)
from processo_seletivo.shared.api.problems import DomainError

SENSIVEIS = ("posicao", "pontuacao", "modalidade", "lista", "motivo", "cpf", "telefone", "situacao")


@pytest.mark.parametrize("nome", sorted(VARIAVEIS))
def test_toda_variavel_da_lista_vale_num_modelo(nome):
    validar(f"Texto com {{{nome}}}.")


@pytest.mark.parametrize("nome", SENSIVEIS)
def test_variavel_sensivel_nao_existe(nome):
    with pytest.raises(DomainError) as erro:
        validar(f"Sua {{{nome}}} é esta.")

    assert erro.value.code == nomes.AVISO_VARIAVEL_DESCONHECIDA
    assert nome in erro.value.detail


@pytest.mark.parametrize(
    ("nome", "origem"),
    [
        ("etapa", nomes.CHAMADA),
        ("natureza_do_resultado", nomes.CHAMADA),
        ("link_da_publicacao", nomes.CHAMADA),
        ("referencia_da_publicacao", nomes.RESULTADO),
    ],
)
def test_variavel_sem_valor_na_origem_e_recusada(nome, origem):
    with pytest.raises(DomainError) as erro:
        validar(f"{{{nome}}}", origem=origem, publicacoes_citadas=1)

    assert erro.value.code == nomes.AVISO_VARIAVEL_SEM_VALOR
    assert nome in erro.value.detail


@pytest.mark.parametrize(
    "nome", [nome for nome, origens in VARIAVEIS.items() if nomes.CHAMADA in origens]
)
def test_as_variaveis_da_chamada_valem_na_chamada(nome):
    validar(f"{{{nome}}}", origem=nomes.CHAMADA)


def test_link_da_publicacao_so_com_uma_publicacao():
    """Com várias publicações não há URL inequívoca, e a recusa sugere a página (`R-008`)."""
    validar("{link_da_publicacao}", origem=nomes.RESULTADO, publicacoes_citadas=1)

    with pytest.raises(DomainError) as erro:
        validar("{link_da_publicacao}", origem=nomes.RESULTADO, publicacoes_citadas=2)

    assert erro.value.code == nomes.AVISO_VARIAVEL_SEM_VALOR
    assert "pagina_do_processo_seletivo" in erro.value.detail


def test_chaves_duplicadas_sao_literais_e_nao_variavel():
    assert usadas("Use {{assim}} e {edital}.") == ["edital"]
    validar("{{qualquer_coisa}} literal")


def test_nao_ha_atributo_nem_expressao():
    """`{edital.title}` não é acesso a atributo: não é variável, e fica como texto."""
    assert usadas("{edital.title} {perfil|upper} {% if %}") == []


def test_resolver_mantem_o_nome_e_as_chaves_literais():
    texto = "Olá, {nome_do_candidato}. {edital} saiu. {{literal}}"

    congelado = resolver(texto, {"edital": "Edital nº 57/2026"})

    assert congelado == "Olá, {nome_do_candidato}. Edital nº 57/2026 saiu. {{literal}}"


def test_valor_com_chaves_chega_como_foi_escrito():
    congelado = resolver("Perfil {perfil}", {"perfil": "Técnico {A} {nome_do_candidato}"})

    final = resolver_no_envio(congelado, nome_do_candidato="Maria")

    assert final == "Perfil Técnico {A} {nome_do_candidato}"


def test_no_envio_so_o_nome_muda():
    final = resolver_no_envio("Olá, {nome_do_candidato}. {{x}}", nome_do_candidato="Maria")

    assert final == "Olá, Maria. {x}"


def test_escapar_dobra_as_chaves():
    assert escapar("a{b}c") == "a{{b}}c"
