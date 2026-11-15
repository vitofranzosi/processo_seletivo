import json, sys, re, collections, glob
S, D = sys.argv[1], sys.argv[2]
inv = json.load(open(f"{S}/inventario-coberto.json"))
comp = {}
for r in json.load(open(f"{S}/rastreio-complemento.json")):
    if r.get("status") == 200: comp.setdefault(r["padrao"], r)
larg = json.load(open(f"{S}/larguras.json"))
# regra: (regex da rota, área, arquétipo, perfil)
R = [
 (r"^/gestao/$", "Processos e Editais", "Central de trabalho", "todo perfil da gestão"),
 (r"^/gestao/(identificar|entrar|sem-acesso)", "Acesso à gestão", "Acesso", "qualquer pessoa"),
 (r"^/gestao/acessos/formalizacao", "Formalização", "Lista administrativa", "administrador de acessos"),
 (r"^/gestao/formalizacao/editais/[^/]+/(verificar|baixar|pessoas)", "Formalização", "Confirmação de ato", "setor da formalização"),
 (r"^/gestao/formalizacao/editais", "Formalização", "Página de entidade", "setor da formalização"),
 (r"^/gestao/formalizacao/$", "Formalização", "Lista administrativa", "setor da formalização"),
 (r"^/gestao/(administracao-de-)?acessos/(conceder|vinculos|pessoas/.+)", "Acessos", "Confirmação de ato", "administrador de acessos / institucional"),
 (r"^/gestao/(administracao-de-)?acessos", "Acessos", "Lista administrativa", "administrador de acessos / institucional"),
 (r"^/gestao/administracao-de-unidades/(cadastrar|unidades/[^/]+/editar)", "Unidades", "Formulário de configuração", "administrador institucional"),
 (r"^/gestao/administracao-de-unidades/unidades/[^/]+/(desativar|reativar)", "Unidades", "Confirmação de ato", "administrador institucional"),
 (r"^/gestao/administracao-de-unidades/unidades", "Unidades", "Página de entidade", "administrador institucional"),
 (r"^/gestao/administracao-de-unidades", "Unidades", "Lista administrativa", "administrador institucional"),
 (r"^/gestao/trilha-da-unidade", "Unidade", "Registro e histórico", "gestor, auditor"),
 (r"^/gestao/visao-geral/relatorio/conjunto", "Visão Geral", "Relatório", "gestor"),
 (r"^/gestao/visao-geral/relatorio", "Visão Geral", "Formulário de configuração", "gestor"),
 (r"^/gestao/visao-geral", "Visão Geral", "Central de trabalho", "gestor"),
 (r"^/gestao/agenda", "Agenda", "Central de trabalho", "todo perfil da gestão"),
 (r"^/gestao/documentacao", "Ajuda", "Guia incorporado", "todo perfil da gestão"),
 (r"^/gestao/autoridades", "Unidade", "Formulário de configuração", "gestor"),
 (r"^/gestao/modelos-de-aviso/(novo|<)", "Avisos", "Formulário de configuração", "comunicação, presidência"),
 (r"^/gestao/modelos-de-aviso", "Avisos", "Lista administrativa", "comunicação, presidência"),
 (r"^/gestao/processos/criar|/editais/criar", "Processos e Editais", "Formulário de configuração", "gestor, elaborador"),
 (r"^/gestao/processos/[^/]+/atos", "Processos e Editais", "Confirmação de ato", "gestor"),
 (r"^/gestao/processos/[^/]+/supervisao", "Processos e Editais", "Central de trabalho", "gestor"),
 (r"^/gestao/processos/[^/]+/comissao", "Comissão", "Formulário de configuração", "gestor, presidência"),
 (r"^/gestao/processos/[^/]+/alocacoes", "Comissão", "Formulário de configuração", "presidência"),
 (r"^/gestao/processos/[^/]+/auditoria", "Comissão", "Registro e histórico", "auditor, presidência"),
 (r"^/gestao/processos/[^/]+/$", "Processos e Editais", "Página de entidade", "todo perfil da gestão"),
 (r"^/gestao/editais/[^/]+/(pagina-anterior/|$)", "Centro de Controle", "Página de entidade", "todo perfil da gestão"),
 (r"^/gestao/editais/[^/]+/centro/", "Centro de Controle", "Página de entidade", "todo perfil da gestão"),
 (r"^/gestao/editais/[^/]+/(duvidas|assistente)", "Assistente de dúvidas", "Central de trabalho", "participante do piloto"),
 (r"^/gestao/editais/[^/]+/compor", "Composição do Edital", "Formulário de configuração", "elaborador"),
 (r"^/gestao/editais/[^/]+/reaproveitar", "Composição do Edital", "Formulário de configuração", "elaborador"),
 (r"^/gestao/editais/[^/]+/previa$", "Composição do Edital", "Avaliação ou conferência", "elaborador, homologador"),
 (r"^/gestao/editais/[^/]+/atos", "Publicação", "Confirmação de ato", "elaborador, homologador, publicador"),
 (r"^/gestao/editais/[^/]+/retificar", "Retificação", "Formulário de configuração", "elaborador"),
 (r"^/gestao/retificacoes/[^/]+/editar", "Retificação", "Formulário de configuração", "elaborador"),
 (r"^/gestao/retificacoes/[^/]+/atos", "Retificação", "Confirmação de ato", "elaborador, homologador, publicador"),
 (r"^/gestao/retificacoes", "Retificação", "Página de entidade", "todo perfil da gestão"),
 (r"^/gestao/editais/[^/]+/(auditoria)", "Auditoria", "Registro e histórico", "auditor"),
 (r"^/gestao/editais/[^/]+/relatorio", "Relatórios", "Relatório", "gestor, presidência"),
 (r"^/gestao/editais/[^/]+/kit-de-divulgacao", "Divulgação", "Central de trabalho", "comunicação"),
 (r"^/gestao/editais/[^/]+/formalizacao", "Formalização", "Formulário de configuração", "presidência"),
 (r"^/gestao/editais/[^/]+/matriculas", "Matrículas", "Operação com etapas", "exportador de matrículas"),
 (r"^/gestao/editais/[^/]+/inscricoes/publicacoes", "Inscrições", "Operação com etapas", "presidência, publicador"),
 (r"^/gestao/editais/[^/]+/inscricoes", "Inscrições", "Lista administrativa", "presidência, gestor"),
 (r"^/gestao/inscricoes", "Inscrições", "Página de entidade", "presidência, gestor"),
 (r"^/gestao/editais/[^/]+/distribuicao/[^/]+/(consolidar|remover|ocorrencia)", "Avaliação", "Confirmação de ato", "presidência"),
 (r"^/gestao/editais/[^/]+/distribuicao/[^/]+/(trilha|conclusoes|resultados|impedimentos)", "Avaliação", "Registro e histórico", "presidência"),
 (r"^/gestao/editais/[^/]+/distribuicao", "Avaliação", "Operação com etapas", "presidência"),
 (r"^/gestao/editais/[^/]+/marcos/[^/]+/(emitir|corte/emitir|corte/continuar|conducao/.+|convocacao/convocar|convocacao/titulares|ocupacao/(acrescentar|desfazer|declarar).*)", "Classificação e vagas", "Confirmação de ato", "presidência"),
 (r"^/gestao/editais/[^/]+/marcos/[^/]+/atos/[^/]+/publicar", "Resultados", "Confirmação de ato", "presidência, publicador"),
 (r"^/gestao/editais/[^/]+/marcos/[^/]+/(atos/|publicacoes|ocupacao/historico|convocacao/historico)", "Classificação e vagas", "Registro e histórico", "presidência"),
 (r"^/gestao/editais/[^/]+/cortes", "Classificação e vagas", "Registro e histórico", "presidência"),
 (r"^/gestao/editais/[^/]+/marcos/[^/]+/convocacao/[^/]+/documentos", "Convocação", "Avaliação ou conferência", "presidência, conferência"),
 (r"^/gestao/editais/[^/]+/(marcos/[^/]+/(convocacao/)?avisos|avisos)|^/gestao/avisos", "Avisos", "Confirmação de ato", "presidência, comunicação"),
 (r"^/gestao/editais/[^/]+/convocacoes/publicacao", "Convocação", "Operação com etapas", "presidência, publicador"),
 (r"^/gestao/editais/[^/]+/marcos/[^/]+/sorteio", "Sorteio", "Operação com etapas", "presidência"),
 (r"^/gestao/editais/[^/]+/marcos/[^/]+/convocacao", "Convocação", "Operação com etapas", "presidência"),
 (r"^/gestao/editais/[^/]+/marcos", "Classificação e vagas", "Operação com etapas", "presidência"),
 (r"^/gestao/editais/[^/]+/recursos", "Recursos", "Lista administrativa", "julgador, presidência"),
 (r"^/gestao/recursos", "Recursos", "Avaliação ou conferência", "julgador, presidência"),
 (r"^/gestao/minhas-etapas/[^/]+/[^/]+/inscricoes", "Mesa de avaliação", "Avaliação ou conferência", "avaliador"),
 (r"^/gestao/minhas-etapas/[^/]+/[^/]+$", "Mesa de avaliação", "Lista administrativa", "avaliador"),
 (r"^/gestao/minhas-etapas", "Minhas atividades", "Central de trabalho", "comissão"),
 (r"^/selecoes/acesso", "Portal — acesso", "Acesso", "candidato"),
 (r"^/selecoes/(meus-dados|conta)", "Portal — conta", "Jornada do candidato", "candidato"),
 (r"^/selecoes/inscricoes/|^/selecoes/recursos|^/selecoes/inscricoes/$", "Portal — área do candidato", "Jornada do candidato", "candidato"),
 (r"^/selecoes/(resultados|inscricoes-publicadas|convocacoes|sorteio)", "Portal — publicações", "Portal público", "sem autenticação"),
 (r"^/selecoes/", "Portal — vitrine e seleção", "Portal público", "sem autenticação"),
]
def classe(rota):
    for rx, *resto in R:
        if re.search(rx, rota): return resto
    return ["?", "?", "?"]
SUITE = {"/gestao/acessos": "suíte: `acessos-busca`, `acessos-historico`", "/gestao/acessos/conceder": "suíte: `acessos-busca`, `acessos-confirmacao`", "/gestao/administracao-de-acessos": "suíte: `acessos-administradores`", "/gestao/administracao-de-acessos/pessoas/<str:identificador>/suspender": "suíte: `acessos-suspensao`", "/gestao/administracao-de-acessos/pessoas/<str:identificador>/reativar": "suíte: `acessos-reativacao`", "/gestao/sem-acesso": "suíte: `sem-acesso`", "/gestao/administracao-de-unidades/cadastrar": "suíte: `unidades-conferencia`"}
def norm(rota): return re.sub(r"<(uuid|str|slug|path):[a-z_]+>", "<id>", rota)
telas, apoio = [], collections.Counter()
for o in inv:
    tpls = [t.split("/")[-1] for t in o["templates"]]
    if "api" in o["modulo"] or o["rota"].startswith("/api"): apoio["API REST (sem tela)"] += 1; continue
    if "/fragmentos/" in o["rota"] or (tpls and all(t.startswith("_") for t in tpls)): apoio["Fragmento htmx (parte de tela)"] += 1; continue
    if not tpls: apoio["Gesto por POST, download ou redirecionamento (sem tela própria)"] += 1; continue
    telas.append(o)
linhas, sit = [], collections.Counter(); por_arq = collections.Counter(); por_area = collections.defaultdict(list)
for o in telas:
    area, arq, perfil = classe(o["rota"]); k = norm(o["rota"])
    est = [e for e in o["estados"]]
    c = comp.get(k) or comp.get(re.sub(r"<id>", "<id>", k))
    if est: ev, s = f"navegador · {len(est)} estado(s) · {', '.join(o['vista_por'])}", "inspecionada"
    elif any(re.fullmatch(re.sub(r"<[^>]+>", "[^/]+", o["rota"]), p) for p in comp): ev, s = "navegador (passada complementar)", "inspecionada"
    elif o["rota"] in SUITE: ev, s = SUITE[o["rota"]], "captura da suíte"
    else: ev, s = "leitura do template", "não vista no navegador"
    sit[s] += 1; por_arq[arq] += 1
    por_area[area].append((o["rota"], o["view"], ", ".join(t.split("/")[-1] for t in o["templates"] if not t.split("/")[-1].startswith("_")), arq, perfil, ev, s))
out = ["# A. Inventário de interfaces", "", "*Gerado por `medicoes/gerar_inventario.py` a partir do resolvedor de URLs do Django e do rastreio no navegador. Base: `main` em `37ed0ad0`, 14/11/2026.*", "",
 "## Como ler", "",
 "- **Rota** é o padrão de URL; **tela** é a view que a serve. Uma rota conta como tela quando rende um template inteiro.",
 "- **Estado** é uma variação da mesma tela: um parâmetro de consulta (aba, filtro, recorte) ou o momento do certame em que o Edital está. Estados não entram na contagem de telas.",
 "- **Perfil** é o papel a que a seção se destina, pelo menu e pelas specs. A regra de autorização de cada rota não foi conferida uma a uma.",
 "- **Situação**: *inspecionada* quer dizer aberta num Chromium real, medida e capturada; *captura da suíte* vem das jornadas de `tests/navegador/`; *não vista no navegador* foi só lida no template.", "",
 "## Contagem", "", f"| O que | Quantas |", "|---|---:|", f"| Rotas no resolvedor | {len(inv)} |", f"| **Rotas que rendem tela** | **{len(telas)}** |"]
for k, v in apoio.items(): out.append(f"| {k} | {v} |")
out += ["", "| Situação da inspeção | Rotas |", "|---|---:|"] + [f"| {k} | {v} |" for k, v in sit.most_common()]
out += ["", "| Arquétipo | Rotas |", "|---|---:|"] + [f"| {k} | {v} |" for k, v in por_arq.most_common()]
n_padroes = len(larg)
tot = 0; padr = set()
for f in glob.glob(f"{S}/rastreio-*.json"):
    for r in json.load(open(f)):
        if r.get("status") == 200: tot += 1; padr.add(r["padrao"])
n_padroes = len(padr)
out += ["", f"No navegador foram abertas **{n_padroes} variações de tela** (rota + parâmetros), em {tot} visitas com resposta 200, por nove identidades: a presidência com todos os papéis da demonstração (em dois Processos), um avaliador, o setor da formalização, quatro candidatos fictícios e o visitante sem autenticação.", "",
 "## Telas por área", ""]
for area in sorted(por_area):
    out += [f"### {area}", "", "| Rota | Tela | Template | Arquétipo | Perfil | Evidência | Situação |", "|---|---|---|---|---|---|---|"]
    for rota, view, tpl, arq, perfil, ev, s in por_area[area]:
        out.append(f"| `{rota}` | `{view}` | {tpl} | {arq} | {perfil} | {ev} | {s} |")
    out.append("")
open(f"{D}/01-inventario.md", "w").write("\n".join(out))
print(len(telas), dict(sit), dict(por_arq)); print([a for a in por_area if a == "?"], [r for r in por_area.get("?", [])])
