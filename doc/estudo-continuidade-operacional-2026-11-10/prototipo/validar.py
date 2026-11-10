# ruff: noqa: E501 — roteiro de estudo, fora do lint do backend: as linhas longas são
# descrições de página e frases de asserção, que se leem melhor inteiras.
"""A validação automatizada dos protótipos: o que cada melhoria promete, medido no navegador.

    cd backend && uv run python ../doc/estudo-continuidade-operacional-2026-11-10/prototipo/validar.py

Sobe o servidor do protótipo com a CSP da gestão, percorre o "antes" e o "depois" e confere:
- **as promessas de cada melhoria** (V1 a V11), como asserções: a posição do ato em relação à dobra, o
  destino de cada link, o percurso de ida e volta ao Centro, a conferência antes de convocar;
- **o que o "depois" não pode piorar**: nenhuma violação de CSP nova, nenhum estilo ou script inline
  novo, nenhuma rolagem horizontal nova a 375 px;
- **o que precisa continuar igual**: os números das vagas, o resumo do método publicado.

Grava `validacao.txt` e as capturas `prototipo-*.png`. Sai com código 1 se alguma asserção falhar.
"""

import re
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright
from servidor import servir

AQUI = Path(__file__).resolve().parent
SITIO = AQUI / "sitio"
CAPTURAS = AQUI.parent / "capturas"
PORTA = 8173
BASE = f"http://127.0.0.1:{PORTA}"
DOBRA = 900

resultados = []


def conferir(codigo, descricao, ok, detalhe=""):
    resultados.append((codigo, descricao, ok, detalhe))
    print(f"{'✓' if ok else '✗'} {codigo} {descricao} {detalhe}")


def y(pagina, seletor):
    caixa = pagina.locator(seletor).first.bounding_box()
    return round(caixa["y"] + pagina.evaluate("window.scrollY")) if caixa else None


def na_dobra(caixa):
    # A rolagem até a âncora deixa o alvo em y≈0, às vezes −0,3 px por arredondamento.
    return caixa is not None and -2 <= caixa["y"] < DOBRA


def inline(texto):
    """Estilo e script que a CSP recusa: atributo style, bloco style, script sem src, on*=."""
    return (
        len(re.findall(r"\sstyle=\"", texto))
        + len(re.findall(r"<style[\s>]", texto))
        + len(re.findall(r"<script(?![^>]*\ssrc=)[^>]*>", texto))
        + len(re.findall(r"\son[a-z]+=\"", texto))
    )


def main():
    servidor = servir(PORTA)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    paginas = sorted(p.stem for p in (SITIO / "depois").glob("*.html"))
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch()
            for largura in (1440, 375):
                contexto = navegador.new_context(
                    viewport={"width": largura, "height": DOBRA}, locale="pt-BR"
                )
                pagina = contexto.new_page()
                violacoes = []
                pagina.on(
                    "console",
                    lambda m, violacoes=violacoes: violacoes.append(m.text)
                    if "Content Security Policy" in m.text
                    else None,
                )
                for nome in paginas:
                    antes_nome = "convocacao-c15" if nome == "convocar-c15-conferencia" else nome
                    medidas = {}
                    for lado, arquivo in (("antes", antes_nome), ("depois", nome)):
                        violacoes.clear()
                        pagina.goto(f"{BASE}/{lado}/{arquivo}.html")
                        largura_doc = pagina.evaluate("document.documentElement.scrollWidth")
                        medidas[lado] = (len(violacoes), largura_doc > largura)
                        if largura == 1440:
                            pagina.screenshot(
                                path=str(CAPTURAS / f"prototipo-{lado}-{nome}-dobra.png")
                            )
                        elif nome in (
                            "sorteio-c06-inicial",
                            "documentos-c12-apos-conferir",
                            "convocar-c15-conferencia",
                        ):
                            pagina.screenshot(
                                path=str(CAPTURAS / f"prototipo-{lado}-{nome}-375.png")
                            )
                    conferir(
                        "V0",
                        f"{nome} a {largura}px: sem CSP nova e sem rolagem horizontal nova",
                        medidas["depois"][0] <= medidas["antes"][0]
                        and (medidas["depois"][1] <= medidas["antes"][1]),
                        f"csp antes={medidas['antes'][0]} depois={medidas['depois'][0]}; rolagem antes={medidas['antes'][1]} depois={medidas['depois'][1]}",
                    )
                contexto.close()

            for nome in paginas:
                antes_nome = "convocacao-c15" if nome == "convocar-c15-conferencia" else nome
                a = inline((SITIO / "antes" / f"{antes_nome}.html").read_text())
                d = inline((SITIO / "depois" / f"{nome}.html").read_text())
                conferir(
                    "V0",
                    f"{nome}: nenhum estilo ou script inline novo",
                    d <= a,
                    f"antes={a} depois={d}",
                )

            pagina = navegador.new_page(viewport={"width": 1440, "height": DOBRA})

            # V1 — o ato do sorteio sobe acima da observação, e para dentro da dobra.
            pagina.goto(f"{BASE}/antes/sorteio-c06-inicial.html")
            antes_fixar = y(pagina, "button:has-text('Publicar e congelar a relação')")
            antes_observar = y(pagina, "button:has-text('Observar a ocorrência')")
            pagina.goto(f"{BASE}/depois/sorteio-c06-inicial.html")
            depois_fixar = y(pagina, "a:has-text('Fixar os participantes desta lista')")
            depois_observar = y(pagina, "button:has-text('Observar a ocorrência')")
            conferir(
                "V1",
                "sorteio: fixar vem antes de observar",
                depois_fixar < depois_observar and antes_fixar > antes_observar,
                f"antes fixar={antes_fixar} observar={antes_observar}; depois fixar={depois_fixar} observar={depois_observar}",
            )
            conferir(
                "V1",
                "sorteio: o primeiro 'fixar' sobe",
                depois_fixar < antes_fixar,
                f"{antes_fixar}px → {depois_fixar}px (dobra {DOBRA})",
            )
            # V2 — o aviso de corte antes do sorteio sai; V3 — o método publicado continua inteiro.
            conferir(
                "V2",
                "sorteio: sem 'Nenhum corte emitido' antes do sorteio",
                "Nenhum corte emitido" not in pagina.inner_text("main"),
            )
            texto_antes = (SITIO / "antes/sorteio-c06-inicial.html").read_text()
            resumo = re.search(r"[0-9a-f]{64}", texto_antes).group(0)
            dentro = (
                pagina.locator("details.metodo-recolhido").inner_text()
                if pagina.locator("details.metodo-recolhido").count()
                else ""
            )
            conferir(
                "V3",
                "sorteio: o resumo do método publicado continua na tela, recolhido",
                resumo in pagina.content()
                and pagina.locator("details.metodo-recolhido").count() == 1,
                resumo[:12],
            )
            del dentro
            # V10 — toda frase sobre a ordem semente × fixar está marcada como dependente da D-5.
            frases = pagina.locator("main :text('fixada depois de conhecida a semente')").count()
            marcadas = pagina.locator(
                ".dependente-da-d5:has-text('fixada depois de conhecida a semente')"
            ).count()
            conferir(
                "V10",
                "sorteio: a frase da ordem semente × fixar só aparece marcada D-5",
                frases == marcadas and marcadas >= 1,
                f"{marcadas} de {frases}",
            )
            # V11 — teclado: o Tab chega ao "fixar" antes do "observar".
            pagina.goto(f"{BASE}/depois/sorteio-c06-inicial.html")
            ordem = []
            for _ in range(60):
                pagina.keyboard.press("Tab")
                ordem.append(
                    pagina.evaluate("document.activeElement.textContent.trim().slice(0, 40)")
                )
            i_fixar = next(
                (i for i, t in enumerate(ordem) if t.startswith("Fixar os participantes desta")), 99
            )
            i_observar = next(
                (i for i, t in enumerate(ordem) if t.startswith("Observar a ocorrência")), 99
            )
            conferir(
                "V11",
                "sorteio: o Tab alcança 'fixar' antes de 'observar'",
                i_fixar < i_observar,
                f"posições {i_fixar} e {i_observar}",
            )

            # V4/V6 — o percurso A, de ida e volta: Centro → sorteio → fixar → feedback → Centro.
            pagina.goto(f"{BASE}/depois/centro-c06-inicial.html")
            pagina.locator("a:has-text('Abrir a tela')").first.click()
            pagina.wait_for_load_state()
            alvo = pagina.evaluate("location.hash")
            conferir(
                "V5",
                "Centro C06 → sorteio aterrissa nos recortes, dentro da dobra",
                alvo == "#titulo-recortes" and na_dobra(pagina.locator(alvo).bounding_box()),
                alvo,
            )
            pagina.locator("a:has-text('Fixar os participantes desta lista')").first.click()
            pagina.wait_for_load_state()
            conferir(
                "V6",
                "fixar a ampla leva ao estado seguinte",
                pagina.url.endswith("sorteio-c06-apos-fixar-a-ampla.html"),
                pagina.url[-40:],
            )
            ainda = pagina.locator("p.ainda-neste-marco a[href='#recorte-ppp']").count()
            conferir(
                "V4",
                "feedback: 'Ainda neste marco' é link para a lista que falta, e ela existe",
                ainda == 1 and pagina.locator("#recorte-ppp").count() == 1,
            )
            y_feedback = y(pagina, "p.retorno-ao-centro a")
            conferir(
                "V4",
                "feedback: o retorno ao Centro está na dobra",
                y_feedback is not None and y_feedback < DOBRA,
                f"y={y_feedback}",
            )
            pagina.locator("p.retorno-ao-centro a").click()
            pagina.wait_for_load_state()
            conferir(
                "V6",
                "o retorno chega ao Centro no estado novo",
                pagina.url.endswith("centro-c06-apos-fixar-a-ampla.html"),
            )
            pagina.locator("main a:has-text('Fixar os participantes')").first.click()
            pagina.wait_for_load_state()
            conferir(
                "V5",
                "Centro → a lista que falta (PPP), na dobra",
                pagina.evaluate("location.hash") == "#recorte-ppp"
                and na_dobra(pagina.locator("#recorte-ppp").bounding_box()),
            )

            # V7 — o percurso E: Centro → chamadas → documentos → desfecho, e a volta.
            pagina.goto(f"{BASE}/antes/convocacao-c12.html")
            antes_chamadas = y(pagina, "#chamadas")
            pagina.goto(f"{BASE}/depois/centro-c12.html")
            pagina.locator("main a:has-text('Conferir os documentos')").first.click()
            pagina.wait_for_load_state()
            conferir(
                "V5",
                "Centro C12 → chamadas praticadas, na dobra (antes: no topo, a chamada a tantos px)",
                pagina.evaluate("location.hash") == "#chamadas"
                and na_dobra(pagina.locator("#chamadas").bounding_box()),
                f"antes a seção ficava a {antes_chamadas}px",
            )
            conferir(
                "V7",
                "convocação: o índice das seções existe e leva a cada uma",
                all(
                    pagina.locator(f"#{h.split('#')[1]}").count() == 1
                    for h in pagina.locator("nav.indice-da-tela a").evaluate_all(
                        "as => as.map(a => a.getAttribute('href'))"
                    )
                ),
            )
            pagina.locator(
                "article.recorte:has-text('Cecília') a:has-text('Documentos da convocação')"
            ).click()
            pagina.wait_for_load_state()
            conferir(
                "V7",
                "documentos: o próximo passo desta pessoa é o desfecho, e leva à chamada dela",
                pagina.locator("a:has-text('registrar o desfecho da Cecília')").get_attribute(
                    "href"
                )
                == "convocacao-c12.html#chamada-3",
            )
            conferir(
                "V7",
                "documentos: o contexto Edital · Perfil · lista está no alto",
                "Professor de Informática · Ampla concorrência" in pagina.inner_text("main"),
            )
            pagina.locator("a:has-text('registrar o desfecho da Cecília')").click()
            pagina.wait_for_load_state()
            conferir(
                "V7",
                "o desfecho da Cecília fica na dobra ao chegar",
                na_dobra(pagina.locator("#chamada-3").bounding_box()),
            )
            pagina.go_back()
            pagina.wait_for_load_state()
            pagina.locator("p.retorno-ao-centro a").click()
            pagina.wait_for_load_state()
            conferir("V6", "documentos → Centro do C12", pagina.url.endswith("centro-c12.html"))

            # V8/V9 — a conferência antes de convocar, e os números da apuração intactos.
            pagina.goto(f"{BASE}/antes/convocacao-c15.html")
            numeros_antes = pagina.locator(
                "#numeros ~ * strong, #numeros + * strong"
            ).all_inner_texts()
            botao_antes = pagina.locator("button:has-text('Convocar as 2')").count()
            pagina.goto(f"{BASE}/depois/convocacao-c15.html")
            numeros_depois = pagina.locator(
                "#numeros ~ * strong, #numeros + * strong"
            ).all_inner_texts()
            conferir(
                "V9",
                "convocação: os números das vagas não mudam, só o rótulo",
                numeros_antes == numeros_depois
                and "Ocupadas na apuração" in pagina.inner_text("main"),
                f"{numeros_antes[:6]}",
            )
            conferir(
                "V8",
                "convocação: a ajuda não promete mais uma conferência que não existe",
                "antes de confirmar, você o verá como o candidato" not in pagina.inner_text("main"),
            )
            pagina.locator("a:has-text('Convocar as 2')").click()
            pagina.wait_for_load_state()
            texto = pagina.inner_text("main")
            conferir(
                "V8",
                "convocar leva à conferência (antes: o botão praticava no clique)",
                pagina.url.endswith("convocar-c15-conferencia.html") and botao_antes == 1,
            )
            conferir(
                "V8",
                "a conferência mostra as 2 pessoas, o texto do candidato, o prazo e quem fica de fora",
                pagina.locator("#convocadas-titulo + ul li").count() == 2
                and "Serão convocadas (2)" in texto
                and "O que cada pessoa lerá" in texto
                and "Prazo" in texto
                and "Fica de fora" in texto,
            )
            pagina.locator("a:has-text('Cancelar e voltar')").click()
            pagina.wait_for_load_state()
            conferir(
                "V8", "cancelar volta à convocação", pagina.url.endswith("convocacao-c15.html")
            )
            navegador.close()
    finally:
        servidor.shutdown()

    falhas = [r for r in resultados if not r[2]]
    linhas = [
        f"{'ok' if ok else 'FALHOU'} | {codigo} | {descricao} | {detalhe}"
        for codigo, descricao, ok, detalhe in resultados
    ]
    (AQUI.parent / "validacao.txt").write_text(
        f"Validação dos protótipos — {len(resultados) - len(falhas)} de {len(resultados)} conferências passaram.\n\n"
        + "\n".join(linhas)
        + "\n"
    )
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
