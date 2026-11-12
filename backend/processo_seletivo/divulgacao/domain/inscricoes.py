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
com protocolo e nome de quem consta, e a contagem de quem não consta. Motivo, CPF e identificador
interno não entram na função que o monta — não há o que esquecer de filtrar.

**A Modalidade entra, mas só como lista** (revisão de 12/11, D-011). O Perfil se reparte nas listas
de concorrência que a versão declara — a ampla com todos, cada reservada com quem a declarou —, e a
linha continua com duas chaves. Quem lê o ato sabe a Modalidade de alguém pela lista em que o nome
está, como nas listas que o Ifes publica; nenhuma coluna a repete.
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

# O nome público da ampla, **um só** para a relação das inscrições e para a divulgação do resultado
# (`conteudo.nome_da_lista` o importa daqui) — e não o rótulo de gestão dos recortes, que fala em
# "linha geral do quadro" para quem opera (FR-5440). Mora neste módulo porque ele é puro.
AMPLA_CONCORRENCIA = "Ampla concorrência"

# A frase que explica por que o mesmo nome aparece duas vezes (FR-5446). Sem ela, o cotista que se
# encontra na ampla e na PPI lê duplicidade onde há concorrência concomitante.
FRASE_DAS_LISTAS = (
    "Quem se inscreveu para vaga reservada consta também na ampla concorrência, porque concorre "
    "nas duas."
)


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


def nomes_das_listas(modalidades):
    """O nome público de cada lista reservada de um Perfil — `[(modalidade_id, nome)]` (FR-5440a).

    `modalidades` vem na ordem dos recortes, como `[(modalidade_id, nome, codigo)]`. Três regras,
    e cada uma fecha um caminho pelo qual o ato publicaria o que não deve:

    - **o nome publicado da Modalidade**, como a divulgação do resultado o diz;
    - **o código quando falta o nome** — o Edital do acervo publicado antes da validação de nome.
      O rótulo de gestão dos recortes cai no UUID nesse caso, e o UUID é identificador interno
      (FR-5421) num ato que não se corrige;
    - **o código entre parênteses quando o nome repete o de outra lista do Perfil**, inclusive o
      da ampla. Um Edital que declara uma Modalidade "Ampla concorrência" sem apontá-la como a
      ampla — o acervo anterior à `122` — teria duas listas "Ampla concorrência", uma com todos e
      outra com quem a declarou: os "dois blocos homônimos" que a `021` corrigiu na gestão.

    A comparação ignora caixa e acento, pela mesma chave da ordem dos nomes: "AMPLA CONCORRENCIA"
    e "Ampla concorrência" são o mesmo título para quem lê.
    """
    usados = {chave_de_ordem(AMPLA_CONCORRENCIA, "")[0]}
    nomes = []
    for posicao, (modalidade_id, nome, codigo) in enumerate(modalidades, start=1):
        nome, codigo = (nome or "").strip(), (codigo or "").strip()
        publico = nome or codigo or f"Lista reservada {posicao}"
        if chave_de_ordem(publico, "")[0] in usados:
            publico = f"{publico} ({codigo})" if codigo else f"{publico} ({posicao})"
        usados.add(chave_de_ordem(publico, "")[0])
        nomes.append((str(modalidade_id), publico))
    return nomes


def projetar(*, natureza, inscricoes, resultados, perfis, listas=None):
    """A projeção de uma natureza sobre as inscrições enviadas.

    - `inscricoes`: dicionários `{id, perfil_id, nome, protocolo}` das **enviadas** do Edital, com
      `modalidade_id` quando a inscrição declarou uma;
    - `resultados`: `{inscricao_id: {"id", "habilitada"}}` dos vigentes da Etapa de análise, ou
      `None` quando a natureza não lê Etapa (recebidas; homologação sem análise);
    - `perfis`: `[(perfil_id, nome)]` na ordem da versão citada;
    - `listas`: `{perfil_id: [(modalidade_id, nome)]}` — as listas **reservadas** de cada Perfil,
      na ordem dos recortes. A ampla não vem aqui porque todo Perfil a tem (FR-5439, FR-5440).

    A inscrição sem resultado na Etapa conta como **pendente** e fica fora dos itens: a prévia diz
    quantas faltam, e o comando recusa enquanto houver alguma (FR-5411).

    **O item é por inscrição, e a lista é só do grupo** (FR-5444). O cotista entra uma vez em
    `itens` — que é o que vira linha gravada, assinatura e divergência — e duas vezes nos grupos.
    """
    listas = listas or {}
    # As reservadas dependem só do Perfil: um conjunto por Perfil, e não um por inscrição.
    reservadas_do_perfil = {
        str(perfil_id): {str(lista_id) for lista_id, _nome in declaradas}
        for perfil_id, declaradas in listas.items()
    }
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
        perfil_id = str(inscricao["perfil_id"])
        grupo = por_perfil.setdefault(perfil_id, {})
        # A ampla recebe todos; a reservada, quem a declarou — se ela for lista **nesta** versão.
        # A Modalidade apontada como a ampla, ou uma que a versão não declara, não está em
        # `listas`, e a inscrição fica só na ampla (FR-5441).
        modalidade = str(inscricao.get("modalidade_id") or "")
        reservada = modalidade in reservadas_do_perfil.get(perfil_id, ())
        destinos = [None, *([modalidade] if reservada else [])]
        for destino in destinos:
            lista = grupo.setdefault(destino, {"constam": [], "nao": 0})
            if situacao == INDEFERIDA:
                lista["nao"] += 1
            else:
                lista["constam"].append(
                    {
                        "protocolo": inscricao["protocolo"] or "",
                        "candidato": inscricao["nome"] or "",
                    }
                )

    ordem = [str(perfil_id) for perfil_id, _nome in perfis]
    nomes = {str(perfil_id): nome for perfil_id, nome in perfis}
    # **Todo Perfil da versão aparece, inclusive sem inscrição**: "ninguém se inscreveu" é resposta,
    # e não ausência dela — o precedente da tela de Inscrições (009). Visto na validação, num Edital
    # de dois Perfis em que o segundo sumia do ato. A mesma regra vale para a lista (FR-5440).
    for chave in ordem:
        por_perfil.setdefault(chave, {})
    # Perfil que a versão não nomeia vai para o fim, sem nome inventado — não deve acontecer, porque
    # a inscrição nasce num Perfil publicado; se acontecer, a inscrição não desaparece do ato.
    chaves = sorted(por_perfil, key=lambda chave: (ordem.index(chave) if chave in ordem else 10**6))
    grupos = []
    for chave in chaves:
        grupo = por_perfil[chave]
        declaradas = [(None, AMPLA_CONCORRENCIA)] + [
            (str(lista_id), nome) for lista_id, nome in listas.get(chave, [])
        ]
        grupos.append(
            {
                "perfil": nomes.get(chave, ""),
                "listas": [
                    _lista(nome, grupo.get(lista_id) or {"constam": [], "nao": 0})
                    for lista_id, nome in declaradas
                ],
            }
        )
    itens.sort(key=lambda item: item.inscricao_id)
    return Projecao(itens=itens, perfis=grupos, pendentes=pendentes)


def _lista(nome, acumulado):
    return {
        "lista": nome,
        "constam": sorted(
            acumulado["constam"],
            key=lambda linha: chave_de_ordem(linha["candidato"], linha["protocolo"]),
        ),
        "nao_constam": acumulado["nao"],
    }


def grupos_publicados(conteudo):
    """Os Perfis do ato com as listas, nos dois formatos que os bytes gravados podem ter.

    **O ato publicado antes da revisão de 12/11 não tem lista**, e continua como foi publicado
    (FR-5447): o Perfil leva `constam` e `nao_constam` direto. A leitura o apresenta como uma lista
    sem nome, e a página e o documento omitem o título que não existe — não inventam "Ampla
    concorrência" num ato que não a declarou. Reescrever os bytes para o formato novo é o que a
    imutabilidade proíbe, e regenerar o PDF mudaria o resumo que a comissão conferiu.
    """
    grupos = []
    for grupo in conteudo.get("perfis") or []:
        if "listas" in grupo:
            listas = grupo["listas"]
        else:
            listas = [
                {
                    "lista": "",
                    "constam": grupo.get("constam") or [],
                    "nao_constam": grupo.get("nao_constam") or 0,
                }
            ]
        grupos.append({"perfil": grupo.get("perfil") or "", "listas": listas})
    return grupos


def tem_lista_reservada(grupos):
    """Algum Perfil tem lista além da ampla? É quando a frase das listas tem o que explicar."""
    return any(len(grupo["listas"]) > 1 for grupo in grupos)


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
    "AMPLA_CONCORRENCIA",
    "CONSTAM",
    "DEFERIDA",
    "FRASE_DAS_LISTAS",
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
    "grupos_publicados",
    "nomes_das_listas",
    "projetar",
    "regride",
    "tem_lista_reservada",
]
