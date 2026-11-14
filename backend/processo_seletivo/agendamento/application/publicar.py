"""Publicar a agenda: o ato imutável, no molde da `149`, com o veículo da `159` (167, T-012).

```text
comando_de_comissao(ator, processo, chave)   # trava o Processo, confere a base, reserva a chave
  ↓
trava da AgendaDaEtapa                       # sempre Processo → agenda, nunca o inverso (T-009)
  ↓
já publicada? → devolve o ato                # a confirmação repetida com outra chave (SC-2396)
  ↓
conferência recomposta sob a trava           # a mesma função da tela (`conferir.py`)
  ↓
assinatura · impedimentos · veículo · autoridade
  ↓
AtoDaAgenda + HorarioPublicado em lote       # bytes canônicos e o resumo deles (FR-7224)
  ↓
revision + 1, trilha `agenda.publicacao`
```

**A trava é a da agenda, e nunca a do ato.** O ato e o horário publicado são append-only, e o
papel de runtime não tem `UPDATE` sobre eles — `SELECT … FOR UPDATE` neles falharia em produção e
passaria nos testes, que conectam como superusuário. A linha da agenda é operacional e travável, e
é ela que serializa duas confirmações; o `UNIQUE` parcial da publicação é a guarda final.

**A confirmação repetida devolve o ato já criado**, por dois caminhos (FR-7223): a mesma chave cai
em `Contexto.repetido`; outra chave, depois da primeira, encontra o ato sob a trava. Nenhum dos dois
grava nada — e, quando os avisos chegarem na entrega C, nenhum dos dois avisa de novo.

Os avisos são da entrega C: aqui `HorarioPublicado.aviso` nasce nulo.
"""

from datetime import date

from django.db import IntegrityError, transaction

from processo_seletivo.agendamento.application import leitura
from processo_seletivo.agendamento.application.conferir import compor_conteudo, conferencia_sob
from processo_seletivo.agendamento.domain import nomes, recusas
from processo_seletivo.agendamento.models import AtoDaAgenda, HorarioPublicado
from processo_seletivo.auditoria.application import record_event
from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.contexto_do_ato import (
    colunas_da_unidade,
    contexto_do_ato,
)
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.canonical import canonical_bytes, canonical_sha256
from processo_seletivo.unidades.domain import nomes as nomes_das_unidades

OPERACAO = "agenda:publicar"

# As recusas da autoridade que a `060` devolve, traduzidas para a frase desta tela: inexistente, de
# outra unidade e fora de vigência são, para quem publica, a mesma coisa — escolher outra.
RECUSAS_DA_AUTORIDADE = {
    nomes_das_unidades.AUTORIDADE_INDISPONIVEL,
    nomes_das_unidades.AUTORIDADE_FORA_DE_VIGENCIA,
}


def veiculo_da_confirmacao(veiculo, declaracao, onde, quando):
    """O veículo escolhido e o que ele exige, ou a recusa (`D-008`, `contracts/recusas.md` §4).

    Nenhum dos dois é presumido, como na `159`: quem publica diz onde a agenda é pública.
    """
    veiculo = (veiculo or "").strip()
    declaracao = (declaracao or "").strip()
    onde = (onde or "").strip()
    if veiculo == nomes.VEICULO_GPS:
        if not declaracao:
            raise recusas.declaracao_do_veiculo_ausente()
        return veiculo, declaracao, "", None
    if veiculo == nomes.VEICULO_EXTERNO:
        if isinstance(quando, str):
            try:
                quando = date.fromisoformat(quando.strip())
            except ValueError:
                quando = None
        if not onde or quando is None:
            raise recusas.publicacao_externa_incompleta()
        return veiculo, "", onde, quando
    raise recusas.veiculo_nao_escolhido()


def _edital(processo, edital_id):
    edital = Edital.objects.filter(pk=edital_id, processo=processo).first()
    if edital is None:
        raise nao_encontrado()
    return edital


def _contexto(edital, autoridade_id, agora):
    if not str(autoridade_id or "").strip():
        raise recusas.autoridade_nao_escolhida()
    try:
        return contexto_do_ato(edital, autoridade_id, agora)
    except DomainError as recusa:
        if recusa.code in RECUSAS_DA_AUTORIDADE:
            raise recusas.autoridade_invalida() from recusa
        raise


def _declarado(ato):
    return {"id": str(ato.id)}


def publicar(
    *,
    actor,
    edital,
    etapa_id,
    assinatura,
    autoridade_id,
    veiculo,
    declaracao="",
    onde="",
    quando=None,
    idempotency_key,
    correlation_id="",
):
    """Publica a agenda conferida, ou devolve a já publicada. Devolve o `AtoDaAgenda`."""
    payload = {
        "edital": str(edital.id),
        "etapa": str(etapa_id),
        "assinatura": assinatura or "",
        "autoridade": str(autoridade_id or ""),
        "veiculo": veiculo or "",
        "declaracao": (declaracao or "").strip(),
        "onde": (onde or "").strip(),
        "quando": str(quando or ""),
    }
    with comando_de_comissao(
        actor=actor,
        processo_id=edital.processo_id,
        operation=OPERACAO,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return AtoDaAgenda.objects.get(pk=ctx.desfecho_anterior["id"])
        agora = ctx.now
        edital = _edital(ctx.processo, edital.id)
        agenda = leitura.agenda_da_etapa(edital, etapa_id, travar=True)
        if agenda is None:
            raise recusas.sem_configuracao()
        existente = leitura.publicacao(agenda)
        if existente is not None:
            ctx.concluir_sem_resultado(200, _declarado(existente))
            return existente

        conferencia = conferencia_sob(edital, etapa_id, agenda, agora=agora)
        if assinatura != conferencia.assinatura:
            raise recusas.agenda_mudou_desde_a_conferencia()
        if conferencia.impedimentos:
            raise recusas.publicacao_impedida(conferencia.impedimentos)
        veiculo, declaracao, onde, quando = veiculo_da_confirmacao(
            veiculo, declaracao, onde, quando
        )
        contexto = _contexto(edital, autoridade_id, agora)
        assinante = contexto.autoridade
        conteudo = compor_conteudo(
            edital,
            conferencia.etapa,
            agenda,
            conferencia.montagem,
            publicado_em=agora,
            signatario={
                "nome": assinante.nome,
                "cargo": assinante.cargo,
                "atoDeNomeacao": assinante.ato_de_nomeacao,
            },
            veiculo=veiculo,
            unidade={
                "cabecalho": list(contexto.unidade.cabecalho),
                "local": contexto.unidade.local,
                "sigla": contexto.unidade.sigla,
                "nome": contexto.unidade.nome,
            },
        )
        try:
            with transaction.atomic():
                ato = AtoDaAgenda.objects.create(
                    agenda=agenda,
                    edital=edital,
                    especie=nomes.PUBLICACAO,
                    praticado_por=actor.subject,
                    praticado_em=agora,
                    veiculo=veiculo,
                    declaracao_do_veiculo=declaracao,
                    publicado_fora_onde=onde,
                    publicado_fora_em=quando,
                    signatario_id=assinante.pk,
                    signatario_nome=assinante.nome,
                    signatario_cargo=assinante.cargo,
                    signatario_ato_de_nomeacao=assinante.ato_de_nomeacao,
                    **colunas_da_unidade(contexto.unidade),
                    conteudo_publico=canonical_bytes(conteudo),
                    conteudo_publico_hash=canonical_sha256(conteudo),
                    assinatura_conferida=assinatura,
                    idempotency_key=idempotency_key or "",
                )
        except IntegrityError:
            # Sob a trava da agenda isto não acontece; se acontecer, o `UNIQUE` parcial diz que
            # outra confirmação publicou primeiro, e a resposta é o ato dela.
            existente = leitura.publicacao(agenda)
            if existente is None:
                raise
            ctx.concluir_sem_resultado(200, _declarado(existente))
            return existente

        agendados = [
            item
            for item in conferencia.montagem.por_inscricao.values()
            if str(item.inscricao_id) in conferencia.montagem.participacao.participantes
        ]
        HorarioPublicado.objects.bulk_create(
            HorarioPublicado(
                ato=ato,
                inscricao_id=item.inscricao_id,
                situacao=nomes.AGENDADO,
                banca_id=item.banca_id,
                banca_nome=item.banca.nome,
                inicio=item.inicio,
                fim=item.fim,
            )
            for item in sorted(agendados, key=lambda i: (i.inicio, i.banca.ordem))
        )
        revisao_anterior = agenda.revision
        agenda.revision += 1
        agenda.atualizada_por = actor.subject
        agenda.atualizada_em = agora
        agenda.save(update_fields=["revision", "atualizada_por", "atualizada_em"])
        record_event(
            actor=actor,
            permission=ctx.base.permissao,
            operation=nomes.PUBLICACAO_DA_AGENDA,
            aggregate=agenda,
            now=agora,
            correlation_id=correlation_id or f"agenda-{agenda.id}",
            previous_state="EM_MONTAGEM",
            new_state="PUBLICADA",
            previous_revision=revisao_anterior,
            new_revision=agenda.revision,
            idempotency_key=idempotency_key or "",
            # O estado posterior são os pares publicados — protocolo, banca e início —, sem e-mail
            # nem sala (FR-7256); o resumo identifica os bytes que a página pública mostra.
            detalhe={
                "ato": str(ato.id),
                "veiculo": veiculo,
                "signatario": assinante.cargo,
                "conteudo": ato.conteudo_publico_hash,
                "posterior": [
                    {
                        "protocolo": item.inscricao.protocolo,
                        "banca": item.banca.nome,
                        "inicio": item.inicio.isoformat(),
                    }
                    for item in sorted(agendados, key=lambda i: (i.inicio, i.banca.ordem))
                ],
            },
        )
        ctx.concluir_sem_resultado(201, _declarado(ato))
        return ato
