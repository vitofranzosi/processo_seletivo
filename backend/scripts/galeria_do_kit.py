"""A galeria do kit de divulgação: as peças dos cenários de referência lado a lado (111, T030).

É o que vai para a comunicação aprovar o template (SC-1054, D-016), e o que vai servir para aprovar
cada família de template que vier depois. Rode de `backend/`, com o PostgreSQL da suíte:

    TEST_DB_ENGINE=postgresql DB_USER=$USER DB_RUNTIME_USER=$USER DB_NAME=ps_galeria LC_ALL=C \\
        uv run python scripts/galeria_do_kit.py --saida /tmp/galeria-kit

**Por família e formato** (119, FR-3831, FR-3834): `--familia pos-lato-sensu` mostra cada template
da família — `--formato post` restringe a um — em todo cenário, com a recusa e o motivo onde não
couber, e o identificador, a versão e o resumo curto de cada template em cada peça. É sobre essa
página que a aprovação de um template se registra, nomeando exatamente essa versão e esse resumo.

Grava em `--saida`, que precisa estar vazia, um `index.html` com um cartão por cenário — a peça, o
texto alternativo, a recusa quando há — e, por cenário, o PNG, o SVG e o ZIP que a exportação
entregaria. A página abre direto do disco, sem servidor.

**Num banco descartável, criado e destruído aqui.** O banco é o de teste do `DB_NAME` (prefixo
`test_`), como o da suíte: os cenários publicam o 91/2026 várias vezes, e a unicidade de número não
deixa duas cópias no mesmo banco; cada cenário roda numa transação desfeita no fim. Nada vai para o
banco da equipe, e uma suíte rodando com o mesmo `DB_NAME` o derrubaria — use um nome próprio.

**Por que em `scripts/`, e não um comando de gestão**: a razão de `publicar_corpus_do_piloto.py`.
Os cenários publicam pelos ajudantes da suíte (`tests/fixtures/kit.py`), pelo fluxo real, e um
comando no pacote levaria a produção a importar a suíte.

**As datas são as de hoje.** O corpus é publicado deslocado até a data em que a galeria roda, como
na suíte; a geometria não muda com isso, e os SVG de referência, que fixam as datas, são o que a
revisão de código compara (`tests/integration/kit/test_referencias.py`).

**O que a galeria não mostra**, de dois cenários da lista da spec: o Perfil substituído inteiro por
Retificação muda a proveniência na tela de conferência, e não a peça; e o mesmo número em duas
unidades muda a busca da legenda, e não a composição. Os dois têm teste próprio.
"""

import argparse
import dataclasses
import hashlib
import html
import io
import os
import subprocess
import sys
import zipfile
from datetime import timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.db import connection, transaction  # noqa: E402
from django.test.utils import setup_test_environment  # noqa: E402
from django.utils import timezone  # noqa: E402
from django.utils.dateparse import parse_datetime  # noqa: E402
from rest_framework.test import APIClient  # noqa: E402

from processo_seletivo.interface import (  # noqa: E402
    kit_de_divulgacao,
    kit_familias,
    kit_pacote,
    kit_peca,
)
from processo_seletivo.portal import ficha as fichas  # noqa: E402
from processo_seletivo.processos.application.finalizacao import cancel_edital  # noqa: E402
from tests.fixtures import editais_do_piloto, kit  # noqa: E402
from tests.fixtures.autoridades import garantir_o_cefor  # noqa: E402


@dataclasses.dataclass
class Leitura:
    chave: str
    titulo: str
    ficha: fichas.Ficha
    nota: str = ""


def _ler(edital, agora=None, **trocas):
    ficha = fichas.ler(edital, agora=agora or timezone.now(), base_url=kit.BASE)
    return dataclasses.replace(ficha, **trocas) if trocas else ficha


# ---- os cenários (spec, "Cenários de referência") ------------------------------------------
# Cada um publica pelo fluxo real e devolve as leituras que mostra. O número é o da lista da spec.


def c91(cliente):
    edital = kit.publicar(cliente, ate=1, chave="galeria-91")
    andamento = kit.inicio(edital) + timedelta(days=1)
    fim = parse_datetime(kit.evento_das_inscricoes(edital)["endAt"])
    return [
        Leitura("01-91-futuro", "1. 91/2026 com inscrições futuras", _ler(edital)),
        Leitura("02-91-em-andamento", "2. 91/2026 em andamento", _ler(edital, andamento)),
        Leitura(
            "12-91-encerrado",
            "12. 91/2026 com o período encerrado",
            _ler(edital, fim + timedelta(days=1)),
        ),
        Leitura(
            "13-91-sem-grafia",
            "13. Caractere sem grafia no título",
            _ler(edital, titulo_sem_numero="Curso para idade ≥ 18 anos"),
            nota="Título trocado na ficha lida: a publicação já recusa o caractere.",
        ),
    ]


def c91_prorrogado(cliente):
    edital = kit.publicar(cliente, ate=2, chave="galeria-91-prorrogado")
    return [Leitura("03-91-prorrogado", "3. 91/2026 prorrogado por Retificação", _ler(edital))]


def c01(cliente):
    edital = kit.publicar(cliente, "01", chave="galeria-01")
    antes = _ler(edital)
    leituras = [Leitura("04-01-a-vigorar", "4. 01/2026 com Retificação a vigorar", antes)]
    if antes.retificacao_a_vigorar:
        depois = parse_datetime(antes.retificacao_a_vigorar) + timedelta(minutes=1)
        leituras.append(
            Leitura("05-01-vigente", "5. 01/2026 depois da vigência", _ler(edital, depois))
        )
    return leituras


def c92(cliente):
    edital = kit.publicar(cliente, "92", ate=1, chave="galeria-92")
    primeira = _ler(edital)
    kit.retificar_secao(cliente, edital, suffix="galeria-92-secao")
    return [
        Leitura("06-92-muitos-perfis", "6. 92/2026 com muitos Perfis", primeira),
        Leitura(
            "07-92-retificacao-sem-material",
            "7. 92/2026 com Retificação que não muda o material",
            _ler(edital),
            nota="A peça é a mesma do cenário 6.",
        ),
    ]


def c_variacoes(cliente):
    um = kit.publicar(cliente, chave="galeria-um", mudar=kit.so_um_perfil)
    return [Leitura("08-91-um-perfil", "8. Um Perfil", _ler(um))]


def c_sem_localidade(cliente):
    edital = kit.publicar(cliente, chave="galeria-sem-local", mudar=kit.sem_localidade)
    return [Leitura("09-91-sem-localidade", "9. Localidade ausente", _ler(edital))]


def c_neutro(cliente):
    edital = kit.publicar(cliente, chave="galeria-neutro", mudar=kit.sem_periodo)
    return [Leitura("10-91-neutro", "10. Sem período designado", _ler(edital))]


def c_cancelado(cliente):
    edital = kit.publicar(cliente, ate=1, chave="galeria-cancelado")
    edital.refresh_from_db()
    cancel_edital(
        actor=editais_do_piloto.GESTORA,
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason="Cancelamento para a galeria do kit.",
        idempotency_key=f"cancelar-galeria-{edital.id}",
        correlation_id="111-galeria",
    )
    edital.refresh_from_db()
    return [Leitura("11-91-cancelado", "11. Cancelado depois de exportado", _ler(edital))]


def c_so_hora(cliente):
    edital = kit.publicar(cliente, "01", ate=1, chave="galeria-hora")
    fim = parse_datetime(kit.evento_das_inscricoes(edital)["endAt"]).astimezone(fichas.ZONA)
    kit.retificar_termino(cliente, edital, fim.replace(hour=18, minute=0), suffix="galeria-hora")
    return [Leitura("14-01-so-hora", "14. Prorrogação que só muda a hora", _ler(edital))]


def c_termo(cliente):
    edital = kit.publicar(cliente, chave="galeria-termo", mudar=kit.termo_no_titulo)
    return [Leitura("17-91-termo", "Valor oficial com termo da lista (EC-26)", _ler(edital))]


def c_lato(cliente):
    edital = kit.publicar(cliente, chave="galeria-lato", mudar=kit.lato_uma_oferta)
    titulo = "17. Pós lato sensu de uma oferta, título de 120 caracteres (119)"
    return [Leitura("18-91-lato-uma-oferta", titulo, _ler(edital))]


def c_carga(cliente):
    edital = kit.publicar(cliente, chave="galeria-carga", mudar=kit.carga_vazia_e_longa)
    titulo = "19. Carga horária vazia num Perfil e longa noutro (119, EC-2, EC-3)"
    return [Leitura("19-91-carga-vazia-e-longa", titulo, _ler(edital))]


CENARIOS = (
    c91,
    c91_prorrogado,
    c01,
    c92,
    c_variacoes,
    c_sem_localidade,
    c_neutro,
    c_cancelado,
    c_so_hora,
    c_termo,
    c_lato,
    c_carga,
)


# ---- a gravação ----------------------------------------------------------------------------


@dataclasses.dataclass
class Resultado:
    leitura: Leitura
    png: str = ""
    svg: str = ""
    zip: str = ""
    alternativo: str = ""
    motivo: str = ""
    omissao: str = ""
    zip_identico: bool | None = None
    resumo_png: str = ""
    largura: int = 1080
    altura: int = 1350


def gravar(leitura, saida):
    ficha = leitura.ficha
    resultado = Resultado(leitura)
    if not ficha.tem_material:
        resultado.motivo = f"Sem material: {ficha.motivo}"
        return resultado
    dados, peca, motivo = kit_de_divulgacao.pacote(ficha, manchete=None, motivo_sem_peca="")
    # O mesmo pacote no mesmo instante de referência (FR-3438): a galeria confere de novo.
    resultado.zip_identico = (
        dados == kit_de_divulgacao.pacote(ficha, manchete=None, motivo_sem_peca="")[0]
    )
    resultado.zip = f"{leitura.chave}.zip"
    (saida / resultado.zip).write_bytes(dados)
    resultado.motivo = motivo
    if peca is None:
        return resultado
    resultado.alternativo = peca.alternativo
    resultado.omissao = peca.omissao
    with zipfile.ZipFile(io.BytesIO(dados)) as pacote:
        nomes = set(pacote.namelist())
        if kit_pacote.PNG in nomes:
            png = pacote.read(kit_pacote.PNG)
            resultado.png = f"{leitura.chave}.png"
            resultado.resumo_png = hashlib.sha256(png).hexdigest()
            (saida / resultado.png).write_bytes(png)
        resultado.svg = f"{leitura.chave}.svg"
        (saida / resultado.svg).write_bytes(pacote.read(kit_pacote.SVG))
    return resultado


def gravar_template(leitura, template, imagem, saida, variante=None):
    """A peça de um template de família no cenário, ou a recusa com o motivo (FR-3831)."""
    ficha = leitura.ficha
    chave = f"{leitura.chave}-{template.formato.chave}"
    resumo = kit_familias.resumo(template)[: kit_familias.RESUMO_CURTO]
    titulo = f"{leitura.titulo} — {template.identificador} #{resumo}"
    resultado = Resultado(dataclasses.replace(leitura, chave=chave, titulo=titulo))
    if not ficha.tem_material:
        resultado.motivo = f"Sem material: {ficha.motivo}"
        return resultado
    try:
        peca = kit_peca.compor_template(
            ficha, template, kit_peca.Escolha(imagem=imagem, variante=variante)
        )
    except kit_peca.PecaRecusada as recusa:
        resultado.motivo = recusa.motivo
        return resultado
    resultado.alternativo = peca.alternativo
    resultado.omissao = " ".join(peca.avisos)
    svg = kit_peca.svg(peca, ficha)
    resultado.svg = f"{chave}.svg"
    (saida / resultado.svg).write_text(kit_peca.svg(peca, ficha, fonte_embutida=True))
    if kit_pacote.disponivel():
        png = kit_pacote.rasterizar(svg, kit_peca.fontes_da_peca(peca))
        resultado.png = f"{chave}.png"
        resultado.resumo_png = hashlib.sha256(png).hexdigest()
        (saida / resultado.png).write_bytes(png)
    resultado.largura, resultado.altura = template.formato.largura, template.formato.altura
    return resultado


def _commit():
    try:
        return subprocess.run(
            ["git", "-C", str(RAIZ), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "desconhecido"


ESTILO = """
:root { color-scheme: light; font-family: system-ui, sans-serif; color: #1c1c1c; }
body { margin: 0 auto; padding: 24px 16px 64px; max-width: 1400px; background: #f6f6f4; }
h1 { font-size: 1.6rem; margin: 0 0 4px; }
.cabecalho p { margin: 2px 0; color: #444; }
.grade { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px;
  margin-top: 24px; }
.cenario { background: #fff; border: 1px solid #d4d4d4; border-radius: 8px; padding: 16px;
  display: flex; flex-direction: column; gap: 10px; }
.cenario h2 { font-size: 1.05rem; margin: 0; }
.cenario img { width: 100%; height: auto; border: 1px solid #d4d4d4; background: #fff; }
.sem-peca { aspect-ratio: 1080 / 1350; display: flex; align-items: center;
  justify-content: center; padding: 24px; text-align: center; background: #fdf5e5;
  color: #8a5300; border: 1px dashed #8a5300; }
.aviso { background: #fdf5e5; color: #6b4100; padding: 8px 10px; border-radius: 4px; margin: 0; }
.nota { color: #555; font-size: .9rem; margin: 0; }
details pre { white-space: pre-wrap; font-size: .85rem; background: #f3f3f3; padding: 8px; }
.arquivos a { margin-right: 12px; }
code { font-size: .8rem; word-break: break-all; }
"""


def pagina(resultados, *, gerada_em, templates=None):
    esc = html.escape
    cartoes = []
    for r in resultados:
        partes = [f"<h2>{esc(r.leitura.titulo)}</h2>"]
        if r.png:
            partes.append(
                f'<img src="{esc(r.png)}" width="{r.largura}" height="{r.altura}" '
                f'alt="{esc(r.alternativo)}">'
            )
        else:
            partes.append(f'<div class="sem-peca">{esc(r.motivo or "Sem peça.")}</div>')
        if r.omissao:
            partes.append(f'<p class="aviso">{esc(r.omissao)}</p>')
        if r.motivo and r.png:
            partes.append(f'<p class="aviso">{esc(r.motivo)}</p>')
        if r.leitura.nota:
            partes.append(f'<p class="nota">{esc(r.leitura.nota)}</p>')
        if r.alternativo:
            partes.append(
                "<details><summary>Texto alternativo</summary>"
                f"<pre>{esc(r.alternativo)}</pre></details>"
            )
        links = [
            f'<a href="{esc(nome)}">{rotulo}</a>'
            for nome, rotulo in ((r.png, "PNG"), (r.svg, "SVG"), (r.zip, "ZIP"))
            if nome
        ]
        if links:
            partes.append(f'<p class="arquivos">{"".join(links)}</p>')
        if r.zip_identico is not None:
            igual = "sim" if r.zip_identico else "NÃO"
            partes.append(f'<p class="nota">ZIP idêntico em duas montagens: {igual}.</p>')
        if r.resumo_png:
            partes.append(f'<p class="nota">PNG <code>{r.resumo_png[:16]}</code></p>')
        cartoes.append(f'<article class="cenario">{"".join(partes)}</article>')
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Galeria do kit de divulgação</title>
<style>{ESTILO}</style>
</head>
<body>
<header class="cabecalho">
<h1>Galeria do kit de divulgação</h1>
<p>Template <strong>{esc(templates or kit_peca.TEMPLATE)}</strong> · rasterizador
{esc(kit_pacote.versao_do_rasterizador() or "ausente")} · commit {esc(_commit())}</p>
<p>Gerada em {esc(gerada_em)}, sobre os cenários de referência da spec 111, publicados pelo fluxo
real num banco descartável. As datas são as do dia da geração.</p>
<p>Para aprovar o template (SC-1054): confira cada peça contra o manual da marca, e registre a
versão do template e o commit acima junto da aprovação.</p>
</header>
<main class="grade">
{"".join(cartoes)}
</main>
</body>
</html>
"""


def principal():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--saida", required=True, type=Path, help="pasta da galeria")
    parser.add_argument("--familia", default="institucional", help="a família (119)")
    parser.add_argument("--formato", help="um formato só: post, story ou banner")
    parser.add_argument("--imagem", help="a imagem do banco; a primeira, se não dita")
    parser.add_argument("--variante", help="a variante da família; a primeira, se não dita")
    argumentos = parser.parse_args()
    familia = kit_familias.familia(argumentos.familia)
    templates = [
        t for formato, t in familia.templates.items() if argumentos.formato in (None, formato)
    ]
    if not templates:
        raise SystemExit(f"A família {familia.chave} não tem o formato {argumentos.formato}.")
    imagem = argumentos.imagem or (familia.imagens[0].chave if familia.imagens else None)
    variante = argumentos.variante or (familia.variantes[0].chave if familia.variantes else None)
    da_111 = familia.chave == "institucional"
    saida = argumentos.saida.resolve()
    # Pasta vazia, e não limpa aqui: um arquivo de cenário que deixou de existir ficaria na galeria
    # como se fosse desta geração, e apagar o que está numa pasta alheia não é papel da galeria.
    if saida.exists() and any(saida.iterdir()):
        raise SystemExit(f"A pasta {saida} não está vazia: use uma pasta nova para a galeria.")
    saida.mkdir(parents=True, exist_ok=True)

    if da_111 and not settings.KIT_DE_DIVULGACAO_PECA:
        raise SystemExit("A peça está desligada nestas settings (KIT_DE_DIVULGACAO_PECA).")
    if connection.vendor != "postgresql":
        raise SystemExit("A galeria publica pelo fluxo real: rode com TEST_DB_ENGINE=postgresql.")
    setup_test_environment()
    nome_original = connection.settings_dict["NAME"]
    connection.creation.create_test_db(verbosity=0, autoclobber=True, serialize=False)
    resultados = []
    try:
        for cenario in CENARIOS:
            with transaction.atomic():
                garantir_o_cefor()
                for leitura in cenario(APIClient()):
                    if da_111:
                        resultados.append(gravar(leitura, saida))
                    else:
                        resultados.extend(
                            gravar_template(leitura, t, imagem, saida, variante) for t in templates
                        )
                    print(f"{leitura.chave}: {resultados[-1].motivo or 'peça gerada'}")
                transaction.set_rollback(True)
    finally:
        connection.creation.destroy_test_db(nome_original, verbosity=0)
    resultados.sort(key=lambda r: r.leitura.chave)
    gerada_em = fichas.instante_por_extenso(timezone.now())
    rotulo = None
    if not da_111:
        rotulo = " · ".join(
            f"{t.identificador} #{kit_familias.resumo(t)[: kit_familias.RESUMO_CURTO]}"
            for t in templates
        )
    (saida / "index.html").write_text(
        pagina(resultados, gerada_em=gerada_em, templates=rotulo), encoding="utf-8"
    )
    print(f"Galeria: {saida / 'index.html'} ({len(resultados)} cenários)")
    if any(r.zip_identico is False for r in resultados):
        raise SystemExit("Algum ZIP saiu diferente em duas montagens: o pacote não é determinista.")


if __name__ == "__main__":
    principal()
