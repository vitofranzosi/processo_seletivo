"""As leituras da publicação de convocados: a seção da seleção, a página e o candidato (148).

**Tudo o que o ato afirma sai dos bytes congelados** (FR-5419, D-005). O que se lê do banco, fora
deles, é só o que acontece **depois** do ato e não o altera: que uma convocação dele foi corrigida
numa publicação posterior (FR-5420). Essa leitura vai ao lado do conteúdo, nunca dentro dele, e o
documento PDF não a tem.

**Consultas fixas** (FR-5436): a seção lê as publicações do Edital numa consulta; a página, o ato,
os vínculos dele, os posteriores e a cadeia do Edital — uma cada, qualquer que seja o número de
pessoas.
"""

import json

from processo_seletivo.convocacao.domain import publicacao as dominio
from processo_seletivo.convocacao.models import (
    Convocacao,
    ConvocacaoPublicada,
    PublicacaoDeConvocados,
)

#: Quantas publicações a seção mostra antes de recolher as anteriores (FR-5421).
A_VISTA = 3


def conteudo_de(ato):
    return json.loads(bytes(ato.conteudo_publico).decode("utf-8"))


def _resumo(ato):
    """Uma publicação na seção: o que a linha diz, sem a relação (D-007)."""
    conteudo = conteudo_de(ato)
    grupos = conteudo["grupos"]
    vencimentos = {pessoa["vencimento"] for grupo in grupos for pessoa in grupo["pessoas"]}
    vagas = []
    for grupo in grupos:
        if grupo["perfil"] not in vagas:
            vagas.append(grupo["perfil"])
    return {
        "ato": ato,
        "id": ato.id,
        "numero": ato.numero,
        "titulo": dominio.titulo(ato.numero),
        "publicada_em": ato.publicado_em,
        "natureza": dominio.natureza(grupos),
        "pessoas": sum(len(grupo["pessoas"]) for grupo in grupos),
        "vagas": vagas,
        # O prazo só quando é um só, e nunca "vários prazos" inventado: a página diz cada um.
        "prazo": (
            dominio.instante(next(iter(vencimentos)))
            if len(vencimentos) == 1 and None not in vencimentos
            else None
        ),
        "traz_correcao": any(p["corrige"] for grupo in grupos for p in grupo["pessoas"]),
    }


def publicacoes_da_selecao(edital_id):
    """As publicações de convocados do Edital, da mais recente para a mais antiga (FR-5421).

    Devolve `{"recentes": [...], "anteriores": [...]}`, ou `None` sem publicação — e então a seção
    não aparece (FR-5423).
    """
    atos = list(PublicacaoDeConvocados.objects.filter(edital_id=edital_id).order_by("-numero"))
    if not atos:
        return None
    resumos = [_resumo(ato) for ato in atos]
    return {"recentes": resumos[:A_VISTA], "anteriores": resumos[A_VISTA:]}


def publicacao_publica(publicacao_id):
    """O ato para a página pública, ou `None` (FR-5418, FR-5419, FR-5420)."""
    ato = PublicacaoDeConvocados.objects.filter(id=publicacao_id).select_related("edital").first()
    if ato is None:
        return None
    conteudo = conteudo_de(ato)
    corrigidas = _corrigidas_depois(ato)
    grupos = []
    for grupo in conteudo["grupos"]:
        pessoas = [
            {
                **pessoa,
                "prazo": dominio.instante(pessoa["vencimento"]),
                "corrigida_na": corrigidas.get(pessoa["protocolo"]),
            }
            for pessoa in grupo["pessoas"]
        ]
        grupos.append(
            {
                **grupo,
                "pessoas": pessoas,
                "prazo": dominio.instante(grupo["vencimento"]),
                "nota": dominio.nota_do_grupo(grupo),
                "com_correcao": any(p["corrige"] for p in pessoas),
            }
        )
    cabecalho = conteudo["cabecalho"]
    outras = list(
        PublicacaoDeConvocados.objects.filter(edital_id=ato.edital_id)
        .exclude(id=ato.id)
        .order_by("-numero")
        .values("id", "numero", "publicado_em")
    )
    return {
        "ato": ato,
        "cabecalho": cabecalho,
        "publicada_em": dominio.instante(cabecalho["publicadoEm"]),
        "grupos": grupos,
        "pessoas": sum(len(g["pessoas"]) for g in grupos),
        "natureza": dominio.natureza(conteudo["grupos"]),
        "orientacoes": dominio.orientacoes(
            requerimento_na_convocacao=cabecalho.get("requerimentoNaConvocacao", False)
        ),
        # As publicações posteriores que corrigiram alguém desta, para o aviso do topo.
        "corrigidas": _publicacoes_que_corrigem(corrigidas),
        "outras": [{**outra, "titulo": dominio.titulo(outra["numero"])} for outra in outras],
    }


def _publicacoes_que_corrigem(corrigidas):
    vistas = {}
    for publicacao in corrigidas.values():
        vistas[publicacao["id"]] = publicacao
    return sorted(vistas.values(), key=lambda publicacao: publicacao["numero"])


def _corrigidas_depois(ato):
    """`{protocolo: {"id", "numero", "titulo"}}` — quem desta publicação foi corrigido depois.

    **Leitura da cadeia, fora do ato** (D-006): uma convocação desta publicação foi sucedida, e a
    sucessora — ou a sucessora dela — saiu numa publicação posterior. O protocolo é a chave porque é
    o que a linha pública tem: o conteúdo não guarda identificador interno (D-008).
    """
    desta = dict(
        ConvocacaoPublicada.objects.filter(publicacao=ato).values_list(
            "convocacao_id", "convocacao__inscricao__protocolo"
        )
    )
    posteriores = {
        linha["convocacao_id"]: linha
        for linha in ConvocacaoPublicada.objects.filter(
            publicacao__edital_id=ato.edital_id, publicacao__numero__gt=ato.numero
        )
        .order_by("publicacao__numero")
        .values("convocacao_id", "publicacao_id", "publicacao__numero")
    }
    if not posteriores:
        return {}
    anterior_de = dict(
        Convocacao.objects.filter(edital_id=ato.edital_id).values_list(
            "id", "convocacao_anterior_id"
        )
    )
    corrigidas = {}
    for convocacao_id, linha in posteriores.items():
        elo = anterior_de.get(convocacao_id)
        while elo is not None:
            if elo in desta:
                protocolo = desta[elo]
                numero = linha["publicacao__numero"]
                if protocolo not in corrigidas or numero > corrigidas[protocolo]["numero"]:
                    corrigidas[protocolo] = {
                        "id": linha["publicacao_id"],
                        "numero": numero,
                        "titulo": dominio.titulo(numero),
                    }
                break
            elo = anterior_de.get(elo)
    return corrigidas


def publicacao_da_convocacao(convocacao):
    """A publicação do GPS que **convocou** esta convocação, ou `None` (FR-5425).

    Só o *convoca*: o *"Publicada em"* do candidato fala do ato oficial, e a relação informativa
    que espelhou uma publicação externa não é onde a convocação dele foi publicada.
    """
    vinculo = (
        ConvocacaoPublicada.objects.filter(
            convocacao=convocacao, efeito=ConvocacaoPublicada.Efeito.CONVOCA
        )
        .select_related("publicacao")
        .first()
    )
    return vinculo.publicacao if vinculo else None


__all__ = [
    "A_VISTA",
    "conteudo_de",
    "publicacao_da_convocacao",
    "publicacao_publica",
    "publicacoes_da_selecao",
]
