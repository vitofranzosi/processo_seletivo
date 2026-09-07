"""A contagem do prazo recursal — função pura, e o erro de um dia que ela existe para impedir.

```text
exclui-se o dia do começo, inclui-se o do vencimento   a regra do processo administrativo
fecha ao fim do último dia, na zona institucional      23h59, e não 00h00
sem prorrogação                                        prorrogar exige calendário não publicado
```

**O erro de um dia aqui é o erro que tira o recurso de alguém.** Por isso a regra é escrita, e não
deduzida — e por isso cada caso tem um teste com a data por extenso, em vez de uma aritmética que
repetiria o mesmo engano da implementação.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from processo_seletivo.recursos.domain.janela import (
    ancora,
    computavel,
    contar,
    declaracao_do_marco,
)
from processo_seletivo.shared.tempo import ZONA

# Função pura: sem banco, sem marcador de integração — é o que permite a tabela-verdade inteira
# caber num teste unitário, como a `regra.py` da 013 já faz.

UTC = ZoneInfo("UTC")


def em(texto):
    """Um instante escrito na zona institucional, que é como o Edital o lê."""
    return datetime.fromisoformat(texto).replace(tzinfo=ZONA)


# ---------------------------------------------------------------------------
# T112 — a contagem
# ---------------------------------------------------------------------------


def test_exclui_o_dia_do_comeco_e_inclui_o_do_vencimento():
    """Publicado numa terça, o prazo de 5 dias fecha ao fim do domingo — e não do sábado."""
    _abre, fecha = contar(abertura=em("2026-09-08T14:30"), dias=5)

    assert fecha.astimezone(ZONA).date().isoformat() == "2026-09-13"


def test_fecha_ao_fim_do_ultimo_dia_e_nao_no_comeco_dele():
    """Quem interpõe às 23h59 do último dia está dentro do prazo."""
    _abre, fecha = contar(abertura=em("2026-09-08T14:30"), dias=5)

    local = fecha.astimezone(ZONA)
    assert (local.hour, local.minute) == (23, 59)
    assert em("2026-09-13T23:59") <= fecha
    assert em("2026-09-14T00:00") > fecha


def test_a_contagem_e_na_zona_institucional_e_nao_na_do_servidor():
    """**Publicar às 22h de São Paulo é publicar no dia 8**, e não no dia 9 em UTC.

    Sem a conversão, uma publicação da noite abriria o prazo no dia seguinte e o fecharia um dia
    depois — o erro cresce justamente perto da meia-noite, onde ele muda também o dia.
    """
    noite = datetime(2026, 9, 8, 22, 0, tzinfo=ZONA)

    _abre, fecha = contar(abertura=noite.astimezone(UTC), dias=5)

    assert fecha.astimezone(ZONA).date().isoformat() == "2026-09-13"


def test_um_dia_fecha_no_dia_seguinte():
    _abre, fecha = contar(abertura=em("2026-09-08T09:00"), dias=1)

    assert fecha.astimezone(ZONA).date().isoformat() == "2026-09-09"


def test_nao_prorroga_o_vencimento_que_cai_em_fim_de_semana():
    """Prorrogar exige o calendário de dias sem expediente, que o Edital não publica (D-004).

    O vencimento cai num sábado, e ali fica. Empurrá-lo para a segunda seria o sistema aplicando
    uma norma que ninguém escreveu — e errando para menos, contra quem recorre, sempre que o
    calendário real não coincidisse com o suposto.
    """
    _abre, fecha = contar(abertura=em("2026-09-07T10:00"), dias=5)

    local = fecha.astimezone(ZONA)
    assert local.date().isoformat() == "2026-09-12"
    assert local.weekday() == 5, "o vencimento cai num sábado, e permanece nele"


def test_a_abertura_e_o_instante_da_publicacao_e_nao_o_comeco_do_dia():
    """Publicação atrasada não produz prazo vencido antes de existir."""
    abertura = em("2026-09-08T18:42")

    abre, _fecha = contar(abertura=abertura, dias=5)

    assert abre == abertura


# ---------------------------------------------------------------------------
# A leitura da declaração
# ---------------------------------------------------------------------------


def test_janela_ausente_ou_nula_nao_e_computavel():
    """`None` significa **não declarada** — e não janela de zero dias (FR-028, FR-029)."""
    assert computavel(None) is None
    assert computavel({}) is None


def test_marco_que_nao_admite_recurso_nao_tem_janela_computavel():
    assert computavel({"admits": False, "durationDays": 5}) is None


def test_janela_sem_duracao_ou_com_duracao_nao_positiva_nao_e_computavel():
    """Declarada e não computável é o mesmo que não declarada, para quem lê.

    A validação da publicação recusa as duas como erro de conteúdo; aqui elas são lidas como
    ausência, porque um Edital já publicado com esse defeito não pode travar a leitura.
    """
    assert computavel({"admits": True}) is None
    assert computavel({"admits": True, "durationDays": 0}) is None
    assert computavel({"admits": True, "durationDays": -3}) is None


def test_unidade_diferente_de_dias_corridos_nao_e_computavel():
    assert computavel({"admits": True, "durationDays": 5, "unit": "DIAS_UTEIS"}) is None


def test_a_janela_declarada_e_lida_do_marco_no_conteudo():
    conteudo = {
        "profiles": [
            {
                "id": "p1",
                "classificationMilestones": [
                    {"id": "m1", "appealWindow": {"admits": True, "durationDays": 5}},
                    {"id": "m2", "appealWindow": None},
                ],
            }
        ]
    }

    assert declaracao_do_marco(conteudo, "m1") == {"admits": True, "durationDays": 5}
    assert declaracao_do_marco(conteudo, "m2") is None
    assert declaracao_do_marco(conteudo, "m3") is None


# ---------------------------------------------------------------------------
# T113 — a reabertura
# ---------------------------------------------------------------------------


class _Publicacao:
    """O mínimo que a âncora lê: identidade do ato, instante e a antecessora."""

    def __init__(self, ato_id, publicado_em, anterior=None):
        self.ato_id = ato_id
        self.publicado_em = publicado_em
        self.publicacao_anterior = anterior


def test_publicar_o_mesmo_ato_mudando_a_natureza_nao_abre_janela_nova():
    """Nada de novo foi divulgado para se contestar (FR-025).

    A comparação é por **identidade do ato**, e não por resumo do conteúdo: o resumo mudaria só por
    causa do rótulo da natureza no cabeçalho, e cada mudança de rótulo reabriria o prazo.
    """
    primeira = _Publicacao("ato-1", em("2026-09-08T10:00"))
    definitiva = _Publicacao("ato-1", em("2026-09-20T10:00"), anterior=primeira)

    assert ancora(definitiva) is primeira


def test_publicar_ato_diferente_abre_janela_nova():
    """Contra o conteúdo novo ninguém recorreu ainda."""
    primeira = _Publicacao("ato-1", em("2026-09-08T10:00"))
    corrigida = _Publicacao("ato-2", em("2026-09-20T10:00"), anterior=primeira)

    assert ancora(corrigida) is corrigida


def test_a_ancora_sobe_a_cadeia_inteira_do_mesmo_ato():
    """Numa cadeia de três republicações do mesmo ato, a âncora é a primeira de todas."""
    primeira = _Publicacao("ato-1", em("2026-09-08T10:00"))
    segunda = _Publicacao("ato-1", em("2026-09-10T10:00"), anterior=primeira)
    terceira = _Publicacao("ato-1", em("2026-09-12T10:00"), anterior=segunda)

    assert ancora(terceira) is primeira


def test_a_ancora_para_no_ato_diferente_mais_recente():
    primeira = _Publicacao("ato-1", em("2026-09-08T10:00"))
    nova = _Publicacao("ato-2", em("2026-09-10T10:00"), anterior=primeira)
    republicada = _Publicacao("ato-2", em("2026-09-12T10:00"), anterior=nova)

    assert ancora(republicada) is nova
    assert contar(abertura=ancora(republicada).publicado_em, dias=5)[1] > em("2026-09-14T00:00")
    assert timedelta(days=1) > timedelta(0)
