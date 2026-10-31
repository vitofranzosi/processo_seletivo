"""O catálogo dos papéis de acesso e o escopo institucional (106, `D-004`, `D-011`).

**Ao lado do `PAPEIS`, e não dentro dele.** O seletor de demonstração desenha uma caixa por chave do
`PAPEIS`, e a tela de identificação tem de continuar exatamente a de hoje (`FR-3001`). Os papéis
daqui só se concedem por vínculo, no modo institucional, e o seletor não os conhece.

Como o `PAPEIS`, este mapa é regra, e não configuração: cada permissão diz o que a pessoa pode fazer
com o acesso dos outros, e torná-la editável desfaria a separação entre quem conduz o certame e
quem dá acesso a ele.
"""

# O escopo dos vínculos e dos eventos que não são de unidade nenhuma. Cabe no formato do código de
# unidade, e por isso a sincronização das unidades o recusa: uma unidade com este código receberia,
# sem ninguém conceder, o que o administrador institucional concede (`D-011`).
ESCOPO_INSTITUCIONAL = "institucional"

# As três capacidades novas (`FR-3009`).
GERIR = "acesso:gerir"
CONSULTAR = "acesso:consultar"
ADMINISTRAR = "acesso:administrar"

# Concedidos pelo administrador de acessos da unidade, ao lado dos oito do `PAPEIS`.
INTEGRANTE = "integrante"
# Concedido pelo administrador institucional, numa unidade.
ADMINISTRADOR_DE_ACESSOS = "administrador-de-acessos"
# Concedido só pelo comando de implantação, no escopo institucional (`FR-3029`).
ADMINISTRADOR_INSTITUCIONAL = "administrador-institucional"

PAPEIS_DE_ACESSO = {
    # Sem permissão nenhuma, de propósito. Quem só avalia não tem papel sistêmico — a autorização
    # dele vem da comissão, objeto a objeto —, e sem vínculo nenhum não haveria `Actor` na unidade
    # (`FR-3018`). É o vínculo que diz que a pessoa atua ali; a comissão diz em quê.
    INTEGRANTE: ("Integrante da unidade", []),
    # Dá acesso e não conduz: nenhuma permissão de Processo, Edital ou resultado vem junto, e
    # nenhum papel de acesso se concede por ele — senão o administrador concederia a um cúmplice o
    # poder de conceder de volta (decisão 5 do estudo, proposta ao usuário na spec).
    ADMINISTRADOR_DE_ACESSOS: ("Administrador de acessos da unidade", [GERIR, CONSULTAR]),
}

PAPEIS_INSTITUCIONAIS = {
    # Concede e revoga o administrador de acessos de qualquer unidade, e administra o registro de
    # Unidades — e nada mais. Um global com poder operacional seria o superusuário que o estudo
    # recusou (§B.4, G2): nenhuma das duas permissões conduz Processo, Edital ou resultado.
    #
    # **O registro de Unidades veio com a 110, e não num papel próprio** (`D-002`): não há exigência
    # institucional de separar quem dá acesso de quem cadastra unidade, e um segundo papel pediria
    # um segundo mecanismo de designação. A ampliação não chega em silêncio a quem já tem o papel —
    # a migração da 110 manda verificar e autorizar antes do deploy. A permissão vai por extenso,
    # como as do `PAPEIS`: a fronteira de identidade não importa quem a consome.
    ADMINISTRADOR_INSTITUCIONAL: (
        "Administrador institucional",
        [ADMINISTRAR, "unidade:administrar"],
    ),
}
