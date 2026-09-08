"""O modelo que estava valendo, na mesa de quem avalia (020, FR-048, FR-050).

A banca confere o que voltou contra a forma que **foi pedida**, e a forma pedida é a da versão que
aquela Inscrição aceitou. Mostrar a vigente faria uma Retificação posterior reescrever, na tela, o
que se exigiu de quem já enviou.

O que a tela **não** afirma é qual arquivo o candidato baixou. Ele pode ter baixado sob outra
versão, e os bytes devolvidos não dizem de onde vieram: conformidade é juízo de quem avalia
(D-004, FR-049).
"""

import pytest
from django.urls import reverse

from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.editais.domain.documentos import modelo_do_requisito
from processo_seletivo.editais.models import AnexoEdital, ArtefatoAnexo, DocumentoExigido
from tests.fixtures.anexos import criar_artefato
from tests.fixtures.comissao import (
    DOCUMENTO_A,
    ETAPA_A1,
    alocar_em,
    constituir,
    publicar_processo_com_etapas,
)
from tests.fixtures.edital import identificador
from tests.fixtures.mesa import distribuir_para, inscricoes_de
from tests.fixtures.publicacao import create_retification, publish_retification
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

SEED = 91


def test_o_modelo_e_resolvido_dentro_da_versao_que_o_conteudo_declara():
    """A resolução é por conteúdo — é o que faz mesa e portal responderem versões diferentes."""
    aceita = {
        "attachments": [
            {"id": "a" * 8, "label": "ANEXO I — ANTIGO", "order": 1, "artifactId": "1" * 8}
        ]
    }
    vigente = {
        "attachments": [
            {"id": "a" * 8, "label": "ANEXO I — NOVO", "order": 1, "artifactId": "2" * 8}
        ]
    }
    requisito = {"id": "r", "attachmentId": "a" * 8}

    assert modelo_do_requisito(aceita, requisito)["artefato_id"] == "1" * 8
    assert modelo_do_requisito(vigente, requisito)["artefato_id"] == "2" * 8


def test_o_requisito_sem_modelo_nao_resolve_nada():
    conteudo = {"attachments": [{"id": "a" * 8, "label": "X", "order": 1, "artifactId": "1" * 8}]}

    assert modelo_do_requisito(conteudo, {"id": "r", "attachmentId": None}) is None
    assert modelo_do_requisito(conteudo, {"id": "r"}) is None


def test_o_vinculo_pendurado_nao_quebra_a_tela():
    """A validação recusa a referência pendurada; versão publicada antes dela não pode derrubar."""
    conteudo = {"attachments": []}

    assert modelo_do_requisito(conteudo, {"id": "r", "attachmentId": "a" * 8}) is None


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    def vincular(edital):
        anexo = AnexoEdital.objects.filter(edital=edital).order_by("order").first()
        DocumentoExigido.objects.filter(edital=edital, id=identificador(DOCUMENTO_A, SEED)).update(
            anexo=anexo
        )

    edital = publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"modelo-mesa-{SEED:04d}"},
        {
            "institutionalCode": f"PS-2026-{SEED}",
            "title": "Processo com modelo",
            "firstEdital": {"number": "91", "year": 2026, "title": "Edital 91/2026"},
        },
        seed=SEED,
        com_documentos=True,
        avaliacoes=2,
        maxima="100.0000",
        anexos=1,
        antes_de_submeter=vincular,
    )
    etapa = identificador(ETAPA_A1, SEED)
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo=f"modelo-{SEED}",
    )
    alocar_em(gestor, edital.processo, membros["joao"], edital, etapa, chave=f"aloc-{SEED}")
    return {
        "edital": edital,
        "etapa": etapa,
        "processo": edital.processo,
        "membros": membros,
    }


def divergir(api_client, cenario):
    """Publica uma Retificação que substitui o artefato — **depois** de a inscrição existir.

    É o que faz a versão aceita e a vigente deixarem de ser a mesma. Sem esta divergência os dois
    testes abaixo passariam com uma tela que lê a versão errada, porque as duas coincidiriam.
    """
    anexo = AnexoEdital.objects.get(edital=cenario["edital"])
    novo = criar_artefato(marca="Z", nome="formulario-retificado.pdf")
    publish_retification(
        api_client,
        create_retification(
            api_client,
            cenario["edital"],
            [
                {
                    "targetPath": f"/attachments/id={anexo.id}/artifactId",
                    "operation": "REPLACE",
                    "newValue": str(novo.id),
                },
                {
                    "targetPath": f"/attachments/id={anexo.id}/artifactHash",
                    "operation": "REPLACE",
                    "newValue": novo.document_hash,
                },
            ],
            suffix="mesa",
        ),
        suffix="mesa",
    )
    return novo


def abrir_mesa(client, cenario, inscricao):
    return client.get(
        reverse(
            "interface:mesa-inscricao",
            args=[cenario["edital"].id, cenario["etapa"], inscricao.id],
        )
    ).content.decode()


def test_a_mesa_oferece_o_modelo_da_versao_aceita_e_nao_o_vigente(
    client, api_client, seletor_ligado, cenario, gestor
):
    """FR-050 e SC-007 — o cenário **diverge**, que é a única forma de a preferência aparecer.

    A inscrição nasce sob a versão com o artefato A; a Retificação publica B. A mesa tem de
    mostrar A, porque foi A que se exigiu de quem enviou — mostrar B faria a banca conferir o que
    voltou contra uma forma que não foi pedida.
    """
    inscricoes = inscricoes_de(cenario, 1, primeiro=9100)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="modelo")
    antigo = AnexoEdital.objects.get(edital=cenario["edital"]).artefato
    novo = divergir(api_client, cenario)
    identificar(client, "joao", [])

    corpo = abrir_mesa(client, cenario, inscricoes[0])

    assert "Modelo exigido" in corpo
    assert reverse("public-anexo", args=[antigo.id]) in corpo, "o de então"
    assert reverse("public-anexo", args=[novo.id]) not in corpo, "e não o de agora"


def test_o_modelo_que_a_mesa_abre_tem_os_bytes_daquela_versao(
    client, api_client, seletor_ligado, cenario, gestor
):
    """Clicar, e não só conferir que o link existe — foi assim que a US2 escondeu um 404."""
    inscricoes = inscricoes_de(cenario, 1, primeiro=9120)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="bytes")
    antigo = AnexoEdital.objects.get(edital=cenario["edital"]).artefato
    novo = divergir(api_client, cenario)
    identificar(client, "joao", [])

    baixado = client.get(reverse("public-anexo", args=[antigo.id]))

    assert baixado.status_code == 200
    assert baixado.content == bytes(ArtefatoAnexo.objects.get(pk=antigo.id).bytes)
    assert baixado.content != bytes(ArtefatoAnexo.objects.get(pk=novo.id).bytes)


# O que a superfície do modelo tem permissão de dizer. É lista de **permitidos**, e não de
# proibidos, porque proibir palavras numa página inteira erra dos dois lados: "recusou" contém
# "usou", e uma formulação nova como "modelo que consta da inscrição" não estaria em lista alguma.
# Pinar o vocabulário torna a próxima frase uma decisão, e não um acidente.
VOCABULARIO_DO_MODELO = {"modelo exigido", "abrir o modelo exigido:"}


def celulas_do_modelo(corpo):
    """O texto de cada célula de modelo: o visível e o que só o leitor de tela ouve.

    Os dois são extraídos **separadamente**. Uma primeira redação injetava um `>` antes do
    `aria-label` para reaproveitar a divisão por tags, e o resultado colava rótulo acessível e texto
    visível numa string só — que passava no guarda por começar com o termo aprovado. O guarda
    parecia funcionar e não funcionava.
    """
    import re

    celulas = re.findall(r'<span class="modelo">(.*?)</span>\s*(?=<span|</li>)', corpo, re.S)
    textos = []
    for celula in celulas:
        visivel = re.sub(r"<[^>]+>", " ", celula).strip().lower()
        if visivel:
            textos.append(visivel)
        textos.extend(
            rotulo.strip().lower() for rotulo in re.findall(r'aria-label="([^"]*)"', celula)
        )
    return textos


def test_a_superficie_do_modelo_so_diz_o_que_foi_aprovado(
    client, api_client, seletor_ligado, cenario, gestor
):
    """FR-049 — a tela mostra a forma **exigida**, e não a origem do arquivo que voltou.

    O guarda roda sobre o cenário divergente de propósito: é ali que a tentação de escrever "modelo
    utilizado" apareceria, porque é ali que existem duas formas e alguém quereria dizer qual delas
    a pessoa teria usado. O sistema não sabe — os bytes devolvidos não dizem de onde vieram.

    E o guarda é sobre a **célula do modelo**, não sobre a página: procurar palavras no HTML
    inteiro acusa "recusou" por conter "usou", e deixa passar a formulação que ninguém previu.
    """
    inscricoes = inscricoes_de(cenario, 1, primeiro=9110)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="origem")
    divergir(api_client, cenario)
    identificar(client, "joao", [])

    celulas = celulas_do_modelo(abrir_mesa(client, cenario, inscricoes[0]))

    assert celulas, "a célula do modelo precisa existir para que o guarda signifique alguma coisa"
    for texto in celulas:
        assert any(texto.startswith(termo) for termo in VOCABULARIO_DO_MODELO), (
            f"a célula do modelo diz {texto!r}, que ninguém aprovou — se a frase é nova, ela é "
            "decisão, e entra nesta lista com a razão ao lado"
        )
