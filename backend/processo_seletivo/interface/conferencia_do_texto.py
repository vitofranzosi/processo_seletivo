"""A conferência do texto que chega ao candidato, antes do ato (125, FR-3993 a FR-3997, D-004).

**O texto livre continua chegando ao candidato** — o complemento do fundamento e o fundamento do
desfecho —, por decisão do usuário de 06/11/2026. O que esta etapa acrescenta é que quem
escreve **veja o texto como o candidato o verá**, e **a quantas pessoas** ele vai, antes do botão
que pratica o ato. Um operador que escreva *"vaga aberta pela desistência de ‹nome›"* num lote
expõe a todos.

**Um passo do servidor, e não um script.** A CSP recusa script no template (091, 092), e a prévia
precisa funcionar sem ele (FR-3995). A composição é a mesma que o ato grava — a da
`convocacao/domain/fundamento.py` —, e não uma segunda feita no navegador (FR-3993).

**Só com texto digitado** (D-004): sem complemento, o fundamento derivado já está na tela, rotulado
*"O candidato lerá este fundamento"*, e o formulário confirma direto, como sempre. O desfecho exige
fundamento, e por isso passa sempre por aqui.

**A prévia assina o texto** (R-006). A confirmação recompõe e compara o resumo: se o fundamento
derivado mudou entre a prévia e o clique — outra apuração, outra versão —, ou se o operador editou o
texto na própria prévia, ela não pratica nada, e volta com a prévia nova à vista. A chave de
idempotência e a assinatura do alcance viajam intactas, e as garantias de hoje continuam as do
comando (FR-3996).

**A sessão é o portador**, como do resultado e do erro de hoje: a tela seguinte a consome.
"""

import hashlib

from django.shortcuts import redirect

CHAVE = "conferencia_do_texto"
#: O campo de texto livre de cada gesto. O desfecho e o indeferimento escrevem o fundamento inteiro;
#: os demais, o complemento que entra depois do derivado.
CAMPO = {"desfecho": "fundamento", "indeferimento": "fundamento"}
ROTULO_DO_CAMPO = {
    "fundamento": "Fundamento",
    "complemento": "Complemento do fundamento",
}
#: O que não volta como campo oculto: o token é renovado pela tela, a etapa e o resumo são desta
#: conferência, e o texto volta editável.
_FORA = {"csrfmiddlewaretoken", "etapa", "texto_conferido"}
TEXTO_MUDOU = (
    "O texto mudou desde a prévia — o fundamento derivado foi atualizado, ou o texto foi editado. "
    "Confira o texto abaixo antes de confirmar."
)


def campo_de(acao):
    return CAMPO.get(acao, "complemento")


def resumo(texto, pessoas):
    """O que a prévia assina: o texto composto e o número de pessoas, juntos."""
    return hashlib.sha256(f"{pessoas}\n{texto}".encode()).hexdigest()[:32]


def exigir(request, *, acao, compor, destino):
    """A resposta da conferência, ou `None` quando o ato pode ser praticado agora.

    `compor()` devolve `(texto, pessoas, rotulo_da_previa, rotulo_do_botao)`: o texto **como o
    candidato o lê**, o número de atos que a confirmação praticará, o rótulo sob o qual o portal o
    mostra e o do botão do ato. Só é chamada com texto digitado, porque compor lê o recorte; devolve
    `None` quando não há o que compor — a recusa, então, é a do comando, como sempre.
    """
    campo = campo_de(acao)
    digitado = (request.POST.get(campo) or "").strip()
    if not digitado:
        return None
    composto = compor()
    if composto is None:
        return None
    texto, pessoas, rotulo_da_previa, rotulo_do_botao = composto
    assinado = resumo(texto, pessoas)
    etapa = request.POST.get("etapa") or ""
    if etapa == "confirmar" and request.POST.get("texto_conferido") == assinado:
        return None
    request.session[CHAVE] = {
        "acao": acao,
        "url": request.path,
        "campos": {
            chave: valor
            for chave, valor in request.POST.items()
            if chave not in _FORA and chave != campo
        },
        "campo": campo,
        "rotuloDoCampo": ROTULO_DO_CAMPO[campo],
        "digitado": digitado,
        "previa": {"rotulo": rotulo_da_previa, "texto": texto},
        "pessoas": pessoas,
        "resumo": assinado,
        "rotuloDoBotao": rotulo_do_botao,
        "erro": TEXTO_MUDOU if etapa == "confirmar" else "",
    }
    return redirect(f"{destino}#conferir-o-texto")


def da_sessao(request):
    """A conferência pendente, consumida pela tela que a mostra."""
    return request.session.pop(CHAVE, None)
