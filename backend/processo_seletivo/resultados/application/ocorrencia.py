"""O desfecho de quem não foi avaliado — constatado pela presidência, e não julgado por ninguém.

Faltou à entrevista, descumpriu pré-requisito, não compareceu ao procedimento de verificação. Os
Editais produzem consequência para os três, e nenhum deles passou por avaliação: não há nota a
copiar, não há sentido a copiar e não há forma sob a qual a conclusão tenha acontecido — não houve
conclusão (D-1).

**Nenhum mecanismo novo.** O invólucro é o mesmo de `consolidacao.py`: `comando_de_comissao` abre a
transação, bloqueia o Processo, reavalia a autorização **depois** do bloqueio e reserva a chave; a
trilha é a mesma chamada explícita; o desfecho declarado é o mesmo formato que a repetição devolve.
A autorização é a da 011 — `comissao:gerir` ou a presidência **deste** Processo —, e não uma
permissão nova: `ATO` abaixo é o `operation` da reserva de idempotência, e não um nome de
permissão.

**O que este comando não consulta, e a ausência é a invariante I-1 em código.** Ele não pergunta se
há avaliação concluída, se a Etapa tem regra de combinação, se a norma histórica é compatível com a
vigente, nem se a Etapa publicou nota mínima. Nada disso governa uma ausência. A prontidão aqui é
outra, e é curta: a inscrição participa da Etapa, e ainda não tem Resultado nela. Uma Etapa
impedida de consolidar — decisória e não eliminatória, ou de leitura múltipla — continua podendo
registrar que alguém não compareceu, porque o impedimento é do mecanismo avaliação e a ocorrência
não passa por ele.

**O que a presidência informa é o motivo, e é a única coisa que ela informa.** Ao contrário da
consolidação, aqui não há cálculo a confirmar: a constatação é o conteúdo do ato. Consequência,
origem, versão, autor e instante saem do comando; o motivo vem de quem constata, porque é ele que
responde ao recurso.

**A consequência é `ELIMINADA`, e isto é decisão desta feature.** Os três casos que a forçam
eliminam, e nenhum Edital lido produz habilitação por ausência de avaliação. Ela **não** vira
constraint: as constraints deste modelo dizem se a linha é internamente coerente, e "que atos a V1
permite" é política — o sorteio e a verificação de reserva de vaga, que a 013 vai hospedar depois,
produzem desfecho favorável por caminho que não é avaliação, e uma constraint escrita hoje os
obrigaria a desfazê-la amanhã.
"""

from processo_seletivo.avaliacoes.application.distribuicao import resultado_declarado
from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.comissoes.domain.etapas import etapas_vigentes
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.resultados.application.consolidacao import Recusa
from processo_seletivo.resultados.application.prontidao import participacao
from processo_seletivo.resultados.application.selectors import inscricoes_com_resultado
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError

REGISTRAR = "RESULTADO_OCORRENCIA"
ATO = "resultado:ocorrencia"

JA_TEM_RESULTADO = "esta inscrição já possui Resultado nesta Etapa"


def _edital_do_processo(processo, edital_id):
    from processo_seletivo.processos.models import Edital

    edital = Edital.objects.filter(pk=identificador(edital_id), processo=processo).first()
    if edital is None:
        raise nao_encontrado()
    return edital


def exigir_motivo(motivo):
    """O motivo é o conteúdo do ato, e por isso a recusa é do pedido — nunca de linha.

    Cobrado aqui e na tela, pela mesma razão que o impedimento da 012 o cobra nos dois lugares:
    validar só no comando transformaria a confirmação num formulário que aceita incompleto e
    recusa depois.
    """
    texto = (motivo or "").strip()
    if not texto:
        raise DomainError(
            "motivo_ausente",
            "Descreva a ocorrência: ela é a causa do Resultado, e é o que responde a um recurso.",
            422,
            campo="motivo",
        )
    return texto


def _participantes_da_selecao(edital, ids, participantes):
    """As inscrições pedidas, exigindo que participem da Etapa.

    Fora do conjunto é **erro do pedido**, e não recusa de linha — a mesma classificação que
    `_inscricoes_da_selecao` aplica na consolidação, e pelo mesmo motivo: registrar ocorrência de
    quem foi eliminado numa Etapa anterior não é o caminho normal esbarrando numa regra, é uma
    seleção que a tela não deveria ter oferecido.
    """
    from processo_seletivo.inscricoes.models import Inscricao

    inscricoes = list(
        Inscricao.objects.filter(pk__in=ids, edital=edital, status=Inscricao.Status.SUBMETIDA)
    )
    if len(inscricoes) != len(set(ids)):
        raise DomainError(
            "inscricao_nao_consolidavel",
            "Só inscrições submetidas deste Edital podem receber Resultado.",
            422,
            campo="inscricao_id",
        )
    if [i for i in inscricoes if i.id not in participantes]:
        raise DomainError(
            "inscricao_fora_da_etapa",
            "Uma ou mais inscrições selecionadas não participam desta Etapa: elas foram "
            "eliminadas numa Etapa anterior ou ainda aguardam o resultado da anterior.",
            422,
            campo="inscricao_id",
        )
    return inscricoes


def participantes_sem_resultado(*, edital, etapa, vigentes=None):
    """As inscrições que ainda podem receber Resultado nesta Etapa — por qualquer caminho.

    É a oferta da tela, e ela é deliberadamente mais larga que a da consolidação: quem não tem
    avaliação concluída aparece aqui, porque é justamente quem falta à Etapa que a ocorrência
    existe para resolver. O que a estreita são as duas regras de participação e a unicidade —
    ninguém recebe dois Resultados na mesma Etapa (I-6).
    """
    from processo_seletivo.inscricoes.models import Inscricao

    participantes, _, _ = participacao(edital=edital, etapa_id=etapa["id"], vigentes=vigentes)
    resolvidas = inscricoes_com_resultado(edital=edital, etapa_id=etapa["id"])
    return Inscricao.objects.filter(pk__in=participantes - resolvidas).order_by("protocolo", "id")


def registrar_ocorrencia(
    *,
    actor,
    processo_id,
    edital_id,
    etapa_id,
    inscricao_ids,
    motivo,
    idempotency_key,
    correlation_id,
):
    """Cria o Resultado por Ocorrência das inscrições selecionadas, e declara o desfecho do lote."""
    ids = [identificador(i) for i in inscricao_ids]
    if not ids:
        raise DomainError(
            "selecao_vazia",
            "Selecione ao menos uma inscrição para registrar a ocorrência.",
            422,
            campo="inscricao_id",
        )
    texto = exigir_motivo(motivo)
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO,
        # O motivo entra na carga da reserva: duas ocorrências diferentes sobre a mesma seleção
        # são atos diferentes, e tratá-las como repetição da mesma chave devolveria o desfecho de
        # uma para a outra.
        payload={
            "etapa": str(etapa_id),
            "inscricoes": sorted(str(i) for i in ids),
            "motivo": texto,
        },
        idempotency_key=idempotency_key,
    ) as ctx:
        edital = _edital_do_processo(ctx.processo, edital_id)
        if ctx.repetido:
            return ctx.desfecho_anterior
        vigentes = etapas_vigentes(edital)
        etapa = vigentes.get(identificador(etapa_id))
        if etapa is None:
            raise nao_encontrado()

        # A norma que fundamenta a constatação é a **vigente no instante do ato**: não há Avaliação
        # de onde herdar versão, e a ausência é constatada sob o Edital que vale agora (I-2).
        versao = effective_version(edital_id=edital.id, at=ctx.now)

        participantes, _, _ = participacao(edital=edital, etapa_id=etapa["id"], vigentes=vigentes)
        inscricoes = _participantes_da_selecao(edital, ids, participantes)
        ja_resolvidas = inscricoes_com_resultado(edital=edital, etapa_id=etapa["id"])

        criados, recusas = [], []
        for inscricao in inscricoes:
            if inscricao.id in ja_resolvidas:
                # Recusa de linha, e não erro do pedido: o lote segue, e I-6 fica intacto — para
                # uma Inscrição × Etapa existe no máximo um Resultado vigente, e a unicidade no
                # banco é a terceira camada disto.
                recusas.append(Recusa(inscricao, JA_TEM_RESULTADO))
                continue
            resultado = ResultadoEtapa.objects.create(
                inscricao=inscricao,
                edital=edital,
                etapa_id=etapa["id"],
                origem=ResultadoEtapa.Origem.OCORRENCIA,
                avaliacao=None,
                versao=versao,
                # Sem forma, sem pontuação e sem sentido: não houve conclusão sob forma nenhuma, e
                # o terceiro ramo de `ck_resultado_completo_por_forma` é feito das três ausências.
                forma="",
                pontuacao=None,
                sentido="",
                consequencia=ResultadoEtapa.Consequencia.ELIMINADA,
                motivo=texto,
                consolidado_em=ctx.now,
                consolidado_por=actor.subject,
            )
            criados.append(resultado)
            auditar(
                actor=actor,
                permissao=ctx.base.permissao,
                operation=REGISTRAR,
                aggregate=resultado,
                now=ctx.now,
                correlation_id=correlation_id,
                reason=(
                    f"Resultado da Etapa {etapa.get('name') or etapa['id']} por ocorrência para a "
                    f"inscrição {inscricao.protocolo or inscricao.id}: {texto}"
                ),
                idempotency_key=idempotency_key,
                # O ato administrativo vai junto porque o motivo **é** o ato: quem responde a um
                # recurso lê a causa da eliminação de `AtoAdministrativo`, como já lê a do
                # impedimento e a da reabertura (FR-093).
                com_ato_administrativo=True,
            )
        declarado = resultado_declarado(criados, recusas, "registrada")
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


__all__ = ["ATO", "JA_TEM_RESULTADO", "REGISTRAR", "exigir_motivo", "registrar_ocorrencia"]
