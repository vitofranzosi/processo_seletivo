"""O que as telas e as mensagens do aviso dizem — e o que nunca dizem (066, `UX-171`, `UX-172`).

**Lista literal, e por isso precisa crescer junto.** Uma tela nova dos avisos que não entre aqui
escapa da regra em silêncio — o defeito que as varreduras com lista literal deste repositório já
tiveram. A lista abaixo é conferida contra os templates que existem, para que um renome não a faça
varrer arquivo nenhum.

**"Aceita pelo servidor de correio", e nunca entregue, recebida ou lida** (`UX-172`). O sistema sabe
o que o servidor respondeu; o que aconteceu na caixa de entrada da pessoa ele não sabe, e não
afirma. **E "aviso", e nunca "notificação oficial"** (`UX-171`): o aviso não é o ato.
"""

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1] / "processo_seletivo"
TEMPLATES = RAIZ / "interface/templates/interface"

DA_066 = [
    TEMPLATES / "aviso_previa.html",
    TEMPLATES / "aviso.html",
    TEMPLATES / "aviso_interromper.html",
    TEMPLATES / "avisos_do_edital.html",
    TEMPLATES / "modelos_de_aviso.html",
    TEMPLATES / "modelo_de_aviso.html",
    RAIZ / "avisos/domain/nomes.py",
    RAIZ / "avisos/domain/mensagem.py",
    RAIZ / "avisos/domain/modelos_iniciais.py",
]

#: O que nenhuma superfície dos avisos afirma. Por palavra inteira: "lida" não pode casar com
#: "modalidade", e "recebida" não pode casar com "recebidas" só por estar no plural — as duas
#: formas são igualmente falsas, e por isso a expressão cobre o plural.
PROIBIDOS = (
    r"\bentregues?\b",
    r"\brecebidas?\b",
    r"\blidas?\b",
    r"\bnotificaç(ão|ões) oficia(l|is)\b",
)


def _sem_prosa(texto):
    """O arquivo sem comentário: explicar por que a palavra é proibida não é usá-la."""
    texto = re.sub(r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", " ", texto, flags=re.S)
    texto = re.sub(r'""".*?"""', " ", texto, flags=re.S)
    return re.sub(r"#[^\n]*", " ", texto)


def test_a_lista_literal_alcanca_toda_tela_dos_avisos():
    assert all(arquivo.exists() for arquivo in DA_066)
    telas = {p.name for p in TEMPLATES.glob("*aviso*.html")} - {"_estilo_do_aviso.html"}
    assert telas == {p.name for p in DA_066 if p.suffix == ".html"}


@pytest.mark.parametrize("arquivo", DA_066, ids=lambda p: p.name)
def test_nenhuma_superficie_afirma_entrega_recebimento_ou_leitura(arquivo):
    texto = _sem_prosa(arquivo.read_text(encoding="utf-8")).lower()

    achados = [padrao for padrao in PROIBIDOS if re.search(padrao, texto)]

    assert achados == [], f"{arquivo.name} afirma o que o sistema não sabe: {achados}"


def test_o_historico_diz_aceita_pelo_servidor():
    from processo_seletivo.avisos.domain import nomes

    assert nomes.ROTULO_DO_ESTADO[nomes.ESTADO_ACEITA] == "aceita pelo servidor de correio"
