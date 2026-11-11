"""A projeção da publicação das inscrições — pura, sem banco e sem relógio (148).

**Uma conta, três leituras.** A prévia, a publicação e a divergência chamam a mesma `projetar`: a
prévia mostra o que vai ser publicado, a publicação grava exatamente isso, e a divergência compara o
que foi gravado com o que a mesma conta daria agora. Três funções seriam três chances de a tela
prometer uma lista e o ato publicar outra.

**A situação não se decide aqui** (D-001). Ela é lida do `ResultadoEtapa` vigente da Etapa de
análise — habilitada é deferida, eliminada é indeferida (FR-5410) —, e quem a decidiu foi a Mesa e a
consolidação, com motivo, sob recurso. A homologação sem análise (D-007) é a única que não lê
resultado: ela contempla todas as recebidas, e só é permitida onde não há Etapa que decida.

**A fronteira pública é de construção, e não de filtro** (D-010). O conteúdo público é montado só
com protocolo e nome de quem consta, e a contagem de quem não consta. Motivo, modalidade, CPF e
identificador interno não entram na função que o monta — não há o que esquecer de filtrar.
"""

import unicodedata
from dataclasses import dataclass, field

RECEBIDAS = "RECEBIDAS"
PRELIMINAR = "PRELIMINAR"
HOMOLOGACAO = "HOMOLOGACAO"

RECEBIDA = "RECEBIDA"
DEFERIDA = "DEFERIDA"
INDEFERIDA = "INDEFERIDA"

ROTULOS = {
    RECEBIDAS: "Relação de inscrições recebidas",
    PRELIMINAR: "Resultado preliminar da análise das inscrições",
    HOMOLOGACAO: "Homologação das inscrições",
}

# Como cada natureza chama quem consta e quem não consta — a página, o documento e a gestão leem
# daqui, para que os três não nomeiem a mesma contagem de dois jeitos.
CONSTAM = {
    RECEBIDAS: "Inscrições recebidas",
    PRELIMINAR: "Inscrições deferidas",
    HOMOLOGACAO: "Inscrições homologadas",
}
NAO_CONSTAM = {
    PRELIMINAR: "inscrições indeferidas",
    HOMOLOGACAO: "inscrições não homologadas",
}


@dataclass(frozen=True)
class Item:
    """A situação de uma inscrição no ato — a projeção individual, nunca pública."""

    inscricao_id: str
    situacao: str
    resultado_id: str | None


@dataclass
class Projecao:
    itens: list = field(default_factory=list)
    perfis: list = field(default_factory=list)
    pendentes: int = 0

    @property
    def total(self):
        return len(self.itens)

    @property
    def deferidas(self):
        return sum(1 for item in self.itens if item.situacao in (RECEBIDA, DEFERIDA))

    @property
    def indeferidas(self):
        return sum(1 for item in self.itens if item.situacao == INDEFERIDA)


def chave_de_ordem(nome, protocolo):
    """Nome sem distinção de caixa nem acento, e depois o protocolo (FR-5422).

    É a ordem em que uma pessoa procura o próprio nome numa lista impressa. O protocolo desempata
    homônimos, e é o que torna a ordem determinística — e, com ela, os bytes do ato.
    """
    sem_acento = unicodedata.normalize("NFKD", nome or "")
    sem_acento = "".join(letra for letra in sem_acento if not unicodedata.combining(letra))
    return (sem_acento.casefold().strip(), protocolo or "")


def projetar(*, natureza, inscricoes, resultados, perfis):
    """A projeção de uma natureza sobre as inscrições enviadas.

    - `inscricoes`: dicionários `{id, perfil_id, nome, protocolo}` das **enviadas** do Edital;
    - `resultados`: `{inscricao_id: {"id", "habilitada"}}` dos vigentes da Etapa de análise, ou
      `None` quando a natureza não lê Etapa (recebidas; homologação sem análise);
    - `perfis`: `[(perfil_id, nome)]` na ordem da versão citada.

    A inscrição sem resultado na Etapa conta como **pendente** e fica fora dos itens: a prévia diz
    quantas faltam, e o comando recusa enquanto houver alguma (FR-5411).
    """
    itens, pendentes = [], 0
    por_perfil = {}
    for inscricao in inscricoes:
        identificador = str(inscricao["id"])
        if natureza == RECEBIDAS:
            situacao, origem = RECEBIDA, None
        elif resultados is None:
            situacao, origem = DEFERIDA, None
        else:
            resultado = resultados.get(identificador)
            if resultado is None:
                pendentes += 1
                continue
            situacao = DEFERIDA if resultado["habilitada"] else INDEFERIDA
            origem = str(resultado["id"])
        itens.append(Item(identificador, situacao, origem))
        grupo = por_perfil.setdefault(str(inscricao["perfil_id"]), {"constam": [], "nao": 0})
        if situacao == INDEFERIDA:
            grupo["nao"] += 1
        else:
            grupo["constam"].append(
                {"protocolo": inscricao["protocolo"] or "", "candidato": inscricao["nome"] or ""}
            )

    ordem = [str(perfil_id) for perfil_id, _nome in perfis]
    nomes = {str(perfil_id): nome for perfil_id, nome in perfis}
    # **Todo Perfil da versão aparece, inclusive sem inscrição**: "ninguém se inscreveu" é resposta,
    # e não ausência dela — o precedente da tela de Inscrições (009). Visto na validação, num Edital
    # de dois Perfis em que o segundo sumia do ato.
    for chave in ordem:
        por_perfil.setdefault(chave, {"constam": [], "nao": 0})
    # Perfil que a versão não nomeia vai para o fim, sem nome inventado — não deve acontecer, porque
    # a inscrição nasce num Perfil publicado; se acontecer, a inscrição não desaparece do ato.
    chaves = sorted(por_perfil, key=lambda chave: (ordem.index(chave) if chave in ordem else 10**6))
    grupos = []
    for chave in chaves:
        grupo = por_perfil[chave]
        grupos.append(
            {
                "perfil": nomes.get(chave, ""),
                "constam": sorted(
                    grupo["constam"],
                    key=lambda linha: chave_de_ordem(linha["candidato"], linha["protocolo"]),
                ),
                "nao_constam": grupo["nao"],
            }
        )
    itens.sort(key=lambda item: item.inscricao_id)
    return Projecao(itens=itens, perfis=grupos, pendentes=pendentes)


def conteudo_publico(
    *,
    projecao,
    natureza,
    processo,
    edital,
    etapa,
    prazo,
    publicado_em,
    signatario,
    unidade,
    sucede=None,
):
    """Os bytes do ato — **só** o que se publica (D-010, FR-5419 a FR-5421).

    `etapa` é o nome publicado da Etapa de análise, ou `""`. `prazo` é `None` fora do preliminar,
    `{"admite": False}` quando o Edital não prevê recurso, e `{"admite": True, "evento", "ate"}` com
    o Evento escolhido. `sucede`, quando há: `{"natureza_rotulo", "publicado_em", "motivo"}` — o
    ato anterior dito pelo que ele é, e não por identificador.
    """
    cabecalho = {
        "titulo": ROTULOS[natureza],
        "natureza": natureza,
        "processo": processo,
        "edital": edital,
        "etapa": etapa or "",
        "publicado_em": publicado_em.isoformat(),
        "signatario_nome": signatario.nome,
        "signatario_cargo": signatario.cargo,
        "signatario_ato_de_nomeacao": signatario.ato_de_nomeacao,
        "unidade": {
            "sigla": unidade.sigla,
            "nome": unidade.nome,
            "cabecalho": list(unidade.cabecalho),
        },
    }
    if prazo is not None:
        cabecalho["prazo"] = prazo
    if sucede:
        cabecalho["sucede"] = sucede
    return {
        "cabecalho": cabecalho,
        "rotulo_constam": CONSTAM[natureza],
        "rotulo_nao_constam": NAO_CONSTAM.get(natureza, ""),
        "perfis": projecao.perfis,
        "total": projecao.total,
    }


def divergencia(publicados, atuais):
    """Em quantas inscrições o ato publicado difere da situação de agora (D-006, FR-5427).

    `publicados` e `atuais` são coleções de `Item` (ou de tuplas com os mesmos três campos). Conta
    três coisas, porque cada uma pede uma frase diferente a quem lê: a inscrição que não estava no
    ato, a que estava e saiu, e a que mudou de situação ou de resultado de origem.
    """
    antes = {item.inscricao_id: item for item in publicados}
    agora = {item.inscricao_id: item for item in atuais}
    novas = sorted(set(agora) - set(antes))
    sairam = sorted(set(antes) - set(agora))
    mudadas = sorted(
        chave
        for chave in set(antes) & set(agora)
        if (antes[chave].situacao, antes[chave].resultado_id)
        != (agora[chave].situacao, agora[chave].resultado_id)
    )
    return {
        "novas": len(novas),
        "sairam": len(sairam),
        "mudadas": len(mudadas),
        "total": len(novas) + len(sairam) + len(mudadas),
    }


def regride(anterior, nova):
    """A natureza nova vem antes da do ato vigente? (FR-5405)."""
    ordem = {RECEBIDAS: 0, PRELIMINAR: 1, HOMOLOGACAO: 2}
    return anterior is not None and ordem[nova] < ordem[anterior]


def etapas_de_analise(conteudo):
    """As Etapas que podem ser a análise das inscrições: decisórias **e** eliminatórias (FR-5408).

    Decisória porque a análise produz deferido ou indeferido, e não nota; eliminatória porque o
    indeferimento tira a inscrição do certame — e a consolidação recusa decisória que não elimina.
    """
    return [
        etapa
        for etapa in sorted(conteudo.get("stages") or [], key=lambda item: item.get("order") or 0)
        if etapa.get("forma") == "DECISORIA" and etapa.get("eliminatory")
    ]


def eventos_de_recurso(conteudo, agora):
    """Os Eventos do Cronograma que podem ser o período de recurso: com término ainda por vir.

    Todos os Eventos, e não um tipo: o tipo é texto livre e nada o lê (D-002). Quem publica escolhe;
    o término passado é recusado porque publicar com prazo vencido suprimiria o recurso (FR-5414).
    """
    from django.utils.dateparse import parse_datetime

    elegiveis = []
    for evento in conteudo.get("schedule") or []:
        if not isinstance(evento, dict) or evento.get("isRegistrationPeriod"):
            continue
        if evento.get("status") == "CANCELADO":
            continue
        fim = parse_datetime(evento.get("endAt") or "") if evento.get("endAt") else None
        if fim is None or fim < agora:
            continue
        elegiveis.append(
            {
                "id": str(evento.get("id")),
                "nome": evento.get("description") or evento.get("type") or "",
                "fim": fim,
            }
        )
    return sorted(elegiveis, key=lambda item: item["fim"])


__all__ = [
    "CONSTAM",
    "DEFERIDA",
    "HOMOLOGACAO",
    "INDEFERIDA",
    "Item",
    "NAO_CONSTAM",
    "PRELIMINAR",
    "Projecao",
    "RECEBIDA",
    "RECEBIDAS",
    "ROTULOS",
    "chave_de_ordem",
    "conteudo_publico",
    "divergencia",
    "etapas_de_analise",
    "eventos_de_recurso",
    "projetar",
    "regride",
]
