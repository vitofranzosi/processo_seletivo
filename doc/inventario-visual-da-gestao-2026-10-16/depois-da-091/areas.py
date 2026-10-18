"""A área de cada regra da folha comum (091, R-002).

    areas.py <gestao.css>   → imprime a contagem por área e grava `areas.json`

A classificação é por **assunto** do seletor, e não por linha: a folha está em ordem de chegada, e o
mesmo trecho mistura tabela, campo e tela. Primeiro os trechos que são de uma área só por inteiro (o
shell, a impressão); depois, regra a regra, pelas palavras do seletor, da mais específica à mais
geral — uma regra que cita uma tela é da tela, mesmo que fale de tabela ou de campo. O resultado é a
área **desejada**; a final sai da prova de ordem (`ordem.py`), que devolve uma regra para depois
quando ela disputa propriedade com outra que ficaria antes dela.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from unidades import ler  # noqa: E402

# Na ordem em que as folhas carregam: da mais geral à mais específica. A impressão logo depois da
# moldura, e não no fim: o `@media print` da 088 estava ali, e disputa propriedade com centenas de
# regras que vêm depois dele — no fim, ele passaria a vencê-las no papel (R-002 da 091).
AREAS = ("base", "moldura", "impressao", "componentes", "formularios", "tabelas", "telas")

# Palavras de seletor que dizem a tela (ou o painel de uma tela só). Uma regra que cita uma delas é
# da tela, ainda que seja de tabela ou de campo.
TELAS = (
    "distribuicao", "etapa-medida", "etapa-nome", "coluna-toda", "ligacao", "gerir-membro",
    "assistente", "auditoria", "recortes", "organizacao-etapas", "comissao", "sinais", "serie",
    "medidor", "sem-distribuicao", "atribuicoes", "acao-do-cartao", "conferencia-lote",
    "alocar-em-lote", "remover-em-lote", "processo", "sem-edital", "quadro", "linha-do-quadro",
    "modalidades", "marcos", "exclusoes", "grupo-empatado", "consequencias", "fundamentacao",
    "motivacao", "julgado", "instruido", "reabilitada", "citacoes", "historico-do-par",
    "dados-da-inscricao", "retiradas", "filtros-da-mesa", "motivo-da-prontidao",
    "resultado-do-lote", "lista-da-mesa", "autoridades", "ficha", "ausente", "documentos",
    "registro-da-avaliacao", "mesa-trabalho", "painel-documento", "barra-do-painel",
    "pagina-da-inscricao", "painel-avaliacao", "coincidencia", "bloco-do-marco", "metodo",
    "ocorrencia", "recorte", "descartadas", "passos-da-anulacao", "indice", "secao-da-retificacao",
    "filtro-da-retificacao", "barra-de-acoes", "object.documento", "identificar", "papel",
    "perms", "participantes", "acoes-do-anexo", "acrescentar", "resumo-da-origem", "lista-acoes",
    "bastao", "acoes-do-painel", "navegacao-etapa", "contadores", "resumo-lista", "em-colunas",
    "etapa:has", "perfil-novo", "aninhada", "data-alterado", "alterad", "categor", "data-or",
    "reabertura", "motivos", "fatos-fixos", "definicoes", "declaracao-derivada", "como-preencher",
    "impedimentos", "trilha", "pendencias", "p-erro", "p-aviso", "marcador", "tudo-certo",
    "parecer-registrado", "codigo-de-verificacao", "linha-de-acoes", "atua", "adicionar",
)
TABELAS = (
    "table", "thead", "tbody", "caption", "th", "td", "tr", "tabela", "rolagem", "paginacao",
)
FORMULARIOS = (
    "campo", "campos", "input", "select", "textarea", "label", "fieldset", "legend", "opcoes",
    "opcao", "dependentes", "escolha", "filtro", "filtros", "salvar", "obrigatorio", "opcional",
    "erro", "recusa", "curto", "largo", "arquivo", "caracter", "linha", "form",
)
BASE = ("*", "body", "a", "main", "h1", "h2", "h3", "p", "pular", "dfn", "hidden")


def palavras(seletor):
    """As palavras de um seletor: classes, elementos, atributos, cada uma sem o sinal."""
    return set(re.findall(r"[A-Za-z*][\w-]*(?::has|\.documento)?", seletor)) | (
        {"*"} if "*" in seletor else set()
    )


def area_da_regra(cabeca, linha, regra=""):
    if cabeca.startswith("@media print"):
        return "impressao"
    # O cabeçalho do topo (as telas sem barra) e o shell da 076, das linhas 17 a 179 (contadas no
    # arquivo da 090 com a regra dos símbolos): a moldura inteira.
    if 17 <= linha < 180 or cabeca.startswith("header.topo"):
        return "moldura"
    # Um bloco `@media` é da área das regras de dentro, e não da condição.
    texto = re.sub(r"/\*.*?\*/", "", regra, flags=re.S) if cabeca.startswith("@") else cabeca
    for nome in TELAS:
        # Prefixo, e não palavra inteira: `.distribuicao-moldura` é da Distribuição.
        if re.search(rf"(?<![\w-]){re.escape(nome)}", texto):
            return "telas"
    p = palavras(texto)
    if re.search(r"\.s-[A-Z]", texto):
        return "componentes"
    if p & set(TABELAS) or any(w.startswith("tabela") for w in p):
        return "tabelas"
    if p & set(FORMULARIOS):
        return "formularios"
    if p and p <= set(BASE) | {"focus", "focus-visible", "hover", "first-child", "last-child"}:
        return "base"
    return "componentes"


def classificar(caminho):
    unidades, resto = ler(Path(caminho).read_text(), origem=str(caminho))
    for u in unidades:
        u.area = area_da_regra(u.cabeca, u.linha, u.regra)
    return unidades, resto


if __name__ == "__main__":
    unidades, _ = classificar(sys.argv[1])
    contagem = {a: sum(u.area == a for u in unidades) for a in AREAS}
    print(contagem)
    Path(Path(__file__).parent / "areas.json").write_text(
        json.dumps(
            [{"indice": u.indice, "linha": u.linha, "cabeca": u.cabeca, "area": u.area} for u in unidades],
            ensure_ascii=False,
            indent=0,
        )
    )
    for a in AREAS:
        print("==", a)
        for u in unidades:
            if u.area == a:
                print(f"  {u.linha:5} {u.cabeca[:100]}")
