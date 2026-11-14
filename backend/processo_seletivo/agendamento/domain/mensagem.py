"""O aviso de uma pessoa: assunto e texto, como sai (167, FR-7231; protótipo `email.html`).

**A prévia e o envio são uma função só**: a conferência exibe a mensagem da primeira pessoa da
agenda, para quem publica ler o que cada um vai receber (FR-7222), e a publicação compõe com ela o
corpo de cada pessoa, gravado no aviso de origem `AGENDA` (entrega C). Não divergem porque não há
duas.

**Três espécies, um texto.** A publicação dá o horário; a remarcação dá o novo e diz que o anterior
não vale mais (FR-7244); a inclusão dá o horário de quem passou a participar depois. O cancelamento
não tem aviso (Out of Scope: o aviso de cancelamento seria situação nova de mensagem).

**É o único texto da agenda que leva o endereço da sala**, e leva o de uma pessoa só: a dela
(FR-7229). A página pública, a trilha e a prévia pública nunca o recebem.
"""

from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.domain.horarios import dia_por_extenso, hora, zona

ABERTURA = {
    nomes.PUBLICACAO: "A comissão publicou a agenda da {etapa} do {edital}. Este é o seu horário:",
    nomes.REMARCACAO: (
        "A comissão remarcou o seu horário na {etapa} do {edital}. O horário anterior não vale "
        "mais. Este é o novo:"
    ),
    nomes.INCLUSAO: (
        "A comissão agendou o seu horário na {etapa} do {edital}. Este é o seu horário:"
    ),
}


def assunto(etapa, edital, especie=nomes.PUBLICACAO):
    if especie == nomes.REMARCACAO:
        return f"Seu horário mudou: {etapa} — {edital}"
    return f"Seu horário: {etapa} — {edital}"


def corpo(
    *,
    nome,
    protocolo,
    etapa,
    edital,
    inicio,
    duracao,
    banca,
    forma,
    acesso,
    orientacoes,
    varias,
    especie=nomes.PUBLICACAO,
):
    """O texto do aviso, linha a linha. `banca` só aparece quando a agenda tem mais de uma."""
    primeiro_nome = (nome or "").split(" ")[0] or protocolo
    local = inicio.astimezone(zona())
    linhas = [
        f"Olá, {primeiro_nome}.",
        "",
        ABERTURA[especie].format(etapa=etapa, edital=edital),
        "",
        f"Dia: {dia_por_extenso(local.date())}",
        f"Horário: {hora(local)} (duração prevista de {duracao} minutos)",
    ]
    if varias:
        linhas.append(f"Banca: {banca}")
    if forma == nomes.REMOTA:
        linhas.append(f"Sala virtual: {acesso}")
    else:
        linhas.append(f"Local: {acesso}")
    if (orientacoes or "").strip():
        linhas += ["", f"Orientações: {orientacoes.strip()}"]
    linhas += [
        "",
        "Este e-mail é um aviso. O que vale é a agenda publicada na página da seleção, também na "
        "sua área: Minhas inscrições.",
        f"Inscrição {protocolo}.",
    ]
    return "\n".join(linhas)
