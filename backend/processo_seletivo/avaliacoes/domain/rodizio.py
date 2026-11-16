"""A proposta de rodízio — e por que ela não é distribuição automática.

FR-017, FR-018 e FR-019 proíbem **o sistema escolher** quem avalia quem. Eles não proíbem a
presidência escolher uma regra: o que a spec recusa é a decisão sem autor, não a decisão tomada com
ajuda. A diferença está em quem pratica o ato, e ela é preservada aqui de três maneiras:

1. **A proposta não grava nada.** Este módulo é puro: recebe o estado e devolve pares. Nenhuma
   Atribuição existe até a confirmação.
2. **A proposta é mostrada inteira antes de valer** — quantas para cada pessoa, e o que fica de
   fora e por quê. Quem confirma sabe o que está confirmando (o mesmo princípio de FR-041).
3. **O ato registrado é o da confirmação**, com o ator que confirmou, e cada Atribuição continua
   gerando o seu evento (FR-016, FR-052).

Sem isso, distribuir 600 inscrições com dupla avaliação custava 24 telas e cerca de 700 marcações,
e o equilíbrio da carga era aritmética de quem distribui. O caminho manual continua existindo e não
mudou: quem quer escolher inscrição por inscrição continua escolhendo.

**A regra do rodízio, dita por extenso**, porque proposta que não se explica não se confere: para
cada inscrição, na ordem do protocolo, as vagas que faltam vão para quem está **com menos carga
projetada** entre as pessoas selecionadas que podem receber aquela inscrição; empate se desfaz pelo
identificador institucional, que é estável. Nada de sorteio: a mesma proposta, sobre o mesmo estado,
é sempre a mesma — e é isso que permite conferi-la sob trava antes de gravar.

**Com agenda, a ordem é a dela, e o conflito é inelegibilidade** (179, FR-8207, a revisão da FR-107
da `012`). Na ordem do protocolo, que não tem relação com o horário, o rodízio formava duplas
fixas e as punha em dois lugares ao mesmo tempo: no caso de 43 pessoas, 6 avaliadores e 3 bancas,
em 8 a 14 dos 15 horários. Percorrendo a agenda — dia, horário, banca —, cada dupla cai numa banca
e fica nela; e quem já tem entrevista que se sobrepõe ao horário da inscrição não a recebe, como o
impedido não recebe. A menor carga, o desempate, o impedimento e a exposição não mudam. Sem
agenda, nada muda.
"""

import hashlib

from processo_seletivo.avaliacoes.domain.conflito import Compromisso, cabe

CONFLITO_NO_RODIZIO = "Todas as pessoas selecionadas têm entrevista neste horário."


class ForaDaProposta:
    """Uma inscrição que a proposta não cobre inteira, e por quê."""

    def __init__(self, inscricao, faltam, motivo):
        self.inscricao = inscricao
        self.faltam = faltam
        self.motivo = motivo

    def declarada(self):
        return {
            "inscricao": self.inscricao.protocolo or str(self.inscricao.id),
            "faltam": self.faltam,
            "motivo": self.motivo,
        }


def propor(
    *,
    previstas,
    inscricoes,
    membros,
    ocupacao,
    carga,
    impedidos,
    ja_atribuidas,
    ja_concluidas,
    horario=None,
    compromissos=None,
    agora=None,
):
    """Os pares `(inscricao, membro)` que a presidência vai confirmar — ou recusar.

    `carga` entra como o número de atribuições ativas que cada pessoa já tem na Etapa, e é a partir
    dele que a projeção começa: propor sobre uma banca que já trabalhou não pode ignorar o que ela
    já recebeu.

    `horario` (`{inscricao_id: (inicio, fim, banca_nome)}`) e `compromissos` (`{subject:
    [Compromisso]}`) são da 179: sem eles, a proposta é a de antes, byte a byte. Com `agora`, a
    inscrição cuja entrevista já acabou não passa pelo teste do conflito, como no lote.
    """
    projecao = {membro.id: carga.get(membro.id, 0) for membro in membros}
    horario = horario or {}
    agenda_projetada = {subject: list(lista) for subject, lista in (compromissos or {}).items()}
    if horario:
        inscricoes = _na_ordem_da_agenda(inscricoes, horario)
    pares, fora = [], []
    for inscricao in inscricoes:
        vagas = previstas - ocupacao.get(inscricao.id, 0)
        if vagas <= 0:
            continue
        elegiveis = [
            membro
            for membro in membros
            if (membro.identity_subject, inscricao.id) not in impedidos
            and (membro.id, inscricao.id) not in ja_atribuidas
            and (membro.identity_subject, inscricao.id) not in ja_concluidas
        ]
        # Menor carga projetada primeiro; empate pelo identificador, que não muda. A ordenação do
        # banco não decide nada aqui — se decidisse, a proposta mudaria entre a tela e a gravação,
        # e a conferência sob trava não teria o que conferir.
        marcado = horario.get(inscricao.id)
        sem_conflito = elegiveis
        if marcado is not None and (agora is None or marcado[1] > agora):
            inicio, fim, banca = marcado
            sem_conflito = [
                membro
                for membro in elegiveis
                if cabe(agenda_projetada.get(membro.identity_subject, []), inicio, fim) is None
            ]
        sem_conflito.sort(key=lambda membro: (projecao[membro.id], membro.identity_subject))
        escolhidos = sem_conflito[:vagas]
        for membro in escolhidos:
            pares.append((inscricao, membro))
            projecao[membro.id] += 1
            if marcado is not None:
                inicio, fim, banca = marcado
                agenda_projetada.setdefault(membro.identity_subject, []).append(
                    Compromisso(inicio, fim, inscricao.id, banca_nome=banca)
                )
        if len(escolhidos) < vagas:
            motivo = (
                CONFLITO_NO_RODIZIO
                if elegiveis and not sem_conflito
                else _motivo_da_lacuna(len(sem_conflito), len(membros))
            )
            fora.append(ForaDaProposta(inscricao, vagas - len(escolhidos), motivo))
    return pares, projecao, fora


def _na_ordem_da_agenda(inscricoes, horario):
    """Dia, horário e banca; as sem horário depois, na ordem em que vieram (a do protocolo)."""
    com = [i for i in inscricoes if i.id in horario]
    sem = [i for i in inscricoes if i.id not in horario]
    com.sort(key=lambda i: (horario[i.id][0], horario[i.id][2], i.protocolo or "", str(i.id)))
    return com + sem


def _motivo_da_lacuna(elegiveis, selecionados):
    if elegiveis == 0:
        return (
            "Nenhuma das pessoas selecionadas pode receber esta inscrição — impedimento, "
            "atribuição que já existe ou avaliação já concluída."
        )
    return (
        f"Só {elegiveis} das {selecionados} pessoas selecionadas podem receber esta inscrição. "
        "Selecione mais gente, ou distribua o que falta à mão."
    )


def assinar(pares):
    """A identidade da proposta, para conferi-la sob trava antes de gravar (o mesmo de FR-106).

    Contar não bastaria: entre ver a proposta e confirmá-la, uma conclusão nova ou um impedimento
    mudam **quem** recebe o quê sem mudar quantos são. O que se confirma tem de ser o que executa.
    """
    conteudo = "|".join(sorted(f"{inscricao.id}:{membro.id}" for inscricao, membro in pares))
    return hashlib.sha256(conteudo.encode()).hexdigest()[:16]
