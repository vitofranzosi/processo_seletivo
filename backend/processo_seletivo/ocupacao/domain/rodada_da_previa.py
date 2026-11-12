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

**Por esgotamento, a rodada diz o que a destinação faria** (155, FR-6343, R-011): desde a `155` a
apuração não cede vaga por esse gatilho, e a vaga vai à ampla por ato próprio quando ninguém mais da
reserva pode ocupá-la (FR-6304). A conta é a de `destinacao.quem_ainda_pode_ocupar`, sobre o que a
prévia tem — as posições, quem ocupa pela ampla e o alcance —, e sem desfecho nem recurso, que a
prévia não simula. Quem ocupa pela ampla **conta** como quem ainda pode ocupar: a confirmação da
ocupação pela ampla é fato que a prévia não tem, e o caminho oficial também o conta até ela.

Mora na `ocupacao` porque a decisão é dela; a `classificacao` não importa este módulo, e quem liga
os dois é a interface (`tests/test_dependencia_da_ocupacao.py`).
"""

from processo_seletivo.ocupacao.domain import apuracao, destinacao, nomes, reversao

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


def _reservada(entrada, ocupantes_da_ampla, especie, motivo_da_ampla, continuacao_admitida=False):
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
    if especie == nomes.REVERSAO_POR_ESGOTAMENTO:
        # **A apuração não cede, e a destinação é dita à parte** (155, FR-6315, FR-6343): as
        # efetivas são as que a emissão gravaria, e `cederia` é o que o ato próprio levaria à ampla.
        restantes = destinacao.quem_ainda_pode_ocupar(
            posicoes=list(zip(entrada["membros"], posicoes, strict=False)),
            alcancaveis=None if continuacao_admitida else progrediram,
            ocupantes=apuracao.ocupantes(
                titulares=apuracao.titulares_iniciais(
                    progrediram_em_ordem=progrediram,
                    efetivas=efetivas,
                    ocupantes_da_ampla=ocupantes_da_ampla,
                    empates_residuais=entrada["empates"],
                    habilitadas=progrediram,
                ),
                habilitadas=progrediram,
            ),
        )
        ha = bool(restantes)
        cede = destinacao.quantidade_destinavel(
            gatilho=especie,
            saldo=apuracao.faltando(efetivas=efetivas, ocupadas=ocupadas),
            ainda_podem_ocupar=len(restantes),
        )
        liquidas = efetivas
    else:
        ha = reversao.ha_quem_ocupar(posicoes=posicoes, ja_ocupadas=ocupadas)
        cede = reversao.quantidade_a_reverter(
            especie=especie, efetivas=efetivas, ocupadas=ocupadas, ha_quem_ocupar=ha
        )
        # **A apuração nasce com a efetiva líquida da cessão**, como `emissao._apurar` grava sob a
        # reversão por saldo: o que a tela mostra é o número que o ato registraria, e a cessão é
        # dita à parte.
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
        # Quem ainda poderia ocupar a vaga que sobra, só por esgotamento (155, FR-6304): é o número
        # que a frase da prévia diz quando a destinação não seria oferecida.
        "ainda_podem_ocupar": len(restantes) if especie == nomes.REVERSAO_POR_ESGOTAMENTO else None,
    }


def rodada(recortes, *, especie, continuacao_admitida=False):
    """`{lista_id: apuração}`, com `cedido` e `efetivas_da_proxima_ampla`.

    `recortes` é a lista na ordem da derivação — a ampla (`lista_id` nulo) primeiro —, e cada um
    traz `vagas` (a linha do quadro, ou `None`), `impedido` (o corte não seria emitido),
    `progrediram` (a faixa, na ordem), `posicoes` (a posição de cada um da ordem do recorte, ou
    `None`), `membros` (todos os do recorte) e `empates` (`{id: posição}` do empate residual).
    `especie` é a reversão declarada no Perfil, ou `None` — e `None` não reverte
    (`reversao.quantidade_a_reverter`). `continuacao_admitida` é se a regra de corte publicada
    admite faixa além da primeira: com ela, quem está fora da faixa ainda alcança a vaga, e a
    reserva não está esgotada (155, FR-6304).
    """
    saida, ocupantes, motivo = {}, None, ""
    cedido = 0
    for entrada in recortes:
        if entrada["lista_id"] is None:
            resultado, ocupantes = _ampla(entrada)
            motivo = resultado["estado"]
        else:
            resultado = _reservada(entrada, ocupantes, especie, motivo, continuacao_admitida)
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
