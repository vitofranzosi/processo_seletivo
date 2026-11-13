"""O texto do aviso de pendência documental: assunto, corpo e rodapé (134, FR-4613 a FR-4617).

**Função pura, e o texto sai congelado.** O aviso da `066` guarda o que saiu (o texto final), e o
deste é de cada pessoa: os documentos pendentes mudam de uma para outra. Por isso não há modelo
editável nem variável: a comissão decide *se* avisa, e não *o que* o aviso diz (3ª decisão do
usuário, 08/11/2026).

**O que não entra, e por quê.** O motivo da pendência fica no portal (FR-3584 da `115`), porque ele
pode revelar saúde, renda ou cota. O nome da pessoa, o CPF, o protocolo e a modalidade não entram
porque o e-mail vai a uma caixa que outra pessoa pode ler. E o documento exigido **por modalidade**
sai como *"um documento da sua modalidade de concorrência"*: o nome do laudo, endereçado a alguém,
diria a cota dela (D-004).

**Sem contagem de dias.** O portal diz *"faltam 3 dias"* porque relê a cada visita; o e-mail fica na
caixa, e a contagem envelheceria errada. O prazo vai com o dia da semana, a data e a hora, que não
envelhecem (FR-3873 da `121`).
"""

from dataclasses import dataclass

from processo_seletivo.avisos.domain.variaveis import escapar

#: A frase que substitui o nome do documento de modalidade (3ª decisão do usuário).
DOCUMENTO_DE_MODALIDADE = "um documento da sua modalidade de concorrência"
DOCUMENTOS_DE_MODALIDADE = "{n} documentos da sua modalidade de concorrência"

#: A primeira linha do rodapé, fixa (3ª decisão): o aviso não é o ato e não mexe no prazo.
NAO_E_A_CONVOCACAO = "Este aviso não é a convocação e não altera o seu prazo."

ASSUNTO = "{instituicao} · {edital}: há documento da sua convocação para revisar"
#: O assunto com dois ou mais documentos: concorda o número, como o corpo já concordava (revisão de
#: 13/11 da FR-4613). O singular com vários documentos fazia a pessoa procurar um só.
ASSUNTO_DOS_DOCUMENTOS = "{instituicao} · {edital}: há documentos da sua convocação para revisar"

RODAPE = (
    "—\n"
    f"{NAO_E_A_CONVOCACAO}\n"
    "Em caso de dúvida, fale com {atendimento}.\n"
    "\n"
    "{assinatura} — Seleções\n"
    "Esta mensagem é automática; não responda."
)


@dataclass(frozen=True)
class Pendente:
    """Um item pendente, como o texto o trata: o nome publicado e se é exigido por modalidade."""

    nome: str
    de_modalidade: bool


def linhas_dos_documentos(pendentes):
    """Os documentos pendentes, um por linha; os de modalidade, juntos numa linha só (D-004).

    A ordem é a da lista. A linha dos de modalidade fica onde aparece o primeiro deles, para que a
    pessoa reconheça a ordem da página quando abrir a convocação.
    """
    de_modalidade = sum(1 for item in pendentes if item.de_modalidade)
    linhas = []
    for item in pendentes:
        if item.de_modalidade:
            if de_modalidade:
                linhas.append(
                    DOCUMENTO_DE_MODALIDADE
                    if de_modalidade == 1
                    else DOCUMENTOS_DE_MODALIDADE.format(n=de_modalidade)
                )
                de_modalidade = 0
            continue
        linhas.append(item.nome)
    return linhas


def bloco_dos_documentos(pendentes):
    """O parágrafo dos documentos, como ele fica no corpo: uma linha por documento, com travessão.

    **Função própria porque o despacho a relê** (FR-4623, D-011): antes de cada tentativa, ele
    compõe de novo o bloco com o que está pendente agora e o procura, parágrafo inteiro, no texto
    congelado. Se não encontrar, a lista mudou desde o gesto, e o aviso não sai.
    """
    return "\n".join(f"- {linha}" for linha in linhas_dos_documentos(pendentes))


def frase_do_prazo(prazo):
    """*"O prazo continua sendo até quinta-feira, 12/11/2026, às 17h00."* (FR-4615, D-007).

    `prazo` é o `PrazoApresentado` da `121`, ou `None` quando a convocação não tem vencimento.
    """
    if prazo is None:
        return "O prazo continua o da sua convocação."
    return f"O prazo continua sendo até {prazo.dia_da_semana}, {prazo.data}, às {prazo.hora}."


def compor(*, instituicao, edital, pendentes, prazo, link, atendimento, assinatura):
    """O assunto e o corpo finais. `edital` é *"Edital 72/2026"*.

    **As chaves são escapadas**, porque o despacho da `066` resolve `{nome_do_candidato}` no envio:
    um nome de documento com chave, posto cru, seria lido ali como variável. Este texto não tem
    variável nenhuma, e o escape garante que continue sem.
    """
    linhas = linhas_dos_documentos(pendentes)
    if not linhas:
        raise ValueError("Aviso de pendência sem documento pendente.")
    um = len(pendentes) == 1
    abertura = (
        f"Há {'um documento' if um else 'documentos'} da sua convocação no {edital} que "
        f"{'precisa' if um else 'precisam'} de atenção:"
    )
    corpo = "\n\n".join(
        [
            abertura,
            bloco_dos_documentos(pendentes),
            f"Veja o que fazer na página da sua convocação: {link}",
            frase_do_prazo(prazo),
            RODAPE.format(atendimento=atendimento, assinatura=assinatura),
        ]
    )
    assunto = (ASSUNTO if um else ASSUNTO_DOS_DOCUMENTOS).format(
        instituicao=instituicao, edital=edital
    )
    return escapar(assunto), escapar(corpo)


__all__ = [
    "ASSUNTO",
    "ASSUNTO_DOS_DOCUMENTOS",
    "DOCUMENTOS_DE_MODALIDADE",
    "DOCUMENTO_DE_MODALIDADE",
    "NAO_E_A_CONVOCACAO",
    "Pendente",
    "RODAPE",
    "bloco_dos_documentos",
    "compor",
    "frase_do_prazo",
    "linhas_dos_documentos",
]
