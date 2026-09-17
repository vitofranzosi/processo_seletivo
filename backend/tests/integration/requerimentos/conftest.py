"""O mínimo para existir um Requerimento: Processo, Edital, Inscrição.

Montado à mão, e não por fixture compartilhada, porque o que estes testes exercitam é o **banco** —
restrição e gatilho. Uma fixture que passasse pela aplicação provaria a aplicação junto, e é
exatamente o que estes testes não devem depender de provar.
"""

import uuid

import pytest
from django.utils import timezone

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.requerimentos.domain import nomes
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula
from tests.fixtures import requerimento

# Reexportado para os arquivos desta pasta, que citam a declaração por extenso ao enviar.
DECLARACAO = requerimento.DECLARACAO
pronta_para_enviar = requerimento.pronta_para_enviar
submeter = requerimento.submeter

NUMERO = iter(range(900, 999))


@pytest.fixture
def inscricao(db):
    agora = timezone.now()
    processo = ProcessoSeletivo.objects.create(
        institution_scope="cefor",
        institutional_code=f"PS-029-{uuid.uuid4().hex[:8]}",
        title="Processo do requerimento",
        created_at=agora,
        created_by="teste",
        last_changed_at=agora,
    )
    edital = Edital.objects.create(
        processo=processo,
        institution_scope="cefor",
        number=str(next(NUMERO)),
        year=2026,
        title="Edital do requerimento",
        created_at=agora,
        created_by="teste",
        last_edited_by="teste",
    )
    return Inscricao.objects.create(
        identity_subject=f"cand:{uuid.uuid4().hex}",
        edital=edital,
        profile_id=uuid.uuid4(),
        created_at=agora,
    )


@pytest.fixture
def selecao_na_inscricao(raiz_de_arquivos, api_client, manager_headers, process_payload):
    """Seleção publicada que coleta o requerimento **na inscrição** — o caso do 77 e do 58."""
    return requerimento.publicar_com_requerimento(
        api_client, manager_headers, process_payload, "AT_ENROLLMENT"
    )


@pytest.fixture
def selecao_na_convocacao(raiz_de_arquivos, api_client, manager_headers, process_payload):
    """Seleção publicada que coleta **na convocação** — o caso do 69 e do 46."""
    return requerimento.publicar_com_requerimento(
        api_client, manager_headers, process_payload, "AT_CALL"
    )


@pytest.fixture
def campos_declarados():
    return requerimento.campos_de_exemplo()


@pytest.fixture
def rascunho(inscricao, campos_declarados):
    agora = timezone.now()
    return RequerimentoDeMatricula.objects.create(
        inscricao=inscricao,
        status=nomes.RASCUNHO,
        disponibilizado_em=agora,
        created_at=agora,
        **campos_declarados,
    )


@pytest.fixture
def versao_consolidada(inscricao):
    """A versão sob a qual o aceite acontece.

    Montada no mínimo: a `ck_requerimento_enviado_completo` exige `versao_aceita` para o estado
    *enviado* ser alcançável, e sem ela não há como exercitar o gatilho sobre um requerimento
    enviado. O conteúdo é irrelevante aqui — o que se prende é forma de banco, não norma.
    """
    agora = timezone.now()
    publicacao = Publicacao.objects.create(
        edital=inscricao.edital,
        publication_order=1,
        published_at=agora,
        effective_at=agora,
        content_hash="0" * 64,
        canonical_content=b"{}",
        published_by="teste",
        signatory_id=uuid.uuid4(),
        signatory_name="Autoridade de teste",
        signatory_role="Diretora-Geral",
    )
    return VersaoConsolidada.objects.create(
        edital=inscricao.edital,
        valid_from=agora,
        materialized_at=agora,
        source_publication=publicacao,
        content={},
        canonical_content=b"{}",
        content_hash="0" * 64,
    )


@pytest.fixture
def inscricao_na_inscricao(selecao_na_inscricao, candidatos_registrados):
    return requerimento.inscricao_aberta(selecao_na_inscricao)


@pytest.fixture
def segunda_inscricao_da_mesma_pessoa(
    inscricao_na_inscricao,
    raiz_de_arquivos,
    api_client,
    manager_headers,
    process_payload,
    candidatos_registrados,
):
    """A mesma pessoa, outro certame — que é o caso que a cópia-para-a-frente existe para atender.

    Um segundo Processo e um segundo Edital, porque `uq_processo_scope_institutional_code` e
    `uq_edital_scope_number_year` recusariam a repetição — e porque o ponto é justamente **outro**
    certame.
    """
    from datetime import timedelta

    from processo_seletivo.editais.models.perfis import PerfilVaga
    from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao
    from tests.fixtures.candidato import MARIA
    from tests.fixtures.selecao import publicar_selecao, rascunho_aberto_com_documentos

    outro = publicar_selecao(
        api_client,
        # **Chave de idempotência própria**: o `manager_headers` traz uma fixa, e o segundo Processo
        # com a mesma chave é recusado como repetição do primeiro — que é exatamente o que a
        # idempotência existe para fazer.
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"029-segundo-{uuid.uuid4().hex[:8]}"},
        {
            **process_payload,
            "institutionalCode": f"PS-029-{uuid.uuid4().hex[:6]}",
            "firstEdital": {
                **process_payload["firstEdital"],
                "number": str(next(NUMERO)),
                "title": "Segundo certame da mesma pessoa",
            },
        },
        # **O rascunho precisa de identificadores próprios.** Os do `rascunho_aberto_com_documentos`
        # são fixos, e reaproveitá-los num segundo Edital é recusado com
        # `identifier_belongs_to_another_edital`: a identidade de um Perfil pertence ao Edital que a
        # publicou. `seed=1` traria identificadores distintos e um período **fechado**, e o que este
        # cenário precisa é dos dois — identificadores novos **e** inscrições abertas.
        rascunho=requerimento.com_identificadores_novos(
            rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1))
        ),
        antes_de_submeter=requerimento.declarar("AT_ENROLLMENT"),
    )
    perfil = PerfilVaga.objects.filter(edital=outro).first()
    return abrir_inscricao(identidade=MARIA, edital_id=outro.id, profile_id=perfil.id)
