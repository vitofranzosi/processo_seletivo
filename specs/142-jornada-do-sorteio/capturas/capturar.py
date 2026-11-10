# ruff: noqa: E501
"""As capturas de antes e depois da tela do sorteio (142), praticando os atos de verdade.

    cd backend && uv run python ../specs/142-jornada-do-sorteio/capturas/capturar.py antes|depois

Roda contra o banco descartável `ps142_dev` (entrada `jornada-do-sorteio-142` do launch.json,
porta 8142), **recém-restaurado** da cópia `ps142_base` (C06 e C07 da 134, rodada 1): os atos são
irreversíveis, e o roteiro só faz sentido uma vez por restauração.

O mesmo roteiro serve aos dois lados, e por isso não clica por texto de botão — o texto é o que muda.
Clica pelo destino do formulário, dentro do recorte.
"""

import os
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("BASE", "http://localhost:8142")
BANCO = os.environ.get("BANCO", "ps142_dev")
LADO = sys.argv[1] if len(sys.argv) > 1 else "antes"
SAIDA = Path(os.environ.get("SAIDA", Path(__file__).resolve().parent))

C06 = ("523754df-43fa-4b2b-81ad-04fc4de051c3", "ca484c38-087c-5c1f-9b9e-666c589a86aa")
C07 = ("66830efd-bd93-4d12-9cd5-9ee110e720ff", "746b5035-38b8-5421-b018-79bf3f0d842f")
PRESIDENCIA, PUBLICACAO = "treino.presidencia", "treino.publicacao"


def tela(cenario):
    edital, marco = cenario
    return f"{BASE}/gestao/editais/{edital}/marcos/{marco}/sorteio"


def entrar(navegador, identidade, largura=1440, altura=900, papeis=()):
    contexto = navegador.new_context(viewport={"width": largura, "height": altura})
    pagina = contexto.new_page()
    pagina.set_default_timeout(15_000)
    pagina.goto(f"{BASE}/gestao/identificar/demonstracao?proximo=/gestao/")
    token = pagina.locator("input[name=csrfmiddlewaretoken]").first.get_attribute("value")
    pagina.request.post(
        f"{BASE}/gestao/identificar",
        data=f"csrfmiddlewaretoken={token}&proximo=/gestao/&subject={identidade}"
        + "".join(f"&papeis={p}" for p in papeis),
        headers={"Content-Type": "application/x-www-form-urlencoded", "Referer": pagina.url},
    )
    return pagina


def medir(pagina):
    """O que a captura sozinha não diz: rolagem horizontal e onde estão os controles."""
    return pagina.evaluate(
        """() => {
          const y = sel => { const e = document.querySelector(sel); return e ? Math.round(e.getBoundingClientRect().top + scrollY) : null };
          return {
            rolagem_horizontal: document.documentElement.scrollWidth > innerWidth,
            altura: document.documentElement.scrollHeight,
            fixar: y("form[action$='/sorteio/relacao'] button"),
            observar: y("form[action$='/sorteio/ocorrencia'] button"),
            sortear: y("form[action$='/sorteio/realizar'] button"),
            formularios: [...document.querySelectorAll("form[method=post]")].map(f => {
              const v = n => (f.querySelector("input[name=" + n + "]") || {}).value || "";
              return f.getAttribute("action").split("/sorteio")[1] + "|" + v("lista_id") + v("relacao_id") + v("sorteio_anterior_id");
            }).filter(t => !t.startsWith("undefined")).sort(),
          }
        }"""
    )


MEDIDAS = {}


def capturar(pagina, nome, *, dobra=True):
    base = SAIDA / f"{LADO}-{nome}"
    pagina.screenshot(path=f"{base}.png", full_page=True)
    if dobra:
        pagina.screenshot(path=f"{base}-dobra.png")
    medida = medir(pagina)
    MEDIDAS[nome] = medida
    print(nome, {k: v for k, v in medida.items() if k != "formularios"})


def enviar(pagina, recorte, destino):
    """Envia o formulário de `destino` do recorte (`ampla` ou o id da lista), ou do marco."""
    escopo = f"#recorte-{recorte} " if recorte else ""
    botao = pagina.locator(f"{escopo}form[action$='/sorteio/{destino}'] button[type=submit]")
    if not botao.count() and recorte:
        # Depois da 142, sortear mora no passo da execução, com a âncora própria.
        botao = pagina.locator(f"#sorteio-{recorte} form[action$='/sorteio/{destino}'] button[type=submit]")
    with pagina.expect_navigation():
        botao.first.click()


def ppp(pagina):
    ids = pagina.eval_on_selector_all("article.recorte", "els => els.map(e => e.id)")
    return next(i for i in ids if i != "recorte-ampla").removeprefix("recorte-")


def rodada_seguinte_do_c06():
    """Restaura o C06 (rodada 2), pelo comando da 134, e devolve `(edital, marco)` da rodada nova."""
    import subprocess

    ambiente = {
        **os.environ,
        "DJANGO_SETTINGS_MODULE": "config.settings.development",
        "DB_NAME": BANCO,
        "DB_USER": os.environ["USER"],
        "DB_RUNTIME_USER": os.environ["USER"],
        "CENARIOS_DE_TREINAMENTO": "true",
        "SORTEIO_FONTE_DE_DEMONSTRACAO": "true",
        "ARQUIVOS_CANDIDATOS_RAIZ": "/tmp/ps142-arquivos",
    }
    subprocess.run(
        ["uv", "run", "python", "manage.py", "restaurar_cenario_de_treinamento", "--cenario", "C06",
         "--confirmar", "C06", "--banco", BANCO, "--autoridade", "00000000-0000-0000-0000-000000000601"],
        env=ambiente, check=True, capture_output=True,
    )
    saida = subprocess.run(
        ["uv", "run", "python", "manage.py", "shell", "-c",
         "from processo_seletivo.treinamento.models import CenarioDeTreinamento as C\n"
         "from processo_seletivo.publicacoes.application.selectors import effective_version\n"
         "c = C.objects.filter(codigo='C06').order_by('-rodada').first()\n"
         "e = c.processo.editais.first()\n"
         "m = effective_version(edital_id=e.id).content['profiles'][0]['classificationMilestones'][0]['id']\n"
         "print(f'ids={e.id},{m}')"],
        env=ambiente, check=True, capture_output=True, text=True,
    ).stdout
    return tuple(re.search(r"ids=(\S+)", saida).group(1).split(","))


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        violacoes = []

        # C07: as duas relações congeladas, a semente por obter.
        pagina = entrar(navegador, PRESIDENCIA)
        pagina.on("console", lambda m: violacoes.append(m.text) if "Content Security Policy" in m.text else None)
        pagina.goto(tela(C07))
        capturar(pagina, "04-c07-todas-congeladas-sem-semente")

        # C06: o caminho inteiro, na ordem das regras.
        pagina.goto(tela(C06))
        capturar(pagina, "01-c06-nada-preparado")
        lista_ppp = ppp(pagina)
        enviar(pagina, "ampla", "relacao")
        capturar(pagina, "02-c06-ampla-fixada-ppp-pendente")
        pagina.goto(tela(C06) + f"?lista={lista_ppp}#recorte-{lista_ppp}")
        enviar(pagina, lista_ppp, "relacao")
        capturar(pagina, "03-c06-todas-fixadas")
        enviar(pagina, None, "ocorrencia")
        capturar(pagina, "05-c06-semente-observada")
        pagina.goto(tela(C06))
        enviar(pagina, "ampla", "realizar")
        capturar(pagina, "06-c06-ampla-sorteada-ppp-nao")
        pagina.goto(tela(C06))
        enviar(pagina, lista_ppp, "realizar")
        capturar(pagina, "07-c06-sorteio-concluido")
        pagina.goto(tela(C06))
        capturar(pagina, "07b-c06-concluido-aberto-pelo-topo")
        pagina.goto(f"{BASE}/gestao/editais/{C06[0]}/centro/")
        capturar(pagina, "11-c06-centro-depois-dos-sorteios")

        # Quem lê e não conduz: a auditoria.
        auditoria = entrar(navegador, "auditoria.142", papeis=["auditor"])
        auditoria.goto(tela(C06))
        capturar(auditoria, "10-c06-auditoria-sem-permissao-de-conduzir")

        # A operação recusada (F-1 do estudo, D-5 decidida): na rodada seguinte do C06, a semente
        # obtida antes de fixar a PPP condena a PPP com a fonte que publica a hora.
        C06_R2 = rodada_seguinte_do_c06()
        if C06_R2:
            pagina.goto(tela(C06_R2))
            r2_ppp = ppp(pagina)
            enviar(pagina, "ampla", "relacao")
            enviar(pagina, None, "ocorrencia")
            capturar(pagina, "09-c06r2-semente-antes-da-ppp")
            pagina.goto(tela(C06_R2) + f"?lista={r2_ppp}#recorte-{r2_ppp}")
            enviar(pagina, r2_ppp, "relacao")
            pagina.goto(tela(C06_R2))
            enviar(pagina, r2_ppp, "realizar")
            capturar(pagina, "08-c06r2-sorteio-recusado")

        # A 375 px: o começo e o fim.
        estreita = entrar(navegador, PRESIDENCIA, 375, 812)
        estreita.goto(tela(C07))
        capturar(estreita, "04-c07-375", dobra=False)
        estreita.goto(tela(C06))
        capturar(estreita, "07-c06-375", dobra=False)

        print("violações de CSP:", violacoes)
        import json

        (SAIDA / f"{LADO}-medidas.json").write_text(json.dumps(MEDIDAS, indent=1, ensure_ascii=False))
        navegador.close()


if __name__ == "__main__":
    main()
