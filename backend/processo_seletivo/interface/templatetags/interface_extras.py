"""Apresentação de valores do domínio. Nenhuma regra aqui — só como o dado é lido."""

from django import template

register = template.Library()

# Edital e Processo usam a forma masculina; Retificação, a feminina. Sem as duas, a trilha
# de auditoria mistura "Em revisão → HOMOLOGADA" com o código cru na tela.
SITUACOES = {
    "EM_ELABORACAO": "Em elaboração",
    "EM_REVISAO": "Em revisão",
    "HOMOLOGADO": "Homologado",
    "HOMOLOGADA": "Homologada",
    "PUBLICADO": "Publicado",
    "PUBLICADA": "Publicada",
    "ENCERRADO": "Encerrado",
    "CANCELADO": "Cancelado",
    "CANCELADA": "Cancelada",
    "ATIVO": "Ativo",
}


@register.filter
def situacao(valor):
    return SITUACOES.get(valor, valor)


@register.simple_tag
def recusa_de(recusas, prefixo, indice, campo):
    """A mensagem de recusa daquele controle, ou vazio.

    Existe como tag, e não como filtro, porque o `id` do controle é composto de três partes —
    `perfil-3-reserveLimit` — e `{% include ... with alvo="perfil-{{ indice }}-..." %}` não
    interpola: dentro de uma tag, `{{ }}` é texto literal, e o alvo nunca casaria.
    """
    return (recusas or {}).get(f"{prefixo}-{indice}-{campo}", "")


@register.filter
def dicionario_simples(dados, chave):
    """Valor de uma chave — o que o template não consegue fazer sozinho.

    Existe para `_recusa.html` ler a mensagem daquele campo entre as recusas da tela.
    """
    return (dados or {}).get(chave, "")


@register.filter
def rotulo_do_ato(chave):
    """O nome humano do ato praticado, lido da tabela que já o declara.

    A faixa dizia "Ato registrado: submeter." porque passava a chave pelo filtro `situacao`, que
    mapeia **situações** — `submeter` não está lá, e o filtro devolve o que não conhece. A trilha
    de auditoria, ao lado, sempre escreveu "Submissão para revisão" corretamente: o rótulo existia
    e não era consultado.
    """
    from processo_seletivo.interface import atos, atos_processo, atos_retificacao

    for tabela in (atos.ATOS, atos_retificacao.ATOS, atos_processo.ATOS):
        ato = tabela.get(valor := str(chave))
        if ato is not None:
            return ato.rotulo
    return SITUACOES.get(valor, valor)


@register.filter
def dicionario(dados, referencia):
    """Lê `campo:<referência>` do que foi enviado, para reexibir sem perder o digitado.

    A referência é a posição do campo no formulário, não o caminho normativo: a tela de
    Retificação não expõe representação a quem elabora (FR-019).
    """
    return dados.get(f"campo:{referencia}", "") if dados else ""


@register.filter
def plural(quantidade, formas):
    """Plural em português não se resolve com sufixo: Edital vira Editais, não Editalis."""
    singular, _, plural_ = str(formas).partition(",")
    return singular if quantidade == 1 else (plural_ or singular)


@register.filter
def marcado(dados, referencia):
    """A marcação de remoção precisa voltar marcada depois do POST, como os campos digitados."""
    return bool(dados and dados.get(f"remover:{referencia}"))
