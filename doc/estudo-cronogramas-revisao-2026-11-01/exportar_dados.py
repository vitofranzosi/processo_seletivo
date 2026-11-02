"""Exporta a agenda do banco demonstrativo, mais casos sintéticos, para as POCs; não grava nada.

Executar de backend/, com as variáveis de conexão exportadas (o script não lê `.env`):

    DB_NAME=ps_demo_101 DB_USER="$USER" DB_RUNTIME_USER="$USER" DB_RUNTIME_PASSWORD='' \
      LC_ALL=en_US.UTF-8 .venv/bin/python \
      ../doc/estudo-cronogramas-revisao-2026-11-01/exportar_dados.py

Os sintéticos existem só em memória. Passam pelas mesmas funções da agenda — `marcos_do_conteudo`,
`periodos_do_conteudo` e o próprio `ler` — para que fase, espécie e período sejam os do produto, e
não uma reimplementação no navegador.
"""

# ruff: noqa: E402
# Os modelos só podem ser importados depois do registro dos aplicativos pelo django.setup().

import copy
import json
import os
import sys
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django

django.setup()

from django.contrib.staticfiles import finders
from django.db import connection, transaction
from django.template.loader import render_to_string

from processo_seletivo.interface import agenda
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import versoes_vigentes
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.estaticos import FOLHAS_DA_GESTAO
from processo_seletivo.shared.tempo import ZONA

PASTA = Path(__file__).resolve().parent
PROTOTIPO = PASTA / "prototipo"
REFERENCIAS = ("2026-11-01T12:00:00-03:00", "2026-11-05T12:00:00-03:00")

# Três formatos de cronograma tirados de editais públicos do Cefor de 2026 — só a forma: quais
# eventos, em que ordem, com que duração. As datas são deslocadas e os casos não são Editais.
# Os doze casos idênticos da primeira versão do estudo não testavam densidade: doze barras iguais
# empilhadas são triviais de ler, e a pergunta é como a tela se comporta com cronogramas diferentes.
# Cada evento: (nome, dias após o início, hora, duração em dias ou None se pontual, espécie).
FORMATOS = {
    "pessoal": (
        ("seleção de pessoal", "Edital 89/2026"),
        [
            ("Período de inscrições", 0, "08:00", 17, "inscricoes"),
            ("Análise de títulos", 19, "08:00", 6, "etapa"),
            ("Resultado preliminar da análise de títulos", 26, "18:00", None, None),
            ("Prazo para recurso", 27, "08:00", 2, None),
            ("Resultado dos recursos", 33, "18:00", None, None),
            ("Entrevistas de verificação da autodeclaração", 37, "08:00", 2, "etapa"),
            ("Resultado final", 41, "18:00", None, None),
        ],
    ),
    "sorteio": (
        ("chamada com sorteio", "Editais 69 e 78/2026"),
        [
            ("Período de inscrições", 0, "08:00", 17, "inscricoes"),
            ("Relação de inscritos", 18, "14:00", None, None),
            ("Sorteio", 19, "10:00", None, "etapa"),
            ("Resultado do sorteio", 19, "16:00", None, None),
            ("Entrega de documentos", 23, "08:00", 4, None),
            ("Resultado final", 30, "18:00", None, None),
        ],
    ),
    "curso": (
        ("curso, inscrição longa", "Edital 28/2026"),
        [
            ("Período de inscrições com envio de documentos", 0, "08:00", 29, "inscricoes"),
            ("Homologação das inscrições", 31, "18:00", None, None),
            ("Sorteio", 33, "10:00", None, "etapa"),
            ("Prazo para recurso", 34, "08:00", 1, None),
            ("Resultado final", 38, "18:00", None, None),
        ],
    ),
    # O Edital 72/2026 abriu inscrições às 07h20 e as fechou às 9h do dia seguinte: é o período
    # mais curto que um Edital real já publicou, e o que mais sofre numa régua diária.
    "relampago": (
        ("inscrição de um dia", "Edital 72/2026"),
        [
            ("Período de inscrições", 0, "07:20", 1, "inscricoes"),
            ("Sorteio", 2, "09:10", None, "etapa"),
            ("Entrega de documentos", 3, "08:00", 6, None),
        ],
    ),
}

# Início de cada caso e o formato: espalhados de setembro a dezembro, para que novembro tenha
# processos começando, no meio e terminando, e não um bloco sincronizado.
CASOS = [
    ("pessoal", "2026-09-21"),
    ("pessoal", "2026-10-05"),
    ("pessoal", "2026-10-19"),
    ("pessoal", "2026-10-26"),
    ("pessoal", "2026-11-09"),
    ("pessoal", "2026-11-23"),
    ("sorteio", "2026-10-13"),
    ("sorteio", "2026-10-27"),
    ("sorteio", "2026-11-03"),
    ("sorteio", "2026-11-16"),
    ("sorteio", "2026-11-24"),
    ("curso", "2026-10-01"),
    ("curso", "2026-11-02"),
    ("curso", "2026-11-17"),
    ("relampago", "2026-11-11"),
    # Dois clones do T08: três Editais com o mesmo cronograma, como 901, 902 e 903 nos prints.
    # É o caso que a faixa com nomes agrupa numa linha só.
    ("sorteio", "2026-10-27"),
    ("sorteio", "2026-10-27"),
    ("aberto", "2026-10-20"),
]

DESCRICAO_LONGA = (
    "Análise documental e conferência dos requisitos específicos para atuação em atividades de "
    "mediação pedagógica em ambientes virtuais de aprendizagem"
)


# O 72/2026 fechou às 9h do dia seguinte; os demais, ao fim do último dia.
FECHAMENTO = {"relampago": "09:00"}


def instante(dia, hora):
    return f"{dia.isoformat()}T{hora}:00-03:00"


def cronograma_sintetico(n, formato, inicio):
    dia0 = datetime.fromisoformat(inicio).date()
    if formato == "aberto":
        # Inscrição sem término: o produto não inventa fechamento, e a POC também não.
        return ("cadastro sem término", "nenhum Edital: caso-limite do FR-2633"), [
            {
                "id": f"teste-{n}-0",
                "description": "Período de inscrições para cadastro de reserva",
                "startAt": instante(dia0, "08:00"),
                "endAt": None,
                "isRegistrationPeriod": True,
                "order": 0,
            }
        ]
    descricao, eventos = FORMATOS[formato]
    schedule = []
    for ordem, (nome, desloc, hora, duracao, especie) in enumerate(eventos):
        dia = dia0 + timedelta(days=desloc)
        if n == 2 and nome == "Análise de títulos":
            nome = DESCRICAO_LONGA
        evento = {
            "id": f"teste-{n}-{ordem}",
            "description": nome,
            "startAt": instante(dia, hora),
            "endAt": (
                instante(dia + timedelta(days=duracao), FECHAMENTO.get(formato, "23:59"))
                if duracao
                else None
            ),
            "order": ordem,
        }
        if especie == "inscricoes":
            evento["isRegistrationPeriod"] = True
        schedule.append(evento)
    return descricao, schedule


def sinteticos(base):
    casos = []
    for n, (formato, inicio) in enumerate(CASOS, start=1):
        descricao, schedule = cronograma_sintetico(n, formato, inicio)
        conteudo = copy.deepcopy(base)
        conteudo["schedule"] = schedule
        etapas = FORMATOS.get(formato, ("", []))[1]
        conteudo["stages"] = [
            {"scheduleEventId": f"teste-{n}-{i}"}
            for i, evento in enumerate(etapas)
            if evento[4] == "etapa"
        ]
        edital = SimpleNamespace(
            pk=f"00000000-0000-4000-8000-{n:012d}",
            number=f"T{n:02d}",
            year=2026,
            processo=SimpleNamespace(title=f"Teste {n:02d} · {descricao[0]}"),
            status=Edital.Status.PUBLICADO,
        )
        edital.formato = descricao[1]
        casos.append((edital, SimpleNamespace(content=conteudo, valid_from=None)))
    return casos


def projetar(edital, conteudo, agora, origem, aviso="", versao=""):
    """Um Edital no formato da POC, com fase e espécie calculadas pelo produto."""
    eventos = {str(e["id"]): e for e in conteudo["schedule"]}
    itens = []
    for periodo in agenda.periodos_do_conteudo(edital, conteudo, agora):
        evento = eventos[periodo.evento_id]
        itens.append(
            dict(
                id=periodo.evento_id,
                nome=periodo.nome,
                inicio=evento["startAt"],
                fim=evento.get("endAt"),
                tipo="periodo",
                especie=periodo.especie,
                fase=periodo.fase,
                faseRotulo=periodo.rotulo_da_fase,
                cancelado=False,
                local=evento.get("location", ""),
            )
        )
    for marco in agenda.marcos_do_conteudo(edital, conteudo, agora):
        if marco.tipo != agenda.PONTUAL:
            continue
        evento = eventos[marco.evento_id]
        itens.append(
            dict(
                id=marco.evento_id,
                nome=marco.nome,
                inicio=evento["startAt"],
                fim=None,
                tipo="pontual",
                especie=marco.especie,
                fase=marco.fase,
                faseRotulo=marco.rotulo_da_fase or "ainda não começou",
                cancelado=marco.cancelado,
                local=marco.local,
            )
        )
    return dict(
        **asdict(edital),
        origem=origem,
        aviso=aviso,
        versao=versao,
        itens=sorted(itens, key=lambda item: (item["inicio"], item["nome"])),
    )


def agenda_atual(reais, extras, agora, parametros):
    """O fragmento que a gestão renderiza hoje, com os sintéticos somados aos reais.

    Os sintéticos não estão no banco; por isso a leitura de Editais e de versões é estendida só
    durante esta chamada. Todo o resto — janela, ordenação, síntese, template — é o do produto.
    """

    def editais_da_agenda(_ator):
        return [*reais, *(edital for edital, _ in extras)]

    def versoes(edital_ids, at):
        resultado = versoes_vigentes(edital_ids=[e.pk for e in reais], at=at)
        resultado.update({edital.pk: versao for edital, versao in extras})
        return resultado

    original = agenda.retificacoes_a_vigorar

    def a_vigorar(ids, agora_):
        return original([e.pk for e in reais], agora_)

    with (
        mock.patch.object(agenda, "editais_da_agenda", editais_da_agenda),
        mock.patch.object(agenda, "versoes_vigentes", versoes),
        mock.patch.object(agenda, "retificacoes_a_vigorar", a_vigorar),
    ):
        leitura = agenda.ler(SimpleNamespace(institution_scope="cefor"), parametros, agora=agora)
    modelo = "_agenda_proximos.html" if parametros.get("visao") else "_agenda_mes.html"
    return render_to_string(f"interface/{modelo}", {"leitura": leitura})


def pagina_atual(titulo, nota, trecho):
    return (
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{titulo}</title>"
        '<link rel="stylesheet" href="tokens.css">'
        '<link rel="stylesheet" href="base-atual.css">'
        '<link rel="stylesheet" href="agenda-atual.css">'
        f'</head><body><main><h1>{titulo}</h1><p class="sub">{nota}</p>'
        + trecho
        + "</main></body></html>"
    )


# Os seis Editais que aparecem nos prints da agenda (01, 91, 901, 902, 903 e 92), lidos de um
# banco local de demonstração que os tem publicados. São os mesmos Editais e os mesmos nomes de
# evento, mas **não** as mesmas datas: a semente as gera a partir do dia em que roda, e nenhum
# banco local reproduz as do print. Servem pelo formato — o 92 tem dezessete eventos com nomes
# longos, e 901 a 903 têm cronogramas idênticos — e trazem os horários que a transcrição não tem.
# 22/11 é a referência do estudo D–G; 01/11, a dos prints.
PRINTS = ("01", "91", "901", "902", "903", "92")
REFERENCIAS_DOS_PRINTS = ("2026-11-01T12:00:00-03:00", "2026-11-22T12:00:00-03:00")


def exportar_prints():
    saida = {"referencias": {}, "zona": str(ZONA)}
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("SET TRANSACTION READ ONLY")
        editais = list(
            Edital.objects.filter(
                institution_scope="cefor", year=2026, number__in=PRINTS
            ).select_related("processo")
        )
        if len(editais) != len(PRINTS):
            raise SystemExit("O banco não tem os seis Editais publicados.")
        for referencia in REFERENCIAS_DOS_PRINTS:
            agora = datetime.fromisoformat(referencia)
            versoes = versoes_vigentes(edital_ids=[e.pk for e in editais], at=agora)
            saida["referencias"][referencia[:10]] = dict(
                instante=referencia,
                demonstrativos=[
                    projetar(
                        agenda.EditalDaAgenda.de(edital),
                        versoes[edital.pk].content,
                        agora,
                        "Banco de demonstração ps_074_local: Editais e nomes dos prints, "
                        "com outras datas",
                        "",
                        versoes[edital.pk].valid_from.isoformat(),
                    )
                    for edital in sorted(editais, key=lambda e: int(e.number))
                ],
                sinteticos=[],
                historico106=[],
            )
    (PROTOTIPO / "dados-prints.js").write_text(
        "window.DADOS_PRINTS = " + json.dumps(saida, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    print(f"Exportados os {len(PRINTS)} Editais do ps_074_local, em duas referências.")


def exportar():
    if connection.settings_dict["NAME"] != "ps_demo_101":
        raise SystemExit("Use exclusivamente DB_NAME=ps_demo_101, banco fictício da agenda.")
    saida = {"referencias": {}, "zona": str(ZONA)}
    with transaction.atomic(), connection.cursor() as cursor:
        # Até a conexão de desenvolvimento fica impedida de escrever durante a exportação.
        cursor.execute("SET TRANSACTION READ ONLY")
        reais = list(
            Edital.objects.filter(
                institution_scope="cefor", number__in=[str(n) for n in range(101, 108)]
            ).select_related("processo")
        )
        if len(reais) != 7:
            raise SystemExit("A demonstração 101 deve conter exatamente os sete Editais esperados.")
        for referencia in REFERENCIAS:
            agora = datetime.fromisoformat(referencia)
            versoes = versoes_vigentes(edital_ids=[e.pk for e in reais], at=agora)
            futuros = agenda.retificacoes_a_vigorar([e.pk for e in reais], agora)
            demonstrativos = []
            for edital in sorted(reais, key=lambda e: int(e.number)):
                aviso = (
                    "Retificação publicada: vigora em "
                    + futuros[edital.pk].astimezone(ZONA).strftime("%d/%m/%Y às %H:%M")
                    if edital.pk in futuros
                    else ""
                )
                demonstrativos.append(
                    projetar(
                        agenda.EditalDaAgenda.de(edital),
                        versoes[edital.pk].content,
                        agora,
                        "Demonstração existente da agenda (banco ps_demo_101)",
                        aviso,
                        versoes[edital.pk].valid_from.isoformat(),
                    )
                )
            extras = sinteticos(versoes[reais[0].pk].content)
            casos = [
                projetar(
                    agenda.EditalDaAgenda.de(edital),
                    versao.content,
                    agora,
                    "Caso sintético de teste, só em memória; formato tirado de " + edital.formato,
                )
                for edital, versao in extras
            ]
            prova = next(e for e in reais if e.number == "106")
            historico = [
                {
                    "vigoraEm": v.valid_from.isoformat(),
                    "prova": next(
                        e["startAt"]
                        for e in v.content["schedule"]
                        if e["description"] == "Prova objetiva"
                    ),
                }
                for v in VersaoConsolidada.objects.filter(edital=prova).order_by("valid_from")
            ]
            saida["referencias"][referencia[:10]] = dict(
                instante=referencia,
                demonstrativos=demonstrativos,
                sinteticos=casos,
                historico106=historico,
            )

        # A interface de hoje, para comparar no mesmo recorte: a lista do mês e os Próximos
        # marcos, com 7 Editais e com 23. A grade não entra — o estudo não a altera.
        grades = {}
        agora = datetime.fromisoformat(REFERENCIAS[0])
        base = versoes_vigentes(edital_ids=[reais[0].pk], at=agora)[reais[0].pk].content
        extras = sinteticos(base)
        for nome, lista, parametros, titulo in (
            ("atual-mes.html", [], {"mes": "2026-11"}, "Agenda atual · Mês (7 Editais)"),
            ("atual-mes-denso.html", extras, {"mes": "2026-11"}, "Agenda atual · Mês (23 Editais)"),
            (
                "atual-proximos.html",
                [],
                {"visao": "proximos"},
                "Agenda atual · Próximos 7 dias (7 Editais)",
            ),
            (
                "atual-proximos-denso.html",
                extras,
                {"visao": "proximos"},
                "Agenda atual · Próximos 7 dias (23 Editais)",
            ),
        ):
            trecho = agenda_atual(reais, lista, agora, parametros)
            if "mes" in parametros:
                # A grade sem a lista de períodos: é o que a página completa com C mostra acima.
                grades["23" if lista else "7"] = trecho.split('<section class="periodos-do-mes"')[0]
            (PROTOTIPO / nome).write_text(
                pagina_atual(
                    titulo,
                    "Fragmento renderizado pelo template de produção, referência "
                    "01/11/2026 às 12h. Os links apontam para a gestão e não funcionam aqui.",
                    trecho,
                ),
                encoding="utf-8",
            )

    (PROTOTIPO / "grade.js").write_text(
        "window.GRADE = " + json.dumps(grades, ensure_ascii=False) + ";\n", encoding="utf-8"
    )
    # dados.js, e não JSON: a POC abre com dois cliques, sem servidor, porque não há fetch.
    (PROTOTIPO / "dados.js").write_text(
        "window.DADOS = " + json.dumps(saida, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    for destino, fontes in (
        ("base-atual.css", FOLHAS_DA_GESTAO),
        ("agenda-atual.css", ("interface/telas/agenda.css",)),
        ("tokens.css", ("shared/tokens.css",)),
    ):
        (PROTOTIPO / destino).write_text(
            "\n".join(Path(finders.find(fonte)).read_text(encoding="utf-8") for fonte in fontes),
            encoding="utf-8",
        )
    print(f"Exportados 7 Editais demonstrativos e {len(CASOS)} casos sintéticos.")


if __name__ == "__main__":
    exportar_prints() if connection.settings_dict["NAME"] == "ps_074_local" else exportar()
