"""O que os bytes gravados contêm — e o que eles não podem conter (contracts/conteudo.md §4).

**A afirmação é sobre os bytes, e não sobre a intenção do código.** Um teste que inspecionasse o
dicionário devolvido pela composição verificaria o que o programa quis gravar; este verifica o que
ele gravou. É a diferença que importa quando alguém acrescenta um campo três features adiante.
"""

import json
import re
import uuid

import pytest

from processo_seletivo.divulgacao.models import SituacaoDivulgada
from processo_seletivo.shared.canonical import canonical_sha256
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato

pytestmark = [pytest.mark.contract, pytest.mark.django_db(transaction=True)]

UUID_EM_QUALQUER_LUGAR = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
# As grafias internas que a apresentação nunca deve carregar (FR-013).
ENUMS_CANONICOS = (
    "PRELIMINAR",
    "DEFINITIVA",
    "HABILITADA",
    "ELIMINADA",
    "CLASSIFICADA",
    "SEM_POSICAO",
)


@pytest.fixture
def publicada(gestor, api_client, manager_headers, process_payload):
    cenario = montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=52,
        codigo="0752",
        pontuacoes=("90.0000", "70.0000", None),
        primeiro=301,
    )
    return cenario, publicar_o_ato(cenario, chave="publicar-0752")


def _bytes_gravados(publicacao):
    return bytes(publicacao.conteudo_publico)


def _texto(publicacao):
    return _bytes_gravados(publicacao).decode("utf-8")


def test_o_conteudo_nao_contem_dado_pessoal_interno(publicada):
    """CPF, e-mail e `identity_subject` não atravessam a fronteira (FR-019, SC-015)."""
    cenario, publicacao = publicada
    texto = _texto(publicacao)

    for inscricao in cenario["inscricoes"]:
        assert inscricao.cpf not in texto
        assert inscricao.cpf_normalizado not in texto
        assert inscricao.email not in texto
        assert inscricao.identity_subject not in texto


def test_o_conteudo_nao_contem_identificador_de_inscricao(publicada):
    """O protocolo identifica publicamente; o UUID da Inscrição é interno (FR-018)."""
    cenario, publicacao = publicada
    texto = _texto(publicacao)

    for inscricao in cenario["inscricoes"]:
        assert str(inscricao.id) not in texto


def test_o_unico_uuid_do_conteudo_e_o_do_ato_de_origem(publicada):
    """`cabecalho.ato.id` é a única identidade técnica que o conteúdo carrega (FR-019).

    Ela fica porque é o vínculo com a decisão divulgada, e porque não descreve pessoa nenhuma.
    Qualquer outro UUID nos bytes seria identificador vazando para a superfície pública.
    """
    _, publicacao = publicada
    conteudo = json.loads(_texto(publicacao))
    encontrados = set(UUID_EM_QUALQUER_LUGAR.findall(_texto(publicacao)))

    assert encontrados == {conteudo["cabecalho"]["ato"]["id"]}


def test_o_conteudo_nao_contem_valor_de_desempate(publicada):
    """A coluna não é lida, e por isso não há valor a vazar (FR-020, SC-015)."""
    from processo_seletivo.classificacao.models import PosicaoNaOrdem

    cenario, publicacao = publicada
    texto = _texto(publicacao)

    proveniencias = PosicaoNaOrdem.objects.filter(ato=cenario["ato"]).values_list(
        "desempate", flat=True
    )
    for proveniencia in proveniencias:
        for criterio in proveniencia or []:
            assert "criterionId" not in texto
            if criterio.get("value") is not None:
                assert str(criterio["value"]) not in texto
    assert "desempate" not in texto
    assert "separated" not in texto


def test_o_conteudo_nao_nomeia_quem_nao_recebeu_posicao(publicada):
    """A fronteira da FR-017, verificada sobre os bytes divulgados."""
    cenario, publicacao = publicada
    texto = _texto(publicacao)

    sem_posicao = SituacaoDivulgada.objects.get(
        publicacao=publicacao, situacao=SituacaoDivulgada.Situacao.SEM_POSICAO
    )
    assert sem_posicao.inscricao.nome not in texto
    assert sem_posicao.inscricao.protocolo not in texto
    assert sem_posicao.motivo not in texto


def test_o_conteudo_nao_carrega_enum_como_texto_de_apresentacao(publicada):
    """`natureza` é dado de vínculo; o que se lê é `natureza_rotulo` (FR-013)."""
    _, publicacao = publicada
    conteudo = json.loads(_texto(publicacao))

    # A única grafia canônica admitida é `cabecalho.natureza`, que existe para a máquina e é
    # acompanhada do rótulo que a pessoa lê.
    del conteudo["cabecalho"]["natureza"]
    resto = json.dumps(conteudo, ensure_ascii=False)
    for enum in ENUMS_CANONICOS:
        assert enum not in resto


def test_a_situacao_individual_nao_esta_no_conteudo_publicado(publicada):
    """T-010: a projeção individual é tabela, e não chave dentro dos bytes divulgados."""
    _, publicacao = publicada
    conteudo = json.loads(_texto(publicacao))

    assert set(conteudo) == {"cabecalho", "posicoes"}
    assert publicacao.situacoes.count() == 3, "as três consideradas moram na tabela à parte"


def test_o_resumo_confere_com_os_bytes_gravados(publicada):
    """SC-004: recalcular o resumo a partir do que está gravado tem de dar o mesmo valor.

    É isto que dá sentido à afirmação de que o divulgado é conferível: quem baixa o conteúdo pode
    reproduzir o resumo e comparar com o publicado.
    """
    _, publicacao = publicada
    conteudo = json.loads(_texto(publicacao))

    assert canonical_sha256(conteudo) == publicacao.conteudo_publico_hash


def test_o_resumo_muda_quando_qualquer_campo_do_conteudo_muda(publicada):
    """Um resumo que não muda com o conteúdo não prova coisa nenhuma (FR-011)."""
    _, publicacao = publicada
    conteudo = json.loads(_texto(publicacao))

    variacoes = [
        ("posição", lambda c: c["posicoes"][0].update({"posicao": 99})),
        ("nome", lambda c: c["posicoes"][0].update({"candidato": "Outra pessoa"})),
        ("pontuação", lambda c: c["posicoes"][0].update({"pontuacao": "10,00"})),
        (
            "instante",
            lambda c: c["cabecalho"].update({"publicado_em": "2020-01-01T00:00:00+00:00"}),
        ),
        ("autoridade", lambda c: c["cabecalho"].update({"signatario_nome": "Outra autoridade"})),
        ("marco", lambda c: c["cabecalho"].update({"marco": "Outro marco"})),
    ]
    for nome, alterar in variacoes:
        alterado = json.loads(_texto(publicacao))
        alterar(alterado)
        assert canonical_sha256(alterado) != publicacao.conteudo_publico_hash, (
            f"alterar {nome} não mudou o resumo: ele não cobre o conteúdo inteiro"
        )
    assert canonical_sha256(conteudo) == publicacao.conteudo_publico_hash


def test_os_dois_resumos_cobrem_materiais_diferentes(publicada):
    """`confirmacao_da_previa` **não** contém o instante; `conteudo_publico_hash` contém.

    Confundi-los não fecha: o instante definitivo só existe no POST, e um resumo calculado na
    prévia jamais coincidiria com um conteúdo que carrega `publicado_em` (contracts/conteudo.md §3).
    """
    from processo_seletivo.divulgacao.application.publicar import assinatura_da_previa
    from processo_seletivo.divulgacao.domain.conteudo import compor

    cenario, publicacao = publicada
    projecao = compor(cenario["ato"])
    da_previa = assinatura_da_previa(
        ato=cenario["ato"], publicacao_anterior=None, projecao=projecao
    )

    assert da_previa != publicacao.conteudo_publico_hash
    # E ela continua a mesma depois de publicada: o que ela cobre não mudou com o ato.
    assert da_previa == assinatura_da_previa(
        ato=cenario["ato"], publicacao_anterior=None, projecao=compor(cenario["ato"])
    )


def test_todo_campo_de_texto_ausente_e_string_vazia(publicada):
    """Texto ausente é `""`, nunca `null` e nunca chave omitida (contracts/conteudo.md §2)."""
    _, publicacao = publicada
    conteudo = json.loads(_texto(publicacao))

    assert None not in conteudo["cabecalho"].values()
    esperadas = {"posicao", "compartilhada", "candidato", "protocolo", "modalidade", "pontuacao"}
    for item in conteudo["posicoes"]:
        assert set(item) == esperadas
        assert None not in item.values()


def test_o_conteudo_nao_declara_versao_de_formato(publicada):
    """Considerado e retirado: prometeria garantia que nada nesta feature entrega.

    Há um renderizador só. Um campo que anuncia que publicações antigas continuam sendo
    renderizadas pela regra em que nasceram é pior que a ausência dele, porque a próxima pessoa
    confia nele (contracts/conteudo.md §2).
    """
    _, publicacao = publicada
    texto = _texto(publicacao)

    assert "schemaVersion" not in texto
    assert "formatVersion" not in texto


def test_os_bytes_sao_canonicos(publicada):
    """`sort_keys`, sem espaço entre separadores, NFC, UTF-8 — a mesma forma do Edital."""
    from processo_seletivo.shared.canonical import canonical_bytes

    _, publicacao = publicada
    conteudo = json.loads(_texto(publicacao))

    assert _bytes_gravados(publicacao) == canonical_bytes(conteudo)


def test_o_conteudo_nao_contem_uuid_de_signatario(publicada):
    """`signatario_id` é dado de vínculo, não de leitura — como na publicação do Edital."""
    _, publicacao = publicada

    assert str(publicacao.signatario_id) not in _texto(publicacao)
    assert isinstance(publicacao.signatario_id, uuid.UUID)
