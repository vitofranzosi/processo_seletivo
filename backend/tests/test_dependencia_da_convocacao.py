"""A seta de dependência corre num sentido só, e isto é prova de import — não de texto (019).

`convocacao` lê `ocupacao`, `classificacao` e `resultados`. **Nenhum deles a conhece**, e não pode
passar a conhecer: a `D-006` fixou que a exclusão e a inclusão chegam por uma porta que a `016`
define, e o `R-003` registrou por que a porta guarda o ato de origem como UUID opaco — uma FK na
direção contrária inverteria a dependência **no grafo de migrations**, que é onde ela é
irreversível. A `016` passaria a não poder migrar sem a `019`.

**Varredura de texto não cobre isto.** Ela prova que a tela não *diz* que convocou; não prova que
nenhum caminho *convoca*. É a mesma divisão que `test_vocabulario_da_ocupacao.py` e
`test_dependencia_da_ocupacao.py` já fazem, aplicada à fronteira seguinte.

**E a `FR-270` também é estrutural**: mover quantidade entre recortes é a reversão da `016`, que é
ato declarado, motivado e registrado. Provar por texto que nenhuma tela diz "moveu" deixaria de
fora o caminho que move sem dizer.
"""

import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1] / "processo_seletivo"

# Os três módulos que a `019` lê, e que não podem lê-la de volta.
A_MONTANTE = ("ocupacao", "classificacao", "resultados")


def modulos(app):
    return [
        caminho
        for caminho in (RAIZ / app).rglob("*.py")
        if "migrations" not in caminho.parts and "__pycache__" not in caminho.parts
    ]


def importados(caminho):
    """Os módulos que este arquivo importa — **inclusive os importados dentro de função**.

    O import tardio é o recurso que este repositório usa para quebrar ciclo em Python, e por isso
    a varredura desce a árvore inteira: um `from processo_seletivo.convocacao import ...` escondido
    dentro de um `def` inverteria a dependência do mesmo jeito, e passaria despercebido numa
    leitura só do topo do arquivo.
    """
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    nomes = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
    return nomes


@pytest.mark.parametrize("app", A_MONTANTE)
def test_nenhum_modulo_a_montante_importa_convocacao(app):
    culpados = {
        str(caminho.relative_to(RAIZ)): sorted(
            nome for nome in importados(caminho) if "convocacao" in nome
        )
        for caminho in modulos(app)
    }
    achados = {arquivo: nomes for arquivo, nomes in culpados.items() if nomes}

    assert achados == {}, (
        f"{app} passou a importar `convocacao`: a seta inverteu, e a `016` deixa de migrar "
        f"sozinha — {achados}"
    )


@pytest.mark.parametrize("app", A_MONTANTE)
def test_nenhuma_migration_a_montante_depende_de_convocacao(app):
    """**É aqui que a inversão seria irreversível.**

    Em Python um import invertido se desfaz refatorando; no grafo de migrations ele fica: a
    dependência entra numa migration aplicada, e migrations aplicadas não se reescrevem.
    """
    pasta = RAIZ / app / "migrations"
    culpadas = {}
    for caminho in sorted(pasta.glob("0*.py")):
        arvore = ast.parse(caminho.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            if isinstance(no, ast.Constant) and no.value == "convocacao":
                culpadas.setdefault(caminho.name, []).append("dependência declarada")
            if isinstance(no, (ast.Import, ast.ImportFrom)):
                alvo = getattr(no, "module", "") or ""
                if "convocacao" in alvo:
                    culpadas.setdefault(caminho.name, []).append(alvo)

    assert culpadas == {}, f"{app} passou a depender de `convocacao` no grafo de migrations"


def test_a_porta_guarda_o_ato_de_origem_como_identidade_opaca():
    """`R-003`: é o que permite a `016` registrar o efeito sem conhecer quem o produziu."""
    from processo_seletivo.ocupacao.models import EfeitoDeOcupacao

    campos = {campo.name: campo for campo in EfeitoDeOcupacao._meta.get_fields()}

    assert campos["ato_de_origem_id"].get_internal_type() == "UUIDField"
    assert "ato_de_origem" not in campos
    assert campos["rotulo_da_origem"], "e o rótulo é o que torna a trilha legível (FR-296)"


def test_o_resultado_por_regularizacao_cita_o_desfecho_como_identidade_opaca():
    """`R-005`, pela mesma razão: `resultados` não pode depender de `convocacao`.

    A integridade referencial existe, e vem do outro lado — o desfecho tem FK
    `resultado_sucessor` para `ResultadoEtapa`, e os dois nascem na mesma transação.
    """
    from processo_seletivo.convocacao.models import DesfechoDaConvocacao
    from processo_seletivo.resultados.models import ResultadoEtapa

    campos = {campo.name: campo for campo in ResultadoEtapa._meta.get_fields()}
    assert campos["desfecho_de_convocacao_id"].get_internal_type() == "UUIDField"
    assert "desfecho_de_convocacao" not in campos

    do_outro_lado = {campo.name for campo in DesfechoDaConvocacao._meta.get_fields()}
    assert "resultado_sucessor" in do_outro_lado


class TestNenhumCaminhoMoveQuantidadeEntreRecortes:
    """`FR-270`, `T088a`: mover quantidade é a reversão da `016`, e ela é ato declarado.

    **Prova de texto não cobre isto**, e é por isso que a tarefa pede prova estrutural: uma tela que
    não diga "moveu" continuaria movendo se algum caminho desta feature gravasse `MovimentoDeVaga`
    ou escrevesse num recorte diferente do que recebeu.
    """

    def test_nenhum_modulo_da_019_grava_movimento_de_vaga(self):
        culpados = {
            str(caminho.relative_to(RAIZ)): sorted(
                nome for nome in importados(caminho) if "movimento" in nome
            )
            for caminho in modulos("convocacao")
        }
        achados = {arquivo: nomes for arquivo, nomes in culpados.items() if nomes}

        assert achados == {}, f"a `019` passou a mexer em movimento de vaga — {achados}"

    def test_o_efeito_nasce_no_recorte_da_convocacao_e_em_nenhum_outro(self):
        """O efeito copia o recorte do ato que o produziu, e não recebe um recorte de fora.

        **Aceitar um recorte por parâmetro seria a porta por onde a quantidade atravessaria**: uma
        exclusão gravada na ampla a partir de um desfecho da reserva tiraria da reserva uma vaga
        que ela nunca cedeu, sem movimento, sem motivo e sem registro.
        """
        origem = (RAIZ / "convocacao/application/desfechar.py").read_text(encoding="utf-8")
        chamada = origem[origem.index("porta_de_efeitos.registrar_efeito(") :]
        chamada = chamada[: chamada.index(")\n")]

        for campo in ("perfil_id", "marco_id", "lista_id", "edital"):
            assert f"{campo}=convocacao." in chamada or f"{campo}=convocacao\n" in chamada, (
                f"{campo} do efeito precisa vir da própria convocação"
            )

    def test_a_apuracao_le_efeitos_do_proprio_recorte(self):
        """E do outro lado a leitura é igualmente fechada: `lista_id` entra no filtro.

        Sem ele, um efeito da reserva apareceria na contagem da ampla — que é a mesma travessia
        vista pelo lado de quem conta.
        """
        origem = (RAIZ / "ocupacao/application/efeitos.py").read_text(encoding="utf-8")
        consulta = origem[origem.index("def efeitos_do_recorte(") :]

        for campo in ("edital=edital", "perfil_id=perfil_id", "marco_id=marco_id", "lista_id="):
            assert campo in consulta
