"""Os quatro passos da tela do sorteio, na língua de quem o conduz (142).

**Apresentação, e não motor** (D-001 da `142`). A situação de cada passo é a célula que a derivação
da `127` já calcula para o Centro de Controle — por lista na relação, no sorteio e na ordem; do
marco na semente. Este módulo só agrupa: conta as listas, escolhe o sinal do passo pela lista que
mais pede atenção (D-003) e diz qual passo é a tarefa de agora. Nada aqui autoriza, recusa ou grava;
os formulários da tela continuam sob as condições de antes (FR-4903).

**Os nomes não são copiados.** Os três primeiros passos leem `conceitos.CONCEITOS`, o mesmo módulo
do Centro (FR-4900). O quarto passo é leitura, e não ato: o Centro não o tem, e o texto dele mora
aqui. As frases daqui não usam «recorte», «faixa» nem «geração», pela razão que `conceitos.py`
registra: texto que chega por variável escapa da varredura de vocabulário.
"""

from dataclasses import dataclass, field

from processo_seletivo.interface import andamento as a
from processo_seletivo.interface import conceitos

ORDEM_SORTEADA = "ordem_sorteada"

#: O passo 4, que é consulta: só existe nesta tela.
CONCEITO_DA_ORDEM = {
    "simples": "Consultar a ordem sorteada",
    "termo": "a ordem que o sorteio gravou",
    "curta": "Mostra, lista a lista, quem ficou em que posição.",
    "porque": "A ordem é o ato do sorteio: não muda, e qualquer pessoa pode reproduzi-la na página "
    "pública de verificação. Ela ainda não é o resultado divulgado — divulgar é outro ato, de quem "
    "publica resultado.",
}

#: O que cada passo pede, alcança, desencadeia e se é irreversível (FR-4901). Curto, e sempre à
#: vista; o «porque» do conceito fica recolhido.
CONTEXTO = {
    a.RELACAO: {
        "precisa": "As inscrições encerradas e, se o Edital exigir, a habilitação feita.",
        "afeta": "Cada lista é fixada à parte.",
        "depois": "Obter a semente pública.",
        "irreversivel": "Não muda mais. Corrigir é publicar uma relação nova, que sucede a "
        "anterior, com motivo.",
    },
    a.SEMENTE: {
        "precisa": "Uma lista fixada, e a extração declarada no Edital já realizada pela fonte.",
        "afeta": "Uma semente só, para todas as listas deste marco.",
        "depois": "Realizar o sorteio de cada lista fixada.",
        "irreversivel": "Fica registrada como a fonte a publicou. Ninguém a escolhe nem a digita.",
    },
    a.SORTEIO: {
        "precisa": "A lista fixada e a semente obtida.",
        "afeta": "Uma lista por vez: cada lista tem o seu sorteio.",
        "depois": "A ordem fica gravada e pode ser verificada; divulgá-la como resultado é o passo "
        "de quem publica resultado.",
        "irreversivel": "Não se refaz: a mesma lista e a mesma semente dão sempre a mesma ordem. "
        "Corrigir é anular, com relação e ocorrência novas.",
    },
    ORDEM_SORTEADA: {
        "precisa": "O sorteio da lista realizado.",
        "afeta": "Cada lista tem a sua ordem.",
        "depois": "Divulgar a classificação, definir até onde se chama e distribuir as vagas.",
        "irreversivel": "Só leitura: consultar não muda nada.",
    },
}

#: A contagem de cada passo por lista: `(singular, plural)` do particípio.
_FEITAS = {
    a.RELACAO: ("lista fixada", "listas fixadas"),
    a.SORTEIO: ("lista sorteada", "listas sorteadas"),
    ORDEM_SORTEADA: ("lista com ordem gravada", "listas com ordem gravada"),
}

#: A ordem em que um passo de várias listas toma o sinal de uma delas (D-003): o que alguém
#: pratica, o que está impedido, o que espera o mundo, o que vem depois, o feito, o que não se
#: aplica. Ordem de leitura, e não estado: a situação de cada lista está ao lado, sempre.
URGENCIA = (a.OBSOLETO, a.PENDENTE, a.IMPEDIDO, a.AGUARDA, a.DEPOIS, a.FEITO, a.NAO_SE_APLICA)

_ANCORAS = {
    a.RELACAO: "titulo-recortes",
    a.SEMENTE: "titulo-ocorrencia",
    a.SORTEIO: "titulo-execucao",
    ORDEM_SORTEADA: "titulo-resultado",
}

#: O passo 4 de uma lista ainda sem sorteio. Construída aqui porque o passo é consulta: não há
#: célula da derivação para "consultar", e a consulta só existe depois do sorteio.
_SEM_ORDEM = a.Celula(a.DEPOIS, razao="a ordem existe depois do sorteio desta lista")


@dataclass
class Passo:
    numero: int
    chave: str
    simples: str
    termo: str
    curta: str
    porque: str
    precisa: str
    afeta: str
    depois: str
    irreversivel: str
    ancora: str
    #: `[(rótulo da lista, Celula)]` nos passos por lista; vazio no da semente.
    listas: list = field(default_factory=list)
    #: A célula do marco, no passo da semente.
    celula: a.Celula | None = None
    agora: bool = False

    @property
    def do_marco(self):
        """O passo da semente é do marco: uma célula só, e nunca uma por lista (FR-4906)."""
        return self.chave == a.SEMENTE

    @property
    def jargao(self):
        """O nome no GPS só aparece quando é jargão (FR-4729 da `136`): "Realizar o sorteio — no
        GPS: sorteio" não ensinaria nada."""
        return self.chave in conceitos.JARGAO

    @property
    def celulas(self):
        if self.do_marco:
            return [self.celula] if self.celula is not None else []
        return [c for _, c in self.listas]

    @property
    def situacao(self):
        """A célula que dá o sinal ao passo: a da lista mais urgente (D-003)."""
        celulas = self.celulas
        if not celulas:
            return None
        return min(celulas, key=lambda c: URGENCIA.index(c.situacao))

    @property
    def a_praticar(self):
        return any(c.situacao in a.A_PRATICAR for c in self.celulas)

    @property
    def contagem(self):
        """ "1 de 2 listas fixadas" — sobre as listas em que o passo se aplica."""
        if self.chave not in _FEITAS:
            return ""
        aplicaveis = [c for c in self.celulas if c.situacao != a.NAO_SE_APLICA]
        feitas = sum(1 for c in aplicaveis if c.situacao == a.FEITO)
        if not aplicaveis:
            return "nenhuma lista com participantes"
        singular, plural = _FEITAS[self.chave]
        return f"{feitas} de {len(aplicaveis)} {singular if len(aplicaveis) == 1 else plural}"


def _passo(numero, chave, conceito, **campos):
    return Passo(
        numero=numero,
        chave=chave,
        simples=conceito["simples"],
        termo=conceito["termo"],
        curta=conceito["curta"],
        porque=conceito["porque"],
        ancora=_ANCORAS[chave],
        **CONTEXTO[chave],
        **campos,
    )


def pontos_do_marco(atual, marco_id):
    """`{tipo: Ponto}` do marco, no Perfil que o tem — ou `{}` sem derivação."""
    if atual is None:
        return {}
    marco_id = str(marco_id)
    for perfil in atual.perfis:
        pontos = {
            p.tipo: p for p in perfil.pontos if p.marco and str(p.marco.get("id")) == marco_id
        }
        if pontos:
            return pontos
    return {}


def celulas_da_lista(pontos, lista_id):
    """As células de uma lista no marco: `{tipo: Celula}`, só das que existem."""
    return {
        tipo: celula
        for tipo, ponto in pontos.items()
        if (celula := ponto.celula(lista_id or None)) is not None
    }


def da_tela(pontos, recortes, *, conduz):
    """Os quatro passos. Sem derivação, eles existem do mesmo jeito, sem situação (FR-4918): os
    nomes e o que cada passo faz não dependem dela.

    `recortes` são os da tela, na ordem dela — a ordem em que o operador lê as listas. `conduz`:
    quem pratica os atos desta tela. Para quem só lê, nenhum passo é "a tarefa de agora" (FR-4917).
    """
    if a.RELACAO not in pontos or a.SORTEIO not in pontos:
        pontos = {}

    def por_lista(tipo, ler=lambda c: c):
        saida = []
        if tipo not in pontos:
            return saida
        for recorte in recortes:
            celula = pontos[tipo].celula(recorte["lista_id"] or None)
            if celula is not None:
                saida.append((recorte["nome"], ler(celula)))
        return saida

    semente = None
    if a.SEMENTE in pontos and recortes:
        semente = next(
            (
                c
                for r in recortes
                if (c := pontos[a.SEMENTE].celula(r["lista_id"] or None)) is not None
            ),
            None,
        )

    def consulta(celula):
        if celula.situacao in (a.FEITO, a.OBSOLETO, a.NAO_SE_APLICA):
            return celula
        return _SEM_ORDEM

    passos = [
        _passo(1, a.RELACAO, conceitos.CONCEITOS[a.RELACAO], listas=por_lista(a.RELACAO)),
        _passo(2, a.SEMENTE, conceitos.CONCEITOS[a.SEMENTE], celula=semente),
        _passo(3, a.SORTEIO, conceitos.CONCEITOS[a.SORTEIO], listas=por_lista(a.SORTEIO)),
        _passo(4, ORDEM_SORTEADA, CONCEITO_DA_ORDEM, listas=por_lista(a.SORTEIO, consulta)),
    ]
    if conduz and pontos:
        # **O primeiro, na ordem, com algo a praticar** (FR-4910). O passo 4 é consulta, e nunca
        # é a tarefa de agora: com a ordem gravada, o que falta é de outro ato e de outra tela.
        vez = next((p for p in passos[:3] if p.a_praticar), None)
        if vez is not None:
            vez.agora = True
    return passos


def ordem_gravada(sorteio):
    """A ordem que o ato do sorteio gravou (D-006 da `142`), com o número de cada pessoa na
    relação que ele consumiu. Leitura do ato constituído — o mesmo que a verificação pública
    reproduz —, e nunca prévia: sem sorteio, não há o que ler.

    Quem ficou sem posição (motivo no lugar do número) vem depois, com o motivo.
    """
    from django.db.models import F

    from processo_seletivo.classificacao.models import PosicaoNaOrdem

    if sorteio is None:
        return []
    numeros = dict(sorteio.relacao.participantes.values_list("inscricao_id", "numero_publico"))
    posicoes = (
        PosicaoNaOrdem.objects.filter(ato_id=sorteio.ato_id)
        .select_related("inscricao")
        .order_by(F("posicao").asc(nulls_last=True), "inscricao__protocolo")
    )
    return [
        {
            "posicao": p.posicao,
            "numero": numeros.get(p.inscricao_id),
            "nome": p.inscricao.nome or "",
            "protocolo": p.inscricao.protocolo or "",
            "motivo": p.motivo,
        }
        for p in posicoes
    ]
