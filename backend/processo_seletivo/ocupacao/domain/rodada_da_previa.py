"""A rodada de ocupação da prévia da classificação: uma apuração por recorte, sem gravar (095).

**Nenhuma regra própria.** Cada número sai das funções que a emissão da apuração chama:
`apuracao.apurar`, `apuracao.ocupantes_pela_ampla`, `reversao.ha_quem_ocupar` e
`reversao.quantidade_a_reverter`. O que este módulo faz é a **ordem** em que um conduzente
apuraria os recortes de um marco, e só uma vez (D-002): a ampla com as vagas publicadas, cada
reservada sem quem ocupa pela ampla, e a reversão de cada reservada.

**Uma rodada, e não o ponto fixo.** No produto, a vaga cedida grava um movimento, a apuração da
ampla passa a aparecer obsoleta, e quem quiser o número novo emite de novo — ninguém refaz a cadeia
sozinho (`causas_de_obsolescencia`). Refazer aqui a ampla com as vagas recebidas inventaria uma
orquestração que o sistema não tem; por isso a rodada diz quantas efetivas a próxima apuração da
ampla leria, e para.

**As hipóteses são da prévia, e entram como dados**: todos os que avançaram estão habilitados,
nenhum movimento nem efeito anterior existe. É o que torna a apuração calculável na composição, onde
nada disso aconteceu ainda.

Mora na `ocupacao` porque a decisão é dela; a `classificacao` não importa este módulo, e quem liga
os dois é a interface (`tests/test_dependencia_da_ocupacao.py`).
"""

from processo_seletivo.ocupacao.domain import apuracao, reversao

AVALIADA = "avaliada"
SEM_LINHA = "sem_linha"
CORTE_NAO_EMITIDO = "corte_nao_emitido"
PAROU_NA_FRONTEIRA = "parou_na_fronteira"
DEPENDE_DA_AMPLA = "depende_da_ampla"


def _nao_avaliada(estado, **detalhe):
    return {"estado": estado, **detalhe}


def _ampla(entrada):
    if entrada["vagas"] is None:
        return _nao_avaliada(SEM_LINHA), None
    if entrada["impedido"]:
        return _nao_avaliada(CORTE_NAO_EMITIDO), None
    progrediram = list(entrada["progrediram"])
    try:
        publicadas, efetivas, ocupadas = apuracao.apurar(
            publicadas=entrada["vagas"],
            progrediram_em_ordem=progrediram,
            habilitadas=progrediram,
            empates_residuais=entrada["empates"],
        )
    except apuracao.EmpateNaFronteiraDoAlvo as erro:
        return _nao_avaliada(PAROU_NA_FRONTEIRA, posicao=erro.posicao, quantas=erro.quantas), None
    # A mesma conta que a reservada subtrai no caminho oficial, com as mesmas entradas.
    ocupantes = apuracao.ocupantes_pela_ampla(
        progrediram_em_ordem=progrediram,
        publicadas=entrada["vagas"],
        empates_residuais=entrada["empates"],
        habilitadas=progrediram,
    )
    return {
        "estado": AVALIADA,
        "publicadas": publicadas,
        "efetivas": efetivas,
        "ocupadas": ocupadas,
        "faltando": apuracao.faltando(efetivas=efetivas, ocupadas=ocupadas),
        "ocupantes": ocupantes,
    }, ocupantes


def _reservada(entrada, ocupantes_da_ampla, especie, motivo_da_ampla):
    if entrada["vagas"] is None:
        return _nao_avaliada(SEM_LINHA)
    if entrada["impedido"]:
        return _nao_avaliada(CORTE_NAO_EMITIDO)
    if ocupantes_da_ampla is None:
        return _nao_avaliada(DEPENDE_DA_AMPLA, motivo=motivo_da_ampla)
    progrediram = list(entrada["progrediram"])
    chaves = {apuracao.chave_da_inscricao(i) for i in progrediram}
    tomadas = len(chaves & ocupantes_da_ampla)
    try:
        publicadas, efetivas, ocupadas = apuracao.apurar(
            publicadas=entrada["vagas"],
            progrediram_em_ordem=progrediram,
            habilitadas=progrediram,
            ocupantes_da_ampla=ocupantes_da_ampla,
            empates_residuais=entrada["empates"],
        )
    except apuracao.EmpateNaFronteiraDoAlvo as erro:
        return _nao_avaliada(PAROU_NA_FRONTEIRA, posicao=erro.posicao, quantas=erro.quantas)
    posicoes = list(entrada["posicoes"])
    ha = reversao.ha_quem_ocupar(posicoes=posicoes, ja_ocupadas=ocupadas)
    cede = reversao.quantidade_a_reverter(
        especie=especie, efetivas=efetivas, ocupadas=ocupadas, ha_quem_ocupar=ha
    )
    # **A apuração nasce com a efetiva líquida da cessão**, como `emissao._apurar` grava: o que a
    # tela mostra é o número que o ato registraria, e a cessão é dita à parte.
    liquidas = efetivas - cede
    membros = {apuracao.chave_da_inscricao(i) for i in entrada["membros"]}
    return {
        "estado": AVALIADA,
        "publicadas": publicadas,
        "efetivas_antes": efetivas,
        "efetivas": liquidas,
        "ocupadas": ocupadas,
        "faltando": apuracao.faltando(efetivas=liquidas, ocupadas=ocupadas),
        "sem_ocupante_antes": apuracao.faltando(efetivas=efetivas, ocupadas=ocupadas),
        "ocupam_pela_ampla": membros & ocupantes_da_ampla,
        "tomadas_pela_ampla": tomadas,
        "alem_da_faixa": sum(1 for p in posicoes if p is not None) - len(progrediram),
        "pessoas_com_posicao": sum(1 for p in posicoes if p is not None),
        "ha_quem_ocupar": ha,
        "cederia": cede,
    }


def rodada(recortes, *, especie):
    """`{lista_id: apuração}`, com `cedido` e `efetivas_da_proxima_ampla`.

    `recortes` é a lista na ordem da derivação — a ampla (`lista_id` nulo) primeiro —, e cada um
    traz `vagas` (a linha do quadro, ou `None`), `impedido` (o corte não seria emitido),
    `progrediram` (a faixa, na ordem), `posicoes` (a posição de cada um da ordem do recorte, ou
    `None`), `membros` (todos os do recorte) e `empates` (`{id: posição}` do empate residual).
    `especie` é a reversão declarada no Perfil, ou `None` — e `None` não reverte
    (`reversao.quantidade_a_reverter`).
    """
    saida, ocupantes, motivo = {}, None, ""
    cedido = 0
    for entrada in recortes:
        if entrada["lista_id"] is None:
            resultado, ocupantes = _ampla(entrada)
            motivo = resultado["estado"]
        else:
            resultado = _reservada(entrada, ocupantes, especie, motivo)
            cedido += resultado.get("cederia") or 0
        saida[entrada["lista_id"]] = resultado
    ampla = saida.get(None) or {}
    return {
        "recortes": saida,
        "especie": especie,
        "cedido": cedido,
        "efetivas_da_proxima_ampla": (
            ampla["publicadas"] + cedido if cedido and ampla.get("estado") == AVALIADA else None
        ),
    }


__all__ = [
    "AVALIADA",
    "CORTE_NAO_EMITIDO",
    "DEPENDE_DA_AMPLA",
    "PAROU_NA_FRONTEIRA",
    "SEM_LINHA",
    "rodada",
]
