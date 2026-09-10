"""Criar Edital a partir de Edital anterior (023).

**O que estes testes existem para pegar.** A cópia preserva a coerência interna do que copia: um
identificador da origem que escape do remapeamento continua consistente com os seus vizinhos e
atravessa a gravação sem recusa. Quatro referências não são conferidas na gravação — Anexo, Etapas
que o marco enumera, critério → Etapa/fato, e a Etapa de habilitação do sorteio —, e para essas
quatro o teste é a única guarda (T-005, FR-010a).

A origem destes cenários **usa todas as quatro**. Uma origem pobre não provaria nada.
"""

import json

import pytest
from django.utils import timezone

from processo_seletivo.editais.application.reaproveitamento import (
    origens_elegiveis,
    rascunho_vazio,
    reaproveitar_edital,
)
from processo_seletivo.editais.domain.secoes import e_textual
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.conftest import ator_institucional
from tests.fixtures.publicacao import publish_original
from tests.fixtures.sorteio import METODO


def ident(numero):
    return f"00000000-0000-0000-0000-0000000c{numero:04d}"


PERFIL = ident(1)
MODALIDADE = ident(2)
REGRA = ident(3)
FATO = ident(4)
MARCO = ident(5)
CRITERIO_ETAPA = ident(6)
CRITERIO_FATO = ident(7)
EVENTO_INSCRICAO = ident(8)
EVENTO_RESULTADO = ident(9)
ETAPA = ident(10)
DOCUMENTO_GERAL = ident(11)
DOCUMENTO_DO_PERFIL = ident(12)

IDENTIDADES_DA_ORIGEM = (
    PERFIL,
    MODALIDADE,
    REGRA,
    FATO,
    MARCO,
    CRITERIO_ETAPA,
    CRITERIO_FATO,
    EVENTO_INSCRICAO,
    EVENTO_RESULTADO,
    ETAPA,
    DOCUMENTO_GERAL,
    DOCUMENTO_DO_PERFIL,
)


def rascunho_rico():
    """Um Edital que usa tudo o que a cópia precisa carregar."""
    return {
        "profiles": [
            {
                "id": PERFIL,
                "code": "P1",
                "name": "Designer Educacional",
                "description": "Perfil da oferta anterior",
                "requirements": ["Graduação"],
                "immediateVacancies": 40,
                "reserveType": "LIMITED",
                "reserveLimit": 10,
                "locality": "Vitória",
                "duties": "Produzir material",
                "workload": "40h",
                "compensation": "R$ 4.200,00",
                "classificationInformation": {"texto": "sem tela"},
                "callInformation": {"texto": "sem tela"},
                "competitionModalities": [
                    {
                        "id": MODALIDADE,
                        "code": "AC",
                        "name": "Ampla concorrência",
                        "description": "Todos",
                        "normativeRule": {
                            "id": REGRA,
                            "foundation": "Lei 12.990/2014",
                            "version": "2014-06-09",
                            "percentage": "20.0000",
                            "calculation": {"modo": "PERCENTUAL"},
                            "rounding": {"scale": 0, "mode": "MEIO_PARA_CIMA"},
                            "distribution": {},
                            "callRules": {},
                            "effectiveFrom": "2026-01-01T00:00:00-03:00",
                        },
                    }
                ],
                "declaredFacts": [
                    {
                        "id": FATO,
                        "code": "NASCIMENTO",
                        "label": "Data de nascimento",
                        "type": "DATA",
                    }
                ],
                "classificationMilestones": [
                    {
                        "id": MARCO,
                        "code": "FINAL",
                        "name": "Classificação final",
                        "stages": [ETAPA],
                        "operation": "SOMA_PONDERADA",
                        "normalization": "NENHUMA",
                        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
                        "appealWindow": {
                            "admits": True,
                            "durationDays": 5,
                            "unit": "DIAS_CORRIDOS",
                        },
                        # A Etapa de habilitação é a mais traiçoeira das quatro referências: na
                        # gravação ela é conferida **apenas** contra as Etapas que o próprio marco
                        # enumera, e as duas vieram juntas da origem.
                        "drawMethod": {**METODO, "qualifyingStageId": ETAPA},
                        "tiebreakers": [
                            {
                                "id": CRITERIO_ETAPA,
                                "order": 1,
                                "type": "MAIOR_PONTUACAO_NA_ETAPA",
                                "parameters": {"stageId": ETAPA},
                                "whenMissing": "ULTIMO_NO_CRITERIO",
                            },
                            {
                                "id": CRITERIO_FATO,
                                "order": 2,
                                "type": "MENOR_VALOR_DE_FATO",
                                "parameters": {"factId": FATO},
                                "whenMissing": "CRITERIO_NAO_SE_APLICA",
                            },
                        ],
                    }
                ],
            }
        ],
        "schedule": [
            {
                "id": EVENTO_INSCRICAO,
                "type": "INSCRICAO",
                "description": "Período de inscrições",
                "startAt": "2025-09-01T09:00:00-03:00",
                "endAt": "2025-09-10T23:59:00-03:00",
                "order": 1,
                "status": "CONCLUIDO",
                "isRegistrationPeriod": True,
                "location": "Campus Vitória",
            },
            {
                "id": EVENTO_RESULTADO,
                "type": "RESULTADO",
                "description": "Resultado final",
                "startAt": "2025-10-01T09:00:00-03:00",
                "order": 2,
                "status": "CANCELADO",
            },
        ],
        "stages": [
            {
                "id": ETAPA,
                "name": "Prova de títulos",
                "order": 1,
                "weight": "1.5000",
                "classificatory": True,
                "minimumScore": "10.0000",
                "evaluationsPerRegistration": 2,
                "maximumScore": "100.0000",
                "scheduleEventId": EVENTO_INSCRICAO,
            }
        ],
        "documentRequirements": [
            {
                "id": DOCUMENTO_GERAL,
                "key": "identidade",
                "name": "Documento de identificação",
                "instructions": "frente e verso",
                "required": True,
                "order": 1,
            },
            {
                "id": DOCUMENTO_DO_PERFIL,
                "key": "diploma",
                "name": "Diploma de graduação",
                "required": True,
                "order": 2,
                "profileId": PERFIL,
                "modalityId": MODALIDADE,
            },
        ],
        "sections": [{"key": "apresentacao", "content": "Texto redigido para a oferta de 2025"}],
    }


def _vincular_anexo_e_fechar_cronograma(edital):
    """O que só existe **antes** da submissão: o vínculo com o Anexo e o estado dos Eventos."""
    anexo = edital.anexos.order_by("order").first()
    edital.documentos_exigidos.filter(key="diploma").update(anexo=anexo)


@pytest.fixture
def origem(db, api_client, manager_headers, process_payload):
    """Edital publicado, rico, com um Anexo que um requisito usa como modelo."""
    return publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho_rico(),
        anexos=1,
        antes_de_submeter=_vincular_anexo_e_fechar_cronograma,
    )


@pytest.fixture
def destino(db, api_client, manager_headers, origem):
    """Edital novo e vazio, em Processo próprio — a nova oferta."""
    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": "PS-2027-001",
            "title": "Processo Seletivo 2027",
            "firstEdital": {"number": "77", "year": 2027, "title": "Edital da nova oferta"},
        },
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "destino-key-0001"},
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


@pytest.fixture
def elaborador():
    return ator_institucional("preparadora", "edital:elaborar")


def copiar(destino, origem, elaborador, *, chave="reaproveitamento-0001"):
    return reaproveitar_edital(
        actor=elaborador,
        edital_id=destino.id,
        origem_id=origem.id,
        expected_revision=destino.revision,
        idempotency_key=chave,
        correlation_id="correlacao-023",
    )


# ---------------------------------------------------------------------------
# T011 — o rascunho vazio, coleção por coleção
# ---------------------------------------------------------------------------


def test_rascunho_vazio_e_o_edital_sem_nenhuma_das_seis_colecoes(destino):
    assert rascunho_vazio(destino) is True


def test_qualquer_uma_das_seis_colecoes_basta_para_o_rascunho_nao_estar_vazio(
    destino, origem, elaborador
):
    copiar(destino, origem, elaborador)
    destino.refresh_from_db()

    assert rascunho_vazio(destino) is False


# ---------------------------------------------------------------------------
# T013 / T014 — a cópia, e a origem intacta
# ---------------------------------------------------------------------------


def test_a_copia_traz_as_colecoes_da_origem(destino, origem, elaborador):
    copiado = copiar(destino, origem, elaborador)

    perfil = copiado.perfis.get()
    assert perfil.code == "P1"
    assert perfil.immediate_vacancies == 40
    assert perfil.reserve_limit == 10
    assert perfil.modalidades.count() == 1
    assert perfil.modalidades.get().regra_normativa.foundation == "Lei 12.990/2014"
    assert perfil.fatos.count() == 1
    assert perfil.marcos.count() == 1
    assert perfil.marcos.get().criterios.count() == 2
    assert copiado.cronograma.eventos.count() == 2
    assert copiado.etapas.count() == 1
    assert copiado.documentos_exigidos.count() == 2
    assert copiado.anexos.count() == 1


def test_as_secoes_copiadas_sao_as_textuais_do_catalogo(destino, origem, elaborador):
    """Todas as textuais, e não só a editada — é o efeito colateral que `T-006` declara.

    O conteúdo publicado traz o padrão do catálogo quando não há linha, então a cópia persiste linha
    para cada textual. É indistinguível do que o assistente produz quando alguém abre e grava a
    etapa `Conteúdo`, e não altera o documento publicado. Gerada nenhuma entra: `_validar_secoes` as
    recusa, e com razão.
    """
    copiado = copiar(destino, origem, elaborador)

    chaves = set(copiado.secoes.values_list("key", flat=True))
    assert chaves and all(e_textual(chave) for chave in chaves)
    assert copiado.secoes.get(key="apresentacao").content == (
        "Texto redigido para a oferta de 2025"
    )


def test_nenhuma_identidade_e_compartilhada_com_a_origem(destino, origem, elaborador):
    copiado = copiar(destino, origem, elaborador)

    do_destino = {
        *(str(item) for item in copiado.perfis.values_list("id", flat=True)),
        *(str(item) for item in copiado.etapas.values_list("id", flat=True)),
        *(str(item) for item in copiado.documentos_exigidos.values_list("id", flat=True)),
        *(str(item) for item in copiado.anexos.values_list("id", flat=True)),
        *(str(item) for item in copiado.cronograma.eventos.values_list("id", flat=True)),
    }

    assert do_destino.isdisjoint(IDENTIDADES_DA_ORIGEM)


def test_o_edital_de_destino_permanece_em_elaboracao(destino, origem, elaborador):
    copiado = copiar(destino, origem, elaborador)

    assert copiado.status == Edital.Status.EM_ELABORACAO
    assert copiado.number == "77" and copiado.year == 2027
    assert copiado.title == "Edital da nova oferta"


def test_a_origem_nao_se_move(destino, origem, elaborador):
    antes = (
        origem.status,
        origem.revision,
        VersaoConsolidada.objects.filter(edital=origem).count(),
        origem.perfis.count(),
        origem.anexos.count(),
    )

    copiar(destino, origem, elaborador)

    origem.refresh_from_db()
    assert antes == (
        origem.status,
        origem.revision,
        VersaoConsolidada.objects.filter(edital=origem).count(),
        origem.perfis.count(),
        origem.anexos.count(),
    )


def test_a_elegibilidade_da_origem_tem_dois_lados(destino, origem, elaborador):
    """Publicado e encerrado são aceitos; é a outra metade da fronteira (FR-004)."""
    assert origem in origens_elegiveis(elaborador)

    Edital.objects.filter(pk=origem.pk).update(status=Edital.Status.ENCERRADO)
    origem.refresh_from_db()
    assert origem in origens_elegiveis(elaborador)

    copiado = copiar(destino, origem, elaborador)
    assert copiado.perfis.count() == 1


# ---------------------------------------------------------------------------
# T024 — nada da execução da origem vem junto
# ---------------------------------------------------------------------------


def _dar_execucao_a(edital):
    """Inscrições, comissão e alocação na origem, para que o isolamento não seja vacuidade."""
    from processo_seletivo.comissoes.models import AlocacaoEtapa, Funcao, MembroComissao
    from processo_seletivo.inscricoes.models import Inscricao

    perfil = edital.perfis.get()
    agora = timezone.now()
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    Inscricao.objects.create(
        identity_subject="maria",
        edital=edital,
        profile_id=perfil.id,
        status=Inscricao.Status.SUBMETIDA,
        created_at=agora,
        submitted_at=agora,
        # O que a submissão exige do banco: versão aceita, declarações, protocolo e CPF.
        versao_aceita=vigente,
        versao_reconhecida=vigente,
        declaracoes_aceitas_em=agora,
        protocolo="INS-2025-0001",
        nome="Maria",
        cpf="123.456.789-09",
        cpf_normalizado="12345678909",
        email="maria@exemplo.test",
    )
    Inscricao.objects.create(
        identity_subject="joao", edital=edital, profile_id=perfil.id, created_at=agora
    )
    membro = MembroComissao.objects.create(
        processo=edital.processo,
        identity_subject="avaliador",
        display_label="Avaliador",
        funcao=Funcao.MEMBRO,
        criado_em=agora,
        criado_por="gestor-a",
    )
    AlocacaoEtapa.objects.create(
        membro=membro,
        edital=edital,
        etapa_id=edital.etapas.get().id,
        criado_em=agora,
        criado_por="gestor-a",
    )
    return edital


def test_nada_da_execucao_da_origem_vem_junto(destino, origem, elaborador):
    """A origem tem certame; o destino nasce vazio dele (FR-013, SC-006)."""
    from processo_seletivo.comissoes.models import MembroComissao
    from processo_seletivo.recursos.models import Recurso

    _dar_execucao_a(origem)
    assert origem.inscricoes.count() == 2
    assert origem.alocacoes.count() == 1

    copiado = copiar(destino, origem, elaborador)

    assert copiado.inscricoes.count() == 0
    assert copiado.alocacoes.count() == 0
    assert copiado.atribuicoes.count() == 0
    assert copiado.resultados.count() == 0
    assert copiado.sorteios.count() == 0
    assert copiado.relacoes_de_sorteio.count() == 0
    assert Recurso.objects.filter(inscricao__edital=copiado).count() == 0
    # A comissão é do **Processo**, não do Edital: não há o que proibir porque não se clona
    # Processo. O que se confere é que o Processo de destino segue com a comissão que ele tinha.
    assert MembroComissao.objects.filter(processo=copiado.processo).count() == 0
    assert MembroComissao.objects.filter(processo=origem.processo).count() == 1


# ---------------------------------------------------------------------------
# T025 a T028 — as quatro referências que a gravação não confere
#
# Cada uma tem a **contraprova**: com aquele remapeamento desfeito, a gravação **passa**. É o que
# justifica um teste por referência em vez de uma verificação genérica (T-005, FR-010a).
# ---------------------------------------------------------------------------


def gravar_sem_remapear(destino, elaborador, origem, desfazer):
    """Grava o rascunho com um remapeamento desfeito, para provar que a gravação não o recusa.

    `attachmentId` é zerado por padrão: apontar o Anexo do destino exigiria criá-lo, e estes
    cenários não estão testando a cópia de bytes.
    """
    from processo_seletivo.editais.application.draft import replace_draft
    from processo_seletivo.editais.domain.reaproveitamento import (
        converter_valores,
        mapa_de_identidades,
        payload_do_conteudo,
        remapear,
    )
    from processo_seletivo.publicacoes.application.selectors import effective_version
    from processo_seletivo.publicacoes.domain.elevacao import elevar

    conteudo = elevar(effective_version(edital_id=origem.id).content)
    mapa = mapa_de_identidades(conteudo)
    payload = payload_do_conteudo(converter_valores(remapear(conteudo, mapa)))
    for documento in payload["documentRequirements"]:
        documento["attachmentId"] = None
    desfazer(payload, mapa)
    replace_draft(
        actor=elaborador,
        edital_id=destino.id,
        expected_revision=destino.revision,
        profiles=payload["profiles"],
        schedule=payload["schedule"],
        stages=payload["stages"],
        sections=payload["sections"],
        document_requirements=payload["documentRequirements"],
        correlation_id="contraprova",
        area="contraprova",
    )
    destino.refresh_from_db()
    return destino


def test_o_documento_exigido_aponta_o_anexo_do_destino(destino, origem, elaborador):
    copiado = copiar(destino, origem, elaborador)

    documento = copiado.documentos_exigidos.get(key="diploma")
    anexo_do_destino = copiado.anexos.get()
    assert documento.anexo_id == anexo_do_destino.id
    assert documento.anexo_id != origem.anexos.get().id
    # Os bytes são os mesmos; o artefato, não — e o do destino é rascunho, substituível.
    assert anexo_do_destino.artefato_id != origem.anexos.get().artefato_id
    assert bytes(anexo_do_destino.artefato.bytes) == bytes(origem.anexos.get().artefato.bytes)
    assert anexo_do_destino.artefato.congelado_em is None
    assert origem.anexos.get().artefato.congelado_em is not None


def test_contraprova_do_anexo_a_gravacao_aceita_o_vinculo_da_origem(destino, origem, elaborador):
    """A referência pendurada só é impedida na **publicação** — aqui ela passa."""
    anexo_da_origem = origem.anexos.get()

    def desfazer(payload, mapa):
        payload["documentRequirements"][1]["attachmentId"] = str(anexo_da_origem.id)

    gravado = gravar_sem_remapear(destino, elaborador, origem, desfazer)

    assert gravado.documentos_exigidos.get(key="diploma").anexo_id == anexo_da_origem.id


def test_o_marco_enumera_etapa_do_destino(destino, origem, elaborador):
    copiado = copiar(destino, origem, elaborador)

    marco = copiado.perfis.get().marcos.get()
    etapa_do_destino = copiado.etapas.get()
    assert [str(item) for item in marco.etapas] == [str(etapa_do_destino.id)]
    assert str(origem.etapas.get().id) not in [str(item) for item in marco.etapas]


def test_contraprova_do_marco_a_gravacao_aceita_etapa_da_origem(destino, origem, elaborador):
    etapa_da_origem = str(origem.etapas.get().id)

    def desfazer(payload, mapa):
        marco = payload["profiles"][0]["classificationMilestones"][0]
        marco["stages"] = [etapa_da_origem]
        # Junto, porque é assim que o esquecimento acontece: a coerência interna do marco se
        # mantém, e é justamente isso que faz a gravação passar.
        marco["drawMethod"]["qualifyingStageId"] = etapa_da_origem

    gravado = gravar_sem_remapear(destino, elaborador, origem, desfazer)

    assert [str(item) for item in gravado.perfis.get().marcos.get().etapas] == [etapa_da_origem]


def test_o_critério_de_desempate_aponta_etapa_e_fato_do_destino(destino, origem, elaborador):
    copiado = copiar(destino, origem, elaborador)

    marco = copiado.perfis.get().marcos.get()
    por_etapa = marco.criterios.get(ordem=1)
    por_fato = marco.criterios.get(ordem=2)
    assert por_etapa.parametros["stageId"] == str(copiado.etapas.get().id)
    assert por_fato.parametros["factId"] == str(copiado.perfis.get().fatos.get().id)
    assert por_etapa.parametros["stageId"] != str(origem.etapas.get().id)
    assert por_fato.parametros["factId"] != str(origem.perfis.get().fatos.get().id)


def test_contraprova_do_critério_a_gravacao_aceita_etapa_e_fato_da_origem(
    destino, origem, elaborador
):
    etapa_da_origem = str(origem.etapas.get().id)
    fato_da_origem = str(origem.perfis.get().fatos.get().id)

    def desfazer(payload, mapa):
        criterios = payload["profiles"][0]["classificationMilestones"][0]["tiebreakers"]
        criterios[0]["parameters"] = {"stageId": etapa_da_origem}
        criterios[1]["parameters"] = {"factId": fato_da_origem}

    gravado = gravar_sem_remapear(destino, elaborador, origem, desfazer)

    marco = gravado.perfis.get().marcos.get()
    assert marco.criterios.get(ordem=1).parametros["stageId"] == etapa_da_origem
    assert marco.criterios.get(ordem=2).parametros["factId"] == fato_da_origem


def test_o_metodo_do_sorteio_habilita_por_etapa_do_destino(destino, origem, elaborador):
    copiado = copiar(destino, origem, elaborador)

    metodo = copiado.perfis.get().marcos.get().metodo_de_sorteio
    assert metodo["qualifyingStageId"] == str(copiado.etapas.get().id)
    assert metodo["qualifyingStageId"] != str(origem.etapas.get().id)


def test_contraprova_do_sorteio_a_coerencia_interna_e_o_que_faz_a_gravacao_passar(
    destino, origem, elaborador
):
    """O mais traiçoeiro dos quatro: a Etapa de habilitação é conferida **contra o próprio marco**.

    Desfazer os dois juntos — as Etapas enumeradas e a de habilitação — mantém o marco coerente
    consigo mesmo, e a gravação não tem como recusar.
    """
    etapa_da_origem = str(origem.etapas.get().id)

    def desfazer(payload, mapa):
        marco = payload["profiles"][0]["classificationMilestones"][0]
        marco["stages"] = [etapa_da_origem]
        marco["drawMethod"]["qualifyingStageId"] = etapa_da_origem

    gravado = gravar_sem_remapear(destino, elaborador, origem, desfazer)

    metodo = gravado.perfis.get().marcos.get().metodo_de_sorteio
    assert metodo["qualifyingStageId"] == etapa_da_origem


# ---------------------------------------------------------------------------
# T029 / T030 — o que reinicia e o que não vem
# ---------------------------------------------------------------------------


def test_o_calendario_nao_vem_cumprido(destino, origem, elaborador):
    """`CONCLUIDO` e `CANCELADO` na origem; `PLANEJADO` no destino (FR-008a)."""
    situacoes_da_origem = set(origem.cronograma.eventos.values_list("status", flat=True))
    assert situacoes_da_origem == {"CONCLUIDO", "CANCELADO"}

    copiado = copiar(destino, origem, elaborador)

    assert set(copiado.cronograma.eventos.values_list("status", flat=True)) == {"PLANEJADO"}
    periodo = copiado.cronograma.eventos.get(is_registration_period=True)
    assert periodo.type == "INSCRICAO"
    assert periodo.location == "Campus Vitória"


def test_o_que_nao_tem_tela_nao_vem(destino, origem, elaborador):
    """Os três campos normativos que nenhuma etapa do assistente desenha (FR-008)."""
    Edital.objects.filter(pk=origem.pk).update(max_inscricoes_por_candidato=1)
    assert origem.perfis.get().classification_information == {"texto": "sem tela"}

    copiado = copiar(destino, origem, elaborador)

    perfil = copiado.perfis.get()
    assert perfil.classification_information == {}
    assert perfil.call_information == {}
    assert copiado.max_inscricoes_por_candidato is None


# ---------------------------------------------------------------------------
# T031 / T031a — a versão, que é o que separa esta cópia de uma cópia de tabelas
# ---------------------------------------------------------------------------


def test_a_copia_parte_da_versao_vigente_e_nao_do_estado_relacional(
    destino, origem, elaborador, api_client
):
    """Origem retificada: o destino nasce com o valor **retificado** (SC-008, D-003).

    A Retificação não reescreve `PerfilVaga` — ela produz versão consolidada nova. Se a cópia lesse
    as tabelas, traria 40 vagas, que é o que está gravado; o que vigora é 50.
    """
    from tests.fixtures.publicacao import retify

    retify(
        api_client,
        origem,
        [
            {
                "targetPath": f"/profiles/id={PERFIL}/immediateVacancies",
                "operation": "REPLACE",
                "newValue": 50,
            }
        ],
    )
    origem.refresh_from_db()
    assert origem.perfis.get().immediate_vacancies == 40, "a tabela segue no dia da publicação"

    copiado = copiar(destino, origem, elaborador)

    assert copiado.perfis.get().immediate_vacancies == 50


def test_a_copia_eleva_conteudo_de_esquema_anterior(destino, origem, elaborador, monkeypatch):
    """Versão vigente num degrau antigo: o destino sai completo e no esquema atual (FR-005).

    A versão publicada é **imutável por trigger** — `publicacoes_versaoconsolidada` é append-only —,
    então o conteúdo legado chega pelo leitor, e não por `UPDATE`. O que se exerce é a integração
    `elevar → copiar`, e não a leitura: sem a elevação, o rascunho nasceria sem o que o degrau
    antigo não declarava.
    """
    from processo_seletivo.editais.application import reaproveitamento as servico
    from processo_seletivo.publicacoes.application.selectors import effective_version

    vigente = effective_version(edital_id=origem.id)
    legado = {
        chave: valor for chave, valor in vigente.content.items() if chave not in ("attachments",)
    }
    legado["schemaVersion"] = 8
    for perfil in legado["profiles"]:
        for marco in perfil.get("classificationMilestones") or []:
            marco.pop("drawMethod", None)
    for documento in legado["documentRequirements"]:
        documento.pop("attachmentId", None)

    class VersaoLegada:
        pk = vigente.pk
        content = legado

    monkeypatch.setattr(servico, "effective_version", lambda **_: VersaoLegada())

    copiado = servico.reaproveitar_edital(
        actor=elaborador,
        edital_id=destino.id,
        origem_id=origem.id,
        expected_revision=destino.revision,
        idempotency_key="legado-0001",
        correlation_id="correlacao-023",
    )

    assert copiado.perfis.count() == 1
    assert copiado.etapas.count() == 1
    assert copiado.cronograma.eventos.count() == 2
    # O degrau 8 não declarava método de sorteio nem anexo: a ausência é o que ele afirma, e a
    # elevação não inventa o que ele não disse.
    assert copiado.perfis.get().marcos.get().metodo_de_sorteio in ({}, None)
    assert copiado.anexos.count() == 0
    assert copiado.documentos_exigidos.filter(anexo__isnull=False).count() == 0


# ---------------------------------------------------------------------------
# T032 / T033 — atomicidade, idempotência e independência
# ---------------------------------------------------------------------------


def test_falha_depois_dos_anexos_nao_deixa_destino_pela_metade(
    destino, origem, elaborador, monkeypatch
):
    """Os Anexos vêm antes do conteúdo; se o conteúdo falhar, eles não podem ficar (FR-017).

    Anexo criado sem o requisito que o usa é conteúdo órfão — e é por isso que os dois estão na
    mesma transação, e não em duas.
    """
    from processo_seletivo.editais.application import reaproveitamento as servico

    def explodir(**_):
        raise RuntimeError("falha depois dos anexos")

    monkeypatch.setattr(servico, "replace_draft", explodir)

    with pytest.raises(RuntimeError):
        copiar(destino, origem, elaborador)

    destino.refresh_from_db()
    assert destino.anexos.count() == 0
    assert destino.perfis.count() == 0
    assert rascunho_vazio(destino) is True


def test_a_repeticao_com_a_mesma_chave_devolve_o_mesmo_edital(destino, origem, elaborador):
    """E **não** `draft_not_empty`: depois da primeira cópia o rascunho já está cheio (FR-017a).

    É o defeito que só a segunda requisição revela. Conferir a precondição antes da chave faria toda
    repetição virar recusa — e a operação seria idempotente em tudo, menos no caso em que a
    idempotência serve.
    """
    primeiro = copiar(destino, origem, elaborador)
    antes = (primeiro.revision, primeiro.perfis.count(), primeiro.anexos.count())

    segundo = reaproveitar_edital(
        actor=elaborador,
        edital_id=destino.id,
        origem_id=origem.id,
        expected_revision=primeiro.revision,
        idempotency_key="reaproveitamento-0001",
        correlation_id="correlacao-023",
    )

    assert segundo.pk == primeiro.pk
    segundo.refresh_from_db()
    assert (segundo.revision, segundo.perfis.count(), segundo.anexos.count()) == antes


def test_outra_chave_sobre_rascunho_cheio_e_recusada(destino, origem, elaborador):
    """A precondição continua de pé: o que a reserva dispensa é a **repetição**, não a regra.

    Com a revisão corrente — para que a recusa observada seja a do rascunho cheio, e não a da
    revisão obsoleta, que é outra conversa e vem antes.
    """
    from processo_seletivo.shared.api.problems import DomainError

    copiado = copiar(destino, origem, elaborador)
    copiado.refresh_from_db()

    with pytest.raises(DomainError) as recusa:
        reaproveitar_edital(
            actor=elaborador,
            edital_id=copiado.id,
            origem_id=origem.id,
            expected_revision=copiado.revision,
            idempotency_key="outra-0002",
            correlation_id="correlacao-023",
        )

    assert recusa.value.code == "draft_not_empty"


def test_alterar_o_destino_nao_alcanca_a_origem(destino, origem, elaborador):
    copiado = copiar(destino, origem, elaborador)
    conteudo_da_origem = origem.perfis.get()

    copiado.perfis.update(immediate_vacancies=99, name="Perfil da nova oferta")

    conteudo_da_origem.refresh_from_db()
    assert conteudo_da_origem.immediate_vacancies == 40
    assert conteudo_da_origem.name == "Designer Educacional"


def test_retificar_a_origem_depois_da_copia_nao_alcanca_o_destino(
    destino, origem, elaborador, api_client
):
    copiado = copiar(destino, origem, elaborador)

    from tests.fixtures.publicacao import retify

    retify(
        api_client,
        origem,
        [
            {
                "targetPath": f"/profiles/id={PERFIL}/name",
                "operation": "REPLACE",
                "newValue": "Nome retificado",
            }
        ],
    )

    copiado.refresh_from_db()
    assert copiado.perfis.get().name == "Designer Educacional"


# ---------------------------------------------------------------------------
# T034 — o registro de origem
# ---------------------------------------------------------------------------


def test_a_trilha_registra_a_versao_o_ator_e_o_instante(destino, origem, elaborador, api_client):
    """A **versão**, e não o Edital: é ela que preserva *independência e versão* (FR-015a).

    E é ela que sobrevive: retificada a origem depois da cópia, o registro continua apontando a
    versão de onde o conteúdo de fato saiu.
    """
    from processo_seletivo.auditoria.models import RegistroAuditoria
    from processo_seletivo.editais.application.reaproveitamento import OPERACAO
    from processo_seletivo.publicacoes.application.selectors import effective_version

    versao = effective_version(edital_id=origem.id)

    copiado = copiar(destino, origem, elaborador)

    registro = RegistroAuditoria.objects.get(operation=OPERACAO, aggregate_id=copiado.pk)
    assert registro.aggregate_type == "Edital"
    assert registro.actor_subject == "preparadora"
    assert registro.permission == "edital:elaborar"
    assert registro.new_state == Edital.Status.EM_ELABORACAO
    assert registro.reason == str(versao.pk)
    assert registro.correlation_id == "correlacao-023"
    # A versão nomeada resolve as duas perguntas: o Edital deriva dela.
    assert VersaoConsolidada.objects.get(pk=registro.reason).edital_id == origem.pk

    from tests.fixtures.publicacao import retify

    retify(
        api_client,
        origem,
        [
            {
                "targetPath": f"/profiles/id={PERFIL}/name",
                "operation": "REPLACE",
                "newValue": "Nome retificado",
            }
        ],
    )

    registro.refresh_from_db()
    assert registro.reason == str(versao.pk)


def test_a_gravacao_do_rascunho_nao_marca_etapa_nenhuma_como_composta(destino, origem, elaborador):
    """A área da gravação não é nome de etapa, de propósito (T-004).

    Vazia, devolveria o registro indistinguível que a `006` corrigiu; com nome de etapa, afirmaria
    que alguém a compôs.
    """
    from processo_seletivo.auditoria.models import RegistroAuditoria
    from processo_seletivo.editais.application.reaproveitamento import AREA

    copiado = copiar(destino, origem, elaborador)

    registro = RegistroAuditoria.objects.get(operation="ALTERAR_RASCUNHO", aggregate_id=copiado.pk)
    assert registro.reason == AREA
    assert registro.reason.strip() != ""


def test_a_origem_nao_entra_no_conteudo_canonico_do_destino(destino, origem, elaborador):
    """Proveniência de autoria não é norma (FR-016).

    O Edital novo **não publica** que foi copiado de outro: a origem vive na trilha, que é onde os
    atos vivem, e não no conteúdo que vira documento. Um vínculo no conteúdo seria também a segunda
    aresta Edital → Edital que a régua de tamanho recusa por colidir com P-6.
    """
    from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot

    copiado = copiar(destino, origem, elaborador)

    serializado = json.dumps(edital_snapshot(copiado), default=str)
    assert str(origem.pk) not in serializado
    assert f'"{origem.number}"' not in serializado
    for identidade in IDENTIDADES_DA_ORIGEM:
        assert identidade not in serializado


def test_a_versao_copiada_e_a_vigente_no_instante_do_comando(destino, origem, elaborador):
    """`at=now`, e não o instante que o seletor tomaria sozinho.

    `effective_version` chama `timezone.now()` quando não recebe o instante, e a auditoria registra
    o `now` da abertura do comando. Os dois são quase o mesmo — e "quase" é o problema: uma vigência
    programada que comece no meio da transação faria o evento afirmar um instante **anterior** à
    versão que ele diz ter copiado, e a proveniência deixaria de fechar.

    O que se prende aqui é a âncora, e não a semântica do seletor: a versão lida é a que vigorava no
    instante que o registro carimba.
    """
    from processo_seletivo.auditoria.models import RegistroAuditoria
    from processo_seletivo.editais.application import reaproveitamento as servico
    from processo_seletivo.editais.application.reaproveitamento import OPERACAO

    original = servico.effective_version
    instantes = []

    def registrando(**kwargs):
        instantes.append(kwargs.get("at"))
        return original(**kwargs)

    servico.effective_version = registrando
    try:
        copiado = copiar(destino, origem, elaborador)
    finally:
        servico.effective_version = original

    registro = RegistroAuditoria.objects.get(operation=OPERACAO, aggregate_id=copiado.pk)
    assert instantes == [registro.occurred_at]


def test_duas_versoes_da_mesma_origem_nao_se_anunciam_iguais(
    destino, origem, elaborador, api_client
):
    """Data não nomeia versão (FR-014a, SC-005).

    Publicar uma Retificação rematerializa **uma versão por fronteira temporal**, e as fronteiras
    caem no mesmo dia — no mesmo minuto, num teste. Enquanto a tela dizia só *"versão de
    09/09/2026"*, duas linhas com identificadores e conteúdos distintos apareciam com a mesma frase,
    e quem lesse a trilha não teria como saber de qual se partiu.
    """
    from processo_seletivo.interface.views import _versao_por_extenso
    from tests.fixtures.publicacao import retify

    primeira = VersaoConsolidada.objects.filter(edital=origem).latest("materialized_at")
    retify(
        api_client,
        origem,
        [
            {
                "targetPath": f"/profiles/id={PERFIL}/name",
                "operation": "REPLACE",
                "newValue": "Nome retificado",
            }
        ],
    )
    segunda = VersaoConsolidada.objects.filter(edital=origem).latest("materialized_at")

    assert primeira.pk != segunda.pk
    assert _versao_por_extenso(primeira) != _versao_por_extenso(segunda)


# ---------------------------------------------------------------------------
# A escolha da origem: localizar e saber o que cada uma traz (FR-004, FR-004a)
# ---------------------------------------------------------------------------


def test_a_busca_localiza_pelos_atributos_que_a_lista_mostra(origem, elaborador):
    """`FR-004` pede a origem **localizável** pelos atributos com que ela é identificada."""
    from processo_seletivo.editais.application.reaproveitamento import origens_elegiveis

    assert list(origens_elegiveis(elaborador, busca=origem.number)) == [origem]
    assert list(origens_elegiveis(elaborador, busca="2026")) == [origem]
    assert list(origens_elegiveis(elaborador, busca="Primeiro Edital")) == [origem]
    assert list(origens_elegiveis(elaborador, busca="PS-2026-001")) == [origem]
    assert list(origens_elegiveis(elaborador, busca="Processo Seletivo 2026")) == [origem]
    assert list(origens_elegiveis(elaborador, busca="nada disso existe")) == []


def test_o_ano_so_entra_na_busca_quando_o_termo_e_um_ano():
    """Ano é inteiro: comparar inteiro por semelhança de texto devolve o que ninguém pediu.

    Contra a expressão, e não contra o resultado: uma origem qualquer casa "202" pelo código do
    Processo — `PS-2026-001` contém o pedaço —, e o resultado não distinguiria o acerto pelo campo
    certo do acerto por acidente.
    """
    from processo_seletivo.editais.application.reaproveitamento import _procura_por

    def compara_ano(procura):
        return "year" in str(procura)

    assert compara_ano(_procura_por("2026"))
    assert not compara_ano(_procura_por("202"))
    assert not compara_ano(_procura_por("20261"))
    assert not compara_ano(_procura_por("Multimídia"))


def test_o_resumo_conta_o_conteudo_que_vigora_e_nao_as_tabelas(origem, elaborador, api_client):
    """A coluna promete o que a cópia entrega, e é por isso que ela não conta nas tabelas.

    A Retificação não reescreve `EventoCronograma`: contar ali anunciaria dois Eventos numa origem
    que hoje vigora com três — e a cópia traria três. É a mesma razão de `D-003`, na apresentação.
    """
    from processo_seletivo.editais.application.reaproveitamento import com_resumo_da_origem
    from tests.fixtures.publicacao import retify

    antes = com_resumo_da_origem([origem])[0].resumo
    assert antes == {"perfis": 1, "eventos": 2, "etapas": 1, "documentos": 2, "anexos": 1}

    retify(
        api_client,
        origem,
        [
            {
                "targetPath": "/schedule/-",
                "operation": "ADD",
                "newValue": {
                    "id": ident(20),
                    "type": "MATRICULA",
                    "description": "Matrícula",
                    "startAt": "2025-11-01T09:00:00-03:00",
                    "endAt": None,
                    "order": 3,
                    "status": "PLANEJADO",
                    "isRegistrationPeriod": False,
                    "location": "",
                },
            }
        ],
    )
    origem.refresh_from_db()

    depois = com_resumo_da_origem([origem])[0].resumo
    assert origem.cronograma.eventos.count() == 2, "a tabela segue no dia da publicação"
    assert depois["eventos"] == 3


def test_o_resumo_de_uma_origem_sem_versao_nao_derruba_a_lista(destino, elaborador):
    """Não deveria existir Edital publicado sem versão — e a lista não é o lugar de descobrir."""
    from processo_seletivo.editais.application.reaproveitamento import com_resumo_da_origem

    Edital.objects.filter(pk=destino.pk).update(status=Edital.Status.PUBLICADO)
    destino.refresh_from_db()

    resumido = com_resumo_da_origem([destino])[0]

    assert resumido.resumo == {
        "perfis": 0,
        "eventos": 0,
        "etapas": 0,
        "documentos": 0,
        "anexos": 0,
    }
    assert resumido.publicado_em is None
