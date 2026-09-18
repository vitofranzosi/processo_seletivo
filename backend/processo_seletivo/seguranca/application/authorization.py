"""A doutrina da negativa: o que cada origem responde, e como cada recusa se explica.

Duas perguntas moram aqui, e a segunda existe porque a primeira não a respondia.

**Uma capacidade nomeada** — `require_permission`. Falta de capacidade é 403, porque a recusa é
sobre o ator e escondê-la atrás de "não encontrado" faria a tela mentir sobre por que não abre.
Escopo institucional alheio é 404, porque o ator não deve sequer saber que aquilo existe.

**Uma base de autorização** — `require_authorization_base`. Boa parte das portas da gestão não
pergunta por *uma* capacidade: pergunta por uma **base** — esta capacidade **ou** aquele vínculo,
cada um suficiente sozinho. `require_permission` recebe uma permissão e não sabe expressar a
alternativa, e por isso **cada porta que dependia de uma base improvisou o seu próprio 404**.
Quatro portas, o mesmo improviso, porque o buraco era o mesmo (033, `FR-479`).

**O conjunto de bases é de quem chama, e não da porta.** Duas portas têm modo: a do marco aceita a
capacidade de auditoria na consulta e **não** a aceita na emissão; a da divulgação aceita auditoria
para consultar e não para divulgar. Uma recusa que assuma conjunto fixo mente em metade das
chamadas — manda pedir o que não resolve, ou esconde a alternativa de quem ela resolveria
(`FR-489`).
"""

from dataclasses import dataclass

from processo_seletivo.shared.api.problems import DomainError


@dataclass(frozen=True)
class Base:
    """Uma alternativa que teria bastado, e como se pede.

    São **dois** campos e não um porque as duas espécies de base se pedem de maneiras diferentes, e
    confundi-las é o defeito que a `FR-485` nomeia. Capacidade de papel se pede a quem a detém;
    presidência **não é papel nenhum** — vem da composição da comissão, e nenhum papel a concede.
    Derivar o "a quem" do "o que falta" faria a recusa mandar pedir "o papel de presidente", que é
    pedir o que não existe.
    """

    nome: str
    a_quem: str


def base_de_permissao(nome: str) -> Base:
    """A base que é capacidade de papel — a espécie que se pede a quem a detém."""
    return Base(f"a permissão de {nome}", f"a alguém com a permissão de {nome}")


def _enumerar(itens):
    if len(itens) == 1:
        return itens[0]
    return f"{', '.join(itens[:-1])} ou {itens[-1]}"


def _com_de(nome):
    """`de` + o nome da base, com a contração que o português exige.

    Os nomes nascem com artigo — *"a permissão de gerir a comissão"* — porque é assim que eles
    aparecem no "peça a alguém com...". Concatenados atrás de "depende de", produziam *"depende de
    a permissão"*, que ninguém escreve. A contração é aqui, e não no nome, para que o mesmo `Base`
    sirva às duas posições da frase.
    """
    return f"da {nome[2:]}" if nome.startswith("a ") else f"de {nome}"


def frase_da_recusa(bases) -> str:
    """O motivo e o a quem pedir, numa frase — a formulação que a tela do Edital já pratica.

    Ela é pública porque é o que a `FR-486` prende: existe **uma** maneira de dizer isto, e criar
    uma segunda para a mesma coisa é o que a feature existe para não fazer.
    """
    bases = tuple(bases)
    sozinha = " — cada uma basta sozinha" if len(bases) > 1 else ""
    return (
        f"Esta operação depende {_enumerar([_com_de(base.nome) for base in bases])}{sozinha}. "
        f"Peça {_enumerar([base.a_quem for base in bases])}."
    )


def require_permission(actor, permission: str, *, institution_scope: str | None = None) -> None:
    if not actor or not actor.is_authenticated or not actor.can(permission):
        raise DomainError("forbidden", "A operação não é permitida.", 403)
    if institution_scope is not None and actor.institution_scope != institution_scope:
        raise DomainError("not_found", "Recurso não encontrado.", 404)


def require_authorization_base(autorizado, *, bases) -> None:
    """Recusa por base de autorização, nomeando **as bases que teriam servido naquela chamada**.

    `autorizado` é a decisão, e ela continua sendo de quem chama: a porta já leu a base para
    decidir, e reler aqui criaria duas verdades sobre a mesma recusa, que divergiriam na primeira
    mudança. O que esta função faz é o **espelho** dessa leitura — nomear o que faltou.

    `bases` é o conjunto aceito **naquele ponto de chamada**, e não uma constante da porta. Ele é
    obrigatório e não tem padrão de propósito: um padrão seria exatamente o conjunto fixo que a
    `FR-489` proíbe, e ninguém repararia na chamada que o herdasse por engano.

    Não cuida de escopo institucional. Ele é protegido pelo **filtro na própria consulta** que
    busca o objeto — de modo que objeto de outra unidade e objeto inexistente caiam no mesmo
    `is None` e sejam indistinguíveis (`FR-487`) —, e é decidido antes de se chegar aqui.
    """
    if autorizado:
        return
    if not bases:
        raise ValueError(
            "recusa por base exige as bases que teriam servido: sem elas a frase não diz o que "
            "falta, que é o defeito que ela existe para fechar (FR-481)"
        )
    raise DomainError("forbidden", frase_da_recusa(bases), 403)
