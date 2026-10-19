import json
import os
import sys

sys.path.insert(0, os.getcwd())
import django  # noqa: E402

django.setup()
from processo_seletivo.interface.urls import urlpatterns  # noqa: E402

resultados = json.load(open(sys.argv[1]))
PASTA = sys.argv[2]  # nome da pasta das capturas, relativo ao .md

POST = {
    "sair", "anexos", "consolidar-resultados", "distribuicao-remover", "reabrir-avaliacao",
    "emitir-ordenacao", "emitir-corte", "emitir-apuracao", "causar-faixa", "convocar",
    "convocar-titulares", "nao-atendimento-dos-vencidos", "emitir-pendentes", "desfechar",
    "comunicar-convocacao", "atestar", "continuar-corte", "publicar-relacao-do-sorteio",
    "observar-ocorrencia-do-sorteio", "realizar-sorteio", "anular-sorteio", "publicar-resultado",
    "gesto-do-marco", "recurso-admitir", "recurso-julgar", "recurso-instruir",
    "mesa-avaliacao-gravar", "mesa-avaliacao-concluir", "modelo-de-aviso-situacao",
    "assistente-nova", "assistente-prototipo-perguntar", "assistente-prototipo-sugestao",
    "assistente-prototipo-nova",
}
DOWNLOAD = {
    "previa-documento": "PDF da prévia do Edital",
    "anexo-arquivo": "arquivo do Anexo do rascunho",
    "documento-da-inscricao": "arquivo enviado pelo candidato",
    "recurso-documento-instruido": "arquivo juntado na instrução do recurso",
    "mesa-documento": "arquivo da inscrição, aberto na Mesa",
}
NAO_MONTADA = {
    "aviso-da-chamada": (
        "exige `?comunicacao=` de uma `ComunicacaoEmitida` **por publicação** e enviada; o "
        "`seed_demo` convoca, mas não emite comunicação nessa forma. Responde 404 sem ela, para "
        "qualquer identidade"
    ),
}

por_rota = {}
for linha in resultados:
    por_rota.setdefault(linha["rota"], []).append(linha)

nomes = [p.name for p in urlpatterns]
caminho_de = {p.name: "/gestao/" + str(p.pattern) for p in urlpatterns}
telas = [n for n in nomes if n not in POST and n not in DOWNLOAD and not n.startswith("fragmento-")]
sem_tela = [n for n in nomes if n not in telas]
for n in telas:
    assert n in por_rota, n


def estouro(m):
    return m["scrollWidth"] > m["clientWidth"]


def celula_375(linha):
    m = linha.get("375")
    if not m:
        return "—"
    if estouro(m):
        return f"**sim** ({m['scrollWidth']} px)"
    return "não"


def capturas(linha):
    if "375" not in linha:
        return "—"
    return (f"[375]({PASTA}/{linha['375']['arquivo']}) · "
            f"[1280]({PASTA}/{linha['1280']['arquivo']})")


variantes = [lin for n in telas for lin in por_rota[n]]
carregadas = [lin for lin in variantes if "375" in lin]
estouram = [lin for lin in carregadas if estouro(lin["375"])]
estouram_1280 = [lin for lin in carregadas if estouro(lin["1280"])]

saida = []
w = saida.append
w(f"<!-- gerado por {PASTA}/gerar_doc.py a partir de {PASTA}/resultados.json -->")
w("")
w("| Números | |")
w("|---|---|")
w(f"| Rotas em `interface/urls.py` | {len(nomes)} |")
w(f"| Rotas que renderizam tela por GET | {len(telas)} |")
w(f"| Variantes capturadas (rota × slug ou estado) | {len(carregadas)} de {len(variantes)} |")
w(f"| Estouram a 375 px | {len(estouram)} |")
w(f"| Estouram a 1280 px | {len(estouram_1280)} |")
w(f"| Rotas sem tela (POST, fragmento htmx, download) | {len(sem_tela)} |")
w("")
w("## Telas")
w("")
w("| # | Rota (`name`) | Caminho medido | Identidade | Carregou | Estoura a 375 | Capturas |")
w("|---|---|---|---|---|---|---|")
i = 0
for n in telas:
    for lin in por_rota[n]:
        i += 1
        rotulo = f"`{n}`" + (f"<br>{lin['obs']}" if lin["obs"] else "")
        caminho = "`" + lin["caminho"] + "`"
        quem = f"`{lin['identidade']}`" if lin["identidade"] else (
            "sem identidade" if lin["id"] == "identificar" else "nenhuma")
        if lin["id"] == "identificar":
            quem = "sem identidade"
        if "375" in lin:
            carregou = "sim"
        else:
            carregou = f"**não** — {lin['status']}"
        w(f"| {i} | {rotulo} | {caminho} | {quem} | {carregou} | {celula_375(lin)} | {capturas(lin)} |")
w("")
w("### Não montadas")
w("")
for n, motivo in NAO_MONTADA.items():
    lins = por_rota[n]
    assert all("375" not in lin for lin in lins), n
    tent = ", ".join(lins[0]["tentativas"])
    w(f"- `{n}` (`{caminho_de[n]}`): {motivo}. Tentativas: {tent}.")
for lin in variantes:
    if "375" not in lin and lin["rota"] not in NAO_MONTADA:
        raise SystemExit(f"tela não montada sem motivo: {lin['id']}")
w("")
w("## Rotas sem tela")
w("")
w("Listadas para que a conta feche com o `urls.py`. Nenhuma foi capturada.")
w("")
w("| Rota (`name`) | Caminho | Por que não é tela |")
w("|---|---|---|")
for n in sem_tela:
    if n in POST:
        motivo = "só POST"
    elif n in DOWNLOAD:
        motivo = f"download: {DOWNLOAD[n]}"
    else:
        motivo = "fragmento htmx"
    w(f"| `{n}` | `{caminho_de[n]}` | {motivo} |")
w("")
w("## Medições dos estouros")
w("")
w("| Tela | `scrollWidth` a 375 | Elemento mais externo que passa da borda |")
w("|---|---|---|")
for lin in estouram:
    culp = ", ".join(f"`{c}`" for c in lin["375"]["culpados"]) or "(ver abaixo)"
    w(f"| `{lin['id']}` | {lin['375']['scrollWidth']} | {culp} |")
print("\n".join(saida))
