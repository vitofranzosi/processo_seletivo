import sys, pathlib
D = pathlib.Path(sys.argv[1]) / "prototipos"
ICONES = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<symbol id="i-pasta" viewBox="0 0 24 24"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></symbol>
<symbol id="i-tarefa" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="m9 12 2 2 4-4"/></symbol>
<symbol id="i-grafico" viewBox="0 0 24 24"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></symbol>
<symbol id="i-agenda" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></symbol>
<symbol id="i-cubo" viewBox="0 0 24 24"><path d="m12 3 8 4.5v9L12 21l-8-4.5v-9zM12 12l8-4.5M12 12v9M12 12 4 7.5"/></symbol>
<symbol id="i-banco" viewBox="0 0 24 24"><path d="M3 10 12 4l9 6M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18"/></symbol>
<symbol id="i-carta" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></symbol>
<symbol id="i-trilha" viewBox="0 0 24 24"><path d="M4 6h10M4 12h7M4 18h10"/><circle cx="18" cy="12" r="2.5"/></symbol>
<symbol id="i-livro" viewBox="0 0 24 24"><path d="M4 5a2 2 0 0 1 2-2h6v16H6a2 2 0 0 0-2 2zM20 5a2 2 0 0 0-2-2h-6v16h6a2 2 0 0 1 2 2z"/></symbol>
<symbol id="i-mais" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></symbol>
<symbol id="i-seta" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>
<symbol id="i-arquivo" viewBox="0 0 24 24"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8zM14 3v5h5"/></symbol>
<symbol id="i-cima" viewBox="0 0 24 24"><path d="M12 19V5M6 11l6-6 6 6"/></symbol>
<symbol id="i-baixo" viewBox="0 0 24 24"><path d="M12 5v14M6 13l6 6 6-6"/></symbol>
<symbol id="i-lixo" viewBox="0 0 24 24"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/></symbol>
</defs></svg>'''
def ic(n): return f'<svg aria-hidden="true"><use href="#i-{n}"/></svg>'
def shell(titulo, trilha, corpo, atual="Processos Seletivos"):
    sec = [("TRABALHO", [("pasta", "Processos Seletivos"), ("tarefa", "Minhas atividades"), ("grafico", "Visão Geral"), ("agenda", "Agenda"), ("cubo", "Formalização")]),
           ("UNIDADE", [("banco", "Autoridades da unidade"), ("carta", "Modelos de aviso"), ("trilha", "Trilha da unidade")]), ("AJUDA", [("livro", "Documentação do Sistema")])]
    nav = "".join(f'<p class="grupo-de-secoes">{g}</p><ul class="secoes">' + "".join(f'<li><a href="#"{" aria-current=\"page\"" if r == atual else ""}>{ic(i)}{r}</a></li>' for i, r in its) + "</ul>" for g, its in sec)
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titulo} — proposta · GPS</title><link rel="stylesheet" href="gps-ds.css"></head><body>{ICONES}
<div class="shell"><div class="barra-lateral"><div class="marca-da-barra"><span class="sigla-do-produto">GPS</span><span class="nome-do-produto">Gestão de Processos Seletivos<span>Cefor/Ifes</span></span></div>
<nav aria-label="Seções">{nav}</nav>
<div class="pessoa-identificada"><span class="iniciais">TP</span><div><strong>treino.presidencia</strong><span>Presidência · Gestor</span></div></div></div>
<div class="area-de-trabalho"><header class="cabecalho-de-contexto"><p>{trilha}</p><a href="#">Trocar identidade</a></header>
<main>{corpo}</main></div></div></body></html>'''

# ───── 1. Lista de Processos Seletivos ─────
procs = [("SIM-TREINAMENTO-017", "Designação para a formalização", "SIM17/2026", "Convocação", "3 aptas sem setor designado", True),
 ("SIM-TREINAMENTO-012", "Conferência documental", "SIM12/2026", "Convocação", "3 convocações com documento a conferir", True),
 ("SIM-TREINAMENTO-010", "Convocação", "SIM10/2026", "Vagas", "3 titulares a convocar", True),
 ("SIM-TREINAMENTO-008", "Resultado preliminar e recursos", "SIM08/2026", "Resultado e recursos", "1 recurso aguardando decisão · até 19/11", True),
 ("SIM-TREINAMENTO-007", "Sorteio pronto para execução", "SIM07/2026", "Classificação", "Observar a extração", True),
 ("SIM-TREINAMENTO-005", "Avaliação pendente", "SIM05/2026", "Avaliação", "3 inscrições prontas para consolidar", True),
 ("SIM-TREINAMENTO-002", "Inscrições abertas", "SIM02/2026", "Inscrições", "Abertas até 14/12 · 3 enviadas", False),
 ("SIM-TREINAMENTO-001", "Elaboração de edital", "SIM01/2026", "Elaboração", "2 avisos antes de submeter", False)]
linhas = ""
for cod, nome, ed, fase, prox, preside in procs:
    sit = '<span class="situacao">Em elaboração</span>' if fase == "Elaboração" else '<span class="situacao ok">Publicado</span>'
    linhas += f'''<tr><td><a href="#"><strong>{nome}</strong></a><span class="segunda"><span class="codigo">{cod}</span> {'· você preside · ' if preside else '· '}<a href="#">Comissão</a> · <a href="#">Alocação</a></span></td>
<td><a href="#" class="codigo">{ed}</a></td><td>{sit}</td><td>{fase}<span class="segunda">{prox}</span></td></tr>'''
linhas += '''<tr><td><a href="#"><strong>Processo Seletivo Simplificado 2026</strong></a><span class="segunda"><span class="codigo">PS-DEMO-2026</span> · <a href="#">Comissão</a> · <a href="#">Alocação</a></span></td><td></td><td><span class="situacao ok">Ativo</span></td><td>3 Editais em fases diferentes</td></tr>
<tr class="filha"><td>Professor Substituto e Técnico-Administrativo</td><td><a href="#" class="codigo">01/2026</a></td><td><span class="situacao ok">Publicado</span></td><td>Inscrições<span class="segunda">Abertas até 04/12</span></td></tr>
<tr class="filha"><td>Seleção por sorteio</td><td><a href="#" class="codigo">26/2026</a></td><td><span class="situacao ok">Publicado</span></td><td>Classificação<span class="segunda">Sorteio realizado</span></td></tr>
<tr class="filha"><td>Seleção concluída</td><td><a href="#" class="codigo">51/2026</a></td><td><span class="situacao ok">Publicado</span></td><td>Convocação<span class="segunda">1 convocada, comunicação não enviada</span></td></tr>'''
lista = f'''<div class="cabecalho-da-pagina"><div class="titulo"><h1>Processos Seletivos</h1>
<p class="sub">Processos e Editais do Centro de Referência em Formação e em Educação a Distância.</p></div>
<div class="acoes"><a class="botao" href="#">{ic("mais")}Novo Processo Seletivo</a></div></div>
<div class="com-trilho"><div class="pilha">
<div class="cartao sem-recuo">
 <div class="cabeca"><nav class="abas" aria-label="Situação" style="border:0"><a href="#" aria-current="page">Em andamento <span>19</span></a><a href="#">Encerrados <span>0</span></a><a href="#">Cancelados <span>0</span></a><a href="#">Todos <span>19</span></a></nav>
 <form class="barra-de-filtros" role="search"><div class="campo busca"><label class="oculto" for="q">Buscar</label><input id="q" type="search" placeholder="Título, código ou número do Edital"></div><button class="acao">Buscar</button></form></div>
 <div class="tabela-rolavel"><table class="tabela empilha"><thead><tr><th>Processo</th><th>Edital</th><th>Situação</th><th>Fase e próximo passo</th></tr></thead><tbody>{linhas}</tbody></table></div>
 <div class="paginacao"><span>19 Processos, mostrando 1–9</span><span class="linha"><a class="acao" href="#">Anterior</a><a class="acao" href="#">Próxima</a></span></div>
</div></div>
<aside class="trilho" aria-label="Para você">
 <section class="cartao"><div class="cabeca" style="margin-bottom:.75rem"><h2>Ações disponíveis para você</h2><span class="marca">3</span></div>
 <ul class="itens"><li><div class="corpo"><strong>Decidir recursos (1)</strong><span>Edital SIM08/2026 · 1 aguardando decisão · até 19/11</span></div><a class="acao" href="#" aria-label="Decidir recursos do Edital SIM08/2026">Abrir</a></li>
 <li><div class="corpo"><strong>Continuar a elaboração</strong><span>Edital SIM01/2026 · em elaboração</span></div><a class="acao" href="#">Abrir</a></li>
 <li><div class="corpo"><strong>Continuar a elaboração</strong><span>Edital 76/2027 · em elaboração</span></div><a class="acao" href="#">Abrir</a></li></ul>
 <details class="explica" style="margin-top:.75rem"><summary>O que entra nesta lista</summary><p>Atos de Edital e de Retificação, recursos e avaliações. Classificação, sorteio, convocação e encerramento ficam em “O que fazer agora”, no Edital.</p></details></section>
 <section class="cartao"><h2>Da sua comissão</h2><p class="fraco" style="font-size:.875rem;margin-bottom:.75rem">Você integra a comissão de 13 Processos.</p><a class="botao secundario largo" href="#">Ver minhas atividades · 22</a></section>
 <p class="aviso info em-linha"><span><strong>Ambiente de demonstração.</strong> A identidade foi escolhida manualmente.</span></p>
</aside></div>'''
(D / "lista-de-processos.html").write_text(shell("Processos Seletivos", "GPS › Processos Seletivos", lista))

# ───── 2. Convocação ─────
ind = [("3", "titulares a convocar", "ativo"), ("0", "convocadas neste recorte", "zero"), ("0", "aguardando resposta", "zero"), ("0", "com documento a conferir", "zero"), ("0", "com pendência", "zero"), ("0", "prontas para o desfecho", "zero"), ("0", "com desfecho registrado", "zero")]
indic = "".join(f'<div class="indicador {c}"><strong>{n}</strong><span>{r}</span></div>' for n, r, c in ind)
fila = [("1º", "INS-2026-TB5YA4B7", "Alice Treinamento C10-01", "vaga inicial", "Titular"), ("2º", "INS-2026-3QA5NCG3", "Bernardo Treinamento C10-02", "vaga inicial", "Titular"), ("3º", "INS-2026-4MVF6DW3", "Cecília Treinamento C10-03", "vaga inicial", "Titular"), ("4º", "INS-2026-9T5HGQK2", "Davi Treinamento C10-04", "vaga que vagou", "Suplente"), ("5º", "INS-2026-NU7H2NRH", "Estela Treinamento C10-05", "vaga que vagou", "Suplente"), ("6º", "INS-2026-3PQZUMKW", "Fernando Treinamento C10-06", "vaga que vagou", "Suplente")]
fl = "".join(f'<tr><td class="numero">{p}</td><td><strong>{n}</strong><span class="segunda"><span class="codigo">{i}</span></span></td><td>{v}</td><td>{"<span class=\"situacao ok\">Titular</span>" if t == "Titular" else "<span class=\"situacao\">Suplente</span>"}</td><td class="acoes">{"" if t == "Titular" else "<a class=\"acao\" href=\"#\">Chamar</a>"}</td></tr>' for p, i, n, v, t in fila)
conv = f'''<div class="cabecalho-da-pagina"><div class="titulo"><h1>Convocação</h1>
<p class="sub">Edital SIM10/2026 · Professor de Informática · Classificação final</p></div>
<div class="acoes"><a class="botao discreto compacto" href="#">Termos desta tela</a><a class="acao" href="#">Histórico do recorte</a></div></div>
<div class="linha" style="margin-bottom:1.25rem"><span class="rotulo-de-secao">Recorte</span><nav class="segmentos" aria-label="Recorte"><a href="#" aria-current="page">Ampla concorrência</a><a href="#">Pessoas pretas, pardas e indígenas (PPP)</a></nav></div>
<section aria-labelledby="sit"><h2 id="sit" class="oculto">Situação atual</h2><div class="indicadores">{indic}</div></section>
<div class="com-trilho" style="margin-top:1.5rem"><div class="pilha">
<section class="cartao destaque" aria-labelledby="c1"><div class="cabeca"><h2 id="c1">Convocar os 3 titulares</h2><span class="marca perigo">Irreversível</span></div>
 <p class="fraco" style="font-size:.875rem;margin:.25rem 0 1rem;max-width:68ch">Uma convocação para cada pessoa, na ordem da fila, todas para vaga inicial. A comunicação sai por mensagem individual no mesmo ato.</p>
 <div class="campos"><div class="campo c-4"><label for="venc">Vencimento do prazo <span class="opcional">(opcional)</span></label><input id="venc" type="datetime-local"><span class="ajuda">O prazo corre a partir do envio da comunicação.</span></div>
 <div class="campo c-8"><label for="compl">Complemento do fundamento <span class="opcional">(opcional)</span></label><textarea id="compl" rows="2"></textarea><span class="ajuda">O candidato lê este texto depois do fundamento derivado.</span></div></div>
 <details class="explica" style="margin-top:.75rem"><summary>O candidato lerá este fundamento</summary><p>Convocação para vaga inicial no Edital nº SIM10/2026, Perfil «Professor de Informática», recorte «Ampla concorrência»: a posição da pessoa na ordem de classificação vigente está dentro das vagas que a apuração de ocupação emitida em 14/11/2026 considerou.</p></details>
 <div class="linha" style="margin-top:1rem"><a class="botao" href="#">Conferir antes de convocar as 3 {ic("seta")}</a><span class="ajuda">Nada é praticado nem enviado antes de você confirmar na conferência.</span></div></section>
<section class="cartao sem-recuo" aria-labelledby="c2"><div class="cabeca"><div><h2 id="c2">Fila deste recorte</h2><p class="fraco" style="font-size:.8125rem">Na ordem de chamada. Chamar um a um é o caminho do suplente e das exceções.</p></div><a class="acao" href="#">O que é a sucessão?</a></div>
 <div class="tabela-rolavel"><table class="tabela"><thead><tr><th class="numero">Posição</th><th>Participante</th><th>Seria chamada para</th><th>Na apuração</th><th><span class="oculto">Ações</span></th></tr></thead><tbody>{fl}</tbody></table></div></section>
<section class="cartao" aria-labelledby="c3"><h2 id="c3">Chamadas praticadas</h2><p class="vazio">Nenhuma convocação praticada neste recorte.</p></section>
</div>
<aside class="trilho" aria-label="Vagas e chamadas deste recorte">
 <section class="cartao calculado"><div class="cabeca" style="margin-bottom:.75rem"><h3>Pela apuração da ocupação</h3><span class="marca neutra">Calculado</span></div>
 <div class="indicadores compactos"><div class="indicador"><strong>3</strong><span>Publicadas no Edital</span></div><div class="indicador"><strong>3</strong><span>Efetivas</span></div><div class="indicador"><strong>3</strong><span>Consideradas ocupadas</span></div><div class="indicador zero"><strong>0</strong><span>A ocupar</span></div></div>
 <p class="ajuda" style="margin-top:.5rem">Conta vagas. Apuração vigente emitida em 14/11/2026 09:34.</p></section>
 <section class="cartao"><h3>Pelas chamadas praticadas</h3>
 <div class="indicadores compactos"><div class="indicador zero"><strong>0</strong><span>Pessoas convocadas</span></div><div class="indicador zero"><strong>0</strong><span>Aguardando resposta</span></div><div class="indicador zero"><strong>0</strong><span>Com desfecho</span></div><div class="indicador zero"><strong>0</strong><span>Aptas para formalização</span></div></div>
 <p class="ajuda" style="margin-top:.5rem">Conta pessoas, ato a ato.</p></section>
 <details class="explica"><summary>Por que os dois números não coincidem</summary><p>A apuração conta vagas, desde que é emitida; as chamadas contam pessoas. Nenhum dos dois diz quem está apta para formalização.</p></details>
 <p class="aviso info em-linha"><span>Abrir esta tela <strong>não convoca ninguém</strong> e não apura nada.</span></p>
</aside></div>'''
(D / "convocacao.html").write_text(shell("Convocação", 'GPS › <a href="#">Processos Seletivos</a> › <a href="#">SIM-TREINAMENTO-010</a> › <a href="#">Edital SIM10/2026</a> › Convocação', conv))

# ───── 3. Compor · Etapas de Avaliação ─────
passos = [("Identificação", "feito", "concluída"), ("Perfis de Vaga", "feito", "concluída"), ("Cronograma", "atencao", "2 avisos"), ("Etapas de Avaliação", "atual", "etapa atual"), ("Classificação", "feito", "concluída"), ("Inscrição", "feito", "concluída"), ("Anexos", "", "pendente"), ("Conteúdo", "", "pronta para revisar"), ("Revisão", "", "pendente")]
st = "".join(f'<li class="{c}"><a href="#"{" aria-current=\"step\"" if c == "atual" else ""}><strong>{n}</strong><span>{s}</span></a></li>' for n, c, s in passos)
def etapa(i, nome, evento, peso, minima, elim, clas, vinc=True):
    return f'''<fieldset class="cartao"><div class="cabeca" style="margin-bottom:1rem"><legend class="linha" style="float:left"><span class="rotulo-de-secao">Etapa {i} de 3</span> <strong>{nome}</strong></legend>
 <span class="linha"><button class="acao" aria-label="Subir {nome}">{ic("cima")}</button><button class="acao" aria-label="Descer {nome}">{ic("baixo")}</button><button class="acao perigoso" aria-label="Remover {nome}">{ic("lixo")}</button></span></div>
 <div class="campos"><div class="campo c-6"><label for="n{i}">Nome da Etapa <span class="obrigatorio">*</span></label><input id="n{i}" value="{nome}"></div>
 <div class="campo c-6"><label for="e{i}">Evento do Cronograma</label><select id="e{i}"><option>{evento}</option></select>{'' if vinc else '<span class="ajuda" style="color:var(--amarelo)">Sem vínculo: a Etapa não aparece no cronograma do Edital.</span>'}</div>
 <fieldset class="campo c-6"><legend>Como esta Etapa é concluída</legend><label class="escolha"><input type="radio" name="c{i}" checked> Com pontuação</label><label class="escolha"><input type="radio" name="c{i}"> Com decisão, sem nota</label></fieldset>
 <div class="campo c-3"><label for="p{i}">Peso <span class="opcional">(opcional)</span></label><input id="p{i}" value="{peso}" inputmode="numeric"></div>
 <div class="campo c-3"><label for="m{i}">Nota mínima <span class="opcional">(opcional)</span></label><input id="m{i}" value="{minima}" inputmode="numeric"></div>
 <fieldset class="campo c-6"><legend>Caráter</legend><div class="linha"><label class="escolha"><input type="checkbox" {"checked" if elim else ""}> Eliminatória</label><label class="escolha"><input type="checkbox" {"checked" if clas else ""}> Classificatória</label></div></fieldset>
 <div class="campo c-6"><span class="rotulo">Barema <span class="opcional">(opcional)</span></span><div class="linha"><button class="acao">{ic("mais")}Acrescentar critério</button><span class="ajuda">Sem barema, a comissão lança o total.</span></div></div></div></fieldset>'''
comp = f'''<div class="cabecalho-da-pagina"><div class="titulo"><h1>Edital SIM01/2026 <span class="situacao">Em elaboração</span></h1>
<p class="sub">Elaboração de edital (treinamento) · SIM-TREINAMENTO-001</p></div>
<div class="acoes"><a class="acao" href="#">Ver a prévia do PDF</a></div></div>
<ol class="passos" aria-label="Etapas da composição">{st}</ol>
<div class="com-trilho" style="margin-top:1.5rem"><div>
<div class="cabeca" style="margin-bottom:1rem"><div><h2>Etapas de Avaliação</h2><p class="fraco" style="font-size:.875rem">As fases pelas quais os candidatos passam, na ordem em que ocorrem. Valem para todos os Perfis deste Edital.</p></div><span class="fraco" style="font-size:.875rem"><strong style="color:var(--tinta)">3</strong> Etapas</span></div>
<div class="pilha">{etapa(1, "Prova objetiva", "Prova objetiva · 26/12/2026 09:34", "2", "6", True, True)}{etapa(2, "Análise de títulos", "Sem vínculo", "1", "", False, True, False)}
<button class="botao secundario" style="justify-self:start">{ic("mais")}Acrescentar Etapa</button></div>
<div class="barra-de-acoes"><a class="botao discreto" href="#">‹ Cronograma</a><div class="fim"><span class="ajuda">Rascunho salvo às 09:41</span><button class="botao secundario">Salvar rascunho</button><button class="botao">Avançar para Classificação {ic("seta")}</button></div></div>
</div>
<aside class="trilho" aria-label="Apoio ao preenchimento">
 <section class="cartao"><div class="cabeca" style="margin-bottom:.75rem"><h3>Pendências desta etapa</h3><span class="marca neutra">2</span></div>
 <ul class="itens"><li><div class="corpo"><strong>2 Etapas sem vínculo com o Cronograma</strong><span>Análise de títulos, Análise documental</span></div><a class="acao" href="#">Ir</a></li></ul></section>
 <section class="cartao"><h3>Como preencher</h3><dl class="dados" style="grid-template-columns:minmax(0,1fr);gap:.6rem">
 <div><dt><strong style="color:var(--tinta)">Peso</strong></dt><dd class="fraco">Só entra na conta quando um marco de classificação enumera esta Etapa.</dd></div>
 <div><dt><strong style="color:var(--tinta)">Nota mínima</strong></dt><dd class="fraco">Abaixo dela a pessoa é eliminada, se a Etapa for eliminatória.</dd></div>
 <div><dt><strong style="color:var(--tinta)">Barema</strong></dt><dd class="fraco">Critérios com pontuação máxima. A mesa de avaliação lança critério a critério.</dd></div></dl></section>
</aside></div>'''
(D / "compor-etapas.html").write_text(shell("Compor · Etapas de Avaliação", 'GPS › <a href="#">Processos Seletivos</a> › <a href="#">SIM-TREINAMENTO-001</a> › <a href="#">Edital SIM01/2026</a> › Compor', comp))

# ───── 4. Portal: convocação do candidato ─────
portal = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sua convocação — proposta · GPS</title><link rel="stylesheet" href="gps-ds.css"></head><body>{ICONES}
<header class="topo-do-portal"><a class="marca-do-portal" href="#">Cefor<span>/Ifes</span> · Seleções</a><nav aria-label="Sua área"><a href="#">Minhas inscrições</a><span class="quem">Alice Treinamento C11-01</span><button class="sair">Sair</button></nav></header>
<main><div class="centrada pilha">
<div><p class="fraco" style="font-size:.875rem"><a href="#">Minhas inscrições</a> › Professor de Informática · Edital SIM11/2026</p>
<h1 style="margin-top:.25rem">Você tem uma convocação</h1><p class="fraco" style="margin-top:.25rem">Nesta etapa, você envia seus documentos para a comissão conferir.</p></div>
<section class="cartao destaque" aria-labelledby="pz"><div class="prazo"><div><span class="rotulo-de-secao" id="pz">Prazo desta convocação</span><strong>até 14/12/2026, às 09h34</strong><span class="fraco" style="font-size:.875rem">segunda-feira · faltam 30 dias</span></div>
 <span class="situacao atencao">Faltam 2 documentos</span></div>
 <div style="margin-top:1rem"><div class="linha entre" style="font-size:.8125rem;margin-bottom:.35rem"><span class="fraco">Enviados e conferidos</span><span><strong>0</strong> de 2</span></div><div class="progresso" role="img" aria-label="0 de 2 documentos enviados"><i style="width:4%"></i></div></div></section>
<section aria-labelledby="oq"><div class="cabeca" style="margin-bottom:.75rem"><h2 id="oq">O que falta enviar</h2><span class="ajuda">PDF de até 10 MB por documento</span></div>
<div class="cartao sem-recuo">
 <div class="documento"><div class="corpo"><strong>Diploma de graduação</strong><span>Diploma ou certidão de conclusão, com histórico.</span></div><span class="situacao">Falta enviar</span><label class="botao secundario">{ic("arquivo")}Escolher PDF<input type="file" class="oculto" accept="application/pdf"></label></div>
 <div class="documento"><div class="corpo"><strong>Comprovante de residência</strong><span>Emitido nos últimos três meses.</span></div><span class="situacao">Falta enviar</span><label class="botao secundario">{ic("arquivo")}Escolher PDF<input type="file" class="oculto" accept="application/pdf"></label></div>
</div>
<div class="linha entre" style="margin-top:1rem"><span class="ajuda">Escolha o PDF de cada documento e envie todos de uma vez.</span><button class="botao grande" disabled>Enviar documentos</button></div></section>
<p class="aviso info"><span>Se você não atender no prazo, a comissão poderá registrar o não atendimento desta convocação. Esta convocação <strong>ainda não é o resultado</strong>: a comissão confere o que você enviar e registra o resultado.</span></p>
<details class="explica"><summary>Por que fui convocado</summary><p>Você foi chamado para uma das vagas da lista Ampla concorrência, pela sua posição na classificação — 1ª chamada, para vaga inicial.</p></details>
</div></main></body></html>'''
(D / "candidato-convocacao.html").write_text(portal)

def bloco(titulo, nota, corpo): return f'<section class="secao"><h2>{titulo}</h2><p class="sub">{nota}</p><div class="cartao">{corpo}</div></section>'
cores = [("--verde", "preenche"), ("--verde-texto", "escreve"), ("--verde-escuro", "marca"), ("--verde-claro", "fundo"), ("--tinta", "texto"), ("--tinta-2", "rótulo"), ("--tinta-3", "apoio"), ("--linha-forte", "borda de controle"), ("--linha", "borda de caixa"), ("--fundo-p", "fundo da página"), ("--amarelo", "atenção"), ("--amarelo-fundo", ""), ("--vermelho", "perigo"), ("--vermelho-fundo", ""), ("--azul", "informação"), ("--azul-fundo", "")]
amostras = "".join(f'<div style="display:grid;gap:.25rem;font-size:.75rem"><span style="height:2.5rem;border-radius:6px;border:1px solid var(--linha);background:var({v})"></span><code>{v}</code><span class="fraco">{u}</span></div>' for v, u in cores)
tipos = "".join(f'<div class="linha" style="align-items:baseline"><code class="codigo" style="width:5.5rem">{t}</code><span style="font-size:var({t});font-weight:{w}">{ex}</span></div>' for t, w, ex in [("--t-24", 600, "Título da página"), ("--t-18", 600, "Título de seção"), ("--t-16", 400, "Corpo, campos e prosa"), ("--t-14", 400, "Interface densa: tabela, botão, lista"), ("--t-13", 400, "Ajuda, rótulo de campo, segunda linha"), ("--t-12", 600, "RÓTULO DE SEÇÃO, SELO, CABEÇALHO DE TABELA")])
comp_html = f"""<div class="cabecalho-da-pagina"><div class="titulo"><h1>Componentes da proposta</h1><p class="sub">Uma amostra de cada peça do GPS Design System proposto, com os tokens que a sustentam. Os nomes de classe são os que o produto já usa, sempre que o papel é o mesmo.</p></div>
<div class="acoes"><a class="acao" href="index.html">Índice dos protótipos</a></div></div>
{bloco("Cores", "Os verdes e os estados são os de hoje. Os neutros são os da tela de entrada, promovidos a oficiais; o azul ganha token.", f'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(7.5rem,1fr));gap:1rem">{amostras}</div>')}
{bloco("Tipografia", "Seis tamanhos. O que hoje sai em 12,8, 13,12, 13,6, 14,4, 14,72 e 15 px cai no vizinho.", f'<div class="pilha" style="gap:.6rem">{tipos}</div>')}
{bloco("Botões", "Três papéis e duas alturas. Um botão cheio por tela ou por cartão; o perigo só no ato irreversível.", f'<div class="pilha"><div class="linha"><button class="botao">{ic("mais")}Primário</button><button class="botao secundario">Secundário</button><button class="botao discreto">Discreto</button><button class="botao perigoso">Perigoso</button><button class="botao" disabled>Indisponível</button></div><div class="linha"><a class="acao" href="#">Ação de linha (a)</a><button class="acao">Ação de linha (button)</button><button class="acao perigoso">Remover</button><button class="acao" aria-label="Subir">{ic("cima")}</button><span class="ajuda">40 px e 32 px; a e button saem com a mesma altura.</span></div></div>')}
{bloco("Campos", "Rótulo em cima, ajuda embaixo, 40 px de altura, grade de doze colunas dentro de uma medida de formulário.", '<div class="campos" style="max-width:var(--formulario)"><div class="campo c-8"><label for="x1">Denominação <span class="obrigatorio">*</span></label><input id="x1" value="Professor de Informática"></div><div class="campo c-4"><label for="x2">Vagas imediatas</label><input id="x2" value="4" inputmode="numeric"></div><div class="campo c-6"><label for="x3">Localidade</label><select id="x3"><option>Campus Serra</option></select><span class="ajuda">Aparece no quadro de vagas do Edital.</span></div><fieldset class="campo c-6"><legend>Cadastro reserva</legend><label class="escolha"><input type="radio" name="cr" checked> Limitado pelo corte</label><label class="escolha"><input type="radio" name="cr"> Ilimitado</label></fieldset></div>')}
{bloco("Indicadores", "Um desenho para número com rótulo: zero esmaecido, o que pede ação em destaque, versão compacta para o trilho.", '<div class="indicadores"><div class="indicador ativo"><strong>3</strong><span>titulares a convocar</span></div><div class="indicador"><strong>116</strong><span>inscrições submetidas</span></div><div class="indicador"><strong>1,5</strong><span>inscrições por vaga</span></div><div class="indicador zero"><strong>0</strong><span>com pendência</span></div></div>')}
{bloco("Selos", "Três espécies: situação (pílula), código (mono) e marca (caixa alta).", '<div class="linha"><span class="situacao">Em elaboração</span><span class="situacao ok">Publicado</span><span class="situacao atencao">Em revisão</span><span class="situacao erro">Cancelado</span><span class="situacao info">Simulação</span><span class="codigo">INS-2026-TB5YA4B7</span><span class="codigo">SIM10/2026</span><span class="marca">Sua</span><span class="marca perigo">Irreversível</span><span class="marca neutra">Calculado</span></div>')}
{bloco("Avisos", "Quatro tons, com ícone além da cor; versão em linha para o aviso que acompanha um controle.", '<div class="pilha"><p class="aviso"><span><strong>Atenção.</strong> O prazo de recurso contra “Classificação final” vai até 19/11/2026 às 23h59.</span></p><p class="aviso info"><span>Abrir esta tela <strong>não apura nada</strong>. Os números vêm de atos já emitidos.</span></p><p class="aviso ok"><span><strong>Rascunho salvo.</strong> Nada foi publicado.</span></p><p class="aviso erro"><span><strong>Este ato não pode ser desfeito.</strong> O Edital passa a Encerrado e deixa de receber inscrição e Retificação.</span></p><p class="aviso em-linha"><span>Sem vínculo com o Cronograma.</span></p></div>')}
{bloco("Navegação dentro da página", "Abas para vistas do mesmo conjunto, segmentos para recortes, passos para sequências.", '<div class="pilha"><nav class="abas"><a href="#" aria-current="page">Em andamento <span>19</span></a><a href="#">Encerrados <span>0</span></a><a href="#">Todos <span>19</span></a></nav><div><nav class="segmentos"><a href="#" aria-current="page">Ampla concorrência</a><a href="#">PPP</a></nav></div><ol class="passos"><li class="feito"><a href="#"><strong>Fixar os participantes</strong><span>feito</span></a></li><li class="atual"><a href="#"><strong>Obter a semente pública</strong><span>agora</span></a></li><li><a href="#"><strong>Realizar o sorteio</strong><span>depois</span></a></li><li><a href="#"><strong>Consultar a ordem</strong><span>depois</span></a></li></ol></div>')}
<section class="secao"><h2>Tabela</h2><p class="sub">Sempre em moldura rolável dentro de um cartão; número à direita; segunda linha para o dado de apoio.</p><div class="cartao sem-recuo"><div class="tabela-rolavel"><table class="tabela"><thead><tr><th class="numero">Posição</th><th>Participante</th><th>Modalidade</th><th class="numero">Pontuação</th><th>Situação</th></tr></thead><tbody><tr><td class="numero">1º</td><td><strong>Alice Treinamento C04-01</strong><span class="segunda"><span class="codigo">INS-2026-P67VP98W</span></span></td><td>Ampla concorrência</td><td class="numero">26,00</td><td><span class="situacao ok">Classificada</span></td></tr><tr><td class="numero">2º</td><td><strong>Bernardo Treinamento C04-02</strong><span class="segunda"><span class="codigo">INS-2026-X97ZXS36</span></span></td><td>Ampla concorrência</td><td class="numero">26,00</td><td><span class="situacao atencao">Empate residual</span></td></tr></tbody></table></div><div class="paginacao"><span>2 de 9</span><span class="linha"><a class="acao" href="#">Anterior</a><a class="acao" href="#">Próxima</a></span></div></div></section>"""
(D / "componentes.html").write_text(shell("Componentes da proposta", "GPS › Estudo de design system › Componentes", comp_html, atual=""))
telas = [("lista-de-processos", "Lista de Processos Seletivos", "Central de trabalho + lista administrativa", "g-lista"), ("convocacao", "Convocação", "Operação com etapas", "g-convocacao"), ("compor-etapas", "Compor · Etapas de Avaliação", "Formulário de configuração", "g-compor-etapas"), ("candidato-convocacao", "Convocação do candidato", "Jornada do candidato", "p-convocacao")]
cart = "".join(f'<section class="cartao"><div class="cabeca"><div><h2>{t}</h2><p class="fraco" style="font-size:.875rem">{a}</p></div><span class="linha"><a class="acao" href="../capturas/{c}.jpg">Como é hoje</a><a class="botao compacto" href="{n}.html">Abrir a proposta</a></span></div></section>' for n, t, a, c in telas)
idx = f"""<div class="cabecalho-da-pagina"><div class="titulo"><h1>Protótipos do estudo de design system</h1><p class="sub">Quatro telas de referência, uma por arquétipo, redesenhadas sobre a mesma folha (<code>gps-ds.css</code>). São páginas estáticas com dados fictícios dos cenários de treinamento: nada aqui é o produto.</p></div><div class="acoes"><a class="acao" href="componentes.html">Folha de componentes</a></div></div><div class="pilha" style="max-width:var(--formulario)">{cart}</div>"""
(D / "index.html").write_text(shell("Protótipos", "GPS › Estudo de design system", idx, atual=""))
print("ok", [p.name for p in D.glob("*.html")])
