"""As identidades do treinamento só valem nos Editais de treinamento (134, FR-6730).

**Por que existe.** Os cenários da formalização (134) concedem à pessoa fictícia
`treino.formalizacao` o papel Formalização **na unidade** — e o vínculo é da unidade, não do
Edital. Na homologação, que é banco partilhado com Editais de verdade, ela passaria a ser oferecida
para designar em qualquer Edital e contada como "pessoa com o papel" no Centro de todos eles.

**Só oferta e contagem.** A autorização da `117` fica como está: quem designa, quem acessa e o que
o predicado decide não mudam. O que muda é o que se mostra e o que se conta fora do treinamento.

**Sem importar o app de treinamento** (a D-001 da `134`: ele sai inteiro sem que o produto
perceba). O Processo é de treinamento quando o manifesto o registra, lido pelo registro de apps;
sem o app instalado, nenhum é, e as identidades `treino.` nunca valem. O prefixo, e não o
manifesto, decide quem é identidade de treino: é o mesmo que a página de acesso da demonstração
deixa fora das sugestões (`interface/demonstracao.py`).
"""

from django.apps import apps

PREFIXO = "treino."


def de_treino(username):
    return (username or "").startswith(PREFIXO)


def admite_identidades_de_treino(edital):
    """Se o Edital é de um Processo que o gerador de cenários criou: o manifesto, numa consulta."""
    if edital is None or not apps.is_installed("processo_seletivo.treinamento"):
        return False
    manifesto = apps.get_model("treinamento", "CenarioDeTreinamento")
    return manifesto.objects.filter(processo_id=edital.processo_id).exists()


def so_as_admitidas(usernames, edital):
    """Os identificadores, sem os de treino quando o Edital não é de treinamento.

    O manifesto só é lido quando há identidade de treino entre eles: nos Editais reais de produção,
    onde nenhuma existe, a contagem continua com as mesmas consultas.
    """
    usernames = set(usernames)
    if any(de_treino(u) for u in usernames) and not admite_identidades_de_treino(edital):
        return {u for u in usernames if not de_treino(u)}
    return usernames
