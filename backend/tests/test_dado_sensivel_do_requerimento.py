"""Cor/raça, filiação, documento, endereço e renda não saem por endereço, recusa ou trilha.

`FR-401`, e é **MUST** do Princípio III: *"Logs e auditoria NÃO DEVEM expor conteúdo sensível
desnecessário"*.

**Por que um teste, se hoje as três garantias existem por construção?** Exatamente por isso. O
endereço da rota é o da Inscrição por convenção do portal; a recusa nomeia o que falta em palavras,
não em valores; a trilha aponta o requerimento em vez de copiá-lo. Nenhuma das três está presa por
mecanismo — as três são **hábito**, e hábito se perde numa refatoração feita com pressa por alguém
que não leu a spec. Este arquivo transforma as três em regra.

**As três superfícies vazam de jeitos diferentes.** O endereço viaja para log de servidor, histórico
de navegador e cabeçalho de referência sem que ninguém decida isso. A mensagem de erro é copiada e
colada em chamado de suporte. A trilha é lida por quem responde questionamento — e é permanente, em
tabela append-only, onde o que entrou não sai.
"""

import re
from pathlib import Path

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.requerimentos.application import preencher
from processo_seletivo.requerimentos.domain import nomes
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import MARIA
from tests.fixtures.requerimento import DECLARACAO, pronta_para_enviar

RAIZ = Path(__file__).resolve().parents[1] / "processo_seletivo"

# Os campos que a `FR-401` nomeia, pelo nome com que viajariam num endereço ou numa mensagem.
SENSIVEIS = (
    "cor_raca",
    "necessidade_especifica",
    "nome_da_mae",
    "nome_do_pai",
    "rg",
    "rg_orgao_emissor",
    "cep",
    "logradouro",
    "bairro",
    "renda_familiar_faixa",
)


# --- 1. Nenhum endereço carrega dado sensível ---------------------------------------------------


def rotas_da_feature():
    from processo_seletivo.interface import urls as gestao
    from processo_seletivo.portal import urls as portal

    return [
        str(rota.pattern)
        for modulo in (gestao, portal)
        for rota in modulo.urlpatterns
        if "requerimento" in str(rota.pattern)
    ]


def test_ha_rotas_a_conferir():
    """Uma varredura sobre lista vazia aprova tudo, calada."""
    assert len(rotas_da_feature()) >= 3


@pytest.mark.parametrize("rota", rotas_da_feature())
def test_nenhum_parametro_de_rota_nomeia_dado_sensivel(rota):
    """`FR-401`: o que viaja no endereço vai para log, histórico e cabeçalho de referência.

    **A conferência é dos parâmetros, e não do caminho inteiro.** A rota da consulta de CEP se
    *chama* `requerimento/cep` — o nome do serviço —, e não carrega valor nenhum: o CEP vai no
    corpo do `POST`. Uma varredura por substring no caminho reprovaria justamente a rota que foi
    desenhada para obedecer à regra, e ensinaria a renomeá-la em vez de a corrigir.
    """
    achados = [
        parametro
        for parametro in re.findall(r"<([^>]+)>", rota)
        for campo in SENSIVEIS
        if campo in parametro.lower()
    ]

    assert achados == [], f"{rota}: carrega {achados} no endereço"


def test_a_consulta_de_cep_recebe_o_cep_no_corpo_e_nao_no_endereco():
    """O caso que quase deu errado, preso por nome.

    `GET /requerimento/cep/<cep>` era a forma óbvia, e o próprio contrato desta feature a oferecia
    numa primeira redação — até a `FR-401` reprová-la. Um endereço fixo é o que garante que o CEP
    não tem por onde entrar nele.
    """
    from processo_seletivo.portal import urls as portal

    rota = next(rota for rota in portal.urlpatterns if rota.name == "requerimento-cep")

    assert "<" not in str(rota.pattern), "endereço fixo: não há segmento variável onde o CEP caiba"


def test_os_parametros_das_rotas_sao_apenas_identificadores():
    """O que entra num endereço desta feature é UUID, e nada mais.

    Um `<str:...>` aqui seria a porta pela qual um CEP, um nome ou um documento entraria no endereço
    sem ninguém decidir — e a regra acima, que procura nomes de campo, não o veria.
    """
    parametros = [
        parametro for rota in rotas_da_feature() for parametro in re.findall(r"<([^>]+)>", rota)
    ]

    assert parametros, "o rastreio quebrou: nenhuma rota com parâmetro"
    for parametro in parametros:
        assert parametro.startswith("uuid:"), f"parâmetro que não é identificador: {parametro}"


# --- 2. Nenhuma recusa repete o que a pessoa digitou --------------------------------------------
#
# **As fixtures são declaradas aqui**, e não importadas de um `conftest.py` de pasta: este arquivo
# mora na raiz de `tests/`, porque a garantia que ele guarda é transversal — ela alcança rota,
# mensagem e trilha, que vivem em camadas diferentes. As funções moram em
# `tests/fixtures/requerimento.py`, como a convenção deste repositório manda.


@pytest.fixture
def selecao_na_inscricao(raiz_de_arquivos, api_client, manager_headers, process_payload):
    from tests.fixtures.requerimento import publicar_com_requerimento

    return publicar_com_requerimento(api_client, manager_headers, process_payload, "AT_ENROLLMENT")


@pytest.fixture
def campos_declarados():
    from tests.fixtures.requerimento import campos_de_exemplo

    return campos_de_exemplo()


@pytest.mark.django_db
@pytest.mark.integration
def test_a_recusa_do_envio_nomeia_o_que_falta_sem_repetir_valor(
    selecao_na_inscricao, candidatos_registrados, campos_declarados
):
    """A mensagem diz *"falta o CEP"*, e nunca *"o CEP 29040860 é inválido"*.

    Mensagem de erro é copiada e colada em chamado de suporte, e o que ela repetir viaja junto.
    """
    inscricao = pronta_para_enviar(selecao_na_inscricao)
    preencher.abrir_rascunho(inscricao=inscricao)
    preencher.gravar(
        inscricao=inscricao,
        dados={**campos_declarados, "cep": "", "rg": "", "nome_da_mae": "Fulana de Tal"},
        expected_revision=None,
    )

    with pytest.raises(DomainError) as recusa:
        preencher.enviar(
            identidade=MARIA,
            inscricao=inscricao,
            versao_exibida_id=preencher._conteudo(inscricao).id,
            declaracao_exibida=DECLARACAO,
            aceite=True,
        )

    detalhe = recusa.value.detail
    assert "o CEP" in detalhe, "ela nomeia o que falta"
    assert "Fulana de Tal" not in detalhe, "e não repete o que foi digitado"
    assert campos_declarados["rg"] not in detalhe


def test_nenhuma_mensagem_do_dominio_interpola_valor_declarado():
    """As mensagens desta feature são **literais**, e o que varia nelas é o nome do campo.

    Uma `f-string` com `{requerimento.cep}` dentro de um `DomainError` seria o vazamento mais fácil
    de escrever e o mais difícil de notar: ele só aparece quando alguém erra o preenchimento.
    """
    import ast

    modulos = [
        RAIZ / "requerimentos/application/preencher.py",
        RAIZ / "requerimentos/application/exigencia.py",
        RAIZ / "editais/application/requerimento.py",
    ]
    vazamentos = []
    for caminho in modulos:
        arvore = ast.parse(caminho.read_text())
        for no in ast.walk(arvore):
            if not (isinstance(no, ast.Call) and getattr(no.func, "id", "") == "DomainError"):
                continue
            for argumento in no.args:
                for parte in ast.walk(argumento):
                    if not isinstance(parte, ast.FormattedValue):
                        continue
                    origem = ast.unparse(parte.value)
                    if any(campo in origem for campo in SENSIVEIS):
                        vazamentos.append(f"{caminho.name}: {origem}")

    assert vazamentos == [], f"recusa interpolando dado declarado: {vazamentos}"


# --- 3. Nenhum registro de auditoria grava o que foi declarado ----------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_a_trilha_do_envio_nao_guarda_nenhum_campo_declarado(
    selecao_na_inscricao, candidatos_registrados, campos_declarados
):
    """**A trilha referencia, e não copia** (`FR-401`).

    Ela é permanente e append-only: o que entrar ali não sai. Duplicar dado sensível numa tabela que
    não admite `DELETE` multiplica a superfície em vez de protegê-la — e a pergunta que a trilha
    responde, *"quem enviou o quê e quando"*, é respondida por um ponteiro.
    """
    inscricao = pronta_para_enviar(selecao_na_inscricao)
    preencher.abrir_rascunho(inscricao=inscricao)
    preencher.gravar(inscricao=inscricao, dados=campos_declarados, expected_revision=None)
    preencher.enviar(
        identidade=MARIA,
        inscricao=inscricao,
        versao_exibida_id=preencher._conteudo(inscricao).id,
        declaracao_exibida=DECLARACAO,
        aceite=True,
    )

    registro = RegistroAuditoria.objects.get(operation=nomes.OPERACAO_ENVIO)
    texto = " ".join(
        str(valor)
        for valor in (
            registro.reason,
            registro.previous_state,
            registro.new_state,
            registro.permission,
            registro.idempotency_key,
        )
    )
    declarados = [
        str(valor)
        for campo, valor in campos_declarados.items()
        if campo in SENSIVEIS and str(valor).strip()
    ]

    assert declarados, "o rastreio quebrou: o cenário não declara campo sensível nenhum"
    achados = [valor for valor in declarados if valor in texto]
    assert achados == [], f"a trilha copiou o que devia referenciar: {achados}"


# **A trilha do ato de elaboração fica presa onde ele acontece.** Que `ALTERAR_REQUERIMENTO` não
# copia o texto da declaração para dentro do registro é afirmado em
# `tests/interface/test_compor_requerimento.py::test_o_ato_fica_na_trilha_com_o_momento`, que compõe
# pela tela. Repeti-lo aqui exigiria um cenário que passa pelo comando de elaboração — e a primeira
# redação, sem ele, virava um `skip`: um teste que não roda não guarda nada.


@pytest.mark.django_db
@pytest.mark.integration
def test_nenhum_registro_desta_feature_usa_a_inscricao_como_agregado(
    selecao_na_inscricao, candidatos_registrados, campos_declarados
):
    """O agregado é o requerimento — e isso também é privacidade, além de correção.

    `record_event` copia `status` e `revision` do agregado para colunas próprias. Com a Inscrição
    ali, o registro passaria a afirmar o estado dela num ato que não a tocou, e a trilha carregaria
    um fato falso sobre um objeto que não é o assunto.
    """
    inscricao = pronta_para_enviar(selecao_na_inscricao)
    preencher.abrir_rascunho(inscricao=inscricao)
    preencher.gravar(inscricao=inscricao, dados=campos_declarados, expected_revision=None)
    preencher.enviar(
        identidade=MARIA,
        inscricao=inscricao,
        versao_exibida_id=preencher._conteudo(inscricao).id,
        declaracao_exibida=DECLARACAO,
        aceite=True,
    )

    tipos = set(
        RegistroAuditoria.objects.filter(
            operation__in=(nomes.OPERACAO_ENVIO, nomes.OPERACAO_SUCESSAO)
        ).values_list("aggregate_type", flat=True)
    )

    assert tipos == {"RequerimentoDeMatricula"}
