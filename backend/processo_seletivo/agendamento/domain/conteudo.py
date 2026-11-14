"""O conteúdo público da agenda: por dia, por horário, e só o que a FR-7225 permite (167, T-014).

**Uma função para três lugares**: a conferência a chama para a prévia da página pública; a
publicação, para os bytes canônicos do ato; e a página pública mostra o cabeçalho que ela compôs.
A prévia é igual ao que a página mostrará porque as duas saem daqui (FR-7222).

**O que não está na entrada não pode vazar na saída.** A função recebe nome e protocolo de cada
pessoa, e o nome e o local de cada banca — nunca o endereço da sala, o CPF, o e-mail, o telefone, a
Modalidade ou o desfecho (FR-7226). O endereço da sala e o local presencial moram no mesmo campo da
banca (`acesso`), e por isso quem chama passa o `acesso` e a forma, e é esta função que decide: na
forma remota o local sai vazio, sempre.

**Na Etapa restrita por Modalidade, a pessoa é só o protocolo** (`D-009`): a agenda dela é, por
construção, a lista de quem concorre pela reserva; com o nome, publicaria a autodeclaração.
"""

from dataclasses import dataclass
from datetime import UTC

from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.domain.horarios import zona

VERSAO = 1


@dataclass(frozen=True)
class Item:
    """Uma pessoa num horário, com o que o conteúdo público pode levar dela."""

    inicio: object
    fim: object
    banca: str
    nome: str
    protocolo: str


def identificacao(restrita: bool) -> str:
    return nomes.PROTOCOLO if restrita else nomes.NOME_E_PROTOCOLO


def _instante(valor):
    """O instante em UTC, como texto: a forma canônica não depende da zona de quem compõe."""
    return valor.astimezone(UTC).isoformat() if valor is not None else None


def compor(
    *,
    unidade,
    edital,
    etapa,
    publicado_em,
    signatario,
    veiculo,
    forma,
    duracao,
    bancas,
    itens,
    restrita,
):
    """O conteúdo público, como valor que `canonical_bytes` serializa.

    `unidade` é `{"cabecalho", "local", "sigla", "nome"}`; `signatario` é `{"nome", "cargo",
    "atoDeNomeacao"}` ou `None` na prévia, que não é ato e não tem quem assine; `bancas` é
    `[(nome, acesso), …]` na ordem; `itens` é `[Item, …]`, em qualquer ordem.
    """
    modo = identificacao(restrita)
    varias = len(bancas) > 1
    presencial = forma == nomes.PRESENCIAL
    dias = {}
    for item in sorted(itens, key=lambda i: (i.inicio, _ordem(bancas, i.banca), i.protocolo)):
        pessoa = {"protocolo": item.protocolo}
        if modo == nomes.NOME_E_PROTOCOLO:
            pessoa["nome"] = item.nome
        horario = {"inicio": _instante(item.inicio), "fim": _instante(item.fim), "pessoa": pessoa}
        if varias:
            horario["banca"] = item.banca
        dia = item.inicio.astimezone(zona()).date().isoformat()
        dias.setdefault(dia, []).append(horario)
    return {
        "versao": VERSAO,
        "cabecalho": {
            "unidade": {
                "cabecalho": list((unidade or {}).get("cabecalho") or []),
                "local": (unidade or {}).get("local", ""),
                "sigla": (unidade or {}).get("sigla", ""),
                "nome": (unidade or {}).get("nome", ""),
            },
            "edital": edital,
            "etapa": etapa,
            "publicadoEm": _instante(publicado_em),
            "signatario": signatario,
            "veiculo": veiculo,
            "forma": forma,
            "duracao": duracao,
            "identificacao": modo,
        },
        "bancas": [
            {"nome": nome, "local": (acesso or "").strip() if presencial else ""}
            for nome, acesso in bancas
        ],
        "dias": [{"dia": dia, "horarios": horarios} for dia, horarios in sorted(dias.items())],
    }


def _ordem(bancas, nome):
    for posicao, (banca, _acesso) in enumerate(bancas):
        if banca == nome:
            return posicao
    return len(bancas)
