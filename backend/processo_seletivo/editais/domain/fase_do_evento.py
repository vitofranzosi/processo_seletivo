"""Em que fase está cada Evento do cronograma publicado, e quais ainda vêm (045, 047).

**Por que o módulo saiu da gestão.** A `045` derivou a fase numa régua só e a pôs em
`interface/supervisao.py`, que é onde ela tinha o primeiro leitor. O portal, que mostra o mesmo
cronograma ao público, ficou com uma régua própria: comparava só o dia, em UTC, e não conhecia o
Evento cancelado (047, `FR-765`, `FR-766`). Para ler a mesma régua sem importar trinta módulos da
gestão, a página pública precisava encontrá-la no domínio. É o movimento que a `028` fez ao criar
`calendario.py`: uma regra consultada de dois lugares vira módulo, e não cópia.

O módulo recebe o **conteúdo publicado** (os dicionários da versão consolidada), e não linhas do
ORM: é o que as duas superfícies têm na mão. Nada aqui grava.
"""

from django.utils.dateparse import parse_datetime

from processo_seletivo.editais.domain import calendario
from processo_seletivo.inscricoes.domain.periodo import (
    ABERTO,
    ENCERRADO,
    FUTURO,
    periodo_de_inscricoes,
)

# O único estado que o Evento declara (045, `FR-736`). É o valor do modelo, escrito por extenso
# porque o domínio não importa modelo — `cronograma.STATUS_DECLARAVEIS` já o escreve assim.
CANCELADO = "CANCELADO"

# A fase do período de inscrições sai do **estado do período**, e não da régua geral: sem
# término, o período segue aberto (FR-347), e a régua geral o venceria pelo início (045, `R-3`).
FASE_DO_PERIODO = {
    FUTURO: calendario.PLANEJADO,
    ABERTO: calendario.EM_ANDAMENTO,
    ENCERRADO: calendario.CONCLUIDO,
}


def eventos_do_conteudo(conteudo):
    """Os Eventos da versão publicada, na ordem do cronograma."""
    eventos = [item for item in (conteudo or {}).get("schedule") or [] if isinstance(item, dict)]
    return sorted(eventos, key=lambda evento: (evento.get("order") or 0))


def descricao_do_evento(evento):
    return evento.get("description") or evento.get("type") or ""


def instantes_do_evento(evento):
    """`(início, término)` do Evento publicado. O término é anulável, e a ausência é legítima."""
    inicio = parse_datetime(evento.get("startAt") or "")
    fim = parse_datetime(evento.get("endAt") or "") if evento.get("endAt") else None
    return inicio, fim


def esta_cancelado(evento):
    return evento.get("status") == CANCELADO


def fase_do_evento(evento, conteudo, agora):
    """A fase ordinária de um Evento publicado, ou `None` para o cancelado e o sem início.

    **O `status` publicado só responde se o Evento foi cancelado** (045, `FR-736`). Qualquer outro
    valor — o `PLANEJADO` que todo Evento carrega, ou um `EM_ANDAMENTO` que a API aceitava antes
    — é lido como *não cancelado*, e a fase vem das datas. O conteúdo publicado não é reescrito.

    **Duas réguas, e nenhuma nova**: a do período de inscrições para o Evento marcado como tal, e
    a do vencido (`calendario.fase`) para os demais.
    """
    if esta_cancelado(evento):
        return None
    if evento.get("isRegistrationPeriod") is True:
        return FASE_DO_PERIODO.get(periodo_de_inscricoes(conteudo, agora).estado)
    inicio, fim = instantes_do_evento(evento)
    return calendario.fase(inicio, fim, agora=agora)


def fase_publica_do_evento(evento, conteudo, agora):
    """A fase que o **portal** diz: a mesma de `fase_do_evento`, com uma exceção nomeada (047).

    **O período de inscrições marcado como cancelado segue a régua do período.** A régua do período
    ignora o `status`, e o sistema continua recebendo inscrição dele (`recebe_inscricoes`). Na
    página pública, a marca da seleção diz *aberta* pela mesma régua; dizer *cancelado* na linha do
    cronograma faria a página afirmar duas coisas contrárias sobre a mesma data, e a segunda seria
    falsa para quem tenta se inscrever. A gestão continua lendo o cancelamento primeiro (045,
    `FR-736`), porque lá o assunto é o que foi declarado.

    A pergunta de fundo — se um período cancelado deveria fechar o recebimento — é regra da
    inscrição, e não projeção; está registrada na spec da `047`, e esta função muda junto quando
    ela for respondida.
    """
    if evento.get("isRegistrationPeriod") is True:
        return FASE_DO_PERIODO.get(periodo_de_inscricoes(conteudo, agora).estado)
    return fase_do_evento(evento, conteudo, agora)


def marcos_pendentes(conteudo, agora):
    """Os Eventos que ainda vêm, em ordem cronológica e sem os cancelados (022 `FR-021`, 047).

    Devolve `(evento, início, término, fase)`, e cada leitor monta a própria forma: a gestão o seu
    `Marco`, o portal o *agora e próximo*.

    **O marco em curso ainda é pendente.** O corte é a fase **concluída**, e não o início: tirar
    da lista o que está acontecendo esconderia justamente o prazo que corre.

    **E o corte é o da régua, e não um quarto critério** (045, `R-3`). A lista cortava por
    `término or início <= agora` — com `<=` onde a régua usa `<`, e tirando da lista o período de
    inscrições sem término no instante em que ele abria, enquanto o período continuava recebendo
    inscrição. Sai o marco concluído, e só ele.

    `CANCELADO` sai da leitura temporal: o Evento deixou o cronograma efetivo, e cobrar prazo dele
    seria cobrar de quem já foi cancelado.
    """
    pendentes = []
    for evento in eventos_do_conteudo(conteudo):
        fase = fase_do_evento(evento, conteudo, agora)
        if fase is None or fase == calendario.CONCLUIDO:
            continue
        inicio, fim = instantes_do_evento(evento)
        pendentes.append((evento, inicio, fim, fase))
    pendentes.sort(key=lambda item: (item[1] or item[2], descricao_do_evento(item[0])))
    return tuple(pendentes)
