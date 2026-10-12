"""Os pontos para revisão antes da abertura pública, por Edital (070, `FR-1443`, `FR-1444`).

São condições da versão vigente que o setor de seleção precisa resolver — por Retificação ou por
decisão institucional — antes de o assistente abrir ao público naquele Edital. **Nada é corrigido
aqui, e nada é gravado** (`D-006`): o ponto é derivado do conteúdo imutável e dos atos, e só some
quando a versão muda. Marcar como resolvido seria uma segunda fonte, e uma decisão que não é desta
tela.
"""

from __future__ import annotations

from dataclasses import replace

from processo_seletivo.duvidas.domain import anexos, leitura
from processo_seletivo.duvidas.domain import canal as canais
from processo_seletivo.duvidas.domain.estruturas import (
    PONTO_ANEXO_CITADO_INEXISTENTE,
    PONTO_CANAIS_DIVERGENTES,
    PONTO_DOCUMENTO_DE_ORIGEM_INCOMPLETO,
    PONTO_EXCLUSIVIDADE_DO_CANAL,
    PONTO_RETIFICACAO_FUTURA,
    PontoParaRevisao,
)
from processo_seletivo.duvidas.domain.origem import origens
from processo_seletivo.duvidas.domain.respostas import documento_de_origem_incompleto

ANTES_DA_ABERTURA = "Resolver antes de abrir o assistente de dúvidas neste Edital."


def _com_origem(contexto, referencias):
    return tuple(
        replace(
            referencia, origens=origens(referencia.caminho, contexto.proveniencias, contexto.atos)
        )
        for referencia in referencias
    )


def pontos_para_revisao(contexto) -> tuple[PontoParaRevisao, ...]:
    pontos = []
    encontrado = canais.canal(contexto.conteudo, contexto.canal_institucional)
    paragrafos = _com_origem(contexto, encontrado.paragrafos)
    if encontrado.divergente:
        pontos.append(
            PontoParaRevisao(
                PONTO_CANAIS_DIVERGENTES,
                f"O Edital informa mais de um canal para dúvidas. {ANTES_DA_ABERTURA}",
                paragrafos,
            )
        )
    if encontrado.exclusividade:
        exclusivos = tuple(
            paragrafo for paragrafo in paragrafos if canais.exclusivo(paragrafo.conteudo)
        )
        pontos.append(
            PontoParaRevisao(
                PONTO_EXCLUSIVIDADE_DO_CANAL,
                "O Edital restringe as dúvidas a um canal (“exclusivamente”, “somente”, "
                f"“unicamente” ou “apenas”). {ANTES_DA_ABERTURA}",
                exclusivos,
            )
        )
    _encontrados, inexistentes = anexos.resolver(
        anexos.textos_do_conteudo(contexto.conteudo), contexto.conteudo
    )
    if inexistentes:
        citados = ", ".join(f"Anexo {identificador.upper()}" for identificador in inexistentes)
        pontos.append(
            PontoParaRevisao(
                PONTO_ANEXO_CITADO_INEXISTENTE,
                f"O texto do Edital cita {citados}, que não está entre os anexos publicados.",
            )
        )
    if contexto.futuras:
        datas = ", ".join(
            leitura.instante_legivel(versao.vigente_desde) for versao in contexto.futuras
        )
        pontos.append(
            PontoParaRevisao(
                PONTO_RETIFICACAO_FUTURA,
                f"Há Retificação publicada com vigência a partir de {datas}.",
            )
        )
    incompleto = documento_de_origem_incompleto(contexto)
    if incompleto:
        pontos.append(PontoParaRevisao(PONTO_DOCUMENTO_DE_ORIGEM_INCOMPLETO, incompleto))
    return tuple(pontos)
