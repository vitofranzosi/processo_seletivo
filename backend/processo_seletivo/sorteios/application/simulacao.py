"""A prévia do sorteio: uma rodada com semente fictícia, e o resumo de muitas (098).

**Nenhuma regra própria.** A ordem é `simulacao.ordem_do_recorte` — `chave.ordem`, a do certame —; a
semente é `normalizacao.normalizar`, pela regra do método; o corte é
`classificacao.application.previa.corte_da_ordem`, o mesmo da prévia da pontuação; e a ocupação é
`apurar_recortes`, a rodada da `ocupacao`, que chega **por parâmetro**, como na `095`: o sorteio não
importa a ocupação, e quem liga os dois é a interface.

**O material chega pronto.** Este app não gera aleatoriedade (021, FR-026), e a prévia não abre
exceção: quem sorteia os cinco números fictícios é a interface (R-004). Aqui eles só são
normalizados.

**O resumo é a soma das rodadas, e nada além** (FR-2504). Uma fórmula fechada seria instantânea e
deixaria de mostrar o comportamento atual das DP-1 e DP-2 da `095`, que nenhuma fórmula reproduz sem
reimplementar a regra. A medição da R-003 mostrou que não precisa: 1.000 rodadas com 500 inscritos e
seis reservadas custam ~1,4 s.
"""

from processo_seletivo.classificacao.application.previa import (
    RESERVADAS_COBERTAS,
    Incompleto,
    consequencias,
    corte_da_ordem,
    entrada_da_rodada,
)
from processo_seletivo.classificacao.domain import faixa
from processo_seletivo.classificacao.domain.cenarios_da_previa import TETO
from processo_seletivo.sorteios.domain import normalizacao, simulacao

#: Quantas rodadas o resumo faz (D-002, R-003).
RODADAS = 1000

#: O estado da apuração que a rodada da `ocupacao` devolve quando avaliou o recorte. Repetido aqui,
#: e não importado, porque o sorteio não importa a ocupação; `test_simulacao_resumo.py` prende os
#: dois valores juntos.
AVALIADA = "avaliada"

#: A regra da Loteria Federal, suposta quando o método ainda não escolheu nenhuma (D-007).
REGRA_SUPOSTA = normalizacao.DIGITOS_EM_SEQUENCIA


def acima_do_limite(so_ampla, por_reservada):
    """A frase do limite, ou `None` quando a população cabe (FR-2491; FR-2343 da `095`)."""
    if len(por_reservada) > RESERVADAS_COBERTAS:
        return (
            "A prévia cobre até seis Modalidades reservadas; este Perfil declara "
            f"{len(por_reservada)}."
        )
    total = int(so_ampla) + sum(int(quantos) for _, quantos in por_reservada)
    if total > TETO:
        return (
            f"A prévia sorteia até {TETO} candidatos fictícios; a população informada soma {total}."
        )
    return None


def regra_de_normalizacao(metodo):
    """`(regra, supos)`: a regra declarada no método, ou a da Loteria Federal, dita como suposta."""
    regra = ((metodo or {}).get("normalization") or {}).get("rule") or ""
    return (regra, False) if regra else (REGRA_SUPOSTA, True)


def simular_sorteio(
    marco,
    *,
    perfil_id,
    metodo,
    material,
    candidatos,
    recortes,
    apurar_recortes=None,
    resumos_oficiais=None,
):
    """Uma rodada: a semente do material, a ordem e o corte de cada recorte, e a ocupação.

    `recortes` é `[{lista_id, rotulo, vagas}]`, a ampla primeiro, na derivação oficial (R-006).
    `resumos_oficiais` é `{lista_id: resumo}` e só o teste de equivalência o passa (R-009): sem ele,
    cada recorte usa o resumo da relação fictícia.
    """
    regra_norm, supos = regra_de_normalizacao(metodo)
    semente = normalizacao.normalizar(material_bruto=material, regra=regra_norm)
    preparo = _preparar(marco, perfil_id, candidatos, recortes, resumos_oficiais)
    previa = _rodada(preparo, semente, apurar_recortes, perfil_id)
    return {
        **previa,
        "material": material,
        "semente": semente,
        "regra_de_normalizacao": regra_norm,
        "supos_regra": supos,
        "regra": preparo["regra"],
        "alvo": preparo["alvo"],
        "suplentes": preparo["suplentes"],
        "total": len(candidatos),
    }


def resumir(marco, *, perfil_id, semente, candidatos, recortes, apurar_recortes, rodadas=RODADAS):
    """O resumo de `rodadas` rodadas com sementes derivadas da exibida (FR-2501 a FR-2505).

    Não guarda ordem nenhuma: cada rodada deixa só os contadores do `data-model.md`.
    """
    preparo = _preparar(marco, perfil_id, candidatos, recortes, None)
    if not preparo["regra"]:
        # Sem corte, toda rodada daria "não há faixa": repetir isso mil vezes não é resumo.
        return {"rodadas": 0, "semente": semente, "sem_corte": True}
    reservadas = [r["lista_id"] for r in recortes if r["lista_id"] is not None]
    contas = {lista: _Conta() for lista in reservadas}
    ampla = _Conta()
    estados = {}
    for indice in range(rodadas):
        rodada = _rodada(
            preparo, simulacao.semente_da_rodada(semente, indice), apurar_recortes, perfil_id
        )
        ocupacao = rodada["ocupacao_por_recorte"]["recortes"]
        pela_ampla = 0
        for lista in reservadas:
            apurado = ocupacao.get(lista) or {}
            estados.setdefault(lista, apurado.get("estado"))
            if apurado.get("estado") != AVALIADA:
                continue
            sobra = apurado["sem_ocupante_antes"]
            ocupam = len(apurado["ocupam_pela_ampla"])
            pela_ampla += ocupam
            contas[lista].somar(
                sem_ocupante=sobra,
                com_sobra=int(sobra > 0),
                pela_ampla=ocupam,
                cedidas=apurado.get("cederia") or 0,
                com_cessao=int((apurado.get("cederia") or 0) > 0),
            )
        estados.setdefault(None, (ocupacao.get(None) or {}).get("estado"))
        if (ocupacao.get(None) or {}).get("estado") == AVALIADA:
            ampla.somar(autodeclarados_ocupando=pela_ampla, ocupadas=ocupacao[None]["ocupadas"])
    return {
        "rodadas": rodadas,
        "semente": semente,
        "ampla": {"estado": estados.get(None), **ampla.resumo(rodadas)},
        "reservadas": {
            lista: {"estado": estados.get(lista), **contas[lista].resumo(rodadas)}
            for lista in reservadas
        },
    }


class _Conta:
    """Soma, mínimo e máximo de cada contador, para a média e para dizer "em todas as rodadas"."""

    def __init__(self):
        self.soma, self.minimo, self.maximo, self.vezes = {}, {}, {}, 0

    def somar(self, **valores):
        self.vezes += 1
        for nome, valor in valores.items():
            self.soma[nome] = self.soma.get(nome, 0) + valor
            self.minimo[nome] = min(self.minimo.get(nome, valor), valor)
            self.maximo[nome] = max(self.maximo.get(nome, valor), valor)

    def resumo(self, rodadas):
        if not self.vezes:
            return {"avaliadas": 0}
        saida = {"avaliadas": self.vezes}
        for nome, soma in self.soma.items():
            saida[nome] = {
                "media": soma / self.vezes,
                "constante": self.minimo[nome] == self.maximo[nome],
                "valor": self.minimo[nome],
            }
        # As duas contagens de rodadas viram porcentagem: é a pergunta que o sorteio faz (D-002).
        for nome in ("com_sobra", "com_cessao"):
            if nome in saida:
                saida[nome]["porcentagem"] = 100 * self.soma[nome] / self.vezes
        return saida


def _preparar(marco, perfil_id, candidatos, recortes, resumos_oficiais):
    """O que não muda entre rodadas: a regra de corte, o alvo de cada recorte e as relações."""
    regra = faixa.normalizar(marco.get("cutRule"))
    vagas_da_ampla = recortes[0]["vagas"] if recortes else None
    alvo = suplentes = None
    if regra:
        suplentes = regra["surplusCount"]
        if regra["targetKind"] == faixa.ALVO_FIXO:
            if regra.get("targetCount") is None:
                raise Incompleto(["Declare o alvo: a quantidade fixa está vazia."])
            alvo = int(regra["targetCount"])
        else:
            alvo = vagas_da_ampla
    por_recorte = []
    for recorte in recortes:
        lista_id = recorte["lista_id"]
        alvo_do_recorte = alvo
        if regra and regra["targetKind"] == faixa.ALVO_DO_QUADRO:
            alvo_do_recorte = recorte["vagas"]
        relacao = simulacao.relacao_ficticia(candidatos, perfil_id=perfil_id, lista_id=lista_id)
        por_recorte.append(
            {
                **recorte,
                "relacao": relacao,
                "alvo": alvo_do_recorte,
                "resumo_oficial": (resumos_oficiais or {}).get(lista_id),
            }
        )
    return {"regra": regra, "alvo": alvo, "suplentes": suplentes, "recortes": por_recorte}


def _rodada(preparo, semente, apurar_recortes, perfil_id):
    regra, suplentes = preparo["regra"], preparo["suplentes"]
    calculados, entradas = [], []
    for recorte in preparo["recortes"]:
        ordem = simulacao.ordem_do_recorte(
            recorte["relacao"],
            perfil_id=perfil_id,
            semente=semente,
            relation_hash=recorte["resumo_oficial"],
        )
        sem_relacao = not recorte["relacao"].participantes
        if sem_relacao:
            # **Lista vazia não é sorteada, e por isso não corta nem apura** — é o que o caminho
            # oficial faz, medido em 21/10/2026: `publicar_relacao` recusa a relação vazia
            # (`relation_would_be_empty`), o corte recusa por `sem_ato_vigente` e a apuração por
            # `ordem_nao_vigente`. A consequência é que a vaga dela **não reverte**, nem sob "por
            # saldo". A prévia mostra o comportamento atual (FR-2507); a leitura da norma é do
            # usuário, e está registrada em `doc/achado-reservada-vazia-nao-reverte.md`.
            corte = {
                "declarado": bool(regra),
                "sem_relacao": True,
                "progrediram": [],
                "excedentes": [],
            }
        elif regra and recorte["alvo"] is None:
            # Sem linha, o alvo do quadro não é apurável neste recorte — e ausência não vira zero,
            # como no corte oficial e na `095` (`recorte_sem_linha_de_quadro`).
            corte = {
                "declarado": True,
                "sem_linha": True,
                "recusado": False,
                "progrediram": [],
                "excedentes": [],
            }
        else:
            corte = corte_da_ordem(regra, ordem, [], alvo=recorte["alvo"], suplentes=suplentes)
        calculados.append(
            {
                "lista_id": recorte["lista_id"],
                "rotulo": recorte["rotulo"],
                "vagas": recorte["vagas"],
                "alvo": recorte["alvo"],
                "ordem": ordem,
                "corte": corte,
                "consequencias": consequencias(ordem, [], corte),
                "total": len(ordem),
            }
        )
        entrada = entrada_da_rodada(recorte["lista_id"], recorte["vagas"], ordem, [], corte)
        if sem_relacao:
            # `impedido` da prévia da pontuação não conhece a lista sem relação — lá, todo recorte
            # tem a população inteira a ordenar. Aqui o corte não seria emitido, e a rodada da
            # `ocupacao` precisa ler isso como lê o corte recusado.
            entrada["impedido"] = True
        entradas.append(entrada)
    ampla = calculados[0]["ordem"] if calculados else []
    return {
        "recortes": calculados,
        "posicao_na_ampla": {item["inscricao_id"]: item["posicao"] for item in ampla},
        "entradas": entradas,
        # **Sem regra de corte, nenhuma apuração** (FR-2500): o marco não emitiria geração, e a
        # ocupação oficial lê a faixa da geração. Apurar sobre "todos progrediram" mostraria vagas
        # ocupadas num marco que não chamaria ninguém.
        "sem_corte": not regra,
        "ocupacao_por_recorte": (apurar_recortes(entradas) if apurar_recortes and regra else None),
    }


__all__ = [
    "AVALIADA",
    "RODADAS",
    "acima_do_limite",
    "regra_de_normalizacao",
    "resumir",
    "simular_sorteio",
]
