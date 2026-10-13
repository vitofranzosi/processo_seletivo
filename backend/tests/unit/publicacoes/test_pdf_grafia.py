"""Caractere sem grafia — o documento oficial não troca caractere por `?` em silêncio.

O renderizador codificava em cp1252 com `"replace"`, e o Edital 90/2026 (Tutor TADS) saiu na prévia
com uma interrogação no lugar de cada marcador das atribuições, coladas do Word com `●` e espaço de
largura zero. Nenhum teste via, porque nenhum usava caractere fora do cp1252 — todos os extratores
decodificam cp1252, e o `?` decodifica sem erro.

Três garantias, e a terceira é a que impede a regressão silenciosa:

- o que a lista de `grafia` resolve sai resolvido, no publicado e na prévia;
- o que ela não resolve **falha** no publicado e aparece como `[U+…]` na prévia, nunca como `?`;
- todo texto que chega ao papel passa pela validação — conferido injetando o caractere em cada
  texto de um snapshot máximo, e não pela memória de quem escreveu a lista de campos.
"""

import copy

import pytest

from processo_seletivo.editais.domain.validation import (
    CARACTERE_SEM_GRAFIA,
    FORMATO_INVALIDO,
    RESTRICAO_VIOLADA,
    blocking_findings,
    validate_for_publication,
)
from processo_seletivo.publicacoes.infrastructure.pdf import (
    CORPO_TEXTO,
    MODO_PREVIA,
    CaractereSemGrafia,
    Composicao,
    largura,
    render_documento,
)
from tests.fixtures.snapshot import anexo, rascunho_completo
from tests.unit.publicacoes.test_pdf import documento, snapshot, texto_de


def _com_atribuicoes(texto):
    conteudo = snapshot()
    conteudo["profiles"][0]["duties"] = texto
    return conteudo


# As atribuições do Edital 90/2026 como chegaram ao banco: o marcador do Word, o espaço de largura
# zero colado depois dele, e a quebra de linha entre os itens.
ATRIBUICOES_DO_90 = (
    "\u25cf\u200b Conhecer o projeto pedagógico do curso;\n"
    "\u25cf\u200b Mediar as atividades no ambiente virtual."
)


@pytest.mark.parametrize("modo", [None, MODO_PREVIA])
def test_as_atribuicoes_do_edital_90_saem_com_o_marcador(modo):
    texto = texto_de(documento(_com_atribuicoes(ATRIBUICOES_DO_90), modo=modo))

    assert "• Conhecer o projeto pedagógico do curso;" in texto
    assert "• Mediar as atividades no ambiente virtual." in texto
    assert "? Conhecer" not in texto
    assert "\u200b" not in texto


def test_texto_decomposto_sai_composto():
    import unicodedata

    texto = texto_de(documento(_com_atribuicoes(unicodedata.normalize("NFD", "Orientação"))))
    assert "Orientação" in texto
    assert "Orienta?" not in texto


def test_separador_de_linha_do_word_separa_paragrafo():
    """Normalizado antes de compor: `_paragrafos` só conhece `\\n`, e o separador o vira."""
    texto = texto_de(documento(_com_atribuicoes("Primeiro item.\u2028Segundo item.")))
    assert "Primeiro item.\nSegundo item." in texto


def test_o_invisivel_nao_ocupa_largura():
    """Medido antes, o espaço de largura zero contava como o glifo mais largo da fonte."""
    assert largura("plane\u200bjar", CORPO_TEXTO) == largura("planejar", CORPO_TEXTO)


def test_o_publicado_recusa_o_caractere_que_a_lista_nao_resolve():
    """A segunda camada: se a validação deixou passar, a publicação falha — e não sai com `?`."""
    with pytest.raises(CaractereSemGrafia, match="U\\+2265"):
        documento(_com_atribuicoes("Experiência ≥ 2 anos."))


def test_a_previa_mostra_o_codigo_no_lugar_do_caractere():
    texto = texto_de(documento(_com_atribuicoes("Experiência ≥ 2 anos."), modo=MODO_PREVIA))

    assert "Experiência [U+2265] 2 anos." in texto
    assert "Experiência ? 2 anos." not in texto


def test_o_marcador_vazado_nao_e_normalizado():
    """Decisão de 08/10: `◦` é o segundo nível da lista, e `•` o apagaria."""
    texto = texto_de(documento(_com_atribuicoes("◦ Subitem"), modo=MODO_PREVIA))
    assert "[U+25E6] Subitem" in texto
    with pytest.raises(CaractereSemGrafia):
        documento(_com_atribuicoes("◦ Subitem"))


def test_os_outros_documentos_continuam_sem_recusar():
    """Comprovante e divulgação imprimem nome de candidato, que nenhuma validação alcança.

    Neles o `?` continua — é registro à parte no achado —, mas a normalização vale.
    """
    composicao = Composicao()
    composicao.escrever("● Nome com ≥", tamanho=CORPO_TEXTO)
    texto = texto_de(render_documento(composicao, identificacao="Comprovante"))
    assert "• Nome com ?" in texto


# ---------------------------------------------------------------------------
# O guarda: todo texto que chega ao papel passa pela validação
# ---------------------------------------------------------------------------


def snapshot_maximo():
    """O máximo que o documento imprime: o Edital da suíte do PDF com as coleções do rascunho
    completo, e o que nenhum dos dois traz — Anexo, Requerimento e os rótulos de Etapa decisória.
    """
    conteudo = snapshot(**rascunho_completo())
    decisoria = conteudo["stages"][1]
    decisoria.update(forma="DECISORIA", rotuloFavoravel="Apto", rotuloDesfavoravel="Inapto")
    conteudo["attachments"] = [
        anexo(
            "00000000-0000-0000-0000-0000000009a1",
            "ANEXO I — Formulário",
            1,
            "00000000-0000-0000-0000-0000000009b1",
        )
    ]
    conteudo["matriculationRequest"] = {
        "moment": "APOS_RESULTADO",
        "declarationText": "Declaro serem verdadeiras as informações.",
    }
    return conteudo


def _textos(valor, caminho=()):
    if isinstance(valor, str):
        yield caminho
    elif isinstance(valor, dict):
        for chave, item in valor.items():
            yield from _textos(item, (*caminho, chave))
    elif isinstance(valor, list):
        for posicao, item in enumerate(valor):
            yield from _textos(item, (*caminho, posicao))


def _injetado(conteudo, caminho, sufixo):
    alterado = copy.deepcopy(conteudo)
    alvo = alterado
    for passo in caminho[:-1]:
        alvo = alvo[passo]
    alvo[caminho[-1]] += sufixo
    return alterado


# O que o documento imprime e esta regra não confere, com a razão de cada um. Não é texto livre:
# é enumeração que a tela só oferece como escolha.
NAO_SAO_TEXTO_LIVRE = {("matriculationRequest", "moment")}


def test_todo_texto_impresso_passa_pela_validacao():
    """Injeta `≥` em cada texto do snapshot máximo, um por vez.

    Onde o documento publicado o recusa, a validação precisa tê-lo recusado antes — pela regra do
    caractere, ou, nos campos estruturais, pela da forma (data, decimal, enumeração inválidos). Um
    campo que o renderizador passe a imprimir sem que a regra o percorra reprova aqui, e não no
    primeiro Edital que alguém colar do Word.
    """
    base = snapshot_maximo()
    documento(base)
    ja_recusados = {
        (item.code, item.path) for item in blocking_findings(validate_for_publication(base))
    }
    impressos, buracos = 0, []
    for caminho in _textos(base):
        if caminho in NAO_SAO_TEXTO_LIVRE:
            continue
        alterado = _injetado(base, caminho, " ≥")
        try:
            documento(alterado)
            continue
        except CaractereSemGrafia:
            impressos += 1
        except (ValueError, TypeError, KeyError):
            # O renderizador não compõe o campo estrutural adulterado; nada chega ao papel.
            continue
        novos = {
            codigo
            for codigo, _ in {
                (item.code, item.path)
                for item in blocking_findings(validate_for_publication(alterado))
            }
            - ja_recusados
        }
        if not novos & {CARACTERE_SEM_GRAFIA, FORMATO_INVALIDO, RESTRICAO_VIOLADA}:
            buracos.append(caminho)
    assert buracos == []
    # Se o snapshot encolher, o guarda passa sem guardar nada.
    assert impressos > 100
