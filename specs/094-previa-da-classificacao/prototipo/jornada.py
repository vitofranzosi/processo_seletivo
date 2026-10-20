"""A jornada do Perfil: as Etapas e os marcos na ordem do Edital (terceira rodada, D-015).

Demonstrativo, e puro: lê só a configuração — Etapas (ordem, forma, nome) e marcos (Etapas que
enumeram, regra de corte) — e devolve a sequência de pontos que o painel desenha. **Não calcula
nada**: o único número da jornada vem da prévia do marco selecionado, que já é calculada pelo
motor oficial. No produto, a mesma função lê o snapshot do rascunho (`edital_snapshot`), e é ela
que a T050 cria em `classificacao/domain/jornada.py`.

**Não supõe que o Edital é linear.** A ordem vem da `order` das Etapas, e cada marco entra depois
da última Etapa que enumera. Uma Etapa pode alimentar mais de um marco (a Prova Escrita entra nos
dois), uma Etapa decisória pode não entrar em marco nenhum (a Análise documental), um marco pode
não cortar ou não alimentar Etapa nenhuma, e a faixa seguinte é um retorno, e não um passo. Cada
um desses casos tem o seu tipo de ponto, para que o painel diga o que acontece ali em vez de
desenhar uma seta reta.
"""

from __future__ import annotations

from processo_seletivo.classificacao.domain import faixa

DECISORIA = "DECISORIA"

#: Os estados de um ponto em relação ao marco selecionado.
SIMULADO = "simulado"  # calculado agora pelo motor, com os candidatos fictícios
CONTEXTO = "contexto"  # existe no Edital, e a prévia diz o que ele faz, sem calcular
INDETERMINADO = "indeterminado"  # depende de notas ou regras que a prévia não simula
PARCIAL = "parcial"  # quem chega é calculado; o que acontece lá dentro, não


def _ultima(marco, etapas):
    ordens = [etapas[e]["order"] for e in marco["stages"] if e in etapas]
    return max(ordens) if ordens else None


def jornada(etapas_publicadas, marcos, selecionado):
    """Os pontos da jornada do Perfil, na ordem, cada um com o seu estado.

    `marcos` são os do Perfil, na forma do conteúdo; `selecionado` é o `sub` do marco simulado.
    """
    etapas = {e["id"]: e for e in etapas_publicadas}
    por_ordem = sorted(etapas_publicadas, key=lambda e: e["order"])
    sel = next(m for m in marcos if m["sub"] == selecionado)
    enumeradas_sel = set(sel["stages"])
    regra_sel = sel.get("cutRule") or {}
    governada_sel = faixa.etapa_governada(regra_sel) if regra_sel else None
    ordem_sel = _ultima(sel, etapas) or 0
    ordem_governada_sel = etapas[governada_sel]["order"] if governada_sel in etapas else None

    governa = {}  # Etapa → marco que a alimenta
    for marco in marcos:
        alvo = faixa.etapa_governada(marco.get("cutRule"))
        if alvo:
            governa[alvo] = marco
    enumerada_por = {}
    for marco in marcos:
        for etapa_id in marco["stages"]:
            enumerada_por.setdefault(etapa_id, []).append(marco)

    pontos, grupo, mostradas = [], [], set()

    def fechar_grupo():
        if not grupo:
            return
        ids = [e["id"] for e in grupo]
        no_sel = [i for i in ids if i in enumeradas_sel]
        pontos.append(
            {
                "tipo": "avaliacoes",
                "etapas": list(grupo),
                "estado": SIMULADO if no_sel else CONTEXTO,
                "usadas_no_selecionado": no_sel,
            }
        )
        mostradas.update(ids)
        grupo.clear()

    for etapa in por_ordem:
        eid = etapa["id"]
        alimentada = governa.get(eid)
        if alimentada is not None:
            fechar_grupo()
            de_quem = alimentada["sub"] == selecionado
            # Uma Etapa alimentada por corte e enumerada pelo marco simulado é o caso da
            # classificação final: a prévia dá nota fictícia a todos, inclusive a quem não
            # chegaria a ela no Edital real (variaveis-simuladas.md, seção 3).
            usada = eid in enumeradas_sel
            portas_antes = [
                e
                for e in por_ordem
                if e["forma"] == DECISORIA
                and e["id"] not in enumerada_por
                and _ultima(alimentada, etapas) is not None
                and _ultima(alimentada, etapas) < e["order"] < etapa["order"]
            ]
            pontos.append(
                {
                    "tipo": "etapa_alimentada",
                    "etapa": etapa,
                    "por": alimentada,
                    "do_selecionado": de_quem,
                    "usada_no_selecionado": usada,
                    "portas_antes": portas_antes,
                    "estado": PARCIAL if de_quem else (CONTEXTO if usada else INDETERMINADO),
                }
            )
            mostradas.add(eid)
        elif etapa["forma"] == DECISORIA and eid not in enumerada_por:
            fechar_grupo()
            depois_do_sel = ordem_sel < etapa["order"] and (
                ordem_governada_sel is None or etapa["order"] < ordem_governada_sel
            )
            pontos.append(
                {
                    "tipo": "porta",
                    "etapa": etapa,
                    "antes_da_governada": depois_do_sel and governada_sel is not None,
                    "governada": etapas.get(governada_sel),
                    "estado": INDETERMINADO if depois_do_sel else CONTEXTO,
                }
            )
            mostradas.add(eid)
        elif eid in enumerada_por:
            grupo.append(etapa)
        else:
            fechar_grupo()
            pontos.append({"tipo": "fora", "etapa": etapa, "estado": CONTEXTO})
        # Os marcos entram depois da última Etapa que enumeram.
        for marco in marcos:
            if _ultima(marco, etapas) == etapa["order"]:
                fechar_grupo()
                regra = marco.get("cutRule") or {}
                governada = faixa.etapa_governada(regra) if regra else None
                if marco["sub"] == selecionado:
                    estado = SIMULADO
                elif (_ultima(marco, etapas) or 0) < ordem_sel:
                    estado = CONTEXTO
                else:
                    estado = INDETERMINADO
                pontos.append(
                    {
                        "tipo": "marco",
                        "marco": marco,
                        "estado": estado,
                        "antes_do_selecionado": estado == CONTEXTO,
                        "governada": etapas.get(governada),
                        "terminal": bool(regra) and regra.get("governedStage") == "NONE",
                        "corta": bool(regra),
                        "por_sorteio": marco.get("orderProduction") == "POR_SORTEIO",
                        "ja_mostradas": [
                            etapas[e] for e in marco["stages"] if e in mostradas and e in etapas
                        ],
                        "nao_simuladas": [
                            etapas[e]
                            for e in marco["stages"]
                            if e in etapas and e not in enumeradas_sel
                        ],
                        "continua": faixa.admite_continuacao(regra),
                    }
                )
    fechar_grupo()
    return pontos
