"""A composição do Centro de Controle do Edital (136) — pura, sobre o andamento da `127`.

**Leitura de leitura** (FR-4705, R-001). Nada aqui toca o banco nem deriva fato novo. A entrada é o
`Andamento` que `andamento.do_edital` já monta, com as sete situações por ponto e por lista e as
providências do nível 1. Esta camada só **agrupa** os pontos em fases e **agrega** as situações, por
regras fixas — e é por serem puras que as regras se provam em todas as famílias de classificação,
inclusive as que nenhum cenário de treinamento tem (dois Perfis, seleção concluída).

**Duas leituras, separadas.** Uma fase pode estar em curso, com uma lista concluída, e ainda assim
oferecer duas ações — uma da pessoa, outra de outro papel. São duas perguntas, com dados próprios:

- **o andamento** (`agregar`, `juntar`): em que ponto a fase está, só pelos atos já feitos;
- **o que a fase oferece agora, e a quem**: as providências da `127`, cada uma na sua fase.

**O que a fase é, e o que ela não é** (D-003). Um rótulo de apresentação para pontos que a derivação
já conhece. Não é coluna, nem estado, nem "a" fase do Edital: várias podem estar em curso ao mesmo
tempo, e nenhuma é eleita a atual. É a primeira decisão do estudo de 09/11, tomada pelo usuário,
e revê a recusa de barra de fases da `127` conservando a razão dela: o Edital não tem etapa atual.

**Nenhuma regra de disponibilidade.** O que se pode fazer é o que a providência diz, e o link é o
dela. A fase Conclusão, em particular, nunca diz que o Edital pode ser encerrado (FR-4714): quem
decide é a tela do ato, com as pendências do encerramento.

Os nomes e as frases moram em `conceitos.py`.
"""

from dataclasses import dataclass, field

from processo_seletivo.interface import andamento as a
from processo_seletivo.interface import conceitos as c
from processo_seletivo.interface import providencias as p

# ---------------------------------------------------------------------------------------------
# Onde cada ponto e cada providência mora (FR-4709, FR-4716, R-004)
# ---------------------------------------------------------------------------------------------

_DO_TIPO = {
    a.RELACAO: c.CLASSIFICACAO,
    a.SEMENTE: c.CLASSIFICACAO,
    a.SORTEIO: c.CLASSIFICACAO,
    a.ORDEM: c.CLASSIFICACAO,
    a.CORTE: c.VAGAS,
    a.APURACAO: c.VAGAS,
    a.RESULTADO: c.RESULTADO,
    a.CONVOCACAO: c.CONVOCACAO,
}
_DA_ETAPA = (a.ETAPA, a.DISTRIBUIR, a.AVALIAR, a.CONSOLIDAR, a.REAVALIAR)
_DA_NATUREZA = {
    **_DO_TIPO,
    **dict.fromkeys(_DA_ETAPA, c.AVALIACAO),
    a.CONFERIR: c.CONVOCACAO,
    a.RECURSO: c.RESULTADO,
    # A passagem ao setor vem depois do desfecho, e é a pergunta da Conclusão (153, D-002).
    a.FORMALIZACAO: c.CONCLUSAO,
}
#: Toda natureza que a `127` emite tem fase. O teste prende que nenhuma cai no padrão.
NATUREZAS_CONHECIDAS = frozenset(_DA_NATUREZA)


def fase_do_ponto(ponto):
    """A fase de um ponto da jornada.

    A Etapa governada corre entre o corte e a apuração (a ordem que a `127` já dá a ela): para quem
    conduz, é parte de "quem ocupa as vagas", e não da avaliação que alimenta a classificação.
    """
    if ponto.tipo == a.ETAPA:
        return c.VAGAS if ponto.grupo == a.GRUPO_DA_GOVERNADA else c.AVALIACAO
    return _DO_TIPO.get(ponto.tipo, c.CLASSIFICACAO)


def etapas_governadas(perfis):
    """Os ids das Etapas que algum corte governa, pelos pontos que a `127` já agrupou."""
    return {
        str((ponto.etapa or {}).get("id"))
        for perfil in perfis
        for ponto in perfil.pontos
        if ponto.tipo == a.ETAPA and ponto.grupo == a.GRUPO_DA_GOVERNADA
    }


def fase_da_providencia(providencia, governadas):
    """A fase de uma providência do nível 1 (D-004).

    A Etapa é achada pelo **id** que a derivação põe na chave (`("etapa", eid, …)`), e não pelo
    nome: o protótipo comparava o nome da Etapa com o texto de `onde`, e duas Etapas homônimas em
    Perfis diferentes o enganariam.
    """
    if providencia.natureza in _DA_ETAPA:
        chave = providencia.chave or ()
        if len(chave) > 1 and chave[0] == "etapa" and str(chave[1]) in governadas:
            return c.VAGAS
        return c.AVALIACAO
    return _DA_NATUREZA.get(providencia.natureza, c.CLASSIFICACAO)


# ---------------------------------------------------------------------------------------------
# A primeira leitura: o andamento (FR-4710, FR-4711)
# ---------------------------------------------------------------------------------------------


def agregar(celulas):
    """O andamento de uma fase numa lista, pelas células dela; `None` se não há célula.

    Tudo feito (ou não se aplica, com algum feito) → concluída; tudo não se aplica → não se aplica;
    só *Depois* → ainda não começou; o resto → em curso. **Não diz se há o que fazer**: isso é das
    providências. A ausência de ato nunca é pendência, como na `127`.

    **O *Depois* com ato vigente para trás é andamento** (141, FR-4845). A ordem sucessora que
    espera a Etapa do reabilitado é *Depois*, mas a ordem vigente existe e produz efeito: dizer
    "ainda não começou" da Classificação, no C08, apagava a ordem já emitida e divulgada.
    """
    presentes = [celula for celula in celulas if celula is not None]
    situacoes = [celula.situacao for celula in presentes]
    if not situacoes:
        return None
    if all(s == a.NAO_SE_APLICA for s in situacoes):
        return c.NAO_SE_APLICA
    if all(s in (a.FEITO, a.NAO_SE_APLICA) for s in situacoes):
        return c.CONCLUIDA
    if all(s in (a.DEPOIS, a.NAO_SE_APLICA) for s in situacoes) and not any(
        celula.vigente_para_tras for celula in presentes
    ):
        return c.NAO_INICIADA
    return c.EM_CURSO


def juntar(andamentos):
    """O andamento da fase no Edital, a partir do de cada lista; `None` se não há nenhum."""
    presentes = [x for x in andamentos if x is not None]
    if not presentes:
        return None
    aplicaveis = [x for x in presentes if x != c.NAO_SE_APLICA]
    if not aplicaveis:
        return c.NAO_SE_APLICA
    if all(x == c.CONCLUIDA for x in aplicaveis):
        return c.CONCLUIDA
    if all(x == c.NAO_INICIADA for x in aplicaveis):
        return c.NAO_INICIADA
    # Uma lista concluída ao lado de outra que não começou é andamento, e não "ainda não".
    return c.EM_CURSO


# ---------------------------------------------------------------------------------------------
# As estruturas (data-model)
# ---------------------------------------------------------------------------------------------


@dataclass
class PassoDoRoteiro:
    simples: str
    termo: str
    curta: str
    porque: str
    ao_confirmar: str
    andamento: str
    feitas: int
    total: int
    #: A semente vale para o marco inteiro, e a Etapa para o Perfil: o passo é um só.
    unico: bool
    tem_acao: bool = False
    #: Por que o passo ainda não começou — a razão que a derivação já dá à célula *Depois*.
    razao: str = ""

    @property
    def rotulo(self):
        return c.ROTULOS.get(self.andamento, "")

    @property
    def sinal(self):
        return c.SINAIS.get(self.andamento, "")

    @property
    def mostra_o_termo(self):
        """ "no GPS: …" só quando diz algo: a Etapa tem o nome do Edital, e o sorteio é sorteio."""
        return self.termo != "Etapa" and self.termo.lower() != self.simples.lower()


@dataclass
class CelulaNaFase:
    passo: str
    celula: a.Celula

    @property
    def ato(self):
        """O ato na língua da coluna: "Classificar a lista", e não "Emitir a ordem"."""
        if self.celula.situacao in a.A_PRATICAR:
            return c.ato_simples(self.celula.natureza, self.celula.ato)
        return self.celula.ato


@dataclass
class ListaNaFase:
    rotulo: str
    andamento: str | None
    celulas: list


@dataclass
class FaseNoPerfil:
    perfil: a.PerfilNoAndamento
    roteiro: list
    listas: list

    @property
    def passos(self):
        """Os nomes das colunas da tabela por lista, na ordem do roteiro."""
        return [passo.simples for passo in self.roteiro]


@dataclass
class ItemDeProvidencia:
    p: p.Providencia
    fase_chave: str
    conceito: dict | None
    #: O nome do ato na língua de quem conduz; o ato da `127` vira "no GPS: …".
    titulo: str
    no_gps: str = ""
    paralela: str = ""

    @property
    def fase(self):
        return c.NOMES[self.fase_chave]

    @property
    def titulo_no_meio_da_frase(self):
        """Depois de "Quem conduz a seleção:", só com a inicial minúscula — o nome da Etapa e o
        código da lista ficam como o Edital os publica."""
        return self.titulo[:1].lower() + self.titulo[1:]


@dataclass
class Macrofase:
    chave: str
    andamento: str
    resumo: str = ""
    nota: str = ""
    paralela: str = ""
    perfis: list = field(default_factory=list)
    providencias: list = field(default_factory=list)
    #: As Retificações em curso que ainda prosseguem, no resumo da `103` (só na fase Edital). Não
    #: são providências (D-017 da `127`), mas são algo em aberto, e de alguém (FR-2819 da `104`).
    retificacoes: list = field(default_factory=list)

    @property
    def nome(self):
        return c.NOMES[self.chave]

    @property
    def pergunta(self):
        return c.PERGUNTAS[self.chave]

    @property
    def rotulo(self):
        return c.ROTULOS[self.andamento]

    @property
    def sinal(self):
        return c.SINAIS[self.andamento]

    @property
    def em_curso(self):
        return self.andamento == c.EM_CURSO

    @property
    def por_lista(self):
        return self.chave in c.POR_LISTA

    # A segunda leitura: o que a fase oferece agora, e a quem (FR-4715).
    @property
    def suas(self):
        return [i for i in self.providencias if i.p.grupo == p.SUA]

    @property
    def de_outros(self):
        return [i for i in self.providencias if i.p.grupo == p.DE_OUTRO]

    @property
    def aguardando(self):
        return [i for i in self.providencias if i.p.situacao == a.AGUARDA]

    @property
    def impedidas(self):
        return [i for i in self.providencias if i.p.situacao == a.IMPEDIDO]

    @property
    def espera_ate(self):
        datas = [i.p.ate for i in self.aguardando if i.p.ate]
        return min(datas) if datas else None

    @property
    def retificacoes_suas(self):
        return [r for r in self.retificacoes if r.get("meu_ato")]

    @property
    def retificacoes_de_outros(self):
        return [r for r in self.retificacoes if not r.get("meu_ato") and r.get("passo")]

    @property
    def quantas_suas(self):
        return len(self.suas) + len(self.retificacoes_suas)

    @property
    def quantas_de_outros(self):
        return len(self.de_outros) + len(self.retificacoes_de_outros)

    @property
    def em_aberto(self):
        return bool(self.providencias or self.retificacoes)

    @property
    def parada(self):
        """Em curso, mas sem nada que alguém possa fazer agora: depende de outra fase."""
        return self.em_curso and not self.em_aberto


@dataclass(frozen=True)
class FaseNaLista:
    """O andamento de uma fase numa lista, para a tabela de "Onde cada lista está"."""

    chave: str
    andamento: str | None

    @property
    def valor(self):
        return self.andamento or c.NAO_SE_APLICA

    @property
    def sinal(self):
        return c.SINAIS[self.valor]

    @property
    def rotulo(self):
        return c.ROTULOS_CURTOS[self.valor]


@dataclass
class ListaNoCentro:
    rotulo: str
    curto: str
    #: `[FaseNaLista]`, uma por fase por lista, na ordem do mapa.
    fases: list
    concluida: bool
    #: `[(nome da fase, Celula, título)]`: os atos a praticar, um por fase, na ordem da jornada.
    atos: list = field(default_factory=list)
    #: A primeira célula em espera ou impedida, quando não há ato a praticar.
    espera: a.Celula | None = None


@dataclass
class PerfilNoCentro:
    andamento: a.PerfilNoAndamento
    listas: list
    matricula_fora: bool

    @property
    def nome(self):
        return self.andamento.nome

    @property
    def fases(self):
        """As fases por lista, para o cabeçalho da tabela."""
        return [(chave, c.NOMES[chave]) for chave in c.POR_LISTA]


@dataclass
class Destaque:
    item: ItemDeProvidencia
    porque: str
    destrava: list = field(default_factory=list)


@dataclass
class Centro:
    fases: list
    perfis: list
    itens: list
    onde: str
    onde_detalhe: str
    papel: str
    ve_a_matriz: bool
    destaque: Destaque | None = None
    sem_destaque: str = ""
    #: As Retificações em curso em que o próximo ato é da pessoa (104, FR-2819).
    retificacoes_suas: list = field(default_factory=list)
    #: O bloco "Disponibilizar ao setor" da fase Conclusão (153); `None` sem pessoa apta.
    passagem: object = None

    @property
    def grupos(self):
        por_chave = {fase.chave: fase for fase in self.fases}
        return [(rotulo, [por_chave[ch] for ch in chaves]) for rotulo, chaves in c.GRUPOS]

    @property
    def em_curso(self):
        return [fase for fase in self.fases if fase.em_curso]

    @property
    def suas(self):
        return [i for i in self.itens if i.p.grupo == p.SUA]

    @property
    def demais_suas(self):
        """As suas, sem a destacada — o "Também sua"."""
        destacada = self.destaque.item if self.destaque else None
        return [i for i in self.suas if i is not destacada]

    @property
    def de_outros(self):
        return [i for i in self.itens if i.p.grupo == p.DE_OUTRO]

    @property
    def aguardando(self):
        return [i for i in self.itens if i.p.situacao == a.AGUARDA]

    @property
    def impedidas(self):
        return [i for i in self.itens if i.p.situacao == a.IMPEDIDO]

    @property
    def total(self):
        return len(self.itens)

    @property
    def tem_algo(self):
        """Há algo em aberto, de alguém: uma providência, ou uma Retificação que prossegue."""
        return any(fase.em_aberto for fase in self.fases)

    @property
    def tem_sua(self):
        """A pessoa tem o que fazer: uma providência sua, ou o próximo ato de uma Retificação.

        Sem a Retificação, o cartão dizia "Nenhuma ação é sua agora" ao lado de "Retificação em
        curso — aguarda você" — a contradição que a `104` tirou do detalhe (FR-2820).
        """
        return bool(self.suas or self.retificacoes_suas)


# ---------------------------------------------------------------------------------------------
# A composição
# ---------------------------------------------------------------------------------------------


def _passo(ponto):
    """`(nome simples, termo, conceito)` de um ponto. A Etapa usa o nome que tem no Edital."""
    dados = c.CONCEITOS.get(ponto.tipo) or c.CONCEITOS[a.ETAPA]
    if ponto.tipo == a.ETAPA:
        return ponto.titulo, dados["termo"], dados
    return dados["simples"], dados["termo"], dados


def _roteiro(pontos, listas):
    roteiro = []
    for ponto in pontos:
        celulas = [ponto.celula(lista_id) for lista_id, _ in listas]
        validas = [x for x in celulas if x is not None and x.situacao != a.NAO_SE_APLICA]
        simples, termo, dados = _passo(ponto)
        roteiro.append(
            PassoDoRoteiro(
                simples=simples,
                termo=termo,
                curta=dados["curta"],
                porque=dados["porque"],
                ao_confirmar=dados["ao_confirmar"],
                andamento=agregar(celulas) or c.NAO_SE_APLICA,
                feitas=sum(1 for x in validas if x.situacao == a.FEITO),
                total=len(validas),
                unico=ponto.tipo in (a.SEMENTE, a.ETAPA),
                tem_acao=any(x.situacao in a.A_PRATICAR for x in validas),
                razao=next((x.razao for x in validas if x.situacao == a.DEPOIS and x.razao), ""),
            )
        )
    return roteiro


def _lista_no_centro(perfil, lista_id, rotulo, curto, andamentos):
    """A linha de "Onde cada lista está": o andamento por fase e o que há agora nela."""
    vistas, atos, espera = set(), [], None
    for ponto in perfil.pontos:
        celula = ponto.celula(lista_id)
        if celula is None:
            continue
        fase = fase_do_ponto(ponto)
        if celula.situacao in a.A_PRATICAR and fase not in vistas:
            vistas.add(fase)
            atos.append((c.NOMES[fase], celula, c.ato_simples(celula.natureza, celula.ato)))
        elif espera is None and celula.situacao in (a.AGUARDA, a.IMPEDIDO):
            espera = celula
    concluida = all(x in (c.CONCLUIDA, c.NAO_SE_APLICA, None) for _, x in andamentos)
    fases = [FaseNaLista(chave, x) for chave, x in andamentos]
    return ListaNoCentro(rotulo, curto, fases, concluida, atos, espera)


def paralela(perfis):
    """A frase da Avaliação que o sorteio não lê, ou "" (D-008, R-005).

    Há paralela quando nenhum marco lê a Etapa: todos os marcos de todos os Perfis classificam por
    sorteio, e nenhum declara Etapa de habilitação. Basta um marco por pontuação — que lê as Etapas
    que enumera e as do desempate —, ou uma habilitação, para que a avaliação segure a
    classificação. A Etapa governada não conta: ela é de Vagas.
    """
    marcos = [ponto.marco or {} for perfil in perfis for ponto in perfil.pontos if ponto.marco]
    if not marcos or not all(a.por_sorteio(marco) for marco in marcos):
        return ""
    if any((marco.get("drawMethod") or {}).get("qualifyingStageId") for marco in marcos):
        return ""
    avaliadas = [
        ponto
        for perfil in perfis
        for ponto in perfil.pontos
        if ponto.tipo == a.ETAPA and fase_do_ponto(ponto) == c.AVALIACAO
    ]
    return c.PARALELA if avaliadas else ""


def _fase_publicacao(edital, documentos, em_curso):
    retificacoes = sum(1 for d in documentos if d.get("retificacao_id"))
    resumo = "Publicado"
    if edital.status == "ENCERRADO":
        resumo = "Publicado e encerrado"
    if retificacoes:
        resumo += f" · {retificacoes} {'Retificação' if retificacoes == 1 else 'Retificações'}"
    if em_curso:
        # A Retificação em curso pode mudar qualquer fase: a do Edital deixa de estar concluída.
        return Macrofase(c.PUBLICACAO, c.EM_CURSO, resumo, c.RETIFICACAO_EM_CURSO)
    return Macrofase(c.PUBLICACAO, c.CONCLUIDA, resumo)


def _fase_inscricoes(inscricoes):
    """O andamento sai do estado do período; o resumo é a linha da `127` (FR-4101), e não outra.

    O cancelado terminou sem chegar ao fim: concluído, e a linha já diz que foi cancelado.
    """
    from processo_seletivo.inscricoes.domain import periodo

    andamento = {periodo.ENCERRADO: c.CONCLUIDA, periodo.ABERTO: c.EM_CURSO}.get(
        inscricoes.get("estado"), c.NAO_INICIADA
    )
    if inscricoes.get("cancelado"):
        andamento = c.CONCLUIDA
    return Macrofase(c.INSCRICOES, andamento, a.linha_das_inscricoes(inscricoes))


def _fase_conclusao(edital, perfis_no_centro):
    nota = c.MATRICULA_FORA if any(pf.matricula_fora for pf in perfis_no_centro) else ""
    if edital.status == "ENCERRADO":
        return Macrofase(c.CONCLUSAO, c.CONCLUIDA, "Edital encerrado", nota)
    listas = [lista for pf in perfis_no_centro for lista in pf.listas]
    if listas and all(lista.concluida for lista in listas):
        # **Nunca uma ação daqui** (FR-4714): se o Edital pode ser encerrado, quem decide são as
        # pendências do encerramento (prazos, recursos, Retificações), que a tela do ato confere.
        return Macrofase(c.CONCLUSAO, c.EM_CURSO, c.CONCLUSAO_PRONTA, nota)
    return Macrofase(c.CONCLUSAO, c.NAO_INICIADA, c.CONCLUSAO_DEPOIS, nota)


def _resumo_da_fase(chave, detalhe, por_lista, andamento_perfis):
    if not detalhe:
        return "Não há neste Edital"
    aplicaveis = [x for x in por_lista if x not in (None, c.NAO_SE_APLICA)]
    feitas = sum(1 for x in aplicaveis if x == c.CONCLUIDA)
    if chave == c.RESULTADO and len(andamento_perfis) == 1:
        # A natureza do que o público lê é a que o resumo do Perfil da `127` já diz — a mesma
        # leitura, e não uma segunda. A `135` a torna dado estruturado; o texto continua o dela.
        palavras = a._resultado_em_palavras(andamento_perfis[0])
        if palavras:
            return palavras[:1].upper() + palavras[1:]
    if len(aplicaveis) > 1 and 0 < feitas < len(aplicaveis):
        return f"{feitas} de {len(aplicaveis)} listas concluídas"
    return ""


def compor(edital, andamento, *, documentos=(), em_curso=(), alcance=None):
    """O Centro de um Edital, a partir do andamento já derivado. Puro (R-001)."""
    perfis = list(andamento.perfis)
    detalhes = {chave: [] for chave in c.POR_LISTA}
    perfis_no_centro = []
    for perfil in perfis:
        pontos = {chave: [] for chave in c.POR_LISTA}
        for ponto in perfil.pontos:
            pontos[fase_do_ponto(ponto)].append(ponto)
        por_fase_e_lista = {chave: [] for chave in c.POR_LISTA}
        listas = []
        # O rótulo curto é o do nível 1 (D-020 da `127`): "Ampla concorrência" e o código de cada
        # Modalidade, ou o nome dela quando não tem código.
        curtos = a._rotulos_curtos(perfil.perfil)
        for lista_id, rotulo in perfil.listas:
            curto = curtos.get(a._chave(lista_id), rotulo)
            andamentos = []
            for chave in c.POR_LISTA:
                celulas = [ponto.celula(lista_id) for ponto in pontos[chave]]
                andamento_da_lista = agregar(celulas)
                andamentos.append((chave, andamento_da_lista))
                por_fase_e_lista[chave].append(
                    ListaNaFase(
                        curto,
                        andamento_da_lista,
                        [
                            CelulaNaFase(_passo(ponto)[0], ponto.celula(lista_id))
                            for ponto in pontos[chave]
                            if ponto.celula(lista_id) is not None
                        ],
                    )
                )
            listas.append(_lista_no_centro(perfil, lista_id, rotulo, curto, andamentos))
        for chave in c.POR_LISTA:
            if pontos[chave]:
                detalhes[chave].append(
                    FaseNoPerfil(
                        perfil, _roteiro(pontos[chave], perfil.listas), por_fase_e_lista[chave]
                    )
                )
        perfis_no_centro.append(PerfilNoCentro(perfil, listas, a.matricula_fora(perfil)))

    fases = []
    for chave in c.CHAVES:
        if chave == c.PUBLICACAO:
            fases.append(_fase_publicacao(edital, documentos, em_curso))
        elif chave == c.INSCRICOES:
            fases.append(_fase_inscricoes(andamento.inscricoes))
        elif chave == c.CONCLUSAO:
            fases.append(_fase_conclusao(edital, perfis_no_centro))
        else:
            detalhe = detalhes[chave]
            por_lista = [lst.andamento for fp in detalhe for lst in fp.listas]
            fases.append(
                Macrofase(
                    chave,
                    juntar(por_lista) or c.NAO_SE_APLICA,
                    _resumo_da_fase(chave, detalhe, por_lista, [fp.perfil for fp in detalhe]),
                    perfis=detalhe,
                )
            )
    por_chave = {fase.chave: fase for fase in fases}
    por_chave[c.AVALIACAO].paralela = paralela(perfis)
    # A parada pelo desfecho do Edital não prossegue: é dita, mas não é algo em aberto.
    por_chave[c.PUBLICACAO].retificacoes = [r for r in em_curso or () if not r.get("parada")]

    # A segunda leitura: as providências do nível 1 da `127`, na ordem dele, cada uma na sua fase.
    governadas = etapas_governadas(perfis)
    nivel = andamento.nivel_1
    itens = [_item(prov, governadas, por_chave) for prov in (nivel.itens if nivel else [])]
    for fase in fases:
        fase.providencias = [i for i in itens if i.fase_chave == fase.chave]

    suas = [i for i in itens if i.p.grupo == p.SUA]
    retificacoes_suas = por_chave[c.PUBLICACAO].retificacoes_suas
    destacado, sem_destaque = destaque(suas, por_chave, retificacoes=len(retificacoes_suas))
    onde, onde_detalhe = onde_estamos(fases, itens)
    return Centro(
        fases=fases,
        perfis=perfis_no_centro,
        itens=itens,
        onde=onde,
        onde_detalhe=onde_detalhe,
        papel=papel(alcance),
        ve_a_matriz=bool(andamento.ve_a_matriz),
        destaque=destacado,
        sem_destaque=sem_destaque,
        retificacoes_suas=retificacoes_suas,
        passagem=bloco_da_passagem(getattr(andamento, "formalizacao", None), itens),
    )


def _item(providencia, governadas, por_chave):
    chave = fase_da_providencia(providencia, governadas)
    dados = c.conceito(providencia.natureza)
    titulo = c.ato_simples(providencia.natureza, providencia.ato)
    no_gps = providencia.ato if titulo != providencia.ato else ""
    return ItemDeProvidencia(providencia, chave, dados, titulo, no_gps, por_chave[chave].paralela)


# ---------------------------------------------------------------------------------------------
# O bloco "Disponibilizar ao setor" da fase Conclusão (153, FR-6118 a FR-6121)
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class LinhaDaPassagem:
    rotulo: str
    texto: str
    feito: bool
    #: A providência da linha, quando ela está em aberto: o link é dela, e só de quem a pratica.
    item: ItemDeProvidencia | None = None


@dataclass(frozen=True)
class BlocoDaPassagem:
    aptas: int
    linhas: tuple
    #: A frase de quando nada falta (FR-6121); vazia enquanto há pessoa pendente.
    conclusao: str = ""

    @property
    def frase_das_aptas(self):
        return f"{_n(self.aptas, 'pessoa apta', 'pessoas aptas')} para formalização"

    @property
    def limite(self):
        return c.LIMITE_DA_PASSAGEM


def _data(instante):
    return a._data(instante)[:10] if instante else ""


def bloco_da_passagem(passagem, itens):
    """As linhas do bloco, a partir da `Passagem` e das providências que já viraram itens.

    **As linhas não decidem nada.** O link de cada uma é o da providência da mesma causa, que o
    andamento já deu só a quem pratica o ato (FR-6119). O bloco só diz o estado de cada passo.
    """
    from processo_seletivo.formalizacao.application import passagem as pa

    if passagem is None:
        return None
    da_causa = {
        i.p.chave[1]: i for i in itens if i.p.natureza == a.FORMALIZACAO and len(i.p.chave) > 1
    }
    if passagem.definicao_vazia:
        return BlocoDaPassagem(
            aptas=passagem.aptas,
            linhas=(),
            conclusao=(
                "Nenhum documento vai ao setor neste Edital, por decisão de "
                f"{_data(passagem.definida_em)}."
            ),
        )
    if not passagem.definida:
        documentos = LinhaDaPassagem(
            "Documentos que o setor recebe", "não definidos", False, da_causa.get(pa.SEM_DEFINICAO)
        )
        quem = LinhaDaPassagem("Quem recebe", "ainda depende da definição", False)
    else:
        documentos = LinhaDaPassagem(
            "Documentos que o setor recebe", f"definidos em {_data(passagem.definida_em)}", True
        )
        sem_quem = passagem.pendentes[pa.SEM_QUEM_RECEBA]
        designadas = _n(passagem.designadas, "pessoa designada", "pessoas designadas")
        if not passagem.designadas:
            texto = "ninguém designado"
        elif sem_quem:
            texto = (
                f"{designadas}; {_n(sem_quem, 'pessoa apta', 'pessoas aptas')} de "
                f"{'Perfil' if sem_quem == 1 else 'Perfis'} sem designação"
            )
        else:
            texto = designadas
        quem = LinhaDaPassagem("Quem recebe", texto, not sem_quem, da_causa.get(pa.SEM_QUEM_RECEBA))
    com_documento = passagem.aptas - passagem.sem_documento
    texto = f"{passagem.disponibilizadas} de {com_documento}"
    if passagem.ultimo_pacote_em:
        texto += f"; o último pacote em {_data(passagem.ultimo_pacote_em)}"
    disponibilizadas = LinhaDaPassagem(
        "Pessoas disponibilizadas",
        texto,
        passagem.completa,
        da_causa.get(pa.A_EXPORTAR),
    )
    conclusao = ""
    if passagem.completa and not com_documento:
        conclusao = "Nenhuma pessoa apta tem documento a disponibilizar ao setor."
    elif passagem.completa:
        conclusao = (
            f"Documentos de todas as {com_documento} pessoas aptas disponibilizados ao setor"
            if com_documento > 1
            else "Documentos da pessoa apta disponibilizados ao setor"
        )
        if passagem.ultimo_pacote_em:
            conclusao += f"; o último pacote em {_data(passagem.ultimo_pacote_em)}"
        conclusao += "."
        if passagem.sem_documento:
            conclusao += (
                f" {_n(passagem.sem_documento, 'pessoa apta não tem', 'pessoas aptas não têm')} "
                "documento a disponibilizar."
            )
    return BlocoDaPassagem(
        aptas=passagem.aptas, linhas=(documentos, quem, disponibilizadas), conclusao=conclusao
    )


# ---------------------------------------------------------------------------------------------
# O destaque (FR-4722 a FR-4725, D-005)
# ---------------------------------------------------------------------------------------------


def destaque(suas, por_chave, *, retificacoes=0):
    """`(Destaque | None, frase quando não há destaque)`. **O critério, dito na tela.**

    1. Uma ação sua só → é ela, porque não há outra.
    2. Várias, e exatamente uma não é paralela e destrava passos seguintes da mesma fase → é essa,
       e a tela diz quais passos esperam por ela. É dependência que a derivação já conhece, e não
       prioridade inventada.
    3. Qualquer outro caso → nenhum destaque. Toda providência *Pendente* já pode ser praticada — o
       que depende de outro ato é *Depois*, e nem vira providência —, e o GPS não tem como saber
       qual importa mais.

    `retificacoes` são os atos da pessoa em Retificações em curso (104, FR-2819). Contam como ações
    suas, e nenhuma é paralela: uma Retificação pode mudar datas, vagas ou regras de qualquer fase,
    e o "corre em paralelo e não segura nada" da regra 2 seria falso. Elas mesmas não se destacam —
    têm a linha da `104` no cartão.

    **Provisório.** O critério é a quarta decisão do estudo, pendente e bloqueante para a liberação
    geral. A regra 1 só fica segura com a `135`: no C08 ela destaca a ordem de uma lista sem
    inscritos, e é a providência que precisa dizê-lo.
    """
    if not suas:
        return None, ""
    quantas = len(suas) + retificacoes
    if quantas == 1:
        item = suas[0]
        return Destaque(item, c.PORQUE_UNICA, destrava(item, por_chave)), ""
    principais = [i for i in suas if not i.paralela]
    if not retificacoes and len(principais) == 1:
        item = principais[0]
        passos = destrava(item, por_chave)
        if passos:
            porque = c.PORQUE_DESTRAVA_UMA if len(suas) == 2 else c.PORQUE_DESTRAVA_VARIAS
            return Destaque(item, porque, passos), ""
    return None, c.SEM_DESTAQUE.format(n=quantas)


def destrava(item, por_chave):
    """Os passos da mesma fase, do mesmo Perfil, depois do primeiro com ação e ainda não começados.

    A providência sem Perfil (a da Etapa, que é do Edital) olha todos os Perfis da fase (R-006).
    """
    fase = por_chave.get(item.fase_chave)
    if fase is None:
        return []
    perfil_id = str(item.p.perfil_id or "")
    nomes = []
    for fase_no_perfil in fase.perfis:
        if perfil_id and str(fase_no_perfil.perfil.perfil.get("id")) != perfil_id:
            continue
        visto_o_atual = False
        for passo in fase_no_perfil.roteiro:
            if passo.tem_acao:
                visto_o_atual = True
                continue
            if visto_o_atual and passo.andamento == c.NAO_INICIADA and passo.simples not in nomes:
                nomes.append(passo.simples)
    return nomes


# ---------------------------------------------------------------------------------------------
# "Onde estamos" e o papel (FR-4718 a FR-4721)
# ---------------------------------------------------------------------------------------------


def _lista_de(nomes):
    return a._lista_de_nomes(nomes)


def _n(quantos, singular, plural):
    return f"{quantos} {singular if quantos == 1 else plural}"


def onde_estamos(fases, itens):
    """`(frase, detalhe)`. Nomeia as fases com algo em aberto **agora**, e não "N frentes".

    A primeira versão do protótipo contava frentes ao mesmo tempo, e contava como frente a fase em
    curso sem nada a fazer. Com muitas fases parcialmente ativas, o número deixava de dizer alguma
    coisa. A frase lista as fases que têm providência, e a segunda diz de quem é.
    """
    abertas = [fase for fase in fases if fase.em_aberto]
    if not abertas:
        conclusao = next((f for f in fases if f.chave == c.CONCLUSAO), None)
        if conclusao is not None and conclusao.andamento == c.CONCLUIDA:
            return "Seleção concluída. Nada em aberto.", ""
        em_curso = [c.NA_FRASE[fase.chave] for fase in fases if fase.em_curso]
        if em_curso:
            return f"Nada em aberto agora. Em curso: {_lista_de(em_curso)}.", ""
        return "Nada em aberto agora.", ""
    frase = f"Há algo em aberto em {_lista_de([c.NA_FRASE[fase.chave] for fase in abertas])}."
    # As Retificações que prosseguem contam com as providências: a que espera a pessoa é dela, e a
    # que espera outro papel é dele (104, FR-2819, FR-2820).
    suas = sum(fase.quantas_suas for fase in fases)
    de_outros = sum(fase.quantas_de_outros for fase in fases)
    aguardando = [i for i in itens if i.p.situacao == a.AGUARDA]
    impedidas = sum(1 for i in itens if i.p.situacao == a.IMPEDIDO)
    partes = []
    if suas:
        partes.append(_n(suas, "ação é sua", "ações são suas"))
    if de_outros:
        partes.append(_n(de_outros, "está com outro papel", "estão com outros papéis"))
    if aguardando:
        datas = [i.p.ate for i in aguardando if i.p.ate]
        ate = f" (a primeira até {a._data(min(datas))[:5]})" if datas else ""
        partes.append(_n(len(aguardando), "aguarda", "aguardam") + f" prazo ou resposta{ate}")
    if impedidas:
        partes.append(_n(impedidas, "está impedida", "estão impedidas"))
    detalhe = _lista_de(partes) + "." if partes else ""
    return frase, detalhe[:1].upper() + detalhe[1:]


def papel(alcance):
    """O papel da pessoa no Edital, em palavras, a partir do alcance da `127` (FR-4721)."""
    if alcance is None:
        return ""
    partes = []
    if alcance.conduz:
        partes.append("conduz a seleção")
    elif alcance.consulta:
        partes.append("acompanha a seleção")
    if alcance.publica:
        partes.append("publica resultados")
    if alcance.julga:
        partes.append("julga recursos")
    if alcance.retifica:
        partes.append("propõe Retificações")
    if not partes:
        return "Você acompanha este Edital sem ato a praticar nele."
    texto = "Você " + _lista_de(partes)
    if not alcance.ativo:
        texto += " — mas o Processo está encerrado, e nenhum ato é seu"
    return texto + "."


# ---------------------------------------------------------------------------------------------
# A fase consultada (FR-4730, R-007)
# ---------------------------------------------------------------------------------------------


def fase_consultada(centro, pedida=None):
    """A fase aberta no detalhe. Regra de apresentação, fixa.

    A pedida, se existe; senão, a da ação em destaque; senão, a primeira com ação **sua** (a
    paralela por último); senão, a primeira com algo em aberto; senão, a primeira em curso; senão, a
    última concluída; senão, a primeira.
    """
    por_chave = {fase.chave: fase for fase in centro.fases}
    if pedida in por_chave:
        return por_chave[pedida]
    if centro.destaque is not None:
        return por_chave[centro.destaque.item.fase_chave]
    for paralela_por_ultimo in (False, True):
        for fase in centro.fases:
            if bool(fase.paralela) == paralela_por_ultimo and fase.quantas_suas:
                return fase
    for fase in centro.fases:
        if fase.em_aberto:
            return fase
    if centro.em_curso:
        return centro.em_curso[0]
    concluidas = [fase for fase in centro.fases if fase.andamento == c.CONCLUIDA]
    return concluidas[-1] if concluidas else centro.fases[0]
