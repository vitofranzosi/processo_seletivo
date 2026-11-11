"""A página do Processo Seletivo: o conjunto dos Editais, e o que fazer nele (147).

**Reagrupa, e não calcula** (FR-5322). Tudo o que esta composição devolve sai do que a view já lê:
o pulso e os sinais da Supervisão (038), os atos e os Editais pendentes do Processo (058), as
Retificações em curso (103) e a faixa "Ações disponíveis para você" da Lista (104), recortada aos
Editais deste Processo. O que se faz aqui é pôr cada fato junto do Edital a que pertence, contar por
situação e ordenar por data.

**O andamento de cada Edital não vem** (D-003 desta feature). A fase, o mapa e as providências por
lista são da página do Edital, e custam dezenas de consultas por Edital; o Processo mostra fatos de
cada um e leva até ele.
"""

from collections import Counter
from dataclasses import dataclass, field

from processo_seletivo.interface import atos_retificacao, trabalho
from processo_seletivo.processos.domain.finalizacao import PROCESSO_FINAL

#: A ordem administrativa do Edital: da composição à publicação e ao fim.
ORDEM_DA_SITUACAO = (
    "EM_ELABORACAO",
    "EM_REVISAO",
    "HOMOLOGADO",
    "PUBLICADO",
    "ENCERRADO",
    "CANCELADO",
)

#: Os três grupos da lista (FR-5310), na ordem do certame: o publicado primeiro, porque é onde o
#: trabalho está. Agrupam situações que existem; não criam outra.
PUBLICADOS, EM_PREPARO, FINAIS = "publicados", "em-preparo", "finais"
GRUPOS = (
    (PUBLICADOS, "Publicados", ("PUBLICADO",)),
    (EM_PREPARO, "Em preparo", ("EM_ELABORACAO", "EM_REVISAO", "HOMOLOGADO")),
    (FINAIS, "Encerrados e cancelados", ("ENCERRADO", "CANCELADO")),
)
AINDA_NAO_PUBLICADO = frozenset({"EM_ELABORACAO", "EM_REVISAO", "HOMOLOGADO"})

#: Quantos marcos a lista consolidada mostra antes de "Ver os outros" (FR-5319).
MARCOS_MOSTRADOS = 6

#: A situação no meio da frase, no singular e no plural (FR-5301).
FORMAS = {
    "EM_ELABORACAO": ("em elaboração", "em elaboração"),
    "EM_REVISAO": ("em revisão", "em revisão"),
    "HOMOLOGADO": ("homologado", "homologados"),
    "PUBLICADO": ("publicado", "publicados"),
    "ENCERRADO": ("encerrado", "encerrados"),
    "CANCELADO": ("cancelado", "cancelados"),
}


@dataclass
class LinhaDoEdital:
    """Um Edital e os fatos dele que a página já leu — uma linha da lista (FR-5312)."""

    edital: object
    pulso: object = None
    sinais: list = field(default_factory=list)
    retificacoes: list = field(default_factory=list)
    meus: list = field(default_factory=list)

    @property
    def periodo(self):
        return self.pulso.periodo if self.pulso is not None else None

    @property
    def inscricoes_abertas(self):
        return self.periodo is not None and not self.periodo.cancelado and self.periodo.em_curso

    @property
    def ainda_nao_publicado(self):
        return self.edital.status in AINDA_NAO_PUBLICADO

    @property
    def proximo_marco(self):
        if self.pulso is None or not self.pulso.proximos_marcos:
            return None
        return self.pulso.proximos_marcos[0]


@dataclass(frozen=True)
class Grupo:
    chave: str
    rotulo: str
    linhas: list
    recolhido: bool = False


@dataclass(frozen=True)
class AtoDaAdministracao:
    ato: object
    impedido: bool = False


@dataclass
class Pagina:
    onde: tuple
    situacoes: str
    linhas: list
    grupos: list
    faixa: trabalho.Faixa
    marcos: list
    marcos_demais: list
    com_sinal: list
    total_de_sinais: int
    com_inscricoes_abertas: list
    #: Os atos que se desfazem — hoje só Ativar —, na ordem do catálogo; cada um com a ajuda dele.
    comuns: list
    terminais: list

    @property
    def algum_impedido(self):
        return any(item.impedido for item in self.terminais)

    @property
    def tem_administracao(self):
        return bool(self.comuns or self.terminais)


def _editais(n):
    return "Nenhum Edital" if n == 0 else f"{n} Edital" if n == 1 else f"{n} Editais"


def situacoes_por_extenso(contagem):
    """`16 em elaboração, 13 publicados, 1 encerrado` — na ordem administrativa."""
    return ", ".join(
        f"{n} {FORMAS[s][0 if n == 1 else 1]}"
        for s in ORDEM_DA_SITUACAO
        if (n := contagem.get(s, 0))
    )


def onde_estamos(processo, contagem, *, abertas, com_sinal):
    """A frase do topo e o detalhe dela (FR-5301): contagens que a página já tem, e nada mais.

    Não há fase do Processo para dizer — as situações administrativas são três, e o certame anda
    em cada Edital. O que se diz é o conjunto: quantos Editais, em que situação, em quantos há
    inscrições abertas e em quantos há condição de atenção que a pessoa alcança.
    """
    total = sum(contagem.values())
    resumo = _editais(total) + (f": {situacoes_por_extenso(contagem)}." if total else ".")
    if processo.status == "CANCELADO":
        return (
            "Processo cancelado.",
            "Interrupção administrativa. Os Editais mantêm suas próprias situações, e todo o "
            f"histórico permanece preservado. {resumo}",
        )
    if processo.status == "ENCERRADO":
        return ("Processo encerrado.", resumo)
    partes = []
    if abertas:
        partes.append(f"Inscrições abertas em {_editais(abertas)}.")
    if com_sinal:
        partes.append(f"{_editais(com_sinal)} com condição de atenção.")
    return (resumo, " ".join(partes))


def marcos_consolidados(pulso):
    """Os próximos marcos de todos os Editais, por data; cada um já carrega o seu Edital."""
    todos = [marco for item in pulso.por_edital for marco in item.proximos_marcos]
    return sorted(
        todos,
        key=lambda m: (m.inicio is None, m.inicio, m.edital.year, str(m.edital.number)),
    )


def compor(*, processo, ator, editais, pulso, sinais, atos, pendentes, elaboravel=None):
    """A página inteira, a partir do que a view já leu. Uma consulta a mais: as Retificações."""
    editais = list(editais)
    por_id = {e.id: LinhaDoEdital(e) for e in editais}
    for item in pulso.por_edital if pulso else ():
        if item.edital.id in por_id:
            por_id[item.edital.id].pulso = item
    for sinal in sinais:
        if sinal.edital.id in por_id:
            por_id[sinal.edital.id].sinais.append(sinal)

    em_curso = atos_retificacao.em_curso_por_edital((e.id for e in editais), ator)
    for edital_id, resumos in em_curso.items():
        if edital_id in por_id:
            por_id[edital_id].retificacoes = resumos

    # A faixa da Lista, sobre os Editais deste Processo (FR-5303). O Edital do botão "Elaborar"
    # não se repete entre as ações: o botão já é o próximo passo dele.
    proximo = ("edital", elaboravel.id) if elaboravel is not None else None
    meus = [
        objeto
        for objeto in trabalho.do_ator(ator, editais, em_curso=em_curso, processo=processo)
        if objeto.edital.id in por_id
    ]
    for objeto in meus:
        por_id[objeto.edital.id].meus.append(objeto)

    linhas = list(por_id.values())
    contagem = Counter(e.status for e in editais)
    final = processo.status in PROCESSO_FINAL
    grupos = [
        Grupo(
            chave,
            rotulo,
            membros,
            recolhido=chave == FINAIS and not final,
        )
        for chave, rotulo, situacoes in GRUPOS
        if (membros := [linha for linha in linhas if linha.edital.status in situacoes])
    ]
    com_sinal = [linha for linha in linhas if linha.sinais]
    abertas = [linha for linha in linhas if linha.inscricoes_abertas]
    marcos = marcos_consolidados(pulso) if pulso else []
    impedidos = bool(pendentes)
    return Pagina(
        onde=onde_estamos(processo, contagem, abertas=len(abertas), com_sinal=len(com_sinal)),
        situacoes=situacoes_por_extenso(contagem),
        linhas=linhas,
        grupos=grupos,
        faixa=trabalho.Faixa([objeto for objeto in meus if objeto.chave != proximo]),
        marcos=marcos[:MARCOS_MOSTRADOS],
        marcos_demais=marcos[MARCOS_MOSTRADOS:],
        com_sinal=com_sinal,
        total_de_sinais=sum(len(linha.sinais) for linha in linhas),
        com_inscricoes_abertas=abertas,
        # Pela marca do próprio ato, e não "o primeiro que não é irreversível": um ato comum novo
        # não herda a ajuda da ativação, nem some da página (revisão do PR #466).
        comuns=[ato for ato in atos if not ato.irreversivel],
        terminais=[
            AtoDaAdministracao(ato, impedido=ato.depende_dos_editais and impedidos)
            for ato in atos
            if ato.irreversivel
        ],
    )
