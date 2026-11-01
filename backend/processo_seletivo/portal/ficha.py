"""A ficha de divulgação: o que a comunicação pode afirmar sobre um Edital, e de onde veio (111).

**Uma fonte, nenhuma saída.** A ficha não sabe de texto, SVG nem PNG: os textos do kit e a peça leem
dela, e só dela (`FR-3423`). É a terceira leitora do conteúdo vigente ao lado da página da seleção e
do cartão da vitrine, e por isso mora aqui, junto do que as outras duas leem (`D-002`).

**Nenhuma regra nova.** Cada valor sai da função que a página pública já usa:

- a versão vigente sai de `effective_version`;
- o período, de `periodo_de_inscricoes`;
- o desfecho, de `desfechos`;
- a marca, de `situacao_publica`;
- a quantidade, de `quantidade_da_oferta`;
- as vagas, de `vagas_do_conteudo`;
- a unidade do ato, de `do_ato`;
- a prorrogação, de `prorrogacao`;
- a origem de cada valor, de `origens` sobre o `contexto` da `070`.

Um teste prende a coincidência com o cartão e com a página (`FR-3407`). A versão de vigência futura
**não** é lida: ela só é anunciada pelo instante em que passa a valer (`FR-3404`).

**As datas já saem escritas, uma vez.** Se a legenda e a peça formatassem cada uma a sua, "23h59" e
"23:59" seriam duas verdades sobre o mesmo prazo.
"""

import hashlib
import json
import re
from dataclasses import asdict, dataclass

from django.urls import reverse

from processo_seletivo.duvidas.application.consultar import contexto
from processo_seletivo.duvidas.domain.estruturas import RETIFICACAO
from processo_seletivo.duvidas.domain.origem import origens
from processo_seletivo.editais.domain.quadro import vagas_do_conteudo
from processo_seletivo.inscricoes.domain.periodo import (
    ENCERRADO,
    NAO_DESIGNADO,
    evento_designado,
    periodo_de_inscricoes,
)
from processo_seletivo.portal import leitura
from processo_seletivo.processos.application.selectors import desfechos
from processo_seletivo.publicacoes.application.selectors import (
    prorrogacao,
    retificacoes_a_vigorar,
    retificacoes_publicadas,
    versoes_original_e_vigente,
)
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.unidades.application.identificacao import do_ato

COM_PERIODO = "com-periodo"
NEUTRO = "neutro"  # sem período designado: o Edital não recebe inscrição pelo GPS
SEM_MATERIAL = "sem-material"

#: A versão da impressão (`FR-3448`, `D-018`). Muda quando os campos ou a serialização mudam, e a
#: exportação gravada com outra versão é comparada recalculando a impressão a partir dos campos.
VERSAO_DA_IMPRESSAO = 1

# "Edital nº 91/2026 – Curso…": o número já sai à parte na peça, e repeti-lo no título é o mesmo
# dado duas vezes (`numero_no_titulo`, `portal/views.py`). Só sai o prefixo deste número.
PREFIXO_DO_NUMERO = r"^\s*Edital\s+(?:n[º°o]\.?\s*)?{numero}/{ano}\s*[–—\-:,]?\s*"

#: O que o material **não diz** por conta própria (`FR-3414`): tempo relativo, estado do momento,
#: promessa, juízo e vocabulário interno. Vale para as frases fixas, a composição e a manchete. Num
#: valor oficial ("São Marcos", "faixa etária") o termo fica, e a conferência o aponta (`EC-26`).
TERMOS_QUE_O_MATERIAL_NAO_DIZ = (
    r"\bfaltam?\b",
    r"\bamanhã\b",
    r"\bhoje\b",
    r"\búltimos? dias?\b",
    r"\búltima oportunidade\b",
    r"\bnão perca\b",
    r"\bgaranta\b",
    r"\bgarantid[ao]s?\b",
    r"\binscrições abertas\b",
    r"\bestão abertas\b",
    r"\bresultado (?:final|disponível)\b",
    r"\baprovad[ao]s?\b",
    r"(?<!não )\bclassificad[ao]s?\b",
    r"\bmarcos?\b",
    r"\brecortes?\b",
    r"\bfaixas?\b",
    r"\bapuração\b",
    r"\bhomologa",
)


def termos_proibidos(texto):
    """Os padrões da lista que aparecem em `texto`, sem caixa."""
    return [
        padrao
        for padrao in TERMOS_QUE_O_MATERIAL_NAO_DIZ
        if re.search(padrao, texto or "", re.IGNORECASE)
    ]


def _data(instante):
    return instante.astimezone(ZONA).strftime("%d/%m/%Y") if instante else ""


def _hora(instante):
    # A mesma forma da página da seleção: `date:"H\hi"` em `_periodo.html`.
    return instante.astimezone(ZONA).strftime("%Hh%M") if instante else ""


def _iso(instante):
    return instante.astimezone(ZONA).isoformat() if instante else None


def instante_por_extenso(instante):
    return f"{_data(instante)}, {_hora(instante)}" if instante else ""


def _periodo_curto(inicio, fim):
    """O período em corpo grande: o ano uma vez só, quando é o mesmo nas duas pontas (`EC-7`)."""
    if inicio and fim:
        mesmo_ano = inicio.astimezone(ZONA).year == fim.astimezone(ZONA).year
        comeco = inicio.astimezone(ZONA).strftime("%d/%m") if mesmo_ano else _data(inicio)
        return f"{comeco} a {_data(fim)}"
    if inicio:
        return f"a partir de {_data(inicio)}"
    return f"até {_data(fim)}" if fim else ""


@dataclass(frozen=True)
class Oferta:
    perfil_id: str
    nome: str
    localidade: str
    vagas_imediatas: int
    cadastro_reserva: bool
    quantidade: str  # `quantidade_da_oferta`: "40 vagas", "cadastro reserva"…
    ancora: str  # "#vaga-<id>", a âncora da página da seleção


@dataclass(frozen=True)
class Origem:
    """De onde veio um valor: o caminho no conteúdo vigente e o ato, ou os atos, que o deram."""

    campo: str
    valor: str
    caminho: str
    atos: tuple[str, ...]


@dataclass(frozen=True)
class Ficha:
    modo: str
    motivo: str
    edital_id: str
    numero: str
    ano: str
    identificacao: str
    titulo: str
    titulo_sem_numero: str
    titulo_do_processo: str
    unidade_sigla: str
    referencia: str
    referencia_texto: str
    situacao_chave: str
    situacao_rotulo: str
    periodo_estado: str
    inicio: str | None
    fim: str | None
    cancelado: bool
    inicio_data: str
    inicio_hora: str
    fim_data: str
    fim_hora: str
    periodo_curto: str
    prorrogado: bool
    fim_original_texto: str
    fim_vigente_texto: str
    ofertas: tuple[Oferta, ...]
    nomes_iguais: bool
    total_de_vagas: int | None
    caminho: str
    endereco: str | None  # nulo em host local (`FR-3447`)
    caminho_curto: str | None
    versao_id: str
    versao_hash: str
    versao_desde: str
    versao_desde_texto: str
    versao_ato: str
    retificacao_a_vigorar: str | None
    retificacao_a_vigorar_texto: str
    campos: dict
    impressao: str
    versao_da_impressao: int = VERSAO_DA_IMPRESSAO
    origens: tuple[Origem, ...] = ()
    termos_em_valor_oficial: tuple[str, ...] = ()

    def como_dict(self):
        return asdict(self)

    @property
    def tem_material(self):
        return self.modo != SEM_MATERIAL


def impressao_dos_campos(campos):
    """SHA-256 da serialização canônica dos campos que o material afirma (`FR-3411`)."""
    canonico = json.dumps(campos, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonico.encode()).hexdigest()


def _campos(numero, ano, titulo, titulo_do_processo, unidade, periodo, ofertas, caminho):
    """Os campos da impressão, versão 1 (`D-018`).

    Ficam fora o instante, a situação, a versão, o host e a ordem publicada: mudam sem que o
    material diga outra coisa, e cada um seria um alarme falso de desatualização.
    """
    return {
        "numero": numero,
        "ano": ano,
        "titulo": titulo,
        "titulo_do_processo": titulo_do_processo,
        "unidade": unidade,
        "inicio": _iso(periodo.inicio),
        "fim": _iso(periodo.fim),
        "cancelado": periodo.cancelado,
        "designado": periodo.estado != NAO_DESIGNADO,
        "ofertas": sorted(
            (
                {
                    "perfil_id": o.perfil_id,
                    "nome": o.nome,
                    "localidade": o.localidade,
                    "vagas": o.vagas_imediatas,
                    "reserva": o.cadastro_reserva,
                }
                for o in ofertas
            ),
            key=lambda item: item["perfil_id"],
        ),
        "caminho": caminho,
    }


def _ofertas(conteudo, quadro):
    resultado = []
    for perfil in conteudo.get("profiles") or []:
        if not isinstance(perfil, dict) or not (perfil.get("name") or "").strip():
            continue
        identidade = str(perfil.get("id"))
        vagas = quadro.quantidades.get(identidade, 0)
        resultado.append(
            Oferta(
                perfil_id=identidade,
                nome=perfil["name"].strip(),
                localidade=(perfil.get("locality") or "").strip(),
                vagas_imediatas=vagas,
                cadastro_reserva=perfil.get("reserveType") in leitura.TIPOS_COM_RESERVA,
                quantidade=leitura.quantidade_da_oferta(vagas, perfil.get("reserveType")),
                ancora=f"#vaga-{identidade}",
            )
        )
    return tuple(resultado)


def _modo(periodo, desfecho):
    """O que o material pode dizer sobre inscrição (`FR-3410`). O desfecho vence o período."""
    if desfecho is not None and desfecho.do_edital:
        rotulo = "cancelado" if desfecho.operacao == "CANCELADO" else "encerrado"
        quando = f" em {_data(desfecho.em)}" if desfecho.em else ""
        return (
            SEM_MATERIAL,
            f"Edital {rotulo}{quando}. Não há material para um Edital que não recebe inscrições.",
        )
    if desfecho is not None:
        # P-8: Processo encerrado ou cancelado com Edital publicado. A página informa; divulgar é
        # outra coisa. O verbo é o do ato registrado: "encerrado" para um cancelamento afirmaria
        # outro ato.
        verbo = "cancelado" if desfecho.operacao == "CANCELADO" else "encerrado"
        quando = f" em {_data(desfecho.em)}" if desfecho.em else ""
        return (
            SEM_MATERIAL,
            f"O Processo foi {verbo}{quando}. Até decisão (P-8), não há material.",
        )
    if periodo.estado == ENCERRADO:
        if periodo.cancelado:
            return SEM_MATERIAL, "Período de inscrições cancelado. Não há material."
        return SEM_MATERIAL, f"Inscrições encerradas em {_data(periodo.fim)}. Não há material."
    if periodo.estado == NAO_DESIGNADO:
        return NEUTRO, "O Edital não recebe inscrições pelo GPS; o material não fala de inscrição."
    if periodo.inicio is None and periodo.fim is None:
        # Designado e sem nenhuma data: não há prazo a dizer, e qualquer frase de período sairia
        # vazia ("até , às"). O material fala só do Edital, como no modo neutro.
        return (
            NEUTRO,
            "O período de inscrições não tem datas declaradas; o material não fala de prazo.",
        )
    return COM_PERIODO, ""


def _rotulo_do_ato(ato, numeracao):
    if ato.ato == RETIFICACAO:
        return f"Retificação nº {numeracao.get(ato.publicacao_id, '?')}"
    return "Publicação original"


def _origens(ctx, conteudo, numeracao):
    """A origem de período e vagas pela regra da `070` (`FR-3408`), e nunca pelo caminho exato."""
    linhas = []

    def origem(campo, valor, caminho):
        atos = origens(caminho, ctx.proveniencias, ctx.atos)
        linhas.append(
            Origem(campo, valor, caminho, tuple(_rotulo_do_ato(ato, numeracao) for ato in atos))
        )

    designado = evento_designado(conteudo)
    if designado is not None:
        base = f"/schedule/id={designado.get('id')}"
        origem("Início das inscrições", str(designado.get("startAt") or ""), f"{base}/startAt")
        origem("Término das inscrições", str(designado.get("endAt") or ""), f"{base}/endAt")
    for perfil in conteudo.get("profiles") or []:
        if not isinstance(perfil, dict):
            continue
        rotulo = " — ".join(filter(None, (perfil.get("name"), perfil.get("locality"))))
        origem(
            f"Vagas — {rotulo}",
            str(perfil.get("immediateVacancies")),
            f"/profiles/id={perfil.get('id')}/immediateVacancies",
        )
    return tuple(linhas)


def ler(edital, *, agora, base_url):
    """A ficha do Edital no instante `agora`. `base_url` nulo é host local, e não dá endereço.

    **Uma leitura da versão, e não duas.** O `contexto()` da `070` já resolve a versão vigente e os
    atos para a proveniência; a ficha busca a versão pelo identificador que ele devolve, com a
    publicação de origem junto, em vez de chamar `effective_version` de novo. O Edital vem de quem
    chama, que já o leu na porta.
    """
    ctx = contexto(edital_id=edital.id, instante=agora)
    versao = VersaoConsolidada.objects.select_related(
        "source_publication", "source_publication__retificacao"
    ).get(pk=ctx.versao.id)
    conteudo = versao.content
    publicacao = versao.source_publication
    desfecho = desfechos([edital])[edital.id]
    periodo = periodo_de_inscricoes(conteudo, agora)
    chave, rotulo = leitura.situacao_publica(periodo, desfecho)
    modo, motivo = _modo(periodo, desfecho)

    numero, ano = str(conteudo.get("number", "")), str(conteudo.get("year", ""))
    titulo = conteudo.get("title", "") or ""
    titulo_do_processo = conteudo.get("processoTitle", "") or ""
    titulo_sem_numero = re.sub(
        PREFIXO_DO_NUMERO.format(numero=re.escape(numero), ano=re.escape(ano)),
        "",
        titulo,
        count=1,
        flags=re.IGNORECASE,
    )
    unidade = do_ato(publicacao.unidade_sigla, edital.institution_scope).sigla or ""
    caminho = reverse("portal:selecao", args=[edital.id])
    endereco = f"{base_url.rstrip('/')}{caminho}" if base_url else None
    caminho_curto = (
        f"{base_url.split('://', 1)[-1].rstrip('/')}{reverse('portal:vitrine')}".rstrip("/")
        if base_url
        else None
    )

    quadro = vagas_do_conteudo(conteudo)
    ofertas = _ofertas(conteudo, quadro)
    # A soma só quando toda opção tem vaga imediata, e dita sempre com o número de opções
    # (`FR-3425`): com um Perfil só de cadastro reserva, "N vagas" leria como se ele as tivesse.
    total = (
        sum(o.vagas_imediatas for o in ofertas)
        if ofertas and all(o.vagas_imediatas > 0 for o in ofertas)
        else None
    )

    original, _ = versoes_original_e_vigente(edital, agora)
    lida = prorrogacao(original, conteudo)
    mesma_data = (
        lida.prorrogado
        and lida.termino_original.astimezone(ZONA).date()
        == lida.termino_vigente.astimezone(ZONA).date()
    )

    def termino(instante):
        # Com a mesma data nas duas pontas, a hora é o que mudou, e precisa aparecer (`EC-25`).
        return instante_por_extenso(instante) if mesma_data else _data(instante)

    numeracao = {
        str(retificacao.publication_id): posicao
        for posicao, retificacao in enumerate(retificacoes_publicadas(edital, agora), start=1)
    }
    retificacao = getattr(publicacao, "retificacao", None)
    versao_ato = (
        f"Retificação nº {numeracao.get(str(publicacao.id), '?')} "
        f"de {_data(publicacao.published_at)}"
        if retificacao is not None
        else f"Publicação original de {_data(publicacao.published_at)}"
    )
    a_vigorar = retificacoes_a_vigorar([edital.id], agora).get(edital.id)

    campos = _campos(numero, ano, titulo, titulo_do_processo, unidade, periodo, ofertas, caminho)
    literais = [
        titulo,
        titulo_do_processo,
        *(o.nome for o in ofertas),
        *(o.localidade for o in ofertas),
    ]
    termos = tuple(sorted({texto for texto in literais if texto and termos_proibidos(texto)}))
    return Ficha(
        modo=modo,
        motivo=motivo,
        edital_id=str(edital.id),
        numero=numero,
        ano=ano,
        identificacao=f"Edital nº {numero}/{ano}",
        titulo=titulo,
        titulo_sem_numero=titulo_sem_numero,
        titulo_do_processo=titulo_do_processo,
        unidade_sigla=unidade,
        referencia=_iso(agora),
        referencia_texto=instante_por_extenso(agora),
        situacao_chave=chave,
        situacao_rotulo=rotulo,
        periodo_estado=periodo.estado,
        inicio=_iso(periodo.inicio),
        fim=_iso(periodo.fim),
        cancelado=periodo.cancelado,
        inicio_data=_data(periodo.inicio),
        inicio_hora=_hora(periodo.inicio),
        fim_data=_data(periodo.fim),
        fim_hora=_hora(periodo.fim),
        periodo_curto=_periodo_curto(periodo.inicio, periodo.fim),
        prorrogado=lida.prorrogado,
        fim_original_texto=termino(lida.termino_original) if lida.prorrogado else "",
        fim_vigente_texto=termino(lida.termino_vigente) if lida.prorrogado else "",
        ofertas=ofertas,
        nomes_iguais=len(ofertas) > 1 and len({o.nome for o in ofertas}) == 1,
        total_de_vagas=total,
        caminho=caminho,
        endereco=endereco,
        caminho_curto=caminho_curto,
        versao_id=str(versao.id),
        versao_hash=versao.content_hash,
        versao_desde=_iso(versao.valid_from),
        versao_desde_texto=instante_por_extenso(versao.valid_from),
        versao_ato=versao_ato,
        retificacao_a_vigorar=_iso(a_vigorar),
        retificacao_a_vigorar_texto=instante_por_extenso(a_vigorar),
        campos=campos,
        impressao=impressao_dos_campos(campos),
        origens=_origens(ctx, conteudo, numeracao),
        termos_em_valor_oficial=termos,
    )


# ---------------------------------------------------------------------------
# O "de → para" da desatualização (`FR-3439`, `FR-3448`)
# ---------------------------------------------------------------------------

ROTULOS_DOS_CAMPOS = {
    "titulo": "título do Edital",
    "titulo_do_processo": "título do Processo",
    "unidade": "unidade",
    "inicio": "início das inscrições",
    "fim": "término das inscrições",
    "caminho": "endereço da página",
}


def _legivel(campo, valor):
    if valor in (None, ""):
        return "—"
    if campo in ("inicio", "fim"):
        from django.utils.dateparse import parse_datetime

        return instante_por_extenso(parse_datetime(valor))
    return str(valor)


def _oferta_legivel(oferta):
    return (
        leitura.quantidade_da_oferta(
            oferta.get("vagas") or 0, "LIMITED" if oferta.get("reserva") else "NONE"
        )
        or "sem vaga nem cadastro reserva"
    )


@dataclass(frozen=True)
class Mudanca:
    campo: str
    de: str
    para: str


@dataclass(frozen=True)
class Desatualizacao:
    exportado_em: str
    mudancas: tuple[Mudanca, ...] = ()
    comparavel: bool = True


def diferencas(antigos, novos):
    """O que mudou entre os campos gravados numa exportação e os de agora: `[Mudanca]`."""
    mudancas = [
        Mudanca(rotulo, _legivel(campo, antigos.get(campo)), _legivel(campo, novos.get(campo)))
        for campo, rotulo in ROTULOS_DOS_CAMPOS.items()
        if antigos.get(campo) != novos.get(campo)
    ]
    if antigos.get("cancelado") != novos.get("cancelado") and novos.get("cancelado"):
        mudancas.append(Mudanca("período de inscrições", "em vigor", "cancelado"))
    if antigos.get("designado") != novos.get("designado"):
        mudancas.append(
            Mudanca(
                "período de inscrições",
                "designado" if antigos.get("designado") else "não designado",
                "designado" if novos.get("designado") else "não designado",
            )
        )
    anteriores = {o["perfil_id"]: o for o in antigos.get("ofertas") or []}
    for oferta in novos.get("ofertas") or []:
        antes = anteriores.pop(oferta["perfil_id"], None)
        rotulo = " — ".join(filter(None, (oferta["nome"], oferta["localidade"])))
        if antes is None:
            mudancas.append(
                Mudanca(f"opção {rotulo}", "—", f"acrescentada: {_oferta_legivel(oferta)}")
            )
            continue
        if (antes["nome"], antes["localidade"]) != (oferta["nome"], oferta["localidade"]):
            anterior = " — ".join(filter(None, (antes["nome"], antes["localidade"])))
            mudancas.append(Mudanca("nome da opção", anterior, rotulo))
        if _oferta_legivel(antes) != _oferta_legivel(oferta):
            mudancas.append(
                Mudanca(f"opção {rotulo}", _oferta_legivel(antes), _oferta_legivel(oferta))
            )
    for antes in anteriores.values():
        rotulo = " — ".join(filter(None, (antes["nome"], antes["localidade"])))
        mudancas.append(Mudanca(f"opção {rotulo}", _oferta_legivel(antes), "retirada"))
    return tuple(mudancas)


def desatualizacoes(exportacoes, ficha, limite=5):
    """As exportações cuja impressão difere da atual, agrupadas pela impressão (`FR-3439`).

    `exportacoes` são os `detalhe` dos eventos, do mais recente ao mais antigo, cada um com
    `exportado_em`. De cada impressão diferente fica a exportação mais recente. Exportação gravada
    com outra versão da impressão é comparada recalculando a impressão dos campos dela; sem campos,
    não é comparável e é dita assim (`FR-3448`).
    """
    vistas, resultado = set(), []
    for registro in exportacoes:
        campos = registro.get("campos")
        versao = registro.get("versao_da_impressao")
        if versao == VERSAO_DA_IMPRESSAO:
            impressao = registro.get("impressao")
        elif isinstance(campos, dict) and set(campos) >= set(ficha.campos):
            impressao = impressao_dos_campos({k: campos[k] for k in ficha.campos})
        else:
            impressao = None
        if impressao == ficha.impressao:
            continue
        chave = impressao or f"incomparavel:{registro.get('impressao')}"
        if chave in vistas:
            continue
        vistas.add(chave)
        if impressao is None:
            resultado.append(Desatualizacao(registro.get("exportado_em", ""), "", comparavel=False))
        else:
            resultado.append(
                Desatualizacao(
                    registro.get("exportado_em", ""), diferencas(campos or {}, ficha.campos)
                )
            )
    return resultado[:limite], max(len(resultado) - limite, 0)
