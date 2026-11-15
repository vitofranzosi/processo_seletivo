"""O aviso de uma pessoa: assunto e texto, como sai (167, FR-7231; protótipo `email.html`).

**Na entrega B ele só é mostrado**: a conferência exibe a mensagem da primeira pessoa da agenda,
para quem publica ler o que cada um vai receber (FR-7222). O envio é da entrega C, pela origem
nova do aviso complementar, e compõe o corpo de cada pessoa com esta mesma função — a prévia e o
envio não divergem porque são uma função só.

**É o único texto da agenda que leva o endereço da sala**, e leva o de uma pessoa só: a dela
(FR-7229). A página pública, a trilha e a prévia pública nunca o recebem.
"""

from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.domain.horarios import dia_por_extenso, hora, zona


def assunto(etapa, edital):
    return f"Seu horário: {etapa} — {edital}"


def corpo(
    *, nome, protocolo, etapa, edital, inicio, duracao, banca, forma, acesso, orientacoes, varias
):
    """O texto do aviso, linha a linha. `banca` só aparece quando a agenda tem mais de uma."""
    primeiro_nome = (nome or "").split(" ")[0] or protocolo
    local = inicio.astimezone(zona())
    linhas = [
        f"Olá, {primeiro_nome}.",
        "",
        f"A comissão publicou a agenda da {etapa} do {edital}. Este é o seu horário:",
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
