"""Montar a agenda: agendar, mudar, liberar, e o preenchimento com prévia (167, US2).

**A trava é a da agenda** (T-009): toda escrita trava a linha de `AgendaDaEtapa`, que a role de
runtime pode atualizar, e não a do Processo — um clique na grade não espera a convocação de outro
Edital. As duas unicidades do `Agendamento` são a última guarda (FR-7211): o `IntegrityError` vira
`horario_ocupado` ou `pessoa_ja_agendada`, dentro de um `atomic()` próprio, para a transação de
fora sobreviver e a tela dizer a frase.

**A prévia não grava nada, e a aplicação confere a assinatura** (FR-7214, FR-7215, T-010): a
`revision` sozinha não vê a participação que mudou sem tocar a agenda — um recurso deferido entre a
prévia e a aplicação mudaria os pares propostos sem subir versão nenhuma. A assinatura leva os pares
propostos, e por isso vê.

A recusa `agenda_publicada` chega com o ato, na entrega B.
"""

from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.utils import timezone

from processo_seletivo.agendamento.application import leitura
from processo_seletivo.agendamento.application.configurar import etapa_e_periodo
from processo_seletivo.agendamento.domain import nomes, recusas
from processo_seletivo.agendamento.domain.preenchimento import propor
from processo_seletivo.agendamento.models import Agendamento
from processo_seletivo.auditoria.application import record_event
from processo_seletivo.comissoes.application import exigir_base_de_comissao, nao_encontrado
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.shared.canonical import canonical_sha256

AGENDAMENTO = nomes.AGENDAMENTO
PREENCHIMENTO_APLICADO = nomes.PREENCHIMENTO_APLICADO


@dataclass
class Previa:
    proposta: object
    assinatura: str
    montagem: object


def _autorizar(actor, edital, etapa_id):
    base = exigir_base_de_comissao(actor=actor, processo_id=edital.processo_id)
    etapa_e_periodo(edital, etapa_id)
    return base


def _agenda_travada(edital, etapa_id):
    agenda = leitura.agenda_da_etapa(edital, etapa_id, travar=True)
    if agenda is None:
        raise recusas.sem_configuracao()
    return agenda


def _subir_versao(agenda, actor, agora):
    agenda.revision += 1
    agenda.atualizada_por = actor.subject
    agenda.atualizada_em = agora
    agenda.save(update_fields=["revision", "atualizada_por", "atualizada_em"])


def _estado(agendamento):
    if agendamento is None:
        return None
    return {
        "protocolo": agendamento.inscricao.protocolo,
        "banca": agendamento.banca.nome,
        "inicio": agendamento.inicio.isoformat(),
    }


def _nome(inscricao):
    return inscricao.nome or inscricao.protocolo


def agendar(
    *, actor, edital, etapa_id, inscricao_id, banca_id, inicio, mudanca=False, correlation_id=""
):
    """Põe a pessoa no horário, ou a muda para ele (FR-7212). Devolve a frase do que aconteceu.

    `mudanca` diz de onde o gesto partiu. Do painel da pessoa ("Mudar de horário"), ela pode já ter
    horário, e ele é trocado. Do painel do horário livre, ela devia estar sem horário — e se outra
    sessão a agendou nesse meio-tempo, é `pessoa_ja_agendada`, e não uma mudança silenciosa que a
    tiraria do horário que a outra pessoa da comissão acabou de escolher.
    """
    base = _autorizar(actor, edital, etapa_id)
    with transaction.atomic():
        agora = timezone.now()
        agenda = _agenda_travada(edital, etapa_id)
        montagem = leitura.montagem(edital, etapa_id, agenda)
        inscricao = Inscricao.objects.filter(pk=inscricao_id, edital=edital).first()
        if inscricao is None:
            raise nao_encontrado()
        horario = next(
            (item for item in montagem.horarios if item.chave == (str(banca_id), inicio)),
            None,
        )
        if horario is None:
            raise recusas.horario_inexistente()
        if str(inscricao.id) not in montagem.participacao.participantes:
            raise recusas.pessoa_nao_participa(
                _nome(inscricao), montagem.participacao.motivo(inscricao.id)
            )
        atual = montagem.por_inscricao.get(str(inscricao.id))
        ocupante = montagem.ocupados.get(horario.chave)
        if atual is not None and not mudanca:
            raise recusas.pessoa_ja_agendada(_nome(inscricao), atual.inicio)
        if ocupante is not None and ocupante.inscricao_id != inscricao.id:
            raise recusas.horario_ocupado()
        if (
            atual is not None
            and atual.banca_id == horario.banca_id
            and atual.inicio == horario.inicio
        ):
            return recusas.agendada_a_mao(_nome(inscricao), horario.inicio, atual.banca.nome)

        anterior = _estado(atual)
        de = atual.inicio if atual is not None else None
        try:
            with transaction.atomic():
                if atual is None:
                    novo = Agendamento.objects.create(
                        agenda=agenda,
                        inscricao=inscricao,
                        banca_id=horario.banca_id,
                        inicio=horario.inicio,
                        fim=horario.fim,
                        origem=nomes.MANUAL,
                        feito_por=actor.subject,
                        feito_em=agora,
                    )
                else:
                    atual.banca_id = horario.banca_id
                    atual.inicio = horario.inicio
                    atual.fim = horario.fim
                    atual.origem = nomes.MANUAL
                    atual.feito_por = actor.subject
                    atual.feito_em = agora
                    atual.save()
                    novo = atual
        except IntegrityError as erro:
            raise _traduzir(erro, inscricao) from erro
        novo = Agendamento.objects.select_related("inscricao", "banca").get(pk=novo.pk)
        revisao_anterior = agenda.revision
        _subir_versao(agenda, actor, agora)
        gesto = "mudar" if atual is not None else "agendar"
        record_event(
            actor=actor,
            permission=base.permissao,
            operation=AGENDAMENTO,
            aggregate=agenda,
            now=agora,
            correlation_id=correlation_id or f"agenda-{agenda.id}",
            new_state="EM_MONTAGEM",
            previous_revision=revisao_anterior,
            new_revision=agenda.revision,
            detalhe={
                "gesto": gesto,
                "origem": nomes.MANUAL,
                "anterior": anterior,
                "posterior": _estado(novo),
            },
        )
    if de is not None:
        return recusas.mudanca(_nome(inscricao), de, novo.inicio)
    return recusas.agendada_a_mao(_nome(inscricao), novo.inicio, novo.banca.nome)


def _traduzir(erro, inscricao):
    """O `UNIQUE` que recusou, pelo nome: ele diz qual das duas regras a outra sessão ganhou."""
    texto = str(erro)
    if "uq_agendamento_inscricao" in texto:
        existente = Agendamento.objects.filter(inscricao=inscricao).order_by("inicio", "id").first()
        return recusas.pessoa_ja_agendada(
            _nome(inscricao), existente.inicio if existente else timezone.now()
        )
    return recusas.horario_ocupado()


def liberar(*, actor, edital, etapa_id, inscricao_id, correlation_id=""):
    """O horário fica livre, e a pessoa volta para "Sem horário" (FR-7212, US2 cenário 7)."""
    base = _autorizar(actor, edital, etapa_id)
    with transaction.atomic():
        agora = timezone.now()
        agenda = _agenda_travada(edital, etapa_id)
        inscricao = Inscricao.objects.filter(pk=inscricao_id, edital=edital).first()
        if inscricao is None:
            raise nao_encontrado()
        atual = (
            Agendamento.objects.filter(agenda=agenda, inscricao=inscricao)
            .select_related("inscricao", "banca")
            .first()
        )
        if atual is None:
            raise recusas.sem_horario_para_liberar(_nome(inscricao))
        anterior = _estado(atual)
        atual.delete()
        revisao_anterior = agenda.revision
        _subir_versao(agenda, actor, agora)
        record_event(
            actor=actor,
            permission=base.permissao,
            operation=AGENDAMENTO,
            aggregate=agenda,
            now=agora,
            correlation_id=correlation_id or f"agenda-{agenda.id}",
            new_state="EM_MONTAGEM",
            previous_revision=revisao_anterior,
            new_revision=agenda.revision,
            detalhe={"gesto": "liberar", "anterior": anterior, "posterior": None},
        )
    return recusas.liberacao(_nome(inscricao))


def _assinatura(agenda, montagem, proposta):
    """`{revision, horários, pares atuais, pares propostos}` — o que a aplicação reencontra."""
    return canonical_sha256(
        {
            "revision": agenda.revision,
            "horarios": [[banca, inicio] for banca, inicio in (h.chave for h in montagem.horarios)],
            "agendados": sorted(
                [str(item.inscricao_id), str(item.banca_id), item.inicio.isoformat()]
                for item in montagem.por_inscricao.values()
            ),
            "propostos": [
                [pessoa.inscricao_id, horario.banca_id, horario.inicio.isoformat()]
                for pessoa, horario in proposta.pares
            ],
        }
    )


def _previa(agenda, montagem):
    proposta = propor(montagem.sem_horario, montagem.livres)
    return Previa(proposta, _assinatura(agenda, montagem, proposta), montagem)


def previa_do_preenchimento(*, actor, edital, etapa_id, montagem_=None):
    """A prévia, sem gravar nada (FR-7214)."""
    _autorizar(actor, edital, etapa_id)
    if montagem_ is None:
        agenda = leitura.agenda_da_etapa(edital, etapa_id)
        if agenda is None:
            raise recusas.sem_configuracao()
        montagem_ = leitura.montagem(edital, etapa_id, agenda)
    return _previa(montagem_.agenda, montagem_)


@dataclass
class MudouDesdeAPrevia(Exception):
    """A recusa da FR-7215 com a prévia nova, que a tela mostra no lugar da antiga."""

    recusa: object
    previa: Previa


def aplicar_preenchimento(*, actor, edital, etapa_id, assinatura, correlation_id=""):
    """Grava os pares da prévia como `AUTOMATICA`, se a agenda for a mesma da prévia (FR-7215)."""
    base = _autorizar(actor, edital, etapa_id)
    with transaction.atomic():
        agora = timezone.now()
        agenda = _agenda_travada(edital, etapa_id)
        montagem = leitura.montagem(edital, etapa_id, agenda)
        previa = _previa(agenda, montagem)
        if previa.assinatura != assinatura:
            raise MudouDesdeAPrevia(recusas.agenda_mudou_desde_a_previa(), previa)
        pares = previa.proposta.pares
        try:
            with transaction.atomic():
                Agendamento.objects.bulk_create(
                    Agendamento(
                        agenda=agenda,
                        inscricao_id=pessoa.inscricao_id,
                        banca_id=horario.banca_id,
                        inicio=horario.inicio,
                        fim=horario.fim,
                        origem=nomes.AUTOMATICA,
                        feito_por=actor.subject,
                        feito_em=agora,
                    )
                    for pessoa, horario in pares
                )
        except IntegrityError as erro:
            # Sob a trava isto não acontece; se acontecer, a guarda do banco fala, e a tela relê.
            raise recusas.horario_ocupado() from erro
        revisao_anterior = agenda.revision
        _subir_versao(agenda, actor, agora)
        record_event(
            actor=actor,
            permission=base.permissao,
            operation=PREENCHIMENTO_APLICADO,
            aggregate=agenda,
            now=agora,
            correlation_id=correlation_id or f"agenda-{agenda.id}",
            new_state="EM_MONTAGEM",
            previous_revision=revisao_anterior,
            new_revision=agenda.revision,
            detalhe={
                "origem": nomes.AUTOMATICA,
                "assinatura": assinatura,
                "posterior": [
                    {
                        "protocolo": pessoa.protocolo,
                        "banca_id": horario.banca_id,
                        "inicio": horario.inicio.isoformat(),
                    }
                    for pessoa, horario in pares
                ],
            },
        )
    return recusas.aplicada(len(pares))
