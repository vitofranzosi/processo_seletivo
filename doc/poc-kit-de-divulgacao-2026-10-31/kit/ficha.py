"""A ficha de divulgação: o que a comunicação pode afirmar sobre um Edital, e de onde veio cada dado.

**Uma fonte, nenhuma saída.** A ficha não sabe de SVG, PNG nem Markdown. Textos e peça leem dela, e
só dela, e é isso que permite provar que os dois dizem a mesma coisa: a conferência de coerência
(`coerencia.py`) recusa qualquer texto da peça que não seja um valor da ficha ou uma frase fixa do
template.

**Lê o que a página pública lê, pelas mesmas funções.** A versão vigente vem de `effective_version`;
o período, de `periodo_de_inscricoes`; o desfecho, de `desfechos`; a marca, de `situacao_publica`;
a quantidade, de `quantidade_da_oferta`. Nada aqui lê tabela de elaboração, e nenhuma versão de
vigência futura entra no conteúdo — ela só é **anunciada**, por `retificacoes_a_vigorar`.

**As datas já saem escritas.** Cada instante vira texto aqui, uma vez, no fuso institucional. Se a
legenda e a peça formatassem cada uma a sua, "23h59" e "23:59" seriam duas verdades sobre o mesmo
prazo — e a conferência teria de aceitar as duas.
"""

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field

from django.urls import reverse

from processo_seletivo.inscricoes.domain.periodo import (
    ENCERRADO,
    NAO_DESIGNADO,
    evento_designado,
    periodo_de_inscricoes,
)
from processo_seletivo.interface.agenda import retificacoes_a_vigorar
from processo_seletivo.interface.relatorio_do_edital import _versoes
from processo_seletivo.portal import leitura
from processo_seletivo.processos.application.selectors import desfechos
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.models_retificacao import Retificacao
from processo_seletivo.shared.tempo import ZONA

# O modo do material. Não é a situação do Edital: é o que o material pode dizer sobre inscrição.
COM_PERIODO = "com-periodo"
NEUTRO = "neutro"  # sem período designado: o Edital não recebe inscrição pelo GPS
INDISPONIVEL = "indisponivel"

# "Edital nº 91/2026 – Curso…": o número já sai à parte na peça, e repeti-lo no título é o mesmo
# dado duas vezes (`numero_no_titulo`, `portal/views.py`). Só o prefixo que repete **este** número
# sai; o resto do título não é tocado.
PREFIXO_DO_NUMERO = r"^\s*Edital\s+(?:n[º°o]\.?\s*)?{numero}/{ano}\s*[–—\-:,]?\s*"


def _data(instante):
    return instante.astimezone(ZONA).strftime("%d/%m/%Y") if instante else ""


def _hora(instante):
    # A mesma forma da página da seleção: `date:"H\hi"` em `_periodo.html`.
    return instante.astimezone(ZONA).strftime("%Hh%M") if instante else ""


def _periodo_curto(inicio, fim):
    """O período em corpo grande: o ano uma vez só, quando é o mesmo nas duas pontas.

    De dezembro a janeiro o ano aparece nas duas: "15/12 a 10/01/2027" leria o início em 2027.
    """
    if inicio and fim:
        mesmo_ano = inicio.astimezone(ZONA).year == fim.astimezone(ZONA).year
        comeco = inicio.astimezone(ZONA).strftime("%d/%m") if mesmo_ano else _data(inicio)
        return f"{comeco} a {_data(fim)}"
    if inicio:
        return f"a partir de {_data(inicio)}"
    return f"até {_data(fim)}" if fim else ""


def _iso(instante):
    return instante.astimezone(ZONA).isoformat() if instante else None


@dataclass(frozen=True)
class Oferta:
    perfil_id: str
    nome: str
    localidade: str
    vagas_imediatas: int
    cadastro_reserva: bool
    quantidade: str  # `quantidade_da_oferta`: "40 vagas", "cadastro reserva"…
    endereco: str  # a âncora do Perfil na página da seleção


@dataclass(frozen=True)
class Origem:
    """De onde veio um valor: o caminho no conteúdo vigente e o ato que o deu."""

    campo: str
    valor: str
    caminho: str
    ato: str


@dataclass(frozen=True)
class Ficha:
    modo: str
    motivo: str
    # Identificação
    edital_id: str
    numero: str
    ano: str
    identificacao: str  # "Edital nº 91/2026"
    titulo: str
    titulo_sem_numero: str
    titulo_do_processo: str
    unidade_sigla: str
    unidade_nome: str
    # Situação, no instante de referência
    referencia: str
    referencia_texto: str
    situacao_chave: str
    situacao_rotulo: str
    # Período, já escrito
    periodo_estado: str
    inicio: str | None
    fim: str | None
    inicio_data: str
    inicio_hora: str
    fim_data: str
    fim_hora: str
    periodo_curto: str  # "13/10 a 04/11/2026": o que a peça escreve em corpo grande
    prorrogado: bool
    fim_original_data: str
    # Oferta
    ofertas: tuple[Oferta, ...]
    nomes_iguais: bool
    total_de_vagas: int | None
    # Destino
    endereco: str
    caminho_curto: str
    # Versão
    versao_id: str
    versao_hash: str
    versao_desde: str
    versao_desde_texto: str
    versao_ato: str
    retificacao_a_vigorar: str | None
    retificacao_a_vigorar_texto: str
    impressao: str
    origens: tuple[Origem, ...] = field(default=())

    def como_dict(self):
        return asdict(self)


def _ato_da_publicacao(publicacao, numeracao):
    retificacao = getattr(publicacao, "retificacao", None)
    if retificacao is None:
        return f"Publicação original de {_data(publicacao.published_at)}"
    return f"Retificação nº {numeracao[retificacao.id]} de {_data(publicacao.published_at)}"


def _numeracao_das_retificacoes(edital):
    publicadas = (
        Retificacao.objects.filter(edital=edital, status=Retificacao.Status.PUBLICADA)
        .select_related("publication")
        .order_by("publication__publication_order")
    )
    return {retificacao.id: posicao for posicao, retificacao in enumerate(publicadas, start=1)}


def _impressao(dados):
    """SHA-256 só dos campos que o material usa (estudo, Eixo D).

    O `content_hash` cobre o conteúdo inteiro: uma Retificação que muda só o desempate marcaria como
    antigo um material que não diz nada de desempate. O instante de referência e a situação ficam
    fora: eles mudam com o relógio, e o que se quer saber é se **o dado** mudou.
    """
    canonico = json.dumps(dados, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonico.encode()).hexdigest()


def ficha_do_edital(edital_id, *, agora, base_url):
    """A ficha do Edital no instante `agora`, com os endereços montados sobre `base_url`.

    `base_url` é parâmetro porque o sistema não tem setting de endereço absoluto: na produção ele
    viria de `request.build_absolute_uri`, como nos avisos (`interface/avisos.py`).
    """
    edital = Edital.objects.select_related("processo").get(pk=edital_id)
    versao = effective_version(edital_id=edital.id, at=agora)
    conteudo = versao.content
    publicacao = versao.source_publication
    numeracao = _numeracao_das_retificacoes(edital)
    desfecho = desfechos([edital])[edital.id]
    periodo = periodo_de_inscricoes(conteudo, agora)
    chave, rotulo = leitura.situacao_publica(periodo, desfecho)

    numero, ano = str(conteudo.get("number", "")), str(conteudo.get("year", ""))
    titulo = conteudo.get("title", "")
    titulo_sem_numero = re.sub(
        PREFIXO_DO_NUMERO.format(numero=re.escape(numero), ano=re.escape(ano)),
        "",
        titulo,
        count=1,
        flags=re.IGNORECASE,
    )
    endereco = base_url.rstrip("/") + reverse("portal:selecao", args=[edital.id])

    # O desfecho vence o período (047): Edital cancelado dentro do prazo não tem material.
    if desfecho is not None and desfecho.do_edital:
        modo = INDISPONIVEL
        motivo = (
            f"{rotulo} em {_data(desfecho.em)}. Não há material de divulgação para um Edital "
            "que não recebe inscrições."
        )
    elif periodo.estado == ENCERRADO:
        modo = INDISPONIVEL
        motivo = (
            "Período de inscrições cancelado."
            if periodo.cancelado
            else f"Inscrições encerradas em {_data(periodo.fim)}. O material de resultado é "
            "etapa futura."
        )
    elif periodo.estado == NAO_DESIGNADO:
        modo, motivo = (
            NEUTRO,
            "O Edital não recebe inscrições pelo GPS; o material não fala de inscrição.",
        )
    else:
        modo, motivo = COM_PERIODO, ""

    # A prorrogação comprovada: o término do original contra o da versão vigente, pela mesma leitura
    # do Relatório do Edital (099).
    original, _ = _versoes(edital, agora)
    evento_original = evento_designado(original or {})
    fim_original = None
    if evento_original and evento_original.get("endAt"):
        fim_original = periodo_de_inscricoes(original, agora).fim
    prorrogado = bool(periodo.fim and fim_original and periodo.fim > fim_original)

    ofertas = tuple(
        Oferta(
            perfil_id=str(perfil.get("id")),
            nome=(perfil.get("name") or "").strip(),
            localidade=(perfil.get("locality") or "").strip(),
            vagas_imediatas=perfil.get("immediateVacancies") or 0,
            cadastro_reserva=(perfil.get("reserveType") or "NONE") != "NONE",
            quantidade=leitura.quantidade_da_oferta(
                perfil.get("immediateVacancies") or 0, perfil.get("reserveType")
            ),
            endereco=f"{endereco}#vaga-{perfil.get('id')}",
        )
        for perfil in conteudo.get("profiles") or []
        if perfil.get("name")
    )
    # A soma só quando toda opção tem vaga imediata (decisão D-4 do estudo, opção b): com um Perfil
    # só de cadastro reserva, "N vagas" leria como se ele também as tivesse.
    total = (
        sum(oferta.vagas_imediatas for oferta in ofertas)
        if ofertas and all(oferta.vagas_imediatas > 0 for oferta in ofertas)
        else None
    )

    a_vigorar = retificacoes_a_vigorar([edital.id], agora).get(edital.id)
    designado = evento_designado(conteudo)
    origens = _origens(versao, designado, numeracao, titulo, periodo, conteudo)

    usados = {
        "numero": numero,
        "ano": ano,
        "titulo": titulo,
        "unidade": publicacao.unidade_sigla,
        "inicio": _iso(periodo.inicio),
        "fim": _iso(periodo.fim),
        "cancelado": periodo.cancelado,
        "designado": periodo.estado != NAO_DESIGNADO,
        "ofertas": [[o.nome, o.localidade, o.vagas_imediatas, o.cadastro_reserva] for o in ofertas],
        "endereco": endereco,
    }
    return Ficha(
        modo=modo,
        motivo=motivo,
        edital_id=str(edital.id),
        numero=numero,
        ano=ano,
        identificacao=f"Edital nº {numero}/{ano}",
        titulo=titulo,
        titulo_sem_numero=titulo_sem_numero,
        titulo_do_processo=conteudo.get("processoTitle", ""),
        unidade_sigla=publicacao.unidade_sigla,
        unidade_nome=publicacao.unidade_nome,
        referencia=_iso(agora),
        referencia_texto=f"{_data(agora)}, {_hora(agora)}",
        situacao_chave=chave,
        situacao_rotulo=rotulo,
        periodo_estado=periodo.estado,
        inicio=_iso(periodo.inicio),
        fim=_iso(periodo.fim),
        inicio_data=_data(periodo.inicio),
        inicio_hora=_hora(periodo.inicio),
        fim_data=_data(periodo.fim),
        fim_hora=_hora(periodo.fim),
        periodo_curto=_periodo_curto(periodo.inicio, periodo.fim),
        prorrogado=prorrogado,
        fim_original_data=_data(fim_original) if prorrogado else "",
        ofertas=ofertas,
        nomes_iguais=len({o.nome for o in ofertas}) == 1 and len(ofertas) > 1,
        total_de_vagas=total,
        endereco=endereco,
        caminho_curto=f"{base_url.split('://', 1)[-1].rstrip('/')}/selecoes",
        versao_id=str(versao.id),
        versao_hash=versao.content_hash,
        versao_desde=_iso(versao.valid_from),
        versao_desde_texto=f"{_data(versao.valid_from)}, {_hora(versao.valid_from)}",
        versao_ato=_ato_da_publicacao(publicacao, numeracao),
        retificacao_a_vigorar=_iso(a_vigorar),
        retificacao_a_vigorar_texto=(
            f"{_data(a_vigorar)}, {_hora(a_vigorar)}" if a_vigorar else ""
        ),
        impressao=_impressao(usados),
        origens=origens,
    )


def _origens(versao, designado, numeracao, titulo, periodo, conteudo):
    """A proveniência dos campos que o material afirma, pela `ProvenienciaConteudo` da versão.

    O caminho é o da `004`. Sem proveniência registrada, o valor é o da publicação original — é o que
    a ausência quer dizer na materialização (`_materialize_affected_versions`).
    """
    por_caminho = {p.target_path: p.publicacao for p in versao.proveniencias.all()}
    original = (
        versao.edital.publicacoes.filter(revisao__isnull=False)
        .order_by("publication_order")
        .first()
    )

    def ato(caminho):
        publicacao = por_caminho.get(caminho, original)
        return _ato_da_publicacao(publicacao, numeracao) if publicacao else ""

    linhas = [
        Origem(
            "Número e ano",
            f"{conteudo.get('number')}/{conteudo.get('year')}",
            "/number, /year",
            ato("/number"),
        ),
        Origem("Título", titulo, "/title", ato("/title")),
    ]
    if designado is not None:
        base = f"/schedule/id={designado.get('id')}"
        linhas.append(
            Origem(
                "Início das inscrições",
                _iso(periodo.inicio) or "",
                f"{base}/startAt",
                ato(f"{base}/startAt"),
            )
        )
        linhas.append(
            Origem(
                "Término das inscrições",
                _iso(periodo.fim) or "",
                f"{base}/endAt",
                ato(f"{base}/endAt"),
            )
        )
    for perfil in conteudo.get("profiles") or []:
        caminho = f"/profiles/id={perfil.get('id')}/immediateVacancies"
        linhas.append(
            Origem(
                f"Vagas — {perfil.get('name')} — {perfil.get('locality') or 'sem localidade'}",
                str(perfil.get("immediateVacancies")),
                caminho,
                ato(caminho),
            )
        )
    linhas.append(
        Origem(
            "Unidade",
            versao.source_publication.unidade_sigla,
            "Publicacao.unidade_sigla (congelada no ato)",
            _ato_da_publicacao(versao.source_publication, numeracao),
        )
    )
    return tuple(linhas)


ROTULOS_DOS_CAMPOS = {
    "titulo": "título",
    "unidade_sigla": "unidade",
    "inicio_data": "início das inscrições",
    "inicio_hora": "hora de início",
    "fim_data": "término das inscrições",
    "fim_hora": "hora do término",
    "endereco": "endereço",
}


def diferencas(antiga, nova):
    """O que mudou entre duas fichas, nos campos que o material afirma: `[(campo, de, para)]`.

    É o "de → para" que o "O que mudou" público não diz (047, RC-111). Vazio quando a impressão é a
    mesma — a Retificação que não toca o material não o marca como antigo.
    """
    if antiga["impressao"] == nova["impressao"]:
        return []
    mudancas = [
        (rotulo, antiga[campo], nova[campo])
        for campo, rotulo in ROTULOS_DOS_CAMPOS.items()
        if antiga[campo] != nova[campo]
    ]
    anteriores = {o["perfil_id"]: o for o in antiga["ofertas"]}
    for oferta in nova["ofertas"]:
        antes = anteriores.pop(oferta["perfil_id"], None)
        rotulo = " — ".join(filter(None, (oferta["nome"], oferta["localidade"])))
        if antes is None:
            mudancas.append((f"oferta {rotulo}", "—", oferta["quantidade"]))
        elif antes["quantidade"] != oferta["quantidade"]:
            mudancas.append((f"oferta {rotulo}", antes["quantidade"], oferta["quantidade"]))
    for antes in anteriores.values():
        rotulo = " — ".join(filter(None, (antes["nome"], antes["localidade"])))
        mudancas.append((f"oferta {rotulo}", antes["quantidade"], "retirada"))
    return mudancas
