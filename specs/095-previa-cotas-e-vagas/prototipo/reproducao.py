"""Reprodução, no motor oficial, das consequências que a fatia 2 mostra (095, D-008, R-001).

Não é a implementação, nem protótipo de tela: é o roteiro que sustenta as afirmações da spec. Cada
cenário monta candidatos fictícios com Modalidade, passa-os pelas funções **do produto** —
`universo_classificavel.preparar` com recorte, `desempate.ordenar`, `faixa.calcular`,
`apuracao.titulares_iniciais`, `apuracao.ocupantes`, `apuracao.apurar` e
`reversao.quantidade_a_reverter` — e imprime, por recorte, o que a prévia diria.

**O que é esboço, e está marcado**: as duas decisões que o caminho oficial toma dentro de funções
que leem banco (D-005). `ocupantes_pela_ampla` reproduz `selectors.ocupantes_da_ampla` —
titulares da ampla, **sem** filtrar habilitação, como o original — e `ha_quem_ocupar` reproduz
`movimento.ha_quem_ocupar` — pessoas com posição na ordem do recorte contra vagas ocupadas. As duas
são as que a T004 extrai; até lá, divergência entre elas e o original é defeito deste roteiro.

Rodar, de dentro de `backend/`:

    uv run python ../specs/095-previa-cotas-e-vagas/prototipo/reproducao.py
"""

from decimal import Decimal

from processo_seletivo.classificacao.domain import desempate, faixa
from processo_seletivo.classificacao.domain.universo_classificavel import HABILITADA, preparar
from processo_seletivo.ocupacao.domain import apuracao, nomes, reversao

ETAPAS = {"prova": {"id": "prova", "name": "Prova Escrita", "weight": "1", "order": 1}}
MARCO = {
    "stages": ["prova"],
    "operation": "SOMA_PONDERADA",
    "normalization": "NENHUMA",
    "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
}
AMPLA = None


def candidato(numero, nota, modalidade=None):
    return {
        "inscricao_id": f"c{numero:02d}",
        "protocolo": f"FIC-{numero:02d}",
        "nome": f"Candidato {numero:02d}",
        "identity_subject": f"ficticio-{numero}",
        "modalidade_id": modalidade,
        "fatos": {},
        "resultados": [
            {
                "id": f"r{numero}",
                "etapa_id": "prova",
                "pontuacao": Decimal(nota),
                "consequencia": HABILITADA,
                "motivo": "",
            }
        ],
    }


def populacao(total, modalidades, *, notas=None):
    """`total` candidatos com notas decrescentes; `modalidades` diz quem é autodeclarado em quê."""
    notas = notas or {}
    return [candidato(n, notas.get(n, 100 - n), modalidades.get(n)) for n in range(1, total + 1)]


def ordem_e_faixa(inscritos, *, recorte, alvo, suplentes, desfecho):
    classificaveis, sem_posicao = preparar(MARCO, ETAPAS, inscritos, recorte=recorte)
    ordem = desempate.ordenar(classificaveis, [])
    posicoes = [(i["inscricao_id"], i["posicao"]) for i in ordem] + [
        (i["inscricao_id"], None) for i in sem_posicao
    ]
    empates = {i["inscricao_id"]: i["posicao"] for i in ordem if i["empate_residual"]}
    try:
        progrediram, _, _, _ = faixa.calcular(
            posicoes, alvo=alvo, excedente=suplentes, desfecho=desfecho
        )
    except faixa.EmpateAtravessaOCorte as erro:
        return ordem, None, empates, f"corte não seria emitido (empate na {erro.posicao}ª)"
    return ordem, progrediram, empates, None


# --- esboços das duas decisões que a T004 extrai (D-005) ------------------------------------


def ocupantes_pela_ampla(*, progrediram, efetivas, empates):
    """`selectors.ocupantes_da_ampla` sem banco: titulares da ampla, sem filtro de habilitação."""
    return apuracao.ocupantes(
        titulares=apuracao.titulares_iniciais(
            progrediram_em_ordem=progrediram, efetivas=efetivas, empates_residuais=empates
        )
    )


def ha_quem_ocupar(*, ordem, ja_ocupadas):
    """`movimento.ha_quem_ocupar` sem banco: pessoas com posição na ordem contra vagas ocupadas."""
    return sum(1 for item in ordem if item["posicao"] is not None) > ja_ocupadas


# --- a rodada da prévia (D-002) ---------------------------------------------------------------


def rodada(inscritos, *, vagas, alvo, suplentes=0, desfecho=faixa.EMPATE_ADMITE_EXCEDENTE, especie):
    """Ampla com as publicadas → cada reservada sem quem ocupa pela ampla → reversão. Uma vez só."""
    linhas, faixas = [], {}
    ordem_a, faixa_a, empates_a, recusa_a = ordem_e_faixa(
        inscritos, recorte=AMPLA, alvo=alvo(AMPLA), suplentes=suplentes, desfecho=desfecho
    )
    faixas[AMPLA] = faixa_a or []
    pela_ampla = None
    if recusa_a:
        linhas.append(("ampla", len(ordem_a), recusa_a))
    else:
        try:
            pub, efe, ocu = apuracao.apurar(
                publicadas=vagas[AMPLA],
                progrediram_em_ordem=faixa_a,
                habilitadas=faixa_a,
                empates_residuais=empates_a,
            )
            pela_ampla = ocupantes_pela_ampla(
                progrediram=faixa_a, efetivas=vagas[AMPLA], empates=empates_a
            )
            linhas.append(
                ("ampla", len(ordem_a), f"faixa {len(faixa_a)}; {pub}/{efe}/{ocu}/{efe - ocu}")
            )
        except apuracao.EmpateNaFronteiraDoAlvo as erro:
            linhas.append(("ampla", len(ordem_a), f"apuração pararia na {erro.posicao}ª"))
    cedidas = 0
    for recorte in [r for r in vagas if r is not AMPLA]:
        ordem_r, faixa_r, empates_r, recusa_r = ordem_e_faixa(
            inscritos, recorte=recorte, alvo=alvo(recorte), suplentes=suplentes, desfecho=desfecho
        )
        faixas[recorte] = faixa_r or []
        if recusa_r:
            linhas.append((recorte, len(ordem_r), recusa_r))
            continue
        if pela_ampla is None:
            linhas.append((recorte, len(ordem_r), "não avaliada: depende de quem ocupa pela ampla"))
            continue
        try:
            pub, efe, ocu = apuracao.apurar(
                publicadas=vagas[recorte],
                progrediram_em_ordem=faixa_r,
                habilitadas=faixa_r,
                ocupantes_da_ampla=pela_ampla,
                empates_residuais=empates_r,
            )
        except apuracao.EmpateNaFronteiraDoAlvo as erro:
            linhas.append((recorte, len(ordem_r), f"apuração pararia na {erro.posicao}ª"))
            continue
        ha = ha_quem_ocupar(ordem=ordem_r, ja_ocupadas=ocu)
        cede = reversao.quantidade_a_reverter(
            especie=especie, efetivas=efe, ocupadas=ocu, ha_quem_ocupar=ha
        )
        cedidas += cede
        na_faixa = [i for i in faixa_r if apuracao.chave_da_inscricao(i) in pela_ampla]
        alem = len([i for i in ordem_r if i["inscricao_id"] not in set(faixa_r)])
        linhas.append(
            (
                recorte,
                len(ordem_r),
                f"faixa {len(faixa_r)} ({len(na_faixa)} ocupariam pela ampla, {alem} além); "
                f"{pub}/{efe}/{ocu}/{efe - ocu}; há quem ocupar: {'sim' if ha else 'não'}; "
                f"cederia {cede}",
            )
        )
    uniao = {apuracao.chave_da_inscricao(i) for f in faixas.values() for i in f}
    return linhas, cedidas, len(uniao), len(faixas[AMPLA])


def imprimir(titulo, inscritos, **kwargs):
    linhas, cedidas, uniao, so_ampla = rodada(inscritos, **kwargs)
    especie = kwargs["especie"] or "não declarada"
    print(f"\n### {titulo} — reversão: {especie}\n")
    print("| Recorte | Universo | Faixa, publicadas/efetivas/ocupadas/faltando, reversão |")
    print("|---|---|---|")
    for recorte, universo, texto in linhas:
        print(f"| {recorte} | {universo} | {texto} |")
    if cedidas:
        print(f"\nA próxima apuração da ampla leria {kwargs['vagas'][AMPLA] + cedidas} efetivas.")
    print(f"\nParticipantes da Etapa seguinte (união): {uniao}; só pela ampla: {so_ampla}.")


if __name__ == "__main__":
    vagas = {AMPLA: 10, "PPI": 3, "PCD": 2}
    do_quadro = vagas.__getitem__
    # PPI: 3 e 8 dentro das vagas da ampla, 15 e 16 fora; PcD: 5 dentro, 18 fora.
    base = populacao(20, {3: "PPI", 8: "PPI", 15: "PPI", 16: "PPI", 5: "PCD", 18: "PCD"})
    for especie in (None, nomes.REVERSAO_POR_SALDO, nomes.REVERSAO_POR_ESGOTAMENTO):
        imprimir(
            "Concomitância, alvo do quadro", base, vagas=vagas, alvo=do_quadro, especie=especie
        )

    imprimir(
        "Alvo fixo 10 em todo recorte",
        base,
        vagas=vagas,
        alvo=lambda _: 10,
        especie=nomes.REVERSAO_POR_SALDO,
    )

    # PcD: os dois autodeclarados estão entre as 10 vagas da ampla.
    toda_na_ampla = populacao(20, {3: "PPI", 8: "PPI", 15: "PPI", 16: "PPI", 2: "PCD", 6: "PCD"})
    imprimir(
        "Reservada toda ocupando pela ampla",
        toda_na_ampla,
        vagas=vagas,
        alvo=do_quadro,
        especie=nomes.REVERSAO_POR_ESGOTAMENTO,
    )

    # Suplente da ampla: o 12º é PPI, com 10 vagas e 5 suplentes. Os suplentes são da regra do
    # marco, e valem também na PPI: a faixa dela é de 3 + 5.
    suplente = populacao(20, {12: "PPI", 15: "PPI", 16: "PPI", 17: "PPI"})
    imprimir(
        "Autodeclarado suplente da ampla, 5 suplentes em todo recorte",
        suplente,
        vagas={AMPLA: 10, "PPI": 3},
        alvo=do_quadro,
        suplentes=5,
        especie=None,
    )

    # Empate de dois na 10ª da ampla (o 11º recebe a nota do 10º).
    empate_ampla = populacao(
        20, {3: "PPI", 8: "PPI", 15: "PPI", 16: "PPI", 5: "PCD", 18: "PCD"}, notas={11: 90}
    )
    imprimir(
        "Empate na última vaga da ampla",
        empate_ampla,
        vagas=vagas,
        alvo=do_quadro,
        suplentes=5,
        especie=nomes.REVERSAO_POR_SALDO,
    )

    # Empate de dois na última vaga da PPI, sem PPI nas vagas da ampla: o 18º recebe a nota do 17º.
    empate_ppi = populacao(
        20, {15: "PPI", 16: "PPI", 17: "PPI", 18: "PPI", 5: "PCD", 19: "PCD"}, notas={18: 83}
    )
    imprimir(
        "Empate na última vaga da reservada",
        empate_ppi,
        vagas=vagas,
        alvo=do_quadro,
        especie=nomes.REVERSAO_POR_SALDO,
    )

    # Reserva sem autodeclarados.
    imprimir(
        "Reserva sem autodeclarados",
        populacao(20, {3: "PPI", 8: "PPI", 15: "PPI", 16: "PPI"}),
        vagas=vagas,
        alvo=do_quadro,
        especie=nomes.REVERSAO_POR_ESGOTAMENTO,
    )
