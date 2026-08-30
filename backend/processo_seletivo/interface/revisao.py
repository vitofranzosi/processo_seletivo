"""A conferência do que será congelado na submissão, lida do próprio conteúdo canônico.

A `006` acrescentou Etapas, modalidades e Seções ao conteúdo publicado, e a tela de Revisão
continuou mostrando Perfis e Cronograma — porque cada coleção era um bloco escrito à mão no
template, e alguém precisava lembrar de acrescentar o próximo. Quem submetia declarava ter lido
metade do Edital.

Aqui a fonte é `edital_snapshot`, o mesmo conteúdo que a submissão congela. Uma coleção nova
aparece na Revisão porque está no snapshot, e não porque foi lembrada — o que faz a classe de
defeito desaparecer em vez de ser corrigida uma vez.

**Não é o snapshot cru na tela.** Cada coleção tem uma leitura curta, no vocabulário de quem
elabora; o que este módulo garante é que nenhuma delas fique de fora.
"""

from datetime import datetime

from processo_seletivo.editais.domain import secoes as catalogo
from processo_seletivo.interface.forms import ZONA

RESERVA = {"NONE": "não há", "LIMITED": "limitado", "UNLIMITED": "ilimitado"}
CARATER = (("eliminatory", "eliminatória"), ("classificatory", "classificatória"))


def _instante(valor):
    if not valor:
        return None
    return datetime.fromisoformat(str(valor)).astimezone(ZONA).strftime("%d/%m/%Y %H:%M")


def _perfil(perfil, _snapshot):
    linhas = [
        f"{perfil.get('immediateVacancies', 0)} vaga(s) imediata(s)",
        f"Cadastro Reserva: {RESERVA.get(perfil.get('reserveType'), '—')}"
        + (f" em {perfil['reserveLimit']}" if perfil.get("reserveLimit") is not None else ""),
    ]
    if perfil.get("locality"):
        linhas.append(f"Localidade: {perfil['locality']}")
    for requisito in perfil.get("requirements") or []:
        linhas.append(f"Requisito: {requisito}")
    for modalidade in perfil.get("competitionModalities") or []:
        regra = modalidade.get("normativeRule") or {}
        partes = [f"{modalidade.get('code', '')} — {modalidade.get('name', '')}"]
        if regra.get("percentage"):
            partes.append(f"{regra['percentage']}%")
        if regra.get("foundation"):
            partes.append(regra["foundation"])
            if regra.get("version"):
                partes.append(f"versão {regra['version']}")
        linhas.append("Modalidade: " + " · ".join(partes))
    return {"titulo": f"{perfil.get('code', '')} — {perfil.get('name', '')}", "linhas": linhas}


def _evento(evento, _snapshot):
    periodo = f"Início: {_instante(evento.get('startAt')) or '—'}"
    if evento.get("endAt"):
        periodo += f" · Término: {_instante(evento['endAt'])}"
    return {
        "titulo": f"{evento.get('order', '')}. {evento.get('type', '')}",
        "linhas": [evento.get("description", ""), periodo],
    }


def _etapa(etapa, snapshot):
    caracteres = [
        rotulo
        for chave, rotulo in CARATER
        if etapa.get(chave)
    ]
    linhas = ["Caráter: " + (" e ".join(caracteres) if caracteres else "não informado")]
    if etapa.get("weight") is not None:
        linhas.append(f"Peso: {etapa['weight']}")
    if etapa.get("minimumScore") is not None:
        linhas.append(f"Nota mínima: {etapa['minimumScore']}")
    vinculado = next(
        (
            evento
            for evento in (snapshot.get("schedule") or [])
            if evento.get("id") == etapa.get("scheduleEventId")
        ),
        None,
    )
    if vinculado:
        linhas.append(
            f"Datas do Evento “{vinculado.get('type', '')}”: {_instante(vinculado.get('startAt'))}"
        )
    return {"titulo": f"{etapa.get('order', '')}. {etapa.get('name', '')}", "linhas": linhas}


def _secao(secao, _snapshot):
    if secao.get("type") == catalogo.GERADA:
        origem = {"profiles": "Perfis", "schedule": "Cronograma", "stages": "Etapas"}
        detalhe = f"Composta a partir de {origem.get(secao.get('source'), secao.get('source'))}."
    else:
        detalhe = secao.get("content", "")
    return {"titulo": f"{secao.get('order', '')}. {secao.get('title', '')}", "linhas": [detalhe]}


# Coleção do conteúdo publicado → como se lê, e onde se corrige. Um teste confere que toda
# coleção-raiz de entidades do snapshot está declarada aqui: é o que impede a Revisão de
# envelhecer de novo.
COLECOES = (
    ("profiles", "Perfis de Vaga", "perfis", _perfil),
    ("schedule", "Cronograma", "cronograma", _evento),
    ("stages", "Etapas de Avaliação", "etapas", _etapa),
    ("sections", "Conteúdo do Edital", "conteudo", _secao),
)


def blocos(snapshot):
    """O Edital inteiro, na ordem em que se elabora, com o caminho de volta para cada etapa."""
    conferencia = [
        {
            "titulo": "Identificação",
            "etapa": "identificacao",
            "itens": [
                {
                    "titulo": f"Edital {snapshot.get('number', '')}/{snapshot.get('year', '')}",
                    "linhas": [
                        snapshot.get("title") or "—",
                        snapshot.get("description") or "sem descrição",
                    ],
                }
            ],
        }
    ]
    for chave, titulo, etapa, leitura in COLECOES:
        itens = snapshot.get(chave) or []
        conferencia.append(
            {
                "titulo": titulo,
                "etapa": etapa,
                "itens": [leitura(item, snapshot) for item in itens],
            }
        )
    return conferencia
