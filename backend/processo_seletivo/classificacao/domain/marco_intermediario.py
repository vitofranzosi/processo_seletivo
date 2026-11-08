"""O marco intermediário: decide quem vai a uma Etapa que outro marco lê (133, FR-4530, D-001).

**O defeito que esta regra fecha.** No Edital 900 do estudo de convergência de 07/11/2026, a
*Classificação para a entrevista* tinha um corte que governava a Entrevista, e a *Classificação
final* lia a Entrevista. Nada no GPS distinguia os dois. O andamento mandava apurar a ocupação do
primeiro, o comando aceitava, e a convocação que vinha depois chamava para vaga quem tinha desistido
e quem ficara fora das vagas no marco final. A `016` apura "por recorte", em qualquer marco, e a
`040` já tinha registrado que não há definição inequívoca de "classificação final" (G-012 dela).

**A definição é a estreita, de propósito.** Um marco é intermediário quando a Etapa que o corte dele
governa é enumerada por **outro** marco do mesmo Perfil. Ela lê dois campos que não se retificam
depois da publicação (`mutabilidade.py`: `stages` e `cutRule/governedStage`), e por isso a
resposta é a mesma em todo instante da vida do Edital. O marco sem Etapa governada seguido de
outro **não** é intermediário: não há caso conhecido, e recusar por inferência um ato legítimo
seria pior que o defeito (decisão do usuário, 08/11/2026). Também não é o sorteio seguido de
uma Etapa de habilitação que nenhum marco lê: é o caso que a `127` trata como legítimo, em que
a apuração espera a Etapa.

**Pura.** Recebe o Perfil do conteúdo e responde; quem chama já tem o conteúdo vigente na mão.
"""

from processo_seletivo.classificacao.domain.faixa import etapa_governada


def _marcos(perfil):
    return (perfil or {}).get("classificationMilestones") or []


def marco_que_le(perfil, marco_id):
    """O outro marco do Perfil que enumera a Etapa governada por `marco_id`, ou `None`.

    Havendo mais de um, vale o primeiro na ordem do Perfil: só muda a frase, nunca a resposta.
    """
    marcos = _marcos(perfil)
    alvo = str(marco_id)
    marco = next((m for m in marcos if str(m.get("id")) == alvo), None)
    if marco is None:
        return None
    governada = etapa_governada(marco.get("cutRule"))
    if governada is None:
        return None
    return next(
        (
            outro
            for outro in marcos
            if str(outro.get("id")) != alvo
            and governada in {str(etapa) for etapa in outro.get("stages") or []}
        ),
        None,
    )


def e_intermediario(perfil, marco_id):
    return marco_que_le(perfil, marco_id) is not None


__all__ = ["e_intermediario", "marco_que_le"]
