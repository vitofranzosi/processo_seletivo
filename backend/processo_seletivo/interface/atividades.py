"""O que é da pessoa entre Editais — "Minhas atividades" (160).

**Leitura, e não regra** (D-005 da `160`). "Sua" é decidido por `_Leitor.e_sua`, a regra que o
Centro de Controle usa, e este módulo só **filtra** o que a derivação já marcou: pela base por que o
Edital foi lido (a presidência, a alocação à conferência), e pelas famílias que a página cobre.
Uma página que escrevesse frases próprias para os mesmos atos teria duas fontes, e divergiria na
primeira mudança.

**Quem não preside não paga a derivação** (D-003 da `160`). Fora da presidência, só três coisas
podem ser da pessoa: avaliar, conferir e a formalização (que fica fora: 7ª decisão do estudo).
Avaliar sai da carga que a página já calcula; conferir, só onde há alocação à conferência. Rodar a
derivação nos Editais de todas as comissões custava ao avaliador dos cenários ~1700 consultas para
achar um item.

**Os Editais vêm do vínculo, e não da base de autorização** (D-002 da `160`). `pode_gerir_comissao`
devolve a permissão sistêmica antes de olhar a presidência: escolher por ela daria ao Gestor a
unidade inteira como "sua", ou tiraria do Gestor que preside o que é dele.
"""

import re
from dataclasses import dataclass, field

from django.urls import reverse

from processo_seletivo.interface import andamento as a
from processo_seletivo.interface import centro
from processo_seletivo.interface import conceitos as c
from processo_seletivo.interface import providencias as p

PRESIDENCIA, ALOCACAO = "Presidência", "Alocação"

#: As providências que a presidência pratica e esta página mostra (R-003 da `160`). Publicar e
#: julgar são papéis da unidade (D-004); a formalização fica fora (7ª decisão do estudo); a
#: avaliação sai da carga, para aparecer uma vez só, pelo mesmo caminho para quem preside e para
#: quem não (R-005).
RESPONSAVEIS_DA_PRESIDENCIA = frozenset({a.CONDUZ, a.CONFERE})
FORA_DA_PAGINA = frozenset({a.FORMALIZACAO, a.AVALIAR, a.RECURSO})

#: A nota de cobertura (FR-6871, FR-6872): o que a página reúne, o que fica fora e onde está.
#: "Nada para fazer agora" não pode virar "você não tem nada a fazer no GPS".
COBERTURA = (
    "Esta página reúne os atos da presidência nos Editais que você preside, a avaliação e a "
    "conferência de documentos a que você foi alocado. Ficam fora, e estão em outro lugar: a "
    "formalização, em Formalização, na barra; os atos de Edital e de Retificação e os recursos a "
    "julgar, em Processos Seletivos; publicar o resultado, a publicação das inscrições e das "
    "convocações, os avisos aos candidatos, o Requerimento de Matrícula e o encerramento, no "
    "Centro de Controle de cada Edital."
)
#: Para o Gestor, que pode intervir em toda comissão e não vê a condução alheia como sua (D-002).
COBERTURA_DO_GESTOR = (
    "O que você pode fazer por permissão de gestão fica no Centro de Controle de cada Edital."
)
#: Sem linha em "Para fazer agora" (FR-6873): o que a página cobre, e não o GPS inteiro.
NADA_PARA_FAZER = "Nada depende de você agora no que esta página cobre."

_COM_NUMERO = re.compile(r"\d")
#: As linhas de avaliação entram depois das providências do mesmo Edital (R-007).
_INDICE_DA_AVALIACAO = 10_000


@dataclass(frozen=True)
class Linha:
    """Uma providência da pessoa num Edital, com o porquê (data-model da `160`)."""

    providencia: object
    edital: object
    base: str
    fase: str
    indice: int

    @property
    def chave_do_edital(self):
        return (self.edital.year, self.edital.number, str(self.edital.id))


@dataclass
class Grupo:
    """Uma ou mais linhas do mesmo ato entre Editais (FR-6865, FR-6870)."""

    linhas: list

    @property
    def primeira(self):
        return self.linhas[0]

    @property
    def providencia(self):
        return self.primeira.providencia

    @property
    def ato(self):
        return self.providencia.ato

    @property
    def situacao(self):
        return self.providencia.situacao

    @property
    def rotulo(self):
        return self.providencia.rotulo

    @property
    def sinal(self):
        return self.providencia.sinal

    @property
    def base(self):
        return self.primeira.base

    @property
    def fase(self):
        return self.primeira.fase

    @property
    def editais(self):
        vistos = {}
        for linha in self.linhas:
            vistos.setdefault(linha.edital.id, linha.edital)
        return list(vistos.values())

    @property
    def quantos_editais(self):
        return len(self.editais)

    @property
    def unico(self):
        return len(self.linhas) == 1

    @property
    def lugar(self):
        """O lugar comum a todas as linhas, ou vazio quando cada Edital tem o seu."""
        lugares = {linha.providencia.onde_por_extenso for linha in self.linhas}
        return lugares.pop() if len(lugares) == 1 else ""


@dataclass
class Atividades:
    """O que a view entrega ao template (data-model da `160`)."""

    para_fazer: list = field(default_factory=list)
    em_espera: list = field(default_factory=list)
    nao_lidos: list = field(default_factory=list)
    preside: bool = False
    gestor: bool = False

    @property
    def quantos_atos(self):
        return sum(len(grupo.linhas) for grupo in self.para_fazer)

    @property
    def quantos_editais(self):
        return len({linha.edital.id for grupo in self.para_fazer for linha in grupo.linhas})

    @property
    def quantas_esperas(self):
        return len(self.em_espera)


# ---------------------------------------------------------------------------------------------
# As funções puras
# ---------------------------------------------------------------------------------------------


def da_presidencia(itens):
    """O que a presidência pratica, entre os itens do nível 1 de um Edital que ela preside."""
    return [
        item
        for item in itens
        if item.grupo == p.SUA
        and item.responsavel in RESPONSAVEIS_DA_PRESIDENCIA
        and item.natureza not in FORA_DA_PAGINA
    ]


def da_conferencia(itens, perfis):
    """A conferência, num Edital lido só pela alocação à conferência (FR-6857).

    `perfis` é `None` para a alocação a todos os Perfis. **Restringe mesmo quando a derivação diz
    "sua"**: ao Gestor ela diz "sua" toda conferência, porque `_pode_conferir` aceita quem conduz, e
    aqui o que vale é a alocação.
    """
    return [
        item
        for item in itens
        if item.grupo == p.SUA
        and item.responsavel == a.CONFERE
        and (perfis is None or str(item.perfil_id) in perfis)
    ]


def esperas(itens):
    """O que espera, num Edital presidido: *Aguarda* e *Impedido*, de quem quer que aja depois."""
    return [item for item in itens if item.grupo == p.EM_ESPERA and item.natureza != a.FORMALIZACAO]


def linhas_de_avaliacao(atribuicoes, carga):
    """Uma linha por Etapa com inscrição pendente, pela carga — sem a derivação (R-005, D-010).

    O número é o da Mesa, o mesmo do cartão e da faixa da `104`. O Centro desconta o que ainda
    depende da distribuição, e pode dizer menos: reproduzir o desconto aqui exigiria o resumo de
    cada Etapa alocada, que é a derivação que a página evita para quem não preside.
    """
    linhas = []
    for n, item in enumerate(atribuicoes):
        edital = item["edital"]
        pendentes = (carga.get((edital.id, str(item["etapa_id"]))) or {}).get("pendentes") or 0
        if not pendentes:
            continue
        nome = item["nome"]
        providencia = p.Providencia(
            natureza=a.AVALIAR,
            chave=("etapa", str(item["etapa_id"]), a.AVALIAR),
            onde=nome,
            ato=a.ato_de_avaliar(pendentes),
            situacao=a.PENDENTE,
            responsavel=a.AVALIA,
            sua=True,
            url=reverse("interface:minha-etapa", args=[edital.id, item["etapa_id"]]),
            contagem=pendentes,
            lugar=nome,
        )
        fase = c.NOMES[c.AVALIACAO]
        linhas.append(Linha(providencia, edital, ALOCACAO, fase, _INDICE_DA_AVALIACAO + n))
    return linhas


def linhas_do_edital(itens, edital, base, governadas):
    """As linhas de um Edital, com a fase do Centro e a posição de emissão (R-007, R-008)."""
    return [
        Linha(item, edital, base, c.NOMES[centro.fase_da_providencia(item, governadas)], n)
        for n, item in enumerate(itens)
    ]


def _chave_do_grupo(linha, *, espera):
    item = linha.providencia
    if _COM_NUMERO.search(item.ato):
        # **Só junta o ato sem número**, como o Centro dentro de um Edital: "Convocar 3 titulares"
        # em dois Editais não é "Convocar 3 titulares" nos dois, e somar exigiria outra frase.
        return None
    if espera:
        # A razão inteira, **com a data**: esperas com datas diferentes são linhas diferentes, e a
        # mesma data não impede a junção (FR-6870).
        return (item.situacao, item.natureza, item.ato, item.razao)
    return (item.situacao, item.natureza, item.ato, linha.base, item.lista_vazia)


def agrupar_entre_editais(linhas, *, espera=False):
    """O mesmo ato em vários Editais vira um grupo, na posição do primeiro (D-006 da `160`)."""
    grupos, por_chave = [], {}
    for linha in linhas:
        chave = _chave_do_grupo(linha, espera=espera)
        if chave is not None and chave in por_chave:
            por_chave[chave].linhas.append(linha)
            continue
        grupo = Grupo([linha])
        grupos.append(grupo)
        if chave is not None:
            por_chave[chave] = grupo
    return grupos


def _ordem_da_situacao(situacao):
    return {a.OBSOLETO: 0, a.PENDENTE: 1, a.IMPEDIDO: 2, a.AGUARDA: 3}.get(situacao, 4)


def ordenar(linhas):
    """*Obsoleto*, depois *Pendente*; o Edital mais antigo; a ordem de emissão (FR-6866, R-007).

    **A data não ordena** (D-007): a derivação tem o fim das inscrições, a extração, o fim do prazo
    de recurso e o prazo do candidato, e nenhuma é prazo de quem age. O nível 1 do Centro põe à
    frente as que têm data, dentro de um Edital; entre Editais, isso misturaria quatro significados.
    """
    return sorted(
        linhas,
        key=lambda linha: (
            _ordem_da_situacao(linha.providencia.situacao),
            linha.chave_do_edital,
            linha.indice,
        ),
    )


# ---------------------------------------------------------------------------------------------
# A leitura (a única parte que toca o banco)
# ---------------------------------------------------------------------------------------------


def editais_presididos(vinculos):
    """Os Editais com andamento dos Processos ativos que a pessoa preside (FR-6854, FR-6855)."""
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from processo_seletivo.processos.domain.finalizacao import PROCESSO_FINAL
    from processo_seletivo.processos.models import Edital

    processos = [v.processo_id for v in vinculos if v.funcao == Funcao.PRESIDENTE]
    if not processos:
        return []
    return list(
        Edital.objects.filter(processo_id__in=processos, status__in=a.ESTADOS_COM_ANDAMENTO)
        .exclude(processo__status__in=PROCESSO_FINAL)
        .select_related("processo")
        .order_by("year", "number", "id")
    )


def editais_da_conferencia(ator, presididos):
    """`{edital_id: (Edital, perfis)}` das alocações à conferência; `perfis` `None` é todos.

    Um Edital presidido não entra: lá, a presidência já confere (edge case da `160`).
    """
    from processo_seletivo.comissoes.models import AlocacaoAConferencia
    from processo_seletivo.processos.domain.finalizacao import PROCESSO_FINAL

    if ator is None or not getattr(ator, "subject", ""):
        return {}
    ja_lidos = {edital.id for edital in presididos}
    alocacoes = (
        AlocacaoAConferencia.objects.filter(
            ativo=True,
            membro__ativo=True,
            membro__identity_subject=ator.subject,
            membro__processo__institution_scope=ator.institution_scope,
            edital__status__in=a.ESTADOS_COM_ANDAMENTO,
        )
        .exclude(edital__processo__status__in=PROCESSO_FINAL)
        .exclude(edital_id__in=ja_lidos)
        .select_related("edital__processo")
    )
    por_edital = {}
    for alocacao in alocacoes:
        edital, perfis = por_edital.get(alocacao.edital_id, (alocacao.edital, set()))
        if perfis is not None:
            perfis = None if alocacao.perfil_id is None else {*perfis, str(alocacao.perfil_id)}
        por_edital[alocacao.edital_id] = (edital, perfis)
    return por_edital


def ler(ator, *, vinculos, atribuicoes, carga, agora=None):
    """As atividades da pessoa: o que fazer, o que espera e o que não pôde ser lido.

    `vinculos`, `atribuicoes` e `carga` são os que a página já lê para os cartões e as comissões:
    passá-los adiante mantém o custo de quem não preside igual ao de hoje (FR-6877).
    """
    from processo_seletivo.comissoes.domain.autorizacao import PERMISSAO_SISTEMICA
    from processo_seletivo.comissoes.domain.funcoes import Funcao

    presididos = editais_presididos(vinculos)
    conferencia = editais_da_conferencia(ator, presididos)
    fazer, espera, nao_lidos = [], [], []

    lidos = [(edital, PRESIDENCIA, None) for edital in presididos] + [
        (edital, ALOCACAO, perfis) for edital, perfis in conferencia.values()
    ]
    for edital, base, perfis in sorted(lidos, key=lambda t: (t[0].year, t[0].number, str(t[0].id))):
        andamento = a.do_edital(edital, ator, agora=agora)
        if andamento is None:
            # O filtro de estado já deixou só Editais com andamento: `None` aqui é a leitura que
            # falhou, e uma lista pessoal que a calasse diria um falso "nada a fazer" (FR-6874).
            nao_lidos.append(edital)
            continue
        itens = p.agrupar(andamento.providencias)
        governadas = centro.etapas_governadas(andamento.perfis)
        if base == PRESIDENCIA:
            fazer += linhas_do_edital(da_presidencia(itens), edital, base, governadas)
            espera += linhas_do_edital(esperas(itens), edital, base, governadas)
        else:
            fazer += linhas_do_edital(da_conferencia(itens, perfis), edital, base, governadas)

    fazer += linhas_de_avaliacao(atribuicoes, carga)
    return Atividades(
        para_fazer=agrupar_entre_editais(ordenar(fazer)),
        em_espera=agrupar_entre_editais(ordenar(espera), espera=True),
        nao_lidos=nao_lidos,
        # Quem preside um Processo ainda sem Edital publicado também preside: o estado vazio fala
        # com ele como com quem preside (FR-6876).
        preside=any(v.funcao == Funcao.PRESIDENTE for v in vinculos),
        gestor=bool(ator is not None and ator.can(PERMISSAO_SISTEMICA)),
    )
