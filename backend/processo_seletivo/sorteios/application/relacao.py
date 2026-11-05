"""Publicar a relação de habilitados — que **é** congelá-la (FR-001, FR-006, FR-007).

**Não há estado "publicada, não congelada".** Uma relação publicada e ainda editável seria
exatamente a janela que esta feature existe para fechar: universo conhecido, compromisso ausente.
Os dois atos da spec são um só instante, e é por isso que este módulo tem um comando de publicação
e nenhum de congelamento.

**No mesmo instante nascem dois compromissos.** O do universo — quem está na relação, com que número
— e o do **método**, citado por resumo (FR-067). Sem o segundo, qual método governa o sorteio seria
resolvido no instante da execução, isto é, depois da semente: a comissão declararia vários métodos,
cada um apontando uma ocorrência diferente, e escolheria o conveniente conhecendo o efeito de cada
um (D-014).
"""

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.avaliacoes.domain.conjunto import (
    CONGELAR_A_RELACAO,
    recusa_por_inscricoes_em_curso,
)
from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.editais.domain.recortes import exigir_recorte_operacional
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.canonical import canonical_sha256
from processo_seletivo.sorteios.application import conferencia
from processo_seletivo.sorteios.application.habilitacao import habilitadas_na_etapa, nome_da_etapa
from processo_seletivo.sorteios.domain import conferencia as dominio_da_conferencia
from processo_seletivo.sorteios.domain import metodo as dominio_do_metodo
from processo_seletivo.sorteios.domain import projecao
from processo_seletivo.sorteios.models import ParticipanteHabilitado, RelacaoDeHabilitados

PUBLICAR = "SORTEIO_PUBLICAR_RELACAO"
ATO = "sorteios:publicar-relacao"


def publicar_relacao(
    *,
    actor,
    processo_id,
    edital_id,
    perfil_id,
    marco_id,
    lista_id=None,
    idempotency_key,
    correlation_id,
    motivo="",
):
    """Projeta, numera, cita o método e publica. Havendo vigente, sucede — nunca edita."""
    # **A conferência do concurso antes da transação** (116, FR-3636): ela é de rede, e a trava do
    # Processo não pode esperar a Caixa. Dentro, só vale para o método da versão relida.
    situacoes = _consultar_antes_de_congelar(
        actor, edital_id, perfil_id, marco_id, idempotency_key=idempotency_key
    )
    payload = {
        "edital": str(edital_id),
        "perfil": str(perfil_id),
        "marco": str(marco_id),
        "lista": str(lista_id) if lista_id else "",
        "motivo": (motivo or "").strip(),
    }
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        edital = _edital_do_processo(ctx.processo, edital_id)
        versao = effective_version(edital_id=edital.id, at=ctx.now)
        # **A Modalidade apontada como a ampla não tem relação própria** (122, FR-3897). A recusa é
        # sob a trava e sobre a versão relida, antes de qualquer outra: a relação da ampla já a
        # inclui, e congelar a dela produziria a lista que a ocupação não consome.
        exigir_recorte_operacional(versao.content, perfil_id=perfil_id, lista_id=lista_id)
        # **O método antes de qualquer coisa.** Recusar aqui é o que impede congelar sob método
        # indefinido, e a recusa nomeia o Edital como o lugar da correção (FR-066).
        metodo, metodo_hash = dominio_do_metodo.exigir_metodo(
            versao.content, perfil_id=perfil_id, marco_id=marco_id
        )
        # **O universo fechado antes do compromisso** (US1: "Encerradas as inscrições, quem
        # conduz o certame publica a relação"). Congelada com o período correndo, a relação deixava
        # de fora quem se inscrevesse depois, e a saída era um segundo ato público para corrigir o
        # primeiro. A regra é a da distribuição, e é a mesma função: as duas partem do mesmo fato.
        # Vale também para a sucessora — uma relação nova com o período aberto repete o defeito.
        recusa = recusa_por_inscricoes_em_curso(
            versao.content, ctx.now, consequencia=CONGELAR_A_RELACAO
        )
        if recusa is not None:
            raise recusa
        conferidas = conferencia.conferidas(
            _referencias_do_congelamento(metodo, perfil_id, marco_id), situacoes, agora=ctx.now
        )
        _recusar_concurso_realizado(conferidas, correlation_id=correlation_id)
        vigente = _vigente(edital, perfil_id, marco_id, lista_id)
        texto_do_motivo = (motivo or "").strip()
        if vigente is not None and not texto_do_motivo:
            raise DomainError(
                "relation_succession_reason_required",
                "Declare o motivo da sucessão da relação vigente. A relação publicada é o "
                "compromisso do universo: substituí-la sem razão escrita apagaria o compromisso "
                "sem que ninguém respondesse por isso.",
                422,
                campo="motivo",
            )
        participantes = _projetar(edital, versao, perfil_id, marco_id, lista_id)
        if not participantes:
            raise DomainError(
                "relation_would_be_empty",
                "Não há inscrição submetida no recorte: não existe universo a comprometer.",
                422,
            )
        criterio_publicado = projecao.criterio(
            lista_id=lista_id,
            nome_da_modalidade=_nome_da_modalidade(versao.content, perfil_id, lista_id),
            quantidade=len(participantes),
            # **A Etapa de habilitação entra na frase publicada** (FR-011, R-012). Sem ela, o
            # critério dizia "todas as inscrições submetidas" numa relação que exclui quem não
            # passou na Etapa anterior — e quem ficou de fora não tinha, no texto publicado, o que
            # explicasse a própria ausência.
            nome_da_etapa=nome_da_etapa(versao.content, metodo.get("qualifyingStageId")),
        )
        relacao = RelacaoDeHabilitados(
            edital=edital,
            perfil_id=identificador(perfil_id),
            marco_id=identificador(marco_id),
            lista_id=identificador(lista_id) if lista_id else None,
            versao=versao,
            metodo_hash=metodo_hash,
            criterio_de_projecao=criterio_publicado,
            quantidade=len(participantes),
            publicada_em=ctx.now,
            publicada_por=actor.subject,
            relacao_anterior=vigente,
            motivo_da_sucessao=texto_do_motivo,
        )
        # O resumo cobre a identidade da própria relação, e por isso ele é calculado depois de o
        # objeto existir em memória — e antes de a linha ser gravada, porque a linha é imutável.
        relacao.resumo = canonical_sha256(
            projecao.conteudo_canonico(
                relacao_id=relacao.id,
                edital_id=edital.id,
                versao_id=versao.id,
                perfil_id=perfil_id,
                marco_id=marco_id,
                lista_id=lista_id,
                metodo_hash=metodo_hash,
                criterio_publicado=criterio_publicado,
                participantes=participantes,
            )
        )
        relacao.save()
        ParticipanteHabilitado.objects.bulk_create(
            [
                ParticipanteHabilitado(relacao=relacao, inscricao=inscricao, numero_publico=numero)
                for numero, inscricao in participantes
            ]
        )
        auditar(
            actor=actor,
            permissao=ctx.base.permissao,
            operation=PUBLICAR,
            aggregate=relacao,
            now=ctx.now,
            correlation_id=correlation_id,
            reason=(
                texto_do_motivo
                or f"Relação de habilitados publicada com {len(participantes)} participantes."
            ),
            idempotency_key=idempotency_key,
            detalhe=conferencia.detalhe(conferidas, CONGELAMENTO),
        )
        conferencia.registrar_no_log(
            conferidas, CONGELAMENTO, correlation_id=correlation_id, desfecho="CONCLUIDO"
        )
        declarado = {
            "relacao": str(relacao.id),
            "quantidade": relacao.quantidade,
            "resumo": relacao.resumo,
            "metodoHash": metodo_hash,
            "algoritmo": metodo.get("algorithm", ""),
        }
        # **A advertência vai junto do desfecho** (FR-3636, FR-3637): a Caixa fora do ar e a forma
        # do acervo não impedem o congelamento, e quem congelou precisa saber, na mesma tela, o que
        # não pôde ser verificado. A chave só existe quando há o que dizer, para que o desfecho de
        # sempre continue o de sempre.
        advertencias = [
            item.mensagem(CONGELAMENTO)
            for item in conferidas
            if item.decisao(CONGELAMENTO) == dominio_da_conferencia.ADVERTE
        ]
        if advertencias:
            declarado["advertencias"] = advertencias
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


CONGELAMENTO = dominio_da_conferencia.CONGELAMENTO


def _referencias_do_congelamento(metodo, perfil_id, marco_id):
    """A referência declarada no método que a relação vai citar — ou nenhuma (FR-3636).

    **Com a declarada registrada como indisponível, a conferência se cala**, como a `102` faz para
    a substituta (`previa._congelar_agora_inviavel`): a da vez é a que a regra de substituição pôs
    no lugar, e ela não tem instante publicado. A fonte que não sabe conferir também se cala
    (D-008).
    """
    from processo_seletivo.sorteios.infrastructure import fontes
    from processo_seletivo.sorteios.models import OcorrenciaDaFonte

    if not isinstance(metodo, dict):
        return []
    fonte = str(metodo.get("source") or "")
    referencia = str(metodo.get("occurrence") or "")
    if fontes.sabe_conferir(fonte) is not True:
        return []
    if OcorrenciaDaFonte.objects.filter(
        fonte=fonte, referencia=referencia, indisponivel=True
    ).exists():
        return []
    return [
        conferencia.Referencia(
            fonte=fonte,
            referencia=referencia,
            caminho=f"/profiles/id={perfil_id}/classificationMilestones/id={marco_id}/drawMethod",
            alvo="O método do marco",
            ocorre_em=str(metodo.get("occurrenceAt") or ""),
        )
    ]


def _consultar_antes_de_congelar(actor, edital_id, perfil_id, marco_id, *, idempotency_key):
    """A consulta à fonte, sem trava e fora da transação (FR-3632).

    A leitura daqui só diz **o que** consultar. O que vale é o método da versão que a transação
    relê, e a referência dele sem consulta é inconclusiva. Repetição de ato concluído, Edital
    alheio ou sem versão vigente não consultam nada: a transação vai repetir ou recusar.
    """
    from django.utils import timezone

    if conferencia.ja_concluido(actor=actor, operation=ATO, key=idempotency_key):
        return {}
    edital = Edital.objects.filter(
        pk=identificador(edital_id), institution_scope=actor.institution_scope
    ).first()
    if edital is None:
        return {}
    try:
        versao = effective_version(edital_id=edital.id, at=timezone.now())
    except DomainError:
        return {}
    if versao is None:
        return {}
    metodo = dominio_do_metodo.metodo_declarado(
        versao.content, perfil_id=perfil_id, marco_id=marco_id
    )
    referencias = _referencias_do_congelamento(metodo, perfil_id, marco_id)
    return conferencia.conferir(referencias) if referencias else {}


def _recusar_concurso_realizado(conferidas, *, correlation_id):
    """Congelar sob concurso já realizado condenaria o sorteio, e não se desfaz (D-005).

    **409, e não 422**: o pedido é bem formado, e o que o impede é o estado do mundo — a extração
    já aconteceu. A saída é retificar o método antes de congelar, e a mensagem diz isso.
    """
    for item in conferidas:
        if item.decisao(CONGELAMENTO) == dominio_da_conferencia.IMPEDE:
            conferencia.registrar_no_log(
                conferidas, CONGELAMENTO, correlation_id=correlation_id, desfecho="RECUSADO"
            )
            raise DomainError(
                "draw_occurrence_already_drawn",
                item.mensagem(CONGELAMENTO),
                409,
            )


def _projetar(edital, versao, perfil_id, marco_id, lista_id):
    """As inscrições do recorte, numeradas. A leitura mora aqui; a regra, no domínio."""
    inscricoes = list(
        Inscricao.objects.filter(
            edital=edital,
            profile_id=identificador(perfil_id),
            status=Inscricao.Status.SUBMETIDA,
        )
    )
    return projecao.numerar(
        projecao.elegiveis(
            inscricoes,
            lista_id=lista_id,
            habilitadas=_habilitadas(edital, versao, perfil_id, marco_id),
        )
    )


def _habilitadas(edital, versao, perfil_id, marco_id):
    """As identidades habilitadas na Etapa anterior, ou `None` quando o Edital não declara uma.

    A regra mora em `application/habilitacao.py` porque a prévia da tela precisa da **mesma**
    resposta: quando as duas divergiam, a comissão via um número e congelava outro (R-012).
    """
    return habilitadas_na_etapa(
        edital,
        dominio_do_metodo.metodo_declarado(versao.content, perfil_id=perfil_id, marco_id=marco_id),
    )


def _nome_da_modalidade(conteudo, perfil_id, lista_id):
    if not lista_id:
        return ""
    for perfil in conteudo.get("profiles") or []:
        if str(perfil.get("id")) != str(perfil_id):
            continue
        for modalidade in perfil.get("competitionModalities") or []:
            if str(modalidade.get("id")) == str(lista_id):
                return modalidade.get("name") or ""
    return ""


def _vigente(edital, perfil_id, marco_id, lista_id):
    """A relação sem sucessora do recorte. Há **uma**, por constraint (FR-070)."""
    return (
        RelacaoDeHabilitados.objects.filter(
            edital=edital,
            perfil_id=identificador(perfil_id),
            marco_id=identificador(marco_id),
            lista_id=identificador(lista_id) if lista_id else None,
            sucessoras__isnull=True,
        )
        .order_by("-publicada_em")
        .first()
    )


def _edital_do_processo(processo, edital_id):
    edital = Edital.objects.filter(
        pk=identificador(edital_id),
        processo=processo,
        institution_scope=processo.institution_scope,
    ).first()
    if edital is None:
        raise nao_encontrado()
    return edital


__all__ = ["ATO", "PUBLICAR", "publicar_relacao"]
