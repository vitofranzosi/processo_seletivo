"""O cenário do Requerimento de Matrícula e os atalhos que os arquivos da `029` usam.

**Funções ficam aqui, e a fixture fica no `conftest.py` de cada pasta.** Importar uma fixture de
outro módulo de teste a redefine no importador, que é o que o `F811` acusa; importar uma função
comum não tem esse problema. É a regra que `tests/fixtures/corte.py` registra, e foi por não
segui-la que a primeira redação destes testes deixou a pasta `tests/interface/` sem acesso ao
cenário — as fixtures viviam num `conftest.py` que só valia para `tests/integration/`.

Dois Editais publicados, e a diferença entre eles é **uma linha**: o momento declarado. É o que
separa o caso do 77 e do 58 — requerimento na inscrição — do caso do 69 e do 46, na convocação.
"""

import json
import re
import uuid
from datetime import timedelta

from django.utils import timezone

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.requerimentos.domain import nomes

NUMERO = iter(range(900, 999))

DECLARACAO = "Declaro, sob as penas da Lei, que as informações fornecidas são verdadeiras."

UUID_NO_TEXTO = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)


def com_identificadores_novos(rascunho):
    """O mesmo rascunho, com **todos** os UUIDs trocados de forma consistente.

    Troca por mapa, e não por campo: as coleções se referenciam entre si — o Documento Exigido
    aponta Perfil e modalidade, o marco aponta Etapas —, e renumerar campo a campo quebraria os
    vínculos em silêncio. O mapa garante que a mesma identidade antiga vire sempre a mesma nova.
    """
    texto = json.dumps(rascunho)
    mapa = {antigo: str(uuid.uuid4()) for antigo in set(UUID_NO_TEXTO.findall(texto))}
    for antigo, novo in mapa.items():
        texto = texto.replace(antigo, novo)
    return json.loads(texto)


def declarar(momento):
    """O gancho que faz o Edital declarar o requerimento **antes** de o snapshot congelar.

    `antes_de_submeter` existe para isto: campo de elaboração que precisa estar de pé antes da
    publicação, porque depois dela o conteúdo é imutável.
    """

    def antes_de_submeter(edital):
        Edital.objects.filter(pk=edital.pk).update(
            requerimento_momento=momento, requerimento_declaracao=DECLARACAO
        )

    return antes_de_submeter


def publicar_com_requerimento(api_client, manager_headers, process_payload, momento):
    from tests.fixtures.selecao import publicar_selecao, rascunho_aberto_com_documentos

    return publicar_selecao(
        api_client,
        manager_headers,
        process_payload,
        rascunho=rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)),
        antes_de_submeter=declarar(momento),
    )


def campos_de_exemplo():
    """O conteúdo mínimo de um requerimento válido — sem o aceite, que cada teste decide."""
    return {
        "data_de_nascimento": "1990-03-14",
        "municipio_natal": "Vitória",
        "uf_natal": "ES",
        "nacionalidade": "Brasileira",
        "sexo": nomes.FEMININO,
        "cor_raca": nomes.PARDA,
        "estado_civil": nomes.SOLTEIRO,
        "nome_da_mae": "Maria da Silva",
        "nome_do_pai": "",
        "rg": "1234567",
        "rg_orgao_emissor": "SSP-ES",
        "rg_expedido_em": "2015-06-01",
        "telefone_celular": "(27) 99999-0000",
        "renda_familiar_faixa": nomes.DE_MEIO_A_UM,
        "cep": "29040860",
        "logradouro": "Rua Barão de Mauá",
        "numero": "30",
        "bairro": "Jucutuquara",
        "municipio": "Vitória",
        "uf": "ES",
    }


def inscricao_aberta(edital, perfil=None):
    """Uma inscrição aberta, com o telefone gravado **direto**.

    E não por `gravar_dados`: aquele comando é da `009` e exige a modalidade escolhida, que não
    tem nada a ver com o que estes testes exercitam. Fixture que atravessa comando alheio passa a
    quebrar quando aquele comando muda — e a quebra apareceria aqui, longe da causa.
    """
    from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao
    from tests.fixtures.candidato import MARIA, PERFIL_DOCENTE

    inscricao = abrir_inscricao(
        identidade=MARIA, edital_id=edital.id, profile_id=perfil or PERFIL_DOCENTE
    )
    Inscricao.objects.filter(pk=inscricao.pk).update(telefone="(27) 99999-0000")
    return Inscricao.objects.get(pk=inscricao.pk)


def pronta_para_enviar(edital, perfil=None):
    """Uma inscrição com modalidade e documentos — tudo **menos** o requerimento.

    Existe para que o teste do bloqueio chame `enviar_inscricao` de verdade. Um teste que chamasse
    só o predicado provaria o predicado, e foi exatamente assim que a primeira redação desta
    feature marcou a tarefa como pronta com a submissão ainda passando reto.
    """
    from processo_seletivo.inscricoes.application.rascunho import (
        abrir_inscricao,
        anexar_documento,
        gravar_dados,
    )
    from tests.fixtures.candidato import MARIA, MODALIDADE_AC, PERFIL_DOCENTE, pdf
    from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

    inscricao = abrir_inscricao(
        identidade=MARIA, edital_id=edital.id, profile_id=perfil or PERFIL_DOCENTE
    )
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "dip.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    Inscricao.objects.filter(pk=inscricao.pk).update(telefone="(27) 99999-0000")
    return Inscricao.objects.get(pk=inscricao.pk)


def submeter(inscricao, chave="envio-029"):
    """O comando de verdade, sem tela nenhuma pelo caminho."""
    from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
    from tests.fixtures.candidato import MARIA

    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key=f"{chave}-{inscricao.pk}",
    )


def publicar_sem_documentos(api_client, manager_headers, process_payload, momento):
    """Um Edital que coleta o requerimento e **não** exige Documento nenhum.

    É o destino natural da feature — adotar o estruturado e retirar o Anexo em papel —, e é o
    cenário que prova que o requerimento não passa a exigir o Anexo implicitamente (`FR-395`).

    **Chave de idempotência própria**: o `manager_headers` traz uma fixa, e um segundo Processo com
    a mesma chave é devolvido como repetição do primeiro — de modo que o teste receberia o Edital
    *do outro cenário*, com os documentos, e passaria medindo a coisa errada. Já custou uma medição
    inteira nesta feature.
    """
    from tests.fixtures.selecao import publicar_selecao, rascunho_aberto_com_documentos

    rascunho = com_identificadores_novos(
        rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1))
    )
    rascunho["documentRequirements"] = []
    return publicar_selecao(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"029-sem-doc-{uuid.uuid4().hex[:8]}"},
        {
            **process_payload,
            "institutionalCode": f"PS-029-{uuid.uuid4().hex[:6]}",
            "firstEdital": {
                **process_payload["firstEdital"],
                "number": str(next(NUMERO)),
                "title": "Certame sem Documento Exigido",
            },
        },
        rascunho=rascunho,
        antes_de_submeter=declarar(momento),
    )


def pronta_sem_documentos(edital, perfil=None):
    """Inscrição com modalidade e **nenhum** documento — o Edital não exige nenhum."""
    from processo_seletivo.editais.models.perfis import PerfilVaga
    from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao, gravar_dados
    from tests.fixtures.candidato import MARIA

    alvo = perfil or PerfilVaga.objects.filter(edital=edital).first().id
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=alvo)
    modalidade = next(
        (linha["id"] for linha in _modalidades_do_perfil(edital, alvo)),
        None,
    )
    if modalidade:
        inscricao = gravar_dados(
            identidade=MARIA, inscricao=inscricao, dados={"modality_id": modalidade}
        )
    Inscricao.objects.filter(pk=inscricao.pk).update(telefone="(27) 99999-0000")
    return Inscricao.objects.get(pk=inscricao.pk)


def _modalidades_do_perfil(edital, perfil_id):
    from processo_seletivo.publicacoes.application import selectors

    conteudo = selectors.selecao_publica(edital_id=edital.id).content
    perfil = next(
        (item for item in conteudo.get("profiles") or [] if str(item["id"]) == str(perfil_id)), {}
    )
    return perfil.get("competitionModalities") or []
