import os, sys
os.chdir(sys.argv[1])
base = open("convocacao.html").read()

def bloco(html, inicio, fim, novo):
    i = html.index(inicio); j = html.index(fim, i)
    return html[:i] + novo + html[j:]

def cartao(html, chave, novo):
    i = html.index(f'<li class="requisito cartao-do-documento" id="item-{chave}"')
    j = html.index("</li>", i) + len("</li>")
    return html[:i] + novo + html[j:]

def recebido(chave, nome, quando, conferido=False):
    selo = '<span class="selo selo-conferido">Conferido</span>' if conferido else '<span class="selo selo-comissao">Aguardando conferência</span>'
    texto = "Conferido: de acordo com o Edital." if conferido else f"Recebido em {quando}. A comissão vai conferir; você não precisa fazer nada agora."
    return f'''<li class="requisito cartao-do-documento" id="item-{chave}" tabindex="-1">
      <h3>{nome}</h3>
      <p class="selos">{selo}</p>
      <p class="situacao-do-documento">{texto}</p>
      <p class="arquivo"><a href="#">Ver o arquivo recebido<span class="oculto">: {nome}</span></a></p>
    </li>'''

def contagem(a, b, c, rot_a="a enviar", rot_c="conferidos"):
    return f'''<ul class="contagem-das-obrigacoes">
    <li class="a-fazer"><span class="numero">{a}</span><span class="rotulo">{rot_a}</span></li>
    <li><span class="numero">{b}</span><span class="rotulo">aguardando conferência</span></li>
    <li class="conferido"><span class="numero">{c}</span><span class="rotulo">{rot_c}</span></li>
  </ul>'''

# --- Depois do envio do primeiro documento ---------------------------------------------------
h = base.replace("<title>Sua convocação", "<title>Sua convocação (depois do envio)")
h = bloco(h, "<!-- Bloco 3", "<!-- Bloco 4", '''<!-- Bloco 3: o progresso, com a confirmação do envio onde a pessoa está. -->
<section class="progresso-das-obrigacoes" id="progresso" aria-labelledby="titulo-progresso" tabindex="-1">
  <h2 id="titulo-progresso">O que você precisa fazer</h2>
  <div class="confirmacao-do-envio" role="status">
    <p><strong>Recebemos a Certidão de nascimento ou casamento</strong> em 05/11/2026, às 10h25. A comissão vai conferir.</p>
    <p>Próximo: <a href="#item-historico">Histórico escolar do ensino médio</a>.</p>
  </div>
  <p class="proximo-passo">Falta enviar 3 documentos e o Requerimento de Matrícula.</p>
  ''' + contagem(4, 1, 0) + '''
</section>

<p class="nota-da-maquete"><strong>Maquete.</strong> Hoje o envio volta a <code>#item-‹id›</code>: a página rola até o cartão, que já desceu para "O que você já apresentou", e a confirmação fica no topo, fora da tela. A proposta volta a <code>#progresso</code>, com a confirmação e o próximo item juntos.</p>

''')
h = cartao(h, "certidao", "")
h = h.replace("<!-- Bloco 5", '''<section class="bloco-dos-formularios" id="o-que-voce-ja-enviou" aria-labelledby="titulo-enviado">
  <h2 id="titulo-enviado">O que você já enviou</h2>
  <ul class="requisitos-lista">
    ''' + recebido("certidao", "Certidão de nascimento ou casamento", "05/11/2026, às 10h25") + '''
  </ul>
</section>

<!-- Bloco 5''')
open("convocacao-apos-envio.html", "w").write(h)

# --- Com pendência (o cenário F) ---------------------------------------------------------------
h = base.replace("<title>Sua convocação", "<title>Sua convocação (com pendência)")
h = h.replace('<p class="faltam">Faltam 5 dias.</p>', '<p class="faltam">Faltam 2 dias.</p>')
h = bloco(h, "<!-- Bloco 3", "<!-- Bloco 4", '''<!-- Bloco 3: o progresso, com a pendência à frente. -->
<section class="progresso-das-obrigacoes" aria-labelledby="titulo-progresso">
  <h2 id="titulo-progresso">O que você precisa fazer</h2>
  <p class="proximo-passo">A comissão pediu a correção de 1 documento, e falta enviar 1.</p>
  ''' + contagem(2, 0, 2, rot_a="a corrigir ou enviar", rot_c="conferidos") + '''
  <p><a class="principal" href="#item-historico">Ver e corrigir os documentos pendentes</a></p>
</section>

''')
h = h.replace('<h2 id="titulo-falta">Envie até 10/11/2026, às 10h23</h2>', '<h2 id="titulo-falta">Corrija e envie até 10/11/2026, às 10h23</h2>')
h = cartao(h, "certidao", "")
h = cartao(h, "certificado", "")
i = h.index('<li class="cartao-do-requerimento"'); j = h.index("</li>", i) + 5
h = h[:i] + h[j:]
h = cartao(h, "historico", '''<li class="requisito cartao-do-documento destaque" id="item-historico" tabindex="-1">
      <h3>Histórico escolar do ensino médio</h3>
      <p class="selos"><span class="selo selo-correcao">Precisa de correção</span></p>
      <p class="instrucao">Todas as páginas, em arquivo único.</p>
      <p class="situacao-do-documento" id="situacao-historico">Precisa de correção: Falta a página 2. Envie um novo arquivo até 10/11/2026, às 10h23.</p>
      <p class="arquivo"><a href="#">Ver o arquivo recebido<span class="oculto">: Histórico escolar do ensino médio</span></a></p>
      <div class="envio"><form method="post" action="#">
        <div class="escolher">
          <input type="file" id="arquivo-historico" name="arquivo" accept="application/pdf" aria-describedby="situacao-historico ajuda-historico">
          <label class="botao-arquivo" for="arquivo-historico">Escolher o novo arquivo PDF<span class="oculto"> para Histórico escolar do ensino médio</span></label>
          <span class="nome-do-arquivo">Nenhum arquivo escolhido</span>
          <button type="submit" class="acao">Enviar<span class="oculto">: Histórico escolar do ensino médio</span></button>
        </div>
        <span class="ajuda limite" id="ajuda-historico">Somente PDF, até 10 MB.</span>
      </form></div>
    </li>''')
h = h.replace("<!-- Bloco 5", '''<section class="bloco-dos-formularios" id="o-que-voce-ja-enviou" aria-labelledby="titulo-enviado">
  <h2 id="titulo-enviado">O que você já enviou</h2>
  <ul class="requisitos-lista">
    ''' + recebido("certidao", "Certidão de nascimento ou casamento", "", True) + recebido("certificado", "Certificado de conclusão do ensino médio", "", True) + '''
  </ul>
  <p class="requerimento-nas-obrigacoes"><span aria-hidden="true">✓</span> Requerimento de Matrícula enviado. <a href="#">Conferir o Requerimento de Matrícula enviado</a></p>
</section>

<p class="nota-da-maquete"><strong>Maquete.</strong> O motivo da pendência aparece só aqui, no portal (115, FR-3584). A política de aviso da seção 7 do estudo diria por e-mail apenas que "há documento da convocação que precisa de atenção".</p>

<!-- Bloco 5''')
open("convocacao-pendencia.html", "w").write(h)

# --- A sucessora (correção da 120) --------------------------------------------------------------
h = base.replace("<title>Sua convocação", "<title>Sua convocação (corrigida)")
h = h.replace('<p class="explicacao">', '''<p class="aviso convocacao-substituida" role="note"><strong>Esta convocação foi corrigida.</strong> Ela substitui a mensagem enviada em 05/11/2026, às 10h23. O prazo que vale é o desta página.</p>
  <p class="explicacao">''', 1)
h = h.replace("até segunda-feira, 10/11/2026, às 10h23", "até quarta-feira, 12/11/2026, às 10h23").replace("Faltam 5 dias.", "Faltam 7 dias.")
h = h.replace("Envie até 10/11/2026, às 10h23", "Envie até 12/11/2026, às 10h23")
h = h.replace("<dt>Comunicação</dt><dd>Mensagem enviada em 05/11/2026, às 10h23. O prazo conta a partir deste envio.</dd>",
              "<dt>Comunicação</dt><dd>Mensagem da correção enviada em 05/11/2026, às 10h24. O prazo conta a partir deste envio. Ela substitui a de 05/11/2026, às 10h23.</dd>")
h = h.replace("<!-- Bloco 5", '''<p class="nota-da-maquete"><strong>Maquete.</strong> Hoje a sucessora não diz que substitui: o prazo muda em silêncio, e quem guardou a data da primeira mensagem não tem como saber qual vale. O motivo da correção continua fora do portal (120, linhas 486–487); o que se acrescenta é só o fato e a data da anterior.</p>

<!-- Bloco 5''')
open("convocacao-sucessora.html", "w").write(h)
print("ok")
