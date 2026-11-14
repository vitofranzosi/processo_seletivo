"""A quem a Etapa se aplica: o alcance por Modalidade (163).

**Uma resposta para três camadas.** A publicação confere o alcance sobre o conteúdo, a
participação o aplica sobre a consulta das inscrições, e as telas e o documento o descrevem. As
três fazem a mesma pergunta — *esta Etapa alcança esta Modalidade?* —, e uma resposta escrita três
vezes diverge na primeira mudança (T-003).

**O alcance é por código, e não por identidade** (D-001). A Modalidade é do Perfil, e um Edital
de três Perfis tem três Modalidades `PPI`; o que elas têm em comum é o código, que é estrutural
depois de publicado. É a forma do recorte transversal do Documento Exigido (`044`).

**`None` é "todas as inscrições"** (D-002), e não a lista de todos os códigos: é o que toda Etapa
significava antes do degrau 22, e a lista mudaria de sentido quando uma Retificação acrescentasse
Modalidade.

**A inscrição sem Modalidade nunca é alcançada por Etapa restrita** (D-003). É a ampla concorrência,
na grafia que a ordem, o sorteio e o quadro de vagas já usam.

Funções puras: nada aqui consulta o banco. A Etapa pode vir do conteúdo publicado, do rascunho ou do
modelo — as três formas têm o mesmo significado.
"""

from __future__ import annotations

#: A chave do alcance na Etapa do conteúdo publicado e do rascunho (degrau 22).
CHAVE = "modalityCodes"


def codigos(etapa) -> frozenset[str] | None:
    """Os códigos que a Etapa alcança, ou `None` quando ela alcança todas as inscrições."""
    if etapa is None:
        return None
    if isinstance(etapa, dict):
        valor = etapa.get(CHAVE)
    else:
        valor = getattr(etapa, "alcance", None)
    if valor is None:
        return None
    return frozenset(str(codigo).strip() for codigo in valor)


def restrita(etapa) -> bool:
    """A Etapa alcança só algumas Modalidades?"""
    return codigos(etapa) is not None


def normalizar(valor) -> list[str] | None:
    """A forma publicada: `None`, ou a lista **ordenada** dos códigos, sem repetição.

    Ordenar torna o resumo canônico independente da ordem em que alguém marcou (T-002). A
    conferência do que entra é de `validate_stage`; aqui só se dá forma ao que já passou por ela.
    """
    if valor is None:
        return None
    return sorted({str(codigo).strip() for codigo in valor})


def alcanca(etapa, codigo_da_modalidade) -> bool:
    """A Etapa alcança a inscrição que declara esta Modalidade (`None` = sem Modalidade)?"""
    alcance = codigos(etapa)
    if alcance is None:
        return True
    if codigo_da_modalidade is None:
        return False
    return str(codigo_da_modalidade).strip() in alcance


def _modalidades(conteudo):
    for perfil in (conteudo or {}).get("profiles") or []:
        if not isinstance(perfil, dict):
            continue
        for modalidade in perfil.get("competitionModalities") or []:
            if isinstance(modalidade, dict):
                yield perfil, modalidade


def _codigo(modalidade) -> str:
    return str(modalidade.get("code") or "").strip()


def modalidades_alcancadas(conteudo, etapa) -> frozenset[str] | None:
    """As **identidades** de Modalidade que a Etapa alcança neste conteúdo, ou `None` = todas.

    A inscrição guarda `modality_id`, e o código é o que o conteúdo diz que aquela identidade tem.
    Lido do conteúdo, e não do banco, pela mesma razão que a participação lê as Etapas do conteúdo
    vigente: é a norma publicada que decide, e não o rascunho que alguém esteja editando.
    """
    alcance = codigos(etapa)
    if alcance is None:
        return None
    return frozenset(
        str(modalidade.get("id"))
        for _perfil, modalidade in _modalidades(conteudo)
        if _codigo(modalidade) in alcance and modalidade.get("id")
    )


def codigo_da_modalidade(conteudo, modality_id) -> str | None:
    """O código da Modalidade desta identidade, no conteúdo; `None` sem Modalidade ou sem achado."""
    if modality_id is None:
        return None
    for _perfil, modalidade in _modalidades(conteudo):
        if str(modalidade.get("id")) == str(modality_id):
            return _codigo(modalidade) or None
    return None


def alcanca_a_inscricao(conteudo, etapa, modality_id) -> bool:
    """A pergunta para **uma** inscrição, pela identidade da Modalidade que ela declarou."""
    if not restrita(etapa):
        return True
    return alcanca(etapa, codigo_da_modalidade(conteudo, modality_id))


def _rotulo_da_modalidade(modalidade) -> str:
    return str(modalidade.get("name") or modalidade.get("code") or "").strip()


def _rotulo_do_perfil(perfil) -> str:
    return str(perfil.get("code") or perfil.get("name") or "").strip()


def descrever(conteudo, etapa) -> list[dict]:
    """Cada código do alcance, com a denominação e os Perfis que o têm, na ordem dos códigos.

    `[]` quando a Etapa alcança todas. A denominação é a do primeiro Perfil que tem o código: a
    publicação impede denominações diferentes para o mesmo código referido (FR-6965). Código que
    nenhum Perfil tem sai com a própria grafia e sem Perfis — a tela e o aviso precisam mostrá-lo.
    """
    alcance = codigos(etapa)
    if alcance is None:
        return []
    por_codigo: dict[str, dict] = {}
    for perfil, modalidade in _modalidades(conteudo):
        codigo = _codigo(modalidade)
        if codigo not in alcance:
            continue
        item = por_codigo.setdefault(
            codigo,
            {"codigo": codigo, "denominacao": _rotulo_da_modalidade(modalidade), "perfis": []},
        )
        rotulo = _rotulo_do_perfil(perfil)
        if rotulo and rotulo not in item["perfis"]:
            item["perfis"].append(rotulo)
    return [
        por_codigo.get(codigo, {"codigo": codigo, "denominacao": codigo, "perfis": []})
        for codigo in sorted(alcance)
    ]


def perfis_sem_alcancado(conteudo, etapa) -> list[str]:
    """Os Perfis em que nenhuma Modalidade do alcance existe (UX-731). `[]` para "todas"."""
    alcance = codigos(etapa)
    if alcance is None:
        return []
    return [
        _rotulo_do_perfil(perfil)
        for perfil in (conteudo or {}).get("profiles") or []
        if isinstance(perfil, dict)
        and not any(
            _codigo(modalidade) in alcance
            for modalidade in perfil.get("competitionModalities") or []
            if isinstance(modalidade, dict)
        )
    ]


def _enumerar(itens: list[str]) -> str:
    if len(itens) <= 1:
        return "".join(itens)
    return f"{', '.join(itens[:-1])} e {itens[-1]}"


def nomes_do_alcance(conteudo, etapa) -> str:
    """ "Pretos e pardos (PPI) e Pessoas com deficiência (PcD)" — a denominação e o código."""
    nomes = []
    for item in descrever(conteudo, etapa):
        denominacao, codigo = item["denominacao"], item["codigo"]
        nomes.append(denominacao if denominacao == codigo else f"{denominacao} ({codigo})")
    return _enumerar(nomes)


def frase_do_alcance(conteudo, etapa) -> str:
    """A frase do documento, da Revisão e da página pública (FR-6983, FR-6984).

    `""` para a Etapa que alcança todas: é o que faz o acervo se recompor byte a byte (SC-2310).
    """
    if not restrita(etapa):
        return ""
    artigo = "na modalidade" if len(codigos(etapa)) == 1 else "nas modalidades"
    nomes = nomes_do_alcance(conteudo, etapa)
    return f"Aplica-se somente aos candidatos inscritos {artigo} {nomes}."
