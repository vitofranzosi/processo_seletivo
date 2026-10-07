"""Como uma autoridade é dita na tela — uma função só, para que nenhuma tela repita a exceção."""


def quem_assinou(nome, cargo):
    """`nome — cargo`, ou só o cargo quando não há nome (054, FR-994).

    Uma função, e não a mesma f-string em cada tela: sem nome, a f-string deixava um travessão
    pendurado — " — Diretora-Geral…" —, e cada tela que a repetisse teria de lembrar a exceção.
    """
    nome = str(nome or "").strip()
    cargo = str(cargo or "").strip()
    return f"{nome} — {cargo}" if nome and cargo else nome or cargo


def rotulo_da_autoridade(autoridade):
    """A opção da escolha ao publicar: quem assina e, se houver, o ato de nomeação (UX-148).

    O ato de nomeação é o que distingue duas autoridades do mesmo cargo sem nome — a titular e a
    substituta designada, por exemplo —, e por isso entra no rótulo, e não só no registro.
    """
    rotulo = quem_assinou(autoridade.nome, autoridade.cargo)
    ato = str(autoridade.ato_de_nomeacao or "").strip()
    return f"{rotulo} · {ato}" if ato else rotulo
