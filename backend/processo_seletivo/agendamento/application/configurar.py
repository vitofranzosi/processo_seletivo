"""Salvar a configuração da agenda de uma Etapa (167, US1, FR-7202 a FR-7208).

```text
exigir_base_de_comissao(ator, processo)       # sem a base, nada se lê nem se grava (FR-7255)
  ↓
etapa_vigente + evento_vigente                # a Etapa e o período, relidos agora (T-002)
  ↓
problemas(configuração, período)              # a lista inteira, ou nada se grava (FR-7204)
  ↓
transação: trava da AgendaDaEtapa             # nunca a do Processo: a montagem não espera a
  ↓                                           # convocação de outro Edital (T-009)
janelas, bancas com id estável, revision + 1
  ↓
quem perdeu o horário volta a "sem horário"   # e a frase diz quem (FR-7208)
  ↓
trilha `agenda.configuracao_salva`            # sem o local nem o endereço da sala (FR-7256)
```

**A insuficiência não impede salvar** (FR-7205), e a lista ainda aberta também não (FR-7207): a
comissão configura antes de a Etapa anterior ter Resultado, e a capacidade é comparada com quem
participa naquele momento.

**Publicada a agenda, a configuração só cresce** (FR-7208, T-015): acrescentar dia, janela a um
dia, ou banca. Remover o horário de quem foi publicado é `horario_publicado_removido`; mudar a
duração, o intervalo, a forma, as orientações, uma janela existente, ou o nome, o local ou o
endereço de uma banca existente é `parametro_publicado_alterado`. O aviso já levou o endereço e as
orientações à pessoa, e nenhuma situação de mensagem desta spec corrigiria a mudança silenciosa.
"""

from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.utils import timezone

from processo_seletivo.agendamento.application import leitura
from processo_seletivo.agendamento.domain import recusas
from processo_seletivo.agendamento.domain.configuracao import problemas
from processo_seletivo.agendamento.domain.horarios import derivar
from processo_seletivo.agendamento.models import (
    AgendaDaEtapa,
    Agendamento,
    BancaDaAgenda,
    JanelaDaAgenda,
)
from processo_seletivo.auditoria.application import record_event
from processo_seletivo.comissoes.application import exigir_base_de_comissao, nao_encontrado
from processo_seletivo.comissoes.domain.etapas import etapa_vigente
from processo_seletivo.shared.api.problems import DomainError


@dataclass
class Salva:
    agenda: AgendaDaEtapa
    devolvidos: list  # nomes, na ordem dos horários que deixaram de existir

    @property
    def frase(self):
        return recusas.configuracao_salva(self.devolvidos)


def etapa_e_periodo(edital, etapa_id):
    """A Etapa vigente e o período do Evento dela; Etapa ausente da versão vigente é 404."""
    try:
        etapa = etapa_vigente(edital, etapa_id)
    except DomainError:
        etapa = None
    if etapa is None:
        raise nao_encontrado()
    return etapa, leitura.periodo_da_etapa(edital, etapa)


def salvar(*, actor, edital, etapa_id, configuracao, correlation_id=""):
    base = exigir_base_de_comissao(actor=actor, processo_id=edital.processo_id)
    _etapa, periodo = etapa_e_periodo(edital, etapa_id)
    lista = problemas(configuracao, periodo=periodo)
    if lista:
        raise recusas.configuracao_recusada(lista)

    with transaction.atomic():
        agora = timezone.now()
        agenda = _travar_ou_criar(edital, etapa_id, configuracao, actor, agora)
        if agenda.revision and leitura.publicacao(agenda) is not None:
            recusadas = so_acrescimo(agenda, configuracao)
            if recusadas:
                raise recusas.configuracao_recusada(recusadas)
        anterior = _descricao(leitura.configuracao_da_agenda(agenda)) if agenda.revision else None
        revisao_anterior = agenda.revision

        agenda.forma = configuracao.forma
        agenda.duracao_minutos = configuracao.duracao
        agenda.intervalo_minutos = configuracao.intervalo or 0
        agenda.orientacoes = (configuracao.orientacoes or "").strip()

        _gravar_bancas(agenda, configuracao)
        JanelaDaAgenda.objects.filter(agenda=agenda).delete()
        JanelaDaAgenda.objects.bulk_create(
            JanelaDaAgenda(agenda=agenda, dia=dia, inicio=inicio, fim=fim)
            for dia, pares in configuracao.dias
            for inicio, fim in sorted(pares)
        )

        devolvidos = _devolver_quem_perdeu_o_horario(agenda, configuracao)

        agenda.revision = revisao_anterior + 1
        agenda.atualizada_por = actor.subject
        agenda.atualizada_em = agora
        agenda.save()

        record_event(
            actor=actor,
            permission=base.permissao,
            operation=leitura.CONFIGURACAO_SALVA,
            aggregate=agenda,
            now=agora,
            correlation_id=correlation_id or f"agenda-{agenda.id}",
            previous_state="",
            new_state="EM_MONTAGEM",
            previous_revision=revisao_anterior,
            new_revision=agenda.revision,
            detalhe={
                "etapa": str(etapa_id),
                "anterior": anterior,
                "posterior": _descricao(configuracao),
                "devolvidos": devolvidos,
            },
        )
    return Salva(
        agenda=agenda, devolvidos=[item["nome"] for item in devolvidos_com_nome(devolvidos)]
    )


def so_acrescimo(agenda, configuracao):
    """O que a configuração nova faria ao que foi publicado: `[Recusa, …]`, vazia no acréscimo.

    Compara com a agenda gravada, que depois da publicação só cresceu: o que existia no dia do ato
    continua existindo, igual. Uma banca existente é a que o formulário carrega com o `id` dela.
    """
    lista = []
    atual = leitura.configuracao_da_agenda(agenda)
    parametros_iguais = (
        atual.forma == configuracao.forma
        and atual.duracao == configuracao.duracao
        and (atual.intervalo or 0) == (configuracao.intervalo or 0)
        and (atual.orientacoes or "").strip() == (configuracao.orientacoes or "").strip()
    )
    janelas_novas = {
        (dia, inicio, fim) for dia, pares in configuracao.dias for inicio, fim in pares
    }
    janelas_mantidas = all(
        (janela.dia, janela.inicio, janela.fim) in janelas_novas
        for janela in agenda.janelas_em_ordem
    )
    novas = {str(banca.id): banca for banca in configuracao.bancas}
    bancas_mantidas = all(
        str(banca.id) in novas
        and novas[str(banca.id)].nome.strip() == banca.nome
        and (novas[str(banca.id)].acesso or "").strip() == (banca.acesso or "").strip()
        for banca in agenda.bancas_em_ordem
    )
    if not (parametros_iguais and janelas_mantidas and bancas_mantidas):
        lista.append(
            recusas.parametro_publicado_alterado(
                agenda.duracao_minutos, agenda.intervalo_minutos, agenda.forma
            )
        )
    derivados = {horario.chave for horario in derivar(configuracao)}
    for item in leitura.vigentes_da_agenda(agenda):
        if (str(item.banca_id), item.inicio) not in derivados:
            lista.append(
                recusas.horario_publicado_removido(
                    item.inscricao.nome or item.inscricao.protocolo,
                    item.inscricao.protocolo,
                    item.inicio,
                    item.banca_nome,
                )
            )
    return lista


def _travar_ou_criar(edital, etapa_id, configuracao, actor, agora):
    """A agenda travada; nasce na primeira configuração, com `revision` zero até ser gravada.

    Duas configurações simultâneas da primeira vez: uma cria, e a outra encontra o `UNIQUE` e trava
    a que já existe — o `atomic()` próprio deixa a transação externa sobreviver ao erro.
    """
    existente = leitura.agenda_da_etapa(edital, etapa_id, travar=True)
    if existente is not None:
        return existente
    try:
        with transaction.atomic():
            agenda = AgendaDaEtapa.objects.create(
                edital=edital,
                etapa_id=etapa_id,
                forma=configuracao.forma,
                duracao_minutos=configuracao.duracao,
                intervalo_minutos=configuracao.intervalo or 0,
                orientacoes="",
                revision=0,
                criada_por=actor.subject,
                criada_em=agora,
                atualizada_por=actor.subject,
                atualizada_em=agora,
            )
    except IntegrityError:
        return leitura.agenda_da_etapa(edital, etapa_id, travar=True)
    agenda.janelas_em_ordem = []
    agenda.bancas_em_ordem = []
    return agenda


def _gravar_bancas(agenda, configuracao):
    """As bancas com o `id` que o formulário carrega: a banca renomeada continua sendo a mesma.

    **Os nomes passam por um nome provisório antes do definitivo**: trocar "Sala 1" e "Sala 2" de
    lugar violaria o `UNIQUE(lower(nome))` no meio da troca, numa linha que no fim seria válida.
    """
    existentes = {str(banca.id): banca for banca in agenda.bancas_em_ordem}
    mantidas = {str(banca.id) for banca in configuracao.bancas if str(banca.id) in existentes}
    removidas = [identidade for identidade in existentes if identidade not in mantidas]
    if removidas:
        # Quem estava numa banca removida perde o horário; a devolução abaixo o conta, mas a linha
        # precisa sair antes da banca, que é `PROTECT`.
        agenda.removidos_por_banca = list(
            Agendamento.objects.filter(agenda=agenda, banca_id__in=removidas)
            .select_related("inscricao", "banca")
            .order_by("inicio", "banca__ordem", "id")
        )
        Agendamento.objects.filter(agenda=agenda, banca_id__in=removidas).delete()
        BancaDaAgenda.objects.filter(agenda=agenda, pk__in=removidas).delete()
    else:
        agenda.removidos_por_banca = []
    for identidade in mantidas:
        BancaDaAgenda.objects.filter(pk=identidade).update(nome=f"~{identidade}")
    for banca in configuracao.bancas:
        valores = {
            "nome": banca.nome.strip(),
            "acesso": (banca.acesso or "").strip(),
            "ordem": banca.ordem,
        }
        if str(banca.id) in mantidas:
            BancaDaAgenda.objects.filter(pk=banca.id).update(**valores)
        else:
            BancaDaAgenda.objects.create(agenda=agenda, **valores)
    agenda.bancas_em_ordem = list(agenda.bancas.order_by("ordem", "id"))


def _devolver_quem_perdeu_o_horario(agenda, configuracao):
    """Apaga o agendamento cujo horário a configuração nova não deriva, e diz de quem era (FR-7208).

    O horário que continua existindo — a mesma banca, o mesmo início — fica com a pessoa, e o fim
    acompanha a duração nova.
    """
    # As bancas como ficaram gravadas: a banca nova só tem identidade depois de criada.
    gravada = leitura.Configuracao(
        forma=configuracao.forma,
        duracao=configuracao.duracao,
        intervalo=configuracao.intervalo or 0,
        dias=configuracao.dias,
        bancas=tuple(
            leitura.Banca(str(banca.id), banca.nome, "", banca.ordem)
            for banca in agenda.bancas_em_ordem
        ),
    )
    derivados = {horario.chave: horario for horario in derivar(gravada)}
    devolvidos = [_par(item) for item in agenda.removidos_por_banca]
    for item in (
        Agendamento.objects.filter(agenda=agenda)
        .select_related("inscricao", "banca")
        .order_by("inicio", "banca__ordem", "id")
    ):
        horario = derivados.get((str(item.banca_id), item.inicio))
        if horario is None:
            devolvidos.append(_par(item))
            item.delete()
        elif horario.fim != item.fim:
            Agendamento.objects.filter(pk=item.pk).update(fim=horario.fim)
    return devolvidos


def _par(agendamento):
    """O estado de um agendamento na trilha: identidade, protocolo, banca e início — sem nome,
    e-mail nem sala (FR-7256, T-019)."""
    return {
        "inscricao": str(agendamento.inscricao_id),
        "protocolo": agendamento.inscricao.protocolo,
        "banca": agendamento.banca.nome,
        "inicio": agendamento.inicio.isoformat(),
    }


def devolvidos_com_nome(devolvidos):
    nomes = leitura.pessoas([item["inscricao"] for item in devolvidos])
    return [
        {**item, "nome": nomes[item["inscricao"]].nome}
        for item in devolvidos
        if item["inscricao"] in nomes
    ]


def _descricao(configuracao):
    """A configuração na trilha, **sem o acesso das bancas**: nem local, nem endereço de sala."""
    return {
        "forma": configuracao.forma,
        "duracao": configuracao.duracao,
        "intervalo": configuracao.intervalo,
        "dias": [
            {"dia": dia.isoformat(), "janelas": [f"{i:%H:%M}-{f:%H:%M}" for i, f in pares]}
            for dia, pares in configuracao.dias
            if dia is not None
        ],
        "bancas": [banca.nome for banca in configuracao.bancas],
    }
