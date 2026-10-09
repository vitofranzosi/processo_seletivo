"""O que sai na caixa de entrada, e de onde vem cada parte (066, contracts/mensagem.md).

**Função pura, e sem `EmailMessage`.** Montar o objeto de correio é do despacho, que é o módulo
remetente declarado na `FR-084` da `010`; um `EmailMessage` aqui faria deste módulo uma quinta
situação de envio aos olhos de `tests/test_situacoes_de_mensagem.py` — e com razão, porque quem
constrói a mensagem é quem a pode mandar.

**Duas etapas, e o registro diz o que saiu.** Na confirmação, o texto da seleção é resolvido com
tudo o que vale para todos, recebe a linha de retificação e o rodapé, e é **congelado** no aviso
(`R-007`). No envio, só `{nome_do_candidato}` muda — e vem de `Inscricao.nome`, que não muda depois
da submissão.
"""

from django.utils import timezone

from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.domain.variaveis import escapar, resolver, resolver_no_envio

# **O rodapé é do sistema, e não da seleção** (`FR-1257`). É ele que impede o aviso de ser lido como
# o ato: aponta a publicação oficial, diz que ela é a referência e que o aviso não a substitui.
RODAPE = """—
A publicação oficial está em {destino_oficial} e é a referência para prazos e
resultados, conforme o {edital}. Este aviso não substitui a publicação.
{frase_da_chamada}Em caso de dúvida, fale com {atendimento}.

Cefor/Ifes — Seleções
Esta mensagem é automática; não responda."""

# **Só na chamada.** Sem esta frase, quem recebe o aviso de uma chamada por publicação contaria o
# prazo a partir do e-mail — e o Edital o conta da publicação (`D-001`).
FRASE_DA_CHAMADA = (
    "O prazo corre conforme o Edital, a partir da publicação, e não do recebimento deste aviso.\n"
)

# **Diz que é retificação, e não que algo mudou para a pessoa** (`FR-1248`). A publicação
# retificadora pode ter mudado outra linha da lista, e o aviso vai a todos os que ela considerou.
LINHA_DA_RETIFICACAO = "Este aviso se refere a publicação que retifica a de {datas}."

#: Cabeçalhos de toda mensagem. `Auto-Submitted` (RFC 3834) faz as respostas automáticas de férias
#: não voltarem para uma caixa que ninguém lê.
CABECALHOS = {"Auto-Submitted": "auto-generated"}

ATENDIMENTO_PADRAO = "a comissão do certame"


def instante(valor):
    """Data e hora no fuso da instalação — e nunca em UTC, que daria três horas de diferença."""
    return timezone.localtime(valor).strftime("%d/%m/%Y às %H:%M")


def validar_texto(*, assunto, corpo):
    """Recusa o texto vazio, longo demais, ou o assunto em mais de uma linha (`FR-1254`).

    **O assunto numa linha só** não é estética: quebra de linha num cabeçalho de e-mail é como se
    injeta cabeçalho, e o Django recusaria no envio — longe de quem escreveu, e depois de
    confirmado.
    """
    from processo_seletivo.shared.api.problems import DomainError

    assunto = (assunto or "").strip()
    corpo = (corpo or "").strip()
    if not assunto:
        problema, campo = "O assunto é obrigatório.", "assunto"
    elif "\n" in assunto or "\r" in assunto:
        problema, campo = "O assunto precisa caber numa linha só.", "assunto"
    elif len(assunto) > nomes.ASSUNTO_MAXIMO:
        problema, campo = f"O assunto tem mais de {nomes.ASSUNTO_MAXIMO} caracteres.", "assunto"
    elif not corpo:
        problema, campo = "O texto do aviso é obrigatório.", "corpo"
    elif len(corpo) > nomes.CORPO_MAXIMO:
        problema, campo = f"O texto tem mais de {nomes.CORPO_MAXIMO} caracteres.", "corpo"
    else:
        return assunto, corpo
    raise DomainError(nomes.AVISO_TEXTO_INVALIDO, problema, 422, campo=campo)


def destino_oficial(*, link_da_publicacao="", referencia_da_publicacao="", pagina=""):
    """Para onde o rodapé aponta, nesta ordem (`R-008`): a publicação, a referência, a página."""
    return link_da_publicacao or referencia_da_publicacao or pagina


def congelar(*, assunto, corpo, valores, origem, datas_retificadas=(), destino, atendimento):
    """O texto que o aviso guarda: tudo resolvido, menos o nome de quem recebe.

    `valores` é o dicionário das variáveis que valem para todos; `datas_retificadas`, os instantes
    das publicações que as citadas sucedem — vazio quando nenhuma é retificadora.
    """
    assunto_final = resolver(assunto.strip(), valores)
    partes = [resolver(corpo.strip(), valores)]
    if datas_retificadas:
        datas = " e ".join(sorted({instante(data) for data in datas_retificadas}))
        partes.append(LINHA_DA_RETIFICACAO.format(datas=escapar(datas)))
    partes.append(
        RODAPE.format(
            destino_oficial=escapar(destino),
            edital=escapar(valores.get("edital", "")),
            frase_da_chamada=FRASE_DA_CHAMADA if origem == nomes.CHAMADA else "",
            atendimento=escapar(atendimento or ATENDIMENTO_PADRAO),
        )
    )
    return assunto_final, "\n\n".join(partes)


def para_a_pessoa(*, assunto, corpo, nome_do_candidato):
    """A mensagem de uma pessoa, a partir do texto congelado: o nome, e as chaves literais."""
    nome = (nome_do_candidato or "").strip() or "candidata(o)"
    return (
        resolver_no_envio(assunto, nome_do_candidato=nome),
        resolver_no_envio(corpo, nome_do_candidato=nome),
    )


__all__ = [
    "CABECALHOS",
    "FRASE_DA_CHAMADA",
    "LINHA_DA_RETIFICACAO",
    "RODAPE",
    "congelar",
    "destino_oficial",
    "instante",
    "para_a_pessoa",
    "validar_texto",
]
