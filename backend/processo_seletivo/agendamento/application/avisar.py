"""Os avisos de um ato da agenda: um por pessoa, pela origem `AGENDA` da `066` (167, T-018).

```text
o ato confirmado (publicar, remarcar, incluir)
  ↓
a chave da 066 ligada?  não → nenhum aviso (D-011)
  ↓ sim
assunto e corpo de cada pessoa, de `domain/mensagem.py`    # a mesma função da prévia
  ↓
Aviso + DestinatarioDoAviso em lote, na transação do ato   # o envio é do despacho
  ↓
{inscrição: aviso}, que o HorarioPublicado grava no INSERT  # append-only: não há UPDATE depois
```

**Um aviso por pessoa, e não um aviso com muitos destinatários.** O corpo tem o horário, a banca e,
na forma remota, o endereço da sala daquela pessoa — e só dela (FR-7229). O aviso da `066` guarda um
texto só, final; o precedente é o aviso de pendência da `134`, que já compõe por pessoa.

**Com a chave desligada, nada nasce** (`D-011`): o aviso é efeito do ato, no instante do ato.
Ligar a chave depois não cria aviso de ato anterior, porque não há varredura que os procure — e é
por isso que o vínculo é a coluna `HorarioPublicado.aviso`, gravada no mesmo `INSERT`, e não uma
pendência.

**A `avisos` não conhece a `agendamento`.** Este módulo grava nas tabelas da `066`; o vínculo de
volta mora no `HorarioPublicado`. O despacho envia estes avisos como os demais, sem saber de onde
vieram.
"""

from dataclasses import dataclass

from processo_seletivo.agendamento.domain import mensagem, nomes
from processo_seletivo.agendamento.domain.horarios import zona
from processo_seletivo.avisos.application.comando import envio_habilitado
from processo_seletivo.avisos.domain import nomes as nomes_dos_avisos
from processo_seletivo.avisos.domain.variaveis import escapar
from processo_seletivo.avisos.models import Aviso, DestinatarioDoAviso

REFERENCIA = {
    nomes.PUBLICACAO: "Agenda da {etapa}, publicada em {data}",
    nomes.REMARCACAO: "Remarcação na agenda da {etapa}, em {data}",
    nomes.INCLUSAO: "Inclusão na agenda da {etapa}, em {data}",
}


@dataclass(frozen=True)
class Destino:
    """Uma pessoa do ato, com o horário que o aviso dela diz."""

    inscricao: object
    banca: object
    inicio: object


def referencia(especie, etapa, praticado_em):
    """A frase com que o aviso cita o ato (`ck_aviso_ato_da_origem` a exige não vazia)."""
    data = praticado_em.astimezone(zona()).strftime("%d/%m/%Y")
    return REFERENCIA[especie].format(etapa=etapa, data=data)


def texto(*, especie, destino, agenda, etapa, edital, varias):
    """O assunto e o corpo de uma pessoa, como saem; os mesmos da prévia da conferência."""
    inscricao = destino.inscricao
    return (
        mensagem.assunto(etapa, edital, especie),
        mensagem.corpo(
            nome=inscricao.nome or "",
            protocolo=inscricao.protocolo or "",
            etapa=etapa,
            edital=edital,
            inicio=destino.inicio,
            duracao=agenda.duracao_minutos,
            banca=destino.banca.nome,
            forma=agenda.forma,
            acesso=destino.banca.acesso,
            orientacoes=agenda.orientacoes,
            varias=varias,
            especie=especie,
        ),
    )


def criar_avisos(
    *,
    especie,
    destinos,
    agenda,
    edital,
    etapa,
    rotulo_do_edital,
    actor,
    agora,
    idempotency_key,
    correlation_id="",
):
    """Grava os avisos do ato e devolve `{inscricao_id: Aviso}`; vazio com a chave desligada."""
    if not destinos or not envio_habilitado():
        return {}
    from processo_seletivo.identidade.application.endereco import enderecos_das_inscricoes

    varias = len(agenda.bancas_em_ordem) > 1
    citacao = referencia(especie, etapa, agora)
    enderecos = enderecos_das_inscricoes(destino.inscricao for destino in destinos)
    avisos = []
    for destino in destinos:
        assunto, corpo = texto(
            especie=especie,
            destino=destino,
            agenda=agenda,
            etapa=etapa,
            edital=rotulo_do_edital,
            varias=varias,
        )
        avisos.append(
            Aviso(
                edital=edital,
                institution_scope=edital.institution_scope,
                origem=nomes_dos_avisos.AGENDA,
                motivo=nomes_dos_avisos.PRIMEIRO_AVISO,
                perfil_id=destino.inscricao.profile_id,
                marco_id=None,
                referencia_da_publicacao=citacao,
                # **Escapado**, porque o despacho resolve `{nome_do_candidato}` no envio: as
                # orientações são texto livre, e uma chave nelas seria lida ali como variável.
                assunto=escapar(assunto),
                corpo=escapar(corpo),
                solicitado_por=actor.subject,
                solicitado_em=agora,
                idempotency_key=idempotency_key or "",
                correlation_id=correlation_id or "",
            )
        )
    # **Em lote**, como a pendência: o ato segura a trava do Processo e a da agenda.
    Aviso.objects.bulk_create(avisos)
    DestinatarioDoAviso.objects.bulk_create(
        DestinatarioDoAviso(
            aviso=aviso,
            inscricao=destino.inscricao,
            elegibilidade=nomes_dos_avisos.ELEGIVEL,
            endereco=enderecos.get(destino.inscricao.id, ""),
        )
        for aviso, destino in zip(avisos, destinos, strict=True)
    )
    return {
        str(destino.inscricao.id): aviso for aviso, destino in zip(avisos, destinos, strict=True)
    }
