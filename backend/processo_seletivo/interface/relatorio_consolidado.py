"""O relatório consolidado da unidade: um conjunto de Editais, somado (100).

**Uma soma, e não uma segunda derivação** (D-001). Cada número de resultado, apuração, convocação,
recurso, pendência e espécie é o da derivação do relatório do Edital (`099`), lida Edital a Edital
por `fatos_do_edital`. Este módulo escolhe o conjunto, abre a leitura num instante só e soma — e a
soma (`consolidar`) não toca o banco, para que se teste com fatos sintéticos.

**O período escolhe Editais; os dados são do instante da emissão** (D-003). Ninguém reconstitui
o estado de 30/06: quem precisa do retrato de 30/06 emite em 30/06, e a emissão registrada é o
retrato.

**Um universo para todo número** (D-005). Os Editais do conjunto que não foram cancelados. O
cancelado conta como Edital, aparece na relação e na situação — e em mais nada.

**O consolidado nunca mostra o que o relatório individual esconde** (FR-2592, D-006). O Edital
cujos totais não públicos o relatório dele omite — menos de cinco inscrições enviadas — não
contribui com fato não público a número nenhum daqui. Somá-lo e esconder a linha não bastaria:
duas emissões, com e sem ele, devolveriam o número por diferença.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, time

from django.utils import timezone

from processo_seletivo.interface import relatorio_do_edital as rel
from processo_seletivo.interface import visao_geral
from processo_seletivo.interface.relatorio_do_edital import (
    ZONA,
    Ausencia,
    Indicador,
    Numero,
    _plural,
    data_curta,
)
from processo_seletivo.interface.templatetags.interface_extras import SITUACOES
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.shared.api.problems import DomainError

OPERACAO_DA_EMISSAO = "EMITIR_RELATORIO_CONSOLIDADO"

#: Medido na tarefa de orçamento (R-006): a emissão é síncrona, e o limite protege o tempo de
#: resposta da gestão. É dito a quem pede mais, e não aplicado em silêncio.
LIMITE_DE_EDITAIS = 60

PUBLICACAO = "publicacao"
NUMERO = "numero"
MANUAL = "manual"
CRITERIOS = (PUBLICACAO, NUMERO, MANUAL)
ANO, PRIMEIRO_SEMESTRE, SEGUNDO_SEMESTRE, DATAS = "ano", "s1", "s2", "datas"
ATALHOS = (ANO, PRIMEIRO_SEMESTRE, SEGUNDO_SEMESTRE, DATAS)

SEGUE, SEGUEM = "Edital segue", "Editais seguem"
AGUARDA, AGUARDAM = "aguarda", "aguardam"

DATA_DOS_DADOS = (
    "O período escolheu os Editais. A situação de cada um é a de {instante}, e não a do fim do "
    "período."
)
TITULO_DA_SERIE = "Inscrições enviadas, por mês do envio"
NOTA_DA_SERIE = (
    "Os meses vão do primeiro ao último envio dos Editais do conjunto e podem passar do período "
    "que os escolheu."
)
NOTA_DA_TRILHA = (
    "A contagem cobre os atos registrados na trilha de auditoria do GPS, e não todo acontecimento."
)
MATRICULA = (
    "O GPS não registra matrículas.",
    "Este relatório mostra convocações aceitas, e não matrículas efetivadas. A confirmação vem do "
    "registro acadêmico.",
)

MOTIVOS_DE_FORA = {
    Edital.Status.EM_ELABORACAO: "em elaboração",
    Edital.Status.EM_REVISAO: "em revisão",
    Edital.Status.HOMOLOGADO: "homologado e ainda não publicado",
}
CANCELADO_ANTES = "cancelado antes da publicação"


# --- O conjunto ---------------------------------------------------------------------------------


@dataclass(frozen=True)
class Criterio:
    modo: str
    ano: int
    atalho: str = ANO
    inicio: date | None = None
    fim: date | None = None
    busca: str = ""

    @property
    def rotulo(self):
        """O critério por extenso, como a ficha e o anexo o dizem (FR-2561)."""
        if self.modo == NUMERO:
            return f"Editais com número de {self.ano}"
        if self.modo == MANUAL:
            return "Editais escolhidos um a um"
        return (
            f"Editais com primeira publicação entre {self.inicio.strftime('%d/%m/%Y')} e "
            f"{self.fim.strftime('%d/%m/%Y')}"
        )

    @property
    def periodo_curto(self):
        """O período na faixa de cada página."""
        if self.modo == NUMERO:
            return f"Editais de número {self.ano}"
        if self.modo == MANUAL:
            return "escolha manual"
        if self.atalho == PRIMEIRO_SEMESTRE:
            return f"1º semestre de {self.ano}"
        if self.atalho == SEGUNDO_SEMESTRE:
            return f"2º semestre de {self.ano}"
        if self.atalho == ANO:
            return f"publicados em {self.ano}"
        return f"publicados de {self.inicio.strftime('%d/%m/%Y')} a {self.fim.strftime('%d/%m/%Y')}"

    def parametros(self):
        """O critério como parâmetros do formulário — o mesmo endereço reproduz a escolha."""
        saida = {"criterio": self.modo, "ano": str(self.ano)}
        if self.modo == PUBLICACAO:
            saida["atalho"] = self.atalho
            if self.atalho == DATAS:
                saida["inicio"] = self.inicio.isoformat()
                saida["fim"] = self.fim.isoformat()
        if self.modo == MANUAL and self.busca:
            saida["busca"] = self.busca
        return saida


def _data(valor):
    try:
        return date.fromisoformat((valor or "").strip())
    except ValueError:
        return None


def criterio_de(parametros, *, hoje=None):
    """O que a pessoa pediu, saneado — valor fora do conjunto aceito cai no padrão (FR-2557)."""
    hoje = hoje or timezone.localtime().date()
    modo = (parametros.get("criterio") or "").strip()
    modo = modo if modo in CRITERIOS else PUBLICACAO
    try:
        ano = int((parametros.get("ano") or "").strip())
    except ValueError:
        ano = hoje.year
    if not 2000 <= ano <= 9999:
        ano = hoje.year
    busca = (parametros.get("busca") or "").strip()[:100]
    if modo != PUBLICACAO:
        return Criterio(modo=modo, ano=ano, busca=busca if modo == MANUAL else "")
    atalho = (parametros.get("atalho") or "").strip()
    atalho = atalho if atalho in ATALHOS else ANO
    if atalho == DATAS:
        inicio, fim = _data(parametros.get("inicio")), _data(parametros.get("fim"))
        if inicio is None or fim is None:
            atalho = ANO
        elif inicio > fim:
            raise DomainError(
                "periodo_invertido", "A data inicial é posterior à final.", 422, campo="inicio"
            )
        else:
            return Criterio(modo=modo, ano=ano, atalho=atalho, inicio=inicio, fim=fim)
    inicio, fim = {
        ANO: (date(ano, 1, 1), date(ano, 12, 31)),
        PRIMEIRO_SEMESTRE: (date(ano, 1, 1), date(ano, 6, 30)),
        SEGUNDO_SEMESTRE: (date(ano, 7, 1), date(ano, 12, 31)),
    }[atalho]
    return Criterio(modo=modo, ano=ano, atalho=atalho, inicio=inicio, fim=fim)


@dataclass(frozen=True)
class Conjunto:
    criterio: Criterio
    #: Os Editais do escopo que o critério alcança, elegíveis ou não, com a primeira publicação.
    alcancados: tuple
    incluidos: tuple
    #: Elegíveis do critério que a pessoa desmarcou.
    retirados: tuple
    #: `(Edital, motivo)` dos que o critério alcança e não podem entrar.
    fora: tuple
    escolha: bool
    primeiras: dict = field(default_factory=dict)

    @property
    def vazio(self):
        return not self.incluidos

    @property
    def grande_demais(self):
        return len(self.incluidos) > LIMITE_DE_EDITAIS

    def primeira(self, edital):
        return self.primeiras.get(edital.pk)

    def exigir_emissivel(self):
        """As recusas do contrato: conjunto vazio, e acima do limite (FR-2562, FR-2563)."""
        if self.vazio:
            raise DomainError(
                "conjunto_vazio",
                "Nenhum Edital publicado entra neste conjunto. Escolha outro período ou marque "
                "Editais.",
                422,
            )
        if self.grande_demais:
            raise DomainError(
                "conjunto_grande_demais",
                f"O relatório reúne até {LIMITE_DE_EDITAIS} Editais por emissão, e este conjunto "
                f"tem {len(self.incluidos)}. Reduza o período ou desmarque Editais.",
                422,
            )


def _chave_do_edital(edital, primeiras):
    primeira = primeiras.get(edital.pk)
    numero = edital.number
    # O número é texto (`9` depois de `10` na ordem de texto); na relação, o que tem dígitos
    # ordena como número.
    return (primeira or datetime.max.replace(tzinfo=ZONA), edital.year, numero.zfill(10), numero)


def _motivo_de_fora(edital, primeiras):
    if edital.status in rel.ESTADOS_COM_RELATORIO and edital.pk in primeiras:
        return None
    if edital.status == Edital.Status.CANCELADO:
        return CANCELADO_ANTES
    return MOTIVOS_DE_FORA.get(edital.status, SITUACOES.get(edital.status, edital.status))


def conjunto_de(ator, parametros, *, hoje=None):
    """Os Editais do escopo do ator que o critério e a escolha definem (FR-2555 a FR-2561).

    Toda consulta filtra pelo escopo do ator: identificador alheio, ou inexistente, enviado no
    formulário simplesmente não volta — sem distinção entre os dois.
    """
    criterio = criterio_de(parametros, hoje=hoje)
    escopo = ator.institution_scope
    editais = list(Edital.objects.filter(institution_scope=escopo).select_related("processo"))
    # A primeira publicação de cada Edital do escopo, numa consulta (R-003).
    primeiras = dict(
        Publicacao.objects.filter(
            edital__institution_scope=escopo, publication_order=1
        ).values_list("edital_id", "published_at")
    )
    if criterio.modo == PUBLICACAO:
        inicio = datetime.combine(criterio.inicio, time.min, tzinfo=ZONA)
        fim = datetime.combine(criterio.fim, time.max, tzinfo=ZONA)
        alcancados = [e for e in editais if e.pk in primeiras and inicio <= primeiras[e.pk] <= fim]
    elif criterio.modo == NUMERO:
        alcancados = [e for e in editais if e.year == criterio.ano]
    else:
        busca = criterio.busca.lower()
        alcancados = [
            e
            for e in editais
            if not busca
            or busca in e.number.lower()
            or busca in (e.title or "").lower()
            or busca in e.processo.title.lower()
            or busca in e.processo.institutional_code.lower()
        ]
    alcancados.sort(key=lambda e: _chave_do_edital(e, primeiras))
    elegiveis = [e for e in alcancados if _motivo_de_fora(e, primeiras) is None]
    fora = tuple(
        (e, motivo) for e in alcancados if (motivo := _motivo_de_fora(e, primeiras)) is not None
    )

    escolha = criterio.modo == MANUAL or (parametros.get("escolha") or "") == "1"
    marcados = {str(v) for v in _lista(parametros, "edital")}
    if criterio.modo == MANUAL:
        # Na escolha manual, os marcados valem mesmo fora da busca da vez: buscar outro nome não
        # desmarca o que já foi escolhido.
        incluidos = [
            e for e in editais if str(e.pk) in marcados and _motivo_de_fora(e, primeiras) is None
        ]
        incluidos.sort(key=lambda e: _chave_do_edital(e, primeiras))
        retirados = []
    elif escolha:
        incluidos = [e for e in elegiveis if str(e.pk) in marcados]
        retirados = [e for e in elegiveis if str(e.pk) not in marcados]
    else:
        incluidos, retirados = list(elegiveis), []
    return Conjunto(
        criterio=criterio,
        alcancados=tuple(alcancados),
        incluidos=tuple(incluidos),
        retirados=tuple(retirados),
        fora=fora,
        escolha=escolha,
        primeiras=primeiras,
    )


def _lista(parametros, chave):
    if hasattr(parametros, "getlist"):
        return parametros.getlist(chave)
    valor = parametros.get(chave)
    return valor if isinstance(valor, list | tuple) else ([valor] if valor else [])


# --- A leitura ----------------------------------------------------------------------------------


def montar(conjunto, *, agora, unidade):
    """Os fatos de cada Edital e a soma. Supõe a transação de `leitura_consistente` aberta."""
    fatos = [rel.fatos_do_edital(edital, agora=agora) for edital in conjunto.incluidos]
    return consolidar(fatos, conjunto, agora=agora, unidade=unidade)


def ler(conjunto, *, agora, unidade):
    """O consolidado no instante `agora`, numa leitura só, para o conjunto inteiro (FR-2564)."""
    with rel.leitura_consistente():
        return montar(conjunto, agora=agora, unidade=unidade)


def proxima_emissao(unidade):
    """O número da emissão seguinte da unidade, contado na trilha (FR-2567, R-005)."""
    from processo_seletivo.auditoria.models import RegistroAuditoria

    return (
        RegistroAuditoria.objects.filter(
            aggregate_type="Unidade", aggregate_id=unidade.pk, operation=OPERACAO_DA_EMISSAO
        ).count()
        + 1
    )


# --- A soma -------------------------------------------------------------------------------------


@dataclass(frozen=True)
class LinhaDoEdital:
    edital: Edital
    primeira: datetime | None
    perfis: int
    vagas: int
    inscricoes: Numero
    por_vaga: Numero


@dataclass(frozen=True)
class LinhaDaRelacao:
    edital: Edital
    primeira: datetime | None
    situacao: str
    especie: str


@dataclass(frozen=True)
class ProvidenciasDoEdital:
    edital: Edital
    situacao: str
    itens: tuple
    omitido: bool


@dataclass
class Consolidado:
    referencia: datetime
    conjunto: Conjunto
    unidade: object
    editais: int
    situacoes: list
    por_especie: Counter
    cancelados: int
    universo: int
    fora_dos_nao_publicos: int
    vagas: int
    vagas_reservadas: int
    perfis: int
    perfis_com_vaga: int
    perfis_so_reserva: int
    inscricoes: Numero
    numerador: int
    razao: Numero
    periodos_abertos: int
    envios_por_mes: list
    linhas: list
    perfis_com_marca: list
    retificacoes: int
    editais_retificados: int
    prorrogados: int
    recursos: rel.Recursos | None
    marcos_declarados: int
    marcos_definitivos: int
    editais_com_resultado_previsto: int
    editais_definitivos: int
    vagas_habilitadas: int
    vagas_apuradas: int
    vagas_desatualizadas: int
    vagas_nao_apuradas: int
    convocacoes: dict | None
    pendencias_por_tipo: list
    providencias_por_edital: list
    encerrados_com_pendencia: int
    com_pendencia: int
    posteriores_por_edital: list
    relacao: list
    situacao_no_gps: str = ""
    providencias: str = ""
    #: O endereço público da página de cada seleção, que a view monta pela requisição (R-005 da
    #: `099`): a derivação não conhece o host.
    enderecos: dict = field(default_factory=dict)
    frases: list = field(default_factory=list)
    indicadores: list = field(default_factory=list)
    pontos_de_atencao: list = field(default_factory=list)

    @property
    def titulo(self):
        return "Relatório consolidado da unidade"

    @property
    def data_dos_dados(self):
        return DATA_DOS_DADOS.format(instante=rel.instante_por_extenso(self.referencia))


ROTULOS_DAS_PENDENCIAS = {
    rel.RESULTADO_NAO_DIVULGADO: "resultado ainda não divulgado",
    rel.DEFINITIVO_NAO_PUBLICADO: "resultado definitivo ainda não publicado",
    rel.REAVALIACAO_PENDENTE: "reavaliação determinada por recurso ainda não concluída",
    rel.PROVIDENCIA_PENDENTE: "providência determinada por recurso ainda não cumprida",
    rel.APURACAO_DESATUALIZADA: "apuração das vagas desatualizada",
    rel.CONVOCACAO_AGUARDANDO: "convocação aguardando resposta",
    rel.CONVOCACAO_VENCIDA: "convocação com prazo encerrado sem registro de resposta",
    rel.RECURSO_AGUARDANDO: "recurso aguardando decisão",
}
ORDEM_DAS_PENDENCIAS = tuple(ROTULOS_DAS_PENDENCIAS)
ROTULOS_NO_PLURAL = {
    rel.RESULTADO_NAO_DIVULGADO: "resultados ainda não divulgados",
    rel.DEFINITIVO_NAO_PUBLICADO: "resultados definitivos ainda não publicados",
    rel.REAVALIACAO_PENDENTE: "reavaliações determinadas por recurso ainda não concluídas",
    rel.PROVIDENCIA_PENDENTE: "providências determinadas por recurso ainda não cumpridas",
    rel.APURACAO_DESATUALIZADA: "apurações das vagas desatualizadas",
    rel.CONVOCACAO_AGUARDANDO: "convocações aguardando resposta",
    rel.CONVOCACAO_VENCIDA: "convocações com prazo encerrado sem registro de resposta",
    rel.RECURSO_AGUARDANDO: "recursos aguardando decisão",
}


def texto_do_item(tipo, quantidade):
    """ "1 convocação aguardando resposta" ou "2 convocações aguardando resposta"."""
    if quantidade == 1:
        return ROTULOS_DAS_PENDENCIAS[tipo]
    return f"{quantidade} {ROTULOS_NO_PLURAL[tipo]}"


def _situacao(fatos):
    rotulo = SITUACOES.get(fatos.edital.status, fatos.edital.status)
    return rotulo + (f" em {data_curta(fatos.desfecho_em)}" if fatos.desfecho_em else "")


def consolidar(fatos, conjunto, *, agora, unidade=None):
    """A soma dos fatos de cada Edital, pelas regras escritas da spec. Não toca o banco."""
    universo = [f for f in fatos if f.edital.status != Edital.Status.CANCELADO]
    cancelados = len(fatos) - len(universo)
    # Os Editais cujo relatório individual omite os totais não públicos ficam fora deles (FR-2592).
    nao_publicos = [f for f in universo if not f.total_omitido]

    perfis = [p for f in universo for p in f.perfis]
    com_vaga = [p for p in perfis if p.vagas.valor]
    vagas = sum(f.vagas for f in universo)
    numerador = sum(p.inscricoes.valor for p in com_vaga)
    abertos = sum(1 for f in universo if f.periodo_aberto)
    inscricoes = sum(f.inscricoes for f in universo)

    if not universo:
        todos_cancelados = Numero.nao_aplicavel("todos os Editais do conjunto foram cancelados")
        numero_inscricoes = razao = todos_cancelados
    else:
        numero_inscricoes = Numero.de(inscricoes, parcial=bool(abertos))
        razao = (
            Numero.de(visao_geral._razao(numerador, vagas), parcial=bool(abertos))
            if vagas
            else Numero.nao_aplicavel("nenhum perfil do conjunto tem vaga imediata")
        )

    meses = Counter()
    for f in universo:
        for instante in f.envios:
            local = instante.astimezone(ZONA)
            meses[(local.year, local.month)] += 1

    linhas = []
    for f in universo:
        num = sum(p.inscricoes.valor for p in f.perfis if p.vagas.valor)
        linhas.append(
            LinhaDoEdital(
                edital=f.edital,
                primeira=conjunto.primeira(f.edital),
                perfis=len(f.perfis),
                vagas=f.vagas,
                inscricoes=Numero.de(f.inscricoes, parcial=f.periodo_aberto),
                por_vaga=(
                    Numero.de(visao_geral._razao(num, f.vagas), parcial=f.periodo_aberto)
                    if f.vagas
                    else Numero.nao_aplicavel("não se aplica")
                ),
            )
        )

    recursos = None
    convocacoes = None
    if nao_publicos:
        somados = Counter()
        for f in nao_publicos:
            for campo in (
                "apresentados",
                "nao_admitidos",
                "indeferidos",
                "deferidos",
                "aguardando",
            ):
                somados[campo] += getattr(f.recursos, campo)
        recursos = rel.Recursos(**{k: somados[k] for k in rel.Recursos.__dataclass_fields__})
        realizadas = sum(f.convocacoes.realizadas for f in nao_publicos)
        aceitas = sum(f.convocacoes.aceitas for f in nao_publicos)
        aguardando = sum(f.convocacoes.aguardando for f in nao_publicos)
        vencidas = sum(f.convocacoes.vencidas for f in nao_publicos)
        convocacoes = {
            "realizadas": realizadas,
            "aceitas": aceitas,
            "aguardando": aguardando,
            "vencidas": vencidas,
            "outros": realizadas - aceitas - aguardando - vencidas,
        }

    vagas_np = sum(f.vagas for f in nao_publicos)
    apuradas = sum(f.vagas_apuradas for f in nao_publicos)
    desatualizadas = sum(f.vagas_desatualizadas for f in nao_publicos)

    por_tipo = defaultdict(lambda: [set(), 0])
    providencias = []
    for f in universo:
        visiveis = [p for p in f.pendencias if p.publica or not f.total_omitido]
        for p in visiveis:
            por_tipo[p.tipo][0].add(f.edital.pk)
            por_tipo[p.tipo][1] += p.quantidade
        if f.pendencias:
            itens = Counter()
            for p in visiveis:
                itens[p.tipo] += p.quantidade
            providencias.append(
                ProvidenciasDoEdital(
                    edital=f.edital,
                    situacao=_situacao(f),
                    itens=tuple(
                        (tipo, itens[tipo]) for tipo in ORDEM_DAS_PENDENCIAS if itens[tipo]
                    ),
                    omitido=f.total_omitido and any(not p.publica for p in f.pendencias),
                )
            )
    pendencias_por_tipo = [
        (ROTULOS_DAS_PENDENCIAS[tipo], len(por_tipo[tipo][0]), por_tipo[tipo][1])
        for tipo in ORDEM_DAS_PENDENCIAS
        if tipo in por_tipo
    ]

    situacoes = Counter(f.edital.status for f in fatos)
    consolidado = Consolidado(
        referencia=agora,
        conjunto=conjunto,
        unidade=unidade,
        editais=len(fatos),
        situacoes=[
            (SITUACOES[s].lower() + ("s" if situacoes[s] > 1 else ""), situacoes[s])
            for s in (Edital.Status.ENCERRADO, Edital.Status.PUBLICADO, Edital.Status.CANCELADO)
            if situacoes[s]
        ],
        por_especie=Counter(f.especie for f in fatos),
        cancelados=cancelados,
        universo=len(universo),
        fora_dos_nao_publicos=len(universo) - len(nao_publicos),
        vagas=vagas,
        vagas_reservadas=sum(rel.reservadas_do_perfil(p) for p in com_vaga),
        perfis=len(perfis),
        perfis_com_vaga=len(com_vaga),
        perfis_so_reserva=sum(1 for p in perfis if rel.so_cadastro_de_reserva(p)),
        inscricoes=numero_inscricoes,
        numerador=numerador,
        razao=razao,
        periodos_abertos=abertos,
        envios_por_mes=sorted(meses.items()),
        linhas=linhas,
        perfis_com_marca=[
            (f.edital, nome, n, v, especies)
            for f in universo
            for nome, n, v, especies in f.perfis_com_marca
        ],
        retificacoes=sum(f.retificacoes for f in universo),
        editais_retificados=sum(1 for f in universo if f.retificacoes),
        prorrogados=sum(1 for f in universo if f.prorrogado),
        recursos=recursos,
        marcos_declarados=sum(f.marcos_declarados for f in universo),
        marcos_definitivos=sum(f.marcos_definitivos for f in universo),
        editais_com_resultado_previsto=sum(1 for f in universo if f.marcos_declarados),
        editais_definitivos=sum(
            1
            for f in universo
            if f.marcos_declarados and f.marcos_definitivos == f.marcos_declarados
        ),
        vagas_habilitadas=sum(f.vagas_habilitadas or 0 for f in nao_publicos),
        vagas_apuradas=apuradas,
        vagas_desatualizadas=desatualizadas,
        vagas_nao_apuradas=vagas_np - apuradas - desatualizadas,
        convocacoes=convocacoes,
        pendencias_por_tipo=pendencias_por_tipo,
        providencias_por_edital=providencias,
        encerrados_com_pendencia=sum(
            1 for f in universo if f.edital.status == Edital.Status.ENCERRADO and f.pendencias
        ),
        com_pendencia=sum(1 for f in universo if f.pendencias),
        posteriores_por_edital=[
            (f.edital, f.desfecho_em, sum(n for _, n, _ in f.posteriores))
            for f in universo
            if f.posteriores
        ],
        relacao=[
            LinhaDaRelacao(
                edital=f.edital,
                primeira=conjunto.primeira(f.edital),
                situacao=_situacao(f),
                especie={
                    rel.ACOMPANHAMENTO: "acompanhamento",
                    rel.ENCERRAMENTO: "encerramento",
                    rel.INTERRUPCAO: "interrupção",
                }[f.especie],
            )
            for f in fatos
        ],
    )
    consolidado.situacao_no_gps = " · ".join(f"{n} {rotulo}" for rotulo, n in consolidado.situacoes)
    if consolidado.com_pendencia:
        sem = consolidado.universo - consolidado.com_pendencia
        consolidado.providencias = (
            f"{consolidado.com_pendencia} "
            f"{_plural(consolidado.com_pendencia, 'Edital', 'Editais')} com providência registrada "
            f"em curso · {sem} sem nenhuma"
        )
    elif consolidado.universo:
        consolidado.providencias = "nenhuma providência pendente registrada no GPS"
    else:
        consolidado.providencias = "não se aplica: todos os Editais do conjunto foram cancelados"
    consolidado.indicadores = _indicadores(consolidado)
    consolidado.frases = _frases(consolidado)
    consolidado.pontos_de_atencao = _pontos_de_atencao(consolidado)
    return consolidado


# --- A redação ----------------------------------------------------------------------------------


def _fora_cancelados(c):
    if not c.cancelados:
        return ""
    return "; fora " + _plural(c.cancelados, "o Edital cancelado", f"os {c.cancelados} cancelados")


def _fora_pequenos(c):
    if not c.fora_dos_nao_publicos:
        return ""
    n = c.fora_dos_nao_publicos
    return (
        f"; fora {n} {_plural(n, 'Edital', 'Editais')} com menos de {rel.MINIMO_PARA_DETALHAR} "
        "inscrições enviadas, cujo relatório individual omite estes totais"
    )


OMITIDO_NO_CONJUNTO = Numero(
    ausencia=Ausencia(
        rel.OMITIDO,
        f"detalhe omitido: nenhum Edital do conjunto tem {rel.MINIMO_PARA_DETALHAR} inscrições",
    )
)


def _indicadores(c):
    if not c.universo:
        cancelados = Numero.nao_aplicavel("todos os Editais do conjunto foram cancelados")
        base = "todos os Editais do conjunto foram cancelados"
        return [
            Indicador(rotulo, cancelados, base)
            for rotulo in (
                "vagas imediatas",
                "inscrições enviadas",
                "inscrições por vaga",
                "Editais com todos os resultados definitivos",
                "vagas com inscrição classificada e habilitada",
                "convocações aceitas",
            )
        ]
    base_vagas = (
        f"em {c.perfis_com_vaga} de {c.perfis} {_plural(c.perfis, 'perfil', 'perfis')}"
        + (
            f"; {c.perfis_so_reserva} {_plural(c.perfis_so_reserva, 'perfil', 'perfis')} só de "
            "cadastro de reserva"
            if c.perfis_so_reserva
            else ""
        )
        + _fora_cancelados(c)
    )
    base_inscricoes = (
        "inscrições, e não pessoas: a mesma pessoa pode se inscrever em mais de um Edital"
        + (
            f"; {c.periodos_abertos} {_plural(c.periodos_abertos, SEGUE, SEGUEM)}"
            " com inscrições abertas"
            if c.periodos_abertos
            else ""
        )
        + _fora_cancelados(c)
    )
    base_razao = (
        f"{c.numerador} {_plural(c.numerador, 'inscrição', 'inscrições')} para {c.vagas} "
        f"{_plural(c.vagas, 'vaga', 'vagas')}, só nos perfis com vaga imediata; não é média dos "
        "Editais"
        if c.vagas
        else "nenhum perfil do conjunto tem vaga imediata"
    )
    if c.editais_com_resultado_previsto:
        definitivos = Numero.de(c.editais_definitivos)
        base_definitivos = (
            f"{c.marcos_definitivos} de {c.marcos_declarados} resultados previstos já são "
            "definitivos"
        )
    else:
        definitivos = Numero.nao_disponivel("nenhum resultado previsto")
        base_definitivos = "nenhum Edital do conjunto tem resultado previsto"

    if c.convocacoes is None:
        habilitadas = aceitas = OMITIDO_NO_CONJUNTO
        base_habilitadas = base_aceitas = OMITIDO_NO_CONJUNTO.ausencia.motivo
        de_habilitadas = de_aceitas = None
    else:
        if c.vagas_apuradas:
            habilitadas = Numero.de(c.vagas_habilitadas)
            de_habilitadas = c.vagas_apuradas
        else:
            habilitadas = Numero.nao_disponivel("nenhuma vaga apurada ainda")
            de_habilitadas = None
        sem_apuracao = c.vagas_nao_apuradas + c.vagas_desatualizadas
        base_habilitadas = (
            "nas vagas já apuradas"
            + (
                f"; {sem_apuracao} {_plural(sem_apuracao, 'vaga', 'vagas')} ainda sem apuração "
                "atualizada"
                if sem_apuracao
                else ""
            )
            + ". Não é matrícula"
            + _fora_pequenos(c)
        )
        conv = c.convocacoes
        if conv["realizadas"]:
            aceitas = Numero.de(conv["aceitas"])
            de_aceitas = conv["realizadas"]
            partes = []
            if conv["aguardando"]:
                partes.append(f"{conv['aguardando']} aguardando resposta")
            if conv["vencidas"]:
                partes.append(f"{conv['vencidas']} com prazo encerrado sem registro de resposta")
            base_aceitas = ("; ".join(partes) or "todas com resposta registrada") + _fora_pequenos(
                c
            )
        else:
            aceitas = Numero.nao_disponivel("nenhuma convocação registrada")
            de_aceitas = None
            base_aceitas = "nenhuma convocação registrada" + _fora_pequenos(c)
    return [
        Indicador("vagas imediatas", Numero.de(c.vagas), base_vagas),
        Indicador("inscrições enviadas", c.inscricoes, base_inscricoes),
        Indicador("inscrições por vaga", c.razao, base_razao),
        Indicador(
            "Editais com todos os resultados definitivos",
            definitivos,
            base_definitivos,
            de=c.editais_com_resultado_previsto or None,
        ),
        Indicador(
            "vagas com inscrição classificada e habilitada",
            habilitadas,
            base_habilitadas,
            de=de_habilitadas,
        ),
        Indicador("convocações aceitas", aceitas, base_aceitas, de=de_aceitas),
    ]


def _frases(c):
    """A visão geral, frase a frase, cada uma com condição verdadeira no instante (FR-2575)."""
    if not c.universo:
        if c.editais == 1:
            return ["O Edital do conjunto foi cancelado."]
        return [f"Os {c.editais} Editais do conjunto foram cancelados."]
    frases = []
    prefixo = (
        "Fora "
        + _plural(c.cancelados, "o Edital cancelado", f"os {c.cancelados} cancelados")
        + ", "
        if c.cancelados
        else ""
    )
    sujeito = _plural(c.universo, "o Edital do conjunto", f"os {c.universo} Editais do conjunto")
    frase = f"{prefixo}{sujeito} {_plural(c.universo, 'ofereceu', 'ofereceram')} {c.vagas} " + (
        f"{_plural(c.vagas, 'vaga imediata', 'vagas imediatas')} em {c.perfis} "
        f"{_plural(c.perfis, 'perfil', 'perfis')} de vaga"
    )
    if c.vagas_reservadas:
        frase += f" — {c.vagas_reservadas} em listas reservadas —"
    if c.perfis_so_reserva:
        frase += (
            f" e {_plural(c.universo, 'abriu', 'abriram')} cadastro de reserva sem vaga imediata "
            f"em {c.perfis_so_reserva} {_plural(c.perfis_so_reserva, 'perfil', 'perfis')}"
        )
    frases.append(frase[:1].upper() + frase[1:] + ".")
    n = c.inscricoes.valor
    frase = (
        f"{_plural(c.universo, 'Recebeu', 'Receberam')} {n} "
        f"{_plural(n, 'inscrição enviada', 'inscrições enviadas')}"
    )
    if c.periodos_abertos:
        frase += (
            f", e {c.periodos_abertos} "
            f"{_plural(c.periodos_abertos, SEGUE, SEGUEM)} com inscrições abertas"
        )
    frases.append(frase + ".")
    if c.editais_com_resultado_previsto:
        frases.append(
            f"Em {c.editais_definitivos} dos {c.editais_com_resultado_previsto} Editais com "
            "resultado previsto, todos os resultados definitivos estão publicados."
        )
    if c.convocacoes is not None and c.vagas_apuradas:
        frase = (
            f"{c.vagas_habilitadas} das {c.vagas_apuradas} vagas já apuradas têm inscrição "
            "classificada e habilitada"
        )
        conv = c.convocacoes
        partes = []
        if conv["aceitas"]:
            partes.append(
                f"{conv['aceitas']} "
                f"{_plural(conv['aceitas'], 'convocação foi aceita', 'convocações foram aceitas')}"
            )
        if conv["aguardando"]:
            partes.append(
                f"{conv['aguardando']} {_plural(conv['aguardando'], AGUARDA, AGUARDAM)} resposta"
            )
        if partes:
            frase += ": " + ", e ".join(partes)
        frases.append(frase + ".")
    if c.encerrados_com_pendencia:
        k = c.encerrados_com_pendencia
        frases.append(
            f"{k} {_plural(k, 'Edital encerrado ainda tem', 'Editais encerrados ainda têm')} "
            "providência registrada em curso."
        )
    return frases


def _pontos_de_atencao(c):
    """No máximo três, nesta ordem (FR-2576)."""
    pontos = []
    if c.encerrados_com_pendencia:
        k = c.encerrados_com_pendencia
        pontos.append(
            (
                f"{k} {_plural(k, 'Edital está encerrado', 'Editais estão encerrados')} no GPS, "
                "mas ainda "
                f"{_plural(k, 'tem', 'têm')} providência registrada.",
                "Encerrar o Edital fecha as inscrições; convocações, recursos e apurações "
                "continuam depois. O detalhe está em Providências.",
            )
        )
    if c.posteriores_por_edital:
        k = len(c.posteriores_por_edital)
        total = sum(n for _, _, n in c.posteriores_por_edital)
        pontos.append(
            (
                f"{k} {_plural(k, 'Edital tem', 'Editais têm')} registros na trilha de auditoria "
                "depois do encerramento.",
                f"São {total} {_plural(total, 'registro', 'registros')}. {NOTA_DA_TRILHA} Um "
                "relatório emitido antes deles mostraria outros números.",
            )
        )
    pontos.append(MATRICULA)
    return pontos[:3]


def mes_por_extenso(ano, mes):
    nomes = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")
    return f"{nomes[mes - 1]}/{ano}"


def texto_da_primeira(instante):
    return data_curta(instante) if instante else "—"


__all__ = [
    "LIMITE_DE_EDITAIS",
    "OPERACAO_DA_EMISSAO",
    "Conjunto",
    "Consolidado",
    "Criterio",
    "conjunto_de",
    "consolidar",
    "criterio_de",
    "ler",
    "montar",
    "proxima_emissao",
]
