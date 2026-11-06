"""A ordem por pontuação sem nenhum resultado não se emite (128, G-01, opção b).

**A ordem nascia antes de qualquer avaliação.** No marco por pontuação de um Edital em que ninguém
fora avaliado, a tela oferecia "Emitir ordem", e o ato saía com todos sem posição: obsoleto assim
que o primeiro resultado chegasse, e com a sucessão exigindo motivo. Não há uso legítimo conhecido
para ele, e o usuário decidiu recusá-lo em 06/11/2026. A ordem parcial e a de universo vazio
continuam.

**Uma regra, lida em quatro lugares** (D-004): o comando, que é a porta de gravação e por onde
passam a sucessão e o gesto da condução; a conferência do gesto, que põe o recorte entre os
impedidos; a tela da ordem, que deixa de oferecer o formulário; e a confirmação da `126`. Todos já
têm a proposta calculada, e por isso a regra a lê, sem consulta: uma pergunta separada ao banco
seria um segundo universo, sem a progressão e a faixa do corte que o cálculo aplica.
"""

from processo_seletivo.classificacao.domain.universo_classificavel import nenhuma_com_resultado
from processo_seletivo.shared.api.problems import DomainError

CODIGO = "ordering_without_stage_results"


def impedimento(proposta):
    """`None`, ou `{inscricoes, etapas, frase}` quando a regra recusaria a emissão desta proposta.

    `etapas` é `[(id, nome publicado)]`, na ordem em que o marco as enumera; a tela as usa para
    levar à distribuição de cada uma.
    """
    marco = proposta.get("marco") or {}
    linhas = list(proposta.get("posicoes") or []) + list(proposta.get("sem_posicao") or [])
    if not nenhuma_com_resultado(marco, linhas):
        return None
    conteudo_das_etapas = proposta.get("etapas") or {}
    etapas = [
        (str(etapa), conteudo_das_etapas[str(etapa)].get("name") or str(etapa))
        for etapa in marco.get("stages") or []
        if str(etapa) in conteudo_das_etapas
    ]
    return {
        "inscricoes": len(linhas),
        "etapas": etapas,
        "frase": _frase(len(linhas), [nome for _, nome in etapas]),
    }


def recusar(proposta):
    """Levanta a recusa quando há impedimento; sem ele, não faz nada."""
    achado = impedimento(proposta)
    if achado is None:
        return
    raise DomainError(CODIGO, achado["frase"], 422, campo="marco")


def _frase(quantas, nomes):
    # A frase diz quantas, onde e o caminho, nessa ordem (UX-260). "Distribuir, avaliar e
    # consolidar" é o caminho inteiro: dizer só "consolide" mandaria à consolidação de uma Etapa sem
    # avaliação.
    sujeito = (
        "A inscrição deste recorte não tem"
        if quantas == 1
        else f"Nenhuma das {quantas} inscrições deste recorte tem"
    )
    if not nomes:
        # Não acontece pelo cálculo, que recusa antes o marco sem Etapa publicada
        # (`marco_sem_etapa`).
        onde, quais = "nas Etapas que o marco enumera", "dessas Etapas"
    elif len(nomes) == 1:
        onde, quais = f"na Etapa {nomes[0]}", "dessa Etapa"
    else:
        onde, quais = f"nas Etapas {_juntar(nomes)}", "dessas Etapas"
    return (
        f"{sujeito} resultado {onde}. Para emitir a ordem, distribua as inscrições, avalie e "
        f"consolide os resultados {quais}."
    )


def _juntar(nomes):
    return nomes[0] if len(nomes) == 1 else ", ".join(nomes[:-1]) + " e " + nomes[-1]


__all__ = ["CODIGO", "impedimento", "recusar"]
