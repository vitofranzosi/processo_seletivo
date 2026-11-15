"""O passo que falta ao candidato numa Etapa restrita (171, FR-7300 a FR-7313; research T-001).

**Derivado, e não guardado** (FR-7308, D-002). O passo sai do alcance (`163`), da participação, do
período do Evento, dos pareceres concluídos, do Resultado e da visibilidade dele (`164`) — todos
fatos que já existem. Um estado guardado seria a segunda fonte, livre para dizer "falta" a quem a
comissão já registrou.

**Calculado aqui, e entregue pronto a `situacao_da_inscricao`**, que é pura e o teste de custo
prende em zero consultas. É o mesmo padrão da convocação, do desfecho e do estado.

**Sem Etapa restrita que alcance a inscrição, nenhuma consulta** (FR-7311): o alcance é lido do
conteúdo que a view já tem, e só a Etapa que alcança pergunta ao banco.

**Toda Etapa restrita, e não só a verificação da autodeclaração** (D-001): o GPS não sabe o que a
Modalidade significa (`163`), e a perícia de pessoa com deficiência, composta como Etapa restrita, é
o mesmo passo, pelo nome que o Edital lhe deu.
"""

from dataclasses import dataclass
from uuid import UUID

from django.conf import settings

from processo_seletivo.editais.domain import alcance
from processo_seletivo.editais.domain.cronograma import periodo_da_etapa
from processo_seletivo.resultados.domain.efeito import efeito_da_ausencia

# O que os dados permitem afirmar, e nada além (decisão do usuário de 14/11, FR-7306): "falta" é o
# passo ainda por fazer; "aguarda a comissão" é o período encerrado sem registro nenhum — **não** é
# análise iniciada —; "aguarda o resultado" é haver parecer ou Resultado que o titular ainda não vê.
FALTA = "FALTA"
AGUARDA_COMISSAO = "AGUARDA_COMISSAO"
AGUARDA_RESULTADO = "AGUARDA_RESULTADO"


@dataclass(frozen=True)
class Passo:
    """O passo de uma inscrição numa Etapa restrita que a alcança e cujo Resultado ela não vê."""

    etapa_id: str
    etapa: str
    modalidade: str
    estado: str
    inicio: object = None
    fim: object = None
    efeito_da_ausencia: str | None = None
    # O período já começou? Derivado aqui, com o relógio, para a situação continuar sem relógio.
    comecou: bool = False
    # A `Situacao` da `166`, só com a chave do vídeo ligada e a Etapa admitindo o vídeo (FR-7312).
    video: object = None


def _nome_da_modalidade(conteudo, perfil_id, modalidade_id) -> str:
    perfil_id, modalidade_id = str(perfil_id), str(modalidade_id)
    for perfil in (conteudo or {}).get("profiles") or []:
        if str(perfil.get("id")) != perfil_id:
            continue
        for modalidade in perfil.get("competitionModalities") or []:
            if str(modalidade.get("id")) == modalidade_id:
                return modalidade.get("name") or modalidade.get("code") or ""
    return ""


def _restritas_que_alcancam(conteudo, modalidade_id, visiveis) -> list[dict]:
    """As Etapas restritas que alcançam a inscrição e cujo Resultado ela ainda não vê. Puro."""
    if modalidade_id is None:
        return []
    return [
        etapa
        for etapa in (conteudo or {}).get("stages") or []
        if alcance.restrita(etapa)
        and str(etapa.get("id")) not in visiveis
        and alcance.alcanca_a_inscricao(conteudo, etapa, modalidade_id)
    ]


def _ha_registro(edital, etapa_id, inscricao_id, *, depois_de=None) -> bool:
    """Há parecer concluído ou Resultado vigente da inscrição naquela Etapa? Até duas consultas.

    A conclusão, e não a Avaliação concluída: a reabertura preserva a `ConclusaoAvaliacao`, e o
    parecer dado continua sendo parecer dado (o mesmo raciocínio da `166`, achado 9 do #547).
    `depois_de` conta só os pareceres posteriores — os da entrevista ao vivo, depois do
    encaminhamento, e não os pelo vídeo que o encaminhamento preservou.
    """
    from processo_seletivo.avaliacoes.models import ConclusaoAvaliacao
    from processo_seletivo.resultados.models import ResultadoEtapa

    conclusoes = ConclusaoAvaliacao.objects.filter(
        avaliacao__atribuicao__edital=edital,
        avaliacao__etapa_id=etapa_id,
        avaliacao__inscricao_id=inscricao_id,
    )
    if depois_de is not None:
        conclusoes = conclusoes.filter(concluida_em__gt=depois_de)
    return (
        conclusoes.exists()
        or ResultadoEtapa.vigentes.filter(
            edital=edital, etapa_id=etapa_id, inscricao_id=inscricao_id
        ).exists()
    )


def _estado_do_video(inscricao, etapa, conteudo):
    """`(estado do passo ou None, Situacao da 166 ou None)` na Etapa que admite o vídeo.

    Com a chave desligada, o vídeo já enviado continua sendo fato (a chave fecha o portal, e não a
    Mesa — achado I1 da `166`): quem enviou lê "aguardando o resultado", sem a palavra vídeo
    (FR-7313; achado U1 do `/speckit-analyze` da `171`).
    """
    from processo_seletivo.verificacao.application import disponibilidade
    from processo_seletivo.verificacao.domain import admissao

    if not admissao.admite_video(etapa):
        return None, None
    ligada = settings.VERIFICACAO_POR_VIDEO
    situacao = disponibilidade.situacao(
        inscricao=inscricao, etapa=etapa, conteudo=conteudo, exigir_chave=ligada
    )
    if situacao is None:
        return None, None
    if situacao.estado in (disponibilidade.RECEBIDO, disponibilidade.EM_ANALISE):
        return AGUARDA_RESULTADO, situacao if ligada else None
    if not ligada:
        return None, None
    if situacao.estado == disponibilidade.PODE_GRAVAR:
        return FALTA, situacao
    if situacao.estado == disponibilidade.ENCAMINHADA:
        # Encaminhada, falta a entrevista ao vivo — até a comissão registrar o parecer dela.
        from processo_seletivo.verificacao.models import EncaminhamentoAoVivo

        quando = (
            EncaminhamentoAoVivo.objects.filter(
                edital=inscricao.edital, etapa_id=etapa["id"], inscricao=inscricao
            )
            .values_list("registrado_em", flat=True)
            .first()
        )
        if _ha_registro(inscricao.edital, etapa["id"], inscricao.id, depois_de=quando):
            return AGUARDA_RESULTADO, None
        return FALTA, situacao
    return None, None


def passos_da_inscricao(inscricao, *, conteudo, resultados_visiveis, agora) -> list[Passo]:
    """Os passos da inscrição, do período mais próximo para o mais distante (FR-7309).

    `resultados_visiveis` é o que a view já leu (`resultados.application.selectors`); a Etapa cujo
    Resultado o titular vê não é passo — o que ele lê dela é o da `164` e da `165` (FR-7307).
    """
    from processo_seletivo.resultados.application.prontidao import participa_da_etapa

    visiveis = {str(item.get("etapa_id")) for item in resultados_visiveis or []}
    etapas = _restritas_que_alcancam(conteudo, inscricao.modality_id, visiveis)
    if not etapas:
        return []
    modalidade = _nome_da_modalidade(conteudo, inscricao.profile_id, inscricao.modality_id)
    passos = []
    for etapa in etapas:
        etapa_id = UUID(str(etapa["id"]))
        if not participa_da_etapa(
            edital=inscricao.edital,
            etapa_id=etapa_id,
            inscricao_id=inscricao.id,
            conteudo=conteudo,
            modalidade=inscricao.modality_id,
        ):
            continue
        inicio, fim = periodo_da_etapa(conteudo, etapa)
        estado, video = _estado_do_video(inscricao, etapa, conteudo)
        if estado is None:
            if _ha_registro(inscricao.edital, etapa_id, inscricao.id):
                estado = AGUARDA_RESULTADO
            elif fim is not None and agora > fim:
                estado = AGUARDA_COMISSAO
            else:
                estado = FALTA
        passos.append(
            Passo(
                etapa_id=str(etapa_id),
                etapa=etapa.get("name") or "",
                modalidade=modalidade,
                estado=estado,
                inicio=inicio,
                fim=fim,
                efeito_da_ausencia=efeito_da_ausencia(etapa),
                comecou=inicio is None or inicio <= agora,
                video=video,
            )
        )
    # O de período mais próximo primeiro; o sem período por último (FR-7309).
    passos.sort(key=lambda passo: (passo.inicio is None, passo.inicio or agora))
    return passos
