"""O método do sorteio, lido do conteúdo versionado do Edital.

**Leitura, e nunca escrita.** O método é conteúdo canônico do marco de classificação; quem o
declara é quem elabora o Edital, e quem o altera está retificando — com a autorização daquele ato,
e não com a dos comandos do sorteio (D-013, R-013). Este módulo só sabe achá-lo numa versão e
resumi-lo.

**Por que o resumo importa tanto.** É ele que a relação grava ao congelar (`metodo_hash`), e é o
que transforma "o método vigente" em compromisso datado: sem essa citação, qual método governa o
sorteio seria resolvido no instante da execução — isto é, **depois** da semente —, e a comissão
poderia declarar vários métodos e escolher o conveniente conhecendo o efeito de cada um (D-014,
FR-067).
"""

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.canonical import canonical_sha256


def marco_na_versao(conteudo, *, perfil_id, marco_id):
    """O marco de classificação, dentro do Perfil, no conteúdo publicado. `None` se não existe."""
    for perfil in conteudo.get("profiles") or []:
        if str(perfil.get("id")) != str(perfil_id):
            continue
        for marco in perfil.get("classificationMilestones") or []:
            if str(marco.get("id")) == str(marco_id):
                return marco
    return None


def metodo_declarado(conteudo, *, perfil_id, marco_id):
    """O `drawMethod` do marco, ou `None` quando o marco não declara método."""
    marco = marco_na_versao(conteudo, perfil_id=perfil_id, marco_id=marco_id)
    return (marco or {}).get("drawMethod") or None


def resumo_do_metodo(metodo) -> str:
    """`canonical_sha256` do método declarado, exatamente como ele foi publicado.

    Sobre o objeto inteiro, sem reescrita nem reordenação nossa: a serialização canônica do sistema
    já ordena as chaves, e é a mesma que o verificador de terceiro reproduz a partir do manifesto.
    """
    return canonical_sha256(metodo)


def exigir_metodo(conteudo, *, perfil_id, marco_id):
    """O método do marco, ou recusa — congelar sob método indefinido é escolhê-lo depois.

    Devolve `(metodo, resumo)`. A recusa é da classe do domínio, e diz o que falta: quem lê a tela
    precisa saber que a correção é do Edital, e não do sorteio.
    """
    metodo = metodo_declarado(conteudo, perfil_id=perfil_id, marco_id=marco_id)
    if metodo is None:
        raise DomainError(
            "draw_method_not_declared",
            "O marco não declara o método do sorteio no Edital publicado. Declare-o na composição "
            "— ou por Retificação, se o Edital já está publicado — antes de congelar a relação: "
            "congelar sob método indefinido seria escolher o método depois de conhecer o universo.",
            422,
            campo="drawMethod",
        )
    return metodo, resumo_do_metodo(metodo)


def conferir_compromisso(conteudo, *, perfil_id, marco_id, metodo_hash):
    """O método da versão citada **é** o que a relação comprometeu — ou o sorteio não acontece.

    Bate quando a relação cita a versão em que congelou, que é o caminho normal. Não bate quando
    alguém tenta sortear apontando para outra versão, e aí a recusa é o ponto inteiro da feature:
    o universo se comprometeu com um método, e é aquele que roda.
    """
    metodo, resumo = exigir_metodo(conteudo, perfil_id=perfil_id, marco_id=marco_id)
    if resumo != metodo_hash:
        raise DomainError(
            "draw_method_mismatch",
            "O método declarado na versão citada não é o que a relação comprometeu ao congelar. "
            "O sorteio roda sob o método vigente no congelamento, e não sob outro.",
            409,
            campo="drawMethod",
        )
    return metodo, resumo


__all__ = [
    "conferir_compromisso",
    "exigir_metodo",
    "marco_na_versao",
    "metodo_declarado",
    "resumo_do_metodo",
]
