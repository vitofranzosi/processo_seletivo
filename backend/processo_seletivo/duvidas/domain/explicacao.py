"""As frases da explicação — escritas aqui, só com os valores dos cartões (070, `FR-1425`, `D-003`).

**Não são as frases do documento.** O compositor do PDF tem as dele, que mudam com o código e que a
`069` reescreve. Esta explicação diz o que os cartões mostram, em linguagem simples, e se declara do
sistema (`FR-1436`). Um guardião (`tests/unit/duvidas/test_importacoes.py`) reprova a importação do
compositor por este pacote.

**Três proibições** (`FR-1422`, `FR-1425`):

- nenhuma avaliação da pessoa ("você pode", "será aceito");
- nenhuma negativa que o Edital não declare ("não cabe", "não há", "não é permitido");
- nenhum valor que não esteja num cartão da mesma resposta.

As formas iniciais passam pela revisão do setor de seleção (070, T046) antes de qualquer abertura.
"""

from __future__ import annotations

from processo_seletivo.duvidas.domain import rotulos


def plural(quantidade, singular, plural_):
    return singular if quantidade == 1 else plural_


def encaminhar(canal_em_palavras: str) -> str:
    return f"Em caso de dúvida, procure {canal_em_palavras}."


def depende_da_leitura(assunto: str, canal_em_palavras: str) -> str:
    return (
        f"O Edital trata de {assunto} em texto, mostrado abaixo. Esta consulta mostra o texto e "
        "não "
        f"o interpreta. {encaminhar(canal_em_palavras)}"
    )


def varias_fontes(assunto: str, canal_em_palavras: str) -> str:
    return (
        f"O Edital trata de {assunto} em mais de um lugar, mostrados abaixo. Esta consulta não os "
        f"concilia. {encaminhar(canal_em_palavras)}"
    )


def nao_informa(assunto: str, canal_em_palavras: str) -> str:
    """A ausência dita como ausência — nunca como proibição (`FR-1422`)."""
    return (
        f"O Edital não traz informação sobre {assunto}. Isso não quer dizer que não caiba ou que "
        "não "
        f"exista. {encaminhar(canal_em_palavras)}"
    )


def inscricoes(periodo, inicio, fim) -> str:
    from processo_seletivo.inscricoes.domain.periodo import ABERTO, ENCERRADO, FUTURO

    if periodo.cancelado:
        return "O período de inscrições foi declarado cancelado no cronograma."
    if periodo.estado == ABERTO:
        return (
            f"As inscrições estão abertas até {fim}."
            if fim
            else ("As inscrições estão abertas, sem término declarado.")
        )
    if periodo.estado == FUTURO:
        return f"As inscrições começam em {inicio}" + (
            f" e vão até {fim}." if fim else ", sem término declarado."
        )
    if periodo.estado == ENCERRADO:
        return f"O período de inscrições terminou em {fim}."
    return "O Edital não declara período de inscrições por este sistema."


def vagas(codigo, total, total_legivel, linhas, reserva, limite) -> str:
    """`linhas`: `(rótulo curto, quantidade)` de cada linha do quadro, na ordem do quadro."""
    if total is None:
        # Ausente não é zero (`FR-1422`): o cartão diz "não declarado", e a frase também.
        frase = f"O Edital não declara a quantidade de vagas imediatas do Perfil {codigo}."
    elif total == 0:
        frase = f"O Perfil {codigo} não tem vagas imediatas."
    else:
        partes = [f"{quantidade} {rotulo}" for rotulo, quantidade in linhas]
        frase = (
            f"O Perfil {codigo} tem {total_legivel} "
            f"{plural(total, 'vaga imediata', 'vagas imediatas')}"
            + (f": {', '.join(partes)}." if partes else ".")
        )
    if reserva == "LIMITED":
        frase += f" O cadastro de reserva é limitado a {limite}."
    elif reserva == "UNLIMITED":
        frase += " O cadastro de reserva não tem limite de quantidade."
    elif reserva == "NONE":
        frase += " O Edital declara que este Perfil não forma cadastro de reserva."
    return frase


def recurso_declarado(janelas) -> str:
    """`janelas`: `(nome do marco, admite, quantidade, unidade)` dos marcos que declaram."""
    frases = []
    for nome, admite, dias, unidade in janelas:
        if admite:
            frases.append(
                f"Cabe recurso contra o resultado de “{nome}”, em {dias} "
                f"{rotulos.em_palavras(rotulos.UNIDADE_DO_PRAZO, unidade)}, como o Edital declara."
            )
        else:
            frases.append(f"O Edital declara que não cabe recurso contra o resultado de “{nome}”.")
    return " ".join(frases)
