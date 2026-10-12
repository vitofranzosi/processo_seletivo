"""O catálogo de Seções do Edital — declarado, e não gerenciável.

O conjunto de seções e a ordem entre elas são definidos pelo sistema; quem elabora edita o texto
das textuais (FR-034). É o que separa um documento institucional estruturado de um construtor de
documentos.

**Por que declaração em código, e não linhas de tabela.** A estrutura passaria a depender do estado
do banco, e um Edital criado antes de uma mudança de catálogo ficaria estruturalmente diferente sem
que nada registrasse a diferença. Declarado, o catálogo é revisável em diff, dispensa migration para
mudar, e a ausência de uma seção do catálogo no conteúdo deixa de ser estado alcançável. A seção
**vazia** é alcançável, e é outra coisa: está no conteúdo, e não sai no documento (054, FR-982).

**A identidade é determinística.** A seção precisa ter identidade **antes de existir linha em
`SecaoEdital`** — a gerada nunca tem linha, e a textual só passa a ter depois da primeira edição.
`uuid5` sobre `(edital.id, key)` dá identidade estável desde o primeiro snapshot, igual entre duas
gerações do mesmo conteúdo e distinta entre Editais. E é UUID, e não a chave textual, porque o
seletor da gramática de Retificação só aceita UUID (`publicacoes/domain/changes.py:101-113`):
`/sections/id=cronograma/content` seria recusado como seletor inválido e a coleção ficaria
inendereçável.
"""

from dataclasses import dataclass
from uuid import NAMESPACE_URL, UUID, uuid5

GERADA = "GENERATED"
TEXTUAL = "TEXT"


@dataclass(frozen=True)
class Secao:
    """Uma entrada do catálogo.

    `source` nomeia a coleção que origina o conteúdo de uma seção gerada; a textual não tem origem,
    e o texto dela é o que quem elabora escreveu para o Edital.

    **Sem redação padrão** (054, FR-983). A entrada carregava um `default_text`, que ia ao ato
    sempre que ninguém tocava a seção. Toda redação padrão afirmava alguma norma — a de "Critérios
    de Classificação" falava de pontuação num Edital por sorteio, a de "Disposições Finais" mandava
    os omissos a uma "autoridade responsável" que os Editais do Cefor não nomeiam assim —, e desde
    28/09 o PDF é o ato oficial: norma que ninguém escreveu passava a ser publicada. Com a E10 = B
    da `DP-20`, o texto nasce no Word do setor e é transcrito, e o padrão não poupava trabalho a
    ninguém. A textual nasce vazia, e vazia não sai no documento.
    """

    key: str
    title: str
    order: int
    type: str
    source: str = ""

    @property
    def gerada(self) -> bool:
        return self.type == GERADA


def _textual(key, title, order):
    return Secao(key=key, title=title, order=order, type=TEXTUAL)


def _gerada(key, title, order, source):
    return Secao(key=key, title=title, order=order, type=GERADA, source=source)


# **O catálogo da 054** (FR-980, D-001), congelado: o que todo Edital publicado até a `069` carrega
# no snapshot, com estes títulos e esta ordem. Não é mais o catálogo vigente — é o que o acervo diz,
# e é por ele que a `069` reconhece a apresentação plana e lê as remissões textuais aos títulos de
# antes (R-013).
#
# **O catálogo da 054** (FR-980, D-001): a união das seções que se repetem nas quatro famílias da
# amostra do Cefor — FIC, pós-graduação e aperfeiçoamento, bolsista UAB/FAPES, chamada pública
# técnica —, na ordem que os quinze Editais seguem, **a oferta antes da inscrição**. Eram 12
# entradas, e no 28/2026, o Edital do teste operacional, 8 das 15 seções não tinham lugar.
#
# **As chaves das 12 de antes não mudaram** (FR-981): a linha de `SecaoEdital` e a identidade
# `uuid5` são pela chave, e é isso que mantém o texto já escrito num rascunho na seção em que foi
# escrito. Só a `order` mudou — e ela não é gravada no rascunho, é lida daqui.
#
# **Mudar este catálogo depois da primeira publicação real não tranca o acervo** — a Retificação
# confere a topologia contra a do Edital publicado, e não contra esta lista (054, D-003) —, mas
# deixa o acervo com duas formas de documento, porque documento publicado não se regenera. É por
# isso que ele foi decidido antes do piloto.
CATALOGO_DA_054: tuple[Secao, ...] = (
    # O preâmbulo: sai sem número, logo abaixo do anúncio do ato (008, FR-010). Nos quinze Editais
    # da amostra ele abre pela autoridade que pratica o ato — "A Diretora do Cefor [...] faz saber".
    _textual("apresentacao", "Apresentação", 1),
    _textual("disposicoes-preliminares", "Disposições Preliminares", 2),
    _textual("informacoes-gerais", "Informações Gerais sobre o Curso", 3),
    _textual("publico-alvo", "Público-Alvo", 4),
    _textual("requisitos-gerais", "Requisitos Gerais de Participação", 5),
    _gerada("perfis", "Perfis de Vaga", 6, "profiles"),
    _textual("inscricao", "Da Inscrição", 7),
    # Gerada, e ao lado da textual `inscricao` em vez de dentro dela: uma entrada do catálogo é
    # textual **ou** gerada, e o híbrido pediria um terceiro tipo para atender um caso. O que a
    # seção enuncia — os documentos que o candidato precisa apresentar — deriva dos dados
    # estruturados, como Perfis, Etapas e Cronograma já derivam (FR-010 da 009).
    _gerada(
        "documentos-exigidos", "Documentos Exigidos para a Inscrição", 8, "documentRequirements"
    ),
    # A verificação da autodeclaração étnico-racial (a heteroidentificação) e a da deficiência, que
    # o 28/2026 separa em duas seções (6 e 7), são a mesma matéria — a elegibilidade às vagas
    # reservadas — para públicos diferentes: uma entrada, e o texto transcrito as separa.
    _textual("verificacao-autodeclaracao", "Da Verificação da Autodeclaração", 9),
    # Depois da verificação, e não depois do certificado como no 28/2026: as duas são matéria da
    # reserva de vagas, e a entrevista acontece antes do início do curso.
    _textual("atendimento-pcd", "Do Atendimento à Pessoa com Deficiência", 10),
    _gerada("etapas", "Etapas de Avaliação", 11, "stages"),
    _textual("classificacao", "Critérios de Classificação", 12),
    # Seção, e não anexo, embora doze dos quinze o publiquem como Anexo I: no sistema, anexo é
    # arquivo à parte com rótulo do autor (020, D-002), e um "Anexo I" gerado colidiria com o que o
    # autor escrever.
    _gerada("cronograma", "Cronograma", 13, "schedule"),
    _textual("recursos", "Dos Recursos", 14),
    _textual("convocacao", "Da Convocação", 15),
    # Onde o documento publica a declaração do Requerimento de Matrícula (054, FR-996).
    _textual("matricula", "Da Matrícula", 16),
    _textual("acesso-ao-curso", "Do Acesso ao Curso", 17),
    _textual("homologacao-matricula", "Da Homologação da Matrícula", 18),
    _textual("certificado", "Do Certificado", 19),
    _textual("prazo-de-validade", "Do Prazo de Validade", 20),
    _gerada("anexos", "Anexos", 21, "attachments"),
    _textual("disposicoes-finais", "Disposições Finais", 22),
)


# **O catálogo da 069** (FR-1367, D-001): a ordem e os títulos do *Catálogo apresentado* da spec —
# a ordem das perguntas do candidato, títulos em pergunta onde ajudam e diretos onde funcionam
# melhor. **As chaves e os tipos são os da 054** (FR-1367): a identidade `uuid5` do texto já escrito
# num rascunho é pela chave, e a Retificação confere a topologia pela chave. Mudam o título e a
# ordem, que o snapshot copia na submissão — e é por essa cópia que a apresentação por perguntas se
# reconhece (R-001).
#
# O título da chave principal de uma seção apresentada é o da seção; o de uma chave que sai como
# subseção (N.k) é o da subseção. `APRESENTACAO`, abaixo, diz quem é principal e quem é subseção.
CATALOGO_DA_069: tuple[Secao, ...] = (
    _textual("apresentacao", "Apresentação", 1),
    _textual("disposicoes-preliminares", "Disposições preliminares", 2),
    # "Informações gerais", para todo Edital (clarify, Q3): a seção serve às quatro famílias da
    # amostra, inclusive à seleção de bolsista. O texto pode abrir subtítulo próprio ("Sobre o
    # curso").
    _textual("informacoes-gerais", "Informações gerais", 3),
    _textual("publico-alvo", "Público-alvo", 4),
    _textual("requisitos-gerais", "Requisitos gerais", 5),
    _gerada("perfis", "Quantas vagas há, e onde?", 6, "profiles"),
    _gerada("cronograma", "Cronograma", 7, "schedule"),
    _textual("inscricao", "Como se inscrever?", 8),
    _textual("atendimento-pcd", "Atendimento à pessoa com deficiência", 9),
    _gerada("documentos-exigidos", "Quais documentos enviar?", 10, "documentRequirements"),
    _textual("classificacao", "Como será a seleção?", 11),
    _gerada("etapas", "Etapas de avaliação", 12, "stages"),
    _textual("verificacao-autodeclaracao", "Verificação da autodeclaração", 13),
    _textual("recursos", "Como recorrer?", 14),
    _textual("convocacao", "Como será a convocação?", 15),
    _textual("matricula", "Como será a matrícula?", 16),
    _textual("acesso-ao-curso", "Acesso ao curso", 17),
    _textual("homologacao-matricula", "Homologação da matrícula", 18),
    _textual("certificado", "Certificado", 19),
    _textual("prazo-de-validade", "Prazo de validade", 20),
    _gerada("anexos", "Anexos", 21, "attachments"),
    _textual("disposicoes-finais", "Disposições finais", 22),
)
CATALOGO = CATALOGO_DA_069

POR_CHAVE = {secao.key: secao for secao in CATALOGO}

# **As redações padrão que o catálogo teve até a `053`**, e que a `054` retirou (FR-983). Ficam
# aqui porque o acervo as carrega: todo Edital publicado antes da `054` com uma seção que ninguém
# tocou publicou uma delas — `ler_secoes` nunca gravava o texto igual ao padrão, então, nesse
# acervo, texto igual a uma delas é exatamente texto que ninguém escreveu. O reuso precisa
# reconhecê-las, ou copiaria para um Edital novo a norma que ninguém redigiu para ele — a de
# "Critérios de Classificação" fala de pontuação num Edital por sorteio. A dos Recursos tem duas
# grafias porque a `018` a reescreveu.
REDACOES_PADRAO_RETIRADAS = frozenset(
    {
        "O Instituto Federal do Espírito Santo, por meio do Centro de Referência em Formação e em "
        "Educação a Distância, torna pública a realização do processo seletivo regido por este "
        "Edital.",
        "O presente Edital estabelece as normas do processo seletivo, cuja execução observará a "
        "legislação aplicável e os princípios que regem a Administração Pública.",
        "Poderá participar do processo seletivo quem atender às condições estabelecidas neste "
        "Edital e aos requisitos específicos do Perfil de Vaga pretendido, comprovados na forma e "
        "nos prazos aqui previstos.",
        "A inscrição será realizada exclusivamente pelos meios indicados neste Edital, nos prazos "
        "do Cronograma, e implica conhecimento e aceitação das condições aqui estabelecidas.",
        "A classificação observará a pontuação obtida nas Etapas de Avaliação, respeitados os "
        "pesos e as notas mínimas declarados neste Edital e as reservas de vaga previstas.",
        "Caberá recurso contra os resultados divulgados, nos prazos do Cronograma, pelos meios "
        "indicados neste Edital.",
        "Caberá recurso contra os resultados divulgados nos casos e prazos que este Edital declara "
        "para cada marco classificatório, pelos meios nele indicados.",
        "Os casos omissos serão resolvidos pela autoridade responsável pelo processo seletivo, "
        "observada a legislação aplicável.",
    }
)


def texto_redigido(conteudo) -> str:
    """O texto da seção, se alguém o escreveu; vazio para a seção vazia e a redação retirada."""
    texto = str(conteudo or "").strip()
    return "" if texto in REDACOES_PADRAO_RETIRADAS else texto


CHAVES_TEXTUAIS = frozenset(secao.key for secao in CATALOGO if not secao.gerada)

# O espaço de nomes do `uuid5`. Fixá-lo é o que torna a identidade reproduzível entre execuções e
# entre máquinas; derivá-lo do ambiente faria a mesma seção do mesmo Edital ter duas identidades.
NAMESPACE = uuid5(NAMESPACE_URL, "https://cefor.ifes.edu.br/editais/sections")


def identidade(edital_id, key: str) -> UUID:
    return uuid5(NAMESPACE, f"{edital_id}:{key}")


def e_textual(key: str) -> bool:
    return key in CHAVES_TEXTUAIS


# --------------------------------------------------------------------------------------------------
# 069 — As duas apresentações do documento (R-001, R-002)
# --------------------------------------------------------------------------------------------------

POR_PERGUNTAS = "por perguntas"
PLANA = "plana"

# Os lugares do conteúdo gerado numa seção apresentada (R-002): o que o sistema escreve a partir do
# dado, e onde. Um nome por lugar, para que a composição e a numeração leiam a mesma lista.
REQUISITOS_DOS_PERFIS = "requisitos dos Perfis"
VAGAS = "vagas"
ATRIBUICOES = "atribuições"
PERIODO = "período de inscrições"
DADOS_DECLARADOS = "dados declarados"
TETO = "teto de inscrições"
LEMBRETE_DO_REQUERIMENTO = "lembrete do Requerimento"
REGRAS_DOS_MARCOS = "regras de classificação"
DADOS_DO_SORTEIO = "dados do sorteio"
ETAPAS = "etapas de avaliação"
RECURSO_DOS_MARCOS = "recurso dos marcos"
FORMA_DE_CONVOCACAO = "forma de convocação"
REQUERIMENTO = "Requerimento de Matrícula"


@dataclass(frozen=True)
class SecaoApresentada:
    """Uma seção do documento na apresentação por perguntas (R-002).

    `principal` é a chave cujo texto sai no corpo da seção, sem subtítulo — no começo, ou onde
    `partes` a puser. `partes` são, na ordem, as chaves que saem como subseções N.k — com o título
    que têm no catálogo — e os lugares do conteúdo gerado. **Nada aqui muda chave**: a seção
    reúne, na apresentação, o que o conteúdo guarda separado, e por isso o snapshot e a topologia
    da Retificação ficam como estão.
    """

    titulo: str
    principal: str | None = None
    partes: tuple[str, ...] = ()

    @property
    def membros(self):
        return tuple(
            parte for parte in self.partes if parte in POR_CHAVE and parte != self.principal
        )

    @property
    def ordem(self):
        """As partes na ordem do documento, com a principal no começo se `partes` não a põe."""
        if self.principal is None or self.principal in self.partes:
            return self.partes
        return (self.principal, *self.partes)

    @property
    def gerados(self):
        return tuple(parte for parte in self.partes if parte not in POR_CHAVE)


# A ordem e os títulos do *Catálogo apresentado* da spec (D-001), com as seções reunidas sob a
# pergunta a que respondem (FR-1368) e cada regra gerada na seção que trata dela (FR-1369).
APRESENTACAO: tuple[SecaoApresentada, ...] = (
    SecaoApresentada("Disposições preliminares", "disposicoes-preliminares"),
    SecaoApresentada("Informações gerais", "informacoes-gerais"),
    SecaoApresentada(
        "Quem pode se inscrever?",
        partes=("publico-alvo", "requisitos-gerais", REQUISITOS_DOS_PERFIS),
    ),
    SecaoApresentada("Quantas vagas há, e onde?", "perfis", partes=(VAGAS, ATRIBUICOES)),
    SecaoApresentada("Cronograma", "cronograma"),
    SecaoApresentada(
        "Como se inscrever?",
        "inscricao",
        partes=(PERIODO, DADOS_DECLARADOS, TETO, LEMBRETE_DO_REQUERIMENTO, "atendimento-pcd"),
    ),
    SecaoApresentada(
        "Quais documentos enviar?", "documentos-exigidos", partes=(LEMBRETE_DO_REQUERIMENTO,)
    ),
    SecaoApresentada(
        "Como será a seleção?",
        "classificacao",
        partes=(REGRAS_DOS_MARCOS, DADOS_DO_SORTEIO, ETAPAS, "verificacao-autodeclaracao"),
    ),
    # O recurso de cada marco e a forma de convocação vêm antes do texto de quem redigiu
    # (contrato do documento §5): a regra do sistema primeiro, e o canal e o modo, que são do texto,
    # depois.
    SecaoApresentada("Como recorrer?", "recursos", partes=(RECURSO_DOS_MARCOS, "recursos")),
    SecaoApresentada(
        "Como será a convocação?", "convocacao", partes=(FORMA_DE_CONVOCACAO, "convocacao")
    ),
    SecaoApresentada(
        "Como será a matrícula?",
        "matricula",
        partes=(REQUERIMENTO, "acesso-ao-curso", "homologacao-matricula"),
    ),
    SecaoApresentada("Certificado", "certificado"),
    SecaoApresentada("Prazo de validade", "prazo-de-validade"),
    SecaoApresentada("Anexos", "anexos"),
    SecaoApresentada("Disposições finais", "disposicoes-finais"),
)
# A chave `etapas` não é principal nem membro: as Etapas saem como subseções da seleção, uma por
# Etapa, pelo lugar `ETAPAS`. O preâmbulo (`apresentacao`) abre o documento, sem número.
CHAVE_DAS_ETAPAS = "etapas"


def assinatura(catalogo) -> frozenset:
    """A marca de um catálogo: o conjunto `(chave, título, ordem)` das suas seções (R-001)."""
    return frozenset((secao.key, secao.title, secao.order) for secao in catalogo)


def assinatura_do_snapshot(snapshot) -> frozenset:
    return frozenset(
        (secao.get("key"), secao.get("title"), secao.get("order"))
        for secao in (snapshot or {}).get("sections") or []
        if isinstance(secao, dict)
    )


# **O registro das apresentações, explícito** (R-001). A assinatura do catálogo da `069` → por
# perguntas; qualquer outra → plana. Explícito, e não "igual ao catálogo vigente": uma mudança
# futura do catálogo devolveria em silêncio os Editais da `069` à forma plana. Quem mudar o
# catálogo congela o de agora e o acrescenta aqui.
APRESENTACOES = {assinatura(CATALOGO_DA_069): POR_PERGUNTAS}


def apresentacao_de(snapshot) -> str:
    """A apresentação do documento deste snapshot: pela assinatura do catálogo em que nasceu."""
    return APRESENTACOES.get(assinatura_do_snapshot(snapshot), PLANA)


# **Os títulos do catálogo anterior e para onde a matéria deles foi** (R-013, FR-1400). Um texto
# livre que cite a seção pelo título de antes ("conforme a seção Perfis de Vaga") aponta para um
# lugar que, na apresentação por perguntas, pode não existir com esse nome — ou existir repartido. O
# aviso de conferência lê daqui: um destino só sugere a seção; mais de um diz que ela foi repartida.
DESTINOS_DOS_TITULOS_DA_054 = {
    "Perfis de Vaga": (
        "Quantas vagas há, e onde?",
        "Quem pode se inscrever?",
        "Como será a seleção?",
    ),
    "Disposições Preliminares": ("Disposições preliminares",),
    "Informações Gerais sobre o Curso": ("Informações gerais",),
    "Público-Alvo": ("Quem pode se inscrever?",),
    "Requisitos Gerais de Participação": ("Quem pode se inscrever?",),
    "Da Inscrição": ("Como se inscrever?",),
    "Documentos Exigidos para a Inscrição": ("Quais documentos enviar?",),
    "Da Verificação da Autodeclaração": ("Como será a seleção?",),
    "Do Atendimento à Pessoa com Deficiência": ("Como se inscrever?",),
    "Etapas de Avaliação": ("Como será a seleção?",),
    "Critérios de Classificação": ("Como será a seleção?",),
    "Dos Recursos": ("Como recorrer?",),
    "Da Convocação": ("Como será a convocação?",),
    "Da Matrícula": ("Como será a matrícula?",),
    "Do Acesso ao Curso": ("Como será a matrícula?",),
    "Da Homologação da Matrícula": ("Como será a matrícula?",),
    "Do Certificado": ("Certificado",),
    "Do Prazo de Validade": ("Prazo de validade",),
    "Disposições Finais": ("Disposições finais",),
}
