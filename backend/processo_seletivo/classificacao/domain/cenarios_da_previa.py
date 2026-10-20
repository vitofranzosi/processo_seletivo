"""Os candidatos fictícios da prévia da classificação (094, D-003).

Função pura, como o resto do domínio da classificação: recebe as Etapas que o marco enumera, os
fatos declarados do Perfil e as fronteiras, e devolve inscritos na forma que
`universo_classificavel.preparar` recebe — a mesma que o caminho oficial monta a partir do banco.
É o que deixa a prévia passar pelo motor oficial sem uma segunda montagem do universo.

**Dois modos, no mesmo seletor** (D-003, revista na segunda rodada):

- **A população estável** é o padrão: montada uma vez, com as fronteiras do momento em que o
  painel abriu, e mantida enquanto ele estiver aberto. Alterar a regra não refaz ninguém, e é isso
  que deixa ver o efeito da regra sobre as mesmas pessoas.
- **Os casos-limite** são demonstração dirigida: cada um planta a situação que o nomeia sobre a
  fronteira de agora, e por isso se refaz junto com alvo, suplentes e vagas.

**Nada aqui é acaso.** Os mesmos argumentos dão os mesmos candidatos, sempre: sem relógio, sem
`random`, sem `uuid4`. Pesos, operação, critérios, desfecho, Etapa governada e continuação não são
argumentos, e por isso não mudam ninguém (FR-2205).

**Os nomes são fictícios e não identificam ninguém.** Os identificadores são `F000`, `F001`…, que
não têm a forma de UUID nem de protocolo, para que nenhum deles se confunda com inscrição real
(FR-2204).
"""

import datetime
from decimal import Decimal

from processo_seletivo.classificacao.domain.universo_classificavel import ELIMINADA, HABILITADA

DECISORIA = "DECISORIA"
DATA, INTEIRO = "DATA", "INTEIRO"

#: O teto da população. Cobre a faixa de 500 da SC-841 com folga para as âncoras.
TETO = 600

#: Quantas Etapas com nota os candidatos sabem receber (spec, Assumptions; R-006).
ETAPAS_COM_NOTA = 4

#: Os casos-limite: `chave → (rótulo, o que mostra)`. A população estável não está aqui: ela é o
#: padrão, e não um caso.
CASOS = {
    "sem_empate": (
        "Classificação sem empate",
        "Pontuações distintas para todos: nenhum critério de desempate é usado.",
    ),
    "criterios_sucessivos": (
        "Desempate por critérios sucessivos",
        "Três candidatos com as mesmas notas em todas as Etapas, perto do fim do alvo. Diferem só "
        "nos fatos: um tem a menor data, e os outros dois diferem no número.",
    ),
    "empate_na_faixa": (
        "Corte impedido: empate na última posição da faixa",
        "Dois candidatos iguais em tudo — notas e fatos —, na última posição de alvo + "
        "suplentes. Um cabe na faixa pela contagem, o outro não.",
    ),
    "empate_nas_vagas": (
        "Empate na fronteira das vagas",
        "Dois candidatos iguais em tudo na última posição das vagas do quadro. Com suplentes, o "
        "empate fica dentro da faixa: o corte sai, e é a apuração das vagas que para.",
    ),
    "valor_ausente": (
        "Valor ausente",
        "Uma candidata sem nota numa Etapa enumerada, um candidato eliminado na Etapa do marco, e "
        "dois empatados na pontuação em que um deles não tem o fato de data.",
    ),
}

_NOMES = (
    "Alice Bruno Carla Diego Elisa Fábio Gabriela Heitor Íris João Karina Lucas Marina Nuno "
    "Olívia Paulo Quitéria Rafael Sofia Tiago Úrsula Vítor Wanda Xavier Yara Zeca"
).split()


def _nome(slot):
    base = _NOMES[slot % len(_NOMES)]
    volta = slot // len(_NOMES)
    return base if volta == 0 else f"{base} {volta + 1}"


def _nota(slot, total):
    """Notas inteiras e distintas enquanto couberem; com mais gente, duas casas.

    **A mesma nota em toda Etapa com nota**, de propósito: com ela, a ordem pela pontuação combinada
    não depende de peso nem de operação, e quem não está plantado num empate não muda de lugar
    quando o elaborador mexe na combinação (R-005).
    """
    if total <= 90:
        return Decimal(95 - slot)
    passo = Decimal(90) / Decimal(total)
    return (Decimal(95) - passo * slot).quantize(Decimal("0.01"))


def _valor_do_fato(fato, posicao_no_tipo, slot):
    """Um valor distinto por candidato, e por fato do mesmo tipo."""
    if fato.get("type") == DATA:
        return datetime.date(1965, 1, 1) + datetime.timedelta(
            days=211 * slot + 13 * posicao_no_tipo
        )
    return 12 + (slot * 7 + posicao_no_tipo * 3) % 97


def _candidatos_base(total, notas, portas, fatos):
    por_tipo = {}
    posicoes = []
    for fato in fatos:
        tipo = fato.get("type")
        posicoes.append(por_tipo.get(tipo, 0))
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
    return [
        {
            "slot": slot,
            "nome": _nome(slot),
            "notas": {etapa["id"]: _nota(slot, total) for etapa in notas},
            "portas": [etapa["id"] for etapa in portas],
            "eliminado_em": None,
            "fatos": {
                str(fato["id"]): _valor_do_fato(fato, posicao, slot)
                for fato, posicao in zip(fatos, posicoes, strict=True)
            },
        }
        for slot in range(total)
    ]


def _igualar(candidatos, destino, origem, *, fatos=True):
    candidatos[destino]["notas"] = dict(candidatos[origem]["notas"])
    if fatos:
        candidatos[destino]["fatos"] = dict(candidatos[origem]["fatos"])


def _trio(candidatos, inicio, fatos):
    """Três com as mesmas notas, separáveis só pelos fatos: menor data num, número no outro par."""
    for slot in (inicio + 1, inicio + 2):
        candidatos[slot]["notas"] = dict(candidatos[inicio]["notas"])
    x, y, z = (candidatos[inicio + i]["fatos"] for i in range(3))
    for fato in fatos:
        chave = str(fato["id"])
        if fato.get("type") == DATA:
            x[chave] = datetime.date(1961, 5, 4)
            y[chave] = z[chave] = datetime.date(1979, 8, 19)
        else:
            x[chave] = 40
            y[chave], z[chave] = 84, 60


def _separar(etapas_enumeradas):
    notas = [e for e in etapas_enumeradas if e.get("forma") != DECISORIA]
    portas = [e for e in etapas_enumeradas if e.get("forma") == DECISORIA]
    return notas, portas


def populacao_estavel(*, etapas_enumeradas, etapa_do_marco, fatos, alvo, faixa, vagas):
    """A população padrão, montada com as fronteiras **da montagem** (D-003).

    `alvo`, `faixa` e `vagas` são os do momento em que o painel abriu, e viajam nele: alterar a
    regra depois não refaz ninguém. Já traz o que costuma importar — um empate residual na última
    vaga (ou no alvo, sem quadro), outro na última posição da faixa, um trio que só os fatos
    separam, uma candidata sem nota e um candidato eliminado; os dois últimos ficam no fim da
    lista, e por isso não deslocam as posições plantadas.

    Devolve `(candidatos, plantados)`, onde `plantados` diz em palavras o que foi plantado e onde.
    """
    referencia = max(faixa or 0, vagas or 0, alvo or 0, 12)
    total = min(referencia + 6, TETO)
    notas, portas = _separar(etapas_enumeradas)
    candidatos = _candidatos_base(total, notas, portas, fatos)
    ocupados, plantados = set(), []

    def par(ultima, rotulo):
        # Os slots `ultima - 1` e `ultima` dividem a posição `ultima`. Um slot de folga para cada
        # lado, para que dois empates não se fundam num só.
        if not ultima or ultima < 2 or ultima >= total - 1:
            return
        if {ultima - 2, ultima - 1, ultima, ultima + 1} & ocupados:
            return
        _igualar(candidatos, ultima, ultima - 1)
        ocupados.update({ultima - 1, ultima})
        plantados.append(f"empate de dois na {ultima}ª posição ({rotulo})")

    par(vagas or alvo, "última vaga" if vagas else "último do alvo")
    if faixa and faixa != (vagas or alvo):
        par(faixa, "última da faixa")
    for inicio in range(2, total - 3):
        if not {inicio - 1, inicio, inicio + 1, inicio + 2, inicio + 3} & ocupados:
            _trio(candidatos, inicio, fatos)
            plantados.append(f"trio que só os fatos separam, a partir da {inicio + 1}ª posição")
            break
    extras = _candidatos_base(total + 2, notas, portas, fatos)[total:]
    for extra, nota in zip(extras, (Decimal(96), Decimal(94)), strict=True):
        # Notas altas de propósito: "teria ficado entre os primeiros", e não ficou.
        extra["notas"] = {etapa["id"]: nota for etapa in notas}
    if notas:
        extras[0]["notas"][notas[-1]["id"]] = None
    if etapa_do_marco is not None:
        extras[1]["eliminado_em"] = etapa_do_marco["id"]
    return candidatos + extras, plantados


def caso_limite(chave, *, etapas_enumeradas, etapa_do_marco, fatos, alvo, suplentes, vagas, corta):
    """O caso-limite `chave`, plantado sobre a fronteira de agora. `(candidatos, onde)`."""
    faixa = (alvo or 0) + (suplentes or 0) if corta else 0
    referencia = max(faixa, vagas or 0, alvo or 0, 8)
    total = min(referencia + 4, TETO)
    notas, portas = _separar(etapas_enumeradas)
    candidatos = _candidatos_base(total, notas, portas, fatos)
    onde = None
    if chave == "criterios_sucessivos":
        primeiro = max(min((alvo or 6) - 2, total - 4), 0)
        _trio(candidatos, primeiro, fatos)
        onde = f"o trio começa na {primeiro + 1}ª posição"
    elif chave == "empate_na_faixa":
        ultima = max(min(faixa if corta and faixa else 5, total - 1), 1)
        _igualar(candidatos, ultima, ultima - 1)
        onde = (
            f"o empate fica na {ultima}ª posição, a última da faixa"
            if corta and faixa
            else "sem regra de corte, o empate fica na 5ª posição"
        )
    elif chave == "empate_nas_vagas":
        ultima = max(min(vagas or alvo or 5, total - 1), 1)
        _igualar(candidatos, ultima, ultima - 1)
        onde = (
            f"o empate fica na {ultima}ª posição, a última das vagas"
            if vagas
            else "sem quadro de vagas, o empate fica na posição do alvo"
        )
    elif chave == "valor_ausente":
        if notas:
            candidatos[1]["notas"][notas[-1]["id"]] = None
        if etapa_do_marco is not None:
            candidatos[3]["eliminado_em"] = etapa_do_marco["id"]
        _igualar(candidatos, 6, 5, fatos=False)
        alvo_do_ausente = next(
            (f for f in fatos if f.get("type") == DATA), fatos[0] if fatos else None
        )
        if alvo_do_ausente is not None:
            candidatos[6]["fatos"].pop(str(alvo_do_ausente["id"]), None)
        onde = "as ausências ficam na 2ª, na 4ª e na 7ª linha"
    return candidatos, onde


def inscritos(candidatos):
    """Os candidatos na forma de `universo_classificavel.preparar` — a do caminho oficial."""

    def consequencia(candidato, etapa_id):
        return ELIMINADA if candidato["eliminado_em"] == etapa_id else HABILITADA

    def motivo(candidato, etapa_id):
        return (
            "Eliminado na Etapa do marco (fictício)."
            if candidato["eliminado_em"] == etapa_id
            else ""
        )

    saida = []
    for c in candidatos:
        resultados = [
            {
                "id": f"R{c['slot']:03d}-{etapa_id}",
                "etapa_id": etapa_id,
                "pontuacao": nota,
                "consequencia": consequencia(c, etapa_id),
                "motivo": motivo(c, etapa_id),
            }
            for etapa_id, nota in c["notas"].items()
            if nota is not None or c["eliminado_em"] == etapa_id
        ] + [
            {
                "id": f"R{c['slot']:03d}-{etapa_id}",
                "etapa_id": etapa_id,
                "pontuacao": None,
                "consequencia": consequencia(c, etapa_id),
                "motivo": motivo(c, etapa_id),
            }
            for etapa_id in c["portas"]
        ]
        saida.append(
            {
                "inscricao_id": f"F{c['slot']:03d}",
                "protocolo": f"FICTICIO-{c['slot']:03d}",
                "nome": c["nome"],
                "identity_subject": "",
                # A porta da fatia 2: a Modalidade do candidato fictício. Nula em toda a fatia 1,
                # que é o universo inteiro (D-008 da 094).
                "modalidade_id": None,
                "fatos": c["fatos"],
                "resultados": resultados,
            }
        )
    return saida


__all__ = [
    "CASOS",
    "ETAPAS_COM_NOTA",
    "TETO",
    "caso_limite",
    "inscritos",
    "populacao_estavel",
]
