"""A visão institucional dos Processos Seletivos: as derivações que a página lê (040).

**Este módulo só lê.** Nenhum `save`, `create`, `update` ou `delete` nasce aqui, e a ausência é
invariante da feature — é a mesma disciplina que `interface/supervisao.py` declara, e pela mesma
razão: a `040` é composição de leituras que outros apps já persistem, e a necessidade de gravar
estado é motivo para revisar a spec, não para escrever migration (`FR-582`).

Ele fica fora de `views.py` de propósito. Aqui vivem as derivações, e mantê-las separadas da
montagem de contexto é o que permite testá-las como domínio de leitura, sem requisição.

**O nível é o de cima.** A `022` e a `038` observam a fronteira entre features **dentro** de um
Processo; esta observa a fronteira **entre** Processos. Nenhuma das duas ganha cópia, e nenhum
número daqui é recalculado: onde o fato já tem selector dono, é ele que o produz.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Count, Q
from django.utils import timezone

from processo_seletivo.inscricoes.domain.periodo import (
    ABERTO,
    ENCERRADO,
    FUTURO,
    NAO_DESIGNADO,
    periodo_de_inscricoes,
)
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import versoes_vigentes

# ---------------------------------------------------------------------------
# 1. A capacidade
# ---------------------------------------------------------------------------

# **Capacidade própria, e negada por padrão** (`FR-604`). Não é `inscricao:consultar` nem
# `auditoria:consultar`: reusar qualquer uma concederia o panorama institucional como efeito
# colateral de outro ato — que é, palavra por palavra, o que a `031` recusou ao criar
# `matricula:exportar` em vez de pendurá-la no Gestor.
#
# A constante mora aqui, e a grafia é repetida **literalmente** em `identidade.py::PAPEIS`: aquele
# módulo é a fronteira de identidade e não deve conhecer quem consome a permissão. É o arranjo que
# `matricula:exportar` já usa, com teste prendendo as duas pontas.
CONSULTAR = "visao:consultar"


# ---------------------------------------------------------------------------
# 2. As formas de leitura
#
# Estruturas montadas na requisição e descartadas com ela. Não são modelos: não têm identidade,
# não têm persistência, e nenhuma delas conhece o banco.
# ---------------------------------------------------------------------------

# As três espécies de ausência que **não** são parcialidade. A quarta — *parcial* — qualifica um
# número que existe, e por isso é atributo de `Numero` e não espécie daqui: colapsá-las faria
# "40 submetidas, ainda crescendo" virar ausência, que é o erro simétrico da `FR-591`.
NAO_APLICAVEL = "nao-aplicavel"
NAO_DISPONIVEL = "nao-disponivel"
NAO_PUBLICADO = "nao-publicado"


@dataclass(frozen=True)
class Ausencia:
    """A razão pela qual um número não existe — dita, e não deixada em branco.

    **É tipo, e não `None`.** Um `None` solto no contexto obrigaria o template a decidir *qual* das
    ausências ele é, e o template decidindo isso é a segunda verdade que a `FR-582` proíbe. Com
    tipo, a derivação decide e a tela apenas escreve.
    """

    especie: str
    motivo: str


@dataclass(frozen=True)
class Numero:
    """Um valor, ou a razão de não haver valor — nunca os dois, nunca nenhum.

    **`valor == 0` é valor**, e é a metade da regra que se perde primeiro. A `016` já a escreve
    inteira: *"Zero é uma afirmação — «não há vaga a ocupar» —, e sem apuração emitida ninguém
    afirmou isso"*. O defeito nunca foi escrever zero; foi escrever zero **no lugar de** um fato
    que não existe. `0` submetidas num Edital publicado é verdade, e apagá-lo esconderia
    justamente o certame sem procura (`FR-591`).
    """

    valor: int | Decimal | None = None
    ausencia: Ausencia | None = None
    parcial: bool = False
    porque: str = ""

    def __post_init__(self):
        tem_valor = self.valor is not None
        if tem_valor == (self.ausencia is not None):
            raise ValueError("Numero é valor ou ausência, nunca os dois e nunca nenhum.")

    @property
    def existe(self) -> bool:
        return self.ausencia is None

    @classmethod
    def de(cls, valor, *, parcial=False, porque=""):
        return cls(valor=valor, parcial=parcial, porque=porque)

    @classmethod
    def nao_aplicavel(cls, motivo):
        return cls(ausencia=Ausencia(NAO_APLICAVEL, motivo))

    @classmethod
    def nao_disponivel(cls, motivo):
        return cls(ausencia=Ausencia(NAO_DISPONIVEL, motivo))

    @classmethod
    def nao_publicado(cls, motivo="sem conteúdo publicado"):
        return cls(ausencia=Ausencia(NAO_PUBLICADO, motivo))


@dataclass(frozen=True)
class SituacaoDoPeriodo:
    """O período de inscrições daquele Edital, na posição do instante da leitura.

    Os três estados vêm do domínio da `009` e **não** são redefinidos aqui: o candidato e a gestão
    precisam responder a mesma pergunta, e dois vocabulários para "as inscrições estão abertas" é o
    que o Princípio I recusa. `NAO_DESIGNADO` não vira quarto estado — vira `Ausencia`.
    """

    estado: str
    inicio: datetime | None = None
    fim: datetime | None = None

    @property
    def aberto(self) -> bool:
        return self.estado == ABERTO

    @property
    def encerrado(self) -> bool:
        return self.estado == ENCERRADO


# As duas marcas, e nada mais (`FR-602`). **Sem identificador de catálogo, sem destino próprio e
# sem severidade**: elas não são espécies de sinal da `022`/`038` — o catálogo daquela feature é
# fechado por requisito (`FR-565`), e acrescentar espécie a ele de fora seria alterá-la sem dizer.
# O destino desta linha é o Edital, como o de qualquer outra linha da tabela (`D-007`).
SEM_PROCURA = "sem-procura"
DEMANDA_ABAIXO_DA_OFERTA = "demanda-abaixo-da-oferta"


@dataclass(frozen=True)
class Marca:
    """A marca, com a frase do resumo e o rótulo curto do detalhe (042, `FR-628`).

    **Dois campos, e não um derivado do outro.** Cortar a frase para obter o rótulo é frágil e
    ilegível; expandir o rótulo para obter a frase perderia o denominador, que é a regra que
    governa esta página. Os dois nascem juntos, da mesma espécie.
    """

    especie: str
    mensagem: str
    rotulo: str = ""


# As três espécies que o conteúdo publica. **Três, e não duas**: `LIMITED` carrega uma quantidade,
# e colapsá-la em "não há" ou em "ilimitado" apagaria o que o Edital declarou (041, `FR-608`).
SEM_RESERVA, RESERVA_LIMITADA, RESERVA_ILIMITADA = "NENHUM", "LIMITADO", "ILIMITADO"


@dataclass(frozen=True)
class Reserva:
    """O cadastro de reserva do Perfil, e o limite quando ele existe.

    **É tipo, e não o booleano `tem_reserva` que a linha do Edital carregava.** Aquele respondia
    *"algum Perfil tem reserva"* — já ambíguo no agregado, e perda no Perfil.
    """

    especie: str = SEM_RESERVA
    limite: int | None = None

    def __post_init__(self):
        if (self.especie == RESERVA_LIMITADA) != (self.limite is not None):
            raise ValueError("reserva limitada tem limite; as outras duas não têm.")

    @property
    def ha(self) -> bool:
        return self.especie != SEM_RESERVA

    @classmethod
    def do_perfil(cls, perfil):
        tipo = (perfil.get("reserveType") or "NONE").upper()
        if tipo == "UNLIMITED":
            return cls(RESERVA_ILIMITADA)
        if tipo == "LIMITED":
            limite = perfil.get("reserveLimit")
            valido = isinstance(limite, int) and not isinstance(limite, bool) and limite >= 0
            # Limitada sem limite legível é conteúdo que o Edital não deveria ter publicado. A
            # tela não inventa o número nem finge que é ilimitada: diz que há reserva e para aí.
            return cls(RESERVA_LIMITADA, limite) if valido else cls(RESERVA_ILIMITADA)
        return cls(SEM_RESERVA)


@dataclass(frozen=True)
class QuadroDoEdital:
    """O que o conteúdo vigente diz sobre vagas, por Perfil e no total."""

    total: int = 0
    quantidades: dict = field(default_factory=dict)
    com_vaga: frozenset = frozenset()
    todos: frozenset = frozenset()
    tem_reserva: bool = False


@dataclass(frozen=True)
class PerfilDaLinha:
    """Um Perfil da versão vigente, com a demanda que coube a ele (041, `FR-607`)."""

    identidade: str
    denominacao: str
    codigo: str
    localidade: str
    vagas: Numero
    reserva: Reserva
    submetidas: Numero
    em_preenchimento: Numero
    razao: Numero
    marcas: tuple = ()

    @property
    def identidade_secundaria(self) -> str:
        """`DOC-INFO · Campus Serra · CR limitado a 6` — o que caracteriza o Perfil (042, `FR-626`).

        **Mora aqui, e não no template** (`FR-582` da `040`): decidir *quais* partes existem e
        *como* se separam é regra, e regra em template é a segunda verdade que aquele requisito
        proíbe.

        **A ausência de reserva não produz texto.** É a grafia que este repositório usa em
        `especie_de_reversao` e em `requerimento_momento`: o vazio **é** a declaração de que não há.
        Escrever *"não há"* em toda linha seria o ruído que a `042` existe para remover.

        **Vazia quando não há nenhuma das três**, e aí a linha some inteira — nunca *"não
        informado"*.
        """
        partes = [parte for parte in (self.codigo, self.localidade) if parte]
        if self.reserva.especie == RESERVA_LIMITADA:
            partes.append(f"CR limitado a {self.reserva.limite}")
        elif self.reserva.especie == RESERVA_ILIMITADA:
            partes.append("CR ilimitado")
        return " · ".join(partes)


@dataclass(frozen=True)
class LinhaDoEdital:
    edital: object
    periodo: SituacaoDoPeriodo | Ausencia
    vagas: Numero
    submetidas: Numero
    em_preenchimento: Numero
    razao: Numero
    marcas: tuple = ()
    perfis: tuple = ()
    # **As que foram para Perfil que a versão vigente não tem mais** (041, `FR-613a`). Contam no
    # total do Edital, não pertencem a Perfil algum, e a diferença é **declarada** — nunca
    # acomodada numa linha que finja ser Perfil.
    submetidas_sem_perfil: int = 0
    rascunhos_sem_perfil: int = 0
    # **A população que a razão usou**, dita quando ela não é a do Edital inteiro (`FR-588`).
    # Vazio significa que numerador e coluna *Submetidas* falam do mesmo conjunto.
    populacao_da_razao: str = ""


@dataclass(frozen=True)
class Consolidado:
    """Os quatro números, e os denominadores que os explicam.

    **Os denominadores são campos, e não prosa montada no template**: é o que permite testá-los sem
    renderizar, e é o que a `FR-585` cobra ao exigir que eles acompanhem o número que explicam —
    como contexto, e nunca como números concorrentes.
    """

    editais: int = 0
    processos: int = 0
    editais_publicados: int = 0
    vagas: Numero = field(default_factory=lambda: Numero.de(0))
    submetidas: Numero = field(default_factory=lambda: Numero.de(0))
    razao: Numero = field(default_factory=lambda: Numero.de(Decimal("0.0")))
    perfis_com_vaga: int = 0
    fora_da_razao: int = 0
    parciais: int = 0

    @property
    def sem_conteudo(self) -> int:
        """Quantos Editais do período não publicaram conteúdo.

        É campo derivado e mora aqui, e não no template: a frase do denominador muda conforme ele
        ser zero ou não — *"em todos os 3"* contra *"em 3 de 5"* —, e um template que subtraísse
        para decidir estaria calculando, que é o que a `FR-582` proíbe.
        """
        return max(self.editais - self.editais_publicados, 0)


TODOS = "todos"


@dataclass(frozen=True)
class Recorte:
    """O que a pessoa pediu, já saneado — valor fora do conjunto aceito nunca chega à consulta."""

    ano: int | str
    situacao: str = ""
    situacao_periodo: str = ""
    busca: str = ""
    ordem: str = ""
    sentido: str = ""
    so_com_atencao: bool = False
    anos_disponiveis: tuple = ()
    padrao: bool = False

    @property
    def rotulo(self) -> str:
        """O recorte aplicado, dito na própria página — e não só no seletor (`FR-599`).

        Sem isto, "12 Editais" é lido como o acervo inteiro.
        """
        return "Editais de todos os anos" if self.ano == TODOS else f"Editais de {self.ano}"


# As ordens aceitas, no padrão de `portal/leitura.py`: o que vier fora do conjunto vira o padrão.
ORDEM_PADRAO = "recentes"
# **As chaves não mudam, e os rótulos sim** (042, `FR-630`, `R-007`). *"Mais recentes"* já era uma
# direção, e combinada com *"Menor primeiro"* significava *"mais antigos"* — que ninguém lê assim.
# Trocar as **chaves** quebraria endereços já guardados, sem ganho nenhum.
ORDENS = {
    "recentes": "Data do Edital",
    "vagas": "Vagas",
    "submetidas": "Inscrições submetidas",
    "razao": "Inscr./vaga",
}
SENTIDOS_LEGIVEIS = {"desc": "Decrescente", "asc": "Crescente"}
SITUACOES_DO_PERIODO = (FUTURO, ABERTO, ENCERRADO, NAO_DESIGNADO)

SENTIDO_PADRAO = "desc"
SENTIDOS = ("asc", "desc")


# ---------------------------------------------------------------------------
# 3. O recorte
# ---------------------------------------------------------------------------


def anos_disponiveis(actor):
    """Os anos que existem na coluna — **uma consulta de uma coluna, sem abrir snapshot algum**.

    Montar as opções a partir do acervo, e não de uma lista fixa, é o que a `024` já decidiu para a
    vitrine: oferecer um ano sem Edital nenhum é prometer resultado onde não há, e lista fixa
    envelhece calada.
    """
    return tuple(
        sorted(
            Edital.objects.filter(institution_scope=actor.institution_scope)
            .values_list("year", flat=True)
            .distinct(),
            reverse=True,
        )
    )


def recorte_de(parametros, *, actor, hoje=None):
    """O que a pessoa pediu, saneado — e o padrão quando ela não pediu nada (`FR-599`).

    **O ano corrente por omissão não é preferência de tela.** O custo dominante desta página é abrir
    um snapshot por Edital do recorte; um padrão "todos os anos" faria esse custo crescer com a
    história institucional para sempre. O recorte aplicado vai declarado na página, para que
    ninguém leia o recorte como o acervo (`D-013`).
    """
    anos = anos_disponiveis(actor)
    corrente = (hoje or timezone.localtime()).year
    pedido = (parametros.get("ano") or "").strip()

    padrao = not pedido
    if pedido == TODOS:
        ano = TODOS
    else:
        try:
            ano = int(pedido)
        except ValueError:
            ano = corrente
            padrao = True
        if ano not in anos and not padrao:
            # Ano que não existe no acervo não é erro de quem digitou nem motivo de recusa: é
            # recorte vazio, e a página o declara. Cair no corrente aqui esconderia o que a pessoa
            # pediu e mostraria outra coisa com o mesmo rótulo.
            pass
    if padrao:
        ano = corrente

    situacao = (parametros.get("situacao") or "").strip()
    periodo = (parametros.get("periodo") or "").strip()
    ordem = (parametros.get("ordem") or "").strip()
    sentido = (parametros.get("sentido") or "").strip()
    return Recorte(
        ano=ano,
        so_com_atencao=(parametros.get("atencao") or "") == "1",
        situacao=situacao if situacao in Edital.Status.values else "",
        situacao_periodo=periodo if periodo in SITUACOES_DO_PERIODO else "",
        busca=(parametros.get("busca") or "").strip()[:100],
        ordem=ordem if ordem in ORDENS else ORDEM_PADRAO,
        sentido=sentido if sentido in SENTIDOS else SENTIDO_PADRAO,
        anos_disponiveis=anos,
        padrao=padrao,
    )


def _editais_do_recorte(actor, recorte):
    """Os filtros **relacionais**, aplicados antes de materializar versão nenhuma (`FR-598`).

    Escopo, ano, situação e busca são colunas. A situação do período **não** é: ela mora no
    conteúdo publicado, e por isso é aplicada depois, sobre o conjunto que estes já reduziram. A
    redação anterior da `FR-598` exigia todos antes de qualquer leitura de conteúdo, e era contrato
    impossível.
    """
    consulta = Edital.objects.filter(institution_scope=actor.institution_scope)
    if recorte.ano != TODOS:
        consulta = consulta.filter(year=recorte.ano)
    if recorte.situacao:
        consulta = consulta.filter(status=recorte.situacao)
    if recorte.busca:
        consulta = consulta.filter(
            Q(number__icontains=recorte.busca)
            | Q(title__icontains=recorte.busca)
            | Q(processo__title__icontains=recorte.busca)
            | Q(processo__institutional_code__icontains=recorte.busca)
        )
    return list(consulta.select_related("processo").order_by("-year", "-number"))


# ---------------------------------------------------------------------------
# 4. O que o conteúdo publicado diz sobre vagas
# ---------------------------------------------------------------------------


def vagas_do_conteudo(conteudo):
    """`QuadroDoEdital` do conteúdo vigente (`FR-587`).

    **Do publicado, e nunca das linhas de elaboração.** A Retificação não reescreve o relacional:
    `PerfilVaga.immediate_vacancies` é o rascunho, e o que o Edital **publicou** está aqui. Ler o
    outro seria mais barato e estaria errado depois da primeira Retificação.

    **`com_vaga` é o que torna a razão honesta** (041, `FR-612`): inscrição em Perfil que não
    publica vaga imediata não disputa vaga nenhuma, e somá-la ao numerador produz número
    aritmeticamente correto e institucionalmente falso.

    **`todos` existe desde a 041, e a ausência dele era um buraco** (`FR-613a`, `R-003`): sem o
    conjunto completo, *"Perfil sem vaga imediata"* e *"Perfil que a Retificação removeu"* caíam no
    mesmo ramo. A Inscrição guarda a identidade **publicada** do Perfil, que sobrevive à remoção —
    e é por isso que a diferença precisa ser reconhecível.
    """
    quantidades, com_vaga, todos, reserva = {}, [], [], False
    for perfil in (conteudo or {}).get("profiles") or []:
        if not isinstance(perfil, dict):
            continue
        identidade = str(perfil.get("id"))
        quantidade = perfil.get("immediateVacancies")
        if isinstance(quantidade, bool) or not isinstance(quantidade, int) or quantidade < 0:
            quantidade = 0
        quantidades[identidade] = quantidade
        todos.append(identidade)
        if quantidade > 0:
            com_vaga.append(identidade)
        if (perfil.get("reserveType") or "NONE") != "NONE":
            reserva = True
    return QuadroDoEdital(
        total=sum(quantidades.values()),
        quantidades=quantidades,
        com_vaga=frozenset(com_vaga),
        todos=frozenset(todos),
        tem_reserva=reserva,
    )


def situacao_do_periodo(conteudo, agora):
    """`SituacaoDoPeriodo` ou `Ausencia` — pela leitura da `009`, e não por uma segunda."""
    if conteudo is None:
        return Ausencia(NAO_PUBLICADO, "sem conteúdo publicado")
    lido = periodo_de_inscricoes(conteudo, agora)
    if not lido.designado:
        return Ausencia(NAO_DISPONIVEL, "o cronograma não designou período de inscrições")
    return SituacaoDoPeriodo(estado=lido.estado, inicio=lido.inicio, fim=lido.fim)


# ---------------------------------------------------------------------------
# 5. As inscrições
# ---------------------------------------------------------------------------


def contagens_por_edital(editais):
    """`{edital_id: {"submetidas": {perfil: n}, "rascunhos": n}}` — **uma** consulta para a página.

    **Agrupa por Perfil porque a razão o exige** (`D-012`). O que cresce é o número de linhas
    devolvidas, limitado por `Editais × Perfis × 2`, e o índice `(edital, status)` continua
    servindo. O total da coluna *Submetidas* sai desta **mesma** leitura, de modo que ele e o
    numerador da razão não podem divergir — que é a metade fácil de perder na implementação.

    **O rascunho também é por Perfil desde a 041** (`FR-610`). A consulta já trazia `profile_id` em
    cada linha e o valor era descartado num contador único; passa a ser dicionário, e o total do
    Edital é a soma dos valores. Mesma consulta, mesmas linhas.
    """
    contagens = {}
    if not editais:
        return contagens
    for linha in (
        Inscricao.objects.filter(edital_id__in=[e.pk for e in editais])
        .values("edital_id", "profile_id", "status")
        .annotate(quantidade=Count("id"))
    ):
        por_edital = contagens.setdefault(linha["edital_id"], {"submetidas": {}, "rascunhos": {}})
        onde = "submetidas" if linha["status"] == Inscricao.Status.SUBMETIDA else "rascunhos"
        chave = str(linha["profile_id"])
        por_edital[onde][chave] = por_edital[onde].get(chave, 0) + linha["quantidade"]
    return contagens


# ---------------------------------------------------------------------------
# 6. A composição — a linha, as marcas e o consolidado
# ---------------------------------------------------------------------------


def _razao(numerador, denominador):
    """`submetidas ÷ vagas`, com uma casa. Arredonda meio para cima, como quem lê espera."""
    return (Decimal(numerador) / Decimal(denominador)).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP
    )


def _marcas(periodo, submetidas, razao):
    """As duas, e só quando o período **encerrou** (`FR-602`).

    Com o período aberto não há marca: o número ainda vai mudar, e acusar baixa procura no meio das
    inscrições seria afirmar sobre um dado parcial o que só o definitivo sustenta.
    """
    if not isinstance(periodo, SituacaoDoPeriodo) or not periodo.encerrado:
        return ()
    marcas = []
    if submetidas.existe and submetidas.valor == 0:
        marcas.append(
            Marca(SEM_PROCURA, "Encerrou sem nenhuma inscrição submetida.", "Sem procura")
        )
    if razao.existe and razao.valor < 1:
        marcas.append(
            Marca(
                DEMANDA_ABAIXO_DA_OFERTA,
                "Encerrou com menos inscrições do que vagas imediatas.",
                "Demanda abaixo da oferta",
            )
        )
    return tuple(marcas)


def _marcas_do_edital(perfis, quadro):
    """O resumo das marcas dos Perfis, **cada espécie com o seu denominador** (041, `FR-614`).

    **Os dois denominadores são diferentes, e é a parte que se perde.** *Sem procura* conta sobre
    **todos** os Perfis vigentes; *demanda abaixo da oferta* conta só sobre os que **publicam vaga
    imediata**, porque os demais não têm denominador e não poderiam estar abaixo de coisa nenhuma.
    *"2 de 5"* num Edital em que só três publicam vaga é aritmeticamente verdadeiro e
    institucionalmente enganoso.

    **Com um Perfil só, a mensagem é a dele** (`R-004`): *"1 de 1 Perfil sem nenhuma inscrição"* é
    aritmética falando com quem quer português, e o Edital de um Perfil é o caso mais comum do
    acervo.
    """
    if not perfis:
        return ()
    if len(perfis) == 1:
        return perfis[0].marcas

    vigentes = len(perfis)
    com_vaga = len(quadro.com_vaga)
    resumo = []
    for especie, denominador, frase in (
        (SEM_PROCURA, vigentes, "Perfi{p} sem nenhuma inscrição"),
        (
            DEMANDA_ABAIXO_DA_OFERTA,
            com_vaga,
            "Perfi{p} com vaga imediata abaixo da oferta",
        ),
    ):
        quantos = sum(1 for perfil in perfis if any(m.especie == especie for m in perfil.marcas))
        if not quantos or not denominador:
            continue
        plural = "l" if denominador == 1 else "s"
        resumo.append(Marca(especie, f"{quantos} de {denominador} " + frase.format(p=plural) + "."))
    return tuple(resumo)


def perfis_do_edital(conteudo, contagem, periodo):
    """Os Perfis da versão vigente, com a demanda que coube a cada um (041, `FR-607`).

    **A razão do Perfil sai da mesma função que a do Edital usa** (`FR-611`): duas implementações
    da mesma regra divergiriam na primeira mudança, e a regra aqui é a que a `040` fixou —
    **não aplicável** onde não há vaga imediata, nunca `0` e nunca infinito.
    """
    quadro = vagas_do_conteudo(conteudo)
    submetidas = (contagem or {}).get("submetidas", {})
    rascunhos = (contagem or {}).get("rascunhos", {})
    aberto = isinstance(periodo, SituacaoDoPeriodo) and periodo.aberto
    porque = "as inscrições ainda estão abertas" if aberto else ""

    perfis = []
    for perfil in (conteudo or {}).get("profiles") or []:
        if not isinstance(perfil, dict):
            continue
        identidade = str(perfil.get("id"))
        vagas = quadro.quantidades.get(identidade, 0)
        recebidas = submetidas.get(identidade, 0)
        numero_submetidas = Numero.de(recebidas, parcial=aberto, porque=porque)
        if vagas > 0:
            razao = Numero.de(_razao(recebidas, vagas), parcial=aberto, porque=porque)
        else:
            razao = Numero.nao_aplicavel("não se aplica: este Perfil não publica vaga imediata")
        perfis.append(
            PerfilDaLinha(
                identidade=identidade,
                denominacao=(perfil.get("name") or perfil.get("code") or "").strip(),
                codigo=(perfil.get("code") or "").strip(),
                # **Como publicada, e nada mais** (`FR-609`). Vazio faz a linha sumir: dizer
                # "não informada" afirmaria uma omissão que o Edital pode nunca ter tido.
                localidade=(perfil.get("locality") or "").strip(),
                vagas=Numero.de(vagas),
                reserva=Reserva.do_perfil(perfil),
                submetidas=numero_submetidas,
                em_preenchimento=Numero.de(rascunhos.get(identidade, 0)),
                razao=razao,
                marcas=_marcas(periodo, numero_submetidas, razao),
            )
        )
    return tuple(perfis), quadro


def linha_do_edital(edital, conteudo, contagem, agora):
    """Uma linha da tabela, com as quatro grafias de ausência no lugar delas (`FR-594`)."""
    periodo = situacao_do_periodo(conteudo, agora)
    submetidas_por_perfil = (contagem or {}).get("submetidas", {})
    rascunhos_por_perfil = (contagem or {}).get("rascunhos", {})
    total_submetidas = sum(submetidas_por_perfil.values())
    aberto = isinstance(periodo, SituacaoDoPeriodo) and periodo.aberto
    porque = "as inscrições ainda estão abertas" if aberto else ""

    submetidas = Numero.de(total_submetidas, parcial=aberto, porque=porque)
    em_preenchimento = Numero.de(sum(rascunhos_por_perfil.values()))

    if conteudo is None:
        # **Não publicado não é zero.** Vaga publicada não existe fora do conteúdo vigente, e
        # dizer `0` afirmaria que o Edital publicou nenhuma — que é outra coisa.
        return LinhaDoEdital(
            edital=edital,
            periodo=periodo,
            vagas=Numero.nao_publicado(),
            submetidas=submetidas,
            em_preenchimento=em_preenchimento,
            razao=Numero.nao_publicado(),
        )

    perfis, quadro = perfis_do_edital(conteudo, contagem, periodo)
    vagas = Numero.de(quadro.total)

    if not quadro.com_vaga:
        # **Cadastro de reserva sem vaga imediata não tem denominador** (`FR-589`). Nunca `0`,
        # nunca infinito, e nunca omissão silenciosa: o Edital continua na tabela com vagas e
        # demanda legíveis, e a razão diz que não se aplica.
        razao = Numero.nao_aplicavel("não há vaga imediata publicada: a oferta é cadastro reserva")
        populacao = ""
    else:
        # **A razão do Edital é recalculada dos totais elegíveis** (041, `FR-612`) — e nunca sai
        # da soma nem da média das razões dos Perfis: razão não é grandeza aditiva. Dois Perfis
        # de 20 vagas com `1,0` e `3,0` dão `2,0` no Edital, e jamais `4,0`.
        numerador = sum(
            quantidade
            for perfil, quantidade in submetidas_por_perfil.items()
            if perfil in quadro.com_vaga
        )
        razao = Numero.de(_razao(numerador, quadro.total), parcial=aberto, porque=porque)
        # **A população é dita quando não é a do Edital inteiro** (`FR-588`). Sem isto, a linha
        # mostra 280 submetidas ao lado de uma razão calculada sobre 80, e nada explica a
        # diferença. E dita em português: `inscrição(ões)` é forma de planilha, não de tela.
        flexao = "inscrição" if numerador == 1 else "inscrições"
        populacao = (
            f"sobre {numerador} {flexao} nos Perfis com vaga imediata"
            if numerador != total_submetidas
            else ""
        )

    return LinhaDoEdital(
        edital=edital,
        periodo=periodo,
        vagas=vagas,
        submetidas=submetidas,
        em_preenchimento=em_preenchimento,
        razao=razao,
        marcas=_marcas_do_edital(perfis, quadro),
        perfis=perfis,
        submetidas_sem_perfil=_fora_do_quadro(submetidas_por_perfil, quadro),
        rascunhos_sem_perfil=_fora_do_quadro(rascunhos_por_perfil, quadro),
        populacao_da_razao=populacao,
    )


def _fora_do_quadro(por_perfil, quadro):
    """Quantas inscrições foram para Perfil que a versão vigente não tem mais (`FR-613a`)."""
    return sum(q for perfil, q in por_perfil.items() if perfil not in quadro.todos)


def _consolidar(linhas, conteudos, contagens):
    """Os quatro números do recorte, e os denominadores que os explicam.

    **A soma só soma o que existe, e declara o denominador** — e a razão do recorte é
    `Σ numerador ÷ Σ vagas`, nunca a média das razões por Edital: a média daria peso igual a um
    Edital de 2 vagas e a um de 200.

    **O numerador é recortado nos dois níveis** (`D-012`). Calcular o Edital de um jeito e o
    consolidado de outro faria os dois discordarem — e no consolidado ninguém percebe a olho.
    """
    editais = len(linhas)
    processos = len({linha.edital.processo_id for linha in linhas})
    publicados = sum(1 for linha in linhas if linha.vagas.existe)
    vagas = sum(linha.vagas.valor for linha in linhas if linha.vagas.existe)
    submetidas = sum(linha.submetidas.valor for linha in linhas if linha.submetidas.existe)
    parciais = sum(1 for linha in linhas if linha.submetidas.parcial)

    numerador = denominador = perfis_com_vaga = fora = 0
    for linha in linhas:
        conteudo = conteudos.get(linha.edital.pk)
        if conteudo is None:
            fora += 1
            continue
        quadro = vagas_do_conteudo(conteudo)
        if not quadro.com_vaga:
            fora += 1
            continue
        perfis_com_vaga += len(quadro.com_vaga)
        denominador += quadro.total
        numerador += sum(
            quantidade
            for perfil, quantidade in (contagens.get(linha.edital.pk) or {})
            .get("submetidas", {})
            .items()
            if perfil in quadro.com_vaga
        )

    if denominador:
        razao = Numero.de(_razao(numerador, denominador), parcial=bool(parciais))
    else:
        razao = Numero.nao_aplicavel("nenhum Edital do recorte publica vaga imediata")

    return Consolidado(
        editais=editais,
        processos=processos,
        editais_publicados=publicados,
        vagas=Numero.de(vagas) if publicados else Numero.nao_publicado(),
        submetidas=Numero.de(submetidas, parcial=bool(parciais)),
        razao=razao,
        perfis_com_vaga=perfis_com_vaga,
        fora_da_razao=fora,
        parciais=parciais,
    )


def _chave_de_ordem(linha, ordem):
    numero = {"vagas": linha.vagas, "submetidas": linha.submetidas, "razao": linha.razao}[ordem]
    return numero


def _ordenar(linhas, recorte):
    """A ordem pedida, com **a ausência ao fim nos dois sentidos** (`FR-601`).

    `reverse=True` sobre a mesma chave jogaria as ausências para o começo — quem não tem número
    apareceria antes de quem tem, nos dois sentidos alternadamente. A chave em tupla põe o
    marcador de ausência **fora** da inversão, e só o valor inverte.
    """
    decrescente = recorte.sentido == "desc"
    if recorte.ordem == ORDEM_PADRAO:
        # **O sentido vale aqui também, e essa era a mentira.** A versão anterior devolvia a lista
        # como veio e **ignorava** `sentido`: com "Mais recentes" escolhido, o controle "Maior /
        # Menor primeiro" ficava na tela sem fazer nada. Controle que não obedece é pior que
        # controle ausente — quem o usa conclui que a ordem é aquela.
        #
        # A ordem decrescente é a da consulta (`-year`, `-number`); a crescente é ela invertida, e
        # não uma segunda chave: duas expressões da mesma ordem divergiriam na primeira mudança.
        return tuple(linhas) if decrescente else tuple(reversed(linhas))

    def chave(linha):
        numero = _chave_de_ordem(linha, recorte.ordem)
        if not numero.existe:
            return (1, Decimal(0))
        valor = Decimal(numero.valor)
        return (0, -valor if decrescente else valor)

    return tuple(sorted(linhas, key=chave))


def ler(actor, parametros, *, agora=None, hoje=None):
    """A página inteira, num número **fixo** de consultas (`SC-209`).

    Cinco leituras, e nenhuma cresce com o número de Editais: os anos do seletor, os Editais do
    recorte, o par que resolve a versão vigente de cada um, e a agregação de inscrições. A
    materialização acontece **depois** dos filtros relacionais, e por isso o custo acompanha o
    recorte e não o acervo (`FR-598`, `FR-599`).
    """
    agora = agora or timezone.now()
    recorte = recorte_de(parametros, actor=actor, hoje=hoje)
    editais = _editais_do_recorte(actor, recorte)
    versoes = versoes_vigentes(edital_ids=[e.pk for e in editais], at=agora)
    conteudos = {
        edital.pk: (versoes[edital.pk].content if edital.pk in versoes else None)
        for edital in editais
    }
    contagens = contagens_por_edital(editais)

    linhas = [
        linha_do_edital(edital, conteudos[edital.pk], contagens.get(edital.pk), agora)
        for edital in editais
    ]
    # **A situação do período entra aqui, e não no filtro relacional**: ela mora no snapshot, e
    # aplicá-la antes seria impossível (`FR-598`).
    if recorte.situacao_periodo:
        linhas = [
            linha for linha in linhas if _estado_do_periodo(linha) == recorte.situacao_periodo
        ]
    # **E a atenção é o terceiro degrau** (041, `FR-621`, `R-009`). A marca depende de razão e de
    # contagem **por Perfil**, que só existem depois de ler o conteúdo publicado: empurrá-la para o
    # `SQL` é impossível, e não caro. O consolidado é montado **depois** dela, e por isso acompanha
    # a tabela — como acompanha os demais filtros.
    if recorte.so_com_atencao:
        linhas = [linha for linha in linhas if linha.marcas]

    consolidado = _consolidar(linhas, conteudos, contagens)
    return recorte, _ordenar(linhas, recorte), consolidado


def _estado_do_periodo(linha):
    return linha.periodo.estado if isinstance(linha.periodo, SituacaoDoPeriodo) else NAO_DESIGNADO
