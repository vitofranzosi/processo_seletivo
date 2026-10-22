"""As duas medições da R-001 e da R-003 da `098`: o motor oficial do sorteio, sem banco e sem tela.

Roda fora da suíte, de dentro de `backend/`, com o Python do projeto:

    PYTHONPATH=. DJANGO_SETTINGS_MODULE=config.settings.test python ../specs/098-previa-do-sorteio/prototipo/medicao.py

**Nenhuma regra própria.** A ordem é `chave.ordem`, a semente é `normalizacao.normalizar`, a faixa é
`faixa.calcular` e a ocupação é `rodada_da_previa.rodada` — as mesmas funções que o caminho oficial e a
prévia da `095` chamam. O que este arquivo acrescenta é só a população fictícia e o laço das rodadas.

O resumo da relação é fictício (um SHA-256 do recorte): ele só muda **qual** ordem sai, e não a forma
de calcular. É a única entrada que difere do caminho oficial, e é por isso que o teste de equivalência
da implementação a injeta (R-002).
"""

import hashlib
import time
from statistics import mean

from processo_seletivo.classificacao.domain import faixa
from processo_seletivo.ocupacao.domain import rodada_da_previa
from processo_seletivo.sorteios.domain import chave, normalizacao

MATERIAL = "048213 771904 302558 919007 116482"


def populacao(so_ampla, reservadas):
    """`[(id, lista_id)]`: primeiro os só da ampla, depois os autodeclarados de cada reservada."""
    pessoas = [(f"a{i}", None) for i in range(so_ampla)]
    for lista, quantos in reservadas:
        pessoas += [(f"{lista}{i}", lista) for i in range(quantos)]
    return pessoas


def rodada(pessoas, vagas, semente, especie, suplentes=0):
    entradas = []
    for lista in [None, *(chave_ for chave_ in vagas if chave_ is not None)]:
        membros = [p for p, m in pessoas if lista is None or m == lista]
        ordem = chave.ordem(
            relation_hash=hashlib.sha256(f"relacao-ficticia:{lista}".encode()).hexdigest(),
            draw_scope_id=chave.recorte(perfil_id="perfil-ficticio", lista_id=lista),
            seed=semente,
            public_numbers=list(range(1, len(membros) + 1)),
        )
        em_ordem = [membros[numero - 1] for numero in ordem]
        progrediram, _, _, _ = faixa.calcular(
            [(p, posicao) for posicao, p in enumerate(em_ordem, 1)],
            alvo=vagas[lista],
            excedente=suplentes,
            desfecho=faixa.EMPATE_ESTRITO,
        )
        entradas.append(
            {
                "lista_id": lista,
                "vagas": vagas[lista],
                "impedido": False,
                "progrediram": list(progrediram),
                "posicoes": list(range(1, len(em_ordem) + 1)),
                "membros": em_ordem,
                "empates": {},
            }
        )
    return rodada_da_previa.rodada(entradas, especie=especie)


def custo(so_ampla, por_reservada, reservadas, rodadas=1000):
    """R-003: uma rodada e o resumo, no pior caso que a spec admite."""
    listas = [(f"r{i}", por_reservada) for i in range(reservadas)]
    pessoas = populacao(so_ampla, listas)
    vagas = {None: 10, **{lista: 3 for lista, _ in listas}}
    base = normalizacao.normalizar(material_bruto=MATERIAL, regra="DIGITOS_EM_SEQUENCIA")
    inicio = time.perf_counter()
    rodada(pessoas, vagas, base, "ON_BALANCE")
    uma = time.perf_counter() - inicio
    inicio = time.perf_counter()
    for i in range(rodadas):
        rodada(pessoas, vagas, f"{base}:{i}", "ON_BALANCE")
    todas = time.perf_counter() - inicio
    print(
        f"{len(pessoas)} inscritos, {reservadas} reservadas: uma rodada {uma * 1000:.1f} ms; "
        f"{rodadas} rodadas {todas:.2f} s"
    )


def historia(rodadas=1000):
    """R-001: a população da história 1 da spec — 20 só na ampla, 6 PPI, 4 PcD; vagas 10/3/2."""
    pessoas = populacao(20, [("PPI", 6), ("PcD", 4)])
    vagas = {None: 10, "PPI": 3, "PcD": 2}
    for especie in (None, "ON_BALANCE", "ON_EXHAUSTION"):
        linhas = []
        for lista in ("PPI", "PcD"):
            sobra, pela_ampla, cedidas = [], [], []
            for i in range(rodadas):
                r = rodada(pessoas, vagas, f"semente-ficticia:{i}", especie)["recortes"]
                sobra.append(r[lista]["sem_ocupante_antes"])
                pela_ampla.append(len(r[lista]["ocupam_pela_ampla"]))
                cedidas.append(r[lista]["cederia"] or 0)
            linhas.append(
                f"{lista}: sobra em {sum(1 for s in sobra if s) * 100 // rodadas}% das rodadas, "
                f"média sem ocupante {mean(sobra):.2f}, média pela ampla {mean(pela_ampla):.2f}, "
                f"média cedida {mean(cedidas):.2f}"
            )
        print(f"reversão {especie or 'não declarada'} — " + "; ".join(linhas))


if __name__ == "__main__":
    custo(20, 6, 2)
    custo(260, 40, 6)
    historia()
