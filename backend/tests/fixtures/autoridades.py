"""A Unidade e as autoridades que a suíte inteira pressupõe (060, R-012).

**Por que uma fixture `autouse`, e não uma data migration.** Um terço dos casos é transacional, e o
Django os limpa truncando todas as tabelas. Qualquer linha que uma migration criasse sumiria depois
do primeiro deles, e a suíte passaria a falhar conforme a ordem — o pior tipo de falha, porque não
se reproduz isolada. Ligar `serialized_rollback` resolveria ao custo de serializar o banco em cada
caso transacional, numa suíte que já leva de 12 a 18 minutos.

**Os valores imitam o que os testes já conferiam.** `AUTORIDADE_DA_SUITE` tem o identificador, o
nome e o cargo do dicionário `SIGNATORY` que a publicação de Edital mandava antes da 060; e
`AUTORIDADE_DO_RESULTADO`, o cargo e o nome vazio que o `diretoria-cefor` do catálogo tinha. É o que
deixa as centenas de asserções sobre o signatário de pé, e concentra a troca nos dois helpers.

O início em 2000 é deliberado: há testes que publicam com o relógio atrasado (`--dias-atras` e o
`freezegun` dos prazos), e uma autoridade que só começasse hoje os recusaria por vigência.
"""

from datetime import UTC, date, datetime
from uuid import UUID

from processo_seletivo.publicacoes.infrastructure.pdf import UnidadeDoAto

CEFOR = {
    "codigo": "cefor",
    "sigla": "Cefor",
    "nome": "Centro de Referência em Formação e em Educação a Distância",
    "cabecalho": ["Centro de Referência em Formação", "e em Educação a Distância"],
    "local": "Vitória (ES)",
    "ativa": True,
}

# As colunas que a Publicação congela de uma Unidade, para os testes que gravam Publicação à mão.
COLUNAS_DO_CEFOR = {
    "unidade_codigo": CEFOR["codigo"],
    "unidade_sigla": CEFOR["sigla"],
    "unidade_nome": CEFOR["nome"],
    "unidade_cabecalho": list(CEFOR["cabecalho"]),
    "unidade_local": CEFOR["local"],
}

# A Unidade como o compositor a recebe — para os testes que chamam o renderizador direto.
UNIDADE_DA_SUITE = UnidadeDoAto(cabecalho=tuple(CEFOR["cabecalho"]), local=CEFOR["local"])

AUTORIDADE_DA_SUITE = UUID("00000000-0000-0000-0000-000000000601")
AUTORIDADE_DO_RESULTADO = UUID("00000000-0000-0000-0000-000000000602")

INICIO = date(2000, 1, 1)
_REGISTRO = datetime(2000, 1, 1, tzinfo=UTC)

_AUTORIDADES = {
    AUTORIDADE_DA_SUITE: {"nome": "Diretora", "cargo": "Diretora-Geral"},
    AUTORIDADE_DO_RESULTADO: {
        "nome": "",
        "cargo": "Diretora-Geral do Centro de Referência em Formação e em Educação a Distância",
    },
}


def registrar_unidade(codigo, **campos):
    """Uma Unidade a mais, para os testes que publicam ou criam em outro escopo."""
    from processo_seletivo.unidades.models import Unidade

    valores = {
        "sigla": codigo.capitalize(),
        "nome": f"Unidade {codigo}",
        "cabecalho": [f"Unidade {codigo}"],
        "local": "Vitória (ES)",
        "ativa": True,
        **campos,
    }
    unidade, _ = Unidade.objects.get_or_create(
        codigo=codigo, defaults={"registrada_em": _REGISTRO, **valores}
    )
    return unidade


def registrar_autoridade(unidade, *, identificador=None, inicio=INICIO, fim=None, **campos):
    """Uma autoridade habilitada, gravada direto: para testes que precisam do estado, e não do ato.

    Grava pelo ORM, e não pelo comando, porque há estados que o comando se recusa a produzir de
    propósito — o fim de ontem, por exemplo (FR-1120) — e o teste da recusa ao publicar precisa
    deles.
    """
    from processo_seletivo.unidades.models import AutoridadeHabilitada

    valores = {"cargo": "Diretor-Geral", "nome": "", "ato_de_nomeacao": "", **campos}
    extra = {"pk": identificador} if identificador else {}
    return AutoridadeHabilitada.objects.create(
        unidade=unidade,
        inicio_vigencia=inicio,
        fim_vigencia=fim,
        cadastrada_por="fixture",
        cadastrada_em=_REGISTRO,
        encerrada_por="fixture" if fim else "",
        encerrada_em=_REGISTRO if fim else None,
        **valores,
        **extra,
    )


def garantir_o_cefor():
    """A Unidade `cefor` e as duas autoridades de teste, idempotente."""
    from processo_seletivo.unidades.models import AutoridadeHabilitada, Unidade

    campos = {chave: valor for chave, valor in CEFOR.items() if chave != "codigo"}
    cefor, _ = Unidade.objects.get_or_create(
        codigo="cefor", defaults={"registrada_em": _REGISTRO, **campos}
    )
    for identificador, valores in _AUTORIDADES.items():
        AutoridadeHabilitada.objects.get_or_create(
            pk=identificador,
            defaults={
                "unidade": cefor,
                "inicio_vigencia": INICIO,
                "cadastrada_por": "fixture",
                "cadastrada_em": _REGISTRO,
                **valores,
            },
        )
    return cefor


def assinatura_do_resultado():
    """`signatario` e `unidade` como `conteudo_divulgado` os recebe, para quem o chama direto."""
    from processo_seletivo.unidades.models import AutoridadeHabilitada

    autoridade = AutoridadeHabilitada.objects.select_related("unidade").get(
        pk=AUTORIDADE_DO_RESULTADO
    )
    return {"signatario": autoridade, "unidade": autoridade.unidade}
