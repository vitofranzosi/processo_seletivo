"""As fontes completas da versão vigente, entregues ao modelo (071, `R-002`, `FR-1470` a `FR-1476`).

**A união das respostas da `070`, e não uma leitura nova.** Para toda pergunta oferecida, todo
Perfil e — na `P-05` — toda lista de concorrência, a resposta determinística da `070` já traz os
cartões de texto do Edital e de dado da versão vigente, com o lugar pelo título, o ato de origem e
os links. A `070` já resolve, e prova com testes, o que é difícil: a versão no instante, a origem de
cada valor, a ampla concorrência pela linha sem modalidade, o silêncio que não é negativa, o anexo
que não se lê. Uma leitura nova, entidade a entidade, repetiria tudo isso e divergiria na primeira
mudança. As explicações da `070` ficam de fora: são do sistema, e não fontes.

**Uma exceção: a obrigatoriedade dos documentos.** O cartão "Obrigatoriedade" da `P-05` depende da
lista escolhida — o mesmo caminho daria valores diferentes sem dizer para qual lista. No lugar dele,
uma fonte calculada por Perfil e lista, pela mesma `aplicabilidade` que a `P-05` usa.

**O texto do Edital fica idêntico ao publicado** (`FR-1472`). O valor que uma Retificação já
publicada vai pôr no lugar não entra no conteúdo do cartão: vira fonte calculada à parte, com
`altera` apontando a fonte vigente (`FR-1475`). Assim nenhuma fonte de texto ou de dado mistura
versões, e o modelo vê o futuro rotulado como futuro.

**Identificadores estáveis** (`FR-1472`). `F1…Fn` na ordem canônica — a das perguntas, e dentro
delas a dos Perfis e das listas. A derivação é determinística: o mesmo conteúdo, no mesmo instante
e com o mesmo código, dá os mesmos identificadores. Uma mudança da `070` que os desloque muda a
impressão das fontes, e por ela a rodada fica marcada como de outra versão da fonte (`FR-1515`).
"""

from __future__ import annotations

import re
from dataclasses import replace

from processo_seletivo.duvidas.domain import catalogo, explicacao, leitura
from processo_seletivo.duvidas.domain.estruturas import (
    AVISO_DESFECHO,
    AVISO_RETIFICACAO_FUTURA,
    DADO,
    TEXTO,
    Contexto,
    Referencia,
    Resposta,
)
from processo_seletivo.duvidas.domain.estruturas_do_piloto import CALCULADA, Fonte
from processo_seletivo.duvidas.domain.origem import origens
from processo_seletivo.duvidas.domain.respostas import responder
from processo_seletivo.editais.domain.documentos import NAO_SE_APLICA, OBRIGATORIO, aplicabilidade
from processo_seletivo.editais.domain.fase_do_evento import marcos_pendentes
from processo_seletivo.inscricoes.domain.periodo import evento_designado, periodo_de_inscricoes

#: O cartão que muda com a lista escolhida (ver o docstring do módulo).
SUFIXO_DA_OBRIGATORIEDADE = "/required"
#: A frase da `070` para a Retificação futura que "não altera o que esta resposta cita": verdade
#: sobre uma resposta, e não sobre o Edital. Aqui ela sai, e a Retificação vem dita à parte.
NAO_ALTERA_ESTA_RESPOSTA = re.compile(
    r"Há Retificação publicada com vigência a partir de [^.]*\. Ela não altera o que esta "
    r"resposta cita\.\s*"
)


def combinacoes(conteudo):
    """`(pergunta, perfil, modalidade)` de toda pergunta oferecida, com todo parâmetro possível."""
    for pergunta in catalogo.oferecidas(conteudo):
        if catalogo.PERFIL not in pergunta.parametros:
            yield pergunta.codigo, None, None
            continue
        for codigo, _ in catalogo.opcoes_de_perfil(conteudo):
            perfil = leitura.perfil_por_codigo(conteudo, codigo)
            if not catalogo.aplicavel_ao_perfil(pergunta.codigo, perfil, conteudo):
                continue
            if catalogo.MODALIDADE not in pergunta.parametros:
                yield pergunta.codigo, codigo, None
                continue
            for modalidade, _ in catalogo.opcoes_de_modalidade(perfil):
                yield pergunta.codigo, codigo, modalidade


def respostas_da_070(contexto: Contexto):
    """`(pergunta, resposta)` para toda combinação — o que as fontes reaproveitam."""
    for codigo, perfil, modalidade in combinacoes(contexto.conteudo):
        try:
            yield codigo, responder(contexto, codigo, perfil=perfil, modalidade=modalidade)
        except catalogo.ParametroRecusado:
            continue


def fontes_completas(contexto: Contexto, respostas=None) -> tuple[Fonte, ...]:
    """Todas as fontes da versão vigente no instante, em ordem canônica e com identificadores."""
    respostas = list(respostas if respostas is not None else respostas_da_070(contexto))
    cartoes: list[Referencia] = []
    vistos = set()
    avisos_futuros: list[str] = []
    desfecho = ""
    for codigo, resposta in respostas:
        for cartao in resposta.referencias:
            if cartao.natureza not in (TEXTO, DADO):
                continue
            if codigo == "P-05" and cartao.caminho.endswith(SUFIXO_DA_OBRIGATORIEDADE):
                continue
            chave = (cartao.natureza, cartao.caminho, cartao.posicao, cartao.localizacao)
            chave += (cartao.rotulo, cartao.conteudo)
            if chave in vistos:
                continue
            vistos.add(chave)
            cartoes.append(cartao)
        for aviso in resposta.avisos:
            if aviso.tipo == AVISO_RETIFICACAO_FUTURA:
                texto = NAO_ALTERA_ESTA_RESPOSTA.sub("", aviso.texto).strip()
                if texto and texto not in avisos_futuros:
                    avisos_futuros.append(texto)
            if aviso.tipo == AVISO_DESFECHO:
                desfecho = aviso.texto

    cartoes.extend(_secoes_que_nenhuma_pergunta_mostra(contexto, cartoes))
    fontes: list[Fonte] = []

    def acrescentar(**campos):
        fonte = Fonte(id=f"F{len(fontes) + 1}", **campos)
        fontes.append(fonte)
        return fonte

    for cartao in cartoes:
        fonte = acrescentar(
            natureza=cartao.natureza,
            lugar=cartao.localizacao,
            conteudo=cartao.conteudo,
            caminho=cartao.caminho,
            posicao=cartao.posicao,
            rotulo=cartao.rotulo,
            origens=cartao.origens,
            links=cartao.links,
            anexo=_e_de_anexo(cartao),
        )
        for valor in cartao.futuro:
            acrescentar(
                natureza=CALCULADA,
                lugar=cartao.localizacao,
                conteudo=_futuro_em_palavras(cartao, valor),
                rotulo=cartao.rotulo,
                origens=(valor.origem,) if valor.origem else (),
                altera=fonte.id,
            )
    for versao in contexto.futuras:
        acrescentar(
            natureza=CALCULADA,
            lugar="Retificação já publicada, de vigência futura",
            conteudo=(
                "Há Retificação já publicada que passa a vigorar em "
                f"{leitura.instante_legivel(versao.vigente_desde)}. Até lá, vale a versão vigente; "
                "as fontes calculadas que dizem “altera” trazem o que muda."
            ),
        )
    for texto in avisos_futuros:
        acrescentar(
            natureza=CALCULADA,
            lugar="Retificação já publicada, de vigência futura",
            conteudo=texto,
        )
    for lugar, conteudo in _documentos_por_perfil_e_lista(contexto.conteudo):
        # O caminho da coleção, para rastreio: é a obrigatoriedade dela que esta fonte diz.
        acrescentar(
            natureza=CALCULADA, lugar=lugar, conteudo=conteudo, caminho="/documentRequirements"
        )
    situacao = _situacao(contexto)
    if situacao:
        acrescentar(natureza=CALCULADA, lugar="Situação de calendário", conteudo=situacao)
    if desfecho:
        acrescentar(natureza=CALCULADA, lugar="Desfecho", conteudo=desfecho)
    return tuple(fontes)


def _secoes_que_nenhuma_pergunta_mostra(contexto: Contexto, cartoes):
    """Toda seção textual preenchida, inteira — as que as doze perguntas não mostram também.

    **Achado na implementação (13/10, `CB-08`).** A união das respostas só traz as seções que alguma
    pergunta da `070` trata ou acompanha, e as da `P-11` só pelo parágrafo em que a detecção do
    canal achou um contato. Uma seção fora dessas tabelas — as disposições preliminares de um Edital
    dos FIC, cuja cláusula de canal a detecção não reconhece — não chegava ao modelo, e o `FR-1472`
    pede o conteúdo completo. O guardião de cobertura não via, porque classifica as seções por
    padrão, e uma seção qualquer mostrada já o satisfazia. O cartão é o da `070` (`leitura.secao`),
    com a origem pela mesma proveniência.
    """
    inteiras = {
        cartao.caminho for cartao in cartoes if cartao.natureza == TEXTO and cartao.posicao is None
    }
    faltando = []
    for secao in contexto.conteudo.get("sections") or []:
        cartao = leitura.secao(contexto.conteudo, secao.get("key"))
        if cartao is None or cartao.caminho in inteiras:
            continue
        faltando.append(
            replace(cartao, origens=origens(cartao.caminho, contexto.proveniencias, contexto.atos))
        )
    return faltando


def _e_de_anexo(cartao: Referencia) -> bool:
    return "/attachments/" in cartao.caminho or cartao.caminho.endswith("/attachmentId")


def _futuro_em_palavras(cartao: Referencia, valor) -> str:
    ato = valor.origem
    publicada = f" em {leitura.instante_legivel(ato.publicado_em)}" if ato else ""
    campo = f" — {cartao.rotulo}" if cartao.rotulo else ""
    return (
        f"Retificação publicada{publicada}, vigente a partir de "
        f"{leitura.instante_legivel(valor.vigente_desde)}, altera {cartao.localizacao}{campo}: "
        f"passa a valer {valor.valor}."
    )


def _documentos_por_perfil_e_lista(conteudo):
    """A obrigatoriedade de cada documento, por Perfil e lista, pela regra única da `044`."""
    if not conteudo.get("documentRequirements"):
        return
    for perfil in conteudo.get("profiles") or []:
        listas = [(None, "sem modalidade (o que vale para todos neste Perfil)")]
        for modalidade in perfil.get("competitionModalities") or []:
            listas.append(
                (modalidade, f"modalidade {modalidade.get('code')} — {modalidade.get('name', '')}")
            )
        for modalidade, nome_da_lista in listas:
            vereditos = aplicabilidade(
                conteudo,
                profile_id=str(perfil.get("id")),
                modality_id=str(modalidade.get("id")) if modalidade else None,
            )
            obrigatorios, facultativos, divergentes = [], [], []
            for veredito in vereditos:
                nome = veredito.requisito.get("name", "")
                if veredito.situacao == NAO_SE_APLICA:
                    if veredito.divergente_do_publicado:
                        divergentes.append(nome)
                    continue
                (obrigatorios if veredito.situacao == OBRIGATORIO else facultativos).append(nome)
            partes = [
                f"obrigatórios — {', '.join(obrigatorios) or 'nenhum'}",
                f"facultativos — {', '.join(facultativos) or 'nenhum'}",
            ]
            if divergentes:
                partes.append(
                    "o nome publicado do grupo alcança também, embora a regra não: "
                    + ", ".join(divergentes)
                )
            yield (
                f"Documentos exigidos — Perfil {perfil.get('code')}, {nome_da_lista}",
                "; ".join(partes) + ".",
            )


def _situacao(contexto: Contexto) -> str:
    """O que está aberto, em andamento e por vir no instante; o desfecho prevalece (`FR-1429`)."""
    quando = leitura.instante_legivel(contexto.instante)
    if contexto.desfecho is not None and contexto.desfecho.do_edital:
        return (
            f"Situação em {quando}: o Edital teve desfecho, e as inscrições e as demais datas do "
            "cronograma não estão em curso."
        )
    partes = []
    evento = evento_designado(contexto.conteudo)
    if evento is not None:
        periodo = periodo_de_inscricoes(contexto.conteudo, contexto.instante)
        inicio = leitura.instante_legivel(evento.get("startAt"))
        fim = leitura.instante_legivel(evento.get("endAt")) if evento.get("endAt") else ""
        partes.append(explicacao.inscricoes(periodo, inicio, fim))
    em_andamento, por_vir = [], []
    for evento, _inicio, _fim, fase in marcos_pendentes(contexto.conteudo, contexto.instante):
        nome = f"“{leitura.nome_do_evento(evento).rstrip('.')}”"
        (em_andamento if fase == "EM_ANDAMENTO" else por_vir).append(nome)
    if em_andamento:
        partes.append(f"Em andamento: {', '.join(em_andamento)}.")
    if por_vir:
        partes.append(f"Por vir: {', '.join(por_vir)}.")
    if not partes:
        return ""
    return f"Situação em {quando}: " + " ".join(partes)


def resposta_de_referencia(respostas, codigo: str) -> Resposta | None:
    """A primeira resposta da `070` à pergunta — para o aviso de mudança de versão (T028)."""
    return next((resposta for cod, resposta in respostas if cod == codigo), None)
